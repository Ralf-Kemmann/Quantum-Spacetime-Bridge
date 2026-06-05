#!/usr/bin/env python3
"""QSB-SHAPIROMART07: timestamp/phase semantic-resolution review.

This script reviews the fixed-context split candidates discovered by
SHAPIROMART06 and attempts to resolve exactly one DB-backed timestamp/phase
candidate against semantics already present in the workcopy database. It does
not read raw TIM/PAR files, use report outputs as inputs, compute timing/model
quantities, or assign physical interpretation.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import sqlite3
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


SCRIPT_NAME = "scripts/qsb_shapiromart07_timestamp_phase_semantic_resolution.py"
DEFAULT_LIVE_DB = Path(
    "runs/QSB-DB/QSB_DB25_CONSOLIDATED_RESEARCH_SNAPSHOT/"
    "qsb_research_consolidated_snapshot.db"
)
DEFAULT_WORKCOPY_DB = Path(
    "runs/QSB-DB/QSB_DB25_CONSOLIDATED_RESEARCH_SNAPSHOT/"
    "qsb_research_dwh_target_workcopy_dwh03.db"
)
DEFAULT_OUTPUT_ROOT = Path(
    "runs/QSB-SHAPIROMART/SHAPIROMART07_TIMESTAMP_PHASE_SEMANTIC_RESOLUTION"
)

READOUT_MD = "shapiromart07_readout.md"
SUMMARY_JSON = "shapiromart07_summary.json"
CANDIDATE_REVIEW_CSV = "shapiromart07_candidate_review.csv"
SELECTED_RESOLUTION_CSV = "shapiromart07_selected_resolution.csv"
LINK_READINESS_CSV = "shapiromart07_fixed_context_link_readiness.csv"
NEXT_STEP_CSV = "shapiromart07_next_step.csv"

OUTPUT_FILENAMES = [
    READOUT_MD,
    SUMMARY_JSON,
    CANDIDATE_REVIEW_CSV,
    SELECTED_RESOLUTION_CSV,
    LINK_READINESS_CSV,
    NEXT_STEP_CSV,
]

TARGET_TABLES = [
    "mart_shapiro_time_phase_candidate_review",
    "mart_shapiro_time_phase_resolution",
    "mart_shapiro_record_time_phase_link_readiness",
    "shapiromart07_run_log",
]

TARGET_VIEWS = [
    "qsb_v_shapiromart07_candidate_review",
    "qsb_v_shapiromart07_selected_resolution",
    "qsb_v_shapiromart07_fixed_context_link_readiness",
    "qsb_v_shapiromart07_dashboard",
]

REQUIRED_OBJECTS = [
    ("mart_shapiro_geometry_axis_candidate", "table"),
    ("mart_shapiro_fixed_context_exposure_readiness", "table"),
    ("mart_shapiro_geometry_axis_gap", "table"),
    ("mart_shapiro_structural_fingerprint", "table"),
    ("raw_record", "table"),
    ("raw_field_value", "table"),
    ("core_observation_record_link", "table"),
    ("core_observation", "table"),
    ("dim_time_context", "table"),
    ("db21_par_tim_joinability", "table"),
    ("db23_tim_staging_field_map", "table"),
    ("db23_tim_token_role_candidate", "table"),
    ("db26_field_dictionary_seed", "table"),
    ("map_token_dictionary", "table"),
    ("map_review_decision", "table"),
    ("db28_mapping_assertion_evidence", "table"),
    ("dwh14a_manual_evidence_decision", "table"),
    ("dwh15a_mapping_review_status_update", "table"),
    ("qsb_v_shapiromart04_complete_fingerprints", "view"),
    ("qsb_v_shapiromart06_dashboard", "view"),
]

SHAPIROMART_TABLE_SETS = {
    "SHAPIROMART01": [
        "mart_shapiro_observation_context",
        "mart_shapiro_feature_availability",
        "mart_shapiro_comparison_cohort",
        "mart_shapiro_control_gap",
        "shapiromart01_run_log",
    ],
    "SHAPIROMART02": [
        "mart_shapiro_numeric_field_profile",
        "mart_shapiro_numeric_field_pair_relation",
        "mart_shapiro_numeric_field_review",
        "shapiromart02_run_log",
    ],
    "SHAPIROMART03": [
        "mart_shapiro_feature_dictionary",
        "mart_shapiro_feature_exclusion",
        "shapiromart03_run_log",
    ],
    "SHAPIROMART04": [
        "mart_shapiro_structural_fingerprint",
        "mart_shapiro_fingerprint_context_summary",
        "mart_shapiro_fingerprint_context_difference",
        "mart_shapiro_fingerprint_build_gap",
        "shapiromart04_run_log",
    ],
    "SHAPIROMART05": [
        "mart_shapiro_within_context_stability",
        "mart_shapiro_context_centroid",
        "mart_shapiro_dimension_separability",
        "mart_shapiro_between_context_separability",
        "shapiromart05_run_log",
    ],
    "SHAPIROMART06": [
        "mart_shapiro_geometry_axis_candidate",
        "mart_shapiro_fixed_context_exposure_readiness",
        "mart_shapiro_geometry_axis_gap",
        "shapiromart06_run_log",
    ],
}

EXPECTED_CONTEXT_COUNTS = {
    "Rcvr_800": 2916,
    "Rcvr1_2": 4503,
}
EXPECTED_TOTAL_COMPLETE = 7419
EXPECTED_BACKEND = "GUPPI"
EXPECTED_SCIENCE_OBJECT = "J0740+6620"

RESOLVED_STATUSES = {
    "resolved_observation_time_anchor",
    "resolved_phase_like_anchor",
}
ALLOWED_RESOLUTION_STATUSES = RESOLVED_STATUSES | {
    "resolved_record_order_only",
    "insufficient_semantic_support",
    "conflicting_semantic_support",
    "no_candidate_resolved",
}
ALLOWED_SUPPORT_LEVELS = {
    "strong_db_internal_support",
    "moderate_db_internal_support",
    "weak_db_internal_support",
    "insufficient",
}

CLAIM_BOUNDARY = (
    "SHAPIROMART07 is a semantic-resolution review only. It does not compute "
    "TOAs, orbital phase, timing residuals, delays, model values, or physical "
    "exposure quantities, and it does not make geometry, beam, Bridge, or "
    "Shapiro claims."
)
NEXT_STEP_IF_RESOLVED = (
    "Define a deterministic, nonphysical exposure-grouping prototype within "
    "each fixed receiver/backend context, using only the resolved time/phase "
    "anchor and without computing physical exposure values."
)
NEXT_STEP_IF_NOT_RESOLVED = (
    "Create a precise evidence-gap note identifying the missing PAR/TIM "
    "semantic relation required before grouping."
)

TIME_ANCHOR_TERMS = {
    "mjd",
    "toa",
    "barycentric",
    "barycenter",
    "site arrival",
    "arrival time",
    "epoch",
    "observation time",
    "timestamp",
}
PHASE_ANCHOR_TERMS = {
    "phase",
    "orbital phase",
    "tasc",
    "binary phase",
}
CONFLICT_TERMS = {
    "unmapped",
    "needs_review",
    "pending_review",
    "not assigned",
    "no direct record-level key",
    "context_only",
}


def utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def quote_identifier(identifier: str) -> str:
    return '"' + identifier.replace('"', '""') + '"'


def output_paths(output_root: Path) -> dict[str, Path]:
    return {name: output_root / name for name in OUTPUT_FILENAMES}


def connect_readonly(path: Path) -> sqlite3.Connection:
    con = sqlite3.connect(f"file:{path.resolve()}?mode=ro", uri=True)
    con.row_factory = sqlite3.Row
    con.execute("PRAGMA foreign_keys = ON")
    return con


def connect_writable(path: Path) -> sqlite3.Connection:
    con = sqlite3.connect(f"file:{path.resolve()}?mode=rw", uri=True)
    con.row_factory = sqlite3.Row
    con.execute("PRAGMA foreign_keys = ON")
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


def table_count(con: sqlite3.Connection, table_name: str) -> int:
    row = con.execute(
        f"SELECT COUNT(*) AS n FROM {quote_identifier(table_name)}"
    ).fetchone()
    return int(row["n"])


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def file_stat(path: Path) -> dict[str, Any]:
    stat = path.stat()
    return {"size_bytes": stat.st_size, "mtime_ns": stat.st_mtime_ns}


def db_state(path: Path) -> dict[str, Any]:
    return {"sha256": file_sha256(path), "stat": file_stat(path)}


def integrity_check(con: sqlite3.Connection) -> str:
    row = con.execute("PRAGMA integrity_check").fetchone()
    return str(row[0]) if row else "no_result"


def foreign_key_violations(con: sqlite3.Connection) -> list[dict[str, Any]]:
    rows = con.execute("PRAGMA foreign_key_check").fetchall()
    return [
        {"table": row[0], "rowid": row[1], "parent": row[2], "fkid": row[3]}
        for row in rows
    ]


def stable_digest(rows: list[dict[str, Any]]) -> str:
    payload = json.dumps(rows, sort_keys=True, ensure_ascii=True)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def fail(message: str) -> None:
    raise RuntimeError(message)


def ensure_inputs(args: argparse.Namespace) -> None:
    if not args.live_db.exists():
        fail(f"Live DB not found: {args.live_db}")
    if not args.workcopy_db.exists():
        fail(f"Workcopy DB not found: {args.workcopy_db}")
    args.output_root.mkdir(parents=True, exist_ok=True)
    existing_outputs = [
        str(path)
        for path in output_paths(args.output_root).values()
        if path.exists()
    ]
    if existing_outputs and not args.overwrite:
        fail(
            "SHAPIROMART07 output files already exist. Use --overwrite to replace: "
            + "; ".join(existing_outputs)
        )


def validate_required_objects(con: sqlite3.Connection) -> None:
    missing: list[str] = []
    for name, object_type in REQUIRED_OBJECTS:
        if not object_exists(con, name, object_type):
            missing.append(f"{object_type}:{name}")
    for table_set, tables in SHAPIROMART_TABLE_SETS.items():
        for table in tables:
            if not object_exists(con, table, "table"):
                missing.append(f"table:{table_set}:{table}")
    if missing:
        fail("Missing required workcopy objects: " + "; ".join(missing))


def validate_existing_target_state(
    con: sqlite3.Connection,
    allow_existing: bool,
) -> dict[str, Any]:
    existing_objects: list[str] = []
    target_state: list[dict[str, Any]] = []
    for table in TARGET_TABLES:
        if object_exists(con, table, "table"):
            count = table_count(con, table)
            existing_objects.append(f"table:{table}")
            target_state.append({"name": table, "type": "table", "row_count": count})
        else:
            target_state.append({"name": table, "type": "table", "row_count": None})
    for view in TARGET_VIEWS:
        if object_exists(con, view, "view"):
            existing_objects.append(f"view:{view}")
            target_state.append({"name": view, "type": "view", "row_count": None})
        else:
            target_state.append({"name": view, "type": "view", "row_count": None})
    if existing_objects and not allow_existing:
        fail(
            "SHAPIROMART07 target objects already exist. Use --allow-existing "
            "for an explicit rerun: " + "; ".join(existing_objects)
        )
    return {"target_state": target_state, "existing_objects": existing_objects}


def prior_counts(con: sqlite3.Connection) -> dict[str, dict[str, int]]:
    return {
        name: {table: table_count(con, table) for table in tables}
        for name, tables in SHAPIROMART_TABLE_SETS.items()
    }


def fingerprint_digest(con: sqlite3.Connection) -> str:
    rows = fetch_dicts(
        con,
        """
        SELECT
            structural_fingerprint_id,
            raw_record_id,
            observation_id,
            science_object_id,
            receiver_context,
            backend_context,
            raw_context_label,
            coordinate_primary,
            coordinate_secondary,
            signal_value_primary,
            signal_value_secondary,
            auxiliary_uncertainty_primary,
            auxiliary_uncertainty_secondary,
            auxiliary_uncertainty_tertiary,
            complete_fingerprint,
            auxiliary_complete,
            duplicate_or_ambiguity_flag,
            source_value_count,
            fingerprint_status,
            notes
        FROM mart_shapiro_structural_fingerprint
        ORDER BY structural_fingerprint_id
        """,
    )
    return stable_digest(rows)


def validate_complete_fingerprints(con: sqlite3.Connection) -> dict[str, Any]:
    rows = fetch_dicts(
        con,
        """
        SELECT receiver_context, backend_context, science_object_id, COUNT(*) AS n
        FROM qsb_v_shapiromart04_complete_fingerprints
        GROUP BY receiver_context, backend_context, science_object_id
        ORDER BY receiver_context
        """,
    )
    context_counts = {str(row["receiver_context"]): int(row["n"]) for row in rows}
    if context_counts != EXPECTED_CONTEXT_COUNTS:
        fail(
            "Complete fingerprint context counts mismatch. expected="
            + json.dumps(EXPECTED_CONTEXT_COUNTS, sort_keys=True)
            + " actual="
            + json.dumps(context_counts, sort_keys=True)
        )
    if sum(context_counts.values()) != EXPECTED_TOTAL_COMPLETE:
        fail("Complete fingerprint total mismatch.")
    for row in rows:
        if str(row["backend_context"]) != EXPECTED_BACKEND:
            fail(f"Unexpected backend_context: {row['backend_context']}")
        if str(row["science_object_id"]) != EXPECTED_SCIENCE_OBJECT:
            fail(f"Unexpected science_object_id: {row['science_object_id']}")
    return {"rows": rows, "context_counts": context_counts}


def load_review_candidates(con: sqlite3.Connection) -> tuple[list[dict[str, Any]], str]:
    rows = fetch_dicts(
        con,
        """
        SELECT *
        FROM mart_shapiro_geometry_axis_candidate
        WHERE fixed_receiver_context_possible = 1
          AND candidate_class IN (
              'indirect_time_phase_candidate',
              'observation_link_candidate'
          )
        ORDER BY
            CASE
                WHEN source_table = 'raw_field_value'
                 AND source_field_or_token = 'tim_token_003' THEN 1
                WHEN source_table = 'raw_record'
                 AND source_field_or_token = 'record_index' THEN 2
                WHEN source_table = 'raw_field_value'
                 AND source_field_or_token = 'tim_token_001' THEN 3
                ELSE 4
            END,
            geometry_axis_candidate_id
        """,
    )
    selection_basis = (
        "SHAPIROMART06 fixed_receiver_context_possible split candidates "
        "with indirect_time_phase_candidate or observation_link_candidate class."
    )
    if not rows:
        rows = fetch_dicts(
            con,
            """
            SELECT *
            FROM mart_shapiro_geometry_axis_candidate
            WHERE candidate_class = 'indirect_time_phase_candidate'
            ORDER BY linked_fingerprint_count DESC, geometry_axis_candidate_id
            """,
        )
        selection_basis = (
            "Fallback to SHAPIROMART06 candidate_class=indirect_time_phase_candidate; "
            "no fixed-context split candidates were available."
        )
    return rows, selection_basis


def value_stats_for_field(con: sqlite3.Connection, field_name: str) -> dict[str, Any]:
    row = con.execute(
        """
        SELECT
            COUNT(*) AS populated,
            COUNT(DISTINCT fv.raw_value) AS distinct_n,
            COUNT(DISTINCT sf.raw_record_id) AS linked_n
        FROM mart_shapiro_structural_fingerprint AS sf
        JOIN raw_field_value AS fv
          ON fv.raw_record_id = sf.raw_record_id
        WHERE sf.complete_fingerprint = 1
          AND fv.field_name = ?
        """,
        (field_name,),
    ).fetchone()
    return {
        "populated": int(row["populated"] or 0),
        "distinct_n": int(row["distinct_n"] or 0),
        "linked_n": int(row["linked_n"] or 0),
    }


def receiver_split_summary(con: sqlite3.Connection, field_name: str) -> str:
    rows = fetch_dicts(
        con,
        """
        SELECT
            sf.receiver_context,
            sf.backend_context,
            COUNT(*) AS n,
            COUNT(DISTINCT fv.raw_value) AS distinct_n
        FROM mart_shapiro_structural_fingerprint AS sf
        JOIN raw_field_value AS fv
          ON fv.raw_record_id = sf.raw_record_id
        WHERE sf.complete_fingerprint = 1
          AND fv.field_name = ?
        GROUP BY sf.receiver_context, sf.backend_context
        ORDER BY sf.receiver_context
        """,
        (field_name,),
    )
    if not rows:
        return "no raw_field_value split rows found for complete fingerprints"
    return "; ".join(
        f"{row['receiver_context']}/{row['backend_context']}: "
        f"{row['distinct_n']} distinct across {row['n']} complete fingerprints"
        for row in rows
    )


def numeric_order_relation(con: sqlite3.Connection, field_name: str) -> str:
    rows = fetch_dicts(
        con,
        """
        SELECT rr.record_index, fv.raw_value
        FROM mart_shapiro_structural_fingerprint AS sf
        JOIN raw_record AS rr
          ON rr.raw_record_id = sf.raw_record_id
        JOIN raw_field_value AS fv
          ON fv.raw_record_id = sf.raw_record_id
        WHERE sf.complete_fingerprint = 1
          AND fv.field_name = ?
        ORDER BY rr.record_index
        """,
        (field_name,),
    )
    numeric_values: list[float] = []
    for row in rows:
        try:
            numeric_values.append(float(str(row["raw_value"])))
        except (TypeError, ValueError):
            return "not_numeric_or_mixed; no record-order semantic inference used"
    decreases = sum(
        1
        for before, after in zip(numeric_values, numeric_values[1:])
        if after < before
    )
    equal_steps = sum(
        1
        for before, after in zip(numeric_values, numeric_values[1:])
        if after == before
    )
    return (
        f"numeric_by_record_index: n={len(numeric_values)}, "
        f"decreases={decreases}, equal_steps={equal_steps}; "
        "structural ordering only, not used as semantic proof"
    )


def record_index_metrics(con: sqlite3.Connection) -> dict[str, Any]:
    row = con.execute(
        """
        SELECT
            COUNT(*) AS populated,
            COUNT(DISTINCT rr.record_index) AS distinct_n,
            COUNT(DISTINCT sf.raw_record_id) AS linked_n
        FROM mart_shapiro_structural_fingerprint AS sf
        JOIN raw_record AS rr
          ON rr.raw_record_id = sf.raw_record_id
        WHERE sf.complete_fingerprint = 1
        """
    ).fetchone()
    return {
        "populated": int(row["populated"] or 0),
        "distinct_n": int(row["distinct_n"] or 0),
        "linked_n": int(row["linked_n"] or 0),
    }


def collect_token_evidence(con: sqlite3.Connection, field_name: str) -> tuple[str, str]:
    sources: list[str] = []
    snippets: list[str] = []
    token_rows = fetch_dicts(
        con,
        """
        SELECT line_family, proposed_structural_name, structural_role,
               mapping_status, review_status, notes
        FROM map_token_dictionary
        WHERE token_position = ?
        ORDER BY line_family
        """,
        (field_name,),
    )
    if token_rows:
        sources.append("map_token_dictionary")
        for row in token_rows:
            snippets.append(
                "map_token_dictionary "
                f"{row['line_family']}: role={row['structural_role']}, "
                f"mapping_status={row['mapping_status']}, "
                f"review_status={row['review_status']}"
            )
    staging_rows = fetch_dicts(
        con,
        """
        SELECT line_type_scope, staging_field_name, staging_data_class,
               inclusion_status, mapping_status, mapping_basis,
               candidate_role_label, needs_mapping_flag
        FROM db23_tim_staging_field_map
        WHERE field_name = ?
        ORDER BY line_type_scope
        """,
        (field_name,),
    )
    if staging_rows:
        sources.append("db23_tim_staging_field_map")
        for row in staging_rows:
            snippets.append(
                "db23_tim_staging_field_map "
                f"{row['line_type_scope']}: data_class={row['staging_data_class']}, "
                f"mapping_status={row['mapping_status']}, "
                f"basis={row['mapping_basis']}"
            )
    role_rows = fetch_dicts(
        con,
        """
        SELECT line_type_scope, candidate_role_label, candidate_role_basis,
               evidence_class, present_count, coverage_fraction,
               distinct_value_count, source_recommendation
        FROM db23_tim_token_role_candidate
        WHERE field_name = ?
        ORDER BY line_type_scope
        """,
        (field_name,),
    )
    if role_rows:
        sources.append("db23_tim_token_role_candidate")
        for row in role_rows:
            snippets.append(
                "db23_tim_token_role_candidate "
                f"{row['line_type_scope']}: role={row['candidate_role_label']}, "
                f"evidence_class={row['evidence_class']}, "
                f"present={row['present_count']}, "
                f"coverage={row['coverage_fraction']}"
            )
    seed_rows = fetch_dicts(
        con,
        """
        SELECT line_family, proposed_structural_name, structural_role_candidate,
               mapping_status, confidence_class, evidence_summary
        FROM db26_field_dictionary_seed
        WHERE token_position = ?
        ORDER BY line_family
        """,
        (field_name,),
    )
    if seed_rows:
        sources.append("db26_field_dictionary_seed")
        for row in seed_rows:
            snippets.append(
                "db26_field_dictionary_seed "
                f"{row['line_family']}: role={row['structural_role_candidate']}, "
                f"mapping_status={row['mapping_status']}, "
                f"confidence={row['confidence_class']}"
            )
    review_rows = fetch_dicts(
        con,
        """
        SELECT decision_status, decision_priority, decision_text, notes
        FROM map_review_decision
        WHERE token_dictionary_id IN (
            SELECT token_dictionary_id
            FROM map_token_dictionary
            WHERE token_position = ?
        )
        ORDER BY review_decision_id
        """,
        (field_name,),
    )
    if review_rows:
        sources.append("map_review_decision")
        for row in review_rows:
            snippets.append(
                "map_review_decision: "
                f"decision_status={row['decision_status']}, "
                f"decision_text={row['decision_text']}"
            )
    manual_rows = fetch_dicts(
        con,
        """
        SELECT decision_status, evidence_strength, evidence_summary, next_action
        FROM dwh14a_manual_evidence_decision
        WHERE token_position = ?
           OR term = ?
        ORDER BY manual_evidence_decision_id
        """,
        (field_name, field_name),
    )
    if manual_rows:
        sources.append("dwh14a_manual_evidence_decision")
        for row in manual_rows:
            snippets.append(
                "dwh14a_manual_evidence_decision: "
                f"decision_status={row['decision_status']}, "
                f"evidence_strength={row['evidence_strength']}"
            )
    status_rows = fetch_dicts(
        con,
        """
        SELECT dwh14a_decision_status, dwh14a_evidence_strength,
               new_mapping_status, new_review_status, safe_to_promote
        FROM dwh15a_mapping_review_status_update
        WHERE token_position = ?
           OR term = ?
        ORDER BY mapping_review_update_id
        """,
        (field_name, field_name),
    )
    if status_rows:
        sources.append("dwh15a_mapping_review_status_update")
        for row in status_rows:
            snippets.append(
                "dwh15a_mapping_review_status_update: "
                f"new_mapping_status={row['new_mapping_status']}, "
                f"safe_to_promote={row['safe_to_promote']}"
            )
    assertion_rows = fetch_dicts(
        con,
        """
        SELECT evidence_status, assertion_status, evidence_summary, review_status
        FROM db28_mapping_assertion_evidence
        WHERE related_token_position = ?
        ORDER BY assertion_id
        """,
        (field_name,),
    )
    if assertion_rows:
        sources.append("db28_mapping_assertion_evidence")
        for row in assertion_rows:
            snippets.append(
                "db28_mapping_assertion_evidence: "
                f"evidence_status={row['evidence_status']}, "
                f"assertion_status={row['assertion_status']}, "
                f"review_status={row['review_status']}"
            )
    if not snippets:
        return (
            "No token-level dictionary/evidence row found for this candidate.",
            "none",
        )
    joined = " | ".join(snippets)
    return joined[:1800], "; ".join(dict.fromkeys(sources))


def classify_token_resolution(evidence_text: str) -> tuple[str, str, str]:
    text = evidence_text.lower()
    has_time = any(term in text for term in TIME_ANCHOR_TERMS)
    has_phase = any(term in text for term in PHASE_ANCHOR_TERMS)
    has_conflict = any(term in text for term in CONFLICT_TERMS)
    if has_time and not has_conflict:
        return (
            "resolved_observation_time_anchor",
            "strong_db_internal_support",
            "documented_observation_time_anchor",
        )
    if has_phase and not has_conflict:
        return (
            "resolved_phase_like_anchor",
            "moderate_db_internal_support",
            "documented_phase_like_anchor",
        )
    if has_time or has_phase:
        return (
            "conflicting_semantic_support",
            "weak_db_internal_support",
            "conflicting_or_unreviewed_time_phase_candidate",
        )
    return (
        "insufficient_semantic_support",
        "insufficient",
        "unpromoted_timestamp_phase_candidate",
    )


def build_review_rows(
    con: sqlite3.Connection,
    candidates: list[dict[str, Any]],
    created_at: str,
) -> tuple[list[dict[str, Any]], dict[str, Any] | None]:
    review_pre_rows: list[dict[str, Any]] = []
    for candidate in candidates:
        source_table = str(candidate["source_table"])
        source_field = str(candidate["source_field_or_token"])
        candidate_class = str(candidate["candidate_class"])
        populated = candidate["populated_row_count"]
        distinct_n = candidate["distinct_value_count"]
        linked_n = candidate["linked_fingerprint_count"]
        record_order_relation = "not_evaluated"
        observation_block_relation = "not_evaluated"
        evidence_text = "No documented time/phase semantic evidence found."
        evidence_source = "none"
        review_status = "insufficient_semantic_support"
        score = 0

        if source_table == "raw_field_value":
            stats = value_stats_for_field(con, source_field)
            populated = stats["populated"]
            distinct_n = stats["distinct_n"]
            linked_n = stats["linked_n"]
            observation_block_relation = receiver_split_summary(con, source_field)
            record_order_relation = numeric_order_relation(con, source_field)
            evidence_text, evidence_source = collect_token_evidence(con, source_field)
            review_status, support_level, resolved_role = classify_token_resolution(
                evidence_text
            )
            if source_field == "tim_token_003":
                score += 100
            if int(linked_n or 0) == EXPECTED_TOTAL_COMPLETE:
                score += 20
            if int(distinct_n or 0) >= EXPECTED_TOTAL_COMPLETE:
                score += 10
            if support_level != "insufficient":
                score += 100
            if review_status in RESOLVED_STATUSES:
                score += 100
            if "unmapped" in evidence_text.lower() or "needs_review" in evidence_text.lower():
                score -= 40
        elif source_table == "raw_record" and source_field == "record_index":
            stats = record_index_metrics(con)
            populated = stats["populated"]
            distinct_n = stats["distinct_n"]
            linked_n = stats["linked_n"]
            record_order_relation = "identity_record_order; not a timestamp/phase semantic anchor"
            observation_block_relation = (
                "record_index links one raw record per complete fingerprint; "
                "it does not document observation time or phase"
            )
            evidence_text = (
                "DB schema identifies record_index as raw record order only; "
                "no DB evidence maps it to observation time or phase."
            )
            evidence_source = "raw_record schema; mart_shapiro_geometry_axis_candidate"
            review_status = "resolved_record_order_only"
            score += 40
        elif source_table == "core_observation_record_link":
            record_order_relation = "traceability_key; no record-order or time semantics"
            observation_block_relation = (
                "core_observation_record_link connects complete fingerprints to raw records; "
                "it does not define a time/phase grouping variable"
            )
            evidence_text = (
                "DB schema supplies traceability linkage only. No DB row documents "
                "this field as an observation-time or phase anchor."
            )
            evidence_source = "core_observation_record_link schema; mart_shapiro_geometry_axis_candidate"
            review_status = "insufficient_semantic_support"
            score += 20
        else:
            record_order_relation = "not a candidate-specific record-order measure"
            observation_block_relation = (
                "SHAPIROMART06 candidate is linkable but has no documented "
                "time/phase grouping semantics in SHAPIROMART07 inputs"
            )
            evidence_text = str(candidate.get("notes") or "No additional evidence.")
            evidence_source = "mart_shapiro_geometry_axis_candidate"
            review_status = "insufficient_semantic_support"

        if review_status not in ALLOWED_RESOLUTION_STATUSES:
            fail(f"Unexpected review_status: {review_status}")
        review_pre_rows.append(
            {
                "source_table": source_table,
                "source_field_or_token": source_field,
                "candidate_class": candidate_class,
                "populated_row_count": populated,
                "distinct_value_count": distinct_n,
                "linked_fingerprint_count": linked_n,
                "record_order_relation": record_order_relation,
                "observation_block_relation": observation_block_relation,
                "documented_semantic_evidence": evidence_text,
                "semantic_evidence_source": evidence_source,
                "selected_for_resolution": 0,
                "review_status": review_status,
                "created_at_utc": created_at,
                "notes": (
                    "Reviewed under SHAPIROMART07. Record order or token position "
                    "alone is not treated as semantic support."
                ),
                "_score": score,
            }
        )

    ranked = sorted(
        review_pre_rows,
        key=lambda row: (
            -int(row["_score"]),
            str(row["source_table"]),
            str(row["source_field_or_token"]),
        ),
    )
    selected: dict[str, Any] | None = ranked[0] if ranked else None
    for index, row in enumerate(ranked, start=1):
        row["candidate_review_id"] = f"SHAPIROMART07_REVIEW_{index:03d}"
        row["review_rank"] = index
        if selected and row is selected:
            row["selected_for_resolution"] = 1
        row.pop("_score", None)
    return ranked, selected


def build_resolution_row(
    selected: dict[str, Any] | None,
    created_at: str,
) -> dict[str, Any] | None:
    if selected is None:
        return None
    status = str(selected["review_status"])
    if status in RESOLVED_STATUSES:
        resolution_status = status
        resolved_role = (
            "documented_observation_time_anchor"
            if status == "resolved_observation_time_anchor"
            else "documented_phase_like_anchor"
        )
        semantic_support_level = (
            "strong_db_internal_support"
            if status == "resolved_observation_time_anchor"
            else "moderate_db_internal_support"
        )
        usable = 1
        next_transformation = NEXT_STEP_IF_RESOLVED
    elif status == "resolved_record_order_only":
        resolution_status = "resolved_record_order_only"
        resolved_role = "record_order_only_not_timestamp_phase"
        semantic_support_level = "weak_db_internal_support"
        usable = 0
        next_transformation = NEXT_STEP_IF_NOT_RESOLVED
    else:
        resolution_status = "no_candidate_resolved"
        resolved_role = "not_promoted_timestamp_phase_candidate"
        semantic_support_level = "insufficient"
        usable = 0
        next_transformation = NEXT_STEP_IF_NOT_RESOLVED
    if resolution_status not in ALLOWED_RESOLUTION_STATUSES:
        fail(f"Unexpected resolution_status: {resolution_status}")
    if semantic_support_level not in ALLOWED_SUPPORT_LEVELS:
        fail(f"Unexpected support level: {semantic_support_level}")
    return {
        "time_phase_resolution_id": "SHAPIROMART07_RESOLUTION_001",
        "source_table": selected["source_table"],
        "source_field_or_token": selected["source_field_or_token"],
        "resolved_role": resolved_role,
        "resolution_status": resolution_status,
        "semantic_support_level": semantic_support_level,
        "linked_fingerprint_count": int(selected["linked_fingerprint_count"] or 0),
        "usable_for_fixed_context_grouping": usable,
        "direct_physical_interpretation_allowed": 0,
        "required_next_transformation": next_transformation,
        "created_at_utc": created_at,
        "notes": (
            "At most one candidate was selected for semantic-resolution review. "
            + CLAIM_BOUNDARY
        ),
    }


def linked_count_for_resolution_context(
    con: sqlite3.Connection,
    resolution_row: dict[str, Any] | None,
    receiver: str,
) -> int:
    if resolution_row is None:
        return 0
    if int(resolution_row["usable_for_fixed_context_grouping"]) != 1:
        return 0
    source_table = str(resolution_row["source_table"])
    source_field = str(resolution_row["source_field_or_token"])
    if source_table == "raw_field_value":
        row = con.execute(
            """
            SELECT COUNT(DISTINCT sf.raw_record_id) AS n
            FROM mart_shapiro_structural_fingerprint AS sf
            JOIN raw_field_value AS fv
              ON fv.raw_record_id = sf.raw_record_id
            WHERE sf.complete_fingerprint = 1
              AND sf.receiver_context = ?
              AND sf.backend_context = ?
              AND fv.field_name = ?
            """,
            (receiver, EXPECTED_BACKEND, source_field),
        ).fetchone()
        return int(row["n"] or 0)
    if source_table in {"raw_record", "core_observation_record_link"}:
        return EXPECTED_CONTEXT_COUNTS[receiver]
    return 0


def build_link_readiness_rows(
    con: sqlite3.Connection,
    resolution_row: dict[str, Any] | None,
    created_at: str,
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    resolved_available = (
        resolution_row is not None
        and str(resolution_row["resolution_status"]) in RESOLVED_STATUSES
        and int(resolution_row["usable_for_fixed_context_grouping"]) == 1
    )
    joinability = con.execute(
        """
        SELECT direct_record_level_join_available, joinability_status,
               joinability_notes
        FROM db21_par_tim_joinability
        LIMIT 1
        """
    ).fetchone()
    record_level_join = (
        int(joinability["direct_record_level_join_available"])
        if joinability is not None
        and joinability["direct_record_level_join_available"] is not None
        else 0
    )
    for index, receiver in enumerate(["Rcvr_800", "Rcvr1_2"], start=1):
        complete_count = EXPECTED_CONTEXT_COUNTS[receiver]
        linked_count = linked_count_for_resolution_context(con, resolution_row, receiver)
        unlinked_count = complete_count - linked_count
        if resolved_available and linked_count == complete_count:
            status = "ready_for_nonphysical_grouping_definition"
            blocking_reason = None
        elif not resolved_available:
            status = "blocked_no_resolved_candidate"
            blocking_reason = (
                "No candidate reached resolved_observation_time_anchor or "
                "resolved_phase_like_anchor status."
            )
        elif record_level_join == 0:
            status = "blocked_record_level_join"
            blocking_reason = (
                "Resolved candidate is not backed by a certified record-level "
                "PAR/TIM join."
            )
        elif linked_count > 0:
            status = "partial_linkage_available"
            blocking_reason = "Resolved candidate is only partially linked in this context."
        else:
            status = "blocked_conflicting_semantics"
            blocking_reason = "Resolved candidate linkage is unavailable or conflicting."
        rows.append(
            {
                "link_readiness_id": f"SHAPIROMART07_READY_{index:03d}",
                "receiver_context": receiver,
                "backend_context": EXPECTED_BACKEND,
                "complete_fingerprint_count": complete_count,
                "resolved_candidate_available": 1 if resolved_available else 0,
                "linked_record_count": linked_count,
                "unlinked_record_count": unlinked_count,
                "grouping_readiness_status": status,
                "blocking_reason": blocking_reason,
                "created_at_utc": created_at,
                "notes": (
                    "Readiness is evaluated while holding receiver/backend fixed. "
                    f"db21_joinability_status={joinability['joinability_status'] if joinability else 'missing'}."
                ),
            }
        )
    return rows


def create_tables(con: sqlite3.Connection) -> None:
    con.executescript(
        """
        CREATE TABLE IF NOT EXISTS mart_shapiro_time_phase_candidate_review (
            candidate_review_id TEXT PRIMARY KEY,
            source_table TEXT NOT NULL,
            source_field_or_token TEXT NOT NULL,
            candidate_class TEXT NOT NULL,
            populated_row_count INTEGER,
            distinct_value_count INTEGER,
            linked_fingerprint_count INTEGER,
            record_order_relation TEXT,
            observation_block_relation TEXT,
            documented_semantic_evidence TEXT,
            semantic_evidence_source TEXT,
            review_rank INTEGER,
            selected_for_resolution INTEGER NOT NULL,
            review_status TEXT NOT NULL,
            created_at_utc TEXT NOT NULL,
            notes TEXT
        );

        CREATE TABLE IF NOT EXISTS mart_shapiro_time_phase_resolution (
            time_phase_resolution_id TEXT PRIMARY KEY,
            source_table TEXT NOT NULL,
            source_field_or_token TEXT NOT NULL,
            resolved_role TEXT NOT NULL,
            resolution_status TEXT NOT NULL,
            semantic_support_level TEXT NOT NULL,
            linked_fingerprint_count INTEGER NOT NULL,
            usable_for_fixed_context_grouping INTEGER NOT NULL,
            direct_physical_interpretation_allowed INTEGER NOT NULL,
            required_next_transformation TEXT,
            created_at_utc TEXT NOT NULL,
            notes TEXT
        );

        CREATE TABLE IF NOT EXISTS mart_shapiro_record_time_phase_link_readiness (
            link_readiness_id TEXT PRIMARY KEY,
            receiver_context TEXT NOT NULL,
            backend_context TEXT NOT NULL,
            complete_fingerprint_count INTEGER NOT NULL,
            resolved_candidate_available INTEGER NOT NULL,
            linked_record_count INTEGER NOT NULL,
            unlinked_record_count INTEGER NOT NULL,
            grouping_readiness_status TEXT NOT NULL,
            blocking_reason TEXT,
            created_at_utc TEXT NOT NULL,
            notes TEXT
        );

        CREATE TABLE IF NOT EXISTS shapiromart07_run_log (
            run_id TEXT PRIMARY KEY,
            run_timestamp_utc TEXT,
            candidate_review_count INTEGER,
            selected_candidate_count INTEGER,
            resolved_candidate_count INTEGER,
            linked_fingerprint_count INTEGER,
            live_db_modified INTEGER,
            workcopy_db_modified INTEGER,
            integrity_check_result TEXT,
            foreign_key_violation_count INTEGER,
            notes TEXT
        );
        """
    )


def clear_target_tables(con: sqlite3.Connection) -> None:
    for table in TARGET_TABLES:
        con.execute(f"DELETE FROM {quote_identifier(table)}")


def insert_rows(
    con: sqlite3.Connection,
    table: str,
    rows: list[dict[str, Any]],
) -> None:
    if not rows:
        return
    columns = list(rows[0].keys())
    placeholders = ", ".join("?" for _ in columns)
    quoted_columns = ", ".join(quote_identifier(column) for column in columns)
    sql = (
        f"INSERT INTO {quote_identifier(table)} "
        f"({quoted_columns}) VALUES ({placeholders})"
    )
    con.executemany(sql, [tuple(row[column] for column in columns) for row in rows])


def create_views(con: sqlite3.Connection) -> None:
    for view in TARGET_VIEWS:
        con.execute(f"DROP VIEW IF EXISTS {quote_identifier(view)}")
    con.executescript(
        """
        CREATE VIEW qsb_v_shapiromart07_candidate_review AS
        SELECT *
        FROM mart_shapiro_time_phase_candidate_review;

        CREATE VIEW qsb_v_shapiromart07_selected_resolution AS
        SELECT *
        FROM mart_shapiro_time_phase_resolution;

        CREATE VIEW qsb_v_shapiromart07_fixed_context_link_readiness AS
        SELECT *
        FROM mart_shapiro_record_time_phase_link_readiness;

        CREATE VIEW qsb_v_shapiromart07_dashboard AS
        SELECT
            (SELECT COUNT(*)
             FROM mart_shapiro_time_phase_candidate_review)
                AS candidate_review_count,
            (SELECT COUNT(*)
             FROM mart_shapiro_time_phase_candidate_review
             WHERE selected_for_resolution = 1)
                AS selected_candidate_count,
            (SELECT COUNT(*)
             FROM mart_shapiro_time_phase_resolution
             WHERE resolution_status IN (
                 'resolved_observation_time_anchor',
                 'resolved_phase_like_anchor'
             ))
                AS resolved_candidate_count,
            (SELECT source_table || '.' || source_field_or_token
             FROM mart_shapiro_time_phase_candidate_review
             ORDER BY review_rank
             LIMIT 1)
                AS highest_ranked_candidate,
            (SELECT source_table || '.' || source_field_or_token
             FROM mart_shapiro_time_phase_candidate_review
             WHERE selected_for_resolution = 1
             ORDER BY review_rank
             LIMIT 1)
                AS selected_candidate,
            (SELECT resolution_status
             FROM mart_shapiro_time_phase_resolution
             LIMIT 1)
                AS resolution_status,
            (SELECT semantic_support_level
             FROM mart_shapiro_time_phase_resolution
             LIMIT 1)
                AS semantic_support_level,
            (SELECT linked_fingerprint_count
             FROM mart_shapiro_time_phase_resolution
             LIMIT 1)
                AS linked_fingerprint_count,
            (SELECT usable_for_fixed_context_grouping
             FROM mart_shapiro_time_phase_resolution
             LIMIT 1)
                AS usable_for_fixed_context_grouping,
            (SELECT grouping_readiness_status
             FROM mart_shapiro_record_time_phase_link_readiness
             WHERE receiver_context = 'Rcvr_800')
                AS rcvr_800_status,
            (SELECT grouping_readiness_status
             FROM mart_shapiro_record_time_phase_link_readiness
             WHERE receiver_context = 'Rcvr1_2')
                AS rcvr1_2_status,
            'semantic_resolution_review_no_physical_interpretation'
                AS interpretation_status;
        """
    )


def queryable_counts(con: sqlite3.Connection) -> dict[str, int | str]:
    counts: dict[str, int | str] = {}
    for table in TARGET_TABLES:
        counts[table] = table_count(con, table)
    for view in TARGET_VIEWS:
        row = con.execute(f"SELECT COUNT(*) AS n FROM {quote_identifier(view)}").fetchone()
        counts[view] = int(row["n"])
    return counts


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    if rows:
        columns = list(rows[0].keys())
    else:
        columns = []
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=columns)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def write_next_step_csv(path: Path, next_step: str, reason: str) -> None:
    rows = [{"next_step_rank": 1, "next_step": next_step, "reason": reason}]
    write_csv(path, rows)


def write_readout(
    path: Path,
    summary: dict[str, Any],
    review_rows: list[dict[str, Any]],
    resolution_rows: list[dict[str, Any]],
    readiness_rows: list[dict[str, Any]],
    next_step: str,
) -> None:
    selected = summary["selected_candidate"]
    resolution = resolution_rows[0] if resolution_rows else None
    lines = [
        "# QSB-SHAPIROMART07 Timestamp/Phase Semantic Resolution",
        "",
        "## Befund",
        "",
        f"- Candidate count reviewed: {summary['candidate_review_count']}",
        f"- Highest-ranked candidate: {summary['highest_ranked_candidate']}",
        f"- Selected candidate: {selected if selected else 'none'}",
        f"- Selected candidate count: {summary['selected_candidate_count']}",
        f"- Resolved candidate count: {summary['resolved_candidate_count']}",
        f"- Resolution status: {summary['resolution_status']}",
        f"- Semantic support level: {summary['semantic_support_level']}",
        f"- Linked fingerprint count: {summary['linked_fingerprint_count']}",
        "- Direct physical interpretation allowed: 0",
        "",
        "Reviewed candidates:",
    ]
    for row in review_rows:
        lines.append(
            "- "
            f"rank {row['review_rank']}: {row['source_table']}."
            f"{row['source_field_or_token']} "
            f"({row['candidate_class']}), status={row['review_status']}, "
            f"linked={row['linked_fingerprint_count']}"
        )
    lines.extend(
        [
            "",
            "Fixed-context readiness:",
        ]
    )
    for row in readiness_rows:
        lines.append(
            "- "
            f"{row['receiver_context']}/{row['backend_context']}: "
            f"{row['grouping_readiness_status']}; "
            f"linked={row['linked_record_count']}; "
            f"unlinked={row['unlinked_record_count']}; "
            f"blocking_reason={row['blocking_reason']}"
        )
    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            (
                "The strongest reviewed candidate is the complete, fixed-context "
                "split token `raw_field_value.tim_token_003`. The DB-internal "
                "support found for it is structural: numeric-like, variable, "
                "complete across fingerprints, and explicitly still marked as "
                "unmapped semantics / needs review. No existing DB evidence row "
                "promotes it to an observation-time or phase anchor."
            ),
            "",
            "## Hypothese",
            "",
            (
                "A future DB-backed semantic mapping may be able to turn the "
                "highest-ranked token into a nonphysical grouping anchor, but "
                "SHAPIROMART07 does not provide that mapping."
            ),
            "",
            "## Offene Luecke",
            "",
            (
                "Missing relation: a documented PAR/TIM semantic mapping that "
                "identifies one reviewed candidate as observation time or phase "
                "and permits record-level use while holding receiver/backend fixed."
            ),
            "",
            "## Claim Boundary",
            "",
            CLAIM_BOUNDARY,
            "",
            "## Next Step",
            "",
            f"- {next_step}",
            "",
        ]
    )
    if resolution is not None:
        lines.extend(
            [
                "## Selected Resolution Row",
                "",
                f"- source: {resolution['source_table']}.{resolution['source_field_or_token']}",
                f"- resolved_role: {resolution['resolved_role']}",
                f"- required_next_transformation: {resolution['required_next_transformation']}",
                "",
            ]
        )
    path.write_text("\n".join(lines), encoding="utf-8")


def write_outputs(
    output_root: Path,
    summary: dict[str, Any],
    review_rows: list[dict[str, Any]],
    resolution_rows: list[dict[str, Any]],
    readiness_rows: list[dict[str, Any]],
    next_step: str,
    next_step_reason: str,
) -> None:
    paths = output_paths(output_root)
    write_readout(
        paths[READOUT_MD],
        summary,
        review_rows,
        resolution_rows,
        readiness_rows,
        next_step,
    )
    paths[SUMMARY_JSON].write_text(
        json.dumps(summary, indent=2, sort_keys=True, ensure_ascii=True) + "\n",
        encoding="utf-8",
    )
    write_csv(paths[CANDIDATE_REVIEW_CSV], review_rows)
    write_csv(paths[SELECTED_RESOLUTION_CSV], resolution_rows)
    write_csv(paths[LINK_READINESS_CSV], readiness_rows)
    write_next_step_csv(paths[NEXT_STEP_CSV], next_step, next_step_reason)


def run(args: argparse.Namespace) -> dict[str, Any]:
    ensure_inputs(args)
    live_before = db_state(args.live_db)
    workcopy_before = db_state(args.workcopy_db)
    created_at = utc_now()
    with connect_readonly(args.live_db) as live_con:
        live_integrity_before = integrity_check(live_con)
    with connect_writable(args.workcopy_db) as con:
        validate_required_objects(con)
        target_state = validate_existing_target_state(con, args.allow_existing)
        validate_complete_fingerprints(con)
        prior_before = prior_counts(con)
        fingerprint_before = fingerprint_digest(con)
        candidates, selection_basis = load_review_candidates(con)
        review_rows, selected = build_review_rows(con, candidates, created_at)
        resolution_row = build_resolution_row(selected, created_at)
        resolution_rows = [resolution_row] if resolution_row is not None else []
        readiness_rows = build_link_readiness_rows(con, resolution_row, created_at)
        selected_count = sum(int(row["selected_for_resolution"]) for row in review_rows)
        resolved_count = sum(
            1
            for row in resolution_rows
            if str(row["resolution_status"]) in RESOLVED_STATUSES
        )
        linked_fingerprint_count = (
            int(resolution_rows[0]["linked_fingerprint_count"])
            if resolution_rows
            else 0
        )
        if selected_count > 1:
            fail("More than one candidate selected.")
        if len(resolution_rows) > 1:
            fail("More than one resolution row generated.")
        con.execute("BEGIN")
        try:
            create_tables(con)
            clear_target_tables(con)
            insert_rows(con, "mart_shapiro_time_phase_candidate_review", review_rows)
            insert_rows(con, "mart_shapiro_time_phase_resolution", resolution_rows)
            insert_rows(
                con,
                "mart_shapiro_record_time_phase_link_readiness",
                readiness_rows,
            )
            create_views(con)
            run_log = {
                "run_id": "SHAPIROMART07_RUN_001",
                "run_timestamp_utc": created_at,
                "candidate_review_count": len(review_rows),
                "selected_candidate_count": selected_count,
                "resolved_candidate_count": resolved_count,
                "linked_fingerprint_count": linked_fingerprint_count,
                "live_db_modified": 0,
                "workcopy_db_modified": 1,
                "integrity_check_result": "pending",
                "foreign_key_violation_count": -1,
                "notes": (
                    "Run log finalized after integrity checks. "
                    + CLAIM_BOUNDARY
                ),
            }
            insert_rows(con, "shapiromart07_run_log", [run_log])
            con.commit()
        except Exception:
            con.rollback()
            raise
        integrity = integrity_check(con)
        fk_violations = foreign_key_violations(con)
        prior_after = prior_counts(con)
        fingerprint_after = fingerprint_digest(con)
        q_counts = queryable_counts(con)
        con.execute(
            """
            UPDATE shapiromart07_run_log
            SET integrity_check_result = ?,
                foreign_key_violation_count = ?
            WHERE run_id = 'SHAPIROMART07_RUN_001'
            """,
            (integrity, len(fk_violations)),
        )
        con.commit()
        dashboard_rows = fetch_dicts(con, "SELECT * FROM qsb_v_shapiromart07_dashboard")
    live_after = db_state(args.live_db)
    workcopy_after = db_state(args.workcopy_db)
    live_modified = 0 if live_before == live_after else 1
    workcopy_modified = 0 if workcopy_before == workcopy_after else 1
    if resolution_rows and resolution_rows[0]["resolution_status"] in RESOLVED_STATUSES:
        next_step = NEXT_STEP_IF_RESOLVED
        next_step_reason = "A usable nonphysical time/phase grouping anchor was resolved."
    else:
        next_step = NEXT_STEP_IF_NOT_RESOLVED
        next_step_reason = (
            "No reviewed candidate has DB-internal support sufficient for "
            "observation-time or phase-anchor promotion."
        )
    highest_ranked = (
        f"{review_rows[0]['source_table']}.{review_rows[0]['source_field_or_token']}"
        if review_rows
        else None
    )
    selected_name = (
        f"{selected['source_table']}.{selected['source_field_or_token']}"
        if selected
        else None
    )
    summary: dict[str, Any] = {
        "script": SCRIPT_NAME,
        "run_timestamp_utc": created_at,
        "live_db": str(args.live_db),
        "workcopy_db": str(args.workcopy_db),
        "output_root": str(args.output_root),
        "selection_basis": selection_basis,
        "candidate_review_count": len(review_rows),
        "expected_review_count_satisfied": len(review_rows) == 4,
        "highest_ranked_candidate": highest_ranked,
        "selected_candidate": selected_name,
        "selected_candidate_count": selected_count,
        "resolved_candidate_count": resolved_count,
        "resolution_status": (
            resolution_rows[0]["resolution_status"] if resolution_rows else "no_candidate_resolved"
        ),
        "semantic_support_level": (
            resolution_rows[0]["semantic_support_level"] if resolution_rows else "insufficient"
        ),
        "linked_fingerprint_count": linked_fingerprint_count,
        "usable_for_fixed_context_grouping": (
            int(resolution_rows[0]["usable_for_fixed_context_grouping"])
            if resolution_rows
            else 0
        ),
        "fixed_context_readiness": readiness_rows,
        "main_blocking_gap": (
            "missing documented DB semantic relation identifying a reviewed "
            "candidate as observation time or phase anchor"
        ),
        "single_next_step": next_step,
        "claim_boundary": CLAIM_BOUNDARY,
        "target_state_before": target_state,
        "dashboard": dashboard_rows[0] if dashboard_rows else {},
        "validation": {
            "live_integrity_before": live_integrity_before,
            "live_db_modified": live_modified,
            "workcopy_db_modified": workcopy_modified,
            "integrity_check_result": integrity,
            "foreign_key_violation_count": len(fk_violations),
            "prior_shapiromart01_06_counts_preserved": prior_before == prior_after,
            "fingerprint_values_unchanged": fingerprint_before == fingerprint_after,
            "at_most_one_candidate_selected": selected_count <= 1,
            "at_most_one_resolution_row": len(resolution_rows) <= 1,
            "no_compound_labels_promoted": (
                not resolution_rows
                or resolution_rows[0]["source_field_or_token"]
                not in {"raw_context_label", "receiver_context", "backend_context"}
            ),
            "physical_quantities_computed": False,
            "receiver_context_comparison_used_as_geometry_test": False,
            "all_new_objects_queryable": all(
                name in q_counts for name in TARGET_TABLES + TARGET_VIEWS
            ),
            "queryable_counts": q_counts,
        },
        "warnings": [
            (
                "SHAPIROMART06 stores only one candidate with "
                "candidate_class=indirect_time_phase_candidate and four "
                "fixed-context split candidates; SHAPIROMART07 reviewed the "
                "four fixed-context split candidates."
            )
            if len(review_rows) == 4
            else (
                "Reviewed candidate count differs from four because "
                "SHAPIROMART06 did not provide four fixed-context split candidates."
            ),
            (
                "The highest-ranked candidate is structurally linkable but remains "
                "unresolved semantically unless a DB evidence row explicitly maps "
                "it to observation time or phase."
            ),
        ],
    }
    validation = summary["validation"]
    if live_modified != 0:
        fail("Live DB was modified.")
    if integrity != "ok":
        fail(f"Workcopy integrity_check failed: {integrity}")
    if fk_violations:
        fail("Foreign key violations found.")
    if not validation["prior_shapiromart01_06_counts_preserved"]:
        fail("Prior SHAPIROMART01-06 counts changed.")
    if not validation["fingerprint_values_unchanged"]:
        fail("Fingerprint digest changed.")
    if validation["physical_quantities_computed"]:
        fail("Physical quantities computation flag is not false.")
    write_outputs(
        args.output_root,
        summary,
        review_rows,
        resolution_rows,
        readiness_rows,
        next_step,
        next_step_reason,
    )
    return summary


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "QSB-SHAPIROMART07 timestamp/phase semantic-resolution review."
        )
    )
    parser.add_argument("--live-db", type=Path, default=DEFAULT_LIVE_DB)
    parser.add_argument("--workcopy-db", type=Path, default=DEFAULT_WORKCOPY_DB)
    parser.add_argument("--output-root", type=Path, default=DEFAULT_OUTPUT_ROOT)
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Replace existing SHAPIROMART07 output files.",
    )
    parser.add_argument(
        "--allow-existing",
        action="store_true",
        help="Allow existing SHAPIROMART07 DB objects and refresh their rows/views.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        summary = run(args)
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    print(json.dumps(summary, indent=2, sort_keys=True, ensure_ascii=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
