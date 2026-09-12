#!/usr/bin/env python
"""Stage 2b — compute local-network permeability metrics for every catchment.

This produces the study's KEY PREDICTOR. Metrics are computed ONLY on the local
subgraph (D-001/D-023), so they can never partly measure the arterial network that
supplies the outcome.

Two things that are easy to get wrong and are handled explicitly here:
  1. OSMnx returns a MultiDiGraph, so a two-way street appears as TWO directed edges.
     Link-node ratio and edge counts must be computed on the UNDIRECTED simple graph
     or every count is inflated ~2x.
  2. Node degree must be computed on the LOCAL subgraph, not the full network —
     otherwise a cul-de-sac meeting an arterial looks like a through-intersection.

D-024: edges and nodes are assigned to a catchment by whether their MIDPOINT/point
falls inside it, using full edge length. Geometric clipping of 165k edges against
9,490 x 4 buffers is O(n*m) and prohibitive; with median local edge length ~126 m
against a 800 m radius the approximation is small and does not favour either
hypothesis. Reported so it can be checked.

Depends on: 01a (--extent urban_area), 02a

Usage
-----
    uv run python code/02_network/02b_permeability.py --city denver
    uv run python code/02_network/02b_permeability.py --city denver --radii 800

Outputs
-------
    data/processed/<city>/permeability_r<R>.parquet   one per radius
"""

from __future__ import annotations

import argparse
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

import geopandas as gpd
import networkx as nx
import numpy as np
import pandas as pd

from lib import cfg, paths, provenance, validate


def undirected_local_graph(edges: gpd.GeoDataFrame) -> tuple[nx.Graph, pd.DataFrame]:
    """Build the undirected simple local graph and return it with a deduped edge table.

    OSMnx MultiDiGraph -> two directed edges per two-way street. Deduplicate on the
    unordered node pair so counts are not doubled.
    """
    e = edges.copy()
    lo = np.minimum(e["u"].values, e["v"].values)
    hi = np.maximum(e["u"].values, e["v"].values)
    e["_pair"] = list(zip(lo, hi))
    before = len(e)
    e = e.drop_duplicates(subset="_pair").copy()
    print(f"  local edges: {before:,} directed -> {len(e):,} undirected "
          f"({1 - len(e)/before:.1%} were reverse duplicates)")
    G = nx.Graph()
    G.add_edges_from(e["_pair"].tolist())
    print(f"  local undirected graph: {G.number_of_nodes():,} nodes, "
          f"{G.number_of_edges():,} edges")
    return G, e


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--city", default=None)
    ap.add_argument("--radii", type=int, nargs="*", default=None,
                    help="subset of config catchment radii (default: all)")
    args = ap.parse_args()

    conf = cfg.config()
    city_key = args.city or conf["project"]["pilot_city"]
    C = cfg.city(city_key)
    metric = conf["crs"]["metric"]

    print(f"Environment: {provenance.environment_stamp()}")
    print(f"City: {city_key} ({C['label']})")

    # --- inputs -------------------------------------------------------------
    loc_fp = paths.raw(city_key, "osm") / "network_urban_area_local.gpkg"
    all_fp = paths.raw(city_key, "osm") / "network_urban_area_all.gpkg"
    if not loc_fp.exists():
        print(f"ERROR: {loc_fp.relative_to(paths.ROOT)} missing.")
        print("Run: 01a_osm_network.py --city denver --extent urban_area")
        return 1

    print("\n=== local subgraph ===")
    local_edges = gpd.read_file(loc_fp, layer="edges")
    G, ed = undirected_local_graph(local_edges)

    # Node geometry comes from the 'all' file (nodes are shared across subgraphs);
    # degree comes from the LOCAL graph only.
    nodes_all = gpd.read_file(all_fp, layer="nodes")
    deg = pd.Series(dict(G.degree()), name="local_degree")
    nodes = nodes_all.set_index("osmid").join(deg, how="inner").reset_index()
    print(f"  local nodes with geometry: {len(nodes):,} "
          f"(of {len(nodes_all):,} network nodes)")
    dc = nodes["local_degree"].value_counts().sort_index()
    print(f"  local degree distribution: {dc.head(8).to_dict()}")
    n_dead = int((nodes["local_degree"] == 1).sum())
    n_inter = int((nodes["local_degree"] >= 3).sum())
    print(f"  dead ends (deg 1): {n_dead:,} ({n_dead/len(nodes):.1%})")
    print(f"  intersections (deg>=3): {n_inter:,} ({n_inter/len(nodes):.1%})")

    # --- geometry prep in metric CRS ---------------------------------------
    nodes_m = nodes.to_crs(metric)
    ed_gdf = gpd.GeoDataFrame(
        ed.drop(columns=["_pair"]), geometry=ed.geometry, crs=local_edges.crs
    ).to_crs(metric)
    ed_gdf["seg_len_m"] = ed_gdf.geometry.length
    # Straight-line distance between each edge's endpoints, for circuity.
    ends = ed_gdf.geometry.apply(
        lambda g: np.hypot(
            g.coords[-1][0] - g.coords[0][0], g.coords[-1][1] - g.coords[0][1]
        ) if g.geom_type == "LineString" else np.nan
    )
    ed_gdf["chord_m"] = ends
    print(f"  edge length: median {ed_gdf['seg_len_m'].median():.1f} m, "
          f"total {ed_gdf['seg_len_m'].sum()/1000:,.1f} km")
    print(f"  chord computable on {int(ed_gdf['chord_m'].notna().sum()):,}/"
          f"{len(ed_gdf):,} edges")

    # Midpoints for assignment (D-024)
    ed_pts = gpd.GeoDataFrame(
        ed_gdf[["seg_len_m", "chord_m"]].reset_index(drop=True),
        geometry=[g.interpolate(0.5, normalized=True) for g in ed_gdf.geometry],
        crs=metric,
    )

    node_pts = nodes_m[["local_degree"]].copy()
    node_pts = gpd.GeoDataFrame(node_pts.reset_index(drop=True),
                                geometry=nodes_m.geometry.values, crs=metric)

    radii = args.radii or conf["catchment"]["radii_m"]
    primary = conf["catchment"]["primary_radius_m"]
    outdir = paths.processed(city_key)
    written = []

    for r in radii:
        cat_fp = outdir / f"catchments_r{r}.parquet"
        if not cat_fp.exists():
            print(f"\n  SKIP r={r}: {cat_fp.name} missing (run 02a)")
            continue
        cat = gpd.read_parquet(cat_fp).to_crs(metric).reset_index(drop=True)
        cat["_cid"] = np.arange(len(cat))
        tag = "  [PRIMARY]" if r == primary else ""
        print(f"\n=== permeability at r={r} m ({len(cat):,} catchments){tag} ===")

        # --- node aggregation ---
        jn = gpd.sjoin(node_pts, cat[["_cid", "geometry"]], how="inner",
                       predicate="within")
        # D-066/D-067 — Marshall & Garrick's link-node ratio contracts degree-2
        # chains: a degree-2 node is not a node, and the two edges meeting there
        # are ONE link. N = #(deg==1) + #(deg>=3); L = sum(deg over those)/2.
        # The old `edges / all nodes` form was internally consistent but not
        # comparable to the published measure (gave 2.60 for Denver cells vs
        # Choi & Ewing's 1.18-1.84 range). Same construction as 02e.
        gn = jn.groupby("_cid")["local_degree"].agg(
            local_nodes="size",
            local_deadends=lambda s: int((s == 1).sum()),
            local_intersections=lambda s: int((s >= 3).sum()),
            local_mg_nodes=lambda s: int(((s == 1) | (s >= 3)).sum()),
            local_mg_links=lambda s: float(s[(s == 1) | (s >= 3)].sum()) / 2.0,
        )

        # --- edge aggregation ---
        je = gpd.sjoin(ed_pts, cat[["_cid", "geometry"]], how="inner",
                       predicate="within")
        ge = je.groupby("_cid").agg(
            local_edges=("seg_len_m", "size"),
            local_len_m=("seg_len_m", "sum"),
            local_chord_m=("chord_m", "sum"),
        )

        m = cat[["segment_uid", "route_id", "cell_id", "catch_area_km2",
                 "catch_area_in_ua_km2", "_cid"]].merge(
            gn, left_on="_cid", right_index=True, how="left"
        ).merge(ge, left_on="_cid", right_index=True, how="left")

        for c in ["local_nodes", "local_deadends", "local_intersections",
                  "local_mg_nodes", "local_mg_links",
                  "local_edges", "local_len_m", "local_chord_m"]:
            m[c] = m[c].fillna(0)

        area = m["catch_area_km2"]
        m["local_int_density"] = m["local_intersections"] / area
        m["local_street_density"] = (m["local_len_m"] / 1000) / area
        with np.errstate(divide="ignore", invalid="ignore"):
            m["local_link_node_ratio"] = np.where(
                m["local_mg_nodes"] > 0,
                m["local_mg_links"] / m["local_mg_nodes"], np.nan)
            m["local_deadend_share"] = np.where(
                m["local_nodes"] > 0, m["local_deadends"] / m["local_nodes"], np.nan)
            m["local_circuity"] = np.where(
                m["local_chord_m"] > 0, m["local_len_m"] / m["local_chord_m"], np.nan)

        n_empty = int((m["local_nodes"] == 0).sum())
        print(f"  catchments with NO local network: {n_empty:,} "
              f"({n_empty/len(m):.1%})")
        if n_empty:
            print("    -> these are arterials with no residential fabric within r "
                  "(industrial, airport, freeway frontage). Permeability is 0/NA, "
                  "not missing-at-random; flag for Stage 4.")

        cols = ["local_int_density", "local_link_node_ratio", "local_street_density",
                "local_deadend_share", "local_circuity"]
        desc = m[cols].describe(percentiles=[.1, .5, .9]).T
        print(desc[["count", "mean", "std", "10%", "50%", "90%"]].to_string(
            float_format=lambda x: f"{x:9.3f}"))

        fp = outdir / f"permeability_r{r}.parquet"
        m.drop(columns=["_cid"]).to_parquet(fp, index=False)
        written.append((r, fp, len(m)))
        print(f"  wrote {fp.relative_to(paths.ROOT)} "
              f"({fp.stat().st_size/1e6:.1f} MB)")

    # --- cross-radius correlation of the primary predictor (MAUP evidence) ---
    if len(written) > 1:
        print("\n=== MAUP: correlation of local_int_density across radii ===")
        frames = {}
        for r, fp, _ in written:
            d = pd.read_parquet(fp, columns=["segment_uid", "local_int_density"])
            frames[r] = d.set_index("segment_uid")["local_int_density"]
        corr = pd.DataFrame(frames).corr()
        print(corr.to_string(float_format=lambda x: f"{x:.3f}"))

    for r, fp, n in written:
        provenance.log(city=city_key, layer=f"permeability_r{r}",
                       source_url="derived: 01a local subgraph + 02a catchments",
                       rows=n, file_path=fp)
    provenance.log_progress(
        "02b_permeability",
        f"{city_key}: permeability metrics for {written[0][2]:,} catchments at "
        f"{[r for r, _, _ in written]} m on a {G.number_of_edges():,}-edge local graph",
    )
    print("\nStage 2b complete.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
