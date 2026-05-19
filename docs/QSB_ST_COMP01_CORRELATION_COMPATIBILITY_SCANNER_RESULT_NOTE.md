# QSB-ST-COMP01 Correlation Compatibility Scanner Result Note

## 1. Purpose

COMP01 documents the first small Correlation Compatibility Scanner after LIC01.

The goal was to:

- compute first psi(i)-psi(j) compatibility candidates,
- compare `structured_local_phase_response` against controls,
- check whether candidate values show any movement at all.

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
7981eaf Add QSB-ST COMP01 minimal correlation compatibility scanner
```

Previous COMP01 plan:

`docs/QSB_ST_COMP01_CORRELATION_COMPATIBILITY_SCANNER_IMPLEMENTATION_PLAN.md`

Concept anchor:

`docs/QSB_ST_COMP01_CORRELATION_COMPATIBILITY_OBSERVABLE_SCANNER_CONCEPT.md`

Previous LIC01 hold point:

`LIC01_tau_epsilon_decision_status_after_J_documented`

## 3. Files involved

Script:

`scripts/run_qsb_st_comp01_correlation_compatibility_scanner.py`

Run output directory:

`runs/QSB-ST-COMP01/correlation_compatibility_scanner_open/`

Outputs:

- `compatibility_scanner_pairwise.csv`
- `compatibility_family_summary.csv`
- `compatibility_control_contrast.csv`
- `summary.json`
- `readout.md`
- `config_resolved.json`

Result note:

`docs/QSB_ST_COMP01_CORRELATION_COMPATIBILITY_SCANNER_RESULT_NOTE.md`

## 4. Scanner implementation

The scanner is an additive new scanner. The LIC01 runner was not changed.

The scanner uses the synthetic LIC01 basis and reuses the `build_synthetic_kernel(seed)` logic. It treats `psi_i` as a complex row/column local relational fingerprint.

Psi is a diagnostic pattern object here, not automatically a physical wavefunction.

Five metrics were computed:

- `normalized_overlap`
- `magnitude_support_overlap`
- `phase_alignment`
- `relative_phase_pattern_similarity`
- `local_pattern_correlation`

No combined compatibility score was defined.

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
?? scripts/run_qsb_st_comp01_correlation_compatibility_scanner.py
```

Commit after acceptance:

```text
7981eaf Add QSB-ST COMP01 minimal correlation compatibility scanner
```

## 6. Output files

Row counts:

- `compatibility_scanner_pairwise.csv`: 320
- `compatibility_family_summary.csv`: 5
- `compatibility_control_contrast.csv`: 20

Families:

- `structured_local_phase_response`
- `global_phase_shift`
- `random_phase`
- `amplitude_preserved_phase_randomized`
- `label_shuffle`

Metrics:

- `normalized_overlap`
- `magnitude_support_overlap`
- `phase_alignment`
- `relative_phase_pattern_similarity`
- `local_pattern_correlation`

## 7. Befund

The COMP01 minimal scanner is technically implemented.

The three main outputs were generated.

Status values:

- `specificity_established = False`
- `tau_model_constructed = False`
- `D_AB_attached = False`
- `S_rel2_constructed = False`

First candidate movement was observed.

Best candidate metrics:

- `local_pattern_correlation`
- `normalized_overlap`
- `relative_phase_pattern_similarity`

Warning metrics:

- `magnitude_support_overlap` shows warnings against all controls.
- `phase_alignment` shows warnings against all controls.
- `normalized_overlap` remains problematic against `global_phase_shift` and `label_shuffle`.
- `relative_phase_pattern_similarity` remains problematic against `global_phase_shift` and `label_shuffle`.
- `local_pattern_correlation` remains problematic against `random_phase`, `amplitude_preserved_phase_randomized`, and `label_shuffle`.

## 8. Candidate movement

`local_pattern_correlation` is interesting because it tests local pattern fit or fingerprint correlation. It does not yet separate cleanly against `random_phase`, `amplitude_preserved_phase_randomized`, and `label_shuffle`.

`normalized_overlap` is interesting as a basic overlap candidate. It remains problematic against `global_phase_shift` and `label_shuffle`.

`relative_phase_pattern_similarity` is especially interesting because it is closer to the idea of relative phase fit. It remains problematic against `global_phase_shift` and `label_shuffle`.

`magnitude_support_overlap` is more a warning or diagnostic metric than a main candidate at this stage. This matches the LIC01 warning pattern around `magnitude_support_dominance_warning`.

`phase_alignment` appears too broad or nonspecific in the minimal form.

## 9. Interpretation

COMP01 provides a better search handle than further expansion of the tau/epsilon cascade.

The scanner shows that some compatibility metrics can pick up structured information. However, the controls do not yet separate cleanly enough.

Result:

- Positive movement: yes.
- Specificity established: no.
- Tau model justified: no.
- `D(A,B)` or `S_rel2` step justified: no.

## 10. Hypothese

Possible working hypotheses:

- `local_pattern_correlation` could indicate source-target or local fingerprint fit.
- `relative_phase_pattern_similarity` could be closer to a global-phase-robuster fit quantity.
- `normalized_overlap` may be useful, but may be too support-sensitive or label-sensitive.
- `magnitude_support_overlap` probably shows which parts of the earlier tau/epsilon warning came from magnitude/support.
- `phase_alignment` in the simple form is probably too coarse.

These are working hypotheses for synthetic diagnostic follow-up, not physical claims.

## 11. Offene Lücke

Open gaps:

- No specificity is established.
- Controls remain problematic.
- The psi representation is still minimal.
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
- psi-overlap is a compatibility observable, not automatically a quantum measurement probability.
- tau is not physical time.
- tau is not proper time.
- tau is not a universal clock.
- COMP01 does not attach D(A,B).
- COMP01 does not construct S_rel2.
- COMP01 does not derive a Lorentzian metric.
- COMP01 does not validate a physical Bridge.
- COMP01 does not establish diagnostic specificity yet.
- This is synthetic diagnostic work only.

## 13. Recommended next step

Recommended next step:

`QSB-ST-COMP01-B candidate metric inspection and focused follow-up plan`

Possible file:

`docs/QSB_ST_COMP01_CANDIDATE_METRIC_INSPECTION_PLAN.md`

Goal:

- Do not start a new output cascade immediately.
- Inspect the three moving candidates more closely:
  - `local_pattern_correlation`
  - `normalized_overlap`
  - `relative_phase_pattern_similarity`
- Check which control contrasts each candidate passes or fails.
- Decide whether a focused COMP01-B scanner is justified.

Do not directly proceed to:

- tau model,
- `D(A,B)`,
- `S_rel2`,
- Lorentz interval,
- Bridge validation.

## 14. Current status label

`COMP01_minimal_scanner_result_documented_candidates_observed_specificity_not_established`
