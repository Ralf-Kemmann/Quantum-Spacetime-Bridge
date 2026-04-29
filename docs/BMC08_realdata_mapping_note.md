# BMC-08 – Realdata Mapping Note

## Status
Mapping- und Dokumentationsschritt vor Build-Script und Realdatenlauf.

## Zweck
Diese Note beschreibt offen, **wie reale Projektartefakte in BMC-08 auf Graphknoten, Kanten und Shell-Zuordnungen abgebildet werden sollen**.

Sie ist bewusst **noch kein Datensatz** und **noch kein Runner-Schritt**, sondern der methodische Zwischenblock, der späteren Realdatendateien eine nachvollziehbare Herkunft gibt.

Ziel ist, dass für jede spätere Datei in `data/` klar beantwortbar ist:

- **Was ist ein Knoten?**
- **Was ist eine Kante?**
- **Wie wird `weight` gebildet?**
- **Wie wird `shell_index` gebildet?**
- **Woher kommt ein optionales `backbone_hint` — falls es überhaupt verwendet wird?**

## Ausgangspunkt

### Letzter belastbarer Befund
BMC-08 ist als Realdaten-Transferblock spezifiziert.
Die I/O-Spezifikation für reale Inputdateien liegt vor.

### Offene Kernfrage
Wie übersetzen wir reale Projektartefakte in:
- `baseline_relational_table_real.csv`
- `node_metadata_real.csv`

ohne stillen Umbau, ohne versteckte Heuristiken und ohne Vermischung von Mapping und späterem Readout?

## Grundregel
**Der Runner baut keine Realdaten.**
Der Runner liest nur offene Dateien.

Alle Realdatenableitungen müssen deshalb
- in `docs/` beschrieben
- und bei Bedarf in einem separaten Script in `scripts/` erzeugt
werden.

## Mapping-Ebenen

### Ebene 1 – Knotenebene
Reale Projektartefakte werden zuerst als Knotenobjekte definiert.

### Ebene 2 – Relationsebene
Zwischen diesen Knoten werden offene Relationen definiert.

### Ebene 3 – Gewichtsebene
Die Stärke dieser Relationen wird als `weight` numerisch festgelegt.

### Ebene 4 – Shell-Ebene
Jeder Knoten erhält eine offene Shell-Zuordnung `shell_index`.

## Zulässige Knotenarten

BMC-08 sollte **nicht** beliebige Mischknoten bauen, sondern klar benannte Knotentypen verwenden.

### Empfohlene Primärknoten
Je nach realem Projektblock sind zulässig:

#### Typ A – Mess- oder Beobachtungseinheiten
Beispiele:
- Frequenz-/Modenpunkte
- Ring-/Cavity-/Membran-Einheiten
- Testfälle / Runs
- Kandidateneinheiten aus vorhandenen Exporten

#### Typ B – bereits aggregierte Strukturträger
Beispiele:
- Familienknoten
- Clusterknoten
- diagnostische Einheiten aus vorgelagerten Blöcken

### Nicht empfohlen als erste BMC-08-Stufe
- Vermischung heterogener Ebenen in einer einzigen Knotentabelle
- künstliche Superknoten ohne klare physikalische oder methodische Rolle
- Knoten, die nur deshalb konstruiert werden, um später ein gewünschtes Arm-Muster zu erzeugen

## Arbeitsregel für die erste Realdatenstufe
Für den ersten offenen BMC-08-Lauf soll die Knotentabelle **möglichst eine einzige klare Objektebene** repräsentieren.

Bevorzugt:
- einheitliche Einheiten
- einheitliche Herkunft
- einheitliche Semantik

## Kantenbildung

## Grundidee
Eine Kante repräsentiert **keine bloße Nachbarschaft im Bauchgefühl**, sondern eine offen beschriebene Relation.

### Zulässige Relationen
- Ähnlichkeit
- Kopplungsstärke
- Distanzumkehr / Nähemaß
- sign-preserving abgeleitete Nähe
- bereits in Vorblöcken definierte relationale Gewichte

### Nicht zulässig ohne offene Dokumentation
- manuelle Kanten nach Eindruck
- informelle Auswahl „sieht passend aus“
- implizite Schwellung im Runner
- Kombination mehrerer Relationen ohne offenes Mischschema

## Gewicht (`weight`)

### Mindestanforderung
`weight` muss ein **offen berechnetes oder offen übernommenes Relationalgewicht** sein.

### Zulässige Quellen
- direkt aus vorhandenen relationalen Projektartefakten
- offen abgeleitete Ähnlichkeits- oder Distanztransformation
- offen dokumentierte Aggregation aus mehreren Teilmaßen

### Dokumentationspflicht
Für jeden Realdatensatz muss in derselben Note oder einem Begleitdokument stehen:

1. Welche Roh- oder Vorstufe benutzt wurde
2. Welche Formel oder Regel `weight` erzeugt
3. Ob vor dem Export normalisiert wurde
4. Ob Voraggregation stattgefunden hat
5. Ob Schwellen oder KNN-Auswahl benutzt wurden

## Empfohlene Mappingmuster für `weight`

### Muster W1 – direktes Relationalgewicht
Wenn eine offene projektinterne Matrix oder Kantenliste bereits existiert.

Beispiel:
- vorhandene gewichtete Beziehung wird direkt übernommen

### Muster W2 – Distanz zu Nähe
Wenn eine Distanzmatrix vorliegt.

Beispielhafte offene Transformation:
- `weight = 1 / (1 + distance)`
- oder andere offen definierte monotone Näheabbildung

### Muster W3 – Sign-sensitive Relation
Wenn positive und negative Beziehungen getrennt behandelt werden.

Dann muss klar dokumentiert sein:
- ob negative Werte ausgeschlossen, transformiert oder in getrennte Datensätze überführt werden
- wie die spätere BMC-08-Kante daraus entsteht

## Shell-Zuordnung (`shell_index`)

## Grundregel
Die Shell-Zuordnung ist **kein dekoratives Label**, sondern ein methodisch tragender Teil des BMC-08-Readouts.
Deshalb muss ihre Herleitung offen und unabhängig genug sein.

## Zulässige Shell-Zuordnungsarten

### S1 – vorbestehende Projekt-Shell
Wenn es im Projekt bereits eine unabhängig definierte Shell-Struktur gibt.

### S2 – offen regelbasierte Shell
Zum Beispiel:
- Distanz zum Referenzkern
- BFS-/Layer-Logik auf einer unabhängig gebauten Grundstruktur
- bestehende Familien-/Ring-/Lagenzuordnung

### S3 – extern oder vorblock-definierte Lageklasse
Wenn Shells aus einem vorgelagerten Block stammen und dort bereits offen dokumentiert wurden.

## Nicht zulässig ohne gesonderte Rechtfertigung
- Shell direkt aus demselben Kriterium bauen, das später nahezu identisch im Readout wieder gemessen wird
- Shell erst nach Blick auf das gewünschte Ergebnis festlegen

## Pflichtdokumentation für Shells
Für jeden Realdatensatz muss dokumentiert werden:

- Regel der Shell-Bildung
- verwendete Inputquelle
- Anzahl Shells
- Sonderbehandlung für Ausreißer oder isolierte Knoten
- warum die Shell-Zuordnung nicht nur nachträgliche Ergebnissteuerung ist

## Optionales `backbone_hint`

## Grundregel
`backbone_hint` ist **optional** und nicht Standard.

Wenn vorhanden, muss separat begründet werden:

- Herkunft
- Erzeugungszeitpunkt
- Unabhängigkeit von den BMC-08-Readouts
- warum kein Readout-Leak vorliegt

## Projektinterne Arbeitsregel
Für den ersten Realdatenlauf bevorzugt:
- **kein** `backbone_hint`
- stattdessen faire Basisvarianten:
  - `strength_topk`
  - `strength_topalpha`

`hint_reference` nur ergänzend, wenn die Herkunft wirklich unabhängig ist.

## Empfohlenes Realdaten-Mapping – erste Stufe

### Ziel
Ein **kleiner, sauberer, echter Realdatensatz** statt sofort maximaler Vollständigkeit.

### Empfohlener Startansatz
- ein klar begrenzter Projektblock
- eine einheitliche Knotensemantik
- eine offen hergeleitete Gewichtung
- eine offen dokumentierte Shell-Zuordnung
- keine readout-nahe Backbone-Vorstruktur

### Minimaler Realdatenlauf sollte leisten
- echter Datentransfer
- offene Provenienz
- Vergleichbarkeit mit BMC-07c/BMC-07d
- keine unnötige Modelllast

## Empfohlene Dokumente, die aus dieser Note folgen

### 1. `docs/BMC08_dataset_manifest_template.md`
Vorlage für Herkunft, Version und Regeln des Realdatensatzes

### 2. `scripts/build_bmc08_realdata_inputs.py`
Offenes Bauscript für
- `data/baseline_relational_table_real.csv`
- `data/node_metadata_real.csv`
- optional `data/bmc08_dataset_manifest.json`

### 3. `data/bmc08_realdata_config.yaml`
Realdatenkonfiguration für den ersten offenen Lauf

## Konkretes Mapping-Schema für spätere Dateien

### Ziel-Datei: `data/baseline_relational_table_real.csv`
Jede Zeile braucht mindestens:
- `source`
- `target`
- `weight`

Zusätzlich empfohlen:
- `edge_family`
- `relation_type`
- `evidence_tag`
- `comment`

### Ziel-Datei: `data/node_metadata_real.csv`
Jede Zeile braucht mindestens:
- `node_id`
- `shell_index`

Zusätzlich empfohlen:
- `node_label`
- `node_family`
- `origin_tag`
- `comment`

## Methodische No-Go-Zonen

### NG1 – Runner baut heimlich Kanten
Nicht zulässig. Kantenbildung muss vorab dokumentiert und exportiert werden.

### NG2 – Shell-Zuordnung wird im Runner implizit rekonstruiert
Nicht zulässig.

### NG3 – Backbone-Definition wird aus dem gewünschten BMC-08-Ergebnis zurückgerechnet
Nicht zulässig.

### NG4 – Realdaten werden im Namen „clean“ oder „filtered“ verändert, ohne dokumentierte Regel
Nicht zulässig.

## Praktische Arbeitsreihenfolge

### Schritt 1
Knotensemantik festlegen:
- Was ist eine Einheit?

### Schritt 2
Relationsregel festlegen:
- Warum gibt es zwischen zwei Knoten eine Kante?

### Schritt 3
Gewichtsregel festlegen:
- Wie genau entsteht `weight`?

### Schritt 4
Shell-Regel festlegen:
- Wie entsteht `shell_index`?

### Schritt 5
Offene Dateien bauen:
- `baseline_relational_table_real.csv`
- `node_metadata_real.csv`
- optional Manifest

### Schritt 6
Erst danach:
- Config
- Runner
- Run-Script
- Lauf

## Befund
Noch keiner. Diese Note ist reine Mapping-Spezifikation.

## Interpretation
Die Note sorgt dafür, dass BMC-08 nicht als stiller Datentransformationsblock entgleist.
Sie macht aus „wir haben echte Daten“ einen offen prüfbaren Mappingvertrag.

## Hypothese
Wenn wir Knoten, Kanten, Gewicht und Shell-Zuordnung offen und unabhängig genug definieren,
kann BMC-08 denselben Vertrauensstandard halten wie der Minimalblock.

## Offene Lücke
Es fehlen noch:
- die konkrete Wahl des ersten realen Projektblocks
- die tatsächliche Mappingentscheidung für Knoten und Kanten
- das offene Build-Script für die Realdatendateien

## Feldliste – empfohlene spätere Manifestdatei
- `dataset_id` — string — Kennung des Realdatensatzes.
- `dataset_version` — string — Version oder Datumsstand.
- `node_semantics` — string — Beschreibung der Knotensemantik.
- `edge_semantics` — string — Beschreibung der Relationssemantik.
- `weight_rule` — string — Regel zur Bildung von `weight`.
- `shell_rule` — string — Regel zur Bildung von `shell_index`.
- `backbone_hint_origin` — string|null — Herkunft eines optionalen Backbone-Hints.
- `source_artifacts` — list[string] — Herkunftsdateien oder Vorblöcke.
- `notes` — list[string] — freie methodische Hinweise.
