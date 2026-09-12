#!/usr/bin/env python
"""Stage 5 — the comparators on their STANDARD constructions (D-087).

The measurement claim was tested against generic connectivity and angular choice as we
compute them: on the local-only subgraph inside an 800 m catchment. A referee replied
that this is not how either family is normally computed, and that the objection
dissolves the test:

  * The P3 metrics as written into subdivision codes, and as used by the prior
    literature, are WHOLE-NETWORK quantities aggregated to an areal unit — which is
    exactly the cell-level construction our own Layer 1 uses.
  * Normalised angular choice is a WHOLE-SYSTEM measure, and the space-syntax
    tradition offers MAIN-ROAD choice as the predictor of vehicular flow. Computing it
    on the local subgraph and reporting that it behaves like a fabric measure is a
    consequence of our construction, not a finding about angular choice.

This script therefore adds, for every segment:
  A. cell-level whole-network P3 (intersection density, link–node ratio, % four-way,
     median block size) — Choi and Ewing's own construction, joined by cell;
  B. full-network NACH computed over major AND local edges together, reported two
     ways: the value ON the arterial segment itself (the steelman: main-road choice)
     and the catchment mean (comparable to the local-only version already reported).

If the null survives on these constructions the measurement claim is earned. If it does
not, the claim has to be restated as one about catchment-scale local-fabric metrics.

Usage
-----
    uv run python code/05_model/05s_standard_comparators.py
"""
from __future__ import annotations
import argparse, math, os, pathlib, sys
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
import geopandas as gpd, networkx as nx, numpy as np, pandas as pd
import statsmodels.formula.api as smf
from lib import cfg, paths, provenance

CTRL = ["pop_density_km2_z", "job_density_km2_z", "lu_entropy_z", "dist_cbd_km_c_z",
        "dist_cbd_km_c_sq_z", "median_year_z", "through_lanes_z"]
R = 800
CELL_P3 = {"int_density_all": "cell intersection density",
           "link_node_all": "cell link–node ratio",
           "pct_4way_all": "cell % four-way",
           "median_block_acres": "cell median block size"}


def z(s):
    sd = s.std(ddof=0)
    return (s - s.mean()) / sd if sd and sd > 0 else s * 0.0


def prep(d):
    # D-094: match the estimation sample used everywhere else, so the P1 coefficient
    # printed beside each comparator is the same quantity as in the primary table.
    floor = float(os.environ.get("MIN_SEG_LEN_M", "0"))
    if floor:
        d = d[d["length_m"] >= floor]
    d = d.copy()
    src = {"pop_density_km2_z": "pop_density_km2", "job_density_km2_z": "job_density_km2",
           "lu_entropy_z": "lu_entropy",
           "dist_cbd_km_c_z": "dist_cbd_km_c", "dist_cbd_km_c_sq_z": "dist_cbd_km_c_sq",
           "median_year_z": "median_year_structure_built",
           "through_lanes_z": "through_lanes"}
    g = d.groupby("city")
    for dst, s in src.items():
        d[dst] = g[s].transform(z)
    d["p1"] = d["p1_any"].astype(float)
    d["y"] = d["log_aadt"]
    return d.dropna(subset=["y", "p1", "cell_id", "route_id", "f_system"] + CTRL).copy()


def fit(d, f):
    try:
        return smf.mixedlm(f, d, groups=d["cell_id"]).fit(method="lbfgs", reml=True)
    except Exception as e:
        print(f"    !! {e}")
        return None


def bearing(geom):
    c = list(geom.coords)
    return math.atan2(c[-1][1] - c[0][1], c[-1][0] - c[0][0])


def nach_full(city, metric, k=400, seed=7):
    """Normalised angular choice on the FULL network — major and local edges together.

    Returns, per analysis segment: `nach_seg` (the choice value of the nearest major
    edge to the segment's midpoint — main-road choice, the space-syntax predictor of
    vehicular flow) and `nach_catch` (the catchment mean over all edges).
    """
    fp = paths.raw(city, "osm") / "network_urban_area_all.gpkg"
    e = gpd.read_file(fp, layer="edges").to_crs(metric)
    e = e[e.geometry.type == "LineString"].reset_index(drop=True)
    lo = np.minimum(e["u"].values, e["v"].values)
    hi = np.maximum(e["u"].values, e["v"].values)
    e["_pair"] = list(zip(lo, hi))
    e = e.drop_duplicates("_pair").reset_index(drop=True)
    ang = np.array([bearing(g) for g in e.geometry])
    at_node = {}
    for i, (u, v) in enumerate(zip(e["u"].values, e["v"].values)):
        at_node.setdefault(u, []).append(i)
        at_node.setdefault(v, []).append(i)
    D = nx.Graph()
    D.add_nodes_from(range(len(e)))
    for segs in at_node.values():
        for a in range(len(segs)):
            for b in range(a + 1, len(segs)):
                i, j = segs[a], segs[b]
                dth = abs(ang[i] - ang[j]) % (2 * math.pi)
                dth = min(dth, 2 * math.pi - dth)
                dth = min(dth, math.pi - dth) if dth > math.pi / 2 else dth
                D.add_edge(i, j, w=float(dth) + 1e-3)
    kk = min(k, D.number_of_nodes())
    ch = nx.betweenness_centrality(D, k=kk, weight="w", seed=seed, normalized=False)
    depth = max(np.mean([d for _, d in D.degree()]), 1.0)
    e["nach"] = [math.log(ch.get(i, 0.0) + 1.0) / math.log(depth + 3.0)
                 for i in range(len(e))]

    seg = gpd.read_parquet(paths.processed(city) / "segments.parquet").to_crs(metric)
    mids = gpd.GeoDataFrame(seg[["segment_uid"]],
                            geometry=[g.interpolate(.5, normalized=True)
                                      for g in seg.geometry], crs=metric)
    # main-road choice: nearest full-network edge to the arterial's own midpoint
    near = gpd.sjoin_nearest(mids, e[["nach", "geometry"]], how="left",
                             max_distance=500, distance_col="_d")
    near = near.drop_duplicates("segment_uid")[["segment_uid", "nach"]]
    near = near.rename(columns={"nach": "nach_seg"})

    emid = gpd.GeoDataFrame(e[["nach"]],
                            geometry=[g.interpolate(.5, normalized=True)
                                      for g in e.geometry], crs=metric)
    cat = gpd.read_parquet(paths.processed(city) / f"catchments_r{R}.parquet").to_crs(metric)
    j = gpd.sjoin(emid, cat[["segment_uid", "geometry"]], how="inner", predicate="within")
    catm = j.groupby("segment_uid")["nach"].mean().rename("nach_catch").reset_index()

    out = near.merge(catm, on="segment_uid", how="outer")
    out["segment_uid"] = city + "|" + out["segment_uid"].astype(str)
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--skip-nach", action="store_true")
    args = ap.parse_args()
    conf = cfg.config(); metric = conf["crs"]["metric"]
    d = prep(pd.read_parquet(paths.ANALYSIS / f"analysis_pooled_r{R}.parquet"))
    base = " + ".join(CTRL) + " + C(f_system)"
    cities = sorted(d.city.unique())
    print(f"Environment: {provenance.environment_stamp()}\nn = {len(d):,}")
    rows = []

    # ------------------------------------------------------------------ A
    print(f"\n{'='*100}\nA. CELL-LEVEL WHOLE-NETWORK P3 — Choi and Ewing's own construction"
          f"\n{'='*100}")
    cm = pd.concat([pd.read_parquet(paths.processed(c) / "cell_metrics.parquet")
                    .assign(cell_id=lambda t, c=c: c + "|" + t["cell_id"].astype(str))
                    for c in cities], ignore_index=True)
    dd = d.merge(cm[["cell_id"] + list(CELL_P3)], on="cell_id", how="left")
    for m in CELL_P3:
        dd[f"{m}_z"] = dd.groupby("city")[m].transform(z)
    print(f"  {'metric':<30}{'UNCONDITIONAL β':>22}{'CONDITIONAL on P1':>24}"
          f"{'P1 in that model':>20}{'n':>9}")
    for m, lab in CELL_P3.items():
        g = dd.dropna(subset=[f"{m}_z"])
        r_u = fit(g, f"y ~ {base} + C(city) + {m}_z")
        r_c = fit(g, f"y ~ {base} + C(city) + p1 + {m}_z")
        if r_u is None or r_c is None:
            continue
        bu, pu = r_u.params[f"{m}_z"], r_u.pvalues[f"{m}_z"]
        bc, pc = r_c.params[f"{m}_z"], r_c.pvalues[f"{m}_z"]
        bp, pp = r_c.params["p1"], r_c.pvalues["p1"]
        print(f"  {lab:<30}{bu:>+13.4f} (p={pu:5.3f}){bc:>+15.4f} (p={pc:5.3f})"
              f"{bp:>+11.4f} (p={pp:5.3f}){len(g):>9,}")
        rows.append({"check": "cell_p3", "metric": lab, "n": len(g), "beta_uncond": bu,
                     "p_uncond": pu, "beta_cond": bc, "p_cond": pc,
                     "p1_beta": bp, "p1_p": pp})
    print("\n  -> these are whole-network, cell-level metrics: the construction the")
    print("     standards use and the prior literature reports.")

    # ------------------------------------------------------------------ B
    if not args.skip_nach:
        print(f"\n{'='*100}\nB. FULL-NETWORK NORMALISED ANGULAR CHOICE (major + local)"
              f"\n{'='*100}")
        parts = []
        for c in cities:
            try:
                parts.append(nach_full(c, metric))
                print(f"  {c}: full-network NACH computed")
            except Exception as e:
                print(f"  {c}: FAILED ({e})")
        if parts:
            nf = pd.concat(parts, ignore_index=True)
            dn = d.merge(nf, on="segment_uid", how="left")
            for v in ("nach_seg", "nach_catch"):
                dn[f"{v}_z"] = dn.groupby("city")[v].transform(z)
            print(f"\n  {'construction':<34}{'UNCONDITIONAL β':>22}"
                  f"{'CONDITIONAL on P1':>24}{'P1 in that model':>20}{'n':>9}")
            for v, lab in (("nach_seg", "NACH on the arterial itself"),
                           ("nach_catch", "NACH, catchment mean (full net)")):
                g = dn.dropna(subset=[f"{v}_z"])
                r_u = fit(g, f"y ~ {base} + C(city) + {v}_z")
                r_c = fit(g, f"y ~ {base} + C(city) + p1 + {v}_z")
                if r_u is None or r_c is None:
                    continue
                bu, pu = r_u.params[f"{v}_z"], r_u.pvalues[f"{v}_z"]
                bc, pc = r_c.params[f"{v}_z"], r_c.pvalues[f"{v}_z"]
                bp, pp = r_c.params["p1"], r_c.pvalues["p1"]
                print(f"  {lab:<34}{bu:>+13.4f} (p={pu:5.3f}){bc:>+15.4f} (p={pc:5.3f})"
                      f"{bp:>+11.4f} (p={pp:5.3f}){len(g):>9,}")
                rows.append({"check": "nach_full", "metric": lab, "n": len(g),
                             "beta_uncond": bu, "p_uncond": pu, "beta_cond": bc,
                             "p_cond": pc, "p1_beta": bp, "p1_p": pp})
                print(f"    corr with P1 = {g[[f'{v}_z','p1']].corr().iloc[0,1]:+.3f}")

    out = pd.DataFrame(rows)
    fp = paths.TABLES / "standard_comparators.csv"
    out.to_csv(fp, index=False)
    print(f"\n  wrote {fp.relative_to(paths.ROOT)}")
    provenance.log_progress("05s_standard_comparators",
                            "whole-network cell P3 and full-network NACH (D-087)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
