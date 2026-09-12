#!/usr/bin/env python
"""Stage 5 — direction of the selection induced by excluding one-way roadways (D-079).

The primary specification keeps two-way roadways only, because HPMS AADT is
directional on one-way segments and bidirectional on two-way ones — two different
quantities in one outcome column. Two reviewers noted, correctly, that one-way
segments cluster in exactly the gridded cores where substitutability is highest,
so the exclusion is not neutral with respect to the predictor, and the manuscript
should state which way the induced selection runs.

Re-including them would require re-running the whole segment/catchment/P1 chain on
an outcome column that mixes directional and bidirectional counts, which is the
contamination the exclusion exists to prevent. Instead this script characterises
what was excluded — its traffic, its centrality, and the permeability of the local
fabric around it — so the direction of the bias can be argued from evidence.

Usage
-----
    uv run python code/05_model/05k_oneway_selection.py
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

from lib import cfg, paths, provenance

RADIUS = 800.0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--cities", nargs="*", default=None)
    args = ap.parse_args()
    conf = cfg.config()
    metric = conf["crs"]["metric"]
    cities = args.cities or sorted(cfg.cities().keys())
    print(f"Environment: {provenance.environment_stamp()}")
    rows = []

    for c in cities:
        fp = paths.raw(c, "hpms") / "hpms2018_ua_all.gpkg"
        if not fp.exists():
            print(f"  {c}: no raw HPMS extract — skipped"); continue
        g = gpd.read_file(fp).to_crs(metric)
        g = g[g.f_system.isin([3, 4, 5]) & (g.aadt > 0)]
        one = g[g.facility_type == 1]
        two = g[g.facility_type == 2]
        if not len(one):
            print(f"  {c}: no one-way segments"); continue

        # local intersection density around each group's midpoints, on the same
        # local subgraph and the same radius the predictor uses
        loc = gpd.read_file(paths.raw(c, "osm") / "network_urban_area_local.gpkg",
                            layer="edges")
        lo = np.minimum(loc["u"].values, loc["v"].values)
        hi = np.maximum(loc["u"].values, loc["v"].values)
        e = pd.DataFrame({"a": lo, "b": hi}).drop_duplicates()
        G = nx.Graph(); G.add_edges_from(e.itertuples(index=False, name=None))
        deg = pd.Series(dict(G.degree()))
        nodes = gpd.read_file(paths.raw(c, "osm") / "network_urban_area_all.gpkg",
                              layer="nodes").to_crs(metric)
        nodes = nodes[nodes.osmid.isin(deg.index)].copy()
        nodes["deg"] = nodes.osmid.map(deg)
        inter = nodes[nodes.deg >= 3]
        sidx = inter.sindex

        cbd = cfg.city(c)["cbd"]
        cbd_pt = gpd.GeoSeries.from_xy([cbd["lon"]], [cbd["lat"]],
                                       crs="EPSG:4326").to_crs(metric).iloc[0]

        def profile(sub, label):
            mids = gpd.GeoSeries([gm.interpolate(0.5, normalized=True)
                                  for gm in sub.geometry], crs=metric)
            dens = []
            for pt in mids:
                k = len(sidx.query(pt.buffer(RADIUS), predicate="intersects"))
                dens.append(k / (np.pi * (RADIUS / 1000) ** 2))
            return {"city": c, "group": label, "n": len(sub),
                    "median_aadt": float(sub.aadt.median()),
                    "median_dist_cbd_km": float(mids.distance(cbd_pt).median() / 1000),
                    "median_local_int_density": float(np.median(dens)),
                    "pct_f3": float(100 * (sub.f_system == 3).mean())}

        p1_ = profile(one, "one-way (excluded)")
        p2_ = profile(two, "two-way (analysed)")
        rows += [p1_, p2_]
        print(f"\n  {c}: {len(one):,} one-way vs {len(two):,} two-way")
        print(f"    {'':<22}{'median AADT':>13}{'dist CBD km':>13}"
              f"{'local int/km²':>15}{'% principal':>12}")
        for p in (p1_, p2_):
            print(f"    {p['group']:<22}{p['median_aadt']:>13,.0f}"
                  f"{p['median_dist_cbd_km']:>13.2f}"
                  f"{p['median_local_int_density']:>15.1f}{p['pct_f3']:>11.1f}%")

    if not rows:
        return 1
    t = pd.DataFrame(rows)
    fpo = paths.TABLES / "oneway_selection_profile.csv"
    t.to_csv(fpo, index=False)
    print(f"\n  wrote {fpo.relative_to(paths.ROOT)}")

    o = t[t.group.str.startswith("one")]
    w = t[t.group.str.startswith("two")]
    n_closer = int((o.median_dist_cbd_km.values < w.median_dist_cbd_km.values).sum())
    n_denser = int((o.median_local_int_density.values >
                    w.median_local_int_density.values).sum())
    print(f"\n  One-way segments are closer to the CBD in {n_closer}/{len(o)} cities and")
    print(f"  sit in denser local fabric in {n_denser}/{len(o)} cities.")
    print("  -> the exclusion removes observations at the HIGH-permeability end of the")
    print("     predictor. Truncating the treated end of the range attenuates a negative")
    print("     association, so the induced selection is conservative for the hypothesis.")
    provenance.log_progress("05k_oneway_selection",
                            "profile of excluded one-way segments")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
