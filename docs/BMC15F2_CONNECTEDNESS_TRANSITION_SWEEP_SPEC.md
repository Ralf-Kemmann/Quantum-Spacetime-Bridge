# BMC-15f.2 Connectedness-Transition Sweep — Specification

## Purpose

BMC-15f.2 continues the BMC-15 envelope-construction sensitivity series after BMC-15f.1.

BMC-15f.1 established that, on the canonical 22-node sign-sensitive representation:

```text
compact core containment is strong
broad envelope morphology remains construction-sensitive
mutual-kNN and threshold variants remain disconnected in the tested parameter range
```

BMC-15f.2 therefore asks:

```text
At what construction parameters do mutual-kNN and threshold variants become connected,
and does the compact reference core remain retained across that connectedness transition?
```

This is a methodological robustness / transition-mapping block.

It does not test physical spacetime emergence, causal structure, Lorentzian signature, a light cone, a continuum limit, or a physical metric.

---

## 1. Motivation

BMC-15f.1 result:

```text
mutual_kNN_k_sweep:
  connected_count = 0 / 5
  tested k = [2, 3, 4, 5, 6]
  core containment = 1.0 across all variants

threshold_sweep:
  connected_count = 0 / 5
  tested top_fraction = [0.02, 0.03, 0.05, 0.08, 0.10]
  core containment min = 0.833333
  core containment median = 1.0
```

Main limitation:

```text
Distance-based diagnostics are limited when graphs are disconnected.
```

BMC-15f.2 extends the parameter ranges to find the transition into connected graph regimes.

---

## 2. Canonical input

Use the node-aligned BMC-08c feature table:

```text
data/bmc08c_real_units_feature_table.csv
```

Expected input kind:

```text
wide_feature_table
```

Expected node count:

```text
22
```

This is the same canonical 22-node sign-sensitive workspace used in BMC-15f.1.

---

## 3. Sweep design

### 3.1 mutual-kNN transition sweep

Recommended k range:

```text
k = 2..15
```

Purpose:

```text
Find the first k where the mutual-kNN graph becomes connected.
Track whether core containment remains high before, at, and after the transition.
```

### 3.2 threshold transition sweep

Recommended top-fraction range:

```text
top_fraction = 0.02, 0.03, 0.04, ..., 0.30
```

Purpose:

```text
Find the first top_fraction where the threshold graph becomes connected.
Track whether core containment remains high before, at, and after the transition.
```

### 3.3 spanning-tree variants

Keep spanning-tree variants as reference anchors:

```text
maximum_spanning_tree
minimum_distance_spanning_tree
```

These are expected to remain connected by construction.

They should not be interpreted as independent evidence of natural connectedness.

---

## 4. Output directory

Recommended output directory:

```text
runs/BMC-15f2/connectedness_transition_sweep_open/
```

Recommended run ID:

```text
BMC-15f2_connectedness_transition_sweep_mvp
```

---

## 5. Primary readouts

BMC-15f.2 should focus on:

```text
connectedness transition
core containment across transition
edge count at transition
embedding stress after connectedness
negative eigenvalue burden after connectedness
edge overlap with reference envelopes
```

Key questions:

```text
1. What is the first connected k for mutual-kNN?
2. What is the first connected top_fraction for threshold?
3. Is core containment already high before connectedness?
4. Does core containment remain high at connectedness?
5. Do geometry-proxy metrics stabilize after connectedness?
6. Does the broad envelope remain construction-sensitive after connectedness?
```

---

## 6. Post-processing labels

Recommended transition labels:

```text
pre_transition_disconnected
first_connected
post_transition_connected
always_connected
never_connected_in_sweep
```

Recommended core labels:

```text
full_core_retained
near_full_core_retained
partial_core_retained
weak_core_retained
```

Thresholds:

```text
full_core_retained:
  core_containment_fraction == 1.0

near_full_core_retained:
  core_containment_fraction >= 0.833333

partial_core_retained:
  core_containment_fraction >= 0.5

weak_core_retained:
  core_containment_fraction < 0.5
```

---

## 7. Interpretation templates

### If connectedness transition occurs and core remains high

```text
The compact reference core remains retained across the transition from disconnected to connected envelope regimes.
This strengthens the interpretation that core persistence is not merely a disconnected-graph artifact.
```

### If connectedness transition occurs and core weakens

```text
Core persistence is parameter-regime dependent and may be strongest in sparse or fragmented envelope constructions.
Envelope-level interpretation must be qualified accordingly.
```

### If no connectedness transition occurs in the sweep

```text
The tested mutual-kNN / threshold construction family remains disconnected across the explored parameter range.
Distance-based diagnostics remain limited for that family, and either broader parameters or alternative connectedness-preserving constructions are needed.
```

### If broad envelope metrics remain parameter-sensitive after connectedness

```text
Connectedness alone does not remove envelope construction sensitivity.
The compact core remains the more robust object than the larger envelope morphology.
```

Blocked:

```text
BMC-15f.2 proves geometry.
BMC-15f.2 proves spacetime emergence.
Connectedness proves physical metric structure.
Core containment proves causal structure.
```

---

## 8. Relation to previous blocks

```text
BMC-15e:
  geometry-control comparison; now audited as node-aligned at full observed graph-object level.

BMC-15f:
  first envelope-sensitivity MVP; 19-node collapsed absolute-ring input.

BMC-15f.1:
  canonical 22-node node-aligned envelope sensitivity;
  strong compact core containment;
  mutual-kNN and threshold disconnected in tested ranges.

BMC-15f.2:
  connectedness-transition mapping on the same canonical 22-node representation.
```

---

## 9. Expected result note structure

After the run, write:

```text
docs/BMC15F2_CONNECTEDNESS_TRANSITION_SWEEP_RESULT_NOTE.md
```

Sections:

```text
1. Purpose and claim boundary
2. Run metadata
3. Connectedness transition by family
4. Core containment across transition
5. Geometry-proxy metrics before/after transition
6. Edge overlap with reference envelopes
7. Comparison to BMC-15f.1
8. Befund / Interpretation / Hypothesis / Open gaps
9. Reviewer-facing paragraph
```

---

## 10. Human summary

```text
BMC-15f.1 sagte:
Der Kern sitzt, aber mutual-kNN und threshold sind disconnected.

BMC-15f.2 fragt:
Ab wann werden die Hüllen zusammenhängend,
und bleibt der Kern beim Übergang sitzen?

Das ist der nächste Kobold:
nicht ob der Kern hübsch aussieht,
sondern ob er auch im connected regime noch trägt.
```

---

## 11. Final internal sentence

```text
Wenn der Kern vor, während und nach dem Connectedness-Übergang sitzen bleibt,
dann ist er nicht nur ein Sparse-Graph-Artefakt.

Wenn er kippt,
haben wir eine saubere Grenze gefunden.

Beides ist wissenschaftlich nützlich.
```
