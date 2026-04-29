# Projektstand QSB / BMC-12 – menschenlesbare Timeline mit Mathematik

## Zweck dieser Notiz

Diese Notiz fasst den aktuellen Stand des QSB/BMC-Arbeitsstrangs in einer menschenlesbaren Form zusammen.

Sie ist bewusst intern geschrieben:

```text
Bildsprache + etwas Mathematik + methodische Einordnung
```

Sie ist nicht als Manuskripttext gedacht, sondern als Orientierung für das Gesamtbild.

---

## 0. Das innere Bild

Das aktuelle Arbeitsbild lautet:

```text
Beziehungsfeld
→ tragendes Gerüst
→ lokale Ordnung
→ möglicher Lokalitäts-/Geometrie-Proxy
```

Oder chemisch gedacht:

```text
homogene Lösung
→ Kristallisationskeim
→ erste Elementarzelle
→ wachsendes Gitter
→ makroskopischer Kristall
```

Für QSB heißt das:

```text
dichtes relationales Feld
→ stabiler lokaler Backbone
→ reproduzierbare Nachbarschaftsordnung
→ raumzeitähnliche Ordnung als spätere Interpretation
```

Wichtig:

```text
Backbone ≠ Raumzeit
Backbone = Kandidat für eine lokalitätsähnliche relationale Grundstruktur
```

Der Backbone ist also nicht der fertige „Klunker“, sondern eher der erste stabile Keim.

---

## 1. Grundidee in einfachen Worten

Wir starten nicht mit fertigen Punkten im Raum.

Wir starten mit Einheiten, die über Merkmale beschrieben werden:

```text
feature_mode_frequency
feature_length_scale
feature_shape_factor
feature_spectral_index
```

Diese Merkmale definieren einen relationalen Feature-Raum.

Aus diesem Feature-Raum bauen wir ein Beziehungsnetz:

```text
ähnliche Einheiten → starke Verbindung
unähnliche Einheiten → schwache Verbindung
```

Dann fragen wir:

```text
Bleibt in diesem Beziehungsnetz ein stabiles lokales Gerüst übrig?
```

Dieses stabile Gerüst ist der Backbone.

---

## 2. Kleine Mathematik des Beziehungsnetzes

Jeder Knoten `i` besitzt einen Feature-Vektor:

```text
x_i = (x_i1, x_i2, ..., x_id)
```

In unserem Fall etwa:

```text
x_i = (
  feature_mode_frequency,
  feature_length_scale,
  feature_shape_factor,
  feature_spectral_index
)
```

Die Features werden standardisiert:

```text
z_ik = (x_ik - mean_k) / std_k
```

Für zwei Knoten `i` und `j` berechnen wir den Abstand:

```text
d(i,j) = || z_i - z_j ||_2
```

also euklidisch:

```text
d(i,j) = sqrt( sum_k (z_ik - z_jk)^2 )
```

Daraus wird ein Gewicht:

```text
w(i,j) = 1 / (1 + d(i,j))
```

Bedeutung:

```text
kleiner Abstand  → großes Gewicht
großer Abstand   → kleines Gewicht
```

Oder im Bild:

```text
ähnliche Struktureinheiten binden stärker
unähnliche Struktureinheiten binden schwächer
```

---

## 3. Full graph, sparse graph, Backbone

Intern übersetzen wir:

| Fachwort | internes Bild |
|---|---|
| full graph | dichtes Beziehungsfeld / Beziehungssuppe |
| sparse graph | ausgedünntes Beziehungsnetz |
| backbone | tragendes Gerüst / Kristallisationskeim |
| edge | Verbindung / Bindung |
| weight | Bindungsstärke |
| node | Strukturpunkt / Baustein |
| graph-size sensitivity | der Klunker wächst anders, wenn die Lösung zu dicht wird |

Das dichte Beziehungsfeld enthält viele mögliche Verbindungen.

Der Backbone ist der Teil, der unter bestimmten Regeln als tragende lokale Struktur übrig bleibt.

---

## 4. BMC09d – der Referenzanker

Der aktuelle wichtige Anker stammt aus:

```text
BMC09d_threshold_tau_03
```

Dort wurde ein Referenz-Beziehungsnetz erzeugt mit:

```text
N = 81 Kanten
```

Die BMC09d-Entscheidung war:

```text
decision_label = backbone_localization_supported
dominant_arm   = backbone_only
```

In normaler Sprache:

```text
Die lokale Backbone-Struktur trägt das Signal stärker als Full-Graph,
Off-Backbone oder Coupling-only.
```

Der wichtige Punkt:

```text
BMC09d N=81 ist der Referenzkeim.
```

---

## 5. BMC-12a/b/c – Feature Leave-One-Out

### Frage

Ist der BMC09d-Backbone nur ein triviales Artefakt eines einzelnen Features?

Dazu wurde jedes Feature einmal entfernt:

```text
drop feature_mode_frequency
drop feature_length_scale
drop feature_shape_factor
drop feature_spectral_index
```

### Erstes Problem

Anfangs lief BMC-12 auf einer falschen/älteren Feature-Basis.

Das war der BMC08a-artige Zweig.

Die Folge:

```text
Referenzgraph passte nicht exakt zu BMC09d
```

Nach Korrektur auf die BMC08c-kompatible Feature-Tabelle wurde der BMC09d-Graph exakt rekonstruiert:

```text
original_edges:        81
bmc12b_baseline_edges: 81
shared_edges:          81
only_original:         0
only_bmc12b:           0
weight_differences:    0
```

In Menschensprache:

```text
Wir haben denselben Keim wiedergefunden.
Nicht ungefähr, sondern exakt.
```

### BMC-12c Ergebnis bei N=81

BMC-12c prüfte, ob die alte Backbone-Entscheidungsstruktur erhalten bleibt.

Bei N=81:

```text
baseline_all_features        → 3/3 retained
drop feature_mode_frequency  → 1/3 retained
drop feature_length_scale    → 1/3 retained
drop feature_shape_factor    → 1/3 retained
drop feature_spectral_index  → 2/3 retained
```

Interpretation damals:

```text
Kein einzelnes Feature trägt trivial die volle 3/3-Backbone-Entscheidung.
```

Aber:

```text
Feature-Drops verändern das Muster deutlich.
```

Also vorsichtig:

```text
structured joint-feature-basis sensitivity
```

Nicht:

```text
bewiesene Feature-Hierarchie
```

---

## 6. BMC-12d – Red-Team Integration

BMC-12d sammelte die Kritik von Claude, Grok, Louis und Deep Research.

Die wichtigste Red-Team-Kritik:

```text
Vielleicht ist BMC-12c nur ein lokaler Artefaktpunkt bei N=81.
```

Außerdem:

```text
matched-edge-count ist sinnvoll, aber nicht neutral
top-k/top-alpha können selbst Strukturannahmen enthalten
hard thresholds können kleine Änderungen stark verstärken
LOFO ist keine kausale Feature-Attribution
```

Die erlaubte Formulierung wurde enger:

```text
BMC-12c ist ein lokaler Robustheitsdiagnostik-Befund,
kein Beweis stabiler Feature-Rollen.
```

---

## 7. BMC-12e – Edge-Count Neighborhood Sweep

### Frage

Ist das BMC-12c-Muster bei N=81 stabil, wenn wir die Kantenzahl verändern?

Getestet wurde:

```text
N = 70, 75, 81, 87, 92
```

### Ergebnis Baseline

```text
N=70  baseline 3/3 retained
N=75  baseline 3/3 retained
N=81  baseline 3/3 retained
N=87  baseline 1/3 retained
N=92  baseline 0/3 retained
```

### Bildliche Interpretation

Bei passender Ausdünnung bildet sich ein stabiler Keim:

```text
N = 70, 75, 81
```

Bei zu dichter Struktur verschwindet die klare Keimordnung:

```text
N = 87, 92
```

Loriot-Version:

```text
Der Klunker wächst bei zu dichter Beziehungssuppe falsch.
```

### Fachliche Interpretation

BMC09d ist nicht graph-density-independent.

Besser:

```text
BMC09d is a sparse/local backbone-regime anchor.
```

Oder auf Deutsch:

```text
BMC09d sitzt in einem sparse/local Backbone-Regime.
```

### Feature-Drops in BMC-12e

Das exakte N=81-Featureprofil wiederholt sich nicht stabil über N.

Also:

```text
BMC-12c bleibt ein lokaler Decision-Point-Befund.
```

Nicht:

```text
globale Feature-Hierarchie
```

---

## 8. BMC-12f – Decision-Threshold / Dominance-Gap Sweep

### Frage

Ist der BMC09d-Referenzanker nur ein Artefakt der exakten Entscheidungsschwellen?

BMC-12f reklassifizierte vorhandene BMC-12e-Signale.

Getestet wurde:

```text
arrangement_signal_min = 0.045, 0.050, 0.055
dominance_gap_min     = 0.020, 0.030, 0.040
```

Das ergibt:

```text
9 threshold/gap pairs
```

### Mathematische Entscheidungsregel

Für jede Variante:

```text
S_full     = full_graph_arrangement_signal
S_backbone = backbone_only_arrangement_signal
S_off      = off_backbone_only_arrangement_signal
S_coupling = coupling_only_arrangement_signal
```

Dann:

```text
best_competing_signal = max(S_full, S_off, S_coupling)
backbone_gap          = S_backbone - best_competing_signal
```

Retained, wenn:

```text
S_backbone >= arrangement_signal_min
backbone_gap >= dominance_gap_min
```

### Ergebnis Baseline

```text
N=70 baseline:
  full = 3/9
  partial = 6/9
  mean_retained_fraction = 0.778
  stability = mixed_sensitive

N=75 baseline:
  full = 6/9
  partial = 3/9
  mean_retained_fraction = 0.889
  stability = mixed_sensitive

N=81 baseline:
  full = 9/9
  partial = 0/9
  mean_retained_fraction = 1.000
  stability = stable_full
```

### Hauptbefund

```text
N=81 ist der bisher stärkste und threshold-robuste Referenzanker.
```

Aber:

```text
N=70 und N=75 sind unterstützend, aber threshold-sensitiv.
```

### Feature-Drops

Die Feature-Drops bleiben gemischt oder instabil.

Also:

```text
keine stabile Feature-Hierarchie
keine kausale Feature-Wichtigkeit
keine stabile scale-dependent feature role
```

---

## 9. Red-Team nach BMC-12f

Claude, Grok und Louis konvergieren stark.

### Konsens

```text
N=81 ist als threshold-robuster Referenzanker im getesteten Grid gerechtfertigt.
N=70/75 sind supportive but threshold-sensitive.
Feature-Drops unterstützen keine stabile Feature-Hierarchie.
BMC-13 ist der richtige nächste Block.
```

### Wichtige Einschränkung

Die Robustheit gilt:

```text
within the tested grid
```

Nicht global.

### Stärkster verbleibender Einwand

Die aktuellen Backbone-Varianten sind nicht unabhängig:

```text
strength_topk_6
strength_topalpha_025
strength_topalpha_050
```

Alle drei sind verschiedene Schnitte derselben Top-Strength-Logik.

Also:

```text
3/3 retained bedeutet nicht drei unabhängige Methoden.
```

Sondern:

```text
Robustheit innerhalb einer Backbone-Familie.
```

Das ist der Hauptgrund für BMC-13.

---

## 10. Aktueller stärkster Claim

Die derzeit stärkste erlaubte Aussage lautet:

> The BMC09d reference anchor at N=81 is stable across the tested decision-threshold and dominance-gap grid. Neighboring sparse edge-counts N=70 and N=75 provide supportive but threshold-sensitive evidence on the same sparsity path. Feature-ablation profiles remain graph-size and threshold-sensitive and do not support a stable feature-role hierarchy at this stage. The main remaining methodological risk is dependence on the current top-strength backbone extraction rules.

Deutsch intern:

> N=81 ist unser bisher stabilster Referenzkeim. N=70/75 gehören zur Nachbarschaft, wackeln aber stärker. Feature-Drops liefern Diagnostik, aber keine stabile Feature-Rangordnung. Der nächste Kobold sitzt in der Backbone-Methode selbst.

---

## 11. Timeline

### Phase 1 – Grundbild

```text
Materiewellen / de Broglie
→ relationale Verbindungen
→ mögliche lokale Ordnung
```

Internes Bild:

```text
Knöpfchen, Erde und ich im Gravitationschaos
chemische Bindung als stabile diskrete Verbindung
Isotopenanalogie für Varianten / Skalen
Kristallisationskeim aus Beziehungssuppe
```

### Phase 2 – Feature-Space und Beziehungsnetz

```text
Features definieren relationalen Raum.
Abstände definieren Gewichte.
Gewichte definieren Beziehungsnetz.
```

Mathe:

```text
d(i,j) = || z_i - z_j ||_2
w(i,j) = 1 / (1 + d(i,j))
```

### Phase 3 – BMC09d Referenzanker

```text
N=81
decision_label = backbone_localization_supported
dominant_arm = backbone_only
```

Bild:

```text
stabiler Kristallisationskeim
```

### Phase 4 – BMC-12 Feature-Abbruchtest

```text
Leave-one-feature-out
```

Frage:

```text
Trägt ein einzelnes Feature alles?
```

Antwort:

```text
Nein, trivialer Single-Feature-Artefakt wird geschwächt.
Aber keine stabile Feature-Hierarchie.
```

### Phase 5 – BMC-12e Graphgrößen-Nachbarschaft

```text
N = 70,75,81,87,92
```

Antwort:

```text
N=70/75/81 baseline retained
N=87/92 kippt
```

Bild:

```text
Keim stabil im sparse/local Bereich,
bei zu dichter Beziehungssuppe wächst anderer Klunker.
```

### Phase 6 – BMC-12f Threshold/GAP-Sweep

```text
9 threshold/gap pairs
```

Antwort:

```text
N=81 stable_full
N=70/75 mixed_sensitive
Feature-Drops mixed/unstable
```

Bild:

```text
Der Referenzkeim N=81 hält auch bei kleinen Schwellenwacklern.
Die Nachbarschaft lebt, aber wackelt.
```

### Phase 7 – Red-Team Konsens

```text
N=81 robust within tested grid.
BMC-13 is next.
```

Offene Lücke:

```text
Sind top-k/top-alpha nur verschiedene Brillen derselben Methode?
```

---

## 12. Was wir jetzt wissen

### Befund

```text
BMC09d N=81 wurde exakt rekonstruiert.
N=81 ist graphgrößen- und threshold-seitig der stabilste Referenzpunkt.
N=70/75 stützen das sparse/local Bild, sind aber empfindlicher.
N=87/92 liegen offenbar in einem anderen/dichteren Regime.
Feature-Drops zeigen Sensitivität, aber keine stabile Hierarchie.
```

### Interpretation

```text
Der Backbone ist ein methodischer Lokalitäts-Proxy.
Der stärkste aktuelle Befund ist ein stabiler sparse/local Referenzanker bei N=81.
```

### Hypothese

```text
Der BMC09d N=81-Anker könnte ein besonders stabiler Kristallisationskeim
einer relationalen Lokalitätsstruktur sein.
```

### Offene Lücke

```text
Der Backbone wurde bisher nur innerhalb top-strength-basierter Varianten getestet.
BMC-13 muss alternative Backbone-Konzepte prüfen.
```

---

## 13. Was wir nicht behaupten

Nicht behaupten:

```text
Wir haben Raumzeit bewiesen.
Der Backbone ist Raumzeit.
Eine Feature-Hierarchie ist etabliert.
Feature X ist kausal wichtig.
Der Befund ist graph-density-independent.
Die drei Backbone-Varianten sind unabhängige Methoden.
```

Stattdessen:

```text
Wir haben einen robusten methodischen Referenzanker
für einen relationalen Lokalitäts-Backbone-Proxy gefunden,
innerhalb klar definierter Pipeline- und Parametergrenzen.
```

---

## 14. Nächster Block: BMC-13

### Ziel

BMC-13 testet:

```text
Ist der N=81-Backbone-Anker abhängig von top-k/top-alpha,
oder erscheint er auch unter anderen Backbone-Konzepten?
```

### Warum nötig?

Weil bisher alle Varianten aus derselben Familie stammen:

```text
top-strength selection
```

### Mögliche BMC-13-Methoden

```text
current top-strength variants as reference
mutual-kNN style local neighborhood filter
spanning-tree style backbone
disparity-like weighted backbone
threshold-path consensus
multi-method consensus backbone
```

### Erwartete Lesart

Wenn N=81 auch unter alternativen Methoden erscheint:

```text
methodenübergreifende Stärkung
```

Wenn nicht:

```text
BMC09d ist method-specific, aber trotzdem als Pipeline-Befund wertvoll
```

---

## 15. Gesamtbild in einem Satz

> QSB/BMC zeigt derzeit keinen Beweis emergenter Raumzeit, sondern einen methodisch kontrollierten Hinweis auf einen stabilen relationalen Lokalitäts-Backbone-Kandidaten: Der BMC09d-Referenzkeim bei N=81 ist exakt rekonstruiert und im getesteten Threshold/GAP-Gitter robust, während Nachbarschaftspunkte und Feature-Ablationen sensibler bleiben und die wichtigste offene Frage nun die Backbone-Methodenabhängigkeit ist.

---

## 16. Interne Kurzform

```text
Beziehungssuppe → Keim → Gerüst → möglicher Lokalitäts-Proxy

N=81:
  stabilster Keim

N=70/75:
  Nachbarschaft, aber wackliger

N=87/92:
  zu dicht, anderes Regime

Feature-Drops:
  diagnostisch, aber keine Rangordnung

Nächster Kobold:
  Backbone-Methode selbst
```

Oder ganz Loriot-kompatibel:

```text
Der Klunker wächst bei N=81 am saubersten.
Bei N=70/75 sieht man den Keim noch, aber er reagiert empfindlicher.
Bei N=87/92 kristallisiert etwas anderes.
Jetzt müssen wir prüfen, ob der Klunker auch mit anderer Brille derselbe bleibt.
```
