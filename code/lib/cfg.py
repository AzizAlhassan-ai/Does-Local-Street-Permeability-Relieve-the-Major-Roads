"""Config loading. Every parameter used anywhere in the pipeline comes from here."""

from __future__ import annotations

import os
from functools import lru_cache
from typing import Any

import yaml

from . import paths


@lru_cache(maxsize=None)
def config() -> dict[str, Any]:
    with open(paths.CONFIG / "config.yml") as f:
        return yaml.safe_load(f)


@lru_cache(maxsize=None)
def cities() -> dict[str, Any]:
    with open(paths.CONFIG / "cities.yml") as f:
        return yaml.safe_load(f)


def city(name: str) -> dict[str, Any]:
    c = cities()
    if name not in c:
        raise KeyError(f"City {name!r} not in config/cities.yml. Have: {sorted(c)}")
    return c[name]


def census_api_key() -> str | None:
    """Read the Census API key from the environment or a gitignored .env file.

    Returns None if absent — callers must handle that explicitly rather than
    failing deep inside a request.
    """
    key = os.environ.get("CENSUS_API_KEY")
    if key:
        return key.strip()
    env = paths.ROOT / ".env"
    if env.exists():
        for line in env.read_text().splitlines():
            line = line.strip()
            if line.startswith("CENSUS_API_KEY="):
                return line.split("=", 1)[1].strip().strip('"').strip("'")
    return None


def states(name: str) -> list[dict]:
    """States a city spans. Falls back to the legacy single-state field."""
    C = city(name)
    if C.get("states"):
        return C["states"]
    return [{"fips": C["state_fips"], "abbrev": None,
             "tiger_dir": None, "hpms_name": None}]


def url_for(kind: str, st: dict, **extra) -> str:
    """Build a source URL from the template in config.yml sources."""
    tpl = config()["sources"][f"{kind}_tpl" if not kind.endswith("_tpl") else kind]
    return tpl.format(**{**st, **extra})


def hpms_services(name: str) -> list[tuple[str, str]]:
    """[(state_fips, service_url)] for every state the city spans."""
    out = []
    for st in states(name):
        if st.get("hpms_name"):
            out.append((st["fips"], url_for("hpms_service", st)))
        else:                                   # legacy denver entry
            C = city(name)
            out.append((st["fips"], C["aadt"]["primary"]["service"]))
    return out


def land_use(name: str) -> dict:
    """City land-use config, falling back to shared defaults (D-048).

    Per-state URLs (LODES, TIGER blocks) are filled from the `sources` templates
    for the FIRST state; multi-state handling loops over cfg.states() in 01e.
    """
    C = city(name)
    if C.get("land_use"):
        return C["land_use"]
    d = {k: dict(v) for k, v in config()["land_use_defaults"].items()}
    st = states(name)[0]
    yr = d["lodes"]["year"]
    d["lodes"]["url_pattern"] = config()["sources"]["lodes_url_tpl"].format(
        abbrev=st["abbrev"], year="{year}")
    d["lodes"]["block_geometry_url"] = config()["sources"]["block_url_tpl"].format(**st)
    return d


def major_filter() -> str:
    """Overpass custom_filter selecting only major-road edges."""
    tags = "|".join(config()["network"]["major_highway_tags"])
    return f'["highway"~"^({tags})$"]'


def local_filter() -> str:
    """Overpass custom_filter selecting only local-road edges.

    Disjoint from major_filter() by construction — see config.yml D-001.
    """
    tags = "|".join(config()["network"]["local_highway_tags"])
    return f'["highway"~"^({tags})$"]'


def assert_filters_disjoint() -> None:
    n = config()["network"]
    overlap = set(n["major_highway_tags"]) & set(n["local_highway_tags"])
    if overlap:
        raise ValueError(
            f"major_highway_tags and local_highway_tags overlap on {sorted(overlap)}. "
            "The predictor would be computed on edges that also supply the outcome."
        )
