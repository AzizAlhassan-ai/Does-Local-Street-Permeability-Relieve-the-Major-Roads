#!/usr/bin/env python
"""Stage 5 — RQ2 and RQ3 re-estimated on the revised frame (D-101).

RQ2 does not survive the revision, and this script is the evidence for that. The
access-role moderation reported in earlier drafts (+0.119, p = 0.0015) is decomposed
against the two changes to the frame, so a reader can see which one removes it:

    previous frame, no floor        +0.119  p = 0.0015   <- the earlier claim
    previous frame + 400 m floor    +0.103  p = 0.072
    exogenous frame, no floor       +0.055  p = 0.230    <- the unit definition does it
    exogenous frame + 400 m floor   +0.049  p = 0.337    <- revised primary

The moderation was therefore an artefact of dissolving units on a key that contained the
outcome, not a conditional mechanism. We report it as withdrawn.

RQ3 (variance decomposition) is re-run on the revised frame with the same LMG/Shapley
procedure, and the length strata are re-reported.

Usage
-----
    uv run python code/05_model/05zc_rq2_rq3_v2.py
"""
from __future__ import annotations
import argparse, itertools, pathlib, sys
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
import numpy as np, pandas as pd, statsmodels.formula.api as smf
from lib import cfg, paths, provenance

R, MIN_LEN = 800, 400.0
CTRL = ["pop_density_km2_z", "job_density_km2_z", "lu_entropy_z", "dist_cbd_km_c_z",
        "dist_cbd_km_c_sq_z", "median_year_z", "through_lanes_z"]


def z(s):
    sd = s.std(ddof=0)
    return (s - s.mean()) / sd if sd and sd > 0 else s * 0.0


def prep(frame="aadtfree", floor=MIN_LEN):
    suf = f"__{frame}" if frame else ""
    d = pd.read_parquet(paths.DATA / f"analysis{suf}" / f"analysis_pooled_r{R}.parquet")
    d = d[d.length_m >= floor].copy()
    d["access_controlled"] = d["access_control_"].isin([1, 2]).astype(float)
    d["betweenness_log"] = np.log10(d["arterial_betweenness"] + 1e-5)
    src = {"pop_density_km2_z": "pop_density_km2", "job_density_km2_z": "job_density_km2",
           "lu_entropy_z": "lu_entropy", "dist_cbd_km_c_z": "dist_cbd_km_c",
           "dist_cbd_km_c_sq_z": "dist_cbd_km_c_sq",
           "median_year_z": "median_year_structure_built",
           "through_lanes_z": "through_lanes", "betw_z": "betweenness_log",
           "p1n_z": "p1_routes"}
    g = d.groupby("city")
    for k, v in src.items():
        if v in d.columns:
            d[k] = g[v].transform(z)
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
    argparse.ArgumentParser(description=__doc__).parse_args()
    d = prep()
    base = " + ".join(CTRL) + " + C(f_system)"
    cities = sorted(d.city.unique())
    print(f"Environment: {provenance.environment_stamp()}\nn = {len(d):,}")
    rows = []

    # ------------------------------------------------------------------ RQ2
    print(f"\n{'='*96}\nRQ2 — WHERE THE MODERATION WENT\n{'='*96}")
    f_mod = (f"y ~ {base} + C(city) + p1 + access_controlled + betw_z"
             f" + p1:access_controlled + p1:betw_z")
    print(f"  {'frame':<34}{'floor':>7}{'n':>9}{'P1 × access-controlled':>24}{'p':>9}")
    for frame, floor, lab in (("", 0, "previous (AADT in the key)"),
                              ("", MIN_LEN, "previous + 400 m floor"),
                              ("aadtfree", 0, "exogenous, no floor"),
                              ("aadtfree", MIN_LEN, "exogenous + 400 m floor [PRIMARY]")):
        dd = prep(frame, floor).dropna(subset=["betw_z", "access_controlled"])
        r = fit(dd, f_mod)
        if r is None:
            continue
        b, p = r.params["p1:access_controlled"], r.pvalues["p1:access_controlled"]
        print(f"  {lab:<34}{floor:>7.0f}{len(dd):>9,}{b:>+24.4f}{p:>9.4f}")
        rows.append({"table": "rq2_decomposition", "frame": lab, "floor": floor,
                     "n": len(dd), "beta_interaction": b, "p": p})
    print("\n  -> the interaction is removed by the UNIT DEFINITION, not by the length")
    print("     floor. Under an outcome-free frame it is indistinguishable from zero.")

    dmo = d.dropna(subset=["betw_z", "access_controlled"])
    r = fit(dmo, f_mod)
    print(f"\n  Revised primary moderation model, n = {len(dmo):,}:")
    for t in ["p1", "access_controlled", "betw_z", "p1:access_controlled", "p1:betw_z"]:
        print(f"    {t:<24}{r.params[t]:>+9.4f} (SE {r.bse[t]:.4f}, p = {r.pvalues[t]:.4f})")
        rows.append({"table": "T_moderation_v2", "term": t, "n": len(dmo),
                     "beta": r.params[t], "se": r.bse[t], "p": r.pvalues[t]})
    print(f"\n  {'city':<16}{'P1 × access-controlled':>24}{'p':>9}{'treated & AC':>14}")
    for c in cities:
        g = dmo[dmo.city == c]
        rr = fit(g, f"y ~ {base} + p1 + access_controlled + p1:access_controlled")
        if rr is None or "p1:access_controlled" not in rr.params.index:
            continue
        nt = int(((g.p1 == 1) & (g.access_controlled == 1)).sum())
        print(f"  {c:<16}{rr.params['p1:access_controlled']:>+24.4f}"
              f"{rr.pvalues['p1:access_controlled']:>9.4f}{nt:>14,}")
        rows.append({"table": "moderation_percity_v2", "city": c,
                     "beta": rr.params["p1:access_controlled"],
                     "p": rr.pvalues["p1:access_controlled"], "n_treated_ac": nt})

    # ------------------------------------------------------------------ RQ3
    print(f"\n{'='*96}\nRQ3 — VARIANCE DECOMPOSITION ON THE REVISED FRAME\n{'='*96}")
    blocks = {"configuration": ["p1"],
              "density and land use": ["pop_density_km2_z", "job_density_km2_z",
                                       "lu_entropy_z"],
              "position and road type": ["dist_cbd_km_c_z", "dist_cbd_km_c_sq_z",
                                         "median_year_z", "through_lanes_z"]}
    dm = d.dropna(subset=sum(blocks.values(), [])).copy()
    fixed = "C(f_system) + C(city)"

    def r2(terms):
        f_ = "y ~ " + fixed + ("" if not terms else " + " + " + ".join(terms))
        return smf.ols(f_, dm).fit().rsquared

    names = list(blocks)
    full, base_r2 = r2(sum(blocks.values(), [])), r2([])
    lmg = {n: 0.0 for n in names}
    perms = list(itertools.permutations(names))
    for order in perms:
        cur, prev = [], base_r2
        for n in order:
            cur += blocks[n]
            now = r2(cur)
            lmg[n] += now - prev
            prev = now
    for n in names:
        lmg[n] /= len(perms)
    print(f"  model R² = {full:.4f} (fixed effects alone {base_r2:.4f})")
    print(f"  {'block':<26}{'LMG share':>14}{'as % of model R²':>20}")
    for n in names:
        print(f"  {n:<26}{lmg[n]:>14.4f}{100*lmg[n]/full:>19.2f}%")
        rows.append({"table": "rq3_lmg", "block": n, "share": lmg[n],
                     "pct_of_model_r2": 100*lmg[n]/full, "model_r2": full})
    ratio = lmg["density and land use"] / lmg["configuration"]
    print(f"  density and land use explain {ratio:.1f}x what configuration does; "
          f"position and road type {lmg['position and road type']/lmg['configuration']:.1f}x")
    r = fit(dm, f"y ~ {base} + C(city) + p1n_z")
    print(f"  (route-count form as a check on the binary coding: "
          f"{r.params['p1n_z']:+.4f}, p = {r.pvalues['p1n_z']:.4f})")

    # ------------------------------------------------------------------ strata
    print(f"\n{'='*96}\nLENGTH STRATA ON THE REVISED FRAME\n{'='*96}")
    edges = [400, 600, 800, 1200, np.inf]
    labs = ["400–600 m", "600–800", "800–1200", "≥1200 m"]
    d["strat"] = pd.cut(d.length_m, edges, labels=labs)
    for s_ in labs:
        g = d[d.strat == s_]
        if len(g) < 200 or g.p1.nunique() < 2:
            continue
        rr = fit(g, f"y ~ {base} + C(city) + p1")
        if rr is None:
            continue
        print(f"  {s_:<12}n={len(g):>7,}  %P1={100*g.p1.mean():>5.1f}%  "
              f"β={rr.params['p1']:>+8.4f} (SE {rr.bse['p1']:.4f}, p={rr.pvalues['p1']:.4f})")
        rows.append({"table": "strata_v2", "stratum": s_, "n": len(g),
                     "pct_p1": 100*g.p1.mean(), "beta": rr.params["p1"],
                     "se": rr.bse["p1"], "p": rr.pvalues["p1"]})

    out = pd.DataFrame(rows)
    fp = paths.TABLES / "rq2_rq3_v2.csv"
    out.to_csv(fp, index=False)
    print(f"\n  wrote {fp.relative_to(paths.ROOT)}")
    provenance.log_progress("05zc_rq2_rq3_v2",
                            "RQ2 withdrawn, RQ3 and strata on the revised frame (D-101)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
