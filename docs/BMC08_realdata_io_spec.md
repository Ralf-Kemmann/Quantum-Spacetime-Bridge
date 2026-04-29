# BMC-08 – I/O-Spezifikation für reale Inputdateien

## Status
Spezifikationsschritt vor Implementierung.

## Zweck
Diese Datei legt den **offenen Input- und Outputvertrag** für BMC-08 fest.

BMC-08 soll die bisherige BMC-07x-Pipeline auf reale Projektgraphen übertragen.
Dafür müssen die Realdaten so in Dateien gegossen werden, dass

- der Rechenweg offen bleibt,
- keine stillen Vorverarbeitungsschritte nötig sind,
- die Zuordnung von Projektartefakten zu Graphknoten und Kanten nachvollziehbar bleibt,
- und spätere Reviewer- oder Replikationsfragen direkt auf Dateien, Felder und Mappingregeln verweisen können.

## Ausgangspunkt

### Letzter belastbarer Befund
BMC-08 ist als Realdaten-Transferblock spezifiziert.
Die Pipeline aus BMC-07 bis BMC-07d steht offen und funktionsfähig,
aber bisher nur auf einem Minimaldatensatz.

### Offene Kernfrage
Wie müssen reale Projektartefakte in `data/` abgelegt werden, damit der Transfer auf echte Inputs
formal sauber, reproduzierbar und methodisch defensiv bleibt?

## Repo-Struktur
Für BMC-08 gilt strikt:

```text
quantum-spacetime-bridge/
├── docs/
├── scripts/
├── data/
└── runs/
```

### Verbindliche Ablageorte
- Spezifikation und Mappingnotizen → `docs/`
- ausführbare Dateien → `scripts/`
- Realdateninputs → `data/`
- Laufoutputs → `runs/`

## Pflichtdateien in `data/`

### 1. `baseline_relational_table_real.csv`
Kantenliste des realen Projektgraphen.

### 2. `node_metadata_real.csv`
Knotenmetadaten inklusive Shell-Zuordnung.

### 3. `bmc08_realdata_config.yaml`
Konfiguration des Realdatenlaufs.

## Optionale Dateien in `data/`

### 4. `pair_neighborhood_matrix_real.npz`
Optionale Referenzmatrix für `pair_neighborhood_shift`.

### 5. `diffusion_distance_matrix_real.npz`
Optionale Referenzmatrix für `diffusion_shift`.

### 6. `bmc04_reference_summary_real.json`
Optionale Referenzzusammenfassung aus vorgelagerten Blöcken.

### 7. `bmc08_dataset_manifest.json`
Empfohlene Manifestdatei mit Herkunft, Version und Ableitungslogik des Datensatzes.

## Inputdatei 1 – `baseline_relational_table_real.csv`

## Zweck
Diese Datei bildet den realen Projektgraphen als offene Kantenliste ab.

Jede Zeile repräsentiert eine gewichtete Beziehung zwischen zwei Knoten.

## Pflichtfelder
- `source`
- `target`
- `weight`

## Empfohlene Zusatzfelder
- `edge_family`
- `relation_type`
- `source_family`
- `target_family`
- `evidence_tag`
- `comment`

## Feldliste
- `source` — string — Kennung des Quellknotens.
- `target` — string — Kennung des Zielknotens.
- `weight` — float — offenes, bereits berechnetes Relationalgewicht.
- `edge_family` — string — optionale Grobklassifikation der Kante.
- `relation_type` — string — optionale genauere Typisierung der Relation.
- `source_family` — string — optionale Familie oder Klasse des Quellknotens.
- `target_family` — string — optionale Familie oder Klasse des Zielknotens.
- `evidence_tag` — string — optionale Kennung der Datengrundlage oder Ableitungsbasis.
- `comment` — string — optionale freie Kurzbeschreibung.

## Regeln
1. `source` und `target` müssen auf Knoten in `node_metadata_real.csv` verweisen.
2. Selbstkanten (`source == target`) sind nicht zulässig.
3. `weight` muss numerisch und endlich sein.
4. Doppelte Kantenpaare sind nur zulässig, wenn ihre Voraggregation offen dokumentiert ist.
5. Wenn der Graph ungerichtet gemeint ist, muss die Tabelle trotzdem jede Kante nur **einmal** enthalten.
6. Negative Gewichte sind nur zulässig, wenn ihre Bedeutung im Mappingdokument explizit erklärt wird.

## Offene Mappingregel
Die Datei muss **das Ergebnis** einer offenen, dokumentierten Relationalisierung sein.
Die Relationalisierung selbst gehört nicht still in den Runner, sondern muss in `docs/` beschrieben werden.

## Inputdatei 2 – `node_metadata_real.csv`

## Zweck
Diese Datei beschreibt die realen Knoten des Projektgraphen.

## Pflichtfelder
- `node_id`
- `shell_index`

## Empfohlene Zusatzfelder
- `node_label`
- `node_family`
- `backbone_hint`
- `role_tag`
- `origin_tag`
- `comment`

## Feldliste
- `node_id` — string — eindeutige Knotenkennung.
- `shell_index` — integer — offene Shell-Zuordnung für den Knoten.
- `node_label` — string — lesbarer Name des Knotens.
- `node_family` — string — optionale Familie / Klasse des Knotens.
- `backbone_hint` — integer|string — optionale unabhängige Backbone-Markierung.
- `role_tag` — string — optionale funktionale Rolle im Datensatz.
- `origin_tag` — string — optionale Herkunftsmarkierung.
- `comment` — string — optionale freie Kurzbeschreibung.

## Regeln
1. Jeder Knoten aus `baseline_relational_table_real.csv` muss genau einmal in `node_metadata_real.csv` vorkommen.
2. `shell_index` muss für jeden Knoten gesetzt und als integer interpretierbar sein.
3. `backbone_hint` darf nur verwendet werden, wenn seine Herleitung **unabhängig** vom späteren BMC-08-Readout ist.
4. Leere Knoteneinträge sind nicht zulässig.
5. Zusätzliche Felder sind erlaubt, solange die Pflichtfelder erhalten bleiben.

## Wichtige methodische Warnung
`backbone_hint` ist **kein Pflichtfeld**.
Wenn es vorhanden ist, muss in `docs/` offen begründet sein,

- woher die Markierung kommt,
- wann sie erzeugt wurde,
- und warum sie nicht bereits dieselbe Struktur in den Backbone einschreibt,
  die später im Readout wieder gemessen wird.

## Inputdatei 3 – `bmc08_realdata_config.yaml`

## Zweck
Diese Datei steuert den offenen BMC-08-Realdatenlauf.

## Mindeststruktur
```yaml
run:
  run_id: "BMC08_realdata_open"
  output_dir: "runs/BMC-08/BMC08_realdata_open"
  seed: 101

inputs:
  baseline_relational_table: "data/baseline_relational_table_real.csv"
  node_metadata: "data/node_metadata_real.csv"
  bmc04_reference_summary: null
  pair_neighborhood_matrix: null
  diffusion_distance_matrix: null

graph:
  directed: false
  weight_column: "weight"
  source_column: "source"
  target_column: "target"

perturbation:
  repeats: 50
  preserve_weight_multiset: true

decision:
  arrangement_signal_min: 0.05
  dominance_gap_min: 0.03
  minimum_repeat_count: 50
  minimum_arm_edge_count: 2

backbone_variants:
  enabled: true
  variants:
    - variant_name: "strength_topk"
      method: "strength_topk"
      top_k: 10

    - variant_name: "strength_topalpha_025"
      method: "strength_topalpha"
      alpha: 0.25
```

## Feldliste
### Abschnitt `run`
- `run.run_id` — string — eindeutige Kennung des Laufs.
- `run.output_dir` — string — Zielordner innerhalb von `runs/`.
- `run.seed` — integer — Startseed für reproduzierbare Shuffle-Wiederholungen.

### Abschnitt `inputs`
- `inputs.baseline_relational_table` — string — Pfad zur realen Kantenliste.
- `inputs.node_metadata` — string — Pfad zur realen Knotentabelle.
- `inputs.bmc04_reference_summary` — null|string — optionale Referenzdatei.
- `inputs.pair_neighborhood_matrix` — null|string — optionale NPZ-Datei.
- `inputs.diffusion_distance_matrix` — null|string — optionale NPZ-Datei.

### Abschnitt `graph`
- `graph.directed` — boolean — Kennzeichnung gerichteter vs. ungerichteter Interpretation.
- `graph.weight_column` — string — Name der Gewichtsspalte.
- `graph.source_column` — string — Name der Quellspalte.
- `graph.target_column` — string — Name der Zielspalte.

### Abschnitt `perturbation`
- `perturbation.repeats` — integer — Anzahl Shuffle-Wiederholungen pro Arm und Variante.
- `perturbation.preserve_weight_multiset` — boolean — Erhaltung des Gewichts-Multisets.

### Abschnitt `decision`
- `decision.arrangement_signal_min` — float — Mindestschwelle für interpretierbaren Arm-Befund.
- `decision.dominance_gap_min` — float — Mindestabstand zur Dominanz anderer Arme.
- `decision.minimum_repeat_count` — integer — Mindestzahl der Wiederholungen.
- `decision.minimum_arm_edge_count` — integer — Mindestzahl Kanten pro Arm.

### Abschnitt `backbone_variants`
- `backbone_variants.enabled` — boolean — Aktivierung der Variantenlogik.
- `backbone_variants.variants` — list — Liste offener Backbone-Varianten.

## Empfohlene Realdaten-Manifestdatei – `bmc08_dataset_manifest.json`

## Zweck
Dokumentiert Herkunft und Ableitung des Realdatensatzes.

## Empfohlene Felder
- `dataset_id` — string — Kennung des Datensatzes.
- `dataset_version` — string — Version oder Datumsstand.
- `source_artifacts` — list[string] — Herkunftsdateien oder Vorblöcke.
- `relationalization_rule` — string — Kurzbeschreibung der Ableitungslogik.
- `shell_assignment_rule` — string — Kurzbeschreibung der Shell-Zuordnung.
- `backbone_hint_origin` — string|null — Herkunft eines optionalen `backbone_hint`.
- `notes` — list[string] — freie methodische Hinweise.

## Outputvertrag für BMC-08

### Zielordner
`runs/BMC-08/<run_id>/`

## Pflichtoutputs
- `summary.json`
- `validation.json`
- `run_metadata.json`
- `backbone_variant_summary.csv`
- `repeat_metrics.csv`
- `readout.md`

## Pro Variante zusätzlich
Unterordner:
`runs/BMC-08/<run_id>/<variant_name>/`

mit:
- `summary.json`
- `arm_metrics.csv`

## Minimaler Readoutvertrag
Der spätere Readout muss explizit trennen:
- **Befund**
- **Interpretation**
- **Hypothese**
- **Offene Lücke**

## Sanity-Checks vor Laufstart

1. Existieren alle Pflichtdateien in `data/`?
2. Decken `node_metadata_real.csv` und `baseline_relational_table_real.csv` dieselbe Knotenmengenbasis ab?
3. Ist `shell_index` vollständig?
4. Ist `weight` numerisch und endlich?
5. Sind die Backbone-Varianten in der Config offen dokumentiert?
6. Ist ein eventuelles `hint_reference` methodisch legitimiert?
7. Gibt es mindestens zwei nichtleere Teilarm-Konfigurationen pro Variante?

## Failure Modes

### F1 – stille Voraggregation
Kanten wurden zusammengeführt, ohne dass die Aggregationsregel offen dokumentiert ist.

### F2 – stille Shell-Zuordnung
`shell_index` wurde heuristisch gesetzt, ohne Dokumentation der Zuweisungsregel.

### F3 – readout-nahe Hint-Erzeugung
`backbone_hint` wurde nachträglich aus derselben Struktur gewonnen, die später gemessen wird.

### F4 – Runner übernimmt Vorverarbeitung
Nicht zulässig. Vorverarbeitung gehört offen in `docs/` und ggf. in ein separates Script in `scripts/`.

### F5 – Realdaten mit Minimaldatenlogik verwechselt
Das Realdatenmapping muss explizit benennen, welche Projektartefakte als Knoten und welche Relationen als Kanten eingehen.

## Empfohlene Begleitdokumente in `docs/`

### 1. `BMC08_realdata_mapping_note.md`
Erklärt:
- was ein Knoten ist
- was eine Kante ist
- wie `weight` gebildet wurde
- wie `shell_index` gebildet wurde

### 2. `BMC08_backbone_hint_justification.md`
Nur falls `backbone_hint` verwendet wird.

### 3. `BMC08_realdata_vs_minimal_note.md`
Vergleich der Realdatenbefunde mit dem Minimalblock.

## Befund
Noch keiner. Diese Datei ist reine I/O-Spezifikation.

## Interpretation
Die Spezifikation macht BMC-08 nicht „schöner“, sondern prüfbar.
Sie zwingt den Realdatentransfer in offene, dateibasierte Verträge.

## Hypothese
Wenn Mapping, Shell-Zuordnung und Backbone-Varianten offen dokumentiert bleiben,
kann BMC-08 auf Realdaten dieselbe methodische Defensivität behalten wie der Minimalblock.

## Offene Lücke
Noch fehlen:
- konkrete Realdaten-Mappingdateien,
- ggf. ein Build-Script für die Realdatentabellen,
- der angepasste Runner-/Run-Script-Schritt für BMC-08.

## Feldliste – Kurzüberblick aller Pflichtdateien

### `baseline_relational_table_real.csv`
- `source` — string — Quellknoten
- `target` — string — Zielknoten
- `weight` — float — Relationalgewicht

### `node_metadata_real.csv`
- `node_id` — string — Knotenkennung
- `shell_index` — integer — Shell-Zuordnung

### `bmc08_realdata_config.yaml`
- `run` — object — Laufdefinition
- `inputs` — object — Dateipfade
- `graph` — object — Graphinterpretation
- `perturbation` — object — Shuffle-Parameter
- `decision` — object — Defensivschwellen
- `backbone_variants` — object — Variantenliste
