# Formelnotiz: aktuelle Testformeln und bisherige mathematische Beschreibung des Phänomens  
## Projekt: Quantum–Spacetime Bridge

## Zweck dieses Dokuments

Diese Notiz sammelt in kompakter, projektinterner Form:

1. die **aktuellen Testformeln** aus den BMC-01- und BMC-01-SX-Probes  
2. eine **vorsichtige mathematische Beschreibung** unseres derzeitigen Phänomenbildes  
3. eine saubere Trennung zwischen
   - **strukturellem Kern**
   - **abgeleiteten Ordnungsschichten**
   - **diagnostischen Größen**

Wichtig:
Das ist **keine fertige Endtheorie** und **keine endgültige Publikationsform**.  
Es ist eine Maschinenraum-Zusammenstellung auf Basis unserer bisherigen Notes, Scripts und Readout-Logiken.

---

## 1. Aktueller mathematischer Grundrahmen

### 1.1 Supportmenge und relationale Basis

Wir betrachten zunächst eine endliche Menge von Stützstellen / Knoten / Support-Einheiten

\[
V = \{v_1, \dots, v_n\}.
\]

Darauf liegt eine Menge relationaler Paarungen

\[
E \subseteq V \times V.
\]

Für jede relationale Paarung \(e_{ij} = (v_i,v_j)\) gibt es eine zugeordnete Gewichtung

\[
w_{ij} \in \mathbb{R}_{\ge 0}.
\]

Damit erhält man als derzeit stärkste low-level-Arbeitsbasis ein **gewichtetes relationales System**

\[
G = (V,E,w).
\]

In Matrixform kann man äquivalent mit einer gewichteten Adjazenz-/Relationsmatrix arbeiten:

\[
W = (w_{ij})_{i,j=1}^n,
\qquad
w_{ij}=0 \text{ falls } (v_i,v_j)\notin E.
\]

### 1.2 Derzeitige Kernhypothese

Unsere derzeitige minimale Arbeitshypothese lautet:

\[
\text{bridge-relevante Struktur} \not\equiv \text{bloße Topologie},
\]

sondern sitzt tiefer in einer **gewichteten relationalen Organisation**.

Also:

\[
\mathcal{B}_{\text{cand}} \;\subseteq\; \mathcal{F}(V,E,w),
\]

wobei \(\mathcal{B}_{\text{cand}}\) den aktuellen Kandidatenraum der brückenrelevanten Struktur bezeichnet.

---

## 2. Aktuelles Schichtenbild in mathematischer Kurzform

### 2.1 Primitive Kandidatenschicht

Der derzeitige primitive oder nahe-primitiven Kandidat ist:

\[
\mathcal{P} = (V,E,w)
\]

oder, noch vorsichtiger formuliert,

\[
\mathcal{P} = (V,E,w,\mathcal{O}_\ast?)
\]

mit einer eventuell tiefer liegenden Ordnungsfähigkeit \(\mathcal{O}_\ast\), die noch nicht endgültig eingeordnet ist.

### 2.2 Frühe abgeleitete Ordnung

Shell-Ordnung wird derzeit **nicht** als primitiv behandelt, sondern als abgeleitete, aber reale Ordnungsform:

\[
\sigma : V \to \{1,2,\dots,S\}
\]

oder auf Paar-/Relationsniveau

\[
\sigma_E : E \to \{s_1,\dots,s_S\}.
\]

Wichtig ist dabei:

\[
\sigma \text{ ist nicht vorausgesetzt als primitive Basis,}
\]

sondern wird als erste robuste realisierte Ordnungsschicht aufgefasst.

### 2.3 Höhere Brückenschicht

Darüber liegt ein noch nicht voll formalisiertes, aber als realer Kandidat behandeltes bridge-facing Scaffold-Verhalten:

\[
\mathcal{S}_{\text{bridge}} = \mathcal{S}(V,E,w,\sigma,\dots)
\]

Das ist derzeit **strukturell gemeint**, aber nur **diagnostisch zugänglich**.

### 2.4 Diagnostische Größen

Die diagnostischen Größen sind **nicht** mit der Struktur selbst zu verwechseln. Formal:

\[
D_k = D_k(V,E,w,\sigma,\dots)
\]

sind Readouts / Testfunktionen / Vergleichsmaße, aber **nicht** Ontologie.

Kurzregel:

\[
\text{Scores sind Sonden, nicht Struktur.}
\]

---

## 3. Derzeitige mathematische Minimalbeschreibung des Phänomens

Die bisher stärkste mathematische Kurzbeschreibung unseres Phänomens wäre derzeit:

### 3.1 Gewichtete relationale Organisation

Die relevante Struktur hängt nicht nur von
- der Existenz einer Kante
- oder der bloßen Gewichtsverteilung

ab, sondern von der **Platzierung** und **Organisation** der Gewichte:

\[
\Phi \neq \Phi(E) \quad\text{und}\quad \Phi \neq \Phi(\{w_{ij}\}_{\text{multiset}})
\]

sondern eher

\[
\Phi = \Phi(V,E,w,\text{Anordnung}(w),\text{Ordnung}(w),\dots).
\]

### 3.2 Tiefe Orderability-Hypothese

Es ist derzeit plausibel, dass es eine tiefere Ordnungsfähigkeit gibt, die unterhalb expliziter Shell-Realisierung liegt:

\[
\mathcal{O}_\ast \prec \sigma,
\]

also:
\[
\text{orderability tiefer als shell realization.}
\]

Nicht im Sinne einer schon abgeschlossenen Theorie, sondern als aktuelle Strukturhypothese.

### 3.3 Derived but real shell order

Die Shell-Schicht verhält sich nach aktuellem Stand wie:

\[
\sigma = \mathcal{S}_{\sigma}(V,E,w;\mathcal{O}_\ast?)
\]

also als **realisierte Ordnungsform**, nicht als primitive Urschicht.

### 3.4 Arrangement-sensitive bridge response

Das empirisch-methodische Phänomenbild lautet derzeit:

\[
\Delta_{\text{arrangement}} > 0
\]

auch dann, wenn grobe Verteilungsgrößen weitgehend stabil bleiben.

Noch schärfer:

\[
\text{preserve shell} \;<\; \text{adjacent shell crossing} \;<\; \text{full shell crossing}
\]

bezogen auf Disruptionsstärke der bridge-facing Ordnung.

Das ist im Moment die stärkste interne Leiterformel.

---

## 4. Aktuelle BMC-01-Testlogik

BMC-01 testet, ob gewichtete relationale Umordnungen bridge-facing Readouts verändern, **ohne** die grobe Topologie aufzugeben.

## 4.1 Grundobjekt des Tests

Gegeben sei eine Basistabelle mit Paaren \(p \in E\) und Gewichten \(w(p)\).

Die Intervention erzeugt ein gestörtes System

\[
G' = (V,E,w')
\]

mit gleicher oder weitgehend gleicher Kantenmenge \(E\), aber umgehängter Gewichtsanordnung \(w'\).

---

## 4.2 Basisgrößen der Gewichtsverteilung

Sei

\[
\mu_w = \frac{1}{|E|}\sum_{p\in E} w(p)
\]

der Mittelwert der Gewichte und

\[
\sigma_w = \sqrt{\frac{1}{|E|}\sum_{p\in E}(w(p)-\mu_w)^2}
\]

die Standardabweichung.

Dann ist im aktuellen Skript der **bridge signal score** definiert als

\[
B_{\text{sig}} =
\begin{cases}
\left|\dfrac{\sigma_w}{\mu_w}\right|, & |\mu_w| > 10^{-12} \\
\sigma_w, & \text{sonst}.
\end{cases}
\]

Das ist also im Kern ein Variations-/Streuungsmaß relativ zum Mittel.

### Interpretation
Diese Größe ist **diagnostisch**, nicht strukturell.  
Sie misst grob, wie stark das Gewichtsprofil kontrastiert.

---

## 4.3 D1/D2-Separation

Im Skript wird die D1/D2-Separation aktuell quantilbasiert definiert:

\[
D_{1/2} = Q_{0.90}(w) - Q_{0.10}(w).
\]

Also:

- \(Q_{0.90}\): 90%-Quantil
- \(Q_{0.10}\): 10%-Quantil

### Interpretation
Auch das ist eine **Readout-Größe**, kein primitives Objekt.

---

## 4.4 Weighted relational contrast score

Der gewichtete Kontrast ist die mittlere absolute Abweichung vom Mittelwert:

\[
C_w = \frac{1}{|E|}\sum_{p\in E} |w(p)-\mu_w|.
\]

### Interpretation
Diese Größe reagiert auf den Kontrast der Gewichte, aber noch nicht direkt auf deren tiefe Organisationslogik.

---

## 4.5 Endpoint loads

Für einen Knoten \(v\in V\) definieren wir die gesamte anliegenden Gewichtsmasse als

\[
L(v) = \sum_{p\in E:\, v\in p} w(p).
\]

Im Skript wird daraus der **endpoint load shift score** zwischen Baseline und Perturbation über den mittleren Absolutunterschied berechnet:

\[
\Delta_{\text{endpoint}} =
\frac{1}{|V|}\sum_{v\in V} |L'(v)-L(v)|.
\]

Genauer im Code: Mittelwert der absoluten Deltas nach Merge über den Schlüssel `endpoint`.

### Interpretation
Das ist bereits arrangement-sensitiver als reine Verteilungsmaße.

---

## 4.6 Pair-neighborhood consistency

Für ein Paar \(p=(a,b)\) wird zunächst der lokale Kontext aus den Endpunktlasten gebildet:

\[
N(p) = \frac{L(a)+L(b)}{2}.
\]

Dann die Konsistenzabweichung:

\[
K(p) = |w(p)-N(p)|.
\]

Der zugehörige Shift-Score zwischen Baseline und Perturbation ist wieder der mittlere absolute Delta-Wert:

\[
\Delta_{\text{pair-neigh}} =
\frac{1}{|E|}\sum_{p\in E} |K'(p)-K(p)|.
\]

### Interpretation
Das ist eine nützliche diagnostische Größe für die Passung eines Paares in seinen lokalen relationalen Kontext.

---

## 5. Erweiterte arrangement-sensitive BMC-01-Formeln

In der nachgeschärften Fassung wurden zusätzliche arrangement-sensitive Größen eingebaut.

## 5.1 Endpoint-load dispersion shift

Sei

\[
\sigma_L = \operatorname{std}\big(L(v)\big)_{v\in V}.
\]

Dann:

\[
\Delta_{\text{disp}} = |\sigma_L' - \sigma_L|.
\]

### Interpretation
Misst, ob die Ungleichverteilung der Lasten über die Knoten sich verändert.

---

## 5.2 Shell-internal pair rank score

Für Paare innerhalb derselben Shell wird ein Gewichts-Ranking gebildet. Formal für Paar \(p\) in Shell \(s\):

\[
r_s(p) = \operatorname{rank}_{q \in E_s}\big(w(q)\big)
\]

mit absteigender Ordnung.

Der **shell arrangement shift score** ist dann:

\[
\Delta_{\text{shell-rank}} =
\frac{1}{|E|}\sum_{p\in E} |r_s'(p)-r_s(p)|.
\]

### Interpretation
Diese Größe reagiert darauf, ob die interne Gewichtsordnung innerhalb der Shell erhalten bleibt oder nicht.

---

## 5.3 Arrangement signal score

Im BMC-01-v2-/SX-Stil ist der zusammengesetzte arrangement signal score der Mittelwert mehrerer Teilsignale.

Für BMC-01-SX konkret:

\[
A =
\frac{
\Delta_{\text{endpoint}}
+
\Delta_{\text{disp}}
+
\Delta_{\text{shell-rank}}
+
\Delta_{\text{pair-neigh}}
+
\Delta_{\text{shell-boundary}}
}{5}.
\]

In der früheren BMC-01-v2-Logik ohne shell-boundary-Term entsprechend als Mittelwert der damals vorhandenen arrangement-sensitive Komponenten.

### Interpretation
Das ist derzeit der wichtigste zusammengesetzte **diagnostische** Marker für echte Organisationsänderung.

---

## 6. BMC-01-SX: shell-preserving vs shell-crossing

BMC-01-SX vergleicht gezielt:
- shell-preserving Reassignments
- shell-crossing Reassignments

## 6.1 Shell crossing fraction

Wenn `shell_crossing_flag(p)` 1 ist, falls ein Paar über Shell-Grenzen hinweg umgehängt wurde, dann gilt:

\[
f_{\text{cross}} =
\frac{1}{|E|}\sum_{p\in E} \mathbf{1}_{\text{cross}}(p).
\]

### Interpretation
Anteil der tatsächlich shell-brechenden Interventionen.

---

## 6.2 Shell distance mean

Wenn zwischen Ursprungs- und Ziel-Shell eine Distanz \(d_{\text{shell}}(p)\) definiert ist, dann:

\[
\bar d_{\text{shell}} =
\frac{1}{|E|}\sum_{p\in E} d_{\text{shell}}(p).
\]

### Interpretation
Nicht nur ob crossing stattfindet, sondern wie weit.

---

## 6.3 Shell boundary disruption score

Im aktuellen Skript:

\[
\Delta_{\text{shell-boundary}} =
f_{\text{cross}} \cdot \max(1,\bar d_{\text{shell}}).
\]

### Interpretation
Das ist eine bewusst einfache, aber brauchbare erste Operationalisierung von Shell-Grenzverletzung.

---

## 6.4 Leiterbefund

Der derzeit stärkste empirische Maschinenraumbefund lautet:

\[
A_{\text{within-shell}}
<
A_{\text{adjacent-crossing}}
<
A_{\text{full-crossing}}.
\]

Das kann man als erste graded disruption ladder lesen.

### Projektinterne Deutung
Je breiter reale Shell-Mitgliedschaft gebrochen wird, desto stärker reagiert die bridge-facing Organisationsdiagnostik.

---

## 7. Kontroll- und Entscheidungslogik

## 7.1 Topology preservation

Im derzeitigen Scaffold wird Topologieerhalt grob als Bedingung verlangt:

\[
S_{\text{topology}} \approx 1.
\]

Im aktuellen Skript ist dieser Wert für die Shell-Crossing-Probe faktisch als Platzhalter

\[
S_{\text{topology}} = 1.0
\]

gesetzt.

### Wichtiger Hinweis
Das ist **noch keine harte mathematische Topologie-Invarianzprüfung**, sondern derzeit ein methodischer Placeholder.

---

## 7.2 Geometry surrogate similarity

Auch die coarse geometry similarity ist derzeit noch nicht voll ausgebaut; im Shell-Crossing-Skript steht derzeit faktisch ein Placeholder-Wert:

\[
S_{\text{geom}} = 0.5.
\]

### Wichtiger Hinweis
Diese Größe ist im jetzigen Stand **noch nicht** als echte geometrische Testfunktion zu überdeuten.

---

## 7.3 Shell-order leaning / carrier leaning

Die Entscheidungslabels sind logisch von den Readouts abgeleitet, aber **selbst nicht Teil der Struktur**.

Formal:

\[
\text{label} = \mathcal{D}_{\text{decision}}(A,\Delta C,\Delta D,\dots)
\]

und nicht:

\[
\text{label} \in \mathcal{P} \text{ oder } \mathcal{S}_{\text{bridge}}.
\]

Kurz:

\[
\text{Labels sind Diagnosen, nicht Ontologie.}
\]

---

## 8. Derzeit beste mathematische Kompaktfassung unseres Phänomens

Wenn ich unsere bisherige Lage in möglichst wenige Formeln komprimiere, dann so:

### 8.1 Primitive Arbeitsbasis

\[
G=(V,E,w)
\]

mit konstitutiver gewichteter relationaler Struktur.

### 8.2 Mögliche tiefe Ordnungsfähigkeit

\[
\mathcal{O}_\ast \text{ tief oder ko-tief zu } (V,E,w).
\]

### 8.3 Reale, aber abgeleitete Shell-Ordnung

\[
\sigma = \mathcal{S}_{\sigma}(V,E,w;\mathcal{O}_\ast?)
\]

mit

\[
\sigma \notin \text{primitive Basis},
\qquad
\sigma \not\equiv \text{bloße Diagnostik}.
\]

### 8.4 Bridge-facing Scaffold-Verhalten

\[
\mathcal{S}_{\text{bridge}} = \mathcal{S}(V,E,w,\sigma,\dots)
\]

als höhere Organisationsschicht.

### 8.5 Diagnostische Readout-Familie

\[
D = \{B_{\text{sig}}, D_{1/2}, C_w, \Delta_{\text{endpoint}}, \Delta_{\text{disp}}, \Delta_{\text{shell-rank}}, \Delta_{\text{pair-neigh}}, \Delta_{\text{shell-boundary}}, A\}.
\]

### 8.6 Der bisher stärkste Testbefund

\[
\text{preserving shell organization} 
\quad < \quad
\text{adjacent shell breaking}
\quad < \quad
\text{full shell breaking}
\]

im Ausmaß der arrangement-sensitive Disruption.

---

## 9. Was davon schon mathematisch belastbar ist – und was noch nicht

## 9.1 Schon belastbar im Projekt-Sinn
- gewichtete relationale Arbeitsbasis \(G=(V,E,w)\)
- endpoint loads
- pair-neighborhood context
- arrangement delta scores
- shell-crossing fraction
- shell-boundary disruption
- arrangement signal score
- graded shell-crossing ladder als empirische Testbeobachtung

## 9.2 Noch nur provisorisch / placeholder / theorieoffen
- echte primitive Definition von \(\mathcal{O}_\ast\)
- generatives Gesetz, das \(\sigma\) aus \((V,E,w)\) zwingend erzeugt
- saubere strukturelle Gleichung für \(\mathcal{S}_{\text{bridge}}\)
- echte geometrische Similarity-Metrik im Testsystem
- carrier-vs-marker-Entscheidung als voll belastbare Theorieaussage

---

## 10. Vorschlag für die nächsten mathematischen Dokumente

Aus dieser Notiz sollten sich direkt drei Folgepapiere ableiten lassen:

### A. `docs/current-test-formulas-note.md`
Saubere, kurze Sammlung nur der tatsächlich im Code benutzten Testformeln.

### B. `docs/current-phenomenon-math-description.md`
Vorsichtige mathematische Beschreibung unseres derzeitigen Phänomens:
primitive layer, orderability, shell derivation, scaffold, diagnostics.

### C. `docs/bridge-functional-candidates-note.md`
Mögliche nächste Stufe:
Welche Functionals / Objectives / Ordnungsfunktionen könnten unser Minimalgesetz tragen?

---

## Bottom line

Ja — aus unseren bisherigen Notes und Testlogiken lässt sich bereits eine **erste mathematische Beschreibung** zusammenstellen.

Die knappste Fassung lautet derzeit:

\[
G=(V,E,w)
\]

als gewichtete relationale Kernschicht,

\[
\mathcal{O}_\ast
\]

als möglicher tiefer Ordnungsfähigkeitskandidat,

\[
\sigma = \mathcal{S}_{\sigma}(V,E,w;\mathcal{O}_\ast?)
\]

als **derived but real** early order layer,

und

\[
D=\{D_k\}
\]

als diagnostische Readout-Familie, die **nicht** mit der Struktur selbst verwechselt werden darf.

Der bislang stärkste empirische Maschinenraum-Satz in Formelgestalt ist:

\[
A_{\text{within-shell}}
<
A_{\text{adjacent-crossing}}
<
A_{\text{full-crossing}}.
\]

Das ist noch keine Endtheorie — aber es ist schon deutlich mehr als bloße Intuition.
