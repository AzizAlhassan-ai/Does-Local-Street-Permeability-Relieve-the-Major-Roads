#!/usr/bin/env python
"""Stage 2a — build the analysis frame: segment set, 1 mi² grid, catchment buffers.

This is where the analytic decisions from the decisions log are first APPLIED to the
acquired data:
  D-017  outcome restricted to two-way roadways (facility_type)
  D-014  level-2 grouping unit = regular 1 mi² grid
  D-004  log_aadt primary, aadt_per_lane co-primary
  catchment.radii_m  the MAUP sweep

Depends on: 01b (urban_area.gpkg), 01d (hpms2018_ua_analysis.gpkg)

Usage
-----
    uv run python code/02_network/02a_analysis_frame.py --city denver

Outputs
-------
    data/processed/<city>/segments.parquet          analysis segments + cell id + outcomes
    data/processed/<city>/grid.parquet              1 mi² cells clipped to the UA
    data/processed/<city>/catchments_r<R>.parquet   one file per buffer radius
"""

from __future__ import annotations

import argparse
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

import geopandas as gpd
import numpy as np
import pandas as pd
from shapely.geometry import box
from shapely.ops import linemerge

from lib import cfg, paths, provenance, validate


def dissolve_homogeneous(seg: gpd.GeoDataFrame, keys: list[str], tol: float,
                         metric: str, max_run_mi: float | None = None) -> gpd.GeoDataFrame:
    """Merge contiguous HPMS increments that share all `keys` into one unit (D-028).

    A new run starts at a route change, any change in `keys`, or a positional gap
    (this record's begin_point does not continue the previous end_point).

    `max_run_mi` caps run length (D-086). It exists for the AADT-free variant: with
    AADT out of the key, runs would otherwise extend for the whole length of a route
    with constant lanes and class. Any attribute not constant within a run is
    length-weighted rather than taken from the first increment.
    """
    s = seg.sort_values(["route_id", "begin_point"]).reset_index(drop=True)
    newroute = s["route_id"] != s["route_id"].shift()
    attrchg = (s[keys] != s[keys].shift()).any(axis=1)
    gap = (s["begin_point"] - s["end_point"].shift()).abs() > tol
    s["run_id"] = (newroute | attrchg | gap.fillna(True)).cumsum()
    print(f"  run triggers -> new route {int(newroute.sum()):,}, "
          f"attribute change {int((attrchg & ~newroute).sum()):,}, "
          f"positional gap {int((gap.fillna(True) & ~newroute & ~attrchg).sum()):,}")

    if max_run_mi:
        # Split each run into consecutive blocks of at most max_run_mi route-miles.
        inc_mi = (s["end_point"] - s["begin_point"]).abs().fillna(0.0)
        cum = inc_mi.groupby(s["run_id"]).cumsum()
        blk = ((cum - 1e-12) // max_run_mi).astype(int)
        s["run_id"] = s["run_id"].astype(str) + "_" + blk.astype(str)
        s["run_id"] = pd.factorize(s["run_id"])[0] + 1
        print(f"  length cap {max_run_mi} mi applied -> {s['run_id'].nunique():,} runs")

    # Attributes are constant within a run by construction UNLESS the length cap or a
    # reduced key set let them vary; length-weight those instead of taking the first.
    s["_w"] = (s["end_point"] - s["begin_point"]).abs().fillna(0.0).clip(lower=1e-9)

    def lw(col):
        v = s[col].astype(float)
        ok = v.notna()
        num = (v.where(ok, 0.0) * s["_w"].where(ok, 0.0)).groupby(s["run_id"]).sum()
        den = s["_w"].where(ok, 0.0).groupby(s["run_id"]).sum()
        return num / den.replace(0.0, np.nan)

    agg = {k: "first" for k in keys}
    agg.update({
        "route_id": "first", "begin_point": "min", "end_point": "max",
        "nhs": "first", "urban_code": "first", "county_code": "first",
        "route_name": "first", "route_signing": "first", "speed_limit": "first",
        "aadt_combination": "first", "aadt_single_unit": "first",
    })
    agg = {k: v for k, v in agg.items() if k in s.columns}
    attrs = s.groupby("run_id").agg(agg)
    attrs["n_hpms_increments"] = s.groupby("run_id").size()

    # Anything numeric that was NOT a homogeneity key gets the length-weighted mean.
    for col in ("aadt", "through_lanes", "aadt_combination", "aadt_single_unit"):
        if col in s.columns and col not in keys:
            attrs[col] = lw(col)
    if "through_lanes" in attrs.columns and "through_lanes" not in keys:
        attrs["through_lanes"] = attrs["through_lanes"].round()

    def merge_geom(g):
        # The GPKG round-trip promotes LineString -> MultiLineString, and linemerge
        # cannot consume multi-part inputs. Flatten to component LineStrings first.
        parts = []
        for geom in g:
            if geom is None or geom.is_empty:
                continue
            if geom.geom_type == "MultiLineString":
                parts.extend(list(geom.geoms))
            else:
                parts.append(geom)
        if not parts:
            return None
        if len(parts) == 1:
            return parts[0]
        merged = linemerge(parts)
        return merged

    geom = s.groupby("run_id")["geometry"].apply(merge_geom)

    out = gpd.GeoDataFrame(attrs, geometry=gpd.GeoSeries(geom, crs=s.crs))
    out = out.reset_index().rename(columns={"run_id": "segment_uid"})
    out["segment_uid"] = "d" + out["segment_uid"].astype(str)
    L = out.to_crs(metric).geometry.length
    out["length_m"] = L.values
    gt = out.geometry.geom_type.value_counts().to_dict()
    print(f"  dissolved geometry types: {gt}")
    print(f"  run length (m): median {L.median():.0f}, p90 {L.quantile(.9):.0f}, "
          f"max {L.max():.0f}")
    return out


def midpoints(geom_series: gpd.GeoSeries) -> gpd.GeoSeries:
    """Point half-way along each line. Falls back to representative_point()."""
    out = []
    for g in geom_series:
        try:
            out.append(g.interpolate(0.5, normalized=True))
        except Exception:
            out.append(g.representative_point())
    return gpd.GeoSeries(out, index=geom_series.index, crs=geom_series.crs)


def build_grid(ua_metric: gpd.GeoDataFrame, side_m: float, crs: str) -> gpd.GeoDataFrame:
    """Regular square grid covering the UA, clipped to it (D-014)."""
    minx, miny, maxx, maxy = ua_metric.total_bounds
    # Anchor to a multiple of side_m so the grid is reproducible and city-independent.
    x0 = np.floor(minx / side_m) * side_m
    y0 = np.floor(miny / side_m) * side_m
    xs = np.arange(x0, maxx + side_m, side_m)
    ys = np.arange(y0, maxy + side_m, side_m)
    cells, ids = [], []
    for i, x in enumerate(xs):
        for j, y in enumerate(ys):
            cells.append(box(x, y, x + side_m, y + side_m))
            ids.append(f"c{i:03d}_{j:03d}")
    grid = gpd.GeoDataFrame({"cell_id": ids}, geometry=cells, crs=crs)
    ua_geom = ua_metric.geometry.iloc[0]
    grid = grid[grid.intersects(ua_geom)].copy()
    grid["cell_area_km2"] = grid.geometry.area / 1e6
    # Land area actually inside the UA — the honest denominator for cell-level rates.
    grid["cell_area_in_ua_km2"] = grid.geometry.intersection(ua_geom).area / 1e6
    return grid.reset_index(drop=True)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--city", default=None)
    args = ap.parse_args()

    conf = cfg.config()
    city_key = args.city or conf["project"]["pilot_city"]
    C = cfg.city(city_key)
    metric = conf["crs"]["metric"]
    dv = conf["dependent_variable"]

    print(f"Environment: {provenance.environment_stamp()}")
    print(f"City: {city_key} ({C['label']})")

    # --- inputs -------------------------------------------------------------
    ua_fp = paths.raw(city_key, "census") / "urban_area.gpkg"
    seg_fp = paths.raw(city_key, "hpms") / "hpms2018_ua_analysis.gpkg"
    for fp, script in ((ua_fp, "01b"), (seg_fp, "01d")):
        if not fp.exists():
            print(f"ERROR: {fp.relative_to(paths.ROOT)} missing. Run {script} first.")
            return 1

    ua = gpd.read_file(ua_fp).to_crs("EPSG:4326")
    ua_m = ua.to_crs(metric)
    seg = gpd.read_file(seg_fp, layer="segments")
    print(f"\nHPMS analysis segments from 01d: {len(seg):,}")

    # --- D-017: two-way roadways only --------------------------------------
    keep_ft = dv["hpms_facility_type_keep"]
    if paths.VARIANT == "oneway":
        # D-089. One-way roadways are excluded from the primary because HPMS reports
        # them directionally. This variant admits them and doubles the reported value,
        # which is the standard assumption of balanced flow on a one-way pair. It
        # converts an argument about attenuation into a number.
        keep_ft = dv["hpms_facility_type_sensitivity"]
        seg.loc[seg["facility_type"] == 1, "aadt"] = seg.loc[
            seg["facility_type"] == 1, "aadt"] * 2.0
        print("\n!! PIPE_VARIANT=oneway — one-way roadways admitted, AADT doubled (D-089)")
    before = len(seg)
    ft_counts = seg["facility_type"].value_counts().sort_index().to_dict()
    print(f"  facility_type composition: {ft_counts}")
    seg = seg[seg["facility_type"].isin(keep_ft)].copy()
    print(f"  D-017 keep facility_type {keep_ft}: {len(seg):,} "
          f"(dropped {before - len(seg):,} = {(before-len(seg))/before:.1%})")
    if seg.empty:
        raise validate.ValidationError("No segments survived the facility_type filter.")

    # --- D-004: outcomes ----------------------------------------------------
    seg["log_aadt"] = np.log(seg["aadt"])
    tl = seg["through_lanes"]
    seg["aadt_per_lane"] = np.where(tl.notna() & (tl > 0), seg["aadt"] / tl, np.nan)
    n_bad_lanes = int(seg["aadt_per_lane"].isna().sum())
    print(f"  log_aadt computed: {int(seg['log_aadt'].notna().sum()):,}")
    print(f"  aadt_per_lane computed: {int(seg['aadt_per_lane'].notna().sum()):,} "
          f"(unusable through_lanes on {n_bad_lanes})")

    # --- D-028: dissolve to AADT-homogeneous contiguous runs ---------------
    sd = conf.get("segment_definition", {})
    if paths.VARIANT == "aadtfree":
        # D-086. Referees objected that AADT in the dissolve key makes unit length a
        # function of the outcome, and P1's detour cap is defined relative to length.
        # This variant dissolves on exogenous attributes only, with a fixed length cap.
        sd = dict(sd)
        sd["homogeneity_keys"] = [k for k in sd["homogeneity_keys"] if k != "aadt"]
        sd["max_run_mi"] = 0.5
        print("\n!! PIPE_VARIANT=aadtfree — AADT removed from the dissolve key (D-086)")
    if sd.get("dissolve_homogeneous"):
        print(f"\n=== D-028 segment definition: dissolve homogeneous runs ===")
        n_before = len(seg)
        seg = dissolve_homogeneous(
            seg, sd["homogeneity_keys"], float(sd["contiguity_tolerance"]), metric,
            max_run_mi=sd.get("max_run_mi"),
        )
        print(f"  {n_before:,} HPMS increments -> {len(seg):,} analysis units "
              f"({n_before/len(seg):.2f}x reduction)")
        print(f"  increments per unit: median "
              f"{seg['n_hpms_increments'].median():.0f}, max {seg['n_hpms_increments'].max()}")
        # Outcomes must be recomputed on the dissolved units (aadt is constant
        # within a run, so this is a relabel, but be explicit).
        seg["log_aadt"] = np.log(seg["aadt"])
        tl = seg["through_lanes"]
        seg["aadt_per_lane"] = np.where(tl.notna() & (tl > 0), seg["aadt"] / tl, np.nan)
    else:
        seg["segment_uid"] = "r" + seg["objectid"].astype(str)
        seg["n_hpms_increments"] = 1

    # --- H2 moderator (D-018): access control ------------------------------
    ac = seg["access_control_"]
    print(f"\n  D-018 access_control_ (H2 moderator): "
          f"non-null {int(ac.notna().sum()):,}/{len(seg):,} "
          f"({ac.notna().mean():.1%})")
    print(f"    distribution: {ac.value_counts(dropna=False).sort_index().to_dict()}")
    sl = seg["speed_limit"]
    lo, hi = dv["speed_limit_plausible_mph"]
    sl_ok = sl.notna() & (sl >= lo) & (sl <= hi)
    print(f"    (for contrast, speed_limit usable on {int(sl_ok.sum()):,} "
          f"= {sl_ok.mean():.1%} — why D-018 exists)")
    seg["speed_limit_usable"] = np.where(sl_ok, sl, np.nan)

    # --- 1 mi² grid (D-014) -------------------------------------------------
    au = conf["analysis_unit"]["primary"]
    side = float(au["cell_side_m"])
    print(f"\n=== 1 mi² grid (side {side:.1f} m, D-014) ===")
    grid = build_grid(ua_m, side, metric)
    print(f"  cells intersecting UA: {len(grid):,}")
    print(f"  cell area (full): {grid['cell_area_km2'].min():.3f}–"
          f"{grid['cell_area_km2'].max():.3f} km² "
          f"(1 mi² = {side**2/1e6:.3f})")
    print(f"  area inside UA: min {grid['cell_area_in_ua_km2'].min():.4f}, "
          f"median {grid['cell_area_in_ua_km2'].median():.3f} km²")
    frac = grid["cell_area_in_ua_km2"] / grid["cell_area_km2"]
    print(f"  cells >=90% inside UA: {int((frac>=0.9).sum()):,} "
          f"| <10% inside (slivers): {int((frac<0.1).sum()):,}")

    # --- assign segments to cells by midpoint ------------------------------
    seg_m = seg.to_crs(metric)
    seg_m["mid_geom"] = midpoints(seg_m.geometry)
    mids = gpd.GeoDataFrame(
        {"_i": np.arange(len(seg_m))}, geometry=seg_m["mid_geom"].values, crs=metric
    )
    joined = gpd.sjoin(mids, grid[["cell_id", "geometry"]], how="left", predicate="within")
    joined = joined.drop_duplicates(subset="_i")            # a midpoint on a shared edge
    seg_m = seg_m.reset_index(drop=True)
    seg_m["cell_id"] = joined.sort_values("_i")["cell_id"].values
    n_nocell = int(seg_m["cell_id"].isna().sum())
    print(f"\n  segments assigned to a cell: {len(seg_m)-n_nocell:,} "
          f"(unassigned {n_nocell})")
    if n_nocell:
        print("    note: unassigned midpoints fall outside the UA-clipped grid; "
              "these are edge segments whose midpoint sits just outside the UA.")
    occ = seg_m["cell_id"].value_counts()
    print(f"  occupied cells: {occ.size:,} of {len(grid):,}")
    print(f"  segments per occupied cell: min {occ.min()}, median {occ.median():.0f}, "
          f"max {occ.max()}")
    print(f"  cells with 1 segment only: {int((occ==1).sum()):,} "
          f"(singletons contribute no within-cell variance)")

    # --- write segments + grid ---------------------------------------------
    outdir = paths.processed(city_key)
    seg_out = seg_m.drop(columns=["mid_geom"]).to_crs("EPSG:4326")
    seg_fp_out = outdir / "segments.parquet"
    seg_out.to_parquet(seg_fp_out, index=False)
    grid_fp = outdir / "grid.parquet"
    grid.to_crs("EPSG:4326").to_parquet(grid_fp, index=False)
    validate.report_gdf(seg_out, "Analysis segments", expect_crs="EPSG:4326")
    print(f"  wrote {seg_fp_out.relative_to(paths.ROOT)} ({seg_fp_out.stat().st_size/1e6:.1f} MB)")
    print(f"  wrote {grid_fp.relative_to(paths.ROOT)} ({grid_fp.stat().st_size/1e6:.1f} MB)")

    # --- catchment buffers at every radius ---------------------------------
    print(f"\n=== catchment buffers (MAUP sweep) ===")
    radii = conf["catchment"]["radii_m"]
    primary = conf["catchment"]["primary_radius_m"]
    ua_geom_m = ua_m.geometry.iloc[0]
    written = []
    for r in radii:
        buf = seg_m[["segment_uid", "route_id", "cell_id"]].copy()
        geom = seg_m.geometry.buffer(r)
        cat = gpd.GeoDataFrame(buf, geometry=geom.values, crs=metric)
        cat["catch_area_km2"] = cat.geometry.area / 1e6
        cat["catch_area_in_ua_km2"] = cat.geometry.intersection(ua_geom_m).area / 1e6
        tag = "  [PRIMARY]" if r == primary else ""
        print(f"  r={r:>4} m: {len(cat):,} catchments, "
              f"area median {cat['catch_area_km2'].median():.3f} km², "
              f"in-UA median {cat['catch_area_in_ua_km2'].median():.3f} km²{tag}")
        fp = outdir / f"catchments_r{r}.parquet"
        cat.to_crs("EPSG:4326").to_parquet(fp, index=False)
        written.append((r, fp, len(cat)))

    # Overlap diagnostic for the primary radius — the D-021 evidence.
    r = primary
    cat = gpd.read_parquet(outdir / f"catchments_r{r}.parquet").to_crs(metric)
    sample = cat.sample(min(400, len(cat)), random_state=conf["reproducibility"]["random_seed"])
    sj = gpd.sjoin(sample[["geometry"]], cat[["geometry"]], predicate="intersects")
    n_overlap = sj.groupby(level=0).size() - 1
    print(f"\n  D-021 overlap check at r={r} m (400-catchment sample):")
    print(f"    other catchments intersected: median {n_overlap.median():.0f}, "
          f"mean {n_overlap.mean():.1f}, max {n_overlap.max()}")
    print("    -> confirms catchments are heavily nested; spatial specification "
          "is primary, not robustness.")

    for r, fp, n in written:
        provenance.log(city=city_key, layer=f"catchments_r{r}", source_url="derived: 01d + 01b",
                       rows=n, file_path=fp)
    provenance.log(city=city_key, layer="analysis_segments", source_url="derived: 01d",
                   rows=len(seg_out), file_path=seg_fp_out)
    provenance.log(city=city_key, layer="grid_1mi2", source_url="derived: 01b",
                   rows=len(grid), file_path=grid_fp)
    provenance.log_progress(
        "02a_analysis_frame",
        f"{city_key}: {len(seg_out):,} two-way segments in {occ.size:,} of {len(grid):,} "
        f"1 mi² cells; catchments at {radii} m",
    )
    print("\nStage 2a complete.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
