# QSB-BRIDGE-SYNTH-01D Result Note

## Befund

QSB-BRIDGE-SYNTH-01D erstellt eine erste Source-Column-Binding- und Gate-Table-Stufe aus den 01A-, 01B- und 01C-Artefakten sowie den dort referenzierten vorhandenen Quellartefakten.

Neu angelegt wurden:

```text
data/qsb_bridge_synth_01d_c60_candidate_gate_table.csv
data/qsb_bridge_synth_01d_replay_certification_ladder.csv
data/qsb_bridge_synth_01d_null_family_normalization_table.csv
data/qsb_bridge_synth_01d_proxy_marker_source_binding.csv
docs/QSB_BRIDGE_SYNTH_01D_C60_CANDIDATE_GATE_TABLE_FIELD_LIST.md
docs/QSB_BRIDGE_SYNTH_01D_REPLAY_CERTIFICATION_LADDER_FIELD_LIST.md
docs/QSB_BRIDGE_SYNTH_01D_NULL_FAMILY_NORMALIZATION_TABLE_FIELD_LIST.md
docs/QSB_BRIDGE_SYNTH_01D_PROXY_MARKER_SOURCE_BINDING_FIELD_LIST.md
docs/QSB_BRIDGE_SYNTH_01D_RESULT_NOTE.md
```

Es wurden keine neuen numerischen Tests ausgefuehrt. Es wurden keine bestehenden Dateien, keine bestehenden Result Notes und keine `runs/`-Artefakte veraendert.

## Interpretation

01D macht vier Bereiche pruefbarer:

```text
1. C60-Kandidatengates:
   near_distance, exact_match, Isomorphie, Mapping Count, Role Transport und
   G5G2 Node/Edge Agreement werden pro Kandidat getrennt.

2. Replay-Zertifizierungsleiter:
   logged-window support, G5G partial/not-certified Status, G5G2 per-index
   photo agreement und Stage3A DRY_RUN_READY werden nicht vermischt.

3. Nullfamilien-Normalisierung:
   BMC14/BMC14d/BMC14e/BMC15h/BMS-IS01/BMS-IS01b/BMS-ST01 werden als
   family-bounded controls gefuehrt.

4. Proxy-Marker-Bindung:
   Source-bound Marker werden von Result-Note-bound, concept-only und gap-only
   Markern getrennt.
```

Die wichtigste praktische Trennung ist: Gate-Status, Replay-Status und Proxy-/Nullfamilien-Status sind unterschiedliche Evidenztypen.

## Hypothese

Die Arbeits-Hypothese fuer spaetere Synthese lautet:

```text
Cross-Test-Muster koennen nur dann belastbar gelesen werden, wenn Kandidaten-Gates,
Replay-Zertifizierung, Nullfamilien und Proxy-Marker jeweils eigene
Source-Binding-Tabellen behalten.
```

01D liefert diese erste Trennung. Sie ist noch keine physikalische Synthese.

## Offene Luecke

Offen bleiben:

```text
1. Einige preserved/broken variables in Nullfamilien sind aus Result Notes
   gebunden, nicht direkt aus CSV-Spalten.
2. BMS-IS01b ist in 01D nur result-note-bound; eine konkrete Summary-CSV wurde
   nicht als 01A-Quelle gebunden.
3. geometry_proxy_score bleibt ein Umbrella-Marker; konkrete Komponenten sind
   teils source-bound, teils nur result-note-bound.
4. weighted_clustering, lambda2_abs und chi_alpha bleiben gap-only.
5. rho_pos und rho_neg bleiben concept-only, solange keine konkrete Quellspalte
   gebunden ist.
6. G5G2 node/edge agreement ist Scaffold-/Per-Index-Unterstuetzung, aber keine
   Full Raw-Order Replay Certification.
```

## Claim Boundary

QSB-BRIDGE-SYNTH-01D beweist keine QSB-These.

Der Block beweist insbesondere nicht:

```text
physikalische Emergenz
Raumzeit-Emergenz
globale Nicht-Generizitaet
metrische Rekonstruktion
kausale Struktur
vollstaendige Raw-Order-Replay-Garantie
direkte de-Broglie-Bestaetigung
```

Besondere Schutzgrenzen:

```text
C60 ist Pruefstand, nicht Ziel.
near_distance=0 ist nicht Identitaet oder Isomorphie.
role_transport_allowed folgt nur aus expliziten Mapping-/Isomorphie-Gates.
Stage3A DRY_RUN_READY ist kein Full Replay.
G5G2 per-index photo agreement ist keine Full Raw-Order Certification.
Geometry Proxy bleibt Proxy.
Core/Envelope-Containment bleibt Graphverhalten.
Isotopen-/Strukturinformationsachsen bleiben structured-null diagnostics,
nicht direkte de-Broglie-Bestaetigung.
```

## Nächster Schritt

Der naechste sinnvolle Schritt ist eine 01E-Readout-Stufe ohne neue Numerik:

```text
1. Kandidaten-Gates und Replay-Leiter gemeinsam lesen, ohne sie zu verschmelzen.
2. Gap-only Marker entweder an konkrete Spalten binden oder aus der evidenztragenden
   Synthese ausklammern.
3. Nullfamilien preserved/broken variables nur dort als source-bound markieren,
   wo sie direkt aus Tabellen oder klaren Result-Note-Abschnitten ableitbar sind.
4. Geometry-Proxy-Komponenten einzeln ausweisen statt geometry_proxy_score als
   Einzelwert zu behandeln.
```
