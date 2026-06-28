"""CSV export for displayed read-only browser pages."""

from __future__ import annotations

import csv
import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from .config import EXPORT_SAFE_ROW_LIMIT


class ExportError(Exception):
    """Raised for export validation errors."""


def export_rows_to_csv(
    destination: Path,
    columns: list[str],
    rows: list[dict[str, Any]],
    manifest: dict[str, Any],
    source_relation: str,
    active_filters: dict[str, str] | None = None,
    write_manifest: bool = False,
    row_limit: int = EXPORT_SAFE_ROW_LIMIT,
) -> Path:
    if len(rows) > row_limit:
        raise ExportError(f"Exportlimit überschritten: {len(rows)} > {row_limit}")
    destination.parent.mkdir(parents=True, exist_ok=True)
    with destination.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=columns)
        writer.writeheader()
        for row in rows:
            writer.writerow({column: row.get(column, "") for column in columns})
    if write_manifest:
        export_manifest = {
            "source_snapshot_checksum": manifest.get("snapshot_sha256", ""),
            "source_relation": source_relation,
            "active_filters": active_filters or {},
            "export_timestamp": datetime.now(UTC).replace(microsecond=0).isoformat(),
            "row_count": len(rows),
            "export_path": str(destination),
        }
        destination.with_suffix(destination.suffix + ".manifest.json").write_text(
            json.dumps(export_manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8"
        )
    return destination
