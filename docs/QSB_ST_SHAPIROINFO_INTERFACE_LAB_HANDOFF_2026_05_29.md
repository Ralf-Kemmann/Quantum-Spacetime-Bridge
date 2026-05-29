# QSB-ST -- ShapiroInfo Interface Lab Handoff 2026-05-29

## Current anchor

`26edb9f Add QSB-ST ShapiroInfo correction-state field schema`

Origin-Anker vor dieser lokalen Arbeitsstrecke:

`183fdbc Add QSB-ST INTERFACE02 minimal record schema spec`

## Scope

Diese Handoff-Datei fasst die lokale Arbeitsstrecke zusammen: INTERFACE03 plus
SHAPIROINFO01 bis SHAPIROINFO10.

- Keine neue Analyse.
- Keine neuen Daten.
- Keine neue Physikinterpretation.
- Nur Uebergabe-/Orientierungsnotiz.

## Executive Summary Fuer Menschen

QSB-ST wurde in dieser Strecke als Interface/Ventil zwischen RT und QM
weitergefuehrt. INTERFACE03 etablierte einen RT/QM-Rosetta-Translator mit `c`
als vorsichtigem Interface-Kandidaten.

SHAPIROINFO01 bis 05 bauten und testeten eine minimale Residual-Logik.
SHAPIROINFO04/05 zeigten: Der Toy-Comparator funktioniert technisch im
Minimalumfang. SHAPIROINFO06/07 ueberfuehrten Deep Research in Dateninventar
und Feasibility-Schleuse.

SHAPIROINFO08/09 planten den Weg zu einem engen halb-realen
Pulsar-Timing-Pilot. SHAPIROINFO10 setzte Correction-State als blockierende
Interpretierbarkeitsschicht fest.

## Commit Timeline

| commit | file/block | purpose | status |
|---|---|---|---|
| `f52223c` | `docs/QSB_ST_INTERFACE03_RT_QM_CAUSALITY_ROSETTA_TRANSLATOR_SPEC.md` / INTERFACE03 | RT/QM-Rosetta-Translator und vorsichtiger Interface-Kandidat `c`. | specification only |
| `58e906a` | `docs/QSB_ST_SHAPIROINFO01_RELATIONAL_DELAY_TO_INFORMATION_RESIDUAL_SPEC.md` / SHAPIROINFO01 | Relationale Delay-zu-Information-Residual-Spezifikation. | specification only |
| `8e9d7ce` | `docs/QSB_ST_INTERFACE_SHAPIROINFO_RESULT_READOUT_2026_05_28.md` / ShapiroInfo interface readout | Ergebnis-/Readout-Rahmen fuer ShapiroInfo-Interface-Arbeit. | orientation/readout |
| `da8263f` | `docs/QSB_ST_SHAPIROINFO02_MINIMAL_SIGNAL_RECORD_SCHEMA_SPEC.md` / SHAPIROINFO02 | Minimales Signal-Record-Schema fuer spaetere A/B-/Kontrollvergleiche. | schema spec |
| `7102e13` | `docs/QSB_ST_SHAPIROINFO03_TOY_COMPARATOR_PLAN.md` / SHAPIROINFO03 | Plan fuer synthetischen Toy-Comparator. | plan only |
| `f925ddc` | `docs/QSB_ST_SHAPIROINFO04_TOY_COMPARATOR_MINIMAL_RUNNER_SPEC.md` / SHAPIROINFO04 | Minimaler Toy-Comparator-Runner und Ausfuehrungsrahmen. | minimal runner created and run locally |
| `0f2565e` | `docs/QSB_ST_SHAPIROINFO05_TOY_COMPARATOR_RESULT_NOTE.md` / SHAPIROINFO05 | Result Note zum synthetischen Toy-Comparator-Lauf. | synthetic toy result note |
| `35da881` | `docs/QSB_ST_SHAPIROINFO06_DATA_AND_SCENARIO_INVENTORY_NOTE.md` / SHAPIROINFO06 | Daten- und Szenarioinventar aus Deep Research. | inventory note |
| `2fe5456` | `docs/QSB_ST_SHAPIROINFO07_PUBLIC_DATASET_FEASIBILITY_MATRIX_SPEC.md` / SHAPIROINFO07 | Feasibility-Matrix fuer oeffentliche Datensatzpfade. | feasibility gate |
| `632539e` | `docs/QSB_ST_SHAPIROINFO08_TOY_TO_SEMI_REAL_ADAPTER_PLAN.md` / SHAPIROINFO08 | Plan fuer Toy-to-semi-real Adapter. | adapter plan only |
| `363720a` | `docs/QSB_ST_SHAPIROINFO09_TARGETED_BINARY_PULSAR_PILOT_PLAN.md` / SHAPIROINFO09 | Enger Pilotpfad fuer targeted binary pulsar package. | pilot plan only |
| `26edb9f` | `docs/QSB_ST_SHAPIROINFO10_CORRECTION_STATE_FIELD_SCHEMA.md` / SHAPIROINFO10 | Correction-State-Feldschema als blockierende Sidecar-Schicht. | schema spec |

## Functional Result

SHAPIROINFO04 minimal runner wurde erstellt. SHAPIROINFO04 wurde lokal
ausgefuehrt.

Run-Outputs lagen unter:

`runs/QSB-ST-SHAPIROINFO04/toy_comparator_minimal_open/`

SHAPIROINFO05 dokumentiert:

- `variant_count = 6`
- `expected_status_check_passed = true`
- Statusklassen:
  - `no_residual`
  - `artifact_likely`
  - `candidate_residual`
  - `inconclusive`

Dieses Ergebnis ist nur ein synthetischer Toy-Funktionstest. Es ist kein
Real-Daten-Ergebnis und keine Aussage ueber echte Residuen.

## Data-Path Result

Deep Research empfahl PTA/Pulsar Timing als sichersten ersten halb-realen
Datenpfad.

- Cassini bleibt physikalisch interessant, aber nicht erster Ingest wegen
  Rohdaten-/Korrekturlast.
- VLBI bleibt relevant, aber QC-/Modellierungs-lastig.
- Lensing bleibt sekundaer-taxonomisch.
- Erster Kandidat: targeted binary pulsar package, e.g. NANOGrav J0740+6620.

## Correction-State Result

Correction-State ist jetzt Pflichtkonzept. Kein halb-realer Adapterlauf ohne
Sidecar.

Zentrale Schichten:

- clock correction state
- ephemeris state
- DM / ISM state
- solar wind state
- backend / instrument state
- noise model state
- QC / outlier state
- provenance / release state

Correction-State is not metadata decoration. Correction-State is a blocking
interpretability layer.

## What Has NOT Been Done

- keine echten Shapiro-Daten geladen
- keine Pulsar-Daten geladen
- keine `.par`/`.tim`-Dateien geparst
- kein PINT/tempo2-Lauf
- keine Cassini-/VLBI-Datenanalyse
- keine reale Residualsuche
- keine physikalische Validierung
- keine Bridge-Bestaetigung
- keine Aussage ueber echte Residuen

## Claim Boundary

- no Bridge confirmation
- no physical validation
- no new Shapiro effect claim
- no claim that GR is incomplete
- no claim that any residual implies QSB-ST
- no dataset-specific evidence claim
- no real-data result
- no candidate residual claim from planning
- no derivation of c
- no explanation of the numerical value of c

## Next Recommended Blocks

Prioritaet A:

SHAPIROINFO11 Correction-State Sidecar Template

Create:

- `data/QSB-ST-SHAPIROINFO/correction_state_sidecar_template.yaml`
- `docs/QSB_ST_SHAPIROINFO11_CORRECTION_STATE_SIDECAR_TEMPLATE_SPEC.md`

Prioritaet B:

SHAPIROINFO12 Public Source and Citation Checklist

Prioritaet C:

SHAPIROINFO13 Targeted Binary Pulsar Dry-Run Adapter Spec

Later:

- Cassini Feasibility Study Plan
- VLBI Feasibility Study Plan

## Push Readiness

- Worktree sollte sauber sein.
- Branch ist lokal mehrere Commits vor `origin/main`.
- Nach diesem Handoff und Abnahme ist `git push` fachlich vertretbar.
- Vor Push empfohlen:
  - `git status --short`
  - `git log --oneline origin/main..HEAD`

Hinweis: Diese Handoff-Datei selbst muss vor einem sauberen Push-Zustand noch
abgenommen und in die lokale Historie aufgenommen werden.

## Acceptance Checks

- Datei existiert
- enthaelt current anchor `26edb9f`
- enthaelt alle 12 Commits
- enthaelt SHAPIROINFO04/05 Funktionstest
- enthaelt `expected_status_check_passed = true`
- enthaelt Correction-State is not metadata decoration
- enthaelt NANOGrav J0740+6620
- enthaelt What has NOT been done
- enthaelt Push readiness
- risk grep clean
- git diff --check clean
- git status --short reported
