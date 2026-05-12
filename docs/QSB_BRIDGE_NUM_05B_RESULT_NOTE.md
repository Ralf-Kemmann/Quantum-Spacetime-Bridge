# QSB-BRIDGE-NUM-05B Result Note

## 1. Purpose

QSB-BRIDGE-NUM-05B tests synthetic phase, gauge, and loop-flux families on one fixed magnitude matrix. It is a method-level toy stress test.

## Human-readable Interpretation / Bauchbild

A global phase is like changing the overall phase convention of the whole toy system. In this run it cancels from pairwise phase differences, so it should not create loop flux.

A local gauge phase assigns a phase label `theta_i` to each node and uses only differences `theta_i - theta_j`. Individual edges can look phase-shifted, but closed loops cancel. That is why local gauge phase can have a nonzero gauge-variant phase score while still carrying near-zero loop flux.

Loop flux is different. It is what remains when phases are summed around a closed triangle. If that loop sum does not cancel, the phase pattern is not just a relabeling of node phases in this toy diagnostic.

Confusing gauge with flux would be a negative finding. It would mean the diagnostic cannot tell a harmless phase convention from a loop-sensitive phase structure.

The magnetic/Hermitian Laplacian adds a method-level spectral readout: it keeps the complex edge phases instead of discarding them. It is useful here because gauge-equivalent cases should be spectrally close to the zero-phase case, while non-gauge flux cases can shift low eigenvalues or the spectral gap.

This remains non-physical and toy-level. The phase diagnostics are not real quantum dynamics, and the spectral shifts are not evidence for physical geometry or de-Broglie physics.


## 2. Result

```text
gauge_flux_distinction_passed: True
magnitude_distance_invariance_all_passed: True
threshold_graph_invariance_all_passed: True
max_low_eigenvalue_shift_non_gauge: 1.2311280991
stop_go_outcome: go_with_documented_boundaries
```

## 3. Phase Families

|phase_family_id|expected_gauge_equivalent|observed_gauge_equivalent|gauge_invariant_loop_flux_rms|low_eigenvalue_shift_vs_phase_zero|
|---|---|---|---|---|
|phase_zero_reference|True|True|0.0|0.0|
|global_phase_transformation|True|True|0.0|0.0|
|local_gauge_transformation_theta_i_minus_theta_j|True|True|0.0|0.0|
|random_low_amplitude_phase_noise|False|False|0.32853906978|0.091559997093|
|random_high_amplitude_phase_noise|False|False|1.859920324653|1.111093568921|
|correlated_phase_field|True|True|0.0|0.0|
|loop_flux_vortex_like_phase_family|False|False|0.886048626357|0.622775303584|
|adversarial_high_frequency_phase_family|False|False|1.774006064496|1.2311280991|

## 4. Interpretation

Gauge-equivalent phase changes are expected to cancel on closed loops. Loop-flux and adversarial non-gauge families are expected to produce nonzero loop closure and spectral response. Failure to separate those cases would be a negative method-level finding.

## 5. Claim Boundary

05B does not physically validate QSB. It does not show spacetime emergence, physical metric recovery, causal structure, physical geometry reconstruction, de-Broglie confirmation, or real quantum dynamics.
