# QSB-DB19 — Synthetic Sample Data Result Note

Date: 2026-06-02
Status: synthetic sample data result documented
Upstream execution: QSB-DB18_SYNTHETIC_SAMPLE_DATA_EXECUTION
Scope: QSB-wide research database infrastructure
Result type: controlled synthetic test-data database result
Tracking decision: this documentation note may be tracked; SQLite database artifacts remain run artifacts

## 1. Purpose

Diese Note dokumentiert das Ergebnis von QSB-DB18: die erste sichtbare kontrollierte synthetische Testdaten-Schicht in der QSB SQLite research database.

Der positive technische Befund ist, dass die Datenbank nun nicht nur Metadaten-Linie und Schema enthält, sondern auch browsbare synthetische Testzeilen für Raw-Staging, Token, Felder, ETL-Regeln, Quality Checks, harmonized-view metadata und Claim Boundaries.

Diese Note dokumentiert keine Real-Daten-Auswertung.

Diese Note dokumentiert keine physikalische Auswertung.

Diese Note dokumentiert keine Residualsuche, kein Model Fitting und keine Bridge-Interpretation.

## 2. Inputs and Execution Anchor

DB17 wurde vor der Ausführung eingefroren.

- DB17 commit hash: `3fcdf82`
- DB17 committed only: `scripts/qsb_db17_synthetic_sample_data.py`

DB18 wurde genau einmal mit folgendem Befehl ausgeführt:

```text
python scripts/qsb_db17_synthetic_sample_data.py --input-db runs/QSB-DB/QSB_DB13_METADATA_SEED/qsb_research_metadata_seed.db --output-root runs/QSB-DB/QSB_DB18_SYNTHETIC_SAMPLE_DATA --output-db runs/QSB-DB/QSB_DB18_SYNTHETIC_SAMPLE_DATA/qsb_research_synthetic_sample.db
```

Die Eingabedatenbank war:

```text
runs/QSB-DB/QSB_DB13_METADATA_SEED/qsb_research_metadata_seed.db
```

Die Ausgabedatenbank war:

```text
runs/QSB-DB/QSB_DB18_SYNTHETIC_SAMPLE_DATA/qsb_research_synthetic_sample.db
```

Execution result:

```text
synthetic_sample: complete
output_db: runs/QSB-DB/QSB_DB18_SYNTHETIC_SAMPLE_DATA/qsb_research_synthetic_sample.db
synthetic_sample_status: completed
inserted_row_count_total: 51
fk_validation_status: passed
forbidden_content_check_status: passed
synthetic_label_check_status: passed
```

## 3. Created Outputs

QSB-DB18 erzeugte folgende Run-Artefakte:

- `runs/QSB-DB/QSB_DB18_SYNTHETIC_SAMPLE_DATA/qsb_research_synthetic_sample.db`
- `runs/QSB-DB/QSB_DB18_SYNTHETIC_SAMPLE_DATA/synthetic_sample_config_resolved.json`
- `runs/QSB-DB/QSB_DB18_SYNTHETIC_SAMPLE_DATA/synthetic_sample_fk_validation.csv`
- `runs/QSB-DB/QSB_DB18_SYNTHETIC_SAMPLE_DATA/synthetic_sample_forbidden_content_check.csv`
- `runs/QSB-DB/QSB_DB18_SYNTHETIC_SAMPLE_DATA/synthetic_sample_insert_counts.csv`
- `runs/QSB-DB/QSB_DB18_SYNTHETIC_SAMPLE_DATA/synthetic_sample_readout.md`
- `runs/QSB-DB/QSB_DB18_SYNTHETIC_SAMPLE_DATA/synthetic_sample_summary.json`
- `runs/QSB-DB/QSB_DB18_SYNTHETIC_SAMPLE_DATA/synthetic_sample_table_row_counts.csv`

Diese Dateien bleiben Run-Artefakte.

Sie wurden durch diese Note nicht gestaged und nicht committed.

## 4. Validation Summary

Die Python-`sqlite3`-Validierung berichtete:

- DB exists: `True`
- `PRAGMA foreign_key_check` returned no rows.

Vorhandene Tabellen:

```text
audit_log
claim_boundary_catalog
document_catalog
document_table_relation
etl_transformation_rule
field_catalog
git_commit_catalog
harmonized_value_view_catalog
pk_fk_relation_catalog
project_file_catalog
quality_check_catalog
quality_check_result
quantity_catalog
quantity_domain_catalog
raw_data
raw_data_source
raw_token_catalog
repo_catalog
run_catalog
run_output_catalog
script_catalog
script_table_relation
table_catalog
transformation_rule_catalog
unit_dimension_catalog
```

Die eigentliche Validierung gegen die aktuelle DB03-Schema-Nomenklatur bestätigte:

- `synthetic_sample_status = completed`
- `metadata_db_modified = False`
- `sample_execution_mode = synthetic_only`
- `inserted_table_count = 9`
- `inserted_row_count_total = 51`
- `fk_validation_status = passed`
- `foreign_key_check_violations = []`
- `forbidden_content_check_status = passed`
- `synthetic_label_check_status = passed`
- `real_data_ingestion = False`
- `c60_value_ingestion = False`
- `analytics_data_ingestion = False`
- `raw_artifact_access_status = not_performed`
- `tim_par_value_reading_status = not_performed`
- `documentation_download_status = not_performed`
- `physical_interpretation_status = forbidden`
- `residual_analysis_gate = closed`
- `model_fitting_gate = closed`
- `bridge_claim_gate = closed`

## 5. Visible Synthetic Test Cases

Die sichtbaren synthetischen `raw_data`-Fälle sind:

- `clean_numeric_sample`
- `blank_value_sample`
- `special_character_sample`
- `string_numeric_cast_sample`
- `scale_normalization_sample`
- `missing_value_sample`
- `quarantine_candidate_sample`
- `harmonization_ready_sample`

Diese Labels stammen aus synthetischen Testzeilen.

Sie sind Infrastruktur-Testfälle für Browsing, Statussichtbarkeit und ETL-Pfadkontrolle.

Sie sind keine Messdaten.

## 6. Actual Row Counts

Die aktuellen Row Counts in den relevanten Tabellen waren:

```text
raw_data_source 3
raw_data 8
raw_token_catalog 10
field_catalog 7
etl_transformation_rule 6
quality_check_catalog 5
quality_check_result 7
harmonized_value_view_catalog 1
claim_boundary_catalog 13
```

Die eingefügten synthetischen Counts laut Summary waren:

```text
raw_data_source: 1
raw_data: 8
raw_token_catalog: 10
field_catalog: 7
etl_transformation_rule: 6
quality_check_catalog: 5
quality_check_result: 7
harmonized_value_view_catalog: 1
claim_boundary_catalog: 6
```

Die Gesamtzahl der synthetischen Einfügungen war:

```text
inserted_row_count_total = 51
```

## 7. Schema-Name Correction from Generic Validation Block

Der erste generische Validierungsblock nutzte ältere oder alternative Tabellen- und Spaltennamen:

- `raw_token`
- `etl_rule_catalog`
- `view_catalog`
- `raw_case_label`
- `raw_data_status`

Das aktuelle DB03-Schema verwendet stattdessen:

- `raw_token_catalog`
- `etl_transformation_rule`
- `harmonized_value_view_catalog`
- Statusfelder wie `raw_ingest_status`, `raw_parse_status`, `raw_quality_status`, `harmonization_status`, `etl_release_status` und `quarantine_status`
- Falllabels im synthetischen Lauf über `raw_data.notes`

Dies ist eine Validierungs-Vokabular- beziehungsweise Schema-Namens-Korrektur.

Es ist kein DB18-Fehler.

Die Datenbank enthielt die erwarteten synthetischen Inhalte in den aktuellen Tabellen.

## 8. ETL Rule Count Warning

Die Summary berichtete:

```text
synthetic_etl_rule_count: 5
```

Die Insert Counts und der tatsächliche Table Count berichteten:

```text
etl_transformation_rule: 6
```

Die Ursache ist eine Suffix-Filter-Definition in der Summary-Abfrage.

Gezählt wurden Rule Names, die auf `_synthetic` enden.

Die Regel `synthetic_unit_to_si_placeholder` ist synthetisch, endet aber nicht mit diesem Suffix.

Damit ist dies eine Count-Definition-Warnung.

Es ist kein Hinweis auf Datenverlust.

## 9. Gate Status

Die Gates blieben geschlossen:

- no real raw artifacts inspected
- no TIM/PAR values read
- no C60/molecular/physical values ingested
- no analytics
- no residual search
- no model fitting
- no Bridge interpretation

Die `claim_boundary_catalog`-Abfrage zeigte 13 Rows.

Alle `physical_interpretation_allowed`, `residual_analysis_allowed`, `model_fitting_allowed`, `bridge_claim_allowed` und `value_reading_allowed` Flags blieben `0`.

## 10. Befund

QSB-DB18 erzeugte erfolgreich eine separate synthetische Sample-Datenbank:

```text
runs/QSB-DB/QSB_DB18_SYNTHETIC_SAMPLE_DATA/qsb_research_synthetic_sample.db
```

Die Datenbank enthält 51 eingefügte synthetische Testzeilen über 9 Tabellen hinweg.

Der Foreign-Key-Check gab keine Zeilen zurück.

Die Forbidden-Content-Prüfung bestand.

Die Synthetic-Label-Prüfung bestand.

Die metadata-seeded Eingabedatenbank wurde laut Summary nicht verändert.

## 11. Interpretation

Der Lauf zeigt, dass die QSB research database als Infrastruktur nun sichtbare, kontrollierte synthetische Datenpfade darstellen kann.

Damit werden DB Browser-Inspektion, Statusketten, Raw-Staging, Tokenisierung, Field Catalog, ETL-Regel-Metadaten, Quality Checks und Claim Boundaries konkret browsbar.

Die wichtigste methodische Verbesserung ist nicht inhaltliche Auswertung, sondern Bedienbarkeit und Auditierbarkeit des Datenbankmodells.

Die Schema-Namens-Korrektur zeigt außerdem, dass zukünftige Validierungsblöcke die aktuelle DB03-Nomenklatur verwenden sollten.

## 12. Hypothese / Next Use

Als nächster praktischer Schritt kann eine DB-Browser-Inspektionsplanung für die synthetische Sample-Datenbank folgen.

Ein sinnvoller nächster Block ist:

```text
QSB-DB20_SYNTHETIC_SAMPLE_DB_BROWSER_INSPECTION_PLAN
```

Diese Inspektion sollte read-only bleiben und prüfen:

- ob die synthetischen Tabellenbereiche sichtbar und verständlich sind
- ob die Row Counts erwartbar erscheinen
- ob die Claim-Boundary-Zeilen geschlossen bleiben
- ob die Schema-Namens-Korrektur in künftigen Prüfungen berücksichtigt werden muss
- ob die Suffix-Filter-Warnung in einer späteren Script-Revision präzisiert werden sollte

## 13. Offene Lücke

Die Summary-Zählung für `synthetic_etl_rule_count` ist nicht vollständig deckungsgleich mit der tatsächlichen synthetischen ETL-Regelanzahl.

Die Ursache ist bekannt: die Zählung verwendet ein `_synthetic`-Suffixkriterium.

Eine spätere Korrektur könnte die Zählung auf `provenance_status = synthetic_controlled` oder eine explizite synthetische Rule-Liste umstellen.

Außerdem sollten spätere generische Validierungsblöcke die aktuellen Tabellennamen `raw_token_catalog`, `etl_transformation_rule` und `harmonized_value_view_catalog` verwenden.

Diese offenen Punkte betreffen Review- und Reporting-Genauigkeit.

Sie betreffen nicht die Integrität des DB18-Laufs.

## 14. Claim Boundary

Diese Note dokumentiert ein kontrolliertes synthetisches Datenbank-Infrastruktur-Ergebnis.

Sie dokumentiert keine Real-Daten-Auswertung.

Sie dokumentiert keine TIM/PAR-Wertlesung.

Sie dokumentiert keine C60-, molekulare, Pulsar-, Timing-, Shapiro- oder physikalische Wertaufnahme.

Sie dokumentiert keine Analytics.

Sie dokumentiert keine Residualsuche.

Sie dokumentiert kein Model Fitting.

Sie dokumentiert keine Bridge-Interpretation.

Diese Note liefert keinen Beleg für ein physikalisches Shapiro-Information-Residual.

Diese Note validiert nicht die QSB-ST Bridge.

Diese Note etabliert keine Aussagen über Spacetime, Quantum Gravity, Relativistik, Pulsar Timing, Molekülstruktur oder C60-Physik.

Die synthetischen Sample Rows sind ausschließlich Infrastruktur-Testdaten.
