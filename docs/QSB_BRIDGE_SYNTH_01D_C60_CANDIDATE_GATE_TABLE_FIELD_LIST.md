# QSB-BRIDGE-SYNTH-01D C60 Candidate Gate Table Field List

| field name | field type | field description |
|---|---|---|
| `candidate_id` | string | Candidate identifier from the FU02g5 candidate tables. |
| `raw_index` | integer or `not_extracted` | Raw index associated with the candidate. |
| `candidate_nodes` | string | Semicolon-separated candidate node set. |
| `near_distance` | integer or `not_extracted` | Coarse near-distance screening value. |
| `exact_match` | boolean or `not_extracted` | Whether the candidate is marked as exact in the source tables. |
| `uncolored_isomorphic_to_reference` | boolean or `not_extracted` | Untyped graph isomorphism status against the reference. |
| `face_type_preserving_isomorphic_to_reference` | boolean or `not_extracted` | Typed face-preserving isomorphism status against the reference. |
| `mapping_count` | integer or `not_extracted` | Count of valid typed mappings. |
| `role_transport_allowed` | boolean or `not_extracted` | Role-transport gate from FU02g5e2-style classification. |
| `role_transport_allowed_under_g5c` | boolean or `not_extracted` | Conservative G5C role-transport gate from G5G2. |
| `node_set_agreement` | boolean or `not_extracted` | Whether replayed/scaffold nodes match expected nodes in G5G2. |
| `edge_set_agreement` | boolean or `not_extracted` | Whether replayed/scaffold edges match expected edges in G5G2. |
| `classification_primary` | string | Primary candidate classification label. |
| `candidate_gate_status` | enum string | Curated gate status such as `near_screen_only`, `exact_positive_control`, or `coarse_signature_degeneracy_stress_case`. |
| `candidate_gate_basis` | string | Short explanation of the gate status. |
| `claim_boundary` | string | Defensive boundary for interpreting the candidate row. |
| `source_files` | string | Semicolon-separated source files used for the row. |
| `notes` | string | Additional audit notes. |
