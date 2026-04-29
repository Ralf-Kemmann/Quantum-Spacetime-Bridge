#!/usr/bin/env python3
"""
BMC-12c Backbone-Aware Matched Leave-One-Out Runner.

Adapter + collector:
- read BMC-12b matched edges
- write old-style BMC graph inputs/configs per case
- call scripts/bmc07_backbone_variation_runner.py
- collect backbone_variant_summary.csv
- compare each case against the BMC09d threshold_tau_03 reference decision
"""

from __future__ import annotations

import argparse
import csv
import json
import shutil
import subprocess
from pathlib import Path
from typing import Any, Dict, List, Sequence

try:
    import yaml
except ImportError as exc:
    raise SystemExit("Missing dependency: PyYAML. Install with: python3 -m pip install pyyaml") from exc


def load_yaml(path: Path) -> Dict[str, Any]:
    with path.open("r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    if not isinstance(data, dict):
        raise ValueError(f"Config is not a mapping: {path}")
    return data


def write_yaml(path: Path, data: Dict[str, Any]) -> None:
    with path.open("w", encoding="utf-8") as f:
        yaml.safe_dump(data, f, sort_keys=False, allow_unicode=True)


def read_csv(path: Path) -> List[Dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as f:
        rows = list(csv.DictReader(f))
    if not rows:
        raise ValueError(f"CSV has no rows: {path}")
    return [dict(r) for r in rows]


def write_csv(path: Path, rows: Sequence[Dict[str, Any]], fieldnames: Sequence[str]) -> None:
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def project_path(root: Path, value: str) -> Path:
    p = Path(value)
    return p if p.is_absolute() else root / p


def safe_case_id(case_id: str) -> str:
    return "".join(ch if (ch.isalnum() or ch in "_-.") else "_" for ch in case_id)


def infer_dropped_feature(case_id: str) -> str:
    prefix = "matched_drop_"
    return case_id[len(prefix):] if case_id.startswith(prefix) else ""


def build_case_input_and_config(
    *,
    root: Path,
    cfg: Dict[str, Any],
    case_id: str,
    edge_rows: Sequence[Dict[str, str]],
) -> Path:
    case_safe = safe_case_id(case_id)

    input_root = project_path(root, cfg["generated"]["input_root"])
    config_root = project_path(root, cfg["generated"]["config_root"])
    output_root = project_path(root, cfg["generated"]["output_root"])

    case_input_dir = input_root / case_safe
    case_output_dir = output_root / case_safe
    case_config_path = config_root / f"{case_safe}.yaml"

    case_input_dir.mkdir(parents=True, exist_ok=True)
    case_output_dir.mkdir(parents=True, exist_ok=True)
    config_root.mkdir(parents=True, exist_ok=True)

    rel_table = case_input_dir / "baseline_relational_table_real.csv"
    rel_rows = [
        {"source": r["source"], "target": r["target"], "weight": r["weight"]}
        for r in edge_rows
    ]
    write_csv(rel_table, rel_rows, ["source", "target", "weight"])

    node_src = project_path(root, cfg["inputs"]["reference_node_metadata"])
    node_dst = case_input_dir / "node_metadata_real.csv"
    shutil.copyfile(node_src, node_dst)

    runner_cfg = {
        "run": {
            "run_id": f"BMC12c_{case_safe}",
            "output_dir": str(case_output_dir.relative_to(root)),
            "seed": 101,
        },
        "inputs": {
            "baseline_relational_table": str(rel_table.relative_to(root / "data")),
            "node_metadata": str(node_dst.relative_to(root / "data")),
            "bmc04_reference_summary": None,
            "pair_neighborhood_matrix": None,
            "diffusion_distance_matrix": None,
        },
        "graph": dict(cfg["graph"]),
        "perturbation": dict(cfg["perturbation"]),
        "readouts": dict(cfg["readouts"]),
        "decision": dict(cfg["decision"]),
        "backbone_variants": dict(cfg["backbone_variants"]),
    }

    write_yaml(case_config_path, runner_cfg)
    return case_config_path


def compare_case(
    *,
    case_id: str,
    rows: Sequence[Dict[str, str]],
    reference_label: str,
    reference_arm: str,
) -> Dict[str, Any]:
    retained = sum(
        1
        for r in rows
        if r.get("decision_label") == reference_label and r.get("dominant_arm") == reference_arm
    )
    total = len(rows)
    failed = total - retained
    if total > 0 and retained == total:
        status = "decision_retained"
    elif retained > 0:
        status = "decision_partially_retained"
    else:
        status = "decision_not_retained"
    return {
        "case_id": case_id,
        "dropped_feature": infer_dropped_feature(case_id),
        "variant_count": total,
        "retained_variant_count": retained,
        "retained_fraction": retained / total if total else 0.0,
        "failed_variant_count": failed,
        "all_variants_retained": str(total > 0 and retained == total).lower(),
        "any_fragment_or_failure": str(failed > 0).lower(),
        "bmc12c_decision_status": status,
    }


def write_readout(path: Path, run_id: str, reference_label: str, reference_arm: str, rows: Sequence[Dict[str, Any]]) -> None:
    lines = [
        "# BMC-12c Backbone-Aware Matched Leave-One-Out Readout",
        "",
        "## Run",
        "",
        f"- run_id: `{run_id}`",
        f"- reference decision_label: `{reference_label}`",
        f"- reference dominant_arm: `{reference_arm}`",
        "",
        "## Befund",
        "",
        "BMC-12c re-ran the established BMC-09d backbone-variant decision logic on BMC-12b matched graph cases.",
        "",
        "| case_id | dropped_feature | retained_variants | retained_fraction | status |",
        "|---|---:|---:|---:|---|",
    ]
    for r in rows:
        lines.append(
            f"| {r['case_id']} | {r['dropped_feature'] or '-'} | "
            f"{r['retained_variant_count']}/{r['variant_count']} | "
            f"{float(r['retained_fraction']):.3f} | {r['bmc12c_decision_status']} |"
        )
    lines += [
        "",
        "## Interpretation",
        "",
        "A retained decision means the old BMC-09d criteria still classify the graph as backbone-localized with `dominant_arm = backbone_only`.",
        "",
        "## Hypothese",
        "",
        "Feature drops that fail or partially retain the decision identify features contributing to decision-level backbone structure.",
        "",
        "## Offene Lücke",
        "",
        "This remains a graph-diagnostic robustness test and does not establish physical meaning.",
        "",
    ]
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", required=True)
    ap.add_argument("--prepare-only", action="store_true")
    args = ap.parse_args()

    root = Path.cwd()
    cfg = load_yaml(project_path(root, args.config))
    run_id = str(cfg.get("run_id", "BMC12c_backbone_aware_matched_loo_open"))

    edges_path = project_path(root, cfg["inputs"]["bmc12b_edges"])
    variant_runner = project_path(root, cfg["variant_runner"])
    python_bin = str(cfg.get("python_bin", "python3"))
    output_root = project_path(root, cfg["generated"]["output_root"])
    output_root.mkdir(parents=True, exist_ok=True)

    include_cases = list(cfg["cases"]["include_case_ids"])
    edges = read_csv(edges_path)
    required = {"case_id", "source", "target", "weight"}
    missing = required - set(edges[0].keys())
    if missing:
        raise ValueError(f"BMC-12b edge file missing columns: {sorted(missing)}")

    by_case: Dict[str, List[Dict[str, str]]] = {}
    for row in edges:
        if row["case_id"] in include_cases:
            by_case.setdefault(row["case_id"], []).append(row)

    missing_cases = [c for c in include_cases if c not in by_case]
    if missing_cases:
        raise ValueError(f"Requested cases not found in BMC-12b edge file: {missing_cases}")

    generated_configs: Dict[str, Path] = {}
    for case_id in include_cases:
        generated_configs[case_id] = build_case_input_and_config(
            root=root, cfg=cfg, case_id=case_id, edge_rows=by_case[case_id]
        )

    if args.prepare_only:
        print("BMC-12c prepare-only completed.")
        for case_id, path in generated_configs.items():
            print(f"{case_id}: {path}")
        return

    for case_id, config_path in generated_configs.items():
        cmd = [python_bin, str(variant_runner), "--config", str(config_path)]
        print("Running:", " ".join(cmd))
        result = subprocess.run(cmd, cwd=root)
        if result.returncode != 0:
            raise SystemExit(f"Variant runner failed for {case_id} with exit code {result.returncode}")

    reference_label = str(cfg["reference_decision"]["decision_label"])
    reference_arm = str(cfg["reference_decision"]["dominant_arm"])

    all_variant_rows: List[Dict[str, Any]] = []
    comparison_rows: List[Dict[str, Any]] = []

    for case_id in include_cases:
        case_safe = safe_case_id(case_id)
        summary_path = root / "data" / output_root.relative_to(root) / case_safe / "backbone_variant_summary.csv"
        summary_rows = read_csv(summary_path)

        for row in summary_rows:
            out = dict(row)
            out["case_id"] = case_id
            out["dropped_feature"] = infer_dropped_feature(case_id)
            all_variant_rows.append(out)

        comparison_rows.append(
            compare_case(
                case_id=case_id,
                rows=summary_rows,
                reference_label=reference_label,
                reference_arm=reference_arm,
            )
        )

    variant_fields = [
        "case_id", "dropped_feature",
        "variant_name", "method", "variant_parameters",
        "backbone_node_count", "off_backbone_node_count", "coupling_edge_count",
        "decision_label", "dominant_arm",
        "full_graph_arrangement_signal", "backbone_only_arrangement_signal",
        "off_backbone_only_arrangement_signal", "coupling_only_arrangement_signal",
    ]
    comparison_fields = [
        "case_id", "dropped_feature", "variant_count", "retained_variant_count",
        "retained_fraction", "failed_variant_count", "all_variants_retained",
        "any_fragment_or_failure", "bmc12c_decision_status",
    ]

    variant_out = output_root / "bmc12c_backbone_variant_summary_all_cases.csv"
    comparison_out = output_root / "bmc12c_decision_comparison_summary.csv"
    metrics_out = output_root / "bmc12c_metrics.json"
    readout_out = output_root / "bmc12c_backbone_aware_readout.md"

    write_csv(variant_out, all_variant_rows, variant_fields)
    write_csv(comparison_out, comparison_rows, comparison_fields)
    metrics_out.write_text(json.dumps({
        "run_id": run_id,
        "case_ids": include_cases,
        "reference_decision": {"decision_label": reference_label, "dominant_arm": reference_arm},
        "comparison": comparison_rows,
    }, indent=2, ensure_ascii=False), encoding="utf-8")
    write_readout(readout_out, run_id, reference_label, reference_arm, comparison_rows)

    print("BMC-12c backbone-aware matched leave-one-out completed.")
    print(f"Wrote: {variant_out}")
    print(f"Wrote: {comparison_out}")
    print(f"Wrote: {metrics_out}")
    print(f"Wrote: {readout_out}")


if __name__ == "__main__":
    main()
