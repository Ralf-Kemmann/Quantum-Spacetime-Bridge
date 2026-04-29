# BMC-08a – Build Script Note

## Status
Offene Implementierung nach Spezifikationskette.

## Zweck
Dieses Paket liefert das erste offene Build-Script für den BMC-08a-Realdaten-Inputsatz.

Das Script baut aus einer flachen offenen Featuretabelle:
- `data/baseline_relational_table_real.csv`
- `data/node_metadata_real.csv`
- `data/bmc08_dataset_manifest.json`

## Eingabedatei
Erwartet wird standardmäßig:
- `data/bmc08a_real_units_feature_table.csv`

## Pflichtfelder der Build-Eingabetabelle
- `node_id`
- `node_family`
- `node_label`
- `L_major_raw`
- `L_minor_raw`
- `m_ref_raw`
- `feature_mode_frequency`
- `feature_length_scale`
- `origin_tag`

Optional:
- `comment`

## Offene Rechenlogik
1. Validierung der Pflichtfelder
2. family-konsistente Shell-Zuordnung:
   - `RING = 0`
   - `CAVITY = 1`
   - `MEMBRANE = 2`
3. Ableitung:
   - `feature_shape_factor = L_major_raw / L_minor_raw`
   - `feature_spectral_index = m_ref_raw`
4. offene z-Standardisierung der vier BMC-08a-Features
5. vollständiger ungerichteter Paarvergleich
6. Kantengewicht:
   - `weight = 1 / (1 + euclidean_distance(z-scored features))`

## Wichtige Grenze
Das Script erzeugt **nur Inputs**, keinen BMC-08-Lauf.
Es ersetzt auch keine offene Festlegung der Rohfeldnamen im realen Exportblock.

## Befund
Noch keiner. Das Paket behauptet keinen Realdatenlauf.

## Interpretation
Die Build-Kette ist jetzt offen genug, um aus einer kleinen fairen Featuretabelle
die ersten echten BMC-08a-Inputdateien zu bauen.

## Hypothese
Wenn ein realer Exportblock diese Eingabetabelle sauber füllen kann,
ist der erste offene Realdatenlauf methodisch erreichbar.

## Offene Lücke
Noch fehlen:
- die tatsächliche `data/bmc08a_real_units_feature_table.csv`
- die BMC-08-Realdaten-Config
- danach erst der BMC-08-Lauf
