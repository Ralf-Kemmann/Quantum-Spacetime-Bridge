# debroglie_matter_signature_admissibility_filters_v1

## 1. Ziel

Dieses Dokument definiert eine neue Testschicht für die materialsensitive Signaturarchitektur:
**Zulässigkeits- bzw. Konsistenzfilter**.

Die bisherige Projektarbeit hat vor allem untersucht,

- ob Signaturachsen Ordnung reorganisieren,
- ob Wellen- und Strukturanteil trennbar sind,
- ob Befunde robust und lesbar bleiben.

Der nächste Reifeschritt lautet nun:

> Nicht nur prüfen, ob ein Befund interessant aussieht, sondern ob er als physikalischer Zustand oder Mechanismuskandidat überhaupt **zulässig** ist.

---

## 2. Warum Zulässigkeitsfilter nötig sind

Je stärker das Projekt in Richtung eines grundlegenden Mechanismus geht, desto weniger genügt es, bloß schöne numerische Strukturen zu finden.

Denn ein Befund kann zugleich sein:

- numerisch sauber,
- interpretierbar,
- robust,

und trotzdem

- physikalisch unzulässig,
- zu stark idealisiert,
- oder mit Grundbedingungen bekannter Physik unvereinbar.

Deshalb wird eine zweite Bewertungsachse nötig:

### Ebene 1
**Signatur- und Reorganisationswert**
- sichtbar?
- robust?
- materialsensitiv?
- lesbar?

### Ebene 2
**Physikalische Zulässigkeit**
- quantenmechanisch zulässig?
- strukturell realisierbar?
- relativistisch kompatibel?
- nicht bloß mathematisch hübsch?

---

## 3. Projektlogik

Die Projektlinie bleibt:

> Wir bauen keine neue Physik gegen die bekannte Physik.

Sondern:

> Wir suchen einen tieferliegenden mechanistischen Rahmen, der erklären kann, warum die bekannten Regeln und Gesetze als stabile Organisationsregeln erscheinen.

Daraus folgt unmittelbar:

- QM muss respektiert werden
- RT muss respektiert werden
- chemische Struktur muss respektiert werden
- numerische Befunde dürfen nicht gegen diese Grundbedingungen ausgespielt werden

Zulässigkeitsfilter sind deshalb keine Zusatzkosmetik, sondern Teil der wissenschaftlichen Selbstdisziplin des Projekts.

---

## 4. Erste Filterklassen

### 4.1 Heisenberg-Konsistenz

**Leitidee:**
Ein angeblicher Zustand oder Mechanismuskandidat darf keine unrealistische gleichzeitige Schärfe von Ort, Impuls oder verwandten Zustandsgrößen voraussetzen.

Projektinterne Lesart:

- Lokalisierung darf nicht klassisch-punktförmig idealisiert werden
- Wellenpaketbreite und Impulsstruktur müssen konsistent bleiben
- stark lokalisierte oder „harte“ Zustände brauchen besondere Vorsicht

Arbeitsfrage:

> Ist der angenommene Zustand mit einer endlichen quantenmechanischen Unschärfestruktur überhaupt plausibel vereinbar?

Mögliche Flags:
- `heisenberg_consistent`
- `localization_warning`
- `over_sharp_state_flag`

### 4.2 Pauli- / Besetzungs-Konsistenz

**Leitidee:**
Innere Strukturzustände dürfen nicht stillschweigend Elektronenkonfigurationen, Besetzungen oder Symmetrien voraussetzen, die fermionisch unzulässig sind.

Projektinterne Lesart:

- Elektronenkonfiguration ist keine freie Dekoration
- Valenz- und Strukturdeskriptoren müssen zu einer zulässigen Besetzungslogik passen
- schöne, aber besetzungswidrige Zustände sind auszusortieren

Arbeitsfrage:

> Ist die angenommene innere Struktur fermionisch und konfigurationsseitig überhaupt zulässig?

Mögliche Flags:
- `pauli_consistent`
- `occupation_consistent`
- `forbidden_configuration_flag`

### 4.3 Chemisch-strukturelle Realisierbarkeit

**Leitidee:**
Nicht jede numerisch beschreibbare Struktur ist chemisch oder atomar als stabiler oder wenigstens plausibler Zustand sinnvoll.

Projektinterne Lesart:

- Strukturfilter brauchen Bezug zu realisierbaren Zuständen
- metastabile, instabile und unrealistische Zustände sollten unterscheidbar sein
- chemische Lesbarkeit bleibt wichtig

Arbeitsfrage:

> Ist der betrachtete Zustand chemisch oder atomar wenigstens als Kandidat plausibel, oder nur ein numerisches Artefakt?

Mögliche Flags:
- `chemically_plausible`
- `state_realizability_flag`
- `metastable_candidate`
- `artifact_warning`

### 4.4 Perspektivisch: Lorentz-/Relativitäts-Konsistenz

**Leitidee:**
Ein universeller Mechanismus darf die relativistische Transformationsstruktur nicht verletzen.

Wichtig:
Diese Filterklasse ist zentral, aber für den nächsten Schritt noch eher rahmend als sofort voll operational.

Projektinterne Lesart:

- der Mechanismus muss perspektivisch Lorentz-kompatibel formulierbar sein
- keine stillschweigende Bevorzugung verbotener absoluter Strukturen
- Zustands- und Kopplungsbilder dürfen nicht offensichtlich relativitätswidrig werden

Arbeitsfrage:

> Ist der vorgeschlagene Mechanismuskandidat wenigstens als relativistisch konsistenter Kandidat denkbar?

Mögliche Flags:
- `relativity_consistent_candidate`
- `lorentz_compatibility_open`
- `preferred_frame_warning`

---

## 5. Wie die Filter wirken sollen

Die Filter sollen nicht primär „harte mathematische Verbote“ in jeder frühen Phase liefern, sondern zunächst eine disziplinierte Einordnung.

Ein Befund kann dann z. B. sein:

### Fall A
- interessant
- robust
- **zulässig**

→ starker Kandidat

### Fall B
- interessant
- robust
- **Zulässigkeit offen**

→ explorativer Kandidat, aber mit Warnschild

### Fall C
- interessant
- robust
- **klar unzulässig**

→ auszusortieren, trotz schöner Ordnung

Das ist der entscheidende Punkt:

> Nicht jeder hübsche Befund darf in der Kandidatenliste bleiben.

---

## 6. Projektinterne Bewertungsmatrix

Künftig kann jeder Block entlang zweier Achsen gelesen werden:

### Achse I: Signaturwert
- Reorganisation
- Materialsensitivität
- Lesbarkeit
- Robustheit

### Achse II: Zulässigkeit
- Heisenberg-Konsistenz
- Pauli-/Besetzungs-Konsistenz
- chemische Realisierbarkeit
- perspektivisch Lorentz-Kompatibilität

So entsteht eine sauberere Vierfelderlogik:

| Signaturwert | Zulässigkeit | Lesart |
|---|---|---|
| hoch | hoch | starker Kandidat |
| hoch | offen | explorativer Kandidat |
| hoch | niedrig | schöner, aber auszusortierender Befund |
| niedrig | hoch | physikalisch sauber, aber signaturseitig unergiebig |

---

## 7. Warum das wissenschaftlich wichtig ist

Diese Filter verschärfen das Projekt in genau der richtigen Richtung.

Sie zeigen:

- wir sammeln nicht blind Effekte
- wir lassen uns nicht von schönen Mustern verführen
- wir prüfen auf physikalische Erlaubtheit
- wir wollen Mechanismus, keine numerische Mythologie

Das stärkt sowohl die interne Projektlogik als auch die Außenwirkung.

Projektinterne Arbeitsformel:

> Nicht nur interessant — auch erlaubt.

---

## 8. Erste operative Umsetzung

### Kurzfristig
Zunächst als Bewertungs- und Dokumentationsschicht:

- pro Block kurze Zulässigkeitssektion
- offene Punkte explizit markieren
- Warnflags für problematische Zustände

### Mittelfristig
Teilweise Operationalisierung:

- einfache Heisenberg-Konsistenzchecks
- Konfigurations-/Besetzungschecks
- Plausibilitätskategorien für Zustände

### Langfristig
Mechanismennahe Konsistenzprüfung:

- relativistische Kompatibilität
- Transformationsverhalten
- Einbettung in eine allgemeinere Brückenmechanik

---

## 9. Verhältnis zu bisherigen Befunden

Die bisherigen Befunde bleiben wertvoll:

- H/D/T
- Carbon
- Strontium
- VDW
- Ionisierung
- Valenz
- Closure

Aber sie erhalten nun eine zusätzliche Ebene:

> Welche dieser Befunde bleiben Kandidaten, wenn wir sie gegen physikalische Zulässigkeitsbedingungen halten?

Damit wird aus einer reinen Signaturarchitektur schrittweise ein physikalisch gehärtetes Theorieprogramm.

---

## 10. Was diese Filter noch nicht leisten

Wichtig ist auch die Grenze:

Diese Notiz liefert noch keine vollständige, formal abgeschlossene Zulässigkeitstheorie.

Sie schafft zunächst:

- Sprache
- Struktur
- Prüflogik
- Dokumentationsdisziplin

Das genügt für den jetzigen Projektstand und ist genau die richtige nächste Ausbaustufe.

---

## 11. Bottom line

`debroglie_matter_signature_admissibility_filters_v1` definiert die nächste Reifeschicht des Projekts:

> von bloßer Signaturerkennung zu physikalisch zulässigen Mechanismuskandidaten.

Die operative Leitformel lautet:

> Schöne Befunde zählen nur dann wirklich, wenn sie auch mit den Grundbedingungen bekannter Physik verträglich bleiben.

Oder knapper:

> Nicht nur interessant — auch erlaubt.
