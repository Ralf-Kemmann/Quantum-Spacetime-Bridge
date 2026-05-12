# QSB-BRIDGE-NUM-05B Phase / Gauge / Flux Stress Test Spec

## 1. Purpose

QSB-BRIDGE-NUM-05B tests phase-sensitive structure in a synthetic toy setting. It separates gauge-equivalent phase changes from loop-flux / non-gauge phase structure and records how a magnetic/Hermitian Laplacian responds.

This block is method-level only. It does not claim real quantum dynamics or physical validation.

## 2. Phase Families

All families share one fixed magnitude matrix `|K_ij|`. Only `phi_ij` changes.

```text
phase_zero_reference
global_phase_transformation
local_gauge_transformation_theta_i_minus_theta_j
random_low_amplitude_phase_noise
random_high_amplitude_phase_noise
correlated_phase_field
loop_flux_vortex_like_phase_family
adversarial_high_frequency_phase_family
```

Hermiticity is enforced by:

```text
K_ji = conjugate(K_ij)
phi_ji = -phi_ij
```

## 3. Gauge / Flux Separation

Gauge-equivalent phases have the form:

```text
phi_ij = theta_i - theta_j
```

Their loop closure around any triangle should be zero modulo `2*pi`.

Loop-flux / non-gauge families are expected to produce nonzero gauge-invariant loop closure:

```text
flux_ijk = angle(exp(i * (phi_ij + phi_jk + phi_ki)))
```

Failure to distinguish gauge-equivalent and loop-flux cases is a possible negative finding.

## 4. Diagnostics

Magnitude-only diagnostics:

```text
magnitude_distance_invariance
threshold_graph_invariance
```

Phase and gauge diagnostics:

```text
phase_diagnostic_response
gauge_invariant_loop_flux
gauge_variant_phase_score
distinction between gauge-equivalent and non-gauge-equivalent phase families
```

Magnetic/Hermitian Laplacian diagnostics:

```text
magnetic_or_hermitian_laplacian_spectrum_summary
low_eigenvalue_shift_vs_phase_zero
spectral_gap_shift
phase_noise_breakdown_curve
```

## 5. Outputs

Static files:

```text
docs/QSB_BRIDGE_NUM_05B_PHASE_GAUGE_FLUX_STRESS_TEST_SPEC.md
data/qsb_bridge_num_05b_phase_gauge_flux_config.yaml
scripts/run_qsb_bridge_num_05b_phase_gauge_flux_stress_test.py
docs/QSB_BRIDGE_NUM_05B_RESULT_NOTE.md
```

Run artifacts:

```text
runs/QSB-BRIDGE-NUM-05B/phase_gauge_flux_stress_test_open/summary.json
runs/QSB-BRIDGE-NUM-05B/phase_gauge_flux_stress_test_open/readout.md
runs/QSB-BRIDGE-NUM-05B/phase_gauge_flux_stress_test_open/phase_family_summary.csv
runs/QSB-BRIDGE-NUM-05B/phase_gauge_flux_stress_test_open/gauge_flux_summary.csv
runs/QSB-BRIDGE-NUM-05B/phase_gauge_flux_stress_test_open/laplacian_spectrum_summary.csv
runs/QSB-BRIDGE-NUM-05B/phase_gauge_flux_stress_test_open/phase_noise_sweep_summary.csv
runs/QSB-BRIDGE-NUM-05B/phase_gauge_flux_stress_test_open/resolved_config.json
```

## 6. Claim Boundary

05B is a toy stress test. It does not show physical validation, spacetime emergence, physical metric recovery, causal structure, physical geometry reconstruction, or de-Broglie confirmation.

Phase diagnostics in this block are toy diagnostics. They are not real quantum dynamics.
