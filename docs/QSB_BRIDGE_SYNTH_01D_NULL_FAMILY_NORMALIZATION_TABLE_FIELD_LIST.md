# QSB-BRIDGE-SYNTH-01D Null Family Normalization Table Field List

| field name | field type | field description |
|---|---|---|
| `block_id` | string | Source block identifier from 01A/01C context. |
| `source_path` | string | Repository-relative source path. |
| `test_family` | string | Test family or diagnostic family. |
| `control_axis` | string | Main control axis for the null/control family. |
| `null_family_or_control_family` | string | Null family or control family name. |
| `preserved_variables` | string | Variables preserved by the family, or `not_extracted`. |
| `broken_or_varied_variables` | string | Variables broken, varied, randomized, or excluded, or `not_extracted`. |
| `primary_marker` | string | Primary marker linked to the family. |
| `secondary_markers` | string | Semicolon-separated secondary markers. |
| `status_or_interpretation_label` | string | Source status or interpretation label. |
| `normalization_status` | string | Binding state, such as `source_column_bound`, `partially_source_bound`, or `result_note_bound`. |
| `claim_boundary` | string | Defensive interpretation boundary. |
| `open_gap` | string | Remaining extraction or normalization gap. |
| `notes` | string | Additional audit notes. |
