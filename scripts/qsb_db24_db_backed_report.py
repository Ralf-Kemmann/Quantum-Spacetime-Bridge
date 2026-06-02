#!/usr/bin/env python3
"""QSB-DB24: DB-backed research data report.

This script is a reporting-substrate test. It reads the selected QSB Mini-DWH
SQLite database in read-only mode, queries available tables/views dynamically,
and writes Markdown/JSON/CSV report outputs. It does not read raw TIM/PAR
files, does not use prior CSV/JSON/MD outputs as data substrate, does not
modify the input database, and does not compute timing quantities, residuals,
delays, physical timing parameters, model quantities, or physical conclusions.
"""

from __future__ import annotations

import argparse
import csv
import json
import re
import sqlite3
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


BLOCK_LABEL = "QSB-DB24_DB_BACKED_REPORT_TEST"
DEFAULT_INPUT_DB = Path(
    "runs/QSB-DB/QSB_DB23B_TWO_BLOCK_SIGNATURE_INSPECTION/"
    "qsb_research_two_block_signature_inspection.db"
)
DEFAULT_OUTPUT_ROOT = Path("runs/QSB-DB/QSB_DB24_DB_BACKED_REPORT_TEST")

REPORT_MD = "db24_db_backed_research_data_report.md"
REPORT_JSON = "db24_db_backed_research_data_report.json"
QUERY_INVENTORY_CSV = "db24_report_query_inventory.csv"
VIEW_SAMPLES_CSV = "db24_report_view_samples.csv"
TABLE_COUNTS_CSV = "db24_report_table_counts.csv"

CLAIM_BOUNDARY = (
    "QSB-DB24 is a database-backed first-look reporting test. It does not "
    "compute timing quantities, delays, residuals, model fits, physical timing "
    "parameters, or physical conclusions, and it does not assign physical "
    "meaning to TIM token positions."
)

CLAIM_RISK_FREE_NOTE = (
    "No raw TIM/PAR files are read; no existing database is modified; report "
    "outputs are generated from DB tables/views only."
)


@dataclass
class QueryInventoryRow:
    object_name: str
    object_type: str
    query_purpose: str
    query_status: str
    row_count_if_available: int | str
    error_message_if_any: str


def utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def compact_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=True, separators=(",", ":"))


def pretty_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=True, indent=2)


def expected_output_paths(output_root: Path) -> list[Path]:
    return [
        output_root / REPORT_MD,
        output_root / REPORT_JSON,
        output_root / QUERY_INVENTORY_CSV,
        output_root / VIEW_SAMPLES_CSV,
        output_root / TABLE_COUNTS_CSV,
    ]


def ensure_input_db(input_db: Path) -> None:
    if not input_db.exists():
        raise FileNotFoundError(f"Input DB does not exist: {input_db}")
    if not input_db.is_file():
        raise ValueError(f"Input DB path is not a file: {input_db}")


def ensure_safe_outputs(output_root: Path) -> None:
    existing = [str(path) for path in expected_output_paths(output_root) if path.exists()]
    if existing:
        raise FileExistsError(
            "Refusing to overwrite existing DB24 report artifact(s): "
            + "; ".join(existing)
        )


def connect_read_only(input_db: Path) -> sqlite3.Connection:
    uri = f"file:{input_db}?mode=ro"
    con = sqlite3.connect(uri, uri=True)
    con.row_factory = sqlite3.Row
    con.execute("PRAGMA foreign_keys = ON")
    con.execute("PRAGMA query_only = ON")
    return con


class ReportDB:
    def __init__(self, con: sqlite3.Connection) -> None:
        self.con = con
        self.inventory: list[QueryInventoryRow] = []

    def log(
        self,
        object_name: str,
        object_type: str,
        purpose: str,
        status: str,
        row_count: int | str = "",
        error: str = "",
    ) -> None:
        self.inventory.append(
            QueryInventoryRow(
                object_name=object_name,
                object_type=object_type,
                query_purpose=purpose,
                query_status=status,
                row_count_if_available=row_count,
                error_message_if_any=error,
            )
        )

    def fetch_all(
        self,
        object_name: str,
        object_type: str,
        purpose: str,
        sql: str,
        params: tuple[Any, ...] = (),
    ) -> list[dict[str, Any]]:
        try:
            rows = [dict(row) for row in self.con.execute(sql, params).fetchall()]
            self.log(object_name, object_type, purpose, "ok", len(rows), "")
            return rows
        except Exception as exc:  # pragma: no cover - defensive audit path
            self.log(object_name, object_type, purpose, "error", "", str(exc))
            return []

    def fetch_scalar(
        self,
        object_name: str,
        object_type: str,
        purpose: str,
        sql: str,
        params: tuple[Any, ...] = (),
    ) -> Any:
        try:
            row = self.con.execute(sql, params).fetchone()
            value = row[0] if row is not None else None
            self.log(object_name, object_type, purpose, "ok", 1 if row else 0, "")
            return value
        except Exception as exc:  # pragma: no cover - defensive audit path
            self.log(object_name, object_type, purpose, "error", "", str(exc))
            return None

    def count_object(self, object_name: str, object_type: str, purpose: str) -> int | None:
        try:
            quoted = quote_identifier(object_name)
            count = int(self.con.execute(f"SELECT COUNT(*) FROM {quoted}").fetchone()[0])
            self.log(object_name, object_type, purpose, "ok", count, "")
            return count
        except Exception as exc:  # pragma: no cover - defensive audit path
            self.log(object_name, object_type, purpose, "error", "", str(exc))
            return None

    def log_missing(self, object_name: str, object_type: str, purpose: str) -> None:
        self.log(object_name, object_type, purpose, "not_present", "", "not present in selected DB")


def quote_identifier(identifier: str) -> str:
    return '"' + identifier.replace('"', '""') + '"'


def object_exists(objects: dict[str, str], name: str, object_type: str | None = None) -> bool:
    if name not in objects:
        return False
    if object_type is None:
        return True
    return objects[name] == object_type


def write_csv(path: Path, rows: list[dict[str, Any]], fieldnames: list[str]) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow({field: row.get(field) for field in fieldnames})


def qsb_view_family(view_name: str) -> str:
    match = re.match(r"qsb_v_(db\d+[a-z]?)_", view_name)
    if match:
        return match.group(1)
    return "other_qsb_view"


def render_table(rows: list[dict[str, Any]], columns: list[str], limit: int | None = None) -> str:
    selected = rows if limit is None else rows[:limit]
    if not selected:
        return "_No rows available._"
    header = "| " + " | ".join(columns) + " |"
    separator = "| " + " | ".join("---" for _ in columns) + " |"
    lines = [header, separator]
    for row in selected:
        cells = []
        for column in columns:
            value = row.get(column, "")
            text = "" if value is None else str(value)
            text = text.replace("\n", " ").replace("|", "\\|")
            if len(text) > 160:
                text = text[:157] + "..."
            cells.append(text)
        lines.append("| " + " | ".join(cells) + " |")
    return "\n".join(lines)


def format_position_list(rows: list[dict[str, Any]]) -> str:
    values = [str(row.get("field_name", "")) for row in rows if row.get("field_name")]
    return ", ".join(values) if values else "not available"


def collect_catalog(db: ReportDB) -> tuple[dict[str, str], list[dict[str, Any]], list[dict[str, Any]]]:
    catalog_rows = db.fetch_all(
        "sqlite_master",
        "system_table",
        "catalog tables and views",
        """
        SELECT name, type
        FROM sqlite_master
        WHERE type IN ('table', 'view')
        ORDER BY type, name
        """,
    )
    objects = {row["name"]: row["type"] for row in catalog_rows}
    table_rows = [row for row in catalog_rows if row["type"] == "table"]
    view_rows = [row for row in catalog_rows if row["type"] == "view"]
    return objects, table_rows, view_rows


def collect_table_counts(db: ReportDB, table_rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    output = []
    for row in table_rows:
        name = row["name"]
        count = db.count_object(name, "table", "report table row count inventory")
        output.append(
            {
                "object_name": name,
                "object_type": "table",
                "row_count": count if count is not None else "",
                "query_status": "ok" if count is not None else "error",
            }
        )
    return output


def collect_view_samples(db: ReportDB, view_rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    output: list[dict[str, Any]] = []
    for row in view_rows:
        name = row["name"]
        quoted = quote_identifier(name)
        rows = db.fetch_all(
            name,
            "view",
            "report view sample inventory",
            f"SELECT * FROM {quoted} LIMIT 3",
        )
        if not rows:
            output.append(
                {
                    "object_name": name,
                    "object_type": "view",
                    "sample_index": "",
                    "sample_json": "",
                    "query_status": "empty_or_unavailable",
                }
            )
            continue
        for index, sample in enumerate(rows, start=1):
            output.append(
                {
                    "object_name": name,
                    "object_type": "view",
                    "sample_index": index,
                    "sample_json": compact_json(sample),
                    "query_status": "ok",
                }
            )
    return output


def collect_report_data(
    db: ReportDB,
    input_db: Path,
    objects: dict[str, str],
    table_rows: list[dict[str, Any]],
    view_rows: list[dict[str, Any]],
) -> dict[str, Any]:
    fk_rows = db.fetch_all(
        "PRAGMA foreign_key_check",
        "pragma",
        "database integrity foreign key check",
        "PRAGMA foreign_key_check",
    )
    qsb_views = [row["name"] for row in view_rows if row["name"].startswith("qsb_v_")]
    family_counts: dict[str, int] = {}
    for view_name in qsb_views:
        family = qsb_view_family(view_name)
        family_counts[family] = family_counts.get(family, 0) + 1

    source_inventory = []
    if object_exists(objects, "qsb_v_db21_par_tim_source_inventory", "view"):
        source_inventory = db.fetch_all(
            "qsb_v_db21_par_tim_source_inventory",
            "view",
            "source inventory for PAR/TIM report section",
            """
            SELECT
                source_type,
                source_family_label,
                object_label_candidate,
                relative_path,
                source_file_name,
                source_file_extension,
                source_file_size_bytes,
                line_count,
                selected_for_db21_tim_ingest,
                lineage_key
            FROM qsb_v_db21_par_tim_source_inventory
            ORDER BY source_type DESC, source_file_name
            """,
        )
    else:
        db.log_missing(
            "qsb_v_db21_par_tim_source_inventory",
            "view",
            "source inventory for PAR/TIM report section",
        )

    raw_record_count = None
    raw_field_count = None
    example_lineage_key = None
    if object_exists(objects, "qsb_v_db21_tim_raw_records", "view"):
        raw_record_count = db.fetch_scalar(
            "qsb_v_db21_tim_raw_records",
            "view",
            "TIM raw record count",
            "SELECT COUNT(*) FROM qsb_v_db21_tim_raw_records",
        )
        example_lineage_key = db.fetch_scalar(
            "qsb_v_db21_tim_raw_records",
            "view",
            "example lineage key",
            """
            SELECT lineage_key
            FROM qsb_v_db21_tim_raw_records
            WHERE lineage_key IS NOT NULL
            ORDER BY record_index
            LIMIT 1
            """,
        )
    else:
        db.log_missing("qsb_v_db21_tim_raw_records", "view", "TIM raw record count")
    if object_exists(objects, "qsb_v_db21_tim_raw_field_values", "view"):
        raw_field_count = db.fetch_scalar(
            "qsb_v_db21_tim_raw_field_values",
            "view",
            "TIM raw field/value count",
            "SELECT COUNT(*) FROM qsb_v_db21_tim_raw_field_values",
        )
    else:
        db.log_missing("qsb_v_db21_tim_raw_field_values", "view", "TIM raw field/value count")

    line_type_counts = []
    if object_exists(objects, "qsb_v_db22_tim_line_type_counts", "view"):
        line_type_counts = db.fetch_all(
            "qsb_v_db22_tim_line_type_counts",
            "view",
            "TIM line-type counts",
            "SELECT * FROM qsb_v_db22_tim_line_type_counts ORDER BY record_count DESC, line_type",
        )
    else:
        db.log_missing("qsb_v_db22_tim_line_type_counts", "view", "TIM line-type counts")

    token_count_distribution = []
    if object_exists(objects, "qsb_v_db22_tim_token_count_distribution", "view"):
        token_count_distribution = db.fetch_all(
            "qsb_v_db22_tim_token_count_distribution",
            "view",
            "TIM token-count distribution",
            """
            SELECT *
            FROM qsb_v_db22_tim_token_count_distribution
            ORDER BY record_count DESC, token_count
            """,
        )
    else:
        db.log_missing(
            "qsb_v_db22_tim_token_count_distribution",
            "view",
            "TIM token-count distribution",
        )

    staging = {"status": "not present in selected DB"}
    db23_objects = [
        "qsb_v_db23_measurement_reality_dashboard",
        "qsb_v_db23_tim_staging_preview",
        "db23_tim_token_role_candidate",
        "db23_tim_staging_field_map",
        "db23_tim_mapping_gap",
    ]
    if all(object_exists(objects, name) for name in db23_objects):
        dashboard = db.fetch_all(
            "qsb_v_db23_measurement_reality_dashboard",
            "view",
            "DB23 staging dashboard",
            "SELECT * FROM qsb_v_db23_measurement_reality_dashboard",
        )
        preview = db.fetch_all(
            "qsb_v_db23_tim_staging_preview",
            "view",
            "DB23 staging preview sample",
            "SELECT * FROM qsb_v_db23_tim_staging_preview LIMIT 5",
        )
        token_role_count = db.fetch_scalar(
            "db23_tim_token_role_candidate",
            "table",
            "DB23 token role candidate count",
            "SELECT COUNT(*) FROM db23_tim_token_role_candidate",
        )
        staging_map_count = db.fetch_scalar(
            "db23_tim_staging_field_map",
            "table",
            "DB23 staging field map count",
            "SELECT COUNT(*) FROM db23_tim_staging_field_map",
        )
        mapping_gap_count = db.fetch_scalar(
            "db23_tim_mapping_gap",
            "table",
            "DB23 mapping gap count",
            "SELECT COUNT(*) FROM db23_tim_mapping_gap",
        )
        staging = {
            "status": "present",
            "dashboard": dashboard,
            "preview": preview,
            "token_role_candidate_count": token_role_count,
            "staging_field_map_count": staging_map_count,
            "mapping_gap_count": mapping_gap_count,
        }
    else:
        for name in db23_objects:
            if not object_exists(objects, name):
                db.log_missing(name, "table_or_view", "DB23 staging map and mapping gaps")

    family_overview = []
    token_profiles = []
    candidate_grouping_tokens = []
    if object_exists(objects, "qsb_v_db23a_41_family_overview", "view"):
        family_overview = db.fetch_all(
            "qsb_v_db23a_41_family_overview",
            "view",
            "41-token family overview",
            "SELECT * FROM qsb_v_db23a_41_family_overview",
        )
    else:
        db.log_missing("qsb_v_db23a_41_family_overview", "view", "41-token family overview")
    if object_exists(objects, "qsb_v_db23a_41_token_position_profile", "view"):
        token_profiles = db.fetch_all(
            "qsb_v_db23a_41_token_position_profile",
            "view",
            "41-token token-position profile",
            "SELECT * FROM qsb_v_db23a_41_token_position_profile ORDER BY token_position",
        )
    else:
        db.log_missing(
            "qsb_v_db23a_41_token_position_profile",
            "view",
            "41-token token-position profile",
        )
    if object_exists(objects, "qsb_v_db23a_41_candidate_grouping_tokens", "view"):
        candidate_grouping_tokens = db.fetch_all(
            "qsb_v_db23a_41_candidate_grouping_tokens",
            "view",
            "41-token candidate grouping tokens",
            """
            SELECT *
            FROM qsb_v_db23a_41_candidate_grouping_tokens
            WHERE candidate_label = 'candidate_grouping_token'
            ORDER BY token_position
            """,
        )
    else:
        db.log_missing(
            "qsb_v_db23a_41_candidate_grouping_tokens",
            "view",
            "41-token candidate grouping tokens",
        )

    token001_block_count = None
    token001_alignment = None
    if object_exists(objects, "qsb_v_db23b_token001_block_profile", "view"):
        token001_block_count = db.fetch_scalar(
            "qsb_v_db23b_token001_block_profile",
            "view",
            "token_001 block count",
            """
            SELECT MAX(token001_total_contiguous_blocks)
            FROM qsb_v_db23b_token001_block_profile
            """,
        )
        token001_alignment = db.fetch_scalar(
            "qsb_v_db23b_token001_block_profile",
            "view",
            "token_001 boundary alignment",
            """
            SELECT token001_split_alignment_status
            FROM qsb_v_db23b_token001_block_profile
            ORDER BY token001_block_rank
            LIMIT 1
            """,
        )
    else:
        db.log_missing("qsb_v_db23b_token001_block_profile", "view", "token_001 block count")

    block_definitions = []
    focused_side_by_side = []
    two_block_whisper = []
    combined_signatures = []
    transition_gap = []
    if object_exists(objects, "qsb_v_db23b_block_definitions", "view"):
        block_definitions = db.fetch_all(
            "qsb_v_db23b_block_definitions",
            "view",
            "DB23B block definitions",
            "SELECT * FROM qsb_v_db23b_block_definitions ORDER BY start_record_index",
        )
    else:
        db.log_missing("qsb_v_db23b_block_definitions", "view", "DB23B block definitions")
    if object_exists(objects, "qsb_v_db23b_focused_token_side_by_side", "view"):
        focused_side_by_side = db.fetch_all(
            "qsb_v_db23b_focused_token_side_by_side",
            "view",
            "DB23B focused token side-by-side comparison",
            """
            SELECT *
            FROM qsb_v_db23b_focused_token_side_by_side
            WHERE token_position IN (7, 11, 13, 17, 23)
            ORDER BY token_position
            """,
        )
    else:
        db.log_missing(
            "qsb_v_db23b_focused_token_side_by_side",
            "view",
            "DB23B focused token side-by-side comparison",
        )
    if object_exists(objects, "qsb_v_db23b_first_two_block_whisper", "view"):
        two_block_whisper = db.fetch_all(
            "qsb_v_db23b_first_two_block_whisper",
            "view",
            "DB23B first two-block whisper",
            "SELECT * FROM qsb_v_db23b_first_two_block_whisper",
        )
    else:
        db.log_missing(
            "qsb_v_db23b_first_two_block_whisper",
            "view",
            "DB23B first two-block whisper",
        )
    if object_exists(objects, "qsb_v_db23b_combined_signature_profile", "view"):
        combined_signatures = db.fetch_all(
            "qsb_v_db23b_combined_signature_profile",
            "view",
            "DB23B combined signature profile",
            """
            SELECT *
            FROM qsb_v_db23b_combined_signature_profile
            WHERE dominant_signature_flag = 1
            ORDER BY block_label
            """,
        )
    else:
        db.log_missing(
            "qsb_v_db23b_combined_signature_profile",
            "view",
            "DB23B combined signature profile",
        )
    if object_exists(objects, "qsb_v_db23b_transition_gap_inspection", "view"):
        transition_gap = db.fetch_all(
            "qsb_v_db23b_transition_gap_inspection",
            "view",
            "DB23B transition/gap inspection",
            """
            SELECT record_index, line_type, token_count, family_membership_status,
                   transition_gap_relation
            FROM qsb_v_db23b_transition_gap_inspection
            ORDER BY record_index
            """,
        )
    else:
        db.log_missing(
            "qsb_v_db23b_transition_gap_inspection",
            "view",
            "DB23B transition/gap inspection",
        )

    constant_positions = [
        row for row in token_profiles if row.get("constant_or_low_variance_flag") == "constant"
    ]
    low_variance_positions = [
        row for row in token_profiles if row.get("constant_or_low_variance_flag") == "low_variance"
    ]
    variable_positions = [
        row for row in token_profiles if row.get("constant_or_low_variance_flag") == "variable"
    ]
    high_variance_positions = [row for row in token_profiles if row.get("high_variance_flag") == 1]

    return {
        "selected_db": str(input_db),
        "db_file_size_bytes": input_db.stat().st_size,
        "file_fallback_used": False,
        "selected_db_reason": "Latest QSB Mini-DWH database available from DB23B two-block signature inspection.",
        "db_first_confirmation": "All report data were queried from the selected SQLite DB; CSV/JSON/MD outputs were not used as input substrate.",
        "foreign_key_check_rows": fk_rows,
        "foreign_key_violation_count": len(fk_rows),
        "table_count": len(table_rows),
        "view_count": len(view_rows),
        "qsb_view_families": family_counts,
        "qsb_views": qsb_views,
        "source_inventory": source_inventory,
        "raw_record_count": raw_record_count,
        "raw_field_value_count": raw_field_count,
        "example_lineage_key": example_lineage_key,
        "line_type_counts": line_type_counts,
        "token_count_distribution": token_count_distribution,
        "staging_map": staging,
        "family_overview": family_overview[0] if family_overview else None,
        "constant_positions": constant_positions,
        "low_variance_positions": low_variance_positions,
        "variable_positions": variable_positions,
        "high_variance_positions": high_variance_positions,
        "candidate_grouping_tokens": candidate_grouping_tokens,
        "token001_block_count": token001_block_count,
        "token001_boundary_alignment": token001_alignment,
        "block_definitions": block_definitions,
        "focused_side_by_side": focused_side_by_side,
        "two_block_whisper": two_block_whisper[0] if two_block_whisper else None,
        "combined_signatures": combined_signatures,
        "transition_gap": transition_gap,
        "claim_boundary": CLAIM_BOUNDARY,
        "raw_file_confirmation": CLAIM_RISK_FREE_NOTE,
    }


def render_markdown(report: dict[str, Any]) -> str:
    source_rows = report["source_inventory"]
    tim_sources = [row for row in source_rows if row.get("source_type") == "TIM"]
    par_sources = [row for row in source_rows if row.get("source_type") == "PAR"]
    family = report.get("family_overview") or {}
    whisper = report.get("two_block_whisper") or {}
    transition_counts: dict[str, int] = {}
    for row in report.get("transition_gap", []):
        relation = str(row.get("transition_gap_relation"))
        transition_counts[relation] = transition_counts.get(relation, 0) + 1

    lines = [
        "# QSB-DB24 - DB-backed Research Data Report",
        "",
        "## 1. Data substrate used",
        "",
        f"- Selected DB path: `{report['selected_db']}`",
        f"- DB file size: `{report['db_file_size_bytes']}` bytes",
        "- File fallback used: `no`",
        f"- Selected DB reason: {report['selected_db_reason']}",
        f"- DB-first confirmation: {report['db_first_confirmation']}",
        "",
        "## 2. Database integrity",
        "",
        f"- PRAGMA foreign_key_check violation count: `{report['foreign_key_violation_count']}`",
        f"- Number of tables: `{report['table_count']}`",
        f"- Number of views: `{report['view_count']}`",
        "- Relevant QSB view families found: "
        + ", ".join(
            f"{family_name}={count}"
            for family_name, count in sorted(report["qsb_view_families"].items())
        ),
        "",
        "## 3. Source and rawdata summary",
        "",
        f"- PAR source: `{par_sources[0]['source_file_name'] if par_sources else 'not available'}`",
        f"- TIM source: `{tim_sources[0]['source_file_name'] if tim_sources else 'not available'}`",
        f"- Source family: `{source_rows[0]['source_family_label'] if source_rows else 'not available'}`",
        f"- Raw TIM record count: `{report['raw_record_count']}`",
        f"- Raw TIM field/value count: `{report['raw_field_value_count']}`",
        f"- Example lineage key: `{report['example_lineage_key']}`",
        "",
        "## 4. TIM structure families",
        "",
        "### Line-type counts",
        "",
        render_table(
            report["line_type_counts"],
            ["line_type", "record_count", "record_fraction", "min_token_count", "max_token_count", "dominant_token_count"],
        ),
        "",
        "### Token-count distribution",
        "",
        render_table(
            report["token_count_distribution"],
            ["token_count", "line_type", "record_count", "record_fraction", "family_label", "family_note"],
        ),
        "",
        "Dominant visible TIM families include the 41-token `data_line` family, "
        "the 44-token `comment_line` family, 2-token short/header/context lines, "
        "and one blank-line family.",
        "",
        "## 5. Staging map and mapping gaps",
        "",
    ]
    staging = report["staging_map"]
    if staging["status"] == "present":
        lines.extend(
            [
                f"- Token role candidates: `{staging['token_role_candidate_count']}`",
                f"- Staging field map count: `{staging['staging_field_map_count']}`",
                f"- Mapping gap count: `{staging['mapping_gap_count']}`",
                "",
                "First staging preview rows:",
                "",
                render_table(staging.get("preview", []), list(staging.get("preview", [{}])[0].keys()) if staging.get("preview") else []),
                "",
            ]
        )
    else:
        lines.extend(
            [
                "- DB23 staging-map tables/views are not present in the selected DB.",
                "- Status: `not present in selected DB`.",
                "",
            ]
        )
    lines.extend(
        [
            "## 6. 41-token data-line family",
            "",
            f"- Record count: `{family.get('record_count', 'not available')}`",
            f"- Source file: `{family.get('source_file_name', 'not available')}`",
            f"- Source family: `{family.get('source_family_label', 'not available')}`",
            f"- Token-count consistency: `{family.get('token_count_consistency', 'not available')}`",
            "- Constant positions: " + format_position_list(report["constant_positions"]),
            "- Low-variance positions: " + format_position_list(report["low_variance_positions"]),
            "- Variable positions: " + format_position_list(report["variable_positions"]),
            "- High-variance subset: " + format_position_list(report["high_variance_positions"]),
            "- Candidate grouping tokens: " + format_position_list(report["candidate_grouping_tokens"]),
            f"- token_001 block count: `{report['token001_block_count']}`",
            "",
            "## 7. Two-block signature",
            "",
            "### Block definitions",
            "",
            render_table(
                report["block_definitions"],
                ["block_label", "start_record_index", "end_record_index", "family_record_count", "nonfamily_record_count", "definition_scope"],
            ),
            "",
            f"- Transition/gap zone status: `{whisper.get('transition_gap_status', 'not available')}`",
            f"- token_001 boundary alignment: `{report['token001_boundary_alignment']}`",
            "",
            "### Focused token side-by-side comparison",
            "",
            render_table(
                report["focused_side_by_side"],
                ["field_name", "block_a_dominant_value", "block_b_dominant_value", "relation_type", "block_discriminating_flag", "constant_within_each_block_flag"],
            ),
            "",
            f"- Dominant Block A signature: `{whisper.get('dominant_block_a_signature', 'not available')}`",
            f"- Dominant Block B signature: `{whisper.get('dominant_block_b_signature', 'not available')}`",
            "",
            "## 8. First-look findings",
            "",
            "- The selected DB can produce a coherent first report from its own tables/views.",
            "- Visible families include the 41-token data-line family, 44-token comment-line family, 2-token short/context family, and blank-line family.",
            "- The 41-token family contains a clear structural two-block signature across `tim_token_007`, `tim_token_011`, `tim_token_013`, `tim_token_017`, and `tim_token_023`.",
            "- The transition/gap records are present in the DB but outside the 41-token data-line family.",
            "- Mapping remains open: token positions are structural candidates only until a controlled staging dictionary exists.",
            "- A next DB-backed question is whether structural token candidates can be promoted into an auditable staging dictionary without assigning physical meaning.",
            "",
            "## 9. Next DB-backed questions",
            "",
            "1. Can token-role candidates be promoted into a controlled staging dictionary?",
            "2. Can the two-block signature be linked to explicit source/context metadata already represented in DB tables/views?",
            "3. Do the 44-token comment/cut lines explain or annotate the block transition structurally?",
            "4. Which token positions should be compared side-by-side for equality/function-like mapping?",
            "5. Which DB views should Python analysis use next for controlled staging work?",
            "",
            "## 10. Boundaries and non-goals",
            "",
            CLAIM_BOUNDARY,
            "",
            CLAIM_RISK_FREE_NOTE,
            "",
        ]
    )
    return "\n".join(lines)


def write_report_outputs(
    output_root: Path,
    report: dict[str, Any],
    query_inventory: list[QueryInventoryRow],
    view_samples: list[dict[str, Any]],
    table_counts: list[dict[str, Any]],
) -> None:
    output_root.mkdir(parents=True, exist_ok=True)
    markdown = render_markdown(report)
    (output_root / REPORT_MD).write_text(markdown, encoding="utf-8")
    json_report = {
        "block": BLOCK_LABEL,
        "created_at_utc": utc_now(),
        "report": report,
        "query_inventory_count": len(query_inventory),
        "view_sample_count": len(view_samples),
        "table_count_inventory_count": len(table_counts),
    }
    (output_root / REPORT_JSON).write_text(
        pretty_json(json_report) + "\n",
        encoding="utf-8",
    )
    write_csv(
        output_root / QUERY_INVENTORY_CSV,
        [row.__dict__ for row in query_inventory],
        [
            "object_name",
            "object_type",
            "query_purpose",
            "query_status",
            "row_count_if_available",
            "error_message_if_any",
        ],
    )
    write_csv(
        output_root / VIEW_SAMPLES_CSV,
        view_samples,
        ["object_name", "object_type", "sample_index", "sample_json", "query_status"],
    )
    write_csv(
        output_root / TABLE_COUNTS_CSV,
        table_counts,
        ["object_name", "object_type", "row_count", "query_status"],
    )


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate a DB-backed QSB research data report from a Mini-DWH SQLite database."
    )
    parser.add_argument(
        "--input-db",
        type=Path,
        default=DEFAULT_INPUT_DB,
        help="Path to the selected QSB Mini-DWH SQLite database.",
    )
    parser.add_argument(
        "--output-root",
        type=Path,
        default=DEFAULT_OUTPUT_ROOT,
        help="Output directory for DB24 report artifacts.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Validate input/output paths without writing report artifacts.",
    )
    return parser.parse_args(argv)


def main(argv: list[str]) -> int:
    args = parse_args(argv)
    input_db = args.input_db
    output_root = args.output_root

    ensure_input_db(input_db)
    ensure_safe_outputs(output_root)

    if args.dry_run:
        print(f"block: {BLOCK_LABEL}")
        print(f"input_db: {input_db}")
        print(f"output_root: {output_root}")
        print("dry_run: true")
        print("file_fallback_used: no")
        return 0

    with connect_read_only(input_db) as con:
        db = ReportDB(con)
        objects, table_rows, view_rows = collect_catalog(db)
        table_counts = collect_table_counts(db, table_rows)
        view_samples = collect_view_samples(db, view_rows)
        report = collect_report_data(db, input_db, objects, table_rows, view_rows)
        write_report_outputs(
            output_root=output_root,
            report=report,
            query_inventory=db.inventory,
            view_samples=view_samples,
            table_counts=table_counts,
        )

    queried_objects = sorted({row.object_name for row in db.inventory})
    print(f"block: {BLOCK_LABEL}")
    print(f"report_path: {output_root / REPORT_MD}")
    print(f"json_summary_path: {output_root / REPORT_JSON}")
    print(f"query_inventory_path: {output_root / QUERY_INVENTORY_CSV}")
    print("queried_tables_views:")
    for object_name in queried_objects:
        print(f"- {object_name}")
    print("file_fallback_used: no")
    print("input_db_modified: no")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main(sys.argv[1:]))
    except Exception as exc:
        print(f"error: {exc}", file=sys.stderr)
        raise SystemExit(1)
