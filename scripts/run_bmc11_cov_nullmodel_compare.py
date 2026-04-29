#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
import subprocess
from pathlib import Path
from typing import List, Dict, Any

try:
    import yaml
except ImportError as exc:
    raise SystemExit("PyYAML is required.") from exc


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run BMC-11 covariance-preserving nullmodel comparison.")
    parser.add_argument("--config", default="data/bmc11_cov_nullmodel_compare_config.yaml")
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
    featuretable_builder = project_root / cfg["scripts"]["featuretable_builder"]
    featuretable_cfg = project_root / cfg["data"]["featuretable_builder_config"]
    baseline_builder = project_root / cfg["scripts"]["baseline_builder"]
    variant_runner = project_root / cfg["scripts"]["variant_runner"]
    out_root = project_root / cfg["run"]["output_root"]
    out_root.mkdir(parents=True, exist_ok=True)

    run_cmd([py, str(featuretable_builder), "--config", str(featuretable_cfg)], project_root)

    base = cfg["base_runner_config"]
    seeds = list(cfg["sweep"]["seeds"])
    tau_cases = list(cfg["sweep"]["tau_cases"])
    rows: List[Dict[str, Any]] = []

    for seed in seeds:
        run_cmd([
            py, str(baseline_builder),
            "--input", str(project_root / "data" / "bmc11_cov_null_feature_table.csv"),
            "--seed", str(seed),
            "--output-dir", str(project_root / "data"),
        ], project_root)

        for case in tau_cases:
            tau = float(case["tau"])
            case_id = case["case_id"]
            run_id = f"BMC11_seed_{seed}_{case_id}_realdata_open"
            run_out_rel = f"runs/BMC-11/{run_id}"

            runner_cfg = {
                "run": {"run_id": run_id, "output_dir": run_out_rel, "seed": base["seed"]},
                "inputs": {
                    "baseline_relational_table": f"data/bmc11_baseline_relational_table_seed_{seed}.csv",
                    "node_metadata": f"data/bmc11_node_metadata_seed_{seed}.csv",
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
            runner_cfg["graph"]["threshold_tau"] = tau
            runner_cfg["run"]["run_label"] = case_id

            runner_cfg_path = project_root / f"data/bmc11_runner_config_seed_{seed}_{case_id}.yaml"
            write_yaml(runner_cfg_path, runner_cfg)

            run_cmd([py, str(variant_runner), "--config", str(runner_cfg_path)], project_root)

            run_summary = read_json(project_root / run_out_rel / "summary.json")
            rows.append({
                "seed": seed,
                "case_id": case_id,
                "tau": tau,
                "run_id": run_id,
                "overall_status": run_summary["overall_status"],
                "variant_count": run_summary["variant_count"],
            })

    summary_path = out_root / "cov_nullmodel_sweep_summary.csv"
    with summary_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=[
            "seed", "case_id", "tau", "run_id", "overall_status", "variant_count"
        ])
        writer.writeheader()
        writer.writerows(rows)

    meta = {
        "seeds": seeds,
        "tau_cases": tau_cases,
        "python_bin": py,
        "notes": [
            "BMC-11 uses covariance-preserving synthetic features.",
            "Same pipeline family, stronger nullmodel than BMC-10.",
            "This compare step tests whether threshold_tau_03 still stands out against covariance-matched null structure.",
        ],
    }
    (out_root / "cov_nullmodel_sweep_metadata.json").write_text(json.dumps(meta, indent=2), encoding="utf-8")
    print(f"Wrote: {summary_path}")
    print(f"Wrote: {out_root / 'cov_nullmodel_sweep_metadata.json'}")


if __name__ == "__main__":
    main()
