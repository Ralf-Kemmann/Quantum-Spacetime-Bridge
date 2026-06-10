# OUTREACH01A-DTC-DEMO01 Field List

| Field Path | Canonical Field Name | German Alias | Type | Required | Description |
|---|---|---|---|---|---|
| `record_id` | `record_id` | Record-ID | string | yes | Stable record identifier; exactly `DTC_A`, `DTC_B`, or `BOUNDARY_AB`. |
| `record_type` | `record_type` | Record-Typ | enum string | yes | `state_configuration` or `boundary_configuration`. |
| `state_class` | `state_class` | Zustandsklasse | string | yes | Declared synthetic state class; German value aliases are presentation metadata only. |
| `dynamic_equivalence_class` | `dynamic_equivalence_class` | Klasse der dynamischen Äquivalenz | string | yes | Declared synthetic dynamic equivalence class or `not_applicable`; German value aliases are not logic inputs. |
| `temporal_phase_offset` | `temporal_phase_offset` | Zeitliche Phasenverschiebung | number or string | yes | Synthetic temporal phase offset, or `not_applicable` for the boundary record. |
| `drive_period_units` | `drive_period_units` | Verschiebung in Antriebsperioden | number or string | yes | Offset measured in drive-period units, or `not_applicable` for the boundary record. |
| `domain_id` | `domain_id` | Domänen-ID | string | yes | Synthetic domain identifier. |
| `boundary_role` | `boundary_role` | Rolle der Grenzstruktur | string | yes | Boundary role; `none` for state records; localized value aliases are display-only. |
| `observable_signature` | `observable_signature` | Beobachtbare Signatur | string | yes | Minimal synthetic observable signature label. |
| `observable_similarity` | `observable_similarity` | Beobachtbare Ähnlichkeit | enum string | yes | Synthetic observable similarity status; German value aliases are display-only. |
| `full_state_identity` | `full_state_identity` | Vollständige Zustandsidentität | enum string | yes | Declared full-state identity status; not an experimental result; German value aliases are display-only. |
| `equivalence_basis` | `equivalence_basis` | Grundlage der Äquivalenz | string | yes | Declared basis for method-demonstration equivalence; German value aliases are display-only. |
| `uncertainty_status` | `uncertainty_status` | Unsicherheitsstatus | enum string | yes | Synthetic-only or representation-choice-open uncertainty status; German value aliases are display-only. |
| `evidence_status` | `evidence_status` | Evidenzstatus | enum string | yes | Evidence status, fixed to `not_experimental`; German value aliases are display-only. |
| `demonstrator_controls.synthetic_record` | `synthetic_record` | Synthetischer Record | boolean | yes | Must be true for every record. |
| `demonstrator_controls.real_system_equivalence_claimed` | `real_system_equivalence_claimed` | Realsystem-Äquivalenz behauptet | boolean | yes | Must be false for every record. |
| `demonstrator_controls.experimental_support_claimed` | `experimental_support_claimed` | Experimentelle Stützung behauptet | boolean | yes | Must be false for every record. |
| `demonstrator_controls.physical_prediction_present` | `physical_prediction_present` | Physikalische Vorhersage vorhanden | boolean | yes | Must be false for every record. |
| `demonstrator_controls.used_as_contact_question_carrier` | `used_as_contact_question_carrier` | Als Kontaktfragen-Träger verwendet | boolean | yes | Must be true for every record. |
