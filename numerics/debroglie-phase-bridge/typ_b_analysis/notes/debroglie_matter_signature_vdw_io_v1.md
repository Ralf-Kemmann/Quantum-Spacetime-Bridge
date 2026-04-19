# debroglie_matter_signature_vdw_io_v1

## 1. Ziel

Diese I/O-Spezifikation definiert die Ein- und Ausgabeschicht für die van-der-Waals-Erweiterung des Materialsignatur-Blocks.

Sie dient dazu, die bisherige de-Broglie-basierte Signaturarchitektur um eine **nicht-ideale Stoffschicht** zu ergänzen, ohne den Block sofort zu einem Vollrealismus-Modell zu überladen.

Leitfrage:

> Erzeugt ein nicht-ideales Stoffmodell überhaupt zusätzliche materiesensitive Struktur jenseits der reinen de-Broglie-Längenskala?

---

## 2. Input-Schicht

### 2.1 Pflicht-Inputs

`DebroglieMatterSignatureVDWInput` enthält mindestens:

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
  - `vdw_mode`
- `tau_grid`
- `constants`
  - `planck_constant`
  - `boltzmann_constant`
  - `avogadro_constant`
  - `atomic_mass_unit`
  - optional `gas_constant`
- optionale `species_data`
  - Name
  - Symbol
  - atomare Masse
  - van-der-Waals-Parameter `a`
  - van-der-Waals-Parameter `b`
  - Override-Werte

### 2.2 Minimaler Default-Input

Für die erste VDW-Erweiterung soll bewusst auf dem bisherigen Standardkontext aufgesetzt werden:

- gleiche Speziesliste wie im Grundblock
- `temperature_C = 20.0`
- `pressure_mbar = 1013.0`
- `volume_m3 = 1.0`
- `gas_model = van_der_waals` oder `ideal_gas` zum Vergleich
- kleines `tau_grid`

### 2.3 Vergleichsmodus

Die I/O-Schicht soll explizit unterstützen:

- `ideal_gas`
- `van_der_waals`

damit idealisierter und erweiterter Signaturraum direkt gegeneinander gelesen werden können.

---

## 3. Interne Zustandsgrößen

### 3.1 Grundgrößen aus dem bisherigen Block

Für jede Spezies:

- `mass_kg`
- `velocity`
- `momentum`
- `lambda_db`
- `k`
- optionale `frequency`
- optionale `energy`
- `number_density`

### 3.2 VDW-spezifische Stoffgrößen

Für jede Spezies zusätzlich:

- `vdw_a`
- `vdw_b`
- `effective_density_vdw` optional
- `interaction_term`
- `excluded_volume_term`

### 3.3 Neue Signatur-Surrogate

- `interaction_score`
- `excluded_volume_score`
- `vdw_signature_score`

### 3.4 Erweiterte Gesamtsignaturen

- `signature_score_wave`
- `signature_score_vdw`
- optional `signature_score_combined`

### 3.5 `tau`-Antwortgrößen

Für jede Spezies und jedes `tau`:

- `tau_response_score`
- `tau_alignment_score`
- `tau_window_label`
- optional `vdw_tau_response_score`

---

## 4. Verarbeitungsschritte

### Schritt 1: Input Normalization

- Pflichtfelder prüfen
- Einheiten konsistent machen
- Stoffdaten validieren
- `tau_grid` prüfen
- prüfen, ob `a` und `b` für VDW-Läufe verfügbar sind

### Schritt 2: Grundgrößen berechnen

- Thermodynamischen Zustand berechnen
- de-Broglie-Grundgrößen berechnen
- bisherige Wellen-Surrogate bilden

### Schritt 3: VDW-Stoffgrößen laden oder berechnen

- `vdw_a`
- `vdw_b`
- daraus:
  - `interaction_term`
  - `excluded_volume_term`
  - optional angepasste Dichte-/Besetzungsgrößen

### Schritt 4: VDW-Surrogate bilden

- `interaction_score`
- `excluded_volume_score`
- `vdw_signature_score`

### Schritt 5: Erweiterte Signaturen aufbauen

- `signature_score_wave`
- `signature_score_vdw`
- optional `signature_score_combined`

### Schritt 6: `tau`-Antwort auswerten

- Antwort der Wellen-Signatur
- Antwort der VDW-Signatur
- optionale kombinierte Antwort

### Schritt 7: Vergleich ideal vs. VDW

- Massenordnung
- reine de-Broglie-Signaturordnung
- VDW-erweiterte Signaturordnung

### Schritt 8: Claims und Readout erzeugen

- zusätzliche materiesensitive Differenzierung markieren
- dokumentieren, ob der VDW-Block überhaupt produktiv ist

---

## 5. Output-Schicht

`DebroglieMatterSignatureVDWOutput` enthält mindestens:

- `run_id`
- `conditions`
- `model_assumptions`
- `tau_grid`
- `species_results`
  - `species`
  - `mass_kg`
  - `lambda_db`
  - `energy`
  - `number_density`
  - `vdw_a`
  - `vdw_b`
  - `interaction_term`
  - `excluded_volume_term`
  - `wave_surrogates`
  - `vdw_surrogates`
  - `combined_surrogates`
  - `tau_response`
- `comparisons`
  - `mass_only_ordering`
  - `wave_signature_ordering`
  - `vdw_signature_ordering`
  - optional `combined_signature_ordering`
  - `difference_flags`
- `claim_readout`
- `testable_claims_ready`

---

## 6. Pflicht-Diagnostiken

### 6.1 `interaction_score`

Wie stark differenziert die attractive Stoffskala zwischen den Spezies?

### 6.2 `excluded_volume_score`

Wie stark differenziert das effektive Eigen-/Ausschlussvolumen?

### 6.3 `vdw_signature_score`

Wie stark ist der grobe kombinierte Stoffbeitrag einer Spezies?

### 6.4 `signature_score_wave`

Wie stark bleibt die reine de-Broglie-Wellenschicht?

### 6.5 `signature_score_combined`

Erzeugt die Kombination aus Wellen- und Stoffschicht zusätzliche materiesensitive Struktur?

### 6.6 `matter_sensitive_delta_vdw`

Wie stark weicht die VDW-erweiterte Signaturordnung von bloßer Massenordnung ab?

---

## 7. Pflicht-Dateioutputs

Der Runner schreibt mindestens:

- `debroglie_matter_signature_vdw_state.json`
- `debroglie_matter_signature_vdw_readout.md`
- `debroglie_matter_signature_vdw_scan.csv`
- `debroglie_matter_signature_vdw_claims.json`

Optional zusätzlich:

- `debroglie_matter_signature_vdw_tau_response.csv`
- `debroglie_matter_signature_vdw_summary.json`
- `debroglie_matter_signature_vdw_debug.json`

---

## 8. Minimaler Erfolg

Die I/O-Spezifikation ist gelungen, wenn sie ermöglicht:

1. die Wellen-Signatur und die VDW-Stoffschicht sauber zu trennen
2. zusätzliche Stoffparameter `a` und `b` explizit zu verarbeiten
3. ideales Gas und van-der-Waals-Modell kontrolliert zu vergleichen
4. zusätzliche materiesensitive Struktur sichtbar oder explizit nicht sichtbar zu machen
5. direkte nächste Tests daraus abzuleiten

---

## 9. Testbare Claims-Readiness

Die I/O-Schicht muss mindestens die Grundlage dafür liefern, folgende Fragen testbar zu machen:

- Öffnet die VDW-Erweiterung überhaupt zusätzliche Differenzierung?
- Bleibt die reine de-Broglie-Längenskala dominant oder nicht?
- Liefern `a` und `b` eine zweite materielle Achse?
- Wird die Ordnung gegenüber bloßer Massenskalierung robuster nichttrivial?
- Reagieren `tau`-Fenster auf die erweiterte Signatur anders?

---

## 10. Minimaler Run-Plan

### Run VDW-A
- gleiche Spezies wie im Grundblock
- `gas_model = ideal_gas`
- Referenzlauf

### Run VDW-B
- gleiche Spezies
- `gas_model = van_der_waals`
- gleiche Grundbedingungen

### Run VDW-C
- ideal vs. VDW direkt vergleichen
- Ordnungen und `matter_sensitive_delta` lesen

---

## 11. Bottom line

`debroglie_matter_signature_vdw_io_v1` definiert die I/O-Schicht für den Übergang von

> reine de-Broglie-Signatur testen

zu

> Wellen-Skala und Stoff-Skala gemeinsam auf zusätzliche materiesensitive Struktur prüfen

Die operative Leitformel lautet:

> Wir testen, ob eine van-der-Waals-Erweiterung dem Signaturblock überhaupt eine zweite materielle Achse jenseits der reinen de-Broglie-Längenskala eröffnet.
