# Seed-Reparatur

## Befund

Die Datei `literature_source_seed.csv` war spaltenverschoben. Vor der Reparatur enthielt `source_url` quellentypartige Werte wie `primary_literature`, und Klassifikationsfelder waren nach rechts/links verschoben.

## Reparatur

Die 23 Literaturzeilen wurden aus der dokumentierten Source-Copy rekonstruiert und mit `csv.DictWriter` in stabiler Feldreihenfolge neu geschrieben.

Nicht vorhandene DOI-, arXiv-, URL- und Venue-Werte wurden nicht erfunden. Diese Felder bleiben leer.

## Ergebnis

Die reparierte Seed-Datei validiert:

- 23 Quellen
- erwartete IDs
- keine DictReader-Overflow-Felder
- gültige Enum-Werte
- keine source_url/source_type-Verwechslung
