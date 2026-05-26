# QSB-ST INTERFACE02 Minimal Record Schema and Acceptance Specification

## 1. Purpose

INTERFACE02 ueberfuehrt die INTERFACE01-Konnektoridee in eine minimale Record-Struktur und Akzeptanzlogik fuer spaeteres Runner-Design.

Der Block bleibt klein, fein, aber zentral: Ein Interface-Record soll spaeter genau eine diagnostische Einheit beschreiben, ohne aus Lesbarkeit Identitaet, Raumzeit, Bridge oder physische Validierung zu machen.

Dies ist keine Implementierung. Es werden keine Daten, keine Skripte und keine Runs erzeugt.

## 2. Source basis

Pflichtquelle:

- `docs/QSB_ST_INTERFACE01_CONNECTOR_DIAGNOSTIC_SPEC.md`

INTERFACE01 definierte das Interface-Record-Konzept als:

```text
interface_record := declared input family
                  + declared diagnostic family
                  + declared controls
                  + declared result states
                  + declared claim boundary flags
```

INTERFACE02 konkretisiert diese Formel als minimale Feldliste und Akzeptanzliste.

## 3. Minimal interface-record concept

Ein Interface-Record ist eine atomare diagnostische Einheit.

Er soll beschreiben:

- was verglichen oder gelesen wurde
- welche diagnostische Familie angewendet wurde
- welche Kontrollen deklariert wurden
- welcher Ergebniszustand erreicht wurde
- welcher Ambiguitaetszustand gilt
- welche Claim-Flags geschlossen bleiben

Ein Interface-Record ist kein physisches Objekt und keine Ontologie. Er ist ein auditierbarer Diagnosecontainer.

## 4. Required field list

Mindestfelder:

1. `interface_record_id`
2. `interface_block_id`
3. `source_lineage_id`
4. `input_family_id`
5. `input_record_id`
6. `comparison_scope`
7. `diagnostic_family_id`
8. `diagnostic_version`
9. `diagnostic_input_columns`
10. `transform_family_id`
11. `controls_declared`
12. `null_families_declared`
13. `control_status`
14. `readability_status`
15. `ambiguity_status`
16. `degeneracy_status`
17. `identity_stop_status`
18. `invalid_outside_scope_status`
19. `bridge_confirmation_flag`
20. `physical_validation_flag`
21. `diagnostic_specificity_flag`
22. `spacetime_emergence_flag`
23. `qg_theory_claim_flag`
24. `claim_boundary_status`
25. `warnings`
26. `failed_checks`
27. `runner_passed`
28. `notes`

## 5. Field list with type and description

| field_name | field_type | description |
| --- | --- | --- |
| `interface_record_id` | string | Eindeutige ID fuer eine atomare Interface-Diagnoseeinheit. |
| `interface_block_id` | string | Blockkennung, zum Beispiel `QSB-ST-INTERFACE02` oder ein spaeterer Runner-Block. |
| `source_lineage_id` | string | Herkunfts- oder Method-Trail-ID, die Eingabe, Spezifikation und Kontext nachvollziehbar macht. |
| `input_family_id` | string | Kennung der Eingabefamilie, etwa synthetische Fingerprint-Records oder relationale Vergleichspaare. |
| `input_record_id` | string | Kennung des konkreten Eingaberecords oder Vergleichsrecords. |
| `comparison_scope` | string enum | Geltungsbereich des Vergleichs, zum Beispiel `single_record`, `pairwise`, `family_level` oder `outside_scope`. |
| `diagnostic_family_id` | string | Kennung der angewendeten Diagnostikfamilie. |
| `diagnostic_version` | string | Versionskennung der Diagnostikdefinition. |
| `diagnostic_input_columns` | list[string] | Explizite Liste der Eingabefelder oder Spalten, die fuer die Diagnostik verwendet wurden. |
| `transform_family_id` | nullable string | Kennung der angewendeten oder geprueften Transformfamilie; null, wenn keine Transformfamilie gilt. |
| `controls_declared` | list[string] | Explizite Liste deklarierter Kontrollfamilien. Muss vor Interpretation nicht-leer sein. |
| `null_families_declared` | list[string] | Explizite Liste deklarierter Nullfamilien. Muss vor Interpretation nicht-leer sein. |
| `control_status` | string enum | Ergebnisstatus der Kontrollen. Erlaubte Werte werden unten definiert. |
| `readability_status` | string enum | Status diagnostischer Lesbarkeit. Erlaubte Werte werden unten definiert. |
| `ambiguity_status` | string enum | Status der Ambiguitaet. Erlaubte Werte werden unten definiert. |
| `degeneracy_status` | string enum | Status der Degeneracy-Einschaetzung. Keine reale Degeneracy-Messung auf INTERFACE02-Ebene. |
| `identity_stop_status` | string enum | Status, warum Identitaetsauflösung nicht behauptet wird. |
| `invalid_outside_scope_status` | string enum | Status, ob ein outside-scope-Fall vorliegt und als non-success behandelt wird. |
| `bridge_confirmation_flag` | bool | Muss fuer INTERFACE01/02-Level false bleiben. |
| `physical_validation_flag` | bool | Muss fuer INTERFACE01/02-Level false bleiben. |
| `diagnostic_specificity_flag` | bool | Muss fuer INTERFACE01/02-Level false bleiben. |
| `spacetime_emergence_flag` | bool | Muss fuer INTERFACE01/02-Level false bleiben. |
| `qg_theory_claim_flag` | bool | Muss fuer INTERFACE01/02-Level false bleiben. |
| `claim_boundary_status` | string enum | Status der Claim-Grenze. Erlaubte Werte werden unten definiert. |
| `warnings` | nullable list[string] | Warnungen, zum Beispiel unvollstaendige Kontrollen oder nicht bewertete Degeneracy. |
| `failed_checks` | nullable list[string] | Fehlgeschlagene Checks. Leer oder null nur bei sauberem Schema-/Acceptance-Pass. |
| `runner_passed` | bool | True nur, wenn alle minimalen Akzeptanzbedingungen erfuellt sind. |
| `notes` | nullable string | Kurzer auditierbarer Kommentar ohne Claim-Erweiterung. |

## 6. Required decision states

Erlaubte Werte fuer `readability_status`:

- `readable_under_declared_diagnostics`
- `not_readable_under_declared_diagnostics`
- `ambiguous_readability`
- `invalid_interface_measurement`

Erlaubte Werte fuer `ambiguity_status`:

- `ambiguity_not_detected`
- `ambiguous_unresolved`
- `ambiguity_resolved_by_declared_rule`
- `ambiguity_not_assessed`

Erlaubte Werte fuer `degeneracy_status`:

- `degeneracy_not_assessed`
- `degeneracy_candidate_detected`
- `degeneracy_unresolved`
- `degeneracy_resolved_by_declared_rule`

Erlaubte Werte fuer `identity_stop_status`:

- `identity_not_claimed`
- `identity_blocked_by_ambiguity`
- `identity_blocked_by_missing_rule`
- `identity_blocked_by_control_failure`

Erlaubte Werte fuer `control_status`:

- `controls_passed`
- `controls_failed`
- `controls_incomplete`
- `controls_not_applicable`

Erlaubte Werte fuer `claim_boundary_status`:

- `all_required_claim_flags_closed`
- `claim_boundary_violation`
- `claim_boundary_incomplete`

`runner_passed` ist ein boolesches Feld.

## 7. Required claim-boundary flags

Folgende Felder sind bool-Felder und muessen standardmaessig false sein:

- `bridge_confirmation_flag`
- `physical_validation_flag`
- `diagnostic_specificity_flag`
- `spacetime_emergence_flag`
- `qg_theory_claim_flag`

Fuer INTERFACE01/02-Level-Arbeit muessen diese Flags false bleiben.

Wenn eines dieser Flags true wird, muss der Record scheitern, ausser es existiert ein separater, explizit autorisierter Validierungsblock. Ein solcher Validierungsblock existiert hier nicht.

## 8. Required control declarations

`controls_declared` und `null_families_declared` muessen explizite Listen sein, kein Prosaersatz.

Minimale Kontrollfamilien, die zu beruecksichtigen sind:

- `label_shuffle_controls`
- `feature_shuffle_controls`
- `representation_preserving_controls`
- `identity_relevant_transform_controls`
- `ambiguity_preserving_controls`
- `matched_coordinate_nulls`
- `matched_marginal_nulls`
- `target_smuggling_checks`
- `claim_boundary_flag_checks`

Welche davon im konkreten Record stehen, muss vor der Interpretation deklariert sein.

## 9. Minimal acceptance list

Ein spaeterer Runner darf auf Schema-/Acceptance-Ebene nur bestehen, wenn:

- alle required fields vorhanden sind
- enum-Felder nur erlaubte Werte verwenden
- erforderliche Claim-Boundary-Flags vorhanden und false sind
- `controls_declared` nicht leer ist
- `null_families_declared` nicht leer ist
- `readability_status` nicht als Identitaetsevidenz verwendet wird
- Ambiguitaetszustaende erhalten bleiben
- `invalid_outside_scope_status` nicht als Erfolg gezaehlt wird
- `failed_checks` leer ist oder ausdruecklich als non-success behandelt wird
- `claim_boundary_status` `all_required_claim_flags_closed` ist
- `runner_passed` nur true ist, wenn alle obigen Bedingungen erfuellt sind

Akzeptanz heisst hier nur: der Record ist auditierbar genug fuer die kleine Interface-Diagnosefrage.

## 10. Rejection / non-success conditions

Ein Record muss non-success sein, wenn:

- required fields fehlen
- Claim-Boundary-Flags fehlen
- ein required-false Claim-Flag true ist
- Kontrollen fehlen oder unvollstaendig sind
- Nullfamilien fehlen
- Ambiguitaet ueberschrieben oder in Erfolg gezwungen wird
- `invalid_outside_scope` als Erfolg gezaehlt wird
- Lesbarkeit zur Identitaets- oder Raumzeitbehauptung verwendet wird
- diagnostische Spezifitaet ohne hostile controls behauptet wird
- source lineage fehlt

Non-success ist kein Scheitern des Projekts. Es ist ein valider Stoppzustand.

## 11. Expected future files, not yet created

Moegliche spaetere Dateien:

- `data/QSB-ST-INTERFACE02/minimal_interface_record_schema.json`
- `data/QSB-ST-INTERFACE02/interface_acceptance_config.yaml`
- `scripts/run_qsb_st_interface02_schema_acceptance.py`
- `runs/QSB-ST-INTERFACE02/<run_id>/summary.json`
- `runs/QSB-ST-INTERFACE02/<run_id>/readout.md`
- `runs/QSB-ST-INTERFACE02/<run_id>/interface_record_validation_summary.csv`

Diese Dateien werden in INTERFACE02 nicht erstellt.

## 12. Befund

INTERFACE01 existiert und definiert die Konnektor-Diagnoseschicht als operationales Interface, nicht als physische Entitaet.

INTERFACE02 definiert nun die minimale Record-Struktur und Akzeptanzlogik. Es fuehrt keinen Run aus und erzeugt keine strukturierten Daten.

## 13. Interpretation

Das Projekt hat jetzt eine Route vom Konzept zur spaeteren Runner-Schemaebene, ohne Claims zu eskalieren.

Die zentrale Bewegung bleibt klein: diagnostische Lesbarkeit, Ambiguitaet, Kontrollstatus und Claim-Flags sollen in einem auditierbaren Record zusammengehalten werden.

## 14. Hypothese

Projektinterne Hypothese:

```text
Wenn spaetere Records Lesbarkeit, Ambiguitaet, Kontrollstatus und
Claim-Flags in einer auditierbaren Einheit bewahren, kann QSB-ST
interfaceartiges diagnostisches Verhalten testen, ohne in Identitaets-
oder Raumzeitclaims zu kollabieren.
```

Diese Hypothese ist methodisch und schema-facing.

## 15. Offene Lücke

Offen bleiben:

- tatsaechliche Schema-Datei
- Acceptance-Config
- Beispielrecords
- Runner-Implementierung
- erste kontrollierte Eingabefamilie
- erste Nullfamilienauswahl
- Entscheidung ueber CSV-/JSON-Readouts

## 16. Claim Boundary

Dies ist eine Spezifikation.

- Keine neue Berechnung.
- Kein public release.
- Kein Upload.
- Keine physische Validierung.
- Keine Bridge-Bestaetigung.
- Kein diagnostischer Spezifitaetsclaim.
- Kein Raumzeit-Emergenzclaim.
- Kein Quantum-Gravity-Theorieclaim.
- Keine reale Degeneracy-Messung.
- Keine Identitaetsaufloesung.
- Keine Oeffnung von WIFM01E.
- Keine Oeffnung von WIFM02.
- Keine Oeffnung von BRIDGE-NATURE-02.
- Interface bleibt operational/metaphorisch, bis es getestet ist.
- Future runner files sind nur konzeptuell gelistet und werden hier nicht erstellt.

## 17. Consequence for next step

Naechster sinnvoller Schritt waere INTERFACE03: eine minimale Schema-/Config-Scaffold-Planung oder, nach expliziter Freigabe, eine erste JSON/YAML-Schema-Datei mit synthetischen Beispielrecords.

Vor jeder Implementierung muessen die required fields, Enums, required-false Claim-Flags, Kontrolllisten und Non-Success-Regeln aus INTERFACE02 uebernommen werden.
