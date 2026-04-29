# BMC-07b – Coupling-Arm Erweiterung (Spezifikation)

## Status
Spezifikationsschritt vor Implementierung.

## Zweck
BMC-07b erweitert den bestehenden BMC-07-Minimalrunner um einen eigenen diagnostischen
**Coupling-Arm**, um die bisher offene Frage gezielt zu testen:

**Sitzt das lokale Arrangement-Signal eher**
- im Backbone-Kern,
- im Off-Backbone-Rest,
- **oder in den Kopplungskanten zwischen beiden Bereichen?**

## Ausgangspunkt

### Letzter belastbarer Befund
Der erste offene BMC-07-Minimallauf (`runs/BMC-07/BMC07_minimal_readouts_open/`) ergab:

- `decision_label = weak_or_inconclusive`
- `full_graph.arrangement_signal = 0.024059`
- `backbone_only.arrangement_signal = -0.004218`
- `off_backbone_only.arrangement_signal = 0.077322`
- `coupling_edge_count = 4`

### Projektinterne Lesart
Der Minimaldatensatz stützt **keine Backbone-Lokalisierung**.
Das kleine positive Signal sitzt dort eher im **Off-Backbone-Arm** als im Backbone-Arm.

### Offene Kernfrage
Die bisherige Trennung
- `backbone_only`
- `off_backbone_only`

lässt die **Kopplungskanten** nur indirekt über den Vollgraphen mitlaufen.
Genau diese Kopplung kann aber der eigentliche Träger des lokalen Signals sein.

## Blockdefinition

### Neue Armstruktur
BMC-07b führt zusätzlich zu den bestehenden Armen einen vierten Arm ein:

- `full_graph`
- `backbone_only`
- `off_backbone_only`
- `coupling_only`

### Definition von `coupling_only`
Eine Kante gehört zu `coupling_only`, wenn genau **ein** Endknoten im Backbone liegt
und der andere **nicht** im Backbone liegt.

Formal für Kante `(u, v)` mit Backbone-Menge `B`:
- `coupling_only` falls `[(u in B) XOR (v in B)] == True`

## Zielhypothesen

### H1 – Coupling-dominant
Das Arrangement-Signal ist im Coupling-Arm am stärksten positiv.
Dann wäre die Kopplungszone der primäre lokale Signalträger.

### H2 – Off-backbone-dominant
Das bisherige Bild bleibt bestehen; das Signal sitzt eher im Restnetz.

### H3 – Backbone-dominant
Die bisherige Minimalheuristik war irreführend; mit Coupling-Arm bleibt der Backbone
trotzdem der stärkere Träger.

### H4 – Mixed / weak
Kein Arm trägt klar; das Muster bleibt schwach oder instabil.

## Readouts
Die Readouts bleiben absichtlich **identisch** zum bisherigen Minimalblock, um keine
Methodenmischung einzuführen.

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
- `diffusion_shift`
- `pair_neighborhood_shift`

## Shuffle-Logik
Unverändert:
- feste Topologie pro Arm
- Gewichte werden pro Wiederholung über die Arm-Kantenliste permutiert
- keine versteckte Nachbearbeitung
- keine neue Optimierungsheuristik in diesem Schritt

## Entscheidungslogik (defensiv)

### Neue mögliche `decision_label`-Werte
- `backbone_localization_supported`
- `off_backbone_localization_supported`
- `coupling_localization_supported`
- `full_only_or_mixed`
- `weak_or_inconclusive`

### Vorschlag für defensive Entscheidungsregel
#### 1. coupling_localization_supported
Wenn:
- `coupling_only.arrangement_signal >= arrangement_signal_min`
- und `coupling_only.arrangement_signal` mindestens um `dominance_gap_min`
  über **beiden** Armen `backbone_only` und `off_backbone_only` liegt

#### 2. backbone_localization_supported
Wenn:
- `backbone_only.arrangement_signal >= arrangement_signal_min`
- und Backbone mindestens um `dominance_gap_min` über `off_backbone_only`
  und `coupling_only` liegt

#### 3. off_backbone_localization_supported
Wenn:
- `off_backbone_only.arrangement_signal >= arrangement_signal_min`
- und Off-Backbone mindestens um `dominance_gap_min` über `backbone_only`
  und `coupling_only` liegt

#### 4. full_only_or_mixed
Wenn:
- `full_graph.arrangement_signal >= arrangement_signal_min`
- aber kein Teilarm klar dominiert

#### 5. weak_or_inconclusive
Wenn:
- alle Signale klein bleiben
- oder Armunterschiede unterhalb der Dominanzschwelle bleiben
- oder ein Arm zu klein / zu dünn besetzt ist

## Sanity-Checks
Zusätzlich zu den bisherigen Prüfungen:

- `coupling_edge_count > 0`
- `coupling_only.edge_count >= minimum_arm_edge_count`
- `coupling_only.node_count >= 2`

Falls nicht erfüllt:
- Coupling-Arm berechnen, aber als **diagnostisch schwach** markieren
- kein starker Lokalisierungsclaim auf Coupling-Basis

## Outputvertrag

### summary.json
Erweiterung:
- neuer Arm `coupling_only` in `arms`
- zusätzlich optional:
  - `dominant_arm`
  - `arm_signal_ranking`

### arm_metrics.csv
Neue mögliche Zeile:
- `arm_name = coupling_only`

### repeat_metrics.csv
Neue mögliche Wiederholungsreihe:
- `arm_name = coupling_only`

### readout.md
Der Readout soll explizit vier Ebenen trennen:
- **Befund**
- **Interpretation**
- **Hypothese**
- **Offene Lücke**

Und im Befundteil den Coupling-Arm ausdrücklich mit ausweisen.

## Minimaländerungen an Dateien

### Zu ändern
- `scripts/bmc07_backbone_scaffold_isolation_runner_minimal_readouts.py`
- `data/bmc07_config_minimal_readouts.yaml`
- optional: `docs/BMC07_execution_contract.md`

### Nicht zu ändern
- Inputtabellenformat in `data/`
- bestehende Readoutdefinitionen
- bestehender offener Startweg über
  `bash scripts/run_bmc07_minimal_readouts_open.sh`

## Konfigurationsvorschlag
Ergänzung im YAML:

```yaml
arms:
  evaluate_full_graph: true
  evaluate_backbone_only: true
  evaluate_off_backbone_only: true
  evaluate_coupling_only: true

decision:
  arrangement_signal_min: 0.05
  dominance_gap_min: 0.03
  minimum_repeat_count: 20
  minimum_arm_edge_count: 2
```

## Was der Block bewusst gut macht
- lokalisiert den Signalort genauer
- bleibt im bestehenden offenen Rechenweg
- führt keine neue Blackbox-Metrik ein
- macht die bisher implizite Kopplungszone explizit sichtbar

## Was der Block bewusst vermeidet
- keine neue physikalische Großdeutung
- keine neue Backbone-Theorie
- keine Überhöhung eines Minimaldatensatzes
- keine Verwechslung von Diagnostikarm und Theoriebeweis

## Befund
Noch keiner. Diese Datei ist reine Spezifikation.

## Interpretation
BMC-07b ist die methodisch naheliegende Fortsetzung des ersten offenen Minimallaufs.

## Hypothese
Der Coupling-Arm könnte der eigentlich relevante lokale Signalträger sein.

## Offene Lücke
Noch offen ist, ob der Coupling-Arm auf dem Minimaldatensatz tatsächlich dominiert
oder ob das Bild bei vier Armen weiterhin `weak_or_inconclusive` bleibt.
