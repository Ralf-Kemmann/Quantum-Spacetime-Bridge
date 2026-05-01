# BMS-IS01 — Isotope and Structure Tests with BMC-15h-Style Specificity Diagnostics

Date: 2026-05-01  
Project: Gravitation und RaumZeit / Quantum-Spacetime-Bridge  
Recommended repo target: `docs/BMS_IS01_ISOTOPE_STRUCTURE_BMC15H_METHOD_PLAN.md`  
Status: Planning note / bridge from BMC-15h methodology to isotope and structure tests

---

## 1. Purpose

This note defines the next methodological step:

```text
Rerun or re-evaluate the existing isotope and structure tests using a
BMC-15h-style structured-specificity diagnostic, then discuss the combined
results across matter signatures and geometry-proxy behavior.
```

The goal is not to claim physical geometry from isotope or structure data.  
The goal is to ask whether matter-side signature structures show a comparable pattern of:

```text
local core behavior
construction sensitivity
structured-null reproducibility
cheap-decoy reproducibility
```

This extends the BMC-15h logic from geometry-proxy diagnostics to matter-information diagnostics.

Internal working image:

```text
BMC-15h fragte beim Geometrie-Proxy:
  Ist der Klunker echt lokal eingebettet,
  oder kann man ihn mit Attrappen billig nachbauen?

BMS-IS01 fragt bei Isotopen und Strukturvarianten:
  Bleibt eine materialsensitive Signatur lokal strukturiert,
  oder entsteht sie schon durch grobe Massenskala, Feature-Family oder
  künstlich gesetzte Seed-Strukturen?
```

---

## 2. Relation to existing project blocks

This block connects two previously separate project threads.

### Geometry-proxy thread

Relevant BMC-15 line:

```text
BMC-15e/f/g:
  envelope construction sensitivity and core robustness

BMC-15h-v1:
  degree-/weight-preserving rewires
  feature-structured shuffles
  construction-dependent local-core specificity

BMC-15h-v2:
  core-seeded decoys
  broad containment shown to be cheap
  selective local embedding remains most informative
```

Current BMC-15h summary:

```text
The compact core is not simply a rewire artifact. However, broad core
containment is not specific, because feature-structured and core-seeded
controls can reproduce it. The informative regime is selective local embedding.
```

### Matter-information thread

Relevant earlier matter-side tests include:

```text
generic de Broglie matter signatures
isotope variants
carbon isotope / carbon-structure variants
strontium isotope variants
planned iso-electronic BMS-IE01
```

Known isotope / structure axes:

```text
Hydrogen:
  light extreme / strong de-Broglie scale contrast

Carbon:
  structure carrier / chemistry and architecture axis

Strontium:
  heavier mass-scale anchor
```

Internal shorthand:

```text
Wasserstoff = Taktgeber extrem leicht
Kohlenstoff = Strukturträger
Strontium = schwerer Massenskalen-Anker
```

---

## 3. Working question

Main question:

```text
Do isotope and structure test outputs contain a relational local structure
that remains distinguishable under BMC-15h-style structured controls?
```

Sub-questions:

```text
1. Are isotope signatures mainly mass-scale ordered, or do they form
   nontrivial local relational neighborhoods?

2. Are carbon structure variants distinguishable as architecture-sensitive
   relational patterns rather than only as scalar score differences?

3. Do feature-preserving nulls reproduce the same local organization?

4. Do core-seeded decoys cheaply reproduce the same apparent signal?

5. Which readouts remain informative only under selective local constructions?
```

---

## 4. Proposed block name

Recommended block name:

```text
BMS-IS01
```

Meaning:

```text
BMS = de Broglie Matter Signature
IS  = Isotope / Structure
01  = first BMC-15h-style structured-specificity rerun
```

Recommended output directory:

```text
runs/BMS-IS01/isotope_structure_specificity_open/
```

Recommended docs:

```text
docs/BMS_IS01_ISOTOPE_STRUCTURE_BMC15H_METHOD_PLAN.md
docs/BMS_IS01_RUNNER_FIELD_LIST.md
docs/BMS_IS01_ISOTOPE_STRUCTURE_RESULT_NOTE.md
docs/BMS_IS01_COMBINED_DISCUSSION_NOTE.md
```

Recommended data/config/scripts:

```text
data/bms_is01_isotope_structure_config.yaml
scripts/run_bms_is01_isotope_structure_specificity.py
```

---

## 5. Method translation from BMC-15h

BMC-15h starts from a graph object and a reference core.

For BMS-IS01, isotope and structure outputs must first be converted into a comparable relational graph object.

### Matter-side table to graph object

Input rows may represent:

```text
species
isotope
structure variant
family
run condition
speed model
frequency mode
tau value
signature score
component scores
```

A relational graph can be built by treating each row or collapsed variant as a node.

Candidate node identity:

```text
node_id = species_or_variant_id + condition_id
```

Candidate edge weight:

```text
weight_ij = similarity(signature_vector_i, signature_vector_j)
```

Candidate distance:

```text
distance_ij = distance(signature_vector_i, signature_vector_j)
```

Possible vector components:

```text
lambda_db
energy
frequency_proxy
length_scale_score
energy_score
occupancy_score
signature_score
matter_sensitive_delta
```

For structure variants, add:

```text
feature_shape_factor
feature_spectral_index
structure_family
topology_label
```

The graph object should then be passed through BMC-15h-style construction families.

---

## 6. Construction families

Use the same conceptual construction families as BMC-15h:

```text
top_strength
threshold
mutual_knn
maximum_spanning_tree
```

Recommended first-pass settings:

```yaml
construction_families:
  top_strength:
    enabled: true
    edge_counts: [6, 10, 15, 21]
  threshold:
    enabled: true
    thresholds: [0.02, 0.05, 0.10, 0.20, 0.30]
  mutual_knn:
    enabled: true
    k_values: [2, 3, 4, 6]
  maximum_spanning_tree:
    enabled: true
```

The exact values should be adjusted after inspecting node count and weight distribution.

---

## 7. Null families

Use three BMC-15h-style nulls.

### 7.1 Degree-/weight-preserving rewire

Purpose:

```text
Tests whether apparent local organization is explained by coarse graph
statistics and weight distribution.
```

Interpretation:

```text
If real exceeds this null, the signal is not explained by degree/weight
structure alone.
```

### 7.2 Feature-structured shuffle

Purpose:

```text
Tests whether the apparent local organization is reproduced when coarse
families are preserved but local assignments are shuffled.
```

Possible family columns:

```text
element_symbol
isotope_family
structure_family
test_axis
speed_model
frequency_mode
tau
```

Recommended first choice:

```text
family_column = test_axis_or_structure_family
```

Interpretation:

```text
If this null reproduces the signal, the signal may be carried by coarse
family structure rather than by a specific local relational arrangement.
```

### 7.3 Core-seeded decoy

Purpose:

```text
Tests whether a compact local signature can be cheaply inserted.
```

Interpretation:

```text
If the decoy reproduces broad containment but not selective local behavior,
then broad containment is non-specific while selective local embedding remains
more informative.
```

---

## 8. Candidate readouts

BMS-IS01 should preserve the BMC-15h separation between broad containment and selective local embedding.

Recommended readouts:

```text
core_edge_retention
core_node_retention
envelope_core_edge_containment
envelope_core_node_containment
real_minus_null_mean
empirical_exceedance_fraction
interpretation_label
```

Matter-side additional readouts:

```text
family_purity
isotope_order_preservation
mass_order_preservation
structure_family_separation
signature_score_rank_stability
matter_sensitive_delta_rank_stability
```

Possible interpretation labels:

```text
real_exceeds_tested_null_family
null_reproduces_core_behavior
mixed_family_dependent_result
mass_scale_dominant_result
structure_sensitive_result
inconclusive_due_to_scope_or_warnings
```

---

## 9. Minimal inventory step

Before writing the runner, locate the existing isotope and structure outputs.

Recommended command:

```bash
cd ~/Downloads/deBroglie_Kaster_Theorie/quantum-spacetime-bridge

find . -type f \( \
  -iname '*isotope*.csv' -o \
  -iname '*isotope*.json' -o \
  -iname '*carbon*.csv' -o \
  -iname '*carbon*.json' -o \
  -iname '*strontium*.csv' -o \
  -iname '*strontium*.json' -o \
  -iname '*matter*signature*.csv' -o \
  -iname '*matter*signature*.json' \
\) | sort
```

Header inspection:

```bash
python - <<'PY'
from pathlib import Path
import csv

candidates = []
for p in Path(".").rglob("*"):
    if not p.is_file():
        continue
    name = p.name.lower()
    if not any(s in name for s in [
        "isotope", "carbon", "strontium", "matter_signature", "signature"
    ]):
        continue
    if p.suffix.lower() != ".csv":
        continue
    candidates.append(p)

for p in sorted(candidates):
    try:
        with p.open(newline="", encoding="utf-8") as f:
            header = next(csv.reader(f), [])
        print("\n", p)
        print(" ", header[:40])
    except Exception as e:
        print("ERR", p, e)
PY
```

This inventory determines whether the next step is:

```text
A. direct BMS-IS01 runner against existing CSV outputs
B. small adapter to normalize old output schemas
C. rerun old isotope/structure tests to produce clean canonical input tables
```

---

## 10. Recommended canonical input table

Recommended target after inventory:

```text
data/bms_is01_isotope_structure_nodes.csv
```

Field list:

| field name | type | description |
|---|---:|---|
| `node_id` | string | Unique node identifier for species / isotope / structure / condition. |
| `test_axis` | string | Main axis: `isotope`, `structure`, or `mixed`. |
| `family_id` | string | Coarse family label, e.g. `hydrogen_isotopes`, `carbon_structures`, `strontium_isotopes`. |
| `species_label` | string | Human-readable species or structure label. |
| `element_symbol` | string | Element symbol where applicable. |
| `isotope_mass_u` | float | Isotope or species mass in atomic mass units where applicable. |
| `structure_label` | string | Structure/topology label where applicable. |
| `condition_id` | string | Condition key, e.g. temperature/speed/frequency/tau setup. |
| `temperature_K` | float | Temperature used for thermal proxy. |
| `speed_model` | string | Speed model used in the source calculation. |
| `frequency_mode` | string | Frequency proxy used in the source calculation. |
| `tau` | float | Tau/window parameter if available. |
| `lambda_db` | float | de Broglie wavelength proxy where available. |
| `energy` | float | Kinetic or proxy energy where available. |
| `frequency_proxy` | float | Frequency proxy where available. |
| `length_scale_score` | float | Length-scale component of the matter signature. |
| `energy_score` | float | Energy-scale component of the matter signature. |
| `occupancy_score` | float | Occupancy/density component where available. |
| `signature_score` | float | Combined matter signature score. |
| `matter_sensitive_delta` | float | Deviation from mass-only or baseline ordering if available. |
| `feature_shape_factor` | float | Structure-shape feature where available. |
| `feature_spectral_index` | float | Spectral/index-like feature where available. |
| `notes` | string | Source, caveats, or transformation notes. |

---

## 11. Recommended output files

Recommended BMS-IS01 outputs:

```text
runs/BMS-IS01/isotope_structure_specificity_open/
  bms_is01_nodes_resolved.csv
  bms_is01_edges.csv
  bms_is01_core_metrics.csv
  bms_is01_envelope_metrics.csv
  bms_is01_real_vs_null_summary.csv
  bms_is01_family_summary.csv
  bms_is01_run_manifest.json
  bms_is01_warnings.json
  bms_is01_config_resolved.yaml
```

---

## 12. Discussion structure after running

The combined discussion should separate four levels.

### 12.1 Befund

```text
What survived under selective local constructions?
What was reproduced by feature-structured nulls?
What was reproduced by core-seeded decoys?
Where do isotope and structure tests differ?
```

### 12.2 Interpretation

```text
Does the matter-side signal look mainly mass-scale dominated?
Does structure/topology add a separable relational signature?
Do isotope and structure variants behave like distinct information axes?
```

### 12.3 Hypothesis

```text
Matter-side bridge-readable information may not be a single scalar signature.
It may separate into mass/wave-scale, coupling-scale, and structure/topology
components, each with different robustness under null families.
```

### 12.4 Open gap

```text
Does the matter-side relational structure survive more physically constrained
controls, such as iso-electronic systems or experimentally grounded molecular
families?
```

---

## 13. Claim boundary

Allowed:

```text
The BMS-IS01 rerun tests whether isotope and structure signatures contain
local relational organization beyond simple scalar score orderings.
```

Allowed after positive selective-local result:

```text
The result supports a construction-qualified indication that matter-side
signature structure is not exhausted by coarse mass or family ordering.
```

Allowed after null reproduction:

```text
The result shows that the tested matter-side readout is reproducible by
structured controls and should not be used as standalone specificity evidence.
```

Not allowed:

```text
Isotope signatures prove emergent geometry.
Carbon structure proves spacetime encoding.
Matter identity is transferred to geometry.
The bridge recognizes elements.
A physical metric has been recovered.
```

---

## 14. Recommended next command

Start with inventory only:

```bash
cd ~/Downloads/deBroglie_Kaster_Theorie/quantum-spacetime-bridge

find . -type f \( \
  -iname '*isotope*.csv' -o \
  -iname '*isotope*.json' -o \
  -iname '*carbon*.csv' -o \
  -iname '*carbon*.json' -o \
  -iname '*strontium*.csv' -o \
  -iname '*strontium*.json' -o \
  -iname '*matter*signature*.csv' -o \
  -iname '*matter*signature*.json' \
\) | sort
```

Then inspect CSV headers:

```bash
python - <<'PY'
from pathlib import Path
import csv

for p in sorted(Path(".").rglob("*.csv")):
    name = p.name.lower()
    if not any(s in name for s in [
        "isotope", "carbon", "strontium", "matter_signature", "signature"
    ]):
        continue
    try:
        with p.open(newline="", encoding="utf-8") as f:
            header = next(csv.reader(f), [])
        print("\n", p)
        print(" ", header[:60])
    except Exception as e:
        print("ERR", p, e)
PY
```

After this inventory, choose one of:

```text
A. build adapter from existing outputs
B. rerun old matter-signature tests into canonical BMS-IS01 input
C. start with carbon-structure only as a clean smoke test
```
