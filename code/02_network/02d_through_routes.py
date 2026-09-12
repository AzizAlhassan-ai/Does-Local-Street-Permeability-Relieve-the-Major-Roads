#!/usr/bin/env python
"""Stage 2R — the mechanism-specific predictor: substitutable local through-routes.

P1 (PRIMARY)  count of edge-disjoint LOCAL-ONLY paths connecting the same two endpoints
              the arterial segment connects, each within the detour cap (D-035, D-037,
              D-039). This is what H1 actually claims: can a trip get from one end of
              this arterial to the other without using it?
P2            count of distinct major-to-major local connections anywhere in the
              catchment, ANY orientation, per km² (D-038). Includes perpendicular
              feeders, so it measures access rather than substitution.
P3            the existing generic metrics — untouched, computed by 02b (D-042).

D-043: P1 cannot separate relief from rat-running. Both require the same structure and
both lower arterial AADT. The coefficient is a NET substitution effect.

Usage
-----
    uv run python code/02_network/02d_through_routes.py --city denver
    uv run python code/02_network/02d_through_routes.py --city denver --radii 800 \
        --export-routes-bbox   # write route geometries for the test-area map

Outputs
-------
    data/processed/<city>/through_routes_r<R>.parquet
    data/processed/<city>/p1_routes_testarea.gpkg     (with --export-routes-bbox)
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
from shapely.geometry import LineString, MultiLineString, Point, box
from shapely.ops import linemerge

from lib import cfg, paths, provenance, validate

SUPER_S, SUPER_T = "__SRC__", "__TGT__"


# NOTE: GeoSeries.sindex.query(geom, predicate) applies the predicate as
# predicate(query_geom, tree_geom) -- the OPPOSITE direction from gpd.sjoin. Using
# predicate="within" here silently returns zero matches for "points inside polygon";
# "intersects" (or "contains") is correct. This cost one full debug cycle.
def build_local_graph(local_edges: gpd.GeoDataFrame, metric: str):
    """Undirected local graph with length weights and edge geometry retained."""
    e = local_edges.to_crs(metric).copy()
    e["len_m"] = e.geometry.length
    lo = np.minimum(e["u"].values, e["v"].values)
    hi = np.maximum(e["u"].values, e["v"].values)
    e["_pair"] = list(zip(lo, hi))
    e = e.sort_values("len_m").drop_duplicates(subset="_pair").reset_index(drop=True)
    G = nx.Graph()
    for i, (pair, L) in enumerate(zip(e["_pair"], e["len_m"])):
        u, v = pair
        if u == v:
            continue
        hw = e["highway"].iloc[i] if "highway" in e.columns else None
        hw = (hw.split(",")[0] if isinstance(hw, str) else
              (hw[0] if isinstance(hw, list) and hw else str(hw)))
        if G.has_edge(u, v):
            if L < G[u][v]["length"]:
                G[u][v].update(length=float(L), eidx=i, hw=hw)
        else:
            G.add_edge(u, v, length=float(L), eidx=i, hw=hw)
    return G, e


def endpoints_of(geom):
    """First and last coordinate of a (possibly multi-part) line."""
    if geom.geom_type == "MultiLineString":
        merged = linemerge(list(geom.geoms))
        if merged.geom_type == "MultiLineString":
            parts = list(merged.geoms)
            return Point(parts[0].coords[0]), Point(parts[-1].coords[-1])
        geom = merged
    return Point(geom.coords[0]), Point(geom.coords[-1])


def disjoint_paths(G, srcs, tgts, seg_geom, seg_len, detour_cap, min_span, k_max,
                   pos):
    """Greedy edge-disjoint shortest paths, validated per path (D-037, D-039).

    D-037a (amendment): the detour baseline is the arterial distance between the
    path's OWN access points, not the full segment length. Access nodes sit up to
    `access_radius` inside each end of the segment, so comparing a shortened local
    path against the full segment length flattered every route -- it produced a
    median 'detour ratio' of 0.93, i.e. substitutes apparently shorter than the road
    they substitute for, which is impossible. Each path's endpoints are projected
    onto the segment geometry; the arterial-equivalent distance is the gap between
    those projections, and a path must also span at least `min_span` of the segment
    to count as a substitute for it rather than a shortcut around one corner.
    """
    if not srcs or not tgts:
        return []
    H = G.copy()
    H.add_node(SUPER_S)
    H.add_node(SUPER_T)
    for n in srcs:
        if H.has_node(n):
            H.add_edge(SUPER_S, n, length=0.0, eidx=-1)
    for n in tgts:
        if H.has_node(n):
            H.add_edge(n, SUPER_T, length=0.0, eidx=-2)
    if not H.has_node(SUPER_S) or not H.has_node(SUPER_T):
        return []
    found = []
    hard_cap = detour_cap * seg_len          # no path can beat this even at full span
    for _ in range(k_max * 3):               # allow rejects without stalling
        if len(found) >= k_max:
            break
        try:
            path = nx.shortest_path(H, SUPER_S, SUPER_T, weight="length")
        except (nx.NetworkXNoPath, nx.NodeNotFound):
            break
        core = [n for n in path if n not in (SUPER_S, SUPER_T)]
        if len(core) < 2:
            for a, b in zip(path[:-1], path[1:]):
                if H.has_edge(a, b):
                    H.remove_edge(a, b)
            continue
        L = sum(H[a][b]["length"] for a, b in zip(core[:-1], core[1:]))
        if L > hard_cap:
            break                            # shortest remaining is already too long
        # per-path validation against its own access points
        try:
            a_m = seg_geom.project(Point(*pos[core[0]]))
            b_m = seg_geom.project(Point(*pos[core[-1]]))
        except Exception:
            a_m = b_m = 0.0
        arterial_equiv = abs(b_m - a_m)
        span_frac = arterial_equiv / seg_len if seg_len > 0 else 0.0
        ratio = L / arterial_equiv if arterial_equiv > 1.0 else np.inf
        if span_frac >= min_span and ratio <= detour_cap:
            found.append((core, L, ratio, span_frac))
        for a, b in zip(core[:-1], core[1:]):
            if H.has_edge(a, b):
                H.remove_edge(a, b)
    return found


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--city", default=None)
    ap.add_argument("--radii", type=int, nargs="*", default=None)
    ap.add_argument("--detour", type=float, default=None)
    ap.add_argument("--export-routes-bbox", action="store_true",
                    help="also write P1 route geometries inside the config test bbox")
    # D-088 ablation switches. P1's contribution is claimed to be its RESTRICTIONS —
    # local-only, endpoint-anchored, detour-capped, per-segment — so each has to be
    # removable one at a time. Use with PIPE_VARIANT so the primary outputs stand.
    ap.add_argument("--graph", choices=["local", "all"], default="local",
                    help="'all' drops the local-only restriction: the alternative route "
                         "may use major roads, excluding the segment's own carriageway")
    ap.add_argument("--no-span", action="store_true",
                    help="drop the minimum-span requirement")
    ap.add_argument("--access-radius", type=float, default=None,
                    help="override the endpoint access radius (m) for the sweep")
    args = ap.parse_args()

    conf = cfg.config()
    city = args.city or conf["project"]["pilot_city"]
    C = cfg.city(city)
    metric = conf["crs"]["metric"]
    tr_cfg = conf.get("through_routes", {})
    detour = args.detour or float(tr_cfg.get("detour_cap", 1.5))
    access_r = float(args.access_radius or tr_cfg.get("access_radius_m", 200.0))
    k_max = int(tr_cfg.get("max_paths", 5))
    short_flag = float(tr_cfg.get("short_segment_m", 500.0))
    min_span = 0.0 if args.no_span else float(tr_cfg.get("min_span_frac", 0.5))
    qcfg = tr_cfg.get("quality", {})
    qspeed = {k: float(v) for k, v in (qcfg.get("local_speed_kmh") or {}).items()}
    qdef = float(qcfg.get("local_speed_default_kmh", 40))
    qart = {int(k): float(v) for k, v in (qcfg.get("arterial_speed_kmh") or {}).items()}
    qartdef = float(qcfg.get("arterial_speed_default_kmh", 56))
    qdelay = float(qcfg.get("intersection_delay_s", 6.0))
    qcap = float(qcfg.get("time_cap", 1.5))

    print(f"Environment: {provenance.environment_stamp()}")
    print(f"City: {city} | detour cap {detour}x | access radius {access_r:.0f} m "
          f"| max paths {k_max} | min span {min_span}")

    loc_fp = paths.raw(city, "osm") / "network_urban_area_local.gpkg"
    maj_fp = paths.raw(city, "osm") / "network_urban_area_major.gpkg"
    seg_fp = paths.processed(city) / "segments.parquet"
    for fp, s in ((loc_fp, "01a"), (maj_fp, "01a"), (seg_fp, "02a")):
        if not fp.exists():
            print(f"ERROR: {fp.relative_to(paths.ROOT)} missing (run {s}).")
            return 1

    print("\n=== building local graph ===")
    if args.graph == "all":
        all_fp = paths.raw(city, "osm") / "network_urban_area_all.gpkg"
        print(f"  !! ABLATION --graph all: the route search may use major roads too")
        G, edf = build_local_graph(gpd.read_file(all_fp, layer="edges"), metric)
    else:
        G, edf = build_local_graph(gpd.read_file(loc_fp, layer="edges"), metric)
    print(f"  local graph: {G.number_of_nodes():,} nodes, {G.number_of_edges():,} edges")
    # Positional index over edf so that a graph edge's `eidx` addresses this series.
    emid_idx = gpd.GeoSeries(
        [g.interpolate(0.5, normalized=True) for g in edf.geometry],
        crs=metric).sindex if args.graph == "all" else None

    nodes_all = gpd.read_file(paths.raw(city, "osm") / "network_urban_area_all.gpkg",
                              layer="nodes").to_crs(metric)
    nodes_all = nodes_all[nodes_all["osmid"].isin(G.nodes)].reset_index(drop=True)
    node_gdf = gpd.GeoDataFrame({"osmid": nodes_all["osmid"].values},
                                geometry=nodes_all.geometry.values, crs=metric)
    nidx = node_gdf.sindex
    pos = dict(zip(node_gdf["osmid"].values,
                   zip(node_gdf.geometry.x.values, node_gdf.geometry.y.values)))
    print(f"  local nodes with geometry: {len(node_gdf):,}")

    # major nodes, for P2
    maj = gpd.read_file(maj_fp, layer="edges").to_crs(metric)
    maj_nodes = set(maj["u"]).union(set(maj["v"]))
    local_on_major = node_gdf[node_gdf["osmid"].isin(maj_nodes)].copy()
    print(f"  local nodes that touch the major network (P2 anchors): "
          f"{len(local_on_major):,}")
    lom_idx = local_on_major.sindex

    seg = gpd.read_parquet(seg_fp).to_crs(metric)
    print(f"  analysis segments: {len(seg):,}")

    radii = args.radii or conf["catchment"]["radii_m"]
    primary = conf["catchment"]["primary_radius_m"]
    written, route_records = [], []

    for r in radii:
        cat_fp = paths.processed(city) / f"catchments_r{r}.parquet"
        if not cat_fp.exists():
            print(f"\n  SKIP r={r}: catchments missing")
            continue
        cat = gpd.read_parquet(cat_fp).to_crs(metric).set_index("segment_uid")
        tag = "  [PRIMARY]" if r == primary else ""
        print(f"\n=== P1/P2 at r={r} m{tag} ===")
        t0 = time.time()
        rows = []
        for i, srow in enumerate(seg.itertuples()):
            uid = srow.segment_uid
            geom = srow.geometry
            seg_len = geom.length
            if uid not in cat.index:
                rows.append({"segment_uid": uid})
                continue
            buf = cat.loc[uid, "geometry"]

            # local subgraph inside the catchment (D-036)
            cand = list(nidx.query(buf, predicate="intersects"))
            sub_nodes = set(node_gdf["osmid"].iloc[cand])
            Gs = G.subgraph(sub_nodes)
            if args.graph == "all":
                # The segment's own carriageway is in this graph, so the search would
                # trivially "substitute" the road for itself. Remove every edge whose
                # midpoint lies within 30 m of the segment before searching.
                Gs = nx.Graph(Gs)
                near = set(emid_idx.query(geom.buffer(30.0), predicate="intersects"))
                for a, b, dat in list(Gs.edges(data=True)):
                    if dat.get("eidx") in near:
                        Gs.remove_edge(a, b)

            p1_start, p1_end = endpoints_of(geom)
            srcs = [node_gdf["osmid"].iloc[j] for j in
                    nidx.query(p1_start.buffer(access_r), predicate="intersects")]
            tgts = [node_gdf["osmid"].iloc[j] for j in
                    nidx.query(p1_end.buffer(access_r), predicate="intersects")]
            srcs = [n for n in srcs if n in sub_nodes]
            tgts = [n for n in tgts if n in sub_nodes]
            overlap = set(srcs) & set(tgts)
            srcs = [n for n in srcs if n not in overlap]
            tgts = [n for n in tgts if n not in overlap]

            paths_found = disjoint_paths(Gs, srcs, tgts, geom, seg_len, detour,
                                        min_span, k_max, pos)

            # P2: distinct local connections between DIFFERENT major-touching nodes
            lom = list(lom_idx.query(buf, predicate="intersects"))
            p2_anchors = [local_on_major["osmid"].iloc[j] for j in lom]
            p2_anchors = [n for n in p2_anchors if n in sub_nodes]
            p2 = 0
            if len(p2_anchors) >= 2:
                Hs = Gs.subgraph(sub_nodes)
                comp = {n: c for c, nodes in enumerate(nx.connected_components(Hs))
                        for n in nodes}
                from collections import Counter
                cc = Counter(comp[n] for n in p2_anchors if n in comp)
                # D-038a: count INDEPENDENT connections, not pairs. A component
                # holding n major-touching anchors ties them together with n-1
                # independent links; the pair count n(n-1)/2 grows quadratically and
                # produced values up to 2,851/km2, which is not a usable measure.
                p2 = sum(max(0, v - 1) for v in cc.values())

            # --- D-058 route quality on the BEST (shortest) candidate ---------
            q = {}
            if paths_found:
                core, L, ratio, span = min(paths_found, key=lambda p: p[1])
                n_int = max(0, len(core) - 2)          # interior nodes traversed
                chord = 0.0
                if core[0] in pos and core[-1] in pos:
                    (x0, y0), (x1, y1) = pos[core[0]], pos[core[-1]]
                    chord = float(np.hypot(x1 - x0, y1 - y0))
                t_route = 0.0
                for a, b in zip(core[:-1], core[1:]):
                    ed = Gs[a][b]
                    v_kmh = qspeed.get(ed.get("hw"), qdef)
                    t_route += ed["length"] / (v_kmh / 3.6)
                t_route += n_int * qdelay
                v_art = qart.get(int(srow.f_system), qartdef) if hasattr(srow, "f_system") else qartdef
                t_art = (seg_len * span) / (v_art / 3.6)
                q = {"p1_best_circuity": (L / chord) if chord > 1 else np.nan,
                     "p1_best_n_intersections": n_int,
                     "p1_best_int_per_km": n_int / (L / 1000) if L > 0 else np.nan,
                     "p1_best_time_ratio": (t_route / t_art) if t_art > 0 else np.nan,
                     "p1q_any": int((t_route / t_art) <= qcap) if t_art > 0 else 0}
            else:
                q = {"p1_best_circuity": np.nan, "p1_best_n_intersections": np.nan,
                     "p1_best_int_per_km": np.nan, "p1_best_time_ratio": np.nan,
                     "p1q_any": 0}

            rec = {
                "segment_uid": uid,
                "p1_routes": len(paths_found),
                "p1_any": int(len(paths_found) > 0),
                "p1_min_detour": (min(p[2] for p in paths_found)
                                  if paths_found else np.nan),
                "p1_min_span": (max(p[3] for p in paths_found)
                                if paths_found else np.nan),
                "p2_pairs": p2,
                "p2_pairs_per_km2": p2 / float(cat.loc[uid, "catch_area_km2"]),
                "p1_short_segment": int(seg_len < short_flag),
                "seg_len_m": seg_len,
                "n_src_nodes": len(srcs),
                "n_tgt_nodes": len(tgts),
                **q,
            }
            rows.append(rec)

            if args.export_routes_bbox and r == primary and paths_found:
                route_records.append((uid, paths_found, Gs))

            if (i + 1) % 500 == 0:
                el = time.time() - t0
                print(f"    {i+1:,}/{len(seg):,} segments  ({el:.0f}s elapsed, "
                      f"{el/(i+1)*1000:.1f} ms/segment)")

        out = pd.DataFrame(rows)
        el = time.time() - t0
        print(f"  done in {el/60:.2f} min ({el/len(seg)*1000:.1f} ms/segment)")

        p1 = out["p1_routes"].fillna(0)
        print(f"\n  P1 (substitutable edge-disjoint routes):")
        print(f"    zero      : {int((p1==0).sum()):,} ({(p1==0).mean():.1%})")
        print(f"    distribution: {p1.value_counts().sort_index().to_dict()}")
        print(f"    min {p1.min():.0f} | median {p1.median():.0f} | "
              f"mean {p1.mean():.2f} | max {p1.max():.0f}")
        print(f"    p1_any = 1 on {int(out['p1_any'].sum()):,} "
              f"({out['p1_any'].mean():.1%})")
        md = out["p1_min_detour"].dropna()
        if len(md):
            print(f"    detour ratio of best route: median {md.median():.2f}, "
                  f"p90 {md.quantile(.9):.2f} (cap {detour})")
        print(f"    short segments flagged (<{short_flag:.0f} m): "
              f"{int(out['p1_short_segment'].sum()):,}")
        if "p1q_any" in out.columns:
            print(f"    D-058 quality-adjusted: p1q_any = 1 on "
                  f"{int(out['p1q_any'].sum()):,} ({out['p1q_any'].mean():.1%}) "
                  f"vs p1_any {out['p1_any'].mean():.1%}")
            wq = out[out["p1_any"] == 1]
            if len(wq):
                print(f"    best-route quality (where a route exists): "
                      f"circuity med {wq['p1_best_circuity'].median():.2f}, "
                      f"intersections/km med {wq['p1_best_int_per_km'].median():.1f}, "
                      f"time ratio med {wq['p1_best_time_ratio'].median():.2f}")
        p2s = out["p2_pairs_per_km2"]
        print(f"  P2 (major-to-major local connections per km²): "
              f"median {p2s.median():.2f}, p90 {p2s.quantile(.9):.2f}, "
              f"max {p2s.max():.2f}, zero on {int((p2s==0).sum()):,}")

        fp = paths.processed(city) / f"through_routes_r{r}.parquet"
        out.to_parquet(fp, index=False)
        written.append((r, fp, len(out)))
        print(f"  wrote {fp.relative_to(paths.ROOT)}")

    # --- export route geometries for the test-area map ---------------------
    if args.export_routes_bbox and route_records:
        w, s, e, n = C["test_area"]["bbox_wsen"]
        tb = gpd.GeoSeries([box(w, s, e, n)], crs="EPSG:4326").to_crs(metric).iloc[0]
        pos = {r.osmid: (r.geometry.x, r.geometry.y)
               for r in node_gdf.itertuples()}
        recs = []
        for uid, paths_found, Gs in route_records:
            for pi, (core, L, _ratio, _span) in enumerate(paths_found):
                coords = [pos[n] for n in core if n in pos]
                if len(coords) < 2:
                    continue
                ls = LineString(coords)
                if ls.intersects(tb):
                    recs.append({"segment_uid": uid, "path_rank": pi,
                                 "path_len_m": L, "geometry": ls})
        if recs:
            g = gpd.GeoDataFrame(recs, crs=metric).to_crs("EPSG:4326")
            fp = paths.processed(city) / "p1_routes_testarea.gpkg"
            g.to_file(fp, layer="routes", driver="GPKG")
            print(f"\n  wrote {len(g):,} P1 route geometries intersecting the test "
                  f"bbox -> {fp.relative_to(paths.ROOT)}")

    for r, fp, nrow in written:
        provenance.log(city=city, layer=f"through_routes_r{r}",
                       source_url="derived: 01a local/major subgraphs + 02a catchments",
                       rows=nrow, file_path=fp)
    provenance.log_progress(
        "02d_through_routes",
        f"{city}: P1/P2 computed at {[r for r, _, _ in written]} m, "
        f"detour cap {detour}x",
    )
    print("\nStage 2R complete.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
