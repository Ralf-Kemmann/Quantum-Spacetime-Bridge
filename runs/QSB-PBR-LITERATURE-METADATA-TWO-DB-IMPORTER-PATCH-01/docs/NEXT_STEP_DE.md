# Nächster Schritt

## Review

Zuerst den Importer-Diff prüfen:

```bash
git diff -- runs/QSB-PBR-LITERATURE-METADATA-SERVER-IMPORT-01/scripts/import_literature_metadata.py
```

Dann die Validierung prüfen:

```bash
sed -n '1,120p' runs/QSB-PBR-LITERATURE-METADATA-TWO-DB-IMPORTER-PATCH-01/validation/validation_results.csv
```

## Spätere Arbeit

Falls reale `meta_*` Registrierungen gewünscht sind, sollte als separater Schritt ein Metadata-Schema-Mapping-Review autorisiert werden. Dieser Patch erzeugt dafür nur eine Dry-Run-Plan-Tabelle und keine echten `meta_*` Inserts.

## Keine Ausführung

Dieser Patch autorisiert keinen Execute-Import.
