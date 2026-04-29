# BMC-15f Envelope-Construction Sensitivity — Result Note

## Purpose

BMC-15f tests whether the BMC-15 geometry-proxy behavior is stable under changes in envelope/backbone construction.

This block addresses the red-team concern:

```text
Could the observed envelope-level geometry-proxy behavior be partly induced by the envelope construction method itself?
```

BMC-15f is a robustness and sensitivity diagnostic. It does not test physical spacetime emergence, causal structure, Lorentzian signature, light-cone structure, continuum structure, or a physical metric.

---

## 1. Run metadata

Run:

```text
BMC-15f_envelope_construction_sensitivity_mvp
```

Output directory:

```text
runs/BMC-15f/envelope_construction_sensitivity_open/
```

Primary outputs:

```text
summary.json
variant_metrics.csv
family_summary.csv
stability_summary.csv
edge_overlap_summary.csv
core_containment_summary.csv
readout.md
```

Technical status:

```text
completed successfully
warnings: none
```

Run size:

```text
variant metric rows:       12
family summary rows:        3
stability rows:            24
edge-overlap rows:         36
core-containment rows:     12
```

Input:

```text
relational_input_kind: edge_table
n_nodes: 19
```

Important caution:

```text
The BMC-15f relational input contains 19 nodes, whereas the BMC-15e exported observed graph objects contained 22 nodes.
Therefore BMC-15f should be read as an envelope-construction sensitivity test on the available relational input,
not as a perfect one-to-one repetition of the BMC-15e 22-node graph-object space.
```

---

## 2. Reference graphs loaded

BMC-15f loaded the following BMC-15 reference graph objects:

| Reference object | Nodes | Edges | Connected |
|---|---:|---:|---|
| `maximum_spanning_tree_envelope` | 22 | 21 | true |
| `mutual_kNN_k3_envelope` | 22 | 23 | false |
| `threshold_path_consensus_envelope` | 22 | 70 | false |
| `top_strength_reference_core` | 9 | 6 | false |

The compact core was used as a containment anchor, not as a standalone geometry object.

---

## 3. Envelope families tested

The MVP tested three envelope-construction families:

```text
mutual_kNN_k_sweep
threshold_sweep
spanning_tree_variants
```

Family connectedness:

| Envelope family | Variants | Connected rate | Median edges | Edge range |
|---|---:|---:|---:|---|
| `mutual_kNN_k_sweep` | 5 | 0.200 | 29.0 | 15–46 |
| `spanning_tree_variants` | 2 | 1.000 | 18.0 | 18–18 |
| `threshold_sweep` | 5 | 0.000 | 9.0 | 3–17 |

Immediate interpretation:

```text
Envelope construction strongly affects connectedness.

The spanning-tree variants are consistently connected.
The threshold sweep fragments completely under the tested sparsity settings.
The mutual-kNN sweep is mostly disconnected, with only one connected variant.
```

Internal short form:

```text
Die Küchenmaschine baut nicht immer dieselbe Hülle.
Einige Messer schneiden sauber, andere machen Konfetti.
```

---

## 4. Stability label counts

Overall stability labels:

| Stability label | Count |
|---|---:|
| `stable_across_variants` | 12 |
| `parameter_sensitive` | 7 |
| `moderately_stable_across_variants` | 5 |

By family:

| Envelope family | moderately stable | parameter sensitive | stable |
|---|---:|---:|---:|
| `mutual_kNN_k_sweep` | 1 | 5 | 2 |
| `spanning_tree_variants` | 0 | 0 | 8 |
| `threshold_sweep` | 4 | 2 | 2 |

Interpretation:

```text
The spanning-tree variants are stable across the implemented diagnostics.
The mutual-kNN sweep is mostly parameter-sensitive.
The threshold sweep is mixed: several moderate-stability labels, but also fragmentation and parameter sensitivity.
```

This means:

```text
The envelope-level geometry-proxy readout is not construction-independent.
It must remain method-qualified.
```

---

## 5. Core containment

Core containment by family:

| Envelope family | Count | Min | Median | Max |
|---|---:|---:|---:|---:|
| `mutual_kNN_k_sweep` | 5 | 0.666667 | 1.000000 | 1.000000 |
| `spanning_tree_variants` | 2 | 0.666667 | 0.666667 | 0.666667 |
| `threshold_sweep` | 5 | 0.500000 | 0.500000 | 0.833333 |

Interpretation:

```text
The compact reference core is partially preserved across all tested envelope families.
In the mutual-kNN sweep, containment rises to full containment for k >= 4.
Spanning-tree variants preserve four of six core edges.
Threshold variants preserve half of the core at lower sparsity settings, rising to five of six at top_fraction = 0.10.
```

Conservative reading:

```text
Core containment is robust enough to remain interesting,
but it is not perfectly construction-invariant.
It depends on envelope family and sparsity/neighbor parameter.
```

---

## 6. Edge-overlap with BMC-15 reference envelopes

Edge-overlap was measured by Jaccard overlap.

### 6.1 Overlap with `maximum_spanning_tree_envelope`

| Envelope family | Count | Min | Median | Max |
|---|---:|---:|---:|---:|
| `mutual_kNN_k_sweep` | 5 | 0.264151 | 0.384615 | 0.413793 |
| `spanning_tree_variants` | 2 | 0.392857 | 0.392857 | 0.392857 |
| `threshold_sweep` | 5 | 0.142857 | 0.346154 | 0.407407 |

### 6.2 Overlap with `mutual_kNN_k3_envelope`

| Envelope family | Count | Min | Median | Max |
|---|---:|---:|---:|---:|
| `mutual_kNN_k_sweep` | 5 | 0.352941 | 0.461538 | 0.592593 |
| `spanning_tree_variants` | 2 | 0.464286 | 0.464286 | 0.464286 |
| `threshold_sweep` | 5 | 0.130435 | 0.391304 | 0.538462 |

### 6.3 Overlap with `threshold_path_consensus_envelope`

| Envelope family | Count | Min | Median | Max |
|---|---:|---:|---:|---:|
| `mutual_kNN_k_sweep` | 5 | 0.164384 | 0.320000 | 0.432099 |
| `spanning_tree_variants` | 2 | 0.173333 | 0.173333 | 0.173333 |
| `threshold_sweep` | 5 | 0.042857 | 0.128571 | 0.191781 |

Interpretation:

```text
Edge overlap is moderate at best.
No tested construction family simply reproduces the BMC-15 reference envelopes.
The mutual-kNN sweep overlaps most strongly with the mutual_kNN_k3 reference, as expected.
Threshold-path-consensus overlap remains low, especially for threshold_sweep and spanning-tree variants.
```

This supports the interpretation that:

```text
The core/envelope morphology is construction-dependent.
Envelope-level claims must remain method-qualified.
```

---

## 7. Main BMC-15f finding

### Befund

```text
BMC-15f completed successfully.

Envelope construction strongly affects connectedness, edge counts, overlap with reference envelopes,
and stability classifications.

The compact reference core is partially retained across all tested families,
with strongest containment in mutual-kNN variants at k >= 4.

Spanning-tree variants are stable and connected, but algorithmically constrained.

Threshold variants fragment under the tested sparsity settings.
```

### Interpretation

```text
The BMC-15 envelope-level geometry-proxy behavior is not fully construction-independent.
It depends on the envelope construction method and parameter regime.

However, the compact core is not simply erased by construction variation.
It remains partially present across all tested families and fully present in higher-k mutual-kNN variants.
```

### Hypothesis

```text
The observed relational structure may contain a compact local core that is more stable than the broader envelope morphology.

The envelope morphology appears method-dependent,
while the core has partial cross-construction persistence.
```

### Open gaps

```text
BMC-15f used a 19-node relational input while some BMC-15 reference graph objects have 22 nodes.
Threshold variants were disconnected in the tested parameter range.
mutual-kNN variants were mostly disconnected, except one tested k.
Spanning-tree stability may partly reflect algorithmic constraints.
The current run is an MVP and should not be treated as a final construction-invariance proof.
No physical geometry, causal structure, Lorentzian signature, or spacetime emergence has been established.
```

---

## 8. Relation to BMC-15e

BMC-15e showed:

```text
Observed graph objects often lie within the range of simple geometry-generated controls,
with selected stress/spectral cases more favorable than those controls.
```

BMC-15f adds:

```text
Envelope construction affects connectedness and morphology strongly.
The compact core shows partial persistence across construction variants.
```

Combined reading:

```text
The geometry-proxy behavior is strengthened by BMC-15e,
but BMC-15f shows that envelope-level interpretations must remain construction-qualified.

The robust object is not the entire envelope morphology.
The more stable candidate is the compact local core plus selected proxy behavior.
```

---

## 9. Allowed and blocked language

### Allowed

```text
envelope-construction sensitivity
method-qualified envelope interpretation
partial core containment across variants
spanning-tree variants stable but algorithmically constrained
mutual-kNN parameter sensitivity
threshold fragmentation under tested sparsity settings
geometry-proxy robustness is limited and construction-dependent
```

### Use carefully

```text
stable core
robust envelope
geometry-like scaffold
construction-invariant
```

These terms require qualification.

### Blocked

```text
envelope morphology proves geometry
BMC-15f confirms spacetime emergence
construction variation proves physical structure
directed neighbor relations imply causality
stable spanning-tree behavior proves physical skeleton
```

---

## 10. Reviewer-facing paragraph

```text
BMC-15f tests the sensitivity of BMC-15 geometry-proxy diagnostics to envelope-construction choices. The MVP run shows that envelope construction strongly affects connectedness and morphology: spanning-tree variants remain connected and stable, threshold variants fragment under the tested sparsity settings, and mutual-kNN variants are parameter-sensitive. Core containment is nevertheless partially preserved across all tested families, reaching full containment for higher-k mutual-kNN variants. These results support a construction-qualified interpretation: the compact core appears more persistent than the broader envelope morphology, but envelope-level geometry-proxy claims are method-dependent and must not be treated as construction-invariant physical geometry.
```

---

## 11. Internal human summary

```text
Die Küchenmaschine baut nicht immer dieselbe Hülle.

Spanning tree:
  sauber connected und stabil,
  aber stark algorithmisch gezwungen.

threshold sweep:
  macht in diesem MVP Konfetti,
  alle Varianten disconnected.

mutual-kNN:
  parameterempfindlich,
  aber der Kern kommt ab k=4 vollständig mit.

Das heißt:
  Die Hülle ist methodenabhängig.
  Der Kern bleibt interessanter als die Hüllenform.
  Geometry-proxy bleibt gültig als vorsichtige Diagnostik,
  aber envelope-level Claims müssen angeleint bleiben.
```

---

## 12. Recommended next steps

### 12.1 BMC-15f.1 node-aligned rerun

Check whether the 19-node input should be aligned with the 22-node BMC-15 graph-object space.

Question:

```text
Can the same sensitivity test be run on the exact 22-node graph-object input used by BMC-15e?
```

### 12.2 Expand threshold parameter range

The tested threshold variants were all disconnected.

Possible follow-up:

```text
increase top_fraction
or define connectedness-preserving threshold variants
```

### 12.3 Expand mutual-kNN sweep

The mutual-kNN family shows meaningful core containment at higher k.

Possible follow-up:

```text
k = 3..10
track connectedness transition
track core containment transition
track stress / negative-eigenvalue behavior
```

### 12.4 Keep BMC-16 deferred

Causal/Lorentzian diagnostics should remain later.

Internal rule:

```text
First finish geometry-proxy robustness.
Then define a defensible arrow.
Only then test causal-set-inspired diagnostics.
```

---

## 13. Final internal closing sentence

```text
BMC-15f sagt nicht:
Die Hülle ist real.

BMC-15f sagt:
Die Hülle hängt an der Küchenmaschine.
Aber der Kern verschwindet nicht einfach.

Das ist ein guter Dämpfer und zugleich eine nützliche Stärkung:
Nicht die ganze Hülle ist der Held.
Der kompakte Kern bleibt der bessere Kandidat für robuste Struktur.
```
