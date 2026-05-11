# QSB-BRIDGE-SYNTH-01D Proxy Marker Source Binding Field List

| field name | field type | field description |
|---|---|---|
| `marker_name` | string | Marker or proxy marker name. |
| `source_block_id` | string | Source block identifier or `uncertain`. |
| `source_path` | string | Repository-relative source path, multiple paths, or `not_extracted`. |
| `source_column_or_section` | string | Concrete source column, metric name, or result-note section used for binding. |
| `binding_status` | string | Binding status such as `bound`, `result_note_bound`, `gap_marker_unbound`, or `conceptually_mapped_not_source_bound`. |
| `bridge_property` | string | Bridge-property bucket from 01A/01C mapping. |
| `known_failure_mode` | string | Known way the marker can mislead. |
| `interpretation_limit` | string | Defensive limit on interpreting the marker. |
| `evidence_weight` | enum string | Evidence weight: `source_bound`, `result_note_bound`, `concept_only`, or `gap_only`. |
| `open_gap` | string | Remaining source-binding gap. |
| `next_action` | string | Concrete follow-up action for later work. |
| `notes` | string | Additional audit notes. |
