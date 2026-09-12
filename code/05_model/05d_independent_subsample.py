#!/usr/bin/env python
"""Stage 5 — D-046: H1 on SPATIALLY INDEPENDENT segments, per city then pooled.

The problem this addresses. Catchments overlap heavily (median 27 neighbours at
r=800 m even after the D-028 dissolve), so nominal n massively overstates effective n
and the full-sample standard errors are optimistic. In Denver alone the independent
subsample gave beta = -0.069 against a full-sample -0.249 — the single largest
outstanding threat to H1. Cities do not overlap each other, so pooling five disjoint
metros is the only way to buy independent observations.

D-057 — selection rule. The Stage 4 version selected units in DESCENDING ORDER OF THE
OUTCOME, which is selection on the dependent variable and can bias the subsample
estimate. This version selects by FEWEST CONFLICTS FIRST (a standard maximum-
independent-set heuristic), which is independent of y, deterministic, and retains more
units. A random-order variant is also reported so the result cannot be an artefact of
either rule.

Per D-054, per-city estimates are primary and pooled is secondary.

Usage
-----
    uv run python code/05_model/05d_independent_subsample.py
"""

from __future__ import annotations

import argparse
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

import geopandas as gpd
import numpy as np
import pandas as pd
import statsmodels.formula.api as smf

from lib import cfg, paths, provenance

CTRL = ["pop_z", "ent_z", "dcbd_z", "dcbd2_z", "yr_z", "ln_z"]


def z(s):
    sd = s.std(ddof=0)
    return (s - s.mean()) / sd if sd and sd > 0 else s * 0.0


def prep(d):
    d = d.copy()
    d["access_controlled"] = d["access_control_"].isin([1, 2]).astype(float)
    for dst, src in [("pop_z", "pop_density_km2"), ("ent_z", "lu_entropy"),
                     ("dcbd_z", "dist_cbd_km_c"), ("dcbd2_z", "dist_cbd_km_c_sq"),
                     ("yr_z", "median_year_structure_built"), ("ln_z", "through_lanes")]:
        d[dst] = z(d[src])
    d["p1"] = d["p1_any"].astype(float)
    return d.dropna(subset=["log_aadt", "p1", "f_system"] + CTRL).copy()


def independent_set(cat: gpd.GeoDataFrame, order: str, seed: int) -> list[int]:
    """Greedy maximal independent set over the catchment-overlap graph (D-057)."""
    sidx = cat.sindex
    nbrs = {}
    for i, geom in enumerate(cat.geometry):
        hit = {int(j) for j in sidx.query(geom, predicate="intersects")} - {i}
        nbrs[i] = hit
    if order == "fewest_conflicts":
        seq = sorted(range(len(cat)), key=lambda i: (len(nbrs[i]), i))
    else:
        rng = np.random.default_rng(seed)
        seq = list(rng.permutation(len(cat)))
    chosen, blocked = [], set()
    for i in seq:
        if i in blocked:
            continue
        chosen.append(i)
        blocked |= nbrs[i]
    return chosen


def fit_h1(d, label):
    """OLS with HC3 SEs. Units are independent by construction, so no random effect."""
    if len(d) < 60 or d["p1"].nunique() < 2 or d["f_system"].nunique() < 2:
        return None
    f = "log_aadt ~ " + " + ".join(CTRL) + " + C(f_system) + p1"
    try:
        m = smf.ols(f, d).fit(cov_type="HC3")
    except Exception as e:
        print(f"    !! {label} failed: {e}")
        return None
    b, se, p = m.params["p1"], m.bse["p1"], m.pvalues["p1"]
    return {"n": len(d), "beta": b, "se": se, "p": p,
            "lo": b - 1.96 * se, "hi": b + 1.96 * se,
            "pct": 100 * (np.exp(b) - 1), "mde": 2.8 * se}


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--radius", type=int, default=None)
    args = ap.parse_args()
    conf = cfg.config()
    r = args.radius or conf["catchment"]["primary_radius_m"]
    seed = conf["reproducibility"]["random_seed"]
    metric = conf["crs"]["metric"]

    print(f"Environment: {provenance.environment_stamp()}")
    pooled = pd.read_parquet(paths.ANALYSIS / f"analysis_pooled_r{r}.parquet")
    cities = sorted(pooled.city.unique())
    print(f"radius {r} m | cities {len(cities)} | full-sample rows {len(pooled):,}\n")

    rows, keep_all = [], []
    for c in cities:
        dc = prep(pooled[pooled.city == c])
        cat = gpd.read_parquet(paths.processed(c) / f"catchments_r{r}.parquet").to_crs(metric)
        # catchments carry the un-namespaced uid; pooled has "city|uid"
        cat["segment_uid"] = c + "|" + cat["segment_uid"].astype(str)
        cat = cat[cat.segment_uid.isin(dc.segment_uid)].reset_index(drop=True)
        if cat.empty:
            print(f"  {c}: no catchments matched"); continue

        idx = independent_set(cat, "fewest_conflicts", seed)
        keep = set(cat.segment_uid.iloc[idx])
        sub = dc[dc.segment_uid.isin(keep)]
        keep_all.extend(keep)

        full = fit_h1(dc, f"{c} full")
        ind = fit_h1(sub, f"{c} independent")
        # random-order variant, as an artefact check
        idx_r = independent_set(cat, "random", seed)
        sub_r = dc[dc.segment_uid.isin(set(cat.segment_uid.iloc[idx_r]))]
        ind_r = fit_h1(sub_r, f"{c} independent(random)")

        rows.append({"city": c, "n_full": len(dc), "n_ind": len(sub),
                     "retain": len(sub) / len(dc),
                     "b_full": full["beta"] if full else np.nan,
                     "b_ind": ind["beta"] if ind else np.nan,
                     "se_ind": ind["se"] if ind else np.nan,
                     "p_ind": ind["p"] if ind else np.nan,
                     "lo": ind["lo"] if ind else np.nan,
                     "hi": ind["hi"] if ind else np.nan,
                     "mde": ind["mde"] if ind else np.nan,
                     "b_ind_rand": ind_r["beta"] if ind_r else np.nan})

    t = pd.DataFrame(rows)
    print("=" * 96)
    print("PER-CITY (primary, D-054): H1 on spatially independent segments")
    print("=" * 96)
    print(f"{'city':<15}{'n full':>8}{'n indep':>9}{'kept':>7}"
          f"{'b full':>9}{'b indep':>9}{'SE':>8}{'p':>8}{'MDE':>7}  95% CI")
    for _, x in t.iterrows():
        star = ("***" if x.p_ind < .001 else "**" if x.p_ind < .01
                else "*" if x.p_ind < .05 else "")
        print(f"{x.city:<15}{x.n_full:>8,.0f}{x.n_ind:>9,.0f}{x.retain:>6.1%}"
              f"{x.b_full:>9.3f}{x.b_ind:>9.3f}{x.se_ind:>8.3f}{x.p_ind:>8.3f}"
              f"{x.mde:>7.3f}  [{x.lo:+.3f},{x.hi:+.3f}] {star}")

    ok = t.dropna(subset=["b_ind"])
    print(f"\n  negative in {(ok.b_ind < 0).sum()}/{len(ok)} cities; "
          f"significant (p<.05) in {((ok.p_ind < .05) & (ok.b_ind < 0)).sum()}/{len(ok)}")
    print(f"  selection-rule check — max |fewest-conflicts − random| = "
          f"{(ok.b_ind - ok.b_ind_rand).abs().max():.4f} "
          f"(large values would mean the result is an artefact of the ordering)")

    # ---------- pooled (secondary) ----------
    print("\n" + "=" * 96)
    print("POOLED (secondary): all independent segments across cities")
    print("=" * 96)
    dp = prep(pooled[pooled.segment_uid.isin(keep_all)])
    f = ("log_aadt ~ " + " + ".join(CTRL) + " + C(f_system) + C(city) + p1")
    m = smf.ols(f, dp).fit(cov_type="HC3")
    b, se, p = m.params["p1"], m.bse["p1"], m.pvalues["p1"]
    print(f"  n = {len(dp):,} independent units across {dp.city.nunique()} cities "
          f"(Denver alone in Stage 4 had 239)")
    print(f"  p1 = {b:+.4f} (SE {se:.4f}), p = {p:.4f}, {100*(np.exp(b)-1):+.1f}% AADT")
    print(f"  95% CI [{b-1.96*se:+.4f}, {b+1.96*se:+.4f}]")
    print(f"  minimum detectable effect at 80% power: {2.8*se:.4f}")

    full_pool = prep(pooled)
    mf = smf.ols(f, full_pool).fit(cov_type="HC3")
    print(f"\n  for comparison, FULL pooled sample (n={len(full_pool):,}): "
          f"p1 = {mf.params['p1']:+.4f} (SE {mf.bse['p1']:.4f})")
    print(f"  full-sample estimate inside the independent CI: "
          f"{b-1.96*se <= mf.params['p1'] <= b+1.96*se}")

    t.to_csv(paths.TABLES / f"h1_independent_subsample_r{r}.csv", index=False)
    print(f"\n  wrote outputs/tables/h1_independent_subsample_r{r}.csv")
    provenance.log_progress("05d_independent_subsample",
                            f"D-046 independent-subsample H1, r={r} m, "
                            f"{len(dp):,} independent units")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
