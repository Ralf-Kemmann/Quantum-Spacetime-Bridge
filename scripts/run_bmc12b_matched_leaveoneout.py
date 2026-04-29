#!/usr/bin/env python3
"""
BMC-12b Matched Leave-One-Out Runner

Purpose
-------
Compare leave-one-out feature subsets at matched graph size.

BMC-12a used fixed tau and therefore mixed two effects:
  1. feature removal
  2. lower-dimensional distance contraction / graph densification

BMC-12b fixes the graph-size issue by:
  - building the all-feature baseline with fixed tau
  - counting its retained edges
  - retaining the same number of strongest edges in each leave-one-out case

No physical claim is assigned here. This is a transparent graph-structure
diagnostic.

Run
---
python3 scripts/run_bmc12b_matched_leaveoneout.py \
  --config data/bmc12b_matched_leaveoneout_config.yaml
"""

from __future__ import annotations

import argparse
import csv
import json
import math
from collections import deque
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Set, Tuple

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


def derive_missing_features(rows: NumberTable) -> List[str]:
    """
    Add known BMC-08c-style derived features in memory if absent.
    The original input file is not modified.
    """
    if not rows:
        return []

    columns = set(rows[0].keys())
    notes: List[str] = []

    if "feature_shape_factor" not in columns:
        required = {"L_major_raw", "L_minor_raw"}
        missing = required - columns
        if missing:
            raise ValueError(
                "Cannot derive feature_shape_factor. Missing raw columns: "
                + ", ".join(sorted(missing))
            )

        for idx, row in enumerate(rows, start=1):
            l_major = as_float(row["L_major_raw"], "L_major_raw", idx)
            l_minor = as_float(row["L_minor_raw"], "L_minor_raw", idx)
            denom = min(l_major, l_minor)
            if denom == 0.0:
                raise ValueError(
                    f"Cannot derive feature_shape_factor in row {idx}: "
                    "min(L_major_raw, L_minor_raw) is zero"
                )
            row["feature_shape_factor"] = max(l_major, l_minor) / denom

        notes.append(
            "feature_shape_factor derived in memory as "
            "max(L_major_raw, L_minor_raw) / min(L_major_raw, L_minor_raw)"
        )

    columns = set(rows[0].keys())

    if "feature_spectral_index" not in columns:
        if "m_ref_raw" not in columns:
            raise ValueError(
                "Cannot derive feature_spectral_index. Missing raw column: m_ref_raw"
            )

        for idx, row in enumerate(rows, start=1):
            row["feature_spectral_index"] = as_float(row["m_ref_raw"], "m_ref_raw", idx)

        notes.append("feature_spectral_index derived in memory as m_ref_raw")

    return notes


def validate_input(rows: NumberTable, node_id_column: str, features: Sequence[str]) -> None:
    columns = set(rows[0].keys())
    missing = [c for c in [node_id_column, *features] if c not in columns]
    if missing:
        raise ValueError(
            "Input table is missing required columns: "
            + ", ".join(missing)
            + f"\nAvailable columns after derivation: {', '.join(sorted(columns))}"
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


def all_pair_weights(
    node_ids: Sequence[str],
    z: Sequence[Sequence[float]],
) -> List[Dict[str, Any]]:
    rows: List[Dict[str, Any]] = []

    for i in range(len(node_ids)):
        for j in range(i + 1, len(node_ids)):
            dist_sq = sum((a - b) ** 2 for a, b in zip(z[i], z[j]))
            dist = math.sqrt(dist_sq)
            weight = 1.0 / (1.0 + dist)
            a, b = sorted((str(node_ids[i]), str(node_ids[j])))
            rows.append(
                {
                    "source": a,
                    "target": b,
                    "distance": dist,
                    "weight": weight,
                }
            )

    return rows


def select_edges_fixed_tau(pair_rows: Sequence[Dict[str, Any]], tau: float) -> Tuple[Set[Edge], List[Dict[str, Any]], float]:
    selected = [dict(row) for row in pair_rows if float(row["weight"]) >= tau]
    edges = {(str(row["source"]), str(row["target"])) for row in selected}
    cutoff = min((float(row["weight"]) for row in selected), default=float("nan"))
    return edges, selected, cutoff


def select_edges_top_n(pair_rows: Sequence[Dict[str, Any]], n: int) -> Tuple[Set[Edge], List[Dict[str, Any]], float]:
    ordered = sorted(
        (dict(row) for row in pair_rows),
        key=lambda r: (-float(r["weight"]), str(r["source"]), str(r["target"])),
    )
    selected = ordered[:n]
    edges = {(str(row["source"]), str(row["target"])) for row in selected}
    cutoff = min((float(row["weight"]) for row in selected), default=float("nan"))
    return edges, selected, cutoff


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


def classify_structure(
    *,
    overlap_fraction: Optional[float],
    component_delta: Optional[int],
    thresholds: Dict[str, Any],
) -> str:
    if overlap_fraction is None or component_delta is None:
        return "baseline_reference"

    fragmentation_flag = bool(thresholds.get("fragmentation_if_component_count_increases", True))
    if fragmentation_flag and component_delta > 0:
        return "fragmentation_under_matched_size"

    high = float(thresholds.get("high_overlap_fraction_at_least", 0.75))
    moderate = float(thresholds.get("moderate_overlap_fraction_at_least", 0.50))

    if overlap_fraction >= high:
        return "high_structure_retention"
    if overlap_fraction >= moderate:
        return "moderate_structure_retention"
    return "low_structure_retention"


def graph_metrics(
    *,
    case_id: str,
    dropped_feature: Optional[str],
    matching_mode: str,
    active_features: Sequence[str],
    node_ids: Sequence[str],
    edges: Set[Edge],
    edge_rows: Sequence[Dict[str, Any]],
    cutoff_weight: float,
    baseline_edges: Optional[Set[Edge]],
    baseline_component_count: Optional[int],
    thresholds: Dict[str, Any],
) -> Dict[str, Any]:
    n = len(node_ids)
    possible_edges = n * (n - 1) / 2
    edge_count = len(edges)
    density = edge_count / possible_edges if possible_edges else 0.0

    components = connected_components(node_ids, edges)
    component_count = len(components)

    degrees: Dict[str, int] = {str(node): 0 for node in node_ids}
    for a, b in edges:
        degrees[a] += 1
        degrees[b] += 1
    degree_values = list(degrees.values())

    overlap_count: Any = ""
    overlap_fraction: Any = ""
    jaccard: Any = ""
    new_edge_count: Any = ""
    component_delta: Any = ""

    overlap_fraction_for_label: Optional[float] = None
    component_delta_for_label: Optional[int] = None

    if baseline_edges is not None and baseline_component_count is not None:
        intersection = edges & baseline_edges
        union = edges | baseline_edges
        overlap_count = len(intersection)
        overlap_fraction_for_label = len(intersection) / len(baseline_edges) if baseline_edges else 1.0
        overlap_fraction = overlap_fraction_for_label
        jaccard = len(intersection) / len(union) if union else 1.0
        new_edge_count = len(edges - baseline_edges)
        component_delta_for_label = component_count - baseline_component_count
        component_delta = component_delta_for_label

    reading = classify_structure(
        overlap_fraction=overlap_fraction_for_label,
        component_delta=component_delta_for_label,
        thresholds=thresholds,
    )

    return {
        "case_id": case_id,
        "dropped_feature": dropped_feature if dropped_feature is not None else "",
        "matching_mode": matching_mode,
        "active_features": "|".join(active_features),
        "feature_count": len(active_features),
        "node_count": n,
        "edge_count": edge_count,
        "density": density,
        "component_count": component_count,
        "largest_component_size": len(components[0]) if components else 0,
        "mean_degree": mean([float(x) for x in degree_values]),
        "median_degree": median([float(x) for x in degree_values]),
        "min_degree": min(degree_values) if degree_values else 0,
        "max_degree": max(degree_values) if degree_values else 0,
        "cutoff_weight": cutoff_weight if math.isfinite(cutoff_weight) else "",
        "baseline_edge_overlap_count": overlap_count,
        "baseline_edge_overlap_fraction": overlap_fraction,
        "jaccard_vs_baseline": jaccard,
        "new_edge_count_vs_baseline": new_edge_count,
        "component_delta_vs_baseline": component_delta,
        "provisional_structure_reading": reading,
    }


def write_csv(path: Path, rows: Sequence[Dict[str, Any]], fieldnames: Sequence[str]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def fmt_float(value: Any, digits: int = 3) -> str:
    if value == "" or value is None:
        return "-"
    return f"{float(value):.{digits}f}"


def write_readout(
    path: Path,
    *,
    run_id: str,
    baseline_tau: float,
    baseline_edge_count: int,
    summary_rows: Sequence[Dict[str, Any]],
    derivation_notes: Sequence[str],
) -> None:
    lines: List[str] = []
    lines.append("# BMC-12b Matched Leave-One-Out Readout")
    lines.append("")
    lines.append("## Run")
    lines.append("")
    lines.append(f"- run_id: `{run_id}`")
    lines.append(f"- baseline_tau: `{baseline_tau}`")
    lines.append(f"- baseline_edge_count: `{baseline_edge_count}`")
    lines.append("")
    lines.append("## Derived feature handling")
    lines.append("")
    if derivation_notes:
        for note in derivation_notes:
            lines.append(f"- {note}")
    else:
        lines.append("- No derived feature columns had to be created in memory.")
    lines.append("")
    lines.append("## Befund")
    lines.append("")
    lines.append(
        "BMC-12b recomputed the all-feature fixed-tau baseline and then matched each leave-one-out graph to the same edge count."
    )
    lines.append("")
    lines.append("| case_id | dropped_feature | edges | components | cutoff_weight | overlap_fraction | jaccard | reading |")
    lines.append("|---|---:|---:|---:|---:|---:|---:|---|")
    for row in summary_rows:
        lines.append(
            "| {case_id} | {dropped} | {edges} | {components} | {cutoff} | {overlap} | {jaccard} | {reading} |".format(
                case_id=row["case_id"],
                dropped=row["dropped_feature"] or "-",
                edges=row["edge_count"],
                components=row["component_count"],
                cutoff=fmt_float(row["cutoff_weight"], 4),
                overlap=fmt_float(row["baseline_edge_overlap_fraction"], 3),
                jaccard=fmt_float(row["jaccard_vs_baseline"], 3),
                reading=row["provisional_structure_reading"],
            )
        )
    lines.append("")
    lines.append("## Interpretation")
    lines.append("")
    lines.append(
        "The matched comparison controls for the densification effect seen in fixed-tau leave-one-out. "
        "The key quantity is therefore not edge count but overlap with the all-feature baseline edge set."
    )
    lines.append("")
    lines.append("## Hypothese")
    lines.append("")
    lines.append(
        "Low matched overlap after dropping a feature indicates that this feature contributes strongly to the ranking of local similarities. "
        "High matched overlap argues against strong single-feature control of the local edge structure."
    )
    lines.append("")
    lines.append("## Offene Lücke")
    lines.append("")
    lines.append(
        "This remains a graph-diagnostic test. It does not establish physical meaning and does not yet import the original BMC-09d backbone-arm decision logic."
    )
    lines.append("")

    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Run BMC-12b matched leave-one-out diagnostics.")
    parser.add_argument("--config", required=True, help="Path to YAML config file.")
    args = parser.parse_args()

    config_path = Path(args.config)
    cfg = load_yaml(config_path)

    run_id = str(cfg.get("run_id", "BMC12b_matched_leaveoneout_open"))
    input_path = Path(str(cfg["input_feature_table"]))
    output_dir = Path(str(cfg.get("output_dir", "runs/BMC-12b/matched_leaveoneout_open")))
    node_id_column = str(cfg.get("node_id_column", "node_id"))
    features = [str(x) for x in cfg["features"]]
    baseline_tau = float(cfg.get("baseline_tau", 0.30))
    matching_mode = str(cfg.get("matching_mode", "edge_count"))

    if matching_mode != "edge_count":
        raise ValueError(f"Unsupported matching_mode for this runner: {matching_mode}")

    standardization = cfg.get("standardization", {}) or {}
    ddof = int(standardization.get("ddof", 0))
    zero_std_policy = str(standardization.get("zero_std_policy", "error"))

    thresholds = cfg.get("structure_thresholds", {}) or {}

    rows = read_csv_table(input_path)
    derivation_notes = derive_missing_features(rows)
    validate_input(rows, node_id_column, features)

    node_ids = [str(row[node_id_column]) for row in rows]
    output_dir.mkdir(parents=True, exist_ok=True)

    summary_rows: List[Dict[str, Any]] = []
    all_edge_rows: List[Dict[str, Any]] = []

    # Baseline: fixed tau on all features.
    z_base = z_standardize(
        rows,
        features,
        ddof=ddof,
        zero_std_policy=zero_std_policy,
    )
    pair_base = all_pair_weights(node_ids, z_base)
    baseline_edges, baseline_edge_rows, baseline_cutoff = select_edges_fixed_tau(pair_base, baseline_tau)
    baseline_components = connected_components(node_ids, baseline_edges)
    baseline_component_count = len(baseline_components)
    baseline_edge_count = len(baseline_edges)

    baseline_metrics = graph_metrics(
        case_id="baseline_all_features_fixed_tau",
        dropped_feature=None,
        matching_mode="fixed_tau",
        active_features=features,
        node_ids=node_ids,
        edges=baseline_edges,
        edge_rows=baseline_edge_rows,
        cutoff_weight=baseline_cutoff,
        baseline_edges=None,
        baseline_component_count=None,
        thresholds=thresholds,
    )
    summary_rows.append(baseline_metrics)

    for er in baseline_edge_rows:
        row = dict(er)
        row["case_id"] = "baseline_all_features_fixed_tau"
        row["dropped_feature"] = ""
        row["matching_mode"] = "fixed_tau"
        all_edge_rows.append(row)

    if baseline_edge_count == 0:
        raise ValueError(
            "Baseline fixed-tau graph has zero edges. Cannot run matched-edge-count comparison."
        )

    # Matched leave-one-out cases.
    for feature in features:
        active = [f for f in features if f != feature]
        case_id = f"matched_drop_{feature}"

        z = z_standardize(
            rows,
            active,
            ddof=ddof,
            zero_std_policy=zero_std_policy,
        )
        pair_rows = all_pair_weights(node_ids, z)
        edges, edge_rows, cutoff = select_edges_top_n(pair_rows, baseline_edge_count)

        metrics = graph_metrics(
            case_id=case_id,
            dropped_feature=feature,
            matching_mode="matched_edge_count",
            active_features=active,
            node_ids=node_ids,
            edges=edges,
            edge_rows=edge_rows,
            cutoff_weight=cutoff,
            baseline_edges=baseline_edges,
            baseline_component_count=baseline_component_count,
            thresholds=thresholds,
        )
        summary_rows.append(metrics)

        for er in edge_rows:
            row = dict(er)
            row["case_id"] = case_id
            row["dropped_feature"] = feature
            row["matching_mode"] = "matched_edge_count"
            all_edge_rows.append(row)

    summary_fieldnames = [
        "case_id",
        "dropped_feature",
        "matching_mode",
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
        "cutoff_weight",
        "baseline_edge_overlap_count",
        "baseline_edge_overlap_fraction",
        "jaccard_vs_baseline",
        "new_edge_count_vs_baseline",
        "component_delta_vs_baseline",
        "provisional_structure_reading",
    ]

    edge_fieldnames = [
        "case_id",
        "dropped_feature",
        "matching_mode",
        "source",
        "target",
        "distance",
        "weight",
    ]

    summary_path = output_dir / "bmc12b_matched_leaveoneout_summary.csv"
    edge_path = output_dir / "bmc12b_matched_leaveoneout_edges.csv"
    metrics_path = output_dir / "bmc12b_matched_leaveoneout_metrics.json"
    readout_path = output_dir / "bmc12b_matched_leaveoneout_readout.md"

    write_csv(summary_path, summary_rows, summary_fieldnames)
    write_csv(edge_path, all_edge_rows, edge_fieldnames)

    metrics_payload = {
        "run_id": run_id,
        "config_path": str(config_path),
        "input_feature_table": str(input_path),
        "output_dir": str(output_dir),
        "node_id_column": node_id_column,
        "features": features,
        "baseline_tau": baseline_tau,
        "matching_mode": matching_mode,
        "baseline_edge_count": baseline_edge_count,
        "derived_feature_notes": list(derivation_notes),
        "summary": summary_rows,
    }
    metrics_path.write_text(json.dumps(metrics_payload, indent=2, ensure_ascii=False), encoding="utf-8")

    write_readout(
        readout_path,
        run_id=run_id,
        baseline_tau=baseline_tau,
        baseline_edge_count=baseline_edge_count,
        summary_rows=summary_rows,
        derivation_notes=derivation_notes,
    )

    print("BMC-12b matched leave-one-out run completed.")
    print(f"Baseline edge count: {baseline_edge_count}")
    if derivation_notes:
        print("Derived feature handling:")
        for note in derivation_notes:
            print(f"  - {note}")
    print(f"Wrote: {summary_path}")
    print(f"Wrote: {edge_path}")
    print(f"Wrote: {metrics_path}")
    print(f"Wrote: {readout_path}")


if __name__ == "__main__":
    main()
