#!/usr/bin/env python
"""Stage 5 — round-3 panel requests, model side (D-083).

A. UNCONDITIONAL P3 + MEDIATION (bravo, delta — the panel's headline concern)
   The manuscript reports each P3 metric *controlling for P1* and reads the null
   as "the standard measures do not detect the mechanism". Two reviewers replied,
   correctly, that P1 is theorised downstream of P3, so a null on P3 | P1 is the
   signature of mediation rather than of a failed measure. The answer is to report
   the unconditional estimate alongside, and decompose: total = direct + indirect.

B. LENGTH-STRATIFIED ESTIMATION (alfa, bravo, delta)
   Unit length is a function of state reporting granularity, and P1's detour cap is
   defined relative to segment length, so prevalence is mechanically suppressed on
   short units. Estimating within common length strata removes that channel from
   the cross-city comparison.

C. SPATIAL DURBIN (alfa, delta)
   The outcome is a redistribution variable: traffic leaving segment A lands on
   B and C in the same sample, so a spatial *error* model treats as nuisance what
   is substantively the interference. A lag/Durbin specification makes the spillover
   estimable, and a positive indirect effect would be the paper's own mechanism
   showing up in the estimator.

D. WILD CLUSTER BOOTSTRAP (alfa)
   Six city clusters cannot support cluster-robust inference; p-values from that
   specification are replaced by a wild cluster bootstrap-t.

Usage
-----
    uv run python code/05_model/05n_round3_models.py
"""
from __future__ import annotations
import argparse, pathlib, sys
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
import numpy as np, pandas as pd, statsmodels.formula.api as smf
from lib import cfg, paths, provenance

CTRL = ["pop_density_km2_z", "lu_entropy_z", "dist_cbd_km_c_z",
        "dist_cbd_km_c_sq_z", "median_year_z", "through_lanes_z"]
P3 = {"local_int_density": "intersection density", "local_link_node_ratio": "link–node ratio",
      "local_street_density": "street density", "local_deadend_share": "dead-end share",
      "local_circuity": "circuity"}


def z(s):
    sd = s.std(ddof=0)
    return (s - s.mean()) / sd if sd and sd > 0 else s * 0.0


def prep(d):
    d = d.copy()
    d["access_controlled"] = d["access_control_"].isin([1, 2]).astype(float)
    d["betweenness_log"] = np.log10(d["arterial_betweenness"] + 1e-5)
    src = {"pop_density_km2_z": "pop_density_km2", "lu_entropy_z": "lu_entropy",
           "dist_cbd_km_c_z": "dist_cbd_km_c", "dist_cbd_km_c_sq_z": "dist_cbd_km_c_sq",
           "median_year_z": "median_year_structure_built", "through_lanes_z": "through_lanes",
           "betw_z": "betweenness_log"}
    for m in P3:
        src[f"{m}_z"] = m
    g = d.groupby("city")
    for dst, s in src.items():
        d[dst] = g[s].transform(z)
    d["p1"] = d["p1_any"].astype(float)
    d["y"] = d["log_aadt"]
    return d.dropna(subset=["y", "p1", "cell_id", "route_id", "f_system",
                            "local_int_density_z"] + CTRL).copy()


def fit(d, f):
    try:
        return smf.mixedlm(f, d, groups=d["cell_id"]).fit(method="lbfgs", reml=True)
    except Exception as e:
        print(f"    !! {e}"); return None


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--radius", type=int, default=800)
    args = ap.parse_args()
    r = args.radius
    d = prep(pd.read_parquet(paths.ANALYSIS / f"analysis_pooled_r{r}.parquet"))
    base = " + ".join(CTRL) + " + C(f_system)"
    cities = sorted(d.city.unique())
    print(f"Environment: {provenance.environment_stamp()}\nn = {len(d):,}, {len(cities)} cities")
    rows = []

    # ---------------------------------------------------------------- A
    print(f"\n{'='*94}\nA. P3 UNCONDITIONAL vs CONDITIONAL ON P1 — mediation decomposition\n{'='*94}")
    print(f"  {'metric':<22}{'TOTAL (P3 alone)':>26}{'DIRECT (P3 | P1)':>26}{'indirect':>12}{'% mediated':>12}")
    for m, lab in P3.items():
        t_ = f"{m}_z"
        dm = d.dropna(subset=[t_])
        r_tot = fit(dm, f"y ~ {base} + C(city) + {t_}")
        r_dir = fit(dm, f"y ~ {base} + C(city) + p1 + {t_}")
        if r_tot is None or r_dir is None:
            continue
        tot, ptot = r_tot.params[t_], r_tot.pvalues[t_]
        dir_, pdir = r_dir.params[t_], r_dir.pvalues[t_]
        ind = tot - dir_
        pct = 100 * ind / tot if abs(tot) > 1e-9 else np.nan
        rows.append({"check": "mediation", "metric": lab, "n": len(dm), "total": tot,
                     "p_total": ptot, "direct": dir_, "p_direct": pdir, "indirect": ind,
                     "pct_mediated": pct})
        print(f"  {lab:<22}{tot:>+13.4f} (p={ptot:5.3f}){dir_:>+13.4f} (p={pdir:5.3f})"
              f"{ind:>+12.4f}{pct:>11.1f}%")
    print("\n  -> If P3 were a valid but blunt proxy, TOTAL would be negative and significant")
    print("     and most of it would be mediated by P1. If P3 simply does not track the")
    print("     mechanism, TOTAL is null on its own — no mediation to decompose.")

    # per-city unconditional, since the Denver pilot is the passage the panel cites
    print(f"\n  Unconditional intersection density, per city:")
    print(f"  {'city':<16}{'β':>10}{'SE':>9}{'p':>9}")
    for c in cities:
        g = d[d.city == c]
        rr = fit(g, f"y ~ {base} + local_int_density_z")
        if rr is None: continue
        b, s, p = (rr.params["local_int_density_z"], rr.bse["local_int_density_z"],
                   rr.pvalues["local_int_density_z"])
        rows.append({"check": "p3_uncond_city", "city": c, "beta": b, "se": s, "p": p})
        print(f"  {c:<16}{b:>+10.4f}{s:>9.4f}{p:>9.4f}")

    # ---------------------------------------------------------------- B
    print(f"\n{'='*94}\nB. LENGTH-STRATIFIED ESTIMATION\n{'='*94}")
    edges = [0, 200, 400, 800, 1600, np.inf]
    labs = ["<200 m", "200–400", "400–800", "800–1600", "≥1600 m"]
    d["lenstrat"] = pd.cut(d.length_m, edges, labels=labs)
    print(f"  {'stratum':<12}{'n':>8}{'%P1':>8}{'β':>10}{'SE':>9}{'p':>9}   cities contributing")
    for s_ in labs:
        g = d[d.lenstrat == s_]
        if len(g) < 200 or g.p1.nunique() < 2:
            print(f"  {s_:<12}{len(g):>8,}  — too few"); continue
        rr = fit(g, f"y ~ {base} + C(city) + p1")
        if rr is None: continue
        b, se, p = rr.params["p1"], rr.bse["p1"], rr.pvalues["p1"]
        ncity = g.groupby("city").size()
        rows.append({"check": "length_stratum", "stratum": s_, "n": len(g),
                     "pct_p1": 100*g.p1.mean(), "beta": b, "se": se, "p": p})
        print(f"  {s_:<12}{len(g):>8,}{100*g.p1.mean():>7.1f}%{b:>+10.4f}{se:>9.4f}{p:>9.4f}   "
              f"{(ncity>50).sum()} cities")
    print("\n  -> A coefficient that is stable across strata cannot be an artefact of the")
    print("     length differences that state reporting practice induces.")

    # ---------------------------------------------------------------- C
    print(f"\n{'='*94}\nC. SPATIAL LAG / DURBIN — direct and indirect effects\n{'='*94}")
    try:
        import geopandas as gpd
        from libpysal.weights import KNN
        from spreg import GM_Lag
        metric = cfg.config()["crs"]["metric"]
        for c in cities:
            g = d[d.city == c].copy()
            seg = gpd.read_parquet(paths.processed(c) / "segments.parquet").to_crs(metric)
            seg["segment_uid"] = c + "|" + seg["segment_uid"].astype(str)
            g = g.merge(seg[["segment_uid", "geometry"]], on="segment_uid", how="inner")
            g = gpd.GeoDataFrame(g, geometry="geometry", crs=metric)
            pts = gpd.GeoDataFrame(geometry=[gm.interpolate(.5, normalized=True)
                                             for gm in g.geometry], crs=metric)
            w = KNN.from_dataframe(pts, k=8); w.transform = "r"
            X = g[CTRL + ["p1"]].to_numpy(float)
            y = g[["y"]].to_numpy(float)
            m = GM_Lag(y, X, w=w, name_x=CTRL + ["p1"], name_y="log_aadt")
            k = m.betas.flatten(); rho = float(k[-1]); b_p1 = float(k[len(CTRL) + 1])
            direct = b_p1
            total = b_p1 / (1 - rho)
            indirect = total - direct
            rows.append({"check": "durbin", "city": c, "rho": rho, "direct": direct,
                         "indirect": indirect, "total": total})
            print(f"  {c:<16} ρ={rho:+.3f}  direct={direct:+.4f}  indirect={indirect:+.4f}"
                  f"  total={total:+.4f}")
        print("\n  -> A NEGATIVE indirect effect would mean substitutable neighbours lower this")
        print("     segment's volume too; a POSITIVE one is the redistribution the paper argues")
        print("     for — traffic displaced from a substitutable segment onto its neighbours.")
    except Exception as e:
        print(f"  spatial lag unavailable: {e}")

    # ---------------------------------------------------------------- D
    print(f"\n{'='*94}\nD. WILD CLUSTER BOOTSTRAP-t on six city clusters\n{'='*94}")
    w_ = d.groupby("city")["y"].transform(lambda s: len(d) / (d.city.nunique() * len(s)))
    f_ = f"y ~ {base} + C(city) + p1"
    m0 = smf.wls(f_, d, weights=w_).fit()
    t_obs = m0.params["p1"] / m0.bse["p1"]
    # restricted model under H0: beta_p1 = 0
    f_r = f"y ~ {base} + C(city)"
    m_r = smf.wls(f_r, d, weights=w_).fit()
    resid_r = m_r.resid.to_numpy()
    fitted_r = m_r.fittedvalues.to_numpy()
    codes = pd.Categorical(d.city).codes
    rng = np.random.default_rng(20260803)
    B, cnt = 999, 0
    for _ in range(B):
        signs = rng.choice([-1.0, 1.0], size=d.city.nunique())[codes]
        d["_yb"] = fitted_r + resid_r * signs
        mb = smf.wls(f_.replace("y ~", "_yb ~"), d, weights=w_).fit()
        if abs(mb.params["p1"] / mb.bse["p1"]) >= abs(t_obs):
            cnt += 1
    p_wcb = (cnt + 1) / (B + 1)
    print(f"  equal-weighted pooled β = {m0.params['p1']:+.4f}, t = {t_obs:+.3f}")
    print(f"  wild cluster bootstrap-t p = {p_wcb:.4f}  ({B} replications, 6 clusters)")
    rows.append({"check": "wild_bootstrap", "beta": m0.params["p1"], "t": t_obs, "p_wcb": p_wcb})

    out = pd.DataFrame(rows)
    fp = paths.TABLES / f"round3_models_r{r}.csv"
    out.to_csv(fp, index=False)
    print(f"\n  wrote {fp.relative_to(paths.ROOT)}")
    provenance.log_progress("05n_round3_models", "mediation, length strata, Durbin, wild bootstrap")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
