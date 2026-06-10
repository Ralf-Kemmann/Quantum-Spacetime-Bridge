# QSB-CAUSALITY07-02 — First Oscillatory State-Cycle Data and Runner Spec

## 1. Status and Scope

```text
block_id = QSB-CAUSALITY07-02
block_type = data_and_runner
data_status = reproducible_model_generated_oregonator_time_series
raw_experimental_measurement_data = false
directly_observed_lab_trajectory = false
full_FKN_mechanism_simulated = false
reduced_model_used = Oregonator
physical_causality_claimed = false
closed_causal_loop_claimed = false
phase_classification_mode = heuristic_state_space_sector_classification
chemical_phase_identity_validated = false
phase_labels_are_functional_working_aliases = true
reference_cycle_order_used_for_cycle_segmentation = true
independent_cycle_order_reconstruction_performed = false
cycle_detection_scope = reference_sequence_conditioned
```

This block creates a first reproducible model-generated time series for a homogeneous temporal Oregonator. It does not use laboratory measurements, spatial waves, diffusion, convection, or reaction-diffusion analysis.

## 2. Model-Generated Data

The runner uses the dimensionless three-variable Oregonator:

```text
dx/dtau = (q*y - x*y + x*(1 - x)) / epsilon
dy/dtau = (-q*y - x*y + f*z) / delta
dz/dtau = x - z
```

Variable roles are neutral model roles:

```text
x = activator_related_dimensionless_variable
y = inhibitor_related_dimensionless_variable
z = oxidized_catalyst_related_dimensionless_variable
```

The configured parameters are `epsilon = 0.01`, `delta = 0.01`, `q = 0.0008`, and `f = 0.8`, with initial state `(x, y, z) = (0.2, 0.1, 0.1)`. These variables are reduced-model coordinates, not exact complete FKN species concentrations.

## 3. Phase Classification

Five functional regions are assigned as heuristic working aliases to sectors of the reduced model trajectory:

```text
BZ01_P0 = bromide_inhibited_region
BZ01_P1 = inhibitor_depletion_and_activation_region
BZ01_P2 = autocatalytic_oxidation_region
BZ01_P3 = oxidized_catalyst_and_recovery_region
BZ01_P4 = inhibitor_regeneration_region
```

The five phase labels are functional working aliases assigned to heuristic sectors of the scaled x-z model state space. They are not independently validated chemical phase identities, not direct species measurements, and not automatically identical with fully separated FKN mechanism phases.

The active phase-classification feature set is exactly:

```text
phase_classification_feature_set =
[
  robust_scaled_x,
  robust_scaled_z,
  state_space_angle_xz,
  local_x_minimum_angle_anchor
]
```

Available output fields that are not used for phase classification are:

```text
unused_available_features_not_used_for_phase_classification =
[
  y_inhibitor,
  dx_dt,
  dy_dt,
  dz_dt
]
```

The rules do not use fixed time windows, cycle index, or reference order as phase truth.

## 4. Local Transitions

Local phase changes are read from consecutive stable phase regions after classification. Transition rows record observed source and target phase regions, timing, local signatures, and explicit guard fields:

```text
reference_cycle_order_used_as_direction_input = false
reference_cycle_order_used_for_cycle_segmentation = true
independent_cycle_order_reconstruction_performed = false
cycle_detection_scope = reference_sequence_conditioned
phase_labels_used_as_direction_input = false
cycle_index_used_as_direction_input = false
local_transition_direction_observed_from_time_order = true
global_cycle_order_independently_reconstructed = false
```

No causal class is assigned.

## 5. Cycle Recurrence

A cycle is counted when the stable sequence returns from a `BZ01_P0` region through `BZ01_P1`, `BZ01_P2`, `BZ01_P3`, and `BZ01_P4` to a later `BZ01_P0`-like region. The reference sequence is not used as local direction input, but it is used to define a complete cycle in this first controlled run. Ten complete cycles were detected under the declared reference-sequence segmentation rule. Observable recurrence, model-state near recurrence, and full chemical-state identity are reported separately.

```text
reference_cycle_order_used_for_cycle_segmentation = true
independent_cycle_order_reconstruction_performed = false
cycle_detection_scope = reference_sequence_conditioned
full_chemical_state_identity_established = false
```

## 6. P0 versus P0 Prime

For each complete cycle, the runner compares the starting `BZ01_P0` sample with the later recurrent `BZ01_P0_prime` sample. It reports observable-marker difference, robustly scaled model-state distance, phase identity, resource-proxy difference, and the fixed boundaries:

```text
same_observable_marker_implies_same_full_state = false
cycle_recurrence_implies_state_reset = false
```

The model-state distance is a reduced-model diagnostic, not a complete chemical-state distance.

The normalized model-state distance threshold is derived from the configured state-vector similarity threshold:

```text
normalized_state_distance_threshold = 1.0 - state_vector_similarity_threshold
```

## 7. Outputs

The runner writes exactly ten files under `runs/QSB-CAUSALITY07-02/first_oscillatory_state_cycle/`:

```text
resolved_config.json
oregonator_time_series.csv
classified_phase_series.csv
local_transition_results.csv
cycle_recurrence_results.csv
p0_vs_p0_prime_comparison.csv
german_alias_view.csv
run_summary.json
readout.md
phase_detection_diagnostics.json
```

## 8. Limitations

- The time series is reproducibly generated from a reduced Oregonator model and is not raw lab measurement data.
- The Oregonator is not the complete FKN mechanism.
- The five phase labels are heuristic functional working aliases assigned to sectors of the reduced model state space.
- Chemical phase identity is not independently validated.
- Cycle segmentation is conditioned on the declared reference phase sequence.
- Independent cycle-order reconstruction is not performed.
- Observable or model-state recurrence does not establish full chemical-state identity.
- Resource depletion of a real batch reaction is not explicitly modeled.
- Local directed transitions within the classified sequence do not establish physical causality.
- No reaction-diffusion, spatial-wave, or convection analysis is performed.
- Localized aliases are presentation metadata only.
