# BMC-09d – Spezifikation: Threshold / Hybrid Local Graph

## Status
Spezifikationsschritt vor Implementierung.

## Zweck
BMC-09d soll das in BMC-09a und BMC-09c beobachtete Spannungsfeld
zwischen
- **zu glättendem lokalem Graphen** (symmetrischer k-NN)
und
- **zu streng fragmentierendem lokalem Graphen** (mutual-kNN)

in ein **kontrolliertes Zwischenregime** überführen.

Die Kernfrage lautet:

**Lässt sich ein lokaler Graph konstruieren, der schwache oder einseitige Nachbarschaften reduziert, ohne die Struktur wie mutual-kNN in Komponenten zu zerlegen?**

BMC-09d ist damit ausdrücklich ein **Intermediärblock**:
nicht zurück zum Vollgraphen, aber auch nicht zur maximal harten Reziprozitätsregel.

## Ausgangspunkt

### Letzter belastbarer Befund
Die BMC-09-Serie ergab bisher:

- **BMC-09a (symmetrischer k-NN)**:
  - bei `k = 3` ein erster Backbone-Hinweis
  - bei `k = 2` und `k = 4` wieder `weak_or_mixed`

- **BMC-09c (mutual-kNN)**:
  - über `k = 2, 3, 4` nur `still_weak_or_mixed`
  - starke Fragmentierung und kleine Zusammenhangskomponenten

### Projektinterne Lesart
Die Struktur scheint weder im Vollgraphen noch im mutual-kNN robust sichtbar zu werden.
Ein möglicher Backbone-Hinweis tauchte nur in einem **engen intermediären symmetrischen k-NN-Regime** auf.

### Offene Kernfrage
War der BMC-09a-Hinweis
- ein nützlicher Zwischenbereich lokaler Struktur
oder
- nur ein Effekt relativ permissiver Nachbarschaftsbildung?

## Prinzip

### Konstant zu halten
- dieselbe BMC-08c-Knoten- und Featurebasis
- dieselben Shells
- dieselben Backbone-Basisvarianten
- dieselben Readouts
- dieselbe defensive Ergebnislogik

### Kontrolliert zu ändern
Nur die **Kantenregel** des lokalen Graphen.

## BMC-09d Grundidee

BMC-09d testet zwei eng verwandte lokale Graphregeln:

### Arm D1 – Threshold Local Graph
Kanten werden nur dann gesetzt, wenn ihre offene Ähnlichkeit
einen Mindestwert überschreitet:

`weight(i,j) >= tau`

### Arm D2 – Hybrid Local Graph
Ein Knoten behält seine `k` nächsten Nachbarn,
aber nur wenn deren Gewicht zusätzlich über einer Mindestschwelle liegt:

`j in kNN(i)` **und** `weight(i,j) >= tau`

Für Version 1 wird die Kantenbildung wieder **symmetrisiert**,
damit die resultierenden Graphen ungerichtet bleiben.

## Warum genau diese beiden Arme?
Sie sind ein natürlicher Zwischenraum zwischen:

- **BMC-09a**: lokale Nähe reicht bereits aus
- **BMC-09c**: nur gegenseitige Nähe reicht aus

BMC-09d fragt:
- kann eine **Gewichtsschwelle** schwache, randständige Kanten entfernen,
  ohne gleichzeitig brauchbare Struktur wie mutual-kNN zu zerstören?

## Distanz- und Gewichtsregel

Wie in BMC-08/BMC-09:

1. offene numerische Featurebasis
2. z-Standardisierung im Build-Script
3. euklidische Distanz im standardisierten Featurevektor
4. Gewicht:
   `weight(i,j) = 1 / (1 + d(i,j))`

Keine neue Distanzdefinition.
Keine readout-nahe Spezialmetrik im ersten Schritt.

## Arm D1 – Threshold Local Graph

### Regel
Eine Kante `(i,j)` bleibt erhalten, wenn:

`weight(i,j) >= tau`

### Start-Schwellen
Für Version 1:

- `tau = 0.25`
- `tau = 0.30`
- `tau = 0.35`

### Begründung
Diese Startwerte liegen in einem Bereich,
in dem schwache Kanten reduziert werden sollten,
ohne sofort fast alle Verbindungen zu verlieren.

## Arm D2 – Hybrid Local Graph

### Regel
Für jeden Knoten `i`:
- bestimme die `k` nächsten Nachbarn
- behalte davon nur jene mit `weight(i,j) >= tau`

Danach symmetrisiere:
Eine Kante `(i,j)` wird gesetzt, wenn die Regel für `i` oder für `j` greift.

### Startleiter
Für Version 1:
- `k = 3`
- `tau = 0.25`
- `tau = 0.30`

### Begründung
`k = 3` war in BMC-09a der einzige Kandidat mit Backbone-Hinweis.
BMC-09d beginnt daher dort und verschärft nur über die Gewichtsschwelle.

## Warum kein Mutual-Hybrid im ersten Schritt?
Das wäre ein zusätzlicher Härtegrad
(`mutual + threshold`) und würde die Interpretation unnötig vermischen.
BMC-09d soll zuerst das **offene Zwischenregime** zwischen 09a und 09c testen.

## Erwartete Strukturfragen

### Q1 – Stabilisierung
Bleibt der Backbone-Hinweis aus BMC-09a erhalten,
wenn schwache Kanten entfernt werden?

### Q2 – Fragmentierung
Ist der Threshold-/Hybrid-Graph weniger zerstörerisch als mutual-kNN?

### Q3 – Coupling
Wird Coupling durch das Entfernen schwacher Fernkanten sichtbarer?

### Q4 – Sensitivität
Taucht ein Effekt nur für sehr enge `tau`-Werte auf,
oder zeigt sich ein belastbarerer Bereich?

## Zusätzliche Graphdiagnostik

Wie in BMC-09a/BMC-09c verpflichtend:

- `graph_construction_method`
- `graph_construction_parameters`
- `graph_node_count`
- `graph_edge_count`
- `connected_component_count`
- `largest_component_size`
- `mean_degree`
- `graph_density`

Zusätzlich empfohlen:
- `isolated_node_count`
- `component_size_profile`

## Warum das wichtig ist
Threshold- und Hybridgraphen können leicht
- zu dünn
- oder inhomogen über Familien
werden.
Ohne Graphdiagnostik wären Befunde kaum interpretierbar.

## Methodische Leitplanken

### Zulässig
- ex ante definierte `tau`- und `k`-Leiter
- offene Gewichtsregel
- symmetrisierte ungerichtete Graphen
- keine stillen Reparaturen

### Nicht zulässig
- `tau` nach Ergebnisinteresse wählen
- isolierte Knoten heimlich anbinden
- familiespezifische Sonderregeln
- Mischung mit readout-nahen Kantenkriterien im selben Schritt

## Priorisierte Testreihenfolge

### Phase 1 – Threshold-only
- `tau = 0.25`
- `tau = 0.30`
- `tau = 0.35`

### Phase 2 – Hybrid local
- `k = 3, tau = 0.25`
- `k = 3, tau = 0.30`

## Begründung der Reihenfolge
Erst die reine Schwellenregel testen.
Danach prüfen, ob die Kombination aus Lokalität und Mindestgewicht
ein besseres Zwischenregime bildet.

## Zu erstellende Dateien

### Neu
- `scripts/build_bmc09d_threshold_and_hybrid_inputs_from_bmc08c.py`
- `data/bmc09d_threshold_hybrid_config.yaml`
- `scripts/run_bmc09d_threshold_hybrid_compare.py`
- `data/bmc09d_threshold_hybrid_compare_config.yaml`

### Wiederverwendet
- `scripts/build_bmc08c_feature_table_from_m39x1_sign_sensitive_ring.py`
- `scripts/bmc07_backbone_variation_runner.py`

## Outputvertrag

### Graph-Build-Ebene
Unter `data/bmc09d_threshold_hybrid_inputs/`:
- je Parameterfall eigener Unterordner
- `baseline_relational_table_real.csv`
- `node_metadata_real.csv`
- `graph_build_summary.json`

### Sweep-Ebene
Unter `runs/BMC-09/BMC09d_threshold_hybrid_open/`:
- `threshold_hybrid_sweep_summary.csv`
- `threshold_hybrid_sweep_metadata.json`

### Einzelruns
Zum Beispiel:
- `runs/BMC-09/BMC09d_threshold_tau_025_realdata_open/`
- `runs/BMC-09/BMC09d_threshold_tau_030_realdata_open/`
- `runs/BMC-09/BMC09d_hybrid_k3_tau_025_realdata_open/`

## Sanity-Checks vor dem Lauf

1. `tau` liegt strikt zwischen `0` und `1`
2. `k` ist positiv und kleiner als Knotenzahl
3. Gewichte sind endlich und positiv
4. keine Selbstkanten
5. Graphdiagnostik wird geschrieben
6. keine stille Komponentenreparatur

## Failure Modes

### F1 – Threshold zu streng
Graph zerfällt ähnlich oder stärker als mutual-kNN.

### F2 – Threshold zu locker
Graph bleibt praktisch zu dicht und bringt keine neue Information.

### F3 – Hybrid wird faktisch zu mutual-kNN
Dann ist das Zwischenregime verloren.

### F4 – Effekt nur in einem mikroskopischen Parameterfenster
Dann liegt eher ein Sensitivitätsbild als ein robuster Strukturhinweis vor.

## Erwartete Lesart

### Fall A – Backbone-Hinweis stabilisiert sich
Dann war BMC-09a wahrscheinlich zu permissiv,
aber die lokale Struktur war real.

### Fall B – Alles bleibt weak/mixed
Dann trägt die aktuelle BMC-08c-Repräsentation selbst kaum robuste Backbone-Struktur.

### Fall C – Coupling wird sichtbar
Dann lag die eigentliche Struktur bislang eher in Brücken- oder Grenzzonen.

## Befund
Noch keiner. Diese Datei ist reine Spezifikation.

## Interpretation
BMC-09d ist der Versuch, den beobachteten Sweet Spot
zwischen Überglättung und Überfragmentierung systematisch zu testen.

## Hypothese
Wenn ein belastbares Strukturregime existiert,
sollte es eher in einem **gewichtsschwellenbasierten lokalen Graphen**
auftauchen als entweder im Vollgraphen oder im mutual-kNN-Extrem.

## Offene Lücke
Noch fehlen:
- Build-Script
- Config
- Sweep-Runner
- danach erst der erste BMC-09d-Lauf

## Feldliste – empfohlene zusätzliche Graphdiagnostik
- `isolated_node_count` — integer — Anzahl isolierter Knoten.
- `component_size_profile` — string/json — Größenverteilung der Zusammenhangskomponenten.
- `graph_construction_family` — string — hier `threshold` oder `hybrid_local`.
