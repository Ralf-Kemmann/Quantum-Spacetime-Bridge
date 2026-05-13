# QSB-BRIDGE-DATA-02A Testdata Scaffold Plan

## 1. Purpose

QSB-BRIDGE-DATA-02A creates synthetic/reference-style test data for an sp2 contrast pair:

```text
benzene: planar aromatic sp2 ring / small resonator
C60: curved fullerene sp2 cage / carrier-like structure
```

This is not real-data validation, physical validation, or molecular validation. It is a controlled scaffold block for building contrast data before any later real DATA-02 attempt.

## 2. Safety Rule

The C60 scaffold must be exact and validated before use. The required checks are:

```text
node_count = 60
edge_count = 90
all node degrees = 3
face_count = 32
pentagon_count = 12
hexagon_count = 20
Euler check: V - E + F = 2
bond_class_counts ideally:
  6_6 = 30
  5_6 = 60
```

If this cannot be implemented deterministically and validated, the run must report:

```text
stop_go_outcome: requires_exact_c60_scaffold_before_use
```

and must not claim C60 scaffold validity.

## 3. Testdata Families

DATA-02A declares these scaffold families:

```text
benzene_planar_ring_reference
benzene_uniform_aromatic_proxy
benzene_bond_alternation_control
c60_fullerene_graph_reference
c60_bond_class_weighted_proxy
c60_curvature_stress_proxy
c60_face_type_local_environment_proxy
matched_random_sp2_control
degree_preserving_random_control
bond_class_shuffle_control
curvature_label_shuffle_control
```

## 4. Core Tables

The scaffold generator should write:

```text
data/QSB-BRIDGE-DATA-02A/benzene_nodes.csv
data/QSB-BRIDGE-DATA-02A/benzene_edges.csv
data/QSB-BRIDGE-DATA-02A/c60_nodes.csv
data/QSB-BRIDGE-DATA-02A/c60_edges.csv
data/QSB-BRIDGE-DATA-02A/c60_faces.csv
data/QSB-BRIDGE-DATA-02A/sp2_contrast_manifest.json
```

## 5. Required Fields

### benzene_nodes.csv

```text
node_id: string, stable node id
system_id: string, benzene
atom_label: string, synthetic atom label
sp2_role: string, planar aromatic carbon role
ring_index: integer, ring position
x_ref: float, reference scaffold x coordinate
y_ref: float, reference scaffold y coordinate
z_ref: float, reference scaffold z coordinate
curvature_label: string, planar label
local_environment_label: string, benzene local environment
claim_role: string, reference/control boundary
```

### benzene_edges.csv

```text
edge_id: string, stable edge id
system_id: string, benzene
source: string, source node id
target: string, target node id
bond_class: string, aromatic or alternation label
bond_order_proxy: float, synthetic/reference edge weight
edge_family: string, family label
is_ring_edge: boolean, benzene ring edge flag
reference_control_role: string, reference/control boundary
```

### c60_nodes.csv

```text
node_id: string, stable C60 node id
system_id: string, c60
atom_label: string, synthetic atom label
sp2_role: string, fullerene sp2 carbon role
degree_target: integer, expected degree
x_ref: float, reference scaffold x coordinate
y_ref: float, reference scaffold y coordinate
z_ref: float, reference scaffold z coordinate
curvature_label: string, toy curvature/environment label
local_environment_label: string, face environment label
claim_role: string, reference/control boundary
```

### c60_edges.csv

```text
edge_id: string, stable C60 edge id
system_id: string, c60
source: string, source node id
target: string, target node id
bond_class: string, 5_6 or 6_6
bond_order_proxy: float, synthetic/reference edge weight
edge_family: string, family label
face_pair_type: string, adjacent face classes
reference_control_role: string, reference/control boundary
```

### c60_faces.csv

```text
face_id: string, stable face id
system_id: string, c60
face_type: string, pentagon or hexagon
node_ids: string, semicolon-separated node ids
edge_ids: string, semicolon-separated edge ids
face_size: integer, 5 or 6
local_environment_label: string, local face environment
claim_role: string, reference/control boundary
```

### sp2_contrast_manifest.json

```text
block_id: string
run_id: string
claim_boundary: string
external_data_downloaded: boolean
systems: array
families: array
proxy_families: array
tables: object
qsb_bridge_num_05c_warning: string
c60_validation: object
```

## 6. Proxy Families

DATA-02A declares or generates:

```text
coordinate_distance_reference_kernel: reference/control only; high smuggling risk
graph_distance_reference_kernel: reference/control only; high smuggling risk
bond_class_weighted_proxy: synthetic contrast proxy only
local_environment_proxy: synthetic local label proxy only
spectral_graph_toy_proxy: toy graph diagnostic only
phase_loop_toy_proxy: toy loop/phase scaffold only
```

Coordinate- and graph-derived kernels must never be presented as independent evidence.

## 7. Diagnostics

The readouts should report:

```text
node_count
edge_count
degree_distribution
bond_class_counts
face_type_counts
aromatic_uniformity_flag
curvature_proxy_summary
proxy_smuggling_risk
benzene_vs_c60_contrast_summary
```

DATA-02A must explicitly carry forward the 05C warning:

```text
local-neighborhood sensitivity under small additive magnitude noise at 0.02
```

## 8. Planned Run Artifacts

The run directory is:

```text
runs/QSB-BRIDGE-DATA-02A/sp2_contrast_scaffold_open/
```

Required artifacts:

```text
summary.json
readout.md
sp2_family_summary.csv
bond_class_summary.csv
face_environment_summary.csv
proxy_risk_summary.csv
resolved_config.json
```

## 9. Future Result Discussion Requirement

After DATA-02A outputs are read, a separate result discussion should be created. It should include a human-readable Bauchbild for the scaffold block and remain defensive and method-level.

The discussion should explain that DATA-02A is a controlled contrast table, not a molecular experiment.

## 10. Claim Boundary

DATA-02A does not establish:

```text
spacetime emergence
physical metric recovery
causal structure
de-Broglie confirmation
real quantum dynamics
real-data validation
molecular validation
physical C60 validation
```

It creates synthetic/reference-style scaffold data only.
