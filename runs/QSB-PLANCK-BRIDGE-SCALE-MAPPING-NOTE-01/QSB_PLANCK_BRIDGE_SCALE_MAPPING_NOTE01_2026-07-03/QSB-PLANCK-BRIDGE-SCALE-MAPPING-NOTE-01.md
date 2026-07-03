# QSB-PLANCK-BRIDGE-SCALE-MAPPING-NOTE-01
## Arbeitsfassung v0.1 — Compton-Schwarzschild-Mapping als Planck-Bridge-Gate

**Stand:** 2026-07-03  
**Status:** scale_mapping_candidate  
**Physical claim release:** blocked_no_physics_claim  
**Review gate:** requires_dimensional_and_physical_review

---

## 1. Zweck

Diese Note hält zwei komplementäre Mapping-Ideen für den QSB-Planck-Bridge-Resonator fest.

Die Compton-Skala und der Schwarzschild-Radius werden dabei nicht als Beweis für eine mikroskopische Resonator-Entität verwendet, sondern als algebraische und dimensionsanalytische Grenzmarker. QSB verwendet sie als **Scale-Gate**: eine formale Markierung der Zone, in der Quantenzustands-Lokalisierung und gravitative Radiusbildung in dieselbe Größenordnung geraten.

Die rote Linie:

```text
Die Mapping-Ideen markieren einen Prüfbereich.
Sie beweisen keinen Planck-Bridge-Resonator.
```

---

## 2. Ausgangsgleichungen

Compton-Skala:

```text
lambda_C = hbar / (m * c)
```

Schwarzschild-Radius:

```text
r_s = 2 * G * m / c^2
```

Hierbei sind:

```text
hbar = reduziertes Planck-Wirkungsquantum
G    = Gravitationskonstante
c    = Lichtgeschwindigkeit
m    = Masse
```

---

## 3. Mapping-Idee A — direkter Skalenquotient

### 3.1 Definition

```text
beta_B = r_s / lambda_C
```

Einsetzen ergibt:

```text
beta_B = [2 * G * m / c^2] / [hbar / (m * c)]
```

also:

```text
beta_B = 2 * G * m^2 / (hbar * c)
```

### 3.2 Bridge-Bedingung

Die Planck-nahe Bridge-Zone ist erreicht, wenn:

```text
beta_B ≈ 1
```

Für exaktes Matching:

```text
r_s = lambda_C
```

folgt:

```text
2 * G * m^2 = hbar * c
```

und damit:

```text
m_B = sqrt(hbar * c / (2 * G))
```

also:

```text
m_B = m_P / sqrt(2)
```

wenn:

```text
m_P = sqrt(hbar * c / G)
```

### 3.3 QSB-Lesart

`beta_B` ist ein dimensionsloser Gate-Parameter.

```text
beta_B << 1
```

Quantenseite dominiert; die Compton-Skala ist viel größer als der Schwarzschild-Radius.

```text
beta_B ≈ 1
```

Interface-Zone; Compton-Skala und Schwarzschild-Radius fallen größenordnungsmäßig zusammen.

```text
beta_B >> 1
```

Gravitative Radiusseite dominiert.

---

## 4. Mapping-Idee B — zweiseitiges Speed-Matching mit Herkunftsindizes

### 4.1 Motivation

Die zweite Idee trennt die Herkunftsseiten ausdrücklich.

Nicht sofort:

```text
m_comp = m_schwarz
```

sondern zunächst:

```text
m_comp    = Masse auf der Compton-/Quantenseite
m_schwarz = Masse auf der Schwarzschild-/Gravitationsseite
```

Dadurch entsteht ein Mapping-Raum statt nur ein einzelner Matching-Punkt.

### 4.2 Compton-Seite nach c aufgelöst

Aus:

```text
lambda_C = hbar / (m_comp * c)
```

folgt:

```text
c_comp = hbar / (m_comp * lambda_C)
```

### 4.3 Schwarzschild-Seite nach c aufgelöst

Aus:

```text
r_s = 2 * G * m_schwarz / c^2
```

folgt:

```text
c_schwarz = sqrt(2 * G * m_schwarz / r_s)
```

Es wird die positive Wurzel genommen, da eine Geschwindigkeitsskala betrachtet wird.

### 4.4 Bridge-Matching

Die Matching-Bedingung lautet:

```text
c_comp = c_schwarz
```

also:

```text
hbar / (m_comp * lambda_C)
=
sqrt(2 * G * m_schwarz / r_s)
```

Quadriert:

```text
hbar^2 / (m_comp^2 * lambda_C^2)
=
2 * G * m_schwarz / r_s
```

Umgestellt:

```text
hbar^2 * r_s
=
2 * G * m_schwarz * m_comp^2 * lambda_C^2
```

Diese Gleichung definiert ein Compton-Schwarzschild-Speed-Matching mit getrennten Herkunftsindizes.

---

## 5. Dimensionsloser Speed-Matching-Parameter

```text
Xi_CS = c_comp^2 / c_schwarz^2
```

Einsetzen ergibt:

```text
Xi_CS =
[hbar^2 / (m_comp^2 * lambda_C^2)]
/
[2 * G * m_schwarz / r_s]
```

also:

```text
Xi_CS =
hbar^2 * r_s
/
(2 * G * m_schwarz * m_comp^2 * lambda_C^2)
```

Die Bridge-Bedingung lautet:

```text
Xi_CS = 1
```

Interpretation:

```text
Xi_CS < 1
```

Die Compton-Seite bildet auf eine kleinere effektive Geschwindigkeitsskala ab als die Schwarzschild-Seite.

```text
Xi_CS = 1
```

Compton- und Schwarzschild-Seite sind im Mapping konsistent.

```text
Xi_CS > 1
```

Die Compton-Seite bildet auf eine größere effektive Geschwindigkeitsskala ab als die Schwarzschild-Seite.

---

## 6. Verhältnis beider Mapping-Ideen

Die beiden Ideen widersprechen sich nicht.

### Idee A

```text
beta_B = r_s / lambda_C
```

fragt:

```text
Wie nah sind die beiden Längenskalen beieinander?
```

### Idee B

```text
Xi_CS = c_comp^2 / c_schwarz^2
```

fragt:

```text
Bilden beide Seiten auf dieselbe effektive Grenzgeschwindigkeit ab,
wenn ihre Herkunftsgrößen getrennt markiert werden?
```

Damit entsteht eine zweistufige QSB-Mapping-Logik:

```text
Level 1: Skalen-Gate über beta_B
Level 2: Bridge-Konsistenz über Xi_CS
```

---

## 7. Spezialfälle

### 7.1 Gleiche Länge

Wenn zusätzlich gilt:

```text
lambda_C = r_s = L_B
```

dann folgt aus dem Speed-Matching:

```text
L_B = hbar^2 / (2 * G * m_schwarz * m_comp^2)
```

Damit hängt die Bridge-Länge von einem Massenpaar ab:

```text
(m_comp, m_schwarz)
```

### 7.2 Gleiche Masse

Wenn zusätzlich gilt:

```text
m_comp = m_schwarz = m
```

wird:

```text
L_B = hbar^2 / (2 * G * m^3)
```

Wird außerdem die physikalische Lichtgeschwindigkeit als gemeinsame Referenz eingesetzt, fällt man auf die bekannte Planck-nahe Matching-Bedingung zurück:

```text
m = sqrt(hbar * c / (2 * G))
```

also:

```text
m = m_P / sqrt(2)
```

---

## 8. Claim Boundary

### Erlaubt

```text
Das Verhältnis r_s / lambda_C und das zweiseitige Speed-Matching
c_comp = c_schwarz liefern algebraische Mapping-Gates für die
Compton-Schwarzschild-Übergangszone.
```

```text
Die Parameter beta_B und Xi_CS können verwendet werden, um Kandidaten
für eine Planck-Bridge-Skalenzone formal zu markieren.
```

### Nicht erlaubt

```text
Damit ist der Planck-Bridge-Resonator bewiesen.
```

```text
Die Lichtgeschwindigkeit wird neu bestimmt.
```

```text
Raumzeit besteht aus solchen Resonatoren.
```

### Saubere Formulierung

```text
Die Lichtgeschwindigkeit wird nicht als frei variabler physikalischer
Parameter behandelt, sondern als Referenzgröße beziehungsweise als
algebraische Matching-Koordinate. Die Größen c_comp und c_schwarz markieren,
aus welcher theoretischen Seite eine Geschwindigkeitsskala rekonstruiert wird.
```

---

## 9. DWH-Statusvorschlag

```text
work_package = QSB-PLANCK-BRIDGE-SCALE-MAPPING-NOTE-01
claim_status = scale_mapping_candidate
physical_claim_release = blocked_no_physics_claim
review_status = requires_dimensional_and_physical_review
```

---

## 10. Kernsatz

Die direkte Ratio `beta_B = r_s / lambda_C` markiert die Nähe von Quantenlokalisierung und gravitativer Radiusbildung.

Das zweiseitige Speed-Matching `Xi_CS = c_comp^2 / c_schwarz^2` markiert, ob Compton-Seite und Schwarzschild-Seite algebraisch auf dieselbe Grenzgeschwindigkeit abbilden.

Gemeinsam liefern beide Mapping-Ideen ein claim-sauberes Scale-Gate für die Planck-Bridge-Zone.
