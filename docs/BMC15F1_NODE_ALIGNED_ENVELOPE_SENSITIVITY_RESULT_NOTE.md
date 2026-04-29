# BMC-15f.1 Node-Aligned Envelope Sensitivity — Result Note

## Purpose

BMC-15f.1 repeats the BMC-15f envelope-construction sensitivity test on a node-aligned input.

The first BMC-15f MVP was useful, but used a 19-node relational edge table with collapsed absolute ring nodes. BMC-15f.1 uses the 22-node sign-sensitive BMC-08c feature table, matching the BMC-15/BMC-15e graph-object node space.

This is a methodological robustness block.

It does not test physical spacetime emergence, causal structure, Lorentzian signature, light-cone structure, continuum structure, or a physical metric.

---

## 1. Run metadata

Run:

```text
BMC-15f1_node_aligned_envelope_construction_sensitivity_mvp
```

Output directory:

```text
runs/BMC-15f1/node_aligned_envelope_sensitivity_open/
```

Input kind:

```text
wide_feature_table
```

Node count:

```text
22
```

Technical status:

```text
completed successfully
warnings: none
```

Run size:

```text
n_variants:          12
n_envelope_families: 3
```

Claim boundary:

```text
Envelope-construction sensitivity only.
No physical geometry, causal structure, Lorentzian signature, or spacetime emergence is established.
```

---

## 2. Why BMC-15f.1 was needed

BMC-15f MVP used:

```text
19 nodes
ring_abs_p_1
ring_abs_p_2
ring_abs_p_3
```

BMC-15/BMC-15e graph-object space uses:

```text
22 nodes
ring_p_1
ring_p_2
ring_p_3
ring_p_m1
ring_p_m2
ring_p_m3
```

The node-alignment preflight identified:

```text
data/bmc08c_real_units_feature_table.csv
```

as the exact 22-node match.

Therefore BMC-15f.1 tests whether the envelope-construction sensitivity conclusion survives on the correct sign-sensitive graph workspace.

Internal summary:

```text
BMC-15f zeigte:
  Die Hülle hängt an der Küchenmaschine.

BMC-15f.1 fragt:
  Passiert das auch auf derselben Werkbank wie BMC-15/BMC-15e?
```

---

## 3. Envelope families tested

BMC-15f.1 used the same family grid as BMC-15f:

```text
mutual_kNN_k_sweep
threshold_sweep
spanning_tree_variants
```

Family connectedness:

| Envelope family | Variants | Connected count | Connected rate | Median edges | Edge range |
|---|---:|---:|---:|---:|---:|
| `mutual_kNN_k_sweep` | 5 | 0 | 0.0 | 34 | 17–55 |
| `spanning_tree_variants` | 2 | 2 | 1.0 | 21 | 21–21 |
| `threshold_sweep` | 5 | 0 | 0.0 | 12 | 5–23 |

Interpretation:

```text
Node alignment did not remove construction sensitivity.

Spanning-tree variants remain connected.
mutual-kNN variants are disconnected across the tested k range.
threshold variants are also disconnected across the tested sparsity range.
```

Compared with BMC-15f MVP:

```text
mutual-kNN connectedness worsened:
  BMC-15f:   0.200
  BMC-15f.1: 0.000

spanning-tree connectedness stayed perfect:
  BMC-15f:   1.000
  BMC-15f.1: 1.000

threshold connectedness stayed fragmented:
  BMC-15f:   0.000
  BMC-15f.1: 0.000
```

---

## 4. Stability classification

By family:

| Envelope family | Stable | Moderately stable | Parameter sensitive |
|---|---:|---:|---:|
| `mutual_kNN_k_sweep` | 2 | 1 | 5 |
| `spanning_tree_variants` | 8 | 0 | 0 |
| `threshold_sweep` | 2 | 1 | 5 |

Interpretation:

```text
The node-aligned rerun preserves the main qualitative pattern:

spanning-tree variants are stable,
while mutual-kNN and threshold variants remain parameter-sensitive.
```

The threshold sweep becomes more parameter-sensitive in the node-aligned run:

```text
BMC-15f:
  threshold_sweep = 2 stable, 4 moderately stable, 2 parameter sensitive

BMC-15f.1:
  threshold_sweep = 2 stable, 1 moderately stable, 5 parameter sensitive
```

This strengthens the conclusion that threshold-envelope behavior is parameter-dependent under the tested settings.

---

## 5. Core containment

Core containment by family:

| Envelope family | Count | Min | Median | Max |
|---|---:|---:|---:|---:|
| `mutual_kNN_k_sweep` | 5 | 1.000000 | 1.000000 | 1.000000 |
| `spanning_tree_variants` | 2 | 1.000000 | 1.000000 | 1.000000 |
| `threshold_sweep` | 5 | 0.833333 | 1.000000 | 1.000000 |

This is the most important positive result of BMC-15f.1.

Interpretation:

```text
After node alignment, the compact reference core is almost completely preserved across all tested construction families.

mutual-kNN:
  full containment in all tested variants

spanning-tree:
  full containment in both tested variants

threshold:
  at least five of six core edges retained,
  median and maximum full containment
```

Compared with BMC-15f MVP:

| Family | BMC-15f median containment | BMC-15f.1 median containment |
|---|---:|---:|
| `mutual_kNN_k_sweep` | 1.000000 | 1.000000 |
| `spanning_tree_variants` | 0.666667 | 1.000000 |
| `threshold_sweep` | 0.500000 | 1.000000 |

Interpretation:

```text
Node alignment strengthens the core-persistence result substantially.

The broad envelope remains construction-sensitive, but the compact core becomes more robust in the aligned 22-node sign-sensitive representation.
```

---

## 6. Edge overlap with reference envelopes

### 6.1 Maximum spanning-tree reference

| Envelope family | Count | Min | Median | Max |
|---|---:|---:|---:|---:|
| `mutual_kNN_k_sweep` | 5 | 0.357143 | 0.527778 | 0.809524 |
| `spanning_tree_variants` | 2 | 0.826087 | 0.826087 | 0.826087 |
| `threshold_sweep` | 5 | 0.238095 | 0.500000 | 0.629630 |

Interpretation:

```text
Node-aligned variants overlap much more strongly with the maximum-spanning-tree reference,
especially the spanning-tree variants.
```

### 6.2 Mutual-kNN-k3 reference

| Envelope family | Count | Min | Median | Max |
|---|---:|---:|---:|---:|
| `mutual_kNN_k_sweep` | 5 | 0.368421 | 0.583333 | 0.777778 |
| `spanning_tree_variants` | 2 | 0.629630 | 0.629630 | 0.629630 |
| `threshold_sweep` | 5 | 0.217391 | 0.521739 | 0.708333 |

Interpretation:

```text
Overlap with the mutual-kNN reference is moderate to high in the aligned run.
This is expected for mutual-kNN variants and notable for spanning-tree variants.
```

### 6.3 Threshold-path-consensus reference

| Envelope family | Count | Min | Median | Max |
|---|---:|---:|---:|---:|
| `mutual_kNN_k_sweep` | 5 | 0.242857 | 0.485714 | 0.644737 |
| `spanning_tree_variants` | 2 | 0.263889 | 0.263889 | 0.263889 |
| `threshold_sweep` | 5 | 0.071429 | 0.171429 | 0.328571 |

Interpretation:

```text
Overlap with the broad threshold-path-consensus envelope remains weaker,
especially for threshold_sweep and spanning-tree variants.
This suggests that the broad consensus envelope remains method-specific.
```

---

## 7. Comparison to BMC-15f MVP

BMC-15f MVP concluded:

```text
The envelope depends on construction.
The core remains more interesting than the broader envelope morphology.
```

BMC-15f.1 refines this:

```text
On the node-aligned 22-node sign-sensitive workspace,
the envelope remains construction-sensitive,
but the compact core becomes substantially more robust.
```

Important changes:

```text
Core containment improves strongly:
  spanning-tree median: 0.666667 → 1.000000
  threshold median:     0.500000 → 1.000000
  mutual-kNN remains:   1.000000 → 1.000000

Edge overlap improves strongly for several reference/family combinations.

Connectedness does not generally improve:
  mutual-kNN and threshold variants remain disconnected under tested settings.
```

---

## 8. Main BMC-15f.1 finding

### Befund

```text
BMC-15f.1 completed successfully on the exact 22-node sign-sensitive graph space.

Envelope construction remains method-dependent.

Spanning-tree variants are connected and stable.
mutual-kNN and threshold variants remain disconnected in the tested parameter range.

Core containment is strongly improved compared with the 19-node MVP:
the compact reference core is fully retained across mutual-kNN and spanning-tree variants,
and nearly fully retained across threshold variants.
```

### Interpretation

```text
The broad envelope morphology remains construction-sensitive.

However, the compact core is much more persistent when the test is run on the node-aligned sign-sensitive representation.

This strengthens the interpretation that the compact local core is the more robust object,
whereas envelope morphology is method-dependent.
```

### Hypothesis

```text
The sign-sensitive 22-node representation better preserves the local relational core than the collapsed absolute-ring representation.

The compact core may represent a more stable support-side structure than the larger method-dependent envelope.
```

### Open gaps

```text
mutual-kNN and threshold variants are still disconnected under the tested settings.
The broad threshold-path-consensus envelope is not strongly reproduced by threshold_sweep.
Spanning-tree stability remains algorithmically constrained.
This is still a geometry-proxy robustness result, not physical geometry.
No causal/Lorentzian structure has been tested.
```

---

## 9. Relation to BMC-15e

BMC-15e refined readout showed:

```text
Observed graph objects often lie within the range of simple geometry-generated controls,
with selected embedding-stress and negative-eigenvalue-burden cases more favorable than controls.
```

BMC-15f.1 adds:

```text
When the envelope-sensitivity test is run on the exact node-aligned sign-sensitive representation,
the compact core is strongly retained across construction families.
```

Combined conservative reading:

```text
BMC-15e strengthens the geometry-proxy compatibility.
BMC-15f.1 strengthens the local-core persistence.
But envelope-level morphology remains construction-sensitive and must be qualified.
```

---

## 10. Allowed and blocked language

### Allowed

```text
node-aligned envelope sensitivity
sign-sensitive 22-node representation
strong core containment across tested construction families
method-dependent envelope morphology
construction-qualified geometry-proxy interpretation
compact core more persistent than broad envelope
```

### Use carefully

```text
robust core
stable scaffold
geometry-like envelope
```

These require explicit proxy and construction qualifications.

### Blocked

```text
BMC-15f.1 proves geometry
the envelope is physical
the core is spacetime
node alignment proves causal structure
spanning-tree stability proves physical skeleton
```

---

## 11. Reviewer-facing paragraph

```text
BMC-15f.1 repeats the BMC-15f envelope-construction sensitivity test on the exact 22-node sign-sensitive graph space used by the BMC-15/BMC-15e graph objects. The node-aligned rerun preserves the main construction-sensitivity conclusion: broad envelope morphology remains method-dependent, with spanning-tree variants stable and connected while mutual-kNN and threshold variants remain disconnected under the tested parameter ranges. However, core containment is substantially strengthened in the node-aligned run: the compact reference core is fully retained across mutual-kNN and spanning-tree variants and nearly fully retained across threshold variants. This supports a construction-qualified interpretation in which the compact local core is more persistent than the broader envelope morphology. The result remains a geometry-proxy robustness finding and does not establish physical geometry, causal structure, Lorentzian signature, or spacetime emergence.
```

---

## 12. Internal human summary

```text
Jetzt benutzen wir dieselbe Werkbank.

BMC-15f.1 sagt:

Die Hülle bleibt Küchenmaschinen-abhängig.
mutual-kNN und threshold sind weiter zickig/disconnected.
Spanning tree ist sauber, aber algorithmisch streng.

Aber:
Der Kern bleibt jetzt richtig stark drin.

Im 22-node sign-sensitive Setup:
  mutual-kNN: Kern komplett drin
  spanning tree: Kern komplett drin
  threshold: Kern fast immer komplett drin

Das ist eine gute Nachricht:
Nicht die große Hülle ist der Held.
Der kleine Kern ist der stabilere Kandidat.
```

---

## 13. Recommended next steps

### 13.1 Update BMC-15f consolidated interpretation

BMC-15f and BMC-15f.1 should be summarized together:

```text
BMC-15f:
  first MVP, 19-node collapsed absolute-ring input

BMC-15f.1:
  node-aligned 22-node sign-sensitive rerun
```

Combined message:

```text
Envelope morphology is construction-sensitive.
Core containment becomes strong in the node-aligned representation.
```

### 13.2 Expand connectedness-preserving parameter ranges

Because mutual-kNN and threshold remain disconnected:

```text
mutual-kNN:
  extend k beyond 6

threshold:
  extend top_fraction beyond 0.10
  or test connectedness-preserving threshold variants
```

### 13.3 Avoid BMC-16 until geometry-proxy robustness is consolidated

Do not jump to causal/Lorentzian claims yet.

Internal rule:

```text
Erst Geometry-Proxy-Robustheit abschließen.
Dann Pfeil definieren.
Dann Causal/Lorentz testen.
```

---

## 14. Final internal sentence

```text
BMC-15f.1 sagt:

Die große Hülle bleibt methodenabhängig.
Aber auf der richtigen 22-node Werkbank verschwindet der Kern nicht —
er sitzt sogar deutlich stabiler als im ersten MVP.

Das ist kein Raumzeitpokal.
Aber es ist ein ziemlich guter Kern-Befund.
```
