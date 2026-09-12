#!/usr/bin/env python
"""Stage 6d — definitional schematic for the three permeability measures.

One stylized fabric drawn three times, so the reader sees that P1, P2 and P3
ask three different QUESTIONS of the same place:

  (a) P1 substitutability — a local-only route joining the arterial segment's
      own two endpoints, within the detour cap (plus a rejected candidate)
  (b) P2 access connections — local links joining major-road access points in
      any orientation: access to the major network, not substitution for S
  (c) P3 generic connectivity — the fabric metrics, computed on the local
      subgraph, with the cul-de-sac pocket scoring intersections that offer
      no way through

Pure matplotlib, no geodata; the figure is a definition, not evidence, and is
labelled "Schematic — not to scale" (which is also why it carries no scale bar
or north arrow).

Usage
-----
    uv run python code/06_figures/06d_schematic_p1p2p3.py
"""

from __future__ import annotations

import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.patches import Circle, FancyBboxPatch

from lib import paths, provenance

FIGDIR = paths.ROOT / "outputs" / "figures"

# palette, consistent with the paper's other figures
C_MAJOR = "#495057"   # major network
C_SEG = "#141a20"     # the arterial segment S
C_LOCAL = "#adb5bd"   # local streets
C_P1 = "#e8590c"      # detected P1 route (orange dashed, as in the Denver map)
C_REJ = "#adb5bd"     # rejected candidate
C_P2 = "#7048e8"      # P2 access connections
C_4WAY, C_3WAY, C_DEAD = "#f5d90a", "#e8890c", "#c92a2a"
C_ACC = "#0b8a4b"     # endpoint access circles

A, B = (22, 35), (78, 35)          # segment endpoints
GRID_X = [30, 38, 46, 54, 62, 70]  # local verticals
GRID_Y = [15, 25, 45, 55]          # local horizontals
TALL_X = [38, 62]                  # verticals that reach the northern arterial


def base_fabric(ax):
    """Majors, segment S, local fabric, catchment. Returns nothing."""
    # catchment buffer
    ax.add_patch(FancyBboxPatch((13, 9), 74, 52,
                                boxstyle="round,pad=0,rounding_size=10",
                                fill=False, edgecolor="#ced4da", lw=1.3,
                                linestyle=(0, (4, 3)), zorder=0))
    ax.text(86.5, 12.5, "catchment\nbuffer (r)", fontsize=7.6, color="#868e96",
            ha="left", va="bottom", style="italic")
    # major network
    ax.plot([0, 100], [35, 35], color=C_MAJOR, lw=3.2, zorder=2)   # arterial corridor
    ax.plot([22, 22], [0, 70], color=C_MAJOR, lw=3.2, zorder=2)    # crossing majors
    ax.plot([78, 78], [0, 70], color=C_MAJOR, lw=3.2, zorder=2)
    ax.plot([0, 100], [63, 63], color=C_MAJOR, lw=3.2, zorder=2)   # flanking arterial
    # the segment S
    ax.plot([A[0], B[0]], [35, 35], color=C_SEG, lw=5.6, zorder=3,
            solid_capstyle="butt")
    for p, lab in ((A, "A"), (B, "B")):
        ax.scatter(*p, s=64, facecolor="white", edgecolor=C_SEG, lw=1.6, zorder=6)
        ax.annotate(lab, p, textcoords="offset points", xytext=(-1, -13),
                    ha="center", fontsize=9, fontweight="bold", zorder=6)
    # local grid
    for x in GRID_X:
        ytop = 63 if x in TALL_X else 55
        ax.plot([x, x], [15, ytop], color=C_LOCAL, lw=1.3, zorder=1)
    for y in GRID_Y:
        ax.plot([30, 70], [y, y], color=C_LOCAL, lw=1.3, zorder=1)
    # cul-de-sac pocket, east of B's crossing major
    ax.plot([78, 96], [25, 25], color=C_LOCAL, lw=1.3, zorder=1)     # spine
    for x in (85, 91):
        ax.plot([x, x], [25, 15], color=C_LOCAL, lw=1.3, zorder=1)   # stubs
    ax.plot([78, 90], [50, 50], color=C_LOCAL, lw=1.3, zorder=1)     # stub
    # two stubs west of A
    ax.plot([8, 22], [45, 45], color=C_LOCAL, lw=1.3, zorder=1)
    ax.plot([10, 22], [20, 20], color=C_LOCAL, lw=1.3, zorder=1)

    ax.set_xlim(0, 100); ax.set_ylim(0, 70)
    ax.set_aspect("equal")
    ax.set_xticks([]); ax.set_yticks([])
    for sp in ax.spines.values():
        sp.set_edgecolor("#dee2e6")


def panel_p1(ax):
    base_fabric(ax)
    # endpoint access sets
    for p in (A, B):
        ax.add_patch(Circle(p, 13, fill=False, edgecolor=C_ACC, lw=1.5,
                            linestyle=(0, (3, 2)), zorder=4))
    ax.annotate("endpoint access\nradius (200 m)", (12, 43),
                xytext=(1, 53), fontsize=7.6, color=C_ACC,
                arrowprops=dict(arrowstyle="-", color=C_ACC, lw=0.8))
    # the counted route: leaves the corridor at a local junction inside A's
    # access set, runs one block north, rejoins inside B's (length 1.07x |S|)
    ax.plot([30, 30, 70, 70], [35, 45, 45, 35], color=C_P1, lw=3.0, zorder=5,
            linestyle=(0, (5, 2)))
    for pt in ((30, 35), (70, 35)):
        ax.scatter(*pt, s=40, facecolor="white", edgecolor=C_P1, lw=1.6, zorder=6)
    ax.annotate("leaves / rejoins the corridor at local\njunctions inside the access radius",
                (30, 35), xytext=(3, 8), fontsize=7.4, color=C_P1,
                arrowprops=dict(arrowstyle="->", color=C_P1, lw=0.8))
    ax.annotate("counted: local-only, joins S's own endpoints,\n"
                "length ≤ 1.5 × |S|, spans ≥ 50% of S",
                (50, 45), xytext=(29, 66.3), fontsize=7.9, color=C_P1,
                arrowprops=dict(arrowstyle="->", color=C_P1, lw=1.0), zorder=7)
    # a rejected candidate: attaches the same way but wanders (1.79x |S|)
    ax.plot([30, 30, 46, 46, 62, 62, 70, 70],
            [35, 15, 15, 25, 25, 15, 15, 35], color=C_REJ, lw=2.4,
            zorder=4, linestyle=(0, (5, 2)))
    ax.annotate("rejected: exceeds the detour cap", (46, 15),
                xytext=(36, 3.5), fontsize=7.9, color="#868e96",
                arrowprops=dict(arrowstyle="->", color="#868e96", lw=1.0))
    ax.set_title("(a)  P1 — substitutability:\ncan a driver avoid S itself?",
                 fontsize=11, fontweight="bold")


def panel_p2(ax):
    base_fabric(ax)
    # perpendicular connections between the arterial corridor and the
    # flanking arterial, plus one to the crossing major
    for x in TALL_X:
        ax.plot([x, x], [35, 63], color=C_P2, lw=3.0, zorder=5)
    ax.plot([22, 30, 30], [45, 45, 35], color=C_P2, lw=3.0, zorder=5)
    for pt in ((38, 35), (38, 63), (62, 35), (62, 63), (22, 45), (30, 35)):
        ax.scatter(*pt, s=34, facecolor="white", edgecolor=C_P2, lw=1.5, zorder=6)
    ax.annotate("counted: any local link between two\nmajor-road access points, "
                "any orientation", (62, 52), xytext=(30, 66.3), fontsize=7.9,
                color=C_P2, arrowprops=dict(arrowstyle="->", color=C_P2, lw=1.0),
                zorder=7)
    ax.text(50, 3.5, "doors onto the major network: access TO it, not\n"
            "substitution FOR segment S — normalized per km²",
            fontsize=7.9, color=C_P2, ha="center")
    ax.set_title("(b)  P2 — access connections:\nhow reachable is the major network?",
                 fontsize=11, fontweight="bold")


def panel_p3(ax):
    base_fabric(ax)
    # local-subgraph nodes only: nodes on the majors are excluded by design
    four, three, dead = [], [], []
    for x in GRID_X:
        for y in GRID_Y:
            if x in (30, 70) and y in (15, 55):
                continue  # degree-2 corner: not a node (chains are contracted)
            if x in (30, 70) or y == 15 or (y == 55 and x not in TALL_X):
                three.append((x, y))
            else:
                four.append((x, y))
    three += [(85, 25), (91, 25)]                       # pocket spine junctions
    dead += [(85, 15), (91, 15), (96, 25), (90, 50)]    # stub ends
    dead += [(8, 45), (10, 20)]                         # west stub ends
    for pts, c, s in ((four, C_4WAY, 30), (three, C_3WAY, 22), (dead, C_DEAD, 22)):
        xs, ys = zip(*pts)
        ax.scatter(xs, ys, s=s, facecolor=c, edgecolor="#495057", lw=0.5, zorder=5)
    ax.annotate("cul-de-sac pocket: adds intersections\nand density, offers no way through",
                (88, 20), xytext=(40, 3.5), fontsize=7.9, color="#c92a2a",
                arrowprops=dict(arrowstyle="->", color="#c92a2a", lw=1.0))
    ax.text(50, 66.6, "intersection density · link–node ratio · dead-end share\n"
            "counted on the local subgraph — blind to where routes lead",
            fontsize=7.9, color="#495057", ha="center", va="center")
    ax.set_title("(c)  P3 — generic connectivity:\nhow much fabric is there?",
                 fontsize=11, fontweight="bold")


def main() -> int:
    print(f"Environment: {provenance.environment_stamp()}")
    fig, axes = plt.subplots(1, 3, figsize=(19, 6.4))
    panel_p1(axes[0]); panel_p2(axes[1]); panel_p3(axes[2])

    handles = [
        Line2D([], [], color=C_SEG, lw=5, label="arterial segment S (endpoints A, B)"),
        Line2D([], [], color=C_MAJOR, lw=3, label="other major roads"),
        Line2D([], [], color=C_LOCAL, lw=1.4, label="local streets"),
        Line2D([], [], color=C_P1, lw=2.6, ls=(0, (5, 2)), label="P1 substitutable route"),
        Line2D([], [], color=C_REJ, lw=2.2, ls=(0, (5, 2)), label="rejected candidate"),
        Line2D([], [], color=C_P2, lw=2.6, label="P2 access connection"),
        Line2D([], [], marker="o", color="none", markerfacecolor=C_4WAY,
               markeredgecolor="#495057", markersize=7, label="4+-way"),
        Line2D([], [], marker="o", color="none", markerfacecolor=C_3WAY,
               markeredgecolor="#495057", markersize=6, label="3-way"),
        Line2D([], [], marker="o", color="none", markerfacecolor=C_DEAD,
               markeredgecolor="#495057", markersize=6, label="cul-de-sac"),
    ]
    fig.legend(handles=handles, loc="lower center", ncol=9, frameon=False,
               fontsize=8.6, bbox_to_anchor=(0.5, -0.005), columnspacing=1.1,
               handletextpad=0.5)
    fig.text(0.995, 0.01, "Schematic — not to scale", fontsize=8,
             color="#868e96", ha="right", style="italic")
    fig.tight_layout(rect=[0, 0.06, 1, 1])
    fp = FIGDIR / "fig2_p1p2p3_schematic.png"
    fig.savefig(fp, dpi=300, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print(f"  wrote {fp.relative_to(paths.ROOT)}")
    provenance.log_progress("06d_schematic_p1p2p3", "P1/P2/P3 definitional schematic")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
