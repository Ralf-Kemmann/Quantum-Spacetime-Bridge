# BMS-FU02g2 — Carrier Diagnostic Transfer to Geometry-Class Controls Specification

Date: 2026-05-02  
Project: Gravitation und RaumZeit / Quantum-Spacetime-Bridge  
Recommended repo target: `docs/BMS_FU02G2_CARRIER_DIAGNOSTIC_TRANSFER_GEOMETRY_CONTROLS_SPEC.md`  
Status: Specification and implementation block

---

## 1. Purpose

BMS-FU02g2 transfers FU02-style carrier/localization diagnostics from the C60
reference chain to the geometry-class control set prepared by FU02g1 and
FU02g1b.

Control set:

```text
c60_reference
graphene_patch
nanotube_armchair_repaired
nanotube_zigzag_repaired
```

Main question:

```text
How do carrier localization and role-balance patterns differ between:
  closed-curved C60,
  flat/open graphene,
  open-curved armchair nanotube,
  open-curved zigzag nanotube?
```

Internal formulation:

```text
Jetzt dürfen die Prüfkörper in die Diagnose.
```

---

## 2. Scope

This block is a diagnostic transfer block.

Allowed:

```text
derive comparable cell-level carrier readouts
compare compactness, boundary proximity and role balance across geometry classes
export transparent diagnostic tables and manifests
```

Not allowed:

```text
claim physical molecular geometry
claim quantum chemistry
claim spacetime
claim final real-structure memory
claim formal statistical p-values
```

FU02g2 asks whether the C60-like compact carrier picture is distinctive relative
to flat/open and open-curved graph controls.

It does not yet prove why that distinctiveness exists.

---

## 3. Inputs

### 3.1 C60 reference inventory

From FU02g1:

```text
data/bms_fu02g_c60_reference_nodes.csv
data/bms_fu02g_c60_reference_edges.csv
data/bms_fu02g_c60_reference_cells.csv
data/bms_fu02g_c60_reference_manifest.json
```

### 3.2 Graphene patch inventory

From FU02g1:

```text
data/bms_fu02g_graphene_patch_nodes.csv
data/bms_fu02g_graphene_patch_edges.csv
data/bms_fu02g_graphene_patch_cells.csv
data/bms_fu02g_graphene_patch_manifest.json
```

### 3.3 Repaired nanotube inventories

From FU02g1b:

```text
data/bms_fu02g1b_nanotube_armchair_repaired_nodes.csv
data/bms_fu02g1b_nanotube_armchair_repaired_edges.csv
data/bms_fu02g1b_nanotube_armchair_repaired_cells.csv
data/bms_fu02g1b_nanotube_armchair_repaired_manifest.json

data/bms_fu02g1b_nanotube_zigzag_repaired_nodes.csv
data/bms_fu02g1b_nanotube_zigzag_repaired_edges.csv
data/bms_fu02g1b_nanotube_zigzag_repaired_cells.csv
data/bms_fu02g1b_nanotube_zigzag_repaired_manifest.json
```

### 3.4 Optional C60 FU02 carrier-region reference

If available, the runner may ingest FU02f/FU02f1 face-layout outputs as the
C60 known carrier-region reference:

```text
runs/BMS-FU02f1/face_id_interval_repair_3d_graph_layout_open/bms_fu02f1_face_layout.csv
```

If this file is missing, FU02g2 still runs with intrinsic proxy carriers.

---

## 4. Diagnostic transfer idea

Because graphene and nanotube controls do not contain the same C60-specific
H,H / H,P seam-boundary roles, FU02g2 uses a generalized cell-level proxy
diagnostic.

Generalized carrier logic:

```text
1. Build cell adjacency from edge incident cells.
2. Compute cell-level structural features:
   - boundary status
   - cell degree in cell-adjacency graph
   - mean node degree
   - low-degree node count
   - periodic-cell flag
   - local edge support
3. Score cells by geometry-readable structural load proxies.
4. Select a comparable carrier-cell set by fraction or top-k rule.
5. Compute localization and role-balance readouts.
```

This is not intended to replace the C60 FU02 carrier chain.

It is a transfer/control diagnostic:

```text
Do open/flat or open-curved controls produce similarly compact carrier
landscapes under a comparable graph/cell readout?
```

---

## 5. Carrier scoring

FU02g2-v0 defines a transparent proxy score:

```text
carrier_score =
    + 1.00 * normalized(cell_adjacency_degree)
    + 0.75 * normalized(mean_node_degree)
    + 0.50 * normalized(two_cell_edge_fraction)
    - 0.75 * boundary_cell
    - 0.50 * low_degree_node_fraction
```

Interpretation:

```text
High score:
  interior-like, well-supported, high local adjacency cells

Low score:
  boundary-heavy or under-supported cells
```

For C60, no open boundary exists. C60 may therefore produce a more globally
distributed score unless FU02f1 reference carriers are explicitly supplied.
That is expected and should be reported.

---

## 6. Carrier selection

Default selection:

```text
top_fraction = 0.30
minimum_carrier_cells = 5
```

For each structure:

```text
carrier_cell_count = max(minimum_carrier_cells, round(top_fraction * cell_count))
```

Then select top-scoring cells.

Tie handling:

```text
stable sort by score descending, then cell_id ascending
```

This makes outputs reproducible but not symmetry-complete.

---

## 7. Cell role labels

FU02g2-v0 uses generalized labels:

```text
carrier_core_cell
carrier_boundary_cell
carrier_adjacent_cell
noncarrier_cell
```

Definitions:

```text
carrier_core_cell:
  selected carrier cell and not boundary

carrier_boundary_cell:
  selected carrier cell and boundary

carrier_adjacent_cell:
  not selected, but adjacent to at least one selected carrier cell

noncarrier_cell:
  neither selected nor adjacent to selected carrier cell
```

For C60 with FU02f1 imported, optional C60-specific labels may be preserved in
a source-role column, not forced onto other structures.

---

## 8. Localization metrics

Per structure:

```text
carrier_cell_count
carrier_cell_fraction
carrier_cell_component_count
largest_carrier_cell_component_count
carrier_boundary_cell_count
carrier_core_cell_count
carrier_adjacent_cell_count
noncarrier_cell_count
max_distance_to_carrier_core
mean_distance_to_carrier_core
cell_adjacency_edge_count
carrier_internal_adjacency_count
carrier_boundary_adjacency_count
carrier_external_neighbor_count
```

Purpose:

```text
Measure compactness, connectedness and spread of carrier-cell landscape.
```

---

## 9. Boundary metrics

For open structures:

```text
boundary_cell_count
boundary_cell_fraction
carrier_boundary_overlap_fraction
carrier_mean_distance_to_boundary
carrier_min_distance_to_boundary
```

For C60:

```text
boundary_cell_count = 0
boundary metrics marked not_applicable or null
```

Purpose:

```text
Separate true geometry-class differences from boundary artifacts.
```

---

## 10. Geometry-class comparison metrics

Across structures:

```text
relative_carrier_fraction
relative_largest_component_fraction
compactness_proxy =
  largest_carrier_cell_component_count / carrier_cell_count

boundary_dependence_proxy =
  carrier_boundary_cell_count / carrier_cell_count

adjacent_shell_ratio =
  carrier_adjacent_cell_count / carrier_cell_count
```

Interpretation:

```text
compact and low-boundary carrier set:
  potential structured localization

large boundary-overlap:
  likely boundary-driven control behavior

spread across many cells:
  weak localization
```

---

## 11. Outputs

Output directory:

```text
runs/BMS-FU02g2/carrier_diagnostic_transfer_geometry_controls_open/
```

Expected files:

```text
bms_fu02g2_cell_diagnostics.csv
bms_fu02g2_structure_summary.csv
bms_fu02g2_geometry_class_comparison.csv
bms_fu02g2_run_manifest.json
bms_fu02g2_warnings.json
bms_fu02g2_config_resolved.yaml
```

Optional:

```text
bms_fu02g2_c60_fu02f1_reference_overlap.csv
```

---

## 12. Interpretation boundary

Allowed:

```text
FU02g2 transfers a transparent cell-level carrier proxy diagnostic to the
prepared geometry-class controls.
```

Allowed if supported:

```text
The generated controls differ in carrier compactness and boundary dependence.
```

Allowed if C60 reference overlap is available:

```text
The FU02g2 proxy can be compared against the FU02f1 C60 carrier-region reference.
```

Not allowed:

```text
FU02g2 proves real-structure memory.
FU02g2 proves molecular chemistry.
FU02g2 proves physical spacetime.
FU02g2 proves formal statistical significance.
```

---

## 13. Recommended next block

After FU02g2:

```text
BMS-FU02g3 — Real-Structure Memory Comparison and Null Specificity
```

Purpose:

```text
Add null families and reference-overlap metrics to test whether carrier
localization is specific beyond boundary, degree and geometry-class effects.
```

---

## 14. Internal summary

```text
FU02g2:

  Inputs:
    C60
    Graphen
    reparierter Armchair-Nanotube
    reparierter Zigzag-Nanotube

  Does:
    cell-level carrier proxy
    compactness
    boundary dependence
    geometry-class comparison

  Does not:
    final proof
    chemistry
    spacetime
    formal p-values

  Question:
    Malt C60 einen anderen Klunker als flach/offen/gekrümmt?
```
