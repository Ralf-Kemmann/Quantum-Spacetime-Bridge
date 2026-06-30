#!/usr/bin/env python3
"""Parse SPARC/RAR MRT files and write baseline-only reproduction artifacts."""

from __future__ import annotations

import csv
import hashlib
import json
import math
import statistics
import subprocess
from pathlib import Path


RUN_ID = "QSB-SPARC-RAR-RESIDUAL-SCOUT-01-BASELINE-RAR-REPRODUCTION"
RUN_DIR = Path("runs") / RUN_ID
DATA_CONTRACT_DIR = Path("runs/QSB-SPARC-RAR-RESIDUAL-SCOUT-01-DATA-CONTRACT")
DATA_REVIEW_DIR = Path("runs/QSB-SPARC-RAR-RESIDUAL-SCOUT-01-DATA-CONTRACT-REVIEW")
INPUT_DIR = DATA_CONTRACT_DIR / "input"
MRT_FILES = [
    INPUT_DIR / "MassModels_Lelli2016c.mrt",
    INPUT_DIR / "RAR.mrt",
    INPUT_DIR / "RARbins.mrt",
    INPUT_DIR / "SPARC_Lelli2016c.mrt",
]
CLAIM_BOUNDARY = [
    "standard_rar_baseline_reproduction_only",
    "sparc_data_parser_and_profile",
    "checksum_revalidation",
    "unit_conversion_review",
    "no_qsb_detection_claim",
    "no_dark_matter_claim",
    "no_mond_claim",
    "no_lambdacdm_refutation_claim",
    "no_gravity_claim",
    "no_spacetime_claim",
    "no_causality_claim",
]
KPC_M = 3.0856775814913673e19
KM2_TO_M2 = 1_000_000.0
ACCEL_FACTOR = KM2_TO_M2 / KPC_M


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


def parse_mrt(path: Path) -> tuple[list[dict[str, str]], dict[str, object]]:
    lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
    columns: list[dict[str, object]] = []
    in_byte_section = False
    data_start = None
    for index, line in enumerate(lines):
        if "Bytes Format Units" in line and "Label" in line:
            in_byte_section = True
            continue
        if in_byte_section:
            parts = line.split()
            if len(parts) >= 5 and parts[0].endswith("-") and parts[1].isdigit():
                try:
                    start = int(parts[0].rstrip("-"))
                    end = int(parts[1])
                except ValueError:
                    continue
                columns.append({"start": start, "end": end, "format": parts[2], "units": parts[3], "label": parts[4]})
                continue
            if columns and line.startswith("-" * 8):
                data_start = index + 1
                break
    if data_start is None:
        for index, line in enumerate(lines):
            if columns and line.startswith("-" * 8):
                data_start = index + 1
        if data_start is None:
            data_start = 0
    rows = []
    parser_warnings = []
    for line in lines[data_start:]:
        if not line.strip():
            continue
        if line.startswith(("Note", "Title:", "Authors:", "Table:", "Byte-by-byte", "====", "----")):
            continue
        if not columns:
            continue
        row: dict[str, str] = {}
        fixed_ok = True
        for col in columns:
            value = line[int(col["start"]) - 1 : int(col["end"])].strip()
            if value == "" and len(line.split()) >= len(columns):
                fixed_ok = False
            row[str(col["label"])] = value
        if not fixed_ok:
            parts = line.split()
            if len(parts) >= len(columns):
                row = {str(col["label"]): parts[i] for i, col in enumerate(columns)}
                parser_warnings.append("fixed_width_fallback_to_whitespace")
        if any(row.values()):
            rows.append(row)
    meta = {
        "file_path": str(path),
        "label_count": len(columns),
        "labels": ";".join(str(col["label"]) for col in columns),
        "units": ";".join(f"{col['label']}={col['units']}" for col in columns),
        "row_count": len(rows),
        "parser_warnings": ";".join(sorted(set(parser_warnings))),
    }
    return rows, meta


def to_float(value: str) -> float | None:
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def stats(values: list[float]) -> dict[str, object]:
    if not values:
        return {"count": 0, "min": "", "median": "", "mean": "", "max": ""}
    return {
        "count": len(values),
        "min": min(values),
        "median": statistics.median(values),
        "mean": statistics.fmean(values),
        "max": max(values),
    }


def profile_table(name: str, rows: list[dict[str, str]], meta: dict[str, object]) -> list[dict[str, object]]:
    output = [
        {"field": "table_name", "value": name, "notes": "MRT table profile"},
        {"field": "row_count", "value": len(rows), "notes": "Parsed data rows"},
        {"field": "column_count", "value": meta["label_count"], "notes": "Parsed labels from byte-by-byte section"},
        {"field": "columns", "value": meta["labels"], "notes": "Header labels"},
        {"field": "units", "value": meta["units"], "notes": "Header units"},
        {"field": "parser_warnings", "value": meta["parser_warnings"], "notes": "Parser fallback warnings"},
    ]
    return output


def direct_rar_dataset(rows: list[dict[str, str]]) -> list[dict[str, object]]:
    output = []
    for index, row in enumerate(rows, start=1):
        log_gbar = to_float(row.get("gbar", ""))
        log_gobs = to_float(row.get("gobs", ""))
        e_gbar = to_float(row.get("e_gbar", ""))
        e_gobs = to_float(row.get("e_gobs", ""))
        output.append(
            {
                "row_id": index,
                "log10_gbar_m_per_s2": "" if log_gbar is None else log_gbar,
                "e_log10_gbar": "" if e_gbar is None else e_gbar,
                "log10_gobs_m_per_s2": "" if log_gobs is None else log_gobs,
                "e_log10_gobs": "" if e_gobs is None else e_gobs,
                "gbar_m_per_s2": "" if log_gbar is None else format(10**log_gbar, ".17g"),
                "gobs_m_per_s2": "" if log_gobs is None else format(10**log_gobs, ".17g"),
                "source_table": "RAR.mrt",
                "claim_boundary": "direct_standard_rar_table_only",
            }
        )
    return output


def massmodels_quantities(rows: list[dict[str, str]]) -> list[dict[str, object]]:
    output = []
    for index, row in enumerate(rows, start=1):
        radius = to_float(row.get("R", ""))
        vobs = to_float(row.get("Vobs", ""))
        vgas = to_float(row.get("Vgas", ""))
        vdisk = to_float(row.get("Vdisk", ""))
        vbul = to_float(row.get("Vbul", ""))
        gobs = None
        if radius is not None and radius > 0 and vobs is not None:
            gobs = (vobs * vobs / radius) * ACCEL_FACTOR
        vbar_ml1 = None
        if all(value is not None for value in [vgas, vdisk, vbul]):
            # Gas can be signed in SPARC mass models. Preserve sign convention in the squared contribution.
            vbar2 = vgas * abs(vgas) + vdisk * vdisk + vbul * vbul
            vbar_ml1 = math.sqrt(vbar2) if vbar2 >= 0 else None
        output.append(
            {
                "row_id": index,
                "galaxy_id": row.get("ID", ""),
                "radius_kpc": row.get("R", ""),
                "vobs_km_s": row.get("Vobs", ""),
                "vgas_km_s": row.get("Vgas", ""),
                "vdisk_km_s_ml1": row.get("Vdisk", ""),
                "vbul_km_s_ml1": row.get("Vbul", ""),
                "gobs_m_per_s2": "" if gobs is None else format(gobs, ".17g"),
                "log10_gobs": "" if gobs is None or gobs <= 0 else format(math.log10(gobs), ".17g"),
                "vbar_ml1_km_s_preparatory": "" if vbar_ml1 is None else format(vbar_ml1, ".17g"),
                "gbar_status": "requires_ml_assumption_not_finalized",
                "mass_to_light_assumption_required": "true",
                "claim_boundary": "massmodels_standard_baseline_preparation_only",
            }
        )
    return output


def main() -> None:
    RUN_DIR.mkdir(parents=True, exist_ok=True)
    write_text(RUN_DIR / "00_git_status_short_before.txt", run_command(["git", "status", "--short"]))
    write_text(RUN_DIR / "01_git_log_oneline_before.txt", run_command(["git", "--no-pager", "log", "--oneline", "-14"]))

    scope = f"""# {RUN_ID}

## Purpose

Parse the registered SPARC/RAR MRT input files and produce standard baseline-only profiles and readouts. This run does not evaluate RBCI_v1 or any QSB Zusatzobservable.

## Inputs

`{INPUT_DIR}`

## Execution Boundary

- no SPARC raw data modification
- no data download
- no RBCI_v1 evaluation
- no QSB observable evaluation
- no dark-matter, MOND, LambdaCDM, gravity, spacetime, or causality claim

## Claim Boundary

{chr(10).join(f"- {item}" for item in CLAIM_BOUNDARY)}
"""
    write_text(RUN_DIR / "02_baseline_rar_reproduction_scope.md", scope)

    contract_checksums = {row["file_path"]: row["sha256"] for row in read_csv(DATA_CONTRACT_DIR / "06_input_file_checksums.csv")}
    review_summary = read_json(DATA_REVIEW_DIR / "04_data_contract_review_summary.json")

    inventory_rows = []
    checksum_rows = []
    parsed: dict[str, tuple[list[dict[str, str]], dict[str, object]]] = {}
    checksum_match_count = 0
    checksum_mismatch_count = 0
    for path in MRT_FILES:
        exists = path.exists()
        digest = sha256(path) if exists else ""
        expected = contract_checksums.get(str(path), "")
        match = exists and digest == expected
        checksum_match_count += int(match)
        checksum_mismatch_count += int(exists and not match)
        inventory_rows.append(
            {
                "path": str(path),
                "exists": str(exists).lower(),
                "file_size_bytes": path.stat().st_size if exists else "",
                "sha256": digest,
                "source_role": "registered_sparc_rar_mrt_input",
                "raw_data_modified": "false",
            }
        )
        checksum_rows.append(
            {
                "file_path": str(path),
                "expected_sha256": expected,
                "actual_sha256": digest,
                "checksum_match": str(match).lower(),
                "status": "pass" if match else "fail",
            }
        )
        if exists:
            parsed[path.name] = parse_mrt(path)
    write_csv(RUN_DIR / "05_input_artifact_inventory.csv", ["path", "exists", "file_size_bytes", "sha256", "source_role", "raw_data_modified"], inventory_rows)
    write_csv(RUN_DIR / "06_checksum_revalidation.csv", ["file_path", "expected_sha256", "actual_sha256", "checksum_match", "status"], checksum_rows)

    parser_rows = []
    for name, (rows, meta) in sorted(parsed.items()):
        parser_rows.append(
            {
                "file_name": name,
                "parsed": "true",
                "row_count": len(rows),
                "label_count": meta["label_count"],
                "labels": meta["labels"],
                "units": meta["units"],
                "parser_warnings": meta["parser_warnings"],
            }
        )
    write_csv(RUN_DIR / "07_parser_report.csv", ["file_name", "parsed", "row_count", "label_count", "labels", "units", "parser_warnings"], parser_rows)

    table_targets = [
        ("RAR.mrt", "08_rar_table_profile.csv", "RAR"),
        ("RARbins.mrt", "09_rarbins_table_profile.csv", "RARbins"),
        ("MassModels_Lelli2016c.mrt", "10_massmodels_table_profile.csv", "MassModels"),
        ("SPARC_Lelli2016c.mrt", "11_sparc_sample_table_profile.csv", "SPARC_sample"),
    ]
    for filename, output_name, table_name in table_targets:
        rows, meta = parsed.get(filename, ([], {"label_count": 0, "labels": "", "units": "", "parser_warnings": ""}))
        write_csv(RUN_DIR / output_name, ["field", "value", "notes"], profile_table(table_name, rows, meta))

    mapping_rows = []
    for name, (rows, meta) in sorted(parsed.items()):
        for unit_item in str(meta["units"]).split(";"):
            if not unit_item:
                continue
            label, _, unit = unit_item.partition("=")
            mapping_rows.append(
                {
                    "source_file": name,
                    "column_label": label,
                    "unit": unit,
                    "used_for": "direct_RAR_baseline" if name == "RAR.mrt" and label in {"gbar", "gobs", "e_gbar", "e_gobs"} else "parser_profile_or_massmodels_preparation",
                    "claim_boundary": "standard_baseline_mapping_only",
                }
            )
    write_csv(RUN_DIR / "12_column_mapping_used.csv", ["source_file", "column_label", "unit", "used_for", "claim_boundary"], mapping_rows)

    unit_rows = [
        {"quantity": "direct_RAR_gbar_gobs", "source": "RAR.mrt", "input_unit": "[m/s2] log10 per MRT header", "conversion": "10**log10_value for linear diagnostic output", "performed": "true"},
        {"quantity": "massmodels_gobs", "source": "MassModels_Lelli2016c.mrt", "input_unit": "Vobs km/s; R kpc", "conversion": "g_obs = Vobs^2 / R * 1e6 / kpc_m", "performed": "true"},
        {"quantity": "massmodels_gbar", "source": "MassModels_Lelli2016c.mrt", "input_unit": "Vgas/Vdisk/Vbul km/s", "conversion": "not finalized because disk/bulge M/L assumption is required", "performed": "false"},
        {"quantity": "rbci_v1", "source": "not_applicable", "input_unit": "not_applicable", "conversion": "not evaluated in this run", "performed": "false"},
    ]
    write_csv(RUN_DIR / "13_unit_conversion_contract.csv", ["quantity", "source", "input_unit", "conversion", "performed"], unit_rows)

    rar_rows, _ = parsed.get("RAR.mrt", ([], {}))
    direct_rows = direct_rar_dataset(rar_rows)
    write_csv(
        RUN_DIR / "14_direct_rar_dataset.csv",
        ["row_id", "log10_gbar_m_per_s2", "e_log10_gbar", "log10_gobs_m_per_s2", "e_log10_gobs", "gbar_m_per_s2", "gobs_m_per_s2", "source_table", "claim_boundary"],
        direct_rows,
    )

    mass_rows, _ = parsed.get("MassModels_Lelli2016c.mrt", ([], {}))
    mass_quantity_rows = massmodels_quantities(mass_rows)
    write_csv(
        RUN_DIR / "15_massmodels_derived_baseline_quantities.csv",
        ["row_id", "galaxy_id", "radius_kpc", "vobs_km_s", "vgas_km_s", "vdisk_km_s_ml1", "vbul_km_s_ml1", "gobs_m_per_s2", "log10_gobs", "vbar_ml1_km_s_preparatory", "gbar_status", "mass_to_light_assumption_required", "claim_boundary"],
        mass_quantity_rows,
    )

    direct_log_gbar = [float(row["log10_gbar_m_per_s2"]) for row in direct_rows if row["log10_gbar_m_per_s2"] != ""]
    direct_log_gobs = [float(row["log10_gobs_m_per_s2"]) for row in direct_rows if row["log10_gobs_m_per_s2"] != ""]
    mass_log_gobs = [float(row["log10_gobs"]) for row in mass_quantity_rows if row["log10_gobs"] != ""]
    diag_rows = []
    for metric_name, values in [
        ("direct_log10_gbar", direct_log_gbar),
        ("direct_log10_gobs", direct_log_gobs),
        ("massmodels_log10_gobs", mass_log_gobs),
    ]:
        s = stats(values)
        diag_rows.append({"metric": metric_name, **s, "notes": "baseline distribution diagnostic only"})
    write_csv(RUN_DIR / "16_baseline_consistency_diagnostics.csv", ["metric", "count", "min", "median", "mean", "max", "notes"], diag_rows)

    reference_rows = [
        {
            "diagnostic_item": "standard_reference_curve_fit",
            "status": "not_performed",
            "value": "",
            "notes": "No RAR fit or reference-function residual analysis was performed in this baseline parser run.",
        },
        {
            "diagnostic_item": "direct_rar_table_profiled",
            "status": "completed",
            "value": len(direct_rows),
            "notes": "Direct RAR rows parsed and written.",
        },
        {
            "diagnostic_item": "massmodels_gobs_preparation",
            "status": "completed",
            "value": sum(1 for row in mass_quantity_rows if row["gobs_m_per_s2"] != ""),
            "notes": "Standard g_obs conversion from Vobs and R only.",
        },
        {
            "diagnostic_item": "massmodels_gbar_preparation",
            "status": "not_finalized",
            "value": "requires_ml_assumption",
            "notes": "No final MassModels g_bar is asserted.",
        },
    ]
    write_csv(RUN_DIR / "17_baseline_fit_or_reference_diagnostics.csv", ["diagnostic_item", "status", "value", "notes"], reference_rows)

    direct_parsed = len(direct_rows) > 0 and {"gbar", "gobs"} <= set(rar_rows[0].keys()) if rar_rows else False
    mass_parsed = len(mass_quantity_rows) > 0
    checksum_ok = checksum_mismatch_count == 0 and checksum_match_count == len(MRT_FILES)
    blockers = []
    if not checksum_ok:
        blockers.append("checksum_mismatch")
    if not direct_parsed:
        blockers.append("missing_direct_rar_columns")
    if not mass_parsed:
        blockers.append("massmodels_parser_failure")
    if not blockers:
        baseline_status = "direct_rar_table_reproduced"
        status = "sparc_rar_baseline_reproduction_completed"
        recommended_next = "QSB-SPARC-RAR-RESIDUAL-SCOUT-01-BASELINE-RAR-REVIEW"
    elif checksum_mismatch_count:
        baseline_status = "blocked_checksum_mismatch"
        status = "sparc_rar_baseline_reproduction_blocked"
        recommended_next = "QSB-SPARC-RAR-RESIDUAL-SCOUT-01-BASELINE-RAR-PARSER-PATCH"
    else:
        baseline_status = "completed_with_parser_warnings"
        status = "sparc_rar_baseline_reproduction_completed_with_warnings"
        recommended_next = "QSB-SPARC-RAR-RESIDUAL-SCOUT-01-BASELINE-RAR-PARSER-PATCH"

    readout_rows = [
        {"readout_item": "review_gate_input", "value": review_summary.get("data_contract_review_decision", ""), "notes": "Data-contract review decision."},
        {"readout_item": "direct_rar_rows_written", "value": len(direct_rows), "notes": "Rows in 14_direct_rar_dataset.csv."},
        {"readout_item": "massmodels_rows_written", "value": len(mass_quantity_rows), "notes": "Rows in 15_massmodels_derived_baseline_quantities.csv."},
        {"readout_item": "baseline_rar_reproduction_status", "value": baseline_status, "notes": "Baseline-only status; no RBCI/QSB evaluation."},
        {"readout_item": "recommended_next_run_id", "value": recommended_next, "notes": "Standard baseline review before any formula freeze."},
    ]
    write_csv(RUN_DIR / "18_baseline_reproduction_readout.csv", ["readout_item", "value", "notes"], readout_rows)

    blocker_rows = [
        {"blocker_id": f"B-{index:02d}", "blocker_type": blocker, "severity": "blocking", "description": blocker, "recommended_resolution": "Run parser/checksum patch before baseline review."}
        for index, blocker in enumerate(blockers, start=1)
    ] or [
        {"blocker_id": "none", "blocker_type": "none", "severity": "none", "description": "no blockers for baseline parser/profile scope", "recommended_resolution": "proceed to baseline RAR review"}
    ]
    write_csv(RUN_DIR / "19_baseline_blocker_report.csv", ["blocker_id", "blocker_type", "severity", "description", "recommended_resolution"], blocker_rows)

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
- Causality was reconstructed.
- The m1/m2 question was proven.
"""
    write_text(RUN_DIR / "20_claim_boundary_and_no_go.md", no_go)

    next_note = f"""# Next Run Recommendation

Recommended next run:

`{recommended_next}`

The next run should review the baseline parser/readout and declare whether the standard RAR baseline reproduction is acceptable. Do not evaluate `RBCI_v1` or any QSB Zusatzobservable before the baseline review passes.
"""
    write_text(RUN_DIR / "21_next_run_recommendation.md", next_note)

    review_note = f"""# {RUN_ID}

## Purpose

This run parses the registered SPARC/RAR MRT files and writes baseline-only data products.

## Results

- Direct RAR rows parsed: `{len(direct_rows)}`
- MassModels rows parsed: `{len(mass_quantity_rows)}`
- Checksum matches: `{checksum_match_count}`
- Checksum mismatches: `{checksum_mismatch_count}`
- Baseline status: `{baseline_status}`

## MassModels Boundary

`g_obs = Vobs^2 / R` was computed with kpc and km/s conversion. MassModels-derived final `g_bar` was not asserted because disk/bulge mass-to-light assumptions are required.

## Claim Boundary

No RBCI_v1 evaluation, no QSB observable, no QSB detection, no dark-matter, MOND, LambdaCDM, gravity, spacetime, or causality claim.
"""
    write_text(RUN_DIR / "22_baseline_rar_reproduction_review_note.md", review_note)

    comparison_rows = [
        {
            "comparison_item": "direct_RAR_vs_MassModels",
            "status": "not_matched_by_row",
            "notes": "Direct RAR table lacks galaxy/radius identifiers in parsed labels; no row-level comparison performed.",
            "claim_boundary": "baseline_parser_limitation_only",
        }
    ]
    write_csv(RUN_DIR / "25_massmodels_vs_direct_rar_comparison.csv", ["comparison_item", "status", "notes", "claim_boundary"], comparison_rows)
    edge_cases = """# Parser Edge Cases

- MRT byte ranges were parsed from byte-by-byte sections.
- Whitespace fallback is available when fixed-width slicing produces empty fields.
- Direct `RAR.mrt` rows do not include galaxy/radius identifiers in the parsed labels.
- MassModels-derived final `g_bar` requires mass-to-light assumptions and is not finalized here.
- Negative gas velocity contributions are preserved through `Vgas * abs(Vgas)` only for preparatory component handling.
"""
    write_text(RUN_DIR / "26_parser_edge_cases.md", edge_cases)
    prompt_note = """# Next Codex Prompt Recommendation

Recommended next run:

`QSB-SPARC-RAR-RESIDUAL-SCOUT-01-BASELINE-RAR-REVIEW`

Review the baseline-only parser outputs, row counts, checksum status, direct RAR profiles, and MassModels preparation. Do not introduce RBCI_v1 until the baseline review passes.
"""
    write_text(RUN_DIR / "27_next_codex_prompt_recommendation.md", prompt_note)

    summary = {
        "baseline_quantity_rows_written": len(direct_rows) + len(mass_quantity_rows),
        "baseline_rar_computed": bool(direct_rows or mass_quantity_rows),
        "baseline_rar_reproduction_status": baseline_status,
        "baseline_reference_residual_diagnostic_written": False,
        "checksum_match_count": checksum_match_count,
        "checksum_mismatch_count": checksum_mismatch_count,
        "claim_boundary": CLAIM_BOUNDARY,
        "direct_rar_row_count": len(direct_rows),
        "input_mrt_file_count": sum(1 for path in MRT_FILES if path.exists()),
        "mass_to_light_assumption_required": True,
        "massmodels_gbar_computed": False,
        "massmodels_gobs_computed": any(row["gobs_m_per_s2"] != "" for row in mass_quantity_rows),
        "massmodels_row_count": len(mass_quantity_rows),
        "massmodels_table_parsed": "MassModels_Lelli2016c.mrt" in parsed,
        "notes": "Baseline-only parser/readout. Direct RAR table preferred; MassModels final gbar not asserted because M/L assumptions are required.",
        "qsb_observable_evaluated": False,
        "rar_table_parsed": "RAR.mrt" in parsed,
        "rarbins_table_parsed": "RARbins.mrt" in parsed,
        "rbci_v1_evaluated": False,
        "recommended_next_run_id": recommended_next,
        "residual_analysis_executed": False,
        "run_id": RUN_ID,
        "sparc_sample_table_parsed": "SPARC_Lelli2016c.mrt" in parsed,
        "status": status,
        "unit_conversion_performed": any(row["gobs_m_per_s2"] != "" for row in mass_quantity_rows),
    }
    write_text(RUN_DIR / "04_baseline_rar_reproduction_summary.json", json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True) + "\n")
    print(json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
