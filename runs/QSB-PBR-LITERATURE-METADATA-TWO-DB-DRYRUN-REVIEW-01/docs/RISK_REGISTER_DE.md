# Risikoregister

## R04: Seed-CSV-Spaltenverschiebung

Status: `blocking_validation_failed`

Die Datei `literature_source_seed.csv` zeigt eine Spaltenverschiebung. Dadurch enthalten Felder wie `source_url`, `source_type`, `source_class`, `author_cluster` und `theory_cluster` nicht die erwarteten Werte.

Minimaler Reparaturschritt:

```text
QSB-PBR-LITERATURE-METADATA-SEED-CSV-REPAIR-VALIDATION-01
```

## R01: Metadata native mapping

Status: `open_nonblocking_for_dryrun_review`

Die Metadata-Registrierung ist derzeit nur als Plan-Tabelle im temporären Metadata-DB-Dry-run vorhanden. Vor einer echten `meta_*` Registrierung ist ein separates Schema-Mapping-Review nötig.
