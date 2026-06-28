#!/usr/bin/env python3
"""Create the INTERFACE01-F2 delta_phi export contract without exporting data."""

from __future__ import annotations

import csv
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


REPO = Path(__file__).resolve().parents[2]
SOURCE_ROOT = (REPO / "../interference_kernel_v1").resolve()
OUTPUT = REPO / "runs/QSB-INTERFACE01F2/interference_kernel_delta_phi_export_contract"
CLAIM = (
    "INTERFACE01-F2 defines a contract for a future delta_phi_ij export based on "
    "interference_kernel_v1 source logic. It does not create data, does not stage evidence, "
    "does not resolve G02, and does not permit G13/go. The contract supports later "
    "provenance-controlled export review only."
)
SOURCE_FILES = [
    SOURCE_ROOT / "models/action_phase.py",
    SOURCE_ROOT / "models/phase_generators.py",
    SOURCE_ROOT / "models/interference_kernel.py",
    SOURCE_ROOT / "models/datatypes.py",
]


def write_csv(name: str, fields: list[str], rows: list[dict[str, Any]]) -> None:
    with (OUTPUT / name).open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def source_rel(path: Path) -> str:
    return path.relative_to(SOURCE_ROOT).as_posix()


def field_row(mode: str, name: str, role: str, data_type: str,
              unit: str, dimension: str, rule: str, notes: str = "") -> dict[str, str]:
    return {
        "source_mode": mode, "field_name": name, "field_role": role, "required": "yes",
        "data_type": data_type, "unit_or_convention": unit, "dimension_status": dimension,
        "validation_rule": rule, "notes": notes,
    }


def required_fields() -> list[dict[str, str]]:
    common = [
        ("export_id", "immutable export-record identifier", "string", "canonical identifier", "not_applicable", "non-empty and unique"),
        ("source_mode", "export mode discriminator", "enum", "static_pair_delta_phi|spatial_pair_delta_phi_x", "not_applicable", "must equal row contract mode"),
        ("run_id", "authorized export-run identifier", "string", "canonical run identifier", "not_applicable", "non-empty and linked to authorization record"),
        ("state_i", "source state identifier", "string", "state ID", "not_applicable", "non-empty and traceable to ensemble input"),
        ("state_j", "target state identifier", "string", "state ID", "not_applicable", "non-empty and traceable to ensemble input"),
        ("pair_i", "integer state index i", "integer", "zero-based index", "dimensionless_index", "0 <= pair_i < N"),
        ("pair_j", "integer state index j", "integer", "zero-based index", "dimensionless_index", "0 <= pair_j < N"),
        ("wrapping_interval", "principal interval label", "string", "[-pi,pi) preferred", "dimensionless_angle_convention", "must match authorized pre-run choice"),
        ("angle_unit", "explicit angle convention", "enum", "rad", "dimensionless_angle", "must equal rad"),
        ("dimension_status", "phase dimension declaration", "enum", "dimensionless_angle", "dimensionless_angle", "must equal dimensionless_angle"),
        ("pair_mask", "pair eligibility flag", "boolean", "true|false", "dimensionless_boolean", "must implement authorized diagonal/mask policy"),
        ("zero_diagonal_policy", "diagonal treatment", "enum", "exclude|retain_zero", "not_applicable", "must be fixed before export and agree with pair_mask"),
        ("generator_path", "source generator path", "string", "path relative to source root", "not_applicable", "must identify inspected local source"),
        ("source_function", "source function name", "string", "canonical function name", "not_applicable", "must match code-level candidate register"),
        ("source_code_hash", "source code SHA256", "hex_string", "sha256", "not_applicable", "64 lowercase hex characters and match staged source"),
        ("config_hash", "resolved configuration SHA256", "hex_string", "sha256", "not_applicable", "64 lowercase hex characters and match immutable config"),
        ("input_hash", "input ensemble/snapshot SHA256", "hex_string", "sha256", "not_applicable", "64 lowercase hex characters and match immutable input"),
        ("authorization_status", "human authorization gate", "enum", "authorized_for_export|not_authorized", "not_applicable", "staging accepts only authorized_for_export"),
    ]
    rows: list[dict[str, str]] = []
    static = "static_pair_delta_phi"
    for values in common:
        rows.append(field_row(static, *values))
    rows.extend([
        field_row(static, "phi_i", "raw phase of state i", "float64", "rad", "dimensionless_angle", "finite real value; provenance matches phases input"),
        field_row(static, "phi_j", "raw phase of state j", "float64", "rad", "dimensionless_angle", "finite real value; provenance matches phases input"),
        field_row(static, "raw_delta_phi_ij", "unwrapped difference phi_i-phi_j", "float64", "rad", "dimensionless_angle", "finite and equals phi_i-phi_j within frozen tolerance"),
        field_row(static, "wrapped_delta_phi_ij", "principal-value phase difference", "float64", "rad", "dimensionless_angle", "equals authorized wrapping function of raw_delta_phi_ij and lies in interval"),
    ])

    spatial = "spatial_pair_delta_phi_x"
    for values in common:
        rows.append(field_row(spatial, *values))
    rows.extend([
        field_row(spatial, "x_index", "grid index", "integer", "zero-based index", "dimensionless_index", "0 <= x_index < Nx"),
        field_row(spatial, "x_value", "grid coordinate", "float64", "explicit x_unit", "source_defined_length_or_model_coordinate", "finite and traceable to ensemble.x"),
        field_row(spatial, "x_unit", "grid-coordinate unit/status", "string", "explicit SI or model-unit label", "source_defined", "must not be blank or inferred after export"),
        field_row(spatial, "x_weight", "normalized spatial averaging weight", "float64", "dimensionless", "dimensionless_weight", "finite, nonnegative, and weights sum to one per run"),
        field_row(spatial, "phi_i_x", "raw phase field for state i at x", "float64", "rad", "dimensionless_angle", "finite and linked to phase-field input"),
        field_row(spatial, "phi_j_x", "raw phase field for state j at x", "float64", "rad", "dimensionless_angle", "finite and linked to phase-field input"),
        field_row(spatial, "raw_delta_phi_ij_x", "unwrapped phi_i(x)-phi_j(x)", "float64", "rad", "dimensionless_angle", "finite and equals phi_i_x-phi_j_x within frozen tolerance"),
        field_row(spatial, "wrapped_delta_phi_ij_x", "principal-value spatial phase difference", "float64", "rad", "dimensionless_angle", "equals authorized wrapping function and lies in interval"),
    ])
    return rows


def main() -> None:
    if OUTPUT.exists():
        raise SystemExit(f"Refusing to overwrite existing output directory: {OUTPUT.relative_to(REPO)}")
    missing = [path for path in SOURCE_FILES if not path.is_file()]
    if missing:
        raise SystemExit("Missing adjacent source files: " + ", ".join(str(path) for path in missing))

    kernel_text = (SOURCE_ROOT / "models/interference_kernel.py").read_text(encoding="utf-8")
    action_text = (SOURCE_ROOT / "models/action_phase.py").read_text(encoding="utf-8")
    required_markers = [
        "delta_phi = phases[:, None] - phases[None, :]",
        "delta_phi_x = phase_field[:, None, :] - phase_field[None, :, :]",
        "delta_phi_repr = delta_phi_x[:, :, mid]",
        "phase_field = (p * x - E * t) / hbar",
    ]
    marker_sources = kernel_text + "\n" + action_text
    absent = [marker for marker in required_markers if marker not in marker_sources]
    if absent:
        raise SystemExit("Required source markers absent: " + "; ".join(absent))

    OUTPUT.mkdir(parents=True)
    hashes = {source_rel(path): sha256(path) for path in SOURCE_FILES}

    candidates = [
        {
            "candidate_id": "F2-SRC-STATIC-01", "candidate_type": "static_pair_delta_phi",
            "source_path": "models/interference_kernel.py", "source_function": "build_interference_kernel",
            "source_expression": "delta_phi = phases[:, None] - phases[None, :]",
            "expected_shape": "N x N",
            "candidate_status": "code_level_source_candidate;not_yet_exported;requires_human_authorization_before_staging",
            "claim_boundary": "Code-level difference logic only; no authorized export or staged source exists.",
            "review_note": "Future export must retain phi_i, phi_j, raw and wrapped delta, mask, hashes, and authorization status.",
        },
        {
            "candidate_id": "F2-SRC-SPATIAL-01", "candidate_type": "spatial_pair_delta_phi_x",
            "source_path": "models/interference_kernel.py", "source_function": "build_spatially_averaged_kernel",
            "source_expression": "delta_phi_x = phase_field[:, None, :] - phase_field[None, :, :]",
            "expected_shape": "N x N x Nx",
            "candidate_status": "code_level_source_candidate;not_yet_exported;requires_human_authorization_before_staging",
            "claim_boundary": "Code-level spatial difference logic only; midpoint delta_phi_repr is not a complete source.",
            "review_note": "Future export must be x-resolved and include grid values, units, weights, phases, raw/wrapped delta, hashes, and authorization.",
        },
    ]
    write_csv("02_source_candidate_register.csv", ["candidate_id", "candidate_type", "source_path", "source_function", "source_expression", "expected_shape", "candidate_status", "claim_boundary", "review_note"], candidates)

    modes = [
        {"source_mode":"static_pair_delta_phi","allowed":"yes_contract_only","shape":"N x N","grain":"one row per run/state_i/state_j pair","raw_field_required":"raw_delta_phi_ij","wrapped_field_required":"wrapped_delta_phi_ij","principal_interval_required":"yes","x_dimension_required":"no","pair_mask_required":"yes","notes":"Export both orientations only if explicitly authorized; diagonal policy fixed before export."},
        {"source_mode":"spatial_pair_delta_phi_x","allowed":"yes_contract_only","shape":"N x N x Nx","grain":"one row per run/state_i/state_j/x_index","raw_field_required":"raw_delta_phi_ij_x","wrapped_field_required":"wrapped_delta_phi_ij_x","principal_interval_required":"yes","x_dimension_required":"yes: x_index,x_value,x_unit,x_weight","pair_mask_required":"yes","notes":"Do not replace full x-resolved tensor with delta_phi_repr midpoint slice or aggregate kernel outputs."},
    ]
    write_csv("03_export_modes_contract.csv", ["source_mode", "allowed", "shape", "grain", "raw_field_required", "wrapped_field_required", "principal_interval_required", "x_dimension_required", "pair_mask_required", "notes"], modes)

    fields = required_fields()
    write_csv("04_required_field_contract.csv", ["source_mode", "field_name", "field_role", "required", "data_type", "unit_or_convention", "dimension_status", "validation_rule", "notes"], fields)

    wrapping = [
        {"contract_item":"raw_phase_convention","required":"yes","allowed_value":"unwrapped real-valued phase difference","default_value":"no implicit wrapping","validation_rule":"raw value equals exported phase_i minus phase_j within frozen tolerance","claim_boundary":"Raw phase is model/source output, not a geometric interval."},
        {"contract_item":"wrapped_phase_convention","required":"yes","allowed_value":"principal interval selected before export","default_value":"[-pi,pi)","validation_rule":"wrapped=((raw+pi) mod 2*pi)-pi with exact +pi mapped to -pi under preferred default","claim_boundary":"Wrapping is a representation convention, not physical compactness evidence."},
        {"contract_item":"allowed_principal_interval","required":"yes","allowed_value":"[-pi,pi) preferred; [0,2*pi) only by explicit authorized override","default_value":"[-pi,pi)","validation_rule":"one interval per export run; no row-dependent convention","claim_boundary":"Alternative interval requires a new reviewed contract/config identity."},
        {"contract_item":"angle_unit","required":"yes","allowed_value":"rad","default_value":"rad","validation_rule":"every phase and delta row explicitly labels rad","claim_boundary":"Radians are a dimensionless-angle convention but must remain explicit."},
        {"contract_item":"dimension_status","required":"yes","allowed_value":"dimensionless_angle","default_value":"dimensionless_angle","validation_rule":"must be present and consistent for phi and delta fields","claim_boundary":"Dimensionless does not permit mixing with unrelated model spaces."},
        {"contract_item":"periodicity","required":"yes","allowed_value":"modulo 2*pi","default_value":"modulo 2*pi","validation_rule":"wrapped values reproduce cos/sin of raw values within frozen tolerance","claim_boundary":"cos/sin consistency validates representation only, not source provenance."},
    ]
    write_csv("05_wrapping_unit_convention_contract.csv", ["contract_item", "required", "allowed_value", "default_value", "validation_rule", "claim_boundary"], wrapping)

    provenance_specs = [
        ("PRA-01","source_code_path","generator_path","Path exists under pinned interference_kernel_v1 source root and matches authorized mode.","reject_export","Record relative and resolved source roots."),
        ("PRA-02","source_code_hash","source_code_hash","SHA256 matches exact inspected source file at export time.","reject_export","Hash interference_kernel.py and any phase generator used."),
        ("PRA-03","source_function","source_function","Function equals build_interference_kernel or build_spatially_averaged_kernel for declared mode.","reject_export","No implicit substitute function."),
        ("PRA-04","config_hash","config_hash","Resolved immutable export configuration has SHA256 and is archived with run.","reject_export","Include wrapping/mask/mode/tolerance policies."),
        ("PRA-05","input_hash","input_hash","Immutable StateEnsemble/phases/phase_field input snapshot has SHA256.","reject_export","Printed samples are insufficient."),
        ("PRA-06","run_identity","run_id","Non-empty unique run ID links every row, config, input, code hashes, and authorization.","reject_export","No reused identity after contract change."),
        ("PRA-07","random_seed","random_seed_if_used","Seed recorded for any regime/noise/ensemble generation; explicit not_applicable otherwise.","reject_export","Seed alone does not establish provenance."),
        ("PRA-08","phase_regime","phase_regime","Regime is explicit and authorized; debroglie/trivial/random/random_field/noisy_db/chirp/quadratic are not silently mixed.","reject_export","Synthetic/control regimes remain labelled controls."),
        ("PRA-09","hbar_convention","hbar_value_and_unit_status","Value plus SI/model convention recorded and dimensionally compatible with p,x,E,t inputs.","reject_export","hbar=1 requires explicit model-unit status."),
        ("PRA-10","x_grid_provenance","x_grid_snapshot_hash","Spatial mode records x values, unit/status, weights, grid generator, and checksum.","reject_spatial_export","Not applicable only for static mode."),
        ("PRA-11","state_ensemble_provenance","state_ensemble_snapshot_hash","State IDs, p, E, t, labels, and generating source are immutable and hashed.","reject_export","No untracked row order as identity."),
        ("PRA-12","human_authorization","authorization_status","Explicit human authorization references reviewed F2 contract and exact export config hash.","not_authorized_for_staging","Authorization must precede export/staging."),
        ("PRA-13","posthoc_tuning_lock","preregistration_lock","No output inspection may change mode, wrapping, mask, fields, inputs, regime, hashes, or validation rules.","invalidate_export","Any change requires new authorization and run ID."),
        ("PRA-14","zero_diagonal_and_pair_mask","zero_diagonal_policy;pair_mask","Policy fixed before export; diagonal and excluded pairs have consistent flags and values.","reject_export","Do not infer pair eligibility after outcomes."),
    ]
    provenance = [
        {"requirement_id": rid, "requirement_type": typ, "required": "yes", "field_or_artifact": artifact,
         "validation_rule": rule, "failure_status": failure, "notes": notes}
        for rid, typ, artifact, rule, failure, notes in provenance_specs
    ]
    write_csv("06_provenance_authorization_contract.csv", ["requirement_id", "requirement_type", "required", "field_or_artifact", "validation_rule", "failure_status", "notes"], provenance)

    exclusion_specs = [
        ("M33 phase_pair_stats.csv","Aggregate legacy statistics; F1 found no operational raw/wrapped source.","yes_lineage_warning","no","Do not reconstruct raw values."),
        ("mean_dphi_x","Spatial arithmetic aggregate, not raw pairwise phase tensor.","yes_aggregate_context","no","Not raw_delta_phi_ij."),
        ("var_dphi_x","Variance aggregate loses values and phase orientation.","yes_aggregate_context","no","Not invertible."),
        ("mean_cos_dphi","Periodic aggregate loses raw phase and branch information.","yes_kernel_context","no","Cannot substitute raw/wrapped delta."),
        ("mean_abs_cos_dphi","Absolute periodic aggregate has additional information loss.","yes_kernel_context","no","Cannot substitute raw/wrapped delta."),
        ("mean_sin_dphi","Periodic aggregate alone does not provide complete raw/wrapped source provenance.","yes_kernel_context","no","Cannot stage alone."),
        ("kbar_ij","Averaged kernel value, not phase difference.","yes_downstream_context","no","Downstream result only."),
        ("K_real","Prefactor-weighted cosine kernel output.","yes_validation_companion","no","Not a phase source."),
        ("G_raw_complex","Prefactor-weighted complex kernel output.","yes_validation_companion","no","Amplitude/overlap/response prefactor prevents use as raw phase source."),
        ("cos(delta_phi)","Many-to-one transform loses branch/raw value.","yes_validation_companion","no","Never accepted alone."),
        ("sin(delta_phi)","Many-to-one transform alone is incomplete and lacks raw source lineage.","yes_validation_companion","no","Never accepted alone."),
        ("delta_phi_repr","Single midpoint slice from spatial tensor; source code labels it representative/debug readability.","yes_debug_warning","no","Full x-resolved export required."),
        ("printed phase samples","Partial display without complete pair/grid/provenance records.","yes_debug_warning","no","No staging from console output."),
        ("CSV summaries without raw/wrapped pairwise fields","Missing canonical required quantities and validation links.","yes_schema_warning","no","Reject at schema gate."),
        ("theta=0.0300 Phase-D calibration","Belongs to separate Phase-D model space and is forbidden as INTERFACE threshold prior.","yes_boundary_guard","no","No numerical transfer."),
        ("Legacy-c/line-element bridge","Not established as a local operational phase source for this contract.","yes_review_context","no","Excluded from export provenance."),
    ]
    exclusions = [
        {"excluded_item": item, "reason": reason, "may_inform_contract": inform,
         "may_stage_for_g02": stage, "notes": notes}
        for item, reason, inform, stage, notes in exclusion_specs
    ]
    write_csv("07_exclusion_rules.csv", ["excluded_item", "reason", "may_inform_contract", "may_stage_for_g02", "notes"], exclusions)

    gate = [{
        "gate": "G02_and_G13", "status_before": "G02=unresolved;G13=no_go",
        "status_after": "G02=unresolved_pending_authorized_export;G13=no_go",
        "decision_basis": "Code-level static and spatial source logic is locally verified and hashed, but no authorized raw/wrapped export or staging was performed.",
        "allowed_next_action": "prepare a separately authorized export/staging run only after F2 contract review",
        "forbidden_next_action": "minimaltest or staging without authorized raw/wrapped delta_phi export",
    }]
    write_csv("08_g02_g13_preflight_decision.csv", ["gate", "status_before", "status_after", "decision_basis", "allowed_next_action", "forbidden_next_action"], gate)

    reviews = [
        ("R01","static vs spatial export mode selection","high","yes","yes","Select one mode or explicitly authorize both with separate schemas/run IDs.","Human review and mode-specific config hash."),
        ("R02","wrapping interval selection","high","yes","yes","Freeze [-pi,pi) preferred or explicitly justified alternative before export.","Authorized wrapping policy in config."),
        ("R03","angle unit / dimensionless-angle labelling","high","yes","yes","Require rad plus dimensionless_angle on every phase/delta field.","Schema validator and reviewed dimension contract."),
        ("R04","phase regime authorization","high","yes","yes","Authorize exact regime; keep synthetic/control regimes explicitly labelled.","Regime, seed, generator and input hashes frozen."),
        ("R05","source/config/input hash capture","high","yes","yes","Capture exact source code, resolved config, and immutable input hashes.","All PRA hash gates pass."),
        ("R06","human authorization before staging","high","yes","yes","No export or staging before explicit authorization tied to config hash.","Signed/recorded authorization status."),
        ("R07","pair diagonal / pair_mask policy","medium","yes","yes","Freeze diagonal exclusion/zero policy and orientation/mask semantics.","Mode config plus schema validation."),
        ("R08","no use of delta_phi_repr as complete source","high","yes","yes","Spatial export must retain all x indices and cannot use midpoint slice alone.","Full x-resolved row-count/shape validation."),
        ("R09","x-grid unit and weight provenance","high","yes","yes","Spatial mode requires x unit/status, grid checksum, and normalized weights.","PRA-10 plus required fields pass."),
        ("R10","authorization versus evidence boundary","high","yes","yes","Authorized export remains candidate input, not physical validation or evidence by itself.","Claim-boundary review at staging."),
    ]
    review_rows = [
        {"review_id": rid, "topic": topic, "severity": severity, "blocking_for_g02": g02,
         "blocking_for_g13": g13, "description": desc, "required_resolution": resolution}
        for rid, topic, severity, g02, g13, desc, resolution in reviews
    ]
    write_csv("09_review_items.csv", ["review_id", "topic", "severity", "blocking_for_g02", "blocking_for_g13", "description", "required_resolution"], review_rows)

    note = f"""# INTERFACE01-F2 Final Result

## Status
`interface01f2_interference_kernel_delta_phi_export_contract_completed_no_export`

## Befund
In `interference_kernel_v1` ist Code-Logik fuer zwei kuenftige Quellen lokal belegt:

- statisch: `delta_phi = phases[:, None] - phases[None, :]` in `build_interference_kernel`;
- raeumlich: `delta_phi_x = phase_field[:, None, :] - phase_field[None, :, :]` in `build_spatially_averaged_kernel`.

Die vier relevanten Quelldateien wurden read-only geprueft und per SHA256 erfasst. F2 definiert dafuer Exportfelder, Roh-/Wrap-Konvention, Provenienz, Autorisierung, Masken und Ausschlussregeln.

## Keine Ausfuehrung
Es wurden keine `delta_phi_ij`-Werte erzeugt, exportiert oder gestaged. Kein Modelllauf und kein Minimaltest wurde gestartet.

## Gates
- G02: `unresolved_pending_authorized_export`.
- G13: `no_go`.

## Ausschluss
Der M33-Aggregatpfad bleibt ausgeschlossen. Insbesondere sind `mean_dphi_x`, Kernel-/Trigonometrie-Aggregate, `K_real`, `G_raw_complex` und `delta_phi_repr` allein keine vollstaendige operative Quelle. Phase-D-`theta=0.0300` und die Legacy-c-/Linienelement-Bruecke sind ebenfalls ausgeschlossen.

## Naechster erlaubter Schritt
Human Review dieses Vertrags. Danach darf nur bei ausdruecklicher Freigabe ein separater, provenance-gesicherter Raw-/Wrapped-Export- und Staging-Lauf vorbereitet werden.

## Claim Boundary
{CLAIM}
"""
    (OUTPUT / "FINAL_RESULT_NOTE.md").write_text(note, encoding="utf-8")

    output_names = [
        "01_f2_run_manifest.json", "02_source_candidate_register.csv", "03_export_modes_contract.csv",
        "04_required_field_contract.csv", "05_wrapping_unit_convention_contract.csv",
        "06_provenance_authorization_contract.csv", "07_exclusion_rules.csv",
        "08_g02_g13_preflight_decision.csv", "09_review_items.csv", "FINAL_RESULT_NOTE.md",
    ]
    manifest = {
        "work_package": "QSB-INTERFACE01F2",
        "status": "interface01f2_interference_kernel_delta_phi_export_contract_completed_no_export",
        "created_at_utc": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "repo_root": str(REPO), "adjacent_source_root": str(SOURCE_ROOT),
        "input_sufficiency": "sufficient_for_export_contract_not_for_g02_resolution",
        "execution_clearance": "no_export_no_minimaltest",
        "g02_status_after_f2": "unresolved_pending_authorized_export",
        "g13_status_after_f2": "no_go",
        "source_paths_checked": [source_rel(path) for path in SOURCE_FILES],
        "source_hashes": hashes, "created_outputs": output_names,
        "claim_boundary": CLAIM, "no_export_performed": True,
        "minimaltest_started": False, "modified_existing_files": [],
    }
    (OUTPUT / "01_f2_run_manifest.json").write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    print(json.dumps(manifest, ensure_ascii=False))


if __name__ == "__main__":
    main()
