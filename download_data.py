#!/usr/bin/env python3
"""Download verified v1.0.1 research archives. Python 3.12+, standard library only.

Pieces are concatenated in manifest order. Nothing is extracted or executed.
Verified pieces are kept so interrupted runs can be resumed safely.
"""
from __future__ import annotations
import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
import hashlib
import http.client
import json
import os
from pathlib import Path
import re
import sys
import tempfile
import time
from urllib.parse import quote
from urllib.request import Request, urlopen

VERSION = "1.0.1"
BASE_URL = "https://github.com/AzizAlhassan-ai/local-permeability-arterial-traffic/releases/download/v1.0.1/"
CHUNK_BYTES = 8 * 1024 * 1024
ATTEMPTS = 3

class DataError(Exception):
    """Manifest, download, or local-file validation failure."""

def file_record(value: object, context: str) -> dict:
    if not isinstance(value, dict):
        raise DataError(f"{context}: expected a file record.")
    name, size, digest = value.get("name"), value.get("bytes"), value.get("sha256")
    if (not isinstance(name, str) or len(name) > 240
            or not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._-]*", name)):
        raise DataError(f"{context}: unsafe or invalid basename.")
    if type(size) is not int or size < 0:
        raise DataError(f"{context}: bytes must be a nonnegative integer.")
    if not isinstance(digest, str) or not re.fullmatch(r"[0-9a-fA-F]{64}", digest):
        raise DataError(f"{context}: invalid SHA-256 digest.")
    return {"name": name, "bytes": size, "sha256": digest.lower()}

def archive_group(name: str) -> str | None:
    if name == "processed-data.tar.gz":
        return "processed"
    if re.fullmatch(r"raw-[a-z][a-z_-]*\.tar\.gz", name):
        return "raw"
    if name == "hpms_2024_national.zip":
        return "hpms"
    return None

def read_manifest(path: Path) -> dict:
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        raise DataError(f"Cannot read manifest {path}: {exc}") from exc
    if not isinstance(raw, dict):
        raise DataError("Manifest must be a JSON object.")
    if raw.get("version") != VERSION or raw.get("base_url") != BASE_URL:
        raise DataError(f"This helper only supports the fixed GitHub release v{VERSION}.")
    if not isinstance(raw.get("archives"), list) or not raw["archives"]:
        raise DataError("Manifest must list at least one archive.")
    archives, archive_names = [], set()
    for i, entry in enumerate(raw["archives"]):
        archive = file_record(entry, f"archives[{i}]")
        name = archive["name"]
        if archive_group(name) is None or name in archive_names:
            raise DataError(f"Unsupported or duplicate logical archive name: {name}")
        archive_names.add(name)
        pieces = entry.get("pieces")
        if not isinstance(pieces, list) or not pieces:
            raise DataError(f"{name}: pieces must be a nonempty list.")
        archive["pieces"] = [file_record(p, f"{name} piece {j+1}") for j, p in enumerate(pieces)]
        if sum(p["bytes"] for p in archive["pieces"]) != archive["bytes"]:
            raise DataError(f"{name}: piece sizes do not sum to archive size.")
        same = [p for p in archive["pieces"] if p["name"] == name]
        if same and (len(archive["pieces"]) != 1
                or same[0] != {k: archive[k] for k in ("name", "bytes", "sha256")}):
            raise DataError(f"{name}: a same-name single piece must match its archive.")
        archives.append(archive)
    support = raw.get("support_files", [])
    if not isinstance(support, list):
        raise DataError("support_files must be a list.")
    support = [file_record(s, f"support_files[{i}]") for i, s in enumerate(support)]
    download_names = set()
    for archive in archives:
        for piece in archive["pieces"]:
            name = piece["name"]
            if name in download_names or (name in archive_names and name != archive["name"]):
                raise DataError(f"Duplicate or conflicting piece name: {name}")
            download_names.add(name)
    for item in support:
        if item["name"] in archive_names or item["name"] in download_names:
            raise DataError(f"Conflicting support-file name: {item['name']}")
        download_names.add(item["name"])
    return {"archives": archives, "support_files": support}

def checksum(path: Path) -> tuple[int, str]:
    digest, total = hashlib.sha256(), 0
    with path.open("rb") as stream:
        while chunk := stream.read(CHUNK_BYTES):
            digest.update(chunk)
            total += len(chunk)
    return total, digest.hexdigest()

def verified_existing(path: Path, record: dict) -> bool:
    """False means absent; a different existing file is never overwritten."""
    if path.is_symlink():
        raise DataError(f"Refusing symbolic-link destination: {path}")
    if not path.exists():
        return False
    if not path.is_file():
        raise DataError(f"Destination is not a regular file: {path}")
    if path.stat().st_size != record["bytes"] or checksum(path) != (record["bytes"], record["sha256"]):
        raise DataError(f"Existing file differs from the release: {path}. It was preserved; "
                        "move it aside or choose another --directory.")
    return True

def new_partial(directory: Path, name: str) -> tuple[int, Path]:
    fd, path = tempfile.mkstemp(prefix=f".{name}.", suffix=".partial", dir=directory)
    return fd, Path(path)

def publish_partial(partial: Path, destination: Path, record: dict) -> None:
    """Atomically promote without overwriting even a concurrently created user file.

    A same-directory hard-link promotion followed by unlinking our temporary name
    avoids the overwrite race of os.replace(). The destination appears complete.
    """
    try:
        os.link(partial, destination)
    except FileExistsError:
        if not verified_existing(destination, record):
            raise DataError(f"Destination changed during publication: {destination}")
    except OSError as exc:
        raise DataError(f"Cannot atomically publish {destination}: {exc}") from exc
    partial.unlink()

def download(record: dict, directory: Path) -> str:
    destination = directory / record["name"]
    if verified_existing(destination, record):
        return f"Verified existing: {record['name']}"
    last_error = None
    for attempt in range(1, ATTEMPTS + 1):
        fd, partial = new_partial(directory, record["name"])
        try:
            digest, total = hashlib.sha256(), 0
            request = Request(BASE_URL + quote(record["name"], safe=""), headers={
                "User-Agent": "permeability-data-downloader/1.0.1", "Accept": "application/octet-stream"})
            with os.fdopen(fd, "wb") as output:
                with urlopen(request, timeout=60) as response:
                    while chunk := response.read(CHUNK_BYTES):
                        total += len(chunk)
                        if total > record["bytes"]:
                            raise DataError("Downloaded content exceeds expected size.")
                        output.write(chunk)
                        digest.update(chunk)
                output.flush()
                os.fsync(output.fileno())
            if (total, digest.hexdigest()) != (record["bytes"], record["sha256"]):
                raise DataError("Downloaded size or SHA-256 does not match the manifest.")
            publish_partial(partial, destination, record)
            return f"Downloaded and verified: {record['name']}"
        except (OSError, DataError, ValueError, http.client.HTTPException) as exc:
            last_error = exc
            if attempt < ATTEMPTS:
                time.sleep(attempt)
        finally:
            if partial.exists():
                partial.unlink()
    raise DataError(f"{record['name']}: failed after {ATTEMPTS} attempts: {last_error}")

def assemble(archive: dict, directory: Path) -> str:
    destination = directory / archive["name"]
    if verified_existing(destination, archive):
        return f"Verified archive: {archive['name']}"
    fd, partial = new_partial(directory, archive["name"])
    try:
        total, digest = 0, hashlib.sha256()
        with os.fdopen(fd, "wb") as output:
            # Listed order is authoritative; names need no numeric interpretation.
            for piece in archive["pieces"]:
                path = directory / piece["name"]
                if path.is_symlink() or not path.is_file():
                    raise DataError(f"Missing or unsafe archive piece: {path}")
                part_size, part_digest = 0, hashlib.sha256()
                with path.open("rb") as source:
                    while chunk := source.read(CHUNK_BYTES):
                        total += len(chunk)
                        part_size += len(chunk)
                        if total > archive["bytes"] or part_size > piece["bytes"]:
                            raise DataError(f"Archive piece exceeds expected size: {path}")
                        output.write(chunk)
                        digest.update(chunk)
                        part_digest.update(chunk)
                if (part_size, part_digest.hexdigest()) != (piece["bytes"], piece["sha256"]):
                    raise DataError(f"Archive piece failed verification: {path}")
            output.flush()
            os.fsync(output.fileno())
        if (total, digest.hexdigest()) != (archive["bytes"], archive["sha256"]):
            raise DataError(f"Reassembled archive failed verification: {archive['name']}")
        publish_partial(partial, destination, archive)
        return f"Reassembled and verified: {archive['name']}"
    finally:
        if partial.exists():
            partial.unlink()

def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path,
                        default=Path(__file__).resolve().with_name("data-assets.json"),
                        help="Manifest JSON (default: beside this helper).")
    parser.add_argument("--directory", type=Path, default=Path("release-assets"),
                        help="Destination (default: release-assets).")
    parser.add_argument("--only", choices=("processed", "raw", "hpms", "all"), default="all")
    parser.add_argument("--verify-only", action="store_true",
                        help="Verify selected logical archives locally; no network, assembly, "
                             "or requirement for pieces/support files.")
    args = parser.parse_args(argv)
    try:
        manifest = read_manifest(args.manifest)
        archives = [a for a in manifest["archives"]
                    if args.only == "all" or archive_group(a["name"]) == args.only]
        if not archives:
            raise DataError(f"Manifest contains no archives for --only {args.only}.")
        directory = args.directory.expanduser().resolve()
        if args.verify_only:
            for archive in archives:
                if not verified_existing(directory / archive["name"], archive):
                    raise DataError(f"Missing archive: {directory / archive['name']}")
                print(f"Verified archive: {archive['name']}", flush=True)
            print(f"Verified {len(archives)} archives. No network used.")
            return 0
        directory.mkdir(parents=True, exist_ok=True)
        pending = []
        for archive in archives:
            if verified_existing(directory / archive["name"], archive):
                print(f"Verified archive: {archive['name']}", flush=True)
            else:
                pending.append(archive)
        records = [p for a in pending for p in a["pieces"]] + manifest["support_files"]
        # Preflight existing destinations before any network transfer.
        for record in records:
            path = directory / record["name"]
            if path.is_symlink() or path.exists():
                verified_existing(path, record)
        if records:
            print(f"Checking/downloading {len(records)} files with 4 workers.", flush=True)
            with ThreadPoolExecutor(max_workers=4) as executor:
                futures = [executor.submit(download, r, directory) for r in records]
                try:
                    for future in as_completed(futures):
                        print(future.result(), flush=True)
                except BaseException:
                    for future in futures:
                        future.cancel()
                    raise
        for archive in pending:
            print(assemble(archive, directory), flush=True)
        print(f"Ready: {len(archives)} verified archives in {directory}. Nothing extracted.")
        return 0
    except (DataError, OSError, ValueError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1
    except KeyboardInterrupt:
        print("Interrupted. Completed verified files are kept for the next run.", file=sys.stderr)
        return 130

if __name__ == "__main__":
    raise SystemExit(main())
