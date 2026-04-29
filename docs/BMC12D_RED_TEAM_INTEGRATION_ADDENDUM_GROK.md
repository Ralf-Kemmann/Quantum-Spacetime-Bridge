# BMC-12d Red-Team Integration Addendum – Grok Sharp Review

## Purpose

This addendum updates the BMC-12d Red-Team Integration Note with Grok's sharper second-pass review.

The original BMC-12d note integrated the first red-team feedback. This addendum records the stronger methodological objections and the revised control priority that emerged from Grok's updated review.

This is an interpretation-control document, not a new numerical result.

---

## 1. Current validated BMC-12 basis

Valid BMC-12 source basis:

```text
data/bmc08c_real_units_feature_table.csv
data/bmc12_feature_table_with_derived_from_bmc08c.csv
```

Current reference anchor:

```text
BMC09d_threshold_tau_03
```

Exact baseline reconciliation after BMC08c correction:

```text
original_edges:        81
bmc12b_baseline_edges: 81
shared_edges:          81
only_original:         0
only_bmc12b:           0
weight_differences:    0
```

Final BMC-12c decision-level result:

| case_id | dropped_feature | retained_variants | retained_fraction | status |
|---|---:|---:|---:|---|
| baseline_all_features_fixed_tau | - | 3/3 | 1.000 | decision_retained |
| matched_drop_feature_mode_frequency | feature_mode_frequency | 1/3 | 0.333 | decision_partially_retained |
| matched_drop_feature_length_scale | feature_length_scale | 1/3 | 0.333 | decision_partially_retained |
| matched_drop_feature_shape_factor | feature_shape_factor | 1/3 | 0.333 | decision_partially_retained |
| matched_drop_feature_spectral_index | feature_spectral_index | 2/3 | 0.667 | decision_partially_retained |

---

## 2. What Grok confirmed

Grok's updated review confirms the main internal strengths already recorded in BMC-12d.

### 2.1 Baseline reconciliation is excellent

The exact reconstruction of the BMC09d reference graph is a strong internal-consistency result.

It confirms that the corrected BMC-12 pipeline is operating on the intended BMC08c / BMC09d-compatible graph basis.

### 2.2 Matched-edge-count is a necessary improvement

Grok agrees that matched-edge-count LOO removes the obvious fixed-tau densification artifact.

This remains a valid methodological improvement over the earlier fixed-threshold leave-one-out.

### 2.3 BMC-12c is useful as a robustness diagnostic

Grok does not reject BMC-12c.

The result remains useful as an internal robustness check showing that the full BMC09d 3/3 decision is not trivially preserved under any single feature removal.

---

## 3. What Grok sharpened

Grok's updated review is stricter than the previous integration note in several places.

### 3.1 BMC-12c is very local

The current BMC-12c result is based on:

```text
4 features
3 backbone variants
1 graph-size point: N = 81
```

This is methodologically thin if used as a major claim.

The single-point nature of the test is now the central limitation.

### 3.2 Many decision values are near hard thresholds

Grok emphasized that several arrangement signals sit close to the hard decision cutoffs.

The decision logic uses:

```text
arrangement_signal_min = 0.05
dominance_gap_min     = 0.03
```

Therefore small continuous changes can create categorical flips:

```text
backbone_localization_supported
weak_or_inconclusive
full_only_or_mixed
coupling_localization_supported
```

This strengthens the concern that the BMC-12c pattern may partly reflect decision-threshold brittleness.

### 3.3 Matched-edge-count itself is not neutral

Grok sharpened a point that should be taken seriously:

```text
Forcing every leave-one-out graph to retain the top 81 edges is not automatically a neutral comparison.
```

Dropping one feature changes the feature-space geometry and therefore the edge-weight ranking.

Selecting the top N edges in the reduced feature space may introduce its own systematic artifact.

Thus matched-edge-count is better than fixed tau, but it is not artifact-free.

### 3.4 Scale-dependent roles are too strong as a claim

Grok's stricter position:

```text
The scale-dependent feature-role pattern is a plausible post-hoc description,
but not yet robust evidence.
```

The current data show a structured pattern, but the pattern rests on only 12 case-variant outcomes:

```text
4 feature drops x 3 variants
```

This is not enough for a strong scale-dependence claim.

---

## 4. Updated interpretation boundary

### Supported minimal statement

The following statement is supported:

```text
After exact BMC08c/BMC09d reconciliation, BMC-12c shows that no single feature removal preserves the full 3/3 backbone-only decision structure, while every single feature removal preserves at least one backbone variant.
```

This weakens the simplest single-feature dominance explanation.

### Still preliminary

The following remains preliminary:

```text
The BMC09d decision reflects a combined feature-space effect with scale-dependent feature roles.
```

This may be true, but the current evidence does not yet distinguish it from:

```text
decision-threshold brittleness
matched-edge-count artifact
top-k / top-alpha parameter artifact
single-point graph-size artifact
```

### Recommended replacement wording

Use:

```text
structured joint-feature-basis sensitivity
```

instead of:

```text
combinatorial feature dependence
```

Use:

```text
preliminary scale-dependent pattern
```

instead of:

```text
scale-dependent feature roles are established
```

---

## 5. Strongest current skeptical objection

The strongest objection after Grok's review is:

```text
The observed BMC-12c pattern may be a local artifact of the matched-edge-count plus hard-decision pipeline at N = 81.
```

More explicitly:

```text
The BMC-12c pattern may not reflect stable feature roles.
It may reflect a narrow decision point where top-N edge selection, top-k/top-alpha backbone definitions, and hard thresholds amplify small numerical changes into categorical retained/failed outcomes.
```

This is now the main risk to address.

---

## 6. Revised next-control priority

The original BMC-12d note prioritized a Decision-Threshold / Dominance-Gap Sensitivity Sweep.

Grok's updated review shifts the immediate priority toward a graph-size control first.

### Updated order

Recommended next sequence:

```text
BMC-12e: Edge-Count Neighborhood Sweep
BMC-12f: Decision-Threshold / Dominance-Gap Sensitivity Sweep
BMC-12g: Covariance-preserving or permutation-based BMC-12 null-control
```

Rationale:

BMC-12c currently rests on a single graph-size point:

```text
N = 81
```

Before sweeping decision thresholds, test whether the observed leave-one-out retention pattern is stable around this graph size.

---

## 7. BMC-12e target design

### Purpose

Test whether the BMC-12c pattern persists when the matched edge count is varied around the BMC09d reference size.

### Suggested edge counts

Minimal neighborhood:

```text
N = 75, 81, 87
```

Preferred broader neighborhood:

```text
N = 70, 75, 81, 87, 92
```

### For each N

Run:

```text
baseline_all_features_topN
matched_drop_feature_mode_frequency_topN
matched_drop_feature_length_scale_topN
matched_drop_feature_shape_factor_topN
matched_drop_feature_spectral_index_topN
```

For each case:

1. compute the graph using the same reconciled BMC08c-derived feature table;
2. retain top N edges;
3. run the established BMC07/BMC09d backbone-variant decision logic;
4. collect decision-level and variant-level outputs.

### Required outputs

```text
bmc12e_edgecount_sweep_decision_summary.csv
bmc12e_edgecount_sweep_variant_summary.csv
bmc12e_edgecount_sweep_readout.md
bmc12e_metrics.json
```

### Key metrics

For each edge count N:

```text
retained_variant_count
retained_fraction
decision_status
variant-specific decision_label
variant-specific dominant_arm
arrangement signals
```

Additional stability metrics:

```text
pattern_repeats_at_N
baseline_retained_at_N
drop_retention_profile
variant_survival_profile
```

---

## 8. How to read BMC-12e

### If the pattern persists

If the same qualitative retention pattern appears across neighboring N values, the BMC-12c result gains weight.

Then one can more defensibly say:

```text
The observed joint-feature-basis sensitivity is not a single graph-size artifact.
```

Still not physical proof, but stronger methodology.

### If the pattern changes strongly

If the pattern appears only at N = 81 and collapses or changes strongly at neighboring edge counts, BMC-12c should be treated as a local decision-point result.

Then the correct interpretation becomes:

```text
The BMC09d threshold_tau_03 anchor has local feature sensitivity at its reference graph size, but the feature-retention pattern is not yet robust across graph-size neighborhoods.
```

### If baseline itself fails near N

If the all-feature baseline does not retain the BMC09d-like decision near N, then the BMC09d anchor is strongly graph-size specific.

That would not invalidate BMC09d, but it would narrow its interpretation.

---

## 9. Updated conservative project wording

A revised wording after Grok's sharper review:

> BMC-12c reproduces the BMC09d threshold_tau_03 baseline exactly after reconciliation to the BMC08c feature source. Under matched-edge-count leave-one-out at N = 81, no individual feature removal preserves the full three-variant backbone-only decision, while each removal preserves at least one variant. This weakens a trivial single-feature dominance explanation and suggests structured sensitivity to the joint feature basis. However, because the current result is based on one graph-size point and hard decision thresholds, scale-dependent feature-role interpretations remain preliminary. The next required control is an edge-count neighborhood sweep around N = 81.

Shorter version:

> BMC-12c is a useful internal robustness diagnostic, not a manuscript-level feature-dependence claim until graph-size and decision-threshold sensitivity are tested.

---

## 10. Updated project status after Grok addendum

### Befund

BMC-12c is valid on the reconciled BMC08c basis and exactly reproduces the BMC09d baseline at N = 81.

### Interpretation

The result weakens a trivial single-feature-artifact explanation and shows structured leave-one-out sensitivity.

### Hypothesis

The BMC09d decision may depend on a joint feature basis with variant-scale-sensitive roles.

### Open gap

The current pattern may be local to N = 81 and to the current decision thresholds.

### Next block

Proceed to:

```text
BMC-12e Edge-Count Neighborhood Sweep
```

using the reconciled BMC08c-derived feature table and the existing BMC12b/BMC12c machinery.
