# H3 Support-Side Manipulationsblock – Befundprotokoll

## 1. Ziel des Blocks
Der Block `H3_SUPPORT_MANIPULATION_DESIGN_01` dient der methodischen Prüfung des bislang einzigen kleinen support-side-H3-Befunds aus `N1_A1_B1_DECOUPLING`.

Er ist **kein Theoriebeweis** und **kein Vollnachweis einer package-role-Hierarchie**, sondern ein gezielter Test auf die Frage, ob ein lokaler support-seitiger Zusatzkontrast

- unter baseline-first erhalten bleibt,
- unter kontrollierter Manipulation geordnet skaliert,
- und unter Nullmodellen wieder auf ein niedriges bzw. nichttragendes Niveau zurückfällt.

## 2. Operative Grundidee
Der Block arbeitet mit einer A/B/C/D-Logik:

- **A** = baseline reference
- **B** = milde support-side Manipulation
- **C** = stärkere Manipulation auf derselben Achse
- **D1** = Permutations-Nullmodell
- **D2** = strukturkonservierendes Random-Nullmodell

Die zentrale Zielgröße ist `gain_value`, verstanden als zusätzlicher support-seitiger Kontrastgewinn der combined reading gegenüber der baseline reading.

## 3. Technische Entwicklung des Blocks
Der Block wurde schrittweise aufgebaut:

1. **Runner-Hülle erstellt**  
   Config, Schema, Templates und Runner-Skelett wurden erfolgreich aufgesetzt.

2. **V1-Inputlogik eingeführt**  
   Zunächst lief der Block mit einer kleinen Test-CSV zur Prüfung der reinen Maschinenraumlogik.

3. **Parameterprofile wirksam gemacht**  
   `base`, `mild_plus`, `mild_minus` wurden von bloßen Etiketten zu echten Profilfaktoren gemacht.

4. **Nullmodelle getrennt**  
   Das ursprüngliche D-Nullmodell wurde in
   - `D1 = permutation_null`
   - `D2 = topology_preserving_random_null`
   aufgeteilt.

5. **Projektnahe Decoupling-Daten angeschlossen**  
   Danach wurde der Input nicht mehr aus einer Demo-Tabelle, sondern aus den Decoupling-Artefakten (`matrices.npz`) erzeugt.

6. **Von row-based auf pair-based Export umgestellt**  
   Die ursprüngliche Zeilenaggregation erwies sich als zu grob.  
   Deshalb wurde auf eine Paar-/Kantenrepräsentation (`eij`) gewechselt.

7. **Support-like vs boundary-like eingeführt**  
   Die frühere grobe Zuordnung
   - `negative/abs = support`
   - `positive = neighbor`
   wurde durch eine feinere Paarlogik ersetzt:
   - `support_like`
   - `boundary_like`
   - `mixed_like`

## 4. Zentrales methodisches Problem unterwegs
Die erste pair-based D2-Analyse zeigte:

- Das Hauptsignal unter B/C blieb stabil.
- Aber `D2` wurde zeitweise leicht positiv.

Die Analyse ergab, dass dieser positive Drift **nicht** aus einem allgemeinen Kollaps der Nullhypothese stammte, sondern vor allem aus **ambigen positiven Paaren**, die unter strukturkonservierender Randomisierung in den effektiven Support rutschen konnten.

Das war ein wichtiger Befund:
Nicht der Runner war das Problem, sondern die zu grobe support/neighbor-Logik auf Paarebene.

## 5. Korrekturmaßnahme
Daraufhin wurde die Export- und Label-Logik präzisiert:

- **support_like**  
  Paare mit tragender Struktur, z. B. mit Adjazenz oder klar nichttrivialer baseline-/combined-Präsenz.

- **boundary_like**  
  Paare ohne Adjazenz und ohne tragendes Signal in beiden Zuständen.

- **mixed_like**  
  Ambige Paare, die weder sauber support-like noch sauber boundary-like sind.

Für den Runner gilt jetzt:
- `is_support = support_like`
- `is_neighbor = boundary_like`

Mixed-Paare werden **nicht** mehr zwangsweise in den boundary-Satz gepresst.

## 6. Aktueller Befundstand

### Hauptsignal
Der support-side Eintrag bleibt unter der aktuellen Logik stabil lesbar:

- `A = 0`
- `B > 0`
- `C > B`
- `mild_minus < base < mild_plus`

### Baseline-first
Die baseline bleibt primär:
- `baseline_first_preserved = true`

### Monotonie
Die Manipulationsachse bleibt geordnet:
- `monotone_support_scaling = true`

### Nullmodelle
Nach der support-like/boundary-like-Umstellung liegen beide Nullmodelle wieder konsistent auf der negativen Seite:

- `D1_permutation_null = -0.005667`
- `D2_topology_preserving_random_null = -0.005667`

### Gesamtstatus
Der Block ergibt derzeit:
- `overall_outcome = limited_supported`

## 7. Defensive Interpretation
Der Block liefert aktuell **keinen breiten Theorieclaim**.  
Er liefert einen **lokalen, methodisch deutlich verbesserten support-side entry**.

Die vorsichtige Lesart lautet:

> Ein kleiner support-seitiger Zusatzkontrast bleibt unter baseline-first erhalten, reagiert geordnet auf die Manipulationsstärke und bleibt gegenüber beiden aktuellen Nullmodellen positiv getrennt. Die Lesbarkeit ist jedoch weiterhin lokal und begrenzt; ein Vollnachweis einer größeren Rollen- oder Paketarchitektur ist daraus ausdrücklich nicht ableitbar.

## 8. Was der Block jetzt gut kann
- klare A/B/C/D1/D2-Architektur
- reproduzierbarer Runner
- echte Profilmodulation
- projektnahe Inputquelle aus Decoupling-Artefakten
- paarbasierte statt plattgebügelter Aggregation
- explizite Trennung zwischen support-like, boundary-like und mixed-like
- härtere und ehrlichere Nullmodellprüfung

## 9. Was weiterhin offen bleibt
- Der Befund ist weiterhin **klein und lokal**.
- Die Datenbasis ist noch nicht breit genug für eine starke Generalisierung.
- Die support-like/boundary-like-Regeln sind eine plausible, aber noch nicht endgültige operative Festlegung.
- Weitere Robustheitstests über zusätzliche Quellen, Parameter und alternative Score-Definitionen bleiben sinnvoll.

## 10. Aktuelle Arbeitsformel
Der Block kann intern derzeit so verbucht werden:

> **Methodisch verbesserter, lokal lesbarer support-side H3-Einstieg unter baseline-first mit geordneter Manipulationsreaktion und wieder stabilisierter Nullmodelltrennung nach pair-based support-like vs boundary-like Re-Labeling.**

## 11. Empfohlene Anschlussrichtung
Die nächsten sinnvollen Schritte wären:

1. denselben Block auf weitere projektnahe Quellen oder Varianten anwenden  
2. die support-like/boundary-like-Regel auf Robustheit prüfen  
3. alternative Score-Kanäle wie `kbar` vergleichend testen  
4. den aktuellen Stand als internen methodischen Zwischenbefund festhalten, aber noch nicht überdehnen
