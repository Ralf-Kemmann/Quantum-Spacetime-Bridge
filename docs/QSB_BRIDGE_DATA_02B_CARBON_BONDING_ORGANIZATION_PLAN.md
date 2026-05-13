# QSB-BRIDGE-DATA-02B Carbon Bonding-Organization Plan

## 1. Purpose

QSB-BRIDGE-DATA-02B extends the DATA-02A benzene/C60 sp2 contrast scaffold into a carbon bonding-organization ladder:

```text
ethyne: linear sp carbon wire
benzene: planar sp2 aromatic resonator
C60: curved sp2 fullerene cage
adamantane: saturated sp3 diamondoid cage
```

This is scaffold/testdata only. It is not real-data validation, molecular validation, or physical validation.

## 2. Primary Representation

The primary scaffold representation is carbon-skeleton-only.

Hydrogen and saturation are represented as metadata rather than primary graph nodes. This keeps all four systems comparable: graph nodes are carbon scaffold positions, graph edges are carbon-carbon organization, and hydrogen counts complete the chemical label without changing the scaffold topology.

This is especially important for adamantane. DATA-02B uses carbon-carbon connectivity, not full valence degree:

```text
node_count = 10
carbon-carbon edge_count = 12
degree_distribution = {2: 6, 3: 4}
bridgehead carbons: degree 3, hydrogen_count_metadata = 1
secondary CH2 carbons: degree 2, hydrogen_count_metadata = 2
all nodes hybridization_label = sp3
pi_system_label = none
sigma_framework_label = diamondoid_sigma_cage
```

The incorrect full-valence scaffold is not used:

```text
edge_count = 16
degree_distribution = {3: 4, 4: 6}
```

## 3. Scaffold Systems

DATA-02B implements:

```text
ethyne_linear_sp_carbon_wire
benzene_planar_sp2_aromatic_resonator
c60_curved_sp2_fullerene_cage
adamantane_saturated_sp3_diamondoid_cage
```

Benzene and C60 are inherited from the local DATA-02A synthetic/reference scaffold tables. They remain scaffold references, not real-data sources.

## 4. Testdata Families

DATA-02B declares:

```text
ethyne_linear_sp_reference
ethyne_triple_bond_proxy
benzene_planar_sp2_reference
benzene_aromatic_uniform_proxy
c60_curved_sp2_cage_reference
c60_bond_class_environment_proxy
adamantane_sp3_cage_reference
adamantane_sigma_framework_proxy
hybridization_label_shuffle_control
topology_matched_random_control
bond_order_shuffle_control
carbon_skeleton_degree_control
```

Controls are scaffold families unless later instantiated as explicit null ensembles.

## 5. Core Tables

The generator writes:

```text
data/QSB-BRIDGE-DATA-02B/ethyne_nodes.csv
data/QSB-BRIDGE-DATA-02B/ethyne_edges.csv
data/QSB-BRIDGE-DATA-02B/adamantane_nodes.csv
data/QSB-BRIDGE-DATA-02B/adamantane_edges.csv
data/QSB-BRIDGE-DATA-02B/carbon_ladder_nodes.csv
data/QSB-BRIDGE-DATA-02B/carbon_ladder_edges.csv
data/QSB-BRIDGE-DATA-02B/carbon_bonding_organization_manifest.json
```

## 6. Required Fields

### ethyne_nodes.csv

```text
node_id: string, stable carbon node id
system_id: string, ethyne
atom_label: string, carbon label
carbon_index: integer, carbon position in scaffold
hybridization_label: string, sp
hydrogen_count_metadata: integer, hydrogen count as metadata
saturation_label: string, unsaturated
pi_system_label: string, linear triple-bond pi descriptor
sigma_framework_label: string, linear sigma descriptor
x_ref: float, reference scaffold coordinate
y_ref: float, reference scaffold coordinate
z_ref: float, reference scaffold coordinate
claim_role: string, scaffold boundary
```

### ethyne_edges.csv

```text
edge_id: string, stable edge id
system_id: string, ethyne
source: string, source carbon node id
target: string, target carbon node id
bond_order_class: string, triple
bond_order_proxy: float, synthetic/reference edge weight
hybridization_pair: string, sp_sp
pi_system_label: string, triple-bond pi descriptor
sigma_framework_label: string, sigma descriptor
reference_control_role: string, scaffold boundary
```

### adamantane_nodes.csv

```text
node_id: string, stable carbon node id
system_id: string, adamantane
atom_label: string, carbon label
carbon_index: integer, carbon position in scaffold
hybridization_label: string, sp3
hydrogen_count_metadata: integer, 1 for bridgehead CH and 2 for secondary CH2
saturation_label: string, saturated
pi_system_label: string, none
sigma_framework_label: string, diamondoid_sigma_cage
degree_target: integer, carbon-skeleton degree
local_environment_label: string, bridgehead_CH or secondary_CH2
x_ref: float, reference scaffold coordinate
y_ref: float, reference scaffold coordinate
z_ref: float, reference scaffold coordinate
claim_role: string, scaffold boundary
```

### adamantane_edges.csv

```text
edge_id: string, stable edge id
system_id: string, adamantane
source: string, source carbon node id
target: string, target carbon node id
bond_order_class: string, single
bond_order_proxy: float, synthetic/reference edge weight
hybridization_pair: string, sp3_sp3
pi_system_label: string, none
sigma_framework_label: string, diamondoid_sigma_cage
reference_control_role: string, scaffold boundary
```

### carbon_ladder_nodes.csv

```text
global_node_id: string, system-qualified stable id
node_id: string, local node id
system_id: string, scaffold system
atom_label: string, carbon label
hybridization_label: string, sp / sp2 / sp3
hydrogen_count_metadata: integer, hydrogen count metadata
saturation_label: string, saturated / unsaturated / aromatic metadata
pi_system_label: string, pi organization label
sigma_framework_label: string, sigma framework label
topology_class: string, wire / ring / fullerene cage / diamondoid cage
x_ref: float, reference scaffold coordinate
y_ref: float, reference scaffold coordinate
z_ref: float, reference scaffold coordinate
claim_role: string, scaffold boundary
```

### carbon_ladder_edges.csv

```text
global_edge_id: string, system-qualified stable id
edge_id: string, local edge id
system_id: string, scaffold system
source: string, local source node id
target: string, local target node id
global_source: string, system-qualified source id
global_target: string, system-qualified target id
bond_order_class: string, single / aromatic / triple / 5_6 / 6_6
bond_order_proxy: float, synthetic/reference edge weight
hybridization_pair: string, hybridization pair label
pi_system_label: string, pi organization label
sigma_framework_label: string, sigma framework label
reference_control_role: string, scaffold boundary
```

### carbon_bonding_organization_manifest.json

```text
block_id: string
run_id: string
claim_boundary: string
external_data_downloaded: boolean
primary_representation: string
hydrogen_policy: string
systems: array
families: array
proxy_families: array
tables: object
qsb_bridge_num_05c_warning: string
validation: object
```

## 7. Proxy Families

DATA-02B declares:

```text
coordinate_distance_reference_kernel: reference/control only; high smuggling risk
graph_distance_reference_kernel: reference/control only; high smuggling risk
bond_order_proxy: synthetic scaffold label; can encode target distinction
hybridization_label_proxy: synthetic label proxy; circular if over-read
local_environment_proxy: scaffold-local environment label only
sigma_pi_organization_proxy: synthetic sigma/pi descriptor only
spectral_graph_toy_proxy: toy graph diagnostic only
```

## 8. Diagnostics

The readouts report:

```text
system_count
node_count
edge_count
degree_distribution
hybridization_counts
bond_order_class_counts
pi_system_label_summary
sigma_framework_label_summary
topology_class_summary
bonding_organization_contrast_summary
proxy_smuggling_risk
```

DATA-02B carries forward the 05C warning:

```text
local-neighborhood sensitivity under small additive magnitude noise at 0.02
```

## 9. Future Result Discussion Requirement

After DATA-02B outputs are read, a separate result discussion should be created. It should include a human-readable Bauchbild for the bonding-organization ladder and remain scaffold-only, defensive, and method-level.

## 10. Claim Boundary

DATA-02B does not establish:

```text
real-data validation
molecular validation
physical validation
spacetime emergence
physical metric recovery
causal structure
de-Broglie confirmation
real quantum dynamics
```

It creates a synthetic/reference-style carbon bonding-organization scaffold only.
