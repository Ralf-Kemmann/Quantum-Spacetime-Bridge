# QSB-ST-SHAPIROINFO07 -- Public Dataset Feasibility Matrix Spec

## Current anchor

`35da881 Add QSB-ST ShapiroInfo data and scenario inventory note`

## Purpose

SHAPIROINFO07 uebersetzt das Inventar aus SHAPIROINFO06 in eine formale
Matrix. Die Matrix soll spaeter helfen, oeffentliche Datenraeume nach Reife,
Risiko, Korrekturlast und Eignung fuer einen vorsichtigen ersten halb-realen
Workflow zu bewerten.

## Source Context

Quelle:

- `docs/QSB_ST_SHAPIROINFO06_DATA_AND_SCENARIO_INVENTORY_NOTE.md`
- `deep-research-report(10).md`

Builds on:

- `docs/QSB_ST_SHAPIROINFO01_RELATIONAL_DELAY_TO_INFORMATION_RESIDUAL_SPEC.md`
- `docs/QSB_ST_SHAPIROINFO02_MINIMAL_SIGNAL_RECORD_SCHEMA_SPEC.md`
- `docs/QSB_ST_SHAPIROINFO03_TOY_COMPARATOR_PLAN.md`
- `docs/QSB_ST_SHAPIROINFO04_TOY_COMPARATOR_MINIMAL_RUNNER_SPEC.md`
- `docs/QSB_ST_SHAPIROINFO05_TOY_COMPARATOR_RESULT_NOTE.md`
- `docs/QSB_ST_SHAPIROINFO06_DATA_AND_SCENARIO_INVENTORY_NOTE.md`

## Scope

- Feasibility specification only
- no data ingestion
- no real-data analysis
- no empirical result
- no Bridge claim
- no Shapiro modification claim
- no claim that any dataset contains a residual

## Bewertungsprinzip

Die Matrix bewertet nicht, ob ein Datensatz interessante Residuen enthaelt.
Sie bewertet nur:

- Ist der Datensatz oeffentlich?
- Ist er dokumentiert?
- Sind Observables klar?
- Sind Korrekturschichten nachvollziehbar?
- Gibt es A/B- oder Kontrollfenster?
- Gibt es zusaetzliche Fingerprint-Kanaele?
- Wie hoch ist der Rekonstruktions- und Artefaktaufwand?
- Ist er fuer einen ersten halb-realen Schritt geeignet?

## Dataset Families Matrix

| dataset_family | example_sources | observable_family | access_level | processing_level | standard_format_availability | correction_state_visibility | a_b_pairing_potential | fingerprint_channel_potential | artifact_risk_level | reconstruction_burden | first_step_suitability | recommended_label | recommended_next_action | boundary_note |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| PTA / Pulsar Timing general releases | NANOGrav, EPTA, PPTA, IPTA, InPTA | TOAs, timing models, residual windows, DM/noise context | public | processed timing products with release-specific modeling layers | high for `.par`/`.tim`-near products | medium to high; depends on release and metadata path | high; pulsar, epoch, band, orbit, or control windows | medium to good; wideband DM, templates, profiles, dynamic spectra where released | medium | medium | high | `public_processed_with_caution` | select small controlled subset | Feasibility only; no dataset-specific evidence claim. |
| Targeted binary pulsar package, e.g. NANOGrav J0740+6620 | NANOGrav J0740+6620 timing package | targeted binary MSP TOAs and timing model | public | processed single-source package | high if `.par`/`.tim` package is complete | medium to high; orbital and timing-model state must be explicit | highest; orbit-phase and off-window controls are plausible | limited to medium; timing strong, auxiliary channels package-dependent | medium | low to medium | highest | `public_processed_ready` | candidate for SHAPIROINFO08 / 09 pilot planning | Best first candidate class, but still no real-data result. |
| NANOGrav 15-year / InPTA small subset | NANOGrav 15-year subset, InPTA small subset | TOAs, timing models, DM series, banded timing context | public | processed release subset | high | medium to high when Clock/DM/Ephemeris/Noise state is retained | high for small, controlled subset | medium to good; especially DM and band controls | medium | medium | high | `public_processed_with_caution` | small subset feasibility, avoid broad ingest first | Keep scope narrow before any broad release handling. |
| EPTA / PPTA / IPTA broader releases | EPTA DR2, PPTA DR3, IPTA DR2 | multi-pulsar timing products and release-level noise context | public | processed but heterogeneous across telescopes/backends/releases | high in broad terms, variable in local details | medium; may require release-specific state reconstruction | medium to high after local pipeline exists | medium to good depending release | medium to high | medium to high | medium | `public_high_heterogeneity` | use after single-source / small-subset pipeline exists | Joint or broad releases can blur correction-state provenance. |
| Cassini SCE1 radio science | Cassini SCE1 RSS, ATDF/TDF, ODF, RSR | Doppler, range, open/closed loop radio science products | public | raw to low-processed archive products | medium; mission formats documented but not simple residual tables | low to medium; correction state requires reconstruction | medium; pass, band, conjunction, and receiver-mode pairing possible | good in RSR/open-loop products | high | high | low for first semi-real step | `public_raw_heavy` | later feasibility study only | Physically relevant, but too reconstruction-heavy for first adapter. |
| Mars Express MaRS / Rosetta RSI | ESA/NASA MaRS and RSI products | Doppler, ranging, tracking, phase/amplitude/polarization where available | public | raw and partly processed mission products | medium | low to medium; mission phase and product level matter | medium | limited to good depending product | high | high | low to medium | `public_raw_heavy` | later comparison path after Cassini/VLBI mapping | Useful comparison path, not first workflow target. |
| VLBI group delay, CDDIS NGS/vgosDB | CDDIS NGS, CDDIS vgosDB | group delay, session, baseline, source, elongation products | public | session/solution-near products | medium to high | medium; provider, edit, atmosphere, and ionosphere state must be explicit | medium; sessions, baselines, source pairs, elongation bins | limited in standard products | high | high | medium to low | `public_qc_heavy` | later QC-heavy feasibility path | Model/QC burden can dominate simple A/B interpretation. |
| Strong lensing time delays | COSMOGRAIL, TDCOSMO-like products | lightcurve delays, lens-model likelihood products | public or partly public by project | processed photometric/lens-model products | medium | low for ShapiroInfo propagation use; different correction stack | low for primary ShapiroInfo A/B | medium for lightcurve-shape vocabulary | high for primary propagation analogy | medium to high | low | `secondary_taxonomy_only` | use only for delay taxonomy / artifact vocabulary | Secondary vocabulary source, not a primary ShapiroInfo pilot. |

## Recommended Labels

- `public_processed_ready`: public, documented, processed enough for a narrow
  pilot, with visible standard formats and manageable correction-state fields.
- `public_processed_with_caution`: public and processed, but still requires
  controlled subset selection and explicit correction-state tracking.
- `public_raw_heavy`: public and relevant, but raw or low-processed enough that
  reconstruction burden dominates first-step suitability.
- `public_high_heterogeneity`: public and processed, but broad release
  heterogeneity makes early interpretation fragile.
- `public_qc_heavy`: public and relevant, but QC/modeling state is central and
  must be mapped before any adapter step.
- `secondary_taxonomy_only`: useful for vocabulary or artifact comparison, not
  for the primary ShapiroInfo pilot.
- `not_first_step`: not suitable as first semi-real workflow target.

## Correction-State Matrix

| correction_layer | relevant_dataset_families | required_state_fields | missing_state_risk | control_requirement |
|---|---|---|---|---|
| GR / Shapiro model state | PTA / Pulsar Timing, targeted binary pulsars, Cassini, MaRS/RSI, VLBI | model family, software/tool convention, fitted vs. fixed terms, geometry variables | standard-model terms could be mistaken for residual structure | compare only within identical or explicitly mapped model state |
| plasma / DM / ISM state | PTA / Pulsar Timing, InPTA/NANOGrav subsets, Cassini, MaRS/RSI | DM model, DM series, band state, plasma correction method, dispersive correction flag | chromatic remnants can mimic structured timing residuals | band controls, DM/null checks, single-band vs. corrected comparisons |
| solar wind state | PTA / Pulsar Timing, Cassini, MaRS/RSI, VLBI near Sun | solar-wind model, solar elongation, epoch window, correction flag | solar-near propagation effects can be over-read | elongation bins and off-solar-window controls |
| troposphere / ionosphere state | Cassini, MaRS/RSI, VLBI, observatory-side timing products | atmosphere model, ionosphere product, weather/radiometer context, station metadata | station or atmosphere effects can dominate residuals | station/baseline controls and QC masks |
| clock correction state | PTA / Pulsar Timing, targeted binary pulsars, VLBI, radio science | clock file/version, observatory clock chain, timescale, applied flag | clock covariance can look like timing structure | rerun or compare under allowed clock-state variants |
| ephemeris state | PTA / Pulsar Timing, targeted binary pulsars, radio science, VLBI | solar-system ephemeris, spacecraft/orbit state, source ephemeris, version | geometry and barycentering differences can shift residuals | fixed-ephemeris comparisons and sensitivity checks |
| source model state | targeted binary pulsars, PTA releases, VLBI, lensing taxonomy | pulsar timing model, binary model, source coordinates, lens/source model where relevant | model mismatch can be assigned to the wrong channel | same-source controls, off-phase windows, source-subset checks |
| instrument / backend state | PTA / Pulsar Timing, Cassini, MaRS/RSI, VLBI | backend ID, receiver mode, band, station, jump parameters, calibration state | hardware changes can create structured offsets | homogeneous backend windows and explicit jump controls |
| noise model state | PTA releases, targeted binary pulsars, VLBI, lensing taxonomy | white/red noise terms, EFAC/EQUAD/ECORR-like state, covariance model, whitening state | uncertainty can be under-read or status labels can drift | evaluate status only with declared noise model |
| QC / flag state | all families | flag source, exclusion logic, quality class, pass/session validity, outlier state | low-quality segments can drive misleading residual status | hard QC gates before candidate language |

## Go / No-Go Logic

### GO_FOR_PILOT

Use this category only when all conditions are plausible:

- public data
- documented standard format
- correction-state visible enough
- manageable artifact burden
- A/B or control pairing plausible
- no raw-heavy reconstruction required

### GO_FOR_FEASIBILITY_ONLY

Use this category when:

- public and relevant
- but heavy reconstruction or correction burden
- suitable for later study, not first semi-real adapter

### HOLD_AS_TAXONOMY_ONLY

Use this category when:

- useful for vocabulary / artifact comparison
- not suitable for primary ShapiroInfo pilot

### NO_GO_FOR_NOW

Use this category when one or more hard blockers apply:

- data inaccessible
- correction-state opaque
- no plausible controls
- too high risk of misleading residuals

## First Pilot Recommendation

Der sicherste erste halb-reale Kandidat bleibt:

- targeted binary pulsar package such as NANOGrav J0740+6620
- oder kleines NANOGrav/InPTA-Subset

Nicht zuerst:

- Cassini
- VLBI
- Lensing

## Relation To SHAPIROINFO08

SHAPIROINFO08 sollte erst nach dieser Matrix ein enger Toy-to-Semi-Real
Adapter Plan werden. Der Adapter sollte zunaechst nur `.par`/`.tim`-nahe
Timingdaten und Correction-State-Metadaten abbilden. Keine breite
Datenaufnahme.

## Befund

Die Datenraeume sind unterschiedlich reif. PTA/Pulsar-Timing ist am
geeignetsten fuer den ersten halb-realen Schritt. Cassini und VLBI bleiben
wichtig, aber spaeter. Correction-State entscheidet ueber Interpretierbarkeit.

## Interpretation

Die Feasibility-Matrix dient als Claim-Bremse und Datenauswahl-Gelaender. Sie
soll vermeiden, dass ikonische, aber schwer rekonstruierbare Datenraeume zu
frueh gewaehlt werden.

## Hypothese

Ein kleiner, kontrollierter Pulsar-Timing-Pilot koennte spaeter die sicherste
Bruecke vom synthetischen Toy-Comparator zu einem halb-realen Workflow bilden.

## Offene Luecke

- keine Daten geladen
- keine konkrete Quelle ausgewaehlt
- keine Feasibility-Werte empirisch geprueft
- keine Downloadentscheidung
- keine PINT/tempo2-Integration
- keine Realanalyse
- keine Residualsuche

## Claim Boundary

- no Bridge confirmation
- no physical validation
- no new Shapiro effect claim
- no claim that GR is incomplete
- no claim that any residual implies QSB-ST
- no dataset-specific evidence claim
- no real-data result
- no ranking as scientific truth; only workflow feasibility ranking

## Next Possible Blocks

- SHAPIROINFO08 Toy-to-Semi-Real Adapter Plan
- SHAPIROINFO09 Targeted Binary Pulsar Pilot Plan
- SHAPIROINFO10 Correction-State Field Schema
- SHAPIROINFO11 Cassini Feasibility Study Plan
- SHAPIROINFO12 VLBI Feasibility Study Plan

## Acceptance Checks

- Datei existiert.
- Enthaelt `public_processed_ready`.
- Enthaelt `public_raw_heavy`.
- Enthaelt `secondary_taxonomy_only`.
- Enthaelt `GO_FOR_PILOT`.
- Enthaelt `GO_FOR_FEASIBILITY_ONLY`.
- Enthaelt Correction-State.
- Enthaelt J0740+6620.
- Enthaelt Cassini.
- Enthaelt VLBI.
- Risk grep clean.
- `git diff --check` clean.
- `git status --short` reported.
