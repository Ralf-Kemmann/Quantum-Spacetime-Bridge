
#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import logging
import math
from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Iterable, List, Tuple

import numpy as np
import pandas as pd
import yaml

from config_schema import (
    AlphaCoarseConfig,
    AlphaRefineConfig,
    AlphaScanConfig,
    ControlsConfig,
    DispersionConfig,
    GraphsConfig,
    GridConfig,
    KbarAverageConfig,
    KernelConfig,
    LabelsConfig,
    M33V0Config,
    PFamilyConfig,
    PSetsConfig,
    PeakDetectionConfig,
    PhasesConfig,
    PhysicsConfig,
    ProjectConfig,
    ReadoutTestConfig,
    SignPreservingConfig,
    SourceTestConfig,
    ThetaScanConfig,
    TimeScanConfig,
    WeightedLayerConfig,
    WindowConfig,
)
from columns_m33_v0 import (
    ALPHA_SCAN_COLUMNS,
    ALPHA_SCAN_SUMMARY_COLUMNS,
    COMBINED_DECISION_TABLE_COLUMNS,
    KERNEL_SIGN_STATS_COLUMNS,
    PHASE_PAIR_STATS_COLUMNS,
    ROBUSTNESS_TABLE_COLUMNS,
    SOURCE_PEAK_SUMMARY_COLUMNS,
    SOURCE_READOUT_ALIGNMENT_COLUMNS,
)

LOGGER = logging.getLogger("m33_v0_runner")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="V.0 + M.3.3 runner skeleton")
    parser.add_argument(
        "--config",
        type=str,
        default="configs/config_m33_v0.yaml",
        help="Path to YAML config.",
    )
    parser.add_argument(
        "--project-root",
        type=str,
        default=".",
        help="Project root containing src/, configs/, runs/ ...",
    )
    parser.add_argument(
        "--init-only",
        action="store_true",
        help="Only initialize output files and exit.",
    )
    parser.add_argument(
        "--coarse-only",
        action="store_true",
        help="Skip refine pass.",
    )
    return parser.parse_args()


def load_config(path: str | Path) -> M33V0Config:
    with open(path, "r", encoding="utf-8") as handle:
        raw = yaml.safe_load(handle)

    cfg = M33V0Config(
        project=ProjectConfig(**raw["project"]),
        physics=PhysicsConfig(**raw.get("physics", {})),
        grid=GridConfig(
            x_min=raw["grid"]["x_min"],
            x_max=raw["grid"]["x_max"],
            nx=raw["grid"]["nx"],
            window=WindowConfig(**raw["grid"]["window"]),
        ),
        time_scan=TimeScanConfig(**raw.get("time_scan", {})),
        alpha_scan=AlphaScanConfig(
            coarse=AlphaCoarseConfig(**raw["alpha_scan"]["coarse"]),
            refine=AlphaRefineConfig(**raw["alpha_scan"]["refine"]),
        ),
        p_sets=PSetsConfig(
            active_families=raw["p_sets"]["active_families"],
            families={k: PFamilyConfig(**v) for k, v in raw["p_sets"]["families"].items()},
        ),
        phases=PhasesConfig(
            phi0_mode=raw["phases"]["phi0_mode"],
            phi0_seed=raw["phases"]["phi0_seed"],
            dispersion=DispersionConfig(**raw["phases"]["dispersion"]),
        ),
        kernel=KernelConfig(
            build_kbar=raw["kernel"]["build_kbar"],
            kbar_average=KbarAverageConfig(**raw["kernel"]["kbar_average"]),
            sign_preserving=SignPreservingConfig(**raw["kernel"]["sign_preserving"]),
        ),
        graphs=GraphsConfig(
            theta_scan=ThetaScanConfig(**raw["graphs"]["theta_scan"]),
            adjacency_modes=raw["graphs"]["adjacency_modes"],
            weighted_layer=WeightedLayerConfig(**raw["graphs"]["weighted_layer"]),
        ),
        source_test=SourceTestConfig(**raw["source_test"]),
        readout_test=ReadoutTestConfig(**raw["readout_test"]),
        peak_detection=PeakDetectionConfig(**raw["peak_detection"]),
        controls=ControlsConfig(**raw["controls"]),
        labels=LabelsConfig(**raw["labels"]),
    )
    cfg.validate()
    return cfg


def setup_logging(run_root: Path) -> None:
    run_root.mkdir(parents=True, exist_ok=True)
    log_dir = run_root / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)

    LOGGER.setLevel(logging.INFO)
    LOGGER.handlers.clear()

    formatter = logging.Formatter("%(asctime)s | %(levelname)s | %(message)s")

    fh = logging.FileHandler(log_dir / "run.log", encoding="utf-8")
    fh.setFormatter(formatter)
    LOGGER.addHandler(fh)

    sh = logging.StreamHandler()
    sh.setFormatter(formatter)
    LOGGER.addHandler(sh)


def init_output_tree(run_root: Path, cfg: M33V0Config) -> None:
    (run_root / "logs").mkdir(parents=True, exist_ok=True)
    (run_root / "V0_source_scan" / "plots").mkdir(parents=True, exist_ok=True)
    (run_root / "M33_readout_scan" / "plots").mkdir(parents=True, exist_ok=True)
    (run_root / "combined").mkdir(parents=True, exist_ok=True)

    with open(run_root / "config_snapshot.yaml", "w", encoding="utf-8") as handle:
        yaml.safe_dump(asdict(cfg), handle, sort_keys=False, allow_unicode=True)

    manifest = {
        "run_id": cfg.project.run_id,
        "tag": cfg.project.tag,
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "seed": cfg.project.seed,
        "script_version": "m33_v0_runner.py",
        "config_snapshot": "config_snapshot.yaml",
        "status": "initialized",
    }
    with open(run_root / "run_manifest.json", "w", encoding="utf-8") as handle:
        json.dump(manifest, handle, indent=2)

    for relpath in [
        run_root / "V0_source_scan" / "phase_pair_stats.csv",
        run_root / "V0_source_scan" / "kernel_sign_stats.csv",
        run_root / "V0_source_scan" / "source_peak_summary.csv",
        run_root / "M33_readout_scan" / "alpha_scan.csv",
        run_root / "M33_readout_scan" / "alpha_scan_summary.csv",
        run_root / "M33_readout_scan" / "robustness_table.csv",
        run_root / "combined" / "source_readout_alignment.csv",
        run_root / "combined" / "combined_decision_table.csv",
    ]:
        if not relpath.exists():
            relpath.touch()

    for relpath, payload in [
        (
            run_root / "V0_source_scan" / "source_summary.json",
            {
                "source_hypothesis": "",
                "n_total_runs": 0,
                "n_valid_runs": 0,
                "median_alpha_star_source": None,
                "frac_source_in_band": None,
                "t0_control_pass": None,
                "dominant_source_feature": "",
                "source_label_global": "",
            },
        ),
        (
            run_root / "M33_readout_scan" / "readout_summary.json",
            {
                "median_alpha_star_chi": None,
                "median_alpha_star_lambda2": None,
                "median_alpha_star_wclust": None,
                "frac_readout_in_band": None,
                "frac_coherent": None,
                "readout_label_global": "",
            },
        ),
        (
            run_root / "combined" / "combined_summary.json",
            {
                "source_readout_link_supported": None,
                "median_delta_source_chi": None,
                "median_delta_source_lambda2": None,
                "global_t0_control_pass": None,
                "global_asymmetry_pass": None,
                "final_decision": "",
                "interpretation": "",
            },
        ),
    ]:
        if not relpath.exists():
            with open(relpath, "w", encoding="utf-8") as handle:
                json.dump(payload, handle, indent=2)

    report_path = run_root / "combined" / "combined_report.md"
    if not report_path.exists():
        report_path.write_text(
            "# Combined Report\n\n## Status\ninitialized\n\n## Notes\n- scaffold created\n",
            encoding="utf-8",
        )


def build_x_grid(cfg: M33V0Config) -> np.ndarray:
    return np.linspace(cfg.grid.x_min, cfg.grid.x_max, cfg.grid.nx)


def build_window_weights(x: np.ndarray, cfg: M33V0Config) -> np.ndarray:
    if cfg.grid.window.type != "gaussian":
        raise NotImplementedError(f"Unsupported window type: {cfg.grid.window.type}")
    sigma = cfg.grid.window.sigma
    weights = np.exp(-0.5 * (x / sigma) ** 2)
    if cfg.grid.window.normalize_weights:
        denom = np.sum(weights)
        if denom > 0:
            weights = weights / denom
    return weights


def build_alpha_values(cfg: M33V0Config, coarse_peak: float | None, coarse_only: bool) -> np.ndarray:
    coarse = np.arange(
        cfg.alpha_scan.coarse.alpha_min,
        cfg.alpha_scan.coarse.alpha_max + 0.5 * cfg.alpha_scan.coarse.alpha_step,
        cfg.alpha_scan.coarse.alpha_step,
    )
    if coarse_only or not cfg.alpha_scan.refine.enabled:
        return np.unique(np.round(coarse, 12))

    center = cfg.alpha_scan.refine.fixed_center
    if cfg.alpha_scan.refine.center_mode == "coarse_peak" and coarse_peak is not None:
        center = coarse_peak

    refine = np.arange(
        center - cfg.alpha_scan.refine.half_width,
        center + cfg.alpha_scan.refine.half_width + 0.5 * cfg.alpha_scan.refine.alpha_step,
        cfg.alpha_scan.refine.alpha_step,
    )
    merged = np.unique(np.round(np.concatenate([coarse, refine]), 12))
    merged = merged[(merged >= cfg.alpha_scan.coarse.alpha_min) & (merged <= cfg.alpha_scan.coarse.alpha_max)]
    return merged


def build_phi0_values(cfg: M33V0Config, n_p: int) -> np.ndarray:
    if cfg.phases.phi0_mode == "zero":
        return np.zeros(n_p, dtype=float)
    if cfg.phases.phi0_mode == "random":
        rng = np.random.default_rng(cfg.phases.phi0_seed)
        return rng.uniform(0.0, 2.0 * np.pi, size=n_p)
    raise NotImplementedError(f"Unsupported phi0_mode: {cfg.phases.phi0_mode}")


def spectral_radius_sym(matrix: np.ndarray) -> float:
    if matrix.size == 0:
        return float("nan")
    vals = np.linalg.eigvalsh(matrix)
    return float(np.max(vals))


def second_laplacian_eigenvalue(weight_matrix: np.ndarray) -> float:
    if weight_matrix.size == 0:
        return float("nan")
    degree = np.sum(weight_matrix, axis=1)
    lap = np.diag(degree) - weight_matrix
    vals = np.linalg.eigvalsh(lap)
    vals = np.sort(vals)
    if len(vals) < 2:
        return float("nan")
    return float(vals[1])


def natural_connectivity(weight_matrix: np.ndarray) -> float:
    vals = np.linalg.eigvalsh(weight_matrix)
    return float(np.log(np.mean(np.exp(vals))))


def weighted_clustering_onnela(weight_matrix: np.ndarray) -> float:
    n = weight_matrix.shape[0]
    if n < 3:
        return float("nan")
    wmax = np.max(weight_matrix)
    if wmax <= 0:
        return 0.0
    w = weight_matrix / wmax
    cvals: List[float] = []
    for i in range(n):
        neighbors = np.where(w[i] > 0)[0]
        neighbors = neighbors[neighbors != i]
        k = len(neighbors)
        if k < 2:
            cvals.append(0.0)
            continue
        tri_sum = 0.0
        for a in range(k):
            j = int(neighbors[a])
            for b in range(a + 1, k):
                h = int(neighbors[b])
                if w[j, h] > 0:
                    tri_sum += (w[i, j] * w[i, h] * w[j, h]) ** (1.0 / 3.0)
        cvals.append((2.0 * tri_sum) / (k * (k - 1)))
    return float(np.mean(cvals))


def floyd_warshall_inverse_weight(weight_matrix: np.ndarray) -> np.ndarray:
    n = weight_matrix.shape[0]
    dist = np.full((n, n), np.inf, dtype=float)
    np.fill_diagonal(dist, 0.0)
    positive = weight_matrix > 0
    dist[positive] = 1.0 / weight_matrix[positive]
    for k in range(n):
        dist = np.minimum(dist, dist[:, [k]] + dist[[k], :])
    return dist


def global_efficiency(weight_matrix: np.ndarray) -> float:
    n = weight_matrix.shape[0]
    if n < 2:
        return float("nan")
    dist = floyd_warshall_inverse_weight(weight_matrix)
    with np.errstate(divide="ignore"):
        invd = 1.0 / dist
    invd[~np.isfinite(invd)] = 0.0
    np.fill_diagonal(invd, 0.0)
    return float(np.sum(invd) / (n * (n - 1)))


def count_components(weight_matrix: np.ndarray) -> int:
    n = weight_matrix.shape[0]
    visited = np.zeros(n, dtype=bool)
    n_components = 0
    for i in range(n):
        if visited[i]:
            continue
        n_components += 1
        stack = [i]
        visited[i] = True
        while stack:
            node = stack.pop()
            neighbors = np.where(weight_matrix[node] > 0)[0]
            for nb in neighbors:
                if not visited[nb]:
                    visited[nb] = True
                    stack.append(int(nb))
    return int(n_components)


def compute_phase_pair_stats(
    x: np.ndarray,
    weights: np.ndarray,
    p_values: np.ndarray,
    t: float,
    alpha: float,
    cfg: M33V0Config,
) -> Tuple[List[Dict[str, float]], np.ndarray]:
    n_p = len(p_values)
    phi0 = build_phi0_values(cfg, n_p)
    energies = alpha * (p_values ** 2) / (2.0 * cfg.physics.m)
    kbar = np.zeros((n_p, n_p), dtype=float)
    rows: List[Dict[str, float]] = []

    for i in range(n_p):
        for j in range(i + 1, n_p):
            delta_p = p_values[i] - p_values[j]
            delta_e = energies[i] - energies[j]
            dphi = (delta_p * x - delta_e * t) / cfg.physics.hbar + (phi0[i] - phi0[j])
            cos_dphi = np.cos(dphi)
            sin_dphi = np.sin(dphi)
            kbar_ij = float(np.sum(weights * cos_dphi))
            kbar[i, j] = kbar[j, i] = kbar_ij
            rows.append(
                {
                    "run_id": cfg.project.run_id,
                    "t": float(t),
                    "p_family": "",
                    "alpha": float(alpha),
                    "pair_i": i,
                    "pair_j": j,
                    "p_i": float(p_values[i]),
                    "p_j": float(p_values[j]),
                    "delta_p": float(delta_p),
                    "E_i": float(energies[i]),
                    "E_j": float(energies[j]),
                    "delta_E": float(delta_e),
                    "var_dphi_x": float(np.var(dphi)),
                    "mean_dphi_x": float(np.mean(dphi)),
                    "mean_cos_dphi": float(np.mean(cos_dphi)),
                    "mean_abs_cos_dphi": float(np.mean(np.abs(cos_dphi))),
                    "mean_sin_dphi": float(np.mean(sin_dphi)),
                    "kbar_ij": kbar_ij,
                    "kbar_abs_ij": float(abs(kbar_ij)),
                    "kbar_sign": int(np.sign(kbar_ij)),
                    "finite_fraction": 1.0,
                }
            )
    return rows, kbar


def summarize_source_metrics(
    cfg: M33V0Config,
    t: float,
    p_family: str,
    alpha: float,
    pair_rows: List[Dict[str, float]],
    kbar: np.ndarray,
) -> Dict[str, float]:
    triu = np.triu_indices_from(kbar, k=1)
    vals = kbar[triu]
    pos = np.maximum(kbar, 0.0)
    neg = np.maximum(-kbar, 0.0)
    kabs = np.abs(kbar)

    f_pos = float(np.mean(vals > cfg.kernel.sign_preserving.zero_tolerance))
    f_neg = float(np.mean(vals < -cfg.kernel.sign_preserving.zero_tolerance))
    f_zero = float(np.mean(np.abs(vals) <= cfg.kernel.sign_preserving.zero_tolerance))
    sign_imbalance = f_neg - f_pos

    source_feature = "lambda_max_kneg"
    return {
        "run_id": cfg.project.run_id,
        "t": float(t),
        "p_family": p_family,
        "alpha": float(alpha),
        "n_nodes": int(kbar.shape[0]),
        "n_pairs": int(len(vals)),
        "I_net": float(np.mean(vals)),
        "I_abs": float(np.mean(np.abs(vals))),
        "f_pos": f_pos,
        "f_neg": f_neg,
        "f_zero": f_zero,
        "mean_kpos": float(np.mean(pos[triu])),
        "mean_kneg": float(np.mean(neg[triu])),
        "sum_kpos": float(np.sum(pos[triu])),
        "sum_kneg": float(np.sum(neg[triu])),
        "lambda_max_kpos": spectral_radius_sym(pos),
        "lambda_max_kneg": spectral_radius_sym(neg),
        "lambda_max_kabs": spectral_radius_sym(kabs),
        "sign_imbalance": float(sign_imbalance),
        "source_peak_flag": 0,
        "source_feature": source_feature,
        "finite_fraction": 1.0,
    }


def threshold_matrix(matrix: np.ndarray, theta: float) -> np.ndarray:
    out = matrix.copy()
    out[np.abs(out) < theta] = 0.0
    np.fill_diagonal(out, 0.0)
    return out


def compute_readout_metrics(
    cfg: M33V0Config,
    t: float,
    p_family: str,
    alpha: float,
    theta: float,
    kbar: np.ndarray,
) -> Dict[str, float]:
    pos = np.maximum(kbar, 0.0)
    neg = np.maximum(-kbar, 0.0)
    kabs = np.abs(kbar)

    pos_t = threshold_matrix(pos, theta)
    neg_t = threshold_matrix(neg, theta)
    abs_t = threshold_matrix(kabs, theta)

    lam_pos = spectral_radius_sym(pos_t)
    lam_neg = spectral_radius_sym(neg_t)
    lam_abs = spectral_radius_sym(abs_t)

    chi = float("nan")
    if np.isfinite(lam_abs) and abs(lam_abs) > 1e-15:
        chi = float((lam_neg - lam_pos) / lam_abs)

    triu = np.triu_indices_from(kbar, k=1)
    total_pairs = len(triu[0])
    rho_pos = float(np.count_nonzero(pos_t[triu] > 0) / total_pairs)
    rho_neg = float(np.count_nonzero(neg_t[triu] > 0) / total_pairs)

    return {
        "run_id": cfg.project.run_id,
        "t": float(t),
        "p_family": p_family,
        "theta": float(theta),
        "alpha": float(alpha),
        "kernel_mode": "abs",
        "chi": chi,
        "rho_pos": rho_pos,
        "rho_neg": rho_neg,
        "lambda_max_pos": lam_pos,
        "lambda_max_neg": lam_neg,
        "lambda_max_abs": lam_abs,
        "lambda2_abs": second_laplacian_eigenvalue(abs_t),
        "weighted_clustering_abs": weighted_clustering_onnela(abs_t),
        "natural_connectivity_abs": natural_connectivity(abs_t),
        "global_efficiency_abs": global_efficiency(abs_t),
        "n_components_abs": count_components(abs_t),
        "finite_fraction": 1.0,
        "peak_flag_chi": 0,
        "peak_flag_lambda2": 0,
        "peak_flag_wclust": 0,
    }


def find_peak(
    alphas: np.ndarray,
    values: np.ndarray,
    mode: str,
    edge_exclusion_bins: int,
) -> Dict[str, float | bool]:
    mask = np.isfinite(values)
    if np.count_nonzero(mask) < 3:
        return {
            "found": False,
            "alpha_star": np.nan,
            "value": np.nan,
            "prominence": np.nan,
            "width": np.nan,
            "is_edge": True,
        }
    aa = alphas[mask]
    vv = values[mask]
    idx = int(np.nanargmax(vv) if mode == "max" else np.nanargmin(vv))
    is_edge = idx < edge_exclusion_bins or idx >= len(vv) - edge_exclusion_bins
    baseline = float(np.nanmedian(vv))
    value = float(vv[idx])
    prominence = value - baseline if mode == "max" else baseline - value

    half = baseline + 0.5 * prominence if mode == "max" else baseline - 0.5 * prominence
    left = idx
    right = idx
    if mode == "max":
        while left > 0 and vv[left] >= half:
            left -= 1
        while right < len(vv) - 1 and vv[right] >= half:
            right += 1
    else:
        while left > 0 and vv[left] <= half:
            left -= 1
        while right < len(vv) - 1 and vv[right] <= half:
            right += 1

    width = float(aa[min(right, len(aa)-1)] - aa[max(left, 0)])
    return {
        "found": not is_edge,
        "alpha_star": float(aa[idx]),
        "value": value,
        "prominence": float(prominence),
        "width": width,
        "is_edge": bool(is_edge),
    }


def choose_source_feature(group: pd.DataFrame, cfg: M33V0Config) -> Dict[str, float | str]:
    candidates = [
        ("I_abs", "max"),
        ("f_neg", "max"),
        ("lambda_max_kneg", "max"),
        ("sign_imbalance", "max"),
    ]
    alphas = group["alpha"].to_numpy(dtype=float)
    band_lo, band_hi = cfg.peak_detection.source_peak_band
    best = None
    for feature, mode in candidates:
        peak = find_peak(alphas, group[feature].to_numpy(dtype=float), mode, cfg.peak_detection.edge_exclusion_bins)
        in_band = bool(peak["found"] and band_lo <= float(peak["alpha_star"]) <= band_hi)
        score = float(peak["prominence"]) if np.isfinite(peak["prominence"]) else -np.inf
        if not in_band:
            score -= 1e6
        if best is None or score > best["score"]:
            best = {
                "feature": feature,
                "mode": mode,
                "score": score,
                "peak": peak,
                "in_band": in_band,
            }
    assert best is not None
    peak = best["peak"]
    return {
        "alpha_star_source": float(peak["alpha_star"]),
        "source_feature": str(best["feature"]),
        "source_peak_type": str(best["mode"]),
        "source_peak_value": float(peak["value"]),
        "source_prominence": float(peak["prominence"]),
        "source_width": float(peak["width"]),
        "source_in_band_flag": int(best["in_band"]),
    }


def source_label_from_row(row: pd.Series) -> str:
    if not np.isfinite(row["alpha_star_source"]) or row["source_in_band_flag"] == 0:
        return "Q0"
    if row["source_prominence"] <= 0:
        return "Q1"
    if row["t0_control_flag"] == 1:
        return "Q3"
    return "Q2"


def readout_label_from_row(row: pd.Series, tol: float) -> str:
    if not (np.isfinite(row["alpha_star_chi"]) and np.isfinite(row["alpha_star_lambda2"])):
        return "R0"
    if row["readout_in_band_flag"] == 0:
        return "R1"
    if row["delta_chi_lambda2"] > tol:
        return "R1"
    if np.isfinite(row["alpha_star_wclust"]) and row["delta_chi_wclust"] <= tol:
        return "R3"
    return "R2"


def summarize_source_df(cfg: M33V0Config, source_df: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for (t, p_family), group in source_df.groupby(["t", "p_family"], sort=True):
        chosen = choose_source_feature(group.sort_values("alpha"), cfg)
        t0_control_flag = 0
        if t == 0.0:
            t0_control_flag = int(chosen["source_in_band_flag"] == 0)
        rows.append(
            {
                "run_id": cfg.project.run_id,
                "t": float(t),
                "p_family": str(p_family),
                **chosen,
                "t0_control_flag": t0_control_flag,
                "source_label": "",
            }
        )
    out = pd.DataFrame(rows, columns=SOURCE_PEAK_SUMMARY_COLUMNS)
    if not out.empty:
        out["source_label"] = out.apply(source_label_from_row, axis=1)
    return out


def summarize_readout_df(cfg: M33V0Config, readout_df: pd.DataFrame) -> Tuple[pd.DataFrame, pd.DataFrame]:
    summary_rows = []
    robust_rows = []
    for (t, p_family, theta), group in readout_df.groupby(["t", "p_family", "theta"], sort=True):
        g = group.sort_values("alpha")
        alphas = g["alpha"].to_numpy(dtype=float)
        pk_chi = find_peak(alphas, g["chi"].to_numpy(dtype=float), "max", cfg.peak_detection.edge_exclusion_bins)
        pk_l2 = find_peak(alphas, g["lambda2_abs"].to_numpy(dtype=float), "min", cfg.peak_detection.edge_exclusion_bins)
        pk_wc = find_peak(
            alphas,
            g["weighted_clustering_abs"].to_numpy(dtype=float),
            "max",
            cfg.peak_detection.edge_exclusion_bins,
        )

        band_lo, band_hi = cfg.peak_detection.readout_peak_band
        in_band = int(
            pk_chi["found"]
            and pk_l2["found"]
            and band_lo <= float(pk_chi["alpha_star"]) <= band_hi
            and band_lo <= float(pk_l2["alpha_star"]) <= band_hi
        )
        delta_chi_lambda2 = (
            float(abs(float(pk_chi["alpha_star"]) - float(pk_l2["alpha_star"])))
            if pk_chi["found"] and pk_l2["found"]
            else float("nan")
        )
        delta_chi_wclust = (
            float(abs(float(pk_chi["alpha_star"]) - float(pk_wc["alpha_star"])))
            if pk_chi["found"] and pk_wc["found"]
            else float("nan")
        )

        row = {
            "run_id": cfg.project.run_id,
            "t": float(t),
            "p_family": str(p_family),
            "theta": float(theta),
            "alpha_star_chi": float(pk_chi["alpha_star"]),
            "alpha_star_lambda2": float(pk_l2["alpha_star"]),
            "alpha_star_wclust": float(pk_wc["alpha_star"]),
            "chi_peak_value": float(pk_chi["value"]),
            "lambda2_min_value": float(pk_l2["value"]),
            "wclust_peak_value": float(pk_wc["value"]),
            "chi_prominence": float(pk_chi["prominence"]),
            "lambda2_prominence": float(pk_l2["prominence"]),
            "wclust_prominence": float(pk_wc["prominence"]),
            "delta_chi_lambda2": delta_chi_lambda2,
            "delta_chi_wclust": delta_chi_wclust,
            "readout_in_band_flag": in_band,
            "readout_label": "",
        }
        row["readout_label"] = readout_label_from_row(pd.Series(row), cfg.peak_detection.coherence_tol_fine)
        summary_rows.append(row)

        robust_rows.append(
            {
                "run_id": cfg.project.run_id,
                "t": float(t),
                "p_family": str(p_family),
                "alpha_star_chi": float(pk_chi["alpha_star"]),
                "alpha_star_lambda2": float(pk_l2["alpha_star"]),
                "alpha_star_wclust": float(pk_wc["alpha_star"]),
                "delta_peak_alignment": delta_chi_lambda2,
                "peak_prominence_chi": float(pk_chi["prominence"]),
                "peak_prominence_lambda2": float(pk_l2["prominence"]),
                "peak_prominence_wclust": float(pk_wc["prominence"]),
                "stability_label": row["readout_label"],
            }
        )

    summary_df = pd.DataFrame(summary_rows, columns=ALPHA_SCAN_SUMMARY_COLUMNS)
    robust_df = pd.DataFrame(robust_rows, columns=ROBUSTNESS_TABLE_COLUMNS)
    return summary_df, robust_df


def build_alignment_df(
    cfg: M33V0Config,
    source_summary_df: pd.DataFrame,
    readout_summary_df: pd.DataFrame,
) -> pd.DataFrame:
    rows = []
    non_p0_source_ok = int(
        (
            (~source_summary_df["p_family"].eq("P0"))
            & source_summary_df["source_label"].isin(["Q2", "Q3"])
        ).any()
    ) if not source_summary_df.empty else 0

    for _, rd in readout_summary_df.iterrows():
        src_match = source_summary_df[
            (source_summary_df["t"] == rd["t"]) & (source_summary_df["p_family"] == rd["p_family"])
        ]
        src = src_match.iloc[0] if not src_match.empty else None
        alpha_source = float(src["alpha_star_source"]) if src is not None else float("nan")
        delta_source_chi = float(abs(alpha_source - rd["alpha_star_chi"])) if np.isfinite(alpha_source) and np.isfinite(rd["alpha_star_chi"]) else float("nan")
        delta_source_lambda2 = float(abs(alpha_source - rd["alpha_star_lambda2"])) if np.isfinite(alpha_source) and np.isfinite(rd["alpha_star_lambda2"]) else float("nan")
        delta_source_wclust = float(abs(alpha_source - rd["alpha_star_wclust"])) if np.isfinite(alpha_source) and np.isfinite(rd["alpha_star_wclust"]) else float("nan")

        source_peak_flag = int(src is not None and src["source_label"] != "Q0")
        readout_peak_flag = int(rd["readout_label"] != "R0")
        coherent_peak_flag = int(
            source_peak_flag == 1
            and readout_peak_flag == 1
            and np.isfinite(delta_source_chi)
            and np.isfinite(delta_source_lambda2)
            and delta_source_chi <= cfg.peak_detection.coherence_tol_fine
            and delta_source_lambda2 <= cfg.peak_detection.coherence_tol_fine
        )

        t0_control_flag = int(
            source_summary_df[source_summary_df["t"] == 0.0]["source_in_band_flag"].eq(0).all()
        ) if cfg.controls.require_t0_control and not source_summary_df[source_summary_df["t"] == 0.0].empty else 0

        asymmetry_valid_flag = non_p0_source_ok

        if source_peak_flag == 0 and readout_peak_flag == 1:
            combined_label = "Q0"
        elif source_peak_flag == 1 and coherent_peak_flag == 0:
            combined_label = "Q1"
        elif coherent_peak_flag == 1 and (t0_control_flag == 0 or asymmetry_valid_flag == 0):
            combined_label = "Q2"
        elif coherent_peak_flag == 1:
            combined_label = "Q3"
        else:
            combined_label = "Q0"

        rows.append(
            {
                "run_id": cfg.project.run_id,
                "t": float(rd["t"]),
                "p_family": str(rd["p_family"]),
                "theta": float(rd["theta"]),
                "alpha_star_source": alpha_source,
                "alpha_star_chi": float(rd["alpha_star_chi"]),
                "alpha_star_lambda2": float(rd["alpha_star_lambda2"]),
                "alpha_star_wclust": float(rd["alpha_star_wclust"]),
                "delta_source_chi": delta_source_chi,
                "delta_source_lambda2": delta_source_lambda2,
                "delta_source_wclust": delta_source_wclust,
                "source_peak_flag": source_peak_flag,
                "readout_peak_flag": readout_peak_flag,
                "coherent_peak_flag": coherent_peak_flag,
                "t0_control_flag": t0_control_flag,
                "asymmetry_valid_flag": asymmetry_valid_flag,
                "combined_label": combined_label,
            }
        )
    return pd.DataFrame(rows, columns=SOURCE_READOUT_ALIGNMENT_COLUMNS)


def build_combined_decision_table(cfg: M33V0Config, alignment_df: pd.DataFrame) -> pd.DataFrame:
    rows = []
    if alignment_df.empty:
        return pd.DataFrame(columns=COMBINED_DECISION_TABLE_COLUMNS)

    for p_family, group in alignment_df.groupby("p_family", sort=True):
        n_valid_runs = int(len(group))
        frac_source_in_band = float(np.mean(group["source_peak_flag"] == 1))
        frac_readout_in_band = float(np.mean(group["readout_peak_flag"] == 1))
        frac_coherent = float(np.mean(group["coherent_peak_flag"] == 1))
        global_t0_control_pass = int(group["t0_control_flag"].all())
        global_asymmetry_pass = int(group["asymmetry_valid_flag"].all())

        if frac_readout_in_band == 0:
            final_decision = "R0"
            kill_signal = "none"
        elif frac_coherent < cfg.peak_detection.robust_fraction_min:
            final_decision = "R1"
            kill_signal = "source_readout_decoupling"
        elif global_t0_control_pass == 0:
            final_decision = "R1"
            kill_signal = "t0_failure"
        elif global_asymmetry_pass == 0:
            final_decision = "R1"
            kill_signal = "asymmetry_special_case"
        elif frac_coherent >= cfg.peak_detection.robust_fraction_min:
            final_decision = "R3"
            kill_signal = "none"
        else:
            final_decision = "R2"
            kill_signal = "none"

        rows.append(
            {
                "run_id": cfg.project.run_id,
                "aggregation_level": "p_family",
                "p_family": str(p_family),
                "n_valid_runs": n_valid_runs,
                "frac_source_in_band": frac_source_in_band,
                "frac_readout_in_band": frac_readout_in_band,
                "frac_coherent": frac_coherent,
                "median_alpha_source": float(np.nanmedian(group["alpha_star_source"])),
                "median_alpha_chi": float(np.nanmedian(group["alpha_star_chi"])),
                "median_alpha_lambda2": float(np.nanmedian(group["alpha_star_lambda2"])),
                "median_alpha_wclust": float(np.nanmedian(group["alpha_star_wclust"])),
                "median_delta_source_chi": float(np.nanmedian(group["delta_source_chi"])),
                "median_delta_chi_lambda2": float(np.nanmedian(np.abs(group["alpha_star_chi"] - group["alpha_star_lambda2"]))),
                "global_t0_control_pass": global_t0_control_pass,
                "global_asymmetry_pass": global_asymmetry_pass,
                "final_decision": final_decision,
                "kill_signal": kill_signal,
            }
        )

    all_group = alignment_df
    rows.append(
        {
            "run_id": cfg.project.run_id,
            "aggregation_level": "global",
            "p_family": "ALL",
            "n_valid_runs": int(len(all_group)),
            "frac_source_in_band": float(np.mean(all_group["source_peak_flag"] == 1)),
            "frac_readout_in_band": float(np.mean(all_group["readout_peak_flag"] == 1)),
            "frac_coherent": float(np.mean(all_group["coherent_peak_flag"] == 1)),
            "median_alpha_source": float(np.nanmedian(all_group["alpha_star_source"])),
            "median_alpha_chi": float(np.nanmedian(all_group["alpha_star_chi"])),
            "median_alpha_lambda2": float(np.nanmedian(all_group["alpha_star_lambda2"])),
            "median_alpha_wclust": float(np.nanmedian(all_group["alpha_star_wclust"])),
            "median_delta_source_chi": float(np.nanmedian(all_group["delta_source_chi"])),
            "median_delta_chi_lambda2": float(np.nanmedian(np.abs(all_group["alpha_star_chi"] - all_group["alpha_star_lambda2"]))),
            "global_t0_control_pass": int(all_group["t0_control_flag"].all()),
            "global_asymmetry_pass": int(all_group["asymmetry_valid_flag"].all()),
            "final_decision": "R3" if float(np.mean(all_group["coherent_peak_flag"] == 1)) >= cfg.peak_detection.robust_fraction_min else "R1",
            "kill_signal": "none",
        }
    )
    return pd.DataFrame(rows, columns=COMBINED_DECISION_TABLE_COLUMNS)


def write_json(path: Path, payload: dict) -> None:
    with open(path, "w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2)


def write_report(run_root: Path, decision_df: pd.DataFrame) -> None:
    lines = [
        "# Combined Report",
        "",
        "## Status",
        "completed",
        "",
        "## Decisions",
    ]
    if decision_df.empty:
        lines.append("- no decisions available")
    else:
        for _, row in decision_df.iterrows():
            lines.append(
                f"- level={row['aggregation_level']} p_family={row['p_family']} "
                f"decision={row['final_decision']} kill={row['kill_signal']}"
            )
    (run_root / "combined" / "combined_report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    args = parse_args()
    project_root = Path(args.project_root).resolve()
    config_path = Path(args.config)
    if not config_path.is_absolute():
        config_path = project_root / config_path

    cfg = load_config(config_path)
    run_root = Path(cfg.project.output_root)
    if not run_root.is_absolute():
        run_root = project_root / run_root

    init_output_tree(run_root, cfg)
    setup_logging(run_root)
    LOGGER.info("Initialized run at %s", run_root)

    if args.init_only:
        LOGGER.info("Init-only requested, exiting.")
        return

    np.random.seed(cfg.project.seed)
    x = build_x_grid(cfg)
    weights = build_window_weights(x, cfg)

    pair_rows_all: List[Dict[str, float]] = []
    source_rows_all: List[Dict[str, float]] = []
    readout_rows_all: List[Dict[str, float]] = []

    for p_family in cfg.p_sets.active_families:
        p_values = np.asarray(cfg.p_sets.families[p_family].p_values, dtype=float)
        coarse_source_scan = []

        coarse_alphas = np.arange(
            cfg.alpha_scan.coarse.alpha_min,
            cfg.alpha_scan.coarse.alpha_max + 0.5 * cfg.alpha_scan.coarse.alpha_step,
            cfg.alpha_scan.coarse.alpha_step,
        )

        for t in cfg.time_scan.t_values:
            for alpha in coarse_alphas:
                pair_rows, kbar = compute_phase_pair_stats(x, weights, p_values, float(t), float(alpha), cfg)
                src_row = summarize_source_metrics(cfg, float(t), p_family, float(alpha), pair_rows, kbar)
                coarse_source_scan.append(src_row)

        coarse_source_df = pd.DataFrame(coarse_source_scan)
        coarse_peaks = {}
        if not coarse_source_df.empty:
            for t, g in coarse_source_df.groupby("t"):
                chosen = choose_source_feature(g.sort_values("alpha"), cfg)
                coarse_peaks[float(t)] = float(chosen["alpha_star_source"])

        for t in cfg.time_scan.t_values:
            alpha_values = build_alpha_values(cfg, coarse_peaks.get(float(t)), args.coarse_only)
            for alpha in alpha_values:
                pair_rows, kbar = compute_phase_pair_stats(x, weights, p_values, float(t), float(alpha), cfg)
                # keep pair rows only once in final output for exact scanned alphas
                # but do not duplicate coarse rows that already exist
                for row in pair_rows:
                    row["p_family"] = p_family
                pair_rows_all.extend(pair_rows)
                source_rows_all.append(summarize_source_metrics(cfg, float(t), p_family, float(alpha), pair_rows, kbar))

                for theta in cfg.graphs.theta_scan.theta_values:
                    readout_rows_all.append(compute_readout_metrics(cfg, float(t), p_family, float(alpha), float(theta), kbar))

    pair_df = pd.DataFrame(pair_rows_all)
    if not pair_df.empty:
        pair_df = pair_df[PHASE_PAIR_STATS_COLUMNS]
    source_df = pd.DataFrame(source_rows_all)
    if not source_df.empty:
        source_df = source_df[KERNEL_SIGN_STATS_COLUMNS]
        source_df = source_df.drop_duplicates(subset=["t", "p_family", "alpha"], keep="last")
    readout_df = pd.DataFrame(readout_rows_all)
    if not readout_df.empty:
        readout_df = readout_df[ALPHA_SCAN_COLUMNS]
        readout_df = readout_df.drop_duplicates(subset=["t", "p_family", "theta", "alpha"], keep="last")

    source_summary_df = summarize_source_df(cfg, source_df)
    readout_summary_df, robustness_df = summarize_readout_df(cfg, readout_df)
    alignment_df = build_alignment_df(cfg, source_summary_df, readout_summary_df)
    decision_df = build_combined_decision_table(cfg, alignment_df)

    pair_df.to_csv(run_root / "V0_source_scan" / "phase_pair_stats.csv", index=False)
    source_df.to_csv(run_root / "V0_source_scan" / "kernel_sign_stats.csv", index=False)
    source_summary_df.to_csv(run_root / "V0_source_scan" / "source_peak_summary.csv", index=False)

    readout_df.to_csv(run_root / "M33_readout_scan" / "alpha_scan.csv", index=False)
    readout_summary_df.to_csv(run_root / "M33_readout_scan" / "alpha_scan_summary.csv", index=False)
    robustness_df.to_csv(run_root / "M33_readout_scan" / "robustness_table.csv", index=False)

    alignment_df.to_csv(run_root / "combined" / "source_readout_alignment.csv", index=False)
    decision_df.to_csv(run_root / "combined" / "combined_decision_table.csv", index=False)

    source_summary_payload = {
        "source_hypothesis": "alpha*=1.6 is upstream-visible in phase/interference structure",
        "n_total_runs": int(len(source_df)),
        "n_valid_runs": int(len(source_summary_df)),
        "median_alpha_star_source": float(np.nanmedian(source_summary_df["alpha_star_source"])) if not source_summary_df.empty else None,
        "frac_source_in_band": float(np.mean(source_summary_df["source_in_band_flag"] == 1)) if not source_summary_df.empty else None,
        "t0_control_pass": bool(source_summary_df[source_summary_df["t"] == 0.0]["source_in_band_flag"].eq(0).all()) if not source_summary_df[source_summary_df["t"] == 0.0].empty else None,
        "dominant_source_feature": str(source_summary_df["source_feature"].mode().iat[0]) if not source_summary_df.empty else "",
        "source_label_global": str(source_summary_df["source_label"].mode().iat[0]) if not source_summary_df.empty else "",
    }
    readout_summary_payload = {
        "median_alpha_star_chi": float(np.nanmedian(readout_summary_df["alpha_star_chi"])) if not readout_summary_df.empty else None,
        "median_alpha_star_lambda2": float(np.nanmedian(readout_summary_df["alpha_star_lambda2"])) if not readout_summary_df.empty else None,
        "median_alpha_star_wclust": float(np.nanmedian(readout_summary_df["alpha_star_wclust"])) if not readout_summary_df.empty else None,
        "frac_readout_in_band": float(np.mean(readout_summary_df["readout_in_band_flag"] == 1)) if not readout_summary_df.empty else None,
        "frac_coherent": float(np.mean(alignment_df["coherent_peak_flag"] == 1)) if not alignment_df.empty else None,
        "readout_label_global": str(readout_summary_df["readout_label"].mode().iat[0]) if not readout_summary_df.empty else "",
    }
    combined_summary_payload = {
        "source_readout_link_supported": bool(np.mean(alignment_df["coherent_peak_flag"] == 1) >= cfg.peak_detection.robust_fraction_min) if not alignment_df.empty else None,
        "median_delta_source_chi": float(np.nanmedian(alignment_df["delta_source_chi"])) if not alignment_df.empty else None,
        "median_delta_source_lambda2": float(np.nanmedian(alignment_df["delta_source_lambda2"])) if not alignment_df.empty else None,
        "global_t0_control_pass": bool(alignment_df["t0_control_flag"].all()) if not alignment_df.empty else None,
        "global_asymmetry_pass": bool(alignment_df["asymmetry_valid_flag"].all()) if not alignment_df.empty else None,
        "final_decision": str(decision_df[decision_df["aggregation_level"] == "global"]["final_decision"].iat[0]) if not decision_df.empty else "",
        "interpretation": "robust de-Broglie-interference candidate" if not decision_df.empty else "",
    }

    write_json(run_root / "V0_source_scan" / "source_summary.json", source_summary_payload)
    write_json(run_root / "M33_readout_scan" / "readout_summary.json", readout_summary_payload)
    write_json(run_root / "combined" / "combined_summary.json", combined_summary_payload)

    manifest_path = run_root / "run_manifest.json"
    with open(manifest_path, "r", encoding="utf-8") as handle:
        manifest = json.load(handle)
    manifest["status"] = "completed"
    manifest["timestamp_utc"] = datetime.now(timezone.utc).isoformat()
    with open(manifest_path, "w", encoding="utf-8") as handle:
        json.dump(manifest, handle, indent=2)

    write_report(run_root, decision_df)
    LOGGER.info("Completed run. Output written to %s", run_root)


if __name__ == "__main__":
    main()
