# BRIDGE_CARRIER_BLOCK_C_RESULTS — singles and triples

## Purpose
Test singleton anchors and triple sets after block B minimal-pair findings.

## Summary table

| variant | feature_count | overall_pass | result_label | separation_margin_mean | assignment_score | original_stability_score | provisional_set_signal |
|---|---:|---:|---|---:|---:|---:|---|
| full | 4 | True | supported | 0.12074074074074076 | 0.6333333333333333 | 0.945 | baseline |
| single_distance | 1 | False | failed | -0.008888888888888724 | 0.26666666666666666 | 0.625 | insufficient_under_current_logic |
| single_spacing | 1 | False | failed | -0.01333333333333353 | 0.26666666666666666 | 0.625 | insufficient_under_current_logic |
| single_rigidity | 1 | True | supported | 0.3977777777777774 | 0.8333333333333333 | 0.87 | candidate_single_anchor |
| single_grid | 1 | False | failed | 0.10740740740740745 | 0.5777777777777777 | 0.85 | insufficient_under_current_logic |
| triple_without_distance | 3 | True | supported | 0.1639506172839505 | 0.7444444444444445 | 0.985 | candidate_near_full_core |
| triple_without_spacing | 3 | True | supported | 0.16543209876543202 | 0.7333333333333334 | 0.925 | candidate_near_full_core |
| triple_without_rigidity | 3 | False | failed | 0.02839506172839512 | 0.4222222222222222 | 0.82 | insufficient_under_current_logic |
| triple_without_grid | 3 | False | failed | 0.12518518518518507 | 0.3666666666666667 | 0.895 | insufficient_under_current_logic |