# Run Commands

Run from repository root:

```bash
cd ~/Downloads/deBroglie_Kaster_Theorie/quantum-spacetime-bridge
```

Read-only DB target inspection:

```bash
python runs/QSB-PBR-LITERATURE-METADATA-DB-TARGET-REVIEW-01/scripts/inspect_literature_metadata_db_targets.py
```

Review assessment:

```bash
sed -n '1,120p' runs/QSB-PBR-LITERATURE-METADATA-DB-TARGET-REVIEW-01/data/db_candidate_target_assessment.csv
```

Review two-DB recommendation:

```bash
sed -n '1,120p' runs/QSB-PBR-LITERATURE-METADATA-DB-TARGET-REVIEW-01/data/two_db_import_assessment.csv
```

Repository checks:

```bash
git diff --check
git status --short --untracked-files=all
```

After human review only:

```bash
git add -f runs/QSB-PBR-LITERATURE-METADATA-DB-TARGET-REVIEW-01
```

Do not run an import and do not use `--mode execute` from this review package.
