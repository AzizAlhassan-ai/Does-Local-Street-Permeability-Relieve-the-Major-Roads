#!/usr/bin/env python
"""Stage 6 — forest plot of per-city estimates, and a to-scale measure-geometry panel.

Two figure requests from the review panel:

  * A FOREST PLOT to replace "significant in four of six" vote-counting, which is a weak
    summary across cities of very different n. The reader should see the heterogeneity
    and the intervals directly.
  * A TO-SCALE panel for the schematic. P1's behaviour depends on the ratio of the
    endpoint attach radius to the segment length, and a not-to-scale drawing hides
    exactly the geometry that makes the measure ill-posed on short segments.

Usage
-----
    uv run python code/06_figures/06e_forest_and_scale.py
"""
from __future__ import annotations
import argparse, pathlib, sys
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np, pandas as pd
from matplotlib.patches import Circle, FancyArrow
from lib import cfg, paths, provenance

LAB = {"denver": "Denver–Aurora", "portland": "Portland", "phoenix": "Phoenix",
       "charlotte": "Charlotte", "boston": "Boston", "wasatch_front": "Wasatch Front"}
ATTACH = 200.0


def forest():
    t = pd.read_csv(paths.TABLES / "primary_v2.csv")
    p = t[(t.table == "T_primary") & t.city.isin(LAB)].copy()
    c = t[(t.table == "T_corridor") & t.city.isin(LAB)].copy()
    p = p.sort_values("beta")
    order = list(p.city)
    fig, ax = plt.subplots(figsize=(9.2, 5.4))
    ypos = np.arange(len(order))[::-1]

    for i, city in enumerate(order):
        y = ypos[i]
        r = p[p.city == city].iloc[0]
        ax.plot([r.lo, r.hi], [y + 0.16] * 2, color="#1f4e79", lw=2.1,
                solid_capstyle="butt", zorder=2)
        ax.plot([r.beta], [y + 0.16], "o", ms=8, color="#1f4e79", zorder=3)
        ax.annotate(f"n = {int(r.n):,}", (1.008, y), xycoords=("axes fraction", "data"),
                    fontsize=8.2, color="#374151", va="center", annotation_clip=False)
        cc = c[c.city == city]
        if len(cc):
            rc = cc.iloc[0]
            lo, hi = rc.beta - 1.96 * rc.se, rc.beta + 1.96 * rc.se
            ax.plot([lo, hi], [y - 0.16] * 2, color="#b45309", lw=2.1,
                    solid_capstyle="butt", zorder=2)
            ax.plot([rc.beta], [y - 0.16], "s", ms=7, color="#b45309", zorder=3)

    pooled = t[(t.table == "T_primary") & (t.city == "pooled + city FE")]
    eq = t[(t.table == "T_primary") & (t.city == "pooled, equal weights")]
    yb = -1.15
    if len(pooled):
        r = pooled.iloc[0]
        lo, hi = r.beta - 1.96 * r.se, r.beta + 1.96 * r.se
        ax.plot([lo, hi], [yb + 0.16] * 2, color="#111827", lw=2.6)
        ax.plot([r.beta], [yb + 0.16], "D", ms=8, color="#111827")
    if len(eq):
        ax.plot([eq.iloc[0].beta], [yb - 0.16], "D", ms=8, color="#6b7280")
        ax.annotate(f"equal city weights, randomization p = {eq.iloc[0].p:.3f}",
                    (eq.iloc[0].beta - 0.012, yb - 0.16), fontsize=8.2, color="#6b7280",
                    va="center", ha="right")

    ax.axvline(0, color="#9ca3af", lw=1, zorder=1)
    ax.axhline(-0.55, color="#e5e7eb", lw=1)
    ax.set_yticks(list(ypos) + [yb])
    ax.set_yticklabels([LAB[c_] for c_ in order] + ["Pooled"], fontsize=10)
    ax.set_xlabel("Effect of a substitutable local route on log(AADT), with 95% interval")
    sec = ax.secondary_xaxis("top", functions=(lambda b: 100 * (np.exp(b) - 1),
                                               lambda q: np.log1p(q / 100)))
    sec.set_xlabel("equivalent % change in AADT", fontsize=9)
    from matplotlib.lines import Line2D
    ax.legend(handles=[Line2D([], [], color="#1f4e79", marker="o", lw=2.1,
                              label="cross-sectional (per city)"),
                       Line2D([], [], color="#b45309", marker="s", lw=2.1,
                              label="within corridor (route fixed effects)")],
              loc="upper center", bbox_to_anchor=(0.5, -0.17), ncol=2,
              frameon=False, fontsize=9)
    ax.set_ylim(yb - 0.55, len(order) - 0.3)
    for s in ("top", "right", "left"):
        ax.spines[s].set_visible(False)
    ax.tick_params(axis="y", length=0)
    fig.tight_layout()
    fp = paths.FIGURES / "fig8_forest.png"
    fig.savefig(fp, dpi=300, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print(f"  wrote {fp.relative_to(paths.ROOT)}")


def scale_panel():
    """Two arterial segments drawn on ONE shared scale against the 200 m attach radius.

    Both panels share an identical x- and y-range, so the 200 m radius is the same
    physical length in each and the reader can compare the two geometries directly.
    That is the whole point of the figure: on a 110 m unit the two attach discs overlap,
    and the measure is searching for a route between two largely identical node sets.
    """
    HALF, YH = 780.0, 570.0
    fig, axes = plt.subplots(1, 2, figsize=(12.0, 5.2))
    for ax, L, title in (
        (axes[0], 800.0, "(a) 800 m — the median unit under the revised primary frame"),
        (axes[1], 110.0, "(b) 110 m — the median Boston unit under the previous frame"),
    ):
        ax.set_aspect("equal")
        ax.set_xlim(L / 2 - HALF, L / 2 + HALF)
        ax.set_ylim(-YH, YH)
        for x in (0.0, L):
            ax.add_patch(Circle((x, 0), ATTACH, facecolor="#1f4e79", alpha=0.15,
                                edgecolor="#1f4e79", lw=1.1, ls="--", zorder=1))
        ax.plot([0, L], [0, 0], color="#111827", lw=5.0, solid_capstyle="butt", zorder=3)
        ax.plot([0, L], [0, 0], "o", color="#111827", ms=7.5, zorder=4)

        # attach radius, drawn from the left endpoint, labelled clear of the discs
        ax.annotate("", xy=(ATTACH, ATTACH + 55), xytext=(0, ATTACH + 55),
                    arrowprops=dict(arrowstyle="<->", color="#1f4e79", lw=1.2))
        ax.text(ATTACH / 2, ATTACH + 78, "attach radius 200 m", ha="center", va="bottom",
                fontsize=9, color="#1f4e79")

        # segment length, below the discs
        yl = -(ATTACH + 55)
        ax.annotate("", xy=(L, yl), xytext=(0, yl),
                    arrowprops=dict(arrowstyle="<->", color="#374151", lw=1.2))
        ax.text(L / 2, yl - 26, f"segment length {L:.0f} m", ha="center", va="top",
                fontsize=9, color="#374151")

        overlap = max(0.0, 2 * ATTACH - L)
        if overlap <= 0:
            note = ("the attach discs are disjoint, so a qualifying route\n"
                    "must genuinely span the road")
            col = "#065f46"
        else:
            note = (f"the attach discs overlap over {overlap:.0f} m, and the detour cap\n"
                    f"(1.5 × {L:.0f} = {1.5 * L:.0f} m) is shorter than the attach radius:\n"
                    "the measure is ill-posed here, not merely imprecise")
            col = "#7f1d1d"
        ax.text(L / 2, -YH + 14, note, ha="center", va="bottom", fontsize=8.6, color=col)
        ax.set_title(title, fontsize=10.5, loc="left", pad=10)
        ax.axis("off")
    fig.tight_layout()
    fp = paths.FIGURES / "fig9_measure_geometry.png"
    fig.savefig(fp, dpi=300, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print(f"  wrote {fp.relative_to(paths.ROOT)}")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.parse_args()
    print(f"Environment: {provenance.environment_stamp()}")
    forest()
    scale_panel()
    provenance.log_progress("06e_forest_and_scale",
                            "forest plot of per-city estimates; to-scale measure geometry")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
