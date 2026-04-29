# GROK Project Reset – QSB / BMC-12 Red-Team Review Prompt

## Role assignment

You are being asked to act as a skeptical red-team reviewer for a graph-based numerical robustness analysis in a theoretical-physics-inspired research project.

Your role is not to be polite and not to hype the result.

Your role is to:

- look for weak points,
- identify methodological artifacts,
- check whether the interpretation follows from the data,
- distinguish robust diagnostic evidence from overclaiming,
- and propose the strongest next control test.

However, please keep the critique technically specific. Do not dismiss the project merely because it is speculative or theory-adjacent. Treat the current material as a numerical/methodological robustness workflow.

---

## Project context

The broader project is called Quantum–Spacetime Bridge / QSB.

The project studies whether relational, wave-based, feature-space and graph-based structures can reveal nontrivial local organization patterns relevant to a larger theoretical framework.

Important framing:

- This is not being claimed as a physical proof.
- The current BMC series is a numerical diagnostic pipeline.
- Results are interpreted defensively.
- The project separates:
  - Befund / finding,
  - Interpretation,
  - Hypothesis,
  - Open gap.
- The key question is methodological robustness, not ontology.

Please evaluate the BMC-12 result as a robustness diagnostic.

---

## Important prior anchor: BMC09d

The current reference anchor is:

```text
BMC09d_threshold_tau_03
```

BMC09d used a local threshold graph constructed from a BMC08c-compatible feature table.

Original BMC09d baseline:

```text
edge count = 81
```

Original BMC09d backbone decision:

```text
3 / 3 variants retained:
decision_label = backbone_localization_supported
dominant_arm   = backbone_only
```

Backbone variants:

```text
strength_topk_6
strength_topalpha_025
strength_topalpha_050
```

Original decision thresholds:

```yaml
decision:
  arrangement_signal_min: 0.05
  dominance_gap_min: 0.03
  minimum_repeat_count: 50
  minimum_arm_edge_count: 2
```

The decision logic comes from the existing runner:

```text
scripts/bmc07_backbone_variation_runner.py
```

BMC-12c reuses this runner rather than reconstructing the logic independently.

---

## BMC-12 purpose

BMC-12 is a feature-dominance / leave-one-out analysis.

The question is:

```text
Is the BMC09d backbone-only decision structure dominated by one individual feature,
or does it require a combined feature basis?
```

The four features are:

```text
feature_mode_frequency
feature_length_scale
feature_shape_factor
feature_spectral_index
```

Derived features:

```text
feature_shape_factor   = max(L_major_raw, L_minor_raw) / min(L_major_raw, L_minor_raw)
feature_spectral_index = m_ref_raw
```

---

## Critical correction: BMC08a vs BMC08c source reconciliation

An initial BMC-12 run accidentally used a BMC08a-like feature source.

That run was superseded.

The mismatch was detected because the reconstructed BMC-12 baseline did not reproduce the BMC09d graph:

```text
original_edges:        81
bmc12c_baseline_edges: 82
shared_edges:          58
only_original:         23
only_bmc12c:           24
weight_differences:    58
```

The mismatch was traced to the wrong feature-table source and a different ring sign convention.

Correct source:

```text
data/bmc08c_real_units_feature_table.csv
```

After switching to the BMC08c-compatible feature table and rebuilding the derived BMC-12 feature table, the baseline was exactly reconciled:

```text
original_edges:        81
bmc12b_baseline_edges: 81
shared_edges:          81
only_original:         0
only_bmc12b:           0
weight_differences:    0
```

This reconciliation is important.

Please treat BMC08a-based BMC-12 outputs as debugging history only. The valid BMC-12 result is the reconciled BMC08c-based result.

---

## BMC-12b: matched edge-count leave-one-out

BMC-12a used fixed tau and showed that dropping features can densify the graph because the feature space becomes lower-dimensional.

Therefore BMC-12b uses matched edge count.

Procedure:

1. Reconstruct the all-feature baseline graph at the BMC09d reference threshold.
2. Confirm the baseline edge count:

```text
N_edges = 81
```

3. For each leave-one-out feature subset, compute all pair weights.
4. Retain the top 81 edges.
5. This controls graph size before comparing decision behavior.

This is meant to avoid the fixed-threshold densification artifact.

---

## BMC-12c: backbone-aware matched leave-one-out

BMC-12c takes the BMC-12b matched graphs and re-runs the established BMC09d/BMC07 backbone-variant decision logic.

After reconciliation, BMC-12c baseline reproduces BMC09d exactly:

```text
baseline_all_features_fixed_tau:
3 / 3 retained
status = decision_retained
```

Final BMC-12c decision-level summary:

| case_id | dropped_feature | retained_variants | retained_fraction | status |
|---|---:|---:|---:|---|
| baseline_all_features_fixed_tau | - | 3/3 | 1.000 | decision_retained |
| matched_drop_feature_mode_frequency | feature_mode_frequency | 1/3 | 0.333 | decision_partially_retained |
| matched_drop_feature_length_scale | feature_length_scale | 1/3 | 0.333 | decision_partially_retained |
| matched_drop_feature_shape_factor | feature_shape_factor | 1/3 | 0.333 | decision_partially_retained |
| matched_drop_feature_spectral_index | feature_spectral_index | 2/3 | 0.667 | decision_partially_retained |

---

## Variant-level pattern

### Baseline

All three reference variants are retained:

| variant | decision_label | dominant_arm |
|---|---|---|
| strength_topk_6 | backbone_localization_supported | backbone_only |
| strength_topalpha_025 | backbone_localization_supported | backbone_only |
| strength_topalpha_050 | backbone_localization_supported | backbone_only |

### Drop `feature_mode_frequency`

| variant | decision_label | dominant_arm |
|---|---|---|
| strength_topk_6 | coupling_localization_supported | full_graph |
| strength_topalpha_025 | coupling_localization_supported | full_graph |
| strength_topalpha_050 | backbone_localization_supported | backbone_only |

### Drop `feature_length_scale`

| variant | decision_label | dominant_arm |
|---|---|---|
| strength_topk_6 | weak_or_inconclusive | backbone_only |
| strength_topalpha_025 | full_only_or_mixed | backbone_only |
| strength_topalpha_050 | backbone_localization_supported | backbone_only |

### Drop `feature_shape_factor`

| variant | decision_label | dominant_arm |
|---|---|---|
| strength_topk_6 | full_only_or_mixed | full_graph |
| strength_topalpha_025 | full_only_or_mixed | full_graph |
| strength_topalpha_050 | backbone_localization_supported | backbone_only |

### Drop `feature_spectral_index`

| variant | decision_label | dominant_arm |
|---|---|---|
| strength_topk_6 | backbone_localization_supported | backbone_only |
| strength_topalpha_025 | backbone_localization_supported | backbone_only |
| strength_topalpha_050 | full_only_or_mixed | backbone_only |

---

## Proposed interpretation to critique

The proposed cautious interpretation is:

1. The BMC09d backbone-only decision is not a trivial single-feature artifact.
2. Full 3/3 decision stability requires the combined feature basis.
3. Removing any one feature weakens the decision-level robustness.
4. The feature roles appear scale-dependent:
   - tighter / smaller backbone variants are mainly stable under spectral-index removal,
   - broader `strength_topalpha_050` is stable under removal of mode_frequency, length_scale, or shape_factor.
5. The result remains methodological and diagnostic.
6. It does not establish physical content.

A possible conservative wording:

> BMC-12 extends the BMC09d threshold_tau_03 anchor by testing feature-level dependence under matched graph size. After reconciling the feature source to the original BMC08c basis, the BMC09d baseline is exactly reproduced. Matched leave-one-out tests show that no single feature removal preserves the full three-variant backbone-only decision structure, while every removal preserves at least one variant. This suggests that the BMC09d decision is not a trivial single-feature artifact, but a combined feature-space effect with scale-dependent feature roles. The result remains methodological and diagnostic; it does not by itself establish physical content.

---

## Your review task

Please critique the result as a skeptical red-team reviewer.

Focus on these questions:

1. Is the baseline reconciliation sufficient?
2. Is matched-edge-count leave-one-out a defensible control?
3. Does the conclusion “not a trivial single-feature artifact, but combinatorial feature dependence” follow from the result?
4. Is the scale-dependent feature-role interpretation supported by the variant-level table?
5. Could the observed pattern be an artifact of:
   - matched edge count,
   - top-k / top-alpha backbone definitions,
   - hard decision thresholds,
   - dominance-gap thresholding,
   - graph-size dependence,
   - or the specific perturbation/readout procedure?
6. What is the strongest skeptical objection?
7. What additional control would you require before this result is used in a manuscript?
8. Would you recommend:
   - accepting the current interpretation,
   - weakening it,
   - or requiring another test first?

---

## Expected style of response

Please answer in a structured way:

```text
1. Strong points
2. Weak points / risks
3. Artifact risks
4. Interpretation check
5. Required next controls
6. Suggested wording
7. Bottom-line verdict
```

Be sharp, but technically specific.
