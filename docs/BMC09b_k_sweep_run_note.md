# BMC-09b – k-Sweep sauber integriert

## Status
Offene Implementierung für einen systematischen k-Sweep nach BMC-09a.

## Zweck
BMC-09b prüft denselben lokalen k-NN-Ansatz nicht nur für einen einzelnen Wert,
sondern für eine vorab festgelegte k-Leiter.

## Sweep
- `k = 2`
- `k = 3`
- `k = 4`

## Was das Script macht
1. baut die BMC-08c-Featuretable neu
2. baut alle k-NN-Inputs über das bestehende BMC-09a-Build-Script
3. erzeugt pro k eine eigene Runner-Config
4. startet pro k den Variantenrunner
5. sammelt zentrale Sweep-Zusammenfassungen in
   - `runs/BMC-09/BMC09b_k_sweep_open/k_sweep_summary.csv`
   - `runs/BMC-09/BMC09b_k_sweep_open/k_sweep_metadata.json`

## Einzel-Run-Ordner
- `runs/BMC-09/BMC09b_k_2_realdata_open/`
- `runs/BMC-09/BMC09b_k_3_realdata_open/`
- `runs/BMC-09/BMC09b_k_4_realdata_open/`

## Befund
Noch keiner. Dieses Paket behauptet keinen Lauf.

## Interpretation
BMC-09b macht aus dem bisher punktuellen k=3-Test eine saubere Sensitivitätsprüfung.

## Hypothese
Wenn Backbone-Lokalisierung nur bei einem einzelnen k-Wert auftaucht, liegt ein Sensitivitätsbild vor.
Wenn sie über mehrere k-Werte stabil bleibt, wird der Strukturclaim deutlich robuster.

## Offene Lücke
Nach dem Sweep müssen zuerst gelesen werden:
- `runs/BMC-09/BMC09b_k_sweep_open/k_sweep_summary.csv`
- die drei Einzel-Readouts
- optional die einzelnen `backbone_variant_summary.csv`
