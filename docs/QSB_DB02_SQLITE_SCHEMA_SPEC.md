# QSB-DB02 — SQLite Schema Specification

Date: 2026-06-02  
Status: SQLite schema specification  
Scope: QSB-wide research-data infrastructure  
Upstream plan: QSB_DB01_RESEARCH_DATABASE_REPO_LINEAGE_SCHEMA_PLAN  
Database target: SQLite first, portable to larger relational systems later  
Repo mode: documentation-only schema specification  
Raw artifact access: no raw artifact inspection by this note  
Physics-analysis status: closed for physical interpretation, residual search, and model fitting  
Tracking decision: this documentation note may be tracked; raw artifacts remain local-only and untracked

## 1. Purpose

This note specifies the first SQLite schema for the QSB research database.

It translates QSB-DB01 into a concrete SQLite-oriented schema specification for source provenance, raw-data staging, repository lineage, script/document/run/output relations, ETL and harmonization, transformation-view planning, audit checks, and claim-boundary control.

This note does not create a database file.

This note does not create SQL files.

This note does not create scripts.

The database is an audit-capable research-data backbone.

It is not an interpretation engine.

It is not a preselection engine.

It is not a physical-claim engine.

Quarantine is preservation, not deletion.

Everything is preserved, but not everything is released into analytics.

The raw-data layer is not an analytics table.

## 2. SQLite Design Principles

Implementation requirements:

- PRAGMA foreign_keys = ON
- INTEGER PRIMARY KEY for internal IDs
- TEXT timestamps in ISO-8601 style or DEFAULT CURRENT_TIMESTAMP
- INTEGER boolean flags using 0 / 1
- explicit FOREIGN KEY definitions
- source-aware lineage uniqueness where records enter staging
- indexes on foreign keys and high-use lookup fields
- CHECK constraints only where stable and non-interpretive
- no raw TIM/PAR value insertion during early bootstrap

SQLite has limited stored procedure support. Procedure-like behavior should be implemented later through validation queries, views, audit-log insertions, and controlled Python runners.

## 3. Core Schema Groups

The first SQLite schema is organized into these groups:

1. Source and raw-data staging
2. Relation catalog
3. Repository and Git lineage
4. Project files and documents
5. Scripts, runs, outputs, and tables
6. Script-table and document-table relations
7. Fields and raw tokens
8. ETL and harmonization
9. Unit, quantity, and transformation-view catalogs
10. Audit and quality
11. Claim boundaries

## 4. Source and Raw-Data Staging Schema

### 4.1 raw_data_source

Purpose:

Track source, datapot, provider, release, access state, checksum state, provenance confidence, and quarantine state for incoming data.

SQLite CREATE TABLE block:

```sql
CREATE TABLE raw_data_source (
    raw_data_source_id INTEGER PRIMARY KEY,
    source_name TEXT NOT NULL,
    source_type TEXT NOT NULL,
    provider_or_project TEXT,
    source_url_or_path TEXT,
    source_release TEXT,
    source_version TEXT,
    source_access_date TEXT,
    source_download_status TEXT NOT NULL DEFAULT 'not_downloaded',
    source_reachability_status TEXT NOT NULL DEFAULT 'unresolved',
    source_corruption_status TEXT NOT NULL DEFAULT 'not_checked',
    checksum_status TEXT NOT NULL DEFAULT 'not_checked',
    license_or_usage_note TEXT,
    provenance_confidence TEXT NOT NULL DEFAULT 'unresolved',
    quarantine_status TEXT NOT NULL DEFAULT 'not_quarantined',
    notes TEXT,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT
);
```

Recommended indexes and uniqueness:

```sql
CREATE INDEX idx_raw_data_source_name ON raw_data_source(source_name);
CREATE INDEX idx_raw_data_source_provider ON raw_data_source(provider_or_project);
CREATE INDEX idx_raw_data_source_quarantine ON raw_data_source(quarantine_status);
```

Field list:

| field name | SQLite type | description |
|---|---|---|
| raw_data_source_id | INTEGER PRIMARY KEY | Internal source identifier. |
| source_name | TEXT NOT NULL | Human-readable source name. |
| source_type | TEXT NOT NULL | Source class such as public_page, local_artifact_set, release, repository, or external_dataset. |
| provider_or_project | TEXT | Provider, project, instrument, archive, or repository owner. |
| source_url_or_path | TEXT | URL or local path reference, without requiring download. |
| source_release | TEXT | Named source release if known. |
| source_version | TEXT | Version string if known. |
| source_access_date | TEXT | ISO-style date of source access or review. |
| source_download_status | TEXT | Download state such as not_downloaded, downloaded, forbidden, or unresolved. |
| source_reachability_status | TEXT | Reachability state such as reachable, unreachable, access_denied, or unresolved. |
| source_corruption_status | TEXT | Corruption or completeness state. |
| checksum_status | TEXT | Checksum state, if applicable. |
| license_or_usage_note | TEXT | License or usage note. |
| provenance_confidence | TEXT | Provenance confidence state. |
| quarantine_status | TEXT | Whether the source is quarantined or usable for later controlled steps. |
| notes | TEXT | Free-form audit note. |
| created_at | TEXT | Creation timestamp. |
| updated_at | TEXT | Update timestamp. |

### 4.2 raw_data

Purpose:

Serve as the controlled raw-data and staging door. This table preserves source-aware lineage and controls whether records may proceed into harmonized tables. The raw-data layer is not an analytics table.

SQLite CREATE TABLE block:

```sql
CREATE TABLE raw_data (
    raw_data_id INTEGER PRIMARY KEY,
    raw_data_source_id INTEGER NOT NULL,
    raw_artifact_id TEXT,
    source_local_file_id TEXT,
    source_local_record_id TEXT,
    source_local_measurement_id TEXT,
    source_record_hash TEXT,
    raw_record_position TEXT,
    raw_object_type TEXT,
    raw_file_type TEXT,
    raw_ingest_status TEXT NOT NULL DEFAULT 'not_ingested',
    raw_parse_status TEXT NOT NULL DEFAULT 'not_parsed',
    raw_quality_status TEXT NOT NULL DEFAULT 'not_checked',
    blank_check_status TEXT NOT NULL DEFAULT 'not_checked',
    special_character_check_status TEXT NOT NULL DEFAULT 'not_checked',
    datatype_check_status TEXT NOT NULL DEFAULT 'not_checked',
    unit_detection_status TEXT NOT NULL DEFAULT 'not_checked',
    scale_detection_status TEXT NOT NULL DEFAULT 'not_checked',
    harmonization_status TEXT NOT NULL DEFAULT 'not_harmonized',
    etl_release_status TEXT NOT NULL DEFAULT 'not_released',
    quarantine_status TEXT NOT NULL DEFAULT 'not_quarantined',
    quarantine_reason TEXT,
    retry_possible INTEGER NOT NULL DEFAULT 0,
    notes TEXT,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT,
    FOREIGN KEY (raw_data_source_id) REFERENCES raw_data_source(raw_data_source_id),
    UNIQUE(raw_data_source_id, source_local_file_id, source_local_record_id)
);
```

Recommended indexes and uniqueness:

```sql
CREATE INDEX idx_raw_data_source ON raw_data(raw_data_source_id);
CREATE INDEX idx_raw_data_artifact ON raw_data(raw_artifact_id);
CREATE INDEX idx_raw_data_parse_status ON raw_data(raw_parse_status);
CREATE INDEX idx_raw_data_harmonization_status ON raw_data(harmonization_status);
CREATE INDEX idx_raw_data_quarantine_status ON raw_data(quarantine_status);
```

Field list:

| field name | SQLite type | description |
|---|---|---|
| raw_data_id | INTEGER PRIMARY KEY | Internal raw/staging identifier. |
| raw_data_source_id | INTEGER NOT NULL | Source FK. |
| raw_artifact_id | TEXT | Optional artifact-level identifier. |
| source_local_file_id | TEXT | Source-local file identifier or relative path key. |
| source_local_record_id | TEXT | Source-local record identifier. |
| source_local_measurement_id | TEXT | Optional source-local measurement identifier. |
| source_record_hash | TEXT | Optional hash of a source record or tokenized record. |
| raw_record_position | TEXT | File, row, object, or block position. |
| raw_object_type | TEXT | Raw object class. |
| raw_file_type | TEXT | Raw file type or extension. |
| raw_ingest_status | TEXT | Ingest status. |
| raw_parse_status | TEXT | Parse status. |
| raw_quality_status | TEXT | Quality check status. |
| blank_check_status | TEXT | Blank/null review status. |
| special_character_check_status | TEXT | Special-character review status. |
| datatype_check_status | TEXT | Datatype review status. |
| unit_detection_status | TEXT | Unit-detection status. |
| scale_detection_status | TEXT | Scale-detection status. |
| harmonization_status | TEXT | Harmonization status. |
| etl_release_status | TEXT | Release state for downstream views. |
| quarantine_status | TEXT | Quarantine state. |
| quarantine_reason | TEXT | Reason for quarantine or technical rejection. |
| retry_possible | INTEGER | 0/1 flag for whether a later technical retry is possible. |
| notes | TEXT | Free-form audit note. |
| created_at | TEXT | Creation timestamp. |
| updated_at | TEXT | Update timestamp. |

## 5. Relation Catalog Schema

### 5.1 pk_fk_relation_catalog

Purpose:

Document enforced and logical PK/FK relationships so the database model remains auditable and reviewable.

SQLite CREATE TABLE block:

```sql
CREATE TABLE pk_fk_relation_catalog (
    relation_id INTEGER PRIMARY KEY,
    source_table TEXT NOT NULL,
    source_column TEXT NOT NULL,
    target_table TEXT NOT NULL,
    target_column TEXT NOT NULL,
    relation_type TEXT NOT NULL,
    cardinality TEXT,
    constraint_name TEXT,
    is_enforced INTEGER NOT NULL DEFAULT 1,
    is_logical_only INTEGER NOT NULL DEFAULT 0,
    join_rule TEXT,
    validity_condition TEXT,
    audit_relevance TEXT,
    notes TEXT,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);
```

Recommended indexes and uniqueness:

```sql
CREATE UNIQUE INDEX uq_pk_fk_relation
ON pk_fk_relation_catalog(source_table, source_column, target_table, target_column);
CREATE INDEX idx_pk_fk_relation_target ON pk_fk_relation_catalog(target_table, target_column);
```

Field list:

| field name | SQLite type | description |
|---|---|---|
| relation_id | INTEGER PRIMARY KEY | Internal relation identifier. |
| source_table | TEXT NOT NULL | FK or logical source table. |
| source_column | TEXT NOT NULL | FK or logical source column. |
| target_table | TEXT NOT NULL | Referenced table. |
| target_column | TEXT NOT NULL | Referenced column. |
| relation_type | TEXT NOT NULL | Relationship type, such as foreign_key or logical_lineage. |
| cardinality | TEXT | Expected cardinality. |
| constraint_name | TEXT | Constraint or index name. |
| is_enforced | INTEGER | 0/1 flag for enforced constraints. |
| is_logical_only | INTEGER | 0/1 flag for logical-only relations. |
| join_rule | TEXT | Join rule description. |
| validity_condition | TEXT | Condition under which relation is valid. |
| audit_relevance | TEXT | Why relation matters for audit. |
| notes | TEXT | Free-form note. |
| created_at | TEXT | Creation timestamp. |

## 6. Repository and Git Lineage Schema

### 6.1 repo_catalog

Purpose:

Track repositories and local roots used by the research database.

SQLite CREATE TABLE block:

```sql
CREATE TABLE repo_catalog (
    repo_id INTEGER PRIMARY KEY,
    repo_name TEXT NOT NULL,
    repo_url TEXT,
    local_root_path TEXT,
    default_branch TEXT,
    project_area TEXT,
    repo_status TEXT NOT NULL DEFAULT 'active',
    notes TEXT,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT
);
```

Recommended indexes and uniqueness:

```sql
CREATE UNIQUE INDEX uq_repo_catalog_name_root ON repo_catalog(repo_name, local_root_path);
CREATE INDEX idx_repo_catalog_url ON repo_catalog(repo_url);
```

Field list:

| field name | SQLite type | description |
|---|---|---|
| repo_id | INTEGER PRIMARY KEY | Internal repository identifier. |
| repo_name | TEXT NOT NULL | Repository name. |
| repo_url | TEXT | Remote URL if tracked. |
| local_root_path | TEXT | Local repository root. |
| default_branch | TEXT | Default branch name. |
| project_area | TEXT | Project area or domain. |
| repo_status | TEXT | Repository status. |
| notes | TEXT | Free-form note. |
| created_at | TEXT | Creation timestamp. |
| updated_at | TEXT | Update timestamp. |

### 6.2 git_commit_catalog

Purpose:

Track commits, branches, tags, and clean-state snapshots connected to research artifacts.

SQLite CREATE TABLE block:

```sql
CREATE TABLE git_commit_catalog (
    commit_id INTEGER PRIMARY KEY,
    repo_id INTEGER NOT NULL,
    commit_hash TEXT NOT NULL,
    short_hash TEXT,
    commit_message TEXT,
    commit_author TEXT,
    commit_date TEXT,
    branch_name TEXT,
    tag_name TEXT,
    is_clean_state INTEGER NOT NULL DEFAULT 0,
    git_status_snapshot TEXT,
    notes TEXT,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (repo_id) REFERENCES repo_catalog(repo_id),
    UNIQUE(repo_id, commit_hash)
);
```

Recommended indexes and uniqueness:

```sql
CREATE INDEX idx_git_commit_repo ON git_commit_catalog(repo_id);
CREATE INDEX idx_git_commit_short_hash ON git_commit_catalog(short_hash);
CREATE INDEX idx_git_commit_date ON git_commit_catalog(commit_date);
```

Field list:

| field name | SQLite type | description |
|---|---|---|
| commit_id | INTEGER PRIMARY KEY | Internal commit identifier. |
| repo_id | INTEGER NOT NULL | Repository FK. |
| commit_hash | TEXT NOT NULL | Full Git commit hash. |
| short_hash | TEXT | Short hash. |
| commit_message | TEXT | Commit message. |
| commit_author | TEXT | Commit author. |
| commit_date | TEXT | Commit date. |
| branch_name | TEXT | Branch at capture time. |
| tag_name | TEXT | Tag if relevant. |
| is_clean_state | INTEGER | 0/1 clean-state flag. |
| git_status_snapshot | TEXT | Captured git status text. |
| notes | TEXT | Free-form note. |
| created_at | TEXT | Creation timestamp. |

## 7. Project File and Document Schema

### 7.1 project_file_catalog

Purpose:

Track project files in docs, data, scripts, runs, and related areas without forcing raw artifacts into tracked status.

SQLite CREATE TABLE block:

```sql
CREATE TABLE project_file_catalog (
    project_file_id INTEGER PRIMARY KEY,
    repo_id INTEGER,
    commit_id INTEGER,
    file_path TEXT NOT NULL,
    file_name TEXT,
    file_type TEXT,
    project_role TEXT,
    tracking_status TEXT NOT NULL DEFAULT 'unknown',
    created_by_block TEXT,
    modified_by_block TEXT,
    checksum TEXT,
    notes TEXT,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT,
    FOREIGN KEY (repo_id) REFERENCES repo_catalog(repo_id),
    FOREIGN KEY (commit_id) REFERENCES git_commit_catalog(commit_id)
);
```

Recommended indexes and uniqueness:

```sql
CREATE UNIQUE INDEX uq_project_file_repo_path_commit
ON project_file_catalog(repo_id, file_path, commit_id);
CREATE INDEX idx_project_file_path ON project_file_catalog(file_path);
CREATE INDEX idx_project_file_role ON project_file_catalog(project_role);
```

Field list:

| field name | SQLite type | description |
|---|---|---|
| project_file_id | INTEGER PRIMARY KEY | Internal file identifier. |
| repo_id | INTEGER | Repository FK. |
| commit_id | INTEGER | Commit FK. |
| file_path | TEXT NOT NULL | Project-relative file path. |
| file_name | TEXT | Basename. |
| file_type | TEXT | File type or extension class. |
| project_role | TEXT | Role such as script, documentation_note, result_note, config, or run_output. |
| tracking_status | TEXT | tracked, untracked, ignored, local_only, or unknown. |
| created_by_block | TEXT | QSB block that created the file. |
| modified_by_block | TEXT | QSB block that modified the file. |
| checksum | TEXT | Optional checksum. |
| notes | TEXT | Free-form note. |
| created_at | TEXT | Creation timestamp. |
| updated_at | TEXT | Update timestamp. |

### 7.2 document_catalog

Purpose:

Track notes, specs, plans, result notes, handoff notes, and public/private documents.

SQLite CREATE TABLE block:

```sql
CREATE TABLE document_catalog (
    document_id INTEGER PRIMARY KEY,
    project_file_id INTEGER NOT NULL,
    document_title TEXT,
    document_type TEXT,
    qsb_block_id TEXT,
    upstream_block TEXT,
    downstream_block TEXT,
    status TEXT,
    claim_boundary_level TEXT,
    tracking_decision TEXT,
    notes TEXT,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT,
    FOREIGN KEY (project_file_id) REFERENCES project_file_catalog(project_file_id),
    UNIQUE(project_file_id)
);
```

Recommended indexes and uniqueness:

```sql
CREATE INDEX idx_document_block ON document_catalog(qsb_block_id);
CREATE INDEX idx_document_type ON document_catalog(document_type);
CREATE INDEX idx_document_claim_boundary ON document_catalog(claim_boundary_level);
```

Field list:

| field name | SQLite type | description |
|---|---|---|
| document_id | INTEGER PRIMARY KEY | Internal document identifier. |
| project_file_id | INTEGER NOT NULL | Project-file FK. |
| document_title | TEXT | Human-readable title. |
| document_type | TEXT | decision_note, plan, spec, result_note, handoff, or similar. |
| qsb_block_id | TEXT | Block ID. |
| upstream_block | TEXT | Upstream block reference. |
| downstream_block | TEXT | Downstream block reference. |
| status | TEXT | Document status. |
| claim_boundary_level | TEXT | Claim-boundary level. |
| tracking_decision | TEXT | Tracking decision. |
| notes | TEXT | Free-form note. |
| created_at | TEXT | Creation timestamp. |
| updated_at | TEXT | Update timestamp. |

## 8. Script, Run, Output, and Table Schema

### 8.1 script_catalog

Purpose:

Track scripts as executable research objects with execution and claim-boundary metadata.

SQLite CREATE TABLE block:

```sql
CREATE TABLE script_catalog (
    script_id INTEGER PRIMARY KEY,
    project_file_id INTEGER NOT NULL,
    script_name TEXT,
    script_path TEXT,
    script_language TEXT,
    execution_allowed_status TEXT NOT NULL DEFAULT 'not_reviewed',
    last_known_commit_hash TEXT,
    purpose TEXT,
    claim_boundary TEXT,
    notes TEXT,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT,
    FOREIGN KEY (project_file_id) REFERENCES project_file_catalog(project_file_id),
    UNIQUE(project_file_id)
);
```

Recommended indexes and uniqueness:

```sql
CREATE INDEX idx_script_path ON script_catalog(script_path);
CREATE INDEX idx_script_execution_status ON script_catalog(execution_allowed_status);
```

Field list:

| field name | SQLite type | description |
|---|---|---|
| script_id | INTEGER PRIMARY KEY | Internal script identifier. |
| project_file_id | INTEGER NOT NULL | Project-file FK. |
| script_name | TEXT | Script name. |
| script_path | TEXT | Project-relative script path. |
| script_language | TEXT | Script language. |
| execution_allowed_status | TEXT | Execution permission status. |
| last_known_commit_hash | TEXT | Last known commit hash for script content. |
| purpose | TEXT | Script purpose. |
| claim_boundary | TEXT | Claim boundary for script output. |
| notes | TEXT | Free-form note. |
| created_at | TEXT | Creation timestamp. |
| updated_at | TEXT | Update timestamp. |

### 8.2 run_catalog

Purpose:

Track controlled script executions, run boundaries, raw access state, download state, and claim-boundary status.

SQLite CREATE TABLE block:

```sql
CREATE TABLE run_catalog (
    run_id INTEGER PRIMARY KEY,
    run_block TEXT,
    script_id INTEGER,
    repo_id INTEGER,
    commit_id INTEGER,
    run_timestamp TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    execution_mode TEXT,
    output_root TEXT,
    run_status TEXT NOT NULL DEFAULT 'not_started',
    git_status_before TEXT,
    git_status_after TEXT,
    raw_access_status TEXT NOT NULL DEFAULT 'not_performed',
    download_status TEXT NOT NULL DEFAULT 'not_performed',
    value_reading_status TEXT NOT NULL DEFAULT 'not_performed',
    claim_boundary_status TEXT NOT NULL DEFAULT 'closed',
    notes TEXT,
    FOREIGN KEY (script_id) REFERENCES script_catalog(script_id),
    FOREIGN KEY (repo_id) REFERENCES repo_catalog(repo_id),
    FOREIGN KEY (commit_id) REFERENCES git_commit_catalog(commit_id)
);
```

Recommended indexes and uniqueness:

```sql
CREATE INDEX idx_run_block ON run_catalog(run_block);
CREATE INDEX idx_run_script ON run_catalog(script_id);
CREATE INDEX idx_run_commit ON run_catalog(commit_id);
CREATE INDEX idx_run_status ON run_catalog(run_status);
```

Field list:

| field name | SQLite type | description |
|---|---|---|
| run_id | INTEGER PRIMARY KEY | Internal run identifier. |
| run_block | TEXT | QSB run block ID. |
| script_id | INTEGER | Script FK. |
| repo_id | INTEGER | Repository FK. |
| commit_id | INTEGER | Commit FK. |
| run_timestamp | TEXT | Run timestamp. |
| execution_mode | TEXT | Execution mode. |
| output_root | TEXT | Output directory. |
| run_status | TEXT | Run status. |
| git_status_before | TEXT | Pre-run Git status. |
| git_status_after | TEXT | Post-run Git status. |
| raw_access_status | TEXT | Raw access state. |
| download_status | TEXT | Download state. |
| value_reading_status | TEXT | Value-reading state. |
| claim_boundary_status | TEXT | Claim-boundary state. |
| notes | TEXT | Free-form note. |

### 8.3 run_output_catalog

Purpose:

Track files created by controlled runs.

SQLite CREATE TABLE block:

```sql
CREATE TABLE run_output_catalog (
    run_output_id INTEGER PRIMARY KEY,
    run_id INTEGER NOT NULL,
    project_file_id INTEGER,
    output_path TEXT,
    output_type TEXT,
    byte_size INTEGER,
    row_count INTEGER,
    checksum TEXT,
    tracked_status TEXT NOT NULL DEFAULT 'run_artifact',
    notes TEXT,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (run_id) REFERENCES run_catalog(run_id),
    FOREIGN KEY (project_file_id) REFERENCES project_file_catalog(project_file_id)
);
```

Recommended indexes and uniqueness:

```sql
CREATE UNIQUE INDEX uq_run_output_path ON run_output_catalog(run_id, output_path);
CREATE INDEX idx_run_output_run ON run_output_catalog(run_id);
CREATE INDEX idx_run_output_type ON run_output_catalog(output_type);
```

Field list:

| field name | SQLite type | description |
|---|---|---|
| run_output_id | INTEGER PRIMARY KEY | Internal run-output identifier. |
| run_id | INTEGER NOT NULL | Run FK. |
| project_file_id | INTEGER | Project-file FK if cataloged. |
| output_path | TEXT | Output path. |
| output_type | TEXT | Output type. |
| byte_size | INTEGER | Byte size. |
| row_count | INTEGER | Row count if table-like. |
| checksum | TEXT | Optional checksum. |
| tracked_status | TEXT | tracked, ignored, run_artifact, or local_only. |
| notes | TEXT | Free-form note. |
| created_at | TEXT | Creation timestamp. |

### 8.4 table_catalog

Purpose:

Track SQLite tables, CSV tables, JSON summaries, markdown readouts, external table-like artifacts, and views.

SQLite CREATE TABLE block:

```sql
CREATE TABLE table_catalog (
    table_id INTEGER PRIMARY KEY,
    table_name TEXT NOT NULL,
    table_type TEXT,
    storage_type TEXT,
    storage_path TEXT,
    schema_status TEXT NOT NULL DEFAULT 'not_reviewed',
    row_count INTEGER,
    column_count INTEGER,
    created_by_script_id INTEGER,
    created_by_run_id INTEGER,
    source_raw_data_id INTEGER,
    notes TEXT,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT,
    FOREIGN KEY (created_by_script_id) REFERENCES script_catalog(script_id),
    FOREIGN KEY (created_by_run_id) REFERENCES run_catalog(run_id),
    FOREIGN KEY (source_raw_data_id) REFERENCES raw_data(raw_data_id)
);
```

Recommended indexes and uniqueness:

```sql
CREATE UNIQUE INDEX uq_table_storage ON table_catalog(table_name, storage_type, storage_path);
CREATE INDEX idx_table_created_by_run ON table_catalog(created_by_run_id);
CREATE INDEX idx_table_source_raw_data ON table_catalog(source_raw_data_id);
```

Field list:

| field name | SQLite type | description |
|---|---|---|
| table_id | INTEGER PRIMARY KEY | Internal table identifier. |
| table_name | TEXT NOT NULL | Table or artifact name. |
| table_type | TEXT | Logical table type. |
| storage_type | TEXT | sqlite_table, csv_file, json_summary, markdown_readout, external_table, or view. |
| storage_path | TEXT | Storage path if applicable. |
| schema_status | TEXT | Schema review status. |
| row_count | INTEGER | Row count if known. |
| column_count | INTEGER | Column count if known. |
| created_by_script_id | INTEGER | Script FK. |
| created_by_run_id | INTEGER | Run FK. |
| source_raw_data_id | INTEGER | Raw-data FK when table derives from one staged object. |
| notes | TEXT | Free-form note. |
| created_at | TEXT | Creation timestamp. |
| updated_at | TEXT | Update timestamp. |

## 9. Script-Table and Document-Table Relations

### 9.1 script_table_relation

Purpose:

Link scripts to tables or table-like artifacts they read, create, validate, export, document, or depend on.

SQLite CREATE TABLE block:

```sql
CREATE TABLE script_table_relation (
    script_table_relation_id INTEGER PRIMARY KEY,
    script_id INTEGER NOT NULL,
    table_id INTEGER NOT NULL,
    relation_type TEXT NOT NULL,
    operation_type TEXT,
    run_id INTEGER,
    commit_id INTEGER,
    notes TEXT,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (script_id) REFERENCES script_catalog(script_id),
    FOREIGN KEY (table_id) REFERENCES table_catalog(table_id),
    FOREIGN KEY (run_id) REFERENCES run_catalog(run_id),
    FOREIGN KEY (commit_id) REFERENCES git_commit_catalog(commit_id)
);
```

Recommended indexes and uniqueness:

```sql
CREATE UNIQUE INDEX uq_script_table_relation
ON script_table_relation(script_id, table_id, relation_type, COALESCE(run_id, -1));
CREATE INDEX idx_script_table_table ON script_table_relation(table_id);
```

Field list:

| field name | SQLite type | description |
|---|---|---|
| script_table_relation_id | INTEGER PRIMARY KEY | Internal relation identifier. |
| script_id | INTEGER NOT NULL | Script FK. |
| table_id | INTEGER NOT NULL | Table FK. |
| relation_type | TEXT NOT NULL | creates, reads, validates, exports, documents, or depends_on. |
| operation_type | TEXT | read_only, write_output, schema_create, etl_transform, validation, or summary. |
| run_id | INTEGER | Run FK if run-specific. |
| commit_id | INTEGER | Commit FK if commit-specific. |
| notes | TEXT | Free-form note. |
| created_at | TEXT | Creation timestamp. |

### 9.2 document_table_relation

Purpose:

Link documents and notes to tables they specify, document, review, summarize, validate, or bound with claim boundaries.

SQLite CREATE TABLE block:

```sql
CREATE TABLE document_table_relation (
    document_table_relation_id INTEGER PRIMARY KEY,
    document_id INTEGER NOT NULL,
    table_id INTEGER NOT NULL,
    relation_type TEXT,
    notes TEXT,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (document_id) REFERENCES document_catalog(document_id),
    FOREIGN KEY (table_id) REFERENCES table_catalog(table_id)
);
```

Recommended indexes and uniqueness:

```sql
CREATE UNIQUE INDEX uq_document_table_relation
ON document_table_relation(document_id, table_id, relation_type);
CREATE INDEX idx_document_table_table ON document_table_relation(table_id);
```

Field list:

| field name | SQLite type | description |
|---|---|---|
| document_table_relation_id | INTEGER PRIMARY KEY | Internal relation identifier. |
| document_id | INTEGER NOT NULL | Document FK. |
| table_id | INTEGER NOT NULL | Table FK. |
| relation_type | TEXT | documents, summarizes, specifies, reviews, validates, or claim_boundary_for. |
| notes | TEXT | Free-form note. |
| created_at | TEXT | Creation timestamp. |

## 10. Field and Raw-Token Schema

### 10.1 field_catalog

Purpose:

Track fields and columns discovered in raw, staged, harmonized, external, or view tables.

SQLite CREATE TABLE block:

```sql
CREATE TABLE field_catalog (
    field_id INTEGER PRIMARY KEY,
    table_id INTEGER,
    raw_data_id INTEGER,
    field_name TEXT,
    field_position INTEGER,
    raw_type TEXT,
    inferred_type TEXT,
    harmonized_type TEXT,
    semantic_status TEXT NOT NULL DEFAULT 'unresolved',
    correction_state_relevance TEXT,
    unit_status TEXT NOT NULL DEFAULT 'not_checked',
    scale_status TEXT NOT NULL DEFAULT 'not_checked',
    missingness_status TEXT NOT NULL DEFAULT 'not_checked',
    notes TEXT,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT,
    FOREIGN KEY (table_id) REFERENCES table_catalog(table_id),
    FOREIGN KEY (raw_data_id) REFERENCES raw_data(raw_data_id)
);
```

Recommended indexes and uniqueness:

```sql
CREATE UNIQUE INDEX uq_field_table_position ON field_catalog(table_id, field_position);
CREATE INDEX idx_field_name ON field_catalog(field_name);
CREATE INDEX idx_field_raw_data ON field_catalog(raw_data_id);
```

Field list:

| field name | SQLite type | description |
|---|---|---|
| field_id | INTEGER PRIMARY KEY | Internal field identifier. |
| table_id | INTEGER | Table FK. |
| raw_data_id | INTEGER | Raw-data FK. |
| field_name | TEXT | Field or column name. |
| field_position | INTEGER | Field position. |
| raw_type | TEXT | Raw type. |
| inferred_type | TEXT | Inferred technical type. |
| harmonized_type | TEXT | Harmonized type. |
| semantic_status | TEXT | Semantic mapping status. |
| correction_state_relevance | TEXT | Whether field relates to correction-state handling. |
| unit_status | TEXT | Unit review status. |
| scale_status | TEXT | Scale review status. |
| missingness_status | TEXT | Missingness review status. |
| notes | TEXT | Free-form note. |
| created_at | TEXT | Creation timestamp. |
| updated_at | TEXT | Update timestamp. |

### 10.2 raw_token_catalog

Purpose:

Optionally preserve raw token-level observations without interpreting them physically.

SQLite CREATE TABLE block:

```sql
CREATE TABLE raw_token_catalog (
    raw_token_id INTEGER PRIMARY KEY,
    raw_data_id INTEGER NOT NULL,
    field_id INTEGER,
    source_local_record_id TEXT,
    raw_token TEXT,
    token_position TEXT,
    token_type_guess TEXT,
    parse_status TEXT NOT NULL DEFAULT 'not_parsed',
    quarantine_status TEXT NOT NULL DEFAULT 'not_quarantined',
    notes TEXT,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (raw_data_id) REFERENCES raw_data(raw_data_id),
    FOREIGN KEY (field_id) REFERENCES field_catalog(field_id)
);
```

Recommended indexes and uniqueness:

```sql
CREATE INDEX idx_raw_token_raw_data ON raw_token_catalog(raw_data_id);
CREATE INDEX idx_raw_token_field ON raw_token_catalog(field_id);
CREATE INDEX idx_raw_token_parse_status ON raw_token_catalog(parse_status);
```

Field list:

| field name | SQLite type | description |
|---|---|---|
| raw_token_id | INTEGER PRIMARY KEY | Internal token identifier. |
| raw_data_id | INTEGER NOT NULL | Raw-data FK. |
| field_id | INTEGER | Field FK. |
| source_local_record_id | TEXT | Source-local record ID. |
| raw_token | TEXT | Preserved raw token text when later authorized. |
| token_position | TEXT | Position in record or file. |
| token_type_guess | TEXT | Technical type guess. |
| parse_status | TEXT | Parse status. |
| quarantine_status | TEXT | Quarantine status. |
| notes | TEXT | Free-form note. |
| created_at | TEXT | Creation timestamp. |

## 11. ETL and Harmonization Schema

### 11.1 etl_transformation_rule

Purpose:

Store documented transformations, casts, mappings, unit harmonization rules, scale rules, missing-value rules, and file-format normalization rules.

SQLite CREATE TABLE block:

```sql
CREATE TABLE etl_transformation_rule (
    etl_rule_id INTEGER PRIMARY KEY,
    rule_name TEXT NOT NULL,
    rule_type TEXT NOT NULL,
    source_field_id INTEGER,
    target_field_name TEXT,
    transformation_expression TEXT,
    cast_rule TEXT,
    mapping_rule TEXT,
    unit_before TEXT,
    unit_after TEXT,
    scale_rule TEXT,
    missing_value_rule TEXT,
    blank_handling_rule TEXT,
    special_character_rule TEXT,
    provenance_status TEXT NOT NULL DEFAULT 'unresolved',
    reversible_flag INTEGER NOT NULL DEFAULT 0,
    allowed_for_analytics INTEGER NOT NULL DEFAULT 0,
    notes TEXT,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT,
    FOREIGN KEY (source_field_id) REFERENCES field_catalog(field_id)
);
```

Recommended indexes and uniqueness:

```sql
CREATE UNIQUE INDEX uq_etl_rule_name ON etl_transformation_rule(rule_name);
CREATE INDEX idx_etl_rule_source_field ON etl_transformation_rule(source_field_id);
CREATE INDEX idx_etl_rule_type ON etl_transformation_rule(rule_type);
```

Field list:

| field name | SQLite type | description |
|---|---|---|
| etl_rule_id | INTEGER PRIMARY KEY | Internal ETL-rule identifier. |
| rule_name | TEXT NOT NULL | Rule name. |
| rule_type | TEXT NOT NULL | cast, mapping, unit_harmonization, scale_normalization, missing_value_handling, blank_handling, special_character_cleanup, or file_format_normalization. |
| source_field_id | INTEGER | Source field FK. |
| target_field_name | TEXT | Target field name. |
| transformation_expression | TEXT | Documented expression, not silently assumed. |
| cast_rule | TEXT | Cast rule. |
| mapping_rule | TEXT | Mapping rule. |
| unit_before | TEXT | Source unit. |
| unit_after | TEXT | Target unit. |
| scale_rule | TEXT | Scaling rule. |
| missing_value_rule | TEXT | Missing-value rule. |
| blank_handling_rule | TEXT | Blank/null handling rule. |
| special_character_rule | TEXT | Special-character handling rule. |
| provenance_status | TEXT | Source/provenance support status. |
| reversible_flag | INTEGER | 0/1 reversibility flag. |
| allowed_for_analytics | INTEGER | 0/1 analytics release flag. |
| notes | TEXT | Free-form note. |
| created_at | TEXT | Creation timestamp. |
| updated_at | TEXT | Update timestamp. |

### 11.2 harmonized_value_view_catalog

Purpose:

Document harmonized blind-descriptive views without treating them as physical interpretation views.

SQLite CREATE TABLE block:

```sql
CREATE TABLE harmonized_value_view_catalog (
    view_id INTEGER PRIMARY KEY,
    view_name TEXT NOT NULL,
    view_type TEXT,
    source_table_ids TEXT,
    transformation_rule_set TEXT,
    blind_descriptive_status TEXT NOT NULL DEFAULT 'not_reviewed',
    interpretation_status TEXT NOT NULL DEFAULT 'closed',
    created_by_run_id INTEGER,
    notes TEXT,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT,
    FOREIGN KEY (created_by_run_id) REFERENCES run_catalog(run_id),
    UNIQUE(view_name)
);
```

Recommended indexes and uniqueness:

```sql
CREATE INDEX idx_harmonized_view_run ON harmonized_value_view_catalog(created_by_run_id);
CREATE INDEX idx_harmonized_view_status ON harmonized_value_view_catalog(blind_descriptive_status);
```

Field list:

| field name | SQLite type | description |
|---|---|---|
| view_id | INTEGER PRIMARY KEY | Internal view identifier. |
| view_name | TEXT NOT NULL | View name. |
| view_type | TEXT | View type. |
| source_table_ids | TEXT | Serialized list of source table IDs. |
| transformation_rule_set | TEXT | Transformation rule set identifier or list. |
| blind_descriptive_status | TEXT | Blind-descriptive status. |
| interpretation_status | TEXT | Interpretation gate status. |
| created_by_run_id | INTEGER | Run FK. |
| notes | TEXT | Free-form note. |
| created_at | TEXT | Creation timestamp. |
| updated_at | TEXT | Update timestamp. |

## 12. Unit, Quantity, and Transformation-View Schema

### 12.1 unit_dimension_catalog

Purpose:

Track units, SI units, dimensions, and conversion rules.

SQLite CREATE TABLE block:

```sql
CREATE TABLE unit_dimension_catalog (
    unit_id INTEGER PRIMARY KEY,
    unit_symbol TEXT NOT NULL,
    si_unit TEXT,
    dimension_expression TEXT,
    conversion_rule TEXT,
    source_status TEXT NOT NULL DEFAULT 'unresolved',
    notes TEXT,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT
);
```

Recommended indexes and uniqueness:

```sql
CREATE UNIQUE INDEX uq_unit_symbol_dimension ON unit_dimension_catalog(unit_symbol, dimension_expression);
CREATE INDEX idx_unit_si_unit ON unit_dimension_catalog(si_unit);
```

Field list:

| field name | SQLite type | description |
|---|---|---|
| unit_id | INTEGER PRIMARY KEY | Internal unit identifier. |
| unit_symbol | TEXT NOT NULL | Unit symbol. |
| si_unit | TEXT | SI unit. |
| dimension_expression | TEXT | Dimension expression. |
| conversion_rule | TEXT | Conversion rule. |
| source_status | TEXT | Source support status. |
| notes | TEXT | Free-form note. |
| created_at | TEXT | Creation timestamp. |
| updated_at | TEXT | Update timestamp. |

### 12.2 quantity_domain_catalog

Purpose:

Track theoretical, data, or mapping domains.

SQLite CREATE TABLE block:

```sql
CREATE TABLE quantity_domain_catalog (
    quantity_domain_id INTEGER PRIMARY KEY,
    domain_name TEXT NOT NULL,
    domain_type TEXT,
    description TEXT,
    notes TEXT,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT,
    UNIQUE(domain_name)
);
```

Recommended indexes and uniqueness:

```sql
CREATE INDEX idx_quantity_domain_type ON quantity_domain_catalog(domain_type);
```

Field list:

| field name | SQLite type | description |
|---|---|---|
| quantity_domain_id | INTEGER PRIMARY KEY | Internal domain identifier. |
| domain_name | TEXT NOT NULL | Domain name. |
| domain_type | TEXT | Domain type. |
| description | TEXT | Domain description. |
| notes | TEXT | Free-form note. |
| created_at | TEXT | Creation timestamp. |
| updated_at | TEXT | Update timestamp. |

### 12.3 quantity_catalog

Purpose:

Track quantities that may later be linked through documented transformation rules.

SQLite CREATE TABLE block:

```sql
CREATE TABLE quantity_catalog (
    quantity_id INTEGER PRIMARY KEY,
    quantity_domain_id INTEGER,
    symbol TEXT,
    quantity_name TEXT,
    si_unit TEXT,
    dimension_expression TEXT,
    observer_dependence TEXT,
    primitive_or_derived TEXT,
    description TEXT,
    notes TEXT,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT,
    FOREIGN KEY (quantity_domain_id) REFERENCES quantity_domain_catalog(quantity_domain_id)
);
```

Recommended indexes and uniqueness:

```sql
CREATE UNIQUE INDEX uq_quantity_domain_symbol ON quantity_catalog(quantity_domain_id, symbol);
CREATE INDEX idx_quantity_name ON quantity_catalog(quantity_name);
```

Field list:

| field name | SQLite type | description |
|---|---|---|
| quantity_id | INTEGER PRIMARY KEY | Internal quantity identifier. |
| quantity_domain_id | INTEGER | Quantity-domain FK. |
| symbol | TEXT | Quantity symbol. |
| quantity_name | TEXT | Quantity name. |
| si_unit | TEXT | SI unit. |
| dimension_expression | TEXT | Dimension expression. |
| observer_dependence | TEXT | Observer/frame dependence note. |
| primitive_or_derived | TEXT | Primitive or derived status. |
| description | TEXT | Quantity description. |
| notes | TEXT | Free-form note. |
| created_at | TEXT | Creation timestamp. |
| updated_at | TEXT | Update timestamp. |

### 12.4 transformation_rule_catalog

Purpose:

Track functional rules connecting quantities across domains as data-model mapping-layer objects, not physical validation claims.

SQLite CREATE TABLE block:

```sql
CREATE TABLE transformation_rule_catalog (
    transformation_rule_id INTEGER PRIMARY KEY,
    rule_name TEXT NOT NULL,
    source_quantity_ids TEXT,
    target_quantity_id INTEGER,
    formula_expression TEXT,
    required_constants TEXT,
    validity_conditions TEXT,
    unit_check_status TEXT NOT NULL DEFAULT 'not_checked',
    invertible_flag INTEGER NOT NULL DEFAULT 0,
    direction TEXT,
    assumption_level TEXT,
    source_status TEXT NOT NULL DEFAULT 'unresolved',
    claim_boundary TEXT NOT NULL DEFAULT 'no_physical_validation_claim',
    notes TEXT,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT,
    FOREIGN KEY (target_quantity_id) REFERENCES quantity_catalog(quantity_id),
    UNIQUE(rule_name)
);
```

Recommended indexes and uniqueness:

```sql
CREATE INDEX idx_transformation_target_quantity ON transformation_rule_catalog(target_quantity_id);
CREATE INDEX idx_transformation_source_status ON transformation_rule_catalog(source_status);
```

Field list:

| field name | SQLite type | description |
|---|---|---|
| transformation_rule_id | INTEGER PRIMARY KEY | Internal transformation-rule identifier. |
| rule_name | TEXT NOT NULL | Rule name. |
| source_quantity_ids | TEXT | Serialized source quantity IDs. |
| target_quantity_id | INTEGER | Target quantity FK. |
| formula_expression | TEXT | Formula or mapping expression. |
| required_constants | TEXT | Required constants. |
| validity_conditions | TEXT | Validity conditions. |
| unit_check_status | TEXT | Unit-check status. |
| invertible_flag | INTEGER | 0/1 invertibility flag. |
| direction | TEXT | Rule direction. |
| assumption_level | TEXT | Assumption level. |
| source_status | TEXT | Source support status. |
| claim_boundary | TEXT | Claim-boundary note. |
| notes | TEXT | Free-form note. |
| created_at | TEXT | Creation timestamp. |
| updated_at | TEXT | Update timestamp. |

## 13. Audit and Quality Schema

### 13.1 audit_log

Purpose:

Track significant DB actions, ETL releases, quarantines, transformations, and schema changes.

SQLite CREATE TABLE block:

```sql
CREATE TABLE audit_log (
    audit_id INTEGER PRIMARY KEY,
    action_type TEXT NOT NULL,
    object_type TEXT,
    object_id TEXT,
    related_rule_id TEXT,
    timestamp TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    actor TEXT,
    status TEXT,
    notes TEXT
);
```

Recommended indexes and uniqueness:

```sql
CREATE INDEX idx_audit_action_type ON audit_log(action_type);
CREATE INDEX idx_audit_object ON audit_log(object_type, object_id);
CREATE INDEX idx_audit_timestamp ON audit_log(timestamp);
```

Field list:

| field name | SQLite type | description |
|---|---|---|
| audit_id | INTEGER PRIMARY KEY | Internal audit identifier. |
| action_type | TEXT NOT NULL | Action type. |
| object_type | TEXT | Object type. |
| object_id | TEXT | Object identifier. |
| related_rule_id | TEXT | Related rule identifier. |
| timestamp | TEXT | Action timestamp. |
| actor | TEXT | Actor or process. |
| status | TEXT | Action status. |
| notes | TEXT | Free-form note. |

### 13.2 quality_check_catalog

Purpose:

Define reusable data-quality checks.

SQLite CREATE TABLE block:

```sql
CREATE TABLE quality_check_catalog (
    quality_check_id INTEGER PRIMARY KEY,
    check_name TEXT NOT NULL,
    check_type TEXT,
    target_table TEXT,
    target_field TEXT,
    check_expression TEXT,
    severity TEXT,
    stop_if_failed INTEGER NOT NULL DEFAULT 0,
    notes TEXT,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT,
    UNIQUE(check_name)
);
```

Recommended indexes and uniqueness:

```sql
CREATE INDEX idx_quality_check_target ON quality_check_catalog(target_table, target_field);
CREATE INDEX idx_quality_check_severity ON quality_check_catalog(severity);
```

Field list:

| field name | SQLite type | description |
|---|---|---|
| quality_check_id | INTEGER PRIMARY KEY | Internal check identifier. |
| check_name | TEXT NOT NULL | Check name. |
| check_type | TEXT | Check type. |
| target_table | TEXT | Target table. |
| target_field | TEXT | Target field. |
| check_expression | TEXT | Check expression. |
| severity | TEXT | Severity. |
| stop_if_failed | INTEGER | 0/1 stop flag. |
| notes | TEXT | Free-form note. |
| created_at | TEXT | Creation timestamp. |
| updated_at | TEXT | Update timestamp. |

### 13.3 quality_check_result

Purpose:

Store quality-check results linked to raw data, tables, and runs.

SQLite CREATE TABLE block:

```sql
CREATE TABLE quality_check_result (
    quality_check_result_id INTEGER PRIMARY KEY,
    quality_check_id INTEGER NOT NULL,
    raw_data_id INTEGER,
    table_id INTEGER,
    run_id INTEGER,
    result_status TEXT NOT NULL,
    result_detail TEXT,
    timestamp TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    notes TEXT,
    FOREIGN KEY (quality_check_id) REFERENCES quality_check_catalog(quality_check_id),
    FOREIGN KEY (raw_data_id) REFERENCES raw_data(raw_data_id),
    FOREIGN KEY (table_id) REFERENCES table_catalog(table_id),
    FOREIGN KEY (run_id) REFERENCES run_catalog(run_id)
);
```

Recommended indexes and uniqueness:

```sql
CREATE INDEX idx_quality_result_check ON quality_check_result(quality_check_id);
CREATE INDEX idx_quality_result_raw_data ON quality_check_result(raw_data_id);
CREATE INDEX idx_quality_result_table ON quality_check_result(table_id);
CREATE INDEX idx_quality_result_run ON quality_check_result(run_id);
```

Field list:

| field name | SQLite type | description |
|---|---|---|
| quality_check_result_id | INTEGER PRIMARY KEY | Internal check-result identifier. |
| quality_check_id | INTEGER NOT NULL | Quality-check FK. |
| raw_data_id | INTEGER | Raw-data FK. |
| table_id | INTEGER | Table FK. |
| run_id | INTEGER | Run FK. |
| result_status | TEXT NOT NULL | Result status. |
| result_detail | TEXT | Result detail. |
| timestamp | TEXT | Result timestamp. |
| notes | TEXT | Free-form note. |

## 14. Claim-Boundary Schema

### 14.1 claim_boundary_catalog

Purpose:

Record permitted and forbidden claim levels for artifacts, tables, runs, documents, and views.

SQLite CREATE TABLE block:

```sql
CREATE TABLE claim_boundary_catalog (
    claim_boundary_id INTEGER PRIMARY KEY,
    object_type TEXT NOT NULL,
    object_id TEXT NOT NULL,
    claim_level TEXT,
    physical_interpretation_allowed INTEGER NOT NULL DEFAULT 0,
    residual_analysis_allowed INTEGER NOT NULL DEFAULT 0,
    model_fitting_allowed INTEGER NOT NULL DEFAULT 0,
    bridge_claim_allowed INTEGER NOT NULL DEFAULT 0,
    value_reading_allowed INTEGER NOT NULL DEFAULT 0,
    notes TEXT,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT,
    UNIQUE(object_type, object_id)
);
```

Recommended indexes and uniqueness:

```sql
CREATE INDEX idx_claim_boundary_level ON claim_boundary_catalog(claim_level);
CREATE INDEX idx_claim_boundary_flags
ON claim_boundary_catalog(
    physical_interpretation_allowed,
    residual_analysis_allowed,
    model_fitting_allowed,
    bridge_claim_allowed,
    value_reading_allowed
);
```

Field list:

| field name | SQLite type | description |
|---|---|---|
| claim_boundary_id | INTEGER PRIMARY KEY | Internal claim-boundary identifier. |
| object_type | TEXT NOT NULL | Artifact, table, run, document, view, or script. |
| object_id | TEXT NOT NULL | Object identifier in its own catalog. |
| claim_level | TEXT | Permitted claim level. |
| physical_interpretation_allowed | INTEGER | 0/1 flag. |
| residual_analysis_allowed | INTEGER | 0/1 flag. |
| model_fitting_allowed | INTEGER | 0/1 flag. |
| bridge_claim_allowed | INTEGER | 0/1 flag. |
| value_reading_allowed | INTEGER | 0/1 flag. |
| notes | TEXT | Free-form note. |
| created_at | TEXT | Creation timestamp. |
| updated_at | TEXT | Update timestamp. |

## 15. Initial Recommended Views

Initial views should be created later in SQL, not by this note.

Recommended first views:

- v_raw_data_lineage: joins raw_data to raw_data_source.
- v_project_document_lineage: joins document_catalog, project_file_catalog, git_commit_catalog, and repo_catalog.
- v_run_output_lineage: joins run_catalog, script_catalog, run_output_catalog, and project_file_catalog.
- v_table_script_document_lineage: joins table_catalog, script_table_relation, document_table_relation, script_catalog, and document_catalog.
- v_claim_boundary_open_gates: lists objects with any interpretation, residual, model-fitting, value-reading, or Bridge gate open.
- v_quarantined_preserved_records: lists quarantined records preserved in raw_data.

These views are for audit and control. They are not interpretation views.

## 16. Initial Validation Queries

Initial validation queries should check:

- foreign-key enforcement is enabled with PRAGMA foreign_keys = ON.
- every raw_data row has a raw_data_source row.
- no duplicate raw_data source lineage key exists.
- no table_catalog row references a missing script or run.
- no document_table_relation row references a missing document or table.
- no script_table_relation row references a missing script or table.
- no harmonized value view has interpretation_status open by default.
- no claim_boundary_catalog row opens residual_analysis_allowed, model_fitting_allowed, bridge_claim_allowed, or physical_interpretation_allowed during early bootstrap.
- quarantined records remain present and auditable.
- no source-to-analytics jump occurs without raw_data lineage.

## 17. Required First Seed Entries Later

A later implementation should seed metadata only:

- one repo_catalog row for this repository,
- current git_commit_catalog row for the DB bootstrap commit,
- project_file_catalog rows for QSB-DB01, QSB-DB02, and later DB files,
- document_catalog rows for QSB-DB01 and QSB-DB02,
- pk_fk_relation_catalog rows for all enforced FKs in this specification,
- claim_boundary_catalog rows closing physical interpretation, residual analysis, model fitting, Bridge claims, and raw value reading for early DB artifacts.

No raw TIM/PAR values should be inserted during early DB bootstrap.

## 18. Portability Notes

The schema is SQLite-first but should remain portable to PostgreSQL or larger relational systems later.

Portability considerations:

- TEXT timestamps can later become TIMESTAMP fields.
- INTEGER boolean flags can later become BOOLEAN fields.
- serialized ID lists may later become join tables.
- SQLite views can later become database views or materialized views.
- audit logging can later move from script-controlled inserts to trigger-based logging.
- CHECK constraints should remain simple and stable.

## 19. Claim Boundary

This note defines a SQLite schema specification for a research-data infrastructure.

It does not provide evidence for a physical Shapiro-information residual.

It does not validate the QSB-ST Bridge.

It does not establish spacetime, quantum-gravity, relativistic, pulsar-timing, or molecular-structure physics claims.

It does not read TIM/PAR values.

It does not analyze raw data.

It only specifies an audit-capable, ETL-aware, lineage-aware SQLite schema for QSB research data and repository artifacts.

## 20. Next Practical Step

Recommended next block:

QSB-DB03_SQLITE_SCHEMA_SQL_FILE

That block may create a standalone SQL schema file if explicitly authorized later.

It must not create a database file unless a later block explicitly opens that implementation step.
