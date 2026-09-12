#!/usr/bin/env python
"""Stage 5 — why the spatially independent subsample gives a larger estimate (D-082).

The independent subsample returns roughly 2.5x the full-sample coefficient. The
direction favours the hypothesis, but a gap that size needs a mechanism rather
than a shrug. The candidate: segments whose 800 m catchments do not intersect are
selected for isolation, which correlates with being longer and more peripheral —
exactly the conditions under which P1 is well defined and access-serving arterials
dominate. This script measures that composition rather than asserting it.

Usage
-----
    uv run python code/05_model/05m_independent_composition.py
"""
from __future__ import annotations
import pathlib, sys
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
import geopandas as gpd, numpy as np, pandas as pd
from lib import cfg, paths, provenance

R = 800


def independent_set(cat):
    """Greedy maximal non-overlapping set, fewest conflicts first (D-057)."""
    idx = cat.sindex
    nb = {i: set(idx.query(g, predicate="intersects")) - {i}
          for i, g in enumerate(cat.geometry)}
    order = sorted(nb, key=lambda i: len(nb[i]))
    chosen, blocked = [], set()
    for i in order:
        if i in blocked:
            continue
        chosen.append(i)
        blocked |= nb[i]
    return chosen


def main() -> int:
    conf = cfg.config(); metric = conf["crs"]["metric"]
    pooled = pd.read_parquet(paths.ANALYSIS / f"analysis_pooled_r{R}.parquet")
    print(f"Environment: {provenance.environment_stamp()}")
    rows = []
    for c in sorted(set(pooled.city)):
        cat = gpd.read_parquet(paths.processed(c) / f"catchments_r{R}.parquet").to_crs(metric)
        cat = cat.reset_index(drop=True)
        keep = independent_set(cat)
        uids = set(c + "|" + cat.loc[keep, "segment_uid"].astype(str))
        g = pooled[pooled.city == c].copy()
        g["ind"] = g.segment_uid.isin(uids)
        for lab, sub in (("independent", g[g.ind]), ("full", g)):
            rows.append({"city": c, "set": lab, "n": len(sub),
                         "median_len_m": sub.length_m.median(),
                         "pct_p1": 100 * sub.p1_any.mean(),
                         "pct_access_controlled": 100 * sub.access_control_.isin([1, 2]).mean(),
                         "median_dist_cbd_km": sub.dist_cbd_km.median()})
        print(f"  {c}: {int(g.ind.sum()):,} independent of {len(g):,}")
    t = pd.DataFrame(rows)
    print(f"\n{'='*86}\nCOMPOSITION: independent subsample vs full sample\n{'='*86}")
    piv = t.pivot_table(index="set", values=["n", "median_len_m", "pct_p1",
                                             "pct_access_controlled", "median_dist_cbd_km"],
                        aggfunc={"n": "sum", "median_len_m": "median", "pct_p1": "mean",
                                 "pct_access_controlled": "mean", "median_dist_cbd_km": "median"})
    print(piv.round(2).to_string())
    print(f"\n  per city:")
    print(t.pivot(index="city", columns="set",
                  values=["median_len_m", "pct_p1", "median_dist_cbd_km"]).round(1).to_string())
    fp = paths.TABLES / "independent_subsample_composition.csv"
    t.to_csv(fp, index=False)
    print(f"\n  wrote {fp.relative_to(paths.ROOT)}")
    provenance.log_progress("05m_independent_composition",
                            "composition of the spatially independent subsample")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
