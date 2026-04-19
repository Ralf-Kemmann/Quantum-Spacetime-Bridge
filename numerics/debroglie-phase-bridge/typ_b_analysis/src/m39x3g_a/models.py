from __future__ import annotations

from pathlib import Path
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


# ---------------------------------------------------------------------------
# Base helpers
# ---------------------------------------------------------------------------

BLOCK_ID = "M.3.9x.3g.a"


class StrictBaseModel(BaseModel):
    """Base model with strict schema handling."""

    model_config = ConfigDict(
        extra="forbid",
        str_strip_whitespace=True,
        validate_assignment=True,
    )


# ---------------------------------------------------------------------------
# Config models
# ---------------------------------------------------------------------------


class ProjectConfig(StrictBaseModel):
    project_id: str = Field(min_length=1)
    project_stage: str = Field(min_length=1)
    analyst_mode: str = Field(min_length=1)
    notes: str = ""


class IdColumnsConfig(StrictBaseModel):
    dataset_id: str = Field(min_length=1)
    family_id: str = Field(min_length=1)
    window_id: str = Field(min_length=1)
    label_internal: str = Field(min_length=1)
    source_type: str = Field(min_length=1)
    control_family: str = Field(min_length=1)
    replicate_id: str = Field(min_length=1)


class SourceTypeValuesConfig(StrictBaseModel):
    original: str = Field(min_length=1)
    control: str = Field(min_length=1)


class DataConfig(StrictBaseModel):
    original_features_path: str = Field(min_length=1)
    control_features_path: str = Field(min_length=1)
    input_manifest_path: str = Field(min_length=1)
    id_columns: IdColumnsConfig
    source_type_values: SourceTypeValuesConfig

    @field_validator(
        "original_features_path",
        "control_features_path",
        "input_manifest_path",
    )
    @classmethod
    def must_not_be_directory(cls, value: str) -> str:
        if value.endswith("/"):
            raise ValueError("path must point to a file, not a directory")
        return value


class FeatureSpaceConfig(StrictBaseModel):
    feature_space_version: str = Field(min_length=1)
    feature_columns: list[str] = Field(min_length=1)
    required_feature_columns: list[str] = Field(default_factory=list)
    allow_additional_features: bool = True
    missing_value_policy: str = Field(min_length=1)
    row_filter_policy: str = Field(min_length=1)

    @model_validator(mode="after")
    def required_features_must_be_subset(self) -> "FeatureSpaceConfig":
        feature_set = set(self.feature_columns)
        missing = [f for f in self.required_feature_columns if f not in feature_set]
        if missing:
            raise ValueError(
                f"required_feature_columns not present in feature_columns: {missing}"
            )
        return self


class PreprocessingConfig(StrictBaseModel):
    scaling_method: str = Field(min_length=1)
    scaling_reference: str = Field(min_length=1)
    center: bool
    scale: bool
    clip_outliers: bool
    outlier_clip_quantiles: list[float] | None = None

    @model_validator(mode="after")
    def validate_clip_quantiles(self) -> "PreprocessingConfig":
        if self.clip_outliers:
            if not self.outlier_clip_quantiles or len(self.outlier_clip_quantiles) != 2:
                raise ValueError(
                    "outlier_clip_quantiles must contain exactly two values when "
                    "clip_outliers is true"
                )
            q_low, q_high = self.outlier_clip_quantiles
            if not (0.0 <= q_low < q_high <= 1.0):
                raise ValueError("outlier_clip_quantiles must satisfy 0 <= low < high <= 1")
        return self


class DistanceConfig(StrictBaseModel):
    distance_metric: str = Field(min_length=1)
    pairwise_engine: str = Field(min_length=1)
    distance_scope: str = Field(min_length=1)


class GroupingConfig(StrictBaseModel):
    original_target_groups: list[str] = Field(min_length=1)
    original_group_mapping: dict[str, list[str]]
    control_grouping_strategy: str = Field(min_length=1)
    minimum_group_size: int = Field(ge=1)

    @model_validator(mode="after")
    def validate_group_mapping(self) -> "GroupingConfig":
        missing_groups = [
            g for g in self.original_target_groups if g not in self.original_group_mapping
        ]
        if missing_groups:
            raise ValueError(
                f"original_group_mapping missing entries for groups: {missing_groups}"
            )
        for group_name, labels in self.original_group_mapping.items():
            if len(labels) == 0:
                raise ValueError(f"group '{group_name}' must have at least one label")
        return self


class MinMaxRuleConfig(StrictBaseModel):
    min: float
    max: float


class MinOnlyRuleConfig(StrictBaseModel):
    min: float


class TypeBRulesConfig(StrictBaseModel):
    version: str = Field(min_length=1)
    notes: str = ""

    distance_to_type_D: MinMaxRuleConfig
    spacing_cv: MinMaxRuleConfig
    grid_deviation_score: MinMaxRuleConfig
    simple_rigidity_surrogate: MinOnlyRuleConfig
    separation_margin: MinOnlyRuleConfig
    assignment_score: MinOnlyRuleConfig
    stability_score: MinOnlyRuleConfig
    separation_margin_ci_low: MinOnlyRuleConfig


class ReferenceRulesConfig(StrictBaseModel):
    version: str = Field(min_length=1)
    notes: str = ""

    original_separation_margin: MinOnlyRuleConfig
    original_stability_score: MinOnlyRuleConfig
    original_assignment_score: MinOnlyRuleConfig
    control_margin_quantile: MinOnlyRuleConfig


class ControlFamilyConfig(StrictBaseModel):
    id: str = Field(min_length=1)
    description: str = Field(min_length=1)
    expected_not_type_B: bool
    enabled: bool
    notes: str = ""

    @field_validator("id")
    @classmethod
    def control_family_must_not_be_original(cls, value: str) -> str:
        if value.lower() == "original":
            raise ValueError("control family id must not be 'original'")
        return value


class MetricsConfig(StrictBaseModel):
    primary_metrics: list[str] = Field(min_length=1)
    pooled_intra_definition: str = Field(min_length=1)
    separation_margin_definition: str = Field(min_length=1)
    separation_ratio_definition: str = Field(min_length=1)


class AssignmentConfig(StrictBaseModel):
    method: str = Field(min_length=1)
    cv_scheme: str = Field(min_length=1)
    report_confusion: bool


class ResamplingConfig(StrictBaseModel):
    enabled: bool
    scheme: Literal["bootstrap", "leave_one_out"]
    n_resamples: int = Field(ge=0)
    stratified: bool
    sample_fraction: float = Field(gt=0.0, le=1.0)
    with_replacement: bool
    confidence_interval: float = Field(gt=0.0, le=1.0)


class DecisionInvalidConditionsConfig(StrictBaseModel):
    require_minimum_two_enabled_control_families: bool
    require_identical_preprocessing_for_original_and_control: bool
    require_resampling: bool
    require_fixed_distance_metric: bool
    require_documented_feature_space: bool


class DecisionThresholdsConfig(StrictBaseModel):
    min_stability_score_for_supported: float = Field(ge=0.0)
    min_original_over_control_margin_delta: float
    max_control_typeB_like_fraction_for_supported: float = Field(ge=0.0, le=1.0)
    max_control_typeB_like_fraction_for_weak: float = Field(ge=0.0, le=1.0)

    @model_validator(mode="after")
    def validate_threshold_order(self) -> "DecisionThresholdsConfig":
        if (
            self.max_control_typeB_like_fraction_for_supported
            > self.max_control_typeB_like_fraction_for_weak
        ):
            raise ValueError(
                "supported threshold for control_typeB_like_fraction must be <= weak threshold"
            )
        return self


class DecisionRulesConfig(StrictBaseModel):
    version: str = Field(min_length=1)
    invalid_conditions: DecisionInvalidConditionsConfig
    thresholds: DecisionThresholdsConfig
    interpretation_logic: dict[str, str]

    @model_validator(mode="after")
    def validate_interpretation_logic(self) -> "DecisionRulesConfig":
        required_keys = {"supported", "weak", "ambiguous", "failed"}
        missing = required_keys - set(self.interpretation_logic.keys())
        if missing:
            raise ValueError(
                f"interpretation_logic missing required keys: {sorted(missing)}"
            )
        return self


class OutputsConfig(StrictBaseModel):
    base_dir: str = Field(min_length=1)
    write_input_manifest_copy: bool
    write_scaled_features: bool
    write_pairwise_distances: bool
    write_diagnostics_tables: bool
    write_resampling_tables: bool
    write_report_md: bool
    write_summary_json: bool


class PathsConfig(StrictBaseModel):
    diagnostics_dir: str = Field(min_length=1)
    resampling_dir: str = Field(min_length=1)
    report_path: str = Field(min_length=1)
    summary_path: str = Field(min_length=1)


class SoftwareEnvConfig(StrictBaseModel):
    python_version: str = ""
    numpy_version: str = ""
    pandas_version: str = ""
    sklearn_version: str = ""


class ReproducibilityConfig(StrictBaseModel):
    random_seed: int
    seed_list: list[int] = Field(min_length=1)
    software_env: SoftwareEnvConfig

    @model_validator(mode="after")
    def seed_consistency(self) -> "ReproducibilityConfig":
        if self.random_seed not in self.seed_list:
            raise ValueError("random_seed must be included in seed_list")
        return self


class AuditConfig(StrictBaseModel):
    created_by: str = Field(min_length=1)
    created_at: str = Field(min_length=1)
    last_modified_at: str = Field(min_length=1)
    notes: str = ""


class RunConfig(StrictBaseModel):
    block_id: Literal["M.3.9x.3g.a"]
    block_title: str = Field(min_length=1)
    run_id: str = Field(min_length=1)
    run_status: Literal["planned", "completed", "invalid", "failed_runtime"]

    project: ProjectConfig
    data: DataConfig
    feature_space: FeatureSpaceConfig
    preprocessing: PreprocessingConfig
    distance: DistanceConfig
    grouping: GroupingConfig
    type_b_rules: TypeBRulesConfig
    reference_rules: ReferenceRulesConfig
    control_families: list[ControlFamilyConfig] = Field(min_length=1)
    metrics: MetricsConfig
    assignment: AssignmentConfig
    resampling: ResamplingConfig
    decision_rules: DecisionRulesConfig
    outputs: OutputsConfig
    paths: PathsConfig
    reproducibility: ReproducibilityConfig
    audit: AuditConfig

    @property
    def enabled_control_families(self) -> list[ControlFamilyConfig]:
        return [cf for cf in self.control_families if cf.enabled]

    @model_validator(mode="after")
    def validate_enabled_controls(self) -> "RunConfig":
        if self.decision_rules.invalid_conditions.require_minimum_two_enabled_control_families:
            if len(self.enabled_control_families) < 2:
                raise ValueError("at least two enabled control families are required")
        if self.decision_rules.invalid_conditions.require_resampling and not self.resampling.enabled:
            raise ValueError("resampling must be enabled by decision rule")
        return self


# ---------------------------------------------------------------------------
# Input manifest model
# ---------------------------------------------------------------------------


class InputManifestRowModel(StrictBaseModel):
    record_id: int = Field(ge=1)
    run_id: str = Field(min_length=1)
    dataset_id: str = Field(min_length=1)

    source_type: Literal["original", "control"]
    control_family: str = Field(min_length=1)
    family_id: str = Field(min_length=1)
    window_id: str = Field(min_length=1)
    label_internal: str = Field(min_length=1)
    group_target: Literal["FSW", "AO", "control", "excluded"]

    replicate_id: int = Field(ge=0)
    is_original_reference: bool
    is_enabled: bool

    feature_space_version: str = Field(min_length=1)
    normalization_version: str = Field(min_length=1)
    input_file: str = Field(min_length=1)
    notes: str = ""

    @model_validator(mode="after")
    def validate_source_consistency(self) -> "InputManifestRowModel":
        if self.source_type == "original":
            if not self.is_original_reference:
                raise ValueError(
                    "original rows must have is_original_reference=true"
                )
            if self.group_target not in {"FSW", "AO", "excluded"}:
                raise ValueError(
                    "original rows must target FSW, AO, or excluded"
                )
            if self.control_family.lower() != "original":
                raise ValueError(
                    "original rows must have control_family='original'"
                )

        if self.source_type == "control":
            if self.is_original_reference:
                raise ValueError(
                    "control rows must have is_original_reference=false"
                )
            if self.group_target not in {"control", "excluded"}:
                raise ValueError(
                    "control rows must target control or excluded"
                )
            if self.control_family.lower() == "original":
                raise ValueError(
                    "control rows must not have control_family='original'"
                )

        return self


# ---------------------------------------------------------------------------
# Diagnostics models
# ---------------------------------------------------------------------------


class DiagnosticRowModel(StrictBaseModel):
    run_id: str = Field(min_length=1)
    block_id: Literal["M.3.9x.3g.a"]
    feature_space_version: str = Field(min_length=1)
    decision_rule_version: str = Field(min_length=1)

    source_group_left: Literal["original"]
    source_group_right: Literal["control"]
    control_family: str = Field(min_length=1)
    comparison_id: str = Field(min_length=1)

    n_left: int = Field(ge=0)
    n_right: int = Field(ge=0)

    mean_intra_left: float = Field(ge=0.0)
    mean_intra_right: float = Field(ge=0.0)
    pooled_intra_distance: float = Field(ge=0.0)
    mean_inter_distance: float = Field(ge=0.0)

    separation_margin: float
    separation_ratio: float = Field(ge=0.0)
    stability_score: float = Field(ge=0.0)
    assignment_score: float = Field(ge=0.0)

    type_B_like_pattern_detected: bool
    interpretation: str = Field(min_length=1)
    warning_flag: bool = False
    notes: str = ""

    @field_validator("control_family")
    @classmethod
    def control_family_must_not_be_original(cls, value: str) -> str:
        if value.lower() == "original":
            raise ValueError("control_family must not be 'original'")
        return value


class ResamplingRowModel(StrictBaseModel):
    run_id: str = Field(min_length=1)
    block_id: Literal["M.3.9x.3g.a"]
    control_family: str = Field(min_length=1)
    comparison_id: str = Field(min_length=1)

    resample_id: int = Field(ge=1)
    resample_scheme: Literal["bootstrap", "leave_one_out"]
    seed: int

    n_left: int = Field(ge=0)
    n_right: int = Field(ge=0)

    mean_intra_left: float = Field(ge=0.0)
    mean_intra_right: float = Field(ge=0.0)
    pooled_intra_distance: float = Field(ge=0.0)
    mean_inter_distance: float = Field(ge=0.0)

    separation_margin: float
    separation_ratio: float = Field(ge=0.0)
    assignment_score: float = Field(ge=0.0)

    type_B_like_pattern_detected: bool
    warning_flag: bool = False

    @field_validator("control_family")
    @classmethod
    def resampling_control_family_must_not_be_original(cls, value: str) -> str:
        if value.lower() == "original":
            raise ValueError("control_family must not be 'original'")
        return value


# ---------------------------------------------------------------------------
# Summary models
# ---------------------------------------------------------------------------


ResultLabel = Literal[
    "type_B_exclusion_supported",
    "type_B_exclusion_weak",
    "type_B_exclusion_ambiguous",
    "type_B_exclusion_failed",
    "not_evaluated",
]


RunStatus = Literal["planned", "completed", "invalid", "failed_runtime"]


class OriginalReferenceSummary(StrictBaseModel):
    dataset_count: int = Field(ge=0)
    group_labels: list[str] = Field(min_length=1)
    n_rows: int = Field(ge=0)
    scaling_method: str = Field(min_length=1)
    distance_metric: str = Field(min_length=1)


class ControlFamilyResultSummary(StrictBaseModel):
    control_family: str = Field(min_length=1)
    enabled: bool
    n_instances: int = Field(ge=0)
    n_rows: int = Field(ge=0)

    mean_intra_distance: float | None = None
    mean_inter_distance: float | None = None
    pooled_intra_distance: float | None = None

    separation_margin_mean: float | None = None
    separation_margin_ci: tuple[float, float] | None = None
    separation_ratio_mean: float | None = None

    stability_score_mean: float | None = None
    stability_score_ci: tuple[float, float] | None = None
    assignment_score_mean: float | None = None

    type_B_like_pattern_detected: bool
    interpretation: str = Field(min_length=1)
    warnings: list[str] = Field(default_factory=list)

    @field_validator("control_family")
    @classmethod
    def summary_control_family_must_not_be_original(cls, value: str) -> str:
        if value.lower() == "original":
            raise ValueError("control_family must not be 'original'")
        return value


class AggregateMetricsSummary(StrictBaseModel):
    original_separation_margin: float | None = None
    original_stability_score: float | None = None
    original_assignment_score: float | None = None
    control_typeB_like_fraction: float | None = Field(default=None, ge=0.0, le=1.0)
    original_vs_control_margin_delta: float | None = None


class DecisionTraceSummary(StrictBaseModel):
    thresholds_used: dict[str, Any] = Field(default_factory=dict)
    supported_conditions_met: bool | None = None
    weak_conditions_met: bool | None = None
    ambiguous_conditions_met: bool | None = None
    failed_conditions_met: bool | None = None


class ReproducibilitySummary(StrictBaseModel):
    random_seed: int | None = None
    seed_list: list[int] = Field(default_factory=list)
    n_resamples: int | None = Field(default=None, ge=0)
    software_env: dict[str, str] = Field(default_factory=dict)


class SummaryModel(StrictBaseModel):
    block_id: Literal["M.3.9x.3g.a"]
    block_title: str = Field(min_length=1)
    run_id: str = Field(min_length=1)
    run_status: RunStatus

    feature_space_version: str = Field(min_length=1)
    decision_rule_version: str = Field(min_length=1)

    result_label: ResultLabel
    overall_interpretation: str = Field(min_length=1)

    original_reference: OriginalReferenceSummary
    control_family_results: list[ControlFamilyResultSummary]
    aggregate_metrics: AggregateMetricsSummary
    decision_trace: DecisionTraceSummary | None = None

    warnings: list[str] = Field(default_factory=list)
    errors: list[str] = Field(default_factory=list)
    reproducibility: ReproducibilitySummary


# ---------------------------------------------------------------------------
# Small utility helpers
# ---------------------------------------------------------------------------


def validate_run_id_consistency(
    manifest_rows: list[InputManifestRowModel],
    diagnostics_rows: list[DiagnosticRowModel] | None = None,
    resampling_rows: list[ResamplingRowModel] | None = None,
    summary: SummaryModel | None = None,
) -> None:
    """
    Lightweight cross-object validation helper.

    Raises:
        ValueError: if inconsistent run_ids are found.
    """
    run_ids: set[str] = set()

    for row in manifest_rows:
        run_ids.add(row.run_id)

    if diagnostics_rows:
        for row in diagnostics_rows:
            run_ids.add(row.run_id)

    if resampling_rows:
        for row in resampling_rows:
            run_ids.add(row.run_id)

    if summary is not None:
        run_ids.add(summary.run_id)

    if len(run_ids) > 1:
        raise ValueError(f"inconsistent run_ids detected: {sorted(run_ids)}")


def validate_feature_space_consistency(
    manifest_rows: list[InputManifestRowModel],
    config: RunConfig,
) -> None:
    """
    Ensures all manifest rows match the configured feature space version.
    """
    expected = config.feature_space.feature_space_version
    mismatches = [
        row.dataset_id
        for row in manifest_rows
        if row.feature_space_version != expected
    ]
    if mismatches:
        raise ValueError(
            f"manifest rows with mismatching feature_space_version: {mismatches}"
        )
