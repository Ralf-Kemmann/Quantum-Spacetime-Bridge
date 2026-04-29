# BMC-08a – Family-spezifische Festlegung von `L_major`, `L_minor` und `m_ref`

## Status
Spezifikationsschritt vor Build-Script.

## Zweck
Diese Datei legt für den gewählten BMC-08a-Exportblock **familiespezifisch und offen** fest,

- wie `L_major` bestimmt wird,
- wie `L_minor` bestimmt wird,
- und wie die Referenzmode `m_ref` für `feature_spectral_index` gewählt wird.

Damit werden die noch offenen Definitionsstellen aus
`BMC08a_feature_shape_and_spectral_definitions.md`
auf die erste reale Startversion heruntergebrochen.

## Ausgangspunkt

### Letzter belastbarer Stand
Für BMC-08a gilt derzeit:
- `feature_shape_factor = L_major / L_minor`
- `feature_spectral_index = m_ref`

Noch offen war die familiespezifische Festlegung für den ersten realen Exportblock:
- `RING`
- `CAVITY`
- `MEMBRANE`

### Kernanforderung
Die Festlegung muss:
1. offen und klein sein
2. pro Familie lesbar bleiben
3. nicht opportunistisch nach Ergebnisinteresse gewählt werden
4. über alle Einheiten derselben Familie konsistent angewendet werden

## Grundregel
Die folgende Festlegung ist eine **Startregel für Version 1**.
Sie ist bewusst defensiv, nicht maximal raffiniert.

Die Arbeitsmaxime lautet:
- lieber grob, klar und konsistent
- als fein, clever und legitimatorisch heikel

---

## 1. Familie `RING`

## Semantische Lesart
Ringe werden in BMC-08a als Einheiten mit einer dominanten Umfangs-/Durchmesserstruktur
und einer sekundären Breiten- bzw. Querschnittsstruktur behandelt.

### `L_major` für `RING`
**Definition:**  
charakteristischer äußerer Ringdurchmesser  
oder, falls im Export so vorliegend, die dazu äquivalente dominante Hauptausdehnung.

**Zielfeld im Vorblock / Export:**  
z. B. `outer_diameter` oder `major_extent`

### `L_minor` für `RING`
**Definition:**  
charakteristische Ringbreite, Querschnittsbreite oder sekundäre laterale Ausdehnung.

**Zielfeld im Vorblock / Export:**  
z. B. `ring_width`, `cross_section_width` oder `minor_extent`

### `m_ref` für `RING`
**Definition:**  
der offen definierte Referenzmodenindex der Ringeinheit.

### Startregel R-M1
Für BMC-08a Version 1:
- wenn die Grundmode sauber vorliegt → `m_ref = 1`
- wenn keine eindeutig ausgewiesene Grundmode vorliegt:
  - wähle die **niedrigste offen und konsistent verfügbare Referenzmode**
  - dokumentiere diese Regel explizit im Manifest

### Kurzform
- `L_major(RING) = outer_diameter`
- `L_minor(RING) = ring_width`
- `m_ref(RING) = fundamental_mode_index if available else lowest_consistent_reference_mode`

---

## 2. Familie `CAVITY`

## Semantische Lesart
Cavities werden als Einheiten mit einer dominanten Hohlraum- oder Resonatorlänge
und einer kleineren Quer- oder Nebenachse gelesen.

### `L_major` für `CAVITY`
**Definition:**  
dominante Kavitätslänge bzw. größte charakteristische Hauptausdehnung des Resonatorraums.

**Zielfeld im Vorblock / Export:**  
z. B. `cavity_length` oder `major_extent`

### `L_minor` für `CAVITY`
**Definition:**  
kleinere Querachse, Nebenlänge oder kleinere charakteristische Ausdehnung.

**Zielfeld im Vorblock / Export:**  
z. B. `cavity_width`, `transverse_extent` oder `minor_extent`

### `m_ref` für `CAVITY`
**Definition:**  
offen definierter Referenzmodenindex der Cavity.

### Startregel C-M1
Für BMC-08a Version 1:
- wenn die Cavity-Grundmode offen ausgewiesen ist → `m_ref = 1`
- sonst:
  - verwende die niedrigste konsistent definierte Referenzmode
  - nicht die „schönste“ oder „trennstärkste“ Mode

### Kurzform
- `L_major(CAVITY) = cavity_length`
- `L_minor(CAVITY) = cavity_width`
- `m_ref(CAVITY) = fundamental_mode_index if available else lowest_consistent_reference_mode`

---

## 3. Familie `MEMBRANE`

## Semantische Lesart
Membranen werden als flächige Einheiten mit einer größten Hauptausdehnung
und einer kleineren sekundären Ausdehnung gelesen.

### `L_major` für `MEMBRANE`
**Definition:**  
größte charakteristische Membran-Ausdehnung in der Ebene.

**Zielfeld im Vorblock / Export:**  
z. B. `membrane_span`, `major_extent` oder `largest_in_plane_extent`

### `L_minor` für `MEMBRANE`
**Definition:**  
kleinere charakteristische Neben- oder Quer-Ausdehnung in der Ebene.

**Zielfeld im Vorblock / Export:**  
z. B. `membrane_width`, `minor_extent` oder `secondary_in_plane_extent`

### `m_ref` für `MEMBRANE`
**Definition:**  
offen definierter Referenzmodenindex der Membran.

### Startregel M-M1
Für BMC-08a Version 1:
- Grundmode verwenden, wenn offen verfügbar
- sonst die niedrigste konsistent bestimmbare Referenzmode

### Kurzform
- `L_major(MEMBRANE) = membrane_span`
- `L_minor(MEMBRANE) = membrane_width`
- `m_ref(MEMBRANE) = fundamental_mode_index if available else lowest_consistent_reference_mode`

---

## 4. Harmonisierung über Familien hinweg

## Ziel
Obwohl die Familien physikalisch verschieden sind, müssen die drei Regeln
**dieselbe methodische Form** behalten.

### Einheitliche BMC-08a-Regel
Für jede Familie gilt:

- `L_major` = größte offen dokumentierte Hauptausdehnung
- `L_minor` = kleinere offen dokumentierte Neben- oder Quer-Ausdehnung
- `m_ref` = Grundmode, falls offen verfügbar; sonst niedrigste konsistent definierte Referenzmode

## Warum das wichtig ist
Damit vermeiden wir:
- family-spezifische Speziallogik nur für bessere Trennung
- implizite Ergebnissteuerung
- schwer verteidigbare Inkompatibilitäten zwischen Familien

---

## 5. Konkrete Ableitungsregeln für das spätere Build-Script

## Regel A – `feature_shape_factor`
Für jede Einheit:

`feature_shape_factor = L_major / L_minor`

mit:
- `L_major > 0`
- `L_minor > 0`
- falls im Export `L_major < L_minor`, dann vor Berechnung offen tauschen:
  - `L_major, L_minor = max, min`

## Regel B – `feature_spectral_index`
Für jede Einheit:

`feature_spectral_index = m_ref`

wobei:
- `m_ref` numerisch sein muss
- dieselbe family-spezifische Referenzregel offen angewendet wird
- keine nachträgliche Optimierung pro Einzelobjekt stattfindet

---

## 6. Beispielhafte Mappingtabelle für den Build

| node_family | L_major source | L_minor source | m_ref rule |
|---|---|---|---|
| `RING` | `outer_diameter` | `ring_width` | Grundmode, sonst niedrigste konsistente Referenzmode |
| `CAVITY` | `cavity_length` | `cavity_width` | Grundmode, sonst niedrigste konsistente Referenzmode |
| `MEMBRANE` | `membrane_span` | `membrane_width` | Grundmode, sonst niedrigste konsistente Referenzmode |

---

## 7. Beispielzeilen für spätere Build-Inputtabelle

```csv
node_id,node_family,node_label,L_major_raw,L_minor_raw,m_ref_raw,feature_mode_frequency,feature_length_scale,origin_tag,comment
ring_001,RING,Ring-001,4.8,4.4,1,12.4,4.8,m39x1_export,baseline ring
ring_002,RING,Ring-002,5.0,4.5,2,13.1,5.0,m39x1_export,ring second reference mode
cavity_001,CAVITY,Cavity-001,7.2,5.3,1,8.7,7.2,m39x1_export,baseline cavity
membrane_001,MEMBRANE,Membrane-001,6.8,3.7,3,5.4,6.8,m39x1_export,membrane third reference mode
```

Daraus ergibt sich im Build:
- `feature_shape_factor = L_major_raw / L_minor_raw`
- `feature_spectral_index = m_ref_raw`

---

## 8. Sanity-Checks vor Export

### Für `L_major` / `L_minor`
1. beide Werte sind numerisch und endlich
2. beide Werte sind positiv
3. `L_major >= L_minor`
4. gleiche family-spezifische Regel für alle Einheiten der Familie
5. keine ad-hoc-Ausnahmefälle ohne Dokumentation

### Für `m_ref`
1. `m_ref` ist numerisch interpretierbar
2. dieselbe Referenzregel gilt innerhalb einer Familie konsistent
3. keine Einzelwahl nach gewünschtem Ergebnis
4. Modeauswahl ist im Manifest offen beschrieben

---

## 9. Failure Modes

### F1 – Familienregel driftet innerhalb der Familie
Nicht zulässig. Alle Ringe müssen derselben RING-Regel folgen usw.

### F2 – `L_major` und `L_minor` werden pro Einzelfall opportunistisch umdefiniert
Nicht zulässig.

### F3 – `m_ref` wird pro Objekt auf maximale Trennung gewählt
Nicht zulässig.

### F4 – Rohfelder sind nicht wirklich vergleichbar
Wenn `outer_diameter`, `cavity_length`, `membrane_span` völlig verschiedene Messlogiken haben,
muss diese Heterogenität im Mappingdokument offen angesprochen werden.

### F5 – Family-spezifische Regeln werden zu komplex
BMC-08a Version 1 soll einfach bleiben.
Feinere Sonderregeln gehören in spätere Ausbauphasen.

---

## 10. Empfohlene Manifestergänzung

Für `data/bmc08_dataset_manifest.json` sollten zusätzlich dokumentiert werden:

- `ring_l_major_rule` — string — z. B. `outer_diameter`
- `ring_l_minor_rule` — string — z. B. `ring_width`
- `ring_m_ref_rule` — string — z. B. `fundamental_mode_or_lowest_consistent_reference`

- `cavity_l_major_rule` — string — z. B. `cavity_length`
- `cavity_l_minor_rule` — string — z. B. `cavity_width`
- `cavity_m_ref_rule` — string — z. B. `fundamental_mode_or_lowest_consistent_reference`

- `membrane_l_major_rule` — string — z. B. `membrane_span`
- `membrane_l_minor_rule` — string — z. B. `membrane_width`
- `membrane_m_ref_rule` — string — z. B. `fundamental_mode_or_lowest_consistent_reference`

---

## Befund
Noch keiner. Diese Datei fixiert nur die familiespezifische Ableitungsregel.

## Interpretation
Mit dieser Festlegung ist BMC-08a jetzt konkret genug,
um ein offenes Build-Script auf einen realen Exportblock anzusetzen.

## Hypothese
Wenn schon unter diesen groben, fairen und family-konsistenten Regeln ein interpretierbares Muster auftritt,
ist das methodisch viel stärker als ein Effekt, der erst unter feinoptimierten Sonderdefinitionen erscheint.

## Offene Lücke
Noch fehlen:
- die tatsächlich ausgewählten Rohfeldnamen des Exportblocks
- das offene Build-Script
- die Manifestdatei
- die Realdaten-Config

## Feldliste – empfohlene Build-Vorstufe
- `node_id` — string — Einheitenkennung
- `node_family` — string — `RING`, `CAVITY`, `MEMBRANE`
- `node_label` — string — lesbarer Name
- `L_major_raw` — float — familiespezifisch definierte Hauptausdehnung
- `L_minor_raw` — float — familiespezifisch definierte Neben- oder Quer-Ausdehnung
- `m_ref_raw` — float|int — Referenzmodenindex
- `feature_mode_frequency` — float — repräsentative Modenfrequenz
- `feature_length_scale` — float — charakteristische Längenskala
- `origin_tag` — string — Herkunft des Blocks
- `comment` — string — optionale Bemerkung
