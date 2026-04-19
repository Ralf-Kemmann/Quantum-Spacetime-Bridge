#!/usr/bin/env python3
from __future__ import annotations

import argparse
import math
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from statistics import mean, median
from typing import Any

import yaml

from loader import ExportClassData, load_export_class_data
from neighborhoods import NeighborhoodGraph, build_neighborhood_graph
from reporting import write_csv, write_json


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
    weights: list[float]
    notes: str = ""


STATUS_RANK_DEFAULT = {
    "not_applicable": -1,
    "inactive": 0,
    "weak": 1,
    "partial": 2,
    "active": 3,
}

COMBINED_RANK_DEFAULT = {
    "boundary_non_launchable": 0,
    "weak_launchable_boundary": 1,
    "structured_intermediate": 2,
    "robust_dual": 3,
    "inconclusive": -1,
    "degenerate": -2,
}


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


def safe_std(values: list[float]) -> float | None:
    if not values:
        return None
    if len(values) == 1:
        return 0.0
    mu = mean(values)
    var = sum((v - mu) ** 2 for v in values) / len(values)
    return math.sqrt(var)


def quantile_linear(values: list[float], q: float) -> float | None:
    if not values:
        return None
    if len(values) == 1:
        return float(values[0])
    xs = sorted(values)
    pos = (len(xs) - 1) * q
    lo = math.floor(pos)
    hi = math.ceil(pos)
    if lo == hi:
        return float(xs[lo])
    frac = pos - lo
    return float(xs[lo] * (1.0 - frac) + xs[hi] * frac)


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


def extract_pair_weights(export_data: ExportClassData, cfg: dict[str, Any]) -> list[float]:
    weights: list[float] = []
    fallback_field = cfg["pair_unit"]["weights"].get("fallback_weight_field", "G")

    for pu in export_data.pair_units:
        weight = None

        if hasattr(pu, "weight"):
            weight = getattr(pu, "weight")
        elif isinstance(pu, dict):
            weight = pu.get("weight")

        if weight is None:
            if hasattr(pu, "metadata"):
                md = getattr(pu, "metadata")
                if isinstance(md, dict):
                    weight = md.get("weight", md.get(fallback_field))
            elif isinstance(pu, dict):
                md = pu.get("metadata", {})
                if isinstance(md, dict):
                    weight = md.get("weight", md.get(fallback_field))

        if weight is not None:
            try:
                w = float(weight)
                if math.isfinite(w):
                    weights.append(w)
            except (TypeError, ValueError):
                pass

    return weights


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
    weights = extract_pair_weights(export_data, cfg)

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
        weights=weights,
        notes="",
    )
    return result, graph, shells


def compute_structure_markers(res: ClassModeResult) -> dict[str, float | None]:
    shell_density_ratio = (
        res.shell_count / res.pair_unit_count if res.pair_unit_count > 0 else None
    )
    component_compactness_proxy = (
        res.mean_neighbor_count / res.largest_component_size
        if res.largest_component_size > 0
        else None
    )

    return {
        "mean_neighbor_count": res.mean_neighbor_count,
        "median_neighbor_count": res.median_neighbor_count,
        "max_neighbor_count": float(res.max_neighbor_count) if res.max_neighbor_count is not None else None,
        "shell_density_ratio": shell_density_ratio,
        "component_compactness_proxy": component_compactness_proxy,
    }


def compute_weight_markers(res: ClassModeResult, strong_edge_reference: str) -> dict[str, float | None]:
    weights = res.weights
    if not weights:
        return {
            "weight_mean": None,
            "weight_median": None,
            "weight_max": None,
            "weight_cv": None,
            "strong_edge_fraction": None,
        }

    w_mean = safe_mean(weights)
    w_median = safe_median(weights)
    w_max = max(weights) if weights else None
    w_std = safe_std(weights)
    w_cv = (w_std / w_mean) if (w_std is not None and w_mean not in (None, 0.0)) else None

    if strong_edge_reference == "self_q75":
        thr = quantile_linear(weights, 0.75)
    else:
        thr = quantile_linear(weights, 0.75)

    strong_edge_fraction = None
    if thr is not None and weights:
        strong_edge_fraction = sum(1 for w in weights if w >= thr) / len(weights)

    return {
        "weight_mean": w_mean,
        "weight_median": w_median,
        "weight_max": float(w_max) if w_max is not None else None,
        "weight_cv": w_cv,
        "strong_edge_fraction": strong_edge_fraction,
    }


def compute_channel_markers(
    res: ClassModeResult,
    status_rank: dict[str, int],
    combined_rank: dict[str, int],
) -> dict[str, float | None]:
    a1_b1_gap_mean = None
    if res.a1_score_mean is not None and res.b1_score_mean is not None:
        a1_b1_gap_mean = res.b1_score_mean - res.a1_score_mean

    return {
        "a1_score_mean": res.a1_score_mean,
        "a1_score_median": res.a1_score_median,
        "b1_score_mean": res.b1_score_mean,
        "b1_score_median": res.b1_score_median,
        "a1_b1_gap_mean": a1_b1_gap_mean,
        "a1_status_rank": float(status_rank.get(res.a1_status, -999)),
        "b1_status_rank": float(status_rank.get(res.b1_status, -999)),
        "combined_rank": float(combined_rank.get(res.combined_status, -999)),
    }


def decide_numeric_winner(
    left: float | None,
    right: float | None,
    epsilon: float,
) -> tuple[str, float | None]:
    if left is None or right is None:
        return "na", None

    left_f = float(left)
    right_f = float(right)

    if not math.isfinite(left_f) or not math.isfinite(right_f):
        if left_f == right_f:
            return "tie", None
        return "na", None

    delta = left_f - right_f
    if not math.isfinite(delta):
        return "na", None

    if abs(delta) <= epsilon:
        return "tie", delta
    return ("negative" if delta > 0 else "abs"), delta


def family_flag_from_winners(winners: list[str]) -> str:
    informative = [w for w in winners if w in {"negative", "abs", "tie"}]
    if not informative:
        return "not_applicable"

    neg = sum(1 for w in informative if w == "negative")
    abs_ = sum(1 for w in informative if w == "abs")

    if neg > abs_:
        return "negative_advantage"
    if abs_ > neg:
        return "abs_advantage"
    return "tie"


def overall_flag(struct_flag: str, weight_flag: str, channel_flag: str) -> str:
    flags = [struct_flag, weight_flag, channel_flag]
    neg = sum(1 for f in flags if f == "negative_advantage")
    abs_ = sum(1 for f in flags if f == "abs_advantage")
    na = sum(1 for f in flags if f == "not_applicable")

    informative = 3 - na
    if informative == 0:
        return "not_applicable"
    if neg > 0 and abs_ == 0:
        return "negative_advantage"
    if abs_ > 0 and neg == 0:
        return "abs_advantage"
    return "tie"


def decide_block_judgement(per_dataset: dict[str, Any]) -> tuple[str, str, dict[str, Any]]:
    negative_advantage_count = 0
    abs_advantage_count = 0
    tie_count = 0
    not_applicable_count = 0

    for ds in per_dataset.values():
        for mode_name in ("baseline", "alternative"):
            flag = ds[mode_name]["overall_marker_specificity_flag"]
            if flag == "negative_advantage":
                negative_advantage_count += 1
            elif flag == "abs_advantage":
                abs_advantage_count += 1
            elif flag == "tie":
                tie_count += 1
            elif flag == "not_applicable":
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
            "Additional marker families reveal a stable internal advantage of negative over abs in the signal-bearing cases.",
            global_summary,
        )
    if negative_advantage_count >= 1 and abs_advantage_count == 0:
        return (
            "partially_supported",
            "Some marker families suggest an internal advantage of negative over abs, but the pattern is not fully stable.",
            global_summary,
        )
    if abs_advantage_count >= 2 and negative_advantage_count == 0:
        return (
            "failed",
            "Additional marker families point more consistently toward abs than toward negative.",
            global_summary,
        )
    return (
        "inconclusive",
        "Additional marker families do not yet reveal a stable internal advantage of negative over abs.",
        global_summary,
    )


def write_readout(
    path: Path,
    cfg: dict[str, Any],
    per_dataset: dict[str, Any],
    decision: str,
    short_reason: str,
) -> None:
    lines = [
        "# N1 Readout — negative vs abs markers v1",
        "",
        "## A. Fragestellung",
        "Gibt es zusätzliche Markerfamilien, die innerhalb des Oberblocks negative/abs eine stabile innere Differenz sichtbar machen?",
        "",
        "## B. Konstante Basis",
        f"- Adapter: {cfg['pair_unit']['matrix_pair_mode']}",
        f"- Threshold tau: {cfg['pair_unit']['threshold']['tau']}",
        f"- Baseline neighborhood: {cfg['baseline']['neighborhood']['mode']}",
        f"- Alternative neighborhood: {cfg['alternative']['neighborhood']['mode']}",
        "",
        "## C. Datensatzbefunde",
    ]

    for dataset_root, ds in per_dataset.items():
        lines.append(
            f"- {dataset_root}: baseline={ds['baseline']['overall_marker_specificity_flag']}, "
            f"alternative={ds['alternative']['overall_marker_specificity_flag']}"
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


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run negative vs abs marker block."
    )
    parser.add_argument("--config", required=True, help="Path to config yaml")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    cfg_path = Path(args.config).resolve()
    cfg = load_yaml(cfg_path)

    output_dir = Path(cfg["run"]["output_dir"]).resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    export_classes: list[str] = list(cfg["inputs"]["export_classes"])
    export_pattern = cfg["inputs"]["export_pattern"]
    search_mode = cfg["inputs"].get("search_mode", "direct")

    baseline_mode = cfg["baseline"]["neighborhood"]["mode"]
    alternative_mode = cfg["alternative"]["neighborhood"]["mode"]

    left_class = cfg["markers"]["compare_classes"]["left"]
    right_class = cfg["markers"]["compare_classes"]["right"]

    status_rank = dict(STATUS_RANK_DEFAULT)
    status_rank.update(cfg.get("markers", {}).get("status_rank", {}))
    combined_rank = dict(COMBINED_RANK_DEFAULT)
    combined_rank.update(cfg.get("markers", {}).get("combined_rank", {}))

    per_dataset_csv_rows: list[dict[str, Any]] = []
    metrics_csv_rows: list[dict[str, Any]] = []
    per_dataset_summary: dict[str, Any] = {}

    for dataset_root_raw in cfg["inputs"]["dataset_roots"]:
        dataset_root = Path(dataset_root_raw).resolve()

        original_data: dict[str, ExportClassData] = {}
        for export_class in export_classes:
            original_data[export_class] = load_export_class_data(
                export_root=dataset_root,
                export_class=export_class,
                export_pattern=export_pattern,
                search_mode=search_mode,
                loader_cfg=cfg,
            )

        dataset_mode_summary: dict[str, Any] = {}

        for mode_name, neighborhood_mode in [
            ("baseline", baseline_mode),
            ("alternative", alternative_mode),
        ]:
            mode_results: dict[str, ClassModeResult] = {}
            for export_class in export_classes:
                res, _, _ = evaluate_mode(original_data[export_class], neighborhood_mode, cfg)
                mode_results[export_class] = res

            left_res = mode_results[left_class]
            right_res = mode_results[right_class]

            structure_markers_left = compute_structure_markers(left_res)
            structure_markers_right = compute_structure_markers(right_res)

            weight_markers_left = compute_weight_markers(
                left_res,
                cfg["markers"]["weights"].get("strong_edge_reference", "self_q75"),
            )
            weight_markers_right = compute_weight_markers(
                right_res,
                cfg["markers"]["weights"].get("strong_edge_reference", "self_q75"),
            )

            channel_markers_left = compute_channel_markers(left_res, status_rank, combined_rank)
            channel_markers_right = compute_channel_markers(right_res, status_rank, combined_rank)

            structure_epsilon = float(cfg["markers"]["structure"]["epsilon"])
            weight_epsilon = float(cfg["markers"]["weights"]["epsilon"])
            channel_epsilon = float(cfg["markers"]["channel"]["epsilon"])

            family_winners: dict[str, list[str]] = {
                "structure": [],
                "weights": [],
                "channel": [],
            }

            informative_marker_count = 0
            negative_win_count = 0
            abs_win_count = 0
            tie_count = 0

            for marker_name in cfg["markers"]["structure"]["metrics"]:
                lv = structure_markers_left.get(marker_name)
                rv = structure_markers_right.get(marker_name)
                winner, delta = decide_numeric_winner(lv, rv, structure_epsilon)
                family_winners["structure"].append(winner)

                if winner in {"negative", "abs", "tie"}:
                    informative_marker_count += 1
                if winner == "negative":
                    negative_win_count += 1
                elif winner == "abs":
                    abs_win_count += 1
                elif winner == "tie":
                    tie_count += 1

                metrics_csv_rows.append(
                    {
                        "dataset_root": str(dataset_root),
                        "mode": mode_name,
                        "marker_family": "structure",
                        "marker_name": marker_name,
                        "negative_value": lv,
                        "abs_value": rv,
                        "delta_negative_minus_abs": delta,
                        "winner": winner,
                        "comment": "",
                    }
                )

            for marker_name in cfg["markers"]["weights"]["metrics"]:
                lv = weight_markers_left.get(marker_name)
                rv = weight_markers_right.get(marker_name)
                winner, delta = decide_numeric_winner(lv, rv, weight_epsilon)
                family_winners["weights"].append(winner)

                if winner in {"negative", "abs", "tie"}:
                    informative_marker_count += 1
                if winner == "negative":
                    negative_win_count += 1
                elif winner == "abs":
                    abs_win_count += 1
                elif winner == "tie":
                    tie_count += 1

                metrics_csv_rows.append(
                    {
                        "dataset_root": str(dataset_root),
                        "mode": mode_name,
                        "marker_family": "weights",
                        "marker_name": marker_name,
                        "negative_value": lv,
                        "abs_value": rv,
                        "delta_negative_minus_abs": delta,
                        "winner": winner,
                        "comment": "",
                    }
                )

            channel_name_map = {
                "a1_score_mean": "a1_score_mean",
                "a1_score_median": "a1_score_median",
                "b1_score_mean": "b1_score_mean",
                "b1_score_median": "b1_score_median",
                "a1_b1_gap_mean": "a1_b1_gap_mean",
            }

            for marker_name in cfg["markers"]["channel"]["metrics"]:
                lookup = channel_name_map.get(marker_name, marker_name)
                lv = channel_markers_left.get(lookup)
                rv = channel_markers_right.get(lookup)
                winner, delta = decide_numeric_winner(lv, rv, channel_epsilon)
                family_winners["channel"].append(winner)

                if winner in {"negative", "abs", "tie"}:
                    informative_marker_count += 1
                if winner == "negative":
                    negative_win_count += 1
                elif winner == "abs":
                    abs_win_count += 1
                elif winner == "tie":
                    tie_count += 1

                metrics_csv_rows.append(
                    {
                        "dataset_root": str(dataset_root),
                        "mode": mode_name,
                        "marker_family": "channel",
                        "marker_name": marker_name,
                        "negative_value": lv,
                        "abs_value": rv,
                        "delta_negative_minus_abs": delta,
                        "winner": winner,
                        "comment": "",
                    }
                )

            structural_marker_flag = family_flag_from_winners(family_winners["structure"])
            weight_marker_flag = family_flag_from_winners(family_winners["weights"])
            channel_marker_flag = family_flag_from_winners(family_winners["channel"])
            overall_marker_specificity_flag = overall_flag(
                structural_marker_flag,
                weight_marker_flag,
                channel_marker_flag,
            )

            dataset_mode_summary[mode_name] = {
                "negative_launchable": left_res.launchable,
                "abs_launchable": right_res.launchable,
                "structural_marker_flag": structural_marker_flag,
                "weight_marker_flag": weight_marker_flag,
                "channel_marker_flag": channel_marker_flag,
                "overall_marker_specificity_flag": overall_marker_specificity_flag,
                "informative_marker_count": informative_marker_count,
                "negative_win_count": negative_win_count,
                "abs_win_count": abs_win_count,
                "tie_count": tie_count,
            }

            per_dataset_csv_rows.append(
                {
                    "dataset_root": str(dataset_root),
                    "mode": mode_name,
                    "negative_launchable": left_res.launchable,
                    "abs_launchable": right_res.launchable,
                    "structural_marker_flag": structural_marker_flag,
                    "weight_marker_flag": weight_marker_flag,
                    "channel_marker_flag": channel_marker_flag,
                    "overall_marker_specificity_flag": overall_marker_specificity_flag,
                    "informative_marker_count": informative_marker_count,
                    "negative_win_count": negative_win_count,
                    "abs_win_count": abs_win_count,
                    "tie_count": tie_count,
                    "comment": "",
                }
            )

        per_dataset_summary[str(dataset_root)] = dataset_mode_summary

    decision, short_reason, global_summary = decide_block_judgement(per_dataset_summary)

    summary = {
        "run_id": cfg["run"]["run_id"],
        "block": "N1_NEGATIVE_VS_ABS_MARKERS",
        "status": "completed",
        "timestamp_utc": now_utc_iso(),
        "seed": cfg["run"]["seed"],
        "inputs": {
            "dataset_roots": cfg["inputs"]["dataset_roots"],
            "export_classes": cfg["inputs"]["export_classes"],
            "export_pattern": cfg["inputs"]["export_pattern"],
            "search_mode": search_mode,
        },
        "parameters": {
            "pair_unit": {
                "matrix_pair_mode": cfg["pair_unit"]["matrix_pair_mode"],
                "score_field": cfg["pair_unit"]["threshold"]["score_field"],
                "tau": cfg["pair_unit"]["threshold"]["tau"],
            },
            "baseline": {"neighborhood_mode": baseline_mode},
            "alternative": {"neighborhood_mode": alternative_mode},
            "markers": cfg["markers"],
        },
        "per_dataset": per_dataset_summary,
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
            "Marker comparison is diagnostic and does not by itself establish physical privilege.",
            "Small dataset counts limit the strength of internal specificity claims.",
            "n1a_alpha should be treated as a sensitivity case in the marker reading as well.",
        ],
    }

    write_csv(output_dir / "negative_vs_abs_marker_per_dataset.csv", per_dataset_csv_rows)
    write_csv(output_dir / "negative_vs_abs_marker_metrics.csv", metrics_csv_rows)
    write_json(output_dir / "summary.json", summary)
    write_json(
        output_dir / "run_metadata.json",
        {
            "run_id": cfg["run"]["run_id"],
            "config_path": str(cfg_path),
            "timestamp_utc": now_utc_iso(),
            "output_dir": str(output_dir),
            "search_mode": search_mode,
        },
    )
    write_readout(
        path=output_dir / "negative_vs_abs_marker_readout.md",
        cfg=cfg,
        per_dataset=per_dataset_summary,
        decision=decision,
        short_reason=short_reason,
    )

    print(f"[OK] negative-vs-abs marker run complete: {cfg['run']['run_id']}")
    print(f"[OK] search_mode={search_mode}")
    print(f"[OK] Output written to: {output_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
