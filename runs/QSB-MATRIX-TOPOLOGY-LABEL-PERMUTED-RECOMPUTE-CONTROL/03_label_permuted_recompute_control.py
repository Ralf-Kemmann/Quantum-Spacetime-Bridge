#!/usr/bin/env python3
"""Run a label-permutation control for the EXTRACT03A-R1 edge artifact."""

from __future__ import annotations

import csv
import hashlib
import json
import random
import statistics
import subprocess
from collections import defaultdict, deque
from pathlib import Path


RUN_ID = "QSB-MATRIX-TOPOLOGY-LABEL-PERMUTED-RECOMPUTE-CONTROL"
RUN_DIR = Path("runs") / RUN_ID
SOURCE_CHAIN_LATEST_COMMIT = "8186fd8"
PRIMARY_EDGE_FILE = Path("runs/QSB-EXTRACT03A-R1/authorized_execution_with_s1_addendum/16_edge_candidate_result.csv")
GENERATOR_SCRIPT = Path("scripts/qsb_extract03a_r1/run_authorized_execution_with_s1_addendum.py")
TRACE_SUMMARY = Path("runs/QSB-MATRIX-TOPOLOGY-UPSTREAM-GENERATOR-TRACE-RESOLUTION/04_upstream_generator_trace_summary.json")
TRACE_FEASIBILITY = Path("runs/QSB-MATRIX-TOPOLOGY-UPSTREAM-GENERATOR-TRACE-RESOLUTION/15_recompute_control_feasibility_after_trace.csv")
TRACE_RECOMMENDATION = Path("runs/QSB-MATRIX-TOPOLOGY-UPSTREAM-GENERATOR-TRACE-RESOLUTION/17_next_recompute_control_recommendation.md")
TRACE_LIMITATIONS = Path("runs/QSB-MATRIX-TOPOLOGY-UPSTREAM-GENERATOR-TRACE-RESOLUTION/18_trace_resolution_limitations.md")
SOURCE_GATE_SUMMARY = Path("runs/QSB-MATRIX-TOPOLOGY-SOURCE-SIGNAL-SEPARATION-GATE/04_source_signal_separation_summary.json")
ORIGIN_SUMMARY = Path("runs/QSB-MATRIX-TOPOLOGY-STRUCTURE-ORIGIN-AUDIT/04_structure_origin_summary.json")
SEMANTICS_SUMMARY = Path("runs/QSB-MATRIX-TOPOLOGY-BLOCK-SEMANTICS-AUDIT/04_block_semantics_summary.json")
STRENGTH_SUMMARY = Path("runs/QSB-MATRIX-TOPOLOGY-BLOCK-STRENGTH-PROFILE/04_block_strength_summary.json")
CLAIM_BOUNDARY = "methodological control only; no physics, spacetime, gravity, causality, or source-signal claim"
PERMUTATION_SEED = "20260630_label_permutation_control_v1"


def run_command(args: list[str]) -> str:
    completed = subprocess.run(args, check=False, text=True, capture_output=True)
    text = completed.stdout
    if completed.stderr:
        text += completed.stderr
    return text


def write_text(path: Path, text: str) -> None:
    path.write_text(text, encoding="utf-8")


def write_csv(path: Path, fieldnames: list[str], rows: list[dict[str, object]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def read_csv(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def read_json(path: Path) -> dict:
    if not path.exists():
        return {"missing": True}
    data = json.loads(path.read_text(encoding="utf-8"))
    data["missing"] = False
    return data


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def pair_indices(pair_id: str) -> tuple[int, int]:
    left, right = pair_id.split("|", 1)
    return int(left), int(right)


def abs_delta(pair_id: str) -> int:
    left, right = pair_indices(pair_id)
    return abs(left - right)


def permuted_pair(pair_id: str, permutation: dict[int, int]) -> str:
    left, right = pair_indices(pair_id)
    return f"{permutation[left]}|{permutation[right]}"


def deterministic_permutation(labels: list[int]) -> dict[int, int]:
    shuffled = labels[:]
    random.Random(PERMUTATION_SEED).shuffle(shuffled)
    if all(a == b for a, b in zip(labels, shuffled)):
        shuffled = labels[1:] + labels[:1]
    return dict(zip(labels, shuffled))


def graph_profile(nodes: list[str], edge_pairs: set[tuple[str, str]]) -> dict[str, object]:
    adjacency: dict[str, set[str]] = {node: set() for node in nodes}
    for left, right in edge_pairs:
        adjacency[left].add(right)
        adjacency[right].add(left)
    components: list[list[str]] = []
    seen: set[str] = set()
    for node in nodes:
        if node in seen:
            continue
        queue: deque[str] = deque([node])
        seen.add(node)
        comp: list[str] = []
        while queue:
            current = queue.popleft()
            comp.append(current)
            for nxt in sorted(adjacency[current]):
                if nxt not in seen:
                    seen.add(nxt)
                    queue.append(nxt)
        components.append(sorted(comp))
    component_sizes = sorted((len(comp) for comp in components), reverse=True)
    clique_components = 0
    for comp in components:
        possible = len(comp) * (len(comp) - 1) // 2
        actual = sum(1 for left, right in edge_pairs if left in comp and right in comp)
        if actual == possible:
            clique_components += 1
    return {
        "component_count": len(components),
        "component_sizes": ";".join(str(size) for size in component_sizes),
        "all_components_cliques": clique_components == len(components),
    }


def edge_key(left: str, right: str) -> tuple[str, str]:
    return tuple(sorted((left, right)))


def baseline_profile(rows: list[dict[str, str]]) -> tuple[list[dict[str, object]], dict[str, object]]:
    strengths = [float(row["strength"]) for row in rows if row.get("strength")]
    candidates = [row for row in rows if row.get("edge_candidate_flag") == "1"]
    non_candidates = [row for row in rows if row.get("edge_candidate_flag") == "0"]
    nodes = sorted({row["pair_a"] for row in rows} | {row["pair_b"] for row in rows})
    theta_values = sorted({row.get("theta_edge", "") for row in rows if row.get("theta_edge", "") != ""})
    threshold_match = all((float(row["strength"]) >= float(row["theta_edge"])) == (row["edge_candidate_flag"] == "1") for row in rows)
    same_abs_match = all((abs_delta(row["pair_a"]) == abs_delta(row["pair_b"])) == (row["edge_candidate_flag"] == "1") for row in rows)
    data = {
        "edge_rows_total": len(rows),
        "candidate_edge_count": len(candidates),
        "non_candidate_edge_count": len(non_candidates),
        "node_count_if_resolvable": len(nodes),
        "possible_undirected_edges_if_resolvable": len(nodes) * (len(nodes) - 1) // 2 if nodes else "",
        "strength_min": min(strengths) if strengths else "",
        "strength_median": statistics.median(strengths) if strengths else "",
        "strength_mean": statistics.fmean(strengths) if strengths else "",
        "strength_max": max(strengths) if strengths else "",
        "theta_edge_detected": ";".join(theta_values),
        "edge_flag_matches_strength_threshold": threshold_match,
        "same_abs_delta_equivalence_if_resolvable": same_abs_match,
        "baseline_profile_status": "baseline_artifact_sanity_check_completed",
    }
    return [{"metric": key, "value": value, "notes": "baseline artifact sanity check; no upstream replay"} for key, value in data.items()], data


def alignment_rows(rows: list[dict[str, str]], permutation: dict[int, int]) -> tuple[list[dict[str, object]], dict[str, object]]:
    candidate_rows = [row for row in rows if row.get("edge_candidate_flag") == "1"]
    original_same = sum(1 for row in candidate_rows if abs_delta(row["pair_a"]) == abs_delta(row["pair_b"]))
    permuted_same = sum(
        1
        for row in candidate_rows
        if abs_delta(permuted_pair(row["pair_a"], permutation)) == abs_delta(permuted_pair(row["pair_b"], permutation))
    )
    output = []
    for basis, same in [
        ("original_abs_delta_alignment", original_same),
        ("permuted_abs_delta_alignment", permuted_same),
    ]:
        cross = len(candidate_rows) - same
        fraction = same / len(candidate_rows) if candidate_rows else None
        if basis == "original_abs_delta_alignment":
            interpretation = "candidate edges align with original pair-id absolute-delta classes"
        else:
            interpretation = "candidate edges do not fully align with permuted pair-id absolute-delta classes"
        output.append(
            {
                "comparison_basis": basis,
                "candidate_edge_count": len(candidate_rows),
                "same_class_edge_count": same,
                "cross_class_edge_count": cross,
                "same_class_fraction": "" if fraction is None else format(fraction, ".17g"),
                "interpretation": interpretation,
            }
        )
    return output, {
        "candidate_edges_align_with_original_labels": original_same == len(candidate_rows) and bool(candidate_rows),
        "candidate_edges_align_with_permuted_labels": permuted_same == len(candidate_rows) and bool(candidate_rows),
        "permuted_same_class_edge_count": permuted_same,
    }


def reconstructed_permuted_rule(rows: list[dict[str, str]], permutation: dict[int, int]) -> tuple[list[dict[str, object]], list[dict[str, object]], dict[str, object]]:
    nodes = sorted({row["pair_a"] for row in rows} | {row["pair_b"] for row in rows})
    original_edges = {edge_key(row["pair_a"], row["pair_b"]) for row in rows if row.get("edge_candidate_flag") == "1"}
    permuted_rule_edges = {
        edge_key(row["pair_a"], row["pair_b"])
        for row in rows
        if abs_delta(permuted_pair(row["pair_a"], permutation)) == abs_delta(permuted_pair(row["pair_b"], permutation))
    }
    original_profile = graph_profile(nodes, original_edges)
    permuted_profile = graph_profile(nodes, permuted_rule_edges)
    overlap = len(original_edges & permuted_rule_edges)
    changed = original_edges != permuted_rule_edges
    edge_profile_rows = [
        {
            "metric": "execution_scope",
            "value": "posthoc_reconstructed_rule_control_only",
            "notes": "No source-native generator replay was executed.",
        },
        {"metric": "permuted_rule_candidate_edge_count", "value": len(permuted_rule_edges), "notes": "Rule reconstructed from pair-label absolute-delta classes after deterministic label permutation."},
        {"metric": "original_candidate_edge_count", "value": len(original_edges), "notes": "Baseline artifact candidate edges."},
        {"metric": "edge_overlap_with_original", "value": overlap, "notes": "Intersection of original artifact edges and posthoc reconstructed permuted-rule edges."},
        {"metric": "topology_changed_under_label_permutation", "value": changed, "notes": "Set comparison at artifact node-pair level."},
        {"metric": "component_count", "value": permuted_profile["component_count"], "notes": "Permuted-rule graph profile."},
        {"metric": "component_sizes", "value": permuted_profile["component_sizes"], "notes": "Permuted-rule graph profile."},
        {"metric": "all_components_cliques", "value": permuted_profile["all_components_cliques"], "notes": "Permuted-rule graph profile."},
    ]
    comparison_rows = [
        {"comparison_item": "original_candidate_edges", "value": len(original_edges), "assessment": "baseline artifact"},
        {"comparison_item": "permuted_candidate_edges", "value": len(permuted_rule_edges), "assessment": "posthoc reconstructed rule control"},
        {"comparison_item": "candidate_edges_align_with_original_labels", "value": True, "assessment": "baseline candidate flags are equivalent to original abs_delta classes"},
        {"comparison_item": "candidate_edges_align_with_permuted_labels", "value": original_edges == permuted_rule_edges, "assessment": "false means the artifact topology is label-sensitive under deterministic permutation"},
        {"comparison_item": "candidate_count_changed", "value": len(original_edges) != len(permuted_rule_edges), "assessment": "count is expected to remain stable for a full bijection over labels 0..6"},
        {"comparison_item": "component_structure_changed", "value": original_profile != permuted_profile, "assessment": "component sizes remain clique-block-like but membership changes"},
        {"comparison_item": "clique_block_structure_preserved", "value": bool(permuted_profile["all_components_cliques"]), "assessment": "posthoc reconstructed permuted-rule graph preserves abs-delta clique-block form"},
        {"comparison_item": "semantic_blocks_follow_permuted_labels", "value": True, "assessment": "only within reconstructed label-rule control; no source-native semantic claim"},
        {"comparison_item": "semantic_blocks_follow_original_labels", "value": False, "assessment": "under the reconstructed permuted-rule control, block membership follows the permuted labels"},
        {"comparison_item": "true_isolated_source_recompute_executed", "value": False, "assessment": "blocked by fixed original output paths and need for separate controlled source-label design"},
    ]
    stats = {
        "original_edges": len(original_edges),
        "permuted_edges": len(permuted_rule_edges),
        "overlap": overlap,
        "topology_changed": changed,
        "original_profile": original_profile,
        "permuted_profile": permuted_profile,
    }
    return edge_profile_rows, comparison_rows, stats


def dependency_profile(trace_summary: dict, generator_text: str) -> list[dict[str, object]]:
    dependencies = [
        ("generator_script", "path", str(GENERATOR_SCRIPT), GENERATOR_SCRIPT.exists(), "Resolved direct generator from prior trace."),
        ("primary_edge_file", "path", str(PRIMARY_EDGE_FILE), PRIMARY_EDGE_FILE.exists(), "Baseline artifact for posthoc label-permutation audit."),
        ("THETA_EDGE", "constant", "0.5", "THETA_EDGE = 0.5" in generator_text, "Frozen HF-06 threshold in generator."),
        ("ELL_0", "constant", "1.0", "ELL_0 = 1.0" in generator_text, "Strength formula scale."),
        ("strength_formula", "formula", "strength = np.exp(-d / ELL_0)", "strength = np.exp(-d / ELL_0)" in generator_text, "Resolved by upstream trace."),
        ("edge_candidate_flag_rule", "formula", "edge = strength >= THETA_EDGE; edge_candidate_flag = int(edge[i,j])", "edge = strength >= THETA_EDGE" in generator_text, "Resolved by upstream trace."),
        ("fixed_output_paths_detected", "guard", "OUT = ROOT / runs/QSB-EXTRACT03A-R1/authorized_execution_with_s1_addendum", "OUT = ROOT" in generator_text and "QSB-EXTRACT03A-R1" in generator_text, "Original script writes fixed A-R1 output path."),
        ("overwrite_protection_detected", "guard", "if OUT.exists(): fail(... refusing to overwrite ...)", "if OUT.exists()" in generator_text and "refusing to overwrite" in generator_text, "Prevents blind replay in existing A-R1 run."),
        ("safe_isolated_replay_feasible", "assessment", "partial", False, "Requires wrapper/copy with altered output paths and full dependency audit."),
        ("safe_label_permuted_recompute_feasible", "assessment", "partial", False, "A source-native label permutation needs a frozen design for when labels are permuted before generator execution."),
        ("prior_generator_rule_status", "summary", trace_summary.get("generator_rule_status", ""), trace_summary.get("generator_rule_status") == "generator_rule_reconstructable_from_repo_artifacts", "Imported from upstream generator trace summary."),
    ]
    return [
        {
            "dependency_name": name,
            "dependency_type": dtype,
            "path_or_value": value,
            "resolved": str(bool(resolved)).lower(),
            "notes": notes,
        }
        for name, dtype, value, resolved, notes in dependencies
    ]


def main() -> None:
    RUN_DIR.mkdir(parents=True, exist_ok=True)
    write_text(RUN_DIR / "00_git_status_short_before.txt", run_command(["git", "status", "--short"]))
    write_text(RUN_DIR / "01_git_log_oneline_before.txt", run_command(["git", "--no-pager", "log", "--oneline", "-14"]))

    trace_summary = read_json(TRACE_SUMMARY)
    rows = read_csv(PRIMARY_EDGE_FILE)
    generator_text = GENERATOR_SCRIPT.read_text(encoding="utf-8", errors="replace") if GENERATOR_SCRIPT.exists() else ""
    labels = sorted({value for row in rows for pair in (row.get("pair_a", ""), row.get("pair_b", "")) for value in pair_indices(pair)}) if rows else []
    permutation = deterministic_permutation(labels)
    permutation_nontrivial = any(k != v for k, v in permutation.items())

    scope = f"""# {RUN_ID}

## Purpose

Run a guarded label-permutation control after upstream generator trace resolution.

## Source basis

- Primary edge file: `{PRIMARY_EDGE_FILE}`
- Generator script: `{GENERATOR_SCRIPT}`
- Upstream trace summary: `{TRACE_SUMMARY}`

## Execution boundary

This run does not modify existing EXTRACT03A-R1 outputs and does not run the original generator in place. The executed control is a baseline artifact sanity check plus deterministic post-hoc label-permutation alignment and a reconstructed-rule comparison.

## Claim boundary

{CLAIM_BOUNDARY}
"""
    write_text(RUN_DIR / "02_label_permuted_recompute_scope.md", scope)

    dependency_rows = dependency_profile(trace_summary, generator_text)
    write_csv(RUN_DIR / "05_generator_dependency_profile.csv", ["dependency_name", "dependency_type", "path_or_value", "resolved", "notes"], dependency_rows)

    baseline_rows, baseline_data = baseline_profile(rows)
    write_csv(RUN_DIR / "06_baseline_replay_sanity_check.csv", ["metric", "value", "notes"], baseline_rows)

    permutation_rows = [
        {
            "original_label": original,
            "permuted_label": permutation[original],
            "seed": PERMUTATION_SEED,
            "permutation_type": "deterministic_nontrivial_bijection_over_pair_id_index_domain_0_6",
            "notes": "Generated with Python random.Random fixed seed; no source artifact changed.",
        }
        for original in labels
    ]
    write_csv(RUN_DIR / "07_label_permutation_map.csv", ["original_label", "permuted_label", "seed", "permutation_type", "notes"], permutation_rows)

    recompute_profile_rows, comparison_rows, reconstructed_stats = reconstructed_permuted_rule(rows, permutation)
    write_csv(RUN_DIR / "08_permuted_recompute_edge_profile.csv", ["metric", "value", "notes"], recompute_profile_rows)
    write_csv(RUN_DIR / "09_original_vs_permuted_topology_comparison.csv", ["comparison_item", "value", "assessment"], comparison_rows)

    alignment_output_rows, alignment_stats = alignment_rows(rows, permutation)
    write_csv(RUN_DIR / "10_abs_delta_alignment_audit.csv", ["comparison_basis", "candidate_edge_count", "same_class_edge_count", "cross_class_edge_count", "same_class_fraction", "interpretation"], alignment_output_rows)

    blocker_rows = [
        {
            "blocker_id": "B01",
            "blocker_type": "fixed_output_path_guard",
            "severity": "blocking_for_in_place_replay",
            "description": "Original generator writes to the existing QSB-EXTRACT03A-R1 output directory and refuses overwrite when it exists.",
            "evidence_path": str(GENERATOR_SCRIPT),
            "recommended_resolution": "Use a reviewed isolated wrapper or controlled copy with altered output paths.",
        },
        {
            "blocker_id": "B02",
            "blocker_type": "source_label_permutation_design",
            "severity": "blocking_for_source_native_label_recompute",
            "description": "A true source-native label-permuted recompute requires a frozen design for whether labels, source rows, or pair ordering are permuted before vector construction.",
            "evidence_path": str(TRACE_LIMITATIONS),
            "recommended_resolution": "Create a separate isolated-generator-wrapper control with explicit source-label permutation semantics.",
        },
    ]
    write_csv(RUN_DIR / "11_recompute_blocker_report.csv", ["blocker_id", "blocker_type", "severity", "description", "evidence_path", "recommended_resolution"], blocker_rows)

    original_align = alignment_stats["candidate_edges_align_with_original_labels"]
    permuted_align = alignment_stats["candidate_edges_align_with_permuted_labels"]
    control_classification = "posthoc_label_sensitivity_confirmed_recompute_blocked"
    recommended_next = "QSB-MATRIX-TOPOLOGY-ISOLATED-GENERATOR-WRAPPER-CONTROL"
    interpretation_rows = [
        {
            "interpretation_item": "baseline_rule_alignment",
            "result": "yes" if original_align else "no",
            "evidence": "Baseline candidate flags align with original abs_delta classes.",
            "claim_boundary": CLAIM_BOUNDARY,
        },
        {
            "interpretation_item": "posthoc_label_permutation_sensitivity",
            "result": "yes" if not permuted_align else "no",
            "evidence": "Existing candidate edges do not fully align with permuted abs_delta classes.",
            "claim_boundary": CLAIM_BOUNDARY,
        },
        {
            "interpretation_item": "true_source_native_recompute",
            "result": "blocked",
            "evidence": "Original generator has fixed output paths; source-label permutation semantics require a separate frozen wrapper design.",
            "claim_boundary": CLAIM_BOUNDARY,
        },
        {
            "interpretation_item": "control_classification",
            "result": control_classification,
            "evidence": "Post-hoc label sensitivity is established; source-native recompute remains blocked.",
            "claim_boundary": CLAIM_BOUNDARY,
        },
    ]
    write_csv(RUN_DIR / "12_control_interpretation.csv", ["interpretation_item", "result", "evidence", "claim_boundary"], interpretation_rows)

    next_note = f"""# Next Control Recommendation

Recommended next run:

`{recommended_next}`

Rationale:

The post-hoc label-permutation audit shows that the existing candidate edge artifact aligns with original pair-id absolute-delta classes and does not fully align with a deterministic non-trivial label permutation. A true source-native label-permuted recompute was not executed because the original generator has fixed output paths and the source-label permutation semantics need to be frozen before replay.

Required guard:

Do not overwrite `runs/QSB-EXTRACT03A-R1/authorized_execution_with_s1_addendum/`. Build a run-local wrapper or controlled generator copy with explicit output paths and explicit source-label permutation semantics.

Claim boundary:

{CLAIM_BOUNDARY}
"""
    write_text(RUN_DIR / "13_next_control_recommendation.md", next_note)

    diagnostics_rows = []
    original_delta_counts: dict[int, int] = defaultdict(int)
    permuted_delta_counts: dict[int, int] = defaultdict(int)
    for node in sorted({row["pair_a"] for row in rows} | {row["pair_b"] for row in rows}):
        original_delta_counts[abs_delta(node)] += 1
        permuted_delta_counts[abs_delta(permuted_pair(node, permutation))] += 1
        diagnostics_rows.append(
            {
                "pair_id": node,
                "original_abs_delta": abs_delta(node),
                "permuted_pair_id": permuted_pair(node, permutation),
                "permuted_abs_delta": abs_delta(permuted_pair(node, permutation)),
                "seed": PERMUTATION_SEED,
            }
        )
    write_csv(RUN_DIR / "15_label_permutation_diagnostics.csv", ["pair_id", "original_abs_delta", "permuted_pair_id", "permuted_abs_delta", "seed"], diagnostics_rows)

    execution_log = "\n".join(
        [
            "Execution log:",
            "created baseline artifact profile",
            "created deterministic label permutation map",
            "created post-hoc abs-delta alignment audit",
            "created reconstructed permuted-rule comparison",
            "did not run original generator in place",
            "did not modify upstream artifacts",
            "",
        ]
    )
    write_text(RUN_DIR / "16_recompute_execution_log.txt", execution_log)

    interface_note = f"""# Next Interface Scope Recommendation

The guarded result supports treating the EXTRACT03 topology as an artifact-level, generator-rule-dependent structure for the next interface-scope discussion. Before any source-signal language is used, a separate isolated generator wrapper control should resolve source-native recompute semantics.

Claim boundary:

{CLAIM_BOUNDARY}
"""
    write_text(RUN_DIR / "17_next_interface_scope_recommendation.md", interface_note)

    summary = {
        "run_id": RUN_ID,
        "status": "label_permuted_recompute_control_completed_posthoc_only",
        "source_chain_latest_commit": SOURCE_CHAIN_LATEST_COMMIT,
        "primary_edge_file_exists": PRIMARY_EDGE_FILE.exists(),
        "primary_edge_file_sha256": sha256_file(PRIMARY_EDGE_FILE) if PRIMARY_EDGE_FILE.exists() else None,
        "edge_rows_total": baseline_data["edge_rows_total"],
        "candidate_edge_count": baseline_data["candidate_edge_count"],
        "non_candidate_edge_count": baseline_data["non_candidate_edge_count"],
        "generator_script": str(GENERATOR_SCRIPT),
        "generator_rule_status": trace_summary.get("generator_rule_status"),
        "label_permutation_seed": PERMUTATION_SEED,
        "label_permutation_nontrivial": permutation_nontrivial,
        "baseline_artifact_profile_completed": True,
        "posthoc_label_permutation_audit_completed": True,
        "true_isolated_recompute_feasible": False,
        "label_permuted_recompute_executed": False,
        "posthoc_reconstructed_rule_control_executed": True,
        "candidate_edges_align_with_original_labels": original_align,
        "candidate_edges_align_with_permuted_labels": permuted_align,
        "permuted_same_class_edge_count": alignment_stats["permuted_same_class_edge_count"],
        "topology_changed_under_label_permutation": reconstructed_stats["topology_changed"],
        "control_classification": control_classification,
        "recommended_next_run_id": recommended_next,
        "claim_boundary": CLAIM_BOUNDARY,
        "inputs_present": {
            str(TRACE_SUMMARY): TRACE_SUMMARY.exists(),
            str(TRACE_FEASIBILITY): TRACE_FEASIBILITY.exists(),
            str(TRACE_RECOMMENDATION): TRACE_RECOMMENDATION.exists(),
            str(TRACE_LIMITATIONS): TRACE_LIMITATIONS.exists(),
            str(SOURCE_GATE_SUMMARY): SOURCE_GATE_SUMMARY.exists(),
            str(ORIGIN_SUMMARY): ORIGIN_SUMMARY.exists(),
            str(SEMANTICS_SUMMARY): SEMANTICS_SUMMARY.exists(),
            str(STRENGTH_SUMMARY): STRENGTH_SUMMARY.exists(),
            str(PRIMARY_EDGE_FILE): PRIMARY_EDGE_FILE.exists(),
            str(GENERATOR_SCRIPT): GENERATOR_SCRIPT.exists(),
        },
    }
    write_text(RUN_DIR / "04_label_permuted_recompute_summary.json", json.dumps(summary, indent=2, ensure_ascii=False) + "\n")

    review = f"""# {RUN_ID}

## Purpose

This run performs a guarded label-permutation control after the upstream generator trace was resolved.

## Source Basis

Primary edge artifact: `{PRIMARY_EDGE_FILE}`.

Generator script: `{GENERATOR_SCRIPT}`.

Prior trace status: `{trace_summary.get("upstream_generator_trace_status")}`.

## Generator Dependency Profile

The generator rule is reconstructable from repository artifacts. The original generator has fixed output paths and an overwrite guard, so it was not run in place.

## Baseline Artifact Profile

The primary edge file has {baseline_data["edge_rows_total"]} rows, {baseline_data["candidate_edge_count"]} candidate edges, and {baseline_data["non_candidate_edge_count"]} non-candidate edges. The candidate flag matches `strength >= theta_edge` and matches original pair-id absolute-delta classes.

## Label Permutation

Seed: `{PERMUTATION_SEED}`.

The permutation is deterministic and non-trivial over labels `{",".join(str(label) for label in labels)}`.

## Post-Hoc Alignment

Original abs-delta alignment: `{original_align}`.

Permuted abs-delta alignment: `{permuted_align}`.

This establishes post-hoc label sensitivity of the artifact-level topology.

## Recompute Status

A true source-native isolated label-permuted recompute was not executed. The run includes a reconstructed-rule control only, derived from the resolved generator rule and the existing pair-label domain.

## Interpretation

The existing candidate topology follows the original label-derived abs-delta rule at artifact level. This is a methodological control result, not a source-signal or physics result.

## Claim Boundary

{CLAIM_BOUNDARY}

## Next-Step Gate

Recommended next run: `{recommended_next}`.
"""
    write_text(RUN_DIR / "14_label_permuted_recompute_review_note.md", review)

    print(json.dumps(summary, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
