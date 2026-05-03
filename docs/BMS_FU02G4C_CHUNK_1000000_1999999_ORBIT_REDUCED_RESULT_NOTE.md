# BMS-FU02g4c — Chunk 1 Orbit-Reduced Result Note

Date: 2026-05-03  
Project: Gravitation und RaumZeit / Quantum-Spacetime-Bridge  
Block: BMS-FU02g4c — Orbit-Reduced / Resumable Connected Patch Enumeration  
Chunk: `chunk_1000000_1999999`

Target repo path:

```bash
docs/BMS_FU02G4C_CHUNK_1000000_1999999_ORBIT_REDUCED_RESULT_NOTE.md
```

---

## 1. Purpose

Chunk 1 continues the resumable connected-patch enumeration from raw patch index 1,000,000 through 1,999,999.

The purpose is to test whether the FU02f1 carrier-region signature and its role-colored subdivision remain rare under connected-patch controls, while reducing duplicate cases by C60 face-graph automorphism classes.

This note supersedes the earlier raw-only Chunk 1 attempt for orbit-reduced interpretation. The earlier run remains interpretable only as a dependency-limited raw-only trace because `networkx` was unavailable and orbit reduction was disabled.

---

## 2. Run command

Executed from the repository root with the local virtual environment active:

```bash
cd ~/Downloads/deBroglie_Kaster_Theorie/quantum-spacetime-bridge
source .venv/bin/activate

python scripts/run_bms_fu02g4c_orbit_reduced_resumable_connected_patch_enumeration.py \
  --config data/bms_fu02g4c_orbit_reduced_resumable_config.yaml
```

---

## 3. Config status

Observed relevant config values:

```text
chunk_id = chunk_1000000_1999999
skip_first_raw_patches = 1000000
max_raw_patches_this_run = 1000000
timeout_seconds = 900
orbit_reduction.enabled = true
```

---

## 4. Run status

Manifest-level status:

```json
{
  "chunk_id": "chunk_1000000_1999999",
  "enumeration_status": "partial_chunk_limit_reached",
  "orbit_reduction_enabled_actual": true,
  "raw_connected_patch_count_processed": 1000000,
  "raw_patch_count_seen_including_skipped": 2000001,
  "reference_is_connected": true,
  "skip_first_raw_patches": 1000000,
  "target_patch_size": 17,
  "unique_orbit_patch_count_processed": 589796,
  "warnings_count": 0
}
```

Summary-level status:

```json
{
  "automorphism_count_used": 120,
  "elapsed_seconds": 737.9109139442444,
  "enumeration_status": "partial_chunk_limit_reached",
  "orbit_reduction_enabled_actual": true,
  "warnings_count": 0
}
```

The run is therefore interpretable as a valid orbit-reduced Chunk 1 result.

---

## 5. Main readouts

Raw readouts:

```json
{
  "raw_carrier_signature_exact_match_count": 2,
  "raw_carrier_signature_exact_match_fraction": 2e-06,
  "raw_carrier_signature_near_match_count": 17,
  "raw_carrier_signature_near_match_fraction": 1.7e-05,
  "raw_role_colored_signature_exact_match_count": 0,
  "raw_role_colored_signature_exact_match_fraction": 0.0,
  "raw_role_colored_signature_near_match_count": 0,
  "raw_role_colored_signature_near_match_fraction": 0.0
}
```

Orbit-reduced readouts:

```json
{
  "orbit_carrier_signature_exact_match_class_count": 1,
  "orbit_carrier_signature_near_match_class_count": 8,
  "orbit_role_colored_signature_exact_match_class_count": 0,
  "orbit_role_colored_signature_near_match_class_count": 0,
  "unique_orbit_patch_count_processed": 589796
}
```

Signature-diversity readouts:

```json
{
  "unique_raw_carrier_signature_count": 30241,
  "unique_orbit_carrier_signature_count": 30241,
  "unique_raw_role_colored_signature_count": 415222,
  "unique_orbit_role_colored_signature_count": 277260
}
```

Role assignment note:

```text
type_preferred_role_assignment; role-colored orbit-class counts are v0 assignment-dependent.
```

---

## 6. Befund

Chunk 1 processed 1,000,000 raw connected patches after skipping the first 1,000,000 raw patches.

Orbit reduction was active and used 120 automorphisms.

The run produced no warnings.

Within Chunk 1:

```text
raw carrier exact matches = 2
raw carrier near matches = 17
raw role-colored exact matches = 0
raw role-colored near matches = 0

orbit carrier exact match classes = 1
orbit carrier near match classes = 8
orbit role-colored exact match classes = 0
orbit role-colored near match classes = 0
```

---

## 7. Interpretation

The uncolored carrier signature remains rare but present in Chunk 1.

The two raw carrier-exact matches collapse to one orbit-canonical carrier-exact class. The seventeen raw near-carrier matches collapse to eight orbit-canonical near-carrier classes.

The role-colored signature remains absent in Chunk 1, both at raw-count level and at orbit-canonical class level.

This reproduces the qualitative pattern already seen in Chunk 0:

```text
uncolored carrier patch: rare but present
role-colored patch: absent in the tested chunk
```

The result supports a cautious distinction between the uncolored carrier footprint and the role-colored subdivision.

---

## 8. Hypothese

The FU02f1 role-colored signature may be more constrained than the uncolored carrier signature under connected-patch controls and C60 automorphism/orbit reduction.

Chunk 1 is compatible with this hypothesis.

---

## 9. Offene Lücke

The enumeration is still chunk-bounded.

The result is not exhaustive.

No statement can yet be made that no role-colored patch exists anywhere in the full connected-patch space.

Further chunks are required before making an aggregated bounded statement across multiple million raw patches or before approaching an exhaustive statement.

The role-colored orbit-class counts remain explicitly v0 assignment-dependent under the current `type_preferred_role_assignment` rule.

---

## 10. Claim boundary

Do not say:

```text
FU02g4c is exhaustive.
No role-colored patch exists anywhere.
The role-colored signature is impossible.
Real-structure memory is proven.
```

Say:

```text
In FU02g4c Chunk 1, 1,000,000 raw connected patches were processed with orbit reduction active over 120 automorphisms.
```

Say:

```text
Within this chunk, the uncolored carrier signature occurred rarely, while no raw or orbit-canonical role-colored exact or near match was observed.
```

Say:

```text
The result is chunk evidence, not exhaustive absence.
```

---

## 11. Relation to Chunk 0

Chunk 0:

```text
raw carrier exact = 12
raw carrier near = 78
raw role-colored exact = 0
raw role-colored near = 0

orbit carrier exact classes = 1
orbit carrier near classes = 9
orbit role-colored exact classes = 0
orbit role-colored near classes = 0

unique_orbit_patch_count_processed = 231,683
```

Chunk 1:

```text
raw carrier exact = 2
raw carrier near = 17
raw role-colored exact = 0
raw role-colored near = 0

orbit carrier exact classes = 1
orbit carrier near classes = 8
orbit role-colored exact classes = 0
orbit role-colored near classes = 0

unique_orbit_patch_count_processed = 589,796
```

Cumulative across Chunk 0 and Chunk 1, raw-level only:

```text
raw connected patches processed = 2,000,000
raw carrier exact matches = 14
raw carrier near matches = 95
raw role-colored exact matches = 0
raw role-colored near matches = 0
```

Cumulative orbit-class totals should not be obtained by naive addition, because the same orbit-canonical classes may recur across chunks. A dedicated aggregation pass is needed for global unique orbit-class counting.

---

## 12. Recommended next step

Proceed to Chunk 2:

```yaml
run:
  chunk_id: "chunk_2000000_2999999"

enumeration:
  skip_first_raw_patches: 2000000
  max_raw_patches_this_run: 1000000
```

Run with the `.venv` active:

```bash
cd ~/Downloads/deBroglie_Kaster_Theorie/quantum-spacetime-bridge
source .venv/bin/activate

python scripts/run_bms_fu02g4c_orbit_reduced_resumable_connected_patch_enumeration.py \
  --config data/bms_fu02g4c_orbit_reduced_resumable_config.yaml
```

Required validity checks after the run:

```text
warnings_count = 0
orbit_reduction_enabled_actual = true
automorphism_count_used = 120
reference_is_connected = true
```

---

## 13. Copy / commit plan

Copy this note into the repo:

```bash
cp ~/Downloads/BMS_FU02G4C_CHUNK_1000000_1999999_ORBIT_REDUCED_RESULT_NOTE.md \
  ~/Downloads/deBroglie_Kaster_Theorie/quantum-spacetime-bridge/docs/BMS_FU02G4C_CHUNK_1000000_1999999_ORBIT_REDUCED_RESULT_NOTE.md
```

Inspect status:

```bash
cd ~/Downloads/deBroglie_Kaster_Theorie/quantum-spacetime-bridge
git status --short
```

Add explicitly:

```bash
git add docs/BMS_FU02G4C_CHUNK_1000000_1999999_ORBIT_REDUCED_RESULT_NOTE.md
```

Optional commit:

```bash
git commit -m "Document FU02g4c chunk 1 orbit-reduced result"
```

---

## 14. Internal summary

```text
Chunk 1 ist jetzt gültig orbit-reduziert.
1M raw patches, 589,796 orbit classes, 120 Automorphismen, warnings 0.
Der Fleck ohne Rollenfarbe bleibt selten:
  raw exact 2, raw near 17,
  orbit exact class 1, orbit near classes 8.
Die Rollenfarbe bleibt verschwunden:
  raw exact/near 0/0,
  orbit exact/near 0/0.
Das ist starke Chunk-Evidence, aber weiterhin keine Exhaustiv-Aussage.
```
