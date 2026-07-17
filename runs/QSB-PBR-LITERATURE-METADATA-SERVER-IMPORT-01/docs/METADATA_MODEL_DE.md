# Metadatenmodell

Diese Literaturdaten sind Kontext- und Suchraum-Metadaten.
Sie sind keine interne Evidenz für QSB/PBR.
Sie autorisieren keine physikalischen oder mechanistischen Claims.

## Tabellenentwurf

- `qsb_literature_source`: bibliographische Literaturmetadaten aus dem Prompt.
- `qsb_literature_mechanism_tag`: Vokabular- und Suchraum-Tags je Literaturzeile.
- `qsb_literature_claim_boundary`: harte Claim-Grenzen je Literaturzeile.
- `qsb_literature_qsb_mapping`: vorbereiteter Platzhalter für spätere Struktur-Tags.
- `qsb_literature_import_manifest`: Importmanifest mit Run-ID, Quelle, Hash, Status und Claim Boundary.

## Metadata-Server

Die Registrierung ist vorbereitet, aber nicht ausgeführt. Im Repository existieren mehrere mögliche Zielmuster:

- PostgreSQL-artige `metadata.meta_field` / `metadata.meta_alias`
- domänenspezifische `qsb_metadata.*` Tabellen aus früheren Litnote-Runs
- SQLite-Snapshots und Browser-Metadaten

Ohne menschliche Auswahl eines Zielsystems bleibt der Status:

```text
blocked_requires_human_db_target
```
