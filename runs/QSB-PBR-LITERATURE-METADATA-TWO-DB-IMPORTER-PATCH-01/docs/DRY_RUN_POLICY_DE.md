# Dry-Run-Policy

## Grundsatz

Der Dry-Run darf die echten Ziel-DBs nicht ändern.

## Umsetzung

- SHA256 und mtime der echten Ziel-DBs werden vor dem Dry-Run erfasst.
- Beide Ziel-DBs werden nach `/tmp` kopiert.
- Literaturtabellen werden nur in der temporären Daten-DB-Kopie erzeugt.
- Metadata-Registrierungsplanung wird nur in der temporären Metadata-DB-Kopie erzeugt.
- SHA256 und mtime der echten Ziel-DBs werden nach dem Dry-Run erneut erfasst.

## Execute

`--mode execute` ist in diesem Patch-Run blockiert.

```text
execution_import_authorized=false
```
