# BMC-15e Geometry-Control Nulls — Result Note, Final Refined Readout

## Purpose

This note is the final BMC-15e result note after the readout-label refinement patch.

BMC-15e extends the BMC-15 geometry-proxy comparison layer by adding explicitly geometry-generated control graph families. The purpose is not to prove geometry, but to ask:

```text
Where do the observed BMC-15 graph objects sit relative to simple geometry-generated control graphs?
```

This remains a geometry-proxy diagnostic. It does **not** establish physical spacetime emergence, causal structure, Lorentzian signature, light-cone structure, continuum structure, or a physical metric.

---

## 1. Input state

BMC-15e follows the consolidated BMC-15 interpretation:

```text
BMC-15b:
  observed graph objects are more favorable than graph-rewire nulls,
  but feature-/family-/correlation-structured nulls can often produce similar proxy values.

BMC-15d:
  red-team integration established strict claim boundaries.

BMC-15e:
  adds explicitly geometry-generated control graph families as a positive comparison anchor.
```

BMC-15e therefore asks whether the observed geometry-proxy behavior is merely better than graph-rewire noise, or whether it also sits in the regime of simple geometry-generated graph controls.

---

## 2. Run metadata

Run:

```text
BMC-15e_geometry_control_nulls_mvp
```

Output directory:

```text
runs/BMC-15e/geometry_control_nulls_open/
```

Primary original outputs:

```text
summary.json
geometry_control_metrics.csv
family_summary.csv
observed_position_summary.csv
readout.md
```

Readout refinement outputs:

```text
observed_position_summary_refined.csv
readout_refined.md
bmc15e_refinement_patch_metrics.json
```

Technical status:

```text
completed successfully
warnings: none
sklearn_available: true
scipy_available: true
```

Output row counts:

```text
control metric rows:       7200
family summary rows:       36
observed-position rows:    288
```

Readout refinement:

```text
rows total:    288
rows changed:  108
```

---

## 3. Observed graph objects loaded

| Graph object | Nodes | Edges | Connected |
|---|---:|---:|---|
| `N81_full_baseline` | 22 | 81 | true |
| `maximum_spanning_tree_envelope` | 22 | 21 | true |
| `mutual_kNN_k3_envelope` | 22 | 23 | false |

Important caution:

```text
mutual_kNN_k3_envelope is disconnected.
Its distance-based diagnostics are affected by disconnected-graph handling
and should be read cautiously.
```

---

## 4. Geometry-control families

The MVP used two explicitly geometry-generated control families:

```text
random_geometric_graph
soft_geometric_kernel
```

Dimensions:

```text
2
3
4
```

Weight modes:

```text
unweighted
observed_rank_remap
```

Replicates:

```text
200 per object / family / dimension / weight-mode combination
```

The MVP therefore provides a first Euclidean-style geometry-control anchor. Hyperbolic or hierarchical controls were not active in this run.

---

## 5. Diagnostics and directional logic

The BMC-15e comparison used:

```text
triangle_defects
embedding_stress_2d
embedding_stress_3d
embedding_stress_4d
negative_eigenvalue_burden
negative_eigenvalue_count
geodesic_consistency_error
local_dimension_proxy
```

Directional interpretation after refinement:

```text
lower triangle_defects                  = more geometry-like in this proxy
lower embedding_stress_2d/3d/4d         = stronger embedding compatibility
lower negative_eigenvalue_burden        = lower Euclidean Gram-burden proxy
lower geodesic_consistency_error        = more homogeneous geodesic proxy
```

Non-directional or cautionary metrics:

```text
local_dimension_proxy
negative_eigenvalue_count
```

---

## 6. Readout-label refinement patch

The first BMC-15e readout labeled all embedding-stress metrics as:

```text
not_directional
```

This was a readout-label issue. Within the BMC-15 geometry-proxy logic, normalized embedding stress is directional:

```text
lower embedding stress = stronger embedding compatibility
```

The refinement patch therefore reclassified:

```text
embedding_stress_2d
embedding_stress_3d
embedding_stress_4d
```

as:

```text
lower_is_more_geometry_like
```

The patch changed only labels. It did not recompute:

```text
geometry controls
graph objects
distance matrices
embedding stress values
negative eigenvalue burden
triangle defects
geodesic consistency values
```

Internal short form:

```text
Die Zahlen bleiben.
Die Schilder wurden richtig herum gedreht.
```

---

## 7. Original position-label counts

Before refinement:

| Label | Count |
|---|---:|
| `not_directional` | 180 |
| `observed_within_geometry_control_range` | 66 |
| `observed_geometry_control_equivalent` | 36 |
| `observed_more_geometry_like_than_geometry_controls` | 6 |

The six favorable cases were all associated with:

```text
negative_eigenvalue_burden
```

---

## 8. Refined position-label counts

After refinement:

| Label | Count |
|---|---:|
| `observed_within_geometry_control_range` | 159 |
| `not_directional` | 72 |
| `observed_geometry_control_equivalent` | 36 |
| `observed_more_geometry_like_than_geometry_controls` | 21 |

Interpretation:

```text
Most directional comparisons place the observed values inside the geometry-control range
or in all-zero equivalence.

A smaller but visible subset places the observed values as more geometry-like
than the tested geometry controls.
```

The favorable label count changed from:

```text
6 → 21
```

because embedding stress was correctly treated as a directional metric.

---

## 9. Changed rows from the refinement patch

The patch changed 108 of 288 rows:

| Metric | Original label | Refined label | Count |
|---|---|---|---:|
| `embedding_stress_2d` | `not_directional` | `observed_more_geometry_like_than_geometry_controls` | 5 |
| `embedding_stress_2d` | `not_directional` | `observed_within_geometry_control_range` | 31 |
| `embedding_stress_3d` | `not_directional` | `observed_more_geometry_like_than_geometry_controls` | 5 |
| `embedding_stress_3d` | `not_directional` | `observed_within_geometry_control_range` | 31 |
| `embedding_stress_4d` | `not_directional` | `observed_more_geometry_like_than_geometry_controls` | 5 |
| `embedding_stress_4d` | `not_directional` | `observed_within_geometry_control_range` | 31 |

Therefore:

```text
Embedding-stress favorable cases: 15
Embedding-stress within-range cases: 93
```

Together with the original negative-eigenvalue-burden favorable cases:

```text
15 stress cases + 6 spectral cases = 21 favorable cases
```

---

## 10. Refined interpretation by metric

### Triangle defects

All triangle-defect comparisons are all-zero equivalent:

```text
observed_geometry_control_equivalent = 36
```

Interpretation:

```text
Observed and geometry-control graphs are equivalent in this sanity check.
This does not prove a physical metric.
```

### Geodesic consistency

All geodesic-consistency directional comparisons lie within the geometry-control range:

```text
observed_within_geometry_control_range = 36
```

Interpretation:

```text
Observed graph objects fall inside the simple geometry-control range
for this geodesic consistency proxy.
```

### Negative eigenvalue burden

Negative eigenvalue burden shows:

```text
observed_within_geometry_control_range = 30
observed_more_geometry_like_than_geometry_controls = 6
```

Interpretation:

```text
Most comparisons are within the geometry-control range.
A small subset, especially involving the N81 full baseline, is more favorable than all tested controls.
```

### Embedding stress

After refinement:

```text
embedding_stress_2d:
  5 more favorable than controls
  31 within control range

embedding_stress_3d:
  5 more favorable than controls
  31 within control range

embedding_stress_4d:
  5 more favorable than controls
  31 within control range
```

Interpretation:

```text
Embedding stress provides the main additional favorable signal after readout refinement.
Most stress comparisons remain within the geometry-control range, but a subset is more favorable
than the tested controls.
```

---

## 11. Favorable cases

The favorable cases after refinement are of two types:

```text
A. embedding-stress favorable cases
B. negative-eigenvalue-burden favorable cases
```

### 11.1 Negative-eigenvalue-burden favorable cases

The original six favorable cases all occur for:

```text
negative_eigenvalue_burden
```

Representative rows:

| Observed object | Control family | Dimension | Weight mode | Observed | Control min | Control median | Control max |
|---|---|---:|---|---:|---:|---:|---:|
| `N81_full_baseline` | `random_geometric_graph` | 3 | `unweighted` | 0.086625 | 0.108481 | 0.206169 | 0.247944 |
| `N81_full_baseline` | `random_geometric_graph` | 4 | `unweighted` | 0.086625 | 0.118654 | 0.216387 | 0.252915 |
| `N81_full_baseline` | `soft_geometric_kernel` | 3 | `unweighted` | 0.086625 | 0.129127 | 0.205171 | 0.259886 |
| `N81_full_baseline` | `soft_geometric_kernel` | 4 | `unweighted` | 0.086625 | 0.133147 | 0.219173 | 0.264106 |

Interpretation:

```text
For these cases, the observed N81 full baseline has lower negative eigenvalue burden
than all tested simple geometry controls.
```

Caution:

```text
This is a spectral proxy result, not a physical geometry proof.
```

### 11.2 Embedding-stress favorable cases

The refinement patch adds:

```text
15 embedding-stress favorable cases
```

These are not new numerical values. They were already present in the original metrics, but were previously labeled as non-directional.

Interpretation:

```text
After correct directional treatment, some observed graph objects show lower embedding stress
than all tested simple geometry controls for specific control-family/dimension/weight-mode settings.
```

Caution:

```text
Lower embedding stress indicates stronger embedding compatibility under the tested diagnostic.
It does not establish physical dimension or physical space.
```

---

## 12. Main BMC-15e finding

### Befund

```text
BMC-15e MVP completed successfully.

The observed BMC-15 graph objects were positioned against simple geometry-generated controls.

After readout-label refinement, most directional comparisons lie inside the geometry-control range
or in all-zero equivalence.

A smaller subset of comparisons is more favorable than all tested geometry controls,
especially in embedding stress and negative eigenvalue burden.
```

### Interpretation

```text
The observed graph objects are not only more favorable than graph-rewire nulls from BMC-15b,
but are also broadly compatible with simple geometry-generated control regimes.

This strengthens the geometry-proxy interpretation.

However, the result is not uniquely specific, because feature-/family-/correlation-structured nulls
from BMC-15b can still produce many similar proxy values.
```

### Hypothesis

```text
The observed relational structures may occupy a geometry-proxy-compatible regime
that is not merely graph-rewire-like and that partially overlaps simple geometry-generated controls.

The favorable stress and spectral cases may point to a specific embedding/spectral profile
of the observed N81 baseline and selected envelopes.
```

### Open gaps

```text
No physical spacetime emergence has been established.
No physical metric has been reconstructed.
No causal structure has been tested.
No Lorentzian signature has been tested.
No light-cone structure has been shown.
No continuum limit has been shown.
Feature-/family-/correlation-structured nulls remain serious alternative explanations.
The mutual-kNN envelope is disconnected and must be read cautiously.
Only simple Euclidean-style MVP controls were active.
Hyperbolic or hierarchical geometry controls remain future work.
```

---

## 13. Relation to BMC-15b

BMC-15b showed:

```text
Observed graph objects are more favorable than graph-rewire nulls,
but feature-/family-/correlation-structured nulls can often produce similar proxy values.
```

BMC-15e refined adds:

```text
Observed graph objects often lie inside the range of simple geometry-generated controls,
and in selected embedding-stress and negative-eigenvalue-burden cases are more favorable
than all tested controls.
```

Combined conservative reading:

```text
The observed geometry-proxy behavior is not merely graph-rewire-like.
It is often compatible with simple geometry-generated controls.
In selected stress/spectral cases it is even more favorable than those controls.
However, because structured feature/family/correlation nulls can also reproduce many proxy values,
the signal remains informative but not uniquely specific.
```

---

## 14. What BMC-15e strengthens

BMC-15e strengthens the following bounded statement:

```text
The observed BMC-15 graph objects occupy a geometry-proxy-compatible region
when compared not only to graph-rewire nulls, but also to simple geometry-generated controls.
```

It also supports:

```text
The observed N81 full baseline has favorable stress/spectral behavior
in selected comparisons relative to the tested geometry controls.
```

---

## 15. What BMC-15e does not show

BMC-15e does not show:

```text
physical spacetime emergence
physical metric reconstruction
causal structure
Lorentzian signature
light-cone structure
continuum geometry
uniqueness against all structured null explanations
```

Blocked wording:

```text
BMC-15e proves geometry.
The observed graph is spacetime-like in the physical sense.
The observed graph reconstructs a metric.
The observed graph has a physical dimension.
```

Allowed wording:

```text
geometry-proxy compatible
embedding-compatible
within geometry-control range
more favorable than tested geometry controls for selected proxies
informative but not uniquely specific
```

---

## 16. Reviewer-facing paragraph

```text
BMC-15e extends the BMC-15 comparison layer by adding explicitly geometry-generated control graph families. In the MVP run, the observed BMC-15 graph objects most often fall within the range of simple Euclidean-style geometry controls or show all-zero equivalence for triangle defects. A readout-label refinement treats embedding-stress diagnostics as directional lower-is-more-embedding-compatible proxies, without recomputing controls or metrics. After this refinement, a subset of embedding-stress and negative-eigenvalue-burden comparisons is more favorable than the tested controls, especially for the N81 full baseline. This positions the observed structures as geometry-proxy compatible with simple geometry-generated scaffolds, but it does not establish physical geometry, causal structure, Lorentzian signature, or spacetime emergence. In combination with BMC-15b, the result remains informative but not uniquely specific, since feature-/family-/correlation-structured nulls can also produce similar proxy values.
```

---

## 17. Internal human summary

```text
Der Klunker liegt bei vielen Diagnostiken im Bereich absichtlich geometrischer Kontrollgerüste.

Das ist gut:
  Er sieht nicht nur besser aus als Graph-Geschüttel,
  sondern passt oft auch in den Bereich einfacher Geometrie-Kontrollen.

Nach dem Stress-Label-Patch sieht man zusätzlich:
  An einigen Stress-/Spektralstellen liegt observed sogar günstiger
  als die getesteten Geometry Controls.

Aber:
  Das ist kein Alleinstellungsbeweis.
  Feature-/Family-/Copula-Nulls bleiben ernst.
  mutual-kNN ist disconnected.
  Hyperbolische Kontrollen fehlen noch.
  Causal/Lorentz ist nicht getestet.

Kurz:
  BMC-15e stärkt die geometry-proxy Lesart,
  aber nicht den Spacetime-Claim.
```

---

## 18. Recommended next steps

### 18.1 Archive this refined result note

This file should replace the earlier BMC-15e result note as the current BMC-15e interpretation basis.

Suggested path:

```text
docs/BMC15E_GEOMETRY_CONTROL_NULLS_RESULT_NOTE.md
```

### 18.2 BMC-15f Envelope-Construction Sensitivity

Next recommended robustness block:

```text
BMC-15f Envelope-Construction Sensitivity
```

Purpose:

```text
Test whether the geometry-proxy behavior remains stable when envelope/backbone construction methods are varied.
```

### 18.3 Hyperbolic or hierarchical controls

Future BMC-15e extension:

```text
hyperbolic / hierarchical geometry controls
```

Requirement:

```text
define generator transparently
avoid over-tuning
match only coarse graph constraints
```

### 18.4 BMC-16 only after BMC-15 robustness

Causal/Lorentzian diagnostics should remain a later line:

```text
first define a defensible directed order
then test causal-set-inspired diagnostics
```

Internal rule:

```text
Erst Pfeil definieren.
Dann Kausalintervalle zählen.
```

---

## 19. Final internal closing sentence

```text
BMC-15e macht aus dem Klunker keine Raumzeit.

Aber nach dem refined readout steht sauber:
Der Klunker liegt oft im Bereich einfacher geometrischer Kontrollgerüste
und ist in ausgewählten Stress-/Spektralvergleichen sogar günstiger als diese Controls.

Das ist eine begrenzte, aber echte Stärkung der Geometry-Proxy-Lesart.
```
