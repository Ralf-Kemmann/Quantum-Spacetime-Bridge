# QSB-BRIDGE-SYNTH-01A Existing Result Index Field List

| field name | field type | field description |
|---|---|---|
| `block_id` | string | Short identifier of the existing result or control block. |
| `source_path` | string | Repository-relative path to the inventoried source artifact. |
| `artifact_type` | string | Artifact class, such as `result_note`, `summary_csv`, `summary_json`, `candidate_csv`, or `feature_table`. |
| `run_id` | string | Run identifier or output directory name when extractable; otherwise `not_extracted`. |
| `test_family` | string | Broad test family represented by the artifact. |
| `control_axis` | string | Main controlled axis, null family, construction axis, or replay/certification axis. |
| `fixed_variable` | string | Variable held fixed in the artifact's comparison design, when extractable. |
| `varied_variable` | string | Variable swept, dropped, randomized, or otherwise varied, when extractable. |
| `primary_marker` | string | Main marker or decision label most relevant for later bridge-pattern synthesis. |
| `secondary_markers` | string | Semicolon-separated related markers present or implied by the artifact. |
| `status_label` | string | Existing result status or decision label when extractable; otherwise `not_extracted` or `uncertain`. |
| `bridge_property` | string | Provisional bridge-property bucket for synthesis mapping. |
| `claim_boundary` | string | Explicit limit on what the artifact can support. |
| `notes` | string | Short audit note explaining why the artifact was included or how it should be read. |
