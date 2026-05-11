# QSB-BRIDGE-SYNTH-01E Readout Claim Map Field List

| field name | field type | field description |
|---|---|---|
| `readout_id` | string | Stable identifier for the conservative 01E readout. |
| `bridge_property_readout` | string | Defensive bridge-property readout text. |
| `supporting_01b_group` | string | 01B bridge-property group supporting the readout. |
| `supporting_01c_roles` | string | Semicolon-separated 01C evidence roles relevant to the readout. |
| `supporting_01d_tables` | string | Semicolon-separated 01D tables supporting or bounding the readout. |
| `support_level` | enum string | Support level: `conservative_inventory_support`, `source_bound_support`, `gate_bound_support`, `boundary_only`, or `gap_only`. |
| `main_supporting_blocks` | string | Semicolon-separated source blocks supporting the readout. |
| `main_limiting_blocks` | string | Semicolon-separated blocks or labels limiting the readout. |
| `required_claim_boundary` | string | Boundary that must accompany the readout. |
| `forbidden_overclaim` | string | Overclaim that this readout explicitly forbids. |
| `next_required_check` | string | Concrete next audit or extraction check. |
| `notes` | string | Additional audit note for the readout. |
