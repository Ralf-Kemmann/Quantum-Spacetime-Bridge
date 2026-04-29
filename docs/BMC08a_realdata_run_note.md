# BMC-08a – Realdaten-Config und offenes Run-Script

## Status
Offene Ausführungsdateien für den ersten echten BMC-08a-Realdatenlauf.

## Zweck
Dieses Paket liefert:
- die Realdaten-Config in `data/`
- das offene Run-Script in `scripts/`

für den ersten echten BMC-08a-Lauf auf dem aus M39x1 abgeleiteten Realdaten-Inputsatz.

## Geänderte Dateien
- `data/bmc08_realdata_config.yaml`
- `scripts/run_bmc08a_realdata_open.sh`

## Warum der bestehende Varianten-Runner verwendet wird
BMC-08a übernimmt bewusst die offene Variantenlogik aus BMC-07c:
- gleiche Armstruktur
- gleiche Readouts
- gleiche defensive Entscheidungslogik

Nur die Inputs wechseln von Minimaldaten zu realen Projektinputs.

## Backbone-Varianten in Version 1
Verwendet werden nur faire Basisvarianten:
- `strength_topk_6`
- `strength_topalpha_025`
- `strength_topalpha_050`

Nicht enthalten:
- `hint_reference`
- `same_shell_core`
- `hybrid_strength_shell`

Begründung:
Der erste echte Realdatenlauf soll methodisch defensiv bleiben und keine readout-näheren Varianten priorisieren.

## Befund
Noch keiner. Dieses Paket behauptet keinen Lauf.

## Interpretation
Mit diesen beiden Dateien ist der erste offene BMC-08a-Realdatenlauf jetzt startbar.

## Hypothese
Wenn auf dem echten M39x1-basierten Realdatensatz unter diesen fairen Basisvarianten ein konsistentes Muster erscheint, ist das der erste belastbare Transferbefund über den Minimalblock hinaus.

## Offene Lücke
Nach dem Lauf müssen zuerst gelesen werden:
- `runs/BMC-08/BMC08a_realdata_open/readout.md`
- `runs/BMC-08/BMC08a_realdata_open/backbone_variant_summary.csv`
- `runs/BMC-08/BMC08a_realdata_open/summary.json`
