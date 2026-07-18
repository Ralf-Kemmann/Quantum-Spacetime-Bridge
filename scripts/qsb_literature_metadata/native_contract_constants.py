#!/usr/bin/env python3
"""Controlled constants for QSB/PBR literature native metadata mapping."""

from __future__ import annotations

CLAIM_BOUNDARY = "literature_context_only_no_internal_evidence_no_mechanism_claim"
PHYSICAL_CLAIM_RELEASE = "blocked_no_physics_claim"
MECHANISM_CLAIM_RELEASE = "blocked_no_mechanism_claim"
EXECUTION_IMPORT_AUTHORIZED = "false"
DATA_MART_CREATION_AUTHORIZED = "false"
METADATA_CATALOG_ROLE = "canonical_field_alias_lineage_registry_boundary_layer"
LITERATURE_TABLE_ROLE = "theory_and_search_space_dimensions_only"
PLANCK_SPACE_MAPPING_STATUS = "future_contract_only_not_populated"
CUBE_MAPPING_STATUS = "future_design_dependency_not_implemented"

LOOKUP_OUTCOMES = (
    "resolved_existing",
    "resolved_create_candidate",
    "resolved_noop",
    "blocked_missing_parent",
    "blocked_multiple_matches",
    "blocked_contract_violation",
)

OPERATION_TYPES = (
    "lookup",
    "insert_candidate",
    "update_candidate",
    "no_op_candidate",
    "block",
)

CONFLICT_CLASSES = (
    "compatible_enrichment_candidate",
    "exact_duplicate_noop",
    "alias_addition_candidate",
    "lineage_addition_candidate",
    "new_version_candidate",
    "vocabulary_entry_addition_candidate",
    "blocked_incompatible_existing_value",
    "blocked_multiple_native_matches",
    "blocked_parent_missing",
    "blocked_claim_boundary_mismatch",
    "blocked_contract_violation",
)

OBSERVATION_STATES = (
    "accepted",
    "rejected",
    "neutral",
    "ambiguous",
    "unmapped",
    "not_tested",
    "nullmodel_reproduced",
    "no_specificity",
    "missing_metadata",
    "incomplete_lineage",
    "blocked_claim_state",
    "negative",
    "unknown",
    "missing",
    "not_applicable",
)

CLAIM_BOUNDARY_STATES = (
    CLAIM_BOUNDARY,
    PHYSICAL_CLAIM_RELEASE,
    MECHANISM_CLAIM_RELEASE,
    f"execution_import_authorized={EXECUTION_IMPORT_AUTHORIZED}",
    f"data_mart_creation_authorized={DATA_MART_CREATION_AUTHORIZED}",
)

CUBE_COMPATIBILITY_STATES = (
    CUBE_MAPPING_STATUS,
    "design_only_no_data_mart_created",
    "future_cube_role",
    "not_cube_eligible",
    "quality_status_dimension",
)

PLANCK_SPACE_COMPATIBILITY_STATES = (
    PLANCK_SPACE_MAPPING_STATUS,
    "coordinate_definition_id",
    "mapping_version",
    "dimension_check_pending",
    "not_populated",
)

QUANTITY_UNIT_DIMENSION_STATES = (
    "quantity_kind",
    "unit_original",
    "unit_calculation",
    "unit_display",
    "dimension_vector",
    "conversion_rule_id",
    "dimensionless",
    "not_applicable",
    "categorical",
    "textual",
    "identifier",
    "temporal",
    "unknown",
    "missing",
)

ALIAS_SCOPES = ("field_label", "table_label", "browser_label", "cube_label")
LANGUAGE_CODES = ("de", "en")
LINEAGE_STATES = ("available", "requires_human_review", "not_implemented", "design_only_not_executed")
VALIDATION_RESULTS = ("pass", "fail", "blocked", "warning")

NATIVE_OBJECT_ORDER = (
    "meta_work_package",
    "meta_object",
    "meta_object_version",
    "meta_vocabulary",
    "meta_vocabulary_entry",
    "meta_field",
    "meta_alias",
    "meta_source",
    "meta_validation_rule",
    "meta_lineage",
)

REQUIRED_NATIVE_TABLES = NATIVE_OBJECT_ORDER
