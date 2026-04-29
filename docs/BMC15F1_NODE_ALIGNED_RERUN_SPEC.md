# BMC-15f.1 Node-Aligned Envelope Sensitivity — Specification

## Purpose

BMC-15f.1 addresses the node-space mismatch found after the first BMC-15f MVP.

BMC-15f was technically successful and methodologically useful, but the diagnostic run used a relational input with:

```text
19 nodes
```

whereas the BMC-15/BMC-15e graph-object exports use:

```text
22 nodes
```

Therefore BMC-15f is valid as a sensitivity test on the available relational input, but not yet perfectly node-aligned with the BMC-15/BMC-15e graph-object space.

BMC-15f.1 prepares a node-aligned rerun.

It is not a new physics-claim block. It does not test spacetime emergence, causal structure, Lorentzian signature, light-cone structure, continuum structure, or a physical metric.

---

## 1. Diagnostic finding

BMC-15 graph-object union:

```text
22 nodes
```

BMC-15f relational input:

```text
19 nodes
```

Nodes present in BMC-15 graph objects but missing in BMC-15f relational input:

```text
ring_p_1
ring_p_2
ring_p_3
ring_p_m1
ring_p_m2
ring_p_m3
```

Nodes present in BMC-15f relational input but not in BMC-15 graph objects:

```text
ring_abs_p_1
ring_abs_p_2
ring_abs_p_3
```

---

## 2. Interpretation

The mismatch is structured, not random.

It likely reflects a ring-representation difference:

```text
BMC-15/BMC-15e:
  sign-sensitive ring nodes
  ring_p_1, ring_p_2, ring_p_3, ring_p_m1, ring_p_m2, ring_p_m3

BMC-15f MVP:
  absolute/collapsed ring nodes
  ring_abs_p_1, ring_abs_p_2, ring_abs_p_3
```

Internal short form:

```text
BMC-15f war nützlich,
aber nicht ganz derselbe Spielplatz.
```

---

## 3. Methodological implication

The first BMC-15f MVP answers:

```text
How sensitive are envelope diagnostics under the available 19-node input?
```

It does not fully answer:

```text
How sensitive are envelope diagnostics in the exact 22-node sign-sensitive graph space used by BMC-15/BMC-15e?
```

BMC-15f.1 should therefore run the same sensitivity logic on a 22-node sign-sensitive relational input, if available.

---

## 4. Candidate input sources

Likely candidate files:

```text
data/baseline_relational_table_real.csv
data/baseline_relational_table_real_bmc08b.csv
data/baseline_relational_table_real_bmc08c.csv
data/bmc08c_real_units_feature_table.csv
data/bmc08a_real_units_feature_table.csv
data/bmc08b_real_units_feature_table.csv
```

The likely target is:

```text
data/baseline_relational_table_real_bmc08c.csv
```

because BMC-08c appears to be the sign-sensitive ring variant.

But this must be verified by node-set preflight before use.

---

## 5. Preflight requirement

Before rerunning BMC-15f.1, compare each candidate input against the BMC-15 graph-object union.

For each candidate report:

```text
candidate_path
candidate_exists
candidate_kind
candidate_node_count
graph_union_node_count
missing_nodes_vs_graph_union
extra_nodes_vs_graph_union
exact_match
recommendation
```

Only an exact match, or an explicitly justified near-match, should be used.

---

## 6. Rerun logic

Reuse the existing runner:

```text
scripts/run_bmc15f_envelope_construction_sensitivity.py
```

with a new config:

```text
data/bmc15f1_node_aligned_envelope_sensitivity_config.yaml
```

Recommended output directory:

```text
runs/BMC-15f1/node_aligned_envelope_sensitivity_open/
```

Keep the BMC-15f MVP family grid:

```text
mutual_kNN_k_sweep:
  k = [2, 3, 4, 5, 6]

threshold_sweep:
  top_fraction = [0.02, 0.03, 0.05, 0.08, 0.10]

spanning_tree_variants:
  maximum_spanning_tree
  minimum_distance_spanning_tree
```

---

## 7. Comparison questions after rerun

Compare BMC-15f and BMC-15f.1:

```text
1. Does connectedness improve, worsen, or stay similar?
2. Does core containment remain partial/full in similar parameter regimes?
3. Do threshold variants still fragment?
4. Does mutual-kNN still show parameter sensitivity?
5. Are geometry-proxy metrics stable across node alignment?
6. Does the result strengthen or weaken the construction-qualified interpretation?
```

---

## 8. Interpretation templates

If BMC-15f.1 reproduces the same pattern:

```text
The construction-sensitivity conclusion is robust to node-space alignment.
Envelope morphology remains method-dependent, while the compact core remains partially persistent.
```

If BMC-15f.1 differs strongly:

```text
The first BMC-15f result was sensitive not only to envelope construction,
but also to node representation / ring representation.
Envelope-level conclusions must therefore be qualified by node-space alignment.
```

If BMC-15f.1 improves connectedness:

```text
The sign-sensitive 22-node representation may be a more suitable graph space for envelope-construction sensitivity testing.
```

Blocked:

```text
The node-aligned rerun proves physical geometry.
```

---

## 9. Risk register

| Risk | Mitigation |
|---|---|
| Treating BMC-15f MVP as fully aligned despite 19/22 mismatch | Explicit BMC-15f.1 node-alignment rerun |
| Silently replacing sign-sensitive ring nodes with absolute ring nodes | Node-set audit before rerun |
| Overinterpreting improved connectedness | Keep geometry-proxy wording |
| Confusing node-representation sensitivity with physics | Treat as methodological sensitivity only |
| Running BMC-15f.1 on wrong candidate input | Require preflight exact node comparison |

---

## 10. Final internal sentence

```text
BMC-15f hat gezeigt:
Die Hülle hängt an der Küchenmaschine.

BMC-15f.1 fragt jetzt:
Passiert das auch, wenn wir dieselbe Werkbank benutzen
wie bei BMC-15/BMC-15e?
```
