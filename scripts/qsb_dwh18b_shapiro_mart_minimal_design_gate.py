#!/usr/bin/env python3
"""QSB-DWH18B: read-only minimal Shapiro-Mart design gate.

This script reads the current workcopy state and writes a small design-gate
artifact set. It does not create mart tables, does not update mappings, and
does not compute analysis quantities.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import sqlite3
import sys
from pathlib import Path
from typing import Any


SCRIPT_NAME = "scripts/qsb_dwh18b_shapiro_mart_minimal_design_gate.py"
DEFAULT_LIVE_DB = Path(
    "runs/QSB-DB/QSB_DB25_CONSOLIDATED_RESEARCH_SNAPSHOT/"
    "qsb_research_consolidated_snapshot.db"
)
DEFAULT_WORKCOPY_DB = Path(
    "runs/QSB-DB/QSB_DB25_CONSOLIDATED_RESEARCH_SNAPSHOT/"
    "qsb_research_dwh_target_workcopy_dwh03.db"
)
DEFAULT_OUTPUT_ROOT = Path("runs/QSB-DB/QSB_DB25_CONSOLIDATED_RESEARCH_SNAPSHOT")

READOUT_MD = "dwh18b_shapiro_mart_minimal_design_gate_readout.md"
SUMMARY_JSON = "dwh18b_shapiro_mart_minimal_design_gate_summary.json"
SUPPORTED_COMPONENT_CSV = "dwh18b_supported_component_inventory.csv"
OPEN_COMPOUND_CSV = "dwh18b_open_compound_label_boundary.csv"
REQUIREMENTS_CSV = "dwh18b_minimal_shapiro_mart_requirements.csv"
CANDIDATE_TABLE_CSV = "dwh18b_candidate_table_design.csv"
NEXT_STEPS_CSV = "dwh18b_next_dwh_steps.csv"

OUTPUT_FILENAMES = [
    READOUT_MD,
    SUMMARY_JSON,
    SUPPORTED_COMPONENT_CSV,
    OPEN_COMPOUND_CSV,
    REQUIREMENTS_CSV,
    CANDIDATE_TABLE_CSV,
    NEXT_STEPS_CSV,
]

REQUIRED_DWH15_VIEWS = [
    "qsb_v_dwh15a_supported_review_ready_candidates",
    "qsb_v_dwh15a_skipped_deferred_candidates",
]

REQUIRED_DWH14_VIEWS = [
    "qsb_v_dwh14a_supported_candidate_terms",
    "qsb_v_dwh14a_open_or_conflict_terms",
]

REQUIRED_DWH05_TABLES = [
    "raw_source_file",
    "raw_ingest_run",
    "raw_record",
    "raw_field_value",
    "core_observation",
    "core_observation_record_link",
]

REQUIRED_DWH06_TABLES = [
    "dim_science_object",
    "dim_telescope",
    "dim_receiver",
    "dim_backend",
    "dim_time_context",
    "dim_processing_context",
    "dim_quality_status",
]

REQUIRED_DWH08_TABLES = [
    "map_token_dictionary",
    "map_token_value_assertion",
    "map_assertion_evidence",
    "map_review_decision",
    "map_evidence_gap",
]

EXPECTED_SUPPORTED_COMPONENTS = ["GUPPI", "Rcvr_800", "Rcvr1_2"]
EXPECTED_OPEN_COMPOUNDS = ["Rcvr_800_GUPPI", "Rcvr1_2_GUPPI"]

SUPPORT_BOUNDARY = "Component support exists. Compound-label support remains open."
COMPOUND_ALLOWED_USE = (
    "may be shown as unresolved context label; must not be used as supported "
    "mapping key; must not drive result interpretation"
)
DESIGN_GATE_REASON = (
    "Design gate only; table creation requires explicit implementation step "
    "after human review."
)
CLAIM_BOUNDARY = (
    "DWH18B is a read-only design-gate note for a future Shapiro-Mart. It uses "
    "supported receiver/backend components only, keeps compound labels open, "
    "does not create mart or result tables, and does not make Bridge, Shapiro, "
    "or physics-result claims."
)


def quote_identifier(identifier: str) -> str:
    return '"' + identifier.replace('"', '""') + '"'


def output_paths(output_root: Path) -> dict[str, Path]:
    return {name: output_root / name for name in OUTPUT_FILENAMES}


def connect_readonly(path: Path) -> sqlite3.Connection:
    con = sqlite3.connect(f"file:{path.resolve()}?mode=ro", uri=True)
    con.row_factory = sqlite3.Row
    con.execute("PRAGMA foreign_keys = ON")
    return con


def fetch_dicts(
    con: sqlite3.Connection,
    sql: str,
    params: tuple[Any, ...] = (),
) -> list[dict[str, Any]]:
    return [dict(row) for row in con.execute(sql, params).fetchall()]


def object_exists(con: sqlite3.Connection, name: str, object_type: str) -> bool:
    row = con.execute(
        """
        SELECT 1
        FROM sqlite_master
        WHERE name = ?
          AND type = ?
        """,
        (name, object_type),
    ).fetchone()
    return row is not None


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def file_stat(path: Path) -> dict[str, Any]:
    stat = path.stat()
    return {
        "size_bytes": stat.st_size,
        "mtime_ns": stat.st_mtime_ns,
    }


def db_state(path: Path) -> dict[str, Any]:
    return {
        "sha256": file_sha256(path),
        "stat": file_stat(path),
    }


def integrity_check(con: sqlite3.Connection) -> str:
    row = con.execute("PRAGMA integrity_check").fetchone()
    return str(row[0]) if row else "no_result"


def foreign_key_violations(con: sqlite3.Connection) -> list[dict[str, Any]]:
    rows = con.execute("PRAGMA foreign_key_check").fetchall()
    return [
        {"table": row[0], "rowid": row[1], "parent": row[2], "fkid": row[3]}
        for row in rows
    ]


def fail(message: str) -> None:
    raise RuntimeError(message)


def ensure_inputs(args: argparse.Namespace) -> None:
    if not args.live_db.exists():
        fail(f"Live DB not found: {args.live_db}")
    if not args.workcopy_db.exists():
        fail(f"Workcopy DB not found: {args.workcopy_db}")
    if not args.output_root.exists():
        fail(f"Output root not found: {args.output_root}")
    if not args.output_root.is_dir():
        fail(f"Output root is not a directory: {args.output_root}")

    existing = [
        str(path)
        for path in output_paths(args.output_root).values()
        if path.exists()
    ]
    if existing and not args.overwrite:
        fail(
            "DWH18B output files already exist. Use --overwrite to replace: "
            + "; ".join(existing)
        )


def validate_required_objects(workcopy_con: sqlite3.Connection) -> dict[str, Any]:
    checks: list[dict[str, str]] = []
    missing: list[str] = []

    for name in REQUIRED_DWH15_VIEWS + REQUIRED_DWH14_VIEWS:
        exists = object_exists(workcopy_con, name, "view")
        checks.append({"object_name": name, "object_type": "view", "status": "exists" if exists else "missing"})
        if not exists:
            missing.append(f"view:{name}")

    for name in REQUIRED_DWH05_TABLES + REQUIRED_DWH06_TABLES + REQUIRED_DWH08_TABLES:
        exists = object_exists(workcopy_con, name, "table")
        checks.append({"object_name": name, "object_type": "table", "status": "exists" if exists else "missing"})
        if not exists:
            missing.append(f"table:{name}")

    if missing:
        fail("Missing required workcopy objects: " + "; ".join(missing))

    return {
        "object_checks": checks,
        "required_view_count": len(REQUIRED_DWH15_VIEWS + REQUIRED_DWH14_VIEWS),
        "required_table_count": len(REQUIRED_DWH05_TABLES + REQUIRED_DWH06_TABLES + REQUIRED_DWH08_TABLES),
    }


def load_supported_rows(workcopy_con: sqlite3.Connection) -> list[dict[str, Any]]:
    return fetch_dicts(
        workcopy_con,
        """
        SELECT
            s.token_position,
            s.term,
            s.dwh14a_decision_status,
            s.dwh14a_evidence_strength,
            s.new_review_status,
            h.proposed_role,
            h.reviewer_note
        FROM qsb_v_dwh15a_supported_review_ready_candidates AS s
        LEFT JOIN qsb_v_dwh14a_supported_candidate_terms AS h
          ON h.term = s.term
         AND h.token_position = s.token_position
        ORDER BY
            CASE s.term
              WHEN 'GUPPI' THEN 1
              WHEN 'Rcvr_800' THEN 2
              WHEN 'Rcvr1_2' THEN 3
              ELSE 99
            END,
            s.term
        """,
    )


def load_open_compound_rows(workcopy_con: sqlite3.Connection) -> list[dict[str, Any]]:
    return fetch_dicts(
        workcopy_con,
        """
        SELECT
            s.token_position,
            s.term,
            s.skip_reason,
            s.dwh14a_decision_status,
            s.dwh14a_evidence_strength,
            h.reviewer_note
        FROM qsb_v_dwh15a_skipped_deferred_candidates AS s
        LEFT JOIN qsb_v_dwh14a_open_or_conflict_terms AS h
          ON h.term = s.term
         AND h.token_position = s.token_position
        WHERE s.term IN ('Rcvr_800_GUPPI', 'Rcvr1_2_GUPPI')
        ORDER BY
            CASE s.term
              WHEN 'Rcvr_800_GUPPI' THEN 1
              WHEN 'Rcvr1_2_GUPPI' THEN 2
              ELSE 99
            END,
            s.term
        """,
    )


def build_supported_component_inventory(rows: list[dict[str, Any]]) -> list[dict[str, str]]:
    by_term = {str(row["term"]): row for row in rows}
    missing = [term for term in EXPECTED_SUPPORTED_COMPONENTS if term not in by_term]
    if missing:
        fail("Missing expected supported components from workcopy views: " + "; ".join(missing))

    inventory: list[dict[str, str]] = []
    for term in EXPECTED_SUPPORTED_COMPONENTS:
        row = by_term[term]
        inventory.append(
            {
                "component_term": term,
                "token_position": str(row["token_position"]),
                "component_role": str(row["proposed_role"] or "component_context_candidate"),
                "evidence_status": str(row["dwh14a_decision_status"]),
                "evidence_strength": str(row["dwh14a_evidence_strength"]),
                "review_ready_status": str(row["new_review_status"]),
                "usable_for_minimal_shapiro_mart": "yes_supported_component_context_only",
                "limitations": "Not a final physical assignment and not compound-label support.",
                "notes": str(row["reviewer_note"] or SUPPORT_BOUNDARY),
            }
        )
    return inventory


def build_open_compound_boundary(rows: list[dict[str, Any]]) -> list[dict[str, str]]:
    by_term = {str(row["term"]): row for row in rows}
    missing = [term for term in EXPECTED_OPEN_COMPOUNDS if term not in by_term]
    if missing:
        fail("Missing expected open compound labels from workcopy views: " + "; ".join(missing))

    boundary: list[dict[str, str]] = []
    for term in EXPECTED_OPEN_COMPOUNDS:
        row = by_term[term]
        boundary.append(
            {
                "compound_label": term,
                "token_position": str(row["token_position"]),
                "current_status": str(row["dwh14a_decision_status"]),
                "reason_not_used_as_supported_component": (
                    "Only separate component support is present; exact compound-label "
                    "support remains unresolved."
                ),
                "required_future_evidence": (
                    "Direct dataset, release, pipeline, file-format, local README, "
                    "or institutional metadata evidence for exact compound-label usage."
                ),
                "allowed_use_in_shapiro_mart": COMPOUND_ALLOWED_USE,
                "notes": str(row["reviewer_note"] or SUPPORT_BOUNDARY),
            }
        )
    return boundary


def build_minimal_requirements() -> list[dict[str, str]]:
    return [
        {
            "requirement_id": "DWH18B_REQ_001",
            "requirement_name": "Observation anchor",
            "requirement_type": "schema_anchor",
            "source_layer": "DWH05 core",
            "required_fields_or_tables": "core_observation; core_observation_record_link",
            "current_availability_status": "available_in_workcopy_schema",
            "minimum_needed_before_implementation": (
                "Human approval of observation selection and trace rules."
            ),
            "claim_boundary": "Anchor rows support provenance only.",
            "notes": "No mart table is created by DWH18B.",
        },
        {
            "requirement_id": "DWH18B_REQ_002",
            "requirement_name": "Raw signal record path",
            "requirement_type": "raw_record_trace",
            "source_layer": "DWH05 raw",
            "required_fields_or_tables": "raw_record; raw_field_value",
            "current_availability_status": "available_in_workcopy_schema",
            "minimum_needed_before_implementation": (
                "Define allowed raw record filters without reading raw TIM/PAR files."
            ),
            "claim_boundary": "Raw record trace is not an analysis result.",
            "notes": "DWH18B does not inspect raw source files.",
        },
        {
            "requirement_id": "DWH18B_REQ_003",
            "requirement_name": "Supported receiver/backend component context",
            "requirement_type": "supported_component_context",
            "source_layer": "DWH14_A/DWH15_A views",
            "required_fields_or_tables": "Rcvr_800; Rcvr1_2; GUPPI",
            "current_availability_status": "available_as_review_ready_supported_components",
            "minimum_needed_before_implementation": (
                "Use components only as receiver/backend context candidates."
            ),
            "claim_boundary": SUPPORT_BOUNDARY,
            "notes": "Component use must not promote compound labels.",
        },
        {
            "requirement_id": "DWH18B_REQ_004",
            "requirement_name": "Open compound-label boundary",
            "requirement_type": "mapping_boundary",
            "source_layer": "DWH14_A/DWH15_A views",
            "required_fields_or_tables": "Rcvr_800_GUPPI; Rcvr1_2_GUPPI",
            "current_availability_status": "open_deferred_in_workcopy_views",
            "minimum_needed_before_implementation": (
                "Keep exact compound labels unresolved unless direct evidence is added later."
            ),
            "claim_boundary": SUPPORT_BOUNDARY,
            "notes": COMPOUND_ALLOWED_USE,
        },
        {
            "requirement_id": "DWH18B_REQ_005",
            "requirement_name": "Mapping/evidence trace",
            "requirement_type": "audit_trace",
            "source_layer": "DWH08 plus DWH14_A/DWH15_A",
            "required_fields_or_tables": (
                "map_token_dictionary; map_token_value_assertion; "
                "map_assertion_evidence; map_review_decision; map_evidence_gap"
            ),
            "current_availability_status": "available_in_workcopy_schema",
            "minimum_needed_before_implementation": (
                "Define trace joins from future mart rows back to mapping/evidence state."
            ),
            "claim_boundary": "Traceability is not semantic finalization.",
            "notes": "No mapping status is updated by DWH18B.",
        },
        {
            "requirement_id": "DWH18B_REQ_006",
            "requirement_name": "Shapiro question context",
            "requirement_type": "future_record_selection_context",
            "source_layer": "DWH05/DWH06/DWH08",
            "required_fields_or_tables": (
                "future selection rules for records relevant to the ShapiroInfo question"
            ),
            "current_availability_status": "design_requirement_only",
            "minimum_needed_before_implementation": (
                "Specify selection criteria and exclusions before any mart build."
            ),
            "claim_boundary": "Question context is not a result.",
            "notes": "DWH18B defines the need, not the selection.",
        },
        {
            "requirement_id": "DWH18B_REQ_007",
            "requirement_name": "Analysis gate",
            "requirement_type": "analysis_boundary",
            "source_layer": "future mart/analysis layer",
            "required_fields_or_tables": "explicit no-result gate before analysis tables",
            "current_availability_status": "boundary_defined_by_DWH18B",
            "minimum_needed_before_implementation": (
                "Separate design approval from any later result or statistical workflow."
            ),
            "claim_boundary": "No residual/result computation yet.",
            "notes": "DWH18B creates no bridge/result tables.",
        },
        {
            "requirement_id": "DWH18B_REQ_008",
            "requirement_name": "Control/failure-mode requirement",
            "requirement_type": "control_design",
            "source_layer": "future mart/analysis layer",
            "required_fields_or_tables": (
                "future controls separating instrument/backend/receiver effects from "
                "candidate anomaly patterns"
            ),
            "current_availability_status": "design_requirement_only",
            "minimum_needed_before_implementation": (
                "Define control groups and failure modes before implementation."
            ),
            "claim_boundary": "Control design is not evidence of an anomaly.",
            "notes": "Required before any interpretive analysis step.",
        },
        {
            "requirement_id": "DWH18B_REQ_009",
            "requirement_name": "Audit/provenance requirement",
            "requirement_type": "provenance",
            "source_layer": "raw/core/mapping/evidence",
            "required_fields_or_tables": (
                "raw_source_file; raw_ingest_run; raw_record; core_observation; "
                "mapping/evidence identifiers"
            ),
            "current_availability_status": "available_in_workcopy_schema",
            "minimum_needed_before_implementation": (
                "Require every future mart row to trace to raw/core/mapping/evidence state."
            ),
            "claim_boundary": "Provenance is not proof of interpretation.",
            "notes": "Future mart rows should be auditable row-by-row.",
        },
        {
            "requirement_id": "DWH18B_REQ_010",
            "requirement_name": "Claim boundary",
            "requirement_type": "scientific_boundary",
            "source_layer": "DWH18B design gate",
            "required_fields_or_tables": "explicit claim-boundary field in future notes",
            "current_availability_status": "defined_in_DWH18B_outputs",
            "minimum_needed_before_implementation": (
                "Carry the boundary into any DWH19 skeleton or implementation task."
            ),
            "claim_boundary": "Mart design is not evidence of Bridge/Shapiro result.",
            "notes": CLAIM_BOUNDARY,
        },
    ]


def build_candidate_table_design() -> list[dict[str, str]]:
    table_specs = [
        (
            "mart_shapiro_observation_context",
            "Observation-level anchor for future Shapiro-Mart rows.",
            "mart_candidate",
            "mart_observation_context_id; observation_id",
            "core_observation; core_observation_record_link; DWH06 dimensions",
        ),
        (
            "mart_shapiro_signal_record_selection",
            "Future record-selection layer for relevant signal records.",
            "mart_candidate",
            "mart_signal_record_selection_id; raw_record_id; observation_id",
            "raw_record; raw_field_value; core_observation_record_link",
        ),
        (
            "mart_shapiro_supported_component_context",
            "Receiver/backend component context using supported components only.",
            "mart_candidate",
            "mart_component_context_id; observation_id; component_term",
            "qsb_v_dwh15a_supported_review_ready_candidates; DWH14_A supported view",
        ),
        (
            "mart_shapiro_open_mapping_boundary",
            "Explicit unresolved compound-label boundary for future mart consumers.",
            "mart_candidate",
            "mart_open_boundary_id; compound_label",
            "qsb_v_dwh15a_skipped_deferred_candidates; DWH14_A open/conflict view",
        ),
        (
            "mart_shapiro_analysis_plan",
            "Human-approved analysis plan placeholder before any result workflow.",
            "mart_candidate",
            "mart_analysis_plan_id; plan_status",
            "DWH18B requirements; future human review decision",
        ),
        (
            "mart_shapiro_control_requirement",
            "Future control and failure-mode specification table.",
            "mart_candidate",
            "mart_control_requirement_id; control_requirement_name",
            "DWH18B requirements; future control design inputs",
        ),
        (
            "mart_shapiro_result_placeholder",
            "Explicit placeholder showing that no results are created at this gate.",
            "mart_candidate",
            "mart_result_placeholder_id; result_status",
            "future explicit implementation task only",
        ),
    ]

    return [
        {
            "proposed_table_name": name,
            "table_purpose": purpose,
            "layer": layer,
            "key_fields": key_fields,
            "source_dependencies": dependencies,
            "create_now": "no",
            "reason_not_created_now": DESIGN_GATE_REASON,
            "notes": "Proposed only; no table/view is created by DWH18B.",
        }
        for name, purpose, layer, key_fields, dependencies in table_specs
    ]


def build_next_steps() -> list[dict[str, str]]:
    return [
        {
            "option_id": "DWH19_A",
            "option_name": "Human review of Shapiro-Mart minimal requirements",
            "recommended_order": "1",
            "requires_db_write": "no",
            "notes": "Recommended next step before any mart skeleton is created.",
        },
        {
            "option_id": "DWH19_B",
            "option_name": "Create Shapiro-Mart skeleton tables only after requirements approval",
            "recommended_order": "2",
            "requires_db_write": "yes_after_explicit_approval",
            "notes": "Would require a separate implementation task.",
        },
        {
            "option_id": "DWH19_C",
            "option_name": "Refine compound-label evidence before mart implementation",
            "recommended_order": "3",
            "requires_db_write": "possible_after_explicit_approval",
            "notes": "Keeps compound labels open until direct support is reviewed.",
        },
        {
            "option_id": "DWH19_D",
            "option_name": "Pause DWH build and write architecture checkpoint note",
            "recommended_order": "4",
            "requires_db_write": "no",
            "notes": "Useful if the project needs a narrative checkpoint before DWH19.",
        },
    ]


def write_csv(path: Path, rows: list[dict[str, str]], fieldnames: list[str]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, extrasaction="raise")
        writer.writeheader()
        writer.writerows(rows)


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.write_text(json.dumps(payload, ensure_ascii=True, indent=2) + "\n", encoding="utf-8")


def write_readout(
    path: Path,
    summary: dict[str, Any],
    supported_rows: list[dict[str, str]],
    open_rows: list[dict[str, str]],
    requirement_rows: list[dict[str, str]],
    candidate_table_rows: list[dict[str, str]],
) -> None:
    supported_terms = ", ".join(row["component_term"] for row in supported_rows)
    open_terms = ", ".join(row["compound_label"] for row in open_rows)
    candidate_tables = ", ".join(row["proposed_table_name"] for row in candidate_table_rows)
    lines = [
        "# QSB-DWH18B Shapiro-Mart Minimal Design Gate Readout",
        "",
        "## 1. Executive summary",
        "",
        (
            "Befund: DWH18B defines minimal design requirements for a future "
            "Shapiro-Mart using supported components only."
        ),
        "",
        f"- Supported components: {supported_terms}",
        f"- Open compound labels: {open_terms}",
        f"- Minimal requirement rows: {len(requirement_rows)}",
        f"- Candidate table designs proposed: {len(candidate_table_rows)}",
        "",
        "## 2. Read-only design-gate principle",
        "",
        (
            "DWH18B opens both databases read-only and writes only external "
            "readout/CSV/JSON artifacts. It is not a mart implementation, "
            "migration, mapping update, or analysis step."
        ),
        "",
        "## 3. Live/workcopy protection result",
        "",
        f"- Live DB: `{summary['paths']['live_db']}`",
        f"- Workcopy DB: `{summary['paths']['workcopy_db']}`",
        f"- Live integrity_check: {summary['validation']['live_integrity_check']}",
        f"- Live foreign-key violations: {summary['validation']['live_foreign_key_violation_count']}",
        f"- Workcopy integrity_check: {summary['validation']['workcopy_integrity_check']}",
        f"- Workcopy foreign-key violations: {summary['validation']['workcopy_foreign_key_violation_count']}",
        f"- Live DB checksum/stat unchanged: {summary['validation']['live_db_unchanged']}",
        f"- Workcopy DB checksum/stat unchanged: {summary['validation']['workcopy_db_unchanged']}",
        "",
        "## 4. Supported components available for future Shapiro-Mart",
        "",
    ]
    for row in supported_rows:
        lines.append(
            "- {component_term}: token={token_position}; role={component_role}; "
            "status={evidence_status}; strength={evidence_strength}; "
            "review={review_ready_status}; use={usable_for_minimal_shapiro_mart}".format(**row)
        )
    lines.extend(
        [
            "",
            "## 5. Open compound-label boundary",
            "",
            SUPPORT_BOUNDARY,
            "",
        ]
    )
    for row in open_rows:
        lines.append(
            "- {compound_label}: token={token_position}; status={current_status}; "
            "allowed_use={allowed_use_in_shapiro_mart}".format(**row)
        )
    lines.extend(
        [
            "",
            "## 6. Minimal Shapiro-Mart requirements",
            "",
        ]
    )
    for row in requirement_rows:
        lines.append(
            "- {requirement_id}: {requirement_name}; type={requirement_type}; "
            "status={current_availability_status}".format(**row)
        )
    lines.extend(
        [
            "",
            "## 7. Candidate table design, not created yet",
            "",
            f"Candidate tables proposed but not created: {candidate_tables}",
            "",
        ]
    )
    for row in candidate_table_rows:
        lines.append(
            "- {proposed_table_name}: create_now={create_now}; reason={reason_not_created_now}".format(**row)
        )
    lines.extend(
        [
            "",
            "## 8. What DWH18_B does not do",
            "",
            (
                "DWH18B does not modify either DB, does not read raw TIM/PAR files, "
                "does not ingest or migrate data, does not update mapping statuses, "
                "does not create Shapiro-Mart tables, does not create bridge/result "
                "tables, does not assign final TIM-column meaning, and does not "
                "compute TOAs, delays, model quantities, residuals, or statistics."
            ),
            "",
            "## 9. Recommended DWH19 options",
            "",
            "- Option A: human review of Shapiro-Mart minimal requirements",
            "- Option B: create Shapiro-Mart skeleton tables only after requirements approval",
            "- Option C: refine compound-label evidence before mart implementation",
            "- Option D: pause DWH build and write architecture checkpoint note",
            "",
            "## 10. Claim boundary",
            "",
            CLAIM_BOUNDARY,
            "",
        ]
    )
    path.write_text("\n".join(lines), encoding="utf-8")


def run(args: argparse.Namespace) -> dict[str, Any]:
    ensure_inputs(args)

    live_before = db_state(args.live_db)
    workcopy_before = db_state(args.workcopy_db)

    with connect_readonly(args.live_db) as live_con, connect_readonly(args.workcopy_db) as workcopy_con:
        live_integrity = integrity_check(live_con)
        live_fk = foreign_key_violations(live_con)
        workcopy_integrity = integrity_check(workcopy_con)
        workcopy_fk = foreign_key_violations(workcopy_con)

        if live_integrity != "ok":
            fail(f"Live DB integrity_check failed: {live_integrity}")
        if live_fk:
            fail(f"Live DB foreign-key violations: {len(live_fk)}")
        if workcopy_integrity != "ok":
            fail(f"Workcopy DB integrity_check failed: {workcopy_integrity}")
        if workcopy_fk:
            fail(f"Workcopy DB foreign-key violations: {len(workcopy_fk)}")

        object_validation = validate_required_objects(workcopy_con)
        supported_source_rows = load_supported_rows(workcopy_con)
        open_compound_source_rows = load_open_compound_rows(workcopy_con)

    supported_rows = build_supported_component_inventory(supported_source_rows)
    open_rows = build_open_compound_boundary(open_compound_source_rows)
    requirement_rows = build_minimal_requirements()
    candidate_table_rows = build_candidate_table_design()
    next_step_rows = build_next_steps()

    live_after_prewrite = db_state(args.live_db)
    workcopy_after_prewrite = db_state(args.workcopy_db)
    if live_before != live_after_prewrite:
        fail("Live DB changed before output writing.")
    if workcopy_before != workcopy_after_prewrite:
        fail("Workcopy DB changed before output writing.")

    paths = output_paths(args.output_root)
    summary: dict[str, Any] = {
        "script_name": SCRIPT_NAME,
        "task": "QSB-DWH18_B",
        "mode": "read_only_minimal_design_gate",
        "paths": {
            "live_db": str(args.live_db),
            "workcopy_db": str(args.workcopy_db),
            "output_root": str(args.output_root),
        },
        "validation": {
            "live_integrity_check": live_integrity,
            "live_foreign_key_violation_count": len(live_fk),
            "workcopy_integrity_check": workcopy_integrity,
            "workcopy_foreign_key_violation_count": len(workcopy_fk),
            "live_db_unchanged": True,
            "workcopy_db_unchanged": True,
            "required_objects": object_validation,
        },
        "counts": {
            "supported_component_count": len(supported_rows),
            "open_compound_label_count": len(open_rows),
            "minimal_requirement_count": len(requirement_rows),
            "candidate_table_design_count": len(candidate_table_rows),
            "next_step_count": len(next_step_rows),
        },
        "supported_components": supported_rows,
        "open_compound_label_boundary": open_rows,
        "minimal_requirements": requirement_rows,
        "candidate_table_designs": candidate_table_rows,
        "recommended_next_option": "DWH19_A",
        "claim_boundary": CLAIM_BOUNDARY,
        "warnings": [
            "Compound labels remain open and must not be used as supported mapping keys.",
            "DWH18B creates output files only; it does not create mart tables.",
        ],
    }

    write_csv(
        paths[SUPPORTED_COMPONENT_CSV],
        supported_rows,
        [
            "component_term",
            "token_position",
            "component_role",
            "evidence_status",
            "evidence_strength",
            "review_ready_status",
            "usable_for_minimal_shapiro_mart",
            "limitations",
            "notes",
        ],
    )
    write_csv(
        paths[OPEN_COMPOUND_CSV],
        open_rows,
        [
            "compound_label",
            "token_position",
            "current_status",
            "reason_not_used_as_supported_component",
            "required_future_evidence",
            "allowed_use_in_shapiro_mart",
            "notes",
        ],
    )
    write_csv(
        paths[REQUIREMENTS_CSV],
        requirement_rows,
        [
            "requirement_id",
            "requirement_name",
            "requirement_type",
            "source_layer",
            "required_fields_or_tables",
            "current_availability_status",
            "minimum_needed_before_implementation",
            "claim_boundary",
            "notes",
        ],
    )
    write_csv(
        paths[CANDIDATE_TABLE_CSV],
        candidate_table_rows,
        [
            "proposed_table_name",
            "table_purpose",
            "layer",
            "key_fields",
            "source_dependencies",
            "create_now",
            "reason_not_created_now",
            "notes",
        ],
    )
    write_csv(
        paths[NEXT_STEPS_CSV],
        next_step_rows,
        [
            "option_id",
            "option_name",
            "recommended_order",
            "requires_db_write",
            "notes",
        ],
    )
    write_json(paths[SUMMARY_JSON], summary)
    write_readout(paths[READOUT_MD], summary, supported_rows, open_rows, requirement_rows, candidate_table_rows)

    live_after = db_state(args.live_db)
    workcopy_after = db_state(args.workcopy_db)
    summary["validation"]["live_db_unchanged"] = live_before == live_after
    summary["validation"]["workcopy_db_unchanged"] = workcopy_before == workcopy_after
    summary["validation"]["live_db_state_before"] = live_before
    summary["validation"]["live_db_state_after"] = live_after
    summary["validation"]["workcopy_db_state_before"] = workcopy_before
    summary["validation"]["workcopy_db_state_after"] = workcopy_after

    if not summary["validation"]["live_db_unchanged"]:
        fail("Live DB changed during DWH18B run.")
    if not summary["validation"]["workcopy_db_unchanged"]:
        fail("Workcopy DB changed during DWH18B run.")

    write_json(paths[SUMMARY_JSON], summary)
    write_readout(paths[READOUT_MD], summary, supported_rows, open_rows, requirement_rows, candidate_table_rows)

    return {
        "output_files": {name: str(path) for name, path in paths.items()},
        "summary": summary,
    }


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Create QSB-DWH18B read-only Shapiro-Mart minimal design-gate "
            "outputs from existing workcopy DB state."
        )
    )
    parser.add_argument("--live-db", type=Path, default=DEFAULT_LIVE_DB)
    parser.add_argument("--workcopy-db", type=Path, default=DEFAULT_WORKCOPY_DB)
    parser.add_argument("--output-root", type=Path, default=DEFAULT_OUTPUT_ROOT)
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Replace existing DWH18B output files.",
    )
    return parser.parse_args(argv)


def main(argv: list[str]) -> int:
    args = parse_args(argv)
    try:
        result = run(args)
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    summary = result["summary"]
    print("QSB-DWH18B read-only design gate complete.")
    print(f"Supported components: {summary['counts']['supported_component_count']}")
    print(f"Open compound labels: {summary['counts']['open_compound_label_count']}")
    print(f"Minimal requirements: {summary['counts']['minimal_requirement_count']}")
    print(f"Candidate table designs: {summary['counts']['candidate_table_design_count']}")
    print(f"Live DB unchanged: {summary['validation']['live_db_unchanged']}")
    print(f"Workcopy DB unchanged: {summary['validation']['workcopy_db_unchanged']}")
    print(f"Output root: {summary['paths']['output_root']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
