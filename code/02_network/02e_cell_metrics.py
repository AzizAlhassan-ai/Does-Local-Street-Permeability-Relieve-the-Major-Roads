#!/usr/bin/env python
"""Stage 2 — Choi & Ewing (2021) comparability layer: their four metrics, per 1 mi² cell.

Their street network design index is a PCA over four measures (their Table 1):

  intersection density   intersections / gross area (sq mi)
  median block size      median CENSUS block area, acres
  link-node ratio        links / nodes  (nodes = intersections + dead ends)
  % 4-way intersections  4-or-more-way / all 3+-way intersections

We already had the first and third at catchment level. This script computes all four at
the CELL level, which is their unit, so the comparison is like-for-like (D-063).

Also computes their three sample filters (their §3.6.1):
  1. activity density (population + employment) >= 1500 per sq mi
  2. major road length >= 2 miles per cell
  3. cells dominated by campus / airport / industrial use excluded

D-065: their metrics are computed on the WHOLE cell network; ours are normally local-only
(D-001). Both are produced here — `*_all` reproduces their construction, `*_local` uses
our partition — so the paper can show what that choice alone does.

Usage
-----
    uv run python code/02_network/02e_cell_metrics.py --city denver

Outputs
-------
    data/processed/<city>/cell_metrics.parquet
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
import pyogrio

from lib import cfg, paths, provenance, validate

SQMI_PER_KM2 = 0.386102
ACRE_PER_M2 = 0.000247105


def degree_table(edges: gpd.GeoDataFrame) -> pd.Series:
    """Undirected node degree from an OSMnx edge table."""
    lo = np.minimum(edges["u"].values, edges["v"].values)
    hi = np.maximum(edges["u"].values, edges["v"].values)
    e = pd.DataFrame({"a": lo, "b": hi}).drop_duplicates()
    G = nx.Graph()
    G.add_edges_from(e[["a", "b"]].itertuples(index=False, name=None))
    return pd.Series(dict(G.degree()), name="deg"), G


def net_metrics(nodes_in_cell: pd.DataFrame, n_edges: int, area_sqmi: float) -> dict:
    """Choi & Ewing's density + connectivity measures for one cell.

    D-066 — link count. Marshall & Garrick's LINK runs intersection-to-intersection
    or intersection-to-dead-end; a degree-2 node is not a node in their sense and the
    two edges meeting there are ONE link. Counting raw OSM edges against a
    degree-2-excluded node count inflates the ratio badly: it gave 2.60 for Denver
    against their published 1.18-1.84 range. Since every link endpoint sits on a
    counted node and every link has two endpoints,

        N = #(deg == 1) + #(deg >= 3)
        L = sum(deg of those same nodes) / 2

    which contracts degree-2 chains exactly, without walking the graph.
    """
    if len(nodes_in_cell) == 0 or area_sqmi <= 0:
        return {"int_density": np.nan, "link_node": np.nan, "pct_4way": np.nan,
                "n_links": np.nan, "n_nodes": np.nan}
    deg = nodes_in_cell["deg"]
    counted = (deg == 1) | (deg >= 3)
    n_int = int((deg >= 3).sum())
    n_4way = int((deg >= 4).sum())
    n_nodes = int(counted.sum())
    n_links = float(deg[counted].sum()) / 2.0
    return {
        "int_density": n_int / area_sqmi,
        "link_node": (n_links / n_nodes) if n_nodes > 0 else np.nan,
        "pct_4way": (100 * n_4way / n_int) if n_int > 0 else np.nan,
        "n_links": n_links, "n_nodes": n_nodes,
    }


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--city", default=None)
    args = ap.parse_args()
    conf = cfg.config()
    city = args.city or conf["project"]["pilot_city"]
    metric = conf["crs"]["metric"]
    proc = paths.processed(city)

    print(f"Environment: {provenance.environment_stamp()}")
    print(f"City: {city} — Choi & Ewing comparability metrics per 1 mi² cell")

    grid = gpd.read_parquet(proc / "grid.parquet").to_crs(metric).reset_index(drop=True)
    grid["cell_area_sqmi"] = grid["cell_area_km2"] * SQMI_PER_KM2
    print(f"  cells: {len(grid):,}")

    loc = gpd.read_file(paths.raw(city, "osm") / "network_urban_area_local.gpkg",
                        layer="edges").to_crs(metric)
    maj = gpd.read_file(paths.raw(city, "osm") / "network_urban_area_major.gpkg",
                        layer="edges").to_crs(metric)
    allnet = pd.concat([loc, maj], ignore_index=True)
    allnet = gpd.GeoDataFrame(allnet, geometry="geometry", crs=metric)
    nodes_all = gpd.read_file(paths.raw(city, "osm") / "network_urban_area_all.gpkg",
                              layer="nodes").to_crs(metric)

    out = grid[["cell_id", "cell_area_km2", "cell_area_sqmi", "geometry"]].copy()

    for label, edges in (("local", loc), ("all", allnet)):
        deg, _ = degree_table(edges)
        nd = nodes_all[nodes_all["osmid"].isin(deg.index)].copy()
        nd["deg"] = nd["osmid"].map(deg)
        nd = gpd.GeoDataFrame(nd[["osmid", "deg"]], geometry=nd.geometry.values, crs=metric)
        jn = gpd.sjoin(nd, grid[["cell_id", "geometry"]], how="inner", predicate="within")
        # edge midpoints -> cell, for the link count
        emid = gpd.GeoDataFrame(
            {"i": np.arange(len(edges))},
            geometry=[g.interpolate(0.5, normalized=True) for g in edges.geometry],
            crs=metric)
        je = gpd.sjoin(emid, grid[["cell_id", "geometry"]], how="inner", predicate="within")
        ecount = je.groupby("cell_id").size()
        rows = []
        for cid, g in jn.groupby("cell_id"):
            a = float(grid.loc[grid.cell_id == cid, "cell_area_sqmi"].iloc[0])
            m = net_metrics(g, int(ecount.get(cid, 0)), a)
            m["cell_id"] = cid
            rows.append(m)
        mt = pd.DataFrame(rows).set_index("cell_id")
        mt.columns = [f"{c}_{label}" for c in mt.columns]
        out = out.merge(mt, left_on="cell_id", right_index=True, how="left")
        print(f"  {label} network: metrics on {len(mt):,} cells")

    # --- median CENSUS block size, acres (their definition) -------------------
    blocks = []
    for st in cfg.states(city):
        z = paths.raw(city, "census") / pathlib.Path(
            conf["sources"]["block_url_tpl"].format(**st)).name
        if not z.exists():
            print(f"  !! block file missing for FIPS {st['fips']}: {z.name}")
            continue
        stem = z.name.replace(".zip", "")
        info = pyogrio.read_info(f"/vsizip/{z}/{stem}.dbf")
        flds = list(info["fields"])
        f_lat = [f for f in flds if f.startswith("INTPTLAT")][0]
        f_lon = [f for f in flds if f.startswith("INTPTLON")][0]
        f_ala = [f for f in flds if f.startswith("ALAND")][0]
        a = pyogrio.read_dataframe(f"/vsizip/{z}/{stem}.dbf",
                                   columns=[f_lat, f_lon, f_ala], read_geometry=False)
        la = pd.to_numeric(a[f_lat], errors="coerce")
        lo_ = pd.to_numeric(a[f_lon], errors="coerce")
        ar = pd.to_numeric(a[f_ala], errors="coerce")
        k = la.notna() & lo_.notna() & ar.notna()
        blocks.append(gpd.GeoDataFrame(
            {"aland_m2": ar[k].values},
            geometry=gpd.points_from_xy(lo_[k], la[k]), crs="EPSG:4326").to_crs(metric))
    if blocks:
        blk = pd.concat(blocks, ignore_index=True)
        blk = gpd.GeoDataFrame(blk, geometry="geometry", crs=metric)
        jb = gpd.sjoin(blk, grid[["cell_id", "geometry"]], how="inner", predicate="within")
        med = (jb.groupby("cell_id")["aland_m2"].median() * ACRE_PER_M2
               ).rename("median_block_acres")
        out = out.merge(med, left_on="cell_id", right_index=True, how="left")
        print(f"  census blocks: median block size on {med.notna().sum():,} cells")
    else:
        out["median_block_acres"] = np.nan

    # --- their sample filters ------------------------------------------------
    tr = gpd.read_file(proc / "tract_density.gpkg").to_crs(metric)
    ov = gpd.overlay(grid[["cell_id", "geometry"]], tr[["total_population", "geometry"]],
                     how="intersection", keep_geom_type=True)
    ov["w"] = ov.geometry.area
    tra = tr.copy(); tra["tract_area"] = tra.geometry.area
    ov = ov.merge(tr[["total_population"]].assign(_i=range(len(tr))), left_index=True,
                  right_index=True, how="left", suffixes=("", "_y"))
    pop = (ov.assign(share=ov["w"] / ov.groupby(level=0)["w"].transform("sum"))
             .groupby("cell_id").apply(lambda g: (g["total_population"] * g["w"]
                                                  / g["w"].sum()).sum(),
                                       include_groups=False).rename("pop_est"))
    out = out.merge(pop, left_on="cell_id", right_index=True, how="left")

    lo_b = gpd.read_file(proc / "lodes_blocks.gpkg").to_crs(metric)
    jj = gpd.sjoin(lo_b[["C000", "geometry"]], grid[["cell_id", "geometry"]],
                   how="inner", predicate="within")
    out = out.merge(jj.groupby("cell_id")["C000"].sum().rename("jobs"),
                    left_on="cell_id", right_index=True, how="left")
    out["jobs"] = out["jobs"].fillna(0)
    out["activity_density"] = (out["pop_est"].fillna(0) + out["jobs"]) / out["cell_area_sqmi"]

    mj = gpd.sjoin(gpd.GeoDataFrame({"L": maj.geometry.length},
                                    geometry=[g.interpolate(0.5, normalized=True)
                                              for g in maj.geometry], crs=metric),
                   grid[["cell_id", "geometry"]], how="inner", predicate="within")
    out = out.merge((mj.groupby("cell_id")["L"].sum() / 1609.344).rename("major_road_mi"),
                    left_on="cell_id", right_index=True, how="left")
    out["major_road_mi"] = out["major_road_mi"].fillna(0)

    out["ce_filter_density"] = out["activity_density"] >= 1500
    out["ce_filter_majorroad"] = out["major_road_mi"] >= 2
    out["ce_eligible"] = out["ce_filter_density"] & out["ce_filter_majorroad"]
    out["city"] = city

    print(f"\n  Choi & Ewing filters:")
    print(f"    activity density >= 1500/sq mi : {int(out.ce_filter_density.sum()):,}"
          f" of {len(out):,}")
    print(f"    major road >= 2 miles          : {int(out.ce_filter_majorroad.sum()):,}")
    print(f"    BOTH (their eligible sample)   : {int(out.ce_eligible.sum()):,}"
          f"  ({out.ce_eligible.mean():.1%})")
    print("    note: their 3rd filter (campus/airport/industrial) not applied — "
          "approximate only from our data")

    e = out[out.ce_eligible]
    if len(e):
        print(f"\n  their four metrics on eligible cells (whole-network construction):")
        for c, lab in [("int_density_all", "intersection density /sq mi"),
                       ("median_block_acres", "median block size (acres)"),
                       ("link_node_all", "link-node ratio"),
                       ("pct_4way_all", "% 4-way intersections")]:
            if c in e.columns:
                print(f"    {lab:32s} median {e[c].median():8.2f}   "
                      f"p10 {e[c].quantile(.1):7.2f}  p90 {e[c].quantile(.9):7.2f}")

    fp = proc / "cell_metrics.parquet"
    out.drop(columns=["geometry"]).to_parquet(fp, index=False)
    validate.report_df(out, "cell metrics", key_cols=[
        "int_density_local", "int_density_all", "pct_4way_all",
        "median_block_acres", "activity_density", "major_road_mi"])
    print(f"  wrote {fp.relative_to(paths.ROOT)}")
    provenance.log(city=city, layer="cell_metrics",
                   source_url="derived: 01a OSM + TIGER blocks + ACS + LODES",
                   rows=len(out), file_path=fp)
    provenance.log_progress("02e_cell_metrics",
                            f"{city}: Choi & Ewing metrics on {len(out):,} cells, "
                            f"{int(out.ce_eligible.sum()):,} eligible")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
