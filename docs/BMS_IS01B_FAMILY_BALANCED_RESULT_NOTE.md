# BMS-IS01b — Family-Balanced Matter Signature Specificity Result Note

Date: 2026-05-01  
Project: Gravitation und RaumZeit / Quantum-Spacetime-Bridge  
Recommended repo target: `docs/BMS_IS01B_FAMILY_BALANCED_RESULT_NOTE.md`  
Status: Result note for BMS-IS01b family-balanced diagnostic

---

## 1. Purpose

BMS-IS01b refines the initial BMS-IS01 isotope / structure specificity diagnostic.

BMS-IS01 found a strong reference core, but that core was dominated by same-isotope cross-run links:

```text
same isotope
same family
different run-weighting variant
```

That result is useful as a run-stability diagnostic, but it does not by itself establish a broader isotope-order or family-internal structure signal.

BMS-IS01b therefore changes the core definition:

```text
family-balanced reference core
3 selected edges per isotope family
same-isotope cross-run edges excluded
```

The working question is:

```text
Does each isotope family retain a stable relational edge structure once
same-isotope cross-run identity links are excluded?
```

Internal working image:

```text
IS01 fand stabile Wiedererkennungs-Kanten.

IS01b fragt:
Wenn wir diese offensichtlichen Wiedererkennungs-Kanten herausnehmen,
bleibt dann innerhalb H, C und Sr noch eine robuste Kantenordnung übrig?
```

---

## 2. Run context

Runner:

```text
scripts/run_bms_is01b_family_balanced_specificity.py
```

Config:

```text
data/bms_is01b_family_balanced_config.yaml
```

Output directory:

```text
runs/BMS-IS01b/family_balanced_specificity_open/
```

Reference-core mode:

```text
family_balanced_top_edges
```

Same-isotope cross-run exclusion:

```text
true
```

Input table count:

```text
9
```

Node count:

```text
27
```

Real edge count:

```text
351
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

## 3. Row counts

```text
core_metrics:              4832
edges:                    53001
envelope_metrics:          7248
family_summary:               3
nodes_resolved:              27
null_family_inventory:      150
real_vs_null_summary:       144
reference_core_edges:         9
warnings:                     0
```

---

## 4. Summary labels

The real-vs-null summary contains 144 rows.

Interpretation labels:

```text
null_reproduces_core_behavior:   68
mixed_family_dependent_result:   26
real_exceeds_tested_null_family: 34
null_reproduces_metric_behavior: 16
```

Breakdown by null family:

```text
degree_weight_preserving_rewire:
  mixed_family_dependent_result: 11
  real_exceeds_tested_null_family: 18
  null_reproduces_core_behavior: 19

feature_structured_shuffle:
  null_reproduces_core_behavior: 23
  mixed_family_dependent_result: 9
  null_reproduces_metric_behavior: 16

core_seeded_decoy:
  null_reproduces_core_behavior: 26
  mixed_family_dependent_result: 6
  real_exceeds_tested_null_family: 16
```

---

## 5. Reference core

The BMS-IS01b reference core contains 9 family-balanced edges, 3 per family.

Same-isotope cross-run edges were excluded. All selected reference-core edges have:

```text
excluded_same_isotope_cross_run = False
```

### Carbon family

```text
carbon_isotopes__carbon_run_b__13c
  -- carbon_isotopes__carbon_run_c__12c
  weight ≈ 0.02810

carbon_isotopes__carbon_run_a__13c
  -- carbon_isotopes__carbon_run_c__12c
  weight ≈ 0.02748

carbon_isotopes__carbon_run_c__12c
  -- carbon_isotopes__carbon_run_c__13c
  weight ≈ 0.02518
```

### Hydrogen family

```text
hydrogen_isotopes__hydrogen_run_a__3h
  -- hydrogen_isotopes__hydrogen_run_c__2h
  weight ≈ 0.18283

hydrogen_isotopes__hydrogen_run_a__2h
  -- hydrogen_isotopes__hydrogen_run_b__3h
  weight ≈ 0.17795

hydrogen_isotopes__hydrogen_run_c__2h
  -- hydrogen_isotopes__hydrogen_run_c__3h
  weight ≈ 0.17753
```

### Strontium family

```text
strontium_isotopes__strontium_run_a__87sr
  -- strontium_isotopes__strontium_run_b__88sr
  weight ≈ 0.25266

strontium_isotopes__strontium_run_c__87sr
  -- strontium_isotopes__strontium_run_c__88sr
  weight ≈ 0.24805

strontium_isotopes__strontium_run_a__88sr
  -- strontium_isotopes__strontium_run_c__87sr
  weight ≈ 0.24770
```

Important observation:

```text
The family-balanced core is composed of different-isotope within-family edges.
It no longer measures same-isotope run-stability.
```

However, the selected edge weights are much lower than the strongest BMS-IS01 same-isotope cross-run edges.

This is especially visible for carbon:

```text
carbon family-balanced edge weights ≈ 0.025 to 0.028
```

Hydrogen is intermediate:

```text
hydrogen family-balanced edge weights ≈ 0.178 to 0.183
```

Strontium is strongest among the balanced different-isotope cores:

```text
strontium family-balanced edge weights ≈ 0.248 to 0.253
```

---

## 6. Befund

BMS-IS01b shows that once same-isotope cross-run identity links are excluded, the family-balanced core becomes substantially less specific.

Null families reproduce core behavior in many construction regimes:

```text
null_reproduces_core_behavior: 68 / 144
```

The real graph still exceeds null families in some rows:

```text
real_exceeds_tested_null_family: 34 / 144
```

But the dominant pattern is no longer the strong real-over-null edge containment observed in BMS-IS01.

The core-seeded decoy family is especially strong:

```text
core_seeded_decoy:
  null_reproduces_core_behavior: 26
  real_exceeds_tested_null_family: 16
  mixed_family_dependent_result: 6
```

Feature-structured shuffle also reproduces many readouts:

```text
feature_structured_shuffle:
  null_reproduces_core_behavior: 23
  mixed_family_dependent_result: 9
  null_reproduces_metric_behavior: 16
```

Degree-/weight-preserving rewire is less destructive than in BMS-IS01, but still does not yield a strong global real-over-null pattern:

```text
degree_weight_preserving_rewire:
  real_exceeds_tested_null_family: 18
  null_reproduces_core_behavior: 19
  mixed_family_dependent_result: 11
```

---

## 7. Interpretation

BMS-IS01b indicates that the strong BMS-IS01 signal was primarily carried by same-isotope cross-run stability links.

After these links are removed and the reference core is forced to include different-isotope within-family edges, the tested null families reproduce core behavior frequently.

Therefore, the stronger claim of family-internal isotope-order specificity is not supported by this first balanced diagnostic.

Defensive interpretation:

```text
BMS-IS01 supports a run-stability interpretation of isotope matter signatures:
same-isotope signature neighborhoods remain stable across run-weighting variants.

BMS-IS01b does not support a broad family-balanced isotope-order specificity
claim under the current construction and null model settings.
```

Internal working image:

```text
Wenn wir die Wiedererkennungs-Kanten rausnehmen,
wird aus dem stabilen Klunker eher eine gut nachbaubare Sortierschale.
```

---

## 8. Relation to BMS-IS01

BMS-IS01 result:

```text
stable same-isotope cross-run core
core-edge containment strongly suppressed in null families
node containment cheap
```

BMS-IS01b result:

```text
same-isotope cross-run edges excluded
different-isotope family-balanced core selected
core behavior often reproduced by null families
```

Combined lesson:

```text
The matter-side isotope signature contains strong run-stability structure, but
the present balanced diagnostic does not yet show robust family-internal
isotope-order specificity beyond that stability structure.
```

This distinction is important for the project's claim discipline.

---

## 9. Hypothesis

The isotope matter-signature vectors are dominated by two effects:

1. same-isotope stability across run-weighting variants;
2. coarse family / score-vector structure.

When same-isotope stability is excluded, the remaining different-isotope within-family edges are weaker and more easily reproduced by structured and seeded controls.

Working hypothesis:

```text
The current isotope data support stable identity-like signature neighborhoods
across run variants, but do not yet support a robust isotope-order relational
core once those identity-like links are removed.
```

Family-specific observation:

```text
Carbon has the weakest balanced core weights in this run.
Hydrogen is intermediate.
Strontium has the strongest balanced different-isotope weights.
```

This may reflect family size, mass spacing, vector degeneracy, or the current signature-score construction. It should not yet be interpreted physically.

---

## 10. Open gap

Open points:

1. Carbon is represented only by 12C and 13C in the current isotope scan.  
   This is not a full carbon-structure test.

2. The family-balanced reference core is forced to select 3 edges per family.  
   For small families, especially carbon, this may select weak edges that are not intrinsically strong relational structures.

3. Same-isotope cross-run exclusion is useful, but it may be too strict for a first stability-to-structure bridge.  
   A graded analysis could compare:
   - identity stability edges,
   - isotope-order edges,
   - mixed stability/order edges.

4. A per-family result table would be useful to separate hydrogen, carbon, and strontium readouts explicitly.

5. A proper carbon-structure input should be located or regenerated before claiming anything about carbon architecture.

6. BMS-IE01 iso-electronic controls remain an important orthogonal test axis.

---

## 11. Claim boundary

Allowed statement:

```text
BMS-IS01b shows that the strong initial BMS-IS01 signal is largely tied to
same-isotope cross-run stability. After excluding those links and enforcing a
family-balanced core, the tested null families frequently reproduce core
behavior, so a broad family-internal isotope-order specificity claim is not
supported by this run.
```

Allowed short statement:

```text
BMS-IS01 supports run-stability; BMS-IS01b weakens the stronger isotope-order
specificity interpretation.
```

Not allowed:

```text
Isotope-order specificity is proven.
Carbon structure has been demonstrated.
The bridge recognizes isotopes.
Matter identity is transferred to geometry.
A physical metric has been recovered.
```

---

## 12. Recommended next step

The next step should not be another broader claim. It should be a clarification split.

Recommended next diagnostic options:

### Option A — BMS-IS01c per-family readout

Purpose:

```text
Summarize BMS-IS01b readouts separately for hydrogen, carbon, and strontium.
```

This requires family-tagged metric summaries or a runner extension that computes per-family core-edge containment.

### Option B — BMS-IS02 carbon-structure input rebuild

Purpose:

```text
Build or locate a true carbon-structure table beyond 12C/13C isotope contrast.
```

This would address the currently open architecture question.

### Option C — BMS-IE01 iso-electronic smoke test

Purpose:

```text
Test a different matter-information axis:
same electron count, different nuclear charge / mass / coupling scale.
```

Recommended immediate next note:

```text
docs/BMS_IS01_IS01B_COMPARATIVE_DISCUSSION_NOTE.md
```

This note should compare:

```text
BMS-IS01:
  run-stability core

BMS-IS01b:
  family-balanced non-identity core mostly reproduced by nulls

BMC-15h:
  broad containment cheap, selective local embedding more informative
```

---

## 13. Minimal commit plan

Commit this result note separately from generated run outputs:

```bash
cd ~/Downloads/deBroglie_Kaster_Theorie/quantum-spacetime-bridge

git add docs/BMS_IS01B_FAMILY_BALANCED_RESULT_NOTE.md

git status --short

git commit -m "Add BMS-IS01b family-balanced result note"

git push
```

If the BMS-IS01b runner/config/spec/field-list have not yet been committed, commit them together with the result note:

```bash
git add \
  data/bms_is01b_family_balanced_config.yaml \
  scripts/run_bms_is01b_family_balanced_specificity.py \
  docs/BMS_IS01B_FAMILY_BALANCED_EXTENSION_SPEC.md \
  docs/BMS_IS01B_RUNNER_FIELD_LIST.md \
  docs/BMS_IS01B_FAMILY_BALANCED_RESULT_NOTE.md

git status --short

git commit -m "Add BMS-IS01b family-balanced matter specificity diagnostic"

git push
```

Run outputs should only be committed deliberately after checking file size and repository policy.
