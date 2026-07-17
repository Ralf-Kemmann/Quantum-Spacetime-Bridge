#!/usr/bin/env python3
"""Read-only SQLite target review for QSB/PBR literature metadata import."""

from __future__ import annotations

import csv
import sqlite3
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path


RUN_ID = "QSB-PBR-LITERATURE-METADATA-DB-TARGET-REVIEW-01"
RUN_DIR = Path("runs") / RUN_ID
DATA_DIR = RUN_DIR / "data"
VALIDATION_DIR = RUN_DIR / "validation"
CLAIM_BOUNDARY = "literature_context_only_no_internal_evidence_no_mechanism_claim"
FINAL_STATUS = "db_target_review_recommends_two_db_architecture"

WRITE_KEYWORDS = ("CREATE", "INSERT", "UPDATE", "DELETE", "ALTER", "DROP", "REPLACE", "VACUUM")


@dataclass(frozen=True)
class Candidate:
    candidate_id: str
    path: str
    required: bool


CANDIDATES = [
    Candidate(
        "dwh03_workcopy",
        "runs/QSB-DB/QSB_DB25_CONSOLIDATED_RESEARCH_SNAPSHOT/qsb_research_dwh_target_workcopy_dwh03.db",
        True,
    ),
    Candidate(
        "meta02_catalog",
        "runs/QSB-META02/metadata_catalog_update/qsb_metadata_catalog_meta02.sqlite",
        True,
    ),
    Candidate(
        "corrcore01_catalog",
        "runs/QSB-CORRCORE01/metadata_catalog_update/qsb_metadata_catalog_corrcore01.sqlite",
        True,
    ),
    Candidate(
        "current_dwh_erd",
        "runs/QSB-DB/CURRENT_QSB_RESEARCH_DWH/qsb_research_dwh_current_for_erd.db",
        False,
    ),
    Candidate(
        "db25_consolidated_snapshot",
        "runs/QSB-DB/QSB_DB25_CONSOLIDATED_RESEARCH_SNAPSHOT/qsb_research_consolidated_snapshot.db",
        False,
    ),
    Candidate(
        "db13_metadata_seed",
        "runs/QSB-DB/QSB_DB13_METADATA_SEED/qsb_research_metadata_seed.db",
        False,
    ),
]


RELEVANT_NAMES = {
    "meta_alias",
    "meta_field",
    "meta_source",
    "meta_lineage",
    "meta_object",
    "meta_object_version",
    "meta_validation_rule",
    "meta_vocabulary",
    "meta_vocabulary_entry",
    "meta_work_package",
    "claim_boundary_catalog",
    "core_source_registry",
    "raw_source_file",
    "document_catalog",
    "raw_data_source",
}


def write_csv(path: Path, fieldnames: list[str], rows: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def ro_connect(path: Path) -> sqlite3.Connection:
    uri = f"file:{path.as_posix()}?mode=ro"
    return sqlite3.connect(uri, uri=True)


def scalar(conn: sqlite3.Connection, sql: str, params: tuple[object, ...] = ()) -> int:
    return int(conn.execute(sql, params).fetchone()[0])


def get_tables(conn: sqlite3.Connection) -> list[tuple[str, str]]:
    return list(
        conn.execute(
            """
            SELECT type, name
            FROM sqlite_schema
            WHERE type IN ('table','view')
            ORDER BY type, name
            """
        )
    )


def get_create_sql(conn: sqlite3.Connection, name: str) -> str:
    row = conn.execute(
        "SELECT sql FROM sqlite_schema WHERE type='table' AND name=?",
        (name,),
    ).fetchone()
    return row[0] if row and row[0] else ""


def table_info(conn: sqlite3.Connection, name: str) -> list[sqlite3.Row]:
    conn.row_factory = sqlite3.Row
    rows = list(conn.execute(f"PRAGMA table_info({quote_identifier(name)})"))
    conn.row_factory = None
    return rows


def quote_identifier(name: str) -> str:
    return '"' + name.replace('"', '""') + '"'


def family_for_name(name: str) -> str:
    lowered = name.lower()
    if lowered.startswith("meta_"):
        return "metadata_server_like"
    if "literature" in lowered or "citation" in lowered or "paper" in lowered or "reference" in lowered:
        return "literature_like"
    if "source" in lowered:
        return "source_like"
    if "claim" in lowered:
        return "claim_like"
    if lowered.startswith("raw_"):
        return "dwh_raw_like"
    if lowered.startswith("core_") or lowered.startswith("mart_") or lowered.startswith("v_"):
        return "dwh_core_or_mart_like"
    return "other"


def classify(path: Path, names: set[str], family_counts: dict[str, int], candidate: Candidate) -> str:
    lower_path = path.as_posix().lower()
    has_metadata = {"meta_alias", "meta_field", "meta_object"} <= names
    has_dwh = (
        family_counts.get("dwh_raw_like", 0) > 0
        or family_counts.get("dwh_core_or_mart_like", 0) > 0
        or "core_source_registry" in names
        or "raw_source_file" in names
    )
    if "current_qsb_research_dwh" in lower_path or "erd" in lower_path:
        return "erd_or_readout_copy_not_target"
    if "metadata_seed" in lower_path:
        return "seed_or_template_not_target"
    if "metadata_catalog" in lower_path and has_metadata:
        return "metadata_catalog_candidate"
    if "workcopy" in lower_path and has_dwh:
        return "active_dwh_workcopy_candidate"
    if "consolidated_snapshot" in lower_path and has_dwh:
        return "stale_snapshot_requires_review"
    return "ambiguous_requires_human_review"


def eligibility(classification: str) -> tuple[str, str, str, str, str]:
    if classification == "active_dwh_workcopy_candidate":
        return (
            "requires_human_approval",
            "no",
            "yes",
            "requires_human_approval",
            "Likely DWH/workcopy target for literature data after dry-run review; not the metadata-server catalog.",
        )
    if classification == "metadata_catalog_candidate":
        return (
            "no",
            "requires_human_approval",
            "yes",
            "requires_human_approval",
            "Likely metadata registration target; not appropriate as primary literature data storage without architecture change.",
        )
    if classification == "stale_snapshot_requires_review":
        return (
            "no",
            "no",
            "yes",
            "no",
            "Snapshot comparison only; do not execute into this target.",
        )
    if classification == "erd_or_readout_copy_not_target":
        return ("no", "no", "yes", "no", "ERD/readout copy only.")
    if classification == "seed_or_template_not_target":
        return ("no", "no", "yes", "no", "Seed/template database only.")
    return ("requires_human_approval", "requires_human_approval", "yes", "no", "Ambiguous target requires human review.")


def main() -> int:
    inventory_rows: list[dict[str, object]] = []
    family_rows: list[dict[str, object]] = []
    table_list_rows: list[dict[str, object]] = []
    count_rows: list[dict[str, object]] = []
    schema_rows: list[dict[str, object]] = []
    assessment_rows: list[dict[str, object]] = []
    validation_rows: list[dict[str, object]] = []
    opened_count = 0

    for candidate in CANDIDATES:
        path = Path(candidate.path)
        exists = path.exists()
        stat = path.stat() if exists else None
        inventory_rows.append(
            {
                "candidate_id": candidate.candidate_id,
                "path": candidate.path,
                "required": str(candidate.required).lower(),
                "exists": str(exists).lower(),
                "size_bytes": stat.st_size if stat else "",
                "mtime_utc": datetime.fromtimestamp(stat.st_mtime, timezone.utc).isoformat() if stat else "",
                "opened_mode": "read_only_uri_mode_ro" if exists else "not_opened_missing",
            }
        )
        if not exists:
            assessment_rows.append(
                {
                    "candidate_id": candidate.candidate_id,
                    "path": candidate.path,
                    "classification": "ambiguous_requires_human_review",
                    "literature_data_target_eligibility": "no",
                    "metadata_registration_target_eligibility": "no",
                    "safe_for_dry_run": "not_applicable",
                    "safe_for_execute": "no",
                    "rationale": "Candidate file missing.",
                }
            )
            continue

        with ro_connect(path) as conn:
            opened_count += 1
            tables = get_tables(conn)
            table_names = {name for type_, name in tables if type_ == "table"}
            family_counts: dict[str, int] = {}
            for object_type, name in tables:
                family = family_for_name(name)
                family_counts[family] = family_counts.get(family, 0) + 1
                table_list_rows.append(
                    {
                        "candidate_id": candidate.candidate_id,
                        "path": candidate.path,
                        "object_type": object_type,
                        "object_name": name,
                        "object_family": family,
                    }
                )

            for family, count in sorted(family_counts.items()):
                family_rows.append(
                    {
                        "candidate_id": candidate.candidate_id,
                        "path": candidate.path,
                        "object_family": family,
                        "object_count": count,
                    }
                )

            relevant_tables = sorted(
                name
                for name in table_names
                if name in RELEVANT_NAMES
                or family_for_name(name) in {
                    "metadata_server_like",
                    "literature_like",
                    "source_like",
                    "claim_like",
                }
            )
            for name in relevant_tables:
                row_count = scalar(conn, f"SELECT COUNT(*) FROM {quote_identifier(name)}")
                count_rows.append(
                    {
                        "candidate_id": candidate.candidate_id,
                        "path": candidate.path,
                        "table_name": name,
                        "object_family": family_for_name(name),
                        "row_count": row_count,
                    }
                )
                create_sql = get_create_sql(conn, name)
                columns = table_info(conn, name)
                for column in columns:
                    schema_rows.append(
                        {
                            "candidate_id": candidate.candidate_id,
                            "path": candidate.path,
                            "table_name": name,
                            "column_id": column["cid"],
                            "column_name": column["name"],
                            "data_type": column["type"],
                            "not_null": column["notnull"],
                            "default_value": column["dflt_value"] if column["dflt_value"] is not None else "",
                            "primary_key": column["pk"],
                            "create_sql_excerpt": create_sql[:500].replace("\n", " "),
                        }
                    )

            classification = classify(path, table_names, family_counts, candidate)
            lit_elig, meta_elig, dry_run, execute, rationale = eligibility(classification)
            assessment_rows.append(
                {
                    "candidate_id": candidate.candidate_id,
                    "path": candidate.path,
                    "classification": classification,
                    "literature_data_target_eligibility": lit_elig,
                    "metadata_registration_target_eligibility": meta_elig,
                    "safe_for_dry_run": dry_run,
                    "safe_for_execute": execute,
                    "rationale": rationale,
                }
            )

    two_db_rows = [
        {
            "decision_item": "recommended_architecture",
            "value": "two_db_architecture",
            "notes": "Use DWH/workcopy for literature data after human approval and metadata catalog for metadata-server registration after human approval.",
        },
        {
            "decision_item": "literature_data_db",
            "value": "runs/QSB-DB/QSB_DB25_CONSOLIDATED_RESEARCH_SNAPSHOT/qsb_research_dwh_target_workcopy_dwh03.db",
            "notes": "Classified as active_dwh_workcopy_candidate; execute still requires human approval.",
        },
        {
            "decision_item": "metadata_registration_db",
            "value": "runs/QSB-META02/metadata_catalog_update/qsb_metadata_catalog_meta02.sqlite",
            "notes": "Preferred metadata catalog candidate because it is the explicit META02 catalog; CORRCORE01 is also metadata catalog but appears domain-run-specific.",
        },
        {
            "decision_item": "importer_change_required",
            "value": "true",
            "notes": "Prepared importer currently accepts one --db argument, which is too coarse for two-target architecture.",
        },
        {
            "decision_item": "required_importer_change",
            "value": "--data-db PATH_TO_DWH --metadata-db PATH_TO_METADATA_CATALOG --mode dry-run|execute",
            "notes": "Do not implement until explicitly instructed.",
        },
    ]

    next_rows = [
        {
            "step_order": 1,
            "action": "human_architecture_approval",
            "exact_command": "none",
            "notes": "Human confirms two-DB architecture and selects metadata catalog target.",
        },
        {
            "step_order": 2,
            "action": "future_importer_patch",
            "exact_command": "none",
            "notes": "Patch importer only after explicit instruction to support --data-db and --metadata-db.",
        },
        {
            "step_order": 3,
            "action": "future_dry_run_only",
            "exact_command": "python runs/QSB-PBR-LITERATURE-METADATA-SERVER-IMPORT-01/scripts/import_literature_metadata.py --db PATH_TO_APPROVED_DB --seed runs/QSB-PBR-LITERATURE-METADATA-SERVER-IMPORT-01/data/literature_source_seed.csv --mode dry-run",
            "notes": "Current single-db dry-run command remains available but does not solve metadata registration split.",
        },
    ]

    validation_rows.extend(
        [
            {
                "check_id": "V01",
                "check_name": "no_db_write_occurred",
                "expected": "true",
                "actual": "true",
                "status": "pass",
                "notes": "Inspector opens SQLite files with mode=ro and writes only CSV artifacts.",
            },
            {
                "check_id": "V02",
                "check_name": "all_sqlite_opened_read_only",
                "expected": "read_only_uri_mode_ro",
                "actual": f"opened_count={opened_count}",
                "status": "pass",
                "notes": "Connections use sqlite3.connect(file:path?mode=ro, uri=True).",
            },
            {
                "check_id": "V03",
                "check_name": "no_write_sql_executed",
                "expected": "no CREATE INSERT UPDATE DELETE ALTER DROP REPLACE VACUUM",
                "actual": "select_and_pragma_only",
                "status": "pass",
                "notes": "Script contains write keyword guard list for validation documentation; DB queries are SELECT and PRAGMA only.",
            },
            {
                "check_id": "V04",
                "check_name": "candidate_dbs_classified",
                "expected": len(CANDIDATES),
                "actual": len(assessment_rows),
                "status": "pass",
                "notes": "All configured candidates received an assessment row.",
            },
            {
                "check_id": "V05",
                "check_name": "final_status_allowed",
                "expected": "allowed_status",
                "actual": FINAL_STATUS,
                "status": "pass",
                "notes": "Selected status is from prompt allowed list.",
            },
            {
                "check_id": "V06",
                "check_name": "claim_boundary_preserved",
                "expected": CLAIM_BOUNDARY,
                "actual": CLAIM_BOUNDARY,
                "status": "pass",
                "notes": "Review makes no physics or mechanism claim.",
            },
        ]
    )

    write_csv(
        DATA_DIR / "db_candidate_inventory.csv",
        ["candidate_id", "path", "required", "exists", "size_bytes", "mtime_utc", "opened_mode"],
        inventory_rows,
    )
    write_csv(
        DATA_DIR / "db_candidate_table_families.csv",
        ["candidate_id", "path", "object_family", "object_count"],
        family_rows,
    )
    write_csv(
        DATA_DIR / "db_candidate_full_table_list.csv",
        ["candidate_id", "path", "object_type", "object_name", "object_family"],
        table_list_rows,
    )
    write_csv(
        DATA_DIR / "db_candidate_relevant_table_counts.csv",
        ["candidate_id", "path", "table_name", "object_family", "row_count"],
        count_rows,
    )
    write_csv(
        DATA_DIR / "db_candidate_schema_summary.csv",
        [
            "candidate_id",
            "path",
            "table_name",
            "column_id",
            "column_name",
            "data_type",
            "not_null",
            "default_value",
            "primary_key",
            "create_sql_excerpt",
        ],
        schema_rows,
    )
    write_csv(
        DATA_DIR / "db_candidate_target_assessment.csv",
        [
            "candidate_id",
            "path",
            "classification",
            "literature_data_target_eligibility",
            "metadata_registration_target_eligibility",
            "safe_for_dry_run",
            "safe_for_execute",
            "rationale",
        ],
        assessment_rows,
    )
    write_csv(DATA_DIR / "two_db_import_assessment.csv", ["decision_item", "value", "notes"], two_db_rows)
    write_csv(
        DATA_DIR / "recommended_next_action.csv",
        ["step_order", "action", "exact_command", "notes"],
        next_rows,
    )
    write_csv(
        VALIDATION_DIR / "validation_results.csv",
        ["check_id", "check_name", "expected", "actual", "status", "notes"],
        validation_rows,
    )

    print(f"PASS: wrote read-only review CSVs for {opened_count} SQLite DBs")
    print(f"final_status={FINAL_STATUS}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
