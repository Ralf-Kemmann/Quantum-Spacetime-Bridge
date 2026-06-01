# QSB-DB10 — Metadata Seed Plan

Date: 2026-06-02  
Status: metadata seed plan  
Scope: QSB-wide research database infrastructure  
Upstream result: QSB_DB09_SQLITE_DB_BROWSER_INSPECTION_EXECUTION_NOTE  
Database artifact: runs/QSB-DB/QSB_DB06_EMPTY_DATABASE/qsb_research_empty.db  
Seed mode: metadata-only planning  
Raw artifact access: no raw artifact inspection by this note  
Physics-analysis status: closed for physical interpretation, residual search, and model fitting  
Tracking decision: this documentation note may be tracked; the SQLite database remains a run artifact

## 1. Purpose

This note defines the first metadata-only seed plan for the QSB SQLite research database.

The database has already been created as an empty schema-only run artifact and inspected both automatically and manually.

The next step is to plan which metadata records may later be inserted in a controlled seed execution.

This note does not modify the database.

This note does not insert seed rows.

This note does not create SQL files.

This note does not create scripts.

This note does not inspect raw artifacts.

This note does not read TIM/PAR values.

This note does not analyze raw data.

The purpose is to prepare controlled metadata lineage, not scientific data ingestion.

## 2. Upstream state

The empty database artifact is:

runs/QSB-DB/QSB_DB06_EMPTY_DATABASE/qsb_research_empty.db

Known state:

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

- next_scope = METADATA_SEED_SPEC
- next_step = QSB-DB11_METADATA_SEED_SPEC
- following_possible_step = QSB-DB12_METADATA_SEED_SCRIPT
- later_possible_step = QSB-DB13_METADATA_SEED_EXECUTION
- allowed_scope = METADATA_ONLY_SEED_PLANNING
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
- research_status = RESEARCH_DATA_INFRASTRUCTURE_METADATA_PLANNING

The next step should specify metadata-only seed rows.

The execution of those seed rows must remain a separate later block.

## 4. Allowed metadata seed domains

The first metadata seed may include only project/control metadata.

Allowed seed domains:

1. Repository metadata
2. Git commit metadata
3. Project file metadata
4. Document metadata
5. Script metadata
6. Table/catalog metadata
7. Run-output metadata as metadata only
8. PK/FK relation-catalog metadata
9. Claim-boundary metadata
10. Source placeholder metadata without raw content

No scientific raw data may be inserted.

No TIM/PAR values may be inserted.

No C60 molecular values may be inserted.

No analytics values may be inserted.

No raw TIM/PAR values should be inserted.

No raw data should be inserted.

## 5. Planned seed tables

The metadata-only seed should plan records for:

- repo_catalog
- git_commit_catalog
- project_file_catalog
- document_catalog
- script_catalog
- table_catalog
- run_catalog, only if representing already documented infrastructure runs as metadata
- run_output_catalog, only as file/output metadata
- pk_fk_relation_catalog
- claim_boundary_catalog
- raw_data_source, only for source/datapot placeholder metadata
- raw_data, only if representing artifact-level placeholders without reading raw contents

The first actual execution should remain conservative.

If raw_data placeholder rows are used, they must not contain raw content, parsed values, TIM/PAR values, or measurement values.

## 6. Seed exclusion rules

Forbidden in the first metadata seed:

- raw TIM/PAR content,
- TIM/PAR values,
- raw artifact text,
- parsed measurement rows,
- C60 coordinate values,
- molecular graph values,
- analytics outputs,
- residuals,
- model fit outputs,
- physical interpretation records,
- downloaded documentation content,
- imported CSV/raw files,
- transformation results from scientific values.

This seed plan is about project lineage and infrastructure metadata only.

## 7. Initial repo metadata plan

The first seed should include one `repo_catalog` record for the local QSB repository.

Planned fields:

- repo_name = quantum-spacetime-bridge
- local_root_path = /home/ralf-kemmann/Downloads/deBroglie_Kaster_Theorie/quantum-spacetime-bridge
- project_area = QSB-wide
- repo_status = active

The remote URL should be inserted only if confirmed from local Git metadata or explicitly supplied.

Do not guess remote URLs.

## 8. Initial commit metadata plan

The first seed may include selected recent commits documented in the workflow.

Candidate commits:

- fd01ea7 Add QSB SQLite DB Browser inspection result note
- fab3bbf Add QSB SQLite DB Browser inspection plan
- 71a9c9c Add QSB SQLite empty database inspection result note
- 86c32ca Add QSB empty SQLite database creation script
- 1b515b6 Add QSB SQLite empty database creation plan
- 7b52119 Add QSB SQLite research database schema SQL
- 32bc8be Add QSB SQLite research database schema spec
- 0a38fa5 Add QSB research database repo lineage schema plan
- 641b35f Add QSB-ST ShapiroInfo ETL harmonization method correction

If commit metadata is inserted later, it should be captured from Git rather than copied manually where possible.

## 9. Initial project file metadata plan

The first seed may include metadata for these tracked files:

- docs/QSB_DB01_RESEARCH_DATABASE_REPO_LINEAGE_SCHEMA_PLAN.md
- docs/QSB_DB02_SQLITE_SCHEMA_SPEC.md
- data/QSB-DB/schema/qsb_research_db_schema.sql
- docs/QSB_DB04_SQLITE_EMPTY_DATABASE_CREATION_PLAN.md
- scripts/qsb_db05_create_empty_sqlite_database.py
- docs/QSB_DB07_SQLITE_SCHEMA_INSPECTION_RESULT_NOTE.md
- docs/QSB_DB08_SQLITE_DB_BROWSER_INSPECTION_PLAN.md
- docs/QSB_DB09_SQLITE_DB_BROWSER_INSPECTION_EXECUTION_NOTE.md
- docs/QSB_ST_SHAPIROINFO74_METHOD_CORRECTION_ETL_HARMONIZATION_AND_TRANSFORMATION_VIEW_DECISION.md

File metadata may include:

- file path,
- file name,
- file type,
- project role,
- tracking status,
- created by block,
- checksum if computed later,
- notes.

No file contents need to be inserted in this seed.

## 10. Initial document metadata plan

The first seed may include document records for QSB-DB01 through QSB-DB09 and the SHAPIROINFO74 method-correction note.

Document metadata may include:

- document title,
- document type,
- qsb_block_id,
- upstream block,
- downstream block,
- status,
- claim-boundary level,
- tracking decision.

Document content itself should not be inserted.

## 11. Initial script metadata plan

The first seed may include a script record for:

- scripts/qsb_db05_create_empty_sqlite_database.py

Script metadata may include:

- script name,
- script path,
- script language = python,
- execution_allowed_status,
- purpose,
- claim boundary.

Script source code content should not be inserted.

## 12. Initial table metadata plan

The first seed may include table_catalog records for the 25 SQLite schema tables as database objects.

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

These records describe schema objects, not scientific table contents.

## 13. Initial PK/FK relation metadata plan

The first seed should include relation-catalog records for enforced foreign keys.

At minimum, include core relations such as:

- raw_data.raw_data_source_id -> raw_data_source.raw_data_source_id
- git_commit_catalog.repo_id -> repo_catalog.repo_id
- project_file_catalog.repo_id -> repo_catalog.repo_id
- project_file_catalog.commit_id -> git_commit_catalog.commit_id
- document_catalog.project_file_id -> project_file_catalog.project_file_id
- script_catalog.project_file_id -> project_file_catalog.project_file_id
- run_catalog.script_id -> script_catalog.script_id
- run_catalog.repo_id -> repo_catalog.repo_id
- run_catalog.commit_id -> git_commit_catalog.commit_id
- run_output_catalog.run_id -> run_catalog.run_id
- run_output_catalog.project_file_id -> project_file_catalog.project_file_id
- table_catalog.created_by_script_id -> script_catalog.script_id
- table_catalog.created_by_run_id -> run_catalog.run_id
- table_catalog.source_raw_data_id -> raw_data.raw_data_id
- script_table_relation.script_id -> script_catalog.script_id
- script_table_relation.table_id -> table_catalog.table_id
- script_table_relation.run_id -> run_catalog.run_id
- script_table_relation.commit_id -> git_commit_catalog.commit_id
- document_table_relation.document_id -> document_catalog.document_id
- document_table_relation.table_id -> table_catalog.table_id
- field_catalog.table_id -> table_catalog.table_id
- field_catalog.raw_data_id -> raw_data.raw_data_id
- raw_token_catalog.raw_data_id -> raw_data.raw_data_id
- raw_token_catalog.field_id -> field_catalog.field_id
- etl_transformation_rule.source_field_id -> field_catalog.field_id
- harmonized_value_view_catalog.created_by_run_id -> run_catalog.run_id
- quantity_catalog.quantity_domain_id -> quantity_domain_catalog.quantity_domain_id
- transformation_rule_catalog.target_quantity_id -> quantity_catalog.quantity_id
- quality_check_result.quality_check_id -> quality_check_catalog.quality_check_id
- quality_check_result.raw_data_id -> raw_data.raw_data_id
- quality_check_result.table_id -> table_catalog.table_id
- quality_check_result.run_id -> run_catalog.run_id

These rows document the database structure itself.

They do not represent scientific data.

## 14. Initial claim-boundary metadata plan

The first seed should include claim-boundary records for infrastructure objects.

Default claim-boundary seed values:

- physical_interpretation_allowed = 0
- residual_analysis_allowed = 0
- model_fitting_allowed = 0
- bridge_claim_allowed = 0
- value_reading_allowed = 0

These defaults apply to:

- DB schema files,
- DB documentation files,
- empty DB run artifacts,
- metadata seed artifacts,
- infrastructure scripts.

No seeded metadata object may authorize physical interpretation.

## 15. Source placeholder plan

A later metadata seed may include source placeholders such as:

- ShapiroInfo public sources directory,
- QSB-DB schema source,
- C60/carbon domain placeholder.

However, source placeholder rows must not contain raw data values or raw file contents.

For `data/QSB-ST-SHAPIROINFO/public_sources/`, source status should remain local-only / untracked unless a later decision changes it.

## 16. Output expectations for later QSB-DB13

A later metadata seed execution should write run outputs such as:

- metadata_seed_summary.json
- metadata_seed_insert_counts.csv
- metadata_seed_table_row_counts.csv
- metadata_seed_fk_validation.csv
- metadata_seed_readout.md
- metadata_seed_config_resolved.json

The DB file may be copied or created under a new run directory for seeded metadata, rather than modifying the original empty DB artifact directly.

The original empty DB should remain a stable baseline.

## 17. Stop conditions

The metadata seed route must stop if:

- the seed plan tries to insert raw data,
- the seed plan tries to insert TIM/PAR values,
- the seed plan tries to insert parsed measurement values,
- the seed plan tries to insert downloaded documentation content,
- the seed plan tries to authorize physical interpretation,
- the seed plan uses guessed GitHub remote URLs,
- foreign-key order is not controlled,
- seeded rows cannot be traced to documented metadata sources,
- the original empty DB artifact would be modified without explicit decision.

A stop condition is a valid technical result.

## 18. Claim boundary

This note defines a metadata-only seed plan.

It does not modify the SQLite database.

It does not insert data.

It does not create seed files.

It does not inspect raw artifacts.

It does not read TIM/PAR values.

It does not analyze raw data.

It does not provide evidence for a physical Shapiro-information residual.

It does not validate the QSB-ST Bridge.

It does not establish spacetime, quantum-gravity, relativistic, pulsar-timing, or molecular-structure physics claims.

It only plans controlled insertion of project, repository, schema, document, script, relation, and claim-boundary metadata into a later seeded research database artifact.
