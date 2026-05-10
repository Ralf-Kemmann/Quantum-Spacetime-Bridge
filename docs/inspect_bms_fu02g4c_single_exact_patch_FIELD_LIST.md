# Field list — `inspect_bms_fu02g4c_single_exact_patch.py` outputs

## JSON photo: `bms_fu02g4c_exact_patch_26187175.json`

- `artifact_type` — string — Human-readable artifact class.
- `runner_path` — string — Original FU02g4c runner used by the wrapper.
- `base_config_path` — string — Base YAML config copied and overridden for the single-patch replay.
- `generated_config_path` — string — Generated one-patch replay config written by the photo script.
- `skip_first_raw_patches` — integer — Raw connected-patch skip index used for the replay.
- `max_raw_patches_this_run` — integer — Number of raw connected patches inspected; expected to be `1` for the photo run.
- `candidate_window_start` — integer — Inclusive raw replay window start.
- `candidate_window_end_exclusive` — integer — Exclusive raw replay window end.
- `reference_event` — object — Captured FU02f1 reference signature event from the original runner’s `patch_signature()` call.
- `candidate_event` — object — Captured inspected candidate signature event from the original runner’s `patch_signature()` call.
- `candidate_nodes` — array[object] — Candidate patch node/face table with roles and cell types.
- `candidate_internal_edges` — array[object] — Candidate patch internal adjacency edges.
- `automorphy_checks` — object — Optional full-graph automorphy checks using `networkx`.
- `claim_boundary` — string — Defensive interpretation boundary for the inspection artifact.

## Signature event object

- `ordinal` — integer — Order in which `patch_signature()` was called during the wrapped run.
- `patch_size` — integer — Number of nodes/faces in the captured patch.
- `carriers` — array[string] — Sorted carrier node/face IDs in the patch.
- `mixed` — array[string] — Sorted nodes assigned to the mixed-core role.
- `pent` — array[string] — Sorted nodes assigned to the pentagon-boundary role.
- `signature` — object — Raw signature dictionary returned by the existing runner.
- `carrier_signature_string` — string/null — Carrier signature string returned by the existing runner.
- `role_signature_string` — string/null — Role-colored signature string returned by the existing runner.

## Nodes CSV: `bms_fu02g4c_exact_patch_26187175_nodes.csv`

- `node_id` — string — Candidate patch node/face ID.
- `in_patch` — boolean — Always true for this file.
- `role` — string — Candidate role label: `mixed_core`, `pentagon_boundary`, or `unassigned_or_other`.
- `cell_type` — string — Cell/face type as read by the original runner’s type map.

## Edges CSV: `bms_fu02g4c_exact_patch_26187175_edges.csv`

- `source` — string — Source node/face ID for an internal candidate edge.
- `target` — string — Target node/face ID for an internal candidate edge.
- `source_role` — string — Role label for `source`.
- `target_role` — string — Role label for `target`.

## Automorphy checks

- `networkx_available` — boolean — Whether `networkx` was available in the active environment.
- `uncolored_patch_automorphic_to_reference` — boolean/null — Whether the candidate patch is automorphic to the FU02f1 reference as an uncolored patch.
- `role_colored_patch_automorphic_to_reference` — boolean/null — Whether the candidate patch is automorphic to the FU02f1 reference while preserving role labels.
- `note` — string — Short explanation or reason for skipped checks.
