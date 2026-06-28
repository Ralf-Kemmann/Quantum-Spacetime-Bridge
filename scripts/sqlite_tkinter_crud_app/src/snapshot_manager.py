"""Verified snapshot creation for QSB metadata catalogs."""

from __future__ import annotations

import hashlib
import json
import os
import shutil
import sqlite3
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from .config import APP_VERSION, DEFAULT_QSB_METADATA_DB, HARDENED_QSB_METADATA_DB, SNAPSHOT_DIR


class SnapshotError(Exception):
    """Raised for snapshot creation or validation failures."""


@dataclass(frozen=True)
class SnapshotInfo:
    source_path: Path
    snapshot_path: Path
    manifest_path: Path
    manifest: dict[str, Any]
    used_snapshot: bool
    warning: str = ""


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def repository_relative(path: Path, repo_root: Path | None = None) -> str:
    root = (repo_root or Path.cwd()).resolve()
    try:
        return path.resolve().relative_to(root).as_posix()
    except ValueError:
        return ""


def resolve_source_database(cli_path: str | None, environ: dict[str, str] | None = None) -> Path:
    env = os.environ if environ is None else environ
    candidates: list[Path] = []
    if cli_path:
        candidates.append(Path(cli_path).expanduser())
    elif env.get("QSB_METADATA_DB"):
        candidates.append(Path(env["QSB_METADATA_DB"]).expanduser())
    else:
        candidates.extend([HARDENED_QSB_METADATA_DB, DEFAULT_QSB_METADATA_DB])
    for candidate in candidates:
        resolved = candidate.resolve()
        if resolved.exists() and resolved.is_file():
            return resolved
    raise SnapshotError("Keine vorhandene QSB-Metadatenbank in der Auflösungsreihenfolge gefunden.")


def validate_sqlite_database(path: Path) -> None:
    if not path.exists() or not path.is_file():
        raise SnapshotError(f"Quelldatenbank nicht gefunden: {path}")
    try:
        uri = f"file:{path.as_posix()}?mode=ro"
        with sqlite3.connect(uri, uri=True) as conn:
            result = conn.execute("PRAGMA quick_check").fetchone()
            if not result or result[0] != "ok":
                raise SnapshotError(f"SQLite quick_check fehlgeschlagen: {result}")
    except sqlite3.Error as exc:
        raise SnapshotError("Quelle ist keine gültige lesbare SQLite-Datenbank.") from exc


def inspect_source(path: Path) -> dict[str, Any]:
    uri = f"file:{path.as_posix()}?mode=ro"
    with sqlite3.connect(uri, uri=True) as conn:
        conn.row_factory = sqlite3.Row
        table_count = conn.execute("SELECT COUNT(*) FROM sqlite_master WHERE type='table'").fetchone()[0]
        view_count = conn.execute("SELECT COUNT(*) FROM sqlite_master WHERE type='view'").fetchone()[0]
        mart_codes = []
        work_package_codes = []
        names = {row["name"] for row in conn.execute("SELECT name FROM sqlite_master WHERE type='table'")}
        if "meta_mart" in names:
            mart_codes = [row[0] for row in conn.execute("SELECT mart_code FROM meta_mart ORDER BY mart_code")]
        if "meta_work_package" in names:
            work_package_codes = [
                row[0] for row in conn.execute("SELECT work_package_code FROM meta_work_package ORDER BY work_package_code")
            ]
    return {
        "detected_table_count": table_count,
        "detected_view_count": view_count,
        "detected_mart_codes": mart_codes,
        "detected_work_package_codes": work_package_codes,
    }


def create_verified_snapshot(
    source_path: Path,
    snapshot_dir: Path = SNAPSHOT_DIR,
    overwrite_snapshot: bool = False,
    timestamp: str | None = None,
    repo_root: Path | None = None,
) -> SnapshotInfo:
    validate_sqlite_database(source_path)
    snapshot_dir.mkdir(parents=True, exist_ok=True)
    stamp = timestamp or datetime.now(UTC).strftime("%Y%m%d_%H%M%S_%f")
    snapshot_path = snapshot_dir / f"qsb_metadata_snapshot_{stamp}.sqlite"
    manifest_path = snapshot_dir / f"qsb_metadata_snapshot_{stamp}.manifest.json"
    if (snapshot_path.exists() or manifest_path.exists()) and not overwrite_snapshot:
        raise SnapshotError(f"Snapshot existiert bereits: {snapshot_path}")
    if overwrite_snapshot and snapshot_path.exists():
        try:
            snapshot_path.chmod(0o644)
        except OSError:
            pass
    source_checksum = sha256_file(source_path)
    shutil.copy2(source_path, snapshot_path)
    snapshot_checksum = sha256_file(snapshot_path)
    if source_checksum != snapshot_checksum:
        raise SnapshotError("Snapshot-Prüfsumme stimmt nicht mit Quelle überein.")
    try:
        snapshot_path.chmod(0o444)
    except OSError:
        pass
    source_info = inspect_source(source_path)
    manifest = {
        "source_database_path": str(source_path),
        "source_database_repository_relative_path": repository_relative(source_path, repo_root),
        "snapshot_path": str(snapshot_path),
        "source_sha256": source_checksum,
        "snapshot_sha256": snapshot_checksum,
        "source_size_bytes": source_path.stat().st_size,
        "snapshot_size_bytes": snapshot_path.stat().st_size,
        "creation_timestamp": datetime.now(UTC).replace(microsecond=0).isoformat(),
        "application_version": APP_VERSION,
        "snapshot_status": "verified",
        **source_info,
    }
    manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return SnapshotInfo(source_path, snapshot_path, manifest_path, manifest, used_snapshot=True)


def use_source_without_snapshot(source_path: Path) -> SnapshotInfo:
    validate_sqlite_database(source_path)
    source_checksum = sha256_file(source_path)
    manifest = {
        "source_database_path": str(source_path),
        "source_database_repository_relative_path": repository_relative(source_path),
        "snapshot_path": str(source_path),
        "source_sha256": source_checksum,
        "snapshot_sha256": source_checksum,
        "source_size_bytes": source_path.stat().st_size,
        "snapshot_size_bytes": source_path.stat().st_size,
        "creation_timestamp": datetime.now(UTC).replace(microsecond=0).isoformat(),
        "application_version": APP_VERSION,
        "snapshot_status": "developer_no_snapshot_warning",
        **inspect_source(source_path),
    }
    return SnapshotInfo(source_path, source_path, source_path.with_suffix(".no_snapshot_manifest.json"), manifest, False, "NO SNAPSHOT MODE")
