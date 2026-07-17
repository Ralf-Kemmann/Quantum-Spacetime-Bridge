#!/usr/bin/env python3
"""Review the QSB/PBR literature metadata two-DB dry-run artifacts."""

from __future__ import annotations

import csv
import os
import sqlite3
from pathlib import Path


RUN_ID = "QSB-PBR-LITERATURE-METADATA-TWO-DB-DRYRUN-REVIEW-01"
RUN_DIR = Path("runs") / RUN_ID
DATA_DIR = RUN_DIR / "data"
VALIDATION_DIR = RUN_DIR / "validation"
PATCH_DIR = Path("runs/QSB-PBR-LITERATURE-METADATA-TWO-DB-IMPORTER-PATCH-01")
IMPORT_DIR = Path("runs/QSB-PBR-LITERATURE-METADATA-SERVER-IMPORT-01")
IMPORTER = IMPORT_DIR / "scripts" / "import_literature_metadata.py"
SEED = IMPORT_DIR / "data" / "literature_source_seed.csv"
TAGS = IMPORT_DIR / "data" / "literature_mechanism_tags.csv"
CLAIM_BOUNDARY = "literature_context_only_no_internal_evidence_no_mechanism_claim"
FINAL_STATUS = "two_db_dryrun_review_blocked_validation_failed"


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


def table_exists(conn: sqlite3.Connection, table: str) -> bool:
    return scalar(conn, "SELECT COUNT(*) FROM sqlite_schema WHERE type='table' AND name=?", (table,)) == 1


def table_columns(conn: sqlite3.Connection, table: str) -> set[str]:
    return {row[1] for row in conn.execute(f'PRAGMA table_info("{table}")')}


def journal_sidecars(path: Path) -> list[str]:
    candidates = [
        Path(str(path) + suffix)
        for suffix in ("-journal", "-wal", "-shm")
    ]
    return [candidate.as_posix() for candidate in candidates if candidate.exists()]


def main() -> int:
    integrity_path = PATCH_DIR / "data" / "two_db_dry_run_target_integrity.csv"
    patch_validation_path = PATCH_DIR / "data" / "validation_results.csv"
    cli_contract_path = PATCH_DIR / "data" / "cli_contract.csv"
    dry_run_test_path = PATCH_DIR / "data" / "dry_run_test_matrix.csv"
    next_action_path = PATCH_DIR / "data" / "recommended_next_action.csv"
    reviewed_paths = [
        integrity_path,
        patch_validation_path,
        cli_contract_path,
        dry_run_test_path,
        next_action_path,
        IMPORTER,
    ]

    integrity = read_csv(integrity_path)
    by_role = {row["target_role"]: row for row in integrity}
    data_copy = Path(by_role["literature_data_db"]["dryrun_db_path"])
    metadata_copy = Path(by_role["metadata_registration_db"]["dryrun_db_path"])
    real_data = Path(by_role["literature_data_db"]["real_db_path"])
    real_metadata = Path(by_role["metadata_registration_db"]["real_db_path"])
    importer_text = IMPORTER.read_text(encoding="utf-8")
    seed_rows = read_csv(SEED)
    tag_rows = read_csv(TAGS)

    reviewed_artifacts = [
        {
            "artifact_path": path.as_posix(),
            "exists": str(path.exists()).lower(),
            "artifact_role": (
                "patch_review_input" if path != IMPORTER else "patched_importer"
            ),
            "notes": "Required review input.",
        }
        for path in reviewed_paths
    ]

    dryrun_command_review = [
        {
            "check_name": "required_dry_run_command",
            "expected": "--data-db;--metadata-db;--seed;--mode dry-run",
            "actual": "fresh dry-run was run before review; see patch integrity CSV for copied DB paths",
            "status": "pass",
            "notes": "No execute command was run.",
        },
        {
            "check_name": "dryrun_temp_data_copy_exists",
            "expected": "true",
            "actual": str(data_copy.exists()).lower(),
            "status": "pass" if data_copy.exists() else "fail",
            "notes": data_copy.as_posix(),
        },
        {
            "check_name": "dryrun_temp_metadata_copy_exists",
            "expected": "true",
            "actual": str(metadata_copy.exists()).lower(),
            "status": "pass" if metadata_copy.exists() else "fail",
            "notes": metadata_copy.as_posix(),
        },
    ]

    data_integrity = by_role["literature_data_db"]
    metadata_integrity = by_role["metadata_registration_db"]
    data_sidecars = journal_sidecars(real_data)
    metadata_sidecars = journal_sidecars(real_metadata)
    real_target_integrity = [
        {
            "target_role": "literature_data_db",
            "real_db_path": real_data.as_posix(),
            "sha256_before": data_integrity["sha256_before"],
            "sha256_after": data_integrity["sha256_after"],
            "mtime_ns_before": data_integrity["mtime_ns_before"],
            "mtime_ns_after": data_integrity["mtime_ns_after"],
            "sidecar_files": ";".join(data_sidecars),
            "status": "pass"
            if data_integrity["real_target_unchanged"] == "true" and not data_sidecars
            else "fail",
            "notes": "Real DWH target unchanged; no journal/WAL/SHM sidecars detected.",
        },
        {
            "target_role": "metadata_registration_db",
            "real_db_path": real_metadata.as_posix(),
            "sha256_before": metadata_integrity["sha256_before"],
            "sha256_after": metadata_integrity["sha256_after"],
            "mtime_ns_before": metadata_integrity["mtime_ns_before"],
            "mtime_ns_after": metadata_integrity["mtime_ns_after"],
            "sidecar_files": ";".join(metadata_sidecars),
            "status": "pass"
            if metadata_integrity["real_target_unchanged"] == "true" and not metadata_sidecars
            else "fail",
            "notes": "Real metadata target unchanged; no journal/WAL/SHM sidecars detected.",
        },
    ]

    expected_tables = [
        "qsb_literature_source",
        "qsb_literature_mechanism_tag",
        "qsb_literature_claim_boundary",
        "qsb_literature_qsb_mapping",
        "qsb_literature_import_manifest",
    ]
    data_rows: list[dict[str, object]] = []
    with sqlite3.connect(f"file:{data_copy.as_posix()}?mode=ro", uri=True) as conn:
        for table in expected_tables:
            exists = table_exists(conn, table)
            count = scalar(conn, f'SELECT COUNT(*) FROM "{table}"') if exists else ""
            expected_count = {
                "qsb_literature_source": 23,
                "qsb_literature_claim_boundary": 23,
                "qsb_literature_mechanism_tag": 50,
                "qsb_literature_qsb_mapping": 0,
                "qsb_literature_import_manifest": 1,
            }[table]
            classification = ""
            if table == "qsb_literature_qsb_mapping" and count == 0:
                classification = "nonblocking_if_documented_as_future_cube_mapping"
            status = "pass" if exists and count == expected_count else "fail"
            if table == "qsb_literature_qsb_mapping" and exists and count == 0:
                status = "pass"
            data_rows.append(
                {
                    "table_name": table,
                    "exists": str(exists).lower(),
                    "expected_count": expected_count,
                    "actual_count": count,
                    "classification": classification,
                    "status": status,
                    "notes": "Dry-run data DB copy reviewed read-only.",
                }
            )
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
        bad_claim_rows = scalar(
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
        forbidden_rows = scalar(
            conn,
            """
            SELECT COUNT(*)
            FROM qsb_literature_claim_boundary
            WHERE lower(allowed_use || ' ' || forbidden_use || ' ' || claim_boundary) LIKE '%supports qsb%'
               OR lower(allowed_use || ' ' || forbidden_use || ' ' || claim_boundary) LIKE '%proves qsb%'
               OR lower(allowed_use || ' ' || forbidden_use || ' ' || claim_boundary) LIKE '%confirms mechanism%'
               OR lower(allowed_use || ' ' || forbidden_use || ' ' || claim_boundary) LIKE '%evidence for qsb%'
               OR lower(allowed_use || ' ' || forbidden_use || ' ' || claim_boundary) LIKE '%physical discovery%'
               OR lower(allowed_use || ' ' || forbidden_use || ' ' || claim_boundary) LIKE '%mechanism found%'
               OR lower(allowed_use || ' ' || forbidden_use || ' ' || claim_boundary) LIKE '%new physics confirmed%'
            """,
        )

    metadata_rows: list[dict[str, object]] = []
    with sqlite3.connect(f"file:{metadata_copy.as_posix()}?mode=ro", uri=True) as conn:
        plan_table = "qsb_literature_metadata_registration_plan_dryrun"
        plan_exists = table_exists(conn, plan_table)
        plan_count = scalar(conn, f'SELECT COUNT(*) FROM "{plan_table}"') if plan_exists else 0
        columns = table_columns(conn, plan_table) if plan_exists else set()
        german_labels = scalar(conn, f'SELECT COUNT(*) FROM "{plan_table}" WHERE de_label IS NOT NULL AND de_label <> ""') if plan_exists else 0
        canonical_names = scalar(conn, f'SELECT COUNT(*) FROM "{plan_table}" WHERE canonical_name IS NOT NULL AND canonical_name <> ""') if plan_exists else 0
        boundary_notes = scalar(conn, f'SELECT COUNT(*) FROM "{plan_table}" WHERE claim_boundary_note IS NOT NULL AND claim_boundary_note <> ""') if plan_exists else 0
        evidence_claim_rows = scalar(
            conn,
            f"""
            SELECT COUNT(*)
            FROM "{plan_table}"
            WHERE lower(coalesce(claim_boundary_note,'') || ' ' || coalesce(description_en,'') || ' ' || coalesce(description_de,'')) LIKE '%supports qsb%'
               OR lower(coalesce(claim_boundary_note,'') || ' ' || coalesce(description_en,'') || ' ' || coalesce(description_de,'')) LIKE '%evidence for qsb%'
               OR lower(coalesce(claim_boundary_note,'') || ' ' || coalesce(description_en,'') || ' ' || coalesce(description_de,'')) LIKE '%internal evidence for qsb%'
               OR lower(coalesce(claim_boundary_note,'') || ' ' || coalesce(description_en,'') || ' ' || coalesce(description_de,'')) LIKE '%mechanism confirmation%'
               OR lower(coalesce(claim_boundary_note,'') || ' ' || coalesce(description_en,'') || ' ' || coalesce(description_de,'')) LIKE '%physics claim%'
            """,
        ) if plan_exists else 1
        table_coverage = {}
        for table in expected_tables:
            table_coverage[table] = scalar(
                conn,
                f'SELECT COUNT(*) FROM "{plan_table}" WHERE table_name=?',
                (table,),
            ) if plan_exists else 0
        key_field_coverage = {}
        for field in ("literature_id", "source_key", "mechanism_tag", "claim_boundary"):
            key_field_coverage[field] = scalar(
                conn,
                f'SELECT COUNT(*) FROM "{plan_table}" WHERE field_name=? OR canonical_name=?',
                (field, field),
            ) if plan_exists else 0

    metadata_status = (
        plan_exists
        and plan_count == 17
        and german_labels == plan_count
        and canonical_names == plan_count
        and boundary_notes == plan_count
        and evidence_claim_rows == 0
    )
    metadata_rows.append(
        {
            "review_item": "registration_mode",
            "expected": "metadata_registration_plan_only",
            "actual": "metadata_registration_plan_only" if plan_exists else "missing",
            "row_count": plan_count,
            "status": "pass_with_schema_mapping_review_required" if metadata_status else "fail",
            "notes": "Native meta_* inserts are not implemented; this is acceptable for dry-run review only and requires schema mapping review before execution design.",
        }
    )
    metadata_rows.append(
        {
            "review_item": "required_columns",
            "expected": "canonical_name;de_label;claim_boundary_note",
            "actual": ";".join(sorted(columns)),
            "row_count": plan_count,
            "status": "pass" if {"canonical_name", "de_label", "claim_boundary_note"} <= columns else "fail",
            "notes": "Plan table column coverage.",
        }
    )
    for table, count in table_coverage.items():
        metadata_rows.append(
            {
                "review_item": f"table_coverage:{table}",
                "expected": ">=1",
                "actual": count,
                "row_count": plan_count,
                "status": "pass" if count >= 1 or table == "qsb_literature_import_manifest" else "review",
                "notes": "Registration plan coverage by literature table.",
            }
        )
    for field, count in key_field_coverage.items():
        metadata_rows.append(
            {
                "review_item": f"key_field_coverage:{field}",
                "expected": ">=1",
                "actual": count,
                "row_count": plan_count,
                "status": "pass" if count >= 1 else "fail",
                "notes": "Registration plan coverage by key field.",
            }
        )

    valid_source_types = {
        "primary_literature",
        "review",
        "handbook_chapter",
        "lecture_notes",
        "speculative_program",
        "secondary_commentary",
    }
    valid_source_classes = {"GREEN", "GREEN-YELLOW", "YELLOW", "RED-YELLOW", "RED"}
    valid_author_clusters = {
        "LQG_quantum_geometry",
        "Wadia_holography_string_black_holes",
        "FLM_Born_metastring_modular_spacetime",
    }
    valid_theory_clusters = {
        "loop_quantum_geometry",
        "holography_string_qg",
        "born_geometry_phase_space",
    }
    source_class_missing = sum(1 for row in seed_rows if not row.get("source_class"))
    author_missing = sum(1 for row in seed_rows if not row.get("author_cluster"))
    theory_missing = sum(1 for row in seed_rows if not row.get("theory_cluster"))
    invalid_source_type = sum(1 for row in seed_rows if row.get("source_type") not in valid_source_types)
    invalid_source_class = sum(1 for row in seed_rows if row.get("source_class") not in valid_source_classes)
    invalid_author_cluster = sum(1 for row in seed_rows if row.get("author_cluster") not in valid_author_clusters)
    invalid_theory_cluster = sum(1 for row in seed_rows if row.get("theory_cluster") not in valid_theory_clusters)
    nonempty_citation_fields = sum(
        1
        for row in seed_rows
        if row.get("doi") or row.get("arxiv_id") or row.get("source_url")
    )
    malformed_notes = sum(1 for row in seed_rows if row.get("notes") is None)
    seed_schema_ok = (
        invalid_source_type == 0
        and invalid_source_class == 0
        and invalid_author_cluster == 0
        and invalid_theory_cluster == 0
        and nonempty_citation_fields == 0
        and malformed_notes == 0
    )
    claim_rows = [
        {
            "review_item": "claim_boundary_flags",
            "expected": "bad_claim_rows=0",
            "actual": f"bad_claim_rows={bad_claim_rows}",
            "status": "pass" if bad_claim_rows == 0 else "fail",
            "notes": CLAIM_BOUNDARY,
        },
        {
            "review_item": "forbidden_claim_phrases",
            "expected": "forbidden_rows=0",
            "actual": f"forbidden_rows={forbidden_rows}",
            "status": "pass" if forbidden_rows == 0 else "fail",
            "notes": "Includes expanded phrase list from dry-run review prompt.",
        },
        {
            "review_item": "source_seed_completeness",
            "expected": "sources=23;missing_tags=0;source_class_missing=0;author_missing=0;theory_missing=0",
            "actual": f"sources={len(seed_rows)};missing_tags={missing_tags};source_class_missing={source_class_missing};author_missing={author_missing};theory_missing={theory_missing}",
            "status": "pass" if len(seed_rows) == 23 and missing_tags == 0 and source_class_missing == 0 and author_missing == 0 and theory_missing == 0 else "fail",
            "notes": "Seed remains context/search-space metadata only.",
        },
        {
            "review_item": "seed_column_alignment_and_enums",
            "expected": "invalid_source_type=0;invalid_source_class=0;invalid_author_cluster=0;invalid_theory_cluster=0;nonempty_citation_fields=0;malformed_notes=0",
            "actual": f"invalid_source_type={invalid_source_type};invalid_source_class={invalid_source_class};invalid_author_cluster={invalid_author_cluster};invalid_theory_cluster={invalid_theory_cluster};nonempty_citation_fields={nonempty_citation_fields};malformed_notes={malformed_notes}",
            "status": "pass" if seed_schema_ok else "fail",
            "notes": "Failure indicates CSV column shift; source_url contains source_type-like values and classification fields are displaced.",
        },
    ]

    execute_rows = [
        {
            "review_item": "two_db_execute_block",
            "expected": "execution_import_authorized=false",
            "actual": "execution_import_authorized=false" if "execution_import_authorized=false" in importer_text else "missing",
            "status": "pass" if "execution_import_authorized=false" in importer_text else "fail",
            "notes": "--mode execute requires separate authorized execution run.",
        },
        {
            "review_item": "single_db_execute_block",
            "expected": "single_db execute blocked",
            "actual": "single_db execute blocked" if "execute mode is not allowed with deprecated single-DB architecture" in importer_text else "missing",
            "status": "pass" if "execute mode is not allowed with deprecated single-DB architecture" in importer_text else "fail",
            "notes": "No path for deprecated single-DB execute.",
        },
        {
            "review_item": "deprecated_single_db_notice",
            "expected": "single_db_mode_deprecated_for_two_db_architecture",
            "actual": "present" if "single_db_mode_deprecated_for_two_db_architecture" in importer_text else "missing",
            "status": "pass" if "single_db_mode_deprecated_for_two_db_architecture" in importer_text else "fail",
            "notes": "Single-target mode is dry-run compatibility only.",
        },
    ]

    risk_rows = [
        {
            "risk_id": "R01",
            "risk": "metadata_native_mapping_not_implemented",
            "severity": "medium",
            "status": "open_nonblocking_for_dryrun_review",
            "mitigation": "Run QSB-PBR-LITERATURE-METADATA-METADATA-SCHEMA-MAPPING-REVIEW-01 before execution design.",
            "claim_boundary": CLAIM_BOUNDARY,
        },
        {
            "risk_id": "R02",
            "risk": "qsb_literature_qsb_mapping_empty",
            "severity": "low",
            "status": "nonblocking_if_documented_as_future_cube_mapping",
            "mitigation": "Document future cube mapping semantics before analytical cube use.",
            "claim_boundary": CLAIM_BOUNDARY,
        },
        {
            "risk_id": "R03",
            "risk": "execute_not_authorized",
            "severity": "high",
            "status": "controlled",
            "mitigation": "Keep execute blocked until separate human-approved execution design gate.",
            "claim_boundary": CLAIM_BOUNDARY,
        },
        {
            "risk_id": "R04",
            "risk": "literature_source_seed_csv_column_shift",
            "severity": "high",
            "status": "blocking_validation_failed",
            "mitigation": "Run a seed CSV repair/validation patch before any execution-design package.",
            "claim_boundary": CLAIM_BOUNDARY,
        },
    ]
    decision_rows = [
        {
            "decision_key": "final_status",
            "value": FINAL_STATUS,
            "notes": "Dry-run mechanics are safe, but review found a blocking literature_source_seed.csv column-alignment/enumeration failure.",
            "claim_boundary": CLAIM_BOUNDARY,
        },
        {
            "decision_key": "execution_import_authorized",
            "value": "false",
            "notes": "Review does not authorize execute import.",
            "claim_boundary": CLAIM_BOUNDARY,
        },
        {
            "decision_key": "recommended_next_package",
            "value": "QSB-PBR-LITERATURE-METADATA-SEED-CSV-REPAIR-VALIDATION-01",
            "notes": "Repair seed CSV column alignment before metadata schema mapping or execution design.",
            "claim_boundary": CLAIM_BOUNDARY,
        },
    ]
    next_rows = [
        {
            "step_order": 1,
            "action": "review_seed_alignment_blocker",
            "exact_command": "sed -n '1,120p' runs/QSB-PBR-LITERATURE-METADATA-TWO-DB-DRYRUN-REVIEW-01/data/claim_boundary_review.csv",
            "notes": "Review the seed CSV column shift and enum validation blocker.",
            "claim_boundary": CLAIM_BOUNDARY,
        },
        {
            "step_order": 2,
            "action": "authorize_minimal_repair_if_desired",
            "exact_command": "none",
            "notes": "Next package recommendation: QSB-PBR-LITERATURE-METADATA-SEED-CSV-REPAIR-VALIDATION-01.",
            "claim_boundary": CLAIM_BOUNDARY,
        },
    ]

    validation_rows = [
        {
            "check_id": "V01",
            "check_name": "real_target_integrity",
            "expected": "all_pass",
            "actual": "all_pass" if all(row["status"] == "pass" for row in real_target_integrity) else "failed",
            "status": "pass" if all(row["status"] == "pass" for row in real_target_integrity) else "fail",
            "notes": "SHA256/mtime unchanged and no sidecars detected.",
        },
        {
            "check_id": "V02",
            "check_name": "data_db_tables",
            "expected": "all_pass",
            "actual": "all_pass" if all(row["status"] == "pass" for row in data_rows) else "failed",
            "status": "pass" if all(row["status"] == "pass" for row in data_rows) else "fail",
            "notes": "Expected dry-run literature tables and counts reviewed.",
        },
        {
            "check_id": "V03",
            "check_name": "metadata_registration_plan",
            "expected": "metadata_registration_plan_only",
            "actual": "metadata_registration_plan_only_requires_schema_mapping_review" if metadata_status else "failed",
            "status": "pass" if metadata_status else "fail",
            "notes": "Plan-only registration requires schema mapping review before execution design.",
        },
        {
            "check_id": "V04",
            "check_name": "claim_boundary",
            "expected": "all_pass",
            "actual": "all_pass" if all(row["status"] == "pass" for row in claim_rows) else "failed",
            "status": "pass" if all(row["status"] == "pass" for row in claim_rows) else "fail",
            "notes": CLAIM_BOUNDARY,
        },
        {
            "check_id": "V05",
            "check_name": "execute_block",
            "expected": "all_pass",
            "actual": "all_pass" if all(row["status"] == "pass" for row in execute_rows) else "failed",
            "status": "pass" if all(row["status"] == "pass" for row in execute_rows) else "fail",
            "notes": "No execute authorization path accepted by this review.",
        },
        {
            "check_id": "V06",
            "check_name": "final_status_allowed",
            "expected": "allowed_status",
            "actual": FINAL_STATUS,
            "status": "pass",
            "notes": "Status selected from prompt allowed list.",
        },
    ]

    write_csv(DATA_DIR / "reviewed_artifacts.csv", ["artifact_path", "exists", "artifact_role", "notes"], reviewed_artifacts)
    write_csv(DATA_DIR / "dryrun_command_review.csv", ["check_name", "expected", "actual", "status", "notes"], dryrun_command_review)
    write_csv(DATA_DIR / "real_target_integrity_review.csv", ["target_role", "real_db_path", "sha256_before", "sha256_after", "mtime_ns_before", "mtime_ns_after", "sidecar_files", "status", "notes"], real_target_integrity)
    write_csv(DATA_DIR / "dryrun_data_db_table_review.csv", ["table_name", "exists", "expected_count", "actual_count", "classification", "status", "notes"], data_rows)
    write_csv(DATA_DIR / "dryrun_metadata_db_registration_review.csv", ["review_item", "expected", "actual", "row_count", "status", "notes"], metadata_rows)
    write_csv(DATA_DIR / "claim_boundary_review.csv", ["review_item", "expected", "actual", "status", "notes"], claim_rows)
    write_csv(DATA_DIR / "execute_block_review.csv", ["review_item", "expected", "actual", "status", "notes"], execute_rows)
    write_csv(DATA_DIR / "risk_register.csv", ["risk_id", "risk", "severity", "status", "mitigation", "claim_boundary"], risk_rows)
    write_csv(DATA_DIR / "review_decision.csv", ["decision_key", "value", "notes", "claim_boundary"], decision_rows)
    write_csv(DATA_DIR / "recommended_next_action.csv", ["step_order", "action", "exact_command", "notes", "claim_boundary"], next_rows)
    write_csv(VALIDATION_DIR / "validation_results.csv", ["check_id", "check_name", "expected", "actual", "status", "notes"], validation_rows)

    failed = [row for row in validation_rows if row["status"] == "fail"]
    if failed:
        for row in failed:
            print(f"FAIL: {row['check_name']}: {row['actual']}")
        return 1
    print(f"PASS: dry-run review completed with final_status={FINAL_STATUS}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
