# debroglie_matter_signature_vdw_extension_v1

## 1. Ziel

Dieses Dokument definiert eine erste Erweiterung des Signaturblocks um eine van-der-Waals-Perspektive.

Die Erweiterung dient **nicht** dazu, sofort ein vollständig realistisches Stoffmodell zu erzwingen.  
Ihr Zweck ist zunächst viel bescheidener und methodisch sauberer:

> Es soll geprüft werden, ob ein nicht-ideales Stoffmodell überhaupt zusätzliche Differenzierung in die materialspezifische Brückensignatur hineinbringt.

Damit ist die van-der-Waals-Erweiterung vorerst ein **Explorationshebel**, kein Abschlussmodell.

---

## 2. Motivation

Die erste Serie `Run A/B/C` hat einen klaren Zwischenstand geliefert:

- die Signaturidee ist operationalisierbar
- die resultierende Ordnung ist robust gegenüber kleinen Modellvarianten
- die Differenzierung wird jedoch in der aktuellen Minimalarchitektur fast vollständig durch die de-Broglie-Längenskala getragen
- `energy_score` und `occupancy_score` tragen unter idealgasartigen Standardannahmen praktisch keine zusätzliche Trennung
- `tau` ist in der aktuellen Form noch nicht stark aktiviert

Daraus folgt die methodische Frage:

> Kann ein realistischeres Stoffmodell zusätzliche materiesensitive Struktur freilegen, die im idealen Gasbild verborgen bleibt?

Genau dafür wird die van-der-Waals-Erweiterung eingeführt.

---

## 3. Methodische Vorsicht

Wichtig ist die Reihenfolge:

Wir wollen **nicht** sofort großen physikalischen Aufwand treiben, bevor überhaupt sichtbar ist, ob der Block auf eine nicht-ideale Erweiterung reagiert.

Die Leitregel lautet daher:

> Erst prüfen, ob überhaupt zusätzliche Struktur auftaucht.  
> Erst danach lohnt sich tiefere stoffphysikalische Ausarbeitung.

Das bedeutet:

- keine vorschnelle Vollrealismus-Forderung
- keine überladene Materialdatenbank im ersten Schritt
- keine Behauptung, dass van der Waals schon die gesuchte Brückenphysik liefert

Sondern nur:

> Testen, ob der Block über die reine de-Broglie-Längenskala hinaus zusätzliche materielle Achsen zu lesen beginnt.

---

## 4. Warum van der Waals?

Das ideale Gasmodell ist für den ersten Einstieg nützlich, macht aber unter gleichen Bedingungen viele Größen zu gleichförmig.

Insbesondere bei festem `T`, `p` und `V` gilt im idealen Gas:

- Teilchendichte ist weitgehend gleichartig behandelt
- thermische Energie pro Teilchen ist weitgehend gleichartig behandelt
- damit kollabieren mehrere Signatur-Surrogate auf triviale oder nahezu triviale Werte

Die van-der-Waals-Gleichung bringt zwei neue physikalische Hebel hinein:

\[
\left(p + a \frac{n^2}{V^2}\right)(V - nb) = nRT
\]

mit:

- `a` als Maß attraktiver Wechselwirkungsbeiträge
- `b` als Maß endlichen Eigen- bzw. Ausschlussvolumens

Dadurch kommt zusätzliche **stoffspezifische Materiecharakteristik** in das Modell.

Kurzformel:

> de Broglie liefert die Wellen-Skala, van der Waals liefert die Stoff-Skala.

---

## 5. Physikalische Lesart der Erweiterung

Die Erweiterung soll so gelesen werden:

- die de-Broglie-Signatur bleibt die materiewellenartige Seite
- die van-der-Waals-Parameter liefern zusätzliche information über reale stoffliche Trägerschaft
- beide zusammen ergeben eine reichere materialspezifische Signatur

Dann wäre die Brücke nicht nur sensitiv auf:

- Impuls / Wellenlänge / Wellenzahl

sondern zusätzlich auch auf:

- effektive Anziehungscharakteristik
- räumliche Verdrängung
- nicht-ideale materielle Präsenz im Volumen

Das ist genau die Art zweiter Achse, die im bisherigen Block noch fehlt.

---

## 6. Was die Erweiterung noch nicht leisten soll

Diese erste van-der-Waals-Erweiterung soll ausdrücklich **nicht**:

- alle realen Phasenverhältnisse korrekt abbilden
- automatisch jede gewählte Spezies unter STP vollständig realistisch modellieren
- komplexe Molekül-, Ionen- oder Kondensatphysik einführen
- bereits eine endgültige Materiesensitivität beweisen

Sie soll nur prüfen:

> Reagiert der Signaturblock überhaupt auf eine nicht-ideale Stofferweiterung?

Wenn die Antwort darauf nein ist, lohnt sich tieferer Aufwand vorerst nicht.  
Wenn die Antwort ja ist, öffnet sich ein neuer produktiver Arbeitsraum.

---

## 7. Neue mögliche Signatur-Surrogate

Die van-der-Waals-Erweiterung legt mindestens drei neue Kandidaten nahe.

### 7.1 `interaction_score`
Basis:
- van-der-Waals-Parameter `a`
- oder daraus abgeleitete Wechselwirkungsgröße

Lesart:
- Maß für attraktive stoffliche Wechselwirkung
- Kandidat für zusätzliche materielle Bindungscharakteristik

### 7.2 `excluded_volume_score`
Basis:
- van-der-Waals-Parameter `b`

Lesart:
- Maß für effektives Eigen- bzw. Ausschlussvolumen
- Kandidat für reale räumliche Trägerschaft

### 7.3 `vdw_signature_score`
Basis:
- einfache kombinierte Größe aus `a` und `b`
- optional zusammen mit Dichte-/Besetzungsgröße

Lesart:
- grober stoffphysikalischer Korrekturterm zur de-Broglie-Signatur

Wichtig:
Diese Größen sind zunächst **Zusatzsurrogate**, nicht Ersatz der bisherigen de-Broglie-Surrogate.

---

## 8. Erweiterte Signatur-Lesart

Mit der Erweiterung könnte die gesamte Brückensignatur in einer ersten Fassung aus zwei Schichten bestehen:

### 8.1 Wellen-Schicht
- `length_scale_score`
- `energy_score`
- später eventuell `frequency_score`

### 8.2 Stoff-Schicht
- `interaction_score`
- `excluded_volume_score`
- `vdw_signature_score`

Dann wäre eine zusammengesetzte Signatur denkbar wie:

- `signature_score_wave`
- `signature_score_vdw`
- optional `signature_score_combined`

Diese Struktur wäre methodisch sauberer als alles sofort in einen einzigen großen Topf zu werfen.

---

## 9. Erwartete Funktion der Erweiterung

Die van-der-Waals-Erweiterung ist dann gelungen, wenn mindestens eines der folgenden Dinge sichtbar wird:

- `occupancy_score` erhält zusätzliche stoffspezifische Struktur
- `interaction_score` oder `excluded_volume_score` differenzieren Spezies nichttrivial
- die kombinierte Signaturordnung weicht robuster von bloßer Massenordnung ab
- `tau`-Fenster reagieren in Verbindung mit der erweiterten Signatur differenzierter

Der Minimalgewinn wäre also:

> eine zweite materiesensitive Achse jenseits der reinen de-Broglie-Längenskala.

---

## 10. Vorsicht bei den Spezies

Im aktuellen Projektstadium soll diese Frage bewusst noch **nicht** mit voller Stoffrealismus-Härte ausgetragen werden.

Trotzdem muss klar bleiben:

- nicht jede atomare Spezies verhält sich unter denselben Alltagsbedingungen wie ein einfaches reales Gas
- van-der-Waals-Parameter setzen bereits eine bestimmte Modelllesart voraus
- die erste Erweiterung ist daher eher als formaler Testblock denn als fertiges Stoffmodell zu lesen

Saubere Lesart:

> Zunächst interessiert nicht perfekte Realistik, sondern ob eine nicht-ideale Stofferweiterung den Signaturraum überhaupt produktiv öffnet.

---

## 11. Minimaler Testplan

### Block VDW-A
- gleicher Grundblock wie Run A
- zusätzlich `interaction_score`, `excluded_volume_score`, `vdw_signature_score`

### Block VDW-B
- Vergleich ideal_gas vs. van_der_waals
- gleiche Spezies, gleiche Grundbedingungen

### Block VDW-C
- Vergleich der resultierenden Ordnungen:
  - Massenordnung
  - reine de-Broglie-Signaturordnung
  - erweiterte vdw-Signaturordnung

Leitfrage:

> Wird aus der aktuellen schmalen de-Broglie-Signatur durch die Stofferweiterung eine breitere materiesensitive Signatur?

---

## 12. Erste Arbeitshypothesen

### Hypothese V1
Das ideale Gasbild unterschätzt die materiespezifische Differenzierung der Signatur.

### Hypothese V2
van-der-Waals-Parameter liefern eine zusätzliche stoffsensitive Achse.

### Hypothese V3
Eine kombinierte de-Broglie- plus van-der-Waals-Signatur weicht stärker von bloßer Massenordnung ab als die bisherige Minimalarchitektur.

### Hypothese V4
Die Erweiterung lohnt sich nur dann weiter auszubauen, wenn im ersten VDW-Block überhaupt zusätzliche strukturierte Differenzierung sichtbar wird.

---

## 13. Nächster Schritt

Der nächste sinnvolle Schritt wäre eine kleine Ergänzung der bestehenden Architektur:

- `debroglie_matter_signature_vdw_io_v1.md`
- `debroglie_matter_signature_vdw_tests_v1.md`
- optionale neue Configs für ideal vs. van_der_waals
- danach erst eine Runner-Erweiterung

So bleibt die Doku-Kette sauber und der Ausbau kontrolliert.

---

## 14. Bottom line

Die zentrale Arbeitslesart dieses Dokuments lautet:

> Die van-der-Waals-Erweiterung ist kein vorweggenommener Vollrealismus, sondern ein gezielter Test darauf, ob eine nicht-ideale Stoffskala dem Signaturblock überhaupt zusätzliche materiesensitive Struktur jenseits der reinen de-Broglie-Längenskala eröffnet.

Oder knapper:

> Erst prüfen, ob die Stoff-Skala überhaupt etwas aufmacht — dann lohnt sich der größere Aufwand.
