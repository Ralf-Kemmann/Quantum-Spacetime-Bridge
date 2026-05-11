# QSB-BRIDGE-SYNTH-01G Visual Map Edges Field List

| field name | field type | field description |
|---|---|---|
| `edge_id` | string | Stable edge identifier used by the visual map. |
| `source_node` | string | Source node identifier from the nodes table. |
| `target_node` | string | Target node identifier from the nodes table. |
| `edge_type` | enum string | Edge category, such as `synthesis_flow`, `supports_readout`, `bounded_by`, `integrates`, or `excludes_overclaim`. |
| `edge_label` | string | Human-readable edge label. |
| `claim_boundary` | string | Boundary attached to the edge. |
| `notes` | string | Additional audit notes for the edge. |
