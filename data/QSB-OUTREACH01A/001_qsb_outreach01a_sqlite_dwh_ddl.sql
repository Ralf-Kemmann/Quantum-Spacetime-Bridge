-- QSB-OUTREACH01A SQLite DWH DDL proposal.
-- Review artifact only; not executed during setup or correction run.
-- Adapted from PostgreSQL scaffold to the local QSB-DWH SQLite convention.
-- Claim boundary: this schema supports lineage and methodological review only.

PRAGMA foreign_keys = ON;

CREATE TABLE outreach_case (
    outreach_case_id TEXT PRIMARY KEY,
    case_code TEXT NOT NULL UNIQUE,
    title TEXT NOT NULL,
    description TEXT,
    status TEXT NOT NULL DEFAULT 'draft',
    claim_boundary TEXT NOT NULL DEFAULT 'methodological_contact_package_only',
    created_at_utc TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at_utc TEXT,
    CHECK (status IN ('draft', 'review', 'ready', 'hold'))
);

CREATE TABLE outreach_raw_observation (
    raw_observation_id TEXT PRIMARY KEY,
    outreach_case_id TEXT NOT NULL REFERENCES outreach_case(outreach_case_id),
    source_record_id TEXT NOT NULL,
    source_uri TEXT,
    source_payload_json TEXT NOT NULL,
    source_checksum TEXT,
    source_checksum_algorithm TEXT,
    raw_immutability_status TEXT NOT NULL DEFAULT 'preserved',
    ingested_at_utc TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (outreach_case_id, raw_observation_id),
    UNIQUE (outreach_case_id, source_record_id),
    CHECK (
        (source_checksum IS NULL AND source_checksum_algorithm IS NULL)
        OR (source_checksum IS NOT NULL AND source_checksum_algorithm IS NOT NULL)
    ),
    CHECK (raw_immutability_status IN ('preserved', 'quarantined_reference', 'unavailable'))
);

CREATE TABLE outreach_staging_state (
    staging_state_id TEXT PRIMARY KEY,
    outreach_case_id TEXT NOT NULL,
    raw_observation_id TEXT NOT NULL,
    source_record_id TEXT NOT NULL,
    event_instance_id TEXT NOT NULL,
    state_descriptor_id TEXT NOT NULL,
    state_id_candidate TEXT NOT NULL,
    forcing_cycle_index INTEGER,
    forcing_phase REAL,
    response_phase_class_candidate TEXT,
    observable_recurrence_class_candidate TEXT,
    background_state_type TEXT,
    background_state_json TEXT,
    history_representation_type TEXT NOT NULL DEFAULT 'none',
    history_descriptor_json TEXT,
    history_window_start REAL,
    history_window_end REAL,
    history_embedding_method TEXT,
    history_embedding_version TEXT,
    staging_status TEXT NOT NULL DEFAULT 'draft',
    created_at_utc TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (outreach_case_id, staging_state_id),
    UNIQUE (outreach_case_id, event_instance_id),
    FOREIGN KEY (outreach_case_id, raw_observation_id)
        REFERENCES outreach_raw_observation(outreach_case_id, raw_observation_id),
    CHECK (history_representation_type IN ('none', 'finite_history_features', 'delay_window', 'embedded_history_vector')),
    CHECK (staging_status IN ('draft', 'review', 'accepted', 'rejected'))
);

CREATE TABLE outreach_transformation_rule (
    transformation_rule_id TEXT PRIMARY KEY,
    rule_code TEXT NOT NULL,
    rule_version TEXT NOT NULL,
    input_layer TEXT NOT NULL,
    output_layer TEXT NOT NULL,
    rule_definition_json TEXT NOT NULL,
    created_at_utc TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (rule_code, rule_version)
);

CREATE TABLE outreach_harmonized_state (
    harmonized_state_id TEXT PRIMARY KEY,
    outreach_case_id TEXT NOT NULL,
    raw_observation_id TEXT NOT NULL,
    staging_state_id TEXT,
    transformation_rule_id TEXT REFERENCES outreach_transformation_rule(transformation_rule_id),
    event_instance_id TEXT NOT NULL,
    state_descriptor_id TEXT NOT NULL,
    state_id TEXT NOT NULL,
    source_record_id TEXT NOT NULL,
    forcing_cycle_index INTEGER NOT NULL,
    forcing_phase REAL,
    response_phase_class TEXT,
    observable_recurrence_class TEXT,
    full_state_equivalence_class TEXT,
    domain_label TEXT,
    background_state_type TEXT,
    background_state_json TEXT,
    history_representation_type TEXT NOT NULL DEFAULT 'none',
    history_descriptor_json TEXT,
    history_window_start REAL,
    history_window_end REAL,
    history_embedding_method TEXT,
    history_embedding_version TEXT,
    transformation_version TEXT NOT NULL,
    harmonization_status TEXT NOT NULL DEFAULT 'draft',
    created_at_utc TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (outreach_case_id, harmonized_state_id),
    UNIQUE (outreach_case_id, event_instance_id),
    UNIQUE (outreach_case_id, state_id),
    FOREIGN KEY (outreach_case_id, raw_observation_id)
        REFERENCES outreach_raw_observation(outreach_case_id, raw_observation_id),
    FOREIGN KEY (outreach_case_id, staging_state_id)
        REFERENCES outreach_staging_state(outreach_case_id, staging_state_id),
    CHECK (history_representation_type IN ('none', 'finite_history_features', 'delay_window', 'embedded_history_vector')),
    CHECK (harmonization_status IN ('draft', 'review', 'accepted', 'rejected'))
);

CREATE TABLE outreach_state_feature (
    state_feature_id TEXT PRIMARY KEY,
    harmonized_state_id TEXT NOT NULL REFERENCES outreach_harmonized_state(harmonized_state_id),
    feature_name TEXT NOT NULL,
    feature_value_numeric REAL,
    feature_value_text TEXT,
    unit_code TEXT,
    feature_family TEXT,
    normalization_rule TEXT,
    feature_status TEXT NOT NULL DEFAULT 'draft',
    UNIQUE (harmonized_state_id, feature_name),
    CHECK (feature_status IN ('draft', 'accepted', 'rejected'))
);

CREATE TABLE outreach_model_run (
    model_run_id TEXT PRIMARY KEY,
    outreach_case_id TEXT NOT NULL REFERENCES outreach_case(outreach_case_id),
    run_code TEXT NOT NULL UNIQUE,
    model_version TEXT NOT NULL,
    parameter_config_json TEXT NOT NULL,
    git_commit_hash TEXT,
    run_status TEXT NOT NULL,
    started_at_utc TEXT,
    completed_at_utc TEXT,
    UNIQUE (outreach_case_id, model_run_id),
    CHECK (run_status IN ('planned', 'running', 'completed', 'failed', 'blocked'))
);

CREATE TABLE outreach_relational_pair (
    relational_pair_id TEXT PRIMARY KEY,
    outreach_case_id TEXT NOT NULL,
    model_run_id TEXT NOT NULL,
    state_i_id TEXT NOT NULL,
    state_j_id TEXT NOT NULL,
    pair_logic TEXT NOT NULL DEFAULT 'symmetric_canonical_order',
    similarity_score REAL NOT NULL,
    phase_distance REAL,
    cycle_distance INTEGER,
    observable_match INTEGER,
    class_match INTEGER,
    edge_status INTEGER,
    relation_status TEXT NOT NULL DEFAULT 'derived',
    FOREIGN KEY (outreach_case_id, model_run_id)
        REFERENCES outreach_model_run(outreach_case_id, model_run_id),
    FOREIGN KEY (outreach_case_id, state_i_id)
        REFERENCES outreach_harmonized_state(outreach_case_id, harmonized_state_id),
    FOREIGN KEY (outreach_case_id, state_j_id)
        REFERENCES outreach_harmonized_state(outreach_case_id, harmonized_state_id),
    CHECK (state_i_id <> state_j_id),
    CHECK (state_i_id < state_j_id),
    CHECK (pair_logic = 'symmetric_canonical_order'),
    CHECK (observable_match IN (0, 1) OR observable_match IS NULL),
    CHECK (class_match IN (0, 1) OR class_match IS NULL),
    CHECK (edge_status IN (0, 1) OR edge_status IS NULL),
    CHECK (relation_status IN ('derived', 'review', 'accepted', 'rejected')),
    UNIQUE (model_run_id, state_i_id, state_j_id)
);

CREATE TABLE outreach_analytical_result (
    analytical_result_id TEXT PRIMARY KEY,
    model_run_id TEXT NOT NULL REFERENCES outreach_model_run(model_run_id),
    result_code TEXT NOT NULL,
    result_status TEXT NOT NULL,
    result_value_json TEXT NOT NULL,
    interpretation_level TEXT NOT NULL DEFAULT 'derived',
    claim_boundary TEXT NOT NULL DEFAULT 'no_physical_validation_claim',
    created_at_utc TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (model_run_id, result_code),
    CHECK (result_status IN ('draft', 'derived', 'review', 'accepted', 'rejected')),
    CHECK (interpretation_level IN ('observed', 'derived', 'interpretive_note'))
);

CREATE INDEX idx_outreach_raw_observation_case ON outreach_raw_observation(outreach_case_id);
CREATE INDEX idx_outreach_staging_state_case ON outreach_staging_state(outreach_case_id);
CREATE INDEX idx_outreach_staging_state_raw ON outreach_staging_state(raw_observation_id);
CREATE INDEX idx_outreach_harmonized_state_case ON outreach_harmonized_state(outreach_case_id);
CREATE INDEX idx_outreach_harmonized_state_raw ON outreach_harmonized_state(raw_observation_id);
CREATE INDEX idx_outreach_harmonized_state_descriptor ON outreach_harmonized_state(state_descriptor_id);
CREATE INDEX idx_outreach_state_feature_state ON outreach_state_feature(harmonized_state_id);
CREATE INDEX idx_outreach_model_run_case ON outreach_model_run(outreach_case_id);
CREATE INDEX idx_outreach_relational_pair_case ON outreach_relational_pair(outreach_case_id);
CREATE INDEX idx_outreach_relational_pair_run ON outreach_relational_pair(model_run_id);
CREATE INDEX idx_outreach_relational_pair_state_i ON outreach_relational_pair(state_i_id);
CREATE INDEX idx_outreach_relational_pair_state_j ON outreach_relational_pair(state_j_id);
CREATE INDEX idx_outreach_analytical_result_run ON outreach_analytical_result(model_run_id);
