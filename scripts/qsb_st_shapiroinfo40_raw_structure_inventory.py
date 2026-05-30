#!/usr/bin/env python3
"""QSB-ST ShapiroInfo raw structure inventory.

This script implements the SHAPIROINFO39 structure-only inventory plan. It is
technical inventory code, not physics analysis code. It never executes raw file
contents, never modifies raw artifacts, and does not make Bridge or physical
residual claims.
"""

from __future__ import annotations

import argparse
import csv
import json
import os
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


DEFAULT_INPUT_ROOT = Path("data/QSB-ST-SHAPIROINFO/public_sources/")
DEFAULT_OUTPUT_ROOT = Path(
    "runs/QSB-ST-SHAPIROINFO/SHAPIROINFO39_RAW_STRUCTURE_INVENTORY/"
)

CSV_EXTENSIONS = {
    ".csv": ("csv", ","),
    ".tsv": ("tsv", "\t"),
}

TEXT_EXTENSIONS = {".txt", ".md", ".log"}
JSON_EXTENSIONS = {".json"}
YAML_EXTENSIONS = {".yaml", ".yml"}
CHECKSUM_EXTENSIONS = {".sha256"}
PARAMETER_EXTENSIONS = {".par"}
TIMING_EXTENSIONS = {".tim"}

CLAIM_BOUNDARY = (
    "Claim boundary: this is a technical raw structure inventory only. "
    "It does not perform physical residual search, signal search, model "
    "fitting, physical interpretation, or QSB-ST Bridge-related claims. "
    "It does not validate the QSB-ST Bridge."
)

TABLE_FIELDS = [
    "relative_path",
    "filename",
    "suffix",
    "size_bytes",
    "apparent_type_by_extension",
    "is_file",
    "is_symlink",
    "parser_attempted",
    "parse_status",
    "row_count",
    "column_count",
    "column_names",
    "json_top_level_type",
    "json_top_level_keys",
    "text_line_count",
    "nonempty_line_count",
    "blank_line_count",
    "comment_line_count",
    "checksum_like_line_count",
    "malformed_line_count",
    "checksum_algorithm_by_extension",
    "yaml_parse_mode",
    "yaml_top_level_type",
    "yaml_top_level_keys",
    "shallow_key_count",
    "key_value_like_line_count",
    "apparent_parameter_file",
    "data_like_line_count",
    "delimiter_hint",
    "apparent_column_count_min",
    "apparent_column_count_max",
    "parse_error",
]


def apparent_type_by_extension(suffix: str) -> str:
    """Return a conservative type label from the file suffix only."""
    if suffix in CSV_EXTENSIONS:
        return CSV_EXTENSIONS[suffix][0]
    if suffix in JSON_EXTENSIONS:
        return "json"
    if suffix in TEXT_EXTENSIONS:
        return "text"
    if suffix in YAML_EXTENSIONS:
        return "yaml_structure"
    if suffix in CHECKSUM_EXTENSIONS:
        return "checksum_text"
    if suffix in PARAMETER_EXTENSIONS:
        return "parameter_text"
    if suffix in TIMING_EXTENSIONS:
        return "timing_text"
    if suffix:
        return "metadata_only"
    return "metadata_only_no_extension"


def empty_record(path: Path, input_root: Path) -> dict[str, Any]:
    """Build the common per-file inventory record without parsing content."""
    suffix = path.suffix.lower()
    try:
        relative_path = path.relative_to(input_root).as_posix()
    except ValueError:
        relative_path = path.as_posix()

    try:
        size_bytes = path.lstat().st_size
    except OSError as exc:
        size_bytes = None
        parse_error = f"stat_failed: {exc}"
    else:
        parse_error = None

    return {
        "relative_path": relative_path,
        "filename": path.name,
        "suffix": suffix,
        "size_bytes": size_bytes,
        "apparent_type_by_extension": apparent_type_by_extension(suffix),
        "is_file": path.is_file() and not path.is_symlink(),
        "is_symlink": path.is_symlink(),
        "parser_attempted": "none",
        "parse_status": "metadata_only",
        "row_count": None,
        "column_count": None,
        "column_names": [],
        "json_top_level_type": None,
        "json_top_level_keys": [],
        "text_line_count": None,
        "nonempty_line_count": None,
        "blank_line_count": None,
        "comment_line_count": None,
        "checksum_like_line_count": None,
        "malformed_line_count": None,
        "checksum_algorithm_by_extension": None,
        "yaml_parse_mode": None,
        "yaml_top_level_type": None,
        "yaml_top_level_keys": [],
        "shallow_key_count": None,
        "key_value_like_line_count": None,
        "apparent_parameter_file": None,
        "data_like_line_count": None,
        "delimiter_hint": None,
        "apparent_column_count_min": None,
        "apparent_column_count_max": None,
        "parse_error": parse_error,
    }


def safe_parse_csv_like(path: Path, delimiter: str, parser_name: str) -> dict[str, Any]:
    """Parse simple CSV or TSV files with the standard csv module."""
    row_count = 0
    column_count = None
    column_names: list[str] = []

    try:
        with path.open("r", encoding="utf-8-sig", newline="") as handle:
            reader = csv.reader(handle, delimiter=delimiter)
            for row_index, row in enumerate(reader):
                row_count += 1
                if row_index == 0:
                    column_names = [str(value) for value in row]
                    column_count = len(row)
                elif column_count is not None:
                    column_count = max(column_count, len(row))
    except (csv.Error, OSError, UnicodeError) as exc:
        return {
            "parser_attempted": parser_name,
            "parse_status": "parse_failed",
            "parse_error": f"{type(exc).__name__}: {exc}",
        }

    if column_count is None:
        column_count = 0

    return {
        "parser_attempted": parser_name,
        "parse_status": "parsed",
        "row_count": row_count,
        "column_count": column_count,
        "column_names": column_names,
        "parse_error": None,
    }


def safe_parse_json(path: Path) -> dict[str, Any]:
    """Parse JSON only enough to identify top-level structure."""
    try:
        with path.open("r", encoding="utf-8") as handle:
            data = json.load(handle)
    except (json.JSONDecodeError, OSError, UnicodeError) as exc:
        return {
            "parser_attempted": "json",
            "parse_status": "parse_failed",
            "parse_error": f"{type(exc).__name__}: {exc}",
        }

    top_level_type = type(data).__name__
    top_level_keys: list[str] = []
    if isinstance(data, dict):
        top_level_keys = [str(key) for key in data.keys()]

    return {
        "parser_attempted": "json",
        "parse_status": "parsed",
        "json_top_level_type": top_level_type,
        "json_top_level_keys": top_level_keys,
        "parse_error": None,
    }


def safe_parse_text(path: Path) -> dict[str, Any]:
    """Count UTF-8 text lines for simple text-like files."""
    try:
        with path.open("r", encoding="utf-8") as handle:
            text_line_count = sum(1 for _ in handle)
    except (OSError, UnicodeError) as exc:
        return {
            "parser_attempted": "text",
            "parse_status": "parse_failed",
            "parse_error": f"{type(exc).__name__}: {exc}",
        }

    return {
        "parser_attempted": "text",
        "parse_status": "parsed",
        "text_line_count": text_line_count,
        "parse_error": None,
    }


def safe_read_text_lines(
    path: Path, parser_name: str
) -> tuple[list[str] | None, dict[str, Any] | None]:
    """Read UTF-8 text lines for shallow structure-only parsing."""
    try:
        with path.open("r", encoding="utf-8") as handle:
            return handle.read().splitlines(), None
    except (OSError, UnicodeError) as exc:
        return None, {
            "parser_attempted": parser_name,
            "parse_status": "parse_failed",
            "parse_error": f"{type(exc).__name__}: {exc}",
        }


def is_comment_like(line: str) -> bool:
    """Detect simple comment-like lines without interpreting content."""
    stripped = line.strip()
    if not stripped:
        return False
    upper = stripped.upper()
    return (
        stripped.startswith("#")
        or stripped.startswith("//")
        or stripped.startswith(";")
        or stripped.startswith("%")
        or upper.startswith("C ")
        or upper == "C"
        or upper.startswith("COMMENT")
    )


def count_text_structure(lines: list[str]) -> dict[str, int]:
    """Count shallow text structure shared by several parser extensions."""
    blank_line_count = 0
    comment_line_count = 0
    nonempty_line_count = 0

    for line in lines:
        if line.strip():
            nonempty_line_count += 1
            if is_comment_like(line):
                comment_line_count += 1
        else:
            blank_line_count += 1

    return {
        "text_line_count": len(lines),
        "nonempty_line_count": nonempty_line_count,
        "blank_line_count": blank_line_count,
        "comment_line_count": comment_line_count,
    }


def parse_checksum_text(path: Path) -> dict[str, Any]:
    """Parse .sha256 files as checksum-line structure only."""
    lines, error = safe_read_text_lines(path, "checksum_text")
    if error is not None:
        return error
    assert lines is not None

    counts = count_text_structure(lines)
    checksum_like_line_count = 0

    for line in lines:
        stripped = line.strip()
        if not stripped:
            continue
        first_token = stripped.split(maxsplit=1)[0].lower()
        if len(first_token) == 64 and all(char in "0123456789abcdef" for char in first_token):
            checksum_like_line_count += 1

    malformed_line_count = counts["nonempty_line_count"] - checksum_like_line_count
    return {
        "parser_attempted": "checksum_text",
        "parse_status": "parsed",
        "text_line_count": counts["text_line_count"],
        "nonempty_line_count": counts["nonempty_line_count"],
        "checksum_like_line_count": checksum_like_line_count,
        "malformed_line_count": malformed_line_count,
        "checksum_algorithm_by_extension": "sha256",
        "parse_error": None,
    }


def shallow_yaml_key_scan(lines: list[str]) -> list[str]:
    """Scan top-level YAML-like keys without resolving or interpreting values."""
    keys: list[str] = []
    seen: set[str] = set()

    for line in lines:
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        if line[:1].isspace() or stripped.startswith("-") or ":" not in line:
            continue
        key = line.split(":", 1)[0].strip()
        if key and key not in seen:
            seen.add(key)
            keys.append(key)

    return keys


def parse_shallow_yaml(path: Path) -> dict[str, Any]:
    """Parse YAML shallowly, using safe_load only when already available."""
    lines, error = safe_read_text_lines(path, "yaml")
    if error is not None:
        return error
    assert lines is not None

    counts = count_text_structure(lines)
    try:
        import yaml  # type: ignore[import-not-found]
    except ImportError:
        yaml = None  # type: ignore[assignment]

    if yaml is not None:
        try:
            data = yaml.safe_load("\n".join(lines))
        except Exception:
            top_level_keys = shallow_yaml_key_scan(lines)
            return {
                "parser_attempted": "yaml",
                "parse_status": "parsed",
                "yaml_parse_mode": "shallow_text_key_scan_after_safe_load_error",
                "yaml_top_level_type": "mapping_like" if top_level_keys else "unknown_text",
                "yaml_top_level_keys": top_level_keys,
                "shallow_key_count": len(top_level_keys),
                "text_line_count": counts["text_line_count"],
                "parse_error": None,
            }

        top_level_type = type(data).__name__
        top_level_keys = [str(key) for key in data.keys()] if isinstance(data, dict) else []
        return {
            "parser_attempted": "yaml",
            "parse_status": "parsed",
            "yaml_parse_mode": "pyyaml_safe_load",
            "yaml_top_level_type": top_level_type,
            "yaml_top_level_keys": top_level_keys,
            "shallow_key_count": len(top_level_keys),
            "text_line_count": counts["text_line_count"],
            "parse_error": None,
        }

    top_level_keys = shallow_yaml_key_scan(lines)
    return {
        "parser_attempted": "yaml",
        "parse_status": "parsed",
        "yaml_parse_mode": "shallow_text_key_scan",
        "yaml_top_level_type": "mapping_like" if top_level_keys else "unknown_text",
        "yaml_top_level_keys": top_level_keys,
        "shallow_key_count": len(top_level_keys),
        "text_line_count": counts["text_line_count"],
        "parse_error": None,
    }


def parse_parameter_text(path: Path) -> dict[str, Any]:
    """Parse .par files as shallow parameter-like text structure only."""
    lines, error = safe_read_text_lines(path, "parameter_text")
    if error is not None:
        return error
    assert lines is not None

    counts = count_text_structure(lines)
    key_value_like_line_count = 0

    for line in lines:
        stripped = line.strip()
        if not stripped or is_comment_like(line):
            continue
        if "=" in stripped or ":" in stripped or len(stripped.split()) >= 2:
            key_value_like_line_count += 1

    return {
        "parser_attempted": "parameter_text",
        "parse_status": "parsed",
        "text_line_count": counts["text_line_count"],
        "blank_line_count": counts["blank_line_count"],
        "comment_line_count": counts["comment_line_count"],
        "key_value_like_line_count": key_value_like_line_count,
        "apparent_parameter_file": True,
        "parse_error": None,
    }


def parse_timing_text(path: Path) -> dict[str, Any]:
    """Parse .tim files as shallow timing/table-like text structure only."""
    lines, error = safe_read_text_lines(path, "timing_text")
    if error is not None:
        return error
    assert lines is not None

    counts = count_text_structure(lines)
    delimiter_hints: set[str] = set()
    column_counts: list[int] = []
    data_like_line_count = 0

    for line in lines:
        stripped = line.strip()
        if not stripped or is_comment_like(line):
            continue

        data_like_line_count += 1
        line_hints: set[str] = set()
        if "\t" in line:
            line_hints.add("tab")
        if "," in line:
            line_hints.add("comma")
        if len(stripped.split()) > 1:
            line_hints.add("whitespace")
        delimiter_hints.update(line_hints or {"none"})

        if "\t" in line:
            columns = [value for value in line.split("\t") if value.strip()]
        elif "," in line:
            columns = [value for value in line.split(",") if value.strip()]
        else:
            columns = stripped.split()
        column_counts.append(len(columns))

    if not delimiter_hints:
        delimiter_hint = None
    elif len(delimiter_hints) == 1:
        delimiter_hint = next(iter(delimiter_hints))
    else:
        delimiter_hint = "mixed"

    return {
        "parser_attempted": "timing_text",
        "parse_status": "parsed",
        "text_line_count": counts["text_line_count"],
        "blank_line_count": counts["blank_line_count"],
        "comment_line_count": counts["comment_line_count"],
        "data_like_line_count": data_like_line_count,
        "delimiter_hint": delimiter_hint,
        "apparent_column_count_min": min(column_counts) if column_counts else 0,
        "apparent_column_count_max": max(column_counts) if column_counts else 0,
        "parse_error": None,
    }


def inventory_file(path: Path, input_root: Path) -> dict[str, Any]:
    """Inventory one path without physical interpretation or deep binary parsing."""
    record = empty_record(path, input_root)

    if record["parse_error"]:
        record["parse_status"] = "metadata_only"
        return record

    if record["is_symlink"]:
        record["parse_status"] = "metadata_only"
        record["parse_error"] = "symlink_not_followed"
        return record

    if not record["is_file"]:
        record["parse_status"] = "unsupported"
        record["parse_error"] = "not_a_regular_file"
        return record

    suffix = record["suffix"]
    if suffix in CSV_EXTENSIONS:
        parser_name, delimiter = CSV_EXTENSIONS[suffix]
        record.update(safe_parse_csv_like(path, delimiter, parser_name))
    elif suffix in JSON_EXTENSIONS:
        record.update(safe_parse_json(path))
    elif suffix in TEXT_EXTENSIONS:
        record.update(safe_parse_text(path))
    elif suffix in YAML_EXTENSIONS:
        record.update(parse_shallow_yaml(path))
    elif suffix in CHECKSUM_EXTENSIONS:
        record.update(parse_checksum_text(path))
    elif suffix in PARAMETER_EXTENSIONS:
        record.update(parse_parameter_text(path))
    elif suffix in TIMING_EXTENSIONS:
        record.update(parse_timing_text(path))
    else:
        record["parse_status"] = "metadata_only"
        record["parse_error"] = "unsupported_extension_metadata_only"

    return record


def iter_inventory_paths(input_root: Path) -> list[Path]:
    """Return deterministic file-like paths without following directory symlinks."""
    paths: list[Path] = []
    for root, dirnames, filenames in os.walk(input_root, followlinks=False):
        dirnames[:] = sorted(dirnames)
        root_path = Path(root)

        for dirname in list(dirnames):
            candidate = root_path / dirname
            if candidate.is_symlink():
                paths.append(candidate)

        for filename in sorted(filenames):
            paths.append(root_path / filename)

    return sorted(paths, key=lambda item: item.relative_to(input_root).as_posix())


def json_ready_record(record: dict[str, Any]) -> dict[str, Any]:
    """Keep CSV cells stable by serializing list fields as JSON strings."""
    ready = dict(record)
    for key in ("column_names", "json_top_level_keys", "yaml_top_level_keys"):
        ready[key] = json.dumps(ready.get(key, []), ensure_ascii=False)
    return ready


def write_outputs(
    records: list[dict[str, Any]],
    input_root: Path,
    output_root: Path,
    run_status: str,
    stop_reasons: list[str],
) -> None:
    """Write the five SHAPIROINFO39 inventory outputs."""
    output_root.mkdir(parents=True, exist_ok=True)

    status_counts = Counter(record["parse_status"] for record in records)
    extension_counts = Counter(record["suffix"] or "<none>" for record in records)
    parse_failures = [
        record
        for record in records
        if record["parse_status"] == "parse_failed" or record["parse_error"]
    ]
    total_records = len(records)

    config = {
        "input_root": input_root.as_posix(),
        "output_root": output_root.as_posix(),
        "allowed_parsers": {
            ".csv": "csv module",
            ".tsv": "csv module with tab delimiter",
            ".json": "json module",
            ".txt": "UTF-8 line count",
            ".md": "UTF-8 line count",
            ".log": "UTF-8 line count",
            ".sha256": "checksum text structure",
            ".yaml": "shallow YAML structure",
            ".yml": "shallow YAML structure",
            ".par": "parameter-like text structure",
            ".tim": "timing/table-like text structure",
            "other": "metadata_only",
        },
        "raw_artifact_policy": "read_only_no_copy_no_tracking",
        "claim_boundary": CLAIM_BOUNDARY,
    }

    summary = {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "run_status": run_status,
        "stop_reasons": stop_reasons,
        "input_root": input_root.as_posix(),
        "output_root": output_root.as_posix(),
        "total_records": total_records,
        "file_count": total_records,
        "parsed_file_count": status_counts.get("parsed", 0),
        "metadata_only_count": status_counts.get("metadata_only", 0),
        "unsupported_count": status_counts.get("unsupported", 0),
        "parse_status_counts": dict(sorted(status_counts.items())),
        "extension_counts": dict(sorted(extension_counts.items())),
        "parse_failure_count": len(parse_failures),
        "output_files": [
            "raw_structure_inventory_summary.json",
            "raw_structure_inventory_table.csv",
            "raw_structure_inventory_readout.md",
            "parse_failures.csv",
            "inventory_config_resolved.json",
        ],
        "claim_boundary": CLAIM_BOUNDARY,
    }

    (output_root / "inventory_config_resolved.json").write_text(
        json.dumps(config, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    (output_root / "raw_structure_inventory_summary.json").write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )

    with (output_root / "raw_structure_inventory_table.csv").open(
        "w", encoding="utf-8", newline=""
    ) as handle:
        writer = csv.DictWriter(handle, fieldnames=TABLE_FIELDS)
        writer.writeheader()
        for record in records:
            writer.writerow(json_ready_record(record))

    with (output_root / "parse_failures.csv").open(
        "w", encoding="utf-8", newline=""
    ) as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=[
                "relative_path",
                "parser_attempted",
                "parse_status",
                "parse_error",
            ],
        )
        writer.writeheader()
        for record in parse_failures:
            writer.writerow(
                {
                    "relative_path": record["relative_path"],
                    "parser_attempted": record["parser_attempted"],
                    "parse_status": record["parse_status"],
                    "parse_error": record["parse_error"],
                }
            )

    readout = build_readout(summary)
    (output_root / "raw_structure_inventory_readout.md").write_text(
        readout, encoding="utf-8"
    )


def build_readout(summary: dict[str, Any]) -> str:
    """Build a human-readable readout with explicit claim boundary text."""
    lines = [
        "# QSB-ST SHAPIROINFO39 Raw Structure Inventory Readout",
        "",
        f"Generated UTC: {summary['generated_at_utc']}",
        f"Run status: {summary['run_status']}",
        f"Input root: {summary['input_root']}",
        f"Output root: {summary['output_root']}",
        "",
        "## Technical Summary",
        "",
        f"Total records: {summary['total_records']}",
        f"Parse failure count: {summary['parse_failure_count']}",
        "",
        "Parse status counts:",
    ]

    for key, value in summary["parse_status_counts"].items():
        lines.append(f"- {key}: {value}")

    lines.extend(
        [
            "",
            "Extension counts:",
        ]
    )
    for key, value in summary["extension_counts"].items():
        lines.append(f"- {key}: {value}")

    lines.extend(
        [
            "",
            "## Stop Reasons",
            "",
        ]
    )
    if summary["stop_reasons"]:
        for reason in summary["stop_reasons"]:
            lines.append(f"- {reason}")
    else:
        lines.append("- none")

    lines.extend(
        [
            "",
            "## Claim Boundary",
            "",
            CLAIM_BOUNDARY,
            "",
            "This readout is inventory, not interpretation.",
            "It does not provide evidence for a physical Shapiro-information residual.",
            "It does not validate the QSB-ST Bridge.",
            "",
        ]
    )
    return "\n".join(lines)


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Create a structure-only inventory of local QSB-ST ShapiroInfo raw "
            "artifacts. No physical interpretation is performed."
        )
    )
    parser.add_argument(
        "--input-root",
        default=DEFAULT_INPUT_ROOT.as_posix(),
        help="Read-only raw artifact root.",
    )
    parser.add_argument(
        "--output-root",
        default=DEFAULT_OUTPUT_ROOT.as_posix(),
        help="Output directory for inventory run artifacts.",
    )
    return parser


def main() -> int:
    parser = build_arg_parser()
    args = parser.parse_args()

    input_root = Path(args.input_root)
    output_root = Path(args.output_root)
    records: list[dict[str, Any]] = []
    stop_reasons: list[str] = []

    if not input_root.exists():
        run_status = "stopped"
        stop_reasons.append("input_root_missing")
    elif not input_root.is_dir():
        run_status = "stopped"
        stop_reasons.append("input_root_not_directory")
    else:
        run_status = "completed"
        for path in iter_inventory_paths(input_root):
            records.append(inventory_file(path, input_root))

    write_outputs(records, input_root, output_root, run_status, stop_reasons)
    print(f"wrote inventory outputs under: {output_root}")
    print(CLAIM_BOUNDARY)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
