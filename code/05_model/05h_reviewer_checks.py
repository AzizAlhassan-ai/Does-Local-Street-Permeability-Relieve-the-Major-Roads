#!/usr/bin/env python
"""Stage 5 — checks requested by the pre-submission review panel (D-076).

Each block below answers a specific reviewer concern. Nothing here changes the
primary specification; every result is an additional column, bracket, or bound
reported alongside it.

  A. lanes/class bracket        the post-treatment argument the paper applies to
                                Choi & Ewing applies to our own models too
  B. segment length             the dissolve places unit boundaries where AADT
                                changes, so length is outcome-dependent: report
                                correlations, add a length control, length-decile FE
  C. full P3 horse race         the null currently rests on intersection density
                                alone; run all five P3 metrics + a PCA composite,
                                and report an equivalence bound rather than "nothing"
  D. common-footing effects     P1 is binary, P2/P3 z-scored — the "six times larger"
                                comparison is not scale-invariant. Re-express every
                                predictor per one standard deviation of itself.
  E. variance decomposition     a binary at 6-21% prevalence cannot explain much
                                variance by construction; redo with the count form
  F. moderation diagnostics     2x2 cell counts behind the access-control interaction,
                                and a coarsened (tercile) betweenness moderator against
                                the attenuation objection
  G. corridor fixed effects     route-level FE absorb corridor-scale demand confounds
  H. sample composition         pooled without Boston; missingness by city

Usage
-----
    uv run python code/05_model/05h_reviewer_checks.py
"""

from __future__ import annotations

import argparse
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

import numpy as np
import pandas as pd
import statsmodels.formula.api as smf

from lib import cfg, paths, provenance

CTRL = ["pop_density_km2_z", "lu_entropy_z", "dist_cbd_km_c_z",
        "dist_cbd_km_c_sq_z", "median_year_z", "through_lanes_z"]
CTRL_NO_LANES = [c for c in CTRL if c != "through_lanes_z"]

P3_METRICS = {
    "local_int_density": "intersection density",
    "local_link_node_ratio": "link–node ratio",
    "local_street_density": "street density",
    "local_deadend_share": "dead-end share",
    "local_circuity": "circuity",
}


def z(s):
    sd = s.std(ddof=0)
    return (s - s.mean()) / sd if sd and sd > 0 else s * 0.0


def prep(d, within_city=True):
    """Same standardisation as 05c, plus the P3 battery and length terms."""
    d = d.copy()
    d["access_controlled"] = d["access_control_"].isin([1, 2]).astype(float)
    d["betweenness_log"] = np.log10(d["arterial_betweenness"] + 1e-5)
    d["log_length"] = np.log(d["length_m"].clip(lower=1))
    src = {"pop_density_km2_z": "pop_density_km2", "lu_entropy_z": "lu_entropy",
           "dist_cbd_km_c_z": "dist_cbd_km_c", "dist_cbd_km_c_sq_z": "dist_cbd_km_c_sq",
           "median_year_z": "median_year_structure_built",
           "through_lanes_z": "through_lanes", "gen_z": "local_int_density",
           "betw_z": "betweenness_log", "loglen_z": "log_length",
           "p2_z": "p2_pairs_per_km2", "p1n_z": "p1_routes"}
    for m in P3_METRICS:
        src[f"{m}_z"] = m
    grp = d.groupby("city") if (within_city and "city" in d.columns) else None
    for dst, s in src.items():
        d[dst] = grp[s].transform(z) if grp is not None else z(d[s])
    d["p1"] = d["p1_any"].astype(float)
    d["y"] = d["log_aadt"]
    need = ["y", "p1", "gen_z", "betw_z", "access_controlled", "cell_id",
            "route_id", "f_system", "loglen_z"] + CTRL
    return d.dropna(subset=need).copy()


def fit(d, formula, groups):
    try:
        return smf.mixedlm(formula, d, groups=groups).fit(method="lbfgs", reml=True)
    except Exception as e:
        print(f"    !! fit failed: {e}")
        return None


def coef(res, term):
    if res is None or term not in res.params.index:
        return (np.nan,) * 3
    return res.params[term], res.bse[term], res.pvalues[term]


def pct(b):
    return 100 * (np.exp(b) - 1)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--radius", type=int, default=None)
    args = ap.parse_args()
    conf = cfg.config()
    r = args.radius or conf["catchment"]["primary_radius_m"]
    fp = paths.ANALYSIS / f"analysis_pooled_r{r}.parquet"
    if not fp.exists():
        print(f"ERROR: {fp} missing — run 03c_pool_cities.py")
        return 1

    print(f"Environment: {provenance.environment_stamp()}")
    raw = pd.read_parquet(fp)
    d = prep(raw)
    base = " + ".join(CTRL) + " + C(f_system)"
    base_nl = " + ".join(CTRL_NO_LANES)          # no lanes, no functional class
    cities = sorted(d.city.unique())
    print(f"\nPooled r={r} m: {len(d):,} units, {len(cities)} cities, "
          f"{d.cell_id.nunique():,} cells")
    rows = []

    # ---------------------------------------------------------------- A
    print(f"\n{'='*78}\nA. LANES / FUNCTIONAL-CLASS BRACKET (reviewer: post-treatment)\n{'='*78}")
    print("   If a connected network reduces the need for wide arterials, lanes and")
    print("   functional class lie on the causal path; conditioning on them biases")
    print("   toward zero. The two columns bracket the effect.")
    print("   Three specifications: (1) primary; (2) lanes dropped, class kept —")
    print("   the defensible post-treatment bracket; (3) both dropped — an outer")
    print("   bound only, since functional class is also a confounder (collectors")
    print("   carry little traffic AND are highly substitutable).")
    print(f"\n  {'city':<15}{'(1) primary':>18}{'(2) no lanes':>18}{'(3) neither':>18}")
    for c in cities + ["POOLED"]:
        g = d if c == "POOLED" else d[d.city == c]
        fe = " + C(city)" if c == "POOLED" else ""
        f1 = f"y ~ {base} + p1" + fe
        f2 = f"y ~ {' + '.join(CTRL_NO_LANES)} + C(f_system) + p1" + fe
        f3 = f"y ~ {base_nl} + p1" + fe
        b1, s1, p1_ = coef(fit(g, f1, g["cell_id"]), "p1")
        b2, s2, p2_ = coef(fit(g, f2, g["cell_id"]), "p1")
        b3, s3, p3_ = coef(fit(g, f3, g["cell_id"]), "p1")
        rows.append({"check": "lanes_bracket", "city": c,
                     "beta_primary": b1, "se_primary": s1, "p_primary": p1_,
                     "beta_nolanes": b2, "se_nolanes": s2, "p_nolanes": p2_,
                     "beta_neither": b3, "se_neither": s3, "p_neither": p3_,
                     "pct_primary": pct(b1), "pct_nolanes": pct(b2),
                     "pct_neither": pct(b3)})
        print(f"  {c:<15}{b1:>10.4f} ({pct(b1):>5.1f}%){b2:>10.4f} ({pct(b2):>5.1f}%)"
              f"{b3:>10.4f} ({pct(b3):>5.1f}%)")

    # ---------------------------------------------------------------- B
    print(f"\n{'='*78}\nB. SEGMENT LENGTH (reviewer: the unit is built from the outcome)\n{'='*78}")
    print(f"  {'city':<15}{'r(P1,len)':>11}{'r(len,logAADT)':>16}{'median len':>12}"
          f"{'β base':>10}{'β +len':>10}{'β lenFE':>10}")
    for c in cities:
        g = d[d.city == c].copy()
        r_p1 = g[["p1", "log_length"]].corr().iloc[0, 1]
        r_len = g[["log_length", "y"]].corr().iloc[0, 1]
        b0, *_ = coef(fit(g, f"y ~ {base} + p1", g["cell_id"]), "p1")
        b1, *_ = coef(fit(g, f"y ~ {base} + loglen_z + p1", g["cell_id"]), "p1")
        g["lendec"] = pd.qcut(g["length_m"], 10, labels=False, duplicates="drop")
        b2, *_ = coef(fit(g, f"y ~ {base} + C(lendec) + p1", g["cell_id"]), "p1")
        rows.append({"check": "length", "city": c, "corr_p1_len": r_p1,
                     "corr_len_aadt": r_len, "median_len_m": g.length_m.median(),
                     "beta_base": b0, "beta_lenctrl": b1, "beta_lenFE": b2})
        print(f"  {c:<15}{r_p1:>+11.3f}{r_len:>+16.3f}{g.length_m.median():>12.0f}"
              f"{b0:>10.4f}{b1:>10.4f}{b2:>10.4f}")

    # ---------------------------------------------------------------- C
    print(f"\n{'='*78}\nC. FULL P3 BATTERY + EQUIVALENCE BOUND (reviewer: horse race is partial)\n{'='*78}")
    # PCA composite over the five catchment P3 metrics (within-city z-scored)
    M = [f"{m}_z" for m in P3_METRICS]
    ok = d[M].notna().all(axis=1)
    Xc = d.loc[ok, M].values.astype(float)
    Xc = Xc - Xc.mean(axis=0)
    C_ = np.cov(Xc, rowvar=False)
    w, v = np.linalg.eigh(C_)
    pc = v[:, np.argmax(w)]
    if pc[M.index("local_int_density_z")] < 0:
        pc = -pc
    d["p3_pca"] = np.nan
    d.loc[ok, "p3_pca"] = Xc @ pc
    d["p3_pca"] = z(d["p3_pca"])
    print(f"  PCA on {int(ok.sum()):,} complete-case segments "
          f"({100*ok.mean():.1f}% of the sample)")
    print(f"  PCA loadings: " + ", ".join(
        f"{m.replace('_z','')}={pc[i]:+.2f}" for i, m in enumerate(M)))
    print(f"\n  {'P3 metric':<24}{'alone':>22}{'| controlling for P1':>28}")
    print(f"  {'':<24}{'β':>9}{'p':>8}{'':>5}{'β':>9}{'p':>8}{'95% CI on β|P1':>22}")
    for m, lab in list(P3_METRICS.items()) + [("p3_pca", "PCA composite")]:
        t = f"{m}_z" if m != "p3_pca" else "p3_pca"
        dm = d.dropna(subset=[t])          # groups must match the model rows
        ba, _, pa = coef(fit(dm, f"y ~ {base} + C(city) + {t}", dm["cell_id"]), t)
        bb, sb, pb = coef(fit(dm, f"y ~ {base} + C(city) + p1 + {t}", dm["cell_id"]), t)
        lo, hi = bb - 1.96 * sb, bb + 1.96 * sb
        rows.append({"check": "p3_battery", "metric": lab, "n": len(dm),
                     "beta_alone": ba,
                     "p_alone": pa, "beta_given_p1": bb, "se_given_p1": sb,
                     "p_given_p1": pb, "ci_lo": lo, "ci_hi": hi,
                     "pct_lo": pct(lo), "pct_hi": pct(hi)})
        print(f"  {lab:<24}{ba:>+9.4f}{pa:>8.3f}{'':>5}{bb:>+9.4f}{pb:>8.3f}"
              f"   [{pct(lo):+.2f}%, {pct(hi):+.2f}%]")
    print("\n  -> read the CI as an equivalence bound: the most negative AADT effect")
    print("     per SD that the data can still support, once P1 is controlled.")

    # ---------------------------------------------------------------- D
    print(f"\n{'='*78}\nD. EFFECTS ON A COMMON FOOTING (reviewer: binary vs z-scored)\n{'='*78}")
    prev = d.p1.mean()
    sd_p1 = np.sqrt(prev * (1 - prev))
    res = fit(d, f"y ~ {base} + C(city) + p1 + p2_z", d["cell_id"])
    b_p1, _, _ = coef(res, "p1")
    b_p2, _, p_p2 = coef(res, "p2_z")
    res3 = fit(d, f"y ~ {base} + C(city) + p1 + gen_z", d["cell_id"])
    b_p3, _, p_p3 = coef(res3, "gen_z")
    print(f"  P1 prevalence {prev:.3f} -> SD(P1) = {sd_p1:.3f}")
    print(f"  {'predictor':<34}{'β (own units)':>16}{'β per 1 SD':>14}{'% AADT / SD':>14}")
    for lab, b, sd in (("P1 substitutability (binary)", b_p1, sd_p1),
                       ("P2 access connections (z)", b_p2, 1.0),
                       ("P3 intersection density (z)", b_p3, 1.0)):
        print(f"  {lab:<34}{b:>+16.4f}{b*sd:>+14.4f}{pct(b*sd):>+13.2f}%")
        rows.append({"check": "common_footing", "predictor": lab, "beta_raw": b,
                     "beta_per_sd": b * sd, "pct_per_sd": pct(b * sd)})
    ratio = (b_p1 * sd_p1) / (b_p2 * 1.0) if b_p2 else np.nan
    print(f"\n  P1:P2 ratio on a per-SD footing: {ratio:.2f}x "
          f"(the raw-coefficient ratio {b_p1/b_p2 if b_p2 else np.nan:.2f}x is not "
          f"scale-invariant and should not be reported)")

    # ---------------------------------------------------------------- E
    print(f"\n{'='*78}\nE. VARIANCE DECOMPOSITION, COUNT FORM (reviewer: binary is handicapped)\n{'='*78}")

    def r2(formula):
        m = smf.ols(formula, d).fit()
        return m.rsquared

    ctrl_block = " + ".join(CTRL) + " + C(city)"
    base_r2 = r2(f"y ~ C(f_system) + C(city)")
    for lab, term in (("P1 binary", "p1"), ("P1 route count (z)", "p1n_z")):
        full = r2(f"y ~ {ctrl_block} + C(f_system) + {term}")
        no_cfg = r2(f"y ~ {ctrl_block} + C(f_system)")
        cfg_only = r2(f"y ~ C(f_system) + C(city) + {term}")
        uniq_cfg = full - no_cfg
        uniq_ctrl = full - cfg_only
        print(f"  {lab:<22} unique config R² {uniq_cfg:.4f} "
              f"({100*uniq_cfg/full:.2f}% of explained) | unique density/land use "
              f"{uniq_ctrl:.4f} ({100*uniq_ctrl/full:.2f}%) | ratio "
              f"{uniq_ctrl/uniq_cfg if uniq_cfg else np.nan:.1f}x")
        rows.append({"check": "variance", "form": lab, "r2_full": full,
                     "unique_config": uniq_cfg, "unique_controls": uniq_ctrl,
                     "ratio": uniq_ctrl / uniq_cfg if uniq_cfg else np.nan})
    print(f"  (functional class + city alone: R² = {base_r2:.4f})")

    # ---------------------------------------------------------------- F
    print(f"\n{'='*78}\nF. MODERATION DIAGNOSTICS\n{'='*78}")
    ct = pd.crosstab(d.access_controlled, d.p1)
    print("  2x2 counts behind the access-control interaction:")
    print(f"    {'':<22}{'P1 = 0':>10}{'P1 = 1':>10}{'% P1':>9}")
    for lvl, lab in ((0.0, "no access control"), (1.0, "access-controlled")):
        n0 = int(ct.loc[lvl, 0.0]) if lvl in ct.index else 0
        n1 = int(ct.loc[lvl, 1.0]) if (lvl in ct.index and 1.0 in ct.columns) else 0
        print(f"    {lab:<22}{n0:>10,}{n1:>10,}{100*n1/(n0+n1):>8.1f}%")
        rows.append({"check": "2x2", "group": lab, "n_p1_0": n0, "n_p1_1": n1})
    # coarsened moderator
    d["betw_tercile"] = d.groupby("city")["betw_z"].transform(
        lambda s: pd.qcut(s, 3, labels=False, duplicates="drop"))
    res_t = fit(d, f"y ~ {base} + C(city) + p1 * C(betw_tercile) + access_controlled"
                   f" + p1:access_controlled", d["cell_id"])
    print("\n  Betweenness moderation, coarsened to terciles (attenuation check):")
    if res_t is not None:
        for t in [x for x in res_t.params.index if "betw_tercile" in x and "p1:" in x]:
            b, s, p = coef(res_t, t)
            print(f"    {t:<42}{b:>+9.4f} (SE {s:.4f}, p = {p:.3f})")
            rows.append({"check": "betw_tercile", "term": t, "beta": b, "se": s, "p": p})
        b, s, p = coef(res_t, "p1:access_controlled")
        print(f"    {'p1:access_controlled':<42}{b:>+9.4f} (SE {s:.4f}, p = {p:.4f})")

    # ---------------------------------------------------------------- G
    print(f"\n{'='*78}\nG. CORRIDOR (ROUTE) FIXED EFFECTS\n{'='*78}")
    print("  Absorbs corridor-scale demand: identification is now WITHIN a named route,")
    print("  comparing stretches of the same arterial that differ in substitutability.")
    keep = d.groupby("route_id")["p1"].transform(lambda s: s.nunique() > 1)
    dw = d[keep].copy()
    print(f"  routes with within-route P1 variation: {dw.route_id.nunique():,} "
          f"({len(dw):,} of {len(d):,} segments)")
    for c in cities + ["POOLED"]:
        g = dw if c == "POOLED" else dw[dw.city == c]
        if len(g) < 100 or g.route_id.nunique() < 10:
            print(f"  {c:<15} too few — skipped")
            continue
        m = smf.ols(f"y ~ {base} + C(route_id) + p1", g).fit(
            cov_type="cluster", cov_kwds={"groups": g["route_id"]})
        b, s, p = m.params["p1"], m.bse["p1"], m.pvalues["p1"]
        rows.append({"check": "route_fe", "city": c, "n": len(g),
                     "n_routes": g.route_id.nunique(), "beta": b, "se": s, "p": p})
        print(f"  {c:<15}n={len(g):>7,} routes={g.route_id.nunique():>5,}"
              f"  β={b:>+8.4f} (SE {s:.4f}, p={p:.4f})  {pct(b):>6.1f}%")

    # ---------------------------------------------------------------- H
    print(f"\n{'='*78}\nH. SAMPLE COMPOSITION\n{'='*78}")
    dnb = d[d.city != "boston"]
    for lab, g, w in (("pooled, all cities (unweighted)", d, None),
                      ("pooled, excluding Boston", dnb, None)):
        res_ = fit(g, f"y ~ {base} + C(city) + p1", g["cell_id"])
        b, s, p = coef(res_, "p1")
        print(f"  {lab:<34}n={len(g):>7,}  β={b:>+8.4f} (SE {s:.4f})  {pct(b):>6.1f}%")
        rows.append({"check": "composition", "spec": lab, "n": len(g),
                     "beta": b, "se": s, "p": p, "pct": pct(b)})
    ww = d.groupby("city")["y"].transform(lambda s: len(d) / (d.city.nunique() * len(s)))
    ols_w = smf.wls(f"y ~ {base} + C(city) + p1", d, weights=ww).fit(
        cov_type="cluster", cov_kwds={"groups": d["city"]})
    print(f"  {'pooled, equal city weights':<34}n={len(d):>7,}  "
          f"β={ols_w.params['p1']:>+8.4f} (SE {ols_w.bse['p1']:.4f})  "
          f"{pct(ols_w.params['p1']):>6.1f}%")
    rows.append({"check": "composition", "spec": "pooled, equal city weights",
                 "n": len(d), "beta": ols_w.params["p1"], "se": ols_w.bse["p1"],
                 "pct": pct(ols_w.params["p1"])})

    print("\n  Missingness (rows dropped from the analysis table by city):")
    tot = raw.groupby("city").size()
    used = d.groupby("city").size()
    for c in cities:
        print(f"    {c:<16}{used.get(c,0):>7,} of {tot.get(c,0):>7,} "
              f"({100*used.get(c,0)/tot.get(c,1):>5.1f}% complete)")
        rows.append({"check": "missingness", "city": c, "n_used": int(used.get(c, 0)),
                     "n_total": int(tot.get(c, 0))})

    out = pd.DataFrame(rows)
    fpo = paths.TABLES / f"reviewer_checks_r{r}.csv"
    out.to_csv(fpo, index=False)
    print(f"\n  wrote {fpo.relative_to(paths.ROOT)}")
    provenance.log_progress("05h_reviewer_checks",
                            f"panel-requested checks at r={r} m, {len(cities)} cities")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
