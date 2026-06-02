#!/usr/bin/env python3
"""QSB-DB26: mapping-gap triage and field-dictionary seed.

This is a DB-first consolidated Mini-DWH step. It uses the DB25 SQLite
consolidated snapshot as the only data substrate, creates a timestamped backup
before DB writes, and then adds DB26-prefixed tables and views in place. The
step records structural mapping triage and conservative field-dictionary seed
rows. It does not read raw source files, does not create a new analysis DB, and
does not assign final semantic or physical meaning to TIM token positions.
"""

from __future__ import annotations

import argparse
import csv
import json
import re
import shutil
import sqlite3
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


SCRIPT_NAME = "scripts/qsb_db26_mapping_gap_triage_field_dictionary_seed.py"
DEFAULT_DB = Path(
    "runs/QSB-DB/QSB_DB25_CONSOLIDATED_RESEARCH_SNAPSHOT/"
    "qsb_research_consolidated_snapshot.db"
)
DEFAULT_OUTPUT_ROOT = Path("runs/QSB-DB/QSB_DB25_CONSOLIDATED_RESEARCH_SNAPSHOT")

REQUIRED_DB25_VIEWS = [
    "qsb_v_db25_current_measurement_reality_dashboard",
    "qsb_v_db25_tim_staging_and_mapping_overview",
    "qsb_v_db25_two_block_signature_overview",
    "qsb_v_db25_report_ready_snapshot",
]

REQUIRED_SOURCE_OBJECTS = [
    "db23_tim_mapping_gap",
    "db23_tim_staging_field_map",
    "db23_tim_token_role_candidate",
    "qsb_v_db23a_41_candidate_grouping_tokens",
    "qsb_v_db23a_41_token_position_profile",
    "qsb_v_db23b_token_block_comparison",
]

OUTPUT_FILENAMES = [
    "db26_mapping_gap_triage_readout.md",
    "db26_mapping_gap_triage_summary.json",
    "db26_mapping_gap_triage.csv",
    "db26_field_dictionary_seed.csv",
    "db26_side_by_side_block_tokens.csv",
]

FOCUS_TOKEN_POSITIONS = [7, 11, 13, 17, 23]
FOCUS_TOKEN_SET = set(FOCUS_TOKEN_POSITIONS)

CLAIM_BOUNDARY = (
    "DB26 is an additive metadata and data-modeling step over DB25. It records "
    "structural mapping triage and conservative dictionary seeds only. No raw "
    "TIM/PAR file is read; no timing quantities, delays, residual quantities, "
    "model quantities, inferential-statistics work, final TIM-column semantics, "
    "or physical interpretation is produced."
)


def utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def timestamp_for_path() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def pretty_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=True, indent=2)


def connect_db(path: Path) -> sqlite3.Connection:
    con = sqlite3.connect(path)
    con.row_factory = sqlite3.Row
    con.execute("PRAGMA foreign_keys = ON")
    return con


def connect_readonly(path: Path) -> sqlite3.Connection:
    con = sqlite3.connect(f"file:{path.resolve()}?mode=ro", uri=True)
    con.row_factory = sqlite3.Row
    return con


def fetch_dicts(
    con: sqlite3.Connection,
    sql: str,
    params: tuple[Any, ...] = (),
) -> list[dict[str, Any]]:
    return [dict(row) for row in con.execute(sql, params).fetchall()]


def object_exists(con: sqlite3.Connection, name: str, object_type: str | None = None) -> bool:
    if object_type is None:
        row = con.execute(
            """
            SELECT 1
            FROM sqlite_master
            WHERE name = ?
              AND type IN ('table', 'view')
            """,
            (name,),
        ).fetchone()
    else:
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


def list_db26_objects(con: sqlite3.Connection) -> list[tuple[str, str]]:
    rows = con.execute(
        """
        SELECT type, name
        FROM sqlite_master
        WHERE name LIKE 'db26_%'
           OR name LIKE 'qsb_v_db26_%'
        ORDER BY type, name
        """
    ).fetchall()
    return [(str(row["type"]), str(row["name"])) for row in rows]


def output_paths(output_root: Path) -> dict[str, Path]:
    return {name: output_root / name for name in OUTPUT_FILENAMES}


def ensure_preconditions(db_path: Path, output_root: Path) -> None:
    if not db_path.exists():
        raise FileNotFoundError(f"DB25 database does not exist: {db_path}")
    if not db_path.is_file():
        raise ValueError(f"DB25 path is not a file: {db_path}")
    if not output_root.exists():
        raise FileNotFoundError(f"Output root does not exist: {output_root}")
    if not output_root.is_dir():
        raise ValueError(f"Output root is not a directory: {output_root}")
    if not db_path.parent.resolve() == output_root.resolve():
        raise ValueError("Output root must be the DB25 consolidated snapshot directory.")
    if not db_path.stat().st_size > 0:
        raise ValueError(f"DB25 database is empty: {db_path}")

    with connect_readonly(db_path) as con:
        missing_views = [
            view for view in REQUIRED_DB25_VIEWS
            if not object_exists(con, view, "view")
        ]
        if missing_views:
            raise RuntimeError(
                "Required DB25 view(s) missing: " + ", ".join(missing_views)
            )

        missing_sources = [
            name for name in REQUIRED_SOURCE_OBJECTS
            if not object_exists(con, name)
        ]
        if missing_sources:
            raise RuntimeError(
                "Required DB25 source object(s) missing: " + ", ".join(missing_sources)
            )

        existing_db26 = list_db26_objects(con)
        if existing_db26:
            formatted = ", ".join(f"{kind}:{name}" for kind, name in existing_db26)
            raise RuntimeError("Refusing to run because DB26 objects already exist: " + formatted)

    existing_outputs = [
        str(path) for path in output_paths(output_root).values()
        if path.exists()
    ]
    if existing_outputs:
        raise FileExistsError(
            "Refusing to overwrite existing DB26 output file(s): "
            + "; ".join(existing_outputs)
        )


def create_backup(db_path: Path) -> Path:
    backup_path = db_path.with_name(
        f"{db_path.stem}.pre_db26_{timestamp_for_path()}.bak.db"
    )
    if backup_path.exists():
        raise FileExistsError(f"Backup path already exists: {backup_path}")
    shutil.copy2(db_path, backup_path)
    return backup_path


def token_position_label(token_position: Any, field_name: Any = None) -> str | None:
    if token_position is None:
        return None
    try:
        position_int = int(token_position)
    except (TypeError, ValueError):
        text = str(token_position).strip()
        return text or None
    if position_int == 0:
        return "raw_line_text"
    return f"tim_token_{position_int:03d}"


def numeric_position(token_position: Any) -> int | None:
    if token_position is None:
        return None
    try:
        return int(token_position)
    except (TypeError, ValueError):
        match = re.search(r"(\d+)$", str(token_position))
        if match:
            return int(match.group(1))
    return None


def sanitize_fragment(value: str | None) -> str:
    if value is None or value == "":
        return "unknown"
    cleaned = re.sub(r"[^A-Za-z0-9]+", "_", value.strip().lower())
    cleaned = re.sub(r"_+", "_", cleaned).strip("_")
    return cleaned or "unknown"


def proposed_structural_name(
    line_family: str | None,
    token_position: Any,
    field_name: str | None,
    structural_role_candidate: str,
) -> str:
    position_int = numeric_position(token_position)
    if field_name == "raw_line_text" or position_int == 0:
        return f"db26_audit_raw_line_{sanitize_fragment(line_family)}"
    if position_int is None:
        return f"db26_candidate_{sanitize_fragment(field_name)}"
    token_label = f"tim_token_{position_int:03d}"
    if structural_role_candidate == "context_token":
        return f"db26_context_{token_label}"
    if structural_role_candidate == "block_switch_token":
        return f"db26_block_switch_{token_label}"
    if structural_role_candidate == "stable_token":
        return f"db26_stable_{token_label}"
    if structural_role_candidate == "low_variance_token":
        return f"db26_low_variance_{token_label}"
    return f"db26_candidate_{token_label}"


def severity_to_priority(severity: str | None) -> str:
    if severity == "high":
        return "high"
    if severity == "medium":
        return "medium"
    return "low"


def create_tables_and_views(con: sqlite3.Connection) -> None:
    con.executescript(
        """
        CREATE TABLE db26_mapping_run_log (
            run_id TEXT PRIMARY KEY,
            run_timestamp_utc TEXT,
            input_db_path TEXT,
            backup_db_path TEXT,
            script_name TEXT,
            operation_mode TEXT,
            row_count_inserted INTEGER,
            foreign_key_violation_count INTEGER,
            notes TEXT
        );

        CREATE TABLE db26_mapping_gap_triage (
            triage_id TEXT PRIMARY KEY,
            source_gap_type TEXT,
            line_family TEXT,
            token_position TEXT,
            source_field_name TEXT,
            gap_severity TEXT,
            triage_status TEXT,
            evidence_summary TEXT,
            recommended_next_action TEXT,
            created_at_utc TEXT,
            CHECK (gap_severity IN ('info', 'low', 'medium', 'high') OR gap_severity IS NULL),
            CHECK (
                triage_status IN (
                    'immediate_context_only',
                    'needs_manual_mapping',
                    'candidate_for_dictionary_seed',
                    'retained_for_audit',
                    'unknown'
                )
            )
        );

        CREATE TABLE db26_field_dictionary_seed (
            dictionary_seed_id TEXT PRIMARY KEY,
            line_family TEXT,
            token_position TEXT,
            proposed_structural_name TEXT,
            structural_role_candidate TEXT,
            mapping_status TEXT,
            evidence_source TEXT,
            evidence_summary TEXT,
            manual_review_required INTEGER,
            confidence_class TEXT,
            created_at_utc TEXT,
            CHECK (
                structural_role_candidate IN (
                    'audit_raw_line',
                    'context_token',
                    'stable_token',
                    'low_variance_token',
                    'variable_token',
                    'block_switch_token',
                    'candidate_grouping_token',
                    'needs_manual_mapping',
                    'unknown'
                )
            ),
            CHECK (
                mapping_status IN (
                    'seed_only',
                    'needs_manual_mapping',
                    'context_only',
                    'ready_for_staging_name_proposal',
                    'blocked_by_missing_dictionary',
                    'retained_for_audit'
                )
            ),
            CHECK (manual_review_required IN (0, 1)),
            CHECK (confidence_class IN ('low', 'medium', 'high'))
        );

        CREATE TABLE db26_side_by_side_block_token_context (
            side_by_side_id TEXT PRIMARY KEY,
            token_position TEXT,
            block_a_value TEXT,
            block_b_value TEXT,
            relation_type TEXT,
            block_a_count INTEGER,
            block_b_count INTEGER,
            structural_role_candidate TEXT,
            evidence_summary TEXT,
            created_at_utc TEXT,
            CHECK (
                relation_type IN (
                    'equal',
                    'different',
                    'partial_overlap',
                    'mixed',
                    'needs_mapping'
                )
            )
        );

        CREATE TABLE db26_mapping_decision_candidate (
            decision_candidate_id TEXT PRIMARY KEY,
            candidate_type TEXT,
            related_token_position TEXT,
            related_line_family TEXT,
            decision_status TEXT,
            rationale TEXT,
            created_at_utc TEXT,
            CHECK (
                candidate_type IN (
                    'dictionary_seed',
                    'block_switch_context',
                    'manual_mapping',
                    'audit_retention'
                )
            ),
            CHECK (
                decision_status IN (
                    'proposed',
                    'needs_review',
                    'accepted_later',
                    'rejected_later'
                )
            )
        );

        CREATE TABLE db26_open_manual_mapping_queue (
            queue_id TEXT PRIMARY KEY,
            queue_type TEXT,
            priority TEXT,
            token_position TEXT,
            line_family TEXT,
            issue_summary TEXT,
            required_decision TEXT,
            blocking_status TEXT,
            created_at_utc TEXT,
            CHECK (
                queue_type IN (
                    'mapping_gap',
                    'block_switch_token',
                    'staging_name_needed',
                    'dictionary_needed'
                )
            ),
            CHECK (priority IN ('low', 'medium', 'high')),
            CHECK (
                blocking_status IN (
                    'blocks_staging',
                    'does_not_block_staging',
                    'blocks_analysis_only',
                    'unknown'
                )
            )
        );

        CREATE VIEW qsb_v_db26_mapping_gap_triage AS
        SELECT *
        FROM db26_mapping_gap_triage;

        CREATE VIEW qsb_v_db26_field_dictionary_seed AS
        SELECT *
        FROM db26_field_dictionary_seed;

        CREATE VIEW qsb_v_db26_side_by_side_block_token_context AS
        SELECT *
        FROM db26_side_by_side_block_token_context;

        CREATE VIEW qsb_v_db26_open_manual_mapping_queue AS
        SELECT *
        FROM db26_open_manual_mapping_queue;

        CREATE VIEW qsb_v_db26_mapping_dashboard AS
        SELECT 'run_id' AS metric_name,
               run_id AS metric_value,
               'db26_mapping_run_log' AS metric_source,
               notes AS dashboard_note
        FROM db26_mapping_run_log
        UNION ALL
        SELECT 'mapping_gap_triage_rows',
               CAST(COUNT(*) AS TEXT),
               'db26_mapping_gap_triage',
               'All DB23 mapping gaps carried into DB26 triage.'
        FROM db26_mapping_gap_triage
        UNION ALL
        SELECT 'candidate_for_dictionary_seed_rows',
               CAST(COUNT(*) AS TEXT),
               'db26_mapping_gap_triage',
               'Mapping gaps that are structurally ready for conservative seed names.'
        FROM db26_mapping_gap_triage
        WHERE triage_status = 'candidate_for_dictionary_seed'
        UNION ALL
        SELECT 'field_dictionary_seed_rows',
               CAST(COUNT(*) AS TEXT),
               'db26_field_dictionary_seed',
               'Conservative structural dictionary seed rows.'
        FROM db26_field_dictionary_seed
        UNION ALL
        SELECT 'manual_review_dictionary_seed_rows',
               CAST(COUNT(*) AS TEXT),
               'db26_field_dictionary_seed',
               'Dictionary seed rows requiring manual review before semantic use.'
        FROM db26_field_dictionary_seed
        WHERE manual_review_required = 1
        UNION ALL
        SELECT 'focused_block_switch_token_rows',
               CAST(COUNT(*) AS TEXT),
               'db26_side_by_side_block_token_context',
               'Focused two-block token context rows.'
        FROM db26_side_by_side_block_token_context
        UNION ALL
        SELECT 'open_manual_mapping_queue_rows',
               CAST(COUNT(*) AS TEXT),
               'db26_open_manual_mapping_queue',
               'Open mapping gaps plus focused two-block switch tokens.'
        FROM db26_open_manual_mapping_queue
        UNION ALL
        SELECT 'foreign_key_violation_count',
               CAST(foreign_key_violation_count AS TEXT),
               'PRAGMA foreign_key_check',
               'SQLite foreign-key check result after DB26 insertions.'
        FROM db26_mapping_run_log;

        CREATE VIEW qsb_v_db26_next_mapping_questions AS
        SELECT
            ROW_NUMBER() OVER (
                ORDER BY
                    CASE priority
                        WHEN 'high' THEN 1
                        WHEN 'medium' THEN 2
                        ELSE 3
                    END,
                    line_family,
                    token_position,
                    queue_id
            ) AS question_rank,
            queue_type AS question_scope,
            token_position,
            line_family,
            issue_summary AS question_text,
            required_decision,
            priority,
            'db26_open_manual_mapping_queue' AS source_object
        FROM db26_open_manual_mapping_queue;
        """
    )


def build_gap_triage(con: sqlite3.Connection, created_at: str) -> list[dict[str, Any]]:
    staging_rows = fetch_dicts(
        con,
        """
        SELECT line_type_scope, token_position, field_name, mapping_status,
               candidate_role_label, present_count, coverage_fraction
        FROM db23_tim_staging_field_map
        """,
    )
    staging_by_key = {
        (
            row["line_type_scope"],
            row["token_position"],
            row["field_name"],
        ): row
        for row in staging_rows
    }

    gap_rows = fetch_dicts(
        con,
        """
        SELECT gap_scope, line_type_scope, token_position, field_name,
               gap_type, gap_severity, gap_note, recommended_next_action,
               supporting_count
        FROM db23_tim_mapping_gap
        ORDER BY
            CASE gap_severity
                WHEN 'high' THEN 1
                WHEN 'medium' THEN 2
                WHEN 'low' THEN 3
                ELSE 4
            END,
            line_type_scope,
            token_position,
            gap_type
        """,
    )
    triage_rows: list[dict[str, Any]] = []
    for idx, gap in enumerate(gap_rows, start=1):
        line_family = gap["line_type_scope"]
        field_name = gap["field_name"]
        token_pos = gap["token_position"]
        staging = staging_by_key.get((line_family, token_pos, field_name))
        gap_type = gap["gap_type"]

        if gap_type == "context_only_retention":
            triage_status = "immediate_context_only"
            next_action = "Retain as context material unless a later mapping gate changes it."
        elif gap_type == "raw_line_audit_only" or field_name == "raw_line_text":
            triage_status = "retained_for_audit"
            next_action = "Retain audit raw-line representation; do not decompose into semantics here."
        elif staging is not None:
            triage_status = "candidate_for_dictionary_seed"
            next_action = (
                "Record a conservative DB26 structural seed name and queue manual "
                "mapping review before semantic use."
            )
        elif gap_type == "unassigned_semantic_mapping":
            triage_status = "needs_manual_mapping"
            next_action = "Route to manual mapping queue before analytical use."
        else:
            triage_status = "unknown"
            next_action = "Inspect DB25 structural evidence and decide the mapping path."

        severity = gap["gap_severity"] or "low"
        evidence_bits = [
            f"source_gap_type={gap_type}",
            f"supporting_count={gap['supporting_count']}",
        ]
        if staging is not None:
            evidence_bits.extend(
                [
                    f"staging_mapping_status={staging['mapping_status']}",
                    f"candidate_role={staging['candidate_role_label']}",
                    f"coverage={staging['coverage_fraction']}",
                ]
            )
        else:
            evidence_bits.append("no_matching_staging_row")

        triage_rows.append(
            {
                "triage_id": f"db26_triage_{idx:04d}",
                "source_gap_type": gap_type,
                "line_family": line_family,
                "token_position": token_position_label(token_pos, field_name),
                "source_field_name": field_name,
                "gap_severity": severity,
                "triage_status": triage_status,
                "evidence_summary": "; ".join(evidence_bits),
                "recommended_next_action": next_action,
                "created_at_utc": created_at,
            }
        )
    return triage_rows


def source_role_by_key(con: sqlite3.Connection) -> dict[tuple[str, int | None, str], dict[str, Any]]:
    role_rows = fetch_dicts(
        con,
        """
        SELECT line_type_scope, token_position, field_name, candidate_role_label,
               candidate_role_basis, evidence_class, present_count,
               coverage_fraction, distinct_value_count, numeric_like_count,
               text_like_count, low_variance_flag, source_recommendation
        FROM db23_tim_token_role_candidate
        """,
    )
    return {
        (
            row["line_type_scope"],
            row["token_position"],
            row["field_name"],
        ): row
        for row in role_rows
    }


def data_profile_by_position(con: sqlite3.Connection) -> dict[int, dict[str, Any]]:
    rows = fetch_dicts(
        con,
        """
        SELECT token_position, field_name, present_count, coverage_fraction,
               distinct_value_count, numeric_like_count, text_like_count,
               constant_or_low_variance_flag, high_variance_flag,
               structural_label, needs_mapping_flag, top_value_fraction,
               contiguous_group_fraction
        FROM qsb_v_db23a_41_token_position_profile
        """,
    )
    return {int(row["token_position"]): row for row in rows}


def grouping_by_position(con: sqlite3.Connection) -> dict[int, dict[str, Any]]:
    rows = fetch_dicts(
        con,
        """
        SELECT token_position, field_name, candidate_label, signal_sources,
               distinct_value_count, top_value_fraction, contiguous_group_fraction,
               candidate_strength, needs_mapping_flag
        FROM qsb_v_db23a_41_candidate_grouping_tokens
        """,
    )
    return {int(row["token_position"]): row for row in rows}


def classify_dictionary_seed(
    staging: dict[str, Any],
    role: dict[str, Any] | None,
    profile: dict[str, Any] | None,
    grouping: dict[str, Any] | None,
) -> tuple[str, str, int, str]:
    line_family = staging["line_type_scope"]
    position_int = numeric_position(staging["token_position"])
    field_name = staging["field_name"]
    role_label = staging["candidate_role_label"] or ""
    mapping_status = staging["mapping_status"] or ""

    if field_name == "raw_line_text" or position_int == 0:
        return "audit_raw_line", "retained_for_audit", 0, "high"

    if line_family != "data_line":
        return "context_token", "context_only", 0, "high"

    if position_int in FOCUS_TOKEN_SET:
        return "block_switch_token", "ready_for_staging_name_proposal", 1, "high"

    if grouping is not None:
        if grouping["candidate_label"] == "candidate_grouping_token":
            return "candidate_grouping_token", "ready_for_staging_name_proposal", 1, "medium"
        if grouping["candidate_label"] == "candidate_block_marker":
            return "stable_token", "ready_for_staging_name_proposal", 1, "high"

    if profile is not None:
        variance_flag = profile["constant_or_low_variance_flag"]
        structural_label = profile["structural_label"] or ""
        if variance_flag == "constant":
            return "stable_token", "ready_for_staging_name_proposal", 1, "high"
        if variance_flag == "low_variance":
            return "low_variance_token", "ready_for_staging_name_proposal", 1, "medium"
        if structural_label.startswith("variable_") or int(profile["high_variance_flag"] or 0) == 1:
            return "variable_token", "seed_only", 1, "medium"

    if "stable" in role_label or "stable" in mapping_status:
        return "stable_token", "ready_for_staging_name_proposal", 1, "medium"

    if role is not None and role["source_recommendation"] == "staging_ready_candidate":
        return "variable_token", "seed_only", 1, "medium"

    return "needs_manual_mapping", "needs_manual_mapping", 1, "low"


def evidence_for_dictionary_seed(
    staging: dict[str, Any],
    role: dict[str, Any] | None,
    profile: dict[str, Any] | None,
    grouping: dict[str, Any] | None,
) -> tuple[str, str]:
    sources = ["db23_tim_staging_field_map"]
    evidence_bits = [
        f"line_family={staging['line_type_scope']}",
        f"source_mapping_status={staging['mapping_status']}",
        f"source_candidate_role={staging['candidate_role_label']}",
        f"present_count={staging['present_count']}",
        f"coverage={staging['coverage_fraction']}",
    ]
    if role is not None:
        sources.append("db23_tim_token_role_candidate")
        evidence_bits.extend(
            [
                f"role_evidence_class={role['evidence_class']}",
                f"source_recommendation={role['source_recommendation']}",
                f"distinct_values={role['distinct_value_count']}",
            ]
        )
    if profile is not None:
        sources.append("qsb_v_db23a_41_token_position_profile")
        evidence_bits.extend(
            [
                f"profile_structural_label={profile['structural_label']}",
                f"profile_variance_flag={profile['constant_or_low_variance_flag']}",
                f"profile_distinct_values={profile['distinct_value_count']}",
                f"profile_top_fraction={profile['top_value_fraction']}",
            ]
        )
    if grouping is not None:
        sources.append("qsb_v_db23a_41_candidate_grouping_tokens")
        evidence_bits.extend(
            [
                f"grouping_label={grouping['candidate_label']}",
                f"grouping_strength={grouping['candidate_strength']}",
                f"contiguous_group_fraction={grouping['contiguous_group_fraction']}",
            ]
        )
    return "; ".join(dict.fromkeys(sources)), "; ".join(evidence_bits)


def build_field_dictionary_seed(
    con: sqlite3.Connection,
    created_at: str,
) -> list[dict[str, Any]]:
    roles = source_role_by_key(con)
    profiles = data_profile_by_position(con)
    groupings = grouping_by_position(con)
    staging_rows = fetch_dicts(
        con,
        """
        SELECT line_type_scope, record_family_label, token_position, field_name,
               staging_field_name, staging_data_class, inclusion_status,
               mapping_status, mapping_basis, candidate_role_label,
               present_count, coverage_fraction, needs_mapping_flag
        FROM db23_tim_staging_field_map
        ORDER BY line_type_scope, token_position, field_name
        """,
    )

    seed_rows: list[dict[str, Any]] = []
    for idx, staging in enumerate(staging_rows, start=1):
        line_family = staging["line_type_scope"]
        position_int = numeric_position(staging["token_position"])
        role = roles.get((line_family, staging["token_position"], staging["field_name"]))
        profile = profiles.get(position_int) if line_family == "data_line" and position_int else None
        grouping = groupings.get(position_int) if line_family == "data_line" and position_int else None

        structural_role, status, manual_review, confidence = classify_dictionary_seed(
            staging,
            role,
            profile,
            grouping,
        )
        evidence_source, evidence_summary = evidence_for_dictionary_seed(
            staging,
            role,
            profile,
            grouping,
        )
        if position_int in FOCUS_TOKEN_SET and line_family == "data_line":
            evidence_source += "; qsb_v_db23b_token_block_comparison"
            evidence_summary += "; focused_two_block_switch_context=present"

        seed_rows.append(
            {
                "dictionary_seed_id": f"db26_seed_{idx:04d}",
                "line_family": line_family,
                "token_position": token_position_label(
                    staging["token_position"],
                    staging["field_name"],
                ),
                "proposed_structural_name": proposed_structural_name(
                    line_family,
                    staging["token_position"],
                    staging["field_name"],
                    structural_role,
                ),
                "structural_role_candidate": structural_role,
                "mapping_status": status,
                "evidence_source": evidence_source,
                "evidence_summary": evidence_summary,
                "manual_review_required": manual_review,
                "confidence_class": confidence,
                "created_at_utc": created_at,
            }
        )
    return seed_rows


def normalize_relation_type(value: str | None) -> str:
    if value in {"equal", "different", "partial_overlap", "mixed", "needs_mapping"}:
        return value
    if value is None:
        return "needs_mapping"
    return "mixed"


def build_side_by_side_context(
    con: sqlite3.Connection,
    created_at: str,
) -> list[dict[str, Any]]:
    placeholders = ",".join("?" for _ in FOCUS_TOKEN_POSITIONS)
    rows = fetch_dicts(
        con,
        f"""
        SELECT token_position, field_name, token_focus_role,
               block_a_dominant_value, block_b_dominant_value,
               block_a_dominant_count, block_b_dominant_count,
               relation_type, block_discriminating_flag,
               constant_within_each_block_flag, transition_gap_relation,
               needs_mapping_flag
        FROM qsb_v_db23b_token_block_comparison
        WHERE token_position IN ({placeholders})
        ORDER BY token_position
        """,
        tuple(FOCUS_TOKEN_POSITIONS),
    )
    context_rows: list[dict[str, Any]] = []
    for idx, row in enumerate(rows, start=1):
        evidence = (
            "source=qsb_v_db25_two_block_signature_overview;"
            " qsb_v_db23b_token_block_comparison; "
            f"token_focus_role={row['token_focus_role']}; "
            f"block_discriminating={row['block_discriminating_flag']}; "
            f"constant_within_each_block={row['constant_within_each_block_flag']}; "
            f"transition_gap_relation={row['transition_gap_relation']}; "
            "structural context only"
        )
        context_rows.append(
            {
                "side_by_side_id": f"db26_side_{idx:04d}",
                "token_position": token_position_label(row["token_position"], row["field_name"]),
                "block_a_value": row["block_a_dominant_value"],
                "block_b_value": row["block_b_dominant_value"],
                "relation_type": normalize_relation_type(row["relation_type"]),
                "block_a_count": row["block_a_dominant_count"],
                "block_b_count": row["block_b_dominant_count"],
                "structural_role_candidate": "block_switch_token",
                "evidence_summary": evidence,
                "created_at_utc": created_at,
            }
        )
    if len(context_rows) != len(FOCUS_TOKEN_POSITIONS):
        raise RuntimeError(
            "Focused side-by-side context is incomplete: "
            f"expected {len(FOCUS_TOKEN_POSITIONS)}, found {len(context_rows)}"
        )
    return context_rows


def build_decision_candidates(
    seed_rows: list[dict[str, Any]],
    side_rows: list[dict[str, Any]],
    triage_rows: list[dict[str, Any]],
    created_at: str,
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    idx = 1
    for seed in seed_rows:
        decision_status = (
            "needs_review"
            if int(seed["manual_review_required"]) == 1
            else "proposed"
        )
        rows.append(
            {
                "decision_candidate_id": f"db26_decision_{idx:04d}",
                "candidate_type": "dictionary_seed",
                "related_token_position": seed["token_position"],
                "related_line_family": seed["line_family"],
                "decision_status": decision_status,
                "rationale": (
                    f"Dictionary seed {seed['proposed_structural_name']} exists "
                    f"with structural_role_candidate={seed['structural_role_candidate']}."
                ),
                "created_at_utc": created_at,
            }
        )
        idx += 1
    for side in side_rows:
        rows.append(
            {
                "decision_candidate_id": f"db26_decision_{idx:04d}",
                "candidate_type": "block_switch_context",
                "related_token_position": side["token_position"],
                "related_line_family": "data_line",
                "decision_status": "needs_review",
                "rationale": (
                    "Focused token has block-side dominant values recorded as "
                    "structural switch context only."
                ),
                "created_at_utc": created_at,
            }
        )
        idx += 1
    for triage in triage_rows:
        candidate_type = (
            "audit_retention"
            if triage["triage_status"] in {"retained_for_audit", "immediate_context_only"}
            else "manual_mapping"
        )
        rows.append(
            {
                "decision_candidate_id": f"db26_decision_{idx:04d}",
                "candidate_type": candidate_type,
                "related_token_position": triage["token_position"],
                "related_line_family": triage["line_family"],
                "decision_status": "needs_review",
                "rationale": (
                    f"Mapping triage row {triage['triage_id']} has status "
                    f"{triage['triage_status']}."
                ),
                "created_at_utc": created_at,
            }
        )
        idx += 1
    return rows


def build_manual_queue(
    triage_rows: list[dict[str, Any]],
    side_rows: list[dict[str, Any]],
    created_at: str,
) -> list[dict[str, Any]]:
    queue_rows: list[dict[str, Any]] = []
    idx = 1
    for triage in triage_rows:
        priority = severity_to_priority(triage["gap_severity"])
        if triage["triage_status"] in {"retained_for_audit", "immediate_context_only"}:
            blocking_status = "does_not_block_staging"
            required_decision = (
                "Confirm audit/context retention policy or mark for later dictionary work."
            )
        elif triage["triage_status"] == "candidate_for_dictionary_seed":
            blocking_status = "blocks_analysis_only"
            required_decision = (
                "Approve or revise the conservative structural seed before semantic use."
            )
        else:
            blocking_status = "blocks_analysis_only"
            required_decision = "Provide a manual mapping decision before analytical use."

        queue_rows.append(
            {
                "queue_id": f"db26_queue_{idx:04d}",
                "queue_type": "mapping_gap",
                "priority": priority,
                "token_position": triage["token_position"],
                "line_family": triage["line_family"],
                "issue_summary": (
                    f"{triage['source_gap_type']} triaged as {triage['triage_status']}."
                ),
                "required_decision": required_decision,
                "blocking_status": blocking_status,
                "created_at_utc": created_at,
            }
        )
        idx += 1

    for side in side_rows:
        queue_rows.append(
            {
                "queue_id": f"db26_queue_{idx:04d}",
                "queue_type": "block_switch_token",
                "priority": "high",
                "token_position": side["token_position"],
                "line_family": "data_line",
                "issue_summary": (
                    "Focused two-block token has different dominant values "
                    "across block contexts."
                ),
                "required_decision": (
                    "Decide whether and how this structural block-switch token "
                    "should be named in a later controlled dictionary."
                ),
                "blocking_status": "blocks_analysis_only",
                "created_at_utc": created_at,
            }
        )
        idx += 1
    return queue_rows


def insert_rows(con: sqlite3.Connection, table_name: str, rows: list[dict[str, Any]]) -> None:
    if not rows:
        return
    columns = list(rows[0].keys())
    placeholders = ", ".join("?" for _ in columns)
    column_sql = ", ".join(columns)
    sql = f"INSERT INTO {table_name} ({column_sql}) VALUES ({placeholders})"
    con.executemany(sql, [[row[column] for column in columns] for row in rows])


def table_count(con: sqlite3.Connection, table_name: str) -> int:
    row = con.execute(f"SELECT COUNT(*) AS n FROM {table_name}").fetchone()
    return int(row["n"])


def counts_by(con: sqlite3.Connection, table_name: str, column_name: str) -> dict[str, int]:
    rows = con.execute(
        f"""
        SELECT {column_name} AS key, COUNT(*) AS n
        FROM {table_name}
        GROUP BY {column_name}
        ORDER BY {column_name}
        """
    ).fetchall()
    return {str(row["key"]): int(row["n"]) for row in rows}


def write_csv(con: sqlite3.Connection, path: Path, source_name: str) -> None:
    cur = con.execute(f"SELECT * FROM {source_name}")
    columns = [description[0] for description in cur.description]
    rows = cur.fetchall()
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(columns)
        for row in rows:
            writer.writerow([row[column] for column in columns])


def first_rows(
    con: sqlite3.Connection,
    source_name: str,
    limit: int = 5,
) -> list[dict[str, Any]]:
    return fetch_dicts(con, f"SELECT * FROM {source_name} LIMIT ?", (limit,))


def build_summary(
    con: sqlite3.Connection,
    db_path: Path,
    backup_path: Path,
    output_root: Path,
    run_id: str,
    created_at: str,
    fk_violations: list[sqlite3.Row],
) -> dict[str, Any]:
    db26_tables = [
        "db26_mapping_run_log",
        "db26_mapping_gap_triage",
        "db26_field_dictionary_seed",
        "db26_side_by_side_block_token_context",
        "db26_mapping_decision_candidate",
        "db26_open_manual_mapping_queue",
    ]
    db26_views = [
        "qsb_v_db26_mapping_gap_triage",
        "qsb_v_db26_field_dictionary_seed",
        "qsb_v_db26_side_by_side_block_token_context",
        "qsb_v_db26_open_manual_mapping_queue",
        "qsb_v_db26_mapping_dashboard",
        "qsb_v_db26_next_mapping_questions",
    ]
    return {
        "run_id": run_id,
        "run_timestamp_utc": created_at,
        "data_substrate": str(db_path),
        "db25_updated_additively": True,
        "backup_db_path": str(backup_path),
        "new_isolated_analysis_db_created": False,
        "raw_files_read": False,
        "script_name": SCRIPT_NAME,
        "claim_boundary": CLAIM_BOUNDARY,
        "db26_tables": db26_tables,
        "db26_views": db26_views,
        "row_counts": {table: table_count(con, table) for table in db26_tables},
        "triage_counts_by_status": counts_by(
            con,
            "db26_mapping_gap_triage",
            "triage_status",
        ),
        "triage_counts_by_severity": counts_by(
            con,
            "db26_mapping_gap_triage",
            "gap_severity",
        ),
        "field_seed_counts_by_role": counts_by(
            con,
            "db26_field_dictionary_seed",
            "structural_role_candidate",
        ),
        "field_seed_counts_by_status": counts_by(
            con,
            "db26_field_dictionary_seed",
            "mapping_status",
        ),
        "manual_queue_counts_by_type": counts_by(
            con,
            "db26_open_manual_mapping_queue",
            "queue_type",
        ),
        "manual_queue_counts_by_priority": counts_by(
            con,
            "db26_open_manual_mapping_queue",
            "priority",
        ),
        "focused_token_context": first_rows(
            con,
            "qsb_v_db26_side_by_side_block_token_context",
            10,
        ),
        "first_dashboard_rows": first_rows(
            con,
            "qsb_v_db26_mapping_dashboard",
            20,
        ),
        "foreign_key_violation_count": len(fk_violations),
        "output_files": {name: str(output_root / name) for name in OUTPUT_FILENAMES},
    }


def write_readout(path: Path, summary: dict[str, Any]) -> None:
    row_counts = summary["row_counts"]
    triage_status = summary["triage_counts_by_status"]
    field_roles = summary["field_seed_counts_by_role"]
    queue_counts = summary["manual_queue_counts_by_type"]
    focused_lines = []
    for row in summary["focused_token_context"]:
        focused_lines.append(
            "- {token_position}: block_a={block_a_value} ({block_a_count}), "
            "block_b={block_b_value} ({block_b_count}), relation={relation_type}".format(**row)
        )

    content = f"""# QSB-DB26 Mapping Gap Triage and Field Dictionary Seed

## Befund

- Data substrate: `{summary['data_substrate']}`
- DB25 update mode: additive in-place DB26 tables/views only
- Backup DB: `{summary['backup_db_path']}`
- DB26 mapping gaps triaged: {row_counts['db26_mapping_gap_triage']}
- DB26 field dictionary seed rows: {row_counts['db26_field_dictionary_seed']}
- DB26 focused side-by-side token rows: {row_counts['db26_side_by_side_block_token_context']}
- DB26 manual queue rows: {row_counts['db26_open_manual_mapping_queue']}
- FK violation count: {summary['foreign_key_violation_count']}

## Interpretation

The open DB23 mapping gaps are structurally triageable from DB25. Audit/raw
and context-only gaps can be retained as audit or context material. Data-line
token gaps can be recorded as conservative structural dictionary seeds, but
manual review remains required before any semantic use.

Triage counts by status:

```json
{pretty_json(triage_status)}
```

Field dictionary seed counts by structural role:

```json
{pretty_json(field_roles)}
```

## Hypothese

The five focused two-block token positions form the clearest first candidates
for block-switch structural naming because DB25 already contains side-by-side
dominant-value context for each token. This remains a structural hypothesis for
dictionary work, not a semantic or physical assignment.

Focused side-by-side context:

{chr(10).join(focused_lines)}

## Offene Luecke

Manual mapping decisions remain open for all mapping-gap queue rows and for the
focused block-switch tokens. The immediate next work item is controlled
dictionary review: approve, rename, or reject the DB26 structural seed names.

Manual queue counts by type:

```json
{pretty_json(queue_counts)}
```

## Claim Boundary

{summary['claim_boundary']}
"""
    path.write_text(content, encoding="utf-8")


def write_outputs(
    con: sqlite3.Connection,
    output_root: Path,
    summary: dict[str, Any],
) -> None:
    paths = output_paths(output_root)
    write_readout(paths["db26_mapping_gap_triage_readout.md"], summary)
    paths["db26_mapping_gap_triage_summary.json"].write_text(
        pretty_json(summary) + "\n",
        encoding="utf-8",
    )
    write_csv(con, paths["db26_mapping_gap_triage.csv"], "qsb_v_db26_mapping_gap_triage")
    write_csv(con, paths["db26_field_dictionary_seed.csv"], "qsb_v_db26_field_dictionary_seed")
    write_csv(
        con,
        paths["db26_side_by_side_block_tokens.csv"],
        "qsb_v_db26_side_by_side_block_token_context",
    )


def execute(db_path: Path, output_root: Path) -> dict[str, Any]:
    ensure_preconditions(db_path, output_root)
    backup_path = create_backup(db_path)
    created_at = utc_now()
    run_id = "DB26_MAPPING_GAP_TRIAGE_FIELD_DICTIONARY_SEED_" + timestamp_for_path()

    with connect_db(db_path) as con:
        con.execute("BEGIN IMMEDIATE")
        try:
            create_tables_and_views(con)
            triage_rows = build_gap_triage(con, created_at)
            seed_rows = build_field_dictionary_seed(con, created_at)
            side_rows = build_side_by_side_context(con, created_at)
            decision_rows = build_decision_candidates(
                seed_rows,
                side_rows,
                triage_rows,
                created_at,
            )
            queue_rows = build_manual_queue(triage_rows, side_rows, created_at)

            insert_rows(con, "db26_mapping_gap_triage", triage_rows)
            insert_rows(con, "db26_field_dictionary_seed", seed_rows)
            insert_rows(con, "db26_side_by_side_block_token_context", side_rows)
            insert_rows(con, "db26_mapping_decision_candidate", decision_rows)
            insert_rows(con, "db26_open_manual_mapping_queue", queue_rows)

            fk_violations = con.execute("PRAGMA foreign_key_check").fetchall()
            total_rows_inserted = (
                len(triage_rows)
                + len(seed_rows)
                + len(side_rows)
                + len(decision_rows)
                + len(queue_rows)
                + 1
            )
            con.execute(
                """
                INSERT INTO db26_mapping_run_log (
                    run_id,
                    run_timestamp_utc,
                    input_db_path,
                    backup_db_path,
                    script_name,
                    operation_mode,
                    row_count_inserted,
                    foreign_key_violation_count,
                    notes
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    run_id,
                    created_at,
                    str(db_path),
                    str(backup_path),
                    SCRIPT_NAME,
                    "DB-first consolidated in-place additive update",
                    total_rows_inserted,
                    len(fk_violations),
                    "DB26 added only DB26-prefixed tables/views and report files.",
                ),
            )
            con.commit()
        except Exception:
            con.rollback()
            raise

        summary = build_summary(
            con,
            db_path,
            backup_path,
            output_root,
            run_id,
            created_at,
            fk_violations,
        )
        write_outputs(con, output_root, summary)
    return summary


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "QSB-DB26 mapping-gap triage and field-dictionary seed over the "
            "existing DB25 consolidated SQLite database."
        )
    )
    parser.add_argument(
        "--db",
        type=Path,
        default=DEFAULT_DB,
        help="Path to the DB25 consolidated SQLite database.",
    )
    parser.add_argument(
        "--output-root",
        type=Path,
        default=DEFAULT_OUTPUT_ROOT,
        help="Existing DB25 consolidated output directory for DB26 reports and backup.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        summary = execute(args.db, args.output_root)
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    print(pretty_json(summary))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
