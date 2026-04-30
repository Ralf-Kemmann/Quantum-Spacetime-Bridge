# BMC-15f Series — Envelope Construction Sensitivity Consolidated Note

## 1. Purpose

This note consolidates the BMC-15f envelope-construction sensitivity line:

- **BMC-15f** — initial envelope-construction sensitivity MVP.
- **BMC-15f1** — node-aligned rerun on the canonical 22-node basis.
- **BMC-15f2** — connectedness-transition sweep on the canonical 22-node basis.

The purpose is to separate two questions:

1. How construction-sensitive are the observable envelope/backbone structures?
2. Does the compact reference core remain contained across these construction variants?

This note is a methodological consolidation. It does not claim physical spacetime emergence, a physical metric, causal structure, Lorentzian signature, or a continuum limit.

## 2. Run overview

### BMC-15f

- Output directory: `runs/BMC-15f/envelope_construction_sensitivity_open`
- Input kind: `edge_table`
- Nodes: `19`
- Variant metric rows: `12`
- Edge-overlap rows: `36`
- Core-containment rows: `12`
- Warnings: none

BMC-15f is useful as an initial construction-sensitivity probe, but it carries a node-basis caveat because it used a 19-node input.

### BMC-15f1

- Output directory: `runs/BMC-15f1/node_aligned_envelope_sensitivity_open`
- Input kind: `wide_feature_table`
- Nodes: `22`
- Variant metric rows: `12`
- Edge-overlap rows: `36`
- Core-containment rows: `12`
- Warnings: none

BMC-15f1 is the corrected node-aligned rerun and is therefore the cleaner reference for the BMC-15 series.

### BMC-15f2

- Output directory: `runs/BMC-15f2/connectedness_transition_sweep_open`
- Input kind: `wide_feature_table`
- Nodes: `22`
- Variant metric rows: `35`
- Edge-overlap rows: `105`
- Core-containment rows: `35`
- Warnings: none

BMC-15f2 extends the node-aligned setting by scanning the transition from sparse/disconnected envelopes to denser/connected envelopes.

## 3. Connectedness and construction sensitivity

### BMC-15f: initial 19-node MVP

| Envelope family | Variants | Connected rate | Median edges | Edge range |
|---|---:|---:|---:|---|
| `mutual_kNN_k_sweep` | 5 | 0.200 | 29.0 | 15–46 |
| `spanning_tree_variants` | 2 | 1.000 | 18.0 | 18–18 |
| `threshold_sweep` | 5 | 0.000 | 9.0 | 3–17 |

### BMC-15f1: node-aligned 22-node rerun

| Envelope family | Variants | Connected rate | Median edges | Edge range |
|---|---:|---:|---:|---|
| `mutual_kNN_k_sweep` | 5 | 0.000 | 34.0 | 17–55 |
| `spanning_tree_variants` | 2 | 1.000 | 21.0 | 21–21 |
| `threshold_sweep` | 5 | 0.000 | 12.0 | 5–23 |

### BMC-15f2: node-aligned connectedness-transition sweep

| Envelope family | Variants | Connected rate | Median edges | Edge range |
|---|---:|---:|---:|---|
| `mutual_kNN_k_transition_sweep` | 14 | 0.643 | 75.0 | 17–133 |
| `spanning_tree_transition_anchors` | 2 | 1.000 | 21.0 | 21–21 |
| `threshold_transition_sweep` | 19 | 0.105 | 28.0 | 5–69 |

## 4. Core-containment summary

The reference core has 6 edges in all reported containment tables.

### BMC-15f: initial 19-node MVP

| Family | Variants | Full containment | Partial containment | Fraction range |
|---|---:|---:|---:|---|
| `mutual_kNN_k_sweep` | 5 | 3 | 2 | 0.667–1.000 |
| `threshold_sweep` | 5 | 0 | 5 | 0.500–0.833 |
| `spanning_tree_variants` | 2 | 0 | 2 | 0.667–0.667 |

BMC-15f already shows partial-to-strong containment, especially for mutual-kNN at k ≥ 4. However, because the input has 19 nodes, it should be treated as an informative MVP rather than the canonical result.

### BMC-15f1: node-aligned 22-node rerun

| Family | Variants | Full containment | Partial containment | Fraction range |
|---|---:|---:|---:|---|
| `mutual_kNN_k_sweep` | 5 | 5 | 0 | 1.000–1.000 |
| `threshold_sweep` | 5 | 4 | 1 | 0.833–1.000 |
| `spanning_tree_variants` | 2 | 2 | 0 | 1.000–1.000 |

BMC-15f1 is the key correction: after node alignment, the compact reference core is fully contained in all mutual-kNN variants, all spanning-tree variants, and all but the sparsest threshold variant. The sparsest threshold setting still contains 5 of 6 core edges.

### BMC-15f2: node-aligned connectedness-transition sweep

| Family | Variants | Full containment | Partial containment | Fraction range |
|---|---:|---:|---:|---|
| `mutual_kNN_k_transition_sweep` | 14 | 14 | 0 | 1.000–1.000 |
| `threshold_transition_sweep` | 19 | 18 | 1 | 0.833–1.000 |
| `spanning_tree_transition_anchors` | 2 | 2 | 0 | 1.000–1.000 |

BMC-15f2 strengthens the containment picture. Across the transition sweep, the compact core is retained in all mutual-kNN variants, all spanning-tree anchors, and every threshold variant except the sparsest top-fraction 0.02 setting, which still retains 5 of 6 core edges.

## 5. Consolidated finding

The BMC-15f series gives a clean split:

1. **Envelope-level structure is construction-sensitive.**  
   Connectedness and edge count vary strongly with construction family and parameter choice. Spanning trees are connected by construction, threshold envelopes remain disconnected at sparse settings, and mutual-kNN connectedness depends strongly on k and density.

2. **The compact reference core remains strongly contained after node alignment.**  
   In the canonical 22-node runs, core containment is almost always complete. The only non-complete cases are the sparsest threshold settings, and even those retain 5 of 6 core edges.

3. **The initial 19-node BMC-15f run should be treated as a useful MVP, not the final reference.**  
   BMC-15f1 and BMC-15f2 are the appropriate canonical continuation because they use the node-aligned 22-node basis.

## 6. Interpretation

The envelope should not be read as a unique physical geometry. It is a method-dependent graph construction around the relational structure.

However, the compact core behaves differently from the larger envelope. Once the node-basis mismatch is corrected, the core appears as a stable local structure anchor inside multiple envelope constructions and across the connectedness-transition sweep.

In internal language:

```text
Die Nebelschale ändert ihre Form.
Der Klunker bleibt im relevanten 22-node-Regime sichtbar.
```

## 7. Relation to BMC-15g

BMC-15g adds an independent robustness angle:

- BMC-15f/f1/f2: construction sensitivity of envelopes and core containment.
- BMC-15g: perturbation robustness of the compact core.

Together, they support a bounded methodological statement:

```text
The large envelope is construction- and parameter-sensitive,
but the compact local core proxy remains stable across node-aligned
construction variants and is robust under small topological perturbations.
```

The boundary from BMC-15g remains important: the top-strength core reconstruction is sensitive to weight-rank perturbations.

## 8. Conservative conclusion

BMC-15f/f1/f2 support a construction-qualified geometry-proxy statement:

```text
Envelope-level geometry proxies are method-dependent and should not be
interpreted as a unique physical geometry. In the canonical node-aligned
runs, however, the compact reference core is consistently retained across
multiple envelope families and through connectedness-transition sweeps.
```

This strengthens the BMC-15 series by distinguishing a stable local core from broader, method-dependent envelopes.

## 9. Recommended next step

The next useful step is not another envelope run, but a compact synthesis layer:

```text
BMC-15h or BMC-15-series synthesis:
  combine BMC-15e, BMC-15f/f1/f2, and BMC-15g
  into one defensively worded claim-boundary note.
```

Suggested framing:

```text
geometry-proxy compatibility:
  supported as a bounded methodological signal

local core stability:
  supported under node-aligned construction variants and small topological perturbations

envelope uniqueness:
  not supported

physical spacetime interpretation:
  not established
```
