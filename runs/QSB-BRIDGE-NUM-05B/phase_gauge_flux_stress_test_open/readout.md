# QSB-BRIDGE-NUM-05B Run Readout

## Run

```text
block_id: QSB-BRIDGE-NUM-05B
run_id: phase_gauge_flux_stress_test_open
phase_family_count: 8
gauge_flux_distinction_passed: True
stop_go_outcome: go_with_documented_boundaries
```

## Human-readable Interpretation / Bauchbild

A global phase is like changing the overall phase convention of the whole toy system. In this run it cancels from pairwise phase differences, so it should not create loop flux.

A local gauge phase assigns a phase label `theta_i` to each node and uses only differences `theta_i - theta_j`. Individual edges can look phase-shifted, but closed loops cancel. That is why local gauge phase can have a nonzero gauge-variant phase score while still carrying near-zero loop flux.

Loop flux is different. It is what remains when phases are summed around a closed triangle. If that loop sum does not cancel, the phase pattern is not just a relabeling of node phases in this toy diagnostic.

Confusing gauge with flux would be a negative finding. It would mean the diagnostic cannot tell a harmless phase convention from a loop-sensitive phase structure.

The magnetic/Hermitian Laplacian adds a method-level spectral readout: it keeps the complex edge phases instead of discarding them. It is useful here because gauge-equivalent cases should be spectrally close to the zero-phase case, while non-gauge flux cases can shift low eigenvalues or the spectral gap.

This remains non-physical and toy-level. The phase diagnostics are not real quantum dynamics, and the spectral shifts are not evidence for physical geometry or de-Broglie physics.


## Phase Family Summary

|phase_family_id|expected_gauge_equivalent|observed_gauge_equivalent|gauge_invariant_loop_flux_rms|gauge_variant_phase_score|phase_diagnostic_response|
|---|---|---|---|---|---|
|phase_zero_reference|True|True|0.0|0.0|0.0|
|global_phase_transformation|True|True|0.0|0.0|0.0|
|local_gauge_transformation_theta_i_minus_theta_j|True|True|0.0|1.17820073485|0.795317481773|
|random_low_amplitude_phase_noise|False|False|0.32853906978|0.17285983958|0.197369862003|
|random_high_amplitude_phase_noise|False|False|1.859920324653|1.306875715161|1.136148375922|
|correlated_phase_field|True|True|0.0|0.961880215352|0.790847915695|
|loop_flux_vortex_like_phase_family|False|False|0.886048626357|1.28519699465|0.780200485303|
|adversarial_high_frequency_phase_family|False|False|1.774006064496|1.202118932467|1.339802082741|

## Magnetic / Hermitian Laplacian Summary

|phase_family_id|spectral_gap|spectral_gap_shift|low_eigenvalue_shift_vs_phase_zero|
|---|---|---|---|
|phase_zero_reference|1.788584533772|0.0|0.0|
|global_phase_transformation|1.788584533772|0.0|0.0|
|local_gauge_transformation_theta_i_minus_theta_j|1.788584533772|0.0|0.0|
|random_low_amplitude_phase_noise|1.760866880565|-0.027717653207|0.091559997093|
|random_high_amplitude_phase_noise|1.528444321096|-0.260140212677|1.111093568921|
|correlated_phase_field|1.788584533772|0.0|0.0|
|loop_flux_vortex_like_phase_family|1.165809230189|-0.622775303584|0.622775303584|
|adversarial_high_frequency_phase_family|1.587038495197|-0.201546038575|1.2311280991|

## Main Findings

- Gauge-equivalent and loop-flux phase families are reported separately.
- Magnitude-only distance and threshold graph readouts remain invariant because |K_ij| is fixed.
- Loop-flux and adversarial phase families produce nonzero loop closure in this toy setting.
- Magnetic/Hermitian Laplacian spectra provide a phase-aware method-level readout.
- All claims remain toy-level and non-physical.

## Claim Boundary

05B is a synthetic method-level phase/gauge/flux stress test. Phase diagnostics are toy diagnostics, not real quantum dynamics. No physical validation claim follows.
