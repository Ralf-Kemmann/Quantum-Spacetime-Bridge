# QSB-ST SHAPIROINFO44 — Harmonized Raw Structure Inventory Result Note

Date: 2026-05-30  
Status: harmonized raw-structure inventory result documented  
Upstream execution: SHAPIROINFO43_CONTROLLED_RAW_STRUCTURE_INVENTORY_RERUN_HARMONIZED_SCHEMA  
Execution scope: technical structure inventory only  
Physics-analysis status: closed for interpretation and residual claims  
Tracking decision: this documentation note may be tracked; raw artifacts remain local-only and untracked

## 1. Purpose

This note documents the harmonized SHAPIROINFO43 raw-structure inventory rerun.

The rerun followed the SHAPIROINFO38 to SHAPIROINFO42 boundary:

- SHAPIROINFO38 opened the first raw inventory gate for structure-only inspection.
- SHAPIROINFO39 defined the raw-structure inventory plan.
- SHAPIROINFO40 created the inventory script.
- SHAPIROINFO42 harmonized the summary schema before final result documentation.
- SHAPIROINFO43 executed the harmonized inventory exactly once.

This is part of a physics-motivated research route, but the present result is a technical structure-inventory result only.

It does not provide physical interpretation, residual search, signal search, model fitting, or QSB-ST Bridge-related claims.

## 2. Command executed

The script help was inspected first.

Then the inventory script was executed exactly once using default paths:

python scripts/qsb_st_shapiroinfo40_raw_structure_inventory.py

The script used the input root:

data/QSB-ST-SHAPIROINFO/public_sources/

The script wrote outputs under:

runs/QSB-ST-SHAPIROINFO/SHAPIROINFO39_RAW_STRUCTURE_INVENTORY/

## 3. Output files

The harmonized rerun produced or refreshed the following run artifacts:

- inventory_config_resolved.json: 774 bytes
- parse_failures.csv: 567 bytes
- raw_structure_inventory_readout.md: 887 bytes
- raw_structure_inventory_summary.json: 1057 bytes
- raw_structure_inventory_table.csv: 1422 bytes

These files are run artifacts first.

They are not automatically tracked by this note.

## 4. Harmonized summary schema result

The harmonized summary schema check passed.

Result:

- missing_required_summary_keys = []
- total_records = 7
- file_count = 7
- parsed_file_count = 2
- metadata_only_count = 5
- unsupported_count = 0
- parse_failure_count = 5

The harmonized summary now provides both the original raw inventory summary structure and convenience keys required by the SHAPIROINFO39 plan and later readouts.

## 5. CSV result summary

The raw_structure_inventory_table.csv file contained 7 rows.

The parse_failures.csv file contained 5 rows.

This confirms that the inventory run produced a coherent table-level and parse-failure-level structure readout.

## 6. Technical interpretation

The SHAPIROINFO43 rerun produced a controlled first technical structure map of the local ShapiroInfo raw artifact set.

The result indicates:

- 7 local raw artifact records were inventoried.
- 2 records were parsed by the minimal inventory procedure.
- 5 records remained metadata-only and/or produced parse-failure records.
- 0 records were counted as unsupported under the harmonized summary schema.

The parse failures are valid inventory outcomes.

They indicate that the first minimal parser did not directly parse those artifacts into the supported simple structures.

They do not imply physical failure or physical evidence.

They only define the next technical review layer.

## 7. Repository and artifact boundary

Final git status showed only:

?? data/QSB-ST-SHAPIROINFO/public_sources/

This confirms that the local raw artifact directory remains untracked.

No files were staged.

No files were committed during the execution.

No raw artifacts were copied into tracked paths.

No raw artifacts were modified.

No physical interpretation, residual search, signal search, model fitting, or QSB-ST Bridge confirmation claim was made.

## 8. Next practical step

The next practical step may be a result-review note or parser-follow-up decision.

A reasonable next block is:

SHAPIROINFO45_RAW_STRUCTURE_INVENTORY_REVIEW_AND_NEXT_PARSER_DECISION

That decision should determine whether to:

- keep the minimal parser unchanged and document the 5 parse failures as accepted inventory limits,
- add a small parser extension for specific file types,
- create a metadata-only review of parse failures,
- or stop the ShapiroInfo raw route if the available artifacts are not suitable.

## 9. Claim boundary

This note documents a technical raw-structure inventory result.

It does not provide evidence for a physical Shapiro-information residual.

It does not validate the QSB-ST Bridge.

It does not establish spacetime, quantum-gravity, or relativistic physics claims.

It does not interpret raw artifact content as physical evidence.

It only documents that the first harmonized structure-only inventory execution completed and produced reviewable run artifacts.
