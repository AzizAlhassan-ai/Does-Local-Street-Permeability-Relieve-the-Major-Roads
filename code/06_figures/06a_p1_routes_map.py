#!/usr/bin/env python
"""Stage 6a — map the detected P1 substitutable routes for visual validation.

Two panels so the eyeball test is a contrast, not just an example:
  (a) the config test area — inner Denver grid, where substitutes should be obvious
  (b) an automatically-selected suburban area where P1 = 0 despite local streets

Usage
-----
    uv run python code/06_figures/06a_p1_routes_map.py --city denver
"""

from __future__ import annotations

import argparse
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

import geopandas as gpd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.lines import Line2D
from shapely.geometry import box

from lib import cfg, paths, provenance


def clip(gdf, b):
    idx = list(gdf.sindex.query(b, predicate="intersects"))
    return gdf.iloc[idx].copy()


def panel(ax, b, maj, loc, seg, routes, title, subtitle):
    clip(loc, b).plot(ax=ax, color="#c9ccd1", linewidth=0.55, zorder=1)
    clip(maj, b).plot(ax=ax, color="#7c828c", linewidth=1.7, zorder=2)
    s = clip(seg, b)
    with_p1 = s[s.p1_routes > 0]
    no_p1 = s[s.p1_routes == 0]
    no_p1.plot(ax=ax, color="#1f3d7a", linewidth=3.4, zorder=3, alpha=.85)
    with_p1.plot(ax=ax, color="#0b8a4b", linewidth=3.4, zorder=4, alpha=.9)
    r = clip(routes, b) if routes is not None and len(routes) else None
    if r is not None and len(r):
        r.plot(ax=ax, color="#e8590c", linewidth=2.2, linestyle=(0, (5, 2)), zorder=5)
    minx, miny, maxx, maxy = b.bounds
    ax.set_xlim(minx, maxx); ax.set_ylim(miny, maxy)
    ax.set_xticks([]); ax.set_yticks([])
    for sp in ax.spines.values():
        sp.set_edgecolor("#adb5bd")
    ax.set_title(title, fontsize=12, fontweight="bold", pad=24, loc="left")
    ax.text(0.0, 1.008, subtitle, transform=ax.transAxes, fontsize=8.6,
            color="#495057", va="bottom")
    # scale bar
    span = maxx - minx
    L = 500 if span > 2200 else 250
    x0, y0 = minx + span * .05, miny + (maxy - miny) * .05
    ax.plot([x0, x0 + L], [y0, y0], color="#212529", lw=2.4, solid_capstyle="butt")
    ax.text(x0 + L / 2, y0 + (maxy - miny) * .012, f"{L} m", ha="center",
            fontsize=8, color="#212529")
    # north arrow (axes are in the city's UTM zone, true-north-up)
    ax.annotate("", xy=(0.95, 0.945), xytext=(0.95, 0.885),
                xycoords="axes fraction",
                arrowprops=dict(arrowstyle="-|>", color="#212529", lw=1.4))
    ax.text(0.95, 0.95, "N", transform=ax.transAxes, ha="center", va="bottom",
            fontsize=10, fontweight="bold", color="#212529")
    return len(with_p1), len(no_p1), (len(r) if r is not None else 0)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--city", default=None)
    args = ap.parse_args()
    conf = cfg.config()
    city = args.city or conf["project"]["pilot_city"]
    C = cfg.city(city)
    metric = conf["crs"]["metric"]
    r0 = conf["catchment"]["primary_radius_m"]

    maj = gpd.read_file(paths.raw(city, "osm") / "network_urban_area_major.gpkg",
                        layer="edges")
    # plot in the city's UTM zone so panels are true-north-up (D-002 is the
    # analysis CRS only; EPSG:5070 grid north is ~5° off true north in Denver)
    metric = maj.estimate_utm_crs()
    maj = maj.to_crs(metric)
    loc = gpd.read_file(paths.raw(city, "osm") / "network_urban_area_local.gpkg",
                        layer="edges").to_crs(metric)
    seg = gpd.read_parquet(paths.processed(city) / "segments.parquet").to_crs(metric)
    thru = pd.read_parquet(paths.processed(city) / f"through_routes_r{r0}.parquet")
    seg = seg.merge(thru[["segment_uid", "p1_routes"]], on="segment_uid", how="left")
    seg["p1_routes"] = seg["p1_routes"].fillna(0)

    rt_fp = paths.processed(city) / "p1_routes_testarea.gpkg"
    routes = gpd.read_file(rt_fp).to_crs(metric) if rt_fp.exists() else None

    # panel (a): configured test area
    w, s, e, n = C["test_area"]["bbox_wsen"]
    b1 = gpd.GeoSeries([box(w, s, e, n)], crs="EPSG:4326").to_crs(metric).iloc[0]

    # panel (b): suburban contrast — dense-ish local fabric but no substitutes
    # D-053: analysis tables are per city
    tab = pd.read_parquet(paths.ANALYSIS / f"analysis_table_{city}.parquet")
    cand = tab[(tab.p1_routes == 0) & (tab.local_deadend_share > 0.45) &
               (tab.dist_cbd_km > 12) & (tab.local_int_density > 15)]
    sub = seg[seg.segment_uid.isin(cand.segment_uid)]
    if len(sub):
        c = sub.geometry.iloc[len(sub) // 2].centroid
        half = 1300
        b2 = box(c.x - half, c.y - half, c.x + half, c.y + half)
    else:
        b2 = b1

    fig, axes = plt.subplots(1, 2, figsize=(15.5, 7.6))
    fig.patch.set_facecolor("white")
    a1 = panel(axes[0], b1, maj, loc, seg, routes,
               "A · Inner Denver grid (test area)",
               C["test_area"]["note"])
    a2 = panel(axes[1], b2, maj, loc, seg, routes,
               "B · Suburban contrast (P1 = 0)",
               "auto-selected: dead-end share > 0.45, >12 km from CBD")

    handles = [
        Line2D([], [], color="#0b8a4b", lw=3.4, label="Arterial WITH substitutable route (P1 > 0)"),
        Line2D([], [], color="#1f3d7a", lw=3.4, label="Arterial with NO substitute (P1 = 0)"),
        Line2D([], [], color="#e8590c", lw=2.2, ls=(0, (5, 2)), label="Detected P1 route (local-only)"),
        Line2D([], [], color="#7c828c", lw=1.7, label="Major network (excluded from P1 paths)"),
        Line2D([], [], color="#c9ccd1", lw=0.9, label="Local network"),
    ]
    fig.legend(handles=handles, loc="lower center", ncol=5, frameon=False,
               fontsize=9.2, bbox_to_anchor=(0.5, 0.005))
    fig.suptitle("P1 — substitutable local through-routes, Denver "
                 f"(detour cap {conf['through_routes']['detour_cap']}×, r = {r0} m)",
                 fontsize=14, fontweight="bold", y=0.985)
    fig.tight_layout(rect=[0, 0.055, 1, 0.955])
    out = paths.FIGURES / "p1_routes_denver.png"
    fig.savefig(out, dpi=300, facecolor="white")
    print(f"panel A: {a1[0]} segments with P1, {a1[1]} without, {a1[2]} routes drawn")
    print(f"panel B: {a2[0]} segments with P1, {a2[1]} without, {a2[2]} routes drawn")
    print(f"wrote {out.relative_to(paths.ROOT)}")
    provenance.log_progress("06a_p1_routes_map", f"{city}: P1 route validation map")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
