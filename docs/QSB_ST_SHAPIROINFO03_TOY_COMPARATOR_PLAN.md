# QSB-ST-SHAPIROINFO03 — Toy Comparator Plan

## Purpose

Plan fuer einen minimalen synthetischen A/B-Comparator zur spaeteren Pruefung
der ShapiroInfo-Residual-Logik. Ein synthetischer Signalvergleich soll nur
testen, ob die Residual-Entscheidungslogik technisch formulierbar ist.

Current anchor:

- `da8263f Add QSB-ST ShapiroInfo minimal signal record schema`

Builds on:

- `docs/QSB_ST_INTERFACE03_RT_QM_CAUSALITY_ROSETTA_TRANSLATOR_SPEC.md`
- `docs/QSB_ST_SHAPIROINFO01_RELATIONAL_DELAY_TO_INFORMATION_RESIDUAL_SPEC.md`
- `docs/QSB_ST_SHAPIROINFO02_MINIMAL_SIGNAL_RECORD_SCHEMA_SPEC.md`
- `docs/QSB_ST_INTERFACE_SHAPIROINFO_RESULT_READOUT_2026_05_28.md`

## Scope

- toy plan only
- no real Shapiro data
- no empirical claim
- no physical validation
- no modification of standard Shapiro delay
- no Bridge confirmation

## Minimalmodell

```text
A_reference = baseline synthetic signal

B_influenced = A_reference
             + known_delay_component
             + optional_standard_artifact
             + optional_candidate_residual

corrected_B = B_influenced
            - known_delay_component
            - known_standard_artifacts
```

## Input Model

Minimale synthetische Signalpaare koennen spaeter in vier kleinen Toy-Klassen
gedacht werden. Sie bleiben kuenstlich und dienen nur der technischen
Unterscheidung von Statuswoertern.

- `timing-only toy`: vergleicht Ankunftszeiten, Korrekturen,
  Unsicherheiten und `residual_timing_s`.
- `phase toy`: vergleicht Phasenlage, Phasenunsicherheit und
  `residual_phase_rad`.
- `frequency toy`: vergleicht Frequenzverschiebung, Frequenzunsicherheit und
  `residual_frequency_hz`.
- `modulation/fingerprint toy`: vergleicht einfache Fingerprint-Werte und
  `residual_fingerprint_score`.

## Required Toy Variants

| variant_id | variant_name | A_definition | B_definition | correction_applied | expected_residual_status | purpose |
|---|---|---|---|---|---|---|
| `V0_identity_control` | Identity control | `B = A` baseline reference | `B = A` | none | `no_residual` | Prueft, ob der Comparator eine identische Paarung ruhig laesst. |
| `V1_known_delay_only` | Known delay only | baseline reference | `B = A + known_delay` | correction removes delay | `no_residual` | Prueft, ob bekannte Verzoegerung nach Korrektur nicht als Residual erscheint. |
| `V2_known_delay_plus_noise` | Known delay plus bounded noise | baseline reference | `B = A + known_delay + bounded_noise` | delay correction plus uncertainty budget | `no_residual` or `inconclusive` depending threshold | Prueft, ob Unsicherheit die Entscheidung kontrolliert. |
| `V3_known_artifact` | Known standard artifact | baseline reference | `B = A + known_delay + standard_artifact` | delay correction plus artifact handling | `artifact_likely` or `no_residual` after correction | Prueft, ob erklaerbare Artefakte Kandidatensprache blockieren. |
| `V4_hidden_residual_candidate` | Hidden residual candidate | baseline reference | `B = A + known_delay + candidate_residual_pattern` | delay correction; controls fail to explain residual | `candidate_residual` | Prueft, ob ein reproduzierbares, nicht durch Kontrollen erklaertes Muster technisch markiert werden kann. |
| `V5_false_positive_control` | False positive control | baseline reference | `B = A + noise/artifact that mimics residual` | artifact/noise control path | `artifact_likely`, not `candidate_residual` | Prueft, ob ein scheinbares Muster durch Kontrollen abgefangen wird. |

## Minimal Observables

- `residual_timing_s`
- `residual_phase_rad`
- `residual_frequency_hz`
- `residual_fingerprint_score`
- `uncertainty_budget`
- `correction_budget_summary`
- `residual_status`

## Comparator Decision Rules

- If `corrected_B` approximately equals `A_reference` within uncertainty:
  `residual_status = no_residual`.
- If `corrected_B` differs from `A_reference` beyond uncertainty, but an
  artifact or control explains the difference:
  `residual_status = artifact_likely`.
- If `corrected_B` differs reproducibly beyond uncertainty and controls:
  `residual_status = candidate_residual`.
- If resolution is insufficient or comparison stability is weak:
  `residual_status = inconclusive`.

Zusatzregeln:

- Tolerance thresholds are toy parameters.
- Uncertainty dominates decisions.
- Controls override candidate language.
- `candidate_residual` requires reproducibility and control failure.
- `candidate_residual` is only a technical diagnostic state.
- `candidate_residual` is not physical validation.

## Connection to INTERFACE03

- c as Rosetta candidate remains vocabulary/interface context only.
- no derivation of c
- no explanation of numerical value of c
- timing/frequency/phase relations may be useful comparator coordinates

## Connection to SHAPIROINFO01

- Standard Shapiro correction remains known-correction layer.
- Residual search begins only after standard correction layers.
- no claim that Shapiro physics is changed

## Connection to SHAPIROINFO02

- Use the minimal signal record fields as future schema target.
- Do not create data yet.
- Do not create scripts yet.

## Befund

The project has a plan-level toy comparator route.

## Interpretation

The comparator can later test whether the residual logic is technically
coherent.

## Hypothese

A controlled synthetic comparator may help distinguish `no_residual`,
`artifact_likely`, `inconclusive`, and `candidate_residual` states.

## Offene Luecke

No implementation, no data, no empirical test, no physical validation.

## Claim Boundary

- no derivation of c
- no explanation of the numerical value of c
- no Bridge confirmation
- no spacetime emergence claim
- no replacement of relativity or quantum mechanics
- no Shapiro modification claim
- no evidence claim from toy planning alone

## Future Implementation Boundary

A later SHAPIROINFO04 may create:

- `data/QSB-ST-SHAPIROINFO/toy_comparator_config.yaml`
- `scripts/run_qsb_st_shapiroinfo_toy_comparator.py`
- `runs/QSB-ST-SHAPIROINFO03 or 04 outputs`

But SHAPIROINFO03 creates none of these.

## Acceptance Checks

- Datei existiert.
- Variant table contains V0 through V5.
- Risk grep clean.
- `git diff --check` clean.
- `git status --short` reported.
