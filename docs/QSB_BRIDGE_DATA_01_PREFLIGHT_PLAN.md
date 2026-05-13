# QSB-BRIDGE-DATA-01 Preflight Plan

## 1. Purpose

QSB-BRIDGE-DATA-01 is a real-data preflight for C60, benzene / Benzol, and a very small sanity candidate.

It does not perform real-data validation. It does not download data. It documents whether later DATA-02 work could be constructed with defensible provenance, machine-readable source fields, and explicit safeguards against re-encoding known geometry into `K_ij`.

## 2. Scope

DATA-01 evaluates candidate source types:

```text
structural_coordinates
molecular_graph_bonding_adjacency
vibrational_frequencies_and_modes
spectral_normal_mode_information
quantum_chemistry_outputs_if_locally_available_later
```

The preflight only records availability, provenance expectations, proxy risks, and go/no-go recommendations for a later DATA-02 block.

## 3. Candidate Systems

### C60 fullerene

Ground truth geometry:

```text
3D molecular coordinates, cage topology, bond lengths, and fullerene symmetry as reference geometry only.
```

Independent input candidates:

```text
vibrational frequencies and modes
spectral / normal-mode information
quantum chemistry coupling-like outputs if provided locally later
```

Smuggling risk:

```text
High if K_ij is built directly from Euclidean distances or from the fullerene graph and then compared back to cage geometry.
```

Uncertainty / noise assumptions to document:

```text
coordinate source and version
experimental versus computed provenance
method and basis for computed data
mode degeneracy and symmetry handling
frequency scaling or assignment uncertainty
local-neighborhood sensitivity carried forward from 05C
```

### Benzene / Benzol

Ground truth geometry:

```text
planar hexagonal geometry, molecular bonding topology, and D6h-like symmetry as reference geometry only.
```

Independent input candidates:

```text
vibrational modes and frequencies
spectroscopy-derived normal modes
quantum chemistry outputs if provided locally later
```

Smuggling risk:

```text
High if K_ij is built from ring coordinates or graph adjacency and then interpreted as recovering ring geometry.
```

Uncertainty / noise assumptions to document:

```text
coordinate precision
hydrogen treatment
planarity assumptions
mode degeneracy
frequency scaling or assignment uncertainty
local-neighborhood sensitivity carried forward from 05C
```

### H2 sanity candidate

Ground truth geometry:

```text
single bond length / two-node geometry as a pipeline sanity reference only.
```

Independent input candidates:

```text
vibrational frequency
simple locally supplied quantum chemistry output
```

Smuggling risk:

```text
Very high interpretive risk because the geometry is nearly exhausted by one distance. H2 can check the pipeline only; it cannot support geometry-recovery claims.
```

Uncertainty / noise assumptions to document:

```text
isotope and state
bond length source
frequency source
method and basis for computed data
trivial-size limitation
```

## 4. Preflight Diagnostics

DATA-01 must emit:

```text
data_availability_status
machine_readable_format_status
provenance_status
geometry_smuggling_risk
possible_K_proxy_definitions
local_neighborhood_noise_risk
phase_information_availability
go_no_go_recommendation_for_DATA02
```

The `local_neighborhood_noise_risk` field must explicitly carry forward the 05C warning: local-neighborhood diagnostics showed sensitivity under small additive magnitude noise, with the first configured warning at `0.02`.

## 5. Planned Artifacts

The run directory is:

```text
runs/QSB-BRIDGE-DATA-01/realdata_preflight_open/
```

Required artifacts:

```text
summary.json
readout.md
candidate_source_matrix.csv
k_proxy_risk_assessment.csv
data_field_inventory.csv
realdata_preflight_decision.csv
resolved_config.json
```

## 6. Future Result Discussion Requirement

After DATA-01 outputs are read, a separate result discussion should be created. It should include a human-readable Bauchbild explaining the preflight in project language, but it should remain defensive and method-level.

The later discussion must not treat DATA-01 as physical validation. It should explain the difference between:

```text
source availability
machine-readable provenance
proxy construction risk
actual physical validation
```

## 7. Claim Boundary

DATA-01 does not establish:

```text
spacetime emergence
physical metric recovery
causal structure
de-Broglie confirmation
real quantum dynamics
molecular validation
```

It is a preflight for later real-data work only.
