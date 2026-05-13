# QSB-BRIDGE-DATA-02A Run Readout

## Run

```text
block_id: QSB-BRIDGE-DATA-02A
run_id: sp2_contrast_scaffold_open
stop_go_outcome: go_scaffold_generated_with_exact_c60_validation
external_data_downloaded: false
```

## Claim Boundary

DATA-02A is a synthetic/reference-style scaffold only.

It is not real-data validation, physical validation, or molecular validation.

## Benzene Checks

```text
node_count: 6
edge_count: 6
degree_distribution: {2: 6}
passed: True
```

## C60 Exact Scaffold Checks

```text
node_count: 60
edge_count: 90
degree_distribution: {3: 60}
all_degrees_3: True
face_count: 32
pentagon_count: 12
hexagon_count: 20
euler_characteristic: 2
bond_class_counts: {'5_6': 60, '6_6': 30}
passed: True
```

## Proxy Risk Summary

|proxy_id|intended_use|geometry_smuggling_risk|claim_boundary|
|---|---|---|---|
|coordinate_distance_reference_kernel|reference_control_only|high|coordinate-derived kernel is not independent evidence|
|graph_distance_reference_kernel|reference_control_only|high|graph-derived kernel is not independent evidence|
|bond_class_weighted_proxy|synthetic_contrast_proxy_only|medium|bond labels are controlled scaffold labels only|
|local_environment_proxy|synthetic_local_label_proxy_only|medium_to_high|local environment labels can encode scaffold construction|
|spectral_graph_toy_proxy|toy_graph_diagnostic_only|medium|toy graph spectrum is not molecular validation|
|phase_loop_toy_proxy|toy_loop_phase_scaffold_only|medium|toy phase labels are not physical phase content|

Coordinate- and graph-derived kernels are labeled reference/control only. They are not independent evidence.

## 05C Warning Carried Forward

local-neighborhood sensitivity under small additive magnitude noise at 0.02

## Future Result Discussion Requirement

Create a separate DATA-02A result discussion only after reading these outputs. It must include a human-readable Bauchbild and remain scaffold-only, defensive, and method-level.

A useful Bauchbild: benzene is the small flat ring tile, C60 is the exact curved cage tile, and DATA-02A checks the labels and controls on the bench before any real molecular-data claim is allowed.
