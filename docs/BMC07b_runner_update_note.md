# BMC-07b – Runner Update Note

## Status
Offene Implementierung nach vorausgehender Spezifikation.

## Zweck
Dieses Update liefert die vollständige Runner-Datei und das YAML-Update für BMC-07b
mit explizitem `coupling_only`-Arm.

## Geänderte Dateien
- `scripts/bmc07_backbone_scaffold_isolation_runner_coupling_arm.py`
- `data/bmc07_config_coupling_arm.yaml`

## Kernänderungen
- neuer Arm `coupling_only`
- neue defensive Entscheidungslabels:
  - `coupling_localization_supported`
  - `backbone_localization_supported`
  - `off_backbone_localization_supported`
  - `full_only_or_mixed`
  - `weak_or_inconclusive`
- `summary.json` enthält zusätzlich:
  - `dominant_arm`
  - `arm_signal_ranking`

## Befund
Noch keiner. Dieses Paket behauptet keinen Lauf.

## Interpretation
BMC-07b ist jetzt implementierbar und offen startbar.

## Hypothese
Der Coupling-Arm kann als eigener diagnostischer Arm jetzt explizit getestet werden.

## Offene Lücke
Ein offenes Run-Script für BMC-07b ist in diesem Paket noch nicht enthalten.
