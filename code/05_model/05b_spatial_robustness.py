#!/usr/bin/env python
"""Stage 4b — spatial specification (D-021 requirement), variance partitioning (H3),
and the robustness sweep.

D-021 makes the spatial model PRIMARY, not a robustness check: catchments overlap
heavily (median 27 neighbours at r=800), so the multilevel standard errors are
optimistic and the H1 p-value from 05a cannot be taken at face value.

Sections
  1. Moran's I on M2 residuals            — is there spatial dependence at all?
  2. Spatial error model (same X as M2)   — H1 under a spatial specification
  3. Route-clustered OLS                  — dependence along a corridor
  4. Non-overlapping subsample            — D-021 requirement, honest effective N
  5. MAUP sweep across all four radii
  6. Alternative outcome (aadt per lane)
  7. Variance partitioning (H3/RQ3)

Usage
-----
    uv run python code/05_model/05b_spatial_robustness.py --city denver
"""

from __future__ import annotations

import argparse
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

import geopandas as gpd
import numpy as np
import pandas as pd
import statsmodels.api as sm
import statsmodels.formula.api as smf

from lib import cfg, paths, provenance

CTRL = ["pop_density_km2_z", "lu_entropy_z", "dist_cbd_km_c_z",
        "dist_cbd_km_c_sq_z", "median_year_z", "through_lanes_z"]


def z(s):
    sd = s.std(ddof=0)
    return (s - s.mean()) / sd if sd and sd > 0 else s * 0.0


def prep(t, outcome="log_aadt"):
    d = t.copy()
    d["access_controlled"] = d["access_control_"].isin([1, 2]).astype(float)
    d["betweenness_log"] = np.log10(d["arterial_betweenness"] + 1e-5)
    d["pop_density_km2_z"] = z(d["pop_density_km2"])
    d["lu_entropy_z"] = z(d["lu_entropy"])
    d["dist_cbd_km_c_z"] = z(d["dist_cbd_km_c"])
    d["dist_cbd_km_c_sq_z"] = z(d["dist_cbd_km_c_sq"])
    d["median_year_z"] = z(d["median_year_structure_built"])
    d["through_lanes_z"] = z(d["through_lanes"])
    # Stage 2R: P1 (binary substitutability) is now the primary predictor.
    d["gen_z"] = z(d["local_int_density"])
    d["perm_z"] = d["p1_any"].astype(float)
    d["betw_z"] = z(d["betweenness_log"])
    d["y"] = np.log(d[outcome]) if outcome == "aadt_per_lane" else d[outcome]
    need = ["y", "perm_z", "gen_z", "betw_z", "access_controlled", "cell_id",
            "route_id", "f_system"] + CTRL
    return d.dropna(subset=need).copy()


def design(d, with_perm=True):
    X = pd.get_dummies(d["f_system"].astype(int).astype(str), prefix="fs",
                       drop_first=True).astype(float)
    for c in CTRL:
        X[c] = d[c].values
    if with_perm:
        X["perm_z"] = d["perm_z"].values
    return X


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--city", default=None)
    args = ap.parse_args()
    conf = cfg.config()
    city = args.city or conf["project"]["pilot_city"]
    primary = conf["catchment"]["primary_radius_m"]
    radii = conf["catchment"]["radii_m"]

    print(f"Environment: {provenance.environment_stamp()}")
    t = pd.read_parquet(paths.ANALYSIS / f"analysis_table_r{primary}.parquet")
    d = prep(t)
    print(f"City: {city} | r={primary} m | n={len(d):,}")

    # geometry for spatial weights
    seg = gpd.read_parquet(paths.processed(city) / "segments.parquet").to_crs(
        conf["crs"]["metric"])
    mid = gpd.GeoDataFrame(
        seg[["segment_uid"]],
        geometry=[g.interpolate(0.5, normalized=True) for g in seg.geometry],
        crs=conf["crs"]["metric"])
    d = d.merge(mid, on="segment_uid", how="left")
    gd = gpd.GeoDataFrame(d, geometry="geometry", crs=conf["crs"]["metric"])

    fml = "y ~ " + " + ".join(CTRL) + " + C(f_system) + perm_z"

    # ---------- 1. Moran's I on M2 residuals ----------
    print(f"\n{'='*72}\n1. Spatial dependence in the M2 residuals\n{'='*72}")
    ols = smf.ols(fml, d).fit()
    from libpysal.weights import KNN
    from esda.moran import Moran
    W = KNN.from_dataframe(gd, k=8)
    W.transform = "r"
    mi = Moran(ols.resid.values, W)
    print(f"  Moran's I = {mi.I:+.4f}  (E[I] = {mi.EI:+.4f})  z = {mi.z_norm:+.2f}, "
          f"p = {mi.p_norm:.2e}")
    print("  -> residuals are spatially autocorrelated; OLS/MixedLM SEs are optimistic"
          if mi.p_norm < 0.05 else "  -> no significant residual autocorrelation")

    # ---------- 2. Spatial error model ----------
    print(f"\n{'='*72}\n2. Spatial error model (same specification as M2)\n{'='*72}")
    from spreg import GM_Error_Het
    X = design(d)
    y = d["y"].values.reshape(-1, 1)
    se_mod = GM_Error_Het(y, X.values, w=W, name_x=list(X.columns), name_y="log_aadt")
    names = list(X.columns)
    idx = names.index("perm_z") + 1        # +1 for the constant
    b = float(se_mod.betas[idx][0]); s = float(se_mod.std_err[idx])
    zsc = b / s
    from scipy import stats as st
    pv = 2 * (1 - st.norm.cdf(abs(zsc)))
    print(f"  perm_z = {b:+.4f} (SE {s:.4f}), z = {zsc:+.2f}, p = {pv:.4f}")
    print(f"  95% CI [{b-1.96*s:+.4f}, {b+1.96*s:+.4f}]  -> "
          f"{100*(np.exp(b)-1):+.2f}% AADT per sd")
    print(f"  lambda (spatial error) = {float(se_mod.betas[-1][0]):+.4f}")
    ml = smf.mixedlm(fml, d, groups=d["cell_id"]).fit(method="lbfgs", reml=True)
    print(f"\n  comparison of the H1 coefficient:")
    print(f"    MixedLM (05a)      {ml.params['perm_z']:+.4f}  SE {ml.bse['perm_z']:.4f}"
          f"  p {ml.pvalues['perm_z']:.4f}")
    print(f"    OLS                {ols.params['perm_z']:+.4f}  SE {ols.bse['perm_z']:.4f}"
          f"  p {ols.pvalues['perm_z']:.4f}")
    print(f"    Spatial error      {b:+.4f}  SE {s:.4f}  p {pv:.4f}")

    # ---------- 3. Route-clustered OLS ----------
    print(f"\n{'='*72}\n3. OLS with route-clustered standard errors\n{'='*72}")
    cl = smf.ols(fml, d).fit(cov_type="cluster",
                             cov_kwds={"groups": d["route_id"]})
    print(f"  perm_z = {cl.params['perm_z']:+.4f} (SE {cl.bse['perm_z']:.4f}), "
          f"p = {cl.pvalues['perm_z']:.4f}   [{d.route_id.nunique():,} clusters]")

    # ---------- 4. Non-overlapping subsample ----------
    print(f"\n{'='*72}\n4. Non-overlapping catchment subsample (D-021)\n{'='*72}")
    cat = gpd.read_parquet(paths.processed(city) / f"catchments_r{primary}.parquet"
                           ).to_crs(conf["crs"]["metric"])
    cat = cat[cat.segment_uid.isin(d.segment_uid)].reset_index(drop=True)
    sidx = cat.sindex
    chosen, blocked = [], set()
    order = np.argsort(-d.set_index("segment_uid").loc[cat.segment_uid, "y"].values)
    for i in order:
        if i in blocked:
            continue
        chosen.append(i)
        for j in sidx.query(cat.geometry.iloc[i], predicate="intersects"):
            if j != i:
                blocked.add(int(j))
    keep = set(cat.segment_uid.iloc[chosen])
    dn = d[d.segment_uid.isin(keep)].copy()
    print(f"  greedy non-overlapping set: {len(dn):,} of {len(d):,} units "
          f"({len(dn)/len(d):.1%}) — this is the honest effective sample size")
    if len(dn) > 40:
        on = smf.ols(fml, dn).fit()
        print(f"  perm_z = {on.params['perm_z']:+.4f} (SE {on.bse['perm_z']:.4f}), "
              f"p = {on.pvalues['perm_z']:.4f}")

    # ---------- 5. MAUP sweep ----------
    print(f"\n{'='*72}\n5. MAUP sweep — H1 across catchment radii\n{'='*72}")
    rows = []
    for r in radii:
        fp = paths.ANALYSIS / f"analysis_table_r{r}.parquet"
        if not fp.exists():
            continue
        dr = prep(pd.read_parquet(fp))
        m = smf.mixedlm(fml, dr, groups=dr["cell_id"]).fit(method="lbfgs", reml=True)
        rows.append({"radius_m": r, "n": len(dr), "beta": m.params["perm_z"],
                     "se": m.bse["perm_z"], "p": m.pvalues["perm_z"],
                     "pct_per_sd": 100 * (np.exp(m.params["perm_z"]) - 1)})
    sweep = pd.DataFrame(rows)
    print(sweep.to_string(index=False, float_format=lambda x: f"{x:.4f}"))

    # ---------- 6. Alternative outcome ----------
    print(f"\n{'='*72}\n6. Co-primary outcome: log(AADT per lane) (D-004)\n{'='*72}")
    dl = prep(t, "aadt_per_lane")
    fml_l = "y ~ " + " + ".join([c for c in CTRL if c != "through_lanes_z"]) \
            + " + C(f_system) + perm_z"
    ml2 = smf.mixedlm(fml_l, dl, groups=dl["cell_id"]).fit(method="lbfgs", reml=True)
    print(f"  perm_z = {ml2.params['perm_z']:+.4f} (SE {ml2.bse['perm_z']:.4f}), "
          f"p = {ml2.pvalues['perm_z']:.4f}")
    print("  (through_lanes dropped — it is the denominator of this outcome)")

    # ---------- 7. Variance partitioning (H3) ----------
    print(f"\n{'='*72}\n7. Variance partitioning — RQ3 / H3\n{'='*72}")
    base = smf.ols("y ~ C(f_system)", d).fit()
    conf_only = smf.ols("y ~ C(f_system) + perm_z", d).fit()
    ctrl_only = smf.ols("y ~ C(f_system) + " + " + ".join(CTRL), d).fit()
    gen_only = smf.ols("y ~ C(f_system) + gen_z", d).fit()
    full = smf.ols(fml, d).fit()
    r2 = {"design only (f_system)": base.rsquared,
          "+ P1 substitutability only": conf_only.rsquared,
          "+ P3 generic connectivity only": gen_only.rsquared,
          "+ density/land use only": ctrl_only.rsquared,
          "full": full.rsquared}
    for k, v in r2.items():
        print(f"  R² {k:28s} {v:.4f}")
    uniq_conf = full.rsquared - ctrl_only.rsquared
    uniq_ctrl = full.rsquared - conf_only.rsquared
    common = (conf_only.rsquared - base.rsquared) + (ctrl_only.rsquared - base.rsquared) \
             - (full.rsquared - base.rsquared)
    print(f"\n  unique to configuration   : {uniq_conf:.4f}")
    print(f"  unique to density/land use: {uniq_ctrl:.4f}")
    print(f"  shared                    : {common:.4f}")
    print(f"  -> configuration explains {uniq_conf/full.rsquared:.2%} of the model's "
          f"explained variance uniquely" if full.rsquared > 0 else "")

    sweep.to_csv(paths.TABLES / "h1_maup_sweep.csv", index=False)
    pd.DataFrame([{
        "spec": "MixedLM", "beta": ml.params["perm_z"], "se": ml.bse["perm_z"],
        "p": ml.pvalues["perm_z"]},
        {"spec": "OLS", "beta": ols.params["perm_z"], "se": ols.bse["perm_z"],
         "p": ols.pvalues["perm_z"]},
        {"spec": "Spatial error", "beta": b, "se": s, "p": pv},
        {"spec": "OLS route-clustered", "beta": cl.params["perm_z"],
         "se": cl.bse["perm_z"], "p": cl.pvalues["perm_z"]},
    ]).to_csv(paths.TABLES / "h1_specification_comparison.csv", index=False)
    print(f"\n  wrote outputs/tables/h1_maup_sweep.csv and "
          f"h1_specification_comparison.csv")
    provenance.log_progress("05b_spatial_robustness",
                            f"{city}: spatial + robustness sweep for H1")
    print("\nStage 4b complete.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
