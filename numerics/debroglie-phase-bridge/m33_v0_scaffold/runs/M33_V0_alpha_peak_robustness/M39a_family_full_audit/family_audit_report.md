# M.3.9a.2 — Family Full Audit Report

## Global summary

- Families total: 5
- Families passed: 4
- Family pass fraction: 0.800
- delta_p2-dominant families: 5
- F5 falsification alert: 0
- Global pass flag: 1

## Family summaries

### F1 (control)
- expected_type: control_symmetric
- dominant_level: delta_p2
- mean_branch_match_frac: 0.543
- mean_identity_strength: 0.386
- delta_p2_strength: 0.464
- family_pass_flag: 1

### F2 (compact_negative)
- expected_type: compact_negative_candidate
- dominant_level: delta_p2
- mean_branch_match_frac: 0.518
- mean_identity_strength: 0.337
- delta_p2_strength: 0.428
- family_pass_flag: 1

### F3 (large_negative)
- expected_type: large_negative_candidate
- dominant_level: delta_p2
- mean_branch_match_frac: 0.657
- mean_identity_strength: 0.614
- delta_p2_strength: 0.636
- family_pass_flag: 1

### F4 (large_negative_distorted)
- expected_type: large_negative_candidate
- dominant_level: delta_p2
- mean_branch_match_frac: 0.563
- mean_identity_strength: 0.426
- delta_p2_strength: 0.495
- family_pass_flag: 1

### F5 (falsification_candidate)
- expected_type: control_symmetric
- dominant_level: delta_p2
- mean_branch_match_frac: 0.468
- mean_identity_strength: 0.237
- delta_p2_strength: 0.353
- family_pass_flag: 0

## Matched-pair comparison

- F2 vs F3: n=7, same_branch_fraction=1.000, label=same_branch_dominance
- F2 vs F4: n=9, same_branch_fraction=1.000, label=same_branch_dominance

## F5 falsification

- family_id: F5
- observed_branch_match_frac: 0.468
- observed_identity_strength: 0.237
- falsification_alert_flag: 0
