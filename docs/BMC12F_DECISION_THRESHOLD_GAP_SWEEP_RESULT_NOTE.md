# BMC-12f Decision-Threshold / Dominance-Gap Sweep Result Note

## Purpose

BMC-12f tests whether the sparse/local regime identified by BMC-12e remains stable under small perturbations of the decision thresholds.

BMC-12e showed that the all-feature baseline is fully retained at:

```text
N = 70, 75, 81
```

and weakens at denser graph sizes:

```text
N = 87, 92
```

BMC-12f therefore focuses on the sparse/local regime:

```text
N = 70, 75, 81
```

Unlike BMC-12e, BMC-12f does not re-run the legacy BMC07/BMC09d backbone runner. Instead, it reclassifies the existing BMC-12e variant-level arrangement signals under a small grid of decision-threshold pairs.

---

## 1. Input

Primary input:

```text
runs/BMC-12e/edgecount_neighborhood_sweep_open/bmc12e_edgecount_sweep_variant_summary.csv
```

BMC-12f uses the existing arrangement signals:

```text
full_graph_arrangement_signal
backbone_only_arrangement_signal
off_backbone_only_arrangement_signal
coupling_only_arrangement_signal
```

This makes BMC-12f a decision-sensitivity analysis, not a new graph construction or shuffle recomputation.

---

## 2. Threshold grid and reclassification rule

BMC-12f uses:

```text
arrangement_signal_min = 0.045, 0.050, 0.055
dominance_gap_min     = 0.020, 0.030, 0.040
```

This gives 9 threshold pairs.

For each variant row:

```text
best_competing_signal = max(S_full, S_off, S_coupling)
backbone_gap          = S_backbone - best_competing_signal
```

A variant is retained under a threshold pair if:

```text
S_backbone >= arrangement_signal_min
backbone_gap >= dominance_gap_min
```

This approximates the retained BMC09d-style condition:

```text
decision_label = backbone_localization_supported
dominant_arm   = backbone_only
```

using already-computed arrangement signals.

---

## 3. BMC-12f result summary

BMC-12f produced:

| N | case_id | dropped_feature | full | partial | none | mean_retained_fraction | stability |
|---:|---|---:|---:|---:|---:|---:|---|
| 70 | baseline_all_features | - | 3 | 6 | 0 | 0.778 | mixed_sensitive |
| 70 | drop_feature_length_scale | feature_length_scale | 0 | 3 | 6 | 0.111 | mixed_sensitive |
| 70 | drop_feature_mode_frequency | feature_mode_frequency | 0 | 9 | 0 | 0.667 | mixed_sensitive |
| 70 | drop_feature_shape_factor | feature_shape_factor | 0 | 0 | 9 | 0.000 | unstable_none |
| 70 | drop_feature_spectral_index | feature_spectral_index | 0 | 0 | 9 | 0.000 | unstable_none |
| 75 | baseline_all_features | - | 6 | 3 | 0 | 0.889 | mixed_sensitive |
| 75 | drop_feature_length_scale | feature_length_scale | 0 | 3 | 6 | 0.111 | mixed_sensitive |
| 75 | drop_feature_mode_frequency | feature_mode_frequency | 0 | 6 | 3 | 0.333 | mixed_sensitive |
| 75 | drop_feature_shape_factor | feature_shape_factor | 0 | 0 | 9 | 0.000 | unstable_none |
| 75 | drop_feature_spectral_index | feature_spectral_index | 6 | 3 | 0 | 0.889 | mixed_sensitive |
| 81 | baseline_all_features | - | 9 | 0 | 0 | 1.000 | stable_full |
| 81 | drop_feature_length_scale | feature_length_scale | 0 | 3 | 6 | 0.222 | mixed_sensitive |
| 81 | drop_feature_mode_frequency | feature_mode_frequency | 0 | 9 | 0 | 0.333 | mixed_sensitive |
| 81 | drop_feature_shape_factor | feature_shape_factor | 0 | 3 | 6 | 0.111 | mixed_sensitive |
| 81 | drop_feature_spectral_index | feature_spectral_index | 0 | 9 | 0 | 0.556 | mixed_sensitive |

---

## 4. Main finding

### 4.1 The BMC09d reference point is threshold-robust

At the original BMC09d reference edge count:

```text
N = 81
```

the all-feature baseline remains fully retained across all tested threshold pairs:

```text
full_retention_count = 9 / 9
mean_retained_fraction = 1.000
stability_label = stable_full
```

### Interpretation

The BMC09d reference anchor at N=81 is not merely a single hard-threshold artifact within the tested threshold grid.

This strengthens the interpretation of N=81 as the most stable reference point of the sparse/local backbone regime.

---

## 5. Sparse-neighborhood result

The lower neighboring edge counts remain supportive but threshold-sensitive:

```text
N = 70 baseline:
  full = 3 / 9
  partial = 6 / 9
  mean_retained_fraction = 0.778
  stability = mixed_sensitive

N = 75 baseline:
  full = 6 / 9
  partial = 3 / 9
  mean_retained_fraction = 0.889
  stability = mixed_sensitive
```

### Interpretation

BMC-12e showed that N=70 and N=75 are fully retained under the original decision thresholds. BMC-12f refines this:

```text
N=70 and N=75 are part of the sparse/local neighborhood,
but they are not fully decision-threshold robust.
```

The sparse/local regime is therefore best described as:

```text
strongest and threshold-robust at N=81,
supportive but threshold-sensitive at N=70 and N=75.
```

---

## 6. Feature-drop result

The leave-one-feature-out cases remain mostly mixed or unstable across the threshold grid.

Important observations:

```text
drop_feature_shape_factor:
  N=70 and N=75 are unstable_none
  N=81 is mixed_sensitive

drop_feature_spectral_index:
  N=70 is unstable_none
  N=75 is strong but mixed_sensitive
  N=81 is mixed_sensitive

drop_feature_mode_frequency:
  mixed_sensitive at N=70,75,81

drop_feature_length_scale:
  mixed_sensitive at N=70,75,81
```

### Interpretation

BMC-12f does not support a stable feature-role hierarchy.

Feature-ablation profiles remain threshold-sensitive and should be interpreted only as local diagnostics, not as causal feature importance.

---

## 7. Updated interpretation of BMC-12e/f

BMC-12e suggested that the BMC09d baseline is fully retained across:

```text
N = 70, 75, 81
```

BMC-12f refines this:

```text
N=81 is threshold-robust.
N=70 and N=75 are supportive but threshold-sensitive.
```

Revised interpretation:

> The BMC09d reference anchor at N=81 is robust under small decision-threshold and dominance-gap perturbations. The lower sparse-neighborhood points N=70 and N=75 retain substantial backbone signal but show threshold sensitivity. Feature-drop profiles remain mixed and should not be interpreted as stable feature-role hierarchies.

---

## 8. Relationship to red-team critique

BMC-12f directly addresses the red-team concern:

```text
The BMC-12e sparse/local regime may be a hard-threshold artifact.
```

The result is mixed but useful:

```text
N=81 baseline: not a single-threshold artifact within tested grid.
N=70/75 baseline: supportive but threshold-sensitive.
Feature drops: threshold-sensitive.
```

This supports a precise and cautious claim:

```text
The reference anchor is robust.
The broader neighborhood is suggestive but sensitive.
Feature-role claims remain premature.
```

---

## 9. Allowed statements after BMC-12f

Allowed:

```text
The BMC09d reference anchor at N=81 is stable across the tested threshold/gap grid.
```

```text
The sparse-neighborhood points N=70 and N=75 provide supportive but threshold-sensitive evidence.
```

```text
BMC-12f does not support a stable feature hierarchy.
```

```text
The strongest current statement concerns the robustness of the reference anchor, not causal feature importance.
```

Avoid:

```text
The entire sparse/local regime is fully threshold-robust.
```

```text
BMC-12 proves scale-dependent feature roles.
```

```text
Feature importance has been established.
```

```text
The BMC09d anchor is graph-density independent.
```

---

## 10. Consequence for project framing

The strongest updated BMC-12-level formulation is:

> BMC-12f supports the decision-threshold robustness of the BMC09d reference anchor at N=81. The lower sparse-neighborhood points N=70 and N=75 remain supportive but threshold-sensitive. Feature-ablation profiles remain mixed across threshold pairs and should not be interpreted as stable feature-role hierarchies.

A slightly broader formulation:

> The BMC09d anchor is best interpreted as a threshold-robust sparse/local reference point at N=81, embedded in a nearby but more threshold-sensitive sparse regime.

---

## 11. Next open control

BMC-12f still uses the same backbone variants:

```text
strength_topk_6
strength_topalpha_025
strength_topalpha_050
```

Therefore the next major methodological risk is method dependence of the backbone extraction itself.

Recommended next block:

```text
BMC-13 Alternative Backbone / Consensus-Backbone Filters
```

Purpose:

```text
Test whether the sparse/local BMC09d anchor depends on top-k/top-alpha extraction rules.
```

Candidate directions:

```text
alternative top-k values
alternative top-alpha values
mutual-kNN style filter
threshold-path consensus
salience / spanning-tree style backbone
null-model or disparity-like backbone filter
consensus backbone across multiple extraction methods
```

---

## 12. File anchors

BMC-12f specification:

```text
docs/BMC12F_DECISION_THRESHOLD_GAP_SWEEP_SPEC.md
```

BMC-12f config:

```text
data/bmc12f_decision_threshold_gap_sweep_config.yaml
```

BMC-12f runner:

```text
scripts/run_bmc12f_decision_threshold_gap_sweep.py
```

BMC-12f outputs:

```text
runs/BMC-12f/decision_threshold_gap_sweep_open/bmc12f_threshold_gap_variant_summary.csv
runs/BMC-12f/decision_threshold_gap_sweep_open/bmc12f_threshold_gap_decision_summary.csv
runs/BMC-12f/decision_threshold_gap_sweep_open/bmc12f_threshold_gap_stability_summary.csv
runs/BMC-12f/decision_threshold_gap_sweep_open/bmc12f_threshold_gap_readout.md
runs/BMC-12f/decision_threshold_gap_sweep_open/bmc12f_metrics.json
```

---

## 13. Consolidated status after BMC-12f

### Befund

The BMC09d reference anchor at N=81 is fully retained across all tested decision-threshold and dominance-gap pairs. Lower neighboring sparse edge-counts N=70 and N=75 retain substantial signal but are threshold-sensitive.

### Interpretation

The strongest current BMC-12 result is the threshold robustness of the N=81 reference anchor. The broader sparse/local regime remains suggestive but not fully threshold-stable.

### Hypothesis

The BMC09d N=81 anchor may represent a particularly stable sparse/local decision point within a nearby but threshold-sensitive relational backbone regime.

### Open gap

Backbone method dependence remains open. BMC-13 should test whether the result depends on the current top-k/top-alpha backbone definitions.
