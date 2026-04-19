# debroglie_matter_signature_io_v1

## 1. Ziel

Diese I/O-Spezifikation legt fest, welche Inputs der Explorationsblock für materialspezifische de-Broglie-Signaturen benötigt, welche internen Zustandsgrößen erzeugt werden und welche testbaren Outputs daraus folgen müssen.

`debroglie_matter_signature_io_v1` dient dazu, die Signaturidee der Brücke in eine klar strukturierte Eingabe-/Ausgabeform zu überführen:

- atomare Spezies unter definierten thermodynamischen Bedingungen
- de-Broglie-bezogene Grundgrößen
- Signatur-Surrogate
- `tau`-Fenstervergleich
- Test auf Massen- vs. Materiesensitivität

Leitfrage:

> Lassen sich aus de-Broglie-bezogenen Materiedaten atomarer Spezies unter klar definierten Bedingungen systematische Signaturkandidaten für eine struktur-sensitive Brückenantwort konstruieren?

---

## 2. Input-Schicht

### 2.1 Pflicht-Inputs

`DebroglieMatterSignatureInput` enthält mindestens:

- `run_id`
- `species_list`
- `conditions`
  - `temperature_C`
  - `pressure_mbar`
  - `volume_m3`
- `model_assumptions`
  - `species_mode`
  - `gas_model`
  - `velocity_model`
  - `frequency_mode`
  - `density_mode`
- `tau_grid`
- `constants`
  - `planck_constant`
  - `boltzmann_constant`
  - `avogadro_constant`
  - `atomic_mass_unit`
- optionale `species_data`
  - Name
  - Symbol
  - atomare Masse
  - Override-Werte

### 2.2 Minimaler Default-Input

Für erste Läufe soll mit einem kleinen Standardset gearbeitet werden:

- `species_list = {hydrogen, sodium, carbon, nitrogen, sulfur, phosphorus}`
- `temperature_C = 20.0`
- `pressure_mbar = 1013.0`
- `volume_m3 = 1.0`
- `species_mode = atomic_species`
- `gas_model = ideal_gas`
- `velocity_model = rms`
- `frequency_mode = kinetic_energy_based`

### 2.3 Kleine Sweep-Inputs

Der Block soll zusätzlich kleine kontrollierte Sweeps unterstützen:

- alternatives `velocity_model`
- alternatives `frequency_mode`
- kleine Variation des `tau_grid`

Wichtig:
Der erste Block soll klein und diszipliniert bleiben.

---

## 3. Interne Zustandsgrößen

### 3.1 Thermodynamische Grundgrößen

- `temperature_K`
- `pressure_Pa`
- `volume_m3`
- `number_density`
- `particle_count`

### 3.2 Materiewellen-Grundgrößen

Für jede Spezies:

- `mass_kg`
- `velocity`
- `momentum`
- `lambda_db`
- `k`
- optional `frequency`
- optional `omega`
- optional `energy`

### 3.3 Signatur-Surrogate

Für jede Spezies:

- `length_scale_score`
- `frequency_score`
- `occupancy_score`
- `energy_score`
- `dispersion_score` optional
- `signature_score`

### 3.4 `tau`-Antwortgrößen

Für jede Spezies und jedes `tau`:

- `tau_response_score`
- `tau_alignment_score`
- `tau_window_label`
- `resonance_candidate_flag` optional

---

## 4. Verarbeitungsschritte

### Schritt 1: Input Normalization

- Vollständigkeit der Pflicht-Inputs prüfen
- Einheitensystem konsistent machen
- Stoffdaten validieren
- `tau_grid` prüfen

### Schritt 2: Stoffdaten laden

- atomare Masse pro Spezies laden oder überschreiben
- Namens- und Symbolkonsistenz prüfen

### Schritt 3: Thermodynamischen Zustand berechnen

- Temperatur in Kelvin
- Druck in Pascal
- Teilchendichte
- Teilchenzahl pro `m^3`

### Schritt 4: Materiewellen-Grundgrößen berechnen

- charakteristische Geschwindigkeit
- Impuls
- de-Broglie-Wellenlänge
- Wellenzahl
- optionale Frequenz-/Energieskalen

### Schritt 5: Signatur-Surrogate bilden

- Längenskalen-Surrogat
- Frequenz-Surrogat
- Besetzungs-Surrogat
- Energie-Surrogat
- kombinierte Signaturgröße

### Schritt 6: `tau`-Antwort berechnen

- mehrere `tau`-Fenster vergleichen
- Antwortstärke und Differenzierung bestimmen

### Schritt 7: Massen- vs. Materiesensitivität vergleichen

- einfache Massenordnung bestimmen
- Signaturordnung bestimmen
- Differenzen und nichttriviale Abweichungen markieren

### Schritt 8: Readout und Claims erzeugen

- Resultate strukturieren
- Plausible Resonanzfenster-Kandidaten markieren
- dokumentieren, ob nur Massenskalierung oder materiesensitive Unterschiede sichtbar werden

---

## 5. Output-Schicht

`DebroglieMatterSignatureOutput` enthält mindestens:

- `run_id`
- `conditions`
- `model_assumptions`
- `tau_grid`
- `species_results`
  - `species`
  - `mass_kg`
  - `velocity`
  - `momentum`
  - `lambda_db`
  - `k`
  - optional `frequency`
  - optional `energy`
  - `number_density`
  - `signature_surrogates`
  - `tau_response`
- `comparisons`
  - `mass_only_ordering`
  - `signature_ordering`
  - `difference_flags`
- `claim_readout`
- `testable_claims_ready`

---

## 6. Pflicht-Diagnostiken

### 6.1 `length_scale_score`

Wie stark unterscheidet sich die de-Broglie-Längenskala zwischen den Spezies?

### 6.2 `frequency_score`

Wie stark unterscheiden sich Frequenz- oder Energieskalen?

### 6.3 `occupancy_score`

Wie relevant ist Teilchendichte oder Besetzung für die Signatur?

### 6.4 `signature_score`

Wie stark ist die kombinierte Signatur pro Spezies ausgeprägt?

### 6.5 `tau_response_score`

Wie reagiert eine Spezies relativ zu einem gegebenen `tau`-Fenster?

### 6.6 `matter_sensitive_delta`

Wie stark weicht die Signaturordnung von bloßer Massenordnung ab?

---

## 7. Pflicht-Dateioutputs

Der Runner schreibt mindestens:

- `debroglie_matter_signature_state.json`
- `debroglie_matter_signature_readout.md`
- `debroglie_matter_signature_scan.csv`
- `debroglie_matter_signature_claims.json`

Optional zusätzlich:

- `debroglie_matter_signature_tau_response.csv`
- `debroglie_matter_signature_summary.json`
- `debroglie_matter_signature_debug.json`

---

## 8. Minimaler Erfolg

Die I/O-Spezifikation ist gelungen, wenn sie ermöglicht:

1. atomare Spezies unter definierten Bedingungen sauber zu instanziieren
2. de-Broglie-bezogene Grundgrößen und Signatur-Surrogate explizit zu unterscheiden
3. verschiedene `tau`-Fenster systematisch zu vergleichen
4. Massen- vs. Materiesensitivität kontrolliert zu prüfen
5. direkte nächste Mechanik- oder Resonanztests daraus abzuleiten

---

## 9. Testbare Claims-Readiness

Die I/O-Schicht muss mindestens die Grundlage dafür liefern, folgende Fragen testbar zu machen:

- Lassen sich reproduzierbare materialspezifische de-Broglie-Signaturen konstruieren?
- Reagieren verschiedene Spezies relativ zu demselben `tau`-Fenster unterschiedlich?
- Sind Unterschiede bloße Massenskalierung oder gehen sie darüber hinaus?
- Gibt es Resonanzfenster-Kandidaten im defensiven Sinn?
- Welche Signatur-Surrogate tragen am meisten zur Differenzierung bei?

---

## 10. Minimaler Run-Plan

### Run A
- Spezies: Wasserstoff, Natrium, Kohlenstoff, Stickstoff, Schwefel, Phosphor
- Bedingungen: `20 °C`, `1013 mbar`, `1 m^3`
- Modell: `rms`, `kinetic_energy_based`

### Run B
- wie Run A
- `velocity_model = mean`

### Run C
- wie Run A
- alternatives `frequency_mode`

---

## 11. Bottom line

`debroglie_matter_signature_io_v1` definiert die I/O-Schicht für den Übergang von

> materialspezifische Signaturidee formulieren

zu

> materialspezifische Signaturkandidaten testbar machen

Die operative Leitformel lautet:

> Wir prüfen, ob de-Broglie-bezogene Materiedaten atomarer Spezies unter definierten Bedingungen systematisch als Kandidaten einer struktur-sensitiven Brückenantwort lesbar werden.
