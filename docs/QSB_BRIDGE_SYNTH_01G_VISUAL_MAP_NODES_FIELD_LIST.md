# QSB-BRIDGE-SYNTH-01G Visual Map Nodes Field List

| field name | field type | field description |
|---|---|---|
| `node_id` | string | Stable node identifier used by the visual map. |
| `node_label` | string | Human-readable node label. |
| `node_type` | enum string | Node category, such as `synthesis_stage`, `readout`, `guardrail`, `integration`, or `gap_register`. |
| `source_block` | string | Source QSB-BRIDGE-SYNTH block or artifact family for the node. |
| `documentation_role` | string | Role the node plays in the documentation map. |
| `claim_boundary` | string | Required boundary attached to the node. |
| `notes` | string | Additional audit notes for the node. |
