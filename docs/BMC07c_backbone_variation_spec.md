# BMC-07c – Variation der Backbone-Definition (Spezifikation)

## Status
Spezifikationsschritt vor Implementierung.

## Zweck
BMC-07c prüft, ob der bisherige Befund aus BMC-07 und BMC-07b
von der **aktuellen Backbone-Definition** abhängt.

Die Kernfrage lautet:

**Bleibt `off_backbone_localization_supported` bestehen,
wenn die Backbone-Menge anders konstruiert wird?**

Damit wird nicht die Theorie geändert, sondern die **Segmentierungsregel**
des bestehenden diagnostischen Blocks variiert.

## Ausgangspunkt

### Letzter belastbarer Befund
Der offene BMC-07b-Minimallauf ergab:

- `decision_label = off_backbone_localization_supported`
- `dominant_arm = off_backbone_only`

Rangfolge der Arme:
1. `off_backbone_only` → `0.077322`
2. `coupling_only` → `0.027570`
3. `full_graph` → `0.024059`
4. `backbone_only` → `-0.004218`

### Projektinterne Lesart
Der Minimaldatensatz stützt aktuell:
- **keine Backbone-Lokalisierung**
- **keine Coupling-Lokalisierung**
- stattdessen einen kleinen Off-Backbone-Kontrastbefund

### Offene Kernfrage
Ist dieser Befund
- **robust gegenüber der Backbone-Definition**
oder
- nur ein Artefakt der bisherigen `backbone_hint`-basierten Segmentierung?

## Blockdefinition

BMC-07c variiert **nur die Backbone-Konstruktion**.
Readouts, Armdefinitionen und Entscheidungslogik bleiben so weit wie möglich stabil,
damit die Vergleichbarkeit erhalten bleibt.

### Konstant zu halten
- dieselben Inputtabellen
- dieselben Readouts
- dieselben vier Arme:
  - `full_graph`
  - `backbone_only`
  - `off_backbone_only`
  - `coupling_only`
- dieselbe Shuffle-Logik
- dieselbe defensive Entscheidungslogik

### Zu variieren
Nur:
- wie die Backbone-Knoten ausgewählt werden

## Zu testende Backbone-Varianten

### V1 – Hint-basierte Referenz
**Name:** `hint_reference`

Definition:
- Backbone = alle Knoten mit `backbone_hint == 1`

Zweck:
- Referenz auf bisherigen Stand
- dient als Vergleichsbasis für alle anderen Varianten

### V2 – Strength-top-k
**Name:** `strength_topk`

Definition:
- berechne gewichtete Inzidenzstärke pro Knoten
- wähle die obersten `k` Knoten als Backbone

Empfohlener Minimalwert:
- `k = backbone_node_count_reference`

Zweck:
- prüft, ob der bisherige Befund verschwindet, wenn der Kern rein nach Gewichtsstärke
  statt nach Hint definiert wird

### V3 – Strength-top-alpha
**Name:** `strength_topalpha`

Definition:
- berechne gewichtete Inzidenzstärke pro Knoten
- wähle die obersten `ceil(alpha * n_nodes)` Knoten

Empfohlene Alpha-Leiter:
- `0.25`
- `0.375`
- `0.50`

Zweck:
- prüft Sensitivität gegenüber der Backbone-Größe

### V4 – Same-shell-core
**Name:** `same_shell_core`

Definition:
- Knoten werden nach Anteil same-shell-gewichteter Inzidenz sortiert
- die obersten `k` oder `ceil(alpha * n_nodes)` bilden den Backbone

Zweck:
- prüft, ob shell-nahe Knoten selbst eine bessere Kerntrennung liefern

### V5 – Hybrid score
**Name:** `hybrid_strength_shell`

Definition:
- Score pro Knoten:
  `hybrid_score = lambda * normalized_strength + (1 - lambda) * normalized_same_shell_fraction`
- Backbone = oberste `k` oder oberstes `alpha`

Empfohlene Minimalwerte:
- `lambda = 0.5`
- `lambda = 0.7`

Zweck:
- defensiver Mischansatz statt harter Vorentscheidung für reine Strength- oder reine Shelllogik

## Priorisierung

### Priorität A – sofort
1. `hint_reference`
2. `strength_topk`
3. `strength_topalpha`

### Priorität B – zweite Welle
4. `same_shell_core`
5. `hybrid_strength_shell`

Begründung:
Zuerst die einfachsten, transparentesten und am leichtesten prüfbaren Varianten.
Erst danach strukturreichere Mischdefinitionen.

## Readouts

### Primäre Vergleichsgrößen pro Variante
- `decision_label`
- `dominant_arm`
- `arm_signal_ranking`
- `backbone_node_count`
- `coupling_edge_count`

### Primäre Vergleichsgrößen pro Arm
- `arrangement_signal`
- `shell_order_drift`
- `same_shell_weight_fraction`
- `edge_count`
- `node_count`

## Vergleichslogik

### Kernfrage 1 – Label-Stabilität
Bleibt bei Backbone-Variation:
- `off_backbone_localization_supported`
oder kippt das Label zu
- `coupling_localization_supported`
- `backbone_localization_supported`
- `full_only_or_mixed`
- `weak_or_inconclusive`

### Kernfrage 2 – Rangstabilität
Bleibt die Reihenfolge
`off_backbone > coupling > full > backbone`
erhalten?

### Kernfrage 3 – Backbone-Rettung
Gibt es eine plausible, offene und einfache Backbone-Definition,
unter der der Backbone-Arm tatsächlich dominant wird?

Wenn **ja**:
- dann war die bisherige Definition vermutlich unpassend

Wenn **nein**:
- dann wächst der Befund, dass das lokale Signal im Minimaldatensatz
  tatsächlich nicht im Backbone sitzt

## Entscheidungslogik (defensiv)

### backbone_definition_sensitive
Wenn:
- verschiedene plausible Backbone-Definitionen zu deutlich verschiedenen Labels führen

### off_backbone_result_robust
Wenn:
- `off_backbone_localization_supported` unter mehreren einfachen Backbone-Definitionen bestehen bleibt

### backbone_result_recovered
Wenn:
- unter mindestens einer einfachen, gut begründeten Variante
  `backbone_localization_supported` auftritt
- und diese Variante nicht künstlich wirkt

### still_weak_or_mixed
Wenn:
- die Variation keine klare und konsistente Lokalisierung liefert

## Outputvertrag

### Neuer Variantensummary-Block
BMC-07c soll nicht nur Einzellaufdateien schreiben,
sondern zusätzlich eine vergleichende Übersicht.

#### Vorschlag:
`runs/BMC-07/<run_id>/backbone_variant_summary.csv`

Felder:
- `variant_name`
- `variant_parameters`
- `backbone_node_count`
- `coupling_edge_count`
- `decision_label`
- `dominant_arm`
- `full_graph_arrangement_signal`
- `backbone_only_arrangement_signal`
- `off_backbone_only_arrangement_signal`
- `coupling_only_arrangement_signal`

### Optional zusätzlich
`docs/BMC07c_variant_matrix_note.md`
als interne Ergebnisnotiz nach Abschluss der Läufe

## YAML-Erweiterung

### Vorschlag
```yaml
backbone_variants:
  enabled: true
  variants:
    - variant_name: "hint_reference"
      method: "hint_reference"

    - variant_name: "strength_topk"
      method: "strength_topk"
      top_k: 4

    - variant_name: "strength_topalpha_025"
      method: "strength_topalpha"
      alpha: 0.25

    - variant_name: "strength_topalpha_050"
      method: "strength_topalpha"
      alpha: 0.50
```

## Sanity-Checks
Für jede Variante separat prüfen:

- `backbone_node_count >= minimum_backbone_nodes`
- `off_backbone_node_count >= minimum_off_backbone_nodes`
- `coupling_edge_count >= 0`
- keine leeren Pflichtarme ohne Kennzeichnung
- Variantennamen eindeutig

Wenn eine Variante zu klein oder degeneriert ist:
- Variante nicht verwerfen
- aber im Summary klar als **diagnostisch schwach** markieren

## Was der Block bewusst gut macht
- trennt Segmentierungsfrage von Readoutfrage
- prüft Robustheit des bisherigen Befunds
- bleibt offen, klein und nachvollziehbar
- führt keine neue Metrik-Blackbox ein

## Was der Block bewusst vermeidet
- keine sofortige Theoriekorrektur
- keine physikalische Überhöhung aus Minimaldaten
- keine versteckte Optimierung „bis Backbone gewinnt“
- keine Vermischung von Backbone-Definition und Ergebniswunsch

## Befund
Noch keiner. Diese Datei ist reine Spezifikation.

## Interpretation
BMC-07c ist die methodisch naheliegende Fortsetzung von BMC-07b.

## Hypothese
Wenn `off_backbone_localization_supported` auch unter einfachen alternativen
Backbone-Definitionen bestehen bleibt, dann wird der aktuelle Minimalbefund robuster.
Wenn dagegen eine plausible einfache Backbone-Variante den Befund kippt,
dann war die bisherige Segmentierung wahrscheinlich der eigentliche Engpass.

## Offene Lücke
Implementierung, Varianten-Runner und offene Vergleichsläufe fehlen noch.
