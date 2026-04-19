# debroglie_matter_signature_vdw_series_note_ac_v1

## 1. Ziel

Diese Kurznotiz fasst die erste VDW-Serie A–C des Materialsignatur-Blocks zusammen.

Die Serie diente dazu, die aus der ersten A–D-Reihe motivierte Frage zu prüfen, ob eine
nicht-universelle Stoffskala dem bisherigen de-Broglie-Signaturraum tatsächlich eine zweite
materiesensitive Achse eröffnet.

Leitfrage:

> Bleibt die Signatur im Wesentlichen ein de-Broglie-Längenskalenmodell, oder reorganisiert
eine van-der-Waals-Stoffschicht die Ordnung substanziell?

---

## 2. Ausgangslage vor der VDW-Serie

Die vorangehende Serie A–D hatte ergeben:

- die Signaturidee ist operational tragfähig und robust
- unter idealgasartigen Standardannahmen bleibt die Differenzierung jedoch im Wesentlichen
  auf die de-Broglie-Längenskala reduziert
- `energy_score`, `occupancy_score` und die explizit aktivierte Frequenzachse kollabieren
  unter den gewählten Bedingungen auf thermisch universelle Beiträge
- daraus ergab sich die Notwendigkeit, eine nicht-universelle Stoffskala zu testen

Die VDW-Serie A–C ist genau dieser Test.

---

## 3. Serienaufbau

### Run A
- Referenzlauf
- `gas_model = ideal_gas`
- nur Wellen-Schicht aktiv

### Run B
- voller VDW-Lauf
- `gas_model = van_der_waals`
- Wellen-Schicht plus aktive Stoff-Schicht
- kombinierte Signatur mit voller Stoffgewichtung

### Run C
- VDW-Lauf mit reduzierter Stoffgewichtung
- Test auf Robustheit der Reorganisation gegenüber schwächerem Stoffbeitrag

---

## 4. Befund von Run A

Run A reproduziert sauber den bisherigen Null- bzw. Referenzfall:

- `combined_signature_ordering = wave_signature_ordering`
- keine aktive Stoffschicht
- die Signaturordnung bleibt vollständig auf die Wellen-Skala zurückgeführt

Damit ist Run A der korrekte Referenzanker für die VDW-Serie.

---

## 5. Befund von Run B

Run B liefert den ersten klaren starken Hinweis auf eine zweite materielle Achse.

### 5.1 VDW-Stoffschicht differenziert wirklich
Die neuen Stoffgrößen sind nicht flach:

- `interaction_score`
- `excluded_volume_score`
- `vdw_signature_score`

Sie zeigen deutliche, speziessensitive Unterschiede.

### 5.2 Die kombinierte Ordnung kippt substanziell
Im Vergleich zur reinen Wellenordnung wird die kombinierte Signatur neu organisiert:

- Wasserstoff verliert seine Dominanz
- Natrium wird neuer Spitzenkandidat
- Schwefel und Phosphor rücken stark nach vorn

Damit ist die kombinierte Ordnung nicht bloß ein umetikettierter Ausdruck der bisherigen
Längenskalenordnung.

### 5.3 Materiesensitive Reorganisation
Die VDW-erweiterte Delta-Struktur relativ zur Massenordnung wird deutlich gemäßigter und
reorganisiert gegenüber der reinen Wellen-Schicht. Das ist nicht als Schwächung zu lesen,
sondern als Hinweis auf eine breitere, weniger eindimensionale Signaturstruktur.

---

## 6. Befund von Run C

Run C prüft, ob der Effekt nur ein Artefakt maximaler Stoffgewichtung ist.

Das Ergebnis ist klar:

- die Reorganisation bleibt bestehen
- die Ordnung fällt nicht auf den Run-A-Referenzfall zurück
- Natrium bleibt Spitzenkandidat
- Schwefel und Phosphor bleiben stark
- Wasserstoff bleibt deutlich zurückgenommen

Damit zeigt Run C:

> Die Stoff-Skala wirkt nicht nur im Vollgewichtungsfall, sondern bleibt auch bei
reduzierter Gewichtung signaturprägend.

Das ist ein wichtiger Robustheitshinweis.

---

## 7. Vergleich A vs. B vs. C

### A
- reine Wellenordnung
- de-Broglie-Längenskala dominiert

### B
- starke Stoff-Reorganisation
- neue kombinierte Ordnung

### C
- Reorganisation bleibt auch bei reduzierter Stoffgewichtung erhalten

Serienlesart:

> Die Stoff-Skala spricht nicht nur, sie bleibt auch hörbar, wenn man ihre Lautstärke reduziert.

---

## 8. Physikalische Lesart

Die VDW-Serie A–C zeigt erstmals robust, dass die Signaturarchitektur nicht auf eine reine
de-Broglie-Längenskalen-Sensitivität beschränkt bleiben muss.

Stattdessen ergibt sich nun eine erste zweischichtige Lesart:

### 8.1 Wellen-Schicht
trägt:
- de-Broglie-Längenskala
- die bisherige signaturprägende Basisebene

### 8.2 Stoff-Schicht
trägt:
- nicht-universelle Wechselwirkungsstruktur
- effektive materielle Präsenz
- Ausschluss- bzw. Volumencharakteristik
- zusätzliche speziessensitive Ordnung

### 8.3 Kombinierte Signatur
ist nicht bloß die Summe alter Resultate, sondern eine reell reorganisierte materiesensitive
Gesamtstruktur.

---

## 9. Claims der Serie

### Belastbar unterstützt
- eine VDW-Stoffschicht erzeugt zusätzliche Differenzierungsstruktur
- die kombinierte Ordnung ist nicht identisch mit der reinen Wellenordnung
- die Reorganisation bleibt auch bei reduzierter Stoffgewichtung bestehen

### Teilweise unterstützt
- die neue Ordnung ist informationsreicher als die reine Wellenordnung
- die Serie zeigt jedoch noch kein abschließendes Stoffmodell, sondern einen ersten
  produktiven Erweiterungshebel

### Noch offen
- wie physikalisch belastbar die verwendeten `a`/`b`-Parameter im Detail sind
- ob alternative Stoffmodelle die gleiche Richtung bestätigen
- wie stark `tau` künftig von der erweiterten Signatur profitieren kann

---

## 10. Kernaussage der Serie

Die erste VDW-Serie A–C zeigt robust:

> Eine nicht-universelle Stoffskala kann die bisherige reine Wellenordnung substanziell
reorganisieren.

Damit erweitert sich der Signaturraum von einem im Wesentlichen eindimensionalen
de-Broglie-Längenskalenmodell zu einer zweischichtigen Wellen-/Stoff-Signaturarchitektur.

---

## 11. Bottom line

Die zentrale Arbeitsformel dieser Serie lautet:

> Die VDW-Serie A–C zeigt erstmals robust, dass eine nicht-universelle Stoffskala dem
bisherigen de-Broglie-Signaturraum eine zweite materielle Achse eröffnet, die die reine
Wellenordnung nicht nur ergänzt, sondern substanziell reorganisiert.

Oder knapper:

> Die Stoff-Skala spricht — und sie bleibt auch bei reduzierter Gewichtung hörbar.
