#!/usr/bin/env python3
"""QSB-SHAPIROMART11 controlled PINT reconstruction.

This script loads the official J0740 TIM/PAR pair with pulsar-timing PINT,
records the software and input identity, and attempts a bounded
model-consistent orbital-phase reconstruction. It performs no fit, no model
parameter changes, no residual analysis, no database access, and no Shapiro
calculation.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import importlib
import json
import os
import platform
import sys
import warnings
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


SCRIPT_NAME = "scripts/qsb_shapiromart11_controlled_pint_reconstruction.py"

SHAPIROMART10_DIR = Path(
    "runs/QSB-SHAPIROMART/SHAPIROMART10_OFFICIAL_J0740_TOA_ELL1_RECONSTRUCTION"
)
SOURCE_IDENTITY_CSV = SHAPIROMART10_DIR / "shapiromart10_source_file_identity.csv"
FINAL_STATUS_10_CSV = SHAPIROMART10_DIR / "shapiromart10_final_status.csv"
PHASE_A_UPDATE_CSV = SHAPIROMART10_DIR / "shapiromart10_phase_a_external_evidence.csv"

DEFAULT_OUTPUT_DIR = Path(
    "runs/QSB-SHAPIROMART/SHAPIROMART11_CONTROLLED_PINT_RECONSTRUCTION"
)

READOUT_MD = "shapiromart11_readout.md"
SUMMARY_JSON = "shapiromart11_summary.json"
ENVIRONMENT_CSV = "shapiromart11_environment.csv"
INPUT_IDENTITY_CSV = "shapiromart11_input_identity.csv"
PINT_LOAD_ASSESSMENT_CSV = "shapiromart11_pint_load_assessment.csv"
MODEL_PARAMETER_ASSESSMENT_CSV = "shapiromart11_model_parameter_assessment.csv"
TOA_PROCESSING_ASSESSMENT_CSV = "shapiromart11_toa_processing_assessment.csv"
ORBITAL_PHASE_ASSESSMENT_CSV = "shapiromart11_orbital_phase_assessment.csv"
FINAL_STATUS_CSV = "shapiromart11_final_status.csv"
TOA_ORBITAL_PHASE_CSV = "shapiromart11_toa_orbital_phase.csv"

BASE_OUTPUT_FILES = [
    READOUT_MD,
    SUMMARY_JSON,
    ENVIRONMENT_CSV,
    INPUT_IDENTITY_CSV,
    PINT_LOAD_ASSESSMENT_CSV,
    MODEL_PARAMETER_ASSESSMENT_CSV,
    TOA_PROCESSING_ASSESSMENT_CSV,
    ORBITAL_PHASE_ASSESSMENT_CSV,
    FINAL_STATUS_CSV,
]

PHASE_OUTPUT_FILES = BASE_OUTPUT_FILES + [TOA_ORBITAL_PHASE_CSV]

INSTALL_PROVENANCE_FILES = [
    "shapiromart11_environment_before_install.txt",
    "shapiromart11_environment_after_install.txt",
    "shapiromart11_pint_install_manifest.csv",
    "shapiromart11_pip_freeze.txt",
]

ENVIRONMENT_FIELDS = [
    "python_version",
    "pint_version",
    "astropy_version",
    "numpy_version",
    "platform",
    "ephemeris_requested",
    "ephemeris_used",
    "clock_data_source",
    "environment_status",
    "notes",
]

INPUT_IDENTITY_FIELDS = [
    "input_role",
    "file_path",
    "file_name",
    "file_size_bytes",
    "sha256",
    "official_identity_supported",
    "format_or_model",
    "notes",
]

PINT_LOAD_FIELDS = [
    "model_loaded",
    "toas_loaded",
    "toa_count",
    "parser_format",
    "clock_corrections_applied",
    "clock_correction_status",
    "barycentric_columns_available",
    "load_status",
    "warning_count",
    "error_count",
    "notes",
]

MODEL_PARAMETER_FIELDS = [
    "parameter_name",
    "parameter_value",
    "unit",
    "frozen",
    "uncertainty",
    "model_component",
    "required_for_phase",
    "present",
    "notes",
]

TOA_PROCESSING_FIELDS = [
    "toa_time_column",
    "original_scale",
    "processed_scale",
    "clock_corrected",
    "barycentric_time_available",
    "model_time_available",
    "processing_status",
    "notes",
]

ORBITAL_PHASE_FIELDS = [
    "phase_method",
    "pint_function_or_fallback",
    "model_component",
    "time_input",
    "tasc_value",
    "tasc_scale",
    "pb_value",
    "pb_unit",
    "phase_range",
    "phase_zero_definition",
    "phase_generated",
    "phase_count",
    "finite_phase_count",
    "minimum_phase",
    "maximum_phase",
    "definition_status",
    "main_gap",
    "notes",
]

TOA_ORBITAL_PHASE_FIELDS = [
    "source_row_index",
    "source_filename",
    "observatory",
    "observing_frequency_mhz",
    "toa_mjd_file",
    "toa_time_scale",
    "processed_time_value",
    "processed_time_scale",
    "orbital_phase",
    "phase_method",
    "model_name",
    "tasc_value",
    "pb_value",
    "calculation_status",
    "notes",
]

FINAL_STATUS_FIELDS = [
    "research_block",
    "official_pair_used",
    "pint_available",
    "model_loaded",
    "toas_loaded",
    "ell1_model_confirmed",
    "tasc_available",
    "pb_available",
    "clock_correction_status",
    "model_consistent_time_available",
    "orbital_phase_definition_supported",
    "orbital_phase_generated",
    "orbital_phase_exported",
    "model_fit_performed",
    "model_parameters_modified",
    "shapiro_delay_calculated",
    "residual_analysis_performed",
    "tim_token_003_used",
    "record_index_used_as_time",
    "database_access",
    "database_modified",
    "additional_gate_created",
    "final_status",
    "main_remaining_gap",
    "recommended_next_action",
]

REQUIRED_MODEL_PARAMETERS = [
    "BINARY",
    "TASC",
    "PB",
    "A1",
    "EPS1",
    "EPS2",
    "PEPOCH",
    "START",
    "FINISH",
]

PHASE_REQUIRED_PARAMETERS = {"TASC", "PB"}

NO_PHASE_GAP = (
    "PINT loaded the official pair, but no documented PINT model function or "
    "toolchain-based fallback met the requirements for orbital-phase generation."
)
NO_ENV_GAP = "The pulsar-timing PINT dependency is not installed in the active Python environment."
SUCCESS_NEXT_ACTION = (
    "Use the exported diagnostic status and, if needed, the explicit phase export "
    "as the reproducible SHAPIROMART11 reconstruction record."
)
INSTALL_NEXT_ACTION = (
    "Install the pulsar-timing PINT package in an approved environment, then rerun "
    "this script without changing the official TIM/PAR input pair."
)
PHASE_NEXT_ACTION = (
    "Inspect the documented PINT binary-model API for an orbital-phase method or "
    "rerun with a PINT version that exposes compatible processed binary-phase data."
)


@dataclass
class PintModules:
    pint: Any
    pint_models: Any
    pint_toa: Any
    astropy: Any
    numpy: Any
    astropy_units: Any


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


def read_csv_rows(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


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


def env_notes() -> str:
    keys = [
        "PINT_CLOCK_OVERRIDE",
        "PINT_DATA_PATH",
        "TEMPO",
        "TEMPO2",
        "EPHEM",
        "ASTROPY_CACHE_DIR",
        "ASTROPY_USE_SYSTEM_TIMEZONE",
        "IERS_A_URL",
        "XDG_CACHE_HOME",
    ]
    present = [f"{key}={os.environ[key]}" for key in keys if key in os.environ]
    return "; ".join(present) if present else "No relevant environment variables set."


def collect_astropy_resource_records() -> list[dict[str, Any]]:
    cache_root = Path.home() / ".astropy" / "cache" / "download" / "url"
    if not cache_root.exists():
        return []
    records: list[dict[str, Any]] = []
    for url_file in sorted(cache_root.glob("*/url")):
        cache_dir = url_file.parent
        contents = cache_dir / "contents"
        if not contents.exists():
            continue
        url = url_file.read_text(encoding="utf-8", errors="replace").strip()
        if not any(
            marker in url
            for marker in [
                "pulsar-clock-corrections",
                "de436.bsp",
                "finals2000A.all",
            ]
        ):
            continue
        records.append(
            {
                "url": url,
                "provider": "IPTA/PINT clock corrections"
                if "pulsar-clock-corrections" in url
                else "JPL ephemeris"
                if "de436.bsp" in url
                else "IERS Earth orientation data",
                "local_cache_path": str(contents),
                "file_size_bytes": contents.stat().st_size,
                "sha256": file_sha256(contents),
                "retrieval_status": "cache_present_after_run",
                "notes": "Resource observed in Astropy download cache after PINT reconstruction.",
            }
        )
    return records


def import_environment(ephem: str) -> tuple[dict[str, str], PintModules | None, str | None]:
    base = {
        "python_version": sys.version.replace("\n", " "),
        "pint_version": "unavailable",
        "astropy_version": "unavailable",
        "numpy_version": "unavailable",
        "platform": platform.platform(),
        "ephemeris_requested": ephem,
        "ephemeris_used": "not_loaded",
        "clock_data_source": "not_loaded",
        "environment_status": "pint_not_available",
        "notes": env_notes(),
    }
    try:
        pint = importlib.import_module("pint")
        pint_models = importlib.import_module("pint.models")
        pint_toa = importlib.import_module("pint.toa")
        astropy = importlib.import_module("astropy")
        numpy = importlib.import_module("numpy")
        astropy_units = importlib.import_module("astropy.units")
    except Exception as exc:
        return base, None, f"{type(exc).__name__}: {exc}"

    modules = PintModules(
        pint=pint,
        pint_models=pint_models,
        pint_toa=pint_toa,
        astropy=astropy,
        numpy=numpy,
        astropy_units=astropy_units,
    )
    base.update(
        {
            "pint_version": str(getattr(pint, "__version__", "unknown")),
            "astropy_version": str(getattr(astropy, "__version__", "unknown")),
            "numpy_version": str(getattr(numpy, "__version__", "unknown")),
            "environment_status": "pulsar_pint_available",
        }
    )
    return base, modules, None


def source_identity_paths() -> tuple[Path, Path, dict[str, str], dict[str, str]]:
    if not SOURCE_IDENTITY_CSV.exists():
        fail(f"Required SHAPIROMART10 source identity file is missing: {SOURCE_IDENTITY_CSV}")
    rows = read_csv_rows(SOURCE_IDENTITY_CSV)
    tim_rows = [
        row
        for row in rows
        if row.get("file_type") == "TIM_TOA_file"
        and row.get("file_name") == "J0740+6620.cfr+19.tim"
    ]
    par_rows = [
        row
        for row in rows
        if row.get("file_type") == "PAR_timing_model_file"
        and row.get("file_name") == "J0740+6620.par"
    ]
    if len(tim_rows) != 1 or len(par_rows) != 1:
        fail(
            "Official TIM/PAR source identity is ambiguous or incomplete: "
            f"tim_candidates={len(tim_rows)}, par_candidates={len(par_rows)}."
        )
    return Path(tim_rows[0]["file_path"]), Path(par_rows[0]["file_path"]), tim_rows[0], par_rows[0]


def resolve_inputs(args: argparse.Namespace) -> tuple[Path, Path, dict[str, str], dict[str, str]]:
    tim_path, par_path, tim_identity, par_identity = source_identity_paths()
    if args.tim_file is not None:
        tim_path = args.tim_file
        tim_identity = {}
    if args.par_file is not None:
        par_path = args.par_file
        par_identity = {}
    if not tim_path.exists():
        fail(f"TIM input is missing: {tim_path}")
    if not par_path.exists():
        fail(f"PAR input is missing: {par_path}")
    return tim_path, par_path, tim_identity, par_identity


def single_status(path: Path) -> dict[str, str]:
    rows = read_csv_rows(path)
    if len(rows) != 1:
        fail(f"Expected exactly one status row in {path}, found {len(rows)}.")
    return rows[0]


def validate_shapiromart10_context() -> dict[str, Any]:
    final_10 = single_status(FINAL_STATUS_10_CSV)
    phase_update = single_status(PHASE_A_UPDATE_CSV)
    required = {
        "official_toa_file_identified": "yes",
        "official_par_file_identified": "yes",
        "official_pair_identity_supported": "yes",
        "ell1_parameter_basis_supported": "yes",
        "orbital_phase_axis_generated": "no",
    }
    for key, value in required.items():
        if final_10.get(key) != value:
            fail(f"SHAPIROMART10 final status mismatch for {key}: {final_10.get(key)!r}")
    update_required = {
        "official_tim_format": "FORMAT 1",
        "toa_field_position": "3",
        "toa_field_name": "TOA",
        "toa_field_unit": "MJD",
        "toa_file_axis_supported": "yes",
        "orbital_phase_definition_supported": "provisionally_supported",
    }
    for key, value in update_required.items():
        if phase_update.get(key) != value:
            fail(f"SHAPIROMART10 evidence update mismatch for {key}: {phase_update.get(key)!r}")
    return {"final_status": final_10, "phase_a_update": phase_update}


def input_identity_rows(
    tim_path: Path,
    par_path: Path,
    tim_identity: dict[str, str],
    par_identity: dict[str, str],
) -> list[dict[str, Any]]:
    return [
        {
            "input_role": "official_tim",
            "file_path": str(tim_path),
            "file_name": tim_path.name,
            "file_size_bytes": tim_path.stat().st_size,
            "sha256": file_sha256(tim_path),
            "official_identity_supported": tim_identity.get("identity_status", "manual_override_unchecked"),
            "format_or_model": "FORMAT 1",
            "notes": "Path resolved from SHAPIROMART10 source identity unless overridden by CLI.",
        },
        {
            "input_role": "official_par",
            "file_path": str(par_path),
            "file_name": par_path.name,
            "file_size_bytes": par_path.stat().st_size,
            "sha256": file_sha256(par_path),
            "official_identity_supported": par_identity.get("identity_status", "manual_override_unchecked"),
            "format_or_model": "ELL1 timing model expected",
            "notes": "Path resolved from SHAPIROMART10 source identity unless overridden by CLI.",
        },
    ]


def check_outputs(output_dir: Path, include_phase_export: bool, overwrite: bool) -> list[str]:
    expected = PHASE_OUTPUT_FILES if include_phase_export else BASE_OUTPUT_FILES
    allowed_existing = set(expected) | set(INSTALL_PROVENANCE_FILES)
    if output_dir.exists():
        files = [path.name for path in output_dir.iterdir() if path.is_file()]
        unexpected = sorted(set(files) - allowed_existing)
        if unexpected:
            fail("Unexpected existing file(s) in SHAPIROMART11 output dir: " + "; ".join(unexpected))
        existing_expected = sorted(set(files) & set(expected))
        if existing_expected and not overwrite:
            fail(
                "SHAPIROMART11 output file(s) already exist. Re-run with --overwrite "
                "to replace only the expected SHAPIROMART11 files: "
                + "; ".join(existing_expected)
            )
    return expected


def table_colnames(toas: Any) -> list[str]:
    return list(getattr(toas.table, "colnames", []))


def value_to_string(value: Any) -> str:
    if value is None:
        return ""
    try:
        return str(value.value)
    except Exception:
        return str(value)


def unit_to_string(value: Any) -> str:
    for attr in ("units", "unit"):
        unit = getattr(value, attr, None)
        if unit is not None:
            return str(unit)
    quantity = getattr(value, "quantity", None)
    if quantity is not None:
        unit = getattr(quantity, "unit", None)
        if unit is not None:
            return str(unit)
    return ""


def parameter_uncertainty(parameter: Any) -> str:
    for attr in ("uncertainty_value", "uncertainty"):
        value = getattr(parameter, attr, None)
        if value is not None:
            return value_to_string(value)
    return ""


def parameter_component(model: Any, parameter_name: str) -> str:
    for name, component in getattr(model, "components", {}).items():
        params = getattr(component, "params", [])
        if parameter_name in params:
            return name
    return ""


def model_parameter_rows(model: Any) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for name in REQUIRED_MODEL_PARAMETERS:
        parameter = getattr(model, name, None)
        present = parameter is not None
        rows.append(
            {
                "parameter_name": name,
                "parameter_value": value_to_string(parameter),
                "unit": unit_to_string(parameter),
                "frozen": str(getattr(parameter, "frozen", "")) if present else "",
                "uncertainty": parameter_uncertainty(parameter) if present else "",
                "model_component": parameter_component(model, name) if present else "",
                "required_for_phase": "yes" if name in PHASE_REQUIRED_PARAMETERS else "no",
                "present": "yes" if present else "no",
                "notes": "Read from loaded PINT model; no parameter was modified."
                if present
                else "Required parameter not present in loaded PINT model.",
            }
        )
    return rows


def model_psr_name(model: Any) -> str:
    for key in ("PSR", "PSRJ", "PSRB"):
        parameter = getattr(model, key, None)
        if parameter is not None:
            return value_to_string(parameter)
    return "unknown"


def ell1_confirmed(model: Any) -> bool:
    binary = getattr(model, "BINARY", None)
    binary_value = value_to_string(binary).upper()
    component_names = [name.upper() for name in getattr(model, "components", {})]
    return binary_value == "ELL1" or any("ELL1" in name for name in component_names)


def get_toa_count(toas: Any) -> int:
    try:
        return len(toas)
    except Exception:
        return len(toas.table)


def has_column(toas: Any, name: str) -> bool:
    return name in table_colnames(toas)


def column_item(column: Any, index: int) -> Any:
    try:
        return column[index]
    except Exception:
        return ""


def scalar_string(value: Any) -> str:
    try:
        if hasattr(value, "value"):
            return str(value.value)
        return str(value)
    except Exception:
        return ""


def time_scale_for_column(column: Any) -> str:
    scale = getattr(column, "scale", None)
    if scale:
        return str(scale)
    try:
        first = column[0]
        scale = getattr(first, "scale", None)
        if scale:
            return str(scale)
    except Exception:
        pass
    return ""


def numeric_column_values(modules: PintModules, column: Any) -> Any:
    np = modules.numpy
    try:
        return np.asarray(column, dtype=np.longdouble)
    except Exception:
        try:
            return np.asarray([float(item) for item in column], dtype=np.longdouble)
        except Exception as exc:
            raise RuntimeError(f"Unable to convert PINT time column to numeric values: {exc}") from exc


def parameter_days(modules: PintModules, parameter: Any) -> tuple[str, str]:
    if parameter is None:
        return "", ""
    quantity = getattr(parameter, "quantity", None)
    if quantity is not None:
        try:
            value = quantity.to(modules.astropy_units.day).value
            return str(value), "d"
        except Exception:
            pass
    return value_to_string(parameter), unit_to_string(parameter)


def tasc_scale(parameter: Any) -> str:
    for attr in ("time_scale", "scale"):
        scale = getattr(parameter, attr, None)
        if scale:
            return str(scale).lower()
    return ""


def try_direct_phase_method(modules: PintModules, model: Any, toas: Any) -> tuple[Any | None, str, str]:
    candidate_objects: list[tuple[str, Any]] = []
    for name, component in getattr(model, "components", {}).items():
        if "ELL1" in name.upper() or "BINARY" in name.upper():
            candidate_objects.append((name, component))
            binary_instance = getattr(component, "binary_instance", None)
            if binary_instance is not None:
                candidate_objects.append((f"{name}.binary_instance", binary_instance))

    for label, obj in candidate_objects:
        for method_name in ("orbital_phase", "binary_phase", "orbits"):
            method = getattr(obj, method_name, None)
            if method is None:
                continue
            try:
                values = method(toas)
            except TypeError:
                try:
                    values = method()
                except Exception:
                    continue
            except Exception:
                continue
            try:
                arr = modules.numpy.asarray(values, dtype=modules.numpy.longdouble)
            except Exception:
                continue
            if arr.size == get_toa_count(toas):
                return arr % 1, f"{label}.{method_name}", label
    return None, "", ""


def fallback_phase_from_processed_time(
    modules: PintModules, model: Any, toas: Any
) -> tuple[Any | None, str, str, str, str]:
    if not has_column(toas, "tdbld"):
        return None, "", "", "", "No PINT tdbld column available."
    tasc = getattr(model, "TASC", None)
    pb = getattr(model, "PB", None)
    tasc_value, tasc_unit = parameter_days(modules, tasc)
    pb_value, pb_unit = parameter_days(modules, pb)
    scale = tasc_scale(tasc)
    if not tasc_value or not pb_value:
        return None, "", "", scale, "TASC or PB value unavailable in loaded model."
    if scale and scale != "tdb":
        return None, "", "", scale, f"TASC scale is {scale}, not TDB."

    model_time = numeric_column_values(modules, toas.table["tdbld"])
    tasc_days = modules.numpy.longdouble(tasc_value)
    pb_days = modules.numpy.longdouble(pb_value)
    if pb_days == 0:
        return None, "", "", scale, "PB is zero."
    cycles = (model_time - tasc_days) / pb_days
    phase = modules.numpy.mod(cycles, 1)
    return phase, tasc_value, pb_value, scale or "tdb", "PINT processed tdbld fallback."


def phase_assessment(
    modules: PintModules, model: Any, toas: Any
) -> tuple[dict[str, Any], Any | None, str]:
    tasc = getattr(model, "TASC", None)
    pb = getattr(model, "PB", None)
    tasc_value, _ = parameter_days(modules, tasc)
    pb_value, pb_unit = parameter_days(modules, pb)
    tasc_scale_value = tasc_scale(tasc)
    component = parameter_component(model, "TASC") or parameter_component(model, "PB")

    phase, direct_method, direct_component = try_direct_phase_method(modules, model, toas)
    method = ""
    method_detail = ""
    notes = ""
    time_input = ""
    if phase is not None:
        method = "pint_direct_orbital_phase"
        method_detail = direct_method
        component = direct_component or component
        time_input = "PINT TOAs object"
        notes = "Orbital phase returned by a PINT binary-model method."
    else:
        phase, tasc_value, pb_value, tasc_scale_value, notes = fallback_phase_from_processed_time(
            modules, model, toas
        )
        if phase is not None:
            method = "pint_processed_tdb_fallback"
            method_detail = "fractional_part((tdbld - TASC) / PB)"
            time_input = "PINT processed tdbld"
        else:
            method = "phase_generation_unresolved"
            method_detail = "none"
            time_input = "none"

    if phase is None:
        return (
            {
                "phase_method": method,
                "pint_function_or_fallback": method_detail,
                "model_component": component,
                "time_input": time_input,
                "tasc_value": tasc_value,
                "tasc_scale": tasc_scale_value,
                "pb_value": pb_value,
                "pb_unit": pb_unit,
                "phase_range": "",
                "phase_zero_definition": "ELL1 TASC ascending-node epoch; no upper-conjunction assignment.",
                "phase_generated": "no",
                "phase_count": "0",
                "finite_phase_count": "0",
                "minimum_phase": "",
                "maximum_phase": "",
                "definition_status": "phase_generation_unresolved",
                "main_gap": NO_PHASE_GAP,
                "notes": notes,
            },
            None,
            method,
        )

    finite = modules.numpy.isfinite(phase)
    finite_count = int(modules.numpy.count_nonzero(finite))
    min_phase = str(float(modules.numpy.min(phase[finite]))) if finite_count else ""
    max_phase = str(float(modules.numpy.max(phase[finite]))) if finite_count else ""
    return (
        {
            "phase_method": method,
            "pint_function_or_fallback": method_detail,
            "model_component": component,
            "time_input": time_input,
            "tasc_value": tasc_value,
            "tasc_scale": tasc_scale_value or "tdb",
            "pb_value": pb_value,
            "pb_unit": pb_unit,
            "phase_range": "[0,1)",
            "phase_zero_definition": "ELL1 TASC ascending-node epoch; no upper-conjunction assignment.",
            "phase_generated": "yes",
            "phase_count": str(len(phase)),
            "finite_phase_count": str(finite_count),
            "minimum_phase": min_phase,
            "maximum_phase": max_phase,
            "definition_status": "phase_axis_reconstructed",
            "main_gap": "",
            "notes": notes,
        },
        phase,
        method,
    )


def toa_processing_row(toas: Any) -> dict[str, Any]:
    cols = table_colnames(toas)
    original_scale = time_scale_for_column(toas.table["mjd"]) if "mjd" in cols else ""
    processed_scale = "tdb" if "tdbld" in cols or "tdb" in cols else ""
    bary_cols = [name for name in cols if name in {"tdb", "tdbld", "ssb_obs_pos", "ssb_obs_vel"}]
    clock_cols = [name for name in cols if "clk" in name.lower() or "clock" in name.lower()]
    return {
        "toa_time_column": "mjd",
        "original_scale": original_scale,
        "processed_scale": processed_scale,
        "clock_corrected": "yes" if clock_cols or processed_scale else "unresolved",
        "barycentric_time_available": "yes" if "tdbld" in cols or "tdb" in cols else "no",
        "model_time_available": "yes" if "tdbld" in cols else "no",
        "processing_status": "pint_toa_processing_supported"
        if processed_scale
        else "pint_toa_processing_unresolved",
        "notes": "Columns: " + ",".join(cols),
    }


def get_table_string(toas: Any, column_name: str, index: int) -> str:
    if not has_column(toas, column_name):
        return ""
    return scalar_string(column_item(toas.table[column_name], index))


def get_time_mjd(toas: Any, index: int) -> str:
    if not has_column(toas, "mjd"):
        return ""
    item = column_item(toas.table["mjd"], index)
    for attr in ("mjd", "value"):
        value = getattr(item, attr, None)
        if value is not None:
            return str(value)
    return scalar_string(item)


def get_frequency_mhz(toas: Any, index: int) -> str:
    if not has_column(toas, "freq"):
        return ""
    item = column_item(toas.table["freq"], index)
    try:
        if hasattr(item, "to"):
            return str(item.to("MHz").value)
    except Exception:
        pass
    return scalar_string(item)


def phase_export_rows(
    toas: Any,
    phase: Any,
    method: str,
    model: Any,
    phase_row: dict[str, Any],
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    count = len(phase)
    for idx in range(count):
        rows.append(
            {
                "source_row_index": idx,
                "source_filename": get_table_string(toas, "name", idx)
                or get_table_string(toas, "flags", idx),
                "observatory": get_table_string(toas, "obs", idx),
                "observing_frequency_mhz": get_frequency_mhz(toas, idx),
                "toa_mjd_file": get_time_mjd(toas, idx),
                "toa_time_scale": time_scale_for_column(toas.table["mjd"])
                if has_column(toas, "mjd")
                else "",
                "processed_time_value": get_table_string(toas, "tdbld", idx)
                or get_table_string(toas, "tdb", idx),
                "processed_time_scale": "tdb",
                "orbital_phase": str(float(phase[idx])),
                "phase_method": method,
                "model_name": model_psr_name(model),
                "tasc_value": phase_row.get("tasc_value", ""),
                "pb_value": phase_row.get("pb_value", ""),
                "calculation_status": "reconstructed",
                "notes": "Phase derived from PINT-loaded model and PINT-processed TOA table.",
            }
        )
    return rows


def final_status_row(
    environment: dict[str, str],
    model_loaded: bool,
    toas_loaded: bool,
    ell1: bool,
    phase_row: dict[str, Any],
    processing_row: dict[str, Any],
    include_phase_export: bool,
    load_status: str,
) -> dict[str, Any]:
    phase_generated = phase_row.get("phase_generated", "no") == "yes"
    if not environment["environment_status"] == "pulsar_pint_available":
        status = "pint_not_available"
        gap = NO_ENV_GAP
        next_action = INSTALL_NEXT_ACTION
    elif not (model_loaded and toas_loaded):
        status = "official_pair_load_failed"
        gap = "PINT did not load the official TIM/PAR pair."
        next_action = "Inspect the load warnings and errors before retrying the same official input pair."
    elif not phase_generated:
        status = "pint_load_supported_phase_unresolved"
        gap = phase_row.get("main_gap", NO_PHASE_GAP)
        next_action = PHASE_NEXT_ACTION
    else:
        status = "orbital_phase_axis_reconstructed"
        gap = ""
        next_action = SUCCESS_NEXT_ACTION
    return {
        "research_block": "QSB-SHAPIROMART11",
        "official_pair_used": "yes" if model_loaded or toas_loaded else "not_loaded",
        "pint_available": "yes"
        if environment["environment_status"] == "pulsar_pint_available"
        else "no",
        "model_loaded": "yes" if model_loaded else "no",
        "toas_loaded": "yes" if toas_loaded else "no",
        "ell1_model_confirmed": "yes" if ell1 else "no",
        "tasc_available": "yes" if phase_row.get("tasc_value") else "no",
        "pb_available": "yes" if phase_row.get("pb_value") else "no",
        "clock_correction_status": load_status,
        "model_consistent_time_available": processing_row.get("model_time_available", "no"),
        "orbital_phase_definition_supported": "yes"
        if phase_generated
        else "provisional_or_unresolved",
        "orbital_phase_generated": "yes" if phase_generated else "no",
        "orbital_phase_exported": "yes" if phase_generated and include_phase_export else "no",
        "model_fit_performed": "no",
        "model_parameters_modified": "no",
        "shapiro_delay_calculated": "no",
        "residual_analysis_performed": "no",
        "tim_token_003_used": "no",
        "record_index_used_as_time": "no",
        "database_access": "none",
        "database_modified": "no",
        "additional_gate_created": "no",
        "final_status": status,
        "main_remaining_gap": gap,
        "recommended_next_action": next_action,
    }


def readout_text(
    timestamp: str,
    tim_path: Path,
    par_path: Path,
    environment: dict[str, str],
    load_row: dict[str, Any],
    phase_row: dict[str, Any],
    final_row: dict[str, Any],
    warnings_list: list[str],
    errors_list: list[str],
    resource_records: list[dict[str, Any]],
    include_phase_export: bool,
) -> str:
    resources = "\n".join(
        "- {provider}: {url}; cache={local_cache_path}; size_bytes={file_size_bytes}; "
        "sha256={sha256}; status={retrieval_status}".format(**record)
        for record in resource_records
    )
    return f"""# QSB-SHAPIROMART11 Controlled PINT Reconstruction

## 1. Purpose

Read the official J0740 TIM/PAR pair with pulsar-timing PINT and document
whether a reproducible model-consistent orbital-phase axis can be reconstructed.

## 2. Input Pair

```text
tim_file = {tim_path}
par_file = {par_path}
official_pair_used = {final_row['official_pair_used']}
```

## 3. Software Environment

```text
timestamp_utc = {timestamp}
python_version = {environment['python_version']}
pint_version = {environment['pint_version']}
astropy_version = {environment['astropy_version']}
numpy_version = {environment['numpy_version']}
platform = {environment['platform']}
ephemeris_requested = {environment['ephemeris_requested']}
ephemeris_used = {environment['ephemeris_used']}
clock_data_source = {environment['clock_data_source']}
environment_status = {environment['environment_status']}
```

## 4. PINT Model Load

```text
model_loaded = {load_row['model_loaded']}
parser_format = {load_row['parser_format']}
```

## 5. PINT TOA Load

```text
toas_loaded = {load_row['toas_loaded']}
toa_count = {load_row['toa_count']}
```

## 6. Clock And Time Processing

```text
clock_corrections_applied = {load_row['clock_corrections_applied']}
clock_correction_status = {load_row['clock_correction_status']}
barycentric_columns_available = {load_row['barycentric_columns_available']}
```

Resource records observed in the Astropy cache after the run:

```text
{resources if resources else 'none'}
```

## 7. ELL1 Parameter Basis

```text
ell1_model_confirmed = {final_row['ell1_model_confirmed']}
tasc_available = {final_row['tasc_available']}
pb_available = {final_row['pb_available']}
```

## 8. Orbital-Phase Method

```text
phase_method = {phase_row['phase_method']}
pint_function_or_fallback = {phase_row['pint_function_or_fallback']}
time_input = {phase_row['time_input']}
phase_zero_definition = {phase_row['phase_zero_definition']}
```

## 9. Reconstruction Result

```text
orbital_phase_generated = {final_row['orbital_phase_generated']}
phase_count = {phase_row['phase_count']}
finite_phase_count = {phase_row['finite_phase_count']}
minimum_phase = {phase_row['minimum_phase']}
maximum_phase = {phase_row['maximum_phase']}
final_status = {final_row['final_status']}
```

## 10. Export Status

```text
include_phase_export = {str(include_phase_export).lower()}
orbital_phase_exported = {final_row['orbital_phase_exported']}
```

## 11. Remaining Gap

{final_row['main_remaining_gap']}

## 12. Limitations

No model fit was performed. No model parameter was modified. No residual
analysis was performed. No Shapiro calculation was performed. No database was
opened. The internal token tim_token_003 was not used, and no source row index
was used as a time value.

Warnings:

```text
{chr(10).join(warnings_list) if warnings_list else 'none'}
```

Errors:

```text
{chr(10).join(errors_list) if errors_list else 'none'}
```
"""


def write_outputs(
    args: argparse.Namespace,
    timestamp: str,
    expected_outputs: list[str],
    tim_path: Path,
    par_path: Path,
    environment: dict[str, str],
    input_rows: list[dict[str, Any]],
    load_row: dict[str, Any],
    parameter_rows: list[dict[str, Any]],
    processing_row: dict[str, Any],
    phase_row: dict[str, Any],
    final_row: dict[str, Any],
    warnings_list: list[str],
    errors_list: list[str],
    phase_export: list[dict[str, Any]],
    shapiromart10_context: dict[str, Any],
    resource_records: list[dict[str, Any]],
) -> None:
    args.output_dir.mkdir(parents=True, exist_ok=True)
    write_csv(args.output_dir / ENVIRONMENT_CSV, [environment], ENVIRONMENT_FIELDS)
    write_csv(args.output_dir / INPUT_IDENTITY_CSV, input_rows, INPUT_IDENTITY_FIELDS)
    write_csv(args.output_dir / PINT_LOAD_ASSESSMENT_CSV, [load_row], PINT_LOAD_FIELDS)
    write_csv(
        args.output_dir / MODEL_PARAMETER_ASSESSMENT_CSV,
        parameter_rows,
        MODEL_PARAMETER_FIELDS,
    )
    write_csv(
        args.output_dir / TOA_PROCESSING_ASSESSMENT_CSV,
        [processing_row],
        TOA_PROCESSING_FIELDS,
    )
    write_csv(
        args.output_dir / ORBITAL_PHASE_ASSESSMENT_CSV,
        [phase_row],
        ORBITAL_PHASE_FIELDS,
    )
    write_csv(args.output_dir / FINAL_STATUS_CSV, [final_row], FINAL_STATUS_FIELDS)
    if args.include_phase_export:
        write_csv(
            args.output_dir / TOA_ORBITAL_PHASE_CSV,
            phase_export,
            TOA_ORBITAL_PHASE_FIELDS,
        )

    readout = readout_text(
        timestamp,
        tim_path,
        par_path,
        environment,
        load_row,
        phase_row,
        final_row,
        warnings_list,
        errors_list,
        resource_records,
        args.include_phase_export,
    )
    (args.output_dir / READOUT_MD).write_text(readout, encoding="utf-8")

    summary = {
        "research_block": "QSB-SHAPIROMART11",
        "script": SCRIPT_NAME,
        "timestamp_utc": timestamp,
        "output_dir": str(args.output_dir),
        "expected_outputs": expected_outputs,
        "include_phase_export": args.include_phase_export,
        "inputs": {
            "tim_file": str(tim_path),
            "par_file": str(par_path),
            "source_identity_csv": str(SOURCE_IDENTITY_CSV),
        },
        "environment": environment,
        "load_assessment": load_row,
        "toa_processing_assessment": processing_row,
        "orbital_phase_assessment": phase_row,
        "final_status": final_row,
        "warnings": warnings_list,
        "errors": errors_list,
        "resources": resource_records,
        "shapiromart10_context": shapiromart10_context,
        "boundaries": {
            "model_fit_performed": "no",
            "model_parameters_modified": "no",
            "shapiro_delay_calculated": "no",
            "residual_analysis_performed": "no",
            "tim_token_003_used": "no",
            "record_index_used_as_time": "no",
            "database_access": "none",
            "database_modified": "no",
            "additional_gate_created": "no",
        },
    }
    write_json(args.output_dir / SUMMARY_JSON, summary)


def run(args: argparse.Namespace) -> dict[str, Any]:
    timestamp = utc_now()
    shapiromart10_context = validate_shapiromart10_context()
    tim_path, par_path, tim_identity, par_identity = resolve_inputs(args)
    input_rows = input_identity_rows(tim_path, par_path, tim_identity, par_identity)

    environment, modules, import_error = import_environment(args.ephem)
    if modules is None:
        fail(
            "Pulsar-timing PINT is not available; no SHAPIROMART11 run outputs "
            f"were written. Import error: {import_error}"
        )

    expected_outputs = check_outputs(args.output_dir, args.include_phase_export, args.overwrite)

    get_model = getattr(modules.pint_models, "get_model")
    get_toas = getattr(modules.pint_toa, "get_TOAs")
    model = None
    toas = None
    warnings_list: list[str] = []
    errors_list: list[str] = []
    model_loaded = False
    toas_loaded = False

    with warnings.catch_warnings(record=True) as captured:
        warnings.simplefilter("always")
        try:
            model = get_model(str(par_path))
            model_loaded = True
            try:
                toas = get_toas(str(tim_path), model=model, ephem=args.ephem)
            except TypeError:
                toas = get_toas(str(tim_path), ephem=args.ephem)
            toas_loaded = True
        except Exception as exc:
            errors_list.append(f"{type(exc).__name__}: {exc}")
        warnings_list.extend(str(item.message) for item in captured)

    if not (model_loaded and toas_loaded):
        fail(
            "PINT did not load the official pair; no SHAPIROMART11 run outputs "
            "were written. Error(s): " + "; ".join(errors_list)
        )

    toa_count = get_toa_count(toas)
    colnames = table_colnames(toas)
    clock_columns = [name for name in colnames if "clk" in name.lower() or "clock" in name.lower()]
    barycentric_columns = [
        name for name in colnames if name in {"tdb", "tdbld", "ssb_obs_pos", "ssb_obs_vel"}
    ]
    environment["ephemeris_used"] = str(args.ephem)
    environment["clock_data_source"] = (
        "PINT TOA processing columns: " + ",".join(clock_columns)
        if clock_columns
        else "No explicit clock column name detected in PINT TOA table."
    )

    parameter_rows = model_parameter_rows(model)
    processing_row = toa_processing_row(toas)
    phase_row, phase_values, method = phase_assessment(modules, model, toas)
    ell1 = ell1_confirmed(model)
    load_status = "pint_load_supported"
    load_row = {
        "model_loaded": "yes",
        "toas_loaded": "yes",
        "toa_count": str(toa_count),
        "parser_format": "FORMAT 1",
        "clock_corrections_applied": processing_row["clock_corrected"],
        "clock_correction_status": load_status,
        "barycentric_columns_available": ",".join(barycentric_columns) if barycentric_columns else "none",
        "load_status": load_status,
        "warning_count": str(len(warnings_list)),
        "error_count": str(len(errors_list)),
        "notes": "API calls: pint.models.get_model(...); pint.toa.get_TOAs(...).",
    }
    final_row = final_status_row(
        environment,
        model_loaded,
        toas_loaded,
        ell1,
        phase_row,
        processing_row,
        args.include_phase_export,
        load_status,
    )

    phase_export: list[dict[str, Any]] = []
    if args.include_phase_export:
        if phase_values is None:
            fail("--include-phase-export was requested, but no phase values were generated.")
        phase_export = phase_export_rows(toas, phase_values, method, model, phase_row)

    resource_records = collect_astropy_resource_records()

    write_outputs(
        args,
        timestamp,
        expected_outputs,
        tim_path,
        par_path,
        environment,
        input_rows,
        load_row,
        parameter_rows,
        processing_row,
        phase_row,
        final_row,
        warnings_list,
        errors_list,
        phase_export,
        shapiromart10_context,
        resource_records,
    )

    return {
        "result": final_row["final_status"],
        "output_dir": str(args.output_dir),
        "orbital_phase_generated": final_row["orbital_phase_generated"],
        "orbital_phase_exported": final_row["orbital_phase_exported"],
        "toa_count": load_row["toa_count"],
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Run a controlled read-only PINT reconstruction for the official "
            "J0740 TIM/PAR pair."
        )
    )
    parser.add_argument("--tim-file", type=Path, default=None)
    parser.add_argument("--par-file", type=Path, default=None)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--ephem", default="DE436")
    parser.add_argument("--include-phase-export", action="store_true")
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Replace only expected SHAPIROMART11 output files in the output directory.",
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
