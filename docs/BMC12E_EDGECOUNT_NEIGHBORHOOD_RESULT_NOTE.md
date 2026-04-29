# BMC-12e Edge-Count Neighborhood Sweep Result Note

## Purpose

BMC-12e tests the strongest graph-size objection raised during red-team review of BMC-12c.

BMC-12c showed a structured feature leave-one-out retention pattern at the BMC09d reference graph size:

```text
N_edges = 81
```

However, Grok's sharper red-team review emphasized that this could be a local graph-size artifact. BMC-12e therefore varies the matched edge count around the BMC09d reference point.

This note records the BMC-12e result and updates the interpretation of BMC-12c.

---

## 1. Input and method

BMC-12e uses the reconciled BMC08c-compatible feature source:

```text
data/bmc12_feature_table_with_derived_from_bmc08c.csv
```

The original BMC09d-compatible graph at N=81 had already been exactly reconstructed in BMC-12b:

```text
original_edges:        81
bmc12b_baseline_edges: 81
shared_edges:          81
only_original:         0
only_bmc12b:           0
weight_differences:    0
```

BMC-12e varies the matched edge count:

```text
N = 70, 75, 81, 87, 92
```

For each N, it tests:

```text
baseline_all_features
drop_feature_mode_frequency
drop_feature_length_scale
drop_feature_shape_factor
drop_feature_spectral_index
```

Each graph is passed through the established BMC07/BMC09d backbone-variant runner.

Reference retained decision:

```text
decision_label = backbone_localization_supported
dominant_arm   = backbone_only
```

Backbone variants:

```text
strength_topk_6
strength_topalpha_025
strength_topalpha_050
```

---

## 2. BMC-12e decision summary

| N | case_id | dropped_feature | retained_variants | retained_fraction | status |
|---:|---|---:|---:|---:|---|
| 70 | baseline_all_features | - | 3/3 | 1.000 | decision_retained |
| 70 | drop_feature_mode_frequency | feature_mode_frequency | 2/3 | 0.667 | decision_partially_retained |
| 70 | drop_feature_length_scale | feature_length_scale | 0/3 | 0.000 | decision_not_retained |
| 70 | drop_feature_shape_factor | feature_shape_factor | 0/3 | 0.000 | decision_not_retained |
| 70 | drop_feature_spectral_index | feature_spectral_index | 0/3 | 0.000 | decision_not_retained |
| 75 | baseline_all_features | - | 3/3 | 1.000 | decision_retained |
| 75 | drop_feature_mode_frequency | feature_mode_frequency | 1/3 | 0.333 | decision_partially_retained |
| 75 | drop_feature_length_scale | feature_length_scale | 1/3 | 0.333 | decision_partially_retained |
| 75 | drop_feature_shape_factor | feature_shape_factor | 0/3 | 0.000 | decision_not_retained |
| 75 | drop_feature_spectral_index | feature_spectral_index | 3/3 | 1.000 | decision_retained |
| 81 | baseline_all_features | - | 3/3 | 1.000 | decision_retained |
| 81 | drop_feature_mode_frequency | feature_mode_frequency | 1/3 | 0.333 | decision_partially_retained |
| 81 | drop_feature_length_scale | feature_length_scale | 1/3 | 0.333 | decision_partially_retained |
| 81 | drop_feature_shape_factor | feature_shape_factor | 1/3 | 0.333 | decision_partially_retained |
| 81 | drop_feature_spectral_index | feature_spectral_index | 2/3 | 0.667 | decision_partially_retained |
| 87 | baseline_all_features | - | 1/3 | 0.333 | decision_partially_retained |
| 87 | drop_feature_mode_frequency | feature_mode_frequency | 1/3 | 0.333 | decision_partially_retained |
| 87 | drop_feature_length_scale | feature_length_scale | 1/3 | 0.333 | decision_partially_retained |
| 87 | drop_feature_shape_factor | feature_shape_factor | 1/3 | 0.333 | decision_partially_retained |
| 87 | drop_feature_spectral_index | feature_spectral_index | 1/3 | 0.333 | decision_partially_retained |
| 92 | baseline_all_features | - | 0/3 | 0.000 | decision_not_retained |
| 92 | drop_feature_mode_frequency | feature_mode_frequency | 3/3 | 1.000 | decision_retained |
| 92 | drop_feature_length_scale | feature_length_scale | 0/3 | 0.000 | decision_not_retained |
| 92 | drop_feature_shape_factor | feature_shape_factor | 0/3 | 0.000 | decision_not_retained |
| 92 | drop_feature_spectral_index | feature_spectral_index | 1/3 | 0.333 | decision_partially_retained |

---

## 3. Main result

### 3.1 The N=81 BMC-12c feature profile is not globally stable

The original BMC-12c profile at N=81 was:

```text
drop feature_mode_frequency: 1/3
drop feature_length_scale:   1/3
drop feature_shape_factor:   1/3
drop feature_spectral_index: 2/3
```

BMC-12e shows that this exact pattern does not persist across neighboring N values.

Examples:

```text
N=70:
  mode_frequency 2/3
  length_scale   0/3
  shape_factor   0/3
  spectral_index 0/3

N=75:
  mode_frequency 1/3
  length_scale   1/3
  shape_factor   0/3
  spectral_index 3/3

N=87:
  all feature drops 1/3

N=92:
  mode_frequency 3/3
  length_scale   0/3
  shape_factor   0/3
  spectral_index 1/3
```

### Interpretation

The BMC-12c feature-retention profile is graph-size sensitive.

Therefore, BMC-12c should be interpreted as a local decision-point diagnostic at the BMC09d reference edge count, not as a globally stable feature-role hierarchy.

---

## 4. Baseline stability across N

The all-feature baseline shows a clear regime structure:

```text
N=70  baseline 3/3 retained
N=75  baseline 3/3 retained
N=81  baseline 3/3 retained
N=87  baseline 1/3 retained
N=92  baseline 0/3 retained
```

### Interpretation

The BMC09d backbone-only decision is stable across a lower-to-reference sparse graph regime:

```text
N = 70, 75, 81
```

It weakens or disappears in denser graph regimes:

```text
N = 87, 92
```

This suggests that the BMC09d anchor is tied to a sparse/local backbone regime rather than to arbitrary graph density.

---

## 5. Important regime warning

At N=92, the all-feature baseline fails completely:

```text
baseline_all_features: 0/3 retained
```

but dropping `feature_mode_frequency` yields:

```text
drop_feature_mode_frequency: 3/3 retained
```

This is a strong warning against simple feature-importance language.

At this density, the graph is no longer in the same decision regime as the original BMC09d anchor. Feature drops may move the graph between regimes rather than reveal simple feature roles.

### Consequence

Avoid statements such as:

```text
feature_mode_frequency is unimportant
```

or:

```text
feature_mode_frequency stabilizes the backbone
```

unless explicitly qualified by edge-count regime.

---

## 6. Updated interpretation of BMC-12c

### Previous cautious interpretation

BMC-12c suggested structured joint-feature-basis sensitivity at N=81.

### Updated after BMC-12e

BMC-12c remains valid as a local diagnostic at the BMC09d reference edge count:

```text
N=81
```

But its feature-retention profile is not stable enough across neighboring edge counts to support a strong global feature-role hierarchy.

### Revised wording

A defensible interpretation is:

> BMC-12c shows structured leave-one-out sensitivity at the BMC09d reference graph size. BMC-12e shows that this sensitivity pattern is graph-size dependent: the all-feature BMC09d backbone decision remains fully retained in the sparse-to-reference range N=70,75,81, but weakens at denser graph sizes N=87 and N=92. The N=81 feature-retention profile should therefore be interpreted as a local decision-point result within a sparse/local backbone regime, not as a globally stable feature-role hierarchy.

---

## 7. Relationship to red-team critique

BMC-12e directly addresses Grok's strongest graph-size objection:

```text
The BMC-12c pattern may be a local artifact of matched-edge-count plus hard-decision logic at N=81.
```

BMC-12e partially confirms this concern:

```text
The exact feature-retention pattern does not persist across N.
```

But it also adds a constructive result:

```text
The all-feature baseline remains fully retained across N=70,75,81.
```

Thus the outcome is not simply negative. It narrows the valid regime:

```text
BMC09d is a sparse/local backbone-regime anchor.
```

---

## 8. Consequences for future interpretation

### Allowed statements

```text
The BMC09d baseline is exactly reproduced at N=81.
```

```text
The BMC09d backbone-only decision remains fully retained across N=70,75,81.
```

```text
The N=81 leave-one-out feature-retention profile is graph-size sensitive.
```

```text
The BMC09d anchor appears tied to a sparse/local graph regime.
```

```text
BMC-12c remains a local diagnostic, not a global feature-role proof.
```

### Avoid

```text
BMC-12 proves scale-dependent feature roles.
```

```text
BMC-12 identifies causal feature importance.
```

```text
The feature hierarchy is stable across graph sizes.
```

```text
The N=81 pattern is globally robust.
```

---

## 9. Recommended next step

The next control remains:

```text
BMC-12f Decision-Threshold / Dominance-Gap Sensitivity Sweep
```

However, BMC-12e changes how BMC-12f should be focused.

Recommended focus:

```text
N = 70, 75, 81
```

because these are the edge-counts where the all-feature baseline remains fully retained.

Optional secondary focus:

```text
N = 87, 92
```

only as denser-regime comparison, not as primary reference.

Suggested threshold grid:

```text
arrangement_signal_min = 0.045, 0.050, 0.055
dominance_gap_min     = 0.020, 0.030, 0.040
```

Main BMC-12f question:

```text
Within the sparse/local regime N=70,75,81,
does the BMC09d-like decision remain stable under small decision-threshold perturbations?
```

---

## 10. Consolidated project status after BMC-12e

### Befund

BMC-12e shows that the all-feature BMC09d backbone decision is stable across N=70,75,81 and unstable at denser graph sizes N=87,92. The BMC-12c feature-drop profile at N=81 does not persist as an exact neighborhood pattern.

### Interpretation

The BMC09d anchor should be interpreted as a sparse/local backbone-regime signal. Feature-drop interpretations are regime-dependent.

### Hypothesis

The BMC09d structure may be associated with a local sparse graph regime in which strong relational organization is preserved before denser graph connections introduce competing full-graph or mixed-arm behavior.

### Open gap

Decision-threshold brittleness remains untested. BMC-12f is needed before using BMC-12 as a manuscript-level robustness argument.

---

## 11. File anchors

BMC-12e specification:

```text
docs/BMC12E_EDGECOUNT_NEIGHBORHOOD_SWEEP_SPEC.md
```

BMC-12e runner:

```text
scripts/run_bmc12e_edgecount_neighborhood_sweep.py
```

BMC-12e collector:

```text
scripts/collect_bmc12e_outputs.py
```

BMC-12e config:

```text
data/bmc12e_edgecount_neighborhood_sweep_config.yaml
```

BMC-12e final outputs:

```text
runs/BMC-12e/edgecount_neighborhood_sweep_open/bmc12e_edgecount_sweep_decision_summary.csv
runs/BMC-12e/edgecount_neighborhood_sweep_open/bmc12e_edgecount_sweep_variant_summary.csv
runs/BMC-12e/edgecount_neighborhood_sweep_open/bmc12e_edgecount_sweep_readout.md
runs/BMC-12e/edgecount_neighborhood_sweep_open/bmc12e_metrics.json
```

BMC-12e edge inventory:

```text
runs/BMC-12e/edgecount_neighborhood_sweep_open/bmc12e_edgecount_sweep_edges_inventory.csv
```
