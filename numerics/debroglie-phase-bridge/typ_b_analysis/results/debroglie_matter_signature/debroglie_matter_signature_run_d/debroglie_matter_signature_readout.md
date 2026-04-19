# debroglie_matter_signature_readout for debroglie_matter_signature_run_d

## 1. Run-Kontext
- **Run-ID:** debroglie_matter_signature_run_d
- **Spezies:** hydrogen, sodium, carbon, nitrogen, sulfur, phosphorus
- **Bedingungen:** 20.0 °C, 1013.0 mbar, 1.0 m^3
- **Geschwindigkeitsmodell:** rms
- **Frequenzmodus:** omega_from_v_over_lambda
- **Tau-Grid:** [0.001, 0.01, 0.1, 1.0]

Kurzlesart:

> Explorationslauf mit explizit aktivierter Frequenz als zweite Signaturachse.

## 2. Signatur-Surrogate
### hydrogen
- `lambda_db`: 1.469902e-10 m
- `energy`: 6.071059e-21 J
- `number_density`: 2.502858e+25 1/m^3
- `frequency`: 1.832476e+13 Hz
- `length_scale_score`: 1.000000
- `energy_score`: 0.500000
- `occupancy_score`: 0.500000
- `frequency_score`: 0.500000
- `signature_score`: 0.625000

### sodium
- `lambda_db`: 3.077634e-11 m
- `energy`: 6.071059e-21 J
- `number_density`: 2.502858e+25 1/m^3
- `frequency`: 1.832476e+13 Hz
- `length_scale_score`: 0.096121
- `energy_score`: 0.500000
- `occupancy_score`: 0.500000
- `frequency_score`: 0.500000
- `signature_score`: 0.399030

### carbon
- `lambda_db`: 4.257892e-11 m
- `energy`: 6.071059e-21 J
- `number_density`: 2.502858e+25 1/m^3
- `frequency`: 1.832476e+13 Hz
- `length_scale_score`: 0.283770
- `energy_score`: 0.500000
- `occupancy_score`: 0.500000
- `frequency_score`: 0.500000
- `signature_score`: 0.445942

### nitrogen
- `lambda_db`: 3.942863e-11 m
- `energy`: 6.071059e-21 J
- `number_density`: 2.502858e+25 1/m^3
- `frequency`: 1.832476e+13 Hz
- `length_scale_score`: 0.239335
- `energy_score`: 0.500000
- `occupancy_score`: 0.500000
- `frequency_score`: 0.500000
- `signature_score`: 0.434834

### sulfur
- `lambda_db`: 2.606169e-11 m
- `energy`: 6.071059e-21 J
- `number_density`: 2.502858e+25 1/m^3
- `frequency`: 1.832476e+13 Hz
- `length_scale_score`: 0.000000
- `energy_score`: 0.500000
- `occupancy_score`: 0.500000
- `frequency_score`: 0.500000
- `signature_score`: 0.375000

### phosphorus
- `lambda_db`: 2.651473e-11 m
- `energy`: 6.071059e-21 J
- `number_density`: 2.502858e+25 1/m^3
- `frequency`: 1.832476e+13 Hz
- `length_scale_score`: 0.009963
- `energy_score`: 0.500000
- `occupancy_score`: 0.500000
- `frequency_score`: 0.500000
- `signature_score`: 0.377491

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
- Die Frequenzachse ist jetzt explizit aktiviert, muss aber gegen alternative Annahmen weiter geprüft werden.
- Die Tau-Fensterantwort ist weiterhin explorativ und noch nicht als starke Resonanzbehauptung zu lesen.

### Nicht gestützt oder unklar
- Noch offen ist, ob frequency_score echte Zusatzstruktur bringt oder nur dieselbe Ordnung neu parametrisiert.
- Noch offen ist, wie direkt tau als physikalische Antwort- oder Taktskala interpretiert werden darf.

## 7. Bottom line

> Der Lauf testet, ob eine explizit aktivierte Frequenzachse die materialspezifische Signatur verbreitert. Entscheidend ist nun, ob dadurch gegenüber der reinen Längenskalenordnung wirklich neue Struktur entsteht oder nur dieselbe Ordnung in neuer Sprache erscheint.

Kurzformel:

> Frequenz ist jetzt im Spiel — jetzt zeigt sich, ob sie wirklich etwas trägt.