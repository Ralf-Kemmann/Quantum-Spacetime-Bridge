# debroglie_matter_signature_vdw_runner_spec_v1

## 1. Ziel

Diese Spezifikation definiert den minimalen Runner für die van-der-Waals-Erweiterung des Materialsignatur-Blocks.

Der Runner soll nicht sofort ein vollrealistisches Stoffmodell liefern, sondern einen **kontrollierten ersten Test** ermöglichen, ob eine nicht-ideale Stoffschicht dem bisherigen de-Broglie-Signaturraum überhaupt eine zusätzliche materiesensitive Achse eröffnet.

Leitfrage:

> Öffnet ein van-der-Waals-basierter Zusatzblock im Vergleich zum idealen Gasmodell eine neue, physikalisch lesbare Differenzierungsstruktur jenseits der reinen de-Broglie-Längenskala?

---

## 2. Ausgangslage

Die erste Serie A–D hat gezeigt:

- die Signaturidee ist operational tragfähig
- die resultierende Ordnung ist robust gegenüber kleinen Modellvarianten
- unter idealgasartigen Standardbedingungen bleibt die Signatur jedoch im Wesentlichen ein de-Broglie-Längenskalenmodell
- `energy_score`, `occupancy_score` und die explizit aktivierte Frequenzachse kollabieren unter den gewählten Standardannahmen auf thermisch universelle Beiträge

Daraus folgt die methodische Motivation für den VDW-Runner:

> Wenn eine echte zweite materielle Achse existiert, muss sie aus einer nicht-universellen Stoffskala kommen.

---

## 3. Runner-Name und Position

Empfohlener Runner-Name:

`src/debroglie_matter_signature_vdw_runner_v1.py`

Optionale Hilfsdateien:

- `src/debroglie_matter_signature_vdw_core_v1.py`
- `src/debroglie_matter_signature_vdw_metrics_v1.py`
- `src/debroglie_matter_signature_vdw_io_v1.py`

Konfigurationsdateien:

- `configs/debroglie_matter_signature_vdw_run_a.yaml`
- `configs/debroglie_matter_signature_vdw_run_b.yaml`
- `configs/debroglie_matter_signature_vdw_run_c.yaml`

Outputs:

- `results/debroglie_matter_signature_vdw/<run_id>/...`

---

## 4. CLI-Schnittstelle

Minimaler Aufruf:

```bash
python src/debroglie_matter_signature_vdw_runner_v1.py --config configs/debroglie_matter_signature_vdw_run_a.yaml
```

Optionale CLI-Parameter:

- `--config <path>`
- `--output-dir <path>`
- `--run-id <string>`
- `--species <name>`
- `--temperature <float>`
- `--pressure <float>`
- `--volume <float>`
- `--gas-model <ideal_gas|van_der_waals>`
- `--tau-grid <comma-separated floats>`
- `--dry-run`

Empfehlung:
Primär config-getrieben arbeiten, CLI-Overrides nur für kleine Vergleichsläufe.

---

## 5. Erwartete Inputs

Der Runner erwartet mindestens:

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
- `species_data`
  - Name
  - Symbol
  - atomare Masse
  - optional `vdw_a`
  - optional `vdw_b`

Minimaler Vergleichskontext:

- `gas_model = ideal_gas` als Referenz
- `gas_model = van_der_waals` als Erweiterung
- gleiche Speziesliste
- gleiche Grundbedingungen

---

## 6. Interne Modulstruktur

### 6.1 `load_inputs()`
Lädt Konfiguration, Speziesdaten und optionale VDW-Parameter.

### 6.2 `normalize_inputs()`
Prüft:

- Pflichtfelder vorhanden
- Einheiten konsistent
- Speziesdaten vollständig
- `tau_grid` sinnvoll
- `a` und `b` vorhanden, falls `gas_model = van_der_waals`

### 6.3 `compute_wave_base()`
Berechnet den bisherigen Wellenblock:

- Teilchenmasse
- Geschwindigkeit
- Impuls
- `lambda_db`
- `k`
- optionale Frequenz-/Energieskalen
- number density

### 6.4 `compute_vdw_terms()`
Berechnet oder liest:

- `vdw_a`
- `vdw_b`
- `interaction_term`
- `excluded_volume_term`
- optionale angepasste Dichte- oder Volumenkorrektur

### 6.5 `build_wave_surrogates()`
Wie bisher:

- `length_scale_score`
- `energy_score`
- `occupancy_score`
- optional `frequency_score`
- `signature_score_wave`

### 6.6 `build_vdw_surrogates()`
Neu:

- `interaction_score`
- `excluded_volume_score`
- `vdw_signature_score`

### 6.7 `build_combined_signature()`
Optional:

- `signature_score_combined`

Ziel:
klare Trennung zwischen
- Wellen-Schicht
- Stoff-Schicht
- kombinierter Schicht

### 6.8 `evaluate_tau_response()`
Vergleicht `tau`-Fenster mit:
- Wellen-Signatur
- VDW-Signatur
- optional kombinierter Signatur

### 6.9 `compare_ideal_vs_vdw()`
Vergleicht:

- Massenordnung
- Wellenordnung
- VDW-Ordnung
- kombinierte Ordnung
- Differenzen und Zusatzgewinn

### 6.10 `write_outputs()`
Schreibt JSON-, CSV- und Markdown-Dateien.

---

## 7. Physikalische Minimalarchitektur

### 7.1 Wellen-Schicht

Pflichtgrößen:

- `length_scale_score`
- `energy_score`
- `occupancy_score`
- optional `frequency_score`

Ziel:
bisherigen Block unverändert nachvollziehbar halten.

### 7.2 Stoff-Schicht

Pflichtgrößen:

- `interaction_score`
- `excluded_volume_score`
- `vdw_signature_score`

Ziel:
erste nicht-universelle Stoffskala operationalisieren.

### 7.3 Kombinierte Schicht

Optionaler erster Minimalansatz:

`signature_score_combined = weighted_sum(signature_score_wave, vdw_signature_score)`

Wichtig:
Die Gewichte müssen im ersten Wurf transparent und klein gehalten werden.

---

## 8. Ablaufreihenfolge

Der Runner soll in dieser Reihenfolge arbeiten:

1. Config laden
2. Inputs laden
3. Inputs normalisieren
4. Wellen-Grundgrößen berechnen
5. Wellen-Surrogate bilden
6. VDW-Terme berechnen
7. VDW-Surrogate bilden
8. optionale kombinierte Signatur bilden
9. `tau`-Fensterantwort auswerten
10. ideal vs. VDW vergleichen
11. Dateien schreiben
12. Readout erzeugen

---

## 9. Konfigurationsschema

Beispielstruktur:

```yaml
run_id: debroglie_matter_signature_vdw_run_a

species_list:
  - hydrogen
  - sodium
  - carbon
  - nitrogen
  - sulfur
  - phosphorus

conditions:
  temperature_C: 20.0
  pressure_mbar: 1013.0
  volume_m3: 1.0

model_assumptions:
  species_mode: atomic_species
  gas_model: van_der_waals
  velocity_model: rms
  frequency_mode: kinetic_energy_based
  density_mode: corrected_density
  vdw_mode: simple_ab

surrogates:
  wave_enabled:
    - length_scale_score
    - energy_score
    - occupancy_score
  vdw_enabled:
    - interaction_score
    - excluded_volume_score
    - vdw_signature_score
  combined_mode: weighted_sum
  weights:
    wave: 1.0
    vdw: 1.0

tau_grid:
  - 0.001
  - 0.01
  - 0.1
  - 1.0

output:
  base_dir: results/debroglie_matter_signature_vdw
  write_state_json: true
  write_readout_md: true
  write_scan_csv: true
  write_claims_json: true
```

---

## 10. Pflicht-Dateioutputs

Pro Run mindestens:

- `debroglie_matter_signature_vdw_state.json`
- `debroglie_matter_signature_vdw_readout.md`
- `debroglie_matter_signature_vdw_scan.csv`
- `debroglie_matter_signature_vdw_claims.json`

Optional:

- `debroglie_matter_signature_vdw_tau_response.csv`
- `debroglie_matter_signature_vdw_summary.json`
- `debroglie_matter_signature_vdw_debug.json`

---

## 11. Minimale JSON-Struktur

### 11.1 `debroglie_matter_signature_vdw_state.json`

Mindestens:

```json
{
  "run_id": "debroglie_matter_signature_vdw_run_a",
  "conditions": {},
  "species_results": [],
  "comparisons": {}
}
```

Jedes Element in `species_results` mindestens:

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

### 11.2 `debroglie_matter_signature_vdw_claims.json`

Mindestens:

- `claim_vdw1_status`
- `claim_vdw2_status`
- `claim_vdw3_status`
- `claim_vdw4_status`
- `claim_vdw5_status`
- `overall_status`
- `notes`

### 11.3 `debroglie_matter_signature_vdw_scan.csv`

Mindestens Spalten:

- `run_id`
- `species`
- `gas_model`
- `lambda_db`
- `energy`
- `number_density`
- `vdw_a`
- `vdw_b`
- `interaction_score`
- `excluded_volume_score`
- `vdw_signature_score`
- `signature_score_wave`
- `signature_score_combined`
- `tau`
- `tau_response_score`
- `matter_sensitive_delta_vdw`
- `response_label`

---

## 12. Readout-Template-Logik

`debroglie_matter_signature_vdw_readout.md` soll kurz und streng strukturiert sein:

1. **Run-Kontext**
2. **Wellen-Schicht**
3. **VDW-Stoff-Schicht**
4. **Vergleich ideal vs. VDW**
5. **Massen- vs. Materiesensitivität**
6. **Tau-Fenstervergleich**
7. **Claim-Status**
8. **Bottom line**

Der Readout soll klar sagen:

- bringt die Stoffschicht überhaupt Zusatzinformation?
- oder bleibt alles im Kern Wellen-Längenskalenordnung?

---

## 13. Minimaler Run-Plan

### Run VDW-A
- `gas_model = ideal_gas`
- Referenz auf Basis der bisherigen Serie

### Run VDW-B
- `gas_model = van_der_waals`
- gleiche Spezies
- gleiche Bedingungen

### Run VDW-C
- direkte Gegenüberstellung:
  - Wellenordnung
  - VDW-Ordnung
  - kombinierte Ordnung

### Run VDW-D optional
- kleine Gewichtungsvariation der kombinierten Signatur

---

## 14. Entscheidungslogik

### Unterstützt
Wenn mindestens gilt:

- VDW-Surrogate sind reproduzierbar
- die Stoffschicht erzeugt zusätzliche Differenzierung
- die kombinierte Signaturordnung kollabiert nicht auf die reine Wellenordnung
- und die materiesensitive Struktur gewinnt an Breite

### Teilweise unterstützt
Wenn:

- Unterschiede sichtbar, aber schwach oder stark modellabhängig sind
- oder der Zusatzgewinn gegenüber der Wellen-Schicht klein bleibt

### Nicht unterstützt
Wenn:

- die Stoffschicht praktisch keine neue Struktur bringt
- alles wieder auf die reine de-Broglie-Längenskala zurückfällt
- oder die VDW-Terme nur numerisches Rauschen hinzufügen

---

## 15. Technische Minimalanforderungen

Der Runner soll:

- robuste Fehlerbehandlung für fehlende `a`/`b`-Parameter haben
- ideal und VDW im selben Outputschema vergleichbar machen
- alle Modellannahmen transparent dokumentieren
- CSV-Output für direkten Ordnungsvergleich erzeugen
- auch bei `inconclusive` saubere Summary-Dateien schreiben

Optional später:

- weitergehende Stoffdaten
- Molekülmodi
- alternative nicht-ideale Zustandsgleichungen
- Plot-Ausgaben

---

## 16. Bottom line

`debroglie_matter_signature_vdw_runner_spec_v1` macht aus der VDW-Erweiterung einen kontrollierten, launchbaren Testblock.

Die operative Leitformel lautet:

> Der Runner soll nicht schon Vollrealismus liefern, sondern zuerst testen, ob die Stoff-Skala über van der Waals dem bisherigen de-Broglie-Signaturraum überhaupt eine zusätzliche materiesensitive Achse eröffnet.
