# BMS-FU02g4d — Coverage and Log Audit Specification

## Purpose

BMS-FU02g4d freezes the current FU02g4c brute-force continuation at the last valid gap-safe resume point and audits all available chunk/segment logs before any further scientific interpretation.

The goal is not to create a stronger physical claim. The goal is to determine which FU02g4c outputs are valid, which are diagnostic only, which are interrupted or empty, and what contiguous raw connected-patch coverage is actually supported by the logs.

## Motivation

FU02g4c was introduced to make the FU02g4b connected-patch enumeration resumable and optionally orbit-reduced under the 120 automorphisms of the C60 face graph.

The V3 gap-safe wrapper repaired the timeout-resume issue by advancing from

```text
NEXT_SKIP = raw_patch_count_seen_including_skipped - 1
```

instead of jumping blindly by the nominal chunk size. This prevents coverage gaps after `partial_timeout_reached` segments.

However, at high `skip_first_raw_patches` values, the current wrapper becomes dominated by repeated fast-forwarding through already skipped connected patches. Around `START_SKIP ≈ 59M`, a 3600-second segment processed only a small number of new raw patches. Further brute-force continuation with the current skip-based mechanism is therefore algorithmically inefficient.

FU02g4d records this as a methodological stop point and audits the data already produced.

## Scope

### Included

- Parse FU02g4c log files from the project run folders.
- Extract all JSON objects from each log.
- Merge manifest-style and summary-style JSON objects for each log.
- Classify each log as valid, invalid, raw-only, zero-progress, empty/aborted, or secondary/diagnostic.
- Detect primary contiguous coverage under the gap-safe rule.
- Detect gaps and overlaps in processed intervals.
- Aggregate counts only from selected valid primary logs.
- Preserve orbit-class counts per segment without naïvely summing them as global unique classes.
- Generate machine-readable CSV/JSON outputs and a human-readable Markdown audit note.

### Excluded

- No new connected-patch enumeration.
- No physical interpretation beyond bounded methodological status.
- No claim of exhaustive completion unless a valid log explicitly reports `enumeration_status = complete` and coverage audit supports it.
- No claim that role-colored signatures are impossible.
- No aggregation of orbit classes as global unique classes unless a dedicated global canonical-hash pass exists.

## Input Directories

Default input log directories:

```text
runs/BMS-FU02g4c/chunk_batch_logs/
runs/BMS-FU02g4c/chunk_batch_logs_gap_safe/
```

The audit script may accept additional log directories by command-line argument.

## Output Directory

Default output directory:

```text
runs/BMS-FU02g4d/coverage_and_log_audit/
```

Expected outputs:

```text
chunk_log_audit.csv
chunk_log_audit.json
coverage_intervals_primary.csv
coverage_gaps_primary.csv
aggregate_counts_primary.json
BMS_FU02G4D_COVERAGE_AND_LOG_AUDIT_RESULT_NOTE.md
```

## Validity Rules

A log is considered methodologically valid for orbit-reduced FU02g4c analysis only if all of the following hold:

```text
warnings_count == 0
orbit_reduction_enabled_actual == true
automorphism_count_used == 120
reference_is_connected == true
raw_connected_patch_count_processed > 0
```

A log with valid environment fields but `raw_connected_patch_count_processed == 0` is classified as `zero_progress_timeout` if it reports a timeout status. Such logs are not included in scientific counts.

A zero-byte log is classified as `empty_or_aborted`.

A log where orbit reduction is disabled or unavailable is classified as `raw_only_invalid_orbit` for the orbit-reduced FU02g4c line. It may be retained as diagnostic raw-only evidence but is excluded from primary orbit-reduced aggregation.

Logs with warnings are excluded from primary aggregation and classified according to the warning context.

## Coverage Interval Definition

For a valid processed log:

```text
interval_start = skip_first_raw_patches
interval_end_exclusive = raw_patch_count_seen_including_skipped - 1
processed_count_expected = interval_end_exclusive - interval_start
```

For the FU02g4c runner, `raw_patch_count_seen_including_skipped` includes the next candidate marker, so the next safe resume value is:

```text
NEXT_SKIP = raw_patch_count_seen_including_skipped - 1
```

The processed interval is therefore treated as half-open:

```text
[skip_first_raw_patches, NEXT_SKIP)
```

The expected interval length should match `raw_connected_patch_count_processed`. If it does not match, the log is flagged for manual inspection.

## Primary vs Secondary Logs

### Primary Logs

Primary logs are valid logs that can be ordered into a contiguous gap-safe coverage chain.

### Secondary / Diagnostic Logs

Secondary logs include:

- V2 timeout-jump logs after a detected gap.
- Raw-only logs from runs where `networkx` was unavailable.
- Empty/aborted logs.
- Zero-progress timeout logs.
- Logs that overlap already accepted primary coverage in a non-trivial way.

Secondary logs are preserved in the audit table but excluded from primary cumulative counts unless explicitly selected later.

## Aggregated Count Fields

The primary aggregate should sum raw segment counts such as:

```text
raw_connected_patch_count_processed
raw_carrier_signature_exact_match_count
raw_carrier_signature_near_match_count
raw_role_colored_signature_exact_match_count
raw_role_colored_signature_near_match_count
```

The primary aggregate should not claim globally unique orbit-class counts by naïvely summing per-segment class counts. Per-segment orbit fields may be summarized as segment-level totals, maxima, and presence/absence indicators only.

## Required Field List

| Field name | Type | Description |
|---|---:|---|
| `source_log_path` | string | Path to the parsed log file relative to project root when possible. |
| `log_size_bytes` | integer | File size in bytes. Zero indicates an empty or aborted log. |
| `chunk_id` | string/null | Segment or chunk identifier extracted from merged JSON or filename. |
| `classification` | string | Audit classification such as `primary_valid`, `empty_or_aborted`, `zero_progress_timeout`, `raw_only_invalid_orbit`, `invalid_warning`, `secondary_overlap`, or `secondary_gap_after_v2_jump`. |
| `classification_reason` | string | Human-readable reason for the classification. |
| `enumeration_status` | string/null | Runner status such as `partial_chunk_limit_reached`, `partial_timeout_reached`, or `complete`. |
| `warnings_count` | integer/null | Warning count reported by manifest or merged JSON. |
| `orbit_reduction_enabled_actual` | boolean/null | Whether orbit reduction was actually enabled. |
| `automorphism_count_used` | integer/null | Number of automorphisms used. Expected value for valid C60 orbit-reduced run is 120. |
| `reference_is_connected` | boolean/null | Whether the reference carrier patch was connected. Expected true. |
| `skip_first_raw_patches` | integer/null | Resume skip value used at start of log. |
| `raw_patch_count_seen_including_skipped` | integer/null | Runner reported raw count marker including skipped candidates. |
| `next_skip` | integer/null | Gap-safe next resume value, computed as `raw_patch_count_seen_including_skipped - 1`. |
| `interval_start` | integer/null | Half-open processed interval start. Normally equal to `skip_first_raw_patches`. |
| `interval_end_exclusive` | integer/null | Half-open processed interval end. Normally equal to `next_skip`. |
| `raw_connected_patch_count_processed` | integer/null | Number of raw connected patches processed in this log. |
| `interval_count_check` | integer/null | Difference `interval_end_exclusive - interval_start`. Should match processed count. |
| `interval_count_matches` | boolean/null | Whether interval length matches processed count. |
| `unique_orbit_patch_count_processed` | integer/null | Number of unique orbit patches processed within this log. Segment-local only. |
| `raw_carrier_signature_exact_match_count` | integer | Raw uncolored carrier exact matches in this log. |
| `raw_carrier_signature_near_match_count` | integer | Raw uncolored carrier near matches in this log. |
| `raw_role_colored_signature_exact_match_count` | integer | Raw role-colored exact matches in this log. |
| `raw_role_colored_signature_near_match_count` | integer | Raw role-colored near matches in this log. |
| `orbit_carrier_signature_exact_match_class_count` | integer | Segment-local orbit-class count for uncolored carrier exact signatures. |
| `orbit_carrier_signature_near_match_class_count` | integer | Segment-local orbit-class count for uncolored carrier near signatures. |
| `orbit_role_colored_signature_exact_match_class_count` | integer | Segment-local orbit-class count for role-colored exact signatures. |
| `orbit_role_colored_signature_near_match_class_count` | integer | Segment-local orbit-class count for role-colored near signatures. |
| `include_in_primary_counts` | boolean | Whether this log contributes to primary raw aggregate counts. |

## Defensive Claim Boundary

Allowed after FU02g4d:

```text
The FU02g4c logs were audited for validity, coverage, gaps, overlaps, and run interruptions. Primary cumulative raw counts are reported only over logs satisfying the explicit validity and coverage criteria. Orbit-class fields remain segment-local unless a later global canonical aggregation is performed.
```

Not allowed after FU02g4d alone:

```text
The enumeration is exhaustive.
The role-colored signature cannot occur.
The absence of exact role-colored matches proves physical specificity.
Per-segment orbit-class counts are global unique orbit-class counts.
```

## Next Step After Audit

Recommended next blocks:

```text
BMS-FU02g5 — Role-Assignment Sensitivity Controls
BMS-FU03a  — External C60 Fullerene-Isomer Controls
```

The current brute-force continuation should remain paused unless a checkpoint-capable or frontier-state enumeration strategy is implemented.
