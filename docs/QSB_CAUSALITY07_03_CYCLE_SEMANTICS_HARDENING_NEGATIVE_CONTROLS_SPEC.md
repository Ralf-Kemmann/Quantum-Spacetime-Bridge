# QSB-CAUSALITY07-03 Cycle Semantics Hardening and Negative Controls Spec

## Status and Scope

```text
block_id = QSB-CAUSALITY07-03
input_run_id = QSB-CAUSALITY07-02
block_type = cycle_semantics_hardening
physical_causality_claimed = no
emergent_time_claimed = no
experimental_data_used = no
complete_state_reset_established = no
```

This block audits the existing QSB-CAUSALITY07-02 reduced Oregonator output. It does not rerun QSB-CAUSALITY06, does not overwrite the 07-02 run, and does not introduce a new physical model. The input is the 07-02 classified phase series and summary outputs.

## Predefined Baseline Sequence

The expected baseline sequence is predefined:

```text
P0 -> P1 -> P2 -> P3 -> P4 -> P0
```

The runner checks whether this sequence occurs completely in the classified time series.

```text
cycle_sequence_source = predefined_phase_sequence
global_cycle_order_independently_reconstructed = no
time_order_used_to_orient_phase_labels = yes
phase_labels_are_model_relative = yes
```

The block must not describe the result as independent cycle discovery, independent reconstruction of global direction, a causal cycle, or emergent time order.

## Explicit Distance Threshold

The 07-03 runner uses an explicit threshold:

```text
state_vector_distance_threshold = 0.08
state_vector_distance_threshold_basis = heuristic_reuse_of_existing_07_02_threshold
distance_threshold_explicit = yes
distance_threshold_empirically_calibrated = no
similarity_function_defined = no
```

The threshold is a heuristic reuse of the 07-02 normalized distance boundary. The runner does not define or validate a mathematical similarity function from this distance.

## Terminology Corrections

The 07-03 outputs do not use the prior 07-02 phase-identity result label. The corresponding 07-03 field is:

```text
same_assigned_phase_label = yes|no
phase_identity_independently_established = no
```

The 07-03 outputs do not use the prior 07-02 resource-indicator result label. The corresponding 07-03 field is:

```text
reduced_state_drift_proxy
real_resource_exhaustion_modelled = no
resource_inventory_reconstructed = no
reduced_state_drift_proxy_used = yes
```

The drift proxy is an indicator of small displacement in the reduced model state, not a real resource inventory.

## Recurrence and Non-Identity

For each complete baseline cycle, the runner records:

```text
cycle_index
p0_time
p0_prime_time
cycle_duration
same_assigned_phase_label
state_vector_distance
state_vector_distance_within_threshold
reduced_state_drift_proxy
recurrent_state_region_detected
complete_state_reset_established
```

Expected interpretation:

```text
recurrent_state_region_detected = yes
complete_state_reset_established = no
```

Reduced-model near recurrence is not a whole-chemistry restart.

## Negative Controls

The reverse control sequence is:

```text
P0 -> P4 -> P3 -> P2 -> P1 -> P0
```

The scrambled control sequence is:

```text
P0 -> P1 -> P3 -> P2 -> P4 -> P0
```

Both controls are evaluated against the same classified 07-02 time series. Passing controls mean only that the detector does not accept these two arbitrary phase orders as complete cycles.

```text
physical_direction_validated = no
arbitrary_sequence_acceptance_detected = no
```

## Required Outputs

The runner writes exactly ten files to:

```text
runs/QSB-CAUSALITY07-03/cycle_semantics_hardening/
```

Required files:

```text
resolved_hardening_config.json
baseline_cycle_semantics.csv
reverse_sequence_control.csv
scrambled_sequence_control.csv
recurrence_identity_comparison.csv
phase_duration_summary.csv
semantic_validation_checks.csv
phase_progression_over_cycles.svg
run_summary.json
readout.md
```

The positive final status is permitted only if all required semantic validation checks pass.

## Claim Boundary

This block may establish that the predefined baseline sequence is found in the classified 07-02 model series and that the two negative controls do not close under the same detector. It does not establish laboratory validation, complete chemical state identity, real resource exhaustion, physical causality, an emergent-time claim, or a general statement about all oscillating reaction systems.
