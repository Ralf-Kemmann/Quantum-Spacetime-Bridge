# BMC-08a – Konkrete Mapping-Spezifikation (Ring / Cavity / Membrane)

## Status
Konkrete Mapping-Spezifikation vor Build-Script und Realdatenlauf.

## Zweck
BMC-08a legt für den ersten realen BMC-08-Block **konkret** fest, wie der physikalisch interpretierbare Strukturblock

- `Ring`
- `Cavity`
- `Membrane`

in offene BMC-08-Inputdateien überführt wird.

Diese Datei beantwortet nicht mehr nur allgemein, **dass** gemappt werden muss, sondern **wie genau** der erste Realdaten-Mappingvertrag aussehen soll.

## Ausgangspunkt

### Letzter belastbarer Befund
Für BMC-08 wurde als erster Realdatenblock priorisiert:
- **Kandidat B = Ring / Cavity / Membrane**
- optional später ergänzend: **Kandidat C = N1 / Neighborhood**

### Projektinterne Lesart
Ring / Cavity / Membrane ist für den ersten Realdatenlauf geeignet, weil:
- die Einheiten physikalisch interpretierbar sind
- die Gruppenbildung nicht künstlich wirkt
- die Readout-Nähe geringer ist als bei bereits hochaggregierten Prädiktor-Feldern
- der Block trotzdem strukturell reich genug ist

## Kernentscheidung

## Knotenebene
Der erste BMC-08a-Datensatz verwendet **einzelne reale Systeminstanzen** als Knoten.

### Knoten = einzelne Einheiten aus den drei Familien
- `RING`
- `CAVITY`
- `MEMBRANE`

Jede reale Einheit wird genau **ein Knoten**.

### Nicht zu verwenden in BMC-08a
- Familien als Superknoten
- künstliche Mischknoten
- Meta-Knoten wie „average ring“
- Voraggregationen auf Familienebene als Primärknoten

## Kantenebene
Eine Kante beschreibt die **offene relationale Nähe** zwischen zwei realen Einheiten.

### Grundregel
BMC-08a arbeitet zunächst mit einem **vollständigen gewichteten ungerichteten Graphen**
über alle zugelassenen Einheiten des Blocks.

Das heißt:
- jede Einheit wird mit jeder anderen Einheit verglichen
- jede Paarung erzeugt genau eine Kante
- keine stille KNN-Auswahl im Runner
- keine implizite Schwellenbildung im Runner

## Vorteil dieser Wahl
- maximale Transparenz
- keine versteckte Topologieentscheidung
- spätere Sparsifizierung kann offen als eigener Block geprüft werden
- BMC-08a trennt zunächst sauber:
  - Mapping
  - Gewicht
  - Shell
  - spätere Diagnostik

## Gewicht (`weight`)

## Grundidee
`weight` soll die **relationale Ähnlichkeit** zweier Einheiten ausdrücken.

Da Ring / Cavity / Membrane als physikalisch interpretierbare Systemfamilien vorliegen, wird die erste BMC-08a-Stufe **nicht** mit schon hochabgeleiteten Projektprädiktoren starten, sondern mit einer **offen dokumentierten Distanz-zu-Nähe-Abbildung** auf einer kleinen, expliziten Merkmalsbasis.

## Offene Basismerkmale
Pro Einheit wird eine **klar dokumentierte Featuremenge** verwendet, z. B.:
- Frequenz- oder Modenlage
- charakteristische Längenskala
- geometrisch-strukturelle Kennzahl
- ggf. einfache normierte Energienähe oder Spektralzahl

### Arbeitsregel
Nur Merkmale verwenden, die
- bereits offen vorliegen
- physikalisch oder methodisch direkt lesbar sind
- nicht selbst schon aus dem späteren Lokalisierungsreadout konstruiert wurden

## Konkrete Gewichtungsregel – BMC-08a Startversion

### Schritt W1 – Featurevektor pro Knoten
Jede Einheit erhält einen offenen numerischen Featurevektor

`x_i = (f_1, f_2, ..., f_p)`

### Schritt W2 – Distanz
Für zwei Einheiten `i, j`:

`d(i,j) = sqrt(sum_k (z_{ik} - z_{jk})^2)`

wobei `z_{ik}` die offen standardisierten Featurewerte sind.

### Schritt W3 – Nähegewicht
Das Kantengewicht wird als monotone Distanzabbildung definiert:

`weight(i,j) = 1 / (1 + d(i,j))`

## Warum diese Regel?
- offen
- klein
- monotone Abbildung
- keine Blackbox
- keine direkte Rückkopplung an das spätere BMC-08-Readout
- leicht reproduzierbar

## Nicht Teil von BMC-08a
- komplexe Kerneltricks
- lernbasierte Embeddings
- nachträgliche Gewichtskalibrierung „bis das Bild passt“

## Shell-Zuordnung (`shell_index`)

## Grundregel
Die Shell-Zuordnung soll in BMC-08a **nicht** direkt aus dem späteren Readout stammen.

### Erste konkrete Regel für BMC-08a
Die Shell wird als **Familien-Lagenregel** definiert.

#### Vorschlag S1 – Familienbasierte Shells
- `RING` → `shell_index = 0`
- `CAVITY` → `shell_index = 1`
- `MEMBRANE` → `shell_index = 2`

## Begründung
- offen
- unmittelbar lesbar
- keine versteckte Optimierung
- physikalisch/strukturell plausibel erste Lagenklassifikation
- klare Trennung von Knotentyp und späterem Gewichtssignal

## Wichtige methodische Einschränkung
Diese Shell-Regel ist **eine erste Arbeitsregel**, nicht die letzte Wahrheit.
Sie ist bewusst grob und defensiv.

### Projektinterne Lesart
BMC-08a testet zunächst, ob schon unter einer einfachen, offen lesbaren Familien-Shell überhaupt ein interpretierbares Lokalisierungsmuster entsteht.

## Optional spätere Shell-Varianten
Nicht in BMC-08a selbst, aber später prüfbar:
- Distanz zum Referenzfamilienkern
- innere Lage innerhalb einer Familie
- modal geordnete Layer
- Vorblock-definierte Strukturstufen

## Knotentabelle – konkrete Felder

## Ziel-Datei
`data/node_metadata_real.csv`

## Pflichtfelder
- `node_id`
- `shell_index`

## Pflicht-Zusatzfelder für BMC-08a
- `node_label`
- `node_family`
- `origin_tag`

## Empfohlene Feldliste
- `node_id` — string — eindeutige Knotenkennung.
- `shell_index` — integer — Familien-Shell (`RING=0`, `CAVITY=1`, `MEMBRANE=2`).
- `node_label` — string — lesbarer Name der Einheit.
- `node_family` — string — eine der Familien `RING`, `CAVITY`, `MEMBRANE`.
- `origin_tag` — string — Herkunft oder Dateiquelle der Einheit.
- `comment` — string — optionale Kurzbeschreibung.

## Kantenliste – konkrete Felder

## Ziel-Datei
`data/baseline_relational_table_real.csv`

## Pflichtfelder
- `source`
- `target`
- `weight`

## Pflicht-Zusatzfelder für BMC-08a
- `edge_family`
- `relation_type`
- `evidence_tag`

## Empfohlene Feldliste
- `source` — string — Knoten-ID der ersten Einheit.
- `target` — string — Knoten-ID der zweiten Einheit.
- `weight` — float — Ähnlichkeitsgewicht `1 / (1 + d)`.
- `edge_family` — string — z. B. `intra_family` oder `cross_family`.
- `relation_type` — string — z. B. `euclidean_similarity`.
- `evidence_tag` — string — Kennung der zugrunde liegenden Merkmalsbasis.
- `comment` — string — optionale Kurzbeschreibung.

## Regel für `edge_family`
- `intra_family` wenn `node_family(source) == node_family(target)`
- `cross_family` sonst

## Keine Verwendung von `backbone_hint` in BMC-08a
Für den ersten Realdatenlauf wird **kein** `backbone_hint` vorausgesetzt.

### Stattdessen faire Backbone-Varianten
- `strength_topk`
- `strength_topalpha`

Optional später:
- `hint_reference`, falls unabhängig begründet
- `hybrid_strength_shell`, rein explorativ

## Konkrete Beispielzeilen

## Beispiel `node_metadata_real.csv`
```csv
node_id,shell_index,node_label,node_family,origin_tag,comment
ring_001,0,Ring-001,RING,m39x1_export,baseline ring instance
ring_002,0,Ring-002,RING,m39x1_export,baseline ring instance
cavity_001,1,Cavity-001,CAVITY,m39x1_export,baseline cavity instance
membrane_001,2,Membrane-001,MEMBRANE,m39x1_export,baseline membrane instance
```

## Beispiel `baseline_relational_table_real.csv`
```csv
source,target,weight,edge_family,relation_type,evidence_tag,comment
ring_001,ring_002,0.8421,intra_family,euclidean_similarity,bmc08a_feature_v1,within-ring similarity
ring_001,cavity_001,0.5314,cross_family,euclidean_similarity,bmc08a_feature_v1,ring-cavity similarity
ring_001,membrane_001,0.4178,cross_family,euclidean_similarity,bmc08a_feature_v1,ring-membrane similarity
cavity_001,membrane_001,0.6023,cross_family,euclidean_similarity,bmc08a_feature_v1,cavity-membrane similarity
```

## Manifest-Empfehlung

## Ziel-Datei
`data/bmc08_dataset_manifest.json`

## Empfohlene Felder
- `dataset_id`
- `dataset_version`
- `source_artifacts`
- `node_semantics`
- `edge_semantics`
- `feature_set`
- `weight_rule`
- `shell_rule`
- `notes`

## Konkrete Startwerte
- `node_semantics = "single physical instances from ring/cavity/membrane block"`
- `edge_semantics = "pairwise similarity between standardized feature vectors"`
- `weight_rule = "1 / (1 + euclidean_distance(z-scored features))"`
- `shell_rule = "family shell: RING=0, CAVITY=1, MEMBRANE=2"`

## Sanity-Checks vor dem Build
1. Jede Einheit gehört genau einer Familie an.
2. Jede Einheit hat vollständige Basisfeatures.
3. Standardisierung der Features ist offen dokumentiert.
4. Jede Paarung erscheint genau einmal.
5. `weight` ist endlich und im offenen Startblock positiv.
6. Alle Knoten der Kantenliste erscheinen in `node_metadata_real.csv`.
7. Die Shell-Regel ist exakt dieselbe für alle Einheiten derselben Familie.

## Failure Modes

### F1 – Familienmischung ohne klare Semantik
Einheiten werden zusammengelegt, obwohl nicht klar ist, ob sie vergleichbar sind.

### F2 – zu komplexe Featurebasis
Die Gewichte hängen schon an hochaggregierten Projektkonstrukten statt an offener Basisnähe.

### F3 – Shell-Regel wird nach Ergebnisinteresse verändert
Nicht zulässig.

### F4 – Runner übernimmt Featurestandardisierung heimlich
Nicht zulässig. Diese gehört in ein offenes Build-Script.

### F5 – KNN oder Schwellen werden still vorab eingeführt
Nicht zulässig in BMC-08a.

## Praktische Arbeitsreihenfolge für BMC-08a

### Schritt 1
Konkreten Exportblock Ring / Cavity / Membrane festlegen.

### Schritt 2
Kleine offene Featureliste definieren.

### Schritt 3
Build-Script schreiben:
- Featurestandardisierung
- Distanzbildung
- Gewichtsbildung
- Export von `baseline_relational_table_real.csv`
- Export von `node_metadata_real.csv`
- optional Export von Manifest

### Schritt 4
Realdaten-Config erstellen.

### Schritt 5
Erst danach:
- Runnerlauf BMC-08

## Befund
Noch keiner. Diese Datei ist reine konkrete Mapping-Spezifikation.

## Interpretation
BMC-08a macht den Realdatentransfer erstmals konkret genug, dass daraus offene Dateien gebaut werden können.

## Hypothese
Wenn bereits unter dieser groben, fairen Familien-Shell ein interpretierbares Muster auftritt, ist das methodisch deutlich stärker als ein Effekt, der erst unter readout-näheren Segmentierungen sichtbar wird.

## Offene Lücke
Noch fehlen:
- die tatsächlich gewählte kleine Featureliste
- das offene Build-Script
- die konkrete Manifestdatei
- die Realdaten-Config für den ersten Lauf

## Feldliste – spätere Build-Inputtabelle (empfohlen)
Falls eine Zwischen-Datei genutzt wird, sollte sie mindestens enthalten:
- `node_id` — string — Einheitenkennung
- `node_family` — string — Familie (`RING`, `CAVITY`, `MEMBRANE`)
- `node_label` — string — lesbarer Name
- `feature_1` ... `feature_p` — float — offene numerische Basismerkmale
- `origin_tag` — string — Herkunft des Datensatzes
- `comment` — string — optionale Bemerkung
