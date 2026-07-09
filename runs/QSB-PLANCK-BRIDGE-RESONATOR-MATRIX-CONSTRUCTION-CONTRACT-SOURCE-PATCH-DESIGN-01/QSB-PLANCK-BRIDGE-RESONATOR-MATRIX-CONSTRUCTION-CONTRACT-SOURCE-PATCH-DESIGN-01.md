# QSB Planck Bridge Resonator Matrix Construction Contract Source Patch Design 01

## 1. Executive Summary

This run designs the minimal source/export patch required to make the QSB/PBR `K_candidate` Matrix Construction Contract reviewable and later executable.

`source_patch_design_status=patch_design_ready_for_implementation`

Patch type:

`combined_patch_required`

This means the later implementation likely needs a scoped K-only callable, export manifests, contract artifacts, and a validation harness.

## 2. Why Source Patch Design Is Needed

The Human Review run classified the contract review as:

`contract_review_status=blocked_requires_source_patch`

Execution 01A remains blocked because essential fields are not yet exposed in a standalone, executable contract form.

## 3. Inputs Used and Limitations

Primary input:

`runs/QSB-PLANCK-BRIDGE-RESONATOR-MATRIX-CONSTRUCTION-CONTRACT-HUMAN-REVIEW-01/`

Supporting inputs:

- `runs/QSB-PLANCK-BRIDGE-RESONATOR-MATRIX-CONSTRUCTION-CONTRACT-DESIGN-01/`
- `runs/QSB-PLANCK-BRIDGE-RESONATOR-MATRIX-CONSTRUCTION-CONTRACT-SOURCE-ALIGNMENT-01/`
- `runs/QSB-PLANCK-BRIDGE-RESONATOR-LAG-CLASS-SUFFICIENCY-EXECUTION-01/`
- `runs/QSB-PLANCK-BRIDGE-RESONATOR-LAG-CLASS-SUFFICIENCY-DESIGN-01/`

Limitation: this run does not implement any patch. It only designs the later implementation scope.

## 4. Human Review Blocking Issues

See `data/blocker_inventory.csv`.

Main blocker themes:

- K-only callable.
- Duplicate and missing row/pair policies.
- Lag-class handoff and export.
- Missing value policy.
- Rank and metric policy.
- Random seed and trial count policy.
- Validation command.

## 5. Patch Scope and Non-Scope

Patch scope:

- Create or wrap a K-only reconstruction/validation callable.
- Export explicit contract fields.
- Export or pin input pair/source identity.
- Export lag-class handoff.
- Export randomization/control policy.
- Create validation harness.

Non-scope:

- No source modification in this run.
- No K reconstruction in this run.
- No sufficiency execution.
- No physical or mechanism claim.

## 6. Source Artifacts to Patch or Wrap

See `data/source_artifacts_to_patch.csv`.

Preferred design: create a new scoped wrapper/module rather than mutating the historical EXTRACT03A-R1 runner.

## 7. P0-P9 Patch Design

### P0 - Patch metadata

See `data/source_patch_design_summary.csv`.

### P1 - Blocker inventory

See `data/blocker_inventory.csv`.

### P2 - Source artifacts to patch or wrap

See `data/source_artifacts_to_patch.csv`.

### P3 - K-only callable / reconstruction interface design

See `data/k_only_callable_design.csv`.

Proposed callable target:

`scripts/qsb_pbr_matrix_contract/reconstruct_k_candidate.py`

### P4 - Pair and data policy export design

See `data/pair_data_policy_export_design.csv`.

### P5 - Lag-class handoff/export design

See `data/lag_class_handoff_export_design.csv`.

### P6 - Matrix rule and numerical policy design

See `data/matrix_rule_numerical_policy_export_design.csv`.

### P7 - Randomization and control policy design

See `data/randomization_control_policy_design.csv`.

### P8 - Validation harness design

See `data/validation_harness_design.csv`.

### P9 - Future implementation prompt skeleton

See `data/future_implementation_prompt_skeleton.csv` and `docs/FUTURE_IMPLEMENTATION_PROMPT_SKELETON.md`.

## 8. Acceptance Tests

See `data/acceptance_tests.csv`.

All acceptance tests are blocking for the next implementation/review chain.

## 9. Patch Risks

See `data/patch_risk_register.csv`.

High risks include hidden state, invented lag values, randomization leakage, and rank-policy tuning.

## 10. Future Implementation Prompt Skeleton

The implementation skeleton is non-executable in this run. It is a reviewable prompt outline for a later implementation run only after design review.

## 11. Recommended Next Actions

Recommended next run:

`QSB-PLANCK-BRIDGE-RESONATOR-MATRIX-CONSTRUCTION-CONTRACT-SOURCE-PATCH-DESIGN-REVIEW-01`

## 12. Claim Boundaries

`physical_claim_release=blocked_no_physics_claim`

`mechanism_claim_release=blocked_no_mechanism_claim`

No source code was modified. No K matrix was reconstructed. No sufficiency test was executed.

## 13. German Claim-Safe Summary

Dieser Source-Patch-Design-Run entwirft den minimalen Patch-/Exportumfang, der erforderlich ist, um den Matrix-Construction-Contract der QSB/PBR-K_candidate-Matrix ausfuehrbar und reviewbar zu machen. Grundlage ist der Human-Review-Befund `blocked_requires_source_patch`. Der Run implementiert keine Codeaenderung, rekonstruiert keine Matrix, berechnet keine Spektren, fuehrt keinen Lag-Class-Sufficiency-Test aus und erzeugt keine neue Matrixregel. Er beschreibt nur, welche Contract-Felder, Policies, Callables und Validierungsbefehle ein spaeterer Implementierungslauf offenlegen muss. Physikalische Claims und Mechanismusclaims bleiben gesperrt.

