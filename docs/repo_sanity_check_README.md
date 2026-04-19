# repo_sanity_check.sh

## Purpose

This script performs a **non-destructive structural sanity check** for the repository and the consolidated numerics subtree.

It is meant to verify:

- whether the core repository files are present
- whether the numerics subtree still exists in the intended place
- whether quarantined and archived files are where they should be
- whether known bad active-path files are gone
- whether the heavy artifact remains archived
- what the current short Git status looks like

## What the script writes

The script creates a timestamped directory under:

`docs/repo_checks/`

Inside it writes:

1. `repo_sanity_report.md` — human-readable summary  
2. `root_checks.txt` — root-level expected file checks  
3. `numerics_checks.txt` — numerics subtree expected structure checks  
4. `absent_active_bad_files.txt` — checks that known bad active-path files are gone  
5. `present_quarantine_files.txt` — checks that known quarantine files exist in quarantine  
6. `present_masterchat_archive_files.txt` — checks that archived non-canonical masterchat files exist  
7. `heavy_archive_check.txt` — checks for heavy artifact archive state  
8. `masterchat_active_scan.txt` — remaining masterchat-like files outside the non-canonical archive  
9. `git_status_short.txt` — short `git status` snapshot  
10. `top_level_tree.txt` — shallow repository structure listing  
11. `numerics_top_tree.txt` — shallow numerics subtree structure listing

It also updates a symlink:

`docs/repo_checks/latest`

## What the script does not do

The script does **not**:

- move files
- delete files
- rename files
- modify Git state
- rewrite repository contents

It only inspects and reports.

## Usage

Standard usage:

```bash
bash scripts/repo_sanity_check.sh
```

Or with explicit root path:

```bash
bash scripts/repo_sanity_check.sh /home/ralf-kemmann/Downloads/deBroglie_Kaster_Theorie/quantum-spacetime-bridge
```

## Field list

1. `PROJECT_ROOT` — Shell string — root path of the repository  
2. `NUMERICS_ROOT` — Shell string — consolidated numerics subtree path  
3. `DOCS_DIR` — Shell string — repository documentation directory  
4. `OUT_DIR` — Shell string — target directory for sanity-check output  
5. `STAMP` — Shell string — timestamp for the current check run  
6. `RUN_DIR` — Shell string — timestamped result directory for one sanity-check run  
7. `REPORT_MD` — Shell string — path to the generated Markdown report  
8. `LATEST_LINK` — Shell string — symlink to the newest check run  
9. `ROOT_ITEMS` — Shell array — expected root-level files/documents  
10. `NUMERICS_ITEMS` — Shell array — expected numerics subtree items  
11. `SHOULD_BE_GONE` — Shell array — known files that should no longer remain in active paths  
12. `SHOULD_BE_IN_QUARANTINE` — Shell array — files expected inside `_quarantine/`  
13. `SHOULD_BE_IN_MASTERCHAT_ARCHIVE` — Shell array — files expected inside `_archive_masterchat_noncanonical/`  
14. `HEAVY_ARCHIVE_ITEM` — Shell string — archived heavy artifact path  
15. `ACTIVE_HEAVY_OLD_PATH` — Shell string — old active-path location of the heavy artifact  
16. `ROOT_CHECKS` — Shell string — output file for root-level checks  
17. `NUMERICS_CHECKS` — Shell string — output file for numerics subtree checks  
18. `ABSENT_ACTIVE_BAD_FILES` — Shell string — output file for removed-active-path checks  
19. `PRESENT_QUARANTINE_FILES` — Shell string — output file for quarantine presence checks  
20. `PRESENT_MASTERCHAT_ARCHIVE_FILES` — Shell string — output file for non-canonical masterchat archive checks  
21. `MASTERCHAT_ACTIVE_SCAN` — Shell string — output file for remaining masterchat-like files outside archive  
22. `HEAVY_CHECK` — Shell string — output file for heavy artifact archive checks  
23. `GIT_STATUS` — Shell string — output file for short Git status  
24. `TOP_LEVEL_TREE` — Shell string — output file for shallow repository tree  
25. `NUMERICS_TOP_TREE` — Shell string — output file for shallow numerics tree  
26. `fail()` — Shell function — abort helper for invalid paths  
27. `status_ok()` — Shell function — report helper for successful checks  
28. `status_warn()` — Shell function — report helper for warning or missing checks

## Maintenance note

This script encodes the current cleanup assumptions. If the repository structure changes intentionally, the expected item arrays should be updated so the script continues to reflect the intended project state.
