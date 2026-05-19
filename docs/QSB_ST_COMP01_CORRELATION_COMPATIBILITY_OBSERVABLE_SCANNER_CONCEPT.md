# QSB-ST-COMP01 Correlation Compatibility Observable Scanner Concept

## 1. Purpose

COMP01 is a new conceptual path after LIC01.

LIC01 is not discarded. It is retained as a negative control and warning result: the tau/epsilon path was technically built and controlled, but it did not establish diagnostic specificity in the tested synthetic setup.

COMP01 asks whether correlation or compatibility values between psi(i) and psi(j) separate structured correlations from controls better than the previous tau/epsilon readout.

This document is a concept and planning note only.

- No implementation is introduced here.
- No new CSV outputs are created here.
- No physical claims are made here.

## 2. Current status after LIC01

LIC01 tau/epsilon is parked as a tested but nonspecific synthetic diagnostic path.

Current LIC01 status:

- LIC01 showed technical buildability.
- LIC01 did not establish diagnostic specificity.
- The tau/epsilon pipeline was technically implemented.
- Controls were implemented.
- Specificity contrast was implemented.
- Observable/normalization audit was implemented.
- Global-phase probe was implemented.
- Residual-control analysis was implemented.
- Seed/label stability controls were implemented.
- `global_phase_warning_reduced = True`
- `specificity_established = false`
- `audit_established_specificity = false`
- `global_phase_probe_established_specificity = False`
- `residual_control_established_specificity = False`
- `seed_label_stability_established_specificity = False`

Interpretation after LIC01:

- Global phase was a subproblem but not the full explanation.
- `random_phase` remained generically strong across seeds.
- `label_shuffle` remained stably close across shuffles.
- Amplitude/support dominance remained a warning.
- No `D(A,B)`, no `S_rel2`, and no interval step were introduced.

## 3. Motivation

Tau as used in LIC01 was too broad or nonspecific in the tested synthetic setup. Adding more tau layers is unlikely to solve the core problem if the underlying observable still does not separate structured reference behavior from controls.

The next better question is compatibility:

Which relational pattern features make a pair correlation-capable?

A careful Diels-Alder analogy may be useful as a heuristic. In a Diels-Alder reaction, reaction feasibility is not just co-presence of reactants; it also depends on orbital symmetry, orientation, overlap, and compatibility. Analogously, QSB-ST may need a compatibility observable rather than a raw response-latency observable.

This analogy is heuristic only. It is not a physical derivation.

## 4. Core question

Which psi(i)-psi(j) compatibility values distinguish structured correlations from controls?

Welche psi(i)-psi(j)-Kompatibilitaetswerte unterscheiden strukturierte Korrelationen von Controls?

## 5. Conceptual shift from tau to compatibility

LIC01 asked mainly how strongly a pair responds under tau/epsilon perturbation.

COMP01 asks what makes a pair specifically correlation-compatible.

Contrast:

- Old question: How large is the response?
- New question: Why and how does this pair fit?

The scanner should first measure pair compatibility candidates, not generate a new tau output cascade.

## 6. Working interpretation of tau

Tau should not be treated as a universal clock.

Tau should not be treated as physical time.

Tau should not be treated as a pre-causal tent structure.

A better project-internal interpretation is:

`tau = Antwortlatenz im Korrelationsnetz`

Under this interpretation:

- Tau may be context-dependent.
- Tau may depend on how correlations form.
- Tau may later be modeled as a function of compatibility, overlap, relative phase, support, and spectral or energy-related quantities.

Conceptual placeholder:

```text
tau_ij = F(C_ij, O_ij, phase_ij, support_ij, DeltaE_ij, ...)
```

This is a conceptual placeholder, not an implemented or validated model.

## 7. Candidate ψ(i)-ψ(j) compatibility observables

Important boundary: psi is a diagnostic pattern object here, not automatically a physical wavefunction.

Candidate observables:

1. `normalized_overlap`

   Concept: normalized inner product or overlap between `psi_i` and `psi_j`.

   Possible sketch:

   ```text
   O_ij = |<psi_i, psi_j>| / (||psi_i|| ||psi_j|| + eta)
   ```

2. `phase_alignment`

   Concept: relative phase agreement between `psi_i` and `psi_j`, or between local patterns associated with the pair.

3. `magnitude_support_overlap`

   Concept: shared support or magnitude overlap independent of phase.

4. `relative_phase_pattern_similarity`

   Concept: compare relative phase patterns rather than absolute or global phase.

5. `local_pattern_correlation`

   Concept: correlation of local relational fingerprints around `i` and `j`.

6. `loop_or_closure_phase_compatibility`

   Concept: closure-style phase quantities along small cycles, intended to reduce global phase sensitivity.

7. `spectral_or_energy_gap_context`

   Concept: if spectral/eigenvalue information exists, compare compatibility against eigenvalue gaps or energy-like separations.

These candidates are diagnostic observables for synthetic pattern analysis. They do not by themselves define measurements of a physical wavefunction.

## 8. Scanner concept

A future scanner would compute pairwise values for each pair `(i,j)`.

Possible future per-pair fields:

- `source_id`
- `target_id`
- `family`
- `normalized_overlap`
- `phase_alignment`
- `magnitude_support_overlap`
- `relative_phase_pattern_similarity`
- `local_pattern_correlation`
- `loop_phase_closure_score`
- `spectral_gap_or_energy_delta`
- `compatibility_score_candidate`
- `warning/status`

The scanner should not directly produce tau. It should first measure compatibility values and report how they behave across structured and control families.

## 9. Control families

COMP01 should later test at least these control families:

- `structured_reference`
- `global_phase_shift`
- `random_phase`
- `amplitude_preserved_phase_randomized`
- `label_shuffle`

Optional later controls:

- `seed_sweep_random_phase`
- `multiple_label_shuffle`
- `magnitude_only`
- `phase_only_or_relative_phase_only`
- `larger_kernel_family`

The goal is not only to see whether the structured reference is high. The goal is to test whether controls are cleanly separated from structured reference behavior.

## 10. Continuous field list for future scanner outputs

Proposed future file: `compatibility_scanner_pairwise.csv`

| Field name | Type | Description |
| --- | --- | --- |
| `family` | string | Control or structured family label. |
| `source_id` | string/integer | Source node, index, or pattern identifier. |
| `target_id` | string/integer | Target node, index, or pattern identifier. |
| `normalized_overlap` | float | Normalized overlap candidate between `psi_i` and `psi_j`. |
| `phase_alignment` | float | Relative phase agreement candidate. |
| `magnitude_support_overlap` | float | Shared magnitude/support overlap independent of phase. |
| `relative_phase_pattern_similarity` | float | Similarity of relative phase patterns. |
| `local_pattern_correlation` | float | Correlation of local relational fingerprints. |
| `loop_phase_closure_score` | float | Closure-style phase compatibility score on small cycles. |
| `spectral_gap_or_energy_delta` | float/null | Spectral gap, eigenvalue gap, or energy-like separation if available. |
| `compatibility_score_candidate` | float/null | Optional combined compatibility candidate, if explicitly defined. |
| `control_status` | string | Structured/control status for contrast reporting. |
| `warning` | string | Warning or status note for this pair. |

Proposed future file: `compatibility_family_summary.csv`

| Field name | Type | Description |
| --- | --- | --- |
| `family` | string | Control or structured family label. |
| `pair_count` | integer | Number of pair rows included in this family. |
| `normalized_overlap_mean` | float | Family mean of `normalized_overlap`. |
| `phase_alignment_mean` | float | Family mean of `phase_alignment`. |
| `magnitude_support_overlap_mean` | float | Family mean of `magnitude_support_overlap`. |
| `relative_phase_pattern_similarity_mean` | float | Family mean of `relative_phase_pattern_similarity`. |
| `local_pattern_correlation_mean` | float | Family mean of `local_pattern_correlation`. |
| `loop_phase_closure_score_mean` | float | Family mean of `loop_phase_closure_score`. |
| `compatibility_score_candidate_mean` | float/null | Family mean of the optional combined candidate, if defined. |
| `structured_vs_control_separation_status` | string | Whether structured-vs-control separation was observed for the family/metric context. |
| `warning` | string | Warning or status note for this family summary. |

Proposed future file: `compatibility_control_contrast.csv`

| Field name | Type | Description |
| --- | --- | --- |
| `control_family` | string | Control family compared against structured reference. |
| `metric_name` | string | Candidate metric used for the contrast. |
| `structured_mean` | float | Mean value for structured reference rows. |
| `control_mean` | float | Mean value for the control family. |
| `delta` | float | `structured_mean - control_mean`, or another explicitly documented signed difference. |
| `ratio` | float/null | Ratio contrast if numerically defined. |
| `effect_direction` | string | Direction of the observed contrast. |
| `separation_status` | string | Reported separation status for this metric and control. |
| `warning` | string | Warning or status note for this contrast. |

These field lists are continuity targets for future scanner outputs. They are not produced by this concept document.

## 11. Interpretation rules

Outcome A: Structured reference separates from `random_phase`, amplitude-preserved controls, and `label_shuffle` on a compatibility metric.

Interpretation: The metric may be a promising compatibility candidate, but no physical claim follows.

Outcome B: Magnitude/support separates poorly but a phase-pattern metric separates better.

Interpretation: Relative phase or pattern structure may be more relevant than raw support in this synthetic diagnostic setup.

Outcome C: All compatibility metrics remain high for controls.

Interpretation: The chosen psi-pattern representation is still too broad, or the synthetic kernel is too small or symmetric.

Outcome D: `label_shuffle` remains close.

Interpretation: Identity sensitivity or kernel-size issues remain unresolved.

Outcome E: Spectral/eigenvalue context improves separation.

Interpretation: Spectral context may be relevant for correlation formation, but no energy claim or physical time claim follows.

## 12. How tau may re-enter later

Tau should not be primary in COMP01.

First measure compatibility. Only if compatibility metrics distinguish structured correlations from controls should later work consider modeling tau as a derived latency.

Possible conceptual model:

```text
tau_ij = F(compatibility_ij, overlap_ij, relative_phase_ij, support_ij, spectral_gap_ij)
```

Possible later project-internal readings:

- Small tau could mean easy or stable correlation formation.
- Large tau could mean delayed or difficult correlation formation.
- Undefined or unstable tau could mean no robust correlation formation.

No physical time claim follows from these readings.

## 13. Acceptance criteria for future implementation

Future implementation is accepted only if:

- The new scanner is additive.
- Existing LIC01 outputs are not rewritten.
- `compatibility_scanner_pairwise.csv` parses.
- `compatibility_family_summary.csv` parses.
- `compatibility_control_contrast.csv` parses.
- Structured-vs-control separation is reported for every candidate metric.
- Controls are not dropped selectively.
- Claim-risk grep returns only boundary contexts.
- `git diff --check` passes.
- Output greater than 50 lines goes to `~/Downloads/Textfiles/`.
- No `D(A,B)`, `S_rel2`, or interval construction is introduced.

## 14. Recommended next step

This file is the small COMP01 design/spec note.

The next possible file could be:

`docs/QSB_ST_COMP01_CORRELATION_COMPATIBILITY_SCANNER_IMPLEMENTATION_PLAN.md`

Alternatively, if the design remains compact and sufficiently bounded, a later implementation step could introduce:

`scripts/run_qsb_st_comp01_correlation_compatibility_scanner.py`

No implementation is part of this assignment.

## 15. Claim Boundary

- psi is a diagnostic pattern object here, not automatically a physical wavefunction.
- psi-overlap is a compatibility observable, not automatically a quantum measurement probability.
- tau is not physical time.
- tau is not proper time.
- tau is not a universal clock.
- tau is not treated here as a pre-causal tent structure.
- COMP01 does not derive a Lorentzian metric.
- COMP01 does not construct a spacetime interval.
- COMP01 does not attach D(A,B).
- COMP01 does not construct S_rel2.
- COMP01 does not validate a physical Bridge.
- COMP01 does not establish diagnostic specificity yet.
- This is conceptual synthetic diagnostic planning only.

## 16. Current status label

`COMP01_correlation_compatibility_scanner_concept_started_after_LIC01`
