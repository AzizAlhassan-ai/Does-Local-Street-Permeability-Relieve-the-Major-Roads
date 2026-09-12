#!/usr/bin/env python
"""Stage 6c — appendix figures: matched-neighbourhood close-up pairs.

Mirrors Choi & Ewing's report Appendix A (UT-20.19): for each city, the matched
study/control cell pair with the LARGEST connectivity-index gap, drawn side by
side at 1 mi² with intersections classified in their visual vocabulary
(4+-way, 3-way, cul-de-sac) and arterials coloured in ours (has a P1
substitutable route / has none). Metrics are printed under each panel.

Node degrees are computed on the full local+major undirected graph clipped to a
500 m buffer around the cell, so boundary effects do not misclassify nodes at
the cell edge.

Usage
-----
    uv run python code/06_figures/06c_matched_pair_closeups.py
"""

from __future__ import annotations

import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

import geopandas as gpd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import networkx as nx
import numpy as np
import pandas as pd
from matplotlib.lines import Line2D

from lib import cfg, paths, provenance

METRIC = cfg.config()["crs"]["metric"]
CITIES = ["denver", "portland", "phoenix", "charlotte", "boston", "wasatch_front"]
LABELS = {c: cfg.city(c)["label"] for c in CITIES}
LABELS["wasatch_front"] = "Wasatch Front, UT"
FIGDIR = paths.ROOT / "outputs" / "figures"
BUF = 500  # m — degree-computation buffer around the cell


def undirected_degrees(edges):
    lo = np.minimum(edges["u"].values, edges["v"].values)
    hi = np.maximum(edges["u"].values, edges["v"].values)
    e = pd.DataFrame({"a": lo, "b": hi}).drop_duplicates()
    G = nx.Graph(); G.add_edges_from(e.itertuples(index=False, name=None))
    return pd.Series(dict(G.degree()), name="deg")


def draw_cell(ax, cell_geom, loc, maj, nodes, seg, title):
    minx, miny, maxx, maxy = cell_geom.bounds
    b = cell_geom.buffer(BUF)
    # degrees from the buffered clip of the whole (local+major) network
    li = loc.iloc[list(loc.sindex.query(b, predicate="intersects"))]
    mi = maj.iloc[list(maj.sindex.query(b, predicate="intersects"))]
    alledges = pd.concat([li, mi], ignore_index=True)
    deg = undirected_degrees(alledges)
    nd = nodes.iloc[list(nodes.sindex.query(cell_geom, predicate="intersects"))].copy()
    nd["deg"] = nd["osmid"].map(deg)
    nd = nd[nd.deg.notna()]

    li.plot(ax=ax, color="#c9ccd1", linewidth=0.9, zorder=1)
    mi.plot(ax=ax, color="#9aa0a8", linewidth=1.6, zorder=2)
    s = seg.iloc[list(seg.sindex.query(cell_geom, predicate="intersects"))]
    s[s.p1_any != True].plot(ax=ax, color="#1f3d7a", linewidth=3.0, zorder=3, alpha=.9)
    s[s.p1_any == True].plot(ax=ax, color="#0b8a4b", linewidth=3.0, zorder=4, alpha=.9)

    for q, color, size, z in ((nd.deg == 1, "#c92a2a", 11, 6),
                              (nd.deg == 3, "#e8890c", 9, 5),
                              (nd.deg >= 4, "#f5d90a", 13, 7)):
        pts = nd[q]
        if len(pts):
            pts.plot(ax=ax, color=color, markersize=size, zorder=z,
                     edgecolor="#495057", linewidth=0.25)

    ax.set_xlim(minx, maxx); ax.set_ylim(miny, maxy)
    ax.set_xticks([]); ax.set_yticks([])
    for sp in ax.spines.values():
        sp.set_edgecolor("#495057")
    ax.set_title(title, fontsize=11.5, fontweight="bold", pad=8)
    # scale bar (cell is 1 mile wide; show 500 m)
    span = maxx - minx
    x0, y0 = minx + span * .05, miny + span * .045
    ax.plot([x0, x0 + 500], [y0, y0], color="#212529", lw=2.4,
            solid_capstyle="butt", zorder=8)
    ax.text(x0 + 250, y0 + span * .014, "500 m", ha="center", fontsize=8,
            zorder=8)
    # north arrow
    ax.annotate("", xy=(0.95, 0.945), xytext=(0.95, 0.885),
                xycoords="axes fraction",
                arrowprops=dict(arrowstyle="-|>", color="#212529", lw=1.4))
    ax.text(0.95, 0.95, "N", transform=ax.transAxes, ha="center", va="bottom",
            fontsize=10, fontweight="bold", color="#212529")


def metrics_text(cm_row, seg_cell, index_val):
    med_aadt = seg_cell.aadt.median() if len(seg_cell) else np.nan
    pct_p1 = 100 * seg_cell.p1_any.mean() if len(seg_cell) else np.nan
    return (f"connectivity idx(z){index_val:6.2f}\n"
            f"link–node ratio    {cm_row.link_node_all:6.2f}\n"
            f"intersections/sq mi{cm_row.int_density_all:6.0f}\n"
            f"% 4-way            {cm_row.pct_4way_all:6.1f}\n"
            f"median block (ac)  {cm_row.median_block_acres:6.1f}\n"
            f"% arterials w/ P1  {pct_p1:6.1f}\n"
            f"median AADT        {med_aadt:6,.0f}")


def main() -> int:
    print(f"Environment: {provenance.environment_stamp()}")
    pairs = pd.read_csv(paths.TABLES / "psm_choi_ewing_replication.csv")
    written = []
    for k, c in enumerate(CITIES, start=1):
        p = pairs[pairs.city == c].copy()
        p["gap"] = p.study_index - p.control_index
        row = p.sort_values("gap", ascending=False).iloc[0]
        print(f"\n{c}: pair with largest index gap "
              f"({row.study_index:.2f} vs {row.control_index:.2f})")

        # per-city UTM so panels are true-north-up (presentation only, D-002 unchanged)
        grid = gpd.read_parquet(paths.processed(c) / "grid.parquet")
        utm = grid.estimate_utm_crs()
        grid = grid.to_crs(utm)
        cm = pd.read_parquet(paths.processed(c) / "cell_metrics.parquet").set_index("cell_id")
        seg = gpd.read_parquet(paths.processed(c) / "segments.parquet").to_crs(utm)
        at = pd.read_parquet(paths.ANALYSIS / f"analysis_table_{c}.parquet",
                             columns=["segment_uid", "p1_any"])
        seg = seg.merge(at, on="segment_uid", how="left")

        g_study = grid.loc[grid.cell_id == row.study_cell, "geometry"].iloc[0]
        g_ctrl = grid.loc[grid.cell_id == row.control_cell, "geometry"].iloc[0]
        # read networks only around the two cells (bbox in the layer CRS 4326)
        both = gpd.GeoSeries([g_study.buffer(BUF + 100), g_ctrl.buffer(BUF + 100)],
                             crs=utm).to_crs("EPSG:4326")
        bb = tuple(both.total_bounds)
        loc = gpd.read_file(paths.raw(c, "osm") / "network_urban_area_local.gpkg",
                            layer="edges", bbox=bb).to_crs(utm)
        maj = gpd.read_file(paths.raw(c, "osm") / "network_urban_area_major.gpkg",
                            layer="edges", bbox=bb).to_crs(utm)
        nodes = gpd.read_file(paths.raw(c, "osm") / "network_urban_area_all.gpkg",
                              layer="nodes", bbox=bb).to_crs(utm)

        fig, axes = plt.subplots(1, 2, figsize=(12.6, 7.9))
        draw_cell(axes[0], g_study, loc, maj, nodes, seg,
                  "Well-connected (study) cell")
        draw_cell(axes[1], g_ctrl, loc, maj, nodes, seg,
                  "Matched poorly-connected (control) cell")
        for ax, cell_id, idx in ((axes[0], row.study_cell, row.study_index),
                                 (axes[1], row.control_cell, row.control_index)):
            sc = seg[seg.cell_id == cell_id]
            ax.text(0.02, -0.03, metrics_text(cm.loc[cell_id], sc, idx),
                    transform=ax.transAxes, va="top", ha="left", fontsize=9,
                    family="monospace", linespacing=1.45)

        handles = [
            Line2D([], [], color="#0b8a4b", lw=3.0, label="arterial with P1 substitute"),
            Line2D([], [], color="#1f3d7a", lw=3.0, label="arterial with none"),
            Line2D([], [], marker="o", color="none", markerfacecolor="#f5d90a",
                   markeredgecolor="#495057", markersize=7, label="4+-way intersection"),
            Line2D([], [], marker="o", color="none", markerfacecolor="#e8890c",
                   markeredgecolor="#495057", markersize=6, label="3-way intersection"),
            Line2D([], [], marker="o", color="none", markerfacecolor="#c92a2a",
                   markeredgecolor="#495057", markersize=6, label="cul-de-sac"),
            Line2D([], [], color="#c9ccd1", lw=1.2, label="local street"),
        ]
        fig.legend(handles=handles, loc="lower center", ncol=6, frameon=False,
                   fontsize=8.8, bbox_to_anchor=(0.5, 0.0))
        fig.suptitle(f"{LABELS[c]} — matched pair with the largest "
                     "connectivity-index gap", fontsize=13, fontweight="bold",
                     y=0.98)
        fig.tight_layout(rect=[0, 0.17, 1, 0.95])
        fp = FIGDIR / f"figA{k}_{c}_pair.png"
        fig.savefig(fp, dpi=300, bbox_inches="tight", facecolor="white")
        plt.close(fig)
        written.append(fp)
        print(f"  wrote {fp.relative_to(paths.ROOT)}")

    provenance.log_progress("06c_matched_pair_closeups",
                            f"appendix pair close-ups for {len(written)} cities")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
