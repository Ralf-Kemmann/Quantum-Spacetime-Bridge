# QSB-BRIDGE-SYNTH-01D Replay Certification Ladder Field List

| field name | field type | field description |
|---|---|---|
| `candidate_id` | string | Candidate identifier from FU02g5 replay/certification artifacts. |
| `raw_index` | integer or `not_extracted` | Candidate raw index. |
| `inside_fu02g4c_logged_window` | boolean or `not_extracted` | Whether G5G places the candidate inside an FU02g4c logged window. |
| `matching_fu02g4c_log_file` | string | Matching FU02g4c log path or `not_extracted`. |
| `g5g_replay_certification_status` | string | G5G replay certification status. |
| `g5g_replay_certification_basis` | string | Textual basis for G5G certification status. |
| `g5g2_per_index_photo_status` | string | G5G2 per-index photo/scaffold status. |
| `node_set_agreement` | boolean or `not_extracted` | G5G2 node-set agreement status. |
| `edge_set_agreement` | boolean or `not_extracted` | G5G2 edge-set agreement status. |
| `full_fu02g4c_replay_certification` | boolean | Whether full FU02g4c replay certification is marked true. |
| `original_enumerator_rerun_certified` | boolean | Whether the original enumerator rerun is certified. |
| `stage3a_gate_status` | string | Stage3A wrapper gate status. |
| `certification_level` | enum string | Curated level such as `partial_certification`, `not_certified`, or `full_raw_order_replay_certified`. |
| `certification_basis` | string | Short explanation for the certification level. |
| `claim_boundary` | string | Defensive boundary for the certification row. |
| `source_files` | string | Semicolon-separated source files used for the row. |
| `notes` | string | Additional audit notes. |
