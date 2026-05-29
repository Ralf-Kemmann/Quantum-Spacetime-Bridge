# QSB-ST-SHAPIROINFO10 -- Correction-State Field Schema

## Current anchor

`363720a Add QSB-ST ShapiroInfo targeted binary pulsar pilot plan`

## Purpose

SHAPIROINFO10 legt das Correction-State-Feldschema fest. Der Correction-State
ist ein Pflicht-Sidecar fuer spaetere halb-reale Adapter, insbesondere fuer
Pulsar-Timing-Daten mit `.par`/`.tim`-nahen Eingaben.

Dieses Schema beschreibt, welche Korrektur-, Modell-, Provenance-, Instrument-
und QC-Zustaende dokumentiert sein muessen, bevor ein Datensatz in einen
Adapter oder Vergleichslauf darf.

## Source Context

Builds on:

- `docs/QSB_ST_SHAPIROINFO02_MINIMAL_SIGNAL_RECORD_SCHEMA_SPEC.md`
- `docs/QSB_ST_SHAPIROINFO07_PUBLIC_DATASET_FEASIBILITY_MATRIX_SPEC.md`
- `docs/QSB_ST_SHAPIROINFO08_TOY_TO_SEMI_REAL_ADAPTER_PLAN.md`
- `docs/QSB_ST_SHAPIROINFO09_TARGETED_BINARY_PULSAR_PILOT_PLAN.md`

## Scope

- schema specification only
- no data download
- no ingestion
- no parsing
- no PINT / tempo2 execution
- no residual calculation
- no empirical result
- no Bridge claim
- no Shapiro modification claim

## Grundregel

Kein halb-realer Datensatz darf in SHAPIROINFO09/11/Adapter-Schritte, wenn
zentrale Correction-State-Felder unbekannt, geraten oder nur implizit sind.

Correction-State is not metadata decoration.
Correction-State is a blocking interpretability layer.

## Sidecar Target

Zukuenftige Datei, noch nicht erstellen:

`data/QSB-ST-SHAPIROINFO/correction_state_sidecar_template.yaml`

Diese Datei wird erst in einem spaeteren Block erzeugt. SHAPIROINFO10
spezifiziert nur die Felder.

## Field-List Format

Die Feldliste ist eine durchgehende Schema-Liste. Jede Zeile verwendet diese
Spalten:

- `field_name`
- `field_type`
- `required_level`
- `allowed_values_or_format`
- `field_description`
- `blocking_if_missing`
- `source_hint`
- `claim_risk_note`

## Required Levels

- `required_blocking`: ohne Feld kein halb-realer Adapterlauf.
- `required_if_applicable`: Pflicht, sobald diese Korrekturschicht fuer den
  Datensatz relevant ist.
- `optional_documentary`: hilfreich, aber kein harter Blocker.
- `unavailable_marked`: darf fehlen, muss aber explizit als `unavailable`,
  `not_applicable` oder `unknown` markiert werden.

## Continuous Field List

| field_name | field_type | required_level | allowed_values_or_format | field_description | blocking_if_missing | source_hint | claim_risk_note |
|---|---|---|---|---|---|---|---|
| `correction_state_schema_version` | string | required_blocking | semantic version or pinned schema label | Version des Correction-State-Schemas. | yes | SHAPIROINFO10 schema label | Versionierung ist Audit-Hilfe, kein Ergebnis. |
| `correction_state_record_id` | string | required_blocking | stable unique sidecar id | Stabiler Identifier fuer den Sidecar-Datensatz. | yes | sidecar authoring context | Identitaetsfeld ohne Evidenzgehalt. |
| `dataset_family` | string | required_blocking | controlled family label | Datensatzfamilie, z. B. targeted binary pulsar pilot. | yes | release docs / pilot plan | Familienlabel ist kein Befund. |
| `dataset_name` | string | required_blocking | dataset or source package name | Name des Datensatzes oder Kandidatenpakets. | yes | release docs / provenance manifest | Name allein traegt keine Validierung. |
| `dataset_version` | string | required_blocking | release version, tag, or explicit unknown marker | Release- oder Versionsstand des Datensatzes. | yes | release docs / README | Unklare Version blockiert Reproduzierbarkeit. |
| `source_url` | string | required_blocking | URL string | Oeffentliche Quelle fuer Datensatz oder Release-Seite. | yes | provenance manifest | URL ist Provenance, keine Datenaussage. |
| `citation_reference` | string | required_blocking | citation text, DOI, BibTeX key, or release citation | Zitierbare Referenz fuer Quelle und Kontext. | yes | paper / release page / README | Ohne Zitation kein auditierbarer Pilot. |
| `retrieval_date_utc` | string | required_blocking | ISO 8601 UTC date or datetime | Dokumentiertes Abrufdatum spaeterer lokaler Daten. | yes | provenance manifest | Datum ist Traceability, kein Ergebnis. |
| `local_file_manifest_id` | string | required_blocking | manifest id or explicit not_created_yet marker | Verweis auf spaeteres lokales Dateimanifest mit `.par`/`.tim`-Nahe. | yes before data use | provenance manifest | Manifest ersetzt keine Korrekturpruefung. |
| `provenance_notes` | string | required_blocking | free text, may be `none` if reviewed | Hinweise zu Quelle, Release-Kontext und lokalen Grenzen. | yes | release docs / human review | Notizen duerfen keine fehlenden Felder ueberdecken. |
| `data_use_note` | string | required_blocking | license/data-use note or explicit unclear marker | Datennutzungs- und Lizenzkontext. | yes | release docs / repository notice | Unklare Nutzung blockiert Pilotpfad. |
| `created_by` | string | required_blocking | person/tool id | Autor oder lokaler Ersteller des Sidecars. | yes | local authoring context | Autorenschaft ist Audit-Spur. |
| `created_date_utc` | string | required_blocking | ISO 8601 UTC date or datetime | Erstellungsdatum des Sidecars. | yes | local authoring context | Zeitstempel ist kein Analysezeitpunkt. |
| `review_status` | enum | required_blocking | `planned`, `manual_review_required`, `known_documented`, `blocked` | Review-Zustand des Sidecars. | yes | human review | Review-Label darf keine inhaltliche Pruefung vortaeuschen. |
| `review_notes` | string | optional_documentary | free text, may be `none` | Zusatznotizen zum Review. | no | human review | Notizen bleiben Nebenkanal, nicht Gate-Ersatz. |
| `timing_model_file_present` | boolean/status | required_blocking | `true`, `false`, `unknown` | Sichtbarkeit einer `.par`-nahen Timingmodell-Datei. | yes | file manifest / release docs | Ohne Timingmodell kein halb-realer Pulsar-Pilot. |
| `timing_model_file_name` | string | required_if_applicable | filename or explicit unavailable marker | Dateiname der Timingmodell-Datei. | yes if file present | file manifest | Dateiname zertifiziert keinen Modellinhalt. |
| `timing_model_format` | enum/string | required_blocking | `.par`, equivalent format, `unknown` | Format des Timingmodells. | yes | file manifest / release docs | Format darf nicht geraten werden. |
| `timing_model_software_context` | string | required_if_applicable | PINT, tempo2, TEMPO, release-specific, or unknown | Software-/Konventionskontext des Timingmodells. | yes if relevant | release docs / `.par` comments | Kein PINT/tempo2-Lauf wird hier ausgefuehrt. |
| `timing_model_version_or_release` | string | required_blocking | release tag, model version, or explicit unknown marker | Versions- oder Releasebezug des Timingmodells. | yes | release docs | Unklarer Modellstand blockiert Vergleich. |
| `timing_model_parameter_state` | enum | required_blocking | allowed status vocabulary | Zustand der sichtbaren Timingmodellparameter. | yes | `.par` / release docs | Parameterzustand ist Kontrollmaterial, kein Fit-Befund. |
| `timing_model_fit_state` | enum | required_blocking | allowed status vocabulary | Sichtbarkeit des Fit- oder Freeze-Zustands. | yes | release docs / timing model notes | Fit-Zustand darf nicht implizit bleiben. |
| `timing_model_notes` | string | optional_documentary | free text, may be `none` | Zusatznotizen zum Timingmodell. | no | sidecar review | Notizen duerfen keine unbekannten Modellfelder heilen. |
| `binary_model_present` | boolean/status | required_blocking | `true`, `false`, `not_applicable`, `unknown` | Gibt an, ob ein Binary-Modell fuer den Kandidaten vorliegt. | yes for binary pilot | `.par` / release docs | Fuer Binary-Pilot ist unknown ein Blocker. |
| `binary_model_name` | string | required_if_applicable | model name, e.g. DD/ELL1-like label, or unknown | Name oder Klasse des Binary-Modells. | yes if binary model present | `.par` / release docs | Modellname ist keine Aussage ueber neue Physik. |
| `binary_model_parameter_state` | enum | required_if_applicable | allowed status vocabulary | Dokumentationszustand der Binary-Parameter. | yes if binary model present | `.par` / release docs | Parameterluecken blockieren Fensterdeutung. |
| `binary_model_shapiro_terms_present` | boolean/status | required_if_applicable | `true`, `false`, `not_applicable`, `unknown` | Sichtbarkeit Shapiro-naher Modellterme im Binary-Kontext. | yes if binary pilot | `.par` / release docs | Praesenz ist keine Shapiro-Modifikationsaussage. |
| `binary_model_shapiro_terms_state` | enum | required_if_applicable | allowed status vocabulary | Dokumentationszustand Shapiro-naher Terme. | yes if terms relevant | `.par` / release docs | Zustand dient der Baseline-Kontrolle. |
| `binary_model_orbital_phase_available` | boolean/status | required_if_applicable | `true`, `false`, `planned`, `unknown` | Sichtbarkeit einer spaeter nutzbaren Orbitalphaseninformation. | yes if windows use orbital phase | `.par`, `.tim`, release docs | Phasenfenster bleiben technische Vergleichsfenster. |
| `binary_model_notes` | string | optional_documentary | free text, may be `none` | Zusatznotizen zum Binary-Modell. | no | sidecar review | Notizen ersetzen keine expliziten Modellfelder. |
| `clock_correction_state` | enum | required_blocking | allowed status vocabulary | Gesamtzustand der Uhrenkorrektur. | yes | release docs / clock notes | Opaque clock state blockiert Pilotvergleich. |
| `clock_file_present` | boolean/status | required_if_applicable | `true`, `false`, `not_applicable`, `unknown` | Sichtbarkeit separater Clock-Dateien oder Clock-Produkte. | yes if required by release | release docs / file manifest | Fehlende Clock-Datei kann nur dokumentiert, nicht geraten werden. |
| `clock_file_name` | string | required_if_applicable | filename or explicit not_applicable marker | Dateiname der Clock-Datei, falls vorhanden. | yes if clock file present | file manifest | Dateiname ist kein Anwendungsnachweis. |
| `clock_timescale` | string | required_blocking | TT, TDB, UTC, TAI, release-specific, or unknown | Zeitstandard oder Timescale-Kontext. | yes | `.par`, `.tim`, release docs | Unklare Timescale ist ein harter Blocker. |
| `clock_version_or_release` | string | required_blocking | version, release label, or unknown | Version oder Releasebezug der Clock-Korrektur. | yes | release docs | Version darf nicht stillschweigend angenommen werden. |
| `clock_application_state` | enum | required_blocking | `applied`, `not_applied`, `partially_applied`, `unknown` | Ob und wie Clock-Korrekturen angewendet wurden. | yes | release docs / processing notes | Anwendung ist Korrekturzustand, kein Analyseergebnis. |
| `clock_notes` | string | optional_documentary | free text, may be `none` | Zusatznotizen zu Clock-Kontext und Unsicherheit. | no | sidecar review | Notizen duerfen Unknown nicht verdecken. |
| `ephemeris_state` | enum | required_blocking | allowed status vocabulary | Gesamtzustand der Ephemerideninformation. | yes | `.par` / release docs | Opaque Ephemeriden blockieren. |
| `solar_system_ephemeris_name` | string | required_blocking | ephemeris name or unknown | Name der Solar-System-Ephemeride. | yes | `.par` / release docs | Name ist Baseline-Kontext, kein Resultat. |
| `ephemeris_version` | string | required_blocking | version/release or unknown | Versionsstand der Ephemeride. | yes | `.par` / release docs | Versionsluecke blockiert Reproduzierbarkeit. |
| `barycentering_state` | enum | required_blocking | allowed status vocabulary | Zustand der Baryzentrierungsinformation. | yes | `.par`, `.tim`, release docs | Baryzentrierung darf nicht implizit bleiben. |
| `observatory_position_state` | enum | required_blocking | allowed status vocabulary | Zustand der Observatoriumspositionsinformation. | yes | `.tim` flags / release docs | Positionszustand ist Timing-Baseline. |
| `spacecraft_or_orbit_state` | enum | required_if_applicable | allowed status vocabulary | Zustand von Spacecraft-/Orbit-Information, falls relevant. | yes if applicable | release docs | Nicht anwendbar muss markiert werden. |
| `ephemeris_notes` | string | optional_documentary | free text, may be `none` | Zusatznotizen zur Ephemeride. | no | sidecar review | Keine Ableitung aus Notiztext. |
| `dm_ism_state` | enum | required_blocking | allowed status vocabulary | Gesamtzustand von DM/ISM-Kontext. | yes for pulsar timing | `.par`, release docs, DM products | Chromatische Struktur ist Artefaktrisiko. |
| `dm_model_present` | boolean/status | required_if_applicable | `true`, `false`, `not_available_in_release`, `unknown` | Sichtbarkeit eines DM-Modells. | yes for pulsar timing | `.par` / release docs | Absent/unknown muss offen bleiben. |
| `dm_value_or_series_state` | enum | required_if_applicable | allowed status vocabulary | Zustand von DM-Wert, DM-Serie oder DMX-nahem Produkt. | yes for pulsar timing | `.par`, DM products | DM darf nicht aus TOAs geraten werden. |
| `wideband_dm_state` | enum | unavailable_marked | allowed status vocabulary | Zustand von Wideband-DM-Metadaten. | no if marked | release docs | Fehlen ist erlaubt, wenn explizit markiert. |
| `ism_scattering_state` | enum | required_if_applicable | allowed status vocabulary | Zustand von ISM-/Scattering-Kontext. | yes if relevant | release docs | Scattering kann Timingstruktur beeinflussen. |
| `plasma_correction_state` | enum | required_if_applicable | allowed status vocabulary | Zustand plasma-naher Korrekturen. | yes if relevant | `.par`, release docs, sidecar | Plasma-Kontext ist kein Residualbeleg. |
| `chromatic_control_available` | boolean/status | required_if_applicable | `true`, `false`, `planned`, `not_available_in_release`, `unknown` | Ob ein chromatischer Kontrollpfad verfuegbar oder planbar ist. | yes if DM controls are used | release docs / window plan | Kontrolle bleibt Workflow, keine physikalische Aussage. |
| `dm_ism_notes` | string | optional_documentary | free text, may be `none` | Zusatznotizen zu DM/ISM. | no | sidecar review | Notizen ersetzen keine DM-State-Felder. |
| `solar_wind_state` | enum | required_if_applicable | allowed status vocabulary | Gesamtzustand des Solarwind-Kontexts. | yes if relevant | timing model / release docs | Solarwind-Unknown darf nicht verschwinden. |
| `solar_wind_model_name` | string | required_if_applicable | model name, not_applicable, or unknown | Name des Solarwind-Modells, falls genutzt. | yes if solar wind relevant | `.par` / release docs | Modellname ist Baseline-Kontext. |
| `solar_elongation_available` | boolean/status | required_if_applicable | `true`, `false`, `planned`, `not_applicable`, `unknown` | Ob Solar-Elongation oder aequivalente Geometrie verfuegbar ist. | yes if solar controls used | release docs / window plan | Geometrie nur Kontrollinformation. |
| `solar_wind_correction_applied` | boolean/status | required_if_applicable | `true`, `false`, `partially_applied`, `not_applicable`, `unknown` | Ob Solarwind-Korrektur angewendet wurde. | yes if relevant | timing model / release docs | Anwendung ist kein Befund. |
| `solar_wind_notes` | string | optional_documentary | free text, may be `none` | Zusatznotizen zum Solarwind-Kontext. | no | sidecar review | Notizen halten Grenzen sichtbar. |
| `backend_instrument_state` | enum | required_blocking | allowed status vocabulary | Gesamtzustand von Backend und Instrument. | yes | `.tim` flags / release docs | Backend-Offsets koennen Vergleichsfenster stoeren. |
| `observatory_id_state` | enum | required_blocking | allowed status vocabulary | Zustand der Observatoriumskennungen. | yes | `.tim` flags | Fehlende IDs blockieren kontrollierte Zuordnung. |
| `receiver_band_state` | enum | required_if_applicable | allowed status vocabulary | Zustand von Receiver-/Bandinformation. | yes if band controls used | `.tim` flags / release docs | Bandinformationen sind Kontrollmaterial. |
| `backend_id_state` | enum | required_if_applicable | allowed status vocabulary | Zustand der Backend-Kennungen. | yes where backend jumps matter | `.tim` flags / release docs | Backend-Unknown ist ein Artefaktrisiko. |
| `instrument_jump_state` | enum | required_if_applicable | allowed status vocabulary | Zustand von Instrument-Jumps oder System-Offets. | yes if release uses jumps | `.par`, `.tim`, release docs | Jumps duerfen Residualsprache nicht verstecken. |
| `calibration_state` | enum | required_blocking | allowed status vocabulary | Zustand von Kalibration und Kalibrationsreferenz. | yes | release docs / calibration notes | Kalibration ist Baseline, kein Validierungsclaim. |
| `instrument_notes` | string | optional_documentary | free text, may be `none` | Zusatznotizen zu Instrument und Backend. | no | sidecar review | Notizen ersetzen keine Tags. |
| `noise_model_state` | enum | required_blocking | allowed status vocabulary | Gesamtzustand des Noise-Modells. | yes | release docs / noise files | Statuslogik braucht sichtbaren Noise-Kontext. |
| `white_noise_model_state` | enum | required_if_applicable | allowed status vocabulary | Zustand des White-Noise-Modells. | yes if used | release docs / noise model | Noise-Modell ist keine Evidenz. |
| `red_noise_model_state` | enum | required_if_applicable | allowed status vocabulary | Zustand des Red-Noise-Modells. | yes if relevant | release docs / noise model | Red noise kann Struktur imitieren. |
| `efac_state` | enum | required_if_applicable | allowed status vocabulary | Zustand EFAC-naher Parameter. | yes if used | release docs / noise files | EFAC ist Korrekturkontext. |
| `equad_state` | enum | required_if_applicable | allowed status vocabulary | Zustand EQUAD-naher Parameter. | yes if used | release docs / noise files | EQUAD darf nicht implizit bleiben. |
| `ecorr_state` | enum | required_if_applicable | allowed status vocabulary | Zustand ECORR-naher Parameter. | yes if used | release docs / noise files | ECORR-Kontext bleibt Kontrollschicht. |
| `covariance_model_state` | enum | required_if_applicable | allowed status vocabulary | Zustand eines Kovarianz- oder GP-nahen Modells. | yes if used | release docs / noise model | Kovarianzannahmen koennen Status beeinflussen. |
| `whitening_state` | enum | required_if_applicable | allowed status vocabulary | Zustand von Whitening oder aequivalenter Transformation. | yes if used | release docs / processing notes | Transformationen muessen sichtbar bleiben. |
| `noise_model_notes` | string | optional_documentary | free text, may be `none` | Zusatznotizen zum Noise-Modell. | no | sidecar review | Notizen sind keine Schwellenlogik. |
| `qc_state` | enum | required_blocking | allowed status vocabulary | Gesamtzustand der Qualitaetskontrolle. | yes | release docs / sidecar review | QC darf keine versteckte Vorselektion sein. |
| `outlier_policy_state` | enum | required_blocking | allowed status vocabulary | Zustand der Ausreisserpolitik. | yes | release docs / processing notes | Ausreisserregeln muessen vor Vergleich sichtbar sein. |
| `flagged_toa_state` | enum | required_if_applicable | allowed status vocabulary | Zustand markierter TOAs oder Flags. | yes if TOA flags exist | `.tim` flags / release docs | Flags duerfen nicht ignoriert werden. |
| `quality_flags_available` | boolean/status | required_blocking | `true`, `false`, `not_available_in_release`, `unknown` | Ob Quality-Flags verfuegbar sind. | yes | `.tim` / release docs | Abwesenheit kann Pilotfenster begrenzen. |
| `excluded_records_state` | enum | required_if_applicable | allowed status vocabulary | Zustand ausgeschlossener Records oder TOAs. | yes if exclusions exist | release docs / processing notes | Ausschluesse muessen auditiert sein. |
| `qc_notes` | string | optional_documentary | free text, may be `none` | Zusatznotizen zur QC. | no | sidecar review | Notizen duerfen keine Ausschlusslogik ersetzen. |
| `window_definition_state` | enum | required_blocking | allowed status vocabulary | Gesamtzustand der Fensterdefinition. | yes | window sidecar / pilot plan | Ohne Fenster keine Vergleichslogik. |
| `a_reference_window_state` | enum | required_blocking | allowed status vocabulary | Zustand des A-Referenzfensters. | yes | window sidecar | Referenzfenster ist technisches Kontrollfenster. |
| `b_model_relevant_window_state` | enum | required_blocking | allowed status vocabulary | Zustand des B-modellrelevanten Fensters. | yes | window sidecar | Modellrelevanz ist kein Physikclaim. |
| `negative_control_window_state` | enum | required_blocking | allowed status vocabulary | Zustand mindestens eines negativen Kontrollfensters. | yes | window sidecar | Ohne negative Kontrolle kein Dry-Run-Preview. |
| `shuffle_control_state` | enum | required_blocking | allowed status vocabulary | Zustand des Shuffle-Control-Konzepts. | yes | window sidecar | Shuffle prueft Sensitivitaet gegen False Positives. |
| `backend_homogeneous_window_state` | enum | required_if_applicable | allowed status vocabulary | Zustand backend-homogener Fensterbeschraenkung. | yes if backend jumps matter | window sidecar / `.tim` flags | Optional nur, wenn sauber markiert. |
| `dm_control_window_state` | enum | required_if_applicable | allowed status vocabulary | Zustand eines DM-/chromatischen Kontrollfensters. | yes if DM control used | window sidecar / DM metadata | DM-Kontrolle ist keine Residualdeutung. |
| `window_notes` | string | optional_documentary | free text, may be `none` | Zusatznotizen zu Fenstern und Kontrollen. | no | sidecar review | Notizen bleiben nachgeordnet. |
| `shapiroinfo02_mapping_state` | enum | required_blocking | allowed status vocabulary | Gesamtzustand der Abbildung in SHAPIROINFO02-Felder. | yes | mapping preview / field audit | Mapping ist Preview, kein Ergebnis. |
| `directly_mapped_field_count` | integer | required_blocking | non-negative integer | Anzahl direkt abgebildeter SHAPIROINFO02-Felder. | yes | mapping audit | Feldzaehlung ist kein Qualitaetsbeweis. |
| `sidecar_mapped_field_count` | integer | required_blocking | non-negative integer | Anzahl ueber Sidecar abgebildeter Felder. | yes | mapping audit | Sidecar-Anteil zeigt Abhaengigkeiten. |
| `blocked_field_count` | integer | required_blocking | non-negative integer | Anzahl blockierter Pflicht- oder Gate-Felder. | yes | mapping audit | Blockierte Felder muessen stoppen koennen. |
| `unavailable_field_count` | integer | required_blocking | non-negative integer | Anzahl explizit nicht verfuegbarer Felder. | yes | mapping audit | Nichtverfuegbarkeit ist sichtbar zu halten. |
| `adapter_readiness_label` | enum | required_blocking | adapter readiness labels | Readiness-Label fuer spaetere Dry-Run-Preview. | yes | sidecar gate logic | Readiness ist Gate-Status, kein Befund. |
| `go_no_go_status` | enum | required_blocking | `GO_FOR_DRY_RUN_PREVIEW`, `NO_GO`, `NEEDS_MANUAL_REVIEW` | Ergebnis des lokalen Go/No-Go-Gates. | yes | sidecar gate logic | GO heisst nur Dry-Run-Preview erlaubt. |
| `go_no_go_reason` | string | required_blocking | concise reason string | Begruendung fuer Gate-Status. | yes | sidecar gate logic | Begruendung darf Claim Boundary nicht lockern. |
| `bridge_confirmation_flag` | boolean | required_blocking | `false` only | Muss false sein. | yes | sidecar constant | Jede true-Setzung blockiert. |
| `physical_validation_flag` | boolean | required_blocking | `false` only | Muss false sein. | yes | sidecar constant | Keine physische Validierung aus Schema oder Sidecar. |
| `new_shapiro_effect_claim_flag` | boolean | required_blocking | `false` only | Muss false sein. | yes | sidecar constant | Keine neue Shapiro-Effekt-Behauptung. |
| `gr_incomplete_claim_flag` | boolean | required_blocking | `false` only | Muss false sein. | yes | sidecar constant | Keine Aussage, dass GR unvollstaendig ist. |
| `residual_implies_qsb_flag` | boolean | required_blocking | `false` only | Muss false sein. | yes | sidecar constant | Residualsprache darf QSB-ST nicht implizieren. |
| `dataset_specific_evidence_claim_flag` | boolean | required_blocking | `false` only | Muss false sein. | yes | sidecar constant | Keine datensatzspezifische Evidenzbehauptung. |
| `real_data_result_claim_flag` | boolean | required_blocking | `false` only | Muss false sein. | yes | sidecar constant | Kein Real-Daten-Ergebnis aus Schemaarbeit. |
| `candidate_residual_claim_flag` | boolean | required_blocking | `false` only | Muss false sein. | yes | sidecar constant | Kein Kandidaten-Residual aus Schema-Planung. |
| `derivation_of_c_claim_flag` | boolean | required_blocking | `false` only | Muss false sein. | yes | sidecar constant | Keine c-Ableitung. |
| `numerical_c_explanation_claim_flag` | boolean | required_blocking | `false` only | Muss false sein. | yes | sidecar constant | Keine Erklaerung des numerischen Werts von c. |

## Allowed Status Vocabulary

Erlaubte Statuswerte fuer enum-nahe State-Felder:

- `known_documented`: explizit durch Release, Datei oder Review dokumentiert.
- `known_inferred_from_release`: aus Release-Kontext abgeleitet, aber als
  Inferenz markiert.
- `unknown`: unbekannt; fuer zentrale Schichten blockierend.
- `not_applicable`: fuer diesen Datensatz nicht anwendbar.
- `not_available_in_release`: im Release nicht verfuegbar.
- `manual_review_required`: menschliche Pruefung noetig.
- `applied`: Korrektur oder Modellschritt angewendet.
- `not_applied`: Korrektur oder Modellschritt nicht angewendet.
- `partially_applied`: nur teilweise angewendet.
- `present`: vorhanden.
- `absent`: nicht vorhanden.
- `planned`: geplant, aber noch nicht umgesetzt.
- `blocked`: blockiert.

## Adapter Readiness Labels

- `ready_for_dry_run_preview`: Sidecar-Gates reichen fuer eine spaetere
  Dry-Run-Preview, ohne Residualrechnung.
- `needs_manual_review`: mindestens ein Feld braucht menschliche Klaerung,
  bevor ein Adapterlauf sinnvoll ist.
- `blocked_missing_correction_state`: zentrale Correction-State-Schicht fehlt
  oder ist unknown.
- `blocked_missing_provenance`: Quelle, Zitation, Datennutzung oder Version ist
  unklar.
- `blocked_missing_timing_model`: Timingmodell fehlt oder ist nicht
  dokumentiert.
- `blocked_missing_observation_file`: Beobachtungsdatei oder `.tim`-aequivalent
  fehlt im spaeteren Manifest.
- `blocked_no_controls`: negative oder technische Kontrollfenster fehlen.
- `not_applicable`: Schema ist fuer diesen Datensatzpfad nicht anwendbar.

## Go/No-Go Logic

`GO_FOR_DRY_RUN_PREVIEW` nur wenn:

- provenance fields complete
- timing model present
- observation file present
- clock state not opaque
- ephemeris state not opaque
- binary model state explicit for binary pilot
- TOA uncertainty state visible
- at least one negative control window planned
- claim flags all false

`NO_GO` wenn:

- correction state unknown for central layers
- time standard unclear
- clock or ephemeris unknown
- binary model state unclear
- no control windows
- provenance unclear
- data-use/citation unclear
- any claim flag true

## Relation To SHAPIROINFO09

SHAPIROINFO09 planned the targeted binary pulsar pilot. SHAPIROINFO10 defines
the sidecar schema required before that pilot can move toward a dry-run
adapter.

## Relation To SHAPIROINFO02

SHAPIROINFO02 defines the signal record. SHAPIROINFO10 defines the
correction-state companion layer needed to interpret or block use of those
records.

## Befund

Correction-State must be treated as a first-class blocking layer for semi-real
data.

## Interpretation

The schema prevents hidden assumptions about clock, ephemeris, DM/ISM,
backend, noise, model state, and QC from silently entering the comparator.

## Hypothese

A strict Correction-State sidecar can reduce false-positive risk before any
real or semi-real timing data are mapped into the ShapiroInfo workflow.

## Offene Luecke

- no template file created yet
- no real sidecar populated
- no dataset selected
- no data parsed
- no adapter implemented
- no dry-run preview executed
- no empirical result

## Claim Boundary

- no Bridge confirmation
- no physical validation
- no new Shapiro effect claim
- no claim that GR is incomplete
- no claim that any residual implies QSB-ST
- no dataset-specific evidence claim
- no real-data result
- no candidate residual claim from schema planning
- no derivation of c
- no explanation of the numerical value of c

## Next Possible Blocks

- SHAPIROINFO11 Correction-State Sidecar Template
- SHAPIROINFO12 Public Source and Citation Checklist
- SHAPIROINFO13 Targeted Binary Pulsar Dry-Run Adapter Spec
- SHAPIROINFO14 Cassini Feasibility Study Plan
- SHAPIROINFO15 VLBI Feasibility Study Plan

## Acceptance Checks

- Datei existiert
- enthaelt correction_state_schema_version
- enthaelt clock_correction_state
- enthaelt ephemeris_state
- enthaelt dm_ism_state
- enthaelt backend_instrument_state
- enthaelt noise_model_state
- enthaelt qc_state
- enthaelt GO_FOR_DRY_RUN_PREVIEW
- enthaelt blocked_missing_correction_state
- enthaelt bridge_confirmation_flag
- enthaelt numerical_c_explanation_claim_flag
- risk grep clean
- git diff --check clean
- git status --short reported
