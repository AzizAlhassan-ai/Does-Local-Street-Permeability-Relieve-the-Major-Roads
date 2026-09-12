#!/usr/bin/env python
"""Stage 1d — acquire the DEPENDENT VARIABLE: major-road AADT from HPMS 2018.

Keyless. The FHWA HPMS Public Release is served as an open ArcGIS FeatureServer,
verified 2026-07-30. DECISION D-007 in PLAN.md: HPMS, not CDOT, is the outcome
source, because HPMS covers the full Federal-aid system (functional class 1-5)
and therefore includes *city-maintained* arterials and collectors. CDOT covers
state highways only, and Denver publishes no AADT layer at all.

Two hard constraints shape the acquisition:

  1. The layer's `maxRecordCount` is 2000 and the Denver UA bounding box holds
     ~17.5k records, so the query MUST be paged with resultOffset /
     resultRecordCount until `exceededTransferLimit` goes false. A single
     unpaged query silently returns the first 2000 features and looks fine —
     this is the main silent-failure mode of ArcGIS acquisition.
  2. Server-side spatial filtering is by ENVELOPE only, so the bbox pull is
     followed by a precise client-side restriction to the UA polygon.

Segment membership in the UA is decided by `intersects` on the *whole* segment
rather than by geometrically truncating the linework. HPMS carries linear
referencing (`route_id` + `begin_point`/`end_point`); cutting a segment at the
UA boundary would leave those fields describing an extent the geometry no
longer has. Instead every retained segment keeps its full geometry, and the
share of its length that actually falls inside the UA is recorded in
`length_in_ua_m` / `frac_in_ua`, with `fully_within_ua` as a flag. Both the
full and inside-UA centreline totals are reported.

Sources
-------
  HPMS 2018 PR, Colorado :
    https://geo.dot.gov/server/rest/services/Hosted/Colorado_2018_PR/FeatureServer/0

Depends on: 01b_census_geography.py (needs data/raw/<city>/census/urban_area.gpkg)

Usage
-----
    uv run python code/01_acquire/01d_hpms_aadt.py --city denver

Outputs (GeoPackage, EPSG:4326, layer `segments`)
-------
    data/raw/<city>/hpms/hpms2018_bbox_raw.gpkg       download cache, bbox extent
    data/raw/<city>/hpms/hpms2018_ua_all.gpkg         inside UA, ALL f_system
    data/raw/<city>/hpms/hpms2018_ua_analysis.gpkg    D-003 subset + derived outcome
"""

from __future__ import annotations

import argparse
import pathlib
import sys
import time

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

import geopandas as gpd
import numpy as np
import pandas as pd
import requests
from shapely.geometry import shape

from lib import cfg, paths, provenance, validate

# --- HPMS codebook constants -------------------------------------------------
# These are not analysis parameters — they are the published FHWA HPMS Field
# Manual code lists, fixed for every state and every year of the public release.
# They exist only to make the validation report readable.
F_SYSTEM_LABEL = {
    1: "Interstate",
    2: "Prin.Art - Other Fwy/Expwy",
    3: "Prin.Art - Other",
    4: "Minor Arterial",
    5: "Major Collector",
    6: "Minor Collector",
    7: "Local",
}
OWNERSHIP_LABEL = {
    1: "State Highway Agency",
    2: "County Highway Agency",
    3: "Town/Township Hwy Agency",
    4: "City/Municipal Hwy Agency",
    11: "State Park/Forest Agency",
    12: "Local Park/Forest Agency",
    21: "Other State Agency",
    25: "Other Local Agency",
    26: "Private (non-railroad)",
    27: "Railroad",
    31: "State Toll Authority",
    32: "Local Toll Authority",
    40: "Other Public Instrumentality",
    50: "Indian Tribe Nation",
    60: "Other Federal Agency",
    62: "Bureau of Indian Affairs",
    64: "US Forest Service",
    66: "National Park Service",
    70: "Corps of Engineers",
    80: "Other",
}
# Ownership codes that mean "not the state DOT". D-007 hinges on these being
# well represented: if HPMS in the Denver UA were effectively state-only, the
# study's outcome would not cover city arterials at all.
NON_STATE_OWNERSHIP = (2, 3, 4, 12, 25, 26, 31, 32, 40)
FACILITY_TYPE_LABEL = {
    1: "One-Way Roadway",
    2: "Two-Way Roadway",
    4: "Ramp",
    5: "Non-Mainline",
    6: "Non-Inventory Direction",
    7: "Planned/Unbuilt",
}

# Fallback field list, used only if cities.yml does not (yet) declare
# aadt.primary.retain_fields. See the config recommendation in the Stage 1d
# report: this belongs in config, and is read from there the moment it exists.
RETAIN_FIELDS_FALLBACK = [
    "objectid", "route_id", "begin_point", "end_point",
    "aadt", "aadt_combination", "aadt_single_unit",
    "f_system", "facility_type", "ownership", "nhs",
    "through_lanes", "speed_limit", "urban_code", "county_code",
    "route_number", "route_name", "route_signing",
]
# Every retained field that is numeric in the HPMS schema. Anything not listed
# stays a string (route_id, route_name).
TEXT_FIELDS = {"route_id", "route_name"}

# Plausible posted-speed window, mph. HPMS 2018 CO carries speed_limit = 999 on
# some records, which is a not-reported sentinel rather than a speed; treating it
# as a number would put a 999 mph arterial into H2's moderator. Anything outside
# this window is counted as unusable alongside null and zero.
SPEED_MIN_MPH, SPEED_MAX_MPH = 5, 90


def speed_usable(s: pd.Series) -> pd.Series:
    """Boolean mask of speed_limit values that can enter the H2 moderator."""
    v = pd.to_numeric(s, errors="coerce")
    return v.notna() & (v >= SPEED_MIN_MPH) & (v <= SPEED_MAX_MPH)


def get_json(url: str, params: dict, *, tries: int = 4, timeout: int = 180) -> dict:
    """GET returning parsed JSON, with a short backoff on transient failure.

    Raises with the verbatim server response on a non-JSON or error payload —
    never returns a partial or invented result.
    """
    last = None
    for attempt in range(1, tries + 1):
        try:
            r = requests.get(url, params=params, timeout=timeout)
            if r.status_code != 200:
                raise RuntimeError(
                    f"HTTP {r.status_code} from {r.url}\n"
                    f"  body (first 500 chars): {r.text[:500]}"
                )
            payload = r.json()
            if isinstance(payload, dict) and "error" in payload:
                raise RuntimeError(f"ArcGIS error from {r.url}\n  {payload['error']}")
            return payload
        except Exception as exc:  # noqa: BLE001 — re-raised below if terminal
            last = exc
            if attempt == tries:
                break
            wait = 2 ** attempt
            print(f"    attempt {attempt}/{tries} failed ({exc.__class__.__name__}); "
                  f"retrying in {wait}s")
            time.sleep(wait)
    raise RuntimeError(f"Request failed after {tries} attempts: {last}")


def layer_metadata(service: str) -> dict:
    return get_json(service, {"f": "json"})


def server_count(service: str, envelope: str) -> int:
    payload = get_json(f"{service}/query", {
        "where": "1=1",
        "geometry": envelope,
        "geometryType": "esriGeometryEnvelope",
        "inSR": "4326",
        "spatialRel": "esriSpatialRelIntersects",
        "returnCountOnly": "true",
        "f": "json",
    })
    if "count" not in payload:
        raise RuntimeError(f"returnCountOnly gave no count: {payload}")
    return int(payload["count"])


def query_paged(
    service: str, envelope: str, out_fields: list[str], page_size: int,
    expected: int,
) -> tuple[list[dict], list[object]]:
    """Page an ArcGIS query to exhaustion. Returns (properties, geometries).

    Stops only when the server reports `exceededTransferLimit` false or returns
    an empty page. The record count is checked against the server's own count
    by the caller — a short pull must never pass silently.
    """
    props: list[dict] = []
    geoms: list[object] = []
    offset = 0
    page = 0
    max_pages = int(expected / max(page_size, 1)) + 25  # generous, but bounded
    while True:
        page += 1
        if page > max_pages:
            raise RuntimeError(
                f"Paging exceeded {max_pages} pages at offset {offset} — "
                "aborting rather than looping forever."
            )
        payload = get_json(f"{service}/query", {
            "where": "1=1",
            "geometry": envelope,
            "geometryType": "esriGeometryEnvelope",
            "inSR": "4326",
            "spatialRel": "esriSpatialRelIntersects",
            "outFields": ",".join(out_fields),
            "returnGeometry": "true",
            "outSR": "4326",
            "orderByFields": "objectid ASC",
            "resultOffset": str(offset),
            "resultRecordCount": str(page_size),
            "f": "geojson",
        })
        feats = payload.get("features") or []
        for ft in feats:
            g = ft.get("geometry")
            props.append(ft.get("properties") or {})
            geoms.append(shape(g) if g else None)
        exceeded = bool((payload.get("properties") or {}).get("exceededTransferLimit"))
        print(f"    page {page:>3}: offset={offset:>6,}  got={len(feats):>5,}  "
              f"total={len(props):>6,}  exceededTransferLimit={exceeded}")
        if not feats or not exceeded:
            break
        offset += len(feats)
    return props, geoms


def to_gdf(props: list[dict], geoms: list[object], fields: list[str]) -> gpd.GeoDataFrame:
    df = pd.DataFrame(props)
    for f in fields:
        if f not in df.columns:
            df[f] = pd.NA
        elif f not in TEXT_FIELDS:
            df[f] = pd.to_numeric(df[f], errors="coerce")
    gdf = gpd.GeoDataFrame(df[fields].copy(), geometry=geoms, crs="EPSG:4326")
    return gdf


def f_system_breakdown(gdf: gpd.GeoDataFrame, km_by_fs: pd.Series) -> pd.DataFrame:
    """The table that decides whether H2's speed moderator is viable at all."""
    rows = []
    for fs, g in gdf.groupby("f_system", dropna=False):
        aadt = g["aadt"].dropna()
        lanes = g["through_lanes"].dropna()
        spd = g["speed_limit"]
        key = int(fs) if pd.notna(fs) else None
        rows.append({
            "f_system": key if key is not None else -1,
            "label": F_SYSTEM_LABEL.get(key, "UNKNOWN/NULL"),
            "n": len(g),
            "n_aadt_gt0": int((g["aadt"] > 0).sum()),
            "aadt_min": aadt.min() if len(aadt) else np.nan,
            "aadt_med": aadt.median() if len(aadt) else np.nan,
            "aadt_max": aadt.max() if len(aadt) else np.nan,
            "lanes_min": lanes.min() if len(lanes) else np.nan,
            "lanes_med": lanes.median() if len(lanes) else np.nan,
            "lanes_max": lanes.max() if len(lanes) else np.nan,
            "spd_null": int(spd.isna().sum()),
            "spd_zero": int((spd == 0).sum()),
            "spd_sentinel": int((spd > SPEED_MAX_MPH).sum()),
            "spd_unusable": int((~speed_usable(spd)).sum()),
            "spd_unusable_pct": float((~speed_usable(spd)).mean() * 100),
            "km_full": float(km_by_fs.get(fs, np.nan)),
        })
    out = pd.DataFrame(rows).sort_values("f_system").reset_index(drop=True)
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--city", default=None)
    args = ap.parse_args()

    conf = cfg.config()
    city_key = args.city or conf["project"]["pilot_city"]
    C = cfg.city(city_key)
    # Cities added in Stage 5 declare only `states`; the HPMS service is built from
    # the template in config.yml sources. Denver keeps its richer legacy block.
    prim = (C.get("aadt") or {}).get("primary") or {
        "name": f"FHWA HPMS Public Release 2018 — {C['label']}",
        "vintage": 2018,
        "key_fields": [],
    }
    dv = conf["dependent_variable"]
    metric = conf["crs"]["metric"]
    geographic = conf["crs"]["geographic"]
    outdir = paths.raw(city_key, "hpms")

    print(f"Environment: {provenance.environment_stamp()}")
    print(f"City: {city_key} ({C['label']})")
    print(f"Outcome source: {prim['name']} (vintage {prim['vintage']})")

    # --- 1. UA polygon from 01b ---------------------------------------------
    ua_fp = paths.raw(city_key, "census") / "urban_area.gpkg"
    if not ua_fp.exists() or ua_fp.stat().st_size == 0:
        print(f"\nERROR: {ua_fp.relative_to(paths.ROOT)} not found or empty.")
        print("Run 01b_census_geography.py first.")
        return 1

    ua = gpd.read_file(ua_fp).to_crs(geographic)
    if len(ua) != 1:
        raise validate.ValidationError(f"Expected 1 UA polygon, found {len(ua)}.")
    ua_geom = ua.geometry.iloc[0]
    minx, miny, maxx, maxy = ua.total_bounds
    envelope = f"{minx},{miny},{maxx},{maxy}"
    print(f"\n=== Study extent (D-005) ===")
    print(f"  {ua.iloc[0]['NAMELSAD20']}  (UACE20 {ua.iloc[0]['UACE20']})")
    print(f"  UA bbox (w,s,e,n): {minx:.6f}, {miny:.6f}, {maxx:.6f}, {maxy:.6f}")

    # --- 2. Layer schema check ---------------------------------------------
    services = cfg.hpms_services(city_key)
    service = services[0][1]
    print(f"\n=== HPMS layer schema ===")
    print(f"  {service}")
    meta = layer_metadata(service)
    schema = {f["name"] for f in meta["fields"]}
    page_size = int(meta.get("maxRecordCount") or 1000)
    print(f"  layer name       : {meta.get('name')}")
    print(f"  geometry type    : {meta.get('geometryType')}")
    print(f"  fields in layer  : {len(schema)}")
    print(f"  maxRecordCount   : {page_size}  -> paging is mandatory")
    print(f"  pagination       : "
          f"{meta.get('advancedQueryCapabilities', {}).get('supportsPagination')}")
    print(f"  query formats    : {meta.get('supportedQueryFormats')}")

    # Field list resolution, most-global first. The HPMS Public Release schema is
    # identical across all 50 states, so config.yml (global) is the correct home;
    # cities.yml allows a per-city override; the module constant is a last resort.
    global_retain = conf.get("dependent_variable", {}).get("hpms_retain_fields")
    if global_retain:
        retain = list(global_retain)
        print("  retained-field list source: config.yml "
              "dependent_variable.hpms_retain_fields (global)")
    elif prim.get("retain_fields"):
        retain = list(prim["retain_fields"])
        print("  retained-field list source: cities.yml aadt.primary.retain_fields")
    else:
        retain = list(RETAIN_FIELDS_FALLBACK)
        print("  note: no retain_fields in config; using the in-script fallback list.")
    missing = [f for f in retain if f not in schema]
    present = [f for f in retain if f in schema]
    print(f"  retained fields requested: {len(retain)}")
    print(f"  present in layer         : {len(present)}")
    if missing:
        print(f"  !! ABSENT from layer     : {missing}")
        raise validate.ValidationError(
            f"Fields absent from the HPMS layer schema: {missing}. "
            "The retain list must be corrected in config before proceeding."
        )
    print("  all requested fields confirmed present in the live schema: OK")

    # cities.yml declares a shorter key_fields list; it must be a subset.
    declared = [f for f in prim.get("key_fields", [])]
    not_covered = [f for f in declared if f not in retain]
    if not_covered:
        print(f"  !! cities.yml key_fields not covered by retain list: {not_covered}")

    # --- 3. Paged bbox pull (write-once cache) ------------------------------
    raw_fp = outdir / "hpms2018_bbox_raw.gpkg"
    print(f"\n=== Server-side bbox query, paged ===")
    n_server = sum(server_count(svc, envelope) for _, svc in services)
    print(f"  states queried: {[f for f, _ in services]}")
    print(f"  server-reported count in UA bbox : {n_server:,}")
    cfg_expect = prim.get("records_denver_bbox_ua") if city_key == "denver" else None
    if cfg_expect is not None:
        print(f"  cities.yml records_denver_bbox   : {int(cfg_expect):,}  "
              f"(informational; a different bbox was used when it was recorded)")

    if raw_fp.exists() and raw_fp.stat().st_size > 0:
        print(f"  [cached] {raw_fp.name} ({raw_fp.stat().st_size:,} bytes) — "
              "raw is write-once, skipping download")
        bbox_gdf = gpd.read_file(raw_fp, layer="segments").to_crs(geographic)
        n_paged = len(bbox_gdf)
        print(f"  loaded {n_paged:,} cached records")
    else:
        all_props, all_geoms = [], []
        for st_fips, svc in services:
            n_st = server_count(svc, envelope)
            print(f"  --- state FIPS {st_fips}: {n_st:,} records in bbox ---")
            if n_st == 0:
                continue
            pr, gm = query_paged(svc, envelope, retain, page_size, n_st)
            for row in pr:
                row["state_fips"] = st_fips
            all_props.extend(pr); all_geoms.extend(gm)
        props, geoms = all_props, all_geoms
        n_paged = len(props)
        # state_fips is added per row in the loop above and is NOT in `retain`;
        # it must be passed explicitly or to_gdf drops it and the composite
        # hpms_uid silently degrades to a bare objectid (multi-state collisions).
        bbox_gdf = to_gdf(props, geoms, retain + ["state_fips"])
        print(f"  wrote nothing yet; building GeoDataFrame of {n_paged:,} records")

    # HPMS objectid and route_id are unique WITHIN a state layer, not across
    # states. Multi-state UAs (Portland OR-WA, Boston MA-NH) therefore collide on
    # both. Prefix each with the state FIPS before any uniqueness check or the
    # D-028 dissolve, which groups by route_id.
    if "state_fips" in bbox_gdf.columns:
        upref = bbox_gdf["state_fips"].astype(str) + "_"
        uid = bbox_gdf["objectid"].astype(str)
        bbox_gdf["hpms_uid"] = uid.where(uid.str.contains("_"), upref + uid)
        # Idempotent: a cached re-run must not prefix an already-prefixed id.
        # (str.startswith needs a SCALAR, so test for the "NN:" shape by regex.)
        pref = bbox_gdf["state_fips"].astype(str) + ":"
        rid = bbox_gdf["route_id"].astype(str)
        already = rid.str.contains(r"^\d{2}:", regex=True, na=False)
        bbox_gdf["route_id"] = rid.where(already, pref + rid)
        n_st = bbox_gdf["state_fips"].nunique()
        if n_st > 1:
            print(f"  multi-state UA: {n_st} states -> objectid/route_id "
                  f"prefixed with state FIPS to keep them unique")
    else:
        bbox_gdf["hpms_uid"] = bbox_gdf["objectid"].astype(str)

    print(f"\n  records paged           : {n_paged:,}")
    print(f"  server-reported count   : {n_server:,}")
    if n_paged != n_server:
        raise validate.ValidationError(
            f"Paging is incomplete: retrieved {n_paged:,} of {n_server:,} records "
            "reported by the server. Refusing to continue on a truncated pull."
        )
    print("  paged == server count   : OK (no silent transfer-limit truncation)")

    n_dup = int(bbox_gdf["hpms_uid"].duplicated().sum())
    print(f"  duplicate hpms_uid rows : {n_dup}")
    if n_dup:
        raise validate.ValidationError(
            f"{n_dup} duplicate objectid values — paging overlapped."
        )

    if not (raw_fp.exists() and raw_fp.stat().st_size > 0):
        bbox_gdf.to_file(raw_fp, layer="segments", driver="GPKG")
        print(f"  wrote {raw_fp.relative_to(paths.ROOT)} "
              f"({raw_fp.stat().st_size:,} bytes)")

    validate.report_gdf(bbox_gdf, "HPMS 2018 — UA bounding box", expect_crs=geographic)

    # NOTE: validate.check_coords_plausible is deliberately NOT used here. It
    # hard-fails when geometry leaves the expected bbox, which is correct for
    # points and polygons but wrong for this layer: esriSpatialRelIntersects
    # returns *whole* features that touch the envelope, and some HPMS route
    # segments are tens of kilometres long, so they legitimately extend far
    # outside it. Reported as a diagnostic instead, because the alternative
    # failure (a query that quietly returned the whole state) has to stay
    # detectable.
    bminx, bminy, bmaxx, bmaxy = bbox_gdf.total_bounds
    seg_bounds = bbox_gdf.bounds
    n_outside = int((
        (seg_bounds["minx"] < minx) | (seg_bounds["maxx"] > maxx)
        | (seg_bounds["miny"] < miny) | (seg_bounds["maxy"] > maxy)
    ).sum())
    print(f"  segments extending beyond the UA bbox: {n_outside:,} "
          f"(expected >0: envelope intersect returns whole features)")
    print(f"  layer extent vs UA bbox: x {bminx:.4f}..{bmaxx:.4f} "
          f"(bbox {minx:.4f}..{maxx:.4f}), y {bminy:.4f}..{bmaxy:.4f} "
          f"(bbox {miny:.4f}..{maxy:.4f})")
    # Sanity guard, generalised for Stage 5. `esriSpatialRelIntersects` returns whole
    # features, so a single long route can legitimately run hundreds of km beyond the
    # UA -- a Washington HPMS segment intersecting the Portland bbox reaches the
    # Canadian border at 49.0N. Testing the ABSOLUTE extent therefore produces false
    # alarms. The failure actually worth catching is a lost spatial filter, which
    # would return the whole state and put MOST features far away. So test the bulk:
    # at least 95% of segment centroids must sit inside the UA bbox plus a small pad.
    cent = bbox_gdf.geometry.representative_point()
    padx = max(0.25, (maxx - minx) * 0.5)
    pady = max(0.25, (maxy - miny) * 0.5)
    inside_pad = (
        (cent.x >= minx - padx) & (cent.x <= maxx + padx)
        & (cent.y >= miny - pady) & (cent.y <= maxy + pady)
    )
    frac_in = float(inside_pad.mean())
    print(f"  segment centroids inside UA bbox + pad ({padx:.2f}deg, {pady:.2f}deg): "
          f"{frac_in:.1%}")
    if frac_in < 0.95:
        raise validate.ValidationError(
            f"Only {frac_in:.1%} of HPMS segment centroids fall near the {city_key} "
            f"UA bbox ({minx:.4f}, {miny:.4f}, {maxx:.4f}, {maxy:.4f}). A lost "
            "spatial filter or wrong axis order would look exactly like this."
        )
    print("  bulk extent check: OK")

    # --- 4. Precise restriction to the UA polygon --------------------------
    print(f"\n=== Client-side restriction to the UA polygon ===")
    inside = bbox_gdf[bbox_gdf.intersects(ua_geom)].copy()
    print(f"  in bbox              : {len(bbox_gdf):,}")
    print(f"  intersecting UA poly : {len(inside):,}  "
          f"(dropped {len(bbox_gdf) - len(inside):,} bbox-only records)")
    if len(inside) == 0:
        raise validate.ValidationError("No HPMS segments intersect the UA polygon.")

    # Length bookkeeping in the metric CRS (D-002). Two measures are kept: the
    # full segment length, and the portion actually inside the UA. The gap is
    # boundary spillover, and it must be visible rather than assumed away.
    m = inside.to_crs(metric)
    inside["length_m"] = m.geometry.length.to_numpy()
    ua_m = ua.to_crs(metric).geometry.iloc[0]
    clipped = m.geometry.intersection(ua_m)
    inside["length_in_ua_m"] = clipped.length.to_numpy()
    inside["frac_in_ua"] = np.where(
        inside["length_m"] > 0, inside["length_in_ua_m"] / inside["length_m"], np.nan
    )
    inside["fully_within_ua"] = inside["frac_in_ua"] >= 0.999
    n_partial = int((~inside["fully_within_ua"]).sum())
    print(f"  fully inside UA      : {int(inside['fully_within_ua'].sum()):,}")
    print(f"  straddling UA edge   : {n_partial:,}")
    print(f"  centreline km, full segments : {inside['length_m'].sum()/1000:,.1f}")
    print(f"  centreline km, inside UA only: {inside['length_in_ua_m'].sum()/1000:,.1f}")

    validate.report_gdf(inside, "HPMS 2018 — inside Denver UA", expect_crs=geographic)
    validate.report_df(
        inside, "HPMS attributes (inside UA)",
        key_cols=["objectid", "route_id", "aadt", "f_system", "through_lanes",
                  "speed_limit", "ownership", "nhs", "urban_code", "county_code",
                  "facility_type", "length_m"],
    )

    # --- 5. f_system breakdown — H2 viability ------------------------------
    km_full = (
        inside.groupby("f_system", dropna=False)["length_m"].sum() / 1000.0
    )
    km_in_ua = (
        inside.groupby("f_system", dropna=False)["length_in_ua_m"].sum() / 1000.0
    )
    fs_tab = f_system_breakdown(inside, km_full)
    fs_tab["km_in_ua"] = [float(km_in_ua.get(
        r if r != -1 else np.nan, np.nan)) for r in fs_tab["f_system"]]

    print("\n" + "=" * 100)
    print("F_SYSTEM BREAKDOWN — this determines whether H2's speed moderator is viable")
    print("=" * 100)
    with pd.option_context("display.width", 200, "display.max_columns", 50):
        print(fs_tab.to_string(index=False, float_format=lambda v: f"{v:,.1f}"))
    keep = [int(x) for x in dv["hpms_f_system_keep"]]
    print(f"\n  D-003 retained f_system: {keep}")
    sub = fs_tab[fs_tab["f_system"].isin(keep)]
    if len(sub):
        tot_n = int(sub["n"].sum())
        tot_missing = int(sub["spd_unusable"].sum())
        print(f"  segments in retained classes             : {tot_n:,}")
        print(f"  of those, speed_limit unusable           : {tot_missing:,} "
              f"({tot_missing / tot_n * 100:.1f}%)")
        print(f"    (null, zero, or outside {SPEED_MIN_MPH}-{SPEED_MAX_MPH} mph — "
              "HPMS CO 2018 uses 999 as a not-reported sentinel)")
        print("  ^^ H2's arterial-speed term is only estimable on the complement.")
        spd_keep = inside.loc[inside["f_system"].isin(keep), "speed_limit"]
        good = spd_keep[speed_usable(spd_keep)]
        if len(good):
            print(f"  usable speed_limit values: n={len(good):,}, "
                  f"range {good.min():.0f}-{good.max():.0f} mph, "
                  f"median {good.median():.0f}")

    # --- 6. ownership x f_system — does HPMS cover city arterials? ---------
    own = inside["ownership"]
    print("\n" + "=" * 100)
    print("OWNERSHIP x F_SYSTEM — tests D-007's core claim that HPMS captures")
    print("city-maintained arterials, not just state highways")
    print("=" * 100)
    print("\n  ownership distribution (all f_system, inside UA):")
    vc = own.value_counts(dropna=False).sort_index()
    for code, n in vc.items():
        key = int(code) if pd.notna(code) else None
        lab = OWNERSHIP_LABEL.get(key, "UNKNOWN/NULL")
        print(f"    {str(key):>5}  {lab:<30s} {n:>7,}  ({n/len(inside)*100:5.1f}%)")

    ct = pd.crosstab(
        inside["ownership"].fillna(-1), inside["f_system"].fillna(-1), dropna=False
    )
    ct.index = [
        "  -1 NULL/not reported" if int(i) == -1
        else f"{int(i):>4} {OWNERSHIP_LABEL.get(int(i), '?')}"
        for i in ct.index
    ]
    ct.columns = [("fsNA" if int(c) == -1 else f"fs{int(c)}") for c in ct.columns]
    ct["TOTAL"] = ct.sum(axis=1)
    print("\n  cross-tab (rows = ownership, cols = f_system):")
    with pd.option_context("display.width", 200, "display.max_columns", 50):
        print(ct.to_string())

    is_state = own == 1
    is_nonstate = own.isin(NON_STATE_OWNERSHIP)
    print(f"\n  state-agency owned      : {int(is_state.sum()):,} "
          f"({is_state.mean()*100:.1f}%)")
    print(f"  non-state (local) owned : {int(is_nonstate.sum()):,} "
          f"({is_nonstate.mean()*100:.1f}%)")
    keep_mask = inside["f_system"].isin(keep)
    if int(keep_mask.sum()):
        ns_keep = int((keep_mask & is_nonstate).sum())
        print(f"  within D-003 classes 3/4/5: {ns_keep:,} of {int(keep_mask.sum()):,} "
              f"({ns_keep / int(keep_mask.sum()) * 100:.1f}%) are locally owned")
        print("  ^^ if this share were near zero, D-007 would be falsified and the "
              "outcome would be state-highway-only.")

    # --- 6b. independent extent cross-check via urban_code ------------------
    # HPMS carries its own urban-area code per segment. It is an entirely
    # separate assertion from our TIGER polygon, so agreement is a real check on
    # D-005 rather than a tautology. 99999 = rural, 99998 = small urban.
    uace = str(ua.iloc[0]["UACE20"])
    print(f"\n  urban_code cross-check against UACE20 {uace} (independent of the "
          "TIGER polygon):")
    # D-051: a city may span several UACE codes (Wasatch Front = 3), in which case
    # `uace` is the joined label "a+b+c". Match against the component codes.
    uace_codes = {u.strip() for u in str(uace).split("+") if u.strip()}
    uc = inside["urban_code"].value_counts(dropna=False).sort_values(ascending=False)
    for code, n in uc.items():
        key = "NULL" if pd.isna(code) else str(int(code))
        tag = ("== study UA" if key in uace_codes else
               "rural" if key == "99999" else
               "small urban" if key == "99998" else "OTHER urban area")
        print(f"    {key:>7}  {n:>7,}  ({n/len(inside)*100:5.1f}%)  {tag}")
    ucs = inside["urban_code"].astype("Float64")
    n_match = int(ucs.isin([float(u) for u in uace_codes]).sum())
    print(f"    agreement with our polygon: {n_match:,}/{len(inside):,} "
          f"({n_match/len(inside)*100:.1f}%)")

    # --- 6c. facility_type — a real analytic hazard, reported not filtered ---
    print("\n  facility_type x f_system (rows = facility_type):")
    ft = pd.crosstab(
        inside["facility_type"].fillna(-1), inside["f_system"].fillna(-1)
    )
    ft.index = [
        "  -1 NULL" if int(i) == -1
        else f"{int(i):>4} {FACILITY_TYPE_LABEL.get(int(i), '?')}" for i in ft.index
    ]
    ft.columns = [("fsNA" if int(c) == -1 else f"fs{int(c)}") for c in ft.columns]
    ft["TOTAL"] = ft.sum(axis=1)
    with pd.option_context("display.width", 200, "display.max_columns", 50):
        print(ft.to_string())
    n_nid = int((inside["facility_type"] == 6).sum())
    n_ramp = int((inside["facility_type"] == 4).sum())
    n_oneway = int((inside["facility_type"] == 1).sum())
    print(f"\n    facility_type 6 (Non-Inventory Direction): {n_nid:,} — the "
          "uninventoried carriageway of a divided road.")
    print("      These carry geometry but NO aadt/through_lanes by design, so the "
          "D-004 aadt>=1 filter removes them.")
    print(f"    facility_type 4 (Ramp)     : {n_ramp:,} — geometrically arterial, "
          "conceptually not; a Stage 3 exclusion candidate.")
    print(f"    facility_type 1 (One-Way)  : {n_oneway:,} — AADT on a one-way "
          "roadway is DIRECTIONAL, not bidirectional.")
    print("      Mixing these with facility_type 2 puts two different quantities in "
          "one outcome column. Must be resolved in Stage 3.")

    print("\n  centreline km by f_system (EPSG:5070; full segment | inside UA):")
    for fs in sorted([f for f in km_full.index if pd.notna(f)]):
        print(f"    f_system {int(fs)} {F_SYSTEM_LABEL.get(int(fs), '?'):<28s} "
              f"{km_full[fs]:>10,.1f} km | {km_in_ua[fs]:>10,.1f} km")
    print(f"    {'TOTAL':<39s} {km_full.sum():>10,.1f} km | "
          f"{km_in_ua.sum():>10,.1f} km")

    # --- 7. write the all-classes layer ------------------------------------
    all_fp = outdir / "hpms2018_ua_all.gpkg"
    inside.to_file(all_fp, layer="segments", driver="GPKG")
    print(f"\n  wrote {all_fp.relative_to(paths.ROOT)} "
          f"({all_fp.stat().st_size:,} bytes)")

    # --- 8. analysis subset (D-003 / D-004) --------------------------------
    min_aadt = int(dv["min_aadt"])
    print(f"\n=== Analysis subset (D-003, D-004) ===")
    print(f"  filter: f_system in {keep} AND aadt >= {min_aadt}")
    step1 = inside[inside["f_system"].isin(keep)].copy()
    print(f"  after f_system filter : {len(step1):,}")
    n_aadt_null = int(step1["aadt"].isna().sum())
    n_aadt_low = int((step1["aadt"] < min_aadt).sum())
    print(f"  aadt null             : {n_aadt_null:,}")
    print(f"  aadt < {min_aadt}             : {n_aadt_low:,}")
    ana = step1[step1["aadt"].notna() & (step1["aadt"] >= min_aadt)].copy()
    print(f"  after aadt filter     : {len(ana):,}")
    if len(ana) == 0:
        raise validate.ValidationError("Analysis subset is empty — check D-003 config.")

    # Primary outcome (D-004).
    ana["log_aadt"] = np.log(ana["aadt"].astype(float))

    # Co-primary outcome (D-004). through_lanes <= 0 or null cannot yield a
    # per-lane rate; those rows get NA rather than an inf or a silent 1-lane
    # assumption.
    lanes = pd.to_numeric(ana["through_lanes"], errors="coerce").astype(float)
    usable = lanes.notna() & (lanes > 0)
    ana["aadt_per_lane"] = np.where(
        usable, ana["aadt"].astype(float) / lanes.where(usable), np.nan
    )
    n_lanes_null = int(lanes.isna().sum())
    n_lanes_zero = int((lanes.notna() & (lanes <= 0)).sum())
    n_unusable = int((~usable).sum())

    # H2 moderator availability, carried as a column so Stage 3/4 cannot forget it.
    ana["speed_limit_usable"] = speed_usable(ana["speed_limit"])
    spd = pd.to_numeric(ana["speed_limit"], errors="coerce")
    n_spd_null = int(spd.isna().sum())
    n_spd_zero = int((spd == 0).sum())
    n_spd_sentinel = int((spd > SPEED_MAX_MPH).sum())
    n_spd_unusable = int((~ana["speed_limit_usable"]).sum())

    print(f"\n  --- derived outcomes ---")
    print(f"  log_aadt computed for        : {int(ana['log_aadt'].notna().sum()):,}")
    print(f"  through_lanes null           : {n_lanes_null:,}")
    print(f"  through_lanes <= 0           : {n_lanes_zero:,}")
    print(f"  aadt_per_lane = NA           : {n_unusable:,} "
          f"({n_unusable/len(ana)*100:.2f}% of the analysis subset)  <- D-004 co-primary")
    print(f"  speed_limit null             : {n_spd_null:,}")
    print(f"  speed_limit == 0             : {n_spd_zero:,}")
    print(f"  speed_limit > {SPEED_MAX_MPH} (sentinel) : {n_spd_sentinel:,}")
    print(f"  speed_limit unusable (total) : {n_spd_unusable:,} "
          f"({n_spd_unusable/len(ana)*100:.2f}%)  <- H2 moderator availability")
    print(f"  speed_limit usable           : "
          f"{int(ana['speed_limit_usable'].sum()):,}")

    validate.report_gdf(ana, "HPMS 2018 — analysis subset", expect_crs=geographic)
    validate.report_df(
        ana, "Analysis subset outcomes",
        key_cols=["aadt", "log_aadt", "aadt_per_lane", "through_lanes",
                  "speed_limit", "f_system", "ownership", "nhs", "length_m"],
    )

    ana_km = ana.groupby("f_system", dropna=False)["length_m"].sum() / 1000.0
    print("\n  analysis subset, n and centreline km by f_system:")
    for fs in sorted([f for f in ana_km.index if pd.notna(f)]):
        n_fs = int((ana["f_system"] == fs).sum())
        print(f"    f_system {int(fs)} {F_SYSTEM_LABEL.get(int(fs), '?'):<28s} "
              f"n={n_fs:>6,}  {ana_km[fs]:>9,.1f} km")

    print("\n  analysis subset, facility_type composition:")
    for code, n in ana["facility_type"].value_counts(dropna=False).sort_index().items():
        key = None if pd.isna(code) else int(code)
        print(f"    {str(key):>5} {FACILITY_TYPE_LABEL.get(key, 'UNKNOWN/NULL'):<26s} "
              f"{n:>6,}  ({n/len(ana)*100:5.1f}%)")

    # HPMS segmentation granularity drives the effective N. If most segments are
    # one 0.1-mile increment of the same route, adjacent rows are near-replicates
    # and the multilevel model's effective sample size is far below its nominal
    # one. This is the number behind the "non-overlapping subsample" robustness
    # run in PLAN.md §4.
    ln = ana["length_m"]
    print(f"\n  segment length (m): min {ln.min():,.1f}  p25 {ln.quantile(.25):,.1f}  "
          f"median {ln.median():,.1f}  p75 {ln.quantile(.75):,.1f}  "
          f"p99 {ln.quantile(.99):,.1f}  max {ln.max():,.1f}")
    near_tenth_mile = int(((ln > 150) & (ln < 170)).sum())
    print(f"  segments of ~161 m (0.1 mile): {near_tenth_mile:,} "
          f"({near_tenth_mile/len(ana)*100:.1f}%) — HPMS reports in 0.1-mile "
          "increments")
    print(f"  distinct route_id           : {ana['route_id'].nunique():,} across "
          f"{len(ana):,} rows "
          f"({len(ana)/max(ana['route_id'].nunique(), 1):.1f} rows per route)")
    print("  ^^ nominal N is NOT effective N; adjacent rows on one route are "
          "near-replicates.")
    n_dupkey = int(ana.duplicated(["route_id", "begin_point"]).sum())
    print(f"  duplicate (route_id, begin_point): {n_dupkey:,} "
          "(0 expected — HPMS linear-reference key)")
    if n_dupkey:
        print("  !! the HPMS linear-referencing key is not unique; investigate "
              "before Stage 3 conflation")

    ana_fp = outdir / "hpms2018_ua_analysis.gpkg"
    ana.to_file(ana_fp, layer="segments", driver="GPKG")
    print(f"\n  wrote {ana_fp.relative_to(paths.ROOT)} "
          f"({ana_fp.stat().st_size:,} bytes)")

    # --- provenance ---------------------------------------------------------
    provenance.log(
        city=city_key, layer="hpms2018_ua_all", source_url=service,
        rows=len(inside), file_path=all_fp,
    )
    provenance.log(
        city=city_key, layer="hpms2018_ua_analysis", source_url=service,
        rows=len(ana), file_path=ana_fp,
    )
    provenance.log_progress(
        "01d_hpms_aadt",
        f"{city_key}: HPMS {prim['vintage']} AADT — {n_paged:,} paged in UA bbox, "
        f"{len(inside):,} inside UA, {len(ana):,} in the D-003 analysis subset "
        f"(f_system {keep}, aadt>={min_aadt}); "
        f"{n_unusable:,} lack usable through_lanes, {n_spd_unusable:,} lack speed_limit",
    )
    print("\nStage 1d complete.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
