# BMC-12a/b/c Feature-Dominance Result Note

## Status

This note records the consolidated BMC-12 feature-dominance diagnostics after baseline reconciliation.

The current valid source basis is:

```text
data/bmc08c_real_units_feature_table.csv
```

not the earlier BMC08a-style table.

The BMC08c-based derived feature table is:

```text
data/bmc12_feature_table_with_derived_from_bmc08c.csv
```

The relevant BMC09d reference anchor remains:

```text
BMC09d_threshold_tau_03
```

with the original backbone decision:

```text
3 / 3 variants:
decision_label = backbone_localization_supported
dominant_arm   = backbone_only
```

---

## 1. Baseline reconciliation

An initial BMC-12 run used a BMC08a-like feature source and therefore did not reproduce the BMC09d threshold_tau_03 graph.

The mismatch was diagnostic, not physical.

Observed mismatch before reconciliation:

```text
original_edges:        81
bmc12c_baseline_edges: 82
shared_edges:          58
only_original:         23
only_bmc12c:           24
weight_differences:    58
```

The mismatch was traced to the wrong feature-table source and a different ring sign convention.

The correct BMC09d-compatible source was identified through:

```text
data/bmc08c_m39x1_sign_sensitive_ring_config.yaml
```

which points to:

```text
data/bmc08c_real_units_feature_table.csv
```

After rebuilding the BMC-12 derived feature table from BMC08c and re-running BMC-12b, the baseline reconciliation became exact:

```text
original_edges:        81
bmc12b_baseline_edges: 81
shared_edges:          81
only_original:         0
only_bmc12b:           0
weight_differences:    0
```

### Interpretation

BMC-12 is valid only on the BMC08c-compatible feature source. Earlier BMC08a-derived BMC-12 diagnostics should be treated as useful debugging history, not as final feature-dominance evidence.

---

## 2. BMC-12b matched edge-count result

BMC-12b controls the fixed-threshold densification effect by matching each leave-one-out graph to the baseline edge count.

Valid baseline after reconciliation:

```text
baseline_edge_count = 81
```

The BMC-12b output used for BMC-12c is:

```text
runs/BMC-12b/matched_leaveoneout_open/bmc12b_matched_leaveoneout_edges.csv
```

### Interpretation

BMC-12b establishes a graph-size-controlled comparison basis. It prevents the fixed-tau leave-one-out artifact where lower-dimensional feature spaces become artificially denser.

---

## 3. BMC-12c backbone-aware matched leave-one-out

BMC-12c reuses the established BMC09d/BMC07 backbone-variant runner:

```text
scripts/bmc07_backbone_variation_runner.py
```

It applies the original decision criteria:

```yaml
decision:
  arrangement_signal_min: 0.05
  dominance_gap_min: 0.03
  minimum_repeat_count: 50
  minimum_arm_edge_count: 2
```

and the original backbone variants:

```text
strength_topk_6
strength_topalpha_025
strength_topalpha_050
```

The final BMC-12c readout is:

```text
runs/BMC-12c/backbone_aware_matched_loo_open/bmc12c_backbone_aware_readout.md
```

The comparison summary is:

```text
runs/BMC-12c/backbone_aware_matched_loo_open/bmc12c_decision_comparison_summary.csv
```

---

## 4. BMC-12c decision-level summary

After baseline reconciliation, BMC-12c produced:

| case_id | dropped_feature | retained_variants | retained_fraction | status |
|---|---:|---:|---:|---|
| baseline_all_features_fixed_tau | - | 3/3 | 1.000 | decision_retained |
| matched_drop_feature_mode_frequency | feature_mode_frequency | 1/3 | 0.333 | decision_partially_retained |
| matched_drop_feature_length_scale | feature_length_scale | 1/3 | 0.333 | decision_partially_retained |
| matched_drop_feature_shape_factor | feature_shape_factor | 1/3 | 0.333 | decision_partially_retained |
| matched_drop_feature_spectral_index | feature_spectral_index | 2/3 | 0.667 | decision_partially_retained |

### Immediate result

The BMC09d baseline is now exactly reproduced as:

```text
3 / 3 decision_retained
```

Under matched leave-one-out, no single feature removal preserves the full 3/3 BMC09d backbone-only decision structure.

However, no feature removal fully destroys the decision structure either: all leave-one-out cases retain at least one backbone variant.

---

## 5. Variant-level result

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

Interpretation: the broad top-alpha backbone survives, while the smaller / tighter variants shift away from the original backbone-only decision.

### Drop `feature_length_scale`

| variant | decision_label | dominant_arm |
|---|---|---|
| strength_topk_6 | weak_or_inconclusive | backbone_only |
| strength_topalpha_025 | full_only_or_mixed | backbone_only |
| strength_topalpha_050 | backbone_localization_supported | backbone_only |

Interpretation: the dominant arm often remains backbone_only, but the stricter decision criteria fail except for the broad top-alpha variant. This suggests a signal-strength or decision-margin weakening rather than a simple arm switch.

### Drop `feature_shape_factor`

| variant | decision_label | dominant_arm |
|---|---|---|
| strength_topk_6 | full_only_or_mixed | full_graph |
| strength_topalpha_025 | full_only_or_mixed | full_graph |
| strength_topalpha_050 | backbone_localization_supported | backbone_only |

Interpretation: the broad top-alpha variant survives, while smaller / tighter backbone definitions shift toward full-graph dominance. Shape factor appears important for localizing the tighter backbone variants.

### Drop `feature_spectral_index`

| variant | decision_label | dominant_arm |
|---|---|---|
| strength_topk_6 | backbone_localization_supported | backbone_only |
| strength_topalpha_025 | backbone_localization_supported | backbone_only |
| strength_topalpha_050 | full_only_or_mixed | backbone_only |

Interpretation: the tighter and intermediate backbone variants survive. The broad variant loses the full decision criterion while still preserving backbone_only as dominant arm. This is the mildest leave-one-out disruption among the tested features.

---

## 6. Consolidated finding

### Befund

BMC-12c reproduces the BMC09d threshold_tau_03 baseline exactly after switching to the BMC08c-compatible feature source. The baseline retains all three original backbone variants.

Under matched leave-one-out, none of the four individual feature removals preserves the full 3/3 decision structure. Retention remains partial in all cases:

```text
feature_mode_frequency: 1/3
feature_length_scale:   1/3
feature_shape_factor:   1/3
feature_spectral_index: 2/3
```

### Interpretation

The BMC09d backbone-only decision is not a trivial single-feature artifact. It requires the combined feature basis for full 3/3 stability.

At the same time, the decision structure is not leave-one-out fully stable. Removing any one feature weakens the full decision-level robustness.

The feature roles are scale-dependent:

```text
Tighter / smaller backbone variants:
  stable mainly under spectral_index removal

Broader topalpha_050 backbone variant:
  stable under removal of mode_frequency, length_scale, or shape_factor
```

### Hypothesis

The BMC09d local backbone decision may reflect a combined feature-space structure in which different features stabilize different backbone scales.

A useful working hypothesis is:

```text
feature_spectral_index:
  less critical for the tighter backbone core,
  but relevant for the broad backbone extension.

feature_mode_frequency, feature_length_scale, feature_shape_factor:
  more critical for the tighter / more local backbone variants,
  while the broad topalpha_050 variant remains more tolerant to their removal.
```

### Offene Lücke

BMC-12c is a matched-edge-count test at the single BMC09d baseline size:

```text
N_edges = 81
```

It does not yet test whether the same scale-dependent feature roles persist over neighboring graph sizes or thresholds.

---

## 7. Recommended next step

The next optional block should be:

```text
BMC-12e Edge-Count Neighborhood Sweep
```

Purpose:

Test whether the BMC-12c feature-role pattern is stable around the BMC09d baseline graph size.

Suggested matched edge counts:

```text
N = 75, 81, 87
```

or a slightly broader but still controlled window:

```text
N = 70, 75, 81, 87, 92
```

The key question:

```text
Does the same scale-dependent retention pattern persist near the baseline edge count?
```

This should remain a robustness diagnostic, not a physical proof.

---

## 8. Conservative project wording

A defensible wording for later use:

> BMC-12 extends the BMC09d threshold_tau_03 anchor by testing feature-level dependence under matched graph size. After reconciling the feature source to the original BMC08c basis, the BMC09d baseline is exactly reproduced. Matched leave-one-out tests show that no single feature removal preserves the full three-variant backbone-only decision structure, while every removal preserves at least one variant. This suggests that the BMC09d decision is not a trivial single-feature artifact, but a combined feature-space effect with scale-dependent feature roles. The result remains methodological and diagnostic; it does not by itself establish physical content.

---

## 9. File and run anchors

Relevant files:

```text
data/bmc08c_real_units_feature_table.csv
data/bmc12_feature_table_with_derived_from_bmc08c.csv
data/bmc12b_matched_leaveoneout_config.yaml
data/bmc12c_backbone_aware_matched_loo_config.yaml
scripts/run_bmc12b_matched_leaveoneout.py
scripts/run_bmc12c_backbone_aware_matched_loo.py
```

Relevant outputs:

```text
runs/BMC-12b/matched_leaveoneout_open/bmc12b_matched_leaveoneout_summary.csv
runs/BMC-12b/matched_leaveoneout_open/bmc12b_matched_leaveoneout_edges.csv
runs/BMC-12b/matched_leaveoneout_open/bmc12b_matched_leaveoneout_readout.md
runs/BMC-12c/backbone_aware_matched_loo_open/bmc12c_decision_comparison_summary.csv
runs/BMC-12c/backbone_aware_matched_loo_open/bmc12c_backbone_variant_summary_all_cases.csv
runs/BMC-12c/backbone_aware_matched_loo_open/bmc12c_backbone_aware_readout.md
```

Important caveat:

```text
Earlier BMC-12 runs based on BMC08a-like input are superseded for final interpretation.
```
