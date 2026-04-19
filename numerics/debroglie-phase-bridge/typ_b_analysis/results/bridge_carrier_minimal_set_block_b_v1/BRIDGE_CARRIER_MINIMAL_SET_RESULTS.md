# BRIDGE_CARRIER_MINIMAL_SET_RESULTS — Block B

## Purpose
Test whether reduced two-feature sets already preserve a recognizable bridge picture under the corridor-based evaluator.

## Summary table

| variant | active_features | overall_pass | result_label | separation_margin_mean | assignment_score | original_stability_score | provisional_set_signal |
|---|---|---:|---|---:|---:|---:|---|
| full | distance_to_type_D, spacing_cv, simple_rigidity_surrogate, grid_deviation_score | True | supported | 0.12074074074074076 | 0.6333333333333333 | 0.945 | baseline |
| pair_rigidity_grid | simple_rigidity_surrogate, grid_deviation_score | True | supported | 0.2525925925925925 | 0.8 | 0.96 | candidate_minimal_sufficient_set |
| pair_rigidity_distance | simple_rigidity_surrogate, distance_to_type_D | True | supported | 0.19444444444444436 | 0.7333333333333334 | 0.855 | candidate_minimal_sufficient_set |
| pair_grid_distance | grid_deviation_score, distance_to_type_D | False | failed | 0.049259259259259225 | 0.3666666666666667 | 0.815 | insufficient_under_current_logic |
| pair_rigidity_spacing | simple_rigidity_surrogate, spacing_cv | True | supported | 0.19222222222222218 | 0.7444444444444445 | 0.99 | candidate_minimal_sufficient_set |
| pair_grid_spacing | grid_deviation_score, spacing_cv | False | failed | 0.04703703703703682 | 0.3666666666666667 | 0.76 | insufficient_under_current_logic |

## Interpretation
- candidate_minimal_sufficient_set: reduced set still passes under current logic
- candidate_near_sufficient_set: reduced set fails formally but remains close to full
- insufficient_under_current_logic: reduced set does not preserve the bridge picture
- weak_or_partial_set: reduced set retains only partial bridge signal