# QSB-ST-COMP01 Correlation Compatibility Scanner Minimal Implementation Plan

## 1. Purpose

COMP01 minimal scanner planning defines only a first candidate test.

The planned first scanner should:

- compute first psi(i)-psi(j) compatibility values,
- compare `structured_reference` or `structured_local_phase_response` against controls,
- check whether any candidate value separates structured correlations from controls better than the previous tau/epsilon readout.

This block is not meant to:

- model tau,
- interpret time,
- attach `D(A,B)`,
- construct `S_rel2`,
- claim a physical wavefunction,
- claim specificity.

No implementation is introduced by this document.

## 2. Current status anchor

Current COMP01 status:

`COMP01_correlation_compatibility_scanner_concept_started_after_LIC01`

Previous LIC01 hold point:

`LIC01_tau_epsilon_decision_status_after_J_documented`

LIC01 is parked. It remains a tested but nonspecific synthetic diagnostic path.

LIC01 status summary:

- tau/epsilon was technically expanded.
- `specificity_established = false`
- `audit_established_specificity = false`
- `global_phase_warning_reduced = True`
- `residual_control_established_specificity = False`
- `seed_label_stability_established_specificity = False`

The COMP01 concept file exists:

`docs/QSB_ST_COMP01_CORRELATION_COMPATIBILITY_OBSERVABLE_SCANNER_CONCEPT.md`

The COMP01 guiding question is psi(i)-psi(j) compatibility:

Welche psi(i)-psi(j)-Kompatibilitaetswerte unterscheiden strukturierte Korrelationen von Controls?

Tau may re-enter later at most as a dependent latency function, after compatibility candidates have shown useful separation.

## 3. Minimal scanner goal

The first scanner should deliberately remain small.

It should only test whether candidate compatibility values show any separation between structured and controlled families.

No output cascade is planned. No additional result families or derived theory layers are planned for the minimal block.

## 4. Input basis

The planned implementation should start from:

- the existing synthetic LIC01 configuration,
- existing family logic from the tau/epsilon runner, if reusable,
- `pair_count = 64` as the expected first pair space,
- the minimal family set listed below.

Expected first-pass families:

- `structured_reference` or `structured_local_phase_response`
- `global_phase_shift`
- `random_phase`
- `amplitude_preserved_phase_randomized`
- `label_shuffle`

If existing `psi_i` patterns are not explicitly stored, the implementation should define a local diagnostic psi representation, for example:

```text
psi_i = local relational fingerprint of row/column pattern around node i
```

Psi is a diagnostic pattern object here, not automatically a physical wavefunction.

For the first version, `psi_i` may be read as a complex row/column pattern from the synthetic kernel, if that matches the existing LIC01 data path.

## 5. Candidate observables for first pass

Only these first candidates are planned for the minimal scanner:

1. `normalized_overlap`

   Sketch:

   ```text
   O_ij = |<psi_i, psi_j>| / (||psi_i|| ||psi_j|| + eta)
   ```

2. `magnitude_support_overlap`

   Sketch:

   ```text
   M_ij = overlap(|psi_i|, |psi_j|)
   ```

   A normalized dot product or cosine of magnitudes is acceptable if documented.

3. `phase_alignment`

   Sketch: phase alignment between `psi_i` and `psi_j` on shared support.

4. `relative_phase_pattern_similarity`

   Sketch: similarity of relative phase patterns after global phase removal.

5. `local_pattern_correlation`

   Sketch: correlation between local relational fingerprints of `i` and `j`.

Not in the first minimal scanner:

- `loop_phase_closure_score`
- `spectral_gap_or_energy_delta`
- tau model
- combined compatibility score, except as an optional empty/null placeholder

## 6. Control families for first pass

Minimal first-pass families:

- `structured_local_phase_response`
- `global_phase_shift`
- `random_phase`
- `amplitude_preserved_phase_randomized`
- `label_shuffle`

For each candidate value, the scanner should report:

- structured vs `global_phase_shift`
- structured vs `random_phase`
- structured vs `amplitude_preserved_phase_randomized`
- structured vs `label_shuffle`

Controls must not be dropped selectively.

## 7. Proposed output files

Only three output files are planned for the first minimal block:

- `compatibility_scanner_pairwise.csv`
- `compatibility_family_summary.csv`
- `compatibility_control_contrast.csv`

No further output files are planned for the first minimal block.

Expected future row counts:

- `compatibility_scanner_pairwise.csv`: 5 families x 64 pairs = 320 rows
- `compatibility_family_summary.csv`: 5 families = 5 rows
- `compatibility_control_contrast.csv`: 4 control families x 5 metrics = 20 rows

Metrics:

- `normalized_overlap`
- `magnitude_support_overlap`
- `phase_alignment`
- `relative_phase_pattern_similarity`
- `local_pattern_correlation`

## 8. Continuous field list

Proposed future file: `compatibility_scanner_pairwise.csv`

| Field name | Type | Description |
| --- | --- | --- |
| `family` | string | Family label for the row. |
| `source_id` | string/integer | Source node, index, or local pattern identifier. |
| `target_id` | string/integer | Target node, index, or local pattern identifier. |
| `normalized_overlap` | float/null | Normalized complex overlap candidate. |
| `magnitude_support_overlap` | float/null | Shared magnitude/support overlap candidate. |
| `phase_alignment` | float/null | Phase agreement candidate on shared support. |
| `relative_phase_pattern_similarity` | float/null | Global-phase-robust relative phase pattern similarity candidate. |
| `local_pattern_correlation` | float/null | Correlation between local relational fingerprints. |
| `compatibility_score_candidate` | float/null | Empty/null placeholder unless a combined score is explicitly defined later. |
| `control_status` | string | Structured/control status for contrast reporting. |
| `warning` | string | Warning if a value is undefined, unstable, or not meaningful. |

Proposed future file: `compatibility_family_summary.csv`

| Field name | Type | Description |
| --- | --- | --- |
| `family` | string | Family label for the summary row. |
| `pair_count` | integer | Number of pair rows summarized for the family. |
| `normalized_overlap_mean` | float/null | Family mean of `normalized_overlap`. |
| `magnitude_support_overlap_mean` | float/null | Family mean of `magnitude_support_overlap`. |
| `phase_alignment_mean` | float/null | Family mean of `phase_alignment`. |
| `relative_phase_pattern_similarity_mean` | float/null | Family mean of `relative_phase_pattern_similarity`. |
| `local_pattern_correlation_mean` | float/null | Family mean of `local_pattern_correlation`. |
| `compatibility_score_candidate_mean` | float/null | Mean of the optional combined score placeholder, if populated later. |
| `structured_vs_control_separation_status` | string | Short summary of whether structured/control separation was observed. |
| `warning` | string | Warning for missing values, unstable values, or interpretation limits. |

Proposed future file: `compatibility_control_contrast.csv`

| Field name | Type | Description |
| --- | --- | --- |
| `control_family` | string | Control family compared against the structured family. |
| `metric_name` | string | Candidate metric used for the contrast. |
| `structured_mean` | float/null | Mean value for the structured family. |
| `control_mean` | float/null | Mean value for the control family. |
| `delta` | float/null | `structured_mean - control_mean`, if numerically defined. |
| `ratio` | float/null | Ratio contrast if numerically meaningful. |
| `effect_direction` | string | Direction of the observed contrast. |
| `separation_status` | string | Separation status for this metric/control pair. |
| `warning` | string | Warning for undefined values, small denominators, or interpretation limits. |

These field lists are planning targets only. They are not generated by this document.

## 9. Minimal computation rules

The future implementation should follow these rules:

- Use `eta` from config if available; otherwise use `1e-12`.
- Define `psi_i` as a local diagnostic pattern representation.
- For the first version, `psi_i` may be a complex row/column pattern read from the synthetic kernel.
- Evaluate magnitude and phase separately.
- Avoid absolute/global phase where possible.
- Make `relative_phase_pattern_similarity` more robust to global phase than raw phase comparison.
- If a value is not meaningfully computable, leave the field empty/null and set `warning`.
- Do not choose a normalization that artificially worsens controls.
- Do not selectively omit controls.

## 10. Interpretation rules

Outcome A: `relative_phase_pattern_similarity` separates structured reference from `random_phase` and `label_shuffle`.

Interpretation: This may be a promising compatibility candidate. No physical claim follows.

Outcome B: `magnitude_support_overlap` is high for both structured and amplitude-preserved control families.

Interpretation: Magnitude/support likely carries part of the previous tau/epsilon response.

Outcome C: `local_pattern_correlation` separates structured behavior from `label_shuffle`.

Interpretation: Identity or local pattern sensitivity may help.

Outcome D: All metrics remain high in controls.

Interpretation: The psi representation may be too broad, or the kernel may be too small or symmetric.

Outcome E: No metric separates.

Interpretation: COMP01 first-pass candidates do not yet provide a useful compatibility observable.

Always:

- No physical claim.
- No tau claim.
- No specificity claim unless predefined controls separate under predefined reporting rules.

## 11. Acceptance criteria for future implementation

Future implementation is accepted only if:

- The new scanner is additive.
- Existing LIC01 outputs are not rewritten.
- `compatibility_scanner_pairwise.csv` parses and has 320 rows.
- `compatibility_family_summary.csv` parses and has 5 rows.
- `compatibility_control_contrast.csv` parses and has 20 rows.
- All five candidate metrics are present.
- All five families are present.
- Structured-vs-control separation is reported for every metric/control pair.
- Controls are not dropped selectively.
- Readout contains a `COMP01 Correlation Compatibility Scanner` section.
- Claim-risk grep returns only boundary contexts.
- `git diff --check` passes.
- Output greater than 50 lines goes to `~/Downloads/Textfiles/`.
- No `D(A,B)`, `S_rel2`, tau model, or interval construction is introduced.

## 12. What this block must not do

- no `D(A,B)`
- no `S_rel2`
- no Lorentz interval
- no physical time
- no proper time
- no physical wavefunction claim
- no Bridge validation
- no real-data validation
- no experimental validation
- no tau model fitting
- no large output cascade

## 13. Claim Boundary

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
- This is synthetic diagnostic planning only.

## 14. Current status label

`COMP01_minimal_scanner_implementation_plan_created`
