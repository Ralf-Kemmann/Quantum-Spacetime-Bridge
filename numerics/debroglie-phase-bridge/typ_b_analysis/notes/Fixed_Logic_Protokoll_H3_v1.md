# Fixed-Logic-Protokoll  
## H3_SUPPORT_MANIPULATION_DESIGN_01  
### Version vor dem nächsten Lauf

## 1. Zweck
Dieses Protokoll fixiert die operative Logik des Blocks `H3_SUPPORT_MANIPULATION_DESIGN_01` **vor** dem nächsten Testlauf, damit nachträgliche Umdeutungen oder Label-Anpassungen ausgeschlossen sind.

Ziel ist nicht die Ergebnisoptimierung, sondern die methodische Härtung des aktuellen lokalen support-side Befunds.

## 2. Geltungsbereich
Dieses Protokoll gilt für den nächsten vollständigen Lauf des Blocks auf Basis von:

- `src/export_h3_support_scores_from_decoupling.py`
- `src/runners/h3_support_manipulation_design_01_runner.py`

und der daraus erzeugten Datei:

- `data/original/h3_support_scores.csv`

## 3. Datenquelle
Die Inputdaten werden aus den vorhandenen Decoupling-Artefakten erzeugt:

- baseline source: `results/a1_probe/k0/*/matrices.npz`
- combined source: `results/a1_probe/n1a_alpha/*/matrices.npz`

Verwendete Klassen:
- `negative`
- `abs`
- `positive`

## 4. Einheit der Analyse
Die operative Einheit ist **paarbasiert**, nicht zeilenbasiert.

Jede Einheit ist ein Off-Diagonal-Paar `i < j` innerhalb einer Klasse:

- `unit_id = <export_class>_eij`

Beispiele:
- `negative_e01`
- `abs_e23`
- `positive_e13`

## 5. Score-Definition
Primäre Runner-Scores:

- `baseline_score = G_baseline[i,j]`
- `combined_score = G_combined[i,j]`

Zusätzliche diagnostische Größen:
- `baseline_score_kbar = kbar_baseline[i,j]`
- `combined_score_kbar = kbar_combined[i,j]`
- `delta_score_g = combined_score - baseline_score`
- `delta_score_kbar = combined_score_kbar - baseline_score_kbar`

Für den nächsten Lauf werden **keine alternativen Score-Definitionen** eingeführt.

## 6. Label-Logik
Für jedes Paar werden drei Labeltypen berechnet:

- `support_like`
- `boundary_like`
- `mixed_like`

### 6.1 support_like
Ein Paar ist `support_like = 1`, wenn mindestens eine der folgenden Bedingungen erfüllt ist:

- `baseline_adjacent == 1` oder `combined_adjacent == 1`
- `baseline_score > 0.0` und `combined_score > 0.0`

Sonst `support_like = 0`.

### 6.2 boundary_like
Ein Paar ist `boundary_like = 1`, wenn beide Bedingungen erfüllt sind:

- `baseline_adjacent == 0` und `combined_adjacent == 0`
- `baseline_score == 0.0` und `combined_score == 0.0`

Sonst `boundary_like = 0`.

### 6.3 mixed_like
Ein Paar ist `mixed_like = 1`, wenn es weder `support_like` noch `boundary_like` ist.

Formal:
- `mixed_like = 1`, falls `support_like == 0` und `boundary_like == 0`

## 7. Runner-Mapping
Für den nächsten Lauf gilt fest:

- `is_support = support_like`
- `is_neighbor = boundary_like`

Mixed-Paare werden **nicht** in den harten Neighbor-Satz aufgenommen.

## 8. Zustandslogik des Blocks
Die Testzustände bleiben unverändert:

- `A = baseline reference`
- `B = mild support-side manipulation`
- `C = stronger support-side manipulation`
- `D1 = permutation_null`
- `D2 = topology_preserving_random_null`

## 9. Parameterprofile
Die Profilfaktoren bleiben fest:

- `base = 1.00`
- `mild_plus = 1.05`
- `mild_minus = 0.95`

Für den nächsten Lauf werden **keine weiteren Profile** ergänzt.

## 10. Nullmodelle
### D1
`D1` permutiert die Support-Zuordnung.

### D2
`D2` verwendet die aktuell implementierte strukturkonservierende Randomisierung.

Wichtig:
Für den nächsten Lauf wird **keine weitere Änderung an D1 oder D2** vorgenommen.  
Die Frage, ob D2 künftig noch stärker von D1 getrennt werden muss, ist **Folgefrage nach dem Lauf**, nicht Teil dieses Protokolls.

## 11. Zentrale Zielgröße
Die zentrale Zielgröße bleibt:

`gain_value = support_sep_combined - support_sep_baseline`

mit:

- `support_sep_baseline = median(baseline_score | support) - median(baseline_score | neighbor)`
- `support_sep_combined = median(combined_score_effective | support_effective) - median(combined_score_effective | neighbor_effective)`

## 12. Vorab festgehaltene methodische Lesart
Der nächste Lauf dient der Prüfung, ob der aktuelle lokale support-side entry

- unter baseline-first erhalten bleibt,
- unter B/C geordnet skaliert,
- und unter D1/D2 niedrig bzw. nichttragend bleibt,

**ohne weitere Änderung der Label- oder Score-Logik**.

## 13. Was vor dem nächsten Lauf ausdrücklich nicht geändert wird
Vor dem nächsten Lauf werden **nicht** geändert:

- die support_like / boundary_like / mixed_like-Definition
- die Paar- statt Zeilenrepräsentation
- die Zuordnung `is_support = support_like`
- die Zuordnung `is_neighbor = boundary_like`
- die A/B/C/D1/D2-Architektur
- die Profilfaktoren
- die primäre G-basierte Score-Definition

## 14. Was nach dem Lauf separat bewertet werden darf
Erst **nach** dem nächsten eingefrorenen Lauf dürfen als Folgefragen bewertet werden:

- ob D2 ausreichend unabhängig von D1 ist
- wie sensitiv der Befund gegenüber mixed_like-Behandlung ist
- ob `kbar` als alternativer Primärscore geprüft werden soll
- ob ein dichterer Manipulations-Sweep nötig ist
- ob weitere Quellen/Replikationen angeschlossen werden sollen

## 15. Aktueller Status des Protokolls
Dieses Protokoll dient als **Freeze-Punkt** vor dem nächsten Lauf.  
Jede Abweichung davon ist als neue Version zu dokumentieren und nicht stillschweigend in denselben Testlauf einzubauen.

## 16. Kurzform für interne Verwendung
> Vor dem nächsten Lauf sind Paarrepräsentation, G-basierte Score-Definition, support_like/boundary_like/mixed_like-Regel, is_support/is_neighbor-Mapping, A/B/C/D1/D2-Architektur und Profilfaktoren eingefroren. Der nächste Lauf dient der Prüfung dieser fixierten Logik ohne weitere Nachjustierung.
