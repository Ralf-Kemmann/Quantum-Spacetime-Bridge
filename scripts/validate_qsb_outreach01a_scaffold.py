#!/usr/bin/env python3
"""Validate the additive QSB-OUTREACH01A scaffold without persistent migration."""
from __future__ import annotations

import csv
import json
import sqlite3
from pathlib import Path
from typing import Iterable


ROOT = Path(__file__).resolve().parents[1]

REQUIRED_FILES = [
    ROOT / "docs/QSB_OUTREACH01A_01_SCOPE_AND_CONTACT_STRATEGY_SPEC.md",
    ROOT / "docs/QSB_OUTREACH01A_02_RESEARCH_GROUP_FIT_MAPPING.md",
    ROOT / "docs/QSB_OUTREACH01A_03_RELATIONAL_STATE_IDENTITY_MATHEMATICAL_SPEC.md",
    ROOT / "docs/QSB_OUTREACH01A_04_DWH_AND_MULTILINGUAL_VIEW_SPEC.md",
    ROOT / "docs/QSB_OUTREACH01A_05_SYNTHETIC_DEMONSTRATOR_CASE_DEFINITION.md",
    ROOT / "docs/QSB_OUTREACH01A_09_CONTACT_GATE_CHECKLIST.md",
    ROOT / "data/QSB-OUTREACH01A/canonical_schema.json",
    ROOT / "data/QSB-OUTREACH01A/field_aliases.csv",
    ROOT / "data/QSB-OUTREACH01A/001_qsb_outreach01a_sqlite_dwh_ddl.sql",
    ROOT / "data/QSB-OUTREACH01A/002_qsb_outreach01a_sqlite_views.sql",
]

REQUIRED_ALIAS_COLUMNS = {
    "canonical_field_name",
    "language_code",
    "sql_alias",
    "display_label",
    "description",
    "review_status",
}
EXPECTED_LANGUAGES = {"en", "de", "ca"}
EXPECTED_ROUTE = ["raw", "staging", "harmonized", "relational", "analytical", "presentation"]
EXPECTED_TABLES = {
    "outreach_case",
    "outreach_raw_observation",
    "outreach_staging_state",
    "outreach_transformation_rule",
    "outreach_harmonized_state",
    "outreach_state_feature",
    "outreach_model_run",
    "outreach_relational_pair",
    "outreach_analytical_result",
}
EXPECTED_VIEWS = {
    "qsb_v_outreach01a_state_en",
    "qsb_v_outreach01a_state_de",
    "qsb_v_outreach01a_state_ca",
    "qsb_v_outreach01a_relation_en",
    "qsb_v_outreach01a_relation_de",
    "qsb_v_outreach01a_relation_ca",
}
EXPECTED_HISTORY_TYPES = {
    "none",
    "finite_history_features",
    "delay_window",
    "embedded_history_vector",
}
EXPECTED_REVIEW_STATUSES = {"reviewed", "not_yet_reviewed"}


def read_schema() -> dict:
    return json.loads((ROOT / "data/QSB-OUTREACH01A/canonical_schema.json").read_text(encoding="utf-8"))


def read_alias_rows() -> tuple[list[dict[str, str]], set[str]]:
    with (ROOT / "data/QSB-OUTREACH01A/field_aliases.csv").open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        return list(reader), set(reader.fieldnames or [])


def validate_files() -> list[str]:
    return [str(path.relative_to(ROOT)) for path in REQUIRED_FILES if not path.exists()]


def validate_route(schema: dict) -> list[str]:
    route = schema.get("dwh_alignment", {}).get("data_route")
    if route != EXPECTED_ROUTE:
        return [f"Unexpected data route: {route}"]
    return []


def validate_declared_enums(schema: dict, alias_rows: Iterable[dict[str, str]]) -> list[str]:
    issues: list[str] = []
    enum_values = schema.get("enum_values", {})
    history_types = set(enum_values.get("history_representation_type", []))
    if history_types != EXPECTED_HISTORY_TYPES:
        issues.append(f"Unexpected history enum values: {sorted(history_types)}")

    review_statuses = set(enum_values.get("review_status", []))
    if review_statuses != EXPECTED_REVIEW_STATUSES:
        issues.append(f"Unexpected review status enum values: {sorted(review_statuses)}")

    row_review_statuses = {row["review_status"] for row in alias_rows}
    unknown = sorted(row_review_statuses - EXPECTED_REVIEW_STATUSES)
    if unknown:
        issues.append(f"Unknown alias review_status values: {unknown}")
    return issues


def validate_aliases(schema: dict, rows: list[dict[str, str]], columns: set[str]) -> list[str]:
    issues: list[str] = []
    missing_columns = sorted(REQUIRED_ALIAS_COLUMNS - columns)
    if missing_columns:
        return [f"Alias catalog missing required columns: {missing_columns}"]

    canonical = {item["name"] for item in schema["state_view_fields"]}
    alias_fields = {row["canonical_field_name"] for row in rows}
    unknown = sorted(alias_fields - canonical)
    if unknown:
        issues.append(f"Aliases reference unknown canonical fields: {unknown}")

    missing_alias_fields = sorted(canonical - alias_fields)
    if missing_alias_fields:
        issues.append(f"Canonical fields without aliases: {missing_alias_fields}")

    seen_field_language: set[tuple[str, str]] = set()
    seen_alias_by_language: set[tuple[str, str]] = set()
    for row in rows:
        key = (row["canonical_field_name"], row["language_code"])
        if key in seen_field_language:
            issues.append(f"Duplicate alias row for canonical/language: {key}")
        seen_field_language.add(key)

        alias_key = (row["language_code"], row["sql_alias"])
        if alias_key in seen_alias_by_language:
            issues.append(f"Duplicate SQL alias within language: {alias_key}")
        seen_alias_by_language.add(alias_key)

    languages = {row["language_code"] for row in rows}
    missing_languages = sorted(EXPECTED_LANGUAGES - languages)
    if missing_languages:
        issues.append(f"Missing language aliases: {missing_languages}")

    for field in canonical:
        field_languages = {row["language_code"] for row in rows if row["canonical_field_name"] == field}
        missing = sorted(EXPECTED_LANGUAGES - field_languages)
        if missing:
            issues.append(f"Field {field} missing aliases for: {missing}")
    return issues


def connect_and_load() -> sqlite3.Connection:
    ddl = (ROOT / "data/QSB-OUTREACH01A/001_qsb_outreach01a_sqlite_dwh_ddl.sql").read_text(encoding="utf-8")
    views = (ROOT / "data/QSB-OUTREACH01A/002_qsb_outreach01a_sqlite_views.sql").read_text(encoding="utf-8")
    conn = sqlite3.connect(":memory:")
    conn.execute("PRAGMA foreign_keys = ON")
    conn.executescript(ddl)
    conn.executescript(views)
    return conn


def object_names(conn: sqlite3.Connection, object_type: str) -> set[str]:
    rows = conn.execute(
        "SELECT name FROM sqlite_master WHERE type = ? AND name NOT LIKE 'sqlite_%'",
        (object_type,),
    ).fetchall()
    return {str(row[0]) for row in rows}


def table_columns(conn: sqlite3.Connection, table_name: str) -> set[str]:
    return {str(row[1]) for row in conn.execute(f"PRAGMA table_info({table_name})").fetchall()}


def validate_sql_inventory(conn: sqlite3.Connection, schema: dict, alias_rows: list[dict[str, str]]) -> list[str]:
    issues: list[str] = []
    fk_status = conn.execute("PRAGMA foreign_keys").fetchone()[0]
    if fk_status != 1:
        issues.append("SQLite foreign keys are not enabled")

    missing_tables = sorted(EXPECTED_TABLES - object_names(conn, "table"))
    if missing_tables:
        issues.append(f"Missing expected tables: {missing_tables}")

    missing_views = sorted(EXPECTED_VIEWS - object_names(conn, "view"))
    if missing_views:
        issues.append(f"Missing expected views: {missing_views}")

    harmonized_columns = table_columns(conn, "outreach_harmonized_state")
    canonical_state_fields = {item["name"] for item in schema["state_view_fields"]}
    missing_state_columns = sorted(canonical_state_fields - harmonized_columns)
    if missing_state_columns:
        issues.append(f"Harmonized state missing canonical fields: {missing_state_columns}")

    if "model_version" in canonical_state_fields:
        issues.append("model_version must not be part of state_view_fields")

    raw_columns = table_columns(conn, "outreach_raw_observation")
    for raw_field in schema.get("raw_fields", []):
        if raw_field["name"] not in raw_columns:
            issues.append(f"Raw observation missing raw field: {raw_field['name']}")

    for language in EXPECTED_LANGUAGES:
        view_columns = table_columns(conn, f"qsb_v_outreach01a_state_{language}")
        expected_aliases = {
            row["sql_alias"]
            for row in alias_rows
            if row["language_code"] == language
        }
        missing_aliases = sorted(expected_aliases - view_columns)
        if missing_aliases:
            issues.append(f"State view {language} missing SQL aliases: {missing_aliases}")
    return issues


def expect_integrity_error(conn: sqlite3.Connection, sql: str, params: tuple[object, ...], label: str) -> list[str]:
    try:
        conn.execute(sql, params)
    except sqlite3.IntegrityError:
        return []
    return [f"Expected integrity error did not occur: {label}"]


def validate_json_payloads(payloads: Iterable[str]) -> list[str]:
    issues: list[str] = []
    for payload in payloads:
        try:
            json.loads(payload)
        except json.JSONDecodeError as exc:
            issues.append(f"Invalid JSON sample payload {payload!r}: {exc}")
    return issues


def insert_case_fixture(conn: sqlite3.Connection) -> None:
    conn.execute(
        "INSERT INTO outreach_case(outreach_case_id, case_code, title, status) VALUES (?, ?, ?, ?)",
        ("case_a", "CASE_A", "Case A", "draft"),
    )
    conn.execute(
        "INSERT INTO outreach_case(outreach_case_id, case_code, title, status) VALUES (?, ?, ?, ?)",
        ("case_b", "CASE_B", "Case B", "draft"),
    )
    for case_id, raw_id, source_id in [
        ("case_a", "raw_a_1", "src_a_1"),
        ("case_a", "raw_a_2", "src_a_2"),
        ("case_b", "raw_b_1", "src_b_1"),
    ]:
        conn.execute(
            """
            INSERT INTO outreach_raw_observation(
                raw_observation_id, outreach_case_id, source_record_id,
                source_payload_json, source_checksum, source_checksum_algorithm
            ) VALUES (?, ?, ?, ?, ?, ?)
            """,
            (raw_id, case_id, source_id, '{"pulse": 1}', None, None),
        )

    state_rows = [
        ("hs_a_1", "case_a", "raw_a_1", "event_a_1", "desc_a_1", "state_a_1", "src_a_1", 1),
        ("hs_a_2", "case_a", "raw_a_2", "event_a_2", "desc_a_2", "state_a_2", "src_a_2", 2),
        ("hs_b_1", "case_b", "raw_b_1", "event_b_1", "desc_b_1", "state_b_1", "src_b_1", 1),
    ]
    for row in state_rows:
        conn.execute(
            """
            INSERT INTO outreach_harmonized_state(
                harmonized_state_id, outreach_case_id, raw_observation_id,
                event_instance_id, state_descriptor_id, state_id, source_record_id,
                forcing_cycle_index, background_state_type, background_state_json,
                history_representation_type, history_descriptor_json,
                history_window_start, history_window_end, transformation_version,
                harmonization_status
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                row[0],
                row[1],
                row[2],
                row[3],
                row[4],
                row[5],
                row[6],
                row[7],
                "synthetic_control",
                '{"resource": "bounded"}',
                "finite_history_features",
                '{"lag_features": [1, 2]}',
                -2.0,
                0.0,
                "transform_v0",
                "accepted",
            ),
        )
    conn.execute(
        """
        INSERT INTO outreach_model_run(
            model_run_id, outreach_case_id, run_code, model_version,
            parameter_config_json, run_status
        ) VALUES (?, ?, ?, ?, ?, ?)
        """,
        ("run_a", "case_a", "RUN_A", "model_v0", '{"threshold": "configured"}', "completed"),
    )
    conn.execute(
        """
        INSERT INTO outreach_model_run(
            model_run_id, outreach_case_id, run_code, model_version,
            parameter_config_json, run_status
        ) VALUES (?, ?, ?, ?, ?, ?)
        """,
        ("run_b", "case_b", "RUN_B", "model_v0", '{"threshold": "configured"}', "completed"),
    )


def validate_integrity_rules(conn: sqlite3.Connection) -> list[str]:
    issues: list[str] = []
    insert_case_fixture(conn)

    sample_json = [
        row[0]
        for row in conn.execute(
            """
            SELECT source_payload_json FROM outreach_raw_observation
            UNION ALL
            SELECT background_state_json FROM outreach_harmonized_state
            UNION ALL
            SELECT history_descriptor_json FROM outreach_harmonized_state
            UNION ALL
            SELECT parameter_config_json FROM outreach_model_run
            """
        ).fetchall()
        if row[0] is not None
    ]
    issues.extend(validate_json_payloads(sample_json))

    conn.execute(
        """
        INSERT INTO outreach_relational_pair(
            relational_pair_id, outreach_case_id, model_run_id, state_i_id, state_j_id,
            similarity_score, observable_match, class_match, edge_status
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        ("pair_a_1", "case_a", "run_a", "hs_a_1", "hs_a_2", 0.9, 1, 1, 1),
    )

    pair_insert = """
        INSERT INTO outreach_relational_pair(
            relational_pair_id, outreach_case_id, model_run_id, state_i_id, state_j_id,
            similarity_score
        ) VALUES (?, ?, ?, ?, ?, ?)
    """
    issues.extend(expect_integrity_error(conn, pair_insert, ("self_pair", "case_a", "run_a", "hs_a_1", "hs_a_1", 1.0), "self-pair"))
    issues.extend(expect_integrity_error(conn, pair_insert, ("mirror_pair", "case_a", "run_a", "hs_a_2", "hs_a_1", 0.9), "mirror pair order"))
    issues.extend(expect_integrity_error(conn, pair_insert, ("cross_case_pair", "case_a", "run_a", "hs_a_1", "hs_b_1", 0.4), "cross-case state"))
    issues.extend(expect_integrity_error(conn, pair_insert, ("cross_case_run", "case_a", "run_b", "hs_a_1", "hs_a_2", 0.4), "cross-case model run"))
    return issues


def validate_sql_and_integrity(schema: dict, alias_rows: list[dict[str, str]]) -> list[str]:
    issues: list[str] = []
    try:
        conn = connect_and_load()
        issues.extend(validate_sql_inventory(conn, schema, alias_rows))
        issues.extend(validate_integrity_rules(conn))
        fk_violations = conn.execute("PRAGMA foreign_key_check").fetchall()
        if fk_violations:
            issues.append(f"Foreign key check returned rows: {fk_violations}")
        conn.close()
    except sqlite3.Error as exc:
        issues.append(f"SQLite DDL/view/integrity validation failed: {exc}")
    return issues


def main() -> int:
    issues = validate_files()
    if not issues:
        schema = read_schema()
        alias_rows, alias_columns = read_alias_rows()
        issues.extend(validate_route(schema))
        issues.extend(validate_aliases(schema, alias_rows, alias_columns))
        issues.extend(validate_declared_enums(schema, alias_rows))
        issues.extend(validate_sql_and_integrity(schema, alias_rows))

    if issues:
        for issue in issues:
            print(f"FAIL: {issue}")
        return 1

    print("QSB-OUTREACH01A scaffold and cross-layer consistency validation passed")
    print("No persistent migration was executed; SQLite checks used an in-memory database only.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
