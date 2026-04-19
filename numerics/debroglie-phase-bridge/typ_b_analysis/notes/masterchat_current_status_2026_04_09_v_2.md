# MASTERCHAT CURRENT STATUS — 2026-04-09

## Projekt
**Spacetime Dynamics from a Wave-Based Perspective**

---

## 1. Arbeitsmodus / interne Regeln

### 1.1 Arbeitsstil
- kleine, belastbare Tests vor großen Behauptungen
- klare Trennung zwischen technischem Pipeline-Erfolg und inhaltlichem Befund
- transparente Benennung von `supported / partially_supported / inconclusive / failed`
- keine implizite Überinterpretation von Adapter- oder Schwellenartefakten
- interne Sprache gerne direkt und maschinenraumtauglich, nach außen defensiv und sauber

### 1.2 Transparenzdisziplin
- technische Läufe ohne brauchbare Inputs gelten **nicht** als physikalische Gegenbefunde
- Adaptertests werden als **operative / diagnostische** Schicht behandelt, nicht als physikalisch privilegierte Wahrheit
- wenn ein Befund nur für bestimmte Datensätze oder Schwellen gilt, wird das explizit markiert
- `n1a_alpha` wird aktuell als **Sensitivitäts-/Dünnfall** behandelt, nicht als globaler Gegenbeweis

### 1.3 Aktueller methodischer Fokus
- kleine, reproduzierbare N1-Tests
- alternative Neighborhood-Definitionen
- Exportklassensensitivität
- A1/B1-Entkopplung
- nächster Block: alternatives Nullmodell für Exportklassen

---

## 2. Letzter belastbarer Ausgangspunkt vor dem aktuellen Block

Arbeitsbasis vor N1-Ausbau:
- **negative robust**
- **abs structured intermediate**
- **positive boundary non-launchable**

Diese Lesart war die operative Ziellinie, gegen die geprüft wurde, ob sie:
- durch alternative Neighborhood-Definitionen stabil bleibt,
- durch Adapterwahl künstlich erzeugt wird,
- oder in dünnen Fällen zusammenbricht.

---

## 3. N1-Block: alternative Neighborhood

## 3.1 Ausgangsproblem
Der ursprüngliche N1-Runner lief technisch, fand aber zunächst keine Daten, weil:
- `export_root` falsch lag
- die NPZs nicht im angenommenen `data/exports/...`-Baum lagen
- reale Inputs stattdessen unter `../results/...` vorhanden waren

Danach wurde der Loader schrittweise auf die reale Matrixstruktur angepasst.

## 3.2 Reale NPZ-Struktur
Die aktuellen N1-relevanten `matrices.npz` enthalten:
- `kbar`
- `G`
- `adjacency`
- `graph_distance`
- `edge_length`
- `d_rel`

Das heißt:
- keine expliziten `pair_ids / endpoint_a / endpoint_b`
- sondern Matrixartefakte, aus denen PairUnits operativ abgeleitet werden mussten

---

## 4. Matrix→PairUnit-Adapterentwicklung

## 4.1 v1: `adjacency_only`
Regel:
- PairUnit nur dann, wenn `adjacency[i,j] != 0`

### Befund
Für mehrere 4x4-Fälle ergab sich typischerweise:
- `negative`: 2 PairUnits, 0 Shells
- `abs`: 2 PairUnits, 0 Shells
- `positive`: 0 PairUnits, 0 Shells
- Ergebnis: **inconclusive**

### Interpretation
- zu mager
- keine auswertbare lokale Shell-Struktur
- Neighborhood-Frage damit nicht entscheidbar

---

## 4.2 v2: `adjacency_or_topk`
Regel:
- PairUnit, wenn `adjacency[i,j] != 0`
- oder Top-k nach `|G[i,j]|`

### Getestete Werte
- `k = 3`
- `k = 1`
- `k = 2`

### Befunde
#### `k = 3`
- alles wird nahezu symmetrisiert
- `negative = abs = positive`
- alle launchable
- qualitative Trennung verloren
- Ergebnis: formal `partially_supported`, inhaltlich aber über-symmetrisiert

#### `k = 1`
- Selektivität kehrt teilweise zurück
- `negative/abs > positive`
- aber weiterhin keine Shells
- Ergebnis: `inconclusive`

#### `k = 2`
- erneute Nivellierung
- wieder keine überzeugende Trennschärfe
- Ergebnis: `inconclusive`

### Interpretation
- Top-k ist für 4x4-Matrizen zu grob
- kippt schnell zwischen „zu dünn“ und „zu egalisierend“
- daher nicht als Standardadapter geeignet

---

## 4.3 v2.2: `adjacency_plus_threshold`
Regel:
- PairUnit, wenn `adjacency[i,j] != 0`
- oder `|G[i,j]| >= tau`

### Warum dieser Schritt
Die Off-Diagonalwerte in `G` lagen im relevanten Bereich bei ca.
- `0.0544`
- `0.0329`
- `0.0294`
- `0.02466`

Daher waren hohe Schwellen wie `0.25` oder `0.5` offensichtlich unpassend.

### Ergebnis
Threshold erwies sich als plausibler als Top-k.

---

## 5. N1-v2.2 — konkrete Befunde

## 5.1 Datensatz: `a1_probe/k0`
Mit:
- `matrix_pair_mode = adjacency_plus_threshold`
- `score_field = G`
- `tau = 0.025`

Ergebnis:
- `negative`: launchable, `pair_unit_count = 4`, `shell_count = 4`, `structured_intermediate`
- `abs`: launchable, `pair_unit_count = 4`, `shell_count = 4`, `structured_intermediate`
- `positive`: non-launchable, `pair_unit_count = 0`, `shell_count = 0`, `boundary_non_launchable`
- Blockurteil: **`partially_supported`**

Interpretation:
- `negative/abs > positive` bleibt erhalten
- `positive` wird nicht künstlich hochgezogen
- innere Trennung `negative` vs `abs` bleibt offen

---

## 5.2 Datensatz: `a1_sign_scan/k0/theta_0.03`
Mit demselben Adapter und `tau = 0.025`:
- qualitativ gleiches Muster wie `k0`
- `negative`, `abs` launchable
- `positive` non-launchable
- Blockurteil: **`partially_supported`**

Interpretation:
- Signal ist nicht auf `k0` allein beschränkt
- mindestens ein zweiter signalhaltiger Fall bestätigt die grobe Ordnung

---

## 5.3 Datensatz: `a1_probe/n1a_alpha`
Mit `tau = 0.025`:
- `negative`: non-launchable, `2 / 0`
- `abs`: non-launchable, `2 / 0`
- `positive`: non-launchable, `0 / 0`
- Blockurteil: **`inconclusive`**

### Threshold-Sweep für `n1a_alpha`
Getestet:
- `tau = 0.02`
- `0.0225`
- `0.025`
- `0.0275`
- `0.03`

### Sweep-Befund
#### `tau >= 0.025`
- alles bleibt zu dünn
- `negative = 2/0`, `abs = 2/0`, `positive = 0/0`
- Ergebnis: **`inconclusive`**

#### `tau <= 0.0225`
- `abs` wird selektiv launchable
- `negative` bleibt non-launchable
- `positive` bleibt non-launchable oder strukturell unterlegen
- Ergebnis: **`failed`**

### Interpretation
- `n1a_alpha` sitzt in einer instabilen Umschaltzone
- der Threshold-Adapter ist hier nicht robust
- insbesondere kippt die Struktur bei abgesenktem `tau` **zugunsten von `abs`**, ohne dass `negative` folgt

### Arbeitslesart
- `n1a_alpha` ist aktuell Sensitivitäts-/Dünnfall
- kein globaler Gegenbeweis
- aber ein klarer Hinweis darauf, dass der Adapter noch nicht universell robust ist

---

## 6. Zwischenfazit zum N1-Adapter

Der derzeit brauchbarste explorative Adapter ist:
- `adjacency_plus_threshold`
- auf `G`
- mit Arbeitswert `tau = 0.025`

### Was dafür spricht
- besser als `adjacency_only`
- klar besser als `adjacency_or_topk`
- reproduziert in signalhaltigen Fällen die grobe Trennung
  - `negative ≈ abs > positive`

### Was dagegen spricht
- nicht global robust
- `n1a_alpha` zeigt instabile Umschaltzone
- innere qualitative Trennung `negative` vs `abs` bleibt offen

### Arbeitsurteil
- **plausible explorative Adapterfamilie**
- **noch kein robuster Standardadapter**

---

## 7. A1/B1-Entkopplung

## 7.1 Ziel
Prüfen, ob das Combined-N1-Signal primär von A1, primär von B1 oder gemischt getragen wird.

## 7.2 Setup
Entkopplungsrunner:
- `run_n1_a1_b1_decoupling_v1.py`

Konfiguration:
- derselbe Adapter wie N1-v2.2
- `matrix_pair_mode = adjacency_plus_threshold`
- `tau = 0.025`

---

## 7.3 Befund: `a1_probe/k0`
### `negative` und `abs`
**Baseline:**
- `a1_status = weak`
- `a1_only_outcome = weak`
- `b1_status = active`
- `b1_only_outcome = strong`
- `dominant_channel = b1`

**Alternative:**
- `a1_status = partial`
- `a1_only_outcome = strong`
- `b1_status = active`
- `b1_only_outcome = strong`
- `dominant_channel = mixed`

**Positive:**
- `dominant_channel = none`

**Blockurteil:**
- **`supported`**

### Interpretation
- Baseline-Signal ist primär **B1-getrieben**
- alternative Neighborhood stärkt **A1 systematisch**
- Combined-Status bleibt gleich, aber der Kanalträger verschiebt sich von `b1` zu `mixed`

---

## 7.4 Befund: `a1_sign_scan/k0/theta_0.03`
Qualitativ identischer Befund wie `k0`:
- `negative`, `abs`: baseline `b1`, alternative `mixed`
- `positive`: `none`
- Blockurteil: **`supported`**

### Interpretation
- das A1/B1-Kanalbild ist über zwei signalhaltige Fälle konsistent

---

## 7.5 Befund: `a1_probe/n1a_alpha`
Bei `tau = 0.025`:
- alle Klassen non-launchable
- alle Klassen `dominant_channel = none`
- Blockurteil: **`inconclusive`**

### Interpretation
- schon die lokale Launchability fehlt
- daher ist keine sinnvolle A1/B1-Entkopplung möglich
- `n1a_alpha` bleibt im Standard-Setup ein Dünnfall

---

## 8. Verdichtetes A1/B1-Arbeitsfazit

Für die signalhaltigen Fälle (`k0`, `theta_0.03`) gilt:
- baseline-seitig ist das Combined-Signal für `negative` und `abs` primär **B1-dominant**
- unter alternativer Neighborhood wird A1 systematisch verstärkt
- die Kanalstruktur kippt in einen **mixed**-Zustand
- `positive` bleibt durchgehend kanalneutral und non-launchable (`none`)

Für `n1a_alpha` gilt:
- keine launchable Struktur
- keine auswertbare A1/B1-Trennung
- `inconclusive`

### Projektinterne Kernaussage
Das N1-Signal ist in tragenden Fällen **nicht bloß ein undifferenziertes Combined-Artefakt**, sondern baseline-seitig klar **B1-getrieben**, während A1 unter alternativer Neighborhood sichtbar nachzieht.

---

## 9. Aktueller Gesamtstand

### Was belastbar steht
1. Der aktuell brauchbarste kleine N1-Adapter ist `adjacency_plus_threshold @ tau=0.025` auf `G`.
2. In `k0` und `theta_0.03` reproduziert er robust die grobe Ordnung:
   - `negative ≈ abs > positive`
3. Die A1/B1-Entkopplung zeigt in diesen signalhaltigen Fällen ein konsistentes Kanalbild:
   - baseline: `b1`
   - alternative: `mixed`
   - positive: `none`
4. `n1a_alpha` bleibt im Standard-Setup strukturell zu dünn und markiert eine Robustheitsgrenze.

### Was offen bleibt
1. innere qualitative Trennung `negative` vs `abs`
2. global robuste Adapterregel über alle kleinen Fälle hinweg
3. alternative Nullmodelle zur Exportklassenzuordnung

---

## 10. Exportclass-Nullmodell v1

## 10.1 Ziel
Prüfen, ob die beobachtete grobe Exportklassentrennung
- `negative/abs > positive`

unter einfachen alternativen Klassenzuordnungen erhalten bleibt oder durch Nullmodelle ebenso gut reproduziert wird.

## 10.2 Setup
Konstant gehalten wurden:
- `matrix_pair_mode = adjacency_plus_threshold`
- `score_field = G`
- `tau = 0.025`
- baseline neighborhood: `shared_endpoint`
- target rule:
  - `negative launchable = true`
  - `abs launchable = true`
  - `positive launchable = false`

Getestet wurden:
- `a1_probe/k0`
- `a1_sign_scan/k0/theta_0.03`
- `a1_probe/n1a_alpha`

Nullmodellfamilien:
- role swaps
- kleine Permutationsmenge

## 10.3 Befund
### `a1_probe/k0`
- reale Zuordnung: `target_match = true`
- Nullruns: `2 / 8` Zieltreffer
- `null_target_match_rate = 0.25`
- `real_beats_null = true`

### `a1_sign_scan/k0/theta_0.03`
- qualitativ identischer Befund wie `k0`
- reale Zuordnung trifft das Zielmuster
- Nullruns ebenfalls nur `2 / 8`
- `real_beats_null = true`

### `a1_probe/n1a_alpha`
- reale Zuordnung: `target_match = false`
- Nullruns: `0 / 8`
- `real_equals_null = true`

## 10.4 Interpretation
Der Nullmodellblock stützt die Lesart, dass in den signalhaltigen Fällen die reale Exportklassenzuordnung **nicht beliebig austauschbar** ist.

Gleichzeitig zeigen die erfolgreichen Nullzuordnungen, dass im Wesentlichen nur der Tausch
- `negative <-> abs`

unschädlich bleibt.

Daraus folgt:
- robust unterstützt ist derzeit der gemeinsame Oberblock
  - `negative/abs > positive`
- nicht robust gezeigt ist bislang
  - `negative > abs`

`n1a_alpha` bleibt auch im Nullmodellvergleich ein Dünn-/Sensitivitätsfall.

## 10.5 Arbeitsfazit nach Nullmodell
Der aktuelle Stand ist jetzt dreifach abgestützt:
1. **Adapterebene:** `adjacency_plus_threshold @ tau=0.025` ist der brauchbarste kleine N1-Adapter.
2. **Kanalebene:** In signalhaltigen Fällen ist das Baseline-Signal primär **B1-getrieben**, unter alternativer Neighborhood wird es **mixed**.
3. **Nullmodellebene:** Die reale Exportklassenzuordnung ist in signalhaltigen Fällen besser als einfache Nullzuordnungen, aber `negative` und `abs` bleiben als Oberblock austauschbar.

---

## 11. Aktueller Gesamtstand

### Was belastbar steht
1. Der aktuell brauchbarste kleine N1-Adapter ist `adjacency_plus_threshold @ tau=0.025` auf `G`.
2. In `k0` und `theta_0.03` reproduziert er robust die grobe Ordnung:
   - `negative ≈ abs > positive`
3. Die A1/B1-Entkopplung zeigt in diesen signalhaltigen Fällen ein konsistentes Kanalbild:
   - baseline: `b1`
   - alternative: `mixed`
   - positive: `none`
4. Das Exportclass-Nullmodell zeigt: reale Zuordnung schlägt einfache Nullzuordnungen in den signalhaltigen Fällen, aber `negative` und `abs` sind als Oberblock weitgehend austauschbar.
5. `n1a_alpha` bleibt im Standard-Setup strukturell zu dünn und markiert eine Robustheitsgrenze.

### Was offen bleibt
1. innere qualitative Trennung `negative` vs `abs`
2. global robuste Adapterregel über alle kleinen Fälle hinweg
3. Ausbau des Nullmodells über einfache Rollenvertauschungen hinaus

---

## 12. Spezifitätsprüfung `negative` vs `abs`

## 12.1 Ziel
Prüfen, ob sich innerhalb des derzeit robusten Oberblocks
- `negative/abs > positive`

eine belastbare innere Trennung
- `negative > abs`

zeigen lässt.

## 12.2 Setup
Konstant gehalten wurden:
- `matrix_pair_mode = adjacency_plus_threshold`
- `score_field = G`
- `tau = 0.025`
- baseline neighborhood: `shared_endpoint`
- alternative neighborhood: `graph_distance_1`

Geprüfte Datensätze:
- `a1_probe/k0`
- `a1_sign_scan/k0/theta_0.03`
- `a1_probe/n1a_alpha`

Verglichen wurden auf `negative` vs `abs` mindestens:
- Strukturmetriken (`pair_unit_count`, `shell_count`, `mean_neighbor_count`)
- Kanalmetriken (`a1_score_mean`, `b1_score_mean`, Statusränge)
- Combined-Status

## 12.3 Befund
Ergebnis pro Datensatz/Modus:
- `k0` baseline: `tie`
- `k0` alternative: `tie`
- `theta_0.03` baseline: `tie`
- `theta_0.03` alternative: `tie`
- `n1a_alpha` baseline: `not_applicable`
- `n1a_alpha` alternative: `not_applicable`

Blockurteil:
- **`inconclusive`**

Kurzbegründung:
- Das aktuelle Signal stützt einen gemeinsamen Oberblock `negative/abs > positive`, zeigt aber noch keinen stabilen inneren Vorteil von `negative` gegenüber `abs`.

## 12.4 Interpretation
Der Block bestätigt die derzeit defensive Zwischenbilanz:
- robust gezeigt ist ein gemeinsamer Oberblock
  - `negative ≈ abs > positive`
- nicht robust gezeigt ist bislang
  - `negative > abs`

`n1a_alpha` bleibt auch hier ein Dünn-/Sensitivitätsfall und trägt nicht zu einer positiven Spezifitätsentscheidung bei.

## 12.5 Arbeitsfazit nach `negative vs abs`
Die bisherige Evidenzlage ist jetzt konsistent auf vier Ebenen:
1. **Adapterebene:** `adjacency_plus_threshold @ tau=0.025` ist der brauchbarste kleine N1-Adapter.
2. **Kanalebene:** In signalhaltigen Fällen ist das Baseline-Signal primär **B1-getrieben**, unter alternativer Neighborhood wird es **mixed**.
3. **Nullmodellebene:** Die reale Exportklassenzuordnung ist in signalhaltigen Fällen besser als einfache Nullzuordnungen, aber `negative` und `abs` bleiben als Oberblock austauschbar.
4. **Spezifitätsebene:** Eine robuste innere Trennung `negative > abs` ist im aktuellen Setup **nicht gezeigt**.

---

## 13. Aktueller Gesamtstand

### Was belastbar steht
1. Der aktuell brauchbarste kleine N1-Adapter ist `adjacency_plus_threshold @ tau=0.025` auf `G`.
2. In `k0` und `theta_0.03` reproduziert er robust die grobe Ordnung:
   - `negative ≈ abs > positive`
3. Die A1/B1-Entkopplung zeigt in diesen signalhaltigen Fällen ein konsistentes Kanalbild:
   - baseline: `b1`
   - alternative: `mixed`
   - positive: `none`
4. Das Exportclass-Nullmodell zeigt: reale Zuordnung schlägt einfache Nullzuordnungen in den signalhaltigen Fällen, aber `negative` und `abs` sind als Oberblock weitgehend austauschbar.
5. Die Spezifitätsprüfung `negative vs abs` bleibt im aktuellen Setup **inconclusive**; ein stabiler interner Vorsprung von `negative` ist nicht gezeigt.
6. `n1a_alpha` bleibt im Standard-Setup strukturell zu dünn und markiert eine Robustheitsgrenze.

### Was offen bleibt
1. neue Marker oder strengere Entscheidungsregeln für eine eventuelle innere Trennung `negative` vs `abs`
2. global robuste Adapterregel über alle kleinen Fälle hinweg
3. Ausbau des Nullmodells über einfache Rollenvertauschungen hinaus

---

## 14. Nächste Priorität

### Nächster Block
**Optionen ab hier:**
- Entwicklung gezielter Marker für `negative` vs `abs`
- oder Konsolidierung des jetzigen Zwischenstands für interne/externe Darstellung

### Leitfrage
Bleibt die defensiv belastbare Formulierung vorerst:
- `negative ≈ abs > positive`

oder lässt sich mit einem nächsten, gezielteren Markerblock doch noch eine reproduzierbare innere Spezifität sichtbar machen?

---

## 15. Terminalbefehl zum Verschieben (`mv`)

Falls diese Masterchat-Datei nach dem Erzeugen aus einem Download-/Zwischenordner in den Projektbaum verschoben werden soll, ist der Standardbefehl:

```bash
mv /tmp/MASTERCHAT_CURRENT_STATUS_2026-04-09_v2.md \
  ~/Downloads/deBroglie_Kaster_Theorie/debroglie-phase-bridge/debroglie-phase-bridge/typ_b_analysis/
```

Falls die Datei direkt in den Projekt-Notizordner soll, z. B.:

```bash
mv /tmp/MASTERCHAT_CURRENT_STATUS_2026-04-09_v2.md \
  ~/Downloads/deBroglie_Kaster_Theorie/debroglie-phase-bridge/debroglie-phase-bridge/notes/
```

Falls sie im aktuellen Ordner liegt und nur umbenannt/verschoben werden soll:

```bash
mv MASTERCHAT_CURRENT_STATUS_2026-04-09_v2.md notes/
```

---

## 16. Empfohlener Dateiname

```text
MASTERCHAT_CURRENT_STATUS_2026-04-09_v2.md
```

---

## 17. Empfohlene Anschlussdatei

Für einen möglichen nächsten Markerblock:

```text
PFLICHTENHEFT_N1_MARKER_NEGATIVE_VS_ABS_v1.md
```

