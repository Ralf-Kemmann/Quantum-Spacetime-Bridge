# BMC-15 Series Geometry-Proxy Consolidated Note

## Purpose

This note consolidates the BMC-15 geometry-proxy series after:

```text
BMC-15a  observed geometry-proxy diagnostics
BMC-15b  geometry-proxy null comparison
BMC-15b  readout / label refinement patch
BMC-15d  red-team integration
```

The goal is to provide one coherent, reviewer-facing account of what the BMC-15 series shows, what it does not show, and what should follow next.

This is a consolidation note, not a new numerical result.

---

## 1. Position in the project

The BMC-15 series follows the BMC-14 robustness series.

The BMC-14 series addressed core identity robustness:

```text
Can the observed compact N=81 core be reconstructed by tested null families?
```

The BMC-15 series asks a different question:

```text
Given the observed core/envelope graph objects,
do they show geometry-like proxy consistency,
and how does that behavior compare to null graph objects?
```

These two layers must remain separate.

```text
BMC-14:
  core identity robustness

BMC-15:
  geometry-like proxy behavior of observed and null graph objects
```

The BMC-15 series does not convert core robustness into physical geometry.

---

## 2. Working objects

The BMC-15 diagnostics evaluate observed graph objects such as:

```text
N81_full_baseline
top_strength_reference_core
maximum_spanning_tree_envelope
mutual_kNN_k3_envelope
threshold_path_consensus_envelope
```

BMC-15b compares corresponding observed and null-derived graph objects, including:

```text
null_N81_full
null_top_strength_core
null_maximum_spanning_tree
null_mutual_kNN_k3
```

The exact graph-object definitions and runner logic remain part of the BMC-15/BMC-15b specification files and should not be redefined here.

---

## 3. Diagnostics used

The BMC-15 geometry-proxy layer uses diagnostics such as:

```text
triangle inequality defects
normalized embedding stress
negative eigenvalue burden
shell-growth proxies
local dimension proxy
geodesic consistency
```

These are deliberately called geometry-proxy diagnostics.

They measure compatibility with certain geometry-like consistency patterns under the tested constructions.

They do not measure physical spacetime.

They do not reconstruct a physical metric.

They do not derive causal order.

They do not establish Lorentzian structure.

---

## 4. BMC-15a observed baseline

BMC-15a evaluated the observed graph objects without a null comparison.

Main observed-level findings:

```text
direct triangle defects:
  zero in the observed cases considered

embedding stress:
  low to moderately low for larger observed graph objects

larger envelopes:
  stable sparse-scaffold shell-growth proxy behavior

compact core alone:
  too small and fragmented for standalone geometry interpretation
```

Interpretation:

```text
The observed envelope-level structures show geometry-like proxy consistency.
The compact core alone should not be interpreted as a standalone geometry object.
```

Conservative reading:

```text
BMC-15a motivates a null comparison.
It does not by itself establish specificity.
```

---

## 5. Why BMC-15b was necessary

BMC-15a only described the observed case.

The necessary next question was:

```text
Are the observed geometry-like proxy values special,
or do null graph objects show similar values?
```

This matters because sparse graph extraction and backbone/envelope construction can generate visually or numerically geometry-like patterns even when the underlying mechanism is not specific.

Internal short form:

```text
Does our Klunker glimmer specifically,
or do null Klumpen glimmer too?
```

---

## 6. BMC-15b null families

BMC-15b used two conceptually different null-family groups.

### 6.1 Graph-rewire nulls

Examples:

```text
weight_rank_edge_rewire
degree_preserving_edge_rewire
degree_weightclass_edge_rewire
```

Question addressed:

```text
Is the observed geometry-proxy behavior reproduced by generic graph topology,
degree preservation, or weight-rank / weight-class structure?
```

---

### 6.2 Feature-structured nulls

Examples:

```text
global_covariance_gaussian
family_covariance_gaussian
gaussian_copula_feature_null
```

Question addressed:

```text
Is the observed geometry-proxy behavior reproduced by feature, family,
or correlation structure?
```

---

## 7. BMC-15b main result

The key BMC-15b pattern is:

```text
Against graph-rewire nulls:
  observed geometry-proxy values are often more favorable,
  especially for embedding-related quantities.

Against feature-/family-/correlation-structured nulls:
  observed geometry-proxy values are often null-typical.
```

Representative example:

```text
N81_full_baseline, degree_preserving_edge_rewire, stress_normalized

observed:
  2D = 0.107
  3D = 0.063
  4D = 0.061

null median:
  2D = 0.361
  3D = 0.234
  4D = 0.167
```

Interpretation:

```text
The observed graph is not merely behaving like a degree-preserving graph-rewire null
for the embedding-stress diagnostics.

However, feature/family/correlation-structured nulls can often generate similar
geometry-proxy values.
```

Conservative claim:

```text
The BMC-15b signal is informative but not uniquely specific.
```

---

## 8. BMC-15b label refinement patch

The BMC-15b readout contained a label artifact in all-zero tie cases.

Problem case:

```text
observed = 0
null_min = 0
null_max = 0
```

Incorrect label:

```text
observed_less_geometry_like_than_null
```

Correct label:

```text
observed_null_equivalent
```

Patch interpretation:

```text
The patch changed readout labels and presentation logic.
It did not change the underlying numerical diagnostics.
```

Methodological decision:

```text
All-zero observed/null ties should be treated as null-equivalent,
not as less geometry-like.
```

---

## 9. BMC-15d red-team integration

BMC-15d integrated feedback from Claude, Grok, and Louis.

### 9.1 Claude

Accepted points:

```text
The all-zero tie-handling correction is methodologically necessary.
The graph-rewire vs feature-structured null grouping is conceptually important.
The result note is required for a full review.
```

Integration:

```text
Patch logic confirmed.
Null-family separation strengthened.
```

---

### 9.2 Grok

Accepted points:

```text
The current diagnostics are useful but weak geometry proxies.
They do not test causal, directed, Lorentzian, or light-cone-like structure.
Embedding compatibility does not imply physical geometry.
Visualizations must remain diagnostic, not rhetorical.
```

Follow-up candidates:

```text
Random Geometric Graph controls
Hyperbolic Random Graph controls
stress-diagnosed layouts
later causal-proxy pre-study
```

Rejected or postponed as current evidence:

```text
Myrheim–Meyer dimension
```

Reason:

```text
Myrheim–Meyer-type diagnostics require a defensible directed causal order or poset.
The current BMC-15 graph objects are not yet causal structures.
```

---

### 9.3 Louis

Accepted points:

```text
BMC-15d should be an interpretation and communication layer.
Backbone/envelope methods may share algorithmic biases.
Alternative explanations must remain visible.
```

Revised wording:

```text
Do not say:
  The core is not random.

Say:
  The tested null families do not fully reconstruct the observed compact core identity.
```

---

## 10. Consolidated interpretation

### Befund

```text
The observed N81 core identity remains difficult to fully reconstruct within
the tested BMC-14 null families.

The observed BMC-15 envelope-level graph objects show geometry-like proxy consistency.

In BMC-15b, observed graph objects are more embedding-compatible than graph-rewire nulls
for key embedding-related diagnostics.

Feature-/family-/correlation-structured nulls can often generate geometry-proxy values
in the observed range.

The BMC-15b patch corrected all-zero tie labels without changing numerical diagnostics.
```

---

### Interpretation

```text
The BMC-15 series provides bounded methodological evidence for geometry-like
proxy consistency in the observed relational core/envelope structures.

The observed behavior is not merely reproduced by graph-rewiring controls.

However, the behavior is not uniquely specific, because structured feature/family/correlation
nulls can often produce similar proxy values.

The result is therefore informative, nontrivial with respect to graph-rewire controls,
and substantially linked to structured relational feature content.
```

---

### Hypothesis

```text
The relational structure may contain feature-organized constraints that support
geometry-like proxy consistency at the envelope level.

This motivates further analysis of which feature/family components contribute to
embedding compatibility, shell behavior, and negative-eigenvalue burden.
```

---

### Open gaps

```text
No physical spacetime emergence has been established.
No physical metric has been reconstructed.
No causal structure has been derived.
No Lorentzian signature has been tested.
No light-cone structure has been shown.
No continuum limit has been shown.
No uniqueness against all structured null explanations has been established.
No independent dataset/family replication has yet confirmed the geometry-proxy behavior.
```

---

## 11. Allowed language

Use:

```text
geometry-like proxy consistency
embedding compatibility
bounded methodological evidence
informative but not uniquely specific
more favorable than graph-rewire controls
structured feature/family/correlation contribution
observed core identity not fully reconstructed by tested nulls
post-hoc diagnostic unless preregistered
```

Use carefully, always with proxy qualification:

```text
geometry-like
dimension-like
metric-like
shell growth
negative eigenvalue burden
core/envelope morphology
```

Avoid or block:

```text
spacetime emergence shown
physical metric reconstructed
causal structure derived
Lorentzian signature detected
light-cone structure found
continuum recovered
geometry proven
the core is not random
all null explanations excluded
physical dimension measured
```

---

## 12. Reviewer-facing paragraph

```text
The BMC-15 geometry-proxy diagnostics provide bounded methodological evidence for
geometry-like consistency in the observed relational core/envelope structures.
The observed N81 baseline and selected envelopes are generally more embedding-compatible
than graph-rewire controls, particularly with respect to normalized embedding stress
and negative-eigenvalue burden. However, feature-, family-, and correlation-structured
null models often generate proxy values in the observed range. The result therefore
does not establish physical spacetime emergence, causal structure, Lorentzian signature,
or a physical metric. Rather, it indicates that the observed geometry-proxy behavior is
informative, nontrivial with respect to graph-rewiring controls, and substantially linked
to structured relational feature content.
```

---

## 13. Internal human summary

```text
Der Klunker bleibt interessant.

Er ist schwer vollständig nachzubauen
und er sieht in seinen Hüllen geometry-like geordnet aus.

Gegen Graph-Rewire-Nulls ist das deutlich nicht-trivial.

Aber:
Feature-/Family-/Copula-Nulls können ähnliche Proxy-Werte erzeugen.

Also:
Der Befund ist informativ,
aber nicht eindeutig spezifisch.

BMC-15 ist Geometry-Proxy.
Nicht Raumzeit.
Nicht Metrik.
Nicht Kausalstruktur.
```

---

## 14. Recommended next steps

### 14.1 BMC-15e Geometry-Control Nulls

Purpose:

```text
Compare observed geometry-proxy behavior against explicitly geometry-generated controls.
```

Candidate controls:

```text
Random Geometric Graphs
Hyperbolic Random Graphs
soft geometry-matched graph controls
```

Diagnostic value:

```text
Clarifies whether observed graph objects resemble graph-rewire nulls,
feature-structured nulls, or explicitly geometry-generated graph families.
```

---

### 14.2 BMC-15f Envelope-Construction Sensitivity

Purpose:

```text
Test whether geometry-proxy behavior is stable under envelope construction changes.
```

Candidate variations:

```text
MST variants
mutual-kNN k sweeps
threshold-path consensus variants
sparse-path consensus variants
parameter sweeps
```

Diagnostic value:

```text
Separates robust envelope-level behavior from method-induced morphology.
```

---

### 14.3 BMC-16 Causal-Proxy Pre-Study

Purpose:

```text
Define whether a directed order or causal-proxy graph can be constructed defensibly.
```

Only after that:

```text
Myrheim–Meyer dimension
midpoint-scaling dimension
causal interval diagnostics
```

Diagnostic value:

```text
Prevents causal-set tools from being applied to an undirected proxy-distance setup without
a justified arrow.
```

---

## 15. Recommended project sequence

```text
1. Archive this consolidated BMC-15 note.
2. Use it as the reviewer-facing summary of the BMC-15 series.
3. Start BMC-15e Geometry-Control Nulls or BMC-15f Envelope-Construction Sensitivity.
4. Keep visualizations diagnostic until the next control layer is complete.
5. Treat causal/Lorentzian diagnostics as a separate later BMC-16 line.
```

---

## 16. Final internal closing sentence

```text
BMC-15 macht den Klunker nicht zur Raumzeit.
Aber BMC-15 zeigt, dass sein geometry-proxy Verhalten nicht bloß Graph-Geschüttel ist
und zugleich stark an Feature-/Family-/Korrelationsstruktur hängt.

Das ist kein Endpunkt.
Das ist eine saubere, prüfbare Arbeitsposition.
```
