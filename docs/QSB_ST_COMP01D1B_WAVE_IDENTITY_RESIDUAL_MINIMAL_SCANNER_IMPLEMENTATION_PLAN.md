# QSB-ST-COMP01-D1b Wave Identity Residual Minimal Scanner Implementation Plan

## 1. Purpose

COMP01-D1b is an implementation plan only.

It does not create a scanner. It does not create a config. It does not create runs. It defines what the next Codex step should produce.

Goal of the later scanner:

```text
A minimal synthetic test of whether wave_identity_residual is a diagnostically computable and controllable residual between type-like wave similarity and relational wave identity.
```

This plan does not validate the residual physically and does not establish diagnostic specificity.

## 2. Current status anchor

COMP01-D Concept is documented.

COMP01-D1 Minimal Design Plan is documented.

COMP01-D1a Scanner Specification is documented.

Current commit anchor:

```text
6c64e58 Add QSB-ST COMP01D1a wave identity residual scanner spec
```

Inherited claim brake from COMP01-C3:

```text
specificity_established = false
stable_candidate_metrics = none
```

## 3. Scientific motivation

The working chain is:

```text
tau -> delay -> missing delay-space problem -> spectral/shift analogy -> wave identity residual
```

Core question:

```text
Woran merke ich, dass ich die gleiche, aber nicht dieselbe Welle habe?
```

D1b plans a minimal scanner that does not answer this physically. It makes the question diagnostically testable in a synthetic setting.

The scanner should test whether same type similarity can be separated from same identity behavior by a transparent residual built from spectral, phase, and local slope/intercept components.

## 4. Implementation scope

D1b plans exactly three files for the next implementation step:

- `data/qsb_st_comp01d1b_wave_identity_residual_minimal_config.yaml`
- `scripts/run_qsb_st_comp01d1b_wave_identity_residual_minimal_scanner.py`
- `docs/QSB_ST_COMP01D1B_WAVE_IDENTITY_RESIDUAL_MINIMAL_SCANNER_RESULT_NOTE_TEMPLATE.md`

Optional for later runs, but not created by D1b itself:

- `runs/QSB-ST-COMP01D1B/wave_identity_residual_minimal_open/`

Important:

This D1b task itself creates only this plan under `docs/`.

## 5. Planned files for the next implementation step

YAML config:

- synthetic wave-pair families,
- wave parameters,
- seeds,
- normalization choices,
- aggregation weights,
- output directory.

Python runner:

- reads the config,
- constructs synthetic wave-pair cases,
- computes minimal observables,
- computes `wave_identity_residual`,
- writes machine-readable outputs.

Result note template:

- Befund,
- Interpretation,
- Hypothese,
- Offene Luecke,
- Claim Boundary.

## 6. Minimal input design

The later scanner should not need external real data.

Minimal synthetic input fields:

- `wave_id`
- `pair_id`
- `k`
- `phase`
- `A`
- `B`
- `control_family`
- `control_seed`

Use the real local diagnostic form:

```text
psi_i(x)=A_i cos(k_i x)+B_i sin(k_i x)
```

Use the local tangent form at `x0 = 0`:

```text
intercept_i = A_i
slope_i = B_i * k_i
```

The complex trigonometric extension should be mentioned only as a later route. It must not be forced into the D1b minimal runner.

## 7. Minimal synthetic wave-pair families

Required families for the later minimal runner:

- `exact_duplicate`: same diagnostic wave copied exactly; should produce near-zero residual.
- `small_delta_k_decoy`: near-duplicate with a small k shift; should produce a small spectral residual.
- `small_phase_drift_decoy`: near-duplicate with a small phase drift; should produce a phase residual.
- `amplitude_preserved_perturbation`: preserves amplitude scale while perturbing local A/B or phase parameters.
- `combined_near_duplicate_decoy`: combines small k, phase, and local linear changes to test accumulation.
- `label_shuffle`: breaks pair assignment at the label level.
- `kernel_node_label_shuffle_proxy`: harder proxy for node-level label disruption in the minimal synthetic setting.

## 8. Minimal observables to compute

Required observables:

- `delta_k`
- `relative_k_shift`
- `k_ratio`
- `relative_phase_drift`
- `phase_gradient_delta`
- `intercept_i`
- `intercept_j`
- `delta_intercept_ij`
- `intercept_similarity`
- `slope_i`
- `slope_j`
- `delta_slope_ij`
- `slope_similarity`
- `slope_intercept_balance`
- `local_linear_response_overlap`
- `spectral_identity_distance`
- `wave_identity_residual`

Not required in D1b:

- sidebands,
- envelope features,
- cross-channel leakage,
- full real/imag complex scanner,
- physical redshift.

These may remain later extensions.

## 9. Wave identity residual aggregation rule

The later scanner should use a simple transparent aggregation with no physical weighting claim.

Planned components:

```text
spectral_component = normalized combination of delta_k / relative_k_shift
phase_component = normalized relative_phase_drift or phase_gradient_delta
local_component = normalized combination of delta_intercept_ij and delta_slope_ij
```

Planned aggregate:

```text
wave_identity_residual = transparent weighted mean of spectral_component, phase_component, local_component
```

Required planning rules:

- weights must be explicit in the later YAML,
- default initial weights may be `1/3`, `1/3`, `1/3`,
- no hidden score logic,
- warnings must be emitted for near-zero denominator,
- warnings must be emitted for missing values,
- warnings must be emitted for phase wrapping.

## 10. Control logic

Expected qualitative behavior:

- `exact_duplicate` should produce near-zero residual.
- `small_delta_k_decoy` should produce small spectral residual.
- `small_phase_drift_decoy` should produce phase residual.
- `amplitude_preserved_perturbation` should mainly affect local / intercept / slope components.
- `combined_near_duplicate_decoy` tests whether small shifts accumulate.
- `label_shuffle` and `kernel_node_label_shuffle_proxy` test control mimicry risk.

If controls produce similar or stronger residuals than structured references, the later scanner must set:

```text
control_mimicry_warning
```

## 11. Output schema

Planned later outputs:

- `runs/QSB-ST-COMP01D1B/wave_identity_residual_minimal_open/summary.json`
- `runs/QSB-ST-COMP01D1B/wave_identity_residual_minimal_open/readout.md`
- `runs/QSB-ST-COMP01D1B/wave_identity_residual_minimal_open/wave_identity_pair_summary.csv`
- `runs/QSB-ST-COMP01D1B/wave_identity_residual_minimal_open/control_family_summary.csv`
- `runs/QSB-ST-COMP01D1B/wave_identity_residual_minimal_open/decision_summary.csv`
- `runs/QSB-ST-COMP01D1B/wave_identity_residual_minimal_open/resolved_config.json`

## 12. Continuous field list

| Field name | Field type | Field description |
|---|---|---|
| `pair_id` | string | Stable pair identifier. |
| `wave_id_i` | string | First synthetic diagnostic wave identifier. |
| `wave_id_j` | string | Second synthetic diagnostic wave identifier. |
| `control_family` | string | Synthetic family or control family. |
| `control_seed` | integer/null | Seed used for generated control cases. |
| `k_i` | float | Diagnostic k value for wave i. |
| `k_j` | float | Diagnostic k value for wave j. |
| `delta_k` | float | Absolute difference between k values. |
| `relative_k_shift` | float/null | Normalized k shift with zero-denominator guard. |
| `k_ratio` | float/null | Ratio of k values with near-zero handling. |
| `phase_i` | float | Diagnostic phase value or local phase anchor for wave i. |
| `phase_j` | float | Diagnostic phase value or local phase anchor for wave j. |
| `relative_phase_drift` | float | Structure-internal phase drift between waves. |
| `phase_gradient_delta` | float | Difference in diagnostic phase gradients. |
| `A_i` | float | Local A coefficient for wave i. |
| `A_j` | float | Local A coefficient for wave j. |
| `B_i` | float | Local B coefficient for wave i. |
| `B_j` | float | Local B coefficient for wave j. |
| `intercept_i` | float | Local intercept for wave i. |
| `intercept_j` | float | Local intercept for wave j. |
| `delta_intercept_ij` | float | Absolute intercept difference. |
| `intercept_similarity` | float | Transparently normalized intercept similarity. |
| `slope_i` | float | Local slope for wave i. |
| `slope_j` | float | Local slope for wave j. |
| `delta_slope_ij` | float | Absolute slope difference. |
| `slope_similarity` | float | Transparently normalized slope similarity. |
| `slope_intercept_balance` | float | Joint local slope/intercept balance. |
| `local_linear_response_overlap` | float | Local linear response overlap. |
| `spectral_component` | float | Normalized spectral contribution to residual. |
| `phase_component` | float | Normalized phase contribution to residual. |
| `local_component` | float | Normalized local slope/intercept contribution to residual. |
| `spectral_identity_distance` | float | Spectral identity distance candidate. |
| `wave_identity_residual` | float | Transparent aggregate diagnostic residual. |
| `duplicate_sanity_distance` | float | Residual for exact duplicate sanity check. |
| `near_duplicate_decoy_distance` | float | Residual for near-duplicate decoy. |
| `control_reference_ratio` | float/null | Ratio between reference and control residuals. |
| `decision_status` | string | Conservative decision label. |
| `warning_flags` | string | Semicolon-separated warnings. |
| `interpretation_note` | string | Short note separating observation from interpretation. |

## 13. Acceptance checks for the later runner

The later runner should satisfy at least these checks:

- YAML config parses.
- Python script runs without external data dependency.
- `summary.json` exists and parses.
- `readout.md` exists.
- all expected CSV outputs exist.
- CSVs parse with `csv.DictReader`.
- `exact_duplicate` produces near-zero `wave_identity_residual`.
- `specificity_established` remains false unless explicit later criteria exist.
- decision labels do not claim proof.
- `readout.md` separates Befund / Interpretation / Hypothese / Offene Luecke / Claim Boundary.
- `git diff --check` passes.

## 14. Readout structure

Later `readout.md` should contain:

```text
# QSB-ST-COMP01-D1b Wave Identity Residual Minimal Scanner Readout

## Befund
## Interpretation
## Hypothese
## Offene Luecke
## Claim Boundary
## Machine-readable status
```

## 15. Interpretation rules

Numerical Befund must be separated from interpretation.

Befund:

- Which residuals were observed?

Interpretation:

- What does that mean only inside the synthetic diagnostic model?

Hypothese:

- Why could this matter for later wave identity diagnostics?

Offene Luecke:

- no physical validation,
- no specificity,
- no real data,
- no Lorentz structure.

## 16. What this implementation plan must not do

This implementation plan:

- does not implement the scanner
- does not create config files
- does not create run outputs
- does not attach D(A,B)
- does not construct S_rel2
- does not introduce tau as physical time
- does not derive proper time
- does not derive a Lorentzian metric
- does not validate the physical Bridge
- does not claim physical wavefunctions
- does not establish diagnostic specificity
- does not claim fermionic Pauli exclusion
- does not invoke spin-statistics
- does not claim cosmological redshift
- does not create matter particles

## 17. Claim Boundary

psi is a diagnostic pattern object here, not automatically a physical wavefunction.

wave_identity_residual is a diagnostic distinguishability construct, not a physical observable by itself.

"wave-Pauli" is a heuristic internal analogy only.

It does not claim fermionic Pauli exclusion.

It does not invoke quantum spin-statistics.

It does not assert a physical exclusion principle.

type-like similarity is not the same as relational identity.

spectral shift is used here as a diagnostic analogy, not as cosmological redshift.

phase drift is used here as a structure-internal pattern marker, not as physical time delay.

tau is not physical time.

tau is not proper time.

tau is not a universal clock.

COMP01-D1b does not attach D(A,B).

COMP01-D1b does not construct S_rel2.

COMP01-D1b does not derive a Lorentzian metric.

COMP01-D1b does not validate a physical Bridge.

COMP01-D1b does not establish diagnostic specificity yet.

This is synthetic diagnostic implementation planning only.

## 18. Current status label

```text
current_status_label: COMP01D1B_wave_identity_residual_minimal_scanner_implementation_plan_created
```
