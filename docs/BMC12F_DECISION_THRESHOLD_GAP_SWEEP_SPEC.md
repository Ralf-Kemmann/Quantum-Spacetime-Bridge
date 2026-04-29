# BMC-12f Decision-Threshold / Dominance-Gap Sensitivity Sweep Specification

## Purpose

BMC-12f tests whether the sparse/local BMC-12e baseline regime remains stable under small perturbations of the decision thresholds.

BMC-12e showed:

```text
N=70 baseline 3/3 retained
N=75 baseline 3/3 retained
N=81 baseline 3/3 retained
N=87 baseline 1/3 retained
N=92 baseline 0/3 retained
```

Therefore BMC-12f focuses on:

```text
N = 70, 75, 81
```

BMC-12f does not re-run the legacy BMC07/BMC09d runner. It reclassifies existing BMC-12e arrangement signals.

## Input

```text
runs/BMC-12e/edgecount_neighborhood_sweep_open/bmc12e_edgecount_sweep_variant_summary.csv
```

Required signal columns:

```text
full_graph_arrangement_signal
backbone_only_arrangement_signal
off_backbone_only_arrangement_signal
coupling_only_arrangement_signal
```

## Threshold grid

```text
arrangement_signal_min = 0.045, 0.050, 0.055
dominance_gap_min     = 0.020, 0.030, 0.040
```

## Reclassification rule

For each variant:

```text
S_full     = full_graph_arrangement_signal
S_backbone = backbone_only_arrangement_signal
S_off      = off_backbone_only_arrangement_signal
S_coupling = coupling_only_arrangement_signal

best_competing_signal = max(S_full, S_off, S_coupling)
backbone_gap          = S_backbone - best_competing_signal
```

A variant is retained if:

```text
S_backbone >= arrangement_signal_min
backbone_gap >= dominance_gap_min
```

This approximates the original retained condition:

```text
decision_label = backbone_localization_supported
dominant_arm   = backbone_only
```

## Outputs

```text
runs/BMC-12f/decision_threshold_gap_sweep_open/bmc12f_threshold_gap_variant_summary.csv
runs/BMC-12f/decision_threshold_gap_sweep_open/bmc12f_threshold_gap_decision_summary.csv
runs/BMC-12f/decision_threshold_gap_sweep_open/bmc12f_threshold_gap_stability_summary.csv
runs/BMC-12f/decision_threshold_gap_sweep_open/bmc12f_threshold_gap_readout.md
runs/BMC-12f/decision_threshold_gap_sweep_open/bmc12f_metrics.json
```

## Field list: stability summary

| field | type | description |
|---|---|---|
| edge_count_target | integer | Matched top-N edge count |
| case_id | string | Baseline or leave-one-out case |
| dropped_feature | string | Dropped feature, empty for baseline |
| threshold_pair_count | integer | Number of threshold pairs |
| full_retention_count | integer | Count of threshold pairs with 3/3 retained |
| partial_retention_count | integer | Count of threshold pairs with 1/3 or 2/3 retained |
| no_retention_count | integer | Count of threshold pairs with 0/3 retained |
| mean_retained_fraction | float | Mean retained fraction over threshold grid |
| min_retained_fraction | float | Minimum retained fraction |
| max_retained_fraction | float | Maximum retained fraction |
| stability_label | string | stable_full / mixed_sensitive / unstable_none |

## Interpretation

If the all-feature baseline remains 3/3 across all threshold pairs for N=70,75,81, the sparse/local BMC09d regime is not merely a single decision-threshold artifact.

If baseline retention changes strongly under small threshold perturbations, the sparse/local regime is threshold-sensitive.

## Open gap

BMC-12f still uses the same top-k/top-alpha variants. Method-dependence remains open for BMC-13.
