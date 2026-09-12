#!/usr/bin/env python
"""Stage 5 — the REVISED primary specification (D-093..D-096).

Two changes to the estimation frame, both requested by the review panel and both
adopted because they are right rather than because they were asked for.

D-093  The exogenous ("AADT-free") unit definition becomes PRIMARY. Units are contiguous
       runs of HPMS increments sharing the five exogenous attributes, capped at half a
       mile, with AADT the length-weighted mean inside each unit. Nothing about a unit's
       extent is a function of the outcome. The previous frame, which had AADT in the
       dissolve key, is demoted to a robustness branch.

D-094  P1 IS TREATED AS UNDEFINED below twice the endpoint attach radius (2 x 200 m =
       400 m) and those segments are EXCLUDED rather than coded as untreated. On a
       110 m unit the two 200 m attach discs overlap almost entirely, the detour cap
       (1.5 x 110 = 165 m) is shorter than the attach radius, and the span requirement is
       trivially satisfied: the measure is not weakly identified there, it is ill-posed.
       Coding such a segment "no substitute" is misclassification, and it is non-random
       with respect to city, since Boston's median unit was 110 m.

D-095  Job density enters as a seventh control. The panel asked for it specifically as a
       test of whether the generic metrics' positive sign is centrality confounding; it
       belongs in the primary set for the same reason.

D-096  Pooled inference is by RANDOMIZATION over the six cities. With G = 6, Rademacher
       weights admit only 2^6 = 64 distinct draws, so a 999-replication wild bootstrap
       reports precision it does not have. The randomization distribution is enumerated
       exhaustively instead, and the achievable p-value grid is reported.

Usage
-----
    uv run python code/05_model/05x_primary_v2.py
"""
from __future__ import annotations
import argparse, itertools, pathlib, sys
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
import numpy as np, pandas as pd, statsmodels.api as sm, statsmodels.formula.api as smf
from lib import cfg, paths, provenance

R = 800
MIN_LEN = 400.0                       # D-094: 2 x the 200 m endpoint attach radius
CTRL = ["pop_density_km2_z", "job_density_km2_z", "lu_entropy_z", "dist_cbd_km_c_z",
        "dist_cbd_km_c_sq_z", "median_year_z", "through_lanes_z"]
BAL = {"pop_density_km2": "population density (/km²)",
       "job_density_km2": "job density (/km²)",
       "median_year_structure_built": "median year built",
       "dist_cbd_km": "distance to CBD (km)",
       "through_lanes": "through lanes",
       "length_m": "segment length (m)"}


def z(s):
    sd = s.std(ddof=0)
    return (s - s.mean()) / sd if sd and sd > 0 else s * 0.0


def load(frame="aadtfree", floor=MIN_LEN, r=R):
    suf = f"__{frame}" if frame else ""
    fp = paths.DATA / f"analysis{suf}" / f"analysis_pooled_r{r}.parquet"
    if not fp.exists():
        raise SystemExit(f"ERROR: {fp} missing")
    d = pd.read_parquet(fp).copy()
    d["_n_raw"] = len(d)
    if floor:
        d = d[d.length_m >= floor].copy()
    d["access_controlled"] = d["access_control_"].isin([1, 2]).astype(float)
    if "arterial_betweenness" in d.columns:
        d["betweenness_log"] = np.log10(d["arterial_betweenness"] + 1e-5)
    src = {"pop_density_km2_z": "pop_density_km2", "job_density_km2_z": "job_density_km2",
           "lu_entropy_z": "lu_entropy", "dist_cbd_km_c_z": "dist_cbd_km_c",
           "dist_cbd_km_c_sq_z": "dist_cbd_km_c_sq",
           "median_year_z": "median_year_structure_built",
           "through_lanes_z": "through_lanes", "p2_z": "p2_pairs_per_km2",
           "p1n_z": "p1_routes"}
    if "betweenness_log" in d.columns:
        src["betw_z"] = "betweenness_log"
    g = d.groupby("city")
    for dst, s in src.items():
        if s in d.columns:
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


def corridor_fe(g, terms):
    """Route fixed effects by within-transformation, cluster-robust on route.

    Dummy-variable route FE puts >1,000 columns in the design matrix and the SVD does
    not converge on the larger cities. Absorbing the effects by demeaning is the same
    estimator and is numerically stable; the residual degrees of freedom are corrected
    for the absorbed effects explicitly.
    """
    X = pd.get_dummies(g[terms + ["f_system"]], columns=["f_system"], drop_first=True)
    X = X.astype(float)
    y = g["y"].to_numpy(float)
    rid = g["route_id"].to_numpy()
    dfm = pd.DataFrame(X)
    dfm["_y"] = y
    dfm["_r"] = rid
    dm = dfm.groupby("_r").transform("mean")
    Xd = (dfm[X.columns] - dm[X.columns]).to_numpy(float)
    yd = (dfm["_y"] - dm["_y"]).to_numpy(float)
    keep = Xd.std(axis=0) > 1e-10
    Xd, cols = Xd[:, keep], list(np.array(X.columns)[keep])
    XtX_inv = np.linalg.pinv(Xd.T @ Xd)
    beta = XtX_inv @ (Xd.T @ yd)
    resid = yd - Xd @ beta
    G = len(np.unique(rid))
    N, K = len(yd), Xd.shape[1] + G
    meat = np.zeros((Xd.shape[1], Xd.shape[1]))
    for r in np.unique(rid):
        m = rid == r
        u = Xd[m].T @ resid[m]
        meat += np.outer(u, u)
    c = (G / (G - 1)) * ((N - 1) / (N - K))
    V = c * XtX_inv @ meat @ XtX_inv
    i = cols.index("p1")
    b, se = float(beta[i]), float(np.sqrt(V[i, i]))
    from scipy import stats as st
    p = 2 * (1 - st.t.cdf(abs(b / se), df=G - 1))
    return b, se, p, G


def randomization_p(d, base):
    """Exhaustive sign-flip randomization over the six city clusters (D-096).

    With G clusters there are 2^G sign assignments and, because a global flip leaves
    |t| unchanged, 2^(G-1) distinct ones. That is the whole achievable p-value grid and
    we report it rather than implying a finer one with 999 bootstrap draws.
    """
    w = d.groupby("city")["y"].transform(lambda s: len(d) / (d.city.nunique() * len(s)))
    f_full = f"y ~ {base} + C(city) + p1"
    m0 = smf.wls(f_full, d, weights=w).fit()
    t_obs = abs(m0.params["p1"] / m0.bse["p1"])
    m_r = smf.wls(f"y ~ {base} + C(city)", d, weights=w).fit()
    fitr, resr = m_r.fittedvalues.to_numpy(), m_r.resid.to_numpy()
    codes = pd.Categorical(d.city).codes
    G = d.city.nunique()
    dd = d.copy()
    ts = []
    for combo in itertools.product([-1.0, 1.0], repeat=G):
        if combo[0] < 0:                      # global flip is a duplicate
            continue
        dd["_yb"] = fitr + resr * np.array(combo)[codes]
        mb = smf.wls(f_full.replace("y ~", "_yb ~"), dd, weights=w).fit()
        ts.append(abs(mb.params["p1"] / mb.bse["p1"]))
    ts = np.array(ts)
    p = float((ts >= t_obs).sum() / len(ts))
    return m0.params["p1"], t_obs, p, len(ts)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--floor", type=float, default=MIN_LEN)
    args = ap.parse_args()
    d = load(floor=args.floor)
    base = " + ".join(CTRL) + " + C(f_system)"
    cities = sorted(d.city.unique())
    print(f"Environment: {provenance.environment_stamp()}")
    rows = []

    # ---------------------------------------------------------------- sample
    raw = pd.read_parquet(paths.DATA / "analysis__aadtfree" / f"analysis_pooled_r{R}.parquet")
    print(f"\n{'='*94}\nSAMPLE CONSTRUCTION (D-093, D-094)\n{'='*94}")
    print(f"  exogenous-frame analysis units                         {len(raw):>8,}")
    print(f"  after the {args.floor:.0f} m construct-validity floor            "
          f"{len(raw[raw.length_m >= args.floor]):>8,}")
    print(f"  after complete cases on all model variables            {len(d):>8,}")
    print(f"  cells {d.cell_id.nunique():,} | routes {d.route_id.nunique():,}")
    sh = {c: round(100 * (d.city == c).mean(), 1) for c in cities}
    print(f"  city shares: {sh}")
    print(f"  median unit length by city: "
          f"{d.groupby('city')['length_m'].median().round(0).to_dict()}")
    rows.append({"table": "sample", "n_units": len(raw),
                 "n_after_floor": len(raw[raw.length_m >= args.floor]), "n_model": len(d),
                 "cells": d.cell_id.nunique(), "routes": d.route_id.nunique(),
                 "boston_share": sh.get("boston")})

    # ---------------------------------------------------------------- per city
    print(f"\n{'='*94}\nPRIMARY — per city\n{'='*94}")
    print(f"  {'city':<16}{'n':>8}{'cells':>7}{'%P1':>7}{'β':>10}{'SE':>8}{'p':>9}"
          f"{'% AADT':>9}   95% CI")
    for c in cities:
        g = d[d.city == c]
        res = fit(g, f"y ~ {base} + p1")
        if res is None:
            continue
        b, se, p = res.params["p1"], res.bse["p1"], res.pvalues["p1"]
        print(f"  {c:<16}{len(g):>8,}{g.cell_id.nunique():>7,}{100*g.p1.mean():>6.1f}%"
              f"{b:>+10.4f}{se:>8.4f}{p:>9.4f}{100*(np.exp(b)-1):>8.1f}%   "
              f"[{b-1.96*se:+.3f}, {b+1.96*se:+.3f}]")
        rows.append({"table": "T_primary", "city": c, "n": len(g),
                     "cells": g.cell_id.nunique(), "pct_p1": 100*g.p1.mean(),
                     "beta": b, "se": se, "p": p, "pct": 100*(np.exp(b)-1),
                     "lo": b-1.96*se, "hi": b+1.96*se})
    res = fit(d, f"y ~ {base} + C(city) + p1")
    b, se, p = res.params["p1"], res.bse["p1"], res.pvalues["p1"]
    print(f"  {'pooled + city FE':<16}{len(d):>8,}{d.cell_id.nunique():>7,}{'':>7}"
          f"{b:>+10.4f}{se:>8.4f}{p:>9.4f}{100*(np.exp(b)-1):>8.1f}%")
    rows.append({"table": "T_primary", "city": "pooled + city FE", "n": len(d),
                 "beta": b, "se": se, "p": p, "pct": 100*(np.exp(b)-1)})
    bw, t_obs, p_ri, ndraw = randomization_p(d, base)
    print(f"  {'pooled, equal w.':<16}{len(d):>8,}{'':>7}{'':>7}{bw:>+10.4f}{'—':>8}"
          f"{p_ri:>9.4f}{100*(np.exp(bw)-1):>8.1f}%   randomization inference, "
          f"{ndraw} distinct assignments, |t| = {t_obs:.2f}")
    print(f"     -> the achievable p-value grid is multiples of 1/{ndraw} = {1/ndraw:.4f};"
          f" the smallest attainable p-value is {1/ndraw:.4f}")
    rows.append({"table": "T_primary", "city": "pooled, equal weights", "n": len(d),
                 "beta": bw, "p": p_ri, "n_draws": ndraw, "t": t_obs,
                 "pct": 100*(np.exp(bw)-1)})

    # ---------------------------------------------------------------- corridor FE + balance
    print(f"\n{'='*94}\nWITHIN-CORRIDOR ESTIMATES, AND WHAT THEY COMPARE\n{'='*94}")
    keep = d.groupby("route_id")["p1"].transform(lambda s: s.nunique() > 1)
    dw = d[keep].copy()
    print(f"  routes with within-route P1 variation: {dw.route_id.nunique():,} "
          f"({len(dw):,} of {len(d):,} segments)")
    print(f"  {'city':<16}{'n':>8}{'routes':>8}{'β':>10}{'SE':>8}{'p':>9}{'% AADT':>9}")
    for c in cities + ["POOLED"]:
        g = dw if c == "POOLED" else dw[dw.city == c]
        if len(g) < 100 or g.route_id.nunique() < 10:
            print(f"  {c:<16} too few — skipped"); continue
        b, se, p, nG = corridor_fe(g, CTRL + ["p1"])
        print(f"  {c:<16}{len(g):>8,}{nG:>8,}{b:>+10.4f}{se:>8.4f}"
              f"{p:>9.4f}{100*(np.exp(b)-1):>8.1f}%")
        rows.append({"table": "T_corridor", "city": c, "n": len(g),
                     "routes": nG, "beta": b, "se": se, "p": p,
                     "pct": 100*(np.exp(b)-1)})

    # THE BALANCE TABLE the panel called the deepest unresolved issue
    print(f"\n  WITHIN-CORRIDOR BALANCE — treated vs untreated stretches of the SAME route")
    print(f"  (each variable demeaned within route, so this is the contrast the estimator"
          f" actually uses)")
    print(f"  {'variable':<32}{'treated':>12}{'untreated':>12}{'diff':>11}{'std. diff':>11}")
    for v, lab in BAL.items():
        if v not in dw.columns:
            continue
        g = dw.dropna(subset=[v]).copy()
        g["_dm"] = g[v] - g.groupby("route_id")[v].transform("mean")
        t, u = g[g.p1 == 1]["_dm"], g[g.p1 == 0]["_dm"]
        pooled_sd = np.sqrt((t.var() + u.var()) / 2)
        smd = (t.mean() - u.mean()) / pooled_sd if pooled_sd > 0 else np.nan
        mt, mu = g[g.p1 == 1][v].mean(), g[g.p1 == 0][v].mean()
        print(f"  {lab:<32}{mt:>12.1f}{mu:>12.1f}{t.mean()-u.mean():>+11.2f}{smd:>+11.3f}")
        rows.append({"table": "T_balance", "variable": lab, "mean_treated": mt,
                     "mean_untreated": mu, "within_route_diff": t.mean()-u.mean(),
                     "smd_within_route": smd})
    print("  -> a standardised difference near zero means the corridor-FE contrast is not")
    print("     comparing systematically different places along the same road.")

    # ---------------------------------------------------------------- moderation
    if "betw_z" in d.columns:
        dmo = d.dropna(subset=["betw_z", "access_controlled"])
        print(f"\n{'='*94}\nMODERATION (RQ2), n = {len(dmo):,}\n{'='*94}")
        res = fit(dmo, f"y ~ {base} + C(city) + p1 + access_controlled + betw_z"
                       f" + p1:access_controlled + p1:betw_z")
        if res is not None:
            for t in ["p1", "access_controlled", "betw_z", "p1:access_controlled",
                      "p1:betw_z"]:
                print(f"  {t:<24}{res.params[t]:>+9.4f} (SE {res.bse[t]:.4f}, "
                      f"p = {res.pvalues[t]:.4f})")
                rows.append({"table": "T_moderation", "term": t, "n": len(dmo),
                             "beta": res.params[t], "se": res.bse[t],
                             "p": res.pvalues[t]})
    else:
        print("\n  !! betweenness absent — run 02c under PIPE_VARIANT=aadtfree")

    # ---------------------------------------------------------------- P1 vs P2, counts
    print(f"\n{'='*94}\nP1 AGAINST P2, COMMON PER-SD FOOTING; AND THE ROUTE-COUNT FORM"
          f"\n{'='*94}")
    dp = d.dropna(subset=["p2_z"])
    res = fit(dp, f"y ~ {base} + C(city) + p1 + p2_z")
    if res is not None:
        sd1 = dp.p1.std(ddof=0)
        e1 = 100*(np.exp(res.params["p1"]*sd1)-1)
        e2 = 100*(np.exp(res.params["p2_z"])-1)
        print(f"  P1 per SD ({sd1:.3f}) -> {e1:+.2f}% "
              f"(β {res.params['p1']:+.4f}, p = {res.pvalues['p1']:.4f})")
        print(f"  P2 per SD          -> {e2:+.2f}% "
              f"(β {res.params['p2_z']:+.4f}, p = {res.pvalues['p2_z']:.4f})")
        print("  -> a ratio is only meaningful when both are signed the same way; where "
              "P2 is\n     indistinguishable from zero we report the two coefficients "
              "and not their ratio.")
        rows.append({"table": "P1vsP2", "p1_per_sd_pct": e1, "p2_per_sd_pct": e2,
                     "beta_p1": res.params["p1"], "p_p1": res.pvalues["p1"],
                     "beta_p2": res.params["p2_z"], "p_p2": res.pvalues["p2_z"],
                     "n": len(dp)})
    res = fit(d, f"y ~ {base} + C(city) + p1n_z")
    if res is not None:
        print(f"  route-count form per SD: {res.params['p1n_z']:+.4f} "
              f"(SE {res.bse['p1n_z']:.4f}, p = {res.pvalues['p1n_z']:.4f}) -> "
              f"{100*(np.exp(res.params['p1n_z'])-1):+.2f}%")
        rows.append({"table": "P1count", "beta": res.params["p1n_z"],
                     "se": res.bse["p1n_z"], "p": res.pvalues["p1n_z"],
                     "pct": 100*(np.exp(res.params["p1n_z"])-1)})

    # ---------------------------------------------------------------- vehicles
    print(f"\n{'='*94}\nWHAT THE ESTIMATE IS WORTH IN VEHICLES (alfa 6)\n{'='*94}")
    r_pool = fit(d, f"y ~ {base} + C(city) + p1")
    bp = r_pool.params["p1"]
    print(f"  {'city':<16}{'median AADT':>13}{'β':>9}{'vehicles/day':>15}"
          f"{'over a 1-mile corridor':>24}")
    for c in cities:
        g = d[d.city == c]
        rr = fit(g, f"y ~ {base} + p1")
        if rr is None: continue
        med = g.aadt.median()
        dv = med * (np.exp(rr.params["p1"]) - 1)
        print(f"  {c:<16}{med:>13,.0f}{rr.params['p1']:>+9.3f}{dv:>15,.0f}"
              f"{dv:>+24,.0f} veh/day")
        rows.append({"table": "vehicles", "city": c, "median_aadt": med,
                     "beta": rr.params["p1"], "veh_per_day": dv})
    medall = d.aadt.median()
    dv_all = medall * (np.exp(bp) - 1)
    print(f"  {'pooled':<16}{medall:>13,.0f}{bp:>+9.3f}{dv_all:>15,.0f}")
    vpl = (d["aadt"] / d["through_lanes"].replace(0, np.nan)).median()
    print(f"\n  For scale, measured in this same sample: the median arterial carries "
          f"{vpl:,.0f}\n  vehicles per day per through lane, so the pooled estimate is "
          f"about {abs(dv_all)/vpl:.2f} of one\n  lane's worth of traffic.")
    rows.append({"table": "vehicles", "city": "pooled", "median_aadt": medall,
                 "beta": bp, "veh_per_day": dv_all, "median_aadt_per_lane": vpl,
                 "lane_equivalents": abs(dv_all)/vpl})

    out = pd.DataFrame(rows)
    fp = paths.TABLES / "primary_v2.csv"
    out.to_csv(fp, index=False)
    print(f"\n  wrote {fp.relative_to(paths.ROOT)}")
    provenance.log_progress("05x_primary_v2",
                            "revised primary frame: exogenous units, 400 m floor, "
                            "job density, randomization inference (D-093..D-096)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
