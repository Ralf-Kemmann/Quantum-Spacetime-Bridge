# QSB-BRIDGE-SYNTH-01B Cross-Test Pattern Matrix Field List

| field name | field type | field description |
|---|---|---|
| `bridge_property_group` | string | Curated bridge-property group used to organize the 01B synthesis row. |
| `synthesis_question` | string | Defensive question the row asks across the 01A inventory and marker map. |
| `supporting_blocks` | string | Semicolon-separated `block_id` list from the 01A existing-result index that supports the working readout. |
| `supporting_markers` | string | Semicolon-separated marker names from the 01A marker-axis map or 01A inventory. |
| `limiting_blocks` | string | Semicolon-separated 01A block IDs that define boundaries, counterexamples, or failure modes. |
| `known_failure_modes` | string | Condensed failure modes drawn from the 01A marker-axis map and result-note boundaries. |
| `open_gap` | string | Unresolved extraction, harmonization, or interpretation gap that remains after 01B. |
| `provisional_pattern_readout` | string | Cautious synthesis readout; an organizing interpretation, not a proof claim. |
| `claim_boundary` | string | Explicit statement of what the row does not establish. |
| `next_check` | string | Concrete follow-up extraction or audit step for later work, without implying new numerics. |
