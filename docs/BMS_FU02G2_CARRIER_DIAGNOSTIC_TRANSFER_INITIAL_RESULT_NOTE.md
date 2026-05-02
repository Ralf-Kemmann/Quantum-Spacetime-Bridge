# BMS-FU02g2 — Carrier Diagnostic Transfer to Geometry-Class Controls Initial Result Note

Date: 2026-05-02  
Project: Gravitation und RaumZeit / Quantum-Spacetime-Bridge  
Recommended repo target: `docs/BMS_FU02G2_CARRIER_DIAGNOSTIC_TRANSFER_INITIAL_RESULT_NOTE.md`  
Status: Initial result note for BMS-FU02g2-v0

---

## 1. Purpose

BMS-FU02g2 transfers a transparent cell-level carrier-proxy diagnostic to the
geometry-class control set prepared by FU02g1 and FU02g1b.

Input control set:

```text
c60_reference
graphene_patch
nanotube_armchair_repaired
nanotube_zigzag_repaired
```

Scope:

```text
Diagnostic transfer only.
No chemistry claim.
No spacetime claim.
No final real-structure memory claim.
```

Internal question:

```text
Malt C60 einen anderen Klunker als flach/offen/gekrümmt?
```

---

## 2. Run status

The FU02g2 runner completed and produced structure summaries, geometry-class
comparison rows and cell-level carrier diagnostics.

The readout shows all four structures processed:

```text
c60_reference
graphene_patch
nanotube_armchair_repaired
nanotube_zigzag_repaired
```

No runner failure is indicated in the supplied readout.

---

## 3. Structure summary

### 3.1 C60 reference

```text
cells = 32
carriers = 10
components = 1
largest = 10
compactness = 1.0
boundary_dep = 0.0
adjacent_ratio = 1.5
label = compact_connected_carrier_candidate
fu02f1_overlap = 0.2
```

Interpretation:

```text
The FU02g2 generic proxy selects one compact connected 10-cell C60 carrier set.
However, overlap with the FU02f1 C60 carrier-region reference is only 0.2.
```

Important:

```text
The selected top C60 proxy cells are largely early hexagon ids H_01-H_10,
not the previously established FU02f1 mixed-core/pentagon-boundary region.
```

This indicates that FU02g2-v0's generic score is not yet recovering the FU02f1
C60 real-structure carrier pattern.

---

### 3.2 Graphene patch

```text
cells = 20
carriers = 6
components = 1
largest = 6
compactness = 1.0
boundary_dep = 0.0
adjacent_ratio = 2.0
label = compact_connected_carrier_candidate
```

Interpretation:

```text
The graphene patch also produces a compact connected interior carrier set.
```

This is expected for the v0 score because interior hexagonal cells have maximal
adjacency and no boundary penalty.

---

### 3.3 Repaired armchair nanotube

```text
cells = 48
carriers = 14
components = 1
largest = 14
compactness = 1.0
boundary_dep = 0.0
adjacent_ratio = 1.3571428571428572
label = compact_connected_carrier_candidate
```

Interpretation:

```text
The repaired armchair nanotube also produces a compact connected interior
carrier set.
```

Again, this is expected for the v0 score because interior tube cells dominate
over open-end boundary cells.

---

### 3.4 Repaired zigzag nanotube

```text
cells = 48
carriers = 14
components = 1
largest = 14
compactness = 1.0
boundary_dep = 0.0
adjacent_ratio = 1.2142857142857142
label = compact_connected_carrier_candidate
```

Interpretation:

```text
The repaired zigzag nanotube also produces a compact connected interior carrier
set.
```

The result is clean as a transfer diagnostic, but not C60-specific.

---

## 4. Geometry-class comparison

The geometry comparison is nearly uniform:

```text
c60_reference:
  carrier_fraction = 0.3125
  compactness = 1.0
  boundary_dep = 0.0
  largest/all = 0.3125

graphene_patch:
  carrier_fraction = 0.3
  compactness = 1.0
  boundary_dep = 0.0
  largest/all = 0.3

nanotube_armchair_repaired:
  carrier_fraction = 0.2916666666666667
  compactness = 1.0
  boundary_dep = 0.0
  largest/all = 0.2916666666666667

nanotube_zigzag_repaired:
  carrier_fraction = 0.2916666666666667
  compactness = 1.0
  boundary_dep = 0.0
  largest/all = 0.2916666666666667
```

Main observation:

```text
The v0 proxy selects compact, connected, non-boundary carrier regions in all
geometry classes.
```

Therefore, the v0 transfer diagnostic does not by itself distinguish C60 from
flat/open or open-curved hexagonal controls.

---

## 5. Cell role counts

```text
c60_reference:
  carrier_adjacent_cell: 15
  noncarrier_cell: 7
  carrier_core_cell: 10

graphene_patch:
  noncarrier_cell: 2
  carrier_adjacent_cell: 12
  carrier_core_cell: 6

nanotube_armchair_repaired:
  noncarrier_cell: 15
  carrier_adjacent_cell: 19
  carrier_core_cell: 14

nanotube_zigzag_repaired:
  carrier_adjacent_cell: 17
  carrier_core_cell: 14
  noncarrier_cell: 17
```

Interpretation:

```text
All structures show a core-plus-adjacent-shell pattern under the v0 proxy.
```

This is useful as a sanity check, but not as a specificity claim.

---

## 6. Top carrier-cell behavior

### 6.1 C60

Top C60 carrier cells are:

```text
H_01
H_02
H_03
H_04
H_05
H_06
H_07
H_08
H_09
H_10
```

All have:

```text
score = 1.0
adjdeg = 6.0
mean_node_deg = 3.0
boundary = 0
```

FU02f1 overlap among these top cells includes only:

```text
H_07 = hp_boundary_face
H_09 = mixed_seam_boundary_face
```

Thus:

```text
fu02f1_overlap = 0.2
```

Interpretation:

```text
The v0 C60 proxy prefers high-adjacency hexagon cells in a stable sort order.
It does not reconstruct the prior FU02f1 mixed-core/pentagon-boundary carrier
region.
```

This is a key limitation.

---

### 6.2 Graphene and nanotubes

For graphene and both nanotubes, top carrier cells have:

```text
score = 2.25
adjdeg = 6.0
mean_node_deg = 3.0
boundary = 0
```

Interpretation:

```text
The proxy score is dominated by interior regularity.
```

This means the selected carriers are essentially interior-cell carriers, not
real-structure-memory carriers.

---

## 7. Main result

BMS-FU02g2-v0 is a successful technical transfer test, but not a successful
specificity diagnostic.

Core result:

```text
The generic cell-level carrier proxy is too broad:
it finds compact connected interior carrier regions in all tested geometry
classes.
```

Therefore:

```text
compact_connected_carrier_candidate
```

is not a C60-specific label in FU02g2-v0.

Internal summary:

```text
Der Proxy malt überall einen schönen Innenklunker.
Das ist sauber gelaufen,
aber noch nicht spezifisch genug.
```

---

## 8. Interpretation

### Befund

```text
All four geometry classes produce compact connected non-boundary carrier sets
under the FU02g2-v0 proxy.
```

### Interpretation

```text
The v0 proxy mainly detects interior regularity and cell-adjacency support.
This is expected for regular hexagonal cell complexes and does not distinguish
C60-specific structure memory.
```

### Hypothesis

```text
Real-structure memory will require reference-aware or role-aware diagnostics,
not only generic interior-support scoring.
```

### Open gap

```text
FU02g2-v0 does not yet test whether the FU02f1 C60 carrier region is specific
against geometry-class controls.
It only shows that a generic compact-cell proxy is not sufficient.
```

---

## 9. Claim boundary

Allowed:

```text
FU02g2-v0 successfully transfers a cell-level carrier proxy diagnostic across
the C60, graphene and repaired nanotube control set.
```

Allowed:

```text
The v0 proxy produces compact connected interior carrier regions in all tested
geometry classes, indicating that compactness alone is not C60-specific.
```

Allowed:

```text
The low C60 FU02f1 reference overlap indicates that the generic v0 score does
not reconstruct the prior FU02f1 mixed-core/pentagon-boundary carrier region.
```

Not allowed:

```text
FU02g2 proves real-structure memory.
FU02g2 proves C60 specificity.
FU02g2 proves molecular chemistry.
FU02g2 proves spacetime.
```

---

## 10. Methodological consequence

FU02g2-v0 tells us what not to use as a specificity claim:

```text
A compact connected carrier patch alone is cheap.
```

This mirrors the earlier FU02e lesson:

```text
Connectedness alone is cheap.
Compactness plus correct role-balance was stronger.
```

For the geometry-class program, the next step must include:

```text
reference-aware structure memory,
role-aware recovery,
null controls,
and C60 FU02f1-region overlap or orbit-aware comparison.
```

---

## 11. Recommended next block

Proceed to:

```text
BMS-FU02g3 — Real-Structure Memory Comparison and Null Specificity
```

Purpose:

```text
Test whether the FU02f1 C60 carrier-region pattern is specific beyond:
  generic interior regularity,
  boundary avoidance,
  hexagonal adjacency support,
  open/flat geometry controls,
  open-curved nanotube controls.
```

Candidate upgrades:

```text
1. Use FU02f1 C60 carrier-region reference explicitly.
2. Define C60 reference roles:
   mixed_core
   pentagon_boundary
   carrier_adjacent
   noncarrier
3. Build role-compatible pseudo-targets in controls where possible.
4. Use nulls:
   boundary-preserving shuffle
   degree-preserving cell shuffle
   cell-adjacency-preserving patch shuffle
   fixed-carrier-count random patches
5. Score:
   reference_overlap
   role_balance_recovery
   compactness beyond random patch
   boundary dependence
   geometry-class separation
```

Internal next-step formulation:

```text
Nicht:
  Findet der Proxy irgendwo einen Innenklunker?

Sondern:
  Kann er den C60-Klunker mit seiner Rollenfarbe wiederfinden,
  und ist das gegen Kontrollen billig oder nicht?
```

---

## 12. Commit plan

Copy result note:

```bash
cd ~/Downloads/deBroglie_Kaster_Theorie/quantum-spacetime-bridge

cp ~/Downloads/BMS_FU02G2_CARRIER_DIAGNOSTIC_TRANSFER_INITIAL_RESULT_NOTE.md \
  docs/BMS_FU02G2_CARRIER_DIAGNOSTIC_TRANSFER_INITIAL_RESULT_NOTE.md

git status --short
```

Commit:

```bash
git add docs/BMS_FU02G2_CARRIER_DIAGNOSTIC_TRANSFER_INITIAL_RESULT_NOTE.md

git status --short

git commit -m "Add BMS-FU02g2 carrier diagnostic transfer result note"

git push
```

---

## 13. Internal summary

```text
FU02g2-v0:

  Läuft.
  Alle Prüfkörper verarbeitet.
  Überall kompakter Innenklunker.
  C60-FU02f1-Overlap nur 0.2.

Conclusion:
  Der Transfer funktioniert technisch.
  Der Proxy ist als Spezifitätsdiagnostik zu generisch.

Next:
  FU02g3 mit Referenzrolle + Nulls.
```
