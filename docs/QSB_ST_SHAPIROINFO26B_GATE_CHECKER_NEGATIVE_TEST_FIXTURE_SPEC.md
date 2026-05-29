# QSB-ST-SHAPIROINFO26B -- Gate-Checker Negative Test Fixture

## Current Anchor

`c17c88a Add QSB-ST ShapiroInfo gate checker dry-run result note`

## Purpose

SHAPIROINFO26B erstellt kuenstliche Negativ-Fixtures fuer den Gate-Checker.
Der Checker soll absichtlich geoeffnete oder claimsensitiv verletzte
Gate-Zustaende erkennen und nicht mit `BLOCKED_EXPECTED` bestehen lassen.

Diese Fixtures sind keine realen Manifestdaten. Sie sind kuenstliche Testdaten.
Sie duerfen niemals als J0740-Manifest verwendet werden.

## Scope

- negative fixture specification only
- artificial test data only
- no download
- no linked timing-data file opened
- no linked parameter file opened
- no dataset ingestion
- no `.par` / `.tim` parsing
- no PINT / tempo2 execution
- no residual calculation
- no real-data result
- no Bridge claim
- no Shapiro modification claim

## Files Created

| path | role | intentional violation |
|---|---|---|
| `data/QSB-ST-SHAPIROINFO/test_fixtures/j0740_gate_negative_download_open.yaml` | artificial negative fixture | `download_allowed: true` |
| `data/QSB-ST-SHAPIROINFO/test_fixtures/j0740_gate_negative_claim_true.yaml` | artificial negative fixture | `bridge_confirmation_flag: true` |
| `docs/QSB_ST_SHAPIROINFO26B_GATE_CHECKER_NEGATIVE_TEST_FIXTURE_SPEC.md` | fixture specification | documents expected fail-closed behavior |

No existing manifests, sidecars, specs, or scripts are changed by this block.

## Fixture Boundary

The fixture files are deliberately shaped like the blocked J0740 manifest only
so the Gate-Checker can exercise its status logic.

They are not:

- public source manifests
- download manifests
- sidecar drafts
- data-use records
- timing data
- parameter files
- evidence artifacts

They must never be used as the operational J0740 manifest.

## Expected Negative-Test Runs

Allowed command shape, only against artificial fixtures:

```bash
python scripts/run_qsb_st_shapiroinfo24b_gate_checker.py \
  --manifest data/QSB-ST-SHAPIROINFO/test_fixtures/j0740_gate_negative_download_open.yaml \
  --sidecar data/QSB-ST-SHAPIROINFO/correction_state_sidecar_template.yaml \
  --output-dir runs/QSB-ST-SHAPIROINFO26B/negative_download_open \
  --overwrite
```

```bash
python scripts/run_qsb_st_shapiroinfo24b_gate_checker.py \
  --manifest data/QSB-ST-SHAPIROINFO/test_fixtures/j0740_gate_negative_claim_true.yaml \
  --sidecar data/QSB-ST-SHAPIROINFO/correction_state_sidecar_template.yaml \
  --output-dir runs/QSB-ST-SHAPIROINFO26B/negative_claim_true \
  --overwrite
```

Expected result for both runs:

- `gate_decision = UNEXPECTED_GATE_STATE`
- non-zero exit code
- not `BLOCKED_EXPECTED`

## Negative Fixture Table

| fixture | artificial violation | expected checker response | interpretation |
|---|---|---|---|
| `j0740_gate_negative_download_open.yaml` | `download_allowed: true` | `UNEXPECTED_GATE_STATE` | An opened download gate must fail closed. |
| `j0740_gate_negative_claim_true.yaml` | `bridge_confirmation_flag: true` | `UNEXPECTED_GATE_STATE` | A true claim flag must fail closed. |

## Relation To SHAPIROINFO25

SHAPIROINFO25 documented the first positive dry-run control result:
`BLOCKED_EXPECTED` with `exit_code: 0`. SHAPIROINFO26B checks the opposite
direction: a deliberately broken fixture must not pass as `BLOCKED_EXPECTED`.

## Relation To SHAPIROINFO24B

SHAPIROINFO24B introduced the executable Gate-Checker. SHAPIROINFO26B supplies
controlled artificial inputs to verify that the checker rejects unexpectedly
open or claim-violating states.

## Befund

Two artificial negative fixtures are defined: one opens the download gate, and
one sets a claim flag to true.

## Interpretation

The negative fixtures test gate sensitivity only. They do not touch real timing
data and do not say anything about J0740+6620.

## Hypothese

Small negative fixtures can reduce the risk that the Gate-Checker only confirms
the happy blocked path while missing unsafe open states.

## Offene Luecke

- no real manifest changed
- no sidecar changed
- no data downloaded
- no linked file opened
- no `.par` parsed
- no `.tim` parsed
- no adapter for real timing data
- no residual calculation
- no physical interpretation

## Claim Boundary

- no Bridge confirmation
- no physical validation
- no new Shapiro effect claim
- no claim that GR is incomplete
- no claim that any residual implies QSB-ST
- no dataset-specific evidence claim
- no real-data result
- no candidate residual claim from negative fixtures
- no derivation of c
- no explanation of the numerical value of c

## Next Possible Blocks

- SHAPIROINFO27 Gate-Checker Negative Test Result Note
- SHAPIROINFO28 File-Link Metadata Review Plan
- SHAPIROINFO29 Correction-State Sidecar Draft for Manual Review Only
- SHAPIROINFO30 Targeted Binary Pulsar Dry-Run Adapter Spec

## Acceptance Checks

- Datei `j0740_gate_negative_download_open.yaml` existiert
- Datei `j0740_gate_negative_claim_true.yaml` existiert
- Spec existiert
- enthaelt `UNEXPECTED_GATE_STATE`
- enthaelt `download_allowed: true`
- enthaelt `bridge_confirmation_flag: true`
- enthaelt `not BLOCKED_EXPECTED`
- enthaelt no download
- enthaelt no Bridge confirmation
- risk grep clean
- git diff --check clean
- git status --short reported
