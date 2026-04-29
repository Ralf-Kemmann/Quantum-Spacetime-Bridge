#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
import subprocess
from pathlib import Path
from typing import List

try:
    import yaml
except ImportError as exc:
    raise SystemExit("PyYAML is required: pip install pyyaml") from exc

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run BMC-09d threshold/hybrid comparison sweep.")
    parser.add_argument("--config", default="data/bmc09d_threshold_hybrid_compare_config.yaml")
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

    py = cfg.get("python_bin", "python3")
    featuretable_script = project_root / cfg["scripts"]["bmc08c_featuretable_script"]
    featuretable_cfg = project_root / cfg["data"]["bmc08c_featuretable_config"]
    build_script = project_root / cfg["scripts"]["threshold_hybrid_build_script"]
    build_cfg = project_root / cfg["data"]["threshold_hybrid_build_config"]
    runner = project_root / cfg["scripts"]["variant_runner"]
    out_root = project_root / cfg["run"]["output_root"]
    out_root.mkdir(parents=True, exist_ok=True)

    run_cmd([py, str(featuretable_script), "--config", str(featuretable_cfg)], project_root)
    run_cmd([py, str(build_script), "--config", str(build_cfg)], project_root)

    base = cfg["base_runner_config"]
    cases = list(cfg["sweep"]["case_ids"])
    rows = []

    for case_id in cases:
        run_id = f"BMC09d_{case_id}_realdata_open"
        run_out_rel = f"runs/BMC-09/{run_id}"
        runner_cfg = {
            "run": {"run_id": run_id, "output_dir": run_out_rel, "seed": base["seed"]},
            "inputs": {
                "baseline_relational_table": f"data/bmc09d_threshold_hybrid_inputs/{case_id}/baseline_relational_table_real.csv",
                "node_metadata": f"data/bmc09d_threshold_hybrid_inputs/{case_id}/node_metadata_real.csv",
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
        runner_cfg_path = project_root / f"data/bmc09d_runner_config_{case_id}.yaml"
        write_yaml(runner_cfg_path, runner_cfg)
        run_cmd([py, str(runner), "--config", str(runner_cfg_path)], project_root)

        run_summary = read_json(project_root / run_out_rel / "summary.json")
        graph_summary = read_json(project_root / f"data/bmc09d_threshold_hybrid_inputs/{case_id}/graph_build_summary.json")
        rows.append({
            "case_id": case_id,
            "run_id": run_id,
            "overall_status": run_summary["overall_status"],
            "variant_count": run_summary["variant_count"],
            "graph_construction_method": graph_summary["graph_construction_method"],
            "graph_construction_parameters": graph_summary["graph_construction_parameters"],
            "graph_node_count": graph_summary["graph_node_count"],
            "graph_edge_count": graph_summary["graph_edge_count"],
            "connected_component_count": graph_summary["connected_component_count"],
            "largest_component_size": graph_summary["largest_component_size"],
            "mean_degree": graph_summary["mean_degree"],
            "graph_density": graph_summary["graph_density"],
            "isolated_node_count": graph_summary["isolated_node_count"],
        })

    with (out_root / "threshold_hybrid_sweep_summary.csv").open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=[
            "case_id","run_id","overall_status","variant_count","graph_construction_method","graph_construction_parameters","graph_node_count","graph_edge_count","connected_component_count","largest_component_size","mean_degree","graph_density","isolated_node_count"
        ])
        writer.writeheader()
        writer.writerows(rows)

    meta = {
        "case_ids": cases,
        "python_bin": py,
        "notes": [
            "BMC-09d compares threshold and hybrid local graph regimes.",
            "Same BMC-08c feature table, different local graph rules.",
            "No hidden component repairs are performed.",
        ],
    }
    (out_root / "threshold_hybrid_sweep_metadata.json").write_text(json.dumps(meta, indent=2), encoding="utf-8")
    print(f"Wrote: {out_root / 'threshold_hybrid_sweep_summary.csv'}")
    print(f"Wrote: {out_root / 'threshold_hybrid_sweep_metadata.json'}")

if __name__ == "__main__":
    main()
