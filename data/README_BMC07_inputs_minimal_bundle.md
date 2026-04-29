# README – BMC-07 Minimal Inputs Bundle

## Status
Offenes Input-Bundle für den ersten BMC-07-Start.

## Zweck
Dieses Bundle schließt genau die aktuell fehlende Lücke:
- `data/baseline_relational_table.csv`
- `data/node_metadata.csv`

Damit kann der offene Runner überhaupt erst starten.

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

## Befund
Noch keiner. Das Bundle liefert nur die fehlenden offenen Inputs.

## Interpretation
Keine. Das ist reine Eingabeschließung.

## Hypothese
Nicht anwendbar.

## Offene Lücke
Die Daten sind ein Minimaldatensatz für den Start, nicht der spätere inhaltliche Produktionsinput.
