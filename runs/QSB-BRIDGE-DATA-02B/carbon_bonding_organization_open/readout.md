# QSB-BRIDGE-DATA-02B Run Readout

## Run

```text
block_id: QSB-BRIDGE-DATA-02B
run_id: carbon_bonding_organization_open
stop_go_outcome: go_scaffold_generated_with_carbon_skeleton_checks
external_data_downloaded: false
```

## Claim Boundary

DATA-02B is a synthetic/reference-style scaffold only.

It is not real-data validation, molecular validation, or physical validation.

## Representation

Primary graph nodes are carbon skeleton atoms only. Hydrogen and saturation are metadata, not primary graph nodes.

## System Checks

```text
ethyne: {'node_count': 2, 'edge_count': 1, 'degree_distribution': {'1': 2}, 'hybridization_counts': {'sp': 2}, 'bond_order_class_counts': {'triple': 1}, 'pi_system_label_counts': {'linear_triple_bond_pi_pair': 2}, 'sigma_framework_label_counts': {'linear_sigma_axis': 2}, 'topology_class_counts': {'linear_sp_carbon_wire': 2}, 'specific_checks': {'node_count': 2, 'edge_count': 1, 'degree_distribution': {'1': 2}, 'passed': True, 'hybridization_counts': {'sp': 2}, 'bond_order_class_counts': {'triple': 1}}}
benzene: {'node_count': 6, 'edge_count': 6, 'degree_distribution': {'2': 6}, 'hybridization_counts': {'sp2': 6}, 'bond_order_class_counts': {'aromatic': 6}, 'pi_system_label_counts': {'planar_aromatic_pi_ring': 6}, 'sigma_framework_label_counts': {'planar_ring_sigma_framework': 6}, 'topology_class_counts': {'planar_aromatic_ring': 6}}
c60: {'node_count': 60, 'edge_count': 90, 'degree_distribution': {'3': 60}, 'hybridization_counts': {'sp2': 60}, 'bond_order_class_counts': {'5_6': 60, '6_6': 30}, 'pi_system_label_counts': {'curved_fullerene_pi_network': 60}, 'sigma_framework_label_counts': {'curved_fullerene_sigma_cage': 60}, 'topology_class_counts': {'curved_fullerene_cage': 60}}
adamantane: {'node_count': 10, 'edge_count': 12, 'degree_distribution': {'2': 6, '3': 4}, 'hybridization_counts': {'sp3': 10}, 'bond_order_class_counts': {'single': 12}, 'pi_system_label_counts': {'none': 10}, 'sigma_framework_label_counts': {'diamondoid_sigma_cage': 10}, 'topology_class_counts': {'saturated_sp3_diamondoid_cage': 10}, 'specific_checks': {'node_count': 10, 'edge_count': 12, 'degree_distribution': {'2': 6, '3': 4}, 'passed': True, 'hybridization_counts': {'sp3': 10}, 'pi_system_label_counts': {'none': 10}, 'sigma_framework_label_counts': {'diamondoid_sigma_cage': 10}, 'hydrogen_count_metadata_counts': {'1': 4, '2': 6}}}
```

## Proxy Risk Summary

|proxy_id|intended_use|smuggling_risk|claim_boundary|
|---|---|---|---|
|coordinate_distance_reference_kernel|reference_control_only|high|coordinate-derived kernel is not independent evidence|
|graph_distance_reference_kernel|reference_control_only|high|graph-derived kernel is not independent evidence|
|bond_order_proxy|synthetic_scaffold_label_only|medium_to_high|bond-order labels can encode the target distinction|
|hybridization_label_proxy|synthetic_scaffold_label_only|high|hybridization labels are circular if over-read|
|local_environment_proxy|synthetic_local_label_proxy_only|medium_to_high|local labels can encode scaffold construction|
|sigma_pi_organization_proxy|synthetic_sigma_pi_descriptor_only|medium_to_high|sigma/pi labels are scaffold metadata, not validation|
|spectral_graph_toy_proxy|toy_graph_diagnostic_only|medium|toy graph spectrum is not molecular validation|

Coordinate- and graph-derived kernels are reference/control only. Label-derived proxies are synthetic and circular if over-read.

## 05C Warning Carried Forward

local-neighborhood sensitivity under small additive magnitude noise at 0.02

## Future Result Discussion Requirement

Create a separate DATA-02B result discussion only after reading these outputs. It must include a human-readable Bauchbild and remain scaffold-only, defensive, and method-level.
