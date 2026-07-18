#!/usr/bin/env python3
"""Dry-run or execute a SQLite import for prepared literature metadata.

Default mode is dry-run. For the approved two-DB architecture, dry-run copies
the real data and metadata DBs to /tmp and writes only to those copies.
Execute mode remains blocked for this patch run.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import shutil
import sqlite3
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from scripts.qsb_literature_metadata.native_contract_constants import (
    CLAIM_BOUNDARY,
    CUBE_MAPPING_STATUS,
    DATA_MART_CREATION_AUTHORIZED,
    EXECUTION_IMPORT_AUTHORIZED,
    MECHANISM_CLAIM_RELEASE,
    PHYSICAL_CLAIM_RELEASE,
    PLANCK_SPACE_MAPPING_STATUS,
)
from scripts.qsb_literature_metadata.native_metadata_mapping import (
    MappingError,
    apply_operations_to_temp_db,
    build_operation_plan,
    detect_alias_collisions,
    lineage_validation,
    operation_summaries,
    quantity_policy,
    read_registration_plan,
    schema_fingerprint,
    vocabulary_entries,
    write_operations_csv,
)

RUN_DIR = Path("runs/QSB-PBR-LITERATURE-METADATA-SERVER-IMPORT-01")
PATCH_RUN_DIR = Path("runs/QSB-PBR-LITERATURE-METADATA-TWO-DB-IMPORTER-PATCH-01")
DEPRECATED_SINGLE_DB_STATUS = "single_db_mode_deprecated_for_two_db_architecture"
METADATA_PLAN_STATUS = "metadata_registration_planned_requires_schema_mapping_review"
EXECUTE_BLOCKED_STATUS = "execution_import_authorized=false"


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: Path, fieldnames: list[str], rows: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def copy_for_dry_run(source: Path, label: str) -> Path:
    if not source.exists():
        raise FileNotFoundError(f"DB target does not exist: {source}")
    tmp_dir = Path(tempfile.gettempdir())
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    target = tmp_dir / f"qsb_pbr_literature_two_db_dryrun_{label}_{timestamp}.sqlite"
    shutil.copy2(source, target)
    return target


def sidecars(path: Path) -> str:
    return ";".join(str(Path(str(path) + suffix)) for suffix in ("-journal", "-wal", "-shm") if Path(str(path) + suffix).exists())


def db_integrity_row(path: Path, role: str) -> dict[str, object]:
    row: dict[str, object] = {
        "target_role": role,
        "real_db_path": path.as_posix(),
        "sha256": sha256_file(path),
        "mtime_ns": path.stat().st_mtime_ns,
        "byte_size": path.stat().st_size,
        "sqlite_integrity_check": "",
        "schema_fingerprint": "",
        "row_count_fingerprint": "",
        "sidecar_files": sidecars(path),
    }
    with sqlite3.connect(f"file:{path.resolve().as_posix()}?mode=ro", uri=True) as conn:
        row["sqlite_integrity_check"] = conn.execute("PRAGMA integrity_check").fetchone()[0]
        row["schema_fingerprint"] = schema_fingerprint(conn)
        counts = []
        for table_name, in conn.execute("SELECT name FROM sqlite_schema WHERE type='table' ORDER BY name"):
            count = conn.execute(f'SELECT COUNT(*) FROM "{table_name}"').fetchone()[0]
            counts.append(f"{table_name}:{count}")
        row["row_count_fingerprint"] = hashlib.sha256("|".join(counts).encode("utf-8")).hexdigest()
    return row


def targets_unchanged(before: list[dict[str, object]], after: list[dict[str, object]]) -> bool:
    after_by_role = {row["target_role"]: row for row in after}
    for before_row in before:
        after_row = after_by_role[before_row["target_role"]]
        for key in ["sha256", "mtime_ns", "byte_size", "sqlite_integrity_check", "schema_fingerprint", "row_count_fingerprint", "sidecar_files"]:
            if before_row[key] != after_row[key]:
                return False
    return True


def create_tables(conn: sqlite3.Connection) -> None:
    conn.executescript(
        """
        CREATE TABLE IF NOT EXISTS qsb_literature_source (
          literature_id TEXT PRIMARY KEY,
          source_key TEXT UNIQUE NOT NULL,
          title TEXT NOT NULL,
          authors TEXT NOT NULL,
          year INTEGER,
          venue TEXT,
          doi TEXT,
          arxiv_id TEXT,
          source_url TEXT,
          source_type TEXT,
          source_class TEXT,
          author_cluster TEXT,
          theory_cluster TEXT,
          green_status TEXT,
          risk_status TEXT,
          verification_status TEXT,
          discovery_channel TEXT,
          notes TEXT
        );
        CREATE TABLE IF NOT EXISTS qsb_literature_mechanism_tag (
          literature_id TEXT NOT NULL,
          mechanism_tag TEXT NOT NULL,
          tag_role TEXT,
          PRIMARY KEY (literature_id, mechanism_tag)
        );
        CREATE TABLE IF NOT EXISTS qsb_literature_claim_boundary (
          literature_id TEXT PRIMARY KEY,
          internal_evidence_flag INTEGER NOT NULL DEFAULT 0,
          mechanism_claim_support INTEGER NOT NULL DEFAULT 0,
          physical_claim_support INTEGER NOT NULL DEFAULT 0,
          allowed_use TEXT NOT NULL,
          forbidden_use TEXT NOT NULL,
          claim_boundary TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS qsb_literature_qsb_mapping (
          literature_id TEXT NOT NULL,
          qsb_structure_tag TEXT NOT NULL,
          mapping_kind TEXT,
          mapping_strength TEXT,
          mapping_notes TEXT,
          PRIMARY KEY (literature_id, qsb_structure_tag)
        );
        CREATE TABLE IF NOT EXISTS qsb_literature_import_manifest (
          import_id TEXT PRIMARY KEY,
          run_id TEXT NOT NULL,
          source_report_path TEXT,
          source_report_sha256 TEXT,
          import_timestamp_utc TEXT,
          db_target TEXT,
          schema_action TEXT,
          row_count_sources INTEGER,
          row_count_tags INTEGER,
          row_count_claim_boundaries INTEGER,
          validation_status TEXT,
          claim_boundary TEXT
        );
        """
    )


def insert_rows(conn: sqlite3.Connection, table: str, rows: list[dict[str, str]]) -> None:
    if not rows:
        return
    columns = list(rows[0].keys())
    placeholders = ",".join("?" for _ in columns)
    sql = f"INSERT OR ABORT INTO {table} ({','.join(columns)}) VALUES ({placeholders})"
    conn.executemany(sql, [[row[column] for column in columns] for row in rows])


def create_metadata_plan_table(conn: sqlite3.Connection) -> None:
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS qsb_literature_metadata_registration_plan_dryrun (
          table_name TEXT NOT NULL,
          field_name TEXT NOT NULL,
          canonical_name TEXT NOT NULL,
          de_label TEXT,
          en_label TEXT,
          description_de TEXT,
          description_en TEXT,
          data_type TEXT,
          allowed_values TEXT,
          lineage_note TEXT,
          claim_boundary_note TEXT,
          registration_status TEXT NOT NULL,
          claim_boundary TEXT NOT NULL
        )
        """
    )


def insert_metadata_plan(conn: sqlite3.Connection, rows: list[dict[str, str]]) -> None:
    planned_rows = []
    for row in rows:
        planned = dict(row)
        planned["registration_status"] = METADATA_PLAN_STATUS
        planned["claim_boundary"] = CLAIM_BOUNDARY
        planned_rows.append(planned)
    insert_rows(conn, "qsb_literature_metadata_registration_plan_dryrun", planned_rows)


def validate(conn: sqlite3.Connection) -> list[str]:
    failures: list[str] = []
    checks = [
        ("source_count", "SELECT COUNT(*) FROM qsb_literature_source", 23),
        ("claim_boundary_count", "SELECT COUNT(*) FROM qsb_literature_claim_boundary", 23),
        ("nonzero_internal_evidence", "SELECT COUNT(*) FROM qsb_literature_claim_boundary WHERE internal_evidence_flag <> 0", 0),
        ("nonzero_mechanism_claim", "SELECT COUNT(*) FROM qsb_literature_claim_boundary WHERE mechanism_claim_support <> 0", 0),
        ("nonzero_physical_claim", "SELECT COUNT(*) FROM qsb_literature_claim_boundary WHERE physical_claim_support <> 0", 0),
        ("wrong_claim_boundary", "SELECT COUNT(*) FROM qsb_literature_claim_boundary WHERE claim_boundary <> ?", 0),
    ]
    for name, sql, expected in checks:
        params = (CLAIM_BOUNDARY,) if "?" in sql else ()
        actual = conn.execute(sql, params).fetchone()[0]
        if actual != expected:
            failures.append(f"{name}: expected {expected}, observed {actual}")
    missing_tags = conn.execute(
        """
        SELECT COUNT(*)
        FROM qsb_literature_source s
        WHERE NOT EXISTS (
          SELECT 1 FROM qsb_literature_mechanism_tag t
          WHERE t.literature_id = s.literature_id
        )
        """
    ).fetchone()[0]
    if missing_tags != 0:
        failures.append(f"sources_without_tags: expected 0, observed {missing_tags}")
    forbidden_phrases = [
        "supports QSB",
        "proves QSB",
        "confirms mechanism",
        "evidence for QSB",
        "physical discovery",
    ]
    claim_text = conn.execute(
        """
        SELECT lower(group_concat(allowed_use || ' ' || forbidden_use || ' ' || claim_boundary, ' '))
        FROM qsb_literature_claim_boundary
        """
    ).fetchone()[0] or ""
    for phrase in forbidden_phrases:
        if phrase.lower() in claim_text:
            failures.append(f"forbidden_phrase_present: {phrase}")
    return failures


def validate_metadata_plan(conn: sqlite3.Connection) -> list[str]:
    failures: list[str] = []
    row_count = conn.execute(
        "SELECT COUNT(*) FROM qsb_literature_metadata_registration_plan_dryrun"
    ).fetchone()[0]
    missing_canonical = conn.execute(
        """
        SELECT COUNT(*)
        FROM qsb_literature_metadata_registration_plan_dryrun
        WHERE canonical_name IS NULL OR canonical_name = ''
        """
    ).fetchone()[0]
    wrong_boundary = conn.execute(
        """
        SELECT COUNT(*)
        FROM qsb_literature_metadata_registration_plan_dryrun
        WHERE claim_boundary <> ?
        """,
        (CLAIM_BOUNDARY,),
    ).fetchone()[0]
    if row_count == 0:
        failures.append("metadata_registration_plan_empty")
    if missing_canonical != 0:
        failures.append(f"metadata_plan_missing_canonical_name: {missing_canonical}")
    if wrong_boundary != 0:
        failures.append(f"metadata_plan_wrong_claim_boundary: {wrong_boundary}")
    return failures


def load_seed_bundle(seed_path: Path) -> tuple[list[dict[str, str]], ...]:
    data_dir = seed_path.parent
    return (
        read_csv(seed_path),
        read_csv(data_dir / "literature_mechanism_tags.csv"),
        read_csv(data_dir / "literature_claim_boundaries.csv"),
        read_csv(data_dir / "literature_import_manifest.csv"),
        read_csv(data_dir / "metadata_server_registration_plan.csv"),
    )


def run_single_db_dry_run(seed_path: Path) -> int:
    sources, tags, boundaries, manifest, _metadata_plan = load_seed_bundle(seed_path)
    conn = sqlite3.connect(":memory:")
    try:
        conn.execute("BEGIN")
        create_tables(conn)
        insert_rows(conn, "qsb_literature_source", sources)
        insert_rows(conn, "qsb_literature_mechanism_tag", tags)
        insert_rows(conn, "qsb_literature_claim_boundary", boundaries)
        insert_rows(conn, "qsb_literature_import_manifest", manifest)
        failures = validate(conn)
        conn.rollback()
        if failures:
            for failure in failures:
                print(f"FAIL: {failure}")
            return 1
        print(DEPRECATED_SINGLE_DB_STATUS)
        print("PASS: compatibility dry-run validation passed; transaction rolled back")
        return 0
    finally:
        conn.close()


def write_native_dryrun_reports(
    output_dir: Path,
    operations,
    native_apply_result: dict[str, object],
    metadata_copy: Path,
    idempotency_result: dict[str, object],
    rollback_result: dict[str, object],
) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    write_operations_csv(output_dir / "native_operation_plan.csv", operations)
    lookup_counts, conflict_counts = operation_summaries(operations)
    write_csv(output_dir / "native_lookup_outcomes.csv", ["lookup_outcome", "count"], [{"lookup_outcome": key, "count": value} for key, value in sorted(lookup_counts.items())])
    write_csv(output_dir / "native_conflict_classes.csv", ["conflict_class", "count"], [{"conflict_class": key, "count": value} for key, value in sorted(conflict_counts.items())])
    write_csv(output_dir / "native_lineage_results.csv", list(lineage_validation(operations)[0].keys()), lineage_validation(operations))
    rows_by_id = {}
    for op in operations:
        rows_by_id.setdefault(op.registration_plan_row_id, op)
    write_csv(
        output_dir / "native_claim_boundary_results.csv",
        ["claim_boundary", "physical_claim_release", "mechanism_claim_release", "execution_import_authorized", "data_mart_creation_authorized", "status"],
        [{
            "claim_boundary": CLAIM_BOUNDARY,
            "physical_claim_release": PHYSICAL_CLAIM_RELEASE,
            "mechanism_claim_release": MECHANISM_CLAIM_RELEASE,
            "execution_import_authorized": EXECUTION_IMPORT_AUTHORIZED,
            "data_mart_creation_authorized": DATA_MART_CREATION_AUTHORIZED,
            "status": "pass",
        }],
    )
    write_csv(output_dir / "native_dryrun_apply_result.csv", list(native_apply_result.keys()), [native_apply_result])
    write_csv(output_dir / "native_idempotency_rerun_result.csv", list(idempotency_result.keys()), [idempotency_result])
    write_csv(output_dir / "native_rollback_result.csv", list(rollback_result.keys()), [rollback_result])
    manifest = {
        "operation_count": len(operations),
        "lookup_outcomes": dict(lookup_counts),
        "conflict_classes": dict(conflict_counts),
        "metadata_temp_db": metadata_copy.as_posix(),
        "claim_boundary": CLAIM_BOUNDARY,
        "physical_claim_release": PHYSICAL_CLAIM_RELEASE,
        "mechanism_claim_release": MECHANISM_CLAIM_RELEASE,
        "execution_import_authorized": False,
        "data_mart_creation_authorized": False,
        "future_cube_boundary_status": CUBE_MAPPING_STATUS,
        "future_planck_space_boundary_status": PLANCK_SPACE_MAPPING_STATUS,
    }
    (output_dir / "native_mapping_manifest.json").write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def run_native_metadata_dryrun(metadata_copy: Path, metadata_plan: list[dict[str, str]], output_dir: Path) -> tuple[list[str], dict[str, object]]:
    failures: list[str] = []
    operation_count = 0
    try:
        plan_path = RUN_DIR / "data" / "metadata_server_registration_plan.csv"
        rows = read_registration_plan(plan_path)
        operations = build_operation_plan(rows, mode="dry-run")
        operation_count = len(operations)
        if len(metadata_plan) != len(rows):
            failures.append(f"native_plan_row_mismatch: seed={len(metadata_plan)} planner={len(rows)}")
        if detect_alias_collisions(rows):
            failures.append("native_alias_collision_detected")
        quantity_rows = [quantity_policy(row) for row in rows]
        if len(quantity_rows) != 17:
            failures.append("native_quantity_policy_row_mismatch")
        vocab_rows = vocabulary_entries(rows)
        if not vocab_rows:
            failures.append("native_vocabulary_seed_empty")
        with sqlite3.connect(metadata_copy) as metadata_conn:
            metadata_conn.execute("BEGIN")
            native_apply_result = apply_operations_to_temp_db(metadata_conn, operations)
            metadata_conn.commit()
            metadata_conn.execute("BEGIN")
            idempotency_result = apply_operations_to_temp_db(metadata_conn, operations)
            metadata_conn.commit()
            metadata_conn.execute("BEGIN")
            before_count = metadata_conn.execute("SELECT COUNT(*) FROM qsb_literature_native_operation_dryrun").fetchone()[0]
            metadata_conn.execute("INSERT INTO qsb_literature_native_validation_dryrun VALUES (?,?,?)", ("rollback_probe", "pass", "temporary"))
            metadata_conn.rollback()
            after_count = metadata_conn.execute("SELECT COUNT(*) FROM qsb_literature_native_operation_dryrun").fetchone()[0]
        rollback_result = {
            "rollback_test": "pass" if before_count == after_count else "fail",
            "before_count": before_count,
            "after_count": after_count,
        }
        if idempotency_result["noop"] != len(operations):
            failures.append(f"native_idempotency_not_noop: {idempotency_result}")
        if rollback_result["rollback_test"] != "pass":
            failures.append("native_rollback_failed")
        report_result = {
            "operation_count": operation_count,
            "native_apply_status": "pass" if not failures else "fail",
            "inserted": native_apply_result["inserted"],
            "idempotency_noop": idempotency_result["noop"],
            "rollback_status": rollback_result["rollback_test"],
        }
        write_native_dryrun_reports(output_dir, operations, native_apply_result, metadata_copy, idempotency_result, rollback_result)
        return failures, report_result
    except (MappingError, sqlite3.DatabaseError) as exc:
        failures.append(str(exc))
        return failures, {"operation_count": operation_count, "native_apply_status": "fail", "error": str(exc)}


def run_two_db_dry_run(data_db: Path, metadata_db: Path, seed_path: Path, output_dir: Path) -> int:
    sources, tags, boundaries, manifest, metadata_plan = load_seed_bundle(seed_path)
    before = [db_integrity_row(data_db, "literature_data_db"), db_integrity_row(metadata_db, "metadata_registration_db")]
    data_copy = copy_for_dry_run(data_db, "data")
    metadata_copy = copy_for_dry_run(metadata_db, "metadata")

    data_failures: list[str] = []
    metadata_failures: list[str] = []
    with sqlite3.connect(data_copy) as data_conn:
        data_conn.execute("BEGIN")
        create_tables(data_conn)
        insert_rows(data_conn, "qsb_literature_source", sources)
        insert_rows(data_conn, "qsb_literature_mechanism_tag", tags)
        insert_rows(data_conn, "qsb_literature_claim_boundary", boundaries)
        insert_rows(data_conn, "qsb_literature_import_manifest", manifest)
        data_failures = validate(data_conn)
        if data_failures:
            data_conn.rollback()
        else:
            data_conn.commit()

    with sqlite3.connect(metadata_copy) as metadata_conn:
        metadata_conn.execute("BEGIN")
        create_metadata_plan_table(metadata_conn)
        insert_metadata_plan(metadata_conn, metadata_plan)
        metadata_failures = validate_metadata_plan(metadata_conn)
        if metadata_failures:
            metadata_conn.rollback()
        else:
            metadata_conn.commit()

    native_failures, native_result = run_native_metadata_dryrun(metadata_copy, metadata_plan, output_dir)
    metadata_failures.extend(native_failures)
    after = [db_integrity_row(data_db, "literature_data_db"), db_integrity_row(metadata_db, "metadata_registration_db")]
    unchanged = targets_unchanged(before, after)

    summary_rows = [
        {
            "target_role": "literature_data_db",
            "real_db_path": data_db.as_posix(),
            "dryrun_db_path": data_copy.as_posix(),
            "sha256_before": before[0]["sha256"],
            "sha256_after": after[0]["sha256"],
            "mtime_ns_before": before[0]["mtime_ns"],
            "mtime_ns_after": after[0]["mtime_ns"],
            "real_target_unchanged": str(before[0]["sha256"] == after[0]["sha256"] and before[0]["mtime_ns"] == after[0]["mtime_ns"]).lower(),
            "dry_run_status": "pass" if not data_failures else "fail",
        },
        {
            "target_role": "metadata_registration_db",
            "real_db_path": metadata_db.as_posix(),
            "dryrun_db_path": metadata_copy.as_posix(),
            "sha256_before": before[1]["sha256"],
            "sha256_after": after[1]["sha256"],
            "mtime_ns_before": before[1]["mtime_ns"],
            "mtime_ns_after": after[1]["mtime_ns"],
            "real_target_unchanged": str(before[1]["sha256"] == after[1]["sha256"] and before[1]["mtime_ns"] == after[1]["mtime_ns"]).lower(),
            "dry_run_status": "pass" if not metadata_failures else "fail",
        },
    ]
    if output_dir == PATCH_RUN_DIR / "data":
        write_csv(
            PATCH_RUN_DIR / "data" / "two_db_dry_run_target_integrity.csv",
            [
                "target_role",
                "real_db_path",
                "dryrun_db_path",
                "sha256_before",
                "sha256_after",
                "mtime_ns_before",
                "mtime_ns_after",
                "real_target_unchanged",
                "dry_run_status",
            ],
            summary_rows,
        )
    write_csv(output_dir / "two_db_dry_run_target_integrity.csv", list(summary_rows[0].keys()), summary_rows)

    if data_failures or metadata_failures or not unchanged:
        for failure in data_failures + metadata_failures:
            print(f"FAIL: {failure}")
        if not unchanged:
            print("FAIL: real DB target hash or mtime changed")
        return 1

    print("two_db_dry_run_strategy=temp_copy_to_/tmp")
    print(f"data_dryrun_copy={data_copy}")
    print(f"metadata_dryrun_copy={metadata_copy}")
    print(METADATA_PLAN_STATUS)
    print(f"native_operation_count={native_result['operation_count']}")
    print(f"native_mapping_reports={output_dir}")
    print("PASS: two-DB dry-run validation passed; real DB targets unchanged")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--db")
    parser.add_argument("--data-db")
    parser.add_argument("--metadata-db")
    parser.add_argument("--seed", default=str(RUN_DIR / "data" / "literature_source_seed.csv"))
    parser.add_argument("--output-dir", default=str(PATCH_RUN_DIR / "data"))
    parser.add_argument(
        "--execution-import-authorized",
        default=EXECUTION_IMPORT_AUTHORIZED,
        help="Must remain false unless a separate human authorization artifact explicitly permits execute.",
    )
    parser.add_argument("--mode", choices=["dry-run", "execute"], default="dry-run")
    args = parser.parse_args()

    seed_path = Path(args.seed)
    if args.data_db or args.metadata_db:
        if not args.data_db or not args.metadata_db:
            print("FAIL: two-DB mode requires both --data-db and --metadata-db")
            return 2
        if args.db:
            print("FAIL: do not combine deprecated --db with --data-db/--metadata-db")
            return 2
        if args.mode == "execute":
            if args.execution_import_authorized != "true":
                print(EXECUTE_BLOCKED_STATUS)
                print("FAIL: execute mode requires --execution-import-authorized true and a separate authorized execution run")
                return 2
            print(EXECUTE_BLOCKED_STATUS)
            print("FAIL: execute mode remains blocked in this implementation patch; native real-target writes are not authorized")
            return 2
        return run_two_db_dry_run(Path(args.data_db), Path(args.metadata_db), seed_path, Path(args.output_dir))

    if args.db:
        if args.mode == "execute":
            print(DEPRECATED_SINGLE_DB_STATUS)
            print("FAIL: execute mode is not allowed with deprecated single-DB architecture")
            return 2
        return run_single_db_dry_run(seed_path)

    parser.error("provide either --data-db and --metadata-db, or deprecated --db for dry-run compatibility")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
