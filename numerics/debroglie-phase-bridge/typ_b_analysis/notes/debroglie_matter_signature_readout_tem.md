# debroglie_matter_signature_readout_template_v1

## 1. Run-Kontext

- **Run-ID:** `<run_id>`
- **Datum:** `<date>`
- **Spezies:** `<species_list>`
- **Bedingungen:** `<temperature_C> °C`, `<pressure_mbar> mbar`, `<volume_m3> m^3`
- **Modellannahmen:**
  - Speziesmodus: `<species_mode>`
  - Gasmodell: `<gas_model>`
  - Geschwindigkeitsmodell: `<velocity_model>`
  - Frequenzmodus: `<frequency_mode>`
  - Dichtemodell: `<density_mode>`
- **Tau-Grid:** `<tau_grid>`

Kurzlesart des Laufs:

> `<one_sentence_run_purpose>`

---

## 2. Grundgrößen pro Spezies

Für jede Spezies wurden mindestens berechnet:

- Teilchenmasse
- charakteristische Geschwindigkeit
- Impuls
- de-Broglie-Wellenlänge
- Wellenzahl
- optionale Frequenz-/Energieskala
- Teilchendichte

### Kompakte Zusammenfassung

| Spezies | Masse | Geschwindigkeit | Impuls | `lambda_db` | `k` | Frequenz/Energie | Teilchendichte |
|---|---:|---:|---:|---:|---:|---:|---:|
| `<species_1>` | `<...>` | `<...>` | `<...>` | `<...>` | `<...>` | `<...>` | `<...>` |
| `<species_2>` | `<...>` | `<...>` | `<...>` | `<...>` | `<...>` | `<...>` | `<...>` |

Kurzlesart:

> `<basic_quantities_interpretation>`

---

## 3. Signatur-Surrogate

Berechnete Surrogate:

- `length_scale_score`
- `frequency_score`
- `occupancy_score`
- `energy_score`
- `signature_score`

### Beobachtete Differenzierung

- **Stärkstes Surrogat:** `<strongest_surrogate>`
- **Schwächstes Surrogat:** `<weakest_surrogate>`
- **Konsistenz der Surrogate:** `<high|medium|low>`

Kurzlesart:

> `<which_surrogates_differentiate_best>`

---

## 4. Tau-Fenstervergleich

Untersucht wurden folgende `tau`-Fenster:

`<tau_grid>`

### Beobachtete Antwort

- **Spezies mit stärkster `tau`-Differenzierung:** `<species_or_set>`
- **Fenster mit stärkster Antworttrennung:** `<tau_value_or_range>`
- **Fenster mit schwacher oder keiner Trennung:** `<tau_value_or_range>`

Kurzlesart:

> `<tau_response_interpretation>`

---

## 5. Massen- vs. Materiesensitivität

Verglichen wurden:

- einfache Massenordnung
- Ordnung nach Signatur-Surrogaten
- `matter_sensitive_delta`

### Ergebnis

- **Massenskalierung dominiert:** `<yes/no/partly>`
- **Nichttriviale Abweichung sichtbar:** `<yes/no/partly>`
- **Welche Spezies weichen am stärksten von bloßer Massenordnung ab?** `<species_or_set>`

Kurzlesart:

> `<mass_vs_matter_reading>`

---

## 6. Resonanzfenster-Kandidaten

Wichtig:
Hier sind nur **defensive Resonanzkandidaten** gemeint, keine starke Behauptung über reale Raumzeitresonanz.

### Kandidatenstatus

- **Plausibler Fensterkandidat:** `<tau_value_or_none>`
- **Grund:** `<reason>`
- **Stabilität des Kandidaten:** `<high|medium|low>`
- **Modellabhängigkeit:** `<high|medium|low>`

Kurzlesart:

> `<candidate_window_reading>`

---

## 7. Claim-Status

### Claim DS1
Reproduzierbare de-Broglie-bezogene Signatur-Surrogate konstruierbar  
**Status:** `<supported|partly_supported|not_supported>`

### Claim DS2
Systematisch unterschiedliche Antwortprofile relativ zu denselben `tau`-Fenstern  
**Status:** `<supported|partly_supported|not_supported>`

### Claim DS3
Mindestens ein nichttrivialer Unterschied über Massenskalierung hinaus  
**Status:** `<supported|partly_supported|not_supported>`

### Claim DS4
Plausibler Antwortfenster- oder Resonanzkandidat  
**Status:** `<supported|partly_supported|not_supported>`

### Claim DS5
Signaturidee als Brückeninput weiterverwendbar  
**Status:** `<supported|partly_supported|not_supported>`

---

## 8. Gesamtbewertung

### Belastbar steht

- `<robust_point_1>`
- `<robust_point_2>`
- `<robust_point_3>`

### Signalhaft, aber noch offen

- `<signal_point_1>`
- `<signal_point_2>`

### Nicht gestützt oder unklar

- `<unclear_point_1>`
- `<unclear_point_2>`

---

## 9. Bottom line

> `<two_to_four_sentence_bottom_line>`

Kurzformel:

> `<one_sentence_takeaway>`

---

## 10. Nächster Schritt

Empfohlener Anschluss:

- `<next_step_1>`
- `<next_step_2>`
- `<next_step_3>`

Leitfrage für den Anschlussblock:

> `<next_block_question>`