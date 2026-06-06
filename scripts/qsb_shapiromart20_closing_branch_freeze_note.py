#!/usr/bin/env python3
"""Create the SHAPIROMART20 branch-freeze closing artifacts from existing run outputs only."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

DEFAULT_OUTPUT_DIR = Path(
    "runs/QSB-SHAPIROMART/SHAPIROMART20_WITHIN_CONTEXT_CONTINUOUS_GEOMETRY_CONFOUNDER_TEST"
)

ALLOWED_INPUTS = [
    "shapiromart20_summary.json",
    "shapiromart20_final_status.csv",
    "shapiromart20_circularity_assessment.csv",
    "shapiromart20_context_group_contingency.csv",
    "shapiromart20_cluster_structure_inventory.csv",
    "shapiromart20_continuous_geometry_associations.csv",
    "shapiromart20_within_context_matched_comparison.csv",
    "shapiromart20_blocked_permutation_results.csv",
    "shapiromart20_negative_control_sensitivity.csv",
    "shapiromart20_finer_observable_inventory.csv",
    "shapiromart20_conventional_explanation_matrix.csv",
]

CLOSING_FILES = [
    "shapiromart20_branch_freeze_decision_note.md",
    "shapiromart20_branch_freeze_summary.json",
    "shapiromart20_branch_freeze_decision.csv",
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Create SHAPIROMART20 branch-freeze closing artifacts from existing outputs only."
    )
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument(
        "--overwrite-closing-files",
        action="store_true",
        help="Replace only the three closing-note artifacts.",
    )
    return parser.parse_args()


def load_json(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def load_csv_rows(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def ensure_allowed_inputs(output_dir: Path) -> None:
    required = [
        output_dir / "shapiromart20_summary.json",
        output_dir / "shapiromart20_final_status.csv",
        output_dir / "shapiromart20_finer_observable_inventory.csv",
    ]
    missing = [path.name for path in required if not path.exists()]
    if missing:
        raise FileNotFoundError(f"Required SHAPIROMART20 inputs are missing: {missing}")
    for path in required:
        if path.name not in ALLOWED_INPUTS:
            raise ValueError(f"Input path is not in the allowed SHAPIROMART20 input set: {path.name}")


def count_readiness(path: Path) -> tuple[int, int, int]:
    ready = 0
    semantics_incomplete = 0
    summary_only = 0
    for row in load_csv_rows(path):
        status = (row.get("readiness_status") or "").strip().lower()
        if status == "available_but_semantics_incomplete":
            semantics_incomplete += 1
        elif status == "summary_only":
            summary_only += 1
        elif status == "available":
            ready += 1
    return ready, semantics_incomplete, summary_only


def build_summary(output_dir: Path, summary: dict, final_status_row: dict, ready_count: int, semantics_incomplete_count: int, summary_only_count: int) -> dict:
    return {
        "prior_final_status": summary.get("final_status", {}).get("final_status") or final_status_row.get("final_status"),
        "branch_status": "branch_frozen_pending_more_diagnostic_data",
        "current_data_sufficient_for_independent_signal_test": "no",
        "toa_mjd_circularity_status": summary.get("final_status", {}).get("toa_mjd_circularity_status") or final_status_row.get("toa_mjd_circularity_status"),
        "global_snr_flux_block_robust": "no",
        "context_specific_associations_remaining": "yes",
        "matched_analysis_supported": "no",
        "cluster_key_status": "proxy_only",
        "finer_observable_ready_count": ready_count,
        "finer_observable_semantics_incomplete_count": semantics_incomplete_count,
        "finer_observable_summary_only_count": summary_only_count,
        "further_same_data_analysis_recommended": "no",
        "branch_frozen": "yes",
        "reopening_requires_new_diagnostic_data": "yes",
        "timing_residual_analysis_performed": "no",
        "shapiro_delay_calculated": "no",
        "model_fit_performed": "no",
        "physical_interpretation_performed": "no",
        "qsb_claim_made": "no",
        "additional_gate_created": "no",
        "closing_status": "completed",
        "inputs_read": [
            "shapiromart20_summary.json",
            "shapiromart20_final_status.csv",
            "shapiromart20_finer_observable_inventory.csv",
        ],
        "output_dir": str(output_dir),
        "generated_from_existing_outputs_only": True,
    }


def build_decision_row(summary: dict) -> dict[str, str]:
    return {
        "prior_final_status": str(summary["prior_final_status"]),
        "branch_status": str(summary["branch_status"]),
        "current_data_sufficient_for_independent_signal_test": str(summary["current_data_sufficient_for_independent_signal_test"]),
        "toa_mjd_circularity_status": str(summary["toa_mjd_circularity_status"]),
        "global_snr_flux_block_robust": str(summary["global_snr_flux_block_robust"]),
        "context_specific_associations_remaining": str(summary["context_specific_associations_remaining"]),
        "matched_analysis_supported": str(summary["matched_analysis_supported"]),
        "cluster_key_status": str(summary["cluster_key_status"]),
        "finer_observable_ready_count": str(summary["finer_observable_ready_count"]),
        "finer_observable_semantics_incomplete_count": str(summary["finer_observable_semantics_incomplete_count"]),
        "finer_observable_summary_only_count": str(summary["finer_observable_summary_only_count"]),
        "further_same_data_analysis_recommended": str(summary["further_same_data_analysis_recommended"]),
        "branch_frozen": str(summary["branch_frozen"]),
        "reopening_requires_new_diagnostic_data": str(summary["reopening_requires_new_diagnostic_data"]),
        "timing_residual_analysis_performed": str(summary["timing_residual_analysis_performed"]),
        "shapiro_delay_calculated": str(summary["shapiro_delay_calculated"]),
        "model_fit_performed": str(summary["model_fit_performed"]),
        "physical_interpretation_performed": str(summary["physical_interpretation_performed"]),
        "qsb_claim_made": str(summary["qsb_claim_made"]),
        "additional_gate_created": str(summary["additional_gate_created"]),
        "closing_status": str(summary["closing_status"]),
    }


def write_markdown(output_dir: Path, summary: dict) -> None:
    note = """# SHAPIROMART20 Branch Freeze Decision Note

## 1. Purpose
This note records the reproducible branch freeze for the existing SHAPIROMART20 run outputs and consolidates the currently available status values without opening databases or computing new analyses.

## 2. Evidence Basis
The closing decision is based only on the existing local SHAPIROMART20 artifacts in this run directory:
- shapiromart20_summary.json
- shapiromart20_final_status.csv
- shapiromart20_finer_observable_inventory.csv

## 3. Consolidated Findings
- prior final status: {prior_final_status}
- branch status: {branch_status}
- TOA-MJD circularity status: {toa_mjd_circularity_status}
- current data sufficient for an independent signal test: {current_data_sufficient_for_independent_signal_test}
- cluster key status: {cluster_key_status}
- finer observable readiness count: {finer_observable_ready_count}
- finer observable semantics-incomplete count: {finer_observable_semantics_incomplete_count}
- finer observable summary-only count: {finer_observable_summary_only_count}

## 4. Why the Branch Is Frozen
With the currently available data, no independent signal test is supported. Residual descriptive associations remain, but the available observation, cluster, and signal structure are not yet sufficient for a controlled follow-up analysis. The branch is therefore frozen pending more diagnostic data.

## 5. What Remains Open
A documented row-level timing-residual basis, session or epoch identifiers, pulse-profile or profile-shape observables, dispersion/Scattering or polarization features, or a second comparable dataset would be required before the branch can be reopened for a more diagnostic comparison.

## 6. Reopening Conditions
Reopening requires at least one of the following items to become available and documented: row-level timing residuals with a clear model basis, true session or epoch IDs, W50/W10 pulse widths, profile-shape parameters, scattering timescale, DM variations, polarization, spectral fine structure, calibrated subband/profile features, a comparable control pulsar, a second suitable dataset, or a quantitative QSB prediction that differs from standard GR plus observation design.

## 7. Claim Boundary
This closing note does not assert a new physical or causal result. It only documents the existing branch-freeze status derived from the current SHAPIROMART20 outputs.

## 8. Final Decision
The branch is frozen with status {branch_status}. The closing status is {closing_status}.

> With the currently available data, no independently supported signal finding was established. Weak context-specific descriptive associations remain, but they cannot yet be resolved with the available observation, cluster, and signal structure. The analysis branch is therefore frozen until diagnostically more suitable data become available.
""".format(**summary)
    (output_dir / "shapiromart20_branch_freeze_decision_note.md").write_text(note, encoding="utf-8")


def write_json(output_dir: Path, summary: dict) -> None:
    (output_dir / "shapiromart20_branch_freeze_summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")


def write_csv(output_dir: Path, summary: dict) -> None:
    path = output_dir / "shapiromart20_branch_freeze_decision.csv"
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(build_decision_row(summary).keys()))
        writer.writeheader()
        writer.writerow(build_decision_row(summary))


def main() -> None:
    args = parse_args()
    output_dir = args.output_dir.resolve()
    if not output_dir.exists():
        raise FileNotFoundError(f"Output directory does not exist: {output_dir}")

    ensure_allowed_inputs(output_dir)

    closing_files = [output_dir / name for name in CLOSING_FILES]
    if any(path.exists() for path in closing_files) and not args.overwrite_closing_files:
        raise FileExistsError("Closing files already exist. Re-run with --overwrite-closing-files to replace them only.")

    summary_file = output_dir / "shapiromart20_summary.json"
    final_status_file = output_dir / "shapiromart20_final_status.csv"
    finer_inventory_file = output_dir / "shapiromart20_finer_observable_inventory.csv"

    summary = load_json(summary_file)
    final_status_rows = load_csv_rows(final_status_file)
    if not final_status_rows:
        raise ValueError("No rows found in shapiromart20_final_status.csv")

    ready_count, semantics_incomplete_count, summary_only_count = count_readiness(finer_inventory_file)
    consolidated = build_summary(output_dir, summary, final_status_rows[0], ready_count, semantics_incomplete_count, summary_only_count)

    write_markdown(output_dir, consolidated)
    write_json(output_dir, consolidated)
    write_csv(output_dir, consolidated)


if __name__ == "__main__":
    main()
