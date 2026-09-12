#!/usr/bin/env python
"""Stage 4a — the core models: M0 (variance components) through M3 (H2 moderation).

Model ladder (PLAN.md §4). The Denver pilot has no city level, so this is two-level:
analysis units nested in 1 mi² cells (D-014, D-028).

  M0  log_aadt ~ 1 + (1|cell)                                   -> ICC
  M1  + controls                                                 RQ3 baseline
  M2  + local_int_density                                        H1
  M3  + access_control + betweenness + interactions              H2

Preregistration discipline: the outcome (D-004), controls (D-006/D-029), centrality
parameterisation (D-027/D-030) and moderators (D-018) were all fixed in the decisions
log BEFORE any model was fitted. Nothing here is chosen after seeing a coefficient.

Usage
-----
    uv run python code/05_model/05a_multilevel.py --city denver
    uv run python code/05_model/05a_multilevel.py --city denver --outcome aadt_per_lane

Outputs
-------
    outputs/models/m0..m3_<outcome>_r<R>.txt
    outputs/tables/model_ladder_<outcome>_r<R>.csv
"""

from __future__ import annotations

import argparse
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

import numpy as np
import pandas as pd
import statsmodels.api as sm
import statsmodels.formula.api as smf

from lib import cfg, paths, provenance, validate

PRED_COL_Z = "p1_z"      # set from --predictor in main()

CTRL_TERMS = [
    "pop_density_km2_z", "lu_entropy_z", "dist_cbd_km_c_z", "dist_cbd_km_c_sq_z",
    "median_year_z", "through_lanes_z", "C(f_system)",
]


def z(s: pd.Series) -> pd.Series:
    sd = s.std(ddof=0)
    return (s - s.mean()) / sd if sd and sd > 0 else s * 0.0


def prep(t: pd.DataFrame, outcome: str) -> tuple[pd.DataFrame, list[str]]:
    d = t.copy()

    # D-018 moderator (a): access control. Codes 1 (full, n=2) and 2 (partial) are
    # collapsed — n=2 cannot support its own level, and the substantive contrast H2
    # needs is "does this arterial control access at all" vs "no control".
    d["access_controlled"] = (d["access_control_"].isin([1, 2])).astype(float)

    # D-031: betweenness is extremely right-skewed (median ~1.1e-3, max ~1.2e-1), so
    # it enters log10-transformed before standardising. An untransformed moderator
    # would let a handful of freeway-adjacent segments drive the whole interaction.
    bt = d["arterial_betweenness"]
    d["betweenness_log"] = np.log10(bt + 1e-5)

    d["pop_density_km2_z"] = z(d["pop_density_km2"])
    d["lu_entropy_z"] = z(d["lu_entropy"])
    d["dist_cbd_km_c_z"] = z(d["dist_cbd_km_c"])
    d["dist_cbd_km_c_sq_z"] = z(d["dist_cbd_km_c_sq"])
    d["median_year_z"] = z(d["median_year_structure_built"])
    d["through_lanes_z"] = z(d["through_lanes"])
    # P3 generic metric (Stage 4 primary, retained for contrast per D-042)
    d["gen_z"] = z(d["local_int_density"])
    # P1 mechanism-specific predictor (Stage 2R). Heavily zero-inflated (78.5%),
    # so both the count and the binary form are carried.
    d["p1_z"] = z(d["p1_routes"])
    d["p1_bin"] = d["p1_any"].astype(float)
    d["p2_z"] = z(d["p2_pairs_per_km2"])
    d["perm_z"] = d[PRED_COL_Z]
    d["betw_z"] = z(d["betweenness_log"])

    d["y"] = np.log(d[outcome]) if outcome == "aadt_per_lane" else d[outcome]

    need = ["y", "perm_z", "gen_z", "p1_z", "p1_bin", "betw_z", "access_controlled",
            "cell_id", "route_id"] + [
        c for c in CTRL_TERMS if not c.startswith("C(")
    ] + ["f_system"]
    before = len(d)
    d = d.dropna(subset=need).copy()
    print(f"  complete cases: {len(d):,} of {before:,} ({len(d)/before:.1%})")
    print(f"  level-2 cells: {d.cell_id.nunique():,} | routes: {d.route_id.nunique():,}")
    occ = d.cell_id.value_counts()
    print(f"  units per cell: median {occ.median():.0f}, singleton cells "
          f"{int((occ==1).sum()):,}")
    return d, need


def fit_mixed(formula: str, d: pd.DataFrame, label: str):
    m = smf.mixedlm(formula, d, groups=d["cell_id"])
    try:
        r = m.fit(method="lbfgs", reml=True)
    except Exception as e:
        print(f"  !! {label} failed to converge: {e}")
        return None
    if not getattr(r, "converged", True):
        print(f"  !! {label}: optimiser reported non-convergence — treat with caution")
    return r


def icc(res) -> float:
    vc = float(res.cov_re.iloc[0, 0])
    return vc / (vc + float(res.scale))


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--city", default=None)
    ap.add_argument("--outcome", default="log_aadt",
                    choices=["log_aadt", "aadt_per_lane"])
    ap.add_argument("--radius", type=int, default=None)
    ap.add_argument("--predictor", default="p1_routes",
                    choices=["p1_routes", "p1_any", "local_int_density"],
                    help="primary permeability predictor (default: P1 count)")
    args = ap.parse_args()
    global PRED_COL_Z
    PRED_COL_Z = {"p1_routes": "p1_z", "p1_any": "p1_bin",
                  "local_int_density": "gen_z"}[args.predictor]

    conf = cfg.config()
    city_key = args.city or conf["project"]["pilot_city"]
    r = args.radius or conf["catchment"]["primary_radius_m"]
    fp = paths.ANALYSIS / (f"analysis_table_r{r}.parquet")
    if not fp.exists():
        print(f"ERROR: {fp} missing (run 03b).")
        return 1

    print(f"Environment: {provenance.environment_stamp()}")
    print(f"City: {city_key} | radius {r} m | outcome {args.outcome} "
          f"| PRIMARY PREDICTOR = {args.predictor}")
    t = pd.read_parquet(fp)
    print(f"\n=== preparing data ===")
    d, _ = prep(t, args.outcome)

    print(f"\n  predictor distributions:")
    print(f"    P1 count : mean {d.p1_routes.mean():.3f}, "
          f"zero on {int((d.p1_routes==0).sum()):,} ({(d.p1_routes==0).mean():.1%})")
    print(f"    P1 binary: {int(d.p1_bin.sum()):,} with a substitute "
          f"({d.p1_bin.mean():.1%})")
    print(f"    P3 int.density: mean {d.local_int_density.mean():.2f}/km², "
          f"sd {d.local_int_density.std():.2f}")
    print(f"    corr(P1, P3) = {d.p1_routes.corr(d.local_int_density):+.3f}")
    print(f"\n  moderator distributions:")
    print(f"    access_controlled: {int(d.access_controlled.sum()):,} controlled / "
          f"{int((1-d.access_controlled).sum()):,} not")
    print(f"    betweenness_log: min {d.betweenness_log.min():.2f}, "
          f"median {d.betweenness_log.median():.2f}, max {d.betweenness_log.max():.2f}")
    raw = {"p1_z": "p1_routes", "p1_bin": "p1_any",
           "gen_z": "local_int_density"}[PRED_COL_Z]
    unit = {"p1_routes": "substitutable routes", "p1_any": "(binary 0/1)",
            "local_int_density": "intersections/km²"}[raw]
    print(f"    perm_z (= {raw}): 1 sd = {d[raw].std():.3f} {unit}")

    ctrl = " + ".join(CTRL_TERMS)
    ladder = {
        "M0": "y ~ 1",
        "M1": f"y ~ {ctrl}",
        "M2": f"y ~ {ctrl} + perm_z",
        # D-044: the P1-vs-P3 contrast is run in the SAME sample so the comparison is
        # like-for-like. M2g is the Stage 4 specification (generic connectivity);
        # M2b enters both, which is legitimate because they correlate only +0.21.
        "M2g": f"y ~ {ctrl} + gen_z",
        "M2b": f"y ~ {ctrl} + perm_z + gen_z",
        "M3": (f"y ~ {ctrl} + perm_z + access_controlled + betw_z"
               f" + perm_z:access_controlled + perm_z:betw_z"),
    }

    results, rows = {}, []
    for label, f in ladder.items():
        print(f"\n{'='*70}\n{label}: {f}\n{'='*70}")
        res = fit_mixed(f, d, label)
        if res is None:
            continue
        results[label] = res
        print(res.summary())
        i = icc(res)
        print(f"  ICC (cell) = {i:.4f}   between-cell var = {float(res.cov_re.iloc[0,0]):.4f}"
              f"   residual var = {float(res.scale):.4f}")
        out = paths.MODELS / f"{label.lower()}_{args.outcome}_r{r}.txt"
        out.write_text(f"{label}: {f}\n\nn={len(d)}  cells={d.cell_id.nunique()}\n"
                       f"ICC={i:.4f}\n\n{res.summary().as_text()}\n")
        rows.append({"model": label, "formula": f, "n": len(d),
                     "cells": d.cell_id.nunique(), "icc": i,
                     "var_cell": float(res.cov_re.iloc[0, 0]),
                     "var_resid": float(res.scale), "loglike": float(res.llf)})

    # --- H1 headline -------------------------------------------------------
    print(f"\n{'='*70}\nP1 vs P3 — mechanism-specific versus generic connectivity\n{'='*70}")
    for lab, term, desc in [("M2", "perm_z", f"P1 ({args.predictor}), alone"),
                            ("M2g", "gen_z", "P3 (intersection density), alone"),
                            ("M2b", "perm_z", f"P1, controlling for P3"),
                            ("M2b", "gen_z", "P3, controlling for P1")]:
        if lab in results and term in results[lab].params.index:
            rr = results[lab]
            bb, ss, pp = rr.params[term], rr.bse[term], rr.pvalues[term]
            star = "***" if pp < .001 else "**" if pp < .01 else "*" if pp < .05 else ""
            print(f"  {desc:34s} {bb:+.4f} (SE {ss:.4f})  p={pp:.4f} {star:3s}"
                  f"  {100*(np.exp(bb)-1):+.2f}%/sd")

    print(f"\n{'='*70}\nH1 — does local permeability reduce arterial traffic?\n{'='*70}")
    if "M2" in results:
        res = results["M2"]
        b = res.params.get("perm_z", np.nan)
        se = res.bse.get("perm_z", np.nan)
        p = res.pvalues.get("perm_z", np.nan)
        lo, hi = b - 1.96 * se, b + 1.96 * se
        raw_p = {"p1_z": "p1_routes", "p1_bin": "p1_any",
                 "gen_z": "local_int_density"}[PRED_COL_Z]
        sd_perm = d[raw_p].std()
        print(f"  perm_z coefficient: {b:+.4f} (SE {se:.4f}), p = {p:.4f}")
        print(f"  95% CI: [{lo:+.4f}, {hi:+.4f}]")
        print(f"  interpretation: a 1 sd rise in {raw_p} ({sd_perm:.3f} units)")
        if args.outcome == "log_aadt":
            print(f"    changes AADT by {100*(np.exp(b)-1):+.2f}% "
                  f"[{100*(np.exp(lo)-1):+.2f}%, {100*(np.exp(hi)-1):+.2f}%]")
        verdict = ("H1 SUPPORTED (negative, p<0.05)" if (p < 0.05 and b < 0)
                   else "H1 CONTRADICTED (positive, p<0.05)" if (p < 0.05 and b > 0)
                   else "H1 NOT SUPPORTED — cannot reject H1-null")
        print(f"  --> {verdict}")

    # --- H2 marginal effects ----------------------------------------------
    print(f"\n{'='*70}\nH2 — is relief conditional? (marginal effects)\n{'='*70}")
    if "M3" in results:
        res = results["M3"]
        pm = res.params
        for term in ["perm_z", "access_controlled", "betw_z",
                     "perm_z:access_controlled", "perm_z:betw_z"]:
            if term in pm.index:
                print(f"  {term:28s} {pm[term]:+.4f}  (SE {res.bse[term]:.4f}, "
                      f"p = {res.pvalues[term]:.4f})")
        print("\n  marginal effect of perm_z (dY/d perm_z):")
        b_p = pm.get("perm_z", 0.0)
        b_pa = pm.get("perm_z:access_controlled", 0.0)
        b_pb = pm.get("perm_z:betw_z", 0.0)
        for ac in (0.0, 1.0):
            for bq, blab in [(d.betw_z.quantile(.1), "low betweenness (p10)"),
                             (d.betw_z.quantile(.5), "median betweenness"),
                             (d.betw_z.quantile(.9), "high betweenness (p90)")]:
                me = b_p + b_pa * ac + b_pb * bq
                actxt = "access-controlled" if ac else "no access control"
                pct = 100 * (np.exp(me) - 1) if args.outcome == "log_aadt" else me
                print(f"    {actxt:20s} · {blab:24s} ME = {me:+.4f}"
                      + (f"  ({pct:+.2f}% AADT per sd)" if args.outcome == "log_aadt" else ""))
        print("\n  H2 predicts the MOST NEGATIVE marginal effect at "
              "'no access control' + low betweenness.")

    if rows:
        tab = pd.DataFrame(rows)
        fp_t = paths.TABLES / f"model_ladder_{args.outcome}_r{r}.csv"
        tab.to_csv(fp_t, index=False)
        print(f"\n  wrote {fp_t.relative_to(paths.ROOT)}")
        print(tab[["model", "n", "cells", "icc", "var_cell", "var_resid",
                   "loglike"]].to_string(index=False,
                                         float_format=lambda x: f"{x:.4f}"))

    provenance.log_progress(
        "05a_multilevel",
        f"{city_key}: M0-M3 fitted, outcome {args.outcome}, r={r} m, n={len(d):,}",
    )
    print("\nStage 4a complete.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
