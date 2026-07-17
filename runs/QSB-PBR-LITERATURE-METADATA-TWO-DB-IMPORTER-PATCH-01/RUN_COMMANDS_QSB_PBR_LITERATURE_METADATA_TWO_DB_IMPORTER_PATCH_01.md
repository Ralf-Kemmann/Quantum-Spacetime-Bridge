# Run Commands

Run from repository root:

```bash
cd ~/Downloads/deBroglie_Kaster_Theorie/quantum-spacetime-bridge
```

Required two-DB dry-run:

```bash
python runs/QSB-PBR-LITERATURE-METADATA-SERVER-IMPORT-01/scripts/import_literature_metadata.py \
  --data-db runs/QSB-DB/QSB_DB25_CONSOLIDATED_RESEARCH_SNAPSHOT/qsb_research_dwh_target_workcopy_dwh03.db \
  --metadata-db runs/QSB-META02/metadata_catalog_update/qsb_metadata_catalog_meta02.sqlite \
  --seed runs/QSB-PBR-LITERATURE-METADATA-SERVER-IMPORT-01/data/literature_source_seed.csv \
  --mode dry-run
```

Validate patch artifacts:

```bash
python runs/QSB-PBR-LITERATURE-METADATA-TWO-DB-IMPORTER-PATCH-01/scripts/validate_two_db_importer_patch.py
```

Deprecated compatibility dry-run:

```bash
python runs/QSB-PBR-LITERATURE-METADATA-SERVER-IMPORT-01/scripts/import_literature_metadata.py \
  --db /tmp/qsb_pbr_literature_compat_dryrun.sqlite \
  --seed runs/QSB-PBR-LITERATURE-METADATA-SERVER-IMPORT-01/data/literature_source_seed.csv \
  --mode dry-run
```

Required git checks:

```bash
git status --short --untracked-files=all
git diff --check
git diff -- runs/QSB-PBR-LITERATURE-METADATA-SERVER-IMPORT-01/scripts/import_literature_metadata.py
```

Do not run `--mode execute` against the real targets in this patch run.
