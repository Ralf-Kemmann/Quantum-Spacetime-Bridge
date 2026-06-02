#!/usr/bin/env python3
"""QSB-DB28: external dictionary evidence seed.

This DB-first consolidated Mini-DWH step uses the existing DB25/DB26/DB27
SQLite database as the primary data substrate. It creates a timestamped backup
before writing, adds only DB28-prefixed tables and views, and writes DB-backed
report exports. The default and first-run mode is no live external retrieval:
entries are seeded from DR01 guidance and marked for later external
verification.
"""

from __future__ import annotations

import argparse
import csv
import json
import shutil
import sqlite3
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


SCRIPT_NAME = "scripts/qsb_db28_external_dictionary_evidence_seed.py"
DEFAULT_DB = Path(
    "runs/QSB-DB/QSB_DB25_CONSOLIDATED_RESEARCH_SNAPSHOT/"
    "qsb_research_consolidated_snapshot.db"
)
DEFAULT_OUTPUT_ROOT = Path("runs/QSB-DB/QSB_DB25_CONSOLIDATED_RESEARCH_SNAPSHOT")

REQUIRED_VIEWS = [
    "qsb_v_db27_first_mapping_work_packet",
    "qsb_v_db27_mapping_review_decision_seed",
    "qsb_v_db27_next_mapping_questions",
    "qsb_v_db26_side_by_side_block_token_context",
    "qsb_v_db25_report_ready_snapshot",
]

OUTPUT_FILENAMES = [
    "db28_external_dictionary_evidence_seed_readout.md",
    "db28_external_dictionary_evidence_seed_summary.json",
    "db28_external_source_registry.csv",
    "db28_dictionary_seed.csv",
    "db28_mapping_assertion_evidence.csv",
    "db28_db27_token_evidence_link.csv",
]

FOCUS_TOKENS = [
    "tim_token_007",
    "tim_token_011",
    "tim_token_013",
    "tim_token_017",
    "tim_token_023",
]

CLAIM_BOUNDARY = (
    "DB28 is an additive external-dictionary evidence seed over the consolidated "
    "DB25/DB26/DB27 SQLite database. It records DR01/manual external source "
    "candidates and evidence gaps only. It does not read raw TIM/PAR files, "
    "does not ingest large external payloads, does not compute timing or model "
    "quantities, does not canonicalize numeric tokens, and does not assign final "
    "physical or semantic meaning to TIM columns."
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


def list_db28_objects(con: sqlite3.Connection) -> list[tuple[str, str]]:
    rows = con.execute(
        """
        SELECT type, name
        FROM sqlite_master
        WHERE name LIKE 'db28_%'
           OR name LIKE 'qsb_v_db28_%'
        ORDER BY type, name
        """
    ).fetchall()
    return [(str(row["type"]), str(row["name"])) for row in rows]


def ensure_preconditions(db_path: Path, output_root: Path) -> None:
    if not db_path.exists():
        raise FileNotFoundError(f"Consolidated database does not exist: {db_path}")
    if not db_path.is_file():
        raise ValueError(f"Consolidated DB path is not a file: {db_path}")
    if not output_root.exists():
        raise FileNotFoundError(f"Output root does not exist: {output_root}")
    if not output_root.is_dir():
        raise ValueError(f"Output root is not a directory: {output_root}")
    if db_path.parent.resolve() != output_root.resolve():
        raise ValueError("Output root must be the consolidated snapshot directory.")
    if db_path.stat().st_size <= 0:
        raise ValueError(f"Consolidated DB is empty: {db_path}")

    with connect_readonly(db_path) as con:
        missing_views = [
            view for view in REQUIRED_VIEWS
            if not object_exists(con, view, "view")
        ]
        if missing_views:
            raise RuntimeError("Required view(s) missing: " + ", ".join(missing_views))
        existing_db28 = list_db28_objects(con)
        if existing_db28:
            formatted = ", ".join(f"{kind}:{name}" for kind, name in existing_db28)
            raise RuntimeError("Refusing to run because DB28 objects already exist: " + formatted)

    existing_outputs = [
        str(path) for path in output_paths(output_root).values()
        if path.exists()
    ]
    if existing_outputs:
        raise FileExistsError(
            "Refusing to overwrite existing DB28 output file(s): "
            + "; ".join(existing_outputs)
        )


def create_backup(db_path: Path) -> Path:
    backup_path = db_path.with_name(
        f"{db_path.stem}.pre_db28_{timestamp_for_path()}.bak.db"
    )
    if backup_path.exists():
        raise FileExistsError(f"Backup path already exists: {backup_path}")
    shutil.copy2(db_path, backup_path)
    return backup_path


def create_tables_and_views(con: sqlite3.Connection) -> None:
    con.executescript(
        """
        CREATE TABLE db28_external_dictionary_run_log (
            run_id TEXT PRIMARY KEY,
            run_timestamp_utc TEXT,
            input_db_path TEXT,
            backup_db_path TEXT,
            script_name TEXT,
            operation_mode TEXT,
            live_external_retrieval_performed INTEGER,
            row_count_inserted INTEGER,
            foreign_key_violation_count INTEGER,
            notes TEXT,
            CHECK (live_external_retrieval_performed IN (0, 1))
        );

        CREATE TABLE db28_external_source_registry (
            source_id TEXT PRIMARY KEY,
            source_name TEXT,
            institution TEXT,
            source_type TEXT,
            official_url TEXT,
            access_method TEXT,
            relevance_class TEXT,
            tier TEXT,
            retrieval_status TEXT,
            citation_or_license_note TEXT,
            created_at_utc TEXT
        );

        CREATE TABLE db28_external_dictionary_seed (
            dictionary_seed_id TEXT PRIMARY KEY,
            source_id TEXT,
            entity_type TEXT,
            raw_term TEXT,
            candidate_canonical_term TEXT,
            evidence_status TEXT,
            assertion_status TEXT,
            evidence_summary TEXT,
            confidence_class TEXT,
            manual_review_required INTEGER,
            created_at_utc TEXT,
            FOREIGN KEY (source_id) REFERENCES db28_external_source_registry(source_id),
            CHECK (manual_review_required IN (0, 1))
        );

        CREATE TABLE db28_telescope_dictionary_seed (
            telescope_seed_id TEXT PRIMARY KEY,
            source_id TEXT,
            raw_telescope_name TEXT,
            candidate_canonical_name TEXT,
            alias_or_short_name TEXT,
            evidence_status TEXT,
            created_at_utc TEXT,
            FOREIGN KEY (source_id) REFERENCES db28_external_source_registry(source_id)
        );

        CREATE TABLE db28_receiver_dictionary_seed (
            receiver_seed_id TEXT PRIMARY KEY,
            source_id TEXT,
            raw_receiver_name TEXT,
            candidate_canonical_name TEXT,
            telescope_context TEXT,
            frequency_low_mhz REAL,
            frequency_high_mhz REAL,
            evidence_status TEXT,
            assertion_status TEXT,
            manual_review_required INTEGER,
            created_at_utc TEXT,
            FOREIGN KEY (source_id) REFERENCES db28_external_source_registry(source_id),
            CHECK (manual_review_required IN (0, 1))
        );

        CREATE TABLE db28_backend_dictionary_seed (
            backend_seed_id TEXT PRIMARY KEY,
            source_id TEXT,
            raw_backend_name TEXT,
            candidate_canonical_name TEXT,
            telescope_context TEXT,
            evidence_status TEXT,
            assertion_status TEXT,
            manual_review_required INTEGER,
            created_at_utc TEXT,
            FOREIGN KEY (source_id) REFERENCES db28_external_source_registry(source_id),
            CHECK (manual_review_required IN (0, 1))
        );

        CREATE TABLE db28_mapping_assertion_evidence (
            assertion_id TEXT PRIMARY KEY,
            related_token_position TEXT,
            raw_value_or_term TEXT,
            proposed_mapping_scope TEXT,
            source_id TEXT,
            evidence_status TEXT,
            assertion_status TEXT,
            evidence_summary TEXT,
            evidence_ref TEXT,
            review_status TEXT,
            created_at_utc TEXT,
            FOREIGN KEY (source_id) REFERENCES db28_external_source_registry(source_id)
        );

        CREATE TABLE db28_db27_token_evidence_link (
            link_id TEXT PRIMARY KEY,
            token_position TEXT,
            db27_work_packet_token TEXT,
            block_a_value TEXT,
            block_b_value TEXT,
            linked_evidence_terms TEXT,
            evidence_status TEXT,
            mapping_readiness TEXT,
            recommended_next_action TEXT,
            created_at_utc TEXT
        );

        CREATE TABLE db28_external_retrieval_log (
            retrieval_id TEXT PRIMARY KEY,
            source_id TEXT,
            retrieval_timestamp_utc TEXT,
            retrieval_method TEXT,
            retrieval_url TEXT,
            retrieval_status TEXT,
            retrieved_row_count INTEGER,
            content_hash_sha256 TEXT,
            notes TEXT,
            FOREIGN KEY (source_id) REFERENCES db28_external_source_registry(source_id)
        );

        CREATE TABLE db28_open_external_evidence_gap (
            gap_id TEXT PRIMARY KEY,
            related_token_position TEXT,
            raw_value_or_term TEXT,
            gap_type TEXT,
            gap_severity TEXT,
            required_external_source TEXT,
            blocking_status TEXT,
            recommended_next_action TEXT,
            created_at_utc TEXT
        );

        CREATE VIEW qsb_v_db28_external_source_registry AS
        SELECT *
        FROM db28_external_source_registry
        ORDER BY tier, source_name;

        CREATE VIEW qsb_v_db28_dictionary_seed AS
        SELECT *
        FROM db28_external_dictionary_seed
        ORDER BY entity_type, raw_term;

        CREATE VIEW qsb_v_db28_receiver_backend_seed AS
        SELECT 'receiver' AS seed_family,
               receiver_seed_id AS seed_id,
               raw_receiver_name AS raw_name,
               candidate_canonical_name,
               telescope_context,
               frequency_low_mhz,
               frequency_high_mhz,
               evidence_status,
               assertion_status,
               manual_review_required,
               source_id,
               created_at_utc
        FROM db28_receiver_dictionary_seed
        UNION ALL
        SELECT 'backend' AS seed_family,
               backend_seed_id AS seed_id,
               raw_backend_name AS raw_name,
               candidate_canonical_name,
               telescope_context,
               NULL AS frequency_low_mhz,
               NULL AS frequency_high_mhz,
               evidence_status,
               assertion_status,
               manual_review_required,
               source_id,
               created_at_utc
        FROM db28_backend_dictionary_seed
        ORDER BY seed_family, raw_name;

        CREATE VIEW qsb_v_db28_mapping_assertion_evidence AS
        SELECT *
        FROM db28_mapping_assertion_evidence
        ORDER BY related_token_position, raw_value_or_term;

        CREATE VIEW qsb_v_db28_db27_token_evidence_link AS
        SELECT *
        FROM db28_db27_token_evidence_link
        ORDER BY token_position;

        CREATE VIEW qsb_v_db28_external_evidence_gap AS
        SELECT *
        FROM db28_open_external_evidence_gap
        ORDER BY
            CASE gap_severity
                WHEN 'high' THEN 1
                WHEN 'medium' THEN 2
                ELSE 3
            END,
            related_token_position,
            raw_value_or_term;

        CREATE VIEW qsb_v_db28_dictionary_evidence_dashboard AS
        SELECT 'run_id' AS metric_name,
               run_id AS metric_value,
               'db28_external_dictionary_run_log' AS metric_source,
               notes AS dashboard_note
        FROM db28_external_dictionary_run_log
        UNION ALL
        SELECT 'live_external_retrieval_performed',
               CAST(live_external_retrieval_performed AS TEXT),
               'db28_external_dictionary_run_log',
               '1 means live external retrieval occurred; 0 means DR01/no-live seed mode.'
        FROM db28_external_dictionary_run_log
        UNION ALL
        SELECT 'external_source_registry_rows',
               CAST(COUNT(*) AS TEXT),
               'db28_external_source_registry',
               'External source families registered for later verification.'
        FROM db28_external_source_registry
        UNION ALL
        SELECT 'dictionary_seed_rows',
               CAST(COUNT(*) AS TEXT),
               'db28_external_dictionary_seed',
               'Conservative dictionary/evidence seed rows.'
        FROM db28_external_dictionary_seed
        UNION ALL
        SELECT 'receiver_seed_rows',
               CAST(COUNT(*) AS TEXT),
               'db28_receiver_dictionary_seed',
               'Receiver seed rows requiring external verification.'
        FROM db28_receiver_dictionary_seed
        UNION ALL
        SELECT 'backend_seed_rows',
               CAST(COUNT(*) AS TEXT),
               'db28_backend_dictionary_seed',
               'Backend seed rows requiring external verification.'
        FROM db28_backend_dictionary_seed
        UNION ALL
        SELECT 'mapping_assertion_evidence_rows',
               CAST(COUNT(*) AS TEXT),
               'db28_mapping_assertion_evidence',
               'Evidence candidate rows linked to DB27 tokens.'
        FROM db28_mapping_assertion_evidence
        UNION ALL
        SELECT 'db27_token_evidence_link_rows',
               CAST(COUNT(*) AS TEXT),
               'db28_db27_token_evidence_link',
               'Token-level links from DB27 work packet to DB28 evidence terms.'
        FROM db28_db27_token_evidence_link
        UNION ALL
        SELECT 'open_external_evidence_gap_rows',
               CAST(COUNT(*) AS TEXT),
               'db28_open_external_evidence_gap',
               'Open external evidence gaps before controlled definitions.'
        FROM db28_open_external_evidence_gap
        UNION ALL
        SELECT 'foreign_key_violation_count',
               CAST(foreign_key_violation_count AS TEXT),
               'PRAGMA foreign_key_check',
               'SQLite foreign-key check result after DB28 insertions.'
        FROM db28_external_dictionary_run_log;

        CREATE VIEW qsb_v_db28_next_evidence_actions AS
        SELECT ROW_NUMBER() OVER (
                   ORDER BY
                       CASE gap_severity
                           WHEN 'high' THEN 1
                           WHEN 'medium' THEN 2
                           ELSE 3
                       END,
                       related_token_position,
                       raw_value_or_term
               ) AS action_rank,
               related_token_position,
               raw_value_or_term,
               gap_type,
               gap_severity,
               required_external_source,
               blocking_status,
               recommended_next_action
        FROM db28_open_external_evidence_gap;
        """
    )


def build_source_registry(created_at: str, no_live_retrieval: bool) -> list[dict[str, Any]]:
    retrieval_status = "dr01_report_seed" if no_live_retrieval else "needs_manual_retrieval"
    note = "DR01 source-family seed; live verification not performed in this run."
    rows = [
        ("db28_src_ipta_pod", "IPTA POD", "International Pulsar Timing Array", "archive", "https://ipta4gw.org/", "documentation/web", "dictionary", "tier_1"),
        ("db28_src_gbo_gbt", "GBO / GBT Receiver and Backend Documentation", "Green Bank Observatory", "documentation", "https://greenbankobservatory.org/", "documentation/web", "dictionary", "tier_1"),
        ("db28_src_psrfits_atnf", "PSRFITS Documentation / ATNF-related format documentation", "ATNF / CSIRO", "documentation", "https://www.atnf.csiro.au/research/pulsar/psrfits_definition/", "documentation/web", "dictionary", "tier_2"),
        ("db28_src_nanograv_docs", "NANOGrav documentation / glossary / public dataset documentation", "NANOGrav", "documentation", "https://nanograv.org/", "documentation/web", "dictionary", "tier_2"),
        ("db28_src_jpl_horizons", "JPL Horizons", "NASA/JPL", "api", "https://ssd.jpl.nasa.gov/horizons/", "REST/API", "context", "tier_3"),
        ("db28_src_iers_bipm", "IERS / BIPM", "IERS / BIPM", "time_context", "https://www.iers.org/; https://www.bipm.org/", "documentation/web", "context", "tier_3"),
        ("db28_src_gaia_archive", "Gaia Archive methodology", "ESA Gaia Archive", "methodology", "https://gea.esac.esa.int/archive/", "TAP/ADQL", "methodology", "low_relevance"),
        ("db28_src_cern_open_data", "CERN Open Data methodology", "CERN", "methodology", "https://opendata.cern.ch/", "documentation/web", "methodology", "low_relevance"),
    ]
    return [
        {
            "source_id": source_id,
            "source_name": source_name,
            "institution": institution,
            "source_type": source_type,
            "official_url": official_url,
            "access_method": access_method,
            "relevance_class": relevance_class,
            "tier": tier,
            "retrieval_status": retrieval_status,
            "citation_or_license_note": note,
            "created_at_utc": created_at,
        }
        for source_id, source_name, institution, source_type, official_url, access_method, relevance_class, tier in rows
    ]


def dictionary_seed_rows(created_at: str) -> list[dict[str, Any]]:
    rows = [
        ("db28_dict_001", "db28_src_gbo_gbt", "telescope", "GBT", "GBT", "dr01_report_seed", "seed_only", "DR01 guidance marks GBO/GBT documentation as the official source class for telescope context.", "medium", 1),
        ("db28_dict_002", "db28_src_gbo_gbt", "receiver", "Rcvr_800", "Rcvr_800", "dr01_report_seed", "candidate_mapping_evidence", "DR01 guidance identifies GBT receiver documentation as likely evidence for this raw receiver-like term.", "medium", 1),
        ("db28_dict_003", "db28_src_gbo_gbt", "receiver", "Rcvr1_2", "Rcvr1_2", "dr01_report_seed", "candidate_mapping_evidence", "DR01 guidance identifies GBT receiver documentation as likely evidence for this raw receiver-like term.", "medium", 1),
        ("db28_dict_004", "db28_src_gbo_gbt", "backend", "GUPPI", "GUPPI", "dr01_report_seed", "candidate_mapping_evidence", "DR01 guidance identifies GBO/GBT backend documentation as likely evidence for this backend-like term.", "medium", 1),
        ("db28_dict_005", "db28_src_nanograv_docs", "backend", "GASP", "GASP", "dr01_report_seed", "seed_only", "DR01 guidance indicates NANOGrav documentation may help with backend/use-context vocabulary.", "low", 1),
        ("db28_dict_006", "db28_src_gbo_gbt", "backend", "VEGAS", "VEGAS", "dr01_report_seed", "seed_only", "DR01 guidance indicates GBO/GBT documentation may help with backend vocabulary.", "low", 1),
        ("db28_dict_007", "db28_src_ipta_pod", "numeric_hypothesis", "3.125", "3.125", "open_mapping_hypothesis", "retained_as_open_hypothesis", "Numeric token retained as an open hypothesis; no canonical meaning assigned in DB28.", "low", 1),
        ("db28_dict_008", "db28_src_ipta_pod", "numeric_hypothesis", "12.5", "12.5", "open_mapping_hypothesis", "retained_as_open_hypothesis", "Numeric token retained as an open hypothesis; no canonical meaning assigned in DB28.", "low", 1),
        ("db28_dict_009", "db28_src_ipta_pod", "numeric_hypothesis", "2", "2", "open_mapping_hypothesis", "retained_as_open_hypothesis", "Numeric token retained as an open hypothesis; no canonical meaning assigned in DB28.", "low", 1),
        ("db28_dict_010", "db28_src_ipta_pod", "numeric_hypothesis", "8", "8", "open_mapping_hypothesis", "retained_as_open_hypothesis", "Numeric token retained as an open hypothesis; no canonical meaning assigned in DB28.", "low", 1),
    ]
    return [
        {
            "dictionary_seed_id": seed_id,
            "source_id": source_id,
            "entity_type": entity_type,
            "raw_term": raw_term,
            "candidate_canonical_term": canonical,
            "evidence_status": evidence_status,
            "assertion_status": assertion_status,
            "evidence_summary": evidence_summary,
            "confidence_class": confidence,
            "manual_review_required": manual_review,
            "created_at_utc": created_at,
        }
        for seed_id, source_id, entity_type, raw_term, canonical, evidence_status, assertion_status, evidence_summary, confidence, manual_review in rows
    ]


def telescope_seed_rows(created_at: str) -> list[dict[str, Any]]:
    return [
        {
            "telescope_seed_id": "db28_tel_001",
            "source_id": "db28_src_gbo_gbt",
            "raw_telescope_name": "GBT",
            "candidate_canonical_name": "GBT",
            "alias_or_short_name": "Green Bank Telescope",
            "evidence_status": "dr01_report_seed",
            "created_at_utc": created_at,
        }
    ]


def receiver_seed_rows(created_at: str) -> list[dict[str, Any]]:
    rows = [
        ("db28_recv_001", "Rcvr_800"),
        ("db28_recv_002", "Rcvr1_2"),
    ]
    return [
        {
            "receiver_seed_id": receiver_seed_id,
            "source_id": "db28_src_gbo_gbt",
            "raw_receiver_name": raw_receiver_name,
            "candidate_canonical_name": raw_receiver_name,
            "telescope_context": "GBT",
            "frequency_low_mhz": None,
            "frequency_high_mhz": None,
            "evidence_status": "dr01_report_seed",
            "assertion_status": "candidate_mapping_evidence",
            "manual_review_required": 1,
            "created_at_utc": created_at,
        }
        for receiver_seed_id, raw_receiver_name in rows
    ]


def backend_seed_rows(created_at: str) -> list[dict[str, Any]]:
    rows = [
        ("db28_backend_001", "GUPPI", "db28_src_gbo_gbt", "GBT", "candidate_mapping_evidence"),
        ("db28_backend_002", "GASP", "db28_src_nanograv_docs", "GBT", "seed_only"),
        ("db28_backend_003", "VEGAS", "db28_src_gbo_gbt", "GBT", "seed_only"),
    ]
    return [
        {
            "backend_seed_id": backend_seed_id,
            "source_id": source_id,
            "raw_backend_name": backend_name,
            "candidate_canonical_name": backend_name,
            "telescope_context": telescope_context,
            "evidence_status": "dr01_report_seed",
            "assertion_status": assertion_status,
            "manual_review_required": 1,
            "created_at_utc": created_at,
        }
        for backend_seed_id, backend_name, source_id, telescope_context, assertion_status in rows
    ]


def build_mapping_assertions(created_at: str) -> list[dict[str, Any]]:
    specs = [
        ("db28_assert_001", "tim_token_007", "Rcvr_800", "receiver", "db28_src_gbo_gbt", "dr01_report_seed", "candidate_mapping_evidence", "DR01 seed links Rcvr_800 to official GBT receiver documentation class; live verification remains open.", "DR01:GBT_receiver_backend_guidance"),
        ("db28_assert_002", "tim_token_007", "Rcvr1_2", "receiver", "db28_src_gbo_gbt", "dr01_report_seed", "candidate_mapping_evidence", "DR01 seed links Rcvr1_2 to official GBT receiver documentation class; live verification remains open.", "DR01:GBT_receiver_backend_guidance"),
        ("db28_assert_003", "tim_token_011", "Rcvr_800_GUPPI", "receiver/backend", "db28_src_gbo_gbt", "dr01_report_seed", "candidate_mapping_evidence", "Composite term contains receiver-like and backend-like components named in DR01 source guidance.", "DR01:GBT_receiver_backend_guidance"),
        ("db28_assert_004", "tim_token_011", "Rcvr1_2_GUPPI", "receiver/backend", "db28_src_gbo_gbt", "dr01_report_seed", "candidate_mapping_evidence", "Composite term contains receiver-like and backend-like components named in DR01 source guidance.", "DR01:GBT_receiver_backend_guidance"),
        ("db28_assert_005", "tim_token_017", "J0740+6620.Rcvr_800.GUPPI.12y.x.sum.sm", "composite_context", "db28_src_ipta_pod", "dr01_report_seed", "candidate_mapping_evidence", "Composite string contains receiver/backend terms and likely requires release metadata or header-level confirmation.", "DR01:IPTA_POD_first_seed_candidate"),
        ("db28_assert_006", "tim_token_017", "J0740+6620.Rcvr1_2.GUPPI.12y.x.sum.sm", "composite_context", "db28_src_ipta_pod", "dr01_report_seed", "candidate_mapping_evidence", "Composite string contains receiver/backend terms and likely requires release metadata or header-level confirmation.", "DR01:IPTA_POD_first_seed_candidate"),
        ("db28_assert_007", "tim_token_013", "3.125", "numeric_hypothesis", "db28_src_ipta_pod", "open_mapping_hypothesis", "retained_as_open_hypothesis", "Numeric token retained as an open mapping hypothesis pending metadata, header, or release-specific evidence.", "DR01:numeric_tokens_remain_hypotheses"),
        ("db28_assert_008", "tim_token_013", "12.5", "numeric_hypothesis", "db28_src_ipta_pod", "open_mapping_hypothesis", "retained_as_open_hypothesis", "Numeric token retained as an open mapping hypothesis pending metadata, header, or release-specific evidence.", "DR01:numeric_tokens_remain_hypotheses"),
        ("db28_assert_009", "tim_token_023", "2", "numeric_hypothesis", "db28_src_ipta_pod", "open_mapping_hypothesis", "retained_as_open_hypothesis", "Numeric token retained as an open mapping hypothesis pending metadata, header, or release-specific evidence.", "DR01:numeric_tokens_remain_hypotheses"),
        ("db28_assert_010", "tim_token_023", "8", "numeric_hypothesis", "db28_src_ipta_pod", "open_mapping_hypothesis", "retained_as_open_hypothesis", "Numeric token retained as an open mapping hypothesis pending metadata, header, or release-specific evidence.", "DR01:numeric_tokens_remain_hypotheses"),
    ]
    return [
        {
            "assertion_id": assertion_id,
            "related_token_position": token,
            "raw_value_or_term": term,
            "proposed_mapping_scope": scope,
            "source_id": source_id,
            "evidence_status": evidence_status,
            "assertion_status": assertion_status,
            "evidence_summary": summary,
            "evidence_ref": evidence_ref,
            "review_status": "needs_review",
            "created_at_utc": created_at,
        }
        for assertion_id, token, term, scope, source_id, evidence_status, assertion_status, summary, evidence_ref in specs
    ]


def build_token_links(
    con: sqlite3.Connection,
    created_at: str,
) -> list[dict[str, Any]]:
    work_packet_rows = fetch_dicts(
        con,
        """
        SELECT token_position, block_a_value, block_b_value
        FROM qsb_v_db27_first_mapping_work_packet
        ORDER BY token_position
        """
    )
    by_token = {row["token_position"]: row for row in work_packet_rows}
    missing = [token for token in FOCUS_TOKENS if token not in by_token]
    if missing:
        raise RuntimeError("DB27 work packet missing token(s): " + ", ".join(missing))

    link_specs = {
        "tim_token_007": ("Rcvr_800,Rcvr1_2", "dr01_report_seed", "needs_external_evidence", "Retrieve official GBT receiver documentation and confirm both raw receiver terms before controlled definition."),
        "tim_token_011": ("Rcvr_800,GUPPI,Rcvr1_2", "dr01_report_seed", "needs_external_evidence", "Confirm receiver/backend composite interpretation against official GBT/IPTA or release metadata."),
        "tim_token_013": ("3.125,12.5", "open_mapping_hypothesis", "open_hypothesis", "Locate release metadata or headers before assigning any controlled numeric meaning."),
        "tim_token_017": ("Rcvr_800,GUPPI,Rcvr1_2,composite_string_pattern", "dr01_report_seed", "needs_external_evidence", "Compare composite strings against IPTA POD or release-specific naming/header documentation."),
        "tim_token_023": ("2,8", "open_mapping_hypothesis", "open_hypothesis", "Locate release metadata or headers before assigning any controlled numeric meaning."),
    }
    rows: list[dict[str, Any]] = []
    for idx, token in enumerate(FOCUS_TOKENS, start=1):
        work = by_token[token]
        terms, evidence_status, readiness, next_action = link_specs[token]
        rows.append(
            {
                "link_id": f"db28_link_{idx:04d}",
                "token_position": token,
                "db27_work_packet_token": token,
                "block_a_value": work["block_a_value"],
                "block_b_value": work["block_b_value"],
                "linked_evidence_terms": terms,
                "evidence_status": evidence_status,
                "mapping_readiness": readiness,
                "recommended_next_action": next_action,
                "created_at_utc": created_at,
            }
        )
    return rows


def build_retrieval_log(
    sources: list[dict[str, Any]],
    created_at: str,
    no_live_retrieval: bool,
) -> list[dict[str, Any]]:
    method = "dr01_report_seed" if no_live_retrieval else "manual_seed"
    status = "not_attempted" if no_live_retrieval else "not_available"
    note = (
        "No live retrieval attempted because --no-live-retrieval was requested; "
        "source is registered as a DR01 report seed."
    )
    return [
        {
            "retrieval_id": f"db28_retrieval_{idx:03d}",
            "source_id": source["source_id"],
            "retrieval_timestamp_utc": created_at,
            "retrieval_method": method,
            "retrieval_url": source["official_url"],
            "retrieval_status": status,
            "retrieved_row_count": 0,
            "content_hash_sha256": None,
            "notes": note,
        }
        for idx, source in enumerate(sources, start=1)
    ]


def build_open_gaps(created_at: str) -> list[dict[str, Any]]:
    specs = [
        ("db28_gap_001", "tim_token_013", "3.125", "unclear_numeric_token", "high", "IPTA POD metadata, PSRFITS headers, or release-specific documentation", "blocks_controlled_definition", "Find concrete metadata/header evidence before assigning any dictionary meaning."),
        ("db28_gap_002", "tim_token_013", "12.5", "unclear_numeric_token", "high", "IPTA POD metadata, PSRFITS headers, or release-specific documentation", "blocks_controlled_definition", "Find concrete metadata/header evidence before assigning any dictionary meaning."),
        ("db28_gap_003", "tim_token_023", "2", "unclear_numeric_token", "high", "IPTA POD metadata, PSRFITS headers, or release-specific documentation", "blocks_controlled_definition", "Find concrete metadata/header evidence before assigning any dictionary meaning."),
        ("db28_gap_004", "tim_token_023", "8", "unclear_numeric_token", "high", "IPTA POD metadata, PSRFITS headers, or release-specific documentation", "blocks_controlled_definition", "Find concrete metadata/header evidence before assigning any dictionary meaning."),
        ("db28_gap_005", "tim_token_007", "Rcvr_800/Rcvr1_2", "missing_dictionary", "medium", "GBO / GBT receiver documentation", "blocks_controlled_definition", "Verify receiver terms against official GBT documentation before controlled naming."),
        ("db28_gap_006", "tim_token_011", "Rcvr_800_GUPPI/Rcvr1_2_GUPPI", "missing_dictionary", "medium", "GBO / GBT receiver/backend documentation and release metadata", "blocks_controlled_definition", "Verify receiver/backend composite terms before controlled naming."),
        ("db28_gap_007", "tim_token_017", "composite string pattern", "missing_release_metadata", "medium", "IPTA POD release metadata or headers", "blocks_controlled_definition", "Verify composite naming pattern against release-specific metadata before controlled naming."),
    ]
    return [
        {
            "gap_id": gap_id,
            "related_token_position": token,
            "raw_value_or_term": term,
            "gap_type": gap_type,
            "gap_severity": severity,
            "required_external_source": source,
            "blocking_status": blocking,
            "recommended_next_action": action,
            "created_at_utc": created_at,
        }
        for gap_id, token, term, gap_type, severity, source, blocking, action in specs
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
    live_external_retrieval_performed: int,
    fk_violations: list[sqlite3.Row],
) -> dict[str, Any]:
    db28_tables = [
        "db28_external_dictionary_run_log",
        "db28_external_source_registry",
        "db28_external_dictionary_seed",
        "db28_telescope_dictionary_seed",
        "db28_receiver_dictionary_seed",
        "db28_backend_dictionary_seed",
        "db28_mapping_assertion_evidence",
        "db28_db27_token_evidence_link",
        "db28_external_retrieval_log",
        "db28_open_external_evidence_gap",
    ]
    db28_views = [
        "qsb_v_db28_external_source_registry",
        "qsb_v_db28_dictionary_seed",
        "qsb_v_db28_receiver_backend_seed",
        "qsb_v_db28_mapping_assertion_evidence",
        "qsb_v_db28_db27_token_evidence_link",
        "qsb_v_db28_external_evidence_gap",
        "qsb_v_db28_dictionary_evidence_dashboard",
        "qsb_v_db28_next_evidence_actions",
    ]
    return {
        "run_id": run_id,
        "run_timestamp_utc": created_at,
        "data_substrate": str(db_path),
        "db25_db26_db27_updated_additively": True,
        "backup_db_path": str(backup_path),
        "live_external_retrieval_performed": bool(live_external_retrieval_performed),
        "new_isolated_analysis_db_created": False,
        "raw_tim_par_files_read": False,
        "script_name": SCRIPT_NAME,
        "claim_boundary": CLAIM_BOUNDARY,
        "db28_tables": db28_tables,
        "db28_views": db28_views,
        "row_counts": {table: table_count(con, table) for table in db28_tables},
        "source_registry_by_tier": counts_by(con, "db28_external_source_registry", "tier"),
        "source_registry_by_retrieval_status": counts_by(con, "db28_external_source_registry", "retrieval_status"),
        "dictionary_seed_by_entity_type": counts_by(con, "db28_external_dictionary_seed", "entity_type"),
        "dictionary_seed_by_evidence_status": counts_by(con, "db28_external_dictionary_seed", "evidence_status"),
        "mapping_assertion_by_status": counts_by(con, "db28_mapping_assertion_evidence", "evidence_status"),
        "open_gap_by_severity": counts_by(con, "db28_open_external_evidence_gap", "gap_severity"),
        "token_evidence_links": first_rows(con, "qsb_v_db28_db27_token_evidence_link", 10),
        "open_external_evidence_gaps": first_rows(con, "qsb_v_db28_external_evidence_gap", 20),
        "first_dashboard_rows": first_rows(con, "qsb_v_db28_dictionary_evidence_dashboard", 20),
        "foreign_key_violation_count": len(fk_violations),
        "output_files": {name: str(output_root / name) for name in OUTPUT_FILENAMES},
    }


def write_readout(path: Path, summary: dict[str, Any]) -> None:
    link_lines = [
        "- {token_position}: {block_a_value} -> {block_b_value}; terms={linked_evidence_terms}; readiness={mapping_readiness}".format(**row)
        for row in summary["token_evidence_links"]
    ]
    gap_lines = [
        "- {related_token_position}: {raw_value_or_term}; gap={gap_type}; source={required_external_source}".format(**row)
        for row in summary["open_external_evidence_gaps"]
    ]
    content = f"""# QSB-DB28 External Dictionary Evidence Seed

## Befund

- Data substrate: `{summary['data_substrate']}`
- DB25/DB26/DB27 update mode: additive in-place DB28 tables/views only
- Backup DB: `{summary['backup_db_path']}`
- Live external retrieval performed: {summary['live_external_retrieval_performed']}
- Source registry rows: {summary['row_counts']['db28_external_source_registry']}
- Dictionary seed rows: {summary['row_counts']['db28_external_dictionary_seed']}
- Mapping assertion evidence rows: {summary['row_counts']['db28_mapping_assertion_evidence']}
- DB27 token evidence links: {summary['row_counts']['db28_db27_token_evidence_link']}
- Open external evidence gaps: {summary['row_counts']['db28_open_external_evidence_gap']}
- FK violation count: {summary['foreign_key_violation_count']}

## Interpretation

DB28 registers external source families and conservative dictionary/evidence
seeds for DB27's first mapping work packet. Because this run used no live
external retrieval, source and term rows remain DR01/manual seeds or open
hypotheses and require later verification before controlled field definitions.

Dictionary seed counts by entity type:

```json
{pretty_json(summary['dictionary_seed_by_entity_type'])}
```

## Hypothese

The first useful external verification path is GBO/GBT documentation for
receiver/backend terms and IPTA POD or release-specific metadata for composite
strings and numeric tokens. This remains a mapping-work hypothesis only.

DB27 token evidence links:

{chr(10).join(link_lines)}

## Offene Luecke

Numeric values `3.125`, `12.5`, `2`, and `8` are retained as open evidence
gaps. DB28 does not canonicalize them.

Open evidence gaps:

{chr(10).join(gap_lines)}

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
    write_readout(paths["db28_external_dictionary_evidence_seed_readout.md"], summary)
    paths["db28_external_dictionary_evidence_seed_summary.json"].write_text(
        pretty_json(summary) + "\n",
        encoding="utf-8",
    )
    write_csv(con, paths["db28_external_source_registry.csv"], "qsb_v_db28_external_source_registry")
    write_csv(con, paths["db28_dictionary_seed.csv"], "qsb_v_db28_dictionary_seed")
    write_csv(con, paths["db28_mapping_assertion_evidence.csv"], "qsb_v_db28_mapping_assertion_evidence")
    write_csv(con, paths["db28_db27_token_evidence_link.csv"], "qsb_v_db28_db27_token_evidence_link")


def execute(db_path: Path, output_root: Path, no_live_retrieval: bool) -> dict[str, Any]:
    ensure_preconditions(db_path, output_root)
    backup_path = create_backup(db_path)
    created_at = utc_now()
    run_id = "DB28_EXTERNAL_DICTIONARY_EVIDENCE_SEED_" + timestamp_for_path()
    live_external_retrieval_performed = 0 if no_live_retrieval else 0

    with connect_db(db_path) as con:
        con.execute("BEGIN IMMEDIATE")
        try:
            create_tables_and_views(con)
            source_rows = build_source_registry(created_at, no_live_retrieval)
            dict_rows = dictionary_seed_rows(created_at)
            tel_rows = telescope_seed_rows(created_at)
            recv_rows = receiver_seed_rows(created_at)
            backend_rows = backend_seed_rows(created_at)
            assertion_rows = build_mapping_assertions(created_at)
            link_rows = build_token_links(con, created_at)
            retrieval_rows = build_retrieval_log(source_rows, created_at, no_live_retrieval)
            gap_rows = build_open_gaps(created_at)

            insert_rows(con, "db28_external_source_registry", source_rows)
            insert_rows(con, "db28_external_dictionary_seed", dict_rows)
            insert_rows(con, "db28_telescope_dictionary_seed", tel_rows)
            insert_rows(con, "db28_receiver_dictionary_seed", recv_rows)
            insert_rows(con, "db28_backend_dictionary_seed", backend_rows)
            insert_rows(con, "db28_mapping_assertion_evidence", assertion_rows)
            insert_rows(con, "db28_db27_token_evidence_link", link_rows)
            insert_rows(con, "db28_external_retrieval_log", retrieval_rows)
            insert_rows(con, "db28_open_external_evidence_gap", gap_rows)

            fk_violations = con.execute("PRAGMA foreign_key_check").fetchall()
            total_rows_inserted = (
                len(source_rows)
                + len(dict_rows)
                + len(tel_rows)
                + len(recv_rows)
                + len(backend_rows)
                + len(assertion_rows)
                + len(link_rows)
                + len(retrieval_rows)
                + len(gap_rows)
                + 1
            )
            con.execute(
                """
                INSERT INTO db28_external_dictionary_run_log (
                    run_id,
                    run_timestamp_utc,
                    input_db_path,
                    backup_db_path,
                    script_name,
                    operation_mode,
                    live_external_retrieval_performed,
                    row_count_inserted,
                    foreign_key_violation_count,
                    notes
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    run_id,
                    created_at,
                    str(db_path),
                    str(backup_path),
                    SCRIPT_NAME,
                    "DB-first consolidated in-place additive update",
                    live_external_retrieval_performed,
                    total_rows_inserted,
                    len(fk_violations),
                    "DB28 added only DB28-prefixed external dictionary evidence seed tables/views and report files.",
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
            live_external_retrieval_performed,
            fk_violations,
        )
        write_outputs(con, output_root, summary)
    return summary


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "QSB-DB28 external dictionary evidence seed over the existing "
            "DB25/DB26/DB27 consolidated SQLite database."
        )
    )
    parser.add_argument(
        "--db",
        type=Path,
        default=DEFAULT_DB,
        help="Path to the consolidated SQLite database.",
    )
    parser.add_argument(
        "--output-root",
        type=Path,
        default=DEFAULT_OUTPUT_ROOT,
        help="Existing consolidated output directory for DB28 reports and backup.",
    )
    parser.add_argument(
        "--no-live-retrieval",
        action="store_true",
        help="Do not perform live external retrieval; seed DR01/manual evidence rows only.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        summary = execute(args.db, args.output_root, args.no_live_retrieval)
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    print(pretty_json(summary))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
