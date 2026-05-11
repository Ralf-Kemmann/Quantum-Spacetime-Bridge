# QSB-BRIDGE-SYNTH-01A Marker Axis Map Field List

| field name | field type | field description |
|---|---|---|
| `marker_name` | string | Marker, metric, decision label, or diagnostic variable name. |
| `marker_type` | string | Marker category, such as decision marker, containment marker, isomorphism marker, or graph metric. |
| `bridge_property` | string | Provisional bridge-property bucket the marker may inform. |
| `sensitive_to` | string | Semicolon-separated factors that can change the marker. |
| `control_needed` | string | Semicolon-separated controls needed before interpreting the marker. |
| `known_failure_mode` | string | Known way the marker can mislead or be over-interpreted. |
| `relevant_blocks` | string | Semicolon-separated block identifiers where the marker is relevant or observed. |
| `interpretation_limit` | string | Boundary on what the marker can support. |
| `notes` | string | Short audit note for later synthesis use. |
