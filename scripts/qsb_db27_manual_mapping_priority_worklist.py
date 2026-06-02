#!/usr/bin/env python3
"""QSB-DB27: manual mapping priority worklist.

This DB-first consolidated Mini-DWH step uses the existing DB25/DB26 SQLite
database as its only data substrate. It creates a timestamped backup before
writing, adds only DB27-prefixed tables and views, and writes report exports
from those DB-backed results. It does not read raw TIM/PAR files and does not
assign final physical or semantic meaning to TIM token positions.
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


SCRIPT_NAME = "scripts/qsb_db27_manual_mapping_priority_worklist.py"
DEFAULT_DB = Path(
    "runs/QSB-DB/QSB_DB25_CONSOLIDATED_RESEARCH_SNAPSHOT/"
    "qsb_research_consolidated_snapshot.db"
)
DEFAULT_OUTPUT_ROOT = Path("runs/QSB-DB/QSB_DB25_CONSOLIDATED_RESEARCH_SNAPSHOT")

REQUIRED_VIEWS = [
    "qsb_v_db26_open_manual_mapping_queue",
    "qsb_v_db26_field_dictionary_seed",
    "qsb_v_db26_side_by_side_block_token_context",
    "qsb_v_db26_mapping_dashboard",
    "qsb_v_db25_two_block_signature_overview",
    "qsb_v_db25_tim_staging_and_mapping_overview",
]

OUTPUT_FILENAMES = [
    "db27_manual_mapping_priority_readout.md",
    "db27_manual_mapping_priority_summary.json",
    "db27_manual_mapping_priority_worklist.csv",
    "db27_first_mapping_work_packet.csv",
    "db27_queue_priority_dashboard.csv",
]

FOCUS_TOKENS = [
    "tim_token_007",
    "tim_token_011",
    "tim_token_013",
    "tim_token_017",
    "tim_token_023",
]
FOCUS_TOKEN_SET = set(FOCUS_TOKENS)

CLAIM_BOUNDARY = (
    "DB27 is an additive priority-worklist step over the consolidated DB25/DB26 "
    "SQLite database. It records manual mapping priority metadata and review "
    "questions only. No raw TIM/PAR file is read; no timing quantities, "
    "physical timing parameters, model quantities, inferential-statistics work, "
    "final TIM-column semantics, or physical interpretation is produced."
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


def output_paths(output_root: Path) -> dict[str, Path]:
    return {name: output_root / name for name in OUTPUT_FILENAMES}


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


def list_db27_objects(con: sqlite3.Connection) -> list[tuple[str, str]]:
    rows = con.execute(
        """
        SELECT type, name
        FROM sqlite_master
        WHERE name LIKE 'db27_%'
           OR name LIKE 'qsb_v_db27_%'
        ORDER BY type, name
        """
    ).fetchall()
    return [(str(row["type"]), str(row["name"])) for row in rows]


def ensure_preconditions(db_path: Path, output_root: Path) -> None:
    if not db_path.exists():
        raise FileNotFoundError(f"DB25/DB26 database does not exist: {db_path}")
    if not db_path.is_file():
        raise ValueError(f"DB25/DB26 path is not a file: {db_path}")
    if not output_root.exists():
        raise FileNotFoundError(f"Output root does not exist: {output_root}")
    if not output_root.is_dir():
        raise ValueError(f"Output root is not a directory: {output_root}")
    if db_path.parent.resolve() != output_root.resolve():
        raise ValueError("Output root must be the consolidated snapshot directory.")
    if db_path.stat().st_size <= 0:
        raise ValueError(f"DB25/DB26 database is empty: {db_path}")

    with connect_readonly(db_path) as con:
        missing_views = [
            view for view in REQUIRED_VIEWS
            if not object_exists(con, view, "view")
        ]
        if missing_views:
            raise RuntimeError(
                "Required DB25/DB26 view(s) missing: " + ", ".join(missing_views)
            )
        existing_db27 = list_db27_objects(con)
        if existing_db27:
            formatted = ", ".join(f"{kind}:{name}" for kind, name in existing_db27)
            raise RuntimeError("Refusing to run because DB27 objects already exist: " + formatted)

    existing_outputs = [
        str(path) for path in output_paths(output_root).values()
        if path.exists()
    ]
    if existing_outputs:
        raise FileExistsError(
            "Refusing to overwrite existing DB27 output file(s): "
            + "; ".join(existing_outputs)
        )


def create_backup(db_path: Path) -> Path:
    backup_path = db_path.with_name(
        f"{db_path.stem}.pre_db27_{timestamp_for_path()}.bak.db"
    )
    if backup_path.exists():
        raise FileExistsError(f"Backup path already exists: {backup_path}")
    shutil.copy2(db_path, backup_path)
    return backup_path


def token_sort_key(token_position: str | None) -> tuple[int, str]:
    if token_position is None:
        return (9999, "")
    match = re.search(r"(\d+)$", token_position)
    if match:
        return (int(match.group(1)), token_position)
    if token_position == "raw_line_text":
        return (0, token_position)
    return (9999, token_position)


def create_tables_and_views(con: sqlite3.Connection) -> None:
    con.executescript(
        """
        CREATE TABLE db27_mapping_priority_run_log (
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

        CREATE TABLE db27_manual_mapping_priority (
            priority_id TEXT PRIMARY KEY,
            queue_id TEXT,
            queue_type TEXT,
            token_position TEXT,
            line_family TEXT,
            issue_summary TEXT,
            required_decision TEXT,
            blocking_status TEXT,
            source_priority TEXT,
            priority_score INTEGER,
            priority_tier TEXT,
            prioritization_reason TEXT,
            created_at_utc TEXT
        );

        CREATE TABLE db27_mapping_work_packet (
            work_packet_id TEXT PRIMARY KEY,
            packet_label TEXT,
            token_position TEXT,
            block_a_value TEXT,
            block_b_value TEXT,
            relation_type TEXT,
            block_a_count INTEGER,
            block_b_count INTEGER,
            proposed_structural_name TEXT,
            required_manual_decision TEXT,
            equality_style_comparison TEXT,
            review_status TEXT,
            created_at_utc TEXT,
            CHECK (
                relation_type IN (
                    'equal',
                    'different',
                    'partial_overlap',
                    'mixed',
                    'needs_mapping'
                )
            ),
            CHECK (
                review_status IN (
                    'proposed',
                    'under_review',
                    'accepted_later',
                    'rejected_later'
                )
            )
        );

        CREATE TABLE db27_mapping_priority_rule (
            rule_id TEXT PRIMARY KEY,
            rule_name TEXT,
            rule_description TEXT,
            score_delta INTEGER,
            applies_to TEXT,
            created_at_utc TEXT
        );

        CREATE TABLE db27_mapping_review_decision_log_seed (
            decision_seed_id TEXT PRIMARY KEY,
            token_position TEXT,
            proposed_structural_name TEXT,
            source_evidence TEXT,
            current_status TEXT,
            decision_placeholder TEXT,
            created_at_utc TEXT,
            CHECK (
                current_status IN (
                    'seed_only',
                    'needs_review',
                    'ready_for_manual_decision'
                )
            )
        );

        CREATE TABLE db27_next_mapping_question (
            question_id TEXT PRIMARY KEY,
            question_rank INTEGER,
            question_text TEXT,
            related_token_positions TEXT,
            required_data_view TEXT,
            expected_decision_type TEXT,
            created_at_utc TEXT,
            CHECK (
                expected_decision_type IN (
                    'dictionary_name',
                    'grouping_key',
                    'block_context',
                    'audit_retention',
                    'other'
                )
            )
        );

        CREATE VIEW qsb_v_db27_manual_mapping_priority AS
        SELECT *
        FROM db27_manual_mapping_priority
        ORDER BY priority_score DESC, priority_tier, token_position, queue_id;

        CREATE VIEW qsb_v_db27_first_mapping_work_packet AS
        SELECT *
        FROM db27_mapping_work_packet
        WHERE packet_label = 'first_block_switch_mapping_packet'
        ORDER BY token_position;

        CREATE VIEW qsb_v_db27_mapping_priority_dashboard AS
        SELECT 'run_id' AS metric_name,
               run_id AS metric_value,
               'db27_mapping_priority_run_log' AS metric_source,
               notes AS dashboard_note
        FROM db27_mapping_priority_run_log
        UNION ALL
        SELECT 'manual_priority_rows',
               CAST(COUNT(*) AS TEXT),
               'db27_manual_mapping_priority',
               'Manual mapping queue rows prioritized from DB26.'
        FROM db27_manual_mapping_priority
        UNION ALL
        SELECT 'tier_1_first_work_packet_rows',
               CAST(COUNT(*) AS TEXT),
               'db27_manual_mapping_priority',
               'Highest priority block-switch queue rows.'
        FROM db27_manual_mapping_priority
        WHERE priority_tier = 'tier_1_first_work_packet'
        UNION ALL
        SELECT 'first_work_packet_tokens',
               CAST(COUNT(*) AS TEXT),
               'db27_mapping_work_packet',
               'Focused block-switch token work packet rows.'
        FROM db27_mapping_work_packet
        UNION ALL
        SELECT 'decision_seed_rows',
               CAST(COUNT(*) AS TEXT),
               'db27_mapping_review_decision_log_seed',
               'Seed rows for later manual mapping decisions.'
        FROM db27_mapping_review_decision_log_seed
        UNION ALL
        SELECT 'next_mapping_question_rows',
               CAST(COUNT(*) AS TEXT),
               'db27_next_mapping_question',
               'Concrete next mapping questions.'
        FROM db27_next_mapping_question
        UNION ALL
        SELECT 'foreign_key_violation_count',
               CAST(foreign_key_violation_count AS TEXT),
               'PRAGMA foreign_key_check',
               'SQLite foreign-key check result after DB27 insertions.'
        FROM db27_mapping_priority_run_log;

        CREATE VIEW qsb_v_db27_mapping_review_decision_seed AS
        SELECT *
        FROM db27_mapping_review_decision_log_seed
        ORDER BY
            CASE current_status
                WHEN 'ready_for_manual_decision' THEN 1
                WHEN 'needs_review' THEN 2
                ELSE 3
            END,
            token_position,
            decision_seed_id;

        CREATE VIEW qsb_v_db27_next_mapping_questions AS
        SELECT *
        FROM db27_next_mapping_question
        ORDER BY question_rank;
        """
    )


def build_priority_rules(created_at: str) -> list[dict[str, Any]]:
    raw_rules = [
        (
            "block_switch_token",
            "Queue item is a DB26 block-switch token.",
            100,
            "queue_type=block_switch_token",
        ),
        (
            "focused_two_block_token",
            "Token is one of the five focused two-block switch tokens.",
            80,
            "token_position in first work packet token set",
        ),
        (
            "blocks_staging",
            "Queue item blocks staging.",
            60,
            "blocking_status=blocks_staging",
        ),
        (
            "high_source_priority",
            "DB26 source priority is high.",
            50,
            "priority=high",
        ),
        (
            "candidate_dictionary_seed",
            "Mapping gap is already a candidate for dictionary seed work.",
            40,
            "queue_type=mapping_gap; issue contains candidate_for_dictionary_seed",
        ),
        (
            "candidate_grouping_token",
            "Dictionary seed marks the token as a candidate grouping token.",
            30,
            "db26_field_dictionary_seed.structural_role_candidate=candidate_grouping_token",
        ),
        (
            "blocks_analysis_only",
            "Queue item blocks analysis only.",
            20,
            "blocking_status=blocks_analysis_only",
        ),
        (
            "medium_source_priority",
            "DB26 source priority is medium.",
            10,
            "priority=medium",
        ),
        (
            "audit_or_context_retention",
            "Audit/context-only rows are retained with low score.",
            5,
            "issue/status contains audit or context retention",
        ),
        (
            "low_source_priority",
            "DB26 source priority is low; no positive score is added.",
            0,
            "priority=low",
        ),
    ]
    return [
        {
            "rule_id": f"db27_rule_{idx:03d}",
            "rule_name": name,
            "rule_description": description,
            "score_delta": delta,
            "applies_to": applies_to,
            "created_at_utc": created_at,
        }
        for idx, (name, description, delta, applies_to) in enumerate(raw_rules, start=1)
    ]


def seed_by_key(con: sqlite3.Connection) -> dict[tuple[str | None, str | None], dict[str, Any]]:
    rows = fetch_dicts(
        con,
        """
        SELECT line_family, token_position, proposed_structural_name,
               structural_role_candidate, mapping_status, evidence_source,
               evidence_summary, manual_review_required, confidence_class
        FROM qsb_v_db26_field_dictionary_seed
        """
    )
    return {
        (row["line_family"], row["token_position"]): row
        for row in rows
    }


def priority_score_and_tier(
    queue_row: dict[str, Any],
    seed_row: dict[str, Any] | None,
) -> tuple[int, str, str]:
    score = 0
    reasons: list[str] = []
    token_position = queue_row["token_position"]
    queue_type = queue_row["queue_type"]
    issue_summary = queue_row["issue_summary"] or ""
    blocking_status = queue_row["blocking_status"]
    source_priority = queue_row["priority"]
    structural_role = seed_row["structural_role_candidate"] if seed_row else None

    if queue_type == "block_switch_token":
        score += 100
        reasons.append("+100 block_switch_token queue item")
    if token_position in FOCUS_TOKEN_SET:
        score += 80
        reasons.append("+80 focused two-block token")
    if blocking_status == "blocks_staging":
        score += 60
        reasons.append("+60 blocks staging")
    if source_priority == "high":
        score += 50
        reasons.append("+50 high source priority")
    if queue_type == "mapping_gap" and "candidate_for_dictionary_seed" in issue_summary:
        score += 40
        reasons.append("+40 candidate dictionary seed gap")
    if structural_role == "candidate_grouping_token":
        score += 30
        reasons.append("+30 candidate grouping token")
    if blocking_status == "blocks_analysis_only":
        score += 20
        reasons.append("+20 blocks analysis only")
    if source_priority == "medium":
        score += 10
        reasons.append("+10 medium source priority")
    if (
        "retained_for_audit" in issue_summary
        or "context" in issue_summary
        or structural_role in {"audit_raw_line", "context_token"}
    ):
        score += 5
        reasons.append("+5 audit/context retention")
    if not reasons:
        reasons.append("no positive priority rule matched")

    if queue_type == "block_switch_token":
        tier = "tier_1_first_work_packet"
    elif blocking_status == "blocks_staging":
        tier = "tier_2_staging_blockers"
    elif queue_type == "mapping_gap" and "candidate_for_dictionary_seed" in issue_summary:
        tier = "tier_4_grouping_context" if structural_role == "candidate_grouping_token" else "tier_3_dictionary_seed_candidates"
    elif structural_role == "candidate_grouping_token":
        tier = "tier_4_grouping_context"
    else:
        tier = "tier_5_audit_context"

    return score, tier, "; ".join(reasons)


def build_manual_mapping_priority(
    con: sqlite3.Connection,
    created_at: str,
) -> list[dict[str, Any]]:
    seeds = seed_by_key(con)
    queue_rows = fetch_dicts(
        con,
        """
        SELECT queue_id, queue_type, priority, token_position, line_family,
               issue_summary, required_decision, blocking_status
        FROM qsb_v_db26_open_manual_mapping_queue
        """
    )
    priority_rows: list[dict[str, Any]] = []
    for idx, queue_row in enumerate(queue_rows, start=1):
        seed_row = seeds.get((queue_row["line_family"], queue_row["token_position"]))
        score, tier, reason = priority_score_and_tier(queue_row, seed_row)
        priority_rows.append(
            {
                "priority_id": f"db27_priority_{idx:04d}",
                "queue_id": queue_row["queue_id"],
                "queue_type": queue_row["queue_type"],
                "token_position": queue_row["token_position"],
                "line_family": queue_row["line_family"],
                "issue_summary": queue_row["issue_summary"],
                "required_decision": queue_row["required_decision"],
                "blocking_status": queue_row["blocking_status"],
                "source_priority": queue_row["priority"],
                "priority_score": score,
                "priority_tier": tier,
                "prioritization_reason": reason,
                "created_at_utc": created_at,
            }
        )
    priority_rows.sort(
        key=lambda row: (
            -int(row["priority_score"]),
            row["priority_tier"],
            token_sort_key(row["token_position"]),
            row["queue_id"] or "",
        )
    )
    for idx, row in enumerate(priority_rows, start=1):
        row["priority_id"] = f"db27_priority_{idx:04d}"
    return priority_rows


def build_work_packet(
    con: sqlite3.Connection,
    created_at: str,
) -> list[dict[str, Any]]:
    seeds = seed_by_key(con)
    queue_rows = fetch_dicts(
        con,
        """
        SELECT token_position, required_decision
        FROM qsb_v_db26_open_manual_mapping_queue
        WHERE queue_type = 'block_switch_token'
        """
    )
    decision_by_token = {
        row["token_position"]: row["required_decision"]
        for row in queue_rows
    }
    placeholders = ",".join("?" for _ in FOCUS_TOKENS)
    side_rows = fetch_dicts(
        con,
        f"""
        SELECT token_position, block_a_value, block_b_value, relation_type,
               block_a_count, block_b_count
        FROM qsb_v_db26_side_by_side_block_token_context
        WHERE token_position IN ({placeholders})
        """,
        tuple(FOCUS_TOKENS),
    )
    side_by_token = {row["token_position"]: row for row in side_rows}
    missing = [token for token in FOCUS_TOKENS if token not in side_by_token]
    if missing:
        raise RuntimeError(
            "Focused block-switch side-by-side rows missing: " + ", ".join(missing)
        )

    packet_rows: list[dict[str, Any]] = []
    for idx, token in enumerate(FOCUS_TOKENS, start=1):
        side = side_by_token[token]
        seed = seeds.get(("data_line", token), {})
        proposed_name = seed.get("proposed_structural_name") or f"db27_candidate_{token}"
        required_decision = decision_by_token.get(
            token,
            "Decide whether and how this structural block-switch token should be named.",
        )
        comparison = (
            f"{token}: Block A value '{side['block_a_value']}' "
            f"vs Block B value '{side['block_b_value']}' "
            f"(relation={side['relation_type']}; "
            f"counts={side['block_a_count']} vs {side['block_b_count']})."
        )
        packet_rows.append(
            {
                "work_packet_id": f"db27_packet_{idx:04d}",
                "packet_label": "first_block_switch_mapping_packet",
                "token_position": token,
                "block_a_value": side["block_a_value"],
                "block_b_value": side["block_b_value"],
                "relation_type": side["relation_type"],
                "block_a_count": side["block_a_count"],
                "block_b_count": side["block_b_count"],
                "proposed_structural_name": proposed_name,
                "required_manual_decision": required_decision,
                "equality_style_comparison": comparison,
                "review_status": "proposed",
                "created_at_utc": created_at,
            }
        )
    return packet_rows


def build_decision_seed_rows(
    con: sqlite3.Connection,
    created_at: str,
) -> list[dict[str, Any]]:
    seed_rows = fetch_dicts(
        con,
        """
        SELECT line_family, token_position, proposed_structural_name,
               structural_role_candidate, mapping_status, evidence_source,
               manual_review_required
        FROM qsb_v_db26_field_dictionary_seed
        WHERE manual_review_required = 1
        ORDER BY line_family, token_position
        """
    )
    rows: list[dict[str, Any]] = []
    for idx, seed in enumerate(seed_rows, start=1):
        if seed["token_position"] in FOCUS_TOKEN_SET:
            current_status = "ready_for_manual_decision"
        elif seed["mapping_status"] == "seed_only":
            current_status = "seed_only"
        else:
            current_status = "needs_review"
        rows.append(
            {
                "decision_seed_id": f"db27_decision_seed_{idx:04d}",
                "token_position": seed["token_position"],
                "proposed_structural_name": seed["proposed_structural_name"],
                "source_evidence": (
                    f"{seed['evidence_source']}; "
                    f"line_family={seed['line_family']}; "
                    f"structural_role_candidate={seed['structural_role_candidate']}; "
                    f"mapping_status={seed['mapping_status']}"
                ),
                "current_status": current_status,
                "decision_placeholder": "",
                "created_at_utc": created_at,
            }
        )
    return rows


def build_next_questions(created_at: str) -> list[dict[str, Any]]:
    question_specs = [
        (
            "Are tim_token_007, tim_token_011, and tim_token_017 different representations of the same receiver/setup context?",
            "tim_token_007,tim_token_011,tim_token_017",
            "qsb_v_db27_first_mapping_work_packet",
            "block_context",
        ),
        (
            "Do tim_token_013 and tim_token_023 functionally scale together with the same block switch?",
            "tim_token_013,tim_token_023",
            "qsb_v_db27_first_mapping_work_packet",
            "block_context",
        ),
        (
            "Does tim_token_001 define finer observation/file blocks inside the two main blocks?",
            "tim_token_001",
            "qsb_v_db27_manual_mapping_priority",
            "grouping_key",
        ),
        (
            "Which DB view should become the human review screen for field dictionary decisions?",
            "",
            "qsb_v_db27_mapping_review_decision_seed",
            "other",
        ),
        (
            "Which mapping decision can be promoted first from seed_only to controlled_definition_candidate?",
            "",
            "qsb_v_db27_mapping_review_decision_seed",
            "dictionary_name",
        ),
        (
            "Should the first block-switch work packet be reviewed as one coupled package or as five independent token decisions?",
            ",".join(FOCUS_TOKENS),
            "qsb_v_db27_first_mapping_work_packet",
            "block_context",
        ),
        (
            "Which candidate_grouping_token rows should be reviewed immediately after the first block-switch packet?",
            "tim_token_001,tim_token_025,tim_token_027",
            "qsb_v_db27_manual_mapping_priority",
            "grouping_key",
        ),
        (
            "Which audit/context queue entries can remain retained_for_audit without blocking dictionary work?",
            "raw_line_text",
            "qsb_v_db27_manual_mapping_priority",
            "audit_retention",
        ),
    ]
    return [
        {
            "question_id": f"db27_question_{idx:03d}",
            "question_rank": idx,
            "question_text": question,
            "related_token_positions": tokens,
            "required_data_view": view_name,
            "expected_decision_type": decision_type,
            "created_at_utc": created_at,
        }
        for idx, (question, tokens, view_name, decision_type)
        in enumerate(question_specs, start=1)
    ]


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


def first_rows(
    con: sqlite3.Connection,
    source_name: str,
    limit: int = 5,
) -> list[dict[str, Any]]:
    return fetch_dicts(con, f"SELECT * FROM {source_name} LIMIT ?", (limit,))


def write_csv(con: sqlite3.Connection, path: Path, source_name: str) -> None:
    cur = con.execute(f"SELECT * FROM {source_name}")
    columns = [description[0] for description in cur.description]
    rows = cur.fetchall()
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(columns)
        for row in rows:
            writer.writerow([row[column] for column in columns])


def build_summary(
    con: sqlite3.Connection,
    db_path: Path,
    backup_path: Path,
    output_root: Path,
    run_id: str,
    created_at: str,
    fk_violations: list[sqlite3.Row],
) -> dict[str, Any]:
    db27_tables = [
        "db27_mapping_priority_run_log",
        "db27_manual_mapping_priority",
        "db27_mapping_work_packet",
        "db27_mapping_priority_rule",
        "db27_mapping_review_decision_log_seed",
        "db27_next_mapping_question",
    ]
    db27_views = [
        "qsb_v_db27_manual_mapping_priority",
        "qsb_v_db27_first_mapping_work_packet",
        "qsb_v_db27_mapping_priority_dashboard",
        "qsb_v_db27_mapping_review_decision_seed",
        "qsb_v_db27_next_mapping_questions",
    ]
    return {
        "run_id": run_id,
        "run_timestamp_utc": created_at,
        "data_substrate": str(db_path),
        "db25_db26_updated_additively": True,
        "backup_db_path": str(backup_path),
        "new_isolated_analysis_db_created": False,
        "raw_files_read": False,
        "script_name": SCRIPT_NAME,
        "claim_boundary": CLAIM_BOUNDARY,
        "db27_tables": db27_tables,
        "db27_views": db27_views,
        "row_counts": {table: table_count(con, table) for table in db27_tables},
        "priority_tier_counts": counts_by(
            con,
            "db27_manual_mapping_priority",
            "priority_tier",
        ),
        "queue_type_counts": counts_by(
            con,
            "db27_manual_mapping_priority",
            "queue_type",
        ),
        "work_packet": first_rows(
            con,
            "qsb_v_db27_first_mapping_work_packet",
            10,
        ),
        "next_mapping_questions": first_rows(
            con,
            "qsb_v_db27_next_mapping_questions",
            10,
        ),
        "first_dashboard_rows": first_rows(
            con,
            "qsb_v_db27_mapping_priority_dashboard",
            20,
        ),
        "foreign_key_violation_count": len(fk_violations),
        "output_files": {name: str(output_root / name) for name in OUTPUT_FILENAMES},
    }


def write_readout(path: Path, summary: dict[str, Any]) -> None:
    row_counts = summary["row_counts"]
    work_packet_lines = [
        "- {token_position}: {block_a_value} ({block_a_count}) vs "
        "{block_b_value} ({block_b_count}); relation={relation_type}; "
        "name={proposed_structural_name}".format(**row)
        for row in summary["work_packet"]
    ]
    question_lines = [
        f"- {row['question_rank']}. {row['question_text']} "
        f"[view: {row['required_data_view']}]"
        for row in summary["next_mapping_questions"]
    ]
    content = f"""# QSB-DB27 Manual Mapping Priority Worklist

## Befund

- Data substrate: `{summary['data_substrate']}`
- DB25/DB26 update mode: additive in-place DB27 tables/views only
- Backup DB: `{summary['backup_db_path']}`
- Manual priority rows: {row_counts['db27_manual_mapping_priority']}
- First work packet rows: {row_counts['db27_mapping_work_packet']}
- Priority rules recorded: {row_counts['db27_mapping_priority_rule']}
- Decision-log seed rows: {row_counts['db27_mapping_review_decision_log_seed']}
- Next mapping questions: {row_counts['db27_next_mapping_question']}
- FK violation count: {summary['foreign_key_violation_count']}

## Interpretation

The DB26 manual queue can be ordered structurally from the consolidated DB.
The first work packet is the five focused block-switch tokens because they have
side-by-side Block A / Block B context and are already marked as high-value
manual review items.

Priority tier counts:

```json
{pretty_json(summary['priority_tier_counts'])}
```

## Hypothese

The first controlled mapping review should treat the five focused tokens as a
single work packet before lower-priority dictionary seeds and audit/context
entries are reviewed. This is a worklist hypothesis, not a physical or final
semantic assignment.

First mapping work packet:

{chr(10).join(work_packet_lines)}

## Offene Luecke

The table `db27_mapping_review_decision_log_seed` is only a seed for later
manual decisions. It contains placeholders and does not record accepted field
definitions.

Next mapping questions:

{chr(10).join(question_lines)}

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
    write_readout(paths["db27_manual_mapping_priority_readout.md"], summary)
    paths["db27_manual_mapping_priority_summary.json"].write_text(
        pretty_json(summary) + "\n",
        encoding="utf-8",
    )
    write_csv(
        con,
        paths["db27_manual_mapping_priority_worklist.csv"],
        "qsb_v_db27_manual_mapping_priority",
    )
    write_csv(
        con,
        paths["db27_first_mapping_work_packet.csv"],
        "qsb_v_db27_first_mapping_work_packet",
    )
    write_csv(
        con,
        paths["db27_queue_priority_dashboard.csv"],
        "qsb_v_db27_mapping_priority_dashboard",
    )


def execute(db_path: Path, output_root: Path) -> dict[str, Any]:
    ensure_preconditions(db_path, output_root)
    backup_path = create_backup(db_path)
    created_at = utc_now()
    run_id = "DB27_MANUAL_MAPPING_PRIORITY_WORKLIST_" + timestamp_for_path()

    with connect_db(db_path) as con:
        con.execute("BEGIN IMMEDIATE")
        try:
            create_tables_and_views(con)
            rule_rows = build_priority_rules(created_at)
            priority_rows = build_manual_mapping_priority(con, created_at)
            work_packet_rows = build_work_packet(con, created_at)
            decision_seed_rows = build_decision_seed_rows(con, created_at)
            question_rows = build_next_questions(created_at)

            insert_rows(con, "db27_mapping_priority_rule", rule_rows)
            insert_rows(con, "db27_manual_mapping_priority", priority_rows)
            insert_rows(con, "db27_mapping_work_packet", work_packet_rows)
            insert_rows(
                con,
                "db27_mapping_review_decision_log_seed",
                decision_seed_rows,
            )
            insert_rows(con, "db27_next_mapping_question", question_rows)

            fk_violations = con.execute("PRAGMA foreign_key_check").fetchall()
            total_rows_inserted = (
                len(rule_rows)
                + len(priority_rows)
                + len(work_packet_rows)
                + len(decision_seed_rows)
                + len(question_rows)
                + 1
            )
            con.execute(
                """
                INSERT INTO db27_mapping_priority_run_log (
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
                    "DB27 added only DB27-prefixed priority worklist tables/views and report files.",
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
            "QSB-DB27 manual mapping priority worklist over the existing "
            "DB25/DB26 consolidated SQLite database."
        )
    )
    parser.add_argument(
        "--db",
        type=Path,
        default=DEFAULT_DB,
        help="Path to the DB25/DB26 consolidated SQLite database.",
    )
    parser.add_argument(
        "--output-root",
        type=Path,
        default=DEFAULT_OUTPUT_ROOT,
        help="Existing consolidated output directory for DB27 reports and backup.",
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
