# QSB-ST-COMP01-B Component-Resolved Compatibility Inspection Plan

## 1. Purpose

COMP01-B plans a focused follow-up test, not a new broad output cascade.

The goal is to:

- use the additive psi decomposition idea,
- test cosine and sine components separately,
- test cross-component compatibility,
- inspect whether component-resolved fit separates `label_shuffle` and residual controls better than whole-psi metrics.

This block does not aim to:

- model tau,
- interpret time,
- attach `D(A,B)`,
- construct `S_rel2`,
- claim a physical wavefunction,
- claim specificity.

## 2. Current status anchor

LIC01 is parked.

The COMP01 minimal scanner is implemented and documented.

First candidate movement was observed, but diagnostic specificity is not established.

Current status before COMP01-B:

`COMP01_minimal_scanner_result_documented_candidates_observed_specificity_not_established`

Relevant recent line:

- COMP01 correlation compatibility scanner concept
- COMP01 scanner implementation plan
- COMP01 minimal scanner implementation
- COMP01 scanner result note

COMP01 minimal findings:

- `compatibility_scanner_pairwise.csv`: 320 rows
- `compatibility_family_summary.csv`: 5 rows
- `compatibility_control_contrast.csv`: 20 rows
- `specificity_established = False`
- `tau_model_constructed = False`
- `D_AB_attached = False`
- `S_rel2_constructed = False`

Best candidate metrics:

- `local_pattern_correlation`
- `normalized_overlap`
- `relative_phase_pattern_similarity`

Observed issue:

- `normalized_overlap` separates structured reference from `random_phase` and `amplitude_preserved_phase_randomized`, but not from `global_phase_shift` or `label_shuffle`.
- `relative_phase_pattern_similarity` separates structured reference from `random_phase` and `amplitude_preserved_phase_randomized`, but not from `global_phase_shift` or `label_shuffle`.
- `local_pattern_correlation` separates from `global_phase_shift`, but remains problematic against `random_phase`, `amplitude_preserved_phase_randomized`, and `label_shuffle`.
- `magnitude_support_overlap` and `phase_alignment` are not useful as primary candidates in their minimal form.

COMP01-B focuses on component resolution instead of adding a broad new metric list.

## 3. Motivation after COMP01

COMP01 showed:

- `relative_phase_pattern_similarity` and `normalized_overlap` move against `random_phase` and `amplitude_preserved_phase_randomized`.
- `label_shuffle` remains a substantial problem.
- `magnitude_support_overlap` does not separate cleanly.
- `phase_alignment` is too broad in the simple form.
- `local_pattern_correlation` shows special movement against `global_phase_shift`, but not enough movement against residual controls.

New motivation:

Since psi can be written additively as two basis contributions, missing separation in whole-psi metrics may come from relevant fit living in one component, or in the balance/cross-coupling between components.

## 4. Core question

Can component-resolved psi(i)-psi(j) compatibility improve separation against `label_shuffle` and residual controls?

Kann eine komponentenaufgeloeste psi(i)-psi(j)-Kompatibilitaet strukturierte Korrelation besser von `label_shuffle` und Restcontrols trennen?

## 5. Component decomposition idea

Starting from the real basis form:

```text
psi_i(x) = A_i cos(k_i x) + B_i sin(k_i x)
```

define conceptual components:

```text
psi_i^c = A_i cos(k_i x)
psi_i^s = B_i sin(k_i x)
```

Interpretation:

- `psi_i^c` = in-phase / cosine component
- `psi_i^s` = quadrature / sine component

Then inspect:

- cos-cos compatibility
- sin-sin compatibility
- cos-sin cross compatibility
- sin-cos cross compatibility
- component balance
- component asymmetry

This decomposition is diagnostic and conceptual. It is not a claim that the implemented synthetic psi exactly reconstructs a physical wavefunction.

## 6. Candidate component-resolved metrics

Planned first component-resolved candidates:

1. `cos_cos_overlap`

   Concept:

   ```text
   O_cc(i,j) = overlap(psi_i^c, psi_j^c)
   ```

2. `sin_sin_overlap`

   Concept:

   ```text
   O_ss(i,j) = overlap(psi_i^s, psi_j^s)
   ```

3. `cos_sin_cross_overlap`

   Concept:

   ```text
   O_cs(i,j) = overlap(psi_i^c, psi_j^s)
   ```

4. `sin_cos_cross_overlap`

   Concept:

   ```text
   O_sc(i,j) = overlap(psi_i^s, psi_j^c)
   ```

5. `component_balance_ratio`

   Concept: balance between cosine-channel and sine-channel strength, for example:

   ```text
   (|psi^c| - |psi^s|) / (|psi^c| + |psi^s| + eta)
   ```

6. `component_asymmetry_delta`

   Concept: difference between same-channel and cross-channel compatibility, for example:

   ```text
   (O_cc + O_ss) - (O_cs + O_sc)
   ```

7. `component_resolved_relative_phase_similarity`

   Concept: relative phase similarity computed separately or conditionally on component channels.

8. `component_resolved_local_pattern_correlation`

   Concept: local pattern correlation computed separately for component channels.

If the current synthetic psi representation does not directly contain A/B/cos/sin components, a future implementation may define a diagnostic component split from complex fingerprints:

- `real(psi_i)` = cosine-like / in-phase proxy
- `imag(psi_i)` = sine-like / quadrature proxy

This must be documented clearly as a proxy.

## 7. Control families

COMP01-B should later test at least the same five families:

- `structured_local_phase_response`
- `global_phase_shift`
- `random_phase`
- `amplitude_preserved_phase_randomized`
- `label_shuffle`

Optional later controls:

- `seed_sweep_random_phase`
- `multiple_label_shuffle`

The first COMP01-B block should not become a new output cascade.

## 8. Proposed output files

Only three output files are planned for the first COMP01-B minimal block:

- `component_compatibility_pairwise.csv`
- `component_compatibility_family_summary.csv`
- `component_compatibility_control_contrast.csv`

Expected future row counts:

- `component_compatibility_pairwise.csv`: 5 families x 64 pairs = 320 rows
- `component_compatibility_family_summary.csv`: 5 families = 5 rows
- `component_compatibility_control_contrast.csv`: 4 control families x planned component metrics

With 8 metrics:

```text
4 x 8 = 32 rows
```

No further outputs should be produced in the first COMP01-B minimal block, except optional:

- `summary.json`
- `readout.md`
- `config_resolved.json`

## 9. Continuous field list

Proposed future file: `component_compatibility_pairwise.csv`

| Field name | Type | Description |
| --- | --- | --- |
| `family` | string | Family label for the pair row. |
| `source_id` | string/integer | Source node, index, or local pattern identifier. |
| `target_id` | string/integer | Target node, index, or local pattern identifier. |
| `cos_cos_overlap` | float/null | Same-channel cosine-like overlap candidate. |
| `sin_sin_overlap` | float/null | Same-channel sine-like overlap candidate. |
| `cos_sin_cross_overlap` | float/null | Cross-channel cosine-to-sine overlap candidate. |
| `sin_cos_cross_overlap` | float/null | Cross-channel sine-to-cosine overlap candidate. |
| `component_balance_ratio` | float/null | Balance ratio between component strengths. |
| `component_asymmetry_delta` | float/null | Same-channel minus cross-channel compatibility contrast. |
| `component_resolved_relative_phase_similarity` | float/null | Relative phase similarity by component channel or component-conditioned proxy. |
| `component_resolved_local_pattern_correlation` | float/null | Local pattern correlation by component channel or component-conditioned proxy. |
| `component_split_mode` | string | Documented component split mode, e.g. `real_imag_proxy`. |
| `control_status` | string | Structured/control status for contrast reporting. |
| `warning` | string | Warning for zero-norm, degenerate, or proxy-only cases. |

Proposed future file: `component_compatibility_family_summary.csv`

| Field name | Type | Description |
| --- | --- | --- |
| `family` | string | Family label for the summary row. |
| `pair_count` | integer | Number of pair rows summarized for the family. |
| `cos_cos_overlap_mean` | float/null | Family mean of `cos_cos_overlap`. |
| `sin_sin_overlap_mean` | float/null | Family mean of `sin_sin_overlap`. |
| `cos_sin_cross_overlap_mean` | float/null | Family mean of `cos_sin_cross_overlap`. |
| `sin_cos_cross_overlap_mean` | float/null | Family mean of `sin_cos_cross_overlap`. |
| `component_balance_ratio_mean` | float/null | Family mean of `component_balance_ratio`. |
| `component_asymmetry_delta_mean` | float/null | Family mean of `component_asymmetry_delta`. |
| `component_resolved_relative_phase_similarity_mean` | float/null | Family mean of `component_resolved_relative_phase_similarity`. |
| `component_resolved_local_pattern_correlation_mean` | float/null | Family mean of `component_resolved_local_pattern_correlation`. |
| `component_split_mode` | string | Component split mode used for the family. |
| `structured_vs_control_separation_status` | string | Summary of structured/control separation status. |
| `warning` | string | Warning for undefined, degenerate, or proxy-only cases. |

Proposed future file: `component_compatibility_control_contrast.csv`

| Field name | Type | Description |
| --- | --- | --- |
| `control_family` | string | Control family compared against structured reference. |
| `metric_name` | string | Component-resolved metric used for the contrast. |
| `structured_mean` | float/null | Mean value for structured reference rows. |
| `control_mean` | float/null | Mean value for the control family. |
| `delta` | float/null | `structured_mean - control_mean`, if numerically defined. |
| `ratio` | float/null | Ratio contrast if numerically meaningful. |
| `effect_direction` | string | Direction of the observed contrast. |
| `separation_status` | string | Separation status for this metric/control pair. |
| `warning` | string | Warning for undefined values, small denominators, or interpretation limits. |

These field lists are planning targets only. They are not generated by this document.

## 10. Minimal computation rules

Future implementation rules:

- Use `eta` from config if available; otherwise use `1e-12`.
- Do not overwrite existing LIC01 outputs.
- Do not overwrite existing COMP01 outputs, except within a dedicated COMP01-B run directory.
- Build `psi_i` components diagnostically.
- If real A/B/cos/sin components are not explicitly available, use a real/imag split as proxy:
  - `real(psi_i)` = cosine-like / in-phase proxy
  - `imag(psi_i)` = sine-like / quadrature proxy
- Document `component_split_mode` in `summary.json`.
- Report same-channel overlaps and cross-channel overlaps separately.
- Do not normalize any metric to make controls look artificially worse.
- If a component has zero norm or is degenerate, write null/empty and set `warning`.
- `specificity_established` remains false unless predefined strict controls separate clearly.
- For this plan, use the conservative rule: no specificity claim.

## 11. Interpretation rules

Outcome A: `cos_cos_overlap` or `sin_sin_overlap` separates structured reference from `label_shuffle`.

Interpretation: A component channel may carry identity-sensitive compatibility.

Outcome B: Cross-channel overlaps separate better than same-channel overlaps.

Interpretation: Compatibility may depend on component coupling rather than simple same-channel overlap.

Outcome C: `component_asymmetry_delta` separates structured reference from controls.

Interpretation: Balance between in-phase/quadrature structure may be informative.

Outcome D: Component metrics reproduce previous near-equal `label_shuffle` behavior.

Interpretation: Component split does not solve the identity sensitivity problem.

Outcome E: All component metrics remain control-sensitive.

Interpretation: The current psi representation or 8-node kernel remains too broad or symmetric.

Always:

- No physical wavefunction claim.
- No tau claim.
- No `D(A,B)`.
- No `S_rel2`.
- No specificity claim unless strict controls separate.

## 12. Acceptance criteria for future implementation

Future implementation is accepted only if:

- The new COMP01-B scanner is additive.
- Existing LIC01 outputs are not rewritten.
- Existing COMP01 outputs are not rewritten.
- `component_compatibility_pairwise.csv` parses and has 320 rows.
- `component_compatibility_family_summary.csv` parses and has 5 rows.
- `component_compatibility_control_contrast.csv` parses and has the expected row count.
- All component metrics are present.
- All five families are present.
- Structured-vs-control separation is reported for every component metric/control pair.
- Controls are not dropped selectively.
- `component_split_mode` is documented.
- Readout contains a `Component-Resolved Compatibility Inspection` section.
- Claim-risk grep returns only boundary contexts.
- `git diff --check` passes.
- Output greater than 50 lines goes to `~/Downloads/Textfiles/`.
- No `D(A,B)`, `S_rel2`, tau model, or interval construction is introduced.

## 13. What this block must not do

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
- no retroactive change of COMP01 minimal scanner result

## 14. Claim Boundary

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
- This is synthetic diagnostic planning only.

## 15. Current status label

`COMP01B_component_resolved_compatibility_inspection_planned`
