# debroglie_matter_signature_admissibility_readout_schema_v1

## 1. Ziel

Dieses Dokument definiert ein erstes **Readout-Schema** für die neue Zulässigkeitsschicht der materialsensitiven Signaturarchitektur.

Die Leitidee lautet:

> Heisenberg-, Pauli- und Lorentz-Filter sollen nicht nur als abstrakte Notizen existieren, sondern künftig als standardisierte Bewertungssektion in Projekt-Readouts erscheinen.

Damit wird aus der bisherigen Filteridee ein operatives Werkzeug.

---

## 2. Ausgangslage

Mit den Dokumenten

- `debroglie_matter_signature_admissibility_filters_v1`
- `debroglie_matter_signature_heisenberg_filter_v1`
- `debroglie_matter_signature_pauli_filter_v1`
- `debroglie_matter_signature_lorentz_filter_v1`

steht nun eine Zulässigkeits-Trias bereit.

Was noch fehlt, ist eine standardisierte Form, wie diese Filter in künftigen Readouts auftauchen sollen.

---

## 3. Grundlogik des Schemas

Jeder künftig relevante Readout kann neben

- Run-Kontext
- Ordnungen
- Deltas
- Claims

zusätzlich einen eigenen Block erhalten:

## X. Zulässigkeits- / Konsistenzsektion

Dieser Block beantwortet knapp:

- Ist der Befund physikalisch **zulässig**, **offen** oder **problematisch**?
- Welche Filter greifen?
- Welche Warnflags gibt es?
- Wie wirkt sich das auf die Interpretation aus?

---

## 4. Standardstruktur im Readout

Die Zulässigkeitssektion soll im Minimalfall folgende Unterblöcke enthalten:

### 4.1 Heisenberg
- `heisenberg_status`
- optionale Flags:
  - `localization_warning`
  - `over_sharp_state_flag`

### 4.2 Pauli
- `pauli_status`
- optionale Flags:
  - `occupation_consistent`
  - `forbidden_configuration_flag`

### 4.3 Lorentz / Relativität
- `lorentz_status`
- optionale Flags:
  - `preferred_frame_warning`
  - `simultaneity_assumption_warning`
  - `causality_warning`

### 4.4 Gesamturteil
- `admissibility_overall`
- kurze verbale Einordnung

---

## 5. Standardwerte

Für die erste Fassung genügt eine einfache Statuslogik:

### Statuswerte
- `consistent`
- `open`
- `warning`
- `problematic`

### Gesamtwert
- `admissible`
- `partly_admissible`
- `not_admissible`

---

## 6. Beispielblock für künftige Readouts

```text
## X. Zulässigkeits- / Konsistenzbewertung

- **heisenberg_status:** open
- **pauli_status:** consistent
- **lorentz_status:** open
- **localization_warning:** false
- **forbidden_configuration_flag:** false
- **preferred_frame_warning:** false
- **causality_warning:** false
- **admissibility_overall:** partly_admissible

Kurzlesart:

> Der Befund ist signaturseitig interessant und zeigt keine offensichtliche Pauli-Verletzung.
> Die Heisenberg- und Lorentz-Konsistenz sind noch nicht vollständig ausgearbeitet und bleiben als offene Prüfpunkte markiert.
```

---

## 7. Interpretationslogik

### Fall A: `admissible`
- keine offensichtlichen Konflikte
- Kandidat bleibt stark im Spiel

### Fall B: `partly_admissible`
- Befund bleibt interessant
- aber wesentliche Konsistenzfragen sind noch offen
- Kandidat nur mit Warnschild

### Fall C: `not_admissible`
- mindestens ein harter Filter schlägt problematisch an
- Befund wird trotz schöner Signatur abgewertet oder aussortiert

---

## 8. Minimalregeln für die Vergabe

### Heisenberg
- `consistent`, wenn keine überharte Lokalisierung implizit ist
- `open`, wenn Zustandsbreite nicht klar genug formuliert ist
- `problematic`, wenn der Befund nur punktförmig sinnvoll erscheint

### Pauli
- `consistent`, wenn Strukturlesart mit zulässiger Besetzung vereinbar ist
- `open`, wenn die Konfigurationslogik noch zu grob bleibt
- `problematic`, wenn besetzungswidrige oder inkonsistente Strukturannahmen nötig wären

### Lorentz
- `consistent`, wenn keine offensichtliche relativistische Kollision vorliegt
- `open`, wenn die Kinematik noch nicht ausgearbeitet ist
- `problematic`, wenn bevorzugte absolute Rahmen, Instantan-Kopplung oder Gleichzeitigkeit stillschweigend vorausgesetzt werden

---

## 9. Verhältnis zu Signaturwert und Robustheit

Wichtig ist die klare Trennung:

- **Signaturwert** beschreibt, wie interessant, lesbar und materialsensitiv der Befund ist
- **Zulässigkeit** beschreibt, ob er physikalisch als Kandidat stehen bleiben darf

Ein Befund kann also sein:

- signaturseitig stark
- aber zulässigkeitsseitig offen oder problematisch

Diese Trennung soll künftig explizit sichtbar bleiben.

---

## 10. Erste Empfehlung für bestehende und kommende Blöcke

Das Schema kann künftig besonders sinnvoll angewendet werden auf:

- Isotopen-Blöcke
- Strukturachsen-Blöcke
- Reaktions- oder Übergangsblock-Ideen
- Mechanikskizzen zur Brücke
- spätere Lokalisierungs- und Signaturraumdiskussionen

Für frühe Readouts reicht zunächst oft:

- ein kurzer Statussatz
- ein paar Flags
- ein Gesamturteil

Das ist schon genug, um die wissenschaftliche Disziplin sichtbar zu erhöhen.

---

## 11. Projektinterne Leitformel

Die wichtigste interne Formel lautet:

> Ein Befund zählt künftig nicht nur danach, wie schön er aussieht, sondern auch danach, wie sauber er die Zulässigkeitsfilter überlebt.

Oder knapper:

> Nicht nur interessant — auch readoutfähig erlaubt.

---

## 12. Bottom line

`debroglie_matter_signature_admissibility_readout_schema_v1` definiert die erste operative Form, in der Heisenberg-, Pauli- und Lorentz-Filter künftig in Projekt-Readouts sichtbar gemacht werden können.

Die operative Leitformel lautet:

> Jeder starke Befund braucht künftig auch einen kurzen Zulässigkeitsausweis.

Oder noch knapper:

> Schöne Befunde bekommen jetzt ihren physikalischen TÜV.
