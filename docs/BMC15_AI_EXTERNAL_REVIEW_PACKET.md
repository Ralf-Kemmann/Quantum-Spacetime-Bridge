# QSB / BMC-15 Analysis Packet for External AI Review

## Purpose of this packet

This file is intended as a compact, AI-readable analysis packet for an external model or assistant.

It is **not** a red-team prompt.
It is **not** a publication text.
It is **not** a claim of physical spacetime emergence.

It summarizes the current BMC-15e / BMC-15f / BMC-15f.1 result state and asks for careful analytical interpretation.

Preferred review mode:

```text
quiet analytical review
methodological synthesis
identify implications, gaps, and next best tests
avoid hype
avoid overclaiming
```

---

# 1. Project frame

The broader project investigates whether relational structures derived from matter-/feature-sensitive representations can show stable local cores and geometry-proxy behavior.

Core language:

```text
observed relational structure
compact local core
method-dependent envelope
geometry-proxy diagnostics
structured nulls
geometry-generated controls
construction sensitivity
```

Strict claim boundary:

```text
No physical spacetime emergence has been proven.
No physical metric has been reconstructed.
No causal structure has been tested.
No Lorentzian signature has been tested.
No light-cone structure has been shown.
No continuum limit has been shown.
```

Allowed language:

```text
geometry-proxy compatible
embedding-compatible
within geometry-control range
more favorable than tested controls for selected proxies
construction-sensitive envelope
partially / strongly persistent compact core
informative but not uniquely specific
```

Blocked language:

```text
proves spacetime
reconstructs physical geometry
shows causal structure
shows Lorentzian spacetime
demonstrates quantum gravity
```

---

# 2. Prior BMC-15 context

Before BMC-15e/f, the consolidated interpretation was:

```text
BMC-15b:
  observed graph objects are more favorable than graph-rewire nulls,
  but feature-/family-/correlation-structured nulls can often produce similar proxy values.

BMC-15d:
  red-team integration forced strict claim boundaries and separated:
    feature_structured_nulls
    graph_rewire_nulls
```

Interpretive baseline:

```text
The observed geometry-proxy behavior is not merely graph-rewire-like.
However, it is not uniquely specific, because structured feature/family/correlation nulls can reproduce many proxy values.
```

---

# 3. BMC-15e Geometry-Control Nulls

## 3.1 Purpose

BMC-15e adds explicitly geometry-generated control graphs.

Question:

```text
Where do observed BMC-15 graph objects sit relative to simple geometry-generated control graphs?
```

This creates a positive geometry-control anchor.

It does not prove physical geometry.

## 3.2 Run metadata

Run ID:

```text
BMC-15e_geometry_control_nulls_mvp
```

Output directory:

```text
runs/BMC-15e/geometry_control_nulls_open/
```

Technical status:

```text
completed successfully
warnings: none
sklearn_available: true
scipy_available: true
```

Row counts:

```text
control metric rows:       7200
family summary rows:       36
observed-position rows:    288
```

Observed graph objects loaded:

| Graph object | Nodes | Edges | Connected |
|---|---:|---:|---|
| `N81_full_baseline` | 22 | 81 | true |
| `maximum_spanning_tree_envelope` | 22 | 21 | true |
| `mutual_kNN_k3_envelope` | 22 | 23 | false |

Caution:

```text
mutual_kNN_k3_envelope is disconnected.
Distance-based diagnostics for this graph use disconnected-graph handling and should be read cautiously.
```

Control families:

```text
random_geometric_graph
soft_geometric_kernel
```

Dimensions:

```text
2, 3, 4
```

Weight modes:

```text
unweighted
observed_rank_remap
```

Replicates:

```text
200 per object / family / dimension / weight mode
```

## 3.3 Original readout counts

Before readout-label refinement:

| Label | Count |
|---|---:|
| `not_directional` | 180 |
| `observed_within_geometry_control_range` | 66 |
| `observed_geometry_control_equivalent` | 36 |
| `observed_more_geometry_like_than_geometry_controls` | 6 |

The 6 favorable cases were all in:

```text
negative_eigenvalue_burden
```

## 3.4 Readout-label refinement

The first readout labeled all embedding-stress metrics as:

```text
not_directional
```

This was corrected because embedding stress is directional:

```text
lower embedding stress = stronger embedding compatibility
```

Refined directional metrics:

```text
embedding_stress_2d: lower_is_more_geometry_like
embedding_stress_3d: lower_is_more_geometry_like
embedding_stress_4d: lower_is_more_geometry_like
```

Patch status:

```text
labels changed only
no controls regenerated
no metrics recomputed
```

Rows changed:

```text
108 of 288
```

Refined counts:

| Label | Count |
|---|---:|
| `observed_within_geometry_control_range` | 159 |
| `not_directional` | 72 |
| `observed_geometry_control_equivalent` | 36 |
| `observed_more_geometry_like_than_geometry_controls` | 21 |

Change:

```text
observed_more_geometry_like_than_geometry_controls:
  6 -> 21
```

Breakdown:

```text
15 favorable cases from embedding stress
6 favorable cases from negative eigenvalue burden
```

Embedding stress changed rows:

```text
embedding_stress_2d:
  5 more favorable than geometry controls
  31 within geometry-control range

embedding_stress_3d:
  5 more favorable than geometry controls
  31 within geometry-control range

embedding_stress_4d:
  5 more favorable than geometry controls
  31 within geometry-control range
```

## 3.5 BMC-15e main finding

Befund:

```text
BMC-15e completed successfully.
Most directional comparisons place observed values inside the range of simple geometry-generated controls or in all-zero equivalence.
A smaller subset of comparisons is more favorable than all tested geometry controls, especially in embedding stress and negative eigenvalue burden.
```

Interpretation:

```text
The observed graph objects are not only more favorable than graph-rewire nulls, but are also broadly compatible with simple geometry-generated control regimes.
This strengthens the geometry-proxy interpretation.
However, the result is not uniquely specific, because feature-/family-/correlation-structured nulls can still produce many similar proxy values.
```

Conservative summary:

```text
BMC-15e strengthens geometry-proxy compatibility.
It does not establish physical geometry or spacetime emergence.
```

---

# 4. BMC-15f Envelope-Construction Sensitivity

## 4.1 Purpose

BMC-15f tests whether envelope/backbone construction choices affect geometry-proxy behavior.

Question:

```text
Could the observed envelope-level geometry-proxy behavior be partly induced by the envelope construction method itself?
```

## 4.2 Run metadata

Run ID:

```text
BMC-15f_envelope_construction_sensitivity_mvp
```

Input:

```text
relational_input_kind: edge_table
n_nodes: 19
```

Run size:

```text
variant metric rows:   12
family summary rows:    3
stability rows:        24
edge-overlap rows:     36
core-containment rows: 12
warnings: none
```

Important mismatch:

```text
BMC-15f used a 19-node relational input.
BMC-15e/BMC-15 graph-object exports use a 22-node graph space.
```

Node mismatch:

```text
BMC-15 graph objects have:
  ring_p_1, ring_p_2, ring_p_3
  ring_p_m1, ring_p_m2, ring_p_m3

BMC-15f input has:
  ring_abs_p_1, ring_abs_p_2, ring_abs_p_3
```

Interpretation:

```text
BMC-15f was useful but not exactly node-aligned with BMC-15/BMC-15e.
```

## 4.3 Families tested

```text
mutual_kNN_k_sweep
threshold_sweep
spanning_tree_variants
```

Family connectedness:

| Envelope family | Variants | Connected rate | Median edges | Edge range |
|---|---:|---:|---:|---|
| `mutual_kNN_k_sweep` | 5 | 0.200 | 29 | 15–46 |
| `spanning_tree_variants` | 2 | 1.000 | 18 | 18–18 |
| `threshold_sweep` | 5 | 0.000 | 9 | 3–17 |

Stability label counts:

| Stability label | Count |
|---|---:|
| `stable_across_variants` | 12 |
| `parameter_sensitive` | 7 |
| `moderately_stable_across_variants` | 5 |

By family:

| Envelope family | Stable | Moderate | Parameter sensitive |
|---|---:|---:|---:|
| `mutual_kNN_k_sweep` | 2 | 1 | 5 |
| `spanning_tree_variants` | 8 | 0 | 0 |
| `threshold_sweep` | 2 | 4 | 2 |

## 4.4 Core containment in BMC-15f

| Envelope family | Min | Median | Max |
|---|---:|---:|---:|
| `mutual_kNN_k_sweep` | 0.666667 | 1.000000 | 1.000000 |
| `spanning_tree_variants` | 0.666667 | 0.666667 | 0.666667 |
| `threshold_sweep` | 0.500000 | 0.500000 | 0.833333 |

Interpretation:

```text
The compact core is partially preserved across all tested families.
It is strongest in mutual-kNN for k >= 4.
The broad envelope is construction-dependent.
```

## 4.5 BMC-15f main finding

Befund:

```text
Envelope construction strongly affects connectedness, edge counts, overlap with reference envelopes, and stability classifications.
The compact reference core is partially retained across all tested families.
```

Interpretation:

```text
The envelope-level geometry-proxy behavior is not fully construction-independent.
The compact core appears more persistent than the broad envelope morphology.
```

Caution:

```text
The 19-node input means this is not yet the fully node-aligned test.
```

---

# 5. BMC-15f.1 Node-Aligned Envelope Sensitivity

## 5.1 Purpose

BMC-15f.1 repeats envelope-construction sensitivity on the exact 22-node sign-sensitive BMC-15/BMC-15e graph space.

Preflight exact-match input:

```text
data/bmc08c_real_units_feature_table.csv
```

Input kind:

```text
wide_feature_table
```

Node count:

```text
22
```

This resolves the 19-node vs 22-node mismatch.

## 5.2 Run metadata

Run ID:

```text
BMC-15f1_node_aligned_envelope_construction_sensitivity_mvp
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

## 5.3 Family connectedness

| Envelope family | Variants | Connected count | Connected rate | Median edges | Edge range |
|---|---:|---:|---:|---:|---|
| `mutual_kNN_k_sweep` | 5 | 0 | 0.000 | 34 | 17–55 |
| `spanning_tree_variants` | 2 | 2 | 1.000 | 21 | 21–21 |
| `threshold_sweep` | 5 | 0 | 0.000 | 12 | 5–23 |

Comparison with BMC-15f:

```text
mutual-kNN connectedness:
  BMC-15f:   0.200
  BMC-15f.1: 0.000

spanning-tree connectedness:
  BMC-15f:   1.000
  BMC-15f.1: 1.000

threshold connectedness:
  BMC-15f:   0.000
  BMC-15f.1: 0.000
```

Interpretation:

```text
Node alignment did not remove construction sensitivity.
Spanning tree remains connected.
mutual-kNN and threshold remain disconnected under tested settings.
```

## 5.4 Stability by family

| Envelope family | Stable | Moderately stable | Parameter sensitive |
|---|---:|---:|---:|
| `mutual_kNN_k_sweep` | 2 | 1 | 5 |
| `spanning_tree_variants` | 8 | 0 | 0 |
| `threshold_sweep` | 2 | 1 | 5 |

Interpretation:

```text
The main qualitative pattern remains:
spanning-tree variants are stable,
mutual-kNN and threshold variants are parameter-sensitive.
```

## 5.5 Core containment in BMC-15f.1

| Envelope family | Min | Median | Max |
|---|---:|---:|---:|
| `mutual_kNN_k_sweep` | 1.000000 | 1.000000 | 1.000000 |
| `spanning_tree_variants` | 1.000000 | 1.000000 | 1.000000 |
| `threshold_sweep` | 0.833333 | 1.000000 | 1.000000 |

This is the strongest positive BMC-15f.1 result.

Comparison to BMC-15f:

| Family | BMC-15f median containment | BMC-15f.1 median containment |
|---|---:|---:|
| `mutual_kNN_k_sweep` | 1.000000 | 1.000000 |
| `spanning_tree_variants` | 0.666667 | 1.000000 |
| `threshold_sweep` | 0.500000 | 1.000000 |

Interpretation:

```text
Node alignment strongly improves core containment.
The broad envelope remains method-dependent, but the compact core becomes substantially more persistent in the 22-node sign-sensitive representation.
```

## 5.6 Edge overlap in BMC-15f.1

### Overlap with `maximum_spanning_tree_envelope`

| Envelope family | Median | Max |
|---|---:|---:|
| `mutual_kNN_k_sweep` | 0.527778 | 0.809524 |
| `spanning_tree_variants` | 0.826087 | 0.826087 |
| `threshold_sweep` | 0.500000 | 0.629630 |

### Overlap with `mutual_kNN_k3_envelope`

| Envelope family | Median | Max |
|---|---:|---:|
| `mutual_kNN_k_sweep` | 0.583333 | 0.777778 |
| `spanning_tree_variants` | 0.629630 | 0.629630 |
| `threshold_sweep` | 0.521739 | 0.708333 |

### Overlap with `threshold_path_consensus_envelope`

| Envelope family | Median | Max |
|---|---:|---:|
| `mutual_kNN_k_sweep` | 0.485714 | 0.644737 |
| `spanning_tree_variants` | 0.263889 | 0.263889 |
| `threshold_sweep` | 0.171429 | 0.328571 |

Interpretation:

```text
Overlap improves substantially in the node-aligned setting for several references.
The broad threshold-path-consensus envelope remains the least reproduced reference.
```

## 5.7 BMC-15f.1 main finding

Befund:

```text
BMC-15f.1 completed successfully on the exact 22-node sign-sensitive graph space.
Envelope construction remains method-dependent.
Spanning-tree variants are connected and stable.
mutual-kNN and threshold variants remain disconnected in the tested parameter range.
Core containment is strongly improved compared with the 19-node MVP.
```

Interpretation:

```text
The broad envelope morphology remains construction-sensitive.
However, the compact core is much more persistent when the test is run on the node-aligned sign-sensitive representation.
```

Hypothesis:

```text
The sign-sensitive 22-node representation better preserves the local relational core than the collapsed absolute-ring representation.
The compact core may represent a more stable support-side structure than the larger method-dependent envelope.
```

---

# 6. Consolidated interpretation across BMC-15e/f/f.1

## 6.1 What is strengthened

BMC-15e strengthens:

```text
geometry-proxy compatibility against simple geometry-generated controls
```

BMC-15f strengthens / qualifies:

```text
envelope morphology is construction-sensitive
compact core is more persistent than broad envelope
```

BMC-15f.1 strengthens:

```text
on exact 22-node sign-sensitive representation,
core containment becomes strong across tested construction families
```

Most defensible combined statement:

```text
The observed BMC-15 structures occupy a geometry-proxy-compatible regime under simple geometry controls, while the broad envelope morphology remains method-dependent. The compact local core is the more persistent object, especially in the node-aligned sign-sensitive representation.
```

## 6.2 What remains weak or qualified

```text
feature-/family-/correlation-structured nulls remain serious alternative explanations
envelope morphology is not construction-invariant
mutual-kNN and threshold variants can be disconnected
spanning-tree stability is algorithmically constrained
geometry-proxy results do not imply physical geometry
no causal/Lorentzian structure has been tested
```

## 6.3 Central conceptual result

Internal language:

```text
Nicht die ganze Hülle ist der Held.
Der kompakte Kern ist der stabilere Kandidat.
```

Technical language:

```text
The compact local core is more persistent under construction variation than the broader envelope morphology.
```

---

# 7. Suggested analysis questions for external AI

Please analyze the result state using the following questions:

## 7.1 Methodological interpretation

```text
1. Does the combined BMC-15e/f/f.1 evidence support a construction-qualified geometry-proxy interpretation?
2. Which conclusions are strongest?
3. Which conclusions are weakest?
4. Does BMC-15f.1 meaningfully improve the BMC-15f result, or mainly shift the input representation?
5. How should the 19-node vs 22-node difference be framed?
```

## 7.2 Robustness

```text
1. Is core containment the strongest surviving signal?
2. Does the disconnectedness of mutual-kNN and threshold variants undermine the result?
3. How serious is the algorithmic constraint of spanning-tree stability?
4. Should the next test expand k/top_fraction ranges to find connectedness transitions?
5. Should a node-aligned geometry-control rerun be performed?
```

## 7.3 Claim boundaries

```text
1. What wording is safe for a reviewer-facing summary?
2. What wording risks overclaiming?
3. What evidence would be required before discussing causal or Lorentzian structure?
4. Which result is most defensible as a methodological contribution?
```

## 7.4 Next best tests

Potential next tests:

```text
BMC-15f.2 connectedness-transition sweep:
  mutual-kNN k = 2..12
  threshold top_fraction = 0.02..0.30

BMC-15g core-specific robustness:
  focus on compact core containment and perturbation tests

BMC-15e.2 node-aligned geometry-control repetition:
  use exact 22-node sign-sensitive representation for geometry controls

BMC-16 delayed:
  causal/Lorentzian diagnostics only after defining a defensible directed relation
```

Please recommend the most efficient next test and explain why.

---

# 8. Reviewer-facing paragraph candidate

```text
BMC-15e–f.1 extends the BMC-15 geometry-proxy analysis by adding geometry-generated controls and envelope-construction sensitivity tests. BMC-15e shows that the observed graph objects often fall within the range of simple geometry-generated controls and, in selected embedding-stress and negative-eigenvalue-burden comparisons, are more favorable than those controls. BMC-15f shows that broad envelope morphology is construction-sensitive. A node-aligned BMC-15f.1 rerun on the exact 22-node sign-sensitive representation strengthens the compact-core result: core containment becomes high across all tested construction families, while mutual-kNN and threshold envelopes remain parameter-sensitive and often disconnected. The combined result supports a construction-qualified geometry-proxy interpretation in which the compact local core is more persistent than the broader envelope morphology. It does not establish physical geometry, causal structure, Lorentzian signature, or spacetime emergence.
```

---

# 9. Internal human summary

```text
BMC-15e:
  Der Klunker liegt oft im Bereich geometrischer Kontrollgerüste
  und ist in einigen Stress-/Spektralstellen sogar günstiger.

BMC-15f:
  Die Hülle hängt an der Küchenmaschine.
  Der Kern bleibt interessanter als die Hülle.

BMC-15f.1:
  Auf der richtigen 22-node Werkbank bleibt der Kern richtig stark drin.

Gesamt:
  Die große Hülle ist methodenabhängig.
  Der kleine Kern ist der robustere Kandidat.
  Geometry-proxy ja.
  Raumzeitpokal nein.
```

---

# 10. Final one-line interpretation

```text
The current BMC-15 evidence most defensibly supports a construction-qualified geometry-proxy signal centered on a persistent compact local core, not a physical spacetime reconstruction.
```
