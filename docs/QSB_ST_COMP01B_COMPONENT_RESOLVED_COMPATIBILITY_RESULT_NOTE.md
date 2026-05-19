# QSB-ST-COMP01-B Component-Resolved Compatibility Result Note

## 1. Purpose

COMP01-B documents the first component-resolved Compatibility Scanner.

The goal was to:

- diagnostically split psi components,
- use a real/imag proxy as cosine-like / sine-like component split,
- test same-channel and cross-channel overlaps,
- test component balance and component asymmetry,
- check whether component-resolved candidates show better movement than whole-psi metrics.

This result note does not:

- model tau,
- attach `D(A,B)`,
- construct `S_rel2`,
- claim a physical wavefunction,
- claim specificity.

## 2. Repo status anchor

Start status was clean:

```text
## main...origin/main
```

Implementation commit anchor:

```text
683cab7 Add QSB-ST COMP01B component resolved compatibility scanner
```

Plan anchor:

`docs/QSB_ST_COMP01B_COMPONENT_RESOLVED_COMPATIBILITY_INSPECTION_PLAN.md`

Previous result anchor:

`docs/QSB_ST_COMP01_CORRELATION_COMPATIBILITY_SCANNER_RESULT_NOTE.md`

Previous status anchors:

- `COMP01B_component_resolved_compatibility_inspection_planned`
- `COMP01_minimal_scanner_result_documented_candidates_observed_specificity_not_established`
- `LIC01_tau_epsilon_decision_status_after_J_documented`

## 3. Files involved

Script:

`scripts/run_qsb_st_comp01b_component_resolved_compatibility.py`

Run output directory:

`runs/QSB-ST-COMP01B/component_resolved_compatibility_open/`

Outputs:

- `component_compatibility_pairwise.csv`
- `component_compatibility_family_summary.csv`
- `component_compatibility_control_contrast.csv`
- `summary.json`
- `readout.md`
- `config_resolved.json`

Result note:

`docs/QSB_ST_COMP01B_COMPONENT_RESOLVED_COMPATIBILITY_RESULT_NOTE.md`

## 4. Component-resolved scanner implementation

The COMP01-B scanner is an additive new scanner.

The LIC01 runner was not changed.

The COMP01 minimal scanner was not changed.

The scanner uses the synthetic COMP01/LIC01 basis. `psi_i` is still treated as a diagnostic complex row/column local relational fingerprint.

`component_split_mode = real_imag_proxy`

- `real(psi_i)` is read as a cosine-like / in-phase proxy.
- `imag(psi_i)` is read as a sine-like / quadrature proxy.

Component channels are diagnostic decomposition channels, not physical observables by themselves.

Eight metrics were computed:

- `cos_cos_overlap`
- `sin_sin_overlap`
- `cos_sin_cross_overlap`
- `sin_cos_cross_overlap`
- `component_balance_ratio`
- `component_asymmetry_delta`
- `component_resolved_relative_phase_similarity`
- `component_resolved_local_pattern_correlation`

No tau model was constructed.

No `D(A,B)` was attached.

No `S_rel2` was constructed.

## 5. Acceptance summary

Acceptance results:

- `py_compile` OK.
- Run OK.
- Summary keys OK.
- CSV row checks OK.
- Readout section checks OK.
- Claim-risk grep: no matches.
- `git diff --check`: OK.

Status after acceptance showed only:

```text
?? scripts/run_qsb_st_comp01b_component_resolved_compatibility.py
```

Commit after acceptance:

```text
683cab7 Add QSB-ST COMP01B component resolved compatibility scanner
```

## 6. Output files

Row counts:

- `component_compatibility_pairwise.csv`: 320
- `component_compatibility_family_summary.csv`: 5
- `component_compatibility_control_contrast.csv`: 32

Families:

- `structured_local_phase_response`
- `global_phase_shift`
- `random_phase`
- `amplitude_preserved_phase_randomized`
- `label_shuffle`

Metrics:

- `cos_cos_overlap`
- `sin_sin_overlap`
- `cos_sin_cross_overlap`
- `sin_cos_cross_overlap`
- `component_balance_ratio`
- `component_asymmetry_delta`
- `component_resolved_relative_phase_similarity`
- `component_resolved_local_pattern_correlation`

## 7. Befund

The COMP01-B component-resolved scanner is technically implemented.

The three main outputs were generated.

Status values:

- `component_split_mode = real_imag_proxy`
- `specificity_established = False`
- `tau_model_constructed = False`
- `D_AB_attached = False`
- `S_rel2_constructed = False`

Component-resolved candidate movement was observed.

Best candidate metrics:

- `component_asymmetry_delta`
- `component_balance_ratio`
- `component_resolved_local_pattern_correlation`
- `component_resolved_relative_phase_similarity`
- `cos_cos_overlap`
- `sin_sin_overlap`

Warning pattern:

- `label_shuffle` remains problematic for multiple metrics.
- Cross-channel overlaps are warning-heavy.
- `component_resolved_local_pattern_correlation` remains problematic against `random_phase`, `amplitude_preserved_phase_randomized`, and `label_shuffle`.
- `component_resolved_relative_phase_similarity` remains problematic against `global_phase_shift` and `label_shuffle`.
- `cos_cos_overlap` remains problematic against `global_phase_shift` and `label_shuffle`.
- `sin_sin_overlap` remains problematic against `label_shuffle`.

## 8. Candidate movement

Same-channel metrics:

- `cos_cos_overlap` and `sin_sin_overlap` show candidate movement.
- They are more interesting than pure cross-channel overlaps in this first pass.
- `label_shuffle` still remains a problem.

`component_balance_ratio` moves as a possible channel-balance signal. It remains `label_shuffle`-problematic.

`component_asymmetry_delta` moves as a possible signal for the relation between same-channel and cross-channel compatibility. It remains `label_shuffle`-problematic.

`component_resolved_relative_phase_similarity` remains conceptually interesting because it is closer to relative phase fit. It remains problematic against `global_phase_shift` and `label_shuffle`.

`component_resolved_local_pattern_correlation` remains interesting for local fingerprint fit. It remains problematic against `random_phase`, `amplitude_preserved_phase_randomized`, and `label_shuffle`.

Cross-channel overlaps:

- `cos_sin_cross_overlap` and `sin_cos_cross_overlap` are warning-heavy.
- In this minimal form, they appear more useful as diagnostic/control values than as primary candidates.

## 9. Interpretation

COMP01-B provides a focused advance over the COMP01 minimal scanner because component resolution makes additional candidate movement visible.

The strongest working direction is:

- same-channel compatibility,
- component balance,
- component asymmetry,
- component-resolved relative phase / local pattern quantities.

However:

- `label_shuffle` remains the hard problem.
- Cross-channel overlap is not the primary candidate in the minimal form.
- `specificity_established` remains false.

Result:

- Positive movement: yes.
- Specificity established: no.
- Tau model justified: no.
- `D(A,B)` or `S_rel2` step justified: no.

## 10. Hypothese

Possible working hypotheses:

- Same-channel component compatibility could be more structurally relevant than cross-channel compatibility.
- `component_asymmetry_delta` could indicate whether structured correlation is carried more by same-channel than by cross-channel coupling.
- `component_balance_ratio` could provide hints about internal channel organization.
- `label_shuffle` problems indicate that identity-sensitive or locality-sensitive additions are still needed.
- `real_imag_proxy` is useful as a first split, but may still be too coarse compared with an explicit A/B/cos/sin representation.

These hypotheses are synthetic diagnostic hypotheses, not physical claims.

## 11. Offene Lücke

Open gaps:

- No specificity is established.
- `label_shuffle` remains problematic.
- `component_split_mode` is only `real_imag_proxy`.
- No explicit A/B/cos/sin reconstruction from string parameters exists.
- No loop/closure phase was tested.
- No spectral or eigenvalue-related companion factors were tested.
- No larger kernel was tested.
- No tau model was constructed.
- No `D(A,B)` was attached.
- No `S_rel2` was constructed.
- No physical wavefunction is claimed.
- No real-data or experimental claim is made.

## 12. Claim Boundary

- psi is a diagnostic pattern object here, not automatically a physical wavefunction.
- Component-resolved psi channels are diagnostic decomposition channels, not physical observables by themselves.
- psi-overlap is a compatibility observable, not automatically a quantum measurement probability.
- tau is not physical time.
- tau is not proper time.
- tau is not a universal clock.
- COMP01-B does not attach D(A,B).
- COMP01-B does not construct S_rel2.
- COMP01-B does not derive a Lorentzian metric.
- COMP01-B does not validate a physical Bridge.
- COMP01-B does not establish diagnostic specificity yet.
- This is synthetic diagnostic work only.

## 13. Recommended next step

Recommended next step:

`QSB-ST-COMP01-C identity-sensitive component contrast plan`

Possible file:

`docs/QSB_ST_COMP01C_IDENTITY_SENSITIVE_COMPONENT_CONTRAST_PLAN.md`

Goal:

- Do not start a new broad metric cascade.
- Address the `label_shuffle` problem directly.
- Test whether same-channel and component-asymmetry candidates can be made identity-sensitive.
- Inspect pairwise rank and top-pair stability rather than only family means.
- Inspect source-target orientation and local-neighborhood conditioning.

Do not directly proceed to:

- tau model,
- `D(A,B)`,
- `S_rel2`,
- Lorentz interval,
- Bridge validation.

## 14. Current status label

`COMP01B_component_resolved_compatibility_result_documented_candidates_observed_specificity_not_established`
