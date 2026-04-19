# debroglie_matter_signature_isotope_test_v1

## 1. Ziel

Dieses Dokument definiert den nächsten Prüfblock für die materialsensitive Signaturarchitektur:
den **Isotopen-Test**.

Die Grundidee ist methodisch besonders stark, weil Isotope bei weitgehend gleicher
Elektronenstruktur unterschiedliche Massen tragen. Dadurch entsteht ein sauberer
Trennschnitt zwischen:

- **Wellen-/Massenskala**
- **innerer elektronischer Struktur**

Leitfrage:

> Bleibt die strukturgetragene Signatur bei isotopischer Massenvariation stabil, während sich
die de-Broglie-/Wellenachse systematisch verschiebt?

---

## 2. Motivation

Die bisherigen Projektblöcke haben gezeigt:

- reine de-Broglie-Läufe erzeugen robuste, aber stark massen- bzw. längenskalengetragene Ordnung
- VDW öffnet eine stoffliche Nichtidealitätsachse
- Ionisierungsenergie wirkt als atomnahe Stärkeachse
- Valenzelektronenzahl wirkt als atomnahe Strukturachse
- shell_closure verfeinert diese Strukturachse

Damit stellt sich nun eine entscheidende methodische Frage:

> Was passiert, wenn die innere elektronische Struktur gleich bleibt, aber die Massenskala
geändert wird?

Genau dafür sind Isotope ideal.

---

## 3. Warum Isotope so wertvoll sind

Isotope eines Elements teilen im ersten Zugriff:

- gleiche Ordnungszahl
- gleiche Elektronenkonfiguration
- gleiche Valenzstruktur
- gleiche Grundlogik von Valenz- und Closure-Deskriptoren

Sie unterscheiden sich jedoch in:

- Kernmasse
- reduzierter Gesamtmassenskala
- daraus resultierend in der de-Broglie-Wellenlänge und abgeleiteten Wellen-Surrogaten

Damit liefern Isotope einen der saubersten denkbaren Tests für die Trennung von:

- **Wellenbasis**
- **Strukturbasis**

---

## 4. Grundhypothese

Die Arbeitshypothese dieses Blocks lautet:

> Wenn die materialsensitive Signaturarchitektur tatsächlich aus einer Wellen- und einer
Strukturseite besteht, dann sollten isotopische Änderungen primär die Wellenachse verschieben,
während strukturgetragene Deskriptoren weitgehend invariant bleiben.

Sauberer gesagt:

- Isotope testen die **Massensensitivität der Wellenachse**
- Isotope testen zugleich die **Robustheit der Strukturachse gegen bloße Massenvariation**

---

## 5. Erste Kandidaten

### 5.1 Minimaler erster Test
- protium (`¹H`)
- deuterium (`²H`)
- tritium (`³H`)

Warum dieser Einstieg?
- gleiche einfache Elektronenstruktur
- maximale methodische Klarheit
- direkte Massendifferenz
- sehr einfache erste Vergleichslogik

### 5.2 Nächste sinnvolle Paare
- `¹²C` vs. `¹³C`
- `¹⁴N` vs. `¹⁵N`

Warum diese Paare?
- gleiche Valenzstruktur
- gleiche Gruppenzugehörigkeit
- zusätzliche Prüfung, ob der H/D/T-Befund auch jenseits des Spezialfalls Wasserstoff trägt

---

## 6. Erwartete Signaturwirkung

### 6.1 Erwartung für die Wellen-Schicht
Die Wellenachse sollte isotopensensitiv sein, weil:

- Masse direkt in thermische Geschwindigkeit, Impuls und de-Broglie-Wellenlänge eingeht
- isotopische Massendifferenzen deshalb systematisch die Wellen-Surrogate verschieben

### 6.2 Erwartung für die Struktur-Schicht
Valenz- und Closure-Deskriptoren sollten in erster Näherung isotopeninvariant bleiben, weil:

- Elektronenkonfiguration gleich bleibt
- Valenzelektronenzahl gleich bleibt
- shell_closure-Proxy gleich bleibt

### 6.3 Erwartung für die kombinierte Signatur
Die kombinierte Signatur sollte deshalb nicht beliebig springen, sondern ein lesbares Muster zeigen:

- Wellenanteil verschiebt sich
- Strukturanteil bleibt stabil
- daraus resultiert ein kontrollierter Gesamtshift statt eines Strukturwechsels

---

## 7. Methodische Stärke des Blocks

Dieser Test ist deshalb so wichtig, weil er nicht bloß „noch mehr Daten“ erzeugt, sondern
eine echte Achsentrennung prüft.

Er fragt nicht:

- „macht die Signatur wieder irgendeine Ordnung?“

sondern:

- „lassen sich Wellen- und Strukturachse unter kontrollierter Variation sauber auseinanderhalten?“

Genau das macht den Isotopen-Test zu einem prüfsteinartigen Block.

---

## 8. Minimaler Run-Plan

### Run ISO-A
- nur `¹H`, `²H`, `³H`
- reine Wellen-Schicht

Ziel:
- prüfen, wie stark die de-Broglie-/Massenskala allein isotopensensitiv reagiert

### Run ISO-B
- `¹H`, `²H`, `³H`
- Wellen-Schicht + QC-Strukturachse (`valence_electron_count`)

Ziel:
- prüfen, ob die Strukturachse isotopenstabil bleibt und die kombinierte Ordnung kontrolliert reagiert

### Run ISO-C
- `¹H`, `²H`, `³H`
- Wellen-Schicht + QC-Strukturachse + `shell_closure`

Ziel:
- prüfen, ob die Feinstruktur ebenfalls isotopenstabil bleibt

### Run ISO-D optional
- `¹²C` / `¹³C`
- `¹⁴N` / `¹⁵N`

Ziel:
- testen, ob der Trennbefund auch jenseits des Wasserstofffalls trägt

---

## 9. Prüfbare Claims

### Claim ISO1
Die Wellen-Schicht reagiert systematisch auf isotopische Massenvariation.

### Claim ISO2
Die Struktur-Schicht bleibt gegenüber isotopischer Massenvariation weitgehend stabil.

### Claim ISO3
Die kombinierte Signatur zeigt bei Isotopen keine willkürliche Umgruppierung, sondern eine
kontrollierte Verschiebung entlang der Wellenachse.

### Claim ISO4
Der Isotopen-Test liefert einen sauberen Kontrollbeleg dafür, dass Wellen- und Strukturachse
nicht identisch sind.

### Claim ISO5
Wenn der Test gelingt, stärkt er die Arbeitshypothese, dass materialsensitive Kopplung nicht
nur an Masse, sondern auch an innere Struktur gebunden ist.

---

## 10. Kritische Gegenfrage

Der Block muss ausdrücklich auch die Gegenmöglichkeit offenhalten:

> Wenn isotopische Änderungen die kombinierte Strukturordnung vollständig dominieren oder
die angeblich strukturgetragenen Deskriptoren faktisch keinen invarianten Anteil zeigen,
dann wäre die bisherige Trennung von Wellen- und Strukturachse zu schwach oder irreführend.

Das ist wichtig für die Falsifizierbarkeit des Blocks.

---

## 11. Verhältnis zu den bisherigen Achsen

### Wellenachse
- isotopensensitiv erwartet

### Ionisierungsachse
- in erster Näherung weitgehend stabil erwartet
- kleine isotopische Effekte möglich, aber für den ersten Block nachrangig

### Valenzachse
- isotopeninvariant erwartet

### shell_closure
- isotopeninvariant erwartet

Gerade diese erwartete Asymmetrie macht den Block so wertvoll.

---

## 12. Nächster technischer Schritt

Nach dieser Notiz wären die logischen Anschlussblöcke:

- `debroglie_matter_signature_isotope_io_v1.md`
- `debroglie_matter_signature_isotope_tests_v1.md`

danach:
- ein kleiner Isotopen-Runner oder eine Isotopen-Erweiterung der bestehenden QC-Runner

---

## 13. Bottom line

Die operative Leitformel dieses Blocks lautet:

> Isotope liefern denselben strukturellen Elektronenrahmen bei veränderter Massenskala und
sind damit ein besonders sauberer Test für die Trennung von Wellen- und Strukturachse.

Oder knapper:

> Gleiche Konfiguration, andere Masse — besser lässt sich Welle gegen Struktur kaum testen.
