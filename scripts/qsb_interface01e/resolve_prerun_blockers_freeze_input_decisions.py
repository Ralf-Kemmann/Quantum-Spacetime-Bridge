#!/usr/bin/env python3
"""Resolve lockable QSB-INTERFACE01-E pre-run decisions without execution."""

from __future__ import annotations

import csv
import json
from datetime import datetime, timezone
from pathlib import Path


REPO = Path(__file__).resolve().parents[2]
OUTPUT = REPO / "runs/QSB-INTERFACE01E/resolve_prerun_blockers_freeze_input_decisions"
CLAIM = "Pre-run blocker resolution and freeze decisions only; no execution result and not a proof of emergent spacetime or gravitation."
I01D = "runs/QSB-INTERFACE01D/minimal_test_freeze_prerun_contract"
I01C = "runs/QSB-INTERFACE01C/minimal_candidate_test_design"
I01B = "runs/QSB-INTERFACE01B/candidate_bridge_forms"
I01A = "runs/QSB-INTERFACE01A/minimal_mechanism_skeleton"
MAT = "runs/QSB-MATERIAL01/typb_materialsensitive_signature_mart_intake"
D0X = "runs/QSB-D0X/phase_d_local_threshold_motif_summary"
COMP_D1J = "runs/QSB-ST-COMP01D1J/explicit_phase_field_exposure_cyclic_recheck_open"


def write_csv(name: str, fields: list[str], rows: list[dict[str, object]]) -> None:
    with (OUTPUT / name).open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def anchor(aid: str, label: str, cls: str, path_text: str, summary: str,
           unit: str, usable: str, note: str) -> dict[str, str]:
    exists = (REPO / path_text).is_file()
    return {
        "anchor_id": aid, "anchor_label": label, "anchor_class": cls,
        "source_path": path_text, "read_status": "read_ok" if exists else "missing",
        "key_content_summary": summary, "unit_status": unit,
        "usable_for_interface01e": usable if exists else "review",
        "review_note": note if exists else f"Missing locally; {note}",
    }


def main() -> None:
    if OUTPUT.exists():
        raise SystemExit(f"Refusing to overwrite existing output directory: {OUTPUT.relative_to(REPO)}")
    OUTPUT.mkdir(parents=True)

    anchors = [
        anchor("IE-IN-01", "INTERFACE01-D freeze scope", "interface01d", f"{I01D}/02_interface01d_freeze_scope_contract.csv", "Eleven scope items with frozen and blocking states.", "mixed contract", "yes", "Primary blocker scope."),
        anchor("IE-IN-02", "INTERFACE01-D phase freeze spec", "interface01d", f"{I01D}/03_interface01d_phase_input_freeze_spec.csv", "Requires operational delta_phi source, pair universe, conventions, and checksums.", "dimensionless radian required", "yes", "G02 source requirements."),
        anchor("IE-IN-03", "INTERFACE01-D material freeze spec", "interface01d", f"{I01D}/04_interface01d_material_injection_rule_freeze_spec.csv", "Separates metadata intake, missing numerical map, N03, and N04.", "mixed review", "yes", "G03 starting state."),
        anchor("IE-IN-04", "INTERFACE01-D theta/epsilon spec", "interface01d", f"{I01D}/05_interface01d_theta_epsilon_freeze_spec.csv", "Leaves method choices open while forbidding Phase-D threshold transfer.", "normalized C02 space", "yes", "G04/G05 starting state."),
        anchor("IE-IN-05", "INTERFACE01-D split/null spec", "interface01d", f"{I01D}/06_interface01d_split_and_nullmodel_freeze_spec.csv", "Defines four splits and six null-model configuration requirements.", "design contract", "yes", "G06/G07 starting state."),
        anchor("IE-IN-06", "INTERFACE01-D gate matrix", "interface01d", f"{I01D}/07_interface01d_prerun_gate_matrix.csv", "Records blockers G02-G07, G11, and consequential G13.", "gate metadata", "yes", "Previous gate state."),
        anchor("IE-IN-07", "INTERFACE01-D open items", "interface01d", f"{I01D}/08_interface01d_open_review_items.csv", "Eight unresolved pre-run items.", "mixed", "yes", "Resolution checklist."),
        anchor("IE-IN-08", "INTERFACE01-D manifest", "interface01d", f"{I01D}/10_interface01d_run_manifest.json", "Records no-go and no execution.", "metadata_only", "yes", "Starting clearance."),
        anchor("IE-IN-09", "INTERFACE01-C test plan", "interface01c", f"{I01C}/02_interface01c_minimal_candidate_test_plan.csv", "Fixes F02/C02/R01, R02 audit, six controls, and design-only scope.", "normalized candidate space", "yes", "Candidate scope."),
        anchor("IE-IN-10", "INTERFACE01-C theta design", "interface01c", f"{I01C}/03_interface01c_theta_calibration_design.csv", "Provides quantile, control-separation, stability, and fixed-grid policies.", "dimensionless C02 [0,1]", "yes", "Basis for formula lock."),
        anchor("IE-IN-11", "INTERFACE01-C null models", "interface01c", f"{I01C}/05_interface01c_required_null_models.csv", "Defines N01-N06 purposes and current input gaps.", "design_only", "yes", "Basis for configuration locks."),
        anchor("IE-IN-12", "INTERFACE01-B candidate registry", "interface01b", f"{I01B}/02_interface01b_bridge_candidate_registry.csv", "Defines candidate formulas and information-loss risks.", "dimensionless/model space", "yes", "Formula source."),
        anchor("IE-IN-13", "INTERFACE01-A dimension contract", "interface01a", f"{I01A}/02_interface01a_quantity_dimension_contract.csv", "Separates SI, model, phase, correlation, threshold, and graph quantities.", "mixed explicit contract", "yes", "Unit guard."),
        anchor("IE-IN-14", "MATERIAL01 material systems", "material01", f"{MAT}/csv/03_dim_material_system.csv", "Readable material_system_id, material_label, and isotope_label fields.", "categorical metadata; mass_number review context", "yes", "Supports metadata-only conditioning."),
        anchor("IE-IN-15", "MATERIAL01 signature facts", "material01", f"{MAT}/csv/04_fact_debroglie_material_signature.csv", "Readable material IDs, source IDs, scores, and mass/wave ranks.", "mixed_review; SI fields retained but excluded from coupling", "partial", "Supports audit and N04 rank source only."),
        anchor("IE-IN-16", "MATERIAL01 isotope shifts", "material01", f"{MAT}/csv/05_fact_isotope_shift.csv", "Readable isotope labels, mass numbers, and mass-order ranks with review flags.", "rank dimensionless; mass fields review-sensitive", "partial", "N04 conditional source."),
        anchor("IE-IN-17", "Phase-D summary manifest", "phase_d", f"{D0X}/12_d0x_run_manifest.json", "theta=0.0300 remains Phase-D-only.", "model_units / dimensionless toy-model units; not_SI_converted", "partial", "Forbidden theta prior."),
        anchor("IE-IN-18", "COMP01-D1J explicit phase source audit", "phase_source_audit", f"{COMP_D1J}/phase_field_exposure_summary.csv", "Reports explicit_phase_source_available=false and explicit_phase_recheck_possible=false.", "proxy/synthetic diagnostic context only", "yes", "Confirms conceptual/proxy fields cannot close G02."),
        anchor("IE-IN-19", "COMP01-D1J readout", "phase_source_audit", f"{COMP_D1J}/readout.md", "States no explicit emitted phase fields and no physical phase reconstruction.", "diagnostic proxy only", "yes", "Negative source-sufficiency anchor."),
    ]
    write_csv("01_interface01e_input_anchor_register.csv", ["anchor_id","anchor_label","anchor_class","source_path","read_status","key_content_summary","unit_status","usable_for_interface01e","review_note"], anchors)

    phase_decisions = [
        {"phase_decision_id":"PD-01","phase_input_name":"operational_relative_phase_pairs","required_quantity":"delta_phi_ij","required_columns":"source_record_id;pair_id;i;j;delta_phi_ij;phase_unit_convention;wrap_interval;material_system_id_or_na;identity_group_or_na;source_checksum;review_status","source_anchor":"unresolved; COMP01-D1J confirms no explicit emitted phase source","periodicity_policy":"delta_phi_wrapped=atan2(sin(delta_phi_raw),cos(delta_phi_raw)); canonical interval [-pi,pi]; exact -pi/pi tie normalized to +pi","normalization_policy":"dimensionless radian convention; no scaling before F02 cosine projection","allowed_transforms":"predefined F02 cosine_projection only after deterministic wrapping and schema validation","forbidden_transforms":"post-hoc phase selection; reconstructed proxy substitution; hidden theta reuse; SI/model-unit mixing; outcome-dependent pair removal","freeze_decision":"unresolved_blocker","blocks_execution_later":"yes","review_note":"No concrete provenance-approved delta_phi_ij records exist. Existing COMP01-D1J is an explicit-source-missing diagnostic, not an input."},
        {"phase_decision_id":"PD-02","phase_input_name":"phase_source_acceptance_contract","required_quantity":"delta_phi_ij","required_columns":"dataset_id;schema_version;record_count;pair_count;content_sha256;source_class;physical_or_diagnostic_status;created_utc","source_anchor":"future user-authorized local source","periodicity_policy":"must match PD-01 globally","normalization_policy":"validator rejects missing/mixed units, nonfinite values, duplicate pair keys, and unreviewed proxy-only records","allowed_transforms":"read-only validation; deterministic hash split after source freeze","forbidden_transforms":"generation of synthetic phase evidence in this block; mutation after checksum; use of evaluation outcomes","freeze_decision":"unresolved_blocker","blocks_execution_later":"yes","review_note":"Acceptance rules are frozen, but no dataset can be named or hashed."},
    ]
    write_csv("03_interface01e_phase_input_decision.csv", ["phase_decision_id","phase_input_name","required_quantity","required_columns","source_anchor","periodicity_policy","normalization_policy","allowed_transforms","forbidden_transforms","freeze_decision","blocks_execution_later","review_note"], phase_decisions)

    material_decisions = [
        {"material_decision_id":"MD-01","material_injection_rule":"metadata_label_conditioning_only","material_anchor_source":f"{MAT}/csv/03_dim_material_system.csv","required_material_fields":"material_system_id;material_label;isotope_label_or_na","injection_point":"metadata_conditioning_and_nullmodel_N03","allowed_use":"grouping;stratification;label-shuffle control;material-sensitivity audit;provenance joins","forbidden_use":"direct numeric SI/model-unit coupling; deriving delta_phi from labels; inserting wavelength, energy, mass, or signature score into F02/C02/R01","unit_dimension_status":"categorical metadata only; no numerical unit coupling","freeze_decision":"frozen","blocks_execution_later":"no","review_note":"Readable fields verified. G03 is resolved by intentionally excluding numerical material injection."},
        {"material_decision_id":"MD-02","material_injection_rule":"mass_order_only_control_source","material_anchor_source":f"{MAT}/csv/05_fact_isotope_shift.csv","required_material_fields":"series_label;isotope_label;mass_number;mass_order_rank;source_file_id;requires_human_review","injection_point":"nullmodel_N04_only","allowed_use":"frozen rank-only surrogate within reviewed isotope series; report all review flags","forbidden_use":"mass_u conversion; physical mass-to-phase formula; geometry interpretation; replacement of primary phase input","unit_dimension_status":"mass_order_rank dimensionless; mass_number identifier context; source rows review-required","freeze_decision":"frozen","blocks_execution_later":"no","review_note":"N04 can be configured conditionally on matched isotope rows; unmatched materials are reported, not imputed."},
    ]
    write_csv("04_interface01e_material_injection_decision.csv", ["material_decision_id","material_injection_rule","material_anchor_source","required_material_fields","injection_point","allowed_use","forbidden_use","unit_dimension_status","freeze_decision","blocks_execution_later","review_note"], material_decisions)

    threshold_decisions = [
        {"threshold_decision_id":"TD-01","parameter_name":"theta_new","candidate_space":"normalized_C02_space","forbidden_prior":"theta_phase_d_0_0300_direct_transfer","calibration_source":"calibration_split plus N01/N02 controls only","calibration_method":"calibration_split_quantile_plus_null_guard","selection_rule":"Use fixed grid {0.00,0.01,...,1.00}; compute predeclared structured-vs-pooled-N01/N02 separation statistic on calibration only; require qualifying contiguous stability window width >=0.05; select midpoint of widest qualifying window, tie by lower midpoint; if none qualifies, stop with no threshold.","pre_registration_lock":"Grid, statistic definition, qualification level, width, midpoint/tie rule, split hash, and code/config checksums fixed before any evaluation/holdout access.","unit_dimension_status":"dimensionless model-space threshold on C02 [0,1]","freeze_decision":"frozen_formula","blocks_execution_later":"no","review_note":"Numeric theta_new is derived later from calibration only; evaluation/holdout cannot modify it."},
        {"threshold_decision_id":"TD-02","parameter_name":"epsilon_new","candidate_space":"normalized_C02_space","forbidden_prior":"Phase-D near-threshold values or outcome-selected edge bands","calibration_source":"same frozen calibration_split C02 values used by TD-01","calibration_method":"normalized_margin_band_policy","selection_rule":"epsilon_new=max(0.02,0.05*IQR(C02_calibration_values)); use linear-interpolation Q1/Q3 convention; cap at 0.10; equality counts near-threshold; freeze numeric result before evaluation and use unchanged for all primary/null runs.","pre_registration_lock":"Formula, quantile convention, cap, inclusivity, decimal serialization, calibration checksum, and no-adjustment rule fixed now.","unit_dimension_status":"dimensionless normalized margin band on C02 scale","freeze_decision":"frozen_formula","blocks_execution_later":"no","review_note":"If calibration IQR is undefined or nonfinite, stop; do not substitute an outcome-driven value."},
    ]
    write_csv("05_interface01e_theta_epsilon_decision.csv", ["threshold_decision_id","parameter_name","candidate_space","forbidden_prior","calibration_source","calibration_method","selection_rule","pre_registration_lock","unit_dimension_status","freeze_decision","blocks_execution_later","review_note"], threshold_decisions)

    hash_rule = "Assign identity_group if known, else source_record_id, by SHA256('20260620|'+key); bucket=first 8 hex digits mod 100."
    split_decisions = [
        {"split_decision_id":"SD-01","split_name":"calibration_split","purpose":"theta_new/epsilon_new calibration and permitted null calibration only","split_rule":hash_rule,"proportion_or_rule":"buckets 0-39 (40%)","random_seed":"20260620","stratification_policy":"preserve material/isotope identity groups where possible; group is assignment unit; fallback deterministic record-key hash flagged for review","leakage_guard":"No identity group or pair member may cross calibration/evaluation/holdout; validate after assignment.","freeze_decision":"frozen_with_group_review","blocks_execution_later":"no","review_note":"Membership materializes only after PD-01 source freeze."},
        {"split_decision_id":"SD-02","split_name":"evaluation_split","purpose":"one-pass primary and matched-null assessment","split_rule":hash_rule,"proportion_or_rule":"buckets 40-69 (30%)","random_seed":"20260620","stratification_policy":"same immutable group-aware policy as SD-01","leakage_guard":"No parameter, criterion, chain, or membership changes after evaluation access.","freeze_decision":"frozen_with_group_review","blocks_execution_later":"no","review_note":"Absent strata are reported; records are not moved post hoc."},
        {"split_decision_id":"SD-03","split_name":"holdout_split","purpose":"final untouched confirmation only after all prior gates pass","split_rule":hash_rule,"proportion_or_rule":"buckets 70-89 (20%)","random_seed":"20260620","stratification_policy":"same immutable group-aware policy as SD-01","leakage_guard":"Holdout remains unopened for calibration, debugging, method choice, and evaluation decisions.","freeze_decision":"frozen_with_group_review","blocks_execution_later":"no","review_note":"Any premature access invalidates holdout use."},
        {"split_decision_id":"SD-04","split_name":"sensitivity_split","purpose":"predeclared robustness companion only","split_rule":hash_rule,"proportion_or_rule":"buckets 90-99 (10%)","random_seed":"20260620","stratification_policy":"same immutable group-aware policy as SD-01","leakage_guard":"Sensitivity results cannot revise primary parameters or pass/fail criteria.","freeze_decision":"frozen_with_group_review","blocks_execution_later":"no","review_note":"Small/empty strata are limitations, not grounds for reassignment."},
    ]
    write_csv("06_interface01e_split_seed_decision.csv", ["split_decision_id","split_name","purpose","split_rule","proportion_or_rule","random_seed","stratification_policy","leakage_guard","freeze_decision","blocks_execution_later","review_note"], split_decisions)

    nulls = [
        {"nullmodel_id":"N01","nullmodel_label":"trivial_uniform_phase","target_failure_mode":"structure generated without relative-phase variation","configuration":"Within each frozen split set all delta_phi_ij=0 rad; retain pair universe and metadata; apply unchanged F02/C02/theta_new/epsilon_new.","random_seed":"not_applicable","preserved_quantities":"pair IDs; split; material metadata; candidate formulas; frozen parameters","destroyed_quantities":"all relative-phase variation","expected_control_behavior":"Uniform F02=1 and C02=1; any heterogeneity must arise only from explicitly declared non-phase metadata and cannot be called phase structure.","pass_condition":"Primary interpretation explicitly distinguishes N01 and does not attribute N01 structure to phase variation.","fail_implication":"Reject phase-structure interpretation.","freeze_decision":"frozen","blocks_execution_later":"no","review_note":"Execution still awaits PD-01 input universe."},
        {"nullmodel_id":"N02","nullmodel_label":"random_phase_shuffle","target_failure_mode":"pair-specific phase relation indistinguishable from shuffled assignment","configuration":"Shuffle delta_phi_ij within split and material/isotope stratum where size>=2; otherwise within split; 100 permutations; preserve values exactly.","random_seed":"20260622 master seed; per permutation SHA256(seed|nullmodel_id|split|index)","preserved_quantities":"delta_phi marginal distribution; split sizes; pair universe; material strata where possible","destroyed_quantities":"pair-specific phase assignment","expected_control_behavior":"Primary predeclared statistic separates from pooled shuffle controls under TD-01 stability rule.","pass_condition":"Frozen separation criterion passes without parameter changes.","fail_implication":"Reject candidate for stated phase-structure target.","freeze_decision":"frozen","blocks_execution_later":"no","review_note":"Sparse-stratum fallback is logged, never silently reassigned."},
        {"nullmodel_id":"N03","nullmodel_label":"material_label_shuffle","target_failure_mode":"material association caused by labels alone","configuration":"Shuffle material_system_id/material_label/isotope_label tuple within split; prefer same system_class and isotope-vs-atomic class; 100 permutations; phase/C02 values fixed.","random_seed":"20260623 master seed; deterministic per split/permutation derivation","preserved_quantities":"phase values; pair assignments; C02; split; label-class counts","destroyed_quantities":"material-label association","expected_control_behavior":"Any preregistered material-association statistic weakens relative to unshuffled metadata conditioning.","pass_condition":"Primary association exceeds frozen control criterion; no numerical material coupling is introduced.","fail_implication":"Report no supported material-conditioned association.","freeze_decision":"frozen","blocks_execution_later":"no","review_note":"Metadata-only conditioning resolves G03 without claiming causal injection."},
        {"nullmodel_id":"N04","nullmodel_label":"mass_order_only_control","target_failure_mode":"candidate adds no information beyond isotope mass order","configuration":"For rows matched to isotope series use mass_order_rank as sole material surrogate; compare frozen material statistic; unmatched rows marked not_applicable and excluded only from N04 comparison.","random_seed":"not_applicable","preserved_quantities":"series membership; mass-order rank; split; source/review flags","destroyed_quantities":"all material conditioning beyond mass-order surrogate","expected_control_behavior":"Primary material-conditioned statistic reports incremental behavior relative to mass-order-only baseline.","pass_condition":"Frozen incremental criterion passes on eligible rows; coverage is reported.","fail_implication":"No demonstrated information beyond mass ordering; do not generalize to unmatched materials.","freeze_decision":"frozen_as_conditional_requires_mass_field","blocks_execution_later":"partial","review_note":"Required rank field is readable in MATERIAL01; execution validates joins and eligible coverage."},
        {"nullmodel_id":"N05","nullmodel_label":"threshold_randomization_or_sweep_guard","target_failure_mode":"isolated or post-hoc threshold effect","configuration":"Evaluate and report full fixed theta grid 0.00..1.00 step 0.01 on calibration and matched nulls; TD-01 alone selects theta_new; R02 uses TD-02 unchanged.","random_seed":"not_applicable","preserved_quantities":"C02 values; splits; full grid; statistic definition","destroyed_quantities":"ability to hide threshold sensitivity by selective reporting","expected_control_behavior":"Selected threshold lies in qualifying stability window width>=0.05; all grid rows retained.","pass_condition":"Window and full-report rules pass; otherwise no theta_new is selected.","fail_implication":"Stop run before evaluation or reject threshold-based interpretation.","freeze_decision":"frozen","blocks_execution_later":"no","review_note":"Phase-D 0.0300 is not a grid prior or favored point."},
        {"nullmodel_id":"N06","nullmodel_label":"pipeline_identity_control","target_failure_mode":"pipeline mutation, leakage, or untracked information loss","configuration":"Reprocess unchanged immutable inputs twice; compare content hashes, split membership, F02/C02 values, margins, and metadata; enumerate F02 even-symmetry merges and R01 losses.","random_seed":"20260620 for any shared split operation; otherwise not_applicable","preserved_quantities":"all immutable input and expected deterministic outputs","destroyed_quantities":"none","expected_control_behavior":"Byte-stable normalized tables where serialization is fixed; numeric fields equal within frozen tolerance 1e-12; no split leakage.","pass_condition":"Hashes/tolerances/membership and information-loss ledger pass before interpretation.","fail_implication":"Invalidate run and investigate pipeline; no result assessment.","freeze_decision":"frozen","blocks_execution_later":"no","review_note":"Tolerance applies to deterministic numeric recomputation, not physical validation."},
    ]
    write_csv("07_interface01e_nullmodel_configuration_lock.csv", ["nullmodel_id","nullmodel_label","target_failure_mode","configuration","random_seed","preserved_quantities","destroyed_quantities","expected_control_behavior","pass_condition","fail_implication","freeze_decision","blocks_execution_later","review_note"], nulls)

    resolutions = [
        {"gate_id":"G02","gate_label":"phase input frozen","previous_status":"fail","resolution_action":"Searched relevant repository outputs and audited COMP01-D1J; froze schema/wrapping/acceptance rules but found no explicit provenance-approved delta_phi source.","new_status":"unresolved_blocker","blocks_execution_later":"yes","evidence_or_rule_anchor":"PD-01; PD-02; IE-IN-18; IE-IN-19","review_note":"Only genuine remaining upstream input blocker."},
        {"gate_id":"G03","gate_label":"material injection rule frozen","previous_status":"fail","resolution_action":"Locked metadata_label_conditioning_only and N03; locked N04 to reviewed mass-order fields; prohibited numerical coupling.","new_status":"pass","blocks_execution_later":"no","evidence_or_rule_anchor":"MD-01; MD-02","review_note":"Material enters as metadata conditioning, not as phase generator."},
        {"gate_id":"G04","gate_label":"theta_new calibration frozen","previous_status":"review_gap","resolution_action":"Locked calibration-only fixed grid, N01/N02 separation, stability-window, midpoint/tie, and no-threshold failure formula.","new_status":"pass_with_condition","blocks_execution_later":"no","evidence_or_rule_anchor":"TD-01","review_note":"Numeric theta derives later; formula is immutable."},
        {"gate_id":"G05","gate_label":"epsilon_new frozen","previous_status":"review_gap","resolution_action":"Locked max(0.02,0.05*IQR) formula, quantile convention, cap, inclusivity, and stop behavior.","new_status":"pass_with_condition","blocks_execution_later":"no","evidence_or_rule_anchor":"TD-02","review_note":"Numeric epsilon derives later from calibration only."},
        {"gate_id":"G06","gate_label":"splits frozen","previous_status":"fail","resolution_action":"Locked 40/30/20/10 SHA256 split with seed 20260620 and group leakage guard.","new_status":"pass_with_condition","blocks_execution_later":"no","evidence_or_rule_anchor":"SD-01 to SD-04","review_note":"Membership awaits G02 input; rule cannot change."},
        {"gate_id":"G07","gate_label":"all six nullmodels frozen","previous_status":"fail","resolution_action":"Locked N01-N06 configurations, seeds, preservation/destruction rules, pass conditions, and failure implications.","new_status":"pass_with_condition","blocks_execution_later":"partial","evidence_or_rule_anchor":"N01-N06","review_note":"N04 is eligibility-conditional; all execution still awaits G02."},
        {"gate_id":"G11","gate_label":"no post-hoc tuning path","previous_status":"review_gap","resolution_action":"Locked chain, formulas, grids, splits, seeds, nulls, statistics, failure actions, and invalidation rule before outcomes.","new_status":"pass","blocks_execution_later":"no","evidence_or_rule_anchor":"POSTHOC-LOCK-01; all decision tables","review_note":"Any change requires a new pre-registered contract and invalidates the old run identity."},
        {"gate_id":"G13","gate_label":"execution clearance decision","previous_status":"fail","resolution_action":"Recomputed strict gate after G02-G07/G11 decisions.","new_status":"unresolved_blocker","blocks_execution_later":"yes","evidence_or_rule_anchor":"G02 unresolved; final decision FD-01","review_note":"No-go follows solely from mandatory gate logic, not hesitation."},
    ]
    write_csv("02_interface01e_blocker_resolution_table.csv", ["gate_id","gate_label","previous_status","resolution_action","new_status","blocks_execution_later","evidence_or_rule_anchor","review_note"], resolutions)

    posthoc_lock = "No evaluation or holdout statistic may change theta_new, epsilon_new, split assignment, nullmodel configuration, candidate chain, phase/pair selection, material conditioning, or pass/fail criteria. Any such change invalidates the run and requires a new pre-registered contract with a new run identity."
    gate_status = {row["gate_id"]: row["new_status"] for row in resolutions}
    required = ["G02", "G03", "G04", "G05", "G06", "G07", "G11"]
    ready_states = {"pass", "pass_with_condition"}
    clearance = "ready_for_minimal_execution_later" if all(gate_status[g] in ready_states for g in required) else "no_go_unresolved_blockers"
    final_gate = [{
        "decision_id":"FD-01", "candidate_chain":"F02 -> C02 -> R01 with mandatory R02 audit",
        "G02_phase_input":gate_status["G02"], "G03_material_injection":gate_status["G03"],
        "G04_theta_new":gate_status["G04"], "G05_epsilon_new":gate_status["G05"],
        "G06_splits":gate_status["G06"], "G07_nullmodels":gate_status["G07"],
        "G11_posthoc_lock":"pass: " + posthoc_lock, "claim_boundary":"pass: " + CLAIM,
        "execution_clearance_later":clearance,
        "next_allowed_action":"provide_and_review_explicit_delta_phi_input_source_then_recompute_gate",
        "forbidden_next_action":"execute_immediately_or_generate_phase_evidence_to_fill_G02",
        "review_note":"All lockable decisions are closed. G02 remains unresolved because no explicit emitted operational phase source is available; G13 therefore remains no-go.",
    }]
    write_csv("08_interface01e_final_gate_decision.csv", ["decision_id","candidate_chain","G02_phase_input","G03_material_injection","G04_theta_new","G05_epsilon_new","G06_splits","G07_nullmodels","G11_posthoc_lock","claim_boundary","execution_clearance_later","next_allowed_action","forbidden_next_action","review_note"], final_gate)

    assessment = f"""# QSB-INTERFACE01-E Final Assessment

## Zweck
INTERFACE01-E schliesst alle aus vorhandenen Ankern entscheidbaren Pre-Run-Regeln fuer `F02 -> C02 -> R01`. Der Minimaltest wurde nicht ausgefuehrt und es wurden keine Phasendaten erzeugt.

## Adressierte D-Blocker
Bearbeitet wurden G02-G07, G11 und G13. G03 ist `pass`; G04-G07 sind `pass_with_condition`; G11 ist `pass`. G02 bleibt `unresolved_blocker`; G13 folgt zwingend als nicht freigegeben.

## Phaseninput-Entscheid
`G02 = unresolved_blocker`.

Erforderlich bleibt ein provenance-gesicherter, dimensionsloser `delta_phi_ij`-Input mit Paar-IDs, Radian-Konvention, Wrap-Intervall, Source-Checksum und Reviewstatus. Die Repo-Pruefung fand zwar COMP01-D1J-Phasenbegriffe, dessen eigener Befund lautet jedoch: keine explizit emittierten Phasenspalten, explizite Repruefung nicht moeglich, Proxy-/synthetischer Diagnosekontext. Dieser Anker darf G02 nicht scheinbar schliessen.

## Material-Injektionsentscheid
`G03 = pass` durch `metadata_label_conditioning_only`.

MATERIAL01 liefert `material_system_id`, `material_label` und `isotope_label` fuer Gruppierung, Stratifikation, N03 und Audit. Es erzeugt keine Phase und koppelt keine SI-Werte an Phase-D- oder C02-Groessen. N04 nutzt ausschliesslich review-markierte Mass-order-Ranks als Kontrollsurrogat.

## theta_new und epsilon_new
Beide Policies sind als Formeln eingefroren.

`theta_new`: festes Grid 0.00 bis 1.00 in 0.01-Schritten; Auswahl nur auf Calibration-Split gegen N01/N02 unter vorab definierter Stabilitaetsfensterregel. Kein qualifizierendes Fenster bedeutet Stopp. Phase-D-`0.0300` ist weder Wert noch Prior.

`epsilon_new = max(0.02, 0.05 * IQR(C02_calibration))`, gedeckelt bei 0.10, mit fixierter Quantil-/Gleichheitsregel. Der Zahlenwert wird spaeter ausschliesslich aus dem Calibration-Split berechnet und danach nicht angepasst.

## Splits und Seeds
Eingefroren sind 40/30/20/10 Prozent fuer Calibration/Evaluation/Holdout/Sensitivity. Zuweisung erfolgt per SHA256-Hash mit Seed `20260620`, bevorzugt auf Identity-Gruppenebene. Bekannte Gruppen duerfen nicht ueber Splits leaken; unbekannte Gruppen nutzen dokumentierten Record-Key-Fallback.

## Nullmodell-Locks
N01-N06 besitzen konkrete Konfigurationen, Seeds, erhaltene/zerstoerte Groessen, Passbedingungen und Failure-Aktionen. N02 nutzt Seed 20260622, N03 Seed 20260623. N04 ist auf vorhandene, review-markierte Isotopen-Mass-order-Ranks begrenzt. N05 erzwingt vollstaendige Grid-Berichte. N06 prueft Determinismus, Leakage und Informationsverlust.

## Post-hoc-Tuning-Sperre
{posthoc_lock}

## Finaler Gate-Entscheid
`execution_clearance_later = {clearance}`

Es gibt genau einen echten verbleibenden Pflichtblocker: G02. Solange keine explizite, autorisierte und gepruefte `delta_phi_ij`-Quelle benannt und gehasht werden kann, ist eine spaetere Minimal-Ausfuehrung nicht freigegeben.

## Claim-Grenze
{CLAIM}

Die eingefrorenen Regeln sind Testmethodik, keine Bestaetigung des Kandidaten oder eines physikalischen Mechanismus.

## Naechster erlaubter Schritt
Nur einen expliziten lokalen `delta_phi_ij`-Input bereitstellen und gegen PD-01/PD-02 pruefen; danach G02 und G13 neu berechnen. Nicht erlaubt ist, in diesem Block synthetische Phasen zu erzeugen oder den Test sofort auszufuehren.
"""
    (OUTPUT / "09_interface01e_final_assessment.md").write_text(assessment, encoding="utf-8")

    status = "interface01e_resolve_prerun_blockers_ready_for_minimal_execution_later" if clearance == "ready_for_minimal_execution_later" else "interface01e_resolve_prerun_blockers_no_go_unresolved_blockers"
    manifest = {
        "run_id": "QSB-INTERFACE01E", "status": status,
        "output_dir": "runs/QSB-INTERFACE01E/resolve_prerun_blockers_freeze_input_decisions",
        "input_sufficiency": "sufficient_for_freeze_decisions_with_missing_operational_phase_input",
        "execution_clearance_later": clearance, "input_anchors": len(anchors),
        "blocker_resolution_rows": len(resolutions), "phase_input_decision_rows": len(phase_decisions),
        "material_injection_decision_rows": len(material_decisions),
        "theta_epsilon_decision_rows": len(threshold_decisions),
        "split_seed_decision_rows": len(split_decisions),
        "nullmodel_configuration_rows": len(nulls), "final_gate_decision_rows": len(final_gate),
        "remaining_mandatory_blockers": ["G02_phase_input", "G13_execution_clearance_consequence"],
        "base_split_seed": 20260620, "phase_d_theta_direct_transfer_allowed": False,
        "mutated_existing_files": False, "generated_synthetic_evidence": False,
        "minimal_test_executed": False, "new_simulation_performed": False,
        "phase_d_rescan_performed": False, "external_research_performed": False,
        "created_utc": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "claim_boundary": CLAIM,
    }
    (OUTPUT / "10_interface01e_run_manifest.json").write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    print(json.dumps(manifest, ensure_ascii=False))


if __name__ == "__main__":
    main()
