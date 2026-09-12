#!/usr/bin/env python
"""Stage 5 — ablation of P1's four restrictions (D-088).

We claim P1's contribution is not the idea of an alternative path but its restriction:
local-only, endpoint-anchored, detour-capped, and computed per arterial segment. A
referee pointed out, correctly, that the constant sweeps vary parameters WITHIN those
restrictions and never remove one. This removes them one at a time and re-estimates the
primary specification on each.

  full        all four restrictions (the primary measure)
  -local      the route may use major roads (the segment's own carriageway excluded)
  -cap        endpoint-anchored and local-only, but no detour cap
  -span       no requirement that the route span half the segment
  -segment    the same computation aggregated to the 1 mi² cell and read off as an
              areal measure — which is what the standard metrics are

Prerequisite (per city, at r = 800 m):
    PIPE_VARIANT=ablall   ... 02d_through_routes.py --graph all
    PIPE_VARIANT=ablnocap ... 02d_through_routes.py --detour 99
    PIPE_VARIANT=ablnospan... 02d_through_routes.py --no-span

Usage
-----
    uv run python code/05_model/05t_ablation.py
"""
from __future__ import annotations
import argparse, pathlib, sys
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
import numpy as np, pandas as pd, statsmodels.formula.api as smf
from lib import cfg, paths, provenance

CTRL = ["pop_density_km2_z", "lu_entropy_z", "dist_cbd_km_c_z",
        "dist_cbd_km_c_sq_z", "median_year_z", "through_lanes_z"]
R = 800
VARIANTS = [("full", "", "all four restrictions"),
            ("minus_local", "ablall", "route may use major roads"),
            ("minus_cap", "ablnocap", "no detour cap"),
            ("minus_span", "ablnospan", "no minimum-span requirement")]


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
    d["y"] = d["log_aadt"]
    d["p1"] = d["p1_any"].astype(float)
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
    conf = cfg.config()
    cities = list(cfg.cities().keys())
    d0 = prep(pd.read_parquet(paths.ANALYSIS / f"analysis_pooled_r{R}.parquet"))
    base = " + ".join(CTRL) + " + C(f_system)"
    print(f"Environment: {provenance.environment_stamp()}\nbase sample n = {len(d0):,}")
    rows = []

    print(f"\n{'='*104}\nABLATION OF P1'S RESTRICTIONS — pooled, city FE, primary controls"
          f"\n{'='*104}")
    print(f"  {'specification':<34}{'% treated':>11}{'β':>10}{'SE':>9}{'p':>9}"
          f"{'% AADT':>9}   per-city sig.")

    for name, variant, note in VARIANTS:
        d = d0.copy()
        if variant:
            parts = []
            for c in cities:
                fp = (paths.PROCESSED / f"{c}__{variant}" /
                      f"through_routes_r{R}.parquet")
                if not fp.exists():
                    print(f"    !! missing {fp}")
                    continue
                t = pd.read_parquet(fp)[["segment_uid", "p1_any"]]
                t["segment_uid"] = c + "|" + t["segment_uid"].astype(str)
                parts.append(t)
            alt = pd.concat(parts, ignore_index=True).rename(columns={"p1_any": "_alt"})
            d = d.drop(columns=["_alt"], errors="ignore").merge(
                alt, on="segment_uid", how="left")
            d = d.dropna(subset=["_alt"])
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
        print(f"  {name + ' (' + note + ')':<34}{100*d.p1.mean():>10.1f}%{b:>+10.4f}"
              f"{se:>9.4f}{p:>9.4f}{100*(np.exp(b)-1):>8.1f}%   {nsig}/6")
        rows.append({"spec": name, "note": note, "n": len(d), "pct_treated": 100*d.p1.mean(),
                     "beta": b, "se": se, "p": p, "pct_aadt": 100*(np.exp(b)-1),
                     "n_cities_sig": nsig})

    # ---- minus per-segment: the same computation read as an areal measure --------
    d = d0.copy()
    cellmean = d.groupby("cell_id")["p1"].transform("mean")
    d["p1cell_z"] = d.groupby("city").apply(
        lambda g: z(cellmean.loc[g.index]), include_groups=False).droplevel(0)
    res = fit(d, f"y ~ {base} + C(city) + p1cell_z")
    if res is not None:
        b, se, p = res.params["p1cell_z"], res.bse["p1cell_z"], res.pvalues["p1cell_z"]
        print(f"  {'minus_segment (cell aggregate)':<34}{'—':>11}{b:>+10.4f}{se:>9.4f}"
              f"{p:>9.4f}{100*(np.exp(b)-1):>8.1f}%   (per SD)")
        rows.append({"spec": "minus_segment", "note": "cell-level areal aggregate",
                     "n": len(d), "beta": b, "se": se, "p": p,
                     "pct_aadt": 100*(np.exp(b)-1)})
        # and conditional on the per-segment measure, which is the informative contrast
        res2 = fit(d, f"y ~ {base} + C(city) + p1 + p1cell_z")
        if res2 is not None:
            print(f"    conditional on segment-level P1: cell aggregate "
                  f"{res2.params['p1cell_z']:+.4f} (p={res2.pvalues['p1cell_z']:.4f}), "
                  f"segment P1 {res2.params['p1']:+.4f} (p={res2.pvalues['p1']:.4f})")
            rows.append({"spec": "minus_segment_conditional",
                         "note": "cell aggregate | segment P1",
                         "beta": res2.params["p1cell_z"], "p": res2.pvalues["p1cell_z"],
                         "beta_p1": res2.params["p1"], "p_p1": res2.pvalues["p1"]})

    out = pd.DataFrame(rows)
    fp = paths.TABLES / "p1_ablation.csv"
    out.to_csv(fp, index=False)
    print(f"\n  wrote {fp.relative_to(paths.ROOT)}")
    provenance.log_progress("05t_ablation", "ablation of P1's four restrictions (D-088)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
