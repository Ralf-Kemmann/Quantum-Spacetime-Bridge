# BMC-10 – Nullmodell-Test, 1:1 kompatibel

## Status
Offene Implementierung für den expliziten Nullmodell-Test auf Graphebene.

## Zweck
BMC-10 prüft, ob das in BMC-09d gefundene Strukturfenster
auch dann wieder auftaucht, wenn die physiktragenden Features
durch ein synthetisches Gaussian-Nullmodell ersetzt werden.

## Designprinzip
- gleiche Node-Anzahl
- gleiche Shell-Verteilung
- gleiche Graphpipeline
- gleiche Threshold-Fälle
- gleiche Backbone-Varianten
- aber keine originale physikalische Featurestruktur

## Nullmodell
Für jeden Seed werden Gaussian-artige Featurewerte erzeugt,
deren Mittelwerte und Streuungen aus der BMC-08c-Featuretable
übernommen werden. Der Node-Contract bleibt erhalten.

## Fälle
- `threshold_tau_028`
- `threshold_tau_03`
- `threshold_tau_032`

## Seeds
- `101`
- `202`
- `303`

## Outputs
### Graph-Build-Ebene
- `data/bmc10_nullmodel_inputs/graph_build_diagnostics.csv`

### Sweep-Ebene
- `runs/BMC-10/BMC10_nullmodel_open/nullmodel_sweep_summary.csv`
- `runs/BMC-10/BMC10_nullmodel_open/nullmodel_sweep_metadata.json`

### Einzelruns
- `runs/BMC-10/BMC10_seed_<seed>_<case>_realdata_open/`

## Befund
Noch keiner. Dieses Paket behauptet keinen Lauf.

## Interpretation
BMC-10 ist der entscheidende Test, ob das bisherige Regimebild
auf physikalischer Struktur oder auf Parametrisierungsartefakten beruht.

## Hypothese
Wenn das Backbone-Fenster auch im Nullmodell wieder auftaucht,
misst die Pipeline eher Graphtopologie als Physik.
Wenn es verschwindet oder stark instabil wird,
spricht das für ein nichttriviales Strukturfenster im Originalsystem.

## Offene Lücke
Nach dem Lauf sollten zuerst gelesen werden:
- `data/bmc10_nullmodel_inputs/graph_build_diagnostics.csv`
- `runs/BMC-10/BMC10_nullmodel_open/nullmodel_sweep_summary.csv`
- dann gezielt einzelne Readouts der auffälligen Seed/Fall-Kombinationen
