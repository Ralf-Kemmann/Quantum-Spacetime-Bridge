# README – BMC-07 Inputs

## Pflichtdateien
- `baseline_relational_table.csv`
- `node_metadata.csv`
- `bmc07_config_minimal_readouts.yaml`

## Optional
- `diffusion_distance_matrix.npz`
- `pair_neighborhood_matrix.npz`
- `bmc04_reference_summary.json`

## Feldliste – baseline_relational_table.csv
- `source` — string — Quellknoten der ungerichteten Kante.
- `target` — string — Zielknoten der ungerichteten Kante.
- `weight` — float — Kantengewicht.

## Feldliste – node_metadata.csv
- `node_id` — string — eindeutige Knotenkennung.
- `shell_index` — integer — grobe Schalenzuordnung.
- `node_label` — string — lesbarer Knotenname.
- `backbone_hint` — integer — 1/0-Hinweis für Backbone-Zugehörigkeit.
- `comment` — string — optionale Kurzbeschreibung.
