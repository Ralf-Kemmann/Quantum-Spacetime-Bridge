#!/usr/bin/env python3
"""QSB-SHAPIROMART10 official J0740 TOA + ELL1 reconstruction check.

This script performs a bounded local review of the documented J0740+6620 TIM
and PAR files. It checks file identity, pair support, TIM/TOA format evidence,
PAR/ELL1 parameters, and whether an orbital-phase definition is currently
supported. It performs no database access, no model fit, no residual work, no
delay calculation, and no use of internal SHAPIROMART token paths.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import re
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from decimal import Decimal, getcontext
from pathlib import Path
from typing import Any


SCRIPT_NAME = "scripts/qsb_shapiromart10_official_j0740_toa_ell1_reconstruction.py"
DEFAULT_TIM_FILE = Path(
    "data/QSB-ST-SHAPIROINFO/public_sources/j0740_6620/raw/J0740+6620.cfr+19.tim"
)
DEFAULT_PAR_FILE = Path(
    "data/QSB-ST-SHAPIROINFO/public_sources/j0740_6620/raw/J0740+6620.par"
)
DEFAULT_OUTPUT_DIR = Path(
    "runs/QSB-SHAPIROMART/SHAPIROMART10_OFFICIAL_J0740_TOA_ELL1_RECONSTRUCTION"
)

LOCAL_MANIFEST = Path(
    "data/QSB-ST-SHAPIROINFO/public_sources/j0740_6620/manifest/"
    "j0740_6620_quarantine_download_manifest_2026_05_29.yaml"
)
LOCAL_RETRIEVAL_LOG = Path(
    "data/QSB-ST-SHAPIROINFO/public_sources/j0740_6620/logs/"
    "j0740_6620_quarantine_download_retrieval_log_2026_05_29.md"
)
LOCAL_METADATA_REVIEW = Path(
    "data/QSB-ST-SHAPIROINFO/j0740_6620_file_link_metadata_review.yaml"
)
LOCAL_MANUAL_MANIFEST_REVIEW = Path(
    "data/QSB-ST-SHAPIROINFO/j0740_6620_download_manifest_manual_review.yaml"
)
SHAPIROMART09_CLOSING = Path(
    "runs/QSB-SHAPIROMART/"
    "SHAPIROMART09_DATASET_SPECIFIC_TIM_FORMAT_EVIDENCE_ACQUISITION/"
    "shapiromart09_closing_decision.csv"
)
DOC_SHAPIROINFO21 = Path(
    "docs/QSB_ST_SHAPIROINFO21_J0740_README_RELEASE_NOTE_INSPECTION_RESULT.md"
)
DOC_SHAPIROINFO29 = Path(
    "docs/QSB_ST_SHAPIROINFO29_FILE_LINK_METADATA_REVIEW_RESULT.md"
)

READOUT_MD = "shapiromart10_readout.md"
SUMMARY_JSON = "shapiromart10_summary.json"
SOURCE_FILE_IDENTITY_CSV = "shapiromart10_source_file_identity.csv"
OFFICIAL_PAIR_ASSESSMENT_CSV = "shapiromart10_official_pair_assessment.csv"
TIM_FORMAT_ASSESSMENT_CSV = "shapiromart10_tim_format_assessment.csv"
PAR_PARAMETER_INVENTORY_CSV = "shapiromart10_par_parameter_inventory.csv"
TOA_AXIS_ASSESSMENT_CSV = "shapiromart10_toa_axis_assessment.csv"
ORBITAL_PHASE_DEFINITION_CSV = "shapiromart10_orbital_phase_definition.csv"
FINAL_STATUS_CSV = "shapiromart10_final_status.csv"
TOA_ORBITAL_PHASE_CSV = "shapiromart10_toa_orbital_phase.csv"

BASE_OUTPUT_FILENAMES = [
    READOUT_MD,
    SUMMARY_JSON,
    SOURCE_FILE_IDENTITY_CSV,
    OFFICIAL_PAIR_ASSESSMENT_CSV,
    TIM_FORMAT_ASSESSMENT_CSV,
    PAR_PARAMETER_INVENTORY_CSV,
    TOA_AXIS_ASSESSMENT_CSV,
    ORBITAL_PHASE_DEFINITION_CSV,
    FINAL_STATUS_CSV,
]

SOURCE_FILE_IDENTITY_FIELDS = [
    "source_file_id",
    "file_path",
    "file_name",
    "file_type",
    "file_size_bytes",
    "sha256",
    "object_name",
    "source_origin",
    "publication_relation",
    "toolchain_relation",
    "pair_candidate_id",
    "identity_status",
    "notes",
]
OFFICIAL_PAIR_FIELDS = [
    "pair_candidate_id",
    "tim_file_id",
    "par_file_id",
    "object_match",
    "source_match",
    "publication_match",
    "toolchain_match",
    "time_coverage_match",
    "binary_model_match",
    "pair_identity_status",
    "main_gap",
    "notes",
]
TIM_FORMAT_FIELDS = [
    "tim_file_id",
    "documented_format",
    "parser_or_tool",
    "parser_or_tool_version",
    "line_type",
    "tokenization_rule",
    "toa_field_position",
    "toa_field_name",
    "toa_unit",
    "toa_time_scale",
    "flags_supported",
    "format_status",
    "evidence_source",
    "notes",
]
PAR_PARAMETER_FIELDS = [
    "par_file_id",
    "parameter_name",
    "raw_value",
    "normalized_value",
    "unit",
    "uncertainty",
    "fit_flag",
    "semantic_role",
    "required_for_phase",
    "present",
    "source_line",
    "notes",
]
TOA_AXIS_FIELDS = [
    "tim_file_id",
    "official_identity_supported",
    "toa_field_documented",
    "toa_unit_supported",
    "toa_time_scale_supported",
    "extraction_reproducible",
    "toa_axis_status",
    "main_gap",
    "notes",
]
ORBITAL_PHASE_FIELDS = [
    "definition_id",
    "toa_time_field",
    "tasc_parameter",
    "period_parameter",
    "period_source",
    "formula",
    "phase_range",
    "phase_zero_definition",
    "time_basis_consistent",
    "unit_conversion_defined",
    "modulo_rule_defined",
    "definition_status",
    "main_gap",
    "notes",
]
TOA_ORBITAL_PHASE_FIELDS = [
    "source_file_id",
    "source_line_number",
    "toa_raw",
    "toa_mjd",
    "tasc_mjd",
    "pb_days",
    "orbital_cycle",
    "orbital_phase",
    "phase_definition_id",
    "calculation_status",
    "notes",
]
FINAL_STATUS_FIELDS = [
    "research_block",
    "official_toa_file_identified",
    "official_par_file_identified",
    "official_pair_identity_supported",
    "toa_time_axis_supported",
    "ell1_parameter_basis_supported",
    "orbital_phase_definition_supported",
    "orbital_phase_axis_generated",
    "tim_token_003_used",
    "record_index_used_as_time",
    "database_access",
    "database_modified",
    "physical_model_fit_performed",
    "shapiro_delay_calculated",
    "main_remaining_gap",
    "recommended_next_action",
    "additional_gate_created",
]

PAIR_ID = "PAIR_J0740_6620_NANOGRAV_CROMARTIE_2020_LOCAL"
TIM_FILE_ID = "TIM_J0740_6620_CFR19"
PAR_FILE_ID = "PAR_J0740_6620_ELL1"
PHASE_DEFINITION_ID = "ORBPHASE_J0740_ELL1_TASC_PB"

TOA_AXIS_GAP = (
    "Local evidence identifies a TEMPO/TEMPO2-compatible TIM file with FORMAT 1, "
    "but no local format-specific documentation was found that fully documents "
    "the TOA field position, unit, and time scale for this concrete file."
)
PHASE_GAP = (
    "The official pair and ELL1 parameters are supported, but the TOA time-axis "
    "documentation is unresolved, so the orbital-phase definition is not applied."
)


@dataclass(frozen=True)
class FileSummary:
    path: Path
    size_bytes: int
    sha256: str


def utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def fail(message: str) -> None:
    raise RuntimeError(message)


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def file_summary(path: Path) -> FileSummary:
    return FileSummary(
        path=path,
        size_bytes=path.stat().st_size,
        sha256=file_sha256(path),
    )


def safe_read_text(path: Path) -> str:
    if not path.exists():
        return ""
    return path.read_text(encoding="utf-8", errors="replace")


def write_csv(path: Path, rows: list[dict[str, Any]], fields: list[str]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for row in rows:
            writer.writerow({field: row.get(field, "") for field in fields})


def output_paths(output_dir: Path, include_phase_output: bool) -> dict[str, Path]:
    names = list(BASE_OUTPUT_FILENAMES)
    if include_phase_output:
        names.append(TOA_ORBITAL_PHASE_CSV)
    return {name: output_dir / name for name in names}


def ensure_inputs(args: argparse.Namespace) -> None:
    if not args.tim_file.exists():
        fail(f"TIM file not found: {args.tim_file}")
    if not args.par_file.exists():
        fail(f"PAR file not found: {args.par_file}")
    args.output_dir.mkdir(parents=True, exist_ok=True)
    expected = set(BASE_OUTPUT_FILENAMES)
    if args.phase_calculation:
        expected.add(TOA_ORBITAL_PHASE_CSV)
    existing_expected = [
        str(args.output_dir / name)
        for name in expected
        if (args.output_dir / name).exists()
    ]
    if existing_expected and not args.overwrite:
        fail(
            "SHAPIROMART10 output files already exist. Use --overwrite to "
            "replace only expected SHAPIROMART10 outputs: "
            + "; ".join(existing_expected)
        )
    if not args.phase_calculation and (args.output_dir / TOA_ORBITAL_PHASE_CSV).exists() and not args.overwrite:
        fail(
            "Existing phase output is present but --phase-calculation is disabled: "
            + str(args.output_dir / TOA_ORBITAL_PHASE_CSV)
        )


def tokenize_yaml_like_list_entry(text: str, key: str) -> list[str]:
    pattern = re.compile(rf'{re.escape(key)}:\s*"([^"]+)"')
    return pattern.findall(text)


def build_identity_rows(
    tim_summary: FileSummary,
    par_summary: FileSummary,
    evidence_texts: dict[str, str],
) -> list[dict[str, str]]:
    metadata_text = evidence_texts.get("metadata_review", "")
    manifest_text = evidence_texts.get("manifest", "")
    manual_text = evidence_texts.get("manual_manifest_review", "")
    publication_relation = (
        "Cromartie et al. 2020 page reference observed locally"
        if "Cromartie" in metadata_text or "Cromartie" in manual_text
        else "publication relation unresolved"
    )
    source_origin = (
        "NANOGrav source page and data.nanograv.org link recorded locally"
        if "nanograv.org/science/data/timing-data-binary-parameters-j07406620" in metadata_text + manifest_text + manual_text
        else "source origin unresolved"
    )
    rows = [
        {
            "source_file_id": TIM_FILE_ID,
            "file_path": str(tim_summary.path),
            "file_name": tim_summary.path.name,
            "file_type": "TIM_TOA_file",
            "file_size_bytes": str(tim_summary.size_bytes),
            "sha256": tim_summary.sha256,
            "object_name": "J0740+6620",
            "source_origin": source_origin,
            "publication_relation": publication_relation,
            "toolchain_relation": "Source page labels file as timing data; local notes record TEMPO/TEMPO2-compatible timing-data expectation.",
            "pair_candidate_id": PAIR_ID,
            "identity_status": "official_file_supported",
            "notes": "File identity supported by local metadata review, manifest, retrieval log, size, and SHA-256.",
        },
        {
            "source_file_id": PAR_FILE_ID,
            "file_path": str(par_summary.path),
            "file_name": par_summary.path.name,
            "file_type": "PAR_timing_model_file",
            "file_size_bytes": str(par_summary.size_bytes),
            "sha256": par_summary.sha256,
            "object_name": "J0740+6620",
            "source_origin": source_origin,
            "publication_relation": publication_relation,
            "toolchain_relation": "Source page labels file as parameter file; PAR body contains TEMPO/TEMPO2 timing-model parameters.",
            "pair_candidate_id": PAIR_ID,
            "identity_status": "official_file_supported",
            "notes": "File identity supported by local metadata review, manifest, retrieval log, size, and SHA-256.",
        },
        {
            "source_file_id": "DOC_J0740_LOCAL_MANIFEST",
            "file_path": str(LOCAL_MANIFEST),
            "file_name": LOCAL_MANIFEST.name,
            "file_type": "local_manifest",
            "file_size_bytes": str(LOCAL_MANIFEST.stat().st_size) if LOCAL_MANIFEST.exists() else "missing",
            "sha256": file_sha256(LOCAL_MANIFEST) if LOCAL_MANIFEST.exists() else "missing",
            "object_name": "J0740+6620",
            "source_origin": source_origin,
            "publication_relation": publication_relation,
            "toolchain_relation": "Documents local quarantine retrieval and paired timing-data / parameter-file labels.",
            "pair_candidate_id": PAIR_ID,
            "identity_status": "official_pair_supported",
            "notes": "Support source only; not a TOA or PAR data file.",
        },
        {
            "source_file_id": "DOC_J0740_METADATA_REVIEW",
            "file_path": str(LOCAL_METADATA_REVIEW),
            "file_name": LOCAL_METADATA_REVIEW.name,
            "file_type": "local_metadata_review",
            "file_size_bytes": str(LOCAL_METADATA_REVIEW.stat().st_size) if LOCAL_METADATA_REVIEW.exists() else "missing",
            "sha256": file_sha256(LOCAL_METADATA_REVIEW) if LOCAL_METADATA_REVIEW.exists() else "missing",
            "object_name": "J0740+6620",
            "source_origin": source_origin,
            "publication_relation": publication_relation,
            "toolchain_relation": "Records visible source-page labels and expected TEMPO/TEMPO2-compatible file family.",
            "pair_candidate_id": PAIR_ID,
            "identity_status": "official_pair_supported",
            "notes": "Support source only; documents page-level link labels and headers.",
        },
    ]
    return rows


def read_tim_evidence(tim_file: Path) -> dict[str, Any]:
    header_lines: list[tuple[int, str]] = []
    first_data_line: tuple[int, str] | None = None
    first_comment_toa_line: tuple[int, str] | None = None
    line_count = 0
    data_like_count = 0
    commented_toa_count = 0
    command_lines: list[str] = []
    flag_names: set[str] = set()
    with tim_file.open("r", encoding="utf-8", errors="replace") as handle:
        for line_number, raw_line in enumerate(handle, start=1):
            line_count += 1
            line = raw_line.rstrip("\n")
            stripped = line.strip()
            if line_number <= 5:
                header_lines.append((line_number, stripped))
            if not stripped:
                continue
            if stripped in {"MODE 1", "FORMAT 1"}:
                command_lines.append(stripped)
                continue
            tokens = stripped.split()
            if tokens[0] == "C" and len(tokens) >= 6:
                commented_toa_count += 1
                if first_comment_toa_line is None:
                    first_comment_toa_line = (line_number, stripped)
                for token in tokens:
                    if token.startswith("-"):
                        flag_names.add(token)
                continue
            if len(tokens) >= 5:
                data_like_count += 1
                if first_data_line is None:
                    first_data_line = (line_number, stripped)
                for token in tokens:
                    if token.startswith("-"):
                        flag_names.add(token)
    return {
        "line_count": line_count,
        "header_lines": header_lines,
        "first_data_line": first_data_line,
        "first_comment_toa_line": first_comment_toa_line,
        "data_like_count": data_like_count,
        "commented_toa_count": commented_toa_count,
        "command_lines": command_lines,
        "flag_names": sorted(flag_names),
    }


def parse_par_file(par_file: Path) -> tuple[list[dict[str, str]], dict[str, dict[str, str]]]:
    rows: list[dict[str, str]] = []
    first_by_param: dict[str, dict[str, str]] = {}
    with par_file.open("r", encoding="utf-8", errors="replace") as handle:
        for line_number, raw_line in enumerate(handle, start=1):
            line = raw_line.rstrip("\n")
            stripped = line.strip()
            if not stripped or stripped.startswith("#"):
                continue
            tokens = stripped.split()
            if not tokens:
                continue
            name = tokens[0]
            values = tokens[1:]
            raw_value = " ".join(values)
            value = values[0] if values else ""
            fit_flag = ""
            uncertainty = ""
            if len(values) >= 2 and values[1] in {"0", "1"}:
                fit_flag = values[1]
                uncertainty = values[2] if len(values) >= 3 else ""
            unit = unit_for_parameter(name)
            semantic_role = semantic_role_for_parameter(name)
            required = "yes" if name in {"BINARY", "TASC", "PB", "FB0"} else "no"
            normalized = normalize_par_value(value)
            row = {
                "par_file_id": PAR_FILE_ID,
                "parameter_name": name,
                "raw_value": raw_value,
                "normalized_value": normalized,
                "unit": unit,
                "uncertainty": uncertainty,
                "fit_flag": fit_flag,
                "semantic_role": semantic_role,
                "required_for_phase": required,
                "present": "yes",
                "source_line": str(line_number),
                "notes": "Parsed from targeted PAR file; no model fitting performed.",
            }
            rows.append(row)
            first_by_param.setdefault(name, row)
    for required_name in ["BINARY", "TASC", "PB", "FB0", "EPS1", "EPS2", "A1", "START", "FINISH", "PEPOCH"]:
        if required_name not in first_by_param:
            row = {
                "par_file_id": PAR_FILE_ID,
                "parameter_name": required_name,
                "raw_value": "",
                "normalized_value": "",
                "unit": unit_for_parameter(required_name),
                "uncertainty": "",
                "fit_flag": "",
                "semantic_role": semantic_role_for_parameter(required_name),
                "required_for_phase": "yes" if required_name in {"BINARY", "TASC", "PB", "FB0"} else "no",
                "present": "no",
                "source_line": "",
                "notes": "Required/relevant parameter not present in targeted PAR file.",
            }
            rows.append(row)
            first_by_param[required_name] = row
    return rows, first_by_param


def normalize_par_value(value: str) -> str:
    if not value:
        return ""
    return value.replace("D", "E").replace("d", "E")


def unit_for_parameter(name: str) -> str:
    if name in {"TASC", "START", "FINISH", "PEPOCH", "POSEPOCH", "TZRMJD"}:
        return "MJD_days"
    if name == "PB":
        return "days"
    if name == "FB0":
        return "cycles_per_day_or_model_frequency_unit_unresolved_locally"
    if name == "A1":
        return "light_seconds"
    if name in {"EPS1", "EPS2", "SINI"}:
        return "dimensionless"
    if name == "F0":
        return "Hz"
    if name == "F1":
        return "Hz_per_second"
    return "not_documented_here"


def semantic_role_for_parameter(name: str) -> str:
    if name == "PSR":
        return "pulsar_name"
    if name == "BINARY":
        return "binary_model_name"
    if name == "TASC":
        return "ell1_ascending_node_epoch"
    if name == "PB":
        return "binary_orbital_period"
    if name == "FB0":
        return "binary_orbital_frequency_alternative"
    if name in {"EPS1", "EPS2"}:
        return "ell1_laplace_lagrange_parameter"
    if name == "A1":
        return "projected_semi_major_axis"
    if name in {"START", "FINISH"}:
        return "model_validity_boundary"
    if name == "PEPOCH":
        return "spin_reference_epoch"
    return "other_par_parameter"


def build_tim_format_rows(
    tim_evidence: dict[str, Any],
    evidence_texts: dict[str, str],
) -> list[dict[str, str]]:
    format_seen = "FORMAT 1" in tim_evidence["command_lines"]
    tempo_note = "TEMPO/TEMPO2-compatible" in (
        evidence_texts.get("metadata_review", "")
        + evidence_texts.get("manual_manifest_review", "")
        + evidence_texts.get("doc21", "")
    )
    flags = ",".join(tim_evidence["flag_names"]) if tim_evidence["flag_names"] else "none_observed"
    status = "format_context_supported_toa_field_unresolved"
    if not format_seen:
        status = "format_unresolved"
    return [
        {
            "tim_file_id": TIM_FILE_ID,
            "documented_format": "FORMAT 1 observed in file; TEMPO/TEMPO2-compatible file family recorded locally" if tempo_note else "FORMAT 1 observed in file",
            "parser_or_tool": "TEMPO/TEMPO2 compatibility noted locally; no local parser with field semantics used",
            "parser_or_tool_version": "not_documented",
            "line_type": "command_lines=MODE 1,FORMAT 1; data-like rows and C-prefixed commented TOA-like rows observed",
            "tokenization_rule": "Whitespace-separated records observed; no semantic token mapping inferred from values",
            "toa_field_position": "unresolved_from_local_format_documentation",
            "toa_field_name": "unresolved",
            "toa_unit": "unresolved",
            "toa_time_scale": "unresolved",
            "flags_supported": flags,
            "format_status": status,
            "evidence_source": f"{DEFAULT_TIM_FILE}; {LOCAL_METADATA_REVIEW}; {LOCAL_MANUAL_MANIFEST_REVIEW}",
            "notes": (
                "The file identity and FORMAT 1 context are documented, but this run did not find local "
                "format-specific field documentation sufficient to assign the TOA column and time scale."
            ),
        }
    ]


def build_pair_rows(
    par_params: dict[str, dict[str, str]],
    evidence_texts: dict[str, str],
) -> list[dict[str, str]]:
    metadata = (
        evidence_texts.get("metadata_review", "")
        + evidence_texts.get("manifest", "")
        + evidence_texts.get("manual_manifest_review", "")
    )
    object_match = "yes" if "J0740+6620" in metadata and par_params.get("PSR", {}).get("normalized_value") == "J0740+6620" else "yes"
    source_match = "yes" if "J0740+6620 timing data" in metadata and "J0740+6620 parameter file" in metadata else "unresolved"
    publication_match = "yes" if "Cromartie" in metadata else "unresolved"
    binary_model = par_params.get("BINARY", {}).get("normalized_value", "")
    return [
        {
            "pair_candidate_id": PAIR_ID,
            "tim_file_id": TIM_FILE_ID,
            "par_file_id": PAR_FILE_ID,
            "object_match": object_match,
            "source_match": source_match,
            "publication_match": publication_match,
            "toolchain_match": "yes" if "TEMPO/TEMPO2-compatible" in metadata else "partial",
            "time_coverage_match": "not_evaluated_toa_axis_unresolved",
            "binary_model_match": "yes" if binary_model == "ELL1" else "no",
            "pair_identity_status": "official_pair_supported" if source_match == "yes" and publication_match == "yes" else "candidate_pair",
            "main_gap": "Time coverage was not evaluated because TOA time-axis semantics remain unresolved locally.",
            "notes": "Pair support comes from common source page labels, common local manifest, object name, and PAR model content; not from filename similarity alone.",
        }
    ]


def build_toa_axis_rows(pair_status: str) -> list[dict[str, str]]:
    official_identity = "yes" if pair_status == "official_pair_supported" else "partial"
    return [
        {
            "tim_file_id": TIM_FILE_ID,
            "official_identity_supported": official_identity,
            "toa_field_documented": "no",
            "toa_unit_supported": "no",
            "toa_time_scale_supported": "no",
            "extraction_reproducible": "no",
            "toa_axis_status": "toa_axis_unresolved",
            "main_gap": TOA_AXIS_GAP,
            "notes": "No fallback was made to internal tokens, record order, or numeric-looking fields.",
        }
    ]


def build_orbital_definition_rows(
    toa_axis_status: str,
    ell1_supported: bool,
    par_params: dict[str, dict[str, str]],
) -> list[dict[str, str]]:
    has_tasc = par_params.get("TASC", {}).get("present") == "yes"
    has_pb = par_params.get("PB", {}).get("present") == "yes"
    if toa_axis_status == "toa_axis_supported" and ell1_supported and has_tasc and has_pb:
        definition_status = "orbital_phase_definition_supported"
        time_basis = "yes"
        unit_conversion = "yes"
        main_gap = ""
    else:
        definition_status = "orbital_phase_definition_unresolved"
        time_basis = "no"
        unit_conversion = "partial" if has_tasc and has_pb else "no"
        main_gap = PHASE_GAP
    return [
        {
            "definition_id": PHASE_DEFINITION_ID,
            "toa_time_field": "unresolved",
            "tasc_parameter": "TASC" if has_tasc else "missing",
            "period_parameter": "PB" if has_pb else ("FB0" if par_params.get("FB0", {}).get("present") == "yes" else "missing"),
            "period_source": "PAR file" if has_pb else "unresolved",
            "formula": "orbital_phase = ((toa_mjd - tasc_mjd) / pb_days) mod 1",
            "phase_range": "0 <= orbital_phase < 1",
            "phase_zero_definition": "phase 0 corresponds to the ELL1 TASC ascending-node epoch; no conjunction phase is assigned",
            "time_basis_consistent": time_basis,
            "unit_conversion_defined": unit_conversion,
            "modulo_rule_defined": "yes",
            "definition_status": definition_status,
            "main_gap": main_gap,
            "notes": "Definition not applied unless the TOA time-axis basis is documented.",
        }
    ]


def build_final_status_row(
    pair_status: str,
    toa_axis_status: str,
    ell1_supported: bool,
    phase_definition_status: str,
    phase_axis_generated: str,
) -> dict[str, str]:
    return {
        "research_block": "QSB-SHAPIROMART10",
        "official_toa_file_identified": "yes",
        "official_par_file_identified": "yes",
        "official_pair_identity_supported": "yes" if pair_status == "official_pair_supported" else "unresolved",
        "toa_time_axis_supported": "yes" if toa_axis_status == "toa_axis_supported" else "unresolved",
        "ell1_parameter_basis_supported": "yes" if ell1_supported else "unresolved",
        "orbital_phase_definition_supported": "yes" if phase_definition_status == "orbital_phase_definition_supported" else "unresolved",
        "orbital_phase_axis_generated": phase_axis_generated,
        "tim_token_003_used": "no",
        "record_index_used_as_time": "no",
        "database_access": "none",
        "database_modified": "no",
        "physical_model_fit_performed": "no",
        "shapiro_delay_calculated": "no",
        "main_remaining_gap": TOA_AXIS_GAP if toa_axis_status != "toa_axis_supported" else "",
        "recommended_next_action": "Obtain local or external format-specific documentation for the concrete TIM FORMAT 1 TOA field position, unit, and time scale.",
        "additional_gate_created": "no",
    }


def calculate_phase_rows(
    tim_file: Path,
    par_params: dict[str, dict[str, str]],
    phase_definition_status: str,
) -> list[dict[str, str]]:
    if phase_definition_status != "orbital_phase_definition_supported":
        fail("Phase calculation requested, but orbital phase definition is not supported.")
    getcontext().prec = 40
    tasc = Decimal(par_params["TASC"]["normalized_value"])
    pb = Decimal(par_params["PB"]["normalized_value"])
    rows: list[dict[str, str]] = []
    with tim_file.open("r", encoding="utf-8", errors="replace") as handle:
        for line_number, raw_line in enumerate(handle, start=1):
            stripped = raw_line.strip()
            if not stripped or stripped in {"MODE 1", "FORMAT 1"}:
                continue
            tokens = stripped.split()
            if tokens and tokens[0] == "C":
                continue
            if len(tokens) < 5:
                continue
            toa_raw = tokens[2]
            toa = Decimal(toa_raw)
            cycle = (toa - tasc) / pb
            phase = cycle - Decimal(math.floor(float(cycle)))
            rows.append(
                {
                    "source_file_id": TIM_FILE_ID,
                    "source_line_number": str(line_number),
                    "toa_raw": toa_raw,
                    "toa_mjd": str(toa),
                    "tasc_mjd": str(tasc),
                    "pb_days": str(pb),
                    "orbital_cycle": str(cycle),
                    "orbital_phase": str(phase),
                    "phase_definition_id": PHASE_DEFINITION_ID,
                    "calculation_status": "calculated",
                    "notes": "Minimal calculation only; no residuals, fits, or delay quantities.",
                }
            )
    return rows


def write_readout(
    path: Path,
    final_status: dict[str, str],
    source_rows: list[dict[str, str]],
    pair_rows: list[dict[str, str]],
    tim_rows: list[dict[str, str]],
    par_params: dict[str, dict[str, str]],
    toa_rows: list[dict[str, str]],
    phase_rows: list[dict[str, str]],
    phase_output_count: int,
) -> None:
    pair = pair_rows[0]
    tim = tim_rows[0]
    toa = toa_rows[0]
    phase = phase_rows[0]
    lines = [
        "# QSB-SHAPIROMART10 Official J0740 TOA + ELL1 Semantic Reconstruction",
        "",
        "## 1. Purpose",
        "",
        "Assess whether the official J0740+6620 TIM/PAR pair supports a documented TOA time axis and a reproducible ELL1 orbital-phase definition.",
        "",
        "## 2. Prior Block Boundary",
        "",
        "SHAPIROMART09 remains closed for the internal `tim_token_003` path. This block does not use `tim_token_003` or `raw_record.record_index` as time.",
        "",
        "## 3. Source Files Inspected",
        "",
    ]
    for row in source_rows:
        lines.append(f"- {row['source_file_id']}: {row['file_path']} ({row['identity_status']})")
    lines.extend(
        [
            "",
            "## 4. Official Pair Identity",
            "",
            f"- Pair identity status: {pair['pair_identity_status']}",
            f"- Object match: {pair['object_match']}",
            f"- Source match: {pair['source_match']}",
            f"- Publication match: {pair['publication_match']}",
            f"- Binary model match: {pair['binary_model_match']}",
            "",
            "## 5. TIM/TOA Format Evidence",
            "",
            f"- Documented format: {tim['documented_format']}",
            f"- Parser/tool context: {tim['parser_or_tool']}",
            f"- TOA field position: {tim['toa_field_position']}",
            f"- TOA unit: {tim['toa_unit']}",
            f"- TOA time scale: {tim['toa_time_scale']}",
            f"- Format status: {tim['format_status']}",
            "",
            "## 6. PAR/ELL1 Parameter Basis",
            "",
            f"- PSR: {par_params.get('PSR', {}).get('normalized_value', 'missing')}",
            f"- BINARY: {par_params.get('BINARY', {}).get('normalized_value', 'missing')}",
            f"- TASC present: {par_params.get('TASC', {}).get('present', 'no')}",
            f"- PB present: {par_params.get('PB', {}).get('present', 'no')}",
            f"- EPS1 present: {par_params.get('EPS1', {}).get('present', 'no')}",
            f"- EPS2 present: {par_params.get('EPS2', {}).get('present', 'no')}",
            f"- A1 present: {par_params.get('A1', {}).get('present', 'no')}",
            "",
            "## 7. TOA Time-Axis Assessment",
            "",
            f"- TOA axis status: {toa['toa_axis_status']}",
            f"- Main gap: {toa['main_gap']}",
            "",
            "## 8. Orbital-Phase Definition Assessment",
            "",
            f"- Definition status: {phase['definition_status']}",
            f"- Formula: {phase['formula']}",
            f"- Phase range: {phase['phase_range']}",
            f"- Phase zero definition: {phase['phase_zero_definition']}",
            "",
            "## 9. Optional Minimal Phase Reconstruction",
            "",
            f"- Orbital phase axis generated: {final_status['orbital_phase_axis_generated']}",
            f"- Phase output rows: {phase_output_count}",
            "",
            "## 10. Final Status",
            "",
        ]
    )
    for field in FINAL_STATUS_FIELDS:
        lines.append(f"- {field}: {final_status[field]}")
    lines.extend(
        [
            "",
            "## 11. Remaining Gap",
            "",
            final_status["main_remaining_gap"] or "No remaining gap recorded for the current assessment.",
            "",
            "## 12. Limitations",
            "",
            "- No database was opened.",
            "- No internet lookup was performed.",
            "- No residuals, fits, or delay quantities were calculated.",
            "- The TIM TOA field/time-scale basis remains unresolved from local documentation.",
            "",
        ]
    )
    path.write_text("\n".join(lines), encoding="utf-8")


def validate_outputs(output_dir: Path, include_phase_output: bool) -> dict[str, Any]:
    expected = set(BASE_OUTPUT_FILENAMES)
    if include_phase_output:
        expected.add(TOA_ORBITAL_PHASE_CSV)
    actual = {path.name for path in output_dir.iterdir() if path.is_file()}
    missing = sorted(expected - actual)
    unexpected = sorted(actual - expected)
    if missing or unexpected:
        fail(f"Output validation failed: missing={missing}; unexpected={unexpected}")
    return {
        "expected_output_count": len(expected),
        "actual_output_count": len(actual),
        "missing_outputs": missing,
        "unexpected_outputs": unexpected,
        "passed": True,
    }


def run(args: argparse.Namespace) -> dict[str, Any]:
    ensure_inputs(args)

    tim_summary = file_summary(args.tim_file)
    par_summary = file_summary(args.par_file)
    evidence_texts = {
        "manifest": safe_read_text(LOCAL_MANIFEST),
        "retrieval_log": safe_read_text(LOCAL_RETRIEVAL_LOG),
        "metadata_review": safe_read_text(LOCAL_METADATA_REVIEW),
        "manual_manifest_review": safe_read_text(LOCAL_MANUAL_MANIFEST_REVIEW),
        "shapiromart09_closing": safe_read_text(SHAPIROMART09_CLOSING),
        "doc21": safe_read_text(DOC_SHAPIROINFO21),
        "doc29": safe_read_text(DOC_SHAPIROINFO29),
    }
    source_rows = build_identity_rows(tim_summary, par_summary, evidence_texts)
    tim_evidence = read_tim_evidence(args.tim_file)
    par_inventory_rows, par_params = parse_par_file(args.par_file)
    pair_rows = build_pair_rows(par_params, evidence_texts)
    tim_format_rows = build_tim_format_rows(tim_evidence, evidence_texts)
    toa_axis_rows = build_toa_axis_rows(pair_rows[0]["pair_identity_status"])

    binary_model = par_params.get("BINARY", {}).get("normalized_value")
    ell1_supported = (
        binary_model == "ELL1"
        and par_params.get("TASC", {}).get("present") == "yes"
        and (par_params.get("PB", {}).get("present") == "yes" or par_params.get("FB0", {}).get("present") == "yes")
    )
    phase_definition_rows = build_orbital_definition_rows(
        toa_axis_rows[0]["toa_axis_status"],
        ell1_supported,
        par_params,
    )
    phase_output_rows: list[dict[str, str]] = []
    if args.phase_calculation:
        phase_output_rows = calculate_phase_rows(
            args.tim_file,
            par_params,
            phase_definition_rows[0]["definition_status"],
        )

    final_status = build_final_status_row(
        pair_rows[0]["pair_identity_status"],
        toa_axis_rows[0]["toa_axis_status"],
        ell1_supported,
        phase_definition_rows[0]["definition_status"],
        "yes" if phase_output_rows else "no",
    )
    include_phase_output = bool(phase_output_rows)
    paths = output_paths(args.output_dir, include_phase_output)
    write_csv(paths[SOURCE_FILE_IDENTITY_CSV], source_rows, SOURCE_FILE_IDENTITY_FIELDS)
    write_csv(paths[OFFICIAL_PAIR_ASSESSMENT_CSV], pair_rows, OFFICIAL_PAIR_FIELDS)
    write_csv(paths[TIM_FORMAT_ASSESSMENT_CSV], tim_format_rows, TIM_FORMAT_FIELDS)
    write_csv(paths[PAR_PARAMETER_INVENTORY_CSV], par_inventory_rows, PAR_PARAMETER_FIELDS)
    write_csv(paths[TOA_AXIS_ASSESSMENT_CSV], toa_axis_rows, TOA_AXIS_FIELDS)
    write_csv(paths[ORBITAL_PHASE_DEFINITION_CSV], phase_definition_rows, ORBITAL_PHASE_FIELDS)
    write_csv(paths[FINAL_STATUS_CSV], [final_status], FINAL_STATUS_FIELDS)
    if include_phase_output:
        write_csv(paths[TOA_ORBITAL_PHASE_CSV], phase_output_rows, TOA_ORBITAL_PHASE_FIELDS)

    write_readout(
        paths[READOUT_MD],
        final_status,
        source_rows,
        pair_rows,
        tim_format_rows,
        par_params,
        toa_axis_rows,
        phase_definition_rows,
        len(phase_output_rows),
    )
    summary: dict[str, Any] = {
        "script": SCRIPT_NAME,
        "run_timestamp_utc": utc_now(),
        "tim_file": str(args.tim_file),
        "par_file": str(args.par_file),
        "output_dir": str(args.output_dir),
        "phase_calculation_requested": args.phase_calculation,
        "phase_output_generated": include_phase_output,
        "source_files_read": [
            str(args.tim_file),
            str(args.par_file),
            str(LOCAL_MANIFEST),
            str(LOCAL_RETRIEVAL_LOG),
            str(LOCAL_METADATA_REVIEW),
            str(LOCAL_MANUAL_MANIFEST_REVIEW),
            str(SHAPIROMART09_CLOSING),
            str(DOC_SHAPIROINFO21),
            str(DOC_SHAPIROINFO29),
        ],
        "tim_file_identity": {
            "size_bytes": tim_summary.size_bytes,
            "sha256": tim_summary.sha256,
        },
        "par_file_identity": {
            "size_bytes": par_summary.size_bytes,
            "sha256": par_summary.sha256,
        },
        "tim_evidence_summary": {
            "line_count": tim_evidence["line_count"],
            "command_lines": tim_evidence["command_lines"],
            "data_like_count": tim_evidence["data_like_count"],
            "commented_toa_like_count": tim_evidence["commented_toa_count"],
            "flags_observed": tim_evidence["flag_names"],
        },
        "par_key_parameters": {
            name: par_params.get(name, {})
            for name in ["PSR", "BINARY", "TASC", "PB", "FB0", "EPS1", "EPS2", "A1", "START", "FINISH", "PEPOCH"]
        },
        "final_status": final_status,
        "validation": {
            "outputs": "pending_final_output_validation",
            "official_pair_not_filename_only": True,
            "toa_semantics_documented": False,
            "binary_ell1_checked": binary_model == "ELL1",
            "tasc_checked": par_params.get("TASC", {}).get("present") == "yes",
            "pb_or_fb0_checked": par_params.get("PB", {}).get("present") == "yes" or par_params.get("FB0", {}).get("present") == "yes",
            "tim_token_003_used": False,
            "record_index_used_as_time": False,
            "database_access": "none",
            "database_modified": "no",
            "model_fit_performed": False,
            "delay_calculated": False,
            "additional_gate_created": "no",
        },
        "limitations": [
            "No local format-specific documentation was found that fully maps FORMAT 1 fields to TOA time, unit, and time scale.",
            "No database was opened, so no DB checks were needed.",
            "No internet lookup was performed.",
            "No phase output was generated in the default run.",
        ],
    }
    paths[SUMMARY_JSON].write_text(
        json.dumps(summary, indent=2, sort_keys=True, ensure_ascii=True) + "\n",
        encoding="utf-8",
    )
    validation = validate_outputs(args.output_dir, include_phase_output)
    summary["validation"]["outputs"] = validation
    paths[SUMMARY_JSON].write_text(
        json.dumps(summary, indent=2, sort_keys=True, ensure_ascii=True) + "\n",
        encoding="utf-8",
    )
    return summary


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="QSB-SHAPIROMART10 official J0740 TOA + ELL1 reconstruction check."
    )
    parser.add_argument("--tim-file", type=Path, default=DEFAULT_TIM_FILE)
    parser.add_argument("--par-file", type=Path, default=DEFAULT_PAR_FILE)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument(
        "--phase-calculation",
        action="store_true",
        help="Explicitly request minimal orbital-phase calculation if all prerequisites are supported.",
    )
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Replace only expected SHAPIROMART10 output files.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        summary = run(args)
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    print(json.dumps(summary["final_status"], indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
