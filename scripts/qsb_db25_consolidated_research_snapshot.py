#!/usr/bin/env python3
"""QSB-DB25: consolidate DB23 staging and DB23B signature branches.

This is a Mini-DWH consolidation step. The script copies the DB23B signature
database as the DB25 base, attaches the DB23 staging-map database in read-only
mode, imports DB23 staging tables/views into DB25, adds consolidation metadata,
and creates report-ready DB25 views. It does not read raw source files and does
not modify either input database.
"""

from __future__ import annotations

import argparse
import csv
import json
import re
import shutil
import sqlite3
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


BLOCK_LABEL = "QSB-DB25_CONSOLIDATED_RESEARCH_SNAPSHOT"
SCRIPT_NAME = "scripts/qsb_db25_consolidated_research_snapshot.py"
DEFAULT_STAGING_DB = Path(
    "runs/QSB-DB/QSB_DB23_TIM_STAGING_FIELD_MAP/"
    "qsb_research_tim_staging_field_map.db"
)
DEFAULT_SIGNATURE_DB = Path(
    "runs/QSB-DB/QSB_DB23B_TWO_BLOCK_SIGNATURE_INSPECTION/"
    "qsb_research_two_block_signature_inspection.db"
)
DEFAULT_OUTPUT_ROOT = Path("runs/QSB-DB/QSB_DB25_CONSOLIDATED_RESEARCH_SNAPSHOT")
DEFAULT_OUTPUT_DB = DEFAULT_OUTPUT_ROOT / "qsb_research_consolidated_snapshot.db"

OUTPUT_FILES = [
    "qsb_research_consolidated_snapshot.db",
    "db25_consolidated_snapshot_readout.md",
    "db25_consolidated_snapshot_summary.json",
    "db25_consolidated_object_inventory.csv",
    "db25_consolidated_table_counts.csv",
    "db25_consolidated_view_inventory.csv",
    "db25_consolidation_map.csv",
]

CLAIM_BOUNDARY = (
    "DB25 is a consolidation snapshot built only from SQLite research DBs. "
    "It does not assign physical meaning to TIM token positions, does not "
    "compute timing quantities, delays, residuals, model quantities, or "
    "statistical tests, and does not make validation or physical-interpretation "
    "claims."
)


@dataclass(frozen=True)
class SourceObject:
    name: str
    object_type: str
    sql: str | None


@dataclass(frozen=True)
class ObjectMapRow:
    source_db_label: str
    source_object_name: str
    source_object_type: str
    target_object_name: str
    target_object_type: str
    import_status: str
    collision_status: str
    notes: str


def utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def compact_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=True, separators=(",", ":"))


def pretty_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=True, indent=2)


def quote_identifier(identifier: str) -> str:
    return '"' + identifier.replace('"', '""') + '"'


def ensure_input_db(path: Path, label: str) -> None:
    if not path.exists():
        raise FileNotFoundError(f"{label} DB does not exist: {path}")
    if not path.is_file():
        raise ValueError(f"{label} DB path is not a file: {path}")


def expected_output_paths(output_root: Path, output_db: Path) -> list[Path]:
    return [
        output_db,
        output_root / "db25_consolidated_snapshot_readout.md",
        output_root / "db25_consolidated_snapshot_summary.json",
        output_root / "db25_consolidated_object_inventory.csv",
        output_root / "db25_consolidated_table_counts.csv",
        output_root / "db25_consolidated_view_inventory.csv",
        output_root / "db25_consolidation_map.csv",
    ]


def ensure_safe_outputs(output_root: Path, output_db: Path) -> None:
    existing = [str(path) for path in expected_output_paths(output_root, output_db) if path.exists()]
    if existing:
        raise FileExistsError(
            "Refusing to overwrite existing DB25 artifact(s): " + "; ".join(existing)
        )


def connect_db(path: Path) -> sqlite3.Connection:
    con = sqlite3.connect(path, uri=True)
    con.row_factory = sqlite3.Row
    con.execute("PRAGMA foreign_keys = ON")
    return con


def connect_readonly(path: Path) -> sqlite3.Connection:
    con = sqlite3.connect(f"file:{path.resolve()}?mode=ro", uri=True)
    con.row_factory = sqlite3.Row
    return con


def attach_readonly(con: sqlite3.Connection, path: Path, alias: str) -> None:
    con.execute(f"ATTACH DATABASE ? AS {quote_identifier(alias)}", (f"file:{path.resolve()}?mode=ro",))


def list_objects(con: sqlite3.Connection, schema: str = "main") -> list[SourceObject]:
    rows = con.execute(
        f"""
        SELECT name, type, sql
        FROM {quote_identifier(schema)}.sqlite_master
        WHERE type IN ('table', 'view')
          AND name NOT LIKE 'sqlite_%'
        ORDER BY type, name
        """
    ).fetchall()
    return [
        SourceObject(name=row["name"], object_type=row["type"], sql=row["sql"])
        for row in rows
    ]


def object_names(con: sqlite3.Connection) -> set[str]:
    return {
        row["name"]
        for row in con.execute(
            """
            SELECT name
            FROM sqlite_master
            WHERE type IN ('table', 'view')
              AND name NOT LIKE 'sqlite_%'
            """
        )
    }


def table_row_count(con: sqlite3.Connection, table_name: str) -> int:
    return int(con.execute(f"SELECT COUNT(*) AS n FROM {quote_identifier(table_name)}").fetchone()["n"])


def fetch_dicts(con: sqlite3.Connection, sql: str, params: tuple[Any, ...] = ()) -> list[dict[str, Any]]:
    return [dict(row) for row in con.execute(sql, params).fetchall()]


def source_object_counts(path: Path) -> tuple[int, int]:
    with connect_readonly(path) as con:
        rows = con.execute(
            """
            SELECT type, COUNT(*) AS n
            FROM sqlite_master
            WHERE type IN ('table', 'view')
              AND name NOT LIKE 'sqlite_%'
            GROUP BY type
            """
        ).fetchall()
    counts = {row["type"]: int(row["n"]) for row in rows}
    return counts.get("table", 0), counts.get("view", 0)


def create_metadata_tables(con: sqlite3.Connection) -> None:
    con.executescript(
        """
        CREATE TABLE db25_consolidation_source_db (
            source_db_label TEXT PRIMARY KEY,
            source_db_path TEXT NOT NULL,
            source_role TEXT NOT NULL,
            source_file_size_bytes INTEGER NOT NULL,
            source_detected_table_count INTEGER NOT NULL,
            source_detected_view_count INTEGER NOT NULL,
            imported_table_count INTEGER NOT NULL,
            imported_view_count INTEGER NOT NULL,
            created_at_utc TEXT NOT NULL
        );

        CREATE TABLE db25_consolidation_object_map (
            object_map_id INTEGER PRIMARY KEY,
            source_db_label TEXT NOT NULL,
            source_object_name TEXT NOT NULL,
            source_object_type TEXT NOT NULL,
            target_object_name TEXT NOT NULL,
            target_object_type TEXT NOT NULL,
            import_status TEXT NOT NULL,
            collision_status TEXT NOT NULL,
            notes TEXT NOT NULL,
            created_at_utc TEXT NOT NULL,
            FOREIGN KEY (source_db_label)
                REFERENCES db25_consolidation_source_db(source_db_label)
        );

        CREATE TABLE db25_consolidation_run_log (
            run_log_id INTEGER PRIMARY KEY,
            event_type TEXT NOT NULL,
            event_key TEXT NOT NULL,
            event_value TEXT NOT NULL,
            event_note TEXT NOT NULL,
            created_at_utc TEXT NOT NULL
        );

        CREATE TABLE db25_result_table_catalog (
            result_catalog_id INTEGER PRIMARY KEY,
            result_object_name TEXT NOT NULL,
            result_object_type TEXT NOT NULL,
            source_stage TEXT NOT NULL,
            purpose TEXT NOT NULL,
            upstream_tables_or_views TEXT NOT NULL,
            created_by_script TEXT NOT NULL,
            created_at_utc TEXT NOT NULL,
            data_substrate TEXT NOT NULL,
            claim_boundary_status TEXT NOT NULL
        );
        """
    )


def insert_source_db_rows(
    con: sqlite3.Connection,
    staging_db: Path,
    signature_db: Path,
    imported_staging_table_count: int,
    imported_staging_view_count: int,
    created_at: str,
) -> None:
    signature_tables, signature_views = source_object_counts(signature_db)
    staging_tables, staging_views = source_object_counts(staging_db)
    rows = [
        {
            "source_db_label": "db23b_signature_branch",
            "source_db_path": str(signature_db),
            "source_role": "base_copy_signature_branch",
            "source_file_size_bytes": signature_db.stat().st_size,
            "source_detected_table_count": signature_tables,
            "source_detected_view_count": signature_views,
            "imported_table_count": signature_tables,
            "imported_view_count": signature_views,
            "created_at_utc": created_at,
        },
        {
            "source_db_label": "db23_staging_branch",
            "source_db_path": str(staging_db),
            "source_role": "attached_readonly_imported_staging_branch",
            "source_file_size_bytes": staging_db.stat().st_size,
            "source_detected_table_count": staging_tables,
            "source_detected_view_count": staging_views,
            "imported_table_count": imported_staging_table_count,
            "imported_view_count": imported_staging_view_count,
            "created_at_utc": created_at,
        },
    ]
    con.executemany(
        """
        INSERT INTO db25_consolidation_source_db (
            source_db_label,
            source_db_path,
            source_role,
            source_file_size_bytes,
            source_detected_table_count,
            source_detected_view_count,
            imported_table_count,
            imported_view_count,
            created_at_utc
        )
        VALUES (
            :source_db_label,
            :source_db_path,
            :source_role,
            :source_file_size_bytes,
            :source_detected_table_count,
            :source_detected_view_count,
            :imported_table_count,
            :imported_view_count,
            :created_at_utc
        )
        """,
        rows,
    )


def insert_object_map_rows(
    con: sqlite3.Connection,
    rows: list[ObjectMapRow],
    created_at: str,
) -> None:
    con.executemany(
        """
        INSERT INTO db25_consolidation_object_map (
            source_db_label,
            source_object_name,
            source_object_type,
            target_object_name,
            target_object_type,
            import_status,
            collision_status,
            notes,
            created_at_utc
        )
        VALUES (
            :source_db_label,
            :source_object_name,
            :source_object_type,
            :target_object_name,
            :target_object_type,
            :import_status,
            :collision_status,
            :notes,
            :created_at_utc
        )
        """,
        [{**row.__dict__, "created_at_utc": created_at} for row in rows],
    )


def transform_view_sql(
    source_sql: str,
    source_name: str,
    target_name: str,
    name_map: dict[str, str],
) -> str:
    match = re.match(
        r"(?is)^\s*CREATE\s+VIEW\s+(?:IF\s+NOT\s+EXISTS\s+)?(?:\"[^\"]+\"|`[^`]+`|\[[^\]]+\]|[A-Za-z0-9_]+)\s+AS\s+(.*)$",
        source_sql,
    )
    if not match:
        raise ValueError(f"Could not parse source view SQL for {source_name}")
    body = match.group(1)
    for source_object, target_object in sorted(name_map.items(), key=lambda item: -len(item[0])):
        if source_object == target_object:
            continue
        body = re.sub(rf"\b{re.escape(source_object)}\b", target_object, body)
    return f"CREATE VIEW {quote_identifier(target_name)} AS {body}"


def import_db23_staging_objects(con: sqlite3.Connection) -> tuple[list[ObjectMapRow], int, int]:
    source_objects = list_objects(con, "db23src")
    import_tables = [
        obj for obj in source_objects
        if obj.object_type == "table" and obj.name.startswith("db23_")
    ]
    import_views = [
        obj for obj in source_objects
        if obj.object_type == "view" and obj.name.startswith("qsb_v_db23_")
    ]
    existing_names = object_names(con)
    name_map: dict[str, str] = {}
    object_map_rows: list[ObjectMapRow] = []

    for obj in import_tables:
        collision = obj.name in existing_names
        target_name = f"db25_from_db23_{obj.name}" if collision else obj.name
        collision_status = "collision_prefixed" if collision else "no_collision"
        con.execute(
            f"""
            CREATE TABLE {quote_identifier(target_name)} AS
            SELECT * FROM db23src.{quote_identifier(obj.name)}
            """
        )
        existing_names.add(target_name)
        name_map[obj.name] = target_name
        object_map_rows.append(
            ObjectMapRow(
                source_db_label="db23_staging_branch",
                source_object_name=obj.name,
                source_object_type=obj.object_type,
                target_object_name=target_name,
                target_object_type="table",
                import_status="imported",
                collision_status=collision_status,
                notes="DB23 staging table copied into DB25.",
            )
        )

    for obj in import_views:
        collision = obj.name in existing_names
        target_name = f"db25_from_db23_{obj.name}" if collision else obj.name
        collision_status = "collision_prefixed" if collision else "no_collision"
        try:
            if obj.sql is None:
                raise ValueError("source view SQL is NULL")
            view_sql = transform_view_sql(obj.sql, obj.name, target_name, name_map)
            con.execute(view_sql)
            import_status = "imported"
            notes = "DB23 staging view recreated in DB25 from copied DB23 tables."
            existing_names.add(target_name)
            name_map[obj.name] = target_name
        except Exception as exc:
            import_status = "not_imported"
            notes = f"View could not be recreated: {exc}"
            name_map[obj.name] = target_name
        object_map_rows.append(
            ObjectMapRow(
                source_db_label="db23_staging_branch",
                source_object_name=obj.name,
                source_object_type=obj.object_type,
                target_object_name=target_name,
                target_object_type="view",
                import_status=import_status,
                collision_status=collision_status,
                notes=notes,
            )
        )

    return object_map_rows, len(import_tables), sum(
        1 for row in object_map_rows
        if row.source_object_type == "view" and row.import_status == "imported"
    )


def build_base_object_map(signature_db: Path) -> list[ObjectMapRow]:
    with connect_readonly(signature_db) as con:
        objects = list_objects(con)
    rows: list[ObjectMapRow] = []
    for obj in objects:
        rows.append(
            ObjectMapRow(
                source_db_label="db23b_signature_branch",
                source_object_name=obj.name,
                source_object_type=obj.object_type,
                target_object_name=obj.name,
                target_object_type=obj.object_type,
                import_status="base_copied",
                collision_status="not_applicable_base_copy",
                notes="Object arrived through DB23B base database copy.",
            )
        )
    return rows


def insert_run_log(
    con: sqlite3.Connection,
    event_type: str,
    event_key: str,
    event_value: str,
    event_note: str,
    created_at: str,
) -> None:
    con.execute(
        """
        INSERT INTO db25_consolidation_run_log (
            event_type,
            event_key,
            event_value,
            event_note,
            created_at_utc
        )
        VALUES (?, ?, ?, ?, ?)
        """,
        (event_type, event_key, event_value, event_note, created_at),
    )


def create_db25_views(con: sqlite3.Connection) -> None:
    con.executescript(
        """
        CREATE VIEW qsb_v_db25_current_measurement_reality_dashboard AS
        SELECT 'source_db_count' AS metric_name,
               CAST((SELECT COUNT(*) FROM db25_consolidation_source_db) AS TEXT) AS metric_value,
               'consolidation_source_db' AS metric_source
        UNION ALL
        SELECT 'imported_db23_table_count',
               CAST(COALESCE((SELECT imported_table_count FROM db25_consolidation_source_db WHERE source_db_label = 'db23_staging_branch'), 0) AS TEXT),
               'db25_consolidation_source_db'
        UNION ALL
        SELECT 'imported_db23_view_count',
               CAST(COALESCE((SELECT imported_view_count FROM db25_consolidation_source_db WHERE source_db_label = 'db23_staging_branch'), 0) AS TEXT),
               'db25_consolidation_source_db'
        UNION ALL
        SELECT 'tim_raw_record_count',
               CAST((SELECT COUNT(*) FROM qsb_v_db21_tim_raw_records) AS TEXT),
               'qsb_v_db21_tim_raw_records'
        UNION ALL
        SELECT 'tim_raw_field_value_count',
               CAST((SELECT COUNT(*) FROM qsb_v_db21_tim_raw_field_values) AS TEXT),
               'qsb_v_db21_tim_raw_field_values'
        UNION ALL
        SELECT '41_family_record_count',
               CAST(COALESCE((SELECT record_count FROM qsb_v_db23a_41_family_overview LIMIT 1), 0) AS TEXT),
               'qsb_v_db23a_41_family_overview'
        UNION ALL
        SELECT '44_comment_family_count',
               CAST(COALESCE((SELECT record_count FROM qsb_v_db22_tim_token_count_distribution WHERE line_type = 'comment_line' AND token_count = 44 LIMIT 1), 0) AS TEXT),
               'qsb_v_db22_tim_token_count_distribution'
        UNION ALL
        SELECT 'staging_map_row_count',
               CAST(COALESCE((SELECT COUNT(*) FROM db23_tim_staging_field_map), 0) AS TEXT),
               'db23_tim_staging_field_map'
        UNION ALL
        SELECT 'mapping_gap_count',
               CAST(COALESCE((SELECT COUNT(*) FROM db23_tim_mapping_gap), 0) AS TEXT),
               'db23_tim_mapping_gap'
        UNION ALL
        SELECT 'two_block_focused_switching_token_count',
               CAST(COALESCE((SELECT COUNT(*) FROM qsb_v_db23b_focused_token_side_by_side WHERE token_position IN (7, 11, 13, 17, 23) AND block_discriminating_flag = 1 AND constant_within_each_block_flag = 1), 0) AS TEXT),
               'qsb_v_db23b_focused_token_side_by_side'
        UNION ALL
        SELECT 'foreign_key_violation_count',
               COALESCE((SELECT event_value FROM db25_consolidation_run_log WHERE event_key = 'foreign_key_violation_count' ORDER BY run_log_id DESC LIMIT 1), 'not_available'),
               'db25_consolidation_run_log';

        CREATE VIEW qsb_v_db25_tim_family_overview AS
        SELECT 'line_type_count' AS overview_section,
               line_type AS object_key,
               line_type,
               NULL AS token_count,
               record_count,
               record_fraction,
               NULL AS field_name,
               NULL AS token_position,
               'line_type_profile' AS status,
               'dominant_token_count=' || dominant_token_count || '; min=' || min_token_count || '; max=' || max_token_count AS detail_text
        FROM qsb_v_db22_tim_line_type_counts
        UNION ALL
        SELECT 'token_count_distribution',
               family_label,
               line_type,
               token_count,
               record_count,
               record_fraction,
               NULL,
               NULL,
               'token_count_family',
               family_note
        FROM qsb_v_db22_tim_token_count_distribution
        UNION ALL
        SELECT '41_family_overview',
               family_key,
               line_type,
               token_count,
               record_count,
               NULL,
               NULL,
               NULL,
               token_count_consistency,
               'source_file=' || source_file_name || '; source_family=' || source_family_label
        FROM qsb_v_db23a_41_family_overview
        UNION ALL
        SELECT 'candidate_grouping_token',
               field_name,
               NULL,
               NULL,
               NULL,
               NULL,
               field_name,
               token_position,
               candidate_strength,
               'distinct=' || distinct_value_count || '; signals=' || signal_sources
        FROM qsb_v_db23a_41_candidate_grouping_tokens
        WHERE candidate_label = 'candidate_grouping_token';

        CREATE VIEW qsb_v_db25_tim_staging_and_mapping_overview AS
        SELECT 'token_role_candidate' AS overview_section,
               field_name AS object_key,
               line_type_scope,
               token_position,
               field_name,
               candidate_role_label AS status,
               1 AS needs_mapping_flag,
               'coverage=' || coverage_fraction || '; distinct=' || distinct_value_count || '; recommendation=' || source_recommendation AS detail_text
        FROM qsb_v_db23_tim_token_role_candidates
        UNION ALL
        SELECT 'staging_field_map',
               staging_field_name,
               line_type_scope,
               token_position,
               source_field_name,
               inclusion_status,
               needs_mapping_flag,
               'mapping_status=' || mapping_status || '; role=' || candidate_role_label
        FROM qsb_v_db23_tim_staging_field_map
        UNION ALL
        SELECT 'mapping_gap',
               gap_scope,
               line_type_scope,
               token_position,
               field_name,
               gap_type,
               1 AS needs_mapping_flag,
               'severity=' || gap_severity || '; next_action=' || recommended_next_action
        FROM qsb_v_db23_tim_mapping_gaps;

        CREATE VIEW qsb_v_db25_two_block_signature_overview AS
        SELECT 'block_definition' AS overview_section,
               block_label AS object_key,
               block_label,
               NULL AS token_position,
               NULL AS field_name,
               NULL AS block_a_value,
               NULL AS block_b_value,
               definition_scope AS status,
               'range=' || start_record_index || '-' || end_record_index || '; family_records=' || family_record_count || '; nonfamily=' || nonfamily_record_count AS detail_text
        FROM qsb_v_db23b_block_definitions
        UNION ALL
        SELECT 'focused_token_side_by_side',
               field_name,
               NULL,
               token_position,
               field_name,
               block_a_dominant_value,
               block_b_dominant_value,
               relation_type,
               'block_discriminating=' || block_discriminating_flag || '; constant_each=' || constant_within_each_block_flag || '; transition=' || transition_gap_relation
        FROM qsb_v_db23b_focused_token_side_by_side
        WHERE token_position IN (7, 11, 13, 17, 23)
        UNION ALL
        SELECT 'transition_gap_status',
               family_key,
               NULL,
               NULL,
               NULL,
               dominant_block_a_signature,
               dominant_block_b_signature,
               transition_gap_status,
               'token001_boundary_alignment=' || token001_boundary_alignment
        FROM qsb_v_db23b_first_two_block_whisper;

        CREATE VIEW qsb_v_db25_report_ready_snapshot AS
        SELECT 'data_substrate_summary' AS snapshot_section,
               'available' AS status,
               'DB25 combines DB23B as base copy with DB23 staging objects imported from read-only DB23.' AS finding,
               'Use qsb_v_db25_current_measurement_reality_dashboard for first dashboard checks.' AS next_db_backed_question
        UNION ALL
        SELECT 'visible_tim_families',
               'available',
               '41-token data_line, 44-token comment_line, 2-token short/context, and blank-line families are visible from DB22 lineage views.',
               'Compare family-level structure against staging-map needs.'
        UNION ALL
        SELECT 'staging_mapping_status',
               CASE WHEN (SELECT COUNT(*) FROM db23_tim_staging_field_map) > 0 THEN 'available' ELSE 'not_available' END,
               'DB23 staging field map rows=' || (SELECT COUNT(*) FROM db23_tim_staging_field_map) || '; mapping gaps=' || (SELECT COUNT(*) FROM db23_tim_mapping_gap),
               'Can token-role candidates be promoted into a controlled staging dictionary?'
        UNION ALL
        SELECT 'two_block_signature_status',
               'available',
               'Focused two-block signature visible: ' || focused_tokens_that_switch_together || '; transition=' || transition_gap_status,
               'Can the two-block signature be linked to explicit source/context metadata?'
        FROM qsb_v_db23b_first_two_block_whisper
        UNION ALL
        SELECT 'open_mapping_gaps',
               CASE WHEN (SELECT COUNT(*) FROM db23_tim_mapping_gap) > 0 THEN 'available' ELSE 'not_available' END,
               'Mapping gap count=' || (SELECT COUNT(*) FROM db23_tim_mapping_gap),
               'Which mapping gaps must be closed before analytical staging?';
        """
    )


def insert_result_catalog(con: sqlite3.Connection, created_at: str) -> None:
    rows = [
        {
            "result_object_name": "qsb_v_db25_current_measurement_reality_dashboard",
            "result_object_type": "view",
            "source_stage": "DB25",
            "purpose": "Metric/value dashboard for consolidated Mini-DWH state.",
            "upstream_tables_or_views": "db25_consolidation_source_db;qsb_v_db21_tim_raw_records;qsb_v_db21_tim_raw_field_values;qsb_v_db23a_41_family_overview;db23_tim_staging_field_map;db23_tim_mapping_gap;qsb_v_db23b_focused_token_side_by_side",
        },
        {
            "result_object_name": "qsb_v_db25_tim_family_overview",
            "result_object_type": "view",
            "source_stage": "DB25",
            "purpose": "Family-level TIM structure overview.",
            "upstream_tables_or_views": "qsb_v_db22_tim_line_type_counts;qsb_v_db22_tim_token_count_distribution;qsb_v_db23a_41_family_overview;qsb_v_db23a_41_candidate_grouping_tokens",
        },
        {
            "result_object_name": "qsb_v_db25_tim_staging_and_mapping_overview",
            "result_object_type": "view",
            "source_stage": "DB25",
            "purpose": "Consolidated DB23 staging-map and mapping-gap overview.",
            "upstream_tables_or_views": "qsb_v_db23_tim_token_role_candidates;qsb_v_db23_tim_staging_field_map;qsb_v_db23_tim_mapping_gaps",
        },
        {
            "result_object_name": "qsb_v_db25_two_block_signature_overview",
            "result_object_type": "view",
            "source_stage": "DB25",
            "purpose": "Two-block signature overview from DB23B branch.",
            "upstream_tables_or_views": "qsb_v_db23b_block_definitions;qsb_v_db23b_focused_token_side_by_side;qsb_v_db23b_first_two_block_whisper",
        },
        {
            "result_object_name": "qsb_v_db25_report_ready_snapshot",
            "result_object_type": "view",
            "source_stage": "DB25",
            "purpose": "Compact report-ready current research snapshot.",
            "upstream_tables_or_views": "db23_tim_staging_field_map;db23_tim_mapping_gap;qsb_v_db23b_first_two_block_whisper",
        },
    ]
    con.executemany(
        """
        INSERT INTO db25_result_table_catalog (
            result_object_name,
            result_object_type,
            source_stage,
            purpose,
            upstream_tables_or_views,
            created_by_script,
            created_at_utc,
            data_substrate,
            claim_boundary_status
        )
        VALUES (
            :result_object_name,
            :result_object_type,
            :source_stage,
            :purpose,
            :upstream_tables_or_views,
            :created_by_script,
            :created_at_utc,
            :data_substrate,
            :claim_boundary_status
        )
        """,
        [
            {
                **row,
                "created_by_script": SCRIPT_NAME,
                "created_at_utc": created_at,
                "data_substrate": "SQLite input DBs only: DB23 staging branch and DB23B signature branch.",
                "claim_boundary_status": CLAIM_BOUNDARY,
            }
            for row in rows
        ],
    )


def create_output_db(signature_db: Path, output_root: Path, output_db: Path) -> None:
    output_root.mkdir(parents=True, exist_ok=True)
    shutil.copy2(signature_db, output_db)


def build_csv_rows(con: sqlite3.Connection) -> dict[str, list[dict[str, Any]]]:
    object_rows = fetch_dicts(
        con,
        """
        SELECT
            name AS object_name,
            type AS object_type,
            CASE
                WHEN name LIKE 'db25_%' OR name LIKE 'qsb_v_db25_%' THEN 'db25_created'
                WHEN name LIKE 'db23_%' OR name LIKE 'qsb_v_db23_%' THEN 'db23_staging_branch_import'
                WHEN name LIKE 'db23a_%' OR name LIKE 'qsb_v_db23a_%' THEN 'db23a_signature_branch_base'
                WHEN name LIKE 'db23b_%' OR name LIKE 'qsb_v_db23b_%' THEN 'db23b_signature_branch_base'
                WHEN name LIKE 'db22_%' OR name LIKE 'qsb_v_db22_%' THEN 'db22_lineage_base'
                WHEN name LIKE 'db21_%' OR name LIKE 'qsb_v_db21_%' THEN 'db21_lineage_base'
                WHEN name LIKE 'db20_%' OR name LIKE 'qsb_v_db20_%' THEN 'db20_lineage_base'
                ELSE 'other_base_metadata'
            END AS source_stage
        FROM sqlite_master
        WHERE type IN ('table', 'view')
          AND name NOT LIKE 'sqlite_%'
        ORDER BY type, name
        """,
    )
    table_rows = []
    for row in fetch_dicts(
        con,
        """
        SELECT name AS object_name
        FROM sqlite_master
        WHERE type = 'table'
          AND name NOT LIKE 'sqlite_%'
        ORDER BY name
        """,
    ):
        name = row["object_name"]
        table_rows.append(
            {
                "object_name": name,
                "object_type": "table",
                "row_count": table_row_count(con, name),
            }
        )
    view_rows = fetch_dicts(
        con,
        """
        SELECT
            name AS view_name,
            CASE
                WHEN name LIKE 'qsb_v_db25_%' THEN 'db25_consolidated_view'
                WHEN name LIKE 'qsb_v_db23_%' THEN 'db23_staging_imported_view'
                WHEN name LIKE 'qsb_v_db23a_%' THEN 'db23a_base_view'
                WHEN name LIKE 'qsb_v_db23b_%' THEN 'db23b_base_view'
                WHEN name LIKE 'qsb_v_db22_%' THEN 'db22_base_view'
                WHEN name LIKE 'qsb_v_db21_%' THEN 'db21_base_view'
                WHEN name LIKE 'qsb_v_db20_%' THEN 'db20_base_view'
                ELSE 'other_view'
            END AS view_family,
            sql AS view_sql
        FROM sqlite_master
        WHERE type = 'view'
        ORDER BY name
        """,
    )
    map_rows = fetch_dicts(
        con,
        """
        SELECT
            source_db_label,
            source_object_name,
            source_object_type,
            target_object_name,
            target_object_type,
            import_status,
            collision_status,
            notes
        FROM db25_consolidation_object_map
        ORDER BY source_db_label, source_object_type, source_object_name
        """,
    )
    return {
        "objects": object_rows,
        "tables": table_rows,
        "views": view_rows,
        "map": map_rows,
    }


def write_csv(path: Path, rows: list[dict[str, Any]], fieldnames: list[str]) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow({field: row.get(field) for field in fieldnames})


def write_outputs(
    con: sqlite3.Connection,
    output_root: Path,
    output_db: Path,
    staging_db: Path,
    signature_db: Path,
    created_at: str,
) -> dict[str, Any]:
    csv_rows = build_csv_rows(con)
    write_csv(
        output_root / "db25_consolidated_object_inventory.csv",
        csv_rows["objects"],
        ["object_name", "object_type", "source_stage"],
    )
    write_csv(
        output_root / "db25_consolidated_table_counts.csv",
        csv_rows["tables"],
        ["object_name", "object_type", "row_count"],
    )
    write_csv(
        output_root / "db25_consolidated_view_inventory.csv",
        csv_rows["views"],
        ["view_name", "view_family", "view_sql"],
    )
    write_csv(
        output_root / "db25_consolidation_map.csv",
        csv_rows["map"],
        [
            "source_db_label",
            "source_object_name",
            "source_object_type",
            "target_object_name",
            "target_object_type",
            "import_status",
            "collision_status",
            "notes",
        ],
    )

    dashboard = fetch_dicts(
        con,
        "SELECT * FROM qsb_v_db25_current_measurement_reality_dashboard",
    )
    report_ready = fetch_dicts(
        con,
        "SELECT * FROM qsb_v_db25_report_ready_snapshot",
    )
    source_dbs = fetch_dicts(
        con,
        "SELECT * FROM db25_consolidation_source_db ORDER BY source_db_label",
    )
    imported_tables = int(
        con.execute(
            """
            SELECT COUNT(*)
            FROM db25_consolidation_object_map
            WHERE source_db_label = 'db23_staging_branch'
              AND source_object_type = 'table'
              AND import_status = 'imported'
            """
        ).fetchone()[0]
    )
    imported_views = int(
        con.execute(
            """
            SELECT COUNT(*)
            FROM db25_consolidation_object_map
            WHERE source_db_label = 'db23_staging_branch'
              AND source_object_type = 'view'
              AND import_status = 'imported'
            """
        ).fetchone()[0]
    )
    collisions = fetch_dicts(
        con,
        """
        SELECT *
        FROM db25_consolidation_object_map
        WHERE collision_status <> 'no_collision'
          AND source_db_label = 'db23_staging_branch'
        ORDER BY source_object_name
        """,
    )
    fk_count = int(
        con.execute(
            """
            SELECT event_value
            FROM db25_consolidation_run_log
            WHERE event_key = 'foreign_key_violation_count'
            ORDER BY run_log_id DESC
            LIMIT 1
            """
        ).fetchone()[0]
    )
    summary = {
        "block": BLOCK_LABEL,
        "created_at_utc": created_at,
        "output_db": str(output_db),
        "staging_db": str(staging_db),
        "signature_db": str(signature_db),
        "data_substrate_used": "SQLite DBs only; DB23B copied as base, DB23 staging attached read-only and imported.",
        "input_dbs_modified": False,
        "raw_file_fallback_used": False,
        "imported_db23_table_count": imported_tables,
        "imported_db23_view_count": imported_views,
        "collision_count": len(collisions),
        "collisions": collisions,
        "db25_metadata_tables": [
            "db25_consolidation_source_db",
            "db25_consolidation_object_map",
            "db25_consolidation_run_log",
            "db25_result_table_catalog",
        ],
        "db25_views": [
            "qsb_v_db25_current_measurement_reality_dashboard",
            "qsb_v_db25_tim_family_overview",
            "qsb_v_db25_tim_staging_and_mapping_overview",
            "qsb_v_db25_two_block_signature_overview",
            "qsb_v_db25_report_ready_snapshot",
        ],
        "dashboard": dashboard,
        "report_ready_snapshot": report_ready,
        "source_dbs": source_dbs,
        "foreign_key_violation_count": fk_count,
        "claim_boundary": CLAIM_BOUNDARY,
    }
    (output_root / "db25_consolidated_snapshot_summary.json").write_text(
        pretty_json(summary) + "\n",
        encoding="utf-8",
    )

    dashboard_lines = "\n".join(
        f"- `{row['metric_name']}`: `{row['metric_value']}` ({row['metric_source']})"
        for row in dashboard
    )
    report_lines = "\n".join(
        f"- `{row['snapshot_section']}`: {row['status']} - {row['finding']}"
        for row in report_ready
    )
    readout = f"""# QSB-DB25 Consolidated Research Snapshot

## Data substrate used

- Signature/base DB: `{signature_db}`
- Staging-map DB: `{staging_db}`
- Output DB: `{output_db}`
- DB23B was copied to DB25 as the base.
- DB23 staging DB was attached read-only and imported.
- Raw TIM/PAR files were not read.
- Input DBs modified: `no`.

## Consolidation result

- Imported DB23 staging tables: `{imported_tables}`
- Imported DB23 staging views: `{imported_views}`
- Collision count: `{len(collisions)}`
- Collision handling: `{'no collisions detected' if not collisions else 'prefixed imported names were used where needed'}`

## DB25 metadata tables

- `db25_consolidation_source_db`
- `db25_consolidation_object_map`
- `db25_consolidation_run_log`
- `db25_result_table_catalog`

## DB25 consolidated views

- `qsb_v_db25_current_measurement_reality_dashboard`
- `qsb_v_db25_tim_family_overview`
- `qsb_v_db25_tim_staging_and_mapping_overview`
- `qsb_v_db25_two_block_signature_overview`
- `qsb_v_db25_report_ready_snapshot`

## Dashboard counts

{dashboard_lines}

## Report-ready first rows

{report_lines}

## Branch visibility

- DB23 staging-map branch visible: `yes`
- DB23B two-block signature branch visible: `yes`

## Claim boundary

{CLAIM_BOUNDARY}

DB25 is a consolidation step, not a new analysis step.
"""
    (output_root / "db25_consolidated_snapshot_readout.md").write_text(
        readout,
        encoding="utf-8",
    )
    return summary


def run_consolidation(
    staging_db: Path,
    signature_db: Path,
    output_root: Path,
    output_db: Path,
) -> dict[str, Any]:
    created_at = utc_now()
    create_output_db(signature_db, output_root, output_db)
    with connect_db(output_db) as con:
        create_metadata_tables(con)
        attach_readonly(con, staging_db, "db23src")

        base_map_rows = build_base_object_map(signature_db)
        staging_map_rows, imported_table_count, imported_view_count = import_db23_staging_objects(con)

        insert_source_db_rows(
            con,
            staging_db=staging_db,
            signature_db=signature_db,
            imported_staging_table_count=imported_table_count,
            imported_staging_view_count=imported_view_count,
            created_at=created_at,
        )
        insert_object_map_rows(con, base_map_rows + staging_map_rows, created_at)
        create_db25_views(con)
        insert_result_catalog(con, created_at)
        con.commit()

        fk_rows = con.execute("PRAGMA foreign_key_check").fetchall()
        insert_run_log(
            con,
            event_type="validation",
            event_key="foreign_key_violation_count",
            event_value=str(len(fk_rows)),
            event_note="PRAGMA foreign_key_check after DB25 consolidation.",
            created_at=created_at,
        )
        con.commit()
        summary = write_outputs(
            con,
            output_root=output_root,
            output_db=output_db,
            staging_db=staging_db,
            signature_db=signature_db,
            created_at=created_at,
        )
    return summary


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Create QSB-DB25 consolidated research snapshot from DB23 and DB23B SQLite branches."
    )
    parser.add_argument(
        "--staging-db",
        type=Path,
        default=DEFAULT_STAGING_DB,
        help="Path to DB23 TIM staging field-map database.",
    )
    parser.add_argument(
        "--signature-db",
        type=Path,
        default=DEFAULT_SIGNATURE_DB,
        help="Path to DB23B two-block signature database.",
    )
    parser.add_argument(
        "--output-root",
        type=Path,
        default=DEFAULT_OUTPUT_ROOT,
        help="Directory for DB25 output artifacts.",
    )
    parser.add_argument(
        "--output-db",
        type=Path,
        default=DEFAULT_OUTPUT_DB,
        help="Path for DB25 consolidated snapshot database.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Validate paths and report planned consolidation without writing outputs.",
    )
    return parser.parse_args(argv)


def main(argv: list[str]) -> int:
    args = parse_args(argv)
    ensure_input_db(args.staging_db, "DB23 staging")
    ensure_input_db(args.signature_db, "DB23B signature")
    ensure_safe_outputs(args.output_root, args.output_db)

    if args.dry_run:
        print(f"block: {BLOCK_LABEL}")
        print(f"staging_db: {args.staging_db}")
        print(f"signature_db: {args.signature_db}")
        print(f"output_root: {args.output_root}")
        print(f"output_db: {args.output_db}")
        print("dry_run: true")
        print("raw_file_fallback_used: no")
        return 0

    summary = run_consolidation(
        staging_db=args.staging_db,
        signature_db=args.signature_db,
        output_root=args.output_root,
        output_db=args.output_db,
    )
    print(f"block: {BLOCK_LABEL}")
    print(f"output_db: {summary['output_db']}")
    print(f"imported_db23_table_count: {summary['imported_db23_table_count']}")
    print(f"imported_db23_view_count: {summary['imported_db23_view_count']}")
    print(f"collision_count: {summary['collision_count']}")
    print(f"foreign_key_violation_count: {summary['foreign_key_violation_count']}")
    print("raw_file_fallback_used: no")
    print("input_dbs_modified: no")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main(sys.argv[1:]))
    except Exception as exc:
        print(f"error: {exc}", file=sys.stderr)
        raise SystemExit(1)
