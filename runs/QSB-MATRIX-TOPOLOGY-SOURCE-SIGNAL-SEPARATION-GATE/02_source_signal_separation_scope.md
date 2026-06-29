# QSB-MATRIX-TOPOLOGY-SOURCE-SIGNAL-SEPARATION-GATE Scope

## Purpose

This run asks whether any source-driven signal remains after the already identified rule, label, `abs_delta`, and threshold structures are separated or accounted for.

The run does not retest whether EXTRACT03 has a structure. That structure is already established. This gate tests whether current artifacts are sufficient to support a source-signal claim beyond the artifact-level rule/label/threshold explanation.

## Source Basis

Primary and context artifacts are read from:

- `runs/QSB-EXTRACT03A-R1/authorized_execution_with_s1_addendum/16_edge_candidate_result.csv`
- `runs/QSB-MATRIX-TOPOLOGY-BLOCK-STRUCTURE-AUDIT/04_block_structure_summary.json`
- `runs/QSB-MATRIX-TOPOLOGY-BLOCK-SEMANTICS-AUDIT/04_block_semantics_summary.json`
- `runs/QSB-MATRIX-TOPOLOGY-BLOCK-STRENGTH-PROFILE/04_block_strength_summary.json`
- `runs/QSB-MATRIX-TOPOLOGY-BLOCK-NULLMODEL-AUDIT/04_nullmodel_summary.json`
- `runs/QSB-MATRIX-TOPOLOGY-STRUCTURE-ORIGIN-AUDIT/04_structure_origin_summary.json`
- `runs/QSB-MATRIX-TOPOLOGY-STRUCTURE-ORIGIN-AUDIT/12_negative_control_recommendations.md`
- optional detector-generalization artifacts, if present

## Claim Boundary

This is a methodological source-signal separation gate. It makes no claim about physical geometry, spacetime, metric structure, gravitation, causality, dynamics, experimental validation, or physical emergence.

Allowed outcomes are limited to:

- `source_signal_supported_under_current_artifacts`
- `source_signal_not_resolved_under_current_artifacts`
- `source_signal_absent_after_rule_label_threshold_controls`

Unsupported outcomes include `spacetime_detected`, `gravity_detected`, `metric_detected`, and `physical_emergence_confirmed`.
