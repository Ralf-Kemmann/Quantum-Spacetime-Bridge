# QSB-ST-COMP01-D1b Wave Identity Residual Minimal Scanner Result Note

## 1. Purpose

This file documents the first minimal run of the `wave_identity_residual` scanner.

It is a result note for the existing synthetic minimal run in:

`runs/QSB-ST-COMP01D1B/wave_identity_residual_minimal_open/`

This note does not introduce a new run, does not change the implementation, and does not provide physical evidence. It documents what the current synthetic diagnostic scanner produced.

## 2. Current status anchor

Current context:

- COMP01-D Concept documented.
- COMP01-D1 Minimal Design Plan documented.
- COMP01-D1a Scanner Specification documented.
- COMP01-D1b Implementation Plan documented.
- COMP01-D1b Minimal Scanner implemented.

Current commit anchor:

`588b200 Add QSB-ST COMP01D1b wave identity residual minimal scanner`

## 3. Run inputs and generated outputs

Run directory:

`runs/QSB-ST-COMP01D1B/wave_identity_residual_minimal_open/`

Generated output files:

- `summary.json`
- `readout.md`
- `wave_identity_pair_summary.csv`
- `control_family_summary.csv`
- `decision_summary.csv`
- `resolved_config.json`

This result note was prepared from the existing run outputs. No new scanner run was performed for this documentation step.

## 4. Befund

Summary values:

```yaml
pair_count: 7
specificity_established: false
stable_candidate_metrics: []
exact_duplicate_sanity_passed: true
min_wave_identity_residual: 0.0
mean_wave_identity_residual: 0.09883413066168968
max_wave_identity_residual: 0.2944441465335814
control_mimicry_warnings_count: 2
```

Decision counts:

```yaml
duplicate_sanity_pass: 1
near_duplicate_decoy_detected: 4
control_mimicry_warning: 2
```

Observed result:

- The exact duplicate sanity check passed.
- The four near-duplicate decoy families produced non-zero residuals and were detected.
- Two controls triggered `control_mimicry_warning`.

The two warning controls were:

- `label_shuffle`
- `kernel_node_label_shuffle_proxy`

## 5. Interpretation

The scanner shows that `wave_identity_residual` is technically computable in the D1b minimal synthetic setup.

The exact duplicate case produced near-zero residual behavior, so the first sanity check passed. This is important because the scanner should not artificially distinguish a configured exact duplicate.

The near-duplicate decoys show that small synthetic changes in `k`, phase, and local slope/intercept parameters can produce non-zero residuals. Within this synthetic diagnostic design, that means the residual is responsive to the intended minimal perturbations.

The two `control_mimicry_warning` cases prevent any specificity claim. They show that the scanner must be stress-tested further before the residual can be treated as a useful candidate signal.

## 6. Hypothese

`wave_identity_residual` could become a useful diagnostic search axis for separating type-like wave similarity from relational wave identity.

That hypothesis remains conditional. It only becomes interesting if later robustness checks show that `label_shuffle`, kernel/node-level controls, and broader null families do not systematically produce similar or stronger residual patterns.

## 7. Offene Lücke

- no real data
- no physical validation
- no diagnostic specificity established
- no robust null-model family yet
- no weight sensitivity test yet
- no broader synthetic sweep yet
- no Lorentzian structure
- no physical time
- no physical wavefunction claim
- no Pauli or spin-statistics claim

## 8. Control mimicry warning

The two `control_mimicry_warning` cases are not a run failure. They are the main methodological warning signal from this minimal scanner.

The first minimal scanner should not be read as a positive specificity result. The control mimicry warnings are the main brake on interpretation.

In practical terms, the current residual can detect the configured synthetic differences, but the controls also produce strong residual values. That means the next step must test whether the residual is measuring relational identity structure or merely reacting to broad synthetic distance between configured wave pairs.

## 9. Machine-readable status

```yaml
block_id: QSB-ST-COMP01D1B
run_id: wave_identity_residual_minimal_open
commit_anchor: 588b200
pair_count: 7
specificity_established: false
stable_candidate_metrics: []
exact_duplicate_sanity_passed: true
control_mimicry_warnings_count: 2
min_wave_identity_residual: 0.0
mean_wave_identity_residual: 0.09883413066168968
max_wave_identity_residual: 0.2944441465335814
current_status_label: COMP01D1B_wave_identity_residual_minimal_scanner_result_documented
```

## 10. Claim Boundary

- psi is a diagnostic pattern object here, not automatically a physical wavefunction.
- wave_identity_residual is a diagnostic distinguishability construct, not a physical observable by itself.
- wave-Pauli is a heuristic internal analogy only.
- It does not claim fermionic Pauli exclusion.
- It does not invoke quantum spin-statistics.
- It does not assert a physical exclusion principle.
- type-like similarity is not the same as relational identity.
- spectral shift is used here as a diagnostic analogy, not as cosmological redshift.
- phase drift is used here as a structure-internal pattern marker, not as physical time delay.
- tau is not physical time.
- tau is not proper time.
- tau is not a universal clock.
- COMP01-D1b does not attach D(A,B).
- COMP01-D1b does not construct S_rel2.
- COMP01-D1b does not derive a Lorentzian metric.
- COMP01-D1b does not validate a physical Bridge.
- COMP01-D1b does not establish diagnostic specificity.
- This is synthetic diagnostic minimal-scanner result documentation only.

## 11. Current status label

current_status_label: COMP01D1B_wave_identity_residual_minimal_scanner_result_documented
