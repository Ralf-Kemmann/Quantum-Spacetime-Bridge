# BMC-15 Series Geometry-Proxy Synthesis Note

Date: 2026-05-01  
Project: Gravitation und RaumZeit / Quantum-Spacetime-Bridge  
Scope: BMC-15e / BMC-15f-f1-f2 / BMC-15g  
Status: Consolidation note, no new numerics  
Recommended repo target: `docs/BMC15_SERIES_GEOMETRY_PROXY_SYNTHESIS_NOTE.md`

---

## 1. Purpose

This note consolidates the BMC-15 geometry-proxy line after the completion of BMC-15g and the BMC-15f envelope-construction consolidation.

The goal is not to claim recovery of a physical geometry. The goal is to summarize what the BMC-15 diagnostics currently support about:

1. geometry-proxy compatibility,
2. construction sensitivity of larger envelope objects,
3. stability of a compact local core proxy,
4. methodological boundaries that remain open before any stronger specificity claim.

The synthesis is intentionally defensive. It treats the BMC-15 outputs as methodological evidence about graph-derived proxy behavior, not as direct evidence for spacetime emergence.

---

## 2. Run context

The BMC-15 series sits downstream of the N81 / node-aligned graph workflow and tests how geometry-like readouts behave under different construction and perturbation choices.

Relevant blocks:

```text
BMC-15e:
  geometry control nulls

BMC-15f/f1/f2:
  envelope construction sensitivity
  node alignment
  connectedness transition

BMC-15g:
  core perturbation robustness
```

Last recorded clean project state before this synthesis:

```text
c9d6a55 Add BMC-15f envelope construction consolidation note
a6b7862 Add BMC-15g core perturbation robustness diagnostic
```

This note does not introduce a new runner, new data table, or new numerical output. It is a documentation-level consolidation of already completed BMC-15e/f/g work.

---

## 3. Inputs

### 3.1 Conceptual inputs

The synthesis uses the following already-established BMC-15 interpretation frame:

```text
Large envelopes:
  construction-sensitive and parameter-sensitive.

Compact local core proxy:
  retained across canonical node-aligned construction variants.

Perturbation behavior:
  topologically robust under small edge perturbations,
  sensitive under weight-rank perturbations.
```

### 3.2 BMC-15f/f1/f2 inputs

BMC-15f/f1/f2 tested envelope construction sensitivity across construction families and node-aligned variants.

Recorded run structure:

```text
BMC-15f:
  Output: runs/BMC-15f/envelope_construction_sensitivity_open
  Input kind: edge_table
  Nodes: 19
  Variant metric rows: 12
  Edge-overlap rows: 36
  Core-containment rows: 12
  Warnings: none

BMC-15f1:
  Output: runs/BMC-15f1/node_aligned_envelope_sensitivity_open
  Input kind: wide_feature_table
  Nodes: 22
  Variant metric rows: 12
  Edge-overlap rows: 36
  Core-containment rows: 12
  Warnings: none

BMC-15f2:
  Output: runs/BMC-15f2/connectedness_transition_sweep_open
  Input kind: wide_feature_table
  Nodes: 22
  Variant metric rows: 35
  Edge-overlap rows: 105
  Core-containment rows: 35
  Warnings: none
```

### 3.3 BMC-15g inputs

BMC-15g tested core perturbation robustness.

Recorded run structure:

```text
Output directory:
  runs/BMC-15g/core_perturbation_robustness_open

Metric rows:   1800
Envelope rows: 5400

Design:
  3 perturbation families
  × 4 strengths
  × 3 seeds
  × 50 repeats
  = 1800 core metric rows

  1800 core rows
  × 3 reference envelopes
  = 5400 envelope rows
```

---

## 4. Method / perturbation / construction families

### 4.1 BMC-15e: geometry control nulls

BMC-15e is treated here as the control-null context for the BMC-15 line. Its role is to keep the geometry-proxy interpretation bounded:

```text
Question:
  Do geometry-proxy readouts survive comparison against control/null constructions?

Use in synthesis:
  BMC-15e provides the caution layer.
  It prevents direct interpretation of proxy geometry as recovered physical geometry.
```

The present synthesis does not restate BMC-15e as a proof of specificity. Instead, it treats BMC-15e as part of the methodological guardrail around the later BMC-15f/g observations.

### 4.2 BMC-15f/f1/f2: envelope construction sensitivity

The BMC-15f family tested whether larger envelope-level geometry proxies remain stable across graph construction choices.

Construction families included:

```text
mutual_kNN variants
spanning-tree variants / anchors
threshold sweeps / transition sweeps
```

The key methodological distinction is:

```text
Envelope-level object:
  large, construction-dependent graph envelope.

Reference core:
  compact six-edge local core proxy monitored for containment.
```

### 4.3 BMC-15g: core perturbation robustness

BMC-15g tested the compact core proxy under perturbation of the canonical graph object.

Perturbation families:

```text
edge_dropout
edge_swap
weight_jitter
```

The diagnostic distinction is:

```text
Topological perturbations:
  edge_dropout and edge_swap.

Weight-rank perturbations:
  weight_jitter.
```

This distinction is central. BMC-15g supports a stronger statement for small topological perturbations than for weight-rank perturbations.

---

## 5. Primary results

### 5.1 BMC-15f/f1/f2 connectedness behavior

Recorded connectedness behavior:

```text
BMC-15f, 19-node MVP:
  mutual_kNN_k_sweep: connected rate 0.200, median edges 29.0, edge range 15–46
  spanning_tree_variants: connected rate 1.000, median edges 18.0, edge range 18–18
  threshold_sweep: connected rate 0.000, median edges 9.0, edge range 3–17

BMC-15f1, 22-node node-aligned:
  mutual_kNN_k_sweep: connected rate 0.000, median edges 34.0, edge range 17–55
  spanning_tree_variants: connected rate 1.000, median edges 21.0, edge range 21–21
  threshold_sweep: connected rate 0.000, median edges 12.0, edge range 5–23

BMC-15f2, 22-node transition sweep:
  mutual_kNN_k_transition_sweep: connected rate 0.643, median edges 75.0, edge range 17–133
  spanning_tree_transition_anchors: connected rate 1.000, median edges 21.0, edge range 21–21
  threshold_transition_sweep: connected rate 0.105, median edges 28.0, edge range 5–69
```

Interpretation of this block:

```text
Large envelope connectedness is construction-dependent.
Spanning-tree families are connected by construction.
Threshold and mutual-kNN families show parameter-dependent transitions.
```

This means envelope-level geometry proxies should not be treated as unique objects.

### 5.2 BMC-15f/f1/f2 core-containment behavior

Reference core size:

```text
6 edges
```

Recorded containment:

```text
BMC-15f, 19-node MVP:
  mutual_kNN k2: 4/6, k3: 5/6, k4-k6: 6/6
  threshold 0.02-0.08: 3/6, threshold 0.10: 5/6
  spanning tree variants: 4/6

BMC-15f1, 22-node node-aligned:
  mutual_kNN k2-k6: 6/6
  threshold 0.02: 5/6, threshold 0.03-0.10: 6/6
  spanning tree variants: 6/6

BMC-15f2, 22-node transition sweep:
  mutual_kNN k2-k15: 6/6
  threshold 0.02: 5/6, threshold 0.03-0.30: 6/6
  spanning tree anchors: 6/6
```

Interpretation of this block:

```text
The 19-node MVP is partially sensitive.
The canonical 22-node node-aligned regime shows near-complete to complete core containment.
The connectedness-transition sweep preserves the compact core across broad construction ranges.
```

Internal image:

```text
The envelope is the Nebelschale.
The compact local core is the Klunker.
The Nebelschale changes shape.
The Klunker remains visible in the relevant 22-node regime.
```

Methodological translation:

```text
Envelope-level geometry proxies are construction-sensitive.
The compact local core proxy is comparatively stable across canonical node-aligned construction variants.
```

### 5.3 BMC-15g perturbation behavior

Recorded BMC-15g core behavior:

```text
edge_dropout / edge_swap at strength 0.10:
  mean core edge retention ≈ 0.89
  min ≈ 0.667
  connected_fraction = 1.0

weight_jitter:
  strength 0.01 mean retention = 0.80
  strength 0.10 mean retention ≈ 0.481
  min = 0.0
  max ≈ 0.833
  connected_fraction = 1.0
```

Interpretation of this block:

```text
Small topological perturbations:
  The compact core remains robustly retained.

Weight-rank perturbations:
  The current top-strength reconstruction rule is sensitive to weight reordering.
```

Internal image:

```text
Bei leichtem Kanten-Rütteln bleibt der Klunker stabil.
Wenn man an den Gewichten rüttelt, sortiert sich die Schmuckschatulle teilweise neu.
```

Methodological translation:

```text
BMC-15g supports construction-qualified robustness of the compact BMC-15 reference-core proxy under small topological perturbations of the canonical graph object.
At the same time, it identifies weight-rank sensitivity as a relevant methodological boundary.
```

---

## 6. Befund

### 6.1 Consolidated finding

The BMC-15e/f/g line supports the following bounded finding:

```text
The large graph envelope is construction- and parameter-sensitive.
The compact local reference-core proxy remains stable across canonical node-aligned construction variants and under small topological perturbations.
The present top-strength core reconstruction rule remains sensitive to weight-rank perturbations.
```

### 6.2 What is robust within the tested scope

Within the tested BMC-15 scope, the most stable object is not the full envelope. It is the compact local core proxy.

Supported within scope:

```text
local core proxy stability
node-aligned construction retention
small-topological-perturbation robustness
construction-qualified geometry-proxy compatibility
```

### 6.3 What is not robust within the tested scope

Not robust as a unique object:

```text
large envelope geometry
single construction-specific graph shape
threshold-specific or k-specific global scaffold
weight-rank-based reconstruction under jitter
```

This is not a failure of the BMC-15 line. It is a useful boundary: the diagnostics distinguish between a method-sensitive envelope and a more stable compact local proxy.

---

## 7. Interpretation

The current BMC-15 series suggests a layered interpretation:

```text
Layer 1 — Envelope:
  The large geometry-like scaffold depends on construction family and parameter regime.

Layer 2 — Core:
  A compact local core proxy remains visible across canonical node-aligned envelope constructions.

Layer 3 — Perturbation response:
  The core is robust to small topological perturbations but sensitive to weight-rank perturbations.
```

This supports a cautious internal picture:

```text
The Nebelschale is not the object to overclaim.
The Klunker is the more interesting methodological signal.
```

External scientific phrasing:

```text
The BMC-15 series indicates that envelope-level geometry proxies are construction-sensitive and should not be interpreted as unique recovered geometries. However, in the canonical node-aligned regime, a compact local reference-core proxy is consistently retained across multiple envelope families and remains robust under small topological perturbations. The current top-strength reconstruction rule remains sensitive to weight-rank perturbations, which defines an important methodological limitation.
```

---

## 8. Methodological caution

The BMC-15 synthesis must not be over-interpreted.

Not supported:

```text
physical spacetime emergence proven
unique geometry recovered
Lorentzian structure recovered
causal structure recovered
metric recovered
continuum limit established
specificity proven
```

Allowed claim level:

```text
geometry-proxy compatible
construction-qualified
methodological signal
local core proxy
robustness diagnostic
sensitivity diagnostic
```

The strongest current statement is therefore not:

```text
The method recovers spacetime geometry.
```

The defensible statement is:

```text
The method identifies a construction-qualified local core proxy that is more stable than the surrounding envelope under the tested node-aligned construction and perturbation families.
```

---

## 9. Conservative conclusion

The BMC-15e/f/g sequence gives a useful and internally consistent methodological result.

Conservative conclusion:

```text
BMC-15 does not establish a unique physical geometry.
It does show that large envelope-level geometry proxies are construction-sensitive.
Within the canonical 22-node node-aligned regime, however, the compact local core proxy is consistently retained across envelope construction families and through connectedness-transition sweeps.
BMC-15g further supports robustness of this compact core under small topological perturbations, while exposing weight-rank sensitivity as a central limitation of the current top-strength reconstruction rule.
```

Compact project phrasing:

```text
The envelope moves; the compact core persists — but only within a construction-qualified and weight-rank-sensitive methodological frame.
```

---

## 10. Recommended next step

Two possible next steps are available.

### Option A — Documentation consolidation

Recommended if the goal is to stabilize the current BMC-15 line before new numerics:

```text
Create or extend a public-facing / reviewer-facing BMC-15 synthesis section.
Connect BMC-15e, BMC-15f/f1/f2, and BMC-15g to a single cautious claim ladder.
Add an explicit “not yet specificity” paragraph.
```

This is the safer next move if the repository is being prepared for external reading.

### Option B — BMC-15h Structured Specificity Extension

Recommended if the goal is to test the next methodological gap:

```text
Question:
  Do structured null families reproduce the same core-containment and envelope behavior?

Purpose:
  Move from robustness / construction sensitivity toward a more specific diagnostic.

Claim boundary:
  Even a positive BMC-15h would still support only a bounded specificity diagnostic unless the null family design is broad and pre-registered.
```

Candidate BMC-15h framing:

```text
BMC-15h Structured Specificity Extension

Core question:
  Is the compact reference-core proxy specifically associated with the original relational / feature-structured construction,
  or can structured null families produce comparable containment and perturbation behavior?
```

Recommended immediate action:

```text
Do not start BMC-15h numerics before writing a short SPEC that freezes:
  input tables,
  null families,
  core definition,
  envelope families,
  primary readouts,
  decision labels,
  failure modes.
```

---

## 11. Suggested commit

After installing this file into `docs/`, use a selective commit only.

```bash
cd ~/Downloads/deBroglie_Kaster_Theorie/quantum-spacetime-bridge

git status --short

git add docs/BMC15_SERIES_GEOMETRY_PROXY_SYNTHESIS_NOTE.md

git status --short

git commit -m "Add BMC-15 geometry proxy synthesis note"

git push

git status --short
git log --oneline -8
```

Do not use `git add .`.

---

## 12. One-sentence anchor

```text
BMC-15e/f/g supports a construction-qualified geometry-proxy picture in which large envelopes are method-sensitive, while a compact local core proxy remains stable across node-aligned construction variants and small topological perturbations, with weight-rank sensitivity remaining the main current boundary.
```
