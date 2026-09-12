#!/usr/bin/env python
"""Stage 1b — acquire Census geography: the Urban Area extent and tract boundaries.

Keyless. TIGER/Line shapefiles are served over plain HTTPS with no credentials,
verified 2026-07-30. This is deliberately separated from 01c (ACS attributes),
which DOES need an API key — so the geometry half of the density layer can be
built and validated today regardless of key status.

Sources
-------
  Urban Areas 2020 : https://www2.census.gov/geo/tiger/TIGER2023/UAC/tl_2023_us_uac20.zip
  Tracts (CO)      : https://www2.census.gov/geo/tiger/TIGER2023/TRACT/tl_2023_08_tract.zip

Usage
-----
    uv run python code/01_acquire/01b_census_geography.py --city denver

Outputs (GeoPackage, EPSG:4326)
-------
    data/raw/<city>/census/urban_area.gpkg   single UA polygon
    data/raw/<city>/census/tracts.gpkg       tracts intersecting the UA
"""

from __future__ import annotations

import argparse
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

import geopandas as gpd
import pandas as pd
import requests

from lib import cfg, paths, provenance, validate


def download(url: str, dest: pathlib.Path, label: str) -> pathlib.Path:
    """Stream a file to disk, skipping if already present (raw is write-once)."""
    if dest.exists() and dest.stat().st_size > 0:
        print(f"  [cached] {label}: {dest.name} ({dest.stat().st_size:,} bytes)")
        return dest
    print(f"  downloading {label} ...")
    with requests.get(url, stream=True, timeout=300) as r:
        r.raise_for_status()
        with open(dest, "wb") as f:
            for chunk in r.iter_content(1 << 20):
                f.write(chunk)
    print(f"  wrote {dest.name} ({dest.stat().st_size:,} bytes)")
    return dest


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--city", default=None)
    args = ap.parse_args()

    conf = cfg.config()
    city_key = args.city or conf["project"]["pilot_city"]
    C = cfg.city(city_key)
    outdir = paths.raw(city_key, "census")

    print(f"Environment: {provenance.environment_stamp()}")
    print(f"City: {city_key} ({C['label']})")

    # --- 1. Urban Area polygon ---------------------------------------------
    ua_url = C["extent"].get("tiger_uac_url") or conf["sources"]["uac_url"]
    # D-051: `uace20` may be a LIST. Choi & Ewing's Wasatch Front study region spans
    # three separate Census urban areas (Salt Lake City, Ogden--Layton, Provo--Orem);
    # treating it as one analytic extent is what makes the comparison meaningful.
    raw_uace = C["extent"]["uace20"]
    uace_list = [str(u) for u in (raw_uace if isinstance(raw_uace, list) else [raw_uace])]
    uace = uace_list[0]
    print(f"\n=== Urban Area(s) (UACE20 = {', '.join(uace_list)}) ===")
    ua_zip = download(ua_url, outdir / "tl_2023_us_uac20.zip", "national urban areas")

    ua_all = gpd.read_file(f"zip://{ua_zip}")
    print(f"  national urban areas in file: {len(ua_all):,}")
    ua = ua_all[ua_all["UACE20"].isin(uace_list)].copy()
    if len(ua) != len(uace_list):
        raise validate.ValidationError(
            f"Expected {len(uace_list)} urban area(s) {uace_list}, found {len(ua)}."
        )
    for nm in ua["NAMELSAD20"]:
        print(f"  matched: {nm}")
    if len(ua) > 1:
        diss = ua.dissolve().reset_index(drop=True)
        diss["NAMELSAD20"] = " + ".join(ua["NAMELSAD20"].tolist())
        diss["UACE20"] = "+".join(uace_list)
        ua = diss
        print(f"  dissolved {len(uace_list)} urban areas into one analytic extent")

    ua = ua.to_crs("EPSG:4326")
    validate.report_gdf(ua, "Urban Area polygon", expect_crs="EPSG:4326")

    # Cross-check reported land area against the config value.
    metric = conf["crs"]["metric"]
    area_m2 = float(ua.to_crs(metric).geometry.area.iloc[0])
    expected = float(C["extent"]["area_land_m2"])
    print(f"  computed area (incl. water): {area_m2/1e6:,.1f} km²")
    print(f"  TIGER ALAND20 (land only)  : {expected/1e6:,.1f} km²")
    ratio = area_m2 / expected
    print(f"  ratio computed/land        : {ratio:.3f}  (>1 expected: includes water)")
    if not 0.95 <= ratio <= 1.15:
        print("  !! WARNING: area ratio outside expected range — check UA identity/CRS")

    ua_fp = outdir / "urban_area.gpkg"
    ua.to_file(ua_fp, layer="urban_area", driver="GPKG")
    print(f"  wrote {ua_fp.relative_to(paths.ROOT)}")

    # --- 2. Tracts intersecting the UA -------------------------------------
    sts = cfg.states(city_key)
    print(f"\n=== Tracts ({len(sts)} state(s): {[s['fips'] for s in sts]}) ===")
    frames, tr_url = [], None
    for st in sts:
        tr_url = (C["census"].get("tract_geometry_url") if len(sts) == 1
                  and C["census"].get("tract_geometry_url")
                  else cfg.url_for("tract_url", st))
        z = download(tr_url, outdir / pathlib.Path(tr_url).name,
                     f"tracts FIPS {st['fips']}")
        g = gpd.read_file(f"zip://{z}").to_crs("EPSG:4326")
        print(f"  tracts in FIPS {st['fips']}: {len(g):,}")
        frames.append(g)
    tracts = pd.concat(frames, ignore_index=True)
    tracts = gpd.GeoDataFrame(tracts, geometry="geometry", crs="EPSG:4326")
    print(f"  tracts pooled: {len(tracts):,}")

    # Spatial subset: tracts whose interior intersects the UA polygon.
    ua_geom = ua.geometry.iloc[0]
    hit = tracts[tracts.intersects(ua_geom)].copy()
    print(f"  tracts intersecting UA: {len(hit):,}")

    hit["state_fips"] = hit["GEOID"].str[:2]
    print(f"  states represented    : {sorted(hit['state_fips'].unique().tolist())}")
    counties = sorted(hit["COUNTYFP"].unique().tolist())
    print(f"  counties represented  : {counties}")
    expected_counties = set(C.get("county_fips") or [])
    extra = set(counties) - expected_counties
    missing = expected_counties - set(counties)
    if extra:
        print(f"  note: counties present but not in config: {sorted(extra)}")
    if missing:
        print(f"  note: config counties with no intersecting tract: {sorted(missing)}")

    # Tract land area, for the density denominator.
    hit["aland_km2"] = hit["ALAND"].astype(float) / 1e6
    validate.report_gdf(hit, "Tracts intersecting UA", expect_crs="EPSG:4326")
    validate.report_df(hit, "Tract attributes", key_cols=["GEOID", "COUNTYFP", "aland_km2"])

    tr_fp = outdir / "tracts.gpkg"
    hit.to_file(tr_fp, layer="tracts", driver="GPKG")
    print(f"  wrote {tr_fp.relative_to(paths.ROOT)}")

    # --- provenance ---------------------------------------------------------
    provenance.log(
        city=city_key, layer="census_urban_area", source_url=ua_url,
        rows=len(ua), file_path=ua_fp,
    )
    provenance.log(
        city=city_key, layer="census_tracts", source_url=tr_url,
        rows=len(hit), file_path=tr_fp,
    )
    provenance.log_progress(
        "01b_census_geography",
        f"{city_key}: UA {uace} ({area_m2/1e6:,.0f} km²) + {len(hit):,} tracts "
        f"across {len(counties)} counties",
    )
    print("\nStage 1b complete.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
