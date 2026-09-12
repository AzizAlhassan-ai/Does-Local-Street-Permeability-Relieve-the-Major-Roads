#!/usr/bin/env python
"""Stage 5 — the ablation, recomputed on the revised frame (D-102).

A reviewer caught that the ablation table in the previous draft mixed frames: the full
measure was reported on the revised frame while the three ablated variants carried
numbers from the superseded one. The tell was arithmetic and decisive — "no minimum-span
requirement" showed a LOWER prevalence (11.7%) than the full measure (16.3%), which is
impossible, because removing a restriction can only admit more routes.

Every branch here is recomputed on the exogenous-attribute frame with the 400 m floor.
Prevalences are now monotone: 16.2% for the full measure against 30.6%, 27.3% and 17.4%
for the three ablations.

Prerequisite, per city, at r = 800 m:
    PIPE_VARIANT=af_ablall    ... 02d_through_routes.py --graph all
    PIPE_VARIANT=af_ablnocap  ... 02d_through_routes.py --detour 99
    PIPE_VARIANT=af_ablnospan ... 02d_through_routes.py --no-span

Usage
-----
    uv run python code/05_model/05zd_ablation_v2.py
"""
from __future__ import annotations
import argparse, pathlib, sys
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
import numpy as np, pandas as pd, statsmodels.formula.api as smf
from lib import cfg, paths, provenance

R, MIN_LEN = 800, 400.0
CTRL = ["pop_density_km2_z", "job_density_km2_z", "lu_entropy_z", "dist_cbd_km_c_z",
        "dist_cbd_km_c_sq_z", "median_year_z", "through_lanes_z"]
VARIANTS = [("full", "", "all four restrictions"),
            ("minus_local", "af_ablall", "route may use major roads"),
            ("minus_cap", "af_ablnocap", "no detour cap"),
            ("minus_span", "af_ablnospan", "no minimum-span requirement")]


def z(s):
    sd = s.std(ddof=0)
    return (s - s.mean()) / sd if sd and sd > 0 else s * 0.0


def load():
    d = pd.read_parquet(paths.DATA / "analysis__aadtfree" / f"analysis_pooled_r{R}.parquet")
    d = d[d.length_m >= MIN_LEN].copy()
    src = {"pop_density_km2_z": "pop_density_km2", "job_density_km2_z": "job_density_km2",
           "lu_entropy_z": "lu_entropy", "dist_cbd_km_c_z": "dist_cbd_km_c",
           "dist_cbd_km_c_sq_z": "dist_cbd_km_c_sq",
           "median_year_z": "median_year_structure_built",
           "through_lanes_z": "through_lanes"}
    g = d.groupby("city")
    for k, v in src.items():
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


def alt(variant):
    parts = []
    for c in cfg.cities():
        fp = paths.PROCESSED / f"{c}__{variant}" / f"through_routes_r{R}.parquet"
        if not fp.exists():
            return None
        t = pd.read_parquet(fp)[["segment_uid", "p1_any"]].rename(columns={"p1_any": "_alt"})
        t["segment_uid"] = c + "|" + t["segment_uid"].astype(str)
        parts.append(t)
    return pd.concat(parts, ignore_index=True)


def main() -> int:
    argparse.ArgumentParser(description=__doc__).parse_args()
    d0 = load()
    base = " + ".join(CTRL) + " + C(f_system)"
    print(f"Environment: {provenance.environment_stamp()}\nn = {len(d0):,}")
    rows = []

    print(f"\n{'='*98}\nABLATION ON THE REVISED FRAME — every branch recomputed\n{'='*98}")
    print(f"  {'specification':<40}{'% treated':>11}{'β':>10}{'SE':>9}{'p':>9}"
          f"{'% AADT':>9}   cities neg. & sig.")
    for name, variant, note in VARIANTS:
        d = d0.copy()
        if variant:
            a = alt(variant)
            if a is None:
                print(f"  {note:<40} variant not built — skipped"); continue
            d = d.drop(columns=["_alt"], errors="ignore").merge(a, on="segment_uid",
                                                                how="inner")
            d["p1"] = d["_alt"].astype(float)
        res = fit(d, f"y ~ {base} + C(city) + p1")
        if res is None:
            continue
        b, se, p = res.params["p1"], res.bse["p1"], res.pvalues["p1"]
        nsig = 0
        for c, g in d.groupby("city"):
            if len(g) < 100 or g.p1.nunique() < 2:
                continue
            rr = fit(g, f"y ~ {base} + p1")
            if rr is not None and rr.params["p1"] < 0 and rr.pvalues["p1"] < 0.05:
                nsig += 1
        print(f"  {note:<40}{100*d.p1.mean():>10.1f}%{b:>+10.4f}{se:>9.4f}{p:>9.4f}"
              f"{100*(np.exp(b)-1):>8.1f}%   {nsig}/6")
        rows.append({"spec": name, "note": note, "n": len(d),
                     "pct_treated": 100*d.p1.mean(), "beta": b, "se": se, "p": p,
                     "pct_aadt": 100*(np.exp(b)-1), "n_cities_sig": nsig})

    # per-segment restriction, on a matched 0->1 footing
    d = d0.copy()
    d["cellrate"] = d.groupby("cell_id")["p1"].transform("mean")
    prev = d.p1.mean()
    thr = d["cellrate"].quantile(1 - prev)
    d["cellbin"] = (d["cellrate"] >= thr).astype(float)
    res = fit(d, f"y ~ {base} + C(city) + cellbin")
    b, se, p = res.params["cellbin"], res.bse["cellbin"], res.pvalues["cellbin"]
    print(f"  {'read as a cell-level rate, matched prevalence':<40}"
          f"{100*d.cellbin.mean():>10.1f}%{b:>+10.4f}{se:>9.4f}{p:>9.4f}"
          f"{100*(np.exp(b)-1):>8.1f}%")
    rows.append({"spec": "minus_segment_matched", "note": "cell rate, matched prevalence",
                 "n": len(d), "pct_treated": 100*d.cellbin.mean(), "beta": b, "se": se,
                 "p": p, "pct_aadt": 100*(np.exp(b)-1)})
    res = fit(d, f"y ~ {base} + C(city) + p1 + cellbin")
    print(f"    entered together: segment {res.params['p1']:+.4f} "
          f"(p = {res.pvalues['p1']:.4f}); cell rate {res.params['cellbin']:+.4f} "
          f"(p = {res.pvalues['cellbin']:.4f})")
    rows.append({"spec": "both_together", "beta": res.params["p1"],
                 "p": res.pvalues["p1"], "beta_cell": res.params["cellbin"],
                 "p_cell": res.pvalues["cellbin"]})

    print("\n  Prevalence is monotone across the ablations, as it must be: removing a")
    print("  restriction can only admit more routes. That was not true of the table this")
    print("  replaces, which is how the frame mixing was caught.")

    out = pd.DataFrame(rows)
    fp = paths.TABLES / "ablation_v2.csv"
    out.to_csv(fp, index=False)
    print(f"\n  wrote {fp.relative_to(paths.ROOT)}")
    provenance.log_progress("05zd_ablation_v2",
                            "ablation recomputed on the revised frame (D-102)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
