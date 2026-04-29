# BMC-15f.2 Connectedness-Transition Sweep — Result Note

## Purpose

BMC-15f.2 extends the BMC-15f.1 envelope-construction sensitivity analysis.

BMC-15f.1 showed that, on the canonical 22-node sign-sensitive representation, compact-core containment is strong while mutual-kNN and threshold variants remain disconnected in the initially tested parameter range.

BMC-15f.2 asks:

```text
At which construction parameters do mutual-kNN and threshold variants become connected,
and does the compact reference core remain retained before, at, and after the connectedness transition?
```

This is a methodological robustness / transition-mapping block.

It does not test physical spacetime emergence, causal structure, Lorentzian signature, a light cone, a continuum limit, or a physical metric.

---

## 1. Run metadata

Run directory:

```text
runs/BMC-15f2/connectedness_transition_sweep_open/
```

Postprocessing outputs:

```text
connectedness_transition_summary.csv
connectedness_transition_readout.md
```

Input workspace:

```text
canonical 22-node sign-sensitive BMC-08c representation
```

Node count:

```text
22
```

Families tested:

```text
mutual_kNN_k_transition_sweep
threshold_transition_sweep
spanning_tree_transition_anchors
```

---

## 2. Transition summary

| Family | Status | First connected parameter | Connected variants | Total variants | Core min | Core median | Core max |
|---|---|---:|---:|---:|---:|---:|---:|
| `mutual_kNN_k_transition_sweep` | `transition_found` | `k = 7` | 9 | 14 | 1.000000 | 1.000000 | 1.000000 |
| `threshold_transition_sweep` | `transition_found` | `top_fraction = 0.28` | 2 | 19 | 0.833333 | 1.000000 | 1.000000 |
| `spanning_tree_transition_anchors` | `always_connected` | by construction | 2 | 2 | 1.000000 | 1.000000 | 1.000000 |

Main result:

```text
Both mutual-kNN and threshold constructions reach connectedness within the extended sweep.

mutual-kNN first becomes connected at k = 7.
threshold first becomes connected at top_fraction = 0.28.

The compact reference core remains fully retained at and beyond both connectedness transitions.
```

---

## 3. mutual-kNN connectedness transition

Parameter sweep:

```text
k = 2..15
```

Transition:

```text
first connected k = 7
```

Pre-transition:

| k | Edges | Connected | Core containment |
|---:|---:|---:|---:|
| 2 | 17 | false | 1.000000 |
| 3 | 25 | false | 1.000000 |
| 4 | 34 | false | 1.000000 |
| 5 | 44 | false | 1.000000 |
| 6 | 55 | false | 1.000000 |

At transition:

| k | Edges | Connected | Core containment |
|---:|---:|---:|---:|
| 7 | 64 | true | 1.000000 |

Post-transition:

| k range | Connected | Core containment |
|---|---:|---:|
| 8–15 | true | 1.000000 throughout |

Interpretation:

```text
The compact core is fully retained before the graph becomes connected,
at the connectedness transition,
and after connectedness is achieved.
```

This directly addresses the BMC-15f.1 limitation:

```text
The mutual-kNN core-retention signal is not merely a disconnected-graph artifact under this sweep.
```

---

## 4. threshold connectedness transition

Parameter sweep:

```text
top_fraction = 0.02..0.30
```

Transition:

```text
first connected top_fraction = 0.28
```

Pre-transition:

```text
top_fraction = 0.02..0.26
connected = false
```

Core containment in pre-transition regime:

```text
minimum = 0.833333
median  = 1.000000
maximum = 1.000000
```

At transition:

| top_fraction | Edges | Connected | Core containment |
|---:|---:|---:|---:|
| 0.28 | 65 | true | 1.000000 |

Post-transition:

| top_fraction | Edges | Connected | Core containment |
|---:|---:|---:|---:|
| 0.30 | 69 | true | 1.000000 |

Interpretation:

```text
The threshold construction requires a much denser graph before connectedness appears.
However, the compact core is already nearly fully retained before connectedness and fully retained at the transition.
```

This means:

```text
The threshold family remains connectivity-sensitive,
but core containment does not collapse at the connectedness transition.
```

---

## 5. spanning-tree anchors

Spanning-tree variants:

```text
maximum_spanning_tree
minimum_distance_spanning_tree
```

Status:

```text
always connected
```

Core containment:

```text
1.000000
```

Interpretation:

```text
Spanning-tree anchors remain useful as connected reference constructions,
but their connectedness and edge count are algorithmically imposed.

Their full core containment is supportive but not sufficient as independent evidence of natural connectedness.
```

---

## 6. Geometry-proxy behavior around transition

### 6.1 mutual-kNN

Selected transition-region values:

| k | Connected | Edges | Core | Stress 2D | Stress 3D | Stress 4D | Neg. eig. burden | Geodesic error |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 6 | false | 55 | 1.000000 | 0.046306 | 0.036522 | 0.035567 | 0.059927 | 0.526102 |
| 7 | true | 64 | 1.000000 | 0.075245 | 0.041721 | 0.038881 | 0.053343 | 0.518148 |
| 8 | true | 71 | 1.000000 | 0.077339 | 0.048061 | 0.044780 | 0.068858 | 0.511895 |

Observation:

```text
Core containment remains unchanged at full retention.
Embedding stress and spectral burden change with k and should remain parameter-qualified.
Geodesic consistency error trends downward with increasing k in the connected range.
```

### 6.2 threshold

Selected transition-region values:

| top_fraction | Connected | Edges | Core | Stress 2D | Stress 3D | Stress 4D | Neg. eig. burden | Geodesic error |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 0.26 | false | 60 | 1.000000 | 0.070145 | 0.043377 | 0.038224 | 0.042189 | 0.508673 |
| 0.28 | true | 65 | 1.000000 | 0.079031 | 0.047269 | 0.042935 | 0.055725 | 0.514518 |
| 0.30 | true | 69 | 1.000000 | 0.072903 | 0.043763 | 0.041074 | 0.064206 | 0.521551 |

Observation:

```text
Core containment remains fully retained at and after threshold connectedness.
Geometry-proxy metrics remain parameter-dependent and do not become construction-invariant merely because the graph is connected.
```

---

## 7. Main BMC-15f.2 finding

### Befund

```text
BMC-15f.2 finds connectedness transitions for both previously disconnected envelope families.

mutual-kNN first becomes connected at k = 7.
threshold first becomes connected at top_fraction = 0.28.

The compact reference core remains fully retained at both transition points and remains fully retained in the connected post-transition regimes tested.
```

### Interpretation

```text
The compact core is not merely a sparse disconnected-graph artifact in the tested construction families.

Connectedness transitions are construction-family specific:
mutual-kNN becomes connected at moderate k,
whereas threshold requires a relatively dense edge fraction.

Broad envelope geometry-proxy metrics remain parameter-dependent, so connectedness does not remove envelope construction sensitivity.
```

### Hypothesis

```text
The compact local core represents a more stable support-side structure than the broader envelope morphology.
It remains recoverable across sparse, transitional, and connected construction regimes in the canonical 22-node sign-sensitive representation.
```

### Open gaps

```text
The sweep is still limited to one 22-node dataset / representation.
The result does not establish specificity against structured feature/family/correlation nulls.
Spanning-tree connectedness remains algorithmically imposed.
Distance-based metrics before connectedness still require caution.
No causal or Lorentzian diagnostics are included.
```

---

## 8. Relation to BMC-15f.1

BMC-15f.1 showed:

```text
mutual-kNN and threshold were disconnected in the initial parameter grid.
core containment was strong.
```

BMC-15f.2 adds:

```text
mutual-kNN becomes connected at k = 7.
threshold becomes connected at top_fraction = 0.28.
core containment remains full through both transitions.
```

Therefore the BMC-15f.1 limitation is partially resolved:

```text
The core-containment signal survives entry into connected graph regimes.
```

But the envelope-level conclusion remains qualified:

```text
The broad envelope still depends on construction family and parameter setting.
```

---

## 9. Relation to BMC-15e and BMC-15e.2

BMC-15e:

```text
geometry-control compatibility on full 22-node observed graph objects
```

BMC-15e.2 preflight:

```text
verified full observed graph-object node alignment with the canonical 22-node BMC-08c workspace
```

BMC-15f.2:

```text
shows that compact-core retention survives connectedness transitions on the same canonical 22-node workspace
```

Combined conservative reading:

```text
The BMC-15 series now supports a construction-qualified geometry-proxy interpretation centered on a persistent compact local core.
The broad envelope remains method-dependent.
```

---

## 10. Updated project-level interpretation

Before BMC-15f.2:

```text
The core remains strong in the node-aligned run,
but mutual-kNN and threshold are disconnected in the tested settings.
```

After BMC-15f.2:

```text
The core remains strong even when mutual-kNN and threshold enter connected regimes.
```

Updated internal statement:

```text
The core is not only visible in sparse/disconnected constructions.
It survives the connectedness transition.
```

This is a meaningful methodological strengthening.

It still remains proxy-level, not physical-spacetime evidence.

---

## 11. Allowed and blocked language

### Allowed

```text
connectedness-transition sweep
first connected k = 7
first connected top_fraction = 0.28
core retained across connectedness transition
compact core not merely a disconnected-graph artifact under tested constructions
broad envelope remains construction-sensitive
geometry-proxy robustness
```

### Use carefully

```text
robust core
stable local scaffold
geometry-like behavior
```

These should remain qualified by:

```text
tested parameter range
canonical 22-node sign-sensitive representation
geometry-proxy diagnostics
```

### Blocked

```text
connectedness proves geometry
core containment proves spacetime
connected graph implies physical metric
BMC-15f.2 establishes causal structure
BMC-15f.2 establishes Lorentzian signature
```

---

## 12. Reviewer-facing paragraph

```text
BMC-15f.2 extends the node-aligned envelope-construction sensitivity analysis by mapping connectedness transitions in the previously disconnected mutual-kNN and threshold construction families. On the canonical 22-node sign-sensitive representation, mutual-kNN first becomes connected at k = 7, while the threshold construction first becomes connected at top_fraction = 0.28. In both families, the compact reference core remains fully retained at the transition point and in the tested connected post-transition regimes. This reduces the concern that the core-containment signal is merely a disconnected sparse-graph artifact. However, broader envelope-level diagnostics remain parameter- and construction-dependent, so the result supports a construction-qualified geometry-proxy interpretation rather than physical geometry or spacetime emergence.
```

---

## 13. Next recommended block

BMC-15f.2 strengthens the core-persistence picture.

The next most useful block is likely:

```text
BMC-15g Core Perturbation Robustness
```

Main question:

```text
Does the compact reference core remain recoverable under controlled node, edge, and weight perturbations?
```

Candidate perturbations:

```text
edge deletion
edge weight noise
node jackknife
feature noise
family-preserving perturbations
```

Why next:

```text
BMC-15f.2 shows the core survives construction connectedness transitions.
The next question is whether it also survives perturbations of the relational data itself.
```

Alternative:

```text
BMC-15h Structured-null specificity extension
```

This addresses uniqueness / specificity rather than stability.

Recommended order:

```text
1. BMC-15g core perturbation robustness
2. BMC-15h structured-null specificity extension
3. BMC-16 causal/Lorentzian diagnostics only later
```

---

## 14. Human summary

```text
Jetzt wird es interessant.

mutual-kNN:
  wird ab k = 7 zusammenhängend.
  Der Kern war vorher drin,
  ist beim Übergang drin,
  und bleibt danach drin.

threshold:
  braucht viel mehr Dichte.
  Erst bei top_fraction = 0.28 connected.
  Aber auch dort bleibt der Kern drin.

Das heißt:
  Der Kern ist nicht nur ein Konfetti-/Sparse-Graph-Artefakt.

Aber:
  Die große Hülle bleibt parameter- und methodenabhängig.
```

---

## 15. Final internal sentence

```text
Der Kobold connectedness hat gebellt,
aber er hat den Kern nicht gefressen.

Das ist kein Raumzeitpokal.
Aber es ist ein guter Robustheitsbefund für den Klunker.
```
