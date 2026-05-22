# QSB-ST COMP01-WIFM01B Minimal Metric Sensitivity Sweep — Result Note

## 1. Purpose

This result note documents the already-created WIFM01B minimal metric sensitivity sweep output.

WIFM01B is a synthetic diagnostic sensitivity sweep. It varies explicit diagnostic weights and explicit toy normalization scales, uses curated variants only rather than full Cartesian bloat, and checks stability of the WIFM01 toy behavior.

It does not validate a physical model, does not establish diagnostic specificity, and does not create physical compact dimensions, spacetime geometry, Hilbert reconstruction, or Bridge confirmation.

## 2. Inputs inspected

Context/spec/result docs inspected:

- `docs/QSB_ST_COMP01_WIFM01_MINIMAL_METRIC_RESULT_NOTE.md`
- `docs/QSB_ST_COMP01_WIFM01B_MINIMAL_METRIC_SENSITIVITY_SWEEP_SPEC.md`
- `docs/QSB_ST_COMP01_WAVE_IDENTITY_FINGERPRINT_PARAMETER_SPACE_MINIMAL_METRIC_SPEC.md`
- `docs/QSB_ST_COMP01_WAVE_IDENTITY_FINGERPRINT_PARAMETER_SPACE_MINIMAL_METRIC_RUNNER_SPEC.md`
- `docs/QSB_ST_COMP01_NEXT_ROUTE_SEED_WAVE_IDENTITY_FINGERPRINT_PARAMETER_SPACE.md`

Implementation files inspected:

- `data/qsb_st_comp01_wifm01b_minimal_metric_sensitivity_sweep_config.yaml`
- `scripts/run_qsb_st_comp01_wifm01b_minimal_metric_sensitivity_sweep.py`

Run outputs inspected:

- `runs/QSB-ST-COMP01-WIFM01B/minimal_metric_sensitivity_sweep_open/summary.json`
- `runs/QSB-ST-COMP01-WIFM01B/minimal_metric_sensitivity_sweep_open/readout.md`
- `runs/QSB-ST-COMP01-WIFM01B/minimal_metric_sensitivity_sweep_open/sweep_variant_summary.csv`
- `runs/QSB-ST-COMP01-WIFM01B/minimal_metric_sensitivity_sweep_open/pair_metric_sweep_long.csv`
- `runs/QSB-ST-COMP01-WIFM01B/minimal_metric_sensitivity_sweep_open/case_family_stability_summary.csv`
- `runs/QSB-ST-COMP01-WIFM01B/minimal_metric_sensitivity_sweep_open/label_stability_summary.csv`
- `runs/QSB-ST-COMP01-WIFM01B/minimal_metric_sensitivity_sweep_open/phase_wrap_stability_summary.csv`
- `runs/QSB-ST-COMP01-WIFM01B/minimal_metric_sensitivity_sweep_open/noncompact_separation_stability_summary.csv`
- `runs/QSB-ST-COMP01-WIFM01B/minimal_metric_sensitivity_sweep_open/ambiguity_stability_summary.csv`
- `runs/QSB-ST-COMP01-WIFM01B/minimal_metric_sensitivity_sweep_open/resolved_config.json`

The run outputs are stored under `runs/`. Depending on repository policy and ignore rules, such outputs may be ignored by normal git status.

## 3. Method summary

WIFM01B uses the WIFM01 baseline config and outputs. The runner confirms the WIFM01 baseline before the sweep, creates curated variants from `weight_variants` and `scale_variants`, uses the baseline toy fingerprints and toy pairs, computes the same WIFM01 metric logic for every variant and pair, compares labels against internal baseline labels, writes summary/readout/CSV outputs, and keeps claim-boundary flags false.

The sweep changes only diagnostic weights and explicit toy normalization scales. It does not infer physical units and does not auto-tune values.

## 4. Befund

Actual `summary.json` values inspected from `runs/QSB-ST-COMP01-WIFM01B/minimal_metric_sensitivity_sweep_open/summary.json`:

```yaml
block_id: QSB-ST-COMP01-WIFM01B
run_id: minimal_metric_sensitivity_sweep_open
sweep_version: wifm01b_weight_scale_sensitivity_v1
baseline_source_block_id: QSB-ST-COMP01-WIFM01
variant_count: 19
weight_variant_count: 10
scale_variant_count: 9
curated_variants_only: true
case_family_count: 5
comparison_pair_count_per_variant: 5
all_variants_expected_behaviors_met: true
variant_warning_review_count: 0
variant_failure_review_count: 0
phase_wrap_all_variants_corrected: true
noncompact_separation_all_variants_preserved: true
mixed_ambiguity_all_variants_preserved: true
stability_label_counts:
  baseline_reference: 2
  stable_expected_behavior_preserved: 17
specificity_established: false
phase_is_physical: false
phase_is_synthetic_diagnostic: true
physical_metric_established: false
physical_compact_dimensions_established: false
hilbert_space_reconstruction: false
bridge_confirmation: false
mastermind_status: parked_not_implemented
knuth_status: parked_not_implemented
manifold_status: parked_not_implemented
```

WIFM01B produced a green synthetic diagnostic sensitivity sweep: all curated variants preserved the expected WIFM01 toy behavior, no warning-review variant occurred, and no failure-review variant occurred.

## 5. Variant sweep result

The sweep contains 19 curated variants:

- 10 weight variants
- 9 scale variants
- `baseline_reference: 2`
- `stable_expected_behavior_preserved: 17`
- no `sensitivity_warning_review_needed`
- no `diagnostic_failure_review_needed`
- `curated_variants_only: true`

This was not a Cartesian sweep and did not create combinatorial bloat. The weights and scales are diagnostic choices, not physical parameters.

## 6. Phase-wrap stability result

`phase_wrap_all_variants_corrected: true`.

The `phase_wrap_equivalent` case was corrected in all 19 variants. In every phase-wrap row, circular phase delta remained smaller than naive phase delta, and circular metric distance remained smaller than naive metric distance.

Interpretation: circular phase handling is stable under the curated diagnostic perturbations.

Claim boundary: this is diagnostic phase-coordinate handling only.

## 7. Non-compact separation stability result

`noncompact_separation_all_variants_preserved: true`.

Across all variants:

- `same_looking_not_same_delta_k` remained `noncompact_difference_preserved`
- `same_looking_not_same_slope_intercept` remained `local_shape_difference_preserved`

Interpretation: circular phase handling and weight/scale perturbation do not collapse non-compact diagnostic separations in the curated sweep.

Claim boundary: this is diagnostic separation only, with no physical identity proof.

## 8. Mixed ambiguity stability result

`mixed_ambiguity_all_variants_preserved: true`.

Across all variants, `mixed_ambiguity_case` remained `mixed_ambiguity_preserved`.

Interpretation: the ambiguity band remains stable in the curated sweep.

Claim boundary: ambiguity handling is diagnostic only.

## 9. Label stability result

Actual `diagnostic_decision_label_count_ranges` from `summary.json`:

```yaml
diagnostic_warning_review_needed:
  baseline_count: 0
  min: 0
  max: 0
  variant_count_with_label: 0
local_shape_difference_preserved:
  baseline_count: 1
  min: 1
  max: 1
  variant_count_with_label: 19
metric_equivalent_expected:
  baseline_count: 1
  min: 1
  max: 1
  variant_count_with_label: 19
mixed_ambiguity_preserved:
  baseline_count: 1
  min: 1
  max: 1
  variant_count_with_label: 19
noncompact_difference_preserved:
  baseline_count: 1
  min: 1
  max: 1
  variant_count_with_label: 19
phase_wrap_corrected_by_circular_metric:
  baseline_count: 1
  min: 1
  max: 1
  variant_count_with_label: 19
```

Interpretation: no diagnostic label drift occurred in the curated sweep.

Claim boundary: label stability is diagnostic only.

## 10. Output artifacts

The inspected WIFM01B output artifacts are:

- summary.json
- readout.md
- sweep_variant_summary.csv: 19 rows
- pair_metric_sweep_long.csv: 95 rows
- case_family_stability_summary.csv: 5 rows
- label_stability_summary.csv: 6 rows
- phase_wrap_stability_summary.csv: 7 rows
- noncompact_separation_stability_summary.csv: 5 rows
- ambiguity_stability_summary.csv: 5 rows
- resolved_config.json

Full run outputs remain in `runs/` and should not be force-added by default unless a deliberate package/digest decision is made.

## 11. Interpretation

WIFM01B confirms that the WIFM01 toy behavior is stable under the curated diagnostic weight/scale perturbations. It reduces the risk that WIFM01 was only a single baseline weighting/scale artifact and makes the circular/torus-aware diagnostic metric route more auditable.

The result supports continuing toward adversarial/ambiguity stress cases. It does not reconstruct physical phase, does not identify physical compact dimensions, does not establish a physical metric, does not settle wave identity, does not reconstruct Hilbert space, does not provide Bridge confirmation, and does not establish diagnostic specificity.

## 12. Hypothese

WIFM01B supports the working hypothesis that circular/torus-aware diagnostic treatment of phase-like fingerprint coordinates remains methodologically stable in the small synthetic toy setting under curated weight/scale perturbations.

This remains a hypothesis only.

## 13. Offene Lücke

- tiny synthetic toy set only
- no real data
- curated variants only
- no full Cartesian sweep
- no broad control set yet
- no adversarial stress cases yet
- no expanded ambiguity families yet
- no physical model validation
- no diagnostic specificity
- no physical phase reconstruction
- no physical compact dimensions
- no physical wavefunction
- no Hilbert-space reconstruction
- no Lorentzian metric
- no physical spacetime geometry
- no Pauli/spin-statistics claim
- no Bridge confirmation
- identity space remains open
- metric weights/scales remain diagnostic choices, not physical parameters
- normalization scales are explicit toy scales and not physical units

## 14. Claim Boundary

- synthetic diagnostic sensitivity sweep result only
- no physical phase
- no physical metric
- no physical manifold
- no physical compact dimensions
- no string compactification claim
- no physical model validation
- no diagnostic specificity
- no Hilbert-space reconstruction
- no conversion of fingerprint metric into spacetime metric
- specificity_established: false
- phase_is_physical: false
- phase_is_synthetic_diagnostic: true
- physical_metric_established: false
- physical_compact_dimensions_established: false
- hilbert_space_reconstruction: false
- bridge_confirmation: false
- Mastermind, Knuth, manifold, and role-permutation remain parked

## 15. Consequence for next step

Recommended next block:

`QSB-ST-COMP01-WIFM01C Adversarial / Ambiguity Stress Case Specification`

Purpose:

- add stronger same-looking/not-same toy cases
- add phase-wrap cases with conflicting non-compact channels
- add cases where phase agrees but local shape disagrees
- add cases where multiple small differences accumulate
- test that WIFM metric does not over-clean ambiguous or adversarial fingerprints
- no physical claims

WIFM01C should be specified before implementation.

## 16. Files created / checked

This task creates only:

- `docs/QSB_ST_COMP01_WIFM01B_MINIMAL_METRIC_SENSITIVITY_SWEEP_RESULT_NOTE.md`

Checked context/spec/result docs:

- `docs/QSB_ST_COMP01_WIFM01_MINIMAL_METRIC_RESULT_NOTE.md`
- `docs/QSB_ST_COMP01_WIFM01B_MINIMAL_METRIC_SENSITIVITY_SWEEP_SPEC.md`
- `docs/QSB_ST_COMP01_WAVE_IDENTITY_FINGERPRINT_PARAMETER_SPACE_MINIMAL_METRIC_SPEC.md`
- `docs/QSB_ST_COMP01_WAVE_IDENTITY_FINGERPRINT_PARAMETER_SPACE_MINIMAL_METRIC_RUNNER_SPEC.md`
- `docs/QSB_ST_COMP01_NEXT_ROUTE_SEED_WAVE_IDENTITY_FINGERPRINT_PARAMETER_SPACE.md`

Checked config/runner:

- `data/qsb_st_comp01_wifm01b_minimal_metric_sensitivity_sweep_config.yaml`
- `scripts/run_qsb_st_comp01_wifm01b_minimal_metric_sensitivity_sweep.py`

Checked run outputs:

- `runs/QSB-ST-COMP01-WIFM01B/minimal_metric_sensitivity_sweep_open/summary.json`
- `runs/QSB-ST-COMP01-WIFM01B/minimal_metric_sensitivity_sweep_open/readout.md`
- `runs/QSB-ST-COMP01-WIFM01B/minimal_metric_sensitivity_sweep_open/sweep_variant_summary.csv`
- `runs/QSB-ST-COMP01-WIFM01B/minimal_metric_sensitivity_sweep_open/pair_metric_sweep_long.csv`
- `runs/QSB-ST-COMP01-WIFM01B/minimal_metric_sensitivity_sweep_open/case_family_stability_summary.csv`
- `runs/QSB-ST-COMP01-WIFM01B/minimal_metric_sensitivity_sweep_open/label_stability_summary.csv`
- `runs/QSB-ST-COMP01-WIFM01B/minimal_metric_sensitivity_sweep_open/phase_wrap_stability_summary.csv`
- `runs/QSB-ST-COMP01-WIFM01B/minimal_metric_sensitivity_sweep_open/noncompact_separation_stability_summary.csv`
- `runs/QSB-ST-COMP01-WIFM01B/minimal_metric_sensitivity_sweep_open/ambiguity_stability_summary.csv`
- `runs/QSB-ST-COMP01-WIFM01B/minimal_metric_sensitivity_sweep_open/resolved_config.json`
