# QSB-ST SHAPIROINFO50 — Extended Parser Rerun Result Note

Date: 2026-05-31  
Status: extended parser rerun result documented  
Upstream execution: SHAPIROINFO49_CONTROLLED_STRUCTURE_INVENTORY_RERUN_EXTENDED_PARSER  
Execution scope: technical structure inventory only  
Physics-analysis status: closed for interpretation and residual claims  
Tracking decision: this documentation note may be tracked; raw artifacts remain local-only and untracked

## 1. Purpose

This note documents the SHAPIROINFO49 controlled structure-inventory rerun after the SHAPIROINFO48 narrow structure-only parser extension.

The rerun tested whether the extended parser could improve technical coverage of the previously metadata-only or parse-failure cases without moving into physical analysis.

This is part of a physics-motivated research route, but the present result is a technical structure-inventory result only.

It does not provide physical interpretation, residual search, signal search, model fitting, or QSB-ST Bridge-related claims.

## 2. Upstream chain

The relevant upstream chain is:

- SHAPIROINFO46: parse-failure class review and extension plan
- SHAPIROINFO47: narrow structure-only parser extension spec
- SHAPIROINFO48: narrow structure-only parser extension patch
- SHAPIROINFO49: controlled structure inventory rerun with extended parser

The parser extension added structure-only handling for:

- .sha256 checksum-like text structure
- .yaml/.yml shallow YAML structure or fallback key scan
- .par parameter-like text structure
- .tim timing/table-like text structure
- .md existing simple text handling

## 3. Command executed

The script help was inspected first.

Then the inventory script was executed exactly once using default paths:

python scripts/qsb_st_shapiroinfo40_raw_structure_inventory.py

The script used the input root:

data/QSB-ST-SHAPIROINFO/public_sources/

The script wrote outputs under:

runs/QSB-ST-SHAPIROINFO/SHAPIROINFO39_RAW_STRUCTURE_INVENTORY/

## 4. Output files

The rerun refreshed the following run artifacts:

- inventory_config_resolved.json: 927 bytes
- parse_failures.csv: 57 bytes
- raw_structure_inventory_readout.md: 868 bytes
- raw_structure_inventory_summary.json: 1033 bytes
- raw_structure_inventory_table.csv: 2165 bytes

These files are run artifacts first.

They are not automatically tracked by this note.

## 5. Summary result

The extended parser rerun reported:

- missing_required_summary_keys = []
- total_records = 7
- file_count = 7
- parsed_file_count = 7
- metadata_only_count = 0
- unsupported_count = 0
- parse_failure_count = 0
- parse_status_counts = {'parsed': 7}
- extension_counts = {'.md': 2, '.par': 1, '.sha256': 2, '.tim': 1, '.yaml': 1}

This confirms that the narrow structure-only parser extension resolved the earlier metadata-only and parse-failure coverage limits at the technical structure level.

## 6. CSV result summary

The raw_structure_inventory_table.csv file contained 7 rows.

The parse_failures.csv file contained 0 rows.

The new-field check reported:

- missing_new_fields = []

Parser attempts were:

- checksum_text: 2
- text: 2
- yaml: 1
- timing_text: 1
- parameter_text: 1

## 7. Compact structure observations

The extended parser produced the following structure-only observations:

- .sha256: 2 rows parsed as checksum_text, each with checksum_like_line_count = 1
- .md: 2 rows parsed as text, with text_line_count = 27 and 13
- .yaml: 1 row parsed as yaml, yaml_parse_mode = pyyaml_safe_load, shallow_key_count = 14
- .tim: 1 row parsed as timing_text, text_line_count = 10939, data_like_line_count = 7421, delimiter_hint = whitespace
- .par: 1 row parsed as parameter_text, text_line_count = 456, key_value_like_line_count = 456

These are technical structure observations only.

They are not physical interpretations.

## 8. Technical interpretation

The SHAPIROINFO49 rerun shows that the previous parse failures were parser-coverage limits, not evidence that the local raw artifacts were unusable.

The narrow parser extension improved the technical inventory from:

- parsed_file_count = 2
- metadata_only_count = 5
- parse_failure_count = 5

to:

- parsed_file_count = 7
- metadata_only_count = 0
- parse_failure_count = 0

This is a valid technical progress result.

It means the artifact set now has a complete structure-only inventory at the current parser depth.

It does not mean that a physical Shapiro-information residual exists.

It does not mean that physical analysis is opened.

## 9. Repository and artifact boundary

Final git status showed only:

?? data/QSB-ST-SHAPIROINFO/public_sources/

This confirms that the local raw artifact directory remains untracked.

No files were staged.

No files were committed during the execution.

Run outputs were refreshed but not staged.

No raw artifacts were copied into tracked paths.

No raw artifacts were modified.

No physical interpretation, residual search, model fitting, signal search, or QSB-ST Bridge confirmation claim was made.

## 10. Next practical step

A reasonable next block is:

SHAPIROINFO51_STRUCTURE_INVENTORY_REVIEW_AND_NEXT_SCOPE_DECISION

That next decision should determine whether to:

- stop at the current structure-only inventory,
- create a schema-level review of the .tim and .par structures,
- create a metadata-level review of the .yaml structure,
- preserve the current outputs as run-only artifacts,
- or define a later controlled physical-analysis gate.

Any later physical-analysis gate would require a separate decision and must not be implied by this result note.

## 11. Claim boundary

This note documents a technical structure-inventory rerun result.

It does not provide evidence for a physical Shapiro-information residual.

It does not validate the QSB-ST Bridge.

It does not establish spacetime, quantum-gravity, or relativistic physics claims.

It does not interpret raw artifact content as physical evidence.

It only documents that the extended structure-only inventory parser produced complete technical coverage of the local raw artifact records at the current parser depth.
