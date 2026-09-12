#!/usr/bin/env python
"""Stage 1a — acquire the OSM street network and split it into major / local subgraphs.

The split is the methodological crux (DECISION D-001): the permeability predictor is
computed ONLY on local edges, so it can never partly measure the same edges that
supply the AADT outcome.

Source: OpenStreetMap via the Overpass API, using OSMnx (Boeing 2017). Open, no key.

Usage
-----
    uv run python code/01_acquire/01a_osm_network.py --city denver --test
    uv run python code/01_acquire/01a_osm_network.py --city denver --extent urban_area

Outputs (GeoPackage, EPSG:4326)
-------
    data/raw/<city>/osm/network_<scope>_all.gpkg     nodes + edges, full drive network
    data/raw/<city>/osm/network_<scope>_major.gpkg   major-road edges only
    data/raw/<city>/osm/network_<scope>_local.gpkg   local-road edges only
"""

from __future__ import annotations

import argparse
import pathlib
import sys
import time

# Add code/ (not the project root) to sys.path: a top-level package named `code`
# would shadow Python's stdlib `code` module.
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

import geopandas as gpd
import networkx as nx
import osmnx as ox

from lib import cfg, paths, provenance, validate

SOURCE_URL = "https://overpass-api.de/api/interpreter (OpenStreetMap, via OSMnx)"


def setup_osmnx() -> None:
    c = cfg.config()
    paths.CACHE.mkdir(parents=True, exist_ok=True)
    ox.settings.use_cache = bool(c["reproducibility"]["osmnx_use_cache"])
    ox.settings.cache_folder = str(paths.CACHE / "osmnx")
    ox.settings.log_console = False
    # Overpass rate-limits and drops connections when several city pipelines query it
    # at once (observed on the Wasatch Front run while three others were live).
    # Generous timeouts + retries, rather than failing a 30-minute pipeline on a blip.
    ox.settings.requests_timeout = 600
    ox.settings.overpass_rate_limit = True
    ox.settings.max_query_area_size = 2_500_000_000
    # Keep the tags we need for classification and the H2 speed moderator.
    ox.settings.useful_tags_way = sorted(
        set(ox.settings.useful_tags_way)
        | {"highway", "maxspeed", "lanes", "oneway", "name", "ref", "surface", "access"}
    )


def _tagset(v) -> set[str]:
    """OSM `highway` may be a single value or a list (OSMnx merges parallel ways
    during simplification). Normalise to a set of strings."""
    if isinstance(v, list):
        return {str(x) for x in v}
    return {str(v)}


def split_major_local(
    edges: gpd.GeoDataFrame, major_tags: list[str], local_tags: list[str]
) -> tuple[gpd.GeoDataFrame, gpd.GeoDataFrame, int]:
    """Partition edges into major and local subgraphs, guaranteed disjoint.

    DECISION D-023 — hierarchy wins. A simplified edge can carry BOTH a major and a
    local tag (e.g. ['residential', 'tertiary']); at UA scale 77 of 218,485 Denver
    edges do. An "any match" rule would place those in both sets, which would let
    outcome-network edges leak into the permeability predictor — the exact failure
    D-001 exists to prevent. So: an edge is MAJOR if it carries any major tag, and
    LOCAL only if it carries a local tag AND no major tag. This is the direction that
    keeps the local subgraph clean; it costs 0.035% of edges being classed up.
    """
    maj_set, loc_set = set(major_tags), set(local_tags)
    tags = edges["highway"].apply(_tagset)
    is_major = tags.apply(lambda s: bool(s & maj_set))
    is_local = tags.apply(lambda s: bool(s & loc_set)) & ~is_major
    n_ambiguous = int((tags.apply(lambda s: bool(s & maj_set) and bool(s & loc_set))).sum())
    return edges[is_major].copy(), edges[is_local].copy(), n_ambiguous


def stringify_list_cols(gdf: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
    """GeoPackage cannot store Python lists. Collapse them to comma-joined strings."""
    out = gdf.copy()
    for col in out.columns:
        if col == out.geometry.name:
            continue
        if out[col].apply(lambda v: isinstance(v, list)).any():
            out[col] = out[col].apply(
                lambda v: ",".join(map(str, v)) if isinstance(v, list) else v
            )
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--city", default=None, help="city key in config/cities.yml")
    ap.add_argument(
        "--extent",
        choices=["test", "urban_area"],
        default="test",
        help="test = small smoke-test bbox; urban_area = full Census UA",
    )
    ap.add_argument("--test", action="store_true", help="shorthand for --extent test")
    args = ap.parse_args()

    conf = cfg.config()
    city_key = args.city or conf["project"]["pilot_city"]
    scope = "test" if args.test else args.extent
    C = cfg.city(city_key)

    # Fail loudly and immediately if the tag partition is broken.
    cfg.assert_filters_disjoint()

    setup_osmnx()
    print(f"Environment: {provenance.environment_stamp()}")
    print(f"City: {city_key} ({C['label']}) · scope: {scope}")

    if scope == "test":
        w, s, e, n = C["test_area"]["bbox_wsen"]
        print(f"Test bbox (w,s,e,n): {w}, {s}, {e}, {n}")
        print(f"  note: {C['test_area']['note']}")
        # OSMnx 2.x takes bbox as a positional tuple (left, bottom, right, top).
        G = ox.graph_from_bbox(
            (w, s, e, n), network_type=conf["network"]["network_type"], simplify=True
        )
        bbox_for_check = [w, s, e, n]
    else:
        ua_fp = paths.raw(city_key, "census") / "urban_area.gpkg"
        if not ua_fp.exists():
            raise SystemExit(
                f"{ua_fp.relative_to(paths.ROOT)} not found. Run "
                "01b_census_geography.py first."
            )
        ua = gpd.read_file(ua_fp).to_crs("EPSG:4326")
        poly = ua.geometry.iloc[0]
        w, s, e, n = ua.total_bounds
        print(f"UA polygon bounds (w,s,e,n): {w:.5f}, {s:.5f}, {e:.5f}, {n:.5f}")
        area_km2 = ua.to_crs(conf["crs"]["metric"]).geometry.area.iloc[0] / 1e6
        print(f"UA area: {area_km2:,.1f} km² — this is a large Overpass query, expect minutes")
        # D-055: query multi-part extents PART BY PART, then compose.
        # A dissolved multi-UA extent (D-051) can be a sparse MultiPolygon: the
        # Wasatch Front is 14 parts spanning a 7,697 km2 bbox that is only 22.7%
        # filled (Provo -> SLC -> Ogden, empty mountain between). OSMnx buffers and
        # subdivides the whole envelope, producing a query Overpass repeatedly drops
        # — six retries failed while a small test query succeeded in 2.8 s, so the
        # cause is query shape, not connectivity or rate limiting. Single compact
        # UAs (Denver, Portland, Phoenix, Boston) are unaffected and take this path
        # as a one-element loop.
        ntype = conf["network"]["network_type"]
        parts = list(poly.geoms) if poly.geom_type == "MultiPolygon" else [poly]
        if len(parts) > 1:
            print(f"  extent is a {len(parts)}-part MultiPolygon — querying per part "
                  f"and composing (avoids one oversized sparse-envelope query)")
        # D-056: a genuinely EMPTY part and a FAILED request must not be conflated.
        # The first version caught every exception and logged "no drivable network",
        # which silently dropped 7 of 14 Wasatch Front parts — including the SECOND
        # LARGEST (Provo or Ogden) — to Overpass rate-limit timeouts. The alternating
        # success/failure pattern was the giveaway. Now: only osmnx's
        # InsufficientResponseError counts as empty; anything else is retried with
        # backoff and RAISES if it never succeeds, so an incomplete network can never
        # be written and analysed.
        from osmnx._errors import InsufficientResponseError
        graphs, empty, failed = [], 0, []
        for i, part in enumerate(sorted(parts, key=lambda g: -g.area), 1):
            gp, err = None, None
            for attempt in range(1, 5):
                try:
                    gp = ox.graph_from_polygon(part, network_type=ntype, simplify=True)
                    break
                except InsufficientResponseError:
                    gp, err = None, "EMPTY"
                    break
                except Exception as exc:                      # transient / rate limit
                    err = f"{type(exc).__name__}"
                    if attempt < 4:
                        wait = 20 * attempt
                        print(f"    part {i}/{len(parts)}: {err}, retry "
                              f"{attempt}/3 in {wait}s")
                        time.sleep(wait)
            if gp is not None:
                graphs.append(gp)
                if len(parts) > 1:
                    print(f"    part {i}/{len(parts)}: {gp.number_of_edges():,} edges")
            elif err == "EMPTY":
                empty += 1
                if len(parts) > 1:
                    print(f"    part {i}/{len(parts)}: genuinely no drivable network")
            else:
                failed.append((i, err))
                print(f"    part {i}/{len(parts)}: FAILED after retries ({err})")
            if len(parts) > 1:
                time.sleep(3)          # respect Overpass's 2-slot rate limit
        if failed:
            raise validate.ValidationError(
                f"{len(failed)} of {len(parts)} extent parts could not be downloaded "
                f"{failed}. Refusing to build an INCOMPLETE network — P1 depends on "
                "network completeness, so a partial graph would silently understate "
                "substitutable routes."
            )
        if not graphs:
            raise SystemExit("No drivable network returned for any part of the extent.")
        G = graphs[0] if len(graphs) == 1 else nx.compose_all(graphs)
        if empty:
            print(f"  {empty} part(s) genuinely empty (slivers/water) — skipped")
        bbox_for_check = [w, s, e, n]

    print(f"\nGraph downloaded: {G.number_of_nodes():,} nodes, {G.number_of_edges():,} edges")

    nodes, edges = ox.graph_to_gdfs(G)
    edges = edges.reset_index()
    nodes = nodes.reset_index()

    validate.report_gdf(edges, "OSM edges (all, drive network)", expect_crs="EPSG:4326")
    validate.check_coords_plausible(edges, "OSM edges (all)", bbox_for_check)
    validate.report_gdf(nodes, "OSM nodes (all)", expect_crs="EPSG:4326")

    # --- the major / local split -------------------------------------------
    net = conf["network"]
    major, local, n_ambiguous = split_major_local(
        edges, net["major_highway_tags"], net["local_highway_tags"]
    )

    print("\n=== highway tag composition (all edges) ===")
    flat = edges["highway"].apply(lambda v: v[0] if isinstance(v, list) else v)
    for tag, cnt in flat.value_counts().items():
        bucket = (
            "MAJOR" if tag in set(net["major_highway_tags"])
            else "local" if tag in set(net["local_highway_tags"])
            else "excluded"
        )
        print(f"  {str(tag):20s} {cnt:6,d}   [{bucket}]")

    n_all, n_maj, n_loc = len(edges), len(major), len(local)
    print(f"\n  major edges : {n_maj:,}  ({n_maj / n_all:.1%} of all)")
    print(f"  local edges : {n_loc:,}  ({n_loc / n_all:.1%} of all)")
    print(f"  unclassed   : {n_all - n_maj - n_loc:,}  (excluded tags)")
    print(f"  D-023 mixed-tag edges resolved to major: {n_ambiguous:,} "
          f"({n_ambiguous / n_all:.3%}) — kept OUT of the local subgraph")

    # Hard invariant: the two sets must not intersect.
    overlap = set(zip(major["u"], major["v"], major["key"])) & set(
        zip(local["u"], local["v"], local["key"])
    )
    if overlap:
        raise validate.ValidationError(
            f"{len(overlap)} edges appear in BOTH major and local sets — "
            "predictor would be contaminated by the outcome network."
        )
    print("  major/local sets disjoint: OK")

    # --- length sanity check in metric CRS ---------------------------------
    metric = conf["crs"]["metric"]
    for label, gdf in (("major", major), ("local", local)):
        if len(gdf) == 0:
            continue
        km = gdf.to_crs(metric).geometry.length.sum() / 1000
        print(f"  {label} network total length: {km:,.2f} km")

    # --- write --------------------------------------------------------------
    outdir = paths.raw(city_key, "osm")
    written = []
    for label, gdf in (("all", edges), ("major", major), ("local", local)):
        fp = outdir / f"network_{scope}_{label}.gpkg"
        stringify_list_cols(gdf).to_file(fp, layer="edges", driver="GPKG")
        if label == "all":
            stringify_list_cols(nodes).to_file(fp, layer="nodes", driver="GPKG")
        written.append((label, fp, len(gdf)))
        print(f"  wrote {fp.relative_to(paths.ROOT)}  ({len(gdf):,} edges)")

    for label, fp, nrows in written:
        provenance.log(
            city=city_key,
            layer=f"osm_network_{scope}_{label}",
            source_url=SOURCE_URL,
            rows=nrows,
            file_path=fp,
        )
    provenance.log_progress(
        "01a_osm_network",
        f"{city_key}/{scope}: {n_all:,} edges total → {n_maj:,} major / {n_loc:,} local",
    )
    print("\nStage 1a complete.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
