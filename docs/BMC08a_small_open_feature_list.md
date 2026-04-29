# BMC-08a – Kleine offene Featureliste

## Status
Spezifikationsschritt vor Build-Script.

## Zweck
Diese Datei legt die **kleine offene Featureliste** für den ersten BMC-08a-Realdatenlauf fest.

Sie beantwortet konkret:

- welche Basismerkmale pro Einheit verwendet werden,
- warum genau diese Merkmale gewählt werden,
- welche Merkmale **bewusst nicht** in den ersten Lauf eingehen,
- und wie daraus später ein offener Featurevektor für
  `Ring / Cavity / Membrane` gebaut wird.

## Ausgangspunkt

### Letzter belastbarer Befund
BMC-08a ist als konkreter Mappingblock für
- `RING`
- `CAVITY`
- `MEMBRANE`

festgelegt.

Die erste Startregel lautet:
- Knoten = einzelne reale Instanzen
- Kanten = vollständiger gewichteter ungerichteter Graph
- Gewicht = Distanz-zu-Nähe-Abbildung auf standardisierten Basisfeatures
- Shell = Familien-Shell (`RING=0`, `CAVITY=1`, `MEMBRANE=2`)

### Offene Kernfrage
Welche kleine Merkmalsmenge ist für den ersten offenen Realdatenlauf
- interpretierbar,
- nicht zu modelllastig,
- nicht readout-nah,
- und trotzdem strukturell aussagekräftig genug?

## Grundregel
Für BMC-08a werden **nur wenige, direkt lesbare und offen verfügbare Basismerkmale** verwendet.

Nicht Ziel:
- maximale Vorhersagekraft
- maximale Trennschärfe
- möglichst „schöne“ Cluster

Ziel:
- offene, faire und reproduzierbare erste Realdatenbasis

## Auswahlprinzipien

Ein Merkmal darf in die erste kleine Featureliste eingehen, wenn es:

1. **direkt interpretierbar** ist  
   also physikalisch oder strukturell lesbar bleibt

2. **einheitlich für Ring, Cavity und Membrane definierbar** ist

3. **nicht bereits selbst ein BMC-07x/08-Readout** oder ein naher Surrogat-Proxy davon ist

4. **in offener Form vorliegt oder offen berechnet werden kann**

5. **nicht erst durch komplexe Modellketten** erzeugt werden muss

## Kleine offene Startliste (Version 1)

Die Startliste enthält **vier Merkmale**.

### F1 – charakteristische Frequenz- oder Modenlage
**Feldname:** `feature_mode_frequency`

**Typ:** float

**Bedeutung:**  
Eine offen lesbare charakteristische Frequenz, Eigenfrequenz oder Modenlage der Einheit.

**Warum drin?**
- physikalisch direkt interpretierbar
- für Ring / Cavity / Membrane natürlich lesbar
- geringe methodische Willkür

**Hinweis:**  
Falls mehrere Moden vorliegen, muss im Mappingdokument offen festgelegt werden,
welche repräsentative Modenlage gewählt wird
(z. B. Grundmode oder definierte Hauptmode).

---

### F2 – charakteristische Längenskala
**Feldname:** `feature_length_scale`

**Typ:** float

**Bedeutung:**  
Eine offen definierte Größen- oder Längenskala der Einheit.

**Beispiele:**
- Ringradius
- charakteristische Cavity-Länge
- charakteristische Membran-Ausdehnung

**Warum drin?**
- einfache, physikalisch lesbare Geometriegröße
- family-übergreifend gut interpretierbar
- nicht readout-nah

---

### F3 – geometrisch-strukturelle Formkennzahl
**Feldname:** `feature_shape_factor`

**Typ:** float

**Bedeutung:**  
Eine kleine, offen definierte dimensionslose Form- oder Strukturkennzahl.

**Beispiele:**
- normiertes Aspektverhältnis
- offene Symmetrie-/Formzahl
- einfache geometrische Kompaktheitskennzahl

**Warum drin?**
- ergänzt reine Größen- und Frequenzinfo
- erlaubt eine erste strukturelle Differenzierung
- bleibt bei guter Definition noch transparent

**Wichtige Regel:**  
Die Kennzahl muss **einfach** und **offen dokumentiert** sein.
Keine versteckten zusammengesetzten Scores.

---

### F4 – einfache spektrale Ordnungszahl
**Feldname:** `feature_spectral_index`

**Typ:** float

**Bedeutung:**  
Eine kleine, offen definierte numerische Kennzahl zur spektralen Lage oder Ordnung.

**Beispiele:**
- normierter Modenindex
- einfache Energienähezahl
- offen gewählte Spektralklasse in numerischer Form

**Warum drin?**
- ergänzt die reine Frequenzlage um eine zweite spektrale Perspektive
- kann Unterschiede zwischen Ring / Cavity / Membrane besser öffnen
- bleibt noch deutlich einfacher als hochaggregierte Projektprädiktoren

## Bewusst nicht in Version 1 enthalten

### Nicht aufnehmen
- `distance_to_type_D`
- `spacing_cv`
- `simple_rigidity_surrogate`
- `grid_deviation_score`
- andere stark projektinterne Meta-Features aus späteren Prädiktorblöcken

## Begründung
Diese Größen sind für spätere Blöcke wertvoll, aber für den **ersten offenen Realdatenlauf** zu nahe an bereits aggregierter Modelllogik.

### Ebenfalls nicht aufnehmen
- zusammengesetzte Mischscores
- latent gelernte Embeddings
- Kernel- oder UMAP-/TSNE-artige Projektionen
- Merkmale, die erst nach Blick auf gewünschte Clusterstruktur ausgewählt werden

## Zielformat für spätere Build-Inputtabelle

### Empfohlene Datei
`data/bmc08a_real_units_feature_table.csv`

### Pflichtfelder
- `node_id`
- `node_family`
- `node_label`
- `feature_mode_frequency`
- `feature_length_scale`
- `feature_shape_factor`
- `feature_spectral_index`

### Empfohlene Zusatzfelder
- `origin_tag`
- `comment`

## Feldliste
- `node_id` — string — eindeutige Einheitenkennung.
- `node_family` — string — Familie (`RING`, `CAVITY`, `MEMBRANE`).
- `node_label` — string — lesbarer Name.
- `feature_mode_frequency` — float — charakteristische Frequenz-/Modenlage.
- `feature_length_scale` — float — charakteristische Längenskala.
- `feature_shape_factor` — float — einfache dimensionslose Strukturkennzahl.
- `feature_spectral_index` — float — einfache spektrale Ordnungszahl.
- `origin_tag` — string — Herkunftsmarkierung.
- `comment` — string — optionale Kurzbeschreibung.

## Standardisierung

## Regel
Die Featurestandardisierung erfolgt **nicht im Runner**, sondern offen im späteren Build-Script.

### Vorgeschlagene Startregel
Für jedes numerische Feature:
- z-Standardisierung über alle im BMC-08a-Lauf verwendeten Einheiten

`z = (x - mean) / std`

## Warum?
- offen
- einfach
- reproduzierbar
- keine stille Skalierung im Runner

## Umgang mit fehlenden Werten
Für BMC-08a Version 1 gilt:

### harte Regel
Einheiten mit fehlenden Pflichtmerkmalen dürfen **nicht still imputiert** werden.

Stattdessen:
- entweder vor dem Build offen ausschließen
- oder die fehlenden Werte in einer Vorstufe offen ergänzen und dokumentieren

## Praktische Arbeitsregel
Für den ersten Lauf lieber:
- kleinerer, vollständiger Datensatz
als
- größerer, halbimputierter Datensatz

## Beispielzeilen

```csv
node_id,node_family,node_label,feature_mode_frequency,feature_length_scale,feature_shape_factor,feature_spectral_index,origin_tag,comment
ring_001,RING,Ring-001,12.4,4.8,1.00,1,m39x1_export,baseline ring
ring_002,RING,Ring-002,13.1,5.0,0.97,2,m39x1_export,baseline ring
cavity_001,CAVITY,Cavity-001,8.7,7.2,1.35,1,m39x1_export,baseline cavity
membrane_001,MEMBRANE,Membrane-001,5.4,6.8,1.82,3,m39x1_export,baseline membrane
```

## Sanity-Checks vor dem Build
1. Jede Einheit hat alle vier Pflichtfeatures.
2. Alle Features sind numerisch und endlich.
3. Jede Einheit gehört genau einer Familie an.
4. Frequenz- und Längenskala sind in offener physikalischer Einheit dokumentiert.
5. `shape_factor` und `spectral_index` sind offen definiert.
6. Keine stillen Imputationen.
7. Keine nachträgliche Merkmalsselektion nach Blick auf das Ergebnis.

## Failure Modes

### F1 – Readout-nahe Featureeinschleusung
Merkmale werden aufgenommen, die faktisch schon spätere Lokalisierungslogik tragen.

### F2 – Zu heterogene Featurebedeutung
Dasselbe Feld bedeutet in Ring, Cavity und Membrane faktisch etwas ganz anderes, ohne dokumentierte Harmonisierung.

### F3 – Versteckte Standardisierung
Skalierung oder Clipping passiert im Runner statt offen im Build-Script.

### F4 – Fehlwerte werden still ersetzt
Nicht zulässig.

### F5 – Featureliste wächst unkontrolliert
BMC-08a soll klein bleiben; zusätzliche Merkmale gehören in spätere Erweiterungsblöcke.

## Projektinterne Lesart der Startliste
Diese Vierer-Liste ist **keine optimale Featureliste**, sondern eine **faire Startliste**.

Sie soll:
- strukturell ausreichen,
- physikalisch lesbar bleiben,
- und methodisch nicht schon das Ergebnis vorprägen.

## Befund
Noch keiner. Diese Datei definiert nur die offene kleine Featureliste.

## Interpretation
Mit dieser Startliste ist BMC-08a erstmals konkret genug, um ein offenes Build-Script für reale Inputdateien zu schreiben.

## Hypothese
Wenn bereits diese kleine, faire und physikalisch lesbare Featurebasis ein konsistentes Lokalisierungsmuster erzeugt, ist das methodisch stärker als ein Effekt, der erst mit hochaggregierten Meta-Features auftaucht.

## Offene Lücke
Noch fehlen:
- die konkrete Definition von `feature_shape_factor`
- die konkrete Definition von `feature_spectral_index`
- die offene Build-Datei
- die Realdaten-Manifestdatei
- die Realdaten-Config

## Feldliste – spätere Manifestergänzung
Zusätzlich zur Manifestdatei sollten dort für BMC-08a dokumentiert sein:
- `feature_set_id` — string — Kennung der verwendeten offenen Featureliste.
- `feature_mode_frequency_rule` — string — Regel zur Wahl der repräsentativen Frequenz.
- `feature_length_scale_rule` — string — Regel zur Wahl der Längenskala.
- `feature_shape_factor_rule` — string — offene Definition der Formkennzahl.
- `feature_spectral_index_rule` — string — offene Definition der spektralen Ordnungszahl.
