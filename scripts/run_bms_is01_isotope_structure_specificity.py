#!/usr/bin/env python3
"""
BMS-IS01 — Isotope / Structure Specificity Diagnostic Runner

Purpose
-------
Convert existing de Broglie matter-signature isotope scan CSVs into a
canonical node table, build a relational signature graph, and run a
BMC-15h-style structured-specificity diagnostic.

This runner is intentionally transparent and dependency-light. It uses PyYAML
for config parsing and Python standard-library modules for all calculations.

Important interpretation boundary
---------------------------------
This is a methodological diagnostic, not a physical-geometry proof. It tests
whether isotope / structure matter-signature outputs contain local relational
organization beyond simple scalar ordering and whether that organization is
reproduced by structured null families.
"""

from __future__ import annotations

import argparse
import csv
import json
import math
import random
import statistics
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Iterable, List, Tuple

try:
    import yaml
except ImportError as exc:  # pragma: no cover
    raise SystemExit(
        "PyYAML is required for this runner. Install with: python -m pip install pyyaml"
    ) from exc


Edge = Tuple[str, str]


def as_float(value: Any, default: float = float("nan")) -> float:
    try:
        if value is None or value == "":
            return default
        return float(value)
    except Exception:
        return default


def edge_key(a: str, b: str) -> Edge:
    return (a, b) if a <= b else (b, a)


def read_yaml(path: Path) -> Dict[str, Any]:
    with path.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def write_csv(path: Path, rows: List[Dict[str, Any]], fieldnames: List[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow({k: row.get(k, "") for k in fieldnames})


def load_nodes(cfg: Dict[str, Any], root: Path, warnings: List[Dict[str, str]]) -> List[Dict[str, Any]]:
    rows_out: List[Dict[str, Any]] = []
    scan_tables = cfg["inputs"]["scan_tables"]

    for table in scan_tables:
        p = root / table["source_path"]
        if not p.exists():
            warnings.append({
                "severity": "warning",
                "message": f"Input scan table not found: {p}",
            })
            continue

        delta_column = table.get("delta_column", "")
        with p.open(newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for source_row in reader:
                isotope = source_row.get("isotope", "")
                label = source_row.get("label", isotope)
                node_id = f'{table["family_id"]}__{table["run_id"]}__{isotope}'

                row = {
                    "node_id": node_id,
                    "run_id": table["run_id"],
                    "family_id": table["family_id"],
                    "test_axis": table.get("test_axis", ""),
                    "isotope": isotope,
                    "label": label,
                    "element_symbol": source_row.get("element_symbol", ""),
                    "mass_u": source_row.get("mass_u", ""),
                    "proton_number": source_row.get("proton_number", ""),
                    "neutron_number": source_row.get("neutron_number", ""),
                    "electron_count": source_row.get("electron_count", ""),
                    "lambda_db": source_row.get("lambda_db", ""),
                    "energy_j": source_row.get("energy_j", ""),
                    "number_density": source_row.get("number_density", ""),
                    "valence_electron_count": source_row.get("valence_electron_count", ""),
                    "shell_closure_score": source_row.get("shell_closure_score", ""),
                    "length_scale_score": source_row.get("length_scale_score", ""),
                    "energy_score": source_row.get("energy_score", ""),
                    "occupancy_score": source_row.get("occupancy_score", ""),
                    "signature_score_wave": source_row.get("signature_score_wave", ""),
                    "valence_score": source_row.get("valence_score", ""),
                    "signature_score_combined": source_row.get("signature_score_combined", ""),
                    "matter_sensitive_delta": source_row.get(delta_column, source_row.get("matter_sensitive_delta", "")),
                    "source_delta_column": delta_column,
                    "source_file": str(table["source_path"]),
                }
                rows_out.append(row)

    if not rows_out:
        warnings.append({"severity": "warning", "message": "No input rows were loaded."})

    return rows_out


def make_vectors(nodes: List[Dict[str, Any]], cfg: Dict[str, Any], warnings: List[Dict[str, str]]) -> Dict[str, List[float]]:
    adapter = cfg["adapter"]
    vector_columns = adapter["vector_columns"]
    log10_columns = set(adapter.get("log10_columns", []))
    normalize = bool(adapter.get("normalize_columns", True))

    raw_by_node: Dict[str, List[float]] = {}
    columns_values: Dict[str, List[float]] = {c: [] for c in vector_columns}

    for node in nodes:
        vals = []
        for col in vector_columns:
            x = as_float(node.get(col))
            if col in log10_columns:
                if x > 0:
                    x = math.log10(x)
                else:
                    warnings.append({
                        "severity": "warning",
                        "message": f"Non-positive value for log10 column {col} in node {node['node_id']}: {node.get(col)}",
                    })
                    x = float("nan")
            vals.append(x)
            if math.isfinite(x):
                columns_values[col].append(x)
        raw_by_node[node["node_id"]] = vals

    means: Dict[str, float] = {}
    stdevs: Dict[str, float] = {}
    for col in vector_columns:
        vals = columns_values[col]
        if not vals:
            means[col] = 0.0
            stdevs[col] = 1.0
            warnings.append({"severity": "warning", "message": f"No finite values for vector column: {col}"})
        else:
            means[col] = statistics.mean(vals)
            stdevs[col] = statistics.pstdev(vals) or 1.0

    vectors: Dict[str, List[float]] = {}
    for node_id, raw in raw_by_node.items():
        out = []
        for col, x in zip(vector_columns, raw):
            if not math.isfinite(x):
                x = means[col]
            if normalize:
                x = (x - means[col]) / stdevs[col]
            out.append(x)
        vectors[node_id] = out

    return vectors


def euclidean(a: List[float], b: List[float]) -> float:
    return math.sqrt(sum((x - y) ** 2 for x, y in zip(a, b)))


def build_edges_from_vectors(
    nodes: List[Dict[str, Any]],
    vectors: Dict[str, List[float]],
    object_id: str,
    null_family: str,
    repeat_index: int | str,
) -> List[Dict[str, Any]]:
    out = []
    ids = [n["node_id"] for n in nodes]
    for i, a in enumerate(ids):
        for b in ids[i + 1:]:
            d = euclidean(vectors[a], vectors[b])
            w = math.exp(-d)
            out.append({
                "object_id": object_id,
                "null_family": null_family,
                "repeat_index": repeat_index,
                "source": a,
                "target": b,
                "weight": w,
                "distance": d,
            })
    return out


def edge_weights_map(edges: List[Dict[str, Any]]) -> Dict[Edge, float]:
    return {edge_key(e["source"], e["target"]): as_float(e["weight"]) for e in edges}


def map_to_edge_rows(weights: Dict[Edge, float], object_id: str, null_family: str, repeat_index: int | str) -> List[Dict[str, Any]]:
    rows = []
    for (a, b), w in weights.items():
        d = -math.log(max(w, 1e-300))
        rows.append({
            "object_id": object_id,
            "null_family": null_family,
            "repeat_index": repeat_index,
            "source": a,
            "target": b,
            "weight": w,
            "distance": d,
        })
    return rows


def top_edges(edge_weights: Dict[Edge, float], count: int) -> Dict[Edge, float]:
    return dict(sorted(edge_weights.items(), key=lambda kv: abs(kv[1]), reverse=True)[:count])


def threshold_edges(edge_weights: Dict[Edge, float], threshold: float) -> Dict[Edge, float]:
    return {e: w for e, w in edge_weights.items() if abs(w) >= threshold}


def mutual_knn_edges(edge_weights: Dict[Edge, float], node_ids: List[str], k: int) -> Dict[Edge, float]:
    neigh: Dict[str, List[Tuple[str, float]]] = {n: [] for n in node_ids}
    for (a, b), w in edge_weights.items():
        neigh[a].append((b, w))
        neigh[b].append((a, w))

    topn: Dict[str, set[str]] = {}
    for n, vals in neigh.items():
        topn[n] = {x for x, _w in sorted(vals, key=lambda t: abs(t[1]), reverse=True)[:k]}

    out: Dict[Edge, float] = {}
    for (a, b), w in edge_weights.items():
        if b in topn[a] and a in topn[b]:
            out[(a, b)] = w
    return out


def mst_edges(edge_weights: Dict[Edge, float], node_ids: List[str]) -> Dict[Edge, float]:
    # Kruskal maximum spanning tree.
    parent = {n: n for n in node_ids}

    def find(x: str) -> str:
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    def union(a: str, b: str) -> bool:
        ra, rb = find(a), find(b)
        if ra == rb:
            return False
        parent[rb] = ra
        return True

    out: Dict[Edge, float] = {}
    for (a, b), w in sorted(edge_weights.items(), key=lambda kv: abs(kv[1]), reverse=True):
        if union(a, b):
            out[(a, b)] = w
        if len(out) >= max(0, len(node_ids) - 1):
            break
    return out


def construct_variants(edge_weights: Dict[Edge, float], node_ids: List[str], cfg: Dict[str, Any]) -> List[Dict[str, Any]]:
    fams = cfg["construction_families"]
    variants: List[Dict[str, Any]] = []

    if fams.get("top_strength", {}).get("enabled", False):
        for n in fams["top_strength"]["edge_counts"]:
            variants.append({
                "construction_family": "top_strength",
                "construction_variant": f"top_edges_{n}",
                "edges": top_edges(edge_weights, int(n)),
            })

    if fams.get("threshold", {}).get("enabled", False):
        for t in fams["threshold"]["thresholds"]:
            variants.append({
                "construction_family": "threshold",
                "construction_variant": f"abs_weight_ge_{t}",
                "edges": threshold_edges(edge_weights, float(t)),
            })

    if fams.get("mutual_knn", {}).get("enabled", False):
        for k in fams["mutual_knn"]["k_values"]:
            variants.append({
                "construction_family": "mutual_knn",
                "construction_variant": f"k_{k}",
                "edges": mutual_knn_edges(edge_weights, node_ids, int(k)),
            })

    if fams.get("maximum_spanning_tree", {}).get("enabled", False):
        variants.append({
            "construction_family": "maximum_spanning_tree",
            "construction_variant": "abs_weight_mst",
            "edges": mst_edges(edge_weights, node_ids),
        })

    return variants


def metric_rows_for_object(
    object_id: str,
    null_family: str,
    repeat_index: int | str,
    edge_weights: Dict[Edge, float],
    node_ids: List[str],
    node_family: Dict[str, str],
    ref_core_edges: set[Edge],
    cfg: Dict[str, Any],
) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    ref_core_nodes = {n for e in ref_core_edges for n in e}
    variants = construct_variants(edge_weights, node_ids, cfg)
    core_rows = []
    envelope_rows = []

    for var in variants:
        env_edges = set(var["edges"].keys())
        env_nodes = {n for e in env_edges for n in e}

        edge_containment = len(ref_core_edges & env_edges) / len(ref_core_edges) if ref_core_edges else 0.0
        node_containment = len(ref_core_nodes & env_nodes) / len(ref_core_nodes) if ref_core_nodes else 0.0

        if env_edges:
            within = sum(1 for a, b in env_edges if node_family.get(a) == node_family.get(b))
            family_purity = within / len(env_edges)
        else:
            family_purity = 0.0

        base = {
            "object_id": object_id,
            "null_family": null_family,
            "repeat_index": repeat_index,
            "construction_family": var["construction_family"],
            "construction_variant": var["construction_variant"],
            "edge_count": len(env_edges),
            "node_count": len(env_nodes),
        }

        for metric_name, value in [
            ("envelope_core_edge_containment", edge_containment),
            ("envelope_core_node_containment", node_containment),
            ("family_purity", family_purity),
        ]:
            row = dict(base)
            row["metric_name"] = metric_name
            row["metric_value"] = value
            envelope_rows.append(row)

        # core_metrics duplicate the two core-specific rows for compatibility with BMC-15h-style outputs.
        for metric_name, value in [
            ("envelope_core_edge_containment", edge_containment),
            ("envelope_core_node_containment", node_containment),
        ]:
            row = dict(base)
            row["metric_name"] = metric_name
            row["metric_value"] = value
            core_rows.append(row)

    return core_rows, envelope_rows


def summarize(real_rows: List[Dict[str, Any]], null_rows: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    real_index: Dict[Tuple[str, str, str], float] = {}
    for r in real_rows:
        key = (r["metric_name"], r["construction_family"], r["construction_variant"])
        real_index[key] = as_float(r["metric_value"])

    grouped: Dict[Tuple[str, str, str, str], List[float]] = defaultdict(list)
    for r in null_rows:
        key = (
            r["null_family"],
            r["metric_name"],
            r["construction_family"],
            r["construction_variant"],
        )
        grouped[key].append(as_float(r["metric_value"]))

    out = []
    for (null_family, metric_name, construction_family, construction_variant), vals in sorted(grouped.items()):
        vals = [v for v in vals if math.isfinite(v)]
        real_value = real_index.get((metric_name, construction_family, construction_variant), float("nan"))
        null_mean = statistics.mean(vals) if vals else float("nan")
        null_min = min(vals) if vals else float("nan")
        null_max = max(vals) if vals else float("nan")
        exceed = sum(1 for v in vals if v >= real_value) / len(vals) if vals and math.isfinite(real_value) else float("nan")
        delta = real_value - null_mean if math.isfinite(real_value) and math.isfinite(null_mean) else float("nan")

        if not math.isfinite(exceed):
            label = "inconclusive_due_to_scope_or_warnings"
        elif exceed >= 0.50:
            label = "null_reproduces_core_behavior" if "core" in metric_name else "null_reproduces_metric_behavior"
        elif exceed > 0.05:
            label = "mixed_family_dependent_result"
        else:
            label = "real_exceeds_tested_null_family"

        out.append({
            "null_family": null_family,
            "metric_name": metric_name,
            "construction_family": construction_family,
            "construction_variant": construction_variant,
            "real_value": real_value,
            "null_mean": null_mean,
            "null_min": null_min,
            "null_max": null_max,
            "real_minus_null_mean": delta,
            "empirical_exceedance_fraction": exceed,
            "null_count": len(vals),
            "interpretation_label": label,
        })
    return out


def run(config_path: Path) -> None:
    root = Path.cwd()
    cfg = read_yaml(config_path)
    rng = random.Random(int(cfg["run"].get("random_seed", 0)))
    output_dir = root / cfg["run"]["output_dir"]
    output_dir.mkdir(parents=True, exist_ok=True)

    warnings: List[Dict[str, str]] = []

    nodes = load_nodes(cfg, root, warnings)
    node_ids = [n["node_id"] for n in nodes]
    node_family = {n["node_id"]: n.get("family_id", "") for n in nodes}

    vectors = make_vectors(nodes, cfg, warnings)
    real_edges = build_edges_from_vectors(nodes, vectors, "real", "real", "real")
    real_weights = edge_weights_map(real_edges)

    ref_core_count = int(cfg["reference_core"]["edge_count"])
    ref_core = set(top_edges(real_weights, ref_core_count).keys())

    all_edge_rows: List[Dict[str, Any]] = []
    all_edge_rows.extend(real_edges)

    null_inventory: List[Dict[str, Any]] = []
    object_weights: List[Tuple[str, str, int | str, Dict[Edge, float]]] = [("real", "real", "real", real_weights)]

    nf = cfg["null_families"]

    # Degree/weight preserving rewire for complete graph is implemented as a weight permutation
    # over the same node-pair universe. This preserves the weight multiset and node set while
    # disrupting the association between local pairs and weights.
    if nf.get("degree_weight_preserving_rewire", {}).get("enabled", False):
        repeats = int(nf["degree_weight_preserving_rewire"].get("repeats", 50))
        pairs = list(real_weights.keys())
        weights = list(real_weights.values())
        for i in range(repeats):
            shuffled = weights[:]
            rng.shuffle(shuffled)
            wmap = dict(zip(pairs, shuffled))
            object_id = f"degree_weight_preserving_rewire_{i:03d}"
            object_weights.append((object_id, "degree_weight_preserving_rewire", i, wmap))
            all_edge_rows.extend(map_to_edge_rows(wmap, object_id, "degree_weight_preserving_rewire", i))
            null_inventory.append({"object_id": object_id, "null_family": "degree_weight_preserving_rewire", "repeat_index": i})

    # Feature-structured shuffle: shuffle normalized vectors within family, then rebuild pairwise weights.
    if nf.get("feature_structured_shuffle", {}).get("enabled", False):
        repeats = int(nf["feature_structured_shuffle"].get("repeats", 50))
        by_family: Dict[str, List[str]] = defaultdict(list)
        for n in nodes:
            by_family[n.get("family_id", "")].append(n["node_id"])

        for i in range(repeats):
            shuffled_vectors = {k: v[:] for k, v in vectors.items()}
            for fam, ids in by_family.items():
                vecs = [vectors[x][:] for x in ids]
                rng.shuffle(vecs)
                for node_id, vec in zip(ids, vecs):
                    shuffled_vectors[node_id] = vec
            object_id = f"feature_structured_shuffle_{i:03d}"
            edges = build_edges_from_vectors(nodes, shuffled_vectors, object_id, "feature_structured_shuffle", i)
            wmap = edge_weights_map(edges)
            object_weights.append((object_id, "feature_structured_shuffle", i, wmap))
            all_edge_rows.extend(edges)
            null_inventory.append({"object_id": object_id, "null_family": "feature_structured_shuffle", "repeat_index": i})

    # Core-seeded decoy: start from a weight permutation and deliberately assign high weights to
    # the real reference-core pairs. This is an intentionally adversarial "cheap-core insertion"
    # diagnostic and must not be interpreted as a physical model.
    if nf.get("core_seeded_decoy", {}).get("enabled", False):
        settings = nf["core_seeded_decoy"]
        repeats = int(settings.get("repeats", 50))
        pairs = list(real_weights.keys())
        weights = list(real_weights.values())
        sorted_weights = sorted(weights)
        q = float(settings.get("seed_weight_quantile", 0.90))
        q_index = min(len(sorted_weights) - 1, max(0, int(q * (len(sorted_weights) - 1))))
        high_weights = [w for w in sorted_weights if w >= sorted_weights[q_index]]
        if not high_weights:
            high_weights = sorted_weights[-max(1, ref_core_count):]

        for i in range(repeats):
            shuffled = weights[:]
            rng.shuffle(shuffled)
            wmap = dict(zip(pairs, shuffled))
            for e in ref_core:
                wmap[e] = rng.choice(high_weights)
            object_id = f"core_seeded_decoy_{i:03d}"
            object_weights.append((object_id, "core_seeded_decoy", i, wmap))
            all_edge_rows.extend(map_to_edge_rows(wmap, object_id, "core_seeded_decoy", i))
            null_inventory.append({"object_id": object_id, "null_family": "core_seeded_decoy", "repeat_index": i})

    all_core_metrics: List[Dict[str, Any]] = []
    all_envelope_metrics: List[Dict[str, Any]] = []

    real_core_rows: List[Dict[str, Any]] = []
    null_core_rows: List[Dict[str, Any]] = []
    real_env_rows: List[Dict[str, Any]] = []
    null_env_rows: List[Dict[str, Any]] = []

    for object_id, null_family, repeat_index, wmap in object_weights:
        core_rows, env_rows = metric_rows_for_object(
            object_id=object_id,
            null_family=null_family,
            repeat_index=repeat_index,
            edge_weights=wmap,
            node_ids=node_ids,
            node_family=node_family,
            ref_core_edges=ref_core,
            cfg=cfg,
        )
        all_core_metrics.extend(core_rows)
        all_envelope_metrics.extend(env_rows)
        if null_family == "real":
            real_core_rows.extend(core_rows)
            real_env_rows.extend(env_rows)
        else:
            null_core_rows.extend(core_rows)
            null_env_rows.extend(env_rows)

    # Summarize using envelope rows so family_purity is included.
    summary = summarize(real_env_rows, null_env_rows)

    family_counts = Counter(n["family_id"] for n in nodes)
    family_summary = []
    for family, count in sorted(family_counts.items()):
        labels = sorted({n["label"] for n in nodes if n["family_id"] == family})
        family_summary.append({
            "family_id": family,
            "node_count": count,
            "labels": ";".join(labels),
        })

    # Output field lists.
    node_fields = [
        "node_id", "run_id", "family_id", "test_axis", "isotope", "label",
        "element_symbol", "mass_u", "proton_number", "neutron_number",
        "electron_count", "lambda_db", "energy_j", "number_density",
        "valence_electron_count", "shell_closure_score", "length_scale_score",
        "energy_score", "occupancy_score", "signature_score_wave",
        "valence_score", "signature_score_combined", "matter_sensitive_delta",
        "source_delta_column", "source_file",
    ]
    edge_fields = ["object_id", "null_family", "repeat_index", "source", "target", "weight", "distance"]
    metric_fields = [
        "object_id", "null_family", "repeat_index", "construction_family",
        "construction_variant", "edge_count", "node_count", "metric_name", "metric_value",
    ]
    summary_fields = [
        "null_family", "metric_name", "construction_family", "construction_variant",
        "real_value", "null_mean", "null_min", "null_max", "real_minus_null_mean",
        "empirical_exceedance_fraction", "null_count", "interpretation_label",
    ]

    out_cfg = cfg["outputs"]
    write_csv(output_dir / out_cfg["nodes_resolved_csv"], nodes, node_fields)
    write_csv(output_dir / out_cfg["edges_csv"], all_edge_rows, edge_fields)

    ref_rows = [{
        "source": a,
        "target": b,
        "weight": real_weights[(a, b)],
        "reference_core_rule": cfg["reference_core"]["definition"],
    } for a, b in sorted(ref_core)]
    write_csv(output_dir / out_cfg["reference_core_edges_csv"], ref_rows, ["source", "target", "weight", "reference_core_rule"])

    write_csv(output_dir / out_cfg["core_metrics_csv"], all_core_metrics, metric_fields)
    write_csv(output_dir / out_cfg["envelope_metrics_csv"], all_envelope_metrics, metric_fields)
    write_csv(output_dir / out_cfg["real_vs_null_summary_csv"], summary, summary_fields)
    write_csv(output_dir / out_cfg["family_summary_csv"], family_summary, ["family_id", "node_count", "labels"])
    write_csv(output_dir / out_cfg["null_family_inventory_csv"], null_inventory, ["object_id", "null_family", "repeat_index"])

    manifest = {
        "run_id": cfg["run"]["run_id"],
        "output_dir": cfg["run"]["output_dir"],
        "input_table_count": len(cfg["inputs"]["scan_tables"]),
        "node_count": len(nodes),
        "real_edge_count": len(real_edges),
        "reference_core_edge_count": len(ref_core),
        "object_count": len(object_weights),
        "null_family_counts": dict(Counter(x[1] for x in object_weights if x[1] != "real")),
        "row_counts": {
            "nodes_resolved": len(nodes),
            "edges": len(all_edge_rows),
            "core_metrics": len(all_core_metrics),
            "envelope_metrics": len(all_envelope_metrics),
            "real_vs_null_summary": len(summary),
            "family_summary": len(family_summary),
            "null_family_inventory": len(null_inventory),
            "warnings": len(warnings),
        },
    }

    with (output_dir / out_cfg["run_manifest_json"]).open("w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2, sort_keys=True)

    with (output_dir / out_cfg["warnings_json"]).open("w", encoding="utf-8") as f:
        json.dump(warnings, f, indent=2, sort_keys=True)

    with (output_dir / out_cfg["resolved_config_yaml"]).open("w", encoding="utf-8") as f:
        yaml.safe_dump(cfg, f, sort_keys=False)

    print(json.dumps(manifest, indent=2, sort_keys=True))
    if warnings:
        print("\nWarnings:")
        for w in warnings:
            print(f'{w["severity"]}: {w["message"]}')


def main() -> None:
    parser = argparse.ArgumentParser(description="Run BMS-IS01 isotope/structure specificity diagnostic.")
    parser.add_argument("--config", required=True, help="Path to YAML config.")
    args = parser.parse_args()
    run(Path(args.config))


if __name__ == "__main__":
    main()
