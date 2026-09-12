#!/usr/bin/env python
"""Stage 2c — arterial betweenness centrality: H2's moderator (b).

H2 asks whether relief depends on the arterial's through-traffic ROLE in the wider
network. Betweenness on the metropolitan major-road graph is the proxy.

Design choices, both reported:
  * Computed on the MAJOR subgraph only. At metropolitan scale, through-traffic
    routes on the major network; residential streets are not viable long-distance
    alternatives, and including 165k local edges would multiply cost ~4x for
    negligible change in the ranking of arterials.
  * DISTANCE-WEIGHTED (weight='length'), not hop-count. Unweighted betweenness on a
    road network rewards topologically short but physically long detours.
  * Exact betweenness is O(V*E) and infeasible here, so Brandes pivot sampling is
    used with k from config (network.betweenness_k_pivots). k is reported, and a
    stability check re-runs at k/2 with a different seed so the sampling error is
    visible rather than assumed.

Depends on: 01a (--extent urban_area), 02a

Usage
-----
    uv run python code/02_network/02c_betweenness.py --city denver
    uv run python code/02_network/02c_betweenness.py --city denver --k 100 --timing-only

Outputs
-------
    data/processed/<city>/segment_betweenness.parquet
"""

from __future__ import annotations

import argparse
import pathlib
import sys
import time

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

import geopandas as gpd
import networkx as nx
import numpy as np
import pandas as pd

from lib import cfg, paths, provenance, validate


def build_major_graph(edges: gpd.GeoDataFrame, metric: str) -> tuple[nx.Graph, gpd.GeoDataFrame]:
    """Undirected simple major-road graph with 'length' weights in metres."""
    e = edges.to_crs(metric).copy()
    e["seg_len_m"] = e.geometry.length
    lo = np.minimum(e["u"].values, e["v"].values)
    hi = np.maximum(e["u"].values, e["v"].values)
    e["_pair"] = list(zip(lo, hi))
    before = len(e)
    # Where a two-way street yields two directed edges, keep the shorter geometry.
    e = e.sort_values("seg_len_m").drop_duplicates(subset="_pair").copy()
    print(f"  major edges: {before:,} directed -> {len(e):,} undirected")
    G = nx.Graph()
    for (u, v), L in zip(e["_pair"], e["seg_len_m"]):
        if u == v:
            continue                       # self loops carry no through-movement
        if G.has_edge(u, v):
            G[u][v]["length"] = min(G[u][v]["length"], float(L))
        else:
            G.add_edge(u, v, length=float(L))
    print(f"  graph: {G.number_of_nodes():,} nodes, {G.number_of_edges():,} edges")
    comps = sorted(nx.connected_components(G), key=len, reverse=True)
    print(f"  connected components: {len(comps):,} "
          f"(largest holds {len(comps[0]):,} = {len(comps[0])/G.number_of_nodes():.1%} of nodes)")
    return G, e


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--city", default=None)
    ap.add_argument("--k", type=int, default=None, help="override pivot count")
    ap.add_argument("--timing-only", action="store_true",
                    help="time a small-k run and exit without writing")
    args = ap.parse_args()

    conf = cfg.config()
    city_key = args.city or conf["project"]["pilot_city"]
    C = cfg.city(city_key)
    metric = conf["crs"]["metric"]
    seed = conf["reproducibility"]["random_seed"]
    k = args.k or conf["network"]["betweenness_k_pivots"]

    print(f"Environment: {provenance.environment_stamp()}")
    print(f"City: {city_key} ({C['label']})")

    maj_fp = paths.raw(city_key, "osm") / "network_urban_area_major.gpkg"
    seg_fp = paths.processed(city_key) / "segments.parquet"
    for fp, s in ((maj_fp, "01a --extent urban_area"), (seg_fp, "02a")):
        if not fp.exists():
            print(f"ERROR: {fp.relative_to(paths.ROOT)} missing. Run {s} first.")
            return 1

    print("\n=== major-road graph ===")
    G, emaj = build_major_graph(gpd.read_file(maj_fp, layer="edges"), metric)

    kk = min(k, G.number_of_nodes())
    print(f"\n=== edge betweenness (Brandes, k={kk:,} pivots, weight=length) ===")
    t0 = time.time()
    eb = nx.edge_betweenness_centrality(G, k=kk, weight="length", seed=seed)
    t1 = time.time() - t0
    print(f"  computed in {t1/60:.1f} min ({t1:.0f} s) for {len(eb):,} edges")

    if args.timing_only:
        rate = t1 / kk
        full = conf["network"]["betweenness_k_pivots"]
        print(f"  per-pivot: {rate:.3f} s -> projected for k={full:,}: "
              f"{rate*full/60:.1f} min")
        print("  timing-only: nothing written.")
        return 0

    # --- sampling stability: half the pivots, different seed ----------------
    k2 = max(2, kk // 2)
    print(f"\n  stability check at k={k2:,}, seed+1 ...")
    eb2 = nx.edge_betweenness_centrality(G, k=k2, weight="length", seed=seed + 1)
    common = list(set(eb) & set(eb2))
    a = np.array([eb[e] for e in common])
    b = np.array([eb2[e] for e in common])
    print(f"    Pearson r  = {np.corrcoef(a, b)[0,1]:.4f}")
    print(f"    Spearman r = {pd.Series(a).corr(pd.Series(b), method='spearman'):.4f}")
    print("    (high rank correlation => pivot sampling is adequate for a moderator)")

    # --- attach to major edges ----------------------------------------------
    emaj = emaj.reset_index(drop=True)
    emaj["betweenness"] = [
        eb.get((u, v), eb.get((v, u), np.nan)) for u, v in emaj["_pair"]
    ]
    n_nan = int(emaj["betweenness"].isna().sum())
    print(f"\n  major edges with betweenness: {len(emaj)-n_nan:,} (NaN {n_nan})")
    bt = emaj["betweenness"].dropna()
    print(f"  betweenness: min {bt.min():.3e}, median {bt.median():.3e}, "
          f"p90 {bt.quantile(.9):.3e}, max {bt.max():.3e}")

    # --- map HPMS segments to nearest major OSM edge ------------------------
    # This doubles as an early feasibility check on Stage 3 conflation.
    seg = gpd.read_parquet(seg_fp).to_crs(metric)
    seg_pts = gpd.GeoDataFrame(
        seg[["segment_uid", "f_system"]].reset_index(drop=True),
        geometry=[g.interpolate(0.5, normalized=True) for g in seg.geometry],
        crs=metric,
    )
    edge_pts = gpd.GeoDataFrame(
        emaj[["betweenness", "highway"]].reset_index(drop=True),
        geometry=[g.interpolate(0.5, normalized=True) for g in emaj.geometry],
        crs=metric,
    ).dropna(subset=["betweenness"])

    print(f"\n=== mapping {len(seg_pts):,} HPMS segments to nearest major OSM edge ===")
    j = gpd.sjoin_nearest(seg_pts, edge_pts, how="left", distance_col="match_dist_m")
    j = j.drop_duplicates(subset="segment_uid")
    d = j["match_dist_m"]
    print(f"  match distance (m): median {d.median():.1f}, p90 {d.quantile(.9):.1f}, "
          f"p99 {d.quantile(.99):.1f}, max {d.max():.1f}")
    for thr in (50, 100, 250, 500):
        print(f"    within {thr:>3} m: {int((d<=thr).sum()):,} ({(d<=thr).mean():.1%})")
    print("  NOTE: this is midpoint-to-midpoint distance, so short HPMS segments "
          "against long OSM edges inflate it. Stage 3 will conflate properly by "
          "geometry overlap; this is a feasibility signal only.")

    out = j[["segment_uid", "betweenness", "match_dist_m"]].rename(
        columns={"betweenness": "arterial_betweenness"}
    ).copy()
    # D-026: refuse to carry a moderator value derived from a far-away edge.
    max_d = conf["network"]["betweenness_max_match_dist_m"]
    bad = out["match_dist_m"] > max_d
    out["betweenness_matched"] = ~bad
    out.loc[bad, "arterial_betweenness"] = np.nan
    print(f"\n  D-026: match distance > {max_d} m on {int(bad.sum()):,} segments "
          f"({bad.mean():.1%}) -> arterial_betweenness set to NA")
    print("    these are HPMS segments with no nearby OSM major edge; they are "
          "flagged (betweenness_matched=False), not silently imputed.")
    print(f"\n  segments with a betweenness value: "
          f"{int(out['arterial_betweenness'].notna().sum()):,}/{len(out):,}")
    validate.report_df(out, "Segment betweenness",
                       key_cols=["arterial_betweenness", "match_dist_m"])

    fp = paths.processed(city_key) / "segment_betweenness.parquet"
    out.to_parquet(fp, index=False)
    print(f"  wrote {fp.relative_to(paths.ROOT)} ({fp.stat().st_size/1e6:.2f} MB)")

    provenance.log(city=city_key, layer="segment_betweenness",
                   source_url="derived: 01a major subgraph",
                   rows=len(out), file_path=fp)
    provenance.log_progress(
        "02c_betweenness",
        f"{city_key}: edge betweenness on {G.number_of_edges():,}-edge major graph "
        f"(k={kk}, weighted) mapped to {len(out):,} HPMS segments in {t1/60:.1f} min",
    )
    print("\nStage 2c complete.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
