#!/usr/bin/env python
"""Stage 1c — acquire ACS tract attributes and build the density controls.

REQUIRES A CENSUS API KEY. Verified 2026-07-30: keyless requests to
api.census.gov 302-redirect to /data/missing_key.html. The script stops cleanly
at that boundary with instructions rather than failing deep in a request.

    Get a free key (instant, no approval):  https://api.census.gov/data/key_signup.html
    Then either:
        export CENSUS_API_KEY=xxxxxxxx
    or create a gitignored file at the project root called  .env  containing:
        CENSUS_API_KEY=xxxxxxxx

Variable names below were verified against the live keyless metadata endpoint
https://api.census.gov/data/2023/acs/acs5/variables.json on 2026-07-30.

Depends on: 01b_census_geography.py (needs data/raw/<city>/census/tracts.gpkg)

Usage
-----
    uv run python code/01_acquire/01c_acs_density.py --city denver

Outputs
-------
    data/processed/<city>/tract_density.gpkg   tracts + ACS + derived densities
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

KEY_SIGNUP = "https://api.census.gov/data/key_signup.html"


def fetch_acs(
    api_base: str, year: int, dataset: str, variables: list[str],
    state_fips: str, key: str,
) -> pd.DataFrame:
    """One request per state, all tracts. Returns a tidy DataFrame with GEOID."""
    url = f"{api_base}/{year}/{dataset}"
    params = {
        "get": ",".join(["NAME"] + variables),
        "for": "tract:*",
        "in": f"state:{state_fips}",
        "key": key,
    }
    r = requests.get(url, params=params, timeout=180)
    if r.status_code != 200 or not r.text.strip().startswith("["):
        raise RuntimeError(
            f"Census API returned status {r.status_code}.\n"
            f"  URL: {r.url.replace(key, 'REDACTED')}\n"
            f"  Body (first 300 chars): {r.text[:300]}"
        )
    rows = r.json()
    df = pd.DataFrame(rows[1:], columns=rows[0])
    df["GEOID"] = df["state"] + df["county"] + df["tract"]
    for v in variables:
        df[v] = pd.to_numeric(df[v], errors="coerce")
        # ACS uses large negative sentinels (e.g. -666666666) for suppressed values.
        df.loc[df[v] < -1e8, v] = pd.NA
    # B25035 (median year structure built) additionally returns 0 for tracts where
    # the median is not computable, INCLUDING tracts that do have housing units.
    # Verified on ACS 2020 5-year CO: 23 such tracts with housing_units > 0.
    # A year of 0 entering the D-006 vintage control would be catastrophic, so any
    # value below 1900 is treated as missing. ACS bottom-codes this variable at
    # "1939 or earlier" = 1939, so 1900 is a safe floor.
    if "B25035_001E" in df.columns:
        df.loc[df["B25035_001E"] < 1900, "B25035_001E"] = pd.NA
    return df


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--city", default=None)
    args = ap.parse_args()

    conf = cfg.config()
    city_key = args.city or conf["project"]["pilot_city"]
    C = cfg.city(city_key)
    cen = C["census"]

    print(f"Environment: {provenance.environment_stamp()}")
    print(f"City: {city_key} ({C['label']})")

    tracts_fp = paths.raw(city_key, "census") / "tracts.gpkg"
    if not tracts_fp.exists():
        print(f"\nERROR: {tracts_fp.relative_to(paths.ROOT)} not found.")
        print("Run 01b_census_geography.py first.")
        return 1

    key = cfg.census_api_key()
    if not key:
        print("\n" + "=" * 72)
        print("STOPPED AT CREDENTIAL BOUNDARY — no Census API key found.")
        print("=" * 72)
        print("\nWhat I need from you:")
        print(f"  1. Request a free key (instant, no approval): {KEY_SIGNUP}")
        print("  2. Then run ONE of:")
        print("       export CENSUS_API_KEY=<your-key>")
        print("     or create a file at the project root named  .env  containing:")
        print("       CENSUS_API_KEY=<your-key>")
        print("     (.env is already gitignored)")
        print("  3. Re-run this script. Nothing else changes.")
        print("\nEverything up to this point is done and verified:")
        print(f"  - tract geometry: {tracts_fp.relative_to(paths.ROOT)} (keyless, present)")
        print(f"  - variables verified against live metadata: "
              f"{', '.join(cen['variables'].keys())}")
        print("\nThe exact request this script will issue:")
        print(f"  GET {cen['api_base']}/{cen['acs_year']}/{cen['acs_dataset']}")
        print(f"      get=NAME,{','.join(cen['variables'].keys())}")
        print(f"      for=tract:*  in=state:"
              f"{[s['fips'] for s in cfg.states(city_key)]}")
        return 2

    print("  Census API key: found")

    variables = list(cen["variables"].keys())
    rename = dict(cen["variables"])

    print(f"\n=== ACS {cen['acs_year']} 5-year, {cen['acs_dataset']} ===")
    print(f"  requesting {len(variables)} variables for all tracts in "
          f"{len(cfg.states(city_key))} state(s)")
    sts = cfg.states(city_key)
    parts = []
    for st in sts:
        a = fetch_acs(cen["api_base"], int(cen["acs_year"]), cen["acs_dataset"],
                      variables, st["fips"], key)
        print(f"    FIPS {st['fips']}: {len(a):,} tract records")
        parts.append(a)
    acs = pd.concat(parts, ignore_index=True)
    print(f"  received {len(acs):,} tract records across {len(sts)} state(s)")
    acs = acs.rename(columns=rename)
    validate.report_df(acs, "ACS raw", key_cols=["GEOID"] + list(rename.values()))

    # --- join to geometry and derive densities ------------------------------
    tracts = gpd.read_file(tracts_fp)
    print(f"\n  tracts (from 01b): {len(tracts):,}")

    merged = tracts.merge(
        acs[["GEOID"] + list(rename.values())], on="GEOID", how="left", validate="1:1"
    )
    n_unmatched = int(merged["total_population"].isna().sum())
    print(f"  tracts with no ACS match: {n_unmatched}")
    if n_unmatched:
        print("  !! investigate before proceeding — GEOID vintage mismatch is the "
              "usual cause (TIGER 2023 vs ACS 2023 should align)")

    # Densities use ALAND (land area), not total area — water would deflate density.
    merged["aland_km2"] = merged["ALAND"].astype(float) / 1e6
    ok = merged["aland_km2"] > 0
    merged.loc[ok, "pop_density_km2"] = (
        merged.loc[ok, "total_population"] / merged.loc[ok, "aland_km2"]
    )
    merged.loc[ok, "housing_density_km2"] = (
        merged.loc[ok, "housing_units"] / merged.loc[ok, "aland_km2"]
    )
    merged["pct_no_vehicle"] = (
        merged["households_no_vehicle"] / merged["households_total"] * 100
    )

    # --- quality flags ------------------------------------------------------
    # Census reserves tract codes 9800-9999 for special land uses: airports, large
    # parks, water, institutional grounds. In the Denver UA these include DIA
    # (103 km²) and several open-space tracts. They have no residential population
    # or housing, so their density values are structurally zero rather than measured.
    # They are NOT dropped here: arterials genuinely run through them (airport access
    # roads), so the decision belongs to Stage 3/4. They are flagged instead.
    tract_code = merged["GEOID"].str[5:].astype(int)
    merged["is_special_use_tract"] = tract_code >= 980000
    merged["acs_reliable"] = (
        (merged["total_population"] > 0)
        & (merged["housing_units"] > 0)
        & merged["median_year_structure_built"].notna()
    )

    print("\n=== quality flags ===")
    print(f"  special-use tracts (98xx)     : {int(merged['is_special_use_tract'].sum())}")
    print(f"  zero housing units            : {int((merged['housing_units'] == 0).sum())}")
    print(f"  median_year_built missing     : "
          f"{int(merged['median_year_structure_built'].isna().sum())}")
    print(f"  acs_reliable = True           : {int(merged['acs_reliable'].sum())} "
          f"of {len(merged)}")
    valid_year = merged.loc[merged["median_year_structure_built"].notna(),
                            "median_year_structure_built"]
    if len(valid_year):
        print(f"\n  vintage control (D-006) spread: {valid_year.min():.0f}–"
              f"{valid_year.max():.0f}, median {valid_year.median():.0f}, "
              f"IQR {valid_year.quantile(.25):.0f}–{valid_year.quantile(.75):.0f}")

    validate.report_gdf(merged, "Tracts + ACS", expect_crs="EPSG:4326")
    validate.report_df(
        merged, "Derived density measures",
        key_cols=[
            "pop_density_km2", "housing_density_km2",
            "median_year_structure_built", "pct_no_vehicle",
        ],
    )

    out_fp = paths.processed(city_key) / "tract_density.gpkg"
    merged.to_file(out_fp, layer="tracts", driver="GPKG")
    print(f"\n  wrote {out_fp.relative_to(paths.ROOT)}")

    provenance.log(
        city=city_key,
        layer=f"acs{cen['acs_year']}_tract_density",
        source_url=f"{cen['api_base']}/{cen['acs_year']}/{cen['acs_dataset']}",
        rows=len(merged),
        file_path=out_fp,
    )
    provenance.log_progress(
        "01c_acs_density",
        f"{city_key}: {len(merged):,} tracts with ACS {cen['acs_year']} density controls",
    )
    print("\nStage 1c complete.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
