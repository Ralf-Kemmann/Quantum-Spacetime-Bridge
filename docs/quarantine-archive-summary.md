# Quarantine and Archive Summary

## Purpose of this document

This document summarizes the current quarantine and archive actions carried out during the cleanup of the consolidated numerics subtree inside the **Quantum–Spacetime Bridge** repository.

Its purpose is to make the cleanup process transparent, reviewable, and recoverable. No cleanup action should disappear into an undocumented side effect. This summary therefore records which files were moved, why they were moved, and how their new locations should be interpreted.

## Scope

The cleanup actions described here apply to the consolidated numerics subtree:

```text
numerics/debroglie-phase-bridge/
```

This subtree was imported as a large historical and active research work tree. Because the project follows a strict transparency rule, cleanup has been performed by **classification and relocation**, not by silent deletion.

## Cleanup location types

At the current stage, three cleanup-related location types are in use.

### 1. `_quarantine/`

This location is used for files that are considered **non-canonical, malformed, misnamed, accidental, or structurally unsafe to keep in the active tree**.

Files moved here are not assumed to be meaningless, but they are treated as unsuitable for the active working structure until explicitly reviewed again.

### 2. `_archive_heavy/`

This location is used for files that are **legitimate project artifacts** but too large or too detail-heavy to remain in the most active visible layer of a run directory.

Files moved here are not errors. They are preserved as heavy artifacts while improving readability of the active run directory.

### 3. `_archive_masterchat_noncanonical/`

This location is used for **non-canonical masterchat and masterchat-like files** that should not remain in the active tree once a single canonical masterchat has been identified.

These files are preserved for provenance and historical reference, but they are no longer treated as active project guidance documents.

## Current canonical rule

At the present stage, the canonical masterchat is:

```text
numerics/debroglie-phase-bridge/docs/project/MASTERCHAT_CANONICAL.md
```

This rule was used to distinguish active and non-canonical masterchat material.

## Current quarantine contents

The current `_quarantine/` area contains files that were identified as malformed or misnamed active-tree artifacts.

### Quarantine rationale

The rationale for quarantine use is:

- the file exists
- the file may contain meaningful content
- but the filename, location, or role is not acceptable for the active tree
- therefore the file is removed from the active path without being destroyed

### Current known quarantine examples

1. **`typ_b_analysis/configs/run:.yaml`**  
   **Reason:** malformed filename and non-canonical parallel configuration artifact

2. **`typ_b_analysis/src/from __future__ import annotations.py`**  
   **Reason:** malformed filename and non-canonical parallel source artifact

3. **`typ_b_analysis/src/bridge_carrier_block_d.py.bak`**  
   **Reason:** backup file not suitable for active source tree

4. **`typ_b_analysis/src/bridge_carrier_leave_one_out.py.bak`**  
   **Reason:** backup file not suitable for active source tree

## Current heavy archive contents

The current `_archive_heavy/` area contains large run artifacts that are legitimate but not ideal as top-level active run files.

### Heavy archive rationale

The rationale for heavy archive use is:

- file is legitimate
- file is not obviously accidental
- file is large enough to reduce run-directory readability
- smaller summaries or derived files already exist nearby

### Current known heavy archive example

1. **`m33_v0_scaffold/runs/M33_V0_alpha_peak_robustness/M35b_packet_kernel/source_curve_grid.csv`**  
   **Reason:** large detail-rich run artifact moved out of the most active run view while preserved in-place under a local heavy archive directory

## Current non-canonical masterchat archive contents

The current `_archive_masterchat_noncanonical/` area contains non-canonical masterchat and masterchat-like files that were moved out of the active tree once the single canonical masterchat was identified.

### Masterchat archive rationale

The rationale for masterchat archival use is:

- there must be a single canonical masterchat
- other masterchat-like files create noise, ambiguity, or split guidance
- historical and context files should be preserved, but not left as apparently active competing sources

### Current known non-canonical masterchat examples

1. **`docs/project/MASTERCHAT_CANONICAL_backup_2026-03-30_M39x1.md`**  
   **Reason:** backup of canonical masterchat, not the active canonical file

2. **`m33_v0_scaffold/docs/project/MASTERCHAT_CANONICAL.md`**  
   **Reason:** non-canonical parallel masterchat location

3. **`typ_b_analysis/docs/MASTERCHAT_RELOCATION_CURRENT_2026-04-05.md`**  
   **Reason:** relocation/status note, not canonical masterchat

4. **`typ_b_analysis/MASTERCHAT_CURRENT_STATUS_2026-04-09_v2.md`**  
   **Reason:** status snapshot, not canonical masterchat

5. **`typ_b_analysis/MASTERCHAT_CURRENT_STATUS_2026-04-10_v3.md`**  
   **Reason:** status snapshot, not canonical masterchat

6. **`typ_b_analysis/masterchat_current_status_2026_04_09_v_2.md`**  
   **Reason:** duplicate status-style masterchat snapshot

7. **`typ_b_analysis/MASTERCHAT_EINFUEGESTUECK_BRUECKE_KONSOLIDIERT_v1.md`**  
   **Reason:** insertion/consolidation note, not canonical masterchat

8. **`typ_b_analysis/notes/MASTERCHAT_CURRENT_STATUS_2026-04-09.md`**  
   **Reason:** notes-level status snapshot, not canonical masterchat

9. **`typ_b_analysis/notes/masterchat_current_status_2026_04_09_v_2.md`**  
   **Reason:** notes-level duplicate status snapshot

10. **`typ_b_analysis/notes/MASTERCHAT_Gravitation_und_RaumZeit_v1.md`**  
    **Reason:** historical/project note, not the current canonical masterchat

## What has not been done

The cleanup so far has intentionally **not** done the following:

- no irreversible deletion of the quarantined or archived files
- no silent cleanup of calculation-relevant material
- no collapse of M33 branches without interpretation
- no hidden rewrite of provenance

This is deliberate and consistent with the project’s transparency standard.

## Current interpretation of the cleanup state

The repository is now in a cleaner and more legible intermediate state:

- malformed or unsafe files have been removed from active paths
- heavy artifacts have been separated from active run surfaces
- masterchat ambiguity has been reduced
- historical material has been preserved rather than destroyed

At the same time, the cleanup remains **recoverable** and **documented**.

## Suggested next step

A reasonable next step would be one of the following:

- create a short `docs/archive-policy.md`
- create a `docs/quarantine-log.md`
- or continue with targeted cleanup of additional non-canonical but non-destructive file classes

## Field list

1. `scope` — String — repository subtree to which the summary applies  
2. `cleanup_location_type` — String — category of cleanup location (`_quarantine`, `_archive_heavy`, `_archive_masterchat_noncanonical`)  
3. `canonical_masterchat` — String — path of the single currently valid canonical masterchat  
4. `quarantine_item` — String — file moved to quarantine  
5. `quarantine_reason` — String — reason why the file was removed from the active tree  
6. `heavy_archive_item` — String — file moved to heavy archive  
7. `heavy_archive_reason` — String — reason why the file was archived as a heavy artifact  
8. `masterchat_archive_item` — String — masterchat-like file moved to non-canonical archive  
9. `masterchat_archive_reason` — String — reason why the file is archived and not active  
10. `not_done_rule` — String — cleanup action intentionally not performed  
11. `current_cleanup_state` — String — interpretation of the present cleanup stage  
12. `next_step_candidate` — String — possible next cleanup or documentation step

## Bottom line

The current cleanup has not hidden anything. It has **classified and relocated** selected files into clearly named non-active areas:

- `_quarantine/` for malformed or unsafe active-tree artifacts
- `_archive_heavy/` for large but legitimate heavy artifacts
- `_archive_masterchat_noncanonical/` for non-canonical masterchat material

This preserves the project’s transparency rule while making the active repository structure cleaner and easier to understand.
