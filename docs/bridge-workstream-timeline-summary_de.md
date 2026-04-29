# Zeitlinie und Ergebnissynthese des Bridge-Workstreams

## Zweck dieses Dokuments

Diese Notiz fasst die bisherige innere Zeitlinie des jüngsten **Bridge-Workstreams** im Projekt **Quantum–Spacetime Bridge** zusammen.

Ziel ist es, den ganzen jüngsten Bogen als ein zusammenhängendes internes Bild festzuhalten:

- wo wir konzeptionell gestartet sind
- was wir Schritt für Schritt gebaut haben
- was nicht funktioniert hat
- was wir verbessert haben
- welche Tests gelaufen sind
- was die Tests derzeit stützen
- was noch offen bleibt

Das ist eine interne Synthesenotiz – also im Grunde das aktuelle „Gesamtkunstwerk“ des bridge-fokussierten Blocks.

---

## 0. Ausgangspunkt: die anfängliche konzeptionelle Position

Am Anfang dieses Workstreams wurde die Brücke bereits in einem **begrenzten, disziplinierten** Sinn verstanden.

Die zentrale interne Position war:

- die Brücke ist **noch keine** fertige Theorie der Raumzeitentstehung
- sie ist **noch keine** vollständige Herleitung der Gravitation
- sie ist **noch kein** abgeschlossenes Quantengravitationsmodell
- aber sie könnte bereits als **begrenzte Strukturschicht** auftauchen, die wellenbasierte relationale Organisation mit raumzeitrelevanter effektiver Struktur verbindet

Der stärkste interne Kandidat für diese Schicht war schon zu Beginn:

- **weighted relational structure**

An diesem Punkt lautete die wichtigste offene interne Frage:

> Ist die weighted-relational Schicht nur ein **Marker** tieferer brückenrelevanter Ordnung, oder ist sie bereits ein **Carrier** dieser Ordnung?

Diese Unterscheidung hat den gesamten jüngsten Block angestoßen.

---

## 1. Phase der begrifflichen Klärung

Bevor wir implementiert haben, wurde die Brückenlinie zunächst in mehreren internen Notizen geschärft.

### 1.1 Bridge core position
Wir haben den Kernanspruch intern festgezogen:

- die Brücke lokalisiert derzeit am plausibelsten in **weighted relational structure**
- **nicht** primär in Topologie
- **nicht** primär in abgeleiteter Distanzgeometrie

Das war eine wichtige Einengung.

### 1.2 Bridge nature and structure
Danach haben wir die Brücke charakterisiert als:

- relational
- gewichtet
- strukturiert
- intermediär
- wellenkompatibel

Damit wurde die Brücke nicht mehr als Schlagwort, sondern als geschichteter Strukturkandidat formuliert.

### 1.3 Marker vs. Carrier
Danach haben wir zwei Lesarten getrennt:

- **Marker** = beste sichtbare Auslesefläche
- **Carrier** = trägt bereits selbst einen Teil der brückenrelevanten Ordnung

Der resultierende innere Status lautete damals:

> starker Marker, offener Carrier-Kandidat

Das war die konzeptionelle Startrampe für die Experimentphase.

---

## 2. Phase der Teststrategie

Nachdem die Marker–Carrier-Frage explizit geworden war, musste sie in ein reales Testprogramm übersetzt werden.

### 2.1 Marker–Carrier-Teststrategie
Wir haben die Grundlogik festgelegt:

- die **weighted-relational layer** gezielt stören
- gröbere Schalen so gut wie möglich stabil halten
- das Antwortmuster vergleichen
- das Ergebnis als marker-leaning, carrier-leaning, undecided oder test-not-informative lesen

### 2.2 Erste BMC-01-Idee
Daraus entstand der erste konkrete Experimentblock:

- **BMC-01**
- **Weighted Relational Scramble Probe**

Die erste Interventionsfamilie war:

- Weight scrambling bei erhaltener Topologie

Die Idee war einfach, aber scharf:
Wenn die Umhängung von Gewichten etwas verändert, dann ist die **Platzierung** der Gewichte selbst strukturell relevant.

---

## 3. Erste BMC-01-Implementierung und erster Dry-Run

### 3.1 Erstes Implementierungsskelett
Ein erstes ausführbares BMC-01-Skript wurde gebaut:
- Baseline-CSV als Input
- einfache Permutationsvarianten für Gewichte
- transparente Outputs
- erste Readout-Schicht
- einfache Decision-Logik

### 3.2 Baseline-Template
Wir haben eine minimale synthetische Baseline-CSV definiert mit:

- `pair_id`
- `endpoint_a`
- `endpoint_b`
- `weight`
- `local_group`
- `shell_label`

Diese Baseline war bewusst klein und synthetisch, also ein Dry-Run-Starter und noch kein kanonischer wissenschaftlicher Datensatz.

### 3.3 Ergebnis des ersten Dry-Runs
Der erste Dry-Run war technisch erfolgreich:
- Outputs wurden korrekt geschrieben
- die Interventionstabelle zeigte, dass Gewichte tatsächlich auf andere Paare verschoben wurden

Wissenschaftlich zeigte sich aber sofort ein zentrales Problem:

- Baseline- und Perturbations-**Verteilungsreadouts** waren identisch
- die Decision-Logik driftete zu einer markerfreundlichen Lesart
- obwohl die Intervention die Gewichtsanordnung real verändert hatte

Damit war der eigentliche Engpass sichtbar:

> Die Intervention änderte bereits die relationale Anordnung, aber der Readout sah nur die globale Gewichtsverteilung.

Das war methodisch ein sehr wichtiger Durchbruch.

---

## 4. Phase des Readout-Upgrades

### 4.1 Hauptlektion
Wir haben verstanden, dass der erste BMC-01-Readout zwar **verteilungssensitiv**, aber nicht ausreichend **anordnungssensitiv** war.

Anders gesagt:
- er maß, welche Werte vorhanden waren
- aber nicht, **wo** diese Werte relational saßen

### 4.2 Readout-Upgrade-Note
Daraus entstand eine formale interne Notiz, die erklärte:
- warum der erste Dry-Run **kein** Marker-Beleg war
- warum die Intervention in Ordnung war
- warum der Readout der Flaschenhals war
- warum arrangement-sensitive Kennzahlen als Nächstes eingebaut werden mussten

### 4.3 Nachgeschärftes BMC-01-Skript
Danach wurde das BMC-01-Skript um arrangement-sensitive Readouts erweitert, darunter:

- endpoint load shift
- endpoint load dispersion shift
- local-group arrangement shift
- shell arrangement shift
- pair-to-neighborhood consistency shift
- kombinierter arrangement signal

Auch die Decision-Logik wurde härter gemacht, damit:
- intervention-positive, aber readout-blinde Läufe
nicht mehr fälschlich als Marker-Support gelesen werden

---

## 5. Zweiter BMC-01-Dry-Run: erste wirklich brauchbare Probe

Nach etwas unerquicklich viel Dateiversions-Chaos lief die nachgeschärfte BMC-01-Fassung endlich korrekt.

### 5.1 Neues Dry-Run-Ergebnis
Der zweite Dry-Run zeigte:

- globale Verteilungsmetriken blieben praktisch gleich
- aber arrangement-sensitive Metriken sprangen jetzt an

Vor allem:
- die Intervention war nun als **strukturelle Umordnung** sichtbar
- und die Decision landete bei **undecided** statt voreilig etwas zu behaupten

### 5.2 Bedeutung
Das war der erste echte Erfolg der BMC-Linie.

Ab diesem Punkt war BMC-01:
- nicht mehr nur ein Software-Skelett
- sondern eine echte strukturelle Probe für weighted relational organization

---

## 6. BMC-01-Variantenmatrix

Der nächste Schritt war eine Vergleichsmatrix über Interventionsmodi und Stärken:

### Varianten
- `global_weight_permutation`
- `within_shell_weight_permutation`
- `within_local_group_weight_permutation`

### Stärken
- `low`
- `medium`
- `high`

### 6.1 Hauptergebnis der Matrix
Die Matrix zeigte:

#### Globale Permutation
- stärkste Gesamtreaktion
- besonders bei medium und high

#### Within-local-group Permutation
- deutliche Reaktion schon bei low
- lokale Struktur war früh relevant

#### Within-shell Permutation
- vergleichsweise gepuffert bei low und medium
- deutlicher erst bei high

### 6.2 Interpretation
Das war der erste starke Hinweis darauf, dass:

- weighted relational structure **nicht flach** ist
- sie **interne Organisation** besitzt
- und insbesondere **shell-preserving perturbation** teilweise gepuffert ist

Daraus entstand der nächste wichtige Verdacht:

> Shell-Struktur könnte bereits einen Teil der brückenrelevanten Ordnung konservieren.

Das war eine zentrale konzeptionelle Wendung.

---

## 7. Entstehung der Shell-Hypothese

Nach der Matrix begann die Brückenarchitektur intern geschichtet statt flach auszusehen.

Das emergierende innere Bild wurde:

1. **Topologie** – zu grob
2. **Shell-Struktur** – stabilere intermediäre Schicht
3. **lokale gewichtete Anordnung** – sensitive Feinstrukturschicht
4. **volle weighted relational configuration** – stärkster Gesamt-Kandidat für die Brücke

Daraus entstand die explizite Shell-Hypothese:

- Shell-Struktur könnte eine **ordnungsgetragene intermediäre Schicht** sein
- noch nicht bewiesen als voller Carrier
- aber nicht mehr plausibel nur ein Label

Das war die Geburt der expliziten **Shell-Order-Hypothese**.

---

## 8. Logik von shell-preserving vs shell-crossing

Um die Shell-Hypothese sauber zu testen, haben wir einen schärferen Vergleich definiert:

- **shell-preserving perturbation**
- **shell-crossing perturbation**

### 8.1 Shell-preserving
Gewichte werden nur **innerhalb derselben Shell** umgehängt.

### 8.2 Shell-crossing
Gewichte werden **über Shell-Grenzen hinweg** umgehängt.

Die Leitfrage wurde:

> Beschädigt das Brechen der Shell-Mitgliedschaft die bridge-facing Ordnung stärker als das Erhalten der Shell-Mitgliedschaft bei gestörter Feinanordnung innerhalb der Shell?

Das ist viel schärfer als die ursprüngliche weighted-relational scrambling-Idee.

---

## 9. BMC-01-SX-Implementierung

Daraus entstand ein neuer, spezieller Implementierungsblock:

- **BMC-01-SX**
- **Shell-Preserving vs Shell-Crossing Weighted Permutation Probe**

### 9.1 Implementierte Varianten
- `within_shell_weight_permutation`
- `shell_crossing_weight_permutation`

### 9.2 Crossing-Policies
- `adjacent_shell_crossing`
- `full_shell_crossing`

### 9.3 Shell-spezifische Readouts
Hinzu kamen neue Kennzahlen wie:

- `shell_boundary_disruption_score`
- `shell_crossing_fraction`
- `shell_distance_mean`

zusätzlich zu den beibehaltenen arrangement-sensitive Metriken:
- endpoint load shift
- shell arrangement shift
- pair-to-neighborhood consistency
- arrangement signal

Das war das erste echte shell-fokussierte Brückenexperiment.

---

## 10. Erster gematchter Vergleich: shell-preserving vs adjacent shell-crossing

Danach wurde ein sauber gematchtes Paar bei mittlerer Stärke gefahren:

- gleiche Baseline
- gleicher Seed
- gleiche Topologie
- gleiche Gewichtsmultimenge
- gleiche Readout-Architektur

### 10.1 Shell-preserving medium
Wichtige Werte:
- arrangement signal: `0.148588`
- shell boundary disruption: `0`
- shell crossing fraction: `0`
- Decision: `undecided`

### 10.2 Adjacent shell-crossing medium
Wichtige Werte:
- arrangement signal: `0.319266`
- shell boundary disruption: `0.500000`
- shell crossing fraction: `0.500000`
- Decision: `shell_order_leaning`

### 10.3 Interpretation
Das war das erste starke direkte Ergebnis, das zeigte:

> Shell-crossing ist unter gematchten Bedingungen klar destruktiver als shell-preserving reassignment.

An diesem Punkt sah Shell nicht mehr nur verdächtig aus, sondern wie ein **gestützter Kandidat für intermediate order**.

---

## 11. BMC-01-SX-Ladder über low / medium / high

Danach wurde der Vergleich preserving vs adjacent über eine ganze Strength-Ladder gezogen.

### Within-shell
- low: `0.148588`
- medium: `0.148588`
- high: `0.410838`

### Adjacent shell-crossing
- low: `0.199224`
- medium: `0.319266`
- high: `0.644468`

### 11.1 Hauptergebnis der Ladder
Über alle Stufen hinweg galt:
- shell-crossing blieb destruktiver als shell-preserving

Damit war klar, dass der Shell-Effekt nicht bloß ein Medium-Artefakt war.

### 11.2 Interpretation
Das stärkte die interne Lesart weiter:

- Shell-Mitgliedschaft konserviert einen Teil der bridge-relevanten Ordnung
- und Shell-Bruch zerstört systematisch mehr dieser Ordnung

Das war eine deutliche Verstärkung der Shell-Order-Linie.

---

## 12. Full shell-crossing als nächster Härtegrad

Danach war die nächste natürliche Frage:

> Ist Shell nur lokal fragil, oder zerstört ein breiterer Shell-Bruch nochmals mehr?

Daher wurde die nächste Leiter konzeptionell definiert:

- `within_shell`
- `adjacent_shell_crossing`
- `full_shell_crossing`

Die erwartete Struktur war:

> `within_shell < adjacent_shell_crossing < full_shell_crossing`

Das wurde zur nächsten entscheidenden graded shell-order ladder hypothesis.

---

## 13. Drei-Modi-Vergleich bei medium: within-shell vs adjacent vs full

Diese Drei-Modi-Leiter wurde dann tatsächlich bei medium gefahren.

### 13.1 Within-shell medium
- arrangement signal: `0.148588`

### 13.2 Adjacent shell-crossing medium
- arrangement signal: `0.319266`

### 13.3 Full shell-crossing medium
- arrangement signal: `0.450544`

### 13.4 Unterstützende Metriken
Dasselbe gestufte Muster zeigte sich auch in den Begleitgrößen:

#### Endpoint load shift
- `0.100000`
- `0.230000`
- `0.395000`

#### Shell arrangement shift
- `0.500000`
- `0.666667`
- `1.000000`

#### Pair-to-neighborhood consistency
- `0.084167`
- `0.137500`
- `0.246667`

#### Shell distance mean
- `0.000000`
- `0.500000`
- `0.666667`

### 13.5 Interpretation
Das war der bislang stärkste interne Shell-Befund.

Die graded ladder hielt sauber:

> `within_shell < adjacent_shell_crossing < full_shell_crossing`

Das heißt:

> Je breiter Shell-Mitgliedschaft gebrochen wird, desto stärker bricht die bridge-facing Ordnung ein.

Das ist ein sehr aussagekräftiger interner Struktur-Befund.

---

## 14. Beste aktuelle interne Interpretation

An diesem Punkt lautet die stärkste disziplinierte interne Lesart:

### 14.1 Weighted arrangement matters
Das ist im Rahmen dieser scaffold-level Probes inzwischen gut gestützt.

### 14.2 Die weighted-relational layer ist intern strukturiert
Sie sollte nicht mehr als flache Wolke gesehen werden.

### 14.3 Shell-Struktur konserviert nichttriviale bridge-relevante Ordnung
Das ist jetzt nicht mehr nur durch Robustheitsandeutung, sondern durch:
- gematchte Vergleiche
- Strength-Ladder
- graded full-crossing behavior
gestützt.

### 14.4 Shell verhält sich wie ein intermediate order-bearing scaffold
Noch nicht als finaler Carrier bewiesen, aber klar mehr als nur ein Label.

### 14.5 Der Brückenkandidat wirkt zunehmend geschichtet
Die plausibelste aktuelle Architektur ist:

1. Topologie  
2. Shell-Ordnung  
3. lokale gewichtete Feinstruktur  
4. volle weighted relational configuration

Diese geschichtete Lesart ist einer der wichtigsten konzeptionellen Gewinne des gesamten Blocks.

---

## 15. Was wir **noch nicht** wissen

Trotz der starken jüngsten internen Fortschritte bleibt vieles offen.

### 15.1 Kein finaler Carrier-Beweis
Wir haben **noch keinen** Beweis, dass Shell oder die weighted-relational layer der finale Bridge-Carrier ist.

### 15.2 Kleine synthetische Baseline
Die aktuellen Läufe verwenden noch das Template und keinen real extrahierten Projektzustand.

### 15.3 Frühe Readout-Architektur
Die arrangement- und shell-sensitiven Kennzahlen sind nützlich, aber noch scaffold-level.

### 15.4 Begrenzte Replikation
Es fehlen noch:
- breite Seed-Sweeps
- Replikation auf realer Baseline
- erweiterte Batch-Statistik

### 15.5 Keine finale physikalische Interpretation
Shell ist jetzt eine starke interne Ordnungshypothese, aber noch kein ausformulierter physikalischer Shell-Satz.

Der korrekte interne Status lautet also:

> starker struktureller Support, aber noch kein Endbeweis

---

## 16. Die stärksten Takeaways des ganzen Workstreams

Wenn man den jüngsten Bridge-Block auf seine stärksten internen Aussagen reduziert, dann sind es diese:

### A. Die Brücke ist nicht am besten als flache weighted layer zu denken
Sie wirkt intern differenziert.

### B. Marker vs Carrier ist jetzt konkreter geworden
Der Brückenkandidat wirkt zunehmend scaffold-artig statt bloß diagnostisch.

### C. Shell matters
Das ist eine der klarsten derzeitigen Botschaften.

### D. Shell-breaking scales with disruption
Das ist der bislang stärkste Shell-spezifische Befund.

### E. Die Brückenarchitektur wirkt jetzt geschichtet
Das ist vielleicht die größte konzeptionelle Verschiebung des ganzen Blocks.

---

## 17. Beste aktuelle interne Arbeitsformeln

Die derzeit nützlichsten Kurzformeln sind:

### Brückenweit
> Die Brücke lokalisiert derzeit in weighted relational structure, aber diese Schicht wirkt jetzt intern geschichtet.

### Shell-spezifisch
> Shell-Mitgliedschaft scheint nichttriviale bridge-relevante Ordnung zu konservieren.

### Full-crossing-Befund
> Breiterer Shell-Bruch erzeugt progressiv stärkere bridge-facing Disruption.

### Architekturansicht
> Der Brückenkandidat sieht zunehmend aus wie ein intern geschichtetes Scaffold und nicht wie eine flache diagnostische Oberfläche.

---

## 18. Wahrscheinlich sinnvollste nächste Schritte

Die saubersten nächsten Schritte, nach Wert geordnet, wären derzeit:

### 1. Real extrahierte Baseline
Zentrale BMC-01- und BMC-01-SX-Vergleiche auf einer echten Projekt-Baseline wiederholen.

### 2. Seed-Replikation
Die Shell-Ladder über mehrere Seeds prüfen.

### 3. Full ladder extension
Die volle Drei-Modi-Leiter nicht nur bei medium, sondern auch bei low und high fahren.

### 4. Shell-spezifische Readout-Verbesserung
Verfeinern von:
- shell coherence retention
- shell-to-shell support redistribution
- refined shell boundary disruption
- shell-local concentration shift

### 5. Dokumentation und Commit-Hygiene
Der Block verdient jetzt einen sauberen Commit und einen klaren Status-Snapshot.

---

## 19. Bottom line

Das „Gesamtkunstwerk“ dieses jüngsten Bridge-Blocks ist:

Wir sind gestartet mit einem breiten, aber disziplinierten Verdacht, dass die Brücke irgendwo in der **weighted relational structure** sitzt.

Dann haben wir:
- die Brücke begrifflich geschärft
- Marker von Carrier getrennt
- BMC-01 entworfen
- entdeckt, dass die ersten Readouts blind waren
- die Readout-Architektur nachgeschärft
- gezeigt, dass arrangement-sensitive Perturbationen zählen
- gesehen, dass shell-preserving perturbation vergleichsweise gepuffert ist
- daraus eine explizite Shell-Order-Hypothese gemacht
- BMC-01-SX implementiert
- gezeigt, dass shell-crossing destruktiver ist als shell-preserving
- das über eine Strength-Ladder gestützt
- und schließlich eine graded three-mode shell-breaking ladder gezeigt:

> `within_shell < adjacent_shell_crossing < full_shell_crossing`

Das ist die derzeit stärkste interne experimentelle Geschichte.

Das Projekt hat **noch keinen** finalen Brückenmechanismus. Aber es hat jetzt etwas viel Wertvolleres als bloße Intuition:

> eine strukturierte, testbare, intern geschichtete Brückenarchitektur, in der Shell-Ordnung als ernstzunehmender Kandidat für eine intermediate order-bearing layer emergiert.
