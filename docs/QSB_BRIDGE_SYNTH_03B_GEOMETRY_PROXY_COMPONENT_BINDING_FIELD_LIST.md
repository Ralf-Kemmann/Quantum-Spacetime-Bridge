# QSB-BRIDGE-SYNTH-03B Geometry Proxy Component Binding Field List

## Field: binding_id

Field type: string identifier

Field description: Stable identifier for one 03B geometry-proxy component binding row.

## Field: source_block

Field type: controlled string

Field description: Source block for the bound artifact, using BMC15, BMC15b, BMC15e, BMC15h, BMC14d, BMC14e, or uncertain.

## Field: source_path

Field type: path string

Field description: Concrete existing source artifact used by the binding row.

## Field: artifact_type

Field type: text

Field description: Type of source artifact, such as result_note, summary_csv, summary_csv_refined, or binding_table.

## Field: proxy_component

Field type: controlled string

Field description: Geometry-proxy component or protected marker class being bound.

## Field: marker_name

Field type: text

Field description: Specific marker, metric, or source-level name used in the artifact.

## Field: source_column_or_section

Field type: text

Field description: Concrete source columns or result-note sections used for the binding; uses not_extracted when no safe column or section was found.

## Field: bound_status_or_value

Field type: text

Field description: Bound value, status, or cautious qualitative source readout from the existing artifact.

## Field: binding_status

Field type: controlled string

Field description: Binding status, using source_bound, result_note_bound, concept_only, gap_only, not_extracted, or uncertain.

## Field: support_role

Field type: controlled string

Field description: Role of the row in the geometry-proxy readout, using supports_proxy_readability, bounds_proxy_readability, gap_marker_exclusion, control_context, limitation, or not_evidence.

## Field: limits_readout

Field type: text

Field description: How the row limits, qualifies, or bounds the geometry-proxy readout.

## Field: claim_boundary

Field type: text

Field description: Required claim boundary for reuse of the row.

## Field: open_gap

Field type: text

Field description: Remaining gap, uncertainty, missing extraction, alias issue, or method-dependence associated with the row.

## Field: next_action

Field type: text

Field description: Conservative next action for later source binding or documentation.

## Field: notes

Field type: text

Field description: Additional clarification about source status, interpretation, or caution.
