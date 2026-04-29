#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
import math
from pathlib import Path
from typing import Any, Dict, List, Sequence, Tuple

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


def project_path(root: Path, value: str) -> Path:
    p = Path(value)
    return p if p.is_absolute() else root / p


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


def as_float(value: Any, field: str) -> float:
    if value is None or value == "":
        return 0.0
    x = float(value)
    if not math.isfinite(x):
        raise ValueError(f"Non-finite float in {field}: {value!r}")
    return x


def threshold_pairs(cfg: Dict[str, Any]) -> List[Tuple[float, float]]:
    grid = cfg["threshold_grid"]
    arrangements = [float(x) for x in grid["arrangement_signal_min"]]
    gaps = [float(x) for x in grid["dominance_gap_min"]]
    return [(a, g) for a in arrangements for g in gaps]


def classify_variant(row: Dict[str, str], cfg: Dict[str, Any], arrangement_min: float, gap_min: float) -> Dict[str, Any]:
    sig = cfg["signals"]
    s_full = as_float(row.get(sig["full_graph"], ""), sig["full_graph"])
    s_backbone = as_float(row.get(sig["backbone_only"], ""), sig["backbone_only"])
    s_off = as_float(row.get(sig["off_backbone_only"], ""), sig["off_backbone_only"])
    s_coupling = as_float(row.get(sig["coupling_only"], ""), sig["coupling_only"])

    best_competing = max(s_full, s_off, s_coupling)
    backbone_gap = s_backbone - best_competing
    retained = (s_backbone >= arrangement_min) and (backbone_gap >= gap_min)

    out = dict(row)
    out.update({
        "edge_count_target": int(float(row["edge_count_target"])),
        "arrangement_signal_min": arrangement_min,
        "dominance_gap_min": gap_min,
        "best_competing_signal": best_competing,
        "backbone_gap": backbone_gap,
        "retained_under_thresholds": str(retained).lower(),
        "reclassified_status": "retained" if retained else "not_retained",
    })
    return out


def summarize_case(rows: Sequence[Dict[str, Any]], edge_count: int, arrangement_min: float, gap_min: float, case_id: str, dropped_feature: str) -> Dict[str, Any]:
    total = len(rows)
    retained = sum(1 for r in rows if r["retained_under_thresholds"] == "true")
    failed = total - retained

    if total > 0 and retained == total:
        status = "decision_retained"
    elif retained > 0:
        status = "decision_partially_retained"
    else:
        status = "decision_not_retained"

    return {
        "edge_count_target": edge_count,
        "arrangement_signal_min": arrangement_min,
        "dominance_gap_min": gap_min,
        "case_id": case_id,
        "dropped_feature": dropped_feature,
        "variant_count": total,
        "retained_variant_count": retained,
        "retained_fraction": retained / total if total else 0.0,
        "failed_variant_count": failed,
        "all_variants_retained": str(total > 0 and retained == total).lower(),
        "any_failure": str(failed > 0).lower(),
        "bmc12f_decision_status": status,
    }


def summarize_stability(decision_rows: Sequence[Dict[str, Any]]) -> List[Dict[str, Any]]:
    grouped: Dict[Tuple[int, str, str], List[Dict[str, Any]]] = {}
    for row in decision_rows:
        key = (int(row["edge_count_target"]), str(row["case_id"]), str(row["dropped_feature"]))
        grouped.setdefault(key, []).append(row)

    out: List[Dict[str, Any]] = []
    for (edge_count, case_id, dropped_feature), rows in sorted(grouped.items()):
        fractions = [float(r["retained_fraction"]) for r in rows]
        full = sum(1 for r in rows if r["bmc12f_decision_status"] == "decision_retained")
        partial = sum(1 for r in rows if r["bmc12f_decision_status"] == "decision_partially_retained")
        none = sum(1 for r in rows if r["bmc12f_decision_status"] == "decision_not_retained")
        count = len(rows)

        if full == count:
            label = "stable_full"
        elif none == count:
            label = "unstable_none"
        else:
            label = "mixed_sensitive"

        out.append({
            "edge_count_target": edge_count,
            "case_id": case_id,
            "dropped_feature": dropped_feature,
            "threshold_pair_count": count,
            "full_retention_count": full,
            "partial_retention_count": partial,
            "no_retention_count": none,
            "mean_retained_fraction": sum(fractions) / count if count else 0.0,
            "min_retained_fraction": min(fractions) if fractions else 0.0,
            "max_retained_fraction": max(fractions) if fractions else 0.0,
            "stability_label": label,
        })
    return out


def write_readout(path: Path, edge_counts: Sequence[int], threshold_pair_count: int, stability_rows: Sequence[Dict[str, Any]]) -> None:
    lines: List[str] = []
    lines.append("# BMC-12f Decision-Threshold / Dominance-Gap Sweep Readout")
    lines.append("")
    lines.append("## Run")
    lines.append("")
    lines.append(f"- edge_counts: `{', '.join(str(x) for x in edge_counts)}`")
    lines.append(f"- threshold_pair_count: `{threshold_pair_count}`")
    lines.append("- mode: reclassification of existing BMC-12e variant signals")
    lines.append("")
    lines.append("## Befund")
    lines.append("")
    lines.append("| N | case_id | dropped_feature | full | partial | none | mean_retained_fraction | stability |")
    lines.append("|---:|---|---:|---:|---:|---:|---:|---|")
    for row in stability_rows:
        lines.append(
            "| {N} | {case} | {drop} | {full} | {partial} | {none} | {mean:.3f} | {label} |".format(
                N=row["edge_count_target"],
                case=row["case_id"],
                drop=row["dropped_feature"] or "-",
                full=row["full_retention_count"],
                partial=row["partial_retention_count"],
                none=row["no_retention_count"],
                mean=float(row["mean_retained_fraction"]),
                label=row["stability_label"],
            )
        )
    lines.append("")
    lines.append("## Interpretation")
    lines.append("")
    lines.append("Stable full retention of the all-feature baseline across the threshold grid supports decision-threshold robustness within the tested sparse/local regime. Mixed or unstable labels indicate threshold sensitivity.")
    lines.append("")
    lines.append("## Hypothesis")
    lines.append("")
    lines.append("If the all-feature baseline remains stable for N=70,75,81, the BMC09d sparse/local backbone regime is less likely to be a single hard-threshold artifact.")
    lines.append("")
    lines.append("## Open gap")
    lines.append("")
    lines.append("BMC-12f still uses the same top-k/top-alpha backbone definitions. Method-dependence remains open for BMC-13.")
    lines.append("")
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Run BMC-12f decision threshold / gap sweep.")
    parser.add_argument("--config", required=True)
    args = parser.parse_args()

    root = Path.cwd()
    cfg = load_yaml(project_path(root, args.config))

    input_path = project_path(root, cfg["inputs"]["variant_summary_csv"])
    output_root = project_path(root, cfg["outputs"]["output_root"])
    output_root.mkdir(parents=True, exist_ok=True)

    raw_rows = read_csv(input_path)
    edge_counts = [int(x) for x in cfg["edge_counts"]]
    case_order = [str(x) for x in cfg["case_order"]]
    pairs = threshold_pairs(cfg)

    variant_rows: List[Dict[str, Any]] = []
    decision_rows: List[Dict[str, Any]] = []

    for arrangement_min, gap_min in pairs:
        for edge_count in edge_counts:
            for case_id in case_order:
                selected = [
                    r for r in raw_rows
                    if int(float(r["edge_count_target"])) == edge_count
                    and str(r["case_id"]) == case_id
                ]
                if not selected:
                    raise ValueError(f"No BMC-12e variant rows found for N={edge_count}, case={case_id}")

                classified = [classify_variant(r, cfg, arrangement_min, gap_min) for r in selected]
                variant_rows.extend(classified)

                dropped_feature = classified[0].get("dropped_feature", "")
                decision_rows.append(summarize_case(classified, edge_count, arrangement_min, gap_min, case_id, dropped_feature))

    stability_rows = summarize_stability(decision_rows)

    variant_fields = [
        "edge_count_target", "arrangement_signal_min", "dominance_gap_min",
        "case_id", "dropped_feature", "variant_name", "method", "variant_parameters",
        "full_graph_arrangement_signal", "backbone_only_arrangement_signal",
        "off_backbone_only_arrangement_signal", "coupling_only_arrangement_signal",
        "best_competing_signal", "backbone_gap",
        "retained_under_thresholds", "reclassified_status",
    ]
    decision_fields = [
        "edge_count_target", "arrangement_signal_min", "dominance_gap_min",
        "case_id", "dropped_feature", "variant_count",
        "retained_variant_count", "retained_fraction", "failed_variant_count",
        "all_variants_retained", "any_failure", "bmc12f_decision_status",
    ]
    stability_fields = [
        "edge_count_target", "case_id", "dropped_feature",
        "threshold_pair_count", "full_retention_count",
        "partial_retention_count", "no_retention_count",
        "mean_retained_fraction", "min_retained_fraction",
        "max_retained_fraction", "stability_label",
    ]

    variant_out = output_root / "bmc12f_threshold_gap_variant_summary.csv"
    decision_out = output_root / "bmc12f_threshold_gap_decision_summary.csv"
    stability_out = output_root / "bmc12f_threshold_gap_stability_summary.csv"
    readout_out = output_root / "bmc12f_threshold_gap_readout.md"
    metrics_out = output_root / "bmc12f_metrics.json"

    write_csv(variant_out, variant_rows, variant_fields)
    write_csv(decision_out, decision_rows, decision_fields)
    write_csv(stability_out, stability_rows, stability_fields)
    write_readout(readout_out, edge_counts, len(pairs), stability_rows)

    metrics = {
        "run_id": cfg.get("run_id", "BMC12f_decision_threshold_gap_sweep_open"),
        "input_variant_summary_csv": str(input_path),
        "output_root": str(output_root),
        "edge_counts": edge_counts,
        "threshold_pairs": [{"arrangement_signal_min": a, "dominance_gap_min": g} for a, g in pairs],
        "variant_rows": len(variant_rows),
        "decision_rows": len(decision_rows),
        "stability_rows": len(stability_rows),
        "classification_rule": "S_backbone >= arrangement_signal_min and S_backbone - max(S_full,S_off,S_coupling) >= dominance_gap_min",
    }
    metrics_out.write_text(json.dumps(metrics, indent=2, ensure_ascii=False), encoding="utf-8")

    print("BMC-12f decision-threshold / dominance-gap sweep completed.")
    print(f"Wrote: {variant_out}")
    print(f"Wrote: {decision_out}")
    print(f"Wrote: {stability_out}")
    print(f"Wrote: {readout_out}")
    print(f"Wrote: {metrics_out}")


if __name__ == "__main__":
    main()
