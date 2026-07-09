# Lag Projector Operator Sketch

Design placeholder:

```text
c_ij = relational cell associated with pair (i,j)
P_l  = lag-class projector or class-incidence operator for lag class l
K_lag_like = sum_l w_l P_l
```

Required alignment before future execution:

- define whether `P_l` is a true projector, incidence matrix, mask, or class kernel
- prove or reject idempotence-like behavior
- define overlap/orthogonality among classes
- define sum-over-classes behavior
- align `K_lag_like` with the documented PBR matrix construction
- predeclare rank/PSD/spectrum metrics and thresholds

Claim boundary:

`K_lag_like` is not a physical area operator and is not computed in this run.
