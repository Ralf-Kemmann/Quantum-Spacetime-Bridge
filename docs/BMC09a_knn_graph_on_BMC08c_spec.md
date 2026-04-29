# BMC-09a – Spezifikation: k-NN-Graph auf BMC-08c-Basis

## Status
Spezifikationsschritt vor Implementierung.

## Zweck
BMC-09a prüft, ob ein **lokaler k-NN-Graph** auf Basis des BMC-08c-Realdatensatzes
ein interpretierbareres Strukturbild liefert als der bisher verwendete vollständige Distanzgraph.

Die Kernfrage lautet:

**Entsteht ein robusteres Backbone-/Off-Backbone-/Coupling-Bild, wenn nur lokale Nachbarschaften statt aller Paarbeziehungen im Graphen erhalten bleiben?**

BMC-09a ist damit der erste gezielte Schritt
- weg vom vollständigen Ähnlichkeitsgraphen
- hin zu einer **strukturbetonten Graphkonstruktion**

## Ausgangspunkt

### Letzter belastbarer Befund
Die BMC-08-Serie ergab:

- BMC-08a: scheinbar robuster Off-Backbone-Befund
- BMC-08b: Effekt kollabiert nach Entfernung der Ring-Spiegelsymmetrie
- BMC-08c: auch mit sign-sensitivem Ring nur `still_weak_or_mixed`

### Projektinterne Lesart
Die bisherige Graphkonstruktion
- vollständiger Graph
- Gewicht aus globaler Distanzähnlichkeit

ist wahrscheinlich zu stark glättend und damit anfällig dafür,
Heterogenität statt lokaler Struktur abzubilden.

### Offene Kernfrage
Kann ein **lokaler Nachbarschaftsgraph** auf derselben Knoten- und Featurebasis
Struktur freilegen, die im Vollgraphen überdeckt wird?

## Prinzip

### Konstant zu halten
- dieselbe Knotenbasis wie BMC-08c
- dieselbe offene Featuretable-Logik
- dieselben Shells
- dieselben Backbone-Basisvarianten
- dieselben Readouts
- dieselbe defensive Entscheidungslogik

### Kontrolliert zu ändern
Nur die **Graphbildungsregel**.

## BMC-09a Grundidee

Ausgehend von der bestehenden BMC-08c-Featuretable wird
nicht mehr jede Knotenpaarung als Kante exportiert.

Stattdessen gilt:

Für jeden Knoten bleiben nur die **k nächsten Nachbarn**
gemessen in derselben offenen Featuredistanz wie bisher erhalten.

## Graphregel

### Distanzbasis
Wie in BMC-08a/BMC-08c:

1. offene numerische Featurebasis
2. z-Standardisierung im Build-Script
3. euklidische Distanz im standardisierten Featurevektor

### k-NN-Regel
Für jeden Knoten `i`:
- berechne die Distanzen zu allen anderen Knoten
- sortiere aufsteigend
- behalte nur die `k` nächsten Nachbarn

### Kantenbildung
BMC-09a verwendet für Version 1 einen **symmetrisierten k-NN-Graphen**:

Eine Kante `(i,j)` wird gesetzt, wenn
- `j` unter den `k` nächsten Nachbarn von `i` liegt
**oder**
- `i` unter den `k` nächsten Nachbarn von `j` liegt

### Gewicht
Das Gewicht bleibt offen kompatibel zum bisherigen Schema:

`weight(i,j) = 1 / (1 + d(i,j))`

mit `d(i,j)` als euklidischer Distanz im z-standardisierten Featurevektor.

## Warum symmetrisiert?
- einfacher lesbar als gerichteter k-NN
- kompatibler mit der bisherigen ungerichteten BMC-08/BMC-07-Logik
- vermeidet unnötige Zusatzkomplexität im ersten k-NN-Test

## Priorisierte k-Werte

### Startleiter
- `k = 2`
- `k = 3`
- `k = 4`

## Begründung
- klein genug, um echte Lokalität zu erzwingen
- groß genug, damit der Graph nicht sofort zerfällt
- gute erste Sensitivitätsleiter

## Erwartete Strukturfragen

### Q1 – Entglättung
Wird das im Vollgraphen schwache oder gemischte Bild unter lokaler Graphbildung schärfer?

### Q2 – Coupling
Entsteht im k-NN-Graphen eine stärkere Rolle lokaler Coupling-Zonen?

### Q3 – Backbone
Wird der Backbone unter lokaler Struktur stärker oder schwächer?

### Q4 – Graphzerfall
Wie stark zerfällt der Graph bei kleinen `k` in Komponenten?

## Zusätzliche Outputgrößen

BMC-09a soll zusätzlich zu den bisherigen Variantenoutputs
explizit Graphdiagnostik mitschreiben.

### Neue Graphdiagnostikfelder
- `graph_construction_method`
- `graph_construction_parameters`
- `graph_node_count`
- `graph_edge_count`
- `connected_component_count`
- `largest_component_size`
- `mean_degree`
- `graph_density`

## Warum das wichtig ist
Ein BMC-09a-Befund ist nur interpretierbar, wenn wir gleichzeitig sehen,
ob der Graph
- sinnvoll zusammenhängt
- zu dünn wird
- oder praktisch noch fast vollständig ist

## Methodische Leitplanken

### Zulässig
- offene Distanzbasis
- offenes `k`
- symmetrisierte Nachbarschaftsregel
- keine stillen Nachkorrekturen

### Nicht zulässig
- stilles Reparieren isolierter Knoten
- ad-hoc Verbinden von Komponenten im Runner
- variantenabhängige Spezialregeln pro Familie
- readout-nahe Kantenregeln im selben ersten Schritt

## Zu erstellende Dateien

### Neu
- `scripts/build_bmc09a_knn_inputs_from_bmc08c.py`
- `data/bmc09a_knn_config.yaml`
- `data/bmc09a_realdata_config.yaml`
- `scripts/run_bmc09a_realdata_open.sh`

### Wiederverwendet
- `scripts/build_bmc08c_feature_table_from_m39x1_sign_sensitive_ring.py`
- `scripts/build_bmc08a_realdata_inputs.py` nur teilweise bzw. als Referenz
- `scripts/bmc07_backbone_variation_runner.py`

## Warum neues Build-Script?
Der bisherige BMC-08-Build erzeugt immer den vollständigen Graphen.
BMC-09a braucht daher ein eigenes Build-Script für:
- Distanzberechnung
- k-NN-Selektion
- symmetrisierte Kantenbildung
- Export der k-NN-Kantenliste

## Backbone-Varianten
Unverändert faire Basisvarianten:
- `strength_topk_6`
- `strength_topalpha_025`
- `strength_topalpha_050`

## Outputvertrag

### Zielordner
`runs/BMC-09/BMC09a_realdata_open/`

### Pflichtoutputs
- `summary.json`
- `validation.json`
- `run_metadata.json`
- `backbone_variant_summary.csv`
- `repeat_metrics.csv`
- `readout.md`

### Zusätzlich empfohlen
- `graph_build_summary.json`
- `graph_build_diagnostics.csv`

## Sanity-Checks vor dem Lauf

1. k-Wert ist positiv und kleiner als Knotenzahl
2. keine Selbstkanten
3. Gewichte sind endlich und positiv
4. Knotenbasis identisch zur BMC-08c-Featuretable
5. Graphdiagnostik wird geschrieben
6. keine stille Komponentenreparatur

## Failure Modes

### F1 – Graph zerfällt zu stark
Bei sehr kleinem `k` entstehen viele kleine Komponenten.

### F2 – Graph bleibt praktisch voll
Wenn `k` zu hoch oder die Symmetrisierung zu stark ist, bringt BMC-09a kaum neue Information.

### F3 – Ergebnis kommt nur aus Komponenteneffekten
Dann muss klar getrennt werden:
Graphzerfall vs. echte lokale Struktur.

### F4 – k wird nach Ergebnisinteresse gewählt
Nicht zulässig.
Die k-Leiter muss ex ante festgelegt sein.

## Erwartete Lesart

### Fall A – Schärferes Muster unter k-NN
Dann war der Vollgraph tatsächlich zu glättend.

### Fall B – Weiterhin weak/mixed
Dann trägt schon die zugrunde liegende Repräsentation kaum robuste Struktur.

### Fall C – Nur einzelne k-Werte zeigen Effekt
Dann liegt ein Sensitivitätsbild vor und kein robuster Strukturclaim.

## Befund
Noch keiner. Diese Datei ist reine Spezifikation.

## Interpretation
BMC-09a ist der erste echte Graphstruktur-Test nach der BMC-08-Serie.
Er verschiebt den Fokus von Featurevariation zu lokaler Nachbarschaftsstruktur.

## Hypothese
Wenn lokale Nachbarschaft statt globalem Vollgraphen physikalisch relevanter ist,
sollte BMC-09a eher interpretierbare Muster freilegen als BMC-08a bis BMC-08c.

## Offene Lücke
Noch fehlen:
- das k-NN-Build-Script
- die k-NN-Config
- die Realdaten-Run-Config
- das offene Run-Script
- danach erst der erste BMC-09a-Lauf

## Feldliste – empfohlene spätere Graphdiagnostik
- `graph_construction_method` — string — hier `symmetric_knn`.
- `graph_construction_parameters` — string — z. B. `{"k": 3}`.
- `graph_node_count` — integer — Anzahl Knoten.
- `graph_edge_count` — integer — Anzahl Kanten.
- `connected_component_count` — integer — Anzahl Zusammenhangskomponenten.
- `largest_component_size` — integer — Größe der größten Komponente.
- `mean_degree` — float — mittlerer Knotengrad.
- `graph_density` — float — Kantendichte des ungerichteten Graphen.
