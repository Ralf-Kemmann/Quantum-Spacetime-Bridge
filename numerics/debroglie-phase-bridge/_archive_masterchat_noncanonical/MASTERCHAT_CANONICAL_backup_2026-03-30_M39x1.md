# Masterchat — Gravitation und RaumZeit
## Arbeitsstand / Referenzdokument
### Version: MC_M39a_RedTeam_2026-03-30

---

## 0. Zweck dieses Dokuments

Dieses Dokument ist der aktuelle **Masterchat** des Projekts.  
Es dient als zentrale, fortschreibbare Referenz für:

- Projektlogik
- Begriffe und Arbeitsdefinitionen
- numerische und mechanische Kernbefunde
- offene Flanken
- nächste Arbeitsblöcke
- defensive Außenformulierungen
- feste Organisationsstruktur und Workflow

Grundsatz:

> Nicht nur Ergebnisse festhalten, sondern auch Motivation, Übergänge und die Konsequenz für den nächsten Schritt.

---

## 1. Projektcharakter

Das Projekt verfolgt einen **wellen-/korrelationsbasierten Zugang** zur Emergenz von Struktur, Dynamik und branch-relevanter Ordnung ohne vorschnelle metaphysische Überdehnung.

Arbeitsstil:

- wissenschaftlich defensiv
- testgetrieben
- reproduzierbar
- klare Trennung zwischen Befund, Deutung und Hoffnung
- Informatik als Werkzeug, Physik als leitende Instanz

Leitmotiv:

> Wir geben unserem Marker einen tragfähigen physikalischen Unterbau.

---

## 2. Zentrale Arbeitsprinzipien

1. **Kein Orakelbetrieb**  
   Numerische Marker sind keine Theorie.

2. **Definition vor Interpretation**  
   Begriffe wie Branch, Asymmetrie, Energieasymmetrie, Familie und Spektrum müssen explizit definiert werden.

3. **Mechanismus vor Story**  
   Ein robuster Marker ist erst dann wissenschaftlich ernst zu nehmen, wenn er physikalisch lesbar und gegen Gegenhypothesen getestet ist.

4. **Kill-Sweeps statt Bestätigungssehnsucht**  
   Das Projekt greift die eigene Hypothese absichtlich an.

5. **Externe Gegenprüfung ist Pflicht**  
   Team-Red, Deep Research und Literaturfamilien dienen als reale Belastungsproben.

---

## 3. Aktueller Kernmarker

Der derzeit stärkste interne Marker ist:

- `delta_p2`

Arbeitsdefinition:

- paarweise quadratische Impulsdifferenz
- in einfachster Form:
  `delta_p2 = p_i^2 - p_j^2`

Bisheriger Status:

- robust in mehreren internen Auditblöcken
- klassenstärker als fixe Paaridentität
- mechanisch relevanter Kandidat
- aber noch nicht automatisch schon Mechanismus

---

## 4. Aktuelle project-interne Lesart von `delta_p2`

Frühere interne Lesart:

- `delta_p2` als quadratische spektrale Asymmetrie
- branchrelevanter Klassenmarker

Verschärfte aktuelle Lesart:

- `delta_p2` ist im freien quadratischen Dispersionsbild direkt proportional zur kinetischen Energiedifferenz zwischen Zustandspaaren

Formal:

`delta_p2 = p_i^2 - p_j^2 = 2m (epsilon_i - epsilon_j)`

Daraus folgt die bevorzugte Formulierung:

> `delta_p2` ist im freien quadratischen Dispersionsbild ein Kandidat für eine **relationale kinetische Energiedifferenz** zwischen Kanälen/Zustandspaaren.

Wichtige Bremse:

- das ist **nicht** automatisch eine Richtungsasymmetrie
- im quadratischen Fall gilt `E(p) = E(-p)`
- `delta_p2` ist vorzeichensensitiv als Differenz, aber nicht direktional

---

## 5. Defensive Außenformulierung

Für halb-externe oder externe Formulierung gilt derzeit bevorzugt:

> Im freien quadratischen Dispersionsbild ist `delta_p2` direkt proportional zur kinetischen Energiedifferenz zwischen Zustandspaaren. Der Marker kann daher als Kandidat einer branchrelevanten relationalen kinetischen Energiedifferenz gelesen werden. Für deformierte Dispersionen, insbesondere bei `alpha != 1`, bleibt diese physikalische Lesart ausdrücklich prüfbedürftig.

---

## 6. Wichtigste theoretische Bremse

Für `alpha != 1` gilt:

- `delta_p2` bleibt als quadratische Impulsdifferenz wohldefiniert
- verliert aber die direkte Energiebedeutung des freien quadratischen Falls

Defensive Form:

> Unter deformierter Dispersion (`alpha != 1`) ist `delta_p2` zunächst eine dispersionsneutrale quadratische Impulsdifferenz; die direkte Interpretation als kinetische Energiedifferenz gilt dann nicht mehr naiv unverändert.

Das ist zugleich eine offene Flanke und ein Spezifitätstest.

---

## 7. Stand vor M.3.9a

Vor M.3.9a war die Lage grob:

- `delta_p2` überlebt mehrere interne Audits
- bleibt unter Diversity-Kontrolle stark
- bleibt sigma-robust
- zeigt Strukturstabilität in ersten Dispersionsblöcken
- aber die Familienfrage war noch offen:
  - steckt dahinter ein Mechanismus?
  - oder nur ein Spezialeffekt der ursprünglichen P0–P3-Familien?

---

## 8. M.3.9a.1 — Familien-Precheck

### 8.1 Ziel

Prüfen, ob sich die beobachteten Asymmetrietypen auf **neu konstruierten Familien** reproduzierbar wiederfinden.

### 8.2 Getestete Familien

- **F1** — symmetrische Kontrolle
- **F2** — kompakt-negativer Kandidat
- **F3** — groß-negativer Kandidat
- **F4** — nichtaffin verzerrter groß-negativer Kandidat
- **F5** — asymmetrie-abgeschwächte Gegenprobe

### 8.3 Finales Ergebnis

Nach Nachschärfung von F2 und Typheuristik ergab sich:

- **F1** → `control_symmetric`
- **F2** → `compact_negative_candidate`
- **F3** → `large_negative_candidate`
- **F4** → `large_negative_candidate`
- **F5** → schwache Gegenprobe / kein main-screen pass

### 8.4 Inhaltliche Bedeutung

Damit konnte erstmals gezeigt werden, dass die erwarteten Asymmetrietypen auf neu konstruierten Familien **reproduzierbar separierbar** sind.

Das stärkt die Hypothese:

> Die branchrelevante Struktur ist nicht bloß ein Spezialeffekt der ursprünglichen P0–P3-Familien.

### 8.5 Wichtigster Einwand

Der Precheck zeigt zunächst **Typ-Reproduzierbarkeit**, noch nicht automatisch **Mechanismus-Reproduzierbarkeit**.

---

## 9. Team-Red / Claude — erste Präzisierungen vor M.3.9a.2

Wichtige Vorpräzisierungen:

- besser als „Energieasymmetrie“ allein:  
  **relationale kinetische Energiedifferenz**
- sauber unterscheiden zwischen:
  - Typ-Reproduzierbarkeit
  - Mechanismus-Reproduzierbarkeit
- matched-pair strategy zwischen F2 und F3/F4
- F5 als echter Falsifikationskandidat
- spätere Notwendigkeit familienfremder / literaturbasierter Referenzfamilien

---

## 10. Deep-Research-Ergebnis I — Theorie-Baukasten

Ein erster Deep-Research-Bericht lieferte die Theorieblöcke, die nötig sind, damit aus dem Marker Physik wird.

### 10.1 Minimaler dynamischer Kern
Quadratische Dispersion führt direkt zu relativer Phasenentwicklung:
`Delta phi_ij(t) = t / (2m hbar) * delta_p2`

Damit ist `delta_p2` nicht nur Energiedifferenz, sondern direkter Interferenz-/Korrelations-Taktgeber.

### 10.2 Operator- und Spektralformulierung
Familien sollen nicht als hübsche Punktmengen bleiben, sondern als Diskretisierung eines Spektralobjekts erscheinen:

- Hamiltonian / Generator
- Spektralmaß
- Green-Funktionen / spektrale Dichte
- Gewichte statt nur nackter Sets

### 10.3 Größere Theoriepfade
Spätere Anschlussmöglichkeiten:

- η-Invariante / Spektralfluss
- Scattering / Spektralverschiebung / Wigner-Zeitverzug
- Floquet / getriebene Systeme

### 10.4 Kernbotschaft
Ohne minimalen Dispersions-/Phasenmechanismus und Operator-/Spektralsprache bleibt `delta_p2` eine starke Heuristik. Mit ihnen kann es theoriegetragen werden.

---

## 11. Deep-Research-Ergebnis II — Externe Referenzfamilien

Ein zweiter Deep-Research-Bericht lieferte externe, physikalisch etablierte Kandidatenfamilien aus der Literatur bzw. Standardphysik.

Genannte Familien:

- Lamb-Wellen in Platten
- EM-Hohlleiter-/Hohlraummoden
- Phonon-Zweige harmonischer Kristalle
- Spinwellen / Magnonen
- Schwere-/Kapillarwellen
- paraxiale optische Moden

### 11.1 Bedeutung
Damit existiert ein Weg, die Familienfrage **aus dem intern konstruierten Raum heraus** zu lösen.

### 11.2 Neuer methodischer Gewinn
- externer Bias-Check
- literaturgestützte Referenzfamilien
- domänenübergreifende Testarchitektur
- Familien nicht nur intern gebaut, sondern extern ableitbar

---

## 12. Feste Organisationsstruktur des Projekts

Die Projektarbeit folgt einer festen Rollen- und Toolstruktur.

### 12.1 Nova / Forschungsraum
Im eigentlichen Forschungsraum bleiben:

- Physik
- Mechanismusfragen
- Begriffsarbeit
- Pflichtenhefte
- Masterchat
- Befund vs. Deutung
- Synthese und Priorisierung

Leitgedanke:

> Physik führt, Werkzeuge dienen.

### 12.2 Codex / Werkbank
Codex ist der bevorzugte Raum für eigentliche Repo-Arbeit und Implementierung:

- Runner
- YAML-Konfigurationen
- Bootstrap-Skripte
- Refactoring
- Tests
- Logging
- CSV/JSON/Markdown-Outputs
- parallele Code-Threads, wenn sinnvoll

### 12.3 Deep Research / Recherche- und Aufklärungsraum
Deep Research wird fest genutzt für:

- Literaturrecherche
- bekannte Verfahren und Standardmodelle
- externe Referenzfamilien
- Vergleich mit Standardphysik
- Gegenargumente
- methodische Einordnung
- Vorstrukturierung externer Testfelder

### 12.4 Claude / Team-Red / Gegnerraum
Claude wird als kritischer Gegenprüfer genutzt für:

- skeptische Reviews
- methodische Einwände
- Formulierungsstress
- Nachschärfung von Falsifikationslogik
- Prüfungen auf Overclaiming und Konstruktionsbias

### 12.5 Praktische Arbeitskette
Die bevorzugte Kette lautet:

1. Forschungsfrage und Pflichtenheft mit Nova klären
2. Literatur, Standardverfahren oder Referenzräume per Deep Research erschließen
3. Implementierung in Codex / VS Code bauen lassen
4. Outputs im Forschungsraum physikalisch auswerten
5. Ergebnisse durch Team-Red angreifen lassen

### 12.6 Arbeitsumgebung
Praktisch wird die Arbeitsumgebung als Kombination verstanden aus:

- ChatGPT-Projekt / Masterchat als Leitstand
- Canvas als Schreib- und Dokumentationsraum
- Codex App / IDE / CLI als Werkbank
- Deep Research als Recherchemodul
- Claude als Gegenprüfungsraum
- TeXstudio als LaTeX-/Manuskriptumgebung

### 12.7 IDE-Hinweis
Für Codex-Arbeit ist **VS Code mit Codex IDE Extension** die Standard-IDE.

---

## 13. Konkreter Workflow pro Arbeitsblock

Jeder neue Arbeitsblock folgt einem festen Ablauf.

### 13.1 Schritt 1 — Forschungsfrage und Ziel klären
- Ziel des Blocks
- Nicht-Ziel
- zentrale Hypothese oder Prüffrage
- Gegenhypothesen
- erwartete Outputs
- Erfolgskriterien
- Gegenkriterien / Kill-Kriterien

Ergebnis:
- Pflichtenheft oder Runner-Spezifikation

### 13.2 Schritt 2 — Recherche und Kontextaufbau
Deep Research übernimmt bei Bedarf:

- Literaturrecherche
- Standardverfahren
- Referenzfamilien
- methodische Vergleichspunkte
- Gegenargumente
- externe Testkandidaten

### 13.3 Schritt 3 — Implementierung auf der Werkbank
Codex / VS Code:

- Runner
- YAML
- Bootstrap
- Pfade
- Logging
- Tests

### 13.4 Schritt 4 — Ausführung und Rohbefunde
Gesammelt werden:

- Logs
- CSV/JSON/Markdown-Outputs
- Reports
- Fehlermeldungen

### 13.5 Schritt 5 — Physikalische Auswertung im Forschungsraum
Trennung zwischen:

- technischem Gelingen
- numerischem Befund
- physikalischer Lesart
- offener Flanke
- Konsequenz für den nächsten Schritt

### 13.6 Schritt 6 — Kritische Gegenprüfung
Claude / Team-Red übernimmt:

- skeptische Prüfung der Interpretation
- Aufspüren von Overclaiming
- Einwände gegen Konstruktionsbias
- Nachschärfung von Falsifikationslogik

### 13.7 Schritt 7 — Rückintegration in den Masterchat
Nach Abschluss eines Blocks werden Ziel, Kernbefund, Grenzen, Präzisierungen, offene Flanken und nächster Schritt in den Masterchat übernommen.

---

## 14. M.3.9a.2 — Vollaudit der neuen Familien (finaler Stand)

Mit M.3.9a.2 wurde erstmals ein voller Auditblock auf dem neuen Familien-Set durchgeführt. Ziel war nicht mehr nur die strukturelle Typtrennung, sondern die erste Prüfung, ob die in M.3.9a.1 separierten Familien auch **mechanisch** tragen.

### 14.1 Ziel des Blocks

M.3.9a.2 sollte prüfen,

- ob `delta_p2` im neuen Familienraum erneut als tragende Klassenebene erscheint,
- ob der Cross-type-Vergleich zwischen kompakt-negativen und groß-negativen Familien bei vergleichbarem `delta_p2` dieselben oder verschiedene Branch-Identitäten liefert,
- und ob F5 als expliziter Falsifikationskandidat erwartungsgemäß schwach bleibt.

### 14.2 Technischer Status

Der Block lief technisch sauber durch und erzeugte:

- globale Audit-Zusammenfassung
- Familien- und Branch-Summaries
- matched-pair-Tabellen
- F5-Falsifikationssummary
- Alpha-Interpretationsnotiz
- Markdown-Gesamtbericht

Damit ist M.3.9a.2 als **formal lauffähiger Auditblock** etabliert.

### 14.3 Nachschärfung der Dominanz- und Passlogik

Der erste Scaffold-Lauf zeigte zwar bereits starke matched-pair- und F5-Befunde, fiel global aber noch formal negativ aus, weil die vereinfachte Dominanzlogik `pair` systematisch bevorzugte.

Daraufhin wurde die family-wise Logik nachgeschärft:

1. `delta_p2_strength` wurde näher an echte Branch-/Mechaniksignale gekoppelt:
   - `mean_identity_strength`
   - `mean_branch_match_frac`

2. `family_pass_flag` wurde verschärft:
   - Kontrollfamilien dürfen nur bestehen, wenn sie kontrollartig bleiben
   - Falsifikationskandidaten zählen nicht als normale Erfolgsfamilien
   - Kandidatenfamilien benötigen Mindeststärke in Branch- und Identity-Maßen

### 14.4 Finales globales Ergebnis

Nach Nachschärfung ergab die globale Summary:

- `n_families_total = 5`
- `n_families_passed = 4`
- `family_pass_fraction = 0.8`
- `delta_p2_dominant_count = 5`
- `global_pass_flag = 1`

Damit gilt im finalen Stand:

> `delta_p2` erscheint im neuen Familienraum global als dominante Ebene, und der Auditblock ist formal positiv.

### 14.5 Family-wise Ergebnis

Finale Branch-Summary:

- **F1** (`control`)  
  `mean_branch_match_frac = 0.542857...`  
  `mean_identity_strength = 0.385714...`  
  `delta_p2_strength = 0.464286...`  
  `dominant_level = delta_p2`  
  `family_pass_flag = 1`

- **F2** (`compact_negative`)  
  `mean_branch_match_frac = 0.518452...`  
  `mean_identity_strength = 0.336905...`  
  `delta_p2_strength = 0.427679...`  
  `dominant_level = delta_p2`  
  `family_pass_flag = 1`

- **F3** (`large_negative`)  
  `mean_branch_match_frac = 0.657143...`  
  `mean_identity_strength = 0.614286...`  
  `delta_p2_strength = 0.635714...`  
  `dominant_level = delta_p2`  
  `family_pass_flag = 1`

- **F4** (`large_negative_distorted`)  
  `mean_branch_match_frac = 0.563012...`  
  `mean_identity_strength = 0.426024...`  
  `delta_p2_strength = 0.494518...`  
  `dominant_level = delta_p2`  
  `family_pass_flag = 1`

- **F5** (`falsification_candidate`)  
  `mean_branch_match_frac = 0.468381...`  
  `mean_identity_strength = 0.236762...`  
  `delta_p2_strength = 0.352571...`  
  `dominant_level = delta_p2`  
  `family_pass_flag = 0`

Rangordnung der Branch-/Mechanikstärke:

> **F3 > F4 > F1 > F2 > F5**

### 14.6 Matched-pair-Kernbefund

- **F2 vs F3**: `n_matched_pairs = 7`, `same_branch_fraction = 1.0`
- **F2 vs F4**: `n_matched_pairs = 9`, `same_branch_fraction = 1.0`

Damit gilt im finalen Lauf:

> Bei vergleichbarem `delta_p2` liefern die gematchten Paare aus F2 und F3/F4 durchgehend dieselbe Branch-Identität.

Das ist ein **klar positives mechanisches Signal** für die Relevanz von `delta_p2`.

### 14.7 F5 als Falsifikationskandidat

F5 fiel im erwarteten Sinn aus:

- `predicted_weak_flag = 1`
- `weaker_than_f2_f3_f4_flag = 1`
- `falsification_alert_flag = 0`

Zusätzlich lagen die beobachteten Werte von F5 unter denen der Hauptfamilien.

Damit gilt:

> F5 verhält sich im finalen Lauf tatsächlich als schwacher Gegenkandidat und löst keinen Falsifikationsalarm aus.

### 14.8 Differenzierte Lesart des Gesamtbefunds

Der finale Befund von M.3.9a.2 ist klarer als in der ersten Scaffold-Fassung:

1. `delta_p2` ist global dominant.
2. Der matched-pair-Kernbefund ist stark positiv.
3. F5 bleibt sauber schwach und alarmfrei.
4. Die Kandidatenfamilien F2/F3/F4 bestehen den Audit.
5. F1 bleibt derzeit noch knapp innerhalb der gewählten Kontrolltoleranz und gilt damit formell als kontrollartig genug.

Sachlich beste Lesart:

> M.3.9a.2 ist im finalen Stand global positiv und liefert zugleich ein starkes mechanisches Teilsignal: `delta_p2` erscheint nicht nur als dominanter Marker, sondern trägt bei matched pairs aus unterschiedlichen Familientypen konsistent dieselbe Branch-Identität; zugleich bleibt F5 als schwacher Gegenkandidat ohne Falsifikationsalarm deutlich abgesetzt.

### 14.9 Offene methodische Feinkante

Die einzige verbleibende Feinkante des Blocks betrifft **F1**.

F1 liegt mit `mean_branch_match_frac = 0.542857...` knapp unter der derzeitigen Kontrollschwelle `control_max_branch_strength = 0.55` und wird deshalb noch als „kontrollartig genug“ akzeptiert.

Das ist keine strukturelle Schwäche des Blocks, sondern eine **Feinjustagefrage der Kontrolltoleranz**.

### 14.10 Arbeitsfazit

> M.3.9a.2 ist nach Nachschärfung der Dominanz- und Passlogik global positiv und liefert ein starkes Signal dafür, dass `delta_p2` im neuen Familienraum nicht nur klassifikatorisch, sondern mechanisch relevant ist: Kandidatenfamilien bestehen, matched pairs zeigen identische Branch-Identitäten, und F5 bleibt als schwacher Gegenkandidat ohne Falsifikationsalarm klar abgesetzt.

---

## 15. Nächster Schritt nach M.3.9a.2

Mit dem finalen Stand von M.3.9a.2 ist ein wichtiger Zwischenpunkt erreicht. Daraus folgt jedoch nicht, dass der Mechanismus bereits abschließend bewiesen wäre.

### 15.1 Unmittelbare Konsequenz

Nach M.3.9a.2 ist die sinnvollste direkte Fortsetzung **nicht** ein weiterer rein interner Familienumbau, sondern die Öffnung des Tests nach außen:

> Der nächste starke Prüfblock soll testen, ob die in M.3.9a.2 beobachtete Marker- und Mechanikstruktur auch auf **literaturbasierten externen Referenzfamilien** trägt.

### 15.2 Konkreter Folgeblock

Der naheliegende nächste Block ist:

> **M.3.9x — Literaturbasierte Referenzfamilien und Bias-Check**

### 15.3 Minimalziele des Folgeblocks

1. Auswahl von **2–3 externen Referenzfamilien** aus physikalisch etablierten Kontexten  
2. Ableitung konkreter diskreter `p_values`-Sätze oder klarer Diskretisierungsrezepte  
3. Einspeisung dieser Familien in die bestehende Audit-Pipeline  
4. Prüfung von:
   - `delta_p2`-Dominanz
   - family-wise Stärke
   - matched-pair-Konsistenz, wo sinnvoll
   - Kontrast zu schwächeren oder symmetrischeren Referenzfällen

### 15.4 Methodische Leitlinie

> Externe Referenzfamilien dienen nicht dazu, unsere Hypothese dekorativ zu bestätigen, sondern dazu, sie an familienfremden, literaturbasierten Strukturen ernsthaft zu belasten.

---

## 16. Claude-Red-Team-Auswertung zu M.3.9a.2

Die externe Red-Team-Prüfung fiel insgesamt **kritisch, aber konstruktiv positiv** aus.

### 16.1 Haupturteil

> `delta_p2` ist nach M.3.9a.2 noch nicht als Mechanismus bewiesen, aber deutlich näher an eine mechanisch relevante Größe herangerückt als vor dem Block.

Der stärkste Einzelbefund bleibt der matched-pair-Cross-type-Test; zugleich wird betont, dass ohne gezielten Kausaltest und ohne externe Referenzfamilien weiterhin offen bleibt, ob `delta_p2` wirklich mechanisch trägt oder nur ein sehr robuster Korrelationsmarker ist.

### 16.2 Positiv bewertete Punkte

- der matched-pair-Befund ist der stärkste Fortschritt des Updates
- F5 ist schwächer als F2/F3/F4
- M.3.9a.2 markiert den Übergang von reiner interner Konsolidierung zu einer Phase, in der externe Validierung nötig wird

### 16.3 Zentrale Bremsen

#### a) Mechanismus vs. Marker
Noch fehlt der gezielte Eingriffstest:
`delta_p2` manipulieren, Rest möglichst konstant halten, und prüfen, ob sich die Branch-Identität entsprechend mitverschiebt.

#### b) Matched-pair-Befund noch mit zwei Vorbehalten
1. kleine Stichprobengröße  
2. interner Konstruktionsraum

#### c) F5 noch zu dekorativ
F5 ist schwächer, aber noch nicht sauber getrennt, **warum** es schwächer ist.

#### d) F1 als Warnsignal
Kontrolle und Kandidat sind methodisch noch nicht scharf genug getrennt.

### 16.4 Gefährlichste methodische Flanke: Runner-Logik-Tuning

- erster Scaffold-Lauf global negativ
- danach Logikänderung
- danach global positives Ergebnis

Daraus folgt die externe Minimalforderung:

> Die aktuelle Dominanz- und family-pass-Logik muss **vor** dem nächsten Datensatz vollständig fixiert und anschließend blind angewendet werden.

### 16.5 Vom Red-Team priorisierte nächste Schritte

#### Priorität 1 — Externe Referenzfamilien
Literatur- oder standardphysikalische Impulskonfigurationen in die Pipeline einspeisen.

#### Priorität 2 — Kausaler Manipulationstest
Existierende Familie minimal so verändern, dass `delta_p2` gezielt verschoben wird, während der Rest möglichst konstant bleibt.

#### Priorität 3 — F1/Kontrollschwelle vorab fixieren
Explizite Maximalwerte für Kontrollfamilien vorab definieren und blind anwenden.

### 16.6 Arbeitsfazit

> Die Claude-Red-Team-Auswertung bestätigt M.3.9a.2 als echten methodischen Fortschritt, verschiebt aber den Maßstab: Nicht weitere interne Nachpolitur, sondern jetzt Logik-Fixierung, externe Referenzfamilien, kausaler `delta_p2`-Manipulationstest und ein schärferer Falsifikationskandidat sind die prioritären nächsten Schritte.

---

## 17. Grok-Red-Team-Auswertung zu M.3.9a.2

Grok sitzt in der Hauptdiagnose fast deckungsgleich auf Claude.

### 17.1 Haupturteil

> M.3.9a.2 ist echter interner Fortschritt, aber noch kein belastbarer mechanischer Fortschritt. `delta_p2` ist derzeit ein sehr robuster Marker in einem intern optimierten Raum, noch kein gesicherter Mechanismus.

### 17.2 Grok bestätigt besonders klar

- Mechanismus vs. Marker: Kausalität fehlt weiterhin
- matched pairs: starkes Signal, aber `n=7` und `n=9` noch zu klein und methodisch nicht hart genug
- F5: noch zu dekorativ
- F1: klares Warnsignal
- Runner-Logik: gefährlichste Flanke
- Bias-Risiko: immer noch primär interner Konstruktionsraum

### 17.3 Prioritätenfolge von Grok

1. **Externe Referenzfamilien sofort starten**  
2. **Kausaler Manipulationstest an `delta_p2`**  
3. **Strengere, vorab fixierte F1/F5-Schwellen plus blinde Anwendung**

### 17.4 Arbeitsfazit

> M.3.9a.2 ist echter interner Fortschritt. Der matched-pair-Befund und die F5-Schwäche sind die besten Signale bisher. Aber wir sind noch nicht bei einem belastbaren mechanischen Fortschritt. Der aktuelle Stand ist ein starker Marker in einem intern optimierten Raum.

---

## 18. Gemeinsame Red-Team-Synthese (Claude + Grok)

Die unabhängigen externen Reviews von Claude und Grok laufen in drei Kernpunkten fast deckungsgleich zusammen:

1. **Noch kein belastbarer Mechanismusnachweis**  
   `delta_p2` ist derzeit ein sehr robuster Marker mit deutlich gestärkter Evidenz, aber der Kausaltest fehlt.

2. **Interner Konstruktionsraum bleibt die Hauptflanke**  
   Alle positiven Familien wurden mit Zielkenntnis konstruiert; externe Referenzfamilien sind jetzt zwingend.

3. **Runner-Logik-Tuning muss entschärft werden**  
   Die aktuelle Dominanz-/Passlogik muss vorab fixiert und blind auf den nächsten Datensatz angewendet werden.

### 18.1 Gemeinsame Prioritätenfolge

#### Priorität 1
**Externe Referenzfamilien / M.3.9x sofort starten**

#### Priorität 2
**Kausaler Manipulationstest an `delta_p2`**

#### Priorität 3
**F1/F5-Schwellen und gesamte Passlogik vorab fixieren und blind anwenden**

### 18.2 Integriertes Arbeitsfazit

> M.3.9a.2 bleibt ein echter Fortschritt, aber beide Red-Team-Quellen ziehen dieselbe Bremse: Jetzt nicht weiter intern nachpolieren, sondern den Schritt in externe Referenzfamilien, kausalen `delta_p2`-Test und vorab fixierte Logik vollziehen.

---

## 19. Aktueller Projektstatus

Der Projektstand ist jetzt:

- interner Marker `delta_p2` deutlich gestärkt
- M.3.9a.1 zeigt Typ-Reproduzierbarkeit
- M.3.9a.2 zeigt global positive interne Evidenz mit starkem matched-pair-Kern und schwachem F5-Gegenkandidaten
- beide Red-Team-Analysen bestätigen echten Fortschritt, aber verweigern noch die Mechanismus-Absegnung
- der nächste Abschnitt muss aus interner Konsolidierung in **externe Validierung und kausale Belastung** übergehen

---

## 20. Nächste konkrete To-dos

1. Aktuelle Dominanz- und family-pass-Logik als **vorab fixierte Regel** dokumentieren  
2. Pflichtenheft für **M.3.9x — Literaturbasierte Referenzfamilien und Bias-Check** erstellen  
3. Externe Referenzfamilien shortlist aus Deep Research operationalisieren  
4. Separaten Pfad für **kausalen Manipulationstest an `delta_p2`** definieren  
5. F1-Kontrollschwelle bewusst entscheiden und nicht stillschweigend nachziehen  
6. F5 später durch einen härteren, konstruktionsunabhängigeren Falsifikationstest ersetzen

---

## 21. Ein-Satz-Synthese des aktuellen Standes

> Das Projekt hat den Schritt von einem robusten internen Marker zu einem intern deutlich gestärkten, aber extern noch nicht abgesicherten Mechanismuskandidaten gemacht; nach M.3.9a.2 und den übereinstimmenden Red-Team-Analysen ist der nächste notwendige Schritt die vorab fixierte Auswertelogik plus externe Referenzfamilien und kausale Belastung von `delta_p2`.

---

## 22. Status

Dieser Masterchat ist der neue aktuelle Arbeitsstand und ersetzt ältere Zwischenfassungen als primäre Referenzbasis für die nächste Projektphase.
