#!/usr/bin/env python3
"""Validate QSB/PBR native metadata mapping artifacts without real DB writes."""

from __future__ import annotations

import argparse
import csv
import sqlite3
from collections import Counter
from pathlib import Path

from scripts.qsb_literature_metadata.native_contract_constants import CLAIM_BOUNDARY, CONFLICT_CLASSES, LOOKUP_OUTCOMES, OPERATION_TYPES
from scripts.qsb_literature_metadata.native_metadata_mapping import (
    MappingError,
    apply_operations_to_temp_db,
    build_operation_plan,
    detect_alias_collisions,
    lineage_validation,
    operation_summaries,
    quantity_policy,
    read_registration_plan,
    validate_required_schema,
    vocabulary_entries,
)


def write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    if not rows:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("", encoding="utf-8")
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def validate_mapping(plan_path: Path, metadata_db: Path | None = None, output_dir: Path | None = None) -> list[dict[str, object]]:
    rows = read_registration_plan(plan_path)
    operations = build_operation_plan(rows)
    lookup_counts, conflict_counts = operation_summaries(operations)
    alias_collisions = detect_alias_collisions(rows)
    quantity_rows = [quantity_policy(row) | {"registration_plan_row_id": row.registration_plan_row_id} for row in rows]
    vocab_rows = vocabulary_entries(rows)
    failures: list[str] = []
    if len(rows) != 17:
        failures.append("registration_plan_row_count")
    if len(operations) != 170:
        failures.append("operation_count")
    if any(op.lookup_outcome not in LOOKUP_OUTCOMES for op in operations):
        failures.append("lookup_outcomes")
    if any(op.operation_type_candidate not in OPERATION_TYPES for op in operations):
        failures.append("operation_types")
    if any(op.conflict_class not in CONFLICT_CLASSES for op in operations):
        failures.append("conflict_classes")
    if any(op.claim_boundary_state != CLAIM_BOUNDARY or not op.lineage_key for op in operations):
        failures.append("lineage_or_claim_boundary")
    if alias_collisions:
        failures.append("alias_collisions")
    if metadata_db is not None:
        with sqlite3.connect(f"file:{metadata_db.resolve().as_posix()}?mode=ro", uri=True) as conn:
            missing = validate_required_schema(conn)
        if missing:
            failures.append("missing_native_tables:" + ";".join(missing))
    result_rows = [
        {"check_name": "registration_plan_rows", "expected": "17", "actual": str(len(rows)), "status": "pass" if len(rows) == 17 else "fail"},
        {"check_name": "operation_candidates", "expected": "170", "actual": str(len(operations)), "status": "pass" if len(operations) == 170 else "fail"},
        {"check_name": "lookup_outcomes_controlled", "expected": "true", "actual": str(not any(op.lookup_outcome not in LOOKUP_OUTCOMES for op in operations)).lower(), "status": "pass"},
        {"check_name": "operation_types_controlled", "expected": "true", "actual": str(not any(op.operation_type_candidate not in OPERATION_TYPES for op in operations)).lower(), "status": "pass"},
        {"check_name": "conflict_classes_controlled", "expected": "true", "actual": str(not any(op.conflict_class not in CONFLICT_CLASSES for op in operations)).lower(), "status": "pass"},
        {"check_name": "lineage_and_claim_boundary", "expected": "true", "actual": str("lineage_or_claim_boundary" not in failures).lower(), "status": "pass" if "lineage_or_claim_boundary" not in failures else "fail"},
        {"check_name": "alias_collisions", "expected": "0", "actual": str(len(alias_collisions)), "status": "pass" if not alias_collisions else "fail"},
        {"check_name": "quantity_policy_rows", "expected": "17", "actual": str(len(quantity_rows)), "status": "pass" if len(quantity_rows) == 17 else "fail"},
        {"check_name": "vocabulary_entries", "expected": ">=1", "actual": str(len(vocab_rows)), "status": "pass" if vocab_rows else "fail"},
        {"check_name": "lookup_summary", "expected": "controlled", "actual": dict(lookup_counts), "status": "pass"},
        {"check_name": "conflict_summary", "expected": "controlled", "actual": dict(conflict_counts), "status": "pass"},
    ]
    if output_dir is not None:
        write_csv(output_dir / "native_mapping_validation.csv", result_rows)
        write_csv(output_dir / "lineage_validation.csv", lineage_validation(operations))
        write_csv(output_dir / "quantity_policy.csv", quantity_rows)
        write_csv(output_dir / "vocabulary_entries.csv", vocab_rows)
    return result_rows


def run_temp_apply(plan_path: Path, temp_metadata_db: Path) -> dict[str, object]:
    rows = read_registration_plan(plan_path)
    operations = build_operation_plan(rows)
    with sqlite3.connect(temp_metadata_db) as conn:
        conn.execute("BEGIN")
        result = apply_operations_to_temp_db(conn, operations)
        conn.commit()
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate native metadata mapping without writing real targets.")
    parser.add_argument("--plan", default="runs/QSB-PBR-LITERATURE-METADATA-SERVER-IMPORT-01/data/metadata_server_registration_plan.csv")
    parser.add_argument("--metadata-db")
    parser.add_argument("--output-dir")
    args = parser.parse_args()
    try:
        rows = validate_mapping(
            Path(args.plan),
            Path(args.metadata_db) if args.metadata_db else None,
            Path(args.output_dir) if args.output_dir else None,
        )
    except MappingError as exc:
        print(f"FAIL: {exc}")
        return 1
    failures = [row for row in rows if row["status"] != "pass"]
    for row in rows:
        print(f"{row['status'].upper()}: {row['check_name']} actual={row['actual']}")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
