PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS qsb_source_ingest_event (
    ingest_event_id TEXT PRIMARY KEY,
    input_family TEXT NOT NULL,
    input_path TEXT NOT NULL,
    present INTEGER NOT NULL,
    files_read TEXT NOT NULL DEFAULT '',
    row_count_total INTEGER NOT NULL DEFAULT 0,
    source_catalogs_mutated INTEGER NOT NULL DEFAULT 0,
    notes TEXT NOT NULL DEFAULT '',
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CHECK (present IN (0, 1)),
    CHECK (source_catalogs_mutated IN (0, 1))
);

CREATE TABLE IF NOT EXISTS qsb_source_object (
    source_object_id TEXT PRIMARY KEY,
    stable_source_key TEXT NOT NULL UNIQUE,
    source_class TEXT NOT NULL,
    source_name TEXT NOT NULL,
    source_status TEXT NOT NULL,
    evidence_status TEXT NOT NULL,
    claim_boundary_status TEXT NOT NULL,
    origin_gap_run TEXT NOT NULL,
    ingest_event_id TEXT NOT NULL,
    primary_declared_path TEXT,
    notes TEXT NOT NULL DEFAULT '',
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (ingest_event_id) REFERENCES qsb_source_ingest_event(ingest_event_id),
    CHECK (evidence_status IN ('SOURCE_METADATA_ONLY', 'NOT_EVIDENCE', 'REQUIRES_REVIEW')),
    CHECK (claim_boundary_status IN ('NOT_ASSESSED', 'CLAIM_BOUNDARY_REQUIRED', 'FRAMEWORK_INTERNAL_ONLY', 'REWRITE_REQUIRED', 'HUMAN_REVIEW_REQUIRED', 'NOT_A_CLAIM_SOURCE')),
    CHECK (source_status IN ('RESOLVED_EXACT', 'MULTIPLE_EXACT_MATCHES', 'CANDIDATE_ONLY', 'NOT_FOUND', 'DERIVED_FROM_GAP_OUTPUT', 'ARCHIVE_ENTRY_ONLY', 'GENERATED_RUNTIME_ARTIFACT'))
);

CREATE TABLE IF NOT EXISTS qsb_source_file (
    source_file_id TEXT PRIMARY KEY,
    source_object_id TEXT NOT NULL,
    filename TEXT NOT NULL,
    normalized_file_key TEXT NOT NULL,
    declared_path TEXT,
    resolved_path TEXT,
    size_bytes INTEGER,
    sha256 TEXT,
    mtime_iso TEXT,
    file_type TEXT,
    source_status TEXT NOT NULL,
    evidence_status TEXT NOT NULL,
    origin_gap_run TEXT NOT NULL,
    ingest_event_id TEXT NOT NULL,
    notes TEXT NOT NULL DEFAULT '',
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (source_object_id) REFERENCES qsb_source_object(source_object_id),
    FOREIGN KEY (ingest_event_id) REFERENCES qsb_source_ingest_event(ingest_event_id),
    UNIQUE (source_object_id, normalized_file_key),
    CHECK (evidence_status IN ('SOURCE_METADATA_ONLY', 'NOT_EVIDENCE', 'REQUIRES_REVIEW')),
    CHECK (source_status IN ('RESOLVED_EXACT', 'MULTIPLE_EXACT_MATCHES', 'CANDIDATE_ONLY', 'NOT_FOUND', 'DERIVED_FROM_GAP_OUTPUT', 'ARCHIVE_ENTRY_ONLY', 'GENERATED_RUNTIME_ARTIFACT'))
);

CREATE TABLE IF NOT EXISTS qsb_source_archive_entry (
    archive_entry_id TEXT PRIMARY KEY,
    source_file_id TEXT NOT NULL,
    archive_filename TEXT NOT NULL,
    entry_path TEXT NOT NULL,
    normalized_entry_path TEXT NOT NULL,
    entry_classification TEXT NOT NULL,
    entry_size_bytes INTEGER,
    compressed_size_bytes INTEGER,
    crc_or_na TEXT NOT NULL DEFAULT 'NA',
    source_status TEXT NOT NULL,
    evidence_status TEXT NOT NULL,
    origin_gap_run TEXT NOT NULL,
    ingest_event_id TEXT NOT NULL,
    notes TEXT NOT NULL DEFAULT '',
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (source_file_id) REFERENCES qsb_source_file(source_file_id),
    FOREIGN KEY (ingest_event_id) REFERENCES qsb_source_ingest_event(ingest_event_id),
    UNIQUE (source_file_id, normalized_entry_path, crc_or_na),
    CHECK (evidence_status IN ('SOURCE_METADATA_ONLY', 'NOT_EVIDENCE', 'REQUIRES_REVIEW')),
    CHECK (source_status IN ('RESOLVED_EXACT', 'MULTIPLE_EXACT_MATCHES', 'CANDIDATE_ONLY', 'NOT_FOUND', 'DERIVED_FROM_GAP_OUTPUT', 'ARCHIVE_ENTRY_ONLY', 'GENERATED_RUNTIME_ARTIFACT'))
);

CREATE TABLE IF NOT EXISTS qsb_source_relationship (
    source_relationship_id TEXT PRIMARY KEY,
    subject_source_object_id TEXT NOT NULL,
    object_source_object_id TEXT NOT NULL,
    relationship_type TEXT NOT NULL,
    relationship_status TEXT NOT NULL,
    origin_gap_run TEXT NOT NULL,
    ingest_event_id TEXT NOT NULL,
    notes TEXT NOT NULL DEFAULT '',
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (subject_source_object_id) REFERENCES qsb_source_object(source_object_id),
    FOREIGN KEY (object_source_object_id) REFERENCES qsb_source_object(source_object_id),
    FOREIGN KEY (ingest_event_id) REFERENCES qsb_source_ingest_event(ingest_event_id),
    UNIQUE (subject_source_object_id, object_source_object_id, relationship_type),
    CHECK (relationship_type IN ('SUPERSEDES', 'PATCH_OF', 'CONTAINS', 'DERIVED_FROM', 'DUPLICATE_CANDIDATE', 'SAME_FAMILY_AS', 'RELATED_TO', 'CONFLICTS_WITH', 'REFERENCES', 'UNKNOWN_REVIEW')),
    CHECK (relationship_status IN ('ASSERTED_BY_SOURCE', 'INFERRED_REQUIRES_REVIEW', 'REVIEW_ACCEPTED_AS_LINEAGE', 'REVIEW_REJECTED', 'INSUFFICIENT_INFORMATION'))
);

CREATE TABLE IF NOT EXISTS qsb_source_claim_boundary_flag (
    claim_flag_id TEXT PRIMARY KEY,
    source_object_id TEXT NOT NULL,
    source_file_id TEXT,
    claim_boundary_status TEXT NOT NULL,
    risk_note TEXT NOT NULL,
    recommended_handling TEXT NOT NULL,
    origin_gap_run TEXT NOT NULL,
    ingest_event_id TEXT NOT NULL,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (source_object_id) REFERENCES qsb_source_object(source_object_id),
    FOREIGN KEY (source_file_id) REFERENCES qsb_source_file(source_file_id),
    FOREIGN KEY (ingest_event_id) REFERENCES qsb_source_ingest_event(ingest_event_id),
    CHECK (claim_boundary_status IN ('NOT_ASSESSED', 'CLAIM_BOUNDARY_REQUIRED', 'FRAMEWORK_INTERNAL_ONLY', 'REWRITE_REQUIRED', 'HUMAN_REVIEW_REQUIRED', 'NOT_A_CLAIM_SOURCE'))
);

CREATE TABLE IF NOT EXISTS qsb_source_mart_candidate (
    mart_candidate_id TEXT PRIMARY KEY,
    source_object_id TEXT NOT NULL,
    source_file_id TEXT,
    target_area TEXT NOT NULL,
    candidate_status TEXT NOT NULL,
    requires_human_review INTEGER NOT NULL DEFAULT 1 CHECK (requires_human_review IN (0, 1)),
    origin_gap_run TEXT NOT NULL,
    ingest_event_id TEXT NOT NULL,
    notes TEXT NOT NULL DEFAULT '',
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (source_object_id) REFERENCES qsb_source_object(source_object_id),
    FOREIGN KEY (source_file_id) REFERENCES qsb_source_file(source_file_id),
    FOREIGN KEY (ingest_event_id) REFERENCES qsb_source_ingest_event(ingest_event_id),
    CHECK (candidate_status IN ('ACCEPT_AS_SEED', 'HOLD_FOR_REVIEW', 'REQUIRES_REPRODUCTION', 'DO_NOT_MAP_YET'))
);

CREATE TRIGGER IF NOT EXISTS trg_claim_boundary_file_matches_object_insert
BEFORE INSERT ON qsb_source_claim_boundary_flag
FOR EACH ROW
WHEN NEW.source_file_id IS NOT NULL
AND NOT EXISTS (
    SELECT 1 FROM qsb_source_file
    WHERE source_file_id = NEW.source_file_id
      AND source_object_id = NEW.source_object_id
)
BEGIN
    SELECT RAISE(ABORT, 'claim_boundary source_file_id must match source_object_id');
END;

CREATE TRIGGER IF NOT EXISTS trg_claim_boundary_file_matches_object_update
BEFORE UPDATE ON qsb_source_claim_boundary_flag
FOR EACH ROW
WHEN NEW.source_file_id IS NOT NULL
AND NOT EXISTS (
    SELECT 1 FROM qsb_source_file
    WHERE source_file_id = NEW.source_file_id
      AND source_object_id = NEW.source_object_id
)
BEGIN
    SELECT RAISE(ABORT, 'claim_boundary source_file_id must match source_object_id');
END;

CREATE TRIGGER IF NOT EXISTS trg_mart_candidate_file_matches_object_insert
BEFORE INSERT ON qsb_source_mart_candidate
FOR EACH ROW
WHEN NEW.source_file_id IS NOT NULL
AND NOT EXISTS (
    SELECT 1 FROM qsb_source_file
    WHERE source_file_id = NEW.source_file_id
      AND source_object_id = NEW.source_object_id
)
BEGIN
    SELECT RAISE(ABORT, 'mart_candidate source_file_id must match source_object_id');
END;

CREATE TRIGGER IF NOT EXISTS trg_mart_candidate_file_matches_object_update
BEFORE UPDATE ON qsb_source_mart_candidate
FOR EACH ROW
WHEN NEW.source_file_id IS NOT NULL
AND NOT EXISTS (
    SELECT 1 FROM qsb_source_file
    WHERE source_file_id = NEW.source_file_id
      AND source_object_id = NEW.source_object_id
)
BEGIN
    SELECT RAISE(ABORT, 'mart_candidate source_file_id must match source_object_id');
END;

CREATE INDEX IF NOT EXISTS idx_qsb_source_file_sha256 ON qsb_source_file(sha256);
CREATE INDEX IF NOT EXISTS idx_qsb_source_file_normalized_key ON qsb_source_file(source_object_id, normalized_file_key);
CREATE INDEX IF NOT EXISTS idx_qsb_source_object_origin ON qsb_source_object(origin_gap_run, source_class);
CREATE INDEX IF NOT EXISTS idx_qsb_source_archive_entry_norm ON qsb_source_archive_entry(normalized_entry_path);
CREATE INDEX IF NOT EXISTS idx_qsb_source_mart_candidate_target ON qsb_source_mart_candidate(target_area, candidate_status);
