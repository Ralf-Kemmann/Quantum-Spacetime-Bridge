# QSB-OUTREACH01A-06 - Synthetic Demonstrator Runner Spec

## Purpose

This runner implements a small reproducible synthetic demonstrator for the OUTREACH01A descriptor, event-instance, pair-similarity, and lag-profile logic.

It does not use real laser data and does not evaluate whether a physical system is a discrete time crystal.

## Case ID Synchronization

The case definition uses earlier compact IDs. The runner uses those canonical IDs and documents the prompt mapping:

| Prompt ID | Runner ID | Meaning |
| --- | --- | --- |
| `T_PERIODIC_CONTROL` | `T_CONTROL` | stable forcing-period response |
| `TWO_T_PERIODIC` | `T2_STABLE` | stable alternating 2T response |
| `TWO_T_NOISY_STABLE` | `T2_NOISY` | noisy but class-stable 2T response |
| `DRIFT_CONTROL` | `DRIFT_CONTROL` | smooth drift without stable alternating class |
| `MISSING_OBSERVATIONS` | `MISSING_OBSERVATIONS` | omitted observations retained as missing markers |
| `FALSE_RECURRENCE_CONTROL` | `FALSE_RECURRENCE_CONTROL` | local similarities without robust lag structure |

## Descriptor And Instance Model

The runner writes one row per event instance:

```text
X_k = (O_k, phi_k, r_k, h_k)
E_k = (e_k, c_k, X_k)
```

`event_instance_id` identifies the historical event instance. `state_descriptor_id` identifies the descriptor class assigned by the synthetic generator. Repeated descriptors do not imply repeated event instances.

## Similarity

The minimal similarity is symmetric and uses only declared numeric descriptor features:

```text
K_ij = sum_m w_m * kappa_m(x_i^(m), x_j^(m))
```

Hardening decision: the runner uses stroboscopic sampling. All synthetic states are sampled at the same forcing-phase reference point, so `forcing_phase = 0.0` is retained as metadata only. It is not a discriminating similarity feature.

The current implementation uses only observable-value similarity:

```json
{"observable_value": 1.0}
```

`forcing_phase`, `response_phase_class`, `observable_recurrence_class`, `state_descriptor_id`, and control roles are not used as similarity inputs. Response class labels are generated for inspection only.

Pairs are stored only once using canonical ID order:

```text
state_i_id < state_j_id
```

Self-pairs and mirror duplicates are invalid.

## Lag Profile

For configured lags:

```text
R(q) = median_{i in I_q} K_(i,i+q)
```

`I_q` excludes missing observations and pairs absent from the relational-pair table. Window-level checks use the same lag relation inside configured sliding windows.

Thresholds such as `minimal_lag_difference` and `minimal_stable_window_fraction` are demonstrator parameters only. They are not physical constants.

## Generic Detection And Control Interpretation

The runner separates generic detection from synthetic-control interpretation.

Generic detection statuses:

- `t_like_recurrence_supported`
- `two_t_like_recurrence_supported`
- `two_t_like_recurrence_partly_supported`
- `non_two_t_pattern`
- `data_quality_inconclusive`
- `inconclusive`

Control interpretation is then derived by comparing the generic status with each case's declared `case_role`, `expected_detection_family`, and `expected_control_outcome`. The generic detector does not branch on `case_id`.

The detector receives only calculated metrics and threshold configuration. Synthetic case identifiers and control roles are evaluated only after generic detection.

For T-like recurrence, high lag-1 similarity is not sufficient. The detector also requires no robust lag-2 dominance and limited decay across higher lags, so a smooth drift is not automatically classified as T-like.

The run validator checks the `detect_status_from_metrics(metrics, config)` function signature and fails if fallbezogene parameters such as `case_id`, `case_role`, `expected_detection_family`, or `control_interpretation` are introduced.

## Outputs

The runner writes:

- `resolved_config.json`
- `synthetic_states.csv`
- `relational_pairs.csv`
- `lag_profile.csv`
- `case_summary.csv`
- `status_summary.csv`
- `summary.json`
- `readout.md`

No database file is created.

## Claim Boundary

The demonstrator is a method test for state-description recurrence, historical instance separation, symmetric pair construction, and robust lag summaries. It is not evidence for a physical time crystal, fundamental time discreteness, ART/QM structure, gravitation, or QSB validation.
