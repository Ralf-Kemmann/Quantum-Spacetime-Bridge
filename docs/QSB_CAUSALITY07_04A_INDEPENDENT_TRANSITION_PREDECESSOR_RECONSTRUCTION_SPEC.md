# QSB-CAUSALITY07-04A Independent Transition and Predecessor Reconstruction Spec

## Status and Scope

```text
block_id = QSB-CAUSALITY07-04A
input_blocks = QSB-CAUSALITY07-01,QSB-CAUSALITY07-02,QSB-CAUSALITY07-03,QSB-CAUSALITY07-04
block_type = independent_transition_predecessor_reconstruction
physical_causality_claimed = no
emergent_time_claimed = no
```

QSB-CAUSALITY07-04 established internal rule consistency for directed transitions and predecessor dependence. The remaining concern is circularity: C2 and C3 used a registered transition set and canonical predecessor relation that were derived from the same baseline cycle vocabulary.

This block therefore tests whether transition structure can be reconstructed from reduced state data and local dynamics without using phase labels, predefined cycle order, or the registered 07-04 transition rules as reconstruction inputs.

## Independent Reconstruction Standard

Independent reconstruction means that the scoring inputs are limited to reduced state vectors, local derivative fields, explicit model-time coordinates, and post-transient selection. The following are excluded from reconstruction:

- phase labels
- predefined cycle order
- registered allowed-transition set
- canonical predecessor identity
- cycle index
- cycle-position labels
- filenames as semantic inputs
- work-package metadata as scoring inputs

Known labels and known predecessors may be added only after reconstruction for evaluation.

## Method

The runner uses a simple inspectable method:

1. IQR-normalize the reduced `x_activator` and `z_oxidized_catalyst` state-space projection.
2. Compute a label-blind angular coordinate in the normalized `x,z` plane.
3. Split the observed angular support into five deterministic candidate sectors.
4. Sort observations by explicit model-time coordinate, not by implicit row order.
5. Count candidate-to-candidate transitions between successive candidate sectors.
6. Score every ordered non-self candidate pair.
7. Rank candidate predecessors for every target.
8. Build a directed graph from highest-scoring reconstructed outgoing edges.
9. Attempt global cycle reconstruction.
10. Compare with the known phase cycle only after reconstruction.

## Score Formula

For each ordered pair:

```text
S_i_to_j = 0.7 * temporal_transition_frequency_score
         + 0.3 * derivative_alignment_score
```

The transition-frequency component is the observed candidate transition count divided by the maximum observed candidate transition count. The derivative-alignment component is `0.5 * (1 + cosine(mean_derivative_source, centroid_target - centroid_source))`.

Both components are normalized before addition. The resulting score is a unitless normalized score and dimensionless after documented normalization. The score calibration is heuristic, not empirically calibrated.

## Direction Reconstruction

For each pair `i -> j`, the runner computes the forward score, reverse score, direction margin, and direction class. Forward direction is supported only when the forward score exceeds the reverse score by the explicit margin threshold.

## Predecessor Ranking

For each target candidate, all non-self candidate predecessors are ranked by score. The known predecessor is attached only after ranking. Reported metrics include top-1 recovery, top-2 recovery, mean reciprocal rank, median rank, ambiguity count, and unresolved count.

## Cycle Recovery

The reconstructed directed graph is built from scored edges only. The known sequence:

```text
P0 -> P1 -> P2 -> P3 -> P4 -> P0
```

is used only for posthoc comparison. Exact recovery supports independent reduced-model transition reconstruction; it does not prove physical causality.

## Leakage and Ablation Controls

Label permutation must not change the reconstruction. Row shuffle must not change the reconstruction because explicit model time is used for ordering. Edge removal, false-edge insertion, predecessor swap, direction-information removal, and bounded score perturbation are deterministic falsification controls.

## Unit and Dimension Discipline

State-vector components retain their source status. Model time remains `model_unit_unmapped` and is not converted to seconds. Scores are dimensionless only after documented normalization. Ranks are ordinal and dimensionless. Counts are dimensionless counts. The 07-03 threshold `0.08` is not used as a 04A score threshold and is not declared dimensionless.

## Claim Boundary

This block may support independent reduced-model transition and predecessor reconstruction. It does not establish laboratory intervention validity, full physical causality, emergent time, universal applicability, complete chemical identity, or proof of a QSB interface layer.
