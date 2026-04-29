# BMC-15e.2 Node-Aligned Geometry-Control Preflight — Result Note

## Purpose

This note records the result of the BMC-15e.2 node-alignment preflight.

The preflight was introduced because BMC-15f.1 showed that the 22-node sign-sensitive representation is methodologically important for core containment. Therefore the central BMC-15e geometry-control comparison needed an explicit alignment audit.

This is an audit / provenance note.

It does not regenerate geometry controls.
It does not test physical spacetime emergence, causal structure, Lorentzian signature, light-cone structure, continuum structure, or a physical metric.

---

## 1. Run metadata

Preflight output directory:

```text
runs/BMC-15e2/node_aligned_geometry_control_preflight_open/
```

Generated files:

```text
node_alignment_summary.csv
readout.md
```

Decision emitted by the audit:

```text
partial_alignment_graph_union_matches_but_some_objects_are_subgraphs
```

This decision is conservative. It is triggered because the graph-object union matches the canonical 22-node space, while one graph object is intentionally a smaller core subgraph.

---

## 2. Canonical input

Canonical node-aligned input:

```text
data/bmc08c_real_units_feature_table.csv
```

Inferred kind:

```text
wide_or_node_table
```

Node count:

```text
22
```

Match to canonical node set:

```text
exact_match_canonical: true
```

This confirms that the BMC-08c sign-sensitive feature table remains the canonical 22-node workspace.

---

## 3. Graph-object alignment results

The preflight found:

| Object | Kind | Nodes | Exact canonical match |
|---|---|---:|---:|
| `canonical_bmc08c_feature_table` | `canonical_feature_table` | 22 | true |
| `N81_full_baseline` | `graph_object` | 22 | true |
| `maximum_spanning_tree_envelope` | `graph_object` | 22 | true |
| `mutual_kNN_k3_envelope` | `graph_object` | 22 | true |
| `threshold_path_consensus_envelope` | `graph_object` | 22 | true |
| `top_strength_reference_core` | `graph_object` | 9 | false |
| `graph_object_union` | `graph_union` | 22 | true |

Interpretation:

```text
All full observed graph objects used by BMC-15e match the canonical 22-node sign-sensitive workspace.

The only non-matching graph object is top_strength_reference_core, which is expected because it is a compact 9-node core subgraph, not a full 22-node envelope graph.
```

Therefore the audit decision should be read as:

```text
BMC-15e full observed graph-object alignment is verified.
The apparent partial alignment is explained by an intentionally smaller core subgraph.
```

---

## 4. Current BMC-15e summary metadata

The existing BMC-15e summary was found:

```text
runs/BMC-15e/geometry_control_nulls_open/summary.json
```

Summary metadata:

```text
run_id: BMC-15e_geometry_control_nulls_mvp
n_control_metric_rows: 7200
n_family_summary_rows: 36
n_observed_position_rows: 288
warnings: []
claim_boundary: Geometry-proxy comparison only. No physical geometry, causal structure, Lorentzian signature, or spacetime emergence is established.
```

Interpretation:

```text
BMC-15e already used the canonical 22-node graph-object space for the full observed graph objects.
```

---

## 5. Main preflight finding

### Befund

```text
The BMC-15 graph-object union exactly matches the canonical BMC-08c 22-node sign-sensitive feature-table node set.

The full observed graph objects used in BMC-15e are each exact 22-node matches.

The compact top_strength_reference_core is a 9-node subgraph and is expected not to match the full canonical node set.
```

### Interpretation

```text
BMC-15e does not require correction for the 19-node vs 22-node mismatch seen in the first BMC-15f MVP.

The BMC-15e geometry-control comparison was already aligned at the full observed graph-object level.
```

### Hypothesis

```text
The BMC-15f MVP mismatch came from using a collapsed 19-node relational input table for envelope sensitivity,
not from the BMC-15/BMC-15e graph-object exports themselves.
```

### Open caveat

```text
This preflight verifies observed graph-object node alignment.
It does not prove that every internal geometry-control generation detail is representation-aware beyond the graph-object level.
If stricter provenance is desired, a full BMC-15e.2 rerun can still be performed, but it is not required to fix a discovered node mismatch.
```

---

## 6. Consequence for BMC-15e.2

The most economical interpretation is:

```text
BMC-15e.2 can be treated as an alignment-certified audit note rather than an immediately necessary full rerun.
```

Recommended label:

```text
BMC-15e.2 alignment-certified geometry-control audit
```

A full rerun is optional, not mandatory.

A full rerun may still be justified if the project wants:

```text
cleaner provenance
explicit BMC-08c input metadata in all run outputs
fresh output folder under BMC-15e2
exact reproducibility package for reviewers
```

But based on the audit:

```text
No node-space mismatch was found in the full BMC-15e observed graph objects.
```

---

## 7. Relation to BMC-15f and BMC-15f.1

BMC-15f MVP:

```text
used a 19-node collapsed absolute-ring input
therefore not fully node-aligned with the BMC-15 observed graph-object space
```

BMC-15f.1:

```text
used the 22-node sign-sensitive BMC-08c feature-table representation
showed much stronger core containment
```

BMC-15e.2 preflight:

```text
shows that BMC-15e observed graph objects were already aligned with the 22-node canonical graph-object space
```

Combined interpretation:

```text
The node mismatch was a BMC-15f MVP input issue, not a BMC-15e observed graph-object issue.
```

---

## 8. Updated consolidated interpretation

The current BMC-15 line can now be stated more cleanly:

```text
BMC-15e:
  geometry-control comparison on full 22-node observed graph objects,
  alignment now audited and certified.

BMC-15f:
  useful 19-node MVP envelope sensitivity test,
  but not canonical node-aligned.

BMC-15f.1:
  canonical 22-node node-aligned envelope sensitivity test,
  showing strong compact-core persistence and continued envelope construction sensitivity.
```

This strengthens the internal documentation chain.

---

## 9. Reviewer-facing paragraph

```text
A BMC-15e.2 node-alignment preflight was performed after BMC-15f.1 showed that the sign-sensitive 22-node representation is important for envelope-sensitivity analysis. The audit verified that the BMC-15 graph-object union and all full observed BMC-15e graph objects match the canonical BMC-08c 22-node sign-sensitive node set. The only non-matching object is the 9-node top-strength reference core, which is expected because it is a compact subgraph rather than a full envelope graph. Thus the BMC-15e geometry-control comparison does not require correction for the 19-node input mismatch seen in the first BMC-15f MVP. The audit supports treating BMC-15e as node-aligned at the observed graph-object level, while retaining the original geometry-proxy claim boundary.
```

---

## 10. Allowed and blocked language

### Allowed

```text
BMC-15e observed graph-object node alignment is verified
BMC-15e.2 preflight certifies full graph-object alignment
top_strength_reference_core is an expected subgraph exception
BMC-15f MVP mismatch was input-specific
BMC-15f.1 remains the canonical node-aligned envelope-sensitivity run
```

### Use carefully

```text
BMC-15e is node-aligned
```

Preferred:

```text
BMC-15e is node-aligned at the full observed graph-object level.
```

### Blocked

```text
BMC-15e.2 proves geometry
alignment certification strengthens physical spacetime claims
the 9-node core mismatch is an error
all objects must be 22-node objects
```

---

## 11. Next recommended step

Since BMC-15e full observed graph-object alignment is verified, the next most useful block is now likely:

```text
BMC-15f.2 Connectedness-Transition Sweep
```

Reason:

```text
BMC-15f.1 still shows disconnected mutual-kNN and threshold variants.
Connectedness-transition mapping directly addresses the biggest remaining limitation of the envelope-sensitivity diagnostics.
```

Suggested BMC-15f.2 scope:

```text
mutual-kNN:
  k = 2..15

threshold:
  top_fraction = 0.02..0.30

readouts:
  connectedness transition
  core containment across transition
  embedding stress on connected regimes
  negative eigenvalue burden on connected regimes
  edge overlap with BMC-15 reference envelopes
```

Alternative optional step:

```text
BMC-15e.2 provenance rerun
```

Only needed if a fresh rerun directory with explicit alignment metadata is desired.

---

## 12. Human summary

```text
Gute Nachricht:
BMC-15e stand offenbar schon auf der richtigen 22-node Werkbank.

Der Preflight meckert nur deshalb "partial",
weil der top_strength_reference_core absichtlich ein 9-node Klunker ist.

Das ist kein Fehler.
Das ist der Kern.

Damit ist BMC-15e nicht vom 19-node Problem aus BMC-15f betroffen.
Das 19-node Problem war ein Inputproblem des ersten f-MVP.

Nächster sinnvoller Maschinenraum:
BMC-15f.2 connectedness transition.
```

---

## 13. Final internal sentence

```text
BMC-15e braucht wahrscheinlich kein Pflaster.
BMC-15e hat jetzt ein Werkbank-Zertifikat.

Der nächste echte Kobold sitzt bei connectedness:
Wann werden mutual-kNN und threshold zusammenhängend,
und bleibt der Kern dann immer noch sitzen?
```
