# QSB-ST-COMP01-D1a Wave Identity Residual Scanner Specification

## 1. Purpose

COMP01-D1a is a scanner specification only.

It defines how a later minimal scanner could test whether two waves or diagnostic pattern objects appear type-like while not carrying the same relational identity.

No implementation is introduced here. No config file is created. No run output is created. No physical evidence is claimed.

D1a operationalizes the D1 plan around this diagnostic question:

```text
How can a later scanner test whether two waves or diagnostic patterns look same-type but do not carry the same relational identity?
```

## 2. Current status anchor

COMP01-D Concept is documented.

COMP01-D1 Minimal Design Plan is documented.

COMP01-C2 found interesting candidates:

- `sin_sin_overlap`
- `component_resolved_relative_phase_similarity`

COMP01-C3 did not confirm these candidates as stable under the real kernel / node-level `label_shuffle` smoke test.

Required status anchors:

```text
specificity_established = false
stable_candidate_metrics = none
```

## 3. Conceptual core: same type, not same identity

Core question:

```text
Woran merke ich, dass ich die gleiche, aber nicht dieselbe Welle habe?
```

Here, same type means type-like wave similarity:

- two waves or diagnostic patterns look formally similar,
- they may share similar k, phase, local slope, intercept, or overlap behavior,
- they may be difficult to separate with coarse compatibility observables.

Here, same identity means relational wave identity:

- two waves or diagnostic patterns carry the same relational fingerprint,
- their spectral, phase-drift, and local slope/intercept signatures remain aligned under the required controls,
- their identity relation survives duplicate sanity checks and harder null controls.

D1a specifies a diagnostic residual between these two levels.

Required term:

```text
wave_identity_residual
```

## 4. Heuristic note: wave-Pauli analogy

The internal working analogy is:

```text
wave-Pauli / Wellen-Pauli-Verbot
```

This is strictly heuristic and defensive.

It is:

- not fermionic Pauli exclusion,
- not spin-statistics,
- not a quantum exclusion principle,
- not a claim that two physical waves cannot occupy a state.

The intended diagnostic meaning is narrower:

```text
Identical-looking diagnostic patterns may still require distinguishable relational identity fingerprints.
```

## 5. Scanner question

Core scanner question:

```text
Can a diagnostic scanner distinguish type-like wave similarity from relational wave identity?
```

Deutsch:

```text
Kann ein Scanner erkennen, dass zwei Wellen gleichartig aussehen, aber nicht dieselbe relationale Identität tragen?
```

## 6. Inputs for later implementation

Hypothetical later inputs:

- `pair_id`
- `wave_id_i`
- `wave_id_j`
- `k_i`
- `k_j`
- `phase_i`
- `phase_j`
- `A_i`
- `A_j`
- `B_i`
- `B_j`
- optional real/imag channel values
- `control_family`
- `control_seed`

No such input files are created in this specification.

## 7. Minimal observables

D1a should focus only on this core set:

- `delta_k`
- `relative_k_shift`
- `k_ratio`
- `relative_phase_drift`
- `phase_gradient_delta`
- `delta_intercept_ij`
- `delta_slope_ij`
- `intercept_similarity`
- `slope_similarity`
- `slope_intercept_balance`
- `local_linear_response_overlap`
- `spectral_identity_distance`
- `wave_identity_residual`

Later extensions may include sidebands, envelope features, cross-channel leakage, phase curvature, or a full real/imag complex scanner. They are not D1a requirements.

## 8. Wave identity residual

`wave_identity_residual` is a cautious aggregate candidate built from:

- a spectral component,
- a phase drift component,
- a local slope/intercept component.

Required boundaries:

- It is a diagnostic residual.
- It is not a physical observable by itself.
- It is not proof of physical wave identity.
- It is not proof of diagnostic specificity.

Possible later qualitative logic:

- exact duplicates should produce near-zero residual,
- near-identical decoys may produce small but non-zero residual,
- label-shuffled or kernel-shuffled controls should test whether residual structure depends on relational organization,
- structured references exceeding tested controls may be flagged cautiously, not treated as proof.

## 9. Control families

Required controls:

- exact duplicate sanity check
- near-identical-wave decoy control
- small `delta_k` decoy
- small phase drift decoy
- amplitude-preserved perturbation
- `label_shuffle`
- true kernel/node-level `label_shuffle`

Optional later controls:

- phase_randomized control
- spectrum_matched control
- distribution_matched control
- noise perturbation

## 10. Decision labels

Allowed cautious labels:

- `duplicate_sanity_pass`
- `duplicate_sanity_fail`
- `type_like_not_identity_equal_candidate`
- `near_duplicate_decoy_detected`
- `structured_reference_exceeds_tested_controls`
- `control_mimicry_warning`
- `inconclusive`
- `failed_sanity_check`

No label may claim established specificity, established identity, or validated Bridge status.

## 11. Proposed output files for later implementation

These are proposals only. This specification creates none of them.

- `data/qsb_st_comp01d1a_wave_identity_residual_scanner_config.yaml`
- `scripts/run_qsb_st_comp01d1a_wave_identity_residual_scanner.py`
- `runs/QSB-ST-COMP01D1A/wave_identity_residual_scanner_open/summary.json`
- `runs/QSB-ST-COMP01D1A/wave_identity_residual_scanner_open/readout.md`
- `runs/QSB-ST-COMP01D1A/wave_identity_residual_scanner_open/wave_identity_pair_summary.csv`
- `runs/QSB-ST-COMP01D1A/wave_identity_residual_scanner_open/control_family_summary.csv`
- `runs/QSB-ST-COMP01D1A/wave_identity_residual_scanner_open/decision_summary.csv`

## 12. Continuous field list

| Field name | Field type | Field description |
|---|---|---|
| `pair_id` | string | Stable pair identifier. |
| `wave_id_i` | string | First diagnostic wave or pattern identifier. |
| `wave_id_j` | string | Second diagnostic wave or pattern identifier. |
| `control_family` | string | Reference, duplicate, decoy, or null-control family. |
| `control_seed` | integer/null | Seed used for generated controls, if applicable. |
| `k_i` | float | Diagnostic wave-number estimate for item i. |
| `k_j` | float | Diagnostic wave-number estimate for item j. |
| `delta_k` | float | Absolute diagnostic wave-number difference. |
| `relative_k_shift` | float/null | Normalized k difference with division-by-zero protection. |
| `k_ratio` | float/null | Ratio of k values with zero/near-zero handling. |
| `phase_i` | float/array | Phase or phase profile for item i. |
| `phase_j` | float/array | Phase or phase profile for item j. |
| `relative_phase_drift` | float | Relative structure-internal phase drift. |
| `phase_gradient_delta` | float | Difference between diagnostic phase gradients. |
| `A_i` | float | Local A coefficient for item i. |
| `A_j` | float | Local A coefficient for item j. |
| `B_i` | float | Local B coefficient for item i. |
| `B_j` | float | Local B coefficient for item j. |
| `intercept_i` | float | Local intercept for item i. |
| `intercept_j` | float | Local intercept for item j. |
| `delta_intercept_ij` | float | Absolute intercept difference. |
| `intercept_similarity` | float | Transparently normalized intercept similarity. |
| `slope_i` | float | Local tangent slope for item i. |
| `slope_j` | float | Local tangent slope for item j. |
| `delta_slope_ij` | float | Absolute slope difference. |
| `slope_similarity` | float | Transparently normalized slope similarity. |
| `slope_intercept_balance` | float | Joint slope/intercept balance measure. |
| `local_linear_response_overlap` | float | Local slope/intercept response overlap. |
| `spectral_identity_distance` | float | Diagnostic spectral identity distance. |
| `wave_identity_residual` | float | Documented aggregate distinguishability residual. |
| `duplicate_sanity_distance` | float | Distance observed for exact duplicate sanity control. |
| `near_duplicate_decoy_distance` | float | Distance observed for near-identical decoy control. |
| `control_reference_ratio` | float/null | Ratio between structured/reference residual and control residual. |
| `decision_status` | string | Cautious scanner decision label. |
| `interpretation_note` | string | Short note separating observation from interpretation. |
| `warning_flags` | string | Explicit semicolon-separated warning flags. |

## 13. Minimal computation rules

Future computation rules should remain explicit and auditable:

- `delta_k = abs(k_i - k_j)`
- `relative_k_shift` uses transparent normalization with division-by-zero protection
- `k_ratio` uses explicit zero/near-zero handling
- `intercept_i = A_i` for the local real diagnostic form
- `slope_i = B_i * k_i` for the local tangent diagnostic form
- `delta_intercept_ij = abs(intercept_i - intercept_j)`
- `delta_slope_ij = abs(slope_i - slope_j)`
- similarity fields must be transparently normalized
- `wave_identity_residual` should be a documented aggregate, not a hidden score
- all warning conditions must be explicit fields, not silent assumptions

## 14. Acceptance criteria for a later scanner

A later implementation should at minimum check:

- exact duplicate sanity produces near-zero residual
- near-identical decoy produces small but detectable residual if designed to differ
- `label_shuffle` does not create false strong specificity claims
- kernel/node-level `label_shuffle` is included as a harder control
- all output CSVs parse cleanly
- `summary.json` contains `specificity_established = false` unless a later explicit criterion is defined and met
- `readout.md` separates Befund / Interpretation / Hypothese / Offene Lücke / Claim Boundary

## 15. Interpretation rules

Befund:

- What was numerically observed?

Interpretation:

- What does it mean within the synthetic diagnostic design?

Hypothese:

- What could become relevant for later work?

Offene Lücke:

- What is not shown?

## 16. What this specification must not do

This specification:

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
- does not create matter particles

## 17. Claim Boundary

psi is a diagnostic pattern object here, not automatically a physical wavefunction.

wave identity residual is a diagnostic distinguishability construct, not a physical observable by itself.

“wave-Pauli” is a heuristic internal analogy only.

It does not claim fermionic Pauli exclusion.

It does not invoke quantum spin-statistics.

It does not assert a physical exclusion principle.

type-like similarity is not the same as relational identity.

spectral shift is used here as a diagnostic analogy, not as cosmological redshift.

phase drift is used here as a structure-internal pattern marker, not as physical time delay.

tau is not physical time.

tau is not proper time.

tau is not a universal clock.

COMP01-D1a does not attach D(A,B).

COMP01-D1a does not construct S_rel2.

COMP01-D1a does not derive a Lorentzian metric.

COMP01-D1a does not validate a physical Bridge.

COMP01-D1a does not establish diagnostic specificity yet.

This is synthetic diagnostic specification work only.

## 18. Current status label

```text
current_status_label: COMP01D1A_wave_identity_residual_scanner_spec_created
```
