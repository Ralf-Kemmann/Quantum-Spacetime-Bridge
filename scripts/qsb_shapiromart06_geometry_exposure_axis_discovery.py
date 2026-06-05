#!/usr/bin/env python3
"""QSB-SHAPIROMART06: geometry/Shapiro exposure axis discovery.

This script inspects existing workcopy DB objects for fields that might support
a geometry/Shapiro-exposure axis within a fixed receiver/backend context. It is
a discovery step only: it does not read raw TIM/PAR files, compute timing or
model quantities, compare receiver contexts as a geometry test, or assign
physical meaning to unresolved fields.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
import sqlite3
import sys
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


SCRIPT_NAME = "scripts/qsb_shapiromart06_geometry_exposure_axis_discovery.py"
DEFAULT_LIVE_DB = Path(
    "runs/QSB-DB/QSB_DB25_CONSOLIDATED_RESEARCH_SNAPSHOT/"
    "qsb_research_consolidated_snapshot.db"
)
DEFAULT_WORKCOPY_DB = Path(
    "runs/QSB-DB/QSB_DB25_CONSOLIDATED_RESEARCH_SNAPSHOT/"
    "qsb_research_dwh_target_workcopy_dwh03.db"
)
DEFAULT_OUTPUT_ROOT = Path(
    "runs/QSB-SHAPIROMART/SHAPIROMART06_GEOMETRY_EXPOSURE_AXIS_DISCOVERY"
)

READOUT_MD = "shapiromart06_readout.md"
SUMMARY_JSON = "shapiromart06_summary.json"
CANDIDATES_CSV = "shapiromart06_geometry_axis_candidates.csv"
READINESS_CSV = "shapiromart06_fixed_context_readiness.csv"
GAPS_CSV = "shapiromart06_geometry_axis_gaps.csv"
NEXT_STEP_CSV = "shapiromart06_next_step.csv"

OUTPUT_FILENAMES = [
    READOUT_MD,
    SUMMARY_JSON,
    CANDIDATES_CSV,
    READINESS_CSV,
    GAPS_CSV,
    NEXT_STEP_CSV,
]

TARGET_TABLES = [
    "mart_shapiro_geometry_axis_candidate",
    "mart_shapiro_fixed_context_exposure_readiness",
    "mart_shapiro_geometry_axis_gap",
    "shapiromart06_run_log",
]

TARGET_VIEWS = [
    "qsb_v_shapiromart06_geometry_axis_candidates",
    "qsb_v_shapiromart06_fixed_context_readiness",
    "qsb_v_shapiromart06_geometry_axis_gaps",
    "qsb_v_shapiromart06_dashboard",
]

REQUIRED_OBJECTS = [
    ("mart_shapiro_structural_fingerprint", "table"),
    ("mart_shapiro_observation_context", "table"),
    ("core_observation", "table"),
    ("core_observation_record_link", "table"),
    ("raw_record", "table"),
    ("raw_field_value", "table"),
    ("dim_time_context", "table"),
    ("dim_processing_context", "table"),
    ("db21_par_tim_field_inventory", "table"),
    ("db21_par_tim_joinability", "table"),
    ("db21_par_tim_source_inventory", "table"),
    ("db20_rawdata_record", "table"),
    ("db20_rawdata_field_value", "table"),
    ("map_token_dictionary", "table"),
    ("map_assertion_evidence", "table"),
    ("qsb_v_shapiromart04_complete_fingerprints", "view"),
    ("qsb_v_shapiromart05_dashboard", "view"),
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
}

EXPECTED_CONTEXT_COUNTS = {
    "Rcvr_800": 2916,
    "Rcvr1_2": 4503,
}
EXPECTED_TOTAL_COMPLETE = 7419
SUPPORTED_BACKEND = "GUPPI"
EXPECTED_SCIENCE_OBJECT = "J0740+6620"
NEXT_STEP = (
    "Resolve one DB-backed timestamp/phase candidate against documented "
    "PAR/TIM semantics and define a fixed receiver/backend exposure grouping "
    "without computing physical exposure values."
)

CANDIDATE_CLASSES = {
    "direct_geometry_exposure_candidate",
    "indirect_time_phase_candidate",
    "ephemeris_parameter_candidate",
    "observation_link_candidate",
    "insufficient_or_unresolved",
    "unusable_for_exposure_axis",
}

CLAIM_BOUNDARY = (
    "SHAPIROMART06 discovers candidate axis inputs only. It does not compute "
    "Shapiro delay, TOAs, timing residuals, orbital models, physical exposure "
    "values, p-values, or confidence intervals, and it does not claim geometry "
    "influence or Shapiro confirmation."
)

DIRECT_GEOMETRY_PAR_NAMES = {
    "LAMBDA",
    "BETA",
    "RAJ",
    "DECJ",
    "ELONG",
    "ELAT",
}
EPHEMERIS_PAR_NAMES = {
    "A1",
    "BINARY",
    "EPS1",
    "EPS2",
    "M2",
    "OM",
    "PB",
    "PBDOT",
    "PEPOCH",
    "PLANET_SHAPIRO",
    "POSEPOCH",
    "SINI",
    "T0",
    "TASC",
    "TZRMJD",
}
TIME_SERIES_PAR_PREFIXES = ("DMXEP_",)
FREQUENCY_SERIES_PAR_PREFIXES = ("DMXF1_", "DMXF2_")
GEOMETRY_KEYWORD_RE = re.compile(
    r"(lambda|beta|raj|decj|elong|elat|sky|coord|geometry)", re.I
)
TIME_PHASE_KEYWORD_RE = re.compile(
    r"(mjd|epoch|time|phase|tasc|tzrmjd|pepoch|posepoch|dmxep)", re.I
)
EPHEMERIS_KEYWORD_RE = re.compile(
    r"(a1|pb|binary|eps1|eps2|m2|sini|om|t0|planet_shapiro|shapiro)", re.I
)


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


def fail(message: str) -> None:
    raise RuntimeError(message)


def stable_digest(rows: list[dict[str, Any]]) -> str:
    payload = json.dumps(rows, sort_keys=True, ensure_ascii=True)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


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
            "SHAPIROMART06 output files already exist. Use --overwrite to replace: "
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
    target_state: list[dict[str, Any]] = []
    existing_objects: list[str] = []
    for table in TARGET_TABLES:
        if object_exists(con, table, "table"):
            count = table_count(con, table)
            target_state.append({"name": table, "type": "table", "row_count": count})
            existing_objects.append(f"table:{table}")
        else:
            target_state.append({"name": table, "type": "table", "row_count": None})
    for view in TARGET_VIEWS:
        if object_exists(con, view, "view"):
            target_state.append({"name": view, "type": "view", "row_count": None})
            existing_objects.append(f"view:{view}")
        else:
            target_state.append({"name": view, "type": "view", "row_count": None})
    if existing_objects and not allow_existing:
        fail(
            "SHAPIROMART06 target objects already exist. Use --allow-existing "
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


def load_complete_fingerprint_counts(con: sqlite3.Connection) -> dict[str, Any]:
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
        if str(row["backend_context"]) != SUPPORTED_BACKEND:
            fail(f"Unexpected backend_context: {row['backend_context']}")
        if str(row["science_object_id"]) != EXPECTED_SCIENCE_OBJECT:
            fail(f"Unexpected science_object_id: {row['science_object_id']}")
    return {"rows": rows, "context_counts": context_counts}


def linked_fingerprint_count_for_token(con: sqlite3.Connection, field_name: str) -> int:
    row = con.execute(
        """
        SELECT COUNT(DISTINCT sf.raw_record_id) AS n
        FROM mart_shapiro_structural_fingerprint AS sf
        JOIN raw_field_value AS fv
          ON fv.raw_record_id = sf.raw_record_id
        WHERE sf.complete_fingerprint = 1
          AND fv.field_name = ?
        """,
        (field_name,),
    ).fetchone()
    return int(row["n"])


def split_possible_by_receiver(con: sqlite3.Connection, field_name: str) -> bool:
    rows = fetch_dicts(
        con,
        """
        SELECT sf.receiver_context, COUNT(DISTINCT fv.raw_value) AS distinct_n
        FROM mart_shapiro_structural_fingerprint AS sf
        JOIN raw_field_value AS fv
          ON fv.raw_record_id = sf.raw_record_id
        WHERE sf.complete_fingerprint = 1
          AND fv.field_name = ?
        GROUP BY sf.receiver_context
        """,
        (field_name,),
    )
    by_receiver = {str(row["receiver_context"]): int(row["distinct_n"]) for row in rows}
    return all(by_receiver.get(receiver, 0) >= 2 for receiver in EXPECTED_CONTEXT_COUNTS)


def add_candidate(
    rows: list[dict[str, Any]],
    *,
    source_table: str,
    source_field_or_token: str,
    candidate_class: str,
    populated_row_count: int | None,
    distinct_value_count: int | None,
    linked_fingerprint_count: int | None,
    fixed_receiver_context_possible: int,
    proposed_use: str,
    semantic_status: str,
    usable_now: int,
    limitation: str,
    created_at: str,
    notes: str,
) -> None:
    if candidate_class not in CANDIDATE_CLASSES:
        fail(f"Unexpected candidate class: {candidate_class}")
    rows.append(
        {
            "geometry_axis_candidate_id": f"SHAPIROMART06_CAND_{len(rows) + 1:03d}",
            "source_table": source_table,
            "source_field_or_token": source_field_or_token,
            "candidate_class": candidate_class,
            "populated_row_count": populated_row_count,
            "distinct_value_count": distinct_value_count,
            "linked_fingerprint_count": linked_fingerprint_count,
            "fixed_receiver_context_possible": fixed_receiver_context_possible,
            "proposed_use": proposed_use,
            "semantic_status": semantic_status,
            "usable_now": usable_now,
            "limitation": limitation,
            "created_at_utc": created_at,
            "notes": notes,
        }
    )


def inspect_observation_link_candidates(
    con: sqlite3.Connection,
    candidate_rows: list[dict[str, Any]],
    created_at: str,
) -> None:
    complete_count = EXPECTED_TOTAL_COMPLETE
    for source_table, source_field, proposed_use, limitation in [
        (
            "core_observation_record_link",
            "raw_record_id",
            "Link complete fingerprints to DB raw records inside each fixed receiver/backend context.",
            "Record linkage supports traceability but is not an exposure variable.",
        ),
        (
            "core_observation_record_link",
            "observation_id",
            "Link complete fingerprints to the single observation context.",
            "Only one observation_id is present; it cannot split exposure groups.",
        ),
        (
            "raw_record",
            "record_index",
            "Structural ordering candidate for within-context partitioning.",
            "Record order is not a documented timestamp or geometry-exposure variable.",
        ),
        (
            "mart_shapiro_observation_context",
            "time_context_id",
            "Trace supported contexts to the time-context dimension.",
            "The linked time context is an unresolved placeholder.",
        ),
        (
            "dim_time_context",
            "mjd_start/mjd_end/ephemeris_context/barycentric_context",
            "Potential observation-level time and ephemeris metadata.",
            "The current row is placeholder-like and has null time/ephemeris fields.",
        ),
    ]:
        if source_table == "raw_record":
            row = con.execute(
                """
                SELECT COUNT(*) AS populated, COUNT(DISTINCT r.record_index) AS distinct_n
                FROM mart_shapiro_structural_fingerprint AS sf
                JOIN raw_record AS r
                  ON r.raw_record_id = sf.raw_record_id
                WHERE sf.complete_fingerprint = 1
                """
            ).fetchone()
            populated = int(row["populated"])
            distinct_n = int(row["distinct_n"])
            fixed_possible = 1 if distinct_n >= 2 else 0
        elif source_table == "core_observation_record_link" and source_field == "raw_record_id":
            populated = complete_count
            distinct_n = complete_count
            fixed_possible = 1
        elif source_table == "core_observation_record_link":
            row = con.execute(
                """
                SELECT COUNT(DISTINCT link.observation_id) AS distinct_n
                FROM mart_shapiro_structural_fingerprint AS sf
                JOIN core_observation_record_link AS link
                  ON link.raw_record_id = sf.raw_record_id
                WHERE sf.complete_fingerprint = 1
                """
            ).fetchone()
            populated = complete_count
            distinct_n = int(row["distinct_n"])
            fixed_possible = 1 if distinct_n >= 2 else 0
        elif source_table == "mart_shapiro_observation_context":
            rows = fetch_dicts(
                con,
                """
                SELECT receiver_term, time_context_id
                FROM mart_shapiro_observation_context
                ORDER BY receiver_term
                """,
            )
            populated = sum(1 for row in rows if row["time_context_id"])
            distinct_n = len({row["time_context_id"] for row in rows if row["time_context_id"]})
            fixed_possible = 0
        else:
            row = con.execute(
                """
                SELECT
                    SUM(CASE WHEN mjd_start IS NOT NULL THEN 1 ELSE 0 END) +
                    SUM(CASE WHEN mjd_end IS NOT NULL THEN 1 ELSE 0 END) +
                    SUM(CASE WHEN ephemeris_context IS NOT NULL THEN 1 ELSE 0 END) +
                    SUM(CASE WHEN barycentric_context IS NOT NULL THEN 1 ELSE 0 END) AS populated,
                    COUNT(*) AS rows_n
                FROM dim_time_context
                """
            ).fetchone()
            populated = int(row["populated"] or 0)
            distinct_n = int(row["rows_n"])
            fixed_possible = 0
        add_candidate(
            candidate_rows,
            source_table=source_table,
            source_field_or_token=source_field,
            candidate_class="observation_link_candidate",
            populated_row_count=populated,
            distinct_value_count=distinct_n,
            linked_fingerprint_count=complete_count,
            fixed_receiver_context_possible=fixed_possible,
            proposed_use=proposed_use,
            semantic_status="traceability_only_not_exposure_semantics",
            usable_now=0,
            limitation=limitation,
            created_at=created_at,
            notes="Discovered from DB schema and complete fingerprint linkage; no physical quantity computed.",
        )


def inspect_tim_token_candidates(
    con: sqlite3.Connection,
    candidate_rows: list[dict[str, Any]],
    created_at: str,
) -> None:
    token_rows = fetch_dicts(
        con,
        """
        SELECT
            fv.field_name,
            COUNT(*) AS populated,
            COUNT(DISTINCT fv.raw_value) AS distinct_n
        FROM raw_field_value AS fv
        JOIN mart_shapiro_structural_fingerprint AS sf
          ON sf.raw_record_id = fv.raw_record_id
        WHERE sf.complete_fingerprint = 1
          AND fv.field_name LIKE 'tim_token_%'
        GROUP BY fv.field_name
        ORDER BY fv.field_name
        """,
    )
    role_rows = {
        str(row["token_position"]): row
        for row in fetch_dicts(
            con,
            """
            SELECT token_position, proposed_structural_name, structural_role,
                   mapping_status, review_status, notes
            FROM map_token_dictionary
            WHERE line_family = 'data_line'
            ORDER BY token_position
            """,
        )
    }
    for row in token_rows:
        field_name = str(row["field_name"])
        distinct_n = int(row["distinct_n"])
        populated = int(row["populated"])
        if field_name not in {"tim_token_001", "tim_token_003", "tim_token_007"}:
            continue
        role = role_rows.get(field_name, {})
        role_text = " ".join(
            str(role.get(key) or "")
            for key in [
                "proposed_structural_name",
                "structural_role",
                "mapping_status",
                "review_status",
                "notes",
            ]
        )
        fixed_possible = 1 if distinct_n >= 2 and split_possible_by_receiver(con, field_name) else 0
        if field_name == "tim_token_003":
            candidate_class = "indirect_time_phase_candidate"
            proposed_use = (
                "Candidate timestamp/epoch-like ordering axis for fixed-context grouping, "
                "pending semantic support."
            )
            semantic_status = "numeric_coordinate_candidate_semantics_unresolved"
            limitation = (
                "Values are complete and highly variable, but the DB mapping does not "
                "certify timestamp, orbital phase, or Shapiro-exposure meaning."
            )
        elif field_name == "tim_token_001":
            candidate_class = "observation_link_candidate"
            proposed_use = "Candidate source/file-block grouping token within fixed contexts."
            semantic_status = "grouping_token_semantics_unresolved"
            limitation = (
                "Text grouping token can split records but is not geometry or phase."
            )
        else:
            candidate_class = "observation_link_candidate"
            proposed_use = "Candidate block-switch token for structural partition checks."
            semantic_status = "block_switch_semantics_unresolved"
            limitation = (
                "Existing mapping marks a block-switch/grouping role, not exposure semantics."
            )
        add_candidate(
            candidate_rows,
            source_table="raw_field_value",
            source_field_or_token=field_name,
            candidate_class=candidate_class,
            populated_row_count=populated,
            distinct_value_count=distinct_n,
            linked_fingerprint_count=linked_fingerprint_count_for_token(con, field_name),
            fixed_receiver_context_possible=fixed_possible,
            proposed_use=proposed_use,
            semantic_status=semantic_status,
            usable_now=0,
            limitation=limitation,
            created_at=created_at,
            notes=(
                "Role evidence from map_token_dictionary: "
                + (role_text[:600] if role_text else "no reviewed role row found")
            ),
        )


def par_source_family_linked_count(con: sqlite3.Connection) -> int:
    row = con.execute(
        """
        SELECT direct_record_level_join_available
        FROM db21_par_tim_joinability
        LIMIT 1
        """
    ).fetchone()
    if row is None:
        return 0
    return EXPECTED_TOTAL_COMPLETE


def inspect_par_candidates(
    con: sqlite3.Connection,
    candidate_rows: list[dict[str, Any]],
    created_at: str,
) -> None:
    linked_count = par_source_family_linked_count(con)
    par_rows = fetch_dicts(
        con,
        """
        SELECT source_type, field_name, occurrence_count, sample_raw_value_text
        FROM db21_par_tim_field_inventory
        WHERE source_type = 'PAR'
        ORDER BY field_name
        """,
    )
    selected: list[dict[str, Any]] = []
    for row in par_rows:
        field_name = str(row["field_name"])
        if (
            field_name in DIRECT_GEOMETRY_PAR_NAMES
            or field_name in EPHEMERIS_PAR_NAMES
            or field_name.startswith(TIME_SERIES_PAR_PREFIXES)
            or GEOMETRY_KEYWORD_RE.search(field_name)
            or TIME_PHASE_KEYWORD_RE.search(field_name)
            or EPHEMERIS_KEYWORD_RE.search(field_name)
        ):
            selected.append(row)
    # Keep repeated DMX epoch families compact but visible as a family candidate.
    dmx_rows = [row for row in selected if str(row["field_name"]).startswith(TIME_SERIES_PAR_PREFIXES)]
    non_dmx_rows = [row for row in selected if row not in dmx_rows]
    for row in non_dmx_rows:
        field_name = str(row["field_name"])
        if field_name in DIRECT_GEOMETRY_PAR_NAMES or GEOMETRY_KEYWORD_RE.search(field_name):
            candidate_class = "direct_geometry_exposure_candidate"
            proposed_use = "Source-level sky/source geometry context candidate."
            semantic_status = "par_parameter_name_present_semantics_need_review"
            limitation = (
                "PAR parameter is source-level/static here and is not a record-level "
                "within-context exposure grouping axis."
            )
        elif field_name in EPHEMERIS_PAR_NAMES or EPHEMERIS_KEYWORD_RE.search(field_name):
            candidate_class = "ephemeris_parameter_candidate"
            proposed_use = "Source-level binary/ephemeris context candidate."
            semantic_status = "par_parameter_name_present_semantics_need_review"
            limitation = (
                "No orbital or Shapiro exposure values are computed; PAR/TIM join is "
                "source-family-level only."
            )
        else:
            candidate_class = "indirect_time_phase_candidate"
            proposed_use = "Source-level epoch/time metadata candidate."
            semantic_status = "par_parameter_name_present_semantics_need_review"
            limitation = (
                "Source-level value lacks record-level exposure grouping semantics."
            )
        add_candidate(
            candidate_rows,
            source_table="db21_par_tim_field_inventory",
            source_field_or_token=field_name,
            candidate_class=candidate_class,
            populated_row_count=int(row["occurrence_count"]),
            distinct_value_count=1,
            linked_fingerprint_count=linked_count,
            fixed_receiver_context_possible=0,
            proposed_use=proposed_use,
            semantic_status=semantic_status,
            usable_now=0,
            limitation=limitation,
            created_at=created_at,
            notes=(
                f"sample_raw_value_text={row['sample_raw_value_text']}; "
                "db21_par_tim_joinability is source-family/file-context level."
            ),
        )
    if dmx_rows:
        distinct_n = len({str(row["sample_raw_value_text"]) for row in dmx_rows})
        add_candidate(
            candidate_rows,
            source_table="db21_par_tim_field_inventory",
            source_field_or_token="DMXEP_*",
            candidate_class="indirect_time_phase_candidate",
            populated_row_count=len(dmx_rows),
            distinct_value_count=distinct_n,
            linked_fingerprint_count=linked_count,
            fixed_receiver_context_possible=0,
            proposed_use="PAR-derived epoch-family inventory candidate.",
            semantic_status="epoch_family_present_but_record_mapping_unresolved",
            usable_now=0,
            limitation=(
                "DMXEP family is present but not mapped to individual complete "
                "fingerprint records as an exposure grouping axis."
            ),
            created_at=created_at,
            notes=(
                f"DMXEP field count={len(dmx_rows)}; source-family linkage only; "
                "no interpolation or exposure value computed."
            ),
        )


def inspect_unusable_context_candidates(
    candidate_rows: list[dict[str, Any]],
    created_at: str,
) -> None:
    for field_name in ["receiver_context", "backend_context", "raw_context_label"]:
        add_candidate(
            candidate_rows,
            source_table="mart_shapiro_structural_fingerprint",
            source_field_or_token=field_name,
            candidate_class="unusable_for_exposure_axis",
            populated_row_count=EXPECTED_TOTAL_COMPLETE,
            distinct_value_count=2 if field_name != "backend_context" else 1,
            linked_fingerprint_count=EXPECTED_TOTAL_COMPLETE,
            fixed_receiver_context_possible=0,
            proposed_use="Do not use as a geometry/Shapiro exposure grouping axis.",
            semantic_status="forbidden_receiver_backend_or_compound_context_axis",
            usable_now=0,
            limitation=(
                "Receiver/backend or unresolved compound-label separation must not be "
                "reused as the geometry test."
            ),
            created_at=created_at,
            notes="Included to make the claim boundary explicit.",
        )


def build_candidate_rows(con: sqlite3.Connection, created_at: str) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    inspect_observation_link_candidates(con, rows, created_at)
    inspect_tim_token_candidates(con, rows, created_at)
    inspect_par_candidates(con, rows, created_at)
    inspect_unusable_context_candidates(rows, created_at)
    return rows


def build_readiness_rows(
    con: sqlite3.Connection,
    candidate_rows: list[dict[str, Any]],
    created_at: str,
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    linkable_candidates = [
        row
        for row in candidate_rows
        if int(row["linked_fingerprint_count"] or 0) > 0
        and row["candidate_class"] != "unusable_for_exposure_axis"
    ]
    direct_count = sum(
        1
        for row in linkable_candidates
        if row["candidate_class"] == "direct_geometry_exposure_candidate"
        and int(row["usable_now"]) == 1
    )
    indirect_count = sum(
        1
        for row in linkable_candidates
        if row["candidate_class"] in {"indirect_time_phase_candidate", "observation_link_candidate"}
        and int(row["fixed_receiver_context_possible"]) == 1
    )
    for index, receiver in enumerate(["Rcvr_800", "Rcvr1_2"], start=1):
        count = EXPECTED_CONTEXT_COUNTS[receiver]
        split_candidates = []
        for row in linkable_candidates:
            if int(row["fixed_receiver_context_possible"]) != 1:
                continue
            if row["source_table"] == "raw_field_value":
                field_name = str(row["source_field_or_token"])
                distinct_row = con.execute(
                    """
                    SELECT COUNT(DISTINCT fv.raw_value) AS n
                    FROM mart_shapiro_structural_fingerprint AS sf
                    JOIN raw_field_value AS fv
                      ON fv.raw_record_id = sf.raw_record_id
                    WHERE sf.complete_fingerprint = 1
                      AND sf.receiver_context = ?
                      AND sf.backend_context = ?
                      AND fv.field_name = ?
                    """,
                    (receiver, SUPPORTED_BACKEND, field_name),
                ).fetchone()
                if int(distinct_row["n"]) >= 2:
                    split_candidates.append(row)
            elif row["source_table"] in {"raw_record", "core_observation_record_link"}:
                split_candidates.append(row)
        if direct_count > 0:
            status = "ready_for_exposure_definition"
            blocking_reason = None
        elif split_candidates:
            status = "partial_axis_available"
            blocking_reason = (
                "At least one linkable fixed-context split candidate exists, but "
                "geometry/Shapiro-exposure semantics remain unresolved."
            )
        elif linkable_candidates:
            status = "blocked_unresolved_semantics"
            blocking_reason = "Candidates are linkable only at context/source level or lack semantics."
        else:
            status = "blocked_missing_geometry_axis"
            blocking_reason = "No linkable candidate axis was found."
        rows.append(
            {
                "exposure_readiness_id": f"SHAPIROMART06_READY_{index:03d}",
                "receiver_context": receiver,
                "backend_context": SUPPORTED_BACKEND,
                "complete_fingerprint_count": count,
                "candidate_axis_count": len(linkable_candidates),
                "directly_usable_axis_count": direct_count,
                "indirectly_usable_axis_count": indirect_count,
                "exposure_grouping_status": status,
                "blocking_reason": blocking_reason,
                "created_at_utc": created_at,
                "notes": (
                    "Readiness holds receiver/backend fixed. Receiver-context "
                    "comparison is not reused as a geometry test."
                ),
            }
        )
    return rows


def build_gap_rows(
    candidate_rows: list[dict[str, Any]],
    readiness_rows: list[dict[str, Any]],
    created_at: str,
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    direct_usable = sum(
        1
        for row in candidate_rows
        if row["candidate_class"] == "direct_geometry_exposure_candidate"
        and int(row["usable_now"]) == 1
    )
    source_family_par = [
        row
        for row in candidate_rows
        if row["candidate_class"] in {
            "direct_geometry_exposure_candidate",
            "ephemeris_parameter_candidate",
            "indirect_time_phase_candidate",
        }
        and row["source_table"] == "db21_par_tim_field_inventory"
    ]
    base_gaps = [
        {
            "receiver_context": None,
            "gap_type": "unresolved_geometry_exposure_semantics",
            "missing_field_or_relation": "supported_geometry_or_shapiro_exposure_axis",
            "current_state": (
                "Candidate TIM tokens and PAR parameters exist, but no DB row "
                "certifies a geometry/Shapiro-exposure grouping variable."
            ),
            "recommended_next_action": (
                "Review DB-backed dictionary/evidence for one timestamp/phase "
                "candidate and define its allowed grouping semantics."
            ),
            "notes": "Main blocking gap for moving from discovery to exposure grouping.",
        },
        {
            "receiver_context": None,
            "gap_type": "missing_record_level_par_tim_join",
            "missing_field_or_relation": "PAR/TIM parameter-to-fingerprint-record relation",
            "current_state": (
                f"{len(source_family_par)} PAR-derived candidates are source-family "
                "linked only; db21_par_tim_joinability has no direct record-level key."
            ),
            "recommended_next_action": (
                "Create or review a DB-backed relation that maps any chosen "
                "PAR-derived axis to complete fingerprint records without reading raw files."
            ),
            "notes": "No physical exposure value should be computed at this step.",
        },
    ]
    if direct_usable == 0:
        base_gaps.append(
            {
                "receiver_context": None,
                "gap_type": "no_directly_usable_axis",
                "missing_field_or_relation": "direct_geometry_exposure_candidate.usable_now",
                "current_state": "No discovered direct geometry candidate is usable now.",
                "recommended_next_action": (
                    "Keep candidates provisional until semantics and record linkage are supported."
                ),
                "notes": "Directly usable means both semantic support and fixed-context grouping support.",
            }
        )
    for readiness in readiness_rows:
        if readiness["exposure_grouping_status"] != "ready_for_exposure_definition":
            base_gaps.append(
                {
                    "receiver_context": readiness["receiver_context"],
                    "gap_type": "fixed_context_axis_not_ready",
                    "missing_field_or_relation": "fixed_receiver_backend_exposure_grouping",
                    "current_state": readiness["blocking_reason"],
                    "recommended_next_action": NEXT_STEP,
                    "notes": (
                        f"complete_fingerprint_count={readiness['complete_fingerprint_count']}; "
                        f"indirectly_usable_axis_count={readiness['indirectly_usable_axis_count']}"
                    ),
                }
            )
    for index, gap in enumerate(base_gaps, start=1):
        rows.append(
            {
                "geometry_axis_gap_id": f"SHAPIROMART06_GAP_{index:03d}",
                "receiver_context": gap["receiver_context"],
                "gap_type": gap["gap_type"],
                "missing_field_or_relation": gap["missing_field_or_relation"],
                "current_state": gap["current_state"],
                "recommended_next_action": gap["recommended_next_action"],
                "created_at_utc": created_at,
                "notes": gap["notes"],
            }
        )
    return rows


def create_tables(con: sqlite3.Connection) -> None:
    con.executescript(
        """
        CREATE TABLE IF NOT EXISTS mart_shapiro_geometry_axis_candidate (
            geometry_axis_candidate_id TEXT PRIMARY KEY,
            source_table TEXT NOT NULL,
            source_field_or_token TEXT NOT NULL,
            candidate_class TEXT NOT NULL,
            populated_row_count INTEGER,
            distinct_value_count INTEGER,
            linked_fingerprint_count INTEGER,
            fixed_receiver_context_possible INTEGER NOT NULL CHECK (fixed_receiver_context_possible IN (0, 1)),
            proposed_use TEXT,
            semantic_status TEXT NOT NULL,
            usable_now INTEGER NOT NULL CHECK (usable_now IN (0, 1)),
            limitation TEXT,
            created_at_utc TEXT NOT NULL,
            notes TEXT
        );

        CREATE TABLE IF NOT EXISTS mart_shapiro_fixed_context_exposure_readiness (
            exposure_readiness_id TEXT PRIMARY KEY,
            receiver_context TEXT NOT NULL,
            backend_context TEXT NOT NULL,
            complete_fingerprint_count INTEGER NOT NULL,
            candidate_axis_count INTEGER NOT NULL,
            directly_usable_axis_count INTEGER NOT NULL,
            indirectly_usable_axis_count INTEGER NOT NULL,
            exposure_grouping_status TEXT NOT NULL CHECK (
                exposure_grouping_status IN (
                    'ready_for_exposure_definition',
                    'partial_axis_available',
                    'blocked_missing_geometry_axis',
                    'blocked_missing_record_link',
                    'blocked_unresolved_semantics'
                )
            ),
            blocking_reason TEXT,
            created_at_utc TEXT NOT NULL,
            notes TEXT
        );

        CREATE TABLE IF NOT EXISTS mart_shapiro_geometry_axis_gap (
            geometry_axis_gap_id TEXT PRIMARY KEY,
            receiver_context TEXT,
            gap_type TEXT NOT NULL,
            missing_field_or_relation TEXT NOT NULL,
            current_state TEXT NOT NULL,
            recommended_next_action TEXT NOT NULL,
            created_at_utc TEXT NOT NULL,
            notes TEXT
        );

        CREATE TABLE IF NOT EXISTS shapiromart06_run_log (
            run_id TEXT PRIMARY KEY,
            run_timestamp_utc TEXT,
            geometry_axis_candidate_count INTEGER,
            linkable_candidate_count INTEGER,
            readiness_row_count INTEGER,
            gap_row_count INTEGER,
            context_a_status TEXT,
            context_b_status TEXT,
            live_db_modified INTEGER,
            workcopy_db_modified INTEGER,
            integrity_check_result TEXT,
            foreign_key_violation_count INTEGER,
            notes TEXT
        );
        """
    )


def clear_target_tables(con: sqlite3.Connection) -> None:
    for table in reversed(TARGET_TABLES):
        if object_exists(con, table, "table"):
            con.execute(f"DELETE FROM {quote_identifier(table)}")


def insert_rows(con: sqlite3.Connection, table: str, rows: list[dict[str, Any]]) -> None:
    if not rows:
        return
    fieldnames = list(rows[0].keys())
    columns = ", ".join(quote_identifier(field) for field in fieldnames)
    placeholders = ", ".join("?" for _ in fieldnames)
    con.executemany(
        f"INSERT INTO {quote_identifier(table)} ({columns}) VALUES ({placeholders})",
        [tuple(row[field] for field in fieldnames) for row in rows],
    )


def create_views(con: sqlite3.Connection) -> None:
    for view in TARGET_VIEWS:
        con.execute(f"DROP VIEW IF EXISTS {quote_identifier(view)}")
    con.executescript(
        """
        CREATE VIEW qsb_v_shapiromart06_geometry_axis_candidates AS
        SELECT *
        FROM mart_shapiro_geometry_axis_candidate
        ORDER BY usable_now DESC,
                 fixed_receiver_context_possible DESC,
                 candidate_class,
                 source_table,
                 source_field_or_token;

        CREATE VIEW qsb_v_shapiromart06_fixed_context_readiness AS
        SELECT *
        FROM mart_shapiro_fixed_context_exposure_readiness
        ORDER BY
            CASE receiver_context
              WHEN 'Rcvr_800' THEN 1
              WHEN 'Rcvr1_2' THEN 2
              ELSE 99
            END,
            receiver_context;

        CREATE VIEW qsb_v_shapiromart06_geometry_axis_gaps AS
        SELECT *
        FROM mart_shapiro_geometry_axis_gap
        ORDER BY
            CASE WHEN receiver_context IS NULL THEN 0 ELSE 1 END,
            receiver_context,
            geometry_axis_gap_id;

        CREATE VIEW qsb_v_shapiromart06_dashboard AS
        SELECT
            (SELECT COUNT(*) FROM mart_shapiro_geometry_axis_candidate)
                AS geometry_axis_candidate_count,
            (SELECT COUNT(*) FROM mart_shapiro_geometry_axis_candidate
             WHERE COALESCE(linked_fingerprint_count, 0) > 0
               AND candidate_class <> 'unusable_for_exposure_axis')
                AS linkable_candidate_count,
            (SELECT COUNT(*) FROM mart_shapiro_geometry_axis_candidate
             WHERE usable_now = 1)
                AS directly_usable_now_count,
            (SELECT COUNT(*) FROM mart_shapiro_geometry_axis_candidate
             WHERE fixed_receiver_context_possible = 1
               AND candidate_class <> 'unusable_for_exposure_axis')
                AS fixed_context_split_candidate_count,
            (SELECT exposure_grouping_status
             FROM mart_shapiro_fixed_context_exposure_readiness
             WHERE receiver_context = 'Rcvr_800')
                AS rcvr_800_status,
            (SELECT exposure_grouping_status
             FROM mart_shapiro_fixed_context_exposure_readiness
             WHERE receiver_context = 'Rcvr1_2')
                AS rcvr1_2_status,
            (SELECT COUNT(*) FROM mart_shapiro_geometry_axis_gap)
                AS gap_count,
            'descriptive_discovery_only_no_physical_interpretation'
                AS interpretation_status;
        """
    )


def queryable_counts(con: sqlite3.Connection) -> dict[str, int | str]:
    counts: dict[str, int | str] = {}
    for name in TARGET_TABLES + TARGET_VIEWS:
        try:
            counts[name] = table_count(con, name)
        except sqlite3.Error as exc:
            counts[name] = f"ERROR: {exc}"
    return counts


def write_csv(path: Path, rows: list[dict[str, Any]], fieldnames: list[str]) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def fmt(value: Any) -> str:
    if value is None:
        return "n/a"
    return str(value)


def markdown_table(rows: list[dict[str, Any]], fieldnames: list[str]) -> list[str]:
    if not rows:
        return ["No rows."]
    lines = [
        "| " + " | ".join(fieldnames) + " |",
        "| " + " | ".join("---" for _ in fieldnames) + " |",
    ]
    for row in rows:
        lines.append("| " + " | ".join(fmt(row.get(field)) for field in fieldnames) + " |")
    return lines


def class_counts(candidate_rows: list[dict[str, Any]]) -> dict[str, int]:
    counts: dict[str, int] = defaultdict(int)
    for row in candidate_rows:
        counts[str(row["candidate_class"])] += 1
    return dict(sorted(counts.items()))


def write_readout(
    path: Path,
    run_id: str,
    created_at: str,
    candidate_rows: list[dict[str, Any]],
    readiness_rows: list[dict[str, Any]],
    gap_rows: list[dict[str, Any]],
    validation: dict[str, Any],
) -> None:
    linkable_rows = [
        row
        for row in candidate_rows
        if int(row["linked_fingerprint_count"] or 0) > 0
        and row["candidate_class"] != "unusable_for_exposure_axis"
    ]
    directly_usable = [row for row in candidate_rows if int(row["usable_now"]) == 1]
    top_candidates = sorted(
        candidate_rows,
        key=lambda row: (
            -int(row["fixed_receiver_context_possible"]),
            0 if row["candidate_class"] != "unusable_for_exposure_axis" else 1,
            row["source_table"],
            row["source_field_or_token"],
        ),
    )[:24]
    lines: list[str] = [
        "# QSB-SHAPIROMART06 - Geometry / Shapiro Exposure Axis Discovery",
        "",
        f"Run ID: {run_id}",
        f"Run timestamp UTC: {created_at}",
        "",
        "## Scope",
        "",
        CLAIM_BOUNDARY,
        "",
        "This run uses existing workcopy DB tables/views only. It does not read "
        "raw TIM/PAR files directly and does not reuse receiver-context "
        "separation as a geometry test.",
        "",
        "## 1. Existing possible geometry/time/phase/ephemeris fields",
        "",
        "Candidate class counts:",
        "",
        "```json",
        json.dumps(class_counts(candidate_rows), indent=2, sort_keys=True),
        "```",
        "",
    ]
    lines.extend(
        markdown_table(
            top_candidates,
            [
                "source_table",
                "source_field_or_token",
                "candidate_class",
                "linked_fingerprint_count",
                "fixed_receiver_context_possible",
                "semantic_status",
                "usable_now",
            ],
        )
    )
    lines.extend(
        [
            "",
            "## 2. Linkage to complete fingerprints",
            "",
            f"Linkable non-forbidden candidates: {len(linkable_rows)}.",
            "",
        ]
    )
    lines.extend(
        markdown_table(
            linkable_rows[:24],
            [
                "source_table",
                "source_field_or_token",
                "candidate_class",
                "linked_fingerprint_count",
                "fixed_receiver_context_possible",
                "limitation",
            ],
        )
    )
    lines.extend(
        [
            "",
            "## 3. Rcvr_800 fixed-context split readiness",
            "",
        ]
    )
    lines.extend(
        markdown_table(
            [row for row in readiness_rows if row["receiver_context"] == "Rcvr_800"],
            [
                "receiver_context",
                "backend_context",
                "complete_fingerprint_count",
                "candidate_axis_count",
                "directly_usable_axis_count",
                "indirectly_usable_axis_count",
                "exposure_grouping_status",
                "blocking_reason",
            ],
        )
    )
    lines.extend(
        [
            "",
            "## 4. Rcvr1_2 fixed-context split readiness",
            "",
        ]
    )
    lines.extend(
        markdown_table(
            [row for row in readiness_rows if row["receiver_context"] == "Rcvr1_2"],
            [
                "receiver_context",
                "backend_context",
                "complete_fingerprint_count",
                "candidate_axis_count",
                "directly_usable_axis_count",
                "indirectly_usable_axis_count",
                "exposure_grouping_status",
                "blocking_reason",
            ],
        )
    )
    lines.extend(
        [
            "",
            "## 5. Direct usability now",
            "",
            f"Directly usable axis candidates now: {len(directly_usable)}.",
            "",
            "No candidate is marked directly usable unless both semantic support "
            "and fixed-context grouping support are present. SHAPIROMART06 found "
            "candidate material, not a certified exposure axis.",
            "",
            "## 6. Unresolved semantics",
            "",
        ]
    )
    lines.extend(
        markdown_table(
            gap_rows,
            [
                "receiver_context",
                "gap_type",
                "missing_field_or_relation",
                "current_state",
                "recommended_next_action",
            ],
        )
    )
    lines.extend(
        [
            "",
            "## 7. Single next concrete research step",
            "",
            NEXT_STEP,
            "",
            "## Validation",
            "",
            "```json",
            json.dumps(validation, indent=2, sort_keys=True),
            "```",
        ]
    )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_outputs(
    output_root: Path,
    run_id: str,
    created_at: str,
    candidate_rows: list[dict[str, Any]],
    readiness_rows: list[dict[str, Any]],
    gap_rows: list[dict[str, Any]],
    validation: dict[str, Any],
) -> dict[str, str]:
    paths = output_paths(output_root)
    write_csv(
        paths[CANDIDATES_CSV],
        candidate_rows,
        [
            "geometry_axis_candidate_id",
            "source_table",
            "source_field_or_token",
            "candidate_class",
            "populated_row_count",
            "distinct_value_count",
            "linked_fingerprint_count",
            "fixed_receiver_context_possible",
            "proposed_use",
            "semantic_status",
            "usable_now",
            "limitation",
            "created_at_utc",
            "notes",
        ],
    )
    write_csv(
        paths[READINESS_CSV],
        readiness_rows,
        [
            "exposure_readiness_id",
            "receiver_context",
            "backend_context",
            "complete_fingerprint_count",
            "candidate_axis_count",
            "directly_usable_axis_count",
            "indirectly_usable_axis_count",
            "exposure_grouping_status",
            "blocking_reason",
            "created_at_utc",
            "notes",
        ],
    )
    write_csv(
        paths[GAPS_CSV],
        gap_rows,
        [
            "geometry_axis_gap_id",
            "receiver_context",
            "gap_type",
            "missing_field_or_relation",
            "current_state",
            "recommended_next_action",
            "created_at_utc",
            "notes",
        ],
    )
    write_csv(
        paths[NEXT_STEP_CSV],
        [
            {
                "next_step_id": "SHAPIROMART06_NEXT_001",
                "recommended_next_step": NEXT_STEP,
                "scope_limit": "separate_explicit_task",
                "claim_boundary": CLAIM_BOUNDARY,
            }
        ],
        ["next_step_id", "recommended_next_step", "scope_limit", "claim_boundary"],
    )
    summary = {
        "run_id": run_id,
        "run_timestamp_utc": created_at,
        "script": SCRIPT_NAME,
        "geometry_axis_candidate_count": len(candidate_rows),
        "candidate_class_counts": class_counts(candidate_rows),
        "linkable_candidate_count": sum(
            1
            for row in candidate_rows
            if int(row["linked_fingerprint_count"] or 0) > 0
            and row["candidate_class"] != "unusable_for_exposure_axis"
        ),
        "directly_usable_axis_count": sum(int(row["usable_now"]) for row in candidate_rows),
        "fixed_context_readiness": readiness_rows,
        "geometry_axis_gaps": gap_rows,
        "validation": validation,
        "claim_boundary": CLAIM_BOUNDARY,
        "next_step": NEXT_STEP,
        "warnings": [
            "Timestamp-like or phase-like fields are candidates only until semantics are supported.",
            "Receiver-context separation is not reused as a geometry test.",
            "No physical quantities were computed.",
        ],
        "output_files": {name: str(path) for name, path in paths.items()},
        "stop_reason": "completed_geometry_exposure_axis_discovery",
    }
    paths[SUMMARY_JSON].write_text(
        json.dumps(summary, indent=2, sort_keys=True, ensure_ascii=True) + "\n",
        encoding="utf-8",
    )
    write_readout(
        paths[READOUT_MD],
        run_id,
        created_at,
        candidate_rows,
        readiness_rows,
        gap_rows,
        validation,
    )
    return {name: str(path) for name, path in paths.items()}


def build_run_log_row(
    run_id: str,
    created_at: str,
    candidate_rows: list[dict[str, Any]],
    readiness_rows: list[dict[str, Any]],
    gap_rows: list[dict[str, Any]],
    live_db_modified: bool,
    workcopy_db_modified: bool,
    integrity_result: str,
    fk_violation_count: int,
) -> dict[str, Any]:
    status_by_receiver = {
        row["receiver_context"]: row["exposure_grouping_status"]
        for row in readiness_rows
    }
    return {
        "run_id": run_id,
        "run_timestamp_utc": created_at,
        "geometry_axis_candidate_count": len(candidate_rows),
        "linkable_candidate_count": sum(
            1
            for row in candidate_rows
            if int(row["linked_fingerprint_count"] or 0) > 0
            and row["candidate_class"] != "unusable_for_exposure_axis"
        ),
        "readiness_row_count": len(readiness_rows),
        "gap_row_count": len(gap_rows),
        "context_a_status": status_by_receiver.get("Rcvr_800"),
        "context_b_status": status_by_receiver.get("Rcvr1_2"),
        "live_db_modified": 1 if live_db_modified else 0,
        "workcopy_db_modified": 1 if workcopy_db_modified else 0,
        "integrity_check_result": integrity_result,
        "foreign_key_violation_count": fk_violation_count,
        "notes": (
            "Geometry/Shapiro exposure axis discovery only; no physical exposure "
            "or timing model quantity computed."
        ),
    }


def run(args: argparse.Namespace) -> dict[str, Any]:
    ensure_inputs(args)
    live_before = db_state(args.live_db)
    workcopy_before = db_state(args.workcopy_db)
    created_at = utc_now()
    run_id = "SHAPIROMART06_RUN_" + created_at.replace("-", "").replace(":", "")

    with connect_readonly(args.live_db) as live_con:
        live_con.execute("SELECT name FROM sqlite_master LIMIT 1").fetchone()

    con = connect_writable(args.workcopy_db)
    try:
        validate_required_objects(con)
        target_state = validate_existing_target_state(con, args.allow_existing)
        prior_before = prior_counts(con)
        fingerprint_digest_before = fingerprint_digest(con)
        fingerprint_counts = load_complete_fingerprint_counts(con)
        candidate_rows = build_candidate_rows(con, created_at)
        readiness_rows = build_readiness_rows(con, candidate_rows, created_at)
        gap_rows = build_gap_rows(candidate_rows, readiness_rows, created_at)

        create_tables(con)
        if args.allow_existing:
            clear_target_tables(con)
        insert_rows(con, "mart_shapiro_geometry_axis_candidate", candidate_rows)
        insert_rows(con, "mart_shapiro_fixed_context_exposure_readiness", readiness_rows)
        insert_rows(con, "mart_shapiro_geometry_axis_gap", gap_rows)
        create_views(con)
        con.commit()

        integrity_result = integrity_check(con)
        fk_violations = foreign_key_violations(con)
        prior_after_data = prior_counts(con)
        fingerprint_digest_after_data = fingerprint_digest(con)
        live_after_data = db_state(args.live_db)
        workcopy_after_data = db_state(args.workcopy_db)
        insert_rows(
            con,
            "shapiromart06_run_log",
            [
                build_run_log_row(
                    run_id,
                    created_at,
                    candidate_rows,
                    readiness_rows,
                    gap_rows,
                    live_before != live_after_data,
                    workcopy_before != workcopy_after_data,
                    integrity_result,
                    len(fk_violations),
                )
            ],
        )
        con.commit()

        final_integrity = integrity_check(con)
        final_fk_violations = foreign_key_violations(con)
        final_live_state = db_state(args.live_db)
        final_workcopy_state = db_state(args.workcopy_db)
        final_live_modified = live_before != final_live_state
        final_workcopy_modified = workcopy_before != final_workcopy_state
        prior_after = prior_counts(con)
        fingerprint_digest_after = fingerprint_digest(con)
        queryable = queryable_counts(con)
        con.execute(
            """
            UPDATE shapiromart06_run_log
            SET live_db_modified = ?,
                workcopy_db_modified = ?,
                integrity_check_result = ?,
                foreign_key_violation_count = ?
            WHERE run_id = ?
            """,
            (
                1 if final_live_modified else 0,
                1 if final_workcopy_modified else 0,
                final_integrity,
                len(final_fk_violations),
                run_id,
            ),
        )
        con.commit()

        validation = {
            "live_db_checksum_stat_unchanged": not final_live_modified,
            "workcopy_db_modified": final_workcopy_modified,
            "workcopy_integrity_check": final_integrity,
            "workcopy_foreign_key_violation_count": len(final_fk_violations),
            "prior_shapiromart01_05_counts_preserved": prior_before == prior_after,
            "no_fingerprint_values_changed": fingerprint_digest_before == fingerprint_digest_after,
            "fingerprint_digest_after_data_before_run_log": fingerprint_digest_after_data,
            "complete_fingerprint_count": EXPECTED_TOTAL_COMPLETE,
            "context_counts": fingerprint_counts["context_counts"],
            "receiver_context_comparison_reused_as_geometry_test": False,
            "physical_quantities_computed": False,
            "all_new_objects_queryable": all(isinstance(value, int) for value in queryable.values()),
            "queryable_counts": queryable,
            "pre_run_target_state": target_state,
            "prior_counts_before": prior_before,
            "prior_counts_after_data": prior_after_data,
            "prior_counts_after": prior_after,
            "live_db_before": live_before,
            "live_db_after": final_live_state,
            "workcopy_db_before": workcopy_before,
            "workcopy_db_after": final_workcopy_state,
        }
        required_passes = [
            validation["live_db_checksum_stat_unchanged"],
            validation["workcopy_integrity_check"] == "ok",
            validation["workcopy_foreign_key_violation_count"] == 0,
            validation["prior_shapiromart01_05_counts_preserved"],
            validation["no_fingerprint_values_changed"],
            not validation["receiver_context_comparison_reused_as_geometry_test"],
            not validation["physical_quantities_computed"],
            validation["all_new_objects_queryable"],
        ]
        if not all(required_passes):
            fail("SHAPIROMART06 validation failed; see validation payload.")

        output_files = write_outputs(
            args.output_root,
            run_id,
            created_at,
            candidate_rows,
            readiness_rows,
            gap_rows,
            validation,
        )
        return {
            "run_id": run_id,
            "run_timestamp_utc": created_at,
            "geometry_axis_candidate_count": len(candidate_rows),
            "linkable_candidate_count": sum(
                1
                for row in candidate_rows
                if int(row["linked_fingerprint_count"] or 0) > 0
                and row["candidate_class"] != "unusable_for_exposure_axis"
            ),
            "fixed_context_readiness": readiness_rows,
            "main_gap": gap_rows[0] if gap_rows else None,
            "output_files": output_files,
            "validation": validation,
        }
    finally:
        con.close()


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Discover DB-backed geometry/Shapiro exposure-axis candidates for "
            "fixed receiver/backend SHAPIROMART fingerprints."
        )
    )
    parser.add_argument("--live-db", type=Path, default=DEFAULT_LIVE_DB)
    parser.add_argument("--workcopy-db", type=Path, default=DEFAULT_WORKCOPY_DB)
    parser.add_argument("--output-root", type=Path, default=DEFAULT_OUTPUT_ROOT)
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Allow replacing SHAPIROMART06 output files.",
    )
    parser.add_argument(
        "--allow-existing",
        action="store_true",
        help="Allow replacing existing SHAPIROMART06 DB target rows/views.",
    )
    return parser.parse_args(argv)


def main(argv: list[str]) -> int:
    args = parse_args(argv)
    try:
        result = run(args)
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    print(json.dumps(result, indent=2, sort_keys=True, ensure_ascii=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
