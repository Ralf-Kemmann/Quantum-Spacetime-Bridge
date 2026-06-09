# QSB-OUTREACH01A-03 - Relational State Identity Mathematical Specification

## Descriptor And Event Instance

For forcing-cycle index `k`, the minimal scaffold separates a state description from a historical event instance.

State descriptor:

```text
X_k = (O_k, phi_k, r_k, h_k)
```

Event or state instance:

```text
E_k = (e_k, c_k, X_k)
```

where:

- `e_k`: unique event or instance identifier
- `c_k`: forcing-cycle index
- `X_k`: descriptive dynamic state
- `O_k`: observable feature vector
- `phi_k`: response or subharmonic phase class
- `r_k`: relevant background or resource state
- `h_k`: declared history representation

A state description may recur; a historical event instance does not recur as the same instance.

## Distinct Relations

- observable equivalence: `X_i ~_obs X_j`
- phase equivalence: `X_i ~_phase X_j`
- state-class equivalence: `X_i ~_class X_j`
- descriptor equality: `X_i = X_j` only under an explicitly declared descriptor representation
- historical instance distinction: `E_i != E_j` for different event identifiers, even if `X_i = X_j`

These relations must not be collapsed into one undifferentiated equality.

## Background State

The background component `r_k` is represented operationally by:

- `background_state_type`
- `background_state_json`

This representation is system-dependent. In the synthetic demonstrator it is limited to declared control metadata and must not be read as a complete physical background state.

## History Representation

The history component `h_k` must declare one of the following representation types:

- `none`
- `finite_history_features`
- `delay_window`
- `embedded_history_vector`

For delay systems, the full history function can be written as:

```text
x_t(theta) = x(t + theta), theta in [-tau, 0]
```

The minimal scaffold does not require storing the full history function. It must, however, declare which representation is used through:

- `history_representation_type`
- `history_descriptor_json`
- `history_window_start`
- `history_window_end`
- `history_embedding_method`
- `history_embedding_version`

A compressed history representation must not be silently equated with the complete dynamic state.

## Relational Similarity

Pairwise descriptor similarity is defined as:

```text
K_ij = sum_m w_m * kappa_m(x_i^(m), x_j^(m))
```

Required metadata:

- feature family
- normalization rule
- kernel
- weight
- missing-value policy
- threshold or neighbour rule
- parameter version
- descriptor representation version
- history representation type

For the minimal scaffold, pairwise similarity is symmetric:

```text
K_ij = K_ji
```

Only one canonical pair order is stored. Directed relations are a possible later extension and are not part of this minimal scaffold.

## Robust Lag Signature

The earlier single comparison `K_(i,i+2) > K_(i,i+1)` is not sufficient as a standalone diagnostic. The scaffold instead defines lag summaries:

```text
R(q) = median_{i in I_q} K_(i,i+q)
```

where `I_q` is the set of valid index pairs for lag `q` after declared missing-observation and window filters.

For a stable 2T synthetic case, the expected diagnostic is:

```text
R(2) > R(1)
```

plus at least one documented robustness condition:

- stability over multiple time windows
- stability under controlled noise
- stability over an allowed threshold or kNN range
- separation from drift controls
- separation from missing-observation artifacts

No numerical threshold is asserted as a physical constant in this scaffold. Thresholds are configured demonstrator parameters until justified by a reviewed demonstrator or source-specific analysis.

## Non-Interpretation Rule

A robust 2T relational pattern alone does not establish a discrete time crystal. Classification remains dependent on established physical criteria and the source study.
