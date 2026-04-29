# Neue Testvorschläge aus der Deep-Research-Außenkartierung  
## Projekt: Quantum–Spacetime Bridge

## Zweck

Diese Notiz übersetzt die stärksten Deep-Research-Treffer direkt in **neue, konkrete Testblöcke** für das Projekt.

Leitidee:

- **nicht** bloß Literaturwissen sammeln
- sondern aus externer Nachbarschaft **operative Probe-Logik** ableiten

Die Vorschläge sind so aufgebaut, dass sie an die bisherige BMC-/BMC-SX-Linie anschließen.

---

## 1. Strategische Grundrichtung

Aus der Außenkartierung ergeben sich derzeit drei besonders fruchtbare Testachsen:

### A. Ordnung tiefer als Shell
Externer Anker:
- Causal Sets
- Energetic Causal Sets

Interne Frage:
- Ist Shell nur eine sichtbare Realisierung einer tieferen Ordnungsfähigkeit?

### B. Organisation wichtiger als Verteilung
Externer Anker:
- Barrat weighted architecture
- DCSBM
- Motif-/Nullmodell-Literatur

Interne Frage:
- Bleibt der Befund bestehen, wenn Verteilungen konserviert, aber Organisation gezielt umgebaut wird?

### C. Bridge-sensitive Grenz- und Übergangsstruktur
Externer Anker:
- Ollivier-Ricci
- resistance perturbation
- backbone extraction
- persistent homology

Interne Frage:
- Sitzt bridge-facing Sensitivität bevorzugt an Grenzen, Brücken, Übergängen oder topologischen Hohlräumen?

---

## 2. Neue Testfamilien — Priorität A

## Test A1 — Orderability beneath shell
### Arbeitstitel
**BMC-02: latent-order vs shell-realization probe**

### Ziel
Prüfen, ob Shell nur eine abgeleitete Ordnungsprojektion ist, während ein tieferes Ordnungsmaß stabiler bleibt.

### Testidee
Konstruiere neben Shell σ mindestens ein zweites Ordnungsmaß τ, das **nicht** direkt als Shell definiert ist, z. B.:

- endpoint-load order
- pair-neighborhood order
- diffusion-based order
- curvature-based order
- block-inference order

Dann vergleiche unter preserving- und crossing-Eingriffen:

- Stabilität von σ
- Stabilität von τ
- Kopplung σ ↔ τ
- Drift zwischen beiden

### Kernfrage
Wenn τ robuster bleibt als σ, dann wäre das ein erster Hinweis auf:

> orderability tiefer als shell realization

### Minimalmetriken
- shell drift:
  \[
  \Delta_{\sigma} = \frac{1}{|V|}\sum_{v\in V} |\sigma'(v)-\sigma(v)|
  \]
- latent-order drift:
  \[
  \Delta_{\tau} = \frac{1}{|V|}\sum_{v\in V} |\tau'(v)-\tau(v)|
  \]
- shell-order coupling:
  \[
  C_{\sigma,\tau} = \operatorname{corr}(\sigma(v),\tau(v))
  \]

### Erwartung
- within-shell: geringe Δσ, geringe Δτ
- adjacent crossing: deutliche Δσ, moderatere Δτ
- full crossing: hohe Δσ, dann Vergleich, ob Δτ ebenfalls kollabiert oder robuster bleibt

### Priorität
Sehr hoch.

---

## Test A2 — Multi-order matrix
### Arbeitstitel
**BMC-03: multi-order consistency matrix**

### Ziel
Explizit mehrere reale Ordnungen getrennt messen, statt nur eine Shell-Schicht zu betrachten.

### Zu vergleichende Ordnungen
- \(\sigma\): shell order
- \(\tau_1\): endpoint-load order
- \(\tau_2\): pair-neighborhood order
- \(\tau_3\): DCSBM/block order
- \(\tau_4\): curvature order

### Testoutput
Konsistenzmatrix:

\[
M_{ij} = \operatorname{corr}(\tau_i,\tau_j)
\]

vor und nach Intervention.

### Kernfrage
Ist Ordnung im System:
- eindimensional
- mehrfach real
- oder nur diagnostisch induziert?

### Erwartung
Wenn mehrere Ordnungen unter Eingriffen verschieden driften, stützt das:
- tieferes Ordnungsbild
- reale Mehrlagenstruktur
- Shell als nur eine sichtbare Schicht

### Priorität
Sehr hoch.

---

## 3. Neue Testfamilien — Priorität B

## Test B1 — Distribution preserved, organization broken
### Arbeitstitel
**BMC-04: distribution-preserving organization scramble**

### Ziel
Den Satz „Arrangement matters more than distribution“ härter prüfen.

### Testidee
Erzeuge Kontrollsysteme, die erhalten:
- Gewichtsmultiset
- Degree-Sequenz
- Strength-Sequenz

aber gezielt zerstören:
- Blockstruktur
- Shell-Zuordnung
- lokale Nachbarschaftspassung
- motif profile

### Teilvarianten
1. weight multiset preserved only
2. degree + weight preserved
3. degree + strength + weight preserved
4. degree + strength + shell counts preserved
5. degree + strength + block counts preserved

### Kernfrage
Wie viel Organisationszerstörung ist möglich, bevor bridge-facing Readouts kippen?

### Minimalmetriken
- arrangement signal score
- block drift
- motif profile distance
- diffusion distance
- resistance perturbation distance

### Erwartung
Wenn der Befund auch bei stark konservierter Verteilung kippt, spricht das sehr klar für:
- Organisation > bloße Verteilung

### Priorität
Sehr hoch.

---

## Test B2 — Block-preserving vs block-breaking
### Arbeitstitel
**BMC-05: DCSBM-informed structure test**

### Ziel
Prüfen, ob eine inferierte Block-/Mesostruktur näher an der bridge-relevanten Organisation sitzt als Shell allein.

### Testidee
1. inferiere DCSBM/nested SBM auf Baseline
2. führe zwei Eingriffstypen aus:
   - block-preserving rewires
   - block-crossing rewires
3. vergleiche mit:
   - shell-preserving
   - shell-crossing

### Kernfrage
Welche frühe Organisationsform ist tragender:
- shell
- block
- beide
- oder keine von beiden?

### Minimalmetriken
- arrangement signal
- shell drift
- block assignment drift
- pair-neighborhood shift
- curvature shift

### Erwartung
Wenn block-breaking stärker schadet als shell-breaking, wäre Shell vielleicht nur sichtbarer Proxy einer tieferen Mesostruktur.

### Priorität
Hoch.

---

## Test B3 — Motif-sensitive BMC
### Arbeitstitel
**BMC-06: motif-sensitive weighted perturbation**

### Ziel
Prüfen, ob bridge-facing Ordnung an charakteristischen Kleinstrukturen hängt.

### Testidee
- berechne Motivprofil auf Baseline
- führe gewichtserhaltende Rewires durch
- zerstöre selektiv Motive:
  - intra-shell motifs
  - cross-shell motifs
  - bridge-adjacent motifs

### Kernfrage
Ist der Effekt:
- global verteilt
- oder an wenige strukturelle Kleinmuster gebunden?

### Priorität
Mittel bis hoch.

---

## 4. Neue Testfamilien — Priorität C

## Test C1 — Backbone-first bridge probe
### Arbeitstitel
**BMC-07: backbone scaffold isolation**

### Ziel
Structural-vs-diagnostic-Trennung härter machen.

### Testidee
Extrahiere Backbones mit:
- disparity filter
- noise-corrected backbone

Dann vergleiche:

1. Baseline full graph
2. baseline backbone only
3. perturbation on full graph
4. perturbation on backbone
5. perturbation only off-backbone

### Kernfrage
Sitzt die brückenrelevante Ordnung:
- im tragenden Backbone
- außerhalb davon
- oder in der Kopplung beider Schichten?

### Erwartung
Wenn Backbone-only große Teile des Signals trägt, wäre das ein starker Hinweis auf echten Scaffold-Kern.

### Priorität
Sehr hoch.

---

## Test C2 — Curvature-guided bridge probe
### Arbeitstitel
**BMC-08: curvature-sensitive boundary probe**

### Ziel
Prüfen, ob bridge-facing Sensitivität bevorzugt an grenznahen / negativ gekrümmten / strukturkritischen Kanten sitzt.

### Testidee
Berechne auf Baseline:
- Ollivier-Ricci curvature
- optional Forman curvature

Dann Eingriffe in Gruppen:
- most negative curvature edges
- near-zero curvature edges
- positive curvature edges

### Kernfrage
Sind Bridge-Kandidaten bevorzugt:
- Grenzkanten
- Spannungszonen
- Übergangsstellen?

### Minimalmetriken
- arrangement signal drop
- component/flow change
- shell-order drift
- pair-neighborhood shift

### Erwartung
Wenn negative-curvature edges überproportional kritisch sind, wäre das methodisch ein sehr starker Bridge-Probe.

### Priorität
Sehr hoch.

---

## Test C3 — Resistance ladder
### Arbeitstitel
**BMC-09: resistance-ranked disruption ladder**

### Ziel
Eine harte graded disruption ladder mit globalem Sensitivitätsmaß bauen.

### Testidee
Rangiere Kanten oder Paarzuordnungen nach:
- effective resistance contribution
- resistance perturbation impact

Dann Eingriffsserien:
- zufällig
- low-resistance first
- high-resistance first
- cross-shell & high-resistance
- cross-block & high-resistance

### Kernfrage
Welche Eingriffe zerstören globale Ordnung am effizientesten?

### Erwartung
Das liefert eine härtere Bruchleiter als bloß within/adjacent/full crossing.

### Priorität
Hoch.

---

## Test C4 — Persistent shell test
### Arbeitstitel
**BMC-10: topological persistence of derived order**

### Ziel
Prüfen, ob derived shell order in gewichteten Filtrationen nichtlokal sichtbar bleibt.

### Testidee
Baue gewichtete Filtrationen und berechne:
- connected components persistence
- hole / cycle persistence
- topological strata signatures

Vergleiche:
- baseline
- shell-preserving perturbation
- shell-crossing perturbation
- block-breaking perturbation
- curvature-targeted perturbation

### Kernfrage
Ist Shell:
- nur ein Ranking-Artefakt
- oder mit nichtlokaler topologischer Zwischenordnung gekoppelt?

### Priorität
Mittel bis hoch.

---

## 5. Neue Testfamilien — Priorität D

## Test D1 — Minimal critical set
### Arbeitstitel
**BMC-11: optimal-percolation scaffold failure test**

### Ziel
Die minimale strukturell kritische Menge von Kanten / Paaren / Knoten finden.

### Testidee
Suche minimale Mengen, deren Entfernung:
- arrangement signal stark senkt
- Shell/Block-Ordnungen fragmentiert
- globale Diffusions-/Resistanzstruktur kippt

### Kernfrage
Gibt es ein kleines tragendes Set, das den bridge-facing Scaffold zusammenhält?

### Priorität
Mittel.

---

## Test D2 — Geometry surrogate upgrade test
### Arbeitstitel
**BMC-12: replace placeholder geometry with real surrogate**

### Ziel
Die derzeitige Placeholder-Geometrie durch echte Surrogate ersetzen.

### Kandidaten
- diffusion distance geometry
- resistance geometry
- curvature-induced geometry
- shortest-path weighted geometry
- embedding-derived geometry

### Kernfrage
Bleibt der bridge-facing Effekt sichtbar, wenn Geometrie nicht als Dummy, sondern als echte abgeleitete Vergleichsschicht geführt wird?

### Priorität
Sehr hoch, aber nach den Kern-Organisationstests.

---

## 6. Empfohlene Reihenfolge

### Runde 1 — sofort
1. BMC-02 latent-order vs shell-realization
2. BMC-04 distribution-preserving organization scramble
3. BMC-07 backbone scaffold isolation
4. BMC-08 curvature-sensitive boundary probe

### Runde 2
5. BMC-05 DCSBM-informed structure test
6. BMC-09 resistance-ranked disruption ladder
7. BMC-03 multi-order consistency matrix

### Runde 3
8. BMC-06 motif-sensitive weighted perturbation
9. BMC-10 topological persistence of derived order
10. BMC-11 optimal-percolation scaffold failure test

### Runde 4
11. BMC-12 geometry surrogate upgrade test

---

## 7. Konkrete Minimalentscheidung für den nächsten Schritt

Wenn wir **nur einen einzigen** nächsten Test sofort aufsetzen wollen, würde ich wählen:

> **BMC-04: distribution-preserving organization scramble**

Warum?
Weil er am direktesten die derzeit stärkste Kernbehauptung prüft:

\[
	ext{Organisation} > 	ext{bloße Verteilung}.
\]

Wenn wir **zwei** Tests sofort aufsetzen wollen:

1. **BMC-04**
2. **BMC-08**

Dann hätten wir:
- einen harten Organisationstest
- und einen harten Bridge-/Grenztest

Wenn wir **drei** Tests sofort aufsetzen wollen:

1. **BMC-04**
2. **BMC-07**
3. **BMC-08**

Dann hätten wir:
- Verteilung vs Organisation
- Scaffold-Kern vs Restnetz
- Bridge-sensitive Grenzstruktur

Das wäre ein richtig starkes nächstes Paket.

---

## 8. Was wir dafür intern vorbereiten sollten

### Für BMC-04
- Baseline-Export mit Degree, Strength, Weight-Multiset, Shell-Zuordnung
- Rewire-Varianten definieren
- Erhaltungsklassen festlegen

### Für BMC-07
- disparity filter
- noise-corrected backbone
- backbone/off-backbone Vergleichsauswertung

### Für BMC-08
- ORC-/Forman-Berechnung
- Kantenranking nach Krümmung
- gezielte Eingriffsserien

### Für BMC-05
- DCSBM/nested SBM Toolpfad
- Blockassignment speichern
- block-preserving vs block-breaking Rewire-Logik

---

## 9. Schärfste Kurzfassung

> **Aus dem Deep Research folgt jetzt nicht “mehr lesen”, sondern eine neue Testgeneration: zuerst Organisation-gegen-Verteilung, dann Backbone-gegen-Restnetz, dann curvature-sensitive Bridge-Probes.**

Oder noch kürzer:

> **Die Literatur hat uns jetzt nicht nur Nachbarn geliefert, sondern neue Angriffsachsen für unsere Tests.**

---

## Bottom line

Ja — wir können und sollten jetzt mit den Deep-Research-Daten direkt neue Tests bauen.

Die stärksten nächsten Schritte sind:

- **BMC-04**: distribution-preserving organization scramble
- **BMC-07**: backbone scaffold isolation
- **BMC-08**: curvature-sensitive boundary probe

Wenn wir diese drei sauber fahren, dann haben wir:
- eine härtere Prüfung der Organisationshypothese
- eine klarere structural-vs-diagnostic-Trennung
- und eine viel bessere bridge-sensitive Probe-Architektur.
