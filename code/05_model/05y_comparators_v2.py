#!/usr/bin/env python
"""Stage 5 — is the "generic metrics point the wrong way" result confounding? (D-097)

The panel's most substantively important objection, raised independently by two
reviewers from different directions:

  * CIRCULARITY. The striking positive coefficients come from whole-network cell
    metrics, computed on a network that INCLUDES the arterials supplying the outcome.
    A cell with a dense arterial grid scores high on cell intersection density because
    of the very roads whose AADT is the dependent variable.
  * CONFOUNDING. Our own discussion conceded the mechanism — "finely gridded areas are
    also busy areas" — which makes the positive sign a statement about centrality and
    activity rather than about measurement failure.

This script completes the 2x2 of constructions and adds the control the panel asked for:

                      whole network          local subgraph only
    cell level        contaminated           CLEAN, previously missing
    catchment level   (not used)             our construction

and re-runs every cell of it with and without job density in the control set. If the
positive sign survives a clean construction and an activity control, the measurement
claim is earned. If it does not, the claim must be restated as: cleanly constructed,
the generic metrics are NULL on arterial volume, and the positive association reported
under the regulated construction is confounding, not measurement failure.

Usage
-----
    uv run python code/05_model/05y_comparators_v2.py
"""
from __future__ import annotations
import argparse, pathlib, sys
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
import numpy as np, pandas as pd, statsmodels.formula.api as smf
from lib import cfg, paths, provenance

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from importlib import import_module
_p = import_module("05x_primary_v2") if False else None   # documented dependency only

R = 800
MIN_LEN = 400.0
CTRL_NOJOB = ["pop_density_km2_z", "lu_entropy_z", "dist_cbd_km_c_z",
              "dist_cbd_km_c_sq_z", "median_year_z", "through_lanes_z"]
CTRL = ["pop_density_km2_z", "job_density_km2_z"] + CTRL_NOJOB[1:]

CELL_WHOLE = {"int_density_all": "intersection density", "link_node_all": "link–node ratio",
              "pct_4way_all": "% four-way", "median_block_acres": "median block size"}
CELL_LOCAL = {"int_density_local": "intersection density",
              "link_node_local": "link–node ratio", "pct_4way_local": "% four-way"}
CATCH_LOCAL = {"local_int_density": "intersection density",
               "local_link_node_ratio": "link–node ratio",
               "local_street_density": "street density",
               "local_deadend_share": "dead-end share", "local_circuity": "circuity"}


def z(s):
    sd = s.std(ddof=0)
    return (s - s.mean()) / sd if sd and sd > 0 else s * 0.0


def load():
    fp = paths.DATA / "analysis__aadtfree" / f"analysis_pooled_r{R}.parquet"
    d = pd.read_parquet(fp)
    d = d[d.length_m >= MIN_LEN].copy()
    src = {"pop_density_km2_z": "pop_density_km2", "job_density_km2_z": "job_density_km2",
           "lu_entropy_z": "lu_entropy", "dist_cbd_km_c_z": "dist_cbd_km_c",
           "dist_cbd_km_c_sq_z": "dist_cbd_km_c_sq",
           "median_year_z": "median_year_structure_built",
           "through_lanes_z": "through_lanes"}
    for m in CATCH_LOCAL:
        src[f"{m}_z"] = m
    g = d.groupby("city")
    for dst, s in src.items():
        if s in d.columns:
            d[dst] = g[s].transform(z)
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


def block(d, metrics, label, ctrl, rows, tag):
    base = " + ".join(ctrl) + " + C(f_system)"
    print(f"\n  --- {label} ---")
    print(f"  {'metric':<24}{'UNCONDITIONAL':>24}{'CONDITIONAL on P1':>24}"
          f"{'P1 there':>12}{'n':>9}")
    for m, lab in metrics.items():
        col = f"{m}_z"
        if col not in d.columns:
            continue
        g = d.dropna(subset=[col])
        if len(g) < 500:
            continue
        ru = fit(g, f"y ~ {base} + C(city) + {col}")
        rc = fit(g, f"y ~ {base} + C(city) + p1 + {col}")
        if ru is None or rc is None:
            continue
        bu, pu = ru.params[col], ru.pvalues[col]
        bc, pc = rc.params[col], rc.pvalues[col]
        print(f"  {lab:<24}{bu:>+13.4f} (p={pu:5.3f}){bc:>+15.4f} (p={pc:5.3f})"
              f"{rc.params['p1']:>+12.4f}{len(g):>9,}")
        rows.append({"construction": label, "controls": tag, "metric": lab, "n": len(g),
                     "beta_uncond": bu, "p_uncond": pu, "beta_cond": bc, "p_cond": pc,
                     "p1_beta": rc.params["p1"], "p1_p": rc.pvalues["p1"]})


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    args = ap.parse_args()
    d = load()
    cities = list(cfg.cities().keys())
    print(f"Environment: {provenance.environment_stamp()}")
    print(f"Revised primary frame: n = {len(d):,}, {d.cell_id.nunique():,} cells")
    rows = []

    cm = pd.concat([pd.read_parquet(paths.processed(c) / "cell_metrics.parquet")
                    .assign(cell_id=lambda t, c=c: c + "|" + t["cell_id"].astype(str))
                    for c in cities], ignore_index=True)
    keep = ["cell_id"] + list(CELL_WHOLE) + list(CELL_LOCAL)
    d = d.merge(cm[[k for k in keep if k in cm.columns]], on="cell_id", how="left")
    for m in list(CELL_WHOLE) + list(CELL_LOCAL):
        if m in d.columns:
            d[f"{m}_z"] = d.groupby("city")[m].transform(z)

    print(f"\n{'='*98}\nA. THE 2x2 OF CONSTRUCTIONS, WITHOUT AN ACTIVITY CONTROL"
          f"\n{'='*98}")
    block(d, CELL_WHOLE, "cell level, WHOLE network (as regulated)", CTRL_NOJOB, rows,
          "no job density")
    block(d, CELL_LOCAL, "cell level, LOCAL subgraph only (the missing cell)",
          CTRL_NOJOB, rows, "no job density")
    block(d, CATCH_LOCAL, "catchment, local subgraph (our construction)", CTRL_NOJOB,
          rows, "no job density")

    print(f"\n{'='*98}\nB. THE SAME 2x2 WITH JOB DENSITY CONTROLLED (D-095)\n{'='*98}")
    block(d, CELL_WHOLE, "cell level, WHOLE network (as regulated)", CTRL, rows,
          "job density controlled")
    block(d, CELL_LOCAL, "cell level, LOCAL subgraph only (the missing cell)", CTRL,
          rows, "job density controlled")
    block(d, CATCH_LOCAL, "catchment, local subgraph (our construction)", CTRL, rows,
          "job density controlled")

    # ------------------------------------------------------------------ C
    print(f"\n{'='*98}\nC. HOW MUCH OF THE WHOLE-NETWORK METRIC IS THE ARTERIAL NETWORK?"
          f"\n{'='*98}")
    for m_all, m_loc, lab in (("int_density_all", "int_density_local",
                               "intersection density"),
                              ("link_node_all", "link_node_local", "link–node ratio"),
                              ("pct_4way_all", "pct_4way_local", "% four-way")):
        if m_all in d.columns and m_loc in d.columns:
            g = d.dropna(subset=[m_all, m_loc])
            r = g[[m_all, m_loc]].corr().iloc[0, 1]
            share = 1 - (g[m_loc].mean() / g[m_all].mean())
            print(f"  {lab:<24} corr(whole, local) = {r:+.3f}; "
                  f"{100*share:>5.1f}% of the whole-network value is not in the local "
                  f"subgraph")
            rows.append({"construction": "decomposition", "metric": lab,
                         "corr_whole_local": r, "share_not_local": share})
    print("  -> the wider that gap, the more the regulated metric is measuring the major")
    print("     road network itself — the network that supplies the outcome.")

    out = pd.DataFrame(rows)
    fp = paths.TABLES / "comparators_v2.csv"
    out.to_csv(fp, index=False)
    print(f"\n  wrote {fp.relative_to(paths.ROOT)}")
    provenance.log_progress("05y_comparators_v2",
                            "2x2 of comparator constructions with job density (D-097)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
