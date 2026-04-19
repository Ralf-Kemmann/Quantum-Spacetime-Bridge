
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Literal


KernelMode = Literal["abs", "positive", "negative"]
WindowType = Literal["gaussian"]
CenterMode = Literal["fixed", "coarse_peak"]
Phi0Mode = Literal["zero", "random", "custom"]
DispersionMode = Literal["scaled_free"]
KbarAverageMode = Literal["weighted_x_average"]


@dataclass(slots=True)
class ProjectConfig:
    run_id: str
    tag: str
    seed: int
    output_root: str


@dataclass(slots=True)
class PhysicsConfig:
    hbar: float = 1.0
    m: float = 1.0


@dataclass(slots=True)
class WindowConfig:
    type: WindowType = "gaussian"
    sigma: float = 8.0
    normalize_weights: bool = True


@dataclass(slots=True)
class GridConfig:
    x_min: float = -40.0
    x_max: float = 40.0
    nx: int = 4001
    window: WindowConfig = field(default_factory=WindowConfig)


@dataclass(slots=True)
class TimeScanConfig:
    enabled: bool = True
    t_values: List[float] = field(default_factory=lambda: [0.0, 2.0, 5.0, 10.0, 20.0, 40.0])


@dataclass(slots=True)
class AlphaCoarseConfig:
    alpha_min: float = 0.3
    alpha_max: float = 3.0
    alpha_step: float = 0.1


@dataclass(slots=True)
class AlphaRefineConfig:
    enabled: bool = True
    center_mode: CenterMode = "fixed"
    fixed_center: float = 1.6
    half_width: float = 0.3
    alpha_step: float = 0.02


@dataclass(slots=True)
class AlphaScanConfig:
    coarse: AlphaCoarseConfig = field(default_factory=AlphaCoarseConfig)
    refine: AlphaRefineConfig = field(default_factory=AlphaRefineConfig)


@dataclass(slots=True)
class PFamilyConfig:
    description: str
    p_values: List[float]


@dataclass(slots=True)
class PSetsConfig:
    active_families: List[str] = field(default_factory=lambda: ["P0", "P1", "P2", "P3"])
    families: Dict[str, PFamilyConfig] = field(
        default_factory=lambda: {
            "P0": PFamilyConfig(
                description="symmetric reference",
                p_values=[-3.0, -2.0, -1.0, 0.0, 1.0, 2.0, 3.0],
            ),
            "P1": PFamilyConfig(
                description="mild asymmetric",
                p_values=[-3.0, -2.0, -1.0, 0.0, 1.0, 2.0, 4.0],
            ),
            "P2": PFamilyConfig(
                description="strong asymmetric",
                p_values=[-4.0, -2.0, -1.0, 0.0, 1.0, 3.0, 6.0],
            ),
            "P3": PFamilyConfig(
                description="affine asymmetric",
                p_values=[-3.0, -1.9, -0.8, 0.0, 1.2, 2.7, 4.4],
            ),
        }
    )


@dataclass(slots=True)
class DispersionConfig:
    mode: DispersionMode = "scaled_free"
    formula: str = "omega_i = alpha * p_i^2 / (2*m)"


@dataclass(slots=True)
class PhasesConfig:
    phi0_mode: Phi0Mode = "zero"
    phi0_seed: int = 123
    dispersion: DispersionConfig = field(default_factory=DispersionConfig)


@dataclass(slots=True)
class KbarAverageConfig:
    mode: KbarAverageMode = "weighted_x_average"


@dataclass(slots=True)
class SignPreservingConfig:
    enabled: bool = True
    zero_tolerance: float = 1.0e-12


@dataclass(slots=True)
class KernelConfig:
    build_kbar: bool = True
    kbar_average: KbarAverageConfig = field(default_factory=KbarAverageConfig)
    sign_preserving: SignPreservingConfig = field(default_factory=SignPreservingConfig)


@dataclass(slots=True)
class ThetaScanConfig:
    enabled: bool = True
    theta_values: List[float] = field(default_factory=lambda: [0.02, 0.03, 0.05])


@dataclass(slots=True)
class WeightedLayerConfig:
    enabled: bool = True
    metrics: List[str] = field(
        default_factory=lambda: [
            "natural_connectivity",
            "weighted_clustering",
            "global_efficiency",
        ]
    )


@dataclass(slots=True)
class GraphsConfig:
    theta_scan: ThetaScanConfig = field(default_factory=ThetaScanConfig)
    adjacency_modes: List[KernelMode] = field(default_factory=lambda: ["abs", "positive", "negative"])
    weighted_layer: WeightedLayerConfig = field(default_factory=WeightedLayerConfig)


@dataclass(slots=True)
class SourceTestConfig:
    enabled: bool = True
    measures: List[str] = field(
        default_factory=lambda: [
            "var_dphi_x",
            "mean_cos_dphi",
            "mean_abs_cos_dphi",
            "kbar_ij",
            "sign_fraction",
            "lambda_max_kpos",
            "lambda_max_kneg",
        ]
    )


@dataclass(slots=True)
class ReadoutTestConfig:
    enabled: bool = True
    measures: List[str] = field(
        default_factory=lambda: [
            "chi",
            "rho_pos",
            "rho_neg",
            "lambda_max_pos",
            "lambda_max_neg",
            "lambda_max_abs",
            "lambda2_abs",
            "weighted_clustering_abs",
            "natural_connectivity_abs",
            "global_efficiency_abs",
        ]
    )


@dataclass(slots=True)
class PeakDetectionConfig:
    edge_exclusion_bins: int = 1
    prominence_mode: str = "median_baseline"
    source_peak_band: List[float] = field(default_factory=lambda: [1.4, 1.8])
    readout_peak_band: List[float] = field(default_factory=lambda: [1.4, 1.8])
    coherence_tol_fine: float = 0.15
    robust_fraction_min: float = 0.70


@dataclass(slots=True)
class ControlsConfig:
    require_t0_control: bool = True
    require_nontrivial_p_asymmetry: bool = True
    finite_fraction_min: float = 1.0
    allow_edge_peaks: bool = False


@dataclass(slots=True)
class LabelsConfig:
    source_labels: List[str] = field(default_factory=lambda: ["Q0", "Q1", "Q2", "Q3"])
    robustness_labels: List[str] = field(default_factory=lambda: ["R0", "R1", "R2", "R3"])


@dataclass(slots=True)
class M33V0Config:
    project: ProjectConfig
    physics: PhysicsConfig = field(default_factory=PhysicsConfig)
    grid: GridConfig = field(default_factory=GridConfig)
    time_scan: TimeScanConfig = field(default_factory=TimeScanConfig)
    alpha_scan: AlphaScanConfig = field(default_factory=AlphaScanConfig)
    p_sets: PSetsConfig = field(default_factory=PSetsConfig)
    phases: PhasesConfig = field(default_factory=PhasesConfig)
    kernel: KernelConfig = field(default_factory=KernelConfig)
    graphs: GraphsConfig = field(default_factory=GraphsConfig)
    source_test: SourceTestConfig = field(default_factory=SourceTestConfig)
    readout_test: ReadoutTestConfig = field(default_factory=ReadoutTestConfig)
    peak_detection: PeakDetectionConfig = field(default_factory=PeakDetectionConfig)
    controls: ControlsConfig = field(default_factory=ControlsConfig)
    labels: LabelsConfig = field(default_factory=LabelsConfig)

    def validate(self) -> None:
        if self.grid.nx < 3:
            raise ValueError("grid.nx must be >= 3")
        if self.grid.x_max <= self.grid.x_min:
            raise ValueError("grid.x_max must be > grid.x_min")
        if self.alpha_scan.coarse.alpha_step <= 0:
            raise ValueError("alpha_scan.coarse.alpha_step must be > 0")
        if self.alpha_scan.refine.enabled and self.alpha_scan.refine.alpha_step <= 0:
            raise ValueError("alpha_scan.refine.alpha_step must be > 0")
        if self.controls.require_t0_control and 0.0 not in self.time_scan.t_values:
            raise ValueError("t=0.0 must be included when require_t0_control=True")
        missing = set(self.p_sets.active_families) - set(self.p_sets.families.keys())
        if missing:
            raise ValueError(f"Unknown active p-family entries: {sorted(missing)}")
        for name, fam in self.p_sets.families.items():
            if len(fam.p_values) < 2:
                raise ValueError(f"p-family {name} must contain at least 2 p_values")
        if self.peak_detection.coherence_tol_fine < 0:
            raise ValueError("peak_detection.coherence_tol_fine must be >= 0")
        if not 0 < self.peak_detection.robust_fraction_min <= 1:
            raise ValueError("peak_detection.robust_fraction_min must be in (0, 1]")


def default_config() -> M33V0Config:
    cfg = M33V0Config(
        project=ProjectConfig(
            run_id="M33_V0_alpha_peak_robustness",
            tag="phase_source_vs_readout",
            seed=42,
            output_root="./runs/M33_V0_alpha_peak_robustness",
        )
    )
    cfg.validate()
    return cfg
