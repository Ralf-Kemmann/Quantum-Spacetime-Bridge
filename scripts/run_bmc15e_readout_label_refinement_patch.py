#!/usr/bin/env python3
"""
run_bmc15e_readout_label_refinement_patch.py

BMC-15e readout-label refinement patch.

Purpose:
- Treat embedding_stress_2d/3d/4d as directional metrics:
    lower_is_more_geometry_like
- Read existing observed_position_summary.csv
- Write observed_position_summary_refined.csv
- Write readout_refined.md
- Write bmc15e_refinement_patch_metrics.json

No geometry controls are regenerated.
No graph metrics are recomputed.
Original files are preserved.
"""

from __future__ import annotations

import argparse
import json
import math
from datetime import datetime
from pathlib import Path
from typing import Any, Dict

import pandas as pd


EMBEDDING_STRESS_METRICS = {
    "embedding_stress_2d",
    "embedding_stress_3d",
    "embedding_stress_4d",
}


def now_iso() -> str:
    return datetime.now().isoformat(timespec="seconds")


def is_finite(x: Any) -> bool:
    try:
        return math.isfinite(float(x))
    except Exception:
        return False


def f(x: Any) -> float:
    return float(x)


def classify_lower_is_more(
    observed_value: Any,
    control_min: Any,
    control_max: Any,
    tie_tolerance: float,
    all_zero_label: str,
) -> str:
    if not (is_finite(observed_value) and is_finite(control_min) and is_finite(control_max)):
        return "not_directional"

    ov = f(observed_value)
    cmin = f(control_min)
    cmax = f(control_max)

    if abs(ov) <= tie_tolerance and abs(cmin) <= tie_tolerance and abs(cmax) <= tie_tolerance:
        return all_zero_label

    if cmin - tie_tolerance <= ov <= cmax + tie_tolerance:
        return "observed_within_geometry_control_range"

    if ov < cmin - tie_tolerance:
        return "observed_more_geometry_like_than_geometry_controls"

    if ov > cmax + tie_tolerance:
        return "observed_less_geometry_like_than_geometry_controls"

    return "observed_outside_geometry_control_range"


def main() -> int:
    parser = argparse.ArgumentParser(description="Refine BMC-15e observed-position labels for embedding stress.")
    parser.add_argument(
        "--run-dir",
        default="runs/BMC-15e/geometry_control_nulls_open",
        help="BMC-15e output directory.",
    )
    parser.add_argument(
        "--tie-tolerance",
        type=float,
        default=1.0e-12,
        help="Tie tolerance for label refinement.",
    )
    parser.add_argument(
        "--all-zero-label",
        default="observed_geometry_control_equivalent",
        help="Label for all-zero observed/control tie cases.",
    )
    args = parser.parse_args()

    run_dir = Path(args.run_dir).expanduser().resolve()
    src_path = run_dir / "observed_position_summary.csv"
    refined_path = run_dir / "observed_position_summary_refined.csv"
    readout_path = run_dir / "readout_refined.md"
    metrics_path = run_dir / "bmc15e_refinement_patch_metrics.json"

    if not src_path.exists():
        raise SystemExit(f"Input file not found: {src_path}")

    df = pd.read_csv(src_path)
    required = {"metric", "observed_value", "control_min", "control_max", "position_label"}
    missing = sorted(required - set(df.columns))
    if missing:
        raise SystemExit(f"Missing required columns in {src_path}: {missing}")

    original_counts = df["position_label"].value_counts().to_dict()

    refined_labels = []
    actions = []

    for _, row in df.iterrows():
        metric = str(row["metric"])
        old_label = str(row["position_label"])

        if metric in EMBEDDING_STRESS_METRICS:
            new_label = classify_lower_is_more(
                row["observed_value"],
                row["control_min"],
                row["control_max"],
                tie_tolerance=args.tie_tolerance,
                all_zero_label=args.all_zero_label,
            )
            action = "embedding_stress_reclassified_lower_is_more"
        else:
            new_label = old_label
            action = "preserved_original_label"

        refined_labels.append(new_label)
        actions.append(action)

    out = df.copy()
    out["position_label_original"] = out["position_label"]
    out["position_label_refined"] = refined_labels
    out["refinement_action"] = actions
    out["position_label"] = out["position_label_refined"]

    refined_counts = out["position_label"].value_counts().to_dict()

    changed = out[out["position_label_original"] != out["position_label_refined"]].copy()

    # Summaries
    changed_by_metric = (
        changed.groupby(["metric", "position_label_original", "position_label_refined"])
        .size()
        .reset_index(name="count")
        .to_dict(orient="records")
        if not changed.empty
        else []
    )

    refined_by_metric = (
        out.groupby(["metric", "position_label"])
        .size()
        .reset_index(name="count")
        .to_dict(orient="records")
    )

    refined_by_object = (
        out.groupby(["observed_object", "position_label"])
        .size()
        .reset_index(name="count")
        .to_dict(orient="records")
        if "observed_object" in out.columns
        else []
    )

    refined_by_family = (
        out.groupby(["control_family", "position_label"])
        .size()
        .reset_index(name="count")
        .to_dict(orient="records")
        if "control_family" in out.columns
        else []
    )

    out.to_csv(refined_path, index=False)

    patch_metrics: Dict[str, Any] = {
        "patch_id": "BMC-15e_readout_label_refinement_patch",
        "generated_at": now_iso(),
        "run_dir": str(run_dir),
        "input_file": str(src_path),
        "output_file": str(refined_path),
        "tie_tolerance": args.tie_tolerance,
        "all_zero_label": args.all_zero_label,
        "refinement_scope": sorted(EMBEDDING_STRESS_METRICS),
        "rows_total": int(len(out)),
        "rows_changed": int(len(changed)),
        "original_position_label_counts": {str(k): int(v) for k, v in original_counts.items()},
        "refined_position_label_counts": {str(k): int(v) for k, v in refined_counts.items()},
        "changed_by_metric": changed_by_metric,
        "refined_by_metric": refined_by_metric,
        "refined_by_object": refined_by_object,
        "refined_by_family": refined_by_family,
        "methodological_boundary": (
            "Readout-label refinement only. No controls, graph metrics, distance matrices, "
            "or MDS/stress values were recomputed."
        ),
    }

    metrics_path.write_text(json.dumps(patch_metrics, indent=2, ensure_ascii=False), encoding="utf-8")

    lines = []
    lines.append("# BMC-15e Readout Label Refinement Patch — Readout\n")
    lines.append(f"- Generated: `{patch_metrics['generated_at']}`")
    lines.append(f"- Run directory: `{run_dir}`")
    lines.append(f"- Input: `{src_path.name}`")
    lines.append(f"- Output: `{refined_path.name}`")
    lines.append("")
    lines.append("## Scope\n")
    lines.append("This patch refines observed-position labels for embedding-stress metrics.")
    lines.append("It does not regenerate geometry controls and does not recompute graph metrics.")
    lines.append("")
    lines.append("## Refinement rule\n")
    lines.append("The following metrics are treated as directional lower-is-more-geometry-like diagnostics:")
    lines.append("")
    for m in sorted(EMBEDDING_STRESS_METRICS):
        lines.append(f"- `{m}`")
    lines.append("")
    lines.append("## Label count changes\n")
    lines.append("")
    lines.append("### Original label counts\n")
    lines.append("| Label | Count |")
    lines.append("|---|---:|")
    for k, v in sorted(original_counts.items(), key=lambda kv: (-kv[1], kv[0])):
        lines.append(f"| `{k}` | {int(v)} |")
    lines.append("")
    lines.append("### Refined label counts\n")
    lines.append("| Label | Count |")
    lines.append("|---|---:|")
    for k, v in sorted(refined_counts.items(), key=lambda kv: (-kv[1], kv[0])):
        lines.append(f"| `{k}` | {int(v)} |")
    lines.append("")
    lines.append("## Changed rows\n")
    lines.append(f"- Rows changed: `{len(changed)}` of `{len(out)}`")
    lines.append("")
    if changed_by_metric:
        lines.append("| Metric | Original label | Refined label | Count |")
        lines.append("|---|---|---|---:|")
        for r in changed_by_metric:
            lines.append(
                f"| `{r['metric']}` | `{r['position_label_original']}` | "
                f"`{r['position_label_refined']}` | {int(r['count'])} |"
            )
    else:
        lines.append("No rows changed.")
    lines.append("")
    lines.append("## Conservative interpretation\n")
    lines.append("The patch corrects the readout logic by treating embedding stress as a directional")
    lines.append("embedding-compatibility proxy. It changes labels only; it does not change the BMC-15e")
    lines.append("control metrics or generated graph objects.")
    lines.append("")
    lines.append("## Claim boundary\n")
    lines.append("This remains a geometry-proxy readout refinement. It does not establish physical geometry,")
    lines.append("causal structure, Lorentzian signature, or spacetime emergence.")
    lines.append("")

    readout_path.write_text("\n".join(lines), encoding="utf-8")

    print("BMC-15e readout label refinement patch complete.")
    print(f"Input: {src_path}")
    print(f"Refined CSV: {refined_path}")
    print(f"Patch metrics: {metrics_path}")
    print(f"Refined readout: {readout_path}")
    print(f"Rows total: {len(out)}")
    print(f"Rows changed: {len(changed)}")
    print("Original counts:", original_counts)
    print("Refined counts:", refined_counts)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
