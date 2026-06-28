# QSB-CAUSALITY07-04 Final Result Note

## Befund

QSB-CAUSALITY07-04 evaluates the minimal conditions for a controlled causal-structure candidate using the existing CAUSALITY07-01, 07-02, and 07-03 artifacts. The baseline sequence remains predefined:

```text
P0 -> P1 -> P2 -> P3 -> P4 -> P0
```

The 07-03 basis reports 10 complete baseline cycles, a mean cycle duration of 20.9 model-time units, 0 reverse-control cycles, and 0 scrambled-control cycles. The sequence source is `predefined_phase_sequence`. The global order is not independently reconstructed.

The 07-04 runner evaluates C1-C8 and writes directed-transition, predecessor-counterfactual, permutation-control, condition, evidence, summary, validation, JSON, and readout outputs to:

```text
runs/QSB-CAUSALITY07-04/controlled_causal_structure/
```

## Interpretation

C1-C5 pass in the reduced-model formal evaluation:

- the five assigned phase labels are distinct reduced-model working aliases;
- baseline transitions are represented in the explicit allowed transition set;
- target-state interpretation is predecessor-context dependent;
- tested reverse, scrambled, and deterministic permutation controls are rejected;
- recurrence is control-sensitive in the 07-03 baseline-versus-controls sense.

C6 is `not_evaluable_from_current_outputs` because no bounded perturbation output is present. C7 passes only for assigned-phase recurrence and reduced-state proximity under the documented threshold. C8 passes as a formal gate with the limitations retained.

The composite class is:

```text
controlled_causal_structure_candidate
```

This means a formally explicit, controlled, and falsifiable candidate structure for causal ordering within the CAUSALITY07 model domain.

## Hypothese

The result supports the hypothesis that the CAUSALITY07 reduced-model artifact can be organized as an ordered recurrence with explicit transition admissibility, structural predecessor dependence, and control selectivity. It does not establish that the model implements complete physical causality.

## Offene Luecke

- The sequence remains predefined.
- No independent global order reconstruction is established.
- The state-vector distance threshold `0.08` remains heuristic and not empirically calibrated.
- The threshold is not declared dimensionless here.
- The mean duration `20.9` remains model time and is not mapped to seconds.
- The outputs are reduced-model outputs, not laboratory measurements.
- The predecessor matrix is a structural counterfactual test, not an intervention.
- Bounded perturbation robustness is not evaluable from current outputs.
- Recurrence does not establish complete chemical identity or full physical-state identity.

## Claim Boundary

This block does not claim complete physical causality, emergent time, irreversible temporal direction, chemical identity from recurrence, a universal causal law, proof of the QSB interface layer, or proof of QM/GR unification. It also does not infer `tau` or a physical time mapping.

Final status:

```text
controlled_causal_structure_evaluation_completed_with_review_items
```
