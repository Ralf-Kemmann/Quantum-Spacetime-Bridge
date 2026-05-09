# BMS-FU02g4c - Full Raw-Order Replay Certification Preflight Field List

**Date:** 2026-05-09
**Project:** Quantum-Spacetime Bridge / Gravitation und RaumZeit
**Artifact:** Field list for FU02g4c full raw-order replay certification preflight config
**Claim level:** preflight only

## Purpose

This field list documents the preflight config:

`data/bms_fu02g4c_full_raw_order_replay_certification_preflight_config.yaml`

The preflight config inventories the intended inputs, original FU02g4c bundle
requirements, candidate targets, risk checks, and claim boundaries for a later
full raw-order replay certification pass.

It does not itself run FU02g4c replay, certify raw-order coverage, or establish
candidate-level scientific claims.

## Status Vocabulary

### `preflight_only`
Configuration and input audit mode. No long replay run is authorized.

### `full_raw_order_replay_ready`
May only be used after a separate preflight runner verifies that the exact
original FU02g4c enumerator, full input bundle, isolated output directory, and
candidate mapping requirements are all satisfied.

### `needs_config_clarification`
Inputs are mostly present, but index semantics, output isolation, candidate
mapping, or original bundle reuse is not fully resolved.

### `not_executable_as_full_replay`
At least one required script, input, mapping table, or output-isolation condition
is missing.

### `not_certified`
No full raw-order replay certification claim is supported.

## Config Fields

## `run`

### `run.run_id`
Stable identifier for the preflight config.

### `run.case_id`
Human-readable case identifier.

### `run.output_dir`
Intended isolated output directory for preflight artifacts.

### `run.mode`
Execution mode. For this config the value is `preflight_only`.

### `run.allow_long_replay_run`
Boolean. Must be false for preflight-only use.

### `run.allow_existing_fu02g4c_anchor_mutation`
Boolean. Must remain false to protect existing FU02g4c anchor artifacts.

### `run.allow_existing_output_overwrite`
Boolean. Must remain false unless an explicit later task allows overwriting.

### `run.require_isolated_output_dir`
Boolean. Requires new outputs to be kept separate from existing FU02g4c output
surfaces.

### `run.claim_full_certification_after_preflight`
Boolean. Must remain false. Preflight alone cannot complete certification.

## `original_fu02g4c_bundle`

### `original_fu02g4c_bundle.base_config_yaml`
Primary FU02g4c base config path.

### `original_fu02g4c_bundle.enumerator_script`
FU02g4c connected-patch enumeration script expected for raw-order replay.

### `original_fu02g4c_bundle.c60_cells_csv`
C60 reference cells input.

### `original_fu02g4c_bundle.c60_edges_csv`
C60 reference edges input.

### `original_fu02g4c_bundle.fu02f1_face_layout_csv`
FU02f1 repaired face layout input used by the FU02g4c bundle.

### `original_fu02g4c_bundle.existing_fu02g4c_run_dir`
Existing FU02g4c run directory to inventory but not mutate.

### `original_fu02g4c_bundle.existing_fu02g4c_inspect_config_glob`
Glob for existing FU02g4c inspect-window configs.

### `original_fu02g4c_bundle.existing_fu02g4c_log_globs`
List of log globs for existing FU02g4c inspect, chunk, or segment logs.

### `original_fu02g4c_bundle.existing_known_exact_patch_photo_json`
Existing FU02g4c exact-patch photo for the known exact positive-control target.

## `candidate_inputs`

### `candidate_inputs.g5e1_candidates_csv`
FU02g5e1 near-match candidate table.

### `candidate_inputs.g5e2_classification_csv`
FU02g5e2 candidate classification table.

### `candidate_inputs.g5f_revalidation_csv`
FU02g5f candidate revalidation table.

### `candidate_inputs.g5g_replay_certification_csv`
FU02g5g candidate replay certification table.

### `candidate_inputs.g5g2_per_index_photo_certification_csv`
FU02g5g2 per-index photo certification table.

### `candidate_inputs.face_graph_edges_csv`
FU02d1 repaired face graph edge table.

## `preflight_checks`

### `preflight_checks.require_all_input_paths_exist`
All configured input paths must exist before any full replay is considered.

### `preflight_checks.require_no_existing_output_overwrite`
Existing outputs must not be overwritten.

### `preflight_checks.require_output_dir_is_not_existing_fu02g4c_anchor_dir`
Preflight or replay output must not target the existing FU02g4c anchor
directory.

### `preflight_checks.require_original_enumerator_declared`
The exact intended FU02g4c enumerator must be declared.

### `preflight_checks.require_original_input_bundle_declared`
All original FU02g4c input-bundle paths must be declared.

### `preflight_checks.require_index_semantics_declared`
The raw-index interpretation must be explicit.

### `preflight_checks.require_candidate_mapping_table`
A candidate mapping/certification table must be available.

### `preflight_checks.require_candidate_005_separate_row`
`candidate_005` must be reported separately as the coarse-signature degeneracy
stress case.

### `preflight_checks.require_candidate_008_separate_row`
`candidate_008` must be reported separately as the positive-control known exact
candidate.

### `preflight_checks.require_near_vs_exact_status_columns`
Outputs must distinguish near-match, exact-match, and isomorphism status.

### `preflight_checks.require_raw_order_coverage_audit_before_claim`
No full raw-order claim may be made before coverage has been audited.

## `index_semantics`

### `index_semantics.expected_semantics`
Text definition of raw-index semantics. Current expected meaning: skip
`raw_index` connected patches, then inspect or capture the next patch.

### `index_semantics.must_be_verified_against_fu02g4c_enumerator`
Boolean. Requires confirmation against the FU02g4c enumerator before full
certification.

### `index_semantics.scaffold_indices_are_not_assumed_certified_raw_order_indices`
Boolean. Scaffold-style indices must not be silently treated as certified
FU02g4c raw-order indices.

## `certification_targets`

### `certification_targets[].candidate_id`
Candidate identifier.

### `certification_targets[].raw_index`
Configured raw index for the candidate.

### `certification_targets[].target_role`
Candidate role in the preflight certification target list.

### `certification_targets[].expected_exact_match`
Expected exact-match status from prior candidate tables.

### `certification_targets[].expected_near_distance`
Expected near-distance value from prior candidate tables.

### `certification_targets[].must_report_separately`
Boolean. The target must have its own row or explicit readout section.

### `certification_targets[].claim_boundary`
Target-specific negative-claim boundary.

## Required Target Semantics

### `candidate_005`
Coarse-signature degeneracy stress case at raw index `26157530`.

Expected status:

- `expected_exact_match: false`
- `expected_near_distance: 0`
- near distance zero must not be interpreted as identity or isomorphism

### `candidate_008`
Positive-control known exact candidate at raw index `26187175`.

Expected status:

- `expected_exact_match: true`
- `expected_near_distance: 0`
- positive control only; not a substitute for full raw-order coverage

## `full_replay_requirements`

### `full_replay_requirements.full_fu02g4c_replay_certification_default`
Default full-certification flag. Must remain false unless all replay
requirements are satisfied.

### `full_replay_requirements.require_exact_original_fu02g4c_enumerator_reused`
Requires replay with the exact original FU02g4c enumerator.

### `full_replay_requirements.require_full_original_input_bundle_reused`
Requires the full original FU02g4c input bundle.

### `full_replay_requirements.require_no_fu02g4c_anchor_file_mutation`
Requires that existing FU02g4c anchor artifacts are not modified.

### `full_replay_requirements.require_isolated_new_outputs`
Requires new outputs in an isolated location.

### `full_replay_requirements.require_complete_raw_order_coverage_or_explicit_gap_report`
Requires complete raw-order coverage or an explicit gap report.

### `full_replay_requirements.require_per_candidate_node_edge_photo_outputs`
Requires per-candidate node and edge photo artifacts.

### `full_replay_requirements.require_candidate_replay_certification_table`
Requires a candidate replay certification table.

### `full_replay_requirements.require_readout_md`
Requires a human-readable readout.

### `full_replay_requirements.require_summary_json`
Requires a structured summary JSON.

## `known_risks_to_report`

### Risk list
Explicit risks that must be carried into the preflight readout:

- incomplete raw-order coverage
- scaffold/window replay mistaken for full raw-order replay
- ambiguous candidate mapping
- unclear near-match vs exact-match status
- candidate_005 degeneracy not separately reported
- candidate_008 positive control not separately reported
- untracked files or outputs influencing replay interpretation

## `claim_boundary`

### `claim_boundary.after_preflight_allowed`
Statements allowed after preflight: inventory and readiness/risk assessment only.

### `claim_boundary.after_preflight_not_allowed`
Statements not allowed after preflight: completed full certification, fully
certified candidates, candidate_005 exactness, near-distance identity, or global
non-genericity.

## Expected Future Preflight Outputs

The config does not create outputs by itself. A later preflight runner may write:

- `summary.json`
- `input_inventory.csv`
- `candidate_target_check.csv`
- `raw_order_coverage_preflight.csv`
- `claim_boundary_readout.md`

These outputs should remain in the configured isolated output directory and must
not overwrite existing FU02g4c artifacts.
