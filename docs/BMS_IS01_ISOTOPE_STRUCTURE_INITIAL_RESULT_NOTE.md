# BMS-IS01 — Isotope / Structure Specificity Initial Result Note

Date: 2026-05-01  
Project: Gravitation und RaumZeit / Quantum-Spacetime-Bridge  
Recommended repo target: `docs/BMS_IS01_ISOTOPE_STRUCTURE_INITIAL_RESULT_NOTE.md`  
Status: Initial result note for BMS-IS01 isotope / structure specificity diagnostic

---

## 1. Purpose

BMS-IS01 transfers the BMC-15h structured-specificity logic to the matter-signature side.

The working question is:

```text
Do isotope / structure matter-signature outputs contain a local relational
organization that remains distinguishable under BMC-15h-style null controls?
```

This run uses existing isotope scan outputs for:

```text
hydrogen isotopes
carbon isotopes
strontium isotopes
```

The run constructs a relational signature graph from matter-signature vectors, defines a compact reference core from the strongest real graph edges, and evaluates BMC-15h-style null families.

---

## 2. Run context

Runner:

```text
scripts/run_bms_is01_isotope_structure_specificity.py
```

Config:

```text
data/bms_is01_isotope_structure_config.yaml
```

Output directory:

```text
runs/BMS-IS01/isotope_structure_specificity_open/
```

Input table count:

```text
9
```

Node count:

```text
27
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

Real edge count:

```text
351
```

Reference core edge count:

```text
6
```

Warnings:

```text
0
```

---

## 3. Row counts

```text
core_metrics:              4832
edges:                    53001
envelope_metrics:          7248
family_summary:               3
nodes_resolved:              27
null_family_inventory:      150
real_vs_null_summary:       144
warnings:                     0
```

The run is technically clean and produced no warnings.

---

## 4. Summary labels

The real-vs-null summary contains 144 rows.

Interpretation labels:

```text
real_exceeds_tested_null_family: 81
null_reproduces_core_behavior:   19
mixed_family_dependent_result:   28
null_reproduces_metric_behavior: 16
```

Breakdown by null family:

```text
degree_weight_preserving_rewire:
  real_exceeds_tested_null_family: 34
  null_reproduces_core_behavior: 5
  mixed_family_dependent_result: 9

feature_structured_shuffle:
  real_exceeds_tested_null_family: 21
  mixed_family_dependent_result: 5
  null_reproduces_core_behavior: 6
  null_reproduces_metric_behavior: 16

core_seeded_decoy:
  real_exceeds_tested_null_family: 26
  null_reproduces_core_behavior: 8
  mixed_family_dependent_result: 14
```

---

## 5. Reference core

The reference core consists of six strongest real graph signature-neighborhood edges:

```text
carbon_isotopes__carbon_run_a__13c
  -- carbon_isotopes__carbon_run_c__13c
  weight = 0.6305070673405435

hydrogen_isotopes__hydrogen_run_a__2h
  -- hydrogen_isotopes__hydrogen_run_b__2h
  weight = 0.833472108776931

hydrogen_isotopes__hydrogen_run_a__3h
  -- hydrogen_isotopes__hydrogen_run_c__3h
  weight = 0.6305070673405435

strontium_isotopes__strontium_run_a__86sr
  -- strontium_isotopes__strontium_run_b__86sr
  weight = 0.992081747571468

strontium_isotopes__strontium_run_a__87sr
  -- strontium_isotopes__strontium_run_b__87sr
  weight = 0.7030301904066193

strontium_isotopes__strontium_run_a__88sr
  -- strontium_isotopes__strontium_run_c__88sr
  weight = 0.6305070673405435
```

Important observation:

```text
The reference core does not connect different element families. It consists of
within-family, same-isotope links across different run variants.
```

Thus, the first BMS-IS01 reference core should be interpreted primarily as a **run-stability / signature-consistency core**, not as an element-crossing matter cluster.

Internal working image:

```text
Der Materie-Klunker sitzt nicht quer zwischen H, C und Sr.
Er besteht aus Isotopen-Knöpfen, die über verschiedene Run-Gewichtungen hinweg
wieder ähnlich auftauchen.
```

---

## 6. Befund

The strongest real-over-null cases are concentrated in core-edge containment.

Representative strongest real-over-null cases:

```text
degree_weight_preserving_rewire
  envelope_core_edge_containment
  top_strength top_edges_6
  real = 1.0
  null_mean = 0.03
  real_minus_null_mean = 0.97
  empirical_exceedance_fraction = 0.0
  label = real_exceeds_tested_null_family

degree_weight_preserving_rewire
  envelope_core_edge_containment
  top_strength top_edges_10
  real = 1.0
  null_mean = 0.04
  real_minus_null_mean = 0.96
  empirical_exceedance_fraction = 0.0
  label = real_exceeds_tested_null_family

feature_structured_shuffle
  envelope_core_edge_containment
  top_strength top_edges_6
  real = 1.0
  null_mean ≈ 0.0567
  real_minus_null_mean ≈ 0.9433
  empirical_exceedance_fraction = 0.0
  label = real_exceeds_tested_null_family

core_seeded_decoy
  envelope_core_edge_containment
  top_strength top_edges_6
  real = 1.0
  null_mean = 0.13
  real_minus_null_mean = 0.87
  empirical_exceedance_fraction = 0.0
  label = real_exceeds_tested_null_family
```

The strongest null-reproduction cases are dominated by core-node containment and broader constructions:

```text
core_seeded_decoy
  envelope_core_node_containment
  mutual_knn k_10
  real = 1.0
  null_mean = 1.0
  real_minus_null_mean = 0.0
  empirical_exceedance_fraction = 1.0
  label = null_reproduces_core_behavior

degree_weight_preserving_rewire
  envelope_core_node_containment
  mutual_knn k_10
  real = 1.0
  null_mean = 1.0
  real_minus_null_mean = 0.0
  empirical_exceedance_fraction = 1.0
  label = null_reproduces_core_behavior

feature_structured_shuffle
  envelope_core_node_containment
  mutual_knn k_10
  real = 1.0
  null_mean = 1.0
  real_minus_null_mean = 0.0
  empirical_exceedance_fraction = 1.0
  label = null_reproduces_core_behavior
```

---

## 7. Interpretation

The initial BMS-IS01 result separates two readout regimes.

### 7.1 Core-node containment is weak / cheap

The null families often recover the same reference-core nodes, especially under broader constructions such as mutual-kNN with larger k or maximum-spanning-tree-like envelopes.

This means:

```text
Node recovery alone is not a specific matter-signature marker in this run.
```

Internal working image:

```text
Die Attrappen finden oft dieselben Knöpfe.
```

### 7.2 Core-edge containment is more informative

The real graph strongly exceeds all tested null families under selective edge-focused constructions, especially:

```text
top_strength top_edges_6
top_strength top_edges_10
threshold abs_weight_ge_0.5
low-k mutual_knn
maximum_spanning_tree for edge containment
```

This means:

```text
The specific relations between the reference-core nodes are harder to reproduce
than the presence of the nodes themselves.
```

Internal working image:

```text
Die Attrappen finden oft dieselben Knöpfe.
Aber sie verdrahten sie nicht so wie der reale Materiegraph.
```

---

## 8. Relation to BMC-15h

BMC-15h showed:

```text
Broad envelope containment is not specific.
Selective local embedding is more informative.
```

BMS-IS01 shows an analogous but matter-specific pattern:

```text
Core-node recovery is not specific.
Core-edge recovery is more informative.
```

Combined methodological lesson:

```text
The informative signal is not mere containment. It is the relational pattern
of how selected nodes are connected under selective local construction rules.
```

Project-internal bridge sentence:

```text
BMC-15h zeigte:
  bloßes Containment in breiten Envelopes ist nicht spezifisch.

BMS-IS01 zeigt:
  bloßes Wiederfinden derselben Materieknoten ist nicht spezifisch;
  spezifischer ist die reale Kantenordnung zwischen ihnen.
```

---

## 9. Hypothesis

The first BMS-IS01 run suggests that isotope matter signatures contain a stable within-family relational edge structure across run variants.

This should be interpreted conservatively:

```text
The observed reference core is not an element-crossing matter cluster. It is a
within-family run-stability core, linking the same isotope across different
signature-weighting variants.
```

Working hypothesis:

```text
Matter-side signature information may be more robustly expressed as stable
within-family relational edge structure than as isolated node identity.
```

More project-specific hypothesis:

```text
The matter-side bridge-relevant content is not the isotope label itself, but
the stability of relational signature neighborhoods across allowed run
weightings.
```

---

## 10. Open gap

This first BMS-IS01 run is a successful smoke test, but it is not yet a full structure test.

Open points:

1. The current reference core is dominated by same-isotope cross-run links.  
   This is useful as a run-stability diagnostic but does not yet test cross-family or architecture-sensitive structure.

2. Carbon appears only as a two-isotope family in the present input.  
   It should not be overinterpreted as a full carbon-structure test.

3. The current core definition selects the six strongest graph edges globally.  
   A family-balanced or axis-balanced core definition may be needed to compare hydrogen, carbon, and strontium more fairly.

4. Node containment is too cheap in this graph and should not be used as a main specificity readout.

5. A second BMS-IS01 variant should separate:
   - isotope stability across run variants,
   - mass-order structure within isotope families,
   - carbon architecture / structure variants, if suitable inputs exist,
   - iso-electronic controls from BMS-IE01 once available.

---

## 11. Claim boundary

Allowed statement:

```text
BMS-IS01 provides an initial construction-qualified indication that isotope
matter-signature outputs contain stable relational edge structure beyond simple
node recovery or coarse null reproduction.
```

More precise allowed statement:

```text
The first BMS-IS01 reference core is a within-family run-stability core:
it links the same isotope across different run-weighting variants. The
specific core edges are strongly suppressed in tested null families under
selective constructions, while core-node containment is frequently reproduced
and is therefore not a specific readout.
```

Not allowed:

```text
Isotope signatures prove emergent geometry.
The bridge recognizes elements.
Matter identity is transferred to geometry.
Carbon structure has been demonstrated from this run alone.
A physical metric has been recovered.
The reference core is a cross-element physical matter cluster.
```

---

## 12. Recommended next step

The next step should be a BMS-IS01b refinement rather than immediately escalating the claim.

Recommended target:

```text
BMS-IS01b — Family-Balanced Matter Signature Specificity Diagnostic
```

Purpose:

```text
Prevent the reference core from being dominated by same-isotope cross-run
links, and test whether each isotope family contributes comparable local
relational structure.
```

Possible refinements:

```text
1. family-balanced reference core:
   choose top N core edges within each family.

2. axis-separated runs:
   hydrogen only
   carbon only
   strontium only
   combined family-balanced

3. exclude same-isotope cross-run edges for one control variant:
   test whether there is nontrivial within-family isotope-order structure.

4. add a dedicated carbon-structure input once structure variants are located
   or regenerated.

5. later add BMS-IE01 iso-electronic family as an orthogonal control axis.
```

Recommended result-note target for the current run:

```text
docs/BMS_IS01_ISOTOPE_STRUCTURE_INITIAL_RESULT_NOTE.md
```

Recommended next method note:

```text
docs/BMS_IS01B_FAMILY_BALANCED_EXTENSION_SPEC.md
```

---

## 13. Minimal commit plan

Commit the runner, config, field list, method plan, and this result note separately from large run outputs:

```bash
cd ~/Downloads/deBroglie_Kaster_Theorie/quantum-spacetime-bridge

git add \
  data/bms_is01_isotope_structure_config.yaml \
  scripts/run_bms_is01_isotope_structure_specificity.py \
  docs/BMS_IS01_ISOTOPE_STRUCTURE_BMC15H_METHOD_PLAN.md \
  docs/BMS_IS01_RUNNER_FIELD_LIST.md \
  docs/BMS_IS01_ISOTOPE_STRUCTURE_INITIAL_RESULT_NOTE.md

git status --short

git commit -m "Add BMS-IS01 isotope structure specificity diagnostic"

git push
```

Run outputs should only be committed deliberately after checking file size and repository policy.
