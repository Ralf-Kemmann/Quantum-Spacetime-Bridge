#!/usr/bin/env python3
"""
BMC-15f.2 connectedness-transition postprocessor.

Reads the standard BMC-15f runner outputs and writes transition-focused summaries.

Expected input:
  runs/BMC-15f2/connectedness_transition_sweep_open/

Outputs:
  connectedness_transition_summary.csv
  connectedness_transition_readout.md
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any

import pandas as pd


def extract_parameter(row: pd.Series) -> tuple[str, float | str]:
    """Extract sweep parameter from common variant naming or columns."""
    for col in ["k", "top_fraction", "mode", "variant_parameter", "parameter_value"]:
        if col in row.index and pd.notna(row[col]):
            val = row[col]
            if col == "k":
                return "k", float(val)
            if col == "top_fraction":
                return "top_fraction", float(val)
            return col, str(val)

    text = " ".join(str(row.get(c, "")) for c in row.index)
    m = re.search(r"k[_=:-]?(\d+)", text)
    if m:
        return "k", float(m.group(1))
    m = re.search(r"top[_-]?fraction[_=:-]?([0-9.]+)", text)
    if m:
        return "top_fraction", float(m.group(1))
    m = re.search(r"fraction[_=:-]?([0-9.]+)", text)
    if m:
        return "top_fraction", float(m.group(1))
    return "unknown", str(row.get("variant_id", row.get("variant_name", "")))


def is_connected_value(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    s = str(value).strip().lower()
    return s in {"true", "1", "yes", "y"}


def core_label(frac: float | None) -> str:
    if frac is None or pd.isna(frac):
        return "core_not_available"
    if abs(frac - 1.0) < 1e-12:
        return "full_core_retained"
    if frac >= 0.833333:
        return "near_full_core_retained"
    if frac >= 0.5:
        return "partial_core_retained"
    return "weak_core_retained"


def main() -> int:
    parser = argparse.ArgumentParser(description="Analyze BMC-15f.2 connectedness transitions.")
    parser.add_argument("--run-dir", default="runs/BMC-15f2/connectedness_transition_sweep_open")
    args = parser.parse_args()

    run_dir = Path(args.run_dir)
    variant_path = run_dir / "variant_metrics.csv"
    core_path = run_dir / "core_containment_summary.csv"
    summary_path = run_dir / "summary.json"

    if not variant_path.exists():
        raise SystemExit(f"Missing {variant_path}")

    variants = pd.read_csv(variant_path)

    core = pd.read_csv(core_path) if core_path.exists() else pd.DataFrame()
    merge_cols = [c for c in ["variant_id", "variant_name", "envelope_family"] if c in variants.columns and c in core.columns]
    if merge_cols:
        variants = variants.merge(
            core[[*merge_cols, "core_containment_fraction"]].drop_duplicates(),
            on=merge_cols,
            how="left",
        )
    elif "core_containment_fraction" not in variants.columns:
        variants["core_containment_fraction"] = pd.NA

    connected_col = None
    for col in ["is_connected", "connected", "graph_connected"]:
        if col in variants.columns:
            connected_col = col
            break
    if connected_col is None:
        raise SystemExit("No connectedness column found in variant_metrics.csv")

    rows = []
    for family, fam in variants.groupby("envelope_family", dropna=False):
        fam = fam.copy()
        params = fam.apply(extract_parameter, axis=1)
        fam["parameter_name"] = [p[0] for p in params]
        fam["parameter_value"] = [p[1] for p in params]
        fam["is_connected_bool"] = fam[connected_col].apply(is_connected_value)
        fam["core_label"] = fam["core_containment_fraction"].apply(
            lambda x: core_label(None if pd.isna(x) else float(x))
        )

        # Sort numeric params first.
        fam["_sort"] = fam["parameter_value"].apply(lambda x: float(x) if isinstance(x, (int, float)) else 1e9)
        fam = fam.sort_values("_sort")

        connected = fam[fam["is_connected_bool"]]
        if connected.empty:
            first_connected_value = ""
            transition_status = "never_connected_in_sweep"
        elif fam["is_connected_bool"].all():
            first_connected_value = connected.iloc[0]["parameter_value"]
            transition_status = "always_connected"
        else:
            first_connected_value = connected.iloc[0]["parameter_value"]
            transition_status = "transition_found"

        for _, r in fam.iterrows():
            if transition_status == "never_connected_in_sweep":
                transition_label = "never_connected_in_sweep"
            elif transition_status == "always_connected":
                transition_label = "always_connected"
            else:
                pv = r["parameter_value"]
                if float(pv) < float(first_connected_value):
                    transition_label = "pre_transition_disconnected"
                elif abs(float(pv) - float(first_connected_value)) < 1e-12:
                    transition_label = "first_connected"
                else:
                    transition_label = "post_transition_connected"

            rows.append({
                "envelope_family": family,
                "variant_id": r.get("variant_id", r.get("variant_name", "")),
                "parameter_name": r["parameter_name"],
                "parameter_value": r["parameter_value"],
                "n_nodes": r.get("n_nodes", ""),
                "n_edges": r.get("n_edges", ""),
                "is_connected": bool(r["is_connected_bool"]),
                "transition_status": transition_status,
                "transition_label": transition_label,
                "first_connected_parameter_value": first_connected_value,
                "core_containment_fraction": r.get("core_containment_fraction", pd.NA),
                "core_label": r["core_label"],
                "embedding_stress_2d": r.get("embedding_stress_2d", pd.NA),
                "embedding_stress_3d": r.get("embedding_stress_3d", pd.NA),
                "embedding_stress_4d": r.get("embedding_stress_4d", pd.NA),
                "negative_eigenvalue_burden": r.get("negative_eigenvalue_burden", pd.NA),
                "geodesic_consistency_error": r.get("geodesic_consistency_error", pd.NA),
            })

    out = pd.DataFrame(rows)
    out_path = run_dir / "connectedness_transition_summary.csv"
    out.to_csv(out_path, index=False)

    summary = {}
    if summary_path.exists():
        summary = json.loads(summary_path.read_text(encoding="utf-8"))

    lines = []
    lines.append("# BMC-15f.2 Connectedness-Transition Readout\n")
    lines.append(f"- Run directory: `{run_dir}`")
    if summary:
        lines.append(f"- Run ID: `{summary.get('run_id', '')}`")
        lines.append(f"- Input kind: `{summary.get('relational_input_kind', '')}`")
        lines.append(f"- Nodes: `{summary.get('n_nodes', '')}`")
        lines.append(f"- Warnings: `{summary.get('warnings', '')}`")
    lines.append("")
    lines.append("## Transition summary\n")
    lines.append("| Family | Status | First connected parameter | Connected variants | Total variants | Core min | Core median | Core max |")
    lines.append("|---|---|---:|---:|---:|---:|---:|---:|")

    for family, fam in out.groupby("envelope_family", dropna=False):
        status = fam["transition_status"].iloc[0]
        first = fam["first_connected_parameter_value"].iloc[0]
        connected_count = int(fam["is_connected"].sum())
        total = len(fam)
        core_vals = pd.to_numeric(fam["core_containment_fraction"], errors="coerce")
        lines.append(
            f"| `{family}` | `{status}` | {first} | {connected_count} | {total} | "
            f"{core_vals.min():.6g} | {core_vals.median():.6g} | {core_vals.max():.6g} |"
        )

    lines.append("")
    lines.append("## Interpretation boundary\n")
    lines.append("This readout maps connectedness transitions and core containment. It does not establish physical geometry or spacetime emergence.")
    lines.append("")
    lines.append("## Key check\n")
    lines.append("If a family reaches connectedness while retaining high core containment, the compact core is less likely to be merely a disconnected sparse-graph artifact.")
    lines.append("")

    readout_path = run_dir / "connectedness_transition_readout.md"
    readout_path.write_text("\n".join(lines), encoding="utf-8")

    print("BMC-15f.2 connectedness-transition postprocessing complete.")
    print(f"Summary CSV: {out_path}")
    print(f"Readout: {readout_path}")
    print(out.to_string(index=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
