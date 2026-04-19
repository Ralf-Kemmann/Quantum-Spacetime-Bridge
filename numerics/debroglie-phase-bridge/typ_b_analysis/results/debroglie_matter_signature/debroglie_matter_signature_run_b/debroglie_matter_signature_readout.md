# debroglie_matter_signature_readout for debroglie_matter_signature_run_b

## 1. Run-Kontext
- **Run-ID:** debroglie_matter_signature_run_b
- **Spezies:** hydrogen, sodium, carbon, nitrogen, sulfur, phosphorus
- **Bedingungen:** 20.0 °C, 1013.0 mbar, 1.0 m^3
- **Geschwindigkeitsmodell:** mean
- **Frequenzmodus:** kinetic_energy_based
- **Tau-Grid:** [0.001, 0.01, 0.1, 1.0]

Kurzlesart:

> Explorationslauf für materialspezifische de-Broglie-Signaturen atomarer Spezies unter definierten Standardbedingungen.

## 2. Signatur-Surrogate
### hydrogen
- `lambda_db`: 1.595435e-10 m
- `energy`: 5.153275e-21 J
- `number_density`: 2.502858e+25 1/m^3
- `length_scale_score`: 1.000000
- `energy_score`: 0.500000
- `occupancy_score`: 0.500000
- `signature_score`: 0.666667

### sodium
- `lambda_db`: 3.340470e-11 m
- `energy`: 5.153275e-21 J
- `number_density`: 2.502858e+25 1/m^3
- `length_scale_score`: 0.096121
- `energy_score`: 0.500000
- `occupancy_score`: 0.500000
- `signature_score`: 0.365374

### carbon
- `lambda_db`: 4.621524e-11 m
- `energy`: 5.153275e-21 J
- `number_density`: 2.502858e+25 1/m^3
- `length_scale_score`: 0.283770
- `energy_score`: 0.500000
- `occupancy_score`: 0.500000
- `signature_score`: 0.427923

### nitrogen
- `lambda_db`: 4.279591e-11 m
- `energy`: 5.153275e-21 J
- `number_density`: 2.502858e+25 1/m^3
- `length_scale_score`: 0.239335
- `energy_score`: 0.500000
- `occupancy_score`: 0.500000
- `signature_score`: 0.413112

### sulfur
- `lambda_db`: 2.828740e-11 m
- `energy`: 5.153275e-21 J
- `number_density`: 2.502858e+25 1/m^3
- `length_scale_score`: 0.000000
- `energy_score`: 0.500000
- `occupancy_score`: 0.500000
- `signature_score`: 0.333333

### phosphorus
- `lambda_db`: 2.877914e-11 m
- `energy`: 5.153275e-21 J
- `number_density`: 2.502858e+25 1/m^3
- `length_scale_score`: 0.009963
- `energy_score`: 0.500000
- `occupancy_score`: 0.500000
- `signature_score`: 0.336654

## 3. Massen- vs. Materiesensitivität

Abweichung von bloßer Massenordnung (`matter_sensitive_delta`):

- `carbon`: -3
- `hydrogen`: -5
- `nitrogen`: -1
- `phosphorus`: +3
- `sodium`: +1
- `sulfur`: +5

## 4. Tau-Fenstervergleich

- Kein starker `near_window`-Kandidat im aktuellen Lauf.

## 5. Claim-Status
- DS1: supported
- DS2: partly_supported
- DS3: supported
- DS4: partly_supported
- DS5: supported

## 6. Gesamtbewertung

### Belastbar steht
- Reproduzierbare de-Broglie-bezogene Grundgrößen wurden pro Spezies konstruiert.
- Die kombinierte Signatur ist im aktuellen Lauf für 'hydrogen' am stärksten ausgeprägt.
- Die stärkste Abweichung von bloßer Massenordnung zeigt 'sulfur'.

### Signalhaft, aber noch offen
- Die Tau-Fensterantwort ist explorativ und noch nicht als starke Resonanzbehauptung zu lesen.
- Materiesensitive Unterschiede sollten gegen alternative Modellannahmen weiter geprüft werden.

### Nicht gestützt oder unklar
- Noch offen ist, welche Einzelsurrogate physikalisch am tragfähigsten sind.
- Noch offen ist, wie direkt tau als physikalische Antwort- oder Taktskala interpretiert werden darf.

## 7. Bottom line

> Der Lauf zeigt, dass aus de-Broglie-bezogenen Materiedaten atomarer Spezies reproduzierbare Signatur-Surrogate konstruiert werden können. Die entscheidende Frage bleibt nun, ob die beobachteten Unterschiede robust über triviale Massenskalierung hinausgehen und sich gegen alternative Modellannahmen halten.

Kurzformel:

> Erst Signatur sichtbar machen, dann prüfen, ob mehr als Masse übrig bleibt.