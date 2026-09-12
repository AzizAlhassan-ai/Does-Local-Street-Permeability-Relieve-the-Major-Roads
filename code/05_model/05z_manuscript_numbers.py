#!/usr/bin/env python
"""Stage 5 — collect every number the manuscript quotes, in one place.

The draft's rule is that no number may be written without checking it against a
logged value. This prints the current value of each quoted quantity, grouped by
the table or passage it belongs to, so a revision pass can be checked against one
output rather than a dozen CSVs.

Usage
-----
    uv run python code/05_model/05z_manuscript_numbers.py
"""

from __future__ import annotations

import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

import numpy as np
import pandas as pd

from lib import cfg, paths

T = paths.TABLES


def show(name, fp, cols=None, fmt=None):
    if not fp.exists():
        print(f"  [MISSING] {fp.name}")
        return None
    d = pd.read_csv(fp)
    print(f"\n--- {name}  ({fp.name}) ---")
    dd = d[cols] if cols else d
    with pd.option_context("display.width", 200, "display.max_columns", 40):
        print(dd.to_string(index=False, float_format=fmt or (lambda x: f"{x:.4f}")))
    return d


def main() -> int:
    r = cfg.config()["catchment"]["primary_radius_m"]
    print("=" * 90)
    print("MANUSCRIPT NUMBERS — current values")
    print("=" * 90)

    # ---- Table 1: descriptive profile -------------------------------------
    pooled = pd.read_parquet(paths.ANALYSIS / f"analysis_pooled_r{r}.parquet")
    print(f"\n--- TABLE 1: profile by city (n total = {len(pooled):,}) ---")
    t1 = pooled.groupby("city").agg(
        segments=("log_aadt", "size"),
        median_aadt=("aadt", "median"),
        pct_p1=("p1_any", lambda s: 100 * s.mean()),
        int_density=("local_int_density", "mean"),
        link_node=("local_link_node_ratio", "mean"),
        deadend=("local_deadend_share", "mean"),
        median_len_m=("length_m", "median"),
    ).round(2)
    print(t1.to_string())
    print(f"\n  TOTAL SEGMENTS: {len(pooled):,}")

    cells = []
    for c in cfg.cities():
        fp = paths.processed(c) / "cell_metrics.parquet"
        if fp.exists():
            cm = pd.read_parquet(fp)
            e = cm[cm.ce_eligible]
            cells.append({"city": c, "eligible_cells": len(e),
                          "int_density_sqmi": e.int_density_all.median(),
                          "block_acres": e.median_block_acres.median(),
                          "link_node": e.link_node_all.median(),
                          "pct_4way": e.pct_4way_all.median()})
    if cells:
        print("\n--- TABLE 1 (cell-level, eligible cells) ---")
        print(pd.DataFrame(cells).round(2).to_string(index=False))

    # ---- Table 3 / per-city H1 --------------------------------------------
    show("TABLE 3: per-city H1", T / f"multicity_h1_r{r}.csv",
         ["model", "n", "cells", "beta", "se", "p", "pct"])

    # ---- Layer 1 / Layer 2 -------------------------------------------------
    ps = T / "psm_choi_ewing_replication.csv"
    if ps.exists():
        d = pd.read_csv(ps)
        diff = d.study_log_aadt.mean() - d.control_log_aadt.mean()
        from scipy import stats as st
        tt = st.ttest_rel(d.study_log_aadt, d.control_log_aadt)
        print(f"\n--- TABLE 2: Layer 1 matched pairs ---")
        print(f"  pairs {len(d):,} | study mean log(AADT) {d.study_log_aadt.mean():.3f} "
              f"| control {d.control_log_aadt.mean():.3f}")
        print(f"  difference {diff:+.4f} -> {100*(np.exp(diff)-1):+.1f}% | "
              f"t = {tt.statistic:+.3f}, p = {tt.pvalue:.4f}")
        print(f"  by city: {d.city.value_counts().to_dict()}")

    show("Layer 2: CE-eligible subsample", T / f"h1_ce_eligible_r{r}.csv",
         ["city", "n_elig", "beta_elig", "p_elig", "n_full", "beta_full", "p_full"])

    # ---- reviewer checks ---------------------------------------------------
    rc = T / f"reviewer_checks_r{r}.csv"
    if rc.exists():
        d = pd.read_csv(rc)
        for chk, cols in [
            ("lanes_bracket", ["city", "beta_primary", "pct_primary", "beta_nolanes",
                               "pct_nolanes", "beta_neither", "pct_neither"]),
            ("length", ["city", "corr_p1_len", "corr_len_aadt", "median_len_m",
                        "beta_base", "beta_lenctrl", "beta_lenFE"]),
            ("p3_battery", ["metric", "n", "beta_alone", "p_alone", "beta_given_p1",
                            "p_given_p1", "pct_lo", "pct_hi"]),
            ("common_footing", ["predictor", "beta_raw", "beta_per_sd", "pct_per_sd"]),
            ("variance", ["form", "r2_full", "unique_config", "unique_controls", "ratio"]),
            ("2x2", ["group", "n_p1_0", "n_p1_1"]),
            ("betw_tercile", ["term", "beta", "se", "p"]),
            ("route_fe", ["city", "n", "n_routes", "beta", "se", "p"]),
            ("composition", ["spec", "n", "beta", "se", "pct"]),
            ("missingness", ["city", "n_used", "n_total"]),
        ]:
            sub = d[d.check == chk]
            if len(sub):
                have = [c for c in cols if c in sub.columns]
                print(f"\n--- reviewer check: {chk} ---")
                print(sub[have].to_string(index=False, float_format=lambda x: f"{x:.4f}"))

    # ---- currency, constants, one-way, independent --------------------------
    show("Currency 2018 vs 2024", T / f"hpms_currency_2018_vs_2024_r{r}.csv",
         ["city", "n_model", "spearman_2018_2024", "median_aadt_ratio",
          "beta_2018", "beta_2024", "p_2024"])
    show("P1 constants sweep", T / f"p1_constants_sweep_r{r}.csv")
    show("One-way selection profile", T / "oneway_selection_profile.csv")
    show("Detour cap sweep", T / "sensitivity_detour_cap.csv")
    show("Tertiary both-sides", T / "sensitivity_tertiary_bothsides.csv")
    show("Independent subsample", T / f"h1_independent_subsample_r{r}.csv",
         ["city", "n_full", "n_ind", "b_full", "b_ind", "p_ind", "mde"])
    show("MAUP sweep (Denver)", T / "h1_maup_sweep.csv")
    show("Specification comparison (Denver)", T / "h1_specification_comparison.csv")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
