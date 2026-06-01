# QSB-DB11 — Metadata Seed Specification and Metadata-Control Rules

Date: 2026-06-02  
Status: metadata seed specification  
Scope: QSB-wide research database infrastructure  
Upstream plan: QSB_DB10_METADATA_SEED_PLAN  
Database artifact baseline: runs/QSB-DB/QSB_DB06_EMPTY_DATABASE/qsb_research_empty.db  
Seed mode: metadata-only specification  
Raw artifact access: no raw artifact inspection by this note  
Physics-analysis status: closed for physical interpretation, residual search, and model fitting  
Tracking decision: this documentation note may be tracked; SQLite database artifacts remain run artifacts

## 1. Purpose

This note specifies the first metadata-only seed set for the QSB SQLite research database.

The focus is metadata control in a data-warehouse sense.

The seed must test repository lineage, document lineage, script lineage, table cataloging, PK/FK relation documentation, and claim-boundary defaults without inserting scientific data.

This note does not modify the database.

This note does not insert seed rows.

This note does not create SQL files.

This note does not create scripts.

This note does not inspect raw artifacts.

This note does not read TIM/PAR values.

This note does not analyze raw data.

The purpose is controlled metadata-lineage bootstrap, not scientific data ingestion.

## 2. Upstream state

The empty database artifact is:

runs/QSB-DB/QSB_DB06_EMPTY_DATABASE/qsb_research_empty.db

Known empty-database state:

- sqlite_validation_status = passed
- table_count = 25
- index_count = 98
- missing_tables = []
- user_row_count_total = 0
- non_empty_tables = {}
- seed_data_inserted = False

The database is empty.

The schema is visible and understandable in DB Browser for SQLite.

The database remains a run artifact and is not tracked.

## 3. Decision

Decision:

- next_scope = METADATA_SEED_SCRIPT
- next_step = QSB-DB12_METADATA_SEED_SCRIPT
- following_possible_step = QSB-DB13_METADATA_SEED_EXECUTION
- later_possible_step = QSB-DB14_METADATA_SEED_RESULT_NOTE
- allowed_scope = METADATA_ONLY_SEED_SPECIFICATION
- database_modification = FORBIDDEN_BY_THIS_NOTE
- seed_execution = FORBIDDEN_BY_THIS_NOTE
- raw_data_seed = FORBIDDEN
- raw_artifact_access = FORBIDDEN
- tim_par_value_reading = FORBIDDEN
- analytics_data_seed = FORBIDDEN
- physical_value_interpretation = FORBIDDEN
- residual_analysis_gate = CLOSED
- model_fitting_gate = CLOSED
- bridge_claim_gate = CLOSED
- research_status = RESEARCH_DATA_INFRASTRUCTURE_METADATA_CONTROL

The next step may create a metadata-seed script.

The execution of that script must remain a separate later block.

## 4. Metadata-control principle

The first seed is a metadata-control seed.

It may insert metadata about the project infrastructure.

It must not insert scientific measurement data.

It must not insert raw TIM/PAR values.

It must not insert raw artifact contents.

It must not insert C60 molecular values.

It must not insert analytics results.

It must not authorize physical interpretation.

The metadata seed is allowed only to test controlled lineage and audit logic.

Metadata control means:

- every seeded row has a known source of authority,
- every seeded row belongs to an allowed metadata domain,
- every seeded row respects FK order,
- every seeded row has a bounded claim status,
- unresolved fields remain explicitly unresolved,
- guessed values are forbidden,
- raw-data placeholders may not contain raw content,
- metadata is used to control lineage, not to make physical claims.

## 5. Baseline protection

The existing empty database should remain a stable baseline.

Do not modify:

runs/QSB-DB/QSB_DB06_EMPTY_DATABASE/qsb_research_empty.db

A later seed execution should create or copy into a new run artifact:

runs/QSB-DB/QSB_DB13_METADATA_SEED/qsb_research_metadata_seed.db

The metadata-seeded database should be separate from the empty baseline database.

The empty baseline remains useful for comparison, repeatability, and troubleshooting.

## 6. Allowed seed tables

The first metadata seed may use these tables:

1. repo_catalog
2. git_commit_catalog
3. project_file_catalog
4. document_catalog
5. script_catalog
6. table_catalog
7. run_catalog
8. run_output_catalog
9. pk_fk_relation_catalog
10. claim_boundary_catalog
11. raw_data_source as placeholder metadata only
12. raw_data as placeholder metadata only if explicitly needed and content-free

The first seed should prefer not to insert raw_data placeholder rows unless necessary for lineage testing.

If raw_data placeholder rows are used, they must remain content-free and measurement-free.

## 7. Forbidden seed tables and content

The first metadata seed must not insert content into raw-token or scientific-value layers.

Forbidden:

- raw_token_catalog rows containing raw tokens,
- field_catalog rows from parsed TIM/PAR values,
- raw TIM/PAR content,
- TIM/PAR parameter values,
- timing residuals,
- C60 coordinates,
- C60 graph values,
- molecular structure values,
- analytics outputs,
- model fit outputs,
- physical interpretation records,
- downloaded documentation content,
- imported raw CSV files,
- transformation results from scientific values.

The metadata seed may define that such tables exist.

It must not populate them with scientific data.

No raw TIM/PAR values should be inserted.

No raw data should be inserted.

## 8. FK-safe seed order

The first metadata seed must follow FK order.

Recommended order:

1. repo_catalog
2. git_commit_catalog
3. project_file_catalog
4. document_catalog
5. script_catalog
6. run_catalog
7. run_output_catalog
8. table_catalog
9. script_table_relation
10. document_table_relation
11. pk_fk_relation_catalog
12. claim_boundary_catalog
13. raw_data_source placeholder rows only if approved
14. raw_data placeholder rows only if approved

The seed script should run inside a transaction.

If any insert fails, the transaction should roll back.

## 9. Repo seed specification

Table:

repo_catalog

Planned row count:

- 1

Seed row:

- repo_name = quantum-spacetime-bridge
- repo_url = unresolved
- local_root_path = /home/ralf-kemmann/Downloads/deBroglie_Kaster_Theorie/quantum-spacetime-bridge
- default_branch = unresolved_unless_read_from_git
- project_area = QSB-wide
- repo_status = active
- notes = metadata seed; remote URL and branch must be captured from Git if used

Metadata-control rule:

Do not guess repo_url.

Do not guess default_branch.

A later script may read local Git metadata if needed.

## 10. Git commit seed specification

Table:

git_commit_catalog

Planned candidate commits:

- fd01ea7 | Add QSB SQLite DB Browser inspection result note
- fab3bbf | Add QSB SQLite DB Browser inspection plan
- 71a9c9c | Add QSB SQLite empty database inspection result note
- 86c32ca | Add QSB empty SQLite database creation script
- 1b515b6 | Add QSB SQLite empty database creation plan
- 7b52119 | Add QSB SQLite research database schema SQL
- 32bc8be | Add QSB SQLite research database schema spec
- 0a38fa5 | Add QSB research database repo lineage schema plan
- 641b35f | Add QSB-ST ShapiroInfo ETL harmonization method correction

Planned row count:

- up to 9

Metadata-control rule:

Commit metadata should preferably be captured from Git commands in the later seed script.

Hardcoded short hashes may be used only as expected candidates for verification.

If a commit is not present locally, the seed should report it as missing rather than inventing data.

## 11. Project file seed specification

Table:

project_file_catalog

Planned files:

- docs/QSB_DB01_RESEARCH_DATABASE_REPO_LINEAGE_SCHEMA_PLAN.md
- docs/QSB_DB02_SQLITE_SCHEMA_SPEC.md
- data/QSB-DB/schema/qsb_research_db_schema.sql
- docs/QSB_DB04_SQLITE_EMPTY_DATABASE_CREATION_PLAN.md
- scripts/qsb_db05_create_empty_sqlite_database.py
- docs/QSB_DB07_SQLITE_SCHEMA_INSPECTION_RESULT_NOTE.md
- docs/QSB_DB08_SQLITE_DB_BROWSER_INSPECTION_PLAN.md
- docs/QSB_DB09_SQLITE_DB_BROWSER_INSPECTION_EXECUTION_NOTE.md
- docs/QSB_DB10_METADATA_SEED_PLAN.md
- docs/QSB_ST_SHAPIROINFO74_METHOD_CORRECTION_ETL_HARMONIZATION_AND_TRANSFORMATION_VIEW_DECISION.md

Planned row count:

- 10

Metadata-control rule:

Only file metadata should be inserted.

File contents should not be inserted.

Checksums may be computed later by the seed script if implemented.

## 12. Document seed specification

Table:

document_catalog

Planned documents:

- QSB-DB01 schema plan
- QSB-DB02 SQLite schema specification
- QSB-DB04 empty database creation plan
- QSB-DB07 schema inspection result note
- QSB-DB08 DB Browser inspection plan
- QSB-DB09 DB Browser inspection execution note
- QSB-DB10 metadata seed plan
- SHAPIROINFO74 ETL harmonization method correction

Planned row count:

- 8

Metadata-control rule:

Document metadata only.

No document body text should be inserted.

## 13. Script seed specification

Table:

script_catalog

Planned scripts:

- scripts/qsb_db05_create_empty_sqlite_database.py

Planned row count:

- 1

Metadata-control rule:

Script metadata only.

Script source code should not be inserted.

## 14. Run seed specification

Table:

run_catalog

Planned runs:

- QSB-DB06_SQLITE_EMPTY_DATABASE_CREATION_EXECUTION

Planned row count:

- 1

Metadata-control rule:

Run metadata only.

The run may reference DB05 script and the appropriate commit if available.

No run output file contents should be inserted.

## 15. Run-output seed specification

Table:

run_output_catalog

Planned DB06 run outputs:

- runs/QSB-DB/QSB_DB06_EMPTY_DATABASE/qsb_research_empty.db
- runs/QSB-DB/QSB_DB06_EMPTY_DATABASE/sqlite_empty_database_config_resolved.json
- runs/QSB-DB/QSB_DB06_EMPTY_DATABASE/sqlite_empty_database_creation_summary.json
- runs/QSB-DB/QSB_DB06_EMPTY_DATABASE/sqlite_empty_database_fk_report.csv
- runs/QSB-DB/QSB_DB06_EMPTY_DATABASE/sqlite_empty_database_readout.md
- runs/QSB-DB/QSB_DB06_EMPTY_DATABASE/sqlite_empty_database_schema_indexes.csv
- runs/QSB-DB/QSB_DB06_EMPTY_DATABASE/sqlite_empty_database_schema_tables.csv

Planned row count:

- 7

Metadata-control rule:

Only output metadata may be inserted:

- path,
- output type,
- byte size,
- tracked status,
- optional checksum.

Do not insert file contents.

## 16. Table-catalog seed specification

Table:

table_catalog

Planned rows:

- 25 SQLite schema table names from the QSB research database.

Required table names:

- raw_data_source
- raw_data
- pk_fk_relation_catalog
- repo_catalog
- git_commit_catalog
- project_file_catalog
- document_catalog
- script_catalog
- run_catalog
- run_output_catalog
- table_catalog
- script_table_relation
- document_table_relation
- field_catalog
- raw_token_catalog
- etl_transformation_rule
- harmonized_value_view_catalog
- unit_dimension_catalog
- quantity_domain_catalog
- quantity_catalog
- transformation_rule_catalog
- audit_log
- quality_check_catalog
- quality_check_result
- claim_boundary_catalog

Metadata-control rule:

These rows describe schema objects.

They do not represent scientific table contents.

## 17. Script-table relation seed specification

Table:

script_table_relation

Planned relation rows:

- DB05 script creates empty database run outputs indirectly through QSB-DB06 execution.
- DB05 script validates schema table presence.
- DB05 script writes schema table inventory.
- DB05 script writes schema index inventory.
- DB05 script writes FK report.
- DB05 script writes summary JSON.
- DB05 script writes readout markdown.

Metadata-control rule:

Relations are metadata relationships, not scientific data relationships.

## 18. Document-table relation seed specification

Table:

document_table_relation

Planned relation rows:

- QSB-DB01 specifies initial database schema plan.
- QSB-DB02 specifies SQLite schema tables.
- QSB-DB03 schema SQL is represented in table_catalog metadata.
- QSB-DB07 documents empty database inspection outputs.
- QSB-DB10 specifies metadata seed plan.

Metadata-control rule:

Document-table relations describe documentation coverage and schema lineage only.

## 19. PK/FK relation-catalog seed specification

Table:

pk_fk_relation_catalog

The first seed should insert relation metadata for enforced foreign keys documented in QSB-DB10.

Planned row count:

- approximately 32 FK rows, matching the DB06 FK report.

Metadata-control rule:

This table documents relationships.

It does not create or modify the actual FK constraints.

## 20. Claim-boundary seed specification

Table:

claim_boundary_catalog

Default seed values for all infrastructure objects:

- physical_interpretation_allowed = 0
- residual_analysis_allowed = 0
- model_fitting_allowed = 0
- bridge_claim_allowed = 0
- value_reading_allowed = 0

Applies to:

- DB schema files,
- DB documentation files,
- DB scripts,
- empty DB run artifacts,
- metadata seed artifacts,
- run-output metadata,
- table-catalog metadata.

Metadata-control rule:

No seeded metadata object may authorize physical interpretation.

## 21. Source placeholder seed specification

Table:

raw_data_source

Allowed placeholder candidates:

- QSB-DB schema source
- QSB-DB empty database run artifact source
- ShapiroInfo public sources directory placeholder
- C60/carbon domain future placeholder

Planned rule:

Prefer source placeholders only where needed for provenance testing.

For `data/QSB-ST-SHAPIROINFO/public_sources/`:

- status = local_only / untracked
- raw_artifact_access_status = not_performed
- tim_par_value_reading_status = not_performed
- content_reading_status = not_performed

No raw_data rows should be inserted unless explicitly required by a later seed spec revision.

## 22. Row-count expectation

Expected approximate row counts for first metadata seed:

- repo_catalog: 1
- git_commit_catalog: up to 9
- project_file_catalog: 10
- document_catalog: 8
- script_catalog: 1
- run_catalog: 1
- run_output_catalog: 7
- table_catalog: 25
- pk_fk_relation_catalog: approximately 32
- claim_boundary_catalog: at least 1 group or object-level rows
- raw_data_source: optional placeholders only
- raw_data: preferably 0

Exact row counts may vary if the later script captures local Git metadata dynamically.

The seed result must report actual inserted counts.

## 23. Validation expectations

The later metadata seed execution must validate:

- FK integrity,
- no raw TIM/PAR values inserted,
- no raw artifact contents inserted,
- no scientific data inserted,
- no user rows in forbidden tables,
- claim-boundary defaults remain closed,
- seeded DB is separate from empty baseline DB,
- inserted counts match or explain expected counts,
- source placeholders remain content-free.

## 24. Output expectations for QSB-DB13

A later metadata seed execution should write:

- metadata_seed_summary.json
- metadata_seed_insert_counts.csv
- metadata_seed_table_row_counts.csv
- metadata_seed_fk_validation.csv
- metadata_seed_forbidden_content_check.csv
- metadata_seed_readout.md
- metadata_seed_config_resolved.json

The metadata-seeded DB should be written under:

runs/QSB-DB/QSB_DB13_METADATA_SEED/qsb_research_metadata_seed.db

The empty baseline DB should not be modified.

## 25. Stop conditions

The metadata seed route must stop if:

- the seed script would modify the empty baseline DB directly,
- raw data values would be inserted,
- TIM/PAR values would be inserted,
- C60 numeric/molecular values would be inserted,
- file contents would be inserted instead of file metadata,
- Git remote URLs would be guessed,
- FK integrity cannot be maintained,
- a seeded object would authorize physical interpretation,
- a row cannot be traced to a documented metadata source,
- a forbidden table would receive data,
- raw public sources would be inspected.

A stop condition is a valid technical result.

## 26. Claim boundary

This note specifies a metadata-only seed set and metadata-control rules.

It does not modify the SQLite database.

It does not insert data.

It does not create seed files.

It does not inspect raw artifacts.

It does not read TIM/PAR values.

It does not analyze raw data.

It does not provide evidence for a physical Shapiro-information residual.

It does not validate the QSB-ST Bridge.

It does not establish spacetime, quantum-gravity, relativistic, pulsar-timing, molecular-structure, or C60 physics claims.

It only specifies how later metadata-only seed rows may be inserted into a separate seeded database artifact for repository lineage, documentation lineage, script/run/output lineage, schema-object cataloging, PK/FK documentation, and claim-boundary control.
