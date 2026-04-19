# bridge_mechanics_tests_v1

## 1. Direkt aus `bridge_mechanics_v1` folgende Claims

### Claim M1
Es gibt mindestens eine kleine Kopplungsform, die `theta` und `A` nichttrivial, aber kontrolliert koppelt.

### Claim M2
Eine tragfähige Kopplungsform verbessert oder stabilisiert den Brückenzustand relativ zur ungekoppelten Baseline.

### Claim M3
Bindung/Stabilisierung und Informations-/Übergangsstruktur sind nicht vollständig deckungsgleich.

### Claim M4
`negative` und `abs` reagieren auf brauchbare Kopplung systematisch günstiger als `positive`.

### Claim M5
Eine physikalisch plausible Brückenmechanik zeigt `phase_influence` klein, aber nicht null, zumindest in den signalhaltigen Fällen.

---

## 2. Unmittelbare Minimalerwartung

Für die derzeit signalhaltigen Datensätze erwartet der Block zunächst:

- `multiplicative` oder `dual_channel` wirken plausibler als rein additive Kopplung
- `negative` und `abs` bleiben im Vorteil
- `positive` bleibt schwächer, instabiler oder kanalärmer
- `macro` zeigt eher kleine, stabile Kopplung
- `coherent` zeigt stärkere, aber noch kontrollierte Kopplung

Diese Minimalerwartung ist noch keine Bestätigung, sondern eine erste Sollbruchkarte für die Mechaniktests.

---

## 3. Pflichttests

### 3.1 Baseline-vs-Coupling

Vergleich von:

- `A0` vs `A_eff`
- `phi_geom_baseline` vs `phi_geom_coupled`
- `d_eff_baseline` vs `d_eff_coupled`

Leitfrage:

> Verbessert die Kopplung überhaupt etwas oder macht sie nur Lärm?

### 3.2 Exportklassenvergleich

Vergleich von:

- `negative`
- `abs`
- `positive`

Leitfrage:

> Bleibt die bekannte Ordnung unter Kopplung erhalten oder kippt sie?

### 3.3 Regimevergleich

Vergleich von:

- `macro`
- `coherent`

Leitfrage:

> Zeigt sich eine sinnvolle Regimeantwort statt bloßer Instabilität?

### 3.4 Kanaltrennungstest

Nur für `dual_channel` oder kanalnahe Diagnostik:

- `binding_channel_score`
- `information_channel_score`

Leitfrage:

> Sind Bindung und Information wirklich partiell getrennt lesbar?

### 3.5 Geometry-response-Test

Leitfrage:

> Wird `d_eff` unter Kopplung geometrisch lesbarer, gleich gut oder schlechter?

---

## 4. Weiterführende Tests

### 4.1 Kleiner Lambda-Sweep

Pflichtwerte:

- `0.0`
- `0.05`
- `0.10`
- `0.20`

Leitfrage:

> Gibt es ein kleines tragfähiges Kopplungsfenster?

### 4.2 Sensitivitätsfall `n1a_alpha`

Nur mit der besten Kopplungsform aus den Hauptläufen.

Leitfrage:

> Trägt dieselbe Mechanik im Sensitivitätsfall noch oder zerfällt sie?

### 4.3 Optional später

- kleine `tau`-Variation
- alternative Neighborhood
- Benchmark gegen triviale Referenzkopplung

---

## 5. Entscheidungslogik

### Unterstützt

Der Block gilt als unterstützt, wenn:

- mindestens eine Kopplung stabil arbeitet
- `delta_vs_baseline` nicht negativ dominiert
- `negative` und `abs` günstiger reagieren als `positive`
- Kanaltrennung oder Regimeantwort sinnvoll lesbar werden

### Teilweise unterstützt

Der Block gilt als teilweise unterstützt, wenn:

- nur einzelne Datensätze tragen
- oder der Effekt vorhanden, aber instabil oder stark regimeselektiv bleibt

### Nicht unterstützt

Der Block gilt als nicht unterstützt, wenn:

- alle Kopplungsformen bloß Rauschen erzeugen
- `theta` entweder praktisch irrelevant oder destruktiv ist
- keine sinnvolle Mechanikantwort erkennbar wird

---

## 6. Arbeitsfrage

Die zentrale Frage des Blocks lautet:

> Ist die de-Broglie-Brücke nur als Zustand beschreibbar, oder lässt sich bereits eine minimale, testbare und funktional gegliederte Kopplungsmechanik identifizieren?

Genau diese Frage entscheidet, ob die Brücke vom deskriptiven Zwischenzustand in Richtung einer physikalisch härteren Mechanik weitergetragen werden kann.

---

## 7. Bottom line

`bridge_mechanics_tests_v1` dient dazu, nicht nur das Vorhandensein eines Brückenzustands zu prüfen, sondern die Kopplungsmechanik selbst gegen klare Minimaltests laufen zu lassen.

Die operative Leitformel lautet:

> Wir testen, ob und wie eine kleine Kopplung zwischen `theta` und `A` den Brückenzustand stabilisiert, funktional gliedert und geometrisch lesbarer macht.
