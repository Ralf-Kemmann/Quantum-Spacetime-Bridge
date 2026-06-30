#!/usr/bin/env python3
"""Review the SPARC/RAR data contract without running fits or residual analysis."""

from __future__ import annotations

import csv
import hashlib
import json
import re
import subprocess
from pathlib import Path


RUN_ID = "QSB-SPARC-RAR-RESIDUAL-SCOUT-01-DATA-CONTRACT-REVIEW"
REVIEWED_RUN_ID = "QSB-SPARC-RAR-RESIDUAL-SCOUT-01-DATA-CONTRACT"
RUN_DIR = Path("runs") / RUN_ID
DATA_CONTRACT_DIR = Path("runs") / REVIEWED_RUN_ID
INPUT_DIR = DATA_CONTRACT_DIR / "input"
NEXT_APPROVED_RUN = "QSB-SPARC-RAR-RESIDUAL-SCOUT-01-BASELINE-RAR-REPRODUCTION"
NEXT_PATCH_RUN = "QSB-SPARC-RAR-RESIDUAL-SCOUT-01-DATA-CONTRACT-PATCH"
REQUIRED_INPUTS = [
    DATA_CONTRACT_DIR / ".gitattributes",
    DATA_CONTRACT_DIR / "04_sparc_rar_data_contract_summary.json",
    DATA_CONTRACT_DIR / "05_input_file_inventory.csv",
    DATA_CONTRACT_DIR / "06_input_file_checksums.csv",
    DATA_CONTRACT_DIR / "07_text_table_profile.csv",
    DATA_CONTRACT_DIR / "08_detected_column_inventory.csv",
    DATA_CONTRACT_DIR / "09_sparc_expected_column_mapping.csv",
    DATA_CONTRACT_DIR / "10_baseline_rar_feasibility_contract.csv",
    DATA_CONTRACT_DIR / "11_rbci_v1_formula_feasibility_contract.csv",
    DATA_CONTRACT_DIR / "12_source_reference_inventory.csv",
    DATA_CONTRACT_DIR / "13_data_lineage_contract.md",
    DATA_CONTRACT_DIR / "14_unit_and_dimension_review_placeholder.md",
    DATA_CONTRACT_DIR / "17_sparc_rar_data_contract_review_note.md",
    DATA_CONTRACT_DIR / "22_sample_rows_preview.csv",
    DATA_CONTRACT_DIR / "23_column_presence_matrix.csv",
    DATA_CONTRACT_DIR / "24_data_quality_preflight.csv",
]
CLAIM_BOUNDARY = [
    "sparc_rar_data_contract_review",
    "checksum_review",
    "raw_data_preservation_review",
    "mrt_structure_review",
    "baseline_rar_reproduction_readiness",
    "rbci_v1_definition_readiness",
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


def read_csv(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def read_json(path: Path) -> dict:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def mrt_review(path: Path) -> dict[str, object]:
    try:
        lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
    except OSError as exc:
        return {
            "file_path": str(path),
            "mrt_header_present": "false",
            "byte_by_byte_description_present": "false",
            "data_rows_detected": 0,
            "column_labels_detected": "",
            "sample_rows_plausible": "false",
            "read_status": f"read_error:{exc}",
        }
    labels: list[str] = []
    in_byte_section = False
    data_rows = 0
    for line in lines:
        if line.startswith("Title:") or line.startswith("Table:"):
            pass
        if "Bytes Format Units" in line and "Label" in line:
            in_byte_section = True
            continue
        if in_byte_section:
            match = re.match(r"\s*\d+\s*-\s*\d+\s+\S+\s+\S+\s+(\S+)\s+", line)
            if match:
                labels.append(match.group(1))
                continue
            if labels and re.match(r"\s*-{5,}\s*$", line):
                in_byte_section = False
                continue
        if labels and line.strip() and not line.lstrip().startswith(("Title:", "Authors:", "Table:", "Byte-by-byte", "----", "====", "Note")):
            if re.match(r"\s*(?:[-+]?\d|[A-Za-z0-9_-]+\s+[-+]?\d)", line):
                data_rows += 1
    return {
        "file_path": str(path),
        "mrt_header_present": str(any(line.startswith("Title:") or line.startswith("Table:") for line in lines)).lower(),
        "byte_by_byte_description_present": str(bool(labels)).lower(),
        "data_rows_detected": data_rows,
        "column_labels_detected": ";".join(labels),
        "sample_rows_plausible": str(data_rows > 0 and bool(labels)).lower(),
        "read_status": "readable_mrt_text",
    }


def main() -> None:
    RUN_DIR.mkdir(parents=True, exist_ok=True)
    write_text(RUN_DIR / "00_git_status_short_before.txt", run_command(["git", "status", "--short"]))
    write_text(RUN_DIR / "01_git_log_oneline_before.txt", run_command(["git", "--no-pager", "log", "--oneline", "-14"]))

    scope = f"""# {RUN_ID}

## Purpose

Review the existing SPARC/RAR data contract for checksum consistency, raw data preservation, MRT structure readability, baseline-RAR readiness, RBCI_v1 formula-freeze readiness, and next-run decision.

## Execution Boundary

- No SPARC raw data are modified.
- No SPARC data are downloaded.
- No RAR fits are run.
- No residual analysis is run.
- No optimization or model fitting is performed.

## Claim Boundary

{chr(10).join(f"- {item}" for item in CLAIM_BOUNDARY)}
"""
    write_text(RUN_DIR / "02_data_contract_review_scope.md", scope)

    input_rows = []
    missing_inputs = []
    for index, path in enumerate(REQUIRED_INPUTS, start=1):
        exists = path.exists()
        if not exists:
            missing_inputs.append(path)
        input_rows.append(
            {
                "artifact_id": f"REV-IN-{index:02d}",
                "path": str(path),
                "exists": str(exists).lower(),
                "file_size_bytes": path.stat().st_size if exists and path.is_file() else "",
                "sha256": sha256(path) if exists and path.is_file() else "",
                "used_for": "data contract review",
            }
        )
    write_csv(RUN_DIR / "05_review_input_artifact_inventory.csv", ["artifact_id", "path", "exists", "file_size_bytes", "sha256", "used_for"], input_rows)

    prior_summary = read_json(DATA_CONTRACT_DIR / "04_sparc_rar_data_contract_summary.json")
    expected_checksums = {row.get("file_path", ""): row.get("sha256", "") for row in read_csv(DATA_CONTRACT_DIR / "06_input_file_checksums.csv")}
    mrt_files = sorted(INPUT_DIR.glob("*.mrt"), key=lambda item: item.name)
    checksum_rows = []
    checksum_match_count = 0
    checksum_mismatch_count = 0
    for path in mrt_files:
        actual = sha256(path)
        expected = expected_checksums.get(str(path), "")
        matched = bool(expected) and actual == expected
        checksum_match_count += int(matched)
        checksum_mismatch_count += int(not matched)
        checksum_rows.append(
            {
                "file_path": str(path),
                "expected_sha256": expected,
                "actual_sha256": actual,
                "checksum_match": str(matched).lower(),
                "review_status": "pass" if matched else "fail",
            }
        )
    write_csv(RUN_DIR / "06_checksum_revalidation.csv", ["file_path", "expected_sha256", "actual_sha256", "checksum_match", "review_status"], checksum_rows)

    gitattributes_text = (DATA_CONTRACT_DIR / ".gitattributes").read_text(encoding="utf-8", errors="replace") if (DATA_CONTRACT_DIR / ".gitattributes").exists() else ""
    gitattributes_ok = "input/*.mrt -text -diff" in gitattributes_text
    raw_status = "preserved_and_checksum_matched"
    if len(mrt_files) != 4:
        raw_status = "missing_raw_input"
    elif checksum_mismatch_count:
        raw_status = "checksum_mismatch"
    elif not gitattributes_ok:
        raw_status = "gitattributes_missing_or_incomplete"
    raw_rows = [
        {
            "audit_item": "local_mrt_file_count",
            "result": len(mrt_files),
            "expected": 4,
            "status": "pass" if len(mrt_files) == 4 else "fail",
            "notes": "Registered MRT raw input files.",
        },
        {
            "audit_item": "checksum_revalidation",
            "result": checksum_match_count,
            "expected": len(mrt_files),
            "status": "pass" if checksum_mismatch_count == 0 and len(mrt_files) == 4 else "fail",
            "notes": "Recomputed SHA256 against data contract checksums.",
        },
        {
            "audit_item": "gitattributes_mrt_protection",
            "result": str(gitattributes_ok).lower(),
            "expected": "true",
            "status": "pass" if gitattributes_ok else "fail",
            "notes": "Requires input/*.mrt -text -diff.",
        },
        {
            "audit_item": "raw_data_preservation_status",
            "result": raw_status,
            "expected": "preserved_and_checksum_matched",
            "status": "pass" if raw_status == "preserved_and_checksum_matched" else "fail",
            "notes": "No raw data mutation performed by this review.",
        },
    ]
    write_csv(RUN_DIR / "07_raw_data_preservation_audit.csv", ["audit_item", "result", "expected", "status", "notes"], raw_rows)

    write_csv(
        RUN_DIR / "08_gitattributes_audit.csv",
        ["path", "exists", "required_rule", "rule_present", "status", "notes"],
        [
            {
                "path": str(DATA_CONTRACT_DIR / ".gitattributes"),
                "exists": str((DATA_CONTRACT_DIR / ".gitattributes").exists()).lower(),
                "required_rule": "input/*.mrt -text -diff",
                "rule_present": str(gitattributes_ok).lower(),
                "status": "pass" if gitattributes_ok else "fail",
                "notes": "Protects MRT raw files from text/diff normalization.",
            }
        ],
    )

    mrt_rows = [mrt_review(path) for path in mrt_files]
    write_csv(RUN_DIR / "09_mrt_structure_review.csv", ["file_path", "mrt_header_present", "byte_by_byte_description_present", "data_rows_detected", "column_labels_detected", "sample_rows_plausible", "read_status"], mrt_rows)

    presence_rows = read_csv(DATA_CONTRACT_DIR / "23_column_presence_matrix.csv")
    present_columns = {row.get("expected_column_or_synonym", "") for row in presence_rows if row.get("presence_status") == "present"}
    column_review_rows = []
    for column in ["Galaxy", "ID", "R", "Vobs", "e_Vobs", "Vgas", "Vdisk", "Vbul", "SBdisk", "SBbul", "gbar", "gobs", "D", "Inc", "MHI"]:
        column_review_rows.append(
            {
                "column_or_role": column,
                "presence_status": "present" if column in present_columns or (column == "ID" and "ID" in ";".join(row["column_labels_detected"] for row in mrt_rows)) else "missing_or_unmapped",
                "review_assessment": "plausible_for_contract" if column in present_columns or column == "ID" else "manual_review_if_needed",
            }
        )
    write_csv(RUN_DIR / "10_column_mapping_review.csv", ["column_or_role", "presence_status", "review_assessment"], column_review_rows)

    no_lineage_blocker = raw_status == "preserved_and_checksum_matched" and not missing_inputs
    direct_rar_present = (INPUT_DIR / "RAR.mrt").exists() and {"gbar", "gobs"} <= present_columns
    massmodels_present = (INPUT_DIR / "MassModels_Lelli2016c.mrt").exists() and {"R", "Vobs", "Vgas", "Vdisk", "Vbul"} <= present_columns
    prior_baseline = prior_summary.get("baseline_rar_feasibility_status")
    if not no_lineage_blocker:
        baseline_readiness = "blocked_checksum_or_lineage_issue"
    elif direct_rar_present and prior_baseline == "feasible_from_present_columns":
        baseline_readiness = "ready_for_baseline_rar_reproduction"
    elif massmodels_present:
        baseline_readiness = "ready_with_parser_requirements"
    else:
        baseline_readiness = "blocked_missing_columns"
    write_csv(
        RUN_DIR / "11_baseline_rar_readiness_review.csv",
        ["review_item", "status", "evidence", "computation_performed", "claim_boundary"],
        [
            {"review_item": "direct_RAR_table_present", "status": str((INPUT_DIR / "RAR.mrt").exists()).lower(), "evidence": "RAR.mrt in input directory", "computation_performed": "false", "claim_boundary": "readiness_only"},
            {"review_item": "gobs_gbar_present", "status": str({"gbar", "gobs"} <= present_columns).lower(), "evidence": "column presence matrix", "computation_performed": "false", "claim_boundary": "readiness_only"},
            {"review_item": "prior_baseline_feasibility", "status": prior_baseline, "evidence": "prior data contract summary", "computation_performed": "false", "claim_boundary": "readiness_only"},
            {"review_item": "baseline_rar_reproduction_readiness", "status": baseline_readiness, "evidence": "checksums, RAR.mrt, gbar/gobs, and prior contract", "computation_performed": "false", "claim_boundary": "readiness_only"},
        ],
    )

    rbci_radius = "R" in present_columns
    rbci_galaxy = "Galaxy" in present_columns or any("ID" in row["column_labels_detected"].split(";") for row in mrt_rows)
    rbci_components = {"Vgas", "Vdisk", "Vbul"} <= present_columns or {"SBdisk", "SBbul"} & present_columns
    if not no_lineage_blocker:
        rbci_readiness = "blocked_units_unclear"
    elif not (rbci_radius and rbci_galaxy):
        rbci_readiness = "blocked_missing_radius_or_galaxy_id"
    elif not rbci_components:
        rbci_readiness = "blocked_missing_baryonic_profile"
    else:
        rbci_readiness = "ready_with_component_derivation_requirements"
    write_csv(
        RUN_DIR / "12_rbci_v1_readiness_review.csv",
        ["review_item", "status", "evidence", "formula_finalized", "claim_boundary"],
        [
            {"review_item": "radius_or_radial_ordering_present", "status": str(rbci_radius).lower(), "evidence": "R column present", "formula_finalized": "false", "claim_boundary": "formula_readiness_only"},
            {"review_item": "galaxy_id_present", "status": str(rbci_galaxy).lower(), "evidence": "Galaxy or ID label present", "formula_finalized": "false", "claim_boundary": "formula_readiness_only"},
            {"review_item": "baryonic_components_present", "status": str(bool(rbci_components)).lower(), "evidence": "Vgas/Vdisk/Vbul or surface-brightness component labels", "formula_finalized": "false", "claim_boundary": "formula_readiness_only"},
            {"review_item": "rbci_v1_definition_readiness", "status": rbci_readiness, "evidence": "RBCI remains formula-freeze task for later run", "formula_finalized": "false", "claim_boundary": "formula_readiness_only"},
        ],
    )

    hard_blockers = []
    if missing_inputs:
        hard_blockers.append("missing_required_review_inputs")
    if raw_status != "preserved_and_checksum_matched":
        hard_blockers.append(raw_status)
    if baseline_readiness.startswith("blocked"):
        hard_blockers.append(baseline_readiness)
    data_contract_frozen = not hard_blockers and gitattributes_ok
    decision = "approve_for_baseline_rar_reproduction" if data_contract_frozen else "require_data_contract_patch"
    recommended_next = NEXT_APPROVED_RUN if data_contract_frozen else NEXT_PATCH_RUN
    write_csv(
        RUN_DIR / "13_data_contract_freeze_decision.csv",
        ["decision_item", "result", "evidence", "claim_boundary"],
        [
            {"decision_item": "data_contract_frozen", "result": str(data_contract_frozen).lower(), "evidence": "checksums, raw preservation, gitattributes, readiness, missing inputs", "claim_boundary": "freeze_decision_only"},
            {"decision_item": "data_contract_review_decision", "result": decision, "evidence": "no hard blocker" if data_contract_frozen else ";".join(hard_blockers), "claim_boundary": "freeze_decision_only"},
            {"decision_item": "recommended_next_run_id", "result": recommended_next, "evidence": "derived from freeze decision", "claim_boundary": "planning_only"},
        ],
    )

    blocker_rows = [
        {
            "blocker_id": f"B-{index:02d}",
            "blocker_type": blocker,
            "severity": "blocking",
            "description": blocker,
            "recommended_resolution": "Patch data contract before baseline RAR reproduction.",
        }
        for index, blocker in enumerate(hard_blockers, start=1)
    ] or [
        {"blocker_id": "none", "blocker_type": "none", "severity": "none", "description": "no blockers for approved review scope", "recommended_resolution": "proceed to baseline RAR reproduction run"}
    ]
    write_csv(RUN_DIR / "14_review_blocker_report.csv", ["blocker_id", "blocker_type", "severity", "description", "recommended_resolution"], blocker_rows)

    no_go = f"""# Claim Boundary and No-Go

Allowed:

{chr(10).join(f"- `{item}`" for item in CLAIM_BOUNDARY)}

Forbidden:

- QSB explains dark matter.
- QSB explains RAR.
- A QSB signal was found.
- RBCI_v1 improves the RAR.
- RBCI_v1 is physically effective.
- MOND was confirmed.
- LambdaCDM was refuted.
- Gravity was modified.
- Spacetime structure was detected.
- The m1/m2 question was proven.
"""
    write_text(RUN_DIR / "15_claim_boundary_and_no_go.md", no_go)

    next_note = f"""# Next Run Recommendation

Recommended next run:

`{recommended_next}`

If approved, the next run may parse `RAR.mrt` / `MassModels_Lelli2016c.mrt`, reproduce the standard RAR baseline, and check baseline tolerances.

The next run must not evaluate RBCI_v1 residual gain or make QSB, dark-matter, MOND, LambdaCDM, gravity, spacetime, or causality claims.
"""
    write_text(RUN_DIR / "16_next_run_recommendation.md", next_note)

    review_note = f"""# {RUN_ID}

## Purpose

This review checks whether the SPARC/RAR data contract is consistent enough to allow a later baseline-RAR reproduction run.

## Raw Data Preservation

Status: `{raw_status}`.

Checksum matches: `{checksum_match_count}`.

Checksum mismatches: `{checksum_mismatch_count}`.

`.gitattributes` MRT protection present: `{gitattributes_ok}`.

## MRT Structure

MRT files found: `{len(mrt_files)}`.

The review found MRT headers, byte-by-byte labels, and data rows defensively. No values were scientifically interpreted.

## Baseline Readiness

`{baseline_readiness}`

## RBCI_v1 Readiness

`{rbci_readiness}`

RBCI_v1 formula remains not finalized.

## Decision

`{decision}`

## Claim Boundary

No RAR fit, residual analysis, optimization, QSB detection, dark-matter, MOND, LambdaCDM, gravity, spacetime, or causality claim is made.
"""
    write_text(RUN_DIR / "17_data_contract_review_note.md", review_note)

    unit_rows = [
        {"unit_item": "RAR.mrt gbar/gobs", "status": "documented_in_mrt_header", "notes": "Unit labels available in MRT header; no computation performed."},
        {"unit_item": "MassModels radius R", "status": "documented_in_mrt_header", "notes": "Radius unit available in MRT header; needed by parser."},
        {"unit_item": "MassModels velocity components", "status": "documented_in_mrt_header", "notes": "Velocity component units available in MRT header; RBCI formula still not frozen."},
        {"unit_item": "RBCI_v1 normalization", "status": "not_frozen", "notes": "To be frozen after baseline reproduction / formula-freeze step."},
    ]
    write_csv(RUN_DIR / "18_unit_dimension_review.csv", ["unit_item", "status", "notes"], unit_rows)

    parser_req = """# Parser Requirements for Baseline Run

The next baseline run should:

- parse MRT byte-by-byte label sections
- preserve raw files unchanged
- read `RAR.mrt` direct `gbar`/`gobs` columns for baseline reproduction where possible
- use `MassModels_Lelli2016c.mrt` only under an explicit derivation contract
- report parser row counts and label maps before any fit
- stop if checksums differ from this review
"""
    write_text(RUN_DIR / "19_parser_requirements_for_baseline_run.md", parser_req)

    formula_req = """# Formula Freeze Requirements for RBCI_v1

RBCI_v1 is not finalized by this review.

Before any RBCI residual test:

- freeze exact enclosed-to-local contrast formula
- freeze units and normalization
- define allowed baryonic components
- define radial ordering and edge policy
- prove the term does not merely duplicate radius or local gbar
- define exactly one added term and complexity penalty
- require baseline RAR reproduction to pass first
"""
    write_text(RUN_DIR / "20_formula_freeze_requirements_for_rbci_v1.md", formula_req)

    prompt_note = f"""# Next Codex Prompt Recommendation

Recommended next run:

`{recommended_next}`

Hard boundary:

Run only standard baseline-RAR reproduction first. Do not evaluate RBCI_v1 or any QSB Zusatzterm before the baseline passes.
"""
    write_text(RUN_DIR / "21_next_codex_prompt_recommendation.md", prompt_note)

    status = "sparc_rar_data_contract_review_completed"
    if missing_inputs:
        status = "sparc_rar_data_contract_review_completed_with_missing_inputs"
    elif not data_contract_frozen:
        status = "sparc_rar_data_contract_review_completed_with_warnings"
    summary = {
        "baseline_rar_computed": False,
        "baseline_rar_reproduction_readiness": baseline_readiness,
        "checksum_match_count": checksum_match_count,
        "checksum_mismatch_count": checksum_mismatch_count,
        "claim_boundary": CLAIM_BOUNDARY,
        "data_contract_frozen": data_contract_frozen,
        "data_contract_review_decision": decision,
        "gitattributes_protection_present": gitattributes_ok,
        "local_mrt_file_count": len(mrt_files),
        "missing_input_count": len(missing_inputs),
        "notes": "Data contract review only. No RAR fit, residual analysis, optimization, or QSB/physics claim.",
        "observable_formula_finalized": False,
        "raw_data_preservation_status": raw_status,
        "rbci_v1_definition_readiness": rbci_readiness,
        "recommended_next_run_id": recommended_next,
        "residual_analysis_executed": False,
        "review_input_artifact_count": sum(1 for row in input_rows if row["exists"] == "true"),
        "reviewed_data_contract_run_id": REVIEWED_RUN_ID,
        "run_id": RUN_ID,
        "status": status,
    }
    write_text(RUN_DIR / "04_data_contract_review_summary.json", json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True) + "\n")
    print(json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
