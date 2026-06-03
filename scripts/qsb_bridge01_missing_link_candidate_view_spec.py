#!/usr/bin/env python3
"""QSB-BRIDGE01: Missing-Link Candidate View specification.

This is a DB-first, read-only schema inventory and specification step over the
consolidated QSB Mini-DWH snapshot. It does not read raw TIM/PAR files, does
not use generated report artifacts as input, does not create a separate DB,
does not modify the input DB, and does not compute timing, model, residual,
path, or statistical quantities.
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


SCRIPT_NAME = "scripts/qsb_bridge01_missing_link_candidate_view_spec.py"
DEFAULT_DB = Path(
    "runs/QSB-DB/QSB_DB25_CONSOLIDATED_RESEARCH_SNAPSHOT/"
    "qsb_research_consolidated_snapshot.db"
)
DEFAULT_OUTPUT_ROOT = Path("runs/QSB-DB/QSB_DB25_CONSOLIDATED_RESEARCH_SNAPSHOT")

REPORT_MD = "bridge01_missing_link_candidate_view_spec.md"
REPORT_JSON = "bridge01_missing_link_candidate_view_spec.json"
AVAILABLE_FIELD_INVENTORY_CSV = "bridge01_available_field_inventory.csv"
MISSING_FIELD_GAP_MATRIX_CSV = "bridge01_missing_field_gap_matrix.csv"
CANDIDATE_TABLE_DESIGN_CSV = "bridge01_candidate_table_design.csv"
EXISTING_VIEW_RELEVANCE_CSV = "bridge01_existing_view_relevance.csv"

OUTPUT_FILENAMES = [
    REPORT_MD,
    REPORT_JSON,
    AVAILABLE_FIELD_INVENTORY_CSV,
    MISSING_FIELD_GAP_MATRIX_CSV,
    CANDIDATE_TABLE_DESIGN_CSV,
    EXISTING_VIEW_RELEVANCE_CSV,
]

REQUIRED_CONTEXT_OBJECTS = [
    "qsb_v_db25_report_ready_snapshot",
    "qsb_v_db26_mapping_dashboard",
    "qsb_v_db27_first_mapping_work_packet",
    "qsb_v_db28_db27_token_evidence_link",
    "qsb_v_db28_external_evidence_gap",
    "qsb_v_db28_dictionary_evidence_dashboard",
]

FUTURE_TABLE_NAMES = [
    "bridge01_qm_quantity_catalog",
    "bridge01_art_quantity_catalog",
    "bridge01_functional_relation_catalog",
    "bridge01_relation_context_condition",
    "bridge01_candidate_connection_map",
    "bridge01_relation_evaluation_plan",
    "bridge01_missing_required_field",
    "bridge01_claim_boundary_catalog",
]

FUTURE_VIEW_NAMES = [
    "qsb_v_bridge01_missing_link_candidate_matrix",
    "qsb_v_bridge01_available_vs_missing_fields",
    "qsb_v_bridge01_first_candidate_route",
    "qsb_v_bridge01_bridge_readiness_dashboard",
]

CLAIM_BOUNDARY = (
    "BRIDGE01 is a read-only inventory and specification step. It produces a "
    "question-producing and test-planning schema design only. It does not test "
    "a bridge relation, does not compute physical quantities, does not perform "
    "model fitting, residual analysis, path-delay derivation, or statistical "
    "inference, and does not assign final physical meaning to unresolved TIM "
    "columns."
)


@dataclass(frozen=True)
class ConceptualField:
    layer: str
    conceptual_field: str
    match_terms: tuple[str, ...]
    availability_status: str
    blockers: tuple[str, ...]
    requires_new_table: bool
    requires_payload_ingest: bool
    requires_theory_specification: bool
    proposed_location: str
    required_before_bridge02: bool
    note: str


CONCEPTUAL_FIELDS: list[ConceptualField] = [
    ConceptualField(
        "Raw / signal layer",
        "source file",
        ("source_file", "source_path", "relative_path", "source_file_name"),
        "available_now",
        (),
        False,
        False,
        False,
        "existing DB20/DB21 source inventory",
        True,
        "File-level provenance is present for raw and TIM-side records.",
    ),
    ConceptualField(
        "Raw / signal layer",
        "raw record id",
        ("record_id", "tim_record_id", "raw_data_id"),
        "available_now",
        (),
        False,
        False,
        False,
        "existing DB20/DB21 raw record tables",
        True,
        "Raw record identifiers are present for lineage and joins.",
    ),
    ConceptualField(
        "Raw / signal layer",
        "record index",
        ("record_index", "line_number"),
        "available_now",
        (),
        False,
        False,
        False,
        "existing DB20/DB21 raw record tables",
        True,
        "Record-order fields are present as inventory fields only.",
    ),
    ConceptualField(
        "Raw / signal layer",
        "line type",
        ("line_type", "line_type_scope", "line_family"),
        "available_now",
        (),
        False,
        False,
        False,
        "existing DB21/DB22/DB23 tables and views",
        True,
        "Line family/type fields are present for staging context.",
    ),
    ConceptualField(
        "Raw / signal layer",
        "token position",
        ("token_position", "field_index", "field_position", "field_name"),
        "available_now",
        ("blocked_by_mapping_gap",),
        False,
        False,
        False,
        "existing DB21 through DB28 mapping layers",
        True,
        "Token positions exist, but final semantic use remains blocked where mapping gaps are open.",
    ),
    ConceptualField(
        "Raw / signal layer",
        "raw token value",
        ("raw_value_text", "raw_value_or_term", "block_a_value", "block_b_value"),
        "available_now",
        ("blocked_by_mapping_gap",),
        False,
        False,
        False,
        "existing DB21 raw field values and DB27/DB28 context links",
        True,
        "Raw token strings are present; unresolved numeric tokens remain non-canonical.",
    ),
    ConceptualField(
        "Raw / signal layer",
        "source family",
        ("source_family", "source_family_label", "source_label", "source_type"),
        "available_now",
        (),
        False,
        False,
        False,
        "existing DB20/DB21 source inventory",
        True,
        "Source-family labels are available for file/context stratification.",
    ),
    ConceptualField(
        "Raw / signal layer",
        "lineage key",
        ("lineage_key", "lineage"),
        "available_now",
        (),
        False,
        False,
        False,
        "existing DB20/DB21 raw inventory",
        True,
        "Lineage keys are present and should remain the first audit join handle.",
    ),
    ConceptualField(
        "Raw / signal layer",
        "observation/file context",
        ("source_file", "source_inventory", "line_type", "record_index", "lineage_key"),
        "partially_available",
        ("blocked_by_mapping_gap",),
        False,
        False,
        False,
        "existing raw/source tables plus future context-condition table",
        True,
        "File context exists; observation semantics require reviewed mapping and evidence.",
    ),
    ConceptualField(
        "Staging / mapping layer",
        "token role candidate",
        ("token_role_candidate", "candidate_role_label", "structural_role_candidate"),
        "available_now",
        ("blocked_by_mapping_gap",),
        False,
        False,
        False,
        "existing DB23/DB26 mapping tables",
        True,
        "Candidate roles exist as non-final mapping aids.",
    ),
    ConceptualField(
        "Staging / mapping layer",
        "field dictionary seed",
        ("dictionary_seed", "field_dictionary_seed", "proposed_structural_name"),
        "available_now",
        ("blocked_by_mapping_gap",),
        False,
        False,
        False,
        "existing DB26 and DB28 dictionary seed tables",
        True,
        "Dictionary seeds exist but require review before bridge use.",
    ),
    ConceptualField(
        "Staging / mapping layer",
        "mapping status",
        ("mapping_status", "mapping_readiness", "triage_status", "blocking_status"),
        "available_now",
        ("blocked_by_mapping_gap",),
        False,
        False,
        False,
        "existing DB26/DB28 mapping dashboards",
        True,
        "Mapping status is visible; open blockers must remain explicit.",
    ),
    ConceptualField(
        "Staging / mapping layer",
        "manual review status",
        ("manual_review", "review_status", "required_manual_decision"),
        "partially_available",
        ("blocked_by_mapping_gap",),
        False,
        False,
        False,
        "existing DB26/DB27/DB28 review fields",
        True,
        "Review flags exist, but completed reviewed mappings are not yet a bridge-ready contract.",
    ),
    ConceptualField(
        "Staging / mapping layer",
        "priority tier",
        ("priority_tier", "priority", "priority_score"),
        "available_now",
        ("blocked_by_mapping_gap",),
        False,
        False,
        False,
        "existing DB26/DB27 priority tables",
        False,
        "Priority is available for ordering curation work.",
    ),
    ConceptualField(
        "Staging / mapping layer",
        "work packet assignment",
        ("work_packet", "packet_label", "required_manual_decision"),
        "available_now",
        ("blocked_by_mapping_gap",),
        False,
        False,
        False,
        "existing DB27 first mapping work packet",
        True,
        "Work-packet assignment exists for manual mapping continuation.",
    ),
    ConceptualField(
        "External evidence layer",
        "source registry id",
        ("source_registry", "source_id", "external_source_registry"),
        "available_now",
        ("blocked_by_external_evidence_gap",),
        False,
        False,
        False,
        "existing DB28 source registry",
        True,
        "External source registry rows exist, with retrieval status fields.",
    ),
    ConceptualField(
        "External evidence layer",
        "evidence status",
        ("evidence_status", "mapping_readiness", "evidence_summary"),
        "available_now",
        ("blocked_by_external_evidence_gap",),
        False,
        False,
        False,
        "existing DB28 evidence tables/views",
        True,
        "Evidence status exists for mapping assertions and dictionary seeds.",
    ),
    ConceptualField(
        "External evidence layer",
        "assertion status",
        ("assertion_status", "assertion_id"),
        "available_now",
        ("blocked_by_external_evidence_gap",),
        False,
        False,
        False,
        "existing DB28 assertion evidence",
        True,
        "Assertion status exists for dictionary/mapping evidence.",
    ),
    ConceptualField(
        "External evidence layer",
        "external dictionary seed",
        ("external_dictionary_seed", "dictionary_seed", "raw_value_or_term"),
        "available_now",
        ("blocked_by_external_evidence_gap",),
        False,
        False,
        False,
        "existing DB28 dictionary seed",
        True,
        "External dictionary seeds exist but are not bridge quantities.",
    ),
    ConceptualField(
        "External evidence layer",
        "receiver/backend/telescope dictionary seed",
        ("receiver_seed", "backend_seed", "telescope_seed", "raw_receiver", "raw_backend"),
        "available_now",
        ("blocked_by_external_evidence_gap",),
        False,
        False,
        False,
        "existing DB28 receiver/backend/telescope seed tables",
        True,
        "Instrument dictionary seed tables exist as curation assets.",
    ),
    ConceptualField(
        "External evidence layer",
        "unresolved evidence gap",
        ("evidence_gap", "open_external_evidence_gap", "gap_severity", "gap_type"),
        "available_now",
        ("blocked_by_external_evidence_gap",),
        False,
        False,
        False,
        "existing DB28 open external evidence gap",
        True,
        "Open evidence gaps are represented explicitly.",
    ),
    ConceptualField(
        "External evidence layer",
        "retrieval status",
        ("retrieval_status", "retrieval_log", "access_method"),
        "available_now",
        ("blocked_by_external_evidence_gap",),
        False,
        False,
        False,
        "existing DB28 source registry and retrieval log",
        True,
        "Retrieval state is available for future evidence readiness filters.",
    ),
    ConceptualField(
        "Future QM-side layer",
        "qm_quantity_id",
        ("qm_quantity_id", "quantity_id"),
        "partially_available",
        ("requires_new_table", "requires_theory_specification"),
        True,
        False,
        True,
        "future bridge01_qm_quantity_catalog",
        True,
        "A generic quantity catalog exists, but no side-specific QM quantity key exists.",
    ),
    ConceptualField(
        "Future QM-side layer",
        "qm_quantity_name",
        ("qm_quantity_name", "quantity_name", "symbol"),
        "partially_available",
        ("requires_new_table", "requires_theory_specification"),
        True,
        False,
        True,
        "future bridge01_qm_quantity_catalog",
        True,
        "Generic names/symbols exist; bridge-side semantics require a dedicated catalog.",
    ),
    ConceptualField(
        "Future QM-side layer",
        "qm_value",
        ("qm_value",),
        "missing",
        ("requires_new_table", "requires_payload_ingest", "requires_theory_specification"),
        True,
        True,
        True,
        "future bridge01_qm_quantity_catalog or value table",
        True,
        "No QM-side value table is present in the consolidated snapshot.",
    ),
    ConceptualField(
        "Future QM-side layer",
        "qm_unit",
        ("qm_unit", "si_unit", "unit_symbol", "unit_status"),
        "partially_available",
        ("requires_new_table", "requires_theory_specification"),
        True,
        False,
        True,
        "future bridge01_qm_quantity_catalog linked to unit catalog",
        True,
        "Generic unit metadata exists, but not attached to QM-side bridge values.",
    ),
    ConceptualField(
        "Future QM-side layer",
        "qm_context",
        ("qm_context", "context_id", "context_condition"),
        "missing",
        ("requires_new_table", "requires_payload_ingest", "requires_theory_specification"),
        True,
        True,
        True,
        "future bridge01_relation_context_condition",
        True,
        "No QM-side context-condition contract is present.",
    ),
    ConceptualField(
        "Future QM-side layer",
        "matter/signal/wave descriptor",
        ("wave", "signal", "matter", "descriptor", "source_family"),
        "partially_available",
        ("blocked_by_mapping_gap", "requires_new_table", "requires_theory_specification"),
        True,
        False,
        True,
        "future bridge01_qm_quantity_catalog",
        True,
        "Signal/file descriptors exist; QM-side descriptor semantics are not specified.",
    ),
    ConceptualField(
        "Future QM-side layer",
        "phase/frequency/momentum/energy/proxy marker",
        ("phase", "frequency", "momentum", "energy", "proxy", "frequency_low_mhz"),
        "partially_available",
        ("blocked_by_external_evidence_gap", "requires_new_table", "requires_theory_specification"),
        True,
        True,
        True,
        "future bridge01_qm_quantity_catalog",
        True,
        "Instrument frequency-band seed metadata exists; no bridge quantity marker is defined.",
    ),
    ConceptualField(
        "Future QM-side layer",
        "source of QM-side value",
        ("qm_source", "source_id", "source_name", "evidence_ref"),
        "partially_available",
        ("requires_new_table", "requires_payload_ingest", "requires_theory_specification"),
        True,
        True,
        True,
        "future bridge01_qm_quantity_catalog linked to DB28 evidence",
        True,
        "Source registry exists, but no QM-side value provenance link exists.",
    ),
    ConceptualField(
        "Future ART-side layer",
        "art_quantity_id",
        ("art_quantity_id", "quantity_id"),
        "partially_available",
        ("requires_new_table", "requires_theory_specification"),
        True,
        False,
        True,
        "future bridge01_art_quantity_catalog",
        True,
        "A generic quantity catalog exists, but no side-specific ART quantity key exists.",
    ),
    ConceptualField(
        "Future ART-side layer",
        "art_quantity_name",
        ("art_quantity_name", "quantity_name", "symbol"),
        "partially_available",
        ("requires_new_table", "requires_theory_specification"),
        True,
        False,
        True,
        "future bridge01_art_quantity_catalog",
        True,
        "Generic names/symbols exist; ART-side bridge semantics require a dedicated catalog.",
    ),
    ConceptualField(
        "Future ART-side layer",
        "art_value",
        ("art_value",),
        "missing",
        ("requires_new_table", "requires_payload_ingest", "requires_theory_specification"),
        True,
        True,
        True,
        "future bridge01_art_quantity_catalog or value table",
        True,
        "No ART-side value table is present in the consolidated snapshot.",
    ),
    ConceptualField(
        "Future ART-side layer",
        "art_unit",
        ("art_unit", "si_unit", "unit_symbol", "unit_status"),
        "partially_available",
        ("requires_new_table", "requires_theory_specification"),
        True,
        False,
        True,
        "future bridge01_art_quantity_catalog linked to unit catalog",
        True,
        "Generic unit metadata exists, but not attached to ART-side bridge values.",
    ),
    ConceptualField(
        "Future ART-side layer",
        "geometry/path/delay/context descriptor",
        ("geometry", "path", "delay", "context", "descriptor"),
        "missing",
        ("requires_new_table", "requires_payload_ingest", "requires_theory_specification"),
        True,
        True,
        True,
        "future bridge01_art_quantity_catalog and bridge01_relation_context_condition",
        True,
        "No ART-side path/geometry/context descriptor table is present.",
    ),
    ConceptualField(
        "Future ART-side layer",
        "gravitational/metric/path context",
        ("gravitational", "metric", "path_context", "geometry"),
        "missing",
        ("requires_new_table", "requires_payload_ingest", "requires_theory_specification"),
        True,
        True,
        True,
        "future bridge01_art_quantity_catalog and relation context table",
        True,
        "No metric/context payload layer is present.",
    ),
    ConceptualField(
        "Future ART-side layer",
        "source of ART-side value",
        ("art_source", "source_id", "source_name", "evidence_ref"),
        "partially_available",
        ("requires_new_table", "requires_payload_ingest", "requires_theory_specification"),
        True,
        True,
        True,
        "future bridge01_art_quantity_catalog linked to DB28 evidence",
        True,
        "Source registry exists, but no ART-side value provenance link exists.",
    ),
    ConceptualField(
        "Future bridge relation layer",
        "relation_id",
        ("relation_id",),
        "missing",
        ("requires_new_table", "requires_theory_specification"),
        True,
        False,
        True,
        "future bridge01_functional_relation_catalog",
        True,
        "No bridge relation identifier exists.",
    ),
    ConceptualField(
        "Future bridge relation layer",
        "qm_quantity_id",
        ("qm_quantity_id",),
        "missing",
        ("requires_new_table", "requires_theory_specification"),
        True,
        False,
        True,
        "future bridge01_functional_relation_catalog",
        True,
        "No bridge relation can point to a QM-side quantity yet.",
    ),
    ConceptualField(
        "Future bridge relation layer",
        "art_quantity_id",
        ("art_quantity_id",),
        "missing",
        ("requires_new_table", "requires_theory_specification"),
        True,
        False,
        True,
        "future bridge01_functional_relation_catalog",
        True,
        "No bridge relation can point to an ART-side quantity yet.",
    ),
    ConceptualField(
        "Future bridge relation layer",
        "relation_expression",
        ("relation_expression", "expression"),
        "missing",
        ("requires_new_table", "requires_theory_specification"),
        True,
        False,
        True,
        "future bridge01_functional_relation_catalog",
        True,
        "No candidate relation expression is specified at BRIDGE01.",
    ),
    ConceptualField(
        "Future bridge relation layer",
        "relation_type",
        ("relation_type",),
        "partially_available",
        ("requires_new_table", "requires_theory_specification"),
        True,
        False,
        True,
        "future bridge01_functional_relation_catalog",
        True,
        "Existing relation_type fields describe structural token comparisons, not bridge relations.",
    ),
    ConceptualField(
        "Future bridge relation layer",
        "unit_mapping_rule",
        ("unit_mapping_rule", "conversion_rule"),
        "partially_available",
        ("requires_new_table", "requires_theory_specification"),
        True,
        False,
        True,
        "future bridge01_functional_relation_catalog linked to unit_dimension_catalog",
        True,
        "Generic conversion rules exist; side-to-side bridge unit mapping does not.",
    ),
    ConceptualField(
        "Future bridge relation layer",
        "validity_domain",
        ("validity_domain", "domain_name", "domain_type"),
        "partially_available",
        ("requires_new_table", "requires_theory_specification"),
        True,
        False,
        True,
        "future bridge01_functional_relation_catalog",
        True,
        "Generic quantity domains exist; bridge validity domains do not.",
    ),
    ConceptualField(
        "Future bridge relation layer",
        "relation_status",
        ("relation_status",),
        "missing",
        ("requires_new_table", "requires_theory_specification"),
        True,
        False,
        True,
        "future bridge01_functional_relation_catalog",
        True,
        "No bridge relation status field exists.",
    ),
    ConceptualField(
        "Future bridge relation layer",
        "evidence_link",
        ("evidence_link", "link_id", "evidence_ref"),
        "partially_available",
        ("blocked_by_external_evidence_gap", "requires_new_table"),
        True,
        False,
        False,
        "future bridge01_candidate_connection_map linked to DB28 evidence",
        True,
        "DB28 token evidence links exist; bridge relation evidence links do not.",
    ),
    ConceptualField(
        "Future bridge relation layer",
        "claim_boundary_status",
        ("claim_boundary", "claim_level", "bridge_claim_allowed"),
        "partially_available",
        ("requires_new_table",),
        True,
        False,
        False,
        "future bridge01_claim_boundary_catalog linked to existing claim catalog",
        True,
        "A generic claim boundary catalog exists; bridge-specific status should be explicit.",
    ),
    ConceptualField(
        "Future evaluation/result layer",
        "evaluation_id",
        ("evaluation_id",),
        "missing",
        ("requires_new_table", "requires_theory_specification"),
        True,
        False,
        True,
        "future bridge01_relation_evaluation_plan",
        True,
        "No evaluation-plan/result identifier exists.",
    ),
    ConceptualField(
        "Future evaluation/result layer",
        "relation_id",
        ("relation_id",),
        "missing",
        ("requires_new_table", "requires_theory_specification"),
        True,
        False,
        True,
        "future bridge01_relation_evaluation_plan",
        True,
        "No result/evaluation table can reference a bridge relation yet.",
    ),
    ConceptualField(
        "Future evaluation/result layer",
        "input_value_id",
        ("input_value_id",),
        "missing",
        ("requires_new_table", "requires_payload_ingest", "requires_theory_specification"),
        True,
        True,
        True,
        "future bridge01_relation_evaluation_plan",
        True,
        "No controlled input value table exists.",
    ),
    ConceptualField(
        "Future evaluation/result layer",
        "expected_value",
        ("expected_value",),
        "missing",
        ("requires_new_table", "requires_payload_ingest", "requires_theory_specification"),
        True,
        True,
        True,
        "future bridge01_relation_evaluation_plan",
        True,
        "No expected-value field should be populated before relation and controls are specified.",
    ),
    ConceptualField(
        "Future evaluation/result layer",
        "observed_value",
        ("observed_value",),
        "missing",
        ("requires_new_table", "requires_payload_ingest"),
        True,
        True,
        False,
        "future bridge01_relation_evaluation_plan",
        True,
        "No observed bridge-result value table exists.",
    ),
    ConceptualField(
        "Future evaluation/result layer",
        "delta",
        ("delta",),
        "missing",
        ("requires_new_table", "requires_payload_ingest", "requires_theory_specification"),
        True,
        True,
        True,
        "future bridge01_relation_evaluation_plan",
        True,
        "No delta field exists and none should be derived in BRIDGE01.",
    ),
    ConceptualField(
        "Future evaluation/result layer",
        "delta_class",
        ("delta_class",),
        "missing",
        ("requires_new_table", "requires_theory_specification"),
        True,
        False,
        True,
        "future bridge01_relation_evaluation_plan",
        True,
        "No delta classification vocabulary exists.",
    ),
    ConceptualField(
        "Future evaluation/result layer",
        "context_id",
        ("context_id", "context_condition"),
        "missing",
        ("requires_new_table", "requires_payload_ingest", "requires_theory_specification"),
        True,
        True,
        True,
        "future bridge01_relation_context_condition",
        True,
        "No bridge evaluation context id exists.",
    ),
    ConceptualField(
        "Future evaluation/result layer",
        "control_status",
        ("control_status",),
        "missing",
        ("requires_new_table", "requires_theory_specification"),
        True,
        False,
        True,
        "future bridge01_relation_evaluation_plan",
        True,
        "No control-status field exists for bridge tests.",
    ),
    ConceptualField(
        "Future evaluation/result layer",
        "failure_mode",
        ("failure_mode",),
        "missing",
        ("requires_new_table", "requires_theory_specification"),
        True,
        False,
        True,
        "future bridge01_relation_evaluation_plan",
        True,
        "No failure-mode vocabulary exists for bridge candidates.",
    ),
    ConceptualField(
        "Future evaluation/result layer",
        "review_status",
        ("review_status",),
        "partially_available",
        ("requires_new_table", "requires_theory_specification"),
        True,
        False,
        True,
        "future bridge01_relation_evaluation_plan",
        True,
        "Review status exists for mapping/evidence, not for bridge evaluation plans.",
    ),
    ConceptualField(
        "Future modulation/recovery test layer",
        "modulation_id",
        ("modulation_id",),
        "missing",
        ("requires_new_table", "requires_theory_specification"),
        True,
        False,
        True,
        "future bridge test-plan extension",
        False,
        "No modulation/recovery test table exists.",
    ),
    ConceptualField(
        "Future modulation/recovery test layer",
        "input_pattern",
        ("input_pattern",),
        "missing",
        ("requires_new_table", "requires_payload_ingest", "requires_theory_specification"),
        True,
        True,
        True,
        "future bridge test-plan extension",
        False,
        "No input-pattern field exists for modulation/recovery tests.",
    ),
    ConceptualField(
        "Future modulation/recovery test layer",
        "expected_response_pattern",
        ("expected_response_pattern",),
        "missing",
        ("requires_new_table", "requires_payload_ingest", "requires_theory_specification"),
        True,
        True,
        True,
        "future bridge test-plan extension",
        False,
        "No expected response-pattern field exists.",
    ),
    ConceptualField(
        "Future modulation/recovery test layer",
        "observed_response_pattern",
        ("observed_response_pattern",),
        "missing",
        ("requires_new_table", "requires_payload_ingest"),
        True,
        True,
        False,
        "future bridge test-plan extension",
        False,
        "No observed response-pattern field exists.",
    ),
    ConceptualField(
        "Future modulation/recovery test layer",
        "match_score",
        ("match_score",),
        "missing",
        ("requires_new_table", "requires_theory_specification"),
        True,
        False,
        True,
        "future bridge test-plan extension",
        False,
        "No match-score field exists and no scoring rule is specified.",
    ),
    ConceptualField(
        "Future modulation/recovery test layer",
        "recovery_status",
        ("recovery_status",),
        "missing",
        ("requires_new_table", "requires_theory_specification"),
        True,
        False,
        True,
        "future bridge test-plan extension",
        False,
        "No recovery-status vocabulary exists.",
    ),
    ConceptualField(
        "Future modulation/recovery test layer",
        "context_controls",
        ("context_controls", "control_status", "context_condition"),
        "missing",
        ("requires_new_table", "requires_theory_specification"),
        True,
        False,
        True,
        "future bridge test-plan extension",
        False,
        "No modulation/recovery context-control layer exists.",
    ),
]


TABLE_DESIGN_ROWS: list[dict[str, str]] = [
    {
        "object_kind": "table",
        "proposed_name": "bridge01_qm_quantity_catalog",
        "design_group": "future QM-side quantity catalog",
        "primary_key_or_join_key": "qm_quantity_id",
        "core_fields": (
            "qm_quantity_id; qm_quantity_name; qm_value_status; qm_unit; qm_context; "
            "signal_or_wave_descriptor; source_evidence_link; claim_boundary_status"
        ),
        "required_inputs": "Reviewed mapping context; side-specific theory vocabulary; value-source rule",
        "bridge02_readiness_role": "Defines one side-specific candidate quantity without populating analysis values.",
        "not_created_reason": "BRIDGE01 is specification-only.",
        "claim_boundary": "Catalog entries would be candidates, not result claims.",
    },
    {
        "object_kind": "table",
        "proposed_name": "bridge01_art_quantity_catalog",
        "design_group": "future ART-side quantity catalog",
        "primary_key_or_join_key": "art_quantity_id",
        "core_fields": (
            "art_quantity_id; art_quantity_name; art_value_status; art_unit; "
            "geometry_path_context_descriptor; source_evidence_link; claim_boundary_status"
        ),
        "required_inputs": "Path/geometry/context payload rule; source evidence; unit/domain vocabulary",
        "bridge02_readiness_role": "Defines one ART-side/path-side candidate quantity without deriving values.",
        "not_created_reason": "BRIDGE01 is specification-only.",
        "claim_boundary": "No path or metric quantity is inferred at BRIDGE01.",
    },
    {
        "object_kind": "table",
        "proposed_name": "bridge01_functional_relation_catalog",
        "design_group": "future bridge relation catalog",
        "primary_key_or_join_key": "relation_id",
        "core_fields": (
            "relation_id; qm_quantity_id; art_quantity_id; relation_expression; "
            "relation_type; unit_mapping_rule; validity_domain; relation_status"
        ),
        "required_inputs": "Explicit theory specification and unit/domain controls",
        "bridge02_readiness_role": "Names the relation to be asked about before any evaluation plan is populated.",
        "not_created_reason": "No relation expression is authorized in BRIDGE01.",
        "claim_boundary": "A relation row would describe a test question, not a result.",
    },
    {
        "object_kind": "table",
        "proposed_name": "bridge01_relation_context_condition",
        "design_group": "future context/control table",
        "primary_key_or_join_key": "context_id",
        "core_fields": (
            "context_id; raw_observation_context_id; receiver_backend_context_id; "
            "external_evidence_status; mapping_status; validity_domain; control_status"
        ),
        "required_inputs": "Raw lineage; reviewed receiver/backend mapping; evidence gap state",
        "bridge02_readiness_role": "Keeps context conditions explicit for each candidate route.",
        "not_created_reason": "Context semantics require reviewed mapping and evidence closure.",
        "claim_boundary": "Context rows are controls, not interpretation.",
    },
    {
        "object_kind": "table",
        "proposed_name": "bridge01_candidate_connection_map",
        "design_group": "future connection table",
        "primary_key_or_join_key": "connection_id",
        "core_fields": (
            "connection_id; lineage_key; token_position; work_packet_id; evidence_link_id; "
            "qm_quantity_id; art_quantity_id; relation_id; missing_field_status"
        ),
        "required_inputs": "DB21 lineage, DB27 work packet, DB28 evidence link, future side catalogs",
        "bridge02_readiness_role": "The minimal join spine for a Missing-Link Candidate View.",
        "not_created_reason": "Future side catalogs and relation catalog do not exist yet.",
        "claim_boundary": "Connection means joinability and readiness state only.",
    },
    {
        "object_kind": "table",
        "proposed_name": "bridge01_relation_evaluation_plan",
        "design_group": "future result/evaluation planning table",
        "primary_key_or_join_key": "evaluation_id",
        "core_fields": (
            "evaluation_id; relation_id; input_value_id; expected_value_status; "
            "observed_value_status; delta_status; context_id; control_status; "
            "failure_mode; review_status"
        ),
        "required_inputs": "Relation catalog; value-source rules; controls; failure-mode vocabulary",
        "bridge02_readiness_role": "Specifies result fields and controls before any result values are generated.",
        "not_created_reason": "BRIDGE01 does not compute or populate evaluation values.",
        "claim_boundary": "Evaluation plan rows are not analysis outputs.",
    },
    {
        "object_kind": "table",
        "proposed_name": "bridge01_missing_required_field",
        "design_group": "future gap-tracking table",
        "primary_key_or_join_key": "missing_field_id",
        "core_fields": (
            "missing_field_id; relation_id; conceptual_layer; conceptual_field; "
            "gap_status; blocker_class; required_action; blocking_bridge02"
        ),
        "required_inputs": "BRIDGE01 gap matrix and future relation catalog",
        "bridge02_readiness_role": "Tracks missing fields that block a bridge candidate route.",
        "not_created_reason": "The CSV gap matrix is the BRIDGE01 artifact for this run.",
        "claim_boundary": "Gap tracking records absence/readiness only.",
    },
    {
        "object_kind": "table",
        "proposed_name": "bridge01_claim_boundary_catalog",
        "design_group": "future bridge claim-boundary table",
        "primary_key_or_join_key": "bridge_claim_boundary_id",
        "core_fields": (
            "bridge_claim_boundary_id; relation_id; evaluation_id; claim_boundary_status; "
            "allowed_statement; forbidden_statement; review_status"
        ),
        "required_inputs": "Existing claim boundary catalog and bridge relation/evaluation ids",
        "bridge02_readiness_role": "Makes allowed/forbidden statements explicit before analysis.",
        "not_created_reason": "Bridge relation and evaluation ids do not exist yet.",
        "claim_boundary": "Prevents claim escalation from schema readiness.",
    },
    {
        "object_kind": "view",
        "proposed_name": "qsb_v_bridge01_missing_link_candidate_matrix",
        "design_group": "future candidate matrix view",
        "primary_key_or_join_key": "connection_id; relation_id",
        "core_fields": (
            "raw context; mapping context; evidence link; qm/art quantity ids; "
            "relation expression status; gap status; claim boundary status"
        ),
        "required_inputs": "All proposed bridge01_* tables above",
        "bridge02_readiness_role": "Presents candidate routes as questions to be tested.",
        "not_created_reason": "Source tables are not yet present.",
        "claim_boundary": "A matrix row would not be a claim row.",
    },
    {
        "object_kind": "view",
        "proposed_name": "qsb_v_bridge01_available_vs_missing_fields",
        "design_group": "future readiness dashboard view",
        "primary_key_or_join_key": "conceptual_field",
        "core_fields": "conceptual layer; conceptual field; availability status; blocker class; required action",
        "required_inputs": "Gap tracking table and schema inventory",
        "bridge02_readiness_role": "Shows whether the bridge question can be asked data-analytically.",
        "not_created_reason": "BRIDGE01 exports this as CSV/JSON/MD instead.",
        "claim_boundary": "Readiness status only.",
    },
    {
        "object_kind": "view",
        "proposed_name": "qsb_v_bridge01_first_candidate_route",
        "design_group": "future minimal route view",
        "primary_key_or_join_key": "connection_id",
        "core_fields": (
            "one raw context; one mapped receiver/backend context; one QM-side quantity; "
            "one ART-side quantity; one relation; one evaluation plan; one evidence chain"
        ),
        "required_inputs": "Connection map, relation catalog, context condition, evaluation plan",
        "bridge02_readiness_role": "Restricts BRIDGE02 to the smallest auditable candidate route.",
        "not_created_reason": "The route cannot be instantiated without future tables.",
        "claim_boundary": "A first route is a test-plan object.",
    },
    {
        "object_kind": "view",
        "proposed_name": "qsb_v_bridge01_bridge_readiness_dashboard",
        "design_group": "future readiness dashboard view",
        "primary_key_or_join_key": "readiness_metric",
        "core_fields": "mapping ready; evidence ready; quantity ready; relation ready; controls ready",
        "required_inputs": "Future bridge tables and claim-boundary rules",
        "bridge02_readiness_role": "Provides go/no-go readiness metrics for BRIDGE02 planning.",
        "not_created_reason": "BRIDGE01 is report-output only.",
        "claim_boundary": "Dashboard metrics are not scientific results.",
    },
]


def utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def pretty_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=True, indent=2)


def output_paths(output_root: Path) -> dict[str, Path]:
    return {name: output_root / name for name in OUTPUT_FILENAMES}


def quote_identifier(identifier: str) -> str:
    return '"' + identifier.replace('"', '""') + '"'


def quote_pragma_name(identifier: str) -> str:
    return "'" + identifier.replace("'", "''") + "'"


def clean_text(value: Any) -> str:
    if value is None:
        return ""
    text = str(value).replace("\n", " ").replace("\r", " ")
    return re.sub(r"\s+", " ", text).strip()


def compact_join(values: list[str] | tuple[str, ...], limit: int | None = None) -> str:
    selected = list(values)
    if limit is not None and len(selected) > limit:
        selected = selected[:limit] + [f"... (+{len(values) - limit} more)"]
    return "; ".join(selected)


def term_in_haystack(term: str, haystack: str) -> bool:
    normalized_haystack = re.sub(r"[^a-z0-9]+", " ", haystack.lower())
    compact_haystack = normalized_haystack.replace(" ", "")
    normalized_term = re.sub(r"[^a-z0-9]+", " ", term.lower()).strip()
    compact_term = normalized_term.replace(" ", "")
    return normalized_term in normalized_haystack or compact_term in compact_haystack


def concept_matches_column(concept: ConceptualField, object_name: str, column_name: str) -> bool:
    haystack = f"{object_name} {column_name}"
    return any(term_in_haystack(term, haystack) for term in concept.match_terms)


def connect_read_only(db_path: Path) -> sqlite3.Connection:
    con = sqlite3.connect(f"file:{db_path.resolve()}?mode=ro", uri=True)
    con.row_factory = sqlite3.Row
    con.execute("PRAGMA foreign_keys = ON")
    con.execute("PRAGMA query_only = ON")
    return con


def ensure_preconditions(db_path: Path, output_root: Path) -> None:
    if not db_path.exists():
        raise FileNotFoundError(f"Input DB does not exist: {db_path}")
    if not db_path.is_file():
        raise ValueError(f"Input DB path is not a file: {db_path}")
    if not output_root.exists():
        raise FileNotFoundError(f"Output root does not exist: {output_root}")
    if not output_root.is_dir():
        raise ValueError(f"Output root is not a directory: {output_root}")
    if db_path.parent.resolve() != output_root.resolve():
        raise ValueError("Output root must be the consolidated snapshot directory.")
    if db_path.stat().st_size <= 0:
        raise ValueError(f"Input DB is empty: {db_path}")

    existing_outputs = [
        str(path) for path in output_paths(output_root).values()
        if path.exists()
    ]
    if existing_outputs:
        raise FileExistsError(
            "Refusing to overwrite existing BRIDGE01 output file(s): "
            + "; ".join(existing_outputs)
        )


def fetch_schema(con: sqlite3.Connection) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]]]:
    objects = [
        dict(row)
        for row in con.execute(
            """
            SELECT type, name, sql
            FROM sqlite_master
            WHERE type IN ('table', 'view')
              AND name NOT LIKE 'sqlite_%'
            ORDER BY type, name
            """
        ).fetchall()
    ]
    schema_rows: list[dict[str, Any]] = []
    fk_rows: list[dict[str, Any]] = []
    for obj in objects:
        name = str(obj["name"])
        object_type = str(obj["type"])
        pragma_name = quote_pragma_name(name)
        for col in con.execute(f"PRAGMA table_info({pragma_name})").fetchall():
            schema_rows.append(
                {
                    "object_type": object_type,
                    "object_name": name,
                    "column_index": col["cid"],
                    "column_name": col["name"],
                    "data_type": col["type"],
                    "notnull": col["notnull"],
                    "default_value": col["dflt_value"],
                    "primary_key": col["pk"],
                }
            )
        if object_type == "table":
            for fk in con.execute(f"PRAGMA foreign_key_list({pragma_name})").fetchall():
                fk_rows.append(
                    {
                        "object_name": name,
                        "fk_id": fk["id"],
                        "fk_seq": fk["seq"],
                        "from_column": fk["from"],
                        "to_table": fk["table"],
                        "to_column": fk["to"],
                        "on_update": fk["on_update"],
                        "on_delete": fk["on_delete"],
                        "match": fk["match"],
                    }
                )
    return objects, schema_rows, fk_rows


def safe_count(con: sqlite3.Connection, object_name: str) -> tuple[str, int | str, str]:
    try:
        quoted = quote_identifier(object_name)
        row = con.execute(f"SELECT COUNT(*) AS row_count FROM {quoted}").fetchone()
        count = int(row["row_count"]) if row is not None else 0
        return "ok", count, ""
    except Exception as exc:  # pragma: no cover - defensive inventory path
        return "error", "", str(exc)


def build_fk_lookup(fk_rows: list[dict[str, Any]]) -> dict[tuple[str, str], list[str]]:
    lookup: dict[tuple[str, str], list[str]] = {}
    for row in fk_rows:
        key = (str(row["object_name"]), str(row["from_column"]))
        target = f"{row['to_table']}.{row['to_column']}"
        lookup.setdefault(key, []).append(target)
    return lookup


def matched_concepts_for_column(row: dict[str, Any]) -> list[ConceptualField]:
    object_name = str(row["object_name"])
    column_name = str(row["column_name"])
    return [
        concept for concept in CONCEPTUAL_FIELDS
        if concept_matches_column(concept, object_name, column_name)
    ]


def build_available_field_inventory(
    schema_rows: list[dict[str, Any]],
    fk_rows: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    fk_lookup = build_fk_lookup(fk_rows)
    output: list[dict[str, Any]] = []
    for row in schema_rows:
        matches = matched_concepts_for_column(row)
        layers = sorted({match.layer for match in matches})
        concepts = sorted({match.conceptual_field for match in matches})
        classifiers = sorted(
            {
                item
                for match in matches
                for item in (
                    [match.availability_status]
                    + list(match.blockers)
                    + (["requires_new_table"] if match.requires_new_table else [])
                    + (["requires_payload_ingest"] if match.requires_payload_ingest else [])
                    + (
                        ["requires_theory_specification"]
                        if match.requires_theory_specification
                        else []
                    )
                )
            }
        )
        if any(match.availability_status == "available_now" for match in matches):
            availability_role = "available_now_support"
        elif any(match.availability_status == "partially_available" for match in matches):
            availability_role = "partial_support"
        elif matches:
            availability_role = "future_gap_reference"
        else:
            availability_role = "schema_inventory"
        notes: list[str] = []
        if row["object_name"] in REQUIRED_CONTEXT_OBJECTS:
            notes.append("required BRIDGE01 context object")
        if matches:
            notes.append("matched to conceptual field inventory")
        else:
            notes.append("no direct bridge concept match")
        fk_refs = fk_lookup.get((str(row["object_name"]), str(row["column_name"])), [])
        output.append(
            {
                "object_type": row["object_type"],
                "object_name": row["object_name"],
                "column_index": row["column_index"],
                "column_name": row["column_name"],
                "data_type": row["data_type"],
                "notnull": row["notnull"],
                "primary_key": row["primary_key"],
                "foreign_key_refs": compact_join(fk_refs),
                "conceptual_layer_matches": compact_join(layers),
                "conceptual_field_matches": compact_join(concepts),
                "availability_role": availability_role,
                "classifiers": compact_join(classifiers),
                "notes": compact_join(notes),
            }
        )
    return output


def find_concept_examples(
    schema_rows: list[dict[str, Any]],
    concept: ConceptualField,
    limit: int = 8,
) -> list[str]:
    examples = []
    for row in schema_rows:
        if concept_matches_column(concept, str(row["object_name"]), str(row["column_name"])):
            examples.append(f"{row['object_name']}.{row['column_name']}")
    return sorted(set(examples))[:limit]


def build_gap_matrix(schema_rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    output: list[dict[str, Any]] = []
    for concept in CONCEPTUAL_FIELDS:
        examples = find_concept_examples(schema_rows, concept)
        status = concept.availability_status
        if status in {"available_now", "partially_available"} and not examples:
            status = "missing"
        available_examples = examples if status == "available_now" else []
        partial_examples = examples if status == "partially_available" else []
        classifiers = [status] + list(concept.blockers)
        if concept.requires_new_table:
            classifiers.append("requires_new_table")
        if concept.requires_payload_ingest:
            classifiers.append("requires_payload_ingest")
        if concept.requires_theory_specification:
            classifiers.append("requires_theory_specification")
        output.append(
            {
                "conceptual_layer": concept.layer,
                "conceptual_field": concept.conceptual_field,
                "availability_status": status,
                "classifiers": compact_join(sorted(set(classifiers))),
                "available_object_count": len(available_examples),
                "available_examples": compact_join(available_examples, limit=8),
                "partial_object_count": len(partial_examples),
                "partial_examples": compact_join(partial_examples, limit=8),
                "blocked_by_mapping_gap": int("blocked_by_mapping_gap" in concept.blockers),
                "blocked_by_external_evidence_gap": int(
                    "blocked_by_external_evidence_gap" in concept.blockers
                ),
                "requires_new_table": int(concept.requires_new_table),
                "requires_payload_ingest": int(concept.requires_payload_ingest),
                "requires_theory_specification": int(concept.requires_theory_specification),
                "proposed_location": concept.proposed_location,
                "required_before_bridge02": int(concept.required_before_bridge02),
                "note": concept.note,
            }
        )
    return output


def relevant_layers_for_columns(schema_rows: list[dict[str, Any]]) -> tuple[list[str], list[str]]:
    layers: set[str] = set()
    concepts: set[str] = set()
    for row in schema_rows:
        for concept in matched_concepts_for_column(row):
            layers.add(concept.layer)
            concepts.add(concept.conceptual_field)
    return sorted(layers), sorted(concepts)


def build_view_relevance(
    con: sqlite3.Connection,
    objects: list[dict[str, Any]],
    schema_rows: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    schema_by_object: dict[str, list[dict[str, Any]]] = {}
    for row in schema_rows:
        schema_by_object.setdefault(str(row["object_name"]), []).append(row)

    output: list[dict[str, Any]] = []
    for obj in objects:
        if obj["type"] != "view":
            continue
        name = str(obj["name"])
        rows_for_object = schema_by_object.get(name, [])
        layers, concepts = relevant_layers_for_columns(rows_for_object)
        layer_text = compact_join(layers)
        concept_text = compact_join(concepts, limit=12)
        row_count_status, row_count, row_count_note = safe_count(con, name)
        raw_signal = any(layer == "Raw / signal layer" for layer in layers)
        mapping = any(layer == "Staging / mapping layer" for layer in layers)
        external = any(layer == "External evidence layer" for layer in layers)
        future = any(layer.startswith("Future ") for layer in layers)
        if name in REQUIRED_CONTEXT_OBJECTS:
            relevance_class = "required_context_view"
            inspected_reason = "required by BRIDGE01 request"
        elif raw_signal or mapping or external:
            relevance_class = "candidate_support_view"
            inspected_reason = "QSB view with current support fields"
        elif future:
            relevance_class = "generic_future_support_view"
            inspected_reason = "QSB view with generic future-support terms"
        else:
            relevance_class = "background_project_view"
            inspected_reason = "project view inventory"
        output.append(
            {
                "object_name": name,
                "object_type": "view",
                "inspected_reason": inspected_reason,
                "row_count_status": row_count_status,
                "row_count": row_count,
                "row_count_note": row_count_note,
                "column_count": len(rows_for_object),
                "relevant_layers": layer_text,
                "relevant_concepts": concept_text,
                "relevance_class": relevance_class,
                "has_raw_signal_context": int(raw_signal),
                "has_mapping_context": int(mapping),
                "has_external_evidence_context": int(external),
                "has_future_bridge_field_names": int(future),
                "notes": (
                    "Required context view inspected."
                    if name in REQUIRED_CONTEXT_OBJECTS
                    else "Inventory classification based on view column names."
                ),
            }
        )
    return output


def required_context_presence(
    objects: list[dict[str, Any]],
    schema_rows: list[dict[str, Any]],
    view_relevance: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    object_lookup = {str(row["name"]): str(row["type"]) for row in objects}
    columns_by_name: dict[str, int] = {}
    for row in schema_rows:
        columns_by_name[str(row["object_name"])] = columns_by_name.get(str(row["object_name"]), 0) + 1
    view_counts = {str(row["object_name"]): row for row in view_relevance}
    rows: list[dict[str, Any]] = []
    for name in REQUIRED_CONTEXT_OBJECTS:
        present = name in object_lookup
        relevance = view_counts.get(name, {})
        rows.append(
            {
                "object_name": name,
                "object_type": object_lookup.get(name, "missing"),
                "presence_status": "present" if present else "missing",
                "column_count": columns_by_name.get(name, 0),
                "row_count": relevance.get("row_count", ""),
                "row_count_status": relevance.get("row_count_status", ""),
            }
        )
    return rows


def summarize_gap_status(gap_matrix: list[dict[str, Any]]) -> list[dict[str, Any]]:
    summary: dict[tuple[str, str], int] = {}
    for row in gap_matrix:
        key = (str(row["conceptual_layer"]), str(row["availability_status"]))
        summary[key] = summary.get(key, 0) + 1
    return [
        {
            "conceptual_layer": layer,
            "availability_status": status,
            "field_count": count,
        }
        for (layer, status), count in sorted(summary.items())
    ]


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
            text = clean_text(row.get(column, ""))
            if len(text) > 140:
                text = text[:137] + "..."
            cells.append(text.replace("|", "\\|"))
        lines.append("| " + " | ".join(cells) + " |")
    return "\n".join(lines)


def build_markdown(data: dict[str, Any]) -> str:
    gap_matrix = data["missing_field_gap_matrix"]
    required_rows = data["required_context_presence"]
    design_rows = data["candidate_table_design"]
    gap_summary = data["gap_status_summary"]

    support_rows = [
        row for row in gap_matrix
        if row["availability_status"] in {"available_now", "partially_available"}
    ]
    missing_rows = [
        row for row in gap_matrix
        if (
            row["availability_status"] == "missing"
            or row["requires_new_table"]
            or row["requires_payload_ingest"]
            or row["requires_theory_specification"]
        )
    ]
    connection_rows = [
        row for row in design_rows
        if "connection" in row["design_group"] or row["proposed_name"] in {
            "bridge01_relation_context_condition",
            "bridge01_candidate_connection_map",
            "bridge01_functional_relation_catalog",
        }
    ]
    result_rows = [
        row for row in design_rows
        if "evaluation" in row["design_group"]
        or "gap-tracking" in row["design_group"]
        or "claim-boundary" in row["design_group"]
        or row["object_kind"] == "view"
    ]

    lines = [
        "# QSB-BRIDGE01 Missing-Link Candidate View Specification",
        "",
        f"Generated at UTC: {data['metadata']['generated_at_utc']}",
        f"Data substrate: `{data['metadata']['db_path']}`",
        f"Operational mode: {data['metadata']['operation_mode']}",
        f"DB modified: {data['metadata']['db_modified']}",
        "",
        "## 1. Executive summary",
        "",
        "BRIDGE01 inspected the consolidated research DB as a read-only schema and "
        "view inventory. Current DB assets already cover raw/source lineage, "
        "token-position staging, mapping work packets, dictionary seeds, and "
        "external evidence-gap state. They do not yet contain side-specific "
        "QM/ART quantity-value tables, a bridge relation catalog, evaluation-plan "
        "fields, or modulation/recovery test fields.",
        "",
        "The proposed Missing-Link Candidate View should therefore be a planning "
        "surface: it asks what can be joined, what relation would be tested later, "
        "which fields are absent, which evidence is required, which controls are "
        "needed, and what would falsify a candidate.",
        "",
        "## 2. Why BRIDGE01 exists",
        "",
        "The project framing treats the database as part of the research method. "
        "The bridge question can only become data-analytical after the DB can "
        "represent raw context, mapping state, evidence state, side-specific "
        "quantity definitions, candidate functional relations, controls, and "
        "result/evaluation fields in one auditable route. BRIDGE01 specifies that "
        "route without testing or populating it.",
        "",
        "## 3. Current DB assets relevant to the Missing-Link question",
        "",
        f"Project tables inspected: {data['metadata']['table_count']}",
        f"Project views inspected: {data['metadata']['view_count']}",
        f"Schema fields inspected via PRAGMA table_info: {data['metadata']['schema_field_count']}",
        f"Table foreign-key entries inspected via PRAGMA foreign_key_list: {data['metadata']['foreign_key_count']}",
        "",
        render_table(
            required_rows,
            ["object_name", "object_type", "presence_status", "column_count", "row_count_status", "row_count"],
        ),
        "",
        "## 4. Existing fields that can already support Bridge candidate construction",
        "",
        "Available or partial support is strongest in the raw/signal, mapping, and "
        "external-evidence layers. These fields can support construction of a "
        "future candidate route, but they do not by themselves define a bridge "
        "relation or result layer.",
        "",
        render_table(
            support_rows,
            [
                "conceptual_layer",
                "conceptual_field",
                "availability_status",
                "classifiers",
                "available_examples",
                "partial_examples",
            ],
            limit=28,
        ),
        "",
        "Gap-status summary:",
        "",
        render_table(gap_summary, ["conceptual_layer", "availability_status", "field_count"]),
        "",
        "## 5. Missing fields / missing tables",
        "",
        "The missing layer is not a single field. It is a set of side-specific "
        "catalogs, relation fields, value-source rules, controls, and result-plan "
        "fields that must exist before the bridge question can be asked in data.",
        "",
        render_table(
            missing_rows,
            [
                "conceptual_layer",
                "conceptual_field",
                "availability_status",
                "classifiers",
                "proposed_location",
                "note",
            ],
            limit=36,
        ),
        "",
        "## 6. Proposed Missing-Link Candidate View design",
        "",
        "The future `qsb_v_bridge01_missing_link_candidate_matrix` should be a "
        "question-producing view, not a claim-producing view. A row should expose "
        "joinability and readiness fields such as:",
        "",
        "- raw lineage and file/record context",
        "- mapped token position and receiver/backend/context state",
        "- external evidence link and open evidence-gap state",
        "- candidate QM-side quantity id and readiness status",
        "- candidate ART-side quantity id and readiness status",
        "- relation id, relation-expression status, unit-mapping status, and validity-domain status",
        "- expected/observed/delta field presence status, without values in BRIDGE01",
        "- control status, failure-mode status, review status, and claim-boundary status",
        "",
        "## 7. Proposed future connection tables",
        "",
        render_table(
            connection_rows,
            [
                "proposed_name",
                "object_kind",
                "primary_key_or_join_key",
                "core_fields",
                "bridge02_readiness_role",
            ],
        ),
        "",
        "## 8. Proposed future result tables",
        "",
        render_table(
            result_rows,
            [
                "proposed_name",
                "object_kind",
                "design_group",
                "primary_key_or_join_key",
                "bridge02_readiness_role",
            ],
        ),
        "",
        "## 9. Minimal first Bridge candidate route",
        "",
        "The smallest future route that could become testable is:",
        "",
        "1. One raw/signal observation context identified by lineage, source file, record id, and token position.",
        "2. One reviewed receiver/backend/context state connected through DB26/DB27/DB28 mapping and evidence rows.",
        "3. One candidate QM-side or signal-side quantity id in a future side-specific quantity catalog.",
        "4. One candidate ART-side/path/geometry quantity id in a future side-specific quantity catalog.",
        "5. One functional relation expression row with explicit relation type, unit rule, validity domain, and status.",
        "6. One evaluation-plan row with expected-value, observed-value, and delta fields declared but not populated by BRIDGE01.",
        "7. One control/failure-mode field that can mark invalid, missing, confounded, or review-blocked routes.",
        "8. One evidence chain linking raw lineage, mapping decision, external source, and claim boundary.",
        "",
        "## 10. Required controls before any physical analysis",
        "",
        "- Mapping review must identify which token positions can carry which structural roles.",
        "- External evidence gaps must be closed or explicitly marked as blockers.",
        "- Quantity catalogs must separate side-specific candidate fields from generic metadata.",
        "- Units, domains, and value-source rules must be specified before any evaluation values are populated.",
        "- Controls and failure modes must be enumerated before a candidate route is evaluated.",
        "- Raw numeric tokens must remain unresolved unless a reviewed ingest rule exists.",
        "- Claim-boundary status must travel with every relation and evaluation-plan row.",
        "",
        "## 11. What would count as ready for BRIDGE02",
        "",
        "BRIDGE02 readiness would require one auditable route where raw lineage, "
        "mapping status, external evidence status, side-specific quantity ids, "
        "relation-expression status, unit/domain rules, controls, and claim "
        "boundaries are all represented as DB fields. A readiness dashboard may "
        "then show that the question can be asked, while still leaving any "
        "analysis outside BRIDGE01.",
        "",
        "## 12. What must not be claimed at BRIDGE01",
        "",
        CLAIM_BOUNDARY,
        "",
        "BRIDGE01 must not state that a bridge relation has been tested, that "
        "QSB has empirical support from this inventory, that spacetime or "
        "physical emergence has been shown, that Lorentz compatibility has been "
        "established, that global uniqueness or rarity has been established, or "
        "that unresolved TIM columns have final physical meaning.",
        "",
    ]
    return "\n".join(lines)


def write_csv(path: Path, rows: list[dict[str, Any]], fieldnames: list[str]) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow({field: row.get(field, "") for field in fieldnames})


def write_outputs(output_root: Path, data: dict[str, Any]) -> dict[str, Path]:
    paths = output_paths(output_root)
    write_csv(
        paths[AVAILABLE_FIELD_INVENTORY_CSV],
        data["available_field_inventory"],
        [
            "object_type",
            "object_name",
            "column_index",
            "column_name",
            "data_type",
            "notnull",
            "primary_key",
            "foreign_key_refs",
            "conceptual_layer_matches",
            "conceptual_field_matches",
            "availability_role",
            "classifiers",
            "notes",
        ],
    )
    write_csv(
        paths[MISSING_FIELD_GAP_MATRIX_CSV],
        data["missing_field_gap_matrix"],
        [
            "conceptual_layer",
            "conceptual_field",
            "availability_status",
            "classifiers",
            "available_object_count",
            "available_examples",
            "partial_object_count",
            "partial_examples",
            "blocked_by_mapping_gap",
            "blocked_by_external_evidence_gap",
            "requires_new_table",
            "requires_payload_ingest",
            "requires_theory_specification",
            "proposed_location",
            "required_before_bridge02",
            "note",
        ],
    )
    write_csv(
        paths[CANDIDATE_TABLE_DESIGN_CSV],
        data["candidate_table_design"],
        [
            "object_kind",
            "proposed_name",
            "design_group",
            "primary_key_or_join_key",
            "core_fields",
            "required_inputs",
            "bridge02_readiness_role",
            "not_created_reason",
            "claim_boundary",
        ],
    )
    write_csv(
        paths[EXISTING_VIEW_RELEVANCE_CSV],
        data["existing_view_relevance"],
        [
            "object_name",
            "object_type",
            "inspected_reason",
            "row_count_status",
            "row_count",
            "row_count_note",
            "column_count",
            "relevant_layers",
            "relevant_concepts",
            "relevance_class",
            "has_raw_signal_context",
            "has_mapping_context",
            "has_external_evidence_context",
            "has_future_bridge_field_names",
            "notes",
        ],
    )
    paths[REPORT_MD].write_text(build_markdown(data), encoding="utf-8")
    paths[REPORT_JSON].write_text(pretty_json(data) + "\n", encoding="utf-8")
    return paths


def collect_report_data(db_path: Path, output_root: Path) -> dict[str, Any]:
    generated_at = utc_now()
    with connect_read_only(db_path) as con:
        objects, schema_rows, fk_rows = fetch_schema(con)
        available_field_inventory = build_available_field_inventory(schema_rows, fk_rows)
        missing_field_gap_matrix = build_gap_matrix(schema_rows)
        existing_view_relevance = build_view_relevance(con, objects, schema_rows)
        required_presence = required_context_presence(objects, schema_rows, existing_view_relevance)
        fk_check_rows = [dict(row) for row in con.execute("PRAGMA foreign_key_check").fetchall()]

    table_count = sum(1 for obj in objects if obj["type"] == "table")
    view_count = sum(1 for obj in objects if obj["type"] == "view")
    warnings = [
        "BRIDGE01 did not modify the DB.",
        "Future bridge tables and views are specified only; they were not created.",
        "Generic quantity/unit catalogs are partial scaffolding, not side-specific bridge value tables.",
        "Enumeration or replay order from earlier non-BRIDGE runners is not certified by this inventory.",
    ]
    data = {
        "metadata": {
            "script_name": SCRIPT_NAME,
            "generated_at_utc": generated_at,
            "db_path": str(db_path),
            "output_root": str(output_root),
            "operation_mode": "read-only DB inventory plus report/spec generation",
            "data_substrate": "consolidated SQLite DB only",
            "db_modified": "no",
            "table_count": table_count,
            "view_count": view_count,
            "schema_field_count": len(schema_rows),
            "foreign_key_count": len(fk_rows),
            "foreign_key_check_issue_count": len(fk_check_rows),
            "required_context_objects": REQUIRED_CONTEXT_OBJECTS,
            "future_tables_specified_not_created": FUTURE_TABLE_NAMES,
            "future_views_specified_not_created": FUTURE_VIEW_NAMES,
            "claim_boundary": CLAIM_BOUNDARY,
            "warnings": warnings,
        },
        "required_context_presence": required_presence,
        "available_field_inventory": available_field_inventory,
        "missing_field_gap_matrix": missing_field_gap_matrix,
        "candidate_table_design": TABLE_DESIGN_ROWS,
        "existing_view_relevance": existing_view_relevance,
        "gap_status_summary": summarize_gap_status(missing_field_gap_matrix),
        "foreign_key_inventory": fk_rows,
        "foreign_key_check_issues": fk_check_rows,
    }
    data["output_files"] = {name: str(path) for name, path in output_paths(output_root).items()}
    return data


def count_csv_rows(path: Path) -> int:
    with path.open(newline="", encoding="utf-8") as handle:
        reader = csv.reader(handle)
        row_count = sum(1 for _ in reader)
    return max(row_count - 1, 0)


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Create a read-only BRIDGE01 Missing-Link Candidate View specification "
            "from the consolidated QSB research SQLite DB."
        )
    )
    parser.add_argument(
        "--db",
        type=Path,
        default=DEFAULT_DB,
        help=f"Consolidated research DB path. Default: {DEFAULT_DB}",
    )
    parser.add_argument(
        "--output-root",
        type=Path,
        default=DEFAULT_OUTPUT_ROOT,
        help=f"Output directory for BRIDGE01 report files. Default: {DEFAULT_OUTPUT_ROOT}",
    )
    return parser.parse_args(argv)


def main(argv: list[str]) -> int:
    args = parse_args(argv)
    db_path = args.db
    output_root = args.output_root
    ensure_preconditions(db_path, output_root)
    data = collect_report_data(db_path, output_root)
    paths = write_outputs(output_root, data)
    csv_counts = {
        AVAILABLE_FIELD_INVENTORY_CSV: count_csv_rows(paths[AVAILABLE_FIELD_INVENTORY_CSV]),
        MISSING_FIELD_GAP_MATRIX_CSV: count_csv_rows(paths[MISSING_FIELD_GAP_MATRIX_CSV]),
        CANDIDATE_TABLE_DESIGN_CSV: count_csv_rows(paths[CANDIDATE_TABLE_DESIGN_CSV]),
        EXISTING_VIEW_RELEVANCE_CSV: count_csv_rows(paths[EXISTING_VIEW_RELEVANCE_CSV]),
    }
    print("BRIDGE01 Missing-Link Candidate View specification generated.")
    print(f"Data substrate: {db_path}")
    print("DB modified: no")
    print(f"Summary JSON: {paths[REPORT_JSON]}")
    print("Generated CSV row counts:")
    for name, count in csv_counts.items():
        print(f"- {name}: {count}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
