#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, List

try:
    import yaml
except ImportError as exc:  # pragma: no cover
    raise SystemExit("PyYAML is required: pip install pyyaml") from exc


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run BMC-09b k-sweep on prebuilt BMC-09a k-NN graph inputs."
    )
    parser.add_argument(
        "--config",
        default="data/bmc09b_k_sweep_config.yaml",
        help="Path to YAML config.",
    )
    return parser.parse_args()


def load_yaml(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as handle:
        return yaml.safe_load(handle)


def write_yaml(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        yaml.safe_dump(data, handle, sort_keys=False)


def run_cmd(cmd: List[str], cwd: Path) -> None:
    proc = subprocess.run(cmd, cwd=str(cwd))
    if proc.returncode != 0:
        raise SystemExit(proc.returncode)


def read_json(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def main() -> None:
    args = parse_args()
    cfg_path = Path(args.config).resolve()
    cfg = load_yaml(cfg_path)
    project_root = cfg_path.parent.parent

    python_bin = cfg.get("python_bin", "python3")
    bmc08c_featuretable_script = project_root / cfg["scripts"]["bmc08c_featuretable_script"]
    bmc08c_featuretable_config = project_root / cfg["data"]["bmc08c_featuretable_config"]
    knn_build_script = project_root / cfg["scripts"]["bmc09a_knn_build_script"]
    knn_build_config = project_root / cfg["data"]["bmc09a_knn_build_config"]
    variant_runner = project_root / cfg["scripts"]["variant_runner"]

    out_root = project_root / cfg["run"]["output_root"]
    out_root.mkdir(parents=True, exist_ok=True)

    # Step 1: rebuild BMC-08c feature table to guarantee source consistency
    run_cmd([python_bin, str(bmc08c_featuretable_script), "--config", str(bmc08c_featuretable_config)], project_root)

    # Step 2: build all k-NN inputs
    run_cmd([python_bin, str(knn_build_script), "--config", str(knn_build_config)], project_root)

    k_values = list(cfg["sweep"]["k_values"])
    base_runner_cfg = cfg["base_runner_config"]

    summary_rows: List[Dict[str, Any]] = []

    for k in k_values:
        k_dir_rel = f"data/bmc09a_knn_inputs/k_{k}"
        run_id = f"BMC09b_k_{k}_realdata_open"
        run_output_rel = f"runs/BMC-09/{run_id}"

        runner_cfg = {
            "run": {
                "run_id": run_id,
                "output_dir": run_output_rel,
                "seed": base_runner_cfg["seed"],
            },
            "inputs": {
                "baseline_relational_table": f"{k_dir_rel}/baseline_relational_table_real.csv",
                "node_metadata": f"{k_dir_rel}/node_metadata_real.csv",
                "bmc04_reference_summary": None,
                "pair_neighborhood_matrix": None,
                "diffusion_distance_matrix": None,
            },
            "graph": dict(base_runner_cfg["graph"]),
            "perturbation": dict(base_runner_cfg["perturbation"]),
            "readouts": dict(base_runner_cfg["readouts"]),
            "decision": dict(base_runner_cfg["decision"]),
            "backbone_variants": dict(base_runner_cfg["backbone_variants"]),
        }

        runner_cfg_path = project_root / f"data/bmc09b_runner_config_k_{k}.yaml"
        write_yaml(runner_cfg_path, runner_cfg)

        run_cmd([python_bin, str(variant_runner), "--config", str(runner_cfg_path)], project_root)

        run_summary = read_json(project_root / run_output_rel / "summary.json")
        graph_summary = read_json(project_root / k_dir_rel / "graph_build_summary.json")

        summary_rows.append({
            "k": k,
            "run_id": run_id,
            "overall_status": run_summary["overall_status"],
            "variant_count": run_summary["variant_count"],
            "graph_node_count": graph_summary["graph_node_count"],
            "graph_edge_count": graph_summary["graph_edge_count"],
            "connected_component_count": graph_summary["connected_component_count"],
            "largest_component_size": graph_summary["largest_component_size"],
            "mean_degree": graph_summary["mean_degree"],
            "graph_density": graph_summary["graph_density"],
        })

    summary_csv = out_root / "k_sweep_summary.csv"
    with summary_csv.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=[
                "k", "run_id", "overall_status", "variant_count",
                "graph_node_count", "graph_edge_count", "connected_component_count",
                "largest_component_size", "mean_degree", "graph_density",
            ],
        )
        writer.writeheader()
        writer.writerows(summary_rows)

    meta = {
        "sweep_k_values": k_values,
        "python_bin": python_bin,
        "notes": [
            "BMC-09b k-sweep reruns BMC-09a logic for multiple k values.",
            "Each k value gets its own runner config and output folder.",
            "No hidden repairs of disconnected graphs are performed.",
        ],
    }
    (out_root / "k_sweep_metadata.json").write_text(json.dumps(meta, indent=2), encoding="utf-8")
    print(f"Wrote: {summary_csv}")
    print(f"Wrote: {out_root / 'k_sweep_metadata.json'}")


if __name__ == "__main__":
    main()
