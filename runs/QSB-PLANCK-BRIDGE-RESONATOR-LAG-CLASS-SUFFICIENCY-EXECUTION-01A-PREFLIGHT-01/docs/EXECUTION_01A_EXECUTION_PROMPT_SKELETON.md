# Execution 01A Execution Prompt Skeleton

This skeleton must not be used until a later preflight passes.

Required prior status:

```text
preflight_status=go_for_execution_01a
```

Minimum required inputs:

- passed preflight run,
- resolved contract value review,
- explicit authorization review,
- contract_field_export.csv,
- lag_class_handoff.csv with resolved values,
- control_policy_export.csv with resolved seed/trial/control values,
- validation_summary.csv,
- dry_run_manifest.json,
- claim_boundaries.csv.

Forbidden unless explicitly authorized:

- physics claims,
- mechanism claims,
- DWH writes,
- literature imports,
- candidate search or repair.
