# debroglie_matter_signature_qc_valence_extension_v1

## 1. Ziel

Dieses Dokument definiert die nächste Erweiterung der quantenchemischen Stoffschicht um
Valenzschalen- und Konfigurationsinformation.

Die Ionisierungsenergie wurde im vorangehenden QC-Lauf als erste atomnahe
**Stärkeachse** getestet. Die vorliegende Erweiterung führt nun eine dazu komplementäre
**Form- bzw. Strukturachse** ein.

Leitfrage:

> Kann die äußere elektronische Struktur atomarer Spezies — insbesondere Valenzschale,
Orbitalblock und Schalenabschluss — eine zusätzliche, physikalisch lesbare
materialsensitive Signaturachse liefern?

---

## 2. Motivation

Der erste QC-Lauf mit `ionization_score` hat gezeigt:

- die atomnahe quantenchemische Stoffschicht reorganisiert die bisherige Wellenordnung
- diese Reorganisation ist deutlich, aber feiner als im VDW-Fall
- Wasserstoff bleibt stark
- Stickstoff gewinnt gegenüber Kohlenstoff
- Natrium verliert deutlich

Das deutet darauf hin, dass Ionisierungsenergie eher eine **atomare Stabilitäts- bzw.
Bindungsstärkeachse** trägt als eine grobe stoffliche Bulk-Skala.

Damit fehlt nun eine komplementäre Achse, die nicht primär „wie stark gebunden“,
sondern eher „wie strukturiert organisiert“ fragt.

Genau dafür wird die Valenzschalen-Erweiterung eingeführt.

---

## 3. Physikalische Lesart

Die Valenzschale ist inhaltlich besonders geeignet, weil sie mehrere strukturrelevante
Eigenschaften trägt:

- Anzahl der Valenzelektronen
- Lage der Außenschale (Hauptquantenzahl)
- Typ der dominanten Valenzorbitale (`s`, `p`, `d`, `f`)
- offene vs. geschlossene Schale
- daraus abgeleitete Stabilitäts- und Resonanzcharakteristik

Diese Größen sind atomnah, quantenmechanisch motiviert und direkt mit der äußeren
elektronischen Organisation einer Spezies verknüpft.

Saubere Arbeitslesart:

> Ionisierungsenergie misst eher eine atomare Stärkeachse.  
> Die Valenzschale liefert dagegen eine atomare Struktur- bzw. Formachse.

---

## 4. Warum nicht die rohe Elektronenkonfiguration?

Die Elektronenkonfiguration ist physikalisch reichhaltig, aber als Rohtext oder
vollständige Orbitalfolge nicht unmittelbar runnerfreundlich.

Beispiel:

- `1s² 2s² 2p²`
- `1s² 2s² 2p⁶ 3s¹`

Solche Strukturen sollten nicht direkt als Signaturwert verwendet werden.

Stattdessen wird vorgeschlagen, aus der Konfiguration einfache, robuste
**abgeleitete Deskriptoren** zu bauen.

---

## 5. Erste Kandidaten für Valenz-Deskriptoren

### 5.1 `valence_electron_count`
Anzahl der Elektronen in der äußeren Schale bzw. im aktiven Valenzbereich.

Lesart:
- grobe äußere Elektronenbesetzung
- chemische Zugänglichkeit
- erstes Strukturmaß

### 5.2 `shell_level_score`
Hauptquantenzahl `n` der Valenzschale.

Lesart:
- räumliche Lage der Außenschale
- Schalenebene der äußeren Elektronen
- erste Größen-/Lagenachse der elektronischen Struktur

### 5.3 `orbital_block_score`
Blockzugehörigkeit der Valenzstruktur:
- `s`
- `p`
- `d`
- `f`

Lesart:
- qualitativer Orbitalcharakter
- möglicher Resonanz- und Bindungsmodus
- nicht primär als lineare Zahl, sondern als strukturierter Deskriptor

### 5.4 `shell_closure_score`
Einfacher Indikator für:
- offene Schale
- abgeschlossene / Edelgaskonfiguration-nahe Schale

Lesart:
- strukturelle Stabilität
- relative Trägheit vs. Offenheit
- Resonanzzugänglichkeit der Außenelektronen

### 5.5 `valence_structure_score`
Zusammengesetzter Struktur-Score aus:
- `valence_electron_count`
- `shell_level_score`
- `orbital_block_score`
- `shell_closure_score`

Lesart:
- grober Gesamtdeskriptor der äußeren elektronischen Organisation

---

## 6. Methodische Reihenfolge

Diese Erweiterung soll bewusst klein anfangen.

### Schritt 1
Zunächst nur einfach ableitbare Deskriptoren verwenden:

- `valence_electron_count`
- `shell_level_score`
- `shell_closure_score`

### Schritt 2
Danach `orbital_block_score` in vorsichtiger Form ergänzen

### Schritt 3
Erst anschließend einen kombinierten `valence_structure_score` prüfen

Diese Reihenfolge verhindert, dass zu früh zu viele diskrete Strukturentscheidungen
in einen einzigen Score gepresst werden.

---

## 7. Verhältnis zur Ionisierungsenergie

Die Valenzschalen-Erweiterung soll **nicht** die Ionisierungsenergie ersetzen, sondern
ergänzen.

### Ionisierungsenergie
trägt eher:
- Bindungsstärke des äußersten Elektrons
- Stabilität gegen Ablösung
- atomnahe Stärkeachse

### Valenzschale
trägt eher:
- Organisationsform der Außenelektronen
- Struktur- und Resonanzcharakter
- atomnahe Formachse

Damit entsteht innerhalb der quantenchemischen Stoffschicht erstmals eine saubere
interne Zweiteilung:

- **Stärkeachse**
- **Formachse**

---

## 8. Verhältnis zu VDW

Auch zur VDW-Schicht besteht eine wichtige Abgrenzung.

### VDW-Schicht
trägt eher:
- nichtideale Bulk- und Wechselwirkungscharakteristik
- effektive stoffliche Präsenz im realgasartigen Sinn

### QC-Schicht
trägt eher:
- atomnahe elektronische Struktur
- innere Organisation
- äußere Bindungs- und Resonanzcharakteristik

Damit sind VDW und QC nicht konkurrierende Dubletten, sondern unterschiedliche
Materialebenen:

- **stoffliche Nichtidealität**
- **atomare Elektronenstruktur**

---

## 9. Erwartete Funktion der Erweiterung

Die Valenzschalen-Erweiterung wäre gelungen, wenn mindestens eines der folgenden
Muster sichtbar wird:

- Spezies mit ähnlicher Ionisierungsenergie, aber unterschiedlicher Außenschalenstruktur
  werden besser getrennt
- die kombinierte QC-Ordnung wird strukturreicher als eine reine
  Ionisierungsenergie-Achse
- geschlossene vs. offene Schalen zeigen lesbare Differenzen
- die QC-Schicht wird interpretierbarer, nicht nur numerisch differenzierter

Wichtig:
Nicht mehr Differenzierung allein ist das Ziel, sondern eine **physikalisch besser lesbare**
Differenzierung.

---

## 10. Erste Testidee

Ein erster Minimaltest könnte mit den vorhandenen oder leicht ergänzbaren Spezies arbeiten:

- H
- C
- N
- O
- Na
- Cl
- ggf. He und Ne als Schalenabschluss-Referenzen

Das wäre besonders interessant, weil dann bereits erste Kontraste sichtbar würden:

- offene vs. geschlossene Schalen
- `s`- vs. `p`-Block
- unterschiedliche Valenzelektronenzahlen
- ähnliche vs. unterschiedliche Ionisierungsenergien

---

## 11. Offene methodische Fragen

Diese Erweiterung wirft ausdrücklich neue Fragen auf:

- Wie wird `orbital_block_score` am besten kodiert?
- Ist `shell_closure_score` binär oder abgestuft zu definieren?
- Wie viel Diskretheit verträgt die Signaturarchitektur, ohne künstlich zu werden?
- Wie stark korreliert die Valenzstruktur mit Ionisierungsenergie?
- Erzeugt die Formachse echte Zusatzdimension oder nur eine Umparametrisierung der
  Stärkeachse?

Diese Fragen markieren bereits den nächsten Kontrollraum.

---

## 12. Nächster Schritt

Die logische nächste Ausbaustufe nach dieser Notiz wäre:

- `debroglie_matter_signature_qc_valence_io_v1.md`
- `debroglie_matter_signature_qc_valence_tests_v1.md`
- danach eine kleine Runner-Erweiterung oder ein separater QC-Valenz-Runner

Wichtig:
Zuerst die Deskriptorschicht sauber festlegen, dann erst rechnen.

---

## 13. Bottom line

Die zentrale Arbeitslesart dieser Erweiterung lautet:

> Wenn Ionisierungsenergie die atomnahe Stärkeachse der QC-Schicht ist, dann liefert die
Valenzschale die dazu komplementäre atomnahe Form- bzw. Strukturachse.

Oder knapper:

> Ionisierungsenergie ist die Stärkeachse — die Valenzschale die Formachse.
