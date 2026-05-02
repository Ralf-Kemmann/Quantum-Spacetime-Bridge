# BMS-FU02g4c — Orbit-Reduced / Resumable Connected Patch Enumeration Chunk 0 Result Note

Date: 2026-05-03  
Project: Gravitation und RaumZeit / Quantum-Spacetime-Bridge  
Recommended repo target: `docs/BMS_FU02G4C_CHUNK_0000000_0999999_RESULT_NOTE.md`  
Status: Initial chunk result note

---

## 1. Purpose

BMS-FU02g4c follows the bounded FU02g4b result.

FU02g4b-v2 counted 3,682,435 connected 17-face C60 patches before timeout and found:

```text
uncolored carrier exact = 20
uncolored carrier near = 127
role-colored exact = 0
role-colored near = 3
```

FU02g4c makes the enumeration resumable and adds orbit-canonical class counts under the observed face-type-preserving C60 automorphism group.

---

## 2. Chunk identity

```text
chunk_id = chunk_0000000_0999999
skip_first_raw_patches = 0
raw_connected_patch_count_processed = 1,000,000
raw_patch_count_seen_including_skipped = 1,000,001
enumeration_status = partial_chunk_limit_reached
```

Interpretation:

```text
This is the first bounded resumable chunk, not an exhaustive run.
```

The status is expected:

```text
partial_chunk_limit_reached
```

because the config requested a 1,000,000 patch chunk.

---

## 3. Orbit reduction status

```text
orbit_reduction_enabled_actual = true
automorphism_count_used = 120
unique_orbit_patch_count_processed = 231,683
warnings_count = 0
```

Interpretation:

```text
Orbit reduction ran successfully using the 120 face-type-preserving C60 face-graph automorphisms.
```

Raw-to-orbit reduction in this chunk:

```text
raw patches processed = 1,000,000
unique orbit patch classes = 231,683
```

Approximate reduction factor:

```text
1,000,000 / 231,683 ≈ 4.32
```

This does not mean each orbit has size 4.32 globally; it means the first deterministic raw chunk contains repeated representatives that collapse into 231,683 canonical classes under the automorphism group.

---

## 4. Raw signature results

```text
raw_carrier_signature_exact_match_count = 12
raw_carrier_signature_exact_match_fraction = 1.2e-05

raw_carrier_signature_near_match_count = 78
raw_carrier_signature_near_match_fraction = 7.8e-05

raw_role_colored_signature_exact_match_count = 0
raw_role_colored_signature_exact_match_fraction = 0.0

raw_role_colored_signature_near_match_count = 0
raw_role_colored_signature_near_match_fraction = 0.0
```

Interpretation:

```text
The uncolored patch signature is rare but appears in the first raw chunk.
The role-colored patch signature is absent in the first raw chunk, both exact and near.
```

Internal formulation:

```text
Der Fleck ohne Rollenfarbe taucht auf.
Die Rollenfarbe taucht in Chunk 0 nicht auf.
```

---

## 5. Orbit-canonical signature results

```text
orbit_carrier_signature_exact_match_class_count = 1
orbit_carrier_signature_near_match_class_count = 9

orbit_role_colored_signature_exact_match_class_count = 0
orbit_role_colored_signature_near_match_class_count = 0
```

Interpretation:

```text
Under orbit canonicalization, the raw uncolored matches collapse to a small number of canonical classes. No role-colored exact or near class appears in this chunk.
```

This is the key FU02g4c Chunk 0 result.

---

## 6. Signature diversity

```text
unique_raw_carrier_signature_count = 20,097
unique_raw_role_colored_signature_count = 188,269

unique_orbit_carrier_signature_count = 20,097
unique_orbit_role_colored_signature_count = 121,946
```

Interpretation:

```text
The carrier-signature space is broad, and the role-colored signature space is much broader. Orbit reduction reduces role-colored diversity substantially, but the reference role-colored signature still does not appear in this chunk.
```

Note:

```text
The identical raw/orbit carrier signature count is plausible because uncolored patch signatures are automorphism-invariant and many raw patches share the same signature.
```

---

## 7. Relation to FU02g4b

FU02g4b after 3.68M raw patches found:

```text
raw uncolored exact = 20
raw uncolored near = 127
raw role-colored exact = 0
raw role-colored near = 3
```

FU02g4c Chunk 0 covers the first 1M raw patches and finds:

```text
raw uncolored exact = 12
raw uncolored near = 78
raw role-colored exact = 0
raw role-colored near = 0
```

Thus:

```text
Chunk 0 reproduces the early FU02g4b pattern: uncolored matches are rare but present; role-colored matches are absent.
```

The g4b near role-colored matches likely occur after the first million raw patches, if the enumeration order is identical.

---

## 8. Befund / Interpretation / Hypothesis / Open Gap

### Befund

```text
FU02g4c Chunk 0 processed 1,000,000 raw connected 17-face patches and 231,683 orbit-canonical patch classes. It found 12 raw uncolored exact matches and 78 raw uncolored near matches. It found no raw or orbit-canonical role-colored exact or near matches.
```

### Interpretation

```text
In the first deterministic chunk, the uncolored reference patch signature is rare but reproducible, while the role-colored signature remains absent. Orbit reduction confirms that the uncolored matches collapse to few canonical classes and that no role-colored near/exact class is present in this chunk.
```

### Hypothesis

```text
The role-colored C60 patch signature remains the strongest specificity candidate because it is more constrained than the uncolored patch signature, even under orbit-canonical chunk enumeration.
```

### Open gap

```text
This is only chunk 0. Exhaustive or full bounded-resumable conclusions require processing subsequent chunks and aggregating them.
```

---

## 9. Claim boundary

Allowed:

```text
FU02g4c Chunk 0 provides orbit-reduced chunk evidence over 1,000,000 raw connected 17-face C60 patches.
```

Allowed:

```text
In this chunk, no raw or orbit-canonical role-colored exact or near match was found.
```

Allowed:

```text
The raw uncolored reference signature appeared rarely, with 12 exact and 78 near matches; orbit-canonical exact uncolored matches collapsed to 1 class and near matches to 9 classes.
```

Not allowed:

```text
FU02g4c is exhaustive.
No connected patch anywhere reproduces the role-colored signature.
Real-structure memory is proven.
Physical spacetime is proven.
```

---

## 10. Recommended next chunk

Run Chunk 1:

```text
chunk_id = chunk_1000000_1999999
skip_first_raw_patches = 1000000
max_raw_patches_this_run = 1000000
```

Then continue:

```text
chunk_2000000_2999999
chunk_3000000_3999999
...
```

The next chunk should test whether the near role-colored matches seen in FU02g4b appear in later deterministic ranges.

---

## 11. Commit plan

Copy result note:

```bash
cd ~/Downloads/deBroglie_Kaster_Theorie/quantum-spacetime-bridge

cp ~/Downloads/BMS_FU02G4C_CHUNK_0000000_0999999_RESULT_NOTE.md \
  docs/BMS_FU02G4C_CHUNK_0000000_0999999_RESULT_NOTE.md

git status --short
```

Commit:

```bash
git add \
  docs/BMS_FU02G4C_CHUNK_0000000_0999999_RESULT_NOTE.md

git status --short

git commit -m "Add BMS-FU02g4c chunk 0 result note"

git push
```

---

## 12. Internal summary

```text
FU02g4c Chunk 0:

  raw patches:
    1,000,000

  orbit classes:
    231,683

  automorphisms:
    120

  raw uncolored:
    exact 12
    near 78

  orbit uncolored:
    exact class 1
    near classes 9

  raw role-colored:
    exact 0
    near 0

  orbit role-colored:
    exact class 0
    near class 0

Conclusion:
  Der ungefähre Fleck ist selten, aber da.
  Die Rollenfarbe bleibt in Chunk 0 verschwunden.
```
