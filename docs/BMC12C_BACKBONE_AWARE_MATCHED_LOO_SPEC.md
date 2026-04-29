# BMC-12c Backbone-Aware Matched Leave-One-Out Specification

## Purpose

BMC-12c tests whether the original BMC-09d `backbone_only` decision structure remains stable under matched leave-one-out feature removal.

BMC-12a showed fixed-tau densification.
BMC-12b controlled graph size by matching every leave-one-out graph to the all-feature baseline edge count.
BMC-12c now reuses the established BMC-09d/BMC-07 backbone-variant runner on those matched graphs.

## Reference decision

Reference file:

```text
runs/BMC-09/BMC09d_threshold_tau_03_realdata_open/backbone_variant_summary.csv
```

Reference result:

```text
3 / 3 variants:
decision_label = backbone_localization_supported
dominant_arm   = backbone_only
```

Reference variants:

```text
strength_topk_6
strength_topalpha_025
strength_topalpha_050
```

## Method

The script:

1. reads `runs/BMC-12b/matched_leaveoneout_open/bmc12b_matched_leaveoneout_edges.csv`
2. filters each BMC-12b case
3. writes old-style input folders with:
   - `baseline_relational_table_real.csv`
   - `node_metadata_real.csv`
4. writes one runner config per case
5. calls `scripts/bmc07_backbone_variation_runner.py`
6. collects `backbone_variant_summary.csv`
7. compares each result against the BMC-09d reference decision

## Generated data

```text
data/bmc12c_backbone_aware_inputs/<case_id>/
data/bmc12c_backbone_aware_configs/<case_id>.yaml
```

## Output

```text
runs/BMC-12c/backbone_aware_matched_loo_open/
```

Final files:

```text
bmc12c_backbone_variant_summary_all_cases.csv
bmc12c_decision_comparison_summary.csv
bmc12c_metrics.json
bmc12c_backbone_aware_readout.md
```

## Decision status

```text
decision_retained
```

All variants retain:

```text
decision_label = backbone_localization_supported
dominant_arm   = backbone_only
```

```text
decision_partially_retained
```

At least one, but not all, variants retain the reference decision.

```text
decision_not_retained
```

No variant retains the reference decision.

## Field list: `bmc12c_decision_comparison_summary.csv`

| field | type | description |
|---|---|---|
| case_id | string | BMC-12b graph case |
| dropped_feature | string | Removed feature, empty for baseline |
| variant_count | integer | Number of backbone variants |
| retained_variant_count | integer | Number retaining the BMC-09d reference decision |
| retained_fraction | float | retained_variant_count / variant_count |
| failed_variant_count | integer | Number not retaining the reference decision |
| all_variants_retained | boolean string | true if all variants retain the decision |
| any_fragment_or_failure | boolean string | true if at least one variant fails |
| bmc12c_decision_status | string | decision_retained / decision_partially_retained / decision_not_retained |

## Interpretation template

### Befund

BMC-12c re-runs the established BMC-09d backbone-variant decision logic on BMC-12b matched leave-one-out graphs.

### Interpretation

If a feature drop retains the 3/3 `backbone_only` decision, the BMC-09d decision structure is robust to that feature removal under matched graph size.

### Hypothesis

Feature drops that fail or partially retain the decision identify features that contribute to decision-level backbone structure, not merely edge overlap.

### Open gap

BMC-12c remains a graph-diagnostic robustness test. It does not prove physical content.
