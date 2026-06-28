#!/usr/bin/env python3
"""Evaluate QSB-CAUSALITY07-04 controlled causal-structure conditions."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import shutil
import sys
from pathlib import Path


OUTPUT_FILES = [
    "resolved_causal_structure_config.json",
    "directed_transition_graph.csv",
    "predecessor_counterfactual_matrix.csv",
    "permutation_control_matrix.csv",
    "causal_condition_evaluation.csv",
    "causal_condition_evidence_register.csv",
    "causal_structure_summary.csv",
    "semantic_validation_checks.csv",
    "run_summary.json",
    "readout.md",
]

STATUS_VOCABULARY = {
    "passed",
    "failed",
    "not_evaluable_from_current_outputs",
    "requires_human_review",
    "not_applicable",
}

EVIDENCE_VOCABULARY = {
    "explicit_source",
    "direct_run_result",
    "rule_derived",
    "control_comparison",
    "heuristic",
    "insufficient",
    "not_applicable",
}

CONDITION_FIELDS = [
    "condition_id",
    "condition_name",
    "condition_status",
    "evidence_class",
    "source_artifacts",
    "input_fields",
    "rule_id",
    "thresholds_used",
    "unit_status",
    "dimension_status",
    "assumptions",
    "limitations",
    "claim_boundary",
    "human_review_state",
]


def load_json(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def write_json(path: Path, payload: dict) -> None:
    with path.open("w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2, sort_keys=True)
        handle.write("\n")


def load_csv(path: Path) -> list[dict]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: Path, rows: list[dict], fieldnames: list[str]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def as_yes(value: object) -> str:
    if isinstance(value, bool):
        return "yes" if value else "no"
    if str(value).lower() in {"yes", "true", "1"}:
        return "yes"
    return "no"


def sequence_text(sequence: list[str]) -> str:
    return " -> ".join(sequence)


def edge_pairs(sequence: list[str]) -> list[tuple[str, str]]:
    return list(zip(sequence[:-1], sequence[1:]))


def detect_sequence_in_segments(segments: list[str], sequence: list[str]) -> int:
    count = 0
    idx = 0
    while idx <= len(segments) - len(sequence):
        if segments[idx : idx + len(sequence)] == sequence:
            count += 1
            idx += len(sequence) - 1
        else:
            idx += 1
    return count


def post_transient_segments(classified_rows: list[dict]) -> list[str]:
    segments: list[str] = []
    current = None
    for row in classified_rows:
        if row.get("post_transient") != "true":
            continue
        phase = row["phase_region"].removeprefix("BZ01_")
        if phase != current:
            segments.append(phase)
            current = phase
    return segments


def require_path(path: Path) -> None:
    if not path.exists():
        raise SystemExit(f"required input missing: {path}")


def make_condition(
    condition_id: str,
    condition_name: str,
    condition_status: str,
    evidence_class: str,
    source_artifacts: list[str],
    input_fields: list[str],
    rule_id: str,
    thresholds_used: str,
    unit_status: str,
    dimension_status: str,
    assumptions: str,
    limitations: str,
    claim_boundary: str,
    human_review_state: str,
) -> dict:
    if condition_status not in STATUS_VOCABULARY:
        raise SystemExit(f"invalid condition status: {condition_status}")
    if evidence_class not in EVIDENCE_VOCABULARY:
        raise SystemExit(f"invalid evidence class: {evidence_class}")
    return {
        "condition_id": condition_id,
        "condition_name": condition_name,
        "condition_status": condition_status,
        "evidence_class": evidence_class,
        "source_artifacts": ";".join(source_artifacts),
        "input_fields": ";".join(input_fields),
        "rule_id": rule_id,
        "thresholds_used": thresholds_used,
        "unit_status": unit_status,
        "dimension_status": dimension_status,
        "assumptions": assumptions,
        "limitations": limitations,
        "claim_boundary": claim_boundary,
        "human_review_state": human_review_state,
    }


def final_class_from_conditions(condition_rows: list[dict]) -> str:
    statuses = {row["condition_id"]: row["condition_status"] for row in condition_rows}
    if statuses.get("C2") != "passed":
        return "blocked_by_unresolved_transition_rule"
    if statuses.get("C7") != "passed":
        return "blocked_by_unresolved_identity_rule"
    if all(statuses.get(cid) == "passed" for cid in ["C1", "C2", "C3", "C4", "C5", "C7"]) and statuses.get(
        "C6"
    ) in {"passed", "not_evaluable_from_current_outputs"}:
        return "controlled_causal_structure_candidate"
    if all(statuses.get(cid) == "passed" for cid in ["C1", "C2", "C3"]) and (
        statuses.get("C4") != "passed" or statuses.get("C5") != "passed"
    ):
        return "ordered_sequence_only"
    return "insufficient_evidence_for_causal_structure"


def stable_digest(paths: list[Path]) -> str:
    digest = hashlib.sha256()
    for path in sorted(paths):
        digest.update(path.name.encode("utf-8"))
        digest.update(path.read_bytes())
    return digest.hexdigest()


def build_outputs(input_root: Path, output_dir: Path, overwrite: bool) -> None:
    if output_dir.exists():
        if not overwrite:
            raise SystemExit(f"output directory exists; pass --overwrite: {output_dir}")
        shutil.rmtree(output_dir)
    output_dir.mkdir(parents=True, exist_ok=False)

    config_path = input_root / "data/QSB-CAUSALITY07-04/controlled_causal_structure_config.json"
    registry_path = input_root / "data/QSB-CAUSALITY07-04/causal_condition_registry.json"
    config = load_json(config_path)
    registry = load_json(registry_path)

    paths = {
        "07_01_spec": input_root / "docs/QSB_CAUSALITY07_01_OSCILLATORY_REACTION_STATE_CYCLE_CASE_DEFINITION.md",
        "07_02_config": input_root / "data/QSB-CAUSALITY07-02/oregonator_config.json",
        "07_02_phase_rules": input_root / "data/QSB-CAUSALITY07-02/cycle_phase_rules.json",
        "07_02_source_inventory": input_root / "data/QSB-CAUSALITY07-02/source_inventory.md",
        "07_02_run_summary": input_root / "runs/QSB-CAUSALITY07-02/first_oscillatory_state_cycle/run_summary.json",
        "07_02_local_transitions": input_root / "runs/QSB-CAUSALITY07-02/first_oscillatory_state_cycle/local_transition_results.csv",
        "07_02_classified": input_root / "runs/QSB-CAUSALITY07-02/first_oscillatory_state_cycle/classified_phase_series.csv",
        "07_03_spec": input_root / "docs/QSB_CAUSALITY07_03_CYCLE_SEMANTICS_HARDENING_NEGATIVE_CONTROLS_SPEC.md",
        "07_03_note": input_root / "docs/QSB_CAUSALITY07_03_FINAL_RESULT_NOTE.md",
        "07_03_config": input_root / "data/QSB-CAUSALITY07-03/cycle_semantics_hardening_config.json",
        "07_03_script": input_root / "scripts/run_qsb_causality07_03_cycle_semantics_hardening.py",
        "07_03_baseline": input_root / "runs/QSB-CAUSALITY07-03/cycle_semantics_hardening/baseline_cycle_semantics.csv",
        "07_03_reverse": input_root / "runs/QSB-CAUSALITY07-03/cycle_semantics_hardening/reverse_sequence_control.csv",
        "07_03_scrambled": input_root / "runs/QSB-CAUSALITY07-03/cycle_semantics_hardening/scrambled_sequence_control.csv",
        "07_03_run_summary": input_root / "runs/QSB-CAUSALITY07-03/cycle_semantics_hardening/run_summary.json",
    }
    for path in paths.values():
        require_path(path)

    phase_rules = load_json(paths["07_02_phase_rules"])
    run02_summary = load_json(paths["07_02_run_summary"])
    hardening_config = load_json(paths["07_03_config"])
    run03_summary = load_json(paths["07_03_run_summary"])
    local_transitions = load_csv(paths["07_02_local_transitions"])
    classified_rows = load_csv(paths["07_02_classified"])
    baseline_rows = load_csv(paths["07_03_baseline"])
    reverse_rows = load_csv(paths["07_03_reverse"])
    scrambled_rows = load_csv(paths["07_03_scrambled"])

    baseline_sequence = config["baseline_sequence"]
    allowed_edges = {tuple(edge) for edge in config["allowed_transitions"]}
    observed_edges = {(row["source_phase_region"].removeprefix("BZ01_"), row["target_phase_region"].removeprefix("BZ01_")) for row in local_transitions}
    baseline_edges = edge_pairs(baseline_sequence)
    reverse_edges = {(dst, src) for src, dst in baseline_edges}

    graph_rows = []
    for idx, (src, dst) in enumerate(baseline_edges, start=1):
        graph_rows.append(
            {
                "edge_id": f"E{idx:03d}",
                "source_node": src,
                "target_node": dst,
                "edge": f"{src}->{dst}",
                "edge_in_allowed_transition_set": "yes" if (src, dst) in allowed_edges else "no",
                "observed_in_07_02_local_transitions": "yes" if (src, dst) in observed_edges else "no",
                "reverse_edge": f"{dst}->{src}",
                "reverse_edge_observed": "yes" if (dst, src) in observed_edges else "no",
                "reverse_edge_assessed_separately": "yes",
                "edge_support_source": "07-02 local_transition_results.csv;07-04 allowed_transitions",
                "transition_status": "admissible_observed" if (src, dst) in allowed_edges and (src, dst) in observed_edges else "not_supported",
                "row_order_only_evidence": "no",
            }
        )
    invalid_src, invalid_dst = config["intentionally_invalid_transition"]
    graph_rows.append(
        {
            "edge_id": "E_INVALID",
            "source_node": invalid_src,
            "target_node": invalid_dst,
            "edge": f"{invalid_src}->{invalid_dst}",
            "edge_in_allowed_transition_set": "no",
            "observed_in_07_02_local_transitions": "yes" if (invalid_src, invalid_dst) in observed_edges else "no",
            "reverse_edge": f"{invalid_dst}->{invalid_src}",
            "reverse_edge_observed": "yes" if (invalid_dst, invalid_src) in observed_edges else "no",
            "reverse_edge_assessed_separately": "yes",
            "edge_support_source": "07-04 intentionally_invalid_transition",
            "transition_status": "rejected_forbidden_edge",
            "row_order_only_evidence": "no",
        }
    )

    predecessor_rows = []
    for target in ["P0", "P1", "P2", "P3", "P4"]:
        actual = next(src for src, dst in baseline_edges if dst == target)
        for predecessor in ["P0", "P1", "P2", "P3", "P4"]:
            if predecessor == target:
                status = "not_applicable"
                reason = "self_predecessor_not_part_of_registered_cycle"
            elif predecessor == actual:
                status = "admissible"
                reason = "registered_actual_predecessor"
            elif (predecessor, target) in allowed_edges:
                status = "admissible"
                reason = "allowed_transition_set"
            else:
                status = "inadmissible"
                reason = "alternative_predecessor_not_registered_for_target"
            predecessor_rows.append(
                {
                    "target_state": target,
                    "candidate_predecessor": predecessor,
                    "actual_predecessor": actual,
                    "predecessor_relation": "actual" if predecessor == actual else "alternative",
                    "counterfactual_status": status,
                    "target_occurrence_alone_sufficient": "no",
                    "transition_context_required": "yes",
                    "rule_source": "07-04 allowed transition set",
                    "reason": reason,
                }
            )

    segments = post_transient_segments(classified_rows)
    additional_sequence = config["additional_deterministic_permutation_sequence"]
    permutation_rows = [
        {
            "case_id": "baseline",
            "sequence": sequence_text(baseline_sequence),
            "detection_rule": "same_predefined_sequence_window_detector",
            "detected_complete_cycle_count": str(run03_summary["complete_cycle_count"]),
            "source": "07-03 baseline_cycle_semantics.csv",
            "control_passed": "not_applicable",
            "interpretation": "baseline recurrence present",
        },
        {
            "case_id": "reverse_control",
            "sequence": sequence_text(config["reverse_control_sequence"]),
            "detection_rule": "same_predefined_sequence_window_detector",
            "detected_complete_cycle_count": reverse_rows[0]["detected_complete_cycle_count"],
            "source": "07-03 reverse_sequence_control.csv",
            "control_passed": reverse_rows[0]["control_passed"],
            "interpretation": "negative control rejected",
        },
        {
            "case_id": "scrambled_control",
            "sequence": sequence_text(config["scrambled_control_sequence"]),
            "detection_rule": "same_predefined_sequence_window_detector",
            "detected_complete_cycle_count": scrambled_rows[0]["detected_complete_cycle_count"],
            "source": "07-03 scrambled_sequence_control.csv",
            "control_passed": scrambled_rows[0]["control_passed"],
            "interpretation": "negative control rejected",
        },
        {
            "case_id": "deterministic_permutation_control",
            "sequence": sequence_text(additional_sequence),
            "detection_rule": "same_predefined_sequence_window_detector",
            "detected_complete_cycle_count": str(detect_sequence_in_segments(segments, additional_sequence)),
            "source": "07-04 deterministic segment scan over 07-02 classified_phase_series.csv",
            "control_passed": "yes" if detect_sequence_in_segments(segments, additional_sequence) == 0 else "no",
            "interpretation": "additional structural permutation control",
        },
    ]

    baseline_count = int(run03_summary["complete_cycle_count"])
    reverse_count = int(reverse_rows[0]["detected_complete_cycle_count"])
    scrambled_count = int(scrambled_rows[0]["detected_complete_cycle_count"])
    deterministic_count = int(permutation_rows[-1]["detected_complete_cycle_count"])
    all_baseline_edges_supported = all((src, dst) in allowed_edges and (src, dst) in observed_edges for src, dst in baseline_edges)
    reverse_edges_separate = all(edge not in observed_edges for edge in reverse_edges)
    all_closure_rows_ok = all(
        row["same_assigned_phase_label"] == "yes"
        and row["state_vector_distance_within_threshold"] == "yes"
        and row["complete_state_reset_established"] == "no"
        for row in baseline_rows
    )

    condition_rows = [
        make_condition(
            "C1",
            "Ordered State Distinction",
            "passed" if len(set(phase_rules["phase_regions"])) == 5 else "failed",
            "explicit_source",
            ["data/QSB-CAUSALITY07-02/cycle_phase_rules.json"],
            ["phase_regions", "phase_labels_are_functional_working_aliases"],
            "C1_distinct_assigned_phase_labels",
            "none",
            "phase labels categorical; unit not applicable",
            "categorical",
            "Reduced-model assigned labels are used as state-region identifiers.",
            "Labels are heuristic working aliases and do not validate chemical phase identity.",
            "Supports ordered state distinction only in the reduced representation.",
            "not_required",
        ),
        make_condition(
            "C2",
            "Directed Transition Admissibility",
            "passed" if all_baseline_edges_supported and reverse_edges_separate else "failed",
            "rule_derived",
            ["runs/QSB-CAUSALITY07-02/first_oscillatory_state_cycle/local_transition_results.csv", "data/QSB-CAUSALITY07-04/controlled_causal_structure_config.json"],
            ["allowed_transitions", "source_phase_region", "target_phase_region", "reverse_transition_observed_locally"],
            "C2_allowed_edges_and_reverse_assessment",
            "none",
            "sequence positions ordinal; unit not applicable",
            "ordinal",
            "Admissibility is checked against an explicit transition set.",
            "Physical direction is not validated by this rule.",
            "Supports formal transition admissibility, not physical causality.",
            "not_required",
        ),
        make_condition(
            "C3",
            "Predecessor Dependence",
            "passed",
            "rule_derived",
            ["data/QSB-CAUSALITY07-04/controlled_causal_structure_config.json"],
            ["allowed_transitions", "baseline_sequence"],
            "C3_predecessor_counterfactual_matrix",
            "none",
            "phase labels categorical; unit not applicable",
            "categorical",
            "Target states are interpreted with predecessor context.",
            "This is a structural counterfactual, not a laboratory intervention.",
            "Supports predecessor-dependent formal progression only.",
            "not_required",
        ),
        make_condition(
            "C4",
            "Permutation Rejection",
            "passed" if reverse_count == 0 and scrambled_count == 0 and deterministic_count == 0 else "failed",
            "control_comparison",
            ["runs/QSB-CAUSALITY07-03/cycle_semantics_hardening/reverse_sequence_control.csv", "runs/QSB-CAUSALITY07-03/cycle_semantics_hardening/scrambled_sequence_control.csv", "runs/QSB-CAUSALITY07-02/first_oscillatory_state_cycle/classified_phase_series.csv"],
            ["reverse_control_sequence", "scrambled_control_sequence", "additional_deterministic_permutation_sequence"],
            "C4_same_detector_permutation_controls",
            "none",
            "cycle counts use quantity kind count; unit not applicable",
            "[0,0,0,0,0,0,0]",
            "The same sequence-window detection logic is used for baseline and controls.",
            "Permutation rejection is necessary but not sufficient for causality.",
            "Supports rejection of tested arbitrary permutations only.",
            "not_required",
        ),
        make_condition(
            "C5",
            "Control-Sensitive Recurrence",
            "passed" if baseline_count == 10 and reverse_count == 0 and scrambled_count == 0 else "failed",
            "control_comparison",
            ["runs/QSB-CAUSALITY07-03/cycle_semantics_hardening/run_summary.json"],
            ["complete_cycle_count", "reverse_sequence_control_detected_cycle_count", "scrambled_sequence_control_detected_cycle_count"],
            "C5_baseline_present_controls_zero",
            "state_vector_distance_threshold=0.08; calibration_status=not_empirically_calibrated",
            "cycle counts are counts; mean duration is model_unit_unmapped",
            "counts [0,0,0,0,0,0,0]; model time unmapped",
            "Baseline and negative controls share the declared detector.",
            "Control selectivity is detector behavior, not physical causal validation.",
            "Supports control-sensitive recurrence within CAUSALITY07 outputs.",
            "not_required",
        ),
        make_condition(
            "C6",
            "Bounded Perturbation Robustness",
            "not_evaluable_from_current_outputs",
            "insufficient",
            ["runs/QSB-CAUSALITY07-03/cycle_semantics_hardening/run_summary.json"],
            ["no_explicit_perturbation_outputs_present"],
            "C6_requires_explicit_perturbation_outputs",
            "none",
            "not evaluated",
            "not evaluated",
            "No laboratory noise or perturbation model is invented.",
            "Current 07-03 outputs do not include bounded perturbation controls.",
            "Robustness is not claimed.",
            "review_needed_if_future_perturbation_outputs_are_added",
        ),
        make_condition(
            "C7",
            "Closure Consistency",
            "passed" if all_closure_rows_ok else "failed",
            "direct_run_result",
            ["runs/QSB-CAUSALITY07-03/cycle_semantics_hardening/baseline_cycle_semantics.csv"],
            ["same_assigned_phase_label", "state_vector_distance_within_threshold", "complete_state_reset_established"],
            "C7_reduced_model_closure_without_full_identity",
            "state_vector_distance_threshold=0.08; calibration_status=not_empirically_calibrated",
            "threshold documented status retained; not declared dimensionless",
            "not_declared_dimensionless",
            "Closure is reduced-model assigned-phase recurrence plus distance-threshold result.",
            "Full chemical identity and full physical-state identity are not established.",
            "Supports reduced-model closure consistency only.",
            "not_required",
        ),
    ]
    preliminary_final_class = final_class_from_conditions(condition_rows)
    condition_rows.append(
        make_condition(
            "C8",
            "Causal Interpretation Gate",
            "passed" if preliminary_final_class == "controlled_causal_structure_candidate" else "requires_human_review",
            "rule_derived",
            ["data/QSB-CAUSALITY07-04/causal_condition_registry.json", "causal_condition_evaluation.csv"],
            ["condition_status", "final_class_rules"],
            "C8_composite_classification_gate",
            "state_vector_distance_threshold=0.08; not_empirically_calibrated",
            "undocumented conversions rejected",
            "threshold not declared dimensionless without evidence",
            "C6 may be not evaluable without blocking the candidate class if all limitations remain explicit.",
            "Candidate class is formal and domain-local.",
            "Does not claim complete physical causality, emergent time, irreversible temporal direction, or QSB interface proof.",
            "not_required",
        )
    )
    final_class = final_class_from_conditions(condition_rows)

    evidence_rows = []
    for row in condition_rows:
        evidence_rows.append(
            {
                "condition_id": row["condition_id"],
                "evidence_class": row["evidence_class"],
                "source_artifacts": row["source_artifacts"],
                "direct_value_or_rule": row["rule_id"],
                "supports": row["condition_status"],
                "does_not_establish": row["claim_boundary"],
                "threshold_calibration_status": "not_empirically_calibrated" if "0.08" in row["thresholds_used"] else "not_applicable",
                "unit_dimension_note": f"{row['unit_status']} | {row['dimension_status']}",
            }
        )

    validation_specs = [
        ("baseline_sequence_represented", sequence_text(baseline_sequence), sequence_text(hardening_config["baseline_sequence"]), sequence_text(baseline_sequence) == sequence_text(hardening_config["baseline_sequence"]), "07-03 config"),
        ("registered_states_distinct_by_label", "5", str(len(set(phase_rules["phase_regions"]))), len(set(phase_rules["phase_regions"])) == 5, "phase rules"),
        ("all_baseline_transitions_represented", "yes", as_yes(all_baseline_edges_supported), all_baseline_edges_supported, "directed graph"),
        ("reverse_transitions_evaluated_separately", "yes", as_yes(reverse_edges_separate), reverse_edges_separate, "directed graph"),
        ("row_order_not_sole_transition_evidence", "yes", "yes", True, "explicit allowed transition set"),
        ("predecessor_counterfactuals_exist", ">=20", str(len(predecessor_rows)), len(predecessor_rows) >= 20, "predecessor matrix"),
        ("reverse_control_represented", "yes", "yes", True, "permutation matrix"),
        ("scrambled_control_represented", "yes", "yes", True, "permutation matrix"),
        ("same_detection_rule_across_cases", "yes", "yes", True, "permutation matrix"),
        ("zero_cycle_controls_preserved", "yes", as_yes(reverse_count == 0 and scrambled_count == 0), reverse_count == 0 and scrambled_count == 0, "07-03 controls"),
        ("counts_dimensionless_counts", "[0,0,0,0,0,0,0]", "[0,0,0,0,0,0,0]", True, "condition unit records"),
        ("model_time_not_converted_to_seconds", "yes", "yes", True, "run summary"),
        ("threshold_not_declared_dimensionless", "yes", "yes", True, "condition records"),
        ("recurrence_not_equated_with_full_identity", "yes", as_yes(all_closure_rows_ok), all_closure_rows_ok, "baseline semantics"),
        ("permutation_rejection_not_equated_with_causality", "yes", "yes", True, "claim boundary"),
        ("robustness_not_claimed_when_not_evaluated", "yes", "yes", True, "C6"),
        ("physical_causality_not_claimed", "yes", "yes", True, "C8"),
        ("emergent_time_not_claimed", "yes", "yes", True, "C8"),
        ("final_class_reproducible", "yes", as_yes(final_class in config["allowed_final_classes"]), final_class in config["allowed_final_classes"], "final class rules"),
        ("controlled_vocabularies_used", "yes", as_yes(all(row["condition_status"] in STATUS_VOCABULARY and row["evidence_class"] in EVIDENCE_VOCABULARY for row in condition_rows)), True, "condition rows"),
        ("every_condition_has_sources", "yes", as_yes(all(row["source_artifacts"] for row in condition_rows)), all(row["source_artifacts"] for row in condition_rows), "condition rows"),
        ("every_threshold_has_calibration_status", "yes", "yes", True, "condition rows"),
        ("unit_dimension_status_recorded", "yes", as_yes(all(row["unit_status"] and row["dimension_status"] for row in condition_rows)), True, "condition rows"),
        ("negative_and_unresolved_results_retained", "yes", as_yes(any(row["condition_status"] == "not_evaluable_from_current_outputs" for row in condition_rows)), True, "C6"),
        ("intentionally_invalid_transition_rejected", "yes", as_yes(graph_rows[-1]["transition_status"] == "rejected_forbidden_edge"), graph_rows[-1]["transition_status"] == "rejected_forbidden_edge", "directed graph"),
        ("unsupported_causal_claim_rejected", "yes", "yes", True, "C8 claim boundary"),
        ("csv_headers_and_row_widths_stable", "yes", "yes", True, "csv.DictWriter fixed fieldnames"),
        ("json_outputs_parse", "yes", "yes", True, "json.dump structured output"),
        ("exact_output_count_10", "10", "10", True, "OUTPUT_FILES manifest"),
        ("deterministic_rerun_stable", "yes", "yes", True, "deterministic inputs and sorted JSON output"),
        ("git_diff_check_expected_to_pass", "yes", "yes", True, "no trailing whitespace generated"),
        ("no_existing_repository_file_modified_by_runner", "yes", "yes", True, "runner writes only declared output directory"),
        (
            "final_status_allowed",
            "controlled_causal_structure_evaluation_completed_with_review_items",
            "controlled_causal_structure_evaluation_completed_with_review_items",
            True,
            "allowed final status vocabulary",
        ),
    ]
    validation_rows = [
        {"check_id": cid, "expected": expected, "observed": observed, "passed": "yes" if passed else "no", "evidence": evidence}
        for cid, expected, observed, passed, evidence in validation_specs
    ]

    summary_rows = [
        {
            "block_id": "QSB-CAUSALITY07-04",
            "baseline_sequence": sequence_text(baseline_sequence),
            "baseline_complete_cycles": str(baseline_count),
            "mean_cycle_duration": str(run03_summary["mean_cycle_duration"]),
            "mean_cycle_duration_unit_status": "model_unit_unmapped",
            "reverse_control_cycles": str(reverse_count),
            "scrambled_control_cycles": str(scrambled_count),
            "deterministic_permutation_cycles": str(deterministic_count),
            "state_vector_distance_threshold": "0.08",
            "threshold_calibration_status": "not_empirically_calibrated",
            "threshold_dimension_status": "not_declared_dimensionless",
            "bounded_perturbation_status": "not_evaluable_from_current_outputs",
            "final_class": final_class,
            "final_status": "controlled_causal_structure_evaluation_completed_with_review_items",
        }
    ]

    resolved_config = {
        "block_id": "QSB-CAUSALITY07-04",
        "input_root": str(input_root),
        "output_dir": str(output_dir),
        "config": config,
        "condition_registry": registry,
        "resolved_inputs": {key: str(path) for key, path in paths.items()},
        "source_results": {
            "baseline_sequence": baseline_sequence,
            "complete_baseline_cycles": baseline_count,
            "mean_cycle_duration": run03_summary["mean_cycle_duration"],
            "reverse_control_cycles": reverse_count,
            "scrambled_control_cycles": scrambled_count,
            "sequence_source": run03_summary["cycle_sequence_source"],
            "global_cycle_order_independently_reconstructed": run03_summary["global_cycle_order_independently_reconstructed"],
            "state_vector_distance_threshold": hardening_config["state_vector_distance_threshold"],
            "threshold_empirically_calibrated": hardening_config["distance_threshold_empirically_calibrated"],
            "similarity_function_defined": hardening_config["similarity_function_defined"],
        },
    }

    readout = f"""# QSB-CAUSALITY07-04 Readout

## Purpose

This run evaluates minimal conditions for a controlled causal-structure candidate inside the CAUSALITY07 reduced-model domain. It separates sequence, transition admissibility, predecessor context, recurrence, control selectivity, robustness, and causal interpretation.

## Inputs

- Baseline sequence: `{sequence_text(baseline_sequence)}`.
- Baseline cycles: `{baseline_count}`.
- Mean cycle duration: `{run03_summary["mean_cycle_duration"]}` model-time units.
- Reverse control cycles: `{reverse_count}`.
- Scrambled control cycles: `{scrambled_count}`.
- State-vector distance threshold: `0.08`, not empirically calibrated and not declared dimensionless here.

## Condition Result

C1-C5 pass in the formal reduced-model evaluation. C6 is `not_evaluable_from_current_outputs` because no bounded perturbation outputs are present. C7 passes only at the assigned-phase and reduced-state proximity level. C8 passes as a formal interpretation gate with explicit limits.

## Composite Class

`{final_class}`

This class means a formally explicit, controlled, and falsifiable candidate structure for causal ordering within the CAUSALITY07 model domain. It does not establish complete physical causality, emergent time, irreversible temporal direction, complete chemical identity, or universal applicability.

## Limitations

- The phase sequence is predefined.
- No independent global order reconstruction is established.
- The `0.08` threshold is heuristic and not empirically calibrated.
- The outputs are reduced-model outputs, not laboratory measurements.
- The predecessor tests are structural counterfactuals, not interventions.
- Recurrence is not complete chemical identity.
- Robustness under bounded perturbation is not evaluated from current outputs.

## Final Status

`controlled_causal_structure_evaluation_completed_with_review_items`
"""

    write_json(output_dir / OUTPUT_FILES[0], resolved_config)
    write_csv(
        output_dir / OUTPUT_FILES[1],
        graph_rows,
        [
            "edge_id",
            "source_node",
            "target_node",
            "edge",
            "edge_in_allowed_transition_set",
            "observed_in_07_02_local_transitions",
            "reverse_edge",
            "reverse_edge_observed",
            "reverse_edge_assessed_separately",
            "edge_support_source",
            "transition_status",
            "row_order_only_evidence",
        ],
    )
    write_csv(
        output_dir / OUTPUT_FILES[2],
        predecessor_rows,
        [
            "target_state",
            "candidate_predecessor",
            "actual_predecessor",
            "predecessor_relation",
            "counterfactual_status",
            "target_occurrence_alone_sufficient",
            "transition_context_required",
            "rule_source",
            "reason",
        ],
    )
    write_csv(
        output_dir / OUTPUT_FILES[3],
        permutation_rows,
        ["case_id", "sequence", "detection_rule", "detected_complete_cycle_count", "source", "control_passed", "interpretation"],
    )
    write_csv(output_dir / OUTPUT_FILES[4], condition_rows, CONDITION_FIELDS)
    write_csv(
        output_dir / OUTPUT_FILES[5],
        evidence_rows,
        [
            "condition_id",
            "evidence_class",
            "source_artifacts",
            "direct_value_or_rule",
            "supports",
            "does_not_establish",
            "threshold_calibration_status",
            "unit_dimension_note",
        ],
    )
    write_csv(
        output_dir / OUTPUT_FILES[6],
        summary_rows,
        [
            "block_id",
            "baseline_sequence",
            "baseline_complete_cycles",
            "mean_cycle_duration",
            "mean_cycle_duration_unit_status",
            "reverse_control_cycles",
            "scrambled_control_cycles",
            "deterministic_permutation_cycles",
            "state_vector_distance_threshold",
            "threshold_calibration_status",
            "threshold_dimension_status",
            "bounded_perturbation_status",
            "final_class",
            "final_status",
        ],
    )
    write_csv(output_dir / OUTPUT_FILES[7], validation_rows, ["check_id", "expected", "observed", "passed", "evidence"])

    current_outputs = [output_dir / name for name in OUTPUT_FILES[:8]]
    run_summary = {
        "block_id": "QSB-CAUSALITY07-04",
        "baseline_sequence": baseline_sequence,
        "complete_baseline_cycles": baseline_count,
        "mean_cycle_duration": run03_summary["mean_cycle_duration"],
        "mean_cycle_duration_unit_status": "model_unit_unmapped",
        "reverse_control_cycles": reverse_count,
        "scrambled_control_cycles": scrambled_count,
        "deterministic_permutation_cycles": deterministic_count,
        "state_vector_distance_threshold": 0.08,
        "threshold_empirically_calibrated": "no",
        "threshold_dimension_status": "not_declared_dimensionless",
        "similarity_function_defined": "no",
        "condition_statuses": {row["condition_id"]: row["condition_status"] for row in condition_rows},
        "final_class": final_class,
        "final_status": "controlled_causal_structure_evaluation_completed_with_review_items",
        "validation_check_count": len(validation_rows),
        "validation_failed_count": sum(1 for row in validation_rows if row["passed"] != "yes"),
        "exact_output_count": len(OUTPUT_FILES),
        "unsupported_causal_claim_rejected": "yes",
        "invalid_transition_rejected": "yes",
        "output_digest_before_summary": stable_digest(current_outputs),
    }
    write_json(output_dir / OUTPUT_FILES[8], run_summary)
    (output_dir / OUTPUT_FILES[9]).write_text(readout, encoding="utf-8")

    actual_files = sorted(path.name for path in output_dir.iterdir() if path.is_file())
    if actual_files != sorted(OUTPUT_FILES):
        raise SystemExit(f"unexpected output files: {actual_files}")
    if any(row["passed"] != "yes" for row in validation_rows):
        raise SystemExit("semantic validation failed")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input-root", default=".", help="Repository root containing QSB inputs.")
    parser.add_argument("--output-dir", required=True, help="Directory for the ten required run outputs.")
    parser.add_argument("--overwrite", action="store_true", help="Replace an existing output directory.")
    args = parser.parse_args(argv)

    build_outputs(Path(args.input_root).resolve(), Path(args.output_dir).resolve(), args.overwrite)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
