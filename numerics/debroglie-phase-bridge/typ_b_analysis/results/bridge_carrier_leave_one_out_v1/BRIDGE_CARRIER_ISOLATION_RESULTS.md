# BRIDGE_CARRIER_ISOLATION_RESULTS — Leave-one-out block A

## Purpose
Test structural necessity of the four current core bridge-carrier candidates by removing one variable at a time.

## Summary table

| variant | removed_variable | overall_pass | result_label | separation_margin_mean | assignment_score | original_stability_score | provisional_role_signal |
|---|---|---:|---|---:|---:|---:|---|
| full | - | True | supported | 0.12074074074074076 | 0.6333333333333333 | 0.945 | baseline |
| minus_distance_to_type_D | distance_to_type_D | True | supported | 0.1639506172839505 | 0.7444444444444445 | 0.985 | candidate_redundant_or_diagnostic |
| minus_spacing_cv | spacing_cv | True | supported | 0.16543209876543202 | 0.7333333333333334 | 0.925 | candidate_redundant_or_diagnostic |
| minus_simple_rigidity_surrogate | simple_rigidity_surrogate | False | failed | 0.02839506172839512 | 0.4222222222222222 | 0.82 | candidate_primary |
| minus_grid_deviation_score | grid_deviation_score | False | failed | 0.12518518518518507 | 0.3666666666666667 | 0.895 | candidate_primary |

## Interpretation
- candidate_primary: strong structural damage or collapse after removal
- candidate_secondary: weakening without total collapse
- candidate_redundant_or_diagnostic: little change under current conditions
