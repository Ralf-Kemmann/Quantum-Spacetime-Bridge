# QSB-ST-LIC01 Tau/Epsilon Phase-Response Config Fields

**Companion file for:**  
`data/qsb_st_lic01_tau_epsilon_phase_response_config.yaml`

**Block:** QSB-ST-LIC01 / LIC01_tau_epsilon  
**Document type:** Config field description  
**Status:** Scaffold companion, no run claim  
**Date:** 2026-05-17

---

## Purpose

This file documents the fields of the LIC01 tau/epsilon phase-response configuration.

The config is a scaffold for a later synthetic runner. It does not construct physical time, proper time, a Lorentzian metric, or empirical validation. It only defines the knobs and expected outputs for a controlled phase-response diagnostic candidate.

---

## Continuous field list

| Field name | Field type | Field description |
|---|---:|---|
| `block.block_id` | string | Fixed project block identifier. Expected value: `QSB-ST-LIC01`. |
| `block.run_id` | string | Specific run label for the first open synthetic phase-response run. |
| `block.status_target` | string | Intended status after adding the config scaffold. |
| `block.construction_route` | string | Selected route for tau-rel construction. |
| `block.design_note` | string | Path to the controlling design note in `docs/`. |
| `claim_boundary.allowed_claim` | string | Compact statement of the allowed claim level. |
| `claim_boundary.disallowed_claims` | list[string] | Terms or claim families that must not be asserted by the run/readout. |
| `baseline.source_mode` | string | Baseline source type; initially synthetic reference only. |
| `baseline.kernel_symbol` | string | Symbolic name of the baseline relational kernel. |
| `baseline.kernel_family` | string | Family/type label of the baseline kernel. |
| `baseline.node_set_mode` | string | Node/object set mode for the first synthetic run. |
| `baseline.require_square_kernel` | boolean | Whether the baseline kernel must be square. |
| `baseline.require_finite_values` | boolean | Whether all baseline values must be finite. |
| `baseline.require_reproducible_ordering` | boolean | Whether node ordering must be deterministic and reproducible. |
| `baseline.notes` | string | Human-readable notes on baseline limitations. |
| `perturbation.perturbation_family` | string | Perturbation family label. |
| `perturbation.operator_symbol` | string | Symbolic name of the perturbation operator. |
| `perturbation.source_selection_mode` | string | Rule for selecting source objects/nodes. |
| `perturbation.target_selection_mode` | string | Rule for selecting target objects/nodes. |
| `perturbation.phase_mode` | string | Preferred phase perturbation mode if complex phase is supported. |
| `perturbation.fallback_mode` | string | Real-valued fallback perturbation mode. |
| `perturbation.preserve_baseline_shape` | boolean | Whether perturbation must preserve matrix shape. |
| `perturbation.epsilon_values` | list[float] | Epsilon sweep values used for perturbation strength. |
| `perturbation.epsilon_zero_required` | boolean | Whether epsilon = 0 must be included as baseline check. |
| `perturbation.symmetric_epsilon_required` | boolean | Whether positive and negative epsilon values must be paired. |
| `perturbation.notes` | string | Human-readable perturbation notes. |
| `response.observable_family` | string | Observable/readout family used to measure target response. |
| `response.response_norm` | string | Norm or distance type used for response magnitude. |
| `response.normalize_response` | boolean | Whether response values should be normalized. |
| `response.normalization_family` | string | Normalization rule for response values. |
| `response.eta` | float | Small numerical stabilizer to avoid division by zero. |
| `response.finite_difference_family` | string | Finite-difference method for estimating small-epsilon slope. |
| `response.finite_difference_epsilon` | float | Epsilon value used for local finite-difference slope. |
| `response.response_integral_family` | string | Rule for integrating response across epsilon sweep. |
| `response.pairwise_score_name` | string | Name of the pairwise response score. |
| `response.tau_rel_transform` | string | Transform from response score to tau-rel candidate. |
| `response.tau_rel_normalization` | string | Normalization rule for tau-rel candidate values. |
| `response.notes` | string | Human-readable notes on response interpretation. |
| `distance.include_distance_D_if_available` | boolean | Whether runner may include existing distance-like comparator D. |
| `distance.distance_source_mode` | string | Source mode for distance-like comparator. |
| `distance.distance_field_name` | string | Output field name for distance-like comparator. |
| `distance.allow_null_distance` | boolean | Whether distance fields may remain null in first run. |
| `distance.notes` | string | Human-readable notes on distance limitations. |
| `interval_candidate.construct_S_rel2_if_distance_available` | boolean | Whether interval-like candidate should be constructed. Initially false. |
| `interval_candidate.formula` | string | Formula string for optional S_rel2 candidate. |
| `interval_candidate.c_eff_values` | list[float] | Scale/sensitivity values for optional c_eff sweep. |
| `interval_candidate.c_eff_default` | float | Default c_eff value. |
| `interval_candidate.c_eff_physical_interpretation_allowed` | boolean | Must remain false in LIC01 synthetic scaffold. |
| `interval_candidate.notes` | string | Human-readable interval-candidate boundary notes. |
| `controls.enabled` | boolean | Whether control families are part of the planned runner design. |
| `controls.control_families` | list[string] | Planned control families for later implementation. |
| `controls.loop_closure_check_enabled` | boolean | Whether loop/closure consistency should be checked if applicable. |
| `controls.component_dominance_check_enabled` | boolean | Whether component dominance should be reported. |
| `controls.c_eff_sensitivity_check_enabled` | boolean | Whether c_eff sensitivity should be reported if interval candidate is enabled. |
| `controls.notes` | string | Human-readable notes on implemented vs planned controls. |
| `outputs.output_dir` | string | Expected run output directory. |
| `outputs.write_summary_json` | boolean | Whether `summary.json` must be written. |
| `outputs.write_readout_md` | boolean | Whether `readout.md` must be written. |
| `outputs.write_config_resolved_json` | boolean | Whether resolved config JSON must be written. |
| `outputs.csv_files.pairwise_response` | string | Filename for pairwise response summary CSV. |
| `outputs.csv_files.response_sweep` | string | Filename for epsilon response sweep CSV. |
| `outputs.csv_files.tau_rel_candidate_matrix` | string | Filename for tau-rel candidate matrix CSV. |
| `outputs.required_summary_keys` | list[string] | Required top-level keys in `summary.json`. |
| `acceptance.config_parse_required` | boolean | Whether YAML parsing is required for acceptance. |
| `acceptance.summary_json_required` | boolean | Whether summary JSON is required for acceptance. |
| `acceptance.csv_parse_required` | boolean | Whether CSV files must parse with `csv.DictReader`. |
| `acceptance.nonzero_pair_count_required` | boolean | Whether pairwise output must contain at least one row. |
| `acceptance.epsilon_values_must_match_config` | boolean | Whether output epsilon values must match resolved config. |
| `acceptance.readout_sections_required` | list[string] | Required sections in the human-readable readout. |
| `acceptance.claim_risk_grep_terms` | list[string] | Terms used for claim-risk grep. |
| `reproducibility.random_seed` | integer | Fixed random seed for deterministic synthetic construction. |
| `reproducibility.deterministic_ordering_required` | boolean | Whether deterministic ordering is mandatory. |
| `reproducibility.hidden_external_dependencies_allowed` | boolean | Must remain false for transparent reproducibility. |
| `reproducibility.runner_should_print_compact_summary` | boolean | Whether runner should print a compact terminal summary. |
| `reproducibility.runner_should_write_resolved_config` | boolean | Whether runner should write resolved config for auditability. |

---

## Claim boundary

This config does not define physical time.  
It does not derive a Lorentzian metric.  
It does not validate spacetime emergence.  
It defines a synthetic, controlled diagnostic setup for later testing of a relational-delay candidate.

---

## Recommended next step

After this config scaffold is committed, the next block should be a runner design or minimal runner file:

```text
scripts/run_qsb_st_lic01_tau_epsilon_phase_response.py
```

That runner should remain synthetic, transparent, and claim-limited.
