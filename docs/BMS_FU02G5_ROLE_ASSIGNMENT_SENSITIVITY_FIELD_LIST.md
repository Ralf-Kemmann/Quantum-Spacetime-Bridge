# BMS-FU02g5 — Role-Assignment Sensitivity Field List

**Date:** 2026-05-06  
**Project:** Quantum–Spacetime Bridge / Gravitation und RaumZeit  
**Artifact:** Field list for FU02g5 config and outputs

---

## 1. Config Fields

### `run.run_id`
**Type:** string  
**Description:** Stable identifier for this FU02g5 run. Used in output metadata.

### `run.case_id`
**Type:** string  
**Description:** Human-readable case name for the control block.

### `run.output_dir`
**Type:** string / path  
**Description:** Output directory for `summary.json`, CSV tables, resolved config, and result note.

### `run.patch_size`
**Type:** integer  
**Description:** Number of nodes in each connected patch. For FU02f1/FU02g4c continuity this should be `17`.

### `run.skip_first_connected_patches`
**Type:** integer  
**Description:** Number of connected patches to skip before counting/enumerating. Supports windowed replay-style testing.

### `run.max_connected_patches_this_run`
**Type:** integer or null  
**Description:** Maximum number of connected patches to process in this run. `null` means no explicit cap, but this may be expensive.

### `run.max_wall_seconds`
**Type:** number or null  
**Description:** Optional wall-clock soft stop in seconds. If reached, the script writes partial output and marks the run as partial.

### `run.progress_every`
**Type:** integer  
**Description:** Print progress after this many enumerated patches.

### `run.near_distance_threshold`
**Type:** integer  
**Description:** Maximum coarse role-histogram distance counted as a near match.

### `input.full_face_graph_edges_csv`
**Type:** string / path  
**Description:** CSV edge list for the C60 face graph. Expected columns are `source,target`; if absent, the first two columns are used.

### `input.reference_carrier_nodes`
**Type:** list[string]  
**Description:** Node labels of the FU02f1 reference carrier.

### `input.reference_mixed_core_nodes`
**Type:** list[string]  
**Description:** Reference nodes assigned to the mixed-core role under the baseline convention.

### `input.reference_pentagon_boundary_nodes`
**Type:** list[string]  
**Description:** Reference nodes assigned to the pentagon-boundary role under the baseline convention.

### `input.localized_exact_patch_nodes`
**Type:** list[string]  
**Description:** Node labels of the localized FU02g4c exact patch at `skip_first_raw_patches = 26,187,175`.

### `input.localized_exact_patch_mixed_core_nodes`
**Type:** list[string]  
**Description:** Localized exact patch nodes assigned to mixed-core role under the transported baseline convention.

### `input.localized_exact_patch_pentagon_boundary_nodes`
**Type:** list[string]  
**Description:** Localized exact patch nodes assigned to pentagon-boundary role under the transported baseline convention.

### `role_variants[].variant_id`
**Type:** string  
**Description:** Short stable ID for the role-assignment variant.

### `role_variants[].description`
**Type:** string  
**Description:** Human-readable explanation of the variant.

### `role_variants[].mode`
**Type:** string  
**Description:** Role assignment mode. Supported initial values: `v0_type_preferred`, `uncolored_carrier_only`, `face_type_only`, `swap_core_boundary`, `core_erased`, `boundary_erased`, `random_role_permutation_seeded`.

### `role_variants[].enabled`
**Type:** boolean  
**Description:** Whether the variant should be included in the run.

### `role_variants[].random_seed`
**Type:** integer or null  
**Description:** Seed for seeded random role permutation variants.

### `report.write_result_note`
**Type:** boolean  
**Description:** Whether to write a human-readable Markdown result note.

### `report.write_candidate_pair_summary`
**Type:** boolean  
**Description:** Whether to write focused reference-vs-localized-candidate comparison CSV.

---

## 2. Output Fields — `variant_summary.csv`

### `run_id`
**Type:** string  
**Description:** Run identifier copied from config.

### `case_id`
**Type:** string  
**Description:** Case identifier copied from config.

### `variant_id`
**Type:** string  
**Description:** Role-assignment variant ID.

### `variant_mode`
**Type:** string  
**Description:** Role assignment mode used by the variant.

### `variant_description`
**Type:** string  
**Description:** Human-readable description of the variant.

### `reference_role_colored_signature`
**Type:** string  
**Description:** Role-colored graph signature/hash for the reference carrier under this variant.

### `localized_candidate_role_colored_signature`
**Type:** string  
**Description:** Role-colored graph signature/hash for the localized automorphic candidate under this variant.

### `localized_candidate_exact_match`
**Type:** boolean  
**Description:** Whether localized candidate signature exactly equals the reference signature under this variant.

### `localized_candidate_near_distance`
**Type:** integer  
**Description:** Coarse distance between reference and localized candidate role-degree histograms.

### `localized_candidate_near_match`
**Type:** boolean  
**Description:** Whether the localized candidate distance is less than or equal to the configured near threshold.

### `enumerated_patch_count`
**Type:** integer  
**Description:** Number of connected patches actually evaluated in the enumeration window.

### `enumerated_exact_match_count`
**Type:** integer  
**Description:** Number of enumerated patches with exact role-colored signature match to reference.

### `enumerated_near_match_count`
**Type:** integer  
**Description:** Number of enumerated patches with near-distance less than or equal to threshold.

### `partial_run`
**Type:** boolean  
**Description:** Whether enumeration stopped before exhausting the configured window due to wall-clock or max-count limits.

### `warnings_count`
**Type:** integer  
**Description:** Number of warnings emitted for this variant.

---

## 3. Output Fields — `candidate_pair_summary.csv`

### `run_id`
**Type:** string  
**Description:** Run identifier.

### `variant_id`
**Type:** string  
**Description:** Role-assignment variant.

### `reference_node_count`
**Type:** integer  
**Description:** Number of nodes in the reference carrier.

### `localized_candidate_node_count`
**Type:** integer  
**Description:** Number of nodes in the localized exact patch.

### `reference_edge_count`
**Type:** integer  
**Description:** Number of induced graph edges inside the reference carrier.

### `localized_candidate_edge_count`
**Type:** integer  
**Description:** Number of induced graph edges inside the localized candidate patch.

### `reference_connected`
**Type:** boolean  
**Description:** Whether the reference carrier is connected in the supplied C60 face graph.

### `localized_candidate_connected`
**Type:** boolean  
**Description:** Whether the localized candidate patch is connected in the supplied C60 face graph.

### `exact_match`
**Type:** boolean  
**Description:** Whether reference and localized candidate have identical role-colored signatures under the variant.

### `near_distance`
**Type:** integer  
**Description:** Coarse role-histogram distance for the candidate pair.

### `near_match`
**Type:** boolean  
**Description:** Whether `near_distance <= near_distance_threshold`.

---

## 4. Output Fields — `summary.json`

### `metadata`
**Type:** object  
**Description:** Run timestamp, script name, run ID, case ID, and claim boundary.

### `config_resolved`
**Type:** object  
**Description:** Config after defaults and path expansion.

### `graph_stats`
**Type:** object  
**Description:** Node count, edge count, component count, and basic C60 face graph validation notes.

### `reference_stats`
**Type:** object  
**Description:** Node count, edge count, connectedness, and face-type counts for reference carrier.

### `localized_candidate_stats`
**Type:** object  
**Description:** Node count, edge count, connectedness, and face-type counts for localized exact patch.

### `variant_results`
**Type:** list[object]  
**Description:** Per-variant result records matching `variant_summary.csv`.

### `warnings`
**Type:** list[string]  
**Description:** Global warnings generated during the run.

### `partial_run`
**Type:** boolean  
**Description:** Global partial-run flag.

---

## 5. Output Fields — `result_note.md`

### `Befund`
**Type:** Markdown section  
**Description:** Only direct observations/counts from the run.

### `Interpretation`
**Type:** Markdown section  
**Description:** Conservative explanation of what the observed sensitivity pattern suggests.

### `Hypothese`
**Type:** Markdown section  
**Description:** Optional working hypothesis, explicitly marked as not yet established.

### `Offene Lücke`
**Type:** Markdown section  
**Description:** Remaining controls, missing external graph families, near-decoy inspection, and dynamical non-claim.

### `Claim Boundary`
**Type:** Markdown section  
**Description:** Explicit statement that FU02g5 is a combinatorial role-assignment sensitivity test only.

### `Next Step`
**Type:** Markdown section  
**Description:** Recommended next technical action based on the run outcome.
