# BMC-15e.2 Node-Aligned Geometry-Control Repetition — Preflight Specification

## Purpose

BMC-15e.2 is the next BMC-15 continuation block after BMC-15f.1 and the Qwewn3 synthesis.

BMC-15e established geometry-control compatibility against simple geometry-generated controls.  
BMC-15f.1 then showed that the canonical 22-node sign-sensitive representation materially improves compact-core containment.

Therefore BMC-15e.2 asks:

```text
Do the BMC-15e geometry-control conclusions remain stable when the geometry-control comparison
is explicitly audited and, if needed, rerun on the canonical 22-node sign-sensitive representation?
```

This is a methodological alignment / robustness block.

It does not test physical spacetime emergence, causal structure, Lorentzian signature, a light cone, a continuum limit, or a physical metric.

---

## 1. Motivation

External synthesis from Qwewn3 recommended:

```text
BMC-15e.2 — Node-aligned geometry-control repetition
```

Reason:

```text
BMC-15f.1 showed that node representation matters.
The compact core becomes much more persistent in the exact 22-node sign-sensitive workspace.
Therefore the central geometry-control comparison from BMC-15e should be audited or repeated under the same canonical representation.
```

---

## 2. Canonical node-space

Canonical node-space for BMC-15e.2:

```text
data/bmc08c_real_units_feature_table.csv
```

Expected node count:

```text
22
```

This file was selected because the BMC-15f.1 preflight found it to be an exact match to the BMC-15 graph-object union.

The sign-sensitive ring nodes should be preserved:

```text
ring_p_1
ring_p_2
ring_p_3
ring_p_m1
ring_p_m2
ring_p_m3
```

The collapsed absolute-ring representation should not be used as canonical for this block:

```text
ring_abs_p_1
ring_abs_p_2
ring_abs_p_3
```

---

## 3. Preflight goal

Before rerunning BMC-15e controls, perform an alignment audit.

The audit should check:

```text
1. canonical feature-table node set
2. BMC-15 graph-object union node set
3. each observed graph-object node set
4. current BMC-15e summary metadata, if available
5. current BMC-15e observed objects and counts
6. whether existing BMC-15e already used the same 22-node graph-object space
```

This matters because BMC-15e may already be node-aligned at the observed-graph-object level.

If BMC-15e is already node-aligned, BMC-15e.2 may become:

```text
alignment-certified BMC-15e readout
```

rather than a full recomputation.

If the audit shows ambiguity, perform a full rerun with explicit BMC-08c alignment metadata.

---

## 4. Preflight decision logic

### Case A — exact alignment already verified

If:

```text
canonical node set == graph-object union
and observed objects have the expected 22-node graph space where applicable
and BMC-15e summary confirms compatible graph-object inputs
```

then the safe conclusion is:

```text
BMC-15e was already aligned at the observed graph-object level.
BMC-15e.2 should document the alignment and optionally rerun only for provenance clarity.
```

### Case B — partial alignment or ambiguity

If:

```text
canonical node set == graph-object union
but BMC-15e metadata does not document this clearly
```

then:

```text
BMC-15e.2 should rerun using explicit node-aligned config and write alignment metadata.
```

### Case C — mismatch

If:

```text
canonical node set != graph-object union
or observed objects differ unexpectedly
```

then:

```text
stop and diagnose before rerun.
```

---

## 5. Expected preflight outputs

Recommended output directory:

```text
runs/BMC-15e2/node_aligned_geometry_control_preflight_open/
```

Expected files:

```text
node_alignment_summary.csv
readout.md
```

Field list:

| Field name | Field type | Description |
|---|---|---|
| `object_name` | string | Name of audited object or candidate input. |
| `object_kind` | string | `canonical_feature_table`, `graph_object`, `graph_union`, or `bmc15e_summary`. |
| `path` | string | Source path. |
| `exists` | boolean | Whether the source exists. |
| `node_count` | integer/string | Number of inferred nodes, or blank if not applicable. |
| `missing_vs_canonical` | JSON list string | Nodes missing relative to canonical BMC-08c node set. |
| `extra_vs_canonical` | JSON list string | Nodes present but not in canonical node set. |
| `exact_match_canonical` | boolean/string | Whether node set equals canonical node set, if applicable. |
| `notes` | string | Additional audit notes. |

---

## 6. Full rerun target

If a full rerun is needed, recommended output directory:

```text
runs/BMC-15e2/node_aligned_geometry_control_nulls_open/
```

Recommended run ID:

```text
BMC-15e2_node_aligned_geometry_control_nulls_mvp
```

Comparison target:

```text
BMC-15e_geometry_control_nulls_mvp
```

The rerun should preserve BMC-15e settings as much as possible:

```text
control families:
  random_geometric_graph
  soft_geometric_kernel

dimensions:
  2, 3, 4

weight modes:
  unweighted
  observed_rank_remap

replicates:
  same as BMC-15e, unless explicitly changed
```

---

## 7. Interpretation templates

### If BMC-15e.2 agrees with BMC-15e

```text
The geometry-control compatibility result is stable under explicit node-alignment auditing / rerun.
This strengthens the BMC-15e interpretation without changing its claim boundary.
```

### If BMC-15e.2 strengthens the favorable rows

```text
The sign-sensitive 22-node representation improves not only core containment but also selected geometry-control proxy positions.
This supports the representation-aligned geometry-proxy interpretation.
```

### If BMC-15e.2 weakens the favorable rows

```text
The geometry-control result is representation-sensitive and must be qualified accordingly.
The compact-core persistence may remain stronger than the broad geometry-control signal.
```

### Blocked

```text
BMC-15e.2 proves physical geometry.
BMC-15e.2 establishes spacetime emergence.
BMC-15e.2 demonstrates causal or Lorentzian structure.
```

---

## 8. Next-step decision after preflight

After running the preflight, decide:

```text
1. audit-only result note
2. full BMC-15e.2 rerun
3. config patch before rerun
4. stop due to mismatch
```

Preferred internal rule:

```text
No rerun before node alignment is documented.
```

---

## 9. Human summary

```text
BMC-15f.1 hat gezeigt:
Auf der richtigen 22-node Werkbank sitzt der Kern deutlich stabiler.

BMC-15e.2 fragt jetzt:
War auch unser zentraler Geometrie-Kontrollvergleich sauber auf dieser Werkbank,
oder müssen wir ihn explizit node-aligned wiederholen?
```

---

## 10. Final internal sentence

```text
Erst prüfen wir, ob BMC-15e schon auf derselben Werkbank stand.
Dann entscheiden wir, ob BMC-15e.2 ein Zertifikat oder ein echter neuer Lauf wird.
```
