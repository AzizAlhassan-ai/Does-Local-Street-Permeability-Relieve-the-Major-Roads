#!/usr/bin/env python
"""Stage 5 — the two remaining sensitivity checks.

A. DETOUR CAP (D-037). P1 currently counts a local route as a substitute if it is
   <= 1.5x the arterial's length. Route-choice evidence says drivers optimise TIME,
   not distance, and accept roughly 5-25% detours; the measured time ratio of P1
   routes is already 1.8-2.0x. So 1.5 on distance is LOOSE, not conservative, and
   1.25 is the more literature-consistent specification. Swept at 1.25 / 1.5 / 2.0.

B. TERTIARY CLASSIFICATION (D-012, superseded by D-061). The original test — move
   OSM `tertiary` into the LOCAL network — is INVALID: 41.2% of outcome segments sit
   on tertiary roads (84.1% of major collectors), so it would put roads that supply
   the outcome into the predictor, the exact contamination D-001 forbids. The valid
   test moves BOTH sides together: tertiary becomes local AND HPMS major collectors
   (f_system 5) are dropped from the outcome. That asks "does the finding hold if we
   study only the larger arterials?", which is answerable.

Nothing here overwrites the primary pipeline outputs.

Usage
-----
    uv run python code/05_model/05e_sensitivity.py
"""

from __future__ import annotations

import argparse
import importlib.util
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

import geopandas as gpd
import networkx as nx
import numpy as np
import pandas as pd
import statsmodels.formula.api as smf
from shapely.geometry import Point

from lib import cfg, paths, provenance

_spec = importlib.util.spec_from_file_location(
    "tr", pathlib.Path(__file__).resolve().parents[1] / "02_network" / "02d_through_routes.py")
TR = importlib.util.module_from_spec(_spec)
sys.argv = [sys.argv[0]]
_spec.loader.exec_module(TR)

CTRL = ["pop_z", "ent_z", "dcbd_z", "dcbd2_z", "yr_z", "ln_z"]


def z(s):
    sd = s.std(ddof=0)
    return (s - s.mean()) / sd if sd and sd > 0 else s * 0.0


def fit(d):
    for dst, src in [("pop_z", "pop_density_km2"), ("ent_z", "lu_entropy"),
                     ("dcbd_z", "dist_cbd_km_c"), ("dcbd2_z", "dist_cbd_km_c_sq"),
                     ("yr_z", "median_year_structure_built"), ("ln_z", "through_lanes")]:
        d[dst] = z(d[src])
    d = d.dropna(subset=["log_aadt", "p1", "f_system", "cell_id"] + CTRL)
    if len(d) < 100 or d["p1"].nunique() < 2 or d["f_system"].nunique() < 2:
        return None, len(d)
    f = "log_aadt ~ " + " + ".join(CTRL) + " + C(f_system) + p1"
    m = smf.mixedlm(f, d, groups=d["cell_id"].astype(str)).fit(method="lbfgs", reml=True)
    return m, len(d)


def compute_p1(city, conf, detour, tertiary_local=False, radius=800):
    """Recompute P1 in memory under a given detour cap / tag partition."""
    metric = conf["crs"]["metric"]
    tr = conf["through_routes"]
    access_r = float(tr["access_radius_m"]); k_max = int(tr["max_paths"])
    min_span = float(tr.get("min_span_frac", 0.5))

    loc = gpd.read_file(paths.raw(city, "osm") / "network_urban_area_local.gpkg", layer="edges")
    if tertiary_local:
        maj = gpd.read_file(paths.raw(city, "osm") / "network_urban_area_major.gpkg", layer="edges")
        hw = maj["highway"].astype(str).str.split(",").str[0]
        add = maj[hw.isin(["tertiary", "tertiary_link"])]
        loc = pd.concat([loc, add], ignore_index=True)
        loc = gpd.GeoDataFrame(loc, geometry="geometry", crs=add.crs)

    G, _ = TR.build_local_graph(loc, metric)
    nodes = gpd.read_file(paths.raw(city, "osm") / "network_urban_area_all.gpkg",
                          layer="nodes").to_crs(metric)
    nodes = nodes[nodes["osmid"].isin(G.nodes)].reset_index(drop=True)
    ng = gpd.GeoDataFrame({"osmid": nodes["osmid"].values},
                          geometry=nodes.geometry.values, crs=metric)
    nidx = ng.sindex
    pos = dict(zip(ng["osmid"].values, zip(ng.geometry.x.values, ng.geometry.y.values)))

    seg = gpd.read_parquet(paths.processed(city) / "segments.parquet").to_crs(metric)
    cat = gpd.read_parquet(paths.processed(city) / f"catchments_r{radius}.parquet"
                           ).to_crs(metric).set_index("segment_uid")
    out = []
    for srow in seg.itertuples():
        uid, geom = srow.segment_uid, srow.geometry
        if uid not in cat.index:
            out.append({"segment_uid": uid, "p1": 0.0}); continue
        buf = cat.loc[uid, "geometry"]
        sub = set(ng["osmid"].iloc[list(nidx.query(buf, predicate="intersects"))])
        Gs = G.subgraph(sub)
        a, b = TR.endpoints_of(geom)
        srcs = [ng["osmid"].iloc[j] for j in nidx.query(a.buffer(access_r), predicate="intersects")]
        tgts = [ng["osmid"].iloc[j] for j in nidx.query(b.buffer(access_r), predicate="intersects")]
        srcs = [n for n in srcs if n in sub]; tgts = [n for n in tgts if n in sub]
        ov = set(srcs) & set(tgts)
        srcs = [n for n in srcs if n not in ov]; tgts = [n for n in tgts if n not in ov]
        found = TR.disjoint_paths(Gs, srcs, tgts, geom, geom.length, detour,
                                  min_span, k_max, pos)
        out.append({"segment_uid": uid, "p1": float(len(found) > 0)})
    return pd.DataFrame(out)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--radius", type=int, default=800)
    args = ap.parse_args()
    conf = cfg.config()
    cities = sorted(cfg.cities().keys())
    pooled = pd.read_parquet(paths.ANALYSIS / f"analysis_pooled_r{args.radius}.parquet")
    print(f"Environment: {provenance.environment_stamp()}")

    # ---------------- A. detour cap ----------------
    print(f"\n{'='*84}\nA. DETOUR CAP sweep — how far a driver will go before it isn't a substitute\n{'='*84}")
    caps = [1.25, 1.5, 2.0]
    rows = []
    for c in cities:
        base = pooled[pooled.city == c].copy()
        line = {"city": c}
        for cap in caps:
            p1 = compute_p1(c, conf, cap, radius=args.radius)
            p1["segment_uid"] = c + "|" + p1["segment_uid"].astype(str)
            d = base.drop(columns=["p1"], errors="ignore").merge(p1, on="segment_uid", how="left")
            m, n = fit(d)
            line[f"prev_{cap}"] = 100 * d["p1"].mean()
            line[f"b_{cap}"] = m.params["p1"] if m is not None else np.nan
            line[f"p_{cap}"] = m.pvalues["p1"] if m is not None else np.nan
        rows.append(line)
        print(f"  {c} done")
    t = pd.DataFrame(rows)
    print(f"\n  {'city':<15}" + "".join(f"{'cap '+str(c):>22}" for c in caps))
    print(f"  {'':<15}" + "".join(f"{'%P1':>8}{'beta':>8}{'p':>6}" for _ in caps))
    for _, x in t.iterrows():
        s = f"  {x.city:<15}"
        for cap in caps:
            s += f"{x[f'prev_{cap}']:>7.1f}%{x[f'b_{cap}']:>8.3f}{x[f'p_{cap}']:>6.3f}"
        print(s)
    t.to_csv(paths.TABLES / "sensitivity_detour_cap.csv", index=False)

    # ---------------- B. tertiary, both sides ----------------
    print(f"\n{'='*84}\nB. TERTIARY as local AND major collectors dropped from the outcome\n{'='*84}")
    print("  (the naive one-sided test is invalid — see D-061)")
    rows2 = []
    for c in cities:
        base = pooled[(pooled.city == c) & (pooled.f_system.isin([3, 4]))].copy()
        p1 = compute_p1(c, conf, float(conf["through_routes"]["detour_cap"]),
                        tertiary_local=True, radius=args.radius)
        p1["segment_uid"] = c + "|" + p1["segment_uid"].astype(str)
        d = base.drop(columns=["p1"], errors="ignore").merge(p1, on="segment_uid", how="left")
        m, n = fit(d)
        prim, _ = fit(pooled[pooled.city == c].assign(p1=lambda x: x.p1_any.astype(float)).copy())
        rows2.append({"city": c, "n": n, "prev": 100 * d["p1"].mean(),
                      "b_sens": m.params["p1"] if m is not None else np.nan,
                      "p_sens": m.pvalues["p1"] if m is not None else np.nan,
                      "b_primary": prim.params["p1"] if prim is not None else np.nan})
        print(f"  {c} done")
    t2 = pd.DataFrame(rows2)
    print(f"\n  {'city':<15}{'n':>8}{'%P1':>8}{'beta sens':>11}{'p':>8}{'beta primary':>14}{'shift':>9}")
    for _, x in t2.iterrows():
        print(f"  {x.city:<15}{x.n:>8,.0f}{x.prev:>7.1f}%{x.b_sens:>11.4f}{x.p_sens:>8.4f}"
              f"{x.b_primary:>14.4f}{x.b_sens-x.b_primary:>+9.4f}")
    t2.to_csv(paths.TABLES / "sensitivity_tertiary_bothsides.csv", index=False)
    print("\n  wrote outputs/tables/sensitivity_detour_cap.csv and "
          "sensitivity_tertiary_bothsides.csv")
    provenance.log_progress("05e_sensitivity", "detour-cap sweep + tertiary both-sides test")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
