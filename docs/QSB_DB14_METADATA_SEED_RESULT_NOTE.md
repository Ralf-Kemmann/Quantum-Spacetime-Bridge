# QSB-DB14 - Metadata Seed Result Note

Date: 2026-06-02
Status: metadata seed execution result documented
Upstream execution: QSB-DB13_METADATA_SEED_EXECUTION
Execution scope: metadata-only SQLite seed execution
Tracking decision: this documentation note may be tracked; generated databases and run outputs remain run artifacts first

## 1. Purpose

This note documents the QSB-DB13 metadata seed execution result.

The execution created a metadata-seeded SQLite research database from the empty baseline database by running the committed QSB-DB12 metadata seed script exactly once.

This note uses only the QSB-DB13 execution readout facts.

It does not execute SQL.

It does not insert seed data.

It does not inspect raw artifact contents.

It does not read TIM/PAR values.

It does not analyze raw data.

## 2. Execution command

The command used exactly once was:

```text
python scripts/qsb_db12_metadata_seed.py
```

The execution block was:

```text
QSB-DB13_METADATA_SEED_EXECUTION
```

## 3. Baseline and output database status

Before execution:

- baseline_db_exists=0
- metadata_seed_db_exists_before=1

The input baseline database was:

```text
runs/QSB-DB/QSB_DB06_EMPTY_DATABASE/qsb_research_empty.db
```

The output directory was:

```text
runs/QSB-DB/QSB_DB13_METADATA_SEED/
```

The output database was:

```text
runs/QSB-DB/QSB_DB13_METADATA_SEED/qsb_research_metadata_seed.db
```

The generated metadata-seeded SQLite database remains a run artifact.

## 4. Metadata seed result

The metadata seed summary reported:

- missing_required_outputs = []
- metadata_seed_status = completed
- baseline_db_modified = False
- output_db_created = True
- seed_execution_mode = metadata_only
- inserted_table_count = 13
- inserted_row_count_total = 130
- fk_validation_status = passed
- foreign_key_check_violations = []
- forbidden_content_check_status = passed
- raw_data_row_count = 0
- raw_token_row_count = 0
- field_catalog_scientific_row_count = 0

The empty baseline database was not modified.

## 5. Inserted metadata tables

The metadata-seeded database contained 25 user tables and 130 total user rows.

The non-empty metadata tables were:

- claim_boundary_catalog: 7
- document_catalog: 9
- document_table_relation: 11
- git_commit_catalog: 11
- pk_fk_relation_catalog: 32
- project_file_catalog: 12
- raw_data_source: 2
- repo_catalog: 1
- run_catalog: 1
- run_output_catalog: 7
- script_catalog: 2
- script_table_relation: 10
- table_catalog: 25

These rows are metadata seed rows only.

They do not contain raw data, TIM/PAR values, C60 values, analytics results, residuals, or model-fit outputs.

## 6. Output files

The QSB-DB13 execution produced the following run artifacts:

- qsb_research_metadata_seed.db: 610304 bytes
- metadata_seed_summary.json: 2067 bytes
- metadata_seed_insert_counts.csv: 309 bytes, 13 rows, header table_name,inserted_rows
- metadata_seed_table_row_counts.csv: 581 bytes, 25 rows, header table_name,row_count
- metadata_seed_fk_validation.csv: 41 bytes, 0 rows, header table_name,rowid,referenced_table,fk_id
- metadata_seed_forbidden_content_check.csv: 202 bytes, 5 rows, header check_name,status,detail
- metadata_seed_readout.md: 1826 bytes
- metadata_seed_config_resolved.json: 565 bytes

These files are run artifacts first.

They are not automatically tracked by this note.

## 7. Validation result

The baseline database validation reported:

- table_count = 25
- total user rows = 0
- non_empty_tables = {}
- FK violations = []

The metadata-seeded database validation reported:

- table_count = 25
- total user rows = 130
- FK violations = []

The SQLite foreign-key validation passed.

## 8. Forbidden-content result

The forbidden-content check passed.

The result confirms:

- no raw data rows were inserted
- no raw token rows were inserted
- no scientific field-catalog rows were inserted
- no TIM/PAR values were inserted or read
- no C60 values were inserted
- no analytics rows, residuals, or model-fit outputs were inserted

The seed execution remained metadata-only.

## 9. Repository and artifact boundary

Final git status after QSB-DB13 showed only:

```text
?? data/QSB-ST-SHAPIROINFO/public_sources/
```

This confirms that data/QSB-ST-SHAPIROINFO/public_sources/ remains local-only and untracked.

No files were staged.

No files were committed during QSB-DB13.

The metadata-seeded SQLite database was not staged.

The run outputs were not staged.

No documentation or data files were downloaded.

## 10. Technical interpretation

QSB-DB13 established that the empty SQLite research database can be copied into a metadata-seeded run artifact and populated with repository, document, script, table, run, relation, source, and claim-boundary metadata.

This is a database-infrastructure result.

It improves auditability of the research repository by adding metadata rows while preserving the boundary between metadata, raw data, and scientific interpretation.

It does not authorize physical interpretation.

## 11. Next practical step

A reasonable next block is:

```text
QSB-DB15_METADATA_SEED_DB_BROWSER_INSPECTION_PLAN
```

That next block should plan manual read-only inspection of the metadata-seeded database in DB Browser for SQLite.

The inspection should verify table visibility, row counts, relations, and metadata readability without modifying the database and without inserting raw data or scientific values.

## 12. Claim boundary

This note documents a metadata-only SQLite seed execution result.

This note does not provide evidence for a physical Shapiro-information residual.

This note does not validate the QSB-ST Bridge.

This note does not establish spacetime, quantum-gravity, relativistic, pulsar-timing, molecular-structure, or C60 physics claims.

No raw artifact contents were inspected.

No TIM/PAR values were read.

No documentation or data files were downloaded.

No raw data, TIM/PAR values, C60 values, analytics rows, residuals, or model-fit outputs were inserted.

Metadata seed rows do not authorize physical interpretation.
