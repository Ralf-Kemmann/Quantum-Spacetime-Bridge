# QSB-CAUSALITY07-04A Final Result Note

## Befund

QSB-CAUSALITY07-04A evaluates whether the 07-04 transition and predecessor structure can be reconstructed from reduced state data without using phase labels, predefined cycle order, or the registered transition set as reconstruction inputs.

The runner creates a label-blind five-candidate state representation from IQR-normalized `x_activator` and `z_oxidized_catalyst` values. It scores directed candidate pairs by transition-frequency support and derivative alignment, ranks predecessors, reconstructs a directed graph, and compares the recovered cycle with the known phase sequence only after reconstruction.

## Interpretation

The method is a structural reconstruction test. It is stronger than 07-04 rule lookup because it ranks predecessor candidates from state-space and local-dynamic information before known predecessor labels are attached. It remains weaker than a laboratory intervention because no experimental manipulation is performed.

Expected result class from the runner is:

```text
independent_transition_and_predecessor_reconstruction_supported
```

This means independent support within the reduced CAUSALITY07 model domain, not full physical causality.

## Hypothese

The reduced model trajectory contains enough local state-space structure to recover the registered transition cycle after label-blind reconstruction. If future data, perturbation runs, or experimental observations break this reconstruction, the class must be reduced.

## Offene Luecke

- The data are reduced model outputs, not an independent experimental dataset.
- No laboratory intervention is performed.
- The state-space metric is conventional and heuristic.
- Score calibration is not empirical.
- Model-time units remain unmapped.
- The posthoc evaluation still uses known phase labels after reconstruction.
- Physical causality, emergent time, universal applicability, and complete chemical identity are not established.

## Claim Boundary

This block reports independent reduced-model support for transition and predecessor reconstruction only. It does not claim physical causality, emergent time, irreversible temporal direction, proof of the QSB interface layer, or QM/GR unification.
