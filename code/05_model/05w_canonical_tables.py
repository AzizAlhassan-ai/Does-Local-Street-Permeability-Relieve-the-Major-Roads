#!/usr/bin/env python
"""Stage 5 — ONE estimation sample, every headline table computed from it (D-092).

A referee counted three values for the Denver coefficient, three for the pooled
corridor-FE estimate, and two different n between Table 3 and Table 6. Each was real:
different scripts dropped rows on different variable sets, so "the sample" was never
one thing. This script fixes the estimation sample once — complete cases on the
outcome, P1, the six controls, functional class, cell, route and log length — and
computes every quantity the manuscript leads with from it.

Betweenness is deliberately NOT in the complete-case rule. It is the RQ2 moderator, it
is missing by construction where the nearest major OSM edge is far from the segment
midpoint, and letting it govern the primary sample was what created the two n.
The one table that needs it reports its own, smaller n.

Usage
-----
    uv run python code/05_model/05w_canonical_tables.py
"""
from __future__ import annotations
import argparse, pathlib, sys
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
import numpy as np, pandas as pd, statsmodels.formula.api as smf
from lib import cfg, paths, provenance

CTRL = ["pop_density_km2_z", "lu_entropy_z", "dist_cbd_km_c_z",
        "dist_cbd_km_c_sq_z", "median_year_z", "through_lanes_z"]
R = 800


def z(s):
    sd = s.std(ddof=0)
    return (s - s.mean()) / sd if sd and sd > 0 else s * 0.0


def prep(d):
    d = d.copy()
    d["access_controlled"] = d["access_control_"].isin([1, 2]).astype(float)
    d["betweenness_log"] = np.log10(d["arterial_betweenness"] + 1e-5)
    src = {"pop_density_km2_z": "pop_density_km2", "lu_entropy_z": "lu_entropy",
           "dist_cbd_km_c_z": "dist_cbd_km_c", "dist_cbd_km_c_sq_z": "dist_cbd_km_c_sq",
           "median_year_z": "median_year_structure_built",
           "through_lanes_z": "through_lanes", "betw_z": "betweenness_log",
           "p2_z": "p2_pairs_per_km2", "p1n_z": "p1_routes"}
    g = d.groupby("city")
    for dst, s in src.items():
        d[dst] = g[s].transform(z)
    d["p1"] = d["p1_any"].astype(float)
    d["y"] = d["log_aadt"]
    d["loglen_z"] = d.groupby("city")["length_m"].transform(lambda s: z(np.log(s)))
    return d.dropna(subset=["y", "p1", "cell_id", "route_id", "f_system",
                            "loglen_z"] + CTRL).copy()


def fit(d, f):
    try:
        return smf.mixedlm(f, d, groups=d["cell_id"]).fit(method="lbfgs", reml=True)
    except Exception as e:
        print(f"    !! {e}")
        return None


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    args = ap.parse_args()
    d = prep(pd.read_parquet(paths.ANALYSIS / f"analysis_pooled_r{R}.parquet"))
    base = " + ".join(CTRL) + " + C(f_system)"
    cities = sorted(d.city.unique())
    print(f"Environment: {provenance.environment_stamp()}")
    print(f"\nCANONICAL ESTIMATION SAMPLE: n = {len(d):,}, "
          f"{d.cell_id.nunique():,} cells, {d.route_id.nunique():,} routes")
    print("  city shares: " + ", ".join(
        f"{c} {100*(d.city == c).mean():.1f}%" for c in cities))
    rows = []

    # ---------------------------------------------------------------- Table 3
    print(f"\n{'='*92}\nTABLE 3 — primary, per city\n{'='*92}")
    print(f"  {'city':<16}{'n':>8}{'cells':>8}{'β':>10}{'SE':>8}{'p':>9}"
          f"{'% AADT':>9}   95% CI")
    for c in cities:
        g = d[d.city == c]
        res = fit(g, f"y ~ {base} + p1")
        if res is None:
            continue
        b, se, p = res.params["p1"], res.bse["p1"], res.pvalues["p1"]
        print(f"  {c:<16}{len(g):>8,}{g.cell_id.nunique():>8,}{b:>+10.4f}{se:>8.4f}"
              f"{p:>9.4f}{100*(np.exp(b)-1):>8.1f}%   "
              f"[{b-1.96*se:+.3f}, {b+1.96*se:+.3f}]")
        rows.append({"table": "T3", "city": c, "n": len(g), "cells": g.cell_id.nunique(),
                     "beta": b, "se": se, "p": p, "pct": 100*(np.exp(b)-1),
                     "lo": b-1.96*se, "hi": b+1.96*se})
    res = fit(d, f"y ~ {base} + C(city) + p1")
    b, se, p = res.params["p1"], res.bse["p1"], res.pvalues["p1"]
    print(f"  {'pooled + city FE':<16}{len(d):>8,}{d.cell_id.nunique():>8,}{b:>+10.4f}"
          f"{se:>8.4f}{p:>9.4f}{100*(np.exp(b)-1):>8.1f}%")
    rows.append({"table": "T3", "city": "pooled + city FE", "n": len(d),
                 "cells": d.cell_id.nunique(), "beta": b, "se": se, "p": p,
                 "pct": 100*(np.exp(b)-1)})
    # equal weights with a bootstrap-t CI, replacing the model SE the panel flagged
    w = d.groupby("city")["y"].transform(lambda s: len(d) / (d.city.nunique() * len(s)))
    f_ = f"y ~ {base} + C(city) + p1"
    m0 = smf.wls(f_, d, weights=w).fit()
    t_obs = m0.params["p1"] / m0.bse["p1"]
    m_r = smf.wls(f"y ~ {base} + C(city)", d, weights=w).fit()
    fitr, resr = m_r.fittedvalues.to_numpy(), m_r.resid.to_numpy()
    codes = pd.Categorical(d.city).codes
    rng = np.random.default_rng(20260803)
    dd = d.copy(); tb = []; cnt = 0
    for _ in range(999):
        s = rng.choice([-1.0, 1.0], size=d.city.nunique())[codes]
        dd["_yb"] = fitr + resr * s
        mb = smf.wls(f_.replace("y ~", "_yb ~"), dd, weights=w).fit()
        t = mb.params["p1"] / mb.bse["p1"]
        tb.append(t); cnt += abs(t) >= abs(t_obs)
    p_wcb = (cnt + 1) / 1000
    q = np.quantile(np.abs(tb), 0.95)
    lo, hi = m0.params["p1"] - q*m0.bse["p1"], m0.params["p1"] + q*m0.bse["p1"]
    print(f"  {'pooled, equal w.':<16}{len(d):>8,}{'':>8}{m0.params['p1']:>+10.4f}"
          f"{'—':>8}{p_wcb:>9.4f}{100*(np.exp(m0.params['p1'])-1):>8.1f}%   "
          f"bootstrap-t CI [{lo:+.3f}, {hi:+.3f}]")
    rows.append({"table": "T3", "city": "pooled, equal weights", "n": len(d),
                 "beta": m0.params["p1"], "p": p_wcb, "lo": lo, "hi": hi,
                 "pct": 100*(np.exp(m0.params["p1"])-1)})

    # ------------------------------------------------------------ Table 5
    print(f"\n{'='*92}\nTABLE 5 — corridor (route) fixed effects, same sample\n{'='*92}")
    keep = d.groupby("route_id")["p1"].transform(lambda s: s.nunique() > 1)
    dw = d[keep].copy()
    print(f"  routes with within-route P1 variation: {dw.route_id.nunique():,} "
          f"({len(dw):,} of {len(d):,} segments)")
    print(f"  {'city':<16}{'n':>8}{'routes':>8}{'β':>10}{'SE':>8}{'p':>9}{'% AADT':>9}")
    for c in cities + ["POOLED"]:
        g = dw if c == "POOLED" else dw[dw.city == c]
        if len(g) < 100 or g.route_id.nunique() < 10:
            print(f"  {c:<16} too few — skipped"); continue
        m = smf.ols(f"y ~ {base} + C(route_id) + p1", g).fit(
            cov_type="cluster", cov_kwds={"groups": g["route_id"]})
        b, se, p = m.params["p1"], m.bse["p1"], m.pvalues["p1"]
        print(f"  {c:<16}{len(g):>8,}{g.route_id.nunique():>8,}{b:>+10.4f}{se:>8.4f}"
              f"{p:>9.4f}{100*(np.exp(b)-1):>8.1f}%")
        rows.append({"table": "T5", "city": c, "n": len(g),
                     "routes": g.route_id.nunique(), "beta": b, "se": se, "p": p,
                     "pct": 100*(np.exp(b)-1)})

    # ------------------------------------------------------------ Table 7
    print(f"\n{'='*92}\nTABLE 7 — moderation (needs betweenness; own n)\n{'='*92}")
    dmo = d.dropna(subset=["betw_z", "access_controlled"])
    print(f"  n = {len(dmo):,} (betweenness missing on {len(d)-len(dmo):,} rows)")
    res = fit(dmo, f"y ~ {base} + C(city) + p1 + access_controlled + betw_z"
                   f" + p1:access_controlled + p1:betw_z")
    if res is not None:
        for t in ["p1", "access_controlled", "betw_z", "p1:access_controlled",
                  "p1:betw_z"]:
            print(f"  {t:<24}{res.params[t]:>+9.4f} (SE {res.bse[t]:.4f}, "
                  f"p = {res.pvalues[t]:.4f})")
            rows.append({"table": "T7", "term": t, "n": len(dmo),
                         "beta": res.params[t], "se": res.bse[t], "p": res.pvalues[t]})

    # ------------------------------------------------------------ P1 vs P2
    print(f"\n{'='*92}\nP1 AGAINST P2, on a common per-SD footing\n{'='*92}")
    dp = d.dropna(subset=["p2_z"])
    res = fit(dp, f"y ~ {base} + C(city) + p1 + p2_z")
    if res is not None:
        sd_p1 = dp.p1.std(ddof=0)
        b1, b2 = res.params["p1"], res.params["p2_z"]
        e1, e2 = 100*(np.exp(b1*sd_p1)-1), 100*(np.exp(b2)-1)
        print(f"  P1 {b1:+.4f} (per SD of the dummy, SD = {sd_p1:.3f}) -> {e1:+.2f}% AADT")
        print(f"  P2 {b2:+.4f} (per SD)                        -> {e2:+.2f}% AADT")
        print(f"  ratio on a common footing: {e1/e2:.2f}×  "
              f"(the raw coefficient ratio, {b1/b2:.1f}×, is not scale-invariant)")
        rows.append({"table": "P1vsP2", "p1_per_sd_pct": e1, "p2_per_sd_pct": e2,
                     "ratio": e1/e2, "n": len(dp)})
    # continuous route-count form as a co-primary
    res = fit(d, f"y ~ {base} + C(city) + p1n_z")
    if res is not None:
        print(f"  route-count form (per SD): {res.params['p1n_z']:+.4f} "
              f"(SE {res.bse['p1n_z']:.4f}, p = {res.pvalues['p1n_z']:.4f}) -> "
              f"{100*(np.exp(res.params['p1n_z'])-1):+.2f}% AADT")
        rows.append({"table": "P1count", "beta": res.params["p1n_z"],
                     "se": res.bse["p1n_z"], "p": res.pvalues["p1n_z"],
                     "pct": 100*(np.exp(res.params["p1n_z"])-1)})

    # ------------------------------------------------------------ length strata
    print(f"\n{'='*92}\nLENGTH STRATA, same sample\n{'='*92}")
    edges = [0, 200, 400, 800, 1600, np.inf]
    labs = ["<200 m", "200–400", "400–800", "800–1600", "≥1600 m"]
    d["strat"] = pd.cut(d.length_m, edges, labels=labs)
    for s_ in labs:
        g = d[d.strat == s_]
        if len(g) < 200 or g.p1.nunique() < 2:
            continue
        rr = fit(g, f"y ~ {base} + C(city) + p1")
        if rr is None:
            continue
        print(f"  {s_:<12}n={len(g):>7,}  %P1={100*g.p1.mean():>5.1f}%  "
              f"β={rr.params['p1']:>+8.4f} (p={rr.pvalues['p1']:.4f})")
        rows.append({"table": "strata", "stratum": s_, "n": len(g),
                     "pct_p1": 100*g.p1.mean(), "beta": rr.params["p1"],
                     "p": rr.pvalues["p1"]})

    out = pd.DataFrame(rows)
    fp = paths.TABLES / "canonical_tables.csv"
    out.to_csv(fp, index=False)
    print(f"\n  wrote {fp.relative_to(paths.ROOT)}")
    provenance.log_progress("05w_canonical_tables",
                            "one estimation sample for every headline table (D-092)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
