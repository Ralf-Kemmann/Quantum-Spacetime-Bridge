# QSB-BRIDGE-SYNTH-01C Result Note

## Befund

QSB-BRIDGE-SYNTH-01C erstellt eine initiale Evidence Binding Table aus den bereits vorliegenden 01A- und 01B-Artefakten:

```text
data/qsb_bridge_synth_01a_existing_result_index.csv
data/qsb_bridge_synth_01a_marker_axis_map.csv
docs/QSB_BRIDGE_SYNTH_01A_RESULT_NOTE.md
data/qsb_bridge_synth_01b_cross_test_pattern_matrix.csv
docs/QSB_BRIDGE_SYNTH_01B_RESULT_NOTE.md
```

Neu angelegt wurden:

```text
data/qsb_bridge_synth_01c_evidence_binding_table.csv
docs/QSB_BRIDGE_SYNTH_01C_EVIDENCE_BINDING_TABLE_FIELD_LIST.md
docs/QSB_BRIDGE_SYNTH_01C_RESULT_NOTE.md
```

Die Evidence Binding Table enthaelt 32 Zeilen, jeweils vier Zeilen pro 01B-Mustergruppe:

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

Es wurden keine neuen numerischen Tests ausgefuehrt. Es wurden keine bestehenden Dateien, keine bestehenden Result Notes und keine `runs/`-Artefakte veraendert.

## Interpretation

01C ist keine neue Ergebnisanalyse, sondern eine Bindungsstufe. Der Block macht die 01B-Mustergruppen pruefbarer, indem jede Zeile an 01A-Quellen, Marker, Statusfelder oder explizite Claim Boundaries gebunden wird.

Die Tabelle trennt fuenf Rollen:

```text
support
control
limitation
boundary
gap
```

Dadurch werden unterstuetzende Evidenz, Kontrollkontext, begrenzende Resultate und offene Extraktionsluecken nicht vermischt.

## Hypothese

Die Arbeits-Hypothese aus 01B bleibt erhalten, wird aber enger gefasst:

```text
Eine spaetere Cross-Test-Synthese ist nur dann belastbar, wenn jede Mustergruppe
auf konkrete Quellartefakte, Marker, Statusfelder und Claim Boundaries
zurueckgefuehrt werden kann.
```

01C zeigt, dass eine solche Rueckbindung fuer mehrere Gruppen bereits auf Inventar- und Marker-Ebene moeglich ist. Zugleich zeigt 01C, wo noch keine konkrete Quellspalte oder Kandidatenzeile gebunden ist.

## Offene Luecke

Die wichtigsten offenen Extraktionsluecken sind:

```text
1. BMC12c/BMC12e/BMC12f brauchen noch Per-Variant-Bindung fuer Entscheidungsschwellen und Backbone-/Off-Backbone-Arme.
2. BMC14/BMC14d/BMC14e/BMC15h brauchen eine harmonisierte Nullfamilien-Tabelle mit preserved/broken variables, metric_name und interpretation_label.
3. BMC15/BMC15b/BMC15e brauchen Quellspaltenbindung fuer einzelne Proxy-Komponenten statt nur Proxy-Buendel.
4. C60-Kandidaten brauchen eine Gate-Tabelle mit candidate_id, raw_index, exact_match, near_distance, uncolored_isomorphic_to_reference, face_type_preserving_isomorphic_to_reference, mapping_count und role_transport_allowed.
5. FU02g5g/FU02g5g2 brauchen eine Replay-Leiter mit scaffold-only, partial certification und moeglichem full rerun Status.
6. weighted_clustering, lambda2_abs, chi_alpha, rho_pos und rho_neg bleiben Gap-Marker, bis konkrete Quellspalten in bereits inventorisierten Artefakten gebunden sind.
```

## Claim Boundary

QSB-BRIDGE-SYNTH-01C beweist keine QSB-These.

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

Besondere Schutzgrenzen bleiben:

```text
C60 ist Pruefstand, nicht Ziel.
near_distance=0 ist nicht Identitaet oder Isomorphie.
geometry_proxy_score ist nicht physikalische Geometrie.
Core/Envelope-Containment ist Graphverhalten, nicht physische Einbettung.
Isotopen-/Strukturinformationsachsen sind structured-null diagnostics, nicht direkte de-Broglie-Bestaetigung.
Replay-Zertifizierung bleibt gestuft und ersetzt keinen Full Raw-Order Replay, solange dieser nicht gelaufen ist.
```

## Naechster Schritt

Der naechste sinnvolle Schritt ist eine eng begrenzte 01D-Extraktion ohne neue Numerik:

```text
1. pro Evidence-Zeile konkrete Quellspalten aus bereits inventorisierten Artefakten binden,
2. Kandidaten- und Replay-Gates separat tabellieren,
3. Nullfamilien und Konstruktionstypen normalisieren,
4. Gap-Marker entweder an konkrete Spalten binden oder aus der evidenztragenden Synthese ausklammern.
```

Erst danach sollte eine staerkere Cross-Test-Synthese formuliert werden.
