# QSB-BRIDGE-DATA-02C Control Ensembles Plan

## 1. Purpose

QSB-BRIDGE-DATA-02C instantiates synthetic/reference-style control ensembles for the DATA-02B carbon bonding-organization ladder:

```text
ethyne linear sp carbon wire
benzene planar sp2 aromatic resonator
C60 curved sp2 fullerene cage
adamantane saturated sp3 diamondoid cage
```

The goal is to test whether later diagnostics can distinguish bonding organization as a coherent pattern, rather than merely reading hybridization labels, bond-order labels, topology, or degree distribution.

DATA-02C is scaffold/control-data only. It is not real-data validation, molecular validation, or physical validation.

## 2. Inputs

DATA-02C uses local DATA-02B scaffold inputs only:

```text
data/QSB-BRIDGE-DATA-02B/carbon_ladder_nodes.csv
data/QSB-BRIDGE-DATA-02B/carbon_ladder_edges.csv
data/QSB-BRIDGE-DATA-02B/carbon_bonding_organization_manifest.json
```

These inputs remain synthetic scaffold sources.

## 3. Determinism

Controls are generated deterministically with a fixed seed. The seed must be reported in:

```text
data/QSB-BRIDGE-DATA-02C/control_ensemble_config.json
data/QSB-BRIDGE-DATA-02C/control_ensemble_manifest.json
runs/QSB-BRIDGE-DATA-02C/control_ensembles_open/summary.json
runs/QSB-BRIDGE-DATA-02C/control_ensembles_open/resolved_config.json
```

## 4. Control Families

DATA-02C instantiates:

```text
hybridization_label_shuffle_control
bond_order_shuffle_control
sigma_pi_label_shuffle_control
topology_matched_random_control
carbon_skeleton_degree_control
within_system_label_shuffle
cross_system_label_swap
topology_preserving_label_randomization
```

The controls distinguish:

```text
label-only destruction
topology-only destruction
degree-preserving topology randomization
bond-organization mismatch
sigma/pi organization mismatch
```

Successful controls must be treated as possible negative findings if they erase or mimic the original organization too easily.

## 5. Core Tables

DATA-02C writes:

```text
data/QSB-BRIDGE-DATA-02C/control_ensemble_manifest.json
data/QSB-BRIDGE-DATA-02C/control_nodes.csv
data/QSB-BRIDGE-DATA-02C/control_edges.csv
data/QSB-BRIDGE-DATA-02C/control_family_summary.csv
data/QSB-BRIDGE-DATA-02C/control_validation_summary.csv
```

## 6. Required Fields

### control_nodes.csv

```text
control_id: string, stable control instance id
control_family_id: string, control family name
source_system_id: string, original system id
global_node_id: string, control node id
source_global_node_id: string, original DATA-02B node id
node_id: string, local node id
atom_label: string, carbon label
hybridization_label: string, original or randomized hybridization label
hydrogen_count_metadata: string, hydrogen metadata
saturation_label: string, saturation metadata
pi_system_label: string, original or randomized pi label
sigma_framework_label: string, original or randomized sigma label
topology_class: string, original or control topology class
x_ref: string, reference coordinate if preserved
y_ref: string, reference coordinate if preserved
z_ref: string, reference coordinate if preserved
control_transform_note: string, what was changed
claim_role: string, synthetic_control_only
```

### control_edges.csv

```text
control_id: string, stable control instance id
control_family_id: string, control family name
source_system_id: string, original system id
global_edge_id: string, control edge id
source_global_edge_id: string, original DATA-02B edge id if inherited
source: string, control source node id
target: string, control target node id
source_original: string, original source if applicable
target_original: string, original target if applicable
bond_order_class: string, original or randomized bond label
bond_order_proxy: string, synthetic/reference value
hybridization_pair: string, original or randomized pair label
pi_system_label: string, original or randomized pi label
sigma_framework_label: string, original or randomized sigma label
control_transform_note: string, what was changed
reference_control_role: string, synthetic_control_only
```

### control_family_summary.csv

```text
control_family_id: string, control family name
control_distinction: string, label/topology/degree/mismatch class
control_count: integer, instances generated
systems_included: string, semicolon-separated source systems
preservation_target: string, what should remain fixed
destruction_target: string, what should be disrupted
interpretation_boundary: string, defensive reading of this family
```

### control_validation_summary.csv

```text
control_id: string, stable control instance id
source_system_id: string, original system
control_family_id: string, control family
node_count_preserved: boolean
edge_count_preserved: boolean
degree_distribution_preserved: boolean
hybridization_counts_preserved: boolean
bond_order_counts_preserved: boolean
topology_class_preserved: boolean
sigma_pi_labels_preserved: boolean
organization_coherence_score: float, toy scaffold score
label_smuggling_risk: string, label-circularity warning
control_interpretation_boundary: string, defensive interpretation
```

## 7. Run Artifacts

The run directory is:

```text
runs/QSB-BRIDGE-DATA-02C/control_ensembles_open/
```

Required artifacts:

```text
summary.json
readout.md
control_family_summary.csv
control_validation_summary.csv
organization_coherence_summary.csv
proxy_risk_summary.csv
resolved_config.json
```

The readout and coherence summary must explicitly report:

```text
highest-risk mimic control, if any
lowest original/control coherence contrast, if computed
whether any control is flagged as a possible negative finding
```

## 8. Claim Boundary

DATA-02C does not establish:

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

It creates synthetic/reference-style control ensembles only.
