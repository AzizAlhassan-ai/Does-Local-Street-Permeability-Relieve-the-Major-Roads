#!/usr/bin/env python
"""Stage 3c — pool the per-city analysis tables into the multi-city table.

Per-city tables are written by 03b (D-053). This concatenates them, harmonises the
segment key across cities, and reports the pooled inventory used by Stage 5.

Usage
-----
    uv run python code/03_conflate/03c_pool_cities.py
"""
from __future__ import annotations
import pathlib, sys
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
import pandas as pd
from lib import cfg, paths, provenance

def main() -> int:
    conf = cfg.config()
    radii = conf["catchment"]["radii_m"]
    primary = conf["catchment"]["primary_radius_m"]
    cities = list(cfg.cities().keys())
    print(f"Environment: {provenance.environment_stamp()}")

    for r in radii:
        parts, missing = [], []
        for c in cities:
            fp = paths.ANALYSIS / f"analysis_table_{c}_r{r}.parquet"
            if not fp.exists():
                missing.append(c); continue
            d = pd.read_parquet(fp)
            d["city"] = c
            # segment_uid is only unique within a city -> namespace it
            d["segment_uid"] = c + "|" + d["segment_uid"].astype(str)
            d["cell_id"] = c + "|" + d["cell_id"].astype(str)
            parts.append(d)
        if not parts:
            print(f"  r={r}: no city tables found"); continue
        pooled = pd.concat(parts, ignore_index=True)
        fp = paths.ANALYSIS / f"analysis_pooled_r{r}.parquet"
        pooled.to_parquet(fp, index=False)
        tag = "  [PRIMARY]" if r == primary else ""
        print(f"\n=== pooled r={r} m{tag} ===")
        if missing:
            print(f"  MISSING cities (not yet run): {missing}")
        print(f"  rows {len(pooled):,} | cities {pooled.city.nunique()} | "
              f"cells {pooled.cell_id.nunique():,} | routes {pooled.route_id.nunique():,}")
        print(pooled.groupby("city").agg(
            n=("log_aadt", "size"),
            cells=("cell_id", "nunique"),
            median_aadt=("aadt", "median"),
            pct_P1=("p1_any", lambda s: 100 * s.mean()),
            mean_P1=("p1_routes", "mean"),
            mean_intdens=("local_int_density", "mean"),
            mean_lnr=("local_link_node_ratio", "mean"),
        ).round(2).to_string())
        if r == primary:
            pooled.to_parquet(paths.ANALYSIS / "analysis_pooled.parquet", index=False)
            print("  wrote data/analysis/analysis_pooled.parquet  <-- CANONICAL")
    provenance.log_progress("03c_pool_cities", "pooled multi-city analysis tables")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
