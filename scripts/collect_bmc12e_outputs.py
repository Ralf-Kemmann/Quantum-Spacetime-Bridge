#!/usr/bin/env python3
"""
Collect existing BMC-12e legacy runner outputs.

This script does not re-run the BMC07/BMC09d backbone runner.
It only collects existing backbone_variant_summary.csv files from the
known legacy output location and writes final BMC-12e summary files.

Expected real runner output location observed in the project:

data/bmc12e_edgecount_sweep_configs/runs/BMC-12e/edgecount_neighborhood_sweep_open/runner_outputs/N_<N>/<case_id>/backbone_variant_summary.csv
"""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from typing import Any, Dict, List, Sequence


def read_csv(path: Path) -> List[Dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as f:
        rows = list(csv.DictReader(f))
    if not rows:
        raise ValueError(f"CSV has no rows: {path}")
    return [dict(r) for r in rows]


def write_csv(path: Path, rows: Sequence[Dict[str, Any]], fieldnames: Sequence[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def compare_case(
    *,
    edge_count: int,
    case_id: str,
    dropped_feature: str,
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
        "edge_count_target": edge_count,
        "case_id": case_id,
        "dropped_feature": dropped_feature,
        "variant_count": total,
        "retained_variant_count": retained,
        "retained_fraction": retained / total if total else 0.0,
        "failed_variant_count": failed,
        "all_variants_retained": str(total > 0 and retained == total).lower(),
        "any_failure": str(failed > 0).lower(),
        "bmc12e_decision_status": status,
    }


def write_readout(path: Path, *, decision_rows: Sequence[Dict[str, Any]], edge_counts: Sequence[int]) -> None:
    lines: List[str] = []
    lines.append("# BMC-12e Edge-Count Neighborhood Sweep Readout")
    lines.append("")
    lines.append("## Run")
    lines.append("")
    lines.append("- collection mode: existing legacy runner outputs")
    lines.append(f"- edge_counts: `{', '.join(str(x) for x in edge_counts)}`")
    lines.append("")
    lines.append("## Befund")
    lines.append("")
    lines.append("BMC-12e collected backbone decision summaries across neighboring matched edge counts.")
    lines.append("")
    lines.append("| N | case_id | dropped_feature | retained_variants | retained_fraction | status |")
    lines.append("|---:|---|---:|---:|---:|---|")

    for row in decision_rows:
        lines.append(
            "| {N} | {case} | {drop} | {retained}/{total} | {frac:.3f} | {status} |".format(
                N=row["edge_count_target"],
                case=row["case_id"],
                drop=row["dropped_feature"] or "-",
                retained=row["retained_variant_count"],
                total=row["variant_count"],
                frac=float(row["retained_fraction"]),
                status=row["bmc12e_decision_status"],
            )
        )

    lines.append("")
    lines.append("## Interpretation")
    lines.append("")
    lines.append(
        "If the N=81 pattern persists across neighboring N values, the BMC-12c result is less likely to be a single graph-size artifact. "
        "If the pattern changes strongly, BMC-12c should be treated as a local decision-point result."
    )
    lines.append("")
    lines.append("## Hypothesis")
    lines.append("")
    lines.append(
        "A stable neighborhood profile would support structured joint-feature-basis sensitivity. "
        "A fragmented profile would support graph-size sensitivity."
    )
    lines.append("")
    lines.append("## Offene Lücke")
    lines.append("")
    lines.append(
        "This sweep does not vary the decision thresholds. A later BMC-12f decision-threshold / dominance-gap sweep remains necessary."
    )
    lines.append("")

    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    ap = argparse.ArgumentParser(description="Collect existing BMC-12e runner outputs.")
    ap.add_argument(
        "--project-root",
        default=".",
        help="Project root. Default: current working directory.",
    )
    ap.add_argument(
        "--runner-output-root",
        default="data/bmc12e_edgecount_sweep_configs/runs/BMC-12e/edgecount_neighborhood_sweep_open/runner_outputs",
        help="Observed legacy runner output root.",
    )
    ap.add_argument(
        "--final-output-root",
        default="runs/BMC-12e/edgecount_neighborhood_sweep_open",
        help="Final BMC-12e summary output root.",
    )
    args = ap.parse_args()

    root = Path(args.project_root).resolve()
    runner_root = (root / args.runner_output_root).resolve()
    final_root = (root / args.final_output_root).resolve()
    final_root.mkdir(parents=True, exist_ok=True)

    if not runner_root.exists():
        raise SystemExit(f"Runner output root not found: {runner_root}")

    edge_counts = [70, 75, 81, 87, 92]
    case_defs = [
        ("baseline_all_features", ""),
        ("drop_feature_mode_frequency", "feature_mode_frequency"),
        ("drop_feature_length_scale", "feature_length_scale"),
        ("drop_feature_shape_factor", "feature_shape_factor"),
        ("drop_feature_spectral_index", "feature_spectral_index"),
    ]

    reference_label = "backbone_localization_supported"
    reference_arm = "backbone_only"

    decision_rows: List[Dict[str, Any]] = []
    variant_rows_all: List[Dict[str, Any]] = []
    missing: List[str] = []

    for edge_count in edge_counts:
        for case_id, dropped_feature in case_defs:
            summary_path = (
                runner_root
                / f"N_{edge_count}"
                / case_id
                / "backbone_variant_summary.csv"
            )

            if not summary_path.exists():
                missing.append(str(summary_path))
                continue

            variant_rows = read_csv(summary_path)

            for row in variant_rows:
                out = dict(row)
                out["edge_count_target"] = edge_count
                out["case_id"] = case_id
                out["dropped_feature"] = dropped_feature
                variant_rows_all.append(out)

            decision_rows.append(
                compare_case(
                    edge_count=edge_count,
                    case_id=case_id,
                    dropped_feature=dropped_feature,
                    rows=variant_rows,
                    reference_label=reference_label,
                    reference_arm=reference_arm,
                )
            )

    if missing:
        raise SystemExit(
            "Missing expected BMC-12e runner summaries:\n" + "\n".join(missing)
        )

    decision_fields = [
        "edge_count_target",
        "case_id",
        "dropped_feature",
        "variant_count",
        "retained_variant_count",
        "retained_fraction",
        "failed_variant_count",
        "all_variants_retained",
        "any_failure",
        "bmc12e_decision_status",
    ]

    variant_fields = [
        "edge_count_target",
        "case_id",
        "dropped_feature",
        "variant_name",
        "method",
        "variant_parameters",
        "backbone_node_count",
        "off_backbone_node_count",
        "coupling_edge_count",
        "decision_label",
        "dominant_arm",
        "full_graph_arrangement_signal",
        "backbone_only_arrangement_signal",
        "off_backbone_only_arrangement_signal",
        "coupling_only_arrangement_signal",
    ]

    decision_summary = final_root / "bmc12e_edgecount_sweep_decision_summary.csv"
    variant_summary = final_root / "bmc12e_edgecount_sweep_variant_summary.csv"
    readout = final_root / "bmc12e_edgecount_sweep_readout.md"
    metrics = final_root / "bmc12e_metrics.json"

    write_csv(decision_summary, decision_rows, decision_fields)
    write_csv(variant_summary, variant_rows_all, variant_fields)
    write_readout(readout, decision_rows=decision_rows, edge_counts=edge_counts)

    metrics.write_text(
        json.dumps(
            {
                "collection_mode": "existing_runner_outputs",
                "runner_output_root": str(runner_root),
                "final_output_root": str(final_root),
                "edge_counts": edge_counts,
                "case_count": len(case_defs),
                "variant_rows": len(variant_rows_all),
                "decision_rows": len(decision_rows),
                "reference_decision": {
                    "decision_label": reference_label,
                    "dominant_arm": reference_arm,
                },
            },
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    print("BMC-12e collection completed.")
    print(f"Wrote: {decision_summary}")
    print(f"Wrote: {variant_summary}")
    print(f"Wrote: {readout}")
    print(f"Wrote: {metrics}")


if __name__ == "__main__":
    main()
