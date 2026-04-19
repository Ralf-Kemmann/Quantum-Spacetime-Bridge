from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Set, Tuple

import numpy as np
import pandas as pd
import yaml


@dataclass(slots=True)
class M38aConfig:
    enabled: bool
    k0_values: List[float]
    sigma_k_values: List[float]
    t_values: List[float]
    v: float
    nu_values: List[float]
    k_min: float
    k_max: float
    n_k: int
    x_min: float
    x_max: float
    n_x: int
    dispersion_modes: List[str]
    class_modes: List[str]
    output_root: Path


def resolve_path(project_root: Path, p: Path) -> Path:
    return p if p.is_absolute() else project_root / p


def safe_json_value(x: Any) -> Any:
    if isinstance(x, dict):
        return {str(k): safe_json_value(v) for k, v in x.items()}
    if isinstance(x, (list, tuple, set)):
        return [safe_json_value(v) for v in x]
    if isinstance(x, np.ndarray):
        return [safe_json_value(v) for v in x.tolist()]
    if isinstance(x, (np.floating, float)):
        return None if not np.isfinite(x) else float(x)
    if isinstance(x, (np.integer, int)):
        return int(x)
    if isinstance(x, (np.bool_, bool)):
        return bool(x)
    try:
        if pd.isna(x):
            return None
    except Exception:
        pass
    return x


def write_json(path: Path, payload: Dict[str, Any]) -> None:
    with path.open("w", encoding="utf-8") as f:
        json.dump({k: safe_json_value(v) for k, v in payload.items()}, f, indent=2, ensure_ascii=False)


def load_config(path: Path) -> tuple[M38aConfig, Dict[str, Any]]:
    with path.open("r", encoding="utf-8") as f:
        raw = yaml.safe_load(f)

    block = raw["m38a_dispersion_test"]
    cfg = M38aConfig(
        enabled=bool(block["enabled"]),
        k0_values=[float(x) for x in block["packet"]["k0_values"]],
        sigma_k_values=[float(x) for x in block["packet"]["sigma_k_values"]],
        t_values=[float(x) for x in block["packet"]["t_values"]],
        v=float(block["packet"]["v"]),
        nu_values=[float(x) for x in block["packet"]["nu_values"]],
        k_min=float(block["grid"]["k_min"]),
        k_max=float(block["grid"]["k_max"]),
        n_k=int(block["grid"]["n_k"]),
        x_min=float(block["grid"]["x_min"]),
        x_max=float(block["grid"]["x_max"]),
        n_x=int(block["grid"]["n_x"]),
        dispersion_modes=[str(x) for x in block["comparison"]["dispersion_modes"]],
        class_modes=[str(x) for x in block["comparison"]["class_modes"]],
        output_root=Path(block["output"]["root"]),
    )
    return cfg, raw


def gaussian_amplitude(k: np.ndarray, k0: float, sigma_k: float) -> np.ndarray:
    sigma = max(float(sigma_k), 1.0e-12)
    return np.exp(-((k - k0) ** 2) / (4.0 * sigma * sigma))


def omega_of_k(k: np.ndarray, v: float, nu: float, mode: str) -> np.ndarray:
    if mode == "none":
        return v * k
    if mode == "quadratic":
        return v * k + nu * (k ** 2)
    raise ValueError(f"Unsupported dispersion mode: {mode}")


def normalize_prob_density(prob: np.ndarray, grid: np.ndarray) -> np.ndarray:
    integ = np.trapezoid(prob, grid)
    if integ <= 0:
        return np.full_like(prob, 1.0 / len(prob))
    return prob / integ


def evolve_packet(k_grid: np.ndarray, x_grid: np.ndarray, k0: float, sigma_k: float, t: float, v: float, nu: float, mode: str) -> tuple[np.ndarray, np.ndarray]:
    amp_k = gaussian_amplitude(k_grid, k0, sigma_k)
    phase_k = np.exp(-1j * omega_of_k(k_grid, v, nu, mode) * t)
    psi_k = amp_k * phase_k
    dk = float(k_grid[1] - k_grid[0])

    phase_xk = np.exp(1j * np.outer(x_grid, k_grid))
    psi_x = phase_xk @ psi_k * dk / np.sqrt(2.0 * np.pi)

    prob_x = np.abs(psi_x) ** 2
    prob_x = normalize_prob_density(prob_x, x_grid)
    return psi_x, prob_x


def packet_metrics(x_grid: np.ndarray, psi_x: np.ndarray, prob_x: np.ndarray) -> Dict[str, float]:
    x_center = float(np.trapezoid(x_grid * prob_x, x_grid))
    var = float(np.trapezoid(((x_grid - x_center) ** 2) * prob_x, x_grid))
    x_width = float(np.sqrt(max(var, 0.0)))

    if x_width > 0:
        skew = float(np.trapezoid((((x_grid - x_center) / x_width) ** 3) * prob_x, x_grid))
        kurt = float(np.trapezoid((((x_grid - x_center) / x_width) ** 4) * prob_x, x_grid))
    else:
        skew = 0.0
        kurt = 0.0

    phase = np.unwrap(np.angle(psi_x))
    if len(x_grid) >= 3:
        d2 = np.gradient(np.gradient(phase, x_grid), x_grid)
        phase_curvature_proxy = float(np.trapezoid(np.abs(d2) * prob_x, x_grid))
    else:
        phase_curvature_proxy = 0.0

    return {
        "x_center": x_center,
        "x_width": x_width,
        "x_skewness": skew,
        "x_kurtosis": kurt,
        "phase_curvature_proxy": phase_curvature_proxy,
    }


def modal_amplitudes(p_values: np.ndarray, k0: float, sigma_k: float, t: float, v: float, nu: float, mode: str) -> np.ndarray:
    amp = gaussian_amplitude(p_values, k0, sigma_k)
    phase = np.exp(-1j * omega_of_k(p_values, v, nu, mode) * t)
    z = amp * phase
    norm = np.sqrt(np.sum(np.abs(z) ** 2))
    return z if norm <= 0 else z / norm


def compute_pair_table(
    run_id: str,
    case_id: str,
    dispersion_mode: str,
    p_family: str,
    p_values: np.ndarray,
    k0: float,
    sigma_k: float,
    t: float,
    v: float,
    nu: float,
) -> pd.DataFrame:
    z = modal_amplitudes(p_values, k0, sigma_k, t, v, nu, dispersion_mode)
    rows: List[Dict[str, Any]] = []
    n = len(p_values)
    for i in range(n):
        for j in range(i + 1, n):
            pair_weight = float(np.abs(z[i]) ** 2 * np.abs(z[j]) ** 2)
            kbar_ij = float(np.real(z[i] * np.conj(z[j])))
            contrib_primary = pair_weight * abs(kbar_ij)
            rows.append(
                {
                    "run_id": run_id,
                    "case_id": case_id,
                    "dispersion_mode": dispersion_mode,
                    "p_family": p_family,
                    "k0": k0,
                    "sigma_k": sigma_k,
                    "t": t,
                    "v": v,
                    "nu": nu,
                    "pair_i": i,
                    "pair_j": j,
                    "p_i": float(p_values[i]),
                    "p_j": float(p_values[j]),
                    "delta_p": float(p_values[i] - p_values[j]),
                    "delta_p2": float((p_values[i] ** 2) - (p_values[j] ** 2)),
                    "pair_weight": pair_weight,
                    "kbar_ij": kbar_ij,
                    "contrib_primary": contrib_primary,
                }
            )

    pair_df = pd.DataFrame(rows).sort_values("contrib_primary", ascending=False).reset_index(drop=True)
    total = float(pair_df["contrib_primary"].sum())
    pair_df["normalized_contrib_primary"] = 0.0 if total <= 0 else pair_df["contrib_primary"] / total
    pair_df["pair_rank_primary"] = np.arange(1, len(pair_df) + 1)
    return pair_df


def concentration_score(pair_df: pd.DataFrame) -> tuple[float, float, float, float, float]:
    arr = pair_df["normalized_contrib_primary"].to_numpy(dtype=float)
    if arr.size == 0:
        return 0.0, 0.0, 0.0, 0.0, 0.0
    top1 = float(arr[:1].sum())
    top3 = float(arr[:3].sum())
    top5 = float(arr[:5].sum())
    eff = 0.0 if np.sum(arr ** 2) <= 0 else float(1.0 / np.sum(arr ** 2))
    proxy = top3
    return top1, top3, top5, eff, proxy


def class_summary_from_pairs(
    pair_df: pd.DataFrame,
    run_id: str,
    case_id: str,
    dispersion_mode: str,
    p_family: str,
    k0: float,
    sigma_k: float,
    t: float,
    v: float,
    nu: float,
    class_modes: List[str],
) -> pd.DataFrame:
    rows: List[Dict[str, Any]] = []
    for class_mode in class_modes:
        if class_mode == "delta_p":
            class_label_series = pair_df["delta_p"].map(lambda x: f"dp={x:.6g}")
        elif class_mode == "delta_p2":
            class_label_series = pair_df["delta_p2"].map(lambda x: f"dp2={x:.6g}")
        else:
            raise ValueError(f"Unsupported class_mode: {class_mode}")

        tmp = pair_df.copy()
        tmp["class_label"] = class_label_series
        grouped = (
            tmp.groupby("class_label", dropna=False)["contrib_primary"]
            .sum()
            .reset_index(name="sum_contrib_primary")
            .sort_values("sum_contrib_primary", ascending=False)
            .reset_index(drop=True)
        )
        total = float(grouped["sum_contrib_primary"].sum())
        grouped["normalized_class_contrib"] = 0.0 if total <= 0 else grouped["sum_contrib_primary"] / total
        grouped["class_rank"] = np.arange(1, len(grouped) + 1)

        for row in grouped.itertuples(index=False):
            rows.append(
                {
                    "run_id": run_id,
                    "case_id": case_id,
                    "dispersion_mode": dispersion_mode,
                    "p_family": p_family,
                    "k0": k0,
                    "sigma_k": sigma_k,
                    "t": t,
                    "v": v,
                    "nu": nu,
                    "class_mode": class_mode,
                    "class_label": row.class_label,
                    "class_rank": int(row.class_rank),
                    "sum_contrib_primary": float(row.sum_contrib_primary),
                    "normalized_class_contrib": float(row.normalized_class_contrib),
                }
            )
    return pd.DataFrame(rows)


def top_class_score(class_df: pd.DataFrame, class_mode: str, top_k: int = 3) -> float:
    sub = class_df[class_df["class_mode"] == class_mode].sort_values("class_rank").head(top_k)
    if sub.empty:
        return 0.0
    return float(sub["normalized_class_contrib"].sum())


def comparison_label(delta_width_x: float, pair_shift: float, dp_shift: float, dp2_shift: float) -> str:
    if delta_width_x > 0 and dp2_shift >= -0.02:
        return "delta_p2_preserved"
    if delta_width_x > 0 and dp2_shift < -0.02:
        return "dispersion_sensitive"
    return "weak_change"


def main() -> None:
    parser = argparse.ArgumentParser(description="M.3.8a explicit null-vs-dispersion test")
    parser.add_argument("--project-root", required=True)
    parser.add_argument("--config", required=True)
    args = parser.parse_args()

    project_root = Path(args.project_root).resolve()
    config_path = Path(args.config).resolve()

    cfg, raw_cfg = load_config(config_path)
    if not cfg.enabled:
        print("M.3.8a disabled in config. Exiting.")
        return

    out_root = resolve_path(project_root, cfg.output_root)
    out_root.mkdir(parents=True, exist_ok=True)

    k_grid = np.linspace(cfg.k_min, cfg.k_max, cfg.n_k)
    x_grid = np.linspace(cfg.x_min, cfg.x_max, cfg.n_x)

    p_sets = raw_cfg.get("p_sets", {}).get("families", {})
    if not p_sets:
        raise ValueError("No p_sets.families found in config; M.3.8a needs discrete p-values for pair/class summaries.")

    run_id = config_path.stem

    case_rows = []
    metric_rows = []
    pair_top_rows = []
    class_frames = []
    comparison_rows = []

    packet_cache: Dict[Tuple[str, str, float, float, float, float], Dict[str, Any]] = {}

    for p_family, fam in p_sets.items():
        p_values = np.asarray(fam["p_values"], dtype=float)

        for k0 in cfg.k0_values:
            for sigma_k in cfg.sigma_k_values:
                psi0, prob0 = evolve_packet(k_grid, x_grid, k0, sigma_k, 0.0, cfg.v, 0.0, "none")
                base_metrics = packet_metrics(x_grid, psi0, prob0)

                for t in cfg.t_values:
                    for mode in cfg.dispersion_modes:
                        if mode == "none":
                            nu_list = [0.0]
                        elif mode == "quadratic":
                            nu_list = [float(nu) for nu in cfg.nu_values if abs(float(nu)) > 0.0]
                            if not nu_list:
                                nu_list = [0.0]
                        else:
                            raise ValueError(f"Unsupported dispersion_mode: {mode}")

                        for nu in nu_list:
                            case_id = f"{p_family}__k0={k0:.6g}__sk={sigma_k:.6g}__t={t:.6g}__mode={mode}__nu={nu:.6g}"

                            psi_x, prob_x = evolve_packet(k_grid, x_grid, k0, sigma_k, t, cfg.v, nu, mode)
                            metrics = packet_metrics(x_grid, psi_x, prob_x)
                            x_width_delta = float(metrics["x_width"] - base_metrics["x_width"])

                            case_rows.append(
                                {
                                    "run_id": run_id,
                                    "case_id": case_id,
                                    "dispersion_mode": mode,
                                    "p_family": p_family,
                                    "k0": k0,
                                    "sigma_k": sigma_k,
                                    "t": t,
                                    "v": cfg.v,
                                    "nu": nu,
                                    "x_grid_size": cfg.n_x,
                                    "k_grid_size": cfg.n_k,
                                    "norm_ok": 1,
                                }
                            )

                            metric_rows.append(
                                {
                                    "run_id": run_id,
                                    "case_id": case_id,
                                    "dispersion_mode": mode,
                                    "p_family": p_family,
                                    "k0": k0,
                                    "sigma_k": sigma_k,
                                    "t": t,
                                    "v": cfg.v,
                                    "nu": nu,
                                    "x_center": metrics["x_center"],
                                    "x_width": metrics["x_width"],
                                    "x_width_delta": x_width_delta,
                                    "x_skewness": metrics["x_skewness"],
                                    "x_kurtosis": metrics["x_kurtosis"],
                                    "phase_curvature_proxy": metrics["phase_curvature_proxy"],
                                }
                            )

                            pair_df = compute_pair_table(run_id, case_id, mode, p_family, p_values, k0, sigma_k, t, cfg.v, nu)
                            top1, top3, top5, eff, proxy = concentration_score(pair_df)
                            pair_top_rows.append(
                                {
                                    "run_id": run_id,
                                    "case_id": case_id,
                                    "dispersion_mode": mode,
                                    "p_family": p_family,
                                    "k0": k0,
                                    "sigma_k": sigma_k,
                                    "t": t,
                                    "v": cfg.v,
                                    "nu": nu,
                                    "n_pairs_total": int(len(pair_df)),
                                    "top1_share": top1,
                                    "top3_share": top3,
                                    "top5_share": top5,
                                    "effective_pair_count": eff,
                                    "dominance_label": "pair_dominated" if top3 > 0.7 else ("collective" if eff >= 6 else "mixed"),
                                }
                            )

                            class_df = class_summary_from_pairs(
                                pair_df, run_id, case_id, mode, p_family, k0, sigma_k, t, cfg.v, nu, cfg.class_modes
                            )
                            class_frames.append(class_df)

                            packet_cache[(p_family, mode, k0, sigma_k, t, nu)] = {
                                "pair_df": pair_df,
                                "class_df": class_df,
                                "metrics": metrics,
                                "x_width_delta": x_width_delta,
                                "pair_proxy": proxy,
                                "dp_proxy": top_class_score(class_df, "delta_p", top_k=3),
                                "dp2_proxy": top_class_score(class_df, "delta_p2", top_k=3),
                            }

    wavepacket_case_grid = pd.DataFrame(case_rows)
    wavepacket_metrics = pd.DataFrame(metric_rows)
    dispersion_pair_top_summary = pd.DataFrame(pair_top_rows)
    dispersion_class_summary = pd.concat(class_frames, ignore_index=True) if class_frames else pd.DataFrame()

    for p_family in p_sets.keys():
        for k0 in cfg.k0_values:
            for sigma_k in cfg.sigma_k_values:
                for t in cfg.t_values:
                    none_key = (p_family, "none", k0, sigma_k, t, 0.0)
                    if none_key not in packet_cache:
                        continue
                    ref = packet_cache[none_key]

                    quad_nus = [float(nu) for nu in cfg.nu_values if abs(float(nu)) > 0.0]
                    for nu in quad_nus:
                        quad_key = (p_family, "quadratic", k0, sigma_k, t, nu)
                        if quad_key not in packet_cache:
                            continue
                        test = packet_cache[quad_key]

                        pair_sep_none = ref["pair_proxy"]
                        pair_sep_quadratic = test["pair_proxy"]
                        dp_sep_none = ref["dp_proxy"]
                        dp_sep_quadratic = test["dp_proxy"]
                        dp2_sep_none = ref["dp2_proxy"]
                        dp2_sep_quadratic = test["dp2_proxy"]
                        delta_width_x = float(test["metrics"]["x_width"] - ref["metrics"]["x_width"])

                        comparison_rows.append(
                            {
                                "run_id": run_id,
                                "comparison_id": f"{p_family}__k0={k0:.6g}__sk={sigma_k:.6g}__t={t:.6g}__nu={nu:.6g}",
                                "p_family": p_family,
                                "k0": k0,
                                "sigma_k": sigma_k,
                                "t": t,
                                "v": cfg.v,
                                "nu": nu,
                                "pair_sep_none": pair_sep_none,
                                "pair_sep_quadratic": pair_sep_quadratic,
                                "delta_p_sep_none": dp_sep_none,
                                "delta_p_sep_quadratic": dp_sep_quadratic,
                                "delta_p2_sep_none": dp2_sep_none,
                                "delta_p2_sep_quadratic": dp2_sep_quadratic,
                                "delta_width_x": delta_width_x,
                                "pair_sep_shift": pair_sep_quadratic - pair_sep_none,
                                "delta_p_sep_shift": dp_sep_quadratic - dp_sep_none,
                                "delta_p2_sep_shift": dp2_sep_quadratic - dp2_sep_none,
                                "identity_shift_label": comparison_label(
                                    delta_width_x,
                                    pair_sep_quadratic - pair_sep_none,
                                    dp_sep_quadratic - dp_sep_none,
                                    dp2_sep_quadratic - dp2_sep_none,
                                ),
                            }
                        )

    dispersion_identity_comparison = pd.DataFrame(comparison_rows)

    if dispersion_identity_comparison.empty:
        summary = {
            "n_cases_total": int(len(wavepacket_case_grid)),
            "width_growth_detected_fraction": 0.0,
            "delta_p2_identity_preserved_fraction": 0.0,
            "delta_p_identity_preserved_fraction": 0.0,
            "pair_identity_preserved_fraction": 0.0,
            "dispersion_sensitive_fraction": 0.0,
            "dominant_preserved_identity_level": None,
            "final_label": "H0",
        }
    else:
        width_growth_detected_fraction = float((dispersion_identity_comparison["delta_width_x"] > 1e-6).mean())
        dp2_preserved = float((dispersion_identity_comparison["delta_p2_sep_quadratic"] >= 0.8 * dispersion_identity_comparison["delta_p2_sep_none"]).mean())
        dp_preserved = float((dispersion_identity_comparison["delta_p_sep_quadratic"] >= 0.8 * dispersion_identity_comparison["delta_p_sep_none"]).mean())
        pair_preserved = float((dispersion_identity_comparison["pair_sep_quadratic"] >= 0.8 * dispersion_identity_comparison["pair_sep_none"]).mean())
        dispersion_sensitive_fraction = float(((dispersion_identity_comparison["delta_width_x"] > 1e-6) & (dispersion_identity_comparison["identity_shift_label"] == "dispersion_sensitive")).mean())

        preserved_map = {
            "pair": pair_preserved,
            "delta_p_class": dp_preserved,
            "delta_p2_class": dp2_preserved,
        }
        dominant_preserved_identity_level = max(preserved_map, key=preserved_map.get)

        if width_growth_detected_fraction < 0.5:
            final_label = "H0"
        elif dp2_preserved >= 0.75:
            final_label = "H3" if dispersion_sensitive_fraction >= 0.4 else "H2"
        elif max(dp_preserved, pair_preserved) >= 0.5:
            final_label = "H1"
        else:
            final_label = "H1"

        summary = {
            "n_cases_total": int(len(wavepacket_case_grid)),
            "width_growth_detected_fraction": width_growth_detected_fraction,
            "delta_p2_identity_preserved_fraction": dp2_preserved,
            "delta_p_identity_preserved_fraction": dp_preserved,
            "pair_identity_preserved_fraction": pair_preserved,
            "dispersion_sensitive_fraction": dispersion_sensitive_fraction,
            "dominant_preserved_identity_level": dominant_preserved_identity_level,
            "final_label": final_label,
        }

    wavepacket_case_grid.to_csv(out_root / "wavepacket_case_grid.csv", index=False)
    wavepacket_metrics.to_csv(out_root / "wavepacket_metrics.csv", index=False)
    dispersion_pair_top_summary.to_csv(out_root / "dispersion_pair_top_summary.csv", index=False)
    dispersion_class_summary.to_csv(out_root / "dispersion_class_summary.csv", index=False)
    dispersion_identity_comparison.to_csv(out_root / "dispersion_identity_comparison.csv", index=False)
    write_json(out_root / "dispersion_summary.json", summary)

    report_lines = [
        "# M.3.8a Dispersion Test",
        "",
        f"- n_cases_total: {safe_json_value(summary['n_cases_total'])}",
        f"- width_growth_detected_fraction: {safe_json_value(summary['width_growth_detected_fraction'])}",
        f"- delta_p2_identity_preserved_fraction: {safe_json_value(summary['delta_p2_identity_preserved_fraction'])}",
        f"- delta_p_identity_preserved_fraction: {safe_json_value(summary['delta_p_identity_preserved_fraction'])}",
        f"- pair_identity_preserved_fraction: {safe_json_value(summary['pair_identity_preserved_fraction'])}",
        f"- dispersion_sensitive_fraction: {safe_json_value(summary['dispersion_sensitive_fraction'])}",
        f"- dominant_preserved_identity_level: {safe_json_value(summary['dominant_preserved_identity_level'])}",
        f"- final_label: {safe_json_value(summary['final_label'])}",
        "",
        "Note: This skeleton implements a minimal explicit packet evolution and a first-pass identity proxy",
        "via pair/class concentration scores. It is intended as a bridge toward later integration",
        "with the existing S1/S2/S3 reference logic.",
    ]
    (out_root / "dispersion_report.md").write_text("\n".join(report_lines) + "\n", encoding="utf-8")

    print(f"M.3.8a completed. Output written to: {out_root}")


if __name__ == "__main__":
    main()
