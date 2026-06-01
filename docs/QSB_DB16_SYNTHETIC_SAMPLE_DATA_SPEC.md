# QSB-DB16 — Synthetic Sample Data Specification

Date: 2026-06-02
Status: synthetic sample data specification
Scope: QSB-wide research database infrastructure
Upstream plan: QSB_DB15_SYNTHETIC_SAMPLE_DATA_PLAN
Baseline metadata DB: runs/QSB-DB/QSB_DB13_METADATA_SEED/qsb_research_metadata_seed.db
Planned synthetic sample DB: runs/QSB-DB/QSB_DB18_SYNTHETIC_SAMPLE_DATA/qsb_research_synthetic_sample.db
Sample mode: synthetic-only controlled test data
Raw artifact access: no raw artifact inspection by this note
Physics-analysis status: closed for physical interpretation, residual search, and model fitting
Tracking decision: this documentation note may be tracked; SQLite database artifacts remain run artifacts

## 1. Purpose

This note specifies the first controlled synthetic sample data set for the QSB SQLite research database.

The goal is to make the database meaningfully browsable while keeping all real-data gates closed.

The sample data are artificial technical probes for the database infrastructure.

They are intended to test:

* source registration,
* raw staging,
* field cataloging,
* token handling,
* blank handling,
* special-character handling,
* datatype casting status,
* scale-normalization status,
* quarantine status,
* ETL rule metadata,
* quality checks,
* harmonized-view metadata,
* closed claim boundaries.

This note does not modify the database.

This note does not insert data.

This note does not create SQL files.

This note does not create scripts.

This note does not inspect raw artifacts.

This note does not read TIM/PAR values.

This note does not analyze raw data.

## 2. Upstream state

QSB-DB13 created the metadata-seeded database artifact:

runs/QSB-DB/QSB_DB13_METADATA_SEED/qsb_research_metadata_seed.db

QSB-DB14 documented that the metadata seed was successful:

* metadata_seed_status = completed
* inserted_table_count = 13
* inserted_row_count_total = 130
* fk_validation_status = passed
* forbidden_content_check_status = passed
* raw_data_row_count = 0
* raw_token_row_count = 0
* field_catalog_scientific_row_count = 0

QSB-DB15 planned the first synthetic-only data path.

The synthetic sample execution should later create:

runs/QSB-DB/QSB_DB18_SYNTHETIC_SAMPLE_DATA/qsb_research_synthetic_sample.db

The metadata-seeded DB must remain unchanged.

## 3. Decision

Decision:

* next_scope = SYNTHETIC_SAMPLE_DATA_SCRIPT
* next_step = QSB-DB17_SYNTHETIC_SAMPLE_DATA_SCRIPT
* following_possible_step = QSB-DB18_SYNTHETIC_SAMPLE_DATA_EXECUTION
* result_note_step = QSB-DB19_SYNTHETIC_SAMPLE_DATA_RESULT_NOTE
* browser_inspection_step = QSB-DB20_SYNTHETIC_SAMPLE_DB_BROWSER_INSPECTION_PLAN
* allowed_scope = SYNTHETIC_ONLY_SAMPLE_DATA_SPECIFICATION
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
* research_status = RESEARCH_DATA_INFRASTRUCTURE_SYNTHETIC_SAMPLE_SPECIFICATION

The next step may create a script.

Execution must remain a later separate block.

## 4. Synthetic-only rule

All sample records must be explicitly synthetic.

No sample row may represent:

* real TIM/PAR content,
* real pulsar-timing values,
* real raw artifact content,
* real C60 coordinates,
* real molecular graph values,
* analytics outputs,
* residuals,
* model-fit values,
* physical interpretations.

All sample rows must carry wording such as:

* synthetic
* synthetic_only
* synthetic_controlled
* not_physical_data
* not_real_measurement

The sample is infrastructure test material only.

## 5. Target database path

Later execution should copy:

runs/QSB-DB/QSB_DB13_METADATA_SEED/qsb_research_metadata_seed.db

to:

runs/QSB-DB/QSB_DB18_SYNTHETIC_SAMPLE_DATA/qsb_research_synthetic_sample.db

The metadata-seeded DB must not be modified.

The synthetic-sample DB is a separate run artifact.

## 6. Synthetic source specification

Insert one synthetic source into `raw_data_source`.

Planned row:

* source_name = synthetic_qsb_db_test_source
* source_type = synthetic_test_source
* provider_or_project = QSB-DB
* source_url_or_path = synthetic://qsb-db/sample-data/v1
* source_release = synthetic_sample_v1
* source_version = 1.0
* source_access_date = 2026-06-02
* source_download_status = not_applicable
* source_reachability_status = synthetic_internal
* source_corruption_status = not_applicable
* checksum_status = not_applicable
* license_or_usage_note = synthetic internal test data only
* provenance_confidence = synthetic_controlled
* quarantine_status = not_quarantined
* notes = synthetic-only database infrastructure test source; no raw external data

This source must not point to raw external data.

## 7. Synthetic raw_data row specification

Insert 8 synthetic `raw_data` rows linked to `synthetic_qsb_db_test_source`.

Required synthetic cases:

1. clean_numeric_sample
2. blank_value_sample
3. special_character_sample
4. string_numeric_cast_sample
5. scale_normalization_sample
6. missing_value_sample
7. quarantine_candidate_sample
8. harmonization_ready_sample

Common required properties:

* raw_data_source_id links to synthetic_qsb_db_test_source
* raw_artifact_id = synthetic_artifact_v1
* source_local_file_id = synthetic_file_v1
* source_local_record_id = synthetic_record_001 through synthetic_record_008
* source_local_measurement_id = synthetic_measurement_001 through synthetic_measurement_008
* raw_object_type = synthetic_record
* raw_file_type = synthetic_inline_test
* notes must include synthetic_only and not_physical_data

Planned row details:

### clean_numeric_sample

* source_local_record_id = synthetic_record_001
* raw_ingest_status = synthetic_loaded
* raw_parse_status = parsed_synthetic
* raw_quality_status = checked_synthetic
* blank_check_status = passed
* special_character_check_status = passed
* datatype_check_status = passed
* unit_detection_status = synthetic_unit_detected
* scale_detection_status = passed
* harmonization_status = rule_defined
* etl_release_status = harmonization_ready
* quarantine_status = not_quarantined
* retry_possible = 1

### blank_value_sample

* source_local_record_id = synthetic_record_002
* blank_check_status = flagged
* datatype_check_status = unresolved_blank
* unit_detection_status = not_applicable
* harmonization_status = needs_missing_value_rule
* etl_release_status = raw_only
* quarantine_status = not_quarantined
* retry_possible = 1

### special_character_sample

* source_local_record_id = synthetic_record_003
* special_character_check_status = flagged
* datatype_check_status = passed_text
* unit_detection_status = not_applicable
* harmonization_status = rule_defined
* etl_release_status = harmonization_ready
* quarantine_status = not_quarantined
* retry_possible = 1

### string_numeric_cast_sample

* source_local_record_id = synthetic_record_004
* blank_check_status = passed
* special_character_check_status = passed
* datatype_check_status = cast_required
* unit_detection_status = synthetic_unit_detected
* scale_detection_status = passed
* harmonization_status = rule_defined
* etl_release_status = harmonization_ready
* quarantine_status = not_quarantined
* retry_possible = 1

### scale_normalization_sample

* source_local_record_id = synthetic_record_005
* datatype_check_status = passed
* unit_detection_status = synthetic_unit_detected
* scale_detection_status = scale_rule_required
* harmonization_status = rule_defined
* etl_release_status = harmonization_ready
* quarantine_status = not_quarantined
* retry_possible = 1

### missing_value_sample

* source_local_record_id = synthetic_record_006
* blank_check_status = flagged
* datatype_check_status = missing_marker_detected
* unit_detection_status = not_applicable
* scale_detection_status = not_applicable
* harmonization_status = needs_missing_value_rule
* etl_release_status = raw_only
* quarantine_status = not_quarantined
* retry_possible = 1

### quarantine_candidate_sample

* source_local_record_id = synthetic_record_007
* raw_quality_status = flagged_synthetic
* blank_check_status = passed
* special_character_check_status = flagged
* datatype_check_status = unresolved
* unit_detection_status = unresolved
* scale_detection_status = unresolved
* harmonization_status = blocked_by_quality
* etl_release_status = quarantined
* quarantine_status = quarantined_synthetic
* quarantine_reason = synthetic_quality_stop_condition
* retry_possible = 1

### harmonization_ready_sample

* source_local_record_id = synthetic_record_008
* blank_check_status = passed
* special_character_check_status = passed
* datatype_check_status = passed
* unit_detection_status = synthetic_unit_detected
* scale_detection_status = passed
* harmonization_status = synthetic_harmonized
* etl_release_status = synthetic_harmonized
* quarantine_status = not_quarantined
* retry_possible = 1

## 8. Synthetic field_catalog specification

Insert synthetic `field_catalog` rows representing synthetic fields.

Recommended rows:

1. sample_id
2. sample_numeric_value
3. sample_text_value
4. sample_unit
5. sample_status
6. sample_missing_marker
7. sample_scale_marker

Common values:

* semantic_status = synthetic_controlled
* correction_state_relevance = not_applicable_synthetic
* notes must include synthetic_only

Field details:

### sample_id

* raw_type = text
* inferred_type = text
* harmonized_type = text
* unit_status = not_applicable
* scale_status = not_applicable
* missingness_status = required

### sample_numeric_value

* raw_type = mixed_text_numeric
* inferred_type = real_or_castable_text
* harmonized_type = real
* unit_status = synthetic_unit
* scale_status = scale_checked
* missingness_status = nullable_synthetic

### sample_text_value

* raw_type = text
* inferred_type = text
* harmonized_type = text
* unit_status = not_applicable
* scale_status = not_applicable
* missingness_status = nullable_synthetic

### sample_unit

* raw_type = text
* inferred_type = unit_marker
* harmonized_type = synthetic_unit_marker
* unit_status = synthetic_unit_detected
* scale_status = not_applicable
* missingness_status = nullable_synthetic

### sample_status

* raw_type = text
* inferred_type = status_marker
* harmonized_type = status_marker
* unit_status = not_applicable
* scale_status = not_applicable
* missingness_status = required

### sample_missing_marker

* raw_type = text
* inferred_type = missing_marker
* harmonized_type = missing_marker
* unit_status = not_applicable
* scale_status = not_applicable
* missingness_status = test_case

### sample_scale_marker

* raw_type = text
* inferred_type = scale_marker
* harmonized_type = scale_marker
* unit_status = not_applicable
* scale_status = scale_rule_required
* missingness_status = nullable_synthetic

## 9. Synthetic raw_token_catalog specification

Insert synthetic raw tokens linked to the synthetic raw_data rows and field_catalog rows.

Required tokens:

* "42.0"
* ""
* "NULL"
* "1.23E+03"
* "value_with_äöü"
* "needs_cast_17"
* "synthetic_missing"
* "scale_x1000"
* "quarantine_candidate"
* "harmonization_ready"

Token rules:

* raw_token values are artificial test strings.
* token_type_guess must be synthetic_numeric, synthetic_blank, synthetic_missing, synthetic_text, synthetic_cast_candidate, synthetic_scale_marker, or synthetic_status.
* parse_status must be synthetic_parsed, synthetic_flagged, or synthetic_unresolved.
* quarantine_status must be not_quarantined or quarantined_synthetic.
* notes must include no_TIM_PAR_content and synthetic_only.

## 10. Synthetic ETL transformation rule specification

Insert synthetic `etl_transformation_rule` rows.

Required rules:

1. cast_text_to_real_synthetic
2. blank_to_missing_marker_synthetic
3. special_character_preservation_rule_synthetic
4. scale_factor_1000_synthetic
5. synthetic_unit_to_si_placeholder
6. quarantine_flag_rule_synthetic

Rules must be metadata rules only.

No rule may represent real physical transformation.

Planned details:

### cast_text_to_real_synthetic

* rule_type = cast
* transformation_expression = CAST synthetic text numeric token to REAL
* cast_rule = text_to_real_synthetic
* reversible_flag = 0
* allowed_for_analytics = 0

### blank_to_missing_marker_synthetic

* rule_type = missing_value_handling
* transformation_expression = map blank synthetic token to synthetic_missing
* missing_value_rule = blank_to_synthetic_missing
* reversible_flag = 0
* allowed_for_analytics = 0

### special_character_preservation_rule_synthetic

* rule_type = special_character_cleanup
* transformation_expression = preserve unicode marker while flagging special characters
* special_character_rule = preserve_and_flag
* reversible_flag = 1
* allowed_for_analytics = 0

### scale_factor_1000_synthetic

* rule_type = scale_normalization
* transformation_expression = synthetic_value / 1000
* scale_rule = divide_by_1000_synthetic
* reversible_flag = 1
* allowed_for_analytics = 0

### synthetic_unit_to_si_placeholder

* rule_type = unit_harmonization
* transformation_expression = map synthetic_unit to synthetic_si_placeholder
* unit_before = synthetic_unit
* unit_after = synthetic_si_placeholder
* reversible_flag = 0
* allowed_for_analytics = 0

### quarantine_flag_rule_synthetic

* rule_type = quality_gate
* transformation_expression = if unresolved datatype and unresolved unit then quarantine_synthetic
* reversible_flag = 0
* allowed_for_analytics = 0

## 11. Synthetic quality_check_catalog specification

Insert quality check definitions.

Required checks:

1. check_blank_marker_synthetic
2. check_numeric_cast_possible_synthetic
3. check_special_character_presence_synthetic
4. check_scale_marker_synthetic
5. check_quarantine_reason_required_synthetic

Common fields:

* severity = synthetic_test
* stop_if_failed = 0 except check_quarantine_reason_required_synthetic may use 1
* notes must include synthetic_only

## 12. Synthetic quality_check_result specification

Insert quality check results linked to synthetic raw_data rows.

Suggested result cases:

* clean_numeric_sample: passed numeric cast check
* blank_value_sample: flagged blank marker
* special_character_sample: flagged special character presence
* string_numeric_cast_sample: passed cast possible
* scale_normalization_sample: flagged scale marker
* quarantine_candidate_sample: passed quarantine reason required
* harmonization_ready_sample: passed synthetic readiness check

No result is a scientific result.

## 13. Synthetic harmonized_value_view_catalog specification

Insert one harmonized-view metadata row:

* view_name = synthetic_harmonized_sample_view
* view_type = synthetic_test_view
* source_table_ids = raw_data,field_catalog,raw_token_catalog,etl_transformation_rule,quality_check_result
* transformation_rule_set = synthetic_sample_rule_set_v1
* blind_descriptive_status = synthetic_only
* interpretation_status = not_opened
* notes = synthetic view metadata only; no SQL view created by this step

This row does not create an actual SQL view.

## 14. Synthetic claim-boundary specification

Insert claim-boundary rows for synthetic sample objects.

Required defaults:

* physical_interpretation_allowed = 0
* residual_analysis_allowed = 0
* model_fitting_allowed = 0
* bridge_claim_allowed = 0
* value_reading_allowed = 0

Applies to:

* synthetic_sample_source
* synthetic_raw_data_rows
* synthetic_raw_tokens
* synthetic_etl_rules
* synthetic_quality_checks
* synthetic_harmonized_view_metadata

No synthetic row may authorize physical interpretation.

## 15. Expected row-count additions

Approximate expected row additions:

* raw_data_source: 1
* raw_data: 8
* field_catalog: 7
* raw_token_catalog: 10
* etl_transformation_rule: 6
* quality_check_catalog: 5
* quality_check_result: 7
* harmonized_value_view_catalog: 1
* claim_boundary_catalog: 6

Expected total synthetic additions:

* approximately 51 rows

Exact row count may vary slightly if later script adds audit_log records or table relation metadata.

The execution must report actual inserted counts.

## 16. Forbidden-content checks

A later execution must verify:

* no real TIM/PAR content inserted,
* no `.tim` or `.par` raw artifact content inserted,
* no real C60 numeric or molecular values inserted,
* no analytics rows inserted,
* no residual rows inserted,
* no model-fit rows inserted,
* no claim-boundary row authorizes physical interpretation,
* all synthetic source/sample/token/rule rows are clearly labeled synthetic,
* raw_artifact_access_status = not_performed,
* tim_par_value_reading_status = not_performed,
* documentation_download_status = not_performed,
* real_data_ingestion = false,
* c60_value_ingestion = false,
* analytics_data_ingestion = false.

## 17. Output expectations for QSB-DB18

A later synthetic sample execution should write:

* synthetic_sample_summary.json
* synthetic_sample_insert_counts.csv
* synthetic_sample_table_row_counts.csv
* synthetic_sample_fk_validation.csv
* synthetic_sample_forbidden_content_check.csv
* synthetic_sample_readout.md
* synthetic_sample_config_resolved.json

Expected output DB:

runs/QSB-DB/QSB_DB18_SYNTHETIC_SAMPLE_DATA/qsb_research_synthetic_sample.db

The metadata-seeded DB should not be modified.

## 18. DB Browser expectation

After execution, DB Browser should show browsable synthetic data in:

* raw_data_source
* raw_data
* field_catalog
* raw_token_catalog
* etl_transformation_rule
* quality_check_catalog
* quality_check_result
* harmonized_value_view_catalog
* claim_boundary_catalog

This should provide the first meaningful database browsing stage without exposing real scientific data.

## 19. Stop conditions

The route must stop if:

* any real TIM/PAR value is introduced,
* any raw artifact content is introduced,
* any C60 numeric or molecular value is introduced,
* any analytics output is introduced,
* any residual or model-fit value is introduced,
* any claim-boundary flag authorizes physical interpretation,
* the metadata-seeded DB would be modified directly,
* synthetic labels are missing,
* real-data ingestion is implied,
* physical interpretation is implied.

A stop condition is a valid technical result.

## 20. Claim boundary

This note specifies synthetic sample data only.

This note does not modify the SQLite database.

This note does not insert data.

This note does not create sample files.

This note does not create SQL files.

This note does not create scripts.

This note does not inspect raw artifacts.

This note does not read TIM/PAR values.

This note does not analyze raw data.

This note does not provide evidence for a physical Shapiro-information residual.

This note does not validate the QSB-ST Bridge.

This note does not establish spacetime, quantum-gravity, relativistic, pulsar-timing, molecular-structure, or C60 physics claims.

It only specifies a synthetic-only controlled sample data set for testing database infrastructure behavior, ETL status readability, quality-check visibility, raw staging behavior, and claim-boundary closure.
