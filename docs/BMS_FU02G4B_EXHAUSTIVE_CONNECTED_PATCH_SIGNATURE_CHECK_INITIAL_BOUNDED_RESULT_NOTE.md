# BMS-FU02g4b — Exhaustive Connected Patch Signature Check Initial Bounded Result Note

Date: 2026-05-03  
Project: Gravitation und RaumZeit / Quantum-Spacetime-Bridge  
Recommended repo target: `docs/BMS_FU02G4B_EXHAUSTIVE_CONNECTED_PATCH_SIGNATURE_CHECK_INITIAL_BOUNDED_RESULT_NOTE.md`  
Status: Initial bounded enumeration result note

---

## 1. Purpose

BMS-FU02g4b follows FU02g4.

FU02g4 showed that the FU02f1 C60 reference patch is one representative of a 120-member face-type-preserving automorphism orbit with trivial stabilizer. In 5000 sampled connected same-size patches, the role-colored signature was not reproduced.

FU02g4b asks whether this sampled evidence can be sharpened by systematic connected-patch enumeration.

---

## 2. Correction history

An initial FU02g4b runner emitted zero patches while incorrectly reporting `enumeration_status = complete`.

That run is discarded.

Reason:

```text
enumerated_connected_patch_count = 0
reference patch is connected
therefore a complete zero-patch enumeration is impossible
```

The valid run below uses the patched V2 runner with:

```text
PATCH_MARKER: FU02G4B_ENUMERATOR_PATCHED_V2_REFERENCE_CONNECTED_GUARD
```

---

## 3. Run status

Manifest:

```json
{
  "enumerated_connected_patch_count": 3682435,
  "enumeration_status": "partial_timeout_reached",
  "reference_is_connected": true,
  "target_patch_size": 17,
  "warnings_count": 0
}
```

Interpretation:

```text
FU02g4b-v2 ran correctly and enumerated 3,682,435 connected 17-face C60 patches before reaching the configured 900-second timeout.
```

This is **bounded enumeration evidence**, not an exhaustive result.

---

## 4. Enumeration summary

```json
{
  "carrier_signature_exact_match_count": 20,
  "carrier_signature_exact_match_fraction": 5.431188873666473e-06,
  "carrier_signature_near_match_count": 127,
  "carrier_signature_near_match_fraction": 3.4488049347782106e-05,
  "role_colored_signature_exact_match_count": 0,
  "role_colored_signature_exact_match_fraction": 0.0,
  "role_colored_signature_near_match_count": 3,
  "role_colored_signature_near_match_fraction": 8.14678331049971e-07,
  "unique_carrier_signature_count": 36314,
  "unique_role_colored_signature_count": 1014145,
  "enumerated_connected_patch_count": 3682435,
  "enumeration_status": "partial_timeout_reached"
}
```

---

## 5. Main result

### 5.1 Uncolored carrier signature

```text
carrier_signature_exact_match_count = 20
carrier_signature_exact_match_fraction ≈ 5.43e-6

carrier_signature_near_match_count = 127
carrier_signature_near_match_fraction ≈ 3.45e-5
```

Interpretation:

```text
The uncolored FU02f1 carrier patch signature is rare but not unique among the enumerated connected 17-face patches.
```

Internal formulation:

```text
Der Fleck ohne Rollenfarbe ist selten, aber nicht einmalig.
```

### 5.2 Role-colored signature

```text
role_colored_signature_exact_match_count = 0
role_colored_signature_exact_match_fraction = 0.0

role_colored_signature_near_match_count = 3
role_colored_signature_near_match_fraction ≈ 8.15e-7
```

Interpretation:

```text
No exact role-colored signature match was found in 3,682,435 enumerated connected patches. Three near role-colored matches were found under the configured near threshold.
```

Internal formulation:

```text
Die genaue Rollenfarbe wurde nicht getroffen.
Sehr nahe Rollenfarbe kommt extrem selten vor.
```

---

## 6. Relation to FU02g4

FU02g4 sampled 5000 connected patches and found:

```text
carrier exact = 1 / 5000
carrier near = 10 / 5000
role exact = 0 / 5000
role near = 0 / 5000
```

FU02g4b bounded enumeration refines this:

```text
carrier exact = 20 / 3,682,435
carrier near = 127 / 3,682,435
role exact = 0 / 3,682,435
role near = 3 / 3,682,435
```

Thus the qualitative FU02g4 result is supported but sharpened:

```text
The uncolored patch signature is rare but reproducible.
The exact role-colored patch signature was not reproduced in the bounded enumeration.
Near role-colored signatures exist but are extremely rare.
```

---

## 7. Relation to FU02g3

FU02g3 showed that connected and role-aware connected decoys can reproduce coarse near-reference profiles around 9-10%.

FU02g4b shows why coarse near-reference is not enough:

```text
Coarse connected role-count similarity is much easier than matching the detailed role-colored patch signature.
```

Sequence:

```text
FU02g3:
  coarse near-reference can be produced by connected/role-aware decoys.

FU02g4:
  sampled detailed role-colored signature was not reproduced.

FU02g4b:
  bounded enumeration finds no exact role-colored match in 3.68M patches,
  and only 3 near role-colored matches.
```

---

## 8. Befund / Interpretation / Hypothesis / Open Gap

### Befund

```text
The patched FU02g4b runner enumerated 3,682,435 connected 17-face C60 patches before timeout. The uncolored reference signature was matched exactly 20 times and near-matched 127 times. The exact role-colored reference signature was not matched. Three near role-colored matches occurred.
```

### Interpretation

```text
The FU02f1 reference patch is not unique at the uncolored patch-signature level. However, the role-colored signature is much more constrained: exact reproduction was absent in the bounded enumeration, while near reproduction was extremely rare.
```

### Hypothesis

```text
The strongest real-structure-memory candidate is not generic connectedness and not the uncolored patch shape alone, but the role-colored C60 patch signature up to automorphism orbit equivalence.
```

### Open gap

```text
The enumeration stopped by timeout. Therefore the result is bounded, not exhaustive. An exhaustive or orbit-reduced enumeration is still needed before claiming exhaustive absence of exact role-colored matches.
```

---

## 9. Claim boundary

Allowed:

```text
FU02g4b-v2 provides bounded enumeration evidence over 3,682,435 connected 17-face C60 patches.
```

Allowed:

```text
Within this bounded enumeration, the exact role-colored FU02f1 reference signature was not reproduced.
```

Allowed:

```text
Near role-colored matches were found but were extremely rare: 3 / 3,682,435.
```

Allowed:

```text
The uncolored carrier signature is rare but not unique: 20 exact matches and 127 near matches in the bounded enumeration.
```

Not allowed:

```text
The enumeration was exhaustive.
No connected patch anywhere can reproduce the signature.
Real-structure memory is proven.
Physical spacetime is proven.
Molecular chemistry is proven.
A universal p-value has been established.
```

---

## 10. Methodological consequence

FU02g4b shifts the evidence level:

```text
From:
  sampled connected-patch evidence

To:
  large bounded connected-patch enumeration evidence
```

But it does not yet close the exhaustive gap.

The next hardening step is therefore not another broad random/null test, but an enumeration strategy improvement.

---

## 11. Recommended next step

Recommended:

```text
BMS-FU02g4c — Orbit-Reduced / Resumable Connected Patch Enumeration
```

Purpose:

```text
Avoid timeout-limited partial enumeration by either:
  1. orbit-reducing connected patches under the 120 C60 automorphisms,
  2. making enumeration resumable in chunks,
  3. or both.
```

Alternative:

```text
Increase timeout_seconds and rerun FU02g4b.
```

But the better methodological route is orbit-reduced or resumable enumeration, because it makes the result more auditable and less dependent on one long run.

---

## 12. Commit plan

Copy result note:

```bash
cd ~/Downloads/deBroglie_Kaster_Theorie/quantum-spacetime-bridge

cp ~/Downloads/BMS_FU02G4B_EXHAUSTIVE_CONNECTED_PATCH_SIGNATURE_CHECK_INITIAL_BOUNDED_RESULT_NOTE.md \
  docs/BMS_FU02G4B_EXHAUSTIVE_CONNECTED_PATCH_SIGNATURE_CHECK_INITIAL_BOUNDED_RESULT_NOTE.md

git status --short
```

Commit the patched runner and bounded result note:

```bash
git add \
  scripts/run_bms_fu02g4b_exhaustive_connected_patch_signature_check.py \
  docs/BMS_FU02G4B_EXHAUSTIVE_CONNECTED_PATCH_SIGNATURE_CHECK_INITIAL_BOUNDED_RESULT_NOTE.md

git status --short

git commit -m "Patch BMS-FU02g4b enumeration and add bounded result note"

git push
```

---

## 13. Internal summary

```text
FU02g4b-v2:

  Status:
    partial_timeout_reached
    3,682,435 connected patches enumerated
    warnings 0

  Uncolored:
    exact 20
    near 127

  Role-colored:
    exact 0
    near 3

Conclusion:
  Der Fleck ohne Rollenfarbe ist selten, aber nicht eindeutig.
  Die genaue Rollenfarbe wurde im bounded run nicht getroffen.
  Fast-Rollenfarbe ist extrem selten.

But:
  Noch nicht exhaustive.
  Nächster harter Schritt: orbit-reduced/resumable enumeration.
```
