CREATE OR REPLACE PROCEDURE validation.register_validation_result(
  p_validation_id text,
  p_dataset_id text,
  p_status text,
  p_message text
)
LANGUAGE plpgsql
AS $$
BEGIN
  INSERT INTO validation.validation_result(
    validation_id, dataset_id, validation_scope, validation_rule,
    validation_status, observed_value, expected_value, notes
  )
  VALUES (p_validation_id, p_dataset_id, 'legacy_migration', p_validation_id,
          p_status, p_message, '', p_message)
  ON CONFLICT (validation_id) DO UPDATE
    SET dataset_id = EXCLUDED.dataset_id,
        validation_status = EXCLUDED.validation_status,
        observed_value = EXCLUDED.observed_value,
        notes = EXCLUDED.notes;
END;
$$;

CREATE OR REPLACE PROCEDURE metadata.register_alias(
  p_canonical_name text,
  p_display_label_de text,
  p_context text
)
LANGUAGE plpgsql
AS $$
DECLARE
  v_alias_id text;
BEGIN
  v_alias_id := md5(p_canonical_name || ':' || p_context);
  INSERT INTO metadata.meta_alias(alias_id, canonical_name, display_label_de, language, alias_status)
  VALUES (v_alias_id, p_canonical_name, p_display_label_de, 'de', 'registered')
  ON CONFLICT (alias_id) DO UPDATE
    SET canonical_name = EXCLUDED.canonical_name,
        display_label_de = EXCLUDED.display_label_de,
        language = EXCLUDED.language,
        alias_status = EXCLUDED.alias_status;
END;
$$;
