# BRIDGE_CARRIER_BLOCK_E_RESULTS — H2 discrimination

## Purpose
Test whether `distance_to_type_D` behaves like a genuine reduced-H2 transfer stabilizer or only as a mirror artifact under proxy-rigidity conditions.

## Summary table

| variant | active_features | internal_pass | internal_assignment | h2_pass | h2_assignment | h2_stability | transfer_signal |
|---|---|---:|---:|---:|---:|---:|---|
| full_reference | distance_to_type_D, spacing_cv, simple_rigidity_surrogate, grid_deviation_score | True | 0.6333333333333333 | False | 0.0 | 0.0 | internal_only_core |
| proxy_rigidity_only | simple_rigidity_surrogate | True | 0.8333333333333333 | False | 0.05555555555555555 | 0.0 | candidate_transfer_partial |
| proxy_rigidity_plus_distance | simple_rigidity_surrogate, distance_to_type_D | True | 0.7333333333333334 | False | 0.0 | 0.0 | internal_only_core |
| proxy_rigidity_plus_grid | simple_rigidity_surrogate, grid_deviation_score | True | 0.8 | False | 0.16666666666666666 | 0.13 | candidate_transfer_partial |
| proxy_rigidity_plus_spacing | simple_rigidity_surrogate, spacing_cv | True | 0.7444444444444445 | False | 0.0 | 0.0 | internal_only_core |
| proxy_rigidity_plus_grid_plus_distance | simple_rigidity_surrogate, grid_deviation_score, distance_to_type_D | True | 0.7333333333333334 | False | 0.0 | 0.0 | internal_only_core |

## Reading rule
- proxy_rigidity_plus_distance > proxy_rigidity_only supports the transfer-stabilizer hypothesis.
- proxy_rigidity_plus_distance > proxy_rigidity_plus_spacing argues against a generic reduced-feature artifact reading.
- proxy_rigidity_plus_grid_plus_distance > proxy_rigidity_plus_grid supports distance as a transport anchor in the richer reduced core.