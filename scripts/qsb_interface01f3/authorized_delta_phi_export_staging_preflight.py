#!/usr/bin/env python3
"""Authorized raw/wrapped delta_phi export preflight; blocks cleanly without a manifest."""

from __future__ import annotations

import csv
import hashlib
import json
import math
import sqlite3
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


REPO = Path(__file__).resolve().parents[2]
SOURCE_ROOT = (REPO / "../interference_kernel_v1").resolve()
F2_DIR = REPO / "runs/QSB-INTERFACE01F2/interference_kernel_delta_phi_export_contract"
F2_MANIFEST = F2_DIR / "01_f2_run_manifest.json"
INPUT_DIR = REPO / "runs/QSB-INTERFACE01F3/input_manifest"
JSON_MANIFEST = INPUT_DIR / "interface01f3_delta_phi_input_manifest.json"
YAML_MANIFEST = INPUT_DIR / "interface01f3_delta_phi_input_manifest.yaml"
OUTPUT = REPO / "runs/QSB-INTERFACE01F3/authorized_delta_phi_export_staging_preflight"
CLAIM = (
    "INTERFACE01-F3 is an authorized export/staging preflight for raw/wrapped delta_phi based on "
    "interference_kernel_v1 source logic. It may stage a source only if the F2 contract, F2H review, "
    "input manifest, provenance hashes, wrapping convention, unit convention, and validation checks pass. "
    "It does not run a Minimaltest and does not claim physical evidence beyond the staged source status."
)
SOURCE_SPECS = [
    (SOURCE_ROOT / "models/action_phase.py", "phase_generator"),
    (SOURCE_ROOT / "models/phase_generators.py", "phase_generator"),
    (SOURCE_ROOT / "models/interference_kernel.py", "delta_phi_source_logic"),
    (SOURCE_ROOT / "models/datatypes.py", "input_and_result_datatypes"),
]
STATIC_FIELDS = [
    "export_id", "source_mode", "run_id", "state_i", "state_j", "pair_i", "pair_j",
    "phi_i", "phi_j", "raw_delta_phi_ij", "wrapped_delta_phi_ij", "wrapping_interval",
    "angle_unit", "dimension_status", "pair_mask", "diagonal_policy", "source_code_hash",
    "config_hash", "input_hash", "authorization_status",
]
SPATIAL_FIELDS = [
    "export_id", "source_mode", "run_id", "state_i", "state_j", "pair_i", "pair_j",
    "x_index", "x_value", "x_unit", "x_weight", "phi_i_x", "phi_j_x",
    "raw_delta_phi_ij_x", "wrapped_delta_phi_ij_x", "wrapping_interval", "angle_unit",
    "dimension_status", "pair_mask", "diagonal_policy", "source_code_hash", "config_hash",
    "input_hash", "authorization_status",
]
REQUIRED_MANIFEST_FIELDS = [
    "authorization_status", "source_mode", "phase_source", "phase_regime", "hbar",
    "wrapping_interval", "angle_unit", "dimension_status", "zero_diagonal_policy",
    "pair_diagonal_policy", "state_labels", "p_values", "E_values", "t_value",
    "config_reference", "config_hash", "input_hash", "human_authorizer",
    "authorization_note", "post_hoc_tuning_lock", "run_id",
]


def write_csv(path: Path, fields: list[str], rows: list[dict[str, Any]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def stable_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def stable_hash(value: Any) -> str:
    return hashlib.sha256(stable_json(value).encode("utf-8")).hexdigest()


def template_payload() -> dict[str, Any]:
    return {
        "_template_note": "Complete and human-authorize this manifest before rerunning in a fresh F3 output path; null arrays are not data.",
        "authorization_status": "not_authorized_template",
        "source_mode": None,
        "phase_source": None,
        "phase_regime": None,
        "hbar": None,
        "wrapping_interval": "[-pi, pi)",
        "angle_unit": "rad",
        "dimension_status": "dimensionless_angle",
        "zero_diagonal_policy": "zero",
        "pair_diagonal_policy": "include_with_mask_false",
        "ordered_pairs": True,
        "run_id": None,
        "state_labels": [],
        "p_values": [],
        "E_values": [],
        "t_value": None,
        "x_values": [],
        "x_unit": None,
        "x_weights": None,
        "phases": None,
        "phase_field": None,
        "phase_offsets": None,
        "seed": None,
        "noise_sigma": 0.0,
        "chirp_strength": 0.15,
        "quadratic_strength": 0.08,
        "config_reference": "embedded_manifest_config",
        "config_hash": None,
        "input_hash": None,
        "human_authorizer": None,
        "authorization_note": None,
        "post_hoc_tuning_lock": True,
    }


def create_template_if_missing() -> bool:
    if JSON_MANIFEST.exists() or YAML_MANIFEST.exists():
        return False
    INPUT_DIR.mkdir(parents=True, exist_ok=True)
    JSON_MANIFEST.write_text(json.dumps(template_payload(), indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return True


def load_manifest(path: Path) -> dict[str, Any]:
    if path.suffix.lower() == ".json":
        value = json.loads(path.read_text(encoding="utf-8"))
    else:
        try:
            import yaml  # type: ignore
        except ImportError as error:
            raise ValueError("YAML manifest requires PyYAML; provide JSON or install reviewed dependency.") from error
        value = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError("Input manifest root must be an object/mapping.")
    return value


def config_subset(manifest: dict[str, Any]) -> dict[str, Any]:
    keys = [
        "source_mode", "phase_source", "phase_regime", "hbar", "wrapping_interval",
        "angle_unit", "dimension_status", "zero_diagonal_policy", "pair_diagonal_policy",
        "ordered_pairs", "seed", "noise_sigma", "chirp_strength", "quadratic_strength",
        "config_reference", "post_hoc_tuning_lock",
    ]
    return {key: manifest.get(key) for key in keys}


def normalized_input(manifest: dict[str, Any]) -> dict[str, Any]:
    volatile = {"created_at", "created_at_utc", "timestamp", "timestamp_utc", "input_hash"}
    return {key: value for key, value in manifest.items() if key not in volatile and not key.startswith("_template")}


def validate_manifest(manifest: dict[str, Any], supplied: bool) -> tuple[list[dict[str, str]], bool, str, str]:
    rows: list[dict[str, str]] = []
    critical_ok = supplied

    def add(field: str, required: bool, valid: bool, observed: Any, notes: str) -> None:
        nonlocal critical_ok
        if required and not valid:
            critical_ok = False
        rows.append({
            "field_name": field, "required": "yes" if required else "conditional",
            "observed": "missing" if observed is None or observed == "" or observed == [] else str(observed)[:240],
            "status": "pass" if valid else "missing_or_invalid",
            "blocking_for_export": "yes" if required and not valid else "no",
            "notes": notes,
        })

    for field in REQUIRED_MANIFEST_FIELDS:
        value = manifest.get(field)
        add(field, True, value is not None and value != "" and value != [], value, "Required manifest field.")

    add("authorization_status_value", True, manifest.get("authorization_status") == "human_authorized_for_interface01_export", manifest.get("authorization_status"), "Must be human_authorized_for_interface01_export.")
    add("source_mode_value", True, manifest.get("source_mode") in {"static_pair_delta_phi", "spatial_pair_delta_phi_x"}, manifest.get("source_mode"), "Only F2H-approved source modes.")
    add("phase_source_value", True, manifest.get("phase_source") in {"explicit_static_phases", "local_plane_wave_phase", "generate_phase_field", "explicit_phase_field"}, manifest.get("phase_source"), "Only approved phase-source types.")
    add("wrapping_interval_value", True, manifest.get("wrapping_interval") == "[-pi, pi)", manifest.get("wrapping_interval"), "F2H-fixed interval.")
    add("angle_unit_value", True, manifest.get("angle_unit") == "rad", manifest.get("angle_unit"), "F2H-fixed angle unit.")
    add("dimension_status_value", True, manifest.get("dimension_status") == "dimensionless_angle", manifest.get("dimension_status"), "F2H-fixed dimension status.")
    add("post_hoc_tuning_lock_value", True, manifest.get("post_hoc_tuning_lock") is True, manifest.get("post_hoc_tuning_lock"), "Must be boolean true.")
    add("pair_diagonal_policy_value", True, manifest.get("pair_diagonal_policy") in {"include_with_mask_false", "exclude"}, manifest.get("pair_diagonal_policy"), "Diagonal pairs are not physical pairs.")

    labels = manifest.get("state_labels") if isinstance(manifest.get("state_labels"), list) else []
    n = len(labels)
    p_values = manifest.get("p_values") if isinstance(manifest.get("p_values"), list) else []
    e_values = manifest.get("E_values") if isinstance(manifest.get("E_values"), list) else []
    add("state_vector_lengths", True, n > 0 and len(p_values) == n and len(e_values) == n, f"N={n};p={len(p_values)};E={len(e_values)}", "State labels, p and E arrays must share nonzero length.")

    mode = manifest.get("source_mode")
    phase_source = manifest.get("phase_source")
    if mode == "static_pair_delta_phi":
        phases = manifest.get("phases")
        add("phases", True, phase_source == "explicit_static_phases" and isinstance(phases, list) and len(phases) == n and n > 0, phases, "Static mode requires explicit_static_phases and N phases.")
    if mode == "spatial_pair_delta_phi_x":
        x_values = manifest.get("x_values") if isinstance(manifest.get("x_values"), list) else []
        add("x_values", True, len(x_values) > 0, f"length={len(x_values)}", "Spatial mode requires nonempty grid.")
        add("x_unit", True, bool(manifest.get("x_unit")), manifest.get("x_unit"), "Spatial export must label x units/status.")
        if phase_source == "explicit_phase_field":
            phase_field = manifest.get("phase_field")
            valid = isinstance(phase_field, list) and len(phase_field) == n and all(isinstance(row, list) and len(row) == len(x_values) for row in phase_field)
            add("phase_field", True, valid, "provided" if phase_field else None, "Explicit phase field must have shape N x Nx.")
        elif phase_source in {"local_plane_wave_phase", "generate_phase_field"}:
            add("phase_generation_inputs", True, n > 0 and len(x_values) > 0 and isinstance(manifest.get("hbar"), (int, float)) and manifest.get("hbar") != 0 and isinstance(manifest.get("t_value"), (int, float)), "checked", "Generator inputs must be numeric and complete.")
            if phase_source == "generate_phase_field" and manifest.get("phase_regime") in {"random", "random_field", "noisy_db", "quadratic"}:
                add("seed", True, isinstance(manifest.get("seed"), int), manifest.get("seed"), "Stochastic regime requires integer seed.")
        else:
            add("spatial_phase_source_compatibility", True, False, phase_source, "Spatial mode requires explicit_phase_field or approved generator.")

    computed_input_hash = stable_hash(normalized_input(manifest)) if supplied else ""
    reference = manifest.get("config_reference")
    if supplied and isinstance(reference, str) and reference not in {"", "embedded_manifest_config"}:
        config_path = Path(reference)
        if not config_path.is_absolute():
            config_path = REPO / config_path
        computed_config_hash = sha256_file(config_path) if config_path.is_file() else ""
    else:
        computed_config_hash = stable_hash(config_subset(manifest)) if supplied else ""
    provided_config_hash = manifest.get("config_hash")
    provided_input_hash = manifest.get("input_hash")
    config_valid = bool(computed_config_hash) and (not provided_config_hash or provided_config_hash == computed_config_hash)
    input_valid = bool(computed_input_hash) and (not provided_input_hash or provided_input_hash == computed_input_hash)
    add("config_hash_validation", True, config_valid, computed_config_hash or None, "Computed from external config or normalized embedded config; supplied value must match.")
    add("input_hash_validation", True, input_valid, computed_input_hash or None, "Computed from normalized manifest including authorization fields; supplied value must match.")
    return rows, critical_ok, computed_config_hash, computed_input_hash


def wrap(raw: float) -> float:
    return ((raw + math.pi) % (2.0 * math.pi)) - math.pi


def generate_exports(manifest: dict[str, Any], source_hash: str, config_hash: str,
                     input_hash: str) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    import numpy as np

    labels = [str(value) for value in manifest["state_labels"]]
    n = len(labels)
    mode = manifest["source_mode"]
    diagonal_policy = manifest["pair_diagonal_policy"]
    auth = manifest["authorization_status"]
    run_id = str(manifest["run_id"])
    static_rows: list[dict[str, Any]] = []
    spatial_rows: list[dict[str, Any]] = []

    if mode == "static_pair_delta_phi":
        phases = np.asarray(manifest["phases"], dtype=float)
        raw = phases[:, None] - phases[None, :]
        for i in range(n):
            for j in range(n):
                if i == j and diagonal_policy == "exclude":
                    continue
                pair_mask = i != j
                static_rows.append({
                    "export_id": f"{run_id}:static:{i}:{j}", "source_mode": mode, "run_id": run_id,
                    "state_i": labels[i], "state_j": labels[j], "pair_i": i, "pair_j": j,
                    "phi_i": float(phases[i]), "phi_j": float(phases[j]),
                    "raw_delta_phi_ij": float(raw[i, j]), "wrapped_delta_phi_ij": wrap(float(raw[i, j])),
                    "wrapping_interval": "[-pi, pi)", "angle_unit": "rad", "dimension_status": "dimensionless_angle",
                    "pair_mask": str(pair_mask).lower(), "diagonal_policy": diagonal_policy,
                    "source_code_hash": source_hash, "config_hash": config_hash, "input_hash": input_hash,
                    "authorization_status": auth,
                })
    else:
        x = np.asarray(manifest["x_values"], dtype=float)
        phase_source = manifest["phase_source"]
        if phase_source == "explicit_phase_field":
            phase_field = np.asarray(manifest["phase_field"], dtype=float)
        else:
            sys.path.insert(0, str(SOURCE_ROOT))
            from models.action_phase import local_plane_wave_phase
            from models.datatypes import StateEnsemble
            from models.phase_generators import generate_phase_field
            ensemble = StateEnsemble(
                x=x, t=float(manifest["t_value"]), p=np.asarray(manifest["p_values"], dtype=float),
                E=np.asarray(manifest["E_values"], dtype=float), labels=labels,
            )
            offsets = manifest.get("phase_offsets")
            if phase_source == "local_plane_wave_phase":
                phase_field = local_plane_wave_phase(
                    ensemble, hbar=float(manifest["hbar"]),
                    phase_offsets=np.asarray(offsets, dtype=float) if offsets is not None else None,
                )
            else:
                phase_field = generate_phase_field(
                    ensemble, regime=str(manifest["phase_regime"]), hbar=float(manifest["hbar"]),
                    seed=int(manifest.get("seed") or 0), noise_sigma=float(manifest.get("noise_sigma", 0.0)),
                    chirp_strength=float(manifest.get("chirp_strength", 0.15)),
                    quadratic_strength=float(manifest.get("quadratic_strength", 0.08)),
                )
        raw = phase_field[:, None, :] - phase_field[None, :, :]
        supplied_weights = manifest.get("x_weights")
        if supplied_weights is None:
            weights = np.ones(len(x), dtype=float) / len(x)
        else:
            weights = np.asarray(supplied_weights, dtype=float)
            weights = weights / np.sum(weights)
        for i in range(n):
            for j in range(n):
                if i == j and diagonal_policy == "exclude":
                    continue
                pair_mask = i != j
                for k in range(len(x)):
                    value = float(raw[i, j, k])
                    spatial_rows.append({
                        "export_id": f"{run_id}:spatial:{i}:{j}:{k}", "source_mode": mode, "run_id": run_id,
                        "state_i": labels[i], "state_j": labels[j], "pair_i": i, "pair_j": j,
                        "x_index": k, "x_value": float(x[k]), "x_unit": manifest["x_unit"],
                        "x_weight": float(weights[k]), "phi_i_x": float(phase_field[i, k]),
                        "phi_j_x": float(phase_field[j, k]), "raw_delta_phi_ij_x": value,
                        "wrapped_delta_phi_ij_x": wrap(value), "wrapping_interval": "[-pi, pi)",
                        "angle_unit": "rad", "dimension_status": "dimensionless_angle",
                        "pair_mask": str(pair_mask).lower(), "diagonal_policy": diagonal_policy,
                        "source_code_hash": source_hash, "config_hash": config_hash, "input_hash": input_hash,
                        "authorization_status": auth,
                    })
    return static_rows, spatial_rows


SCHEMA = """PRAGMA foreign_keys = ON;

CREATE TABLE stg_delta_phi_static (
  export_id TEXT PRIMARY KEY, source_mode TEXT NOT NULL, run_id TEXT NOT NULL,
  state_i TEXT NOT NULL, state_j TEXT NOT NULL, pair_i INTEGER NOT NULL, pair_j INTEGER NOT NULL,
  phi_i REAL NOT NULL, phi_j REAL NOT NULL, raw_delta_phi_ij REAL NOT NULL,
  wrapped_delta_phi_ij REAL NOT NULL, wrapping_interval TEXT NOT NULL, angle_unit TEXT NOT NULL,
  dimension_status TEXT NOT NULL, pair_mask INTEGER NOT NULL CHECK(pair_mask IN (0,1)),
  diagonal_policy TEXT NOT NULL, source_code_hash TEXT NOT NULL, config_hash TEXT NOT NULL,
  input_hash TEXT NOT NULL, authorization_status TEXT NOT NULL
);

CREATE TABLE stg_delta_phi_spatial (
  export_id TEXT PRIMARY KEY, source_mode TEXT NOT NULL, run_id TEXT NOT NULL,
  state_i TEXT NOT NULL, state_j TEXT NOT NULL, pair_i INTEGER NOT NULL, pair_j INTEGER NOT NULL,
  x_index INTEGER NOT NULL, x_value REAL NOT NULL, x_unit TEXT NOT NULL, x_weight REAL NOT NULL,
  phi_i_x REAL NOT NULL, phi_j_x REAL NOT NULL, raw_delta_phi_ij_x REAL NOT NULL,
  wrapped_delta_phi_ij_x REAL NOT NULL, wrapping_interval TEXT NOT NULL, angle_unit TEXT NOT NULL,
  dimension_status TEXT NOT NULL, pair_mask INTEGER NOT NULL CHECK(pair_mask IN (0,1)),
  diagonal_policy TEXT NOT NULL, source_code_hash TEXT NOT NULL, config_hash TEXT NOT NULL,
  input_hash TEXT NOT NULL, authorization_status TEXT NOT NULL
);

CREATE TABLE stg_delta_phi_export_metadata (
  metadata_id TEXT PRIMARY KEY, work_package TEXT NOT NULL, status TEXT NOT NULL,
  input_manifest_path TEXT, source_mode TEXT, export_performed INTEGER NOT NULL CHECK(export_performed IN (0,1)),
  static_row_count INTEGER NOT NULL, spatial_row_count INTEGER NOT NULL,
  config_hash TEXT, input_hash TEXT, authorization_status TEXT, claim_boundary TEXT NOT NULL
);

CREATE TABLE stg_delta_phi_validation_result (
  validation_id TEXT PRIMARY KEY, validation_layer TEXT NOT NULL, check_name TEXT NOT NULL,
  status TEXT NOT NULL, severity TEXT NOT NULL, observed_value TEXT, expected_value TEXT,
  message TEXT NOT NULL, blocking_for_g02 INTEGER NOT NULL CHECK(blocking_for_g02 IN (0,1)),
  blocking_for_g13 INTEGER NOT NULL CHECK(blocking_for_g13 IN (0,1))
);
"""


def validation_row(vid: str, layer: str, name: str, status: str, severity: str,
                   observed: Any, expected: Any, message: str, g02: bool, g13: bool) -> dict[str, str]:
    return {
        "validation_id": vid, "validation_layer": layer, "check_name": name, "status": status,
        "severity": severity, "observed_value": str(observed), "expected_value": str(expected),
        "message": message, "blocking_for_g02": "yes" if g02 else "no",
        "blocking_for_g13": "yes" if g13 else "no",
    }


def validate_export_rows(mode: str | None, static_rows: list[dict[str, Any]],
                         spatial_rows: list[dict[str, Any]], export_performed: bool) -> dict[str, tuple[bool, str]]:
    rows = static_rows if mode == "static_pair_delta_phi" else spatial_rows
    finite_fields = ["phi_i", "phi_j", "raw_delta_phi_ij", "wrapped_delta_phi_ij"] if mode == "static_pair_delta_phi" else ["x_value", "x_weight", "phi_i_x", "phi_j_x", "raw_delta_phi_ij_x", "wrapped_delta_phi_ij_x"]
    finite = bool(rows) and all(math.isfinite(float(row[field])) for row in rows for field in finite_fields) if export_performed else False
    wrapped_field = "wrapped_delta_phi_ij" if mode == "static_pair_delta_phi" else "wrapped_delta_phi_ij_x"
    wrapped_ok = bool(rows) and all(-math.pi <= float(row[wrapped_field]) < math.pi for row in rows) if export_performed else False
    raw_field = "raw_delta_phi_ij" if mode == "static_pair_delta_phi" else "raw_delta_phi_ij_x"
    key_extra = None if mode == "static_pair_delta_phi" else "x_index"
    lookup = {(int(r["pair_i"]), int(r["pair_j"]), r.get(key_extra) if key_extra else None): float(r[raw_field]) for r in rows}
    antisym = bool(rows)
    if rows:
        for row in rows:
            i, j = int(row["pair_i"]), int(row["pair_j"])
            k = row.get(key_extra) if key_extra else None
            if (j, i, k) in lookup and not math.isclose(float(row[raw_field]), -lookup[(j, i, k)], abs_tol=1e-12):
                antisym = False
                break
    else:
        antisym = False
    diagonal_ok = bool(rows) and all((int(r["pair_i"]) != int(r["pair_j"])) or r["pair_mask"] == "false" for r in rows) if export_performed else False
    return {
        "nonempty": (bool(rows), f"rows={len(rows)}"), "finite": (finite, str(finite)),
        "wrapped": (wrapped_ok, str(wrapped_ok)), "antisymmetry": (antisym, str(antisym)),
        "diagonal": (diagonal_ok, str(diagonal_ok)),
    }


def main() -> None:
    if OUTPUT.exists():
        raise SystemExit(f"Refusing to overwrite existing output directory: {OUTPUT.relative_to(REPO)}")
    OUTPUT.mkdir(parents=True)

    template_created = create_template_if_missing()
    supplied_path: Path | None = None
    if not template_created:
        supplied_path = JSON_MANIFEST if JSON_MANIFEST.is_file() else YAML_MANIFEST if YAML_MANIFEST.is_file() else None
    manifest_path = supplied_path or JSON_MANIFEST
    manifest: dict[str, Any] = {}
    load_error = ""
    if supplied_path:
        try:
            manifest = load_manifest(supplied_path)
        except (OSError, ValueError, json.JSONDecodeError) as error:
            load_error = str(error)
            manifest = {}
    else:
        manifest = template_payload()

    f2_seen = False
    f2_status = "missing"
    if F2_MANIFEST.is_file():
        f2 = json.loads(F2_MANIFEST.read_text(encoding="utf-8"))
        f2_status = str(f2.get("status", "unknown"))
        f2_seen = f2_status == "interface01f2_interference_kernel_delta_phi_export_contract_completed_no_export"

    source_rows = []
    hashes: dict[str, str] = {}
    source_ok = True
    for path, role in SOURCE_SPECS:
        exists = path.is_file()
        value = sha256_file(path) if exists else "na"
        source_ok = source_ok and exists
        relative = f"../interference_kernel_v1/{path.relative_to(SOURCE_ROOT).as_posix()}"
        hashes[relative] = value
        source_rows.append({
            "source_path": relative, "exists": str(exists).lower(), "sha256": value,
            "role": role, "source_status": "read_ok_hashed" if exists else "missing",
            "notes": "Read-only inspection; source file not modified.",
        })
    write_csv(OUTPUT / "03_source_hashes.csv", ["source_path", "exists", "sha256", "role", "source_status", "notes"], source_rows)

    f2h_specs = [
        ("static_pair_delta_phi_allowed", "yes", "F2 static schema and provenance gates", "approved"),
        ("spatial_pair_delta_phi_x_allowed", "yes", "F2 spatial schema and x-provenance gates", "approved"),
        ("wrapping_interval_fixed", "[-pi, pi)", "single preselected interval", "approved"),
        ("angle_unit_dimensionless_angle_clear", "rad / dimensionless_angle", "explicit labels on every row", "approved"),
        ("pair_mask_diagonal_policy_clear", "pair_mask required; diagonals nonphysical", "policy fixed in manifest", "approved"),
        ("source_config_input_hash_required", "yes", "all hashes present and validated", "approved"),
        ("human_authorization_required", "yes", "exact authorization status and authorizer", "approved"),
        ("export_after_review_only", "yes", "manifest gates pass before computation", "approved"),
    ]
    f2h_rows = [
        {"review_item": item, "decision": decision, "required_condition": condition, "status": status, "notes": "F2H decision encoded by F3 prompt; not a substitute for input-manifest authorization."}
        for item, decision, condition, status in f2h_specs
    ]
    write_csv(OUTPUT / "02_f2h_review_decision.csv", ["review_item", "decision", "required_condition", "status", "notes"], f2h_rows)

    preflight_rows, manifest_valid, config_hash, input_hash = validate_manifest(manifest, supplied_path is not None and not load_error)
    if load_error:
        preflight_rows.append({"field_name":"manifest_parse","required":"yes","observed":load_error,"status":"missing_or_invalid","blocking_for_export":"yes","notes":"Manifest could not be parsed."})
        manifest_valid = False
    write_csv(OUTPUT / "04_input_manifest_preflight.csv", ["field_name", "required", "observed", "status", "blocking_for_export", "notes"], preflight_rows)

    selected_mode = manifest.get("source_mode") if manifest_valid else None
    all_gates = f2_seen and source_ok and manifest_valid
    mode_rows = []
    for mode in ("static_pair_delta_phi", "spatial_pair_delta_phi_x"):
        selected = selected_mode == mode
        can_export = all_gates and selected
        mode_rows.append({
            "source_mode": mode, "allowed_by_f2h": "yes", "selected_by_input_manifest": str(selected).lower(),
            "can_export": str(can_export).lower(),
            "decision_status": "authorized_for_controlled_export" if can_export else "not_selected" if all_gates else "blocked_input_manifest_missing_or_invalid",
            "reason": "All gates passed for selected mode." if can_export else "No valid authorized input manifest was available." if not all_gates else "Other approved mode selected.",
        })
    write_csv(OUTPUT / "05_export_mode_decision.csv", ["source_mode", "allowed_by_f2h", "selected_by_input_manifest", "can_export", "decision_status", "reason"], mode_rows)

    static_rows: list[dict[str, Any]] = []
    spatial_rows: list[dict[str, Any]] = []
    export_error = ""
    if all_gates:
        try:
            kernel_hash = hashes["../interference_kernel_v1/models/interference_kernel.py"]
            static_rows, spatial_rows = generate_exports(manifest, kernel_hash, config_hash, input_hash)
        except Exception as error:  # controlled export failure becomes blocked, with no partial staged rows
            export_error = f"{type(error).__name__}: {error}"
            static_rows, spatial_rows = [], []
    export_performed = all_gates and not export_error and bool(static_rows or spatial_rows)
    if not export_performed:
        static_rows, spatial_rows = [], []
    write_csv(OUTPUT / "06_static_delta_phi_export.csv", STATIC_FIELDS, static_rows)
    write_csv(OUTPUT / "07_spatial_delta_phi_x_export.csv", SPATIAL_FIELDS, spatial_rows)

    (OUTPUT / "08_staging_schema.sql").write_text(SCHEMA, encoding="utf-8")
    export_checks = validate_export_rows(selected_mode, static_rows, spatial_rows, export_performed)
    validation_rows = [
        validation_row("V01","contract","f2_contract_seen","pass" if f2_seen else "fail","high",f2_status,"completed_no_export","F2 contract status checked.",not f2_seen,not f2_seen),
        validation_row("V02","authorization","f2h_review_complete","pass","high",8,8,"All eight F2H decisions encoded.",False,False),
        validation_row("V03","provenance","source_hashes_present","pass" if source_ok else "fail","high",sum(1 for r in source_rows if r['exists']=='true'),4,"Required adjacent sources checked and hashed.",not source_ok,not source_ok),
        validation_row("V04","input","input_manifest_present","pass" if supplied_path else "fail","high",str(supplied_path) if supplied_path else "missing_template_created","authorized manifest","Template is not an authorized input manifest.",not bool(supplied_path),not bool(supplied_path)),
        validation_row("V05","authorization","authorization_status_valid","pass" if manifest.get('authorization_status')=='human_authorized_for_interface01_export' and bool(supplied_path) else "fail","high",manifest.get('authorization_status'),"human_authorized_for_interface01_export","Authorization status checked.",not manifest_valid,not manifest_valid),
        validation_row("V06","convention","wrapping_interval_valid","pass" if manifest.get('wrapping_interval')=='[-pi, pi)' and bool(supplied_path) else "not_run","high",manifest.get('wrapping_interval'),"[-pi, pi)","Wrapping contract checked only on supplied manifest.",not manifest_valid,not manifest_valid),
        validation_row("V07","convention","angle_unit_valid","pass" if manifest.get('angle_unit')=='rad' and bool(supplied_path) else "not_run","high",manifest.get('angle_unit'),"rad","Angle unit checked.",not manifest_valid,not manifest_valid),
        validation_row("V08","convention","dimension_status_valid","pass" if manifest.get('dimension_status')=='dimensionless_angle' and bool(supplied_path) else "not_run","high",manifest.get('dimension_status'),"dimensionless_angle","Dimension status checked.",not manifest_valid,not manifest_valid),
        validation_row("V09","mode","source_mode_allowed","pass" if selected_mode in {'static_pair_delta_phi','spatial_pair_delta_phi_x'} else "not_run","high",selected_mode,"approved mode","Source mode checked.",not manifest_valid,not manifest_valid),
        validation_row("V10","shape","phase_input_shape_valid","pass" if manifest_valid else "not_run","high","validated" if manifest_valid else "not_available","mode-specific shape","Shape validation is part of manifest preflight.",not manifest_valid,not manifest_valid),
        validation_row("V11","export","export_rows_nonempty_if_export_performed","pass" if export_performed and export_checks['nonempty'][0] else "not_run" if not export_performed else "fail","high",export_checks['nonempty'][1],"nonempty selected export","No export rows required on blocked path.",export_performed and not export_checks['nonempty'][0],export_performed and not export_checks['nonempty'][0]),
        validation_row("V12","pair","pair_mask_diagonal_policy_valid","pass" if export_performed and export_checks['diagonal'][0] else "not_run","high",export_checks['diagonal'][1],"diagonal false/excluded","Pair policy validation.",export_performed and not export_checks['diagonal'][0],export_performed and not export_checks['diagonal'][0]),
        validation_row("V13","numeric","finite_values","pass" if export_performed and export_checks['finite'][0] else "not_run","high",export_checks['finite'][1],"all finite","Numeric finiteness validation.",export_performed and not export_checks['finite'][0],export_performed and not export_checks['finite'][0]),
        validation_row("V14","numeric","wrapped_values_in_interval","pass" if export_performed and export_checks['wrapped'][0] else "not_run","high",export_checks['wrapped'][1],"[-pi,pi)","Wrapped interval validation.",export_performed and not export_checks['wrapped'][0],export_performed and not export_checks['wrapped'][0]),
        validation_row("V15","numeric","raw_antisymmetry_static_or_spatial","pass" if export_performed and export_checks['antisymmetry'][0] else "not_run","high",export_checks['antisymmetry'][1],"raw_ij=-raw_ji","Antisymmetry validation.",export_performed and not export_checks['antisymmetry'][0],export_performed and not export_checks['antisymmetry'][0]),
        validation_row("V16","boundary","no_m33_aggregate_source","pass","high","interference_kernel_v1 only","no M33 aggregate","M33 aggregates are not read as export input.",False,False),
        validation_row("V17","boundary","no_minimaltest_started","pass","high",False,False,"F3 performs export preflight only.",False,False),
        validation_row("V18","boundary","no_theta_0300_transfer","pass","high","not used","not used","No Phase-D threshold input is accepted or referenced by computation.",False,False),
    ]
    if export_error:
        validation_rows.append(validation_row("V19","execution","controlled_export_error","fail","high",export_error,"no error","Partial rows discarded; export blocked.",True,True))
        export_performed = False
        static_rows, spatial_rows = [], []
        write_csv(OUTPUT / "06_static_delta_phi_export.csv", STATIC_FIELDS, [])
        write_csv(OUTPUT / "07_spatial_delta_phi_x_export.csv", SPATIAL_FIELDS, [])
    write_csv(OUTPUT / "10_export_validation_results.csv", ["validation_id", "validation_layer", "check_name", "status", "severity", "observed_value", "expected_value", "message", "blocking_for_g02", "blocking_for_g13"], validation_rows)

    if export_performed:
        status = "interface01f3_authorized_delta_phi_export_staging_preflight_completed_export_staged"
        g02, g13 = "resolved_authorized_export_staged", "ready_for_minimaltest_design_not_started"
    else:
        status = "interface01f3_authorized_delta_phi_export_staging_preflight_blocked_no_export"
        g02, g13 = "unresolved_pending_authorized_export", "no_go"

    db_path = OUTPUT / "09_delta_phi_staging_preflight.sqlite"
    connection = sqlite3.connect(db_path)
    connection.executescript(SCHEMA)
    if export_performed:
        static_insert = "INSERT INTO stg_delta_phi_static VALUES (" + ",".join("?" for _ in STATIC_FIELDS) + ")"
        spatial_insert = "INSERT INTO stg_delta_phi_spatial VALUES (" + ",".join("?" for _ in SPATIAL_FIELDS) + ")"
        if static_rows:
            connection.executemany(static_insert, [[row[field] if field != 'pair_mask' else int(row[field]=='true') for field in STATIC_FIELDS] for row in static_rows])
        if spatial_rows:
            connection.executemany(spatial_insert, [[row[field] if field != 'pair_mask' else int(row[field]=='true') for field in SPATIAL_FIELDS] for row in spatial_rows])
    connection.execute(
        "INSERT INTO stg_delta_phi_export_metadata VALUES (?,?,?,?,?,?,?,?,?,?,?,?)",
        ("F3-META-01", "QSB-INTERFACE01F3", status, str(manifest_path), selected_mode,
         int(export_performed), len(static_rows), len(spatial_rows), config_hash or None,
         input_hash or None, manifest.get("authorization_status"), CLAIM),
    )
    connection.executemany(
        "INSERT INTO stg_delta_phi_validation_result VALUES (?,?,?,?,?,?,?,?,?,?)",
        [[row[key] if key not in {'blocking_for_g02','blocking_for_g13'} else int(row[key]=='yes') for key in ["validation_id","validation_layer","check_name","status","severity","observed_value","expected_value","message","blocking_for_g02","blocking_for_g13"]] for row in validation_rows],
    )
    connection.commit()
    connection.close()

    gate_rows = [
        {"gate":"G02","status_before":"unresolved_pending_authorized_export","status_after":g02,"decision_basis":"Authorized raw/wrapped export staged with blocking checks passed." if export_performed else "No concrete human-authorized input manifest was supplied; only a template and schema were created.","allowed_next_action":"review staged source and design next Minimaltest step without running it in F3" if export_performed else "complete and human-authorize the input manifest, then run a fresh controlled export preflight","forbidden_next_action":"running Minimaltest inside F3"},
        {"gate":"G13","status_before":"no_go","status_after":g13,"decision_basis":"G02 staged source is available; design only remains next." if export_performed else "G02 remains unresolved because export was blocked.","allowed_next_action":"Minimaltest design review only" if export_performed else "remain no_go until authorized export/staging succeeds","forbidden_next_action":"running Minimaltest inside F3"},
    ]
    write_csv(OUTPUT / "11_g02_g13_decision.csv", ["gate", "status_before", "status_after", "decision_basis", "allowed_next_action", "forbidden_next_action"], gate_rows)

    if export_performed:
        review_specs = [
            ("R01","staged row-count reconciliation","high","yes","yes",f"Static rows={len(static_rows)}; spatial rows={len(spatial_rows)}.","Human reviewer verifies counts against authorized state/grid and pair policy."),
            ("R02","human sign-off before Minimaltest execution","high","no","yes","Staging completion is not execution authorization.","Record separate human sign-off for any later Minimaltest."),
            ("R03","theta_new/epsilon_new freeze preservation","high","no","yes","F3 did not tune thresholds.","Verify later design uses unchanged prior freeze policies."),
        ]
    else:
        review_specs = [
            ("R01","authorized input manifest missing","high","yes","yes","Only a template was created; no concrete arrays/provenance authorization supplied.","Complete JSON/YAML manifest with reviewed real/authorized inputs and exact authorization."),
            ("R02","phase input and shape authorization","high","yes","yes","No phases or phase_field were available for validation/export.","Supply mode-compatible arrays or authorized generator inputs."),
            ("R03","config and input hashes","high","yes","yes","Hashes cannot be finalized without concrete manifest/input.","Provide immutable config/input; allow deterministic hash validation."),
            ("R04","human authorization identity","high","yes","yes","Authorizer and authorization note are absent.","Record named human authorization tied to exact manifest/config hash."),
        ]
    review_rows = [
        {"review_id": rid, "topic": topic, "severity": severity, "blocking_for_g02": bg02,
         "blocking_for_g13": bg13, "description": description, "required_resolution": resolution}
        for rid, topic, severity, bg02, bg13, description, resolution in review_specs
    ]
    write_csv(OUTPUT / "12_review_items.csv", ["review_id", "topic", "severity", "blocking_for_g02", "blocking_for_g13", "description", "required_resolution"], review_rows)

    note = f"""# INTERFACE01-F3 Final Result

## Status
`{status}`

## Export und Staging
- Export performed: `{'yes' if export_performed else 'no'}`.
- Staging DB created: `yes`.
- Selected source mode: `{selected_mode or 'none'}`.
- Static export rows: `{len(static_rows)}`.
- Spatial export rows: `{len(spatial_rows)}`.

{'Kein konkretes human-autorisiertes Input-Manifest lag vor. F3 hat deshalb die vorgeschriebene JSON-Vorlage, beide header-only Exportdateien und nur das SQLite-Schema mit Metadaten/Validierungen erzeugt.' if not export_performed else 'Der autorisierte Export wurde in die Staging-Datenbank geladen; eine getrennte Human-Pruefung bleibt vor jedem weiteren Schritt erforderlich.'}

## Gates
- G02: `{g02}`.
- G13: `{g13}`.

## Minimaltest
Kein Minimaltest wurde gestartet. F3 hat weder `theta_new` noch `epsilon_new` veraendert und keine Phase-D-Schwelle uebertragen.

## Naechster erlaubter Schritt
{'Die Manifest-Vorlage mit konkreten, provenance-gesicherten Inputs vervollstaendigen und human autorisieren; danach einen frischen F3-Exportlauf starten.' if not export_performed else 'Den gestagten Export und seine Zeilen-/Hash-/Maskenvalidierung human pruefen; danach nur den naechsten Minimaltest-Designschritt planen.'}

## Claim Boundary
{CLAIM}
"""
    (OUTPUT / "FINAL_RESULT_NOTE.md").write_text(note, encoding="utf-8")

    source_mode_selected = selected_mode or "none"
    run_manifest = {
        "work_package": "QSB-INTERFACE01F3", "status": status,
        "created_at_utc": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "repo_root": str(REPO), "adjacent_source_root": str(SOURCE_ROOT),
        "f2_contract_path": str(F2_MANIFEST), "f2_contract_status_seen": f2_status,
        "f2h_review_status": "eight_decisions_approved_for_preflight",
        "input_manifest_path": str(manifest_path),
        "input_manifest_status": "template_created_missing_authorized_manifest" if template_created else "valid_authorized_manifest" if manifest_valid else "present_but_invalid_or_unauthorized",
        "export_performed": export_performed, "staging_db_created": True,
        "minimaltest_started": False, "g02_status_after_f3": g02, "g13_status_after_f3": g13,
        "source_mode_selected": source_mode_selected,
        "source_paths_checked": [row["source_path"] for row in source_rows], "source_hashes": hashes,
        "config_hash": config_hash or "not_computed_missing_authorized_manifest",
        "input_hash": input_hash or "not_computed_missing_authorized_manifest",
        "static_export_rows": len(static_rows), "spatial_export_rows": len(spatial_rows),
        "claim_boundary": CLAIM, "modified_existing_files": [],
    }
    (OUTPUT / "01_f3_run_manifest.json").write_text(
        json.dumps(run_manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    print(json.dumps(run_manifest, ensure_ascii=False))


if __name__ == "__main__":
    main()
