# BMS-ST01 — Structure Information Diagnostic Specification

Date: 2026-05-01  
Project: Gravitation und RaumZeit / Quantum-Spacetime-Bridge  
Recommended repo target: `docs/BMS_ST01_STRUCTURE_INFORMATION_DIAGNOSTIC_SPEC.md`  
Status: Specification and inventory plan

---

## 1. Purpose

BMS-IS01 and BMS-IS01b tested isotope-side matter-signature structure.

Their combined lesson was:

```text
BMS-IS01 supports run-stability:
  same-isotope signature neighborhoods remain stable across run-weighting variants.

BMS-IS01b weakens the stronger isotope-order specificity interpretation:
  after excluding same-isotope cross-run links and enforcing a family-balanced core,
  null families frequently reproduce core behavior.
```

The next question is the structure-information axis.

BMS-ST01 asks:

```text
Do structure / topology variants carry relational information that remains
detectable under BMC-15h-style structured-specificity diagnostics?
```

Internal working image:

```text
Isotope fragten:
  Hört die Bridge den anderen Takt?

BMS-ST01 fragt:
  Bleibt Architektur als Kantenordnung sichtbar,
  oder reicht schon grobe Family-Sortierung?
```

---

## 2. Relation to previous blocks

### BMC-15h

BMC-15h established a methodological pattern:

```text
Broad containment is cheap.
Selective local embedding is more informative.
Core-seeded decoys expose which readouts are cheaply reproducible.
```

### BMS-IS01

BMS-IS01 transferred this logic to isotope matter signatures and found:

```text
same-isotope cross-run stability core
strong edge-containment signal
cheap node containment
```

### BMS-IS01b

BMS-IS01b excluded same-isotope cross-run edges and found:

```text
family-balanced isotope-order core often reproduced by nulls
broad isotope-order specificity not supported by this run
```

### BMS-ST01

BMS-ST01 now tests a different information axis:

```text
structure / topology / architecture
```

This is closer to the original project intuition that relation, topology, and robust local organization may be more relevant than object identity.

---

## 3. Working question

Main question:

```text
Does structure information survive as a relational edge pattern after
controlling for coarse family labels and cheap seeded cores?
```

Sub-questions:

```text
1. Do structural families such as Ring, Cavity, and Membrane form distinguishable
   relational neighborhoods?

2. Is the signal only family purity, or are there specific local edges that
   null families fail to reproduce?

3. Does a feature-structured null reproduce most of the structure signal?

4. Can core-seeded decoys cheaply reproduce the selected structure core?

5. Which readout is informative:
   node containment, edge containment, family purity, or selective-local embedding?
```

---

## 4. Recommended block name

```text
BMS-ST01
```

Meaning:

```text
BMS = de Broglie Matter Signature / Bridge-readable Matter Structure
ST  = Structure / Topology
01  = first dedicated structure-information diagnostic
```

Recommended output directory:

```text
runs/BMS-ST01/structure_information_specificity_open/
```

Recommended repo files:

```text
docs/BMS_ST01_STRUCTURE_INFORMATION_DIAGNOSTIC_SPEC.md
docs/BMS_ST01_RUNNER_FIELD_LIST.md
docs/BMS_ST01_STRUCTURE_INFORMATION_RESULT_NOTE.md

data/bms_st01_structure_information_config.yaml
scripts/run_bms_st01_structure_information_specificity.py
```

---

## 5. Candidate input sources

The project already contains likely structure-information inputs from the real-data mapping line.

Likely files:

```text
data/baseline_relational_table_real.csv
data/node_metadata_real.csv
data/bmc08_dataset_manifest.json
```

Known or expected structure families:

```text
RING
CAVITY
MEMBRANE
```

Known metadata fields from previous inspection:

```text
node_id
shell_index
node_label
node_family
origin_tag
comment
feature_shape_factor
feature_spectral_index
```

Known or expected feature fields from earlier BMC-08 mapping:

```text
L_major_raw
L_minor_raw
m_ref_raw
feature_mode_frequency
feature_length_scale
feature_shape_factor
feature_spectral_index
```

The first task is to inspect and freeze the actual available headers before writing the final runner.

---

## 6. Minimal inventory commands

Run:

```bash
cd ~/Downloads/deBroglie_Kaster_Theorie/quantum-spacetime-bridge

ls -lh data/baseline_relational_table_real.csv data/node_metadata_real.csv data/bmc08_dataset_manifest.json 2>/dev/null || true
```

Header inspection:

```bash
python - <<'PY'
from pathlib import Path
import csv, json

for p in [
    Path("data/baseline_relational_table_real.csv"),
    Path("data/node_metadata_real.csv"),
]:
    print("\nFILE:", p)
    print("exists:", p.exists())
    if p.exists():
        with p.open(newline="", encoding="utf-8") as f:
            reader = csv.reader(f)
            header = next(reader, [])
            print("HEADER:")
            for i, h in enumerate(header):
                print(f"  {i}: {h!r}")
            print("FIRST_ROWS:")
            for _, row in zip(range(5), reader):
                print(" ", row[:len(header)])

manifest = Path("data/bmc08_dataset_manifest.json")
print("\nFILE:", manifest)
print("exists:", manifest.exists())
if manifest.exists():
    obj = json.loads(manifest.read_text(encoding="utf-8"))
    print(json.dumps(obj, indent=2)[:4000])
PY
```

Family count inspection:

```bash
python - <<'PY'
from pathlib import Path
import csv
from collections import Counter

p = Path("data/node_metadata_real.csv")
if not p.exists():
    raise SystemExit("missing data/node_metadata_real.csv")

with p.open(newline="", encoding="utf-8") as f:
    rows = list(csv.DictReader(f))

print("rows:", len(rows))
print("node_family:")
for k, v in Counter(r.get("node_family", "") for r in rows).items():
    print(" ", k, v)

print("\norigin_tag:")
for k, v in Counter(r.get("origin_tag", "") for r in rows).items():
    print(" ", k, v)
PY
```

This inventory determines whether BMS-ST01 can use the current real-data mapping directly.

---

## 7. Canonical node table

Recommended canonical input table after inventory:

```text
data/bms_st01_structure_nodes.csv
```

Field list:

| field name | type | description |
|---|---:|---|
| `node_id` | string | Unique structure node identifier. |
| `node_family` | string | Structure family label, e.g. `RING`, `CAVITY`, `MEMBRANE`. |
| `structure_label` | string | Human-readable structure label. |
| `origin_tag` | string | Source or construction origin tag. |
| `shell_index` | integer-like | Optional shell / layer index. |
| `feature_shape_factor` | float | Shape-factor feature. |
| `feature_spectral_index` | float | Spectral-index feature. |
| `feature_mode_frequency` | float | Mode-frequency proxy if available. |
| `feature_length_scale` | float | Length-scale proxy if available. |
| `L_major_raw` | float | Raw major length scale if available. |
| `L_minor_raw` | float | Raw minor length scale if available. |
| `m_ref_raw` | float | Raw mode/reference index if available. |
| `notes` | string | Source caveats or construction notes. |

If the current files already include all needed fields, the adapter can write this table directly.

---

## 8. Relational graph construction

Each structure node becomes a node in a relational graph.

Candidate signature vector:

```text
feature_shape_factor
feature_spectral_index
feature_mode_frequency
feature_length_scale
L_major_raw
L_minor_raw
m_ref_raw
```

The exact vector should be frozen after header inspection.

Recommended similarity:

```text
weight_ij = exp(-euclidean_distance(zscore(feature_vector_i), zscore(feature_vector_j)))
```

Recommended distance:

```text
distance_ij = euclidean_distance(zscore(feature_vector_i), zscore(feature_vector_j))
```

This mirrors BMS-IS01 while keeping structure-specific feature vectors.

---

## 9. Reference-core options

BMS-ST01 should avoid selecting only trivial same-family nearest neighbors unless that is exactly what is being tested.

Recommended first core mode:

```yaml
reference_core:
  mode: "family_balanced_top_edges"
  edges_per_family: 3
  within_family_only: true
```

Meaning:

```text
Select strongest internal structure-neighborhood edges separately within
RING, CAVITY, and MEMBRANE.
```

Recommended second core mode for later:

```yaml
reference_core:
  mode: "cross_family_bridge_edges"
```

Meaning:

```text
Select edges that connect different structure families, if any meaningful
bridge structure exists.
```

First run should use the within-family balanced core.

---

## 10. Null families

Use the same three diagnostic nulls:

```text
degree_weight_preserving_rewire
feature_structured_shuffle
core_seeded_decoy
```

Interpretation:

```text
degree_weight_preserving_rewire:
  Does the structure core survive random reassignment of weights to pairs?

feature_structured_shuffle:
  Does preserving node_family reproduce the signal?

core_seeded_decoy:
  Can the structure core be cheaply inserted?
```

Important:

```text
If feature_structured_shuffle reproduces the signal, the result may be mostly
coarse family structure rather than specific local architecture.
```

---

## 11. Construction families

Recommended first-pass settings:

```yaml
construction_families:
  top_strength:
    enabled: true
    edge_counts: [6, 10, 15, 21, 34]
  threshold:
    enabled: true
    thresholds: [0.50, 0.65, 0.80, 0.90, 0.95]
  mutual_knn:
    enabled: true
    k_values: [2, 3, 4, 6, 10]
  maximum_spanning_tree:
    enabled: true
```

These can be adjusted after observing node count and weight distribution.

---

## 12. Required outputs

Recommended outputs:

```text
runs/BMS-ST01/structure_information_specificity_open/
  bms_st01_nodes_resolved.csv
  bms_st01_edges.csv
  bms_st01_reference_core_edges.csv
  bms_st01_core_metrics.csv
  bms_st01_envelope_metrics.csv
  bms_st01_real_vs_null_summary.csv
  bms_st01_family_summary.csv
  bms_st01_null_family_inventory.csv
  bms_st01_run_manifest.json
  bms_st01_warnings.json
  bms_st01_config_resolved.yaml
```

---

## 13. Expected interpretation patterns

### Pattern A — structure core survives nulls

```text
Real graph strongly exceeds rewire, feature-structured shuffle, and seeded
decoys under selective local edge-containment readouts.
```

Interpretation:

```text
This would support a construction-qualified indication that structure features
carry local relational organization beyond coarse family sorting.
```

### Pattern B — feature-structured null reproduces core

```text
Feature-structured shuffle reproduces most core behavior.
```

Interpretation:

```text
The signal is mostly coarse structure-family information rather than specific
local architecture.
```

### Pattern C — core-seeded decoy reproduces broad but not selective readouts

```text
Broad containment is cheap; selective local edge containment remains informative.
```

Interpretation:

```text
Analogous to BMC-15h: broad containment should not be used as standalone
specificity evidence.
```

### Pattern D — all nulls reproduce core

```text
The selected structure core is not specific under current construction.
```

Interpretation:

```text
The current feature vector or reference-core rule is insufficient for a
structure-information claim.
```

---

## 14. Claim boundary

Allowed:

```text
BMS-ST01 tests whether structure-feature outputs contain local relational
organization beyond coarse family labels.
```

Allowed after positive selective result:

```text
BMS-ST01 supports a construction-qualified indication that structure
information is expressed in selective local relational edge patterns.
```

Allowed after null reproduction:

```text
BMS-ST01 shows that the tested structure readout is reproduced by structured
controls and should not be used as standalone specificity evidence.
```

Not allowed:

```text
Structure information proves emergent spacetime.
The bridge recognizes geometry.
Carbon architecture is proven from unrelated proxy data.
A physical metric has been recovered.
```

---

## 15. Recommended immediate next action

Run the inventory commands in Section 6.

After the headers are known, choose one of:

```text
A. use data/baseline_relational_table_real.csv directly
B. merge baseline_relational_table_real.csv with node_metadata_real.csv
C. rebuild a clean bms_st01_structure_nodes.csv adapter
```

Recommended next implementation files after inventory:

```text
data/bms_st01_structure_information_config.yaml
scripts/run_bms_st01_structure_information_specificity.py
docs/BMS_ST01_RUNNER_FIELD_LIST.md
```

---

## 16. Minimal commit plan

Commit this specification before implementation:

```bash
cd ~/Downloads/deBroglie_Kaster_Theorie/quantum-spacetime-bridge

git add docs/BMS_ST01_STRUCTURE_INFORMATION_DIAGNOSTIC_SPEC.md

git status --short

git commit -m "Add BMS-ST01 structure information diagnostic specification"

git push
```
