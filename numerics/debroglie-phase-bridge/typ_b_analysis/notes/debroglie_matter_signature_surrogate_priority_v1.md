# debroglie_matter_signature_surrogate_priority_v1

## 1. Ziel

Dieses Dokument priorisiert die konkreten Signatur-Surrogate für den ersten Explorationsrunner zur materialspezifischen de-Broglie-Brücke.

Die Priorisierung soll verhindern, dass der erste Runner mit zu vielen Freiheitsgraden überladen wird. Ziel ist ein **kleiner, physikalisch lesbarer und technisch launchbarer Minimalblock**, der die Schlüsselfrage testet:

> Bleibt am Ende nur triviale Massenskalierung übrig, oder werden tatsächlich materialspezifische Signaturunterschiede sichtbar?

---

## 2. Priorisierungsprinzip

Die Surrogate werden nach drei Kriterien geordnet:

1. **physikalische Klarheit**
2. **rechnerische Einfachheit**
3. **Nutzen für die Unterscheidung von Massen- vs. Materiesensitivität**

Daraus ergeben sich drei Stufen:

- **Priorität 1:** sofort in den ersten Runner
- **Priorität 2:** früh danach, aber nicht im ersten Minimalwurf
- **Priorität 3:** spätere Ausbau- oder Verfeinerungsschicht

---

## 3. Priorität 1 — sofort in den ersten Runner

Diese Surrogate sollen im ersten Minimalblock verpflichtend enthalten sein.

### 3.1 `length_scale_score`

Basis:
- `lambda_db`
- alternativ äquivalent `k = 2*pi / lambda_db`

Begründung:
Dies ist der direkteste de-Broglie-Anker und damit die primäre materialspezifische Wellenlängenskala.

Arbeitslesart:
- charakteristische Materiewellenskala des Trägers
- erste physikalische Signaturskala

### 3.2 `energy_score`

Basis:
- thermische kinetische Energie pro Teilchen
- oder klar definierte charakteristische Energieskala

Begründung:
Neben der Längenskala wird eine zweite robuste physikalische Achse benötigt, die die dynamische Trägerskala erfasst. Energie ist hierfür im ersten Wurf stabiler und weniger interpretationsanfällig als Frequenz.

Arbeitslesart:
- charakteristische Bewegungs- oder Energieträgerskala der Spezies

### 3.3 `occupancy_score`

Basis:
- Teilchendichte pro `m^3`
- oder normierte Besetzungsgröße

Begründung:
Die Brückensignatur soll nicht bloß als Einteilchen-Charakteristik gelesen werden, sondern als coarse-grained materielle Trägerschaft im Raum. Dafür ist ein Besetzungsmaß nötig.

Arbeitslesart:
- materielle Präsenz bzw. Trägerbesetzung im gegebenen Volumen

### 3.4 `signature_score`

Basis:
- einfache normierte Kombination aus
  - `length_scale_score`
  - `energy_score`
  - `occupancy_score`

Begründung:
Es wird ein zusammengesetzter Minimalindikator benötigt, um eine gesamte materialspezifische Signatur zunächst grob, aber transparent lesbar zu machen.

Wichtig:
Im ersten Wurf keine komplizierte Gewichtungslogik.  
Lieber einfache, nachvollziehbare Normierung als frühe Blackbox.

Arbeitslesart:
- grober Gesamtkandidat der materialspezifischen Brückensignatur

---

## 4. Priorität 2 — früh danach, aber nicht im ersten Minimalwurf

Diese Größen sind wichtig, sollen aber erst nach dem ersten stabilen Basislauf explizit hinzukommen.

### 4.1 `tau_alignment_score`

Basis:
- Nähemaß oder Verhältnis zwischen `tau` und charakteristischer Signaturskala

Begründung:
Für die eigentliche Brückenfrage ist dies sehr wichtig.  
Es setzt aber voraus, dass die primären Signatur-Surrogate stabil laufen.

Arbeitslesart:
- Grad der Kompatibilität eines `tau`-Fensters mit einer materialspezifischen Signatur

### 4.2 `frequency_score`

Basis:
- aus Energienäherung
- oder aus `v / lambda_db`

Begründung:
Frequenz ist physikalisch reizvoll, aber in der aktuellen Projektphase noch interpretationsanfälliger als Energie. Daher früh, aber nicht im ersten Minimalwurf.

Arbeitslesart:
- mögliche Takt- oder Antwortfrequenz der Signatur

### 4.3 `matter_sensitive_delta`

Basis:
- Differenz zwischen einfacher Massenordnung und Signaturordnung

Begründung:
Diese Größe ist entscheidend für die Auswertung der Leitfrage, ist aber keine primäre Signaturgröße, sondern eine Diagnostik.

Arbeitslesart:
- Maß dafür, wie stark sich die Signaturlesart von bloßer Massenskalierung entfernt

---

## 5. Priorität 3 — spätere Ausbau- und Verfeinerungsschicht

Diese Größen sind interessant, aber erst sinnvoll, wenn der erste Block stabil und interpretierbar läuft.

### 5.1 `dispersion_score`

Basis:
- Breite oder Streuung der Signaturverteilung

Begründung:
Physikalisch sinnvoll, aber für den ersten Runner zusätzlicher Freiheitsgrad ohne klaren Anfangsgewinn.

Arbeitslesart:
- Verteilungsbreite bzw. Streuungscharakter der Signatur

### 5.2 `composite_resonance_score`

Basis:
- kombinierte Funktion aus `tau`, Frequenz, Energie, Dichte oder weiteren Größen

Begründung:
Zu früh eingeführt würde diese Größe zu schnell Blackbox-Charakter bekommen.

Arbeitslesart:
- zusammengesetzter Resonanz- oder Antwortkandidat

### 5.3 `species_structure_modifier`

Basis:
- zusätzlicher materialspezifischer Korrekturterm jenseits einfacher atomarer Massen- und Thermogrößen

Begründung:
Im aktuellen Projektstadium noch zu offen. Erst muss gezeigt werden, dass die einfachen Größen überhaupt etwas tragen.

Arbeitslesart:
- spätere Verfeinerung materialspezifischer Besonderheiten

---

## 6. Empfohlene Minimalarchitektur für Run A

Für den ersten Runner sollen verpflichtend verwendet werden:

### Primäre Grundsurrogate
- `length_scale_score`
- `energy_score`
- `occupancy_score`

### Zusammengesetzter Surrogat-Kandidat
- `signature_score`

### Zusätzliche Auswertungsdiagnostik
- `tau_alignment_score` optional vorbereiten, aber nicht zwingend voll ausreizen
- `matter_sensitive_delta` im Readout ausweisen

Kurzlesart:

> Drei Grundsurrogate, ein zusammengesetzter Signaturkandidat und zwei Auswertungshebel genügen für den ersten belastbaren Minimalblock.

---

## 7. Physikalische Kurzsemantik

### `length_scale_score`
materielle Wellenlängensignatur

### `energy_score`
dynamische Trägerskala

### `occupancy_score`
coarse-grained materielle Präsenz im Volumen

### `signature_score`
grober Gesamtkandidat der materialspezifischen Brückensignatur

### `tau_alignment_score`
Kompatibilität eines Antwortfensters mit einer Signaturskala

### `matter_sensitive_delta`
Abweichung von bloßer Massenskalierung

---

## 8. Begründung der Priorität

Diese Priorisierung ist bewusst konservativ.

Sie soll verhindern, dass der erste Runner:

- zu viele Modellentscheidungen gleichzeitig enthält
- Frequenz- und Resonanzfragen zu früh überlädt
- oder durch zu viele zusammengesetzte Größen interpretativ unlesbar wird

Die Strategie lautet daher:

> Erst robuste physikalische Basissurrogate, dann Takt- und Resonanzverfeinerung, zuletzt komplexe Verteilungs- und Kompositgrößen.

---

## 9. Nächster Schritt

Auf Basis dieser Priorisierung kann der erste Runner mit klarer Scope-Begrenzung umgesetzt werden.

Empfohlene Reihenfolge:

1. Grundgrößen berechnen
2. `length_scale_score`, `energy_score`, `occupancy_score` bilden
3. `signature_score` konstruieren
4. `tau`-Fenstervergleich ergänzen
5. `matter_sensitive_delta` ausweisen
6. erst danach Frequenz- und Dispersionsschicht erweitern

---

## 10. Bottom line

Die zentrale Arbeitsformel dieses Dokuments lautet:

> Für den ersten Explorationsrunner sollen nur wenige, aber physikalisch klare Signatur-Surrogate priorisiert werden: Wellenlängenskala, Energieskala, Besetzungsmaß und ein transparenter kombinierter Signaturscore.

Oder knapper:

> Erst klare Basissurrogate, dann Resonanzverfeinerung.
