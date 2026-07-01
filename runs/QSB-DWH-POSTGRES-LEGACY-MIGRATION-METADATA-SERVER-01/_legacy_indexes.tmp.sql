CREATE INDEX IF NOT EXISTS idx_raw_source_artifact_domain ON raw.source_artifact(domain_guess);
CREATE INDEX IF NOT EXISTS idx_raw_source_artifact_kind ON raw.source_artifact(artifact_kind);
CREATE INDEX IF NOT EXISTS idx_csv_row_json_artifact ON staging.csv_row_json(artifact_id);
CREATE INDEX IF NOT EXISTS idx_json_document_artifact ON staging.json_document(artifact_id);
CREATE INDEX IF NOT EXISTS idx_markdown_document_artifact ON staging.markdown_document(artifact_id);
CREATE INDEX IF NOT EXISTS idx_qsb_artifact_domain ON canonical.qsb_artifact(domain_guess);
CREATE INDEX IF NOT EXISTS idx_meta_search_domain ON metadata.meta_search_token(domain_guess);
CREATE INDEX IF NOT EXISTS idx_meta_search_text ON metadata.meta_search_token USING gin(to_tsvector('simple', search_text));
