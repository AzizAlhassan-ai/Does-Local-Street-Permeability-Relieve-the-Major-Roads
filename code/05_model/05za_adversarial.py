#!/usr/bin/env python
"""Stage 5 — adversarial specifications, robust models, matched ablation (D-098).

The previous specification curve was correctly criticised as non-adversarial: thirteen
nested perturbations of one dataset, all chosen by us, agreeing in sign almost
mechanically. This adds branches designed to BREAK the result, chosen by the reviewers
rather than by us:

  * drop the two strongest cities (Denver and Portland) together
  * Boston alone — the city where the measure behaves worst
  * long segments only, in every city simultaneously
  * the exogenous frame AND corridor fixed effects AND equal city weights, jointly
  * a count model on raw AADT rather than a log-linear model on the conditional mean
  * a median (quantile) regression pooled, not only for Boston
  * a heteroskedasticity- and outlier-robust specification

It also re-runs the per-segment ablation on a matched contrast (bravo 5): the earlier
version aggregated a binary to a cell rate and standardised it, changing estimand and
scale at once, so part of the fall was mechanical.

Usage
-----
    uv run python code/05_model/05za_adversarial.py
"""
from __future__ import annotations
import argparse, pathlib, sys
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
import numpy as np, pandas as pd, statsmodels.api as sm, statsmodels.formula.api as smf
from lib import cfg, paths, provenance

R = 800
MIN_LEN = 400.0
CTRL = ["pop_density_km2_z", "job_density_km2_z", "lu_entropy_z", "dist_cbd_km_c_z",
        "dist_cbd_km_c_sq_z", "median_year_z", "through_lanes_z"]


def z(s):
    sd = s.std(ddof=0)
    return (s - s.mean()) / sd if sd and sd > 0 else s * 0.0


def load(frame="aadtfree", floor=MIN_LEN):
    suf = f"__{frame}" if frame else ""
    fp = paths.DATA / f"analysis{suf}" / f"analysis_pooled_r{R}.parquet"
    if not fp.exists():
        return None
    d = pd.read_parquet(fp)
    if floor:
        d = d[d.length_m >= floor]
    d = d.copy()
    src = {"pop_density_km2_z": "pop_density_km2", "job_density_km2_z": "job_density_km2",
           "lu_entropy_z": "lu_entropy", "dist_cbd_km_c_z": "dist_cbd_km_c",
           "dist_cbd_km_c_sq_z": "dist_cbd_km_c_sq",
           "median_year_z": "median_year_structure_built",
           "through_lanes_z": "through_lanes"}
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


def corridor_fe(g, terms, weights=None):
    """Route FE by within-transformation, cluster-robust on route.

    City weights are constant within a route (routes nest inside cities), so weighted
    and unweighted demeaning give the same absorption; only the final regression is
    weighted, which is applied here by scaling the demeaned data by sqrt(w).
    """
    X = pd.get_dummies(g[terms + ["f_system"]], columns=["f_system"],
                       drop_first=True).astype(float)
    dfm = pd.DataFrame(X); dfm["_y"] = g["y"].to_numpy(float)
    rid = g["route_id"].to_numpy(); dfm["_r"] = rid
    dm = dfm.groupby("_r").transform("mean")
    Xd = (dfm[X.columns] - dm[X.columns]).to_numpy(float)
    yd = (dfm["_y"] - dm["_y"]).to_numpy(float)
    if weights is not None:
        s = np.sqrt(np.asarray(weights, dtype=float))[:, None]
        Xd, yd = Xd * s, yd * s.ravel()
    keep = Xd.std(axis=0) > 1e-10
    Xd, cols = Xd[:, keep], list(np.array(X.columns)[keep])
    inv = np.linalg.pinv(Xd.T @ Xd)
    beta = inv @ (Xd.T @ yd); resid = yd - Xd @ beta
    G = len(np.unique(rid)); N, K = len(yd), Xd.shape[1] + G
    meat = np.zeros((Xd.shape[1],) * 2)
    for r in np.unique(rid):
        m = rid == r
        u = Xd[m].T @ resid[m]
        meat += np.outer(u, u)
    V = (G / (G - 1)) * ((N - 1) / (N - K)) * inv @ meat @ inv
    i = cols.index("p1")
    from scipy import stats as st
    b, se = float(beta[i]), float(np.sqrt(V[i, i]))
    return b, se, 2 * (1 - st.t.cdf(abs(b / se), df=G - 1)), G


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    args = ap.parse_args()
    d = load()
    base = " + ".join(CTRL) + " + C(f_system)"
    print(f"Environment: {provenance.environment_stamp()}\nprimary n = {len(d):,}")
    rows = []

    # ------------------------------------------------------------------ A
    print(f"\n{'='*100}\nA. ADVERSARIAL BRANCHES — chosen to break the result\n{'='*100}")
    print(f"  {'branch':<52}{'source':<12}{'n':>8}{'β':>10}{'SE':>8}{'p':>9}")

    def report(lab, src, d_, formula=None, kind="mixed"):
        if d_ is None or len(d_) < 400:
            print(f"  {lab:<52}{src:<12}{'—':>8}  not estimable"); return
        if kind == "mixed":
            r = fit(d_, formula or f"y ~ {base} + C(city) + p1")
            if r is None or "p1" not in r.params.index: return
            b, se, p = r.params["p1"], r.bse["p1"], r.pvalues["p1"]
        elif kind == "corridor":
            b, se, p, _ = corridor_fe(d_, CTRL + ["p1"])
        print(f"  {lab:<52}{src:<12}{len(d_):>8,}{b:>+10.4f}{se:>8.4f}{p:>9.4f}")
        rows.append({"check": "adversarial", "branch": lab, "source": src,
                     "n": len(d_), "beta": b, "se": se, "p": p,
                     "pct": 100*(np.exp(b)-1)})

    report("primary (revised frame, 400 m floor)", "—", d)
    report("drop Denver AND Portland (two strongest)", "alfa/delta",
           d[~d.city.isin(["denver", "portland"])])
    report("Boston alone", "alfa/delta", d[d.city == "boston"],
           f"y ~ {base} + p1")
    report("segments ≥ 800 m in every city", "alfa/delta", d[d.length_m >= 800])
    report("drop the three largest cities by n", "adversarial",
           d[~d.city.isin(d.city.value_counts().head(3).index)])
    report("exogenous frame + corridor FE (all cities)", "alfa/delta",
           d[d.groupby("route_id")["p1"].transform(lambda s: s.nunique() > 1)],
           kind="corridor")

    # exogenous frame + corridor FE + equal city weights, jointly
    dw = d[d.groupby("route_id")["p1"].transform(lambda s: s.nunique() > 1)].copy()
    w = dw.groupby("city")["y"].transform(lambda s: len(dw) / (dw.city.nunique()*len(s)))
    b, se, p, G = corridor_fe(dw, CTRL + ["p1"], weights=w.to_numpy())
    print(f"  {'exogenous + corridor FE + equal weights':<52}{'delta':<12}{len(dw):>8,}"
          f"{b:>+10.4f}{se:>8.4f}{p:>9.4f}")
    rows.append({"check": "adversarial", "branch": "exogenous + corridor FE + equal w.",
                 "source": "delta", "n": len(dw), "beta": b, "se": se, "p": p})

    # count model on raw AADT
    try:
        X = pd.get_dummies(d[CTRL + ["p1", "f_system", "city"]],
                           columns=["f_system", "city"], drop_first=True).astype(float)
        X = sm.add_constant(X)
        m = sm.GLM(d["aadt"].to_numpy(float), X.to_numpy(float),
                   family=sm.families.NegativeBinomial(alpha=1.0)).fit(
                       cov_type="cluster", cov_kwds={"groups": d["city"].to_numpy()})
        i = list(X.columns).index("p1")
        print(f"  {'negative binomial on raw AADT':<52}{'delta':<12}{len(d):>8,}"
              f"{m.params[i]:>+10.4f}{m.bse[i]:>8.4f}{m.pvalues[i]:>9.4f}")
        rows.append({"check": "adversarial", "branch": "negative binomial, raw AADT",
                     "source": "delta", "n": len(d), "beta": m.params[i],
                     "se": m.bse[i], "p": m.pvalues[i]})
    except Exception as e:
        print(f"  count model failed: {e}")

    # ------------------------------------------------------------------ B
    print(f"\n{'='*100}\nB. FUNCTIONAL FORM — pooled quantile profile and a robust fit "
          f"(alfa 7)\n{'='*100}")
    X = pd.get_dummies(d[CTRL + ["p1", "f_system", "city"]],
                       columns=["f_system", "city"], drop_first=True).astype(float)
    X = sm.add_constant(X); i = list(X.columns).index("p1")
    Xn, yn = X.to_numpy(float), d["y"].to_numpy(float)
    print(f"  {'quantile of AADT':<24}{'β on P1':>11}{'SE':>9}{'p':>9}")
    for q in (0.10, 0.25, 0.50, 0.75, 0.90):
        try:
            m = sm.QuantReg(yn, Xn).fit(q=q)
            print(f"  {f'q = {q:.2f}':<24}{m.params[i]:>+11.4f}{m.bse[i]:>9.4f}"
                  f"{m.pvalues[i]:>9.4f}")
            rows.append({"check": "quantile_pooled", "q": q, "beta": m.params[i],
                         "se": m.bse[i], "p": m.pvalues[i]})
        except Exception as e:
            print(f"  q = {q}: {e}")
    rlm = sm.RLM(yn, Xn, M=sm.robust.norms.HuberT()).fit()
    print(f"  {'Huber robust regression':<24}{rlm.params[i]:>+11.4f}{rlm.bse[i]:>9.4f}"
          f"{rlm.pvalues[i]:>9.4f}")
    rows.append({"check": "robust", "beta": rlm.params[i], "se": rlm.bse[i],
                 "p": rlm.pvalues[i]})
    from scipy import stats as st
    r = fit(d, f"y ~ {base} + C(city) + p1")
    print(f"  residual skewness {float(st.skew(r.resid)):+.3f}, "
          f"excess kurtosis {float(st.kurtosis(r.resid)):+.3f} "
          f"(against −1.21 / +11.8 on the old frame)")
    rows.append({"check": "residuals", "skew": float(st.skew(r.resid)),
                 "kurtosis": float(st.kurtosis(r.resid))})

    # ------------------------------------------------------------------ C
    print(f"\n{'='*100}\nC. PER-SEGMENT ABLATION ON A MATCHED CONTRAST (bravo 5)"
          f"\n{'='*100}")
    d2 = d.copy()
    d2["cellrate"] = d2.groupby("cell_id")["p1"].transform("mean")
    prev = d2.p1.mean()
    thr = d2["cellrate"].quantile(1 - prev)          # same treated share as P1 itself
    d2["cellbin"] = (d2["cellrate"] >= thr).astype(float)
    print(f"  segment-level P1 prevalence {100*prev:.1f}%; cell-rate threshold {thr:.3f} "
          f"gives {100*d2.cellbin.mean():.1f}% treated")
    for lab, term in (("segment-level P1 (0→1)", "p1"),
                      ("cell-rate, dichotomised at the same prevalence (0→1)", "cellbin")):
        r = fit(d2, f"y ~ {base} + C(city) + {term}")
        if r is None: continue
        print(f"  {lab:<52}{r.params[term]:>+10.4f} (SE {r.bse[term]:.4f}, "
              f"p = {r.pvalues[term]:.4f})")
        rows.append({"check": "ablation_matched", "spec": lab, "beta": r.params[term],
                     "se": r.bse[term], "p": r.pvalues[term]})
    r = fit(d2, f"y ~ {base} + C(city) + p1 + cellbin")
    if r is not None:
        print(f"  {'both together — segment P1':<52}{r.params['p1']:>+10.4f} "
              f"(p = {r.pvalues['p1']:.4f})")
        print(f"  {'both together — cell rate':<52}{r.params['cellbin']:>+10.4f} "
              f"(p = {r.pvalues['cellbin']:.4f})")
        rows.append({"check": "ablation_matched", "spec": "both, segment P1",
                     "beta": r.params["p1"], "p": r.pvalues["p1"]})
        rows.append({"check": "ablation_matched", "spec": "both, cell rate",
                     "beta": r.params["cellbin"], "p": r.pvalues["cellbin"]})
    print("  -> both are now 0→1 contrasts on the same sample, so the comparison is fair.")

    # ------------------------------------------------------------------ D
    print(f"\n{'='*100}\nD. THE OLD FRAME, FOR COMPARISON\n{'='*100}")
    for lab, frame, floor in (("previous primary (AADT in key, no floor)", "", 0),
                              ("previous frame + 400 m floor", "", MIN_LEN),
                              ("revised frame, no floor", "aadtfree", 0)):
        dd = load(frame, floor)
        if dd is None: continue
        r = fit(dd, f"y ~ {base} + C(city) + p1")
        if r is None: continue
        print(f"  {lab:<52}{len(dd):>8,}{r.params['p1']:>+10.4f}{r.bse['p1']:>8.4f}"
              f"{r.pvalues['p1']:>9.4f}")
        rows.append({"check": "frame_comparison", "branch": lab, "n": len(dd),
                     "beta": r.params["p1"], "se": r.bse["p1"], "p": r.pvalues["p1"]})

    out = pd.DataFrame(rows)
    fp = paths.TABLES / "adversarial_v2.csv"
    out.to_csv(fp, index=False)
    print(f"\n  wrote {fp.relative_to(paths.ROOT)}")
    provenance.log_progress("05za_adversarial",
                            "adversarial branches, robust forms, matched ablation (D-098)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
