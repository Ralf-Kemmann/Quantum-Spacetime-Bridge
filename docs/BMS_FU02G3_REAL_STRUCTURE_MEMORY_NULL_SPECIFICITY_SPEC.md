# BMS-FU02g3 — Real-Structure Memory Comparison and Null Specificity Specification

Date: 2026-05-02  
Project: Gravitation und RaumZeit / Quantum-Spacetime-Bridge  
Recommended repo target: `docs/BMS_FU02G3_REAL_STRUCTURE_MEMORY_NULL_SPECIFICITY_SPEC.md`  
Status: Specification and implementation block

---

## 1. Purpose

BMS-FU02g3 follows the FU02g2 result:

```text
FU02g2-v0:
  The generic cell-level proxy produced compact connected interior carrier
  regions in all tested geometry classes.

Conclusion:
  Compact interior patches are cheap.
```

FU02g3 therefore asks the sharper real-structure-memory question:

```text
Can the FU02f1 C60 carrier-region pattern, including its role-balance structure,
be recovered or mimicked under controlled null patch assignments?
```

Internal formulation:

```text
Nicht:
  Findet der Proxy irgendwo einen Innenklunker?

Sondern:
  Kann er den C60-Klunker mit seiner Rollenfarbe wiederfinden,
  und ist das gegen Kontrollen billig oder nicht?
```

---

## 2. Scope

FU02g3 is a null-specificity and real-structure-memory comparison block.

Allowed:

```text
Use FU02f1 C60 reference roles.
Construct null patches on the same C60 face graph.
Compare overlap, role balance, compactness and boundary-shell structure.
Report empirical null exceedance fractions.
```

Not allowed:

```text
Claim physical spacetime.
Claim molecular quantum chemistry.
Claim formal universal p-values.
Claim impossible under all nulls.
Claim final proof of real-structure memory.
```

The result is construction-qualified and null-family-specific.

---

## 3. Inputs

Required C60 FU02f1 reference:

```text
runs/BMS-FU02f1/face_id_interval_repair_3d_graph_layout_open/bms_fu02f1_face_layout.csv
```

Required C60 inventory:

```text
data/bms_fu02g_c60_reference_cells.csv
data/bms_fu02g_c60_reference_edges.csv
data/bms_fu02g_c60_reference_nodes.csv
```

Optional FU02g2 diagnostic output:

```text
runs/BMS-FU02g2/carrier_diagnostic_transfer_geometry_controls_open/bms_fu02g2_cell_diagnostics.csv
```

If FU02g2 diagnostics are present, FU02g3 can compare the generic proxy patch
against the FU02f1 reference.

---

## 4. Reference roles

FU02f1 role labels are mapped into a compact reference profile:

```text
mixed_seam_boundary_face:
  reference role = mixed_core

hp_boundary_face:
  reference role = pentagon_boundary

carrier_adjacent_face:
  reference role = adjacent_shell

noncarrier_face:
  reference role = noncarrier
```

Primary reference carrier set:

```text
mixed_core + pentagon_boundary
```

Expected from FU02f1:

```text
carrier faces = 17
mixed core faces = 8
pentagon boundary faces = 9
```

But the runner should compute these from the FU02f1 table rather than hard-code
them.

---

## 5. Null families

FU02g3-v0 uses same-C60 face-graph null patches. These are not universal nulls;
they are controlled construction probes.

### 5.1 carrier_count_random_patch

Randomly choose the same number of carrier faces as the reference carrier set.

Preserves:

```text
carrier face count
```

Does not preserve:

```text
cell type
role balance
compactness
adjacency
```

### 5.2 type_count_preserving_patch

Choose the same number of hexagon and pentagon carrier faces as the reference.

Preserves:

```text
carrier face count
hexagon/pentagon count
```

Does not preserve:

```text
mixed-core/pentagon-boundary role arrangement
compactness
adjacency
```

### 5.3 connected_patch_seeded

Grow a connected patch of the same size on the C60 face adjacency graph.

Preserves:

```text
carrier face count
connectedness
```

Does not preserve:

```text
role balance
hexagon/pentagon count unless accidentally matched
```

### 5.4 role_count_preserving_connected_patch

Grow a connected patch and assign roles to match the reference role counts.

Preserves:

```text
carrier face count
connectedness
mixed_core count
pentagon_boundary count
```

Does not preserve:

```text
exact placement
reference overlap
symmetry/orbit relation
```

This is the strongest v0 decoy family.

---

## 6. Metrics

### 6.1 Reference overlap

```text
carrier_overlap_count
carrier_overlap_fraction
mixed_core_overlap_count
mixed_core_overlap_fraction
pentagon_boundary_overlap_count
pentagon_boundary_overlap_fraction
```

### 6.2 Role-balance profile

```text
carrier_face_count
mixed_core_count
pentagon_boundary_count
adjacent_shell_count
noncarrier_count
carrier_hexagon_count
carrier_pentagon_count
role_balance_deviation
```

Role-balance deviation:

```text
abs(mixed_core_count - reference_mixed_core_count)
+ abs(pentagon_boundary_count - reference_pentagon_boundary_count)
+ abs(carrier_hexagon_count - reference_carrier_hexagon_count)
+ abs(carrier_pentagon_count - reference_carrier_pentagon_count)
```

### 6.3 Compactness and adjacency

```text
carrier_component_count
largest_carrier_component_count
compactness_proxy
carrier_internal_adjacency_count
carrier_boundary_adjacency_count
carrier_external_neighbor_count
max_distance_to_reference_mixed_core
mean_distance_to_reference_mixed_core
```

### 6.4 Near-reference criteria

Default near-reference rule:

```text
carrier_overlap_fraction >= 0.70
role_balance_deviation <= 2
carrier_component_count == 1
compactness_proxy >= 0.90
```

Strict near-reference rule:

```text
carrier_overlap_fraction >= 0.85
role_balance_deviation == 0
carrier_component_count == 1
compactness_proxy >= 0.95
```

---

## 7. Empirical null comparisons

For each null family:

```text
near_reference_count
near_reference_fraction
strict_near_reference_count
strict_near_reference_fraction
median carrier overlap
max carrier overlap
min role-balance deviation
median role-balance deviation
```

Interpretation:

```text
If near-reference profiles are rare or absent in stronger nulls, this supports
a construction-qualified specificity indication.

If near-reference profiles are common, the reference carrier pattern is cheap
under that null family.
```

---

## 8. Outputs

Output directory:

```text
runs/BMS-FU02g3/real_structure_memory_null_specificity_open/
```

Expected files:

```text
bms_fu02g3_reference_profile.json
bms_fu02g3_null_replicates.csv
bms_fu02g3_null_family_summary.csv
bms_fu02g3_generic_proxy_reference_overlap.csv
bms_fu02g3_run_manifest.json
bms_fu02g3_warnings.json
bms_fu02g3_config_resolved.yaml
```

---

## 9. Interpretation boundary

Allowed:

```text
FU02g3 tests whether the FU02f1 C60 role-colored carrier region is cheap or
rare under selected same-C60 face-graph null patch families.
```

Allowed if supported:

```text
The FU02f1 C60 carrier-region profile is not frequently reproduced by the
tested null patch families.
```

Not allowed:

```text
This proves physical real-structure memory.
This proves C60 symmetry recovery.
This proves spacetime.
This is a universal p-value.
```

---

## 10. Recommended next block

If FU02g3 finds a non-cheap reference profile:

```text
BMS-FU02g4 — Symmetry-Orbit Inspection of the C60 Reference Carrier Region
```

Purpose:

```text
Determine whether the FU02f1 carrier region is unique, symmetry-equivalent to
many copies, or a representative of an orbit class.
```

---

## 11. Internal summary

```text
FU02g2:
  Der einfache Innenklunker ist billig.

FU02g3:
  Ist der richtige C60-Klunker mit Rollenfarbe billig?

Test:
  Referenzregion aus FU02f1
  Null-Patches auf derselben C60-Face-Struktur
  Overlap
  Rollenbalance
  Kompaktheit

Ziel:
  construction-qualified real-structure-memory specificity indication,
  falls die Attrappen die Rollenfarbe nicht treffen.
```
