# BMS-FU02g5g - FU02g4c Raw-Order Replay Certification Field List

**Date:** 2026-05-08
**Project:** Quantum-Spacetime Bridge / Gravitation und RaumZeit
**Artifact:** Field list for FU02g5g config and outputs
**Claim level:** certification/recovery block only

## Purpose

BMS-FU02g5g attempts to recover whether the FU02g5e1/g5e2/g5f
scaffold-localized near candidates correspond to original FU02g4c raw-order
enumeration candidates.

The block inventories FU02g4c logs/configs, audits candidate raw indices against
logged FU02g4c windows, and reports certification status without silently
treating scaffold indices as FU02g4c raw indices.

No physical emergence, spacetime emergence, global uniqueness, or global rarity
claim is made.

## Certification Status Vocabulary

### `certified`
A target is directly supported by an explicit FU02g4c raw-window artifact and
matching candidate evidence.

### `partially_certified`
FU02g4c artifacts support a bounded correspondence, but exact raw-order replay
was not independently rerun by FU02g5g.

### `not_certified`
Available artifacts do not certify the claimed raw-order correspondence.

### `insufficient_input_bundle`
The original FU02g4c input bundle/logic cannot be safely reused for replay in
this block.

### `order_mismatch`
Observed artifacts contradict the requested raw-order correspondence.

## Config Fields

### `run.run_id`
Stable identifier for this FU02g5g run.

### `run.case_id`
Human-readable case identifier.

### `run.output_dir`
Output directory for FU02g5g artifacts.

### `run.allow_replay_rerun`
Boolean. If false, the runner does not rerun FU02g4c inspect windows.

### `run.rerun_policy`
Text explanation for the replay decision.

### `input.g5e1_candidates_csv`
FU02g5e1 near-match candidate table.

### `input.g5e2_classification_csv`
FU02g5e2 classification table.

### `input.g5f_revalidation_csv`
FU02g5f revalidation table.

### `input.fu02g4c_run_dir`
FU02g4c run directory to inventory.

### `input.fu02g4c_base_config_yaml`
Primary FU02g4c config path, if present.

### `input.fu02g4c_inspect_config_glob`
Glob for FU02g4c inspect-window configs.

### `input.face_graph_edges_csv`
FU02d1 repaired C60 face graph path used for input-bundle presence checks.

### `input.required_certification_targets`
Named raw-index targets that must be called out explicitly.

## Output Fields - `summary.json`

### `metadata`
Run id, case id, timestamp, script path, and config path.

### `inputs`
Resolved input paths and required certification targets.

### `input_bundle`
Presence and sufficiency assessment for FU02g4c configs, inspect configs, run
logs, and graph inputs.

### `log_inventory_counts`
Counts of inventoried logs, parsed windows, candidate-covering logs, and status
classes.

### `candidate_counts`
Aggregate candidate and certification-status counts.

### `required_targets`
Explicit status summaries for candidate_008/raw_index 26187175 and
candidate_005/raw_index 26157530.

### `overall_certification_status`
Overall FU02g5g status.

### `overall_certification_basis`
Text basis for the overall status.

### `outputs`
Generated artifact paths.

### `claim_boundary`
Explicit negative-claim boundary.

## Output Fields - `fu02g4c_log_inventory.csv`

### `log_file`
FU02g4c log path.

### `log_kind`
One of `inspect_window`, `segment`, `chunk`, or `other`.

### `chunk_id`
Chunk/window id parsed from JSON content or filename.

### `window_start`
Start index parsed from filename/config/log metadata, when available.

### `window_end`
End index parsed from filename/config/log metadata, when available.

### `skip_first_raw_patches`
FU02g4c `skip_first_raw_patches` value parsed from log JSON.

### `max_raw_patches_this_run`
Inferred or config-level max patch count when available.

### `raw_patch_count_seen_including_skipped`
Raw seen count parsed from log JSON.

### `raw_connected_patch_count_processed`
Raw connected patch count parsed from log JSON.

### `raw_role_colored_signature_exact_match_count`
Raw role-colored exact-match count.

### `raw_role_colored_signature_near_match_count`
Raw role-colored near-match count.

### `enumeration_status`
FU02g4c enumeration status.

### `stop_or_timeout_status`
Derived stop/timeout status.

### `covers_candidate_raw_indices`
Semicolon-separated candidate raw indices covered by this log.

### `parse_warnings`
Semicolon-separated parse warnings.

## Output Fields - `candidate_window_crosscheck.csv`

### `candidate_id`
Candidate id.

### `scaffold_raw_index`
Raw index reported by FU02g5e1/g5e2/g5f. This is not silently certified as
FU02g4c raw order.

### `candidate_nodes`
Semicolon-separated candidate nodes.

### `inside_fu02g4c_logged_window`
Whether at least one parsed FU02g4c log window covers this raw index.

### `matching_fu02g4c_log_file`
Best matching FU02g4c log file.

### `all_matching_fu02g4c_log_files`
All matching FU02g4c log files.

### `fu02g4c_window_exact_count`
Exact-match count from the best matching log.

### `fu02g4c_window_near_count`
Near-match count from the best matching log.

### `best_window_start`
Best matching window start.

### `best_window_end`
Best matching window end.

### `best_window_status`
Best matching enumeration/stop status.

### `crosscheck_basis`
Text basis for the window cross-check.

## Output Fields - `candidate_replay_certification.csv`

### `candidate_id`
Candidate id.

### `scaffold_raw_index`
Raw index reported by FU02g5e1/g5e2/g5f.

### `candidate_nodes`
Semicolon-separated candidate nodes.

### `exact_match`
FU02g5e1 exact-match flag.

### `near_distance`
FU02g5e1 near-distance value.

### `classification_primary`
FU02g5e2 classification, when available.

### `g5f_raw_order_certification_status`
FU02g5f raw-order certification status, when available.

### `inside_fu02g4c_logged_window`
Whether FU02g4c logs cover this raw index.

### `matching_fu02g4c_log_file`
Best matching log file.

### `fu02g4c_window_exact_count`
Best-window raw exact count.

### `fu02g4c_window_near_count`
Best-window raw near count.

### `required_target_label`
Configured required target label, if applicable.

### `replay_attempted`
Whether FU02g5g reran a FU02g4c inspect window.

### `replay_certification_status`
One of the status vocabulary values.

### `replay_certification_basis`
Text basis for the candidate-level status.

### `scaffold_index_warning`
Warning that scaffold indices remain uncertified unless direct replay artifacts
support them.

## Output Fields - `result_note.md`

Required sections:

- Befund
- Interpretation
- Hypothese
- Offene Luecke
- Claim Boundary

The note explicitly states whether raw-order certification was achieved,
whether the original FU02g4c input bundle was sufficient, whether scaffold
indices remain uncertified, whether candidate_008/raw_index 26187175 is
certified, whether candidate_005/raw_index 26157530 is certified, and that no
physical or global uniqueness claim follows.
