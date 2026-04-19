# Befundprotokoll  
## H3_MIXED_LIKE_SENSITIVITY_01

## 1. Ziel des Tests
Der Block `H3_MIXED_LIKE_SENSITIVITY_01` dient der Prüfung, ob der aktuelle lokale support-side H3-Befund empfindlich auf die Behandlung der `mixed_like`-Paare reagiert.

Die zentrale Frage lautet:

> Bleibt der Befund stabil, wenn `mixed_like`-Paare alternativ als neutral, boundary-like oder support-like behandelt werden?

Der Test ist damit ein gezielter Härtetest gegen den Vorwurf, dass die aktuelle support/boundary/mixed-Logik den Befund künstlich stützt.

## 2. Ausgangspunkt
Ausgangspunkt war der eingefrorene pair-based H3-Block mit:

- paarbasierter Exportstruktur
- G-basierter Score-Definition
- `support_like`
- `boundary_like`
- `mixed_like`

Im Freeze-Stand galt:

- `is_support = support_like`
- `is_neighbor = boundary_like`

Mixed-Paare wurden also neutral behandelt und nicht in den harten boundary-Satz aufgenommen.

## 3. Getestete Mapping-Modi
Für den Sensitivitätstest wurden drei Mapping-Modi definiert:

### M0 — mixed_as_neutral
- `is_support = support_like`
- `is_neighbor = boundary_like`

### M1 — mixed_as_boundary
- `is_support = support_like`
- `is_neighbor = boundary_like OR mixed_like`

### M2 — mixed_as_support
- `is_support = support_like OR mixed_like`
- `is_neighbor = boundary_like`

Wichtig:
Außer diesem Mapping wurde **keine weitere Logik geändert**.  
Score-Definition, Paarrepräsentation, Profilfaktoren, Zustandsarchitektur und Nullmodelle blieben unverändert.

## 4. Testarchitektur
Für jeden Mapping-Modus wurden erneut die Zustände gerechnet:

- `A`
- `B`
- `C`
- `D1`
- `D2`

mit den bekannten Profilen:

- `base`
- `mild_minus`
- `mild_plus`

und den Seeds:

- `101`
- `202`
- `303`
- `404`
- `505`

## 5. Hauptbefund
Alle drei Mapping-Modi ergeben denselben Gesamtstatus:

- `overall_outcome = limited_supported`

Zusätzlich bleibt in allen drei Modi erhalten:

- `A < B < C`
- `baseline_first_preserved = true`
- `monotone_support_scaling = true`
- `null_model_suppression = true`

Das ist der zentrale Robustheitsbefund des Blocks.

## 6. Numerischer Überblick

### M0 — mixed_as_neutral
- `gain_A = 0.0`
- `gain_B = 0.346623`
- `gain_C = 0.696622`
- `gain_D1 = -0.005667`
- `gain_D2 = -0.005667`

### M1 — mixed_as_boundary
- `gain_A = 0.0`
- `gain_B = 0.346623`
- `gain_C = 0.696622`
- `gain_D1 = -0.005667`
- `gain_D2 = -0.002834`

### M2 — mixed_as_support
- `gain_A = 0.0`
- `gain_B = 0.343789`
- `gain_C = 0.693789`
- `gain_D1 = -0.005667`
- `gain_D2 = -0.006211`

## 7. Interpretation der drei Modi

### 7.1 M0 — Neutralbehandlung
Der Referenzmodus bestätigt den bereits bekannten Freeze-Stand:
- B/C bleiben klar positiv,
- D1 und D2 bleiben niedrig und negativ.

### 7.2 M1 — mixed_as_boundary
Wenn mixed-Paare vollständig in den Neighbor-Satz aufgenommen werden,
- bleiben B und C praktisch unverändert,
- D2 wird leicht weniger negativ,
- kippt aber nicht ins Positive.

Das heißt:
Der Befund hängt **nicht** daran, dass mixed-Paare aus dem boundary-Satz herausgehalten werden.

### 7.3 M2 — mixed_as_support
Wenn mixed-Paare in den Support-Satz aufgenommen werden,
- bleiben B und C ebenfalls stabil,
- werden sogar minimal kleiner,
- D2 bleibt negativ.

Das heißt:
Der Befund wird durch mixed-Paare **auch nicht künstlich aufgeblasen**, wenn man sie support-seitig mitzählt.

## 8. Zentrale methodische Aussage
Der Test zeigt:

> Die aktuelle `support_like / boundary_like / mixed_like`-Logik ist **nicht bloß ein fragiler Tuning-Hebel**.

Denn der H3-Befund bleibt nicht nur im Referenzmodus bestehen, sondern auch unter beiden naheliegenden Gegenmappings:

- mixed-like als boundary
- mixed-like als support

Damit verliert der Vorwurf deutlich an Kraft, dass die Neutralbehandlung von mixed-Paaren den Block künstlich trägt.

## 9. Was der Test ausdrücklich **nicht** zeigt
Der Test zeigt **nicht**:
- einen Vollnachweis der H3-Logik,
- keinen Nachweis einer größeren package-role-Hierarchie,
- keine breite Generalisierung über andere Quellen,
- und keine abschließende Widerlegung aller Nullmodell-Einwände.

Insbesondere bleibt die Frage nach der **wirklichen Trennung von D1 und D2** weiterhin ein relevanter nächster Härtetest.

## 10. Defensive Gesamtlesart
Die defensiv angemessene Lesart lautet:

> Der lokale support-side H3-Befund bleibt unter drei unterschiedlichen Behandlungen der mixed-like-Paare stabil. Die geordnete A/B/C-Struktur bleibt erhalten, und beide Nullmodelle bleiben in allen Modi niedrig bzw. negativ. Damit wirkt der Block gegenüber der Behandlung ambiger Paare robuster als zunächst befürchtet.

## 11. Projektinterne Schlussfolgerung
Der Sensitivitätstest kann intern als **bestandener Robustheitstest** verbucht werden.

Kurzform:
- `mixed_like` ist **nicht** der entscheidende versteckte Hebel,
- der Befund ist gegenüber dieser Label-Variation stabil,
- die support-like/boundary-like-Logik wirkt damit methodisch plausibler.

## 12. Offene Folgefragen
Nach diesem Test bleiben vor allem folgende Punkte offen:

1. **D1 vs. D2**
   - Warum liegen beide so nah beieinander?
   - Reicht die aktuelle D2-Definition als wirklich unabhängiger harter Test?

2. **Weitere Replikation**
   - Bleibt dieselbe Struktur auf anderen Quellen / source blocks erhalten?

3. **Alternativer Primärscore**
   - Sollte `kbar` zusätzlich oder alternativ systematisch geprüft werden?

4. **Dichterer Manipulations-Sweep**
   - Ist die beobachtete A/B/C-Ordnung auch mit mehr Zwischenstufen stabil?

## 13. Aktuelle Arbeitsformel
Der Block kann nach diesem Test intern so verbucht werden:

> **Der lokale support-side H3-Einstieg bleibt unter pair-based mixed-like-Sensitivitätsprüfung robust. Die geordnete Manipulationsreaktion und die Nullmodelltrennung bleiben über drei Mapping-Modi erhalten.**

## 14. Kurze Einordnung
Das ist kein spektakulärer Theoriedurchbruch.  
Aber es ist ein **ernster methodischer Fortschritt**, weil ein naheliegender Kritikpunkt explizit getestet wurde — und der Befund dabei **nicht** zusammenbricht.
