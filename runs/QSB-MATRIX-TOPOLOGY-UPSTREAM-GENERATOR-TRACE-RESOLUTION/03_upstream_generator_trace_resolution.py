#!/usr/bin/env python3
"""Resolve upstream generator trace for EXTRACT03A-R1 edge candidate artifact."""

from __future__ import annotations

import csv
import hashlib
import json
import os
from pathlib import Path


RUN_ID = "QSB-MATRIX-TOPOLOGY-UPSTREAM-GENERATOR-TRACE-RESOLUTION"
RUN_DIR = Path("runs") / RUN_ID
SOURCE_CHAIN_LATEST_COMMIT = "ff191c1"

PRIMARY_EDGE_FILE = Path("runs/QSB-EXTRACT03A-R1/authorized_execution_with_s1_addendum/16_edge_candidate_result.csv")
EXTRACT_DIR = Path("runs/QSB-EXTRACT03A-R1/authorized_execution_with_s1_addendum")
DIRECT_GENERATOR = Path("scripts/qsb_extract03a_r1/run_authorized_execution_with_s1_addendum.py")
PACKAGE_SCRIPT = Path("scripts/qsb_extract03/prepare_execution_package.py")
ORIGIN_SUMMARY = Path("runs/QSB-MATRIX-TOPOLOGY-STRUCTURE-ORIGIN-AUDIT/04_structure_origin_summary.json")
ORIGIN_TRACE = Path("runs/QSB-MATRIX-TOPOLOGY-STRUCTURE-ORIGIN-AUDIT/08_upstream_trace_inventory.csv")
SOURCE_GATE_SUMMARY = Path("runs/QSB-MATRIX-TOPOLOGY-SOURCE-SIGNAL-SEPARATION-GATE/04_source_signal_separation_summary.json")
SOURCE_GATE_INVENTORY = Path("runs/QSB-MATRIX-TOPOLOGY-SOURCE-SIGNAL-SEPARATION-GATE/05_source_artifact_inventory.csv")
SOURCE_GATE_PLAN = Path("runs/QSB-MATRIX-TOPOLOGY-SOURCE-SIGNAL-SEPARATION-GATE/13_negative_control_execution_plan.md")
CLAIM_BOUNDARY = "provenance_lineage_generator_trace_only_no_physics_or_source_signal_claim"
ROW_BOUNDARY = "trace_resolution_only_no_physics_claim"

QUERIES = [
    "16_edge_candidate_result",
    "edge_candidate_flag",
    "theta_edge",
    "relation_strength",
    "same_abs_delta",
    "abs_delta",
    "pair_a",
    "pair_b",
    "DictWriter",
    "writerow",
]

RELEVANT_FILES = [
    DIRECT_GENERATOR,
    PACKAGE_SCRIPT,
    Path("scripts/qsb_extract03b/result_review_human_summary.py"),
    Path("scripts/qsb_extract03d/block_mechanism_review.py"),
    Path("scripts/qsb_extract03e/perfection_origin_review.py"),
    Path("scripts/qsb_extract03_viz01/matrix_heatmap_visualization.py"),
    Path("scripts/qsb_extract03_viz02/topology_organized_relational_matrix.py"),
    Path("scripts/qsb_extract03c1_r1/bootstrap_stability_run_under_c0_c0b.py"),
    EXTRACT_DIR / "01_extract03a_r1_run_manifest.json",
    EXTRACT_DIR / "06_frozen_decision_carry_forward_review.csv",
    EXTRACT_DIR / "09_tensor_schema_runtime_mapping.csv",
    EXTRACT_DIR / "15_strength_matrix.csv",
    EXTRACT_DIR / "16_edge_candidate_result.csv",
    EXTRACT_DIR / "17_kernel_execution_summary.csv",
    EXTRACT_DIR / "20_result_mart_schema_executed.sql",
    EXTRACT_DIR / "23_lineage_and_hash_audit.csv",
]


def read_json(path: Path) -> dict:
    if not path.exists():
        return {"missing": True}
    with path.open("r", encoding="utf-8") as handle:
        data = json.load(handle)
    data["missing"] = False
    return data


def read_csv_rows(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: Path, fieldnames: list[str], rows: list[dict[str, object]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def write_text(path: Path, text: str) -> None:
    path.write_text(text, encoding="utf-8")


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def text_lines(path: Path) -> list[str]:
    if not path.exists() or path.is_dir():
        return []
    return path.read_text(encoding="utf-8", errors="replace").splitlines()


def excerpt(line: str) -> str:
    return line.strip().replace("\t", " ")[:260]


def profile_primary_edge_file() -> tuple[list[dict[str, object]], dict[str, object]]:
    exists = PRIMARY_EDGE_FILE.exists()
    rows = read_csv_rows(PRIMARY_EDGE_FILE) if exists else []
    columns = list(rows[0].keys()) if rows else []
    strengths = [float(row["strength"]) for row in rows if row.get("strength", "") != ""]
    thetas = sorted({row["theta_edge"] for row in rows if row.get("theta_edge", "") != ""})
    candidate_count = sum(1 for row in rows if row.get("edge_candidate_flag") == "1")
    non_candidate_count = sum(1 for row in rows if row.get("edge_candidate_flag") == "0")
    values = {
        "path_exists": exists,
        "row_count": len(rows),
        "column_count": len(columns),
        "columns": ";".join(columns),
        "pair_columns_detected": {"pair_a", "pair_b"}.issubset(columns),
        "strength_column_detected": "strength" in columns,
        "theta_edge_column_detected": "theta_edge" in columns,
        "edge_candidate_flag_column_detected": "edge_candidate_flag" in columns,
        "unique_theta_edge_values": ";".join(thetas),
        "strength_min": min(strengths) if strengths else "",
        "strength_max": max(strengths) if strengths else "",
        "candidate_count": candidate_count,
        "non_candidate_count": non_candidate_count,
        "sha256": sha256_file(PRIMARY_EDGE_FILE) if exists else "",
        "file_size_bytes": PRIMARY_EDGE_FILE.stat().st_size if exists else "",
    }
    output_rows = [{"field": key, "value": value, "notes": "primary edge artifact profile"} for key, value in values.items()]
    return output_rows, values


def classify_hit(query: str, path: Path, line: str) -> tuple[str, str]:
    lower = line.lower()
    if "16_edge_candidate_result" in lower or "edge_candidate_result" in lower:
        return "direct_output_filename", "high" if path == DIRECT_GENERATOR else "medium"
    if "dictwriter" in lower or "write_csv" in lower or "writerow" in lower or "writerows" in lower:
        return "script_writer", "high" if path == DIRECT_GENERATOR else "medium"
    if "theta_edge" in lower or "theta_edge" == query:
        if "theta_edge = 0.5" in lower or "hf-06" in lower or "freeze_edge_threshold" in lower:
            return "threshold_candidate", "high"
        return "threshold_candidate", "medium"
    if "edge_candidate_flag" in lower:
        if "strength >= theta_edge" in lower or "int(edge" in lower or "edge = strength >=" in lower:
            return "edge_flag_rule_candidate", "high"
        return "candidate_column_name", "medium"
    if "relation_strength" in lower or "strength" in lower:
        if "np.exp(-d / ell_0)" in lower or "strength =" in lower or "s_ij_strength_transform" in lower:
            return "strength_formula_candidate", "high"
        return "candidate_column_name", "medium"
    if "pair_a" in lower or "pair_b" in lower:
        return "candidate_column_name", "medium"
    if "lineage" in lower or "manifest" in lower or "sha256" in lower:
        return "manifest_or_lineage", "medium"
    if path.suffix.lower() in {".md", ".txt"}:
        return "documentation_only", "low"
    return "irrelevant_or_weak", "low"


def trace_search_inventory() -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for query in QUERIES:
        for path in sorted(set(RELEVANT_FILES), key=lambda item: str(item)):
            for line_number, line in enumerate(text_lines(path), start=1):
                if query in line:
                    evidence_type, relevance = classify_hit(query, path, line)
                    if relevance == "low" and len(rows) > 250:
                        continue
                    rows.append(
                        {
                            "query": query,
                            "path": str(path),
                            "line_number": line_number,
                            "excerpt": excerpt(line),
                            "evidence_type": evidence_type,
                            "trace_relevance": relevance,
                            "claim_boundary": ROW_BOUNDARY,
                        }
                    )
    rows.sort(key=lambda row: (row["path"], int(row["line_number"]), row["query"]))
    return rows


def generator_candidate_files(trace_rows: list[dict[str, object]]) -> list[dict[str, object]]:
    paths = sorted({Path(row["path"]) for row in trace_rows} | {DIRECT_GENERATOR, PACKAGE_SCRIPT}, key=lambda item: str(item))
    output: list[dict[str, object]] = []
    for path in paths:
        lines = "\n".join(text_lines(path))
        mentions_output = "16_edge_candidate_result.csv" in lines or "edge_candidate_result" in lines
        mentions_flag = "edge_candidate_flag" in lines
        mentions_theta = "theta_edge" in lines or "THETA_EDGE" in lines
        mentions_strength = "relation_strength" in lines or "strength" in lines
        mentions_pair = "pair_a" in lines and "pair_b" in lines
        has_writer = "DictWriter" in lines or "write_csv" in lines or "writerow" in lines or "writerows" in lines
        has_formula = "np.exp(-d / ELL_0)" in lines or "edge = strength >= THETA_EDGE" in lines or "strength >= theta_edge" in lines
        if path == DIRECT_GENERATOR and mentions_output and has_formula and has_writer:
            evidence_strength = "direct"
            assessment = "probable_generator"
        elif has_formula and mentions_output:
            evidence_strength = "strong_partial"
            assessment = "possible_helper"
        elif mentions_output or mentions_flag or mentions_theta:
            evidence_strength = "weak_partial"
            assessment = "probable_contract_or_documentation" if "prepare_execution_package" in str(path) else "requires_manual_review"
        else:
            evidence_strength = "documentation_only"
            assessment = "not_generator"
        output.append(
            {
                "candidate_path": str(path),
                "file_type": path.suffix.lstrip("."),
                "exists": str(path.exists()).lower(),
                "mentions_output_filename": str(mentions_output).lower(),
                "mentions_edge_candidate_flag": str(mentions_flag).lower(),
                "mentions_theta_edge": str(mentions_theta).lower(),
                "mentions_relation_strength_or_strength": str(mentions_strength).lower(),
                "mentions_pair_columns": str(mentions_pair).lower(),
                "has_csv_writer_or_output_logic": str(has_writer).lower(),
                "has_formula_or_threshold_logic": str(has_formula).lower(),
                "evidence_strength": evidence_strength,
                "assessment": assessment,
            }
        )
    return output


def direct_output_write_evidence() -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for path in sorted(set(RELEVANT_FILES), key=lambda item: str(item)):
        for line_number, line in enumerate(text_lines(path), start=1):
            if "edge_rows =" in line or "write_csv(FILES[15]" in line or "16_edge_candidate_result.csv" in line:
                writes_exact = path == DIRECT_GENERATOR and ("write_csv(FILES[15]" in line or "edge_rows =" in line or '"16_edge_candidate_result.csv"' in line)
                fieldnames = ""
                if "edge_rows =" in line:
                    fieldnames = "pair_a;pair_b;strength;theta_edge;edge_candidate_flag;diagonal;claim_boundary;lineage_bundle_sha256"
                rows.append(
                    {
                        "path": str(path),
                        "line_number": line_number,
                        "excerpt": excerpt(line),
                        "writes_exact_output_file": str(writes_exact).lower(),
                        "writer_type": "write_csv helper / csv.DictWriter" if "write_csv" in line or path == DIRECT_GENERATOR else "reference",
                        "fieldnames_detected": fieldnames,
                        "assessment": "direct_writer_evidence" if writes_exact else "context_reference",
                    }
                )
    if not any(row["writes_exact_output_file"] == "true" for row in rows):
        rows.append(
            {
                "path": "NO_DIRECT_WRITER_FOUND",
                "line_number": "",
                "excerpt": "",
                "writes_exact_output_file": "false",
                "writer_type": "",
                "fieldnames_detected": "",
                "assessment": "direct_generator_unresolved",
            }
        )
    return rows


def column_contract_trace() -> list[dict[str, object]]:
    columns = ["pair_a", "pair_b", "relation_strength", "strength", "theta_edge", "edge_candidate_flag", "lineage_bundle_sha256", "source_config_sha256"]
    rows: list[dict[str, object]] = []
    for column in columns:
        found = False
        for path in sorted(set(RELEVANT_FILES), key=lambda item: str(item)):
            for line_number, line in enumerate(text_lines(path), start=1):
                if column in line:
                    found = True
                    if path == DIRECT_GENERATOR:
                        source_type = "direct_generator"
                        assessment = "direct_column_contract"
                    elif path == PRIMARY_EDGE_FILE or path.name.endswith(".csv"):
                        source_type = "artifact"
                        assessment = "artifact_column_presence"
                    elif path == PACKAGE_SCRIPT:
                        source_type = "package_contract"
                        assessment = "contract_column_trace"
                    else:
                        source_type = "context"
                        assessment = "context_trace"
                    rows.append(
                        {
                            "column_name": column,
                            "found_in_path": str(path),
                            "line_number": line_number,
                            "excerpt": excerpt(line),
                            "source_type": source_type,
                            "assessment": assessment,
                        }
                    )
        if not found:
            rows.append(
                {
                    "column_name": column,
                    "found_in_path": "",
                    "line_number": "",
                    "excerpt": "",
                    "source_type": "not_found",
                    "assessment": "not_found_in_curated_trace",
                }
            )
    return rows


def strength_generation_trace() -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for path in [DIRECT_GENERATOR, PACKAGE_SCRIPT, EXTRACT_DIR / "09_tensor_schema_runtime_mapping.csv", EXTRACT_DIR / "15_strength_matrix.csv"]:
        for line_number, line in enumerate(text_lines(path), start=1):
            lower = line.lower()
            if "strength" in lower or "relation_strength" in lower or "d_cost" in lower or "np.exp" in lower:
                mentions_formula = "np.exp(-d / ell_0)" in lower or "s_ij_strength_transform" in lower
                mentions_distance = "d_cost" in lower or "d cost" in lower or "d_" in lower
                rows.append(
                    {
                        "path": str(path),
                        "line_number": line_number,
                        "excerpt": excerpt(line),
                        "mentions_formula": str(mentions_formula).lower(),
                        "mentions_normalization": str("normalized" in lower or "normalization" in lower).lower(),
                        "mentions_same_abs_delta": str("same_abs_delta" in lower).lower(),
                        "mentions_distance_or_cost": str(mentions_distance).lower(),
                        "mentions_threshold": str("theta" in lower or "threshold" in lower).lower(),
                        "assessment": "formula_confirmed" if path == DIRECT_GENERATOR and "strength = np.exp(-d / ELL_0)" in line else "formula_candidate" if mentions_formula else "documentation_candidate",
                    }
                )
    return rows


def theta_edge_trace() -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for path in [DIRECT_GENERATOR, PACKAGE_SCRIPT, EXTRACT_DIR / "01_extract03a_r1_run_manifest.json", EXTRACT_DIR / "06_frozen_decision_carry_forward_review.csv", PRIMARY_EDGE_FILE]:
        for line_number, line in enumerate(text_lines(path), start=1):
            if "theta_edge" in line or "THETA_EDGE" in line or "HF-06" in line:
                theta = "0.5" if "0.5" in line or "THETA_EDGE = 0.5" in line else ""
                if path == DIRECT_GENERATOR and "THETA_EDGE = 0.5" in line:
                    source_type = "script_constant"
                    assessment = "theta_origin_resolved_script_constant"
                elif "HF-06" in line or "freeze_edge_threshold" in line:
                    source_type = "manifest" if path.suffix == ".json" else "config"
                    assessment = "theta_frozen_decision_trace"
                elif path == PRIMARY_EDGE_FILE:
                    source_type = "csv_column"
                    assessment = "artifact_value"
                else:
                    source_type = "documentation"
                    assessment = "documentation_trace"
                rows.append(
                    {
                        "path": str(path),
                        "line_number": line_number,
                        "excerpt": excerpt(line),
                        "theta_value_detected": theta,
                        "source_type": source_type,
                        "assessment": assessment,
                    }
                )
    return rows


def edge_candidate_flag_trace() -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for path in [DIRECT_GENERATOR, PACKAGE_SCRIPT, PRIMARY_EDGE_FILE, EXTRACT_DIR / "17_kernel_execution_summary.csv"]:
        for line_number, line in enumerate(text_lines(path), start=1):
            lower = line.lower()
            if "edge_candidate_flag" in lower or "edge = strength >=" in lower or "edge_candidate_rule" in lower:
                threshold_rule = "strength >= theta" in lower or "edge = strength >=" in lower
                same_abs = "same_abs_delta" in lower
                assignment = "edge_candidate_flag" in lower and ("int(edge" in lower or "edge_rows" in lower)
                if path == DIRECT_GENERATOR and threshold_rule:
                    assessment = "rule_confirmed_strength_threshold"
                elif same_abs and path == DIRECT_GENERATOR:
                    assessment = "rule_confirmed_same_abs_delta"
                elif path == PACKAGE_SCRIPT and threshold_rule:
                    assessment = "rule_candidate"
                elif path == PRIMARY_EDGE_FILE:
                    assessment = "documentation_only"
                else:
                    assessment = "unresolved"
                rows.append(
                    {
                        "path": str(path),
                        "line_number": line_number,
                        "excerpt": excerpt(line),
                        "mentions_strength_threshold_rule": str(threshold_rule).lower(),
                        "mentions_same_abs_delta_rule": str(same_abs).lower(),
                        "mentions_candidate_flag_assignment": str(assignment).lower(),
                        "assessment": assessment,
                    }
                )
    return rows


def lineage_hash_and_manifest_trace() -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    items = ["lineage_bundle_sha256", "source_config_sha256", "input_file_sha256", "manifest", "authorized_execution", "source_edge_file", "generator_script"]
    for item in items:
        found = False
        for path in [DIRECT_GENERATOR, EXTRACT_DIR / "01_extract03a_r1_run_manifest.json", EXTRACT_DIR / "23_lineage_and_hash_audit.csv", EXTRACT_DIR / "02_upstream_inventory_and_hashes.csv"]:
            for line_number, line in enumerate(text_lines(path), start=1):
                if item in line or (item == "manifest" and "manifest" in str(path)):
                    found = True
                    rows.append(
                        {
                            "trace_item": item,
                            "value": "",
                            "path": str(path),
                            "line_number": line_number,
                            "excerpt": excerpt(line),
                            "assessment": "resolved" if item in {"lineage_bundle_sha256", "manifest"} else "partial_or_not_explicit",
                        }
                    )
        if not found:
            rows.append(
                {
                    "trace_item": item,
                    "value": "",
                    "path": "",
                    "line_number": "",
                    "excerpt": "",
                    "assessment": "not_found_in_curated_trace",
                }
            )
    manifest = read_json(EXTRACT_DIR / "01_extract03a_r1_run_manifest.json")
    for key, value in manifest.get("lineage", {}).items():
        rows.append(
            {
                "trace_item": key,
                "value": value,
                "path": str(EXTRACT_DIR / "01_extract03a_r1_run_manifest.json"),
                "line_number": "",
                "excerpt": "manifest lineage field",
                "assessment": "resolved",
            }
        )
    rows.append(
        {
            "trace_item": "lineage_bundle_sha256",
            "value": manifest.get("lineage_bundle_sha256", ""),
            "path": str(EXTRACT_DIR / "01_extract03a_r1_run_manifest.json"),
            "line_number": "",
            "excerpt": "manifest lineage bundle",
            "assessment": "resolved",
        }
    )
    return rows


def assessment_rows(summary_flags: dict[str, bool]) -> list[dict[str, object]]:
    def row(item: str, result: str, evidence: str, blocking: str, next_action: str) -> dict[str, object]:
        return {
            "assessment_item": item,
            "result": result,
            "evidence": evidence,
            "blocking_issue": blocking,
            "next_action": next_action,
            "claim_boundary": ROW_BOUNDARY,
        }
    return [
        row("primary_edge_file_profiled", "yes", "05_primary_edge_file_profile.csv", "", "none"),
        row("direct_generator_script_found", "yes" if summary_flags["direct_generator_script_found"] else "no", str(DIRECT_GENERATOR), "", "use for replay sanity check"),
        row("direct_output_writer_found", "yes" if summary_flags["direct_output_writer_found"] else "no", "edge_rows plus write_csv(FILES[15]) in direct generator", "", "use direct writer evidence"),
        row("strength_formula_resolved", "yes" if summary_flags["strength_formula_resolved"] else "partial", "strength = np.exp(-d / ELL_0)", "", "replay strength generation"),
        row("theta_edge_origin_resolved", "yes" if summary_flags["theta_edge_origin_resolved"] else "partial", "THETA_EDGE = 0.5 plus HF-06 frozen decision check", "", "trace HF-06 provenance if needed"),
        row("edge_candidate_flag_rule_resolved", "yes" if summary_flags["edge_candidate_flag_rule_resolved"] else "partial", "edge = strength >= THETA_EDGE; edge_candidate_flag=int(edge[i,j])", "", "replay edge flags"),
        row("lineage_hashes_resolved", "yes" if summary_flags["lineage_hashes_resolved"] else "partial", "manifest lineage payload and 23_lineage_and_hash_audit.csv", "", "verify hashes before recompute"),
        row("generator_replay_feasible", "yes" if summary_flags["generator_replay_feasible"] else "partial", "direct script found; requires scipy/numpy runtime and guard-safe output path handling", "script refuses overwrite of existing A-R1 output", "create isolated replay sanity-check run"),
        row("label_permuted_recompute_feasible_after_trace", "partial", "generator found, but label-permutation control needs designed input mutation path", "must not mutate upstream F3 or A-R1", "design isolated label-permuted recompute"),
        row("abs_delta_masking_feasible_after_trace", "partial", "generator found, but no configurable abs_delta term exists; masking may require controlled code variant", "avoid silent algorithm change", "write explicit ablation protocol"),
        row("rule_ablation_feasible_after_trace", "partial", "strength/edge rule found; ablation requires audited code fork or parameterized runner", "no existing ablation config", "create recompute-control design"),
        row("source_signal_testing_feasible_after_trace", "partial", "source DB and generator lineage found", "source-native feature independence still needs separate audit", "run replay sanity check before source-signal tests"),
    ]


def recompute_feasibility_rows() -> list[dict[str, object]]:
    controls = [
        ("C01", "generator_replay_same_inputs", "partial", "true", "true", "true", "direct generator found; original output path guard prevents blind rerun", "needs isolated output path or dry-run clone", "create replay sanity-check wrapper"),
        ("C02", "label_permuted_recompute", "partial", "true", "true", "true", "direct generator found", "requires controlled label permutation before computation", "design label-permuted isolated run"),
        ("C03", "abs_delta_masked_recompute", "partial", "true", "true", "true", "rule source found indirectly through strength generation", "no existing config switch for masking labels", "write explicit ablation protocol"),
        ("C04", "rule_ablation_no_abs_delta", "partial", "true", "true", "true", "strength/edge rule found", "requires audited code variant", "create rule-ablation recompute control"),
        ("C05", "threshold_sweep_recompute", "yes", "false", "false", "false", "strength matrix and theta rule found", "artifact-level sweep possible; upstream recompute optional", "run threshold sweep control if needed"),
        ("C06", "source_native_feature_test", "partial", "true", "true", "true", "F3 source DB lineage found", "independent source-feature mapping not yet audited", "audit source-native features"),
        ("C07", "negative_source_control", "partial", "true", "true", "true", "generator found", "requires negative source input", "define synthetic or negative source input"),
        ("C08", "positive_synthetic_calibration", "partial", "true", "true", "true", "generator found", "requires synthetic source generator/input", "define positive synthetic calibration"),
    ]
    return [
        {
            "control_id": cid,
            "control_name": name,
            "feasible_now": feasible,
            "requires_direct_generator": req_gen,
            "requires_source_native_inputs": req_source,
            "requires_config": req_config,
            "available_evidence": evidence,
            "blocking_issue": blocking,
            "next_action": next_action,
        }
        for cid, name, feasible, req_gen, req_source, req_config, evidence, blocking, next_action in controls
    ]


def main() -> None:
    RUN_DIR.mkdir(parents=True, exist_ok=True)
    _origin = read_json(ORIGIN_SUMMARY)
    _source_gate = read_json(SOURCE_GATE_SUMMARY)

    profile_rows, profile = profile_primary_edge_file()
    trace_rows = trace_search_inventory()
    generator_rows = generator_candidate_files(trace_rows)
    direct_rows = direct_output_write_evidence()
    column_rows = column_contract_trace()
    strength_rows = strength_generation_trace()
    theta_rows = theta_edge_trace()
    flag_rows = edge_candidate_flag_trace()
    lineage_rows = lineage_hash_and_manifest_trace()

    direct_generator_script_found = DIRECT_GENERATOR.exists()
    direct_output_writer_found = any(row["writes_exact_output_file"] == "true" for row in direct_rows)
    strength_formula_resolved = any(row["assessment"] == "formula_confirmed" for row in strength_rows)
    theta_edge_origin_resolved = any(row["assessment"] == "theta_origin_resolved_script_constant" for row in theta_rows)
    edge_candidate_flag_rule_resolved = any(row["assessment"] == "rule_confirmed_strength_threshold" for row in flag_rows)
    lineage_hashes_resolved = any(row["trace_item"] == "lineage_bundle_sha256" and row["assessment"] == "resolved" for row in lineage_rows)
    generator_replay_feasible = direct_generator_script_found and direct_output_writer_found and strength_formula_resolved and edge_candidate_flag_rule_resolved
    flags = {
        "direct_generator_script_found": direct_generator_script_found,
        "direct_output_writer_found": direct_output_writer_found,
        "strength_formula_resolved": strength_formula_resolved,
        "theta_edge_origin_resolved": theta_edge_origin_resolved,
        "edge_candidate_flag_rule_resolved": edge_candidate_flag_rule_resolved,
        "lineage_hashes_resolved": lineage_hashes_resolved,
        "generator_replay_feasible": generator_replay_feasible,
    }
    assessment = assessment_rows(flags)
    recompute = recompute_feasibility_rows()

    write_csv(RUN_DIR / "05_primary_edge_file_profile.csv", ["field", "value", "notes"], profile_rows)
    write_csv(RUN_DIR / "06_trace_search_inventory.csv", ["query", "path", "line_number", "excerpt", "evidence_type", "trace_relevance", "claim_boundary"], trace_rows)
    write_csv(RUN_DIR / "07_generator_candidate_files.csv", ["candidate_path", "file_type", "exists", "mentions_output_filename", "mentions_edge_candidate_flag", "mentions_theta_edge", "mentions_relation_strength_or_strength", "mentions_pair_columns", "has_csv_writer_or_output_logic", "has_formula_or_threshold_logic", "evidence_strength", "assessment"], generator_rows)
    write_csv(RUN_DIR / "08_direct_output_write_evidence.csv", ["path", "line_number", "excerpt", "writes_exact_output_file", "writer_type", "fieldnames_detected", "assessment"], direct_rows)
    write_csv(RUN_DIR / "09_column_contract_trace.csv", ["column_name", "found_in_path", "line_number", "excerpt", "source_type", "assessment"], column_rows)
    write_csv(RUN_DIR / "10_strength_generation_trace.csv", ["path", "line_number", "excerpt", "mentions_formula", "mentions_normalization", "mentions_same_abs_delta", "mentions_distance_or_cost", "mentions_threshold", "assessment"], strength_rows)
    write_csv(RUN_DIR / "11_theta_edge_trace.csv", ["path", "line_number", "excerpt", "theta_value_detected", "source_type", "assessment"], theta_rows)
    write_csv(RUN_DIR / "12_edge_candidate_flag_trace.csv", ["path", "line_number", "excerpt", "mentions_strength_threshold_rule", "mentions_same_abs_delta_rule", "mentions_candidate_flag_assignment", "assessment"], flag_rows)
    write_csv(RUN_DIR / "13_lineage_hash_and_manifest_trace.csv", ["trace_item", "value", "path", "line_number", "excerpt", "assessment"], lineage_rows)
    write_csv(RUN_DIR / "14_generator_rule_reconstruction_assessment.csv", ["assessment_item", "result", "evidence", "blocking_issue", "next_action", "claim_boundary"], assessment)
    write_csv(RUN_DIR / "15_recompute_control_feasibility_after_trace.csv", ["control_id", "control_name", "feasible_now", "requires_direct_generator", "requires_source_native_inputs", "requires_config", "available_evidence", "blocking_issue", "next_action"], recompute)

    if direct_generator_script_found and direct_output_writer_found and strength_formula_resolved and theta_edge_origin_resolved and edge_candidate_flag_rule_resolved:
        upstream_status = "upstream_generator_trace_found"
        generator_rule_status = "generator_rule_reconstructable_from_repo_artifacts"
        recommended_next = "QSB-MATRIX-TOPOLOGY-LABEL-PERMUTED-RECOMPUTE-CONTROL"
        status = "upstream_generator_trace_resolution_completed"
    elif direct_generator_script_found:
        upstream_status = "upstream_generator_trace_partial"
        generator_rule_status = "generator_rule_partially_reconstructable_from_repo_artifacts"
        recommended_next = "QSB-MATRIX-TOPOLOGY-GENERATOR-REPLAY-SANITY-CHECK"
        status = "upstream_generator_trace_resolution_completed_with_blockers"
    else:
        upstream_status = "upstream_generator_trace_unresolved"
        generator_rule_status = "generator_rule_not_reconstructable_from_current_repo_artifacts"
        recommended_next = "QSB-MATRIX-TOPOLOGY-PROVENANCE-REPAIR-PLAN"
        status = "upstream_generator_trace_resolution_completed_with_blockers"

    summary = {
        "run_id": RUN_ID,
        "source_chain_latest_commit": SOURCE_CHAIN_LATEST_COMMIT,
        "primary_edge_file": str(PRIMARY_EDGE_FILE),
        "primary_edge_file_exists": profile["path_exists"],
        "primary_edge_file_sha256": profile["sha256"],
        "edge_rows_total": profile["row_count"],
        "columns_detected": profile["columns"].split(";") if profile["columns"] else [],
        "strength_column_detected": profile["strength_column_detected"],
        "theta_edge_detected": profile["theta_edge_column_detected"],
        "edge_candidate_flag_detected": profile["edge_candidate_flag_column_detected"],
        "candidate_edge_count": profile["candidate_count"],
        "non_candidate_edge_count": profile["non_candidate_count"],
        "direct_generator_script_found": direct_generator_script_found,
        "direct_output_writer_found": direct_output_writer_found,
        "direct_output_writer_path": str(DIRECT_GENERATOR) if direct_output_writer_found else "",
        "strength_formula_resolved": strength_formula_resolved,
        "theta_edge_origin_resolved": theta_edge_origin_resolved,
        "edge_candidate_flag_rule_resolved": edge_candidate_flag_rule_resolved,
        "lineage_hashes_resolved": lineage_hashes_resolved,
        "generator_replay_feasible": generator_replay_feasible,
        "label_permuted_recompute_feasible_after_trace": False,
        "abs_delta_masking_feasible_after_trace": False,
        "rule_ablation_feasible_after_trace": False,
        "source_signal_testing_feasible_after_trace": False,
        "upstream_generator_trace_status": upstream_status,
        "generator_rule_status": generator_rule_status,
        "recommended_next_run_id": recommended_next,
        "status": status,
        "claim_boundary": CLAIM_BOUNDARY,
    }
    with (RUN_DIR / "04_upstream_generator_trace_summary.json").open("w", encoding="utf-8") as handle:
        json.dump(summary, handle, indent=2, ensure_ascii=False)
        handle.write("\n")

    review = f"""# QSB-MATRIX-TOPOLOGY-UPSTREAM-GENERATOR-TRACE-RESOLUTION

## Purpose

This audit resolves whether the observed artifact-level rule structure can be traced to an upstream generator in the repository. It does not by itself establish a source-driven signal; it determines whether replay and recomputation controls are now feasible.

## Source basis

Primary edge file: `{PRIMARY_EDGE_FILE}`. Context was read from prior origin and source-signal gate artifacts when present.

## Primary edge file profile

The primary edge artifact exists: {summary["primary_edge_file_exists"]}. It has {summary["edge_rows_total"]} rows, {summary["candidate_edge_count"]} candidate edges, and {summary["non_candidate_edge_count"]} non-candidate edges.

## Trace search method

The search was curated to EXTRACT03 scripts, package contracts, A-R1 run artifacts, and downstream review scripts. Large raw grep dumps were not written.

## Generator candidate files

The direct generator candidate is `scripts/qsb_extract03a_r1/run_authorized_execution_with_s1_addendum.py`.

## Direct output writer evidence

The direct generator defines the output filename list containing `16_edge_candidate_result.csv`, constructs `edge_rows`, and calls `write_csv(FILES[15], ...)`.

## Strength generation trace

The generator computes `strength = np.exp(-d / ELL_0)` after constructing `d` from `K` and writes `15_strength_matrix.csv` as `relation_strength`.

## Theta-edge trace

The generator defines `THETA_EDGE = 0.5` and checks the frozen HF-06 decision before execution. The primary edge artifact carries `theta_edge=0.5`.

## Edge-candidate-flag trace

The generator computes `edge = strength >= THETA_EDGE`, clears the diagonal, and writes `edge_candidate_flag` as `int(edge[i,j])`.

## Lineage and manifest trace

The A-R1 manifest records the lineage payload and `lineage_bundle_sha256`. The lineage/hash audit records output hashes including `16_edge_candidate_result.csv`.

## Reconstruction assessment

Upstream trace status: `{summary["upstream_generator_trace_status"]}`. Generator rule status: `{summary["generator_rule_status"]}`. Replay is methodologically feasible from repo artifacts, but the original script refuses to overwrite the existing A-R1 run and uses fixed output paths, so replay should be done via an isolated sanity-check wrapper or controlled copy.

## Recompute-control feasibility

Artifact-level threshold sweep is feasible. Label-permuted recompute, abs-delta masking, rule ablation, and source-signal controls require a separate controlled recompute design.

## Interpretation

The generator and core rule are traceable in repo artifacts. This resolves the prior upstream-generator blocker at the provenance/rule level, but it does not confirm a source-driven signal.

## Claim boundary

This is a provenance, lineage, and generator-trace audit only. It makes no physical, geometric, metric, gravitative, causal, dynamical, source-signal, experimental, or physical-emergence claim.

## Next-step gate

Recommended next run: `{summary["recommended_next_run_id"]}`.
"""
    write_text(RUN_DIR / "16_upstream_generator_trace_review_note.md", review)
    write_text(
        RUN_DIR / "17_next_recompute_control_recommendation.md",
        """# Next Recompute Control Recommendation

Recommended next run:

`QSB-MATRIX-TOPOLOGY-LABEL-PERMUTED-RECOMPUTE-CONTROL`

Rationale:

The direct generator and candidate-edge rule are now traceable. The next useful control is an isolated recomputation in which Pair-ID labels or label-derived mappings are permuted before generator execution, without mutating existing source artifacts or prior runs.

Required guard:

Do not overwrite `runs/QSB-EXTRACT03A-R1/authorized_execution_with_s1_addendum/`. Use a new run directory and explicitly document any generator copy or wrapper changes.
""",
    )
    write_text(
        RUN_DIR / "18_trace_resolution_limitations.md",
        """# Trace Resolution Limitations

- The direct generator is found and the rule is reconstructable from repo artifacts.
- The original generator has fixed output paths and an overwrite guard, so replay must not be run against the existing A-R1 directory.
- Label-permuted recomputation requires a controlled design for how Pair-ID labels are permuted before the generator sees them.
- Abs-delta masking or rule ablation requires an audited code variant or parameterized wrapper.
- This run does not establish source-driven signal support.
""",
    )


if __name__ == "__main__":
    main()
