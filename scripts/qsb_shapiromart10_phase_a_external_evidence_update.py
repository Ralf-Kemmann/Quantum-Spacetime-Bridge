#!/usr/bin/env python3
"""QSB-SHAPIROMART10 Phase-A external evidence update.

This script validates locally archived TEMPO/TEMPO2 FORMAT 1 primary
documentation, reads the existing SHAPIROMART10 Phase-A outputs, and writes
three additive update files. It performs no database access, no model fit, no
TOA reconstruction, no orbital-phase generation, and no Shapiro calculation.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.parse import urlparse


SCRIPT_NAME = "scripts/qsb_shapiromart10_phase_a_external_evidence_update.py"

DEFAULT_OUTPUT_DIR = Path(
    "runs/QSB-SHAPIROMART/SHAPIROMART10_OFFICIAL_J0740_TOA_ELL1_RECONSTRUCTION"
)
DEFAULT_TIM_FILE = Path(
    "data/QSB-ST-SHAPIROINFO/public_sources/j0740_6620/raw/J0740+6620.cfr+19.tim"
)
DEFAULT_PAR_FILE = Path(
    "data/QSB-ST-SHAPIROINFO/public_sources/j0740_6620/raw/J0740+6620.par"
)
DEFAULT_EVIDENCE_NOTE = Path(
    "data/QSB-ST-SHAPIROINFO/manual_evidence/"
    "tempo_tempo2_format1_primary_field_definition.md"
)
DEFAULT_EVIDENCE_MANIFEST = Path(
    "data/QSB-ST-SHAPIROINFO/manual_evidence/"
    "tempo_tempo2_format1_primary_evidence_manifest.csv"
)
DEFAULT_SOURCE_DIR = Path(
    "data/QSB-ST-SHAPIROINFO/manual_evidence/tempo_tempo2_format1"
)

PHASE_A_FILES = [
    "shapiromart10_par_parameter_inventory.csv",
    "shapiromart10_summary.json",
    "shapiromart10_readout.md",
    "shapiromart10_tim_format_assessment.csv",
    "shapiromart10_source_file_identity.csv",
    "shapiromart10_toa_axis_assessment.csv",
    "shapiromart10_final_status.csv",
    "shapiromart10_orbital_phase_definition.csv",
    "shapiromart10_official_pair_assessment.csv",
]

UPDATE_MD = "shapiromart10_phase_a_external_evidence_update.md"
UPDATE_JSON = "shapiromart10_phase_a_external_evidence_summary.json"
UPDATE_CSV = "shapiromart10_phase_a_external_evidence.csv"
UPDATE_FILES = [UPDATE_MD, UPDATE_JSON, UPDATE_CSV]

EXPECTED_SOURCE_FILES = {
    "tempo_reference_toa_format.txt",
    "tempo2_examples_ver1.pdf",
    "tempo2_manual.pdf",
}

ALLOWED_SOURCE_HOSTS = {
    "tempo.sourceforge.net",
    "www.jb.man.ac.uk",
}

MAIN_REMAINING_GAP = (
    "Model-consistent TOA handling, clock corrections, and orbital-phase "
    "generation have not yet been validated through a documented TEMPO2 "
    "or PINT execution."
)

RECOMMENDED_NEXT_ACTION = (
    "Perform one controlled read-only PINT or TEMPO2 reconstruction using "
    "the official J0740 TIM/PAR pair. Validate the model-consistent TOA "
    "objects and generate the orbital-phase axis without fitting or changing "
    "the timing model."
)

CSV_FIELDS = [
    "research_block",
    "update_type",
    "update_timestamp_utc",
    "official_toa_file_identified",
    "official_par_file_identified",
    "official_pair_identity_supported",
    "prior_toa_axis_status",
    "official_tim_format",
    "toa_field_position_supported",
    "toa_field_position",
    "toa_field_name",
    "toa_field_unit_supported",
    "toa_field_unit",
    "toa_file_axis_supported",
    "toa_model_time_basis_fully_validated",
    "ell1_model_supported",
    "ell1_parameter_basis_supported",
    "tasc_present",
    "pb_present",
    "orbital_phase_definition_supported",
    "orbital_phase_axis_generated",
    "tim_token_003_mapping_changed",
    "external_primary_evidence_used",
    "existing_phase_a_outputs_modified",
    "database_access",
    "physical_calculation_performed",
    "model_fit_performed",
    "shapiro_delay_calculated",
    "additional_gate_created",
    "main_remaining_gap",
    "recommended_next_action",
    "evidence_note_path",
    "evidence_manifest_path",
    "primary_sources_retrieved",
]


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


def file_record(path: Path) -> dict[str, Any]:
    stat = path.stat()
    return {
        "path": str(path),
        "size_bytes": stat.st_size,
        "mtime_ns": stat.st_mtime_ns,
        "sha256": file_sha256(path),
    }


def read_csv_rows(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def read_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def write_csv(path: Path, rows: list[dict[str, Any]], fields: list[str]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for row in rows:
            writer.writerow({field: row.get(field, "") for field in fields})


def write_json(path: Path, payload: dict[str, Any]) -> None:
    with path.open("w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2, sort_keys=True)
        handle.write("\n")


def single_row(path: Path) -> dict[str, str]:
    rows = read_csv_rows(path)
    if len(rows) != 1:
        fail(f"Expected exactly one row in {path}, found {len(rows)}.")
    return rows[0]


def keyed_rows(path: Path, key_field: str) -> dict[str, dict[str, str]]:
    rows = read_csv_rows(path)
    keyed: dict[str, dict[str, str]] = {}
    for row in rows:
        key = row.get(key_field, "")
        if key:
            keyed[key] = row
    return keyed


def parse_note_key_values(text: str) -> dict[str, str]:
    values: dict[str, str] = {}
    for line in text.splitlines():
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        key = key.strip()
        value = value.strip()
        if re.fullmatch(r"[A-Za-z0-9_]+", key):
            values[key] = value
    return values


def ensure_required_paths(args: argparse.Namespace) -> None:
    required = [
        args.output_dir,
        args.tim_file,
        args.par_file,
        args.evidence_note,
        args.evidence_manifest,
        args.source_dir,
    ]
    required.extend(args.output_dir / name for name in PHASE_A_FILES)
    for path in required:
        if not path.exists():
            fail(f"Required input is missing: {path}")

    existing = [
        str(args.output_dir / name)
        for name in UPDATE_FILES
        if (args.output_dir / name).exists()
    ]
    if existing and not args.overwrite_update_files:
        fail(
            "Update output file(s) already exist. Re-run with "
            "--overwrite-update-files to replace only these files: "
            + "; ".join(existing)
        )


def validate_source_directory(source_dir: Path) -> dict[str, Any]:
    actual = {path.name for path in source_dir.iterdir() if path.is_file()}
    unexpected = sorted(actual - EXPECTED_SOURCE_FILES)
    missing = sorted(EXPECTED_SOURCE_FILES - actual)
    if missing:
        fail("Expected archived primary source file(s) missing: " + "; ".join(missing))
    if unexpected:
        fail("Unexpected file(s) in primary evidence directory: " + "; ".join(unexpected))
    return {"expected_files": sorted(EXPECTED_SOURCE_FILES), "unexpected_files": []}


def validate_evidence_note(path: Path) -> dict[str, Any]:
    text = path.read_text(encoding="utf-8")
    values = parse_note_key_values(text)
    expected = {
        "evidence_id": "TEMPO_TEMPO2_FORMAT1_PRIMARY_FIELD_DEFINITION",
        "evidence_type": "external_primary_documentation",
        "evidence_status": "supported",
        "format_name": "TEMPO/TEMPO2 FORMAT 1",
        "field_position_2_unit": "MHz",
        "field_position_3": "TOA_or_site_arrival_time",
        "field_position_3_unit": "MJD",
        "field_position_4": "TOA_uncertainty",
        "field_position_4_unit": "microseconds",
        "applies_to_file": "J0740+6620.cfr+19.tim",
        "format_header_confirmed": "yes",
        "maps_to_tim_token_003": "no",
    }
    for key, expected_value in expected.items():
        if values.get(key) != expected_value:
            fail(
                f"Evidence note value mismatch for {key}: "
                f"expected {expected_value!r}, found {values.get(key)!r}."
            )
    required_phrases = [
        "This evidence documents the official FORMAT 1 file layout.",
        "It does not establish any mapping from the official TIM fields",
        "tim_token_003",
        "The documentation supports the file-level TOA field and its MJD unit.",
        "It does not by itself validate the complete model-consistent clock",
    ]
    for phrase in required_phrases:
        if phrase not in text:
            fail(f"Evidence note missing required phrase: {phrase}")
    return {"path": str(path), "key_values_checked": sorted(expected)}


def validate_manifest(path: Path) -> dict[str, Any]:
    rows = read_csv_rows(path)
    if not rows:
        fail(f"Evidence manifest has no rows: {path}")

    required_fields = [
        "evidence_source_id",
        "source_title",
        "source_organization",
        "source_url",
        "retrieval_timestamp_utc",
        "local_path",
        "file_name",
        "file_size_bytes",
        "sha256",
        "detected_file_type",
        "retrieval_status",
        "supports_field_order",
        "supports_toa_position",
        "supports_toa_mjd_unit",
        "supports_uncertainty_unit",
        "supports_full_time_scale",
        "notes",
    ]
    for field in required_fields:
        if field not in rows[0]:
            fail(f"Evidence manifest missing field: {field}")

    validated_sources: list[dict[str, Any]] = []
    field_order_sources = 0
    toa_position_sources = 0
    toa_mjd_sources = 0
    uncertainty_sources = 0

    for row in rows:
        url = row["source_url"]
        parsed = urlparse(url)
        if parsed.scheme != "https" or parsed.netloc not in ALLOWED_SOURCE_HOSTS:
            fail(f"Evidence source is not on an allowed official host: {url}")
        if row["retrieval_status"] != "downloaded_via_curl_exit_0_and_local_validation_passed":
            fail(f"Evidence source retrieval status is not supported: {row}")
        if row["supports_full_time_scale"] != "no":
            fail("Manifest may not mark full model time-scale support as yes.")

        local_path = Path(row["local_path"])
        if not local_path.exists():
            fail(f"Archived primary source missing: {local_path}")
        actual_size = local_path.stat().st_size
        if actual_size <= 0:
            fail(f"Archived primary source is empty: {local_path}")
        if str(actual_size) != row["file_size_bytes"]:
            fail(f"Archived source size mismatch for {local_path}")
        actual_sha = file_sha256(local_path)
        if actual_sha != row["sha256"]:
            fail(f"Archived source SHA-256 mismatch for {local_path}")

        suffix = local_path.suffix.lower()
        if suffix == ".pdf":
            with local_path.open("rb") as handle:
                if handle.read(5) != b"%PDF-":
                    fail(f"Archived PDF does not begin with %PDF: {local_path}")
        elif suffix == ".txt":
            text = local_path.read_text(encoding="utf-8", errors="replace")
            lowered = text[:200].lower()
            if "<html" in lowered or "<!doctype html" in lowered:
                fail(f"Archived TXT looks like an HTML page: {local_path}")
            for phrase in [
                "FORMAT 1",
                "Observing frequency",
                "TOA",
                "TOA uncertainty",
                "Observatory",
            ]:
                if phrase not in text:
                    fail(f"Archived TXT missing required phrase {phrase!r}: {local_path}")
        else:
            fail(f"Unexpected archived source extension: {local_path}")

        if row["supports_field_order"] == "yes":
            field_order_sources += 1
        if row["supports_toa_position"] == "yes":
            toa_position_sources += 1
        if row["supports_toa_mjd_unit"] == "yes":
            toa_mjd_sources += 1
        if row["supports_uncertainty_unit"] == "yes":
            uncertainty_sources += 1

        validated_sources.append(
            {
                "evidence_source_id": row["evidence_source_id"],
                "source_url": url,
                "local_path": str(local_path),
                "file_size_bytes": actual_size,
                "sha256": actual_sha,
                "supports_field_order": row["supports_field_order"],
                "supports_toa_position": row["supports_toa_position"],
                "supports_toa_mjd_unit": row["supports_toa_mjd_unit"],
                "supports_uncertainty_unit": row["supports_uncertainty_unit"],
                "supports_full_time_scale": row["supports_full_time_scale"],
            }
        )

    if field_order_sources < 1 or toa_position_sources < 1:
        fail("No official source supports FORMAT 1 field order and TOA position.")
    if toa_mjd_sources < 1:
        fail("No official source supports the TOA MJD unit.")
    if uncertainty_sources < 1:
        fail("No official source supports the TOA uncertainty unit.")

    return {
        "path": str(path),
        "validated_source_count": len(validated_sources),
        "sources": validated_sources,
        "field_order_source_count": field_order_sources,
        "toa_position_source_count": toa_position_sources,
        "toa_mjd_source_count": toa_mjd_sources,
        "uncertainty_source_count": uncertainty_sources,
    }


def validate_tim_file(path: Path) -> dict[str, Any]:
    text = path.read_text(encoding="utf-8", errors="replace")
    lines = [line.strip() for line in text.splitlines()[:20]]
    if "FORMAT 1" not in lines:
        fail(f"Official TIM file does not contain FORMAT 1 in the header: {path}")
    return {"path": str(path), "format_header_confirmed": "yes"}


def validate_par_file(path: Path) -> dict[str, str]:
    values: dict[str, str] = {}
    with path.open("r", encoding="utf-8", errors="replace") as handle:
        for line in handle:
            stripped = line.strip()
            if not stripped or stripped.startswith("#"):
                continue
            parts = stripped.split()
            if parts:
                values.setdefault(parts[0], parts[1] if len(parts) > 1 else "")
    if values.get("BINARY") != "ELL1":
        fail(f"PAR file does not contain BINARY ELL1: {path}")
    for parameter in ["TASC", "PB"]:
        if parameter not in values:
            fail(f"PAR file missing required ELL1 parameter {parameter}: {path}")
    return {"binary_model": values["BINARY"], "TASC_present": "yes", "PB_present": "yes"}


def validate_phase_a_outputs(output_dir: Path) -> dict[str, Any]:
    final_status = single_row(output_dir / "shapiromart10_final_status.csv")
    expected_final = {
        "official_toa_file_identified": "yes",
        "official_par_file_identified": "yes",
        "official_pair_identity_supported": "yes",
        "toa_time_axis_supported": "unresolved",
        "ell1_parameter_basis_supported": "yes",
        "orbital_phase_definition_supported": "unresolved",
        "orbital_phase_axis_generated": "no",
        "tim_token_003_used": "no",
        "database_access": "none",
        "physical_model_fit_performed": "no",
        "shapiro_delay_calculated": "no",
        "additional_gate_created": "no",
    }
    for key, expected_value in expected_final.items():
        if final_status.get(key) != expected_value:
            fail(
                f"Phase-A final status mismatch for {key}: "
                f"expected {expected_value!r}, found {final_status.get(key)!r}."
            )

    source_rows = read_csv_rows(output_dir / "shapiromart10_source_file_identity.csv")
    if not any(row.get("file_name") == "J0740+6620.cfr+19.tim" for row in source_rows):
        fail("Phase-A source identity does not include the official TIM file.")
    if not any(row.get("file_name") == "J0740+6620.par" for row in source_rows):
        fail("Phase-A source identity does not include the official PAR file.")

    pair = single_row(output_dir / "shapiromart10_official_pair_assessment.csv")
    if pair.get("pair_identity_status") != "official_pair_supported":
        fail("Phase-A official pair status is not official_pair_supported.")

    toa_axis = single_row(output_dir / "shapiromart10_toa_axis_assessment.csv")
    if toa_axis.get("toa_axis_status") != "toa_axis_unresolved":
        fail("Phase-A TOA axis status is not toa_axis_unresolved.")

    par_by_name = keyed_rows(
        output_dir / "shapiromart10_par_parameter_inventory.csv", "parameter_name"
    )
    binary = par_by_name.get("BINARY", {})
    tasc = par_by_name.get("TASC", {})
    pb = par_by_name.get("PB", {})
    if binary.get("normalized_value") != "ELL1" or binary.get("present") != "yes":
        fail("Phase-A PAR inventory does not support BINARY ELL1.")
    if tasc.get("present") != "yes":
        fail("Phase-A PAR inventory does not mark TASC present.")
    if pb.get("present") != "yes":
        fail("Phase-A PAR inventory does not mark PB present.")

    return {
        "final_status": final_status,
        "source_identity_rows": len(source_rows),
        "official_pair_assessment": pair,
        "toa_axis_assessment": toa_axis,
        "ell1_model_supported": "yes",
        "tasc_present": "yes",
        "pb_present": "yes",
    }


def update_row(
    timestamp: str,
    args: argparse.Namespace,
    phase_a: dict[str, Any],
    manifest: dict[str, Any],
) -> dict[str, Any]:
    final_status = phase_a["final_status"]
    return {
        "research_block": "QSB-SHAPIROMART10",
        "update_type": "external_primary_evidence_update",
        "update_timestamp_utc": timestamp,
        "official_toa_file_identified": final_status["official_toa_file_identified"],
        "official_par_file_identified": final_status["official_par_file_identified"],
        "official_pair_identity_supported": final_status[
            "official_pair_identity_supported"
        ],
        "prior_toa_axis_status": final_status["toa_time_axis_supported"],
        "official_tim_format": "FORMAT 1",
        "toa_field_position_supported": "yes",
        "toa_field_position": "3",
        "toa_field_name": "TOA",
        "toa_field_unit_supported": "yes",
        "toa_field_unit": "MJD",
        "toa_file_axis_supported": "yes",
        "toa_model_time_basis_fully_validated": "no",
        "ell1_model_supported": phase_a["ell1_model_supported"],
        "ell1_parameter_basis_supported": final_status[
            "ell1_parameter_basis_supported"
        ],
        "tasc_present": phase_a["tasc_present"],
        "pb_present": phase_a["pb_present"],
        "orbital_phase_definition_supported": "provisionally_supported",
        "orbital_phase_axis_generated": "no",
        "tim_token_003_mapping_changed": "no",
        "external_primary_evidence_used": "yes",
        "existing_phase_a_outputs_modified": "no",
        "database_access": "none",
        "physical_calculation_performed": "no",
        "model_fit_performed": "no",
        "shapiro_delay_calculated": "no",
        "additional_gate_created": "no",
        "main_remaining_gap": MAIN_REMAINING_GAP,
        "recommended_next_action": RECOMMENDED_NEXT_ACTION,
        "evidence_note_path": str(args.evidence_note),
        "evidence_manifest_path": str(args.evidence_manifest),
        "primary_sources_retrieved": str(manifest["validated_source_count"]),
    }


def build_markdown(row: dict[str, Any], manifest: dict[str, Any]) -> str:
    sources = "\n".join(
        f"- {source['evidence_source_id']}: {source['local_path']}"
        for source in manifest["sources"]
    )
    return f"""# QSB-SHAPIROMART10 Phase-A External Evidence Update

## 1. Result

This additive update uses locally archived official TEMPO/TEMPO2 documentation
to support the FORMAT 1 file-level TOA axis for the official J0740 TIM file.

## 2. Prior Phase-A Status

```text
official_toa_file_identified = {row['official_toa_file_identified']}
official_par_file_identified = {row['official_par_file_identified']}
official_pair_identity_supported = {row['official_pair_identity_supported']}
prior_toa_axis_status = {row['prior_toa_axis_status']}
ell1_parameter_basis_supported = {row['ell1_parameter_basis_supported']}
orbital_phase_axis_generated = no
```

## 3. External Primary Evidence

The local evidence note and manifest identify official FORMAT 1 documentation
and validate the archived source files by local path, size, SHA-256, source URL,
file type, and retrieval status.

{sources}

## 4. FORMAT 1 Field Semantics

The official FORMAT 1 documentation supports field position 3 of the official
J0740 TIM data line as the TOA field. The documented TOA or arrival-time unit
is MJD.

```text
official_tim_format = FORMAT 1
toa_field_position_supported = yes
toa_field_position = 3
toa_field_name = TOA
toa_field_unit_supported = yes
toa_field_unit = MJD
```

## 5. Applicability

The official J0740 TIM file contains a FORMAT 1 header, so the file-level
FORMAT 1 layout evidence applies to that TIM file.

## 6. Updated Status

```text
toa_file_axis_supported = yes
toa_model_time_basis_fully_validated = no
ell1_model_supported = yes
tasc_present = yes
pb_present = yes
orbital_phase_definition_supported = provisionally_supported
orbital_phase_axis_generated = no
```

Here, provisionally_supported means that the official pair is identified, the
TOA field and MJD unit are documented, ELL1 is present, TASC and PB are present,
and a mathematical phase definition is possible in principle. The documented
TEMPO2 or PINT processing chain has not been executed here.

## 7. tim_token_003 Boundary

This update applies to the official FORMAT 1 file layout only. It does not map
the official TIM fields to the previously unresolved internal token
tim_token_003.

```text
tim_token_003_mapping_changed = no
```

## 8. Processing Boundary

```text
database_access = none
physical_calculation_performed = no
model_fit_performed = no
shapiro_delay_calculated = no
additional_gate_created = no
```

No orbital phase axis was generated, no clock-correction chain was executed,
and no timing model was changed.

## 9. Remaining Gap

{MAIN_REMAINING_GAP}

## 10. Recommended Next Action

{RECOMMENDED_NEXT_ACTION}
"""


def build_summary_json(
    row: dict[str, Any],
    args: argparse.Namespace,
    source_dir: dict[str, Any],
    evidence_note: dict[str, Any],
    manifest: dict[str, Any],
    tim_validation: dict[str, Any],
    par_validation: dict[str, Any],
    phase_a: dict[str, Any],
    phase_a_records_before: list[dict[str, Any]],
) -> dict[str, Any]:
    return {
        "research_block": row["research_block"],
        "update_type": row["update_type"],
        "update_timestamp_utc": row["update_timestamp_utc"],
        "script": SCRIPT_NAME,
        "update_status": "supported",
        "updated_status": row,
        "inputs": {
            "output_dir": str(args.output_dir),
            "tim_file": str(args.tim_file),
            "par_file": str(args.par_file),
            "evidence_note": str(args.evidence_note),
            "evidence_manifest": str(args.evidence_manifest),
            "source_dir": str(args.source_dir),
        },
        "validations": {
            "source_dir": source_dir,
            "evidence_note": evidence_note,
            "evidence_manifest": manifest,
            "tim_file": tim_validation,
            "par_file": par_validation,
            "phase_a": phase_a,
        },
        "phase_a_file_records_before_update": phase_a_records_before,
        "boundaries": {
            "database_access": "none",
            "raw_data_recalculation": "no",
            "orbital_phase_axis_generated": "no",
            "tim_token_003_mapping_changed": "no",
            "model_fit_performed": "no",
            "shapiro_delay_calculated": "no",
            "physical_calculation_performed": "no",
            "additional_gate_created": "no",
        },
        "main_remaining_gap": MAIN_REMAINING_GAP,
        "recommended_next_action": RECOMMENDED_NEXT_ACTION,
    }


def ensure_phase_a_records_unchanged(
    before: list[dict[str, Any]], output_dir: Path
) -> None:
    after = [file_record(output_dir / name) for name in PHASE_A_FILES]
    before_by_path = {record["path"]: record for record in before}
    for record in after:
        prior = before_by_path.get(record["path"])
        if prior != record:
            fail(f"Existing Phase-A output changed unexpectedly: {record['path']}")


def run(args: argparse.Namespace) -> dict[str, Any]:
    ensure_required_paths(args)

    phase_a_records_before = [file_record(args.output_dir / name) for name in PHASE_A_FILES]

    source_dir = validate_source_directory(args.source_dir)
    evidence_note = validate_evidence_note(args.evidence_note)
    manifest = validate_manifest(args.evidence_manifest)
    tim_validation = validate_tim_file(args.tim_file)
    par_validation = validate_par_file(args.par_file)
    phase_a = validate_phase_a_outputs(args.output_dir)

    timestamp = utc_now()
    row = update_row(timestamp, args, phase_a, manifest)

    outputs = {
        UPDATE_MD: args.output_dir / UPDATE_MD,
        UPDATE_JSON: args.output_dir / UPDATE_JSON,
        UPDATE_CSV: args.output_dir / UPDATE_CSV,
    }

    markdown = build_markdown(row, manifest)
    summary = build_summary_json(
        row,
        args,
        source_dir,
        evidence_note,
        manifest,
        tim_validation,
        par_validation,
        phase_a,
        phase_a_records_before,
    )

    outputs[UPDATE_MD].write_text(markdown, encoding="utf-8")
    write_json(outputs[UPDATE_JSON], summary)
    write_csv(outputs[UPDATE_CSV], [row], CSV_FIELDS)

    ensure_phase_a_records_unchanged(phase_a_records_before, args.output_dir)

    return {
        "result": "wrote_update_files",
        "outputs": {name: str(path) for name, path in outputs.items()},
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Create the additive SHAPIROMART10 Phase-A external primary "
            "evidence update after validating local TEMPO/TEMPO2 FORMAT 1 evidence."
        )
    )
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--tim-file", type=Path, default=DEFAULT_TIM_FILE)
    parser.add_argument("--par-file", type=Path, default=DEFAULT_PAR_FILE)
    parser.add_argument("--evidence-note", type=Path, default=DEFAULT_EVIDENCE_NOTE)
    parser.add_argument(
        "--evidence-manifest", type=Path, default=DEFAULT_EVIDENCE_MANIFEST
    )
    parser.add_argument("--source-dir", type=Path, default=DEFAULT_SOURCE_DIR)
    parser.add_argument(
        "--overwrite-update-files",
        action="store_true",
        help="Replace only the three additive update output files.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        result = run(args)
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
