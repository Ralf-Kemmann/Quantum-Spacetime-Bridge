# QSB Source Hub Prototype

This package contains the GAP02A dry-run Source Hub prototype. It creates a SQLite database from prior GAP metadata and local file fingerprints only.

The Source Hub separates four layers:

- source metadata: files, archives, paths, hashes, classes, flags, and lineage
- mart raw records: future staging rows that must point back to source metadata
- canonical mart records: future typed records created only by explicit mart rules
- result records: future result objects linked back through canonical and raw lineage

The dry-run database is not a production catalog. It is a disposable prototype under `runs/` for checking schema shape, row counts, foreign keys, and safe statuses.

Run:

```bash
.venv/bin/python scripts/qsb_source_hub/source_hub_dry_run_loader.py \
  --repo-root . \
  --output-dir runs/QSB-GAP02A/source_hub_schema_dry_run_loader \
  --db runs/QSB-GAP02A/source_hub_schema_dry_run_loader/qsb_source_hub_dry_run.sqlite
```

GAP02C hardening run:

```bash
.venv/bin/python scripts/qsb_source_hub/source_hub_dry_run_loader.py \
  --repo-root . \
  --output-dir runs/QSB-GAP02C/source_hub_schema_hardening \
  --db runs/QSB-GAP02C/source_hub_schema_hardening/qsb_source_hub_hardened_dry_run.sqlite
```

GAP02C constrains `requires_human_review` to integer 0/1 values, constrains source relationships to the review vocabulary, uses `normalized_file_key` for file uniqueness per source object, and adds triggers that reject claim-flag or mart-candidate rows whose `source_file_id` belongs to a different source object.

Current limitation: metadata and fingerprints only. Source bodies are not loaded as evidence, PDFs are not OCR-processed, archives are not broadly extracted, and no canonical mart or result tables are created.

GAP01D should later use the Source Hub as the controlled reference point for M33 version-lineage review: scaffold, patch, generated cache entries, run logs, and mapping candidates should be resolved through Source Hub IDs before any reproduction planning.
