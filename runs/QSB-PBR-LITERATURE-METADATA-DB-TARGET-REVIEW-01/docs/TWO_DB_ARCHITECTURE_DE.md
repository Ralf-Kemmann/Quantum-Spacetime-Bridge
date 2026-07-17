# Zwei-DB-Architektur

## Empfehlung

Die Literaturmetadaten sollten nicht mit einem einzigen `--db` Ziel importiert werden.

Empfohlene Architektur:

- Literaturdaten in der DWH-Workcopy nach menschlicher Freigabe.
- Metadata-Server-Registrierung im META02-Metadatenkatalog nach menschlicher Freigabe.

## Konkrete Zielpfade

```text
literature_data_db = runs/QSB-DB/QSB_DB25_CONSOLIDATED_RESEARCH_SNAPSHOT/qsb_research_dwh_target_workcopy_dwh03.db
metadata_registration_db = runs/QSB-META02/metadata_catalog_update/qsb_metadata_catalog_meta02.sqlite
```

## Importer-Folge

Der vorhandene Importer mit einem einzigen `--db` Argument ist für diese Architektur zu grob.

Erforderliche spätere Änderung, falls explizit beauftragt:

```text
--data-db PATH_TO_DWH
--metadata-db PATH_TO_METADATA_CATALOG
--mode dry-run|execute
```

Diese Änderung wurde in diesem Review nicht implementiert.
