# QSB-CAUSALITY07-03 Final Result Note

## Research Question

QSB-CAUSALITY07-03 asks whether the existing 07-02 reduced Oregonator model output can be closed with stricter cycle semantics: predefined sequence matching, recurrence, phase-label assignment, reduced-state closeness, and non-identity are treated as separate statements.

## Existing 07-02 Basis

The input is the QSB-CAUSALITY07-02 classified phase series and run summary. The 07-02 basis is a reproducible reduced Oregonator model run, not a laboratory trajectory and not a complete FKN mechanism simulation.

## Semantic Corrections

The 07-03 block treats the phase sequence as predefined:

```text
P0 -> P1 -> P2 -> P3 -> P4 -> P0
```

The global cycle order is not independently reconstructed. The assigned phase labels are model-relative working labels oriented by the time-series construction. The state-vector distance threshold is explicit:

```text
state_vector_distance_threshold = 0.08
state_vector_distance_threshold_basis = heuristic_reuse_of_existing_07_02_threshold
distance_threshold_empirically_calibrated = no
similarity_function_defined = no
```

## Baseline Result

The 07-03 runner detected 10 complete cycles for the predefined baseline sequence. The mean detected cycle duration is 20.9 model-time units. The baseline count matches the 07-02 summary and readout count.

## Negative Controls

The reverse control sequence:

```text
P0 -> P4 -> P3 -> P2 -> P1 -> P0
```

detected 0 complete cycles.

The scrambled control sequence:

```text
P0 -> P1 -> P3 -> P2 -> P4 -> P0
```

detected 0 complete cycles.

These controls show that the detector did not accept these two alternative phase orders as complete cycles in the same classified time series. They do not validate physical direction, uniqueness of the cycle order, chemical completeness, or experimental truth.

## Recurrence and Non-Identity

For all 10 detected baseline cycles, `P0_prime` remains in the same assigned phase region as `P0`. The reduced state-vector distances are within the explicit heuristic threshold of 0.08. The recorded drift is a reduced-state drift proxy, not a real resource inventory or resource-exhaustion measurement.

Recurrent state region detection is therefore separated from complete state reset:

```text
recurrent_state_region_detected = yes
complete_state_reset_established = no
phase_identity_independently_established = no
real_resource_exhaustion_modelled = no
```

## Direction and Sequence Boundary

The phase sequence was predefined and checked against the time series. The run does not claim independent reconstruction of the global cycle order. It also does not turn local phase progression into a physical causality claim.

## What Is Established

- The 07-02 model run contains a regularly recurring assigned phase sequence.
- The predefined baseline sequence is fully recovered 10 times.
- The reverse and scrambled control sequences are not accepted as complete cycles.
- `P0_prime` lies in the same assigned phase region as `P0`.
- The reduced state vector lies within the explicitly configured heuristic distance threshold.
- Recurrence, phase label, reduced-state closeness, and full identity remain separate statements.

## What Is Not Established

- No laboratory validation is established.
- No independent reconstruction of the global cycle order is established.
- No complete chemical state identity is established.
- No whole-chemistry restart is established.
- No real resource exhaustion is established.
- No physical causality is established.
- No emergent time is established.
- No general statement about all oscillating reaction systems is established.

## Relation to the QSB Interface Layer

The case shows that an interface layer can represent cyclic recurrence without merging record identity, dynamic equivalence, phase location, and full physical identity. It does not show that the Oregonator proves QSB or supports a spacetime interpretation.

## Final Status

```text
cycle_semantics_hardening_completed
```
