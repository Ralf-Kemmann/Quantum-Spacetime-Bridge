# BMS-FU02g4c — Orbit-Reduced / Resumable Connected Patch Enumeration Specification

Date: 2026-05-03  
Project: Gravitation und RaumZeit / Quantum-Spacetime-Bridge  
Recommended repo target: `docs/BMS_FU02G4C_ORBIT_REDUCED_RESUMABLE_CONNECTED_PATCH_ENUMERATION_SPEC.md`  
Status: Specification and implementation block

---

## 1. Purpose

BMS-FU02g4c follows the bounded FU02g4b result.

FU02g4b-v2 enumerated:

```text
3,682,435 connected 17-face C60 patches
status = partial_timeout_reached
carrier exact matches = 20
carrier near matches = 127
role-colored exact matches = 0
role-colored near matches = 3
```

FU02g4c asks:

```text
Can the connected-patch enumeration be made resumable and optionally reduced
under the 120 face-type-preserving C60 automorphisms?
```

Internal formulation:

```text
Nicht noch ein langer Lauf auf gut Glück.
Jetzt machen wir das zählbar, fortsetzbar und orbit-sicher.
```

---

## 2. Scope

BMS-FU02g4c is a methodological hardening block.

Allowed:

```text
enumerate connected same-size C60 face patches in deterministic chunks
resume enumeration from checkpoint-like state
canonicalize patches under observed face-graph automorphisms if networkx is available
count raw patches and orbit-canonical patch classes
count exact and near reference signatures
report completion or partial status
```

Not allowed:

```text
claim exhaustive completion unless enumeration_status == complete
claim uniqueness beyond the tested signature/canonicalization definitions
claim physical spacetime
claim molecular quantum chemistry
claim real-structure-memory proof
claim universal p-values
```

---

## 3. Design goals

FU02g4c addresses three limitations of FU02g4b:

### 3.1 Timeout dependence

FU02g4b stopped after 900 seconds.

FU02g4c writes chunk outputs so progress is not lost.

### 3.2 Duplicate / orbit redundancy

FU02g4 already found:

```text
automorphism_count_observed = 120
carrier_orbit_size_observed = 120
role_colored_orbit_size_observed = 120
```

FU02g4c can canonicalize patches under the observed automorphism group.

### 3.3 Auditability

FU02g4c emits:

```text
chunk manifests
aggregate summary
canonical orbit representative counts
match examples
warnings
```

---

## 4. Inputs

Required:

```text
data/bms_fu02g_c60_reference_cells.csv
data/bms_fu02g_c60_reference_edges.csv
runs/BMS-FU02f1/face_id_interval_repair_3d_graph_layout_open/bms_fu02f1_face_layout.csv
```

Optional:

```text
runs/BMS-FU02g4/symmetry_orbit_inspection_c60_reference_open/bms_fu02g4_automorphism_orbit_summary.json
```

The runner recomputes automorphisms when `orbit_reduction.enabled = true` and
`networkx` is available.

---

## 5. Enumeration strategy

FU02g4c uses a deterministic connected-subset enumerator.

The enumerator emits connected patches of size:

```text
target_patch_size = reference carrier_face_count
```

For C60/FU02f1 this is expected to be:

```text
target_patch_size = 17
```

Patches are emitted in deterministic sorted-root expansion order.

FU02g4c supports:

```text
skip_first_raw_patches
max_raw_patches_this_run
```

This gives a simple resumable chunk mechanism:

```text
run 1: skip=0, max=1,000,000
run 2: skip=1,000,000, max=1,000,000
run 3: skip=2,000,000, max=1,000,000
...
```

This is not as elegant as a full recursion-state checkpoint, but it is transparent,
portable, and auditable.

---

## 6. Orbit reduction

If enabled and networkx is available, FU02g4c computes all face-type-preserving
C60 face-graph automorphisms and canonicalizes each patch.

Canonical patch key:

```text
minimum sorted face tuple over all automorphic images
```

The runner counts:

```text
raw_connected_patch_count_processed
unique_orbit_patch_count_processed
```

This reduces interpretation from labelled patches to symmetry-equivalence
classes.

Important:

```text
Orbit reduction is only used for canonical class counting.
Raw signature matches are still counted separately.
```

---

## 7. Role assignment

Candidate patches still do not naturally have FU02f1 roles.

FU02g4c keeps the same deterministic v0 role assignment used in FU02g4b:

```text
type_preferred_role_assignment
```

Rule:

```text
1. Assign mixed_core roles preferentially to hexagons.
2. Assign pentagon_boundary roles preferentially to pentagons.
3. Fill remaining role slots by deterministic sorted order.
```

This keeps FU02g4b and FU02g4c comparable.

---

## 8. Signature matching

FU02g4c reuses FU02g4b signature definitions.

Counts:

```text
carrier_signature_exact_match_count
carrier_signature_near_match_count
role_colored_signature_exact_match_count
role_colored_signature_near_match_count
```

Near threshold:

```text
max_abs_difference_sum = 2
```

The runner also counts canonical-orbit versions:

```text
orbit_carrier_signature_exact_match_class_count
orbit_carrier_signature_near_match_class_count
orbit_role_colored_signature_exact_match_class_count
orbit_role_colored_signature_near_match_class_count
```

where applicable.

---

## 9. Outputs

Output directory:

```text
runs/BMS-FU02g4c/orbit_reduced_resumable_connected_patch_enumeration_open/
```

Expected files:

```text
bms_fu02g4c_reference_patch_signature.json
bms_fu02g4c_chunk_summary.json
bms_fu02g4c_match_examples.csv
bms_fu02g4c_orbit_match_examples.csv
bms_fu02g4c_orbit_reduction_summary.json
bms_fu02g4c_run_manifest.json
bms_fu02g4c_warnings.json
bms_fu02g4c_config_resolved.yaml
```

Optional if enabled:

```text
bms_fu02g4c_signature_counts.csv
bms_fu02g4c_orbit_signature_counts.csv
```

---

## 10. Completion semantics

Possible status values:

```text
complete
partial_chunk_limit_reached
partial_timeout_reached
partial_runtime_error
```

Meaning:

```text
complete:
  The enumerator finished all connected patches after applying skip.

partial_chunk_limit_reached:
  The configured max_raw_patches_this_run was reached.

partial_timeout_reached:
  The configured timeout was reached.

partial_runtime_error:
  An error occurred.
```

Important:

```text
A chunk with partial_chunk_limit_reached is not a failure.
It is the expected resumable mode.
```

---

## 11. Recommended run mode

Initial chunk:

```text
skip_first_raw_patches = 0
max_raw_patches_this_run = 1000000
timeout_seconds = 900
orbit_reduction.enabled = true
```

Then rerun by increasing skip.

Example:

```text
chunk 0: skip 0
chunk 1: skip 1000000
chunk 2: skip 2000000
chunk 3: skip 3000000
```

---

## 12. Interpretation boundary

Allowed:

```text
FU02g4c chunk N processed a bounded range of raw connected patches and counted
raw/orbit-canonical signature matches.
```

Allowed when all chunks cover full enumeration:

```text
FU02g4c completed a resumable exhaustive enumeration under the specified graph,
role-assignment, and orbit-canonicalization definitions.
```

Not allowed:

```text
Exhaustive result before all chunks complete.
Universal p-values.
Physical spacetime proof.
Molecular chemistry proof.
```

---

## 13. Recommended next block

If g4c completes enough chunks to close the enumeration:

```text
BMS-FU02g5 — Geometry-Class Memory Synthesis
```

If orbit-canonical exact role signature remains absent:

```text
The synthesis can say that the evidence survives sampled, bounded, and
orbit-reduced enumeration checks under the specified definitions.
```

---

## 14. Internal summary

```text
FU02g4b:
  ein langer Lauf, bounded, 3.68M Patches

FU02g4c:
  viele kleine Läufe
  fortsetzbar
  orbit-reduziert
  besser prüfbar

Ziel:
  Aus Maschinenraum-Zählen wird ein sauberer Zählprozess.
```
