#!/usr/bin/env python
"""Stage 6b — the paper's figure set, mirroring Choi & Ewing's (2021) map programme.

Their report (UT-20.19) figures and our analogues:
  their 3.1 study area          -> Fig 1: five UAs, arterial network coloured by AADT
  their 3.2 selected cells      -> Fig 2: 1 mi2 cells shaded by P1 prevalence
  their 3.3 network close-up    -> Fig 3: existing p1_routes_denver.png (06a)
  their 4.1 matched pairs map   -> Fig 4: Layer-1 matched study/control cells
  (new, discriminating case)    -> Fig 5: Phoenix, link-node ratio vs P1 prevalence
  (new, the H2 finding)         -> Fig 6: marginal effects of P1 by access control

All values plotted are read from the pipeline's own outputs; Fig 6 uses the logged
Denver marginal effects from notes/stage4R-findings.md verbatim.

Usage
-----
    uv run python code/06_figures/06b_paper_figures.py
"""

from __future__ import annotations

import os
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

import geopandas as gpd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.colors import BoundaryNorm, ListedColormap
from matplotlib.lines import Line2D
from matplotlib.patches import Patch

from lib import cfg, paths, provenance

METRIC = cfg.config()["crs"]["metric"]
CITIES = ["denver", "portland", "phoenix", "charlotte", "boston", "wasatch_front"]
LABELS = {c: cfg.city(c)["label"] for c in CITIES}
LABELS["wasatch_front"] = "Wasatch Front, UT"
NROW, NCOL = 2, 3   # 2x3 grid: larger, more legible panels than a 1x6 strip
FIGDIR = paths.ROOT / "outputs" / "figures"

# one sequential scheme for all cell choropleths, so panels are comparable
P1_BINS = [0, 5, 10, 20, 35, 100]
P1_COLORS = ["#f1f3f5", "#c5e0b4", "#7fc97f", "#2e8b57", "#0b5334"]
P1_LABELS = ["0–5%", "5–10%", "10–20%", "20–35%", "≥35%"]


def north_arrow(ax, x=0.94, y=0.88):
    """North arrow; axes are plotted in the city's UTM zone, which is
    true-north-up to within a fraction of a degree."""
    ax.annotate("", xy=(x, y + 0.07), xytext=(x, y), xycoords="axes fraction",
                arrowprops=dict(arrowstyle="-|>", color="#212529", lw=1.4))
    ax.text(x, y + 0.075, "N", transform=ax.transAxes, ha="center",
            va="bottom", fontsize=10, fontweight="bold", color="#212529")


def scalebar(ax, km):
    """Simple scale bar in the lower-left of an axis (metric CRS)."""
    x0, x1 = ax.get_xlim(); y0, y1 = ax.get_ylim()
    L = km * 1000
    bx = x0 + 0.06 * (x1 - x0); by = y0 + 0.05 * (y1 - y0)
    ax.plot([bx, bx + L], [by, by], color="black", lw=2, solid_capstyle="butt")
    ax.text(bx + L / 2, by + 0.012 * (y1 - y0), f"{km} km",
            ha="center", va="bottom", fontsize=8)


def load_city(c):
    # Plot in the city's own UTM zone so maps are true-north-up. The analysis
    # CRS (EPSG:5070, D-002) is an Albers conic whose grid north rotates away
    # from true north with distance from the -96° meridian (~16° in Portland);
    # this is a presentation choice only, no analysis value changes.
    seg = gpd.read_parquet(paths.processed(c) / "segments.parquet")
    utm = seg.estimate_utm_crs()
    seg = seg.to_crs(utm)
    grid = gpd.read_parquet(paths.processed(c) / "grid.parquet").to_crs(utm)
    cm = pd.read_parquet(paths.processed(c) / "cell_metrics.parquet")
    ua = gpd.read_file(paths.raw(c, "census") / "urban_area.gpkg").to_crs(utm)
    at = pd.read_parquet(paths.ANALYSIS / f"analysis_table_{c}.parquet",
                         columns=["segment_uid", "cell_id", "p1_any", "length_m"])
    # D-094: P1 is undefined below twice the endpoint attach radius, so the maps show
    # the same sample the models estimate on rather than a larger, differently-defined one.
    floor = float(os.environ.get("MIN_SEG_LEN_M", "0"))
    if floor:
        at = at[at["length_m"] >= floor]
        seg = seg[seg["segment_uid"].isin(set(at["segment_uid"]))]
    return seg, grid, cm, ua, at


def cell_p1(at):
    g = at.dropna(subset=["p1_any"]).groupby("cell_id")["p1_any"]
    return (100 * g.mean()).rename("pct_p1"), g.size().rename("n_seg")


# ---------------------------------------------------------------- Figure 1
def fig1(data):
    fig, axes = plt.subplots(NROW, NCOL, figsize=(16.5, 12.5))
    axes = axes.ravel()
    vmax = 5  # log10 AADT colour range 3..5 (1k..100k)
    for ax, c in zip(axes, CITIES):
        seg, grid, cm, ua, at = data[c]
        ua.boundary.plot(ax=ax, color="#adb5bd", linewidth=0.8, zorder=1)
        s = seg[seg.aadt > 0].copy()
        s["log_aadt10"] = np.log10(s.aadt)
        s.plot(ax=ax, column="log_aadt10", cmap="magma_r", vmin=3, vmax=vmax,
               linewidth=0.7, zorder=2)
        ax.set_title(LABELS[c], fontsize=12, fontweight="bold")
        ax.set_aspect("equal"); ax.set_axis_off()
        scalebar(ax, 10)
        north_arrow(ax)
    for ax in axes[len(CITIES):]:
        ax.set_axis_off()
    sm = plt.cm.ScalarMappable(cmap="magma_r",
                               norm=plt.Normalize(vmin=3, vmax=vmax))
    cb = fig.colorbar(sm, ax=axes, fraction=0.022, pad=0.02,
                      ticks=[3, 4, 5])
    cb.ax.set_yticklabels(["1,000", "10,000", "100,000"])
    cb.set_label("AADT (log scale)", fontsize=10)
    fp = FIGDIR / "fig1_study_areas.png"
    fig.savefig(fp, dpi=300, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    return fp


# ---------------------------------------------------------------- Figures 2 & 4 share machinery
def cell_panel(ax, grid, cm, values, title, cmap, norm):
    m = grid.merge(cm[["cell_id", "ce_eligible"]], on="cell_id", how="left")
    m = m.merge(values, left_on="cell_id", right_index=True, how="left")
    has = m[m.pct_p1.notna()]
    none = m[m.pct_p1.isna()]
    none.plot(ax=ax, facecolor="white", edgecolor="#dee2e6", linewidth=0.2)
    has.plot(ax=ax, column="pct_p1", cmap=cmap, norm=norm,
             edgecolor="#adb5bd", linewidth=0.2)
    ax.set_title(title, fontsize=12, fontweight="bold")
    ax.set_aspect("equal"); ax.set_axis_off()
    scalebar(ax, 10)
    north_arrow(ax)


def fig2(data):
    cmap = ListedColormap(P1_COLORS)
    norm = BoundaryNorm(P1_BINS, cmap.N)
    fig, axes = plt.subplots(NROW, NCOL, figsize=(16.5, 12.5))
    axes = axes.ravel()
    for ax, c in zip(axes, CITIES):
        seg, grid, cm, ua, at = data[c]
        pct, n = cell_p1(at)
        cell_panel(ax, grid, cm, pct, LABELS[c], cmap, norm)
    for ax in axes[len(CITIES):]:
        ax.set_axis_off()
    handles = [Patch(facecolor=col, edgecolor="#adb5bd") for col in P1_COLORS]
    handles.append(Patch(facecolor="white", edgecolor="#dee2e6"))
    fig.legend(handles, P1_LABELS + ["no analysis segments"],
               loc="lower center", ncol=6, frameon=False, fontsize=10,
               title="share of arterial segments in the cell with a substitutable local route (P1)",
               title_fontsize=10, bbox_to_anchor=(0.5, 0.02))
    fp = FIGDIR / "fig2_p1_cells.png"
    fig.savefig(fp, dpi=300, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    return fp


# ---------------------------------------------------------------- Figure 4
def fig4(data):
    pairs = pd.read_csv(paths.TABLES / "psm_choi_ewing_replication.csv")
    fig, axes = plt.subplots(NROW, NCOL, figsize=(16.5, 12.5))
    axes = axes.ravel()
    for ax, c in zip(axes, CITIES):
        seg, grid, cm, ua, at = data[c]
        p = pairs[pairs.city == c]
        elig = grid.merge(cm[["cell_id", "ce_eligible"]], on="cell_id", how="left")
        elig[elig.ce_eligible != True].plot(ax=ax, facecolor="white",
                                            edgecolor="#e9ecef", linewidth=0.2)
        elig[elig.ce_eligible == True].plot(ax=ax, facecolor="#f8f9fa",
                                            edgecolor="#ced4da", linewidth=0.25)
        st = grid[grid.cell_id.isin(p.study_cell)]
        ct = grid[grid.cell_id.isin(p.control_cell)]
        ct.plot(ax=ax, facecolor="#c92a2a", edgecolor="white", linewidth=0.3)
        st.plot(ax=ax, facecolor="#1864ab", edgecolor="white", linewidth=0.3)
        ax.set_title(f"{LABELS[c]}  (n = {len(p)} pairs)", fontsize=12,
                     fontweight="bold")
        ax.set_aspect("equal"); ax.set_axis_off()
        scalebar(ax, 10)
        north_arrow(ax)
    for ax in axes[len(CITIES):]:
        ax.set_axis_off()
    handles = [Patch(facecolor="#1864ab"), Patch(facecolor="#c92a2a"),
               Patch(facecolor="#f8f9fa", edgecolor="#ced4da")]
    fig.legend(handles, ["well-connected (study) cells",
                         "matched poorly-connected (control) cells",
                         "cells passing Choi & Ewing's eligibility filters"],
               loc="lower center", ncol=3, frameon=False, fontsize=10,
               bbox_to_anchor=(0.5, 0.03))
    fp = FIGDIR / "fig4_matched_pairs.png"
    fig.savefig(fp, dpi=300, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    return fp


# ---------------------------------------------------------------- Figure 5
def fig5(data):
    seg, grid, cm, ua, at = data["phoenix"]
    pct, n = cell_p1(at)
    m = grid.merge(cm[["cell_id", "link_node_all", "ce_eligible"]],
                   on="cell_id", how="left")
    m = m.merge(pct, left_on="cell_id", right_index=True, how="left")

    fig, axes = plt.subplots(1, 2, figsize=(13.5, 7.6))

    # (a) link-node ratio, their whole-network construction
    ax = axes[0]
    have = m[m.link_node_all.notna()]
    none = m[m.link_node_all.isna()]
    none.plot(ax=ax, facecolor="white", edgecolor="#dee2e6", linewidth=0.2)
    bins = [0, 1.2, 1.3, 1.4, 1.5, 3.0]
    cmap_a = ListedColormap(["#f1f3f5", "#bcd4e6", "#74a9cf", "#2b8cbe", "#045a8d"])
    norm_a = BoundaryNorm(bins, cmap_a.N)
    have.plot(ax=ax, column="link_node_all", cmap=cmap_a, norm=norm_a,
              edgecolor="#adb5bd", linewidth=0.2)
    ax.set_title("(a) Generic connectivity:\nlink–node ratio (whole network)",
                 fontsize=12, fontweight="bold")
    ax.set_aspect("equal"); ax.set_axis_off(); scalebar(ax, 10); north_arrow(ax)
    handles = [Patch(facecolor=c_, edgecolor="#adb5bd") for c_ in cmap_a.colors]
    ax.legend(handles, ["<1.2", "1.2–1.3", "1.3–1.4", "1.4–1.5", "≥1.5"],
              loc="lower right", fontsize=8, frameon=False,
              title="link–node ratio", title_fontsize=8)

    # (b) substitutability
    ax = axes[1]
    cmap_b = ListedColormap(P1_COLORS)
    norm_b = BoundaryNorm(P1_BINS, cmap_b.N)
    has = m[m.pct_p1.notna()]
    none = m[m.pct_p1.isna()]
    none.plot(ax=ax, facecolor="white", edgecolor="#dee2e6", linewidth=0.2)
    has.plot(ax=ax, column="pct_p1", cmap=cmap_b, norm=norm_b,
             edgecolor="#adb5bd", linewidth=0.2)
    ax.set_title("(b) Substitutability:\n% arterials with a P1 route",
                 fontsize=12, fontweight="bold")
    ax.set_aspect("equal"); ax.set_axis_off(); scalebar(ax, 10); north_arrow(ax)
    handles = [Patch(facecolor=c_, edgecolor="#adb5bd") for c_ in P1_COLORS]
    ax.legend(handles, P1_LABELS, loc="lower right", fontsize=8,
              frameon=False, title="% with substitute", title_fontsize=8)

    fig.suptitle("Phoenix–Mesa–Scottsdale: high generic connectivity, low substitutability",
                 fontsize=13, fontweight="bold", y=0.98)
    fp = FIGDIR / "fig5_phoenix_divergence.png"
    fig.savefig(fp, dpi=300, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    return fp


# ---------------------------------------------------------------- Figure 6
def fig6():
    # Logged Denver marginal effects (notes/stage4R-findings.md), verbatim.
    betw = ["low", "median", "high"]
    no_ac = [-30.96, -29.05, -27.57]
    ac = [-5.60, -2.99, -0.97]
    fig, ax = plt.subplots(figsize=(7.5, 5.2))
    x = np.arange(3)
    ax.plot(x, no_ac, "o-", color="#0b8a4b", lw=2.2, ms=8,
            label="no access control (serves local access)")
    ax.plot(x, ac, "s-", color="#1f3d7a", lw=2.2, ms=8,
            label="access-controlled")
    for xi, yi in zip(x, no_ac):
        ax.annotate(f"{yi:.1f}%", (xi, yi), textcoords="offset points",
                    xytext=(0, -16), ha="center", fontsize=9, color="#0b8a4b")
    for xi, yi in zip(x, ac):
        ax.annotate(f"{yi:.1f}%", (xi, yi), textcoords="offset points",
                    xytext=(0, 10), ha="center", fontsize=9, color="#1f3d7a")
    ax.axhline(0, color="#adb5bd", lw=0.8)
    ax.set_xticks(x); ax.set_xticklabels([f"{b}\nbetweenness" for b in betw])
    ax.set_ylabel("marginal effect of a substitutable route on AADT (%)")
    ax.set_ylim(-36, 6)
    ax.spines[["top", "right"]].set_visible(False)
    ax.legend(frameon=False, loc="center", bbox_to_anchor=(0.55, 0.5), fontsize=10)
    fp = FIGDIR / "fig6_h2_marginal_effects.png"
    fig.savefig(fp, dpi=300, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    return fp


def main() -> int:
    print(f"Environment: {provenance.environment_stamp()}")
    data = {}
    for c in CITIES:
        data[c] = load_city(c)
        print(f"  loaded {c}: {len(data[c][0]):,} segments, {len(data[c][1]):,} cells")
    for fn in (fig1, fig2, fig4, fig5):
        fp = fn(data)
        print(f"  wrote {fp.relative_to(paths.ROOT)}")
    fp = fig6()
    print(f"  wrote {fp.relative_to(paths.ROOT)}")
    provenance.log_progress("06b_paper_figures", "paper figure set generated")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
