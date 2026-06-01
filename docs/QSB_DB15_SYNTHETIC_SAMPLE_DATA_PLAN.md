# QSB-DB15 — Synthetic Sample Data Plan

Date: 2026-06-02
Status: synthetic sample data plan
Scope: QSB-wide research database infrastructure
Upstream result: QSB_DB14_METADATA_SEED_RESULT_NOTE
Baseline metadata DB: runs/QSB-DB/QSB_DB13_METADATA_SEED/qsb_research_metadata_seed.db
Planned synthetic sample DB: runs/QSB-DB/QSB_DB18_SYNTHETIC_SAMPLE_DATA/qsb_research_synthetic_sample.db
Sample mode: synthetic-only controlled test data
Raw artifact access: no raw artifact inspection by this note
Physics-analysis status: closed for physical interpretation, residual search, and model fitting
Tracking decision: this documentation note may be tracked; SQLite database artifacts remain run artifacts

## 1. Purpose

This note defines the plan for the first controlled synthetic sample data load into the QSB SQLite research database line.

The database currently contains metadata lineage, but no measurement values.

That is methodologically safe, but not yet useful for browsing data behavior.

The purpose of this next phase is to add visible synthetic sample records so that the database can be inspected as a working data system.

The sample data must remain synthetic.

The sample data must not be TIM/PAR data.

The sample data must not be C60 or molecular data.

The sample data must not be analytics output.

The sample data must not be physical evidence.

This note does not modify the database.

This note does not insert data.

This note does not create SQL files.

This note does not create scripts.

This note does not inspect raw artifacts.

This note does not read TIM/PAR values.

This note does not analyze raw data.

## 2. Upstream state

QSB-DB13 created a metadata-seeded database artifact:

runs/QSB-DB/QSB_DB13_METADATA_SEED/qsb_research_metadata_seed.db

QSB-DB14 documented:

* metadata_seed_status = completed
* baseline_db_modified = False
* output_db_created = True
* inserted_table_count = 13
* inserted_row_count_total = 130
* fk_validation_status = passed
* forbidden_content_check_status = passed
* raw_data_row_count = 0
* raw_token_row_count = 0
* field_catalog_scientific_row_count = 0

The database now has repository, document, script, run, output, table, relation, source-placeholder, and claim-boundary metadata.

It still contains no real measurement values.

## 3. Decision

Decision:

* next_scope = SYNTHETIC_SAMPLE_DATA_SPEC
* next_step = QSB-DB16_SYNTHETIC_SAMPLE_DATA_SPEC
* following_possible_step = QSB-DB17_SYNTHETIC_SAMPLE_DATA_SCRIPT
* later_possible_step = QSB-DB18_SYNTHETIC_SAMPLE_DATA_EXECUTION
* result_note_step = QSB-DB19_SYNTHETIC_SAMPLE_DATA_RESULT_NOTE
* browser_inspection_step = QSB-DB20_SYNTHETIC_SAMPLE_DB_BROWSER_INSPECTION_PLAN
* allowed_scope = SYNTHETIC_ONLY_SAMPLE_DATA_PLANNING
* database_modification = FORBIDDEN_BY_THIS_NOTE
* sample_execution = FORBIDDEN_BY_THIS_NOTE
* raw_artifact_access = FORBIDDEN
* tim_par_value_reading = FORBIDDEN
* real_data_ingestion = FORBIDDEN
* c60_value_ingestion = FORBIDDEN
* analytics_data_ingestion = FORBIDDEN
* physical_value_interpretation = FORBIDDEN
* residual_analysis_gate = CLOSED
* model_fitting_gate = CLOSED
* bridge_claim_gate = CLOSED
* research_status = RESEARCH_DATA_INFRASTRUCTURE_SYNTHETIC_TEST_PLANNING

The next step should specify the synthetic sample rows.

The execution must remain a separate later block.

## 4. Baseline protection

The metadata-seeded database should remain a stable upstream artifact.

Do not modify directly:

runs/QSB-DB/QSB_DB13_METADATA_SEED/qsb_research_metadata_seed.db

A later synthetic sample execution should copy it into a new run artifact:

runs/QSB-DB/QSB_DB18_SYNTHETIC_SAMPLE_DATA/qsb_research_synthetic_sample.db

This keeps three distinct database states:

1. Empty schema baseline
2. Metadata-seeded database
3. Synthetic-sample database

This separation protects reproducibility and debugging.

## 5. Synthetic-only principle

The first sample data must be artificial and explicitly labeled.

Allowed sample type:

* synthetic technical sample records

Forbidden sample type:

* real TIM/PAR records,
* real pulsar-timing values,
* real raw artifact values,
* real C60 coordinates or graph values,
* real molecular values,
* analytics outputs,
* residuals,
* model-fit values,
* physical interpretation values.

The sample records are test probes for the database infrastructure.

They are not scientific evidence.

## 6. Planned visible data targets

The synthetic sample should make these database areas visible and browsable:

* raw_data_source
* raw_data
* field_catalog
* raw_token_catalog
* etl_transformation_rule
* quality_check_catalog
* quality_check_result
* harmonized_value_view_catalog
* table_catalog
* claim_boundary_catalog

The goal is to test the path:

source placeholder -> raw staging record -> field catalog -> raw token -> quality check -> ETL rule -> harmonized-view metadata -> claim boundary

This is a structural and ETL-behavior test.

It is not a physical analysis.

## 7. Planned synthetic source

A later synthetic sample spec may define one synthetic source:

* source_name = synthetic_qsb_db_test_source
* source_type = synthetic_test_source
* provider_or_project = QSB-DB
* source_url_or_path = synthetic://qsb-db/sample-data/v1
* source_release = synthetic_sample_v1
* source_version = 1.0
* source_download_status = not_applicable
* source_reachability_status = synthetic_internal
* source_corruption_status = not_applicable
* checksum_status = not_applicable
* provenance_confidence = synthetic_controlled
* quarantine_status = not_quarantined
* notes = synthetic-only database infrastructure test source

This source must not point to raw external data.

## 8. Planned synthetic raw_data records

A later synthetic sample spec may define a small set of raw_data records.

Recommended count:

* 5 to 8 synthetic raw_data rows

Suggested cases:

1. clean_numeric_sample
2. blank_value_sample
3. special_character_sample
4. string_numeric_cast_sample
5. scale_normalization_sample
6. missing_value_sample
7. quarantine_candidate_sample
8. harmonization_ready_sample

These cases should test ETL status logic, not physics.

Example statuses:

* raw_ingest_status = synthetic_loaded
* raw_parse_status = parsed_synthetic
* raw_quality_status = checked_synthetic
* blank_check_status = passed / flagged
* special_character_check_status = passed / flagged
* datatype_check_status = passed / cast_required
* unit_detection_status = synthetic_unit_detected / not_applicable
* scale_detection_status = passed / scale_rule_required
* harmonization_status = not_started / rule_defined / harmonized_synthetic
* etl_release_status = raw_only / harmonization_ready / synthetic_harmonized / quarantined
* quarantine_status = not_quarantined / quarantined_synthetic

## 9. Planned field_catalog records

Synthetic field records should demonstrate field typing.

Recommended field examples:

* sample_id
* sample_numeric_value
* sample_text_value
* sample_unit
* sample_status
* sample_missing_marker
* sample_scale_marker

Field statuses should demonstrate:

* raw_type,
* inferred_type,
* harmonized_type,
* semantic_status = synthetic_controlled,
* unit_status,
* scale_status,
* missingness_status.

These are synthetic test fields, not observed scientific fields.

## 10. Planned raw_token_catalog records

The synthetic sample may include raw tokens such as:

* "42.0"
* ""
* "NULL"
* "1.23E+03"
* "value_with_äöü"
* "needs_cast_17"
* "synthetic_missing"

These tokens are synthetic.

They do not represent real TIM/PAR content.

They do not represent real molecular values.

They are inserted only to test parsing, missingness, datatype, special-character, and harmonization paths.

## 11. Planned ETL transformation rules

The synthetic sample may include ETL rules such as:

* cast_text_to_real_synthetic
* blank_to_missing_marker_synthetic
* special_character_preservation_rule
* scale_factor_1000_synthetic
* synthetic_unit_to_si_placeholder
* quarantine_flag_rule_synthetic

These rules must be labeled as synthetic.

No rule may be represented as a real scientific transformation.

## 12. Planned quality checks

The synthetic sample may include quality checks such as:

* check_blank_marker
* check_numeric_cast_possible
* check_special_character_presence
* check_scale_marker
* check_quarantine_reason_required

Quality-check results may point to synthetic raw_data rows.

The goal is to test the quality-check tables and DB Browser readability.

## 13. Planned harmonized-view metadata

The synthetic sample may include a harmonized_value_view_catalog row such as:

* view_name = synthetic_harmonized_sample_view
* view_type = synthetic_test_view
* blind_descriptive_status = synthetic_only
* interpretation_status = not_opened

This does not create an actual SQL view unless a later block explicitly specifies that.

This row documents a synthetic view concept only.

## 14. Claim-boundary rule

Every synthetic sample artifact must keep claims closed.

Default claim-boundary flags:

* physical_interpretation_allowed = 0
* residual_analysis_allowed = 0
* model_fitting_allowed = 0
* bridge_claim_allowed = 0
* value_reading_allowed = 0

For synthetic rows, value_reading_allowed may remain 0 because these are not real values.

The purpose is infrastructure testing, not measurement evaluation.

## 15. Forbidden-content checks

A later execution must verify:

* no TIM/PAR content inserted,
* no real raw artifact content inserted,
* no C60 or molecular values inserted,
* no analytics rows inserted,
* no residuals inserted,
* no model-fit values inserted,
* no claim-boundary rows authorize physical interpretation,
* synthetic rows are clearly labeled synthetic,
* real_data_ingestion = false,
* raw_artifact_access_status = not_performed,
* tim_par_value_reading_status = not_performed.

## 16. Output expectations for QSB-DB18

A later synthetic sample execution should write:

* synthetic_sample_summary.json
* synthetic_sample_insert_counts.csv
* synthetic_sample_table_row_counts.csv
* synthetic_sample_fk_validation.csv
* synthetic_sample_forbidden_content_check.csv
* synthetic_sample_readout.md
* synthetic_sample_config_resolved.json

The synthetic sample database should be written under:

runs/QSB-DB/QSB_DB18_SYNTHETIC_SAMPLE_DATA/qsb_research_synthetic_sample.db

The metadata-seeded DB should not be modified.

## 17. DB Browser expectation

After synthetic sample execution, DB Browser inspection should become meaningfully browsable.

Expected visible areas:

* synthetic source in raw_data_source,
* synthetic staging records in raw_data,
* synthetic fields in field_catalog,
* synthetic raw tokens in raw_token_catalog,
* ETL sample rules in etl_transformation_rule,
* quality checks and results,
* synthetic harmonized-view metadata,
* claim-boundary records showing closed claims.

This is the first intended “stöbern” stage.

## 18. Stop conditions

The route must stop if:

* the sample plan tries to use real TIM/PAR values,
* the sample plan tries to use raw artifact contents,
* the sample plan tries to use C60 numeric or molecular data,
* the sample plan tries to use analytics outputs,
* claim-boundary flags are opened,
* the metadata-seeded DB would be modified directly,
* synthetic records are not clearly labeled,
* real-data ingestion is implied,
* physical interpretation is implied.

A stop condition is a valid technical result.

## 19. Claim boundary

This note defines a synthetic sample data plan.

It does not modify the SQLite database.

It does not insert data.

It does not create sample files.

It does not create SQL files.

It does not create scripts.

It does not inspect raw artifacts.

It does not read TIM/PAR values.

It does not analyze raw data.

This note does not provide evidence for a physical Shapiro-information residual.

This note does not validate the QSB-ST Bridge.

It does not establish spacetime, quantum-gravity, relativistic, pulsar-timing, molecular-structure, or C60 physics claims.

It only plans a synthetic-only, controlled database infrastructure sample so that ETL status, raw staging, field cataloging, token handling, quality checks, harmonization metadata, and claim-boundary behavior can be browsed safely.
