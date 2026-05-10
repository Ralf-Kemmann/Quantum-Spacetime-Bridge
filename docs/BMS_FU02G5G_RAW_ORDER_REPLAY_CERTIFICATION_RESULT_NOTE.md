# BMS-FU02g5g — Raw-Order Replay Certification Result Note

**Date:** 2026-05-08  
**Project:** Quantum–Spacetime Bridge / Gravitation und RaumZeit  
**Status:** Internal result note  
**Block:** BMS-FU02g5g — FU02g4c Raw-Order Replay Certification Recovery

---

## 1. Purpose

BMS-FU02g5g was introduced after the FU02g5e2 red-team review and FU02g5f candidate_005 inspection.

The purpose was to address the remaining certification question:

```text
Do the BMS-FU02g5e1/g5e2/g5f scaffold-localized candidate indices correspond
to the original FU02g4c raw-order enumeration indices?
```

This block does not test a new physical hypothesis.

It is a certification/recovery audit.

Internal shorthand:

```text
Das alte Lagerbuch kennt die Regale.
Der Spiegelklunker hat eine direkte Karteikarte.
candidate_005 steht nur im Regalbereich, aber noch nicht mit eigener Inventarkarte.
```

---

## 2. Inputs

### 2.1 Candidate inputs

```text
runs/BMS-FU02g5e1/near_match_localization/near_match_candidates.csv
runs/BMS-FU02g5e2/near_match_decoy_classification/candidate_classification.csv
runs/BMS-FU02g5f/raw_order_replay_certification/candidate_revalidation.csv
```

### 2.2 FU02g4c audit material

```text
runs/BMS-FU02g4c/
data/bms_fu02g4c_orbit_reduced_resumable_config.yaml
data/bms_fu02g4c_inspect_window_*.yaml
```

### 2.3 Source graph

```text
runs/BMS-FU02d1/face_parser_repair_and_face_localization_open/bms_fu02d1_face_adjacency_edges.csv
```

---

## 3. Outputs

Generated output directory:

```text
runs/BMS-FU02g5g/fu02g4c_raw_order_replay_certification/
```

Generated files:

```text
summary.json
fu02g4c_log_inventory.csv
candidate_window_crosscheck.csv
candidate_replay_certification.csv
result_note.md
```

---

## 4. Befund

FU02g5g inventories available FU02g4c logs/configs and cross-checks the FU02g5e1/g5e2/g5f scaffold-localized candidates against parsed FU02g4c logged windows.

Observed certification status:

```text
overall_certification_status = partially_certified
original_fu02g4c_input_bundle_sufficient_for_rerun = False
candidate_008_raw_index_26187175_status = partially_certified
candidate_005_raw_index_26157530_status = not_certified
```

The runner did **not** achieve full raw-order replay certification.

The reason is explicit:

```text
The original FU02g4c enumerator and input bundle were not safely re-executed in this block.
```

---

## 5. Candidate-Level Certification Summary

### 5.1 Candidate_008 — known exact mirror candidate

```text
candidate_id = candidate_008
raw_index = 26187175
classification_primary = known_exact_spiegelklunker
exact_match = True
near_distance = 0
```

Certification result:

```text
replay_certification_status = partially_certified
```

Certification basis:

```text
FU02g4c exact-patch photo and narrow inspect log support raw_index 26187175,
but FU02g5g did not rerun the original enumerator.
```

Direct supporting FU02g4c window:

```text
runs/BMS-FU02g4c/inspect_window_26187175_26187176.log
```

Observed window counts:

```text
fu02g4c_window_exact_count = 1
fu02g4c_window_near_count = 1
```

Interpretation:

```text
candidate_008 has direct FU02g4c per-window support and is therefore stronger
than a scaffold-only candidate. However, because the original enumerator was not
re-executed in this block, the status remains partially_certified rather than
fully replay_certified.
```

Internal shorthand:

```text
Der Spiegelklunker hat eine direkte Karteikarte,
aber das Lagerbuch wurde noch nicht vollständig neu abgeschrieben.
```

---

### 5.2 Candidate_005 — coarse-signature degeneracy stress case

```text
candidate_id = candidate_005
raw_index = 26157530
classification_primary = coarse_signature_twin_but_not_exact
exact_match = False
near_distance = 0
```

Certification result:

```text
replay_certification_status = not_certified
```

Window relation:

```text
inside_fu02g4c_logged_window = True
matching_fu02g4c_log_file =
runs/BMS-FU02g4c/chunk_batch_logs_gap_safe/segment_25979015_26979014.log
```

Observed window counts:

```text
fu02g4c_window_exact_count = 1
fu02g4c_window_near_count = 7
```

Interpretation:

```text
candidate_005 lies inside a FU02g4c logged window that contains role-colored near
matches, but there is no direct per-index FU02g4c artifact confirming this
specific scaffold candidate as an original FU02g4c raw-order candidate.
```

Therefore:

```text
candidate_005 remains a scaffold-localized stress case pending narrow replay/photo certification.
```

Internal shorthand:

```text
candidate_005 steht im richtigen Regalbereich,
aber noch ohne eigene Inventarkarte.
```

---

### 5.3 Other near candidates

All other non-exact candidates are inside parsed FU02g4c logged windows.

However, without per-index replay or inspect-window artifacts, they remain:

```text
partially_certified by window compatibility
not fully replay_certified
```

This means:

```text
Their scaffold raw_index values are plausible relative to logged FU02g4c windows,
but not independently certified as FU02g4c raw-order indices.
```

---

## 6. Interpretation

FU02g5g creates a useful intermediate certification layer:

```text
1. The scaffold-localized candidates are not floating outside the FU02g4c audit material.
2. Their raw indices fall inside FU02g4c windows with matching aggregate near/exact counts.
3. The known exact candidate has direct narrow FU02g4c inspect support.
4. The non-exact candidates, including candidate_005, still lack per-index FU02g4c artifacts.
```

Therefore, the current situation is:

```text
log/window compatible, but not fully raw-order replay certified
```

for the non-exact candidates.

The known exact candidate is stronger:

```text
direct inspect-window support, but not full rerun certification
```

---

## 7. Hypothese

A bounded working hypothesis is:

```text
The known exact candidate at raw_index 26187175 is recoverable from FU02g4c audit
material, while the non-exact near candidates require explicit narrow replay/photo
artifacts before their scaffold indices can be promoted to FU02g4c raw-order
certified candidates.
```

This remains a methodological hypothesis, not a physical claim.

---

## 8. Offene Lücke

Full raw-order replay certification remains open.

A stronger certification would require:

```text
1. Reuse or isolation of the original FU02g4c enumerator.
2. Reuse or exact reconstruction of the original FU02g4c input bundle.
3. Narrow per-index replay windows for candidate_005 and the other non-exact candidates.
4. Output of direct per-index candidate node sets and signature status.
5. No overwrite of existing FU02g4c audit artifacts.
```

The most important missing item is:

```text
direct per-index FU02g4c artifact for candidate_005 / raw_index 26157530
```

---

## 9. Claim Boundary

### Allowed

```text
FU02g5g partially certifies the FU02g5e1/g5e2/g5f scaffold-localized candidate set
against available FU02g4c log/window artifacts.
```

Allowed:

```text
candidate_008 / raw_index 26187175 has direct FU02g4c narrow inspect-window support
and is therefore partially certified.
```

Allowed:

```text
candidate_005 / raw_index 26157530 lies inside a FU02g4c logged window with near
matches, but lacks direct per-index replay/photo support and remains not certified.
```

### Not allowed

```text
FU02g5g fully certifies FU02g4c raw-order replay.
```

Not allowed:

```text
candidate_005 is confirmed as an original FU02g4c near candidate.
```

Not allowed:

```text
The 10 non-exact near candidates are fully FU02g4c replay-certified.
```

Not allowed:

```text
FU02g5g proves global uniqueness, global rarity, physical emergence, spacetime
emergence, or Lorentz compatibility.
```

---

## 10. Consequence for the FU02 Line

The current FU02 chain should now be described as:

```text
FU02g4c/g4d:
exact match found, localized, photographed, automorphic to reference.

FU02g5c:
role transport frozen defensively:
no reference-role transport without explicit automorphy/isomorphism.

FU02g5d:
known exact candidate receives unique transported roles via one face-type-preserving mapping.

FU02g5e1:
11 near candidates localized in scaffold mode.

FU02g5e2:
only the known exact candidate is face-type-preserving isomorphic and role-transport-eligible;
the other 10 are non-isomorphic under this criterion.

FU02g5f:
candidate_005 explained as coarse-signature degeneracy:
near_distance = 0 does not imply exact match or isomorphism.

FU02g5g:
candidate set cross-checked against FU02g4c windows;
known exact candidate partially certified;
candidate_005 and other non-exact candidates remain pending per-index replay certification.
```

---

## 11. Recommended Next Control

Recommended next block:

```text
BMS-FU02g5g2 — Narrow Per-Index Replay/Photo Certification
```

Purpose:

```text
Generate direct per-index replay/photo artifacts for:
- candidate_005 / raw_index 26157530
- all 10 non-exact near candidates
```

Alternative next block:

```text
BMS-FU02g5h — Local Structural Role Rule Sensitivity Controls
```

But this should only follow after the certification status is made explicit in the project notes.

---

## 12. External-Facing Formulation

A safe external-facing formulation is:

```text
A follow-up certification audit cross-checked the scaffold-localized near-candidate
indices against available FU02g4c log and inspect-window artifacts. The known exact
candidate at raw_index 26187175 is supported by a narrow FU02g4c inspect window and
is treated as partially certified. The non-exact near candidates, including the
coarse-signature degeneracy case candidate_005, remain window-compatible but not
per-index replay-certified.
```

Avoid:

```text
All near candidates are certified FU02g4c candidates.
```

Avoid:

```text
The replay problem is solved.
```

---

## 13. Internal Summary

```text
Das alte Lagerbuch kennt die Regale.
Der Spiegelklunker hat eine direkte Karteikarte.
candidate_005 steht im richtigen Regalbereich,
aber noch ohne eigene Inventarkarte.

Nächster sauberer Schritt:
Karteikarten für die übrigen Near-Klunker ziehen,
ohne das alte Lagerbuch zu überschreiben.
```
