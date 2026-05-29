# QSB-ST-SHAPIROINFO23 -- Local Storage and Raw Data Policy Note

## Current anchor

`40e3808 Update QSB-ST ShapiroInfo J0740 manifest after README release inspection`

## Purpose

SHAPIROINFO23 definiert eine lokale Speicher- und Rohdatenpolitik fuer
spaetere J0740+6620-Datenkontakte. Ziel ist, unkontrollierte Downloads, stille
Dateiaenderungen, versehentliche Raw-Data-Commits und unklare Provenance zu
verhindern.

Dieser Block ist eine Policy Note, kein Download- oder Datenkontakt-Block.

## Source Context

Builds on:

- `docs/QSB_ST_SHAPIROINFO22_J0740_MANIFEST_UPDATE_AFTER_README_RELEASE_INSPECTION.md`
- `docs/QSB_ST_SHAPIROINFO21_J0740_README_RELEASE_NOTE_INSPECTION_RESULT.md`
- `docs/QSB_ST_SHAPIROINFO19_J0740_MANIFEST_UPDATE_AFTER_DATA_USE_REVIEW.md`
- `data/QSB-ST-SHAPIROINFO/j0740_6620_download_manifest_manual_review.yaml`

## Scope

- local storage / raw-data policy only
- no download
- no file opening
- no dataset ingestion
- no `.par` / `.tim` parsing
- no PINT / tempo2 execution
- no residual calculation
- no real-data result
- no Bridge claim
- no Shapiro modification claim

## Arbeitsrealismus

Die SHAPIROINFO-Kette darf nicht endlos nur weitere Gate-Notes erzeugen.
SHAPIROINFO23 soll der letzte reine Infrastruktur-/Policy-Block vor einem
Wechsel zu einem kontrollierten naechsten technischen Schritt sein.

After SHAPIROINFO23, the project should move toward a bounded technical step
rather than extending the gate chain indefinitely.

## Proposed Local Storage Layout

Geplante Struktur, noch nicht erstellen:

- `data/QSB-ST-SHAPIROINFO/public_sources/j0740_6620/`
- `data/QSB-ST-SHAPIROINFO/public_sources/j0740_6620/raw/`
- `data/QSB-ST-SHAPIROINFO/public_sources/j0740_6620/manifest/`
- `data/QSB-ST-SHAPIROINFO/public_sources/j0740_6620/checksums/`
- `data/QSB-ST-SHAPIROINFO/public_sources/j0740_6620/notes/`

Diese Ordner werden in SHAPIROINFO23 nicht erzeugt. Nur Policy.

## Raw-Data Tracking Policy

- raw timing-data files are local-only by default
- raw parameter files are local-only by default
- raw files are local-only by default
- raw public files are not committed unless explicit later policy pass says otherwise
- checksums and manifests may be tracked
- derived tiny metadata summaries may be tracked only after review
- no silent overwrite
- no silent replacement
- no manual copy without manifest entry
- no file rename without manifest update

## Git Policy Table

| item | git_tracking_default | allowed_if | blocking_note |
|---|---|---|---|
| `raw_timing_data_file` | not tracked | only after explicit later policy pass | Raw timing data stays local-only by default. |
| `raw_parameter_file` | not tracked | only after explicit later policy pass | Raw parameter files stay local-only by default. |
| `download_manifest` | trackable | source, path, timestamp, and gate status are explicit | Manifest is audit material, not raw data. |
| `checksum_file` | trackable | checksum method and source file identity are explicit | sha256 file can be tracked after review. |
| `retrieval_log` | trackable | retrieval action is documented without raw payload | Logs must not include hidden downloaded content. |
| `source_review_note` | trackable | note stays at public context level | Review notes do not authorize download. |
| `correction_state_sidecar` | trackable after manual review | sidecar fields are reviewed and claim flags remain false | No sidecar from unreviewed raw files. |
| `derived_metadata_summary` | trackable after review | tiny, non-raw, provenance-linked summary only | Must not reconstruct raw data content. |
| `adapter_output` | not applicable until later | only after separate adapter gate | No adapter output exists here. |
| `residual_output` | not applicable until later | only after separate residual gate | No residual output exists here. |

## Integrity Requirements

Before any later adapter use, a controlled file contact must record:

- sha256 checksum
- file size
- retrieval timestamp UTC
- source URL
- retrieval command or browser action note
- downloaded filename
- local path
- no overwrite policy
- post-download manifest update
- checksum verification before adapter use

## Quarantine Principle

A downloaded public file is not a project datum until its manifest, checksum,
source context, and correction-state relevance are reviewed.

Ein heruntergeladenes File ist noch kein Projektdatensatz. Es ist zuerst
Quarantaene-Material (Quarantäne-Material).

## Gate Statuses

`local_storage_policy_status = LOCAL_STORAGE_POLICY_DEFINED`

`raw_data_tracking_status = BLOCKED_RAW_DATA_TRACKING`

`download_gate_status = BLOCKED_BEFORE_DOWNLOAD`

`sidecar_gate_status = BLOCKED_BEFORE_SIDECAR_DRAFT`

`dry_run_gate_status = BLOCKED_BEFORE_DRY_RUN`

## What This Policy Allows Later

Nur spaeter:

- controlled download manifest update
- controlled local raw directory creation
- checksum generation
- source/path recording
- still no parsing unless separate adapter gate exists

## What Remains Blocked

- current download
- raw data commit
- `.par` / `.tim` parsing
- sidecar population from files
- adapter dry-run
- residual preview
- physical interpretation

## Relation To SHAPIROINFO22

SHAPIROINFO22 updated the manifest after page-level inspection. SHAPIROINFO23
defines where data may later live if a download gate ever opens.

## Befund

The project now has a storage and raw-data policy before any J0740+6620 file is
downloaded.

## Interpretation

This reduces the risk that public files enter the repo as uncontrolled
artifacts.

## Hypothese

A short local-storage policy can prevent later provenance drift without
prolonging the gate chain indefinitely.

## Offene Luecke

- no directories created
- no download
- no files inspected
- no checksums generated
- no sidecar populated
- no adapter run
- no residual calculation

## Claim Boundary

- no Bridge confirmation
- no physical validation
- no new Shapiro effect claim
- no claim that GR is incomplete
- no claim that any residual implies QSB-ST
- no dataset-specific evidence claim
- no real-data result
- no candidate residual claim from storage policy
- no derivation of c
- no explanation of the numerical value of c

## Next Recommended Block

Recommended next:

SHAPIROINFO24 -- Minimal Controlled Download Gate or File-Link Metadata Review

Alternative:

SHAPIROINFO24 -- Targeted Binary Pulsar Dry-Run Adapter Spec, if download
remains blocked.

Do not continue indefinitely with more pure policy notes unless a concrete
blocker requires it.

## Acceptance Checks

- Datei existiert
- enthaelt LOCAL_STORAGE_POLICY_DEFINED
- enthaelt BLOCKED_RAW_DATA_TRACKING
- enthaelt BLOCKED_BEFORE_DOWNLOAD
- enthaelt BLOCKED_BEFORE_SIDECAR_DRAFT
- enthaelt BLOCKED_BEFORE_DRY_RUN
- enthaelt raw files are local-only by default
- enthaelt sha256
- enthaelt Quarantäne
- enthaelt After SHAPIROINFO23
- enthaelt no download
- enthaelt no Bridge confirmation
- risk grep clean
- git diff --check clean
- git status --short reported
