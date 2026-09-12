"""Machine-appended data provenance.

Every acquisition writes one row to notes/data-provenance.md recording where the
data came from, when, how much of it there was, and its hash. This is what makes
"verify before claiming done" mechanical instead of a promise.
"""

from __future__ import annotations

import hashlib
import platform
from datetime import datetime, timezone
from pathlib import Path

from . import paths

_HEADER = """# Data provenance

Machine-appended by `code/lib/provenance.py`. One row per acquisition.
Do not edit by hand — re-run the acquisition script instead.

| retrieved (UTC) | city | layer | source URL | rows | bytes | sha256 (first 16) | file |
|---|---|---|---|---|---|---|---|
"""


def sha256(path: Path, chunk: int = 1 << 20) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while block := f.read(chunk):
            h.update(block)
    return h.hexdigest()


def log(
    *,
    city: str,
    layer: str,
    source_url: str,
    rows: int | None,
    file_path: Path | None = None,
) -> None:
    paths.NOTES.mkdir(parents=True, exist_ok=True)
    log_path = paths.PROVENANCE_LOG
    if not log_path.exists():
        log_path.write_text(_HEADER)

    ts = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M")
    if file_path is not None and Path(file_path).exists():
        fp = Path(file_path)
        nbytes = fp.stat().st_size
        digest = sha256(fp)[:16]
        rel = fp.relative_to(paths.ROOT) if paths.ROOT in fp.parents else fp.name
    else:
        nbytes, digest, rel = "", "", ""

    row = (
        f"| {ts} | {city} | {layer} | {source_url} | "
        f"{rows if rows is not None else ''} | {nbytes} | {digest} | `{rel}` |\n"
    )
    with open(log_path, "a") as f:
        f.write(row)


def log_progress(stage: str, message: str) -> None:
    """Append a line to PROGRESS.md. Append-only run log."""
    p = paths.PROGRESS_LOG
    if not p.exists():
        p.write_text(
            "# Progress log\n\nAppend-only. Written by `code/lib/provenance.py`.\n\n"
        )
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M")
    with open(p, "a") as f:
        f.write(f"- **{ts} UTC** · `{stage}` · {message}\n")


def environment_stamp() -> str:
    import geopandas
    import networkx
    import osmnx
    import pandas

    return (
        f"python {platform.python_version()} · osmnx {osmnx.__version__} · "
        f"geopandas {geopandas.__version__} · pandas {pandas.__version__} · "
        f"networkx {networkx.__version__}"
    )
