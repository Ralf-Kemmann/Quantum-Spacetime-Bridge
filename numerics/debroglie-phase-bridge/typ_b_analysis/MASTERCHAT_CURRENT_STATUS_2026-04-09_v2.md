
### Markerblock `negative vs abs` (korrigierter Stand)

**Ziel.**  
Prüfung, ob zusätzliche Markerfamilien innerhalb des robusten Oberblocks `negative/abs > positive` doch noch eine reproduzierbare innere Differenz `negative > abs` sichtbar machen.

**Geprüfte Markerfamilien.**  
- Strukturmarker  
- Gewichtsmarker  
- Kanalmarker  

auf derselben eingefrorenen Basis:
- `adjacency_plus_threshold @ tau=0.025`
- Datensätze: `k0`, `theta_0.03`, `n1a_alpha`

**Wichtige Korrektur.**  
Im ersten Lauf zeigte der Markerblock formal ein `abs_advantage`. Das erwies sich jedoch als numerisches Artefakt in der Gewichtsfamilie:
- nicht-endliche Werte (`inf`, `nan`) in Gewichtsmarkern
- fehlerhafte Winner-Zuordnung bei `nan`
- dadurch künstlicher Ausschlag zugunsten von `abs`

Nach Korrektur der nicht-endlichen Behandlung wurde der Markerblock neu gerechnet.

**Korrigierter Befund.**
- `k0` baseline: `tie`
- `k0` alternative: `tie`
- `theta_0.03` baseline: `tie`
- `theta_0.03` alternative: `tie`
- `n1a_alpha` baseline: `tie`
- `n1a_alpha` alternative: `tie`

**Blockurteil.**  
- `inconclusive`

**Lesart.**  
Der korrigierte Markerblock liefert keine zusätzliche Evidenz für `negative > abs`.  
Er liefert nach Korrektur aber auch keine belastbare Evidenz für `abs > negative`.

**Konsequenz für den Gesamtstand.**  
Damit bleibt die derzeit defensiv belastbare Zwischenbilanz:
- robust: `negative ≈ abs > positive`
- offen/nicht gezeigt: `negative > abs`

Der Markerblock stärkt somit nicht die innere Trennung des Oberblocks, sondern bestätigt deren derzeitige Nicht-Sichtbarkeit.


### Vergleich mit dem Primeon-Paper (John G. de la Torre) — interne Einordnung

**Anlass.**  
Das gesichtete Primeon-Paper (*Amplitude–Phase State Dynamics as a Pre-Geometric Origin of Gravity*) verfolgt ebenfalls einen pre-geometrischen Emergenzansatz, in dem Gravitation aus einer polaren Zustandsstruktur `℘ = A e^{iθ}` hervorgehen soll. Die Nähe im Vokabular macht einen internen Vergleich sinnvoll.

**Gemeinsame Richtung.**  
Beide Projekte teilen eine ähnliche ontologische Grundbewegung:
- Raumzeit/Geometrie nicht als fundamental,
- sondern als emergente Beschreibung tieferer Zustands- oder Relationsstruktur.
- Sowohl dort als auch hier spielen Amplitude/Phase bzw. Interferenz-/Korrelationsstruktur eine zentrale Rolle.

**Worin das Primeon-Paper stärker wirkt.**
1. Es ist stärker **paperförmig geschlossen**: klare Framework-Erzählung, Variationsprinzip, Feldgleichungen, weak-field map, tensorieller Ausbau.
2. Es besitzt ein einheitlicheres theoretisches Vokabular und wirkt dadurch auf den ersten Blick „weiter“.

**Worin das Primeon-Paper nicht klar weiter ist.**
1. Mehrere zentrale Brückenstücke werden im aktuellen Stand **gesetzt statt hergeleitet**:
   - die emergente Metrik wird über einen minimalen Ansatz eingeführt,
   - die Konstante `α` zur Verbindung von `ln A` mit dem Newton-Potential bleibt offen,
   - Newtons Konstante `G` ist nicht mikroskopisch hergeleitet,
   - der Einstein-Hilbert-Term wird zunächst konservativ hinzugefügt, die eigentliche induzierte Herleitung bleibt programmatisch.
2. Das Papier benennt selbst fundamentale offene Meilensteine:
   - Metrik wirklich ableiten,
   - `G` herleiten,
   - GR-Lösungen recovern,
   - anomale Vorhersagen identifizieren.
3. Der gezeigte Newton-Fall ist eher ein **Konsistenzbeispiel im Minimalregime** als ein harter emergenter Durchstich.

**Worin unser Projekt derzeit stärker ist.**
1. **Adversariale Testtiefe:** Nullmodelle, Markerprüfungen, A1/B1-Entkopplung, Fehlerfunde und Korrekturen.
2. **Defensive Wissenschaftlichkeit:** robuste Zwischenbilanz statt glatter Theoriebehauptung.
3. **Ehrlicher Umgang mit Grenzen:**  
   - robust: `negative ≈ abs > positive`
   - nicht gezeigt: `negative > abs`
   - Geometrieprüfung steht als nächster expliziter Schritt noch aus.

**Vorläufiges Urteil.**  
Das Primeon-Paper ist **nicht klar weiter als unser Projekt**, sondern **anders gereift**:
- stärker in theoretischer Verpackung und Framework-Kohärenz,
- schwächer in adversarialer Testhärtung und belastbarer Zwischenabsicherung.

**Interne Schlussfolgerung.**  
Für den Vergleich gilt:
- Das Primeon-Paper ist als konzeptioneller Nachbar interessant,
- aber kein Grund, unser Projekt als „hinterher“ zu lesen.
- Unser Projekt ist derzeit näher an einer **ehrlich getesteten Brückenhypothese**,
  während das Primeon-Paper näher an einem **ambitionierten, aber noch offenen Framework-Narrativ** liegt.

**Konsequenz für die eigene Arbeit.**  
Nicht rhetorisch aufholen wollen, sondern den eigenen Vorteil ausbauen:
- robuste Geometrieprüfung,
- Metrik-/Dimensions- und Geodäsietests,
- weitere defensive Absicherung der Brücke gegen triviale oder rein graphische Artefakte.


### Was wir aus dem Primeon-Paper konstruktiv übernehmen

Das Primeon-Paper wird **nicht** als überlegene oder bereits weiter abgeschlossene Theorie gelesen, sondern als konzeptioneller Nachbar mit einigen nützlichen Arbeitsbausteinen.

**Konstruktiv übernehmbar sind vor allem drei Punkte:**

1. **Saubere Regime-Trennung.**  
   Die Unterscheidung zwischen
   - einem makroskopischen, langwelligen geometrischen/gravitationsnahen Regime und
   - einem phasenkohärenten, quantennahen Regime

   ist auch für unser Projekt hilfreich. Sie passt gut zur Idee, dass dieselbe tiefere Relations-/Interferenzstruktur je nach Auflösung unterschiedlich gelesen werden kann.

2. **Explizite technische Meilensteine.**  
   Als projektinterne Checkliste sinnvoll übernehmbar sind die Fragen:
   - Wie wird eine effektive Metrik wirklich hergeleitet?
   - Wie entsteht ein effektives `G` bzw. eine makroskopische Kopplung?
   - Gibt es einen Regimebereich, in dem Standard-GR-Lösungen oder klare Näherungen recoverbar werden?
   - Welche abweichenden Vorhersagen wären später testbar?

   Diese Punkte sind auch für unsere Brücke gute Reifekriterien.

3. **Minimal-worked-example-Denke.**  
   Nützlich ist die methodische Haltung:
   - erst ein kleiner, harter Minimalfall,
   - dann erst größerer theoretischer Anspruch.

   Für uns spricht das dafür, Geometrie-/Metriktests zunächst in kleinen, klar interpretierbaren Settings aufzubauen, bevor eine weitergehende gravitative Sprache verwendet wird.

**Nicht übernommen wird:**
- der Primeon-spezifische Unterbau (`p-space`, prime-indexed modes, stationäre Resonanz als Framework-Kern),
- die konkrete Metriksetzung als eigener Projektkern,
- oder der Eindruck, dass dort bereits ein abgeschlossener Durchstich zur emergenten Gravitation vorliegt.

**Interne Schlussfolgerung.**  
Das Primeon-Paper ist für uns weniger als Vorbild einer fertigen Theorie relevant, sondern eher als Erinnerung an drei Dinge:
- Regime sauber trennen,
- Reifekriterien explizit benennen,
- Minimalfälle zuerst hart machen.

Das ist konstruktiv nutzbar, ohne unseren eigenen Ansatz zu verwässern.


### Erster Befund des Minimalmodells der Brückenphysik

Das Minimalmodell `bridge_minimal_model_v1` läuft erfolgreich und liefert erstmals einen kleinen, aber konsistenten physikalischen Brückenbefund.

**Makroregime (`macro`).**  
Für die signalhaltigen Fälle `k0` und `theta_0.03` ergibt sich:

- `negative` und `abs` verhalten sich im Minimalmodell praktisch gleich,
- beide zeigen
  - mittlere Strukturstabilität,
  - kleine, aber nichtverschwindende Phasenwirkung,
  - und maximale geometrische Lesbarkeit im verwendeten Surrogat-Score.

Konkret:
- `negative`: `stability ≈ 0.56`, `phase_influence ≈ 0.0123`, `geometry_readability = 1.0000`
- `abs`: `stability ≈ 0.55`, `phase_influence ≈ 0.0123`, `geometry_readability = 1.0000`

Für `positive` ergibt sich dagegen systematisch:
- geringere Strukturstabilität bzw. schwächerer Brückenzustand,
- verschwindende Phasenwirkung (`phase_influence = 0.0000`),
- reduzierte geometrische Lesbarkeit (`geometry_readability = 0.7000`).

Dasselbe Muster erscheint auch für `n1a_alpha`, wobei das Minimalmodell diesen Fall glatter und großzügiger liest als die strengeren N1-Launchability-/Shell-Logiken.

**Interne Arbeitslesart.**  
Das Minimalmodell reproduziert damit erstmals in expliziter Brückenform die bereits bekannte Oberblockstruktur:

- `negative ≈ abs > positive`

und legt zusätzlich nahe:
- `A` kann im Makroregime sinnvoll als primärer geometrischer Proxy gelesen werden,
- `theta` wirkt in `negative/abs` klein, aber nicht null,
- `positive` erscheint dagegen als deutlich schwächerer Brückenträger mit praktisch verschwindender Phasenwirkung.

**Wichtiger Vorbehalt.**  
Die aktuelle `geometry_readability` ist noch ein zusammengesetzter Surrogat-Score und **kein Nachweis metrischer Geometrie**. Der Block zeigt daher noch keine „fertige Geometrie“, sondern einen **geometrie-kompatiblen Brückenzustand**.

**Konsequenz.**  
Das Minimalmodell rechtfertigt nun den nächsten Schritt:
- explizite Metrik-/Geometrietests auf `d_eff`
- insbesondere:
  - Dreiecksungleichung,
  - geodätische Konsistenz,
  - Dimensionsmarker,
  - Benchmark-Vergleich gegen triviale Referenzgraphen.

**Vorläufiges Fazit.**  
Mit `bridge_minimal_model_v1` liegt erstmals ein arbeitsfähiges kleines Physikmodell der Brücke vor, das die bekannte Oberblockstruktur nicht nur numerisch reproduziert, sondern als Unterschied im Brückenzustand selbst lesbar macht.

