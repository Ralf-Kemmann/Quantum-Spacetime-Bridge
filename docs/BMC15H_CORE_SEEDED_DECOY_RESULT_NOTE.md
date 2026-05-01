# BMC-15h — Core-Seeded Decoy Result Note

Date: 2026-05-01  
Project: Gravitation und RaumZeit / Quantum-Spacetime-Bridge  
Recommended repo target: `docs/BMC15H_CORE_SEEDED_DECOY_RESULT_NOTE.md`  
Status: Result note for BMC-15h core-seeded decoy diagnostic

---

## 1. Purpose

This note documents the BMC-15h run with the `core_seeded_decoy` null family enabled.

The purpose of this run is adversarial and methodological:

```text
Can the compact BMC-15 reference-core behavior be deliberately and cheaply
reproduced by inserting a small high-weight local seed into otherwise
controlled null graph objects?
```

Internal working image:

```text
Kann man den Klunker absichtlich billig nachbauen?
```

This test does not aim to prove or disprove physical geometry. It tests whether the current core-containment readouts are specific to the canonical relational structure, or whether they can be reproduced by an intentionally seeded local decoy.

---

## 2. Run context

Runner:

```text
scripts/run_bmc15h_structured_specificity_extension.py
```

Config:

```text
data/bmc15h_structured_specificity_extension_config.yaml
```

Output directory:

```text
runs/BMC-15h/structured_specificity_extension_open/
```

Enabled null families:

```text
degree_weight_preserving_rewire
feature_structured_shuffle
core_seeded_decoy
```

Core-seeded decoy config:

```yaml
core_seeded_decoy:
  enabled: true
  repeats: 50
  seed_edge_count: 6
  seed_weight_quantile: 0.90
  preserve_global_edge_count: true
```

---

## 3. Summary readout

The real-vs-null summary contains 162 comparison rows.

Interpretation labels:

```text
real_exceeds_tested_null_family: 118
null_reproduces_core_behavior:   20
mixed_family_dependent_result:   24
```

Breakdown by null family:

```text
degree_weight_preserving_rewire:
  real_exceeds_tested_null_family: 54

feature_structured_shuffle:
  real_exceeds_tested_null_family: 32
  mixed_family_dependent_result: 22

core_seeded_decoy:
  real_exceeds_tested_null_family: 32
  null_reproduces_core_behavior: 20
  mixed_family_dependent_result: 2
```

This confirms that the core-seeded decoy family is substantially harder than the degree-/weight-preserving rewire family and more adversarial than the feature-structured shuffle in broad envelope regimes.

---

## 4. Befund

The core-seeded decoy family reproduces the core behavior in 20 of 54 comparison rows.

The reproduction occurs mainly in broad or dense envelope constructions:

```text
mutual_knn k_10
mutual_knn k_15
threshold abs_weight_ge_0.02
threshold abs_weight_ge_0.03
threshold abs_weight_ge_0.05
threshold abs_weight_ge_0.08
threshold abs_weight_ge_0.10
threshold abs_weight_ge_0.20
threshold abs_weight_ge_0.30
top_strength top_edges_75
```

Representative decoy-reproduction cases:

```text
core_seeded_decoy
  envelope_core_edge_containment
  mutual_knn k_15
  real = 1.0
  null_mean ≈ 0.9633
  real_minus_null_mean ≈ 0.0367
  empirical_exceedance_fraction ≈ 0.80
  label = null_reproduces_core_behavior

core_seeded_decoy
  envelope_core_node_containment
  mutual_knn k_15
  real = 1.0
  null_mean ≈ 0.9733
  real_minus_null_mean ≈ 0.0267
  empirical_exceedance_fraction ≈ 0.80
  label = null_reproduces_core_behavior

core_seeded_decoy
  envelope_core_edge_containment
  threshold abs_weight_ge_0.02 to abs_weight_ge_0.30
  real = 1.0
  null_mean ≈ 0.9633
  real_minus_null_mean ≈ 0.0367
  empirical_exceedance_fraction ≈ 0.80
  label = null_reproduces_core_behavior

core_seeded_decoy
  envelope_core_node_containment
  threshold abs_weight_ge_0.02 to abs_weight_ge_0.30
  real = 1.0
  null_mean ≈ 0.9733
  real_minus_null_mean ≈ 0.0267
  empirical_exceedance_fraction ≈ 0.80
  label = null_reproduces_core_behavior

core_seeded_decoy
  envelope_core_edge_containment
  top_strength top_edges_75
  real = 1.0
  null_mean ≈ 0.8833
  real_minus_null_mean ≈ 0.1167
  empirical_exceedance_fraction ≈ 0.50
  label = null_reproduces_core_behavior
```

At the same time, the canonical real graph still exceeds the core-seeded decoy family in 32 of 54 rows.

The strongest real-over-decoy cases occur in selective local or smaller-envelope constructions:

```text
core_seeded_decoy
  envelope_core_edge_containment
  mutual_knn k_2
  real = 1.0
  null_mean ≈ 0.1167
  real_minus_null_mean ≈ 0.8833
  empirical_exceedance_fraction = 0.0
  label = real_exceeds_tested_null_family

core_seeded_decoy
  envelope_core_node_containment
  mutual_knn k_2
  real = 1.0
  null_mean ≈ 0.1533
  real_minus_null_mean ≈ 0.8467
  empirical_exceedance_fraction = 0.0
  label = real_exceeds_tested_null_family

core_seeded_decoy
  envelope_core_edge_containment
  top_strength top_edges_21
  real = 1.0
  null_mean ≈ 0.1567
  real_minus_null_mean ≈ 0.8433
  empirical_exceedance_fraction = 0.0
  label = real_exceeds_tested_null_family

core_seeded_decoy
  envelope_core_edge_containment
  maximum_spanning_tree abs_weight_mst
  real = 1.0
  null_mean ≈ 0.1867
  real_minus_null_mean ≈ 0.8133
  empirical_exceedance_fraction = 0.0
  label = real_exceeds_tested_null_family
```

Intermediate cases appear around `mutual_knn k_6`, where the label becomes mixed:

```text
core_seeded_decoy
  envelope_core_edge_containment
  mutual_knn k_6
  real = 1.0
  null_mean ≈ 0.6767
  real_minus_null_mean ≈ 0.3233
  empirical_exceedance_fraction ≈ 0.08
  label = mixed_family_dependent_result

core_seeded_decoy
  envelope_core_node_containment
  mutual_knn k_6
  real = 1.0
  null_mean ≈ 0.7422
  real_minus_null_mean ≈ 0.2578
  empirical_exceedance_fraction ≈ 0.08
  label = mixed_family_dependent_result
```

---

## 5. Interpretation

BMC-15h with core-seeded decoys confirms that broad core-containment readouts are not sufficiently specific on their own.

A deliberately seeded compact local structure can reproduce core containment in broad or dense envelopes, especially:

- high-k mutual-kNN,
- broad threshold envelopes,
- large top-strength envelopes.

This is an important methodological boundary.

However, the decoy does not reproduce the real graph uniformly. In selective local constructions, especially low-k mutual-kNN and smaller top-strength envelopes, the canonical real graph remains clearly above the seeded decoys.

The diagnostic therefore sharpens the BMC-15h interpretation:

```text
Broad envelope containment is cheap.
Selective local-core behavior is harder to fake.
```

Internal working image:

```text
Man kann einen künstlichen Klunker in die Schmuckschatulle legen.
Aber bei streng-lokaler Prüfung verhält er sich nicht überall wie der echte.
```

---

## 6. Hypothesis

The compact BMC-15 reference-core proxy is not adequately characterized by a single containment metric.

The result suggests a two-regime picture:

1. Broad-envelope regime  
   In broad or dense envelope constructions, core containment is easily reproduced by feature-structured and core-seeded controls. These readouts are therefore weak specificity markers.

2. Selective-local regime  
   In selective local constructions, especially low-k mutual-kNN and small top-strength envelopes, the real graph remains strongly separated from rewire, feature-structured, and core-seeded null families. These readouts are more informative for construction-qualified local-core specificity.

Working hypothesis:

```text
The specificity-relevant signal is not merely the presence of a compact core,
but the way that core is embedded in selective local relational neighborhoods.
```

---

## 7. Open gap

The current result does not prove physical geometry or full core specificity.

Open points:

1. The core-seeded decoy construction itself should be documented in detail in the runner field list or a companion method note.  
   The interpretation depends on how seed nodes/edges are selected and inserted.

2. A higher-repeat run may be useful for stabilizing empirical exceedance fractions near the mixed boundary.

3. The threshold-envelope results are highly non-specific under seeded decoys.  
   Future claims should avoid treating broad threshold containment as standalone specificity evidence.

4. A compact aggregate score could be useful, separating:
   - selective-local constructions,
   - transition constructions,
   - broad-envelope constructions.

5. The remaining optional reference-envelope warnings should either be resolved or explicitly removed from the config for a clean final run.

---

## 8. Claim boundary

Allowed statement:

```text
BMC-15h supports a construction-qualified specificity indication for selective
local core behavior. Broad core-containment readouts are partially reproducible
by feature-structured and core-seeded controls and therefore should not be used
as standalone specificity evidence.
```

More detailed allowed statement:

```text
The core-seeded decoy test shows that deliberate local seed insertion can
reproduce core containment in broad envelope constructions. However, the
canonical real graph remains clearly separated from seeded decoys under
selective local constructions such as low-k mutual-kNN and smaller
top-strength envelopes.
```

Not allowed:

```text
Core specificity is proven.
The decoy test was passed in an absolute sense.
Feature-structured and core-seeded nulls are defeated.
A physical geometry has been recovered.
A unique spacetime geometry has been derived.
The core is independent of construction choice.
```

---

## 9. Recommended next step

The next methodological step should consolidate BMC-15h into a short synthesis note that explicitly separates construction regimes.

Recommended target:

```text
docs/BMC15H_STRUCTURED_SPECIFICITY_SYNTHESIS_NOTE.md
```

Suggested synthesis structure:

```text
1. What survived all tested nulls?
2. What was reproduced by feature-structured controls?
3. What was reproduced by core-seeded decoys?
4. Which construction regimes remain informative?
5. Claim boundary for the BMC-15h series
```

Recommended internal summary sentence:

```text
Der Klunker ist nicht einfach ein Umverdrahtungsartefakt. Er ist aber auch
nicht als bloßes Containment in breiten Envelopes spezifisch. Interessant
bleibt vor allem die streng-lokale Einbettung.
```

Recommended external summary sentence:

```text
The BMC-15h diagnostics indicate that compact core containment alone is not a
sufficiently specific marker, since broad envelope readouts can be reproduced
by structured and seeded controls. The more informative signal is the
persistence of the real core under selective local construction rules.
```

---

## 10. Minimal commit plan

Commit this result note separately from generated run outputs:

```bash
cd ~/Downloads/deBroglie_Kaster_Theorie/quantum-spacetime-bridge

git add docs/BMC15H_CORE_SEEDED_DECOY_RESULT_NOTE.md

git status --short

git commit -m "Add BMC-15h core-seeded decoy result note"

git push
```

Run outputs should only be committed deliberately after checking file size and repository policy.
