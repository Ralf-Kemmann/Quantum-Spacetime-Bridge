# BMC-07c – Runner Update Note

## Status
Offene Implementierung nach Spezifikation.

## Zweck
Dieses Update liefert die vollständige Runner-Datei und das YAML-Update für BMC-07c
zur Variation der Backbone-Definition bei konstanten Readouts und konstanter Armstruktur.

## Geänderte Dateien
- `scripts/bmc07_backbone_variation_runner.py`
- `data/bmc07c_backbone_variation_config.yaml`

## Varianten im YAML
- `hint_reference`
- `strength_topk`
- `strength_topalpha_025`
- `strength_topalpha_050`
- `same_shell_core_topk`
- `hybrid_strength_shell_lambda_05`
- `hybrid_strength_shell_lambda_07`

## Neue Outputs
Im Zielordner `runs/BMC-07/<run_id>/`:
- `summary.json`
- `validation.json`
- `run_metadata.json`
- `backbone_variant_summary.csv`
- `repeat_metrics.csv`
- `readout.md`

Zusätzlich pro Variante in einem Unterordner:
- `summary.json`
- `arm_metrics.csv`

## Befund
Noch keiner. Dieses Paket behauptet keinen Lauf.

## Interpretation
BMC-07c ist jetzt offen implementierbar und vergleichsorientiert aufgesetzt.

## Hypothese
Wenn `off_backbone_localization_supported` unter mehreren Varianten bestehen bleibt,
wird der aktuelle Minimalbefund robuster.

## Offene Lücke
Ein offenes Run-Script für BMC-07c ist in diesem Paket noch nicht enthalten.
