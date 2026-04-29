# BMC-07d – Legitimationsmatrix der Backbone-Varianten

## Status
Methodische Prüfnote nach offenem BMC-07c-Variantenlauf.

## Zweck
BMC-07d bewertet die in BMC-07c verwendeten Backbone-Varianten **nicht** nach gewünschtem Ergebnis,
sondern nach ihrer **methodischen Legitimation**.

Die Kernfrage lautet:

**Welche Backbone-Definitionen sind als faire, ex-ante vertretbare Segmentierungsregeln lesbar — und welche sind dem späteren Readout bereits zu nah?**

Damit trennt BMC-07d:
- **Signalbefund**
von
- **Legitimität der Segmentierungsregel**

## Ausgangspunkt

### Letzter belastbarer Befund
Der offene BMC-07c-Lauf ergab:

- unter den meisten einfachen Varianten bleibt `off_backbone_localization_supported`
- unter `same_shell_core_topk` wird `backbone_localization_supported` zurückgewonnen
- `hybrid_strength_shell_lambda_07` bleibt `weak_or_inconclusive`

### Projektinterne Lesart
Der Minimalbefund ist **backbone-definition-sensitiv**, aber nicht beliebig.
Gerade deshalb muss jetzt geprüft werden, **welche Varianten methodisch fair** sind.

## Bewertungslogik

Jede Variante wird entlang derselben Prüfkriterien bewertet:

1. **Ex-ante-Plausibilität**
   - Ist die Regel unabhängig vom gewünschten Ergebnis begründbar?

2. **Nähe zum Readout**
   - Nutzt die Backbone-Definition bereits Struktur, die dem späteren Readout stark ähnelt?

3. **Risiko der Definition-Readout-Kopplung**
   - Besteht die Gefahr, dass der Backbone-Befund teilweise schon durch die Definition vorgeprägt wird?

4. **Transparenz**
   - Ist die Regel offen, klein und gut nachvollziehbar?

5. **Projektinterner Status**
   - `faire Basis`
   - `plausibel, aber sensitiv`
   - `explorativ`
   - `kritisch / readout-nah`

## Legitimationsmatrix

| Variante | Kurzdefinition | Ex-ante-Plausibilität | Nähe zum Readout | Risiko Definition-Readout-Kopplung | Transparenz | Projektinterner Status | Kurzlesart |
|---|---|---|---|---|---|---|---|
| `hint_reference` | Backbone aus vorhandener `backbone_hint`-Markierung | mittel | gering | gering bis mittel | hoch | faire Basis | Referenzvariante; nicht stark theorienah, aber als offener Ausgangspunkt vertretbar |
| `strength_topk` | oberste Knoten nach gewichteter Inzidenzstärke, fixes `k` | hoch | gering | gering | hoch | faire Basis | einfache und gut begründbare Kernregel ohne direkte Readout-Nähe |
| `strength_topalpha` | oberste Knoten nach gewichteter Inzidenzstärke, Anteil `alpha` | hoch | gering | gering | hoch | faire Basis | wie `strength_topk`, zusätzlich Sensitivität gegenüber Kerngröße offen prüfbar |
| `same_shell_core` | oberste Knoten nach same-shell-orientierter Inzidenz | mittel | hoch | hoch | hoch | kritisch / readout-nah | offen definiert, aber der späteren Shell-Ordnungslogik methodisch deutlich angenähert |
| `hybrid_strength_shell (λ=0.5)` | Mischscore aus Strength und same-shell-Anteil | mittel | mittel bis hoch | mittel bis hoch | mittel bis hoch | plausibel, aber sensitiv | diagnostisch interessant, aber bereits partiell readout-nah |
| `hybrid_strength_shell (λ=0.7)` | stärker strength-lastiger Mischscore | mittel bis hoch | mittel | mittel | mittel bis hoch | plausibel, aber sensitiv | defensiver als λ=0.5, aber nicht mehr reine Basisregel |

## Einzelfallbewertung

### 1. `hint_reference`
**Befund**  
Off-Backbone bleibt dominant.

**Interpretation**  
Die Variante ist nicht besonders tief begründet, aber als Referenz legitim, weil sie den bisherigen Stand offen konserviert.

**Hypothese**  
Wenn selbst die Referenz auf Off-Backbone zeigt, ist das als Ausgangsbefund brauchbar.

**Offene Lücke**  
Die Qualität der ursprünglichen Hint-Markierung selbst bleibt begrenzt.

### 2. `strength_topk`
**Befund**  
Off-Backbone bleibt dominant.

**Interpretation**  
Das ist eine der methodisch saubersten Varianten: offen, einfach, gut begründbar, readout-fern.

**Hypothese**  
Wenn Off-Backbone hier trägt, dann ist der Befund nicht bloß ein Hint-Artefakt.

**Offene Lücke**  
Fixes `k` kann die Kerngröße etwas arbiträr setzen.

### 3. `strength_topalpha`
**Befund**  
Off-Backbone bleibt bei `alpha = 0.25` und `0.50` dominant.

**Interpretation**  
Sehr wichtiger Stützbefund, weil hier nicht nur die Kernregel, sondern auch die Kern**größe** offen variiert wird.

**Hypothese**  
Das spricht für eine gewisse Robustheit der Off-Backbone-Tendenz innerhalb einfacher Basiskonstruktionen.

**Offene Lücke**  
Weitere Alpha-Stufen könnten das Bild noch feiner machen.

### 4. `same_shell_core`
**Befund**  
Hier wird Backbone-Lokalisierung zurückgewonnen.

**Interpretation**  
Die Variante ist transparent und nachvollziehbar definiert, aber **nicht methodisch neutral**:
Sie baut den Backbone bereits mit einer Regel, die in Richtung shell-naher Organisation weist.

**Hypothese**  
Der Backbone-Befund dieser Variante kann inhaltlich interessant sein, darf aber nicht ohne Zusatzprüfung als faire Bestätigung einer Backbone-Lokalisierung gelesen werden.

**Offene Lücke**  
Genau hier ist eine formale Legitimitätsdiskussion zwingend.

### 5. `hybrid_strength_shell`
**Befund**  
Bei `λ = 0.5` bleibt Off-Backbone dominant, bei `λ = 0.7` wird das Bild schwächer.

**Interpretation**  
Die Hybridvarianten sind nützlich als Übergangsdiagnostik, aber nicht mehr so sauber readout-fern wie pure Strength-Regeln.

**Hypothese**  
Sie zeigen, wie sensibel die Segmentierung auf schrittweise Shell-Nähe reagiert.

**Offene Lücke**  
Als primäre Basen sind sie schwächer legitimiert als `strength_topk` oder `strength_topalpha`.

## Projektinterne Gesamtlesart

### Methodisch stärkste Basisvarianten
- `strength_topk`
- `strength_topalpha`

Diese Varianten sind:
- offen
- klein
- gut begründbar
- relativ readout-fern

### Zulässige Referenz, aber schwächer
- `hint_reference`

### Diagnostisch interessant, aber nicht neutral
- `hybrid_strength_shell`

### Besonders prüfbedürftig
- `same_shell_core`

## Vorläufige Arbeitsregel für spätere Dokumentation

### Als faire Hauptbasis verwenden
- `strength_topk`
- `strength_topalpha`
- optional ergänzend `hint_reference`

### Als explorative Zusatzvarianten ausweisen
- `hybrid_strength_shell`

### Nicht als alleinige Hauptstütze für Backbone-Claims verwenden
- `same_shell_core`

Begründung:
`same_shell_core` ist keine Blackbox, aber methodisch zu nah an der späteren Shell-Ordnungslogik, um ohne ausdrückliche Legitimitätswarnung als neutrale Backbone-Basis zu dienen.

## Konsequenz für BMC-07c-Lesart

### Sauber defensiver Satz
Der in BMC-07c beobachtete Off-Backbone-Befund bleibt unter mehreren einfachen und methodisch fairen Backbone-Definitionen erhalten.
Ein Backbone-Recovery tritt nur unter einer readout-näheren Variante (`same_shell_core`) auf und ist daher als explorativer, aber legitimatorisch besonders prüfbedürftiger Zusatzbefund zu lesen.

## Befund
BMC-07d liefert keine neuen numerischen Ergebnisse, sondern eine methodische Einordnung der bereits beobachteten Variantenbefunde.

## Interpretation
Die stärksten Stützen des bisherigen Minimalbefunds liegen derzeit bei den **einfachen strength-basierten Backbone-Definitionen**.

## Hypothese
Wenn der Off-Backbone-Befund auf realeren Inputs ebenfalls unter fairen Basisvarianten bestehen bleibt, wird er methodisch deutlich belastbarer.

## Offene Lücke
Noch offen ist die Übertragung vom Minimaldatensatz auf reale Projektgraphen.
Ebenso offen bleibt, ob später eine formal noch sauberere, aber readout-ferne Backbone-Regel entwickelt werden kann.

## Feldliste – mögliche spätere Matrixdatei
- `variant_name` — string — Name der Backbone-Variante.
- `definition_short` — string — Kurzbeschreibung der Segmentierungsregel.
- `ex_ante_plausibility` — string — qualitative Einstufung der ex-ante Begründbarkeit.
- `readout_proximity` — string — qualitative Nähe zur späteren Messlogik.
- `coupling_risk` — string — Risiko einer Definition-Readout-Kopplung.
- `transparency` — string — qualitative Transparenzbewertung.
- `status` — string — projektinterner Legitimationsstatus.
- `comment` — string — kurze interpretative Einordnung.
