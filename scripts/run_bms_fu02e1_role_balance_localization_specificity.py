#!/usr/bin/env python3
"""
BMS-FU02e1 — Role-Balance Localization Specificity Extension

Purpose:
  Compare the real FU02d1/FU02e carrier-face localization profile against null
  replicates using joint compactness and role-balance metrics.

Interpretation:
  Diagnostic profile comparison only; not a formal physical p-value.
"""

from __future__ import annotations

import argparse
import csv
import json
import math
import statistics
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Dict, List

try:
    import yaml
except ImportError as exc:
    raise SystemExit("PyYAML is required. Install with: python -m pip install pyyaml") from exc


def read_yaml(path: Path) -> Dict[str, Any]:
    with path.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def read_csv(path: Path) -> List[Dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def write_csv(path: Path, rows: List[Dict[str, Any]], fieldnames: List[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        for r in rows:
            w.writerow({k: r.get(k, "") for k in fieldnames})


def as_float(x: Any, default: float = 0.0) -> float:
    try:
        if x is None or x == "":
            return default
        return float(x)
    except Exception:
        return default


def summarize(vals: List[float]) -> Dict[str, float]:
    if not vals:
        return {
            "min": 0.0, "mean": 0.0, "std": 0.0, "median": 0.0, "max": 0.0
        }
    return {
        "min": min(vals),
        "mean": statistics.mean(vals),
        "std": statistics.pstdev(vals) if len(vals) > 1 else 0.0,
        "median": statistics.median(vals),
        "max": max(vals),
    }


def interpretation(near_frac: float, strict_frac: float, min_dist: float) -> str:
    if strict_frac >= 0.05 or near_frac >= 0.20:
        return "near_real_profiles_common"
    if strict_frac > 0 or near_frac > 0:
        return "near_real_profiles_present_but_rare"
    if min_dist <= 2.0:
        return "profile_distance_overlaps_real_neighborhood"
    return "near_real_profiles_absent"


def run(config_path: Path) -> None:
    root = Path.cwd()
    cfg = read_yaml(config_path)
    outdir = root / cfg["run"]["output_dir"]
    outdir.mkdir(parents=True, exist_ok=True)

    warnings: List[Dict[str, str]] = []

    fu02e_dir = root / cfg["inputs"]["fu02e_output_dir"]
    fu02e_manifest = read_json(fu02e_dir / "bms_fu02e_run_manifest.json")
    fu02e_warnings = read_json(fu02e_dir / "bms_fu02e_warnings.json") if (fu02e_dir / "bms_fu02e_warnings.json").exists() else []
    if fu02e_warnings:
        warnings.append({"severity": "info", "message": f"FU02e warnings carried forward: {len(fu02e_warnings)}"})

    real = read_json(fu02e_dir / "bms_fu02e_real_face_metrics.json")
    null_rows = read_csv(fu02e_dir / "bms_fu02e_null_localization_metrics.csv")

    primary = list(cfg["profile"]["primary_metrics"])
    secondary = list(cfg["profile"].get("secondary_metrics", []))
    all_metrics = primary + secondary

    # Family-specific std for z-distance.
    rows_by_family = defaultdict(list)
    for r in null_rows:
        rows_by_family[r["null_family"]].append(r)

    family_stats = {}
    for nf, rows in rows_by_family.items():
        family_stats[nf] = {}
        for m in primary:
            vals = [as_float(r.get(m, 0.0)) for r in rows]
            family_stats[nf][m] = summarize(vals)

    thresholds = cfg["near_real_thresholds"]
    component_required = as_float(thresholds["require_carrier_face_component_count"])
    component_penalty = as_float(cfg["scoring"]["component_mismatch_penalty"])
    zero_std_scale = as_float(cfg["scoring"]["zero_std_scale"])

    distance_rows: List[Dict[str, Any]] = []
    near_rows: List[Dict[str, Any]] = []

    for r in null_rows:
        nf = r["null_family"]

        abs_parts = {}
        z_parts = {}
        abs_distance = 0.0
        z_sq_sum = 0.0

        for m in primary:
            x = as_float(r.get(m, 0.0))
            rv = as_float(real.get(m, 0.0))
            diff = abs(x - rv)
            abs_parts[m] = diff
            abs_distance += diff

            std = family_stats[nf][m]["std"]
            scale = std if std > 0 else zero_std_scale
            z = (x - rv) / scale
            z_parts[m] = z
            z_sq_sum += z * z

        z_distance = math.sqrt(z_sq_sum)

        role_balance_deviation = (
            abs(as_float(r["carrier_face_count"]) - as_float(real["carrier_face_count"]))
            + abs(as_float(r["carrier_pentagon_face_count"]) - as_float(real["carrier_pentagon_face_count"]))
            + abs(as_float(r["mixed_seam_boundary_face_count"]) - as_float(real["mixed_seam_boundary_face_count"]))
            + abs(as_float(r["largest_mixed_face_component_count"]) - as_float(real["largest_mixed_face_component_count"]))
            + component_penalty * (1 if as_float(r["carrier_face_component_count"]) != component_required else 0)
        )

        near_real = (
            abs(as_float(r["carrier_face_count"]) - as_float(real["carrier_face_count"])) <= as_float(thresholds["carrier_face_count_abs"])
            and abs(as_float(r["carrier_pentagon_face_count"]) - as_float(real["carrier_pentagon_face_count"])) <= as_float(thresholds["carrier_pentagon_face_count_abs"])
            and abs(as_float(r["mixed_seam_boundary_face_count"]) - as_float(real["mixed_seam_boundary_face_count"])) <= as_float(thresholds["mixed_seam_boundary_face_count_abs"])
            and as_float(r["carrier_face_component_count"]) == component_required
        )

        strict_near_real = (
            as_float(r["carrier_face_count"]) == as_float(real["carrier_face_count"])
            and as_float(r["carrier_pentagon_face_count"]) == as_float(real["carrier_pentagon_face_count"])
            and as_float(r["mixed_seam_boundary_face_count"]) == as_float(real["mixed_seam_boundary_face_count"])
            and as_float(r["carrier_face_component_count"]) == component_required
        )

        out = {
            "null_family": nf,
            "replicate_index": r["replicate_index"],
            "D_abs_primary": abs_distance,
            "D_z_primary": z_distance,
            "role_balance_deviation": role_balance_deviation,
            "near_real_profile": int(near_real),
            "strict_near_real_profile": int(strict_near_real),
        }
        for m in all_metrics:
            out[m] = r.get(m, "")
            out[f"{m}_real"] = real.get(m, "")
        for m in primary:
            out[f"{m}_abs_diff"] = abs_parts[m]
            out[f"{m}_z_diff"] = z_parts[m]
        distance_rows.append(out)

        if near_real or strict_near_real:
            near_rows.append(out.copy())

    # Summary by family
    summary_rows: List[Dict[str, Any]] = []
    for nf, rows in defaultdict(list, {k: [r for r in distance_rows if r["null_family"] == k] for k in rows_by_family}).items():
        n = len(rows)
        if n == 0:
            continue
        near_count = sum(int(r["near_real_profile"]) for r in rows)
        strict_count = sum(int(r["strict_near_real_profile"]) for r in rows)
        d_abs = summarize([as_float(r["D_abs_primary"]) for r in rows])
        d_z = summarize([as_float(r["D_z_primary"]) for r in rows])
        rb = summarize([as_float(r["role_balance_deviation"]) for r in rows])
        min_dist = d_abs["min"]

        summary = {
            "null_family": nf,
            "replicate_count": n,
            "near_real_count": near_count,
            "near_real_fraction": near_count / n,
            "strict_near_real_count": strict_count,
            "strict_near_real_fraction": strict_count / n,
            "D_abs_min": d_abs["min"],
            "D_abs_mean": d_abs["mean"],
            "D_abs_median": d_abs["median"],
            "D_abs_max": d_abs["max"],
            "D_z_min": d_z["min"],
            "D_z_mean": d_z["mean"],
            "D_z_median": d_z["median"],
            "D_z_max": d_z["max"],
            "role_balance_deviation_min": rb["min"],
            "role_balance_deviation_mean": rb["mean"],
            "role_balance_deviation_median": rb["median"],
            "role_balance_deviation_max": rb["max"],
            "interpretation_label": interpretation(near_count / n, strict_count / n, min_dist),
        }

        # Include metric means for quick diagnosis.
        for m in primary:
            vals = [as_float(r[m]) for r in rows]
            s = summarize(vals)
            summary[f"{m}_real"] = real.get(m, "")
            summary[f"{m}_null_mean"] = s["mean"]
            summary[f"{m}_null_min"] = s["min"]
            summary[f"{m}_null_max"] = s["max"]

        summary_rows.append(summary)

    # Sort rows for readability.
    distance_rows.sort(key=lambda r: (r["null_family"], as_float(r["role_balance_deviation"]), as_float(r["D_abs_primary"]), int(float(r["replicate_index"]))))
    near_rows.sort(key=lambda r: (r["null_family"], as_float(r["role_balance_deviation"]), as_float(r["D_abs_primary"]), int(float(r["replicate_index"]))))
    summary_rows.sort(key=lambda r: r["null_family"])

    out = cfg["outputs"]

    base_fields = [
        "null_family", "replicate_index", "D_abs_primary", "D_z_primary",
        "role_balance_deviation", "near_real_profile", "strict_near_real_profile",
    ]
    metric_fields = []
    for m in all_metrics:
        metric_fields.extend([m, f"{m}_real"])
    diff_fields = []
    for m in primary:
        diff_fields.extend([f"{m}_abs_diff", f"{m}_z_diff"])

    distance_fields = base_fields + metric_fields + diff_fields
    write_csv(outdir / out["profile_distance_by_replicate_csv"], distance_rows, distance_fields)
    write_csv(outdir / out["near_real_replicates_csv"], near_rows, distance_fields)

    summary_fields = [
        "null_family", "replicate_count", "near_real_count", "near_real_fraction",
        "strict_near_real_count", "strict_near_real_fraction",
        "D_abs_min", "D_abs_mean", "D_abs_median", "D_abs_max",
        "D_z_min", "D_z_mean", "D_z_median", "D_z_max",
        "role_balance_deviation_min", "role_balance_deviation_mean",
        "role_balance_deviation_median", "role_balance_deviation_max",
        "interpretation_label",
    ]
    for m in primary:
        summary_fields.extend([f"{m}_real", f"{m}_null_mean", f"{m}_null_min", f"{m}_null_max"])
    write_csv(outdir / out["profile_summary_by_family_csv"], summary_rows, summary_fields)

    real_profile = {
        "primary_metrics": {m: real.get(m, None) for m in primary},
        "secondary_metrics": {m: real.get(m, None) for m in secondary},
        "near_real_thresholds": thresholds,
        "component_mismatch_penalty": component_penalty,
        "interpretation_note": "Profile comparison is diagnostic; empirical fractions are not formal physical p-values.",
    }
    with (outdir / out["real_profile_json"]).open("w", encoding="utf-8") as f:
        json.dump(real_profile, f, indent=2, sort_keys=True)

    label_counts = Counter(r["interpretation_label"] for r in summary_rows)
    manifest = {
        "run_id": cfg["run"]["run_id"],
        "output_dir": cfg["run"]["output_dir"],
        "fu02e_run_id": fu02e_manifest.get("run_id", ""),
        "fu02e_warning_count": len(fu02e_warnings),
        "primary_metrics": primary,
        "secondary_metrics": secondary,
        "null_family_count": len(rows_by_family),
        "null_replicate_count": len(null_rows),
        "near_real_total_count": sum(int(r["near_real_profile"]) for r in distance_rows),
        "strict_near_real_total_count": sum(int(r["strict_near_real_profile"]) for r in distance_rows),
        "summary_label_counts": dict(sorted(label_counts.items())),
        "summary_by_family": summary_rows,
        "row_counts": {
            "profile_distance_by_replicate": len(distance_rows),
            "profile_summary_by_family": len(summary_rows),
            "near_real_replicates": len(near_rows),
            "warnings": len(warnings),
        },
        "scope_note": "FU02e1 evaluates joint compactness/role-balance profiles for FU02e null replicates; diagnostic only.",
    }

    with (outdir / out["run_manifest_json"]).open("w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2, sort_keys=True)
    with (outdir / out["warnings_json"]).open("w", encoding="utf-8") as f:
        json.dump(warnings, f, indent=2, sort_keys=True)
    with (outdir / out["resolved_config_yaml"]).open("w", encoding="utf-8") as f:
        yaml.safe_dump(cfg, f, sort_keys=False)

    print(json.dumps(manifest, indent=2, sort_keys=True))
    if warnings:
        print("\\nWarnings:")
        for w in warnings:
            print(f'{w["severity"]}: {w["message"]}')


def main() -> None:
    parser = argparse.ArgumentParser(description="Run BMS-FU02e1 role-balance localization specificity extension.")
    parser.add_argument("--config", required=True)
    args = parser.parse_args()
    run(Path(args.config))


if __name__ == "__main__":
    main()
