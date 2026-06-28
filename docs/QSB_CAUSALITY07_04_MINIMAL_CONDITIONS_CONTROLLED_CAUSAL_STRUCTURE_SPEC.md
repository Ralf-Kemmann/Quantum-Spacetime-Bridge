# QSB-CAUSALITY07-04 Minimal Conditions for a Controlled Causal Structure Spec

## Status and Scope

```text
block_id = QSB-CAUSALITY07-04
input_blocks = QSB-CAUSALITY07-01,QSB-CAUSALITY07-02,QSB-CAUSALITY07-03
block_type = controlled_causal_structure_condition_evaluation
physical_causality_claimed = no
emergent_time_claimed = no
irreversible_temporal_direction_claimed = no
complete_chemical_identity_claimed = no
```

This block evaluates whether the CAUSALITY07 reduced Oregonator case satisfies explicit minimal conditions for a controlled causal-structure candidate. It does not claim that recurrence alone proves causality. The valid target is a formally explicit, controlled, and falsifiable candidate structure for causal ordering within the CAUSALITY07 model domain.

## Required Inputs

The evaluation uses the 07-01 case definition, the 07-02 reduced-model configuration and source inventory, and the 07-03 cycle-semantics hardening outputs. The known 07-03 basis is:

```text
baseline_sequence = P0 -> P1 -> P2 -> P3 -> P4 -> P0
complete_baseline_cycles = 10
mean_cycle_duration = 20.9 model-time units
reverse_control_cycles = 0
scrambled_control_cycles = 0
cycle_sequence_source = predefined_phase_sequence
global_cycle_order_independently_reconstructed = no
state_vector_distance_threshold = 0.08
threshold_empirically_calibrated = no
similarity_function_defined = no
```

The value `20.9` remains model time. The threshold `0.08` retains its documented status and is not silently declared dimensionless.

## Sequence Versus Causality

An ordered sequence is not by itself a causality claim. QSB-CAUSALITY07-04 separates:

- ordered state sequence
- directed transition admissibility
- predecessor-dependent progression
- rejection of arbitrary permutation
- control-sensitive recurrence
- bounded perturbation robustness
- closure consistency
- causal interpretation gate

The final class is derived from the condition matrix, not from recurrence alone.

## Conditions

### C1 Ordered State Distinction

C1 asks whether the assigned states are distinguishable in the reduced representation. Evidence may include distinct assigned phase labels and documented reduced-model descriptors. Passing C1 does not validate full chemical phase identity.

### C2 Directed Transition Admissibility

C2 checks whether observed baseline edges belong to an explicit allowed transition set. Reverse edges and an intentionally invalid transition are evaluated separately. Direction is not inferred solely from row order.

### C3 Predecessor Dependence

C3 asks whether the interpretation of a target state depends on its actual predecessor. The predecessor counterfactual matrix compares actual and alternative predecessors. This is a structural counterfactual test, not a laboratory intervention.

### C4 Permutation Rejection

C4 checks whether reverse, scrambled, and deterministic non-baseline permutations fail under the same detection rule. Permutation rejection is necessary for this controlled structure but is not sufficient for causality.

### C5 Control-Sensitive Recurrence

C5 requires baseline recurrence and zero or reduced recurrence in controls under the same detector. The existing 07-03 controls provide reverse and scrambled zero-cycle results.

### C6 Bounded Perturbation Robustness

C6 may pass only if bounded perturbation outputs exist and do not redefine the model. No laboratory noise model is invented. If current outputs lack explicit perturbation runs, the status is `not_evaluable_from_current_outputs`.

### C7 Closure Consistency

C7 asks whether the terminal state returns to the registered entry condition under the same identity rule. This block distinguishes assigned-phase recurrence and reduced-state proximity from complete chemical identity and full physical-state identity.

### C8 Causal Interpretation Gate

C8 assigns a final class only after C1-C7 have been evaluated. The gate rejects undocumented unit conversions, undocumented threshold claims, recurrence-as-identity claims, and unsupported physical-causality or emergent-time claims.

## Composite Classification

Allowed final classes are:

- `controlled_causal_structure_candidate`
- `ordered_recurrence_with_control_selectivity`
- `ordered_sequence_only`
- `insufficient_evidence_for_causal_structure`
- `blocked_by_unresolved_identity_rule`
- `blocked_by_unresolved_transition_rule`

The expected 07-04 derivation is: C1-C5 pass, C6 is not evaluable from current outputs, C7 passes only at reduced-model level, and C8 passes with explicit limitations. Under the registry rule this yields `controlled_causal_structure_candidate`.

## Unit and Dimension Discipline

Cycle counts are counts with dimension vector `[0,0,0,0,0,0,0]`. Phase labels are categorical. Sequence positions are ordinal. Model time is `model_unit_unmapped`. The mean cycle duration `20.9` is not converted to seconds. The state-vector distance threshold `0.08` is not declared dimensionless without evidence and remains not empirically calibrated.

## Required Runner

```bash
.venv/bin/python \
  scripts/run_qsb_causality07_04_controlled_causal_structure.py \
  --input-root . \
  --output-dir runs/QSB-CAUSALITY07-04/controlled_causal_structure \
  --overwrite
```

The runner writes exactly ten files to the output directory and supports `--help`.

## Contribution to QSB

This block contributes a controlled audit pattern for separating recurrence, admissible ordered progression, control selectivity, and formal causal interpretation inside a reduced model. It does not prove the QSB interface layer, spacetime emergence, Lorentz compatibility, complete physical causality, or QM/GR unification.

## Unresolved Limits

- The phase sequence is predefined.
- No independent global order reconstruction is established.
- The threshold is heuristic and not empirically calibrated.
- The outputs are reduced-model outputs rather than laboratory measurements.
- The predecessor counterfactuals are structural tests rather than interventions.
- Recurrence is not complete chemical identity.
- Bounded perturbation robustness is not evaluable unless explicit perturbation outputs exist.
- No emergent-time claim is made.
- No full physical-causality claim is made.
- No universal-applicability claim is made.

## Tau and Emergent-Time Boundary

The symbol or concept of `tau` and any emergent-time interpretation remain outside this block. The runner treats duration as model time only and performs no physical time mapping.
