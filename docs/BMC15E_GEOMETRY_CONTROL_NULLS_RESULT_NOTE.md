# BMC-15e Geometry-Control Nulls — Result Note

## Purpose

This note summarizes the first BMC-15e MVP run.

BMC-15e adds explicitly geometry-generated control graph families to the BMC-15 geometry-proxy comparison layer. The purpose is not to prove geometry, but to ask where the observed BMC-15 graph objects sit relative to simple geometry-generated control graphs.

This remains a geometry-proxy diagnostic. It does not establish physical spacetime emergence, causal structure, Lorentzian signature, light-cone structure, or a physical metric.

---

## 1. Run metadata

Run:

```text
BMC-15e_geometry_control_nulls_mvp
```

Output directory:

```text
runs/BMC-15e/geometry_control_nulls_open/
```

Primary outputs:

```text
summary.json
geometry_control_metrics.csv
family_summary.csv
observed_position_summary.csv
readout.md
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

---

## 2. Observed graph objects loaded

| Object | Nodes | Edges | Connected |
|---|---:|---:|---|
| `N81_full_baseline` | 22 | 81 | True |
| `maximum_spanning_tree_envelope` | 22 | 21 | True |
| `mutual_kNN_k3_envelope` | 22 | 23 | False |

Important caution:

```text
mutual_kNN_k3_envelope is disconnected.
Its distance-based diagnostics are affected by disconnected-graph handling
and should be read cautiously.
```

---

## 3. Control families

The MVP used two explicitly geometry-generated control families:

```text
random_geometric_graph
soft_geometric_kernel
```

Control dimensions:

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
200 per object / family / dimension / weight-mode combination
```

---

## 4. Position-label counts

Observed-vs-geometry-control label counts:

| Label | Count |
|---|---:|
| `not_directional` | 180 |
| `observed_within_geometry_control_range` | 66 |
| `observed_geometry_control_equivalent` | 36 |
| `observed_more_geometry_like_than_geometry_controls` | 6 |

Interpretation:

```text
Most directional comparisons place the observed values inside the geometry-control range
or in all-zero equivalence.

Only a small subset of comparisons places the observed value as more geometry-like
than the tested geometry controls.
```

---

## 5. Label counts by observed object

| Observed object | not_directional | geometry_control_equivalent | more_geometry_like_than_controls | within_geometry_control_range |
|---|---:|---:|---:|---:|
| `N81_full_baseline` | 60 | 12 | 4 | 20 |
| `maximum_spanning_tree_envelope` | 60 | 12 | 0 | 24 |
| `mutual_kNN_k3_envelope` | 60 | 12 | 2 | 22 |

Interpretation:

```text
The maximum-spanning-tree envelope is entirely within-range or equivalent for directional metrics.
The N81 full baseline has four cases where negative eigenvalue burden is lower than all tested controls.
The mutual-kNN envelope has two such cases, but this graph is disconnected and therefore needs caution.
```

---

## 6. Label counts by control family

| Control family | not_directional | geometry_control_equivalent | more_geometry_like_than_controls | within_geometry_control_range |
|---|---:|---:|---:|---:|
| `random_geometric_graph` | 90 | 18 | 4 | 32 |
| `soft_geometric_kernel` | 90 | 18 | 2 | 34 |

Interpretation:

```text
The two MVP control families give broadly similar positioning.
There is no strong sign that the result is driven by only one of the two simple geometry-control families.
```

---

## 7. Label counts by metric

| Metric | not_directional | geometry_control_equivalent | more_geometry_like_than_controls | within_geometry_control_range |
|---|---:|---:|---:|---:|
| `embedding_stress_2d` | 36 | 0 | 0 | 0 |
| `embedding_stress_3d` | 36 | 0 | 0 | 0 |
| `embedding_stress_4d` | 36 | 0 | 0 | 0 |
| `geodesic_consistency_error` | 0 | 0 | 0 | 36 |
| `local_dimension_proxy` | 36 | 0 | 0 | 0 |
| `negative_eigenvalue_burden` | 0 | 0 | 6 | 30 |
| `negative_eigenvalue_count` | 36 | 0 | 0 | 0 |
| `triangle_defects` | 0 | 36 | 0 | 0 |

Interpretation:

```text
The active directional signal in the MVP is concentrated in:

  geodesic_consistency_error
  negative_eigenvalue_burden
  triangle_defects

Triangle defects are all-zero equivalent.
Geodesic consistency is always within the geometry-control range.
Negative eigenvalue burden is mostly within the geometry-control range, with six cases
where the observed value is lower than all geometry controls.
```

Important caveat:

```text
Embedding stress is currently labeled not_directional in the position summary.
This is likely a labeling/configuration issue rather than a substantive absence of stress information,
because embedding stress is a directional diagnostic in the BMC-15 logic.

A follow-up readout refinement should include embedding_stress_2d/3d/4d as lower-is-more-geometry-like.
```

---

## 8. Cases where observed is more geometry-like than geometry controls

All six `observed_more_geometry_like_than_geometry_controls` cases occur for:

```text
negative_eigenvalue_burden
```

| Observed object | Control family | Dimension | Weight mode | Observed | Control min | Control median | Control max |
|---|---|---:|---|---:|---:|---:|---:|
| `N81_full_baseline` | `random_geometric_graph` | 3 | `unweighted` | 0.086625 | 0.108481 | 0.206169 | 0.247944 |
| `N81_full_baseline` | `random_geometric_graph` | 4 | `unweighted` | 0.086625 | 0.118654 | 0.216387 | 0.252915 |
| `N81_full_baseline` | `soft_geometric_kernel` | 3 | `unweighted` | 0.086625 | 0.129127 | 0.205171 | 0.259886 |
| `N81_full_baseline` | `soft_geometric_kernel` | 4 | `unweighted` | 0.086625 | 0.133147 | 0.219173 | 0.264106 |
| `mutual_kNN_k3_envelope` | `random_geometric_graph` | 4 | `observed_rank_remap` | 0.010796 | 0.012149 | 0.050687 | 0.124092 |
| `mutual_kNN_k3_envelope` | `random_geometric_graph` | 4 | `unweighted` | 0.010796 | 0.015275 | 0.054978 | 0.151094 |

Interpretation:

```text
The strongest favorable observed-vs-geometry-control deviations appear in negative eigenvalue burden,
especially for the N81 full baseline under unweighted 3D/4D geometry controls.

This suggests that the observed N81 baseline is not worse than simple geometry controls under this proxy,
and in a few settings has lower negative-eigenvalue burden than all tested controls.

However, this remains proxy-specific and does not establish physical geometry.
```

---

## 9. Main BMC-15e finding

### Befund

```text
The BMC-15e MVP completed successfully and positioned three observed graph objects
against two simple geometry-generated control families.

For directional metrics, most observed values are within the geometry-control range
or all-zero equivalent.

A small subset of negative-eigenvalue-burden comparisons places the observed value
below all tested geometry-control values.
```

### Interpretation

```text
The observed BMC-15 graph objects are broadly compatible with simple geometry-control regimes
under several geometry-proxy diagnostics.

This is informative because BMC-15b showed that the observed structures were more favorable
than graph-rewire nulls, while feature-structured nulls often generated similar proxy values.

BMC-15e adds a positive comparison anchor:
the observed graph objects often fall within explicitly geometry-generated control ranges.
```

### Hypothesis

```text
The observed relational structures may occupy a geometry-proxy regime that is not merely graph-rewire-like
and is partly compatible with simple geometry-generated scaffolds.

The negative-eigenvalue-burden deviations may indicate a specific spectral feature of the observed
N81 baseline relative to simple unweighted Euclidean controls.
```

### Open gaps

```text
No physical geometry has been established.
No causal structure has been tested.
No Lorentzian signature has been tested.
No light-cone structure has been shown.
No continuum limit has been shown.
Embedding-stress position labels need readout refinement.
The mutual-kNN result is affected by disconnectedness.
Only simple Euclidean-style MVP controls were active; hyperbolic controls remain disabled.
```

---

## 10. Relation to BMC-15b

BMC-15b result:

```text
Observed graph objects are more favorable than graph-rewire nulls,
but feature-/family-/correlation-structured nulls can often produce similar proxy values.
```

BMC-15e adds:

```text
Observed graph objects often lie inside the range of explicitly geometry-generated MVP controls,
with a small number of favorable negative-eigenvalue-burden deviations.
```

Combined conservative reading:

```text
The observed geometry-proxy behavior is not merely graph-rewire-like.
It is often compatible with simple geometry-generated controls.
However, because feature-structured nulls can also reproduce many proxy values,
the signal remains informative but not uniquely specific.
```

---

## 11. Recommended readout refinement

The current position summary labels all embedding-stress metrics as:

```text
not_directional
```

Recommended refinement:

```text
embedding_stress_2d: lower_is_more_geometry_like
embedding_stress_3d: lower_is_more_geometry_like
embedding_stress_4d: lower_is_more_geometry_like
```

Reason:

```text
Embedding stress is a central directional proxy in the BMC-15 series.
Lower normalized stress corresponds to stronger embedding compatibility under the tested construction.
```

This refinement should be implemented as a readout/labeling improvement. It should not change the generated control metrics.

---

## 12. Recommended next steps

Immediate:

```text
BMC-15e readout refinement:
  include embedding_stress_2d/3d/4d in directional labels
  preserve all metrics
  do not recompute controls unless necessary
```

Next numerical extension:

```text
BMC-15e second pass:
  activate toy_hyperbolic_control only after checking generator transparency
  or add a clearer hyperbolic / hierarchical geometry-control family
```

Parallel robustness block:

```text
BMC-15f Envelope-Construction Sensitivity:
  test whether the geometry-proxy behavior survives envelope-construction changes
```

---

## 13. Reviewer-facing cautious paragraph

```text
BMC-15e adds explicitly geometry-generated control families to the BMC-15 comparison layer.
In the MVP run, the observed BMC-15 graph objects most often fall within the range of simple
Euclidean-style geometry controls or show all-zero equivalence for triangle defects. A small subset
of negative-eigenvalue-burden comparisons, especially for the N81 full baseline, is more favorable
than the tested controls. This positions the observed structures as geometry-proxy compatible with
simple geometry-generated scaffolds, but it does not establish physical geometry, causal structure,
Lorentzian signature, or spacetime emergence. In combination with BMC-15b, the result remains
informative but not uniquely specific, since feature-/family-/correlation-structured nulls can also
produce similar proxy values.
```

---

## 14. Internal human summary

```text
Der Klunker liegt bei vielen Diagnostiken im Bereich absichtlich geometrischer Kontrollgerüste.

Das ist gut:
  Er sieht nicht nur besser aus als Graph-Geschüttel,
  sondern passt oft auch in den Bereich einfacher Geometrie-Kontrollen.

Aber:
  Das ist kein Alleinstellungsbeweis.
  Feature-/Family-/Copula-Nulls bleiben ernst.
  mutual-kNN ist disconnected.
  Embedding-Stress muss im Label-Readout noch sauber directional gemacht werden.

Kurz:
  BMC-15e stärkt die geometry-proxy Lesart,
  aber nicht den Spacetime-Claim.
```
