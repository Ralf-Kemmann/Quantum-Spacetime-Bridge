# QSB-BRIDGE-SYNTH-03A BMC12 Per-Variant Binding Field List

## Field: binding_id

Field type: string identifier

Field description: Stable identifier for one 03A source-binding row.

## Field: source_block

Field type: controlled string

Field description: Source block for the bound artifact, using BMC12, BMC12b, BMC12c, BMC12e, BMC12f, or uncertain.

## Field: source_path

Field type: path string

Field description: Concrete existing source artifact used by the binding row.

## Field: artifact_type

Field type: text

Field description: Type of source artifact, such as csv_summary, csv_decision_summary, csv_variant_summary, readout_md, or result_note_bound.

## Field: variant_id

Field type: text

Field description: Case, variant, threshold group, or compact variant set named by the row.

## Field: variant_family

Field type: controlled string

Field description: Variant family, using baseline, leave_one_out, density_matched, backbone_aware_matched, threshold_variant, off_backbone_arm, backbone_arm, uncertain, or not_extracted.

## Field: threshold_or_control_setting

Field type: text

Field description: Threshold, edge-count, matched-size, or decision-control setting associated with the row.

## Field: arm_or_comparison

Field type: text

Field description: Arm, graph comparison, or decision comparison represented by the row.

## Field: primary_marker

Field type: text

Field description: Main marker or status field bound by the row.

## Field: secondary_markers

Field type: text

Field description: Additional markers or fields used to interpret the binding row.

## Field: bound_source_field

Field type: text

Field description: Concrete source field names when safely extractable; otherwise not_extracted.

## Field: bound_status_or_value

Field type: text

Field description: Bound value, status, or cautious qualitative readout from the existing source artifact.

## Field: supports_readout

Field type: text

Field description: How the row supports the 02A/02E feature/backbone sensitivity readout.

## Field: limits_readout

Field type: text

Field description: How the row limits, qualifies, or bounds the feature/backbone sensitivity readout.

## Field: claim_boundary

Field type: text

Field description: Required claim boundary for the row.

## Field: open_gap

Field type: text

Field description: Remaining gap, uncertainty, missing extraction, or method-dependence associated with the row.

## Field: next_action

Field type: text

Field description: Conservative next action for later source binding or documentation.

## Field: notes

Field type: text

Field description: Additional clarification about source status, interpretation, or caution.
