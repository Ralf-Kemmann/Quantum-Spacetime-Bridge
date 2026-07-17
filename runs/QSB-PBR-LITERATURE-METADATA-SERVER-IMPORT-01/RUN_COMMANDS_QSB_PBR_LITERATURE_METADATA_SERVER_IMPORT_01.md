# Run Commands

Run from repository root:

```bash
cd ~/Downloads/deBroglie_Kaster_Theorie/quantum-spacetime-bridge
```

Prepare/seed validation:

```bash
python runs/QSB-PBR-LITERATURE-METADATA-SERVER-IMPORT-01/scripts/prepare_literature_metadata_seed.py
```

Dry-run import after a human selects the DB target:

```bash
python runs/QSB-PBR-LITERATURE-METADATA-SERVER-IMPORT-01/scripts/import_literature_metadata.py \
  --db PATH_TO_APPROVED_DB \
  --seed runs/QSB-PBR-LITERATURE-METADATA-SERVER-IMPORT-01/data/literature_source_seed.csv \
  --mode dry-run
```

Execute import only after dry-run review:

```bash
python runs/QSB-PBR-LITERATURE-METADATA-SERVER-IMPORT-01/scripts/import_literature_metadata.py \
  --db PATH_TO_APPROVED_DB \
  --seed runs/QSB-PBR-LITERATURE-METADATA-SERVER-IMPORT-01/data/literature_source_seed.csv \
  --mode execute
```

Validate executed import:

```bash
python runs/QSB-PBR-LITERATURE-METADATA-SERVER-IMPORT-01/scripts/validate_literature_metadata_import.py \
  --db PATH_TO_APPROVED_DB
```

Repository checks:

```bash
git diff --check
git status --short --untracked-files=all
```

Do not commit or push automatically.
