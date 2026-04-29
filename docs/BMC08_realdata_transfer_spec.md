# BMC-08 – Real-Data Transfer Block (Spezifikation)

## Status
Spezifikationsschritt vor Implementierung.

## Zweck
BMC-08 überträgt die bis BMC-07d offen aufgebaute Diagnostikpipeline
vom **Minimaldatensatz** auf **reale Projektgraphen**.

Die Kernfrage lautet:

**Überlebt die bisher beobachtete Lokalisierungstendenz auf realen Inputs, wenn dieselbe offene Logik ohne Hidden Code auf echte Relationaldaten angewendet wird?**

BMC-08 ist damit der Übergang von
- **Funktions- und Legitimationsprüfung**
zu
- **inhaltlich relevantem Projekttest**.

## Ausgangspunkt

### Letzter belastbarer Befund
Aus BMC-07 bis BMC-07d ergibt sich auf dem Minimaldatensatz:

- Off-Backbone-Tendenz unter mehreren einfachen, methodisch fairen Backbone-Definitionen
- Backbone-Recovery nur unter `same_shell_core`
- `same_shell_core` methodisch transparent, aber legitimatorisch readout-nah
- damit insgesamt:
  - **definition-sensitiv**
  - aber **nicht beliebig**
  - und unter fairen Basisvarianten eher **off-backbone-freundlich**

### Projektinterne Lesart
Der Minimalblock hat seine Aufgabe erfüllt:
- Rechenweg offen
- Segmentierung offen
- Varianten offen
- methodische Selbstkritik offen

Was noch fehlt, ist der eigentliche Transfer auf reale Projektinputs.

## Blockdefinition

BMC-08 verwendet die bestehende BMC-07c/BMC-07d-Logik weiter, ersetzt aber den Minimaldatensatz durch reale Eingaben aus dem Projekt.

### Konstant zu halten
- offene Repo-Struktur
- keine hidden calculations
- gleiche Armstruktur:
  - `full_graph`
  - `backbone_only`
  - `off_backbone_only`
  - `coupling_only`
- gleiche Readouts:
  - `arrangement_signal`
  - `shell_order_drift`
  - `same_shell_weight_fraction`
  - optional `diffusion_shift`
  - optional `pair_neighborhood_shift`
- gleiche defensive Entscheidungslogik
- gleiche Trennung von
  - Befund
  - Interpretation
  - Hypothese
  - offener Lücke

### Zu ersetzen
- der künstliche Minimaldatensatz in `data/`
durch
- reale Projektinputs

## Zielfragen

### Q1 – Realer Transfer
Tritt unter realen Projektgraphen überhaupt ein analoges Lokalisierungsmuster auf?

### Q2 – Robustheit unter fairen Backbone-Varianten
Bleibt ein mögliches Off-Backbone- oder Backbone-Muster unter `strength_topk` und `strength_topalpha` erhalten?

### Q3 – Rolle der Kopplung
Ist `coupling_only` auf realen Graphen weiterhin nur sekundär oder wird die Kopplungszone dort wichtiger?

### Q4 – Minimal-vs-Real-Divergenz
Unterscheidet sich das reale Muster klar vom Minimaldatensatz?
Wenn ja, an welcher Stelle:
- Arm-Rangfolge
- Dominanzstärke
- Stabilität
- Kopplungskantenanteil
- Backbone-Größe

## Inputvertrag

### Pflichtdateien in `data/`
BMC-08 braucht mindestens:

- `baseline_relational_table_real.csv`
- `node_metadata_real.csv`
- `bmc08_realdata_config.yaml`

### Optional
- `pair_neighborhood_matrix_real.npz`
- `diffusion_distance_matrix_real.npz`
- `bmc04_reference_summary_real.json`

## Feldanforderungen – baseline_relational_table_real.csv
Pflichtfelder:
- `source`
- `target`
- `weight`

Optional, aber empfohlen:
- `edge_family`
- `relation_type`
- `source_family`
- `target_family`

## Feldanforderungen – node_metadata_real.csv
Pflichtfelder:
- `node_id`
- `shell_index`

Empfohlen:
- `node_label`
- `node_family`
- `backbone_hint` (nur falls bereits unabhängig begründet vorhanden)
- `comment`

## Wichtige methodische Regel für Realdaten
Ein vorhandenes `backbone_hint` darf in BMC-08 **nur dann** als Referenzvariante genutzt werden, wenn es
**vor** diesem Block unabhängig definiert wurde.

Nicht zulässig:
- ein `backbone_hint`, das nachträglich aus denselben Strukturmerkmalen konstruiert wird,
  die später im Readout wieder gemessen werden.

## Backbone-Varianten für BMC-08

### Als faire Basisvarianten priorisiert
- `strength_topk`
- `strength_topalpha`

### Optional ergänzend
- `hint_reference` nur bei unabhängiger Vorbegründung

### Nur explorativ
- `hybrid_strength_shell`

### Nicht als primäre Hauptstütze
- `same_shell_core`

## Readouts

### Primäre Readouts je Arm
- `edge_count`
- `node_count`
- `total_weight`
- `same_shell_weight_fraction`
- `weighted_shell_gap`
- `shuffle_mean_gap`
- `shuffle_std_gap`
- `arrangement_signal`
- `shell_order_drift`

### Optionale Zusatzreadouts
- `diffusion_shift`
- `pair_neighborhood_shift`

## Primäre Vergleichsebenen

### Ebene A – pro Variante
- `decision_label`
- `dominant_arm`
- `arm_signal_ranking`

### Ebene B – variantenübergreifend
- bleibt eine Lokalisierung unter fairen Basisvarianten erhalten?
- kippt das Bild nur unter readout-näheren Varianten?
- entstehen neue Mischbilder?

### Ebene C – Minimal-vs-Real
- Vergleich der Arm-Rangfolge
- Vergleich der Dominanzabstände
- Vergleich des Coupling-Anteils
- Vergleich der Backbone-Sensitivität

## Entscheidungslogik (defensiv)

### Mögliche Befundklassen
- `off_backbone_result_robust`
- `backbone_result_recovered`
- `coupling_result_emergent`
- `backbone_definition_sensitive`
- `still_weak_or_mixed`

### Projektinterne Lesart
#### off_backbone_result_robust
Wenn unter fairen Basisvarianten Off-Backbone konsistent dominiert.

#### backbone_result_recovered
Wenn unter fairen Basisvarianten Backbone konsistent dominiert.
Nicht ausreichend:
- Backbone-Recovery nur unter readout-näheren Varianten.

#### coupling_result_emergent
Wenn Coupling auf realen Inputs erstmals unter fairen Varianten der stärkste Arm wird.

#### backbone_definition_sensitive
Wenn das Gesamtbild zwischen fairen Varianten spürbar kippt.

#### still_weak_or_mixed
Wenn reale Inputs kein klar interpretierbares Lokalisierungsmuster tragen.

## Outputvertrag

### Zielordner
`runs/BMC-08/<run_id>/`

### Pflichtoutputs
- `summary.json`
- `validation.json`
- `run_metadata.json`
- `backbone_variant_summary.csv`
- `repeat_metrics.csv`
- `readout.md`

### Pro Variante zusätzlich
Unterordner:
`runs/BMC-08/<run_id>/<variant_name>/`

mit:
- `summary.json`
- `arm_metrics.csv`

### Vergleichsartefakt zusätzlich empfohlen
- `docs/BMC08_realdata_vs_minimal_note.md`

## Failure Modes

### F1 – Inputstruktur unvollständig
- fehlende Pflichtspalten
- inkonsistente Knotennamen
- Shell-Zuordnungen fehlen

### F2 – Graph degeneriert
- zu wenige Knoten
- zu wenige Kanten
- leere Teilarme
- fast keine Coupling-Kanten

### F3 – Backbone-Definition nicht legitim
- `hint_reference` ohne unabhängige Herleitung
- readout-nahe Regel als Hauptstütze

### F4 – Ergebnisüberdehnung
- schwache oder gemischte Resultate werden als klare Lokalisierung formuliert

## Sanity-Checks

Vor jedem Lauf offen prüfen:
- sind `source`, `target`, `weight` vorhanden?
- sind alle Knoten aus der Kantenliste in `node_metadata_real.csv` abgedeckt?
- ist `shell_index` für alle Knoten gesetzt?
- existieren mindestens zwei nichtleere Teilarme?
- ist die Variantendefinition offen dokumentiert?
- ist `hint_reference` methodisch legitimiert, falls verwendet?

## Was der Block bewusst gut macht
- zieht die Pipeline vom Testsystem in den realen Projektkontext
- hält Readouts und Segmentierungslogik offen
- erlaubt direkte Minimal-vs-Real-Vergleiche
- schützt vor vorschneller Backbone-Rettung durch readout-nahe Definitionen

## Was der Block bewusst vermeidet
- keine Theoriekorrektur aus einem Einzelrun
- keine große physikalische Deutung aus schwachen Lokalisierungsmustern
- keine versteckten Vorverarbeitungen
- keine stillen Optimierungen an der Segmentierung bis ein gewünschtes Ergebnis erscheint

## Befund
Noch keiner. Diese Datei ist reine Spezifikation.

## Interpretation
BMC-08 ist der methodisch notwendige Übergang vom Minimalblock zum realen Projekttest.

## Hypothese
Wenn die bisherige Off-Backbone-Tendenz auch auf realen Projektgraphen unter fairen Basisvarianten erscheint, wird sie methodisch deutlich belastbarer.
Wenn sich dagegen Coupling oder Backbone unter fairen Regeln durchsetzt, dann war der Minimaldatensatz nur ein Funktionsbild und nicht inhaltlich leitend.

## Offene Lücke
Es fehlen noch:
- konkrete Realdaten-Mappings
- I/O-Spezifikation der realen Inputdateien
- vollständiger Runner bzw. Adaption des bestehenden Varianten-Runners auf Realdaten
- offene Startskripte für den Realdatenlauf

## Feldliste – mögliche spätere Realdaten-Matrix
- `variant_name` — string — Name der Backbone-Variante.
- `decision_label` — string — Ergebnislabel für die Variante.
- `dominant_arm` — string — stärkster Arm der Variante.
- `full_graph_arrangement_signal` — float — Arrangement-Signal Vollgraph.
- `backbone_only_arrangement_signal` — float — Arrangement-Signal Backbone-Arm.
- `off_backbone_only_arrangement_signal` — float — Arrangement-Signal Off-Backbone-Arm.
- `coupling_only_arrangement_signal` — float — Arrangement-Signal Coupling-Arm.
- `backbone_node_count` — integer — Anzahl Backbone-Knoten.
- `coupling_edge_count` — integer — Anzahl Coupling-Kanten.
- `input_dataset_id` — string — Kennung des realen Inputsatzes.
- `note` — string — kurze methodische Einordnung.
