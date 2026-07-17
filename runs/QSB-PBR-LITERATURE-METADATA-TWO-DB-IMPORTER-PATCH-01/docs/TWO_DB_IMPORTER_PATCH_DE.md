# Zwei-DB-Importer-Patch

## Befund

Der Importer wurde auf die Zwei-DB-Architektur erweitert.

Neue CLI:

```text
--data-db PATH_TO_DWH
--metadata-db PATH_TO_METADATA_CATALOG
--seed PATH
--mode dry-run
```

Die alte `--db` Variante bleibt nur als deprecated Dry-Run-Kompatibilitätsmodus erhalten und meldet:

```text
single_db_mode_deprecated_for_two_db_architecture
```

## Dry-Run

Der Dry-Run schreibt nicht in die echten Ziel-DBs. Er kopiert DWH und Metadatenkatalog nach `/tmp`, schreibt nur in diese Kopien und prüft danach SHA256 und mtime der echten Ziele.

## Metadata-Registrierung

Die konkrete `meta_*` Registrierung wird nicht erfunden. Im temporären Metadata-DB-Dry-Run wird eine Plan-Tabelle erzeugt:

```text
qsb_literature_metadata_registration_plan_dryrun
```

Damit bleibt die echte `meta_*` Einfügung einem separaten Schema-Mapping-Review vorbehalten.
