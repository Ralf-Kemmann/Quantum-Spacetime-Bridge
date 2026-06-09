# QSB-OUTREACH01A-06 Synthetic Demonstrator Result Note

## Befund

The synthetic demonstrator runner was implemented and executed with:

- config: `data/QSB-OUTREACH01A/synthetic_demonstrator_config.yaml`
- output directory: `runs/QSB-OUTREACH01A/synthetic_demonstrator_v1/`
- random seed: `20260609`
- config hash: `6e9141d2b5c459698403d6e2a3020369b28f36f7a361e0b2f89218e2e263931c`

Generated output files:

- `resolved_config.json`
- `synthetic_states.csv`
- `relational_pairs.csv`
- `lag_profile.csv`
- `case_summary.csv`
- `status_summary.csv`
- `summary.json`
- `readout.md`

The hardened run emitted 240 synthetic state/event records, 4396 canonical relational pairs, and 24 lag-profile rows across 6 cases.

## Similarity Correction

The earlier runner used:

```text
forcing_phase = 2.0 * pi * (index % 1)
```

For integer indices this is always `0.0`, so forcing-phase similarity was always `1.0`. The configured phase weight therefore acted only as a constant offset.

The hardened runner chooses the stroboscopic minimal variant:

- `forcing_phase = 0.0` is retained as reference metadata.
- `forcing_phase` is excluded from `K_ij`.
- `K_ij` uses only `observable_value`.
- `response_phase_class`, `observable_recurrence_class`, `state_descriptor_id`, and control roles are excluded from similarity input.

## Expected Structure

The runner implements the OUTREACH01A separation:

```text
X_k = (O_k, phi_k, r_k, h_k)
E_k = (e_k, c_k, X_k)
```

The synthetic state table includes `event_instance_id`, `state_descriptor_id`, cycle index, forcing phase, response phase class, observable vector JSON, background JSON, history representation JSON, source lineage fields, seed, and transformation version.

Pair rows use symmetric canonical ordering:

```text
state_i_id < state_j_id
```

Self-pairs and mirror duplicates are not part of the emitted pair table.

## Observed Synthetic Output

Observed generic detection and control interpretation:

| Case | Generic detection | Control role | Control interpretation |
| --- | --- | --- | --- |
| `T_CONTROL` | `t_like_recurrence_supported` | `t_periodic_control` | `control_pass` |
| `T2_STABLE` | `two_t_like_recurrence_supported` | `two_t_positive_control` | `control_pass` |
| `T2_NOISY` | `two_t_like_recurrence_supported` | `two_t_noisy_positive_control` | `control_pass` |
| `DRIFT_CONTROL` | `non_two_t_pattern` | `drift_control` | `control_pass` |
| `MISSING_OBSERVATIONS` | `two_t_like_recurrence_supported` | `missing_observation_control` | `control_pass_with_missing_data_warning` |
| `FALSE_RECURRENCE_CONTROL` | `non_two_t_pattern` | `false_recurrence_control` | `control_pass` |

Selected lag outcomes:

- `T2_STABLE`: lag-1 median `0.5`, lag-2 median `1.0`, lag-2 minus lag-1 `0.5`.
- `T2_NOISY`: lag-1 median `0.5092027022`, lag-2 median `0.9749446807`, lag-2 minus lag-1 `0.4657419785`.
- `DRIFT_CONTROL`: lag-2 minus lag-1 `-0.0153846154`; the generic detector found no robust 2T-like recurrence. Because the synthetic case was generated as a drift control, this counts as a passed drift-control outcome.
- `FALSE_RECURRENCE_CONTROL`: lag-2 minus lag-1 `-0.0454158811`; the generic detector found no robust 2T-like recurrence. Because the synthetic case was generated as a false-recurrence control, this counts as a passed false-recurrence-control outcome.
- `MISSING_OBSERVATIONS`: 8 missing observations were excluded from observed pair construction. The generic detector still found a 2T-like recurrence with sufficient data quality, and the control interpretation is `control_pass_with_missing_data_warning`.

The summary reports:

- `expected_status_check_passed: true`
- `validation_passed: true`
- `detector_input_independence_check_passed: true`
- `persistent_migration_executed: false`
- `real_data_used: false`
- `physics_claim_gate: closed`

## Methodischer Erfolg

The run demonstrates that the current scaffold can:

- generate deterministic synthetic event instances from a documented seed;
- keep event instances and descriptors separate;
- build only canonical symmetric pairs;
- compute lag profiles for configured lags;
- distinguish stable synthetic 2T patterns from drift and false-recurrence controls under the configured method parameters;
- retain missing observations as an uncertainty condition rather than a physical interpretation.

## Offene Luecke

- The data are synthetic.
- No real laser measurement data were used.
- No calibration against real experimental systems was performed.
- Thresholds are method parameters and are not physically calibrated.
- The runner is a minimal demonstrator and not a production DWH ingest pipeline.

## Claim Boundary

This result is a methodological scaffold test only. It does not validate QSB, does not establish a discrete time crystal, does not claim fundamental discreteness of time, and does not make claims about ART, QM, gravitation, emergent spacetime, or physical dynamics.
