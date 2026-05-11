# QSB-BRIDGE-SYNTH-01F Documentation Synthesis Map Field List

| field name | field type | field description |
|---|---|---|
| `readout_id` | string | Stable identifier for the documentation-ready readout row. |
| `documentation_title` | string | Short title suitable for documentation headings. |
| `documentation_readout` | string | Documentation-ready but defensive readout statement. |
| `support_level` | enum string | Support level inherited from 01E or integrated for 01F. |
| `supporting_artifacts` | string | Semicolon-separated artifact groups supporting the readout. |
| `supporting_tables` | string | Semicolon-separated concrete tables or documents used for the readout. |
| `boundary_artifacts` | string | Semicolon-separated artifacts carrying the required claim boundaries. |
| `required_claim_boundary` | string | Boundary that must travel with the readout. |
| `forbidden_overclaim` | string | Overclaim explicitly forbidden for this readout. |
| `documentation_use` | string | Suggested documentation contexts, such as `internal_method_note`, `masterchat_summary`, `public_cautious_background`, or `gap_register_only`. |
| `next_required_check` | string | Concrete next audit/check before stronger use. |
| `status` | enum string | Documentation status: `documentation_ready_with_boundary`, `documentation_ready_as_gap`, or `internal_only_until_further_binding`. |
