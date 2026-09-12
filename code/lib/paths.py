"""Project paths. Resolved relative to this file — never hard-coded, never absolute.

This module exists because the single most common reproducibility failure in the
surrounding portfolio was a script with an absolute path to a machine that no
longer exists.
"""

from __future__ import annotations

import os
from pathlib import Path

# code/lib/paths.py -> parents[2] is the project root
ROOT = Path(__file__).resolve().parents[2]

CONFIG = ROOT / "config"
CODE = ROOT / "code"

DATA = ROOT / "data"
RAW = DATA / "raw"
CACHE = DATA / "cache"
PROCESSED = DATA / "processed"

# D-086. A named pipeline VARIANT re-runs the whole chain against an alternative
# analytic choice without disturbing the primary outputs. Raw acquisitions (data/raw)
# are shared; everything derived is namespaced. Set with the PIPE_VARIANT env var:
#     PIPE_VARIANT=aadtfree uv run python code/02_network/02a_analysis_frame.py --city denver
VARIANT = os.environ.get("PIPE_VARIANT", "").strip()
_VSUF = f"__{VARIANT}" if VARIANT else ""

ANALYSIS = DATA / ("analysis" + _VSUF)

OUTPUTS = ROOT / "outputs"
FIGURES = OUTPUTS / "figures"
TABLES = OUTPUTS / "tables"
MODELS = OUTPUTS / "models"

NOTES = ROOT / "notes"
MANUSCRIPT = ROOT / "manuscript"

PROVENANCE_LOG = NOTES / "data-provenance.md"
PROGRESS_LOG = ROOT / "PROGRESS.md"


def raw(city: str, layer: str) -> Path:
    """data/raw/<city>/<layer>/ — created on demand, write-once by convention."""
    p = RAW / city / layer
    p.mkdir(parents=True, exist_ok=True)
    return p


def processed(city: str) -> Path:
    p = PROCESSED / (city + _VSUF)
    p.mkdir(parents=True, exist_ok=True)
    return p


def ensure_all() -> None:
    for p in (RAW, CACHE, PROCESSED, ANALYSIS, FIGURES, TABLES, MODELS, NOTES):
        p.mkdir(parents=True, exist_ok=True)
