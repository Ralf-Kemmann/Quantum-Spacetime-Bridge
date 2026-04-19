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
class SpecificityModeResult:
    dataset_root: str
    mode: str

    negative_launchable: bool
    abs_launchable: bool

    negative_pair_unit_count: int
    abs_pair_unit_count: int

    negative_shell_count: int
    abs_shell_count: int

    negative_mean_neighbor_count: float
    abs_mean_neighbor_count: float

    negative_a1_status: str
    abs_a1_status: str

    negative_b1_status: str
    abs_b1_status: str

    negative_combined_status: str
    abs_combined_status: str

    negative_beats_abs_structural: bool
    negative_beats_abs_channel: bool
    negative_beats_abs_combined: bool

    specificity_flag: str
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


# ============================================================================
# Core mode evaluation
# ============================================================================

def evaluate_mode(
    export_data: ExportClassData,
    neighborhood_mode: str,
    cfg: dict[str, Any],
) -> tuple[ClassModeResult, NeighborhoodGraph, list[ShellRecord]]:
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
    return result, graph, shells


# ============================================================================
# Specificity helpers
# ============================================================================

def get_status_rank(status: str, cfg: dict[str, Any]) -> int:
    rank_map = cfg["specificity"]["status_rank"]
    return int(rank_map.get(status, -999))


def get_combined_rank(status: str, cfg: dict[str, Any]) -> int:
    rank_map = cfg["specificity"]["combined_rank"]
    return int(rank_map.get(status, -999))


def bool_advantage(left: float | int | None, right: float | int | None) -> bool:
    if left is None or right is None:
        return False
    return left > right


def compare_negative_vs_abs(
    dataset_root: str,
    mode: str,
    negative_res: ClassModeResult,
    abs_res: ClassModeResult,
    cfg: dict[str, Any],
) -> tuple[SpecificityModeResult, list[dict[str, Any]]]:
    metrics_rows: list[dict[str, Any]] = []

    # Structural metrics
    structural_checks: list[bool] = []
    structural_metric_names = list(cfg["specificity"]["structure_metrics"])

    struct_values = {
        "pair_unit_count": (negative_res.pair_unit_count, abs_res.pair_unit_count),
        "shell_count": (negative_res.shell_count, abs_res.shell_count),
        "mean_neighbor_count": (negative_res.mean_neighbor_count, abs_res.mean_neighbor_count),
    }

    for metric_name in structural_metric_names:
        neg_val, abs_val = struct_values[metric_name]
        winner = "negative" if neg_val > abs_val else "abs" if abs_val > neg_val else "tie"
        metrics_rows.append(
            {
                "dataset_root": dataset_root,
                "mode": mode,
                "metric_name": metric_name,
                "negative_value": neg_val,
                "abs_value": abs_val,
                "delta_negative_minus_abs": neg_val - abs_val,
                "winner": winner,
                "comment": "",
            }
        )
        structural_checks.append(neg_val > abs_val)

    negative_beats_abs_structural = any(structural_checks)

    # Channel metrics
    channel_metric_names = list(cfg["specificity"]["channel_metrics"])
    channel_checks: list[bool] = []

    channel_values_numeric = {
        "a1_score_mean": (negative_res.a1_score_mean, abs_res.a1_score_mean),
        "b1_score_mean": (negative_res.b1_score_mean, abs_res.b1_score_mean),
    }
    channel_values_status = {
        "a1_status": (negative_res.a1_status, abs_res.a1_status),
        "b1_status": (negative_res.b1_status, abs_res.b1_status),
    }

    for metric_name in channel_metric_names:
        if metric_name in channel_values_numeric:
            neg_val, abs_val = channel_values_numeric[metric_name]
            if neg_val is None or abs_val is None:
                winner = "tie"
                delta = None
            else:
                winner = "negative" if neg_val > abs_val else "abs" if abs_val > neg_val else "tie"
                delta = neg_val - abs_val
                channel_checks.append(neg_val > abs_val)

            metrics_rows.append(
                {
                    "dataset_root": dataset_root,
                    "mode": mode,
                    "metric_name": metric_name,
                    "negative_value": neg_val,
                    "abs_value": abs_val,
                    "delta_negative_minus_abs": delta,
                    "winner": winner,
                    "comment": "",
                }
            )

        elif metric_name in channel_values_status:
            neg_status, abs_status = channel_values_status[metric_name]
            neg_rank = get_status_rank(neg_status, cfg)
            abs_rank = get_status_rank(abs_status, cfg)
            winner = "negative" if neg_rank > abs_rank else "abs" if abs_rank > neg_rank else "tie"
            channel_checks.append(neg_rank > abs_rank)

            metrics_rows.append(
                {
                    "dataset_root": dataset_root,
                    "mode": mode,
                    "metric_name": metric_name,
                    "negative_value": neg_status,
                    "abs_value": abs_status,
                    "delta_negative_minus_abs": neg_rank - abs_rank,
                    "winner": winner,
                    "comment": "",
                }
            )

    negative_beats_abs_channel = any(channel_checks)

    # Combined
    neg_combined_rank = get_combined_rank(negative_res.combined_status, cfg)
    abs_combined_rank = get_combined_rank(abs_res.combined_status, cfg)
    negative_beats_abs_combined = neg_combined_rank > abs_combined_rank

    metrics_rows.append(
        {
            "dataset_root": dataset_root,
            "mode": mode,
            "metric_name": "combined_rank",
            "negative_value": neg_combined_rank,
            "abs_value": abs_combined_rank,
            "delta_negative_minus_abs": neg_combined_rank - abs_combined_rank,
            "winner": "negative" if neg_combined_rank > abs_combined_rank else "abs" if abs_combined_rank > neg_combined_rank else "tie",
            "comment": f"{negative_res.combined_status} vs {abs_res.combined_status}",
        }
    )

    # Overall specificity flag
    any_negative_adv = (
        negative_beats_abs_structural
        or negative_beats_abs_channel
        or negative_beats_abs_combined
    )

    any_abs_adv = any(row["winner"] == "abs" for row in metrics_rows)

    if (not negative_res.launchable) and (not abs_res.launchable):
        specificity_flag = "not_applicable"
    elif any_negative_adv and not any_abs_adv:
        specificity_flag = "negative_advantage"
    elif any_abs_adv and not any_negative_adv:
        specificity_flag = "abs_advantage"
    else:
        specificity_flag = "tie"

    result = SpecificityModeResult(
        dataset_root=dataset_root,
        mode=mode,

        negative_launchable=negative_res.launchable,
        abs_launchable=abs_res.launchable,

        negative_pair_unit_count=negative_res.pair_unit_count,
        abs_pair_unit_count=abs_res.pair_unit_count,

        negative_shell_count=negative_res.shell_count,
        abs_shell_count=abs_res.shell_count,

        negative_mean_neighbor_count=negative_res.mean_neighbor_count,
        abs_mean_neighbor_count=abs_res.mean_neighbor_count,

        negative_a1_status=negative_res.a1_status,
        abs_a1_status=abs_res.a1_status,

        negative_b1_status=negative_res.b1_status,
        abs_b1_status=abs_res.b1_status,

        negative_combined_status=negative_res.combined_status,
        abs_combined_status=abs_res.combined_status,

        negative_beats_abs_structural=negative_beats_abs_structural,
        negative_beats_abs_channel=negative_beats_abs_channel,
        negative_beats_abs_combined=negative_beats_abs_combined,

        specificity_flag=specificity_flag,
        comment="",
    )
    return result, metrics_rows


# ============================================================================
# Row writers
# ============================================================================

def per_dataset_row(res: SpecificityModeResult) -> dict[str, Any]:
    return {
        "dataset_root": res.dataset_root,
        "mode": res.mode,
        "negative_launchable": res.negative_launchable,
        "abs_launchable": res.abs_launchable,
        "negative_pair_unit_count": res.negative_pair_unit_count,
        "abs_pair_unit_count": res.abs_pair_unit_count,
        "negative_shell_count": res.negative_shell_count,
        "abs_shell_count": res.abs_shell_count,
        "negative_mean_neighbor_count": res.negative_mean_neighbor_count,
        "abs_mean_neighbor_count": res.abs_mean_neighbor_count,
        "negative_a1_status": res.negative_a1_status,
        "abs_a1_status": res.abs_a1_status,
        "negative_b1_status": res.negative_b1_status,
        "abs_b1_status": res.abs_b1_status,
        "negative_combined_status": res.negative_combined_status,
        "abs_combined_status": res.abs_combined_status,
        "negative_beats_abs_structural": res.negative_beats_abs_structural,
        "negative_beats_abs_channel": res.negative_beats_abs_channel,
        "negative_beats_abs_combined": res.negative_beats_abs_combined,
        "specificity_flag": res.specificity_flag,
        "comment": res.comment,
    }


# ============================================================================
# Summary / decision
# ============================================================================

def decide_block_judgement(
    per_dataset_results: dict[str, dict[str, SpecificityModeResult]],
) -> tuple[str, str, dict[str, Any]]:
    negative_advantage_count = 0
    abs_advantage_count = 0
    tie_count = 0
    not_applicable_count = 0

    for _, mode_map in per_dataset_results.items():
        for _, res in mode_map.items():
            if res.specificity_flag == "negative_advantage":
                negative_advantage_count += 1
            elif res.specificity_flag == "abs_advantage":
                abs_advantage_count += 1
            elif res.specificity_flag == "tie":
                tie_count += 1
            elif res.specificity_flag == "not_applicable":
                not_applicable_count += 1

    global_summary = {
        "negative_advantage_count": negative_advantage_count,
        "abs_advantage_count": abs_advantage_count,
        "tie_count": tie_count,
        "not_applicable_count": not_applicable_count,
    }

    if negative_advantage_count >= 2 and abs_advantage_count == 0:
        return (
            "supported",
            "Negative shows a stable internal advantage over abs across the signal-bearing comparisons tested.",
            global_summary,
        )

    if negative_advantage_count >= 1 and abs_advantage_count == 0:
        return (
            "partially_supported",
            "Negative shows some internal advantage over abs, but the pattern is not yet fully stable across datasets and modes.",
            global_summary,
        )

    if tie_count >= 2 and abs_advantage_count == 0:
        return (
            "inconclusive",
            "Current signal supports a shared upper block negative/abs over positive, but does not yet show a stable internal advantage of negative over abs.",
            global_summary,
        )

    return (
        "failed",
        "Abs shows equal or stronger evidence than negative in the current specificity comparisons.",
        global_summary,
    )


def assemble_summary(
    cfg: dict[str, Any],
    per_dataset_results: dict[str, dict[str, SpecificityModeResult]],
    decision: str,
    short_reason: str,
    global_summary: dict[str, Any],
) -> dict[str, Any]:
    per_dataset: dict[str, Any] = {}

    for dataset_root, mode_map in per_dataset_results.items():
        per_dataset[dataset_root] = {
            "baseline": {
                "specificity_flag": mode_map["baseline"].specificity_flag,
                "negative_beats_abs_structural": mode_map["baseline"].negative_beats_abs_structural,
                "negative_beats_abs_channel": mode_map["baseline"].negative_beats_abs_channel,
                "negative_beats_abs_combined": mode_map["baseline"].negative_beats_abs_combined,
            },
            "alternative": {
                "specificity_flag": mode_map["alternative"].specificity_flag,
                "negative_beats_abs_structural": mode_map["alternative"].negative_beats_abs_structural,
                "negative_beats_abs_channel": mode_map["alternative"].negative_beats_abs_channel,
                "negative_beats_abs_combined": mode_map["alternative"].negative_beats_abs_combined,
            },
        }

    return {
        "run_id": cfg["run"]["run_id"],
        "block": "N1_NEGATIVE_VS_ABS",
        "status": "completed",
        "timestamp_utc": now_utc_iso(),
        "seed": cfg["run"]["seed"],
        "inputs": {
            "dataset_roots": cfg["inputs"]["dataset_roots"],
            "export_classes": cfg["inputs"]["export_classes"],
            "export_pattern": cfg["inputs"]["export_pattern"],
            "search_mode": cfg["inputs"].get("search_mode", "direct"),
        },
        "parameters": {
            "pair_unit": {
                "matrix_pair_mode": cfg["pair_unit"]["matrix_pair_mode"],
                "score_field": cfg["pair_unit"]["threshold"]["score_field"],
                "tau": cfg["pair_unit"]["threshold"]["tau"],
            },
            "baseline": {
                "neighborhood_mode": cfg["baseline"]["neighborhood"]["mode"],
            },
            "alternative": {
                "neighborhood_mode": cfg["alternative"]["neighborhood"]["mode"],
            },
            "specificity": {
                "compare_classes": cfg["specificity"]["compare_classes"],
                "structure_metrics": cfg["specificity"]["structure_metrics"],
                "channel_metrics": cfg["specificity"]["channel_metrics"],
                "combined_metrics": cfg["specificity"]["combined_metrics"],
            },
        },
        "per_dataset": per_dataset,
        "global_summary": global_summary,
        "decision": {
            "block_judgement": decision,
            "short_reason": short_reason,
        },
        "validation": {
            "dataset_count": len(cfg["inputs"]["dataset_roots"]),
            "nan_metrics_detected": False,
            "validation_notes": [],
        },
        "warnings": [],
        "open_points": [
            "Current specificity test is still diagnostic and depends on the frozen adapter setup.",
            "A tie between negative and abs is an informative outcome, not a failure of the block.",
            "n1a_alpha remains a sensitivity case and should not dominate the reading of signal-bearing datasets.",
        ],
    }


def write_readout(
    path: Path,
    cfg: dict[str, Any],
    per_dataset_results: dict[str, dict[str, SpecificityModeResult]],
    decision: str,
    short_reason: str,
) -> None:
    lines = [
        "# N1 Readout — Specificity negative vs abs v1",
        "",
        "## A. Fragestellung",
        "Lässt sich innerhalb des robusten Oberblocks negative/abs > positive eine belastbare innere Trennung negative > abs zeigen?",
        "",
        "## B. Konstante Basis",
        f"- Adapter: {cfg['pair_unit']['matrix_pair_mode']}",
        f"- Threshold tau: {cfg['pair_unit']['threshold']['tau']}",
        f"- Baseline neighborhood: {cfg['baseline']['neighborhood']['mode']}",
        f"- Alternative neighborhood: {cfg['alternative']['neighborhood']['mode']}",
        "",
        "## C. Datensatzbefunde",
    ]

    for dataset_root, mode_map in per_dataset_results.items():
        lines.append(
            f"- {dataset_root}: baseline={mode_map['baseline'].specificity_flag}, "
            f"alternative={mode_map['alternative'].specificity_flag}"
        )

    lines.extend(
        [
            "",
            "## D. Blockurteil",
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
        description="Run N1 specificity block negative vs abs."
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

    export_classes: list[str] = list(cfg["inputs"]["export_classes"])
    export_pattern = cfg["inputs"]["export_pattern"]
    search_mode = cfg["inputs"].get("search_mode", "direct")

    baseline_mode = cfg["baseline"]["neighborhood"]["mode"]
    alternative_mode = cfg["alternative"]["neighborhood"]["mode"]

    per_dataset_results: dict[str, dict[str, SpecificityModeResult]] = {}
    per_dataset_rows: list[dict[str, Any]] = []
    metrics_rows: list[dict[str, Any]] = []

    for dataset_root_raw in cfg["inputs"]["dataset_roots"]:
        dataset_root = Path(dataset_root_raw).resolve()

        loaded: dict[str, ExportClassData] = {}
        for export_class in export_classes:
            loaded[export_class] = load_export_class_data(
                export_root=dataset_root,
                export_class=export_class,
                export_pattern=export_pattern,
                search_mode=search_mode,
                loader_cfg=cfg,
            )

        baseline_eval: dict[str, ClassModeResult] = {}
        alternative_eval: dict[str, ClassModeResult] = {}

        for export_class in export_classes:
            baseline_res, _, _ = evaluate_mode(loaded[export_class], baseline_mode, cfg)
            alternative_res, _, _ = evaluate_mode(loaded[export_class], alternative_mode, cfg)
            baseline_eval[export_class] = baseline_res
            alternative_eval[export_class] = alternative_res

        baseline_spec, baseline_metric_rows = compare_negative_vs_abs(
            dataset_root=str(dataset_root),
            mode="baseline",
            negative_res=baseline_eval["negative"],
            abs_res=baseline_eval["abs"],
            cfg=cfg,
        )
        alternative_spec, alternative_metric_rows = compare_negative_vs_abs(
            dataset_root=str(dataset_root),
            mode="alternative",
            negative_res=alternative_eval["negative"],
            abs_res=alternative_eval["abs"],
            cfg=cfg,
        )

        per_dataset_results[str(dataset_root)] = {
            "baseline": baseline_spec,
            "alternative": alternative_spec,
        }

        per_dataset_rows.append(per_dataset_row(baseline_spec))
        per_dataset_rows.append(per_dataset_row(alternative_spec))
        metrics_rows.extend(baseline_metric_rows)
        metrics_rows.extend(alternative_metric_rows)

    decision, short_reason, global_summary = decide_block_judgement(per_dataset_results)

    summary = assemble_summary(
        cfg=cfg,
        per_dataset_results=per_dataset_results,
        decision=decision,
        short_reason=short_reason,
        global_summary=global_summary,
    )

    write_csv(output_dir / "negative_vs_abs_per_dataset.csv", per_dataset_rows)
    write_csv(output_dir / "negative_vs_abs_metrics.csv", metrics_rows)
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
    write_readout(
        path=output_dir / "negative_vs_abs_readout.md",
        cfg=cfg,
        per_dataset_results=per_dataset_results,
        decision=decision,
        short_reason=short_reason,
    )

    print(f"[OK] Negative-vs-abs run complete: {run_id}")
    print(f"[OK] search_mode={search_mode}")
    print(f"[OK] Output written to: {output_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())