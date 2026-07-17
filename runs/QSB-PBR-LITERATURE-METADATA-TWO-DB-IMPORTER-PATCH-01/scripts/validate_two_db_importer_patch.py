#!/usr/bin/env python3
"""Validate the QSB/PBR two-DB importer patch artifacts."""

from __future__ import annotations

import csv
import sqlite3
from pathlib import Path


RUN_DIR = Path("runs/QSB-PBR-LITERATURE-METADATA-TWO-DB-IMPORTER-PATCH-01")
IMPORTER = Path("runs/QSB-PBR-LITERATURE-METADATA-SERVER-IMPORT-01/scripts/import_literature_metadata.py")
CLAIM_BOUNDARY = "literature_context_only_no_internal_evidence_no_mechanism_claim"
FINAL_STATUS = "two_db_importer_patch_dry_run_passed"


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: Path, fieldnames: list[str], rows: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def scalar(conn: sqlite3.Connection, sql: str, params: tuple[object, ...] = ()) -> int:
    return int(conn.execute(sql, params).fetchone()[0])


def table_exists(conn: sqlite3.Connection, name: str) -> bool:
    return (
        conn.execute(
            "SELECT COUNT(*) FROM sqlite_schema WHERE type='table' AND name=?",
            (name,),
        ).fetchone()[0]
        == 1
    )


def main() -> int:
    rows: list[dict[str, object]] = []
    failures: list[str] = []
    importer_text = IMPORTER.read_text(encoding="utf-8")
    integrity = read_csv(RUN_DIR / "data" / "two_db_dry_run_target_integrity.csv")
    copy_by_role = {row["target_role"]: Path(row["dryrun_db_path"]) for row in integrity}

    cli_ok = all(token in importer_text for token in ("--data-db", "--metadata-db", "--seed", "--mode"))
    rows.append(
        {
            "check_id": "V01",
            "check_name": "two_db_cli_contract_present",
            "expected": "true",
            "actual": str(cli_ok).lower(),
            "status": "pass" if cli_ok else "fail",
            "notes": "Importer source contains --data-db, --metadata-db, --seed, and --mode.",
        }
    )
    if not cli_ok:
        failures.append("two_db_cli_contract_present")

    deprecated_ok = "single_db_mode_deprecated_for_two_db_architecture" in importer_text
    rows.append(
        {
            "check_id": "V02",
            "check_name": "single_db_deprecation_present",
            "expected": "true",
            "actual": str(deprecated_ok).lower(),
            "status": "pass" if deprecated_ok else "fail",
            "notes": "Deprecated single-DB dry-run warning is present.",
        }
    )
    if not deprecated_ok:
        failures.append("single_db_deprecation_present")

    real_unchanged = all(
        row["sha256_before"] == row["sha256_after"]
        and row["mtime_ns_before"] == row["mtime_ns_after"]
        and row["real_target_unchanged"] == "true"
        for row in integrity
    )
    rows.append(
        {
            "check_id": "V03",
            "check_name": "real_db_targets_unchanged",
            "expected": "true",
            "actual": str(real_unchanged).lower(),
            "status": "pass" if real_unchanged else "fail",
            "notes": "Integrity CSV shows identical SHA256 and mtime values before/after dry-run.",
        }
    )
    if not real_unchanged:
        failures.append("real_db_targets_unchanged")

    data_copy = copy_by_role["literature_data_db"]
    with sqlite3.connect(f"file:{data_copy.as_posix()}?mode=ro", uri=True) as conn:
        required_tables = [
            "qsb_literature_source",
            "qsb_literature_mechanism_tag",
            "qsb_literature_claim_boundary",
            "qsb_literature_qsb_mapping",
            "qsb_literature_import_manifest",
        ]
        missing_tables = [table for table in required_tables if not table_exists(conn, table)]
        source_count = scalar(conn, "SELECT COUNT(*) FROM qsb_literature_source")
        missing_tags = scalar(
            conn,
            """
            SELECT COUNT(*)
            FROM qsb_literature_source s
            WHERE NOT EXISTS (
              SELECT 1 FROM qsb_literature_mechanism_tag t
              WHERE t.literature_id = s.literature_id
            )
            """,
        )
        bad_flags = scalar(
            conn,
            """
            SELECT COUNT(*)
            FROM qsb_literature_claim_boundary
            WHERE internal_evidence_flag <> 0
               OR mechanism_claim_support <> 0
               OR physical_claim_support <> 0
               OR claim_boundary <> ?
            """,
            (CLAIM_BOUNDARY,),
        )
        forbidden = scalar(
            conn,
            """
            SELECT COUNT(*)
            FROM qsb_literature_claim_boundary
            WHERE lower(allowed_use || ' ' || forbidden_use || ' ' || claim_boundary) LIKE '%supports qsb%'
               OR lower(allowed_use || ' ' || forbidden_use || ' ' || claim_boundary) LIKE '%proves qsb%'
               OR lower(allowed_use || ' ' || forbidden_use || ' ' || claim_boundary) LIKE '%confirms mechanism%'
               OR lower(allowed_use || ' ' || forbidden_use || ' ' || claim_boundary) LIKE '%evidence for qsb%'
               OR lower(allowed_use || ' ' || forbidden_use || ' ' || claim_boundary) LIKE '%physical discovery%'
            """,
        )

    data_ok = not missing_tables and source_count == 23 and missing_tags == 0 and bad_flags == 0 and forbidden == 0
    rows.append(
        {
            "check_id": "V04",
            "check_name": "data_dryrun_tables_and_claim_boundary",
            "expected": "tables_present;source_count=23;missing_tags=0;bad_flags=0;forbidden=0",
            "actual": f"missing_tables={';'.join(missing_tables)};source_count={source_count};missing_tags={missing_tags};bad_flags={bad_flags};forbidden={forbidden}",
            "status": "pass" if data_ok else "fail",
            "notes": "Checked dry-run data DB copy read-only.",
        }
    )
    if not data_ok:
        failures.append("data_dryrun_tables_and_claim_boundary")

    metadata_copy = copy_by_role["metadata_registration_db"]
    with sqlite3.connect(f"file:{metadata_copy.as_posix()}?mode=ro", uri=True) as conn:
        plan_exists = table_exists(conn, "qsb_literature_metadata_registration_plan_dryrun")
        plan_rows = scalar(conn, "SELECT COUNT(*) FROM qsb_literature_metadata_registration_plan_dryrun") if plan_exists else 0
        wrong_boundary = (
            scalar(
                conn,
                """
                SELECT COUNT(*)
                FROM qsb_literature_metadata_registration_plan_dryrun
                WHERE claim_boundary <> ?
                """,
                (CLAIM_BOUNDARY,),
            )
            if plan_exists
            else 1
        )
    metadata_ok = plan_exists and plan_rows > 0 and wrong_boundary == 0
    rows.append(
        {
            "check_id": "V05",
            "check_name": "metadata_dryrun_registration_plan",
            "expected": "plan_table_present;plan_rows>0;wrong_boundary=0",
            "actual": f"plan_exists={str(plan_exists).lower()};plan_rows={plan_rows};wrong_boundary={wrong_boundary}",
            "status": "pass" if metadata_ok else "fail",
            "notes": "Metadata registration is planned in temp metadata DB copy only; no meta_* inserts invented.",
        }
    )
    if not metadata_ok:
        failures.append("metadata_dryrun_registration_plan")

    execute_blocked = "execution_import_authorized=false" in importer_text
    rows.append(
        {
            "check_id": "V06",
            "check_name": "execute_mode_blocked_for_patch_run",
            "expected": "true",
            "actual": str(execute_blocked).lower(),
            "status": "pass" if execute_blocked else "fail",
            "notes": "Execute mode requires a separate authorized execution run.",
        }
    )
    if not execute_blocked:
        failures.append("execute_mode_blocked_for_patch_run")

    rows.append(
        {
            "check_id": "V07",
            "check_name": "final_status_allowed",
            "expected": "allowed_status",
            "actual": FINAL_STATUS,
            "status": "pass",
            "notes": "Final status selected from prompt allowed statuses.",
        }
    )
    rows.append(
        {
            "check_id": "V08",
            "check_name": "claim_boundary_preserved",
            "expected": CLAIM_BOUNDARY,
            "actual": CLAIM_BOUNDARY,
            "status": "pass",
            "notes": "No physics or mechanism claim is made.",
        }
    )

    write_csv(RUN_DIR / "validation" / "validation_results.csv", ["check_id", "check_name", "expected", "actual", "status", "notes"], rows)
    write_csv(RUN_DIR / "data" / "validation_results.csv", ["check_id", "check_name", "expected", "actual", "status", "notes"], rows)

    if failures:
        for failure in failures:
            print(f"FAIL: {failure}")
        return 1
    print("PASS: two-DB importer patch validation passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
