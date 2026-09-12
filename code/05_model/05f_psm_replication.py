#!/usr/bin/env python
"""Stage 5 — Layer 1: Choi & Ewing's (2021) design applied to our data.

Their method, step for step (their §3.6):
  1. 1 mi² grid cells as the unit
  2. their four metrics -> one street network design index via PCA
  3. their sample filters (activity density >= 1500/sq mi, major road >= 2 mi)
  4. top-N cells by index = "study group" (they used top 40); the rest = control pool
  5. propensity score matching, 1:1 nearest neighbour with a caliper
  6. compare the outcome between matched groups

NOT a replication of their RESULT. Their outcome is a Travel Time Index from
StreetLight (commercial); ours is AADT volume from HPMS. So this transfers their
*design* to our *outcome* and asks whether the same matched-pair logic, applied to
volume rather than congestion, points the same way. Stated as such (D-070).

Covariates: we match on what we have. Their set also included household income,
% non-white, % older adults and number of schools, which we do not currently pull
from ACS. Balance is reported so the gap is visible rather than assumed.

Usage
-----
    uv run python code/05_model/05f_psm_replication.py
"""

from __future__ import annotations

import argparse
import os
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

import geopandas as gpd
import numpy as np
import pandas as pd
import statsmodels.api as sm
from scipy import stats as st

from lib import cfg, paths, provenance

# their four metrics, whole-network construction (matches their pipeline)
CE_METRICS = ["int_density_all", "median_block_acres", "link_node_all", "pct_4way_all"]
COVARS = ["activity_density", "major_road_mi", "pop_density_cell",
          "median_year_cell", "lu_entropy_cell"]


def pca_index(X: pd.DataFrame) -> tuple[pd.Series, pd.Series]:
    """First principal component of standardised metrics, sign-fixed so that
    HIGHER = denser and better connected (their convention)."""
    Z = (X - X.mean()) / X.std(ddof=0)
    C = np.cov(Z.values, rowvar=False)
    w, v = np.linalg.eigh(C)
    pc = v[:, np.argmax(w)]
    load = pd.Series(pc, index=X.columns)
    # block size loads negatively in their Table 2; orient the index the same way
    if load.get("int_density_all", 0) < 0:
        load, pc = -load, -pc
    return pd.Series(Z.values @ pc, index=X.index, name="ce_index"), load


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--top-n", type=int, default=40,
                    help="cells per city in the study group (their value: 40)")
    ap.add_argument("--caliper", type=float, default=0.2,
                    help="caliper in propensity-score SDs (convention: 0.2)")
    args = ap.parse_args()
    conf = cfg.config()
    r = conf["catchment"]["primary_radius_m"]
    print(f"Environment: {provenance.environment_stamp()}")

    # ---- assemble cell table ------------------------------------------------
    cells, segs = [], []
    for c in cfg.cities():
        fp = paths.processed(c) / "cell_metrics.parquet"
        if not fp.exists():
            continue
        cells.append(pd.read_parquet(fp))
        t = pd.read_parquet(paths.ANALYSIS / f"analysis_table_{c}_r{r}.parquet")
        # D-094: P1 is undefined below twice the endpoint attach radius, so cells must be
        # summarised over the same segments the models estimate on.
        floor = float(os.environ.get("MIN_SEG_LEN_M", "0"))
        if floor and "length_m" in t.columns:
            t = t[t["length_m"] >= floor]
        t["city"] = c
        segs.append(t)
    d = pd.concat(cells, ignore_index=True)
    s = pd.concat(segs, ignore_index=True)

    # cell-level outcome + remaining covariates, from the segment table
    s = s[s.cell_id.notna()]
    agg = s.groupby(["city", "cell_id"]).agg(
        mean_log_aadt=("log_aadt", "mean"),
        n_seg=("log_aadt", "size"),
        vmt=("aadt", lambda x: float(np.sum(x))),
        pop_density_cell=("pop_density_km2", "mean"),
        median_year_cell=("median_year_structure_built", "mean"),
        lu_entropy_cell=("lu_entropy", "mean"),
        pct_p1=("p1_any", "mean"),
    ).reset_index()
    d = d.merge(agg, on=["city", "cell_id"], how="inner")

    n0 = len(d)
    d = d[d.ce_eligible].dropna(subset=CE_METRICS + ["mean_log_aadt"] + COVARS)
    print(f"\ncells: {n0:,} -> {len(d):,} after their filters and complete cases")
    print(f"  by city: {d.city.value_counts().to_dict()}")

    # ---- their PCA index ----------------------------------------------------
    idx, load = pca_index(d[CE_METRICS])
    d["ce_index"] = idx.values
    print(f"\n=== street network design index (PCA), our loadings vs theirs ===")
    theirs = {"int_density_all": 0.423, "median_block_acres": -0.578,
              "link_node_all": 0.840, "pct_4way_all": 0.772}
    print(f"  {'metric':<24}{'ours':>9}{'theirs':>9}")
    for k in CE_METRICS:
        print(f"  {k:<24}{load[k]:>9.3f}{theirs[k]:>9.3f}")
    print("  (sign pattern is what matters: block size negative, the rest positive)")

    # ---- study vs control, per city ----------------------------------------
    d["study"] = 0
    for c, g in d.groupby("city"):
        top = g.nlargest(min(args.top_n, len(g) // 3), "ce_index").index
        d.loc[top, "study"] = 1
    print(f"\n  study group (top {args.top_n}/city by index): {int(d.study.sum()):,}"
          f" | control pool: {int((1-d.study).sum()):,}")

    # ---- propensity score ---------------------------------------------------
    X = d[COVARS].copy()
    X = (X - X.mean()) / X.std(ddof=0)
    X = sm.add_constant(pd.concat([X, pd.get_dummies(d["city"], prefix="c",
                                                     drop_first=True).astype(float)], axis=1))
    ps = sm.Logit(d["study"].values, X.values).fit(disp=0)
    d["pscore"] = ps.predict(X.values)
    cal = args.caliper * d["pscore"].std(ddof=0)
    print(f"  propensity model pseudo-R² = {ps.prsquared:.3f} | caliper = {cal:.4f}")

    # ---- 1:1 nearest-neighbour matching within city, without replacement ----
    pairs = []
    for c, g in d.groupby("city"):
        tr = g[g.study == 1].sort_values("pscore", ascending=False)
        ct = g[g.study == 0].copy()
        used = set()
        for i, row in tr.iterrows():
            pool = ct[~ct.index.isin(used)]
            if pool.empty:
                continue
            dist = (pool["pscore"] - row["pscore"]).abs()
            j = dist.idxmin()
            if dist.loc[j] <= cal:
                used.add(j)
                pairs.append((i, j))
    print(f"\n  matched pairs: {len(pairs):,}  (Choi & Ewing had 31)")
    if not pairs:
        print("  no pairs within caliper — widen it")
        return 1
    ti = [p[0] for p in pairs]; ci = [p[1] for p in pairs]
    T, C = d.loc[ti], d.loc[ci]

    # ---- balance ------------------------------------------------------------
    print(f"\n=== covariate balance after matching ===")
    print(f"  {'variable':<24}{'study':>11}{'control':>11}{'std diff':>10}{'p':>8}")
    for v in COVARS + CE_METRICS:
        a, b = T[v].values, C[v].values
        sd = np.sqrt((a.var(ddof=1) + b.var(ddof=1)) / 2)
        smd = (a.mean() - b.mean()) / sd if sd > 0 else np.nan
        p = st.ttest_rel(a, b).pvalue
        flag = "  <-- design var" if v in CE_METRICS else (
            "  !! imbalanced" if abs(smd) > 0.25 else "")
        print(f"  {v:<24}{a.mean():>11.2f}{b.mean():>11.2f}{smd:>10.2f}{p:>8.3f}{flag}")

    # ---- outcome ------------------------------------------------------------
    print(f"\n=== outcome: mean log(AADT) on major roads in the cell ===")
    a, b = T["mean_log_aadt"].values, C["mean_log_aadt"].values
    diff = a.mean() - b.mean()
    tt = st.ttest_rel(a, b)
    print(f"  well-connected cells : {a.mean():.4f}   (AADT ≈ {np.exp(a.mean()):,.0f})")
    print(f"  poorly-connected     : {b.mean():.4f}   (AADT ≈ {np.exp(b.mean()):,.0f})")
    print(f"  difference           : {diff:+.4f}  ->  {100*(np.exp(diff)-1):+.1f}% AADT")
    print(f"  paired t = {tt.statistic:+.3f}, p = {tt.pvalue:.4f}, n pairs = {len(a)}")
    verdict = ("LOWER traffic in better-connected cells — same direction as their "
               "congestion finding" if diff < 0 and tt.pvalue < .05 else
               "HIGHER traffic in better-connected cells — opposite direction"
               if diff > 0 and tt.pvalue < .05 else
               "no significant difference")
    print(f"  --> {verdict}")

    print(f"\n=== and our P1 measure on the same matched cells ===")
    a1, b1 = T["pct_p1"].values * 100, C["pct_p1"].values * 100
    print(f"  % arterials with a substitutable route: study {a1.mean():.1f}% vs "
          f"control {b1.mean():.1f}%  (p = {st.ttest_rel(a1, b1).pvalue:.4f})")
    print("  -> shows how far their connectivity index tracks substitutability")

    out = pd.DataFrame({"city": T["city"].values,
                        "study_cell": T["cell_id"].values,
                        "control_cell": C["cell_id"].values,
                        "study_log_aadt": a, "control_log_aadt": b,
                        "study_index": T["ce_index"].values,
                        "control_index": C["ce_index"].values})
    fp = paths.TABLES / "psm_choi_ewing_replication.csv"
    out.to_csv(fp, index=False)
    print(f"\n  wrote {fp.relative_to(paths.ROOT)}")
    provenance.log_progress("05f_psm_replication",
                            f"Choi & Ewing design on our data: {len(pairs)} matched pairs")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
