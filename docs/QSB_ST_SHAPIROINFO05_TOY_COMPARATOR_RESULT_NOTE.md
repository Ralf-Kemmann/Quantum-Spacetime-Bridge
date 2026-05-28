# QSB-ST-SHAPIROINFO05 — Toy Comparator Result Note

## Current anchor

`f925ddc Add QSB-ST ShapiroInfo toy comparator minimal runner`

## Run source

`runs/QSB-ST-SHAPIROINFO04/toy_comparator_minimal_open/`

Gelesene Run-Dateien:

- `summary.json`
- `toy_comparator_variant_results.csv`
- `toy_comparator_status_summary.csv`
- `readout.md`
- `resolved_config.json`

Builds on:

- `docs/QSB_ST_SHAPIROINFO01_RELATIONAL_DELAY_TO_INFORMATION_RESIDUAL_SPEC.md`
- `docs/QSB_ST_SHAPIROINFO02_MINIMAL_SIGNAL_RECORD_SCHEMA_SPEC.md`
- `docs/QSB_ST_SHAPIROINFO03_TOY_COMPARATOR_PLAN.md`
- `docs/QSB_ST_SHAPIROINFO04_TOY_COMPARATOR_MINIMAL_RUNNER_SPEC.md`
- `scripts/run_qsb_st_shapiroinfo_toy_comparator.py`
- `data/QSB-ST-SHAPIROINFO/toy_comparator_config.yaml`

## Befund

Aus `summary.json`:

- `variant_count = 6`
- `expected_status_check_passed = true`
- `residual_status_counts`:
  - `artifact_likely: 2`
  - `candidate_residual: 1`
  - `inconclusive: 1`
  - `no_residual: 2`
- `warnings`:
  - `comparison_resolution_or_stability_limit`

## Variant-Level Table

| variant_id | residual_status | expected_residual_status | expected_match | warnings | claim_boundary_flag |
|---|---|---|---|---|---|
| `V0_identity_control` | `no_residual` | `no_residual` | `true` |  | `true` |
| `V1_known_delay_only` | `no_residual` | `no_residual` | `true` |  | `true` |
| `V2_known_delay_plus_noise` | `inconclusive` | `no_residual|inconclusive` | `true` | `comparison_resolution_or_stability_limit` | `true` |
| `V3_known_artifact` | `artifact_likely` | `artifact_likely|no_residual` | `true` |  | `true` |
| `V4_hidden_residual_candidate` | `candidate_residual` | `candidate_residual` | `true` |  | `true` |
| `V5_false_positive_control` | `artifact_likely` | `artifact_likely` | `true` |  | `true` |

## Funktionstest-Bewertung

Der Toy-Comparator funktioniert technisch im geplanten Minimalumfang, wenn:

- alle sechs Varianten vorhanden sind,
- `expected_status_check_passed = true` ist,
- `no_residual`, `artifact_likely`, `candidate_residual` und `inconclusive`
  unterscheidbar auftreten,
- `claim_boundary_flag` in den Variantenausgaben nicht verletzt wird.

Diese Bedingungen sind im gelesenen SHAPIROINFO04-Run erfuellt. Die Warnung
`comparison_resolution_or_stability_limit` gehoert zum V2-Fall und markiert
die bewusst schwache Aufloesungs-/Stabilitaetslage dieses Toy-Vergleichs.

## Interpretation

Der Runner prueft nicht Physik, sondern die technische Entscheidungslogik. Er
zeigt, dass die in SHAPIROINFO03 geplanten Zustaende algorithmisch darstellbar
sind: `no_residual`, `artifact_likely`, `candidate_residual` und
`inconclusive` treten im Minimal-Run getrennt auf.

## Hypothese

Der Minimal-Comparator kann als Vorlage fuer spaetere kontrollierte
A/B-Vergleichslaeufe dienen, sofern diese weiter mit klaren Korrekturbudgets,
Kontrollen, Unsicherheiten und Claim Boundaries gefuehrt werden.

## Offene Luecke

- synthetische Toy-Daten
- keine echten Shapiro-Daten
- keine empirische Aussage
- keine physikalische Validierung
- keine Spezifitaetspruefung
- keine Aussage ueber reale Residuen
- Run-Outputs sind aktuell nicht als Repo-Dateien getrackt

## Claim Boundary

- no derivation of c
- no explanation of numerical value of c
- no Bridge confirmation
- no spacetime emergence claim
- no replacement of relativity or quantum mechanics
- no Shapiro modification claim
- no evidence claim from toy run alone

## Next possible blocks

- SHAPIROINFO06 tracked minimal output snapshot
- SHAPIROINFO07 comparator robustness sweep
- SHAPIROINFO08 hostile artifact controls
- INTERFACE04 Lorentz-compatible vocabulary constraints

## Acceptance Checks

- Datei existiert.
- Result note names the actual run directory.
- Includes `expected_status_check_passed = true`.
- Includes all four statuses: `no_residual`, `artifact_likely`,
  `candidate_residual`, `inconclusive`.
- Risk grep clean.
- `git diff --check` clean.
- `git status --short` reported.
