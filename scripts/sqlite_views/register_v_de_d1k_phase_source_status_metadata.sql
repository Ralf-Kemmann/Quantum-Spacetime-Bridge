CREATE TABLE IF NOT EXISTS qsb_view_metadata_registry (
    artifact_id TEXT PRIMARY KEY,
    artifact_kind TEXT NOT NULL,
    artifact_path TEXT NOT NULL,
    view_name TEXT NOT NULL,
    source_path TEXT NOT NULL,
    source_run_id TEXT,
    source_block_id TEXT,
    claim_boundary TEXT NOT NULL,
    evidence_class TEXT NOT NULL,
    allowed_use TEXT NOT NULL,
    blocked_use TEXT NOT NULL,
    created_by TEXT NOT NULL,
    created_at_utc TEXT DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ','now')),
    notes TEXT
);

INSERT OR REPLACE INTO qsb_view_metadata_registry (
    artifact_id,
    artifact_kind,
    artifact_path,
    view_name,
    source_path,
    source_run_id,
    source_block_id,
    claim_boundary,
    evidence_class,
    allowed_use,
    blocked_use,
    created_by,
    notes
) VALUES (
    'VIEW-DE-D1K-PHASE-SOURCE-STATUS',
    'sqlite_view_definition',
    'scripts/sqlite_views/v_de_d1k_phase_source_status.sql',
    'v_de_d1k_phase_source_status',
    'runs/QSB-ST-COMP01D1K/deterministic_synthetic_phase_field_exposure_open/phase_exposed_case_profile_summary.csv',
    'deterministic_synthetic_phase_field_exposure_open',
    'QSB-ST-COMP01D1K',
    'synthetic diagnostic deterministic phase-field exposure extension only',
    'synthetic_diagnostic_phase_view_not_real_source',
    'Human-readable German DWH view for D1K phase-source status and claim boundary inspection.',
    'REAL01 evidence; physical phase claim; physical C-layer source; Bridge validation; spacetime/metric interpretation.',
    'manual_qsb_metadata_link',
    'Registers the German D1K phase-source status view as a metadata-linked artifact. Existing meta_* tables are not modified.'
);

DROP VIEW IF EXISTS v_de_qsb_view_metadata_registry;

CREATE VIEW v_de_qsb_view_metadata_registry AS
SELECT
    artifact_id AS "Artefakt-ID",
    artifact_kind AS "Artefaktart",
    artifact_path AS "Artefaktpfad",
    view_name AS "View-Name",
    source_path AS "Quellpfad",
    source_run_id AS "Quelllauf-ID",
    source_block_id AS "Quellblock",
    CASE evidence_class
        WHEN 'synthetic_diagnostic_phase_view_not_real_source'
        THEN 'Synthetische Diagnose-View; keine reale Quelle'
        ELSE evidence_class
    END AS "Evidenzklasse, lesbar",
    claim_boundary AS "Claim Boundary",
    allowed_use AS "Erlaubte Verwendung",
    blocked_use AS "Gesperrte Verwendung",
    created_at_utc AS "Registriert am",
    notes AS "Notiz"
FROM qsb_view_metadata_registry;
