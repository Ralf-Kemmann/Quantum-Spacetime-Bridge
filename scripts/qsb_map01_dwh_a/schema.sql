PRAGMA foreign_keys = ON;

CREATE TABLE qsb_map (
    map_id TEXT PRIMARY KEY,
    title TEXT NOT NULL,
    map_level INTEGER NOT NULL,
    scope TEXT NOT NULL,
    status TEXT NOT NULL,
    version TEXT NOT NULL,
    created_at TEXT NOT NULL,
    updated_at TEXT,
    owner_role TEXT,
    claim_boundary_summary TEXT NOT NULL,
    notes TEXT
);

CREATE TABLE qsb_map_node (
    node_id TEXT PRIMARY KEY,
    map_id TEXT NOT NULL,
    parent_node_id TEXT,
    label TEXT NOT NULL,
    canonical_key TEXT NOT NULL,
    node_type TEXT NOT NULL,
    qsb_layer TEXT,
    short_description TEXT,
    sort_order INTEGER,
    status TEXT NOT NULL,
    review_status TEXT,
    FOREIGN KEY (map_id) REFERENCES qsb_map(map_id),
    FOREIGN KEY (parent_node_id) REFERENCES qsb_map_node(node_id)
);

CREATE TABLE qsb_map_edge (
    edge_id TEXT PRIMARY KEY,
    map_id TEXT NOT NULL,
    source_node_id TEXT NOT NULL,
    target_node_id TEXT NOT NULL,
    relation_type TEXT NOT NULL,
    relation_label TEXT,
    directionality TEXT NOT NULL,
    confidence_level TEXT,
    status TEXT NOT NULL,
    FOREIGN KEY (map_id) REFERENCES qsb_map(map_id),
    FOREIGN KEY (source_node_id) REFERENCES qsb_map_node(node_id),
    FOREIGN KEY (target_node_id) REFERENCES qsb_map_node(node_id)
);

CREATE TABLE qsb_map_alias (
    alias_id TEXT PRIMARY KEY,
    node_id TEXT NOT NULL,
    alias TEXT NOT NULL,
    language TEXT NOT NULL,
    alias_type TEXT NOT NULL,
    status TEXT NOT NULL,
    FOREIGN KEY (node_id) REFERENCES qsb_map_node(node_id)
);

CREATE TABLE qsb_map_source_link (
    link_id TEXT PRIMARY KEY,
    node_id TEXT NOT NULL,
    source_type TEXT NOT NULL,
    source_ref TEXT NOT NULL,
    source_title TEXT,
    evidence_role TEXT NOT NULL,
    claim_use TEXT NOT NULL,
    source_status TEXT NOT NULL,
    notes TEXT,
    FOREIGN KEY (node_id) REFERENCES qsb_map_node(node_id)
);

CREATE TABLE qsb_map_claim_boundary (
    boundary_id TEXT PRIMARY KEY,
    node_id TEXT NOT NULL,
    admissible_use TEXT NOT NULL,
    forbidden_use TEXT NOT NULL,
    overclaim_risk TEXT NOT NULL,
    review_status TEXT NOT NULL,
    notes TEXT,
    FOREIGN KEY (node_id) REFERENCES qsb_map_node(node_id)
);

CREATE TABLE qsb_map_export (
    export_id TEXT PRIMARY KEY,
    map_id TEXT NOT NULL,
    export_type TEXT NOT NULL,
    output_path TEXT NOT NULL,
    generated_at TEXT NOT NULL,
    generator_name TEXT,
    generator_version TEXT,
    content_hash TEXT,
    status TEXT NOT NULL,
    FOREIGN KEY (map_id) REFERENCES qsb_map(map_id)
);

CREATE TABLE qsb_map_validation_result (
    validation_id TEXT PRIMARY KEY,
    map_id TEXT NOT NULL,
    rule_id TEXT NOT NULL,
    severity TEXT NOT NULL,
    status TEXT NOT NULL,
    message TEXT NOT NULL,
    checked_at TEXT NOT NULL,
    FOREIGN KEY (map_id) REFERENCES qsb_map(map_id)
);

CREATE VIEW v_qsb_map_search AS
SELECT
    n.map_id,
    n.node_id,
    n.label,
    n.canonical_key,
    n.node_type,
    n.qsb_layer,
    a.alias,
    n.short_description,
    b.admissible_use,
    b.forbidden_use,
    b.overclaim_risk,
    s.source_title,
    s.evidence_role,
    s.claim_use
FROM qsb_map_node AS n
LEFT JOIN qsb_map_alias AS a
    ON a.node_id = n.node_id
LEFT JOIN qsb_map_claim_boundary AS b
    ON b.node_id = n.node_id
LEFT JOIN qsb_map_source_link AS s
    ON s.node_id = n.node_id;

CREATE VIEW v_qsb_map_claim_risk AS
SELECT
    n.map_id,
    n.node_id,
    n.label,
    n.canonical_key,
    b.overclaim_risk,
    b.admissible_use,
    b.forbidden_use,
    b.review_status
FROM qsb_map_node AS n
JOIN qsb_map_claim_boundary AS b
    ON b.node_id = n.node_id;

CREATE VIEW v_qsb_map_source_context AS
SELECT
    n.node_id,
    n.label,
    n.canonical_key,
    s.source_type,
    s.source_ref,
    s.source_title,
    s.evidence_role,
    s.claim_use,
    s.source_status
FROM qsb_map_node AS n
JOIN qsb_map_source_link AS s
    ON s.node_id = n.node_id;
