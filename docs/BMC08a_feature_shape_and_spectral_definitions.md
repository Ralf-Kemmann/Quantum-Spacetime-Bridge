# BMC-08a – Definition von `feature_shape_factor` und `feature_spectral_index`

## Status
Spezifikationsschritt vor Build-Script.

## Zweck
Diese Datei präzisiert die beiden in BMC-08a noch offenen Merkmale:

- `feature_shape_factor`
- `feature_spectral_index`

Ziel ist eine **kleine, offene, family-übergreifend lesbare und methodisch faire** Definition,
die für den ersten Realdatenlauf verwendbar ist, ohne schon eine readout-nahe Meta-Logik einzubauen.

## Ausgangspunkt

### Letzter belastbarer Stand
Die kleine offene BMC-08a-Featureliste umfasst:

- `feature_mode_frequency`
- `feature_length_scale`
- `feature_shape_factor`
- `feature_spectral_index`

Offen waren bisher die konkreten Definitionen von
`feature_shape_factor` und `feature_spectral_index`.

### Kernanforderung
Beide Merkmale müssen:

1. offen definierbar sein
2. family-übergreifend lesbar bleiben
3. keine Blackbox sein
4. nicht bloß spätere BMC-Readouts in anderer Verpackung darstellen
5. für Ring / Cavity / Membrane mit derselben Grundlogik formulierbar sein

---

## 1. Definition von `feature_shape_factor`

## Zielidee
`feature_shape_factor` soll eine **einfache dimensionslose Form- bzw. Strukturkennzahl** sein,
die eine reale Einheit grob charakterisiert, ohne schon hochaggregierte Modelllogik einzubauen.

## Arbeitsdefinition
Für BMC-08a Version 1 wird `feature_shape_factor` als

**dimensionsloses Verhältnis aus Hauptausdehnung zu Nebenausdehnung**

definiert:

`feature_shape_factor = L_major / L_minor`

mit:
- `L_major > 0`
- `L_minor > 0`
- und per Definition `L_major >= L_minor`

Damit gilt immer:
- `feature_shape_factor >= 1`

## Interpretation
- Werte nahe `1` → eher kompakt / rund / isotrop
- höhere Werte → eher länglich / anisotrop / ausgedehnt

## Family-übergreifende Lesart
### Ring
- `L_major`: äußerer charakteristischer Durchmesser oder Hauptausdehnung
- `L_minor`: Ringbreite, effektive Querschnittsskala oder sekundäre Ausdehnung

### Cavity
- `L_major`: dominante Kavitätslänge
- `L_minor`: kleinere Quer- oder Nebenachse

### Membrane
- `L_major`: größte charakteristische Ausdehnung
- `L_minor`: kleinere charakteristische Nebenachse oder effektive zweite Lagenskala

## Warum diese Regel?
- dimensionslos
- transparent
- einfach zu berechnen
- family-übergreifend verwendbar
- keine direkte Nähe zu späteren Lokalisierungsreadouts

## Wichtige methodische Einschränkung
Die konkrete Wahl von `L_major` und `L_minor` muss **vorab offen dokumentiert** sein.
Nicht zulässig:
- die Achsen nach Blick auf das gewünschte Ergebnis auswählen
- pro Familie völlig unterschiedliche Logiken verwenden, ohne dies offen zu harmonisieren

## Falls keine zwei Achsen offen vorliegen
Dann sind zulässige Ersatzdefinitionen nur, wenn sie offen dokumentiert werden, z. B.:
- `max_extent / min_extent`
- `diameter / thickness`
- `span / width`

### Nicht zulässig
- zusammengesetzte verdeckte Formscores
- learned shape embeddings
- nachträgliche „optimierte“ Anisotropiekennzahlen

---

## 2. Definition von `feature_spectral_index`

## Zielidee
`feature_spectral_index` soll eine **kleine offene spektrale Ordnungszahl** sein,
die eine Einheit spektral einordnet, ohne gleich komplexe Spektraldiagnostik einzuschleusen.

## Arbeitsdefinition
Für BMC-08a Version 1 wird `feature_spectral_index` als

**indexartige Kennzahl der gewählten repräsentativen Mode / Spektralstufe**

definiert.

### Basale Regel
- Wenn eine eindeutig definierte Haupt- oder Referenzmode vorliegt:
  - verwende deren offenen Modenindex als Zahl
- Wenn stattdessen eine geordnete Spektralstufe vorliegt:
  - verwende die offene Rangposition / Stufe dieser Repräsentantmode

## Startform
`feature_spectral_index = m_ref`

wobei `m_ref` die **offen dokumentierte Referenzmode** ist.

Beispiele:
- Grundmode → `1`
- zweite Referenzmode → `2`
- dritte Referenzmode → `3`

## Interpretation
- kleine Werte → tiefer / fundamentaler Spektralbereich
- größere Werte → höhere Ordnungs- oder Anregungsstufe

## Family-übergreifende Lesart
### Ring
- Referenzmode nach offen gewählter Ringmode-Ordnung

### Cavity
- Referenzmode nach offen gewählter Cavity-Mode-Ordnung

### Membrane
- Referenzmode nach offen gewählter Membranmode-Ordnung

## Warum diese Regel?
- sehr einfach
- keine Blackbox
- spektral interpretierbar
- trennt Frequenzhöhe (`feature_mode_frequency`) von Ordnungsposition (`feature_spectral_index`)

## Wichtige methodische Einschränkung
Die Wahl von `m_ref` muss **einheitlich und ex ante** erfolgen.

### Zulässig
- immer Grundmode
- immer dominante Hauptmode nach fester Regel
- immer niedrigste stabile Referenzmode nach offener Regel

### Nicht zulässig
- pro Einheit die Mode wählen, die später die beste Trennung erzeugt
- pro Familie unterschiedliche Auswahl ohne Dokumentation
- ein readout-naher zusammengesetzter Spektralscore statt einer offenen Indexzahl

---

## 3. Zusammenspiel mit den anderen BMC-08a-Features

## `feature_mode_frequency`
liefert die kontinuierliche Lage des repräsentativen Spektralpunkts

## `feature_spectral_index`
liefert die diskrete oder ordinal interpretierbare Einordnung dieses Spektralpunkts

## `feature_length_scale`
liefert einfache Größeninformation

## `feature_shape_factor`
liefert einfache Form-/Anisotropieinformation

## Projektinterne Lesart
Die vier Merkmale sollen **nicht maximal stark**, sondern **minimal hinreichend und offen lesbar** sein.

---

## 4. Konkrete Startregeln für BMC-08a Version 1

### Regel SF1 – `feature_shape_factor`
Verwende:

`feature_shape_factor = L_major / L_minor`

mit offen dokumentierter Achsenwahl pro Familie.

### Regel SI1 – `feature_spectral_index`
Verwende:

`feature_spectral_index = m_ref`

wobei `m_ref` der offen festgelegte Referenzmodenindex ist.

### Empfohlene Startentscheidung
Für den ersten BMC-08a-Lauf:
- `m_ref = 1`, falls eine Grundmode sauber verfügbar ist
- sonst die niedrigste offen und konsistent bestimmbare Referenzmode

---

## 5. Beispielzeilen

```csv
node_id,node_family,node_label,feature_mode_frequency,feature_length_scale,feature_shape_factor,feature_spectral_index,origin_tag,comment
ring_001,RING,Ring-001,12.4,4.8,1.08,1,m39x1_export,baseline ring with fundamental mode
ring_002,RING,Ring-002,13.1,5.0,1.11,2,m39x1_export,ring with second reference mode
cavity_001,CAVITY,Cavity-001,8.7,7.2,1.35,1,m39x1_export,baseline cavity
membrane_001,MEMBRANE,Membrane-001,5.4,6.8,1.82,3,m39x1_export,membrane with third reference mode
```

---

## 6. Sanity-Checks vor dem Build

### Für `feature_shape_factor`
1. `L_major` und `L_minor` sind offen dokumentiert
2. beide Größen sind positiv
3. `L_major >= L_minor`
4. `feature_shape_factor >= 1`
5. keine stillen familienabhängigen Sondertricks

### Für `feature_spectral_index`
1. `m_ref` ist offen dokumentiert
2. Auswahlregel ist für alle Einheiten konsistent
3. `m_ref` ist numerisch interpretierbar
4. keine nachträgliche Auswahl nach Ergebnisinteresse
5. Frequenz und Index sind nicht unklar doppelt belegt

---

## 7. Failure Modes

### F1 – `shape_factor` wird zu einer versteckten Sammelkennzahl
Nicht zulässig. Er muss bei BMC-08a auf einer einfachen Verhältnisdefinition bleiben.

### F2 – `spectral_index` wird faktisch aus einem komplexen Ranking recycelt
Nicht zulässig, wenn dieses Ranking selbst schon stark modelliert ist.

### F3 – Family-spezifische Bedeutungen driften auseinander
Wenn `shape_factor` oder `spectral_index` in Ring, Cavity und Membrane faktisch ganz andere Dinge bedeuten,
muss das vorab offen harmonisiert werden.

### F4 – Referenzmode wird pro Einheit opportunistisch gewählt
Nicht zulässig.

### F5 – Merkmale werden im Runner statt im Build-Script erzeugt
Nicht zulässig.

---

## 8. Praktische nächste Ableitung

Aus dieser Definition folgt als nächster Schritt:

### spätere Build-Inputdatei
`data/bmc08a_real_units_feature_table.csv`

mit mindestens:
- `node_id`
- `node_family`
- `node_label`
- `feature_mode_frequency`
- `feature_length_scale`
- `feature_shape_factor`
- `feature_spectral_index`
- `origin_tag`
- `comment`

### begleitend in `docs/`
sollte dokumentiert werden:
- wie `L_major` und `L_minor` pro Familie bestimmt wurden
- welche Referenzmode-Regel für `m_ref` gilt

---

## Befund
Noch keiner. Diese Datei präzisiert nur zwei offene BMC-08a-Merkmale.

## Interpretation
Mit diesen Definitionen wird die kleine offene Featureliste jetzt konkret genug,
um in ein offenes Build-Script überführt zu werden.

## Hypothese
Wenn bereits diese einfachen Definitionsregeln ein tragfähiges Realdatenmapping ermöglichen,
bleibt BMC-08a methodisch fair und trotzdem strukturell aussagekräftig genug für einen ersten echten Transferlauf.

## Offene Lücke
Noch fehlen:
- die konkrete family-spezifische Festlegung von `L_major` und `L_minor`
- die konkrete Referenzmode-Regel für den gewählten Exportblock
- das offene Build-Script
- die Realdaten-Manifestdatei
- die Realdaten-Config

## Feldliste – ergänzende spätere Dokumentationsfelder
- `shape_factor_rule_id` — string — Kennung der verwendeten `shape_factor`-Regel
- `spectral_index_rule_id` — string — Kennung der verwendeten `spectral_index`-Regel
- `l_major_definition` — string — konkrete Definition von `L_major`
- `l_minor_definition` — string — konkrete Definition von `L_minor`
- `reference_mode_rule` — string — konkrete Regel zur Wahl von `m_ref`
