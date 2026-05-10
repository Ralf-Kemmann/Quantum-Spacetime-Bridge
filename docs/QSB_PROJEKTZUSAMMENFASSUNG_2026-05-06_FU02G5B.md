# QSB Projektzusammenfassung — Stand 2026-05-06

## Arbeitsmodus

QSB-Ankerverhalten ist aktiv. Gearbeitet wird repo-orientiert, transparent und defensiv: keine versteckten Rechnungen, kein hidden code, keine Overclaims. Ergebnisse werden getrennt nach Befund, Interpretation, Hypothese, offener Lücke und Claim Boundary gelesen.

Standard-Repo:

```bash
/home/ralf-kemmann/Downloads/deBroglie_Kaster_Theorie/quantum-spacetime-bridge
```

Repo-Struktur:

```text
docs/     Spezifikationen, Result Notes, Feldlisten
data/     Configs, Inputs, CSV/JSON/YAML-Artefakte
scripts/  ausführbare Skripte
runs/     Run Outputs und Diagnostik
```

## Wissenschaftlicher Kontext

Im aktuellen Block untersuchen wir role-colored Carrier-Patches im C60-Face-Graphen. Der Graph ist der Dualgraph der C60-Flächen: jede C60-Fläche ist ein Knoten, gemeinsame Kanten zwischen Flächen sind Graphkanten. Hexagonflächen haben im vollständigen Dualgraphen Grad 6, Pentagonflächen Grad 5.

Die zentrale Frage ist methodisch begrenzt:

```text
Ist die FU02f1-C60-Carrier-Region nur ein generischer connected patch,
oder trägt sie eine ungewöhnlich eingeschränkte role-colored Struktur-Signatur
unter connected-patch-, Automorphie- und Rollenzuweisungskontrollen?
```

## FU02g4c / FU02g4d Abschlussstand

Der bisherige Abschlussbefund bleibt:

```text
exact match found
exact match localized
exact match photographed
exact match automorphic to reference
```

Primary-audited coverage:

```text
0 → 26,784,196 connected 17er-Patches
```

Aggregate raw counts:

```text
raw_carrier_signature_exact_match_count = 42
raw_carrier_signature_near_match_count  = 272
raw_role_colored_signature_exact_match_count = 1
raw_role_colored_signature_near_match_count  = 11
```

Der einzige raw role-colored exact match wurde lokalisiert bei:

```text
skip_first_raw_patches = 26,187,175
```

Der fotografierte Patch ist:

```text
H_01;H_02;H_03;H_05;H_06;H_07;H_08;H_09;H_10;H_15;H_16;H_17;P_00;P_01;P_02;P_03;P_07
```

Automorphie-Ergebnis:

```json
{
  "networkx_available": true,
  "role_colored_patch_automorphic_to_reference": true,
  "uncolored_patch_automorphic_to_reference": true
}
```

Saubere Lesart:

```text
Der einzige bisher beobachtete raw role-colored exact match in der primary-audited Coverage
wurde lokalisiert, fotografiert und als automorph zur FU02f1-Referenz identifiziert.
```

Interne Kurzform:

```text
Der Klunker war kein fremder Kristall.
Es war unser eigener Klunker im Spiegelkabinett.
```

Nicht behaupten:

```text
Wir haben einen zweiten unabhängigen role-colored Klunker gefunden.
```

## FU02g5 — Role-Assignment Sensitivity Controls

FU02g5 wurde als nächster Block aufgesetzt, um zu prüfen, ob die role-colored exact/near Befunde robust gegen Varianten der Rollenzuweisung sind oder wesentlich von der v0 type-preferred Rollenzuweisung abhängen.

Erzeugte/benutzte Artefakte:

```text
docs/BMS_FU02G5_ROLE_ASSIGNMENT_SENSITIVITY_SPEC.md
docs/BMS_FU02G5_ROLE_ASSIGNMENT_SENSITIVITY_FIELD_LIST.md
data/bms_fu02g5_role_assignment_sensitivity_config.yaml
scripts/run_bms_fu02g5_role_assignment_sensitivity.py
```

Technische Reparaturen am Runner:

```text
1. full_face_graph_edges_csv wurde auf den reparierten FU02d1-Face-Adjacency-Graph gesetzt.
2. read_edge_csv liest jetzt korrekt face_a / face_b als Kantenenden.
3. Der C60-Face-Graph wurde geprüft: 32 Knoten, 90 Kanten, zusammenhängend.
4. Eine falsche Frontier-Pruning-Regel im connected_k_subgraphs-Generator wurde entfernt.
5. partial_run-Semantik wurde korrigiert.
6. stop_reason wurde in das CSV-Readout aufgenommen.
```

Der ursprüngliche Fehler war nicht physikalisch oder numerisch, sondern maschinenraumseitig:

```text
Die Datei war korrekt.
Der Parser las zunächst edge_key / face_a statt face_a / face_b.
Danach killte eine zu aggressive Frontier-Pruning-Regel alle k=17-Patches.
```

## FU02g5 Smoke-Test

Direkter Vergleich:

```text
FU02f1 reference carrier
vs.
lokalisierter FU02g4c automorpher exact patch
```

Geprüfte Varianten:

```text
v0_type_preferred
uncolored_carrier_only
face_type_only
swap_core_boundary
core_erased
boundary_erased
```

Befund:

```text
localized_candidate_exact_match = True
localized_candidate_near_distance = 0
localized_candidate_near_match = True
```

für alle sechs Varianten.

Saubere Interpretation:

```text
Innerhalb dieses FU02g5-Smoke-Tests ist die Übereinstimmung zwischen FU02f1-Referenz
und lokalisiertem automorphen FU02g4c-Kandidaten nicht sensitiv gegenüber den sechs
getesteten Rollenzuweisungsvarianten.
```

Claim Boundary:

```text
Das ist kein globaler Rolleninvarianzbeweis und keine physikalische Dynamikaussage.
Es ist ein direkter Referenz-vs-Kandidat-Test im C60-Face-Graph-Kontrollraum.
```

## FU02g5b — First-500 Enumeration Smoke

Ein kleines deterministisches Enumeration-Fenster wurde eingerichtet:

```text
data/bms_fu02g5b_first500_enumeration_smoke_config.yaml
runs/BMS-FU02g5b/first500_enumeration_smoke/
```

Konfiguration:

```text
enumerate_connected_patches = true
skip_first_connected_patches = 0
max_connected_patches_this_run = 500
```

Finaler sauberer Readout:

```text
enumerated_patch_count = 500
enumerated_exact_match_count = 0
enumerated_near_match_count = 0
partial_run = False
stop_reason = max_count_reached
```

für alle sechs Varianten.

Warnings treten bei Varianten auf, die für beliebige enumerierte Patches eine noch nicht definierte Patch-Level-Role-Transport-Regel benötigen:

```text
v0_type_preferred
swap_core_boundary
core_erased
boundary_erased
```

Direkt am saubersten interpretierbar sind:

```text
uncolored_carrier_only
face_type_only
```

Dort gilt:

```text
500 Patches
0 exact
0 near
0 warnings
stop_reason = max_count_reached
```

Saubere Lesart:

```text
FU02g5b bestätigt, dass der reparierte Scaffold-Enumerator kleine deterministische
connected-17-Face-Patchfenster auf dem C60-Face-Graphen verarbeitet. In den ersten
500 enumerierten Patches wurden unter den direkt interpretierbaren Varianten keine
exact oder near matches gefunden.
```

Nicht behaupten:

```text
globale Einzigartigkeit
globale Seltenheit
Reproduktion des FU02g4c-Indexraums
```

Wichtig:

```text
FU02g4c raw_index 26,187,175 ist nicht automatisch FU02g5-Scaffold raw_index 26,187,175.
```

## Patch-Adjazenzliste

Für den lokalisierten FU02g4c-Patch wurde eine echte Nachbarschaftsliste aus dem reparierten C60-Face-Graphen gezogen.

Output:

```text
runs/BMS-FU02g5b/first500_enumeration_smoke/exact_patch_adjacency_list.md
runs/BMS-FU02g5b/first500_enumeration_smoke/exact_patch_adjacency_list.csv
```

Patch nodes:

```text
H_01;H_02;H_03;H_05;H_06;H_07;H_08;H_09;H_10;H_15;H_16;H_17;P_00;P_01;P_02;P_03;P_07
```

Interne Patch-Nachbarschaften:

```text
H_01: H_02, H_05, H_06, P_00, P_01, P_02
H_02: H_01, H_03, H_08, P_00, P_02, P_03
H_03: H_02, H_10, P_00, P_03
H_05: H_01, P_00, P_01
H_06: H_01, H_07, H_15, P_01, P_02
H_07: H_06, H_08, H_16, P_02, P_07
H_08: H_02, H_07, H_09, P_02, P_03, P_07
H_09: H_08, H_10, H_17, P_03, P_07
H_10: H_03, H_09, P_03
H_15: H_06, P_01
H_16: H_07, H_17, P_07
H_17: H_09, H_16, P_07
P_00: H_01, H_02, H_03, H_05
P_01: H_01, H_05, H_06, H_15
P_02: H_01, H_02, H_06, H_07, H_08
P_03: H_02, H_03, H_08, H_09, H_10
P_07: H_07, H_08, H_09, H_16, H_17
```

Diese Liste ist jetzt die belastbare Strukturgrundlage für eine schematische Dualgraph-Grafik. Eine Bild-KI soll künftig nicht mehr frei aus der Node-Liste halluzinieren, sondern diese Adjazenz respektieren.

## Bild-/Visualisierungslesart

Zwei Bildtypen wurden unterschieden:

```text
PM-/Cover-Bild:
ästhetisch stark, aber fachlich riskant, wenn es eine exakte 3D-Einbettung suggeriert.

Dualgraph-Schema:
nüchterner, aber näher an der Theorie und am tatsächlichen Face-Adjacency-Graphen.
```

Kurz:

```text
Bild 1 ist der Trailer.
Bild 2 ist das Laborbuch.
```

Für Dokumentation und Result Notes zählt das Laborbuch. Eine finale Visualisierung sollte daher als schematischer Dualgraph geführt werden, optional mit gestrichelten Außenkanten für Nachbarn außerhalb des Patches.

## Aktueller Claim-Stand

Erlaubt:

```text
Within the primary-audited connected-patch enumeration, the only observed role-colored exact match was localized to a single patch and identified as automorphic to the FU02f1 reference carrier.
```

Erlaubt:

```text
FU02g5 confirms at scaffold/smoke-test level that the localized FU02g4c automorphic exact patch remains signature-identical to the FU02f1 reference carrier under all configured role-assignment variants.
```

Erlaubt:

```text
FU02g5b verifies that the patched scaffold enumerator processes small deterministic connected-17-face patch windows on the repaired C60 face graph. In the first 500 enumerated patches, no exact or near matches were observed under the directly interpretable uncolored-carrier and face-type-only variants.
```

Nicht erlaubt:

```text
physikalische Emergenz gezeigt
globale Einzigartigkeit bewiesen
zweiter unabhängiger Klunker gefunden
C60-Spezifität belegt
Role-colored Seltenheit global bewiesen
```

## Offene Lücken

```text
1. Patch-Level-Role-Transport für mixed_core / pentagon_boundary bei beliebigen enumerierten Patches.
2. Near-exact role-colored Decoys außerhalb der Automorphieklasse separat prüfen.
3. FU02g5-Indexraum und FU02g4c-Indexraum sauber kalibrieren, falls der bekannte Patch im Scaffold gesucht werden soll.
4. Größere deterministische FU02g5b-Fenster nach dem First-500-Smoke-Test.
5. Externe Fullerene-/Planar-/Sphären-Graphkontrollen als FU03a.
6. Keine physikalische Dynamik- oder Emergenzaussage aus diesen kombinatorischen Kontrollen ableiten.
```

## Nächster sinnvoller Schritt

Empfohlen als nächster technischer Block:

```text
BMS-FU02g5c — Role-Transport Rule Specification
```

Ziel:

```text
Eine explizite, defensive Regel definieren, wie mixed_core / pentagon_boundary Rollen
für beliebige connected 17er-Patches transportiert oder bewusst nicht transportiert werden.
```

Alternativ als kleinerer Direktblock:

```text
BMS-FU02g5b-next — larger deterministic windows
```

mit z. B.:

```text
skip_first_connected_patches = 0
max_connected_patches_this_run = 5000
```

oder mehreren kleinen Fenstern, bevor ein größerer Auditlauf gerechtfertigt wird.

## Tagesfazit

```text
FU02g4c/g4d:
Klunker lokalisiert und als Spiegelklunker identifiziert.

FU02g5:
Rollenbrille stabil im direkten Referenz-vs-Kandidat-Test.

FU02g5b:
Scaffold-Enumerator repariert, First-500-Fenster sauber verarbeitet, keine exact/near Treffer.

Patch-Grafik:
Node-Liste reicht nicht; echte Adjazenzliste liegt jetzt vor.

Claim:
stark genug für methodischen Fortschritt,
nicht stark genug für globale oder physikalische Großbehauptungen.
```

Interner Abschluss:

```text
Klunker fotografiert.
Kanten gezählt.
Rollenbrille geprüft.
Staubsauger repariert.
Fahrtenbuch sauber.
Feierabend verdient.
```
