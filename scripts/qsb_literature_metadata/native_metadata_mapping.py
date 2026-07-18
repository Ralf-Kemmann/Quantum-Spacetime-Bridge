#!/usr/bin/env python3
"""Pure native metadata operation planning for QSB/PBR literature rows."""

from __future__ import annotations

import csv
import hashlib
import json
import sqlite3
import unicodedata
from collections import Counter
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Iterable, Sequence

from scripts.qsb_literature_metadata.native_contract_constants import (
    ALIAS_SCOPES,
    CLAIM_BOUNDARY,
    CONFLICT_CLASSES,
    CUBE_MAPPING_STATUS,
    EXECUTION_IMPORT_AUTHORIZED,
    LANGUAGE_CODES,
    LOOKUP_OUTCOMES,
    MECHANISM_CLAIM_RELEASE,
    NATIVE_OBJECT_ORDER,
    OPERATION_TYPES,
    PHYSICAL_CLAIM_RELEASE,
    PLANCK_SPACE_MAPPING_STATUS,
    REQUIRED_NATIVE_TABLES,
)


TRANSFORMATION_RULE = "registration_plan_row_to_native_metadata_operations_implementation_01"


@dataclass(frozen=True)
class RegistrationPlanRow:
    registration_plan_row_id: str
    table_name: str
    field_name: str
    canonical_name: str
    de_label: str
    en_label: str
    description_de: str
    description_en: str
    data_type: str
    allowed_values: str
    lineage_note: str
    claim_boundary_note: str
    claim_boundary: str = CLAIM_BOUNDARY


@dataclass(frozen=True)
class OperationCandidate:
    registration_plan_row_id: str
    operation_sequence: int
    native_object: str
    operation_type_candidate: str
    lookup_outcome: str
    lookup_key: str
    parent_dependency: str
    idempotency_key: str
    conflict_class: str
    validation_dependency: str
    lineage_key: str
    claim_boundary_state: str
    native_target_version: str
    mode: str
    authorization_state: str
    review_status: str
    implementation_status: str = "implemented_temp_dryrun_only"

    def to_row(self) -> dict[str, object]:
        return asdict(self)


class MappingError(ValueError):
    """Controlled mapping failure."""


def read_registration_plan(path: Path) -> list[RegistrationPlanRow]:
    with path.open(newline="", encoding="utf-8") as handle:
        rows = []
        for idx, row in enumerate(csv.DictReader(handle), start=1):
            rows.append(
                RegistrationPlanRow(
                    registration_plan_row_id=f"RP{idx:02d}",
                    table_name=row["table_name"],
                    field_name=row["field_name"],
                    canonical_name=row["canonical_name"],
                    de_label=row["de_label"],
                    en_label=row["en_label"],
                    description_de=row["description_de"],
                    description_en=row["description_en"],
                    data_type=row["data_type"],
                    allowed_values=row.get("allowed_values", ""),
                    lineage_note=row["lineage_note"],
                    claim_boundary_note=row["claim_boundary_note"],
                )
            )
    validate_registration_rows(rows)
    return rows


def validate_registration_rows(rows: Sequence[RegistrationPlanRow]) -> None:
    if len(rows) != 17:
        raise MappingError(f"blocked_contract_violation: expected 17 registration rows, observed {len(rows)}")
    for row in rows:
        if row.claim_boundary != CLAIM_BOUNDARY:
            raise MappingError(f"blocked_claim_boundary_mismatch: {row.registration_plan_row_id}")
        if not row.table_name or not row.canonical_name:
            raise MappingError(f"blocked_contract_violation: missing stable identifier in {row.registration_plan_row_id}")


def stable_key(*parts: object) -> str:
    return "::".join(str(part).strip().replace(" ", "_") for part in parts)


def normalize_alias(text: str) -> str:
    return unicodedata.normalize("NFC", text.strip())


def canonical_collision_key(text: str) -> str:
    return normalize_alias(text).casefold()


def quantity_policy(row: RegistrationPlanRow) -> dict[str, str]:
    if row.field_name in {"literature_id", "source_key"}:
        quantity_kind = "literature_metadata_identifier"
        semantic_status = "identifier"
        key_role = "primary_or_unique_identifier"
    elif row.field_name in {"internal_evidence_flag", "mechanism_claim_support", "physical_claim_support", "claim_boundary"}:
        quantity_kind = "claim_boundary_control"
        semantic_status = "categorical"
        key_role = "claim_boundary_control"
    elif row.allowed_values:
        quantity_kind = "literature_metadata_categorical"
        semantic_status = "categorical"
        key_role = "attribute"
    elif row.data_type.upper() == "INTEGER":
        quantity_kind = "literature_metadata_temporal"
        semantic_status = "temporal"
        key_role = "attribute"
    else:
        quantity_kind = "literature_metadata_textual"
        semantic_status = "textual"
        key_role = "attribute"
    return {
        "quantity_kind": quantity_kind,
        "unit_original": "not_applicable",
        "unit_calculation": "not_applicable",
        "unit_display": "not_applicable",
        "dimension_vector": "not_applicable",
        "conversion_rule_id": "not_applicable",
        "dimensionless": "not_applicable",
        "not_applicable": "preserved_distinct_from_missing",
        "semantic_status": semantic_status,
        "key_role": key_role,
        "unknown": "preserved_if_controlled",
        "missing": "preserved_distinct_from_unknown",
    }


def parent_dependency(native_object: str) -> str:
    return {
        "meta_work_package": "meta_mart",
        "meta_object": "meta_work_package",
        "meta_object_version": "meta_object",
        "meta_vocabulary": "none",
        "meta_vocabulary_entry": "meta_vocabulary",
        "meta_field": "meta_object;meta_quantity_kind",
        "meta_alias": "meta_field",
        "meta_source": "meta_mart",
        "meta_validation_rule": "none",
        "meta_lineage": "meta_source;meta_object;meta_field",
    }[native_object]


def operation_shape(native_object: str) -> tuple[str, str, str]:
    return {
        "meta_work_package": ("lookup", "resolved_existing", "exact_duplicate_noop"),
        "meta_object": ("insert_candidate", "resolved_create_candidate", "compatible_enrichment_candidate"),
        "meta_object_version": ("insert_candidate", "resolved_create_candidate", "new_version_candidate"),
        "meta_vocabulary": ("lookup", "resolved_existing", "exact_duplicate_noop"),
        "meta_vocabulary_entry": ("insert_candidate", "resolved_create_candidate", "vocabulary_entry_addition_candidate"),
        "meta_field": ("insert_candidate", "resolved_create_candidate", "compatible_enrichment_candidate"),
        "meta_alias": ("insert_candidate", "resolved_create_candidate", "alias_addition_candidate"),
        "meta_source": ("insert_candidate", "resolved_create_candidate", "compatible_enrichment_candidate"),
        "meta_validation_rule": ("insert_candidate", "resolved_create_candidate", "compatible_enrichment_candidate"),
        "meta_lineage": ("insert_candidate", "resolved_create_candidate", "lineage_addition_candidate"),
    }[native_object]


def build_operation_plan(rows: Sequence[RegistrationPlanRow], mode: str = "dry-run") -> list[OperationCandidate]:
    validate_registration_rows(rows)
    if mode not in {"dry-run", "execute"}:
        raise MappingError(f"blocked_contract_violation: unsupported mode {mode}")
    operations: list[OperationCandidate] = []
    sequence = 0
    for row in rows:
        for native_object in NATIVE_OBJECT_ORDER:
            operation_type, lookup_outcome, conflict_class = operation_shape(native_object)
            sequence += 1
            op = OperationCandidate(
                registration_plan_row_id=row.registration_plan_row_id,
                operation_sequence=sequence,
                native_object=native_object,
                operation_type_candidate=operation_type,
                lookup_outcome=lookup_outcome,
                lookup_key=stable_key(native_object, row.table_name, row.canonical_name),
                parent_dependency=parent_dependency(native_object),
                idempotency_key=stable_key("qsb_pbr_lit", native_object, row.table_name, row.canonical_name, row.registration_plan_row_id),
                conflict_class=conflict_class,
                validation_dependency="schema;lookup;idempotency;lineage;claim_boundary;quantity;alias;vocabulary",
                lineage_key=stable_key("lineage", row.registration_plan_row_id, native_object, row.table_name, row.canonical_name),
                claim_boundary_state=CLAIM_BOUNDARY,
                native_target_version="native_mapping_implementation_01",
                mode=mode,
                authorization_state=f"execution_import_authorized={EXECUTION_IMPORT_AUTHORIZED}",
                review_status="reviewed_by_source_patch_design",
            )
            validate_operation(op)
            operations.append(op)
    if len(operations) != 170:
        raise MappingError(f"blocked_contract_violation: expected 170 operations, observed {len(operations)}")
    return operations


def validate_operation(op: OperationCandidate) -> None:
    if op.lookup_outcome not in LOOKUP_OUTCOMES:
        raise MappingError(f"blocked_contract_violation: lookup outcome {op.lookup_outcome}")
    if op.operation_type_candidate not in OPERATION_TYPES:
        raise MappingError(f"blocked_contract_violation: operation type {op.operation_type_candidate}")
    if op.conflict_class not in CONFLICT_CLASSES:
        raise MappingError(f"blocked_contract_violation: conflict class {op.conflict_class}")
    if op.claim_boundary_state != CLAIM_BOUNDARY:
        raise MappingError(f"blocked_claim_boundary_mismatch: {op.registration_plan_row_id}")
    if not op.lineage_key or not op.idempotency_key:
        raise MappingError(f"blocked_contract_violation: missing lineage/idempotency on {op.operation_sequence}")


def validate_required_schema(conn: sqlite3.Connection) -> list[str]:
    tables = {row[0] for row in conn.execute("SELECT name FROM sqlite_schema WHERE type='table'")}
    return [table for table in REQUIRED_NATIVE_TABLES if table not in tables]


def schema_fingerprint(conn: sqlite3.Connection) -> str:
    rows = conn.execute(
        "SELECT type,name,tbl_name,coalesce(sql,'') FROM sqlite_schema "
        "WHERE type IN ('table','index','view','trigger') ORDER BY type,name"
    ).fetchall()
    return hashlib.sha256(json.dumps(rows, sort_keys=True).encode("utf-8")).hexdigest()


def classify_conflict(existing: dict[str, object] | None, candidate: OperationCandidate) -> str:
    if existing is None:
        return candidate.conflict_class
    immutable = ("idempotency_key", "native_object", "claim_boundary_state")
    if all(str(existing.get(key, "")) == str(getattr(candidate, key)) for key in immutable):
        return "exact_duplicate_noop"
    return "blocked_incompatible_existing_value"


def detect_alias_collisions(rows: Sequence[RegistrationPlanRow]) -> list[dict[str, str]]:
    seen: dict[tuple[str, str, str], str] = {}
    collisions: list[dict[str, str]] = []
    for row in rows:
        for language, text in (("de", row.de_label), ("en", row.en_label)):
            if language not in LANGUAGE_CODES:
                collisions.append({"registration_plan_row_id": row.registration_plan_row_id, "collision": "unsupported_language"})
                continue
            scope = "field_label"
            if scope not in ALIAS_SCOPES:
                collisions.append({"registration_plan_row_id": row.registration_plan_row_id, "collision": "unsupported_scope"})
                continue
            key = (row.table_name, language, canonical_collision_key(text))
            target = row.canonical_name
            prior = seen.get(key)
            if prior and prior != target:
                collisions.append({"registration_plan_row_id": row.registration_plan_row_id, "collision": stable_key(*key)})
            seen[key] = target
    return collisions


def vocabulary_entries(rows: Sequence[RegistrationPlanRow]) -> list[dict[str, str]]:
    entries: dict[tuple[str, str], dict[str, str]] = {}
    entries[("claim_boundary_status", CLAIM_BOUNDARY)] = {
        "vocabulary_name": "claim_boundary_status",
        "canonical_code": CLAIM_BOUNDARY,
        "english_label": "Literature context only",
        "german_alias": "Nur Literaturkontext",
        "definition": "Boundary forbids internal evidence, mechanism, and physics claims.",
    }
    for row in rows:
        if row.allowed_values:
            vocab = f"qsb_literature_{row.canonical_name}"
            for raw in row.allowed_values.split(";"):
                code = raw.strip()
                if not code:
                    continue
                entries[(vocab, code)] = {
                    "vocabulary_name": vocab,
                    "canonical_code": code,
                    "english_label": code.replace("_", " "),
                    "german_alias": "",
                    "definition": f"Source-supported value for {row.canonical_name}.",
                }
    return [entries[key] for key in sorted(entries)]


def write_operations_csv(path: Path, operations: Sequence[OperationCandidate]) -> None:
    rows = [op.to_row() for op in operations]
    if not rows:
        raise MappingError("blocked_contract_violation: empty operation plan")
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def create_native_dryrun_tables(conn: sqlite3.Connection) -> None:
    conn.executescript(
        """
        CREATE TABLE IF NOT EXISTS qsb_literature_native_operation_dryrun (
          idempotency_key TEXT PRIMARY KEY,
          registration_plan_row_id TEXT NOT NULL,
          operation_sequence INTEGER NOT NULL,
          native_object TEXT NOT NULL,
          operation_type_candidate TEXT NOT NULL,
          lookup_outcome TEXT NOT NULL,
          lookup_key TEXT NOT NULL,
          parent_dependency TEXT NOT NULL,
          conflict_class TEXT NOT NULL,
          validation_dependency TEXT NOT NULL,
          lineage_key TEXT NOT NULL,
          claim_boundary_state TEXT NOT NULL,
          native_target_version TEXT NOT NULL,
          mode TEXT NOT NULL,
          authorization_state TEXT NOT NULL,
          review_status TEXT NOT NULL,
          implementation_status TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS qsb_literature_native_validation_dryrun (
          check_name TEXT PRIMARY KEY,
          check_status TEXT NOT NULL,
          check_value TEXT NOT NULL
        );
        """
    )


def apply_operations_to_temp_db(conn: sqlite3.Connection, operations: Sequence[OperationCandidate]) -> dict[str, object]:
    missing = validate_required_schema(conn)
    if missing:
        raise MappingError("blocked_contract_violation: missing native tables " + ";".join(missing))
    create_native_dryrun_tables(conn)
    inserted = 0
    noop = 0
    for op in operations:
        validate_operation(op)
        existing = conn.execute(
            "SELECT idempotency_key,native_object,claim_boundary_state FROM qsb_literature_native_operation_dryrun WHERE idempotency_key = ?",
            (op.idempotency_key,),
        ).fetchone()
        if existing:
            conflict = classify_conflict(
                {"idempotency_key": existing[0], "native_object": existing[1], "claim_boundary_state": existing[2]},
                op,
            )
            if conflict == "exact_duplicate_noop":
                noop += 1
                continue
        else:
            conflict = op.conflict_class
        if conflict.startswith("blocked_"):
            raise MappingError(f"{conflict}: {op.idempotency_key}")
        conn.execute(
            """
            INSERT INTO qsb_literature_native_operation_dryrun (
              idempotency_key,registration_plan_row_id,operation_sequence,native_object,
              operation_type_candidate,lookup_outcome,lookup_key,parent_dependency,conflict_class,
              validation_dependency,lineage_key,claim_boundary_state,native_target_version,mode,
              authorization_state,review_status,implementation_status
            ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
            """,
            (
                op.idempotency_key,
                op.registration_plan_row_id,
                op.operation_sequence,
                op.native_object,
                op.operation_type_candidate,
                op.lookup_outcome,
                op.lookup_key,
                op.parent_dependency,
                op.conflict_class,
                op.validation_dependency,
                op.lineage_key,
                op.claim_boundary_state,
                op.native_target_version,
                op.mode,
                op.authorization_state,
                op.review_status,
                op.implementation_status,
            ),
        )
        inserted += 1
    conn.execute(
        "INSERT OR REPLACE INTO qsb_literature_native_validation_dryrun VALUES (?,?,?)",
        ("operation_count", "pass", str(len(operations))),
    )
    return {"inserted": inserted, "noop": noop, "operation_count": len(operations)}


def lineage_validation(operations: Sequence[OperationCandidate]) -> list[dict[str, str]]:
    return [
        {
            "operation_sequence": str(op.operation_sequence),
            "registration_plan_row_id": op.registration_plan_row_id,
            "native_object": op.native_object,
            "lineage_key": op.lineage_key,
            "claim_boundary": op.claim_boundary_state,
            "status": "pass" if op.lineage_key and op.claim_boundary_state == CLAIM_BOUNDARY else "fail",
        }
        for op in operations
    ]


def operation_summaries(operations: Sequence[OperationCandidate]) -> tuple[Counter[str], Counter[str]]:
    return Counter(op.lookup_outcome for op in operations), Counter(op.conflict_class for op in operations)
