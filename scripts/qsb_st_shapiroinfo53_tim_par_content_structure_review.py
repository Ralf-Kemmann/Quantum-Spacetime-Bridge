#!/usr/bin/env python3
"""QSB-ST ShapiroInfo TIM/PAR content-structure review.

This script implements the SHAPIROINFO52 controlled content-structure plan. It
is limited to field, row, header, parameter-name, comment, delimiter, and
value-format structure. It does not perform physical value interpretation,
residual_search, model_fitting, anomaly claims, or QSB-ST Bridge confirmation.
"""

from __future__ import annotations

import argparse
import csv
import json
import re
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


DEFAULT_INVENTORY_ROOT = Path(
    "runs/QSB-ST-SHAPIROINFO/SHAPIROINFO39_RAW_STRUCTURE_INVENTORY/"
)
DEFAULT_RAW_INPUT_ROOT = Path("data/QSB-ST-SHAPIROINFO/public_sources/")
DEFAULT_OUTPUT_ROOT = Path(
    "runs/QSB-ST-SHAPIROINFO/SHAPIROINFO53_TIM_PAR_CONTENT_STRUCTURE_REVIEW/"
)

INVENTORY_TABLE_NAME = "raw_structure_inventory_table.csv"
MAX_SNIPPETS_PER_FILE = 50
SNIPPET_CHAR_LIMIT = 160

TIM_ROW_CLASSES = ["blank", "comment_like", "header_like", "data_like", "malformed_like"]
PAR_ROW_CLASSES = ["blank", "comment_like", "key_value_like", "malformed_like"]

CLAIM_BOUNDARY = (
    "Claim boundary: this is a controlled content-structure review only. "
    "It does not perform physical value interpretation, residual search, "
    "model fitting, anomaly claims, or QSB-ST Bridge confirmation. It does "
    "not validate the QSB-ST Bridge."
)

OUTPUT_FILES = [
    "tim_content_structure_summary.json",
    "tim_row_format_inventory.csv",
    "tim_column_count_distribution.csv",
    "tim_header_comment_inventory.csv",
    "par_content_structure_summary.json",
    "par_parameter_name_inventory.csv",
    "par_parameter_prefix_groups.csv",
    "par_value_format_classes.csv",
    "tim_par_content_structure_review_readout.md",
    "content_structure_review_config_resolved.json",
]


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def read_inventory_targets(inventory_table: Path) -> tuple[list[str], list[str], list[str]]:
    """Return .tim and .par relative paths from the existing inventory table."""
    tim_paths: list[str] = []
    par_paths: list[str] = []
    warnings: list[str] = []

    try:
        with inventory_table.open("r", encoding="utf-8", newline="") as handle:
            reader = csv.DictReader(handle)
            for row_number, row in enumerate(reader, start=2):
                relative_path = (row.get("relative_path") or "").strip()
                suffix = (row.get("suffix") or "").strip().lower()
                if not relative_path:
                    warnings.append(f"inventory row {row_number}: missing relative_path")
                    continue
                if suffix == ".tim":
                    tim_paths.append(relative_path)
                elif suffix == ".par":
                    par_paths.append(relative_path)
    except OSError as exc:
        warnings.append(f"inventory_table_read_failed: {type(exc).__name__}: {exc}")

    return tim_paths, par_paths, warnings


def safe_read_text_lines(path: Path) -> tuple[list[str], str | None]:
    """Read text with replacement characters, never executing file contents."""
    try:
        with path.open("r", encoding="utf-8", errors="replace") as handle:
            return handle.read().splitlines(), None
    except OSError as exc:
        return [], f"{type(exc).__name__}: {exc}"


def is_comment_like(line: str) -> bool:
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


def delimiter_hint_for_line(line: str) -> str:
    stripped = line.strip()
    hints: set[str] = set()
    if "\t" in line:
        hints.add("tab")
    if "," in line:
        hints.add("comma")
    if len(stripped.split()) > 1:
        hints.add("whitespace")
    if not hints:
        return "unknown"
    if len(hints) == 1:
        return next(iter(hints))
    return "mixed"


def split_by_hint(line: str, delimiter_hint: str) -> list[str]:
    stripped = line.strip()
    if delimiter_hint == "tab":
        return [part for part in line.split("\t") if part.strip()]
    if delimiter_hint == "comma":
        return [part for part in line.split(",") if part.strip()]
    if delimiter_hint == "mixed":
        return [part for part in re.split(r"[\s,\t]+", stripped) if part]
    if delimiter_hint == "whitespace":
        return stripped.split()
    return [stripped] if stripped else []


def has_digit(text: str) -> bool:
    return any(char.isdigit() for char in text)


def has_alpha(text: str) -> bool:
    return any(char.isalpha() for char in text)


def classify_tim_line(line: str) -> str:
    """Classify a TIM line by structure only."""
    stripped = line.strip()
    if not stripped:
        return "blank"
    if is_comment_like(line):
        return "comment_like"

    tokens = stripped.split()
    if has_alpha(stripped) and not has_digit(stripped):
        return "header_like"
    if len(tokens) >= 2 and has_digit(stripped):
        return "data_like"
    if has_alpha(stripped) and len(tokens) >= 2:
        return "header_like"
    return "malformed_like"


def snippet(line: str) -> str:
    text = " ".join(line.strip().split())
    if len(text) <= SNIPPET_CHAR_LIMIT:
        return text
    return text[: SNIPPET_CHAR_LIMIT - 3] + "..."


def analyze_tim_file(relative_path: str, raw_input_root: Path) -> dict[str, Any]:
    """Collect TIM content-structure only, with no physical interpretation."""
    full_path = raw_input_root / relative_path
    lines, error = safe_read_text_lines(full_path)
    class_counts = Counter({line_class: 0 for line_class in TIM_ROW_CLASSES})
    delimiter_counts: Counter[str] = Counter()
    column_counts: Counter[int] = Counter()
    header_comment_rows: list[dict[str, Any]] = []

    if error is not None:
        return {
            "relative_path": relative_path,
            "error": error,
            "total_lines": 0,
            "class_counts": dict(class_counts),
            "delimiter_counts": {},
            "column_counts": {},
            "header_comment_rows": [],
        }

    for line_number, line in enumerate(lines, start=1):
        line_class = classify_tim_line(line)
        class_counts[line_class] += 1

        if line_class == "data_like":
            delimiter_hint = delimiter_hint_for_line(line)
            delimiter_counts[delimiter_hint] += 1
            column_counts[len(split_by_hint(line, delimiter_hint))] += 1
        elif line_class in {"comment_like", "header_like"}:
            if len(header_comment_rows) < MAX_SNIPPETS_PER_FILE:
                header_comment_rows.append(
                    {
                        "relative_path": relative_path,
                        "line_number": line_number,
                        "line_class": line_class,
                        "text_snippet": snippet(line),
                    }
                )

    return {
        "relative_path": relative_path,
        "error": None,
        "total_lines": len(lines),
        "class_counts": dict(class_counts),
        "delimiter_counts": dict(delimiter_counts),
        "column_counts": dict(column_counts),
        "header_comment_rows": header_comment_rows,
    }


def parse_parameter_parts(line: str) -> tuple[str | None, str, str]:
    """Extract parameter name and value string without value interpretation."""
    stripped = line.strip()
    if "=" in stripped:
        name, value = stripped.split("=", 1)
        return name.strip() or None, "equals", value.strip()
    if ":" in stripped:
        name, value = stripped.split(":", 1)
        return name.strip() or None, "colon", value.strip()

    parts = stripped.split(maxsplit=1)
    if len(parts) == 2:
        return parts[0].strip() or None, "whitespace", parts[1].strip()
    return None, "unknown", ""


def classify_par_line(line: str) -> str:
    """Classify a PAR line by structure only."""
    stripped = line.strip()
    if not stripped:
        return "blank"
    if is_comment_like(line):
        return "comment_like"
    name, _separator_type, _value = parse_parameter_parts(line)
    if name:
        return "key_value_like"
    return "malformed_like"


INTEGER_RE = re.compile(r"^[+-]?\d+$")
FLOAT_RE = re.compile(
    r"^[+-]?(?:(?:\d+\.\d*)|(?:\.\d+)|(?:\d+))(?:[eE][+-]?\d+)?$"
)
BOOL_VALUES = {"true", "false", "yes", "no", "on", "off"}


def value_format_class(value: str) -> str:
    """Classify value text shape only, not physical meaning."""
    stripped = value.strip()
    if not stripped:
        return "empty"
    lower = stripped.lower()
    if "," in stripped or stripped.startswith("[") or stripped.startswith("("):
        return "list_like"
    if lower in BOOL_VALUES:
        return "bool_like"
    if INTEGER_RE.match(stripped):
        return "integer_like"
    if FLOAT_RE.match(stripped):
        return "float_like"
    if len(stripped.split()) > 1:
        return "list_like"
    if stripped:
        return "string_like"
    return "mixed_or_unknown"


def parameter_prefix_group(parameter_name: str) -> str:
    if "_" in parameter_name:
        prefix = parameter_name.split("_", 1)[0]
        return prefix or "ungrouped"

    match = re.match(r"^[A-Za-z]+", parameter_name)
    if match:
        return match.group(0)
    return "ungrouped"


def analyze_par_file(relative_path: str, raw_input_root: Path) -> dict[str, Any]:
    """Collect PAR content-structure only, with no physical interpretation."""
    full_path = raw_input_root / relative_path
    lines, error = safe_read_text_lines(full_path)
    class_counts = Counter({line_class: 0 for line_class in PAR_ROW_CLASSES})
    parameters: dict[str, dict[str, Any]] = {}
    value_format_counts: Counter[str] = Counter()

    if error is not None:
        return {
            "relative_path": relative_path,
            "error": error,
            "total_lines": 0,
            "class_counts": dict(class_counts),
            "parameters": {},
            "prefix_counts": {},
            "value_format_counts": {},
        }

    for line in lines:
        line_class = classify_par_line(line)
        class_counts[line_class] += 1
        if line_class != "key_value_like":
            continue

        name, separator_type, value = parse_parameter_parts(line)
        if not name:
            continue

        format_class = value_format_class(value)
        value_format_counts[format_class] += 1
        if name not in parameters:
            parameters[name] = {
                "separator_types": Counter(),
                "value_format_classes": Counter(),
                "occurrence_count": 0,
            }
        parameters[name]["separator_types"][separator_type] += 1
        parameters[name]["value_format_classes"][format_class] += 1
        parameters[name]["occurrence_count"] += 1

    prefix_counts: Counter[str] = Counter()
    for name in parameters:
        prefix_counts[parameter_prefix_group(name)] += 1

    return {
        "relative_path": relative_path,
        "error": None,
        "total_lines": len(lines),
        "class_counts": dict(class_counts),
        "parameters": parameters,
        "prefix_counts": dict(prefix_counts),
        "value_format_counts": dict(value_format_counts),
    }


def dominant_counter_key(counter: Counter[str]) -> str:
    if not counter:
        return "unknown"
    return sorted(counter.items(), key=lambda item: (-item[1], item[0]))[0][0]


def build_tim_outputs(
    tim_results: list[dict[str, Any]],
    generated_at_utc: str,
    inventory_table: Path,
    raw_input_root: Path,
    output_root: Path,
) -> tuple[dict[str, Any], list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]]]:
    row_format_rows: list[dict[str, Any]] = []
    column_distribution_rows: list[dict[str, Any]] = []
    header_comment_rows: list[dict[str, Any]] = []
    delimiter_hints: Counter[str] = Counter()
    all_column_counts: list[int] = []
    total_lines = 0
    total_data_like = 0

    for result in tim_results:
        relative_path = result["relative_path"]
        total_lines += result["total_lines"]
        total_data_like += int(result["class_counts"].get("data_like", 0))

        for line_class in TIM_ROW_CLASSES:
            row_format_rows.append(
                {
                    "relative_path": relative_path,
                    "line_class": line_class,
                    "count": result["class_counts"].get(line_class, 0),
                }
            )

        for hint, count in result["delimiter_counts"].items():
            delimiter_hints[hint] += count

        for column_count_raw, row_count in result["column_counts"].items():
            column_count = int(column_count_raw)
            all_column_counts.append(column_count)
            column_distribution_rows.append(
                {
                    "relative_path": relative_path,
                    "apparent_column_count": column_count,
                    "row_count": row_count,
                }
            )

        header_comment_rows.extend(result["header_comment_rows"])

    summary = {
        "generated_at_utc": generated_at_utc,
        "input_inventory_table": inventory_table.as_posix(),
        "raw_input_root": raw_input_root.as_posix(),
        "output_root": output_root.as_posix(),
        "tim_files_found": len(tim_results),
        "total_tim_lines": total_lines,
        "total_tim_data_like_lines": total_data_like,
        "delimiter_hints": dict(sorted(delimiter_hints.items())),
        "column_count_min": min(all_column_counts) if all_column_counts else None,
        "column_count_max": max(all_column_counts) if all_column_counts else None,
        "claim_boundary": CLAIM_BOUNDARY,
    }
    return summary, row_format_rows, column_distribution_rows, header_comment_rows


def build_par_outputs(
    par_results: list[dict[str, Any]],
    generated_at_utc: str,
    inventory_table: Path,
    raw_input_root: Path,
    output_root: Path,
) -> tuple[dict[str, Any], list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]]]:
    parameter_rows: list[dict[str, Any]] = []
    prefix_rows: list[dict[str, Any]] = []
    value_format_rows: list[dict[str, Any]] = []
    total_lines = 0
    total_parameter_like = 0
    unique_names: set[tuple[str, str]] = set()
    duplicate_parameter_name_count = 0

    for result in par_results:
        relative_path = result["relative_path"]
        total_lines += result["total_lines"]
        total_parameter_like += int(result["class_counts"].get("key_value_like", 0))

        for name, info in sorted(result["parameters"].items()):
            occurrence_count = int(info["occurrence_count"])
            duplicate_flag = occurrence_count > 1
            if duplicate_flag:
                duplicate_parameter_name_count += 1
            unique_names.add((relative_path, name))
            parameter_rows.append(
                {
                    "relative_path": relative_path,
                    "parameter_name": name,
                    "separator_type": dominant_counter_key(info["separator_types"]),
                    "value_format_class": dominant_counter_key(info["value_format_classes"]),
                    "occurrence_count": occurrence_count,
                    "duplicate_flag": str(duplicate_flag).lower(),
                }
            )

        for prefix_group, parameter_count in sorted(result["prefix_counts"].items()):
            prefix_rows.append(
                {
                    "relative_path": relative_path,
                    "prefix_group": prefix_group,
                    "parameter_count": parameter_count,
                }
            )

        for format_class, count in sorted(result["value_format_counts"].items()):
            value_format_rows.append(
                {
                    "relative_path": relative_path,
                    "value_format_class": format_class,
                    "count": count,
                }
            )

    summary = {
        "generated_at_utc": generated_at_utc,
        "input_inventory_table": inventory_table.as_posix(),
        "raw_input_root": raw_input_root.as_posix(),
        "output_root": output_root.as_posix(),
        "par_files_found": len(par_results),
        "total_par_lines": total_lines,
        "total_parameter_like_lines": total_parameter_like,
        "unique_parameter_names": len(unique_names),
        "duplicate_parameter_name_count": duplicate_parameter_name_count,
        "claim_boundary": CLAIM_BOUNDARY,
    }
    return summary, parameter_rows, prefix_rows, value_format_rows


def write_json(path: Path, data: dict[str, Any]) -> None:
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def write_csv(path: Path, fieldnames: list[str], rows: list[dict[str, Any]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def build_readout(
    tim_summary: dict[str, Any],
    par_summary: dict[str, Any],
    warnings: list[str],
    tim_paths: list[str],
    par_paths: list[str],
) -> str:
    lines = [
        "# QSB-ST SHAPIROINFO53 TIM/PAR Content-Structure Review Readout",
        "",
        "## Purpose",
        "",
        "This readout reports controlled content-structure inspection only.",
        "",
        "## Files Reviewed",
        "",
        "TIM files:",
    ]
    lines.extend([f"- {path}" for path in tim_paths] or ["- none"])
    lines.append("")
    lines.append("PAR files:")
    lines.extend([f"- {path}" for path in par_paths] or ["- none"])

    lines.extend(
        [
            "",
            "## TIM Structure Summary",
            "",
            f"TIM files found: {tim_summary['tim_files_found']}",
            f"Total TIM lines: {tim_summary['total_tim_lines']}",
            f"Total TIM data-like lines: {tim_summary['total_tim_data_like_lines']}",
            f"Column count min: {tim_summary['column_count_min']}",
            f"Column count max: {tim_summary['column_count_max']}",
            f"Delimiter hints: {tim_summary['delimiter_hints']}",
            "",
            "## PAR Structure Summary",
            "",
            f"PAR files found: {par_summary['par_files_found']}",
            f"Total PAR lines: {par_summary['total_par_lines']}",
            f"Total parameter-like lines: {par_summary['total_parameter_like_lines']}",
            f"Unique parameter names: {par_summary['unique_parameter_names']}",
            f"Duplicate parameter name count: {par_summary['duplicate_parameter_name_count']}",
            "",
            "## Failures Or Limitations",
            "",
        ]
    )
    lines.extend([f"- {warning}" for warning in warnings] or ["- none"])
    lines.extend(
        [
            "",
            "## Claim Boundary",
            "",
            CLAIM_BOUNDARY,
            "",
            "This readout is content structure, not physical interpretation.",
            "It does not provide evidence for a physical Shapiro-information residual.",
            "It does not validate the QSB-ST Bridge.",
            "",
        ]
    )
    return "\n".join(lines)


def write_outputs(
    inventory_root: Path,
    raw_input_root: Path,
    output_root: Path,
    tim_paths: list[str],
    par_paths: list[str],
    warnings: list[str],
) -> None:
    output_root.mkdir(parents=True, exist_ok=True)
    inventory_table = inventory_root / INVENTORY_TABLE_NAME
    generated_at_utc = utc_now()

    tim_results = [analyze_tim_file(path, raw_input_root) for path in tim_paths]
    par_results = [analyze_par_file(path, raw_input_root) for path in par_paths]

    for result in tim_results + par_results:
        if result.get("error"):
            warnings.append(f"{result['relative_path']}: {result['error']}")

    (
        tim_summary,
        tim_row_format_rows,
        tim_column_distribution_rows,
        tim_header_comment_rows,
    ) = build_tim_outputs(
        tim_results, generated_at_utc, inventory_table, raw_input_root, output_root
    )
    (
        par_summary,
        par_parameter_rows,
        par_prefix_rows,
        par_value_format_rows,
    ) = build_par_outputs(
        par_results, generated_at_utc, inventory_table, raw_input_root, output_root
    )

    config = {
        "script": Path(__file__).as_posix(),
        "inventory_root": inventory_root.as_posix(),
        "raw_input_root": raw_input_root.as_posix(),
        "output_root": output_root.as_posix(),
        "execution_scope": "content_structure_only",
        "physical_value_interpretation": "forbidden",
        "residual_search": "forbidden",
        "model_fitting": "forbidden",
        "bridge_claim_gate": "closed",
        "output_files": OUTPUT_FILES,
        "claim_boundary": CLAIM_BOUNDARY,
    }

    write_json(output_root / "tim_content_structure_summary.json", tim_summary)
    write_csv(
        output_root / "tim_row_format_inventory.csv",
        ["relative_path", "line_class", "count"],
        tim_row_format_rows,
    )
    write_csv(
        output_root / "tim_column_count_distribution.csv",
        ["relative_path", "apparent_column_count", "row_count"],
        tim_column_distribution_rows,
    )
    write_csv(
        output_root / "tim_header_comment_inventory.csv",
        ["relative_path", "line_number", "line_class", "text_snippet"],
        tim_header_comment_rows,
    )
    write_json(output_root / "par_content_structure_summary.json", par_summary)
    write_csv(
        output_root / "par_parameter_name_inventory.csv",
        [
            "relative_path",
            "parameter_name",
            "separator_type",
            "value_format_class",
            "occurrence_count",
            "duplicate_flag",
        ],
        par_parameter_rows,
    )
    write_csv(
        output_root / "par_parameter_prefix_groups.csv",
        ["relative_path", "prefix_group", "parameter_count"],
        par_prefix_rows,
    )
    write_csv(
        output_root / "par_value_format_classes.csv",
        ["relative_path", "value_format_class", "count"],
        par_value_format_rows,
    )
    readout = build_readout(tim_summary, par_summary, warnings, tim_paths, par_paths)
    (output_root / "tim_par_content_structure_review_readout.md").write_text(
        readout, encoding="utf-8"
    )
    write_json(output_root / "content_structure_review_config_resolved.json", config)


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Review TIM/PAR content structure only. No physical interpretation, "
            "residual search, model fitting, anomaly claims, or Bridge "
            "confirmation is performed."
        )
    )
    parser.add_argument(
        "--inventory-root",
        default=DEFAULT_INVENTORY_ROOT.as_posix(),
        help="Inventory output root containing raw_structure_inventory_table.csv.",
    )
    parser.add_argument(
        "--raw-input-root",
        default=DEFAULT_RAW_INPUT_ROOT.as_posix(),
        help="Read-only local raw artifact root.",
    )
    parser.add_argument(
        "--output-root",
        default=DEFAULT_OUTPUT_ROOT.as_posix(),
        help="Output root for content-structure review run artifacts.",
    )
    return parser


def main() -> int:
    parser = build_arg_parser()
    args = parser.parse_args()

    inventory_root = Path(args.inventory_root)
    raw_input_root = Path(args.raw_input_root)
    output_root = Path(args.output_root)
    inventory_table = inventory_root / INVENTORY_TABLE_NAME

    tim_paths, par_paths, warnings = read_inventory_targets(inventory_table)
    write_outputs(inventory_root, raw_input_root, output_root, tim_paths, par_paths, warnings)
    print(f"wrote content-structure outputs under: {output_root}")
    print(CLAIM_BOUNDARY)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
