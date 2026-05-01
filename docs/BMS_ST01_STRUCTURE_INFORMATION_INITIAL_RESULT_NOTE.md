# BMS-ST01 — Structure Information Specificity Initial Result Note

Date: 2026-05-01  
Project: Gravitation und RaumZeit / Quantum-Spacetime-Bridge  
Recommended repo target: `docs/BMS_ST01_STRUCTURE_INFORMATION_INITIAL_RESULT_NOTE.md`  
Status: Initial result note for BMS-ST01 structure-information diagnostic

---

## 1. Purpose

BMS-ST01 transfers the BMC-15h structured-specificity diagnostic logic to the structure-information axis.

The tested input graph is not an isotope signature graph. It is a prebuilt relational structure graph from BMC-08a:

```text
data/baseline_relational_table_real.csv
data/node_metadata_real.csv
data/bmc08_dataset_manifest.json
```

The central question is:

```text
Do structure / topology families carry relational information that remains
detectable under BMC-15h-style structured null controls?
```

Internal working image:

```text
Isotope testeten den Takt.
ST01 testet die Architektur.
```

---

## 2. Input semantics

The real edge table already contains pairwise similarity edges.

Dataset manifest:

```text
dataset_id: BMC08a_realdata_v1
node_semantics: single physical instances from ring/cavity/membrane block
edge_semantics: pairwise similarity between standardized feature vectors
feature_set:
  feature_mode_frequency
  feature_length_scale
  feature_shape_factor
  feature_spectral_index
weight_rule:
  1 / (1 + euclidean_distance(z-scored features))
shell_rule:
  family shell: RING=0, CAVITY=1, MEMBRANE=2
record_count: 19
```

Thus, BMS-ST01 operates directly on a transparent relational structure graph.

---

## 3. Run context

Runner:

```text
scripts/run_bms_st01_structure_information_specificity.py
```

Config:

```text
data/bms_st01_structure_information_config.yaml
```

Output directory:

```text
runs/BMS-ST01/structure_information_specificity_open/
```

Reference-core mode:

```text
family_balanced_within_family_top_edges
```

Input edge table:

```text
data/baseline_relational_table_real.csv
```

Input node metadata:

```text
data/node_metadata_real.csv
```

Node count:

```text
19
```

Real edge count:

```text
171
```

Reference core edge count:

```text
9
```

Null families:

```text
degree_weight_preserving_rewire: 50
feature_structured_shuffle:     50
core_seeded_decoy:              50
```

Object count:

```text
151
```

Warnings:

```text
0
```

The run completed cleanly.

---

## 4. Row counts

```text
core_metrics:              5134
edges:                    25821
envelope_metrics:         10268
family_summary:               3
nodes_resolved:              19
null_family_inventory:      150
real_vs_null_summary:       204
reference_core_edges:         9
warnings:                     0
```

---

## 5. Summary labels

The real-vs-null summary contains 204 rows.

Interpretation labels:

```text
null_reproduces_metric_behavior: 68
null_reproduces_core_behavior:   56
mixed_family_dependent_result:   18
real_exceeds_tested_null_family: 62
```

Breakdown by null family:

```text
degree_weight_preserving_rewire:
  null_reproduces_metric_behavior: 17
  real_exceeds_tested_null_family: 32
  mixed_family_dependent_result: 6
  null_reproduces_core_behavior: 13

feature_structured_shuffle:
  null_reproduces_metric_behavior: 34
  real_exceeds_tested_null_family: 13
  mixed_family_dependent_result: 5
  null_reproduces_core_behavior: 16

core_seeded_decoy:
  null_reproduces_metric_behavior: 17
  null_reproduces_core_behavior: 27
  mixed_family_dependent_result: 7
  real_exceeds_tested_null_family: 17
```

---

## 6. Reference core

The BMS-ST01 reference core selects three strongest within-family structure edges per family.

### RING

```text
ring_abs_p_2 -- ring_abs_p_3
  weight = 0.42786684973
  labels: p=2.0 -- p=3.0
  shape: 1 -> 1
  spectral: 2 -> 3

ring_abs_p_1 -- ring_abs_p_2
  weight = 0.303362112301
  labels: p=1.0 -- p=2.0
  shape: 1 -> 1
  spectral: 1 -> 2

ring_abs_p_1 -- ring_abs_p_3
  weight = 0.225015275779
  labels: p=1.0 -- p=3.0
  shape: 1 -> 1
  spectral: 1 -> 3
```

Interpretation:

```text
The RING reference core is the complete three-node internal ring graph over
p=1,2,3. It is ordered by spectral proximity: 2--3 and 1--2 are stronger
than 1--3.
```

### CAVITY

```text
cavity_2_1_2 -- cavity_2_2_1
  weight = 0.692205423461
  modes: (2,1,2) -- (2,2,1)
  shape: 2 -> 2
  spectral: 6 -> 7

cavity_2_2_1 -- cavity_2_2_2
  weight = 0.690680452834
  modes: (2,2,1) -- (2,2,2)
  shape: 2 -> 2
  spectral: 7 -> 8

cavity_2_1_1 -- cavity_2_1_2
  weight = 0.684788127883
  modes: (2,1,1) -- (2,1,2)
  shape: 2 -> 2
  spectral: 5 -> 6
```

Interpretation:

```text
The CAVITY reference core is a high-weight local mode-neighborhood chain in
the spectral range 5--8. It is not a random set of cavity nodes; it follows
adjacent or near-adjacent mode/spectral organization.
```

### MEMBRANE

```text
membrane_0_3 -- membrane_2_2
  weight = 0.692856108785
  modes: (0,3) -- (2,2)
  shape: 1 -> 1
  spectral: 8 -> 7

membrane_0_2 -- membrane_2_1
  weight = 0.68288636872
  modes: (0,2) -- (2,1)
  shape: 1 -> 1
  spectral: 4 -> 3

membrane_1_2 -- membrane_3_1
  weight = 0.662218910223
  modes: (1,2) -- (3,1)
  shape: 1 -> 1
  spectral: 6 -> 5
```

Interpretation:

```text
The MEMBRANE reference core links mode pairs with nearby spectral indices
and equal shape factor. It appears as a set of local mode-neighborhood
relations rather than a single linear chain.
```

---

## 7. Befund

BMS-ST01 gives a mixed but informative first structure-information result.

The real graph frequently exceeds degree-/weight-preserving rewires:

```text
degree_weight_preserving_rewire:
  real_exceeds_tested_null_family: 32
```

This indicates that the real structure graph is not simply reproduced by randomly assigning the same weight multiset to different node pairs.

However, feature-structured shuffles reproduce a substantial amount of behavior:

```text
feature_structured_shuffle:
  null_reproduces_metric_behavior: 34
  null_reproduces_core_behavior: 16
```

Core-seeded decoys also reproduce a substantial amount:

```text
core_seeded_decoy:
  null_reproduces_core_behavior: 27
  real_exceeds_tested_null_family: 17
```

Thus:

```text
The structure graph contains non-random local organization, but a substantial
part of the signal is family-structured or cheap to reproduce by seeded-core
controls.
```

Internal working image:

```text
Die Architektur ist nicht nur Rauschen.
Aber ein Teil des Gerüsts ist mit Familienetiketten und Attrappen schon gut
nachbaubar.
```

---

## 8. Interpretation

The reference core itself is meaningful:

```text
RING:
  complete p=1,2,3 internal neighborhood ordered by spectral distance.

CAVITY:
  strong local mode-neighborhood chain in spectral range 5--8.

MEMBRANE:
  local mode-neighborhood pairings with nearby spectral indices.
```

This is stronger than a mere node-label recovery statement.

However, the real-vs-null result shows that the present readout is not fully specific.

Conservative interpretation:

```text
BMS-ST01 provides a construction-qualified structure-information indication:
the real structure graph often exceeds degree-/weight-preserving rewires and
its reference core follows interpretable within-family spectral/mode
neighborhoods. At the same time, feature-structured shuffles and core-seeded
decoys reproduce substantial parts of the behavior, so the result should not
be used as standalone specificity evidence.
```

Short internal version:

```text
Struktur trägt etwas.
Aber Familie trägt viel mit.
```

---

## 9. Comparison with BMS-IS01 and BMS-IS01b

### BMS-IS01

```text
same-isotope cross-run stability core
strong edge-containment signal
node containment cheap
```

### BMS-IS01b

```text
same-isotope cross-run links excluded
family-balanced different-isotope core
null families frequently reproduce core behavior
stronger isotope-order specificity not supported
```

### BMS-ST01

```text
family-balanced within-structure core
interpretable spectral/mode neighborhoods
real graph often exceeds degree-/weight rewires
feature-structured and seeded controls reproduce substantial behavior
```

Combined lesson:

```text
Run-stability, isotope-order, and structure-information are distinct axes.
Structure information appears more promising than the family-balanced isotope
order result, but remains construction-qualified and family-dependent.
```

---

## 10. Hypothesis

The current structure graph carries two intertwined signals:

1. coarse family structure:
   ```text
   RING / CAVITY / MEMBRANE labels and shell structure
   ```

2. local within-family spectral/mode neighborhood structure:
   ```text
   nearby spectral indices and related mode labels form high-weight local edges
   ```

Working hypothesis:

```text
Structure information is present primarily as local within-family spectral /
mode-neighborhood organization, but the current readouts still mix this signal
with coarse family separability.
```

This suggests that the next diagnostic should separate:

```text
family separability
within-family local ordering
cross-family bridge edges
```

---

## 11. Open gaps

1. The current reference core is within-family only.  
   It does not yet test whether cross-family bridge edges carry meaningful structure information.

2. Feature-structured shuffle reproduces substantial behavior.  
   This indicates that coarse family structure explains a large part of the result.

3. Core-seeded decoy reproduction is substantial.  
   Broad containment should not be used as standalone specificity evidence.

4. The metric set includes family purity and cross-family fraction, but the current summary is global.  
   A per-family readout would clarify which family drives the signal.

5. The input graph has only 19 nodes.  
   Small graph effects and family-size imbalance should be considered.

---

## 12. Claim boundary

Allowed statement:

```text
BMS-ST01 provides a mixed but informative first structure-information result:
the real structure graph often exceeds degree-/weight-preserving rewires, and
the selected reference core follows interpretable within-family spectral/mode
neighborhoods. However, feature-structured shuffles and core-seeded decoys
reproduce substantial parts of the behavior, so the result is
construction-qualified and not standalone specificity evidence.
```

Short allowed statement:

```text
BMS-ST01 supports structure-sensitive organization in a construction-qualified
sense, but not a standalone structure-specificity claim.
```

Not allowed:

```text
Structure information proves emergent spacetime.
The bridge recognizes geometry.
A physical metric has been recovered.
Ring/cavity/membrane structure is proven to encode spacetime.
```

---

## 13. Recommended next step

Recommended next block:

```text
BMS-ST01b — Structure Information Decomposition
```

Purpose:

```text
Separate coarse family structure from within-family local spectral/mode
ordering and from cross-family bridge behavior.
```

Recommended diagnostics:

```text
1. within-family-only diagnostic:
   evaluate each family separately.

2. cross-family-only diagnostic:
   test whether RING-CAVITY, RING-MEMBRANE, and CAVITY-MEMBRANE edges carry
   nontrivial bridge structure.

3. family-label-permutation control:
   preserve weights but scramble family labels to test dependence on family shell.

4. per-family reference-core summary:
   report core-edge containment separately for RING, CAVITY, MEMBRANE.

5. cross-family bridge core:
   select strongest cross-family edges and test whether they survive nulls.
```

Recommended result-note target for this run:

```text
docs/BMS_ST01_STRUCTURE_INFORMATION_INITIAL_RESULT_NOTE.md
```

Recommended next spec:

```text
docs/BMS_ST01B_STRUCTURE_INFORMATION_DECOMPOSITION_SPEC.md
```

---

## 14. Minimal commit plan

Commit this result note separately from large run outputs:

```bash
cd ~/Downloads/deBroglie_Kaster_Theorie/quantum-spacetime-bridge

git add docs/BMS_ST01_STRUCTURE_INFORMATION_INITIAL_RESULT_NOTE.md

git status --short

git commit -m "Add BMS-ST01 structure information result note"

git push
```

If the BMS-ST01 runner/config/spec/field-list have not yet been committed, commit them together:

```bash
git add \
  data/bms_st01_structure_information_config.yaml \
  scripts/run_bms_st01_structure_information_specificity.py \
  docs/BMS_ST01_STRUCTURE_INFORMATION_DIAGNOSTIC_SPEC.md \
  docs/BMS_ST01_RUNNER_FIELD_LIST.md \
  docs/BMS_ST01_STRUCTURE_INFORMATION_INITIAL_RESULT_NOTE.md

git status --short

git commit -m "Add BMS-ST01 structure information diagnostic"

git push
```

Run outputs should only be committed deliberately after checking file size and repository policy.
