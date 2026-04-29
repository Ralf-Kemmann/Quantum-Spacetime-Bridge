# BMC-08a – M39x1 to Featuretable Script Note

## Status
Offene Implementierung nach Mapping- und Feature-Spezifikation.

## Zweck
Dieses Script baut aus dem realen M39x1-Familienblock eine offene
`data/bmc08a_real_units_feature_table.csv`.

## Eingabe
Standardmäßig:
- `numerics/debroglie-phase-bridge/m33_v0_scaffold/configs/m39x1_ring_dispersion_irregularity_families.yaml`

## Ausgabe
Standardmäßig:
- `data/bmc08a_real_units_feature_table.csv`

## Offene Rechenlogik
### Ring
- Nodes aus `p`-Werten der Ringfamilie
- `feature_mode_frequency = p^2 / 2`
- `feature_length_scale = 1 / |p|`
- `L_major_raw = 1.0`
- `L_minor_raw = 1.0`
- `m_ref_raw` = Rang von `|p|`

### Cavity
- Nodes aus den `mode_indices`
- `k = sqrt((n/a)^2 + (m/b)^2 + (l/d)^2)`
- `feature_mode_frequency = k`
- `feature_length_scale = 1 / k`
- `L_major_raw` = größte Geometrieausdehnung
- `L_minor_raw` = kleinste Geometrieausdehnung
- `m_ref_raw` = Energierang nach `k`

### Membrane
- Nodes aus den `mode_indices`
- `k = j_(m,n) / R` mit offen hartkodierten Bessel-Nullstellen für die im YAML vorhandenen Moden
- `feature_mode_frequency = k`
- `feature_length_scale = 1 / k`
- `L_major_raw = 2R`
- `L_minor_raw = 2R`
- `m_ref_raw` = Energierang nach `k`

## Wichtige Grenze
Dieses Script ist ein offener Startblock für BMC-08a.
Es erhebt keinen Anspruch auf maximale physikalische Vollständigkeit.
Insbesondere:
- `shape_factor` wird für Ring und Membrane geometrisch neutralisiert
- Membran-`k` basiert nur auf den im Startblock benötigten Bessel-Nullstellen

## Befund
Noch keiner. Das Paket behauptet keinen BMC-08-Lauf.

## Interpretation
Damit ist jetzt erstmals ein echter projektinterner Weg vorhanden,
aus M39x1 direkt eine BMC-08a-Featuretabelle zu bauen.

## Hypothese
Wenn der daraus gebaute Realdaten-Inputsatz unter fairen Backbone-Varianten ein interpretierbares Muster trägt,
wird BMC-08 methodisch deutlich stärker als der reine Smoke-Test.

## Offene Lücke
Noch fehlen:
- der offene Build-Schritt mit diesem neuen Featuretable-Script
- danach das Build der realen Inputdateien
- danach der erste echte BMC-08-Lauf
