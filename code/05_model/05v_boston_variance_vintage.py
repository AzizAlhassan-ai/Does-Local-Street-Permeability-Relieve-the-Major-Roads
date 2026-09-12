#!/usr/bin/env python
"""Stage 5 — Boston capacity test, variance decomposition, vintage, diagnostics (D-091).

A. THE BOSTON CAPACITY ACCOUNT, TESTED (bravo M6)
   The manuscript lists capacity censoring as one of three surviving explanations for
   Boston's small coefficient and then stops, on the grounds that HPMS carries no
   capacity field. But censoring at the top of the conditional distribution has a
   signature: the P1 coefficient should attenuate at high quantiles of AADT and hold at
   low ones. Quantile regression and a P1 × volume-per-lane interaction discriminate
   without a capacity field.

B. VARIANCE DECOMPOSITION, SPECIFIED (bravo M5)
   "A hierarchical decomposition" names a family, not a method. This reports the exact
   procedure — averaging each block's incremental R² over all orderings of the blocks
   (the LMG/Shapley decomposition), on a fixed-effects OLS so that R² is unambiguous —
   with block membership stated and the sequential result alongside for comparison.

C. OSM VINTAGE (alfa M5)
   A 2026 network extract against a 2018 outcome credits post-2018 links to segments
   that lacked them, and the error concentrates in the fastest-growing fabric. OSM
   history is not retrievable at metropolitan scale within this pipeline, so the test
   here restricts to catchments whose housing stock predates the outcome (ACS median
   year built) — where the network can hardly have changed — and to the pre-2018-built
   share, and asks whether the estimate holds.

D. PER-CITY AND EQUAL-WEIGHTED COMPARATORS AND MODERATION (alfa M1)
   Every pooled quantity in the paper is Boston-weighted. Table 6 and Table 7 are
   re-estimated per city and under equal city weights.

E. DIAGNOSTICS (bravo m5, m7)
   Per-city Moran's I and spatial-error models; residual normality, heteroskedasticity
   across cities, and influence of high-leverage cells.

F. SIGN CONVENTION (bravo m4)
   Dead-end share and circuity run the opposite way to the other three P3 metrics. All
   five are re-reported oriented so that higher = more connected.

Usage
-----
    uv run python code/05_model/05v_boston_variance_vintage.py
"""
from __future__ import annotations
import argparse, itertools, pathlib, sys
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
import numpy as np, pandas as pd, statsmodels.api as sm, statsmodels.formula.api as smf
from lib import cfg, paths, provenance

CTRL = ["pop_density_km2_z", "lu_entropy_z", "dist_cbd_km_c_z",
        "dist_cbd_km_c_sq_z", "median_year_z", "through_lanes_z"]
P3 = {"local_int_density": ("intersection density", +1),
      "local_link_node_ratio": ("link–node ratio", +1),
      "local_street_density": ("street density", +1),
      "local_deadend_share": ("dead-end share", -1),
      "local_circuity": ("circuity", -1)}
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
           "through_lanes_z": "through_lanes", "betw_z": "betweenness_log"}
    for m in P3:
        src[f"{m}_z"] = m
    g = d.groupby("city")
    for dst, s in src.items():
        d[dst] = g[s].transform(z)
    d["p1"] = d["p1_any"].astype(float)
    d["y"] = d["log_aadt"]
    d["vpl"] = d["aadt"] / d["through_lanes"].replace(0, np.nan)
    return d.dropna(subset=["y", "p1", "cell_id", "route_id", "f_system"] + CTRL).copy()


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
    print(f"Environment: {provenance.environment_stamp()}\nn = {len(d):,}")
    rows = []

    # ------------------------------------------------------------------ A
    print(f"\n{'='*96}\nA. IS BOSTON CAPACITY-CENSORED? quantile and volume-per-lane"
          f"\n{'='*96}")
    for c in ["boston", "denver"]:
        g = d[d.city == c].dropna(subset=["vpl"]).copy()
        print(f"\n  --- {c} (n = {len(g):,}, median volume per lane "
              f"{g.vpl.median():,.0f}) ---")
        print(f"  {'quantile of AADT':<20}{'β on P1':>11}{'SE':>9}{'p':>9}")
        X = sm.add_constant(pd.get_dummies(
            g[CTRL + ["p1", "f_system"]], columns=["f_system"], drop_first=True
        ).astype(float))
        for q in (0.10, 0.25, 0.50, 0.75, 0.90):
            try:
                m = sm.QuantReg(g["y"].to_numpy(float), X.to_numpy(float)).fit(q=q)
                i = list(X.columns).index("p1")
                b, se, p = m.params[i], m.bse[i], m.pvalues[i]
                print(f"  {f'q = {q:.2f}':<20}{b:>+11.4f}{se:>9.4f}{p:>9.4f}")
                rows.append({"check": "quantile", "city": c, "q": q, "beta": b,
                             "se": se, "p": p})
            except Exception as e:
                print(f"  q = {q:.2f}: failed ({e})")
        # NOTE: volume per lane is AADT divided by lanes, so log(vpl) = y - log(lanes).
        # Interacting P1 with it puts the outcome on the right-hand side; the referee's
        # suggested interaction is not estimable here and the quantile profile is the
        # test. What IS estimable without circularity is P1 x lanes, since lanes are the
        # supply side of the same ratio.
        rr = fit(g, f"y ~ {base} + p1 + p1:through_lanes_z")
        if rr is not None and "p1:through_lanes_z" in rr.params.index:
            t = "p1:through_lanes_z"
            print(f"  P1 × through lanes (supply proxy): {rr.params[t]:+.4f} "
                  f"(SE {rr.bse[t]:.4f}, p = {rr.pvalues[t]:.4f})   "
                  f"main P1 {rr.params['p1']:+.4f}")
            rows.append({"check": "lanes_interaction", "city": c,
                         "beta_int": rr.params[t], "p_int": rr.pvalues[t],
                         "beta_p1": rr.params["p1"]})
    print("\n  -> capacity censoring predicts ATTENUATION at the TOP of the conditional")
    print("     distribution and an intact effect at the bottom. The opposite profile,")
    print("     or a flat one, does not support it.")

    # ------------------------------------------------------------------ B
    print(f"\n{'='*96}\nB. VARIANCE DECOMPOSITION — LMG/Shapley over three blocks"
          f"\n{'='*96}")
    blocks = {
        "configuration": ["p1"],
        "density and land use": ["pop_density_km2_z", "lu_entropy_z"],
        "position and road type": ["dist_cbd_km_c_z", "dist_cbd_km_c_sq_z",
                                   "median_year_z", "through_lanes_z"],
    }
    dm = d.dropna(subset=sum(blocks.values(), [])).copy()
    fixed = "C(f_system) + C(city)"
    y = dm["y"].to_numpy(float)

    def r2(terms):
        f_ = "y ~ " + fixed + ("" if not terms else " + " + " + ".join(terms))
        return smf.ols(f_, dm).fit().rsquared

    names = list(blocks)
    full = r2(sum(blocks.values(), []))
    base_r2 = r2([])
    lmg = {n: 0.0 for n in names}
    perms = list(itertools.permutations(names))
    for order in perms:
        cur = []
        prev = base_r2
        for n in order:
            cur += blocks[n]
            now = r2(cur)
            lmg[n] += now - prev
            prev = now
    for n in names:
        lmg[n] /= len(perms)
    print(f"  model R² (OLS, city and functional-class fixed effects) = {full:.4f}")
    print(f"  fixed effects alone R² = {base_r2:.4f}")
    print(f"  {'block':<26}{'LMG share of R²':>18}{'as % of model R²':>20}")
    for n in names:
        print(f"  {n:<26}{lmg[n]:>18.4f}{100*lmg[n]/full:>19.2f}%")
        rows.append({"check": "lmg", "block": n, "share": lmg[n],
                     "pct_of_model_r2": 100*lmg[n]/full, "model_r2": full})
    ratio = lmg["density and land use"] / lmg["configuration"] if lmg["configuration"] else np.nan
    print(f"\n  density and land use explain {ratio:.1f}× what configuration does.")
    print(f"  Method: R² is the OLS coefficient of determination on the fixed-effects")
    print(f"  model; each block's share is its incremental R² averaged over all "
          f"{len(perms)} orderings.")

    # ------------------------------------------------------------------ C
    print(f"\n{'='*96}\nC. OSM VINTAGE — does the estimate hold in fabric that predates the "
          f"outcome?\n{'='*96}")
    print(f"  {'restriction':<40}{'n':>9}{'β':>10}{'SE':>9}{'p':>9}")
    for lab, mask in (
        ("all segments", pd.Series(True, index=d.index)),
        ("catchment median year built ≤ 2000", d["median_year_structure_built"] <= 2000),
        ("catchment median year built ≤ 1990", d["median_year_structure_built"] <= 1990),
    ):
        g = d[mask.fillna(False)]
        if len(g) < 500:
            continue
        rr = fit(g, f"y ~ {base} + C(city) + p1")
        if rr is None:
            continue
        print(f"  {lab:<40}{len(g):>9,}{rr.params['p1']:>+10.4f}{rr.bse['p1']:>9.4f}"
              f"{rr.pvalues['p1']:>9.4f}")
        rows.append({"check": "vintage", "restriction": lab, "n": len(g),
                     "beta": rr.params["p1"], "p": rr.pvalues["p1"]})
    for c in ("charlotte", "phoenix"):
        g = d[(d.city == c) & (d["median_year_structure_built"] <= 2000)]
        if len(g) < 200:
            print(f"  {c}, pre-2000 fabric: only {len(g)} segments — not estimated")
            continue
        rr = fit(g, f"y ~ {base} + p1")
        if rr is not None:
            print(f"  {c + ', pre-2000 fabric':<40}{len(g):>9,}"
                  f"{rr.params['p1']:>+10.4f}{rr.bse['p1']:>9.4f}{rr.pvalues['p1']:>9.4f}")
            rows.append({"check": "vintage_city", "city": c, "n": len(g),
                         "beta": rr.params["p1"], "p": rr.pvalues["p1"]})

    # ------------------------------------------------------------------ D
    print(f"\n{'='*96}\nD. COMPARATORS AND MODERATION, PER CITY AND EQUAL-WEIGHTED"
          f"\n{'='*96}")
    print("  P3 metrics oriented so that HIGHER = MORE CONNECTED "
          "(dead-end share and circuity sign-flipped):")
    print(f"  {'metric':<22}" + "".join(f"{c[:9]:>11}" for c in cities) + f"{'equal-w':>11}")
    for m, (lab, sgn) in P3.items():
        cells = []
        for c in cities:
            g = d[d.city == c].dropna(subset=[f"{m}_z"])
            rr = fit(g, f"y ~ {base} + p1 + {m}_z")
            cells.append(sgn * rr.params[f"{m}_z"] if rr is not None else np.nan)
        gg = d.dropna(subset=[f"{m}_z"])
        w = gg.groupby("city")["y"].transform(
            lambda s: len(gg) / (gg.city.nunique() * len(s)))
        mw = smf.wls(f"y ~ {base} + C(city) + p1 + {m}_z", gg, weights=w).fit()
        ew = sgn * mw.params[f"{m}_z"]
        print(f"  {lab:<22}" + "".join(f"{x:>+11.4f}" for x in cells) + f"{ew:>+11.4f}")
        rows.append({"check": "p3_percity", "metric": lab,
                     **{c: v for c, v in zip(cities, cells)}, "equal_weight": ew})
    print("  (a NEGATIVE value here would mean more connectivity, less traffic)")

    print(f"\n  P1 and the moderation, equal city weights:")
    dm2 = d.dropna(subset=["betw_z", "access_controlled"])
    w = dm2.groupby("city")["y"].transform(
        lambda s: len(dm2) / (dm2.city.nunique() * len(s)))
    mw = smf.wls(f"y ~ {base} + C(city) + p1 + access_controlled + betw_z"
                 f" + p1:access_controlled + p1:betw_z", dm2, weights=w).fit()
    for t in ["p1", "p1:access_controlled", "p1:betw_z"]:
        print(f"    {t:<24}{mw.params[t]:>+9.4f} (SE {mw.bse[t]:.4f})")
        rows.append({"check": "moderation_equalw", "term": t, "beta": mw.params[t],
                     "se": mw.bse[t]})
    print(f"  {'city':<16}{'P1 × access-controlled':>24}{'p':>9}{'n treated AC':>14}")
    for c in cities:
        g = dm2[dm2.city == c]
        rr = fit(g, f"y ~ {base} + p1 + access_controlled + p1:access_controlled")
        if rr is None or "p1:access_controlled" not in rr.params.index:
            continue
        nt = int(((g.p1 == 1) & (g.access_controlled == 1)).sum())
        print(f"  {c:<16}{rr.params['p1:access_controlled']:>+24.4f}"
              f"{rr.pvalues['p1:access_controlled']:>9.4f}{nt:>14,}")
        rows.append({"check": "moderation_percity", "city": c,
                     "beta": rr.params["p1:access_controlled"],
                     "p": rr.pvalues["p1:access_controlled"], "n_treated_ac": nt})

    # ------------------------------------------------------------------ E
    print(f"\n{'='*96}\nE. DIAGNOSTICS — spatial dependence and residuals, per city"
          f"\n{'='*96}")
    try:
        import geopandas as gpd
        from libpysal.weights import KNN
        from esda.moran import Moran
        from spreg import GM_Error_Het
        metric = cfg.config()["crs"]["metric"]
        print(f"  {'city':<16}{'Moran I (OLS resid)':>21}{'p':>9}"
              f"{'spatial-error β':>17}{'λ':>9}")
        for c in cities:
            g = d[d.city == c].copy()
            seg = gpd.read_parquet(paths.processed(c) / "segments.parquet").to_crs(metric)
            seg["segment_uid"] = c + "|" + seg["segment_uid"].astype(str)
            g = g.merge(seg[["segment_uid", "geometry"]], on="segment_uid", how="inner")
            pts = gpd.GeoDataFrame(geometry=[gm.interpolate(.5, normalized=True)
                                             for gm in g["geometry"]], crs=metric)
            w = KNN.from_dataframe(pts, k=8); w.transform = "r"
            ols = smf.ols(f"y ~ {base} + p1", g).fit()
            mi = Moran(ols.resid.to_numpy(), w)
            X = g[CTRL + ["p1"]].to_numpy(float)
            yv = g[["y"]].to_numpy(float)
            me = GM_Error_Het(yv, X, w=w, name_x=CTRL + ["p1"], name_y="log_aadt")
            b = float(me.betas.flatten()[len(CTRL) + 1])
            lam = float(me.betas.flatten()[-1])
            print(f"  {c:<16}{mi.I:>21.4f}{mi.p_sim:>9.4f}{b:>+17.4f}{lam:>9.3f}")
            rows.append({"check": "spatial_diag", "city": c, "moran_i": mi.I,
                         "moran_p": mi.p_sim, "sperr_beta": b, "lambda": lam})
    except Exception as e:
        print(f"  spatial diagnostics unavailable: {e}")

    print(f"\n  residual diagnostics on the pooled mixed model:")
    res = fit(d, f"y ~ {base} + C(city) + p1")
    if res is not None:
        r_ = res.resid
        from scipy import stats as st
        sk, ku = float(st.skew(r_)), float(st.kurtosis(r_))
        print(f"    residual skewness {sk:+.3f}, excess kurtosis {ku:+.3f}")
        print(f"    residual SD by city: " + ", ".join(
            f"{c} {d.assign(r=r_).groupby('city')['r'].std()[c]:.3f}" for c in cities))
        re_ = pd.Series({k: float(np.asarray(v).ravel()[0])
                         for k, v in res.random_effects.items()})
        print(f"    cell random effects: SD {re_.std():.3f}, skewness "
              f"{float(st.skew(re_)):+.3f}, |max| {re_.abs().max():.3f}")
        # influence: drop the 1% most extreme cells and refit
        drop = re_.abs().sort_values(ascending=False).head(max(1, len(re_)//100)).index
        rr = fit(d[~d.cell_id.isin(drop)], f"y ~ {base} + C(city) + p1")
        if rr is not None:
            print(f"    dropping the 1% highest-|effect| cells "
                  f"({len(drop)} cells): P1 {rr.params['p1']:+.4f} "
                  f"against {res.params['p1']:+.4f}")
            rows.append({"check": "influence", "beta_full": res.params["p1"],
                         "beta_trimmed": rr.params["p1"], "cells_dropped": len(drop),
                         "resid_skew": sk, "resid_kurtosis": ku})

    out = pd.DataFrame(rows)
    fp = paths.TABLES / "boston_variance_vintage.csv"
    out.to_csv(fp, index=False)
    print(f"\n  wrote {fp.relative_to(paths.ROOT)}")
    provenance.log_progress("05v_boston_variance_vintage",
                            "capacity test, LMG decomposition, vintage, diagnostics (D-091)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
