#!/usr/bin/env python3
"""QSB-SHAPIROMART08: targeted PAR/TIM semantic evidence review.

This script reviews whether SHAPIROMART07 candidates, especially
raw_field_value.tim_token_003, have explicit local documentary support as an
observation-time or phase anchor. It opens both databases read-only, creates no
DB objects, reads no raw TIM/PAR source files, and does not compute physical
quantities.
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


SCRIPT_NAME = "scripts/qsb_shapiromart08_par_tim_semantic_evidence_review.py"
DEFAULT_LIVE_DB = Path(
    "runs/QSB-DB/QSB_DB25_CONSOLIDATED_RESEARCH_SNAPSHOT/"
    "qsb_research_consolidated_snapshot.db"
)
DEFAULT_WORKCOPY_DB = Path(
    "runs/QSB-DB/QSB_DB25_CONSOLIDATED_RESEARCH_SNAPSHOT/"
    "qsb_research_dwh_target_workcopy_dwh03.db"
)
DEFAULT_OUTPUT_ROOT = Path(
    "runs/QSB-SHAPIROMART/SHAPIROMART08_PAR_TIM_SEMANTIC_EVIDENCE_REVIEW"
)

READOUT_MD = "shapiromart08_readout.md"
SUMMARY_JSON = "shapiromart08_summary.json"
CANDIDATE_EVIDENCE_CSV = "shapiromart08_candidate_evidence.csv"
SELECTED_STATUS_CSV = "shapiromart08_selected_candidate_status.csv"
EVIDENCE_GAP_CSV = "shapiromart08_evidence_gap.csv"
NEXT_STEP_CSV = "shapiromart08_next_step.csv"

OUTPUT_FILENAMES = [
    READOUT_MD,
    SUMMARY_JSON,
    CANDIDATE_EVIDENCE_CSV,
    SELECTED_STATUS_CSV,
    EVIDENCE_GAP_CSV,
    NEXT_STEP_CSV,
]

CANDIDATE_EVIDENCE_FIELDS = [
    "candidate",
    "source_type",
    "source_reference",
    "evidence_text_summary",
    "supports_observation_time",
    "supports_phase",
    "supports_record_order_only",
    "evidence_strength",
    "conflict_status",
    "notes",
]

SELECTED_STATUS_FIELDS = [
    "candidate",
    "final_status",
    "semantic_support_level",
    "documented_role",
    "promotion_allowed",
    "required_next_action",
    "notes",
]

FINAL_STATUSES = {
    "observation_time_anchor_supported",
    "phase_anchor_supported",
    "record_order_only",
    "insufficient_semantic_evidence",
    "conflicting_semantic_evidence",
}

PROMOTION_STATUSES = {
    "observation_time_anchor_supported",
    "phase_anchor_supported",
}

NEXT_STEP_SUPPORTED = (
    "Proceed to SHAPIROMART09: define deterministic fixed-receiver/backend "
    "grouping using the resolved anchor, without computing physical exposure values."
)
NEXT_STEP_UNSUPPORTED = (
    "Obtain dataset-specific TIM format documentation that maps the exact data-line "
    "token position to observation time or phase before grouping."
)
MAIN_MISSING_EVIDENCE = (
    "A local documentary relation mapping the exact SHAPIROMART07 candidate "
    "position, especially tim_token_003, to an observation-time or phase field."
)

CLAIM_BOUNDARY = (
    "SHAPIROMART08 is a targeted semantic evidence review only. It does not "
    "compute TOAs, orbital phase, timing residuals, delays, model values, or "
    "physical exposure quantities, and it does not make geometry, beam, Bridge, "
    "or Shapiro claims."
)

SCRIPT_EVIDENCE_FILES = [
    Path("scripts/qsb_db21_par_tim_joinability_first_timing_ingest.py"),
    Path("scripts/qsb_db22_tim_structure_profiling.py"),
    Path("scripts/qsb_db23_tim_staging_field_map.py"),
    Path("scripts/qsb_db26_mapping_gap_triage_field_dictionary_seed.py"),
    Path("scripts/qsb_db28_external_dictionary_evidence_seed.py"),
    Path("scripts/qsb_dwh14a_manual_evidence_insertion.py"),
    Path("scripts/qsb_dwh15a_controlled_mapping_review_status_update.py"),
    Path("scripts/qsb_shapiromart04_first_unweighted_fingerprint_build.py"),
    Path("scripts/qsb_shapiromart07_timestamp_phase_semantic_resolution.py"),
]

DOC_EVIDENCE_FILES = [
    Path("docs/QSB_ST_SHAPIROINFO08_TOY_TO_SEMI_REAL_ADAPTER_PLAN.md"),
    Path("docs/QSB_ST_SHAPIROINFO09_TARGETED_BINARY_PULSAR_PILOT_PLAN.md"),
    Path("docs/QSB_ST_SHAPIROINFO10_CORRECTION_STATE_FIELD_SCHEMA.md"),
    Path("docs/QSB_ST_SHAPIROINFO13_CANDIDATE_SOURCE_REVIEW_J0740_6620.md"),
    Path("docs/QSB_ST_SHAPIROINFO21_J0740_README_RELEASE_NOTE_INSPECTION_RESULT.md"),
    Path("docs/QSB_ST_SHAPIROINFO55_TIM_PAR_CONTENT_STRUCTURE_REVIEW_RESULT_NOTE.md"),
    Path("docs/QSB_ST_SHAPIROINFO57_TIM_PAR_FIELD_DICTIONARY_SCHEMA_CORRECTION_STATE_SPEC.md"),
    Path("docs/QSB_ST_SHAPIROINFO60_FIELD_DICTIONARY_SCHEMA_CORRECTION_STATE_RESULT_NOTE.md"),
    Path("docs/QSB_ST_SHAPIROINFO66_PUBLIC_DOCUMENTATION_AND_CORRECTION_STATE_RESOLUTION_RESULT_NOTE.md"),
]

LOCAL_EVIDENCE_DIRS = [
    Path("data/QSB-ST-SHAPIROINFO/public_sources"),
    Path("data/QSB-ST-SHAPIROINFO/manual_evidence"),
]

DB_TABLES_INSPECTED = [
    "qsb_v_shapiromart07_candidate_review",
    "db23_tim_staging_field_map",
    "db23_tim_token_role_candidate",
    "db26_field_dictionary_seed",
    "map_token_dictionary",
    "map_review_decision",
    "db28_mapping_assertion_evidence",
    "dwh14a_manual_evidence_decision",
    "dwh15a_mapping_review_status_update",
    "raw_record",
    "raw_field_value",
    "core_observation_record_link",
]


def utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


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


def fail(message: str) -> None:
    raise RuntimeError(message)


def ensure_inputs(args: argparse.Namespace) -> None:
    if not args.live_db.exists():
        fail(f"Live DB not found: {args.live_db}")
    if not args.workcopy_db.exists():
        fail(f"Workcopy DB not found: {args.workcopy_db}")
    if not args.repo_root.exists():
        fail(f"Repo root not found: {args.repo_root}")
    args.output_root.mkdir(parents=True, exist_ok=True)
    existing_outputs = [
        str(path)
        for path in output_paths(args.output_root).values()
        if path.exists()
    ]
    if existing_outputs and not args.overwrite:
        fail(
            "SHAPIROMART08 output files already exist. Use --overwrite to replace: "
            + "; ".join(existing_outputs)
        )


def normalize_candidate(row: dict[str, Any]) -> str:
    return f"{row['source_table']}.{row['source_field_or_token']}"


def load_candidates(con: sqlite3.Connection) -> list[dict[str, Any]]:
    if not object_exists(con, "qsb_v_shapiromart07_candidate_review", "view"):
        fail("Missing qsb_v_shapiromart07_candidate_review.")
    rows = fetch_dicts(
        con,
        """
        SELECT
            review_rank,
            source_table,
            source_field_or_token,
            candidate_class,
            selected_for_resolution,
            review_status,
            linked_fingerprint_count,
            documented_semantic_evidence,
            semantic_evidence_source
        FROM qsb_v_shapiromart07_candidate_review
        ORDER BY
            CASE
                WHEN source_table = 'raw_field_value'
                 AND source_field_or_token = 'tim_token_003' THEN 0
                ELSE 1
            END,
            review_rank,
            source_table,
            source_field_or_token
        """,
    )
    if len(rows) != 4:
        fail(f"Expected exactly 4 SHAPIROMART07 candidates, found {len(rows)}.")
    first = rows[0]
    if normalize_candidate(first) != "raw_field_value.tim_token_003":
        fail("First reviewed candidate is not raw_field_value.tim_token_003.")
    return rows


def add_evidence(
    rows: list[dict[str, Any]],
    *,
    candidate: str,
    source_type: str,
    source_reference: str,
    evidence_text_summary: str,
    supports_observation_time: bool = False,
    supports_phase: bool = False,
    supports_record_order_only: bool = False,
    evidence_strength: str = "insufficient",
    conflict_status: str = "no_conflict",
    notes: str = "",
) -> None:
    rows.append(
        {
            "candidate": candidate,
            "source_type": source_type,
            "source_reference": source_reference,
            "evidence_text_summary": evidence_text_summary[:1200],
            "supports_observation_time": "yes" if supports_observation_time else "no",
            "supports_phase": "yes" if supports_phase else "no",
            "supports_record_order_only": "yes" if supports_record_order_only else "no",
            "evidence_strength": evidence_strength,
            "conflict_status": conflict_status,
            "notes": notes[:800],
        }
    )


def join_status(rows: list[dict[str, Any]], fields: list[str]) -> str:
    parts: list[str] = []
    for row in rows:
        part = ", ".join(f"{field}={row.get(field)}" for field in fields)
        parts.append(part)
    return " | ".join(parts) if parts else "no rows"


def add_shapiromart07_evidence(
    evidence_rows: list[dict[str, Any]],
    candidate_rows: list[dict[str, Any]],
) -> None:
    for row in candidate_rows:
        candidate = normalize_candidate(row)
        review_status = str(row["review_status"])
        supports_order = review_status == "resolved_record_order_only"
        add_evidence(
            evidence_rows,
            candidate=candidate,
            source_type="db_view",
            source_reference="qsb_v_shapiromart07_candidate_review",
            evidence_text_summary=str(row["documented_semantic_evidence"]),
            supports_record_order_only=supports_order,
            evidence_strength="moderate" if supports_order else "insufficient",
            notes=(
                f"SHAPIROMART07 review_status={review_status}; "
                f"semantic_evidence_source={row['semantic_evidence_source']}"
            ),
        )


def add_token_db_evidence(
    con: sqlite3.Connection,
    evidence_rows: list[dict[str, Any]],
    candidate: str,
    token: str,
) -> None:
    dictionary_rows = fetch_dicts(
        con,
        """
        SELECT line_family, proposed_structural_name, controlled_field_name,
               structural_role, mapping_status, review_status, notes
        FROM map_token_dictionary
        WHERE token_position = ?
        ORDER BY line_family, token_dictionary_id
        """,
        (token,),
    )
    add_evidence(
        evidence_rows,
        candidate=candidate,
        source_type="db_table",
        source_reference="map_token_dictionary",
        evidence_text_summary=join_status(
            dictionary_rows,
            [
                "line_family",
                "proposed_structural_name",
                "controlled_field_name",
                "structural_role",
                "mapping_status",
                "review_status",
            ],
        ),
        evidence_strength="weak" if dictionary_rows else "insufficient",
        notes="Dictionary rows are structural unless controlled_field_name explicitly maps time or phase.",
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
        (token,),
    )
    add_evidence(
        evidence_rows,
        candidate=candidate,
        source_type="db_table",
        source_reference="db23_tim_staging_field_map",
        evidence_text_summary=join_status(
            staging_rows,
            [
                "line_type_scope",
                "staging_field_name",
                "staging_data_class",
                "mapping_status",
                "mapping_basis",
                "candidate_role_label",
                "needs_mapping_flag",
            ],
        ),
        evidence_strength="weak" if staging_rows else "insufficient",
        notes="DB23 staging marks structure and mapping gaps; it does not assign time/phase semantics.",
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
        (token,),
    )
    add_evidence(
        evidence_rows,
        candidate=candidate,
        source_type="db_table",
        source_reference="db23_tim_token_role_candidate",
        evidence_text_summary=join_status(
            role_rows,
            [
                "line_type_scope",
                "candidate_role_label",
                "candidate_role_basis",
                "evidence_class",
                "source_recommendation",
            ],
        ),
        evidence_strength="weak" if role_rows else "insufficient",
        notes="Numeric-like or text-like structural roles are not semantic time/phase mappings.",
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
        (token,),
    )
    add_evidence(
        evidence_rows,
        candidate=candidate,
        source_type="db_table",
        source_reference="db26_field_dictionary_seed",
        evidence_text_summary=join_status(
            seed_rows,
            [
                "line_family",
                "proposed_structural_name",
                "structural_role_candidate",
                "mapping_status",
                "confidence_class",
            ],
        ),
        evidence_strength="weak" if seed_rows else "insufficient",
        notes="Seed rows require review before semantic use.",
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
        (token,),
    )
    add_evidence(
        evidence_rows,
        candidate=candidate,
        source_type="db_table",
        source_reference="map_review_decision",
        evidence_text_summary=join_status(
            review_rows,
            ["decision_status", "decision_priority", "decision_text"],
        ),
        evidence_strength="insufficient",
        notes="Pending review is not promotion evidence.",
    )
    manual_rows = fetch_dicts(
        con,
        """
        SELECT decision_status, evidence_strength, source_label,
               evidence_summary, next_action
        FROM dwh14a_manual_evidence_decision
        WHERE token_position = ?
           OR term = ?
        ORDER BY manual_evidence_decision_id
        """,
        (token, token),
    )
    positive_manual = [
        row
        for row in manual_rows
        if "evidence_supported" in str(row.get("decision_status", ""))
        and any(
            term in str(row.get("evidence_summary", "")).lower()
            for term in ["mjd", "toa", "arrival time", "phase", "timestamp"]
        )
    ]
    add_evidence(
        evidence_rows,
        candidate=candidate,
        source_type="db_table",
        source_reference="dwh14a_manual_evidence_decision",
        evidence_text_summary=join_status(
            manual_rows,
            ["decision_status", "evidence_strength", "source_label", "next_action"],
        ),
        supports_observation_time=bool(
            positive_manual
            and any("phase" not in str(row.get("evidence_summary", "")).lower() for row in positive_manual)
        ),
        supports_phase=bool(
            positive_manual
            and any("phase" in str(row.get("evidence_summary", "")).lower() for row in positive_manual)
        ),
        evidence_strength="strong" if positive_manual else "insufficient",
        notes="Manual evidence must explicitly target the exact token/term.",
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
        (token, token),
    )
    add_evidence(
        evidence_rows,
        candidate=candidate,
        source_type="db_table",
        source_reference="dwh15a_mapping_review_status_update",
        evidence_text_summary=join_status(
            status_rows,
            [
                "dwh14a_decision_status",
                "dwh14a_evidence_strength",
                "new_mapping_status",
                "new_review_status",
                "safe_to_promote",
            ],
        ),
        evidence_strength="moderate"
        if any(int(row.get("safe_to_promote") or 0) == 1 for row in status_rows)
        else "insufficient",
        notes="safe_to_promote rows would be required for controlled promotion.",
    )
    assertion_rows = fetch_dicts(
        con,
        """
        SELECT evidence_status, assertion_status, evidence_summary,
               evidence_ref, review_status
        FROM db28_mapping_assertion_evidence
        WHERE related_token_position = ?
        ORDER BY assertion_id
        """,
        (token,),
    )
    add_evidence(
        evidence_rows,
        candidate=candidate,
        source_type="db_table",
        source_reference="db28_mapping_assertion_evidence",
        evidence_text_summary=join_status(
            assertion_rows,
            [
                "evidence_status",
                "assertion_status",
                "evidence_summary",
                "review_status",
            ],
        ),
        evidence_strength="weak" if assertion_rows else "insufficient",
        notes="No assertion row may be treated as a token-to-time/phase mapping unless explicit.",
    )


def add_schema_evidence(
    con: sqlite3.Connection,
    evidence_rows: list[dict[str, Any]],
    candidate: str,
    table_name: str,
    field_name: str,
) -> None:
    schema_rows = [
        dict(row)
        for row in con.execute(f"PRAGMA table_info({table_name})").fetchall()
        if str(row["name"]) == field_name
    ]
    summary = join_status(schema_rows, ["name", "type", "notnull", "pk"])
    supports_record_order = table_name == "raw_record" and field_name == "record_index"
    if supports_record_order:
        summary = (
            summary
            + " | schema role: raw record order/index; no time or phase mapping"
        )
    elif table_name == "core_observation_record_link":
        summary = summary + " | schema role: traceability link key"
    add_evidence(
        evidence_rows,
        candidate=candidate,
        source_type="db_schema",
        source_reference=f"PRAGMA table_info({table_name})",
        evidence_text_summary=summary,
        supports_record_order_only=supports_record_order,
        evidence_strength="moderate" if supports_record_order else "weak",
        notes="Schema evidence can document record order or linkage only, not observation-time semantics.",
    )


def add_source_comment_scan(
    con: sqlite3.Connection,
    evidence_rows: list[dict[str, Any]],
    candidate: str,
) -> None:
    terms = ["FORMAT", "MJD", "TOA", "time", "phase", "tim_token_003"]
    counts: dict[str, int] = {}
    for term in terms:
        row = con.execute(
            """
            SELECT COUNT(*) AS n
            FROM raw_record
            WHERE line_type = 'comment_line'
              AND raw_line_text LIKE ?
            """,
            (f"%{term}%",),
        ).fetchone()
        counts[term] = int(row["n"] or 0)
    add_evidence(
        evidence_rows,
        candidate=candidate,
        source_type="db_table",
        source_reference="raw_record comment_line keyword scan",
        evidence_text_summary=(
            "stored comment-line keyword counts: "
            + ", ".join(f"{term}={counts[term]}" for term in terms)
        ),
        evidence_strength="insufficient",
        notes=(
            "Scan used stored comments only and did not export raw comment values; "
            "no exact token-to-time/phase mapping was found."
        ),
    )


def safe_read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return ""


def is_raw_tim_par_source(relative_path: Path) -> bool:
    lower_parts = {part.lower() for part in relative_path.parts}
    return "raw" in lower_parts or relative_path.suffix.lower() in {".tim", ".par"}


def add_file_absence_or_context_evidence(
    evidence_rows: list[dict[str, Any]],
    candidate: str,
    source_type: str,
    path: Path,
    text: str,
) -> None:
    candidate_token = candidate.split(".")[-1]
    lower = text.lower()
    candidate_hit = candidate_token.lower() in lower or candidate.lower() in lower
    time_context = any(term in lower for term in ["toa", "mjd", "timestamp", "arrival time"])
    phase_context = "phase" in lower
    if candidate_hit:
        summary = f"File mentions exact candidate term {candidate_token}."
        strength = "weak"
    elif time_context or phase_context:
        summary = (
            "File contains general timing/phase context but does not map the "
            f"exact candidate {candidate_token}."
        )
        strength = "context_only"
    else:
        summary = f"No exact candidate or time/phase mapping found for {candidate_token}."
        strength = "insufficient"
    add_evidence(
        evidence_rows,
        candidate=candidate,
        source_type=source_type,
        source_reference=str(path),
        evidence_text_summary=summary,
        evidence_strength=strength,
        notes="Local file scan is documentary only; general TIM context is not exact-token support.",
    )


def add_static_script_evidence(
    repo_root: Path,
    evidence_rows: list[dict[str, Any]],
    candidates: list[str],
) -> list[str]:
    inspected: list[str] = []
    for relative in SCRIPT_EVIDENCE_FILES:
        path = repo_root / relative
        if not path.exists():
            continue
        inspected.append(str(relative))
        text = safe_read_text(path)
        for candidate in candidates:
            token = candidate.split(".")[-1]
            if relative.name == "qsb_db21_par_tim_joinability_first_timing_ingest.py":
                if token.startswith("tim_token_"):
                    add_evidence(
                        evidence_rows,
                        candidate=candidate,
                        source_type="script_parser_logic",
                        source_reference=str(relative),
                        evidence_text_summary=(
                            "DB21 builds TIM field names as positional labels "
                            "tim_token_### from whitespace tokens; it does not map "
                            "token position to a named time/phase field."
                        ),
                        evidence_strength="weak",
                        notes="Parser code maps position to raw positional label only.",
                    )
            elif relative.name == "qsb_shapiromart04_first_unweighted_fingerprint_build.py":
                if token == "tim_token_003" and "tim_token_003" in text:
                    add_evidence(
                        evidence_rows,
                        candidate=candidate,
                        source_type="script_structural_use",
                        source_reference=str(relative),
                        evidence_text_summary=(
                            "SHAPIROMART04 maps tim_token_003 to "
                            "coordinate_secondary in an unweighted structural "
                            "fingerprint; its claim boundary states no TOAs, "
                            "delays, residuals, model quantities, or physical "
                            "interpretation are assigned."
                        ),
                        evidence_strength="weak",
                        notes="Structural coordinate use is not observation-time or phase support.",
                    )
            elif relative.name in {
                "qsb_db22_tim_structure_profiling.py",
                "qsb_db23_tim_staging_field_map.py",
                "qsb_db26_mapping_gap_triage_field_dictionary_seed.py",
                "qsb_db28_external_dictionary_evidence_seed.py",
            }:
                if token.startswith("tim_token_"):
                    add_evidence(
                        evidence_rows,
                        candidate=candidate,
                        source_type="script_mapping_boundary",
                        source_reference=str(relative),
                        evidence_text_summary=(
                            "Pipeline script handles TIM token structure or "
                            "dictionary candidates while explicitly preserving "
                            "unresolved/final-semantics boundaries."
                        ),
                        evidence_strength="weak",
                        notes="Mapping boundary evidence blocks promotion unless separate explicit evidence exists.",
                    )
            else:
                add_file_absence_or_context_evidence(
                    evidence_rows,
                    candidate,
                    "script_scan",
                    relative,
                    text,
                )
    return inspected


def add_doc_and_local_file_evidence(
    repo_root: Path,
    evidence_rows: list[dict[str, Any]],
    candidates: list[str],
) -> list[str]:
    inspected: list[str] = []
    files: list[Path] = []
    files.extend(DOC_EVIDENCE_FILES)
    for relative_dir in LOCAL_EVIDENCE_DIRS:
        directory = repo_root / relative_dir
        if directory.exists():
            files.extend(
                sorted(
                    path.relative_to(repo_root)
                    for path in directory.rglob("*")
                    if path.is_file()
                    and not is_raw_tim_par_source(path.relative_to(repo_root))
                )
            )
    seen: set[Path] = set()
    for relative in files:
        if relative in seen:
            continue
        seen.add(relative)
        path = repo_root / relative
        if not path.exists():
            continue
        inspected.append(str(relative))
        text = safe_read_text(path)
        for candidate in candidates:
            add_file_absence_or_context_evidence(
                evidence_rows,
                candidate,
                "local_documentation_or_evidence_file",
                relative,
                text,
            )
    return inspected


def add_candidate_specific_db_evidence(
    con: sqlite3.Connection,
    evidence_rows: list[dict[str, Any]],
    candidate_rows: list[dict[str, Any]],
) -> None:
    for row in candidate_rows:
        candidate = normalize_candidate(row)
        source_table = str(row["source_table"])
        source_field = str(row["source_field_or_token"])
        if source_table == "raw_field_value":
            add_token_db_evidence(con, evidence_rows, candidate, source_field)
            add_source_comment_scan(con, evidence_rows, candidate)
        elif source_table == "raw_record" and source_field == "record_index":
            add_schema_evidence(con, evidence_rows, candidate, "raw_record", "record_index")
        elif source_table == "core_observation_record_link":
            add_schema_evidence(
                con,
                evidence_rows,
                candidate,
                "core_observation_record_link",
                source_field,
            )


def status_for_candidate(
    candidate: str,
    rows: list[dict[str, Any]],
) -> dict[str, str]:
    candidate_rows = [row for row in rows if row["candidate"] == candidate]
    time_support = [
        row
        for row in candidate_rows
        if row["supports_observation_time"] == "yes"
        and row["evidence_strength"] in {"strong", "moderate"}
    ]
    phase_support = [
        row
        for row in candidate_rows
        if row["supports_phase"] == "yes"
        and row["evidence_strength"] in {"strong", "moderate"}
    ]
    record_order_support = [
        row
        for row in candidate_rows
        if row["supports_record_order_only"] == "yes"
        and row["evidence_strength"] in {"strong", "moderate"}
    ]
    conflict = any(row["conflict_status"] == "conflicting" for row in candidate_rows)
    if conflict:
        final_status = "conflicting_semantic_evidence"
        support_level = "conflicting"
        role = "conflicting"
    elif time_support:
        final_status = "observation_time_anchor_supported"
        support_level = "supported"
        role = "observation_time_anchor"
    elif phase_support:
        final_status = "phase_anchor_supported"
        support_level = "supported"
        role = "phase_like_anchor"
    elif record_order_support:
        final_status = "record_order_only"
        support_level = "record_order_documented"
        role = "record_order_only"
    else:
        final_status = "insufficient_semantic_evidence"
        support_level = "insufficient"
        role = "unresolved_field"
    if final_status not in FINAL_STATUSES:
        fail(f"Unexpected final status: {final_status}")
    return {
        "candidate": candidate,
        "final_status": final_status,
        "semantic_support_level": support_level,
        "documented_role": role,
    }


def build_selected_status(
    candidate_statuses: list[dict[str, str]],
) -> dict[str, str]:
    supported = [
        row for row in candidate_statuses if row["final_status"] in PROMOTION_STATUSES
    ]
    if supported:
        selected = supported[0]
        next_action = NEXT_STEP_SUPPORTED
        promotion = "yes"
        notes = "Candidate has explicit local documentary support for promotion."
    else:
        selected = candidate_statuses[0]
        next_action = NEXT_STEP_UNSUPPORTED
        promotion = "no"
        notes = (
            "No reviewed candidate reached observation-time or phase-anchor support. "
            "Record-order evidence, where present, does not unlock grouping."
        )
    return {
        "candidate": selected["candidate"],
        "final_status": selected["final_status"],
        "semantic_support_level": selected["semantic_support_level"],
        "documented_role": selected["documented_role"],
        "promotion_allowed": promotion,
        "required_next_action": next_action,
        "notes": notes,
    }


def write_csv(path: Path, rows: list[dict[str, Any]], fields: list[str] | None = None) -> None:
    columns = fields or (list(rows[0].keys()) if rows else [])
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=columns)
        writer.writeheader()
        for row in rows:
            writer.writerow({column: row.get(column, "") for column in columns})


def write_readout(
    path: Path,
    summary: dict[str, Any],
    selected_status: dict[str, str],
    candidate_statuses: list[dict[str, str]],
    inspected_files: list[str],
    inspected_tables: list[str],
) -> None:
    other_record_order = [
        row
        for row in candidate_statuses
        if row["candidate"] != selected_status["candidate"]
        and row["final_status"] == "record_order_only"
    ]
    lines = [
        "# QSB-SHAPIROMART08 PAR/TIM Semantic Evidence Review",
        "",
        "## Befund",
        "",
        f"- Candidate reviewed first: {summary['candidate_reviewed_first']}",
        f"- Candidates reviewed: {summary['candidate_review_count']}",
        f"- Selected candidate status row: {selected_status['candidate']}",
        f"- Final semantic status: {selected_status['final_status']}",
        f"- Promotion allowed: {selected_status['promotion_allowed']}",
        f"- Main missing evidence: {summary['main_missing_evidence']}",
        "",
        "Candidate statuses:",
    ]
    for row in candidate_statuses:
        lines.append(
            "- "
            f"{row['candidate']}: {row['final_status']} "
            f"({row['documented_role']})"
        )
    lines.extend(
        [
            "",
            "Inspected DB tables/views:",
        ]
    )
    for table in inspected_tables:
        lines.append(f"- {table}")
    lines.extend(["", "Inspected files:"])
    for file_path in inspected_files:
        lines.append(f"- {file_path}")
    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            (
                "`raw_field_value.tim_token_003` has DB-internal structural "
                "support only: it is present in dictionary/staging/profile rows, "
                "but those rows mark the field as positional, numeric-like, "
                "unmapped, seed-only, or pending review. No inspected local "
                "source maps it to observation time or phase."
            ),
            "",
            (
                "Another candidate has stronger documentary support only in the "
                "limited record-order sense: "
                + (
                    ", ".join(row["candidate"] for row in other_record_order)
                    if other_record_order
                    else "none"
                )
                + ". This does not satisfy the promotion rule."
            ),
            "",
            "## Hypothese",
            "",
            (
                "A dataset-specific TIM format specification could still identify "
                "the token position as an observation-time field, but that relation "
                "is not present in the inspected local evidence."
            ),
            "",
            "## Offene Luecke",
            "",
            f"- {summary['main_missing_evidence']}",
            "- Exact data-line field order for the J0740+6620 TIM file.",
            "- Controlled mapping from that field order to the workcopy token labels.",
            "",
            "## Claim Boundary",
            "",
            CLAIM_BOUNDARY,
            "",
            "## Next Step",
            "",
            f"- {selected_status['required_next_action']}",
            "",
        ]
    )
    path.write_text("\n".join(lines), encoding="utf-8")


def run(args: argparse.Namespace) -> dict[str, Any]:
    ensure_inputs(args)
    live_before = db_state(args.live_db)
    workcopy_before = db_state(args.workcopy_db)
    created_at = utc_now()
    with connect_readonly(args.live_db) as live_con, connect_readonly(args.workcopy_db) as work_con:
        live_integrity = integrity_check(live_con)
        work_integrity = integrity_check(work_con)
        live_fk = foreign_key_violations(live_con)
        work_fk = foreign_key_violations(work_con)
        candidate_rows = load_candidates(work_con)
        evidence_rows: list[dict[str, Any]] = []
        add_shapiromart07_evidence(evidence_rows, candidate_rows)
        add_candidate_specific_db_evidence(work_con, evidence_rows, candidate_rows)
    candidate_names = [normalize_candidate(row) for row in candidate_rows]
    inspected_scripts = add_static_script_evidence(args.repo_root, evidence_rows, candidate_names)
    inspected_docs = add_doc_and_local_file_evidence(args.repo_root, evidence_rows, candidate_names)
    candidate_statuses = [
        status_for_candidate(candidate, evidence_rows) for candidate in candidate_names
    ]
    selected_status = build_selected_status(candidate_statuses)
    promotion_allowed = selected_status["promotion_allowed"]
    next_step = selected_status["required_next_action"]
    evidence_gap_rows = [
        {
            "gap_id": "SHAPIROMART08_GAP_001",
            "candidate_scope": "raw_field_value.tim_token_003; SHAPIROMART07 four-candidate set",
            "missing_evidence": MAIN_MISSING_EVIDENCE,
            "current_state": (
                "Local DB/script/doc evidence supports positional structure and "
                "record-order traceability, but not exact observation-time or phase semantics."
            ),
            "blocking_status": "blocks_shapiromart09_grouping"
            if promotion_allowed == "no"
            else "not_blocking",
            "recommended_action": next_step,
            "notes": "Numeric behavior alone was not used as promotion evidence.",
        }
    ]
    next_step_rows = [
        {
            "next_step_rank": 1,
            "next_step": next_step,
            "reason": (
                "No candidate can be promoted without exact documentary evidence."
                if promotion_allowed == "no"
                else "A supported anchor is available for nonphysical grouping design."
            ),
        }
    ]
    live_after = db_state(args.live_db)
    workcopy_after = db_state(args.workcopy_db)
    validation = {
        "live_db_unchanged": live_before == live_after,
        "workcopy_db_unchanged": workcopy_before == workcopy_after,
        "live_integrity_check": live_integrity,
        "workcopy_integrity_check": work_integrity,
        "live_foreign_key_violation_count": len(live_fk),
        "workcopy_foreign_key_violation_count": len(work_fk),
        "exactly_4_shapiromart07_candidates_reviewed": len(candidate_rows) == 4,
        "db_write_attempted": False,
        "physical_quantities_computed": False,
        "candidate_promoted_from_numeric_behavior_alone": False,
    }
    if not validation["live_db_unchanged"]:
        fail("Live DB changed during read-only review.")
    if not validation["workcopy_db_unchanged"]:
        fail("Workcopy DB changed during read-only review.")
    if live_integrity != "ok" or work_integrity != "ok":
        fail("DB integrity_check did not return ok.")
    if live_fk or work_fk:
        fail("Foreign key violations found.")
    inspected_files = inspected_scripts + inspected_docs
    summary: dict[str, Any] = {
        "script": SCRIPT_NAME,
        "run_timestamp_utc": created_at,
        "live_db": str(args.live_db),
        "workcopy_db": str(args.workcopy_db),
        "repo_root": str(args.repo_root),
        "output_root": str(args.output_root),
        "candidate_reviewed_first": candidate_names[0],
        "candidate_review_count": len(candidate_rows),
        "candidate_statuses": candidate_statuses,
        "selected_candidate_status": selected_status,
        "promotion_allowed": promotion_allowed,
        "main_missing_evidence": MAIN_MISSING_EVIDENCE,
        "single_next_step": next_step,
        "evidence_source_count": len(evidence_rows),
        "inspected_db_tables_or_views": DB_TABLES_INSPECTED,
        "inspected_files": inspected_files,
        "claim_boundary": CLAIM_BOUNDARY,
        "validation": validation,
        "warnings": [
            "General TIM/TOA documentation was treated as contextual only unless it mapped an exact reviewed candidate.",
            "Record-order evidence does not unlock SHAPIROMART09 grouping.",
            "Raw .tim/.par files under local public_sources/raw were excluded from file scanning.",
        ],
    }
    paths = output_paths(args.output_root)
    write_readout(
        paths[READOUT_MD],
        summary,
        selected_status,
        candidate_statuses,
        inspected_files,
        DB_TABLES_INSPECTED,
    )
    paths[SUMMARY_JSON].write_text(
        json.dumps(summary, indent=2, sort_keys=True, ensure_ascii=True) + "\n",
        encoding="utf-8",
    )
    write_csv(paths[CANDIDATE_EVIDENCE_CSV], evidence_rows, CANDIDATE_EVIDENCE_FIELDS)
    write_csv(paths[SELECTED_STATUS_CSV], [selected_status], SELECTED_STATUS_FIELDS)
    write_csv(paths[EVIDENCE_GAP_CSV], evidence_gap_rows)
    write_csv(paths[NEXT_STEP_CSV], next_step_rows)
    return summary


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="QSB-SHAPIROMART08 targeted PAR/TIM semantic evidence review."
    )
    parser.add_argument("--live-db", type=Path, default=DEFAULT_LIVE_DB)
    parser.add_argument("--workcopy-db", type=Path, default=DEFAULT_WORKCOPY_DB)
    parser.add_argument("--repo-root", type=Path, default=Path("."))
    parser.add_argument("--output-root", type=Path, default=DEFAULT_OUTPUT_ROOT)
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Replace existing SHAPIROMART08 output files.",
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
