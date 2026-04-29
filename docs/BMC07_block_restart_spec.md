# BMC-07 – Block Restart Specification

## Status
Neuaufsetzung des BMC-07-Blocks im offenen Repo-Modus.

## Zweck
Dieser Restart setzt BMC-07 noch einmal sauber auf, mit strikt offener Struktur:
- `docs/` für Spezifikation und Ausführungsvertrag
- `scripts/` für vollständige ausführbare Dateien
- `data/` für offene Inputs und Konfiguration
- `runs/` für spätere Testläufe

## Ausgangspunkt
Der vorige Zwischenstand hat funktional schon sinnvolle Bausteine geliefert, war aber repo-seitig nicht sauber genug gebündelt.
Dieser Restart zieht die Linie deshalb noch einmal klar:

1. **Spezifikation vor Implementierung**
2. **vollständige Dateien statt Fragmentflicken**
3. **kein hidden code**
4. **keine behaupteten Läufe**
5. **offener Startweg über Terminal-Befehl und Shell-Script**

## Blockdefinition
BMC-07 fragt:
**Sitzt ein lokales Ordnungs-/Arrangementsignal eher im Backbone-Kern, im Off-Backbone-Rest oder nur im Vollgraphen?**

Dafür werden drei Primärarme getrennt ausgewertet:
- `full_graph`
- `backbone_only`
- `off_backbone_only`

Zusätzlich wird diagnostisch gezählt:
- `coupling_edges`

## Minimalreadouts
### 1. arrangement_signal
Defensiver Ordnungsreadout gegen offene Shuffle-Referenz auf fixer Topologie.

Definition:
- Für jede Kante: `gap_e = |shell(u) - shell(v)|`
- Beobachteter gewichteter Gap:
  `weighted_shell_gap = sum(w_e * gap_e) / sum(w_e)`
- Shuffle-Referenz:
  Gewichte werden offen über dieselbe Kantenliste permutiert.
- Readout:
  `arrangement_signal = shuffle_mean_gap - observed_gap`

Lesart:
- positiv: Gewichte sitzen shell-näher als unter Shuffle-Referenz
- nahe 0: wenig zusätzliche Ordnung
- negativ: anti-ordnende Tendenz

### 2. shell_order_drift
`abs(shuffle_mean_gap - observed_gap)`

### 3. diffusion_shift
Optionaler Matrixvergleich gegen offene Referenzmatrix aus `data/`.

### 4. pair_neighborhood_shift
Optionaler Matrixvergleich gegen offene Referenzmatrix aus `data/`.

## Inputvertrag
Pflichtdateien in `data/`:
- `baseline_relational_table.csv`
- `node_metadata.csv`
- `bmc07_config_minimal_readouts.yaml`

Optional:
- `diffusion_distance_matrix.npz`
- `pair_neighborhood_matrix.npz`
- `bmc04_reference_summary.json`

## Outputvertrag
Der Runner schreibt in `runs/<run_id>/`:
- `summary.json`
- `validation.json`
- `run_metadata.json`
- `arm_metrics.csv`
- `repeat_metrics.csv`
- `readout.md`

## Befund
Noch keiner. Dieses Bundle behauptet keinen Lauf.

## Interpretation
Keine. Dieses Bundle ist reine offene Neuaufsetzung.

## Hypothese
Wenn ein lokales Ordnungssignal vor allem im Backbone konzentriert ist, sollte
`backbone_only` ein höheres `arrangement_signal` zeigen als `off_backbone_only`.

## Offene Lücke
Die Backbone-Heuristik ist noch minimal und defensiv. Eine spätere Ausbaustufe kann
strength-/structure-aware Auswahlregeln ergänzen, aber nicht in diesem Restart-Schritt.
