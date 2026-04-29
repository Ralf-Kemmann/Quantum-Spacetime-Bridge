# BMC-04-v3 — Soft-Repair / Balanced-Objective Variante

## Zweck

BMC-04-v3 soll den Bereich treffen, den v1 und v2 jeweils verfehlt haben:

- **v1**: genug Organisationsstörung, aber Preservation zu schwach
- **v2**: Preservation perfekt, aber Organisationsstörung kollabiert

BMC-04-v3 soll deshalb **nicht** nur Preservation maximieren, sondern einen **balancierten Zielraum** suchen:

\[
\text{Preservation hoch}
\quad\cap\quad
\text{Disruption nicht trivial}
\]

Die Leitfrage bleibt:

\[
\text{Organisation} > \text{bloße Verteilung} \, ?
\]

aber der Suchmechanismus wird intelligenter.

---

## 1. Kernidee

Statt die Repair-Phase nur nach minimalem Strength-Fehler zu steuern, bekommt v3 eine **balancierte Zielfunktion**:

\[
J = \lambda_P \, P_{\text{total}} + \lambda_D \, D_{\text{org}}
\]

oder, äquivalent als Fehlerform:

\[
L = \alpha \, E_{\text{pres}} - \beta \, D_{\text{org}}
\]

mit:

- \(P_{\text{total}}\): Gesamtqualität der Preservation
- \(D_{\text{org}}\): Organisationsdisruption
- \(E_{\text{pres}}\): Preservation-Fehler
- \(\lambda_P, \lambda_D, \alpha, \beta > 0\): Balancierungsgewichte

### Arbeitsintuition
Nicht:
- „so nah wie möglich zurück zur Baseline“

sondern:
- „so gut wie nötig Preservation halten“
- **und gleichzeitig**
- „so viel Umorganisation wie möglich im zulässigen Korridor erhalten“

---

## 2. Soft-Repair statt Hard-Repair

### 2.1 Problem von v2
v2 minimiert faktisch:

\[
E_{\text{strength}} = \sum_{v\in V} |s'(v)-s(v)|
\]

bis zum quasi perfekten Wert.

Dadurch wird aber die Organisation mitrepariert.

### 2.2 Lösung in v3
v3 führt **Zielkorridore** statt **Perfektionszwang** ein.

Beispiel:

- Weight multiset: exakt erhalten
- Degree: exakt erhalten
- Strength: **nur innerhalb eines Zielbands**
- Shell counts: **nur innerhalb eines Zielbands** oder exakt, je nach Variante

Dann stoppt die Repair-Phase, sobald die Zielkorridore erfüllt sind, **nicht erst** bei maximaler Rückannäherung an die Baseline.

---

## 3. Zielkorridore

### 3.1 Harte Constraints
Diese bleiben hart:

#### Weight multiset preservation
\[
P_w = 1
\]

#### Degree preservation
für degree-preserving Varianten:
\[
P_d = 1
\]

### 3.2 Weiche Constraints
Diese werden soft:

#### Strength preservation target band
zum Beispiel:

\[
P_s \ge \theta_s^{\min}
\]

mit erster plausibler Startwahl:

\[
\theta_s^{\min} \in [0.985, 0.995]
\]

nicht zwingend 1.0.

#### Shell count preservation target band
falls gebraucht:

\[
P_{\sigma} \ge \theta_{\sigma}^{\min}
\]

je nach Variante.

---

## 4. Organisationsdisruption als explizite Zielgröße

v3 braucht eine explizite Disruptionskomponente, damit Repair nicht zurück in triviale Baseline-Nähe fällt.

### 4.1 Naheliegende Disruptionsgrößen

#### A. Shell arrangement shift
\[
\Delta_{\text{shell-rank}}
\]

#### B. Pair-neighborhood consistency shift
\[
\Delta_{\text{pair-neigh}}
\]

#### C. Endpoint arrangement shift
\[
\Delta_{\text{endpoint}}
\]

#### D. Kompositmaß
\[
D_{\text{org}} =
\frac{
\Delta_{\text{endpoint}}
+
\Delta_{\text{disp}}
+
\Delta_{\text{pair-neigh}}
+
\Delta_{\text{shell-rank}}
+
\Delta_{\text{shell-boundary}}
}{m}
\]

mit \(m\) = Zahl verfügbarer Komponenten.

### 4.2 Empfehlung
Für v3 würde ich als erste Zielfunktion **nicht** den finalen `arrangement_signal_score` selbst maximieren, sondern zunächst ein internes Disruptionsziel wie:

\[
D_{\text{repair}}
=
\Delta_{\text{pair-neigh}} + \Delta_{\text{shell-rank}}
\]

verwenden.

---

## 5. Balanced Objective

### 5.1 Fehlerform
Definiere Preservation-Fehler z. B. als:

\[
E_{\text{pres}}
=
c_s \cdot (1-P_s)
+
c_{\sigma} \cdot (1-P_{\sigma})
+
c_b \cdot (1-P_b)
\]

je nach Variante.

Dann:

\[
L = E_{\text{pres}} - \beta D_{\text{org}}
\]

und wir akzeptieren einen Tausch / Swap / Reassignment-Schritt, wenn:

\[
L_{\text{new}} < L_{\text{old}}
\]

### 5.2 Korridorform
Noch robuster für den Einstieg:

1. zuerst harte Constraints prüfen  
2. dann nur Zustände akzeptieren, die
   \[
   P_s \ge \theta_s^{\min}
   \]
   und ggf.
   \[
   P_{\sigma} \ge \theta_{\sigma}^{\min}
   \]
   erfüllen  
3. innerhalb dieser zulässigen Menge den Zustand mit maximalem \(D_{\text{org}}\) bevorzugen

---

## 6. Repair-Logik in v3

### 6.1 Initiale Zuweisung
Wie in v2:
- greedy constrained assignment

### 6.2 Repair-Kandidaten
Danach:
- paarweise Gewichtsswaps
- ggf. nur innerhalb zulässiger Shell-Klassen
- ggf. später auch 3-Zyklen statt nur 2-Swaps

### 6.3 Akzeptanzregel
Nicht mehr:
- nur Strength-Fehler senken

sondern:

#### Fall A — außerhalb Zielkorridor
Wenn \(P_s < \theta_s^{\min}\), dann Schritte bevorzugen, die \(P_s\) verbessern.

#### Fall B — im Zielkorridor
Wenn \(P_s \ge \theta_s^{\min}\), dann Schritte bevorzugen, die \(D_{\text{org}}\) erhöhen, **ohne** den Korridor wieder zu verlassen.

---

## 7. Varianten in v3

### 7.1 `degree_strength_weight_preserved`
Hier ist der Suchraum größer.  
Das ist wahrscheinlich die beste erste v3-Testvariante.

### Ziel
\[
P_w = 1,\quad P_d = 1,\quad P_s \ge \theta_s^{\min}
\]

und dann

\[
D_{\text{org}} \text{ maximal im Zielkorridor}
\]

### 7.2 `degree_strength_shellcount_preserved`
Hier ist der Suchraum enger.

### Ziel
\[
P_w = 1,\quad P_d = 1,\quad P_s \ge \theta_s^{\min},\quad P_{\sigma}=1
\]

aber genau hier droht wieder Trivialisierung.  
Deshalb sollte diese Variante erst nach der lockereren Variante geprüft werden.

---

## 8. Neue Entscheidungslogik

v3 sollte zusätzlich zwischen drei Fällen unterscheiden:

### 8.1 Preservation-failed
wie bisher:
\[
P_{\text{required}} < \theta
\]

→ `test_not_informative`

### 8.2 Preservation-met but disruption-trivial
\[
P_{\text{required}} \text{ erfüllt}
\quad\text{und}\quad
D_{\text{org}} \approx 0
\]

→ `overconstrained_or_trivialized`

### 8.3 Preservation-met and disruption-readable
\[
P_{\text{required}} \text{ erfüllt}
\quad\text{und}\quad
D_{\text{org}} > \theta_D
\]

→ `organization_sensitive`

---

## 9. Neue Output-Felder

Zusätzlich zu v2 würde ich aufnehmen:

- `repair_mode`
  - `hard_repair`
  - `soft_repair`
  - `balanced_objective`

- `strength_target_min`
- `shell_target_min`
- `preservation_error_score`
- `organization_objective_score`
- `balanced_objective_score`
- `repair_exit_status`
  - `target_band_reached`
  - `max_iterations_reached`
  - `collapsed_to_trivial_solution`

---

## 10. Empfohlene erste Parameter

Für die erste v3-Testrunde würde ich nehmen:

### Für `degree_strength_weight_preserved`
- \(\theta_s^{\min} = 0.99\)

### Für `degree_strength_shellcount_preserved`
- \(\theta_s^{\min} = 0.985\)
- \(P_{\sigma}=1\)

### Disruptionsziel
\[
D_{\text{repair}} =
\Delta_{\text{pair-neigh}} + \Delta_{\text{shell-rank}}
\]

### Abbruchregel
Stoppe, wenn:
- Zielkorridor erreicht
- und keine Verbesserung von \(D_{\text{repair}}\) in den letzten \(k\) Schritten mehr erfolgt

---

## 11. Empfohlene erste Testreihe

### Serie V3-S1
Variante:
- `degree_strength_weight_preserved`

mit:
- `low`
- `medium`
- `high`

### Erwartung
Hier habt ihr die beste Chance auf:

- saubere Preservation
- nichttriviale Umorganisation
- lesbaren arrangement signal

### Serie V3-S2
Danach:
- `degree_strength_shellcount_preserved`

mit denselben Stufen.

---

## 12. Schärfste Maschinenraumdiagnose

v1 und v2 zusammen haben im Grunde bereits die Notwendigkeit von v3 bewiesen:

\[
\text{v1: } \text{Disruption ja, Preservation nein}
\]

\[
\text{v2: } \text{Preservation ja, Disruption nein}
\]

Daraus folgt fast zwingend:

\[
\text{v3: } \text{Preservation hoch, Disruption nicht trivial}
\]

---

## 13. Kurzfassung für die direkte Umsetzung

### Kernsatz
BMC-04-v3 ersetzt „perfekte Repair“ durch „zielkorridorbasierte Repair mit Disruptionsinteresse“.

### Minimalform
Finde einen Zustand mit:

\[
P_w = 1,\quad P_d = 1,\quad P_s \ge \theta_s^{\min}
\]

und innerhalb dieser Menge:

\[
D_{\text{org}} \text{ möglichst groß}
\]

### Schärfste Formel
\[
\text{informative regime}
=
\text{Preservation hoch}
\;\cap\;
\text{Disruption nicht trivial}
\]

---

## Bottom line

BMC-04-v3 sollte als **soft-repair / balanced-objective Variante** gebaut werden.

Nicht mehr:
- maximale Rückannäherung an die Baseline

sondern:
- genug Preservation
- plus bewusst erhaltene Umorganisation

Die beste erste praktische Route ist:

1. zuerst `degree_strength_weight_preserved`
2. dann `degree_strength_shellcount_preserved`
3. Repair über Zielkorridor statt Perfektionszwang
4. Disruptionsziel explizit in die Akzeptanzregel einbauen
