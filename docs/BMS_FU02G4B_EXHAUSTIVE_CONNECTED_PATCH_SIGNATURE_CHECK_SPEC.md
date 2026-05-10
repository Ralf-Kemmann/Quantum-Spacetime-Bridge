# BMS-FU02g4b — Exhaustive Connected Patch Signature Check Specification

Date: 2026-05-03  
Project: Gravitation und RaumZeit / Quantum-Spacetime-Bridge  
Recommended repo target: `docs/BMS_FU02G4B_EXHAUSTIVE_CONNECTED_PATCH_SIGNATURE_CHECK_SPEC.md`  
Status: Specification and implementation block

---

## 1. Purpose

BMS-FU02g4b follows the completed FU02g4 symmetry-orbit result.

FU02g4 showed:

```text
automorphism_count_observed = 120
carrier_orbit_size_observed = 120
role_colored_orbit_size_observed = 120
carrier_stabilizer_size_observed = 1
role_colored_stabilizer_size_observed = 1

sampled connected patches:
  carrier exact match = 1 / 5000
  carrier near match = 10 / 5000
  role-colored exact match = 0 / 5000
  role-colored near match = 0 / 5000
```

FU02g4b asks the harder question:

```text
Can we replace sampled connected-patch evidence with an exhaustive or bounded-
exhaustive connected 17-face patch signature check?
```

Internal formulation:

```text
Sampling war stark.
Jetzt zählen wir den Maschinenraum aus — soweit rechnerisch sauber möglich.
```

---

## 2. Scope

BMS-FU02g4b is an exact/bounded enumeration and signature-count block.

Allowed:

```text
enumerate connected same-size C60 face patches
count exact and near reference patch signatures
count role-colored signature matches under deterministic role assignment rules
report whether enumeration completed
report caps/timeouts transparently
```

Not allowed:

```text
claim exhaustive result if enumeration stopped early
claim physical spacetime
claim molecular quantum chemistry
claim universal p-value
claim real-structure memory proof
```

The most important output field is:

```text
enumeration_status
```

Possible values:

```text
complete
partial_max_patches_reached
partial_timeout_reached
partial_runtime_error
```

---

## 3. Inputs

Required:

```text
data/bms_fu02g_c60_reference_cells.csv
data/bms_fu02g_c60_reference_edges.csv
runs/BMS-FU02f1/face_id_interval_repair_3d_graph_layout_open/bms_fu02f1_face_layout.csv
```

Optional:

```text
runs/BMS-FU02g4/symmetry_orbit_inspection_c60_reference_open/bms_fu02g4_reference_patch_signature.json
runs/BMS-FU02g4/symmetry_orbit_inspection_c60_reference_open/bms_fu02g4_automorphism_orbit_summary.json
```

---

## 4. Reference patch

FU02g4b uses the same FU02f1 role mapping as FU02g4:

```text
mixed_seam_boundary_face -> mixed_core
hp_boundary_face -> pentagon_boundary
carrier_adjacent_face -> adjacent_shell
noncarrier_face -> noncarrier
```

Reference carrier patch:

```text
carrier_set = mixed_core + pentagon_boundary
```

Expected FU02f1 reference profile:

```text
carrier_face_count = 17
mixed_core_count = 8
pentagon_boundary_count = 9
carrier_hexagon_count = 12
carrier_pentagon_count = 5
```

The runner computes these from input, not from hard-coded IDs.

---

## 5. Enumeration logic

FU02g4b enumerates connected induced face subsets of size:

```text
target_patch_size = reference carrier_face_count
```

The C60 face graph has 32 face nodes. Naive enumeration of all 17-subsets is
too broad, so the runner uses a connected-subset backtracking strategy:

```text
1. Order face IDs deterministically.
2. For each root face, enumerate connected patches whose minimum ordered face
   is that root.
3. Grow patches from a boundary/frontier set.
4. Keep only connected patches of target size.
5. Use canonical sorted tuple keys to avoid duplicates.
```

The runner may still be expensive. Therefore it has explicit safety caps.

---

## 6. Exhaustiveness controls

Configurable controls:

```text
max_patches
timeout_seconds
progress_every
```

Interpretation:

```text
If all connected patches are enumerated before caps/timeouts:
  enumeration_status = complete

If a cap or timeout is hit:
  enumeration_status = partial_...
```

This prevents accidental overclaiming.

---

## 7. Role assignment for candidate patches

Candidate connected patches do not naturally have FU02f1 roles. FU02g4b offers
deterministic role-assignment modes.

Default:

```text
type_preferred_role_assignment
```

Rule:

```text
1. Assign mixed_core roles preferentially to hexagons.
2. Assign pentagon_boundary roles preferentially to pentagons.
3. Fill remaining role slots by deterministic sorted order.
```

This mirrors the strong role-aware decoy idea but removes randomness.

Alternative mode:

```text
best_effort_role_assignment_by_signature
```

This can try multiple deterministic assignments, but v0 defaults to the stable
type-preferred mode for transparency.

---

## 8. Signature metrics

FU02g4b reuses FU02g4 patch signatures.

### 8.1 Uncolored signature

```text
carrier_face_count
carrier_hexagon_count
carrier_pentagon_count
carrier_component_count
largest_carrier_component_count
carrier_internal_adjacency_count
carrier_boundary_adjacency_count
carrier_external_neighbor_count
carrier_induced_degree_histogram
boundary_neighbor_type_counts
```

### 8.2 Role-colored signature

```text
mixed_core_count
pentagon_boundary_count
mixed_core_internal_adjacency_count
pentagon_boundary_internal_adjacency_count
mixed_to_pentagon_boundary_adjacency_count
mixed_core_induced_degree_histogram
pentagon_boundary_induced_degree_histogram
```

---

## 9. Match criteria

Exact:

```text
carrier_signature_string == reference carrier_signature_string
role_colored_signature_string == reference role_colored_signature_string
```

Near:

```text
signature_distance <= max_abs_difference_sum
```

Default:

```text
max_abs_difference_sum = 2
```

---

## 10. Outputs

Output directory:

```text
runs/BMS-FU02g4b/exhaustive_connected_patch_signature_check_open/
```

Expected files:

```text
bms_fu02g4b_reference_patch_signature.json
bms_fu02g4b_enumeration_summary.json
bms_fu02g4b_match_examples.csv
bms_fu02g4b_signature_count_summary.csv
bms_fu02g4b_run_manifest.json
bms_fu02g4b_warnings.json
bms_fu02g4b_config_resolved.yaml
```

Optional large/debug file if enabled:

```text
bms_fu02g4b_patch_signature_counts.csv
```

---

## 11. Interpretation boundary

Allowed if complete:

```text
FU02g4b completed exhaustive connected 17-face C60 patch enumeration under the
specified graph/signature definitions.
```

Allowed if partial:

```text
FU02g4b provides bounded enumeration evidence up to the stated cap/timeout.
```

Allowed if no role-colored exact/near matches in a complete run:

```text
No connected same-size C60 face patch in the enumerated space reproduced the
reference role-colored signature under the specified deterministic role-
assignment rule.
```

Not allowed:

```text
This proves physical real-structure memory.
This proves universal absence under all possible role assignments.
This proves molecular chemistry.
This proves spacetime.
```

---

## 12. Recommended next block

If FU02g4b completes and confirms rarity/absence:

```text
BMS-FU02g5 — Geometry-Class Memory Synthesis
```

If FU02g4b is partial:

```text
BMS-FU02g4c — Optimized Canonical Patch Enumeration / Orbit-Reduced Exhaustion
```

---

## 13. Internal summary

```text
FU02g4:
  Orbitklasse steht.
  Sample sagt: Rollen-Signatur nicht billig.

FU02g4b:
  Jetzt zählen wir verbundene 17-Face-Patches systematisch.

Entscheidend:
  complete oder partial?
  Exact carrier signature?
  Near carrier signature?
  Exact role-colored signature?
  Near role-colored signature?
```
