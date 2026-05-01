# BMS-FU01b — C60 Core Selection Sensitivity Specification

Date: 2026-05-01  
Project: Gravitation und RaumZeit / Quantum-Spacetime-Bridge  
Recommended repo target: `docs/BMS_FU01B_C60_CORE_SELECTION_SENSITIVITY_SPEC.md`  
Status: Specification only; no numerical run completed yet

---

## 1. Purpose

BMS-FU01b extends BMS-FU01 by testing whether the C60 structure-information result depends on the particular reference-core selection rule.

BMS-FU01-v0 used an `edge_class_core` consisting of the first 12 sorted `6_6` edges. Inspection showed that this reference core is not symmetry-distributed across the whole C60 cage. It forms a local H-H patch involving early hexagon faces such as:

```text
H_01, H_02, H_03, H_04, H_05,
H_06, H_07, H_08,
H_14, H_15
```

Therefore, FU01-v0 should be interpreted as:

```text
a local 6:6 edge-class calibration
```

not yet as:

```text
a global fullerene-symmetry diagnostic
```

BMS-FU01b asks:

```text
Does the real-over-null result survive when the C60 reference core is selected
in different, explicitly controlled ways?
```

Internal working image:

```text
FU01 fand eine echte Nahtstelle im Fußball.
FU01b fragt, ob auch andere Nähte und verteilte Muster tragen.
```

---

## 2. Relation to BMS-FU01

BMS-FU01 result summary:

```text
input_graph_valid: true
warnings: 0

node_count: 60
edge_count: 90
face_count: 32
pentagon_count: 12
hexagon_count: 20

edge_type_counts:
  5_6: 60
  6_6: 30
```

BMS-FU01 showed:

```text
degree_preserving_rewire:
  real_exceeds_tested_null_family: 31

edge_class_shuffle:
  real_exceeds_tested_null_family: 15

core_seeded_decoy:
  null_reproduces_core_behavior: 38
```

Interpretation:

```text
The diagnostic detects known C60 edge-class/core placement beyond
degree-preserving rewires, while core-seeded decoys show that broad
core-containment readouts are cheap.
```

FU01b tightens this by testing whether the conclusion is robust to the selected core.

---

## 3. Working question

Main question:

```text
Is the C60 structure-information signal robust under alternative reference-core
selection rules?
```

Sub-questions:

```text
1. Does the local 6:6 patch core reproduce the FU01-v0 result?

2. Does a symmetry-distributed 6:6 core show similar real-over-null separation?

3. Does a pentagon-boundary / 5:6 motif core behave differently?

4. Do random balanced 6:6 cores show high variance?

5. Which readouts are stable across core rules, and which are artifacts of one
   deterministic local patch?
```

---

## 4. Recommended block label

```text
BMS-FU01b
```

Meaning:

```text
BMS = Bridge-readable Matter / Structure
FU  = Fullerene
01b = C60 core-selection sensitivity extension
```

Recommended output directory:

```text
runs/BMS-FU01b/c60_core_selection_sensitivity_open/
```

Recommended repo files:

```text
docs/BMS_FU01B_C60_CORE_SELECTION_SENSITIVITY_SPEC.md
docs/BMS_FU01B_RUNNER_FIELD_LIST.md
docs/BMS_FU01B_C60_CORE_SELECTION_RESULT_NOTE.md

data/bms_fu01b_c60_core_selection_config.yaml
scripts/run_bms_fu01b_c60_core_selection_sensitivity.py
```

---

## 5. Input artifacts

Use the validated C60 audit object from BMS-FU01:

```text
data/bms_fu01_c60_nodes.csv
data/bms_fu01_c60_edges.csv
data/bms_fu01_c60_faces.csv
data/bms_fu01_c60_graph_manifest.json
```

The runner must refuse to proceed if the builder manifest does not report:

```text
c60_valid: true
warnings: []
```

or if the loaded graph does not satisfy:

```text
node_count == 60
edge_count == 90
face_count == 32
pentagon_count == 12
hexagon_count == 20
edge_type_counts:
  5_6 == 60
  6_6 == 30
all node degrees == 3
```

---

## 6. Core variants

BMS-FU01b should evaluate multiple reference-core definitions against the same null families and construction families.

### 6.1 Core A — local 6:6 patch core

This reproduces FU01-v0.

```yaml
core_id: "local_6_6_patch_core"
mode: "first_sorted_edge_type"
edge_type: "6_6"
edge_count: 12
```

Purpose:

```text
Control / continuity with FU01-v0.
```

Expected:

```text
Should reproduce the FU01-v0 pattern:
strong over degree-preserving rewires,
partial over edge-class shuffle,
cheap under core-seeded decoy.
```

### 6.2 Core B — symmetry-distributed 6:6 core

Select 12 `6_6` edges distributed across the cage.

Recommended deterministic rule:

```text
Sort all 6:6 edges by edge id or source/target id.
Then take approximately evenly spaced indices across the 30 available 6:6 edges.
```

Example selection logic:

```python
indices = round(linspace(0, 29, 12))
```

Core config:

```yaml
core_id: "symmetry_distributed_6_6_core"
mode: "evenly_spaced_edge_type"
edge_type: "6_6"
edge_count: 12
```

Purpose:

```text
Test whether the 6:6 edge-class signal is local-patch dependent or
distributed across the fullerene cage.
```

Interpretation:

```text
If this core behaves similarly to the local patch core, FU01 supports a broader
6:6 edge-class placement signal.

If it weakens strongly, FU01-v0 was mostly a local patch effect.
```

### 6.3 Core C — pentagon-boundary / 5:6 motif core

Select 12 `5_6` edges belonging to pentagon-hexagon boundaries.

Since every C60 pentagon is isolated and surrounded by hexagons, 5:6 edges
represent pentagon boundary structure.

Recommended deterministic rule:

```yaml
core_id: "pentagon_boundary_5_6_core"
mode: "first_sorted_edge_type"
edge_type: "5_6"
edge_count: 12
```

Purpose:

```text
Test whether pentagon-boundary structure is similarly detectable.
```

Interpretation:

```text
If 5:6 cores behave differently from 6:6 cores, the diagnostic distinguishes
hexagon-hexagon seam structure from pentagon-boundary motif structure.
```

### 6.4 Core D — evenly distributed pentagon-boundary core

Select 12 `5_6` edges distributed across all 60 available 5:6 edges.

```yaml
core_id: "distributed_pentagon_boundary_5_6_core"
mode: "evenly_spaced_edge_type"
edge_type: "5_6"
edge_count: 12
```

Purpose:

```text
Distinguish local pentagon-boundary patch behavior from distributed
pentagon-boundary behavior.
```

### 6.5 Core E — random balanced edge-type cores

Generate repeated random cores with fixed composition.

Example:

```yaml
core_id: "random_balanced_6_6_5_6_core"
mode: "random_edge_type_balanced"
repeats: 30
edge_count: 12
edge_type_counts:
  6_6: 6
  5_6: 6
```

Purpose:

```text
Estimate how sensitive the readout is to arbitrary core choice.
```

Interpretation:

```text
High variance across random balanced cores indicates core-selection dependence.
Low variance indicates robust diagnostic behavior.
```

Recommended FU01b-v0 core set:

```text
A local_6_6_patch_core
B symmetry_distributed_6_6_core
C pentagon_boundary_5_6_core
D distributed_pentagon_boundary_5_6_core
```

Random balanced cores can be added in FU01c if runtime or output volume becomes large.

---

## 7. Null families

Use the same null families as FU01 for comparability.

### 7.1 Degree-preserving rewire

```text
Preserves node degree sequence.
Perturbs topology and edge-class placement.
```

Purpose:

```text
Tests whether the core is more than degree-3 regularity.
```

### 7.2 Edge-class shuffle

```text
Preserves topology and edge-type counts.
Shuffles 5:6 / 6:6 labels over edges.
```

Purpose:

```text
Tests whether the placement of edge classes matters.
```

### 7.3 Core-seeded decoy

```text
Preserves topology and edge-type counts.
Deliberately assigns the target core's preferred high-priority edge class to
the reference-core edges while preserving counts.
```

Purpose:

```text
Tests whether broad core-containment is cheap for the selected core.
```

Important:

```text
Core-seeded decoy must be generated separately for each core variant.
```

Otherwise the decoy would seed the wrong core and the interpretation would be invalid.

---

## 8. Construction families

Use FU01 construction families for comparability:

```yaml
construction_families:
  top_strength:
    enabled: true
    edge_counts: [12, 20, 30, 45, 60, 90]

  threshold:
    enabled: true
    thresholds: [0.80, 0.85, 0.90, 0.95, 1.00]

  mutual_knn:
    enabled: true
    k_values: [2, 3, 4, 6]

  maximum_spanning_tree:
    enabled: true

  graph_distance_shells:
    enabled: true
    shell_depths: [1, 2, 3]
```

Known limitation:

```text
Threshold and top-strength readouts are strongly tied to the two-weight design
6:6 = 1.00 and 5:6 = 0.85.
```

This is acceptable for FU01b as long as it is explicitly reported.

---

## 9. Metrics

Standard metrics:

```text
envelope_core_edge_containment
envelope_core_node_containment
edge_type_6_6_fraction
edge_type_5_6_fraction
connected_component_count
```

FU01b-specific metrics:

```text
core_variant_id
core_variant_mode
core_edge_type_composition
core_face_span_count
core_connected_component_count
core_hexagon_face_count
core_pentagon_face_count
```

Required summary grouping:

```text
by core_variant_id
by null_family
by metric_name
by construction_family
by construction_variant
```

Recommended additional summary:

```text
core_variant_summary.csv
```

Fields:

| field name | type | description |
|---|---:|---|
| `core_variant_id` | string | Core variant label. |
| `core_variant_mode` | string | Core selection mode. |
| `edge_count` | integer | Number of core edges. |
| `node_count` | integer | Number of core nodes. |
| `edge_type_counts` | string/json | Composition of `5_6` and `6_6` core edges. |
| `face_span_count` | integer | Number of unique faces touched by the core. |
| `pentagon_face_span_count` | integer | Number of unique pentagons touched by the core. |
| `hexagon_face_span_count` | integer | Number of unique hexagons touched by the core. |
| `connected_component_count` | integer | Number of connected components within the core. |
| `selection_rule` | string | Human-readable selection rule. |

---

## 10. Expected outputs

Recommended output directory:

```text
runs/BMS-FU01b/c60_core_selection_sensitivity_open/
```

Expected files:

```text
bms_fu01b_nodes_resolved.csv
bms_fu01b_edges.csv
bms_fu01b_faces.csv
bms_fu01b_core_variants.csv
bms_fu01b_reference_core_edges.csv
bms_fu01b_core_metrics.csv
bms_fu01b_envelope_metrics.csv
bms_fu01b_real_vs_null_summary.csv
bms_fu01b_core_variant_summary.csv
bms_fu01b_null_family_inventory.csv
bms_fu01b_run_manifest.json
bms_fu01b_warnings.json
bms_fu01b_config_resolved.yaml
```

---

## 11. Interpretation patterns

### Pattern A — all 6:6 cores beat degree rewires

Allowed interpretation:

```text
The diagnostic is robustly sensitive to 6:6 edge-class placement beyond simple
degree-3 regularity.
```

### Pattern B — local 6:6 core strong, distributed 6:6 core weak

Allowed interpretation:

```text
FU01-v0 was mainly a local H-H patch effect. The current diagnostic is not yet
a global 6:6 cage-organization marker.
```

### Pattern C — 5:6 pentagon cores behave differently from 6:6 cores

Allowed interpretation:

```text
The diagnostic distinguishes hexagon-hexagon seam structure from
pentagon-boundary structure.
```

### Pattern D — edge-class shuffle reproduces all cores

Allowed interpretation:

```text
The readout is mostly edge-type-count driven and not a reliable placement
specificity marker.
```

### Pattern E — core-seeded decoy reproduces broad containment for all cores

Allowed interpretation:

```text
Broad core-containment remains cheap under deliberate seeding. Only
decoy-resistant selective readouts should be treated as informative.
```

---

## 12. Claim boundary

Allowed:

```text
BMS-FU01b tests whether the BMS-FU01 C60 result is robust under alternative
reference-core selection rules, including local, distributed, 6:6, and 5:6
core variants.
```

Allowed after positive result:

```text
BMS-FU01b supports that the C60 diagnostic is not merely an artifact of one
deterministic local 6:6 patch core.
```

Allowed after core dependence:

```text
BMS-FU01b shows that the C60 result is core-selection dependent and should be
interpreted as a local edge-class calibration rather than a global
fullerene-symmetry diagnostic.
```

Not allowed:

```text
C60 proves emergent spacetime.
The bridge recognizes molecules.
A physical metric has been recovered.
Fullerene symmetry is proven as spacetime structure.
Quantum chemistry has been reproduced.
```

---

## 13. Recommended immediate implementation

Create:

```text
data/bms_fu01b_c60_core_selection_config.yaml
scripts/run_bms_fu01b_c60_core_selection_sensitivity.py
docs/BMS_FU01B_RUNNER_FIELD_LIST.md
```

Implementation should reuse FU01 runner logic where possible, with one key change:

```text
loop over core variants first,
then run metrics and nulls per core variant.
```

Pseudo-flow:

```text
load validated C60 graph
build core variants
for each core variant:
    compute real metrics
    generate nulls for that core variant
    compute null metrics
    summarize real-vs-null
write combined summary with core_variant_id columns
```

Critical implementation requirement:

```text
core_seeded_decoy must be conditioned on the current core_variant_id.
```

---

## 14. Minimal commit plan

Commit the specification first:

```bash
cd ~/Downloads/deBroglie_Kaster_Theorie/quantum-spacetime-bridge

cp ~/Downloads/BMS_FU01B_C60_CORE_SELECTION_SENSITIVITY_SPEC.md \
  docs/BMS_FU01B_C60_CORE_SELECTION_SENSITIVITY_SPEC.md

git add docs/BMS_FU01B_C60_CORE_SELECTION_SENSITIVITY_SPEC.md

git status --short

git commit -m "Add BMS-FU01b C60 core selection sensitivity specification"

git push
```

Do not implement before confirming that FU01 builder and FU01 runner commits are cleanly pushed.

---

## 15. Internal summary

```text
FU01-v0:
  The local 6:6 patch is real and degree-rewire resistant.

FU01b:
  Now test whether that remains true for other cuts through the C60 football.

Not the whole football yet.
First, test the seams.
```
