# QSB-ST-SHAPIROINFO12 -- Public Source and Citation Checklist

## Current anchor

`b98f258 Add QSB-ST ShapiroInfo correction-state sidecar template`

## Purpose

SHAPIROINFO12 legt fest, welche Quellen-, Zitier-, Release-, Datei- und
Nutzungsinformationen vor einem spaeteren Targeted-Binary-Pulsar-Pilot sichtbar
sein muessen.

Das Ziel ist ein vorgelagertes Gate vor jedem halb-realen Datensatzkontakt.
Der Kandidat darf erst in einen konkreten Correction-State-Sidecar-Draft
ueberfuehrt werden, wenn Quelle, Zitation, Release-Identitaet, Dateierwartung
und Nutzungsnotiz nachvollziehbar dokumentiert sind.

## Source Context

Builds on:

- `docs/QSB_ST_SHAPIROINFO10_CORRECTION_STATE_FIELD_SCHEMA.md`
- `docs/QSB_ST_SHAPIROINFO11_CORRECTION_STATE_SIDECAR_TEMPLATE_SPEC.md`
- `docs/QSB_ST_SHAPIROINFO09_TARGETED_BINARY_PULSAR_PILOT_PLAN.md`
- `docs/QSB_ST_SHAPIROINFO08_TOY_TO_SEMI_REAL_ADAPTER_PLAN.md`
- `docs/QSB_ST_SHAPIROINFO02_MINIMAL_SIGNAL_RECORD_SCHEMA_SPEC.md`

## Scope

- checklist specification only
- no download
- no dataset ingestion
- no `.par` / `.tim` parsing
- no PINT / tempo2 execution
- no residual calculation
- no real-data result
- no Bridge claim
- no Shapiro modification claim

## Gate Principle

A dataset candidate is not allowed into the Correction-State sidecar unless its
public source, citation path, file expectations, release identity, and data-use
notes are explicit enough for reproducible handling.

Der Tuersteher prueft nicht, ob die Daten interessant sind. Er prueft nur, ob
die Daten sauber, zitierbar und nachvollziehbar in den Maschinenraum duerfen.

## Candidate Class

Bevorzugter erster Kandidatenraum:

- targeted binary pulsar package
- example: NANOGrav J0740+6620

Noch keine Entscheidung fuer konkreten Download.

## Checklist Table

| checklist_item | required_level | expected_evidence | allowed_status | blocking_if_missing | notes |
|---|---|---|---|---|---|
| `source_page_url` | required_blocking | Oeffentliche Release-, Projekt- oder Datensatzseite. | `known_documented`, `known_but_needs_review`, `unknown`, `manual_review_required`, `blocking_missing` | yes | Keine URL erfinden; ohne Quelle kein Datensatzkontakt. |
| `dataset_or_release_name` | required_blocking | Name des Kandidatenpakets oder Release-Kontexts. | `known_documented`, `known_but_needs_review`, `unknown`, `manual_review_required`, `blocking_missing` | yes | Muss enger sein als ein breiter Multi-Release-Ingest. |
| `release_version_or_date` | required_blocking | Release-Version, Release-Datum oder eindeutig benannter Stand. | `known_documented`, `known_but_needs_review`, `unknown`, `manual_review_required`, `blocking_missing` | yes | Version/Datum darf nicht implizit bleiben. |
| `citation_reference` | required_blocking | Paper, Release-Zitation, BibTeX-Key oder zitierbarer Hinweis. | `known_documented`, `known_but_needs_review`, `unknown`, `manual_review_required`, `blocking_missing` | yes | Ohne Zitation kein Sidecar-Draft. |
| `doi_or_stable_identifier` | required_if_available | DOI, Zenodo-ID, release tag, repository commit, dataset id oder not_available. | `known_documented`, `known_but_needs_review`, `not_available`, `unknown`, `manual_review_required` | yes if available but unclear | Nicht erfinden; `not_available` ist erlaubt, wenn geprueft. |
| `data_access_method` | required_blocking | Download-Seite, repository release, archive entry, request path oder dokumentierte Zugriffsmethode. | `known_documented`, `known_but_needs_review`, `unknown`, `manual_review_required`, `blocking_missing` | yes | Kein Download vor Gate-Pass. |
| `data_use_or_license_note` | required_blocking | Lizenz-, Nutzungs-, Zitations- oder Datenverwendungsnotiz. | `known_documented`, `known_but_needs_review`, `unknown`, `manual_review_required`, `blocking_missing` | yes | Unklare Nutzung blockiert. |
| `expected_timing_model_file` | required_blocking | Erwartete `.par`-Datei oder aequivalente Timingmodell-Datei. | `known_documented`, `known_but_needs_review`, `unknown`, `not_available`, `manual_review_required`, `blocking_missing` | yes | Praesenz wird hier nicht behauptet; nur Erwartung dokumentieren. |
| `expected_timing_observation_file` | required_blocking | Erwartete `.tim`-Datei oder aequivalente TOA-/Timing-Beobachtungsdatei. | `known_documented`, `known_but_needs_review`, `unknown`, `not_available`, `manual_review_required`, `blocking_missing` | yes | Ohne `.tim` oder aequivalenten Pfad kein Pulsar-Pilot. |
| `expected_readme_or_release_notes` | required_blocking | README, release notes, paper appendix oder Datensatzdokumentation. | `known_documented`, `known_but_needs_review`, `unknown`, `not_available`, `manual_review_required`, `blocking_missing` | yes | Dokumentation muss Modell- und Nutzungskontext tragen. |
| `expected_clock_or_ephemeris_context` | required_blocking | Hinweise zu Clock, Timescale, Ephemeride oder Baryzentrierung. | `known_documented`, `known_but_needs_review`, `unknown`, `not_available`, `manual_review_required`, `blocking_missing` | yes | Uhren-/Ephemeriden-Unknown blockiert spaeteren Sidecar. |
| `expected_noise_or_correction_context` | required_blocking | Noise-, DM/ISM-, Backend-, Instrument- oder Korrekturkontext. | `known_documented`, `known_but_needs_review`, `unknown`, `not_available`, `manual_review_required`, `blocking_missing` | yes | Korrekturkontext ist Gate-Material, kein Ergebnis. |
| `file_format_expectation` | required_blocking | Erwartete Formate, z. B. `.par`, `.tim`, README, YAML/JSON sidecar. | `known_documented`, `known_but_needs_review`, `unknown`, `manual_review_required`, `blocking_missing` | yes | Formatannahmen muessen sichtbar sein. |
| `local_storage_plan` | required_blocking | Geplanter lokaler Pfad und Nicht-Ueberschreib-Regel fuer spaetere Daten. | `known_documented`, `known_but_needs_review`, `unknown`, `manual_review_required`, `blocking_missing` | yes before download | In SHAPIROINFO12 wird noch kein Pfad befuellt. |
| `checksum_or_integrity_plan` | required_blocking | Geplante Checksummen, Datei-Groessen oder Integritaetsnotizen. | `known_documented`, `known_but_needs_review`, `unknown`, `manual_review_required`, `blocking_missing` | yes before download | Integritaet muss vor tracked data use geplant sein. |
| `provenance_manifest_required` | required_blocking | Entscheidung, dass ein spaeteres Provenance-Manifest Pflicht ist. | `known_documented`, `manual_review_required`, `blocking_missing` | yes | Muss fuer jeden halb-realen Kontakt true/required sein. |
| `correction_state_sidecar_required` | required_blocking | Entscheidung, dass der Correction-State-Sidecar Pflicht ist. | `known_documented`, `manual_review_required`, `blocking_missing` | yes | Kein Adapterlauf ohne Sidecar. |
| `window_definition_sidecar_required` | required_blocking | Entscheidung, dass A/B-/Kontrollfenster als Sidecar geplant werden. | `known_documented`, `manual_review_required`, `blocking_missing` | yes | Ohne Kontrollfenster kein Vergleich. |
| `manual_review_required_before_download` | required_blocking | Explizite manuelle Review-Grenze vor Download. | `known_documented`, `manual_review_required`, `blocking_missing` | yes | Menschlicher Gate-Check vor jedem Datensatzkontakt. |
| `no_download_until_gate_passed` | required_blocking | Explizite Sperre gegen Download vor Gate-Pass. | `known_documented`, `manual_review_required`, `blocking_missing` | yes | Muss sichtbar bleiben, bis alle Blocker geklaert sind. |

## Allowed Checklist Statuses

- `known_documented`
- `known_but_needs_review`
- `unknown`
- `not_applicable`
- `not_available`
- `manual_review_required`
- `blocking_missing`
- `ready_for_sidecar_draft`

## Blocking Logic

`GO_TO_SIDECAR_DRAFT` nur wenn:

- `source_page_url` `known_documented`
- `citation_reference` `known_documented`
- release identity `known_documented`
- data access method `known_documented`
- expected `.par` / `.tim` or equivalent files identified
- data-use note checked
- provenance manifest planned
- correction-state sidecar required
- manual review completed

`BLOCKED_BEFORE_DOWNLOAD` wenn:

- source URL unclear
- citation missing
- release version unclear
- data-use/citation unclear
- expected files unclear
- broad release required instead of targeted package
- local storage/provenance plan missing

## Candidate Prefill: NANOGrav J0740+6620

Diese Prefill-Sektion ist kein Download-Plan und keine lokale Quellenpruefung.
Sie markiert nur den bevorzugten Kandidatenraum aus SHAPIROINFO09. Keine URL,
kein DOI und keine Dateipraesenz werden behauptet.

| field | prefill_value | status | note |
|---|---|---|---|
| candidate_label | NANOGrav J0740+6620 | manual_review_required | Prefill-Kandidatenlabel aus dem Pilotplan, noch keine lokale Quellenpruefung. |
| source_page_url | manual_review_required | manual_review_required | Keine URL erfunden. |
| dataset_or_release_name | unknown | manual_review_required | Muss durch oeffentliche Quelle belegt werden. |
| release_version_or_date | unknown | manual_review_required | Muss vor Sidecar-Draft sichtbar sein. |
| citation_reference | manual_review_required | manual_review_required | Keine Zitation erfunden. |
| doi_or_stable_identifier | unknown | manual_review_required | DOI oder stabiler Identifier erst nach Review. |
| data_access_method | unknown | manual_review_required | Kein Download, keine Zugriffsmethode geprueft. |
| data_use_or_license_note | manual_review_required | manual_review_required | Nutzungsnotiz offen. |
| expected_timing_model_file | unknown | manual_review_required | `.par`-Erwartung noch nicht lokal geprueft. |
| expected_timing_observation_file | unknown | manual_review_required | `.tim`-Erwartung noch nicht lokal geprueft. |
| expected_readme_or_release_notes | unknown | manual_review_required | Release-Dokumentation noch nicht geprueft. |
| expected_clock_or_ephemeris_context | unknown | manual_review_required | Clock-/Ephemeridenkontext offen. |
| expected_noise_or_correction_context | unknown | manual_review_required | Noise-/Correction-Kontext offen. |
| file_format_expectation | unknown | manual_review_required | Keine Dateiformate als geprueft markieren. |
| local_storage_plan | manual_review_required | manual_review_required | Erst spaeterer Manifest-/Storage-Block. |
| checksum_or_integrity_plan | manual_review_required | manual_review_required | Erst vor echtem Datensatzkontakt befuellen. |
| provenance_manifest_required | true | manual_review_required | Pflichtkonzept, aber noch kein Manifest. |
| correction_state_sidecar_required | true | manual_review_required | Pflichtkonzept aus SHAPIROINFO10/11. |
| window_definition_sidecar_required | true | manual_review_required | Pflicht fuer spaetere A/B-/Kontrollfenster. |
| manual_review_required_before_download | true | manual_review_required | Download bleibt gesperrt. |
| no_download_until_gate_passed | true | manual_review_required | Gate muss zuerst bestanden werden. |

## Relation To SHAPIROINFO11

SHAPIROINFO11 erzeugte das Correction-State-Sidecar-Template. SHAPIROINFO12
entscheidet, ob ein Kandidat sauber genug ist, um in einen konkreten
Sidecar-Draft ueberfuehrt zu werden.

## Relation To SHAPIROINFO09

SHAPIROINFO09 plante den targeted binary pulsar pilot. SHAPIROINFO12 ist das
Quellen-/Zitiergate vor diesem Pilot.

## Befund

Der ShapiroInfo-Pfad hat nun ein vorgelagertes Quellen- und Zitationsgate vor
jedem halb-realen Datensatzkontakt.

## Interpretation

Dieses Gate trennt die Frage nach Quellenhygiene von der Frage nach
Dateninteresse. Ein Kandidat darf erst dann in den Sidecar-Maschinenraum, wenn
Quelle, Zitation, Release-Stand, Dateierwartung, Nutzungsnotiz und
Provenance-Plan sichtbar sind.

## Hypothese

Ein hartes Quellen-/Zitiergate kann spaetere Korrektur- und
Interpretationsrisiken reduzieren, weil unklare Herkunft, unklare Nutzung und
unklare Dateierwartungen vor jedem Datenkontakt blockieren.

## Offene Luecke

- no source URL reviewed
- no citation reviewed
- no DOI or stable identifier checked
- no data-use note checked
- no dataset selected for download
- no `.par` / `.tim` files inspected
- no provenance manifest created
- no candidate sidecar draft created
- no PINT / tempo2 run
- no residual calculation
- no empirical result

## Claim Boundary

- no Bridge confirmation
- no physical validation
- no new Shapiro effect claim
- no claim that GR is incomplete
- no claim that any residual implies QSB-ST
- no dataset-specific evidence claim
- no real-data result
- no candidate residual claim from source checklist
- no derivation of c
- no explanation of the numerical value of c

## Next Possible Blocks

- SHAPIROINFO13 Candidate Source Review for J0740+6620
- SHAPIROINFO14 Correction-State Sidecar Draft for Manual Review Only
- SHAPIROINFO15 Targeted Binary Pulsar Dry-Run Adapter Spec
- SHAPIROINFO16 Public Source Download Manifest Template
- SHAPIROINFO17 Cassini Feasibility Study Plan

## Acceptance Checks

- Datei existiert
- enthaelt source_page_url
- enthaelt citation_reference
- enthaelt expected_timing_model_file
- enthaelt expected_timing_observation_file
- enthaelt GO_TO_SIDECAR_DRAFT
- enthaelt BLOCKED_BEFORE_DOWNLOAD
- enthaelt NANOGrav J0740+6620
- enthaelt manual_review_required
- enthaelt no_download_until_gate_passed
- enthaelt no Bridge confirmation
- risk grep clean
- git diff --check clean
- git status --short reported
