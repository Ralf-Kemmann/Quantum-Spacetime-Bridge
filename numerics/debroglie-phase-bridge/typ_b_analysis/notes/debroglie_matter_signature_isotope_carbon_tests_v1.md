# debroglie_matter_signature_isotope_carbon_tests_v1

## 1. Direkt aus `debroglie_matter_signature_isotope_carbon_io_v1` folgende Claims

### Claim CISO1
Die Wellen-Schicht reagiert auch im Carbon-Block systematisch auf isotopische Massenvariation.

### Claim CISO2
Die strukturgetragenen QC-Deskriptoren bleiben zwischen `12C` und `13C` im Minimalfall invariant.

### Claim CISO3
Die kombinierte Signatur zeigt keinen chaotischen Ordnungswechsel, sondern eine kontrollierte Verschiebung entlang der Wellenachse.

### Claim CISO4
Der Carbon-Block generalisiert den H/D/T-Befund über den Wasserstoff-Spezialfall hinaus.

### Claim CISO5
Wenn der Block gelingt, stützt er die Arbeitshypothese, dass Wellen- und Strukturanteil der Signatur auch bei einer chemisch zentralen Atomsorte methodisch getrennt auslesbar bleiben.

---

## 2. Unmittelbare Minimalerwartung

Für den ersten Carbon-Isotopenblock ist zu erwarten:

- `12C` und `13C` unterscheiden sich in der Wellen-Schicht systematisch
- `valence_electron_count` bleibt gleich
- `shell_closure_score` bleibt gleich
- die kombinierte Signatur verschiebt sich geordnet und nicht sprunghaft
- der Befund bleibt strukturell analog zum H/D/T-Block

Diese Erwartung dient als Testhorizont, nicht als Vorabbestätigung.

---

## 3. Pflichttests

### 3.1 Reine Wellenantwort

Vergleich von:
- `mass_only_ordering`
- `wave_signature_ordering`

Leitfrage:

> Reagiert die Wellen-Schicht im Carbon-Block so, wie es die de-Broglie-Logik der Massenskala erwarten lässt?

### 3.2 Strukturinvarianz

Prüfen:
- `valence_electron_count`
- `shell_closure_score`

Leitfrage:

> Bleiben die strukturgetragenen Größen zwischen `12C` und `13C` invariant?

### 3.3 Kombinierte Signatur

Vergleich von:
- `wave_signature_ordering`
- `combined_signature_ordering`

Leitfrage:

> Bleibt die kombinierte Ordnung kontrolliert und lesbar, wenn nur die isotopische Masse variiert?

### 3.4 Delta relativ zur Massenordnung

Vergleich von:
- `matter_sensitive_delta_wave`
- `matter_sensitive_delta_isotope_carbon`

Leitfrage:

> Wird sichtbar, dass Struktur- und Wellenbeitrag auch im Carbon-Fall unterschiedliche Rollen tragen?

### 3.5 Carbon-Generalisation

Prüfen:
- Analogie des Musters zu H/D/T
- Strukturinvarianz-Flags
- `carbon_generalization_flag`

Leitfrage:

> Ist der Carbon-Block ein echter Generalisierungstest und nicht bloß ein zufälliger Zweierlauf?

---

## 4. Weiterführende Tests

### 4.1 Optional `14C`
Später prüfen:
- `14C` als zusätzlicher Massenpunkt

Leitfrage:

> Bleibt die Carbon-Logik auch bei einem dritten Isotop konsistent?

### 4.2 Vergleich mit H/D/T
Direkt vergleichen:
- H/D/T
- `12C` / `13C`

Leitfrage:

> Ist der Carbon-Befund nur analog oder zeigt er bereits neue Charakteristika eines schwereren, valenzreicheren Atoms?

### 4.3 Spätere Brücke zu kollektiver Kohlenstofforganisation
Noch nicht in diesem Block, aber perspektivisch relevant:
- Graphit
- Diamant
- Graphen
- Fullerene

Leitfrage:

> Wie viel der späteren Materialvielfalt ist bereits in der atomaren Carbon-Signatur angelegt?

---

## 5. Entscheidungslogik

### Unterstützt

Der Carbon-Block gilt als unterstützt, wenn:

- die Wellen-Schicht isotopensensitiv reagiert
- die Struktur-Schicht invariant bleibt
- die kombinierte Signatur kontrolliert verschoben wird
- und der H/D/T-Befund methodisch sauber generalisiert wird

### Teilweise unterstützt

Der Block gilt als teilweise unterstützt, wenn:

- die Richtung sichtbar ist,
- aber die Reaktion schwach bleibt
- oder die Generalisierung noch nicht klar genug lesbar ist

### Nicht unterstützt

Der Block gilt als nicht unterstützt, wenn:

- Strukturgrößen im Minimalfall nicht stabil bleiben
- die kombinierte Ordnung chaotisch reagiert
- oder sich kein sauberer Generalisierungseffekt gegenüber H/D/T zeigt

---

## 6. Kritische Gegenfrage

Die zentrale Gegenfrage lautet:

> Wenn der Carbon-Block die H/D/T-Logik nicht sauber reproduziert, ist dann die bisherige Achsentrennung nur für sehr einfache Spezies stabil?

Diese Gegenfrage bleibt ausdrücklich offen.

---

## 7. Arbeitsfrage

Die Arbeitsfrage dieses Blocks lautet:

> Kann Kohlenstoff als chemisch zentrale Atomsorte den ersten harten Achsentrennungsbefund des H/D/T-Blocks über Wasserstoff hinaus bestätigen?

Genau daran entscheidet sich der eigentliche Wert dieses Tests.

---

## 8. Bottom line

`debroglie_matter_signature_isotope_carbon_tests_v1` dient dazu, den erfolgreichen H/D/T-Minimaltest an einer inhaltlich deutlich reicheren Atomsorte zu generalisieren.

Die operative Leitformel lautet:

> Wenn auch Carbon zeigt: gleiche Struktur, andere Masse, kontrollierte Wellenverschiebung — dann trägt der Isotopenbefund über Wasserstoff hinaus.
