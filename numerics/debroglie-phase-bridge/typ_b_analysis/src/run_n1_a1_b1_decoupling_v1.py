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
from reporting import write_csv, write_json


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
class DecouplingModeResult:
    export_class: str
    mode: str
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
    a1_only_outcome: str

    b1_score_mean: float | None
    b1_score_median: float | None
    b1_status: str
    b1_only_outcome: str

    combined_status: str

    a1_drives_result: bool
    b1_drives_result: bool
    a1_b1_disagreement: bool
    dominant_channel: str

    notes: str = ""


@dataclass(slots=True)
class DecouplingComparisonResult:
    export_class: str

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

    baseline_dominant_channel: str
    alternative_dominant_channel: str
    dominance_shift: str

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
# A1 / B1 stub logic
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
# Status helpers
# ============================================================================

STATUS_RANK = {
    "not_applicable": -1,
    "inactive": 0,
    "weak": 1,
    "partial": 2,
    "active": 3,
}

OUTCOME_RANK = {
    "na": -1,
    "none": 0,
    "weak": 1,
    "strong": 2,
}

COMBINED_STATUS_RANK = {
    "boundary_non_launchable": 0,
    "weak_launchable_boundary": 1,
    "structured_intermediate": 2,
    "robust_dual": 3,
    "inconclusive": -1,
    "degenerate": -2,
}


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


def status_to_outcome(
    status: str,
    launchable: bool,
    strong_statuses: list[str],
    weak_statuses: list[str],
) -> str:
    if (not launchable) or status == "not_applicable":
        return "na"
    if status in strong_statuses:
        return "strong"
    if status in weak_statuses:
        return "weak"
    return "none"


def compute_decoupling_flags(
    a1_only_outcome: str,
    b1_only_outcome: str,
    cfg: dict[str, Any],
) -> tuple[bool, bool, bool, str]:
    dom_cfg = cfg["decoupling"]["dominance_rule"]
    prefer_single = bool(dom_cfg.get("prefer_single_channel_if_other_is_weak", True))
    mark_gap = bool(dom_cfg.get("mark_disagreement_if_strength_gap_ge_1", True))

    a1_rank = OUTCOME_RANK[a1_only_outcome]
    b1_rank = OUTCOME_RANK[b1_only_outcome]

    disagreement = False
    if mark_gap:
        if a1_only_outcome != "na" and b1_only_outcome != "na" and abs(a1_rank - b1_rank) >= 1:
            disagreement = True

    a1_drives = False
    b1_drives = False

    if prefer_single:
        if a1_only_outcome == "strong" and b1_only_outcome in {"weak", "none"}:
            a1_drives = True
        if b1_only_outcome == "strong" and a1_only_outcome in {"weak", "none"}:
            b1_drives = True

    if a1_drives and not b1_drives:
        dominant = "a1"
    elif b1_drives and not a1_drives:
        dominant = "b1"
    elif a1_only_outcome == "na" and b1_only_outcome == "na":
        dominant = "none"
    elif a1_only_outcome in {"none", "na"} and b1_only_outcome in {"none", "na"}:
        dominant = "none"
    else:
        dominant = "mixed"

    return a1_drives, b1_drives, disagreement, dominant


# ============================================================================
# Mode evaluation
# ============================================================================

def evaluate_mode(
    export_data: ExportClassData,
    neighborhood_mode: str,
    cfg: dict[str, Any],
) -> tuple[DecouplingModeResult, NeighborhoodGraph, list[ShellRecord]]:
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

    a1_only_outcome = status_to_outcome(
        status=a1_status,
        launchable=launchable,
        strong_statuses=list(cfg["decoupling"]["a1_only"]["strong_statuses"]),
        weak_statuses=list(cfg["decoupling"]["a1_only"]["weak_statuses"]),
    )
    b1_only_outcome = status_to_outcome(
        status=b1_status,
        launchable=launchable,
        strong_statuses=list(cfg["decoupling"]["b1_only"]["strong_statuses"]),
        weak_statuses=list(cfg["decoupling"]["b1_only"]["weak_statuses"]),
    )

    a1_drives, b1_drives, disagreement, dominant = compute_decoupling_flags(
        a1_only_outcome=a1_only_outcome,
        b1_only_outcome=b1_only_outcome,
        cfg=cfg,
    )

    combined_status = combined_status_from_result(launchable, a1_status, b1_status)

    neighbor_counts = [s.neighbor_count for s in shells]

    result = DecouplingModeResult(
        export_class=export_data.export_class,
        mode=neighborhood_mode,
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
        a1_only_outcome=a1_only_outcome,

        b1_score_mean=safe_mean(b1_scores),
        b1_score_median=safe_median(b1_scores),
        b1_status=b1_status,
        b1_only_outcome=b1_only_outcome,

        combined_status=combined_status,

        a1_drives_result=a1_drives,
        b1_drives_result=b1_drives,
        a1_b1_disagreement=disagreement,
        dominant_channel=dominant,

        notes="",
    )
    return result, graph, shells


# ============================================================================
# Comparison helpers
# ============================================================================

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


def dominance_shift(before: str, after: str) -> str:
    if before == after:
        return "unchanged"
    if before == "none" and after != "none":
        return "from_none"
    if before != "none" and after == "none":
        return "to_none"
    return "shifted"


def interpretation_flag(
    baseline: DecouplingModeResult,
    alternative: DecouplingModeResult,
) -> str:
    delta = combined_status_delta(baseline.combined_status, alternative.combined_status)
    if delta == "unchanged" and baseline.dominant_channel == alternative.dominant_channel:
        return "stable"
    if delta == "major_change":
        return "major_change"
    return "soft_shift"


def compare_modes(
    baseline: DecouplingModeResult,
    alternative: DecouplingModeResult,
) -> DecouplingComparisonResult:
    return DecouplingComparisonResult(
        export_class=baseline.export_class,

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
            baseline.combined_status,
            alternative.combined_status,
        ),

        baseline_dominant_channel=baseline.dominant_channel,
        alternative_dominant_channel=alternative.dominant_channel,
        dominance_shift=dominance_shift(
            baseline.dominant_channel,
            alternative.dominant_channel,
        ),

        interpretation_flag=interpretation_flag(baseline, alternative),
        comment="",
    )


# ============================================================================
# Row writers
# ============================================================================

def per_class_row(res: DecouplingModeResult) -> dict[str, Any]:
    return {
        "export_class": res.export_class,
        "mode": res.mode,
        "launchable": res.launchable,
        "pair_unit_count": res.pair_unit_count,
        "shell_count": res.shell_count,
        "mean_neighbor_count": res.mean_neighbor_count,
        "median_neighbor_count": res.median_neighbor_count,
        "max_neighbor_count": res.max_neighbor_count,
        "connected_component_count": res.connected_component_count,
        "largest_component_size": res.largest_component_size,
        "a1_score_mean": res.a1_score_mean,
        "a1_score_median": res.a1_score_median,
        "a1_status": res.a1_status,
        "a1_only_outcome": res.a1_only_outcome,
        "b1_score_mean": res.b1_score_mean,
        "b1_score_median": res.b1_score_median,
        "b1_status": res.b1_status,
        "b1_only_outcome": res.b1_only_outcome,
        "combined_status": res.combined_status,
        "a1_drives_result": res.a1_drives_result,
        "b1_drives_result": res.b1_drives_result,
        "a1_b1_disagreement": res.a1_b1_disagreement,
        "dominant_channel": res.dominant_channel,
        "notes": res.notes,
    }


def comparison_row(comp: DecouplingComparisonResult) -> dict[str, Any]:
    return {
        "export_class": comp.export_class,
        "baseline_launchable": comp.baseline_launchable,
        "alternative_launchable": comp.alternative_launchable,
        "delta_launchable": comp.delta_launchable,
        "baseline_shell_count": comp.baseline_shell_count,
        "alternative_shell_count": comp.alternative_shell_count,
        "delta_shell_count": comp.delta_shell_count,
        "baseline_mean_neighbor_count": comp.baseline_mean_neighbor_count,
        "alternative_mean_neighbor_count": comp.alternative_mean_neighbor_count,
        "delta_mean_neighbor_count": comp.delta_mean_neighbor_count,
        "baseline_a1_status": comp.baseline_a1_status,
        "alternative_a1_status": comp.alternative_a1_status,
        "delta_a1_status": comp.delta_a1_status,
        "baseline_b1_status": comp.baseline_b1_status,
        "alternative_b1_status": comp.alternative_b1_status,
        "delta_b1_status": comp.delta_b1_status,
        "baseline_combined_status": comp.baseline_combined_status,
        "alternative_combined_status": comp.alternative_combined_status,
        "delta_combined_status": comp.delta_combined_status,
        "baseline_dominant_channel": comp.baseline_dominant_channel,
        "alternative_dominant_channel": comp.alternative_dominant_channel,
        "dominance_shift": comp.dominance_shift,
        "interpretation_flag": comp.interpretation_flag,
        "comment": comp.comment,
    }


# ============================================================================
# Block decision
# ============================================================================

def decide_block_judgement(
    baseline_results: dict[str, DecouplingModeResult],
    alternative_results: dict[str, DecouplingModeResult],
) -> tuple[str, str, dict[str, Any]]:
    all_results = list(baseline_results.values()) + list(alternative_results.values())

    b1_dominant_classes = sorted({
        r.export_class for r in all_results if r.dominant_channel == "b1"
    })
    a1_dominant_classes = sorted({
        r.export_class for r in all_results if r.dominant_channel == "a1"
    })
    mixed_classes = sorted({
        r.export_class for r in all_results if r.dominant_channel == "mixed"
    })
    none_classes = sorted({
        r.export_class for r in all_results if r.dominant_channel == "none"
    })

    disagreement_count = sum(1 for r in all_results if r.a1_b1_disagreement)
    launchable_baseline = sum(1 for r in baseline_results.values() if r.launchable)
    launchable_alternative = sum(1 for r in alternative_results.values() if r.launchable)

    global_summary = {
        "b1_dominant_classes": b1_dominant_classes,
        "a1_dominant_classes": a1_dominant_classes,
        "mixed_classes": mixed_classes,
        "none_classes": none_classes,
        "disagreement_count": disagreement_count,
        "launchable_class_count_baseline": launchable_baseline,
        "launchable_class_count_alternative": launchable_alternative,
    }

    if b1_dominant_classes and not a1_dominant_classes:
        return (
            "supported",
            "Combined N1 pattern is primarily B1-driven while A1 remains weak across launchable classes.",
            global_summary,
        )

    if (b1_dominant_classes or a1_dominant_classes or mixed_classes) and (launchable_baseline + launchable_alternative) > 0:
        return (
            "partially_supported",
            "A1/B1 separation is visible, but the dominant channel pattern is not fully stable across classes and modes.",
            global_summary,
        )

    if (launchable_baseline + launchable_alternative) == 0:
        return (
            "inconclusive",
            "Too little launchable local structure is present to cleanly separate A1 and B1 contributions.",
            global_summary,
        )

    return (
        "failed",
        "A1/B1 decoupling does not support a coherent channel-based reading of the combined result.",
        global_summary,
    )


# ============================================================================
# Summary assembly
# ============================================================================

def assemble_summary(
    cfg: dict[str, Any],
    export_root: Path,
    baseline_results: dict[str, DecouplingModeResult],
    alternative_results: dict[str, DecouplingModeResult],
    comparisons: dict[str, DecouplingComparisonResult],
    decision: str,
    short_reason: str,
    global_summary: dict[str, Any],
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
                "a1_only_outcome": b.a1_only_outcome,
                "b1_score_mean": b.b1_score_mean,
                "b1_score_median": b.b1_score_median,
                "b1_status": b.b1_status,
                "b1_only_outcome": b.b1_only_outcome,
                "combined_status": b.combined_status,
                "a1_drives_result": b.a1_drives_result,
                "b1_drives_result": b.b1_drives_result,
                "a1_b1_disagreement": b.a1_b1_disagreement,
                "dominant_channel": b.dominant_channel,
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
                "a1_only_outcome": a.a1_only_outcome,
                "b1_score_mean": a.b1_score_mean,
                "b1_score_median": a.b1_score_median,
                "b1_status": a.b1_status,
                "b1_only_outcome": a.b1_only_outcome,
                "combined_status": a.combined_status,
                "a1_drives_result": a.a1_drives_result,
                "b1_drives_result": a.b1_drives_result,
                "a1_b1_disagreement": a.a1_b1_disagreement,
                "dominant_channel": a.dominant_channel,
                "notes": a.notes,
            },
            "comparison": {
                "delta_launchable": c.delta_launchable,
                "delta_shell_count": c.delta_shell_count,
                "delta_mean_neighbor_count": c.delta_mean_neighbor_count,
                "delta_a1_status": c.delta_a1_status,
                "delta_b1_status": c.delta_b1_status,
                "delta_combined_status": c.delta_combined_status,
                "baseline_dominant_channel": c.baseline_dominant_channel,
                "alternative_dominant_channel": c.alternative_dominant_channel,
                "dominance_shift": c.dominance_shift,
                "interpretation_flag": c.interpretation_flag,
                "comment": c.comment,
            },
        }

    return {
        "run_id": cfg["run"]["run_id"],
        "block": "N1_A1_B1_DECOUPLING",
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
            "pair_unit": {
                "matrix_pair_mode": cfg["pair_unit"]["matrix_pair_mode"],
                "score_field": cfg["pair_unit"]["threshold"]["score_field"],
                "tau": cfg["pair_unit"]["threshold"]["tau"],
            },
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
        "global_summary": global_summary,
        "decision": {
            "block_judgement": decision,
            "short_reason": short_reason,
        },
        "validation": {
            "all_export_classes_present": all(v > 0 for v in input_file_counts.values()),
            "empty_inputs_detected": any(v == 0 for v in input_file_counts.values()),
            "nan_metrics_detected": False,
            "validation_notes": [],
        },
        "warnings": [],
        "open_points": [
            "Decoupling is diagnostic and does not by itself establish physical privilege.",
            "A1/B1 dominance may still depend on adapter and threshold choices.",
            "n1a_alpha should be treated as a sensitivity case, not as a settled regime failure by itself.",
        ],
    }


# ============================================================================
# Readout
# ============================================================================

def write_decoupling_readout(
    path: Path,
    cfg: dict[str, Any],
    baseline_results: dict[str, DecouplingModeResult],
    alternative_results: dict[str, DecouplingModeResult],
    decision: str,
    short_reason: str,
) -> None:
    lines = [
        "# N1 Readout — A1/B1 Decoupling v1",
        "",
        "## A. Fragestellung",
        "Trägt die beobachtete N1-Klassifikation primär A1, primär B1 oder beide Kanäle gemeinsam?",
        "",
        "## B. Konstante Basis",
        f"- Exportklassen: {', '.join(cfg['inputs']['export_classes'])}",
        f"- Pair-unit adapter: {cfg['pair_unit']['matrix_pair_mode']}",
        f"- Threshold tau: {cfg['pair_unit']['threshold']['tau']}",
        f"- Baseline neighborhood: {cfg['baseline']['neighborhood']['mode']}",
        f"- Alternative neighborhood: {cfg['alternative']['neighborhood']['mode']}",
        "",
        "## C. Beobachteter Befund",
    ]

    for export_class in cfg["inputs"]["export_classes"]:
        b = baseline_results[export_class]
        a = alternative_results[export_class]
        lines.append(
            f"- {export_class}: baseline dominant={b.dominant_channel}, alternative dominant={a.dominant_channel}, "
            f"baseline combined={b.combined_status}, alternative combined={a.combined_status}"
        )

    lines.extend(
        [
            "",
            "## D. Entkopplungslesart",
            "- A1-only und B1-only werden getrennt gegen den Combined-Status gelesen.",
            "- Dominanz wird nur diagnostisch, nicht ontologisch interpretiert.",
            "",
            "## E. Blockurteil",
            f"- {decision}",
            f"- {short_reason}",
            "",
        ]
    )

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


# ============================================================================
# CLI
# ============================================================================

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run N1 A1/B1 decoupling block."
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

    baseline_results: dict[str, DecouplingModeResult] = {}
    alternative_results: dict[str, DecouplingModeResult] = {}
    comparisons: dict[str, DecouplingComparisonResult] = {}

    per_class_rows: list[dict[str, Any]] = []
    comparison_rows: list[dict[str, Any]] = []

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

        baseline_res, _, _ = evaluate_mode(export_data, baseline_mode, cfg)
        alternative_res, _, _ = evaluate_mode(export_data, alternative_mode, cfg)
        comparison = compare_modes(baseline_res, alternative_res)

        baseline_results[export_class] = baseline_res
        alternative_results[export_class] = alternative_res
        comparisons[export_class] = comparison

        per_class_rows.append(per_class_row(baseline_res))
        per_class_rows.append(per_class_row(alternative_res))
        comparison_rows.append(comparison_row(comparison))

    decision, short_reason, global_summary = decide_block_judgement(
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
        global_summary=global_summary,
        input_file_counts=input_file_counts,
    )

    write_csv(output_dir / "a1_b1_decoupling_per_class.csv", per_class_rows)
    write_csv(output_dir / "a1_b1_decoupling_comparison.csv", comparison_rows)
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
    write_decoupling_readout(
        path=output_dir / "block_readout.md",
        cfg=cfg,
        baseline_results=baseline_results,
        alternative_results=alternative_results,
        decision=decision,
        short_reason=short_reason,
    )

    print(f"[OK] Decoupling run complete: {run_id}")
    print(f"[OK] search_mode={search_mode}")
    print(f"[OK] Output written to: {output_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())