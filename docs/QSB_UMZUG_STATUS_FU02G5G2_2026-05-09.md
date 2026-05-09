# QSB Umzugsdatei 2 — Statusanker FU02g5g2

**Date:** 2026-05-09  
**Project:** Quantum–Spacetime Bridge / Gravitation und RaumZeit  
**Status:** Umzugsanker nach FU02g5g2  
**Scope:** FU02g5c → FU02g5g2

---

## 1. Arbeitsmodell

```text
Nova:
methodisches Klemmbrett — Spezifikation, Logik, Claim-Bremse, Red-Team-Synthese.

Codex:
lokaler Schraubenschlüssel — Dateien, Skripte, Configs, Tests, Outputs.

Ralf:
kreativer Kopf, Forschungsarchitekt und finale Kontrollinstanz.
```

Ralf liefert die originären Leitideen:

```text
de-Broglie-Interferenz
Isotopentest
isoelektrischer Test
Informationsübertragung analog chemischer Bindungsvarianz
C60 / Nanotube / Graphen als Vergleichsräume
Kristallmodell: Graphkanten analog Bindungen mit kovalent / gemischt / ionisch als möglicher Varianz
Knöpfchen-/Dellen-Intuition als Motivationswurzel
```

---

## 2. Repo-Anker

```bash
/home/ralf-kemmann/Downloads/deBroglie_Kaster_Theorie/quantum-spacetime-bridge
```

Verbindliche Struktur:

```text
docs/     Spezifikationen, Result Notes, Feldlisten, Zusammenfassungen
data/     Configs, Inputs, YAML/CSV/JSON
scripts/  ausführbare Skripte
runs/     Run Outputs und Diagnostik
```

---

## 3. FU02g4c/g4d Ausgangsanker

```text
raw_role_colored_signature_exact_match_count = 1
raw_role_colored_signature_near_match_count  = 11
```

Known exact candidate:

```text
raw_index = 26187175
nodes =
H_01;H_02;H_03;H_05;H_06;H_07;H_08;H_09;H_10;H_15;H_16;H_17;P_00;P_01;P_02;P_03;P_07
```

Kurzlesart:

```text
Der Klunker war kein fremder Kristall.
Es war unser eigener Klunker im Spiegelkabinett.
```

---

## 4. FU02g5c — Role Transport Rule

Eingefrorene Regel:

```text
mixed_core / pentagon_boundary dürfen nur unter expliziter Automorphie/Isomorphie
von der FU02f1-Referenz auf einen Kandidaten transportiert werden.
```

Nicht erlaubt:

```text
freie Rollenzuweisung
Analogietransport
post-hoc Rollenetiketten
```

Kurzform:

```text
Keine Etiketten auf fremde Klunker kleben.
Nur Spiegelklunker dürfen Referenzetiketten tragen.
```

---

## 5. FU02g5d — Automorphy-only Role Transport

Known exact candidate:

```text
mapping_count = 1
transport_allowed = true
mixed_core_invariant_across_mappings = True
pentagon_boundary_invariant_across_mappings = True
```

Lesart:

```text
Der Spiegelklunker bekommt seine Referenzrollen eindeutig über genau ein
face-type-preserving Mapping zurück.
```

---

## 6. FU02g5e1 / g5e2

g5e1:

```text
11 near candidates scaffold-localized
exact_match_count = 1
fu02g4c_order_guarantee = False
```

g5e2:

```text
candidate_count = 11
face_type_preserving_isomorphic_candidates = 1
non_isomorphic_near_candidates = 10
role_transport_allowed_candidates = 1
```

Klassifikation:

```text
1 known_exact_spiegelklunker
1 coarse_signature_twin_but_not_exact
2 local_near_decoy_distance_1
7 near_decoy_distance_2
```

---

## 7. candidate_005

```text
candidate_005
raw_index = 26157530
near_distance = 0
exact_match = False
uncolored_isomorphic_to_reference = False
face_type_preserving_isomorphic_to_reference = False
role_transport_allowed = False
```

g5f-Befund:

```text
candidate_005 ist ein coarse-signature degeneracy stress case.
near_distance = 0 bedeutet nicht exact match oder Isomorphie.
```

Node-Diff zum known exact:

```text
only_in_candidate_005: H_14
only_in_known_exact_candidate: H_17
```

Edge-Diff:

```text
only_in_candidate_005:
H_05--H_14
H_14--H_15
H_14--P_01

only_in_known_exact_candidate:
H_09--H_17
H_16--H_17
H_17--P_07
```

---

## 8. FU02g5g

```text
overall_certification_status = partially_certified
original_fu02g4c_input_bundle_sufficient_for_rerun = False
candidate_008_raw_index_26187175_status = partially_certified
candidate_005_raw_index_26157530_status = not_certified
```

Lesart:

```text
Das alte Lagerbuch kennt die Regale.
Der Spiegelklunker hat eine direkte Karteikarte.
candidate_005 steht im richtigen Regalbereich,
aber noch ohne eigene Inventarkarte.
```

---

## 9. FU02g5g2

g5g2 erzeugte narrow per-index photo certification im aktuellen scaffold/FU02g4c-style Replay.

Für alle 11 Kandidaten:

```text
node_set_agreement = True
edge_set_agreement = True
per_index_photo_status = matched_expected_nodes
```

candidate_005:

```text
matched_expected_nodes
node_set_agreement = True
edge_set_agreement = True
coarse_signature_degeneracy_stress_case = true
```

candidate_008 positive control:

```text
matched_expected_nodes
node_set_agreement = True
edge_set_agreement = True
uncolored_isomorphic_to_reference = True
face_type_preserving_isomorphic_to_reference = True
mapping_count = 1
role_transport_allowed_under_g5c = True
```

Weiterhin offen:

```text
full_fu02g4c_replay_certification = False
```

---

## 10. Sicherer Claim

```text
BMS-FU02g5g2 reproduces all 11 scaffold-localized near candidates by per-index
photo in the current deterministic scaffold/FU02g4c-style enumeration, with
node-set and induced-edge-set agreement. The known exact candidate remains the
only face-type-preserving isomorphic reference twin and the only candidate
eligible for automorphy-only role transport under FU02g5c. Candidate_005 is
directly reproduced as a coarse-signature degeneracy stress case: it has
near_distance=0 but is neither exact nor isomorphic. Full FU02g4c raw-order
replay certification remains open because the original enumerator and full
original input bundle were not certified as identically reused.
```

Nicht behaupten:

```text
global rarity
global uniqueness
physical emergence
spacetime emergence
full FU02g4c certification solved
```

---

## 11. Nächster Schritt offen

Mögliche Anschlussblöcke:

```text
BMS-FU02g5g3 — Certification Synthesis / Red-Team Update
BMS-FU02g5i — Original FU02g4c Enumerator/Input Bundle Recovery
FU03a — External Fullerene / Planar / Spherical Graph Controls
```

Empfehlung aus altem Chat:

```text
Erst g5g3 als Synthese schreiben,
dann entscheiden, ob voller FU02g4c-Amtsstempel oder externe Kontrollen wichtiger sind.
```
