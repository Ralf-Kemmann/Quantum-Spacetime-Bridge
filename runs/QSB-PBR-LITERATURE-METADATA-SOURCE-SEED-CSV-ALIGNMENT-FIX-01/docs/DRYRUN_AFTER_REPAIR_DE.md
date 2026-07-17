# Dry-run Nach Reparatur

Nach der Seed-Reparatur wurde der Zwei-DB-Dry-run erneut ausgeführt.

Der Dry-run schrieb nur in temporäre Kopien unter `/tmp`. Die echten Ziel-DBs blieben laut SHA256/mtime-Prüfung unverändert.

Validierte Zählungen:

- `qsb_literature_source = 23`
- `qsb_literature_mechanism_tag = 50`
- `qsb_literature_claim_boundary = 23`
- Metadata-Plan-Zeilen = 17

Dies autorisiert keine Execute-Ausführung.
