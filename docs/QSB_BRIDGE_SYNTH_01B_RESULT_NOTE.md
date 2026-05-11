# QSB-BRIDGE-SYNTH-01B Result Note

## Befund

QSB-BRIDGE-SYNTH-01B erstellt eine erste kuratierte Cross-Test Pattern Matrix aus den 01A-Artefakten:

```text
data/qsb_bridge_synth_01a_existing_result_index.csv
data/qsb_bridge_synth_01a_marker_axis_map.csv
docs/QSB_BRIDGE_SYNTH_01A_RESULT_NOTE.md
```

Neu angelegt wurden:

```text
data/qsb_bridge_synth_01b_cross_test_pattern_matrix.csv
docs/QSB_BRIDGE_SYNTH_01B_CROSS_TEST_PATTERN_MATRIX_FIELD_LIST.md
docs/QSB_BRIDGE_SYNTH_01B_RESULT_NOTE.md
```

Die Matrix enthaelt acht Zeilen:

```text
feature_backbone_sensitivity
null_family_specificity_boundary
geometry_proxy_readability
core_envelope_robustness
carrier_role_transport_specificity
replay_certification_boundary
isotope_structure_information_axis
marker_extraction_gap
```

Es wurden keine neuen numerischen Tests ausgefuehrt. Es wurden keine bestehenden Result Notes, keine bestehenden Datenartefakte und keine `runs/`-Artefakte veraendert.

## Interpretation

01B verdichtet 01A zu einer Arbeitsmatrix. Die Matrix trennt unterstuetzende Bloecke, begrenzende Bloecke, Marker, bekannte Failure Modes, offene Luecken und naechste Checks.

Die wiederkehrende Arbeitslesart ist:

```text
1. Feature-/Backbone-Verhalten ist kontrolliert inventarisierbar, aber sensitiv gegen Featurequelle, Abtragung, Edge Count und Entscheidungsschwellen.
2. Nullfamilien begrenzen Spezifitaetslesarten; sie liefern keine globale Nicht-Generizitaet.
3. Geometrieproxy-Readouts sind graphische Proxy-Diagnostik und duerfen nicht als physikalische Geometrie gelesen werden.
4. Core/Envelope-Verhalten sollte getrennt gelesen werden: kompakte Core-Marker und groessere Envelope-Objekte haben unterschiedliche Sensitivitaeten.
5. C60-Carrier- und Rollentransport-Aussagen brauchen explizite Isomorphie-/Automorphie-Gates.
6. Replay-Zertifizierung ist gestuft und bleibt von vollstaendiger Raw-Order-Reproduktion getrennt.
7. Isotopen- und Strukturinformationsachsen erweitern structured-null diagnostics, bestaetigen aber keine physikalische Grundthese.
8. Mehrere Marker bleiben bis zur exakten Spaltenbindung Extraktionsluecken.
```

## Hypothese

Die 01B-Matrix formuliert eine Arbeits-Hypothese fuer spaetere Synthese:

```text
Mehrere bestehende QSB-Ergebnislinien koennen als wiederkehrende Musterfamilien
geordnet werden, wenn jede Markerklasse mit ihrer Kontrollachse und ihrer
Claim Boundary verbunden bleibt.
```

Diese Hypothese ist keine Beweisbehauptung. Sie ist ein Sortiermodell fuer spaetere, auditierbare Cross-Test Pattern Synthesis.

## Offene Luecke

Die wichtigsten offenen Luecken sind:

```text
1. Per-Variant- und Per-Candidate-Zeilen sind noch nicht in ein harmonisiertes Evidenzformat extrahiert.
2. Marker wie weighted_clustering, lambda2_abs, chi_alpha, rho_pos und rho_neg sind noch nicht belastbar an konkrete Quellspalten gebunden.
3. Nullfamilien sind noch nicht ueber BMC14, BMC15h, BMS-IS01 und BMS-ST01 hinweg normalisiert.
4. C60-Kandidaten brauchen eine explizite Gate-Tabelle fuer exact_match, near_distance, Isomorphie, Mapping Count und role_transport_allowed.
5. Replay-Zertifizierung braucht eine eigene Leiter von scaffold-only ueber partial certification bis full rerun, falls ein spaeterer Block das leisten soll.
```

## Claim Boundary

QSB-BRIDGE-SYNTH-01B beweist keine QSB-These.

Der Block beweist insbesondere nicht:

```text
physikalische Emergenz
Raumzeit-Emergenz
globale Nicht-Generizitaet
metrische Rekonstruktion
kausale Struktur
vollstaendige Raw-Order-Replay-Garantie
direkte de-Broglie-Bestaetigung durch Isotopen- oder Strukturinformationsachsen
```

Besondere Schutzgrenzen:

```text
C60 ist Pruefstand, nicht Ziel.
near_distance=0 ist nicht Identitaet oder Isomorphie.
geometry_proxy_score ist nicht physikalische Geometrie.
Core/Envelope-Containment ist Graphverhalten, nicht physische Einbettung.
Isotopen-/Strukturinformationsachsen sind structured-null diagnostics, nicht direkte de-Broglie-Bestaetigung.
```

## Naechster Schritt

Der naechste sinnvolle Schritt ist eine 01C-artige Evidence Binding Table ohne neue Numerik:

```text
1. exakte Quellspalten fuer die noch offenen Marker binden,
2. pro Matrixgruppe die relevanten 01A-Zeilen in ein einheitliches Evidenzschema ueberfuehren,
3. C60-Kandidatengates und Replay-Zertifizierungsstufen getrennt ausweisen,
4. Nullfamilien mit ihren erhaltenen und gebrochenen Variablen normalisieren.
```

Erst danach sollte eine staerkere Cross-Test-Synthese formuliert werden.
