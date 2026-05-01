#!/usr/bin/env python3
"""
BMS-IS01b — Family-Balanced Matter Signature Specificity Runner

This runner refines BMS-IS01 by selecting a family-balanced reference core and
optionally excluding same-isotope cross-run edges from the reference core.

Boundary:
This is a methodological diagnostic. It does not recover a physical metric and
does not prove emergent geometry.
"""

from __future__ import annotations

import argparse
import csv
import json
import math
import random
import statistics
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Dict, List, Tuple

try:
    import yaml
except ImportError as exc:
    raise SystemExit("PyYAML is required. Install with: python -m pip install pyyaml") from exc


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

    for table in cfg["inputs"]["scan_tables"]:
        p = root / table["source_path"]
        if not p.exists():
            warnings.append({"severity": "warning", "message": f"Input scan table not found: {p}"})
            continue

        delta_column = table.get("delta_column", "")
        with p.open(newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for source_row in reader:
                isotope = source_row.get("isotope", "")
                node_id = f'{table["family_id"]}__{table["run_id"]}__{isotope}'
                rows_out.append({
                    "node_id": node_id,
                    "run_id": table["run_id"],
                    "family_id": table["family_id"],
                    "test_axis": table.get("test_axis", ""),
                    "isotope": isotope,
                    "label": source_row.get("label", isotope),
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
                    "matter_sensitive_delta": source_row.get(delta_column, ""),
                    "source_delta_column": delta_column,
                    "source_file": str(table["source_path"]),
                })

    if not rows_out:
        warnings.append({"severity": "warning", "message": "No input rows loaded."})
    return rows_out


def make_vectors(nodes: List[Dict[str, Any]], cfg: Dict[str, Any], warnings: List[Dict[str, str]]) -> Dict[str, List[float]]:
    adapter = cfg["adapter"]
    vector_columns = adapter["vector_columns"]
    log10_columns = set(adapter.get("log10_columns", []))
    normalize = bool(adapter.get("normalize_columns", True))

    raw: Dict[str, List[float]] = {}
    by_col: Dict[str, List[float]] = {c: [] for c in vector_columns}

    for node in nodes:
        vals = []
        for col in vector_columns:
            x = as_float(node.get(col))
            if col in log10_columns:
                if x > 0:
                    x = math.log10(x)
                else:
                    warnings.append({"severity": "warning", "message": f"Non-positive log10 value for {col} in {node['node_id']}"})
                    x = float("nan")
            vals.append(x)
            if math.isfinite(x):
                by_col[col].append(x)
        raw[node["node_id"]] = vals

    mean = {}
    sd = {}
    for col, vals in by_col.items():
        mean[col] = statistics.mean(vals) if vals else 0.0
        sd[col] = statistics.pstdev(vals) if len(vals) > 1 else 1.0
        if sd[col] == 0:
            sd[col] = 1.0

    vectors = {}
    for node_id, vals in raw.items():
        out = []
        for col, x in zip(vector_columns, vals):
            if not math.isfinite(x):
                x = mean[col]
            if normalize:
                x = (x - mean[col]) / sd[col]
            out.append(x)
        vectors[node_id] = out
    return vectors


def euclidean(a: List[float], b: List[float]) -> float:
    return math.sqrt(sum((x - y) ** 2 for x, y in zip(a, b)))


def build_edges(nodes: List[Dict[str, Any]], vectors: Dict[str, List[float]], object_id: str, null_family: str, repeat_index: int | str) -> List[Dict[str, Any]]:
    ids = [n["node_id"] for n in nodes]
    rows = []
    for i, a in enumerate(ids):
        for b in ids[i + 1:]:
            d = euclidean(vectors[a], vectors[b])
            w = math.exp(-d)
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


def edge_weights_map(edges: List[Dict[str, Any]]) -> Dict[Edge, float]:
    return {edge_key(e["source"], e["target"]): as_float(e["weight"]) for e in edges}


def map_to_edge_rows(weights: Dict[Edge, float], object_id: str, null_family: str, repeat_index: int | str) -> List[Dict[str, Any]]:
    return [{
        "object_id": object_id,
        "null_family": null_family,
        "repeat_index": repeat_index,
        "source": a,
        "target": b,
        "weight": w,
        "distance": -math.log(max(w, 1e-300)),
    } for (a, b), w in weights.items()]


def top_edges(weights: Dict[Edge, float], count: int) -> Dict[Edge, float]:
    return dict(sorted(weights.items(), key=lambda kv: abs(kv[1]), reverse=True)[:count])


def threshold_edges(weights: Dict[Edge, float], threshold: float) -> Dict[Edge, float]:
    return {e: w for e, w in weights.items() if abs(w) >= threshold}


def mutual_knn_edges(weights: Dict[Edge, float], node_ids: List[str], k: int) -> Dict[Edge, float]:
    neigh = {n: [] for n in node_ids}
    for (a, b), w in weights.items():
        neigh[a].append((b, w))
        neigh[b].append((a, w))

    topn = {}
    for n, vals in neigh.items():
        topn[n] = {x for x, _ in sorted(vals, key=lambda t: abs(t[1]), reverse=True)[:k]}

    return {(a, b): w for (a, b), w in weights.items() if b in topn[a] and a in topn[b]}


def mst_edges(weights: Dict[Edge, float], node_ids: List[str]) -> Dict[Edge, float]:
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

    out = {}
    for (a, b), w in sorted(weights.items(), key=lambda kv: abs(kv[1]), reverse=True):
        if union(a, b):
            out[(a, b)] = w
        if len(out) >= len(node_ids) - 1:
            break
    return out


def construct_variants(weights: Dict[Edge, float], node_ids: List[str], cfg: Dict[str, Any]) -> List[Dict[str, Any]]:
    fams = cfg["construction_families"]
    variants = []

    if fams["top_strength"]["enabled"]:
        for n in fams["top_strength"]["edge_counts"]:
            variants.append({"construction_family": "top_strength", "construction_variant": f"top_edges_{n}", "edges": top_edges(weights, int(n))})

    if fams["threshold"]["enabled"]:
        for t in fams["threshold"]["thresholds"]:
            variants.append({"construction_family": "threshold", "construction_variant": f"abs_weight_ge_{t}", "edges": threshold_edges(weights, float(t))})

    if fams["mutual_knn"]["enabled"]:
        for k in fams["mutual_knn"]["k_values"]:
            variants.append({"construction_family": "mutual_knn", "construction_variant": f"k_{k}", "edges": mutual_knn_edges(weights, node_ids, int(k))})

    if fams["maximum_spanning_tree"]["enabled"]:
        variants.append({"construction_family": "maximum_spanning_tree", "construction_variant": "abs_weight_mst", "edges": mst_edges(weights, node_ids)})

    return variants


def is_same_isotope_cross_run(a: str, b: str, meta: Dict[str, Dict[str, Any]]) -> bool:
    ma, mb = meta[a], meta[b]
    return (
        ma.get("family_id") == mb.get("family_id")
        and ma.get("isotope") == mb.get("isotope")
        and ma.get("run_id") != mb.get("run_id")
    )


def select_reference_core(
    weights: Dict[Edge, float],
    nodes: List[Dict[str, Any]],
    cfg: Dict[str, Any],
    warnings: List[Dict[str, str]],
) -> List[Dict[str, Any]]:
    meta = {n["node_id"]: n for n in nodes}
    settings = cfg["reference_core"]
    edges_per_family = int(settings.get("edges_per_family", 3))
    exclude_same = bool(settings.get("exclude_same_isotope_cross_run", True))
    fallback = bool(settings.get("fallback_allow_same_isotope_if_needed", False))

    families = sorted({n["family_id"] for n in nodes})
    core_rows = []

    for family in families:
        family_nodes = {n["node_id"] for n in nodes if n["family_id"] == family}
        candidates = []
        excluded = []

        for (a, b), w in weights.items():
            if a not in family_nodes or b not in family_nodes:
                continue
            ex = exclude_same and is_same_isotope_cross_run(a, b, meta)
            row = {
                "family_id": family,
                "source": a,
                "target": b,
                "weight": w,
                "reference_core_rule": settings.get("mode", "family_balanced_top_edges"),
                "excluded_same_isotope_cross_run": ex,
                "source_isotope": meta[a].get("isotope", ""),
                "target_isotope": meta[b].get("isotope", ""),
                "source_run_id": meta[a].get("run_id", ""),
                "target_run_id": meta[b].get("run_id", ""),
            }
            if ex:
                excluded.append(row)
            else:
                candidates.append(row)

        selected = sorted(candidates, key=lambda r: abs(as_float(r["weight"])), reverse=True)[:edges_per_family]

        if len(selected) < edges_per_family:
            warnings.append({
                "severity": "warning",
                "message": f"Family {family} has only {len(selected)} eligible core edges after same-isotope exclusion; requested {edges_per_family}.",
            })
            if fallback:
                need = edges_per_family - len(selected)
                selected_keys = {edge_key(r["source"], r["target"]) for r in selected}
                extra = [
                    r for r in sorted(excluded, key=lambda r: abs(as_float(r["weight"])), reverse=True)
                    if edge_key(r["source"], r["target"]) not in selected_keys
                ][:need]
                for r in extra:
                    r["fallback_selected_same_isotope_cross_run"] = True
                selected.extend(extra)

        for r in selected:
            r.setdefault("fallback_selected_same_isotope_cross_run", False)
        core_rows.extend(selected)

    return core_rows


def metrics_for_object(
    object_id: str,
    null_family: str,
    repeat_index: int | str,
    weights: Dict[Edge, float],
    nodes: List[Dict[str, Any]],
    ref_core_edges: set[Edge],
    cfg: Dict[str, Any],
) -> tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    node_ids = [n["node_id"] for n in nodes]
    node_family = {n["node_id"]: n["family_id"] for n in nodes}
    ref_nodes = {x for e in ref_core_edges for x in e}
    variants = construct_variants(weights, node_ids, cfg)

    core_rows = []
    env_rows = []

    for var in variants:
        env_edges = set(var["edges"].keys())
        env_nodes = {x for e in env_edges for x in e}

        edge_containment = len(ref_core_edges & env_edges) / len(ref_core_edges) if ref_core_edges else 0.0
        node_containment = len(ref_nodes & env_nodes) / len(ref_nodes) if ref_nodes else 0.0
        if env_edges:
            family_purity = sum(1 for a, b in env_edges if node_family.get(a) == node_family.get(b)) / len(env_edges)
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
            env_rows.append(row)

        for metric_name, value in [
            ("envelope_core_edge_containment", edge_containment),
            ("envelope_core_node_containment", node_containment),
        ]:
            row = dict(base)
            row["metric_name"] = metric_name
            row["metric_value"] = value
            core_rows.append(row)

    return core_rows, env_rows


def summarize(real_rows: List[Dict[str, Any]], null_rows: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    real_index = {
        (r["metric_name"], r["construction_family"], r["construction_variant"]): as_float(r["metric_value"])
        for r in real_rows
    }
    grouped: Dict[Tuple[str, str, str, str], List[float]] = defaultdict(list)
    for r in null_rows:
        grouped[(r["null_family"], r["metric_name"], r["construction_family"], r["construction_variant"])].append(as_float(r["metric_value"]))

    out = []
    for (null_family, metric_name, family, variant), vals in sorted(grouped.items()):
        vals = [v for v in vals if math.isfinite(v)]
        real = real_index.get((metric_name, family, variant), float("nan"))
        mean = statistics.mean(vals) if vals else float("nan")
        mn = min(vals) if vals else float("nan")
        mx = max(vals) if vals else float("nan")
        exceed = sum(1 for v in vals if v >= real) / len(vals) if vals and math.isfinite(real) else float("nan")
        delta = real - mean if math.isfinite(real) and math.isfinite(mean) else float("nan")

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
            "construction_family": family,
            "construction_variant": variant,
            "real_value": real,
            "null_mean": mean,
            "null_min": mn,
            "null_max": mx,
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
    outdir = root / cfg["run"]["output_dir"]
    outdir.mkdir(parents=True, exist_ok=True)

    warnings: List[Dict[str, str]] = []
    nodes = load_nodes(cfg, root, warnings)
    vectors = make_vectors(nodes, cfg, warnings)
    real_edges = build_edges(nodes, vectors, "real", "real", "real")
    real_weights = edge_weights_map(real_edges)

    ref_rows = select_reference_core(real_weights, nodes, cfg, warnings)
    ref_core_edges = {edge_key(r["source"], r["target"]) for r in ref_rows}

    all_edge_rows = list(real_edges)
    object_weights: List[Tuple[str, str, int | str, Dict[Edge, float]]] = [("real", "real", "real", real_weights)]
    null_inventory = []

    nf = cfg["null_families"]
    pairs = list(real_weights.keys())
    weights_list = list(real_weights.values())

    if nf["degree_weight_preserving_rewire"]["enabled"]:
        for i in range(int(nf["degree_weight_preserving_rewire"]["repeats"])):
            shuffled = weights_list[:]
            rng.shuffle(shuffled)
            wmap = dict(zip(pairs, shuffled))
            oid = f"degree_weight_preserving_rewire_{i:03d}"
            object_weights.append((oid, "degree_weight_preserving_rewire", i, wmap))
            all_edge_rows.extend(map_to_edge_rows(wmap, oid, "degree_weight_preserving_rewire", i))
            null_inventory.append({"object_id": oid, "null_family": "degree_weight_preserving_rewire", "repeat_index": i})

    if nf["feature_structured_shuffle"]["enabled"]:
        by_family: Dict[str, List[str]] = defaultdict(list)
        for n in nodes:
            by_family[n["family_id"]].append(n["node_id"])

        for i in range(int(nf["feature_structured_shuffle"]["repeats"])):
            sv = {k: v[:] for k, v in vectors.items()}
            for fam, ids in by_family.items():
                vecs = [vectors[x][:] for x in ids]
                rng.shuffle(vecs)
                for node_id, vec in zip(ids, vecs):
                    sv[node_id] = vec
            oid = f"feature_structured_shuffle_{i:03d}"
            edges = build_edges(nodes, sv, oid, "feature_structured_shuffle", i)
            wmap = edge_weights_map(edges)
            object_weights.append((oid, "feature_structured_shuffle", i, wmap))
            all_edge_rows.extend(edges)
            null_inventory.append({"object_id": oid, "null_family": "feature_structured_shuffle", "repeat_index": i})

    if nf["core_seeded_decoy"]["enabled"]:
        settings = nf["core_seeded_decoy"]
        sorted_weights = sorted(weights_list)
        q = float(settings.get("seed_weight_quantile", 0.90))
        q_index = min(len(sorted_weights) - 1, max(0, int(q * (len(sorted_weights) - 1))))
        high_weights = [w for w in sorted_weights if w >= sorted_weights[q_index]]
        if not high_weights:
            high_weights = sorted_weights[-max(1, len(ref_core_edges)):]
        for i in range(int(settings["repeats"])):
            shuffled = weights_list[:]
            rng.shuffle(shuffled)
            wmap = dict(zip(pairs, shuffled))
            for e in ref_core_edges:
                wmap[e] = rng.choice(high_weights)
            oid = f"core_seeded_decoy_{i:03d}"
            object_weights.append((oid, "core_seeded_decoy", i, wmap))
            all_edge_rows.extend(map_to_edge_rows(wmap, oid, "core_seeded_decoy", i))
            null_inventory.append({"object_id": oid, "null_family": "core_seeded_decoy", "repeat_index": i})

    all_core, all_env = [], []
    real_core, real_env, null_core, null_env = [], [], [], []

    for oid, nfam, rep, wmap in object_weights:
        cr, er = metrics_for_object(oid, nfam, rep, wmap, nodes, ref_core_edges, cfg)
        all_core.extend(cr)
        all_env.extend(er)
        if nfam == "real":
            real_core.extend(cr)
            real_env.extend(er)
        else:
            null_core.extend(cr)
            null_env.extend(er)

    summary = summarize(real_env, null_env)

    family_summary = []
    for fam in sorted({n["family_id"] for n in nodes}):
        labels = sorted({n["label"] for n in nodes if n["family_id"] == fam})
        family_summary.append({"family_id": fam, "node_count": sum(1 for n in nodes if n["family_id"] == fam), "labels": ";".join(labels)})

    out = cfg["outputs"]
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
    ref_fields = [
        "family_id", "source", "target", "weight", "reference_core_rule",
        "excluded_same_isotope_cross_run", "fallback_selected_same_isotope_cross_run",
        "source_isotope", "target_isotope", "source_run_id", "target_run_id",
    ]
    metric_fields = [
        "object_id", "null_family", "repeat_index", "construction_family",
        "construction_variant", "edge_count", "node_count", "metric_name", "metric_value",
    ]
    summary_fields = [
        "null_family", "metric_name", "construction_family", "construction_variant",
        "real_value", "null_mean", "null_min", "null_max", "real_minus_null_mean",
        "empirical_exceedance_fraction", "null_count", "interpretation_label",
    ]

    write_csv(outdir / out["nodes_resolved_csv"], nodes, node_fields)
    write_csv(outdir / out["edges_csv"], all_edge_rows, edge_fields)
    write_csv(outdir / out["reference_core_edges_csv"], ref_rows, ref_fields)
    write_csv(outdir / out["core_metrics_csv"], all_core, metric_fields)
    write_csv(outdir / out["envelope_metrics_csv"], all_env, metric_fields)
    write_csv(outdir / out["real_vs_null_summary_csv"], summary, summary_fields)
    write_csv(outdir / out["family_summary_csv"], family_summary, ["family_id", "node_count", "labels"])
    write_csv(outdir / out["null_family_inventory_csv"], null_inventory, ["object_id", "null_family", "repeat_index"])

    manifest = {
        "run_id": cfg["run"]["run_id"],
        "output_dir": cfg["run"]["output_dir"],
        "input_table_count": len(cfg["inputs"]["scan_tables"]),
        "node_count": len(nodes),
        "real_edge_count": len(real_edges),
        "reference_core_edge_count": len(ref_core_edges),
        "reference_core_mode": cfg["reference_core"].get("mode"),
        "exclude_same_isotope_cross_run": cfg["reference_core"].get("exclude_same_isotope_cross_run"),
        "object_count": len(object_weights),
        "null_family_counts": dict(Counter(x[1] for x in object_weights if x[1] != "real")),
        "row_counts": {
            "nodes_resolved": len(nodes),
            "edges": len(all_edge_rows),
            "reference_core_edges": len(ref_rows),
            "core_metrics": len(all_core),
            "envelope_metrics": len(all_env),
            "real_vs_null_summary": len(summary),
            "family_summary": len(family_summary),
            "null_family_inventory": len(null_inventory),
            "warnings": len(warnings),
        },
    }

    with (outdir / out["run_manifest_json"]).open("w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2, sort_keys=True)
    with (outdir / out["warnings_json"]).open("w", encoding="utf-8") as f:
        json.dump(warnings, f, indent=2, sort_keys=True)
    with (outdir / out["resolved_config_yaml"]).open("w", encoding="utf-8") as f:
        yaml.safe_dump(cfg, f, sort_keys=False)

    print(json.dumps(manifest, indent=2, sort_keys=True))
    if warnings:
        print("\nWarnings:")
        for w in warnings:
            print(f'{w["severity"]}: {w["message"]}')


def main() -> None:
    parser = argparse.ArgumentParser(description="Run BMS-IS01b family-balanced matter specificity diagnostic.")
    parser.add_argument("--config", required=True)
    args = parser.parse_args()
    run(Path(args.config))


if __name__ == "__main__":
    main()
