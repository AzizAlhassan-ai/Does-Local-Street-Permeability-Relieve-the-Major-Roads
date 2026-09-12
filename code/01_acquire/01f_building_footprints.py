#!/usr/bin/env python
"""Stage 1f — acquire building footprints for the Urban Area extent.

Supplies the `built_density` control (footprint area / buffer area, config.yml
`controls.secondary`). Source is the Microsoft Global Building Footprints
release: a set of gzipped newline-delimited GeoJSON tiles indexed by zoom-9
Bing/slippy-map quadkey, listed in a single manifest CSV.

Keyless. `cities.yml` marks this source `status: TODO_VERIFY`; this script
establishes coverage empirically rather than assuming it — it resolves the
manifest, reports its schema, and reports which RegionName/quadkey rows match
the AOI. If no manifest row matches the AOI quadkeys it stops instead of
improvising.

The AOI is read from the Urban Area polygon written by 01b (DECISION D-005).
No AOI coordinates appear in this file: the bounding box that selects quadkeys
and the polygon that selects features are both derived from that file on disk.

Sources
-------
  Manifest : cities.yml denver.land_use.building_footprints.dataset_links
  Tiles    : URLs read from the manifest (never constructed here)

Usage
-----
    uv run python code/01_acquire/01f_building_footprints.py --city denver

Outputs (EPSG:4326)
-------
    data/raw/<city>/building_footprints/footprints_ua.parquet   (GeoParquet;
        falls back to .gpkg if the Parquet engine is unavailable)

Notes
-----
  * Footprint geometries are NOT truncated at the UA boundary. Features are
    selected by intersecting the UA polygon and kept whole, because
    `footprint_area_m2` must be the true area of the building. Truncating at
    the boundary would bias built_density downward for edge buffers. The count
    of boundary-straddling buildings is reported so the effect is auditable.
  * SIZE GUARD: nothing is written if the clipped result exceeds
    MAX_FEATURES or MAX_OUTPUT_BYTES. The script reports the numbers and exits
    non-zero so the thresholds can be raised deliberately.
"""

from __future__ import annotations

import argparse
import csv
import math
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

import geopandas as gpd
import pandas as pd
import pyogrio
import requests
import shapely

from lib import cfg, paths, provenance, validate

# --- SIZE GUARD thresholds -------------------------------------------------
# Refuse to write an unmanageably large extract rather than silently sampling.
# TODO: promote to config.yml (see final report) once a second city is added.
MAX_FEATURES = 5_000_000
MAX_OUTPUT_BYTES = 3 * 1024**3  # ~3 GB

# Implausibility screen for a building footprint, m². Reporting-only: nothing
# is dropped. 5 m² is smaller than a garden shed; 200,000 m² is larger than any
# single-footprint structure in a US metro outside a handful of megastructures.
MIN_PLAUSIBLE_AREA_M2 = 5.0
MAX_PLAUSIBLE_AREA_M2 = 200_000.0


def download(url: str, dest: pathlib.Path, label: str) -> pathlib.Path:
    """Stream a file to disk, skipping if already present (raw is write-once)."""
    if dest.exists() and dest.stat().st_size > 0:
        print(f"  [cached] {label}: {dest.name} ({dest.stat().st_size:,} bytes)")
        return dest
    print(f"  downloading {label} ...")
    dest.parent.mkdir(parents=True, exist_ok=True)
    tmp = dest.with_suffix(dest.suffix + ".part")
    with requests.get(url, stream=True, timeout=600) as r:
        r.raise_for_status()
        with open(tmp, "wb") as f:
            for chunk in r.iter_content(1 << 20):
                f.write(chunk)
    tmp.replace(dest)
    print(f"  wrote {dest.name} ({dest.stat().st_size:,} bytes)")
    return dest


# --- slippy-map / quadkey math --------------------------------------------
# `mercantile` is not a project dependency; this is the standard Web-Mercator
# tiling used by Bing Maps and by the Microsoft footprints partitioning.


def tile_xy(lon: float, lat: float, zoom: int) -> tuple[int, int]:
    """Web-Mercator tile column/row containing (lon, lat) at `zoom`."""
    n = 1 << zoom
    x = int((lon + 180.0) / 360.0 * n)
    y = int((1.0 - math.asinh(math.tan(math.radians(lat))) / math.pi) / 2.0 * n)
    return min(max(x, 0), n - 1), min(max(y, 0), n - 1)


def quadkey(x: int, y: int, zoom: int) -> str:
    """Bing quadkey string for tile (x, y, zoom)."""
    digits = []
    for i in range(zoom, 0, -1):
        bit = 1 << (i - 1)
        d = 0
        if x & bit:
            d += 1
        if y & bit:
            d += 2
        digits.append(str(d))
    return "".join(digits)


def quadkeys_for_bounds(bounds: tuple[float, float, float, float], zoom: int) -> list[str]:
    """All quadkeys at `zoom` whose tiles intersect a WGS84 (minx,miny,maxx,maxy) box."""
    minx, miny, maxx, maxy = bounds
    x0, y0 = tile_xy(minx, maxy, zoom)   # NW corner
    x1, y1 = tile_xy(maxx, miny, zoom)   # SE corner
    return [
        quadkey(x, y, zoom)
        for x in range(min(x0, x1), max(x0, x1) + 1)
        for y in range(min(y0, y1), max(y0, y1) + 1)
    ]


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--city", default=None)
    args = ap.parse_args()

    conf = cfg.config()
    city_key = args.city or conf["project"]["pilot_city"]
    C = cfg.city(city_key)
    B = cfg.land_use(city_key)["building_footprints"]
    metric = conf["crs"]["metric"]
    geographic = conf["crs"]["geographic"]
    zoom = int(B["quadkey_zoom"])

    outdir = paths.raw(city_key, "building_footprints")
    tiledir = paths.CACHE / "ms_global_buildings"
    tiledir.mkdir(parents=True, exist_ok=True)

    print(f"Environment: {provenance.environment_stamp()}")
    print(f"City: {city_key} ({C['label']})")
    print(f"Source: {B['name']}  (config status: {B.get('status')})")

    out_parquet = outdir / "footprints_ua.parquet"
    out_gpkg = outdir / "footprints_ua.gpkg"
    for existing in (out_parquet, out_gpkg):
        if existing.exists() and existing.stat().st_size > 0:
            print(
                f"\n[cached] {existing.relative_to(paths.ROOT)} "
                f"({existing.stat().st_size:,} bytes) — raw/ is write-once, nothing to do.\n"
                "Delete the file to force a re-acquisition."
            )
            return 0

    # --- 1. AOI: the Urban Area polygon from 01b ---------------------------
    ua_fp = paths.raw(city_key, "census") / "urban_area.gpkg"
    if not ua_fp.exists() or ua_fp.stat().st_size == 0:
        print(
            f"\nERROR: missing {ua_fp.relative_to(paths.ROOT)}.\n"
            "  The AOI for this stage is the Census Urban Area polygon (DECISION D-005).\n"
            "  Run first:  uv run python code/01_acquire/01b_census_geography.py "
            f"--city {city_key}",
            file=sys.stderr,
        )
        return 1

    ua = gpd.read_file(ua_fp).to_crs(geographic)
    if len(ua) != 1:
        raise validate.ValidationError(
            f"Expected exactly 1 UA polygon in {ua_fp.name}, found {len(ua)}."
        )
    ua_geom = ua.geometry.iloc[0]
    ua_bounds = tuple(float(v) for v in ua.total_bounds)
    ua_land_m2 = float(C["extent"]["area_land_m2"])
    print(f"\n=== AOI ===")
    print(f"  {ua.iloc[0]['NAMELSAD20']}  (UACE20 {ua.iloc[0]['UACE20']})")
    print(f"  bbox (minx,miny,maxx,maxy): "
          f"({ua_bounds[0]:.6f}, {ua_bounds[1]:.6f}, {ua_bounds[2]:.6f}, {ua_bounds[3]:.6f})")
    print(f"  TIGER ALAND20             : {ua_land_m2/1e6:,.1f} km²")

    # --- 2. Verify the manifest resolves, and report its schema ------------
    links_url = B["dataset_links"]
    print(f"\n=== Dataset manifest ===")
    print(f"  {links_url}")
    links_fp = download(links_url, tiledir / "dataset-links.csv", "dataset-links manifest")

    with open(links_fp, newline="") as f:
        reader = csv.DictReader(f)
        fieldnames = list(reader.fieldnames or [])
        rows = list(reader)
    if not rows:
        raise validate.ValidationError(f"Manifest at {links_url} parsed to 0 rows.")
    print(f"  schema  : {fieldnames}")
    print(f"  rows    : {len(rows):,}")
    print(f"  regions : {len(set(r['Location'] for r in rows)):,}")
    print(f"  example : {rows[0]}")

    for required in ("Location", "QuadKey", "Url"):
        if required not in fieldnames:
            raise validate.ValidationError(
                f"Manifest schema changed: no {required!r} column. Got {fieldnames}."
            )

    # --- 3. Quadkeys intersecting the AOI bbox -> matching manifest rows ---
    qks = quadkeys_for_bounds(ua_bounds, zoom)
    print(f"\n=== Quadkeys (zoom {zoom}) ===")
    print(f"  needed ({len(qks)}): {qks}")

    by_qk: dict[str, list[dict]] = {q: [] for q in qks}
    for r in rows:
        if r["QuadKey"] in by_qk:
            by_qk[r["QuadKey"]].append(r)
    for q in qks:
        hits = by_qk[q]
        regions = sorted(set(h["Location"] for h in hits))
        sizes = [h.get("Size", "?") for h in hits]
        print(f"  {q}: {len(hits)} link(s)  regions={regions}  sizes={sizes}")

    matched = [h for q in qks for h in by_qk[q]]
    if not matched:
        print(
            "\nERROR: the manifest resolved, but NO row matches any AOI quadkey.\n"
            f"  quadkeys searched: {qks}\n"
            f"  This source does not cover {C['label']}. Stopping — nothing written.\n"
            "  Set land_use.building_footprints.status accordingly and choose another\n"
            "  source (e.g. Overture Maps buildings).",
            file=sys.stderr,
        )
        return 1

    regions = sorted(set(h["Location"] for h in matched))
    print(f"  US/Colorado coverage confirmed: regions supplying AOI tiles = {regions}")

    # --- 4. Stream each tile, filter to the UA polygon ---------------------
    print(f"\n=== Tiles ===")
    parts: list[gpd.GeoDataFrame] = []
    raw_total = 0
    bytes_on_disk = 0
    for h in matched:
        qk = h["QuadKey"]
        # Local name ends .geojsonl.gz so GDAL picks the GeoJSONSeq driver
        # through /vsigzip/ (the published name is .csv.gz, but the payload is
        # newline-delimited GeoJSON — verified 2026-07-30).
        dest = tiledir / f"{h['Location']}_{qk}.geojsonl.gz"
        download(h["Url"], dest, f"tile {qk} ({h.get('Size', '?')})")
        bytes_on_disk += dest.stat().st_size

        vsi = f"/vsigzip/{dest}"
        n_raw = int(pyogrio.read_info(vsi)["features"])
        raw_total += n_raw

        # bbox pre-filter in GDAL (cheap, sequential), then exact polygon test.
        part = pyogrio.read_dataframe(vsi, bbox=ua_bounds, fid_as_index=True)
        n_bbox = len(part)
        part = part.set_crs(geographic, allow_override=True)
        part = part[part.geometry.intersects(ua_geom)].copy()
        part["id"] = [f"msgb_{qk}_{fid}" for fid in part.index]
        part["quadkey"] = qk
        print(f"  {qk}: raw={n_raw:,}  in bbox={n_bbox:,}  in UA polygon={len(part):,}")
        parts.append(part.reset_index(drop=True))

    gdf = gpd.GeoDataFrame(
        pd.concat(parts, ignore_index=True), geometry="geometry", crs=geographic
    )
    del parts
    print(f"\n  raw features across {len(matched)} tile(s): {raw_total:,}")
    print(f"  features after clipping to UA polygon    : {len(gdf):,}")
    print(f"  tile bytes cached on disk                : {bytes_on_disk:,}")
    if len(gdf) == 0:
        raise validate.ValidationError(
            "0 features inside the UA polygon — coverage gap or CRS/axis error."
        )

    # Boundary fidelity: how many footprints straddle the UA edge?
    straddle = int((~gdf.geometry.within(ua_geom)).sum())
    print(f"  footprints straddling the UA boundary    : {straddle:,} "
          f"({100*straddle/len(gdf):.3f}%) — kept whole, not truncated")

    # --- 5. footprint_area_m2 in the metric CRS ----------------------------
    print(f"\n=== Footprint area ({metric}) ===")
    gdf["footprint_area_m2"] = gdf.to_crs(metric).geometry.area.astype("float64")

    # --- SIZE GUARD --------------------------------------------------------
    wkb_bytes = int(sum(len(b) for b in shapely.to_wkb(gdf.geometry.to_numpy())))
    # Multiplier is the worst case of the two writers: measured 2.36x WKB for the
    # GeoPackage fallback (geometry + attributes + the R-tree spatial index),
    # against ~1.35x for GeoParquet. Calibrated on the Denver run, 2026-07-30.
    est_bytes = int(wkb_bytes * 2.5)
    print(f"\n=== SIZE GUARD ===")
    print(f"  features to write     : {len(gdf):,}  (limit {MAX_FEATURES:,})")
    print(f"  geometry WKB bytes    : {wkb_bytes:,}")
    print(f"  estimated output bytes: {est_bytes:,}  (limit {MAX_OUTPUT_BYTES:,})")
    if len(gdf) > MAX_FEATURES or est_bytes > MAX_OUTPUT_BYTES:
        print(
            "\nSTOP: clipped extract exceeds the size guard. NOTHING WRITTEN.\n"
            f"  features {len(gdf):,} vs limit {MAX_FEATURES:,}\n"
            f"  bytes ~{est_bytes:,} vs limit {MAX_OUTPUT_BYTES:,}\n"
            "  Not truncating and not sampling. Raise MAX_FEATURES/MAX_OUTPUT_BYTES\n"
            "  deliberately, or narrow the extent, then re-run.",
            file=sys.stderr,
        )
        return 2
    print("  within guard: OK")

    # --- validation --------------------------------------------------------
    keep = ["id", "quadkey", "height", "confidence", "footprint_area_m2", "geometry"]
    gdf = gdf[[c for c in keep if c in gdf.columns]]

    validate.report_gdf(gdf, "Building footprints (UA)", expect_crs=geographic)
    validate.check_coords_plausible(gdf, "Building footprints (UA)", list(ua_bounds))
    validate.report_df(
        gdf.drop(columns="geometry"),
        "Footprint attributes",
        key_cols=["id", "footprint_area_m2", "height", "confidence"],
    )

    a = gdf["footprint_area_m2"]
    n_small = int((a < MIN_PLAUSIBLE_AREA_M2).sum())
    n_large = int((a > MAX_PLAUSIBLE_AREA_M2).sum())
    print(f"\n--- footprint_area_m2 distribution ---")
    print(f"  min    : {a.min():,.2f}")
    print(f"  p25    : {a.quantile(0.25):,.2f}")
    print(f"  median : {a.median():,.2f}")
    print(f"  mean   : {a.mean():,.2f}")
    print(f"  p75    : {a.quantile(0.75):,.2f}")
    print(f"  p99    : {a.quantile(0.99):,.2f}")
    print(f"  max    : {a.max():,.2f}")
    print(f"  < {MIN_PLAUSIBLE_AREA_M2:g} m²  : {n_small:,} ({100*n_small/len(a):.4f}%)")
    print(f"  > {MAX_PLAUSIBLE_AREA_M2:,.0f} m² : {n_large:,} ({100*n_large/len(a):.4f}%)")
    if not 80.0 <= a.median() <= 600.0:
        print("  !! WARNING: median footprint outside the low-hundreds-of-m² range "
              "expected for US residential fabric — check CRS and clipping")

    built_km2 = float(a.sum()) / 1e6
    share = built_km2 / (ua_land_m2 / 1e6)
    print(f"\n--- built area vs UA ---")
    print(f"  total built area : {built_km2:,.1f} km²")
    print(f"  UA land area     : {ua_land_m2/1e6:,.1f} km²")
    print(f"  built share      : {100*share:.2f}%")
    if not 0.02 <= share <= 0.25:
        print("  !! WARNING: built share outside the ~2-25% band typical of US urban areas")

    # --- 6. write GeoParquet, falling back to GeoPackage -------------------
    print(f"\n=== Write ===")
    out_fp = out_parquet
    fmt = "GeoParquet"
    try:
        gdf.to_parquet(out_parquet, index=False)
    except Exception as exc:  # noqa: BLE001 — any engine failure falls back
        print(f"  !! GeoParquet write FAILED ({type(exc).__name__}: {exc})")
        print("  !! falling back to GeoPackage — output is .gpkg, not .parquet")
        if out_parquet.exists():
            out_parquet.unlink()
        gdf.to_file(out_gpkg, layer="footprints_ua", driver="GPKG")
        out_fp = out_gpkg
        fmt = "GeoPackage (GeoParquet unavailable)"
    size = out_fp.stat().st_size
    print(f"  format : {fmt}")
    print(f"  wrote  : {out_fp.relative_to(paths.ROOT)} ({size:,} bytes, {size/1e6:,.1f} MB)")
    print(f"  peak disk (cached tiles + manifest + output): "
          f"{(bytes_on_disk + links_fp.stat().st_size + size)/1e6:,.1f} MB")

    # --- provenance --------------------------------------------------------
    provenance.log(
        city=city_key, layer="building_footprints", source_url=links_url,
        rows=len(gdf), file_path=out_fp,
    )
    provenance.log_progress(
        "01f_building_footprints",
        f"{city_key}: {len(gdf):,} MS Global Building Footprints in UA "
        f"({len(qks)} zoom-{zoom} quadkeys, {len(matched)} tiles); "
        f"median {a.median():,.0f} m², built area {built_km2:,.0f} km² "
        f"= {100*share:.1f}% of UA land",
    )
    print("\nStage 1f complete.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
