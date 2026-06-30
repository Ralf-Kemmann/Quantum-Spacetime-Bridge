#!/usr/bin/env python3
"""Create the SPARC/RAR residual scout precontract artifacts."""

from __future__ import annotations

import csv
import hashlib
import json
import subprocess
from pathlib import Path


RUN_ID = "QSB-SPARC-RAR-RESIDUAL-SCOUT-01-PRECONTRACT"
RUN_DIR = Path("runs") / RUN_ID
NEXT_RUN_ID = "QSB-SPARC-RAR-RESIDUAL-SCOUT-01-DATA-CONTRACT"
FUTURE_INPUT_DIR = Path("runs") / NEXT_RUN_ID / "input"
INPUTS = [
    Path("runs/QSB-OBSERVATIONAL-CANDIDATE-SCOUT-01/input/deep_research_report.md"),
    Path("runs/QSB-OBSERVATIONAL-CANDIDATE-SCOUT-01-DEEP-RESEARCH-INGEST/04_deep_research_ingest_summary.json"),
    Path("runs/QSB-OBSERVATIONAL-CANDIDATE-SCOUT-01-DEEP-RESEARCH-INGEST/07_scoring_matrix_extracted.csv"),
    Path("runs/QSB-OBSERVATIONAL-CANDIDATE-SCOUT-01-DEEP-RESEARCH-INGEST/08_narrative_priority_ranking.csv"),
    Path("runs/QSB-OBSERVATIONAL-CANDIDATE-SCOUT-01-DEEP-RESEARCH-INGEST/11_observable_contract_requirements.csv"),
    Path("runs/QSB-OBSERVATIONAL-CANDIDATE-SCOUT-01-DEEP-RESEARCH-INGEST/14_best_first_practical_run_extract.md"),
    Path("runs/QSB-OBSERVATIONAL-CANDIDATE-SCOUT-01-DEEP-RESEARCH-INGEST/15_next_run_recommendation.md"),
    Path("runs/QSB-OBSERVATIONAL-CANDIDATE-SCOUT-01-DEEP-RESEARCH-INGEST/16_deep_research_ingest_review_note.md"),
]
CLAIM_BOUNDARY = [
    "sparc_rar_residual_scout_precontract",
    "observable_candidate_definition",
    "methodological_preparation_only",
    "no_qsb_detection_claim",
    "no_dark_matter_claim",
    "no_mond_claim",
    "no_lambdacdm_refutation_claim",
    "no_gravity_claim",
    "no_spacetime_claim",
    "no_causality_claim",
]


def run_command(args: list[str]) -> str:
    completed = subprocess.run(args, check=False, text=True, capture_output=True)
    text = completed.stdout
    if completed.stderr:
        text += completed.stderr
    return text


def write_text(path: Path, text: str) -> None:
    path.write_text(text, encoding="utf-8")


def write_csv(path: Path, fieldnames: list[str], rows: list[dict[str, object]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, lineterminator="\n", extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def input_inventory() -> tuple[list[dict[str, object]], list[Path]]:
    rows = []
    missing = []
    for index, path in enumerate(INPUTS, start=1):
        exists = path.exists()
        if not exists:
            missing.append(path)
        rows.append(
            {
                "artifact_id": f"IN-{index:02d}",
                "path": str(path),
                "exists": str(exists).lower(),
                "sha256": sha256(path) if exists and path.is_file() else "",
                "file_size_bytes": path.stat().st_size if exists and path.is_file() else "",
                "used_for": "precontract source context",
                "claim_boundary": "input_inventory_only_no_external_verification",
            }
        )
    return rows, missing


def main() -> None:
    RUN_DIR.mkdir(parents=True, exist_ok=True)
    write_text(RUN_DIR / "00_git_status_short_before.txt", run_command(["git", "status", "--short"]))
    write_text(RUN_DIR / "01_git_log_oneline_before.txt", run_command(["git", "--no-pager", "log", "--oneline", "-14"]))

    inventory_rows, missing = input_inventory()
    status = "sparc_rar_precontract_completed" if not missing else "sparc_rar_precontract_completed_with_missing_inputs"

    scope = f"""# {RUN_ID}

## Purpose

This is a precontract run for a later SPARC/RAR residual scout. It defines the audit contract for baseline reproduction, exactly one candidate relational Zusatzobservable, null models, complexity protection, no-go conditions, and the next data-contract run.

## Non-Execution Boundary

- No SPARC data were downloaded.
- No residual analysis was executed.
- No external source was queried.
- No existing run artifacts were modified.

## Input Condition

Missing input count: `{len(missing)}`.

## Claim Boundary

{chr(10).join(f"- {item}" for item in CLAIM_BOUNDARY)}
"""
    write_text(RUN_DIR / "02_sparc_rar_precontract_scope.md", scope)

    write_csv(
        RUN_DIR / "05_input_artifact_inventory.csv",
        ["artifact_id", "path", "exists", "sha256", "file_size_bytes", "used_for", "claim_boundary"],
        inventory_rows,
    )

    baseline_rows = [
        {
            "baseline_model_id": "SPARC_RAR_BASELINE_REPRODUCTION_V1",
            "baseline_inputs": "public SPARC/RAR data package to be registered in the next data-contract run",
            "baseline_outputs": "standard_RAR_reproduction_table; baseline_fit_summary; residual_table_before_RBCI",
            "baseline_success_criteria": "public SPARC/RAR relation must be reproduced within declared tolerance before any RBCI candidate term is evaluated",
            "baseline_failure_handling": "if baseline is not reproducible, stop and do not interpret any QSB Zusatzobservable result",
            "claim_boundary": "baseline_reproduction_required_no_qsb_interpretation",
        }
    ]
    write_csv(
        RUN_DIR / "06_sparc_rar_baseline_contract.csv",
        [
            "baseline_model_id",
            "baseline_inputs",
            "baseline_outputs",
            "baseline_success_criteria",
            "baseline_failure_handling",
            "claim_boundary",
        ],
        baseline_rows,
    )

    observable_rows = [
        {
            "observable_candidate_id": "RBCI_v1",
            "observable_candidate_name": "qsb_relational_baryonic_configuration_index_v1",
            "working_family": "enclosed-to-local baryonic contrast index",
            "primary_variant_selected": "true",
            "core_intent": "measure whether a rotation-curve point sits in a locally under/over-represented baryonic shell relative to the enclosed baryonic distribution",
            "formula_status": "not_finalized_pending_sparc_column_contract",
            "units_and_normalization_status": "to_define_after_available_columns_are_profiled",
            "allowed_parameter_count": "exactly_one_added_candidate_term; no uncontrolled parameter expansion",
            "must_be_derivable_from": "public SPARC profiles registered in the next data-contract run",
            "must_not_duplicate": "radius_only_or_local_gbar_only_information",
            "claim_boundary": "observable_candidate_definition_only_no_qsb_detection_claim",
        }
    ]
    write_csv(
        RUN_DIR / "07_qsb_observable_candidate_contract.csv",
        [
            "observable_candidate_id",
            "observable_candidate_name",
            "working_family",
            "primary_variant_selected",
            "core_intent",
            "formula_status",
            "units_and_normalization_status",
            "allowed_parameter_count",
            "must_be_derivable_from",
            "must_not_duplicate",
            "claim_boundary",
        ],
        observable_rows,
    )

    rbci_note = """# RBCI_v1 Definition Note

Primary observable candidate:

`qsb_relational_baryonic_configuration_index_v1` (`RBCI_v1`)

Selected candidate family:

`enclosed-to-local baryonic contrast index`

Working idea:

`RBCI_v1` should measure whether a rotation-curve point sits in a locally under- or over-represented baryonic shell relative to the enclosed baryonic distribution.

Formula boundary:

No final formula is asserted in this precontract. The exact formula, units, required SPARC columns, interpolation rules, normalization, missing-value policy, and allowed transformations must be frozen in the next data-contract run after available SPARC columns are profiled.

Design constraints:

- exactly one additional candidate term
- derivable from public SPARC profiles
- no uncontrolled parameter expansion
- not merely radius information
- not merely local baryonic acceleration duplication
- no QSB detection, dark-matter, MOND, LambdaCDM, gravity, spacetime, or causality claim
"""
    write_text(RUN_DIR / "08_rbci_v1_definition_note.md", rbci_note)

    nullmodel_rows = [
        {"nullmodel_id": "N0", "nullmodel_name": "baseline RAR only", "purpose": "establish baseline residuals before RBCI", "execution_status": "not_executed_precontract_only", "required_for_interpretation": "yes"},
        {"nullmodel_id": "N1", "nullmodel_name": "shuffled RBCI labels within galaxy", "purpose": "test within-galaxy label dependence", "execution_status": "not_executed_precontract_only", "required_for_interpretation": "yes"},
        {"nullmodel_id": "N2", "nullmodel_name": "shuffled RBCI labels across comparable radius bins", "purpose": "test radius-bin confounding", "execution_status": "not_executed_precontract_only", "required_for_interpretation": "yes"},
        {"nullmodel_id": "N3", "nullmodel_name": "galaxy-wise bootstrap", "purpose": "test sample stability across galaxies", "execution_status": "not_executed_precontract_only", "required_for_interpretation": "yes"},
        {"nullmodel_id": "N4", "nullmodel_name": "leave-one-galaxy-out / out-of-sample validation", "purpose": "test out-of-sample predictive behavior", "execution_status": "not_executed_precontract_only", "required_for_interpretation": "yes"},
        {"nullmodel_id": "N5", "nullmodel_name": "complexity-penalized added-term test", "purpose": "guard against in-sample overfit", "execution_status": "not_executed_precontract_only", "required_for_interpretation": "yes"},
    ]
    write_csv(
        RUN_DIR / "09_nullmodel_contract.csv",
        ["nullmodel_id", "nullmodel_name", "purpose", "execution_status", "required_for_interpretation"],
        nullmodel_rows,
    )

    complexity = """# Complexity Penalty Contract

The later execution run must preserve these constraints:

- exactly one additional candidate term: `RBCI_v1`
- no uncontrolled parameter expansion
- report AIC/BIC or an equivalent complexity penalty if feasible
- report cross-validation or leave-one-galaxy-out validation if feasible
- no interpretation if improvement is only in-sample
- no tuning of RBCI formula after observing residual improvement
- any formula change after data profiling requires a new precontract or explicit amendment

Interpretation boundary:

Only out-of-sample or complexity-penalized residual improvement may be called a candidate residual structure. It must not be called QSB detection, dark-matter explanation, gravity claim, spacetime claim, or causality claim.
"""
    write_text(RUN_DIR / "10_complexity_penalty_contract.md", complexity)

    criteria_rows = [
        {"outcome_id": "baseline_reproduction_failed", "condition": "standard RAR baseline cannot be reproduced within declared tolerance", "allowed_interpretation": "analysis blocked; no RBCI interpretation", "next_action": "repair data/baseline contract"},
        {"outcome_id": "baseline_reproduced_no_residual_gain", "condition": "baseline reproduces and RBCI_v1 adds no residual improvement", "allowed_interpretation": "no candidate residual structure found under this contract", "next_action": "record negative/control result"},
        {"outcome_id": "baseline_reproduced_in_sample_gain_only", "condition": "RBCI_v1 improves only in-sample without penalty/out-of-sample support", "allowed_interpretation": "overfit risk; no candidate residual structure claim", "next_action": "strengthen controls or stop"},
        {"outcome_id": "baseline_reproduced_out_of_sample_gain_candidate", "condition": "RBCI_v1 improves residuals out-of-sample or under complexity penalty", "allowed_interpretation": "candidate residual structure only; no QSB detection", "next_action": "independent replication/robustness run"},
        {"outcome_id": "analysis_blocked_by_data_contract", "condition": "SPARC columns, units, lineage, or formula feasibility cannot be frozen", "allowed_interpretation": "blocked before residual analysis", "next_action": "complete data-contract remediation"},
    ]
    write_csv(
        RUN_DIR / "11_success_failure_criteria.csv",
        ["outcome_id", "condition", "allowed_interpretation", "next_action"],
        criteria_rows,
    )

    claim_note = f"""# Claim Boundary and No-Go

Allowed:

{chr(10).join(f"- `{item}`" for item in CLAIM_BOUNDARY)}

Forbidden:

- QSB explains dark matter.
- QSB explains RAR.
- QSB refutes LambdaCDM.
- QSB confirms MOND.
- QSB replaces gravity.
- A QSB signal was found.
- Spacetime structure was detected.
- The m1/m2 question was proven.

This run only defines a precontract for a later residual scout.
"""
    write_text(RUN_DIR / "12_claim_boundary_and_no_go.md", claim_note)

    next_contract = f"""# Next Execution Run Contract

Next run:

`{NEXT_RUN_ID}`

Goal:

Download/register the SPARC data package manually or via a documented source, profile available columns, define exact formula feasibility for `RBCI_v1`, and freeze the data contract before any residual analysis.

Required sequence:

1. Register source package and checksums.
2. Profile available files and columns.
3. Freeze units, missing-value rules, and lineage.
4. Decide whether `RBCI_v1` is formula-feasible from public SPARC profiles.
5. Freeze exact RBCI formula or block before residual analysis.

No residual analysis before data contract is frozen.
"""
    write_text(RUN_DIR / "13_next_execution_run_contract.md", next_contract)

    review = f"""# {RUN_ID}

## Purpose

This precontract prepares a later SPARC/RAR residual scout. It does not execute a SPARC data analysis.

## Source Basis

The observational Deep Research ingest identified SPARC/RAR as the best immediate practical scout and matterwave/interferometry as mechanistically closest to the QSB guiding idea. This precontract uses only repository-local ingest artifacts.

## Baseline First

The later execution run must reproduce the standard SPARC/RAR baseline before evaluating `RBCI_v1`. If baseline reproduction fails, no QSB Zusatzobservable result may be interpreted.

## Primary Observable Candidate

Primary candidate: `RBCI_v1`, an enclosed-to-local baryonic contrast index. The exact formula is not finalized because SPARC columns, units, and available profiles are not frozen in this run.

## Nullmodels

Six null/control definitions are prepared: N0 through N5. They are contracts only, not executed results.

## Overfit Protection

The next execution design must use exactly one candidate term and preserve complexity penalties or out-of-sample validation before any candidate residual structure language is allowed.

## Claim Boundary

No QSB detection, dark-matter, MOND, LambdaCDM-refutation, gravity, spacetime, or causality claim is made.

## Next Run

`{NEXT_RUN_ID}`
"""
    write_text(RUN_DIR / "14_sparc_rar_precontract_review_note.md", review)

    data_plan = f"""# Data Acquisition Plan

No data are downloaded in this precontract.

Expected future input directory:

`{FUTURE_INPUT_DIR}`

Expected SPARC public data package:

- public SPARC/RAR source package or manually registered equivalent
- rotation-curve tables
- baryonic component/model tables where available
- metadata/readme/citation files
- checksums for every registered source file

Requirements:

- no manual editing of downloaded/registered data
- preserve original files read-only
- create checksum inventory
- record source URL/reference and access date in the future data-contract run
- define local normalized copies only as derived artifacts with lineage back to originals
- no residual analysis until the data contract is frozen
"""
    write_text(RUN_DIR / "15_data_acquisition_plan.md", data_plan)

    column_rows = [
        {"column_role": "galaxy_id", "required": "yes", "status": "to_define_after_sparc_profile", "notes": "Stable galaxy identifier."},
        {"column_role": "radius", "required": "yes", "status": "to_define_after_sparc_profile", "notes": "Radius coordinate; units must be frozen."},
        {"column_role": "observed_velocity_or_acceleration", "required": "yes", "status": "to_define_after_sparc_profile", "notes": "Required for baseline RAR reproduction."},
        {"column_role": "baryonic_acceleration_or_components", "required": "yes", "status": "to_define_after_sparc_profile", "notes": "Required for standard RAR and RBCI feasibility."},
        {"column_role": "uncertainties", "required": "preferred", "status": "to_define_after_sparc_profile", "notes": "Required for weighted fits if available."},
        {"column_role": "quality_flags", "required": "preferred", "status": "to_define_after_sparc_profile", "notes": "Required for exclusion policy if available."},
    ]
    write_csv(RUN_DIR / "16_sparc_column_contract_placeholder.csv", ["column_role", "required", "status", "notes"], column_rows)

    formula_todo = """# Observable Formula TODO

`RBCI_v1` formula is not finalized in this precontract.

To define in the data-contract run:

1. Identify available SPARC baryonic profile columns.
2. Decide whether enclosed baryonic distribution can be computed directly or approximated from available profiles.
3. Define local shell quantity.
4. Define enclosed-to-local contrast.
5. Define normalization and units.
6. Define missing-value and edge-radius policy.
7. Prove the formula does not merely duplicate radius or local baryonic acceleration.
8. Freeze exactly one formula before residual analysis.
"""
    write_text(RUN_DIR / "17_observable_formula_todo.md", formula_todo)

    next_prompt = f"""# Next Codex Prompt Recommendation

Recommended next run:

`{NEXT_RUN_ID}`

Prompt objective:

Create a data-contract run that registers the SPARC public data package, profiles all available files and columns, creates checksums/lineage, and decides whether `RBCI_v1` can be exactly formulated from public SPARC profiles.

Hard stop:

Do not run residual analysis before the data contract and exact observable formula are frozen.
"""
    write_text(RUN_DIR / "18_next_codex_prompt_recommendation.md", next_prompt)

    summary = {
        "baseline_required_before_qsb_candidate": True,
        "claim_boundary": CLAIM_BOUNDARY,
        "complexity_penalty_required": True,
        "input_artifact_count": sum(1 for row in inventory_rows if row["exists"] == "true"),
        "missing_input_count": len(missing),
        "nullmodel_count": 6,
        "observable_formula_finalized": False,
        "primary_observable_candidate_id": "RBCI_v1",
        "primary_observable_candidate_name": "qsb_relational_baryonic_configuration_index_v1",
        "recommended_next_run_id": NEXT_RUN_ID,
        "residual_analysis_executed": False,
        "run_id": RUN_ID,
        "sparc_data_downloaded": False,
        "status": status,
        "notes": "Precontract only. No SPARC data download, no residual analysis, and no QSB/dark-matter/gravity/spacetime claim.",
    }
    write_text(RUN_DIR / "04_sparc_rar_precontract_summary.json", json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True) + "\n")
    print(json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
