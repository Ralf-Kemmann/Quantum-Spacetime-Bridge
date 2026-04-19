# inventory_numerics_cleanup.sh

## Purpose

This script performs a **non-destructive inventory pass** on the consolidated numerics subtree:

`numerics/debroglie-phase-bridge/`

It is meant as the first technical step of repository cleanup.

## What the script does

The script creates a timestamped inventory folder under:

`docs/numerics_inventory/`

Inside that folder it writes:

1. `all_files.txt` — list of all files in the numerics subtree  
2. `all_dirs.txt` — list of all directories  
3. `backup_files.txt` — likely backup or temporary files such as `.bak`, `~`, `.tmp`, `.orig`  
4. `suspicious_names.txt` — suspicious filenames and likely accident artifacts  
5. `duplicate_basenames.txt` — repeated filenames across different paths  
6. `large_files_over_10MB.txt` — large files for later review  
7. `markdown_files.txt` — all Markdown files  
8. `json_files.txt` — all JSON files  
9. `csv_files.txt` — all CSV files  
10. `run_like_directories.txt` — directories that look like runs or result bundles  
11. `numerics_inventory_report.md` — compact human-readable summary

It also updates a symlink:

`docs/numerics_inventory/latest`

so the newest run is easy to find.

## What the script does not do

The script does **not**:

- delete files
- rename files
- move files
- archive files
- rewrite repository structure

This is deliberate and matches the project's transparency rule.

## Usage

Standard usage from the project root:

```bash
bash scripts/inventory_numerics_cleanup.sh
```

Or with explicit path:

```bash
bash scripts/inventory_numerics_cleanup.sh /home/ralf-kemmann/Downloads/deBroglie_Kaster_Theorie/quantum-spacetime-bridge
```

## Field list

1. `PROJECT_ROOT` — Shell string — root path of the project repository  
2. `NUMERICS_DIR` — Shell string — location of the imported numerics subtree  
3. `OUT_DIR` — Shell string — target directory for inventory outputs  
4. `STAMP` — Shell string — timestamp for the current inventory run  
5. `RUN_DIR` — Shell string — timestamped directory containing one inventory run  
6. `ALL_FILES` — Shell string — path to the generated full file list  
7. `ALL_DIRS` — Shell string — path to the generated full directory list  
8. `BAK_FILES` — Shell string — path to the generated backup-file list  
9. `SUSPICIOUS_NAMES` — Shell string — path to the generated suspicious-name list  
10. `DUPLICATE_BASENAMES` — Shell string — path to the generated duplicate-basename list  
11. `LARGE_FILES` — Shell string — path to the generated large-file list  
12. `MD_FILES` — Shell string — path to the generated Markdown-file list  
13. `JSON_FILES` — Shell string — path to the generated JSON-file list  
14. `CSV_FILES` — Shell string — path to the generated CSV-file list  
15. `RUN_DIRS` — Shell string — path to the generated run-like-directory list  
16. `REPORT_MD` — Shell string — path to the generated Markdown report  
17. `LATEST_LINK` — Shell string — path to the symlink pointing to the newest inventory run  
18. `count_lines()` — Shell function — helper function that counts lines in generated inventory files

## Maintenance note

This script should remain non-destructive. If later cleanup automation is added, it should be done in a separate script so that inventory and action remain clearly separated.
