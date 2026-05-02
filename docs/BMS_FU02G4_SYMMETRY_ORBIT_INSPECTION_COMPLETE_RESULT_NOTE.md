# BMS-FU02g4 — Symmetry-Orbit Inspection of the C60 Reference Carrier Region Complete Result Note

Date: 2026-05-03  
Project: Gravitation und RaumZeit / Quantum-Spacetime-Bridge  
Recommended repo target: `docs/BMS_FU02G4_SYMMETRY_ORBIT_INSPECTION_COMPLETE_RESULT_NOTE.md`  
Status: Complete result note after networkx-enabled rerun

---

## 1. Purpose

BMS-FU02g4 follows the mixed FU02g3 result.

FU02g3 showed:

```text
The FU02f1 C60 reference region is not cheap under simple same-size/type nulls,
but connected and role-aware connected decoys can produce near-reference
profiles at about 9-10%.
```

FU02g4 asks the sharper symmetry/signature question:

```text
Is the FU02f1 C60 carrier region merely one common connected C60 face patch,
or does it represent a constrained role-colored patch class under the C60
face-adjacency graph automorphisms?
```

Internal formulation:

```text
Ist unser Klunker nur irgendein verbundener Patch,
oder eine besondere Rollen-/Symmetrieklasse?
```

---

## 2. Run status

The networkx-enabled rerun completed successfully.

Warnings:

```text
WARNINGS: 0
```

Automorphism enumeration status:

```text
status = complete
stopped_reason = complete
```

This supersedes the earlier fallback-only run in which networkx was unavailable.

---

## 3. Automorphism summary

Observed automorphism summary:

```json
{
  "automorphism_count_observed": 120,
  "carrier_orbit_size_observed": 120,
  "carrier_stabilizer_size_observed": 1,
  "enabled": true,
  "node_match_preserves_cell_type": true,
  "role_colored_orbit_size_observed": 120,
  "role_colored_stabilizer_size_observed": 1,
  "scope_note": "Automorphisms are face-adjacency graph automorphisms preserving cell_type.",
  "status": "complete",
  "stopped_reason": "complete"
}
```

Interpretation:

```text
The reconstructed C60 face-adjacency graph has 120 observed automorphisms when
cell type is preserved.
```

The reference carrier patch has:

```text
carrier_orbit_size_observed = 120
carrier_stabilizer_size_observed = 1
```

The role-colored reference patch has:

```text
role_colored_orbit_size_observed = 120
role_colored_stabilizer_size_observed = 1
```

This means:

```text
No nontrivial observed automorphism leaves the carrier set or the role-colored
assignment fixed.
```

Equivalently:

```text
The FU02f1 patch is one representative of a 120-member symmetry-equivalent
orbit class under the reconstructed face-type-preserving C60 face graph.
```

Internal formulation:

```text
Der konkrete Ort ist nicht heilig.
Die Strukturklasse zählt.
```

---

## 4. Symmetry interpretation

The stabilizer result is important.

```text
carrier_stabilizer_size_observed = 1
role_colored_stabilizer_size_observed = 1
```

This indicates that the patch is not centered on a symmetry-invariant fixed
region of the C60 face graph.

Instead:

```text
The patch breaks the full observed face-graph automorphism symmetry.
```

But it does so in a symmetric way:

```text
There are 120 equivalent placements of the same carrier/role-colored patch
under the automorphism group.
```

Thus the result should be phrased as an orbit-class result, not a unique-place
result.

Allowed wording:

```text
The FU02f1 carrier region should be interpreted as an orbit representative of a
role-colored C60 patch class, not as a unique absolute location on the molecule.
```

Not allowed:

```text
The diagnostic identifies a unique physical place on C60.
```

---

## 5. Patch-signature sampling summary

Signature-match summary after rerun:

```json
{
  "carrier_signature_match_count": 1,
  "carrier_signature_match_fraction": 0.0002,
  "diagnostic_label": "role_signature_not_reproduced_in_samples",
  "near_carrier_signature_count": 10,
  "near_carrier_signature_fraction": 0.002,
  "near_role_colored_signature_count": 0,
  "near_role_colored_signature_fraction": 0.0,
  "near_signature_max_abs_difference_sum": 2,
  "role_colored_signature_match_count": 0,
  "role_colored_signature_match_fraction": 0.0,
  "sample_count": 5000,
  "scope_note": "Sampled connected same-size patches; not exhaustive unless stated elsewhere."
}
```

Interpretation:

```text
Among 5000 sampled connected same-size C60 face patches, the uncolored patch
signature is rare and the role-colored signature is not reproduced.
```

Detailed readout:

```text
uncolored exact signature:
  1 / 5000 = 0.0002

uncolored near signature:
  10 / 5000 = 0.002

role-colored exact signature:
  0 / 5000 = 0.0

role-colored near signature:
  0 / 5000 = 0.0
```

This confirms the fallback-mode finding and slightly updates the near-uncolored
count from 6/5000 to 10/5000 because the rerun resampled connected patches.

Central result:

```text
The uncolored patch profile is rare in the sampled connected-patch ensemble.
The role-colored patch profile is not observed in the sampled connected-patch
ensemble.
```

Internal formulation:

```text
Der Fleck allein ist selten.
Der Fleck mit Rollenfarbe wurde im Sample gar nicht getroffen.
```

---

## 6. Combined FU02g4 result

FU02g4 now has two completed pieces:

### 6.1 Orbit piece

```text
The reference patch is one representative of a 120-member automorphism orbit.
The stabilizer is trivial.
```

Meaning:

```text
The concrete face labels are not absolute.
The symmetry-equivalence class is the meaningful object.
```

### 6.2 Signature piece

```text
The detailed role-colored patch signature is not reproduced among 5000 sampled
connected same-size patches.
```

Meaning:

```text
The role-colored structure is not merely any connected same-size patch.
```

Together:

```text
The FU02f1 reference carrier region is best interpreted as a role-colored
orbit-class representative with a rare sampled patch signature.
```

This is stronger than FU02g3 but still construction-qualified.

---

## 7. Relation to FU02g3

FU02g3 showed:

```text
connected_patch_seeded:
  near_reference_fraction = 0.09

role_count_preserving_connected_patch:
  near_reference_fraction = 0.095
```

FU02g4 explains why that did not settle the issue:

```text
The FU02g3 near-reference criteria were coarse.
They could be satisfied by broad connected/role-count similarity.

FU02g4 uses sharper role-colored patch signatures.
Under that sharper criterion, no exact or near role-colored signature appears
in 5000 connected same-size samples.
```

Thus:

```text
FU02g3:
  coarse similarity is sometimes cheap.

FU02g4:
  detailed role-colored signature is not observed in the sampled decoys.
```

---

## 8. Befund / Interpretation / Hypothesis / Open Gap

### Befund

```text
The reconstructed C60 face-adjacency graph has 120 face-type-preserving
automorphisms. The FU02f1 carrier set and role-colored carrier assignment each
have observed orbit size 120 and stabilizer size 1. Among 5000 sampled connected
same-size patches, the uncolored reference signature is rare and the role-
colored reference signature is not reproduced.
```

### Interpretation

```text
The FU02f1 carrier region is not a unique absolute face location. It is one
representative of a full symmetry-equivalent orbit class. Its detailed
role-colored patch profile appears substantially more constrained than generic
connected same-size patch structure.
```

### Hypothesis

```text
The real-structure-memory candidate may reside in the role-colored orbit class:
a symmetry-equivalent family of C60 face patches with specific mixed-core /
pentagon-boundary coupling, rather than in one absolute labelled patch.
```

### Open gap

```text
The connected-patch comparison is sampled, not exhaustive. FU02g4 does not yet
prove that no other connected same-size patches share the role-colored signature
outside the 5000-sample ensemble.
```

---

## 9. Claim boundary

Allowed:

```text
FU02g4 supports a construction-qualified role-colored orbit-class specificity
indication for the FU02f1 C60 carrier region.
```

Allowed:

```text
The FU02f1 patch is one representative of a 120-member face-type-preserving
automorphism orbit with trivial stabilizer.
```

Allowed:

```text
The detailed role-colored patch signature was not reproduced among 5000
sampled connected same-size C60 face patches.
```

Not allowed:

```text
FU02g4 proves physical real-structure memory.
FU02g4 proves molecular quantum chemistry.
FU02g4 proves physical spacetime.
FU02g4 proves uniqueness of the patch beyond automorphism equivalence.
FU02g4 proves exhaustive absence among all connected C60 face patches.
FU02g4 provides a universal p-value.
```

---

## 10. Methodological consequence

FU02g4 changes the correct object of interpretation.

Not:

```text
This exact face label set is uniquely special.
```

But:

```text
This role-colored patch class, up to C60 face-graph automorphism, is the
relevant structure.
```

This is exactly the right symmetry-safe framing.

Internal formulation:

```text
Nicht der Ort ist heilig.
Die Orbitklasse ist der Klunker.
```

---

## 11. Recommended next block

Proceed to:

```text
BMS-FU02g5 — Geometry-Class Memory Synthesis
```

Purpose:

```text
Synthesize FU02g1-FU02g4 into a controlled statement about real-structure
memory:

  FU02g1:
    control structures built

  FU02g1b:
    nanotubes repaired

  FU02g2:
    generic interior proxy is cheap

  FU02g3:
    simple nulls rare, connected role-aware near profiles partly reproducible

  FU02g4:
    role-colored orbit-class signature is rare in sampled connected patches
    and forms a 120-member automorphism orbit with trivial stabilizer
```

Alternative before synthesis:

```text
BMS-FU02g4b — Exhaustive Connected Patch Signature Check
```

Purpose:

```text
Attempt exhaustive enumeration of connected 17-face C60 patches, if feasible,
to replace sampled evidence with exhaustive patch-signature counts.
```

Recommended if the project wants an even harder specificity statement before
synthesis.

---

## 12. Commit plan

Copy result note:

```bash
cd ~/Downloads/deBroglie_Kaster_Theorie/quantum-spacetime-bridge

cp ~/Downloads/BMS_FU02G4_SYMMETRY_ORBIT_INSPECTION_COMPLETE_RESULT_NOTE.md \
  docs/BMS_FU02G4_SYMMETRY_ORBIT_INSPECTION_COMPLETE_RESULT_NOTE.md

git status --short
```

Commit:

```bash
git add docs/BMS_FU02G4_SYMMETRY_ORBIT_INSPECTION_COMPLETE_RESULT_NOTE.md

git status --short

git commit -m "Add BMS-FU02g4 complete symmetry orbit result note"

git push
```

---

## 13. Internal summary

```text
FU02g4 complete:

  Automorphisms:
    120 complete

  Carrier orbit:
    size 120
    stabilizer 1

  Role-colored orbit:
    size 120
    stabilizer 1

  Sampling:
    carrier exact 1 / 5000
    carrier near 10 / 5000
    role exact 0 / 5000
    role near 0 / 5000

Conclusion:
  Nicht der konkrete Ort ist heilig.
  Die Orbitklasse ist der Klunker.

  Und diese Rollen-Signatur sieht im Sample nicht billig aus.
```
