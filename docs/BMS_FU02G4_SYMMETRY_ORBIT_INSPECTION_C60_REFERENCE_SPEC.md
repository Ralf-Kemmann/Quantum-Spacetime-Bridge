# BMS-FU02g4 — Symmetry-Orbit Inspection of the C60 Reference Carrier Region Specification

Date: 2026-05-03  
Project: Gravitation und RaumZeit / Quantum-Spacetime-Bridge  
Recommended repo target: `docs/BMS_FU02G4_SYMMETRY_ORBIT_INSPECTION_C60_REFERENCE_SPEC.md`  
Status: Specification and implementation block

---

## 1. Purpose

BMS-FU02g4 follows the mixed FU02g3 result.

FU02g3 showed:

```text
Simple same-size and type-preserving null patches rarely reproduce the FU02f1
reference region.

Connected and role-aware connected decoys reproduce near-reference profiles at
about 9-10%.

Strict near-reference reproduction is absent or nearly absent.
```

Therefore FU02g4 asks the sharper symmetry question:

```text
Is the FU02f1 C60 carrier region merely one of many common connected C60
face-patches, or does it represent a more constrained symmetry/orbit class?
```

Internal formulation:

```text
Ist unser Klunker nur irgendein verbundener Patch,
oder eine besondere Orbit-/Symmetrieklasse?
```

---

## 2. Scope

FU02g4 is a symmetry-orbit and patch-signature inspection block.

Allowed:

```text
inspect C60 face-graph automorphisms
compute orbit/stabilizer indicators if feasible
compute role-colored patch signatures
compare reference signature to connected same-size patches
```

Not allowed:

```text
claim physical spacetime
claim molecular quantum chemistry
claim full C60 group-theory proof unless explicitly validated
claim uniqueness without checking automorphism/orbit equivalence
claim universal statistical significance
```

---

## 3. Inputs

Required:

```text
data/bms_fu02g_c60_reference_cells.csv
data/bms_fu02g_c60_reference_edges.csv
runs/BMS-FU02f1/face_id_interval_repair_3d_graph_layout_open/bms_fu02f1_face_layout.csv
```

Optional:

```text
runs/BMS-FU02g3/real_structure_memory_null_specificity_open/bms_fu02g3_null_replicates.csv
runs/BMS-FU02g3/real_structure_memory_null_specificity_open/bms_fu02g3_reference_profile.json
```

---

## 4. Reference roles

FU02f1 labels are mapped as in FU02g3:

```text
mixed_seam_boundary_face -> mixed_core
hp_boundary_face -> pentagon_boundary
carrier_adjacent_face -> adjacent_shell
noncarrier_face -> noncarrier
```

Reference carrier set:

```text
mixed_core + pentagon_boundary
```

Role-colored reference:

```text
mixed_core:
  H_09 H_11 H_13 H_16 H_17 H_18 H_19 H_20

pentagon_boundary:
  H_07 H_12 H_14 H_15 P_07 P_08 P_09 P_10 P_11
```

The runner computes this from input rather than hard-coding it.

---

## 5. Automorphism-orbit inspection

If `networkx` is available, FU02g4 builds the C60 face-adjacency graph and
enumerates graph automorphisms using `GraphMatcher`.

For each automorphism:

```text
image of reference carrier set
image of role-colored reference assignment
```

Readouts:

```text
automorphism_count
carrier_orbit_size
role_colored_orbit_size
carrier_stabilizer_size
role_colored_stabilizer_size
inversion_like_partner_candidate_count
```

Important caveat:

```text
Face-graph automorphisms are graph automorphisms of the reconstructed face
adjacency graph, not an externally certified full molecular symmetry group
unless explicitly cross-validated.
```

If automorphism enumeration is too expensive or unavailable, the runner falls
back to patch-signature diagnostics only and emits a warning.

---

## 6. Patch-signature inspection

FU02g4 computes reference patch signatures independent of full automorphism
enumeration.

### 6.1 Uncolored carrier signature

```text
carrier_face_count
carrier_hexagon_count
carrier_pentagon_count
carrier_component_count
largest_carrier_component_count
carrier_internal_adjacency_count
carrier_boundary_adjacency_count
carrier_external_neighbor_count
carrier_induced_degree_histogram
boundary_neighbor_type_counts
distance_shell_counts_from_mixed_core
```

### 6.2 Role-colored signature

```text
mixed_core_count
pentagon_boundary_count
mixed_core_internal_adjacency_count
pentagon_boundary_internal_adjacency_count
mixed_to_pentagon_boundary_adjacency_count
mixed_core_induced_degree_histogram
pentagon_boundary_induced_degree_histogram
role_boundary_profile
```

### 6.3 Canonical-ish signatures

Without a full canonical graph isomorphism backend, FU02g4-v0 uses stable
signature strings from sorted counts and histograms:

```text
carrier_signature_string
role_colored_signature_string
```

These are not full isomorphism certificates. They are auditable patch-profile
fingerprints.

---

## 7. Connected patch comparison

FU02g4 samples connected same-size patches on the C60 face graph and computes
their signatures.

Default:

```text
sample_count = 5000
random_seed = 260504
```

Readouts:

```text
carrier_signature_match_count
carrier_signature_match_fraction
role_colored_signature_match_count
role_colored_signature_match_fraction
carrier_signature_near_count
role_colored_signature_near_count
```

Interpretation:

```text
If the exact or near reference patch signature is common, the FU02f1 patch class
is cheap.

If exact or near signatures are rare while automorphism orbit size is bounded,
the patch has a stronger construction-qualified specificity indication.
```

---

## 8. Outputs

Output directory:

```text
runs/BMS-FU02g4/symmetry_orbit_inspection_c60_reference_open/
```

Expected files:

```text
bms_fu02g4_reference_patch_signature.json
bms_fu02g4_automorphism_orbit_summary.json
bms_fu02g4_connected_patch_signature_samples.csv
bms_fu02g4_signature_match_summary.json
bms_fu02g4_run_manifest.json
bms_fu02g4_warnings.json
bms_fu02g4_config_resolved.yaml
```

---

## 9. Interpretation boundary

Allowed:

```text
FU02g4 inspects whether the FU02f1 C60 reference carrier region belongs to a
small or large automorphism orbit and whether its role-colored patch signature
is common among connected same-size C60 face patches.
```

Allowed if supported:

```text
The reference patch signature is rare among sampled connected same-size patches.
```

Allowed if supported:

```text
The reference patch is one representative of a symmetry-equivalent orbit class.
```

Not allowed:

```text
FU02g4 proves physical real-structure memory.
FU02g4 proves spacetime.
FU02g4 proves full molecular symmetry unless externally validated.
FU02g4 proves uniqueness beyond the tested graph/signature scope.
```

---

## 10. Recommended next block

If FU02g4 shows a rare role-colored orbit/signature:

```text
BMS-FU02g5 — Geometry-Class Memory Synthesis
```

If FU02g4 remains inconclusive:

```text
BMS-FU02g4b — Stronger Canonical Patch Isomorphism / Exact Orbit Enumeration
```

---

## 11. Internal summary

```text
FU02g3:
  Nicht völlig billig,
  aber connected/role-aware Attrappen können grob mithalten.

FU02g4:
  Symmetrie-Orbit und Patch-Signatur prüfen.

Frage:
  Ist der Klunker nur ein verbundener C60-Fleck,
  oder ein besonderer Repräsentant einer Rollen-/Symmetrieklasse?
```
