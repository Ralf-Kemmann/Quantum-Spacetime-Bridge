# QSB-BRIDGE-SYNTH-01C Evidence Binding Table Field List

| field name | field type | field description |
|---|---|---|
| `bridge_property_group` | string | One of the eight 01B bridge-property groups to which the evidence row is bound. |
| `source_block_id` | string | `block_id` copied from the 01A existing-result index. |
| `source_path` | string | Repository-relative source path copied from the 01A existing-result index. |
| `artifact_type` | string | Artifact class copied or directly derived from the 01A existing-result index. |
| `evidence_role` | enum string | Evidence role for the row: `support`, `limitation`, `boundary`, `gap`, or `control`. |
| `bound_marker` | string | Marker bound from 01A/01B, or `not_extracted` if no marker can be safely named. |
| `bound_source_field` | string | Concrete 01A/01B field, marker, source column, or result-note section used for binding. |
| `bound_status_or_value` | string | Status label, marker list, boundary text, or value available from 01A/01B. |
| `supports_pattern` | string | How this row supports the 01B pattern, if at all. |
| `limits_pattern` | string | How this row limits or qualifies the 01B pattern. |
| `claim_boundary` | string | Defensive boundary on what the row does not establish. |
| `open_extraction_gap` | string | Honest statement of any remaining extraction gap or missing row-level binding. |
| `next_action` | string | Concrete follow-up extraction or audit step for later work. |
| `notes` | string | Short audit note explaining the binding choice. |
