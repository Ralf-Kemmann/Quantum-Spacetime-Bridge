#!/usr/bin/env python3
"""QSB-DB23B: DB-backed two-block signature inspection.

This script copies DB23A into DB23B and inspects structural value signatures in
the 41-token TIM data-line family. It reads only database tables/views already
inside the DB23A database copy. It does not read raw TIM/PAR files, does not
assign physical meaning to token positions, and does not compute timing
quantities, residuals, delays, or model quantities.
"""

from __future__ import annotations

import argparse
import csv
import json
import shutil
import sqlite3
import sys
from collections import Counter, defaultdict
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable


BLOCK_LABEL = "QSB-DB23B_TWO_BLOCK_SIGNATURE_INSPECTION"
DEFAULT_INPUT_DB = Path(
    "runs/QSB-DB/QSB_DB23A_41_TOKEN_FAMILY_INSPECTION/"
    "qsb_research_41_token_family_inspection.db"
)
DEFAULT_OUTPUT_ROOT = Path("runs/QSB-DB/QSB_DB23B_TWO_BLOCK_SIGNATURE_INSPECTION")
DEFAULT_OUTPUT_DB = DEFAULT_OUTPUT_ROOT / "qsb_research_two_block_signature_inspection.db"

LINE_TYPE = "data_line"
TOKEN_COUNT = 41
FAMILY_KEY = "data_line_token_count_41"

BLOCK_A = ("block_a", 3, 5133)
BLOCK_B = ("block_b", 5144, 10939)
TRANSITION = ("transition_gap", 5134, 5143)

FOCUSED_SWITCH_POSITIONS = [7, 11, 13, 17, 23]
TOKEN001_POSITION = 1
LOW_VARIANCE_RECURRING_POSITIONS = [25, 27]
HIGH_VARIANCE_CONTEXT_POSITIONS = [2, 3, 4, 29, 31, 33]
INSPECTED_POSITIONS = sorted(
    set(
        [TOKEN001_POSITION]
        + FOCUSED_SWITCH_POSITIONS
        + LOW_VARIANCE_RECURRING_POSITIONS
        + HIGH_VARIANCE_CONTEXT_POSITIONS
    )
)
TRANSITION_POSITIONS = sorted(set(INSPECTED_POSITIONS + FOCUSED_SWITCH_POSITIONS))

CLAIM_BOUNDARY = (
    "DB23B is a structural two-block signature inspection based only on the "
    "DB23A database substrate. It does not assign physical meaning to TIM "
    "token positions, does not compute timing quantities, residuals, delays, "
    "or model quantities, and does not make Shapiro, QSB-validation, Bridge, "
    "or physical-interpretation claims."
)


@dataclass(frozen=True)
class FamilyRecord:
    tim_record_id: str
    record_index: int
    line_number: int
    source_file_name: str
    source_family_label: str


@dataclass
class BlockDefinition:
    block_label: str
    start_record_index: int
    end_record_index: int
    definition_scope: str
    total_record_index_slots: int
    db_record_count: int
    family_record_count: int
    nonfamily_record_count: int
    line_type_counts_json: str
    token_count_counts_json: str
    block_note: str


@dataclass
class TokenBlockProfile:
    token_position: int
    field_name: str
    block_label: str
    token_focus_role: str
    family_record_count: int
    present_count: int
    missing_count: int
    distinct_value_count: int
    distinct_values_json: str
    top_values_json: str
    dominant_value: str | None
    dominant_count: int
    dominant_fraction: float
    constant_within_block_flag: int
    profile_note: str


@dataclass
class TokenComparison:
    token_position: int
    field_name: str
    token_focus_role: str
    block_a_distinct_count: int
    block_b_distinct_count: int
    block_a_distinct_values_json: str
    block_b_distinct_values_json: str
    block_a_top_values_json: str
    block_b_top_values_json: str
    block_a_dominant_value: str | None
    block_b_dominant_value: str | None
    block_a_dominant_count: int
    block_b_dominant_count: int
    block_a_dominant_fraction: float
    block_b_dominant_fraction: float
    dominant_values_differ_flag: int
    value_set_overlap_count: int
    relation_type: str
    block_discriminating_flag: int
    constant_within_each_block_flag: int
    transition_gap_relation: str
    needs_mapping_flag: int
    comparison_note: str


@dataclass
class CombinedSignatureProfile:
    signature_scope: str
    block_label: str
    signature_rank: int
    signature_json: str
    signature_value: str
    record_count: int
    record_fraction: float
    first_record_index: int
    last_record_index: int
    dominant_signature_flag: int
    signature_note: str


@dataclass
class Token001BlockProfile:
    token001_block_rank: int
    token_position: int
    grouping_token: str
    group_value: str
    first_record_index: int
    last_record_index: int
    record_count: int
    family_sequence_segment_count: int
    contiguous_block_flag: int
    overlaps_block_a_flag: int
    overlaps_transition_gap_flag: int
    overlaps_block_b_flag: int
    crosses_two_block_split_flag: int
    ends_at_block_a_boundary_flag: int
    starts_at_block_b_boundary_flag: int
    boundary_relation: str
    token001_total_contiguous_blocks: int
    token001_split_alignment_status: str
    block_note: str


@dataclass
class TransitionGapRecord:
    record_index: int
    line_exists_flag: int
    line_type: str | None
    token_count: int | None
    family_membership_status: str
    focused_signature_json: str
    inspected_token_values_json: str
    matches_block_a_signature_flag: int
    matches_block_b_signature_flag: int
    transition_gap_relation: str
    status_note: str


def utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def token_name(position: int) -> str:
    return f"tim_token_{position:03d}"


def compact_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=True, separators=(",", ":"))


def pretty_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=True, indent=2)


def ensure_input_db(path: Path) -> None:
    if not path.exists():
        raise FileNotFoundError(f"Input DB does not exist: {path}")
    if not path.is_file():
        raise ValueError(f"Input DB path is not a file: {path}")


def expected_artifacts(output_root: Path, output_db: Path) -> list[Path]:
    return [
        output_db,
        output_root / "db23b_two_block_signature_readout.md",
        output_root / "db23b_two_block_signature_summary.json",
        output_root / "db23b_token_block_comparison.csv",
        output_root / "db23b_focused_token_side_by_side.csv",
        output_root / "db23b_combined_signature_profile.csv",
        output_root / "db23b_token001_block_profile.csv",
        output_root / "db23b_transition_gap_inspection.csv",
        output_root / "db23b_pattern_notes.csv",
    ]


def ensure_safe_outputs(output_root: Path, output_db: Path) -> None:
    existing = [str(path) for path in expected_artifacts(output_root, output_db) if path.exists()]
    if existing:
        raise FileExistsError(
            "Refusing to overwrite existing DB23B artifact(s): "
            + "; ".join(existing)
        )


def connect_db(path: Path) -> sqlite3.Connection:
    con = sqlite3.connect(path)
    con.row_factory = sqlite3.Row
    con.execute("PRAGMA foreign_keys = ON")
    return con


def copy_input_db(input_db: Path, output_root: Path, output_db: Path) -> None:
    output_root.mkdir(parents=True, exist_ok=True)
    shutil.copy2(input_db, output_db)


def query_count_map(
    con: sqlite3.Connection,
    column_name: str,
    start_record_index: int,
    end_record_index: int,
) -> dict[str, int]:
    rows = con.execute(
        f"""
        SELECT {column_name} AS value, COUNT(*) AS n
        FROM db21_tim_raw_record
        WHERE record_index BETWEEN ? AND ?
        GROUP BY {column_name}
        ORDER BY {column_name}
        """,
        (start_record_index, end_record_index),
    ).fetchall()
    return {str(row["value"]): int(row["n"]) for row in rows}


def fetch_family_records(con: sqlite3.Connection) -> list[FamilyRecord]:
    rows = con.execute(
        """
        SELECT
            tim_record_id,
            record_index,
            line_number,
            source_file_name,
            source_family_label
        FROM db21_tim_raw_record
        WHERE line_type = ? AND token_count = ?
        ORDER BY record_index
        """,
        (LINE_TYPE, TOKEN_COUNT),
    ).fetchall()
    if not rows:
        raise RuntimeError("No 41-token data_line family records found in DB23A copy.")
    return [
        FamilyRecord(
            tim_record_id=row["tim_record_id"],
            record_index=int(row["record_index"]),
            line_number=int(row["line_number"]),
            source_file_name=row["source_file_name"],
            source_family_label=row["source_family_label"],
        )
        for row in rows
    ]


def record_indices_in_range(
    family_records: list[FamilyRecord],
    start_record_index: int,
    end_record_index: int,
) -> list[int]:
    return [
        record.record_index
        for record in family_records
        if start_record_index <= record.record_index <= end_record_index
    ]


def create_tables(con: sqlite3.Connection) -> None:
    con.executescript(
        """
        CREATE TABLE db23b_block_definition (
            block_label TEXT PRIMARY KEY,
            start_record_index INTEGER NOT NULL,
            end_record_index INTEGER NOT NULL,
            definition_scope TEXT NOT NULL,
            total_record_index_slots INTEGER NOT NULL,
            db_record_count INTEGER NOT NULL,
            family_record_count INTEGER NOT NULL,
            nonfamily_record_count INTEGER NOT NULL,
            line_type_counts_json TEXT NOT NULL,
            token_count_counts_json TEXT NOT NULL,
            block_note TEXT NOT NULL,
            created_at_utc TEXT NOT NULL,
            claim_boundary TEXT NOT NULL
        );

        CREATE TABLE db23b_token_block_value_profile (
            token_block_value_profile_id INTEGER PRIMARY KEY,
            token_position INTEGER NOT NULL,
            field_name TEXT NOT NULL,
            block_label TEXT NOT NULL,
            token_focus_role TEXT NOT NULL,
            family_record_count INTEGER NOT NULL,
            present_count INTEGER NOT NULL,
            missing_count INTEGER NOT NULL,
            distinct_value_count INTEGER NOT NULL,
            distinct_values_json TEXT NOT NULL,
            top_values_json TEXT NOT NULL,
            dominant_value TEXT,
            dominant_count INTEGER NOT NULL,
            dominant_fraction REAL NOT NULL,
            constant_within_block_flag INTEGER NOT NULL CHECK (constant_within_block_flag IN (0, 1)),
            profile_note TEXT NOT NULL,
            created_at_utc TEXT NOT NULL,
            UNIQUE (token_position, block_label),
            FOREIGN KEY (block_label)
                REFERENCES db23b_block_definition(block_label)
        );

        CREATE TABLE db23b_token_block_comparison (
            token_block_comparison_id INTEGER PRIMARY KEY,
            token_position INTEGER NOT NULL,
            field_name TEXT NOT NULL,
            token_focus_role TEXT NOT NULL,
            block_a_distinct_count INTEGER NOT NULL,
            block_b_distinct_count INTEGER NOT NULL,
            block_a_distinct_values_json TEXT NOT NULL,
            block_b_distinct_values_json TEXT NOT NULL,
            block_a_top_values_json TEXT NOT NULL,
            block_b_top_values_json TEXT NOT NULL,
            block_a_dominant_value TEXT,
            block_b_dominant_value TEXT,
            block_a_dominant_count INTEGER NOT NULL,
            block_b_dominant_count INTEGER NOT NULL,
            block_a_dominant_fraction REAL NOT NULL,
            block_b_dominant_fraction REAL NOT NULL,
            dominant_values_differ_flag INTEGER NOT NULL CHECK (dominant_values_differ_flag IN (0, 1)),
            value_set_overlap_count INTEGER NOT NULL,
            relation_type TEXT NOT NULL,
            block_discriminating_flag INTEGER NOT NULL CHECK (block_discriminating_flag IN (0, 1)),
            constant_within_each_block_flag INTEGER NOT NULL CHECK (constant_within_each_block_flag IN (0, 1)),
            transition_gap_relation TEXT NOT NULL,
            needs_mapping_flag INTEGER NOT NULL CHECK (needs_mapping_flag IN (0, 1)),
            comparison_note TEXT NOT NULL,
            created_at_utc TEXT NOT NULL,
            UNIQUE (token_position)
        );

        CREATE TABLE db23b_combined_signature_profile (
            combined_signature_profile_id INTEGER PRIMARY KEY,
            signature_scope TEXT NOT NULL,
            block_label TEXT NOT NULL,
            signature_rank INTEGER NOT NULL,
            signature_json TEXT NOT NULL,
            signature_value TEXT NOT NULL,
            record_count INTEGER NOT NULL,
            record_fraction REAL NOT NULL,
            first_record_index INTEGER NOT NULL,
            last_record_index INTEGER NOT NULL,
            dominant_signature_flag INTEGER NOT NULL CHECK (dominant_signature_flag IN (0, 1)),
            signature_note TEXT NOT NULL,
            created_at_utc TEXT NOT NULL,
            UNIQUE (signature_scope, block_label, signature_rank),
            FOREIGN KEY (block_label)
                REFERENCES db23b_block_definition(block_label)
        );

        CREATE TABLE db23b_token001_block_profile (
            token001_block_profile_id INTEGER PRIMARY KEY,
            token001_block_rank INTEGER NOT NULL,
            token_position INTEGER NOT NULL,
            grouping_token TEXT NOT NULL,
            group_value TEXT NOT NULL,
            first_record_index INTEGER NOT NULL,
            last_record_index INTEGER NOT NULL,
            record_count INTEGER NOT NULL,
            family_sequence_segment_count INTEGER NOT NULL,
            contiguous_block_flag INTEGER NOT NULL CHECK (contiguous_block_flag IN (0, 1)),
            overlaps_block_a_flag INTEGER NOT NULL CHECK (overlaps_block_a_flag IN (0, 1)),
            overlaps_transition_gap_flag INTEGER NOT NULL CHECK (overlaps_transition_gap_flag IN (0, 1)),
            overlaps_block_b_flag INTEGER NOT NULL CHECK (overlaps_block_b_flag IN (0, 1)),
            crosses_two_block_split_flag INTEGER NOT NULL CHECK (crosses_two_block_split_flag IN (0, 1)),
            ends_at_block_a_boundary_flag INTEGER NOT NULL CHECK (ends_at_block_a_boundary_flag IN (0, 1)),
            starts_at_block_b_boundary_flag INTEGER NOT NULL CHECK (starts_at_block_b_boundary_flag IN (0, 1)),
            boundary_relation TEXT NOT NULL,
            token001_total_contiguous_blocks INTEGER NOT NULL,
            token001_split_alignment_status TEXT NOT NULL,
            block_note TEXT NOT NULL,
            created_at_utc TEXT NOT NULL
        );

        CREATE TABLE db23b_transition_gap_inspection (
            transition_gap_inspection_id INTEGER PRIMARY KEY,
            record_index INTEGER NOT NULL UNIQUE,
            line_exists_flag INTEGER NOT NULL CHECK (line_exists_flag IN (0, 1)),
            line_type TEXT,
            token_count INTEGER,
            family_membership_status TEXT NOT NULL,
            focused_signature_json TEXT NOT NULL,
            inspected_token_values_json TEXT NOT NULL,
            matches_block_a_signature_flag INTEGER NOT NULL CHECK (matches_block_a_signature_flag IN (0, 1)),
            matches_block_b_signature_flag INTEGER NOT NULL CHECK (matches_block_b_signature_flag IN (0, 1)),
            transition_gap_relation TEXT NOT NULL,
            status_note TEXT NOT NULL,
            created_at_utc TEXT NOT NULL
        );

        CREATE TABLE db23b_two_block_pattern_note (
            pattern_note_id INTEGER PRIMARY KEY,
            note_type TEXT NOT NULL,
            token_position INTEGER,
            field_name TEXT,
            note_text TEXT NOT NULL,
            claim_boundary TEXT NOT NULL,
            created_at_utc TEXT NOT NULL
        );
        """
    )


def create_views(con: sqlite3.Connection) -> None:
    con.executescript(
        """
        CREATE VIEW qsb_v_db23b_block_definitions AS
        SELECT
            block_label,
            start_record_index,
            end_record_index,
            definition_scope,
            total_record_index_slots,
            db_record_count,
            family_record_count,
            nonfamily_record_count,
            line_type_counts_json,
            token_count_counts_json,
            block_note,
            claim_boundary
        FROM db23b_block_definition
        ORDER BY start_record_index;

        CREATE VIEW qsb_v_db23b_token_block_comparison AS
        SELECT
            token_position,
            field_name,
            token_focus_role,
            block_a_distinct_count,
            block_b_distinct_count,
            block_a_dominant_value,
            block_b_dominant_value,
            block_a_dominant_count,
            block_b_dominant_count,
            block_a_dominant_fraction,
            block_b_dominant_fraction,
            dominant_values_differ_flag,
            value_set_overlap_count,
            relation_type,
            block_discriminating_flag,
            constant_within_each_block_flag,
            transition_gap_relation,
            needs_mapping_flag,
            comparison_note
        FROM db23b_token_block_comparison
        ORDER BY token_position;

        CREATE VIEW qsb_v_db23b_focused_token_side_by_side AS
        SELECT
            token_position,
            field_name,
            token_focus_role,
            block_a_dominant_value,
            block_b_dominant_value,
            relation_type,
            block_discriminating_flag,
            constant_within_each_block_flag,
            transition_gap_relation,
            block_a_top_values_json,
            block_b_top_values_json,
            needs_mapping_flag
        FROM db23b_token_block_comparison
        WHERE token_position IN (1, 7, 11, 13, 17, 23, 25, 27)
        ORDER BY token_position;

        CREATE VIEW qsb_v_db23b_combined_signature_profile AS
        SELECT
            signature_scope,
            block_label,
            signature_rank,
            signature_value,
            signature_json,
            record_count,
            record_fraction,
            first_record_index,
            last_record_index,
            dominant_signature_flag,
            signature_note
        FROM db23b_combined_signature_profile
        ORDER BY signature_scope, block_label, signature_rank;

        CREATE VIEW qsb_v_db23b_token001_block_profile AS
        SELECT
            token001_block_rank,
            grouping_token,
            group_value,
            first_record_index,
            last_record_index,
            record_count,
            family_sequence_segment_count,
            contiguous_block_flag,
            overlaps_block_a_flag,
            overlaps_transition_gap_flag,
            overlaps_block_b_flag,
            crosses_two_block_split_flag,
            ends_at_block_a_boundary_flag,
            starts_at_block_b_boundary_flag,
            boundary_relation,
            token001_total_contiguous_blocks,
            token001_split_alignment_status,
            block_note
        FROM db23b_token001_block_profile
        ORDER BY token001_block_rank;

        CREATE VIEW qsb_v_db23b_transition_gap_inspection AS
        SELECT
            record_index,
            line_exists_flag,
            line_type,
            token_count,
            family_membership_status,
            focused_signature_json,
            inspected_token_values_json,
            matches_block_a_signature_flag,
            matches_block_b_signature_flag,
            transition_gap_relation,
            status_note
        FROM db23b_transition_gap_inspection
        ORDER BY record_index;

        CREATE VIEW qsb_v_db23b_first_two_block_whisper AS
        SELECT
            'data_line_token_count_41' AS family_key,
            (
                SELECT 'A=' || family_record_count || ' records [' ||
                       start_record_index || '-' || end_record_index || ']'
                FROM db23b_block_definition
                WHERE block_label = 'block_a'
            ) AS block_a_definition,
            (
                SELECT 'B=' || family_record_count || ' records [' ||
                       start_record_index || '-' || end_record_index || ']'
                FROM db23b_block_definition
                WHERE block_label = 'block_b'
            ) AS block_b_definition,
            (
                SELECT group_concat(field_name || '@' || token_position, '; ')
                FROM db23b_token_block_comparison
                WHERE token_position IN (7, 11, 13, 17, 23)
                  AND block_discriminating_flag = 1
                  AND constant_within_each_block_flag = 1
            ) AS focused_tokens_that_switch_together,
            (
                SELECT signature_value
                FROM db23b_combined_signature_profile
                WHERE block_label = 'block_a'
                  AND dominant_signature_flag = 1
                LIMIT 1
            ) AS dominant_block_a_signature,
            (
                SELECT signature_value
                FROM db23b_combined_signature_profile
                WHERE block_label = 'block_b'
                  AND dominant_signature_flag = 1
                LIMIT 1
            ) AS dominant_block_b_signature,
            (
                SELECT CASE
                    WHEN COUNT(*) = 0 THEN 'absent'
                    WHEN SUM(CASE WHEN family_membership_status = 'outside_41_data_line_family'
                                   THEN 1 ELSE 0 END) = COUNT(*)
                         THEN 'separate_outside_41_family'
                    WHEN SUM(matches_block_a_signature_flag) = COUNT(*) THEN 'aligns_with_block_a'
                    WHEN SUM(matches_block_b_signature_flag) = COUNT(*) THEN 'aligns_with_block_b'
                    ELSE 'mixed_or_separate'
                END
                FROM db23b_transition_gap_inspection
            ) AS transition_gap_status,
            (
                SELECT token001_split_alignment_status
                FROM db23b_token001_block_profile
                ORDER BY token001_block_rank
                LIMIT 1
            ) AS token001_boundary_alignment,
            (
                SELECT group_concat(field_name || '@' || token_position || ':' ||
                                    relation_type || '/needs_mapping', '; ')
                FROM db23b_token_block_comparison
                WHERE needs_mapping_flag = 1
                ORDER BY token_position
            ) AS open_mapping_needs,
            'DB23A copied to DB23B; no raw file fallback' AS data_substrate_used,
            (
                SELECT claim_boundary
                FROM db23b_block_definition
                WHERE block_label = 'block_a'
            ) AS claim_boundary;
        """
    )


def build_block_definitions(
    con: sqlite3.Connection,
    family_records: list[FamilyRecord],
) -> list[BlockDefinition]:
    family_sets = {
        label: set(record_indices_in_range(family_records, start, end))
        for label, start, end in [BLOCK_A, BLOCK_B, TRANSITION]
    }
    definitions = []
    for label, start, end in [BLOCK_A, BLOCK_B, TRANSITION]:
        db_record_count = int(
            con.execute(
                """
                SELECT COUNT(*) AS n
                FROM db21_tim_raw_record
                WHERE record_index BETWEEN ? AND ?
                """,
                (start, end),
            ).fetchone()["n"]
        )
        family_count = len(family_sets[label])
        nonfamily_count = db_record_count - family_count
        if label == "transition_gap":
            note = (
                "Transition/gap zone between the two 41-family blocks; records "
                "are inspected directly from DB rows."
            )
            scope = "transition_gap_zone"
        else:
            note = "41-token data-line family block defined by record-index range."
            scope = "41_token_data_line_family"
        definitions.append(
            BlockDefinition(
                block_label=label,
                start_record_index=start,
                end_record_index=end,
                definition_scope=scope,
                total_record_index_slots=end - start + 1,
                db_record_count=db_record_count,
                family_record_count=family_count,
                nonfamily_record_count=nonfamily_count,
                line_type_counts_json=compact_json(query_count_map(con, "line_type", start, end)),
                token_count_counts_json=compact_json(query_count_map(con, "token_count", start, end)),
                block_note=note,
            )
        )
    return definitions


def insert_block_definitions(
    con: sqlite3.Connection,
    definitions: list[BlockDefinition],
    created_at: str,
) -> None:
    con.executemany(
        """
        INSERT INTO db23b_block_definition (
            block_label,
            start_record_index,
            end_record_index,
            definition_scope,
            total_record_index_slots,
            db_record_count,
            family_record_count,
            nonfamily_record_count,
            line_type_counts_json,
            token_count_counts_json,
            block_note,
            created_at_utc,
            claim_boundary
        )
        VALUES (
            :block_label,
            :start_record_index,
            :end_record_index,
            :definition_scope,
            :total_record_index_slots,
            :db_record_count,
            :family_record_count,
            :nonfamily_record_count,
            :line_type_counts_json,
            :token_count_counts_json,
            :block_note,
            :created_at_utc,
            :claim_boundary
        )
        """,
        [
            {
                **definition.__dict__,
                "created_at_utc": created_at,
                "claim_boundary": CLAIM_BOUNDARY,
            }
            for definition in definitions
        ],
    )


def fetch_token_values(
    con: sqlite3.Connection,
    positions: Iterable[int],
    family_only: bool,
    start_record_index: int | None = None,
    end_record_index: int | None = None,
) -> dict[int, dict[int, str]]:
    position_list = sorted(set(positions))
    fields = [token_name(position) for position in position_list]
    placeholders = ",".join("?" for _ in fields)
    values_by_position: dict[int, dict[int, str]] = {position: {} for position in position_list}
    conditions = [f"f.field_name IN ({placeholders})"]
    params: list[Any] = list(fields)
    if family_only:
        conditions.append("r.line_type = ?")
        conditions.append("r.token_count = ?")
        params.extend([LINE_TYPE, TOKEN_COUNT])
    if start_record_index is not None and end_record_index is not None:
        conditions.append("r.record_index BETWEEN ? AND ?")
        params.extend([start_record_index, end_record_index])
    sql = f"""
        SELECT
            r.record_index,
            f.field_name,
            f.raw_value_text
        FROM db21_tim_raw_record r
        JOIN db21_tim_raw_field_value f
            ON f.tim_record_id = r.tim_record_id
        WHERE {' AND '.join(conditions)}
        ORDER BY r.record_index, f.field_name
    """
    for row in con.execute(sql, params):
        field_name = row["field_name"]
        position = int(field_name.rsplit("_", 1)[1])
        values_by_position[position][int(row["record_index"])] = row["raw_value_text"]
    return values_by_position


def token_focus_role(position: int) -> str:
    if position in FOCUSED_SWITCH_POSITIONS:
        return "focused_two_block_switch_token"
    if position == TOKEN001_POSITION:
        return "token001_contiguous_block_context"
    if position in LOW_VARIANCE_RECURRING_POSITIONS:
        return "low_variance_recurring_context"
    if position in HIGH_VARIANCE_CONTEXT_POSITIONS:
        return "high_variance_context_only"
    return "needs_mapping"


def top_values(values: list[str], denominator: int, limit: int = 10) -> list[dict[str, Any]]:
    counts = Counter(values)
    ranked = sorted(counts.items(), key=lambda item: (-item[1], str(item[0])))
    return [
        {
            "value": value,
            "count": int(count),
            "fraction": count / denominator if denominator else 0.0,
        }
        for value, count in ranked[:limit]
    ]


def build_token_block_profiles(
    family_records: list[FamilyRecord],
    values_by_position: dict[int, dict[int, str]],
) -> list[TokenBlockProfile]:
    block_ranges = [BLOCK_A, BLOCK_B]
    profiles: list[TokenBlockProfile] = []
    for position in INSPECTED_POSITIONS:
        field_name = token_name(position)
        for block_label, start, end in block_ranges:
            record_indices = record_indices_in_range(family_records, start, end)
            values = [
                values_by_position[position][record_index]
                for record_index in record_indices
                if record_index in values_by_position[position]
            ]
            distinct_values = sorted(set(values), key=str)
            top = top_values(values, len(record_indices))
            dominant = top[0] if top else {"value": None, "count": 0, "fraction": 0.0}
            profiles.append(
                TokenBlockProfile(
                    token_position=position,
                    field_name=field_name,
                    block_label=block_label,
                    token_focus_role=token_focus_role(position),
                    family_record_count=len(record_indices),
                    present_count=len(values),
                    missing_count=len(record_indices) - len(values),
                    distinct_value_count=len(distinct_values),
                    distinct_values_json=compact_json(distinct_values),
                    top_values_json=compact_json(top),
                    dominant_value=dominant["value"],
                    dominant_count=int(dominant["count"]),
                    dominant_fraction=float(dominant["fraction"]),
                    constant_within_block_flag=int(
                        len(distinct_values) == 1 and len(values) == len(record_indices)
                    ),
                    profile_note=(
                        "Structural token/block profile only; token remains "
                        "needs_mapping before semantic use."
                    ),
                )
            )
    return profiles


def insert_token_block_profiles(
    con: sqlite3.Connection,
    profiles: list[TokenBlockProfile],
    created_at: str,
) -> None:
    con.executemany(
        """
        INSERT INTO db23b_token_block_value_profile (
            token_position,
            field_name,
            block_label,
            token_focus_role,
            family_record_count,
            present_count,
            missing_count,
            distinct_value_count,
            distinct_values_json,
            top_values_json,
            dominant_value,
            dominant_count,
            dominant_fraction,
            constant_within_block_flag,
            profile_note,
            created_at_utc
        )
        VALUES (
            :token_position,
            :field_name,
            :block_label,
            :token_focus_role,
            :family_record_count,
            :present_count,
            :missing_count,
            :distinct_value_count,
            :distinct_values_json,
            :top_values_json,
            :dominant_value,
            :dominant_count,
            :dominant_fraction,
            :constant_within_block_flag,
            :profile_note,
            :created_at_utc
        )
        """,
        [{**profile.__dict__, "created_at_utc": created_at} for profile in profiles],
    )


def transition_relation_for_token(
    con: sqlite3.Connection,
    position: int,
    block_a_values: set[str],
    block_b_values: set[str],
) -> str:
    field_name = token_name(position)
    rows = con.execute(
        """
        SELECT
            r.line_type,
            r.token_count,
            f.raw_value_text
        FROM db21_tim_raw_record r
        LEFT JOIN db21_tim_raw_field_value f
            ON f.tim_record_id = r.tim_record_id
           AND f.field_name = ?
        WHERE r.record_index BETWEEN ? AND ?
        ORDER BY r.record_index
        """,
        (field_name, TRANSITION[1], TRANSITION[2]),
    ).fetchall()
    if not rows:
        return "absent"
    family_rows = [
        row for row in rows if row["line_type"] == LINE_TYPE and int(row["token_count"]) == TOKEN_COUNT
    ]
    if not family_rows:
        return "separate_non_41_family_zone"
    values = {row["raw_value_text"] for row in family_rows if row["raw_value_text"] is not None}
    if values and values.issubset(block_a_values):
        return "aligns_with_block_a"
    if values and values.issubset(block_b_values):
        return "aligns_with_block_b"
    if values and values.intersection(block_a_values) and values.intersection(block_b_values):
        return "mixed"
    return "separate_pattern"


def classify_relation(
    a_values: set[str],
    b_values: set[str],
    a_dominant: str | None,
    b_dominant: str | None,
) -> str:
    if not a_values and not b_values:
        return "needs_mapping"
    if a_values == b_values and a_dominant == b_dominant:
        return "equal"
    overlap = a_values.intersection(b_values)
    if not overlap and a_dominant != b_dominant:
        return "different"
    if overlap:
        return "partial_overlap"
    if a_dominant is None or b_dominant is None:
        return "needs_mapping"
    return "mixed"


def build_token_comparisons(
    con: sqlite3.Connection,
    profiles: list[TokenBlockProfile],
) -> list[TokenComparison]:
    profile_by_key = {(profile.token_position, profile.block_label): profile for profile in profiles}
    comparisons: list[TokenComparison] = []
    for position in INSPECTED_POSITIONS:
        a_profile = profile_by_key[(position, "block_a")]
        b_profile = profile_by_key[(position, "block_b")]
        a_values = set(json.loads(a_profile.distinct_values_json))
        b_values = set(json.loads(b_profile.distinct_values_json))
        relation = classify_relation(
            a_values,
            b_values,
            a_profile.dominant_value,
            b_profile.dominant_value,
        )
        dominant_values_differ = int(a_profile.dominant_value != b_profile.dominant_value)
        overlap_count = len(a_values.intersection(b_values))
        constant_each = int(
            a_profile.constant_within_block_flag == 1
            and b_profile.constant_within_block_flag == 1
        )
        block_discriminating = int(
            bool(a_values)
            and bool(b_values)
            and overlap_count == 0
            and dominant_values_differ == 1
        )
        transition_relation = transition_relation_for_token(con, position, a_values, b_values)
        if position in FOCUSED_SWITCH_POSITIONS and block_discriminating and constant_each:
            note = "Token switches together with the focused five-token block signature."
        elif position == TOKEN001_POSITION:
            note = (
                "Token has many contiguous value blocks; it partitions records more "
                "finely than the two-block split."
            )
        elif position in LOW_VARIANCE_RECURRING_POSITIONS:
            note = "Low-variance recurring token; values are not a primary two-block driver."
        elif position in HIGH_VARIANCE_CONTEXT_POSITIONS:
            note = "High-variance token retained only as context for this block inspection."
        else:
            note = "Structural comparison only."
        comparisons.append(
            TokenComparison(
                token_position=position,
                field_name=token_name(position),
                token_focus_role=token_focus_role(position),
                block_a_distinct_count=a_profile.distinct_value_count,
                block_b_distinct_count=b_profile.distinct_value_count,
                block_a_distinct_values_json=a_profile.distinct_values_json,
                block_b_distinct_values_json=b_profile.distinct_values_json,
                block_a_top_values_json=a_profile.top_values_json,
                block_b_top_values_json=b_profile.top_values_json,
                block_a_dominant_value=a_profile.dominant_value,
                block_b_dominant_value=b_profile.dominant_value,
                block_a_dominant_count=a_profile.dominant_count,
                block_b_dominant_count=b_profile.dominant_count,
                block_a_dominant_fraction=a_profile.dominant_fraction,
                block_b_dominant_fraction=b_profile.dominant_fraction,
                dominant_values_differ_flag=dominant_values_differ,
                value_set_overlap_count=overlap_count,
                relation_type=relation,
                block_discriminating_flag=block_discriminating,
                constant_within_each_block_flag=constant_each,
                transition_gap_relation=transition_relation,
                needs_mapping_flag=1,
                comparison_note=note,
            )
        )
    return comparisons


def insert_token_comparisons(
    con: sqlite3.Connection,
    comparisons: list[TokenComparison],
    created_at: str,
) -> None:
    con.executemany(
        """
        INSERT INTO db23b_token_block_comparison (
            token_position,
            field_name,
            token_focus_role,
            block_a_distinct_count,
            block_b_distinct_count,
            block_a_distinct_values_json,
            block_b_distinct_values_json,
            block_a_top_values_json,
            block_b_top_values_json,
            block_a_dominant_value,
            block_b_dominant_value,
            block_a_dominant_count,
            block_b_dominant_count,
            block_a_dominant_fraction,
            block_b_dominant_fraction,
            dominant_values_differ_flag,
            value_set_overlap_count,
            relation_type,
            block_discriminating_flag,
            constant_within_each_block_flag,
            transition_gap_relation,
            needs_mapping_flag,
            comparison_note,
            created_at_utc
        )
        VALUES (
            :token_position,
            :field_name,
            :token_focus_role,
            :block_a_distinct_count,
            :block_b_distinct_count,
            :block_a_distinct_values_json,
            :block_b_distinct_values_json,
            :block_a_top_values_json,
            :block_b_top_values_json,
            :block_a_dominant_value,
            :block_b_dominant_value,
            :block_a_dominant_count,
            :block_b_dominant_count,
            :block_a_dominant_fraction,
            :block_b_dominant_fraction,
            :dominant_values_differ_flag,
            :value_set_overlap_count,
            :relation_type,
            :block_discriminating_flag,
            :constant_within_each_block_flag,
            :transition_gap_relation,
            :needs_mapping_flag,
            :comparison_note,
            :created_at_utc
        )
        """,
        [{**comparison.__dict__, "created_at_utc": created_at} for comparison in comparisons],
    )


def signature_for_record(
    record_index: int,
    values_by_position: dict[int, dict[int, str]],
) -> dict[str, str | None]:
    return {
        token_name(position): values_by_position[position].get(record_index)
        for position in FOCUSED_SWITCH_POSITIONS
    }


def signature_value(signature: dict[str, str | None]) -> str:
    return "|".join(f"{field}={value}" for field, value in signature.items())


def build_combined_signatures(
    family_records: list[FamilyRecord],
    values_by_position: dict[int, dict[int, str]],
) -> tuple[list[CombinedSignatureProfile], dict[str, str]]:
    profiles: list[CombinedSignatureProfile] = []
    dominant_by_block: dict[str, str] = {}
    for block_label, start, end in [BLOCK_A, BLOCK_B]:
        record_indices = record_indices_in_range(family_records, start, end)
        by_signature: dict[str, dict[str, Any]] = {}
        for record_index in record_indices:
            signature = signature_for_record(record_index, values_by_position)
            sig_value = signature_value(signature)
            if sig_value not in by_signature:
                by_signature[sig_value] = {
                    "signature": signature,
                    "record_indices": [],
                }
            by_signature[sig_value]["record_indices"].append(record_index)
        ranked = sorted(
            by_signature.items(),
            key=lambda item: (-len(item[1]["record_indices"]), item[0]),
        )
        if ranked:
            dominant_by_block[block_label] = ranked[0][0]
        for rank, (sig_value, payload) in enumerate(ranked, start=1):
            indices = payload["record_indices"]
            profiles.append(
                CombinedSignatureProfile(
                    signature_scope="tim_token_007_011_013_017_023",
                    block_label=block_label,
                    signature_rank=rank,
                    signature_json=compact_json(payload["signature"]),
                    signature_value=sig_value,
                    record_count=len(indices),
                    record_fraction=len(indices) / len(record_indices)
                    if record_indices
                    else 0.0,
                    first_record_index=min(indices),
                    last_record_index=max(indices),
                    dominant_signature_flag=int(rank == 1),
                    signature_note=(
                        "Combined focused-token structural signature; no semantic "
                        "role assigned."
                    ),
                )
            )
    return profiles, dominant_by_block


def insert_combined_signatures(
    con: sqlite3.Connection,
    profiles: list[CombinedSignatureProfile],
    created_at: str,
) -> None:
    con.executemany(
        """
        INSERT INTO db23b_combined_signature_profile (
            signature_scope,
            block_label,
            signature_rank,
            signature_json,
            signature_value,
            record_count,
            record_fraction,
            first_record_index,
            last_record_index,
            dominant_signature_flag,
            signature_note,
            created_at_utc
        )
        VALUES (
            :signature_scope,
            :block_label,
            :signature_rank,
            :signature_json,
            :signature_value,
            :record_count,
            :record_fraction,
            :first_record_index,
            :last_record_index,
            :dominant_signature_flag,
            :signature_note,
            :created_at_utc
        )
        """,
        [{**profile.__dict__, "created_at_utc": created_at} for profile in profiles],
    )


def segment_count(indices: list[int]) -> int:
    if not indices:
        return 0
    ordered = sorted(indices)
    segments = 1
    previous = ordered[0]
    for current in ordered[1:]:
        if current != previous + 1:
            segments += 1
        previous = current
    return segments


def build_token001_blocks(
    family_records: list[FamilyRecord],
    values_by_position: dict[int, dict[int, str]],
) -> list[Token001BlockProfile]:
    values_by_record = values_by_position[TOKEN001_POSITION]
    records_by_value: dict[str, list[int]] = defaultdict(list)
    sequence_positions_by_value: dict[str, list[int]] = defaultdict(list)
    for sequence_position, record in enumerate(family_records, start=1):
        value = values_by_record.get(record.record_index)
        if value is not None:
            records_by_value[value].append(record.record_index)
            sequence_positions_by_value[value].append(sequence_position)
    raw_blocks: list[dict[str, Any]] = []
    for value, indices in records_by_value.items():
        sequence_segments = segment_count(sequence_positions_by_value[value])
        raw_blocks.append(
            {
                "value": value,
                "indices": sorted(indices),
                "first": min(indices),
                "last": max(indices),
                "count": len(indices),
                "segments": sequence_segments,
                "contiguous": int(sequence_segments == 1),
            }
        )
    total_blocks = len(raw_blocks)
    crossing_count = sum(
        1
        for block in raw_blocks
        if block["first"] <= BLOCK_A[2] and block["last"] >= BLOCK_B[1]
    )
    ends_at_a = sum(1 for block in raw_blocks if block["last"] == BLOCK_A[2])
    starts_at_b = sum(1 for block in raw_blocks if block["first"] == BLOCK_B[1])
    if crossing_count:
        alignment_status = "token001_block_crosses_two_block_split"
    elif ends_at_a and starts_at_b and total_blocks > 2:
        alignment_status = "boundary_present_at_split_but_not_unique"
    elif ends_at_a and starts_at_b:
        alignment_status = "boundary_present_at_split"
    else:
        alignment_status = "no_token001_boundary_at_split"
    ranked = sorted(raw_blocks, key=lambda item: (-item["count"], item["first"], item["value"]))
    profiles: list[Token001BlockProfile] = []
    for rank, block in enumerate(ranked, start=1):
        first = int(block["first"])
        last = int(block["last"])
        overlaps_a = int(first <= BLOCK_A[2] and last >= BLOCK_A[1])
        overlaps_transition = int(first <= TRANSITION[2] and last >= TRANSITION[1])
        overlaps_b = int(first <= BLOCK_B[2] and last >= BLOCK_B[1])
        crosses_split = int(first <= BLOCK_A[2] and last >= BLOCK_B[1])
        ends_at_boundary = int(last == BLOCK_A[2])
        starts_at_boundary = int(first == BLOCK_B[1])
        if crosses_split:
            boundary_relation = "crosses_two_block_split"
        elif ends_at_boundary:
            boundary_relation = "ends_at_block_a_boundary"
        elif starts_at_boundary:
            boundary_relation = "starts_at_block_b_boundary"
        elif overlaps_a:
            boundary_relation = "inside_block_a"
        elif overlaps_b:
            boundary_relation = "inside_block_b"
        else:
            boundary_relation = "outside_two_block_ranges"
        profiles.append(
            Token001BlockProfile(
                token001_block_rank=rank,
                token_position=TOKEN001_POSITION,
                grouping_token=token_name(TOKEN001_POSITION),
                group_value=block["value"],
                first_record_index=first,
                last_record_index=last,
                record_count=int(block["count"]),
                family_sequence_segment_count=int(block["segments"]),
                contiguous_block_flag=int(block["contiguous"]),
                overlaps_block_a_flag=overlaps_a,
                overlaps_transition_gap_flag=overlaps_transition,
                overlaps_block_b_flag=overlaps_b,
                crosses_two_block_split_flag=crosses_split,
                ends_at_block_a_boundary_flag=ends_at_boundary,
                starts_at_block_b_boundary_flag=starts_at_boundary,
                boundary_relation=boundary_relation,
                token001_total_contiguous_blocks=total_blocks,
                token001_split_alignment_status=alignment_status,
                block_note=(
                    "token_001 contiguous block is structural context only; "
                    "no semantic role assigned."
                ),
            )
        )
    return profiles


def insert_token001_blocks(
    con: sqlite3.Connection,
    profiles: list[Token001BlockProfile],
    created_at: str,
) -> None:
    con.executemany(
        """
        INSERT INTO db23b_token001_block_profile (
            token001_block_rank,
            token_position,
            grouping_token,
            group_value,
            first_record_index,
            last_record_index,
            record_count,
            family_sequence_segment_count,
            contiguous_block_flag,
            overlaps_block_a_flag,
            overlaps_transition_gap_flag,
            overlaps_block_b_flag,
            crosses_two_block_split_flag,
            ends_at_block_a_boundary_flag,
            starts_at_block_b_boundary_flag,
            boundary_relation,
            token001_total_contiguous_blocks,
            token001_split_alignment_status,
            block_note,
            created_at_utc
        )
        VALUES (
            :token001_block_rank,
            :token_position,
            :grouping_token,
            :group_value,
            :first_record_index,
            :last_record_index,
            :record_count,
            :family_sequence_segment_count,
            :contiguous_block_flag,
            :overlaps_block_a_flag,
            :overlaps_transition_gap_flag,
            :overlaps_block_b_flag,
            :crosses_two_block_split_flag,
            :ends_at_block_a_boundary_flag,
            :starts_at_block_b_boundary_flag,
            :boundary_relation,
            :token001_total_contiguous_blocks,
            :token001_split_alignment_status,
            :block_note,
            :created_at_utc
        )
        """,
        [{**profile.__dict__, "created_at_utc": created_at} for profile in profiles],
    )


def fetch_record_token_values(
    con: sqlite3.Connection,
    record_index: int,
    positions: Iterable[int],
) -> dict[str, str | None]:
    values = {token_name(position): None for position in positions}
    fields = list(values.keys())
    placeholders = ",".join("?" for _ in fields)
    rows = con.execute(
        f"""
        SELECT f.field_name, f.raw_value_text
        FROM db21_tim_raw_record r
        JOIN db21_tim_raw_field_value f
            ON f.tim_record_id = r.tim_record_id
        WHERE r.record_index = ?
          AND f.field_name IN ({placeholders})
        ORDER BY f.field_name
        """,
        [record_index] + fields,
    ).fetchall()
    for row in rows:
        values[row["field_name"]] = row["raw_value_text"]
    return values


def build_transition_records(
    con: sqlite3.Connection,
    dominant_signatures: dict[str, str],
) -> list[TransitionGapRecord]:
    records: list[TransitionGapRecord] = []
    for record_index in range(TRANSITION[1], TRANSITION[2] + 1):
        row = con.execute(
            """
            SELECT record_index, line_type, token_count
            FROM db21_tim_raw_record
            WHERE record_index = ?
            """,
            (record_index,),
        ).fetchone()
        if row is None:
            records.append(
                TransitionGapRecord(
                    record_index=record_index,
                    line_exists_flag=0,
                    line_type=None,
                    token_count=None,
                    family_membership_status="absent_from_db",
                    focused_signature_json=compact_json({}),
                    inspected_token_values_json=compact_json({}),
                    matches_block_a_signature_flag=0,
                    matches_block_b_signature_flag=0,
                    transition_gap_relation="absent",
                    status_note="No DB record exists at this record_index.",
                )
            )
            continue
        line_type = row["line_type"]
        token_count = int(row["token_count"])
        family_status = (
            "in_41_data_line_family"
            if line_type == LINE_TYPE and token_count == TOKEN_COUNT
            else "outside_41_data_line_family"
        )
        focused_values = fetch_record_token_values(con, record_index, FOCUSED_SWITCH_POSITIONS)
        inspected_values = fetch_record_token_values(con, record_index, TRANSITION_POSITIONS)
        sig_value = signature_value(focused_values)
        matches_a = int(sig_value == dominant_signatures.get("block_a"))
        matches_b = int(sig_value == dominant_signatures.get("block_b"))
        if family_status == "outside_41_data_line_family":
            relation = "separate_outside_41_family"
            note = "DB record exists but is not a 41-token data_line family row."
        elif matches_a:
            relation = "aligns_with_block_a"
            note = "41-family row matches dominant Block A focused signature."
        elif matches_b:
            relation = "aligns_with_block_b"
            note = "41-family row matches dominant Block B focused signature."
        else:
            relation = "mixed_or_separate"
            note = "41-family row does not match either dominant focused signature."
        records.append(
            TransitionGapRecord(
                record_index=record_index,
                line_exists_flag=1,
                line_type=line_type,
                token_count=token_count,
                family_membership_status=family_status,
                focused_signature_json=compact_json(focused_values),
                inspected_token_values_json=compact_json(inspected_values),
                matches_block_a_signature_flag=matches_a,
                matches_block_b_signature_flag=matches_b,
                transition_gap_relation=relation,
                status_note=note,
            )
        )
    return records


def insert_transition_records(
    con: sqlite3.Connection,
    records: list[TransitionGapRecord],
    created_at: str,
) -> None:
    con.executemany(
        """
        INSERT INTO db23b_transition_gap_inspection (
            record_index,
            line_exists_flag,
            line_type,
            token_count,
            family_membership_status,
            focused_signature_json,
            inspected_token_values_json,
            matches_block_a_signature_flag,
            matches_block_b_signature_flag,
            transition_gap_relation,
            status_note,
            created_at_utc
        )
        VALUES (
            :record_index,
            :line_exists_flag,
            :line_type,
            :token_count,
            :family_membership_status,
            :focused_signature_json,
            :inspected_token_values_json,
            :matches_block_a_signature_flag,
            :matches_block_b_signature_flag,
            :transition_gap_relation,
            :status_note,
            :created_at_utc
        )
        """,
        [{**record.__dict__, "created_at_utc": created_at} for record in records],
    )


def build_pattern_notes(
    definitions: list[BlockDefinition],
    comparisons: list[TokenComparison],
    signatures: list[CombinedSignatureProfile],
    token001_blocks: list[Token001BlockProfile],
    transition_records: list[TransitionGapRecord],
) -> list[dict[str, Any]]:
    definition_by_label = {definition.block_label: definition for definition in definitions}
    switched = [
        comparison.field_name
        for comparison in comparisons
        if comparison.token_position in FOCUSED_SWITCH_POSITIONS
        and comparison.block_discriminating_flag == 1
        and comparison.constant_within_each_block_flag == 1
    ]
    dominant_a = next(
        signature.signature_value
        for signature in signatures
        if signature.block_label == "block_a" and signature.dominant_signature_flag == 1
    )
    dominant_b = next(
        signature.signature_value
        for signature in signatures
        if signature.block_label == "block_b" and signature.dominant_signature_flag == 1
    )
    transition_counts = Counter(record.family_membership_status for record in transition_records)
    token001_status = (
        token001_blocks[0].token001_split_alignment_status
        if token001_blocks
        else "token001_not_available"
    )
    token001_total = (
        token001_blocks[0].token001_total_contiguous_blocks if token001_blocks else 0
    )
    notes = [
        {
            "note_type": "data_substrate",
            "token_position": None,
            "field_name": None,
            "note_text": (
                "DB23B was generated from a copied DB23A database. No raw source "
                "file fallback was used."
            ),
        },
        {
            "note_type": "block_counts",
            "token_position": None,
            "field_name": None,
            "note_text": (
                f"Block A family count={definition_by_label['block_a'].family_record_count}; "
                f"Block B family count={definition_by_label['block_b'].family_record_count}; "
                f"transition family count={definition_by_label['transition_gap'].family_record_count}."
            ),
        },
        {
            "note_type": "focused_tokens_switch_together",
            "token_position": None,
            "field_name": None,
            "note_text": (
                "Focused switch tokens with constant, disjoint Block A/B values: "
                + ", ".join(switched)
                + "."
            ),
        },
        {
            "note_type": "dominant_combined_signatures",
            "token_position": None,
            "field_name": None,
            "note_text": (
                "Dominant focused signature changes between Block A and Block B. "
                f"Block A: {dominant_a}. Block B: {dominant_b}."
            ),
        },
        {
            "note_type": "transition_gap_status",
            "token_position": None,
            "field_name": None,
            "note_text": (
                "Transition/gap records 5134-5143 are DB-present but outside the "
                f"41-token data-line family: {dict(transition_counts)}."
            ),
        },
        {
            "note_type": "token001_context",
            "token_position": TOKEN001_POSITION,
            "field_name": token_name(TOKEN001_POSITION),
            "note_text": (
                f"token_001 forms {token001_total} contiguous value blocks. "
                f"Split alignment status: {token001_status}."
            ),
        },
        {
            "note_type": "low_variance_recurring_context",
            "token_position": None,
            "field_name": None,
            "note_text": (
                "tim_token_025 and tim_token_027 are retained as recurring "
                "low-variance context, not as primary two-block switch tokens."
            ),
        },
        {
            "note_type": "open_mapping_needs",
            "token_position": None,
            "field_name": None,
            "note_text": (
                "All inspected tokens remain needs_mapping before semantic or "
                "analytical use."
            ),
        },
    ]
    return notes


def insert_pattern_notes(
    con: sqlite3.Connection,
    notes: list[dict[str, Any]],
    created_at: str,
) -> None:
    con.executemany(
        """
        INSERT INTO db23b_two_block_pattern_note (
            note_type,
            token_position,
            field_name,
            note_text,
            claim_boundary,
            created_at_utc
        )
        VALUES (
            :note_type,
            :token_position,
            :field_name,
            :note_text,
            :claim_boundary,
            :created_at_utc
        )
        """,
        [
            {
                **note,
                "claim_boundary": CLAIM_BOUNDARY,
                "created_at_utc": created_at,
            }
            for note in notes
        ],
    )


def fetch_dicts(con: sqlite3.Connection, sql: str) -> list[dict[str, Any]]:
    return [dict(row) for row in con.execute(sql).fetchall()]


def write_csv(path: Path, rows: list[dict[str, Any]], fieldnames: list[str]) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow({field: row.get(field) for field in fieldnames})


def table_count(con: sqlite3.Connection, table_name: str) -> int:
    return int(con.execute(f"SELECT COUNT(*) AS n FROM {table_name}").fetchone()["n"])


def write_outputs(
    con: sqlite3.Connection,
    input_db: Path,
    output_root: Path,
    output_db: Path,
    created_at: str,
) -> dict[str, Any]:
    comparison_rows = fetch_dicts(
        con,
        """
        SELECT *
        FROM qsb_v_db23b_token_block_comparison
        ORDER BY token_position
        """,
    )
    side_by_side_rows = fetch_dicts(
        con,
        """
        SELECT *
        FROM qsb_v_db23b_focused_token_side_by_side
        ORDER BY token_position
        """,
    )
    signature_rows = fetch_dicts(
        con,
        """
        SELECT *
        FROM qsb_v_db23b_combined_signature_profile
        ORDER BY signature_scope, block_label, signature_rank
        """,
    )
    token001_rows = fetch_dicts(
        con,
        """
        SELECT *
        FROM qsb_v_db23b_token001_block_profile
        ORDER BY token001_block_rank
        """,
    )
    transition_rows = fetch_dicts(
        con,
        """
        SELECT *
        FROM qsb_v_db23b_transition_gap_inspection
        ORDER BY record_index
        """,
    )
    pattern_note_rows = fetch_dicts(
        con,
        """
        SELECT
            note_type,
            token_position,
            field_name,
            note_text,
            claim_boundary,
            created_at_utc
        FROM db23b_two_block_pattern_note
        ORDER BY pattern_note_id
        """,
    )
    block_rows = fetch_dicts(con, "SELECT * FROM qsb_v_db23b_block_definitions")
    whisper_rows = fetch_dicts(con, "SELECT * FROM qsb_v_db23b_first_two_block_whisper")
    fk_violations = [dict(row) for row in con.execute("PRAGMA foreign_key_check")]

    write_csv(
        output_root / "db23b_token_block_comparison.csv",
        comparison_rows,
        list(comparison_rows[0].keys()) if comparison_rows else [],
    )
    write_csv(
        output_root / "db23b_focused_token_side_by_side.csv",
        side_by_side_rows,
        list(side_by_side_rows[0].keys()) if side_by_side_rows else [],
    )
    write_csv(
        output_root / "db23b_combined_signature_profile.csv",
        signature_rows,
        list(signature_rows[0].keys()) if signature_rows else [],
    )
    write_csv(
        output_root / "db23b_token001_block_profile.csv",
        token001_rows,
        list(token001_rows[0].keys()) if token001_rows else [],
    )
    write_csv(
        output_root / "db23b_transition_gap_inspection.csv",
        transition_rows,
        list(transition_rows[0].keys()) if transition_rows else [],
    )
    write_csv(
        output_root / "db23b_pattern_notes.csv",
        pattern_note_rows,
        list(pattern_note_rows[0].keys()) if pattern_note_rows else [],
    )

    table_counts = {
        table_name: table_count(con, table_name)
        for table_name in [
            "db23b_block_definition",
            "db23b_token_block_value_profile",
            "db23b_token_block_comparison",
            "db23b_combined_signature_profile",
            "db23b_token001_block_profile",
            "db23b_transition_gap_inspection",
            "db23b_two_block_pattern_note",
        ]
    }
    block_by_label = {row["block_label"]: row for row in block_rows}
    switched_tokens = [
        row["field_name"]
        for row in comparison_rows
        if row["token_position"] in FOCUSED_SWITCH_POSITIONS
        and row["block_discriminating_flag"] == 1
        and row["constant_within_each_block_flag"] == 1
    ]
    block_a_signature = next(
        (
            row["signature_value"]
            for row in signature_rows
            if row["block_label"] == "block_a" and row["dominant_signature_flag"] == 1
        ),
        None,
    )
    block_b_signature = next(
        (
            row["signature_value"]
            for row in signature_rows
            if row["block_label"] == "block_b" and row["dominant_signature_flag"] == 1
        ),
        None,
    )
    token001_status = token001_rows[0]["token001_split_alignment_status"] if token001_rows else None
    transition_status_counts = Counter(row["transition_gap_relation"] for row in transition_rows)

    summary = {
        "block": BLOCK_LABEL,
        "created_at_utc": created_at,
        "input_db": str(input_db),
        "output_db": str(output_db),
        "output_root": str(output_root),
        "data_substrate_used": "DB23A copied into DB23B; DB tables in the copy queried.",
        "db23a_copied_to_db23b": True,
        "db23a_modified_in_place": False,
        "raw_file_fallback_used": False,
        "block_a_family_record_count": block_by_label["block_a"]["family_record_count"],
        "block_b_family_record_count": block_by_label["block_b"]["family_record_count"],
        "transition_gap_family_record_count": block_by_label["transition_gap"]["family_record_count"],
        "transition_gap_db_record_count": block_by_label["transition_gap"]["db_record_count"],
        "focused_tokens_that_switch_together": switched_tokens,
        "dominant_block_a_signature": block_a_signature,
        "dominant_block_b_signature": block_b_signature,
        "dominant_signature_changes_at_split": block_a_signature != block_b_signature,
        "token001_block_count": token001_rows[0]["token001_total_contiguous_blocks"]
        if token001_rows
        else 0,
        "token001_split_alignment_status": token001_status,
        "transition_gap_status_counts": dict(transition_status_counts),
        "table_counts": table_counts,
        "foreign_key_violation_count": len(fk_violations),
        "first_two_block_whisper": whisper_rows,
        "claim_boundary": CLAIM_BOUNDARY,
    }
    with (output_root / "db23b_two_block_signature_summary.json").open(
        "w",
        encoding="utf-8",
    ) as handle:
        json.dump(summary, handle, indent=2, ensure_ascii=True)
        handle.write("\n")

    readout_lines = [
        "# QSB-DB23B Two-Block Signature Inspection",
        "",
        "## Data substrate used",
        "",
        f"- Input DB: `{input_db}`",
        f"- Output DB: `{output_db}`",
        "- DB23A was copied before DB23B tables/views were written.",
        "- Raw TIM/PAR files were not read.",
        "- Raw file fallback used: no.",
        "",
        "## Claim boundary",
        "",
        CLAIM_BOUNDARY,
        "",
        "## Block definitions",
        "",
        f"- Block A: records `3-5133`, 41-family count `{summary['block_a_family_record_count']}`",
        f"- Block B: records `5144-10939`, 41-family count `{summary['block_b_family_record_count']}`",
        f"- Transition/gap: records `5134-5143`, DB record count `{summary['transition_gap_db_record_count']}`, 41-family count `{summary['transition_gap_family_record_count']}`",
        "",
        "## Structural switch tokens",
        "",
        "- Focused tokens switching together: " + ", ".join(switched_tokens),
        "",
        "## Dominant combined signatures",
        "",
        f"- Block A: `{block_a_signature}`",
        f"- Block B: `{block_b_signature}`",
        f"- Dominant signature changes at split: `{summary['dominant_signature_changes_at_split']}`",
        "",
        "## token_001 block context",
        "",
        f"- token_001 contiguous block count: `{summary['token001_block_count']}`",
        f"- split alignment status: `{token001_status}`",
        "",
        "## Transition/gap zone",
        "",
        "- Records `5134-5143` are DB-present but outside the 41-token data-line family.",
        f"- Transition relation counts: `{dict(transition_status_counts)}`",
        "",
        "## First two-block whisper",
        "",
        "```json",
        pretty_json(whisper_rows),
        "```",
        "",
        "## Open mapping needs",
        "",
        "All inspected token positions remain `needs_mapping` before semantic or analytical use.",
        "",
        "## Foreign key check",
        "",
        f"- PRAGMA foreign_key_check violation count: `{len(fk_violations)}`",
        "",
    ]
    (output_root / "db23b_two_block_signature_readout.md").write_text(
        "\n".join(readout_lines),
        encoding="utf-8",
    )
    return summary


def populate_db23b(
    con: sqlite3.Connection,
    input_db: Path,
    output_root: Path,
    output_db: Path,
    created_at: str,
) -> dict[str, Any]:
    create_tables(con)
    family_records = fetch_family_records(con)
    definitions = build_block_definitions(con, family_records)
    insert_block_definitions(con, definitions, created_at)

    values_by_position = fetch_token_values(con, INSPECTED_POSITIONS, family_only=True)
    token_block_profiles = build_token_block_profiles(family_records, values_by_position)
    insert_token_block_profiles(con, token_block_profiles, created_at)
    comparisons = build_token_comparisons(con, token_block_profiles)
    insert_token_comparisons(con, comparisons, created_at)

    combined_signatures, dominant_signatures = build_combined_signatures(
        family_records,
        values_by_position,
    )
    insert_combined_signatures(con, combined_signatures, created_at)

    token001_blocks = build_token001_blocks(family_records, values_by_position)
    insert_token001_blocks(con, token001_blocks, created_at)

    transition_records = build_transition_records(con, dominant_signatures)
    insert_transition_records(con, transition_records, created_at)

    pattern_notes = build_pattern_notes(
        definitions,
        comparisons,
        combined_signatures,
        token001_blocks,
        transition_records,
    )
    insert_pattern_notes(con, pattern_notes, created_at)
    create_views(con)
    con.commit()
    return write_outputs(con, input_db, output_root, output_db, created_at)


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Build QSB-DB23B, a conservative DB-backed two-block signature "
            "inspection from the DB23A 41-token family substrate."
        )
    )
    parser.add_argument(
        "--input-db",
        type=Path,
        default=DEFAULT_INPUT_DB,
        help="Path to DB23A 41-token family inspection database.",
    )
    parser.add_argument(
        "--output-root",
        type=Path,
        default=DEFAULT_OUTPUT_ROOT,
        help="Directory for DB23B outputs.",
    )
    parser.add_argument(
        "--output-db",
        type=Path,
        default=DEFAULT_OUTPUT_DB,
        help="Path to DB23B output database.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Validate paths and report intended action without writing outputs.",
    )
    return parser.parse_args(argv)


def main(argv: list[str]) -> int:
    args = parse_args(argv)
    input_db = args.input_db
    output_root = args.output_root
    output_db = args.output_db

    ensure_input_db(input_db)
    ensure_safe_outputs(output_root, output_db)

    if args.dry_run:
        print(f"block: {BLOCK_LABEL}")
        print(f"input_db: {input_db}")
        print(f"output_root: {output_root}")
        print(f"output_db: {output_db}")
        print("dry_run: true")
        print("raw_file_fallback_used: no")
        print(f"claim_boundary: {CLAIM_BOUNDARY}")
        return 0

    created_at = utc_now()
    copy_input_db(input_db, output_root, output_db)
    with connect_db(output_db) as con:
        summary = populate_db23b(con, input_db, output_root, output_db, created_at)

    print(f"block: {BLOCK_LABEL}")
    print(f"input_db: {input_db}")
    print(f"output_db: {output_db}")
    print(f"block_a_family_record_count: {summary['block_a_family_record_count']}")
    print(f"block_b_family_record_count: {summary['block_b_family_record_count']}")
    print(
        "transition_gap_family_record_count: "
        f"{summary['transition_gap_family_record_count']}"
    )
    print(
        "focused_tokens_that_switch_together: "
        + ",".join(summary["focused_tokens_that_switch_together"])
    )
    print(f"token001_block_count: {summary['token001_block_count']}")
    print(f"foreign_key_violation_count: {summary['foreign_key_violation_count']}")
    print("raw_file_fallback_used: no")
    print(f"claim_boundary: {CLAIM_BOUNDARY}")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main(sys.argv[1:]))
    except Exception as exc:
        print(f"error: {exc}", file=sys.stderr)
        raise SystemExit(1)
