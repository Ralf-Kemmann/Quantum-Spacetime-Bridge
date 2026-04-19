#!/usr/bin/env python3
from __future__ import annotations

import argparse
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from statistics import mean, median
from typing import Any

import yaml

from loader import ExportClassData, load_export_class_data
from neighborhoods import NeighborhoodGraph, build_neighborhood_graph
from reporting import (
    write_csv,
    write_json,
    class_mode_to_row,
    comparison_to_row,
    graph_stats_row,
    shell_stats_row,
    write_block_readout,
)


# ============================================================================
# Data containers
# ============================================================================

@dataclass(slots=True)
class ShellRecord:
    shell_id: str
    center_id: str
    member_ids: list[str]
    neighbor_count: int
    valid: bool


@dataclass(slots=True)
class A1Result:
    score: float | None
    status: str
    late_stage: bool


@dataclass(slots=True)
class B1Result:
    score: float | None
    status: str


@dataclass(slots=True)
class ClassModeResult:
    export_class: str
    neighborhood_mode: str
    launchable: bool
    pair_unit_count: int
    shell_count: int
    mean_neighbor_count: float
    median_neighbor_count: float | None
    max_neighbor_count: int | None
    connected_component_count: int
    largest_component_size: int
    a1_score_mean: float | None
    a1_score_median: float | None
    a1_status: str
    b1_score_mean: float | None
    b1_score_median: float | None
    b1_status: str
    combined_status: str
    notes: str = ""


@dataclass(slots=True)
class ClassComparisonResult:
    export_class: str
    baseline_mode: str
    alternative_mode: str
    baseline_launchable: bool
    alternative_launchable: bool
    delta_launchable: str
    baseline_shell_count: int
    alternative_shell_count: int
    delta_shell_count: int
    baseline_mean_neighbor_count: float
    alternative_mean_neighbor_count: float
    delta_mean_neighbor_count: float
    baseline_a1_status: str
    alternative_a1_status: str
    delta_a1_status: str
    baseline_b1_status: str
    alternative_b1_status: str
    delta_b1_status: str
    baseline_combined_status: str
    alternative_combined_status: str
    delta_combined_status: str
    interpretation_flag: str
    comment: str = ""


# ============================================================================
# Helpers
# ============================================================================

def load_yaml(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        data = yaml.safe_load(handle)
    if not isinstance(data, dict):
        raise ValueError(f"YAML root must be a mapping: {path}")
    return data


def now_utc_iso() -> str:
    return (
        datetime.now(timezone.utc)
        .replace(microsecond=0)
        .isoformat()
        .replace("+00:00", "Z")
    )


def safe_mean(values: list[float]) -> float | None:
    return float(mean(values)) if values else None


def safe_median(values: list[float]) -> float | None:
    return float(median(values)) if values else None


# ============================================================================
# Shell construction
# ============================================================================

def build_shells(graph: NeighborhoodGraph) -> list[ShellRecord]:
    shells: list[ShellRecord] = []
    for node_id in graph.node_ids:
        neighbors = sorted(graph.adjacency.get(node_id, set()))
        shells.append(
            ShellRecord(
                shell_id=f"shell::{node_id}",
                center_id=node_id,
                member_ids=neighbors,
                neighbor_count=len(neighbors),
                valid=len(neighbors) > 0,
            )
        )
    return shells


# ============================================================================
# A1 / B1 stubs
# Replace later with real project logic if needed.
# ============================================================================

def compute_a1_for_shell(shell: ShellRecord, cfg_a1: dict[str, Any]) -> A1Result:
    if not shell.valid:
        return A1Result(score=None, status="not_applicable", late_stage=False)

    neighbor_min = int(cfg_a1["neighbor_min"])
    stabilization_ceiling = float(cfg_a1["stabilization_ceiling"])

    score = min(1.0, shell.neighbor_count / max(neighbor_min + 1, 1))
    late_stage = (score >= stabilization_ceiling) and (shell.neighbor_count >= neighbor_min)

    if score >= 0.95:
        status = "active"
    elif score >= 0.60:
        status = "partial"
    elif score > 0.0:
        status = "weak"
    else:
        status = "inactive"

    return A1Result(score=score, status=status, late_stage=late_stage)


def compute_b1_for_shell(shell: ShellRecord, cfg_b1: dict[str, Any]) -> B1Result:
    if not shell.valid:
        return B1Result(score=None, status="not_applicable")

    penalty = float(cfg_b1["conflict_penalty"])
    score = min(2.0, shell.neighbor_count / penalty)

    if score >= 1.5:
        status = "active"
    elif score >= 0.75:
        status = "partial"
    elif score > 0.0:
        status = "weak"
    else:
        status = "inactive"

    return B1Result(score=score, status=status)


# ============================================================================
# Aggregation
# ============================================================================

def classify_activity(statuses: list[str]) -> str:
    if not statuses:
        return "not_applicable"
    if all(s == "not_applicable" for s in statuses):
        return "not_applicable"
    if any(s == "active" for s in statuses):
        return "active"
    if any(s == "partial" for s in statuses):
        return "partial"
    if any(s == "weak" for s in statuses):
        return "weak"
    return "inactive"


def combined_status_from_result(launchable: bool, a1_status: str, b1_status: str) -> str:
    if not launchable:
        return "boundary_non_launchable"
    if a1_status == "active" and b1_status == "active":
        return "robust_dual"
    if a1_status in {"active", "partial", "weak"} or b1_status in {"active", "partial"}:
        return "structured_intermediate"
    if a1_status == "weak" or b1_status == "weak":
        return "weak_launchable_boundary"
    return "inconclusive"


def evaluate_mode(
    export_data: ExportClassData,
    neighborhood_mode: str,
    cfg: dict[str, Any],
) -> tuple[ClassModeResult, NeighborhoodGraph, list[ShellRecord], int]:
    graph = build_neighborhood_graph(export_data.pair_units, neighborhood_mode)
    shells = build_shells(graph)

    min_pair_units = int(cfg["decision"]["launchability"]["min_pair_units"])
    min_local_shells = int(cfg["decision"]["launchability"]["min_local_shells"])

    valid_shells = [s for s in shells if s.valid]
    launchable = (
        len(export_data.pair_units) >= min_pair_units
        and len(valid_shells) >= min_local_shells
    )

    a1_results: list[A1Result] = []
    b1_results: list[B1Result] = []

    if launchable:
        for shell in valid_shells:
            a1_results.append(compute_a1_for_shell(shell, cfg["a1"]))
            b1_results.append(compute_b1_for_shell(shell, cfg["b1"]))

    a1_scores = [r.score for r in a1_results if r.score is not None]
    b1_scores = [r.score for r in b1_results if r.score is not None]

    a1_status = classify_activity([r.status for r in a1_results]) if launchable else "not_applicable"
    b1_status = classify_activity([r.status for r in b1_results]) if launchable else "not_applicable"

    neighbor_counts = [s.neighbor_count for s in shells]
    late_stage_count = sum(1 for r in a1_results if r.late_stage)

    result = ClassModeResult(
        export_class=export_data.export_class,
        neighborhood_mode=neighborhood_mode,
        launchable=launchable,
        pair_unit_count=len(export_data.pair_units),
        shell_count=len(valid_shells),
        mean_neighbor_count=float(mean(neighbor_counts)) if neighbor_counts else 0.0,
        median_neighbor_count=float(median(neighbor_counts)) if neighbor_counts else None,
        max_neighbor_count=max(neighbor_counts) if neighbor_counts else None,
        connected_component_count=len(graph.connected_components),
        largest_component_size=graph.largest_component_size,
        a1_score_mean=safe_mean(a1_scores),
        a1_score_median=safe_median(a1_scores),
        a1_status=a1_status,
        b1_score_mean=safe_mean(b1_scores),
        b1_score_median=safe_median(b1_scores),
        b1_status=b1_status,
        combined_status=combined_status_from_result(launchable, a1_status, b1_status),
        notes="",
    )
    return result, graph, shells, late_stage_count


# ============================================================================
# Comparison logic
# ============================================================================

STATUS_RANK = {
    "not_applicable": -1,
    "inactive": 0,
    "weak": 1,
    "partial": 2,
    "active": 3,
}

COMBINED_STATUS_RANK = {
    "boundary_non_launchable": 0,
    "weak_launchable_boundary": 1,
    "structured_intermediate": 2,
    "robust_dual": 3,
    "inconclusive": -1,
    "degenerate": -2,
}


def status_delta(before: str, after: str) -> str:
    if before == after:
        return "unchanged"
    if before == "not_applicable" and after != "not_applicable":
        return "from_not_applicable"
    if before != "not_applicable" and after == "not_applicable":
        return "to_not_applicable"
    if STATUS_RANK.get(after, -99) > STATUS_RANK.get(before, -99):
        return "strengthened"
    return "weakened"


def combined_status_delta(before: str, after: str) -> str:
    if before == after:
        return "unchanged"
    if before == "boundary_non_launchable" and after == "weak_launchable_boundary":
        return "boundary_relaxed"
    if after == "degenerate":
        return "degenerate"
    if abs(COMBINED_STATUS_RANK.get(after, 0) - COMBINED_STATUS_RANK.get(before, 0)) >= 2:
        return "major_change"
    return "minor_shift"


def launchable_delta(before: bool, after: bool) -> str:
    if before and after:
        return "same_true"
    if (not before) and (not after):
        return "same_false"
    if (not before) and after:
        return "to_true"
    return "to_false"


def interpretation_flag(baseline: ClassModeResult, alternative: ClassModeResult) -> str:
    delta = combined_status_delta(baseline.combined_status, alternative.combined_status)
    if delta == "unchanged":
        return "stable"
    if delta == "boundary_relaxed":
        return "boundary_relaxed"
    if delta == "major_change":
        return "major_change"
    if delta == "degenerate":
        return "degenerate"
    return "soft_shift"


def compare_modes(
    baseline: ClassModeResult,
    alternative: ClassModeResult,
) -> ClassComparisonResult:
    return ClassComparisonResult(
        export_class=baseline.export_class,
        baseline_mode=baseline.neighborhood_mode,
        alternative_mode=alternative.neighborhood_mode,
        baseline_launchable=baseline.launchable,
        alternative_launchable=alternative.launchable,
        delta_launchable=launchable_delta(baseline.launchable, alternative.launchable),
        baseline_shell_count=baseline.shell_count,
        alternative_shell_count=alternative.shell_count,
        delta_shell_count=alternative.shell_count - baseline.shell_count,
        baseline_mean_neighbor_count=baseline.mean_neighbor_count,
        alternative_mean_neighbor_count=alternative.mean_neighbor_count,
        delta_mean_neighbor_count=alternative.mean_neighbor_count - baseline.mean_neighbor_count,
        baseline_a1_status=baseline.a1_status,
        alternative_a1_status=alternative.a1_status,
        delta_a1_status=status_delta(baseline.a1_status, alternative.a1_status),
        baseline_b1_status=baseline.b1_status,
        alternative_b1_status=alternative.b1_status,
        delta_b1_status=status_delta(baseline.b1_status, alternative.b1_status),
        baseline_combined_status=baseline.combined_status,
        alternative_combined_status=alternative.combined_status,
        delta_combined_status=combined_status_delta(
            baseline.combined_status, alternative.combined_status
        ),
        interpretation_flag=interpretation_flag(baseline, alternative),
        comment="",
    )


def ordering_preserved(
    baseline_results: dict[str, ClassModeResult],
    alternative_results: dict[str, ClassModeResult],
) -> bool:
    expected = ["negative", "abs", "positive"]
    baseline_ranked = sorted(
        baseline_results.values(),
        key=lambda x: COMBINED_STATUS_RANK.get(x.combined_status, -99),
        reverse=True,
    )
    alternative_ranked = sorted(
        alternative_results.values(),
        key=lambda x: COMBINED_STATUS_RANK.get(x.combined_status, -99),
        reverse=True,
    )
    return (
        [x.export_class for x in baseline_ranked] == expected
        and [x.export_class for x in alternative_ranked] == expected
    )


def decide_block_judgement(
    baseline_results: dict[str, ClassModeResult],
    alternative_results: dict[str, ClassModeResult],
) -> tuple[str, str, dict[str, Any]]:
    negative_base = baseline_results["negative"]
    negative_alt = alternative_results["negative"]
    abs_base = baseline_results["abs"]
    abs_alt = alternative_results["abs"]
    positive_base = baseline_results["positive"]
    positive_alt = alternative_results["positive"]

    overall_preserved = ordering_preserved(baseline_results, alternative_results)

    all_baseline_non_launchable = all(not r.launchable for r in baseline_results.values())
    all_alternative_non_launchable = all(not r.launchable for r in alternative_results.values())

    total_baseline_shells = sum(r.shell_count for r in baseline_results.values())
    total_alternative_shells = sum(r.shell_count for r in alternative_results.values())

    any_pair_units_present = any(
        r.pair_unit_count > 0
        for r in list(baseline_results.values()) + list(alternative_results.values())
    )

    negative_destabilized = negative_alt.combined_status not in {
        "robust_dual",
        "structured_intermediate",
        "boundary_non_launchable",
        "weak_launchable_boundary",
        "inconclusive",
    }

    major_regime_break = (not overall_preserved) or negative_destabilized

    global_flags = {
        "negative_status_stable": negative_alt.combined_status == negative_base.combined_status,
        "abs_status_stable": abs_alt.combined_status == abs_base.combined_status,
        "positive_boundary_changed": positive_base.combined_status != positive_alt.combined_status,
        "overall_ordering_preserved": overall_preserved,
        "major_regime_break": major_regime_break,
    }

    if (
        overall_preserved
        and negative_alt.launchable
        and abs_alt.launchable
        and positive_alt.combined_status in {
            "boundary_non_launchable",
            "weak_launchable_boundary",
            "structured_intermediate",
        }
        and negative_alt.combined_status == "robust_dual"
    ):
        return (
            "supported",
            "Baseline ordering preserved under alternative neighborhood without loss of negative privileged status.",
            global_flags,
        )

    if (
        all_baseline_non_launchable
        and all_alternative_non_launchable
        and total_baseline_shells == 0
        and total_alternative_shells == 0
    ):
        return (
            "inconclusive",
            "No usable local shell structure was generated under either neighborhood; block is not interpretable as a regime failure.",
            global_flags,
        )

    if (
        all_baseline_non_launchable
        and all_alternative_non_launchable
        and any_pair_units_present
    ):
        return (
            "weak",
            "Pair-units are present but remain too sparse to produce launchable local shell structure under either neighborhood.",
            global_flags,
        )

    if overall_preserved and not major_regime_break:
        return (
            "partially_supported",
            "Ordering broadly preserved, but one or more class-level shifts are stronger than ideal.",
            global_flags,
        )

    if major_regime_break:
        return (
            "failed",
            "Alternative neighborhood breaks the expected regime ordering or destabilizes the negative reference class.",
            global_flags,
        )

    return (
        "inconclusive",
        "Run completed, but comparison does not support a clean judgement.",
        global_flags,
    )


# ============================================================================
# Summary assembly
# ============================================================================

def assemble_summary(
    cfg: dict[str, Any],
    export_root: Path,
    baseline_results: dict[str, ClassModeResult],
    alternative_results: dict[str, ClassModeResult],
    comparisons: dict[str, ClassComparisonResult],
    decision: str,
    short_reason: str,
    global_flags: dict[str, Any],
    input_file_counts: dict[str, int],
) -> dict[str, Any]:
    per_class: dict[str, Any] = {}

    for export_class in cfg["inputs"]["export_classes"]:
        b = baseline_results[export_class]
        a = alternative_results[export_class]
        c = comparisons[export_class]

        per_class[export_class] = {
            "baseline": {
                "launchable": b.launchable,
                "pair_unit_count": b.pair_unit_count,
                "shell_count": b.shell_count,
                "mean_neighbor_count": b.mean_neighbor_count,
                "median_neighbor_count": b.median_neighbor_count,
                "max_neighbor_count": b.max_neighbor_count,
                "connected_component_count": b.connected_component_count,
                "largest_component_size": b.largest_component_size,
                "a1_score_mean": b.a1_score_mean,
                "a1_score_median": b.a1_score_median,
                "a1_status": b.a1_status,
                "b1_score_mean": b.b1_score_mean,
                "b1_score_median": b.b1_score_median,
                "b1_status": b.b1_status,
                "combined_status": b.combined_status,
                "notes": b.notes,
            },
            "alternative": {
                "launchable": a.launchable,
                "pair_unit_count": a.pair_unit_count,
                "shell_count": a.shell_count,
                "mean_neighbor_count": a.mean_neighbor_count,
                "median_neighbor_count": a.median_neighbor_count,
                "max_neighbor_count": a.max_neighbor_count,
                "connected_component_count": a.connected_component_count,
                "largest_component_size": a.largest_component_size,
                "a1_score_mean": a.a1_score_mean,
                "a1_score_median": a.a1_score_median,
                "a1_status": a.a1_status,
                "b1_score_mean": a.b1_score_mean,
                "b1_score_median": a.b1_score_median,
                "b1_status": a.b1_status,
                "combined_status": a.combined_status,
                "notes": a.notes,
            },
            "comparison": {
                "delta_launchable": c.delta_launchable,
                "delta_shell_count": c.delta_shell_count,
                "delta_mean_neighbor_count": c.delta_mean_neighbor_count,
                "delta_a1_status": c.delta_a1_status,
                "delta_b1_status": c.delta_b1_status,
                "delta_combined_status": c.delta_combined_status,
                "interpretation_flag": c.interpretation_flag,
                "comment": c.comment,
            },
        }

    return {
        "run_id": cfg["run"]["run_id"],
        "block": "N1",
        "status": "completed",
        "timestamp_utc": now_utc_iso(),
        "seed": cfg["run"]["seed"],
        "inputs": {
            "export_root": str(export_root),
            "export_classes": cfg["inputs"]["export_classes"],
            "export_pattern": cfg["inputs"]["export_pattern"],
            "search_mode": cfg["inputs"].get("search_mode", "direct"),
            "input_file_counts": input_file_counts,
        },
        "baseline": {
            "neighborhood_mode": cfg["baseline"]["neighborhood"]["mode"],
            "directed": cfg["baseline"]["neighborhood"].get("directed", False),
        },
        "alternative": {
            "neighborhood_mode": cfg["alternative"]["neighborhood"]["mode"],
            "directed": cfg["alternative"]["neighborhood"].get("directed", False),
            "require_mutual": cfg["alternative"]["neighborhood"].get("require_mutual"),
        },
        "parameters": {
            "a1": {
                "stabilization_ceiling": cfg["a1"]["stabilization_ceiling"],
                "neighbor_min": cfg["a1"]["neighbor_min"],
                "late_stage_rule": cfg["a1"]["late_stage_rule"],
            },
            "b1": {
                "conflict_penalty": cfg["b1"]["conflict_penalty"],
            },
            "decision": {
                "min_pair_units": cfg["decision"]["launchability"]["min_pair_units"],
                "min_local_shells": cfg["decision"]["launchability"]["min_local_shells"],
            },
        },
        "per_class": per_class,
        "global_comparison": {
            **global_flags,
            "ordering_comment": short_reason,
        },
        "decision": {
            "block_judgement": decision,
            "short_reason": short_reason,
        },
        "validation": {
            "all_export_classes_present": all(v > 0 for v in input_file_counts.values()),
            "baseline_reproduces_expected_pattern": (
                baseline_results["negative"].launchable
                and baseline_results["abs"].launchable
                and not baseline_results["positive"].launchable
            ),
            "nan_metrics_detected": False,
            "empty_inputs_detected": any(v == 0 for v in input_file_counts.values()),
            "validation_notes": [],
        },
        "warnings": [],
        "open_points": [
            "Alternative neighborhood is operational, not yet physically privileged.",
            "Positive launchability under alternative rule does not by itself imply meaningful local structure.",
            "No claim about geometric emergence follows from this block alone.",
        ],
    }


# ============================================================================
# CLI
# ============================================================================

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run N1 alternative neighborhood comparison."
    )
    parser.add_argument(
        "--config",
        required=True,
        help="Path to config yaml",
    )
    return parser.parse_args()


# ============================================================================
# Main
# ============================================================================

def main() -> int:
    args = parse_args()
    cfg_path = Path(args.config).resolve()
    cfg = load_yaml(cfg_path)

    run_id = cfg["run"]["run_id"]
    output_dir = Path(cfg["run"]["output_dir"]).resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    export_root = Path(cfg["inputs"]["export_root"]).resolve()
    export_classes: list[str] = list(cfg["inputs"]["export_classes"])
    export_pattern = cfg["inputs"]["export_pattern"]
    search_mode = cfg["inputs"].get("search_mode", "direct")

    baseline_mode = cfg["baseline"]["neighborhood"]["mode"]
    alternative_mode = cfg["alternative"]["neighborhood"]["mode"]

    baseline_results: dict[str, ClassModeResult] = {}
    alternative_results: dict[str, ClassModeResult] = {}
    comparisons: dict[str, ClassComparisonResult] = {}

    baseline_rows: list[dict[str, Any]] = []
    alternative_rows: list[dict[str, Any]] = []
    comparison_rows: list[dict[str, Any]] = []
    neighbor_stats_rows: list[dict[str, Any]] = []
    shell_stats_rows: list[dict[str, Any]] = []

    input_file_counts: dict[str, int] = {}

    for export_class in export_classes:
        export_data = load_export_class_data(
            export_root=export_root,
            export_class=export_class,
            export_pattern=export_pattern,
            search_mode=search_mode,
            loader_cfg=cfg,
        )
        input_file_counts[export_class] = len(export_data.source_files)

        baseline_res, baseline_graph, baseline_shells, baseline_late_stage_count = evaluate_mode(
            export_data, baseline_mode, cfg
        )
        alternative_res, alternative_graph, alternative_shells, alternative_late_stage_count = evaluate_mode(
            export_data, alternative_mode, cfg
        )
        comparison = compare_modes(baseline_res, alternative_res)

        baseline_results[export_class] = baseline_res
        alternative_results[export_class] = alternative_res
        comparisons[export_class] = comparison

        baseline_rows.append(class_mode_to_row(baseline_res))
        alternative_rows.append(class_mode_to_row(alternative_res))
        comparison_rows.append(comparison_to_row(comparison))

        neighbor_stats_rows.append(
            graph_stats_row(
                export_class=export_class,
                mode=baseline_mode,
                graph=baseline_graph,
                launchable=baseline_res.launchable,
                pair_unit_count=baseline_res.pair_unit_count,
            )
        )
        neighbor_stats_rows.append(
            graph_stats_row(
                export_class=export_class,
                mode=alternative_mode,
                graph=alternative_graph,
                launchable=alternative_res.launchable,
                pair_unit_count=alternative_res.pair_unit_count,
            )
        )

        shell_stats_rows.append(
            shell_stats_row(
                export_class=export_class,
                mode=baseline_mode,
                shells=baseline_shells,
                a1_neighbor_min=int(cfg["a1"]["neighbor_min"]),
                late_stage_count=baseline_late_stage_count,
            )
        )
        shell_stats_rows.append(
            shell_stats_row(
                export_class=export_class,
                mode=alternative_mode,
                shells=alternative_shells,
                a1_neighbor_min=int(cfg["a1"]["neighbor_min"]),
                late_stage_count=alternative_late_stage_count,
            )
        )

    decision, short_reason, global_flags = decide_block_judgement(
        baseline_results,
        alternative_results,
    )

    summary = assemble_summary(
        cfg=cfg,
        export_root=export_root,
        baseline_results=baseline_results,
        alternative_results=alternative_results,
        comparisons=comparisons,
        decision=decision,
        short_reason=short_reason,
        global_flags=global_flags,
        input_file_counts=input_file_counts,
    )

    write_csv(output_dir / "baseline_status_table.csv", baseline_rows)
    write_csv(output_dir / "alternative_status_table.csv", alternative_rows)
    write_csv(output_dir / "class_comparison.csv", comparison_rows)
    write_csv(output_dir / "neighbor_stats.csv", neighbor_stats_rows)
    write_csv(output_dir / "shell_stats.csv", shell_stats_rows)

    write_json(output_dir / "summary.json", summary)
    write_json(
        output_dir / "run_metadata.json",
        {
            "run_id": run_id,
            "config_path": str(cfg_path),
            "timestamp_utc": now_utc_iso(),
            "output_dir": str(output_dir),
            "search_mode": search_mode,
        },
    )

    write_block_readout(
        path=output_dir / "block_readout.md",
        cfg=cfg,
        baseline_results=baseline_results,
        alternative_results=alternative_results,
        decision=decision,
        short_reason=short_reason,
    )

    print(f"[OK] N1 run complete: {run_id}")
    print(f"[OK] search_mode={search_mode}")
    print(f"[OK] Output written to: {output_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())