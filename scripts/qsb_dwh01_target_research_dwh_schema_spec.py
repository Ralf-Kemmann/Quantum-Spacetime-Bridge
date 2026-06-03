#!/usr/bin/env python3
"""QSB-DWH01: target Research DWH schema specification.

This is a read-only architecture and specification step over the consolidated
QSB SQLite snapshot. It inspects SQLite metadata and current table row counts
only. It does not read raw TIM/PAR files, does not use generated report
artifacts as input, does not create a separate database, does not modify the
input database, and does not calculate physical, model, residual, delay, TOA,
or statistical quantities.
"""

from __future__ import annotations

import argparse
import csv
import json
import re
import sqlite3
import sys
from collections import Counter, defaultdict
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


SCRIPT_NAME = "scripts/qsb_dwh01_target_research_dwh_schema_spec.py"
DEFAULT_DB = Path(
    "runs/QSB-DB/QSB_DB25_CONSOLIDATED_RESEARCH_SNAPSHOT/"
    "qsb_research_consolidated_snapshot.db"
)
DEFAULT_OUTPUT_ROOT = Path("runs/QSB-DB/QSB_DB25_CONSOLIDATED_RESEARCH_SNAPSHOT")

SPEC_MD = "dwh01_target_research_dwh_schema_spec.md"
SPEC_JSON = "dwh01_target_research_dwh_schema_spec.json"
TABLE_DESIGN_CSV = "dwh01_target_table_design.csv"
FIELD_CATALOG_CSV = "dwh01_target_field_catalog.csv"
PK_FK_DESIGN_CSV = "dwh01_target_pk_fk_design.csv"
CURRENT_TO_TARGET_CSV = "dwh01_current_to_target_mapping.csv"
ERD_SLICE_CSV = "dwh01_erd_slice_plan.csv"
MIGRATION_PHASE_CSV = "dwh01_migration_phase_plan.csv"
ADR_MD = "dwh01_architecture_decision_record.md"

OUTPUT_FILENAMES = [
    SPEC_MD,
    SPEC_JSON,
    TABLE_DESIGN_CSV,
    FIELD_CATALOG_CSV,
    PK_FK_DESIGN_CSV,
    CURRENT_TO_TARGET_CSV,
    ERD_SLICE_CSV,
    MIGRATION_PHASE_CSV,
    ADR_MD,
]

TARGET_ARCHITECTURE = (
    "Observation-centered modified star/snowflake architecture with "
    "Bridge/Result layer and Audit/Provenance sidecar"
)

RECOMMENDED_NEXT_STEP = (
    "Create an implementation DDL proposal for Phase 0 and Phase 1 only: "
    "freeze the current snapshot, create a backup/workcopy, then add the first "
    "audit schema-version and migration-log tables in a controlled migration."
)

CLAIM_BOUNDARY = (
    "DWH01 is a target schema specification only. It inspects current SQLite "
    "schema metadata and table row counts from the consolidated snapshot. It "
    "does not test a Bridge relation, calculate physical quantities, infer "
    "final TIM semantics, evaluate relation outcomes, or make "
    "physical-interpretation claims."
)

LAYER_ORDER = [
    "Raw / Entrance Layer",
    "Core / Observation-Centered Layer",
    "Dimensions / Context Layer",
    "Mapping / Evidence Layer",
    "Observation / Signal Fact Layer",
    "Bridge / Connection Layer",
    "Result / Evaluation Layer",
    "Audit / Provenance Sidecar",
    "Report / View Layer",
]


@dataclass(frozen=True)
class TargetField:
    field_name: str
    field_type: str
    field_role: str
    nullable: str
    field_description: str
    source_field_or_rule: str
    data_quality_rule: str
    claim_boundary_note: str


@dataclass(frozen=True)
class TargetTable:
    target_table_name: str
    layer: str
    purpose: str
    grain: str
    primary_key: str
    natural_key_candidate: str
    source_from_current_db: str
    migration_strategy: str
    implementation_priority: str
    notes: str
    fields: tuple[TargetField, ...]


@dataclass(frozen=True)
class TargetFk:
    source_table: str
    source_field: str
    target_table: str
    target_field: str
    relation_type: str
    mandatory: str
    index_recommended: str
    relationship_description: str
    erd_slice: str


@dataclass(frozen=True)
class ErdSlice:
    erd_slice_id: str
    erd_slice_name: str
    included_tables: str
    included_views: str
    main_question_answered: str
    intended_audience: str
    export_priority: str
    notes: str


@dataclass(frozen=True)
class MigrationPhase:
    phase_id: str
    phase_name: str
    phase_goal: str
    writes_db: str
    requires_backup: str
    input_objects: str
    output_objects: str
    validation_checks: str
    rollback_plan: str
    risk_level: str
    notes: str


def utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def pretty_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=True, indent=2)


def quote_identifier(identifier: str) -> str:
    return '"' + identifier.replace('"', '""') + '"'


def field(
    field_name: str,
    field_type: str,
    field_role: str,
    nullable: str,
    field_description: str,
    source_field_or_rule: str,
    data_quality_rule: str,
    claim_boundary_note: str = "Schema/governance field; no relation test is performed here.",
) -> TargetField:
    return TargetField(
        field_name=field_name,
        field_type=field_type,
        field_role=field_role,
        nullable=nullable,
        field_description=field_description,
        source_field_or_rule=source_field_or_rule,
        data_quality_rule=data_quality_rule,
        claim_boundary_note=claim_boundary_note,
    )


def fk(
    source_table: str,
    source_field: str,
    target_table: str,
    target_field: str,
    relation_type: str,
    mandatory: str,
    relationship_description: str,
    erd_slice: str,
    index_recommended: str = "yes",
) -> TargetFk:
    return TargetFk(
        source_table=source_table,
        source_field=source_field,
        target_table=target_table,
        target_field=target_field,
        relation_type=relation_type,
        mandatory=mandatory,
        index_recommended=index_recommended,
        relationship_description=relationship_description,
        erd_slice=erd_slice,
    )


def table(
    target_table_name: str,
    layer: str,
    purpose: str,
    grain: str,
    primary_key: str,
    natural_key_candidate: str,
    source_from_current_db: str,
    migration_strategy: str,
    implementation_priority: str,
    notes: str,
    fields: list[TargetField],
) -> TargetTable:
    return TargetTable(
        target_table_name=target_table_name,
        layer=layer,
        purpose=purpose,
        grain=grain,
        primary_key=primary_key,
        natural_key_candidate=natural_key_candidate,
        source_from_current_db=source_from_current_db,
        migration_strategy=migration_strategy,
        implementation_priority=implementation_priority,
        notes=notes,
        fields=tuple(fields),
    )


def build_target_tables() -> list[TargetTable]:
    claim = "Must preserve DWH01 boundary: design metadata only; no physical result is asserted."
    unresolved = "Unresolved numeric or semantic tokens remain text/status until reviewed."
    return [
        table(
            "raw_source_file",
            "Raw / Entrance Layer",
            "Registers files or file-like payloads at the entrance boundary.",
            "One row per source file or payload reference.",
            "source_file_id",
            "source_registry_id + source_path + checksum_sha256",
            "Current raw/source/file inventory tables and source-path fields.",
            "migrate_to_target_table",
            "P2",
            "Keep large payloads outside analytic facts; store path, URI, and checksum references.",
            [
                field("source_file_id", "TEXT", "primary_key", "no", "Stable project identifier for the file reference.", "Generated during migration.", "Unique, non-empty, immutable.", claim),
                field("source_registry_id", "TEXT", "foreign_key", "yes", "Owning source registry entry.", "Derived from source/source_family fields.", "Must reference core_source_registry when known.", claim),
                field("source_path", "TEXT", "lineage_attribute", "no", "Repository-relative or external path/URI for the source artifact.", "Current source path or file name fields.", "Non-empty; preserve original spelling.", claim),
                field("source_basename", "TEXT", "descriptor", "yes", "Basename extracted for browsing and diagnostics.", "Derived from source_path.", "May be regenerated from source_path.", claim),
                field("source_family", "TEXT", "classification", "yes", "Raw source family label such as PAR, TIM, report, or derived inventory.", "Current family/source-type fields.", "Use controlled family values when available.", claim),
                field("file_format", "TEXT", "classification", "yes", "Detected or declared source format.", "Current file extension and ingest metadata.", "Do not infer final semantics from extension alone.", claim),
                field("checksum_sha256", "TEXT", "lineage_attribute", "yes", "Checksum reference for rebuild and parity checks.", "Checksum fields when present; otherwise future rebuild control.", "64 hex characters when populated.", claim),
                field("file_size_bytes", "INTEGER", "lineage_attribute", "yes", "Byte length of referenced payload.", "Current file metadata when present.", "Non-negative integer.", claim),
                field("detected_at_utc", "TEXT", "audit_timestamp", "yes", "UTC timestamp when the file was detected or registered.", "Current ingest/run metadata.", "ISO-8601 UTC text.", claim),
                field("ingest_run_id", "TEXT", "foreign_key", "yes", "Raw ingest run that registered this file.", "Current run-log metadata.", "Must reference raw_ingest_run when known.", claim),
                field("audit_run_id", "TEXT", "foreign_key", "yes", "Audit run that created or migrated the registry row.", "Migration audit run.", "Must reference audit_run.", claim),
                field("lineage_note", "TEXT", "note", "yes", "Free-text lineage note for unresolved source details.", "Migration note.", "No scientific interpretation in this note.", claim),
            ],
        ),
        table(
            "raw_ingest_run",
            "Raw / Entrance Layer",
            "Captures raw entrance or import runs without changing source meaning.",
            "One row per raw ingest or import run.",
            "ingest_run_id",
            "script_id + started_at_utc + input_root_ref",
            "Current DB20/DB21 ingest and run-log style metadata.",
            "migrate_to_target_table",
            "P2",
            "Connects raw entrance objects to audit governance.",
            [
                field("ingest_run_id", "TEXT", "primary_key", "no", "Stable identifier for the ingest run.", "Generated during migration.", "Unique, non-empty.", claim),
                field("audit_run_id", "TEXT", "foreign_key", "yes", "Audit sidecar run for this ingest.", "Migration audit run.", "Must reference audit_run when available.", claim),
                field("script_id", "TEXT", "foreign_key", "yes", "Script that performed the ingest or import.", "Current run-log/script fields.", "Must reference audit_script when available.", claim),
                field("source_registry_id", "TEXT", "foreign_key", "yes", "Primary source registry entry for the run.", "Current source family metadata.", "Must reference core_source_registry when known.", claim),
                field("input_root_ref", "TEXT", "lineage_attribute", "yes", "Path or URI root used by the ingest run.", "Current run configuration.", "Store reference, not payload.", claim),
                field("started_at_utc", "TEXT", "audit_timestamp", "yes", "Run start time in UTC.", "Current run-log timestamps.", "ISO-8601 UTC text.", claim),
                field("completed_at_utc", "TEXT", "audit_timestamp", "yes", "Run completion time in UTC.", "Current run-log timestamps.", "ISO-8601 UTC text.", claim),
                field("operation_mode", "TEXT", "classification", "no", "Mode label such as read-only, migrate, or rebuild.", "Current script/run metadata.", "Controlled mode values.", claim),
                field("record_count", "INTEGER", "measure_count", "yes", "Number of raw records registered by the run.", "Current row counts or run logs.", "Non-negative integer.", claim),
                field("warning_count", "INTEGER", "measure_count", "yes", "Number of warnings emitted by the run.", "Current run logs.", "Non-negative integer.", claim),
                field("stop_reason", "TEXT", "audit_status", "yes", "Reason the run stopped.", "Current run logs.", "Required for interrupted or bounded runs.", claim),
            ],
        ),
        table(
            "raw_record",
            "Raw / Entrance Layer",
            "Stores line/record-level raw references for lineage.",
            "One row per source-local raw record.",
            "raw_record_id",
            "source_file_id + source_local_record_id or record_index",
            "Current DB20/DB21 raw record tables.",
            "migrate_to_target_table",
            "P2",
            "Raw text is referenced or stored only as source text; analytic meaning remains separate.",
            [
                field("raw_record_id", "TEXT", "primary_key", "no", "Stable identifier for a source-local raw record.", "Generated during migration.", "Unique, non-empty.", claim),
                field("source_file_id", "TEXT", "foreign_key", "no", "Source file containing the record.", "Current source file fields.", "Must reference raw_source_file.", claim),
                field("ingest_run_id", "TEXT", "foreign_key", "yes", "Ingest run that created the raw record row.", "Current ingest metadata.", "Must reference raw_ingest_run when known.", claim),
                field("source_local_record_id", "TEXT", "lineage_attribute", "yes", "Identifier used in the source or staging table.", "Current record_id fields.", "Preserve source-local value.", claim),
                field("record_index", "INTEGER", "lineage_attribute", "yes", "Zero- or one-based record order as preserved from source.", "Current record_index or line_number fields.", "Do not reinterpret order without source rule.", claim),
                field("line_number", "INTEGER", "lineage_attribute", "yes", "Line number when available.", "Current line_number fields.", "Positive integer when populated.", claim),
                field("raw_line_type", "TEXT", "classification", "yes", "Source-local line type or block label.", "Current line_type fields.", "Controlled only after mapping review.", claim),
                field("raw_text_ref", "TEXT", "payload_reference", "yes", "Raw text or reference to raw text storage.", "Current raw line text fields.", "Preserve verbatim if stored.", claim),
                field("record_hash", "TEXT", "lineage_attribute", "yes", "Hash of source-local record content.", "Future rebuild control or current hash.", "Stable for unchanged raw text.", claim),
                field("parse_status_id", "TEXT", "foreign_key", "yes", "Quality status of the parsed raw record.", "Current parse/status fields.", "Must reference dim_quality_status when known.", claim),
                field("audit_run_id", "TEXT", "foreign_key", "yes", "Audit run that created or migrated the row.", "Migration audit run.", "Must reference audit_run.", claim),
            ],
        ),
        table(
            "raw_field_value",
            "Raw / Entrance Layer",
            "Captures source-local field/token values before semantic commitment.",
            "One row per field value within a raw record.",
            "raw_field_value_id",
            "raw_record_id + field_position + field_name_source",
            "Current raw field/token tables and DB23/DB26 token inventories.",
            "migrate_to_target_table",
            "P2",
            "Unresolved numeric tokens remain raw text until reviewed.",
            [
                field("raw_field_value_id", "TEXT", "primary_key", "no", "Stable identifier for a raw field value.", "Generated during migration.", "Unique, non-empty.", claim),
                field("raw_record_id", "TEXT", "foreign_key", "no", "Raw record containing the field value.", "Current raw record joins.", "Must reference raw_record.", claim),
                field("field_position", "INTEGER", "lineage_attribute", "yes", "Source-local token or field position.", "Current token_position or field_index fields.", "Non-negative integer when populated.", unresolved),
                field("field_name_source", "TEXT", "lineage_attribute", "yes", "Source-local field name when available.", "Current field_name fields.", "Preserve source spelling.", unresolved),
                field("raw_value_text", "TEXT", "raw_value", "yes", "Verbatim source-local value text.", "Current raw value fields.", "No numeric canonicalization in DWH01.", unresolved),
                field("raw_value_type_hint", "TEXT", "classification", "yes", "Non-binding type hint observed during ingest.", "Current token type/status fields.", "Hint only; not final meaning.", unresolved),
                field("token_dictionary_id", "TEXT", "foreign_key", "yes", "Reviewed dictionary token, if one exists.", "DB26/DB27/DB28 mapping outputs.", "Must reference map_token_dictionary when assigned.", unresolved),
                field("value_hash", "TEXT", "lineage_attribute", "yes", "Hash of raw_value_text for parity checks.", "Future rebuild control.", "Stable for unchanged text.", claim),
                field("quality_status_id", "TEXT", "foreign_key", "yes", "Quality/review status for the value.", "Current mapping status fields.", "Must reference dim_quality_status when known.", claim),
                field("audit_run_id", "TEXT", "foreign_key", "yes", "Audit run that created or migrated the row.", "Migration audit run.", "Must reference audit_run.", claim),
            ],
        ),
        table(
            "core_source_registry",
            "Core / Observation-Centered Layer",
            "Conformed registry of source systems, authorities, and source families.",
            "One row per stable source system or source authority.",
            "source_registry_id",
            "source_name + source_type + source_uri",
            "Current source family, source registry, and DB28 external-source metadata.",
            "migrate_to_target_table",
            "P2",
            "Separates source authority from individual files.",
            [
                field("source_registry_id", "TEXT", "primary_key", "no", "Stable identifier for a source registry entry.", "Generated during migration.", "Unique, non-empty.", claim),
                field("source_name", "TEXT", "descriptor", "no", "Human-readable source name.", "Current source_name/source_label fields.", "Non-empty.", claim),
                field("source_type", "TEXT", "classification", "no", "Source type such as raw archive, staging DB, external registry, or report source.", "Current source_type fields.", "Controlled vocabulary.", claim),
                field("source_authority", "TEXT", "descriptor", "yes", "Institutional or project authority for the source.", "Current source metadata.", "Use explicit unknown status when not available.", claim),
                field("source_uri", "TEXT", "lineage_attribute", "yes", "Path, URI, or database object reference.", "Current path/URI fields.", "Store reference only.", claim),
                field("source_family", "TEXT", "classification", "yes", "Conformed family label used for migration routing.", "Classified from current object names and metadata.", "Controlled family values.", claim),
                field("access_method", "TEXT", "classification", "yes", "How the source is accessed for rebuild.", "Current source metadata or future manifest.", "Controlled values such as local_path, sqlite, uri.", claim),
                field("license_note", "TEXT", "note", "yes", "License or usage note when relevant.", "DB28 external source fields when present.", "No payload copied into note.", claim),
                field("active_from_utc", "TEXT", "audit_timestamp", "yes", "Start of source validity period.", "Current run/source metadata.", "ISO-8601 UTC text.", claim),
                field("active_to_utc", "TEXT", "audit_timestamp", "yes", "End of source validity period, if retired.", "Future governance control.", "ISO-8601 UTC text or NULL.", claim),
                field("audit_run_id", "TEXT", "foreign_key", "yes", "Audit run that created or migrated the source registry row.", "Migration audit run.", "Must reference audit_run.", claim),
            ],
        ),
        table(
            "core_dataset",
            "Core / Observation-Centered Layer",
            "Defines stable datasets and snapshots used by observations.",
            "One row per dataset snapshot or version.",
            "dataset_id",
            "source_registry_id + dataset_name + dataset_version",
            "Current DB25 snapshot metadata and source/run tables.",
            "migrate_to_target_table",
            "P2",
            "Dataset is the join point between source provenance and observations.",
            [
                field("dataset_id", "TEXT", "primary_key", "no", "Stable identifier for a dataset snapshot.", "Generated during migration.", "Unique, non-empty.", claim),
                field("source_registry_id", "TEXT", "foreign_key", "no", "Source registry that owns the dataset.", "Current source metadata.", "Must reference core_source_registry.", claim),
                field("dataset_name", "TEXT", "descriptor", "no", "Dataset name.", "Current DB/block labels.", "Non-empty.", claim),
                field("dataset_version", "TEXT", "descriptor", "yes", "Version or snapshot label.", "Current run/snapshot metadata.", "Preserve exact label.", claim),
                field("snapshot_label", "TEXT", "descriptor", "yes", "Project snapshot label.", "DB25 snapshot label when available.", "Preserve exact label.", claim),
                field("snapshot_path", "TEXT", "lineage_attribute", "yes", "Path to the snapshot database or manifest.", "Input DB path or manifest reference.", "Store reference only.", claim),
                field("checksum_manifest_ref", "TEXT", "lineage_attribute", "yes", "Reference to checksum manifest.", "Future rebuild manifest.", "Manifest must be immutable once accepted.", claim),
                field("created_at_utc", "TEXT", "audit_timestamp", "yes", "Dataset creation or snapshot time.", "Current snapshot/run metadata.", "ISO-8601 UTC text.", claim),
                field("dataset_scope", "TEXT", "classification", "yes", "Scope such as raw contact, staging, consolidation, mapping, evidence, or bridge design.", "Classified from current object names.", "Controlled vocabulary.", claim),
                field("audit_run_id", "TEXT", "foreign_key", "yes", "Audit run that created or migrated the dataset row.", "Migration audit run.", "Must reference audit_run.", claim),
            ],
        ),
        table(
            "core_observation",
            "Core / Observation-Centered Layer",
            "Central real-world anchor for observation-centered joins.",
            "One row per observation candidate or reviewed observation.",
            "observation_id",
            "dataset_id + source_observation_key",
            "Current raw/staging observation-like rows, source keys, and mapping worklists.",
            "migrate_to_target_table",
            "P3",
            "Every applicable fact, mapping route, bridge candidate, and result row should connect here.",
            [
                field("observation_id", "TEXT", "primary_key", "no", "Stable identifier for an observation anchor.", "Generated during migration.", "Unique, non-empty.", claim),
                field("dataset_id", "TEXT", "foreign_key", "no", "Dataset containing the observation.", "Current source/dataset metadata.", "Must reference core_dataset.", claim),
                field("science_object_id", "TEXT", "foreign_key", "yes", "Observed science object, when reviewed.", "Current object/source token mappings.", "Must reference dim_science_object when assigned.", unresolved),
                field("time_context_id", "TEXT", "foreign_key", "yes", "Conformed time context.", "Current time-like token mappings.", "Must reference dim_time_context when assigned.", unresolved),
                field("telescope_id", "TEXT", "foreign_key", "yes", "Conformed telescope context.", "Current telescope-like token mappings.", "Must reference dim_telescope when assigned.", unresolved),
                field("receiver_id", "TEXT", "foreign_key", "yes", "Conformed receiver context.", "Current receiver-like token mappings.", "Must reference dim_receiver when assigned.", unresolved),
                field("backend_id", "TEXT", "foreign_key", "yes", "Conformed backend context.", "Current backend-like token mappings.", "Must reference dim_backend when assigned.", unresolved),
                field("processing_context_id", "TEXT", "foreign_key", "yes", "Conformed processing context.", "Current run/script/config metadata.", "Must reference dim_processing_context when assigned.", claim),
                field("quality_status_id", "TEXT", "foreign_key", "yes", "Observation-level quality status.", "Current review/status fields.", "Must reference dim_quality_status.", claim),
                field("source_observation_key", "TEXT", "lineage_attribute", "yes", "Source-local key or composite lineage key.", "Current lineage and record keys.", "Preserve exact source value.", claim),
                field("observation_label", "TEXT", "descriptor", "yes", "Human-readable observation label.", "Derived from source context.", "No scientific outcome text.", claim),
                field("observation_start_raw", "TEXT", "raw_value", "yes", "Raw start-time token/text, if present.", "Current raw/mapping fields.", "Do not canonicalize in DWH01.", unresolved),
                field("observation_end_raw", "TEXT", "raw_value", "yes", "Raw end-time token/text, if present.", "Current raw/mapping fields.", "Do not canonicalize in DWH01.", unresolved),
                field("observation_status", "TEXT", "classification", "no", "Lifecycle status for the observation anchor.", "Migration/review decision.", "Controlled values such as candidate, reviewed, blocked.", claim),
                field("audit_run_id", "TEXT", "foreign_key", "yes", "Audit run that created or migrated the observation row.", "Migration audit run.", "Must reference audit_run.", claim),
                field("claim_boundary_id", "TEXT", "foreign_key", "yes", "Claim boundary governing the observation row.", "DWH claim-boundary catalog.", "Must reference audit_claim_boundary when assigned.", claim),
            ],
        ),
        table(
            "core_observation_record_link",
            "Core / Observation-Centered Layer",
            "Connects observation anchors to raw records and mapping decisions.",
            "One row per observation-to-raw-record link.",
            "observation_record_link_id",
            "observation_id + raw_record_id + link_role",
            "Current joins between raw records, staged tokens, and mapping work packets.",
            "migrate_to_target_table",
            "P3",
            "Keeps many-to-many source lineage explicit instead of hiding it in facts.",
            [
                field("observation_record_link_id", "TEXT", "primary_key", "no", "Stable identifier for the observation-record link.", "Generated during migration.", "Unique, non-empty.", claim),
                field("observation_id", "TEXT", "foreign_key", "no", "Observation anchor.", "Future migration join.", "Must reference core_observation.", claim),
                field("raw_record_id", "TEXT", "foreign_key", "no", "Raw record linked to the observation.", "Current raw record identifiers.", "Must reference raw_record.", claim),
                field("link_role", "TEXT", "classification", "no", "Role of the raw record in the observation bundle.", "Current line/block type and review status.", "Controlled vocabulary.", unresolved),
                field("link_confidence_status", "TEXT", "classification", "no", "Review status of the link.", "DB26/DB27 review fields.", "Controlled values; no numeric confidence implied.", claim),
                field("created_by_review_decision_id", "TEXT", "foreign_key", "yes", "Review decision that accepted or queued the link.", "Current mapping decision/worklist data.", "Must reference map_review_decision when present.", claim),
                field("audit_run_id", "TEXT", "foreign_key", "yes", "Audit run that created or migrated the link.", "Migration audit run.", "Must reference audit_run.", claim),
                field("notes", "TEXT", "note", "yes", "Lineage note for non-obvious links.", "Migration note.", "No relation outcome text.", claim),
            ],
        ),
        table(
            "dim_science_object",
            "Dimensions / Context Layer",
            "Conformed science-object dimension for observation context.",
            "One row per reviewed object identity or unresolved object candidate.",
            "science_object_id",
            "object_name + catalog_identifier",
            "Current object-like tokens and DB28 external source seeds.",
            "migrate_to_target_table",
            "P4",
            "Supports context joins without assigning unsupported meanings.",
            [
                field("science_object_id", "TEXT", "primary_key", "no", "Stable identifier for a science object dimension member.", "Generated during migration.", "Unique, non-empty.", claim),
                field("source_registry_id", "TEXT", "foreign_key", "yes", "Source registry supporting the object entry.", "Current source/evidence fields.", "Must reference core_source_registry when known.", claim),
                field("object_name", "TEXT", "descriptor", "no", "Object name or candidate label.", "Current object/name tokens.", "Non-empty; preserve unresolved status.", unresolved),
                field("object_alias", "TEXT", "descriptor", "yes", "Alias or alternate label.", "Current mapping or external source fields.", "Do not merge aliases without review.", unresolved),
                field("object_type", "TEXT", "classification", "yes", "Object type label.", "Current token role/evidence fields.", "Controlled only after review.", unresolved),
                field("catalog_identifier", "TEXT", "lineage_attribute", "yes", "External catalog identifier when supported.", "DB28 external evidence source fields.", "Source and identifier must be paired.", claim),
                field("external_source_id", "TEXT", "foreign_key", "yes", "External evidence source for the dimension row.", "DB28 external source registry.", "Must reference map_external_source when present.", claim),
                field("evidence_status_id", "TEXT", "foreign_key", "yes", "Evidence quality/status for the dimension row.", "Current evidence/review statuses.", "Must reference dim_quality_status.", claim),
                field("audit_run_id", "TEXT", "foreign_key", "yes", "Audit run that created or migrated the row.", "Migration audit run.", "Must reference audit_run.", claim),
                field("notes", "TEXT", "note", "yes", "Context note for unresolved identity details.", "Migration/review note.", "No physical outcome text.", claim),
            ],
        ),
        table(
            "dim_telescope",
            "Dimensions / Context Layer",
            "Conformed telescope dimension.",
            "One row per telescope or unresolved telescope candidate.",
            "telescope_id",
            "telescope_name + site_name",
            "Current telescope-like tokens and evidence seeds.",
            "migrate_to_target_table",
            "P4",
            "Instrument identity remains reviewable and source-linked.",
            [
                field("telescope_id", "TEXT", "primary_key", "no", "Stable identifier for a telescope dimension member.", "Generated during migration.", "Unique, non-empty.", claim),
                field("telescope_name", "TEXT", "descriptor", "no", "Telescope name or candidate label.", "Current instrument tokens.", "Non-empty.", unresolved),
                field("site_name", "TEXT", "descriptor", "yes", "Site name.", "Current source/evidence fields.", "Review before conformance.", unresolved),
                field("institution", "TEXT", "descriptor", "yes", "Institution or operator label.", "External source or current metadata.", "Source-linked when populated.", claim),
                field("location_label", "TEXT", "descriptor", "yes", "Non-coordinate location label.", "External source or current metadata.", "Do not derive coordinates in DWH01.", claim),
                field("external_source_id", "TEXT", "foreign_key", "yes", "External source supporting the telescope row.", "DB28 external source registry.", "Must reference map_external_source when present.", claim),
                field("evidence_status_id", "TEXT", "foreign_key", "yes", "Evidence status for the row.", "Current evidence/review statuses.", "Must reference dim_quality_status.", claim),
                field("audit_run_id", "TEXT", "foreign_key", "yes", "Audit run that created or migrated the row.", "Migration audit run.", "Must reference audit_run.", claim),
                field("notes", "TEXT", "note", "yes", "Context note for unresolved instrument details.", "Migration/review note.", "No relation outcome text.", claim),
            ],
        ),
        table(
            "dim_receiver",
            "Dimensions / Context Layer",
            "Conformed receiver dimension.",
            "One row per receiver/configuration candidate.",
            "receiver_id",
            "telescope_id + receiver_name + configuration_label",
            "Current receiver-like tokens and evidence seeds.",
            "migrate_to_target_table",
            "P4",
            "Snowflakes receiver context under telescope where known.",
            [
                field("receiver_id", "TEXT", "primary_key", "no", "Stable identifier for a receiver dimension member.", "Generated during migration.", "Unique, non-empty.", claim),
                field("telescope_id", "TEXT", "foreign_key", "yes", "Parent telescope when known.", "Current instrument context.", "Must reference dim_telescope when assigned.", unresolved),
                field("receiver_name", "TEXT", "descriptor", "no", "Receiver name or candidate label.", "Current receiver-like tokens.", "Non-empty.", unresolved),
                field("band_label", "TEXT", "descriptor", "yes", "Receiver band label.", "Current token/evidence fields.", "Review before conformance.", unresolved),
                field("configuration_label", "TEXT", "descriptor", "yes", "Receiver configuration label.", "Current token/evidence fields.", "Preserve exact source label.", unresolved),
                field("external_source_id", "TEXT", "foreign_key", "yes", "External source supporting the receiver row.", "DB28 external source registry.", "Must reference map_external_source when present.", claim),
                field("evidence_status_id", "TEXT", "foreign_key", "yes", "Evidence status for the row.", "Current evidence/review statuses.", "Must reference dim_quality_status.", claim),
                field("audit_run_id", "TEXT", "foreign_key", "yes", "Audit run that created or migrated the row.", "Migration audit run.", "Must reference audit_run.", claim),
                field("notes", "TEXT", "note", "yes", "Context note for unresolved receiver details.", "Migration/review note.", "No relation outcome text.", claim),
            ],
        ),
        table(
            "dim_backend",
            "Dimensions / Context Layer",
            "Conformed backend/instrument-processing dimension.",
            "One row per backend/configuration candidate.",
            "backend_id",
            "backend_name + configuration_label",
            "Current backend-like tokens and processing metadata.",
            "migrate_to_target_table",
            "P4",
            "Keeps instrument acquisition context separate from processing context.",
            [
                field("backend_id", "TEXT", "primary_key", "no", "Stable identifier for a backend dimension member.", "Generated during migration.", "Unique, non-empty.", claim),
                field("backend_name", "TEXT", "descriptor", "no", "Backend name or candidate label.", "Current backend-like tokens.", "Non-empty.", unresolved),
                field("backend_type", "TEXT", "classification", "yes", "Backend type label.", "Current token/evidence fields.", "Controlled after review.", unresolved),
                field("configuration_label", "TEXT", "descriptor", "yes", "Backend configuration label.", "Current token/evidence fields.", "Preserve exact source label.", unresolved),
                field("external_source_id", "TEXT", "foreign_key", "yes", "External source supporting the backend row.", "DB28 external source registry.", "Must reference map_external_source when present.", claim),
                field("evidence_status_id", "TEXT", "foreign_key", "yes", "Evidence status for the row.", "Current evidence/review statuses.", "Must reference dim_quality_status.", claim),
                field("audit_run_id", "TEXT", "foreign_key", "yes", "Audit run that created or migrated the row.", "Migration audit run.", "Must reference audit_run.", claim),
                field("notes", "TEXT", "note", "yes", "Context note for unresolved backend details.", "Migration/review note.", "No relation outcome text.", claim),
            ],
        ),
        table(
            "dim_time_context",
            "Dimensions / Context Layer",
            "Conformed time-context dimension for raw and observation anchors.",
            "One row per reviewed time-context state or unresolved candidate.",
            "time_context_id",
            "timescale_label + calendar_system + reference_epoch_text",
            "Current time-like token roles, raw fields, and mapping evidence.",
            "migrate_to_target_table",
            "P4",
            "Stores context labels only; it does not calculate or normalize TOA values.",
            [
                field("time_context_id", "TEXT", "primary_key", "no", "Stable identifier for a time-context dimension member.", "Generated during migration.", "Unique, non-empty.", claim),
                field("timescale_label", "TEXT", "descriptor", "yes", "Timescale label when reviewed.", "Current time-like token mappings.", "Do not assign final meaning without review.", unresolved),
                field("calendar_system", "TEXT", "descriptor", "yes", "Calendar system or source-local calendar label.", "Current time-like token mappings.", "Preserve raw/source label.", unresolved),
                field("reference_epoch_text", "TEXT", "raw_value", "yes", "Reference epoch text from source or reviewed mapping.", "Current raw/mapping fields.", "No epoch conversion in DWH01.", unresolved),
                field("source_time_token_id", "TEXT", "foreign_key", "yes", "Token dictionary row that supplied the time context.", "DB26/DB27 token dictionary.", "Must reference map_token_dictionary when present.", unresolved),
                field("precision_note", "TEXT", "note", "yes", "Text note about declared precision, if source-supported.", "Current mapping/evidence notes.", "No derived precision calculation.", claim),
                field("unresolved_numeric_policy", "TEXT", "classification", "no", "Policy for unresolved numeric tokens.", "DWH design rule.", "Use controlled policy values.", unresolved),
                field("evidence_status_id", "TEXT", "foreign_key", "yes", "Evidence status for the time context.", "Current evidence/review statuses.", "Must reference dim_quality_status.", claim),
                field("audit_run_id", "TEXT", "foreign_key", "yes", "Audit run that created or migrated the row.", "Migration audit run.", "Must reference audit_run.", claim),
                field("notes", "TEXT", "note", "yes", "Context note for unresolved time details.", "Migration/review note.", "No relation outcome text.", claim),
            ],
        ),
        table(
            "dim_processing_context",
            "Dimensions / Context Layer",
            "Conformed processing and script-context dimension.",
            "One row per processing pipeline/configuration state.",
            "processing_context_id",
            "processing_pipeline_name + processing_version + parameter_set_ref",
            "Current script/run metadata and future rebuild manifests.",
            "migrate_to_target_table",
            "P4",
            "Separates data acquisition context from processing and migration context.",
            [
                field("processing_context_id", "TEXT", "primary_key", "no", "Stable identifier for a processing context.", "Generated during migration.", "Unique, non-empty.", claim),
                field("processing_pipeline_name", "TEXT", "descriptor", "no", "Pipeline or workflow name.", "Current script/run metadata.", "Non-empty.", claim),
                field("processing_version", "TEXT", "descriptor", "yes", "Pipeline version or script version.", "Current script metadata.", "Preserve exact label.", claim),
                field("parameter_set_ref", "TEXT", "lineage_attribute", "yes", "Reference to a parameter/configuration set.", "Current config/run metadata.", "Store reference only.", claim),
                field("correction_model_ref", "TEXT", "lineage_attribute", "yes", "Reference to a declared model/config artifact, if any.", "Future implementation metadata.", "Reference only; no model calculation in DWH01.", claim),
                field("algorithm_family", "TEXT", "classification", "yes", "Controlled family label for processing logic.", "Current script names and run metadata.", "Controlled vocabulary.", claim),
                field("script_id", "TEXT", "foreign_key", "yes", "Script associated with this processing context.", "Current script metadata.", "Must reference audit_script when present.", claim),
                field("audit_run_id", "TEXT", "foreign_key", "yes", "Audit run that created or migrated the row.", "Migration audit run.", "Must reference audit_run.", claim),
                field("notes", "TEXT", "note", "yes", "Processing-context note.", "Migration/review note.", "No relation outcome text.", claim),
            ],
        ),
        table(
            "dim_quality_status",
            "Dimensions / Context Layer",
            "Conformed quality, review, and blocker status dimension.",
            "One row per status code.",
            "quality_status_id",
            "status_code",
            "Current status/review/blocker fields across DB26/DB27/DB28/bridge01 objects.",
            "migrate_to_target_table",
            "P4",
            "Provides reusable status semantics across mapping, context, facts, and results.",
            [
                field("quality_status_id", "TEXT", "primary_key", "no", "Stable identifier for a quality-status member.", "Generated during migration.", "Unique, non-empty.", claim),
                field("status_code", "TEXT", "natural_key", "no", "Machine-readable status code.", "Current status fields and target controlled vocabulary.", "Unique, non-empty.", claim),
                field("status_label", "TEXT", "descriptor", "no", "Human-readable status label.", "Current status fields.", "Non-empty.", claim),
                field("severity_rank", "INTEGER", "classification", "yes", "Ordered severity rank for dashboards.", "Target governance rule.", "Non-negative integer when populated.", claim),
                field("review_required", "INTEGER", "flag", "no", "Boolean flag for statuses needing review.", "Target governance rule.", "Must be 0 or 1.", claim),
                field("blocker_flag", "INTEGER", "flag", "no", "Boolean flag for statuses blocking migration or evaluation.", "Target governance rule.", "Must be 0 or 1.", claim),
                field("description", "TEXT", "descriptor", "yes", "Status definition.", "Target controlled vocabulary.", "Must not contain unsupported scientific interpretation.", claim),
                field("audit_run_id", "TEXT", "foreign_key", "yes", "Audit run that created or migrated the row.", "Migration audit run.", "Must reference audit_run.", claim),
            ],
        ),
        table(
            "map_token_dictionary",
            "Mapping / Evidence Layer",
            "Controlled token dictionary for source-local fields and token positions.",
            "One row per token or source field dictionary entry.",
            "token_dictionary_id",
            "token_family + token_name + token_position + source_field_name",
            "DB23/DB26/DB27 token inventories and mapping gap triage.",
            "migrate_to_target_table",
            "P5",
            "A token dictionary entry is not a final physical meaning.",
            [
                field("token_dictionary_id", "TEXT", "primary_key", "no", "Stable identifier for a dictionary token.", "Generated during migration.", "Unique, non-empty.", claim),
                field("token_family", "TEXT", "classification", "no", "Token family such as TIM, PAR, source, block, or derived.", "Current token family fields.", "Controlled vocabulary.", unresolved),
                field("token_name", "TEXT", "descriptor", "yes", "Token name or source-local label.", "Current field/token names.", "Preserve original label.", unresolved),
                field("token_position", "INTEGER", "lineage_attribute", "yes", "Source-local token position.", "Current token_position fields.", "No position semantics beyond source order.", unresolved),
                field("source_field_name", "TEXT", "lineage_attribute", "yes", "Source field name when available.", "Current field_name fields.", "Preserve source spelling.", unresolved),
                field("canonical_role_status", "TEXT", "classification", "no", "Status of semantic role assignment.", "DB26/DB27 review status.", "Controlled values such as unresolved, candidate, reviewed.", unresolved),
                field("preferred_label", "TEXT", "descriptor", "yes", "Preferred display label after review.", "Review decision.", "Must trace to review decision.", unresolved),
                field("description", "TEXT", "descriptor", "yes", "Dictionary description.", "Current mapping notes.", "Defensive wording required.", claim),
                field("first_seen_raw_field_value_id", "TEXT", "foreign_key", "yes", "First observed raw field value for lineage.", "Current raw field values.", "Must reference raw_field_value when present.", claim),
                field("audit_run_id", "TEXT", "foreign_key", "yes", "Audit run that created or migrated the row.", "Migration audit run.", "Must reference audit_run.", claim),
                field("claim_boundary_id", "TEXT", "foreign_key", "yes", "Claim boundary governing token use.", "DWH claim-boundary catalog.", "Must reference audit_claim_boundary when assigned.", claim),
            ],
        ),
        table(
            "map_token_role",
            "Mapping / Evidence Layer",
            "Stores reviewed or candidate token roles separately from raw values.",
            "One row per token-role assertion.",
            "token_role_id",
            "token_dictionary_id + role_label + role_scope",
            "DB26/DB27 mapping gap triage and manual worklist outputs.",
            "migrate_to_target_table",
            "P5",
            "Supports role transport only where evidence and review status allow it.",
            [
                field("token_role_id", "TEXT", "primary_key", "no", "Stable identifier for a token-role assertion.", "Generated during migration.", "Unique, non-empty.", claim),
                field("token_dictionary_id", "TEXT", "foreign_key", "no", "Dictionary token receiving the role.", "Current token dictionary rows.", "Must reference map_token_dictionary.", unresolved),
                field("role_label", "TEXT", "descriptor", "no", "Candidate or reviewed role label.", "Current mapping role fields.", "Controlled after review.", unresolved),
                field("role_family", "TEXT", "classification", "yes", "Role family such as source, time, instrument, signal, or bridge-input.", "Current mapping and bridge01 design fields.", "Controlled vocabulary.", unresolved),
                field("role_status", "TEXT", "classification", "no", "Status of the role assignment.", "DB26/DB27 review status.", "Controlled values.", unresolved),
                field("role_scope", "TEXT", "classification", "yes", "Scope where the role is allowed.", "Review decision.", "Do not apply outside reviewed scope.", claim),
                field("role_source", "TEXT", "lineage_attribute", "yes", "Source of the role proposal.", "Current mapping worklist/evidence fields.", "Must be source-linked.", claim),
                field("review_decision_id", "TEXT", "foreign_key", "yes", "Review decision governing the role.", "DB27 review decision fields.", "Must reference map_review_decision when present.", claim),
                field("evidence_gap_id", "TEXT", "foreign_key", "yes", "Open gap blocking the role, if any.", "DB26/DB28 gap fields.", "Must reference map_evidence_gap when present.", claim),
                field("audit_run_id", "TEXT", "foreign_key", "yes", "Audit run that created or migrated the row.", "Migration audit run.", "Must reference audit_run.", claim),
                field("claim_boundary_id", "TEXT", "foreign_key", "yes", "Claim boundary governing the role.", "DWH claim-boundary catalog.", "Must reference audit_claim_boundary when assigned.", claim),
            ],
        ),
        table(
            "map_token_value_assertion",
            "Mapping / Evidence Layer",
            "Connects raw field values to candidate or reviewed value assertions.",
            "One row per raw-value assertion.",
            "assertion_id",
            "raw_field_value_id + token_dictionary_id + asserted_value_text + assertion_status",
            "DB27 manual mapping work packets and DB28 evidence links.",
            "migrate_to_target_table",
            "P5",
            "Does not canonicalize unresolved numeric tokens.",
            [
                field("assertion_id", "TEXT", "primary_key", "no", "Stable identifier for a token value assertion.", "Generated during migration.", "Unique, non-empty.", claim),
                field("raw_field_value_id", "TEXT", "foreign_key", "no", "Raw field value being asserted.", "Current raw field value rows.", "Must reference raw_field_value.", unresolved),
                field("token_dictionary_id", "TEXT", "foreign_key", "no", "Token dictionary entry for the assertion.", "DB26/DB27 mapping fields.", "Must reference map_token_dictionary.", unresolved),
                field("asserted_value_text", "TEXT", "raw_value", "yes", "Asserted value text; may remain raw.", "Current mapping/evidence outputs.", "No numeric canonicalization in DWH01.", unresolved),
                field("asserted_value_type", "TEXT", "classification", "yes", "Declared value type, if reviewed.", "Current mapping/evidence outputs.", "Type is status-gated.", unresolved),
                field("canonicalization_status", "TEXT", "classification", "no", "Status of any canonical form.", "Current mapping/review fields.", "Controlled values; unresolved remains explicit.", unresolved),
                field("assertion_status", "TEXT", "classification", "no", "Review state of the assertion.", "DB27/DB28 status fields.", "Controlled values.", claim),
                field("evidence_id", "TEXT", "foreign_key", "yes", "Evidence row supporting or blocking the assertion.", "DB28 evidence rows.", "Must reference map_assertion_evidence when present.", claim),
                field("review_decision_id", "TEXT", "foreign_key", "yes", "Review decision for the assertion.", "DB27 review decision fields.", "Must reference map_review_decision when present.", claim),
                field("quality_status_id", "TEXT", "foreign_key", "yes", "Quality status for the assertion.", "Current review/status fields.", "Must reference dim_quality_status.", claim),
                field("audit_run_id", "TEXT", "foreign_key", "yes", "Audit run that created or migrated the row.", "Migration audit run.", "Must reference audit_run.", claim),
                field("claim_boundary_id", "TEXT", "foreign_key", "yes", "Claim boundary governing the assertion.", "DWH claim-boundary catalog.", "Must reference audit_claim_boundary when assigned.", claim),
            ],
        ),
        table(
            "map_external_source",
            "Mapping / Evidence Layer",
            "Registry of external sources used for mapping and context support.",
            "One row per external source reference.",
            "external_source_id",
            "source_name + uri + accessed_at_utc",
            "DB28 external source registry.",
            "migrate_to_target_table",
            "P5",
            "Stores evidence references and retrieval status, not large payloads.",
            [
                field("external_source_id", "TEXT", "primary_key", "no", "Stable identifier for an external source reference.", "Generated during migration.", "Unique, non-empty.", claim),
                field("source_name", "TEXT", "descriptor", "no", "External source name.", "DB28 source_name fields.", "Non-empty.", claim),
                field("source_type", "TEXT", "classification", "no", "External source type.", "DB28 source_type fields.", "Controlled vocabulary.", claim),
                field("authority_level", "TEXT", "classification", "yes", "Authority or tier label.", "DB28 tier/relevance fields.", "Controlled vocabulary.", claim),
                field("uri", "TEXT", "lineage_attribute", "yes", "Official URL, URI, or locator.", "DB28 URL fields.", "Preserve exact locator.", claim),
                field("citation_text", "TEXT", "descriptor", "yes", "Citation or source note.", "DB28 citation/license fields.", "No large copied payload.", claim),
                field("retrieval_status", "TEXT", "classification", "no", "Retrieval/review status.", "DB28 retrieval status.", "Controlled values.", claim),
                field("license_note", "TEXT", "note", "yes", "License or usage note.", "DB28 license fields.", "No payload copied into note.", claim),
                field("accessed_at_utc", "TEXT", "audit_timestamp", "yes", "Access timestamp when applicable.", "DB28 access metadata.", "ISO-8601 UTC text.", claim),
                field("audit_run_id", "TEXT", "foreign_key", "yes", "Audit run that created or migrated the row.", "Migration audit run.", "Must reference audit_run.", claim),
            ],
        ),
        table(
            "map_assertion_evidence",
            "Mapping / Evidence Layer",
            "Evidence sidecar for token, context, bridge, and result assertions.",
            "One row per evidence item or evidence gap link.",
            "evidence_id",
            "external_source_id + evidence_locator + evidence_type",
            "DB28 mapping assertion evidence and gap outputs.",
            "migrate_to_target_table",
            "P5",
            "Evidence rows document support, limits, and gaps; they do not produce relation outcomes.",
            [
                field("evidence_id", "TEXT", "primary_key", "no", "Stable identifier for an evidence row.", "Generated during migration.", "Unique, non-empty.", claim),
                field("assertion_id", "TEXT", "foreign_key", "yes", "Token value assertion supported or constrained by this evidence.", "DB28 assertion-evidence links.", "Must reference map_token_value_assertion when applicable.", claim),
                field("external_source_id", "TEXT", "foreign_key", "yes", "External source supplying the evidence reference.", "DB28 source registry.", "Must reference map_external_source when present.", claim),
                field("evidence_type", "TEXT", "classification", "no", "Type of evidence reference.", "DB28 evidence type fields.", "Controlled vocabulary.", claim),
                field("evidence_locator", "TEXT", "lineage_attribute", "yes", "Section, page, URL fragment, object key, or locator.", "DB28 evidence locator fields.", "Preserve exact locator.", claim),
                field("evidence_quote_ref", "TEXT", "payload_reference", "yes", "Short quote reference or pointer to review note.", "DB28 evidence text fields.", "Avoid large copied payloads.", claim),
                field("evidence_summary", "TEXT", "descriptor", "yes", "Defensive summary of what the evidence supports or leaves open.", "DB28 evidence summary fields.", "Must separate support from gaps.", claim),
                field("support_status", "TEXT", "classification", "no", "Status such as supports, conflicts, insufficient, or pending.", "DB28 support status fields.", "Controlled vocabulary.", claim),
                field("gap_id", "TEXT", "foreign_key", "yes", "Evidence gap associated with this evidence row.", "DB28 gap fields.", "Must reference map_evidence_gap when present.", claim),
                field("audit_run_id", "TEXT", "foreign_key", "yes", "Audit run that created or migrated the row.", "Migration audit run.", "Must reference audit_run.", claim),
                field("claim_boundary_id", "TEXT", "foreign_key", "yes", "Claim boundary governing use of the evidence.", "DWH claim-boundary catalog.", "Must reference audit_claim_boundary when assigned.", claim),
            ],
        ),
        table(
            "map_review_decision",
            "Mapping / Evidence Layer",
            "Records manual or scripted review decisions.",
            "One row per review decision.",
            "review_decision_id",
            "reviewed_object_table + reviewed_object_id + decision_at_utc",
            "DB27 manual mapping worklist and DB28 evidence review status.",
            "migrate_to_target_table",
            "P5",
            "Review decisions are first-class objects so later changes remain auditable.",
            [
                field("review_decision_id", "TEXT", "primary_key", "no", "Stable identifier for a review decision.", "Generated during migration.", "Unique, non-empty.", claim),
                field("reviewed_object_table", "TEXT", "classification", "no", "Name of the table/object type under review.", "Current review worklist fields.", "Must name an allowed target object family.", claim),
                field("reviewed_object_id", "TEXT", "lineage_attribute", "no", "Identifier of the reviewed row or object.", "Current review worklist fields.", "Must be non-empty.", claim),
                field("decision_status", "TEXT", "classification", "no", "Status of the decision.", "DB27 decision/status fields.", "Controlled vocabulary.", claim),
                field("decision_label", "TEXT", "descriptor", "yes", "Decision label.", "DB27 decision fields.", "Defensive wording required.", claim),
                field("reviewer_role", "TEXT", "classification", "yes", "Role of reviewer or process.", "DB27 review metadata.", "Do not store private personal data unless approved.", claim),
                field("decision_at_utc", "TEXT", "audit_timestamp", "yes", "Decision timestamp.", "Current review metadata.", "ISO-8601 UTC text.", claim),
                field("rationale", "TEXT", "note", "yes", "Reason for the decision.", "Current review notes.", "Separate finding, interpretation, and open gap.", claim),
                field("supersedes_decision_id", "TEXT", "foreign_key", "yes", "Earlier decision superseded by this row.", "Future review lineage.", "Must reference map_review_decision when present.", claim),
                field("audit_run_id", "TEXT", "foreign_key", "yes", "Audit run that created or migrated the row.", "Migration audit run.", "Must reference audit_run.", claim),
                field("claim_boundary_id", "TEXT", "foreign_key", "yes", "Claim boundary governing the decision.", "DWH claim-boundary catalog.", "Must reference audit_claim_boundary when assigned.", claim),
            ],
        ),
        table(
            "map_evidence_gap",
            "Mapping / Evidence Layer",
            "Tracks missing, weak, or unresolved evidence needed for mapping and relation readiness.",
            "One row per evidence or review gap.",
            "evidence_gap_id",
            "affected_object_table + affected_object_id + gap_type",
            "DB26 mapping gaps, DB27 priority worklists, and DB28 external evidence gaps.",
            "migrate_to_target_table",
            "P5",
            "Open gaps block promotion into stricter target layers.",
            [
                field("evidence_gap_id", "TEXT", "primary_key", "no", "Stable identifier for an evidence gap.", "Generated during migration.", "Unique, non-empty.", claim),
                field("gap_type", "TEXT", "classification", "no", "Type of gap.", "Current gap fields.", "Controlled vocabulary.", claim),
                field("gap_status", "TEXT", "classification", "no", "Lifecycle status of the gap.", "Current gap/status fields.", "Controlled vocabulary.", claim),
                field("affected_object_table", "TEXT", "classification", "yes", "Table or object family affected by the gap.", "Current worklist fields.", "Must name allowed target object family when populated.", claim),
                field("affected_object_id", "TEXT", "lineage_attribute", "yes", "Identifier of affected row or object.", "Current worklist fields.", "Must preserve original ID when unresolved.", claim),
                field("blocking_level", "TEXT", "classification", "no", "Blocking level for migration or readiness.", "Current priority/blocker fields.", "Controlled vocabulary.", claim),
                field("remediation_step", "TEXT", "note", "yes", "Proposed next action to close or reduce the gap.", "Current worklist notes.", "Must not assert outcomes.", claim),
                field("opened_at_utc", "TEXT", "audit_timestamp", "yes", "UTC timestamp when the gap opened.", "Current run metadata.", "ISO-8601 UTC text.", claim),
                field("closed_at_utc", "TEXT", "audit_timestamp", "yes", "UTC timestamp when the gap closed.", "Future review metadata.", "NULL while open.", claim),
                field("audit_run_id", "TEXT", "foreign_key", "yes", "Audit run that created or migrated the row.", "Migration audit run.", "Must reference audit_run.", claim),
                field("claim_boundary_id", "TEXT", "foreign_key", "yes", "Claim boundary governing the gap.", "DWH claim-boundary catalog.", "Must reference audit_claim_boundary when assigned.", claim),
            ],
        ),
        table(
            "fact_token_observation",
            "Observation / Signal Fact Layer",
            "Observation-centered fact table for raw token observations.",
            "One row per observed token value linked to an observation.",
            "token_observation_id",
            "observation_id + raw_field_value_id + token_dictionary_id",
            "Current raw token values and DB26/DB27/DB28 mapping context.",
            "migrate_to_target_table",
            "P6",
            "Carries observed token text and status, not physical interpretation.",
            [
                field("token_observation_id", "TEXT", "primary_key", "no", "Stable identifier for a token observation fact.", "Generated during migration.", "Unique, non-empty.", claim),
                field("observation_id", "TEXT", "foreign_key", "no", "Observation anchor for the fact.", "Future observation migration.", "Must reference core_observation.", claim),
                field("raw_field_value_id", "TEXT", "foreign_key", "no", "Raw value observed in the source record.", "Current raw field values.", "Must reference raw_field_value.", unresolved),
                field("token_dictionary_id", "TEXT", "foreign_key", "yes", "Dictionary token, if mapped.", "DB26/DB27 dictionary rows.", "Must reference map_token_dictionary when assigned.", unresolved),
                field("token_role_id", "TEXT", "foreign_key", "yes", "Reviewed or candidate role for the token.", "DB26/DB27 role rows.", "Must reference map_token_role when assigned.", unresolved),
                field("asserted_value_id", "TEXT", "foreign_key", "yes", "Value assertion linked to the token observation.", "DB27/DB28 assertion rows.", "Must reference map_token_value_assertion when assigned.", unresolved),
                field("observed_value_text", "TEXT", "raw_value", "yes", "Observed value text preserved from source or assertion.", "Current raw/mapping values.", "No canonicalization in DWH01.", unresolved),
                field("value_status", "TEXT", "classification", "no", "Status of the observed token value.", "Current mapping/status fields.", "Controlled vocabulary.", unresolved),
                field("quality_status_id", "TEXT", "foreign_key", "yes", "Quality status for this fact.", "Current review/status fields.", "Must reference dim_quality_status.", claim),
                field("audit_run_id", "TEXT", "foreign_key", "yes", "Audit run that created or migrated the fact.", "Migration audit run.", "Must reference audit_run.", claim),
                field("claim_boundary_id", "TEXT", "foreign_key", "yes", "Claim boundary governing the fact.", "DWH claim-boundary catalog.", "Must reference audit_claim_boundary when assigned.", claim),
            ],
        ),
        table(
            "fact_signal_observation",
            "Observation / Signal Fact Layer",
            "Observation-centered signal-value fact skeleton.",
            "One row per reviewed signal value or signal candidate in an observation.",
            "signal_observation_id",
            "observation_id + signal_family + measurement_token_id",
            "Future promoted rows from token observations after review.",
            "migrate_to_target_table",
            "P7",
            "Stores value text/status; later computation layers must be separately audited.",
            [
                field("signal_observation_id", "TEXT", "primary_key", "no", "Stable identifier for a signal observation fact.", "Generated during migration.", "Unique, non-empty.", claim),
                field("observation_id", "TEXT", "foreign_key", "no", "Observation anchor for the signal fact.", "Future observation migration.", "Must reference core_observation.", claim),
                field("signal_family", "TEXT", "classification", "no", "Signal family label.", "Reviewed token-role mapping.", "Controlled vocabulary.", unresolved),
                field("measurement_token_id", "TEXT", "foreign_key", "yes", "Token observation supplying the signal value.", "fact_token_observation.", "Must reference fact_token_observation when present.", unresolved),
                field("value_text", "TEXT", "raw_value", "yes", "Signal value text.", "Reviewed mapping output.", "No physical calculation in DWH01.", unresolved),
                field("unit_label", "TEXT", "descriptor", "yes", "Declared or reviewed unit label.", "Reviewed evidence/mapping output.", "Source-linked when populated.", unresolved),
                field("numeric_status", "TEXT", "classification", "no", "Status of numeric interpretation.", "Review decision.", "Controlled values; unresolved allowed.", unresolved),
                field("quality_status_id", "TEXT", "foreign_key", "yes", "Quality status for the signal fact.", "Current review/status fields.", "Must reference dim_quality_status.", claim),
                field("evidence_id", "TEXT", "foreign_key", "yes", "Evidence supporting the signal mapping.", "map_assertion_evidence.", "Must reference map_assertion_evidence when present.", claim),
                field("audit_run_id", "TEXT", "foreign_key", "yes", "Audit run that created or migrated the fact.", "Migration audit run.", "Must reference audit_run.", claim),
                field("claim_boundary_id", "TEXT", "foreign_key", "yes", "Claim boundary governing the fact.", "DWH claim-boundary catalog.", "Must reference audit_claim_boundary when assigned.", claim),
            ],
        ),
        table(
            "fact_block_signature",
            "Observation / Signal Fact Layer",
            "Observation-centered block-signature fact for comparing source-local block structure.",
            "One row per observation/block-signature candidate.",
            "block_signature_id",
            "observation_id + signature_family + source_file_id",
            "DB23A/DB23B block signature inspection outputs.",
            "migrate_to_target_table",
            "P6",
            "Retains scaffold/block inventory status without elevating it to relation evidence.",
            [
                field("block_signature_id", "TEXT", "primary_key", "no", "Stable identifier for a block-signature fact.", "Generated during migration.", "Unique, non-empty.", claim),
                field("observation_id", "TEXT", "foreign_key", "yes", "Observation anchor for the block signature.", "Future observation migration.", "Must reference core_observation when assigned.", claim),
                field("raw_record_id", "TEXT", "foreign_key", "yes", "Raw record supporting the block signature.", "Current raw/staging record IDs.", "Must reference raw_record when present.", claim),
                field("source_file_id", "TEXT", "foreign_key", "yes", "Source file supporting the signature.", "Current source inventory.", "Must reference raw_source_file when present.", claim),
                field("signature_family", "TEXT", "classification", "no", "Block-signature family label.", "DB23A/DB23B signature fields.", "Controlled vocabulary.", claim),
                field("block_a_signature", "TEXT", "descriptor", "yes", "Source-local signature text for block A.", "DB23B signature outputs.", "Preserve source/local representation.", claim),
                field("block_b_signature", "TEXT", "descriptor", "yes", "Source-local signature text for block B.", "DB23B signature outputs.", "Preserve source/local representation.", claim),
                field("comparison_status", "TEXT", "classification", "no", "Status of block comparison.", "DB23B comparison status.", "Controlled vocabulary.", claim),
                field("quality_status_id", "TEXT", "foreign_key", "yes", "Quality status for the block signature.", "Current status fields.", "Must reference dim_quality_status.", claim),
                field("audit_run_id", "TEXT", "foreign_key", "yes", "Audit run that created or migrated the fact.", "Migration audit run.", "Must reference audit_run.", claim),
                field("claim_boundary_id", "TEXT", "foreign_key", "yes", "Claim boundary governing the fact.", "DWH claim-boundary catalog.", "Must reference audit_claim_boundary when assigned.", claim),
            ],
        ),
        table(
            "bridge_qm_quantity",
            "Bridge / Connection Layer",
            "Catalog of QM-side quantity candidates available for future relation design.",
            "One row per QM-side quantity definition or candidate.",
            "qm_quantity_id",
            "quantity_name + quantity_symbol + relation scope",
            "bridge01 design/readiness fields and reviewed token roles.",
            "migrate_to_target_table",
            "P6",
            "Quantity rows require evidence and claim boundary before use in evaluations.",
            [
                field("qm_quantity_id", "TEXT", "primary_key", "no", "Stable identifier for a QM-side quantity.", "Generated during migration.", "Unique, non-empty.", claim),
                field("quantity_name", "TEXT", "descriptor", "no", "Quantity name or candidate label.", "bridge01 quantity design fields.", "Non-empty.", claim),
                field("quantity_symbol", "TEXT", "descriptor", "yes", "Quantity symbol, if defined.", "bridge01 design fields.", "Source-linked when populated.", claim),
                field("quantity_family", "TEXT", "classification", "no", "Quantity family.", "bridge01 design fields.", "Controlled vocabulary.", claim),
                field("source_token_role_id", "TEXT", "foreign_key", "yes", "Token role supplying the quantity candidate.", "map_token_role.", "Must reference map_token_role when present.", unresolved),
                field("expected_unit_label", "TEXT", "descriptor", "yes", "Expected unit label for future evaluation design.", "bridge01 design fields.", "No conversion in DWH01.", claim),
                field("definition_status", "TEXT", "classification", "no", "Status of quantity definition.", "bridge01 readiness/status fields.", "Controlled vocabulary.", claim),
                field("evidence_id", "TEXT", "foreign_key", "yes", "Evidence supporting the quantity definition.", "map_assertion_evidence.", "Must reference map_assertion_evidence when present.", claim),
                field("audit_run_id", "TEXT", "foreign_key", "yes", "Audit run that created or migrated the row.", "Migration audit run.", "Must reference audit_run.", claim),
                field("claim_boundary_id", "TEXT", "foreign_key", "yes", "Claim boundary governing the quantity.", "DWH claim-boundary catalog.", "Must reference audit_claim_boundary when assigned.", claim),
            ],
        ),
        table(
            "bridge_art_quantity",
            "Bridge / Connection Layer",
            "Catalog of ART-side quantity candidates available for future relation design.",
            "One row per ART-side quantity definition or candidate.",
            "art_quantity_id",
            "quantity_name + quantity_symbol + relation scope",
            "bridge01 design/readiness fields and reviewed token roles.",
            "migrate_to_target_table",
            "P6",
            "Quantity rows require evidence and claim boundary before use in evaluations.",
            [
                field("art_quantity_id", "TEXT", "primary_key", "no", "Stable identifier for an ART-side quantity.", "Generated during migration.", "Unique, non-empty.", claim),
                field("quantity_name", "TEXT", "descriptor", "no", "Quantity name or candidate label.", "bridge01 quantity design fields.", "Non-empty.", claim),
                field("quantity_symbol", "TEXT", "descriptor", "yes", "Quantity symbol, if defined.", "bridge01 design fields.", "Source-linked when populated.", claim),
                field("quantity_family", "TEXT", "classification", "no", "Quantity family.", "bridge01 design fields.", "Controlled vocabulary.", claim),
                field("source_token_role_id", "TEXT", "foreign_key", "yes", "Token role supplying the quantity candidate.", "map_token_role.", "Must reference map_token_role when present.", unresolved),
                field("expected_unit_label", "TEXT", "descriptor", "yes", "Expected unit label for future evaluation design.", "bridge01 design fields.", "No conversion in DWH01.", claim),
                field("definition_status", "TEXT", "classification", "no", "Status of quantity definition.", "bridge01 readiness/status fields.", "Controlled vocabulary.", claim),
                field("evidence_id", "TEXT", "foreign_key", "yes", "Evidence supporting the quantity definition.", "map_assertion_evidence.", "Must reference map_assertion_evidence when present.", claim),
                field("audit_run_id", "TEXT", "foreign_key", "yes", "Audit run that created or migrated the row.", "Migration audit run.", "Must reference audit_run.", claim),
                field("claim_boundary_id", "TEXT", "foreign_key", "yes", "Claim boundary governing the quantity.", "DWH claim-boundary catalog.", "Must reference audit_claim_boundary when assigned.", claim),
            ],
        ),
        table(
            "bridge_functional_relation",
            "Bridge / Connection Layer",
            "Defines candidate functional relations between QM-side and ART-side quantities.",
            "One row per relation definition or candidate relation.",
            "relation_id",
            "relation_name + qm_quantity_id + art_quantity_id + relation_scope",
            "bridge01 candidate relation specification fields.",
            "migrate_to_target_table",
            "P6",
            "A relation definition is a design object, not an evaluated result.",
            [
                field("relation_id", "TEXT", "primary_key", "no", "Stable identifier for a functional relation candidate.", "Generated during migration.", "Unique, non-empty.", claim),
                field("relation_name", "TEXT", "descriptor", "no", "Relation name or candidate label.", "bridge01 design fields.", "Non-empty.", claim),
                field("qm_quantity_id", "TEXT", "foreign_key", "no", "QM-side quantity linked by the relation.", "bridge_qm_quantity.", "Must reference bridge_qm_quantity.", claim),
                field("art_quantity_id", "TEXT", "foreign_key", "no", "ART-side quantity linked by the relation.", "bridge_art_quantity.", "Must reference bridge_art_quantity.", claim),
                field("relation_expression_ref", "TEXT", "payload_reference", "yes", "Reference to expression or theory note, not embedded calculation output.", "Future relation spec artifact.", "Reference only; no calculation in DWH01.", claim),
                field("relation_status", "TEXT", "classification", "no", "Lifecycle/readiness status for the relation.", "bridge01 readiness fields.", "Controlled vocabulary.", claim),
                field("relation_scope", "TEXT", "classification", "yes", "Allowed scope or context for the relation.", "bridge01 context fields.", "Must be explicit before evaluation.", claim),
                field("evidence_id", "TEXT", "foreign_key", "yes", "Evidence supporting the relation definition.", "map_assertion_evidence.", "Must reference map_assertion_evidence when present.", claim),
                field("required_context_summary", "TEXT", "descriptor", "yes", "Summary of required context conditions.", "bridge01 missing-link design.", "Must list blockers explicitly.", claim),
                field("audit_run_id", "TEXT", "foreign_key", "yes", "Audit run that created or migrated the row.", "Migration audit run.", "Must reference audit_run.", claim),
                field("claim_boundary_id", "TEXT", "foreign_key", "yes", "Claim boundary governing the relation.", "DWH claim-boundary catalog.", "Must reference audit_claim_boundary when assigned.", claim),
            ],
        ),
        table(
            "bridge_relation_context_condition",
            "Bridge / Connection Layer",
            "Lists context conditions required for a candidate relation.",
            "One row per relation-context condition.",
            "relation_context_condition_id",
            "relation_id + context_dimension_table + condition_type + condition_value_text",
            "bridge01 missing field/context design and current mapping gaps.",
            "migrate_to_target_table",
            "P6",
            "Context conditions make readiness blockers queryable.",
            [
                field("relation_context_condition_id", "TEXT", "primary_key", "no", "Stable identifier for a relation context condition.", "Generated during migration.", "Unique, non-empty.", claim),
                field("relation_id", "TEXT", "foreign_key", "no", "Relation requiring the context condition.", "bridge_functional_relation.", "Must reference bridge_functional_relation.", claim),
                field("context_dimension_table", "TEXT", "polymorphic_reference", "no", "Target dimension or fact table where the condition is checked.", "bridge01 context design fields.", "Must name an allowed target table.", claim),
                field("context_dimension_id", "TEXT", "polymorphic_reference", "yes", "Specific dimension row when condition is instance-specific.", "Future relation setup.", "Must pair with context_dimension_table.", claim),
                field("condition_type", "TEXT", "classification", "no", "Condition type such as required, excluded, status, or range-text.", "bridge01 design fields.", "Controlled vocabulary.", claim),
                field("condition_value_text", "TEXT", "descriptor", "yes", "Text value of the condition.", "bridge01 design fields.", "No calculation in DWH01.", claim),
                field("mandatory", "INTEGER", "flag", "no", "Boolean flag for mandatory relation readiness.", "Target design rule.", "Must be 0 or 1.", claim),
                field("evidence_id", "TEXT", "foreign_key", "yes", "Evidence supporting the condition.", "map_assertion_evidence.", "Must reference map_assertion_evidence when present.", claim),
                field("audit_run_id", "TEXT", "foreign_key", "yes", "Audit run that created or migrated the row.", "Migration audit run.", "Must reference audit_run.", claim),
                field("claim_boundary_id", "TEXT", "foreign_key", "yes", "Claim boundary governing the condition.", "DWH claim-boundary catalog.", "Must reference audit_claim_boundary when assigned.", claim),
            ],
        ),
        table(
            "bridge_candidate_connection",
            "Bridge / Connection Layer",
            "Connects relation definitions to observations, quantities, evidence chains, and blockers.",
            "One row per observation-level candidate connection.",
            "bridge_candidate_connection_id",
            "relation_id + observation_id + qm_quantity_id + art_quantity_id",
            "bridge01 candidate matrix/readiness fields.",
            "migrate_to_target_table",
            "P6",
            "This is the operational join object; it still does not evaluate the relation.",
            [
                field("bridge_candidate_connection_id", "TEXT", "primary_key", "no", "Stable identifier for a bridge candidate connection.", "Generated during migration.", "Unique, non-empty.", claim),
                field("relation_id", "TEXT", "foreign_key", "no", "Functional relation candidate.", "bridge_functional_relation.", "Must reference bridge_functional_relation.", claim),
                field("observation_id", "TEXT", "foreign_key", "no", "Observation anchor being connected.", "core_observation.", "Must reference core_observation.", claim),
                field("qm_quantity_id", "TEXT", "foreign_key", "yes", "QM-side quantity in the connection.", "bridge_qm_quantity.", "Must reference bridge_qm_quantity when present.", claim),
                field("art_quantity_id", "TEXT", "foreign_key", "yes", "ART-side quantity in the connection.", "bridge_art_quantity.", "Must reference bridge_art_quantity when present.", claim),
                field("candidate_status", "TEXT", "classification", "no", "Lifecycle status of the candidate connection.", "bridge01 readiness fields.", "Controlled vocabulary.", claim),
                field("readiness_status", "TEXT", "classification", "no", "Readiness status for future evaluation.", "bridge01 missing/gap fields.", "Controlled vocabulary; blockers explicit.", claim),
                field("evidence_chain_status", "TEXT", "classification", "no", "Status of evidence chain completeness.", "DB28/bridge01 evidence links.", "Controlled vocabulary.", claim),
                field("failure_mode_status", "TEXT", "classification", "yes", "Known failure or blocker mode.", "bridge01 gap matrix.", "Controlled vocabulary.", claim),
                field("audit_run_id", "TEXT", "foreign_key", "yes", "Audit run that created or migrated the row.", "Migration audit run.", "Must reference audit_run.", claim),
                field("claim_boundary_id", "TEXT", "foreign_key", "yes", "Claim boundary governing the candidate connection.", "DWH claim-boundary catalog.", "Must reference audit_claim_boundary when assigned.", claim),
            ],
        ),
        table(
            "fact_relation_evaluation",
            "Result / Evaluation Layer",
            "Future evaluation fact connecting candidate relations to expected and observed value text.",
            "One row per evaluation attempt for a candidate connection.",
            "relation_evaluation_id",
            "bridge_candidate_connection_id + evaluation_run_id",
            "Future implementation; current bridge01 can seed readiness only.",
            "migrate_to_target_table",
            "P7",
            "Skeleton only in DWH01; no relation evaluation is run.",
            [
                field("relation_evaluation_id", "TEXT", "primary_key", "no", "Stable identifier for a relation evaluation fact.", "Generated during future implementation.", "Unique, non-empty.", claim),
                field("bridge_candidate_connection_id", "TEXT", "foreign_key", "no", "Candidate connection being evaluated.", "bridge_candidate_connection.", "Must reference bridge_candidate_connection.", claim),
                field("observation_id", "TEXT", "foreign_key", "no", "Observation anchor for the evaluation.", "core_observation.", "Must reference core_observation.", claim),
                field("relation_id", "TEXT", "foreign_key", "no", "Relation definition evaluated.", "bridge_functional_relation.", "Must reference bridge_functional_relation.", claim),
                field("evaluation_run_id", "TEXT", "foreign_key", "yes", "Audit run for a future evaluation.", "audit_run.", "Must reference audit_run.", claim),
                field("evaluation_status", "TEXT", "classification", "no", "Lifecycle/readiness status of the evaluation row.", "Future evaluation run metadata.", "Controlled vocabulary.", claim),
                field("expected_value_text", "TEXT", "result_value", "yes", "Expected value text captured by a future audited evaluation.", "Future evaluated output.", "DWH01 leaves NULL/unpopulated.", claim),
                field("observed_value_text", "TEXT", "result_value", "yes", "Observed value text captured by a future audited evaluation.", "Future evaluated output.", "DWH01 leaves NULL/unpopulated.", claim),
                field("evaluation_method_ref", "TEXT", "payload_reference", "yes", "Reference to future method specification.", "Future method artifact.", "Reference only.", claim),
                field("quality_status_id", "TEXT", "foreign_key", "yes", "Quality status for the evaluation row.", "Future status dimension.", "Must reference dim_quality_status.", claim),
                field("evidence_id", "TEXT", "foreign_key", "yes", "Evidence chain used by the evaluation.", "map_assertion_evidence.", "Must reference map_assertion_evidence when present.", claim),
                field("claim_boundary_id", "TEXT", "foreign_key", "yes", "Claim boundary governing the evaluation.", "DWH claim-boundary catalog.", "Must reference audit_claim_boundary when assigned.", claim),
            ],
        ),
        table(
            "fact_delta_result",
            "Result / Evaluation Layer",
            "Future delta/result fact linked to relation evaluations.",
            "One row per delta result emitted by an audited evaluation.",
            "delta_result_id",
            "relation_evaluation_id + comparison_basis",
            "Future implementation; no current DB object should be treated as final delta result.",
            "migrate_to_target_table",
            "P7",
            "Skeleton only in DWH01; values remain future audited outputs.",
            [
                field("delta_result_id", "TEXT", "primary_key", "no", "Stable identifier for a delta result fact.", "Generated during future implementation.", "Unique, non-empty.", claim),
                field("relation_evaluation_id", "TEXT", "foreign_key", "no", "Relation evaluation that produced the delta row.", "fact_relation_evaluation.", "Must reference fact_relation_evaluation.", claim),
                field("observation_id", "TEXT", "foreign_key", "no", "Observation anchor for the delta row.", "core_observation.", "Must reference core_observation.", claim),
                field("delta_value_text", "TEXT", "result_value", "yes", "Delta value text from a future audited evaluation.", "Future evaluated output.", "DWH01 leaves NULL/unpopulated.", claim),
                field("delta_unit_label", "TEXT", "descriptor", "yes", "Unit label for the future delta value.", "Future method/evidence output.", "Source-linked when populated.", claim),
                field("delta_status", "TEXT", "classification", "no", "Lifecycle/status of the delta result.", "Future evaluation metadata.", "Controlled vocabulary.", claim),
                field("comparison_basis", "TEXT", "descriptor", "yes", "Text reference to comparison basis.", "Future method artifact.", "Reference only.", claim),
                field("quality_status_id", "TEXT", "foreign_key", "yes", "Quality status for the delta row.", "Future status dimension.", "Must reference dim_quality_status.", claim),
                field("audit_run_id", "TEXT", "foreign_key", "yes", "Audit run that created the delta row.", "Future evaluation audit run.", "Must reference audit_run.", claim),
                field("claim_boundary_id", "TEXT", "foreign_key", "yes", "Claim boundary governing the delta row.", "DWH claim-boundary catalog.", "Must reference audit_claim_boundary when assigned.", claim),
            ],
        ),
        table(
            "fact_control_check",
            "Result / Evaluation Layer",
            "Future control-check fact linked to relation evaluations.",
            "One row per control check for an evaluation.",
            "control_check_id",
            "relation_evaluation_id + control_type + control_object_ref",
            "Future implementation; bridge01 can seed required control categories.",
            "migrate_to_target_table",
            "P7",
            "Controls and failure modes are explicit result-layer objects.",
            [
                field("control_check_id", "TEXT", "primary_key", "no", "Stable identifier for a control check.", "Generated during future implementation.", "Unique, non-empty.", claim),
                field("relation_evaluation_id", "TEXT", "foreign_key", "no", "Relation evaluation checked by the control.", "fact_relation_evaluation.", "Must reference fact_relation_evaluation.", claim),
                field("observation_id", "TEXT", "foreign_key", "yes", "Observation anchor for the control.", "core_observation.", "Must reference core_observation when applicable.", claim),
                field("control_type", "TEXT", "classification", "no", "Control type.", "Future evaluation/control design.", "Controlled vocabulary.", claim),
                field("control_object_ref", "TEXT", "payload_reference", "yes", "Reference to control object or cohort.", "Future control manifest.", "Reference only.", claim),
                field("control_expected_status", "TEXT", "classification", "yes", "Expected status for the control.", "Future method artifact.", "Controlled vocabulary.", claim),
                field("control_observed_status", "TEXT", "classification", "yes", "Observed status for the control.", "Future evaluation output.", "Controlled vocabulary.", claim),
                field("pass_fail_status", "TEXT", "classification", "no", "Control result status.", "Future evaluation output.", "Controlled vocabulary; not a scientific claim by itself.", claim),
                field("quality_status_id", "TEXT", "foreign_key", "yes", "Quality status for the control row.", "Future status dimension.", "Must reference dim_quality_status.", claim),
                field("audit_run_id", "TEXT", "foreign_key", "yes", "Audit run that created the control row.", "Future evaluation audit run.", "Must reference audit_run.", claim),
                field("claim_boundary_id", "TEXT", "foreign_key", "yes", "Claim boundary governing the control row.", "DWH claim-boundary catalog.", "Must reference audit_claim_boundary when assigned.", claim),
            ],
        ),
        table(
            "fact_modulation_recovery",
            "Result / Evaluation Layer",
            "Future modulation-recovery fact linked to relation evaluations.",
            "One row per modulation-recovery attempt.",
            "modulation_recovery_id",
            "relation_evaluation_id + modulation_family + recovery_method_ref",
            "Future implementation; current DB does not populate this as a result.",
            "migrate_to_target_table",
            "P7",
            "Skeleton only in DWH01; no recovery process is run.",
            [
                field("modulation_recovery_id", "TEXT", "primary_key", "no", "Stable identifier for a modulation-recovery result.", "Generated during future implementation.", "Unique, non-empty.", claim),
                field("relation_evaluation_id", "TEXT", "foreign_key", "no", "Relation evaluation associated with recovery.", "fact_relation_evaluation.", "Must reference fact_relation_evaluation.", claim),
                field("observation_id", "TEXT", "foreign_key", "yes", "Observation anchor for the recovery row.", "core_observation.", "Must reference core_observation when applicable.", claim),
                field("modulation_family", "TEXT", "classification", "no", "Modulation family label.", "Future method artifact.", "Controlled vocabulary.", claim),
                field("recovery_method_ref", "TEXT", "payload_reference", "yes", "Reference to recovery method.", "Future method artifact.", "Reference only.", claim),
                field("recovery_status", "TEXT", "classification", "no", "Lifecycle/status of the recovery attempt.", "Future evaluation output.", "Controlled vocabulary.", claim),
                field("recovered_value_text", "TEXT", "result_value", "yes", "Recovered value text from a future audited evaluation.", "Future evaluated output.", "DWH01 leaves NULL/unpopulated.", claim),
                field("quality_status_id", "TEXT", "foreign_key", "yes", "Quality status for the recovery row.", "Future status dimension.", "Must reference dim_quality_status.", claim),
                field("evidence_id", "TEXT", "foreign_key", "yes", "Evidence chain used by the recovery row.", "map_assertion_evidence.", "Must reference map_assertion_evidence when present.", claim),
                field("audit_run_id", "TEXT", "foreign_key", "yes", "Audit run that created the recovery row.", "Future evaluation audit run.", "Must reference audit_run.", claim),
                field("claim_boundary_id", "TEXT", "foreign_key", "yes", "Claim boundary governing the recovery row.", "DWH claim-boundary catalog.", "Must reference audit_claim_boundary when assigned.", claim),
            ],
        ),
        table(
            "audit_script",
            "Audit / Provenance Sidecar",
            "Registry of scripts that create, migrate, rebuild, or inspect DWH objects.",
            "One row per script identity/version.",
            "script_id",
            "script_path + checksum_sha256",
            "Current script paths from run logs and future migration manifests.",
            "migrate_to_target_table",
            "P1",
            "Script identity anchors reproducibility and migration audit trails.",
            [
                field("script_id", "TEXT", "primary_key", "no", "Stable identifier for a script.", "Generated during migration.", "Unique, non-empty.", claim),
                field("script_path", "TEXT", "lineage_attribute", "no", "Repository-relative script path.", "Current run/script metadata.", "Non-empty path.", claim),
                field("script_name", "TEXT", "descriptor", "no", "Script basename or display name.", "Derived from script_path.", "Non-empty.", claim),
                field("script_version", "TEXT", "descriptor", "yes", "Script version or block label.", "Current script constants or migration manifest.", "Preserve exact label.", claim),
                field("checksum_sha256", "TEXT", "lineage_attribute", "yes", "Script checksum.", "Future rebuild manifest.", "64 hex characters when populated.", claim),
                field("language", "TEXT", "classification", "no", "Implementation language.", "Derived from script extension.", "Controlled vocabulary.", claim),
                field("purpose", "TEXT", "descriptor", "yes", "Defensive purpose statement.", "Script metadata.", "Must not contain unsupported scientific interpretation.", claim),
                field("active_flag", "INTEGER", "flag", "no", "Boolean active/retired flag.", "Target governance rule.", "Must be 0 or 1.", claim),
                field("created_at_utc", "TEXT", "audit_timestamp", "yes", "UTC time the script registry row was created.", "Migration audit run.", "ISO-8601 UTC text.", claim),
            ],
        ),
        table(
            "audit_run",
            "Audit / Provenance Sidecar",
            "Run ledger for all schema, migration, rebuild, and report-generation operations.",
            "One row per audited run.",
            "audit_run_id",
            "script_id + run_started_at_utc + operation_mode",
            "Current DB25/DB26/DB27/DB28/bridge01 run logs and future run metadata.",
            "migrate_to_target_table",
            "P1",
            "Every generated or migrated row should link to an audit run where practical.",
            [
                field("audit_run_id", "TEXT", "primary_key", "no", "Stable identifier for an audited run.", "Generated during migration.", "Unique, non-empty.", claim),
                field("script_id", "TEXT", "foreign_key", "no", "Script executed by the run.", "Current script/run metadata.", "Must reference audit_script.", claim),
                field("run_label", "TEXT", "descriptor", "yes", "Human-readable run label.", "Current run-log labels.", "Defensive wording.", claim),
                field("run_started_at_utc", "TEXT", "audit_timestamp", "yes", "UTC run start time.", "Current run-log timestamps.", "ISO-8601 UTC text.", claim),
                field("run_completed_at_utc", "TEXT", "audit_timestamp", "yes", "UTC run completion time.", "Current run-log timestamps.", "ISO-8601 UTC text.", claim),
                field("input_db_path", "TEXT", "lineage_attribute", "yes", "Input database path when applicable.", "Current run metadata.", "Store path reference only.", claim),
                field("output_root_path", "TEXT", "lineage_attribute", "yes", "Output root path when applicable.", "Current run metadata.", "Store path reference only.", claim),
                field("operation_mode", "TEXT", "classification", "no", "Run mode such as read-only spec, migration, rebuild, or report.", "Current run metadata.", "Controlled vocabulary.", claim),
                field("db_write_mode", "TEXT", "classification", "no", "Database write mode used by the run.", "Current run metadata.", "Controlled values such as readonly, ddl, dml.", claim),
                field("stop_reason", "TEXT", "audit_status", "yes", "Reason the run stopped.", "Current run logs.", "Required for bounded or interrupted runs.", claim),
                field("warning_count", "INTEGER", "measure_count", "yes", "Number of warnings emitted by the run.", "Current run logs.", "Non-negative integer.", claim),
                field("row_count_summary_json", "TEXT", "payload_reference", "yes", "Compact JSON summary of row counts created or inspected.", "Current run summaries.", "Valid JSON text when populated.", claim),
                field("claim_boundary_id", "TEXT", "foreign_key", "yes", "Claim boundary governing the run.", "DWH claim-boundary catalog.", "Must reference audit_claim_boundary when assigned.", claim),
            ],
        ),
        table(
            "audit_schema_version",
            "Audit / Provenance Sidecar",
            "Version ledger for target schema states.",
            "One row per schema version/state.",
            "schema_version_id",
            "version_label",
            "Future implementation DDL and migration manifest.",
            "migrate_to_target_table",
            "P1",
            "Required before any target schema DDL is applied.",
            [
                field("schema_version_id", "TEXT", "primary_key", "no", "Stable identifier for a schema version.", "Generated during migration.", "Unique, non-empty.", claim),
                field("version_label", "TEXT", "natural_key", "no", "Schema version label.", "Target DDL manifest.", "Unique, non-empty.", claim),
                field("status", "TEXT", "classification", "no", "Schema version status.", "Migration governance.", "Controlled values such as proposed, active, retired.", claim),
                field("effective_from_utc", "TEXT", "audit_timestamp", "yes", "UTC start of schema-version validity.", "Migration audit run.", "ISO-8601 UTC text.", claim),
                field("effective_to_utc", "TEXT", "audit_timestamp", "yes", "UTC end of schema-version validity.", "Future migration governance.", "NULL while active.", claim),
                field("migration_phase_id", "TEXT", "foreign_key", "yes", "Migration phase that introduced this version.", "audit_migration_log phase ID.", "Must reference audit_migration_log phase context when present.", claim),
                field("ddl_manifest_ref", "TEXT", "payload_reference", "yes", "Reference to DDL manifest.", "Future DDL artifact.", "Reference only.", claim),
                field("audit_run_id", "TEXT", "foreign_key", "yes", "Audit run that created the schema version row.", "Migration audit run.", "Must reference audit_run.", claim),
                field("notes", "TEXT", "note", "yes", "Schema-version note.", "Migration note.", "No scientific outcome text.", claim),
            ],
        ),
        table(
            "audit_migration_log",
            "Audit / Provenance Sidecar",
            "Detailed migration ledger for target-schema rollout.",
            "One row per migration action or phase step.",
            "migration_log_id",
            "schema_version_id + phase_id + migration_action + target_object_name",
            "Future implementation migration runs.",
            "migrate_to_target_table",
            "P1",
            "Must be available before data migration phases begin.",
            [
                field("migration_log_id", "TEXT", "primary_key", "no", "Stable identifier for a migration-log row.", "Generated during migration.", "Unique, non-empty.", claim),
                field("schema_version_id", "TEXT", "foreign_key", "yes", "Schema version affected by the migration action.", "audit_schema_version.", "Must reference audit_schema_version when present.", claim),
                field("phase_id", "TEXT", "classification", "no", "Migration phase identifier.", "Migration phase plan.", "Must match approved phase plan.", claim),
                field("migration_action", "TEXT", "classification", "no", "Migration action label.", "Migration implementation.", "Controlled vocabulary.", claim),
                field("source_object_name", "TEXT", "lineage_attribute", "yes", "Current DB object used as input.", "Current sqlite_master object names.", "Preserve exact source object name.", claim),
                field("target_object_name", "TEXT", "lineage_attribute", "yes", "Target object affected by the migration.", "Target schema catalog.", "Must name approved target object.", claim),
                field("writes_db", "INTEGER", "flag", "no", "Boolean flag indicating DB writes.", "Migration run metadata.", "Must be 0 or 1.", claim),
                field("started_at_utc", "TEXT", "audit_timestamp", "yes", "UTC start time of migration action.", "Migration run metadata.", "ISO-8601 UTC text.", claim),
                field("completed_at_utc", "TEXT", "audit_timestamp", "yes", "UTC completion time of migration action.", "Migration run metadata.", "ISO-8601 UTC text.", claim),
                field("status", "TEXT", "classification", "no", "Migration action status.", "Migration run metadata.", "Controlled vocabulary.", claim),
                field("rollback_ref", "TEXT", "payload_reference", "yes", "Reference to rollback or restore plan.", "Migration plan.", "Reference only.", claim),
                field("audit_run_id", "TEXT", "foreign_key", "yes", "Audit run that executed the migration action.", "Migration audit run.", "Must reference audit_run.", claim),
                field("claim_boundary_id", "TEXT", "foreign_key", "yes", "Claim boundary governing the migration action.", "DWH claim-boundary catalog.", "Must reference audit_claim_boundary when assigned.", claim),
            ],
        ),
        table(
            "audit_lineage_event",
            "Audit / Provenance Sidecar",
            "Row/object lineage ledger connecting current objects to target objects.",
            "One row per lineage event.",
            "lineage_event_id",
            "source_object_table + source_object_id + target_object_table + target_object_id + lineage_action",
            "Current object inventory and future migration events.",
            "migrate_to_target_table",
            "P3",
            "Makes source-to-target movement explicit and queryable.",
            [
                field("lineage_event_id", "TEXT", "primary_key", "no", "Stable identifier for a lineage event.", "Generated during migration.", "Unique, non-empty.", claim),
                field("source_object_table", "TEXT", "classification", "yes", "Source table/object family name.", "Current sqlite_master object names.", "Preserve exact source object name.", claim),
                field("source_object_id", "TEXT", "lineage_attribute", "yes", "Source row/object identifier.", "Current source IDs.", "Preserve source-local ID.", claim),
                field("target_object_table", "TEXT", "classification", "yes", "Target table/object family name.", "Target schema catalog.", "Must name approved target object.", claim),
                field("target_object_id", "TEXT", "lineage_attribute", "yes", "Target row/object identifier.", "Target migration output.", "Must be non-empty when row-level lineage exists.", claim),
                field("lineage_action", "TEXT", "classification", "no", "Lineage action such as migrate, split, merge, retain, or supersede.", "Migration run metadata.", "Controlled vocabulary.", claim),
                field("lineage_key", "TEXT", "lineage_attribute", "yes", "Composite lineage key used by the migration.", "Current lineage fields.", "Preserve exact key.", claim),
                field("audit_run_id", "TEXT", "foreign_key", "yes", "Audit run that created the lineage event.", "Migration audit run.", "Must reference audit_run.", claim),
                field("claim_boundary_id", "TEXT", "foreign_key", "yes", "Claim boundary governing the lineage event.", "DWH claim-boundary catalog.", "Must reference audit_claim_boundary when assigned.", claim),
                field("notes", "TEXT", "note", "yes", "Lineage note for non-trivial transforms.", "Migration note.", "No scientific outcome text.", claim),
            ],
        ),
        table(
            "audit_view_dependency",
            "Audit / Provenance Sidecar",
            "Tracks report/view dependencies over target and legacy objects.",
            "One row per view dependency edge.",
            "view_dependency_id",
            "view_name + depends_on_object_name + dependency_type",
            "Current qsb_v_* view inventory and future target views.",
            "migrate_to_target_table",
            "P8",
            "Prevents report views from becoming hidden logic islands.",
            [
                field("view_dependency_id", "TEXT", "primary_key", "no", "Stable identifier for a view dependency row.", "Generated during migration.", "Unique, non-empty.", claim),
                field("view_name", "TEXT", "descriptor", "no", "View name.", "Current and target qsb_v_* views.", "Must name an existing or planned view.", claim),
                field("depends_on_object_name", "TEXT", "descriptor", "no", "Table or view used by the view.", "Parsed future view SQL or current sqlite_master SQL.", "Must name an inspected or planned object.", claim),
                field("dependency_type", "TEXT", "classification", "no", "Dependency type such as base_table, view, audit_sidecar, or legacy_source.", "View dependency extraction.", "Controlled vocabulary.", claim),
                field("dependency_status", "TEXT", "classification", "no", "Dependency status.", "Future validation.", "Controlled vocabulary.", claim),
                field("schema_version_id", "TEXT", "foreign_key", "yes", "Schema version where dependency is valid.", "audit_schema_version.", "Must reference audit_schema_version when present.", claim),
                field("audit_run_id", "TEXT", "foreign_key", "yes", "Audit run that created or validated the dependency.", "Migration audit run.", "Must reference audit_run.", claim),
                field("notes", "TEXT", "note", "yes", "Dependency note.", "Migration/rebuild note.", "No scientific outcome text.", claim),
            ],
        ),
        table(
            "audit_rebuild_manifest",
            "Audit / Provenance Sidecar",
            "Manifest for deterministic rebuild/parity checks.",
            "One row per rebuild manifest or rebuild attempt.",
            "rebuild_manifest_id",
            "schema_version_id + rebuild_run_id",
            "Future rebuild tests after migration phases.",
            "migrate_to_target_table",
            "P9",
            "Separates rebuild/parity controls from scientific result tables.",
            [
                field("rebuild_manifest_id", "TEXT", "primary_key", "no", "Stable identifier for a rebuild manifest.", "Generated during migration.", "Unique, non-empty.", claim),
                field("schema_version_id", "TEXT", "foreign_key", "yes", "Schema version being rebuilt or checked.", "audit_schema_version.", "Must reference audit_schema_version when present.", claim),
                field("rebuild_run_id", "TEXT", "foreign_key", "yes", "Audit run for the rebuild attempt.", "audit_run.", "Must reference audit_run when present.", claim),
                field("source_manifest_ref", "TEXT", "payload_reference", "yes", "Reference to source manifest.", "Future rebuild manifest.", "Reference only.", claim),
                field("expected_output_manifest_ref", "TEXT", "payload_reference", "yes", "Reference to expected output manifest.", "Future rebuild manifest.", "Reference only.", claim),
                field("row_count_parity_status", "TEXT", "classification", "no", "Status of row-count parity check.", "Future rebuild validation.", "Controlled vocabulary.", claim),
                field("fk_validation_status", "TEXT", "classification", "no", "Status of FK validation check.", "Future rebuild validation.", "Controlled vocabulary.", claim),
                field("checksum_status", "TEXT", "classification", "no", "Status of checksum comparison.", "Future rebuild validation.", "Controlled vocabulary.", claim),
                field("audit_run_id", "TEXT", "foreign_key", "yes", "Audit run that created the manifest row.", "Migration/rebuild audit run.", "Must reference audit_run.", claim),
                field("claim_boundary_id", "TEXT", "foreign_key", "yes", "Claim boundary governing rebuild reporting.", "DWH claim-boundary catalog.", "Must reference audit_claim_boundary when assigned.", claim),
            ],
        ),
        table(
            "audit_claim_boundary",
            "Audit / Provenance Sidecar",
            "Machine-queryable claim-boundary catalog.",
            "One row per claim boundary rule.",
            "claim_boundary_id",
            "boundary_label + applies_to_layer",
            "Current result-note claim boundaries and future governance rules.",
            "migrate_to_target_table",
            "P1",
            "Lets dashboards show what a row may and may not support.",
            [
                field("claim_boundary_id", "TEXT", "primary_key", "no", "Stable identifier for a claim-boundary rule.", "Generated during migration.", "Unique, non-empty.", claim),
                field("boundary_label", "TEXT", "descriptor", "no", "Short label for the boundary.", "Target governance rule.", "Non-empty.", claim),
                field("allowed_statement", "TEXT", "descriptor", "yes", "Defensive statement allowed by the rule.", "Current claim-boundary notes.", "Must be scoped to inspected data/run outputs.", claim),
                field("disallowed_statement", "TEXT", "descriptor", "yes", "Statement type excluded by the rule.", "Current claim-boundary notes.", "Must remain explicit.", claim),
                field("evidence_requirement", "TEXT", "descriptor", "yes", "Evidence or validation required before promotion.", "Target governance rule.", "Do not imply the requirement has been met.", claim),
                field("applies_to_layer", "TEXT", "classification", "no", "Layer governed by the boundary.", "Target layer catalog.", "Must match approved target layer.", claim),
                field("created_at_utc", "TEXT", "audit_timestamp", "yes", "UTC timestamp when the rule was created.", "Migration audit run.", "ISO-8601 UTC text.", claim),
                field("retired_at_utc", "TEXT", "audit_timestamp", "yes", "UTC timestamp when the rule was retired.", "Future governance run.", "NULL while active.", claim),
                field("audit_run_id", "TEXT", "foreign_key", "yes", "Audit run that created the rule.", "Migration audit run.", "Must reference audit_run when known.", claim),
            ],
        ),
    ]


def build_target_fks() -> list[TargetFk]:
    return [
        fk("raw_source_file", "source_registry_id", "core_source_registry", "source_registry_id", "many_to_one", "no", "Source files are owned by a conformed source registry entry.", "01 Raw / Entrance Layer"),
        fk("raw_source_file", "ingest_run_id", "raw_ingest_run", "ingest_run_id", "many_to_one", "no", "Source files can be linked to the ingest run that registered them.", "01 Raw / Entrance Layer"),
        fk("raw_source_file", "audit_run_id", "audit_run", "audit_run_id", "many_to_one", "no", "Source-file registration is auditable.", "07 Audit / Provenance Sidecar"),
        fk("raw_ingest_run", "audit_run_id", "audit_run", "audit_run_id", "one_to_one_or_many_to_one", "no", "Raw ingest runs are governed by audit runs.", "07 Audit / Provenance Sidecar"),
        fk("raw_ingest_run", "script_id", "audit_script", "script_id", "many_to_one", "no", "Ingest run references the script that ran it.", "07 Audit / Provenance Sidecar"),
        fk("raw_ingest_run", "source_registry_id", "core_source_registry", "source_registry_id", "many_to_one", "no", "Ingest run references the source registry it processed.", "01 Raw / Entrance Layer"),
        fk("raw_record", "source_file_id", "raw_source_file", "source_file_id", "many_to_one", "yes", "Raw records are contained by source files.", "01 Raw / Entrance Layer"),
        fk("raw_record", "ingest_run_id", "raw_ingest_run", "ingest_run_id", "many_to_one", "no", "Raw records link back to their ingest run.", "01 Raw / Entrance Layer"),
        fk("raw_record", "parse_status_id", "dim_quality_status", "quality_status_id", "many_to_one", "no", "Raw record parse status uses conformed quality status.", "03 Instrument / Time / Processing Snowflake"),
        fk("raw_record", "audit_run_id", "audit_run", "audit_run_id", "many_to_one", "no", "Raw-record migration is auditable.", "07 Audit / Provenance Sidecar"),
        fk("raw_field_value", "raw_record_id", "raw_record", "raw_record_id", "many_to_one", "yes", "Raw field values are contained by raw records.", "01 Raw / Entrance Layer"),
        fk("raw_field_value", "token_dictionary_id", "map_token_dictionary", "token_dictionary_id", "many_to_one", "no", "Raw field values can link to reviewed token dictionary entries.", "04 Token Mapping / Evidence Layer"),
        fk("raw_field_value", "quality_status_id", "dim_quality_status", "quality_status_id", "many_to_one", "no", "Raw value status uses conformed quality status.", "04 Token Mapping / Evidence Layer"),
        fk("raw_field_value", "audit_run_id", "audit_run", "audit_run_id", "many_to_one", "no", "Raw-field migration is auditable.", "07 Audit / Provenance Sidecar"),
        fk("core_source_registry", "audit_run_id", "audit_run", "audit_run_id", "many_to_one", "no", "Source registry rows are auditable.", "07 Audit / Provenance Sidecar"),
        fk("core_dataset", "source_registry_id", "core_source_registry", "source_registry_id", "many_to_one", "yes", "Datasets are owned by source registry entries.", "02 Core Observation Star"),
        fk("core_dataset", "audit_run_id", "audit_run", "audit_run_id", "many_to_one", "no", "Dataset migration is auditable.", "07 Audit / Provenance Sidecar"),
        fk("core_observation", "dataset_id", "core_dataset", "dataset_id", "many_to_one", "yes", "Observation is anchored to a dataset.", "02 Core Observation Star"),
        fk("core_observation", "science_object_id", "dim_science_object", "science_object_id", "many_to_one", "no", "Observation links to reviewed science-object context.", "02 Core Observation Star"),
        fk("core_observation", "time_context_id", "dim_time_context", "time_context_id", "many_to_one", "no", "Observation links to reviewed time context.", "03 Instrument / Time / Processing Snowflake"),
        fk("core_observation", "telescope_id", "dim_telescope", "telescope_id", "many_to_one", "no", "Observation links to telescope context.", "03 Instrument / Time / Processing Snowflake"),
        fk("core_observation", "receiver_id", "dim_receiver", "receiver_id", "many_to_one", "no", "Observation links to receiver context.", "03 Instrument / Time / Processing Snowflake"),
        fk("core_observation", "backend_id", "dim_backend", "backend_id", "many_to_one", "no", "Observation links to backend context.", "03 Instrument / Time / Processing Snowflake"),
        fk("core_observation", "processing_context_id", "dim_processing_context", "processing_context_id", "many_to_one", "no", "Observation links to processing context.", "03 Instrument / Time / Processing Snowflake"),
        fk("core_observation", "quality_status_id", "dim_quality_status", "quality_status_id", "many_to_one", "no", "Observation lifecycle/status uses conformed quality status.", "02 Core Observation Star"),
        fk("core_observation", "audit_run_id", "audit_run", "audit_run_id", "many_to_one", "no", "Observation creation/migration is auditable.", "07 Audit / Provenance Sidecar"),
        fk("core_observation", "claim_boundary_id", "audit_claim_boundary", "claim_boundary_id", "many_to_one", "no", "Observation rows can carry a queryable claim boundary.", "07 Audit / Provenance Sidecar"),
        fk("core_observation_record_link", "observation_id", "core_observation", "observation_id", "many_to_one", "yes", "Observation-record links attach raw records to the central anchor.", "02 Core Observation Star"),
        fk("core_observation_record_link", "raw_record_id", "raw_record", "raw_record_id", "many_to_one", "yes", "Observation-record links preserve raw lineage.", "02 Core Observation Star"),
        fk("core_observation_record_link", "created_by_review_decision_id", "map_review_decision", "review_decision_id", "many_to_one", "no", "Record-link decisions are reviewable.", "04 Token Mapping / Evidence Layer"),
        fk("core_observation_record_link", "audit_run_id", "audit_run", "audit_run_id", "many_to_one", "no", "Observation-record links are auditable.", "07 Audit / Provenance Sidecar"),
        fk("dim_science_object", "source_registry_id", "core_source_registry", "source_registry_id", "many_to_one", "no", "Science-object entries can cite their source registry.", "03 Instrument / Time / Processing Snowflake"),
        fk("dim_science_object", "external_source_id", "map_external_source", "external_source_id", "many_to_one", "no", "Science-object entries can cite external evidence sources.", "04 Token Mapping / Evidence Layer"),
        fk("dim_science_object", "evidence_status_id", "dim_quality_status", "quality_status_id", "many_to_one", "no", "Science-object evidence status is conformed.", "03 Instrument / Time / Processing Snowflake"),
        fk("dim_science_object", "audit_run_id", "audit_run", "audit_run_id", "many_to_one", "no", "Science-object dimension rows are auditable.", "07 Audit / Provenance Sidecar"),
        fk("dim_telescope", "external_source_id", "map_external_source", "external_source_id", "many_to_one", "no", "Telescope entries can cite external sources.", "04 Token Mapping / Evidence Layer"),
        fk("dim_telescope", "evidence_status_id", "dim_quality_status", "quality_status_id", "many_to_one", "no", "Telescope evidence status is conformed.", "03 Instrument / Time / Processing Snowflake"),
        fk("dim_telescope", "audit_run_id", "audit_run", "audit_run_id", "many_to_one", "no", "Telescope dimension rows are auditable.", "07 Audit / Provenance Sidecar"),
        fk("dim_receiver", "telescope_id", "dim_telescope", "telescope_id", "many_to_one", "no", "Receiver rows snowflake under telescope when known.", "03 Instrument / Time / Processing Snowflake"),
        fk("dim_receiver", "external_source_id", "map_external_source", "external_source_id", "many_to_one", "no", "Receiver entries can cite external sources.", "04 Token Mapping / Evidence Layer"),
        fk("dim_receiver", "evidence_status_id", "dim_quality_status", "quality_status_id", "many_to_one", "no", "Receiver evidence status is conformed.", "03 Instrument / Time / Processing Snowflake"),
        fk("dim_receiver", "audit_run_id", "audit_run", "audit_run_id", "many_to_one", "no", "Receiver dimension rows are auditable.", "07 Audit / Provenance Sidecar"),
        fk("dim_backend", "external_source_id", "map_external_source", "external_source_id", "many_to_one", "no", "Backend entries can cite external sources.", "04 Token Mapping / Evidence Layer"),
        fk("dim_backend", "evidence_status_id", "dim_quality_status", "quality_status_id", "many_to_one", "no", "Backend evidence status is conformed.", "03 Instrument / Time / Processing Snowflake"),
        fk("dim_backend", "audit_run_id", "audit_run", "audit_run_id", "many_to_one", "no", "Backend dimension rows are auditable.", "07 Audit / Provenance Sidecar"),
        fk("dim_time_context", "source_time_token_id", "map_token_dictionary", "token_dictionary_id", "many_to_one", "no", "Time-context rows can cite source tokens.", "04 Token Mapping / Evidence Layer"),
        fk("dim_time_context", "evidence_status_id", "dim_quality_status", "quality_status_id", "many_to_one", "no", "Time-context evidence status is conformed.", "03 Instrument / Time / Processing Snowflake"),
        fk("dim_time_context", "audit_run_id", "audit_run", "audit_run_id", "many_to_one", "no", "Time-context dimension rows are auditable.", "07 Audit / Provenance Sidecar"),
        fk("dim_processing_context", "script_id", "audit_script", "script_id", "many_to_one", "no", "Processing context links to the responsible script.", "07 Audit / Provenance Sidecar"),
        fk("dim_processing_context", "audit_run_id", "audit_run", "audit_run_id", "many_to_one", "no", "Processing-context dimension rows are auditable.", "07 Audit / Provenance Sidecar"),
        fk("dim_quality_status", "audit_run_id", "audit_run", "audit_run_id", "many_to_one", "no", "Quality-status vocabulary changes are auditable.", "07 Audit / Provenance Sidecar"),
        fk("map_token_dictionary", "first_seen_raw_field_value_id", "raw_field_value", "raw_field_value_id", "many_to_one", "no", "Dictionary entries can cite the first raw value where seen.", "04 Token Mapping / Evidence Layer"),
        fk("map_token_dictionary", "audit_run_id", "audit_run", "audit_run_id", "many_to_one", "no", "Token dictionary changes are auditable.", "07 Audit / Provenance Sidecar"),
        fk("map_token_dictionary", "claim_boundary_id", "audit_claim_boundary", "claim_boundary_id", "many_to_one", "no", "Token dictionary entries can carry claim boundaries.", "07 Audit / Provenance Sidecar"),
        fk("map_token_role", "token_dictionary_id", "map_token_dictionary", "token_dictionary_id", "many_to_one", "yes", "Token roles attach to token dictionary entries.", "04 Token Mapping / Evidence Layer"),
        fk("map_token_role", "review_decision_id", "map_review_decision", "review_decision_id", "many_to_one", "no", "Token roles can be governed by review decisions.", "04 Token Mapping / Evidence Layer"),
        fk("map_token_role", "evidence_gap_id", "map_evidence_gap", "evidence_gap_id", "many_to_one", "no", "Token roles can cite open evidence gaps.", "04 Token Mapping / Evidence Layer"),
        fk("map_token_role", "audit_run_id", "audit_run", "audit_run_id", "many_to_one", "no", "Token-role changes are auditable.", "07 Audit / Provenance Sidecar"),
        fk("map_token_role", "claim_boundary_id", "audit_claim_boundary", "claim_boundary_id", "many_to_one", "no", "Token-role entries can carry claim boundaries.", "07 Audit / Provenance Sidecar"),
        fk("map_token_value_assertion", "raw_field_value_id", "raw_field_value", "raw_field_value_id", "many_to_one", "yes", "Value assertions attach to raw field values.", "04 Token Mapping / Evidence Layer"),
        fk("map_token_value_assertion", "token_dictionary_id", "map_token_dictionary", "token_dictionary_id", "many_to_one", "yes", "Value assertions use dictionary entries.", "04 Token Mapping / Evidence Layer"),
        fk("map_token_value_assertion", "evidence_id", "map_assertion_evidence", "evidence_id", "many_to_one", "no", "Value assertions can cite evidence.", "04 Token Mapping / Evidence Layer"),
        fk("map_token_value_assertion", "review_decision_id", "map_review_decision", "review_decision_id", "many_to_one", "no", "Value assertions can cite review decisions.", "04 Token Mapping / Evidence Layer"),
        fk("map_token_value_assertion", "quality_status_id", "dim_quality_status", "quality_status_id", "many_to_one", "no", "Value assertion status is conformed.", "04 Token Mapping / Evidence Layer"),
        fk("map_token_value_assertion", "audit_run_id", "audit_run", "audit_run_id", "many_to_one", "no", "Value-assertion changes are auditable.", "07 Audit / Provenance Sidecar"),
        fk("map_token_value_assertion", "claim_boundary_id", "audit_claim_boundary", "claim_boundary_id", "many_to_one", "no", "Value assertions can carry claim boundaries.", "07 Audit / Provenance Sidecar"),
        fk("map_external_source", "audit_run_id", "audit_run", "audit_run_id", "many_to_one", "no", "External-source registry changes are auditable.", "07 Audit / Provenance Sidecar"),
        fk("map_assertion_evidence", "assertion_id", "map_token_value_assertion", "assertion_id", "many_to_one", "no", "Evidence rows can attach to token value assertions.", "04 Token Mapping / Evidence Layer"),
        fk("map_assertion_evidence", "external_source_id", "map_external_source", "external_source_id", "many_to_one", "no", "Evidence rows cite external sources.", "04 Token Mapping / Evidence Layer"),
        fk("map_assertion_evidence", "gap_id", "map_evidence_gap", "evidence_gap_id", "many_to_one", "no", "Evidence rows can cite gaps.", "04 Token Mapping / Evidence Layer"),
        fk("map_assertion_evidence", "audit_run_id", "audit_run", "audit_run_id", "many_to_one", "no", "Evidence rows are auditable.", "07 Audit / Provenance Sidecar"),
        fk("map_assertion_evidence", "claim_boundary_id", "audit_claim_boundary", "claim_boundary_id", "many_to_one", "no", "Evidence rows can carry claim boundaries.", "07 Audit / Provenance Sidecar"),
        fk("map_review_decision", "supersedes_decision_id", "map_review_decision", "review_decision_id", "self_reference", "no", "Review decisions can supersede earlier decisions.", "04 Token Mapping / Evidence Layer"),
        fk("map_review_decision", "audit_run_id", "audit_run", "audit_run_id", "many_to_one", "no", "Review decisions are auditable.", "07 Audit / Provenance Sidecar"),
        fk("map_review_decision", "claim_boundary_id", "audit_claim_boundary", "claim_boundary_id", "many_to_one", "no", "Review decisions can carry claim boundaries.", "07 Audit / Provenance Sidecar"),
        fk("map_evidence_gap", "audit_run_id", "audit_run", "audit_run_id", "many_to_one", "no", "Evidence gaps are auditable.", "07 Audit / Provenance Sidecar"),
        fk("map_evidence_gap", "claim_boundary_id", "audit_claim_boundary", "claim_boundary_id", "many_to_one", "no", "Evidence gaps can carry claim boundaries.", "07 Audit / Provenance Sidecar"),
        fk("fact_token_observation", "observation_id", "core_observation", "observation_id", "many_to_one", "yes", "Token facts are observation-centered.", "02 Core Observation Star"),
        fk("fact_token_observation", "raw_field_value_id", "raw_field_value", "raw_field_value_id", "many_to_one", "yes", "Token facts preserve raw field lineage.", "04 Token Mapping / Evidence Layer"),
        fk("fact_token_observation", "token_dictionary_id", "map_token_dictionary", "token_dictionary_id", "many_to_one", "no", "Token facts can link to dictionary entries.", "04 Token Mapping / Evidence Layer"),
        fk("fact_token_observation", "token_role_id", "map_token_role", "token_role_id", "many_to_one", "no", "Token facts can link to reviewed roles.", "04 Token Mapping / Evidence Layer"),
        fk("fact_token_observation", "asserted_value_id", "map_token_value_assertion", "assertion_id", "many_to_one", "no", "Token facts can link to value assertions.", "04 Token Mapping / Evidence Layer"),
        fk("fact_token_observation", "quality_status_id", "dim_quality_status", "quality_status_id", "many_to_one", "no", "Token fact status is conformed.", "04 Token Mapping / Evidence Layer"),
        fk("fact_token_observation", "audit_run_id", "audit_run", "audit_run_id", "many_to_one", "no", "Token facts are auditable.", "07 Audit / Provenance Sidecar"),
        fk("fact_token_observation", "claim_boundary_id", "audit_claim_boundary", "claim_boundary_id", "many_to_one", "no", "Token facts can carry claim boundaries.", "07 Audit / Provenance Sidecar"),
        fk("fact_signal_observation", "observation_id", "core_observation", "observation_id", "many_to_one", "yes", "Signal facts are observation-centered.", "02 Core Observation Star"),
        fk("fact_signal_observation", "measurement_token_id", "fact_token_observation", "token_observation_id", "many_to_one", "no", "Signal facts can be promoted from token observations.", "06 Result / Evaluation Layer"),
        fk("fact_signal_observation", "quality_status_id", "dim_quality_status", "quality_status_id", "many_to_one", "no", "Signal fact status is conformed.", "06 Result / Evaluation Layer"),
        fk("fact_signal_observation", "evidence_id", "map_assertion_evidence", "evidence_id", "many_to_one", "no", "Signal facts can cite mapping evidence.", "04 Token Mapping / Evidence Layer"),
        fk("fact_signal_observation", "audit_run_id", "audit_run", "audit_run_id", "many_to_one", "no", "Signal facts are auditable.", "07 Audit / Provenance Sidecar"),
        fk("fact_signal_observation", "claim_boundary_id", "audit_claim_boundary", "claim_boundary_id", "many_to_one", "no", "Signal facts can carry claim boundaries.", "07 Audit / Provenance Sidecar"),
        fk("fact_block_signature", "observation_id", "core_observation", "observation_id", "many_to_one", "no", "Block signatures can be observation-centered.", "02 Core Observation Star"),
        fk("fact_block_signature", "raw_record_id", "raw_record", "raw_record_id", "many_to_one", "no", "Block signatures can preserve raw record lineage.", "01 Raw / Entrance Layer"),
        fk("fact_block_signature", "source_file_id", "raw_source_file", "source_file_id", "many_to_one", "no", "Block signatures can preserve source-file lineage.", "01 Raw / Entrance Layer"),
        fk("fact_block_signature", "quality_status_id", "dim_quality_status", "quality_status_id", "many_to_one", "no", "Block signature status is conformed.", "06 Result / Evaluation Layer"),
        fk("fact_block_signature", "audit_run_id", "audit_run", "audit_run_id", "many_to_one", "no", "Block signature facts are auditable.", "07 Audit / Provenance Sidecar"),
        fk("fact_block_signature", "claim_boundary_id", "audit_claim_boundary", "claim_boundary_id", "many_to_one", "no", "Block signature facts can carry claim boundaries.", "07 Audit / Provenance Sidecar"),
        fk("bridge_qm_quantity", "source_token_role_id", "map_token_role", "token_role_id", "many_to_one", "no", "QM quantity candidates can cite reviewed token roles.", "05 Bridge Relation Layer"),
        fk("bridge_qm_quantity", "evidence_id", "map_assertion_evidence", "evidence_id", "many_to_one", "no", "QM quantity candidates can cite evidence.", "05 Bridge Relation Layer"),
        fk("bridge_qm_quantity", "audit_run_id", "audit_run", "audit_run_id", "many_to_one", "no", "QM quantity rows are auditable.", "07 Audit / Provenance Sidecar"),
        fk("bridge_qm_quantity", "claim_boundary_id", "audit_claim_boundary", "claim_boundary_id", "many_to_one", "no", "QM quantity rows can carry claim boundaries.", "07 Audit / Provenance Sidecar"),
        fk("bridge_art_quantity", "source_token_role_id", "map_token_role", "token_role_id", "many_to_one", "no", "ART quantity candidates can cite reviewed token roles.", "05 Bridge Relation Layer"),
        fk("bridge_art_quantity", "evidence_id", "map_assertion_evidence", "evidence_id", "many_to_one", "no", "ART quantity candidates can cite evidence.", "05 Bridge Relation Layer"),
        fk("bridge_art_quantity", "audit_run_id", "audit_run", "audit_run_id", "many_to_one", "no", "ART quantity rows are auditable.", "07 Audit / Provenance Sidecar"),
        fk("bridge_art_quantity", "claim_boundary_id", "audit_claim_boundary", "claim_boundary_id", "many_to_one", "no", "ART quantity rows can carry claim boundaries.", "07 Audit / Provenance Sidecar"),
        fk("bridge_functional_relation", "qm_quantity_id", "bridge_qm_quantity", "qm_quantity_id", "many_to_one", "yes", "Functional relations connect to QM-side quantity definitions.", "05 Bridge Relation Layer"),
        fk("bridge_functional_relation", "art_quantity_id", "bridge_art_quantity", "art_quantity_id", "many_to_one", "yes", "Functional relations connect to ART-side quantity definitions.", "05 Bridge Relation Layer"),
        fk("bridge_functional_relation", "evidence_id", "map_assertion_evidence", "evidence_id", "many_to_one", "no", "Functional relations can cite evidence.", "05 Bridge Relation Layer"),
        fk("bridge_functional_relation", "audit_run_id", "audit_run", "audit_run_id", "many_to_one", "no", "Functional relation rows are auditable.", "07 Audit / Provenance Sidecar"),
        fk("bridge_functional_relation", "claim_boundary_id", "audit_claim_boundary", "claim_boundary_id", "many_to_one", "no", "Functional relation rows can carry claim boundaries.", "07 Audit / Provenance Sidecar"),
        fk("bridge_relation_context_condition", "relation_id", "bridge_functional_relation", "relation_id", "many_to_one", "yes", "Context conditions attach to relation definitions.", "05 Bridge Relation Layer"),
        fk("bridge_relation_context_condition", "evidence_id", "map_assertion_evidence", "evidence_id", "many_to_one", "no", "Context conditions can cite evidence.", "05 Bridge Relation Layer"),
        fk("bridge_relation_context_condition", "audit_run_id", "audit_run", "audit_run_id", "many_to_one", "no", "Context condition rows are auditable.", "07 Audit / Provenance Sidecar"),
        fk("bridge_relation_context_condition", "claim_boundary_id", "audit_claim_boundary", "claim_boundary_id", "many_to_one", "no", "Context condition rows can carry claim boundaries.", "07 Audit / Provenance Sidecar"),
        fk("bridge_candidate_connection", "relation_id", "bridge_functional_relation", "relation_id", "many_to_one", "yes", "Candidate connections instantiate relation definitions.", "05 Bridge Relation Layer"),
        fk("bridge_candidate_connection", "observation_id", "core_observation", "observation_id", "many_to_one", "yes", "Candidate connections are observation-centered.", "05 Bridge Relation Layer"),
        fk("bridge_candidate_connection", "qm_quantity_id", "bridge_qm_quantity", "qm_quantity_id", "many_to_one", "no", "Candidate connections can cite the QM-side quantity.", "05 Bridge Relation Layer"),
        fk("bridge_candidate_connection", "art_quantity_id", "bridge_art_quantity", "art_quantity_id", "many_to_one", "no", "Candidate connections can cite the ART-side quantity.", "05 Bridge Relation Layer"),
        fk("bridge_candidate_connection", "audit_run_id", "audit_run", "audit_run_id", "many_to_one", "no", "Candidate connection rows are auditable.", "07 Audit / Provenance Sidecar"),
        fk("bridge_candidate_connection", "claim_boundary_id", "audit_claim_boundary", "claim_boundary_id", "many_to_one", "no", "Candidate connection rows can carry claim boundaries.", "07 Audit / Provenance Sidecar"),
        fk("fact_relation_evaluation", "bridge_candidate_connection_id", "bridge_candidate_connection", "bridge_candidate_connection_id", "many_to_one", "yes", "Evaluation rows attach to candidate connections.", "06 Result / Evaluation Layer"),
        fk("fact_relation_evaluation", "observation_id", "core_observation", "observation_id", "many_to_one", "yes", "Evaluation rows remain observation-centered.", "06 Result / Evaluation Layer"),
        fk("fact_relation_evaluation", "relation_id", "bridge_functional_relation", "relation_id", "many_to_one", "yes", "Evaluation rows cite the relation definition.", "06 Result / Evaluation Layer"),
        fk("fact_relation_evaluation", "evaluation_run_id", "audit_run", "audit_run_id", "many_to_one", "no", "Evaluation rows cite their future audit run.", "07 Audit / Provenance Sidecar"),
        fk("fact_relation_evaluation", "quality_status_id", "dim_quality_status", "quality_status_id", "many_to_one", "no", "Evaluation status is conformed.", "06 Result / Evaluation Layer"),
        fk("fact_relation_evaluation", "evidence_id", "map_assertion_evidence", "evidence_id", "many_to_one", "no", "Evaluation rows can cite evidence chains.", "06 Result / Evaluation Layer"),
        fk("fact_relation_evaluation", "claim_boundary_id", "audit_claim_boundary", "claim_boundary_id", "many_to_one", "no", "Evaluation rows can carry claim boundaries.", "07 Audit / Provenance Sidecar"),
        fk("fact_delta_result", "relation_evaluation_id", "fact_relation_evaluation", "relation_evaluation_id", "many_to_one", "yes", "Delta rows attach to relation evaluations.", "06 Result / Evaluation Layer"),
        fk("fact_delta_result", "observation_id", "core_observation", "observation_id", "many_to_one", "yes", "Delta rows remain observation-centered.", "06 Result / Evaluation Layer"),
        fk("fact_delta_result", "quality_status_id", "dim_quality_status", "quality_status_id", "many_to_one", "no", "Delta status is conformed.", "06 Result / Evaluation Layer"),
        fk("fact_delta_result", "audit_run_id", "audit_run", "audit_run_id", "many_to_one", "no", "Delta rows are auditable.", "07 Audit / Provenance Sidecar"),
        fk("fact_delta_result", "claim_boundary_id", "audit_claim_boundary", "claim_boundary_id", "many_to_one", "no", "Delta rows can carry claim boundaries.", "07 Audit / Provenance Sidecar"),
        fk("fact_control_check", "relation_evaluation_id", "fact_relation_evaluation", "relation_evaluation_id", "many_to_one", "yes", "Control checks attach to relation evaluations.", "06 Result / Evaluation Layer"),
        fk("fact_control_check", "observation_id", "core_observation", "observation_id", "many_to_one", "no", "Control checks can remain observation-centered.", "06 Result / Evaluation Layer"),
        fk("fact_control_check", "quality_status_id", "dim_quality_status", "quality_status_id", "many_to_one", "no", "Control status is conformed.", "06 Result / Evaluation Layer"),
        fk("fact_control_check", "audit_run_id", "audit_run", "audit_run_id", "many_to_one", "no", "Control rows are auditable.", "07 Audit / Provenance Sidecar"),
        fk("fact_control_check", "claim_boundary_id", "audit_claim_boundary", "claim_boundary_id", "many_to_one", "no", "Control rows can carry claim boundaries.", "07 Audit / Provenance Sidecar"),
        fk("fact_modulation_recovery", "relation_evaluation_id", "fact_relation_evaluation", "relation_evaluation_id", "many_to_one", "yes", "Recovery rows attach to relation evaluations.", "06 Result / Evaluation Layer"),
        fk("fact_modulation_recovery", "observation_id", "core_observation", "observation_id", "many_to_one", "no", "Recovery rows can remain observation-centered.", "06 Result / Evaluation Layer"),
        fk("fact_modulation_recovery", "quality_status_id", "dim_quality_status", "quality_status_id", "many_to_one", "no", "Recovery status is conformed.", "06 Result / Evaluation Layer"),
        fk("fact_modulation_recovery", "evidence_id", "map_assertion_evidence", "evidence_id", "many_to_one", "no", "Recovery rows can cite evidence chains.", "06 Result / Evaluation Layer"),
        fk("fact_modulation_recovery", "audit_run_id", "audit_run", "audit_run_id", "many_to_one", "no", "Recovery rows are auditable.", "07 Audit / Provenance Sidecar"),
        fk("fact_modulation_recovery", "claim_boundary_id", "audit_claim_boundary", "claim_boundary_id", "many_to_one", "no", "Recovery rows can carry claim boundaries.", "07 Audit / Provenance Sidecar"),
        fk("audit_run", "script_id", "audit_script", "script_id", "many_to_one", "yes", "Runs are anchored to script identities.", "07 Audit / Provenance Sidecar"),
        fk("audit_run", "claim_boundary_id", "audit_claim_boundary", "claim_boundary_id", "many_to_one", "no", "Runs can carry claim boundaries.", "07 Audit / Provenance Sidecar"),
        fk("audit_schema_version", "audit_run_id", "audit_run", "audit_run_id", "many_to_one", "no", "Schema-version changes are auditable.", "07 Audit / Provenance Sidecar"),
        fk("audit_migration_log", "schema_version_id", "audit_schema_version", "schema_version_id", "many_to_one", "no", "Migration actions can attach to schema versions.", "07 Audit / Provenance Sidecar"),
        fk("audit_migration_log", "audit_run_id", "audit_run", "audit_run_id", "many_to_one", "no", "Migration actions are auditable.", "07 Audit / Provenance Sidecar"),
        fk("audit_migration_log", "claim_boundary_id", "audit_claim_boundary", "claim_boundary_id", "many_to_one", "no", "Migration logs can carry claim boundaries.", "07 Audit / Provenance Sidecar"),
        fk("audit_lineage_event", "audit_run_id", "audit_run", "audit_run_id", "many_to_one", "no", "Lineage events are auditable.", "07 Audit / Provenance Sidecar"),
        fk("audit_lineage_event", "claim_boundary_id", "audit_claim_boundary", "claim_boundary_id", "many_to_one", "no", "Lineage events can carry claim boundaries.", "07 Audit / Provenance Sidecar"),
        fk("audit_view_dependency", "schema_version_id", "audit_schema_version", "schema_version_id", "many_to_one", "no", "View dependencies are version-scoped.", "07 Audit / Provenance Sidecar"),
        fk("audit_view_dependency", "audit_run_id", "audit_run", "audit_run_id", "many_to_one", "no", "View dependency scans are auditable.", "07 Audit / Provenance Sidecar"),
        fk("audit_rebuild_manifest", "schema_version_id", "audit_schema_version", "schema_version_id", "many_to_one", "no", "Rebuild manifests are schema-version scoped.", "07 Audit / Provenance Sidecar"),
        fk("audit_rebuild_manifest", "rebuild_run_id", "audit_run", "audit_run_id", "many_to_one", "no", "Rebuild manifests cite the rebuild audit run.", "07 Audit / Provenance Sidecar"),
        fk("audit_rebuild_manifest", "audit_run_id", "audit_run", "audit_run_id", "many_to_one", "no", "Rebuild manifest row creation is auditable.", "07 Audit / Provenance Sidecar"),
        fk("audit_rebuild_manifest", "claim_boundary_id", "audit_claim_boundary", "claim_boundary_id", "many_to_one", "no", "Rebuild manifests can carry claim boundaries.", "07 Audit / Provenance Sidecar"),
        fk("audit_claim_boundary", "audit_run_id", "audit_run", "audit_run_id", "many_to_one", "no", "Claim-boundary rules can be tied to the run that introduced them.", "07 Audit / Provenance Sidecar"),
    ]


REPORT_VIEWS = [
    {
        "view_name": "qsb_v_current_research_dwh_dashboard",
        "purpose": "High-level counts, status, open gaps, migration phase, and claim-boundary status.",
        "base_objects": "core_dataset; core_observation; fact_token_observation; bridge_candidate_connection; audit_run; audit_claim_boundary",
    },
    {
        "view_name": "qsb_v_observation_context",
        "purpose": "Observation-centered context join across dataset, object, instrument, time, processing, and status dimensions.",
        "base_objects": "core_observation; core_dataset; dim_science_object; dim_telescope; dim_receiver; dim_backend; dim_time_context; dim_processing_context; dim_quality_status",
    },
    {
        "view_name": "qsb_v_raw_to_observation_lineage",
        "purpose": "Raw file/record/field lineage from entrance layer into observation anchors.",
        "base_objects": "raw_source_file; raw_record; raw_field_value; core_observation_record_link; core_observation; audit_lineage_event",
    },
    {
        "view_name": "qsb_v_token_mapping_status",
        "purpose": "Token dictionary, role, assertion, review, quality, and open-gap status.",
        "base_objects": "map_token_dictionary; map_token_role; map_token_value_assertion; map_review_decision; map_evidence_gap; dim_quality_status",
    },
    {
        "view_name": "qsb_v_external_evidence_status",
        "purpose": "External source, evidence item, support status, and evidence gap dashboard.",
        "base_objects": "map_external_source; map_assertion_evidence; map_evidence_gap; audit_claim_boundary",
    },
    {
        "view_name": "qsb_v_bridge_candidate_matrix",
        "purpose": "Candidate connection matrix across observations, quantities, relations, context conditions, evidence, and claim boundaries.",
        "base_objects": "bridge_candidate_connection; bridge_functional_relation; bridge_qm_quantity; bridge_art_quantity; bridge_relation_context_condition; core_observation; map_assertion_evidence",
    },
    {
        "view_name": "qsb_v_relation_evaluation_readiness",
        "purpose": "Readiness of future relation evaluations based on candidate, evidence, context, control, and blocker status.",
        "base_objects": "bridge_candidate_connection; bridge_relation_context_condition; fact_relation_evaluation; fact_control_check; map_evidence_gap; dim_quality_status",
    },
    {
        "view_name": "qsb_v_claim_boundary_dashboard",
        "purpose": "Claim-boundary coverage across observations, mappings, bridge candidates, result rows, runs, and migration phases.",
        "base_objects": "audit_claim_boundary; core_observation; map_token_dictionary; bridge_candidate_connection; fact_relation_evaluation; audit_run; audit_migration_log",
    },
    {
        "view_name": "qsb_v_rebuild_status",
        "purpose": "Rebuild, checksum, row-count parity, FK validation, schema version, and migration status.",
        "base_objects": "audit_rebuild_manifest; audit_schema_version; audit_migration_log; audit_run; audit_view_dependency",
    },
]


def build_erd_slices() -> list[ErdSlice]:
    return [
        ErdSlice("01", "Raw / Entrance Layer", "raw_source_file; raw_ingest_run; raw_record; raw_field_value; core_source_registry; audit_run", "qsb_v_raw_to_observation_lineage", "How do source files and raw records enter the DWH and remain traceable?", "Data engineering and audit reviewers", "P1", "Focus on payload references, checksums, raw record lineage, and ingest audit."),
        ErdSlice("02", "Core Observation Star", "core_source_registry; core_dataset; core_observation; core_observation_record_link; dim_science_object; dim_quality_status", "qsb_v_observation_context", "What is the central observation anchor and how does it connect to source and context?", "Research data model reviewers", "P1", "Use this as the main target ERD slice for implementation review."),
        ErdSlice("03", "Instrument / Time / Processing Snowflake", "core_observation; dim_telescope; dim_receiver; dim_backend; dim_time_context; dim_processing_context; dim_quality_status; audit_script; audit_run", "qsb_v_observation_context", "Which conformed dimensions describe instrument, time, and processing context?", "Domain reviewers and data engineers", "P2", "Show nullable context paths and unresolved status handling."),
        ErdSlice("04", "Token Mapping / Evidence Layer", "raw_field_value; map_token_dictionary; map_token_role; map_token_value_assertion; map_external_source; map_assertion_evidence; map_review_decision; map_evidence_gap; dim_quality_status; audit_claim_boundary", "qsb_v_token_mapping_status; qsb_v_external_evidence_status", "How do raw tokens become reviewed, evidence-linked mapping objects?", "Mapping reviewers and audit reviewers", "P1", "Highlight gaps, review decisions, and claim-boundary gates."),
        ErdSlice("05", "Bridge Relation Layer", "core_observation; bridge_qm_quantity; bridge_art_quantity; bridge_functional_relation; bridge_relation_context_condition; bridge_candidate_connection; map_assertion_evidence; audit_claim_boundary", "qsb_v_bridge_candidate_matrix", "How can candidate QM/ART relation objects be connected without evaluating them?", "Research architects", "P1", "This slice defines operational connection objects only."),
        ErdSlice("06", "Result / Evaluation Layer", "bridge_candidate_connection; fact_relation_evaluation; fact_delta_result; fact_control_check; fact_modulation_recovery; core_observation; dim_quality_status; audit_run; audit_claim_boundary", "qsb_v_relation_evaluation_readiness", "What future result/evaluation rows are required for expected, observed, delta, control, and failure-mode reporting?", "Research architects and validation reviewers", "P2", "All result rows remain audit-run and claim-boundary gated."),
        ErdSlice("07", "Audit / Provenance Sidecar", "audit_script; audit_run; audit_schema_version; audit_migration_log; audit_lineage_event; audit_view_dependency; audit_rebuild_manifest; audit_claim_boundary", "qsb_v_claim_boundary_dashboard; qsb_v_rebuild_status", "How are schema, runs, scripts, migrations, lineage, rebuild checks, and claim boundaries governed?", "Audit reviewers and maintainers", "P1", "Must be implemented early because all other layers depend on it."),
        ErdSlice("08", "Full High-Level QSB Research DWH", "All target raw_*, core_*, dim_*, map_*, bridge_*, fact_*, audit_* tables", "All qsb_v_* target views", "How does the full target DWH connect source, observation, mapping, evidence, bridge candidates, results, and audit controls?", "Project leads and architecture reviewers", "P3", "Use a simplified high-level export; detailed work should use slices 01-07."),
    ]


def build_migration_phases() -> list[MigrationPhase]:
    return [
        MigrationPhase("Phase 0", "freeze current DB and create backup/workcopy", "Establish immutable source snapshot and writable workcopy before any target DDL.", "no on source DB; yes on workcopy setup", "yes", "qsb_research_consolidated_snapshot.db", "backup DB; workcopy DB; manifest entry", "Backup exists; source checksum recorded; workcopy path distinct from source.", "Restore from frozen backup; discard workcopy.", "low", "DWH01 itself does not perform this phase."),
        MigrationPhase("Phase 1", "create audit_schema_version and audit_migration_log", "Create minimal audit schema governance before target data movement.", "yes on workcopy", "yes", "workcopy DB; DDL proposal", "audit_schema_version; audit_migration_log; seed audit_run/audit_script as needed", "DDL succeeds; sqlite_master contains audit tables; FK pragma clean.", "Restore workcopy from Phase 0 backup.", "medium", "This is the recommended next implementation step."),
        MigrationPhase("Phase 2", "create target raw/core tables", "Create raw entrance and core observation tables with PK/FK constraints.", "yes on workcopy", "yes", "Phase 1 workcopy; target DDL", "raw_*; core_* tables", "DDL succeeds; required indexes exist; no legacy objects removed.", "Drop only newly created target tables in workcopy or restore backup.", "medium", "Keep legacy DBXX tables intact."),
        MigrationPhase("Phase 3", "populate source/dataset/observation/raw target tables from current DB", "Migrate entrance records, datasets, and observation anchors with lineage events.", "yes on workcopy", "yes", "raw/db20/db21/db22/db23/db23a/db23b/db25 objects", "raw_source_file; raw_ingest_run; raw_record; raw_field_value; core_source_registry; core_dataset; core_observation; core_observation_record_link; audit_lineage_event", "Row-count parity by source family; orphan checks; unresolved mappings remain status-coded.", "Restore workcopy or reverse migration batch using audit_migration_log.", "high", "Do not assign final semantic meaning during migration."),
        MigrationPhase("Phase 4", "create dimensions and context tables", "Create and seed conformed context dimensions.", "yes on workcopy", "yes", "raw/core target tables; mapping candidates; source metadata", "dim_science_object; dim_telescope; dim_receiver; dim_backend; dim_time_context; dim_processing_context; dim_quality_status", "Dimension natural-key uniqueness; observation FK checks; unresolved context statuses explicit.", "Restore workcopy or delete Phase 4 rows by audit_run_id.", "medium", "Dimension conformance requires review gates."),
        MigrationPhase("Phase 5", "migrate mapping/evidence tables", "Move token dictionary, role, assertion, evidence, review, and gap objects into target map_* layer.", "yes on workcopy", "yes", "db26/db27/db28 objects; raw_field_value; dim_quality_status", "map_token_dictionary; map_token_role; map_token_value_assertion; map_external_source; map_assertion_evidence; map_review_decision; map_evidence_gap", "Mapping row counts; evidence links; open gaps; no unresolved numeric canonicalization.", "Restore workcopy or delete Phase 5 rows by audit_run_id.", "high", "Do not promote analog labels outside reviewed scope."),
        MigrationPhase("Phase 6", "create bridge relation catalog skeleton", "Create QM/ART quantity, relation, context-condition, and candidate-connection skeletons.", "yes on workcopy", "yes", "bridge01 objects; map_* evidence; core_observation", "bridge_qm_quantity; bridge_art_quantity; bridge_functional_relation; bridge_relation_context_condition; bridge_candidate_connection", "All bridge rows have relation/status/evidence/claim-boundary gates; no result rows required.", "Restore workcopy or delete Phase 6 rows by audit_run_id.", "high", "Design/readiness only; no relation test."),
        MigrationPhase("Phase 7", "create result/evaluation skeleton", "Create future result tables without populating evaluated values.", "yes on workcopy", "yes", "bridge_candidate_connection; audit_run; dim_quality_status", "fact_relation_evaluation; fact_delta_result; fact_control_check; fact_modulation_recovery", "Tables empty or status-skeleton only; FK constraints clean; claim boundaries present.", "Restore workcopy or drop Phase 7 target tables.", "medium", "No expected/observed/delta values should be populated in this phase unless separately approved later."),
        MigrationPhase("Phase 8", "build views over target schema", "Create report/query views over target tables.", "yes on workcopy", "yes", "target raw/core/dim/map/bridge/fact/audit tables", "qsb_v_current_research_dwh_dashboard and related qsb_v_* views", "Views compile; dependency registry populated; no hidden source-only logic.", "Drop target views or restore workcopy.", "medium", "Views should be report surfaces, not uncontrolled transformation layers."),
        MigrationPhase("Phase 9", "row-count parity and FK validation", "Validate row-count parity, orphan counts, FK checks, and status coverage.", "yes on audit tables only", "yes", "target tables; legacy DBXX tables; audit_migration_log", "audit_rebuild_manifest; validation rows", "PRAGMA foreign_key_check clean; parity exceptions documented; warnings listed.", "Restore workcopy or mark phase failed and keep audit trail.", "high", "Do not silently accept parity gaps."),
        MigrationPhase("Phase 10", "ERD export and visual inspection", "Export ERD slices and inspect for disconnected tables or unclear paths.", "yes on audit tables only", "yes", "target schema; audit_view_dependency; ERD slice plan", "ERD exports; audit review notes", "All central target objects reachable; dead ends documented or fixed.", "Keep schema but mark ERD review failed until corrected.", "medium", "Use slices before full high-level diagram."),
        MigrationPhase("Phase 11", "rebuild test from raw/staged sources", "Test deterministic rebuild from approved source/staging inputs into target workcopy.", "yes on workcopy/test DB", "yes", "approved raw/staging sources; target migration scripts; manifests", "rebuild test DB; audit_rebuild_manifest rows", "Checksum status; row-count parity; FK validation; view row counts.", "Discard rebuild test DB; retain audit report.", "high", "If enumeration order differs from earlier runners, label affected outputs as not order-certified."),
        MigrationPhase("Phase 12", "mark target schema as current", "Promote target schema only after parity, FK, ERD, rebuild, and claim-boundary checks pass.", "yes on workcopy/current DB", "yes", "validated target workcopy; audit logs; review sign-off", "active audit_schema_version; current-schema marker", "All previous phases passed; no unresolved critical gaps; source snapshot preserved.", "Revert current marker to previous schema version; restore from backup if needed.", "high", "Do not delete legacy DBXX objects until a separate retirement decision."),
    ]


def connect_readonly(path: Path) -> sqlite3.Connection:
    con = sqlite3.connect(f"file:{path.resolve()}?mode=ro", uri=True)
    con.row_factory = sqlite3.Row
    return con


def list_sqlite_objects(con: sqlite3.Connection) -> list[dict[str, Any]]:
    rows = con.execute(
        """
        SELECT name, type, sql
        FROM sqlite_master
        WHERE type IN ('table', 'view')
          AND name NOT LIKE 'sqlite_%'
        ORDER BY type, name
        """
    ).fetchall()
    return [dict(row) for row in rows]


def pragma_table_info(con: sqlite3.Connection, object_name: str) -> list[dict[str, Any]]:
    try:
        rows = con.execute(f"PRAGMA table_info({quote_identifier(object_name)})").fetchall()
    except sqlite3.DatabaseError:
        return []
    return [dict(row) for row in rows]


def pragma_fk_list(con: sqlite3.Connection, table_name: str) -> list[dict[str, Any]]:
    try:
        rows = con.execute(f"PRAGMA foreign_key_list({quote_identifier(table_name)})").fetchall()
    except sqlite3.DatabaseError:
        return []
    return [dict(row) for row in rows]


def pragma_index_list(con: sqlite3.Connection, table_name: str) -> list[dict[str, Any]]:
    try:
        rows = con.execute(f"PRAGMA index_list({quote_identifier(table_name)})").fetchall()
    except sqlite3.DatabaseError:
        return []
    return [dict(row) for row in rows]


def pragma_index_info(con: sqlite3.Connection, index_name: str) -> list[dict[str, Any]]:
    try:
        rows = con.execute(f"PRAGMA index_info({quote_identifier(index_name)})").fetchall()
    except sqlite3.DatabaseError:
        return []
    return [dict(row) for row in rows]


def table_row_count(con: sqlite3.Connection, table_name: str) -> int | None:
    try:
        row = con.execute(
            f"SELECT COUNT(*) AS row_count FROM {quote_identifier(table_name)}"
        ).fetchone()
    except sqlite3.DatabaseError:
        return None
    return int(row["row_count"])


def classify_current_family(name: str) -> str:
    lower = name.lower()
    if lower.startswith("qsb_v_"):
        return "qsb_v"
    if lower.startswith("bridge01"):
        return "bridge01"
    for prefix in ("raw", "db20", "db21", "db22", "db23a", "db23b", "db23", "db25", "db26", "db27", "db28"):
        if lower.startswith(prefix + "_") or lower == prefix:
            return prefix
    if any(term in lower for term in ("raw", "source", "record", "field")):
        return "raw"
    return "other"


def classify_current_role(name: str, object_type: str, fields: list[dict[str, Any]]) -> str:
    lower = name.lower()
    field_names = " ".join(str(row.get("name", "")).lower() for row in fields)
    combined = lower + " " + field_names
    if object_type == "view":
        return "report/query view"
    if "run" in combined or "log" in combined or "manifest" in combined:
        return "run/audit/consolidation metadata"
    if "source" in combined or "file" in combined:
        return "source/raw entrance inventory"
    if "record" in combined or "line" in combined:
        return "raw or staged record inventory"
    if "token" in combined or "field" in combined or "mapping" in combined:
        return "token/mapping/evidence staging"
    if "evidence" in combined or "external" in combined or "gap" in combined:
        return "external evidence or gap staging"
    if "bridge" in combined or "candidate" in combined or "relation" in combined:
        return "bridge design/readiness staging"
    if "count" in combined or "inventory" in combined:
        return "inventory/report metadata"
    return "legacy research artifact"


def target_for_current_object(name: str, object_type: str, family: str, role: str) -> tuple[str, str, str, str]:
    lower = name.lower()
    role_lower = role.lower()
    if object_type == "view" or family == "qsb_v":
        return (
            "Report / View Layer",
            choose_target_view(lower),
            "convert_to_view",
            "P8",
        )
    if family == "raw":
        if "file" in lower or "source" in lower:
            target = "raw_source_file"
        elif "field" in lower or "token" in lower:
            target = "raw_field_value"
        else:
            target = "raw_record"
        return ("Raw / Entrance Layer", target, "migrate_to_target_table", "P3")
    if family in {"db20", "db21", "db22", "db23", "db23a", "db23b"}:
        if any(term in lower for term in ("signature", "block")):
            return ("Observation / Signal Fact Layer", "fact_block_signature", "migrate_to_target_table", "P6")
        if any(term in lower for term in ("token", "field", "mapping")):
            return ("Mapping / Evidence Layer", "map_token_dictionary", "migrate_to_target_table", "P5")
        return ("Raw / Entrance Layer", "raw_record", "keep_as_legacy_staging", "P3")
    if family == "db25":
        if any(term in lower for term in ("run", "consolidation", "object", "inventory", "count", "map")):
            return ("Audit / Provenance Sidecar", "audit_lineage_event", "migrate_to_target_table", "P3")
        return ("Audit / Provenance Sidecar", "audit_run", "keep_as_legacy_staging", "P3")
    if family in {"db26", "db27"}:
        if "gap" in lower:
            return ("Mapping / Evidence Layer", "map_evidence_gap", "migrate_to_target_table", "P5")
        if "decision" in lower or "review" in lower or "work" in lower or "queue" in lower:
            return ("Mapping / Evidence Layer", "map_review_decision", "migrate_to_target_table", "P5")
        if "role" in role_lower:
            return ("Mapping / Evidence Layer", "map_token_role", "migrate_to_target_table", "P5")
        return ("Mapping / Evidence Layer", "map_token_dictionary", "migrate_to_target_table", "P5")
    if family == "db28":
        if "source" in lower:
            return ("Mapping / Evidence Layer", "map_external_source", "migrate_to_target_table", "P5")
        if "gap" in lower:
            return ("Mapping / Evidence Layer", "map_evidence_gap", "migrate_to_target_table", "P5")
        return ("Mapping / Evidence Layer", "map_assertion_evidence", "migrate_to_target_table", "P5")
    if family == "bridge01":
        if "field" in lower or "gap" in lower:
            return ("Bridge / Connection Layer", "bridge_relation_context_condition", "migrate_to_target_table", "P6")
        if "view" in lower:
            return ("Report / View Layer", "qsb_v_bridge_candidate_matrix", "convert_to_view", "P8")
        return ("Bridge / Connection Layer", "bridge_candidate_connection", "migrate_to_target_table", "P6")
    if "source" in lower or "file" in lower:
        return ("Raw / Entrance Layer", "raw_source_file", "needs_manual_review", "P3")
    return ("Audit / Provenance Sidecar", "audit_lineage_event", "needs_manual_review", "P3")


def choose_target_view(current_name_lower: str) -> str:
    if "mapping" in current_name_lower or "token" in current_name_lower:
        return "qsb_v_token_mapping_status"
    if "evidence" in current_name_lower or "external" in current_name_lower:
        return "qsb_v_external_evidence_status"
    if "bridge" in current_name_lower or "candidate" in current_name_lower:
        return "qsb_v_bridge_candidate_matrix"
    if "raw" in current_name_lower or "lineage" in current_name_lower:
        return "qsb_v_raw_to_observation_lineage"
    if "rebuild" in current_name_lower or "migration" in current_name_lower:
        return "qsb_v_rebuild_status"
    if "claim" in current_name_lower:
        return "qsb_v_claim_boundary_dashboard"
    return "qsb_v_current_research_dwh_dashboard"


def inspect_current_db(db_path: Path) -> dict[str, Any]:
    with connect_readonly(db_path) as con:
        objects = list_sqlite_objects(con)
        fields_by_object: dict[str, list[dict[str, Any]]] = {}
        fks_by_table: dict[str, list[dict[str, Any]]] = {}
        indexes_by_table: dict[str, list[dict[str, Any]]] = {}
        index_fields_by_index: dict[str, list[dict[str, Any]]] = {}
        row_counts: dict[str, int | None] = {}
        mapping_rows: list[dict[str, Any]] = []

        for obj in objects:
            name = str(obj["name"])
            object_type = str(obj["type"])
            fields = pragma_table_info(con, name)
            fields_by_object[name] = fields
            family = classify_current_family(name)
            role = classify_current_role(name, object_type, fields)
            target_layer, target_object, action, priority = target_for_current_object(
                name, object_type, family, role
            )
            mapping_rows.append(
                {
                    "current_object_name": name,
                    "current_object_type": object_type,
                    "current_family": family,
                    "current_role": role,
                    "target_layer": target_layer,
                    "target_table_or_view": target_object,
                    "migration_action": action,
                    "migration_priority": priority,
                    "notes": (
                        "Classified from current object name and field inventory; "
                        "manual review remains required before implementation."
                    ),
                }
            )
            if object_type == "table":
                fks_by_table[name] = pragma_fk_list(con, name)
                row_counts[name] = table_row_count(con, name)
                indexes = pragma_index_list(con, name)
                indexes_by_table[name] = indexes
                for index in indexes:
                    index_name = str(index.get("name", ""))
                    index_fields_by_index[index_name] = pragma_index_info(con, index_name)

    families = sorted({row["current_family"] for row in mapping_rows})
    family_summary: dict[str, dict[str, int]] = {}
    for family in families:
        family_rows = [row for row in mapping_rows if row["current_family"] == family]
        table_names = [row["current_object_name"] for row in family_rows if row["current_object_type"] == "table"]
        view_names = [row["current_object_name"] for row in family_rows if row["current_object_type"] == "view"]
        row_total = 0
        for table_name in table_names:
            count = row_counts.get(table_name)
            if count is not None:
                row_total += count
        family_summary[family] = {
            "table_count": len(table_names),
            "view_count": len(view_names),
            "approx_table_rows": row_total,
        }

    return {
        "objects": objects,
        "fields_by_object": fields_by_object,
        "fks_by_table": fks_by_table,
        "indexes_by_table": indexes_by_table,
        "index_fields_by_index": index_fields_by_index,
        "row_counts": row_counts,
        "mapping_rows": sorted(mapping_rows, key=lambda row: (row["current_family"], row["current_object_type"], row["current_object_name"])),
        "family_summary": family_summary,
    }


def target_layer_summary(target_tables: list[TargetTable]) -> list[dict[str, Any]]:
    fields_by_table = {table.target_table_name: len(table.fields) for table in target_tables}
    result = []
    for layer in LAYER_ORDER:
        layer_tables = [table for table in target_tables if table.layer == layer]
        if not layer_tables and layer != "Report / View Layer":
            continue
        result.append(
            {
                "layer": layer,
                "table_count": len(layer_tables),
                "field_count": sum(fields_by_table.get(table.target_table_name, 0) for table in layer_tables),
                "tables": [table.target_table_name for table in layer_tables],
                "views": [view["view_name"] for view in REPORT_VIEWS] if layer == "Report / View Layer" else [],
            }
        )
    return result


def output_paths(output_root: Path) -> dict[str, Path]:
    return {name: output_root / name for name in OUTPUT_FILENAMES}


def ensure_preconditions(db_path: Path, output_root: Path, overwrite: bool) -> None:
    if not db_path.exists():
        raise FileNotFoundError(f"Input DB does not exist: {db_path}")
    if not db_path.is_file():
        raise ValueError(f"Input DB path is not a file: {db_path}")
    if not output_root.exists():
        raise FileNotFoundError(f"Output root does not exist: {output_root}")
    if not output_root.is_dir():
        raise ValueError(f"Output root is not a directory: {output_root}")
    if db_path.stat().st_size <= 0:
        raise ValueError(f"Input DB is empty: {db_path}")
    existing = [str(path) for path in output_paths(output_root).values() if path.exists()]
    if existing and not overwrite:
        raise FileExistsError(
            "Refusing to overwrite existing DWH01 output file(s): "
            + "; ".join(existing)
            + ". Re-run with --overwrite only when controlled regeneration is intended."
        )


def write_csv(path: Path, fieldnames: list[str], rows: list[dict[str, Any]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def write_text(path: Path, text: str) -> None:
    path.write_text(text, encoding="utf-8")


def table_design_rows(target_tables: list[TargetTable]) -> list[dict[str, Any]]:
    return [
        {
            "target_table_name": table.target_table_name,
            "layer": table.layer,
            "purpose": table.purpose,
            "grain": table.grain,
            "primary_key": table.primary_key,
            "natural_key_candidate": table.natural_key_candidate,
            "source_from_current_db": table.source_from_current_db,
            "migration_strategy": table.migration_strategy,
            "implementation_priority": table.implementation_priority,
            "notes": table.notes,
        }
        for table in target_tables
    ]


def field_catalog_rows(target_tables: list[TargetTable]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for table_spec in target_tables:
        for field_spec in table_spec.fields:
            rows.append(
                {
                    "target_table_name": table_spec.target_table_name,
                    "field_name": field_spec.field_name,
                    "field_type": field_spec.field_type,
                    "field_role": field_spec.field_role,
                    "nullable": field_spec.nullable,
                    "field_description": field_spec.field_description,
                    "source_field_or_rule": field_spec.source_field_or_rule,
                    "data_quality_rule": field_spec.data_quality_rule,
                    "claim_boundary_note": field_spec.claim_boundary_note,
                }
            )
    return rows


def fk_rows(target_fks: list[TargetFk]) -> list[dict[str, Any]]:
    return [
        {
            "source_table": item.source_table,
            "source_field": item.source_field,
            "target_table": item.target_table,
            "target_field": item.target_field,
            "relation_type": item.relation_type,
            "mandatory": item.mandatory,
            "index_recommended": item.index_recommended,
            "relationship_description": item.relationship_description,
            "erd_slice": item.erd_slice,
        }
        for item in target_fks
    ]


def erd_slice_rows(slices: list[ErdSlice]) -> list[dict[str, Any]]:
    return [
        {
            "erd_slice_id": item.erd_slice_id,
            "erd_slice_name": item.erd_slice_name,
            "included_tables": item.included_tables,
            "included_views": item.included_views,
            "main_question_answered": item.main_question_answered,
            "intended_audience": item.intended_audience,
            "export_priority": item.export_priority,
            "notes": item.notes,
        }
        for item in slices
    ]


def migration_phase_rows(phases: list[MigrationPhase]) -> list[dict[str, Any]]:
    return [
        {
            "phase_id": item.phase_id,
            "phase_name": item.phase_name,
            "phase_goal": item.phase_goal,
            "writes_db": item.writes_db,
            "requires_backup": item.requires_backup,
            "input_objects": item.input_objects,
            "output_objects": item.output_objects,
            "validation_checks": item.validation_checks,
            "rollback_plan": item.rollback_plan,
            "risk_level": item.risk_level,
            "notes": item.notes,
        }
        for item in phases
    ]


def count_inspected_fields(inspected: dict[str, Any]) -> int:
    return sum(len(fields) for fields in inspected["fields_by_object"].values())


def count_inspected_fks(inspected: dict[str, Any]) -> int:
    return sum(len(items) for items in inspected["fks_by_table"].values())


def count_inspected_indexes(inspected: dict[str, Any]) -> int:
    return sum(len(items) for items in inspected["indexes_by_table"].values())


def markdown_table(rows: list[list[str]]) -> str:
    if not rows:
        return ""
    header = rows[0]
    separator = ["---" for _ in header]
    lines = [
        "| " + " | ".join(header) + " |",
        "| " + " | ".join(separator) + " |",
    ]
    for row in rows[1:]:
        clean = [str(cell).replace("\n", " ").replace("|", "/") for cell in row]
        lines.append("| " + " | ".join(clean) + " |")
    return "\n".join(lines)


def render_markdown_spec(
    db_path: Path,
    inspected: dict[str, Any],
    target_tables: list[TargetTable],
    target_fks: list[TargetFk],
    erd_slices: list[ErdSlice],
    migration_phases: list[MigrationPhase],
) -> str:
    table_count = sum(1 for obj in inspected["objects"] if obj["type"] == "table")
    view_count = sum(1 for obj in inspected["objects"] if obj["type"] == "view")
    field_count = count_inspected_fields(inspected)
    fk_count = count_inspected_fks(inspected)
    index_count = count_inspected_indexes(inspected)
    target_field_count = sum(len(table.fields) for table in target_tables)
    mapping_action_counts = Counter(row["migration_action"] for row in inspected["mapping_rows"])
    mapping_family_counts = Counter(row["current_family"] for row in inspected["mapping_rows"])
    layer_summary = target_layer_summary(target_tables)

    lines: list[str] = []
    lines.append("# QSB-DWH01 Target Research DWH Schema Specification")
    lines.append("")
    lines.append(f"Generated at UTC: {utc_now()}")
    lines.append(f"Script: `{SCRIPT_NAME}`")
    lines.append(f"Input DB: `{db_path}`")
    lines.append("DB modified: `false`")
    lines.append("")
    lines.append("## 1. Executive summary")
    lines.append("")
    lines.append(
        "DWH01 defines a professional target schema for the QSB Research DWH. "
        "The target architecture is observation-centered: raw files and records "
        "enter through a controlled raw layer, stable source/dataset/observation "
        "objects form the core, dimensions provide conformed context, mapping "
        "and evidence objects document token meaning and gaps, bridge connection "
        "objects make candidate relations joinable, result facts remain separated "
        "from bridge design, and an audit/provenance sidecar keeps schema, runs, "
        "lineage, rebuild status, and claim boundaries queryable."
    )
    lines.append("")
    lines.append(
        f"The current consolidated snapshot was inspected in read-only SQLite mode. "
        f"The inspection found {table_count} tables, {view_count} views, "
        f"{field_count} fields, {fk_count} declared current FKs, and "
        f"{index_count} current table indexes. The target design contains "
        f"{len(target_tables)} tables, {target_field_count} fields, "
        f"{len(target_fks)} FK or FK-like relationship rows, and "
        f"{len(REPORT_VIEWS)} report/query views."
    )
    lines.append("")
    lines.append("## 2. Architectural decision")
    lines.append("")
    lines.append(f"Decision: {TARGET_ARCHITECTURE}.")
    lines.append("")
    lines.append(
        "The observation is the central real-world anchor. Source, dataset, raw "
        "record, token, mapping, evidence, context, bridge candidate, result, "
        "audit, and claim-boundary objects should be reachable through explicit "
        "PK/FK paths. The target model is modified star/snowflake because the "
        "core observation star is extended by snowflaked dimensions, many-to-many "
        "lineage links, evidence/review side tables, bridge connection objects, "
        "and result/audit layers."
    )
    lines.append("")
    lines.append("## 3. Current DB diagnosis")
    lines.append("")
    lines.append(
        "The current DB is valuable as a connected research artifact database, "
        "but its shape reflects historical growth across DB20 through DB28, "
        "bridge01, and qsb_v report layers. It contains useful inventories, "
        "mapping worklists, evidence seeds, and bridge-readiness design objects, "
        "yet many tables are additive islands rather than members of one enforced "
        "DWH relationship graph."
    )
    lines.append("")
    lines.append("Current naming-family summary:")
    lines.append("")
    family_rows = [["Family", "Tables", "Views", "Approx table rows"]]
    for family, summary in sorted(inspected["family_summary"].items()):
        family_rows.append(
            [
                family,
                str(summary["table_count"]),
                str(summary["view_count"]),
                str(summary["approx_table_rows"]),
            ]
        )
    lines.append(markdown_table(family_rows))
    lines.append("")
    lines.append("## 4. Why the current DB is not yet a professional Research DWH")
    lines.append("")
    lines.append("- There is not yet a single enforced observation-centered core that all applicable facts and mappings reference.")
    lines.append("- Current DBXX families preserve useful audit trail, but they are not normalized into conformed raw, core, dimension, mapping, bridge, result, and audit layers.")
    lines.append("- Existing views are helpful report surfaces, but view logic cannot replace stable PK/FK relationships for migration, rebuild, and review.")
    lines.append("- Mapping, evidence, gaps, bridge readiness, results, controls, and claim boundaries need first-class relational objects so they can be joined and audited.")
    lines.append("- Legacy tables should remain as staging/history until row-count parity, FK validation, rebuild checks, and ERD review pass.")
    lines.append("")
    lines.append("## 5. Target architecture overview")
    lines.append("")
    lines.append("Target layers:")
    lines.append("")
    for summary in layer_summary:
        if summary["layer"] == "Report / View Layer":
            lines.append(
                f"- {summary['layer']}: {len(summary['views'])} planned qsb_v_* views."
            )
        else:
            lines.append(
                f"- {summary['layer']}: {summary['table_count']} tables, "
                f"{summary['field_count']} fields."
            )
    lines.append("")
    lines.append(
        "The Bridge/Result layer becomes operational at the database-design level "
        "when connection tables and result tables connect QM-side quantities, "
        "ART-side quantities, functional relations, context conditions, evidence "
        "chains, expected-value fields, observed-value fields, delta result "
        "placeholders, controls, and failure-mode statuses. DWH01 defines those "
        "tables; it does not populate or evaluate them as physical results."
    )
    lines.append("")
    lines.append("## 6. Layer-by-layer target schema")
    lines.append("")
    for summary in layer_summary:
        lines.append(f"### {summary['layer']}")
        lines.append("")
        if summary["layer"] == "Report / View Layer":
            for view in REPORT_VIEWS:
                lines.append(f"- `{view['view_name']}`: {view['purpose']}")
        else:
            for table_name in summary["tables"]:
                table_spec = next(item for item in target_tables if item.target_table_name == table_name)
                lines.append(f"- `{table_name}`: {table_spec.purpose}")
        lines.append("")
    lines.append("## 7. Table specifications")
    lines.append("")
    table_rows = [["Table", "Layer", "Grain", "PK", "Priority"]]
    for item in target_tables:
        table_rows.append([item.target_table_name, item.layer, item.grain, item.primary_key, item.implementation_priority])
    lines.append(markdown_table(table_rows))
    lines.append("")
    lines.append("Full table design is written to `dwh01_target_table_design.csv`.")
    lines.append("")
    lines.append("## 8. Field catalog summary")
    lines.append("")
    field_role_counts = Counter(field.field_role for table_spec in target_tables for field in table_spec.fields)
    field_rows = [["Field role", "Count"]]
    for role_name, count in sorted(field_role_counts.items()):
        field_rows.append([role_name, str(count)])
    lines.append(markdown_table(field_rows))
    lines.append("")
    lines.append("Every target table has field-level catalog entries in `dwh01_target_field_catalog.csv`.")
    lines.append("")
    lines.append("## 9. PK/FK strategy")
    lines.append("")
    lines.append("- Use stable text surrogate IDs for project-controlled entities.")
    lines.append("- Preserve source-local IDs and composite lineage keys as attributes.")
    lines.append("- Treat natural keys as unique constraints only where stable.")
    lines.append("- Every applicable fact references `core_observation`.")
    lines.append("- Mapping and evidence decisions link to source/evidence/review status.")
    lines.append("- Bridge and result rows link to observation/context, relation, evidence, audit, and claim-boundary objects where applicable.")
    lines.append("- Migration-generated rows link to `audit_run` when practical.")
    lines.append("")
    lines.append(f"The target FK design contains {len(target_fks)} relationship rows in `dwh01_target_pk_fk_design.csv`.")
    lines.append("")
    lines.append("## 10. Current-to-target mapping")
    lines.append("")
    action_rows = [["Migration action", "Object count"]]
    for action, count in sorted(mapping_action_counts.items()):
        action_rows.append([action, str(count)])
    lines.append(markdown_table(action_rows))
    lines.append("")
    family_mapping_rows = [["Current family", "Object count"]]
    for family, count in sorted(mapping_family_counts.items()):
        family_mapping_rows.append([family, str(count)])
    lines.append(markdown_table(family_mapping_rows))
    lines.append("")
    lines.append("Object-level mapping is written to `dwh01_current_to_target_mapping.csv`.")
    lines.append("")
    lines.append("## 11. ERD slice plan")
    lines.append("")
    for item in erd_slices:
        lines.append(f"- {item.erd_slice_id} {item.erd_slice_name}: {item.main_question_answered}")
    lines.append("")
    lines.append("Detailed ERD slice rows are written to `dwh01_erd_slice_plan.csv`.")
    lines.append("")
    lines.append("## 12. Migration phase plan")
    lines.append("")
    for item in migration_phases:
        lines.append(f"- {item.phase_id}: {item.phase_name} - {item.phase_goal}")
    lines.append("")
    lines.append("Detailed migration phase rows are written to `dwh01_migration_phase_plan.csv`.")
    lines.append("")
    lines.append("## 13. Controls before implementation")
    lines.append("")
    lines.append("- Freeze the current DB and create a separate workcopy before DDL.")
    lines.append("- Implement audit schema-version and migration-log tables before target data movement.")
    lines.append("- Keep DBXX, bridge01, and qsb_v legacy objects until parity and rebuild checks pass.")
    lines.append("- Validate row counts, FK constraints, index presence, view dependencies, and ERD reachability.")
    lines.append("- Preserve unresolved numeric tokens as text/status until review and evidence are sufficient.")
    lines.append("- Require claim-boundary rows for bridge, result, and report objects.")
    lines.append("- Document any non-certified replay/order behavior explicitly in run outputs.")
    lines.append("")
    lines.append("## 14. Recommended next implementation step")
    lines.append("")
    lines.append(RECOMMENDED_NEXT_STEP)
    lines.append("")
    lines.append("## 15. Claim boundary")
    lines.append("")
    lines.append(CLAIM_BOUNDARY)
    lines.append("")
    return "\n".join(lines)


def render_adr(db_path: Path, target_tables: list[TargetTable], target_fks: list[TargetFk]) -> str:
    lines = [
        "# Architecture Decision Record: QSB Research DWH Target Schema",
        "",
        "Status: proposed",
        "",
        "## Context",
        "",
        (
            "The consolidated QSB snapshot is a useful research artifact database "
            "with historically grown DBXX, bridge01, and qsb_v families. The next "
            "DWH step needs a connected target schema rather than a loose sequence "
            "of additive tables."
        ),
        "",
        "## Decision",
        "",
        (
            f"Adopt a {TARGET_ARCHITECTURE}. The target contains "
            f"{len(target_tables)} tables, {sum(len(item.fields) for item in target_tables)} "
            f"field catalog entries, {len(target_fks)} relationship rows, and "
            f"{len(REPORT_VIEWS)} planned report/query views."
        ),
        "",
        "## Consequences",
        "",
        "- Observation becomes the central anchor for applicable facts, mappings, bridge candidates, and result rows.",
        "- Raw/source payloads remain referenced through path, URI, checksum, and lineage keys.",
        "- Mapping, evidence, gaps, review decisions, bridge candidates, controls, and claim boundaries become queryable objects.",
        "- Initial migration requires backup/workcopy discipline and parity checks before any target schema is marked current.",
        "",
        "## Alternatives considered",
        "",
        "- Keep adding DBXX tables: rejected because it would preserve historical islands and weak relationship guarantees.",
        "- Build a single wide fact table: rejected because it would mix raw lineage, mapping, evidence, relation design, results, and audit controls.",
        "- Build a pure star schema: rejected because QSB needs snowflaked context, many-to-many lineage, evidence gaps, bridge connection objects, and audit sidecars.",
        "",
        "## Claim boundary",
        "",
        CLAIM_BOUNDARY,
        "",
        "## Next step",
        "",
        RECOMMENDED_NEXT_STEP,
        "",
        f"Input DB inspected read-only: `{db_path}`",
        "",
    ]
    return "\n".join(lines)


def json_summary(
    db_path: Path,
    inspected: dict[str, Any],
    target_tables: list[TargetTable],
    target_fks: list[TargetFk],
) -> dict[str, Any]:
    table_count = sum(1 for obj in inspected["objects"] if obj["type"] == "table")
    view_count = sum(1 for obj in inspected["objects"] if obj["type"] == "view")
    target_field_count = sum(len(table.fields) for table in target_tables)
    return {
        "input_db_path": str(db_path),
        "db_modified": False,
        "inspected_table_count": table_count,
        "inspected_view_count": view_count,
        "inspected_field_count": count_inspected_fields(inspected),
        "inspected_fk_count": count_inspected_fks(inspected),
        "inspected_index_count": count_inspected_indexes(inspected),
        "target_table_count": len(target_tables),
        "target_view_count": len(REPORT_VIEWS),
        "target_field_count": target_field_count,
        "target_fk_count": len(target_fks),
        "target_layers": target_layer_summary(target_tables),
        "current_family_summary": inspected["family_summary"],
        "current_to_target_action_summary": dict(Counter(row["migration_action"] for row in inspected["mapping_rows"])),
        "recommended_next_step": RECOMMENDED_NEXT_STEP,
        "claim_boundary": CLAIM_BOUNDARY,
        "warnings": [
            "DWH01 is design/specification only.",
            "Current table row counts are used for architecture diagnosis and migration planning only.",
            "Current-to-target mapping is heuristic and must be reviewed before migration.",
        ],
    }


def validate_target_design(target_tables: list[TargetTable], target_fks: list[TargetFk]) -> None:
    table_names = {item.target_table_name for item in target_tables}
    if len(table_names) != len(target_tables):
        raise ValueError("Duplicate target table names detected.")
    missing_fields = [item.target_table_name for item in target_tables if not item.fields]
    if missing_fields:
        raise ValueError("Target table(s) missing fields: " + ", ".join(missing_fields))
    for item in target_tables:
        if not any(field_spec.field_name == item.primary_key for field_spec in item.fields):
            raise ValueError(f"Primary key {item.primary_key} missing from {item.target_table_name}")
    for item in target_fks:
        if item.source_table not in table_names:
            raise ValueError(f"FK source table missing from target design: {item.source_table}")
        if item.target_table not in table_names:
            raise ValueError(f"FK target table missing from target design: {item.target_table}")


def run(args: argparse.Namespace) -> int:
    db_path = Path(args.db)
    output_root = Path(args.output_root)
    ensure_preconditions(db_path, output_root, args.overwrite)

    target_tables = build_target_tables()
    target_fks = build_target_fks()
    erd_slices = build_erd_slices()
    migration_phases = build_migration_phases()
    validate_target_design(target_tables, target_fks)

    inspected = inspect_current_db(db_path)
    paths = output_paths(output_root)

    write_text(
        paths[SPEC_MD],
        render_markdown_spec(db_path, inspected, target_tables, target_fks, erd_slices, migration_phases),
    )
    write_text(paths[SPEC_JSON], pretty_json(json_summary(db_path, inspected, target_tables, target_fks)) + "\n")
    write_csv(
        paths[TABLE_DESIGN_CSV],
        [
            "target_table_name",
            "layer",
            "purpose",
            "grain",
            "primary_key",
            "natural_key_candidate",
            "source_from_current_db",
            "migration_strategy",
            "implementation_priority",
            "notes",
        ],
        table_design_rows(target_tables),
    )
    write_csv(
        paths[FIELD_CATALOG_CSV],
        [
            "target_table_name",
            "field_name",
            "field_type",
            "field_role",
            "nullable",
            "field_description",
            "source_field_or_rule",
            "data_quality_rule",
            "claim_boundary_note",
        ],
        field_catalog_rows(target_tables),
    )
    write_csv(
        paths[PK_FK_DESIGN_CSV],
        [
            "source_table",
            "source_field",
            "target_table",
            "target_field",
            "relation_type",
            "mandatory",
            "index_recommended",
            "relationship_description",
            "erd_slice",
        ],
        fk_rows(target_fks),
    )
    write_csv(
        paths[CURRENT_TO_TARGET_CSV],
        [
            "current_object_name",
            "current_object_type",
            "current_family",
            "current_role",
            "target_layer",
            "target_table_or_view",
            "migration_action",
            "migration_priority",
            "notes",
        ],
        inspected["mapping_rows"],
    )
    write_csv(
        paths[ERD_SLICE_CSV],
        [
            "erd_slice_id",
            "erd_slice_name",
            "included_tables",
            "included_views",
            "main_question_answered",
            "intended_audience",
            "export_priority",
            "notes",
        ],
        erd_slice_rows(erd_slices),
    )
    write_csv(
        paths[MIGRATION_PHASE_CSV],
        [
            "phase_id",
            "phase_name",
            "phase_goal",
            "writes_db",
            "requires_backup",
            "input_objects",
            "output_objects",
            "validation_checks",
            "rollback_plan",
            "risk_level",
            "notes",
        ],
        migration_phase_rows(migration_phases),
    )
    write_text(paths[ADR_MD], render_adr(db_path, target_tables, target_fks))

    print(f"Wrote {len(paths)} DWH01 output files to {output_root}")
    print(f"Input DB inspected read-only: {db_path}")
    print("DB modified: false")
    print(f"Target tables: {len(target_tables)}")
    print(f"Target fields: {sum(len(item.fields) for item in target_tables)}")
    print(f"Target relationships: {len(target_fks)}")
    return 0


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Generate QSB-DWH01 target Research DWH schema specification "
            "artifacts from the consolidated SQLite snapshot metadata."
        )
    )
    parser.add_argument("--db", default=str(DEFAULT_DB), help="Path to consolidated snapshot SQLite DB.")
    parser.add_argument("--output-root", default=str(DEFAULT_OUTPUT_ROOT), help="Directory for DWH01 output artifacts.")
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Allow controlled regeneration when DWH01 output files already exist.",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    try:
        args = parse_args(sys.argv[1:] if argv is None else argv)
        return run(args)
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
