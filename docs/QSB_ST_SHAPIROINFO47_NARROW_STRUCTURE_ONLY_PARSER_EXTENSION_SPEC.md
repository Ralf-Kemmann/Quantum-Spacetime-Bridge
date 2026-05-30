# QSB-ST SHAPIROINFO47 — Narrow Structure-Only Parser Extension Spec

Date: 2026-05-31  
Status: narrow structure-only parser extension specification  
Upstream decision: SHAPIROINFO46_PARSE_FAILURE_CLASS_REVIEW_AND_EXTENSION_PLAN  
Implementation status: not implemented by this note  
Execution status: not executed by this note  
Raw artifact access: no direct raw artifact inspection  
Physics-analysis status: closed for interpretation and residual claims  
Tracking decision: this documentation note may be tracked; raw artifacts remain local-only and untracked

## 1. Purpose

This note specifies a narrow structure-only parser extension for the QSB-ST ShapiroInfo raw-structure inventory script.

The purpose is to improve technical structure inventory coverage for already classified parse-failure cases, without moving into physical analysis.

This is part of a physics-motivated research route, but this note is a parser specification only.

It does not inspect raw artifacts directly.

It does not run an inventory.

It does not search for physical Shapiro-information residuals.

It does not make QSB-ST Bridge-related claims.

## 2. Upstream basis

The extension is based on the SHAPIROINFO46 parse-failure review.

Known inventory facts:

- total_records = 7
- parsed_file_count = 2
- metadata_only_count = 5
- unsupported_count = 0
- parse_failure_count = 5

Known extension counts:

- .md = 2
- .par = 1
- .sha256 = 2
- .tim = 1
- .yaml = 1

Known failure classes:

- unsupported_extension_metadata_only = 4
- yaml_deep_parsing_not_enabled = 1

These facts indicate that the first minimal parser was conservative and that a small structure-only parser extension is justified.

## 3. Design principle

The parser extension must remain boring, shallow, and structural.

It must answer questions such as:

- Is the file text-like?
- How many lines are present?
- Are there key-value-like lines?
- Are there comment lines?
- Are there blank lines?
- Does the file resemble a checksum file?
- Does the file resemble a simple parameter file?
- Does the file resemble a timing/table-like text file?
- Does the YAML file expose shallow top-level keys?

It must not answer questions such as:

- Does this support a physical Shapiro-information residual?
- Does this confirm a QSB-ST Bridge?
- Does this show spacetime structure?
- Does this fit a model?
- Does this encode a physical signal?

## 4. Extension scope by file class

### 4.1 .sha256 files

Allowed parser behavior:

- read as UTF-8 text with safe error handling
- count lines
- detect whether non-empty lines resemble checksum records
- count checksum-like lines
- count malformed non-empty lines
- report checksum algorithm label as sha256_by_extension only
- do not verify raw payload files unless explicitly authorized in a later step
- do not interpret checksum values beyond structure

Allowed output fields may include:

- text_line_count
- nonempty_line_count
- checksum_like_line_count
- malformed_line_count
- checksum_algorithm_by_extension

### 4.2 .yaml and .yml files

Allowed parser behavior:

- prefer shallow safe parsing only
- if PyYAML is available, use yaml.safe_load
- if PyYAML is not available, fall back to shallow text-key scanning
- report top-level type
- report top-level keys if object-like
- report line count
- do not resolve external references
- do not execute tags
- do not perform deep semantic interpretation

Allowed output fields may include:

- yaml_parse_mode
- yaml_top_level_type
- yaml_top_level_keys
- text_line_count
- shallow_key_count

### 4.3 .par files

Allowed parser behavior:

- treat as text-like parameter structure
- read as UTF-8 text with safe error handling
- count lines
- count blank lines
- count comment-like lines
- detect simple key-value-like lines using conservative separators such as equals, colon, or whitespace-delimited first token
- do not infer physical parameter meaning
- do not classify parameters as physical variables
- do not use parameter values for computation

Allowed output fields may include:

- text_line_count
- blank_line_count
- comment_line_count
- key_value_like_line_count
- apparent_parameter_file = true

### 4.4 .tim files

Allowed parser behavior:

- treat as text-like timing/table structure
- read as UTF-8 text with safe error handling
- count lines
- count blank lines
- count comment-like lines
- count data-like lines
- estimate delimiter hints such as whitespace, comma, or tab
- estimate apparent column counts per data-like line
- do not interpret timestamps physically
- do not compute residuals
- do not fit timing models

Allowed output fields may include:

- text_line_count
- blank_line_count
- comment_line_count
- data_like_line_count
- delimiter_hint
- apparent_column_count_min
- apparent_column_count_max

### 4.5 .md files

Existing text-like handling may remain sufficient.

Allowed parser behavior:

- preserve or keep simple text line count
- do not add semantic Markdown interpretation
- do not extract claims from Markdown content
- do not interpret document content physically

## 5. Required summary schema behavior

The harmonized summary schema from SHAPIROINFO42 must be preserved.

The script must continue to write:

- total_records
- file_count
- parsed_file_count
- metadata_only_count
- unsupported_count
- parse_failure_count
- parse_status_counts
- extension_counts
- stop_reasons
- output_files
- claim_boundary

If the parser extension succeeds, expected direction is:

- parsed_file_count may increase
- metadata_only_count may decrease
- parse_failure_count may decrease

However, no such outcome is required.

A boring or unchanged result remains valid.

## 6. Output discipline

The parser extension must keep the same output root:

runs/QSB-ST-SHAPIROINFO/SHAPIROINFO39_RAW_STRUCTURE_INVENTORY/

The script must continue to write:

- raw_structure_inventory_summary.json
- raw_structure_inventory_table.csv
- raw_structure_inventory_readout.md
- parse_failures.csv
- inventory_config_resolved.json

If new columns are added to raw_structure_inventory_table.csv, they must be explicit, technical, and structure-only.

The readout must keep claim-boundary text.

## 7. Forbidden behavior

The parser extension must not:

- modify raw artifacts
- copy raw artifacts into tracked paths
- stage raw artifacts
- commit raw artifacts
- perform physical interpretation
- compute residuals
- run model fitting
- infer Shapiro signal content
- infer QSB-ST Bridge confirmation
- interpret timing values physically
- interpret parameter values physically
- classify content as evidence
- introduce dependencies without fallback behavior

Forbidden git commands remain:

- git add data/QSB-ST-SHAPIROINFO/public_sources/
- git add data/
- git add .

## 8. Implementation recommendation for SHAPIROINFO48

Recommended next block:

SHAPIROINFO48_NARROW_STRUCTURE_ONLY_PARSER_EXTENSION_PATCH

SHAPIROINFO48 should patch the existing script:

scripts/qsb_st_shapiroinfo40_raw_structure_inventory.py

The patch should be additive and conservative.

Recommended helper functions:

- safe_read_text_lines
- parse_checksum_text
- parse_shallow_yaml
- parse_parameter_text
- parse_timing_text
- count_text_structure

The patch should preserve existing behavior for .csv, .tsv, .json, .txt, .md, and .log.

The patch should not run the inventory automatically.

## 9. Acceptance checks for SHAPIROINFO48

The implementation patch should pass at least:

- python -m py_compile on the script
- grep checks for new parser function names
- schema marker checks for preserved summary keys
- git diff --check
- git status review

The inventory rerun should occur only in a later explicit execution block after the patch is committed.

## 10. Claim boundary

This note is a technical parser-extension specification within a physics-motivated research route.

It does not provide evidence for a physical Shapiro-information residual.

It does not validate the QSB-ST Bridge.

It does not establish spacetime, quantum-gravity, or relativistic physics claims.

It does not interpret raw artifact content as physical evidence.

It only specifies a narrow structure-only parser extension for already classified inventory parse-failure classes.
