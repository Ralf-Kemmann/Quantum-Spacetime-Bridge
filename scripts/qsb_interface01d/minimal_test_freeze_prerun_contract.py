#!/usr/bin/env python3
"""Generate the QSB-INTERFACE01-D no-execution pre-run freeze contract."""

from __future__ import annotations

import csv
import json
from datetime import datetime, timezone
from pathlib import Path


REPO = Path(__file__).resolve().parents[2]
OUTPUT = REPO / "runs/QSB-INTERFACE01D/minimal_test_freeze_prerun_contract"
CLAIM = "Pre-run freeze contract only; no execution result and not a proof of emergent spacetime or gravitation."
I01C = "runs/QSB-INTERFACE01C/minimal_candidate_test_design"
I01B = "runs/QSB-INTERFACE01B/candidate_bridge_forms"
I01A = "runs/QSB-INTERFACE01A/minimal_mechanism_skeleton"
MAT = "runs/QSB-MATERIAL01/typb_materialsensitive_signature_mart_intake"
D0X = "runs/QSB-D0X/phase_d_local_threshold_motif_summary"


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
        "usable_for_interface01d": usable if exists else "review",
        "review_note": note if exists else f"Not found locally; {note}",
    }


def main() -> None:
    if OUTPUT.exists():
        raise SystemExit(f"Refusing to overwrite existing output directory: {OUTPUT.relative_to(REPO)}")
    OUTPUT.mkdir(parents=True)

    anchors = [
        anchor("ID-IN-01", "INTERFACE01-C input register", "interface01c", f"{I01C}/01_interface01c_input_anchor_register.csv", "Carries read status and boundaries for design inputs.", "mixed_by_anchor", "yes", "Read-only provenance input."),
        anchor("ID-IN-02", "INTERFACE01-C minimal test plan", "interface01c", f"{I01C}/02_interface01c_minimal_candidate_test_plan.csv", "Defines F02 -> C02 -> R01, R02 audit, all six nulls, and design-only scope.", "normalized candidate space", "yes", "Primary scope input."),
        anchor("ID-IN-03", "INTERFACE01-C theta design", "interface01c", f"{I01C}/03_interface01c_theta_calibration_design.csv", "Defines candidate methods and direct Phase-D transfer guard but does not freeze one method.", "dimensionless C02 [0,1]", "yes", "Method choice remains a blocker."),
        anchor("ID-IN-04", "INTERFACE01-C margin audit", "interface01c", f"{I01C}/04_interface01c_margin_audit_design.csv", "Defines signed margins, epsilon policy requirements, near-threshold flags, and required later columns.", "dimensionless C02 margin space", "yes", "Schema can be frozen; epsilon value/rule remains open."),
        anchor("ID-IN-05", "INTERFACE01-C null models", "interface01c", f"{I01C}/05_interface01c_required_null_models.csv", "Lists N01-N06; N01-N04 need inputs/review and no seeds/configurations are fixed.", "design_only", "yes", "Execution remains blocked."),
        anchor("ID-IN-06", "INTERFACE01-C acceptance/abort matrix", "interface01c", f"{I01C}/06_interface01c_acceptance_abort_matrix.csv", "Eight acceptance and seven abort gates.", "mixed gate checks", "yes", "Transferred into pre-run gates."),
        anchor("ID-IN-07", "INTERFACE01-C legacy c-bridge review", "legacy_c_bridge", f"{I01C}/07_interface01c_legacy_c_bridge_review.csv", "Records c/line-element bridge as not found locally and outside the candidate test.", "review only", "yes", "Must remain excluded unless source status changes after review."),
        anchor("ID-IN-08", "INTERFACE01-C open review items", "interface01c", f"{I01C}/08_interface01c_open_review_items.csv", "Lists missing phase input, injection map, calibration freezes, null inputs, and reproducibility contract.", "mixed", "yes", "Primary blocker inventory."),
        anchor("ID-IN-09", "INTERFACE01-C final assessment", "interface01c", f"{I01C}/09_interface01c_final_assessment.md", "Concludes design sufficient but later execution no-go.", "not_applicable", "yes", "Starting gate state."),
        anchor("ID-IN-10", "INTERFACE01-C manifest", "interface01c", f"{I01C}/10_interface01c_run_manifest.json", "Records execution_readiness=no_go and no candidate execution.", "metadata_only", "yes", "Manifest status is not evidence."),
        anchor("ID-IN-11", "INTERFACE01-B recommendation", "interface01b", f"{I01B}/07_interface01b_recommended_candidate_set.csv", "Conditionally recommends F02/C02/R01 with R02 and all controls.", "dimensionless/model space", "yes", "Candidate recommendation only."),
        anchor("ID-IN-12", "INTERFACE01-A dimensions contract", "interface01a", f"{I01A}/02_interface01a_quantity_dimension_contract.csv", "Separates phase, kernel, correlation, threshold, graph, SI, and model-unit objects.", "mixed explicit contract", "yes", "Unit guard source."),
        anchor("ID-IN-13", "MATERIAL01 result anchors", "material01", f"{MAT}/csv/06_result_material_sensitivity_anchor.csv", "Bounded material-sensitive phase/wave/signature anchors.", "mixed_review; SI wavelength/energy; mass_u review", "partial", "Labels/metadata only until injection map is frozen."),
        anchor("ID-IN-14", "Phase-D summary manifest", "phase_d", f"{D0X}/12_d0x_run_manifest.json", "theta=0.0300 is confined to Phase-D toy-model space.", "model_units / dimensionless toy-model units; not_SI_converted", "partial", "Numeric transfer is forbidden."),
        anchor("ID-IN-15", "Named Red-Team warning anchor", "red_team", "Red-Team_2026_05_23.md", "Named method-warning source was not found locally.", "not_applicable", "review", "Do not attribute warning statements to an unavailable file."),
        anchor("ID-IN-16", "Named personal evening-file warning anchor", "red_team", "QSB_ST_Persoenliche_Abenddatei_2026-05-20.pdf", "Named method-warning source was not found locally.", "not_applicable", "review", "Pointer remains unresolved; no content claim is imported."),
    ]
    write_csv("01_interface01d_input_anchor_register.csv", ["anchor_id","anchor_label","anchor_class","source_path","read_status","key_content_summary","unit_status","usable_for_interface01d","review_note"], anchors)

    scope = [
        {"scope_id":"SC-01","scope_item":"candidate_chain_F02_C02_R01","required_freeze_state":"frozen_required","current_state":"frozen","why_required":"Prevents candidate substitution after outcomes.","source_anchor":"ID-IN-02; ID-IN-11","blocks_execution":"no","contract_statement":"Only F02 K=cos(delta_phi), C02=(K+1)/2, and R01 hard threshold are in primary scope.","review_note":"No claim of physical preference."},
        {"scope_id":"SC-02","scope_item":"R02_margin_audit","required_freeze_state":"frozen_required","current_state":"frozen","why_required":"Edges without margins hide threshold instability.","source_anchor":"ID-IN-04","blocks_execution":"no","contract_statement":"Every evaluated pair and edge/flip must retain signed margin, near-threshold flag, run/null provenance, and frozen parameters.","review_note":"Audit schema frozen; epsilon parameter remains separate blocker."},
        {"scope_id":"SC-03","scope_item":"phase_input","required_freeze_state":"frozen_required","current_state":"missing","why_required":"No candidate can run without operational phase values and provenance.","source_anchor":"ID-IN-08","blocks_execution":"yes","contract_statement":"Execution is forbidden until source, pair universe, columns, modulo convention, split membership, and checksums are frozen.","review_note":"Conceptual phase language is insufficient."},
        {"scope_id":"SC-04","scope_item":"material_injection_rule","required_freeze_state":"frozen_required","current_state":"missing","why_required":"N03/N04 and material-retention claims need a declared injection point.","source_anchor":"ID-IN-13","blocks_execution":"yes","contract_statement":"MATERIAL01 labels/metadata may not enter F/C/R numerically until a dimension-safe injection transform is approved.","review_note":"Metadata-only use does not satisfy the gate."},
        {"scope_id":"SC-05","scope_item":"theta_new_calibration","required_freeze_state":"frozen_required","current_state":"review_gap","why_required":"Threshold selection controls the graph.","source_anchor":"ID-IN-03; ID-IN-14","blocks_execution":"yes","contract_statement":"Select and preregister one C02-space calibration method, split, statistic, grid, tie rule, and failure outcome; never transfer Phase-D 0.0300.","review_note":"Candidate methods exist but none is selected."},
        {"scope_id":"SC-06","scope_item":"epsilon_new_policy","required_freeze_state":"frozen_required","current_state":"review_gap","why_required":"Near-threshold classification depends on epsilon.","source_anchor":"ID-IN-04","blocks_execution":"yes","contract_statement":"Freeze a calibration-only or resolution-based epsilon rule and exact sensitivity companions before evaluation.","review_note":"No concrete rule/value is frozen."},
        {"scope_id":"SC-07","scope_item":"split_strategy","required_freeze_state":"frozen_required","current_state":"missing","why_required":"Calibration and evaluation must be independent.","source_anchor":"ID-IN-08","blocks_execution":"yes","contract_statement":"Freeze disjoint calibration, evaluation, holdout, and optional sensitivity memberships with checksums.","review_note":"No records exist to assign."},
        {"scope_id":"SC-08","scope_item":"six_nullmodel_configurations","required_freeze_state":"frozen_required","current_state":"review_gap","why_required":"Controls must precede primary outcomes.","source_anchor":"ID-IN-05","blocks_execution":"yes","contract_statement":"N01-N06 each require exact inputs, parameters, seed policy, output statistic, expected behavior, and failure action.","review_note":"Design labels alone are insufficient."},
        {"scope_id":"SC-09","scope_item":"SI_model_unit_separation","required_freeze_state":"frozen_required","current_state":"frozen","why_required":"Input spaces lack a validated numerical bridge.","source_anchor":"ID-IN-12; ID-IN-13; ID-IN-14","blocks_execution":"no","contract_statement":"Keep MATERIAL01 SI/mass-review fields, Phase-D model units, and normalized C02 values in separate declared channels.","review_note":"Any undeclared mixing triggers abort."},
        {"scope_id":"SC-10","scope_item":"claim_boundary","required_freeze_state":"frozen_required","current_state":"frozen","why_required":"Prevents interpretation beyond a candidate test.","source_anchor":"ID-IN-06","blocks_execution":"no","contract_statement":CLAIM,"review_note":"Must be checked in all future outputs."},
        {"scope_id":"SC-11","scope_item":"legacy_c_bridge_status","required_freeze_state":"excluded","current_state":"frozen","why_required":"Local source was not found.","source_anchor":"ID-IN-07","blocks_execution":"no","contract_statement":"Legacy c/line-element mapping is excluded from execution unless a local authoritative source is found and separately reviewed.","review_note":"Current exclusion satisfies the gate."},
    ]
    write_csv("02_interface01d_freeze_scope_contract.csv", ["scope_id","scope_item","required_freeze_state","current_state","why_required","source_anchor","blocks_execution","contract_statement","review_note"], scope)

    phase_rows = [
        {"phase_input_id":"PH-01","input_label":"operational phase source and provenance","phase_quantity":"phi_i and/or delta_phi_ij","source_context":"not identified","required_columns":"source_record_id;object_id;i;j;phi_i;phi_j;delta_phi_ij;phase_unit_convention;source_checksum;split_id;review_status","allowed_transformations":"Only checksum-traceable derivation of delta_phi from frozen phi values.","forbidden_transformations":"No conceptual substitution, after-the-fact record selection, or hidden Phase-D variable reuse.","periodicity_policy":"Must be explicit before execution.","normalization_policy":"Dimensionless radian convention required.","freeze_state":"missing","blocks_execution":"yes","review_note":"No source records exist."},
        {"phase_input_id":"PH-02","input_label":"relative phase derivation","phase_quantity":"delta_phi_ij","source_context":"future approved phase source","required_columns":"i;j;raw_difference;wrapped_delta_phi;wrap_interval;derivation_rule_id;source_checksum","allowed_transformations":"delta_phi=wrap(phi_i-phi_j) using one frozen interval and tie rule.","forbidden_transformations":"No pair-specific wrapping or result-dependent sign/orientation changes.","periodicity_policy":"Explicit 2*pi periodicity; choose and freeze one canonical interval.","normalization_policy":"No extra scaling before F02 unless separately approved.","freeze_state":"provisional","blocks_execution":"yes","review_note":"Rule template exists; interval/tie convention not selected."},
        {"phase_input_id":"PH-03","input_label":"pair universe and selection","phase_quantity":"ordered or unordered pair set","source_context":"future approved objects","required_columns":"pair_id;i;j;pair_semantics;inclusion_rule;split_id;selection_timestamp;checksum","allowed_transformations":"Apply one frozen inclusion/exclusion rule before outcomes.","forbidden_transformations":"No removal of inconvenient pairs or post-hoc phase-window selection.","periodicity_policy":"Inherited from PH-02.","normalization_policy":"All selected pairs use identical F02/C02 rules.","freeze_state":"missing","blocks_execution":"yes","review_note":"Pair semantics and universe absent."},
        {"phase_input_id":"PH-04","input_label":"phase input integrity gate","phase_quantity":"phase dataset as a whole","source_context":"future immutable input snapshot","required_columns":"dataset_id;record_count;pair_count;content_sha256;schema_version;created_utc;freeze_decision","allowed_transformations":"Read-only load after freeze; deterministic validation only.","forbidden_transformations":"No mutation between calibration, nulls, and evaluation; no Phase-D theta encoded in phase input.","periodicity_policy":"Validator must reject absent/mixed conventions.","normalization_policy":"Validator must confirm dimensionless phase and C02 output range.","freeze_state":"missing","blocks_execution":"yes","review_note":"No immutable snapshot exists."},
    ]
    write_csv("03_interface01d_phase_input_freeze_spec.csv", ["phase_input_id","input_label","phase_quantity","source_context","required_columns","allowed_transformations","forbidden_transformations","periodicity_policy","normalization_policy","freeze_state","blocks_execution","review_note"], phase_rows)

    material_rows = [
        {"material_rule_id":"MR-01","rule_label":"MATERIAL01 label/metadata intake","material_anchor_source":f"{MAT}/csv/06_result_material_sensitivity_anchor.csv","material_fields_required":"material_or_series;source_anchor;evidence_status;unit_status;review_note","injection_point":"metadata_only","allowed_use":"Carry labels, series, provenance, and bounded material-sensitive anchor status.","forbidden_use":"Do not infer phase values, graph edges, geometry, or a numerical transform from labels alone.","unit_dimension_status":"metadata channel; mixed_review retained","freeze_state":"frozen","blocks_execution":"no","review_note":"This row does not satisfy the numerical injection requirement."},
        {"material_rule_id":"MR-02","rule_label":"primary material injection map","material_anchor_source":"future reviewed mapping specification","material_fields_required":"source field; target phase/weight field; equation; units; parameters; provenance; validation status","injection_point":"review","allowed_use":"Only an explicitly approved dimension-safe map into phase_input or declared candidate weight.","forbidden_use":"No direct MATERIAL01 SI/mass value insertion into Phase-D or normalized C02 threshold operations.","unit_dimension_status":"unknown until mapping supplied","freeze_state":"missing","blocks_execution":"yes","review_note":"Injection point and formula are absent."},
        {"material_rule_id":"MR-03","rule_label":"material-label shuffle control","material_anchor_source":"MATERIAL01 labels plus frozen primary map","material_fields_required":"record_id;original_label;permuted_label;seed;permutation_id;split_id","injection_point":"nullmodel","allowed_use":"N03 only under a fixed permutation universe and seed policy.","forbidden_use":"No label shuffle after primary outcomes or across forbidden split boundaries.","unit_dimension_status":"labels categorical; numerical map unchanged","freeze_state":"provisional","blocks_execution":"yes","review_note":"Blocked by MR-02 and seed/split absence."},
        {"material_rule_id":"MR-04","rule_label":"mass-order-only control","material_anchor_source":"reviewed isotope records","material_fields_required":"series;isotope;mass_order_rank;wave_order_rank;unit/review flags;split_id","injection_point":"nullmodel","allowed_use":"N04 baseline only with review flags and a frozen statistic.","forbidden_use":"No silent mass_u conversion or use as a geometry proxy.","unit_dimension_status":"rank dimensionless; mass_u remains review","freeze_state":"provisional","blocks_execution":"yes","review_note":"Input rows/statistic/splits are not frozen."},
    ]
    write_csv("04_interface01d_material_injection_rule_freeze_spec.csv", ["material_rule_id","rule_label","material_anchor_source","material_fields_required","injection_point","allowed_use","forbidden_use","unit_dimension_status","freeze_state","blocks_execution","review_note"], material_rows)

    thresholds = [
        {"threshold_id":"TE-01","parameter_name":"theta_new","source_context":"normalized C02 candidate space [0,1]","allowed_calibration_source":"Frozen calibration split and preregistered N01/N02 controls only.","forbidden_calibration_source":"Phase-D 0.0300, evaluation/holdout outcomes, desired edge pattern, or material labels reserved for testing.","calibration_method":"not selected: choose exactly one primary rule from control separation, fixed quantile, or stability-window design; full fixed grid remains reporting guard.","selection_rule":"Must freeze objective/statistic, grid, tie rule, minimum stability width, failure outcome, and exact-decimal policy.","pre_registration_requirement":"Configuration checksum and timestamp before control generation/evaluation.","unit_dimension_status":"dimensionless threshold in C02 [0,1], not Phase-D model space","freeze_state":"review_gap","blocks_execution":"yes","review_note":"Direct transfer prohibition is frozen; actual method is not."},
        {"threshold_id":"TE-02","parameter_name":"epsilon_new","source_context":"normalized C02 signed-margin space","allowed_calibration_source":"Calibration-only resolution rule or fixed fraction of preregistered theta-grid spacing.","forbidden_calibration_source":"Observed edge flips, desired near-threshold membership, evaluation outcomes, or Phase-D near-threshold band value.","calibration_method":"not selected: choose one rule and fixed companion sensitivity values.","selection_rule":"Freeze exact value/rule, inclusivity at equality, decimal precision, and same-value requirement across primary/null runs.","pre_registration_requirement":"Configuration checksum and timestamp before any C02 evaluation.","unit_dimension_status":"dimensionless margin on the same C02 scale as theta_new","freeze_state":"review_gap","blocks_execution":"yes","review_note":"R02 schema is frozen but epsilon policy/value is not."},
    ]
    write_csv("05_interface01d_theta_epsilon_freeze_spec.csv", ["threshold_id","parameter_name","source_context","allowed_calibration_source","forbidden_calibration_source","calibration_method","selection_rule","pre_registration_requirement","unit_dimension_status","freeze_state","blocks_execution","review_note"], thresholds)

    split_nulls = [
        {"freeze_id":"SN-01","item_type":"split_strategy","item_id":"calibration_split","item_label":"calibration split","required_configuration":"Immutable member IDs used only for theta/epsilon calibration and permitted control fitting.","fixed_parameters":"membership; fraction/count; stratification; leakage policy; checksum","random_seed_policy":"Seed required if random assignment; otherwise deterministic key rule.","expected_control_behavior":"No evaluation/holdout labels enter calibration.","failure_implication":"No-go due leakage or undefined calibration population.","freeze_state":"missing","blocks_execution":"yes","review_note":"No input population exists."},
        {"freeze_id":"SN-02","item_type":"split_strategy","item_id":"evaluation_split","item_label":"evaluation split","required_configuration":"Immutable held-out member IDs for primary preregistered statistic and all matched controls.","fixed_parameters":"membership; fraction/count; statistic; one-pass policy; checksum","random_seed_policy":"Same assignment seed policy as split generator.","expected_control_behavior":"Parameters remain frozen during evaluation.","failure_implication":"Abort for post-hoc tuning/leakage.","freeze_state":"missing","blocks_execution":"yes","review_note":"No records or split seed."},
        {"freeze_id":"SN-03","item_type":"split_strategy","item_id":"holdout_split","item_label":"final holdout split","required_configuration":"Immutable untouched member IDs opened only if all prior gates pass.","fixed_parameters":"membership; minimum size; access rule; checksum","random_seed_policy":"Frozen with split generation; access logged.","expected_control_behavior":"No calibration, method selection, or debugging uses holdout.","failure_implication":"Holdout invalid; execution result cannot support planned assessment.","freeze_state":"missing","blocks_execution":"yes","review_note":"No records or access protocol."},
        {"freeze_id":"SN-04","item_type":"split_strategy","item_id":"optional_sensitivity_split","item_label":"optional sensitivity split","required_configuration":"Either explicitly excluded or immutable sensitivity membership/purpose fixed before run.","fixed_parameters":"include/exclude decision; membership; allowed analyses; checksum","random_seed_policy":"Required if included and randomly assigned.","expected_control_behavior":"Cannot become a second outcome-shopping evaluation set.","failure_implication":"Unplanned sensitivity claims excluded; repeated tuning triggers abort.","freeze_state":"missing","blocks_execution":"yes","review_note":"Even exclusion decision is not frozen."},
        {"freeze_id":"SN-05","item_type":"nullmodel","item_id":"N01","item_label":"trivial_uniform_phase","required_configuration":"Uniform phase value, pair universe, declared non-phase inputs, expected analytic K/C/A pattern.","fixed_parameters":"phase value; theta/epsilon source; statistic; exact tie handling","random_seed_policy":"none unless ancillary assignment uses randomness","expected_control_behavior":"No unexplained relational heterogeneity.","failure_implication":"Reject phase-structure attribution.","freeze_state":"missing","blocks_execution":"yes","review_note":"Blocked by phase and pair inputs."},
        {"freeze_id":"SN-06","item_type":"nullmodel","item_id":"N02","item_label":"random_phase_shuffle","required_configuration":"Permutation universe/count, statistic, preserved marginals, split boundaries, replacement policy.","fixed_parameters":"permutation count; alpha/effect criterion; tie handling; output schema","random_seed_policy":"Exact master seed plus deterministic per-permutation derivation required.","expected_control_behavior":"Primary structured statistic meets preregistered separation criterion.","failure_implication":"Reject candidate for stated target.","freeze_state":"missing","blocks_execution":"yes","review_note":"No phase input, count, seed, or criterion."},
        {"freeze_id":"SN-07","item_type":"nullmodel","item_id":"N03","item_label":"material_label_shuffle","required_configuration":"Label universe, permitted within-series permutations, map held fixed, split boundaries, statistic.","fixed_parameters":"permutation count; label strata; retention criterion","random_seed_policy":"Exact master seed and deterministic derivation required.","expected_control_behavior":"Frozen material statistic degrades relative to unshuffled mapping.","failure_implication":"No supported material propagation.","freeze_state":"review_gap","blocks_execution":"yes","review_note":"Primary injection map absent."},
        {"freeze_id":"SN-08","item_type":"nullmodel","item_id":"N04","item_label":"mass_order_only_control","required_configuration":"Reviewed isotope rows, rank baseline equation, target statistic, series handling.","fixed_parameters":"included series; rank tie rule; comparison criterion","random_seed_policy":"none unless resampling is separately approved","expected_control_behavior":"Primary path reports incremental behavior beyond frozen mass-only baseline.","failure_implication":"No demonstrated information beyond mass order.","freeze_state":"review_gap","blocks_execution":"yes","review_note":"Rows/statistic and review handling not frozen."},
        {"freeze_id":"SN-09","item_type":"nullmodel","item_id":"N05","item_label":"threshold_randomization_or_sweep_guard","required_configuration":"Full theta grid, epsilon companions, stability statistic/tolerance, minimum window, report-all rule.","fixed_parameters":"grid decimals; selection rule; isolated-effect failure rule","random_seed_policy":"none unless randomized threshold control is used; then exact seed required","expected_control_behavior":"Target behavior is not confined to an isolated tuned threshold.","failure_implication":"Abort threshold interpretation.","freeze_state":"provisional","blocks_execution":"yes","review_note":"Design exists; numerical grid and rules not frozen."},
        {"freeze_id":"SN-10","item_type":"nullmodel","item_id":"N06","item_label":"pipeline_identity_control","required_configuration":"Phase-class merge ledger at F02, affine inversion check at C02, R01 loss and R02 retention audit.","fixed_parameters":"equivalence definitions; tolerances; required columns; failure thresholds","random_seed_policy":"none","expected_control_behavior":"Every information loss is enumerated and intended.","failure_implication":"Block phase/material-specific interpretation.","freeze_state":"provisional","blocks_execution":"yes","review_note":"Schema logic exists; tolerances and inputs not frozen."},
    ]
    write_csv("06_interface01d_split_and_nullmodel_freeze_spec.csv", ["freeze_id","item_type","item_id","item_label","required_configuration","fixed_parameters","random_seed_policy","expected_control_behavior","failure_implication","freeze_state","blocks_execution","review_note"], split_nulls)

    gates = [
        {"gate_id":"G01","gate_label":"candidate chain fixed","gate_type":"acceptance","test_question":"Is only F02/C02/R01 primary with R02 audit?","pass_condition":"Exact formulas and scope frozen.","fail_condition":"Candidate changes after outcomes.","current_status":"pass","source_anchor":"SC-01; SC-02","blocks_execution":"no","recommended_action":"Retain checksum in future config.","review_note":"Scope frozen."},
        {"gate_id":"G02","gate_label":"phase input frozen","gate_type":"blocker","test_question":"Are source, values, pairs, conventions, splits, and checksums immutable?","pass_condition":"PH-01 to PH-04 frozen.","fail_condition":"Any phase-input row missing/provisional/review gap.","current_status":"fail","source_anchor":"PH-01 to PH-04","blocks_execution":"yes","recommended_action":"Provide operational phase snapshot.","review_note":"Core blocker."},
        {"gate_id":"G03","gate_label":"material injection rule frozen","gate_type":"blocker","test_question":"Is dimension-safe injection point/equation approved?","pass_condition":"MR-02 to MR-04 frozen.","fail_condition":"Metadata labels are substituted for a numerical rule or controls are underspecified.","current_status":"fail","source_anchor":"MR-02 to MR-04","blocks_execution":"yes","recommended_action":"Define injection map and controls.","review_note":"Core blocker."},
        {"gate_id":"G04","gate_label":"theta_new calibration frozen","gate_type":"blocker","test_question":"Is one method with split/statistic/grid/ties/failure frozen?","pass_condition":"TE-01 frozen in C02 space.","fail_condition":"Method unresolved or 0.0300 reused.","current_status":"review_gap","source_anchor":"TE-01","blocks_execution":"yes","recommended_action":"Select and preregister method.","review_note":"Direct-transfer guard passes; method does not."},
        {"gate_id":"G05","gate_label":"epsilon_new frozen","gate_type":"blocker","test_question":"Is exact epsilon rule/value preregistered?","pass_condition":"TE-02 frozen before evaluation.","fail_condition":"Outcome-dependent or absent epsilon.","current_status":"review_gap","source_anchor":"TE-02","blocks_execution":"yes","recommended_action":"Choose resolution/grid-based rule.","review_note":"R02 schema alone is insufficient."},
        {"gate_id":"G06","gate_label":"splits frozen","gate_type":"blocker","test_question":"Are calibration/evaluation/holdout/sensitivity memberships and seeds frozen?","pass_condition":"SN-01 to SN-04 frozen and disjoint.","fail_condition":"Any split absent or leakage possible.","current_status":"fail","source_anchor":"SN-01 to SN-04","blocks_execution":"yes","recommended_action":"Freeze after input snapshot exists.","review_note":"Core blocker."},
        {"gate_id":"G07","gate_label":"all six nullmodels frozen","gate_type":"blocker","test_question":"Do N01-N06 have exact inputs/parameters/seeds/statistics/failure actions?","pass_condition":"SN-05 to SN-10 frozen.","fail_condition":"Any null configuration incomplete.","current_status":"fail","source_anchor":"SN-05 to SN-10","blocks_execution":"yes","recommended_action":"Complete every configuration before primary run.","review_note":"All six currently block."},
        {"gate_id":"G08","gate_label":"R02 margin audit frozen","gate_type":"acceptance","test_question":"Is required audit schema and reporting rule fixed?","pass_condition":"SC-02 frozen; no edge-only reporting.","fail_condition":"Margins/provenance omitted.","current_status":"pass","source_anchor":"SC-02; ID-IN-04","blocks_execution":"no","recommended_action":"Instantiate schema after epsilon freeze.","review_note":"Schema passes; G05 remains separate."},
        {"gate_id":"G09","gate_label":"SI/model_units separation preserved","gate_type":"acceptance","test_question":"Are all numerical spaces explicitly separated?","pass_condition":"SC-09 frozen and future validator enforces it.","fail_condition":"Undeclared cross-space arithmetic.","current_status":"pass","source_anchor":"SC-09","blocks_execution":"no","recommended_action":"Retain hard abort validator.","review_note":"Contract-level pass."},
        {"gate_id":"G10","gate_label":"legacy_c_bridge excluded unless found_local","gate_type":"acceptance","test_question":"Is unavailable legacy mapping excluded?","pass_condition":"SC-11 excluded; no execution dependency.","fail_condition":"Mapping enters input without found-local source review.","current_status":"pass","source_anchor":"SC-11; ID-IN-07","blocks_execution":"no","recommended_action":"Keep excluded.","review_note":"Local source remains absent."},
        {"gate_id":"G11","gate_label":"no post-hoc tuning path","gate_type":"blocker","test_question":"Are phase selection, thresholds, epsilon, splits, controls, and statistics frozen before outcomes?","pass_condition":"All blocker specs frozen with checksums/timestamps.","fail_condition":"Any adjustable path remains after outcome access.","current_status":"review_gap","source_anchor":"PH; TE; SN specs","blocks_execution":"yes","recommended_action":"Close G02-G07 first.","review_note":"Current open parameters permit tuning."},
        {"gate_id":"G12","gate_label":"claim boundary passes","gate_type":"acceptance","test_question":"Does contract avoid execution/evidence/metric/mechanism claims?","pass_condition":"All outputs remain within SC-10.","fail_condition":"Any unsupported physical conclusion.","current_status":"pass","source_anchor":"SC-10","blocks_execution":"no","recommended_action":"Repeat scan after future run.","review_note":"Contract-level pass."},
        {"gate_id":"G13","gate_label":"execution clearance decision","gate_type":"blocker","test_question":"Do G02-G08, G10-G12 satisfy gate logic?","pass_condition":"All mandatory gates pass.","fail_condition":"Any mandatory gate fail/review_gap.","current_status":"fail","source_anchor":"G02-G12","blocks_execution":"yes","recommended_action":"Set execution_clearance=no_go.","review_note":"Computed no-go due multiple blockers."},
    ]
    write_csv("07_interface01d_prerun_gate_matrix.csv", ["gate_id","gate_label","gate_type","test_question","pass_condition","fail_condition","current_status","source_anchor","blocks_execution","recommended_action","review_note"], gates)

    reviews = [
        {"review_id":"ID-R01","source_path":"03_interface01d_phase_input_freeze_spec.csv","issue_type":"phase_input_not_frozen","description":"Operational phase source, pair universe, convention, and snapshot are absent.","severity":"high","recommended_resolution":"Provide immutable reviewed phase input and freeze PH-01 to PH-04.","blocks_execution":"yes","review_note":"Mandatory blocker."},
        {"review_id":"ID-R02","source_path":"04_interface01d_material_injection_rule_freeze_spec.csv","issue_type":"material_injection_rule_not_frozen","description":"Injection point/equation and material controls are not frozen.","severity":"high","recommended_resolution":"Approve a dimension-safe map and complete MR-02 to MR-04.","blocks_execution":"yes","review_note":"Mandatory blocker."},
        {"review_id":"ID-R03","source_path":"05_interface01d_theta_epsilon_freeze_spec.csv#TE-01","issue_type":"theta_new_method_not_frozen","description":"Candidate methods exist but no primary method/configuration is selected.","severity":"high","recommended_resolution":"Freeze one method, split, statistic, grid, ties, and failure outcome.","blocks_execution":"yes","review_note":"0.0300 remains prohibited."},
        {"review_id":"ID-R04","source_path":"05_interface01d_theta_epsilon_freeze_spec.csv#TE-02","issue_type":"epsilon_new_not_frozen","description":"No epsilon rule/value or sensitivity companions are frozen.","severity":"high","recommended_resolution":"Select a calibration-only/resolution-based rule before outcomes.","blocks_execution":"yes","review_note":"Mandatory blocker."},
        {"review_id":"ID-R05","source_path":"06_interface01d_split_and_nullmodel_freeze_spec.csv#SN-01-SN-04","issue_type":"splits_not_frozen","description":"Calibration, evaluation, holdout, sensitivity decision, memberships, and seeds are absent.","severity":"high","recommended_resolution":"Freeze disjoint memberships and checksums after input snapshot.","blocks_execution":"yes","review_note":"Mandatory blocker."},
        {"review_id":"ID-R06","source_path":"06_interface01d_split_and_nullmodel_freeze_spec.csv#SN-05-SN-10","issue_type":"nullmodel_configurations_not_frozen","description":"N01-N06 lack complete inputs, parameters, seeds/tolerances, and failure thresholds.","severity":"high","recommended_resolution":"Complete all six configs before primary evaluation.","blocks_execution":"yes","review_note":"Design names are not configurations."},
        {"review_id":"ID-R07","source_path":f"{I01C}/07_interface01c_legacy_c_bridge_review.csv","issue_type":"legacy_c_bridge_not_found_local","description":"Legacy c/line-element source remains not found locally.","severity":"medium","recommended_resolution":"Keep excluded or locate and separately review authoritative source.","blocks_execution":"no","review_note":"Exclusion currently passes G10."},
        {"review_id":"ID-R08","source_path":"Red-Team_2026_05_23.md; QSB_ST_Persoenliche_Abenddatei_2026-05-20.pdf","issue_type":"red_team_warning_self_testing","description":"Named warning anchors are not found locally; self-testing, toy-designed pass conditions, degeneracy, and fingerprint/identity confusion must still be guarded methodologically.","severity":"high","recommended_resolution":"Resolve sources if attribution is needed; independently enforce frozen external-to-outcome inputs, nulls, degeneracy reporting, and non-identity claim boundaries.","blocks_execution":"partial","review_note":"Warnings are contract requirements from the task, not attributed file findings."},
    ]
    write_csv("08_interface01d_open_review_items.csv", ["review_id","source_path","issue_type","description","severity","recommended_resolution","blocks_execution","review_note"], reviews)

    assessment = f"""# QSB-INTERFACE01-D Final Assessment

## Zweck
INTERFACE01-D definiert einen Pre-Run-Freeze-Vertrag fuer einen moeglichen spaeteren Minimaltest von `F02 -> C02 -> R01`. Es wurde kein Test, Nullmodell, Scan oder Simulation ausgefuehrt.

## Input-Sufficiency
Status: `sufficient_for_freeze_contract_with_unresolved_execution_blockers`

INTERFACE01-C/B/A sowie MATERIAL01 und Phase D reichen zur Formulierung des Vertrags. Sie liefern nicht die fehlenden operationalen Inputs oder Parameterentscheidungen.

## Freeze-Scope
Eingefroren sind Kandidatenkette, R02-Auditschema, Trennung der Einheiten-/Modellraeume, Claim-Grenze und Ausschluss der unbelegten Legacy-c-Bridge. Nicht eingefroren sind Phaseninput, Material-Injektion, theta-/epsilon-Parameterpolitik, Splits, Seeds und vollstaendige Nullkonfigurationen.

## Phaseninput
Status: `missing / provisional`; Gate G02: `fail`.

Ein spaeterer Input benoetigt unveraenderliche Quell- und Paar-IDs, phi/delta_phi, dimensionslose Radian-Konvention, explizite 2*pi-Periodizitaet, Split-ID, Reviewstatus und Checksums. Ergebnisabhaengige Auswahl ist verboten.

## Material-Injektionsregel
Status: `missing`; Gate G03: `fail`.

MATERIAL01 darf Labels, Serien, Provenienz und Reviewstatus liefern. Eine numerische Injektion in Phase oder Kandidatengewicht benoetigt eine eigene dimensionssichere Abbildung. Ohne sie sind N03/N04 und jede materialsensitive Auswertung blockiert.

## theta_new und epsilon_new
Status: beide `review_gap`; Gates G04/G05 nicht bestanden.

`theta_new` muss im C02-Raum `[0,1]` kalibriert werden. Phase-D-`0.0300` ist direkt und als versteckter Prior ausgeschlossen. Eine primaere Methode, Split, Statistik, Grid, Tie-Regel und Failure-Policy fehlen. Fuer `epsilon_new` fehlen konkrete Regel, Wert und Sensitivitaetsbegleiter. Post-hoc-Aenderungen sind Abbruchgruende.

## Splits und Nullmodelle
Kalibrierung, Evaluation, Holdout und optionale Sensitivitaet besitzen keine Mitglieder, Seeds oder Checksums. N01-N06 besitzen Designziele, aber keine vollstaendig eingefrorenen Ausfuehrungskonfigurationen. Gates G06/G07: `fail`.

## Legacy-c-Bridge und Warnanker
Die Legacy-c-/Linienelement-Bridge bleibt `not_found_local` und ist aus dem Test ausgeschlossen; G10 besteht dadurch. Die zwei benannten Red-Team-/Abenddatei-Quellen wurden ebenfalls nicht gefunden. Methodische Schutzregeln gegen Self-Testing, Toy-Design, Degeneracy-Verschleierung und Fingerprint-/Identitaetsverwechslung bleiben dennoch Vertragsanforderungen ohne Quellenattribution.

## Pre-Run-Gate-Entscheid
`execution_clearance = no_go`

Mehrere Pflichtgates G02-G07 sowie G11 sind `fail` oder `review_gap`. G13 setzt daher verbindlich `no_go`. Das ist der korrekte Vertragsstatus, kein fehlgeschlagener Physiklauf.

## Claim-Grenze
{CLAIM}

Die Kandidatenkette bleibt ein Testkandidat. Der Vertrag liefert keine Evidenz fuer Mechanismus, Geometrie, Raumzeit oder Gravitation.

## Empfehlung
Keine Ausfuehrung vorbereiten, bevor ein autorisierter Input-Freeze-Block konkrete Phasenrecords und Paaruniversum bereitstellt. Danach in dieser Reihenfolge schliessen: Material-Injektionsentscheidung, theta-/epsilon-Methode, Splits/Seeds, N01-N06-Konfigurationen, reproduzierbarer Config-Hash und erneute Gate-Berechnung. Erst ein vollstaendiger Pass darf einen separaten Ausfuehrungsauftrag ermoeglichen.
"""
    (OUTPUT / "09_interface01d_final_assessment.md").write_text(assessment, encoding="utf-8")

    mandatory_blocked = any(row["gate_id"] in {f"G{i:02d}" for i in range(2, 9)} | {"G10", "G11", "G12"} and row["current_status"] in {"fail", "review_gap"} for row in gates)
    clearance = "no_go" if mandatory_blocked else "go"
    status = "interface01d_minimal_test_freeze_prerun_contract_no_go" if mandatory_blocked else "interface01d_minimal_test_freeze_prerun_contract_completed_with_review_items"
    required_missing = sum(row["read_status"] == "missing" for row in anchors[:14])
    if required_missing:
        status = "interface01d_minimal_test_freeze_prerun_contract_partial_inputs"
    manifest = {
        "run_id": "QSB-INTERFACE01D", "status": status,
        "output_dir": "runs/QSB-INTERFACE01D/minimal_test_freeze_prerun_contract",
        "input_sufficiency": "sufficient_for_freeze_contract_with_unresolved_execution_blockers",
        "execution_clearance": clearance, "input_anchors": len(anchors),
        "freeze_scope_rows": len(scope), "phase_input_rows": len(phase_rows),
        "material_injection_rows": len(material_rows), "theta_epsilon_rows": len(thresholds),
        "split_nullmodel_rows": len(split_nulls), "gate_matrix_rows": len(gates),
        "review_items": len(reviews), "mandatory_blocking_gates": [row["gate_id"] for row in gates if row["blocks_execution"] == "yes" and row["current_status"] in {"fail", "review_gap"}],
        "legacy_c_bridge_source_status": "not_found_local",
        "named_red_team_warning_anchors_status": "not_found_local",
        "mutated_existing_files": False, "generated_synthetic_evidence": False,
        "minimal_test_executed": False, "new_simulation_performed": False,
        "phase_d_rescan_performed": False, "external_research_performed": False,
        "created_utc": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "claim_boundary": CLAIM,
    }
    (OUTPUT / "10_interface01d_run_manifest.json").write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    print(json.dumps(manifest, ensure_ascii=False))


if __name__ == "__main__":
    main()
