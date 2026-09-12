#!/usr/bin/env python
"""Stage 5 — multi-city models.

Reports PER-CITY estimates first and pooled estimates second, deliberately.

Rationale (D-054): pooled row counts are wildly unbalanced — Boston supplies ~70% of
units because Massachusetts HPMS reports far finer AADT variation, so fewer 0.1-mile
increments merge under D-028. An unweighted pooled coefficient would be mostly Boston's
coefficient, which defeats the purpose of a purposive multi-city design built to test
whether the effect holds ACROSS contrasting network cultures. So:

  1. per-city models      -> is the effect stable across network types?
  2. pooled + city FE     -> D-047, level differences absorbed
  3. pooled, equal city weight -> does balancing change the story?

Usage
-----
    uv run python code/05_model/05c_multicity.py
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


def z(s):
    sd = s.std(ddof=0)
    return (s - s.mean()) / sd if sd and sd > 0 else s * 0.0


def prep(d, within_city=True):
    """Standardise. Within-city z-scoring keeps per-city coefficients comparable."""
    d = d.copy()
    d["access_controlled"] = d["access_control_"].isin([1, 2]).astype(float)
    d["betweenness_log"] = np.log10(d["arterial_betweenness"] + 1e-5)
    src = {"pop_density_km2_z": "pop_density_km2", "lu_entropy_z": "lu_entropy",
           "dist_cbd_km_c_z": "dist_cbd_km_c", "dist_cbd_km_c_sq_z": "dist_cbd_km_c_sq",
           "median_year_z": "median_year_structure_built",
           "through_lanes_z": "through_lanes", "gen_z": "local_int_density",
           "betw_z": "betweenness_log"}
    grp = d.groupby("city") if (within_city and "city" in d.columns) else None
    for dst, s in src.items():
        d[dst] = grp[s].transform(z) if grp is not None else z(d[s])
    d["p1"] = d["p1_any"].astype(float)
    d["y"] = d["log_aadt"]
    need = ["y", "p1", "gen_z", "betw_z", "access_controlled", "cell_id",
            "route_id", "f_system"] + CTRL
    return d.dropna(subset=need).copy()


def fit(d, formula, groups):
    try:
        return smf.mixedlm(formula, d, groups=groups).fit(method="lbfgs", reml=True)
    except Exception as e:
        print(f"    !! fit failed: {e}")
        return None


def row(res, term, label, n, ncell):
    if res is None or term not in res.params.index:
        return None
    b, se, p = res.params[term], res.bse[term], res.pvalues[term]
    return {"model": label, "n": n, "cells": ncell, "beta": b, "se": se, "p": p,
            "lo": b - 1.96 * se, "hi": b + 1.96 * se,
            "pct": 100 * (np.exp(b) - 1)}


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
    print(f"\nPooled r={r} m: {len(d):,} units, {d.city.nunique()} cities, "
          f"{d.cell_id.nunique():,} cells")
    share = (d.city.value_counts(normalize=True) * 100).round(1)
    print(f"  city shares: {share.to_dict()}")

    base = " + ".join(CTRL) + " + C(f_system)"
    rows = []

    # ---------- 1. per city ----------
    print(f"\n{'='*74}\n1. PER-CITY estimates — H1 (P1 substitutability)\n{'='*74}")
    for c, g in d.groupby("city"):
        if len(g) < 100 or g.f_system.nunique() < 2:
            print(f"  {c}: too few units ({len(g)}) — skipped")
            continue
        res = fit(g, f"y ~ {base} + p1", g["cell_id"])
        rr = row(res, "p1", c, len(g), g.cell_id.nunique())
        if rr:
            rows.append(rr)
    if rows:
        t = pd.DataFrame(rows)
        print(f"\n  {'city':<14}{'n':>7}{'cells':>7}{'beta':>9}{'SE':>8}"
              f"{'p':>9}{'% AADT':>9}   95% CI")
        for _, x in t.iterrows():
            star = "***" if x.p < .001 else "**" if x.p < .01 else "*" if x.p < .05 else ""
            print(f"  {x.model:<14}{x.n:>7,.0f}{x.cells:>7,.0f}{x.beta:>9.4f}"
                  f"{x.se:>8.4f}{x.p:>9.4f}{x.pct:>8.1f}%   "
                  f"[{x.lo:+.3f},{x.hi:+.3f}] {star}")
        neg = int((t.beta < 0).sum())
        sig = int(((t.p < .05) & (t.beta < 0)).sum())
        print(f"\n  negative in {neg}/{len(t)} cities; "
              f"negative AND significant in {sig}/{len(t)}")
        rng = t.beta.max() - t.beta.min()
        print(f"  coefficient spread: {t.beta.min():+.4f} to {t.beta.max():+.4f} "
              f"(range {rng:.4f})")
        print("  -> if the range is wide, the effect is CONDITIONAL on network culture,"
              "\n     which is itself the H2-style finding; pooling would hide it.")

    # ---------- 2. pooled, city fixed effects ----------
    print(f"\n{'='*74}\n2. POOLED with city fixed effects (D-047)\n{'='*74}")
    res_fe = fit(d, f"y ~ {base} + C(city) + p1", d["cell_id"])
    r_fe = row(res_fe, "p1", "pooled + city FE", len(d), d.cell_id.nunique())
    if r_fe:
        print(f"  p1 = {r_fe['beta']:+.4f} (SE {r_fe['se']:.4f}), p = {r_fe['p']:.4f}, "
              f"{r_fe['pct']:+.1f}% AADT")

    # ---------- 3. pooled, equal city weight ----------
    print(f"\n{'='*74}\n3. POOLED with EQUAL city weights\n{'='*74}")
    w = d.groupby("city")["y"].transform(lambda s: len(d) / (d.city.nunique() * len(s)))
    ols_w = smf.wls(f"y ~ {base} + C(city) + p1", d, weights=w).fit(
        cov_type="cluster", cov_kwds={"groups": d["city"]})
    print(f"  p1 = {ols_w.params['p1']:+.4f} (SE {ols_w.bse['p1']:.4f}), "
          f"p = {ols_w.pvalues['p1']:.4f}   [city-clustered, {d.city.nunique()} clusters]")
    print("  NOTE: with few cities, city-clustered SEs are themselves unreliable; "
          "read the per-city table as primary.")

    # ---------- 4. P1 vs P3 across cities ----------
    print(f"\n{'='*74}\n4. P1 vs P3 (generic connectivity), pooled + city FE\n{'='*74}")
    for lab, term, f_ in [("P1 alone", "p1", f"y ~ {base} + C(city) + p1"),
                          ("P3 alone", "gen_z", f"y ~ {base} + C(city) + gen_z"),
                          ("P1 | both", "p1", f"y ~ {base} + C(city) + p1 + gen_z"),
                          ("P3 | both", "gen_z", f"y ~ {base} + C(city) + p1 + gen_z")]:
        rr = fit(d, f_, d["cell_id"])
        if rr is not None and term in rr.params.index:
            b, se, p = rr.params[term], rr.bse[term], rr.pvalues[term]
            star = "***" if p < .001 else "**" if p < .01 else "*" if p < .05 else ""
            print(f"  {lab:<12} {b:+.4f} (SE {se:.4f})  p={p:.4f} {star}")

    # ---------- 5. H2 moderation, pooled ----------
    print(f"\n{'='*74}\n5. H2 moderation, pooled + city FE\n{'='*74}")
    res_h2 = fit(d, f"y ~ {base} + C(city) + p1 + access_controlled + betw_z"
                    f" + p1:access_controlled + p1:betw_z", d["cell_id"])
    if res_h2 is not None:
        for term in ["p1", "access_controlled", "betw_z",
                     "p1:access_controlled", "p1:betw_z"]:
            if term in res_h2.params.index:
                print(f"  {term:24s} {res_h2.params[term]:+.4f} "
                      f"(SE {res_h2.bse[term]:.4f}, p={res_h2.pvalues[term]:.4f})")

    if rows:
        out = pd.DataFrame(rows)
        if r_fe:
            out = pd.concat([out, pd.DataFrame([r_fe])], ignore_index=True)
        fpo = paths.TABLES / f"multicity_h1_r{r}.csv"
        out.to_csv(fpo, index=False)
        print(f"\n  wrote {fpo.relative_to(paths.ROOT)}")
    provenance.log_progress("05c_multicity",
                            f"multi-city H1 at r={r} m, {d.city.nunique()} cities")
    print("\nStage 5 modelling complete.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
