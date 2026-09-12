#!/usr/bin/env python
"""Stage 5 — sensitivity of P1 to its remaining fixed constants (D-077).

The detour cap already has a full sweep (05e). The reviewer panel noted that the
other three operational constants are asserted rather than tested, and that since
P1 is the paper's whole contribution each deserves either a sweep or a mechanism-
tied justification:

  access_radius_m   200   how far from the segment's endpoint a local street may
                          attach. Swept at 100 / 200 / 300 m.
  min_span_frac     0.5   how much of the segment a candidate route must span.
                          Swept at 0.33 / 0.50 / 0.67.
  max_paths         5     cap on edge-disjoint routes counted. Irrelevant to the
                          binary primary form by construction; reported for the
                          count form only.

Everything is recomputed in memory; no pipeline output is overwritten.

Usage
-----
    uv run python code/05_model/05i_p1_constants.py
    uv run python code/05_model/05i_p1_constants.py --cities denver portland
"""

from __future__ import annotations

import argparse
import importlib.util
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

import geopandas as gpd
import numpy as np
import pandas as pd
import statsmodels.formula.api as smf

from lib import cfg, paths, provenance

_spec = importlib.util.spec_from_file_location(
    "tr", pathlib.Path(__file__).resolve().parents[1] / "02_network" / "02d_through_routes.py")
TR = importlib.util.module_from_spec(_spec)
_argv = sys.argv
sys.argv = [sys.argv[0]]
_spec.loader.exec_module(TR)
sys.argv = _argv

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


def compute_p1(city, conf, access_r, min_span, k_max, detour, radius=800):
    """Recompute P1 in memory under a given set of operational constants."""
    metric = conf["crs"]["metric"]
    loc = gpd.read_file(paths.raw(city, "osm") / "network_urban_area_local.gpkg",
                        layer="edges")
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
            out.append({"segment_uid": uid, "p1": 0.0, "p1n": 0}); continue
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
        out.append({"segment_uid": uid, "p1": float(len(found) > 0), "p1n": len(found)})
    return pd.DataFrame(out)


def sweep(pooled, cities, conf, radius, label, variants, base_kw):
    print(f"\n{'='*86}\n{label}\n{'='*86}")
    hdr = "".join(f"{'%P1':>8}{'β':>9}{'p':>8}" for _ in variants)
    print(f"  {'city':<15}" + "".join(f"{str(v):>25}" for v, _ in variants))
    print(f"  {'':<15}" + hdr)
    rows = []
    for c in cities:
        base = pooled[pooled.city == c].copy()
        line = {"check": label.split("—")[0].strip(), "city": c}
        cells = []
        for vlabel, kw in variants:
            kws = {**base_kw, **kw}
            p1 = compute_p1(c, conf, radius=radius, **kws)
            p1["segment_uid"] = c + "|" + p1["segment_uid"].astype(str)
            d = base.drop(columns=["p1", "p1n"], errors="ignore").merge(
                p1, on="segment_uid", how="left")
            m, n = fit(d)
            b = m.params["p1"] if m is not None else np.nan
            p = m.pvalues["p1"] if m is not None else np.nan
            prev = 100 * d["p1"].mean()
            line[f"prev_{vlabel}"] = prev
            line[f"beta_{vlabel}"] = b
            line[f"p_{vlabel}"] = p
            cells.append(f"{prev:>8.1f}{b:>9.4f}{p:>8.4f}")
        rows.append(line)
        print(f"  {c:<15}" + "".join(cells))
    return rows


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--radius", type=int, default=800)
    ap.add_argument("--cities", nargs="*", default=None)
    args = ap.parse_args()
    conf = cfg.config()
    tr = conf["through_routes"]
    cities = args.cities or sorted(cfg.cities().keys())
    pooled = pd.read_parquet(paths.ANALYSIS / f"analysis_pooled_r{args.radius}.parquet")
    cities = [c for c in cities if c in set(pooled.city.unique())]
    print(f"Environment: {provenance.environment_stamp()}")
    print(f"Cities: {cities}")

    dflt = dict(access_r=float(tr["access_radius_m"]),
                min_span=float(tr.get("min_span_frac", 0.5)),
                k_max=int(tr["max_paths"]),
                detour=float(tr["detour_cap"]))
    rows = []
    rows += sweep(pooled, cities, conf, args.radius,
                  "A. ENDPOINT ACCESS RADIUS — how far from the segment end a local street may attach",
                  [("100m", {"access_r": 100.0}), ("200m", {"access_r": 200.0}),
                   ("300m", {"access_r": 300.0})], dflt)
    rows += sweep(pooled, cities, conf, args.radius,
                  "B. MINIMUM SPAN FRACTION — how much of the segment a route must parallel",
                  [("0.33", {"min_span": 0.33}), ("0.50", {"min_span": 0.50}),
                   ("0.67", {"min_span": 0.67})], dflt)

    out = pd.DataFrame(rows)
    fpo = paths.TABLES / f"p1_constants_sweep_r{args.radius}.csv"
    out.to_csv(fpo, index=False)
    print(f"\n  wrote {fpo.relative_to(paths.ROOT)}")
    print("\n  Note on max_paths = 5: the primary form is binary, so the cap can only")
    print("  matter for segments with 6+ edge-disjoint substitutes. It is reported for")
    print("  the count form; the binary result is invariant to it by construction.")
    provenance.log_progress("05i_p1_constants",
                            f"P1 constant sweeps at r={args.radius} m")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
