# QSB-BRIDGE-SYNTH-03A Result Note

## Befund

QSB-BRIDGE-SYNTH-03A erstellt einen ersten begrenzten Nachbindungs-Lauf fuer die offene 02A/02E-Luecke:

```text
BMC12c/BMC12e/BMC12f per-variant threshold and arm rows
```

Neu angelegt wurden:

```text
data/qsb_bridge_synth_03a_bmc12_per_variant_binding.csv
docs/QSB_BRIDGE_SYNTH_03A_BMC12_PER_VARIANT_BINDING_FIELD_LIST.md
docs/QSB_BRIDGE_SYNTH_03A_RESULT_NOTE.md
```

Es wurden keine neuen numerischen Tests ausgefuehrt. Es wurden keine bestehenden Dateien, keine bestehenden Result Notes und keine `runs/`-Artefakte veraendert.

Die Binding-Tabelle enthaelt 19 Zeilen. Sie bindet vorhandene BMC12-, BMC12b-, BMC12c-, BMC12e- und BMC12f-Artefakte an den 02A/02E-Readout:

```text
feature/backbone sensitivity
```

## Interpretation

03A macht den Feature-/Backbone-Sensitivitaetsreadout pruefbarer, indem er vorhandene Quellen nach Block, Variant Family, Threshold/Control Setting, Arm/Comparison, Markern und Bound Source Fields trennt.

Die wichtigste methodische Lesart ist:

```text
BMC12 zeigt fixed-tau leave-one-out Sensitivitaet, ist aber durch spaetere
Reconciliation und Densification-Warnungen begrenzt.

BMC12b bindet matched edge-count overlap, jaccard und cutoff_weight als
graph-size-controlled Vergleichsbasis.

BMC12c bindet die BMC09d-artige backbone-aware Arm-Entscheidung auf
variant_name, decision_label, dominant_arm und arrangement_signal Felder.

BMC12e bindet die Edgecount-Regime N=70,75,81,87,92 und zeigt, dass der
N=81 Feature-Drop-Profile lokal und graph-size-sensitive ist.

BMC12f bindet die Entscheidungsschwellen- und Dominance-Gap-Sensitivitaet
aus vorhandenen BMC12e-Signalen. N=81 baseline ist innerhalb des getesteten
Grid robust; Feature-Drop-Profile bleiben gemischt oder instabil.
```

03A erzeugt damit keine neue Numerik, sondern eine Source-Binding-Tabelle fuer bestehende numerische Artefakte.

## Hypothese

Die Arbeits-Hypothese fuer 03A lautet:

```text
Der Feature-/Backbone-Sensitivitaetsreadout wird belastbarer dokumentierbar,
wenn fixed-tau, matched edge-count, backbone-aware variants, edgecount regimes
und threshold-grid Reclassification getrennt gebunden werden.
```

Diese Hypothese ist methodisch. Sie behauptet keine physikalische Bruecke, keine physikalische Emergenz und keine Raumzeit-Emergenz.

## Offene Lücke

Offen bleiben:

```text
1. BMC12 fixed-tau Zeilen bleiben durch Densification und Feature-Source-Reconciliation begrenzt.
2. BMC12b hat overlap_fraction, jaccard und cutoff_weight, aber noch keine originalen Backbone-Arm-Entscheidungen.
3. BMC12c bindet BMC09d-artige top-k/top-alpha Varianten, aber nicht alle moeglichen Backbone-Definitionen.
4. BMC12e zeigt Edgecount-Regime-Abhaengigkeit; daraus folgt keine globale Stabilitaet.
5. BMC12f reklassifiziert vorhandene BMC12e arrangement signals; es ist kein neuer Graph- oder Shuffle-Run.
6. Feature-Drop-Profile bleiben lokal, threshold-sensitive und nicht als stabile Feature-Role-Hierarchie zu lesen.
7. Einige kompakte Result-Note-Bindungen sind bewusst mit bound_source_field=not_extracted markiert, wenn die konkrete Spalte nicht in dieser Zeile sicher extrahiert wurde.
```

## Claim Boundary

QSB-BRIDGE-SYNTH-03A beweist keine QSB-These.

Der Block beweist insbesondere nicht:

```text
physikalische Emergenz
Raumzeit-Emergenz
globale Nicht-Generizitaet
metrische Rekonstruktion
kausale Struktur
vollstaendige Raw-Order-Replay-Garantie
```

Besondere Schutzgrenzen:

```text
Feature/backbone sensitivity ist eine methodische Sensitivitaetsachse.
arrangement_signal ist kein physikalischer Primitive.
Backbone/off-backbone localization ist Graph-/Artefaktverhalten, kein physikalischer Brueckenbeweis.
Threshold- oder arm-spezifische Stabilitaet beweist keine Raumzeit-Emergenz.
Geometry Proxy bleibt Proxy.
Gap-only Marker tragen keine Evidenzlast.
Die integrierte Brueckenkarte bleibt methodisch, kein physikalischer Beweis.
```

## Nächster Schritt

Der naechste sinnvolle Schritt ist eine kleine, auditierbare Weiterbindung:

```text
1. Falls benoetigt, BMC12c und BMC12e per-row variant summaries voll expandieren.
2. BMC12f stability_summary fuer alle threshold-grid Aggregate maschinenlesbar in eine spaetere Detailbindung ueberfuehren.
3. Backbone-Definition-Methodenabhaengigkeit separat behandeln, statt 03A zu ueberdehnen.
4. Feature/backbone sensitivity weiter als methodische Sensitivitaetsachse dokumentieren.
```
