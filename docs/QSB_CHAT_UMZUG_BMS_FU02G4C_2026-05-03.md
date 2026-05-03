# QSB Chat-Umzug — BMS-FU02g4c State Freeze — 2026-05-03

Project: Gravitation und RaumZeit / Quantum-Spacetime-Bridge  
Current thread: BMS-FU02 real-structure memory / C60 carrier-region specificity  
Purpose: Transfer current project state into a new chat.

---

## 1. Repo root

```bash
/home/ralf-kemmann/Downloads/deBroglie_Kaster_Theorie/quantum-spacetime-bridge
```

Strict folders:

```text
docs/
data/
scripts/
runs/
```

---

## 2. Current scientific question

We are testing whether the FU02f1 C60 carrier-region pattern is merely a generic connected patch or whether its role-colored structure is unusually constrained under C60 face-graph controls and automorphism/orbit checks.

Internal:

```text
Ist der Klunker nur irgendein Fleck,
oder trägt er eine echte Rollenfarbe,
die nicht billig nachzumalen ist?
```

External:

```text
The FU02g sequence tests whether the FU02f1 C60 carrier-region signature shows
construction-qualified specificity under connected-patch, null, and
automorphism/orbit controls.
```

---

## 3. FU02f1 reference carrier region

Reference carrier region:

```text
carrier_face_count = 17
carrier_hexagon_count = 12
carrier_pentagon_count = 5
carrier_component_count = 1
largest_carrier_component_count = 17
```

Reference sets:

```text
carrier_set =
H_07;H_09;H_11;H_12;H_13;H_14;H_15;H_16;H_17;H_18;H_19;H_20;P_07;P_08;P_09;P_10;P_11

mixed_core_set =
H_09;H_11;H_13;H_16;H_17;H_18;H_19;H_20

pentagon_boundary_set =
H_07;H_12;H_14;H_15;P_07;P_08;P_09;P_10;P_11
```

Role mapping:

```text
mixed_core = mixed_seam_boundary_face
pentagon_boundary = hp_boundary_face
```

Internal:

```text
Hexagon-Mixed-Core plus Pentagongrenze.
```

---

## 4. FU02g3 summary

FU02g3 tested null specificity.

Result:

```text
carrier_count_random_patch:
  near = 17/1000
  strict = 0/1000

type_count_preserving_patch:
  near = 35/1000
  strict = 0/1000

connected_patch_seeded:
  near = 90/1000
  strict = 0/1000

role_count_preserving_connected_patch:
  near = 95/1000
  strict = 1/1000
```

Interpretation:

```text
Simple nulls rarely reproduce the reference.
Connected/role-aware nulls reproduce coarse near-reference more often.
Strict reproduction is absent or nearly absent.
```

Claim boundary:

```text
weak-to-moderate construction-qualified specificity against simple nulls,
not strong specificity against connected/role-aware decoys.
```

---

## 5. FU02g4 summary

FU02g4 performed symmetry-orbit inspection.

Complete automorphism result:

```json
{
  "automorphism_count_observed": 120,
  "carrier_orbit_size_observed": 120,
  "carrier_stabilizer_size_observed": 1,
  "role_colored_orbit_size_observed": 120,
  "role_colored_stabilizer_size_observed": 1,
  "node_match_preserves_cell_type": true,
  "status": "complete"
}
```

Sampled connected patch result:

```text
sample_count = 5000
carrier_signature_match_count = 1
near_carrier_signature_count = 10
role_colored_signature_match_count = 0
near_role_colored_signature_count = 0
```

Interpretation:

```text
Der konkrete Ort ist nicht heilig.
Die Orbitklasse ist der Klunker.
```

Claim boundary:

```text
not a unique physical location
not exhaustive
not real-structure-memory proof
```

---

## 6. FU02g4b summary

FU02g4b attempted exhaustive connected-patch signature check.

Important correction:

```text
An initial runner emitted zero patches and falsely reported complete.
That run is discarded.
```

Patched marker:

```text
PATCH_MARKER: FU02G4B_ENUMERATOR_PATCHED_V2_REFERENCE_CONNECTED_GUARD
```

Valid patched V2 bounded run:

```json
{
  "enumerated_connected_patch_count": 3682435,
  "enumeration_status": "partial_timeout_reached",
  "reference_is_connected": true,
  "target_patch_size": 17,
  "warnings_count": 0
}
```

Enumeration summary:

```text
carrier_signature_exact_match_count = 20
carrier_signature_exact_match_fraction ≈ 5.43e-6

carrier_signature_near_match_count = 127
carrier_signature_near_match_fraction ≈ 3.45e-5

role_colored_signature_exact_match_count = 0
role_colored_signature_exact_match_fraction = 0.0

role_colored_signature_near_match_count = 3
role_colored_signature_near_match_fraction ≈ 8.15e-7
```

Interpretation:

```text
The uncolored patch signature is rare but not unique.
The exact role-colored signature was not reproduced in 3.68M bounded patches.
Near role-colored matches exist but are extremely rare.
```

Claim boundary:

```text
bounded enumeration evidence, not exhaustive absence.
```

---

## 7. FU02g4c current block

Block:

```text
BMS-FU02g4c — Orbit-Reduced / Resumable Connected Patch Enumeration
```

Purpose:

```text
Turn the long bounded FU02g4b run into a resumable chunked enumeration with
optional orbit-canonical class counting under the 120 C60 automorphisms.
```

Created files:

```text
docs/BMS_FU02G4C_ORBIT_REDUCED_RESUMABLE_CONNECTED_PATCH_ENUMERATION_SPEC.md
data/bms_fu02g4c_orbit_reduced_resumable_config.yaml
scripts/run_bms_fu02g4c_orbit_reduced_resumable_connected_patch_enumeration.py
docs/BMS_FU02G4C_ORBIT_REDUCED_RESUMABLE_CONNECTED_PATCH_ENUMERATION_FIELD_LIST.md
```

Initial config:

```yaml
run:
  chunk_id: "chunk_0000000_0999999"

enumeration:
  skip_first_raw_patches: 0
  max_raw_patches_this_run: 1000000
  timeout_seconds: 900

orbit_reduction:
  enabled: true
```

---

## 8. FU02g4c Chunk 0 result

User ran:

```bash
python scripts/run_bms_fu02g4c_orbit_reduced_resumable_connected_patch_enumeration.py \
  --config data/bms_fu02g4c_orbit_reduced_resumable_config.yaml
```

Chunk 0 manifest:

```json
{
  "chunk_id": "chunk_0000000_0999999",
  "enumeration_status": "partial_chunk_limit_reached",
  "orbit_reduction_enabled_actual": true,
  "raw_connected_patch_count_processed": 1000000,
  "raw_patch_count_seen_including_skipped": 1000001,
  "reference_is_connected": true,
  "skip_first_raw_patches": 0,
  "target_patch_size": 17,
  "unique_orbit_patch_count_processed": 231683,
  "warnings_count": 0
}
```

Chunk 0 summary:

```text
automorphism_count_used = 120
elapsed_seconds ≈ 705.16
unique_orbit_patch_count_processed = 231,683

raw_carrier_signature_exact_match_count = 12
raw_carrier_signature_near_match_count = 78

raw_role_colored_signature_exact_match_count = 0
raw_role_colored_signature_near_match_count = 0

orbit_carrier_signature_exact_match_class_count = 1
orbit_carrier_signature_near_match_class_count = 9

orbit_role_colored_signature_exact_match_class_count = 0
orbit_role_colored_signature_near_match_class_count = 0

unique_raw_carrier_signature_count = 20,097
unique_raw_role_colored_signature_count = 188,269

unique_orbit_carrier_signature_count = 20,097
unique_orbit_role_colored_signature_count = 121,946
```

Interpretation:

```text
Chunk 0 reproduces the pattern:
  uncolored matches are rare but present;
  role-colored matches are absent.

Orbit reduction collapses uncolored matches to few classes:
  exact = 1 orbit class
  near = 9 orbit classes

Role-colored remains absent even orbit-canonically:
  exact = 0
  near = 0
```

Internal:

```text
Der ungefähre Fleck ist selten, aber da.
Die Rollenfarbe bleibt in Chunk 0 verschwunden.
```

---

## 9. Next action

Next chunk:

```text
BMS-FU02g4c Chunk 1
```

Edit config:

```yaml
run:
  chunk_id: "chunk_1000000_1999999"

enumeration:
  skip_first_raw_patches: 1000000
  max_raw_patches_this_run: 1000000
```

Then run:

```bash
python scripts/run_bms_fu02g4c_orbit_reduced_resumable_connected_patch_enumeration.py \
  --config data/bms_fu02g4c_orbit_reduced_resumable_config.yaml
```

Expected status:

```text
partial_chunk_limit_reached
```

Important fields:

```text
raw_role_colored_signature_exact_match_count
raw_role_colored_signature_near_match_count
orbit_role_colored_signature_exact_match_class_count
orbit_role_colored_signature_near_match_class_count
unique_orbit_patch_count_processed
warnings_count
```

---

## 10. Claim boundary for next chat

Do not say:

```text
FU02g4c is exhaustive.
No role-colored patch exists anywhere.
Real-structure memory is proven.
```

Say:

```text
FU02g4c Chunk 0 provides orbit-reduced chunk evidence over 1,000,000 raw connected patches and 231,683 canonical patch classes.
```

Say:

```text
In Chunk 0, no raw or orbit-canonical role-colored exact or near match was found.
```

Say:

```text
Further chunks are needed before aggregated bounded or exhaustive statements.
```

---

## 11. Internal handoff summary

```text
We are mid-FU02g4c.

Last valid result:
  Chunk 0
  1,000,000 raw patches
  231,683 orbit classes
  120 automorphisms
  warnings 0

Uncolored:
  raw exact 12
  raw near 78
  orbit exact classes 1
  orbit near classes 9

Role-colored:
  raw exact 0
  raw near 0
  orbit exact classes 0
  orbit near classes 0

Next:
  run Chunk 1 with skip_first_raw_patches = 1000000
```

Short internal phrase:

```text
Der Fleck ohne Rollenfarbe taucht selten auf.
Die Rollenfarbe bleibt in Chunk 0 verschwunden.
Jetzt Chunk 1.
```
