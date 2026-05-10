# QSB Abschlussbericht — FU02g5g2 Per-Index Replay/Photo Certification

**Date:** 2026-05-09  
**Project:** Quantum–Spacetime Bridge / Gravitation und RaumZeit  
**Status:** Internal Abschlussbericht  
**Block range:** FU02g5c → FU02g5g2  
**Main topic:** Role transport, near-decoy classification, candidate_005, per-index photo certification

---

## 1. Arbeitsmodus

Der Maschinenraum-Workflow bleibt bestätigt:

```text
Nova:
methodisches Klemmbrett — Spezifikation, Logik, Claim-Bremse, Red-Team-Synthese.

Codex:
lokaler Schraubenschlüssel — Dateien, Skripte, Tests, Repo-Maschinenraum.

Ralf:
kreativer Kopf, Forschungsarchitekt und finale Kontrollinstanz.
```

Ralf liefert die originären physikalisch-chemischen Leitideen und entscheidet über Richtung, Plausibilität, wissenschaftliche Freigabe und Claim-Grenzen.

Codex ist als ressourcenschonender lokaler Implementierungshelfer nützlich, solange die Aufgaben eng geführt sind:

```text
Create exactly these files.
Do not edit existing files.
Do not touch closed FU02 anchor files.
Do not run git add / git commit / git reset / git push.
Show git status.
```

---

## 2. Ausgangslage vor FU02g5g2

### FU02g4c / FU02g4d

```text
raw_role_colored_signature_exact_match_count = 1
raw_role_colored_signature_near_match_count  = 11
```

Bekannter exact candidate:

```text
raw_index = 26187175
nodes =
H_01;H_02;H_03;H_05;H_06;H_07;H_08;H_09;H_10;H_15;H_16;H_17;P_00;P_01;P_02;P_03;P_07
```

Dieser Kandidat wurde lokalisiert, fotografiert und als automorph/isomorph zur FU02f1-Referenz identifiziert.

Interne Kurzform:

```text
Der Klunker war kein fremder Kristall.
Es war unser eigener Klunker im Spiegelkabinett.
```

### FU02g5c

Die Rollen-Transport-Regel wurde defensiv eingefroren:

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

Interne Kurzform:

```text
Keine Etiketten auf fremde Klunker kleben.
Nur Spiegelklunker dürfen Referenzetiketten tragen.
```

### FU02g5d

Der known exact candidate bestand den Automorphy-only Role-Transport-Check:

```text
mapping_count = 1
transport_allowed = true
mixed_core_invariant_across_mappings = True
pentagon_boundary_invariant_across_mappings = True
```

### FU02g5e1

Die 11 Near-Kandidaten wurden als scaffold-localized candidate photo set lokalisiert.

Wichtige Bremse:

```text
Run label: scaffold localization
fu02g4c_order_guarantee = False
```

### FU02g5e2

Die 11 Kandidaten wurden klassifiziert:

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

Nur candidate_008 / raw_index 26187175 war isomorph und role-transport-berechtigt.

### FU02g5f

Candidate_005 wurde als coarse-signature degeneracy stress case untersucht:

```text
candidate_005
raw_index = 26157530
near_distance = 0
exact_match = False
uncolored_isomorphic_to_reference = False
face_type_preserving_isomorphic_to_reference = False
```

Wichtiger Befund:

```text
near_distance = 0 bedeutet nicht:
- exact match
- node-set identity
- edge-set identity
- graph isomorphism
- role-transport eligibility
```

Candidate_005 unterscheidet sich vom known exact candidate durch:

```text
only_in_candidate_005:
H_14

only_in_known_exact_candidate:
H_17
```

und drei geänderte interne Kanten:

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

### FU02g5g

FU02g5g prüfte die FU02g4c-Log-/Window-Kompatibilität:

```text
overall_certification_status = partially_certified
original_fu02g4c_input_bundle_sufficient_for_rerun = False
candidate_008_raw_index_26187175_status = partially_certified
candidate_005_raw_index_26157530_status = not_certified
```

Der known exact candidate hatte direkte FU02g4c-Inspect-Unterstützung. Candidate_005 lag in einem passenden FU02g4c-Logfenster, aber noch ohne direkte per-index Karteikarte.

---

## 3. FU02g5g2 — Ziel

BMS-FU02g5g2 wurde gestartet, um die nächste Audit-Stufe zu erreichen:

```text
Narrow Per-Index Replay/Photo Certification
```

Ziel war:

```text
Für jeden Near-Kandidaten eine eigene per-index Foto-Karteikarte im aktuellen
scaffold/FU02g4c-style Replay erzeugen.
```

Wichtig: Der Block sollte **nicht** automatisch volle FU02g4c raw-order certification behaupten.

Zu unterscheiden waren:

```text
per_index_photo_agreement
scaffold_order_agreement
full_fu02g4c_replay_certification
```

---

## 4. FU02g5g2 — Inputs und Outputs

Verwendete Inputs:

```text
runs/BMS-FU02g5e1/near_match_localization/near_match_candidates.csv
runs/BMS-FU02g5e2/near_match_decoy_classification/candidate_classification.csv
runs/BMS-FU02g5f/raw_order_replay_certification/candidate_revalidation.csv
runs/BMS-FU02g5g/fu02g4c_raw_order_replay_certification/candidate_replay_certification.csv
runs/BMS-FU02d1/face_parser_repair_and_face_localization_open/bms_fu02d1_face_adjacency_edges.csv
```

Output-Verzeichnis:

```text
runs/BMS-FU02g5g2/narrow_per_index_replay_photo_certification/
```

Wichtige Outputs:

```text
summary.json
per_index_photo_certification.csv
per_index_node_photos.csv
per_index_edge_photos.csv
isomorphism_recheck.csv
result_note.md
```

Neue Codex-Dateien:

```text
docs/BMS_FU02G5G2_NARROW_PER_INDEX_REPLAY_PHOTO_CERTIFICATION_FIELD_LIST.md
data/bms_fu02g5g2_narrow_per_index_replay_photo_certification_config.yaml
scripts/run_bms_fu02g5g2_narrow_per_index_replay_photo_certification.py
```

Bestehende Dateien wurden nicht verändert.

---

## 5. FU02g5g2 — Befund

FU02g5g2 rekonstruierte die aktuelle deterministic scaffold/FU02g4c-style connected 17-face patch order aus dem reparierten C60-Face-Graphen und erzeugte per-index Photos für die konfigurierten Targets.

Für alle Kandidaten:

```text
node_set_agreement = True
edge_set_agreement = True
per_index_photo_status = matched_expected_nodes
```

Kandidaten:

```text
candidate_000 / raw_index 2338804: matched_expected_nodes
candidate_001 / raw_index 2338805: matched_expected_nodes
candidate_002 / raw_index 2839553: matched_expected_nodes
candidate_003 / raw_index 18575893: matched_expected_nodes
candidate_004 / raw_index 26157529: matched_expected_nodes
candidate_005 / raw_index 26157530: matched_expected_nodes
candidate_006 / raw_index 26161006: matched_expected_nodes
candidate_007 / raw_index 26167866: matched_expected_nodes
candidate_008 / raw_index 26187175: matched_expected_nodes
candidate_009 / raw_index 26187327: matched_expected_nodes
candidate_010 / raw_index 26328307: matched_expected_nodes
```

Besondere Targets:

```text
candidate_005_status = matched_expected_nodes
candidate_005_node_set_agreement = True
candidate_005_edge_set_agreement = True
candidate_005_coarse_signature_degeneracy_stress_case = true
```

Positive Control:

```text
candidate_008_status = matched_expected_nodes
candidate_008_node_set_agreement = True
candidate_008_edge_set_agreement = True
```

Aber weiterhin:

```text
full_fu02g4c_replay_certification = False
```

---

## 6. FU02g5g2 — Interpretation

FU02g5g2 schließt eine wichtige Lücke aus FU02g5g:

```text
candidate_005 hat jetzt eine direkte per-index Foto-Karteikarte
im aktuellen scaffold/FU02g4c-style Replay.
```

Vor g5g2 war candidate_005 nur:

```text
in passendem FU02g4c-Logfenster
aber ohne eigene Karteikarte
```

Nach g5g2 ist candidate_005:

```text
per-index reproduzierbar im aktuellen Scaffold-Replay
node_set_agreement = True
edge_set_agreement = True
```

Trotzdem bleibt candidate_005:

```text
exact_match = False
near_distance = 0
uncolored_isomorphic_to_reference = False
face_type_preserving_isomorphic_to_reference = False
mapping_count = 0
role_transport_allowed_under_g5c = False
```

Das heißt:

```text
candidate_005 ist reproduzierbar,
aber kein exact candidate,
kein isomorpher Referenz-Twin,
und nicht role-transport-berechtigt.
```

Interne Kurzform:

```text
candidate_005 ist jetzt direkt fotografiert,
aber bleibt ein Problemklunker:
grob ähnlich, nicht topologisch gleich.
```

---

## 7. Isomorphie-Recheck

FU02g5g2 bestätigte den FU02g5e2-Isomorphie-Befund vollständig:

```text
candidate_000–candidate_007, candidate_009, candidate_010:
uncolored_isomorphic_to_reference = False
face_type_preserving_isomorphic_to_reference = False
mapping_count = 0
```

Known exact positive control:

```text
candidate_008:
uncolored_isomorphic_to_reference = True
face_type_preserving_isomorphic_to_reference = True
mapping_count = 1
```

Alle g5e2-Vergleichswerte stimmen:

```text
g5e2_agrees_uncolored = True
g5e2_agrees_face_type_preserving = True
g5e2_agrees_mapping_count = True
```

---

## 8. Was jetzt erreicht ist

Wir haben vier sauber getrennte Evidenzebenen:

### Ebene 1 — Scaffold-localized candidates

```text
g5e1 lokalisiert 11 Near-Kandidaten im scaffold mode.
```

### Ebene 2 — Role-transport classification

```text
g5e2 zeigt:
Nur candidate_008 ist face-type-preserving isomorphic und role-transport-berechtigt.
Die anderen 10 bleiben nicht-isomorphe Near-Decoys.
```

### Ebene 3 — Candidate_005 Deep Inspection

```text
g5f zeigt:
candidate_005 ist ein coarse-signature degeneracy case.
near_distance = 0 bedeutet nicht exact/isomorph.
```

### Ebene 4 — Per-index photo agreement

```text
g5g2 zeigt:
Alle 11 Kandidaten sind im aktuellen scaffold/FU02g4c-style per-index Replay
mit Node- und Edge-Set-Agreement reproduzierbar.
```

Offen bleibt:

```text
full FU02g4c raw-order replay certification
```

---

## 9. Was weiterhin nicht erreicht ist

Trotz des starken g5g2-Audit-Fortschritts gilt weiterhin:

```text
full_fu02g4c_replay_certification = False
```

Grund:

```text
Der exakt originale FU02g4c-Enumerator und das vollständige ursprüngliche Input-Bundle
wurden nicht als identisch wiederverwendet/zertifiziert.
```

Also nicht behaupten:

```text
Alle g5e1/g5e2/g5f/g5g2-Kandidaten sind vollständig FU02g4c raw-order certified.
```

Besser:

```text
Alle Kandidaten sind im aktuellen scaffold/FU02g4c-style per-index Replay reproduzierbar.
```

---

## 10. Aktueller Claim-Stand

### Erlaubt

```text
BMS-FU02g5g2 reproduces all 11 scaffold-localized near candidates by per-index
photo in the current deterministic scaffold/FU02g4c-style enumeration.
```

Erlaubt:

```text
For all configured candidates, node_set_agreement=True and edge_set_agreement=True
relative to the FU02g5e1 candidate table.
```

Erlaubt:

```text
candidate_005 is directly reproduced as a per-index photo but remains non-exact,
non-isomorphic, and non-role-transportable under the FU02g5c automorphy-only rule.
```

Erlaubt:

```text
candidate_008 reproduces as the positive control and remains the only candidate
that is uncolored and face-type-preserving isomorphic to the FU02f1 reference.
```

### Nicht erlaubt

```text
FU02g5g2 fully certifies FU02g4c raw-order replay.
candidate_005 is an exact candidate.
candidate_005 is role-transport eligible.
The 10 non-exact candidates are globally irrelevant.
The result proves global rarity, global uniqueness, physical emergence, spacetime emergence,
or Lorentz compatibility.
```

---

## 11. Wissenschaftliche Lesart

Die FU02g5c–g5g2-Kette ist methodisch deutlich gehärtet:

```text
Der Spiegelklunker hält.

Die Near-Decoys sind nicht verschwunden, sondern sauber klassifiziert.

candidate_005 erklärt, warum grobe Near-Distanz nicht mit Identität verwechselt werden darf.

g5g2 zeigt, dass die Kandidaten im aktuellen per-index Replay stabil reproduzierbar sind.

Der volle FU02g4c-Amtsstempel bleibt bewusst offen.
```

Interne Kurzform:

```text
Jetzt hat jeder Near-Klunker eine eigene Karteikarte im aktuellen Replay.

candidate_005:
nicht mehr nur Regalbereich,
sondern direkt fotografierter Problemklunker.

candidate_008:
Spiegelklunker reproduziert als Positivkontrolle.

Aber:
Der Amtsstempel „voll FU02g4c-certified“ bleibt noch aus.
```

---

## 12. Nächster sinnvoller Schritt

Es gibt zwei sinnvolle Anschlusswege:

### Option A — Result-Synthesis / Red-Team-ready Abschluss

```text
BMS-FU02g5g3 — Certification Synthesis / Red-Team Update
```

Ziel:

```text
Die Kette g5c–g5g2 als methodischen Abschlussblock dokumentieren
und die Red-Teams erneut nur auf die verbleibende FU02g4c-Replay-Boundary prüfen lassen.
```

### Option B — Original-Enumerator Recovery

```text
BMS-FU02g5i — Original FU02g4c Enumerator/Input Bundle Recovery
```

Ziel:

```text
Vollen FU02g4c-Amtsstempel vorbereiten:
exakter Original-Enumerator
exaktes Input-Bundle
isolierte Output-Surface
dokumentierte Order-Garantie
```

Empfehlung:

```text
Erst g5g3 als Synthese schreiben,
dann entscheiden, ob der Aufwand für g5i jetzt gerechtfertigt ist
oder ob FU03a externe Graphkontrollen methodisch wertvoller sind.
```

---

## 13. Abschlussformulierung

Eine sichere externe Formulierung wäre:

```text
A narrow per-index replay/photo control reproduced all scaffold-localized near
candidates in the current deterministic scaffold/FU02g4c-style enumeration, with
both node-set and induced-edge-set agreement. The known exact candidate remains
the only face-type-preserving isomorphic reference twin and the only candidate
eligible for automorphy-only role transport. Candidate_005 is now directly
reproduced as a coarse-signature degeneracy stress case: it has near_distance=0
but is neither exact nor isomorphic. Full FU02g4c raw-order replay certification
remains open because the original enumerator and full original input bundle were
not certified as identically reused.
```

---

## 14. Interner Abschluss

```text
Die Klunker sind jetzt einzeln fotografiert.

Der Spiegelklunker hält.
candidate_005 ist aufgesägt und direkt fotografiert.
Die zehn falschen Klunker bleiben falsche Klunker — aber jetzt mit Karteikarte.
Codex hat sauber geschraubt.
Nova hält die Claim-Bremse.
Ralf entscheidet, ob wir jetzt den Amtsstempel jagen oder ins nächste Testfeld gehen.
```
