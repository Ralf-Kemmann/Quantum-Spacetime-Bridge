from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
import pandas as pd
import yaml


@dataclass(slots=True)
class ExportConfig:
    enabled: bool
    phase_pair_stats: Path
    pair_kernel_csv: Path
    summary_json: Path
    validation_csv: Path
    sign_zero_tolerance: float
    require_pair_order: bool
    drop_nonfinite_rows: bool
    sort_rows: bool


def resolve_path(project_root: Path, p: Path) -> Path:
    return p if p.is_absolute() else project_root / p


def safe_json_value(x: Any) -> Any:
    if isinstance(x, (np.floating, float)):
        return None if not np.isfinite(x) else float(x)
    if isinstance(x, (np.integer, int)):
        return int(x)
    if pd.isna(x):
        return None
    return x


def load_config(path: Path) -> ExportConfig:
    with path.open("r", encoding="utf-8") as f:
        raw = yaml.safe_load(f)

    block = raw["m35b_pair_kernel_export"]
    return ExportConfig(
        enabled=bool(block["enabled"]),
        phase_pair_stats=Path(block["input"]["phase_pair_stats"]),
        pair_kernel_csv=Path(block["output"]["pair_kernel_csv"]),
        summary_json=Path(block["output"]["summary_json"]),
        validation_csv=Path(block["output"]["validation_csv"]),
        sign_zero_tolerance=float(block["export"]["sign_zero_tolerance"]),
        require_pair_order=bool(block["export"]["require_pair_order"]),
        drop_nonfinite_rows=bool(block["export"]["drop_nonfinite_rows"]),
        sort_rows=bool(block["export"]["sort_rows"]),
    )


def load_full_yaml(path: Path) -> Dict[str, Any]:
    with path.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def infer_index_base(vals: pd.Series, n_modes: int) -> int:
    vals = vals.dropna().astype(int)
    if vals.empty:
        return 0
    mn = int(vals.min())
    mx = int(vals.max())
    if mn >= 1 and mx <= n_modes:
        return 1
    return 0


def infer_p_values_for_family(p_family: str, raw_cfg: Dict[str, Any]) -> np.ndarray:
    fam = raw_cfg["p_sets"]["families"][p_family]
    return np.asarray(fam["p_values"], dtype=float)


def maybe_fill_p_columns(df: pd.DataFrame, raw_cfg: Dict[str, Any]) -> pd.DataFrame:
    if "p_i" in df.columns and "p_j" in df.columns:
        return df

    out = df.copy()
    out["p_i"] = np.nan
    out["p_j"] = np.nan

    for p_family, g_idx in out.groupby("p_family").groups.items():
        p_values = infer_p_values_for_family(str(p_family), raw_cfg)
        sub = out.loc[g_idx, ["pair_i", "pair_j"]].copy()
        idx_base = infer_index_base(pd.concat([sub["pair_i"], sub["pair_j"]]), len(p_values))

        def map_idx(v: Any) -> float:
            try:
                ii = int(v) - idx_base
                if 0 <= ii < len(p_values):
                    return float(p_values[ii])
            except Exception:
                pass
            return np.nan

        out.loc[g_idx, "p_i"] = out.loc[g_idx, "pair_i"].map(map_idx)
        out.loc[g_idx, "p_j"] = out.loc[g_idx, "pair_j"].map(map_idx)

    return out


def compute_sign(x: float, tol: float) -> int:
    if not np.isfinite(x):
        return 0
    if x > tol:
        return 1
    if x < -tol:
        return -1
    return 0


def reconstruct_kbar_if_needed(df: pd.DataFrame) -> pd.DataFrame:
    """
    Skeleton-only fallback.

    Supported direct case:
    - kbar_ij already present

    Placeholder future reconstruction path:
    - from mean_cos_dphi if user stored it equivalently per pair/alpha
    """
    out = df.copy()

    if "kbar_ij" in out.columns:
        return out

    if "mean_cos_dphi" in out.columns:
        out["kbar_ij"] = out["mean_cos_dphi"].astype(float)
        return out

    raise NotImplementedError(
        "phase_pair_stats.csv does not contain 'kbar_ij' or a supported fallback "
        "column such as 'mean_cos_dphi'. For full reconstruction, add raw pairwise "
        "phase data and implement weighted x-averaging of cos(Delta phi_ij)."
    )


def validate_required_columns(df: pd.DataFrame, required: List[str]) -> None:
    missing = [c for c in required if c not in df.columns]
    if missing:
        raise ValueError(f"phase_pair_stats is missing required columns: {missing}")


def build_output_table(
    phase_df: pd.DataFrame,
    raw_cfg: Dict[str, Any],
    tol: float,
    require_pair_order: bool,
    drop_nonfinite_rows: bool,
) -> pd.DataFrame:
    work = reconstruct_kbar_if_needed(phase_df)
    validate_required_columns(work, ["run_id", "t", "p_family", "alpha", "pair_i", "pair_j", "kbar_ij"])

    work = maybe_fill_p_columns(work, raw_cfg)
    validate_required_columns(work, ["p_i", "p_j"])

    out = work[["run_id", "t", "p_family", "alpha", "pair_i", "pair_j", "p_i", "p_j", "kbar_ij"]].copy()
    out["kbar_ij"] = out["kbar_ij"].astype(float)
    out["kbar_abs_ij"] = out["kbar_ij"].abs()
    out["kbar_sign"] = out["kbar_ij"].map(lambda x: compute_sign(float(x), tol))

    nonfinite_mask = ~np.isfinite(out["kbar_ij"])
    if drop_nonfinite_rows:
        out = out.loc[~nonfinite_mask].copy()

    if require_pair_order:
        bad_mask = out["pair_i"].astype(float) >= out["pair_j"].astype(float)
        if bad_mask.any():
            bad_n = int(bad_mask.sum())
            raise ValueError(f"Found {bad_n} rows with pair_i >= pair_j")

    return out


def build_validation_table(out_df: pd.DataFrame, raw_cfg: Dict[str, Any], tol: float) -> pd.DataFrame:
    rows: List[Dict[str, Any]] = []

    for (run_id, t, p_family, alpha), g in out_df.groupby(["run_id", "t", "p_family", "alpha"], dropna=False):
        p_values = infer_p_values_for_family(str(p_family), raw_cfg)
        n_modes = len(p_values)
        expected_pairs = n_modes * (n_modes - 1) // 2
        found_pairs = len(g)

        finite_fraction = float(np.isfinite(g["kbar_ij"]).mean()) if len(g) else 0.0

        sign_ok = True
        for row in g.itertuples(index=False):
            expected_sign = compute_sign(float(row.kbar_ij), tol)
            if int(row.kbar_sign) != expected_sign:
                sign_ok = False
                break
            if not np.isclose(float(row.kbar_abs_ij), abs(float(row.kbar_ij)), atol=max(tol, 1e-15)):
                sign_ok = False
                break

        rows.append(
            {
                "run_id": run_id,
                "t": t,
                "p_family": p_family,
                "alpha": alpha,
                "expected_pairs": expected_pairs,
                "found_pairs": found_pairs,
                "pair_count_ok": int(found_pairs == expected_pairs),
                "finite_fraction": finite_fraction,
                "sign_consistency_ok": int(sign_ok),
            }
        )

    return pd.DataFrame(
        rows,
        columns=[
            "run_id",
            "t",
            "p_family",
            "alpha",
            "expected_pairs",
            "found_pairs",
            "pair_count_ok",
            "finite_fraction",
            "sign_consistency_ok",
        ],
    )


def build_summary(out_df: pd.DataFrame, validation_df: pd.DataFrame, source_origin: str) -> Dict[str, Any]:
    summary: Dict[str, Any] = {
        "run_id": str(out_df["run_id"].iloc[0]) if not out_df.empty else None,
        "n_rows": int(len(out_df)),
        "n_t_values": int(out_df["t"].nunique()) if not out_df.empty else 0,
        "n_p_families": int(out_df["p_family"].nunique()) if not out_df.empty else 0,
        "n_alpha_values": int(out_df["alpha"].nunique()) if not out_df.empty else 0,
        "n_pairs_per_family": {},
        "finite_fraction_global": float(np.isfinite(out_df["kbar_ij"]).mean()) if not out_df.empty else 0.0,
        "source_origin": source_origin,
        "all_pair_count_ok": bool(validation_df["pair_count_ok"].all()) if not validation_df.empty else False,
        "all_sign_consistency_ok": bool(validation_df["sign_consistency_ok"].all()) if not validation_df.empty else False,
    }

    if not out_df.empty:
        for p_family, g in out_df.groupby("p_family", dropna=False):
            counts = g.groupby(["run_id", "t", "p_family", "alpha"]).size()
            summary["n_pairs_per_family"][str(p_family)] = int(counts.iloc[0]) if not counts.empty else 0

    return {k: safe_json_value(v) if k != "n_pairs_per_family" else v for k, v in summary.items()}


def write_json(path: Path, payload: Dict[str, Any]) -> None:
    with path.open("w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2, ensure_ascii=False)


def main() -> None:
    parser = argparse.ArgumentParser(description="M.3.5b.1 exporter for source_pair_kernel_alpha.csv")
    parser.add_argument("--project-root", required=True, help="Project root directory")
    parser.add_argument("--config", required=True, help="Path to YAML config")
    args = parser.parse_args()

    project_root = Path(args.project_root).resolve()
    config_path = Path(args.config).resolve()

    cfg = load_config(config_path)
    if not cfg.enabled:
        print("m35b_pair_kernel_export disabled in config. Exiting.")
        return

    raw_cfg = load_full_yaml(config_path)

    phase_pair_stats_path = resolve_path(project_root, cfg.phase_pair_stats)
    pair_kernel_csv_path = resolve_path(project_root, cfg.pair_kernel_csv)
    summary_json_path = resolve_path(project_root, cfg.summary_json)
    validation_csv_path = resolve_path(project_root, cfg.validation_csv)

    pair_kernel_csv_path.parent.mkdir(parents=True, exist_ok=True)
    summary_json_path.parent.mkdir(parents=True, exist_ok=True)
    validation_csv_path.parent.mkdir(parents=True, exist_ok=True)

    phase_df = pd.read_csv(phase_pair_stats_path)

    source_origin = "phase_pair_stats.csv"
    out_df = build_output_table(
        phase_df=phase_df,
        raw_cfg=raw_cfg,
        tol=cfg.sign_zero_tolerance,
        require_pair_order=cfg.require_pair_order,
        drop_nonfinite_rows=cfg.drop_nonfinite_rows,
    )

    if cfg.sort_rows and not out_df.empty:
        out_df = out_df.sort_values(
            ["run_id", "t", "p_family", "alpha", "pair_i", "pair_j"],
            kind="stable",
        ).reset_index(drop=True)

    validation_df = build_validation_table(out_df, raw_cfg, cfg.sign_zero_tolerance)
    summary = build_summary(out_df, validation_df, source_origin)

    out_df.to_csv(pair_kernel_csv_path, index=False)
    validation_df.to_csv(validation_csv_path, index=False)
    write_json(summary_json_path, summary)

    print(f"M.3.5b.1 completed. Output written to: {pair_kernel_csv_path}")
    print(f"Validation written to: {validation_csv_path}")
    print(f"Summary written to: {summary_json_path}")


if __name__ == "__main__":
    main()
