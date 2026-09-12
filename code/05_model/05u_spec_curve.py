#!/usr/bin/env python
"""Stage 5 — specification curve, sweep balance, dose–response, one-way fit (D-090).

A. SPECIFICATION CURVE (bravo M2)
   The pooled estimate moves by a factor of seven across defensible branches, and the
   abstract quoted a range from one of them. This enumerates the branches — control
   set, sample rule, weighting, unit definition, identification — and reports the whole
   distribution, so the range in the abstract can be the range across it.

B. SWEEP BALANCE (charlie M3)
   Tightening the endpoint radius more than doubles the coefficient. That is read in
   the paper as mechanism confirmation, but monotone strengthening under an
   increasingly selective treatment definition is equally the signature of selection on
   fabric type. The discriminating evidence is the size and covariate profile of the
   treated group at each sweep level, which was never reported.

C. DOSE–RESPONSE (alfa M4)
   "Effect size tracks available substitutability" is a six-point post-hoc pattern with
   two inversions. The proper test is within-city dose–response on the continuous
   route-count form, which the pipeline already computes.

D. ONE-WAY SENSITIVITY (alfa m2)
   Requires PIPE_VARIANT=oneway through 02a..03c first.

Usage
-----
    uv run python code/05_model/05u_spec_curve.py
"""
from __future__ import annotations
import argparse, pathlib, sys
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
import numpy as np, pandas as pd, statsmodels.formula.api as smf
from lib import cfg, paths, provenance

CTRL = ["pop_density_km2_z", "lu_entropy_z", "dist_cbd_km_c_z",
        "dist_cbd_km_c_sq_z", "median_year_z", "through_lanes_z"]
CTRL_NOLANE = [c for c in CTRL if c != "through_lanes_z"]
R = 800


def z(s):
    sd = s.std(ddof=0)
    return (s - s.mean()) / sd if sd and sd > 0 else s * 0.0


def prep(d):
    d = d.copy()
    src = {"pop_density_km2_z": "pop_density_km2", "lu_entropy_z": "lu_entropy",
           "dist_cbd_km_c_z": "dist_cbd_km_c", "dist_cbd_km_c_sq_z": "dist_cbd_km_c_sq",
           "median_year_z": "median_year_structure_built",
           "through_lanes_z": "through_lanes"}
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


def load(variant, r=R):
    suf = f"__{variant}" if variant else ""
    fp = paths.DATA / f"analysis{suf}" / f"analysis_pooled_r{r}.parquet"
    return prep(pd.read_parquet(fp)) if fp.exists() else None


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    args = ap.parse_args()
    d = load("")
    base = " + ".join(CTRL) + " + C(f_system)"
    print(f"Environment: {provenance.environment_stamp()}\nn = {len(d):,}")
    rows = []

    # ------------------------------------------------------------------ A
    print(f"\n{'='*100}\nA. SPECIFICATION CURVE — every defensible branch\n{'='*100}")
    specs = []

    def add(label, family, d_, formula, weights=None, cluster=None):
        specs.append((label, family, d_, formula, weights, cluster))

    add("primary (full controls, city FE)", "controls", d,
        f"y ~ {base} + C(city) + p1")
    add("drop through lanes (post-treatment)", "controls", d,
        " + ".join(CTRL_NOLANE) + " + C(f_system) + C(city) + p1")
    add("drop lanes and functional class", "controls", d,
        "y ~ " + " + ".join(CTRL_NOLANE) + " + C(city) + p1")
    add("add log segment length", "controls", d,
        f"y ~ {base} + C(city) + loglen_z + p1")
    add("controls only, no city FE", "controls", d, f"y ~ {base} + p1")
    elig = pd.concat([pd.read_parquet(paths.processed(c) / "cell_metrics.parquet")
                      .assign(cell_id=lambda t, c=c: c + "|" + t["cell_id"].astype(str))
                      [["cell_id", "ce_eligible"]] for c in cfg.cities()],
                     ignore_index=True)
    d_ce = d.merge(elig, on="cell_id", how="left")
    d_ce = d_ce[d_ce["ce_eligible"].fillna(False)]
    add("Choi–Ewing-eligible cells only", "sample", d_ce, f"y ~ {base} + C(city) + p1")
    add("segments ≥ 500 m", "sample", d[d.length_m >= 500],
        f"y ~ {base} + C(city) + p1")
    add("excluding Boston", "sample", d[d.city != "boston"],
        f"y ~ {base} + C(city) + p1")
    add("excluding Charlotte", "sample", d[d.city != "charlotte"],
        f"y ~ {base} + C(city) + p1")

    print(f"  {'specification':<40}{'family':<12}{'n':>8}{'β':>10}{'SE':>9}{'p':>9}"
          f"{'% AADT':>9}")
    for label, family, d_, formula, w, cl in specs:
        if d_ is None or len(d_) < 500:
            continue
        f_ = formula if formula.startswith("y ~") else "y ~ " + formula
        res = fit(d_, f_)
        if res is None or "p1" not in res.params.index:
            continue
        b, se, p = res.params["p1"], res.bse["p1"], res.pvalues["p1"]
        print(f"  {label:<40}{family:<12}{len(d_):>8,}{b:>+10.4f}{se:>9.4f}{p:>9.4f}"
              f"{100*(np.exp(b)-1):>8.1f}%")
        rows.append({"check": "spec_curve", "spec": label, "family": family,
                     "n": len(d_), "beta": b, "se": se, "p": p,
                     "pct": 100*(np.exp(b)-1)})

    # weighting and identification branches, estimated differently
    w = d.groupby("city")["y"].transform(lambda s: len(d) / (d.city.nunique() * len(s)))
    m = smf.wls(f"y ~ {base} + C(city) + p1", d, weights=w).fit()
    print(f"  {'equal city weights':<40}{'weighting':<12}{len(d):>8,}"
          f"{m.params['p1']:>+10.4f}{m.bse['p1']:>9.4f}{'—':>9}"
          f"{100*(np.exp(m.params['p1'])-1):>8.1f}%")
    rows.append({"check": "spec_curve", "spec": "equal city weights",
                 "family": "weighting", "n": len(d), "beta": m.params["p1"],
                 "se": m.bse["p1"], "pct": 100*(np.exp(m.params["p1"])-1)})

    keep = d.groupby("route_id")["p1"].transform(lambda s: s.nunique() > 1)
    dw = d[keep]
    mfe = smf.ols(f"y ~ {base} + C(route_id) + p1", dw).fit(
        cov_type="cluster", cov_kwds={"groups": dw["route_id"]})
    print(f"  {'corridor fixed effects':<40}{'identif.':<12}{len(dw):>8,}"
          f"{mfe.params['p1']:>+10.4f}{mfe.bse['p1']:>9.4f}{mfe.pvalues['p1']:>9.4f}"
          f"{100*(np.exp(mfe.params['p1'])-1):>8.1f}%")
    rows.append({"check": "spec_curve", "spec": "corridor fixed effects",
                 "family": "identification", "n": len(dw), "beta": mfe.params["p1"],
                 "se": mfe.bse["p1"], "p": mfe.pvalues["p1"],
                 "pct": 100*(np.exp(mfe.params["p1"])-1)})

    for lab, var in (("AADT-free units", "aadtfree"), ("one-way admitted", "oneway")):
        dv_ = load(var)
        if dv_ is None:
            print(f"  {lab}: variant not built — skipped")
            continue
        res = fit(dv_, f"y ~ {base} + C(city) + p1")
        if res is None:
            continue
        b, se, p = res.params["p1"], res.bse["p1"], res.pvalues["p1"]
        print(f"  {lab:<40}{'unit/frame':<12}{len(dv_):>8,}{b:>+10.4f}{se:>9.4f}"
              f"{p:>9.4f}{100*(np.exp(b)-1):>8.1f}%")
        rows.append({"check": "spec_curve", "spec": lab, "family": "unit/frame",
                     "n": len(dv_), "beta": b, "se": se, "p": p,
                     "pct": 100*(np.exp(b)-1)})

    cur = pd.DataFrame([r for r in rows if r["check"] == "spec_curve"])
    print(f"\n  {len(cur)} branches: median β = {cur.beta.median():+.4f}, "
          f"range {cur.beta.min():+.4f} to {cur.beta.max():+.4f}; "
          f"{int((cur.beta < 0).sum())}/{len(cur)} negative")

    # ------------------------------------------------------------------ B
    print(f"\n{'='*100}\nB. TREATED-GROUP SIZE AND BALANCE AT EACH SWEEP LEVEL\n{'='*100}")
    sw = paths.TABLES / f"p1_constants_sweep_r{R}.csv"
    bal_vars = ["pop_density_km2", "lu_entropy", "dist_cbd_km_c", "length_m",
                "local_int_density", "through_lanes"]
    # rebuild the treated indicator at each endpoint radius from the sweep outputs if
    # present; otherwise report balance for the primary definition only.
    print(f"  {'definition':<26}{'N treated':>11}{'% treated':>11}   "
          + "".join(f"{v[:12]:>13}" for v in bal_vars))
    print("  (standardised difference, treated minus untreated, per variable)")
    for lab, mask in (("primary (P1 = 1)", d.p1 == 1),):
        t, u = d[mask], d[~mask]
        sds = []
        for v in bal_vars:
            if v not in d.columns:
                sds.append(np.nan); continue
            s = np.sqrt((t[v].var() + u[v].var()) / 2)
            sds.append((t[v].mean() - u[v].mean()) / s if s > 0 else np.nan)
        print(f"  {lab:<26}{len(t):>11,}{100*len(t)/len(d):>10.1f}%   "
              + "".join(f"{x:>+13.3f}" for x in sds))
        rows.append({"check": "balance", "definition": lab, "n_treated": len(t),
                     **{f"smd_{v}": s for v, s in zip(bal_vars, sds)}})
    for var, lab in (("ar100", "endpoint radius 100 m"),
                     ("ar300", "endpoint radius 300 m"),
                     ("ablall", "route may use major roads"),
                     ("ablnocap", "no detour cap")):
        parts = []
        for c in cfg.cities():
            fp = paths.PROCESSED / f"{c}__{var}" / f"through_routes_r{R}.parquet"
            if fp.exists():
                t = pd.read_parquet(fp)[["segment_uid", "p1_any"]]
                t["segment_uid"] = c + "|" + t["segment_uid"].astype(str)
                parts.append(t.rename(columns={"p1_any": "_alt"}))
        if not parts:
            continue
        alt = pd.concat(parts, ignore_index=True)
        dd = d.drop(columns=["_alt"], errors="ignore").merge(alt, on="segment_uid",
                                                            how="inner")
        tt, uu = dd[dd._alt == 1], dd[dd._alt != 1]
        sds = []
        for v in bal_vars:
            s = np.sqrt((tt[v].var() + uu[v].var()) / 2)
            sds.append((tt[v].mean() - uu[v].mean()) / s if s > 0 else np.nan)
        print(f"  {lab:<26}{len(tt):>11,}{100*len(tt)/len(dd):>10.1f}%   "
              + "".join(f"{x:>+13.3f}" for x in sds))
        rows.append({"check": "balance", "definition": lab, "n_treated": len(tt),
                     "pct_treated": 100*len(tt)/len(dd),
                     **{f"smd_{v}": s for v, s in zip(bal_vars, sds)}})

    # ------------------------------------------------------------------ C
    print(f"\n{'='*100}\nC. WITHIN-CITY DOSE–RESPONSE on the continuous route count\n{'='*100}")
    print(f"  {'city':<16}{'%P1':>7}{'β per route':>14}{'SE':>9}{'p':>9}"
          f"{'β (binary)':>13}")
    dose = []
    for c, g in d.groupby("city"):
        g = g.copy()
        g["nroutes"] = g["p1_routes"].astype(float)
        rr = fit(g, f"y ~ {base} + nroutes")
        rb = fit(g, f"y ~ {base} + p1")
        if rr is None or rb is None:
            continue
        b, se, p = rr.params["nroutes"], rr.bse["nroutes"], rr.pvalues["nroutes"]
        print(f"  {c:<16}{100*g.p1.mean():>6.1f}%{b:>+14.4f}{se:>9.4f}{p:>9.4f}"
              f"{rb.params['p1']:>+13.4f}")
        dose.append((100*g.p1.mean(), rb.params["p1"]))
        rows.append({"check": "dose", "city": c, "beta_count": b, "se": se, "p": p,
                     "beta_binary": rb.params["p1"], "pct_p1": 100*g.p1.mean()})
    if len(dose) > 3:
        pv, bv = zip(*dose)
        from scipy import stats as st
        rho, pr = st.spearmanr(pv, bv)
        print(f"\n  across cities, Spearman(prevalence, binary β) = {rho:+.3f} "
              f"(p = {pr:.3f}, n = {len(dose)}) — a six-point rank correlation, "
              f"reported as an observation")
        rows.append({"check": "dose_across_cities", "spearman": rho, "p": pr,
                     "n": len(dose)})

    out = pd.DataFrame(rows)
    fp = paths.TABLES / "spec_curve.csv"
    out.to_csv(fp, index=False)
    print(f"\n  wrote {fp.relative_to(paths.ROOT)}")
    provenance.log_progress("05u_spec_curve",
                            "specification curve, sweep balance, dose–response (D-090)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
