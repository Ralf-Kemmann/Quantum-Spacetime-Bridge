# QSB-ST Resonance Matter Signature
## Matter Signature Canonicalization Plan

Guiding principle:

"Die Idee ins Licht. Die Grenzen ans Geländer. Die Details in den Maschinenraum."

## 1. Purpose

This document creates a positive, auditable canonicalization plan for the recovered Matter Signature / Carrier Specificity result cluster. The goal is to preserve the value of the recovered work, make its provenance explicit, and define a restrained path toward reproducible canonical reruns.

The typ_b_analysis / duplicate-quarantine Matter Signature cluster is valuable because it shows that the project had already explored possible RMS carrier-axis candidates across wave-only, mass-only, isotope, carbon isotope, strontium isotope, QC descriptors, shell descriptors, valence descriptors, VDW matter-interaction layer, negative/abs/positive marker channels, bridge carrier blocks, bridge minimal model, and leave-one-out / minimal-set tests.

This document is a provenance, reproducibility, and pre-registration planning document. It is not a rerun, not a result note, and not a validation claim.

## 2. Why canonicalization is needed

The recovered cluster appears to contain many surrogate-level readouts that may be useful for the QSB-ST roadmap, but the currently recoverable status is archival rather than canonical. Canonicalization is needed to separate:

- preserved archival observations from reproducible current results,
- exploratory score behavior from pre-registered hypotheses,
- replay candidates from archival-only records,
- matter-sensitive modifier layers from RMS carrier claims,
- duplicate-quarantine provenance from stable working-tree provenance.

Because many axes were tested, future canonical reruns must avoid accumulating loosely supported axes. The old supported and partly_supported labels should remain archival labels until code, inputs, configs, result files, and rerun conditions are mapped and a minimal canonical rerun is completed.

## 3. Current archival status

Archival source path used as provenance context:

`/home/ralf-kemmann/Downloads/_duplicate_quarantine/run_20260429_091132/files/deBroglie_Kaster_Theorie/debroglie-phase-bridge/debroglie-phase-bridge/typ_b_analysis/results`

The active working-tree `typ_b_analysis/results` directories appeared mostly empty, while the duplicate-quarantine copy contained the actual result files. Therefore the recovered cluster must be treated as archival until code, inputs, configs, result files, and rerun conditions are mapped.

Current status: archival recovered surrogate result cluster, not canonical current result.

## 4. Recovered result clusters

Recovered clusters to preserve in the canonicalization inventory include at least:

- `bridge_carrier_block_c_v1`
- `bridge_carrier_block_d_v1`
- `bridge_carrier_block_e_v1`
- `bridge_carrier_leave_one_out_v1`
- `bridge_carrier_minimal_set_block_b_v1`
- `bridge_minimal_model_v1`
- `debroglie_matter_signature` runs A-D
- `debroglie_matter_signature_isotope` runs A-C
- `debroglie_matter_signature_isotope_carbon` runs A-C
- `debroglie_matter_signature_isotope_strontium` runs A-C
- `debroglie_matter_signature_qc` run A
- `debroglie_matter_signature_qc_shell` run A
- `debroglie_matter_signature_qc_valence` run A
- `debroglie_matter_signature_vdw` runs A-C
- `n1_a1_b1_decoupling_v1`
- `n1_alt_neighborhood_v1`
- `n1_alt_neighborhood_v2`
- `n1_alt_neighborhood_v22`
- `n1_exportclass_nullmodel_v1`
- `n1_negative_vs_abs_markers_v1`
- `n1_negative_vs_abs_v1`

Claim/status inventory to preserve as archival language:

- Matter Signature A-D: `overall_status` partly_supported.
- Matter Signature A-C: `matter_sensitive_status` supported; `mass_only_status` partly_supported; `max_matter_sensitive_delta` 5.0; `tau_candidate_count` 0.
- Matter Signature run D: `overall_status` partly_supported; `max_matter_sensitive_delta` 5.0; `near_window_count` 0.
- Isotope A-C, carbon isotope A-C, and strontium isotope A-C: supported.
- QC, shell, and valence: supported at surrogate level.
- VDW run A: partly_supported.
- VDW B/C: supported overall; `max_wave_delta` 5.0; `max_combined_delta` 2.0; strongest wave candidate hydrogen; strongest combined candidate sodium; VDW3 partly_supported; inspected run C had `tau_response_score` 0.0 / `tau_alignment_score` 0.0 / off_window.
- `n1_a1_b1_decoupling_v1`: supported; combined N1 pattern primarily B1-driven while A1 remains weak across launchable classes.
- `n1_negative_vs_abs_v1` and `n1_negative_vs_abs_markers_v1`: inconclusive.
- Current safest interpretation: shared negative/abs upper block over positive, but no stable internal advantage of negative over abs.
- `n1_alt_neighborhood` v1/v2/v22: inconclusive in listed readouts.
- `n1_exportclass_nullmodel_v1`: supported.

## 5. What must be canonicalized

Canonicalization goals:

1. Locate source files.
2. Locate or reconstruct configs.
3. Locate scripts / code version.
4. Locate input data.
5. Record hashes or file inventories where possible.
6. Identify which results are replayable.
7. Identify which results are archival-only.
8. Create a minimal canonical rerun plan.
9. Pre-register hypotheses before rerun.
10. Keep old supported/partly_supported labels as archival until rerun.

The canonicalization unit is not just a readout file. Each run must be mapped to script, config, input data, environment, output files, and claim/status source where possible.

## 6. Provenance questions

Checklist for each recovered run:

- Which exact script produced each run?
- Which exact input files were used?
- Which config parameters were used?
- Were random seeds set?
- Were thresholds/tau values predeclared or exploratory?
- Were claims generated automatically or manually?
- Are result files complete?
- Can the run be reproduced from files currently available?
- Is the output path canonical or duplicate-quarantine recovered?
- Does the recovered result match any committed repo state?
- Are there hidden dependencies?

## 7. Canonical rerun map

The canonical rerun map should classify each old run as one of:

- archival_only: useful historical record, but not replayable from currently available files.
- replay_candidate: enough provenance may exist for a faithful replay attempt.
- canonical_candidate: suitable for a limited rerun under pre-registered diagnostics and current repository rules.

High-priority canonical rerun families:

- one baseline Matter Signature run,
- one isotope run,
- one carbon isotope or strontium isotope run,
- one QC/shell/valence representative run,
- one VDW disambiguation run,
- one negative/abs/positive marker rerun,
- one bridge minimal model rerun.

The rerun map should not expand the hypothesis space unless a separate pre-registration update is written first.

## 8. Pre-registered hypotheses

These pre-registered hypotheses define the small future rerun target set:

- H1 Matter-sensitive axis: Matter-sensitive descriptors separate cases beyond mass-only ordering under predeclared diagnostics.
- H2 Isotope sensitivity: Isotope changes produce controlled signature shifts without chemical identity overclaiming.
- H3 VDW second-axis test: VDW descriptors add information beyond wave-only ordering and do not reduce to score mixing / normalization artifact.
- H4 negative/abs upper block: negative/abs remain jointly stronger than positive under current controls.
- H5 negative-vs-abs internal separation: negative does not become privileged unless it separates robustly from abs under predeclared tests.
- H6 Carrier caution: Matter Signature axes are modifiers / marker layers unless connected to RMS carrier stability and Geometry Anchor conditions.

## 9. Minimal rerun design

The recommended rerun design is limited, not a broad expansion:

- one baseline Matter Signature run,
- one isotope run,
- one carbon isotope or strontium isotope run,
- one QC/shell/valence representative run,
- one VDW disambiguation run,
- one negative/abs/positive marker rerun,
- one bridge minimal model rerun.

VDW disambiguation must include:

- wave-only,
- VDW-only,
- combined,
- weight sweep,
- permuted VDW parameters,
- mass/lambda-matched controls,
- normalization sensitivity,
- tau-window readout reported even when off-window.

The design should prefer small, auditable reruns with complete output schemas over additional exploratory axes.

## 10. Control hierarchy

Required control hierarchy:

- mass-only controls,
- wave-only controls,
- shuffled matter descriptors,
- permuted VDW descriptors,
- isotope-matched controls,
- label/family shuffles,
- negative/abs/positive marker controls,
- spectrum-matched phase controls where applicable,
- covariance-preserving nulls where applicable,
- known mimic controls if transferred from Carbon / DATA-02E.

Controls should be declared before rerun and reported even when the main diagnostic is off-window or inconclusive.

## 11. Multiple-comparison and score-engineering risks

Because many axes were tested, future canonical reruns must avoid accumulating loosely supported axes.

Requirements:

- predeclared diagnostics,
- predeclared primary endpoints,
- report all tested axes,
- correction or explicit flagging for multiple comparisons,
- no post hoc promotion of the best-looking score,
- blind or semi-blind evaluation where practical.

Score-engineering risk is especially relevant where combined scores, normalization choices, tau windows, and marker channels interact. The canonical plan should treat each such interaction as a risk to be measured, not as automatic support.

## 12. Required outputs and schemas

Future outputs are proposed under:

`runs/QSB-ST-MATTER-SIGNATURE-CANONICALIZATION/provenance_and_rerun_plan_open/`

Do not create this directory as part of this plan.

Proposed files:

- `summary.json`
- `readout.md`
- `archival_cluster_inventory.csv`
- `provenance_status_table.csv`
- `canonical_rerun_map.csv`
- `preregistered_hypotheses.csv`
- `rerun_minimal_design.csv`
- `canonicalization_risk_register.csv`
- `recovered_file_manifest.csv`
- `resolved_plan.json`

### `archival_cluster_inventory.csv`

| field name | field type | field description |
| --- | --- | --- |
| `cluster_id` | string | recovered result cluster identifier |
| `run_id` | string | individual run identifier |
| `source_path` | string | archival source path |
| `result_files_found` | integer | number of result files found |
| `readout_found` | boolean | whether a readout file exists |
| `claims_found` | boolean | whether claims/status file exists |
| `archival_status` | string | archival_only/replay_candidate/canonical_candidate |
| `note` | string | short note |

### `provenance_status_table.csv`

| field name | field type | field description |
| --- | --- | --- |
| `run_id` | string | individual run identifier |
| `script_found` | boolean | whether the producing script was found |
| `config_found` | boolean | whether the exact config was found |
| `input_data_found` | boolean | whether the input data were found |
| `random_seed_found` | boolean | whether a random seed was found |
| `environment_known` | boolean | whether the runtime environment is known |
| `committed_state_known` | boolean | whether the matching committed state is known |
| `reproducibility_status` | string | unknown/partial/replayable/not_replayable |
| `missing_items` | string | missing provenance items |
| `note` | string | short note |

### `canonical_rerun_map.csv`

| field name | field type | field description |
| --- | --- | --- |
| `old_run_id` | string | recovered archival run identifier |
| `proposed_canonical_run_id` | string | proposed canonical rerun identifier |
| `rerun_priority` | string | high/medium/low/defer |
| `rerun_purpose` | string | reason for rerun |
| `required_inputs` | string | required input files or datasets |
| `required_controls` | string | required controls for this rerun |
| `primary_endpoint` | string | predeclared primary endpoint |
| `expected_output_files` | string | expected outputs for the canonical rerun |
| `note` | string | short note |

### `preregistered_hypotheses.csv`

| field name | field type | field description |
| --- | --- | --- |
| `hypothesis_id` | string | hypothesis identifier |
| `hypothesis_text` | string | pre-registered hypothesis text |
| `primary_endpoint` | string | predeclared primary endpoint |
| `required_control` | string | required control condition |
| `success_condition` | string | condition that supports the hypothesis |
| `failure_condition` | string | condition that does not support the hypothesis |
| `claim_safe_interpretation` | string | bounded interpretation if supported |

### `rerun_minimal_design.csv`

| field name | field type | field description |
| --- | --- | --- |
| `canonical_run_id` | string | canonical rerun identifier |
| `run_family` | string | run family name |
| `included` | boolean | whether this run is included in the minimal rerun |
| `reason_for_inclusion` | string | reason for inclusion |
| `required_controls` | string | controls required for this run |
| `primary_diagnostic` | string | predeclared primary diagnostic |
| `warning_mode` | string | warning mode to watch |

### `canonicalization_risk_register.csv`

| field name | field type | field description |
| --- | --- | --- |
| `risk_id` | string | risk identifier |
| `risk_description` | string | risk description |
| `risk_level` | string | low/medium/high |
| `affected_runs` | string | affected run identifiers or families |
| `mitigation` | string | mitigation plan |
| `status` | string | open/mitigated/accepted/deferred |

### `recovered_file_manifest.csv`

| field name | field type | field description |
| --- | --- | --- |
| `file_path` | string | recovered file path |
| `file_role` | string | role of the file in the run |
| `file_type` | string | file type or extension |
| `size_bytes` | integer | file size in bytes |
| `hash_available` | boolean | whether a hash is available |
| `hash_value` | string | recorded hash value if available |
| `associated_run_id` | string | run associated with the file |
| `note` | string | short note |

### `summary.json`

| field name | field type | field description |
| --- | --- | --- |
| `block_id` | string | canonicalization block identifier |
| `status` | string | plan status |
| `archival_source` | string | duplicate-quarantine archival source path |
| `recovered_cluster_count` | integer | number of recovered clusters |
| `recovered_run_count` | integer | number of recovered runs |
| `replay_candidate_count` | integer | number of replay candidates |
| `canonical_rerun_count` | integer | number of proposed canonical reruns |
| `highest_priority_rerun` | string | highest-priority rerun identifier |
| `strongest_warning_mode` | string | most important warning mode |
| `claim_boundary` | array of strings | compact claim boundary statements |

### `readout.md`

| field name | field type | field description |
| --- | --- | --- |
| `section` | string | readout section name |
| `content` | string | human-readable readout content |
| `source_reference` | string | source file or run reference |
| `claim_boundary_reference` | string | boundary note connected to the section |

### `resolved_plan.json`

| field name | field type | field description |
| --- | --- | --- |
| `plan_id` | string | resolved plan identifier |
| `created_from` | string | source planning document |
| `included_runs` | array of strings | canonical reruns selected for execution |
| `excluded_runs` | array of strings | runs deferred or excluded |
| `required_outputs` | array of strings | required output files |
| `approval_status` | string | open/approved/deferred |

## 13. Relationship to PADS-01

PADS-01 tests phase/amplitude/label/pipeline dependence.

Matter Signature Canonicalization tests whether old matter-sensitive axes are reproducible and interpretable.

The two should be linked but not conflated. PADS-01 can help determine whether an apparent signature depends on phase, amplitude, labels, or pipeline behavior. Matter Signature Canonicalization separately asks whether recovered matter-sensitive axes can be mapped, replayed, and rerun under pre-registered controls.

## 14. Relationship to Geometry Anchor and Carrier Criteria

Matter Signature axes remain candidate modifiers / marker layers unless:

- canonical rerun reproduces them,
- PADS-01 separates phase/amplitude/label effects,
- Geometry Anchor conditions are met where distance interpretation is used,
- RMS Carrier/Stability Criteria are satisfied.

Without those links, isotope, QC, shell, valence, VDW, and negative/abs marker effects remain surrogate-level observations or replay candidates, not established physical carriers.

## 15. Failure and warning modes

Required warning modes:

- archival result treated as canonical,
- missing code/config/input provenance,
- score engineering,
- multiple-comparison accumulation,
- post hoc axis promotion,
- VDW normalization artifact,
- isotope result overread as physical validation,
- negative/abs ambiguity ignored,
- Carbon scanner calibration conflated with Matter Signature validation,
- PADS-01 and Matter Signature rerun conflated,
- untracked duplicate-quarantine path treated as stable source.

Any future readout should carry these warning modes forward until resolved or explicitly accepted.

## 16. Compact Claim Boundary

Claim Boundary:

This plan does not:

- rerun Matter Signature analyses,
- validate archival results,
- establish RMS,
- establish Matter Signature axes as physical carriers,
- validate isotope, QC, shell, valence, or VDW descriptors,
- resolve negative/abs carrier ambiguity,
- replace PADS-01,
- replace Geometry Anchor validation,
- provide experimental prediction.

The safest current statement is that the recovered cluster is an archival recovered surrogate result cluster with candidate modifier and marker-layer relevance. Canonical results are not established.

## 17. Recommended next steps

This document implements roadmap step 6:

1. Status-/Claim-Taxonomy
2. Geometry Anchor Conditions
3. RMS Carrier / Stability Criteria
4. Causality & Entropy Anchor Note
5. PADS-01 Spec
6. Matter Signature Canonicalization

Recommended next steps:

1. Create a recovered file manifest from duplicate-quarantine.
2. Map each run to script/config/input/result files.
3. Mark each run as archival-only, replay-candidate, or canonical-candidate.
4. Pre-register hypotheses before rerun.
5. Choose a minimal rerun set.
6. Link results to PADS-01 and Geometry Anchor only after rerun.
7. Keep archival results in inventory language until canonicalized.
