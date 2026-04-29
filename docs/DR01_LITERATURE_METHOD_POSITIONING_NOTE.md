# DR-01 Literature and Methodology Positioning Note

## Purpose

This note records the project-level implications of the Deep Research literature and methodology scan.

It does not replace the full Deep Research report. Instead, it translates the report into a practical positioning and control roadmap for the Quantum-Spacetime Bridge / QSB project.

The central question is:

```text
How should the current graph-based BMC workflow be framed so that it remains scientifically cautious, methodologically defensible, and literature-adjacent without overclaiming physical spacetime emergence?
```

---

## 1. Main conclusion from DR-01

The Deep Research scan identifies two relevant literature layers:

```text
1. Physics / emergent-locality layer
2. Methodological graph / network-science layer
```

The physics layer includes:

```text
Quantum Graphity
causal sets
spin networks
group field theory
tensor networks
entanglement-based geometry reconstruction
relational approaches
```

The methodological layer includes:

```text
similarity graphs
correlation networks
graph sparsification
backbone extraction
threshold sensitivity
feature ablation
leave-one-feature-out diagnostics
null models
high-dimensional neighborhood artifacts
```

### Project implication

The current QSB/BMC workflow is best positioned not as a proof of emergent spacetime, but as:

```text
methodological robustness diagnostics for a relational locality-backbone proxy
```

or in German:

```text
methodische Robustheitsdiagnostik für einen relationalen Lokalitäts-Backbone
```

This is the strongest currently defensible positioning.

---

## 2. What the physics literature supports

The emergent-spacetime literature supports the broad idea that locality or geometry can sometimes be studied through relational structures such as:

```text
graphs
causal orders
entanglement patterns
tensor networks
spin-network connectivity
correlation or mutual-information structures
```

However, the literature also makes a strict limitation clear:

```text
A graph alone is not physical spacetime.
```

In established approaches, graph-like or relational structures gain physical meaning only together with additional structure, for example:

```text
dynamics
causal order
state class
geometric labels
renormalization structure
continuum-limit criteria
explicit reconstruction criteria
```

### Project implication

QSB should not claim:

```text
emergent spacetime has been shown
```

or:

```text
physical geometry has been reconstructed
```

The safer claim is:

```text
a locality-like relational substructure is being tested as an operational proxy
```

---

## 3. What the methodology literature supports

The closest technical neighborhood is not primarily quantum gravity, but network science and graph methodology.

Important neighboring methods and concerns:

```text
graph construction from feature vectors
thresholded similarity graphs
density-matched graph comparison
graph backbone extraction
top-k and kNN-like local rules
feature ablation / LOFO / LOCO
null-model filtering
sparsity path analysis
high-dimensional nearest-neighbor artifacts
```

### Project implication

The BMC workflow should be framed as a graph-methodology pipeline applied to a physically motivated relational feature table.

This framing is stronger than presenting it as a direct physical model.

---

## 4. Recommended terminology

Use:

```text
relational feature-space graph
local backbone candidate
locality proxy
locality-like substructure
operational geometry proxy
sparse/local backbone regime
backbone persistence
density-matched control
matched-edge-count leave-one-out
ablation robustness profile
sparsity-path diagnostic
methodological robustness diagnostic
```

Use with caution:

```text
manifold-likeness proxy
emergent locality
geometry-like structure
relational reconstruction
```

Only use these with explicit operational definitions.

Avoid or strongly qualify:

```text
proof of emergent spacetime
reconstruction of physical geometry
derivation of locality
evidence for spacetime emergence
physical feature hierarchy
causal feature importance
```

---

## 5. Best current project framing

A compact project framing:

> This work develops methodological robustness diagnostics for a relational locality-backbone proxy. Weighted graphs are constructed from standardized, physically motivated feature vectors and tested for reproducible sparse/local backbone structure under controlled sparsification, feature ablation, edge-count sweeps, and red-team motivated robustness checks. The current results are diagnostic and operational; they do not by themselves establish physical spacetime emergence.

A shorter version:

> QSB currently tests whether relational feature-space graphs contain reproducible locality-like backbone structure under controlled graph-construction and robustness diagnostics.

German internal version:

> QSB prüft derzeit, ob relationale Feature-Space-Graphen unter kontrollierter Graphkonstruktion und Robustheitsdiagnostik reproduzierbare lokalitätsähnliche Backbone-Strukturen zeigen. Das ist ein methodischer Lokalitäts-Proxy, kein Nachweis emergenter physikalischer Raumzeit.

---

## 6. Reviewer objections identified by DR-01

The Deep Research scan identifies several likely reviewer objections.

### 6.1 Graph construction may dominate the result

Reviewer concern:

```text
The observed structure may be produced by the graph constructor rather than by the underlying relational feature space.
```

Project response:

BMC-12 already tests feature-ablation and matched edge count, but more work is needed:

```text
BMC-13 alternative graph/backbone filters
BMC-14 null-model controls
```

### 6.2 Thresholding and density matching are not neutral

Reviewer concern:

```text
Matched edge count controls graph size, but it can also insert or remove different edge classes in different feature spaces.
```

Project response:

BMC-12e directly tests graph-size sensitivity across:

```text
N = 70, 75, 81, 87, 92
```

BMC-12e found that the BMC09d all-feature baseline is stable across:

```text
N = 70, 75, 81
```

but weakens at:

```text
N = 87, 92
```

This supports the updated interpretation:

```text
BMC09d is a sparse/local backbone-regime anchor.
```

### 6.3 Top-k / top-alpha may encode structure assumptions

Reviewer concern:

```text
The chosen backbone extraction rules may themselves induce the apparent scale structure.
```

Project response:

Current BMC-12 uses:

```text
strength_topk_6
strength_topalpha_025
strength_topalpha_050
```

Future work should compare alternative backbone methods.

Potential next block:

```text
BMC-13 Alternative Backbone / Consensus-Backbone Filters
```

Candidate alternatives:

```text
threshold path
kNN / mutual-kNN
disparity-like filter
noise-corrected / null-model filter
salience / spanning-tree style backbone
consensus backbone across methods
```

### 6.4 Similarity is not geometry

Reviewer concern:

```text
A similarity or correlation graph does not automatically imply physical geometry.
```

Project response:

Current wording must stay operational:

```text
locality proxy
geometry-like ordering
relational backbone candidate
```

Future geometry-facing tests could include:

```text
embedding stress
triangle-inequality defects
local dimension estimators
neighborhood consistency
geodesic-distance stability
```

These are not yet part of BMC-12.

### 6.5 Leave-one-feature-out is not causal feature attribution

Reviewer concern:

```text
LOFO / LOCO-style ablation is hard to interpret when features are correlated or interacting.
```

Project response:

BMC-12 should not be described as causal feature attribution.

Allowed:

```text
feature-ablation sensitivity
joint-feature-basis sensitivity
structured leave-one-out profile
```

Avoid:

```text
causal feature importance
```

Future checks:

```text
feature correlation matrix
grouped ablations
leave-two-out
restandardization vs frozen-standardization comparison
permutation importance / null feature controls
```

### 6.6 Threshold paths are not independent replications

Reviewer concern:

```text
Graph results across nearby thresholds or densities are correlated and cannot be treated as independent samples.
```

Project response:

BMC-12e should be treated as a sparsity-path diagnostic, not as five independent confirmations.

Allowed:

```text
the baseline remains stable across a sparse/local edge-count range
```

Avoid:

```text
five independent replications
```

---

## 7. Mapping DR-01 to existing BMC blocks

### Already addressed

| Concern | Addressed by | Current status |
|---|---|---|
| Wrong feature source | BMC-12 reconciliation | fixed: BMC08c exact baseline |
| Fixed-tau densification | BMC-12b | matched-edge-count control |
| Feature single-dominance | BMC-12c | trivial single-feature dominance weakened |
| Single N=81 artifact | BMC-12e | graph-size sensitivity tested |
| Red-team interpretation risk | BMC-12d | integration note and Grok addendum |

### Still open

| Concern | Needed block |
|---|---|
| Decision threshold brittleness | BMC-12f |
| Top-k/top-alpha method dependence | BMC-13 |
| Null feature / covariance artifact | BMC-14 |
| Strong geometry interpretation | later geometry-proxy diagnostics |
| Feature correlation / higher-order interactions | later LOFO/LTO or grouped ablation block |

---

## 8. Updated roadmap after DR-01

Recommended next sequence:

```text
BMC-12f Decision-Threshold / Dominance-Gap Sensitivity Sweep
BMC-13 Alternative Backbone / Consensus-Backbone Filters
BMC-14 Null-Model or Covariance-Preserving Feature Controls
DR-02 Physics-facing positioning and bibliography note
```

### BMC-12f

Purpose:

```text
Test whether the BMC09d / BMC-12e sparse-local regime survives small changes in decision thresholds.
```

Focus edge counts:

```text
N = 70, 75, 81
```

because these are the edge counts where the all-feature baseline remained 3/3 retained in BMC-12e.

Suggested grid:

```text
arrangement_signal_min = 0.045, 0.050, 0.055
dominance_gap_min     = 0.020, 0.030, 0.040
```

### BMC-13

Purpose:

```text
Test whether the sparse/local backbone regime depends on top-k/top-alpha extraction rules.
```

### BMC-14

Purpose:

```text
Test whether comparable patterns arise in permuted, randomized, or covariance-preserving feature controls.
```

---

## 9. Consequence for BMC-12e interpretation

DR-01 strengthens the interpretation of BMC-12e.

BMC-12e should not be described as proving feature roles.

It should be described as showing:

```text
the BMC09d all-feature backbone decision persists across a sparse/local edge-count range N=70,75,81
```

and:

```text
the BMC-12c N=81 feature-retention profile is graph-size sensitive
```

Therefore the current strongest BMC-12-level statement is:

> BMC-12 identifies a sparse/local edge-count regime in which the reconciled BMC09d all-feature backbone decision remains stable, while feature-ablation profiles remain graph-size sensitive and should not yet be interpreted as a stable feature hierarchy.

---

## 10. Conservative external paragraph

A suitable paragraph for a research note:

> The present analysis should be read as a methodological robustness diagnostic for a relational locality-backbone proxy. After reconciling the feature source to the BMC08c-compatible table, the BMC09d threshold_tau_03 reference graph is exactly reproduced. Matched-edge-count leave-one-out tests weaken a trivial single-feature dominance explanation, but subsequent edge-count neighborhood sweeps show that the detailed ablation profile is graph-size sensitive. The all-feature backbone decision remains stable only across a sparse-to-reference edge-count range, suggesting a sparse/local backbone regime rather than a graph-density-independent feature hierarchy. No claim of physical spacetime emergence or geometry reconstruction is made.

---

## 11. Important caution

The DR-01 report supports the current direction, but it does not validate the physical interpretation.

It reinforces the project's best discipline:

```text
Befund
Interpretation
Hypothesis
Open gap
```

and confirms that the BMC workflow should continue as a controlled methodology pipeline before any stronger physics-facing claim is attempted.

---

## 12. File anchors

Full Deep Research report:

```text
deep-research-report(18).md
```

Related project notes:

```text
docs/BMC12_ABC_FEATURE_DOMINANCE_RESULT_NOTE.md
docs/BMC12D_RED_TEAM_INTEGRATION_NOTE.md
docs/BMC12D_RED_TEAM_INTEGRATION_ADDENDUM_GROK.md
docs/BMC12E_EDGECOUNT_NEIGHBORHOOD_RESULT_NOTE.md
```

Suggested new file:

```text
docs/DR01_LITERATURE_METHOD_POSITIONING_NOTE.md
```
