#!/usr/bin/env python3
"""SHAPIROMART13 ELL1 geometric phase mapping."""

from __future__ import annotations

import argparse
import ast
import csv
import hashlib
import json
import math
import statistics
from pathlib import Path


RESEARCH_BLOCK = "QSB-SHAPIROMART13"
EXPECTED_ROW_COUNT = 7419
EXPECTED_OUTPUTS = [
    "shapiromart13_readout.md",
    "shapiromart13_summary.json",
    "shapiromart13_evidence_assessment.csv",
    "shapiromart13_geometric_reference_points.csv",
    "shapiromart13_phase_geometry_mapping.csv",
    "shapiromart13_phase_distance_qc.csv",
    "shapiromart13_context_phase_distance_summary.csv",
    "shapiromart13_final_status.csv",
]

EVIDENCE_NOTE_KEYS = {
    "evidence_id": "ELL1_GEOMETRIC_PHASE_MAPPING",
    "model": "ELL1",
    "phase_origin": "TASC",
    "phase_origin_semantics": "ascending_node_epoch",
    "superior_conjunction_phase": "0.25",
    "mapping_status": "supported",
    "mapping_type": "documented_model_inference",
    "applies_to_phase_axis": "SHAPIROMART11",
}

MANIFEST_FIELDS = [
    "evidence_source_id",
    "source_title",
    "source_type",
    "source_organization_or_journal",
    "source_url",
    "retrieval_timestamp_utc",
    "local_path",
    "file_size_bytes",
    "sha256",
    "supports_tasc_ascending_node",
    "supports_ell1_phase_definition",
    "supports_shapiro_sin_phi_form",
    "supports_superior_conjunction_phase_025",
    "applies_to_j0740",
    "evidence_status",
    "notes",
]

FINAL_STATUS_FIELDS = [
    "research_block",
    "ell1_phase_axis_available",
    "phase_origin_tasc_supported",
    "ascending_node_phase",
    "superior_conjunction_mapping_supported",
    "superior_conjunction_phase",
    "geometric_phase_distance_generated",
    "geometric_phase_distance_row_count",
    "exposure_classes_created",
    "shapiro_delay_calculated",
    "residual_analysis_performed",
    "model_fit_performed",
    "model_parameters_modified",
    "conjunction_measurement_claimed",
    "physical_distance_claimed",
    "database_access",
    "additional_gate_created",
    "final_status",
    "recommended_next_action",
    "limitations",
]

REFERENCE_POINTS = [
    {
        "reference_point_id": "ascending_node",
        "normalized_phase": 0.0,
        "angular_phase_radians": 0.0,
        "geometric_role": "ascending_node",
        "support_type": "direct",
        "evidence_source": "PINT_1_1_5_BINARY_ELL1_SOURCE",
        "interpretation_limit": "geometric_phase_coordinate_only",
        "notes": "Directly anchored by TASC semantics.",
    },
    {
        "reference_point_id": "superior_conjunction",
        "normalized_phase": 0.25,
        "angular_phase_radians": math.pi / 2.0,
        "geometric_role": "superior_conjunction",
        "support_type": "documented_model_inference",
        "evidence_source": "PINT_1_1_5_STANDALONE_ELL1_SOURCE;PINT_1_1_5_TIMING_MODEL_SOURCE",
        "interpretation_limit": "geometric_phase_coordinate_only",
        "notes": "Supported by the ELL1 sin(Phi) form and the PINT superior-conjunction criterion.",
    },
    {
        "reference_point_id": "descending_node",
        "normalized_phase": 0.5,
        "angular_phase_radians": math.pi,
        "geometric_role": "descending_node",
        "support_type": "symmetric_derived",
        "evidence_source": "ELL1_NORMALIZED_ORBIT_CONVENTION",
        "interpretation_limit": "derived_counterpoint_only",
        "notes": "Derived as the half-cycle node counterpart in the normalized ELL1 phase coordinate.",
    },
    {
        "reference_point_id": "inferior_conjunction",
        "normalized_phase": 0.75,
        "angular_phase_radians": 3.0 * math.pi / 2.0,
        "geometric_role": "inferior_conjunction",
        "support_type": "symmetric_derived",
        "evidence_source": "ELL1_NORMALIZED_ORBIT_CONVENTION",
        "interpretation_limit": "derived_counterpoint_only",
        "notes": "Derived as the half-cycle counterpart to superior conjunction.",
    },
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Map SHAPIROMART11 ELL1 phases to a cyclic coordinate around superior conjunction."
    )
    parser.add_argument("--phase-input", required=True, type=Path)
    parser.add_argument("--evidence-note", required=True, type=Path)
    parser.add_argument("--evidence-manifest", required=True, type=Path)
    parser.add_argument("--output-dir", required=True, type=Path)
    parser.add_argument(
        "--superior-conjunction-phase",
        type=float,
        default=0.25,
    )
    parser.add_argument("--overwrite", action="store_true")
    return parser.parse_args()


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: Path, fieldnames: list[str], rows: list[dict[str, object]]) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def write_json(path: Path, data: dict[str, object]) -> None:
    with path.open("w", encoding="utf-8") as handle:
        json.dump(data, handle, indent=2, sort_keys=True)
        handle.write("\n")


def fmt_float(value: float) -> str:
    return format(value, ".17g")


def read_final_status(path: Path) -> dict[str, str]:
    rows = read_csv(path)
    if len(rows) != 1:
        raise ValueError(f"Expected one final-status row in {path}")
    return rows[0]


def parse_note_keys(path: Path) -> dict[str, str]:
    values: dict[str, str] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        key = key.strip()
        if key in EVIDENCE_NOTE_KEYS:
            values[key] = value.strip()
    return values


def validate_evidence(note_path: Path, manifest_path: Path, phi_sc: float) -> dict[str, object]:
    if not note_path.exists():
        raise FileNotFoundError(note_path)
    if not manifest_path.exists():
        raise FileNotFoundError(manifest_path)
    if not math.isclose(phi_sc, 0.25, rel_tol=0.0, abs_tol=1e-15):
        raise ValueError("The superior-conjunction phase must be 0.25 for this evidence block.")

    note_values = parse_note_keys(note_path)
    missing_or_mismatched = {
        key: {"expected": expected, "observed": note_values.get(key, "")}
        for key, expected in EVIDENCE_NOTE_KEYS.items()
        if note_values.get(key, "") != expected
    }
    if missing_or_mismatched:
        raise ValueError(f"Evidence note key validation failed: {missing_or_mismatched}")

    with manifest_path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames != MANIFEST_FIELDS:
            raise ValueError(f"Unexpected evidence manifest fields: {reader.fieldnames}")
        manifest_rows = list(reader)
    if not manifest_rows:
        raise ValueError("Evidence manifest has no source rows.")

    supported = {
        "tasc": any(row["supports_tasc_ascending_node"] == "yes" for row in manifest_rows),
        "ell1_phase": any(
            row["supports_ell1_phase_definition"] in {"yes", "partial"}
            for row in manifest_rows
        ),
        "shapiro_sin_phi": any(
            row["supports_shapiro_sin_phi_form"] == "yes" for row in manifest_rows
        ),
        "superior_025": any(
            row["supports_superior_conjunction_phase_025"] in {"yes", "derived"}
            for row in manifest_rows
        ),
    }
    if not all(supported.values()):
        raise ValueError(f"Evidence support incomplete: {supported}")

    missing_local_files: list[str] = []
    for row in manifest_rows:
        local_path = Path(row["local_path"])
        if not local_path.exists():
            missing_local_files.append(row["local_path"])
            continue
        if str(local_path.stat().st_size) != row["file_size_bytes"]:
            raise ValueError(f"Evidence source size mismatch: {local_path}")
        digest = hashlib.sha256(local_path.read_bytes()).hexdigest()
        if digest != row["sha256"]:
            raise ValueError(f"Evidence source SHA-256 mismatch: {local_path}")
    if missing_local_files:
        raise FileNotFoundError(f"Missing archived evidence source(s): {missing_local_files}")

    return {
        "evidence_id": EVIDENCE_NOTE_KEYS["evidence_id"],
        "manifest_source_count": len(manifest_rows),
        "support": supported,
        "status": "supported",
        "main_gap": "No J0740-specific phase-0.25 publication figure was used in this block.",
    }


def cyclic_offset(phase: float, phi_sc: float) -> float:
    offset = ((phase - phi_sc + 0.5) % 1.0) - 0.5
    if offset >= 0.5:
        offset -= 1.0
    if offset < -0.5:
        offset += 1.0
    return offset


def nearest_reference_point(phase: float) -> str:
    best_name = ""
    best_distance = float("inf")
    for point in REFERENCE_POINTS:
        ref_phase = float(point["normalized_phase"])
        distance = abs(cyclic_offset(phase, ref_phase))
        if distance < best_distance:
            best_distance = distance
            best_name = str(point["reference_point_id"])
    return best_name


def load_phase_rows(path: Path) -> list[dict[str, str]]:
    rows = read_csv(path)
    required = {
        "source_row_index",
        "source_filename",
        "orbital_phase",
        "phase_method",
        "model_name",
        "tasc_value",
        "pb_value",
        "calculation_status",
    }
    missing = sorted(required - set(rows[0].keys())) if rows else sorted(required)
    if missing:
        raise ValueError(f"Phase input is missing required fields: {missing}")
    return rows


def context_name(row: dict[str, str]) -> str:
    try:
        parsed = ast.literal_eval(row.get("source_filename", ""))
    except (SyntaxError, ValueError):
        return "unparsed"
    if not isinstance(parsed, dict):
        return "unparsed"
    fe = parsed.get("fe", "")
    be = parsed.get("be", "")
    return f"{fe} / {be}" if fe and be else "unparsed"


def summarize_context(name: str, rows: list[dict[str, object]]) -> dict[str, object]:
    if not rows:
        return {
            "context_name": name,
            "toa_count": 0,
            "minimum_absolute_phase_distance": "",
            "median_absolute_phase_distance": "",
            "mean_absolute_phase_distance": "",
            "maximum_absolute_phase_distance": "",
            "minimum_signed_phase_offset": "",
            "maximum_signed_phase_offset": "",
            "exact_conjunction_count": 0,
            "mapping_status": "missing",
            "notes": "No rows found for this context.",
        }

    distances = [float(row["absolute_phase_distance"]) for row in rows]
    offsets = [float(row["signed_phase_offset"]) for row in rows]
    exact_count = sum(1 for offset in offsets if offset == 0.0)
    return {
        "context_name": name,
        "toa_count": len(rows),
        "minimum_absolute_phase_distance": fmt_float(min(distances)),
        "median_absolute_phase_distance": fmt_float(statistics.median(distances)),
        "mean_absolute_phase_distance": fmt_float(statistics.fmean(distances)),
        "maximum_absolute_phase_distance": fmt_float(max(distances)),
        "minimum_signed_phase_offset": fmt_float(min(offsets)),
        "maximum_signed_phase_offset": fmt_float(max(offsets)),
        "exact_conjunction_count": exact_count,
        "mapping_status": "mapped",
        "notes": "Continuous phase-coordinate summary; no class labels assigned.",
    }


def validate_inputs(phase_rows: list[dict[str, str]], phase_input: Path) -> dict[str, str]:
    shapiromart11_dir = phase_input.parent
    shapiromart11_final = read_final_status(shapiromart11_dir / "shapiromart11_final_status.csv")
    shapiromart12_final = read_final_status(
        Path("runs/QSB-SHAPIROMART/SHAPIROMART12_ORBITAL_PHASE_AXIS_QC")
        / "shapiromart12_final_status.csv"
    )
    with (shapiromart11_dir / "shapiromart11_summary.json").open(encoding="utf-8") as handle:
        shapiromart11_summary = json.load(handle)

    checks = {
        "shapiromart11_final_status": shapiromart11_final.get("final_status", ""),
        "shapiromart11_ell1_model_confirmed": shapiromart11_final.get(
            "ell1_model_confirmed", ""
        ),
        "shapiromart11_tasc_available": shapiromart11_final.get("tasc_available", ""),
        "shapiromart11_pb_available": shapiromart11_final.get("pb_available", ""),
        "shapiromart11_phase_exported": shapiromart11_final.get(
            "orbital_phase_exported", ""
        ),
        "shapiromart12_phase_axis_quality_status": shapiromart12_final.get(
            "phase_axis_quality_status", ""
        ),
        "shapiromart12_observed_row_count": shapiromart12_final.get(
            "observed_row_count", ""
        ),
        "shapiromart11_phase_zero_definition": shapiromart11_summary.get(
            "orbital_phase_assessment", {}
        ).get("phase_zero_definition", ""),
    }
    required_pairs = {
        "shapiromart11_final_status": "orbital_phase_axis_reconstructed",
        "shapiromart11_ell1_model_confirmed": "yes",
        "shapiromart11_tasc_available": "yes",
        "shapiromart11_pb_available": "yes",
        "shapiromart11_phase_exported": "yes",
        "shapiromart12_phase_axis_quality_status": "qc_passed_with_coverage_anomalies",
        "shapiromart12_observed_row_count": str(EXPECTED_ROW_COUNT),
    }
    failed = {
        key: {"expected": expected, "observed": checks.get(key, "")}
        for key, expected in required_pairs.items()
        if checks.get(key, "") != expected
    }
    if failed:
        raise ValueError(f"Input status validation failed: {failed}")
    if len(phase_rows) != EXPECTED_ROW_COUNT:
        raise ValueError(f"Expected {EXPECTED_ROW_COUNT} phase rows, observed {len(phase_rows)}")
    return checks


def build_mapping_rows(
    phase_rows: list[dict[str, str]],
    phi_sc: float,
) -> list[dict[str, object]]:
    mapping_rows: list[dict[str, object]] = []
    for row in phase_rows:
        phase = float(row["orbital_phase"])
        if not math.isfinite(phase) or not (0.0 <= phase < 1.0):
            raise ValueError(f"Invalid orbital phase at source_row_index={row['source_row_index']}")
        offset = cyclic_offset(phase, phi_sc)
        distance = abs(offset)
        mapping_rows.append(
            {
                "source_row_index": row["source_row_index"],
                "orbital_phase": fmt_float(phase),
                "phase_origin": "TASC",
                "phase_origin_role": "ascending_node_epoch",
                "superior_conjunction_phase": fmt_float(phi_sc),
                "signed_phase_offset": fmt_float(offset),
                "absolute_phase_distance": fmt_float(distance),
                "nearest_reference_point": nearest_reference_point(phase),
                "phase_geometry_status": "mapped",
                "phase_method": row["phase_method"],
                "notes": "Continuous geometric phase coordinate; no class label assigned.",
                "_context_name": context_name(row),
            }
        )
    return mapping_rows


def build_qc_row(mapping_rows: list[dict[str, object]]) -> dict[str, object]:
    offsets = [float(row["signed_phase_offset"]) for row in mapping_rows]
    distances = [float(row["absolute_phase_distance"]) for row in mapping_rows]
    source_indices = [row["source_row_index"] for row in mapping_rows]
    synthetic_wrap_offsets = [
        cyclic_offset(0.0, 0.25),
        cyclic_offset(1.0 - 1e-12, 0.25),
        cyclic_offset(1e-12, 0.25),
        cyclic_offset(0.25, 0.25),
        cyclic_offset(0.75, 0.25),
    ]
    wrap_passed = all(-0.5 <= value < 0.5 for value in synthetic_wrap_offsets)
    finite_offsets = [value for value in offsets if math.isfinite(value)]
    finite_distances = [value for value in distances if math.isfinite(value)]
    in_range = all(-0.5 <= value < 0.5 for value in offsets) and all(
        0.0 <= value <= 0.5 for value in distances
    )
    valid_phase_count = len(mapping_rows)
    qc_status = (
        "phase_distance_qc_passed"
        if (
            len(mapping_rows) == EXPECTED_ROW_COUNT
            and len(finite_offsets) == EXPECTED_ROW_COUNT
            and len(finite_distances) == EXPECTED_ROW_COUNT
            and in_range
            and len(set(source_indices)) == len(source_indices)
            and wrap_passed
        )
        else "phase_distance_qc_failed"
    )
    return {
        "expected_row_count": EXPECTED_ROW_COUNT,
        "observed_row_count": len(mapping_rows),
        "valid_phase_count": valid_phase_count,
        "valid_signed_offset_count": len(finite_offsets),
        "valid_absolute_distance_count": len(finite_distances),
        "signed_offset_min": fmt_float(min(offsets)),
        "signed_offset_max": fmt_float(max(offsets)),
        "absolute_distance_min": fmt_float(min(distances)),
        "absolute_distance_max": fmt_float(max(distances)),
        "exact_conjunction_count": sum(1 for value in offsets if value == 0.0),
        "near_wrap_consistency_passed": "yes" if wrap_passed else "no",
        "all_values_finite": "yes"
        if len(finite_offsets) == len(offsets) and len(finite_distances) == len(distances)
        else "no",
        "all_values_in_range": "yes" if in_range else "no",
        "source_row_indices_unique": "yes"
        if len(set(source_indices)) == len(source_indices)
        else "no",
        "qc_status": qc_status,
        "notes": "Continuous cyclic coordinate only; no thresholds applied to mapped rows.",
    }


def strip_internal_columns(rows: list[dict[str, object]]) -> list[dict[str, object]]:
    return [{key: value for key, value in row.items() if not key.startswith("_")} for row in rows]


def build_readout(
    evidence: dict[str, object],
    input_checks: dict[str, str],
    qc_row: dict[str, object],
    context_rows: list[dict[str, object]],
) -> str:
    context_lines = [
        f"- {row['context_name']}: n={row['toa_count']}, "
        f"min_abs={row['minimum_absolute_phase_distance']}, "
        f"median_abs={row['median_absolute_phase_distance']}, "
        f"max_abs={row['maximum_absolute_phase_distance']}"
        for row in context_rows
    ]
    return "\n".join(
        [
            "# SHAPIROMART13 Readout",
            "",
            "## 1. Purpose",
            "Document the geometric meaning of the reconstructed ELL1 orbital-phase axis and compute a continuous cyclic phase distance to superior conjunction.",
            "",
            "## 2. Input Phase Axis",
            f"Input status: {input_checks['shapiromart11_final_status']}. Rows: {qc_row['observed_row_count']}.",
            "",
            "## 3. Evidence Basis",
            f"Evidence status: {evidence['status']}. Archived source count: {evidence['manifest_source_count']}.",
            "",
            "## 4. ELL1 Phase Origin",
            "The phase origin is TASC, interpreted as the ascending-node epoch.",
            "",
            "## 5. Superior-Conjunction Mapping",
            "The superior-conjunction reference phase is 0.25. This is a documented model inference from the ELL1 phase and PINT conjunction convention.",
            "",
            "## 6. Geometric Reference Points",
            "Reference points written: ascending_node, superior_conjunction, descending_node, inferior_conjunction.",
            "",
            "## 7. Cyclic Phase-Distance Definition",
            "signed_phase_offset = ((orbital_phase - 0.25 + 0.5) mod 1.0) - 0.5. absolute_phase_distance is the absolute value of that cyclic phase offset.",
            "",
            "## 8. Mapping Result",
            f"Mapped rows: {qc_row['observed_row_count']}. Signed-offset range: {qc_row['signed_offset_min']} to {qc_row['signed_offset_max']}.",
            "",
            "## 9. Quality Control",
            f"QC status: {qc_row['qc_status']}. All values finite: {qc_row['all_values_finite']}. All values in range: {qc_row['all_values_in_range']}.",
            "",
            "## 10. Context Summary",
            *context_lines,
            "",
            "## 11. What This Does Not Establish",
            "This block does not calculate a Shapiro delay, measure a residual, fit a model, alter model parameters, assign class labels, or claim a conjunction measurement.",
            "",
            "## 12. Recommended Next Action",
            "Use this continuous phase-coordinate mapping as an auditable input if a later block separately specifies a class policy or descriptive analysis.",
            "",
            "## 13. Limitations",
            str(evidence["main_gap"]),
            "",
        ]
    )


def main() -> int:
    args = parse_args()
    phase_input = args.phase_input
    evidence_note = args.evidence_note
    evidence_manifest = args.evidence_manifest
    output_dir = args.output_dir
    phi_sc = args.superior_conjunction_phase

    if output_dir.exists():
        existing = sorted(path.name for path in output_dir.iterdir() if path.is_file())
        unexpected = sorted(set(existing) - set(EXPECTED_OUTPUTS))
        if unexpected:
            raise ValueError(f"Unexpected existing files in output dir: {unexpected}")
        if existing and not args.overwrite:
            raise FileExistsError(
                f"Output dir already contains expected files; rerun with --overwrite: {output_dir}"
            )
    output_dir.mkdir(parents=True, exist_ok=True)

    evidence = validate_evidence(evidence_note, evidence_manifest, phi_sc)
    phase_rows = load_phase_rows(phase_input)
    input_checks = validate_inputs(phase_rows, phase_input)
    mapping_rows = build_mapping_rows(phase_rows, phi_sc)
    qc_row = build_qc_row(mapping_rows)

    if qc_row["qc_status"] != "phase_distance_qc_passed":
        raise ValueError(f"QC failed: {qc_row}")

    grouped: dict[str, list[dict[str, object]]] = {
        "overall": mapping_rows,
        "Rcvr_800 / GUPPI": [
            row for row in mapping_rows if row["_context_name"] == "Rcvr_800 / GUPPI"
        ],
        "Rcvr1_2 / GUPPI": [
            row for row in mapping_rows if row["_context_name"] == "Rcvr1_2 / GUPPI"
        ],
    }
    context_rows = [summarize_context(name, rows) for name, rows in grouped.items()]

    evidence_assessment = [
        {
            "evidence_id": "ELL1_GEOMETRIC_PHASE_MAPPING",
            "ell1_model_confirmed": "yes",
            "tasc_semantics_supported": "yes",
            "phase_origin_supported": "yes",
            "shapiro_phase_formula_supported": "yes",
            "superior_conjunction_phase_supported": "yes",
            "superior_conjunction_phase": fmt_float(phi_sc),
            "mapping_type": "documented_model_inference",
            "j0740_applicability": "applies_via_SHAPIROMART11_ELL1_model_confirmation",
            "evidence_status": "supported",
            "main_gap": evidence["main_gap"],
            "notes": "Local PINT evidence supports the ELL1 convention; no timing-delay or residual calculation was performed.",
        }
    ]

    reference_rows = [
        {
            **point,
            "normalized_phase": f"{float(point['normalized_phase']):.2f}",
            "angular_phase_radians": fmt_float(float(point["angular_phase_radians"])),
        }
        for point in REFERENCE_POINTS
    ]

    final_status = [
        {
            "research_block": RESEARCH_BLOCK,
            "ell1_phase_axis_available": "yes",
            "phase_origin_tasc_supported": "yes",
            "ascending_node_phase": "0.00",
            "superior_conjunction_mapping_supported": "yes",
            "superior_conjunction_phase": fmt_float(phi_sc),
            "geometric_phase_distance_generated": "yes",
            "geometric_phase_distance_row_count": len(mapping_rows),
            "exposure_classes_created": "no",
            "shapiro_delay_calculated": "no",
            "residual_analysis_performed": "no",
            "model_fit_performed": "no",
            "model_parameters_modified": "no",
            "conjunction_measurement_claimed": "no",
            "physical_distance_claimed": "no",
            "database_access": "none",
            "additional_gate_created": "no",
            "final_status": "ell1_geometric_phase_mapping_supported",
            "recommended_next_action": "Use the continuous phase-coordinate mapping only as an auditable input for any separately specified later analysis.",
            "limitations": evidence["main_gap"],
        }
    ]

    summary = {
        "research_block": RESEARCH_BLOCK,
        "phase_input": str(phase_input),
        "evidence_note": str(evidence_note),
        "evidence_manifest": str(evidence_manifest),
        "output_dir": str(output_dir),
        "evidence": evidence,
        "input_checks": input_checks,
        "reference_points": reference_rows,
        "qc": qc_row,
        "context_summary": context_rows,
        "boundaries": {
            "exposure_classes_created": "no",
            "shapiro_delay_calculated": "no",
            "residual_analysis_performed": "no",
            "model_fit_performed": "no",
            "model_parameters_modified": "no",
            "conjunction_measurement_claimed": "no",
            "physical_distance_claimed": "no",
            "database_access": "none",
            "additional_gate_created": "no",
        },
        "final_status": final_status[0],
    }

    readout = build_readout(evidence, input_checks, qc_row, context_rows)
    (output_dir / "shapiromart13_readout.md").write_text(readout, encoding="utf-8")
    write_json(output_dir / "shapiromart13_summary.json", summary)
    write_csv(
        output_dir / "shapiromart13_evidence_assessment.csv",
        [
            "evidence_id",
            "ell1_model_confirmed",
            "tasc_semantics_supported",
            "phase_origin_supported",
            "shapiro_phase_formula_supported",
            "superior_conjunction_phase_supported",
            "superior_conjunction_phase",
            "mapping_type",
            "j0740_applicability",
            "evidence_status",
            "main_gap",
            "notes",
        ],
        evidence_assessment,
    )
    write_csv(
        output_dir / "shapiromart13_geometric_reference_points.csv",
        [
            "reference_point_id",
            "normalized_phase",
            "angular_phase_radians",
            "geometric_role",
            "support_type",
            "evidence_source",
            "interpretation_limit",
            "notes",
        ],
        reference_rows,
    )
    write_csv(
        output_dir / "shapiromart13_phase_geometry_mapping.csv",
        [
            "source_row_index",
            "orbital_phase",
            "phase_origin",
            "phase_origin_role",
            "superior_conjunction_phase",
            "signed_phase_offset",
            "absolute_phase_distance",
            "nearest_reference_point",
            "phase_geometry_status",
            "phase_method",
            "notes",
        ],
        strip_internal_columns(mapping_rows),
    )
    write_csv(
        output_dir / "shapiromart13_phase_distance_qc.csv",
        [
            "expected_row_count",
            "observed_row_count",
            "valid_phase_count",
            "valid_signed_offset_count",
            "valid_absolute_distance_count",
            "signed_offset_min",
            "signed_offset_max",
            "absolute_distance_min",
            "absolute_distance_max",
            "exact_conjunction_count",
            "near_wrap_consistency_passed",
            "all_values_finite",
            "all_values_in_range",
            "source_row_indices_unique",
            "qc_status",
            "notes",
        ],
        [qc_row],
    )
    write_csv(
        output_dir / "shapiromart13_context_phase_distance_summary.csv",
        [
            "context_name",
            "toa_count",
            "minimum_absolute_phase_distance",
            "median_absolute_phase_distance",
            "mean_absolute_phase_distance",
            "maximum_absolute_phase_distance",
            "minimum_signed_phase_offset",
            "maximum_signed_phase_offset",
            "exact_conjunction_count",
            "mapping_status",
            "notes",
        ],
        context_rows,
    )
    write_csv(
        output_dir / "shapiromart13_final_status.csv",
        FINAL_STATUS_FIELDS,
        final_status,
    )

    actual_outputs = sorted(path.name for path in output_dir.iterdir() if path.is_file())
    if actual_outputs != sorted(EXPECTED_OUTPUTS):
        raise ValueError(f"Unexpected output set: {actual_outputs}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
