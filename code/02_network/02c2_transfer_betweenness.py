#!/usr/bin/env python
"""Stage 2c (transfer) — carry betweenness onto the exogenous-frame units (D-100).

Betweenness is a property of the metro-wide MAJOR-ROAD graph, not of the unit definition.
Stage 2c computes edge betweenness once per city and then assigns each HPMS analysis unit
the value of the nearest major OSM edge to its midpoint. Changing how HPMS increments are
dissolved into units changes only which midpoints are queried — it does not change the
graph, the pivots, or the edge values.

Re-running the k = 8,000 pivot computation for the exogenous frame would therefore
recompute an identical quantity at a cost of hours. Instead we transfer: each exogenous-
frame unit takes the betweenness of the nearest PRIMARY-frame unit midpoint, subject to a
maximum match distance. The primary frame is strictly finer (more, shorter units cut from
the same roads), so the nearest primary midpoint lies on the same carriageway in all but
pathological cases, and the match distance is reported so the reader can see that.

This affects one table only — the RQ2 moderation model — where betweenness enters as a
moderator. It is not used in the primary specification.

Usage
-----
    uv run python code/02_network/02c2_transfer_betweenness.py
"""
from __future__ import annotations
import argparse, pathlib, sys
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
import geopandas as gpd, numpy as np, pandas as pd
from lib import cfg, paths, provenance

MAX_MATCH_M = 300.0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--variant", default="aadtfree")
    args = ap.parse_args()
    conf = cfg.config()
    metric = conf["crs"]["metric"]
    print(f"Environment: {provenance.environment_stamp()}")
    print(f"  {'city':<16}{'units':>9}{'matched':>9}{'median dist':>14}{'p95 dist':>11}")

    for c in cfg.cities():
        src_dir = paths.PROCESSED / c
        dst_dir = paths.PROCESSED / f"{c}__{args.variant}"
        bt_fp = src_dir / "segment_betweenness.parquet"
        if not (bt_fp.exists() and dst_dir.exists()):
            print(f"  {c:<16} missing inputs — skipped")
            continue

        src = gpd.read_parquet(src_dir / "segments.parquet").to_crs(metric)
        bt = pd.read_parquet(bt_fp)
        src = src.merge(bt, on="segment_uid", how="left")
        src = src.dropna(subset=["arterial_betweenness"])
        src_pts = gpd.GeoDataFrame(
            src[["arterial_betweenness"]].reset_index(drop=True),
            geometry=[g.interpolate(0.5, normalized=True) for g in src.geometry],
            crs=metric)

        dst = gpd.read_parquet(dst_dir / "segments.parquet").to_crs(metric)
        dst_pts = gpd.GeoDataFrame(
            dst[["segment_uid"]].reset_index(drop=True),
            geometry=[g.interpolate(0.5, normalized=True) for g in dst.geometry],
            crs=metric)

        j = gpd.sjoin_nearest(dst_pts, src_pts, how="left",
                              max_distance=MAX_MATCH_M, distance_col="_d")
        j = j.sort_values("_d").drop_duplicates("segment_uid")
        out = j[["segment_uid", "arterial_betweenness"]].copy()
        n_ok = int(out["arterial_betweenness"].notna().sum())
        d = j["_d"].dropna()
        print(f"  {c:<16}{len(dst):>9,}{n_ok:>9,}{d.median():>13.0f}m{d.quantile(.95):>10.0f}m")
        out.to_parquet(dst_dir / "segment_betweenness.parquet", index=False)
        provenance.log(city=c, layer=f"betweenness_transfer_{args.variant}",
                       source_url="derived: 02c on the primary frame", rows=n_ok,
                       file_path=dst_dir / "segment_betweenness.parquet")

    print("\n  Transfer complete. Re-run 03b/03c for the variant to fold it in.")
    provenance.log_progress("02c2_transfer_betweenness",
                            "betweenness carried onto exogenous-frame units (D-100)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
