#!/usr/bin/env python
"""Stage 5 — Layer 2: our segment-level design restricted to Choi & Ewing's sample.

Layer 1 (05f) ran THEIR design on our data. This runs OUR design on THEIR sample:
the per-city H1 models of 05c, restricted to segments whose 1 mi² cell passes the
Choi & Ewing eligibility filters already computed in 02e (activity density >=
1500/sq mi AND major road >= 2 miles; their third filter — campus/airport/
industrial — is not applied, as recorded in D-063).

Answers the reviewer question "is your different answer just a different sample?"
If per-city H1 holds on the eligible subsample, the P1 result is not an artefact
of including the low-density fringe their filters remove.

Model, controls, z-scoring and fitting are identical to 05c; the ONLY change is
the sample restriction.

Usage
-----
    uv run python code/05_model/05g_ce_eligible.py
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
    """Identical to 05c.prep — standardise within city, build model columns."""
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

    # ---- eligibility flags from 02e, namespaced like the pooled table ----------
    elig = []
    for c in cfg.cities():
        cm_fp = paths.processed(c) / "cell_metrics.parquet"
        if not cm_fp.exists():
            print(f"  !! cell_metrics.parquet missing for {c}")
            continue
        cm = pd.read_parquet(cm_fp, columns=["cell_id", "ce_eligible"])
        cm["cell_id"] = c + "|" + cm["cell_id"].astype(str)
        elig.append(cm)
    elig = pd.concat(elig, ignore_index=True)
    print(f"cells with eligibility flags: {len(elig):,} "
          f"({int(elig.ce_eligible.sum()):,} eligible, {elig.ce_eligible.mean():.1%})")

    raw = raw.merge(elig, on="cell_id", how="left", validate="m:1")
    n_unmatched = int(raw["ce_eligible"].isna().sum())
    if n_unmatched:
        print(f"  segments in cells with no metrics row (no local/major network "
              f"in cell): {n_unmatched:,} — treated as ineligible")
    raw["ce_eligible"] = raw["ce_eligible"].fillna(False)

    d_full = prep(raw)
    d_res = prep(raw[raw.ce_eligible])
    print(f"\nfull model sample:      {len(d_full):,} segments, "
          f"{d_full.cell_id.nunique():,} cells")
    print(f"CE-eligible subsample:  {len(d_res):,} segments, "
          f"{d_res.cell_id.nunique():,} cells "
          f"({len(d_res)/len(d_full):.1%} of segments)")
    print(d_res.groupby('city').agg(n=('y', 'size'),
                                    pct_P1=('p1', lambda s: 100 * s.mean())).round(1)
          .to_string())

    base = " + ".join(CTRL) + " + C(f_system)"
    rows = []

    print(f"\n{'='*74}\nPER-CITY H1 on the Choi & Ewing-eligible subsample vs full"
          f"\n{'='*74}")
    print(f"  {'city':<14}{'n elig':>8}{'beta elig':>11}{'p':>9}"
          f"{'n full':>8}{'beta full':>11}{'p':>9}")
    for c in sorted(d_res.city.unique()):
        ge = d_res[d_res.city == c]
        gf = d_full[d_full.city == c]
        out = {"city": c}
        for tag, g in (("elig", ge), ("full", gf)):
            if len(g) < 100 or g.f_system.nunique() < 2:
                out[f"beta_{tag}"] = np.nan
                continue
            res = fit(g, f"y ~ {base} + p1", g["cell_id"])
            if res is not None and "p1" in res.params.index:
                out[f"n_{tag}"] = len(g)
                out[f"cells_{tag}"] = g.cell_id.nunique()
                out[f"beta_{tag}"] = res.params["p1"]
                out[f"se_{tag}"] = res.bse["p1"]
                out[f"p_{tag}"] = res.pvalues["p1"]
                out[f"pct_{tag}"] = 100 * (np.exp(res.params["p1"]) - 1)
        rows.append(out)
        print(f"  {c:<14}{out.get('n_elig', float('nan')):>8,.0f}"
              f"{out.get('beta_elig', float('nan')):>11.4f}"
              f"{out.get('p_elig', float('nan')):>9.4f}"
              f"{out.get('n_full', float('nan')):>8,.0f}"
              f"{out.get('beta_full', float('nan')):>11.4f}"
              f"{out.get('p_full', float('nan')):>9.4f}")

    # pooled + city FE on the subsample, mirroring 05c section 2
    print(f"\npooled + city FE, eligible subsample:")
    res_fe = fit(d_res, f"y ~ {base} + C(city) + p1", d_res["cell_id"])
    if res_fe is not None and "p1" in res_fe.params.index:
        b, se, p = (res_fe.params["p1"], res_fe.bse["p1"], res_fe.pvalues["p1"])
        print(f"  p1 = {b:+.4f} (SE {se:.4f}), p = {p:.4g}, "
              f"{100*(np.exp(b)-1):+.1f}% AADT")
        rows.append({"city": "pooled + city FE", "n_elig": len(d_res),
                     "cells_elig": d_res.cell_id.nunique(), "beta_elig": b,
                     "se_elig": se, "p_elig": p,
                     "pct_elig": 100 * (np.exp(b) - 1)})

    out = pd.DataFrame(rows)
    fpo = paths.TABLES / f"h1_ce_eligible_r{r}.csv"
    out.to_csv(fpo, index=False)
    print(f"\n  wrote {fpo.relative_to(paths.ROOT)}")
    provenance.log_progress("05g_ce_eligible",
                            f"Layer 2: per-city H1 on CE-eligible cells at r={r} m")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
