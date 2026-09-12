#!/usr/bin/env python
"""Stage 5 — outcome-currency check: does the association survive on 2024 traffic? (D-078)

The paper's primary outcome is the FHWA HPMS 2018 public release (the last year
distributed as per-state shapefile services). That is NOT the data frontier: BTS
publishes HPMS annually through the National Transportation Atlas Database, and
the 2024 edition — a national file geodatabase, one feature class per state,
representing the system as of 31 December 2024 — is available. The manuscript's
claim that 2018 is "the most recent national release" was wrong and is corrected.

This script isolates the outcome vintage. The unit of analysis, the catchments,
the controls and P1 are all held FIXED at their 2018-pipeline values; only AADT
is replaced, by matching each analysis segment's midpoint to the nearest 2024
HPMS centreline of the same functional class within a tolerance. So the question
answered is narrow and clean: on the same roads with the same measured
substitutability, does the association hold six years and one pandemic later?

Depends on: data/raw/_hpms_currency/HPMS2024.gdb (2.6 GB download, see README)

Usage
-----
    uv run python code/05_model/05j_hpms_currency.py
"""

from __future__ import annotations

import argparse
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

import geopandas as gpd
import numpy as np
import pandas as pd
import statsmodels.formula.api as smf

from lib import cfg, paths, provenance

GDB = paths.ROOT / "data" / "raw" / "_hpms_currency" / "HPMS2024.gdb"
STATE_ABBR = {"08": "CO", "41": "OR", "53": "WA", "04": "AZ", "25": "MA",
              "33": "NH", "49": "UT", "37": "NC", "45": "SC"}
MATCH_TOL_M = 100.0            # midpoint-to-centreline tolerance
CTRL = ["pop_z", "ent_z", "dcbd_z", "dcbd2_z", "yr_z", "ln_z"]


def z(s):
    sd = s.std(ddof=0)
    return (s - s.mean()) / sd if sd and sd > 0 else s * 0.0


def fit(d, ycol):
    d = d.copy()
    for dst, src in [("pop_z", "pop_density_km2"), ("ent_z", "lu_entropy"),
                     ("dcbd_z", "dist_cbd_km_c"), ("dcbd2_z", "dist_cbd_km_c_sq"),
                     ("yr_z", "median_year_structure_built"), ("ln_z", "through_lanes")]:
        d[dst] = z(d[src])
    d["p1"] = d["p1_any"].astype(float)
    d = d.dropna(subset=[ycol, "p1", "f_system", "cell_id"] + CTRL)
    if len(d) < 100 or d["p1"].nunique() < 2 or d["f_system"].nunique() < 2:
        return None, len(d)
    f = f"{ycol} ~ " + " + ".join(CTRL) + " + C(f_system) + p1"
    m = smf.mixedlm(f, d, groups=d["cell_id"].astype(str)).fit(method="lbfgs", reml=True)
    return m, len(d)


def load_2024(city, metric):
    """2024 HPMS centrelines for the states this city spans, clipped to the UA."""
    ua = gpd.read_file(paths.raw(city, "census") / "urban_area.gpkg").to_crs(metric)
    ua_geom = ua.union_all() if hasattr(ua, "union_all") else ua.unary_union
    parts = []
    for st in cfg.states(city):
        ab = STATE_ABBR.get(st["fips"])
        if ab is None:
            print(f"  !! no abbrev mapped for FIPS {st['fips']}")
            continue
        layer = f"HPMS_FULL_{ab}_2024"
        bbox = tuple(gpd.GeoSeries([ua_geom], crs=metric).to_crs(4326).total_bounds)
        g = gpd.read_file(GDB, layer=layer, bbox=bbox,
                          columns=["aadt", "f_system", "facility_type", "route_id",
                                   "through_lanes"])
        g = g.to_crs(metric)
        g = g[g.geometry.notna() & (g.aadt > 0)]
        g = g[g.f_system.isin([3, 4, 5])]
        if "facility_type" in g.columns:
            g = g[g.facility_type == 2]
        idx = list(g.sindex.query(ua_geom, predicate="intersects"))
        g = g.iloc[idx]
        parts.append(g[["aadt", "f_system", "geometry"]])
        print(f"    {layer}: {len(g):,} eligible centrelines in the UA")
    if not parts:
        return None
    return gpd.GeoDataFrame(pd.concat(parts, ignore_index=True), crs=metric)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--radius", type=int, default=800)
    ap.add_argument("--cities", nargs="*", default=None)
    args = ap.parse_args()
    conf = cfg.config()
    metric = conf["crs"]["metric"]
    if not GDB.exists():
        print(f"ERROR: {GDB} missing. Download the HPMS 2024 NTAD geodatabase first.")
        return 1
    pooled = pd.read_parquet(paths.ANALYSIS / f"analysis_pooled_r{args.radius}.parquet")
    cities = args.cities or sorted(set(pooled.city.unique()))
    print(f"Environment: {provenance.environment_stamp()}")
    print("Outcome vintage check: 2018 (primary) vs 2024 (NTAD), units and P1 fixed.\n")

    rows, frames = [], []
    for c in cities:
        print(f"  {c}")
        g24 = load_2024(c, metric)
        if g24 is None or not len(g24):
            print("    no 2024 features — skipped"); continue
        seg = gpd.read_parquet(paths.processed(c) / "segments.parquet").to_crs(metric)
        mid = gpd.GeoDataFrame(
            seg[["segment_uid"]].reset_index(drop=True),
            geometry=[g.interpolate(0.5, normalized=True) for g in seg.geometry],
            crs=metric)
        j = gpd.sjoin_nearest(mid, g24[["aadt", "geometry"]], how="left",
                              max_distance=MATCH_TOL_M, distance_col="d24")
        j = (j.sort_values("d24").drop_duplicates("segment_uid")
             .rename(columns={"aadt": "aadt_2024"}))
        j["segment_uid"] = c + "|" + j["segment_uid"].astype(str)
        base = pooled[pooled.city == c].merge(
            j[["segment_uid", "aadt_2024", "d24"]], on="segment_uid", how="left")
        base["log_aadt_2024"] = np.log(base["aadt_2024"].where(base["aadt_2024"] > 0))
        matched = int(base["aadt_2024"].notna().sum())
        print(f"    matched {matched:,} of {len(base):,} segments "
              f"({100*matched/len(base):.1f}%) within {MATCH_TOL_M:.0f} m")

        both = base.dropna(subset=["log_aadt", "log_aadt_2024"])
        rho = both[["log_aadt", "log_aadt_2024"]].corr(method="spearman").iloc[0, 1]
        med_ratio = float((both.aadt_2024 / both.aadt).median())
        m18, n18 = fit(both, "log_aadt")
        m24, n24 = fit(both, "log_aadt_2024")
        b18 = m18.params["p1"] if m18 is not None else np.nan
        b24 = m24.params["p1"] if m24 is not None else np.nan
        p24 = m24.pvalues["p1"] if m24 is not None else np.nan
        rows.append({"city": c, "n_matched": matched, "n_model": n24,
                     "spearman_2018_2024": rho, "median_aadt_ratio": med_ratio,
                     "beta_2018": b18, "beta_2024": b24, "p_2024": p24,
                     "pct_2018": 100*(np.exp(b18)-1), "pct_2024": 100*(np.exp(b24)-1)})
        frames.append(base[["segment_uid", "city", "aadt", "aadt_2024"]])
        print(f"    rank corr(2018, 2024) = {rho:.3f} | median AADT ratio "
              f"{med_ratio:.3f} | β 2018 {b18:+.4f} -> 2024 {b24:+.4f} (p={p24:.4f})")

    if not rows:
        print("no cities processed"); return 1
    t = pd.DataFrame(rows)
    print(f"\n{'='*80}\nSUMMARY — same segments, same P1, outcome swapped\n{'='*80}")
    print(f"  {'city':<15}{'n':>8}{'ρ(18,24)':>10}{'AADT ratio':>12}"
          f"{'β 2018':>10}{'β 2024':>10}{'p 2024':>9}")
    for _, x in t.iterrows():
        print(f"  {x.city:<15}{x.n_model:>8,.0f}{x.spearman_2018_2024:>10.3f}"
              f"{x.median_aadt_ratio:>12.3f}{x.beta_2018:>10.4f}{x.beta_2024:>10.4f}"
              f"{x.p_2024:>9.4f}")
    neg = int((t.beta_2024 < 0).sum())
    sig = int(((t.beta_2024 < 0) & (t.p_2024 < 0.05)).sum())
    print(f"\n  2024 outcome: negative in {neg}/{len(t)} cities, "
          f"negative and significant in {sig}/{len(t)}")
    fpo = paths.TABLES / f"hpms_currency_2018_vs_2024_r{args.radius}.csv"
    t.to_csv(fpo, index=False)
    print(f"  wrote {fpo.relative_to(paths.ROOT)}")
    provenance.log_progress("05j_hpms_currency",
                            f"2018 vs 2024 outcome check, {len(t)} cities")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
