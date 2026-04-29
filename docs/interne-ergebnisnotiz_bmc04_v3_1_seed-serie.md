# Interne Ergebnisnotiz  
## BMC-04-v3.1 Seed-Serie — erster robuster organizationssensitiver Befund

## Zweck

Diese kurze Notiz hält den aktuellen Zwischenstand von **BMC-04-v3.1** fest.

Sie dient als interne Projektkonsolidierung und soll knapp dokumentieren:

- was getestet wurde
- was der belastbare Befund ist
- was daraus folgt
- und was ausdrücklich noch **nicht** folgt

---

## 1. Testkontext

BMC-04 wurde als Folgeblock aus der Deep-Research-Außenkartierung entwickelt, um die Kernfrage

\[
\text{Organisation} > \text{bloße Verteilung} \, ?
\]

methodisch sauberer zu prüfen.

Die Entwicklung verlief bisher in drei Stufen:

- **v1:** genügend Organisationsstörung, aber Preservation zu schwach  
- **v2:** Preservation perfekt, aber Organisationsstörung kollabiert  
- **v3 / v3.1:** Soft-repair / balanced-objective-Ansatz mit Zielkorridor

BMC-04-v3.1 ist aktuell die erste Version, in der ein **informativer Korridor** praktisch getroffen wurde.

---

## 2. Getestete Variante

In der aktuellen kleinen Seed-Serie wurde die Variante

- `degree_strength_weight_preserved`

unter BMC-04-v3.1 untersucht.

### Harte Constraints
- Weight multiset exakt erhalten
- Degree exakt erhalten

### Weiche bzw. corridor-basierte Constraint
- Strength preservation innerhalb eines arbeitsfähigen Ziel-/Akzeptanzbereichs

### Ziel
Nichttriviale Organisationsstörung erhalten, ohne die grobe Verteilungsseite zu verlieren.

---

## 3. Seed-Serie

Ausgewertet wurden die Seeds:

- `101`
- `123`
- `211`
- `307`
- `509`

Alle Läufe wurden unter derselben v3.1-Logik gefahren.

---

## 4. Kurzresultat

Alle fünf Läufe wurden klassifiziert als:

- `preservation = passed`
- `decision_label = organization_sensitive`

Das ist der bisher wichtigste Befund.

---

## 5. Zahlenbereich

Die Serie zeigt folgende Bereiche:

### Strength preservation
ungefähr

\[
0.967 \lesssim P_s \lesssim 0.984
\]

### Arrangement signal
ungefähr

\[
0.280 \lesssim A \lesssim 0.293
\]

Also operational:

\[
P_w = 1,\quad P_d = 1,\quad P_s \approx 0.97\text{–}0.98,
\quad
A \approx 0.28\text{–}0.29
\]

bei konsistentem Entscheidungslabel:

\[
\texttt{organization\_sensitive}
\]

---

## 6. Inhaltliche Lesart

Die Serie stützt derzeit folgende vorsichtige Aussage:

> Unter erhaltener grober Verteilungsstruktur bleibt eine lesbare, seed-robuste organizationssensitive Reaktion bestehen.

Oder in formaler Kurzfassung:

\[
\Delta_{\text{organization-broken}} > 0
\quad\text{bei}\quad
\Delta_{\text{distribution-preserved}} \approx 0
\]

nicht im streng-theoretischen Grenzsinne, aber im **operativen Testsinn**.

Das ist ein erster robuster methodischer Zwischenbefund zugunsten der Arbeitshypothese:

\[
\text{Organisation} > \text{bloße Verteilung}
\]

---

## 7. Warum dieser Befund wichtig ist

Der Wert der Serie liegt nicht nur in einem einzelnen schönen Lauf, sondern in der Kombination aus:

- bestandener Preservation
- nichttrivialer Disruption
- konsistenter Decision-Logik
- Stabilität über mehrere Seeds

Das unterscheidet die Serie klar von:
- reinem Tuning
- einem einmaligen lucky shot
- oder einem Test, der nur auf einem Sonderseed lebt

Der aktuelle Befund ist deshalb **methodisch ernst zu nehmen**.

---

## 8. Was daraus noch nicht folgt

Trotz des positiven Zwischenstands folgt daraus ausdrücklich noch **nicht**:

1. dass bereits ein formaler Beweis für  
   \[
   \text{Organisation} > \text{bloße Verteilung}
   \]
   vorliegt

2. dass die verwendete organization objective bereits die tiefste richtige Strukturgröße ist

3. dass die aktuelle Variante `degree_strength_weight_preserved` schon den gesamten strukturellen Kern des Projekts abdeckt

4. dass Shell, Block oder andere Mesostrukturen damit schon endgültig gegeneinander entschieden wären

5. dass die BMC-04-Linie bereits eine vollständige Theorieaussage trägt

Die Serie ist also **stark als Methodensignal**, aber noch **nicht** als Endaussage.

---

## 9. Aktueller Projektwert

Für das Projekt bedeutet die Serie im Moment:

### A. Der informative Korridor existiert
Das ist vielleicht der wichtigste methodische Punkt.

### B. Soft-repair / balanced-objective war der richtige Schritt
v3.1 ist demnach nicht bloß kosmetisch, sondern strukturell sinnvoll.

### C. BMC-04 ist jetzt ein echter Arbeitsblock
Nicht mehr nur ein Entwurf, sondern ein verwendbarer Testpfad.

### D. Die decision logic ist jetzt besser an die realen Zahlen angepasst
Das vermeidet eine künstlich zu schwache Interpretation tatsächlich lesbarer Läufe.

---

## 10. Empfohlene nächste Schritte

Die sinnvollsten nächsten Schritte sind derzeit:

1. **diese Ergebnisnotiz festhalten**  
2. **kleine Strength-/Threshold-Ladder** innerhalb v3.1 prüfen  
3. **Shellcount-Variante** in derselben Logik nachziehen  
4. später:
   - kleine Statistik über Seed-Serie
   - Mittelwert / Streuung
   - evtl. kompakte Plotdarstellung

---

## 11. Schärfste Kurzfassung

> BMC-04-v3.1 liefert erstmals einen kleinen seed-robusten Befund, in dem bei erhaltener grober Verteilungsstruktur eine lesbare organizationssensitive Reaktion bestehen bleibt.

Noch kürzer:

> **Der informative Korridor ist gefunden.**

---

## Bottom line

BMC-04-v3.1 ist aktuell der erste Stand, in dem die BMC-04-Linie methodisch wirklich trägt.

Die knappste ehrliche Projektformel lautet derzeit:

\[
P_w = 1,\quad P_d = 1,\quad P_s \approx 0.97\text{–}0.98,
\quad
A \approx 0.28\text{–}0.29
\]

mit seed-robustem Label:

\[
\texttt{organization\_sensitive}.
\]

Das ist kein Endbeweis, aber ein echter interner Zwischenbefund.
