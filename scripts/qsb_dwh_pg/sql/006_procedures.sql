CREATE OR REPLACE FUNCTION admin.fn_now_utc()
RETURNS timestamptz
LANGUAGE sql
STABLE
AS $$
  SELECT now() AT TIME ZONE 'UTC';
$$;

CREATE OR REPLACE PROCEDURE admin.register_etl_run(
  p_run_id text,
  p_dataset_id text,
  p_status text,
  p_claim_boundary text
)
LANGUAGE plpgsql
AS $$
BEGIN
  INSERT INTO admin.etl_run(run_id, dataset_id, status, claim_boundary, started_at)
  VALUES (p_run_id, p_dataset_id, p_status, p_claim_boundary, admin.fn_now_utc())
  ON CONFLICT (run_id) DO UPDATE
    SET dataset_id = EXCLUDED.dataset_id,
        status = EXCLUDED.status,
        claim_boundary = EXCLUDED.claim_boundary;
END;
$$;

CREATE OR REPLACE PROCEDURE admin.register_validation_result(
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
  VALUES (p_validation_id, p_dataset_id, 'procedure_registration', p_validation_id,
          p_status, p_message, '', p_message)
  ON CONFLICT (validation_id) DO UPDATE
    SET dataset_id = EXCLUDED.dataset_id,
        validation_status = EXCLUDED.validation_status,
        observed_value = EXCLUDED.observed_value,
        notes = EXCLUDED.notes;
END;
$$;

CREATE OR REPLACE PROCEDURE admin.mark_etl_step(
  p_run_id text,
  p_step_name text,
  p_status text,
  p_message text
)
LANGUAGE plpgsql
AS $$
BEGIN
  INSERT INTO admin.etl_step(run_id, step_name, status, message, recorded_at)
  VALUES (p_run_id, p_step_name, p_status, p_message, admin.fn_now_utc())
  ON CONFLICT (run_id, step_name) DO UPDATE
    SET status = EXCLUDED.status,
        message = EXCLUDED.message,
        recorded_at = EXCLUDED.recorded_at;
END;
$$;
