#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import math
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from statistics import mean
from typing import Any

import numpy as np
import yaml

from loader import load_export_class_data


def now_utc_iso() -> str:
    return (
        datetime.now(timezone.utc)
        .replace(microsecond=0)
        .isoformat()
        .replace("+00:00", "Z")
    )


def load_yaml(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    if not isinstance(data, dict):
        raise ValueError(f"Config root must be a mapping: {path}")
    return data


def ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def write_json(path: Path, payload: dict[str, Any]) -> None:
    ensure_dir(path.parent)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")


def write_md(path: Path, text: str) -> None:
    ensure_dir(path.parent)
    path.write_text(text, encoding="utf-8")


def normalize_max_abs(matrix: np.ndarray, epsilon: float) -> np.ndarray:
    max_abs = float(np.max(np.abs(matrix))) if matrix.size else 0.0
    denom = max(max_abs, epsilon)
    return matrix / denom


def minmax_unit(x: np.ndarray, epsilon: float) -> np.ndarray:
    x_min = float(np.min(x))
    x_max = float(np.max(x))
    span = max(x_max - x_min, epsilon)
    return (x - x_min) / span


def pair_units_from_export_data(export_data: Any) -> list[Any]:
    if hasattr(export_data, "pair_units"):
        return list(getattr(export_data, "pair_units") or [])
    if isinstance(export_data, dict):
        return list(export_data.get("pair_units", []) or [])
    return []


def source_files_from_export_data(export_data: Any) -> list[str]:
    if hasattr(export_data, "source_files"):
        files = getattr(export_data, "source_files") or []
        return [str(x) for x in files]
    if isinstance(export_data, dict):
        return [str(x) for x in export_data.get("source_files", []) or []]
    return []


def adjacency_from_pair_units(pair_units: list[Any], n_nodes: int) -> np.ndarray:
    adj = np.zeros((n_nodes, n_nodes), dtype=int)
    for pu in pair_units:
        i = j = None
        if isinstance(pu, dict):
            i = pu.get("i", pu.get("src", pu.get("u")))
            j = pu.get("j", pu.get("dst", pu.get("v")))
        else:
            for left_name in ("i", "src", "u"):
                if hasattr(pu, left_name):
                    i = getattr(pu, left_name)
                    break
            for right_name in ("j", "dst", "v"):
                if hasattr(pu, right_name):
                    j = getattr(pu, right_name)
                    break
        if i is None or j is None:
            continue
        try:
            ii = int(i)
            jj = int(j)
        except Exception:
            continue
        if 0 <= ii < n_nodes and 0 <= jj < n_nodes and ii != jj:
            adj[ii, jj] = 1
            adj[jj, ii] = 1
    return adj


def load_npz_payload_from_export_data(export_data: Any) -> tuple[Path | None, dict[str, np.ndarray] | None]:
    src_files = source_files_from_export_data(export_data)
    if not src_files:
        return None, None

    src = Path(src_files[0]).resolve()
    if not src.exists():
        return src, None

    with np.load(src, allow_pickle=True) as data:
        payload = {k: data[k] for k in data.files}
    return src, payload


def find_preferred_matrix_in_payload(
    payload: dict[str, np.ndarray] | None,
    preference_order: list[str],
) -> tuple[str | None, np.ndarray | None]:
    if payload is None:
        return None, None
    for field in preference_order:
        if field in payload:
            arr = np.asarray(payload[field], dtype=float)
            return field, arr
    return None, None


@dataclass
class BridgeState:
    A: np.ndarray
    theta: np.ndarray
    phi_geom: np.ndarray
    d_eff: np.ndarray
    neighborhoods: dict[int, list[int]]
    diagnostics: dict[str, float | str | bool | None]


def construct_A(
    matrix: np.ndarray,
    adjacency: np.ndarray | None,
    cfg: dict[str, Any],
) -> np.ndarray:
    amp_cfg = cfg["coarse_graining"]["amplitude_proxy"]
    epsilon = float(amp_cfg["epsilon"])
    use_abs = bool(amp_cfg.get("use_absolute_value", True))
    use_neighborhood_weighting = bool(amp_cfg.get("neighborhood_weighting", True))
    normalize_to_unit = bool(amp_cfg.get("normalize_to_unit_interval", True))

    M = np.abs(matrix) if use_abs else matrix.copy()

    if use_neighborhood_weighting and adjacency is not None and adjacency.shape == M.shape:
        weighted = M * (1.0 + adjacency.astype(float))
    else:
        weighted = M

    A = np.mean(weighted, axis=1)

    if normalize_to_unit:
        A = minmax_unit(A, epsilon)

    return np.maximum(A, epsilon)


def construct_theta(
    matrix: np.ndarray,
    cfg: dict[str, Any],
) -> np.ndarray:
    phase_cfg = cfg["coarse_graining"]["phase_proxy"]
    epsilon = float(phase_cfg["epsilon"])
    center_by_global_mean = bool(phase_cfg.get("center_by_global_mean", True))

    theta = np.mean(matrix.copy(), axis=1)

    if center_by_global_mean:
        theta = theta - float(np.mean(theta))

    denom = max(float(np.max(np.abs(theta))) if theta.size else 0.0, epsilon)
    return theta / denom


def apply_regime_and_coupling(
    A: np.ndarray,
    theta: np.ndarray,
    cfg: dict[str, Any],
    regime_name: str,
) -> tuple[np.ndarray, np.ndarray, dict[str, float | bool]]:
    reg = cfg["regimes"][regime_name]
    coupling = cfg["coarse_graining"]["coupling"]

    theta_visibility = float(reg["theta_visibility"])
    phase_averaging_strength = float(reg["phase_averaging_strength"])

    a_theta_coupling = float(coupling["a_theta_coupling"])
    theta_feedback_weight = float(coupling["theta_feedback_weight"])
    stabilization_weight = float(coupling["stabilization_weight"])

    theta_reg = theta_visibility * theta
    modulation = 1.0 + a_theta_coupling * theta_feedback_weight * np.tanh(theta_reg)

    A_mod = stabilization_weight * A + (1.0 - stabilization_weight) * (A * modulation)
    theta_mod = (1.0 - phase_averaging_strength) * theta_reg

    meta = {
        "theta_visibility": theta_visibility,
        "phase_averaging_strength": phase_averaging_strength,
        "a_theta_coupling_active": abs(a_theta_coupling) > 0.0,
    }
    return A_mod, theta_mod, meta


def construct_phi_geom(A: np.ndarray, cfg: dict[str, Any]) -> np.ndarray:
    pg = cfg["geometry_projection"]["phi_geom"]
    epsilon = float(pg["epsilon"])
    return np.log(np.maximum(A, epsilon) + epsilon)


def construct_d_eff(
    phi_geom: np.ndarray,
    adjacency: np.ndarray | None,
    cfg: dict[str, Any],
) -> np.ndarray:
    ed = cfg["geometry_projection"]["effective_distance"]
    epsilon = float(ed["epsilon"])
    n = len(phi_geom)
    d = np.zeros((n, n), dtype=float)

    for i in range(n):
        for j in range(n):
            if i == j:
                d[i, j] = 0.0
            else:
                d[i, j] = abs(float(phi_geom[i]) - float(phi_geom[j]))

    if bool(ed.get("add_graph_constraint", True)) and adjacency is not None and adjacency.shape == d.shape:
        penalty = np.where(adjacency > 0, 1.0, 2.0)
        d = d * penalty

    d = np.maximum(d, 0.0)
    d[np.diag_indices_from(d)] = 0.0
    d = np.where(np.isfinite(d), d, 1.0 / epsilon)
    return d


def construct_neighborhoods(
    d_eff: np.ndarray,
    cfg: dict[str, Any],
) -> dict[int, list[int]]:
    nb = cfg["geometry_projection"]["neighborhoods"]
    quantile = float(nb["quantile"])
    minimum_neighbors = int(nb["minimum_neighbors"])

    n = d_eff.shape[0]
    offdiag = d_eff[~np.eye(n, dtype=bool)]
    if offdiag.size == 0:
        return {i: [] for i in range(n)}

    threshold = float(np.quantile(offdiag, quantile))
    neighborhoods: dict[int, list[int]] = {}

    for i in range(n):
        neigh = [j for j in range(n) if j != i and d_eff[i, j] <= threshold]
        if len(neigh) < minimum_neighbors:
            ranked = np.argsort(d_eff[i])
            neigh = [int(j) for j in ranked if j != i][:minimum_neighbors]
        neighborhoods[i] = neigh
    return neighborhoods


def recompute_A_under_perturbation(
    matrix: np.ndarray,
    adjacency: np.ndarray | None,
    cfg: dict[str, Any],
    strength: float,
    rng: np.random.Generator,
) -> np.ndarray:
    pert = rng.normal(loc=0.0, scale=strength, size=matrix.shape)
    pert = 0.5 * (pert + pert.T)
    np.fill_diagonal(pert, 0.0)
    mat2 = matrix + pert
    return construct_A(mat2, adjacency, cfg)


def structure_stability_score(
    matrix: np.ndarray,
    adjacency: np.ndarray | None,
    A_ref: np.ndarray,
    cfg: dict[str, Any],
    seed: int,
) -> float:
    dcfg = cfg["diagnostics"]["structure_stability_score"]
    strength = float(dcfg["perturbation_strength"])
    n_trials = int(dcfg["n_trials"])

    rng = np.random.default_rng(seed)
    diffs = []
    for _ in range(n_trials):
        A_new = recompute_A_under_perturbation(matrix, adjacency, cfg, strength, rng)
        diffs.append(float(np.mean(np.abs(A_new - A_ref))))
    avg_diff = float(mean(diffs)) if diffs else 0.0
    return max(0.0, 1.0 - avg_diff)


def phase_influence_score(
    A_uncoupled: np.ndarray,
    A_coupled: np.ndarray,
) -> float:
    diff = float(np.mean(np.abs(A_coupled - A_uncoupled)))
    denom = max(float(np.mean(np.abs(A_uncoupled))), 1.0e-12)
    return diff / denom


def geometry_readability_score(
    d_eff: np.ndarray,
    neighborhoods: dict[int, list[int]],
    phi_geom: np.ndarray,
    cfg: dict[str, Any],
) -> float:
    gcfg = cfg["diagnostics"]["geometry_readability_score"]
    weights = gcfg["weights"]

    finite_fraction = float(np.mean(np.isfinite(d_eff)))

    neighborhood_sizes = [len(v) for v in neighborhoods.values()]
    if neighborhood_sizes:
        size_mean = float(mean(neighborhood_sizes))
        size_std = float(np.std(neighborhood_sizes))
        neighborhood_stability = 1.0 / (1.0 + size_std / max(size_mean, 1.0e-12))
    else:
        neighborhood_stability = 0.0

    phi_std = float(np.std(phi_geom))
    phi_geom_variation = min(1.0, phi_std)

    return float(
        float(weights["distance_finiteness"]) * finite_fraction
        + float(weights["neighborhood_stability"]) * neighborhood_stability
        + float(weights["phi_geom_variation"]) * phi_geom_variation
    )


def build_readout(
    dataset_id: str,
    regime: str,
    source_matrix_name: str,
    diagnostics: dict[str, Any],
    claims: list[dict[str, str]],
) -> str:
    lines = [
        "# Bridge Minimal Model Readout",
        "",
        f"- dataset_id: `{dataset_id}`",
        f"- regime: `{regime}`",
        f"- source_matrix: `{source_matrix_name}`",
        "",
        "## Diagnostiken",
        f"- structure_stability_score: `{diagnostics.get('structure_stability_score')}`",
        f"- phase_influence_score: `{diagnostics.get('phase_influence_score')}`",
        f"- geometry_readability_score: `{diagnostics.get('geometry_readability_score')}`",
        f"- a_theta_coupling_active: `{diagnostics.get('a_theta_coupling_active')}`",
        "",
        "## Arbeitslesart",
        "- `A` fungiert als geometrisch lesbarer Makroproxy.",
        "- `theta` trägt Interferenz-/Phasenstruktur und moduliert `A`.",
        "- `phi_geom` ist die erste geometrienahe Projektion aus `A`.",
        "- `d_eff` ist noch kein Beweis von Geometrie, aber ein Kandidat für nachfolgende Metriktests.",
        "",
        "## Direkte nächste Tests",
    ]
    for item in claims:
        lines.append(f"- {item['id']}: {item['text']}")
    lines.append("")
    return "\n".join(lines)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run bridge minimal model v1.")
    parser.add_argument("--config", required=True, help="Path to YAML config.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    cfg_path = Path(args.config).resolve()
    cfg = load_yaml(cfg_path)

    output_dir = Path(cfg["run"]["output_dir"]).resolve()
    ensure_dir(output_dir)

    dataset_roots: list[str] = cfg["inputs"]["dataset_roots"]
    export_classes: list[str] = cfg["inputs"]["export_classes"]
    export_pattern = cfg["inputs"]["export_pattern"]
    search_mode = cfg["inputs"]["search_mode"]

    default_regime = cfg["regimes"]["default"]
    preference_order: list[str] = cfg["coarse_graining"]["input_preference_order"]
    normalization_eps = float(cfg["coarse_graining"]["normalization"]["epsilon"])
    seed = int(cfg["run"]["seed"])

    all_states: dict[str, Any] = {}
    all_claims: dict[str, Any] = {}
    summary_rows: list[dict[str, Any]] = []

    for dataset_root in dataset_roots:
        dataset_path = Path(dataset_root).resolve()
        dataset_id = dataset_path.name

        for export_class in export_classes:
            export_data = load_export_class_data(
                export_root=dataset_path,
                export_class=export_class,
                export_pattern=export_pattern,
                search_mode=search_mode,
                loader_cfg=cfg,
            )

            src_path, payload = load_npz_payload_from_export_data(export_data)
            src_files = [str(src_path)] if src_path is not None else []
            loaded_matrix_name, M = find_preferred_matrix_in_payload(payload, preference_order)

            if M is None:
                if cfg["validation"]["fail_on_missing_all_matrices"]:
                    available = sorted(payload.keys()) if payload else []
                    raise ValueError(
                        f"No preferred matrix found for dataset={dataset_id}, class={export_class}. "
                        f"Preferred={preference_order}, available={available}, npz={src_path}"
                    )
                continue

            M = np.asarray(M, dtype=float)
            if M.ndim != 2 or M.shape[0] != M.shape[1]:
                raise ValueError(
                    f"Preferred matrix must be square for dataset={dataset_id}, class={export_class}"
                )

            if cfg["coarse_graining"]["normalization"]["enabled"]:
                M = normalize_max_abs(M, normalization_eps)

            n_nodes = M.shape[0]
            pair_units = pair_units_from_export_data(export_data)
            adjacency = adjacency_from_pair_units(pair_units, n_nodes)
            if not np.any(adjacency):
                adjacency = (np.abs(M) > normalization_eps).astype(int)
                np.fill_diagonal(adjacency, 0)

            A_base = construct_A(M, adjacency, cfg)
            theta_base = construct_theta(M, cfg)

            A_reg, theta_reg, regime_meta = apply_regime_and_coupling(
                A=A_base,
                theta=theta_base,
                cfg=cfg,
                regime_name=default_regime,
            )

            A_uncoupled = A_base.copy()

            phi_geom = construct_phi_geom(A_reg, cfg)
            d_eff = construct_d_eff(phi_geom, adjacency, cfg)
            neighborhoods = construct_neighborhoods(d_eff, cfg)

            stability = structure_stability_score(
                matrix=M,
                adjacency=adjacency,
                A_ref=A_reg,
                cfg=cfg,
                seed=seed,
            )
            phase_score = phase_influence_score(A_uncoupled=A_uncoupled, A_coupled=A_reg)
            geometry_score = geometry_readability_score(
                d_eff=d_eff,
                neighborhoods=neighborhoods,
                phi_geom=phi_geom,
                cfg=cfg,
            )

            diagnostics = {
                "structure_stability_score": float(stability),
                "phase_influence_score": float(phase_score),
                "geometry_readability_score": float(geometry_score),
                "a_theta_coupling_active": bool(regime_meta["a_theta_coupling_active"]),
                "theta_visibility": float(regime_meta["theta_visibility"]),
                "phase_averaging_strength": float(regime_meta["phase_averaging_strength"]),
            }

            if cfg["validation"]["require_nontrivial_A"]:
                if float(np.std(A_reg)) <= 1.0e-15:
                    raise ValueError(f"A is trivial for dataset={dataset_id}, class={export_class}")

            if cfg["validation"]["require_nonconstant_theta_unless_decoupling_test"]:
                if float(np.std(theta_reg)) <= 1.0e-15:
                    raise ValueError(f"theta is constant/trivial for dataset={dataset_id}, class={export_class}")

            if cfg["validation"]["fail_on_nan_fields"]:
                for name, arr in {
                    "A": A_reg,
                    "theta": theta_reg,
                    "phi_geom": phi_geom,
                    "d_eff": d_eff,
                }.items():
                    if np.isnan(arr).any():
                        raise ValueError(f"NaN detected in {name} for dataset={dataset_id}, class={export_class}")

            claims = list(cfg["testable_claims"]["claims"])

            key = f"{dataset_id}::{export_class}"
            state_payload = {
                "run_id": cfg["run"]["run_id"],
                "dataset_id": dataset_id,
                "dataset_root": str(dataset_path),
                "export_class": export_class,
                "regime": default_regime,
                "source_files": src_files,
                "source_matrix_name": loaded_matrix_name,
                "available_npz_fields": sorted(payload.keys()) if payload else [],
                "state_fields": {
                    "A": A_reg.tolist(),
                    "theta": theta_reg.tolist(),
                    "phi_geom": phi_geom.tolist(),
                },
                "effective_structure": {
                    "d_eff": d_eff.tolist(),
                    "neighborhoods": {str(k): v for k, v in neighborhoods.items()},
                    "graph_proxy": adjacency.tolist(),
                },
                "diagnostics": diagnostics,
                "testable_claims_ready": [c["id"] for c in claims],
                "timestamp_utc": now_utc_iso(),
            }
            all_states[key] = state_payload
            all_claims[key] = {"claims": claims}

            local_dir = output_dir / dataset_id / export_class
            ensure_dir(local_dir)

            write_json(local_dir / cfg["outputs"]["filenames"]["state_json"], state_payload)
            write_json(local_dir / cfg["outputs"]["filenames"]["claims_json"], {"claims": claims})
            write_md(
                local_dir / cfg["outputs"]["filenames"]["readout_md"],
                build_readout(
                    dataset_id=dataset_id,
                    regime=default_regime,
                    source_matrix_name=loaded_matrix_name or "unknown",
                    diagnostics=diagnostics,
                    claims=claims,
                ),
            )

            summary_rows.append(
                {
                    "dataset_id": dataset_id,
                    "export_class": export_class,
                    "regime": default_regime,
                    "source_matrix_name": loaded_matrix_name,
                    "structure_stability_score": float(stability),
                    "phase_influence_score": float(phase_score),
                    "geometry_readability_score": float(geometry_score),
                }
            )

    write_json(output_dir / "bridge_minimal_model_state.json", all_states)
    write_json(output_dir / "bridge_minimal_model_claims.json", all_claims)

    summary_md_lines = [
        "# Bridge Minimal Model v1 — Global Summary",
        "",
        f"- run_id: `{cfg['run']['run_id']}`",
        f"- timestamp_utc: `{now_utc_iso()}`",
        "",
        "## Summary Rows",
        "",
    ]
    for row in summary_rows:
        summary_md_lines.append(
            f"- {row['dataset_id']} / {row['export_class']} / {row['regime']}: "
            f"A-source=`{row['source_matrix_name']}`, "
            f"stability={row['structure_stability_score']:.4f}, "
            f"phase_influence={row['phase_influence_score']:.4f}, "
            f"geometry_readability={row['geometry_readability_score']:.4f}"
        )
    summary_md_lines.append("")
    write_md(output_dir / "bridge_minimal_model_readout.md", "\n".join(summary_md_lines))

    print(f"[OK] Bridge minimal model run complete: {cfg['run']['run_id']}")
    print(f"[OK] Output written to: {output_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
