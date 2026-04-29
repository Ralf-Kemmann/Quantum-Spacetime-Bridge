#!/usr/bin/env python3
"""
BMC-12 Feature Leave-One-Out Runner

Transparent project runner for the Quantum-Spacetime-Bridge / BMC workflow.

Purpose
-------
Test whether the BMC09d threshold_tau_03-style local graph anchor is
single-feature dominated or broadly supported by the configured feature set.

This script intentionally avoids hidden assumptions about physical meaning.
It computes graph diagnostics only.

Expected run command
--------------------
python3 scripts/run_bmc12_feature_leaveoneout.py \
  --config data/bmc12_feature_leaveoneout_config.yaml
"""

from __future__ import annotations

import argparse
import csv
import json
import math
from collections import deque
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Sequence, Set, Tuple

try:
    import yaml
except ImportError as exc:
    raise SystemExit(
        "Missing dependency: PyYAML. Install it in your project environment, e.g. "
        "python3 -m pip install pyyaml"
    ) from exc


NumberTable = List[Dict[str, Any]]
Edge = Tuple[str, str]


def load_yaml(path: Path) -> Dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        data = yaml.safe_load(handle)
    if not isinstance(data, dict):
        raise ValueError(f"Config is not a mapping: {path}")
    return data


def read_csv_table(path: Path) -> NumberTable:
    with path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        rows = [dict(row) for row in reader]
    if not rows:
        raise ValueError(f"Input CSV has no rows: {path}")
    return rows


def as_float(value: Any, column: str, row_index: int) -> float:
    if value is None or value == "":
        raise ValueError(f"Missing numeric value in column '{column}', row {row_index}")
    try:
        x = float(value)
    except Exception as exc:
        raise ValueError(
            f"Non-numeric value in column '{column}', row {row_index}: {value!r}"
        ) from exc
    if not math.isfinite(x):
        raise ValueError(f"Non-finite value in column '{column}', row {row_index}: {value!r}")
    return x


def validate_input(rows: NumberTable, node_id_column: str, features: Sequence[str]) -> None:
    columns = set(rows[0].keys())
    missing = [c for c in [node_id_column, *features] if c not in columns]
    if missing:
        raise ValueError(
            "Input table is missing required columns: "
            + ", ".join(missing)
            + f"\nAvailable columns: {', '.join(sorted(columns))}"
        )

    node_ids = [str(row[node_id_column]) for row in rows]
    if len(node_ids) != len(set(node_ids)):
        raise ValueError(f"Duplicate node IDs detected in column '{node_id_column}'")


def mean(values: Sequence[float]) -> float:
    if not values:
        return float("nan")
    return sum(values) / len(values)


def median(values: Sequence[float]) -> float:
    if not values:
        return float("nan")
    s = sorted(values)
    n = len(s)
    mid = n // 2
    if n % 2:
        return s[mid]
    return 0.5 * (s[mid - 1] + s[mid])


def z_standardize(
    rows: NumberTable,
    features: Sequence[str],
    *,
    ddof: int,
    zero_std_policy: str,
) -> List[List[float]]:
    matrix: List[List[float]] = []
    for r_idx, row in enumerate(rows, start=1):
        matrix.append([as_float(row[f], f, r_idx) for f in features])

    n = len(matrix)
    if n <= ddof:
        raise ValueError(f"Cannot standardize with n={n} and ddof={ddof}")

    columns = list(zip(*matrix))
    means = [mean(list(col)) for col in columns]
    stds: List[float] = []

    for f, col, mu in zip(features, columns, means):
        var = sum((x - mu) ** 2 for x in col) / (n - ddof)
        std = math.sqrt(var)
        if std == 0.0:
            if zero_std_policy == "error":
                raise ValueError(f"Feature has zero standard deviation: {f}")
            if zero_std_policy == "drop_to_zero":
                std = 1.0
            else:
                raise ValueError(f"Unknown zero_std_policy: {zero_std_policy}")
        stds.append(std)

    z: List[List[float]] = []
    for row in matrix:
        z.append([(x - mu) / sd for x, mu, sd in zip(row, means, stds)])
    return z


def build_threshold_graph(
    node_ids: Sequence[str],
    z: Sequence[Sequence[float]],
    tau: float,
) -> Tuple[Set[Edge], List[Dict[str, Any]]]:
    edges: Set[Edge] = set()
    edge_rows: List[Dict[str, Any]] = []

    for i in range(len(node_ids)):
        for j in range(i + 1, len(node_ids)):
            dist_sq = sum((a - b) ** 2 for a, b in zip(z[i], z[j]))
            dist = math.sqrt(dist_sq)
            weight = 1.0 / (1.0 + dist)
            if weight >= tau:
                a, b = sorted((str(node_ids[i]), str(node_ids[j])))
                edges.add((a, b))
                edge_rows.append(
                    {
                        "source": a,
                        "target": b,
                        "distance": dist,
                        "weight": weight,
                    }
                )

    return edges, edge_rows


def connected_components(node_ids: Sequence[str], edges: Set[Edge]) -> List[List[str]]:
    adjacency: Dict[str, Set[str]] = {str(n): set() for n in node_ids}
    for a, b in edges:
        adjacency[a].add(b)
        adjacency[b].add(a)

    seen: Set[str] = set()
    components: List[List[str]] = []

    for node in adjacency:
        if node in seen:
            continue
        q: deque[str] = deque([node])
        seen.add(node)
        comp: List[str] = []
        while q:
            cur = q.popleft()
            comp.append(cur)
            for nxt in adjacency[cur]:
                if nxt not in seen:
                    seen.add(nxt)
                    q.append(nxt)
        components.append(sorted(comp))

    components.sort(key=len, reverse=True)
    return components


def graph_metrics(
    *,
    case_id: str,
    dropped_feature: Optional[str],
    active_features: Sequence[str],
    node_ids: Sequence[str],
    edges: Set[Edge],
    edge_rows: Sequence[Dict[str, Any]],
    baseline_edges: Optional[Set[Edge]],
    baseline_metrics: Optional[Dict[str, Any]],
    thresholds: Dict[str, Any],
) -> Dict[str, Any]:
    n = len(node_ids)
    possible_edges = n * (n - 1) / 2
    edge_count = len(edges)
    density = edge_count / possible_edges if possible_edges else 0.0

    components = connected_components(node_ids, edges)
    degrees: Dict[str, int] = {str(node): 0 for node in node_ids}
    for a, b in edges:
        degrees[a] += 1
        degrees[b] += 1
    degree_values = list(degrees.values())

    weights = [float(row["weight"]) for row in edge_rows]

    metrics: Dict[str, Any] = {
        "case_id": case_id,
        "dropped_feature": dropped_feature if dropped_feature is not None else "",
        "active_features": "|".join(active_features),
        "feature_count": len(active_features),
        "node_count": n,
        "edge_count": edge_count,
        "density": density,
        "component_count": len(components),
        "largest_component_size": len(components[0]) if components else 0,
        "mean_degree": mean([float(x) for x in degree_values]),
        "median_degree": median([float(x) for x in degree_values]),
        "min_degree": min(degree_values) if degree_values else 0,
        "max_degree": max(degree_values) if degree_values else 0,
        "mean_weight_edges": mean(weights) if weights else "",
        "median_weight_edges": median(weights) if weights else "",
        "min_weight_edges": min(weights) if weights else "",
        "max_weight_edges": max(weights) if weights else "",
        "delta_edge_count_vs_baseline": "",
        "delta_density_vs_baseline": "",
        "delta_component_count_vs_baseline": "",
        "edge_retention_vs_baseline": "",
        "new_edge_fraction_vs_baseline": "",
        "provisional_dominance_reading": "baseline_reference",
    }

    if baseline_edges is not None and baseline_metrics is not None:
        retained = len(edges & baseline_edges)
        new_edges = len(edges - baseline_edges)
        baseline_edge_count = len(baseline_edges)

        edge_retention = retained / baseline_edge_count if baseline_edge_count else 1.0
        new_edge_fraction = new_edges / edge_count if edge_count else 0.0

        delta_edge_count = edge_count - int(baseline_metrics["edge_count"])
        delta_density = density - float(baseline_metrics["density"])
        delta_component_count = len(components) - int(baseline_metrics["component_count"])

        metrics.update(
            {
                "delta_edge_count_vs_baseline": delta_edge_count,
                "delta_density_vs_baseline": delta_density,
                "delta_component_count_vs_baseline": delta_component_count,
                "edge_retention_vs_baseline": edge_retention,
                "new_edge_fraction_vs_baseline": new_edge_fraction,
            }
        )

        metrics["provisional_dominance_reading"] = classify_dominance(
            edge_retention=edge_retention,
            density=float(density),
            baseline_density=float(baseline_metrics["density"]),
            delta_component_count=delta_component_count,
            thresholds=thresholds,
        )

    return metrics


def classify_dominance(
    *,
    edge_retention: float,
    density: float,
    baseline_density: float,
    delta_component_count: int,
    thresholds: Dict[str, Any],
) -> str:
    strong_retention = float(thresholds.get("strong_edge_retention_drop_below", 0.70))
    moderate_retention = float(thresholds.get("moderate_edge_retention_drop_below", 0.85))
    strong_density = float(thresholds.get("strong_density_relative_change_above", 0.35))
    moderate_density = float(thresholds.get("moderate_density_relative_change_above", 0.20))
    comp_strong = int(thresholds.get("component_count_increase_strong", 2))
    comp_moderate = int(thresholds.get("component_count_increase_moderate", 1))

    if baseline_density == 0:
        density_rel_change = 0.0 if density == 0 else float("inf")
    else:
        density_rel_change = abs(density - baseline_density) / baseline_density

    if delta_component_count >= comp_strong:
        return "fragmentation_sensitive_to_drop"

    if edge_retention < strong_retention or density_rel_change > strong_density:
        return "strongly_sensitive_to_drop"

    if delta_component_count >= comp_moderate:
        return "fragmentation_sensitive_to_drop"

    if edge_retention < moderate_retention or density_rel_change > moderate_density:
        return "moderately_sensitive_to_drop"

    return "stable_under_drop"


def write_csv(path: Path, rows: Sequence[Dict[str, Any]], fieldnames: Sequence[str]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def write_readout(path: Path, *, run_id: str, tau: float, summary_rows: Sequence[Dict[str, Any]]) -> None:
    lines: List[str] = []
    lines.append(f"# BMC-12 Feature Leave-One-Out Readout")
    lines.append("")
    lines.append(f"## Run")
    lines.append("")
    lines.append(f"- run_id: `{run_id}`")
    lines.append(f"- tau: `{tau}`")
    lines.append("")
    lines.append("## Befund")
    lines.append("")
    lines.append("BMC-12 recomputed the threshold graph for the full feature set and for each leave-one-out feature subset.")
    lines.append("")
    lines.append("| case_id | dropped_feature | edges | components | density | edge_retention_vs_baseline | reading |")
    lines.append("|---|---:|---:|---:|---:|---:|---|")
    for row in summary_rows:
        retention = row["edge_retention_vs_baseline"]
        retention_text = "" if retention == "" else f"{float(retention):.3f}"
        lines.append(
            "| {case_id} | {dropped_feature} | {edge_count} | {component_count} | {density:.4f} | {retention} | {reading} |".format(
                case_id=row["case_id"],
                dropped_feature=row["dropped_feature"] or "-",
                edge_count=row["edge_count"],
                component_count=row["component_count"],
                density=float(row["density"]),
                retention=retention_text or "-",
                reading=row["provisional_dominance_reading"],
            )
        )
    lines.append("")
    lines.append("## Interpretation")
    lines.append("")
    lines.append("The provisional dominance labels are methodological diagnostics only. They indicate whether dropping one feature strongly alters the threshold graph relative to the all-feature baseline.")
    lines.append("")
    lines.append("## Hypothese")
    lines.append("")
    lines.append("A strongly sensitive leave-one-out case is a candidate for feature-level dominance. Stable leave-one-out cases argue against single-feature dominance at this diagnostic level.")
    lines.append("")
    lines.append("## Offene Lücke")
    lines.append("")
    lines.append("This run does not establish physical meaning. It only tests whether the local graph anchor is fragile with respect to individual feature removal.")
    lines.append("")

    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Run BMC-12 feature leave-one-out diagnostics.")
    parser.add_argument("--config", required=True, help="Path to YAML config file.")
    args = parser.parse_args()

    config_path = Path(args.config)
    cfg = load_yaml(config_path)

    run_id = str(cfg.get("run_id", "BMC12_feature_leaveoneout_open"))
    input_path = Path(str(cfg["input_feature_table"]))
    output_dir = Path(str(cfg.get("output_dir", "runs/BMC-12/feature_leaveoneout_open")))
    node_id_column = str(cfg.get("node_id_column", "node_id"))
    features = [str(x) for x in cfg["features"]]
    tau = float(cfg.get("tau", 0.30))

    standardization = cfg.get("standardization", {}) or {}
    ddof = int(standardization.get("ddof", 0))
    zero_std_policy = str(standardization.get("zero_std_policy", "error"))

    thresholds = cfg.get("dominance_thresholds", {}) or {}

    rows = read_csv_table(input_path)
    validate_input(rows, node_id_column, features)

    node_ids = [str(row[node_id_column]) for row in rows]

    output_dir.mkdir(parents=True, exist_ok=True)

    cases: List[Tuple[str, Optional[str], List[str]]] = [
        ("baseline_all_features", None, list(features))
    ]
    for feature in features:
        active = [f for f in features if f != feature]
        cases.append((f"drop_{feature}", feature, active))

    summary_rows: List[Dict[str, Any]] = []
    all_edge_rows: List[Dict[str, Any]] = []

    baseline_edges: Optional[Set[Edge]] = None
    baseline_metrics: Optional[Dict[str, Any]] = None

    for case_id, dropped_feature, active_features in cases:
        z = z_standardize(
            rows,
            active_features,
            ddof=ddof,
            zero_std_policy=zero_std_policy,
        )
        edges, edge_rows = build_threshold_graph(node_ids, z, tau)

        metrics = graph_metrics(
            case_id=case_id,
            dropped_feature=dropped_feature,
            active_features=active_features,
            node_ids=node_ids,
            edges=edges,
            edge_rows=edge_rows,
            baseline_edges=baseline_edges,
            baseline_metrics=baseline_metrics,
            thresholds=thresholds,
        )

        if case_id == "baseline_all_features":
            baseline_edges = set(edges)
            baseline_metrics = dict(metrics)

        summary_rows.append(metrics)

        for er in edge_rows:
            out_row = dict(er)
            out_row["case_id"] = case_id
            out_row["dropped_feature"] = dropped_feature if dropped_feature is not None else ""
            all_edge_rows.append(out_row)

    summary_fieldnames = [
        "case_id",
        "dropped_feature",
        "active_features",
        "feature_count",
        "node_count",
        "edge_count",
        "density",
        "component_count",
        "largest_component_size",
        "mean_degree",
        "median_degree",
        "min_degree",
        "max_degree",
        "mean_weight_edges",
        "median_weight_edges",
        "min_weight_edges",
        "max_weight_edges",
        "delta_edge_count_vs_baseline",
        "delta_density_vs_baseline",
        "delta_component_count_vs_baseline",
        "edge_retention_vs_baseline",
        "new_edge_fraction_vs_baseline",
        "provisional_dominance_reading",
    ]

    edge_fieldnames = [
        "case_id",
        "dropped_feature",
        "source",
        "target",
        "distance",
        "weight",
    ]

    summary_path = output_dir / "bmc12_feature_leaveoneout_summary.csv"
    edge_path = output_dir / "bmc12_feature_leaveoneout_edges.csv"
    metrics_path = output_dir / "bmc12_feature_leaveoneout_metrics.json"
    readout_path = output_dir / "bmc12_feature_leaveoneout_readout.md"

    write_csv(summary_path, summary_rows, summary_fieldnames)
    write_csv(edge_path, all_edge_rows, edge_fieldnames)

    metrics_payload = {
        "run_id": run_id,
        "config_path": str(config_path),
        "input_feature_table": str(input_path),
        "output_dir": str(output_dir),
        "node_id_column": node_id_column,
        "features": features,
        "tau": tau,
        "summary": summary_rows,
    }
    metrics_path.write_text(json.dumps(metrics_payload, indent=2, ensure_ascii=False), encoding="utf-8")

    write_readout(readout_path, run_id=run_id, tau=tau, summary_rows=summary_rows)

    print("BMC-12 feature leave-one-out run completed.")
    print(f"Wrote: {summary_path}")
    print(f"Wrote: {edge_path}")
    print(f"Wrote: {metrics_path}")
    print(f"Wrote: {readout_path}")


if __name__ == "__main__":
    main()
