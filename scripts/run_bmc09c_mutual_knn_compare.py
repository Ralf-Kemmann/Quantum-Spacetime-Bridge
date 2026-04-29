#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
import subprocess
from pathlib import Path
from typing import Any, Dict, List

try:
    import yaml
except ImportError as exc:
    raise SystemExit("PyYAML is required: pip install pyyaml") from exc


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run BMC-09c mutual-kNN comparison sweep.")
    parser.add_argument("--config", default="data/bmc09c_mutual_knn_compare_config.yaml")
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
    cfg_file = Path(args.config).resolve()
    cfg = load_yaml(cfg_file)
    project_root = cfg_file.parent.parent

    py = cfg.get("python_bin", "python3")
    featuretable_script = project_root / cfg["scripts"]["bmc08c_featuretable_script"]
    featuretable_cfg = project_root / cfg["data"]["bmc08c_featuretable_config"]
    mutual_build_script = project_root / cfg["scripts"]["mutual_knn_build_script"]
    mutual_build_cfg = project_root / cfg["data"]["mutual_knn_build_config"]
    variant_runner = project_root / cfg["scripts"]["variant_runner"]
    out_root = project_root / cfg["run"]["output_root"]
    out_root.mkdir(parents=True, exist_ok=True)

    run_cmd([py, str(featuretable_script), "--config", str(featuretable_cfg)], project_root)
    run_cmd([py, str(mutual_build_script), "--config", str(mutual_build_cfg)], project_root)

    k_values = list(cfg["sweep"]["k_values"])
    base = cfg["base_runner_config"]
    rows = []

    for k in k_values:
        run_id = f"BMC09c_mutual_k_{k}_realdata_open"
        run_out_rel = f"runs/BMC-09/{run_id}"
        runner_cfg = {
            "run": {"run_id": run_id, "output_dir": run_out_rel, "seed": base["seed"]},
            "inputs": {
                "baseline_relational_table": f"data/bmc09c_mutual_knn_inputs/k_{k}/baseline_relational_table_real.csv",
                "node_metadata": f"data/bmc09c_mutual_knn_inputs/k_{k}/node_metadata_real.csv",
                "bmc04_reference_summary": None,
                "pair_neighborhood_matrix": None,
                "diffusion_distance_matrix": None,
            },
            "graph": dict(base["graph"]),
            "perturbation": dict(base["perturbation"]),
            "readouts": dict(base["readouts"]),
            "decision": dict(base["decision"]),
            "backbone_variants": dict(base["backbone_variants"]),
        }
        cfg_path = project_root / f"data/bmc09c_runner_config_k_{k}.yaml"
        write_yaml(cfg_path, runner_cfg)
        run_cmd([py, str(variant_runner), "--config", str(cfg_path)], project_root)

        run_summary = read_json(project_root / run_out_rel / "summary.json")
        graph_summary = read_json(project_root / f"data/bmc09c_mutual_knn_inputs/k_{k}/graph_build_summary.json")
        rows.append({
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

    with (out_root / "mutual_knn_sweep_summary.csv").open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=[
            "k","run_id","overall_status","variant_count","graph_node_count","graph_edge_count","connected_component_count","largest_component_size","mean_degree","graph_density"
        ])
        writer.writeheader()
        writer.writerows(rows)

    meta = {
        "sweep_k_values": k_values,
        "python_bin": py,
        "notes": [
            "BMC-09c compares mutual-kNN structure across k values.",
            "Same BMC-08c feature table, different graph rule than BMC-09a.",
            "No hidden component repairs are performed.",
        ],
    }
    (out_root / "mutual_knn_sweep_metadata.json").write_text(json.dumps(meta, indent=2), encoding="utf-8")
    print(f"Wrote: {out_root / 'mutual_knn_sweep_summary.csv'}")
    print(f"Wrote: {out_root / 'mutual_knn_sweep_metadata.json'}")

if __name__ == "__main__":
    main()
