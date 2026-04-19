# debroglie_matter_signature_vdw_readout for debroglie_matter_signature_vdw_run_b

## 1. Run-Kontext
- **Run-ID:** debroglie_matter_signature_vdw_run_b
- **Gasmodell:** van_der_waals
- **Spezies:** hydrogen, sodium, carbon, nitrogen, sulfur, phosphorus
- **Bedingungen:** 20.0 °C, 1013.0 mbar, 1.0 m^3
- **Tau-Grid:** [0.001, 0.01, 0.1, 1.0]

Kurzlesart:

> Explorationslauf zur Frage, ob die VDW-Stoffschicht dem bisherigen Wellenblock eine zusätzliche materiesensitive Achse eröffnet.

## 2. Wellen-Schicht
### hydrogen
- `lambda_db`: 1.469902e-10 m
- `energy`: 6.071059e-21 J
- `number_density`: 2.502858e+25 1/m^3
- `length_scale_score`: 1.000000
- `energy_score`: 0.500000
- `occupancy_score`: 0.500000
- `signature_score_wave`: 0.666667

### sodium
- `lambda_db`: 3.077634e-11 m
- `energy`: 6.071059e-21 J
- `number_density`: 2.502858e+25 1/m^3
- `length_scale_score`: 0.096121
- `energy_score`: 0.500000
- `occupancy_score`: 0.500000
- `signature_score_wave`: 0.365374

### carbon
- `lambda_db`: 4.257892e-11 m
- `energy`: 6.071059e-21 J
- `number_density`: 2.502858e+25 1/m^3
- `length_scale_score`: 0.283770
- `energy_score`: 0.500000
- `occupancy_score`: 0.500000
- `signature_score_wave`: 0.427923

### nitrogen
- `lambda_db`: 3.942863e-11 m
- `energy`: 6.071059e-21 J
- `number_density`: 2.502858e+25 1/m^3
- `length_scale_score`: 0.239335
- `energy_score`: 0.500000
- `occupancy_score`: 0.500000
- `signature_score_wave`: 0.413112

### sulfur
- `lambda_db`: 2.606169e-11 m
- `energy`: 6.071059e-21 J
- `number_density`: 2.502858e+25 1/m^3
- `length_scale_score`: 0.000000
- `energy_score`: 0.500000
- `occupancy_score`: 0.500000
- `signature_score_wave`: 0.333333

### phosphorus
- `lambda_db`: 2.651473e-11 m
- `energy`: 6.071059e-21 J
- `number_density`: 2.502858e+25 1/m^3
- `length_scale_score`: 0.009963
- `energy_score`: 0.500000
- `occupancy_score`: 0.500000
- `signature_score_wave`: 0.336654

## 3. VDW-Stoff-Schicht

### hydrogen
- `vdw_a`: 2.470000e-02
- `vdw_b`: 2.661000e-05
- `interaction_term`: 4.260617e+01
- `excluded_volume_term`: 1.105179e-03
- `interaction_score`: 0.000000
- `excluded_volume_score`: 0.000000
- `vdw_signature_score`: 0.000000
- `signature_score_combined`: 0.333333

### sodium
- `vdw_a`: 4.500000e-01
- `vdw_b`: 7.100000e-05
- `interaction_term`: 7.847054e+02
- `excluded_volume_term`: 2.964868e-03
- `interaction_score`: 0.977902
- `excluded_volume_score`: 1.000000
- `vdw_signature_score`: 0.988951
- `signature_score_combined`: 0.677162

### carbon
- `vdw_a`: 3.000000e-01
- `vdw_b`: 4.500000e-05
- `interaction_term`: 5.215806e+02
- `excluded_volume_term`: 1.876345e-03
- `interaction_score`: 0.840801
- `excluded_volume_score`: 0.536385
- `vdw_signature_score`: 0.688593
- `signature_score_combined`: 0.558258

### nitrogen
- `vdw_a`: 1.370000e-01
- `vdw_b`: 3.870000e-05
- `interaction_term`: 2.369855e+02
- `excluded_volume_term`: 1.609576e-03
- `interaction_score`: 0.576005
- `excluded_volume_score`: 0.380983
- `vdw_signature_score`: 0.478494
- `signature_score_combined`: 0.445803

### sulfur
- `vdw_a`: 4.800000e-01
- `vdw_b`: 6.800000e-05
- `interaction_term`: 8.381024e+02
- `excluded_volume_term`: 2.841429e-03
- `interaction_score`: 1.000000
- `excluded_volume_score`: 0.956907
- `vdw_signature_score`: 0.978453
- `signature_score_combined`: 0.655893

### phosphorus
- `vdw_a`: 4.200000e-01
- `vdw_b`: 6.200000e-05
- `interaction_term`: 7.321906e+02
- `excluded_volume_term`: 2.588684e-03
- `interaction_score`: 0.954652
- `excluded_volume_score`: 0.862506
- `vdw_signature_score`: 0.908579
- `signature_score_combined`: 0.622616

## 4. Massen- vs. Materiesensitivität

### Delta relativ zur Massenordnung (Wellen-Schicht)
- `carbon`: -3
- `hydrogen`: -5
- `nitrogen`: -1
- `phosphorus`: +3
- `sodium`: +1
- `sulfur`: +5

### Delta relativ zur Massenordnung (kombinierte Signatur)
- `carbon`: -1
- `hydrogen`: +0
- `nitrogen`: +1
- `phosphorus`: +1
- `sodium`: -2
- `sulfur`: +1

## 5. Claim-Status
- VDW1: supported
- VDW2: supported
- VDW3: partly_supported
- VDW4: supported
- VDW5: supported

## 6. Bottom line

> Der stärkste Wellenkandidat ist 'hydrogen'. Der stärkste kombinierte Kandidat ist 'sodium'. Die entscheidende Frage ist nun, ob die VDW-Stoffschicht echte Zusatzstruktur bringt oder die Ordnung im Kern auf der bisherigen Wellenachse bleibt.

Kurzformel:

> Prüfen, ob die Stoff-Skala wirklich eine zweite Achse öffnet.