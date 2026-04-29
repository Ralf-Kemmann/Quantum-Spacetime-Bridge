# BMC-08b – Ring-Symmetrie entfernt

## Status
Offene Implementierung für einen kontrollierten Folgelauf nach BMC-08a.

## Zweck
BMC-08b testet gezielt, ob der robuste Off-Backbone-Befund aus BMC-08a
hauptsächlich durch die Ring-Spiegelsymmetrie (`p` vs `-p`) getragen oder verstärkt wurde.

## Kontrollierte Änderung
Gegenüber BMC-08a wird nur die Ring-Repräsentation geändert:

### BMC-08a
- Ringzustände enthalten `p = -3,-2,-1,1,2,3`

### BMC-08b
- Ringzustände werden auf eine spiegelreduzierte Darstellung reduziert
- Startregel:
  - `keep_rule = positive_only`
  - also nur `p = 1,2,3`

## Konstant gehalten
- dieselben Cavity-Moden
- dieselben Membran-Moden
- dieselbe Build-Logik
- dieselben Backbone-Basisvarianten
- dieselbe BMC-08-Variantenlogik

## Erwartete Lesart
### Fall A
Off-Backbone bleibt robust:
- dann spricht das gegen eine reine Spiegelartefakt-Erklärung

### Fall B
Signal kippt deutlich:
- dann war die Ring-Symmetrie ein zentraler Treiber

## Dateien im Paket
- `scripts/build_bmc08a_feature_table_from_m39x1_no_ring_mirror.py`
- `data/bmc08b_m39x1_no_ring_mirror_config.yaml`
- `data/bmc08b_realdata_config.yaml`
- `scripts/run_bmc08b_realdata_open.sh`

## Befund
Noch keiner. Dieses Paket behauptet keinen Lauf.

## Interpretation
BMC-08b ist ein gezielter Kontrollblock, kein neuer Theorierunner.

## Hypothese
Wenn der Off-Backbone-Befund auch ohne Ring-Spiegelsymmetrie bestehen bleibt,
wird der BMC-08a-Befund methodisch deutlich robuster.

## Offene Lücke
Nach dem Lauf müssen wieder zuerst gelesen werden:
- `runs/BMC-08/BMC08b_realdata_open/readout.md`
- `runs/BMC-08/BMC08b_realdata_open/backbone_variant_summary.csv`
- `runs/BMC-08/BMC08b_realdata_open/summary.json`
