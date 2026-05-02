# BMS-FU02g4 — Symmetry-Orbit Inspection of the C60 Reference Carrier Region Initial Result Note

Date: 2026-05-03  
Project: Gravitation und RaumZeit / Quantum-Spacetime-Bridge  
Recommended repo target: `docs/BMS_FU02G4_SYMMETRY_ORBIT_INSPECTION_INITIAL_RESULT_NOTE.md`  
Status: Initial result note for BMS-FU02g4 fallback-mode run

---

## 1. Purpose

BMS-FU02g4 follows the mixed FU02g3 result.

FU02g3 showed:

```text
The FU02f1 C60 reference region is not cheap under simple same-size/type nulls,
but connected and role-aware connected decoys can produce near-reference
profiles at about 9-10%.
```

FU02g4 therefore asks the sharper patch/symmetry question:

```text
Is the FU02f1 C60 carrier region just any connected same-size C60 face patch,
or does it carry a rarer role-colored patch signature?
```

Internal formulation:

```text
Ist unser Klunker nur irgendein verbundener Patch,
oder eine besondere Rollen-/Symmetrieklasse?
```

---

## 2. Run status

FU02g4 completed in patch-signature fallback mode.

Automorphism enumeration was skipped because `networkx` was unavailable:

```text
warning - networkx unavailable; automorphism orbit summary skipped.
```

Automorphism summary:

```json
{
  "enabled": true,
  "status": "skipped_networkx_unavailable"
}
```

This means:

```text
The automorphism-orbit readouts are unavailable in this run.
The patch-signature and connected-patch sampling outputs remain usable.
```

Scope statement:

```text
FU02g4-v0 fallback mode provides patch-signature sampling evidence, not a full
automorphism-orbit result.
```

---

## 3. Reference patch signature

### 3.1 Carrier composition

```text
carrier_face_count = 17
carrier_hexagon_count = 12
carrier_pentagon_count = 5
carrier_component_count = 1
largest_carrier_component_count = 17
```

Interpretation:

```text
The FU02f1 reference region is one connected 17-face patch with 12 hexagons
and 5 pentagons.
```

### 3.2 Carrier adjacency profile

```text
carrier_internal_adjacency_count = 37
carrier_boundary_adjacency_count = 23
carrier_external_neighbor_count = 11
```

Interpretation:

```text
The patch is highly internally connected while still having an 11-face external
neighbor shell.
```

### 3.3 Carrier induced degree histogram

```text
carrier_induced_degree_histogram =
  {'2': 1, '3': 4, '4': 3, '5': 6, '6': 3}
```

Interpretation:

```text
The induced patch is not a simple uniform disk. It has a structured internal
degree profile with several high-support carrier faces.
```

### 3.4 Boundary neighbor type counts

```text
boundary_neighbor_type_counts =
  {'hexagon': 10, 'pentagon': 13}
```

Interpretation:

```text
The external boundary shell is pentagon-rich relative to a purely hexagonal
patch intuition.
```

---

## 4. Role-colored reference signature

### 4.1 Role counts

```text
mixed_core_count = 8
pentagon_boundary_count = 9
```

Reference sets:

```text
mixed_core_set =
  H_09
  H_11
  H_13
  H_16
  H_17
  H_18
  H_19
  H_20

pentagon_boundary_set =
  H_07
  H_12
  H_14
  H_15
  P_07
  P_08
  P_09
  P_10
  P_11
```

Full carrier set:

```text
carrier_set =
  H_07
  H_09
  H_11
  H_12
  H_13
  H_14
  H_15
  H_16
  H_17
  H_18
  H_19
  H_20
  P_07
  P_08
  P_09
  P_10
  P_11
```

### 4.2 Role adjacency profile

```text
mixed_core_internal_adjacency_count = 8
pentagon_boundary_internal_adjacency_count = 5
mixed_to_pentagon_boundary_adjacency_count = 24
```

Interpretation:

```text
The role-colored structure is dominated by cross-role coupling:
24 mixed-core to pentagon-boundary adjacencies.
```

This is the strongest qualitative feature of the FU02g4 reference profile.

Internal image:

```text
Der Hexagon-Mixed-Core ist nicht isoliert.
Er ist dicht mit der Pentagon-/Boundary-Rolle vernäht.
```

### 4.3 Role induced degree histograms

```text
mixed_core_induced_degree_histogram =
  {'1': 3, '2': 2, '3': 3}

pentagon_boundary_induced_degree_histogram =
  {'0': 2, '1': 4, '2': 3}
```

Interpretation:

```text
The mixed-core role is internally connected but not closed.
The pentagon-boundary role contains weakly or non-internally connected members,
consistent with a boundary/shell role rather than a second dense core.
```

---

## 5. Signature match sampling result

FU02g4 sampled 5000 connected same-size C60 face patches.

Signature match summary:

```text
sample_count = 5000

carrier_signature_match_count = 1
carrier_signature_match_fraction = 0.0002

near_carrier_signature_count = 6
near_carrier_signature_fraction = 0.0012

role_colored_signature_match_count = 0
role_colored_signature_match_fraction = 0.0

near_role_colored_signature_count = 0
near_role_colored_signature_fraction = 0.0

near_signature_max_abs_difference_sum = 2

diagnostic_label = role_signature_not_reproduced_in_samples
```

### Interpretation

Uncolored carrier signature:

```text
Exact uncolored patch-profile matches are extremely rare:
  1 / 5000 = 0.0002

Near uncolored patch-profile matches are also rare:
  6 / 5000 = 0.0012
```

Role-colored signature:

```text
No exact role-colored signature match occurred in 5000 samples.
No near role-colored signature match occurred in 5000 samples.
```

This is the central FU02g4 fallback-mode result.

Internal formulation:

```text
Der Fleck allein ist schon selten.
Der Fleck mit Rollenfarbe wurde in den Samples gar nicht getroffen.
```

---

## 6. Relation to FU02g3

FU02g3 had shown that connected/role-aware decoys can reproduce coarse
near-reference criteria at about 9-10%.

FU02g4 refines this:

```text
Coarse near-reference profiles can be reproduced.
But the detailed role-colored patch signature is not reproduced in 5000
connected same-size patch samples.
```

Thus the apparent tension resolves as follows:

```text
FU02g3 near criteria were broad enough for connected decoys to pass.

FU02g4 patch-signature criteria are sharper and reveal that the detailed
role-colored structure is much rarer in the sampled C60 face graph.
```

---

## 7. Befund / Interpretation / Hypothesis / Open Gap

### Befund

```text
The FU02f1 C60 reference carrier region has a rare sampled patch signature.
Exact uncolored signature match occurs in 1/5000 samples; near uncolored
signature match occurs in 6/5000 samples. No exact or near role-colored
signature match occurs in 5000 connected same-size patch samples.
```

### Interpretation

```text
The FU02f1 carrier region is not merely any connected same-size patch on the
C60 face graph. Its detailed role-colored patch profile appears substantially
more constrained than the coarse FU02g3 near-reference criteria suggested.
```

### Hypothesis

```text
The relevant real-structure-memory specificity may reside in the role-colored
patch signature: a connected hexagon/pentagon region with strong mixed-core to
pentagon-boundary cross-coupling and a distinctive induced-degree profile.
```

### Open gap

```text
Automorphism-orbit enumeration was not performed in this run because networkx
was unavailable. Therefore FU02g4-v0 fallback mode does not yet determine the
automorphism orbit size, stabilizer size, or the number of symmetry-equivalent
role-colored copies.
```

---

## 8. Claim boundary

Allowed:

```text
FU02g4 fallback mode supports a construction-qualified patch-signature
specificity indication: the FU02f1 role-colored C60 carrier signature was not
reproduced among 5000 sampled connected same-size C60 face patches.
```

Allowed:

```text
The uncolored reference patch profile is rare in the sampled connected-patch
ensemble, with one exact match and six near matches among 5000 samples.
```

Allowed:

```text
The result sharpens FU02g3 by showing that coarse near-reference criteria are
less selective than the detailed role-colored patch signature.
```

Not allowed:

```text
FU02g4 proves real-structure memory.
FU02g4 proves physical spacetime.
FU02g4 proves molecular quantum chemistry.
FU02g4 proves full C60 automorphism-orbit uniqueness.
FU02g4 proves impossibility under all connected patches.
FU02g4 provides a universal p-value.
```

---

## 9. Methodological consequence

FU02g4 fallback mode gives a stronger direction than FU02g3:

```text
The specificity candidate is no longer merely:
  compact connected patch

Nor merely:
  same role counts

But:
  role-colored patch signature with strong mixed-core / pentagon-boundary
  cross-adjacency and distinctive induced-degree profile.
```

Internal formulation:

```text
Die Attrappen konnten grob die Rollenfarbe treffen.
Aber die genaue Rollen-Naht des Klunkers treffen sie nicht.
```

---

## 10. Recommended next step

There are two reasonable next steps.

### Option A — install networkx and rerun FU02g4

Purpose:

```text
Complete automorphism-orbit and stabilizer readouts.
```

Command:

```bash
cd ~/Downloads/deBroglie_Kaster_Theorie/quantum-spacetime-bridge

python -m pip install networkx

python scripts/run_bms_fu02g4_symmetry_orbit_inspection.py \
  --config data/bms_fu02g4_symmetry_orbit_inspection_config.yaml
```

If PEP-668 blocks global installation, use the project venv instead.

### Option B — proceed to FU02g4b

```text
BMS-FU02g4b — Exact Patch Signature Exhaustion / Stronger Canonical Patch Test
```

Purpose:

```text
Strengthen the sampled-patch result by either exhaustive connected-patch
enumeration where feasible or by canonical graph-isomorphism signatures for
role-colored patches.
```

Recommended if automorphism enumeration remains unavailable.

---

## 11. Commit plan

Copy result note:

```bash
cd ~/Downloads/deBroglie_Kaster_Theorie/quantum-spacetime-bridge

cp ~/Downloads/BMS_FU02G4_SYMMETRY_ORBIT_INSPECTION_INITIAL_RESULT_NOTE.md \
  docs/BMS_FU02G4_SYMMETRY_ORBIT_INSPECTION_INITIAL_RESULT_NOTE.md

git status --short
```

Commit:

```bash
git add docs/BMS_FU02G4_SYMMETRY_ORBIT_INSPECTION_INITIAL_RESULT_NOTE.md

git status --short

git commit -m "Add BMS-FU02g4 symmetry orbit inspection result note"

git push
```

---

## 12. Internal summary

```text
FU02g4 fallback mode:

  Automorphism:
    skipped, networkx unavailable

  Patch signature:
    carrier exact match: 1 / 5000
    carrier near match: 6 / 5000

  Role-colored signature:
    exact match: 0 / 5000
    near match: 0 / 5000

Conclusion:
  Der Fleck mit Rollenfarbe sieht in diesem Sample nicht billig aus.

Next:
  networkx rerun for automorphism orbit
  or FU02g4b for stronger exact/canonical patch test.
```
