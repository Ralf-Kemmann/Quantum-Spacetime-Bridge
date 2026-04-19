# debroglie_matter_signature_qc_valence_tests_v1

## 1. Direkt aus `debroglie_matter_signature_qc_valence_extension_v1` folgende Claims

### Claim QCV1
Die Valenzelektronenzahl liefert als atomnahe Strukturachse eine von der bisherigen Wellenordnung unterscheidbare Reorganisation.

### Claim QCV2
Die QC-Valenz-Schicht ist physikalisch interpretierbar und nicht bloß eine numerische Zusatzsortierung.

### Claim QCV3
Die Valenzschicht wirkt anders als die Ionisierungsenergie-Schicht, also eher strukturgebend als bloß stärkegebend.

### Claim QCV4
Die kombinierte Signatur aus Wellen- und Valenzschicht ist informationsreicher als die reine Wellenordnung.

### Claim QCV5
Die Valenzelektronenzahl ist ein sinnvoller erster Minimaldeskriptor, auf dem später Schalen- und Subschalenstruktur aufbauen können.

---

## 2. Unmittelbare Minimalerwartung

Für den ersten QC-Valenz-Block ist zunächst zu erwarten:

- Spezies mit gleicher oder ähnlicher Valenzelektronenzahl können zusammenrücken
- H und Na könnten sich annähern, da beide eine Valenzelektronenzahl von 1 tragen
- N und P könnten sich annähern, da beide 5 Valenzelektronen tragen
- S könnte wegen 6 Valenzelektronen eine eigene Stellung einnehmen
- die Reorganisation sollte anders aussehen als bei Ionisierungsenergie und VDW

Diese Erwartung ist keine Bestätigung, sondern ein Orientierungshorizont.

---

## 3. Pflichttests

### 3.1 Wellen- vs. Valenzordnung

Vergleich von:

- `wave_signature_ordering`
- `combined_signature_ordering`

Leitfrage:

> Verändert die Valenzelektronenzahl die bisherige Wellenordnung überhaupt?

### 3.2 Delta relativ zur Massenordnung

Vergleich von:

- `matter_sensitive_delta_wave`
- `matter_sensitive_delta_qc_valence`

Leitfrage:

> Wird die materiesensitive Reorganisation durch die Valenzschicht sichtbar anders?

### 3.3 Vergleich mit Ionisierungsenergie

Vergleich von:

- QC-Lauf mit `ionization_score`
- QC-Valenz-Lauf mit `valence_score`

Leitfrage:

> Wirkt die Valenzzahl eher als Strukturgeber und die Ionisierungsenergie eher als Stärkegeber?

### 3.4 Gruppierungsverhalten

Prüfen:

- ob Spezies mit gleicher oder ähnlicher Valenzelektronenzahl im Signaturraum näher zusammenrücken
- ob dieses Verhalten physikalisch lesbar ist

Leitfrage:

> Liefert die Valenzschicht eine interpretierbare Strukturierung oder nur eine andere Reihenfolge?

---

## 4. Weiterführende Tests

### 4.1 Kombination von Stärke- und Strukturachse

Später prüfen:

- `ionization_score`
- `valence_score`
- gemeinsame QC-Signatur

Leitfrage:

> Ergänzen sich Stärke- und Strukturachse sinnvoll?

### 4.2 Shell Closure als nächster Ausbau

Wenn die Valenzzahl trägt:

- offene vs. geschlossene Schale ergänzen

Leitfrage:

> Verbessert ein Closure-Deskriptor die Strukturlesbarkeit?

### 4.3 Hauptschalenniveau

Danach prüfen:

- `shell_level_score`

Leitfrage:

> Trägt die Lage der Valenzschale zusätzliche physikalische Struktur?

---

## 5. Entscheidungslogik

### Unterstützt

Der Block gilt als unterstützt, wenn:

- die Valenzelektronenzahl die Wellenordnung sichtbar reorganisiert
- diese Reorganisation physikalisch interpretierbar ist
- und sie sich sinnvoll von der Ionisierungsenergie-Achse unterscheidet

### Teilweise unterstützt

Der Block gilt als teilweise unterstützt, wenn:

- eine Reorganisation sichtbar ist
- diese aber schwach bleibt oder stark mit der Wellenordnung korreliert
- oder die physikalische Interpretierbarkeit noch unklar bleibt

### Nicht unterstützt

Der Block gilt als nicht unterstützt, wenn:

- die Valenzelektronenzahl praktisch keine zusätzliche Struktur erzeugt
- oder nur eine triviale Re-Sortierung ohne interpretierbaren Mehrwert liefert

---

## 6. Arbeitsfrage

Die zentrale Frage dieses Blocks lautet:

> Ist die Zahl der Valenzelektronen bereits ein brauchbarer atomarer Strukturdeskriptor für eine materialsensitive Signaturarchitektur?

Genau diese Frage entscheidet, ob der Weg zur Schalen- und Subschalenstruktur weiter ausgebaut werden sollte.

---

## 7. Bottom line

`debroglie_matter_signature_qc_valence_tests_v1` dient dazu, die Valenzelektronenzahl als ersten atomnahen Strukturgeber gegen die bisherige Wellenordnung und gegen die Ionisierungsenergie-Achse laufen zu lassen.

Die operative Leitformel lautet:

> Erst testen wir, ob die Valenzelektronenzahl als minimaler Strukturdeskriptor trägt; erst dann bauen wir Schalen- und Subschalenstruktur darauf auf.
