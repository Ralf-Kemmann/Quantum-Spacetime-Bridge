# Nächster Schritt

## Menschliche Entscheidung erforderlich

Vor jeder Import-Ausführung sollte der Mensch entscheiden:

1. Soll die Zwei-DB-Architektur verwendet werden?
2. Soll `qsb_research_dwh_target_workcopy_dwh03.db` als Literaturdatenziel dienen?
3. Soll `qsb_metadata_catalog_meta02.sqlite` als Metadata-Server-Registrierungsziel dienen?
4. Soll der Importer später auf getrennte Argumente `--data-db` und `--metadata-db` erweitert werden?

## Kein Execute in diesem Review

In diesem Review wurde kein Import ausgeführt und keine Datenbank beschrieben.

## Exakter Review-Befehl

```bash
sed -n '1,120p' runs/QSB-PBR-LITERATURE-METADATA-DB-TARGET-REVIEW-01/data/db_candidate_target_assessment.csv
```
