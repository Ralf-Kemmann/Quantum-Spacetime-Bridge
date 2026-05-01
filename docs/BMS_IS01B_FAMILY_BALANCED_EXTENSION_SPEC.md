# BMS-IS01b — Family-Balanced Matter Signature Specificity Diagnostic

Date: 2026-05-01  
Project: Gravitation und RaumZeit / Quantum-Spacetime-Bridge  
Recommended repo target: `docs/BMS_IS01B_FAMILY_BALANCED_EXTENSION_SPEC.md`  
Status: Extension specification after BMS-IS01 initial result

---

## 1. Purpose

BMS-IS01 produced a technically clean first isotope / structure specificity diagnostic.

The key result was:

```text
The first BMS-IS01 reference core is a within-family run-stability core:
it links the same isotope across different run-weighting variants.
```

This is useful, but it does not yet answer the stronger matter-signature question:

```text
Is there stable relational organization within each isotope family beyond
same-isotope cross-run identity links?
```

BMS-IS01b therefore introduces a family-balanced reference-core definition and an optional exclusion rule for same-isotope cross-run edges.

Internal working image:

```text
IS01 fand: derselbe Knopf taucht über Run-Gewichtungen stabil wieder auf.

IS01b fragt:
  Wenn wir diese offensichtlichen Wiedererkennungs-Kanten herausnehmen,
  bleibt dann innerhalb jeder Familie noch eine belastbare Kantenordnung übrig?
```

---

## 2. Relation to BMS-IS01

BMS-IS01:

```text
global top-6 reference core
dominated by same-isotope cross-run links
strong edge-containment specificity under selective constructions
cheap node containment
```

BMS-IS01b:

```text
family-balanced reference core
optional exclusion of same-isotope cross-run edges
separate family-level readouts for H, C, Sr
focus on edge containment and local relational embedding
```

The goal is not to replace BMS-IS01, but to refine its interpretation.

---

## 3. Working questions

Main question:

```text
Does each isotope family contain a stable local relational edge structure
beyond same-isotope cross-run stability?
```

Sub-questions:

```text
1. Which families retain core-edge specificity after family balancing?

2. Does hydrogen behave differently from carbon or strontium?

3. Are heavy-isotope families more stable because their signature vectors are
   closer together, or less specific because nulls can reproduce them?

4. Does excluding same-isotope cross-run edges reveal isotope-order or
   mass-order structure?

5. Does core-seeded decoy reproduction remain restricted to broad constructions,
   or does it also reproduce selective local family-balanced cores?
```

---

## 4. Recommended block label

```text
BMS-IS01b
```

Meaning:

```text
BMS = de Broglie Matter Signature
IS  = Isotope / Structure
01b = family-balanced refinement of the first structured-specificity diagnostic
```

Recommended output directory:

```text
runs/BMS-IS01b/family_balanced_specificity_open/
```

Recommended repo files:

```text
docs/BMS_IS01B_FAMILY_BALANCED_EXTENSION_SPEC.md
docs/BMS_IS01B_RUNNER_FIELD_LIST.md
docs/BMS_IS01B_FAMILY_BALANCED_RESULT_NOTE.md

data/bms_is01b_family_balanced_config.yaml
scripts/run_bms_is01b_family_balanced_specificity.py
```

---

## 5. Reference-core definition

BMS-IS01 used a global top-strength reference core.

BMS-IS01b should use a family-balanced reference core.

Recommended default:

```yaml
reference_core:
  mode: "family_balanced_top_edges"
  edges_per_family: 3
  exclude_same_isotope_cross_run: true
  fallback_allow_same_isotope_if_needed: false
```

Interpretation:

| field name | type | description |
|---|---:|---|
| `mode` | string | Reference-core selection rule. |
| `edges_per_family` | integer | Number of reference-core edges selected within each family. |
| `exclude_same_isotope_cross_run` | boolean | If true, remove edges linking the same isotope label across different run variants. |
| `fallback_allow_same_isotope_if_needed` | boolean | If true, same-isotope edges may be used if a family has too few eligible edges. For a strict diagnostic this should be false. |

Expected first-pass reference core size:

```text
3 families × 3 edges per family = 9 reference-core edges
```

If a family has too few eligible edges, warnings should be emitted and the actual core size should be reported in the manifest.

---

## 6. Edge eligibility rule

Given two nodes A and B, an edge is excluded from the strict family-balanced core if:

```text
A.family_id == B.family_id
A.isotope == B.isotope
A.run_id != B.run_id
```

This targets the BMS-IS01 pattern where the strongest global core edges were same-isotope links across run variants.

Allowed edges after exclusion include:

```text
same family, different isotope
different run, different isotope
same run, different isotope
```

This focuses the diagnostic on family-internal relational ordering rather than run-stability identity matching.

---

## 7. Construction families

Use the same construction families as BMS-IS01:

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

Depending on resulting reference-core size, `top_edges_6` may become smaller than the core itself. This is acceptable as a selectivity test, but should be interpreted carefully.

---

## 8. Null families

Retain all three null families from BMS-IS01:

```text
degree_weight_preserving_rewire
feature_structured_shuffle
core_seeded_decoy
```

Interpretation boundary:

```text
degree_weight_preserving_rewire:
  tests whether edge structure is just weight distribution over pairs.

feature_structured_shuffle:
  tests whether family-preserving vector reassignment reproduces local order.

core_seeded_decoy:
  tests whether family-balanced core behavior can be cheaply inserted.
```

---

## 9. Required outputs

Recommended output files:

```text
runs/BMS-IS01b/family_balanced_specificity_open/
  bms_is01b_nodes_resolved.csv
  bms_is01b_edges.csv
  bms_is01b_reference_core_edges.csv
  bms_is01b_core_metrics.csv
  bms_is01b_envelope_metrics.csv
  bms_is01b_real_vs_null_summary.csv
  bms_is01b_family_summary.csv
  bms_is01b_null_family_inventory.csv
  bms_is01b_run_manifest.json
  bms_is01b_warnings.json
  bms_is01b_config_resolved.yaml
```

---

## 10. Result interpretation structure

The result note should separate:

```text
Befund
Interpretation
Hypothesis
Open gap
Claim boundary
```

Key diagnostic split:

```text
1. family-balanced core-edge containment
2. family-balanced core-node containment
3. null reproduction under broad constructions
4. selective local constructions
5. family-specific contributions
```

---

## 11. Possible outcomes

### Pattern A — family-balanced core remains specific

```text
The real graph exceeds all null families under selective core-edge containment
even after same-isotope cross-run edges are excluded.
```

Interpretation:

```text
This supports a stronger construction-qualified indication that isotope
families contain nontrivial relational edge organization beyond run-stability
identity links.
```

### Pattern B — family-balanced core collapses

```text
Null families reproduce most family-balanced core-edge behavior.
```

Interpretation:

```text
The BMS-IS01 signal was mostly run-stability / same-isotope identity matching,
not a stronger isotope-order structure.
```

### Pattern C — mixed family-dependent result

```text
Hydrogen, carbon, and strontium behave differently.
```

Interpretation:

```text
Matter-side relational structure may depend on family size, mass spacing,
or score-vector degeneracy. A per-family analysis is required.
```

---

## 12. Claim boundary

Allowed:

```text
BMS-IS01b tests whether the BMS-IS01 matter-signature core remains informative
after excluding same-isotope cross-run identity links and balancing the
reference core across isotope families.
```

Allowed after positive result:

```text
BMS-IS01b supports a construction-qualified indication of family-internal
relational edge structure beyond same-isotope run-stability links.
```

Allowed after collapse:

```text
BMS-IS01b shows that the first BMS-IS01 core was primarily a run-stability
core and should not be interpreted as broader isotope-order specificity.
```

Not allowed:

```text
Isotopes prove emergent geometry.
The bridge recognizes elements.
Matter identity is transferred to geometry.
A physical metric has been recovered.
Carbon structure has been demonstrated from this run alone.
```

---

## 13. Recommended first run

Recommended command:

```bash
cd ~/Downloads/deBroglie_Kaster_Theorie/quantum-spacetime-bridge

python scripts/run_bms_is01b_family_balanced_specificity.py \
  --config data/bms_is01b_family_balanced_config.yaml
```

Then read out:

```bash
python - <<'PY'
from pathlib import Path
import csv, json
from collections import Counter, defaultdict

root = Path("runs/BMS-IS01b/family_balanced_specificity_open")

manifest = json.loads((root / "bms_is01b_run_manifest.json").read_text())
warnings = json.loads((root / "bms_is01b_warnings.json").read_text())

print(json.dumps(manifest, indent=2))
print("\nwarnings:", len(warnings))
for w in warnings:
    print(w["severity"], "-", w["message"])

rows = list(csv.DictReader((root / "bms_is01b_real_vs_null_summary.csv").open()))

print("\nsummary rows:", len(rows))

print("\nInterpretation labels:")
for k, v in Counter(r["interpretation_label"] for r in rows).items():
    print(" ", k + ":", v)

print("\nBy null family:")
byfam = defaultdict(Counter)
for r in rows:
    byfam[r["null_family"]][r["interpretation_label"]] += 1

for fam, c in byfam.items():
    print("\n" + fam)
    for k, v in c.items():
        print(" ", k + ":", v)
PY
```

Also inspect the reference core:

```bash
python - <<'PY'
from pathlib import Path
import csv

root = Path("runs/BMS-IS01b/family_balanced_specificity_open")

with (root / "bms_is01b_reference_core_edges.csv").open(newline="", encoding="utf-8") as f:
    for r in csv.DictReader(f):
        print(
            r["family_id"],
            r["source"],
            "--",
            r["target"],
            "weight=",
            r["weight"],
            "excluded_same_isotope_cross_run=",
            r["excluded_same_isotope_cross_run"],
        )
PY
```

---

## 14. Minimal commit plan

Commit code/config/docs separately from large run outputs:

```bash
cd ~/Downloads/deBroglie_Kaster_Theorie/quantum-spacetime-bridge

git add \
  data/bms_is01b_family_balanced_config.yaml \
  scripts/run_bms_is01b_family_balanced_specificity.py \
  docs/BMS_IS01B_FAMILY_BALANCED_EXTENSION_SPEC.md \
  docs/BMS_IS01B_RUNNER_FIELD_LIST.md

git status --short

git commit -m "Add BMS-IS01b family-balanced matter specificity diagnostic"

git push
```
