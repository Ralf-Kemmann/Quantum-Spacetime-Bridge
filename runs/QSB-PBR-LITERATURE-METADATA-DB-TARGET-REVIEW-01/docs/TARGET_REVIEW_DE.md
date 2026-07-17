# Zielprüfung

## Befund

Sechs SQLite-Kandidaten wurden ausschließlich read-only geöffnet. Die drei Pflichtkandidaten existieren:

- `qsb_research_dwh_target_workcopy_dwh03.db`
- `qsb_metadata_catalog_meta02.sqlite`
- `qsb_metadata_catalog_corrcore01.sqlite`

Die DWH-Workcopy enthält DWH-nahe Roh-, Core-/Mart-, Source- und Claim-Tabellen. Die META02- und CORRCORE01-Dateien enthalten jeweils vollständige `meta_*` Tabellenfamilien.

## Bewertung

`qsb_research_dwh_target_workcopy_dwh03.db` ist der plausibelste Kandidat für Literaturdaten nach menschlicher Freigabe.

`qsb_metadata_catalog_meta02.sqlite` ist der plausibelste Kandidat für Metadata-Server-Registrierung nach menschlicher Freigabe.

`qsb_metadata_catalog_corrcore01.sqlite` ist ebenfalls ein Metadata-Catalog-Kandidat, wirkt aber stärker an den CORRCORE01-Lauf gebunden.

## Status

```text
db_target_review_recommends_two_db_architecture
```
