#!/usr/bin/env python
"""Stage 3b — assemble THE canonical analysis table.

One row per analysis unit (D-028 dissolved segment) per radius. Everything the
models in Stage 4 need, and nothing else, with a completeness audit and
collinearity diagnostics so the modelling stage starts from a known state.

    data/analysis/analysis_table.parquet        primary radius — CANONICAL
    data/analysis/analysis_table_r<R>.parquet   MAUP sweep

Every row is traceable: `segment_uid` -> the dissolved HPMS run, `route_id` -> the
HPMS route, `n_hpms_increments` -> how many 0.1-mile records were merged.

Depends on: 02a, 02b, 02c, 03a

Usage
-----
    uv run python code/03_conflate/03b_analysis_table.py --city denver
"""

from __future__ import annotations

import argparse
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

import geopandas as gpd
import numpy as np
import pandas as pd

from lib import cfg, paths, provenance, validate

SEG_COLS = [
    "segment_uid", "route_id", "cell_id", "aadt", "log_aadt", "aadt_per_lane",
    "f_system", "facility_type", "through_lanes", "access_control_", "ownership",
    "nhs", "length_m", "n_hpms_increments", "speed_limit_usable",
]
PERM_COLS = [
    "segment_uid", "local_int_density", "local_link_node_ratio",
    "local_street_density", "local_deadend_share", "local_circuity",
    "local_nodes", "local_edges",
]


def vif(df: pd.DataFrame) -> pd.Series:
    """Variance inflation factors via R² of each column on the others."""
    X = df.dropna()
    out = {}
    for c in X.columns:
        y = X[c].values
        A = np.column_stack([np.ones(len(X)), X.drop(columns=[c]).values])
        beta, *_ = np.linalg.lstsq(A, y, rcond=None)
        resid = y - A @ beta
        ss_tot = ((y - y.mean()) ** 2).sum()
        r2 = 1 - (resid ** 2).sum() / ss_tot if ss_tot > 0 else 0.0
        out[c] = np.inf if r2 >= 1 else 1.0 / (1.0 - r2)
    return pd.Series(out).sort_values(ascending=False)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--city", default=None)
    args = ap.parse_args()

    conf = cfg.config()
    city_key = args.city or conf["project"]["pilot_city"]
    C = cfg.city(city_key)
    proc = paths.processed(city_key)
    primary = conf["catchment"]["primary_radius_m"]
    radii = conf["catchment"]["radii_m"]

    print(f"Environment: {provenance.environment_stamp()}")
    print(f"City: {city_key} ({C['label']})")

    seg_fp = proc / "segments.parquet"
    bet_fp = proc / "segment_betweenness.parquet"
    if not seg_fp.exists():
        print("ERROR: segments.parquet missing (run 02a).")
        return 1
    seg = gpd.read_parquet(seg_fp)
    seg = pd.DataFrame(seg.drop(columns=[seg.geometry.name]))
    keep = [c for c in SEG_COLS if c in seg.columns]
    seg = seg[keep]
    print(f"\nanalysis units (D-028): {len(seg):,}")

    if bet_fp.exists():
        bet = pd.read_parquet(bet_fp)
        print(f"betweenness rows: {len(bet):,} "
              f"(non-null {int(bet['arterial_betweenness'].notna().sum()):,})")
    else:
        bet = None
        print("!! segment_betweenness.parquet missing — H2 moderator (b) will be absent")

    paths.ANALYSIS.mkdir(parents=True, exist_ok=True)
    written = []

    for r in radii:
        pf, cf = proc / f"permeability_r{r}.parquet", proc / f"controls_r{r}.parquet"
        if not (pf.exists() and cf.exists()):
            print(f"\n  SKIP r={r}: permeability/controls missing")
            continue
        perm = pd.read_parquet(pf)[[c for c in PERM_COLS if c in
                                    pd.read_parquet(pf, columns=None).columns]]
        ctrl = pd.read_parquet(cf)
        # P1/P2 — the redefined mechanism-specific predictor (Stage 2R, D-035..D-041)
        trf = proc / f"through_routes_r{r}.parquet"
        thru = pd.read_parquet(trf) if trf.exists() else None
        if thru is None:
            print(f"  !! through_routes_r{r}.parquet missing — P1/P2 absent")
        tag = "  [PRIMARY -> canonical]" if r == primary else ""
        print(f"\n=== analysis table r={r} m{tag} ===")

        t = seg.merge(perm, on="segment_uid", how="left", validate="1:1")
        t = t.merge(ctrl.drop(columns=["catch_area_in_ua_km2"], errors="ignore"),
                    on="segment_uid", how="left", validate="1:1")
        if bet is not None:
            t = t.merge(bet, on="segment_uid", how="left", validate="1:1")
        if thru is not None:
            t = t.merge(thru.drop(columns=["seg_len_m"], errors="ignore"),
                        on="segment_uid", how="left", validate="1:1")

        # D-027 + D-030: centrality enters non-linearly, on a CENTRED base so the
        # linear and quadratic terms are not artificially collinear.
        if "dist_cbd_km" in t.columns:
            mu = t["dist_cbd_km"].mean()
            t["dist_cbd_mean_km"] = mu
            t["dist_cbd_km_c"] = t["dist_cbd_km"] - mu
            t["dist_cbd_km_c_sq"] = t["dist_cbd_km_c"] ** 2
        # Structural-zero flag (Stage 2b finding): arterials with no local fabric.
        t["no_local_network"] = (t.get("local_nodes", pd.Series(0, index=t.index))
                                 .fillna(0) == 0)
        t["radius_m"] = r
        # D-053: analysis tables are PER CITY. The previous single-file naming meant
        # each city's run silently overwrote the last; the canonical table ended up
        # holding only whichever city ran most recently. City also enters as a column
        # because D-047 makes it a fixed effect.
        t["city"] = city_key

        # --- completeness audit ---
        model_vars = (
            ["log_aadt", "aadt_per_lane", "p1_routes", "p1_any", "p2_pairs_per_km2",
             "local_int_density", "access_control_", "arterial_betweenness"]
            + list(conf["controls"]["first_class"])
        )
        model_vars = [v for v in dict.fromkeys(model_vars) if v in t.columns]
        print("  completeness of model variables:")
        for v in model_vars:
            nn = int(t[v].notna().sum())
            print(f"    {v:32s} {nn:>6,}/{len(t):,}  ({nn/len(t):6.1%})")

        cc = t[model_vars].dropna()
        print(f"\n  COMPLETE CASES on all model variables: {len(cc):,}/{len(t):,} "
              f"({len(cc)/len(t):.1%})")
        n_cells = t.loc[t[model_vars].notna().all(axis=1), "cell_id"].nunique()
        print(f"  occupied level-2 cells among complete cases: {n_cells:,}")
        print(f"  distinct routes among complete cases: "
              f"{t.loc[t[model_vars].notna().all(axis=1), 'route_id'].nunique():,}")

        if r == primary:
            num = [v for v in model_vars
                   if pd.api.types.is_numeric_dtype(t[v]) and v not in
                   ("f_system", "access_control_")]
            print("\n  correlation with log_aadt (primary radius):")
            for v in num:
                if v == "log_aadt":
                    continue
                c = t[["log_aadt", v]].dropna()
                print(f"    {v:32s} r = {c['log_aadt'].corr(c[v]):+.3f}")
            vif_vars = [v for v in conf["controls"]["first_class"]
                        if v in t.columns and pd.api.types.is_numeric_dtype(t[v])]
            vif_vars += ["local_int_density", "dist_cbd_km_c_sq"]
            vif_vars = [v for v in dict.fromkeys(vif_vars) if v in t.columns]
            print("\n  VIF (first-class controls + predictor):")
            v_ = vif(t[vif_vars])
            for k_, val in v_.items():
                flag = "  <-- HIGH" if val > 10 else ("  <- watch" if val > 5 else "")
                print(f"    {k_:32s} {val:8.2f}{flag}")

        fp = paths.ANALYSIS / f"analysis_table_{city_key}_r{r}.parquet"
        t.to_parquet(fp, index=False)
        written.append((r, fp, len(t)))
        print(f"\n  wrote {fp.relative_to(paths.ROOT)} "
              f"({fp.stat().st_size/1e6:.2f} MB, {t.shape[1]} columns)")
        if r == primary:
            canon = paths.ANALYSIS / f"analysis_table_{city_key}.parquet"
            t.to_parquet(canon, index=False)
            print(f"  wrote {canon.relative_to(paths.ROOT)}  <-- CANONICAL")
            validate.report_df(t, "CANONICAL analysis table",
                               key_cols=["log_aadt", "local_int_density",
                                         "arterial_betweenness", "dist_cbd_km"])

    for r, fp, n in written:
        provenance.log(city=city_key, layer=f"analysis_table_r{r}",
                       source_url="derived: 02a/02b/02c + 03a",
                       rows=n, file_path=fp)
    provenance.log_progress(
        "03b_analysis_table",
        f"{city_key}: canonical analysis table built at r={primary} m "
        f"({written[0][2]:,} units) plus MAUP sweep {[r for r, _, _ in written]}",
    )
    print("\nStage 3b complete.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
