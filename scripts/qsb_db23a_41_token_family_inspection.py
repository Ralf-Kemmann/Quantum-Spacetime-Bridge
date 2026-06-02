#!/usr/bin/env python3
"""QSB-DB23A: conservative 41-token TIM data-line family inspection.

This script is DB-first. It copies DB22 into a DB23A output database and
derives structural staging profiles only from tables/views already present in
DB22. It does not read raw TIM/PAR files, does not assign physical meaning to
TIM token positions, and does not compute TOAs, residuals, delays, timing-model
quantities, statistical inference, Shapiro confirmation, QSB validation, Bridge
evidence, or physical interpretation.
"""

from __future__ import annotations

import argparse
import csv
import json
import re
import shutil
import sqlite3
import sys
from collections import Counter, defaultdict
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable


BLOCK_LABEL = "QSB-DB23A_41_TOKEN_FAMILY_INSPECTION"
DEFAULT_INPUT_DB = Path(
    "runs/QSB-DB/QSB_DB22_TIM_STRUCTURE_PROFILING/"
    "qsb_research_tim_structure_profile.db"
)
DEFAULT_OUTPUT_ROOT = Path("runs/QSB-DB/QSB_DB23A_41_TOKEN_FAMILY_INSPECTION")
DEFAULT_OUTPUT_DB = DEFAULT_OUTPUT_ROOT / "qsb_research_41_token_family_inspection.db"

LINE_TYPE = "data_line"
TOKEN_COUNT = 41
FAMILY_KEY = "data_line_token_count_41"

CLAIM_BOUNDARY = (
    "DB23A is a conservative structural inspection of the 41-token TIM "
    "data-line family based only on DB22 database content. It does not assign "
    "physical meaning to TIM columns, compute TOAs, residuals, delays, physical "
    "timing parameters, model quantities, or statistical inference. It does "
    "not make Shapiro confirmation, QSB validation, Bridge evidence, or "
    "physical interpretation claims."
)

NUMERIC_RE = re.compile(
    r"^[+-]?(?:"
    r"(?:\d+(?:\.\d*)?)|"
    r"(?:\.\d+)"
    r")(?:[eE][+-]?\d+)?$"
)
TOKEN_FIELD_RE = re.compile(r"^tim_token_(\d{3})$")


@dataclass(frozen=True)
class FamilyRecord:
    tim_record_id: str
    record_index: int
    line_number: int
    source_file_name: str
    source_family_label: str
    source_path: str


@dataclass
class TokenProfile:
    token_position: int
    field_name: str
    present_count: int
    coverage_fraction: float
    distinct_value_count: int
    example_values: str
    numeric_like_count: int
    text_like_count: int
    constant_or_low_variance_flag: str
    high_variance_flag: int
    empty_or_missing_count: int
    structural_label: str
    needs_mapping_flag: int
    top_value: str | None
    top_value_count: int
    top_value_fraction: float
    contiguous_group_fraction: float
    distinct_contiguous_group_count: int
    distinct_noncontiguous_group_count: int
    profile_note: str


@dataclass
class ValueFrequency:
    token_position: int
    field_name: str
    raw_value_text: str
    value_rank: int
    value_count: int
    value_fraction: float
    first_record_index: int
    last_record_index: int
    family_sequence_segment_count: int
    contiguous_block_flag: int


@dataclass
class CandidateToken:
    token_position: int
    field_name: str
    candidate_label: str
    signal_sources: str
    distinct_value_count: int
    top_values: str
    top_value_fraction: float
    contiguous_group_fraction: float
    candidate_strength: str
    needs_mapping_flag: int
    evidence_note: str


@dataclass
class RecordBlock:
    token_position: int
    grouping_token: str
    group_value: str
    first_record_index: int
    last_record_index: int
    record_count: int
    family_sequence_segment_count: int
    contiguous_block_flag: int
    block_note: str


def utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def is_numeric_like(value: str) -> bool:
    return bool(NUMERIC_RE.match(value.strip()))


def token_position_from_field_name(field_name: str) -> int | None:
    match = TOKEN_FIELD_RE.match(field_name)
    if not match:
        return None
    return int(match.group(1))


def compact_json(values: Any) -> str:
    return json.dumps(values, ensure_ascii=True, separators=(",", ":"))


def ensure_input_db(path: Path) -> None:
    if not path.exists():
        raise FileNotFoundError(f"Input DB does not exist: {path}")
    if not path.is_file():
        raise ValueError(f"Input DB path is not a file: {path}")


def ensure_safe_outputs(output_root: Path, output_db: Path) -> None:
    artifacts = [
        output_db,
        output_root / "db23a_41_token_family_readout.md",
        output_root / "db23a_41_token_family_summary.json",
        output_root / "db23a_41_token_position_profile.csv",
        output_root / "db23a_41_token_value_frequency.csv",
        output_root / "db23a_41_candidate_grouping_tokens.csv",
        output_root / "db23a_41_record_blocks.csv",
        output_root / "db23a_41_pattern_notes.csv",
    ]
    existing = [str(path) for path in artifacts if path.exists()]
    if existing:
        raise FileExistsError(
            "Refusing to overwrite existing DB23A artifact(s): "
            + "; ".join(existing)
        )


def connect_db(path: Path) -> sqlite3.Connection:
    con = sqlite3.connect(path)
    con.row_factory = sqlite3.Row
    con.execute("PRAGMA foreign_keys = ON")
    return con


def query_one(con: sqlite3.Connection, sql: str, params: Iterable[Any] = ()) -> sqlite3.Row:
    row = con.execute(sql, tuple(params)).fetchone()
    if row is None:
        raise RuntimeError(f"Expected one row, got none for query: {sql}")
    return row


def create_db23a_tables(con: sqlite3.Connection) -> None:
    con.executescript(
        """
        CREATE TABLE db23a_41_family_overview (
            family_key TEXT PRIMARY KEY,
            line_type TEXT NOT NULL,
            token_count INTEGER NOT NULL,
            record_count INTEGER NOT NULL,
            field_value_count INTEGER NOT NULL,
            token_field_value_count INTEGER NOT NULL,
            first_record_index INTEGER NOT NULL,
            last_record_index INTEGER NOT NULL,
            first_line_number INTEGER NOT NULL,
            last_line_number INTEGER NOT NULL,
            source_file_name TEXT NOT NULL,
            source_family_label TEXT NOT NULL,
            source_path TEXT NOT NULL,
            source_file_count INTEGER NOT NULL,
            source_family_count INTEGER NOT NULL,
            distinct_token_count_values INTEGER NOT NULL,
            min_token_count INTEGER NOT NULL,
            max_token_count INTEGER NOT NULL,
            records_with_41_token_fields INTEGER NOT NULL,
            records_with_non41_token_fields INTEGER NOT NULL,
            token_count_consistency TEXT NOT NULL,
            data_substrate_used TEXT NOT NULL,
            raw_file_fallback_used TEXT NOT NULL,
            claim_boundary TEXT NOT NULL,
            created_at_utc TEXT NOT NULL
        );

        CREATE TABLE db23a_41_token_position_profile (
            token_position INTEGER PRIMARY KEY,
            family_key TEXT NOT NULL,
            field_name TEXT NOT NULL,
            present_count INTEGER NOT NULL,
            coverage_fraction REAL NOT NULL,
            distinct_value_count INTEGER NOT NULL,
            example_values TEXT NOT NULL,
            numeric_like_count INTEGER NOT NULL,
            text_like_count INTEGER NOT NULL,
            constant_or_low_variance_flag TEXT NOT NULL,
            high_variance_flag INTEGER NOT NULL CHECK (high_variance_flag IN (0, 1)),
            empty_or_missing_count INTEGER NOT NULL,
            structural_label TEXT NOT NULL,
            needs_mapping_flag INTEGER NOT NULL CHECK (needs_mapping_flag IN (0, 1)),
            top_value TEXT,
            top_value_count INTEGER NOT NULL,
            top_value_fraction REAL NOT NULL,
            contiguous_group_fraction REAL NOT NULL,
            distinct_contiguous_group_count INTEGER NOT NULL,
            distinct_noncontiguous_group_count INTEGER NOT NULL,
            profile_note TEXT NOT NULL,
            created_at_utc TEXT NOT NULL,
            FOREIGN KEY (family_key)
                REFERENCES db23a_41_family_overview(family_key)
        );

        CREATE TABLE db23a_41_token_value_frequency (
            token_value_frequency_id INTEGER PRIMARY KEY,
            token_position INTEGER NOT NULL,
            field_name TEXT NOT NULL,
            raw_value_text TEXT NOT NULL,
            value_rank INTEGER NOT NULL,
            value_count INTEGER NOT NULL,
            value_fraction REAL NOT NULL,
            first_record_index INTEGER NOT NULL,
            last_record_index INTEGER NOT NULL,
            family_sequence_segment_count INTEGER NOT NULL,
            contiguous_block_flag INTEGER NOT NULL CHECK (contiguous_block_flag IN (0, 1)),
            created_at_utc TEXT NOT NULL,
            UNIQUE (token_position, value_rank),
            FOREIGN KEY (token_position)
                REFERENCES db23a_41_token_position_profile(token_position)
        );

        CREATE TABLE db23a_41_candidate_grouping_token (
            candidate_grouping_token_id INTEGER PRIMARY KEY,
            token_position INTEGER NOT NULL,
            field_name TEXT NOT NULL,
            candidate_label TEXT NOT NULL,
            signal_sources TEXT NOT NULL,
            distinct_value_count INTEGER NOT NULL,
            top_values TEXT NOT NULL,
            top_value_fraction REAL NOT NULL,
            contiguous_group_fraction REAL NOT NULL,
            candidate_strength TEXT NOT NULL,
            needs_mapping_flag INTEGER NOT NULL CHECK (needs_mapping_flag IN (0, 1)),
            evidence_note TEXT NOT NULL,
            created_at_utc TEXT NOT NULL,
            UNIQUE (token_position, candidate_label),
            FOREIGN KEY (token_position)
                REFERENCES db23a_41_token_position_profile(token_position)
        );

        CREATE TABLE db23a_41_record_block_profile (
            record_block_profile_id INTEGER PRIMARY KEY,
            token_position INTEGER NOT NULL,
            grouping_token TEXT NOT NULL,
            group_value TEXT NOT NULL,
            first_record_index INTEGER NOT NULL,
            last_record_index INTEGER NOT NULL,
            record_count INTEGER NOT NULL,
            family_sequence_segment_count INTEGER NOT NULL,
            contiguous_block_flag INTEGER NOT NULL CHECK (contiguous_block_flag IN (0, 1)),
            block_note TEXT NOT NULL,
            created_at_utc TEXT NOT NULL,
            FOREIGN KEY (token_position)
                REFERENCES db23a_41_token_position_profile(token_position)
        );

        CREATE TABLE db23a_41_pattern_note (
            pattern_note_id INTEGER PRIMARY KEY,
            family_key TEXT NOT NULL,
            note_type TEXT NOT NULL,
            token_position INTEGER,
            field_name TEXT,
            note_text TEXT NOT NULL,
            claim_boundary TEXT NOT NULL,
            created_at_utc TEXT NOT NULL,
            FOREIGN KEY (family_key)
                REFERENCES db23a_41_family_overview(family_key),
            FOREIGN KEY (token_position)
                REFERENCES db23a_41_token_position_profile(token_position)
        );
        """
    )


def create_db23a_views(con: sqlite3.Connection) -> None:
    con.executescript(
        """
        CREATE VIEW qsb_v_db23a_41_family_overview AS
        SELECT
            family_key,
            line_type,
            token_count,
            record_count,
            field_value_count,
            token_field_value_count,
            first_record_index,
            last_record_index,
            source_file_name,
            source_family_label,
            source_file_count,
            source_family_count,
            token_count_consistency,
            data_substrate_used,
            raw_file_fallback_used,
            claim_boundary
        FROM db23a_41_family_overview;

        CREATE VIEW qsb_v_db23a_41_token_position_profile AS
        SELECT
            token_position,
            field_name,
            present_count,
            coverage_fraction,
            distinct_value_count,
            example_values,
            numeric_like_count,
            text_like_count,
            constant_or_low_variance_flag,
            high_variance_flag,
            empty_or_missing_count,
            structural_label,
            needs_mapping_flag,
            top_value,
            top_value_count,
            top_value_fraction,
            contiguous_group_fraction,
            profile_note
        FROM db23a_41_token_position_profile
        ORDER BY token_position;

        CREATE VIEW qsb_v_db23a_41_top_repeated_values AS
        SELECT
            token_position,
            field_name,
            value_rank,
            raw_value_text,
            value_count,
            value_fraction,
            first_record_index,
            last_record_index,
            family_sequence_segment_count,
            contiguous_block_flag
        FROM db23a_41_token_value_frequency
        ORDER BY token_position, value_rank;

        CREATE VIEW qsb_v_db23a_41_candidate_grouping_tokens AS
        SELECT
            token_position,
            field_name,
            candidate_label,
            signal_sources,
            distinct_value_count,
            top_values,
            top_value_fraction,
            contiguous_group_fraction,
            candidate_strength,
            needs_mapping_flag,
            evidence_note
        FROM db23a_41_candidate_grouping_token
        ORDER BY
            CASE candidate_label
                WHEN 'candidate_grouping_token' THEN 0
                WHEN 'candidate_block_marker' THEN 1
                ELSE 2
            END,
            token_position;

        CREATE VIEW qsb_v_db23a_41_record_blocks AS
        SELECT
            token_position,
            grouping_token,
            group_value,
            first_record_index,
            last_record_index,
            record_count,
            family_sequence_segment_count,
            contiguous_block_flag,
            block_note
        FROM db23a_41_record_block_profile
        ORDER BY token_position, first_record_index, group_value;

        CREATE VIEW qsb_v_db23a_41_first_family_whisper AS
        SELECT
            o.family_key,
            o.record_count AS family_record_count,
            (
                SELECT group_concat(
                    field_name || '@' || token_position || '=' ||
                    structural_label || '/distinct=' || distinct_value_count,
                    '; '
                )
                FROM (
                    SELECT field_name, token_position, structural_label,
                           distinct_value_count
                    FROM db23a_41_token_position_profile
                    ORDER BY distinct_value_count ASC, token_position ASC
                    LIMIT 12
                )
            ) AS most_stable_token_positions,
            (
                SELECT group_concat(
                    field_name || '@' || token_position || '=' ||
                    structural_label || '/distinct=' || distinct_value_count,
                    '; '
                )
                FROM (
                    SELECT field_name, token_position, structural_label,
                           distinct_value_count
                    FROM db23a_41_token_position_profile
                    ORDER BY distinct_value_count DESC, token_position ASC
                    LIMIT 8
                )
            ) AS most_variable_token_positions,
            (
                SELECT group_concat(
                    field_name || '@' || token_position || '=' ||
                    candidate_label || '[' || signal_sources || ']',
                    '; '
                )
                FROM (
                    SELECT field_name, token_position, candidate_label,
                           signal_sources
                    FROM db23a_41_candidate_grouping_token
                    WHERE candidate_label = 'candidate_grouping_token'
                    ORDER BY candidate_strength DESC,
                             contiguous_group_fraction DESC,
                             distinct_value_count ASC,
                             token_position ASC
                    LIMIT 12
                )
            ) AS candidate_grouping_tokens,
            (
                SELECT group_concat(
                    grouping_token || ':' || group_value ||
                    '[' || first_record_index || '-' || last_record_index ||
                    ',n=' || record_count || ',segments=' ||
                    family_sequence_segment_count || ']',
                    '; '
                )
                FROM (
                    SELECT grouping_token, group_value, first_record_index,
                           last_record_index, record_count,
                           family_sequence_segment_count
                    FROM db23a_41_record_block_profile
                    WHERE contiguous_block_flag = 1
                    ORDER BY record_count DESC, token_position ASC,
                             first_record_index ASC
                    LIMIT 12
                )
            ) AS visible_block_patterns,
            (
                SELECT group_concat(
                    field_name || '@' || token_position || ':' ||
                    structural_label,
                    '; '
                )
                FROM (
                    SELECT field_name, token_position, structural_label
                    FROM db23a_41_token_position_profile
                    WHERE needs_mapping_flag = 1
                    ORDER BY high_variance_flag DESC,
                             distinct_value_count DESC,
                             token_position ASC
                    LIMIT 12
                )
            ) AS open_mapping_needs,
            o.token_count_consistency,
            o.raw_file_fallback_used,
            o.claim_boundary
        FROM db23a_41_family_overview o
        WHERE o.family_key = 'data_line_token_count_41';
        """
    )


def copy_input_db(input_db: Path, output_root: Path, output_db: Path) -> None:
    output_root.mkdir(parents=True, exist_ok=True)
    shutil.copy2(input_db, output_db)


def load_family_records(con: sqlite3.Connection) -> list[FamilyRecord]:
    rows = con.execute(
        """
        SELECT
            tim_record_id,
            record_index,
            line_number,
            source_file_name,
            source_family_label,
            source_path
        FROM db21_tim_raw_record
        WHERE line_type = ? AND token_count = ?
        ORDER BY record_index
        """,
        (LINE_TYPE, TOKEN_COUNT),
    ).fetchall()
    if not rows:
        raise RuntimeError("No 41-token data_line records found in DB22 substrate.")
    return [
        FamilyRecord(
            tim_record_id=row["tim_record_id"],
            record_index=int(row["record_index"]),
            line_number=int(row["line_number"]),
            source_file_name=row["source_file_name"],
            source_family_label=row["source_family_label"],
            source_path=row["source_path"],
        )
        for row in rows
    ]


def insert_family_overview(
    con: sqlite3.Connection,
    family_records: list[FamilyRecord],
    created_at: str,
) -> dict[str, Any]:
    record_count = len(family_records)
    first_record = family_records[0]
    last_record = family_records[-1]

    field_value_count = int(
        query_one(
            con,
            """
            SELECT COUNT(*) AS n
            FROM db21_tim_raw_field_value f
            JOIN db21_tim_raw_record r
                ON r.tim_record_id = f.tim_record_id
            WHERE r.line_type = ? AND r.token_count = ?
            """,
            (LINE_TYPE, TOKEN_COUNT),
        )["n"]
    )
    token_field_value_count = int(
        query_one(
            con,
            """
            SELECT COUNT(*) AS n
            FROM db21_tim_raw_field_value f
            JOIN db21_tim_raw_record r
                ON r.tim_record_id = f.tim_record_id
            WHERE r.line_type = ?
              AND r.token_count = ?
              AND f.field_name LIKE 'tim_token_%'
            """,
            (LINE_TYPE, TOKEN_COUNT),
        )["n"]
    )
    token_count_row = query_one(
        con,
        """
        SELECT
            COUNT(DISTINCT token_count) AS distinct_token_count_values,
            MIN(token_count) AS min_token_count,
            MAX(token_count) AS max_token_count
        FROM db21_tim_raw_record
        WHERE line_type = ? AND token_count = ?
        """,
        (LINE_TYPE, TOKEN_COUNT),
    )

    per_record_token_counts = con.execute(
        """
        SELECT
            r.tim_record_id,
            COUNT(f.tim_field_value_id) AS token_field_count
        FROM db21_tim_raw_record r
        LEFT JOIN db21_tim_raw_field_value f
            ON f.tim_record_id = r.tim_record_id
           AND f.field_name LIKE 'tim_token_%'
        WHERE r.line_type = ? AND r.token_count = ?
        GROUP BY r.tim_record_id
        """,
        (LINE_TYPE, TOKEN_COUNT),
    ).fetchall()
    records_with_41_token_fields = sum(
        1 for row in per_record_token_counts if int(row["token_field_count"]) == TOKEN_COUNT
    )
    records_with_non41_token_fields = record_count - records_with_41_token_fields

    source_files = sorted({record.source_file_name for record in family_records})
    source_families = sorted({record.source_family_label for record in family_records})
    source_paths = sorted({record.source_path for record in family_records})

    token_count_consistency = (
        "consistent_41_tokens"
        if (
            int(token_count_row["distinct_token_count_values"]) == 1
            and int(token_count_row["min_token_count"]) == TOKEN_COUNT
            and int(token_count_row["max_token_count"]) == TOKEN_COUNT
            and records_with_non41_token_fields == 0
        )
        else "inconsistent_or_needs_review"
    )

    overview = {
        "family_key": FAMILY_KEY,
        "line_type": LINE_TYPE,
        "token_count": TOKEN_COUNT,
        "record_count": record_count,
        "field_value_count": field_value_count,
        "token_field_value_count": token_field_value_count,
        "first_record_index": first_record.record_index,
        "last_record_index": last_record.record_index,
        "first_line_number": first_record.line_number,
        "last_line_number": last_record.line_number,
        "source_file_name": " | ".join(source_files),
        "source_family_label": " | ".join(source_families),
        "source_path": " | ".join(source_paths),
        "source_file_count": len(source_files),
        "source_family_count": len(source_families),
        "distinct_token_count_values": int(token_count_row["distinct_token_count_values"]),
        "min_token_count": int(token_count_row["min_token_count"]),
        "max_token_count": int(token_count_row["max_token_count"]),
        "records_with_41_token_fields": records_with_41_token_fields,
        "records_with_non41_token_fields": records_with_non41_token_fields,
        "token_count_consistency": token_count_consistency,
        "data_substrate_used": "DB22 copied into DB23A output DB; DB21/DB22 tables inside copy queried.",
        "raw_file_fallback_used": "no",
        "claim_boundary": CLAIM_BOUNDARY,
        "created_at_utc": created_at,
    }
    con.execute(
        """
        INSERT INTO db23a_41_family_overview (
            family_key,
            line_type,
            token_count,
            record_count,
            field_value_count,
            token_field_value_count,
            first_record_index,
            last_record_index,
            first_line_number,
            last_line_number,
            source_file_name,
            source_family_label,
            source_path,
            source_file_count,
            source_family_count,
            distinct_token_count_values,
            min_token_count,
            max_token_count,
            records_with_41_token_fields,
            records_with_non41_token_fields,
            token_count_consistency,
            data_substrate_used,
            raw_file_fallback_used,
            claim_boundary,
            created_at_utc
        )
        VALUES (
            :family_key,
            :line_type,
            :token_count,
            :record_count,
            :field_value_count,
            :token_field_value_count,
            :first_record_index,
            :last_record_index,
            :first_line_number,
            :last_line_number,
            :source_file_name,
            :source_family_label,
            :source_path,
            :source_file_count,
            :source_family_count,
            :distinct_token_count_values,
            :min_token_count,
            :max_token_count,
            :records_with_41_token_fields,
            :records_with_non41_token_fields,
            :token_count_consistency,
            :data_substrate_used,
            :raw_file_fallback_used,
            :claim_boundary,
            :created_at_utc
        )
        """,
        overview,
    )
    return overview


def load_token_values(
    con: sqlite3.Connection,
) -> dict[int, dict[int, str]]:
    values_by_position: dict[int, dict[int, str]] = {
        position: {} for position in range(1, TOKEN_COUNT + 1)
    }
    rows = con.execute(
        """
        SELECT
            f.field_name,
            f.raw_value_text,
            r.record_index
        FROM db21_tim_raw_field_value f
        JOIN db21_tim_raw_record r
            ON r.tim_record_id = f.tim_record_id
        WHERE r.line_type = ?
          AND r.token_count = ?
          AND f.field_name LIKE 'tim_token_%'
        ORDER BY r.record_index, f.field_name
        """,
        (LINE_TYPE, TOKEN_COUNT),
    ).fetchall()
    for row in rows:
        position = token_position_from_field_name(row["field_name"])
        if position is None or position < 1 or position > TOKEN_COUNT:
            continue
        values_by_position[position][int(row["record_index"])] = row["raw_value_text"]
    return values_by_position


def segment_count_for_sequence(sequence_positions: Iterable[int]) -> int:
    ordered = sorted(sequence_positions)
    if not ordered:
        return 0
    segments = 1
    previous = ordered[0]
    for current in ordered[1:]:
        if current != previous + 1:
            segments += 1
        previous = current
    return segments


def build_profiles_and_frequencies(
    family_records: list[FamilyRecord],
    values_by_position: dict[int, dict[int, str]],
    created_at: str,
) -> tuple[list[TokenProfile], list[ValueFrequency], dict[int, dict[str, Any]]]:
    record_count = len(family_records)
    low_variance_threshold = max(2, int(round(record_count * 0.01)))
    high_variance_fraction_threshold = 0.50
    sequence_by_record_index = {
        record.record_index: sequence_index
        for sequence_index, record in enumerate(family_records, start=1)
    }

    profiles: list[TokenProfile] = []
    frequencies: list[ValueFrequency] = []
    block_stats_by_position: dict[int, dict[str, Any]] = {}

    for position in range(1, TOKEN_COUNT + 1):
        field_name = f"tim_token_{position:03d}"
        record_values = values_by_position[position]
        nonempty_items = [
            (record_index, value)
            for record_index, value in record_values.items()
            if value is not None and value != ""
        ]
        present_count = len(nonempty_items)
        empty_or_missing_count = record_count - present_count
        values = [value for _, value in nonempty_items]
        counts = Counter(values)
        distinct_value_count = len(counts)
        coverage_fraction = present_count / record_count if record_count else 0.0
        numeric_like_count = sum(1 for value in values if is_numeric_like(value))
        text_like_count = present_count - numeric_like_count

        example_values: list[str] = []
        seen_examples: set[str] = set()
        for record in family_records:
            value = record_values.get(record.record_index)
            if value is None or value == "" or value in seen_examples:
                continue
            seen_examples.add(value)
            example_values.append(value)
            if len(example_values) >= 5:
                break

        if distinct_value_count <= 1:
            constant_or_low_variance_flag = "constant"
        elif distinct_value_count <= low_variance_threshold:
            constant_or_low_variance_flag = "low_variance"
        else:
            constant_or_low_variance_flag = "variable"

        distinct_fraction = (
            distinct_value_count / present_count if present_count else 0.0
        )
        high_variance_flag = int(distinct_fraction >= high_variance_fraction_threshold)
        mostly_numeric = numeric_like_count >= text_like_count and numeric_like_count > 0
        mostly_text = text_like_count > numeric_like_count

        if constant_or_low_variance_flag in {"constant", "low_variance"} and mostly_text:
            structural_label = "stable_text_token"
        elif constant_or_low_variance_flag in {"constant", "low_variance"} and mostly_numeric:
            structural_label = "stable_numeric_token"
        elif mostly_numeric:
            structural_label = "variable_numeric_token"
        elif mostly_text:
            structural_label = "variable_text_token"
        else:
            structural_label = "needs_mapping"

        seq_positions_by_value: dict[str, list[int]] = defaultdict(list)
        record_indices_by_value: dict[str, list[int]] = defaultdict(list)
        for record_index, value in nonempty_items:
            sequence_index = sequence_by_record_index[record_index]
            seq_positions_by_value[value].append(sequence_index)
            record_indices_by_value[value].append(record_index)

        contiguous_values = 0
        noncontiguous_values = 0
        segment_counts_by_value: dict[str, int] = {}
        for value, seq_positions in seq_positions_by_value.items():
            segments = segment_count_for_sequence(seq_positions)
            segment_counts_by_value[value] = segments
            if segments == 1:
                contiguous_values += 1
            else:
                noncontiguous_values += 1
        contiguous_group_fraction = (
            contiguous_values / distinct_value_count if distinct_value_count else 0.0
        )

        ranked_values = sorted(
            counts.items(),
            key=lambda item: (-item[1], str(item[0])),
        )
        top_value = ranked_values[0][0] if ranked_values else None
        top_value_count = int(ranked_values[0][1]) if ranked_values else 0
        top_value_fraction = (
            top_value_count / record_count if record_count else 0.0
        )

        profile_note = (
            "Structural token profile only; token remains needs_mapping before any "
            "semantic use."
        )

        profiles.append(
            TokenProfile(
                token_position=position,
                field_name=field_name,
                present_count=present_count,
                coverage_fraction=coverage_fraction,
                distinct_value_count=distinct_value_count,
                example_values=compact_json(example_values),
                numeric_like_count=numeric_like_count,
                text_like_count=text_like_count,
                constant_or_low_variance_flag=constant_or_low_variance_flag,
                high_variance_flag=high_variance_flag,
                empty_or_missing_count=empty_or_missing_count,
                structural_label=structural_label,
                needs_mapping_flag=1,
                top_value=top_value,
                top_value_count=top_value_count,
                top_value_fraction=top_value_fraction,
                contiguous_group_fraction=contiguous_group_fraction,
                distinct_contiguous_group_count=contiguous_values,
                distinct_noncontiguous_group_count=noncontiguous_values,
                profile_note=profile_note,
            )
        )

        for value_rank, (value, value_count) in enumerate(ranked_values[:10], start=1):
            record_indices = record_indices_by_value[value]
            segments = segment_counts_by_value[value]
            frequencies.append(
                ValueFrequency(
                    token_position=position,
                    field_name=field_name,
                    raw_value_text=value,
                    value_rank=value_rank,
                    value_count=int(value_count),
                    value_fraction=value_count / record_count if record_count else 0.0,
                    first_record_index=min(record_indices),
                    last_record_index=max(record_indices),
                    family_sequence_segment_count=segments,
                    contiguous_block_flag=int(segments == 1),
                )
            )

        block_stats_by_position[position] = {
            "record_indices_by_value": record_indices_by_value,
            "segment_counts_by_value": segment_counts_by_value,
            "counts": counts,
            "ranked_values": ranked_values,
            "low_variance_threshold": low_variance_threshold,
        }

    return profiles, frequencies, block_stats_by_position


def classify_candidate_strength(
    candidate_label: str,
    signal_sources: list[str],
    profile: TokenProfile,
) -> str:
    if candidate_label == "candidate_grouping_token":
        if (
            "explicit_tim_token_001_check" in signal_sources
            or "record_index_block_signal" in signal_sources
        ):
            return "high_structural_interest"
        if profile.distinct_value_count > 1:
            return "medium_structural_interest"
    if candidate_label == "candidate_block_marker":
        return "layout_marker"
    return "context_structural_interest"


def build_candidates(
    profiles: list[TokenProfile],
    block_stats_by_position: dict[int, dict[str, Any]],
) -> list[CandidateToken]:
    candidates: list[CandidateToken] = []
    for profile in profiles:
        stats = block_stats_by_position[profile.token_position]
        ranked_values: list[tuple[str, int]] = stats["ranked_values"]
        low_variance_threshold = int(stats["low_variance_threshold"])
        top_values = compact_json(
            [
                {
                    "value": value,
                    "count": count,
                    "fraction": count / profile.present_count
                    if profile.present_count
                    else 0.0,
                }
                for value, count in ranked_values[:5]
            ]
        )

        signal_sources: list[str] = []
        candidate_label: str | None = None

        if profile.token_position == 1:
            signal_sources.append("explicit_tim_token_001_check")
            candidate_label = "candidate_grouping_token"

        top_value = profile.top_value or ""
        if (
            profile.structural_label == "stable_text_token"
            and profile.distinct_value_count > 1
        ):
            signal_sources.append("low_variance_text_like_token")
            candidate_label = "candidate_grouping_token"

        if (
            profile.structural_label == "stable_numeric_token"
            and 1 < profile.distinct_value_count <= low_variance_threshold
        ):
            signal_sources.append("low_variance_numeric_token")
            candidate_label = candidate_label or "candidate_grouping_token"

        if (
            profile.structural_label == "stable_text_token"
            and profile.distinct_value_count == 1
            and top_value.startswith("-")
        ):
            signal_sources.append("stable_flag_like_token_position")
            candidate_label = "candidate_block_marker"

        if profile.token_position == 1:
            underscore_count = sum(
                count
                for value, count in ranked_values
                if "_" in str(value)
            )
            if profile.present_count and underscore_count / profile.present_count >= 0.95:
                signal_sources.append("repeated_file_or_prefix_pattern")

        if (
            profile.distinct_value_count > 1
            and profile.distinct_value_count <= 250
            and profile.contiguous_group_fraction >= 0.80
        ):
            signal_sources.append("record_index_block_signal")
            candidate_label = candidate_label or "candidate_grouping_token"

        if not candidate_label:
            continue

        unique_signal_sources = list(dict.fromkeys(signal_sources))
        evidence_note = (
            "Structural grouping/block signal only; no semantic or physical role "
            "assigned."
        )
        candidate_strength = classify_candidate_strength(
            candidate_label,
            unique_signal_sources,
            profile,
        )
        candidates.append(
            CandidateToken(
                token_position=profile.token_position,
                field_name=profile.field_name,
                candidate_label=candidate_label,
                signal_sources=";".join(unique_signal_sources),
                distinct_value_count=profile.distinct_value_count,
                top_values=top_values,
                top_value_fraction=profile.top_value_fraction,
                contiguous_group_fraction=profile.contiguous_group_fraction,
                candidate_strength=candidate_strength,
                needs_mapping_flag=1,
                evidence_note=evidence_note,
            )
        )
    return candidates


def build_record_blocks(
    candidates: list[CandidateToken],
    block_stats_by_position: dict[int, dict[str, Any]],
) -> list[RecordBlock]:
    blocks: list[RecordBlock] = []
    for candidate in candidates:
        stats = block_stats_by_position[candidate.token_position]
        record_indices_by_value: dict[str, list[int]] = stats["record_indices_by_value"]
        segment_counts_by_value: dict[str, int] = stats["segment_counts_by_value"]
        counts: Counter[str] = stats["counts"]

        for value, count in sorted(
            counts.items(),
            key=lambda item: (min(record_indices_by_value[item[0]]), str(item[0])),
        ):
            record_indices = record_indices_by_value[value]
            segment_count = segment_counts_by_value[value]
            contiguous_block_flag = int(segment_count == 1)
            block_note = (
                "Candidate contiguous block in 41-family sequence."
                if contiguous_block_flag
                else "Value recurs in multiple family-sequence segments."
            )
            blocks.append(
                RecordBlock(
                    token_position=candidate.token_position,
                    grouping_token=candidate.field_name,
                    group_value=value,
                    first_record_index=min(record_indices),
                    last_record_index=max(record_indices),
                    record_count=int(count),
                    family_sequence_segment_count=segment_count,
                    contiguous_block_flag=contiguous_block_flag,
                    block_note=block_note,
                )
            )
    return blocks


def insert_profiles(
    con: sqlite3.Connection,
    profiles: list[TokenProfile],
    created_at: str,
) -> None:
    con.executemany(
        """
        INSERT INTO db23a_41_token_position_profile (
            token_position,
            family_key,
            field_name,
            present_count,
            coverage_fraction,
            distinct_value_count,
            example_values,
            numeric_like_count,
            text_like_count,
            constant_or_low_variance_flag,
            high_variance_flag,
            empty_or_missing_count,
            structural_label,
            needs_mapping_flag,
            top_value,
            top_value_count,
            top_value_fraction,
            contiguous_group_fraction,
            distinct_contiguous_group_count,
            distinct_noncontiguous_group_count,
            profile_note,
            created_at_utc
        )
        VALUES (
            :token_position,
            :family_key,
            :field_name,
            :present_count,
            :coverage_fraction,
            :distinct_value_count,
            :example_values,
            :numeric_like_count,
            :text_like_count,
            :constant_or_low_variance_flag,
            :high_variance_flag,
            :empty_or_missing_count,
            :structural_label,
            :needs_mapping_flag,
            :top_value,
            :top_value_count,
            :top_value_fraction,
            :contiguous_group_fraction,
            :distinct_contiguous_group_count,
            :distinct_noncontiguous_group_count,
            :profile_note,
            :created_at_utc
        )
        """,
        [
            {
                **profile.__dict__,
                "family_key": FAMILY_KEY,
                "created_at_utc": created_at,
            }
            for profile in profiles
        ],
    )


def insert_frequencies(
    con: sqlite3.Connection,
    frequencies: list[ValueFrequency],
    created_at: str,
) -> None:
    con.executemany(
        """
        INSERT INTO db23a_41_token_value_frequency (
            token_position,
            field_name,
            raw_value_text,
            value_rank,
            value_count,
            value_fraction,
            first_record_index,
            last_record_index,
            family_sequence_segment_count,
            contiguous_block_flag,
            created_at_utc
        )
        VALUES (
            :token_position,
            :field_name,
            :raw_value_text,
            :value_rank,
            :value_count,
            :value_fraction,
            :first_record_index,
            :last_record_index,
            :family_sequence_segment_count,
            :contiguous_block_flag,
            :created_at_utc
        )
        """,
        [{**frequency.__dict__, "created_at_utc": created_at} for frequency in frequencies],
    )


def insert_candidates(
    con: sqlite3.Connection,
    candidates: list[CandidateToken],
    created_at: str,
) -> None:
    con.executemany(
        """
        INSERT INTO db23a_41_candidate_grouping_token (
            token_position,
            field_name,
            candidate_label,
            signal_sources,
            distinct_value_count,
            top_values,
            top_value_fraction,
            contiguous_group_fraction,
            candidate_strength,
            needs_mapping_flag,
            evidence_note,
            created_at_utc
        )
        VALUES (
            :token_position,
            :field_name,
            :candidate_label,
            :signal_sources,
            :distinct_value_count,
            :top_values,
            :top_value_fraction,
            :contiguous_group_fraction,
            :candidate_strength,
            :needs_mapping_flag,
            :evidence_note,
            :created_at_utc
        )
        """,
        [{**candidate.__dict__, "created_at_utc": created_at} for candidate in candidates],
    )


def insert_blocks(
    con: sqlite3.Connection,
    blocks: list[RecordBlock],
    created_at: str,
) -> None:
    con.executemany(
        """
        INSERT INTO db23a_41_record_block_profile (
            token_position,
            grouping_token,
            group_value,
            first_record_index,
            last_record_index,
            record_count,
            family_sequence_segment_count,
            contiguous_block_flag,
            block_note,
            created_at_utc
        )
        VALUES (
            :token_position,
            :grouping_token,
            :group_value,
            :first_record_index,
            :last_record_index,
            :record_count,
            :family_sequence_segment_count,
            :contiguous_block_flag,
            :block_note,
            :created_at_utc
        )
        """,
        [{**block.__dict__, "created_at_utc": created_at} for block in blocks],
    )


def build_pattern_notes(
    overview: dict[str, Any],
    profiles: list[TokenProfile],
    candidates: list[CandidateToken],
    blocks: list[RecordBlock],
) -> list[dict[str, Any]]:
    profile_by_position = {profile.token_position: profile for profile in profiles}
    stable_positions = [
        profile.token_position
        for profile in profiles
        if profile.constant_or_low_variance_flag == "constant"
    ]
    low_variance_positions = [
        profile.token_position
        for profile in profiles
        if profile.constant_or_low_variance_flag == "low_variance"
    ]
    high_variance_positions = [
        profile.token_position
        for profile in profiles
        if profile.high_variance_flag == 1
    ]
    flag_like_positions = [
        profile.token_position
        for profile in profiles
        if profile.constant_or_low_variance_flag == "constant"
        and (profile.top_value or "").startswith("-")
    ]
    candidate_grouping_positions = [
        candidate.token_position
        for candidate in candidates
        if candidate.candidate_label == "candidate_grouping_token"
    ]
    contiguous_blocks = [block for block in blocks if block.contiguous_block_flag == 1]
    noncontiguous_blocks = [block for block in blocks if block.contiguous_block_flag == 0]

    notes = [
        {
            "note_type": "family_consistency",
            "token_position": None,
            "field_name": None,
            "note_text": (
                f"The inspected family has {overview['record_count']} records, "
                f"{overview['token_field_value_count']} token field values, one "
                f"line type ({overview['line_type']}), and token-count status "
                f"{overview['token_count_consistency']}."
            ),
        },
        {
            "note_type": "stable_positions",
            "token_position": None,
            "field_name": None,
            "note_text": (
                "Constant token positions: "
                + ", ".join(f"tim_token_{pos:03d}" for pos in stable_positions)
                + ". Low-variance token positions: "
                + ", ".join(f"tim_token_{pos:03d}" for pos in low_variance_positions)
                + "."
            ),
        },
        {
            "note_type": "flag_like_marker_pattern",
            "token_position": None,
            "field_name": None,
            "note_text": (
                "Stable hyphen-prefixed text markers appear at positions: "
                + ", ".join(f"tim_token_{pos:03d}" for pos in flag_like_positions)
                + ". These are structural markers only."
            ),
        },
        {
            "note_type": "high_variance_positions",
            "token_position": None,
            "field_name": None,
            "note_text": (
                "High-variance token positions requiring mapping before analytical "
                "use: "
                + ", ".join(f"tim_token_{pos:03d}" for pos in high_variance_positions)
                + "."
            ),
        },
        {
            "note_type": "candidate_grouping_positions",
            "token_position": None,
            "field_name": None,
            "note_text": (
                "Candidate grouping tokens by structural evidence: "
                + ", ".join(
                    f"tim_token_{pos:03d}" for pos in candidate_grouping_positions
                )
                + "."
            ),
        },
        {
            "note_type": "block_pattern_summary",
            "token_position": None,
            "field_name": None,
            "note_text": (
                f"Record-block table contains {len(contiguous_blocks)} contiguous "
                f"value groups and {len(noncontiguous_blocks)} recurring "
                "non-contiguous value groups across candidate marker positions."
            ),
        },
        {
            "note_type": "open_mapping_need",
            "token_position": None,
            "field_name": None,
            "note_text": (
                "All token positions remain needs_mapping before any semantic, "
                "analytical, or physical use."
            ),
        },
    ]
    if 1 in profile_by_position:
        profile = profile_by_position[1]
        notes.append(
            {
                "note_type": "tim_token_001_signal",
                "token_position": 1,
                "field_name": profile.field_name,
                "note_text": (
                    "tim_token_001 has "
                    f"{profile.distinct_value_count} distinct text values and "
                    f"contiguous-group fraction {profile.contiguous_group_fraction:.6f}; "
                    "this is a structural grouping signal only."
                ),
            }
        )
    return notes


def insert_pattern_notes(
    con: sqlite3.Connection,
    notes: list[dict[str, Any]],
    created_at: str,
) -> None:
    con.executemany(
        """
        INSERT INTO db23a_41_pattern_note (
            family_key,
            note_type,
            token_position,
            field_name,
            note_text,
            claim_boundary,
            created_at_utc
        )
        VALUES (
            :family_key,
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
                "family_key": FAMILY_KEY,
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


def summarize_counts(con: sqlite3.Connection) -> dict[str, int]:
    table_names = [
        "db23a_41_family_overview",
        "db23a_41_token_position_profile",
        "db23a_41_token_value_frequency",
        "db23a_41_candidate_grouping_token",
        "db23a_41_record_block_profile",
        "db23a_41_pattern_note",
    ]
    return {
        table_name: int(
            con.execute(f"SELECT COUNT(*) AS n FROM {table_name}").fetchone()["n"]
        )
        for table_name in table_names
    }


def write_outputs(
    con: sqlite3.Connection,
    output_root: Path,
    output_db: Path,
    input_db: Path,
    overview: dict[str, Any],
    created_at: str,
) -> dict[str, Any]:
    profile_rows = fetch_dicts(
        con,
        """
        SELECT
            token_position,
            field_name,
            present_count,
            coverage_fraction,
            distinct_value_count,
            example_values,
            numeric_like_count,
            text_like_count,
            constant_or_low_variance_flag,
            high_variance_flag,
            empty_or_missing_count,
            structural_label,
            needs_mapping_flag,
            top_value,
            top_value_count,
            top_value_fraction,
            contiguous_group_fraction,
            distinct_contiguous_group_count,
            distinct_noncontiguous_group_count,
            profile_note
        FROM db23a_41_token_position_profile
        ORDER BY token_position
        """,
    )
    frequency_rows = fetch_dicts(
        con,
        """
        SELECT
            token_position,
            field_name,
            value_rank,
            raw_value_text,
            value_count,
            value_fraction,
            first_record_index,
            last_record_index,
            family_sequence_segment_count,
            contiguous_block_flag
        FROM db23a_41_token_value_frequency
        ORDER BY token_position, value_rank
        """,
    )
    candidate_rows = fetch_dicts(
        con,
        """
        SELECT
            token_position,
            field_name,
            candidate_label,
            signal_sources,
            distinct_value_count,
            top_values,
            top_value_fraction,
            contiguous_group_fraction,
            candidate_strength,
            needs_mapping_flag,
            evidence_note
        FROM db23a_41_candidate_grouping_token
        ORDER BY token_position, candidate_label
        """,
    )
    block_rows = fetch_dicts(
        con,
        """
        SELECT
            token_position,
            grouping_token,
            group_value,
            first_record_index,
            last_record_index,
            record_count,
            family_sequence_segment_count,
            contiguous_block_flag,
            block_note
        FROM db23a_41_record_block_profile
        ORDER BY token_position, first_record_index, group_value
        """,
    )
    note_rows = fetch_dicts(
        con,
        """
        SELECT
            note_type,
            token_position,
            field_name,
            note_text,
            claim_boundary,
            created_at_utc
        FROM db23a_41_pattern_note
        ORDER BY pattern_note_id
        """,
    )
    whisper_rows = fetch_dicts(
        con,
        "SELECT * FROM qsb_v_db23a_41_first_family_whisper",
    )
    counts = summarize_counts(con)
    fk_violations = [dict(row) for row in con.execute("PRAGMA foreign_key_check")]

    write_csv(
        output_root / "db23a_41_token_position_profile.csv",
        profile_rows,
        [
            "token_position",
            "field_name",
            "present_count",
            "coverage_fraction",
            "distinct_value_count",
            "example_values",
            "numeric_like_count",
            "text_like_count",
            "constant_or_low_variance_flag",
            "high_variance_flag",
            "empty_or_missing_count",
            "structural_label",
            "needs_mapping_flag",
            "top_value",
            "top_value_count",
            "top_value_fraction",
            "contiguous_group_fraction",
            "distinct_contiguous_group_count",
            "distinct_noncontiguous_group_count",
            "profile_note",
        ],
    )
    write_csv(
        output_root / "db23a_41_token_value_frequency.csv",
        frequency_rows,
        [
            "token_position",
            "field_name",
            "value_rank",
            "raw_value_text",
            "value_count",
            "value_fraction",
            "first_record_index",
            "last_record_index",
            "family_sequence_segment_count",
            "contiguous_block_flag",
        ],
    )
    write_csv(
        output_root / "db23a_41_candidate_grouping_tokens.csv",
        candidate_rows,
        [
            "token_position",
            "field_name",
            "candidate_label",
            "signal_sources",
            "distinct_value_count",
            "top_values",
            "top_value_fraction",
            "contiguous_group_fraction",
            "candidate_strength",
            "needs_mapping_flag",
            "evidence_note",
        ],
    )
    write_csv(
        output_root / "db23a_41_record_blocks.csv",
        block_rows,
        [
            "token_position",
            "grouping_token",
            "group_value",
            "first_record_index",
            "last_record_index",
            "record_count",
            "family_sequence_segment_count",
            "contiguous_block_flag",
            "block_note",
        ],
    )
    write_csv(
        output_root / "db23a_41_pattern_notes.csv",
        note_rows,
        [
            "note_type",
            "token_position",
            "field_name",
            "note_text",
            "claim_boundary",
            "created_at_utc",
        ],
    )

    stable_positions = [
        row["field_name"]
        for row in profile_rows
        if row["constant_or_low_variance_flag"] == "constant"
    ]
    low_variance_positions = [
        row["field_name"]
        for row in profile_rows
        if row["constant_or_low_variance_flag"] == "low_variance"
    ]
    high_variance_positions = [
        row["field_name"] for row in profile_rows if row["high_variance_flag"] == 1
    ]
    candidate_grouping_positions = [
        row["field_name"]
        for row in candidate_rows
        if row["candidate_label"] == "candidate_grouping_token"
    ]
    block_marker_positions = [
        row["field_name"]
        for row in candidate_rows
        if row["candidate_label"] == "candidate_block_marker"
    ]

    summary = {
        "block": BLOCK_LABEL,
        "created_at_utc": created_at,
        "input_db": str(input_db),
        "output_db": str(output_db),
        "output_root": str(output_root),
        "data_substrate_used": overview["data_substrate_used"],
        "db22_copied_to_db23a": True,
        "db22_modified_in_place": False,
        "raw_file_fallback_used": False,
        "line_type": LINE_TYPE,
        "token_count": TOKEN_COUNT,
        "family_record_count": overview["record_count"],
        "field_value_count": overview["field_value_count"],
        "token_field_value_count": overview["token_field_value_count"],
        "token_count_consistency": overview["token_count_consistency"],
        "source_file_name": overview["source_file_name"],
        "source_family_label": overview["source_family_label"],
        "table_counts": counts,
        "foreign_key_violation_count": len(fk_violations),
        "stable_token_positions": stable_positions,
        "low_variance_token_positions": low_variance_positions,
        "high_variance_token_positions": high_variance_positions,
        "candidate_grouping_tokens": candidate_grouping_positions,
        "candidate_block_markers": block_marker_positions,
        "first_family_whisper": whisper_rows,
        "claim_boundary": CLAIM_BOUNDARY,
    }
    with (output_root / "db23a_41_token_family_summary.json").open(
        "w",
        encoding="utf-8",
    ) as handle:
        json.dump(summary, handle, indent=2, ensure_ascii=True)
        handle.write("\n")

    readout_lines = [
        "# QSB-DB23A 41-Token Data-Line Family Inspection",
        "",
        "## Data substrate used",
        "",
        f"- Input DB: `{input_db}`",
        f"- Output DB: `{output_db}`",
        "- DB22 was copied before DB23A tables/views were written.",
        "- Raw TIM/PAR files were not read.",
        "- Raw file fallback used: no.",
        "",
        "## Claim boundary",
        "",
        CLAIM_BOUNDARY,
        "",
        "## Family overview",
        "",
        f"- line_type: `{LINE_TYPE}`",
        f"- token_count: `{TOKEN_COUNT}`",
        f"- record_count: `{overview['record_count']}`",
        f"- DB-backed field/value count including raw_line_text: `{overview['field_value_count']}`",
        f"- token field/value count: `{overview['token_field_value_count']}`",
        f"- first_record_index: `{overview['first_record_index']}`",
        f"- last_record_index: `{overview['last_record_index']}`",
        f"- source_file: `{overview['source_file_name']}`",
        f"- source_family: `{overview['source_family_label']}`",
        f"- token_count_consistency: `{overview['token_count_consistency']}`",
        "",
        "## Structural connection",
        "",
        "The family is connected structurally by one DB-backed source family/file, "
        "one line type, a consistent 41-token count, complete token-position "
        "coverage, and repeated positional layout markers. All token positions "
        "remain needs_mapping before semantic or analytical use.",
        "",
        "## Stable and variable positions",
        "",
        "- Constant positions: "
        + ", ".join(stable_positions),
        "- Low-variance positions: "
        + ", ".join(low_variance_positions),
        "- High-variance positions: "
        + ", ".join(high_variance_positions),
        "",
        "## Candidate grouping and block markers",
        "",
        "- Candidate grouping tokens: "
        + ", ".join(candidate_grouping_positions),
        "- Candidate block markers: "
        + ", ".join(block_marker_positions),
        "",
        "## First family whisper",
        "",
        "```json",
        json.dumps(whisper_rows, indent=2, ensure_ascii=True),
        "```",
        "",
        "## Open mapping needs",
        "",
        "All token positions are structural candidates only and remain "
        "`needs_mapping` before semantic, analytical, or physical use.",
        "",
        "## Foreign key check",
        "",
        f"- PRAGMA foreign_key_check violation count: `{len(fk_violations)}`",
        "",
    ]
    (output_root / "db23a_41_token_family_readout.md").write_text(
        "\n".join(readout_lines),
        encoding="utf-8",
    )
    return summary


def populate_db23a(con: sqlite3.Connection, created_at: str) -> dict[str, Any]:
    create_db23a_tables(con)
    family_records = load_family_records(con)
    overview = insert_family_overview(con, family_records, created_at)
    values_by_position = load_token_values(con)
    profiles, frequencies, block_stats_by_position = build_profiles_and_frequencies(
        family_records,
        values_by_position,
        created_at,
    )
    candidates = build_candidates(profiles, block_stats_by_position)
    blocks = build_record_blocks(candidates, block_stats_by_position)
    pattern_notes = build_pattern_notes(overview, profiles, candidates, blocks)

    insert_profiles(con, profiles, created_at)
    insert_frequencies(con, frequencies, created_at)
    insert_candidates(con, candidates, created_at)
    insert_blocks(con, blocks, created_at)
    insert_pattern_notes(con, pattern_notes, created_at)
    create_db23a_views(con)
    con.commit()
    return overview


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Build QSB-DB23A, a conservative DB-backed structural inspection of "
            "the dominant 41-token TIM data_line family from DB22."
        )
    )
    parser.add_argument(
        "--input-db",
        type=Path,
        default=DEFAULT_INPUT_DB,
        help="Path to DB22 TIM structure profiling database.",
    )
    parser.add_argument(
        "--output-root",
        type=Path,
        default=DEFAULT_OUTPUT_ROOT,
        help="Directory for DB23A outputs.",
    )
    parser.add_argument(
        "--output-db",
        type=Path,
        default=DEFAULT_OUTPUT_DB,
        help="Path to DB23A output database.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Validate paths and report the intended action without writing outputs.",
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

    try:
        with connect_db(output_db) as con:
            overview = populate_db23a(con, created_at)
            summary = write_outputs(
                con=con,
                output_root=output_root,
                output_db=output_db,
                input_db=input_db,
                overview=overview,
                created_at=created_at,
            )
    except Exception:
        raise

    print(f"block: {BLOCK_LABEL}")
    print(f"input_db: {input_db}")
    print(f"output_db: {output_db}")
    print(f"family_record_count: {summary['family_record_count']}")
    print(f"token_count_consistency: {summary['token_count_consistency']}")
    print(
        "candidate_grouping_token_count: "
        f"{len(summary['candidate_grouping_tokens'])}"
    )
    print(
        "candidate_block_marker_count: "
        f"{len(summary['candidate_block_markers'])}"
    )
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
