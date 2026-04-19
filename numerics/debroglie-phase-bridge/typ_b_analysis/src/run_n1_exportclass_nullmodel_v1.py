#!/usr/bin/env python3
from __future__ import annotations

import argparse
import itertools
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from statistics import mean, median
from typing import Any

import yaml

from loader import ExportClassData, PairUnit, load_export_class_data
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
class DatasetAssignmentResult:
    dataset_root: str
    nullmodel_type: str
    assignment_label: str
    assignment_map: dict[str, str]  # target_class -> source_class

    negative_launchable: bool
    abs_launchable: bool
    positive_launchable: bool

    negative_combined_status: str
    abs_combined_status: str
    positive_combined_status: str

    negative_pair_unit_count: int
    abs_pair_unit_count: int
    positive_pair_unit_count: int

    negative_shell_count: int
    abs_shell_count: int
    positive_shell_count: int

    target_match: bool
    ordering_flag: str
    comment: str = ""


# ============================================================================
# Helpers
# ============================================================================

COMBINED_STATUS_RANK = {
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
# Evaluation
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
# Assignment logic
# ============================================================================

def make_role_swap_mapping(swap_label: str, export_classes: list[str]) -> dict[str, str]:
    mapping = {c: c for c in export_classes}
    left, right = [x.strip() for x in swap_label.split("<->")]
    mapping[left], mapping[right] = mapping[right], mapping[left]
    return mapping


def make_assignment_label(mapping: dict[str, str], export_classes: list[str]) -> str:
    parts = [f"{target}<={mapping[target]}" for target in export_classes]
    return ";".join(parts)


def apply_assignment(
    original_data: dict[str, ExportClassData],
    assignment_map: dict[str, str],
) -> dict[str, ExportClassData]:
    remapped: dict[str, ExportClassData] = {}
    for target_class, source_class in assignment_map.items():
        source = original_data[source_class]
        remapped[target_class] = ExportClassData(
            export_class=target_class,
            source_files=source.source_files,
            pair_units=source.pair_units,
            metadata={
                **source.metadata,
                "assigned_from": source_class,
            },
        )
    return remapped


def generate_permutation_mappings(
    export_classes: list[str],
    include_identity: bool,
    max_permutations: int,
) -> list[dict[str, str]]:
    perms = []
    for perm in itertools.permutations(export_classes):
        mapping = {target: source for target, source in zip(export_classes, perm)}
        is_identity = all(mapping[c] == c for c in export_classes)
        if (not include_identity) and is_identity:
            continue
        perms.append(mapping)
    return perms[:max_permutations]


# ============================================================================
# Ordering / target evaluation
# ============================================================================

def evaluate_target_match(
    results_by_class: dict[str, ClassModeResult],
    cfg: dict[str, Any],
) -> tuple[bool, str]:
    target_cfg = cfg["nullmodel"]["target_rule"]
    require_negative_launchable = bool(target_cfg["require_negative_launchable"])
    require_abs_launchable = bool(target_cfg["require_abs_launchable"])
    require_positive_non_launchable = bool(target_cfg["require_positive_non_launchable"])

    negative_ok = (results_by_class["negative"].launchable is True) if require_negative_launchable else True
    abs_ok = (results_by_class["abs"].launchable is True) if require_abs_launchable else True
    positive_ok = (results_by_class["positive"].launchable is False) if require_positive_non_launchable else True

    target_match = negative_ok and abs_ok and positive_ok

    neg_rank = COMBINED_STATUS_RANK.get(results_by_class["negative"].combined_status, -99)
    abs_rank = COMBINED_STATUS_RANK.get(results_by_class["abs"].combined_status, -99)
    pos_rank = COMBINED_STATUS_RANK.get(results_by_class["positive"].combined_status, -99)

    if neg_rank >= pos_rank and abs_rank >= pos_rank and not results_by_class["positive"].launchable:
        ordering_flag = "negative_abs_above_positive"
    elif neg_rank == abs_rank == pos_rank:
        ordering_flag = "flat"
    elif pos_rank > neg_rank or pos_rank > abs_rank:
        ordering_flag = "positive_intrudes"
    else:
        ordering_flag = "mixed_order"

    return target_match, ordering_flag


# ============================================================================
# Row writers
# ============================================================================

def assignment_result_row(res: DatasetAssignmentResult) -> dict[str, Any]:
    return {
        "dataset_root": res.dataset_root,
        "nullmodel_type": res.nullmodel_type,
        "assignment_label": res.assignment_label,
        "negative_launchable": res.negative_launchable,
        "abs_launchable": res.abs_launchable,
        "positive_launchable": res.positive_launchable,
        "negative_combined_status": res.negative_combined_status,
        "abs_combined_status": res.abs_combined_status,
        "positive_combined_status": res.positive_combined_status,
        "negative_pair_unit_count": res.negative_pair_unit_count,
        "abs_pair_unit_count": res.abs_pair_unit_count,
        "positive_pair_unit_count": res.positive_pair_unit_count,
        "negative_shell_count": res.negative_shell_count,
        "abs_shell_count": res.abs_shell_count,
        "positive_shell_count": res.positive_shell_count,
        "target_match": res.target_match,
        "ordering_flag": res.ordering_flag,
        "comment": res.comment,
    }


def ordering_table_row(res: DatasetAssignmentResult) -> dict[str, Any]:
    return {
        "dataset_root": res.dataset_root,
        "nullmodel_type": res.nullmodel_type,
        "assignment_label": res.assignment_label,
        "target_match": res.target_match,
        "ordering_flag": res.ordering_flag,
    }


# ============================================================================
# Summary / decision
# ============================================================================

def decide_block_judgement(per_dataset_summary: dict[str, Any]) -> tuple[str, str, dict[str, Any]]:
    datasets_tested = len(per_dataset_summary)
    real_target_matches = 0
    null_match_rates: list[float] = []

    real_better_count = 0
    real_equal_count = 0
    real_worse_count = 0

    for _, ds in per_dataset_summary.items():
        if ds["real_assignment"]["target_match"]:
            real_target_matches += 1

        null_summary = ds["null_summary"]
        null_rate = float(null_summary["null_target_match_rate"])
        null_match_rates.append(null_rate)

        real_beats_null = bool(null_summary["real_beats_null"])
        real_equals_null = bool(null_summary["real_equals_null"])

        if real_beats_null:
            real_better_count += 1
        elif real_equals_null:
            real_equal_count += 1
        else:
            real_worse_count += 1

    global_summary = {
        "datasets_tested": datasets_tested,
        "real_target_matches": real_target_matches,
        "null_target_match_rate_mean": (sum(null_match_rates) / len(null_match_rates)) if null_match_rates else 0.0,
        "real_better_count": real_better_count,
        "real_equal_count": real_equal_count,
        "real_worse_count": real_worse_count,
    }

    if real_better_count >= 2 and real_worse_count == 0:
        return (
            "supported",
            "Real exportclass assignments outperform simple null assignments in the signal-bearing datasets tested.",
            global_summary,
        )

    if real_better_count >= 1 and real_worse_count <= 1:
        return (
            "partially_supported",
            "Real exportclass assignments show some advantage over simple null assignments, but robustness is not uniform across all datasets.",
            global_summary,
        )

    if real_better_count == 0 and real_equal_count >= 1:
        return (
            "inconclusive",
            "Real and null exportclass assignments are not cleanly separable in the current test set.",
            global_summary,
        )

    return (
        "failed",
        "Simple null exportclass assignments reproduce the target ordering as well as or better than the real assignments.",
        global_summary,
    )


def assemble_summary(
    cfg: dict[str, Any],
    per_dataset_summary: dict[str, Any],
    decision: str,
    short_reason: str,
    global_summary: dict[str, Any],
) -> dict[str, Any]:
    return {
        "run_id": cfg["run"]["run_id"],
        "block": "N1_EXPORTCLASS_NULLMODEL",
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
            "target_rule": cfg["nullmodel"]["target_rule"],
            "ordering_rule": cfg["nullmodel"]["ordering_rule"],
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
            "Nullmodel comparison is operational and does not by itself establish physical privilege.",
            "Small dataset counts limit the strength of permutation-style conclusions.",
            "n1a_alpha should be treated as a sensitivity case in the nullmodel reading as well.",
        ],
    }


def write_readout(
    path: Path,
    cfg: dict[str, Any],
    per_dataset_summary: dict[str, Any],
    decision: str,
    short_reason: str,
) -> None:
    lines = [
        "# N1 Readout — Exportclass Nullmodel v1",
        "",
        "## A. Fragestellung",
        "Bleibt die beobachtete Trennung der Exportklassen unter alternativen Nullzuordnungen ungewöhnlich stabil?",
        "",
        "## B. Konstante Basis",
        f"- Adapter: {cfg['pair_unit']['matrix_pair_mode']}",
        f"- Threshold tau: {cfg['pair_unit']['threshold']['tau']}",
        f"- Baseline neighborhood: {cfg['baseline']['neighborhood']['mode']}",
        f"- Alternative neighborhood: {cfg['alternative']['neighborhood']['mode']}",
        "",
        "## C. Datensatzbefunde",
    ]

    for ds_root, ds in per_dataset_summary.items():
        null_summary = ds["null_summary"]
        lines.append(
            f"- {ds_root}: real_target_match={ds['real_assignment']['target_match']}, "
            f"null_target_match_rate={null_summary['null_target_match_rate']:.3f}, "
            f"real_beats_null={null_summary['real_beats_null']}"
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
        description="Run exportclass nullmodel block."
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

    all_run_rows: list[dict[str, Any]] = []
    ordering_rows: list[dict[str, Any]] = []
    per_dataset_summary: dict[str, Any] = {}

    for dataset_root_raw in cfg["inputs"]["dataset_roots"]:
        dataset_root = Path(dataset_root_raw).resolve()

        original_data: dict[str, ExportClassData] = {}
        input_file_counts: dict[str, int] = {}

        for export_class in export_classes:
            export_data = load_export_class_data(
                export_root=dataset_root,
                export_class=export_class,
                export_pattern=export_pattern,
                search_mode=search_mode,
                loader_cfg=cfg,
            )
            original_data[export_class] = export_data
            input_file_counts[export_class] = len(export_data.source_files)

        assignment_results: list[DatasetAssignmentResult] = []

        # --------------------------------------------------------------
        # Real assignment
        # --------------------------------------------------------------
        real_map = {c: c for c in export_classes}
        remapped_real = apply_assignment(original_data, real_map)
        real_results_by_class: dict[str, ClassModeResult] = {}

        for export_class in export_classes:
            res, _, _ = evaluate_mode(remapped_real[export_class], baseline_mode, cfg)
            real_results_by_class[export_class] = res

        real_target_match, real_ordering_flag = evaluate_target_match(real_results_by_class, cfg)
        real_assignment_result = DatasetAssignmentResult(
            dataset_root=str(dataset_root),
            nullmodel_type="real",
            assignment_label=make_assignment_label(real_map, export_classes),
            assignment_map=real_map,
            negative_launchable=real_results_by_class["negative"].launchable,
            abs_launchable=real_results_by_class["abs"].launchable,
            positive_launchable=real_results_by_class["positive"].launchable,
            negative_combined_status=real_results_by_class["negative"].combined_status,
            abs_combined_status=real_results_by_class["abs"].combined_status,
            positive_combined_status=real_results_by_class["positive"].combined_status,
            negative_pair_unit_count=real_results_by_class["negative"].pair_unit_count,
            abs_pair_unit_count=real_results_by_class["abs"].pair_unit_count,
            positive_pair_unit_count=real_results_by_class["positive"].pair_unit_count,
            negative_shell_count=real_results_by_class["negative"].shell_count,
            abs_shell_count=real_results_by_class["abs"].shell_count,
            positive_shell_count=real_results_by_class["positive"].shell_count,
            target_match=real_target_match,
            ordering_flag=real_ordering_flag,
            comment="",
        )
        assignment_results.append(real_assignment_result)

        # --------------------------------------------------------------
        # Role swaps
        # --------------------------------------------------------------
        if cfg["nullmodel"]["role_swaps"]["enabled"]:
            for swap_label in cfg["nullmodel"]["role_swaps"]["include"]:
                mapping = make_role_swap_mapping(swap_label, export_classes)
                remapped = apply_assignment(original_data, mapping)

                results_by_class: dict[str, ClassModeResult] = {}
                for export_class in export_classes:
                    res, _, _ = evaluate_mode(remapped[export_class], baseline_mode, cfg)
                    results_by_class[export_class] = res

                target_match, ordering_flag = evaluate_target_match(results_by_class, cfg)

                assignment_results.append(
                    DatasetAssignmentResult(
                        dataset_root=str(dataset_root),
                        nullmodel_type="role_swap",
                        assignment_label=make_assignment_label(mapping, export_classes),
                        assignment_map=mapping,
                        negative_launchable=results_by_class["negative"].launchable,
                        abs_launchable=results_by_class["abs"].launchable,
                        positive_launchable=results_by_class["positive"].launchable,
                        negative_combined_status=results_by_class["negative"].combined_status,
                        abs_combined_status=results_by_class["abs"].combined_status,
                        positive_combined_status=results_by_class["positive"].combined_status,
                        negative_pair_unit_count=results_by_class["negative"].pair_unit_count,
                        abs_pair_unit_count=results_by_class["abs"].pair_unit_count,
                        positive_pair_unit_count=results_by_class["positive"].pair_unit_count,
                        negative_shell_count=results_by_class["negative"].shell_count,
                        abs_shell_count=results_by_class["abs"].shell_count,
                        positive_shell_count=results_by_class["positive"].shell_count,
                        target_match=target_match,
                        ordering_flag=ordering_flag,
                        comment=swap_label,
                    )
                )

        # --------------------------------------------------------------
        # Permutations
        # --------------------------------------------------------------
        if cfg["nullmodel"]["permutations"]["enabled"]:
            perm_maps = generate_permutation_mappings(
                export_classes=export_classes,
                include_identity=bool(cfg["nullmodel"]["permutations"].get("include_identity", True)),
                max_permutations=int(cfg["nullmodel"]["permutations"]["max_permutations_per_dataset"]),
            )
            for mapping in perm_maps:
                label = make_assignment_label(mapping, export_classes)

                # avoid duplicate identity if already present as real
                if label == real_assignment_result.assignment_label:
                    continue

                remapped = apply_assignment(original_data, mapping)
                results_by_class: dict[str, ClassModeResult] = {}
                for export_class in export_classes:
                    res, _, _ = evaluate_mode(remapped[export_class], baseline_mode, cfg)
                    results_by_class[export_class] = res

                target_match, ordering_flag = evaluate_target_match(results_by_class, cfg)

                assignment_results.append(
                    DatasetAssignmentResult(
                        dataset_root=str(dataset_root),
                        nullmodel_type="permutation",
                        assignment_label=label,
                        assignment_map=mapping,
                        negative_launchable=results_by_class["negative"].launchable,
                        abs_launchable=results_by_class["abs"].launchable,
                        positive_launchable=results_by_class["positive"].launchable,
                        negative_combined_status=results_by_class["negative"].combined_status,
                        abs_combined_status=results_by_class["abs"].combined_status,
                        positive_combined_status=results_by_class["positive"].combined_status,
                        negative_pair_unit_count=results_by_class["negative"].pair_unit_count,
                        abs_pair_unit_count=results_by_class["abs"].pair_unit_count,
                        positive_pair_unit_count=results_by_class["positive"].pair_unit_count,
                        negative_shell_count=results_by_class["negative"].shell_count,
                        abs_shell_count=results_by_class["abs"].shell_count,
                        positive_shell_count=results_by_class["positive"].shell_count,
                        target_match=target_match,
                        ordering_flag=ordering_flag,
                        comment="",
                    )
                )

        # --------------------------------------------------------------
        # Dataset summary
        # --------------------------------------------------------------
        real_runs = [r for r in assignment_results if r.nullmodel_type == "real"]
        null_runs = [r for r in assignment_results if r.nullmodel_type != "real"]

        n_null = len(null_runs)
        n_target_matches = sum(1 for r in null_runs if r.target_match)
        null_rate = (n_target_matches / n_null) if n_null > 0 else 0.0
        real_target = real_runs[0].target_match if real_runs else False

        real_beats_null = real_target and (null_rate < 1.0)
        real_equals_null = (real_target and null_rate == 1.0) or ((not real_target) and n_target_matches == 0)

        per_dataset_summary[str(dataset_root)] = {
            "input_file_counts": input_file_counts,
            "real_assignment": {
                "assignment_label": real_runs[0].assignment_label,
                "target_match": real_runs[0].target_match,
                "ordering_flag": real_runs[0].ordering_flag,
            },
            "null_runs": [
                {
                    "nullmodel_type": r.nullmodel_type,
                    "assignment_label": r.assignment_label,
                    "target_match": r.target_match,
                    "ordering_flag": r.ordering_flag,
                }
                for r in null_runs
            ],
            "null_summary": {
                "n_runs": n_null,
                "n_target_matches": n_target_matches,
                "null_target_match_rate": null_rate,
                "real_beats_null": real_beats_null,
                "real_equals_null": real_equals_null,
            },
        }

        for r in assignment_results:
            all_run_rows.append(assignment_result_row(r))
            ordering_rows.append(ordering_table_row(r))

    decision, short_reason, global_summary = decide_block_judgement(per_dataset_summary)

    summary = assemble_summary(
        cfg=cfg,
        per_dataset_summary=per_dataset_summary,
        decision=decision,
        short_reason=short_reason,
        global_summary=global_summary,
    )

    write_csv(output_dir / "exportclass_nullmodel_runs.csv", all_run_rows)
    write_csv(output_dir / "exportclass_nullmodel_ordering_table.csv", ordering_rows)
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
        path=output_dir / "block_readout.md",
        cfg=cfg,
        per_dataset_summary=per_dataset_summary,
        decision=decision,
        short_reason=short_reason,
    )

    print(f"[OK] Exportclass nullmodel run complete: {run_id}")
    print(f"[OK] search_mode={search_mode}")
    print(f"[OK] Output written to: {output_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())