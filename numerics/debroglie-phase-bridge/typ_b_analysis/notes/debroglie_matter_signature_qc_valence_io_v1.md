# debroglie_matter_signature_qc_valence_io_v1

## 1. Ziel

Diese I/O-Spezifikation definiert die Ein- und Ausgabeschicht für die nächste Erweiterung der quantenchemischen Stoffschicht um valenzbezogene Strukturdeskriptoren.

Im ersten Schritt soll bewusst klein begonnen werden:

- **Valenzelektronenzahl** als erster Strukturgeber
- danach erst Schalen- und Subschalenstruktur

Leitfrage:

> Reicht bereits die Valenzelektronenzahl als atomnahe Strukturachse aus, um die bisherige Wellenordnung sinnvoll und physikalisch lesbar zu reorganisieren?

---

## 2. Ausgangslage

Der vorangehende QC-Lauf mit `ionization_score` hat gezeigt:

- die Wellenordnung kann durch eine atomnahe quantenchemische Stoffachse reorganisiert werden
- diese Reorganisation ist feiner als bei der VDW-Schicht
- Ionisierungsenergie wirkt eher als **Stärkeachse**
- es fehlt eine komplementäre **Strukturachse**

Die Valenzelektronenzahl ist dafür der naheliegende erste Kandidat.

---

## 3. Input-Schicht

### 3.1 Pflicht-Inputs

`DebroglieMatterSignatureQCValenceInput` enthält mindestens:

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
  - `qc_mode`
- optionale `species_data`
  - atomare Masse
  - `valence_electron_count`
  - später weitere Konfigurationsdeskriptoren
- `surrogates`
  - aktive Wellen-Surrogate
  - aktive QC-Valenz-Surrogate
  - Kombinationsmodus
  - Gewichte

### 3.2 Minimaler Default-Input

Für den ersten Minimalblock:

- gleiche Speziesliste wie in den bisherigen Läufen
  - hydrogen
  - sodium
  - carbon
  - nitrogen
  - sulfur
  - phosphorus
- gleiche Standardbedingungen
  - 20 °C
  - 1013 mbar
  - 1.0 m³
- `qc_mode = valence_electron_count`

### 3.3 Optionale spätere Erweiterungen

Noch nicht im ersten Wurf verpflichtend:

- `shell_level_score`
- `shell_closure_score`
- `subshell_structure_score`

---

## 4. Interne Zustandsgrößen

### 4.1 Wellen-Grundgrößen

Wie im bisherigen Block:

- `mass_kg`
- `velocity`
- `momentum`
- `lambda_db`
- `energy`
- `number_density`

### 4.2 QC-Valenz-Grundgrößen

Im ersten Wurf mindestens:

- `valence_electron_count`

Später optional:

- `shell_level`
- `shell_closure_flag`
- `orbital_block`
- `subshell_structure_descriptor`

### 4.3 Signatur-Surrogate

#### Wellen-Schicht
- `length_scale_score`
- `energy_score`
- `occupancy_score`
- `signature_score_wave`

#### QC-Valenz-Schicht
- `valence_score`
- optional später weitere Strukturscores
- `signature_score_qc_valence`

#### Kombinierte Schicht
- `signature_score_combined`

---

## 5. Verarbeitungsschritte

### Schritt 1: Input Normalization
- Pflichtfelder prüfen
- Einheiten konsistent machen
- Speziesdaten validieren
- prüfen, ob `valence_electron_count` für alle Spezies verfügbar ist

### Schritt 2: Wellen-Grundgrößen berechnen
- thermische Geschwindigkeit
- Impuls
- de-Broglie-Wellenlänge
- Energie
- Teilchendichte

### Schritt 3: Wellen-Surrogate bilden
- `length_scale_score`
- `energy_score`
- `occupancy_score`
- `signature_score_wave`

### Schritt 4: QC-Valenz-Grundgrößen laden
- `valence_electron_count` pro Spezies

### Schritt 5: QC-Valenz-Surrogat bilden
- `valence_score`
- `signature_score_qc_valence`

### Schritt 6: Kombinierte Signatur berechnen
- `signature_score_combined`

### Schritt 7: Ordnungen vergleichen
- Massenordnung
- Wellenordnung
- kombinierte QC-Valenz-Ordnung
- Delta relativ zur Massenordnung

### Schritt 8: Readout und Claims schreiben
- Ordnungen
- Delta-Strukturen
- Kommentar zur Reorganisationsstärke

---

## 6. Output-Schicht

`DebroglieMatterSignatureQCValenceOutput` enthält mindestens:

- `run_id`
- `conditions`
- `model_assumptions`
- `species_results`
  - `species`
  - `mass_kg`
  - `lambda_db`
  - `energy`
  - `number_density`
  - `valence_electron_count`
  - `wave_surrogates`
  - `qc_valence_surrogates`
  - `combined_surrogates`
- `comparisons`
  - `mass_only_ordering`
  - `wave_signature_ordering`
  - `combined_signature_ordering`
  - `matter_sensitive_delta_wave`
  - `matter_sensitive_delta_qc_valence`
- `claim_readout`

---

## 7. Pflicht-Diagnostiken

### 7.1 `valence_score`
Wie stark differenziert die Valenzelektronenzahl zwischen den Spezies?

### 7.2 `signature_score_qc_valence`
Wie stark wirkt die reine QC-Valenz-Schicht?

### 7.3 `signature_score_combined`
Wie verändert sich die Ordnung, wenn Wellen- und Valenzschicht kombiniert werden?

### 7.4 `matter_sensitive_delta_qc_valence`
Wie stark weicht die kombinierte Ordnung von der bloßen Massenordnung ab?

---

## 8. Pflicht-Dateioutputs

Der Runner schreibt mindestens:

- `debroglie_matter_signature_qc_valence_state.json`
- `debroglie_matter_signature_qc_valence_readout.md`
- `debroglie_matter_signature_qc_valence_scan.csv`
- `debroglie_matter_signature_qc_valence_claims.json`

Optional später:

- `debroglie_matter_signature_qc_valence_debug.json`
- zusätzliche Konfigurationsreports

---

## 9. Minimaler Erfolg

Die I/O-Spezifikation ist gelungen, wenn sie ermöglicht:

1. die Valenzelektronenzahl sauber als ersten Strukturdeskriptor einzuspeisen
2. Wellen- und QC-Valenz-Schicht klar zu trennen
3. kombinierte Ordnungen direkt mit der Wellenordnung zu vergleichen
4. die Reorganisationswirkung dieses ersten Strukturdeskriptors explizit sichtbar zu machen

---

## 10. Testbare Claims-Readiness

Die I/O-Schicht muss mindestens die Grundlage dafür liefern, folgende Fragen testbar zu machen:

- Reorganisiert die Valenzelektronenzahl die bisherige Wellenordnung?
- Ist diese Reorganisation stärker, schwächer oder anders als bei der Ionisierungsenergie?
- Ist die Valenzschicht eher gruppierend, ordnend oder stark umwerfend?
- Trägt sie echte neue Struktur oder nur eine alternative Sortierung bereits bekannter Muster?

---

## 11. Minimaler Run-Plan

### Run QCV-A
- gleiche Spezies wie bisher
- nur `valence_electron_count` als QC-Strukturachse
- kombinierter Lauf mit Wellen-Schicht

### Run QCV-B
- gleiche Spezies
- Vergleich `ionization_score` vs. `valence_score`

### Run QCV-C
- optional: Kombination von Stärke- und Strukturachse innerhalb der QC-Schicht

---

## 12. Bottom line

`debroglie_matter_signature_qc_valence_io_v1` definiert die I/O-Schicht für den ersten Schritt von der atomnahen **Stärkeachse** zur atomnahen **Strukturachse**.

Die operative Leitformel lautet:

> Zuerst testen wir die Valenzelektronenzahl als minimalen Strukturgeber; erst danach folgen Schalen- und Subschalenstruktur.
