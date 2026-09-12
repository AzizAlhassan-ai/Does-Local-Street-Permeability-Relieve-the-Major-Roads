#!/usr/bin/env python
"""Stage 3a — aggregate every control variable into each catchment.

No HPMS<->OSM conflation is needed for any of this: catchments are buffers drawn
around HPMS geometry directly, so all controls reach the segment by spatial join.
(Conflation is required only for betweenness — see 02c.)

Applies:
  D-019  poi_density excludes parking and street furniture
  D-020  land-use entropy is re-pooled from raw sector counts at BUFFER level,
         never averaged from block-level entropy
  D-024  point-in-buffer assignment, consistent with the permeability metrics
  D-006  dist_cbd_km and median_year_structure_built as first-class controls

Density/vintage come from tracts by AREA-WEIGHTED mean over the buffer's overlap,
not from the segment midpoint's tract — an 800 m buffer routinely spans several
tracts, and midpoint assignment would throw that information away.

Depends on: 01c, 01e, 01f, 02a

Usage
-----
    uv run python code/03_conflate/03a_controls.py --city denver
    uv run python code/03_conflate/03a_controls.py --city denver --radii 800

Outputs
-------
    data/processed/<city>/controls_r<R>.parquet
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

TRACT_VARS = [
    "pop_density_km2", "housing_density_km2", "median_year_structure_built",
    "pct_no_vehicle", "avg_household_size",
]


def normalised_entropy(counts: np.ndarray, min_sectors: int) -> np.ndarray:
    """Row-wise normalised Shannon entropy over sector counts (D-020).

    E = -sum(p_i ln p_i) / ln(k), where k is the number of non-zero sectors.
    NA where total == 0 or k < min_sectors — 'no mix' is undefined, not zero.
    """
    tot = counts.sum(axis=1)
    k = (counts > 0).sum(axis=1)
    out = np.full(len(counts), np.nan)
    ok = (tot > 0) & (k >= min_sectors)
    if not ok.any():
        return out
    # Explicit `out` so no element is ever read uninitialised. `ok` already
    # guarantees tot > 0, but relying on that implicitly is fragile.
    p = np.zeros_like(counts[ok], dtype=float)
    np.divide(counts[ok], tot[ok, None], out=p, where=tot[ok, None] > 0)
    with np.errstate(divide="ignore", invalid="ignore"):
        lp = np.where(p > 0, np.log(p), 0.0)
    out[ok] = -(p * lp).sum(axis=1) / np.log(k[ok])
    return out


def area_weighted_tracts(cat: gpd.GeoDataFrame, tr: gpd.GeoDataFrame,
                         cid: str) -> pd.DataFrame:
    """Area-weighted mean of tract variables over each catchment's overlap."""
    ov = gpd.overlay(cat[[cid, "geometry"]], tr, how="intersection",
                     keep_geom_type=True)
    ov["w"] = ov.geometry.area
    rows = {}
    for v in TRACT_VARS:
        if v not in ov.columns:
            continue
        d = ov[[cid, v, "w"]].dropna(subset=[v])
        num = (d[v] * d["w"]).groupby(d[cid]).sum()
        den = d["w"].groupby(d[cid]).sum()
        rows[v] = num / den
    out = pd.DataFrame(rows)
    # how much of each buffer was covered by a tract carrying a value at all
    cov = ov.groupby(cid)["w"].sum()
    out["tract_overlap_km2"] = cov / 1e6
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--city", default=None)
    ap.add_argument("--radii", type=int, nargs="*", default=None)
    args = ap.parse_args()

    conf = cfg.config()
    city_key = args.city or conf["project"]["pilot_city"]
    C = cfg.city(city_key)
    metric = conf["crs"]["metric"]
    lu = cfg.land_use(city_key)

    print(f"Environment: {provenance.environment_stamp()}")
    print(f"City: {city_key} ({C['label']})")

    proc = paths.processed(city_key)
    need = {
        "tracts": proc / "tract_density.gpkg",
        "lodes": proc / "lodes_blocks.gpkg",
        "pois": paths.raw(city_key, "osm_poi") / "pois.gpkg",
        "footprints": paths.raw(city_key, "building_footprints") / "footprints_ua.parquet",
        "segments": proc / "segments.parquet",
    }
    # D-080: the POI layer supplies `poi_density`, which config.yml lists as a
    # SECONDARY control and which no primary model uses. Overpass can throttle a
    # whole-urban-area POI query for a long time, and blocking the entire control
    # assembly on an optional layer is the wrong trade. Every other layer is still
    # mandatory. When POIs are absent the columns are written as NaN, loudly, and
    # the gap is recorded in the provenance log rather than silently filled.
    OPTIONAL = {"pois"}
    have_pois = need["pois"].exists()
    for k, fp in need.items():
        if not fp.exists():
            if k in OPTIONAL:
                print(f"WARNING: optional layer {k} missing at "
                      f"{fp.relative_to(paths.ROOT)} — poi_density will be NaN "
                      f"(secondary control; no primary model uses it)")
                continue
            print(f"ERROR: {k} missing at {fp.relative_to(paths.ROOT)}")
            return 1

    # --- load once ----------------------------------------------------------
    print("\n=== loading control layers ===")
    tr = gpd.read_file(need["tracts"]).to_crs(metric)
    tr = tr[["GEOID"] + [c for c in TRACT_VARS if c in tr.columns]
            + ["acs_reliable", "is_special_use_tract", "geometry"]]
    print(f"  tracts        : {len(tr):,}")

    lodes = gpd.read_file(need["lodes"]).to_crs(metric)
    sectors = [c for c in lu["lodes"]["entropy_sectors"] if c in lodes.columns]
    print(f"  LODES blocks  : {len(lodes):,} ({len(sectors)} sector columns)")

    pois = gpd.read_file(need["pois"]).to_crs(metric) if have_pois else None
    n_poi_raw = len(pois) if pois is not None else 0
    excl = (lu["osm_poi"].get("exclude_values") or {}).get("amenity") or []
    if pois is None:
        print("  POIs          : ABSENT — poi_density_km2 written as NaN")
    elif "amenity" in pois.columns and excl:
        drop = pois["amenity"].isin(excl)
        pois = pois[~drop].copy()
        print(f"  POIs          : {n_poi_raw:,} raw -> {len(pois):,} destinations "
              f"(D-019 removed {int(drop.sum()):,} = {drop.mean():.1%})")
    else:
        print(f"  POIs          : {len(pois):,} (no exclusion list applied!)")

    fps = gpd.read_parquet(need["footprints"]).to_crs(metric)
    # Centroids must be taken in the METRIC CRS; computing them in EPSG:4326 is
    # geometrically wrong (geopandas warns) even if the error is small here.
    fp_pts = gpd.GeoDataFrame(
        fps[["footprint_area_m2"]].reset_index(drop=True),
        geometry=fps.geometry.centroid.values, crs=metric,
    )
    print(f"  footprints    : {len(fp_pts):,} (centroids)")

    seg = gpd.read_parquet(need["segments"]).to_crs(metric)
    cbd = gpd.GeoSeries.from_xy(
        [C["cbd"]["lon"]], [C["cbd"]["lat"]], crs="EPSG:4326"
    ).to_crs(metric).iloc[0]
    seg_mid = gpd.GeoSeries(
        [g.interpolate(0.5, normalized=True) for g in seg.geometry], crs=metric
    )
    dist = pd.DataFrame({
        "segment_uid": seg["segment_uid"].values,
        "dist_cbd_km": seg_mid.distance(cbd).values / 1e3,
    })
    print(f"  dist_cbd_km   : median {dist.dist_cbd_km.median():.2f}, "
          f"max {dist.dist_cbd_km.max():.2f} km "
          f"(anchor: {C['cbd']['note']})")

    min_sec = int(lu["lodes"].get("entropy_min_sectors", 2))
    radii = args.radii or conf["catchment"]["radii_m"]
    primary = conf["catchment"]["primary_radius_m"]
    written = []

    for r in radii:
        cat_fp = proc / f"catchments_r{r}.parquet"
        if not cat_fp.exists():
            print(f"\n  SKIP r={r}: {cat_fp.name} missing")
            continue
        cat = gpd.read_parquet(cat_fp).to_crs(metric).reset_index(drop=True)
        tag = "  [PRIMARY]" if r == primary else ""
        print(f"\n=== controls at r={r} m ({len(cat):,} catchments){tag} ===")
        area = cat["catch_area_km2"].values
        base = cat[["segment_uid", "catch_area_km2", "catch_area_in_ua_km2"]].copy()

        # --- tracts: area-weighted ---
        tw = area_weighted_tracts(cat, tr, "segment_uid")
        m = base.merge(tw, left_on="segment_uid", right_index=True, how="left")
        cov = m["tract_overlap_km2"] / m["catch_area_km2"]
        print(f"  tract coverage of buffer: median {cov.median():.3f}, "
              f"<0.5 on {int((cov<0.5).sum()):,} catchments")
        for v in TRACT_VARS:
            if v in m.columns:
                print(f"    {v:32s} non-null {int(m[v].notna().sum()):,}/{len(m):,}")

        # --- LODES: re-pool raw counts, THEN entropy (D-020) ---
        jl = gpd.sjoin(lodes[["C000"] + sectors + ["geometry"]],
                       cat[["segment_uid", "geometry"]], how="inner", predicate="within")
        pooled = jl.groupby("segment_uid")[sectors + ["C000"]].sum()
        ent = normalised_entropy(pooled[sectors].to_numpy(dtype=float), min_sec)
        pooled_out = pd.DataFrame({
            "lu_entropy": ent,
            "jobs_total": pooled["C000"].values,
            "n_sectors_present": (pooled[sectors].to_numpy() > 0).sum(axis=1),
        }, index=pooled.index)
        m = m.merge(pooled_out, left_on="segment_uid", right_index=True, how="left")
        m["jobs_total"] = m["jobs_total"].fillna(0)
        m["job_density_km2"] = m["jobs_total"] / m["catch_area_km2"]
        ne = m["lu_entropy"]
        print(f"  lu_entropy: non-null {int(ne.notna().sum()):,}/{len(m):,} "
              f"({ne.notna().mean():.1%}) | median {ne.median():.3f}")
        print(f"    D-020: entropy pooled at buffer level, not averaged from blocks")
        print(f"    catchments with zero jobs: {int((m['jobs_total']==0).sum()):,}")

        # --- POIs (optional layer, D-080) ---
        if pois is None:
            m["poi_count"] = np.nan
            m["poi_density_km2"] = np.nan
            print("  poi_density_km2: NaN (POI layer absent — secondary control)")
        else:
            jp = gpd.sjoin(pois[["geometry"]], cat[["segment_uid", "geometry"]],
                           how="inner", predicate="within")
            pc = jp.groupby("segment_uid").size().rename("poi_count")
            m = m.merge(pc, left_on="segment_uid", right_index=True, how="left")
            m["poi_count"] = m["poi_count"].fillna(0)
            m["poi_density_km2"] = m["poi_count"] / m["catch_area_km2"]
            print(f"  poi_density_km2: median {m.poi_density_km2.median():.2f}, "
                  f"p90 {m.poi_density_km2.quantile(.9):.2f}")

        # --- built density ---
        jf = gpd.sjoin(fp_pts, cat[["segment_uid", "geometry"]],
                       how="inner", predicate="within")
        fb = jf.groupby("segment_uid").agg(
            n_buildings=("footprint_area_m2", "size"),
            built_area_m2=("footprint_area_m2", "sum"),
        )
        m = m.merge(fb, left_on="segment_uid", right_index=True, how="left")
        m["n_buildings"] = m["n_buildings"].fillna(0)
        m["built_area_m2"] = m["built_area_m2"].fillna(0)
        m["built_density"] = m["built_area_m2"] / (m["catch_area_km2"] * 1e6)
        bd = m["built_density"]
        print(f"  built_density (footprint area / buffer area): "
              f"median {bd.median():.4f}, p90 {bd.quantile(.9):.4f}, max {bd.max():.4f}")
        if bd.max() > 1.0:
            print(f"    !! {int((bd>1).sum())} catchments exceed 1.0 — impossible, investigate")

        # --- distance to CBD ---
        m = m.merge(dist, on="segment_uid", how="left")

        validate.report_df(m, f"controls r={r}", key_cols=[
            "pop_density_km2", "median_year_structure_built", "lu_entropy",
            "poi_density_km2", "built_density", "dist_cbd_km"])

        fp_out = proc / f"controls_r{r}.parquet"
        m.to_parquet(fp_out, index=False)
        written.append((r, fp_out, len(m)))
        print(f"  wrote {fp_out.relative_to(paths.ROOT)} "
              f"({fp_out.stat().st_size/1e6:.2f} MB)")

    for r, fp, n in written:
        provenance.log(city=city_key, layer=f"controls_r{r}",
                       source_url="derived: 01c ACS + 01e LODES/POI + 01f footprints",
                       rows=n, file_path=fp)
    provenance.log_progress(
        "03a_controls",
        f"{city_key}: control variables aggregated into catchments at "
        f"{[r for r, _, _ in written]} m",
    )
    print("\nStage 3a complete.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
