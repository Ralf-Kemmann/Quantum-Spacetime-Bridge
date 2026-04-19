# debroglie_matter_signature_tests_v1

## 1. Direkt aus `debroglie_matter_signature_resonance_test_v1` folgende Claims

### Claim DS1
Für die gewählten atomaren Spezies unter definierten Standardbedingungen lassen sich reproduzierbare de-Broglie-bezogene Signatur-Surrogate konstruieren.

### Claim DS2
Verschiedene Spezies zeigen relativ zu demselben `tau`-Fenster systematisch unterschiedliche Antwortprofile.

### Claim DS3
Mindestens ein Signatur-Surrogat liefert Unterschiede, die nicht vollständig auf triviale Massenskalierung reduzierbar sind.

### Claim DS4
Mindestens ein `tau`-Fenster erscheint als plausibler Antwortfenster- oder Resonanzkandidat im defensiven Sinn.

### Claim DS5
Die Signaturidee ist konkret genug, um als Brückeninput für `A`, `theta` oder `B_info` weiterverwendet zu werden.

---

## 2. Unmittelbare Minimalerwartung

Für den ersten Explorationsblock ist zunächst zu erwarten:

- alle Spezies unterscheiden sich mindestens trivial nach Masse
- de-Broglie-Längenskalen und Impulsgrößen liefern reproduzierbare Unterschiede
- die eigentliche Frage ist nicht, ob Unterschiede existieren, sondern ob sie über bloße Massenordnung hinausgehen
- `tau`-Antwort wird zunächst wahrscheinlich modell- und Fenster-abhängig sein
- einzelne Surrogate können stärker differenzieren als andere

Diese Minimalerwartung ist noch keine Bestätigung, sondern die Sollbruchkarte des Tests.

---

## 3. Pflichttests

### 3.1 Stoffdaten- und Einheitenkonsistenz

Prüfen:

- atomare Massen korrekt geladen
- Temperatur-, Druck- und Volumenumrechnung korrekt
- keine stillen Unit-Fehler

Leitfrage:

> Sind die Grunddaten sauber genug, damit spätere Unterschiede physikalisch interpretierbar sind?

### 3.2 Reproduzierbarkeit der Grundgrößen

Vergleich von:

- `mass_kg`
- `velocity`
- `momentum`
- `lambda_db`
- `k`
- optional `frequency`
- optional `energy`

Leitfrage:

> Entstehen stabile und nachvollziehbare de-Broglie-bezogene Grundgrößen pro Spezies?

### 3.3 Signatur-Surrogate

Vergleich von:

- `length_scale_score`
- `frequency_score`
- `occupancy_score`
- `energy_score`
- `signature_score`

Leitfrage:

> Welche Surrogate differenzieren Spezies am stärksten?

### 3.4 `tau`-Fenstervergleich

Vergleich pro Spezies und `tau`:

- `tau_response_score`
- `tau_alignment_score`
- Fensterlabels

Leitfrage:

> Reagieren verschiedene Spezies relativ zu denselben `tau`-Fenstern systematisch verschieden?

### 3.5 Massen- vs. Materiesensitivität

Vergleich von:

- einfacher Massenordnung
- Signaturordnung
- Abweichungsmaß / `matter_sensitive_delta`

Leitfrage:

> Kollabiert alles auf triviale Massenskalierung oder bleibt materiesensitive Struktur übrig?

---

## 4. Weiterführende Tests

### 4.1 Geschwindigkeitsmodell-Sensitivität

Vergleich von:

- `rms`
- `mean`
- optional `most_probable`

Leitfrage:

> Bleiben die Signaturmuster robust gegenüber vernünftigen thermischen Modellvarianten?

### 4.2 Frequenzmodus-Sensitivität

Vergleich von:

- `kinetic_energy_based`
- `omega_from_v_over_lambda`

Leitfrage:

> Hängt die materiesensitive Lesart stark an der Frequenzdefinition oder bleibt sie strukturell ähnlich?

### 4.3 Surrogat-Konsistenz

Prüfen:

- ob mehrere Surrogate dieselbe Ordnungsstruktur andeuten
- oder ob nur ein einzelnes Surrogat die Differenzierung trägt

Leitfrage:

> Ist die Signaturidee breit abgestützt oder an eine Einzelgröße geklammert?

---

## 5. Entscheidungslogik

### Unterstützt

Der Block gilt als unterstützt, wenn:

- reproduzierbare Signatur-Surrogate entstehen
- Spezies relativ zu denselben `tau`-Fenstern systematisch unterschiedlich reagieren
- mindestens ein nichttrivialer Unterschied über Massenskalierung hinaus bleibt
- und die Resultate robust genug für einen nächsten Brückenschritt sind

### Teilweise unterstützt

Der Block gilt als teilweise unterstützt, wenn:

- Unterschiede sichtbar, aber stark modellabhängig bleiben
- `tau`-Antwort nur schwach oder inkonsistent differenziert
- materiesensitive Abweichungen klein, aber konsistent sind

### Nicht unterstützt

Der Block gilt als nicht unterstützt, wenn:

- alle Resultate praktisch vollständig auf Massenskalierung kollabieren
- `tau` keine sinnvolle Fensterdifferenz erzeugt
- oder die Surrogatkonstruktion physikalisch zu unscharf bleibt

---

## 6. Arbeitsfrage

Die zentrale Frage dieses Blocks lautet:

> Lassen sich materialspezifische de-Broglie-Signaturen atomarer Spezies unter Standardbedingungen so operationalisieren, dass daraus mehr entsteht als eine verkleidete Massenskala?

Genau diese Frage entscheidet, ob die Signaturidee physikalisch weitergetragen werden kann.

---

## 7. Bottom line

`debroglie_matter_signature_tests_v1` dient dazu, die Signaturidee nicht nur begrifflich, sondern gegen klare Minimaltests laufen zu lassen.

Die operative Leitformel lautet:

> Wir prüfen, ob de-Broglie-bezogene Materiedaten atomarer Spezies systematische, `tau`-sensitive und nicht bloß massentriviale Kandidaten einer Brückenantwort erzeugen.
