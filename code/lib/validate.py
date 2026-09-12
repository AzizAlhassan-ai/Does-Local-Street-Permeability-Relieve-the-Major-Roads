"""Layer validation and reporting.

Prints the checks that must be seen before any layer is treated as done:
row count, CRS, coordinate ranges, null counts, geometry validity.
"""

from __future__ import annotations

import geopandas as gpd
import pandas as pd


class ValidationError(AssertionError):
    pass


def report_gdf(gdf: gpd.GeoDataFrame, name: str, expect_crs: str | None = None) -> dict:
    """Print a standard report for a GeoDataFrame and return it as a dict."""
    n = len(gdf)
    print(f"\n--- {name} ---")
    print(f"  rows          : {n:,}")
    print(f"  CRS           : {gdf.crs}")

    if n == 0:
        print("  !! EMPTY LAYER")
        return {"name": name, "rows": 0}

    geom_types = gdf.geometry.geom_type.value_counts().to_dict()
    print(f"  geometry types: {geom_types}")

    minx, miny, maxx, maxy = gdf.total_bounds
    print(f"  bounds x      : {minx:.6f} .. {maxx:.6f}")
    print(f"  bounds y      : {miny:.6f} .. {maxy:.6f}")

    n_invalid = int((~gdf.geometry.is_valid).sum())
    n_empty = int(gdf.geometry.is_empty.sum())
    n_null = int(gdf.geometry.isna().sum())
    print(f"  invalid geom  : {n_invalid}")
    print(f"  empty geom    : {n_empty}")
    print(f"  null geom     : {n_null}")

    if expect_crs is not None and gdf.crs is not None:
        actual = gdf.crs.to_string()
        ok = actual.upper().endswith(expect_crs.split(":")[-1])
        print(f"  CRS as expected ({expect_crs}): {ok}")

    return {
        "name": name,
        "rows": n,
        "crs": str(gdf.crs),
        "bounds": (minx, miny, maxx, maxy),
        "invalid_geom": n_invalid,
        "geom_types": geom_types,
    }


def report_df(df: pd.DataFrame, name: str, key_cols: list[str] | None = None) -> dict:
    n = len(df)
    print(f"\n--- {name} ---")
    print(f"  rows    : {n:,}")
    print(f"  columns : {len(df.columns)}")
    if n == 0:
        print("  !! EMPTY TABLE")
        return {"name": name, "rows": 0}
    for c in key_cols or []:
        if c not in df.columns:
            print(f"  !! missing expected column: {c}")
            continue
        s = df[c]
        nn = int(s.isna().sum())
        if pd.api.types.is_numeric_dtype(s):
            valid = s.dropna()
            rng = f"{valid.min():,.2f} .. {valid.max():,.2f}" if len(valid) else "n/a"
            print(f"  {c:32s} nulls={nn:6d}  range={rng}")
        else:
            print(f"  {c:32s} nulls={nn:6d}  n_unique={s.nunique()}")
    return {"name": name, "rows": n}


def check_coords_plausible(gdf: gpd.GeoDataFrame, name: str, bbox_wsen: list[float]) -> None:
    """Hard-fail if geometry falls outside an expected WGS84 bbox (with slack).

    Catches the classic silent errors: axis-swapped coordinates, wrong CRS
    assumed on read, or a query that returned the whole state.
    """
    if gdf.crs is None:
        raise ValidationError(f"{name}: CRS is None — cannot validate coordinates.")
    g = gdf.to_crs("EPSG:4326") if gdf.crs.to_epsg() != 4326 else gdf
    w, s, e, n = bbox_wsen
    pad = 0.05
    minx, miny, maxx, maxy = g.total_bounds
    if not (w - pad <= minx and maxx <= e + pad and s - pad <= miny and maxy <= n + pad):
        raise ValidationError(
            f"{name}: geometry outside expected bbox.\n"
            f"  expected (w,s,e,n) = {bbox_wsen}\n"
            f"  actual   (w,s,e,n) = ({minx:.5f}, {miny:.5f}, {maxx:.5f}, {maxy:.5f})"
        )
    print(f"  coords within expected bbox: OK")
