PRAGMA foreign_keys = ON;

CREATE TABLE qsb_artifact (
    artifact_id TEXT PRIMARY KEY,
    title TEXT NOT NULL,
    artifact_type TEXT NOT NULL,
    semantic_role TEXT NOT NULL,
    mime_type TEXT,
    file_extension TEXT,
    canonical_path TEXT NOT NULL,
    uri TEXT,
    content_hash TEXT NOT NULL,
    hash_algorithm TEXT NOT NULL DEFAULT 'sha256',
    size_bytes INTEGER,
    created_at TEXT NOT NULL,
    created_by TEXT,
    source_system TEXT,
    status TEXT NOT NULL,
    visibility TEXT NOT NULL,
    notes TEXT
);

CREATE TABLE qsb_artifact_version (
    artifact_version_id TEXT PRIMARY KEY,
    artifact_id TEXT NOT NULL,
    version TEXT NOT NULL,
    canonical_path TEXT NOT NULL,
    content_hash TEXT NOT NULL,
    generated_at TEXT NOT NULL,
    generator_name TEXT,
    generator_version TEXT,
    supersedes_version_id TEXT,
    change_summary TEXT,
    status TEXT NOT NULL,
    FOREIGN KEY (artifact_id) REFERENCES qsb_artifact(artifact_id),
    FOREIGN KEY (supersedes_version_id) REFERENCES qsb_artifact_version(artifact_version_id)
);

CREATE TABLE qsb_artifact_lineage (
    lineage_id TEXT PRIMARY KEY,
    artifact_id TEXT NOT NULL,
    source_type TEXT NOT NULL,
    source_ref TEXT NOT NULL,
    source_artifact_id TEXT,
    source_table TEXT,
    source_query TEXT,
    run_id TEXT,
    evidence_role TEXT NOT NULL,
    transformation_summary TEXT,
    status TEXT NOT NULL,
    FOREIGN KEY (artifact_id) REFERENCES qsb_artifact(artifact_id),
    FOREIGN KEY (source_artifact_id) REFERENCES qsb_artifact(artifact_id)
);

CREATE TABLE qsb_artifact_relation (
    relation_id TEXT PRIMARY KEY,
    source_artifact_id TEXT NOT NULL,
    target_artifact_id TEXT NOT NULL,
    relation_type TEXT NOT NULL,
    relation_label TEXT,
    status TEXT NOT NULL,
    FOREIGN KEY (source_artifact_id) REFERENCES qsb_artifact(artifact_id),
    FOREIGN KEY (target_artifact_id) REFERENCES qsb_artifact(artifact_id)
);

CREATE TABLE qsb_artifact_alias (
    alias_id TEXT PRIMARY KEY,
    artifact_id TEXT NOT NULL,
    alias TEXT NOT NULL,
    language TEXT NOT NULL,
    alias_type TEXT NOT NULL,
    status TEXT NOT NULL,
    FOREIGN KEY (artifact_id) REFERENCES qsb_artifact(artifact_id)
);

CREATE TABLE qsb_artifact_text_index (
    text_index_id TEXT PRIMARY KEY,
    artifact_id TEXT NOT NULL,
    text_role TEXT NOT NULL,
    language TEXT,
    extracted_text_path TEXT,
    text_hash TEXT,
    excerpt TEXT,
    extraction_method TEXT,
    extraction_status TEXT NOT NULL,
    FOREIGN KEY (artifact_id) REFERENCES qsb_artifact(artifact_id)
);

CREATE TABLE qsb_artifact_claim_boundary (
    boundary_id TEXT PRIMARY KEY,
    artifact_id TEXT NOT NULL,
    admissible_use TEXT NOT NULL,
    forbidden_use TEXT NOT NULL,
    overclaim_risk TEXT NOT NULL,
    review_status TEXT NOT NULL,
    notes TEXT,
    FOREIGN KEY (artifact_id) REFERENCES qsb_artifact(artifact_id)
);

CREATE TABLE qsb_artifact_export (
    export_id TEXT PRIMARY KEY,
    artifact_id TEXT NOT NULL,
    export_type TEXT NOT NULL,
    output_path TEXT NOT NULL,
    generated_at TEXT NOT NULL,
    generator_name TEXT,
    generator_version TEXT,
    content_hash TEXT NOT NULL,
    download_label TEXT,
    status TEXT NOT NULL,
    FOREIGN KEY (artifact_id) REFERENCES qsb_artifact(artifact_id)
);

CREATE TABLE qsb_artifact_review (
    review_id TEXT PRIMARY KEY,
    artifact_id TEXT NOT NULL,
    reviewer_role TEXT NOT NULL,
    review_status TEXT NOT NULL,
    review_note TEXT,
    reviewed_at TEXT NOT NULL,
    FOREIGN KEY (artifact_id) REFERENCES qsb_artifact(artifact_id)
);

CREATE TABLE qsb_artifact_validation_result (
    validation_id TEXT PRIMARY KEY,
    rule_id TEXT NOT NULL,
    severity TEXT NOT NULL,
    status TEXT NOT NULL,
    message TEXT NOT NULL,
    checked_at TEXT NOT NULL
);

CREATE VIEW v_qsb_artifact_search AS
SELECT
    a.artifact_id,
    a.title,
    a.artifact_type,
    a.semantic_role,
    a.mime_type,
    a.canonical_path,
    a.content_hash,
    a.status,
    a.visibility,
    al.alias,
    ti.text_role,
    ti.excerpt,
    li.source_type,
    li.source_ref,
    li.evidence_role,
    cb.admissible_use,
    cb.forbidden_use,
    cb.overclaim_risk,
    cb.review_status
FROM qsb_artifact AS a
LEFT JOIN qsb_artifact_alias AS al
    ON al.artifact_id = a.artifact_id
LEFT JOIN qsb_artifact_text_index AS ti
    ON ti.artifact_id = a.artifact_id
LEFT JOIN qsb_artifact_lineage AS li
    ON li.artifact_id = a.artifact_id
LEFT JOIN qsb_artifact_claim_boundary AS cb
    ON cb.artifact_id = a.artifact_id;

CREATE VIEW v_qsb_artifact_downloads AS
SELECT
    a.artifact_id,
    a.title,
    a.artifact_type,
    a.semantic_role,
    e.download_label,
    e.output_path,
    e.content_hash,
    a.visibility,
    r.review_status,
    cb.forbidden_use
FROM qsb_artifact AS a
JOIN qsb_artifact_export AS e
    ON e.artifact_id = a.artifact_id
LEFT JOIN qsb_artifact_review AS r
    ON r.artifact_id = a.artifact_id
LEFT JOIN qsb_artifact_claim_boundary AS cb
    ON cb.artifact_id = a.artifact_id;

CREATE VIEW v_qsb_artifact_lineage AS
SELECT
    a.artifact_id,
    a.title,
    a.artifact_type,
    li.source_type,
    li.source_ref,
    li.source_artifact_id,
    li.run_id,
    li.transformation_summary,
    a.content_hash,
    li.status
FROM qsb_artifact AS a
JOIN qsb_artifact_lineage AS li
    ON li.artifact_id = a.artifact_id;

CREATE VIEW v_qsb_artifact_claim_risk AS
SELECT
    a.artifact_id,
    a.title,
    a.artifact_type,
    a.semantic_role,
    a.visibility,
    cb.overclaim_risk,
    cb.admissible_use,
    cb.forbidden_use,
    cb.review_status
FROM qsb_artifact AS a
JOIN qsb_artifact_claim_boundary AS cb
    ON cb.artifact_id = a.artifact_id;
