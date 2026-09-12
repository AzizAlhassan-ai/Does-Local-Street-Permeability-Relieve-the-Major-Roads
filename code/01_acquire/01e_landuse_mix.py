#!/usr/bin/env python
"""Stage 1e — acquire the land-use mix controls: LODES employment + OSM POIs.

Two layers, both UA-wide, both keyless:

  A. LEHD LODES v8 Workplace Area Characteristics (WAC), Colorado. Census-block
     resolution job counts by NAICS sector, from which `lu_entropy` (normalised
     Shannon entropy over sectors) is computed. Block resolution is what makes an
     800 m-buffer land-use-mix measure meaningful — tracts are far too coarse.
  B. OSM amenity/shop/office features, for `poi_density`.

Block *locations* come from the TIGER tabblock20 DBF's INTPTLAT/INTPTLON
attributes (the Census-published internal point), read WITHOUT the polygon
geometry. The polygon layer for Colorado is ~128 MB zipped and is not needed:
every block is aggregated to a single representative point anyway.

Depends on: 01b_census_geography.py (needs data/raw/<city>/census/urban_area.gpkg)

Usage
-----
    uv run python code/01_acquire/01e_landuse_mix.py --city denver

Outputs
-------
    data/processed/<city>/lodes_blocks.gpkg   layer `blocks` — in-UA blocks,
                                              sector job counts + job_entropy
    data/raw/<city>/osm_poi/pois.gpkg         layer `pois`  — POI point reps
"""

from __future__ import annotations

import argparse
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

import geopandas as gpd
import numpy as np
import osmnx as ox
import pandas as pd
import pyogrio
import requests
import shapely

from lib import cfg, paths, provenance, validate

# --- schema facts, not tunable parameters --------------------------------------
# These are LODES/TIGER column *identities*. They are not analysis choices, so
# they live here rather than in config.yml; see the config recommendations in the
# Stage 1e report if they should be promoted.
LODES_TOTAL_JOBS = "C000"          # LODES WAC: total jobs at the workplace block
LODES_BLOCK_KEY = "w_geocode"      # LODES WAC: 15-digit 2020 census block GEOID
TIGER_GEOID_PREFIX = "GEOID"       # tabblock20 DBF -> GEOID20
TIGER_LAT_PREFIX = "INTPTLAT"      # tabblock20 DBF -> INTPTLAT20
TIGER_LON_PREFIX = "INTPTLON"      # tabblock20 DBF -> INTPTLON20
TIGER_UACE_PREFIX = "UACE"         # tabblock20 DBF -> UACE20 (cross-check only)
POI_NAME_FIELD = "name"

OSM_SOURCE_URL = "https://overpass-api.de/api/interpreter (OpenStreetMap, via OSMnx)"


# --- shared helpers ------------------------------------------------------------
def download(url: str, dest: pathlib.Path, label: str) -> pathlib.Path:
    """Stream a file to disk, skipping if already present (raw is write-once)."""
    if dest.exists() and dest.stat().st_size > 0:
        print(f"  [cached] {label}: {dest.name} ({dest.stat().st_size:,} bytes)")
        return dest
    print(f"  downloading {label} ...")
    with requests.get(url, stream=True, timeout=900) as r:
        r.raise_for_status()
        with open(dest, "wb") as f:
            for chunk in r.iter_content(1 << 20):
                f.write(chunk)
    print(f"  wrote {dest.name} ({dest.stat().st_size:,} bytes)")
    return dest


def probe(url: str) -> tuple[int, str]:
    """HEAD a URL, following redirects. Returns (status, content-length)."""
    try:
        r = requests.head(url, allow_redirects=True, timeout=60)
        return r.status_code, r.headers.get("content-length", "?")
    except requests.RequestException as e:
        return -1, f"{type(e).__name__}: {e}"


def verify_lodes_url(url_pattern: str, year: int) -> str:
    """Confirm the configured LODES URL resolves. Probe neighbours if it does not.

    Never silently substitutes a different year — a year swap would break the
    temporal alignment with HPMS 2018 (D-013), so it is reported, not applied.
    """
    url = url_pattern.format(year=year)
    status, size = probe(url)
    print(f"  HEAD {url}\n    -> HTTP {status}, content-length {size}")
    if status == 200:
        return url

    print("  !! configured LODES URL did NOT resolve. Probing adjacent years:")
    for y in range(year - 4, year + 6):
        if y == year:
            continue
        s, sz = probe(url_pattern.format(year=y))
        print(f"       {y}: HTTP {s}, content-length {sz}")
    listing = url_pattern.format(year=year).rsplit("/", 1)[0] + "/"
    print(f"  !! directory listing {listing}")
    try:
        r = requests.get(listing, timeout=60)
        print(f"       HTTP {r.status_code}, {len(r.text):,} chars of body")
        import re

        names = sorted(set(re.findall(r'href="([^"]+\.csv\.gz)"', r.text)))
        for n in names:
            print(f"       found: {n}")
    except requests.RequestException as e:
        print(f"       listing request failed: {type(e).__name__}: {e}")
    raise validate.ValidationError(
        f"LODES URL from config does not resolve (HTTP {status}): {url}. "
        "See probe output above; fix config/cities.yml rather than guessing here."
    )


def resolve_field(fields: list[str], prefix: str, where: str) -> str:
    """Find the one DBF field starting with `prefix` (TIGER suffixes by vintage)."""
    hits = [f for f in fields if f.upper().startswith(prefix.upper())]
    if len(hits) != 1:
        raise validate.ValidationError(
            f"Expected exactly 1 field starting with {prefix!r} in {where}, "
            f"found {hits}. Full schema: {fields}"
        )
    return hits[0]


# --- Part A: LODES -------------------------------------------------------------
def normalised_entropy(counts: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Row-wise normalised Shannon entropy over sector job counts.

        E = -sum(p_i ln p_i) / ln(k)

    with p_i the share of the row's jobs in sector i and k the number of sectors
    with non-zero jobs. Undefined (NaN) where the row has no jobs or k < 2 —
    a single-sector block is not "perfectly unmixed" on a 0-1 scale, it has no
    defined mix, and emitting 0 there would be a fabricated value.

    Returns (entropy, total_jobs, k).
    """
    counts = np.asarray(counts, dtype="float64")
    total = counts.sum(axis=1)
    k = (counts > 0).sum(axis=1)

    with np.errstate(divide="ignore", invalid="ignore"):
        p = counts / total[:, None]
        terms = np.where(counts > 0, p * np.log(p), 0.0)
        ent = -terms.sum(axis=1) / np.log(k)

    ent = np.where((total > 0) & (k >= 2), ent, np.nan)
    return ent, total, k


def build_lodes(city_key: str, C: dict, conf: dict) -> tuple[gpd.GeoDataFrame, str, str]:
    lod = cfg.land_use(city_key)["lodes"]
    sectors = list(lod["entropy_sectors"])
    year = int(lod["year"])

    print(f"\n=== A. LODES WAC {year} (config status: {lod.get('status', 'n/a')}) ===")
    sts = cfg.states(city_key)
    wac_urls = []
    for st in sts:
        tpl = (lod["url_pattern"] if len(sts) == 1 and st.get("abbrev") is None
               else conf["sources"]["lodes_url_tpl"].replace("{year}", "{year}")
                    .format(abbrev=st["abbrev"], year="{year}"))
        wac_urls.append((st, verify_lodes_url(tpl, year)))
    wac_url = wac_urls[0][1]

    # D-049: LODES is published per state, so a multi-state UA needs one download
    # per state, pooled. Loading only the first state would silently zero out
    # employment on the other side of the state line (Vancouver WA for Portland,
    # the NH fringe for Boston) and bias lu_entropy, a first-class control.
    lodes_dir = paths.raw(city_key, "lodes")
    wac_parts = []
    for st, u in wac_urls:
        fp_st = download(u, lodes_dir / pathlib.Path(u).name,
                         f"WAC {st['abbrev'] or st['fips']}")
        w_st = pd.read_csv(fp_st, dtype={LODES_BLOCK_KEY: "string"})
        w_st["state_fips"] = st["fips"]
        print(f"  LODES rows (FIPS {st['fips']}, blocks with >=1 job): {len(w_st):,}")
        wac_parts.append(w_st)
    wac = pd.concat(wac_parts, ignore_index=True)
    print(f"  LODES rows pooled across {len(wac_parts)} state(s): {len(wac):,}")
    print(f"  LODES columns: {len(wac.columns)}")
    geo_len = wac[LODES_BLOCK_KEY].str.len().value_counts().to_dict()
    print(f"  w_geocode length distribution: {geo_len}")

    missing = [s for s in sectors if s not in wac.columns]
    if missing:
        raise validate.ValidationError(
            f"config entropy_sectors not present in LODES schema: {missing}. "
            f"Available: {sorted(wac.columns.tolist())}"
        )
    print(f"  all {len(sectors)} configured entropy sectors present: OK")
    validate.report_df(wac, "LODES WAC raw", key_cols=[LODES_BLOCK_KEY, LODES_TOTAL_JOBS])

    # --- block internal points, attributes only (no polygon geometry) ----------
    blk_urls = []
    for st in sts:
        if st.get("tiger_dir"):
            blk_urls.append((st, conf["sources"]["block_url_tpl"].format(**st)))
        else:
            blk_urls.append((st, lod["block_geometry_url"]))
    print(f"\n=== block internal points (TIGER tabblock20 DBF, attributes only) ===")
    blk_parts = []
    for st, u in blk_urls:
        status, size = probe(u)
        print(f"  HEAD {u}\n    -> HTTP {status}, content-length {size}")
        z = download(u, paths.raw(city_key, "census") / pathlib.Path(u).name,
                     f"tabblock20 FIPS {st['fips']}")
        print(f"    on disk: {z.stat().st_size/1e6:,.1f} MB")
        # Address the .dbf sidecar inside the zip directly, so GDAL opens the table
        # rather than the shapefile: the .shp is never touched.
        stem = pathlib.Path(u).stem
        dbf_vsi = f"/vsizip/{z}/{stem}.dbf"
        info = pyogrio.read_info(dbf_vsi)
        fields = list(info["fields"])
        f_geoid = resolve_field(fields, TIGER_GEOID_PREFIX, "tabblock20 DBF")
        f_lat = resolve_field(fields, TIGER_LAT_PREFIX, "tabblock20 DBF")
        f_lon = resolve_field(fields, TIGER_LON_PREFIX, "tabblock20 DBF")
        f_uace = resolve_field(fields, TIGER_UACE_PREFIX, "tabblock20 DBF")
        a = pyogrio.read_dataframe(
            dbf_vsi, columns=[f_geoid, f_lat, f_lon, f_uace], read_geometry=False)
        print(f"    DBF features {info['features']:,} -> rows read {len(a):,} "
              f"(fields {f_geoid}, {f_lat}, {f_lon})")
        la = pd.to_numeric(a[f_lat], errors="coerce")
        lo = pd.to_numeric(a[f_lon], errors="coerce")
        bad = int(la.isna().sum() + lo.isna().sum())
        if bad:
            print(f"    !! {bad} unparseable INTPTLAT/INTPTLON — dropped")
            k = la.notna() & lo.notna()
            a, la, lo = a[k], la[k], lo[k]
        blk_parts.append(gpd.GeoDataFrame(
            {"block_geoid": a[f_geoid].astype("string"),
             "uace_tiger": a[f_uace].astype("string"),
             "state_fips": st["fips"]},
            geometry=shapely.points(np.c_[lo.to_numpy(), la.to_numpy()]),
            crs=conf["crs"]["geographic"]))
    blocks = pd.concat(blk_parts, ignore_index=True)
    blocks = gpd.GeoDataFrame(blocks, geometry="geometry",
                              crs=conf["crs"]["geographic"])
    f_uace = "UACE20"
    print(f"  block points pooled across {len(blk_parts)} state(s): {len(blocks):,}")
    validate.report_gdf(blocks, "block internal points (all states)", expect_crs="EPSG:4326")

    # --- spatial subset to the UA (D-005) -------------------------------------
    ua_fp = paths.raw(city_key, "census") / "urban_area.gpkg"
    if not ua_fp.exists():
        raise validate.ValidationError(
            f"{ua_fp.relative_to(paths.ROOT)} not found — run 01b_census_geography.py first."
        )
    ua = gpd.read_file(ua_fp).to_crs(conf["crs"]["geographic"])
    ua_geom = ua.union_all()
    uace = str(C["extent"]["uace20"])
    w, s, e, n = ua.total_bounds
    print(f"\n  UA bbox (w,s,e,n): {w:.5f}, {s:.5f}, {e:.5f}, {n:.5f}")

    bbox_hit = blocks.cx[w:e, s:n]
    print(f"  blocks in UA bbox    : {len(bbox_hit):,}")
    in_ua = bbox_hit[bbox_hit.geometry.within(ua_geom)].copy()
    print(f"  blocks inside UA poly: {len(in_ua):,}  (of {len(blocks):,} pooled)")
    if in_ua["state_fips"].nunique() > 1:
        print(f"    by state: {in_ua['state_fips'].value_counts().to_dict()}")

    # Attempted cross-check against TIGER's own UACE20 assignment on the block.
    # NOT available in the TIGER2020PL release: the 2020 urban-area delineation was
    # published after it, so UACE20/UR20/UATYPE20 are NULL for every block. Report
    # that rather than a misleading "0 matches".
    n_uace_populated = int(blocks["uace_tiger"].notna().sum())
    print(f"  cross-check on block-level {f_uace}: "
          f"{n_uace_populated:,}/{len(blocks):,} blocks have a non-null value")
    if n_uace_populated == 0:
        print(f"    -> {f_uace} is entirely NULL in this TIGER release; the "
              f"independent UA cross-check is UNAVAILABLE. Spatial "
              f"point-in-polygon against UACE20={uace} is the only assignment.")
    else:
        tiger_ua = int((in_ua["uace_tiger"] == uace).sum())
        print(f"    blocks with {f_uace} == {uace}, statewide          : "
              f"{int((blocks['uace_tiger'] == uace).sum()):,}")
        print(f"    of those, inside my spatial UA subset           : "
              f"{tiger_ua:,} ({tiger_ua/max(len(in_ua),1):.1%})")

    # --- join jobs ------------------------------------------------------------
    # Referential integrity first: every LODES w_geocode must be a real 2020 block.
    state_geoids = set(blocks["block_geoid"].dropna().tolist())
    unmatched = int((~wac[LODES_BLOCK_KEY].isin(state_geoids)).sum())
    print(f"\n  LODES w_geocode values not found in the 2020 block file: "
          f"{unmatched:,} of {len(wac):,}")
    if unmatched:
        bad = wac.loc[~wac[LODES_BLOCK_KEY].isin(state_geoids), LODES_BLOCK_KEY]
        print(f"    examples: {bad.head(5).tolist()}")
        print(f"    jobs stranded on unmatched geocodes: "
              f"{float(wac.loc[bad.index, LODES_TOTAL_JOBS].sum()):,.0f}")

    keep_cols = [LODES_BLOCK_KEY, LODES_TOTAL_JOBS] + sectors
    joined = in_ua.merge(
        wac[keep_cols], left_on="block_geoid", right_on=LODES_BLOCK_KEY,
        how="inner", validate="1:1",
    ).drop(columns=[LODES_BLOCK_KEY])
    print(f"\n  in-UA blocks with a LODES record: {len(joined):,}")
    print(f"  in-UA blocks with NO LODES record: {len(in_ua) - len(joined):,} "
          f"(LODES omits zero-job blocks)")
    lodes_outside = len(wac) - len(joined)
    print(f"  LODES records outside the UA     : {lodes_outside:,}")

    # --- entropy --------------------------------------------------------------
    ent, sector_total, k = normalised_entropy(joined[sectors].to_numpy())
    joined["job_entropy"] = ent
    joined["n_sectors"] = k

    c000 = joined[LODES_TOTAL_JOBS].to_numpy(dtype="float64")
    mismatch = int((np.abs(sector_total - c000) > 0.5).sum())
    print(f"\n  sum(CNS01..CNS20) != C000 on {mismatch:,} blocks "
          f"(expect 0 — sectors partition total jobs)")

    n_zero = int((c000 == 0).sum())
    n_k1 = int(((c000 > 0) & (k < 2)).sum())
    n_na = int(np.isnan(ent).sum())
    print(f"\n=== entropy (normalised Shannon over {len(sectors)} sectors) ===")
    print(f"  blocks total            : {len(joined):,}")
    print(f"  C000 == 0 (entropy NA)  : {n_zero:,}")
    print(f"  k < 2    (entropy NA)   : {n_k1:,}")
    print(f"  entropy NA total        : {n_na:,} ({n_na/len(joined):.1%})")
    valid = ent[~np.isnan(ent)]
    if len(valid):
        print(f"  entropy min/median/max  : {valid.min():.4f} / "
              f"{np.median(valid):.4f} / {valid.max():.4f}")
        print(f"  entropy mean            : {valid.mean():.4f}")
        for q in (0.10, 0.25, 0.75, 0.90):
            print(f"  entropy p{int(q*100):02d}              : {np.quantile(valid, q):.4f}")
    print(f"  k (sectors present) min/median/max: {k.min()} / "
          f"{int(np.median(k))} / {k.max()}")

    total_jobs = float(c000.sum())
    print(f"\n=== employment plausibility ===")
    print(f"  total jobs, in-UA blocks : {total_jobs:,.0f}")
    print(f"  total jobs, all Colorado : {float(wac[LODES_TOTAL_JOBS].sum()):,.0f}")
    print(f"  UA share of state jobs   : "
          f"{total_jobs/float(wac[LODES_TOTAL_JOBS].sum()):.1%}")
    print(f"  mean jobs per job-block  : {total_jobs/max(len(joined),1):,.1f}")
    print(f"  max jobs in one block    : {c000.max():,.0f}")

    validate.report_gdf(joined, "LODES blocks in UA", expect_crs="EPSG:4326")
    validate.check_coords_plausible(joined, "LODES blocks in UA", [w, s, e, n])
    validate.report_df(
        joined, "LODES block attributes",
        key_cols=["block_geoid", LODES_TOTAL_JOBS, "job_entropy", "n_sectors"],
    )

    out_fp = paths.processed(city_key) / "lodes_blocks.gpkg"
    # `uace_tiger` was carried only for the cross-check above; drop it rather than
    # ship an all-NULL column that a later stage might mistake for an assignment.
    joined.drop(columns=["uace_tiger"]).to_file(out_fp, layer="blocks", driver="GPKG")
    print(f"\n  wrote {out_fp.relative_to(paths.ROOT)} "
          f"({out_fp.stat().st_size:,} bytes)")

    provenance.log(
        city=city_key, layer=f"lodes{year}_wac_blocks", source_url=wac_url,
        rows=len(joined), file_path=out_fp,
    )
    return joined, wac_url, str(out_fp)


# --- Part B: OSM POIs ----------------------------------------------------------
def setup_osmnx(overpass_timeout: int) -> None:
    c = cfg.config()
    paths.CACHE.mkdir(parents=True, exist_ok=True)
    ox.settings.use_cache = bool(c["reproducibility"]["osmnx_use_cache"])
    ox.settings.cache_folder = str(paths.CACHE / "osmnx")
    ox.settings.log_console = False
    ox.settings.requests_timeout = overpass_timeout
    ox.settings.overpass_rate_limit = True


def tile_polygon(geom, n: int):
    """Split a polygon's bbox into an n x n grid and intersect with the polygon."""
    minx, miny, maxx, maxy = geom.bounds
    dx, dy = (maxx - minx) / n, (maxy - miny) / n
    out = []
    for i in range(n):
        for j in range(n):
            cell = shapely.box(minx + i * dx, miny + j * dy,
                               minx + (i + 1) * dx, miny + (j + 1) * dy)
            part = cell.intersection(geom)
            if not part.is_empty:
                out.append(part)
    return out


def fetch_pois(ua_geom, tags: dict, tiles: int) -> tuple[gpd.GeoDataFrame, int]:
    """features_from_polygon over the whole UA, falling back to tiling on error."""
    try:
        print(f"  attempting single Overpass query over the whole UA "
              f"(tags={ {k: v for k, v in tags.items()} })")
        g = ox.features_from_polygon(ua_geom, tags=tags)
        print(f"  single query OK: {len(g):,} features")
        return g, 1
    except Exception as e:  # noqa: BLE001 - report verbatim, then degrade
        print(f"  !! single-polygon query FAILED, verbatim error:")
        print(f"     {type(e).__name__}: {e}")
        print(f"  falling back to a {tiles}x{tiles} tiling of the UA bbox")

    parts = tile_polygon(ua_geom, tiles)
    print(f"  {len(parts)} non-empty tiles intersect the UA")
    frames = []
    for i, part in enumerate(parts, 1):
        try:
            gi = ox.features_from_polygon(part, tags=tags)
            frames.append(gi)
            print(f"    tile {i:>3}/{len(parts)}: {len(gi):,} features")
        except Exception as e:  # noqa: BLE001
            print(f"    tile {i:>3}/{len(parts)}: FAILED {type(e).__name__}: {e}")
    if not frames:
        raise validate.ValidationError("Every Overpass tile failed — see errors above.")
    g = pd.concat(frames)
    g = g[~g.index.duplicated(keep="first")]
    return gpd.GeoDataFrame(g, geometry="geometry", crs=frames[0].crs), len(parts)


def build_pois(city_key: str, C: dict, conf: dict, tiles: int) -> tuple[gpd.GeoDataFrame, str]:
    poi_cfg = cfg.land_use(city_key)["osm_poi"]
    tags = dict(poi_cfg["tags"])
    tag_keys = list(tags.keys())
    outdir = paths.raw(city_key, "osm_poi")
    out_fp = outdir / "pois.gpkg"

    print(f"\n=== B. OSM POIs ({poi_cfg['source']}) ===")

    if out_fp.exists() and out_fp.stat().st_size > 0:
        print(f"  [cached] {out_fp.relative_to(paths.ROOT)} "
              f"({out_fp.stat().st_size:,} bytes) — raw is write-once, reusing")
        pois = gpd.read_file(out_fp, layer="pois")
        n_tiles = 0
    else:
        ua = gpd.read_file(paths.raw(city_key, "census") / "urban_area.gpkg")
        ua = ua.to_crs(conf["crs"]["geographic"])
        ua_geom = ua.union_all()
        area_km2 = float(ua.to_crs(conf["crs"]["metric"]).geometry.area.sum() / 1e6)
        print(f"  UA area: {area_km2:,.0f} km²")

        raw, n_tiles = fetch_pois(ua_geom, tags, tiles)
        print(f"  raw features returned: {len(raw):,}")
        print(f"  raw geometry types   : "
              f"{raw.geometry.geom_type.value_counts().to_dict()}")

        raw = raw[raw.geometry.notna() & ~raw.geometry.is_empty].copy()
        print(f"  after dropping null/empty geometry: {len(raw):,}")

        # POINT representatives: centroid for anything that is not already a point.
        # Centroids are taken in the metric CRS (D-002), not in degrees.
        metric = conf["crs"]["metric"]
        geom = raw.geometry
        non_pt = geom.geom_type != "Point"
        print(f"  non-point features to centroid: {int(non_pt.sum()):,}")
        rep = geom.to_crs(metric).centroid.to_crs(conf["crs"]["geographic"])
        raw = raw.set_geometry(np.where(non_pt, rep, geom), crs=conf["crs"]["geographic"])

        cols = [c for c in tag_keys + [POI_NAME_FIELD] if c in raw.columns]
        absent = [c for c in tag_keys + [POI_NAME_FIELD] if c not in raw.columns]
        if absent:
            print(f"  !! configured tag keys absent from the Overpass result: {absent}")
        pois = raw.reset_index()[
            [c for c in ("element", "id") if c in raw.reset_index().columns]
            + cols + ["geometry"]
        ].copy()
        for c in cols:
            pois[c] = pois[c].astype("string")

        # Every kept feature must carry at least one of the configured tag keys.
        has_tag = pois[[c for c in cols if c in tag_keys]].notna().any(axis=1)
        print(f"  features carrying >=1 configured tag: {int(has_tag.sum()):,} "
              f"of {len(pois):,}")
        pois = pois[has_tag].copy()

        # Clip to the UA polygon: Overpass returns whole ways that merely touch
        # the bbox, and centroids can land outside.
        inside = pois.geometry.within(ua_geom)
        print(f"  POI points inside UA polygon: {int(inside.sum()):,} "
              f"(dropping {int((~inside).sum()):,})")
        pois = pois[inside].copy()

        pois.to_file(out_fp, layer="pois", driver="GPKG")
        print(f"  wrote {out_fp.relative_to(paths.ROOT)} "
              f"({out_fp.stat().st_size:,} bytes)")

    # --- category report ------------------------------------------------------
    present = [c for c in tag_keys if c in pois.columns]
    cat = pd.concat(
        [pois[c].dropna().map(lambda v, c=c: f"{c}={v}") for c in present]
    )
    print(f"\n=== POI categories ({len(cat):,} tag values on {len(pois):,} points) ===")
    for key in present:
        print(f"  {key:8s}: {int(pois[key].notna().sum()):,} points")
    print(f"\n  top 20 categories by count:")
    for i, (name, n) in enumerate(cat.value_counts().head(20).items(), 1):
        print(f"   {i:>3}. {name:38s} {n:>7,d}")
    print(f"\n  distinct categories: {cat.nunique():,}")

    validate.report_gdf(pois, "OSM POI points", expect_crs="EPSG:4326")
    ua_bounds = gpd.read_file(
        paths.raw(city_key, "census") / "urban_area.gpkg"
    ).total_bounds.tolist()
    validate.check_coords_plausible(pois, "OSM POI points", ua_bounds)
    validate.report_df(pois, "OSM POI attributes",
                       key_cols=present + [POI_NAME_FIELD])

    provenance.log(
        city=city_key, layer="osm_poi", source_url=OSM_SOURCE_URL,
        rows=len(pois), file_path=out_fp,
    )
    return pois, str(out_fp)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--city", default=None, help="city key in config/cities.yml")
    ap.add_argument("--overpass-timeout", type=int, default=600,
                    help="seconds to allow a single Overpass request")
    ap.add_argument("--poi-tiles", type=int, default=4,
                    help="n x n tiling of the UA bbox, used only if the single "
                         "whole-UA Overpass query fails")
    ap.add_argument("--skip-lodes", action="store_true")
    ap.add_argument("--skip-poi", action="store_true")
    args = ap.parse_args()

    conf = cfg.config()
    city_key = args.city or conf["project"]["pilot_city"]
    C = cfg.city(city_key)

    setup_osmnx(args.overpass_timeout)
    print(f"Environment: {provenance.environment_stamp()}")
    print(f"City: {city_key} ({C['label']})")
    print(f"Extent: UA {C['extent']['uace20']} (D-005) · metric CRS "
          f"{conf['crs']['metric']} (D-002)")

    parts = []
    if not args.skip_lodes:
        blocks = build_lodes(city_key, C, conf)[0]
        n_na = int(blocks["job_entropy"].isna().sum())
        parts.append(
            f"LODES {cfg.land_use(city_key)['lodes']['year']} WAC → {len(blocks):,} in-UA "
            f"blocks, {int(blocks[LODES_TOTAL_JOBS].sum()):,} jobs, job_entropy "
            f"NA on {n_na:,} single-sector blocks"
        )
    else:
        parts.append("LODES SKIPPED (--skip-lodes)")

    if not args.skip_poi:
        pois = build_pois(city_key, C, conf, args.poi_tiles)[0]
        parts.append(f"OSM POIs → {len(pois):,} points")
    else:
        parts.append("OSM POIs SKIPPED (--skip-poi)")

    provenance.log_progress("01e_landuse_mix", f"{city_key}: " + "; ".join(parts))
    print("\nStage 1e complete.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
