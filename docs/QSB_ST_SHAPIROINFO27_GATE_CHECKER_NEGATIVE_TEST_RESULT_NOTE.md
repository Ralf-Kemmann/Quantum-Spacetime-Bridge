# QSB-ST-SHAPIROINFO27 -- Gate-Checker Negative Test Result Note

## Current Anchor

`855b606 Add QSB-ST ShapiroInfo gate checker negative fixtures`

## Purpose

SHAPIROINFO27 haelt fest, dass der Gate-Checker nicht nur korrekt geschlossene
Gates akzeptiert, sondern auch kuenstlich geoeffnete oder claimsensitiv
verletzte Gate-Zustaende ablehnt.

Dieser Block dokumentiert das Ergebnis der SHAPIROINFO26B-Negativtests. Der
Gate-Checker hat kuenstlich verletzte Gate-Zustaende erkannt und mit non-zero
Exit abgelehnt.

## Scope

- negative test result note only
- artificial fixtures only
- no download
- no linked timing-data file opened
- no linked parameter file opened
- no real J0740 data
- no dataset ingestion
- no `.par` / `.tim` parsing
- no PINT / tempo2 execution
- no residual calculation
- no real-data result
- no Bridge claim
- no Shapiro modification claim

## Tested Fixtures

- `data/QSB-ST-SHAPIROINFO/test_fixtures/j0740_gate_negative_download_open.yaml`
- `data/QSB-ST-SHAPIROINFO/test_fixtures/j0740_gate_negative_claim_true.yaml`

## Runtime Commands

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

## Observed Result Summary

negative_download_open:

- gate_decision: UNEXPECTED_GATE_STATE
- failed_checks: 1
- exit_code: 2
- overall_status: UNEXPECTED_GATE_STATE
- expected_blocked_check_passed: False
- unexpected_open_fields: ['download_allowed']

negative_claim_true:

- gate_decision: UNEXPECTED_GATE_STATE
- failed_checks: 1
- exit_code: 2
- overall_status: UNEXPECTED_GATE_STATE
- expected_blocked_check_passed: False

## Result Table

| fixture | artificial_violation | expected_behavior | observed_status | exit_code | result |
|---|---|---|---|---|---|
| `j0740_gate_negative_download_open.yaml` | `download_allowed: true` | fail closed / non-zero | `UNEXPECTED_GATE_STATE` | `2` | pass |
| `j0740_gate_negative_claim_true.yaml` | `bridge_confirmation_flag: true` | fail closed / non-zero | `UNEXPECTED_GATE_STATE` | `2` | pass |

## Interpretation

Der Negativtest ist erfolgreich, weil der Checker die Fixtures nicht als
`BLOCKED_EXPECTED` akzeptiert. Ein erfolgreicher Negativtest bedeutet hier:
kuenstliche Verletzung erkannt, Testlauf abgelehnt.

## Befund

Der Gate-Checker erkennt:

- ein kuenstlich geoeffnetes Download-Gate
- eine kuenstliche Claim-Flag-Verletzung

und liefert jeweils `UNEXPECTED_GATE_STATE` mit `exit_code: 2`.

## Hypothese

Negative Fixtures reduzieren das Risiko eines false green, falls spaetere
Manifest- oder Sidecar-Felder versehentlich geoeffnet oder claimsensitiv
verletzt werden.

## Offene Luecke

- no real data tested
- no download
- no `.par` parsed
- no `.tim` parsed
- no sidecar populated from data
- no adapter run on timing data
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

- SHAPIROINFO28 File-Link Metadata Review Plan
- SHAPIROINFO29 Correction-State Sidecar Draft for Manual Review Only
- SHAPIROINFO30 Targeted Binary Pulsar Dry-Run Adapter Spec

## Acceptance Checks

- Datei existiert
- enthaelt UNEXPECTED_GATE_STATE
- enthaelt expected_blocked_check_passed: False
- enthaelt exit_code: 2
- enthaelt failed_checks: 1
- enthaelt download_allowed
- enthaelt bridge_confirmation_flag
- enthaelt false green
- enthaelt no download
- enthaelt no Bridge confirmation
- risk grep clean
- git diff --check clean
- git status --short reported
