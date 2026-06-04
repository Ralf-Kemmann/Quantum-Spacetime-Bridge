#!/usr/bin/env python3
"""QSB-DWH16A: read-only DBeaver/manual inspection package.

This script opens the live and workcopy DBs read-only, inspects DWH14A/DWH15A
candidate separation, and writes a compact output package for manual review.
It does not create, alter, or update database objects.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import sqlite3
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


SCRIPT_NAME = "scripts/qsb_dwh16a_dbeaver_candidate_separation_inspection.py"
DEFAULT_LIVE_DB = Path(
    "runs/QSB-DB/QSB_DB25_CONSOLIDATED_RESEARCH_SNAPSHOT/"
    "qsb_research_consolidated_snapshot.db"
)
DEFAULT_WORKCOPY_DB = Path(
    "runs/QSB-DB/QSB_DB25_CONSOLIDATED_RESEARCH_SNAPSHOT/"
    "qsb_research_dwh_target_workcopy_dwh03.db"
)
DEFAULT_OUTPUT_ROOT = Path("runs/QSB-DB/QSB_DB25_CONSOLIDATED_RESEARCH_SNAPSHOT")

READOUT_MD = "dwh16a_dbeaver_candidate_separation_inspection_readout.md"
SUMMARY_JSON = "dwh16a_dbeaver_candidate_separation_inspection_summary.json"
STATUS_CSV = "dwh16a_candidate_separation_status.csv"
CHECKLIST_CSV = "dwh16a_dbeaver_inspection_checklist.csv"
NEXT_STEPS_CSV = "dwh16a_next_dwh_steps.csv"

OUTPUT_FILENAMES = [
    READOUT_MD,
    SUMMARY_JSON,
    STATUS_CSV,
    CHECKLIST_CSV,
    NEXT_STEPS_CSV,
]

REQUIRED_TABLES = [
    "dwh14a_manual_evidence_decision",
    "dwh15a_mapping_review_status_update",
    "dwh15a_mapping_review_status_skip",
    "dwh15a_mapping_review_status_update_run_log",
]

REQUIRED_VIEWS = [
    "qsb_v_dwh14a_supported_candidate_terms",
    "qsb_v_dwh14a_open_or_conflict_terms",
    "qsb_v_dwh14a_high_priority_decision_status",
    "qsb_v_dwh15a_mapping_review_update_dashboard",
    "qsb_v_dwh15a_supported_review_ready_candidates",
    "qsb_v_dwh15a_skipped_deferred_candidates",
    "qsb_v_dwh15a_next_mapping_actions",
]

SUPPORTED_TERMS = {
    ("tim_token_011", "GUPPI"),
    ("tim_token_007", "Rcvr_800"),
    ("tim_token_007", "Rcvr1_2"),
}

DEFERRED_TERMS = {
    ("tim_token_011", "Rcvr_800_GUPPI"),
    ("tim_token_011", "Rcvr1_2_GUPPI"),
}

TERM_ORDER = {
    ("tim_token_011", "GUPPI"): 1,
    ("tim_token_007", "Rcvr_800"): 2,
    ("tim_token_007", "Rcvr1_2"): 3,
    ("tim_token_011", "Rcvr_800_GUPPI"): 4,
    ("tim_token_011", "Rcvr1_2_GUPPI"): 5,
}

CLAIM_BOUNDARY = (
    "DWH16A is a read-only inspection support step for the DWH14A/DWH15A "
    "candidate separation. It writes report files only. It does not modify DBs, "
    "does not assign final semantics, does not create bridge/result tables, "
    "does not retrieve live sources, and does not perform physics analysis."
)


def utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def pretty_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=True, indent=2)


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


def table_count(con: sqlite3.Connection, table_name: str) -> int:
    row = con.execute(f'SELECT COUNT(*) AS n FROM "{table_name}"').fetchone()
    return int(row["n"])


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


def ensure_paths(live_db: Path, workcopy_db: Path, output_root: Path) -> None:
    if not live_db.exists() or not live_db.is_file():
        raise FileNotFoundError(f"Live DB file missing: {live_db}")
    if not workcopy_db.exists() or not workcopy_db.is_file():
        raise FileNotFoundError(f"Workcopy DB file missing: {workcopy_db}")
    if not output_root.exists() or not output_root.is_dir():
        raise FileNotFoundError(f"Output root missing: {output_root}")


def ensure_no_outputs(output_root: Path, overwrite: bool) -> None:
    existing = [str(path) for path in output_paths(output_root).values() if path.exists()]
    if existing and not overwrite:
        raise FileExistsError(
            "Refusing to overwrite existing DWH16A output file(s): "
            + "; ".join(existing)
        )


def status(status_bool: bool) -> str:
    return "passed" if status_bool else "failed"


def term_key(row: dict[str, Any]) -> tuple[int, str]:
    return (
        TERM_ORDER.get((str(row.get("token_position")), str(row.get("term"))), 99),
        str(row.get("term")),
    )


def fetch_inspection_inputs(con: sqlite3.Connection) -> dict[str, Any]:
    dwh14_high = sorted(
        fetch_dicts(
            con,
            """
            SELECT token_position, term, proposed_role,
                   dwh14a_decision_status, evidence_strength,
                   safe_to_promote, proposed_next_mapping_status, notes
            FROM qsb_v_dwh14a_high_priority_decision_status
            """,
        ),
        key=term_key,
    )
    dwh14_supported = sorted(
        fetch_dicts(
            con,
            """
            SELECT token_position, term, decision_status, evidence_strength, next_action
            FROM qsb_v_dwh14a_supported_candidate_terms
            """,
        ),
        key=term_key,
    )
    dwh14_open = sorted(
        fetch_dicts(
            con,
            """
            SELECT token_position, term, decision_status, evidence_strength, next_action
            FROM qsb_v_dwh14a_open_or_conflict_terms
            """,
        ),
        key=term_key,
    )
    dwh15_supported = sorted(
        fetch_dicts(
            con,
            """
            SELECT token_position, term, dwh14a_decision_status,
                   dwh14a_evidence_strength, update_action, safe_to_promote,
                   new_mapping_status, new_review_status, notes
            FROM qsb_v_dwh15a_supported_review_ready_candidates
            """,
        ),
        key=term_key,
    )
    dwh15_skipped = sorted(
        fetch_dicts(
            con,
            """
            SELECT token_position, term, dwh14a_decision_status,
                   dwh14a_evidence_strength, skip_reason, safe_to_promote, notes
            FROM qsb_v_dwh15a_skipped_deferred_candidates
            """,
        ),
        key=term_key,
    )
    dashboard = fetch_dicts(
        con,
        """
        SELECT metric_name, metric_value
        FROM qsb_v_dwh15a_mapping_review_update_dashboard
        """,
    )
    run_log = fetch_dicts(
        con,
        """
        SELECT operation_mode, forbidden_update_count
        FROM dwh15a_mapping_review_status_update_run_log
        ORDER BY run_timestamp_utc DESC
        LIMIT 1
        """,
    )
    return {
        "dwh14_high": dwh14_high,
        "dwh14_supported": dwh14_supported,
        "dwh14_open": dwh14_open,
        "dwh15_supported": dwh15_supported,
        "dwh15_skipped": dwh15_skipped,
        "dashboard": dashboard,
        "run_log": run_log[0] if run_log else {},
    }


def preflight(
    live_db: Path,
    workcopy_db: Path,
    output_root: Path,
    overwrite: bool,
) -> dict[str, Any]:
    ensure_paths(live_db, workcopy_db, output_root)
    ensure_no_outputs(output_root, overwrite)
    live_before = db_state(live_db)
    workcopy_before = db_state(workcopy_db)

    with connect_readonly(live_db) as live_con:
        live_integrity = integrity_check(live_con)
        live_fk = foreign_key_violations(live_con)
    if live_integrity != "ok":
        raise RuntimeError(f"Live DB integrity_check failed: {live_integrity}")
    if live_fk:
        raise RuntimeError(f"Live DB foreign_key_check returned {len(live_fk)} row(s).")

    with connect_readonly(workcopy_db) as con:
        workcopy_integrity = integrity_check(con)
        workcopy_fk = foreign_key_violations(con)
        missing_tables = [
            table for table in REQUIRED_TABLES
            if not object_exists(con, table, "table")
        ]
        missing_views = [
            view for view in REQUIRED_VIEWS
            if not object_exists(con, view, "view")
        ]
        if missing_tables:
            raise RuntimeError("Missing required table(s): " + ", ".join(missing_tables))
        if missing_views:
            raise RuntimeError("Missing required view(s): " + ", ".join(missing_views))
        inputs = fetch_inspection_inputs(con)

    if workcopy_integrity != "ok":
        raise RuntimeError(f"Workcopy integrity_check failed: {workcopy_integrity}")
    if workcopy_fk:
        raise RuntimeError(f"Workcopy foreign_key_check returned {len(workcopy_fk)} row(s).")

    return {
        "live_before": live_before,
        "workcopy_before": workcopy_before,
        "live_integrity": live_integrity,
        "live_fk_count": len(live_fk),
        "workcopy_integrity": workcopy_integrity,
        "workcopy_fk_count": len(workcopy_fk),
        "inputs": inputs,
    }


def build_status_rows(inputs: dict[str, Any]) -> list[dict[str, Any]]:
    dwh15_supported = {
        (row["token_position"], row["term"]): row
        for row in inputs["dwh15_supported"]
    }
    dwh15_skipped = {
        (row["token_position"], row["term"]): row
        for row in inputs["dwh15_skipped"]
    }
    rows: list[dict[str, Any]] = []
    for row in inputs["dwh14_high"]:
        pair = (row["token_position"], row["term"])
        if pair in dwh15_supported:
            dwh15 = dwh15_supported[pair]
            status_group = "supported_review_ready"
            action_value = dwh15["update_action"]
            inspection_status = "passed"
            notes = "Candidate support is additive/review-ready only."
        elif pair in dwh15_skipped:
            dwh15 = dwh15_skipped[pair]
            status_group = "deferred_open"
            action_value = "skipped"
            inspection_status = "passed"
            notes = "Compound label remains deferred and needs direct dataset/pipeline evidence."
        else:
            dwh15 = {}
            status_group = "missing_dwh15_status"
            action_value = "missing"
            inspection_status = "failed"
            notes = "No DWH15A supported or skipped row found."
        rows.append(
            {
                "term": row["term"],
                "token_position": row["token_position"],
                "dwh14a_decision_status": row["dwh14a_decision_status"],
                "dwh14a_evidence_strength": row["evidence_strength"],
                "dwh15a_status_group": status_group,
                "dwh15a_action": action_value,
                "safe_to_promote": dwh15.get("safe_to_promote", row.get("safe_to_promote")),
                "final_semantics_assigned": "no",
                "inspection_status": inspection_status,
                "notes": notes,
            }
        )
    return sorted(rows, key=term_key)


def build_checklist(inputs: dict[str, Any], status_rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    dwh14_supported_terms = {
        (row["token_position"], row["term"]) for row in inputs["dwh14_supported"]
    }
    dwh14_open_terms = {
        (row["token_position"], row["term"]) for row in inputs["dwh14_open"]
    }
    dwh15_supported_terms = {
        (row["token_position"], row["term"]) for row in inputs["dwh15_supported"]
    }
    dwh15_skipped_terms = {
        (row["token_position"], row["term"]) for row in inputs["dwh15_skipped"]
    }
    run_log = inputs["run_log"]
    dashboard = {row["metric_name"]: row["metric_value"] for row in inputs["dashboard"]}
    checks = [
        (
            "CHK01",
            "Open workcopy DB in DBeaver",
            "Use read-only/manual inspection against the workcopy DB path.",
            "Workcopy DB opened read-only by script; DBeaver should open the same path without schema sync.",
            True,
            "Path is included in the readout.",
        ),
        (
            "CHK02",
            "Inspect qsb_v_dwh14a_high_priority_decision_status",
            "Five high-priority terms visible.",
            f"{len(inputs['dwh14_high'])} rows visible.",
            len(inputs["dwh14_high"]) == 5,
            "Expected three supported and two deferred rows.",
        ),
        (
            "CHK03",
            "Inspect qsb_v_dwh15a_supported_review_ready_candidates",
            "Three supported/review-ready rows.",
            f"{len(inputs['dwh15_supported'])} rows: {', '.join(row['term'] for row in inputs['dwh15_supported'])}",
            dwh15_supported_terms == SUPPORTED_TERMS,
            "Supported set must be GUPPI, Rcvr_800, Rcvr1_2.",
        ),
        (
            "CHK04",
            "Inspect qsb_v_dwh15a_skipped_deferred_candidates",
            "Two skipped/deferred compound rows.",
            f"{len(inputs['dwh15_skipped'])} rows: {', '.join(row['term'] for row in inputs['dwh15_skipped'])}",
            dwh15_skipped_terms == DEFERRED_TERMS,
            "Deferred set must be Rcvr_800_GUPPI and Rcvr1_2_GUPPI.",
        ),
        (
            "CHK05",
            "Confirm 3 supported and 2 deferred",
            "3 supported, 2 deferred/open.",
            f"{len(dwh14_supported_terms)} supported, {len(dwh14_open_terms)} deferred/open.",
            dwh14_supported_terms == SUPPORTED_TERMS and dwh14_open_terms == DEFERRED_TERMS,
            "This checks the DWH14A split.",
        ),
        (
            "CHK06",
            "Confirm DWH15A update mode is additive only",
            "Run log operation mode contains additive_only.",
            str(run_log.get("operation_mode")),
            "additive_only" in str(run_log.get("operation_mode", "")),
            "No direct map update is expected.",
        ),
        (
            "CHK07",
            "Confirm forbidden update count is zero",
            "forbidden_update_count = 0.",
            str(dashboard.get("forbidden_update_count")),
            str(dashboard.get("forbidden_update_count")) == "0",
            "Dashboard source is qsb_v_dwh15a_mapping_review_update_dashboard.",
        ),
        (
            "CHK08",
            "Confirm no final semantics or physics interpretation",
            "All status rows have final_semantics_assigned = no.",
            ", ".join(sorted({row["final_semantics_assigned"] for row in status_rows})),
            all(row["final_semantics_assigned"] == "no" for row in status_rows),
            "DWH16A is inspection support only.",
        ),
        (
            "CHK09",
            "Confirm compound labels still need direct dataset evidence",
            "Skipped compound labels remain deferred/open.",
            ", ".join(row["term"] for row in inputs["dwh15_skipped"]),
            dwh15_skipped_terms == DEFERRED_TERMS,
            "No compound label is marked review-ready.",
        ),
        (
            "CHK10",
            "Confirm supported candidate status is candidate/review-ready only",
            "Supported rows are candidate/review-ready, not final.",
            ", ".join(row["new_review_status"] for row in inputs["dwh15_supported"]),
            all(
                row["new_review_status"] == "review_ready_supported_candidate"
                for row in inputs["dwh15_supported"]
            ),
            "DWH15A status is additive candidate status.",
        ),
    ]
    return [
        {
            "checklist_id": checklist_id,
            "inspection_question": question,
            "expected_result": expected,
            "actual_result": actual,
            "status": status(ok),
            "notes": notes,
        }
        for checklist_id, question, expected, actual, ok, notes in checks
    ]


def next_dwh_steps_rows() -> list[dict[str, str]]:
    return [
        {
            "next_step_id": "DWH17_A",
            "next_step_name": "Manual evidence follow-up for compound labels only",
            "prerequisite": "DWH16A inspection confirms compound labels remain deferred/open",
            "recommended_action": "Collect direct dataset/pipeline evidence for Rcvr_800_GUPPI and Rcvr1_2_GUPPI.",
            "risk_level": "medium",
            "notes": "Recommended if compound labels are still needed.",
        },
        {
            "next_step_id": "DWH17_B",
            "next_step_name": "Minimal Shapiro-Mart design gate",
            "prerequisite": "Supported/open candidate separation is reviewed",
            "recommended_action": "Draft a bounded design question using status separation only; create no result tables yet.",
            "risk_level": "high",
            "notes": "Do not compute quantities.",
        },
        {
            "next_step_id": "DWH17_C",
            "next_step_name": "DWH status consolidation note / architecture checkpoint",
            "prerequisite": "DWH16A checklist is passed",
            "recommended_action": "Write a compact architecture checkpoint summarizing DWH14A-DWH16A boundaries.",
            "risk_level": "low",
            "notes": "Useful for audit continuity.",
        },
        {
            "next_step_id": "DWH17_D",
            "next_step_name": "Pause DWH build and inspect current workcopy visually",
            "prerequisite": "DWH16A output package exists",
            "recommended_action": "Use DBeaver to inspect the listed views before further DWH construction.",
            "risk_level": "low",
            "notes": "Good manual review pause point.",
        },
    ]


def csv_text(fieldnames: list[str], rows: list[dict[str, Any]]) -> str:
    handle = io.StringIO()
    writer = csv.DictWriter(handle, fieldnames=fieldnames, extrasaction="ignore")
    writer.writeheader()
    for row in rows:
        writer.writerow(row)
    return handle.getvalue()


def summarize_status(checklist: list[dict[str, Any]]) -> dict[str, int]:
    passed = sum(1 for row in checklist if row["status"] == "passed")
    failed = sum(1 for row in checklist if row["status"] != "passed")
    return {"passed": passed, "failed": failed, "total": len(checklist)}


def render_readout(summary: dict[str, Any]) -> str:
    supported_lines = "\n".join(
        f"- {row['token_position']}: {row['term']} ({row['dwh14a_evidence_strength']})"
        for row in summary["candidate_status_rows"]
        if row["dwh15a_status_group"] == "supported_review_ready"
    )
    deferred_lines = "\n".join(
        f"- {row['token_position']}: {row['term']} ({row['dwh14a_evidence_strength']})"
        for row in summary["candidate_status_rows"]
        if row["dwh15a_status_group"] == "deferred_open"
    )
    checklist_lines = "\n".join(
        "- {checklist_id}: {status}; {inspection_question}".format(**row)
        for row in summary["checklist_rows"]
    )
    next_lines = "\n".join(
        "- {next_step_id}: {next_step_name}".format(**row)
        for row in summary["next_dwh_steps"]
    )
    live_status = "unchanged" if summary["live_db_unchanged"] else "changed"
    workcopy_status = "unchanged" if summary["workcopy_db_unchanged"] else "changed"
    return f"""# QSB-DWH16A DBeaver Candidate Separation Inspection Readout

## 1. Executive summary

Befund: DWH16A inspected the DWH14A/DWH15A supported/open candidate separation in read-only mode.

- Supported/review-ready terms: {summary['supported_count']}
- Deferred/open terms: {summary['deferred_count']}
- Checklist passed: {summary['checklist_summary']['passed']} / {summary['checklist_summary']['total']}
- Checklist failed: {summary['checklist_summary']['failed']}

## 2. Read-only inspection principle

Both DBs were opened read-only. DWH16A created no DB tables/views, ingested no data, and performed no mapping-status update.

## 3. Live/workcopy protection result

- Live DB: `{summary['live_db_path']}`
- Live integrity_check: {summary['live_integrity_check']}
- Live foreign-key violations: {summary['live_foreign_key_violation_count']}
- Live DB checksum/stat status after DWH16A: {live_status}
- Workcopy DB: `{summary['workcopy_db_path']}`
- Workcopy integrity_check: {summary['workcopy_integrity_check']}
- Workcopy foreign-key violations: {summary['workcopy_foreign_key_violation_count']}
- Workcopy DB checksum/stat status after DWH16A: {workcopy_status}

## 4. Supported candidate separation

{supported_lines}

## 5. Deferred/open compound labels

{deferred_lines}

## 6. DBeaver inspection instructions

- Open workcopy DB: `runs/QSB-DB/QSB_DB25_CONSOLIDATED_RESEARCH_SNAPSHOT/qsb_research_dwh_target_workcopy_dwh03.db`
- Inspect `qsb_v_dwh14a_high_priority_decision_status`
- Inspect `qsb_v_dwh14a_supported_candidate_terms`
- Inspect `qsb_v_dwh14a_open_or_conflict_terms`
- Inspect `qsb_v_dwh15a_supported_review_ready_candidates`
- Inspect `qsb_v_dwh15a_skipped_deferred_candidates`
- Inspect `qsb_v_dwh15a_mapping_review_update_dashboard`
- Expected visible pattern: supported/review-ready = GUPPI, Rcvr_800, Rcvr1_2; skipped/deferred = Rcvr_800_GUPPI, Rcvr1_2_GUPPI.
- Do not synchronize or write schema changes from DBeaver back to the DB.

## 7. Pass/fail checklist

{checklist_lines}

## 8. What DWH16_A does not do

DWH16A does not modify the live DB or workcopy DB, does not read raw TIM/PAR files, does not create or alter DB tables/views, does not update mapping statuses, does not create bridge/result tables, does not assign final physical meaning to TIM columns, does not retrieve live sources, does not compute timing/model/statistical quantities, and does not make physical interpretation statements.

## 9. Recommended DWH17 options

{next_lines}

## 10. Claim boundary

{summary['claim_boundary']}
"""


def render_outputs(summary: dict[str, Any]) -> dict[str, str]:
    return {
        READOUT_MD: render_readout(summary),
        SUMMARY_JSON: pretty_json(summary) + "\n",
        STATUS_CSV: csv_text(
            [
                "term",
                "token_position",
                "dwh14a_decision_status",
                "dwh14a_evidence_strength",
                "dwh15a_status_group",
                "dwh15a_action",
                "safe_to_promote",
                "final_semantics_assigned",
                "inspection_status",
                "notes",
            ],
            summary["candidate_status_rows"],
        ),
        CHECKLIST_CSV: csv_text(
            [
                "checklist_id",
                "inspection_question",
                "expected_result",
                "actual_result",
                "status",
                "notes",
            ],
            summary["checklist_rows"],
        ),
        NEXT_STEPS_CSV: csv_text(
            [
                "next_step_id",
                "next_step_name",
                "prerequisite",
                "recommended_action",
                "risk_level",
                "notes",
            ],
            summary["next_dwh_steps"],
        ),
    }


def write_outputs(output_root: Path, output_texts: dict[str, str]) -> None:
    for name in OUTPUT_FILENAMES:
        (output_root / name).write_text(output_texts[name], encoding="utf-8")


def execute(
    live_db: Path,
    workcopy_db: Path,
    output_root: Path,
    overwrite: bool,
) -> dict[str, Any]:
    run_timestamp = utc_now()
    pre = preflight(live_db, workcopy_db, output_root, overwrite)
    inputs = pre["inputs"]
    candidate_status_rows = build_status_rows(inputs)
    checklist_rows = build_checklist(inputs, candidate_status_rows)
    checklist_summary = summarize_status(checklist_rows)
    supported_rows = [
        row for row in candidate_status_rows
        if row["dwh15a_status_group"] == "supported_review_ready"
    ]
    deferred_rows = [
        row for row in candidate_status_rows
        if row["dwh15a_status_group"] == "deferred_open"
    ]

    live_after = db_state(live_db)
    workcopy_after = db_state(workcopy_db)
    summary = {
        "run_timestamp_utc": run_timestamp,
        "script_name": SCRIPT_NAME,
        "operation_mode": "QSB Research DWH visual/manual inspection support, read-only documentation mode",
        "data_substrate_used": str(workcopy_db),
        "live_db_path": str(live_db),
        "workcopy_db_path": str(workcopy_db),
        "live_integrity_check": pre["live_integrity"],
        "live_foreign_key_violation_count": pre["live_fk_count"],
        "workcopy_integrity_check": pre["workcopy_integrity"],
        "workcopy_foreign_key_violation_count": pre["workcopy_fk_count"],
        "live_db_state_before": pre["live_before"],
        "live_db_state_after": live_after,
        "workcopy_db_state_before": pre["workcopy_before"],
        "workcopy_db_state_after": workcopy_after,
        "live_db_unchanged": pre["live_before"] == live_after,
        "workcopy_db_unchanged": pre["workcopy_before"] == workcopy_after,
        "supported_count": len(supported_rows),
        "supported_terms": [row["term"] for row in supported_rows],
        "deferred_count": len(deferred_rows),
        "deferred_terms": [row["term"] for row in deferred_rows],
        "candidate_status_rows": candidate_status_rows,
        "checklist_rows": checklist_rows,
        "checklist_summary": checklist_summary,
        "next_dwh_steps": next_dwh_steps_rows(),
        "claim_boundary": CLAIM_BOUNDARY,
        "output_files": {name: str(output_root / name) for name in OUTPUT_FILENAMES},
    }
    write_outputs(output_root, render_outputs(summary))
    return summary


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="QSB-DWH16A read-only DBeaver inspection package for candidate separation."
    )
    parser.add_argument(
        "--live-db",
        type=Path,
        default=DEFAULT_LIVE_DB,
        help="Path to the live consolidated SQLite DB; opened read-only.",
    )
    parser.add_argument(
        "--workcopy-db",
        type=Path,
        default=DEFAULT_WORKCOPY_DB,
        help="Path to the DWH target workcopy SQLite DB; opened read-only.",
    )
    parser.add_argument(
        "--output-root",
        type=Path,
        default=DEFAULT_OUTPUT_ROOT,
        help="Existing output directory for DWH16A reports.",
    )
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Allow overwriting the five DWH16A output files if they already exist.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        summary = execute(args.live_db, args.workcopy_db, args.output_root, args.overwrite)
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    print(pretty_json(summary))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
