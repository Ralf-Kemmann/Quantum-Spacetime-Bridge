#!/usr/bin/env python3
"""
BMS-FU02g4d — Coverage and Log Audit for FU02g4c chunk outputs.

This script parses FU02g4c chunk/segment log files, extracts JSON objects,
merges manifest and summary dictionaries, classifies logs, audits coverage,
and writes CSV/JSON/Markdown outputs.

Default project-root usage:

    cd ~/Downloads/deBroglie_Kaster_Theorie/quantum-spacetime-bridge
    python scripts/aggregate_bms_fu02g4c_chunk_outputs.py

Optional:

    python scripts/aggregate_bms_fu02g4c_chunk_outputs.py \
      --log-dir runs/BMS-FU02g4c/chunk_batch_logs \
      --log-dir runs/BMS-FU02g4c/chunk_batch_logs_gap_safe \
      --out-dir runs/BMS-FU02g4d/coverage_and_log_audit

Design notes:
- JSON extraction is brace-balanced and tolerant of mixed text logs.
- Manifest and summary JSON objects are merged in file order; later keys win.
- warnings_count is preserved if present only in an earlier manifest object.
- Raw counts are summed only for logs included in the primary contiguous chain.
- Orbit-class counts are not claimed as global unique classes by naive summation.
"""

from __future__ import annotations

import argparse
import csv
import json
import re
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Tuple

COUNT_FIELDS = [
    "raw_connected_patch_count_processed",
    "unique_orbit_patch_count_processed",
    "raw_carrier_signature_exact_match_count",
    "raw_carrier_signature_near_match_count",
    "raw_role_colored_signature_exact_match_count",
    "raw_role_colored_signature_near_match_count",
    "orbit_carrier_signature_exact_match_class_count",
    "orbit_carrier_signature_near_match_class_count",
    "orbit_role_colored_signature_exact_match_class_count",
    "orbit_role_colored_signature_near_match_class_count",
]

RAW_AGGREGATE_FIELDS = [
    "raw_connected_patch_count_processed",
    "raw_carrier_signature_exact_match_count",
    "raw_carrier_signature_near_match_count",
    "raw_role_colored_signature_exact_match_count",
    "raw_role_colored_signature_near_match_count",
]

SEGMENT_LOCAL_ORBIT_FIELDS = [
    "orbit_carrier_signature_exact_match_class_count",
    "orbit_carrier_signature_near_match_class_count",
    "orbit_role_colored_signature_exact_match_class_count",
    "orbit_role_colored_signature_near_match_class_count",
]

AUDIT_FIELDS = [
    "source_log_path",
    "log_size_bytes",
    "json_object_count",
    "chunk_id",
    "classification",
    "classification_reason",
    "enumeration_status",
    "warnings_count",
    "orbit_reduction_enabled_actual",
    "automorphism_count_used",
    "reference_is_connected",
    "skip_first_raw_patches",
    "raw_patch_count_seen_including_skipped",
    "next_skip",
    "interval_start",
    "interval_end_exclusive",
    "raw_connected_patch_count_processed",
    "interval_count_check",
    "interval_count_matches",
    "unique_orbit_patch_count_processed",
    "raw_carrier_signature_exact_match_count",
    "raw_carrier_signature_near_match_count",
    "raw_role_colored_signature_exact_match_count",
    "raw_role_colored_signature_near_match_count",
    "orbit_carrier_signature_exact_match_class_count",
    "orbit_carrier_signature_near_match_class_count",
    "orbit_role_colored_signature_exact_match_class_count",
    "orbit_role_colored_signature_near_match_class_count",
    "include_in_primary_counts",
]


def int_or_none(value: Any) -> Optional[int]:
    if value is None or value == "":
        return None
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def bool_or_none(value: Any) -> Optional[bool]:
    if isinstance(value, bool):
        return value
    if value is None:
        return None
    if isinstance(value, str):
        v = value.strip().lower()
        if v in {"true", "1", "yes", "y"}:
            return True
        if v in {"false", "0", "no", "n"}:
            return False
    return None


def extract_balanced_json_objects(text: str) -> List[Dict[str, Any]]:
    """Extract top-level JSON objects from arbitrary log text."""
    objects: List[Dict[str, Any]] = []
    start: Optional[int] = None
    depth = 0
    in_string = False
    escape = False

    for i, ch in enumerate(text):
        if start is None:
            if ch == "{":
                start = i
                depth = 1
                in_string = False
                escape = False
            continue

        if in_string:
            if escape:
                escape = False
            elif ch == "\\":
                escape = True
            elif ch == '"':
                in_string = False
            continue

        if ch == '"':
            in_string = True
        elif ch == "{":
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0 and start is not None:
                candidate = text[start : i + 1]
                try:
                    parsed = json.loads(candidate)
                    if isinstance(parsed, dict):
                        objects.append(parsed)
                except json.JSONDecodeError:
                    pass
                start = None

    return objects


def merge_json_objects(objs: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Merge JSON objects while preserving warnings_count from earlier manifest when later summary omits it."""
    merged: Dict[str, Any] = {}
    for obj in objs:
        for key, value in obj.items():
            if key == "warnings_count" and value is not None:
                merged[key] = value
            elif key not in merged or value is not None:
                merged[key] = value
    return merged


def infer_chunk_id_from_filename(path: Path) -> str:
    name = path.name
    if name.endswith(".log"):
        return name[:-4]
    return name


@dataclass
class AuditRecord:
    source_log_path: str
    log_size_bytes: int
    json_object_count: int
    chunk_id: Optional[str]
    classification: str
    classification_reason: str
    enumeration_status: Optional[str]
    warnings_count: Optional[int]
    orbit_reduction_enabled_actual: Optional[bool]
    automorphism_count_used: Optional[int]
    reference_is_connected: Optional[bool]
    skip_first_raw_patches: Optional[int]
    raw_patch_count_seen_including_skipped: Optional[int]
    next_skip: Optional[int]
    interval_start: Optional[int]
    interval_end_exclusive: Optional[int]
    raw_connected_patch_count_processed: Optional[int]
    interval_count_check: Optional[int]
    interval_count_matches: Optional[bool]
    unique_orbit_patch_count_processed: Optional[int]
    raw_carrier_signature_exact_match_count: int
    raw_carrier_signature_near_match_count: int
    raw_role_colored_signature_exact_match_count: int
    raw_role_colored_signature_near_match_count: int
    orbit_carrier_signature_exact_match_class_count: int
    orbit_carrier_signature_near_match_class_count: int
    orbit_role_colored_signature_exact_match_class_count: int
    orbit_role_colored_signature_near_match_class_count: int
    include_in_primary_counts: bool


def classify_initial(record: AuditRecord) -> Tuple[str, str]:
    if record.log_size_bytes == 0:
        return "empty_or_aborted", "zero-byte log; no JSON output; excluded from counts"

    if record.json_object_count == 0:
        return "invalid_no_json", "non-empty log but no parseable JSON object found"

    if record.warnings_count is not None and record.warnings_count != 0:
        return "invalid_warning", f"warnings_count={record.warnings_count}; excluded from primary counts"

    if record.reference_is_connected is not True:
        return "invalid_reference", "reference_is_connected is not true"

    if record.orbit_reduction_enabled_actual is not True:
        return "raw_only_invalid_orbit", "orbit reduction was not actually enabled"

    if record.automorphism_count_used != 120:
        return "invalid_automorphism_count", f"automorphism_count_used={record.automorphism_count_used}; expected 120"

    processed = record.raw_connected_patch_count_processed
    if processed is None:
        return "invalid_missing_processed_count", "raw_connected_patch_count_processed missing"

    if processed == 0:
        if record.enumeration_status == "partial_timeout_reached":
            return "zero_progress_timeout", "valid environment but zero processed patches during timeout; excluded from counts"
        return "zero_progress", "valid environment but zero processed patches; excluded from counts"

    if record.interval_count_matches is False:
        return "invalid_interval_mismatch", "processed count does not match computed half-open coverage interval"

    return "candidate_valid", "valid environment and positive processed count; pending coverage-chain classification"


def make_record(path: Path, project_root: Path) -> AuditRecord:
    size = path.stat().st_size
    text = path.read_text(errors="replace") if size > 0 else ""
    objs = extract_balanced_json_objects(text) if text else []
    merged = merge_json_objects(objs)

    chunk_id = merged.get("chunk_id") or infer_chunk_id_from_filename(path)
    warnings_count = int_or_none(merged.get("warnings_count"))
    orbit_enabled = bool_or_none(merged.get("orbit_reduction_enabled_actual"))
    automorphism_count = int_or_none(merged.get("automorphism_count_used"))
    reference_connected = bool_or_none(merged.get("reference_is_connected"))
    skip = int_or_none(merged.get("skip_first_raw_patches"))
    seen = int_or_none(merged.get("raw_patch_count_seen_including_skipped"))
    processed = int_or_none(merged.get("raw_connected_patch_count_processed"))
    unique_orbit = int_or_none(merged.get("unique_orbit_patch_count_processed"))

    next_skip = seen - 1 if seen is not None else None
    interval_start = skip
    interval_end = next_skip
    interval_count_check = None
    interval_count_matches = None
    if interval_start is not None and interval_end is not None:
        interval_count_check = interval_end - interval_start
        if processed is not None:
            interval_count_matches = interval_count_check == processed

    def count_field(name: str) -> int:
        return int_or_none(merged.get(name)) or 0

    try:
        rel_path = str(path.relative_to(project_root))
    except ValueError:
        rel_path = str(path)

    rec = AuditRecord(
        source_log_path=rel_path,
        log_size_bytes=size,
        json_object_count=len(objs),
        chunk_id=str(chunk_id) if chunk_id is not None else None,
        classification="unclassified",
        classification_reason="",
        enumeration_status=merged.get("enumeration_status"),
        warnings_count=warnings_count,
        orbit_reduction_enabled_actual=orbit_enabled,
        automorphism_count_used=automorphism_count,
        reference_is_connected=reference_connected,
        skip_first_raw_patches=skip,
        raw_patch_count_seen_including_skipped=seen,
        next_skip=next_skip,
        interval_start=interval_start,
        interval_end_exclusive=interval_end,
        raw_connected_patch_count_processed=processed,
        interval_count_check=interval_count_check,
        interval_count_matches=interval_count_matches,
        unique_orbit_patch_count_processed=unique_orbit,
        raw_carrier_signature_exact_match_count=count_field("raw_carrier_signature_exact_match_count"),
        raw_carrier_signature_near_match_count=count_field("raw_carrier_signature_near_match_count"),
        raw_role_colored_signature_exact_match_count=count_field("raw_role_colored_signature_exact_match_count"),
        raw_role_colored_signature_near_match_count=count_field("raw_role_colored_signature_near_match_count"),
        orbit_carrier_signature_exact_match_class_count=count_field("orbit_carrier_signature_exact_match_class_count"),
        orbit_carrier_signature_near_match_class_count=count_field("orbit_carrier_signature_near_match_class_count"),
        orbit_role_colored_signature_exact_match_class_count=count_field("orbit_role_colored_signature_exact_match_class_count"),
        orbit_role_colored_signature_near_match_class_count=count_field("orbit_role_colored_signature_near_match_class_count"),
        include_in_primary_counts=False,
    )
    rec.classification, rec.classification_reason = classify_initial(rec)
    return rec


def discover_logs(log_dirs: Iterable[Path]) -> List[Path]:
    found: List[Path] = []
    for d in log_dirs:
        if not d.exists():
            continue
        found.extend(sorted(d.glob("*.log")))
    # Stable unique paths.
    unique = sorted({p.resolve(): p for p in found}.values(), key=lambda p: str(p))
    return unique


def classify_coverage_chain(records: List[AuditRecord]) -> Tuple[List[AuditRecord], List[Dict[str, Any]]]:
    """Mark a primary contiguous chain and record gaps/overlaps among candidate logs."""
    candidates = [
        r for r in records
        if r.classification == "candidate_valid"
        and r.interval_start is not None
        and r.interval_end_exclusive is not None
    ]
    candidates.sort(key=lambda r: (r.interval_start or -1, r.interval_end_exclusive or -1, r.source_log_path))

    gaps: List[Dict[str, Any]] = []
    current_end: Optional[int] = None

    for rec in candidates:
        start = rec.interval_start
        end = rec.interval_end_exclusive
        assert start is not None and end is not None

        if current_end is None:
            rec.classification = "primary_valid"
            rec.classification_reason = "first valid interval in primary audited chain"
            rec.include_in_primary_counts = True
            current_end = end
            continue

        if start == current_end:
            rec.classification = "primary_valid"
            rec.classification_reason = "contiguous with previous accepted primary interval"
            rec.include_in_primary_counts = True
            current_end = max(current_end, end)
        elif start < current_end:
            # Accept extension if it starts before current_end and extends beyond it? Safer to mark secondary.
            rec.classification = "secondary_overlap"
            rec.classification_reason = f"interval starts at {start}, before current primary end {current_end}; excluded from primary counts"
            rec.include_in_primary_counts = False
            if end > current_end:
                gaps.append({
                    "type": "overlap_with_extension_excluded_for_manual_review",
                    "previous_primary_end": current_end,
                    "overlap_start": start,
                    "overlap_end": min(end, current_end),
                    "extension_end": end,
                    "source_log_path": rec.source_log_path,
                })
        else:
            gap = {
                "type": "coverage_gap",
                "gap_start": current_end,
                "gap_end": start,
                "gap_size": start - current_end,
                "next_log": rec.source_log_path,
            }
            gaps.append(gap)
            rec.classification = "secondary_gap_after_break"
            rec.classification_reason = f"coverage gap detected: previous primary end {current_end}, next start {start}; excluded from primary chain"
            rec.include_in_primary_counts = False
            # Do not advance current_end; primary chain remains the first contiguous chain.

    # Any remaining candidate_valid without interval was already excluded by filtering, but keep safe.
    for rec in records:
        if rec.classification == "candidate_valid":
            rec.classification = "secondary_not_in_primary_chain"
            rec.classification_reason = "valid candidate not included in primary contiguous chain"
            rec.include_in_primary_counts = False

    return records, gaps


def write_csv(path: Path, rows: List[Dict[str, Any]], fieldnames: List[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def aggregate_primary(records: List[AuditRecord]) -> Dict[str, Any]:
    primary = [r for r in records if r.include_in_primary_counts]
    aggregate: Dict[str, Any] = {
        "primary_log_count": len(primary),
        "primary_interval_start": min((r.interval_start for r in primary if r.interval_start is not None), default=None),
        "primary_interval_end_exclusive": max((r.interval_end_exclusive for r in primary if r.interval_end_exclusive is not None), default=None),
        "claim_boundary": "Raw counts are summed over primary_valid logs only. Orbit-class counts remain segment-local and are not global unique class counts.",
    }

    for field in RAW_AGGREGATE_FIELDS:
        aggregate[field] = sum(getattr(r, field) or 0 for r in primary)

    aggregate["segment_local_orbit_presence"] = {}
    for field in SEGMENT_LOCAL_ORBIT_FIELDS:
        vals = [getattr(r, field) or 0 for r in primary]
        aggregate["segment_local_orbit_presence"][field] = {
            "segment_sum_not_global_unique": sum(vals),
            "segment_max": max(vals) if vals else 0,
            "segments_with_positive_value": sum(1 for v in vals if v > 0),
        }

    return aggregate


def make_result_note(records: List[AuditRecord], gaps: List[Dict[str, Any]], aggregate: Dict[str, Any]) -> str:
    total_logs = len(records)
    by_class: Dict[str, int] = {}
    for r in records:
        by_class[r.classification] = by_class.get(r.classification, 0) + 1

    lines: List[str] = []
    lines.append("# BMS-FU02g4d — Coverage and Log Audit Result Note")
    lines.append("")
    lines.append("## Purpose")
    lines.append("")
    lines.append("This note audits FU02g4c chunk/segment logs before any further interpretation or continuation. It classifies logs, checks coverage continuity, and aggregates only primary valid raw counts.")
    lines.append("")
    lines.append("## Audit Summary")
    lines.append("")
    lines.append(f"- Total log files inspected: `{total_logs}`")
    for cls in sorted(by_class):
        lines.append(f"- `{cls}`: `{by_class[cls]}`")
    lines.append("")
    lines.append("## Primary Coverage")
    lines.append("")
    lines.append(f"- Primary log count: `{aggregate.get('primary_log_count')}`")
    lines.append(f"- Primary interval start: `{aggregate.get('primary_interval_start')}`")
    lines.append(f"- Primary interval end exclusive / next resume marker: `{aggregate.get('primary_interval_end_exclusive')}`")
    lines.append("")
    lines.append("## Primary Raw Aggregate Counts")
    lines.append("")
    for field in RAW_AGGREGATE_FIELDS:
        lines.append(f"- `{field}`: `{aggregate.get(field, 0)}`")
    lines.append("")
    lines.append("## Coverage Gaps / Overlaps")
    lines.append("")
    if gaps:
        for gap in gaps[:50]:
            lines.append(f"- `{gap}`")
        if len(gaps) > 50:
            lines.append(f"- ... plus `{len(gaps) - 50}` additional gap/overlap records in `coverage_gaps_primary.csv`.")
    else:
        lines.append("- No gaps detected within the accepted primary contiguous chain.")
    lines.append("")
    lines.append("## Orbit-Class Count Boundary")
    lines.append("")
    lines.append("Per-segment orbit-class counts are reported in the audit table, but they are not treated as globally unique orbit classes. A separate global canonical-hash aggregation would be required for that claim.")
    lines.append("")
    lines.append("## Befund")
    lines.append("")
    lines.append("The audit separates valid primary FU02g4c outputs from raw-only, interrupted, zero-progress, warning-bearing, overlapping, or gap-separated logs. Primary raw counts are aggregated only over logs passing the explicit validity and coverage-chain criteria.")
    lines.append("")
    lines.append("## Interpretation")
    lines.append("")
    lines.append("The current FU02g4c continuation remains methodologically useful as bounded, audited evidence. However, the high-skip regime makes further skip-based continuation inefficient because repeated fast-forwarding dominates runtime.")
    lines.append("")
    lines.append("## Hypothese")
    lines.append("")
    lines.append("The role-colored signature appears rarer than the uncolored carrier footprint under the current assignment definition, but this remains assignment-dependent and requires sensitivity tests and external graph-family controls.")
    lines.append("")
    lines.append("## Offene Lücke")
    lines.append("")
    lines.append("A checkpoint-capable or frontier-state enumerator would be needed for efficient exhaustive continuation. Role-assignment sensitivity and external fullerene/isomer controls remain open.")
    lines.append("")
    lines.append("## Claim Boundary")
    lines.append("")
    lines.append("This audit does not prove exhaustive absence of role-colored matches. It does not turn segment-local orbit counts into global unique orbit-class counts. It documents bounded, validated coverage and prepares the next controls.")
    lines.append("")
    lines.append("## Suggested Next Blocks")
    lines.append("")
    lines.append("- `BMS-FU02g5 — Role-Assignment Sensitivity Controls`")
    lines.append("- `BMS-FU03a — External C60 Fullerene-Isomer Controls`")
    lines.append("- Optional later: checkpoint-capable connected-patch enumerator")
    lines.append("")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description="Audit FU02g4c chunk output logs for BMS-FU02g4d.")
    parser.add_argument("--project-root", default=".", help="Project root directory. Default: current directory.")
    parser.add_argument(
        "--log-dir",
        action="append",
        default=None,
        help="Log directory to inspect. Can be passed multiple times. Defaults to FU02g4c chunk log folders.",
    )
    parser.add_argument(
        "--out-dir",
        default="runs/BMS-FU02g4d/coverage_and_log_audit",
        help="Output directory for audit artifacts.",
    )
    args = parser.parse_args()

    project_root = Path(args.project_root).resolve()
    if args.log_dir:
        log_dirs = [project_root / d for d in args.log_dir]
    else:
        log_dirs = [
            project_root / "runs/BMS-FU02g4c/chunk_batch_logs",
            project_root / "runs/BMS-FU02g4c/chunk_batch_logs_gap_safe",
        ]
    out_dir = project_root / args.out_dir
    out_dir.mkdir(parents=True, exist_ok=True)

    logs = discover_logs(log_dirs)
    records = [make_record(path, project_root) for path in logs]
    records, gaps = classify_coverage_chain(records)
    aggregate = aggregate_primary(records)

    record_rows = [asdict(r) for r in records]
    write_csv(out_dir / "chunk_log_audit.csv", record_rows, AUDIT_FIELDS)
    (out_dir / "chunk_log_audit.json").write_text(json.dumps(record_rows, indent=2, sort_keys=True))

    primary_rows = [asdict(r) for r in records if r.include_in_primary_counts]
    coverage_fields = [
        "source_log_path",
        "chunk_id",
        "interval_start",
        "interval_end_exclusive",
        "raw_connected_patch_count_processed",
        "enumeration_status",
    ]
    write_csv(out_dir / "coverage_intervals_primary.csv", primary_rows, coverage_fields)

    gap_fields = sorted({k for g in gaps for k in g.keys()}) if gaps else ["type", "gap_start", "gap_end", "gap_size", "next_log"]
    write_csv(out_dir / "coverage_gaps_primary.csv", gaps, gap_fields)

    (out_dir / "aggregate_counts_primary.json").write_text(json.dumps(aggregate, indent=2, sort_keys=True))
    note = make_result_note(records, gaps, aggregate)
    (out_dir / "BMS_FU02G4D_COVERAGE_AND_LOG_AUDIT_RESULT_NOTE.md").write_text(note)

    print("BMS-FU02g4d audit complete")
    print(f"logs_inspected={len(records)}")
    print(f"primary_log_count={aggregate.get('primary_log_count')}")
    print(f"primary_interval_start={aggregate.get('primary_interval_start')}")
    print(f"primary_interval_end_exclusive={aggregate.get('primary_interval_end_exclusive')}")
    print(f"out_dir={out_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
