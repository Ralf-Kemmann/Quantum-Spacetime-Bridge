#!/usr/bin/env python3
"""Create a SPARC/RAR data contract without running residual analysis."""

from __future__ import annotations

import csv
import hashlib
import json
import re
import subprocess
from pathlib import Path


RUN_ID = "QSB-SPARC-RAR-RESIDUAL-SCOUT-01-DATA-CONTRACT"
RUN_DIR = Path("runs") / RUN_ID
INPUT_DIR = RUN_DIR / "input"
PRECONTRACT_CONTEXT = [
    Path("runs/QSB-SPARC-RAR-RESIDUAL-SCOUT-01-PRECONTRACT/04_sparc_rar_precontract_summary.json"),
    Path("runs/QSB-SPARC-RAR-RESIDUAL-SCOUT-01-PRECONTRACT/13_next_execution_run_contract.md"),
    Path("runs/QSB-SPARC-RAR-RESIDUAL-SCOUT-01-PRECONTRACT/15_data_acquisition_plan.md"),
    Path("runs/QSB-SPARC-RAR-RESIDUAL-SCOUT-01-PRECONTRACT/16_sparc_column_contract_placeholder.csv"),
    Path("runs/QSB-SPARC-RAR-RESIDUAL-SCOUT-01-PRECONTRACT/17_observable_formula_todo.md"),
    Path("runs/QSB-OBSERVATIONAL-CANDIDATE-SCOUT-01-DEEP-RESEARCH-INGEST/13_public_data_source_extract.csv"),
    Path("runs/QSB-OBSERVATIONAL-CANDIDATE-SCOUT-01-DEEP-RESEARCH-INGEST/17_source_url_inventory.csv"),
]
CLAIM_BOUNDARY = [
    "sparc_rar_data_contract",
    "data_source_registration",
    "file_inventory",
    "checksum_lineage",
    "column_profile",
    "baseline_feasibility_assessment_only",
    "rbci_v1_formula_feasibility_assessment_only",
    "methodological_preparation_only",
    "no_qsb_detection_claim",
    "no_dark_matter_claim",
    "no_mond_claim",
    "no_lambdacdm_refutation_claim",
    "no_gravity_claim",
    "no_spacetime_claim",
    "no_causality_claim",
]
EXPECTED_COLUMNS = [
    "Name", "Galaxy", "R", "Rad", "Radius", "Vobs", "e_Vobs", "Vgas", "Vdisk", "Vbul",
    "SBdisk", "SBbul", "Lum", "MHI", "gobs", "gbar", "gdag", "loggobs", "loggbar",
    "D", "Dist", "Inc", "L", "Mstar", "Mgas",
]
DELIMITERS = [(",", "comma"), (";", "semicolon"), ("\t", "tab"), (None, "whitespace")]
TEXT_EXTENSIONS = {".csv", ".txt", ".dat", ".tsv", ".tbl", ".mrt", ".md", ".readme", ""}


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


def text_lines(path: Path, limit: int | None = None) -> list[str]:
    lines: list[str] = []
    with path.open("r", encoding="utf-8", errors="replace") as handle:
        for index, line in enumerate(handle):
            if limit is not None and index >= limit:
                break
            lines.append(line.rstrip("\n\r"))
    return lines


def detect_table(path: Path) -> dict[str, object]:
    if path.suffix.lower() not in TEXT_EXTENSIONS:
        return {
            "read_status": "not_text_extension",
            "line_count_if_text": "",
            "detected_delimiter": "",
            "header_detected": "false",
            "header_columns": "",
            "column_count": "",
            "sample_rows": [],
        }
    try:
        lines_all = text_lines(path)
    except OSError as exc:
        return {
            "read_status": f"read_error:{exc}",
            "line_count_if_text": "",
            "detected_delimiter": "",
            "header_detected": "false",
            "header_columns": "",
            "column_count": "",
            "sample_rows": [],
        }
    nonempty = [line for line in lines_all if line.strip() and not line.lstrip().startswith("#")]
    if not nonempty:
        return {
            "read_status": "text_empty_or_comments_only",
            "line_count_if_text": len(lines_all),
            "detected_delimiter": "",
            "header_detected": "false",
            "header_columns": "",
            "column_count": "",
            "sample_rows": [],
        }
    if path.suffix.lower() == ".mrt":
        labels: list[str] = []
        data_rows: list[str] = []
        in_byte_section = False
        for line in lines_all:
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
                    data_rows.append(line.strip())
        return {
            "read_status": "readable_mrt_text",
            "line_count_if_text": len(lines_all),
            "detected_delimiter": "fixed_width_mrt",
            "header_detected": str(bool(labels)).lower(),
            "header_columns": ";".join(labels),
            "column_count": len(labels),
            "sample_rows": data_rows[:4],
        }
    header = nonempty[0].strip()
    best_columns: list[str] = []
    best_name = ""
    for delimiter, name in DELIMITERS:
        if delimiter is None:
            columns = re.split(r"\s+", header.strip())
        else:
            columns = [part.strip() for part in header.split(delimiter)]
        if len(columns) > len(best_columns):
            best_columns = columns
            best_name = name
    alpha_columns = sum(1 for column in best_columns if re.search(r"[A-Za-z]", column))
    header_detected = alpha_columns >= max(1, len(best_columns) // 2)
    return {
        "read_status": "readable_text",
        "line_count_if_text": len(lines_all),
        "detected_delimiter": best_name,
        "header_detected": str(header_detected).lower(),
        "header_columns": ";".join(best_columns) if header_detected else "",
        "column_count": len(best_columns),
        "sample_rows": nonempty[:4],
    }


def input_files() -> list[Path]:
    if not INPUT_DIR.exists():
        return []
    return sorted([path for path in INPUT_DIR.rglob("*") if path.is_file()], key=lambda item: str(item))


def source_references() -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for path in PRECONTRACT_CONTEXT:
        if not path.exists():
            rows.append(
                {
                    "source_id": f"SRC-{len(rows)+1:03d}",
                    "source_label": path.name,
                    "source_url_or_reference": str(path),
                    "source_type": "missing_repo_artifact",
                    "documented_in_artifact": str(path),
                    "retrieval_status": "not_available",
                    "retrieval_performed": "false",
                    "notes": "Expected context artifact missing.",
                }
            )
            continue
        rows.append(
            {
                "source_id": f"SRC-{len(rows)+1:03d}",
                "source_label": path.name,
                "source_url_or_reference": str(path),
                "source_type": "repo_context_artifact",
                "documented_in_artifact": str(path),
                "retrieval_status": "local_artifact_readable",
                "retrieval_performed": "false",
                "notes": "Used as local source/context input; no external retrieval.",
            }
        )
        if path.name == "17_source_url_inventory.csv":
            try:
                with path.open("r", encoding="utf-8", newline="") as handle:
                    for item in csv.DictReader(handle):
                        url = item.get("url", "")
                        if "SPARC" in url.upper() or "astroweb" in url.lower() or "1609.05917" in url:
                            rows.append(
                                {
                                    "source_id": f"SRC-{len(rows)+1:03d}",
                                    "source_label": "SPARC/RAR URL from Deep Research ingest",
                                    "source_url_or_reference": url,
                                    "source_type": "documented_external_url_not_retrieved",
                                    "documented_in_artifact": str(path),
                                    "retrieval_status": "not_retrieved",
                                    "retrieval_performed": "false",
                                    "notes": "Carried forward as source_reference only.",
                                }
                            )
            except OSError:
                pass
    return rows


def classify_feasibility(found_columns: set[str], file_count: int) -> tuple[str, str]:
    lower = {column.lower() for column in found_columns}
    if file_count == 0:
        return "pending_local_data", "pending_local_data"
    has_direct = bool({"gobs", "gbar"} <= lower or {"loggobs", "loggbar"} <= lower)
    has_radius = bool({"r", "rad", "radius"} & lower)
    has_vobs = "vobs" in lower
    has_baryonic_components = bool({"vgas", "vdisk", "vbul", "gbar", "mstar", "mgas", "sb disk", "sbdisk"} & lower)
    if has_direct:
        baseline = "feasible_from_present_columns"
    elif has_radius and has_vobs and has_baryonic_components:
        baseline = "partially_feasible_requires_derived_quantities"
    else:
        baseline = "blocked_missing_required_columns"
    if not has_radius:
        rbci = "blocked_missing_radius_or_ordering"
    elif has_baryonic_components:
        rbci = "partially_feasible_requires_component_derivation"
    else:
        rbci = "blocked_missing_baryonic_profile_columns"
    return baseline, rbci


def main() -> None:
    RUN_DIR.mkdir(parents=True, exist_ok=True)
    INPUT_DIR.mkdir(parents=True, exist_ok=True)
    write_text(RUN_DIR / "00_git_status_short_before.txt", run_command(["git", "status", "--short"]))
    write_text(RUN_DIR / "01_git_log_oneline_before.txt", run_command(["git", "--no-pager", "log", "--oneline", "-14"]))

    files = input_files()
    source_rows = source_references()
    scope = f"""# {RUN_ID}

## Purpose

Create a SPARC/RAR data contract: local file inventory, checksums, table/column profiling, source-reference registration, baseline feasibility, and RBCI_v1 formula feasibility. This is not a residual analysis run.

## Data Mode

Local input directory: `{INPUT_DIR}`

Local input file count: `{len(files)}`

## Execution Boundary

- No SPARC data downloaded.
- No external retrieval performed.
- No RAR fit computed.
- No residual analysis executed.
- `RBCI_v1` formula remains not finalized.

## Claim Boundary

{chr(10).join(f"- {item}" for item in CLAIM_BOUNDARY)}
"""
    write_text(RUN_DIR / "02_sparc_rar_data_contract_scope.md", scope)

    inventory_rows = []
    checksum_rows = []
    profile_rows = []
    detected_columns: set[str] = set()
    sample_rows = []
    for file_index, path in enumerate(files, start=1):
        rel = str(path)
        digest = sha256(path)
        profile = detect_table(path)
        inventory_rows.append(
            {
                "file_path": rel,
                "file_name": path.name,
                "file_size_bytes": path.stat().st_size,
                "sha256": digest,
                "extension": path.suffix.lower(),
                "line_count_if_text": profile["line_count_if_text"],
                "detected_delimiter": profile["detected_delimiter"],
                "header_detected": profile["header_detected"],
                "header_columns": profile["header_columns"],
                "read_status": profile["read_status"],
                "notes": "local input file; not modified",
            }
        )
        checksum_rows.append({"file_path": rel, "sha256": digest, "checksum_algorithm": "sha256", "lineage_role": "local_input_integrity"})
        profile_rows.append(
            {
                "file_path": rel,
                "read_status": profile["read_status"],
                "line_count_if_text": profile["line_count_if_text"],
                "detected_delimiter": profile["detected_delimiter"],
                "header_detected": profile["header_detected"],
                "column_count": profile["column_count"],
                "header_columns": profile["header_columns"],
                "notes": "defensive text-table profile; no scientific analysis",
            }
        )
        for column in str(profile["header_columns"]).split(";"):
            if column:
                detected_columns.add(column)
        for row_index, sample in enumerate(profile["sample_rows"], start=1):
            sample_rows.append({"file_id": file_index, "file_path": rel, "sample_row_index": row_index, "sample_text": sample[:500]})
    write_csv(
        RUN_DIR / "05_input_file_inventory.csv",
        ["file_path", "file_name", "file_size_bytes", "sha256", "extension", "line_count_if_text", "detected_delimiter", "header_detected", "header_columns", "read_status", "notes"],
        inventory_rows,
    )
    write_csv(RUN_DIR / "06_input_file_checksums.csv", ["file_path", "sha256", "checksum_algorithm", "lineage_role"], checksum_rows)
    write_csv(RUN_DIR / "07_text_table_profile.csv", ["file_path", "read_status", "line_count_if_text", "detected_delimiter", "header_detected", "column_count", "header_columns", "notes"], profile_rows)

    detected_rows = []
    for column in sorted(detected_columns, key=str.lower):
        matched_expected = next((expected for expected in EXPECTED_COLUMNS if expected.lower() == column.lower()), "")
        detected_rows.append(
            {
                "detected_column": column,
                "matched_expected_column": matched_expected,
                "sparc_relevance": "candidate_match" if matched_expected else "unknown",
                "presence_status": "present",
                "claim_boundary": "column_profile_only",
            }
        )
    write_csv(RUN_DIR / "08_detected_column_inventory.csv", ["detected_column", "matched_expected_column", "sparc_relevance", "presence_status", "claim_boundary"], detected_rows)

    mapping_rows = []
    lower_detected = {column.lower() for column in detected_columns}
    for expected in EXPECTED_COLUMNS:
        mapping_rows.append(
            {
                "expected_column_or_synonym": expected,
                "presence_status": "present" if expected.lower() in lower_detected else ("missing_from_local_input" if files else "not_yet_available"),
                "matched_detected_column": next((column for column in detected_columns if column.lower() == expected.lower()), ""),
                "role": "SPARC/RAR column search helper",
                "notes": "Presence is based only on local input headers.",
            }
        )
    write_csv(RUN_DIR / "09_sparc_expected_column_mapping.csv", ["expected_column_or_synonym", "presence_status", "matched_detected_column", "role", "notes"], mapping_rows)

    baseline_status, rbci_status = classify_feasibility(detected_columns, len(files))
    baseline_rows = [
        {
            "contract_item": "baseline_rar_feasibility_status",
            "status": baseline_status,
            "required_before_qsb_candidate": "true",
            "basis": "direct gobs/gbar columns, or Vobs plus baryonic components plus radius, if present",
            "computation_performed": "false",
            "failure_handling": "No QSB/RBCI interpretation if baseline cannot be reproduced.",
        }
    ]
    write_csv(RUN_DIR / "10_baseline_rar_feasibility_contract.csv", ["contract_item", "status", "required_before_qsb_candidate", "basis", "computation_performed", "failure_handling"], baseline_rows)

    rbci_rows = [
        {
            "observable_candidate_id": "RBCI_v1",
            "formula_feasibility_status": rbci_status,
            "formula_finalized": "false",
            "radius_or_ordering_present": str(bool({"r", "rad", "radius"} & {column.lower() for column in detected_columns})).lower(),
            "baryonic_profile_columns_present": str(bool({"vgas", "vdisk", "vbul", "gbar", "mstar", "mgas", "sbdisk", "sbbul"} & {column.lower() for column in detected_columns})).lower(),
            "units_to_freeze": "radius units; velocity/acceleration units; baryonic component definitions; normalization",
            "computation_performed": "false",
            "claim_boundary": "formula_feasibility_assessment_only",
        }
    ]
    write_csv(RUN_DIR / "11_rbci_v1_formula_feasibility_contract.csv", ["observable_candidate_id", "formula_feasibility_status", "formula_finalized", "radius_or_ordering_present", "baryonic_profile_columns_present", "units_to_freeze", "computation_performed", "claim_boundary"], rbci_rows)
    write_csv(RUN_DIR / "12_source_reference_inventory.csv", ["source_id", "source_label", "source_url_or_reference", "source_type", "documented_in_artifact", "retrieval_status", "retrieval_performed", "notes"], source_rows)

    lineage = f"""# Data Lineage Contract

Local input directory:

`{INPUT_DIR}`

Lineage requirements:

- every registered input file must have SHA256 recorded
- original downloaded/registered files must remain unmodified
- documentation/README/citation files must be stored with data files
- normalized or derived files must be created only in later run output locations
- no residual analysis before data contract is frozen
- source references may be carried from repo artifacts, but external retrieval is not performed in this run
"""
    write_text(RUN_DIR / "13_data_lineage_contract.md", lineage)

    unit_note = """# Unit and Dimension Review Placeholder

No units are frozen in this run unless local files explicitly provide parseable headers/documentation.

To freeze in a later review:

- radius coordinate and unit
- observed velocity or acceleration unit
- baryonic component velocity/mass/acceleration definitions
- distance/inclination correction status
- log versus linear acceleration columns
- uncertainty columns and weighting policy
- RBCI_v1 normalization

No scientific interpretation is allowed before these contracts are frozen.
"""
    write_text(RUN_DIR / "14_unit_and_dimension_review_placeholder.md", unit_note)

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

    next_id = "QSB-SPARC-RAR-RESIDUAL-SCOUT-01-DATA-REGISTRATION" if not files else "QSB-SPARC-RAR-RESIDUAL-SCOUT-01-DATA-CONTRACT-REVIEW"
    next_contract = f"""# Next Execution Run Contract

Recommended next run:

`{next_id}`

If no local data are present:

- manually register official SPARC/RAR files under `{INPUT_DIR}`
- include documentation/README/citation files
- rerun this data-contract script or run a review pass

If local data are present:

- review column profiles and checksums
- freeze unit and formula feasibility contracts
- do not run baseline RAR reproduction until data contract is frozen
"""
    write_text(RUN_DIR / "16_next_execution_run_contract.md", next_contract)

    review = f"""# {RUN_ID}

## Local Data

Local SPARC input files found: `{len(files)}`.

## Inventory and Checksums

Input files were inventoried and hashed when present. No local input files were modified.

## Column Profile

Detected table file count: `{sum(1 for row in profile_rows if str(row['read_status']).startswith('readable_'))}`.

Detected column count: `{len(detected_columns)}`.

## Baseline RAR Feasibility

`{baseline_status}`

## RBCI_v1 Formula Feasibility

`{rbci_status}`

## Execution Boundary

No data were downloaded. No residual analysis, RAR fit, or RBCI_v1 computation was executed. No QSB detection or physics claim is made.

## Tooling Note

DWH/CSV/scoring-style outputs are audit tools, not the project goal.
"""
    write_text(RUN_DIR / "17_sparc_rar_data_contract_review_note.md", review)

    manual = f"""# Manual Data Registration Instructions

1. Place official SPARC/RAR data manually in:

   `{INPUT_DIR}`

2. Do not edit data files.

3. Place documentation/README/citation files in the same input directory.

4. Rerun this data-contract script or create a review run.

5. Do not execute residual analysis before the frozen data contract exists.

Documented source references are listed in `12_source_reference_inventory.csv`; they are not automatically verified by this run.
"""
    write_text(RUN_DIR / "18_manual_data_registration_instructions.md", manual)

    missing_report = f"""# Missing Data Report

Local input file count: `{len(files)}`.

Status: `{'pending_local_data' if not files else 'local_data_present'}`

Expected data classes:

1. galaxy-level metadata
2. rotation curve point table
3. baryonic component velocity/mass model table
4. RAR point table or derived relation table, if present
5. fit/result table, if present
6. documentation/readme files
"""
    write_text(RUN_DIR / "19_missing_data_report.md", missing_report)

    write_text(RUN_DIR / "20_download_not_performed_note.md", "# Download Not Performed Note\n\nNo external download or retrieval was performed in this run.\n")
    write_text(RUN_DIR / "21_next_codex_prompt_recommendation.md", f"# Next Codex Prompt Recommendation\n\nRecommended next run: `{next_id}`\n\nDo not run residual analysis before local data registration and data-contract review are complete.\n")

    if files:
        write_csv(RUN_DIR / "22_sample_rows_preview.csv", ["file_id", "file_path", "sample_row_index", "sample_text"], sample_rows)
        presence_rows = [
            {"expected_column_or_synonym": row["expected_column_or_synonym"], "presence_status": row["presence_status"], "matched_detected_column": row["matched_detected_column"]}
            for row in mapping_rows
        ]
        write_csv(RUN_DIR / "23_column_presence_matrix.csv", ["expected_column_or_synonym", "presence_status", "matched_detected_column"], presence_rows)
        quality_rows = [
            {"quality_item": "local_input_files_present", "status": "pass", "observed": len(files), "notes": "Presence only; no science analysis."},
            {"quality_item": "readable_text_tables", "status": "review", "observed": sum(1 for row in profile_rows if str(row["read_status"]).startswith("readable_")), "notes": "Manual review required."},
            {"quality_item": "baseline_columns", "status": baseline_status, "observed": ";".join(sorted(detected_columns)), "notes": "Feasibility only."},
        ]
        write_csv(RUN_DIR / "24_data_quality_preflight.csv", ["quality_item", "status", "observed", "notes"], quality_rows)

    status = "sparc_rar_data_contract_pending_local_data" if not files else ("sparc_rar_data_contract_completed_with_local_data" if baseline_status != "blocked_missing_required_columns" else "sparc_rar_data_contract_completed_with_partial_local_data")
    summary = {
        "baseline_rar_computed": False,
        "baseline_rar_feasibility_status": baseline_status,
        "checksum_file_count": len(checksum_rows),
        "claim_boundary": CLAIM_BOUNDARY,
        "data_contract_frozen": False,
        "detected_column_count": len(detected_columns),
        "detected_table_file_count": sum(1 for row in profile_rows if str(row["read_status"]).startswith("readable_")),
        "local_input_directory": str(INPUT_DIR),
        "local_input_file_count": len(files),
        "notes": "No local SPARC input files found; pending manual data registration." if not files else "Local input files profiled defensively; no residual analysis performed.",
        "observable_formula_finalized": False,
        "rbci_v1_formula_feasibility_status": rbci_status,
        "recommended_next_run_id": next_id,
        "residual_analysis_executed": False,
        "retrieval_performed": False,
        "run_id": RUN_ID,
        "source_reference_count": len(source_rows),
        "sparc_data_downloaded": False,
        "status": status,
    }
    write_text(RUN_DIR / "04_sparc_rar_data_contract_summary.json", json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True) + "\n")
    print(json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
