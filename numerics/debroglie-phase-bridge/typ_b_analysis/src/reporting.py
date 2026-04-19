from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)

    if not rows:
        path.write_text("", encoding="utf-8")
        return

    fieldnames = list(rows[0].keys())
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )


def class_mode_to_row(res: Any) -> dict[str, Any]:
    return {
        "export_class": res.export_class,
        "neighborhood_mode": res.neighborhood_mode,
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
        "b1_score_mean": res.b1_score_mean,
        "b1_score_median": res.b1_score_median,
        "b1_status": res.b1_status,
        "combined_status": res.combined_status,
        "notes": res.notes,
    }


def comparison_to_row(comp: Any) -> dict[str, Any]:
    return {
        "export_class": comp.export_class,
        "baseline_mode": comp.baseline_mode,
        "alternative_mode": comp.alternative_mode,
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
        "interpretation_flag": comp.interpretation_flag,
        "comment": comp.comment,
    }


def graph_stats_row(
    export_class: str,
    mode: str,
    graph: Any,
    launchable: bool,
    pair_unit_count: int,
) -> dict[str, Any]:
    return {
        "export_class": export_class,
        "neighborhood_mode": mode,
        "node_count": len(graph.node_ids),
        "pair_unit_count": pair_unit_count,
        "edge_count": graph.edge_count,
        "mean_degree": graph.mean_degree,
        "median_degree": graph.median_degree,
        "max_degree": graph.max_degree,
        "min_degree": graph.min_degree,
        "isolated_count": graph.isolated_count,
        "connected_component_count": len(graph.connected_components),
        "largest_component_size": graph.largest_component_size,
        "launchability_support_flag": launchable,
    }


def shell_stats_row(
    export_class: str,
    mode: str,
    shells: list[Any],
    a1_neighbor_min: int,
    late_stage_count: int = 0,
) -> dict[str, Any]:
    shell_sizes = [s.neighbor_count for s in shells]
    valid_shells = [s for s in shells if s.valid]
    invalid_shells = [s for s in shells if not s.valid]

    return {
        "export_class": export_class,
        "neighborhood_mode": mode,
        "shell_count": len(valid_shells),
        "mean_shell_size": (sum(shell_sizes) / len(shell_sizes)) if shell_sizes else 0.0,
        "median_shell_size": _median(shell_sizes),
        "max_shell_size": max(shell_sizes) if shell_sizes else 0,
        "min_shell_size": min(shell_sizes) if shell_sizes else 0,
        "valid_shell_count": len(valid_shells),
        "invalid_shell_count": len(invalid_shells),
        "late_stage_count": late_stage_count,
        "a1_neighbor_min": a1_neighbor_min,
        "comment": "",
    }


def _median(values: list[int | float]) -> float:
    if not values:
        return 0.0
    vals = sorted(values)
    n = len(vals)
    mid = n // 2
    if n % 2 == 1:
        return float(vals[mid])
    return float((vals[mid - 1] + vals[mid]) / 2.0)


def write_block_readout(
    path: Path,
    cfg: dict[str, Any],
    baseline_results: dict[str, Any],
    alternative_results: dict[str, Any],
    decision: str,
    short_reason: str,
) -> None:
    lines = [
        "# N1 Readout — Alternative Neighborhood v1",
        "",
        "## A. Fragestellung",
        "Prüfung der Sensitivität der aktuellen Exportklassen-Ordnung gegenüber einer alternativen Neighborhood-Definition.",
        "",
        "## B. Konstante Baseline",
        f"- Exportklassen: {', '.join(cfg['inputs']['export_classes'])}",
        f"- A1: {cfg['a1']['late_stage_rule']} rule",
        f"- B1 conflict_penalty: {cfg['b1']['conflict_penalty']}",
        "- Decision logic unchanged",
        "",
        "## C. Variierte Komponente",
        f"- Neighborhood changed from {cfg['baseline']['neighborhood']['mode']} to {cfg['alternative']['neighborhood']['mode']}",
        "",
        "## D. Beobachteter Befund",
    ]

    for export_class in cfg["inputs"]["export_classes"]:
        b = baseline_results[export_class]
        a = alternative_results[export_class]
        lines.append(
            f"- {export_class}: baseline={b.combined_status}, alternative={a.combined_status}, "
            f"baseline_launchable={b.launchable}, alternative_launchable={a.launchable}"
        )

    lines.extend(
        [
            "",
            "## E. Struktursignal",
            "- Vergleich bleibt operational; keine physikalische Privilegierung der alternativen Neighborhood wird behauptet.",
            "",
            "## F. Offene Punkte",
            "- Alternative neighborhood remains operational, not physically privileged.",
            "- No direct geometry claim follows from this block.",
            "",
            "## G. Blockurteil",
            f"- {decision}",
            f"- {short_reason}",
            "",
        ]
    )

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")