# QSB-BRIDGE-DATA-02C Run Readout

## Run

```text
block_id: QSB-BRIDGE-DATA-02C
run_id: control_ensembles_open
fixed_seed: 20260514
stop_go_outcome: go_control_ensembles_generated_with_deterministic_seed
external_data_downloaded: false
control_count: 32
```

## Claim Boundary

DATA-02C is a synthetic/reference-style control ensemble only.

It is not real-data validation, molecular validation, or physical validation.

## Highest-Risk Mimic Control

```text
highest_risk_mimic_control: {'control_id': 'within_system_label_shuffle__ethyne', 'source_system_id': 'ethyne', 'control_family_id': 'within_system_label_shuffle', 'organization_coherence_score': 1.0, 'original_control_coherence_contrast': 0.0}
lowest_original_control_coherence_contrast: {'control_id': 'within_system_label_shuffle__adamantane', 'source_system_id': 'adamantane', 'control_family_id': 'within_system_label_shuffle', 'organization_coherence_score': 1.0, 'original_control_coherence_contrast': 0.0}
possible_negative_finding_present: True
```

Successful controls are treated as possible negative findings if they mimic or erase the original organization too easily.

## Control Families

|control_family_id|control_count|control_distinction|destruction_target|
|---|---|---|---|
|hybridization_label_shuffle_control|4|label_only_destruction|hybridization_label_coherence|
|bond_order_shuffle_control|4|bond_organization_mismatch|bond_order_label_coherence|
|sigma_pi_label_shuffle_control|4|sigma_pi_organization_mismatch|sigma_pi_label_coherence|
|topology_matched_random_control|4|topology_only_destruction|connectivity_and_topology_class|
|carbon_skeleton_degree_control|4|degree_preserving_topology_randomization|higher_order_connectivity|
|within_system_label_shuffle|4|label_only_destruction|node_edge_label_alignment|
|cross_system_label_swap|4|bond_organization_mismatch|system_label_coherence|
|topology_preserving_label_randomization|4|label_only_destruction|hybridization_bond_sigma_pi_label_coherence|

## 05C Warning Carried Forward

local-neighborhood sensitivity under small additive magnitude noise at 0.02

## Future Result Discussion Requirement

Create a separate DATA-02C result discussion after reading outputs; include a human-readable Bauchbild and keep all interpretation control-ensemble-only.
