# QSB-OUTREACH01A-05 - Synthetic Demonstrator Case Definition

## Required Cases

- `T_CONTROL`: stable forcing-period response
- `T2_STABLE`: stable period-doubled response
- `T2_NOISY`: noisy but class-stable 2T response
- `DRIFT_CONTROL`: slow drift without stable subharmonic class
- `MISSING_OBSERVATIONS`: omitted pulses/records
- `FALSE_RECURRENCE_CONTROL`: apparent alternation without robust class structure

## Required State Records

Each demonstrator record must distinguish:

- `event_instance_id`
- `state_descriptor_id`
- `forcing_cycle_index`
- descriptor fields for observable, phase, background, and history representation

The same descriptor may recur across event instances. The same event instance must not recur.

## Required History Declaration

Each case must declare `history_representation_type` as one of:

- `none`
- `finite_history_features`
- `delay_window`
- `embedded_history_vector`

For delay-window or embedded-history cases, the demonstrator must document the window bounds and the embedding method/version if used.

## Required Outputs

- state event records
- descriptor records or descriptor identifiers
- pairwise relational table using symmetric canonical pair order
- lag summary table for `R(q)`
- class assignment
- parameter configuration
- sensitivity summary
- gate-compatible result note

## Robust Lag Requirement

The demonstrator should report:

```text
R(q) = median_{i in I_q} K_(i,i+q)
```

and evaluate the 2T case with documented robustness checks. Thresholds are demonstrator parameters, not physical constants.

## Success Condition

The demonstrator must expose both detection capability and failure boundaries, including drift and missing-observation controls.
