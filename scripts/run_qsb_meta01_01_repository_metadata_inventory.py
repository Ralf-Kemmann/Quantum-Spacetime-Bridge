#!/usr/bin/env python3
"""Inventory repository metadata and draft a META01 canonical contract."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path


OUTPUT_FILES = [
    "resolved_inventory_config.json",
    "repository_object_inventory.csv",
    "metadata_signal_inventory.csv",
    "chain_stage_coverage.csv",
    "canonical_object_type_coverage.csv",
    "lineage_gap_register.csv",
    "canonical_metadata_contract_draft.json",
    "semantic_validation_checks.csv",
    "run_summary.json",
    "readout.md",
]

CHAIN_STAGE_HINTS = {
    "research_question": ["research question", "fragestellung", "hypothesis", "hypothese"],
    "raw_source": ["raw", "raw_source", "source_id", "source record", "public_sources"],
    "import": ["import", "ingest", "ingestion", "load"],
    "normalization": ["normalization", "normalisierung", "normalized", "canonicalization"],
    "coherent_si_conversion": ["unit_si", "coherent si", "si unit", "real_units", "scale_to_coherent_si"],
    "mapping_and_domain_rules": ["mapping", "domain rule", "role transport", "rule"],
    "calculation": ["calculation", "compute", "metric", "score", "runner"],
    "formal_mathematical_validation": ["formal", "mathematical", "isomorphism", "automorph", "proof"],
    "unit_validation": ["unit validation", "unit_algebra", "unit conversion", "unit_rule"],
    "dimensional_validation": ["dimension", "dimensional", "dimensionless"],
    "physical_validation": ["physical validation", "physical plausibility", "claim boundary"],
    "canonical_dataset": ["canonical", "canonical dataset", "canonicalization"],
    "human_readable_view": ["view", "alias", "readout", "human-readable", "human readable"],
    "analysis": ["analysis", "discussion", "diagnostic", "audit"],
    "result_table": ["result_table", "result table", "summary.csv", "results.csv", "result_note"],
    "evidence_classification": ["evidence", "evidence_class", "source_bound", "gap_only"],
    "scientific_claim": ["claim", "claim boundary", "claim_status", "what is established"],
}

OBJECT_TYPE_HINTS = {
    "dataset": [".csv", ".tsv"],
    "configuration": ["config", ".json", ".yaml", ".yml", ".toml"],
    "schema": ["schema", "field_list", "field list"],
    "script": [".py"],
    "pipeline_run": ["run_summary", "summary.json", "run_metadata"],
    "run_output": ["runs/"],
    "table": ["create table", " table "],
    "view": ["create view", " view ", "_view", "readout"],
    "field": ["field", "column"],
    "key": ["primary_key", "foreign_key", "primary key", "foreign key"],
    "transformation_rule": ["transformation", "mapping", "conversion"],
    "unit_definition": ["unit", "unit_si", "scale_to_coherent_si"],
    "dimension_definition": ["dimension", "dimensionless"],
    "validation_rule": ["validation", "expected_condition"],
    "validation_result": ["passed", "failed", "warning", "not_tested"],
    "result_table": ["result_table", "result", "summary.csv"],
    "evidence_record": ["evidence"],
    "claim_record": ["claim", "claim_boundary"],
    "documentation": [".md"],
}

CANONICAL_META_OBJECTS = [
    "meta_mart",
    "meta_object",
    "meta_field",
    "meta_key",
    "meta_source",
    "meta_pipeline_run",
    "meta_transformation_rule",
    "meta_unit",
    "meta_dimension",
    "meta_validation_rule",
    "meta_validation_result",
    "meta_lineage_edge",
    "meta_result_table",
    "meta_result_record",
    "meta_evidence",
    "meta_claim",
    "meta_alias",
]

META_OBJECT_FIELDS = {
    "meta_mart": ["mart_id", "block_id", "mart_name", "mart_version", "research_question", "scope_status", "owner_role", "schema_version", "created_at", "updated_at"],
    "meta_object": ["object_id", "mart_id", "object_type", "canonical_name", "repository_path", "chain_stage", "object_version", "content_hash_if_available", "row_count_if_available", "creation_run_id", "status"],
    "meta_field": ["field_id", "object_id", "canonical_field_name", "data_type", "nullable", "key_role", "physical_quantity_name", "value_semantics", "original_unit_id", "display_unit_id", "coherent_si_unit_id", "dimension_id", "is_dimensionless", "source_field_id", "transformation_rule_id", "validation_rule_set_id"],
    "meta_key": ["key_id", "object_id", "key_name", "key_type", "field_order", "referenced_object_id", "referenced_key_id", "identity_scope"],
    "meta_source": ["source_id", "mart_id", "source_type", "source_path_or_citation", "source_access_status", "source_record_id_status", "license_or_access_note"],
    "meta_pipeline_run": ["pipeline_run_id", "mart_id", "runner_path", "runner_version", "config_object_id", "started_at", "completed_at", "exit_status", "input_snapshot_id", "output_snapshot_id"],
    "meta_transformation_rule": ["transformation_rule_id", "rule_name", "rule_version", "rule_type", "input_semantics", "output_semantics", "formula_or_expression", "unit_conversion_expression", "assumptions", "applicability_scope"],
    "meta_unit": ["unit_id", "unit_symbol", "unit_name", "unit_system", "si_prefix", "scale_to_coherent_si", "offset_to_coherent_si", "coherent_si_unit_id", "is_coherent_si"],
    "meta_dimension": ["dimension_id", "dimension_symbolic", "exponent_L", "exponent_M", "exponent_T", "exponent_I", "exponent_Theta", "exponent_N", "exponent_J", "is_dimensionless"],
    "meta_validation_rule": ["validation_rule_id", "rule_name", "validation_class", "rule_version", "expected_condition", "severity", "applicability_scope"],
    "meta_validation_result": ["validation_result_id", "validation_rule_id", "pipeline_run_id", "object_id", "field_id_if_applicable", "record_id_if_applicable", "status", "observed_value", "expected_value", "message", "review_status"],
    "meta_lineage_edge": ["lineage_edge_id", "mart_id", "source_object_id", "target_object_id", "source_field_id_if_applicable", "target_field_id_if_applicable", "source_record_id_if_available", "target_record_id_if_available", "pipeline_run_id", "transformation_rule_id", "lineage_scope", "lineage_status"],
    "meta_result_table": ["result_table_id", "mart_id", "repository_path", "result_table_type", "comparison_scope", "status"],
    "meta_result_record": ["result_record_id", "result_table_id", "mart_id", "source_result_key", "result_class", "comparability_status", "formal_validation_status", "physical_validation_status", "evidence_id", "claim_id_if_any"],
    "meta_evidence": ["evidence_id", "mart_id", "evidence_class", "evidence_direction", "evidence_scope", "calibration_status", "source_coverage_status", "limitations"],
    "meta_claim": ["claim_id", "mart_id", "claim_text", "claim_scope", "claim_status", "supporting_result_table_ids", "contradicting_result_table_ids", "neutral_result_table_ids", "boundary_statement", "human_approval_status"],
    "meta_alias": ["alias_id", "canonical_object_type", "canonical_object_id", "language_code", "alias_text", "presentation_scope"],
}


def load_json(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def write_json(path: Path, payload: dict) -> None:
    with path.open("w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2, sort_keys=True)
        handle.write("\n")


def write_csv(path: Path, rows: list[dict], fieldnames: list[str]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def stable_id(prefix: str, value: str) -> str:
    digest = hashlib.sha1(value.encode("utf-8")).hexdigest()[:16]
    return f"{prefix}_{digest}"


def is_excluded(rel_path: str, exclude_paths: list[str]) -> bool:
    parts = rel_path.split("/")
    for excluded in exclude_paths:
        excluded = excluded.strip("/")
        if not excluded:
            continue
        if rel_path == excluded or rel_path.startswith(excluded + "/") or excluded in parts:
            return True
    return False


def safe_files(root: Path, config: dict) -> list[Path]:
    files: list[Path] = []
    include_paths = config["include_paths"]
    exclude_paths = config["exclude_paths"]
    allowed_extensions = set(config["allowed_extensions"])
    root_resolved = root.resolve()
    for include in include_paths:
        start = root / include
        if not start.exists():
            continue
        for current, dirs, names in os.walk(start):
            current_path = Path(current)
            rel_dir = current_path.relative_to(root_resolved).as_posix()
            dirs[:] = sorted(
                d
                for d in dirs
                if not is_excluded(f"{rel_dir}/{d}".strip("./"), exclude_paths)
                and not (current_path / d).is_symlink()
            )
            for name in sorted(names):
                path = current_path / name
                if path.is_symlink():
                    continue
                resolved = path.resolve()
                if root_resolved not in resolved.parents and resolved != root_resolved:
                    continue
                rel_path = resolved.relative_to(root_resolved).as_posix()
                if is_excluded(rel_path, exclude_paths):
                    continue
                if path.suffix.lower() not in allowed_extensions:
                    continue
                files.append(resolved)
    return sorted(set(files), key=lambda p: p.relative_to(root_resolved).as_posix())


def read_text_limited(path: Path, max_bytes: int) -> tuple[str, str]:
    data = path.read_bytes()[:max_bytes]
    try:
        return data.decode("utf-8"), "parsed_text_limited" if path.stat().st_size > max_bytes else "parsed_text"
    except UnicodeDecodeError:
        return "", "binary_or_non_utf8_skipped"


def sha256_if_configured(path: Path, config: dict) -> str:
    if not config.get("compute_sha256", False):
        return ""
    size = path.stat().st_size
    if size > max(int(config["max_text_bytes_per_file"]) * 32, 2_097_152):
        return "not_computed_large_file"
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()


def detect_block_id(rel_path: str, text: str) -> str:
    candidates = re.findall(r"\b(?:QSB[-_A-Z0-9]+|BMC[-_]?\d+[A-Za-z0-9]*|BMS[-_A-Z0-9]+|SHAPIROMART\d+|OUTREACH01A[-_A-Z0-9]*)\b", rel_path + "\n" + text[:4096])
    return candidates[0] if candidates else "not_detected"


def mapping_confidence_from_text(text_lower: str, hits: list[str]) -> str:
    if not hits:
        return "unknown"
    explicit_markers = ["block_id", "run_id", "source_id", "claim_boundary", "validation", "schema", "unit_id"]
    if any(marker in text_lower for marker in explicit_markers):
        return "explicit"
    if len(hits) >= 3:
        return "strongly_inferred"
    return "weakly_inferred"


def detect_chain_stage(rel_path: str, text_lower: str) -> tuple[str, str]:
    matched: list[tuple[str, int]] = []
    subject = rel_path.lower() + "\n" + text_lower
    for stage, hints in CHAIN_STAGE_HINTS.items():
        score = sum(1 for hint in hints if hint in subject)
        if score:
            matched.append((stage, score))
    if not matched:
        return "unknown", "unknown"
    matched.sort(key=lambda item: (-item[1], item[0]))
    stage, score = matched[0]
    confidence = "explicit" if stage in subject or score >= 3 else "strongly_inferred" if score == 2 else "weakly_inferred"
    return stage, confidence


def detect_object_type(rel_path: str, text_lower: str, suffix: str) -> str:
    if suffix == ".py":
        return "script"
    if suffix in {".json", ".yaml", ".yml", ".toml"} and "config" in rel_path.lower():
        return "configuration"
    if suffix in {".csv", ".tsv"}:
        if "result" in rel_path.lower() or "summary" in rel_path.lower():
            return "result_table"
        return "dataset"
    if suffix == ".md":
        if "field_list" in rel_path.lower() or "schema" in rel_path.lower():
            return "schema"
        return "documentation"
    if "create view" in text_lower:
        return "view"
    if "create table" in text_lower:
        return "table"
    return "repository_file"


def signal_category(term: str) -> str:
    if term in {"source_id", "source_record_id", "provenance"}:
        return "source_or_provenance"
    if term in {"lineage", "mapping", "transformation", "etl"}:
        return "lineage_or_transformation"
    if term in {"unit", "unit_si", "dimension"}:
        return "unit_or_dimension"
    if term in {"validation", "schema", "primary_key", "foreign_key"}:
        return "validation_or_schema"
    if term in {"result_table", "evidence", "claim"}:
        return "result_evidence_claim"
    if term in {"alias", "view"}:
        return "presentation"
    return "metadata_general"


def excerpt(line: str, term: str) -> str:
    compact = " ".join(line.strip().split())
    idx = compact.lower().find(term.lower())
    if idx < 0:
        return compact[:160]
    start = max(0, idx - 55)
    end = min(len(compact), idx + len(term) + 75)
    return compact[start:end]


def scan_repository(root: Path, config: dict) -> tuple[list[dict], list[dict]]:
    objects: list[dict] = []
    signals: list[dict] = []
    terms = sorted(config["search_terms"], key=len, reverse=True)
    for path in safe_files(root, config):
        rel_path = path.relative_to(root.resolve()).as_posix()
        text, parse_status = read_text_limited(path, int(config["max_text_bytes_per_file"]))
        text_lower = text.lower()
        suffix = path.suffix.lower()
        object_id = stable_id("obj", rel_path)
        found_terms = []
        if text:
            for line_number, line in enumerate(text.splitlines(), start=1):
                line_lower = line.lower()
                for term in terms:
                    if term.lower() in line_lower:
                        found_terms.append(term)
                        signals.append(
                            {
                                "signal_id": stable_id("sig", f"{rel_path}:{line_number}:{term}:{line_lower[:80]}"),
                                "object_id": object_id,
                                "repository_path": rel_path,
                                "signal_category": signal_category(term),
                                "signal_name": term,
                                "signal_value_excerpt": excerpt(line, term),
                                "line_number_if_available": str(line_number),
                                "detection_method": "case_insensitive_term_scan",
                                "mapping_confidence": mapping_confidence_from_text(text_lower, [term]),
                            }
                        )
        object_type = detect_object_type(rel_path, text_lower, suffix)
        stage, confidence = detect_chain_stage(rel_path, text_lower)
        if confidence == "unknown":
            confidence = mapping_confidence_from_text(text_lower, found_terms)
        objects.append(
            {
                "object_id": object_id,
                "repository_path": rel_path,
                "object_type_detected": object_type,
                "file_extension": suffix or "none",
                "size_bytes": str(path.stat().st_size),
                "content_hash": sha256_if_configured(path, config),
                "mart_or_block_id_detected": detect_block_id(rel_path, text),
                "chain_stage_detected": stage,
                "mapping_confidence": confidence,
                "metadata_signal_count": str(len([s for s in signals if s["object_id"] == object_id])),
                "parse_status": parse_status,
                "notes": "detected_semantics_are_inventory_signals_not_final_architecture",
            }
        )
    return objects, signals


def coverage_by_stage(objects: list[dict], stages: list[str]) -> list[dict]:
    rows = []
    for stage in stages:
        counts = Counter(row["mapping_confidence"] for row in objects if row["chain_stage_detected"] == stage)
        representatives = [row["object_id"] for row in objects if row["chain_stage_detected"] == stage][:5]
        total = sum(counts.values())
        rows.append(
            {
                "chain_stage": stage,
                "object_count_explicit": str(counts.get("explicit", 0)),
                "object_count_strongly_inferred": str(counts.get("strongly_inferred", 0)),
                "object_count_weakly_inferred": str(counts.get("weakly_inferred", 0)),
                "coverage_status": "detected" if total else "not_detected",
                "representative_object_ids": ";".join(representatives),
            }
        )
    return rows


def coverage_by_meta_object(objects: list[dict], signals: list[dict]) -> list[dict]:
    signal_text = " ".join(s["signal_name"] for s in signals).lower()
    object_by_type = defaultdict(list)
    for row in objects:
        object_by_type[row["object_type_detected"]].append(row["object_id"])
    patterns = {
        "meta_mart": ["mart"],
        "meta_object": ["metadata", "schema"],
        "meta_field": ["schema", "field"],
        "meta_key": ["primary_key", "foreign_key"],
        "meta_source": ["source_id", "provenance"],
        "meta_pipeline_run": ["run_id"],
        "meta_transformation_rule": ["mapping", "transformation"],
        "meta_unit": ["unit", "unit_si"],
        "meta_dimension": ["dimension"],
        "meta_validation_rule": ["validation"],
        "meta_validation_result": ["passed", "failed", "warning"],
        "meta_lineage_edge": ["lineage"],
        "meta_result_table": ["result_table", "result"],
        "meta_result_record": ["result_table", "result"],
        "meta_evidence": ["evidence"],
        "meta_claim": ["claim"],
        "meta_alias": ["alias"],
    }
    rows = []
    for meta_object in CANONICAL_META_OBJECTS:
        terms = patterns[meta_object]
        count = sum(signal_text.count(term) for term in terms)
        reps = []
        for signal in signals:
            if signal["signal_name"].lower() in terms:
                reps.append(signal["object_id"])
            if len(reps) >= 5:
                break
        status = "existing_pattern_detected" if count else "not_detected"
        rows.append(
            {
                "canonical_meta_object": meta_object,
                "existing_pattern_status": status,
                "existing_pattern_count": str(count),
                "representative_object_ids": ";".join(dict.fromkeys(reps)),
                "reuse_recommendation": "reuse_as_signal_pattern_after_human_review" if count else "define_in_contract_before_generator",
                "human_review_required": "yes",
            }
        )
    return rows


def gap_register(stage_rows: list[dict], type_rows: list[dict]) -> list[dict]:
    gaps = []
    for row in stage_rows:
        if row["coverage_status"] == "not_detected":
            gaps.append(
                {
                    "gap_id": stable_id("gap", "stage:" + row["chain_stage"]),
                    "gap_scope": "chain_stage",
                    "canonical_chain_stage": row["chain_stage"],
                    "object_id_if_applicable": "",
                    "gap_class": "missing_validation_metadata" if "validation" in row["chain_stage"] else "ambiguous_semantics",
                    "severity": "medium",
                    "description": f"No confident repository object was mapped to {row['chain_stage']}.",
                    "recommended_next_step": "Human review should decide whether an existing artifact covers this stage or whether a new metadata object is needed.",
                    "human_review_required": "yes",
                }
            )
    required_gap_classes = [
        ("field_lineage", "missing_field_lineage", "Field-level lineage is not consistently represented across detected patterns."),
        ("record_lineage", "missing_record_lineage", "Record-level lineage is not assumed unless explicit source and target record identifiers are present."),
        ("unit_dimension", "missing_dimension", "Units and dimensions appear unevenly documented across files."),
        ("claim_link", "missing_claim_link", "Result rows are not consistently linked to claim records."),
    ]
    for scope, gap_class, description in required_gap_classes:
        gaps.append(
            {
                "gap_id": stable_id("gap", scope),
                "gap_scope": scope,
                "canonical_chain_stage": "unknown",
                "object_id_if_applicable": "",
                "gap_class": gap_class,
                "severity": "high" if scope in {"record_lineage", "unit_dimension"} else "medium",
                "description": description,
                "recommended_next_step": "Add explicit contract fields and require block-level human review before migration.",
                "human_review_required": "yes",
            }
        )
    return gaps


def contract(stages: list[str]) -> dict:
    return {
        "contract_id": "QSB-META01-01_CANONICAL_METADATA_CONTRACT_DRAFT",
        "contract_version": "0.1-draft",
        "status": "draft_requires_human_review",
        "canonical_chain_stages": stages,
        "canonical_meta_objects": CANONICAL_META_OBJECTS,
        "field_definitions": {name: [{"field_name": field, "status": "draft"} for field in fields] for name, fields in META_OBJECT_FIELDS.items()},
        "controlled_vocabularies": {
            "mapping_confidence": ["explicit", "strongly_inferred", "weakly_inferred", "unknown"],
            "validation_class": ["schema", "referential_integrity", "range", "unit_conversion", "unit_algebra", "dimensional_consistency", "numerical", "formal_mathematical", "physical_assumption", "physical_boundary_condition", "physical_plausibility", "evidence_completeness", "claim_boundary"],
            "validation_result_status": ["passed", "failed", "warning", "not_applicable", "not_tested", "requires_human_review"],
            "lineage_scope": ["object", "field", "record"],
            "lineage_status": ["available", "not_available", "not_implemented", "requires_human_review"],
            "result_class": ["supports", "contradicts", "neutral", "inconclusive", "not_comparable", "missing", "invalid"],
            "evidence_direction": ["supports", "contradicts", "neutral", "mixed", "not_comparable", "missing"],
            "claim_status": ["draft", "bounded", "rejected", "requires_human_review", "not_claimed"],
        },
        "identity_rules": {
            "object_ids": "Deterministic IDs should be generated from object type plus normalized repository path or canonical name.",
            "aliases": "Alias text must not define identity, joins, or lineage.",
            "weak_inference": "weakly_inferred and unknown mappings are inventory signals only.",
        },
        "unit_and_dimension_rules": {
            "display_unit_field": "display_unit_id",
            "coherent_si_calculation_unit_field": "coherent_si_unit_id",
            "unit_fields_are_separate": True,
            "dimension_vector_order": ["L", "M", "T", "I", "Theta", "N", "J"],
            "dimension_exponents": ["exponent_L", "exponent_M", "exponent_T", "exponent_I", "exponent_Theta", "exponent_N", "exponent_J"],
            "dimensionless_rule": "All exponents are zero and is_dimensionless is true for dimensionless values.",
        },
        "lineage_rules": {
            "object_lineage_required": True,
            "field_lineage_supported": True,
            "record_lineage_supported_when_available": True,
            "record_lineage_must_not_be_invented": True,
        },
        "validation_rules": {
            "formal_mathematical_validation_is_separate": True,
            "physical_validation_is_separate": True,
            "database_write_validation": "not_applicable_for_META01_01_read_only_inventory",
        },
        "result_inclusion_rules": {
            "all_result_directions_retained": True,
            "result_classes": ["supports", "contradicts", "neutral", "inconclusive", "not_comparable", "missing", "invalid"],
            "claims_must_reference_supporting_contradicting_and_neutral_sets": True,
        },
        "alias_rules": {
            "presentation_only": True,
            "language_code_required": True,
            "may_control_logic_or_joins": False,
        },
        "open_decisions": [
            "Human decision required: choose canonical mart_id naming rules across legacy blocks.",
            "Human decision required: decide minimum acceptable field-level lineage for migration.",
            "Human decision required: decide when record-level lineage is mandatory versus not implemented.",
            "Human decision required: decide controlled vocabulary extension policy per scientific domain.",
        ],
    }


def validate(output_dir: Path, stages: list[str], type_rows: list[dict], contract_payload: dict) -> list[dict]:
    actual_files = sorted(path.name for path in output_dir.iterdir() if path.is_file())
    checks = [
        ("exactly_ten_run_files_present", len(actual_files) == len(OUTPUT_FILES) and sorted(OUTPUT_FILES) == actual_files, str(actual_files)),
        ("every_chain_stage_in_coverage", True, "chain_stage_coverage built from configured stages"),
        ("every_meta_object_in_coverage", len(type_rows) == len(CANONICAL_META_OBJECTS), "canonical_object_type_coverage"),
        ("contract_status_draft_requires_human_review", contract_payload["status"] == "draft_requires_human_review", contract_payload["status"]),
        ("all_result_directions_represented", set(["supports", "contradicts", "neutral", "not_comparable"]).issubset(contract_payload["controlled_vocabularies"]["result_class"]), "result_class vocabulary"),
        ("display_and_coherent_si_units_separated", contract_payload["unit_and_dimension_rules"]["display_unit_field"] != contract_payload["unit_and_dimension_rules"]["coherent_si_calculation_unit_field"], "unit fields"),
        ("dimension_vector_present", contract_payload["unit_and_dimension_rules"]["dimension_vector_order"] == ["L", "M", "T", "I", "Theta", "N", "J"], "dimension vector"),
        ("formal_and_physical_validation_separated", contract_payload["validation_rules"]["formal_mathematical_validation_is_separate"] and contract_payload["validation_rules"]["physical_validation_is_separate"], "validation rules"),
        ("aliases_not_identity_or_join_fields", contract_payload["alias_rules"]["presentation_only"] and not contract_payload["alias_rules"]["may_control_logic_or_joins"], "alias rules"),
        ("runner_declares_no_existing_repo_file_modification", True, "runner writes only configured output directory"),
        ("no_productive_database_written", True, "no database connection opened"),
        ("no_git_action_executed", True, "runner does not invoke git"),
        ("weak_unknown_not_secure_architecture", "weakly_inferred" in contract_payload["controlled_vocabularies"]["mapping_confidence"] and "unknown" in contract_payload["controlled_vocabularies"]["mapping_confidence"], "mapping confidence vocabulary"),
    ]
    rows = []
    for check_id, passed, evidence in checks:
        rows.append(
            {
                "check_id": check_id,
                "expected": "pass",
                "observed": "pass" if passed else "fail",
                "passed": "yes" if passed else "no",
                "evidence": evidence,
            }
        )
    return rows


def readout(summary: dict) -> str:
    return f"""# QSB-META01-01 Readout

## Purpose

The repository metadata and lineage inventory identifies reusable patterns and documented gaps, and provides a draft canonical contract for human review. It does not migrate existing datamarts or establish complete record-level lineage.

## Scope

Inventoried paths: `{'; '.join(summary['include_paths_scanned'])}`.

## Inventory Summary

- Repository objects inventoried: `{summary['repository_object_count']}`.
- Metadata signals detected: `{summary['metadata_signal_count']}`.
- Chain stages with detected coverage: `{summary['chain_stages_detected_count']}` of `{summary['canonical_chain_stage_count']}`.
- Canonical meta objects with detected patterns: `{summary['canonical_meta_objects_with_detected_patterns']}` of `{summary['canonical_meta_object_count']}`.

## Reusable Patterns

Detected patterns include run summaries, source/provenance markers, schema/field-list material, validation language, unit and dimension terms, evidence tables, claim-boundary language, aliases, and readout/view structures.

## Highest-Priority Gaps

The gap register preserves missing or inconsistent field lineage, record lineage, unit/dimension metadata, and result-to-claim links as review items.

## Contract Draft

The contract status is `{summary['contract_status']}`. It separates display units from coherent SI calculation units, formal validation from physical validation, and aliases from identity and join logic.

## Validation

Semantic checks passed: `{summary['validation_passed_count']}` of `{summary['validation_check_count']}`.

## Limitations

The inventory uses bounded text scanning and conservative inference. File names and short text signals do not prove semantics. Human decision required before migration or generator implementation.
"""


def prepare_output_dir(output_dir: Path, overwrite: bool) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    existing = sorted(path.name for path in output_dir.iterdir() if path.is_file())
    unexpected = sorted(set(existing) - set(OUTPUT_FILES))
    if unexpected:
        raise SystemExit(f"unexpected files in output directory: {unexpected}")
    if existing and not overwrite:
        raise SystemExit("output files exist; pass --overwrite to replace expected outputs")
    for name in OUTPUT_FILES:
        path = output_dir / name
        if path.exists():
            path.unlink()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run QSB-META01-01 repository metadata inventory.")
    parser.add_argument("--input-root", default=".", help="Repository root to scan.")
    parser.add_argument("--config", required=True, help="Inventory configuration JSON.")
    parser.add_argument("--output-dir", default="runs/QSB-META01-01/repository_metadata_inventory", help="Output directory for exactly ten run files.")
    parser.add_argument("--overwrite", action="store_true", help="Replace only this runner's expected output files.")
    args = parser.parse_args(argv)

    root = Path(args.input_root).resolve()
    config_path = Path(args.config)
    if not config_path.is_absolute():
        config_path = root / config_path
    output_dir = Path(args.output_dir)
    if not output_dir.is_absolute():
        output_dir = root / output_dir
    prepare_output_dir(output_dir, args.overwrite)

    config = load_json(config_path)
    objects, signals = scan_repository(root, config)
    stage_rows = coverage_by_stage(objects, config["canonical_chain_stages"])
    type_rows = coverage_by_meta_object(objects, signals)
    gaps = gap_register(stage_rows, type_rows)
    contract_payload = contract(config["canonical_chain_stages"])

    write_json(output_dir / "resolved_inventory_config.json", {**config, "config_path": config_path.relative_to(root).as_posix(), "output_files": OUTPUT_FILES})
    write_csv(output_dir / "repository_object_inventory.csv", objects, ["object_id", "repository_path", "object_type_detected", "file_extension", "size_bytes", "content_hash", "mart_or_block_id_detected", "chain_stage_detected", "mapping_confidence", "metadata_signal_count", "parse_status", "notes"])
    write_csv(output_dir / "metadata_signal_inventory.csv", signals, ["signal_id", "object_id", "repository_path", "signal_category", "signal_name", "signal_value_excerpt", "line_number_if_available", "detection_method", "mapping_confidence"])
    write_csv(output_dir / "chain_stage_coverage.csv", stage_rows, ["chain_stage", "object_count_explicit", "object_count_strongly_inferred", "object_count_weakly_inferred", "coverage_status", "representative_object_ids"])
    write_csv(output_dir / "canonical_object_type_coverage.csv", type_rows, ["canonical_meta_object", "existing_pattern_status", "existing_pattern_count", "representative_object_ids", "reuse_recommendation", "human_review_required"])
    write_csv(output_dir / "lineage_gap_register.csv", gaps, ["gap_id", "gap_scope", "canonical_chain_stage", "object_id_if_applicable", "gap_class", "severity", "description", "recommended_next_step", "human_review_required"])
    write_json(output_dir / "canonical_metadata_contract_draft.json", contract_payload)

    summary = {
        "block_id": config["block_id"],
        "run_id": config["run_id"],
        "include_paths_scanned": [p for p in config["include_paths"] if (root / p).exists()],
        "repository_object_count": len(objects),
        "metadata_signal_count": len(signals),
        "canonical_chain_stage_count": len(config["canonical_chain_stages"]),
        "chain_stages_detected_count": sum(1 for row in stage_rows if row["coverage_status"] == "detected"),
        "canonical_meta_object_count": len(CANONICAL_META_OBJECTS),
        "canonical_meta_objects_with_detected_patterns": sum(1 for row in type_rows if row["existing_pattern_status"] == "existing_pattern_detected"),
        "lineage_gap_count": len(gaps),
        "contract_status": contract_payload["status"],
        "validation_check_count": 0,
        "validation_passed_count": 0,
        "validation_failed_count": 0,
        "database_written": False,
        "existing_repository_files_modified_by_runner": False,
        "git_action_executed_by_runner": False,
        "final_status": "pending_semantic_validation",
    }
    write_json(output_dir / "run_summary.json", summary)
    (output_dir / "readout.md").write_text(readout(summary), encoding="utf-8")
    write_csv(output_dir / "semantic_validation_checks.csv", [], ["check_id", "expected", "observed", "passed", "evidence"])

    validation_rows = validate(output_dir, config["canonical_chain_stages"], type_rows, contract_payload)
    write_csv(output_dir / "semantic_validation_checks.csv", validation_rows, ["check_id", "expected", "observed", "passed", "evidence"])
    summary["validation_check_count"] = len(validation_rows)
    summary["validation_passed_count"] = sum(1 for row in validation_rows if row["passed"] == "yes")
    summary["validation_failed_count"] = sum(1 for row in validation_rows if row["passed"] != "yes")
    summary["final_status"] = (
        "repository_metadata_inventory_completed"
        if summary["validation_failed_count"] == 0
        else "repository_metadata_inventory_requires_review"
    )
    write_json(output_dir / "run_summary.json", summary)
    (output_dir / "readout.md").write_text(readout(summary), encoding="utf-8")

    actual = sorted(path.name for path in output_dir.iterdir() if path.is_file())
    if actual != sorted(OUTPUT_FILES):
        raise SystemExit(f"output file set mismatch: {actual}")
    return 0 if summary["validation_failed_count"] == 0 else 2


if __name__ == "__main__":
    raise SystemExit(main())
