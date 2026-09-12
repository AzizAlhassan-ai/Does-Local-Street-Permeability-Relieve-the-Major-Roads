#!/usr/bin/env python
"""Stage 5 — re-estimate the primary specification on AADT-free analysis units (D-086).

The objection this answers is the sharpest one the panel raised. The primary unit is a
contiguous run of HPMS increments sharing AADT, functional class, lanes, access control,
ownership and facility type. AADT is the outcome, so unit length is a function of the
spatial variability of the dependent variable — and P1's detour cap is defined relative
to unit length, so P1 prevalence is mechanically a function of length. Conditioning on
realised length downstream does not undo an outcome-dependent construction of the units.

The AADT-free variant dissolves on the five exogenous attributes only and imposes a
fixed 0.5-mile cap, so unit boundaries carry no information from the outcome. AADT is
then the length-weighted mean of the increments inside each unit. Everything downstream
— the local network, the P1 route search, the catchment controls — is recomputed from
that frame. This script compares the two frames and re-estimates every quantity the
manuscript leads with.

Run the variant pipeline first:
    for c in denver portland phoenix boston wasatch_front charlotte; do
      for s in 02a_analysis_frame 02b_permeability 02d_through_routes; do
        PIPE_VARIANT=aadtfree uv run python code/02_network/$s.py --city $c; done
      for s in 03a_controls 03b_analysis_table; do
        PIPE_VARIANT=aadtfree uv run python code/03_conflate/$s.py --city $c; done; done
    PIPE_VARIANT=aadtfree uv run python code/03_conflate/03c_pool_cities.py

Usage
-----
    uv run python code/05_model/05r_aadtfree_units.py
"""
from __future__ import annotations
import argparse, os, pathlib, sys
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
import numpy as np, pandas as pd, statsmodels.formula.api as smf
from lib import cfg, paths, provenance

CTRL = ["pop_density_km2_z", "lu_entropy_z", "dist_cbd_km_c_z",
        "dist_cbd_km_c_sq_z", "median_year_z", "through_lanes_z"]


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
    # loglen_z is in the complete-case rule so that every table in the paper — primary,
    # length-controlled, and corridor-FE — is estimated on ONE sample (a referee counted
    # three different n for the corridor-FE estimate across the previous draft).
    d["loglen_z"] = d.groupby("city")["length_m"].transform(lambda s: z(np.log(s)))
    return d.dropna(subset=["y", "p1", "cell_id", "route_id", "f_system",
                            "loglen_z"] + CTRL).copy()


def fit(d, f, groups):
    try:
        return smf.mixedlm(f, d, groups=groups).fit(method="lbfgs", reml=True)
    except Exception as e:
        print(f"    !! {e}")
        return None


def load(variant: str, r: int) -> pd.DataFrame:
    suf = f"__{variant}" if variant else ""
    fp = paths.DATA / f"analysis{suf}" / f"analysis_pooled_r{r}.parquet"
    if not fp.exists():
        raise SystemExit(f"ERROR: {fp} missing")
    return pd.read_parquet(fp)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--radius", type=int, default=800)
    args = ap.parse_args()
    r = args.radius
    print(f"Environment: {provenance.environment_stamp()}")

    frames = {"primary (AADT in key)": prep(load("", r)),
              "AADT-free (D-086)": prep(load("aadtfree", r))}
    rows = []

    # ------------------------------------------------------------------ 1
    print(f"\n{'='*96}\n1. WHAT THE UNIT DEFINITION CHANGES\n{'='*96}")
    print(f"  {'frame':<24}{'n':>8}{'median len':>12}{'%<200m':>9}{'%P1':>8}"
          f"{'Boston share':>14}{'cells':>8}")
    for lab, d in frames.items():
        print(f"  {lab:<24}{len(d):>8,}{d.length_m.median():>11.0f}m"
              f"{100*(d.length_m < 200).mean():>8.1f}%{100*d.p1.mean():>7.1f}%"
              f"{100*(d.city == 'boston').mean():>13.1f}%{d.cell_id.nunique():>8,}")
        rows.append({"check": "frame", "frame": lab, "n": len(d),
                     "median_len_m": d.length_m.median(),
                     "pct_under_200m": 100*(d.length_m < 200).mean(),
                     "pct_p1": 100*d.p1.mean(),
                     "boston_share": 100*(d.city == "boston").mean()})
    print("\n  -> the AADT-free frame is the direct test of whether outcome-dependent")
    print("     unit boundaries manufactured the association. It also happens to cut")
    print("     Boston's share of the pooled sample, which was a separate objection.")

    # ------------------------------------------------------------------ 2
    base = " + ".join(CTRL) + " + C(f_system)"
    print(f"\n{'='*96}\n2. PRIMARY SPECIFICATION, PER CITY, BOTH FRAMES\n{'='*96}")
    print(f"  {'city':<16}{'primary β':>12}{'p':>9}{'  |':>4}"
          f"{'AADT-free β':>14}{'p':>9}{'n':>9}{'%P1':>8}")
    for c in sorted(frames["primary (AADT in key)"].city.unique()):
        out = {}
        for lab, d in frames.items():
            g = d[d.city == c]
            res = fit(g, f"y ~ {base} + p1", g["cell_id"])
            out[lab] = (res.params["p1"], res.pvalues["p1"], len(g), 100*g.p1.mean()) \
                if res is not None and "p1" in res.params.index else (np.nan,)*4
        a, b = out["primary (AADT in key)"], out["AADT-free (D-086)"]
        print(f"  {c:<16}{a[0]:>+12.4f}{a[1]:>9.4f}{'  |':>4}"
              f"{b[0]:>+14.4f}{b[1]:>9.4f}{b[2]:>9,}{b[3]:>7.1f}%")
        rows.append({"check": "per_city", "city": c, "beta_primary": a[0],
                     "p_primary": a[1], "beta_aadtfree": b[0], "p_aadtfree": b[1],
                     "n_aadtfree": b[2], "pct_p1_aadtfree": b[3]})

    # ------------------------------------------------------------------ 3
    print(f"\n{'='*96}\n3. POOLED AND WITHIN-CORRIDOR, BOTH FRAMES\n{'='*96}")
    for lab, d in frames.items():
        print(f"\n  --- {lab} ---")
        res = fit(d, f"y ~ {base} + C(city) + p1", d["cell_id"])
        if res is not None:
            b, se, p = res.params["p1"], res.bse["p1"], res.pvalues["p1"]
            print(f"  pooled + city FE      {b:>+9.4f} (SE {se:.4f}) p={p:.4f}"
                  f"  -> {100*(np.exp(b)-1):+.1f}% AADT")
            rows.append({"check": "pooled_cityfe", "frame": lab, "beta": b, "se": se,
                         "p": p, "n": len(d)})
        # corridor (route) fixed effects — the within-corridor estimate
        keep = d.groupby("route_id")["p1"].transform(lambda s: s.nunique() > 1)
        dd = d[keep].copy()
        if len(dd) > 500:
            m = smf.ols(f"y ~ {base} + C(route_id) + p1", dd).fit(
                cov_type="cluster", cov_kwds={"groups": dd["route_id"]})
            b, se, p = m.params["p1"], m.bse["p1"], m.pvalues["p1"]
            print(f"  corridor FE           {b:>+9.4f} (SE {se:.4f}) p={p:.4f}"
                  f"  -> {100*(np.exp(b)-1):+.1f}% AADT   n={len(dd):,}, "
                  f"{dd.route_id.nunique():,} corridors")
            rows.append({"check": "corridor_fe", "frame": lab, "beta": b, "se": se,
                         "p": p, "n": len(dd), "corridors": dd.route_id.nunique()})
        # equal city weights + wild cluster bootstrap-t
        w = d.groupby("city")["y"].transform(
            lambda s: len(d) / (d.city.nunique() * len(s)))
        f_ = f"y ~ {base} + C(city) + p1"
        m0 = smf.wls(f_, d, weights=w).fit()
        t_obs = m0.params["p1"] / m0.bse["p1"]
        m_r = smf.wls(f"y ~ {base} + C(city)", d, weights=w).fit()
        fit_r, res_r = m_r.fittedvalues.to_numpy(), m_r.resid.to_numpy()
        codes = pd.Categorical(d.city).codes
        rng = np.random.default_rng(20260803)
        B, cnt, tb = 999, 0, []
        dd2 = d.copy()
        for _ in range(B):
            signs = rng.choice([-1.0, 1.0], size=d.city.nunique())[codes]
            dd2["_yb"] = fit_r + res_r * signs
            mb = smf.wls(f_.replace("y ~", "_yb ~"), dd2, weights=w).fit()
            tt = mb.params["p1"] / mb.bse["p1"]
            tb.append(tt)
            cnt += abs(tt) >= abs(t_obs)
        p_wcb = (cnt + 1) / (B + 1)
        # bootstrap-t confidence interval (the SE/p reconciliation the panel asked for)
        q = np.quantile(np.abs(tb), 0.95)
        lo, hi = (m0.params["p1"] - q * m0.bse["p1"], m0.params["p1"] + q * m0.bse["p1"])
        print(f"  equal city weights    {m0.params['p1']:>+9.4f}  wild-bootstrap "
              f"p={p_wcb:.4f}, 95% bootstrap-t CI [{lo:+.3f}, {hi:+.3f}]")
        rows.append({"check": "equal_weight", "frame": lab, "beta": m0.params["p1"],
                     "p_wcb": p_wcb, "ci_lo": lo, "ci_hi": hi})

    out = pd.DataFrame(rows)
    fp = paths.TABLES / f"aadtfree_units_r{r}.csv"
    out.to_csv(fp, index=False)
    print(f"\n  wrote {fp.relative_to(paths.ROOT)}")
    provenance.log_progress("05r_aadtfree_units",
                            "primary re-estimated on AADT-free analysis units (D-086)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
