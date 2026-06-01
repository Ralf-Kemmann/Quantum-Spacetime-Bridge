# QSB-DB01 — Research Database, Repository Lineage, and Schema Plan

Date: 2026-06-02  
Status: schema plan  
Scope: QSB-wide research-data infrastructure  
Database target: SQLite first, portable to larger relational systems later  
Repo mode: documentation-only planning block  
Raw artifact access: no raw artifact inspection by this note  
Physics-analysis status: closed for physical interpretation, residual search, and model fitting  
Tracking decision: this documentation note may be tracked; raw artifacts remain local-only and untracked

## 1. Purpose

This note defines the first QSB-wide research database schema plan.

The purpose is to move from loose CSV files, notes, scripts, and run folders toward an audit-capable research-data backbone.

The database is intended to support:

- source and provenance tracking,
- raw-data staging,
- repository and GitHub lineage,
- script/table/document/run relationships,
- PK/FK relation documentation,
- ETL and harmonization rules,
- quarantine and preservation of problematic data,
- blind-descriptive data views,
- later analytics,
- future transformation views between theory-domain quantities.

This database is not an interpretation engine.

It is not a preselection engine.

It is not a physical-claim engine.

It is a research-data control, lineage, harmonization, and audit layer.

## 2. Method position

The database follows the SHAPIROINFO74 method correction.

The documentation track remains important as an interpretation safeguard.

The ETL/harmonization track is required for real-data handling.

The transformation-view track is required for later cross-domain value mapping.

The measurement remains primary.

Gates, notes, schemas, and documentation layers are safeguards.

They are not authorities over what may be observed.

Harmonization is allowed for comparability.

Preselection for expectation-fitting is forbidden.

Quarantine is preservation, not deletion.

The raw-data layer is not an analytics table.

It is an audit-safe staging and lineage layer.

## 3. Database target

The first implementation target should be SQLite.

SQLite is suitable because it is:

- lightweight,
- file-based,
- repo-adjacent,
- easy to inspect with DB Browser for SQLite,
- scriptable through Python,
- capable of primary keys, foreign keys, indexes, views, and constraints,
- portable to PostgreSQL or larger relational systems later.

This plan does not create a database file.

A later block may create:

- schema SQL,
- SQLite initialization script,
- validation queries,
- example seed data,
- DB Browser inspection notes.

## 4. Core architecture

The research database should follow this conceptual flow:

1. raw_data_source  
2. raw_data / staging entry  
3. field and raw-token catalogs  
4. ETL / harmonization rules  
5. harmonized tables and blind-descriptive views  
6. run and output lineage  
7. document and script lineage  
8. transformation-view layer  
9. later analytics  
10. later interpretation gate

The important boundary is:

Data may enter the raw/staging layer before harmonization.

Only controlled and harmonized data may enter analytics views.

Problematic data are quarantined and preserved, not deleted.

## 5. Required table: raw_data_source

Purpose:

Track the source, origin, datapot, release, provider, and provenance state of incoming data.

This table answers:

Where did the data come from?

Suggested fields:

- raw_data_source_id INTEGER PRIMARY KEY
- source_name TEXT NOT NULL
- source_type TEXT NOT NULL
- provider_or_project TEXT
- source_url_or_path TEXT
- source_release TEXT
- source_version TEXT
- source_access_date TEXT
- source_download_status TEXT
- source_reachability_status TEXT
- source_corruption_status TEXT
- checksum_status TEXT
- license_or_usage_note TEXT
- provenance_confidence TEXT
- quarantine_status TEXT
- notes TEXT

Allowed source_reachability_status examples:

- reachable
- unreachable
- access_denied
- unresolved

Allowed source_corruption_status examples:

- not_checked
- no_external_corruption_detected
- externally_corrupted
- checksum_failed
- format_unreadable
- incomplete
- unresolved

## 6. Required table: raw_data

Purpose:

Serve as the controlled raw-data / staging entry table.

This table is the database door.

It is not an analytics table.

It preserves source-aware lineage and controls whether records may proceed into harmonized tables.

Suggested fields:

- raw_data_id INTEGER PRIMARY KEY
- raw_data_source_id INTEGER NOT NULL
- raw_artifact_id TEXT
- source_local_file_id TEXT
- source_local_record_id TEXT
- source_local_measurement_id TEXT
- source_record_hash TEXT
- raw_record_position TEXT
- raw_object_type TEXT
- raw_file_type TEXT
- raw_ingest_status TEXT
- raw_parse_status TEXT
- raw_quality_status TEXT
- blank_check_status TEXT
- special_character_check_status TEXT
- datatype_check_status TEXT
- unit_detection_status TEXT
- scale_detection_status TEXT
- harmonization_status TEXT
- etl_release_status TEXT
- quarantine_status TEXT
- quarantine_reason TEXT
- retry_possible INTEGER
- notes TEXT
- FOREIGN KEY raw_data_source_id REFERENCES raw_data_source(raw_data_source_id)

The schema should also support a source-aware unique lineage key, for example:

UNIQUE(raw_data_source_id, source_local_file_id, source_local_record_id)

or, when artifacts are explicitly modeled:

UNIQUE(raw_data_source_id, raw_artifact_id, source_local_record_id)

The exact uniqueness rule should be finalized in a later schema specification.

## 7. Raw-data status principle

The raw-data layer must preserve records.

Problematic records should not be silently discarded.

Allowed statuses should include:

- raw_only
- parsed
- harmonization_ready
- harmonized
- quarantined
- rejected_technical
- unresolved

Quarantined means preserved but not released into analytics.

Rejected_technical means not analytics-ready because a documented technical condition failed.

It does not mean deleted.

Every quarantine or technical rejection must carry a reason.

## 8. Required table: pk_fk_relation_catalog

Purpose:

Document enforced and logical table relationships.

This makes the database model auditable and reviewable.

Suggested fields:

- relation_id INTEGER PRIMARY KEY
- source_table TEXT NOT NULL
- source_column TEXT NOT NULL
- target_table TEXT NOT NULL
- target_column TEXT NOT NULL
- relation_type TEXT NOT NULL
- cardinality TEXT
- constraint_name TEXT
- is_enforced INTEGER NOT NULL
- is_logical_only INTEGER NOT NULL
- join_rule TEXT
- validity_condition TEXT
- audit_relevance TEXT
- notes TEXT

This table should document relations such as:

- raw_data.raw_data_source_id -> raw_data_source.raw_data_source_id
- field_catalog.raw_data_id -> raw_data.raw_data_id
- etl_transformation_rule.source_field_id -> field_catalog.field_id
- harmonized_value.raw_data_id -> raw_data.raw_data_id
- script_table_relation.script_id -> script_catalog.script_id
- script_table_relation.table_id -> table_catalog.table_id
- document_table_relation.document_id -> document_catalog.document_id
- document_table_relation.table_id -> table_catalog.table_id

## 9. Repository and GitHub lineage tables

The database should include repository lineage.

This allows the project to answer:

Which commit, script, note, and run generated or documented a table?

### repo_catalog

Suggested fields:

- repo_id INTEGER PRIMARY KEY
- repo_name TEXT NOT NULL
- repo_url TEXT
- local_root_path TEXT
- default_branch TEXT
- project_area TEXT
- repo_status TEXT
- notes TEXT

### git_commit_catalog

Suggested fields:

- commit_id INTEGER PRIMARY KEY
- repo_id INTEGER NOT NULL
- commit_hash TEXT NOT NULL
- short_hash TEXT
- commit_message TEXT
- commit_author TEXT
- commit_date TEXT
- branch_name TEXT
- tag_name TEXT
- is_clean_state INTEGER
- git_status_snapshot TEXT
- notes TEXT
- FOREIGN KEY repo_id REFERENCES repo_catalog(repo_id)

A uniqueness constraint should prevent duplicate commits for a repo:

UNIQUE(repo_id, commit_hash)

## 10. Project file and document tables

### project_file_catalog

Purpose:

Track project files in the repository or run output areas.

Suggested fields:

- project_file_id INTEGER PRIMARY KEY
- repo_id INTEGER
- commit_id INTEGER
- file_path TEXT NOT NULL
- file_name TEXT
- file_type TEXT
- project_role TEXT
- tracking_status TEXT
- created_by_block TEXT
- modified_by_block TEXT
- checksum TEXT
- notes TEXT
- FOREIGN KEY repo_id REFERENCES repo_catalog(repo_id)
- FOREIGN KEY commit_id REFERENCES git_commit_catalog(commit_id)

Allowed project_role examples:

- script
- documentation_note
- decision_note
- plan
- spec
- result_note
- input_data
- run_output
- schema
- config
- visual
- unknown

### document_catalog

Purpose:

Track notes, specs, plans, result notes, handoff notes, and public/private documents.

Suggested fields:

- document_id INTEGER PRIMARY KEY
- project_file_id INTEGER NOT NULL
- document_title TEXT
- document_type TEXT
- qsb_block_id TEXT
- upstream_block TEXT
- downstream_block TEXT
- status TEXT
- claim_boundary_level TEXT
- tracking_decision TEXT
- notes TEXT
- FOREIGN KEY project_file_id REFERENCES project_file_catalog(project_file_id)

Allowed document_type examples:

- decision_note
- plan
- spec
- result_note
- red_team_pack
- handoff
- public_note
- private_note
- unknown

## 11. Script, run, output, and table lineage

### script_catalog

Purpose:

Track scripts as executable research objects.

Suggested fields:

- script_id INTEGER PRIMARY KEY
- project_file_id INTEGER NOT NULL
- script_name TEXT
- script_path TEXT
- script_language TEXT
- execution_allowed_status TEXT
- last_known_commit_hash TEXT
- purpose TEXT
- claim_boundary TEXT
- notes TEXT
- FOREIGN KEY project_file_id REFERENCES project_file_catalog(project_file_id)

### run_catalog

Purpose:

Track controlled script executions.

Suggested fields:

- run_id INTEGER PRIMARY KEY
- run_block TEXT
- script_id INTEGER
- repo_id INTEGER
- commit_id INTEGER
- run_timestamp TEXT
- execution_mode TEXT
- output_root TEXT
- run_status TEXT
- git_status_before TEXT
- git_status_after TEXT
- raw_access_status TEXT
- download_status TEXT
- value_reading_status TEXT
- claim_boundary_status TEXT
- notes TEXT
- FOREIGN KEY script_id REFERENCES script_catalog(script_id)
- FOREIGN KEY repo_id REFERENCES repo_catalog(repo_id)
- FOREIGN KEY commit_id REFERENCES git_commit_catalog(commit_id)

### run_output_catalog

Purpose:

Track files created by a run.

Suggested fields:

- run_output_id INTEGER PRIMARY KEY
- run_id INTEGER NOT NULL
- project_file_id INTEGER
- output_path TEXT
- output_type TEXT
- byte_size INTEGER
- row_count INTEGER
- checksum TEXT
- tracked_status TEXT
- notes TEXT
- FOREIGN KEY run_id REFERENCES run_catalog(run_id)
- FOREIGN KEY project_file_id REFERENCES project_file_catalog(project_file_id)

### table_catalog

Purpose:

Track SQLite tables, CSV tables, JSON summaries, markdown readouts, views, and external table-like artifacts.

Suggested fields:

- table_id INTEGER PRIMARY KEY
- table_name TEXT NOT NULL
- table_type TEXT
- storage_type TEXT
- storage_path TEXT
- schema_status TEXT
- row_count INTEGER
- column_count INTEGER
- created_by_script_id INTEGER
- created_by_run_id INTEGER
- source_raw_data_id INTEGER
- notes TEXT
- FOREIGN KEY created_by_script_id REFERENCES script_catalog(script_id)
- FOREIGN KEY created_by_run_id REFERENCES run_catalog(run_id)
- FOREIGN KEY source_raw_data_id REFERENCES raw_data(raw_data_id)

Allowed storage_type examples:

- sqlite_table
- csv_file
- json_summary
- markdown_readout
- external_table
- view

## 12. Script-table and document-table relations

### script_table_relation

Purpose:

Link scripts to the tables or table-like artifacts they read, create, validate, export, or document.

Suggested fields:

- script_table_relation_id INTEGER PRIMARY KEY
- script_id INTEGER NOT NULL
- table_id INTEGER NOT NULL
- relation_type TEXT NOT NULL
- operation_type TEXT
- run_id INTEGER
- commit_id INTEGER
- notes TEXT
- FOREIGN KEY script_id REFERENCES script_catalog(script_id)
- FOREIGN KEY table_id REFERENCES table_catalog(table_id)
- FOREIGN KEY run_id REFERENCES run_catalog(run_id)
- FOREIGN KEY commit_id REFERENCES git_commit_catalog(commit_id)

Allowed relation_type examples:

- creates
- reads
- updates
- validates
- exports
- documents
- depends_on

Allowed operation_type examples:

- read_only
- write_output
- schema_create
- etl_transform
- validation
- summary

### document_table_relation

Purpose:

Link documents and notes to the tables they specify, document, review, summarize, or validate.

Suggested fields:

- document_table_relation_id INTEGER PRIMARY KEY
- document_id INTEGER NOT NULL
- table_id INTEGER NOT NULL
- relation_type TEXT
- notes TEXT
- FOREIGN KEY document_id REFERENCES document_catalog(document_id)
- FOREIGN KEY table_id REFERENCES table_catalog(table_id)

Allowed relation_type examples:

- documents
- summarizes
- specifies
- reviews
- validates
- claim_boundary_for

## 13. Field and value modeling

### field_catalog

Purpose:

Track fields/columns discovered in raw, staged, harmonized, or external tables.

Suggested fields:

- field_id INTEGER PRIMARY KEY
- table_id INTEGER
- raw_data_id INTEGER
- field_name TEXT
- field_position INTEGER
- raw_type TEXT
- inferred_type TEXT
- harmonized_type TEXT
- semantic_status TEXT
- correction_state_relevance TEXT
- unit_status TEXT
- scale_status TEXT
- missingness_status TEXT
- notes TEXT
- FOREIGN KEY table_id REFERENCES table_catalog(table_id)
- FOREIGN KEY raw_data_id REFERENCES raw_data(raw_data_id)

### raw_token_catalog

Purpose:

Optionally preserve raw token-level observations without interpreting them physically.

Suggested fields:

- raw_token_id INTEGER PRIMARY KEY
- raw_data_id INTEGER NOT NULL
- field_id INTEGER
- source_local_record_id TEXT
- raw_token TEXT
- token_position TEXT
- token_type_guess TEXT
- parse_status TEXT
- quarantine_status TEXT
- notes TEXT
- FOREIGN KEY raw_data_id REFERENCES raw_data(raw_data_id)
- FOREIGN KEY field_id REFERENCES field_catalog(field_id)

## 14. ETL and harmonization tables

### etl_transformation_rule

Purpose:

Store documented transformations, casts, mappings, unit harmonization rules, scale rules, and missing-value rules.

Suggested fields:

- etl_rule_id INTEGER PRIMARY KEY
- rule_name TEXT
- rule_type TEXT
- source_field_id INTEGER
- target_field_name TEXT
- transformation_expression TEXT
- cast_rule TEXT
- mapping_rule TEXT
- unit_before TEXT
- unit_after TEXT
- scale_rule TEXT
- missing_value_rule TEXT
- blank_handling_rule TEXT
- special_character_rule TEXT
- provenance_status TEXT
- reversible_flag INTEGER
- allowed_for_analytics INTEGER
- notes TEXT
- FOREIGN KEY source_field_id REFERENCES field_catalog(field_id)

Allowed rule_type examples:

- cast
- mapping
- unit_harmonization
- scale_normalization
- missing_value_handling
- blank_handling
- special_character_cleanup
- file_format_normalization

### harmonized_value_view_catalog

Purpose:

Document harmonized blind-descriptive views.

Suggested fields:

- view_id INTEGER PRIMARY KEY
- view_name TEXT NOT NULL
- view_type TEXT
- source_table_ids TEXT
- transformation_rule_set TEXT
- blind_descriptive_status TEXT
- interpretation_status TEXT
- created_by_run_id INTEGER
- notes TEXT
- FOREIGN KEY created_by_run_id REFERENCES run_catalog(run_id)

No harmonized value view may be treated as a physical interpretation view unless a later interpretation gate permits it.

## 15. Unit, dimension, and quantity transformation tables

### unit_dimension_catalog

Purpose:

Track units, SI units, dimensions, and conversion rules.

Suggested fields:

- unit_id INTEGER PRIMARY KEY
- unit_symbol TEXT
- si_unit TEXT
- dimension_expression TEXT
- conversion_rule TEXT
- source_status TEXT
- notes TEXT

### quantity_domain_catalog

Purpose:

Track theoretical or data-domain sides.

Suggested fields:

- quantity_domain_id INTEGER PRIMARY KEY
- domain_name TEXT
- domain_type TEXT
- description TEXT
- notes TEXT

Examples:

- de_broglie_side
- relativity_side
- timing_data_side
- carbon_structure_side
- bridge_mapping_side

### quantity_catalog

Purpose:

Track quantities that may be linked through transformation rules.

Suggested fields:

- quantity_id INTEGER PRIMARY KEY
- quantity_domain_id INTEGER
- symbol TEXT
- quantity_name TEXT
- si_unit TEXT
- dimension_expression TEXT
- observer_dependence TEXT
- primitive_or_derived TEXT
- description TEXT
- notes TEXT
- FOREIGN KEY quantity_domain_id REFERENCES quantity_domain_catalog(quantity_domain_id)

### transformation_rule_catalog

Purpose:

Track functional rules connecting quantities across domains.

Suggested fields:

- transformation_rule_id INTEGER PRIMARY KEY
- rule_name TEXT
- source_quantity_ids TEXT
- target_quantity_id INTEGER
- formula_expression TEXT
- required_constants TEXT
- validity_conditions TEXT
- unit_check_status TEXT
- invertible_flag INTEGER
- direction TEXT
- assumption_level TEXT
- source_status TEXT
- claim_boundary TEXT
- notes TEXT
- FOREIGN KEY target_quantity_id REFERENCES quantity_catalog(quantity_id)

This supports transformation views such as representing quantities from one theoretical domain through quantities from another domain.

This is a data-model / mapping-layer concept, not a physical validation claim.

## 16. Audit and quality tables

### audit_log

Purpose:

Track significant DB actions, ETL releases, quarantines, transformations, and schema changes.

Suggested fields:

- audit_id INTEGER PRIMARY KEY
- action_type TEXT
- object_type TEXT
- object_id TEXT
- related_rule_id TEXT
- timestamp TEXT
- actor TEXT
- status TEXT
- notes TEXT

### quality_check_catalog

Purpose:

Define reusable data-quality checks.

Suggested fields:

- quality_check_id INTEGER PRIMARY KEY
- check_name TEXT
- check_type TEXT
- target_table TEXT
- target_field TEXT
- check_expression TEXT
- severity TEXT
- stop_if_failed INTEGER
- notes TEXT

### quality_check_result

Purpose:

Store check results.

Suggested fields:

- quality_check_result_id INTEGER PRIMARY KEY
- quality_check_id INTEGER NOT NULL
- raw_data_id INTEGER
- table_id INTEGER
- run_id INTEGER
- result_status TEXT
- result_detail TEXT
- timestamp TEXT
- notes TEXT
- FOREIGN KEY quality_check_id REFERENCES quality_check_catalog(quality_check_id)
- FOREIGN KEY raw_data_id REFERENCES raw_data(raw_data_id)
- FOREIGN KEY table_id REFERENCES table_catalog(table_id)
- FOREIGN KEY run_id REFERENCES run_catalog(run_id)

## 17. Claim-boundary tables

### claim_boundary_catalog

Purpose:

Record permitted and forbidden claim levels for artifacts, tables, runs, documents, and views.

Suggested fields:

- claim_boundary_id INTEGER PRIMARY KEY
- object_type TEXT
- object_id TEXT
- claim_level TEXT
- physical_interpretation_allowed INTEGER
- residual_analysis_allowed INTEGER
- model_fitting_allowed INTEGER
- bridge_claim_allowed INTEGER
- value_reading_allowed INTEGER
- notes TEXT

This helps enforce that research artifacts cannot silently inflate into physical claims.

## 18. C60 and future domain portability

The database should not be ShapiroInfo-only.

It should be QSB-wide.

Future domains may include:

- ShapiroInfo / pulsar timing data,
- C60 / carbon scaffold data,
- molecular graph data,
- simulation outputs,
- relational-structure diagnostics,
- public documentation metadata,
- transformation-view quantities.

Domain-specific tables may be added later.

The core lineage and ETL framework should remain shared.

## 19. Constraints and rules

The database should enforce or document these principles:

- no analytics release without ETL status,
- no harmonized view without documented transformation rules,
- no transformation without source/provenance status,
- no deletion of problematic records without audit log,
- quarantine means preservation, not deletion,
- no physical interpretation unless claim boundary allows it,
- no residual analysis unless explicitly gated,
- no model fitting unless explicitly gated,
- no Bridge claim unless explicitly gated,
- no source-to-analytics jump without raw_data lineage.

## 20. Suggested first implementation sequence

A later implementation should proceed in small blocks:

1. DB02 schema SQL plan.
2. DB03 SQLite schema creation script.
3. DB04 create empty SQLite database under runs/ first.
4. DB05 inspect schema using DB Browser for SQLite.
5. DB06 seed minimal repo/source/document/script records.
6. DB07 add PK/FK relation catalog seed rows.
7. DB08 add validation queries.
8. DB09 connect first ShapiroInfo docs/scripts/runs as metadata only.
9. DB10 later connect C60/carbon domain metadata.

No raw TIM/PAR values should be inserted during early DB bootstrap.

## 21. Claim boundary

This note defines a research database schema plan.

It does not provide evidence for a physical Shapiro-information residual.

It does not validate the QSB-ST Bridge.

It does not establish spacetime, quantum-gravity, relativistic, pulsar-timing, or molecular-structure physics claims.

It does not read TIM/PAR values.

It does not analyze raw data.

It only defines an audit-capable, ETL-aware, lineage-aware database planning layer for QSB research data and repository artifacts.
