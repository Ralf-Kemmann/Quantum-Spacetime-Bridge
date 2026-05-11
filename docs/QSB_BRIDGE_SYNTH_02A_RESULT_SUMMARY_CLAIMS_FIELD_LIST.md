# QSB-BRIDGE-SYNTH-02A Result Summary Claims Field List

## Field: claim_id

Field type: string identifier

Field description: Stable claim identifier for one 02A result-summary claim.

## Field: result_statement

Field type: text

Field description: Compact documentation-level statement of the result being summarized.

## Field: supporting_readout

Field type: text

Field description: The 01E to 01G readout, visual-map node, or integrated readout that supports the claim.

## Field: support_basis

Field type: text

Field description: Existing artifact basis used for the claim. This field names prior synthesis documents or tables, not new tests.

## Field: support_level

Field type: controlled string

Field description: Conservative support class for the claim, using documentation_synthesis, gate_bound_support, source_bound_support, conservative_inventory_support, boundary_only, or gap_only.

## Field: claim_status

Field type: controlled string

Field description: Documentation status of the claim, using documentation_ready_with_boundary, boundary_only, gap_register_only, or internal_method_result.

## Field: required_boundary

Field type: text

Field description: Required claim boundary that must remain attached whenever the claim is reused.

## Field: forbidden_overclaim

Field type: text

Field description: Overclaim language or interpretation explicitly excluded by the 02A summary.

## Field: next_research_move

Field type: text

Field description: Conservative next step needed to strengthen, bind, or preserve the claim without changing its current boundary.

## Field: documentation_use

Field type: text

Field description: Suggested documentation context for the claim, such as internal method note, masterchat summary, cautious documentation, or gap register.

## Field: notes

Field type: text

Field description: Additional clarification about how the claim should be read or protected.
