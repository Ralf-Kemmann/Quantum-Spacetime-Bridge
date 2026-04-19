#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import math
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Any, Literal

import numpy as np


def sinc_unscaled(x: np.ndarray | float) -> np.ndarray | float:
    x_arr = np.asarray(x, dtype=float)
    out = np.ones_like(x_arr)
    mask = np.abs(x_arr) > 1e-15
    out[mask] = np.sin(x_arr[mask]) / x_arr[mask]
    if np.isscalar(x):
        return float(out)
    return out


@dataclass
class BaseConfig:
    mode: Literal["free", "force"]
    p: np.ndarray
    m: float
    t: float
    L: float
    theta: float
    hbar: float = 1.0
    c: float = 1.0
    ell0: float = 1.0
    s_min: float = 1.0
    epsilon: float = 1e-12
    F: float = 0.0
    weight: Literal["uniform"] = "uniform"

    def validate(self) -> None:
        if self.mode not in {"free", "force"}:
            raise ValueError("mode must be 'free' or 'force'")
        if self.p.ndim != 1 or len(self.p) < 2:
            raise ValueError("p must be a 1D array with at least two entries")
        if not np.all(np.isfinite(self.p)):
            raise ValueError("p contains non-finite values")
        if not np.isfinite(self.m) or self.m <= 0:
            raise ValueError("m must be positive")
        if not np.isfinite(self.L) or self.L <= 0:
            raise ValueError("L must be positive")
        if not np.isfinite(self.theta) or self.theta <= 0:
            raise ValueError("theta must be positive")
        if not np.isfinite(self.hbar) or self.hbar <= 0:
            raise ValueError("hbar must be positive")
        if not np.isfinite(self.c) or self.c <= 0:
            raise ValueError("c must be positive")
        if not np.isfinite(self.ell0) or self.ell0 < 0:
            raise ValueError("ell0 must be non-negative")
        if not np.isfinite(self.s_min) or self.s_min <= 0:
            raise ValueError("s_min must be positive")
        if not np.isfinite(self.epsilon) or self.epsilon <= 0:
            raise ValueError("epsilon must be positive")


@dataclass
class NullSpec:
    null_mode: Literal["random_phase"]
    seed: int

    def validate(self) -> None:
        if self.null_mode != "random_phase":
            raise ValueError("Only null_mode='random_phase' is supported.")


@dataclass
class WrongDispersionSpec:
    dispersion_mode: Literal["scaled_quadratic"]
    alpha: float

    def validate(self) -> None:
        if self.dispersion_mode != "scaled_quadratic":
            raise ValueError("Only dispersion_mode='scaled_quadratic' is supported.")
        if not np.isfinite(self.alpha) or self.alpha <= 0.0:
            raise ValueError("alpha must be positive and finite.")
        if abs(self.alpha - 1.0) < 1e-15:
            raise ValueError("alpha=1.0 is just K.0 and not a wrong-dispersion control.")


@dataclass
class KernelMapSpec:
    kernel_mode: Literal["abs", "positive", "negative"]

    def validate(self) -> None:
        if self.kernel_mode not in {"abs", "positive", "negative"}:
            raise ValueError("kernel_mode must be one of: 'abs', 'positive', 'negative'")


@dataclass
class K0N0Result:
    run_kind: Literal["k0", "n0", "n1a"]
    config: BaseConfig
    null_spec: NullSpec | None
    wrong_dispersion_spec: WrongDispersionSpec | None
    kernel_spec: KernelMapSpec | None

    phase_source_summary: dict[str, Any]
    kbar: np.ndarray
    G: np.ndarray
    theta_crit: list[float]

    adjacency: np.ndarray
    connected_components: list[list[int]]
    graph_distance: np.ndarray
    graph_diameter: float | None

    edge_length: np.ndarray
    d_rel: np.ndarray

    connected_pairs: list[tuple[int, int]]
    disconnected_pairs: list[tuple[int, int]]

    standard_pairs: dict[str, float | None]
    bridge_predictions: dict[str, float | None]


def parse_float_list(text: str) -> np.ndarray:
    return np.array([float(x.strip()) for x in text.split(",") if x.strip()], dtype=float)


def _public_phase_source_summary(phase_source: dict[str, Any]) -> dict[str, Any]:
    out = {}
    for k, v in phase_source.items():
        if k.startswith("_"):
            continue
        if isinstance(v, np.ndarray):
            out[k] = v.tolist()
        else:
            out[k] = v
    return out


def build_reference_phase_source(config: BaseConfig) -> dict[str, Any]:
    return {
        "phase_type": "debroglie_reference",
        "mode": config.mode,
        "p": config.p.copy(),
        "m": config.m,
        "t": config.t,
        "L": config.L,
        "hbar": config.hbar,
        "F": config.F,
    }


def build_null_phase_source(config: BaseConfig, null_spec: NullSpec) -> dict[str, Any]:
    null_spec.validate()
    rng = np.random.default_rng(null_spec.seed)
    n = len(config.p)
    n_grid = 256
    phases = rng.uniform(0.0, 2.0 * np.pi, size=(n, n_grid))
    kbar = np.cos(phases[:, None, :] - phases[None, :, :]).mean(axis=2)
    np.fill_diagonal(kbar, 1.0)
    return {
        "phase_type": "random_phase",
        "mode": config.mode,
        "seed": null_spec.seed,
        "n_grid": n_grid,
        "_kbar": kbar,
    }


def build_wrong_dispersion_phase_source(config: BaseConfig, wd_spec: WrongDispersionSpec) -> dict[str, Any]:
    wd_spec.validate()
    if config.mode != "free":
        raise ValueError("N.1a currently supports only mode='free'.")
    return {
        "phase_type": "wrong_dispersion",
        "mode": "free",
        "p": config.p.copy(),
        "m": config.m,
        "t": config.t,
        "L": config.L,
        "hbar": config.hbar,
        "dispersion_mode": wd_spec.dispersion_mode,
        "alpha": wd_spec.alpha,
    }


def compute_kbar_from_phase_source(config: BaseConfig, phase_source: dict[str, Any]) -> np.ndarray:
    p = np.asarray(config.p, dtype=float)

    if phase_source["phase_type"] == "debroglie_reference":
        dp = p[:, None] - p[None, :]
        if config.mode == "free":
            dp2 = p[:, None] ** 2 - p[None, :] ** 2
            phase = (dp2 * config.t) / (2.0 * config.m * config.hbar)
            kbar = sinc_unscaled(dp * config.L / config.hbar) * np.cos(phase)
            np.fill_diagonal(kbar, 1.0)
            return np.asarray(kbar, dtype=float)
        if config.mode == "force":
            dp2 = p[:, None] ** 2 - p[None, :] ** 2
            phase = (dp2 * config.t + (p[:, None] - p[None, :]) * config.F * config.t**2) / (2.0 * config.m * config.hbar)
            kbar = sinc_unscaled(dp * config.L / config.hbar) * np.cos(phase)
            np.fill_diagonal(kbar, 1.0)
            return np.asarray(kbar, dtype=float)

    if phase_source["phase_type"] == "random_phase":
        return np.asarray(phase_source["_kbar"], dtype=float)

    if phase_source["phase_type"] == "wrong_dispersion":
        if config.mode != "free":
            raise ValueError("wrong_dispersion currently supports only free mode.")
        alpha = float(phase_source["alpha"])
        dp = p[:, None] - p[None, :]
        dp2 = p[:, None] ** 2 - p[None, :] ** 2
        phase = alpha * (dp2 * config.t) / (2.0 * config.m * config.hbar)
        kbar = sinc_unscaled(dp * config.L / config.hbar) * np.cos(phase)
        np.fill_diagonal(kbar, 1.0)
        return np.asarray(kbar, dtype=float)

    raise ValueError("Unsupported phase source type.")


def apply_kernel_map(kbar: np.ndarray, kernel_spec: KernelMapSpec) -> np.ndarray:
    kernel_spec.validate()
    if kernel_spec.kernel_mode == "abs":
        G = np.abs(kbar)
    elif kernel_spec.kernel_mode == "positive":
        G = np.maximum(kbar, 0.0)
    elif kernel_spec.kernel_mode == "negative":
        G = np.maximum(-kbar, 0.0)
    else:
        raise ValueError(f"Unsupported kernel_mode: {kernel_spec.kernel_mode}")
    np.fill_diagonal(G, 1.0)
    return G


def compute_G(kbar: np.ndarray) -> np.ndarray:
    return apply_kernel_map(kbar, KernelMapSpec(kernel_mode="abs"))


def extract_theta_crit(G: np.ndarray) -> list[float]:
    vals = []
    n = G.shape[0]
    for i in range(n):
        for j in range(i + 1, n):
            vals.append(float(G[i, j]))
    return sorted(set(vals))


def build_adjacency(G: np.ndarray, theta: float) -> np.ndarray:
    A = (G >= theta).astype(int)
    np.fill_diagonal(A, 0)
    return A


def connected_components(A: np.ndarray) -> list[list[int]]:
    n = A.shape[0]
    seen = [False] * n
    comps = []
    for start in range(n):
        if seen[start]:
            continue
        stack = [start]
        seen[start] = True
        comp = []
        while stack:
            u = stack.pop()
            comp.append(u)
            for v in range(n):
                if A[u, v] and not seen[v]:
                    seen[v] = True
                    stack.append(v)
        comps.append(sorted(comp))
    return comps


def graph_distance(A: np.ndarray) -> np.ndarray:
    n = A.shape[0]
    D = np.full((n, n), np.inf, dtype=float)
    np.fill_diagonal(D, 0.0)
    for i in range(n):
        for j in range(n):
            if A[i, j]:
                D[i, j] = 1.0
    for k in range(n):
        for i in range(n):
            dik = D[i, k]
            if not np.isfinite(dik):
                continue
            for j in range(n):
                alt = dik + D[k, j]
                if alt < D[i, j]:
                    D[i, j] = alt
    return D


def build_edge_lengths(A: np.ndarray, G: np.ndarray, ell0: float, s_min: float, epsilon: float) -> np.ndarray:
    n = A.shape[0]
    out = np.full((n, n), np.inf, dtype=float)
    np.fill_diagonal(out, 0.0)
    offdiag = G.copy()
    np.fill_diagonal(offdiag, 0.0)
    gmax = float(np.max(offdiag))
    if gmax <= 0:
        raise ValueError("Maximum off-diagonal G is zero; cannot normalize edge lengths.")
    for i in range(n):
        for j in range(n):
            if A[i, j]:
                gij = G[i, j] / gmax
                out[i, j] = s_min + ell0 * (-math.log(max(float(gij), epsilon)))
    return out


def relational_distance(edge_length: np.ndarray) -> np.ndarray:
    D = edge_length.copy()
    n = D.shape[0]
    for k in range(n):
        for i in range(n):
            dik = D[i, k]
            if not np.isfinite(dik):
                continue
            for j in range(n):
                alt = dik + D[k, j]
                if alt < D[i, j]:
                    D[i, j] = alt
    return D


def compute_standard_pair_differences(d_rel: np.ndarray) -> dict[str, float | None]:
    def diff(a: tuple[int, int], b: tuple[int, int]) -> float | None:
        va = d_rel[a]
        vb = d_rel[b]
        if not np.isfinite(va) or not np.isfinite(vb):
            return None
        return float(va - vb)
    return {
        "d03_minus_d01": diff((0, 3), (0, 1)),
        "d03_minus_d12": diff((0, 3), (1, 2)),
        "d02_minus_d13": diff((0, 2), (1, 3)),
    }


def compute_bridge_predictions(standard_pairs: dict[str, float | None], m: float, hbar: float, c: float) -> dict[str, float | None]:
    factor = -(m * c) / hbar
    return {k: None if v is None else float(factor * v) for k, v in standard_pairs.items()}


def run_downstream_from_G(config: BaseConfig, run_kind: Literal["k0", "n0", "n1a"], phase_source_summary: dict[str, Any], kbar: np.ndarray, G: np.ndarray, null_spec: NullSpec | None, wrong_dispersion_spec: WrongDispersionSpec | None, kernel_spec: KernelMapSpec) -> K0N0Result:
    theta_crit = extract_theta_crit(G)
    adjacency = build_adjacency(G, config.theta)
    cc = connected_components(adjacency)
    graph_dist = graph_distance(adjacency)
    graph_diam = None
    finite_vals = graph_dist[np.isfinite(graph_dist)]
    finite_vals = finite_vals[finite_vals > 0]
    if finite_vals.size > 0:
        graph_diam = float(np.max(finite_vals))
    edge_length = build_edge_lengths(adjacency, G, config.ell0, config.s_min, config.epsilon)
    d_rel = relational_distance(edge_length)
    n = len(config.p)
    connected_pairs = []
    disconnected_pairs = []
    for i in range(n):
        for j in range(i + 1, n):
            if np.isfinite(d_rel[i, j]):
                connected_pairs.append((i, j))
            else:
                disconnected_pairs.append((i, j))
    standard_pairs = compute_standard_pair_differences(d_rel)
    bridge_predictions = compute_bridge_predictions(standard_pairs, config.m, config.hbar, config.c)
    return K0N0Result(
        run_kind=run_kind,
        config=config,
        null_spec=null_spec,
        wrong_dispersion_spec=wrong_dispersion_spec,
        kernel_spec=kernel_spec,
        phase_source_summary=phase_source_summary,
        kbar=kbar,
        G=G,
        theta_crit=theta_crit,
        adjacency=adjacency,
        connected_components=cc,
        graph_distance=graph_dist,
        graph_diameter=graph_diam,
        edge_length=edge_length,
        d_rel=d_rel,
        connected_pairs=connected_pairs,
        disconnected_pairs=disconnected_pairs,
        standard_pairs=standard_pairs,
        bridge_predictions=bridge_predictions,
    )


def _run_common(config: BaseConfig, run_kind: Literal["k0", "n0", "n1a"], phase_source: dict[str, Any], null_spec: NullSpec | None, wrong_dispersion_spec: WrongDispersionSpec | None, kernel_spec: KernelMapSpec | None = None) -> K0N0Result:
    if kernel_spec is None:
        kernel_spec = KernelMapSpec(kernel_mode="abs")
    kbar = compute_kbar_from_phase_source(config, phase_source)
    G = apply_kernel_map(kbar, kernel_spec)
    return run_downstream_from_G(config, run_kind, _public_phase_source_summary(phase_source), kbar, G, null_spec, wrong_dispersion_spec, kernel_spec)


def run_k0(config: BaseConfig) -> K0N0Result:
    config.validate()
    return _run_common(config, "k0", build_reference_phase_source(config), None, None, KernelMapSpec("abs"))


def run_n0(config: BaseConfig, null_spec: NullSpec) -> K0N0Result:
    config.validate()
    null_spec.validate()
    return _run_common(config, "n0", build_null_phase_source(config, null_spec), null_spec, None, KernelMapSpec("abs"))


def run_n1a(config: BaseConfig, wd_spec: WrongDispersionSpec) -> K0N0Result:
    config.validate()
    wd_spec.validate()
    return _run_common(config, "n1a", build_wrong_dispersion_phase_source(config, wd_spec), None, wd_spec, KernelMapSpec("abs"))


def run_n0_ensemble(config: BaseConfig, seeds: list[int], null_mode: str = "random_phase") -> list[K0N0Result]:
    return [run_n0(config, NullSpec(null_mode="random_phase", seed=int(seed))) for seed in seeds]


def run_with_kernel_map(result_base: K0N0Result, kernel_spec: KernelMapSpec) -> K0N0Result:
    kernel_spec.validate()
    G = apply_kernel_map(result_base.kbar, kernel_spec)
    return run_downstream_from_G(result_base.config, result_base.run_kind, result_base.phase_source_summary, result_base.kbar, G, result_base.null_spec, result_base.wrong_dispersion_spec, kernel_spec)


def _jsonable(v: Any) -> Any:
    if isinstance(v, np.ndarray):
        return v.tolist()
    if isinstance(v, (np.floating, np.integer)):
        return v.item()
    if isinstance(v, dict):
        return {k: _jsonable(x) for k, x in v.items()}
    if isinstance(v, (list, tuple)):
        return [_jsonable(x) for x in v]
    return v


def result_to_jsonable(result: K0N0Result) -> dict[str, Any]:
    return {
        "run_kind": result.run_kind,
        "config": {**{k: _jsonable(v) for k, v in asdict(result.config).items()}, "p": result.config.p.tolist()},
        "null_spec": None if result.null_spec is None else _jsonable(asdict(result.null_spec)),
        "wrong_dispersion_spec": None if result.wrong_dispersion_spec is None else _jsonable(asdict(result.wrong_dispersion_spec)),
        "kernel_spec": None if result.kernel_spec is None else _jsonable(asdict(result.kernel_spec)),
        "phase_source_summary": _jsonable(result.phase_source_summary),
        "theta_crit": [float(x) for x in result.theta_crit],
        "connected_components": _jsonable(result.connected_components),
        "graph_diameter": result.graph_diameter,
        "connected_pairs": _jsonable(result.connected_pairs),
        "disconnected_pairs": _jsonable(result.disconnected_pairs),
        "standard_pairs": _jsonable(result.standard_pairs),
        "bridge_predictions": _jsonable(result.bridge_predictions),
    }


def render_summary(result: K0N0Result) -> str:
    lines = [f"run_kind: {result.run_kind}", f"mode: {result.config.mode}", f"theta: {result.config.theta}", f"p: {result.config.p.tolist()}", f"m={result.config.m}, t={result.config.t}, L={result.config.L}, F={result.config.F}"]
    if result.null_spec is not None:
        lines.append(f"null_mode: {result.null_spec.null_mode}, seed: {result.null_spec.seed}")
    if result.wrong_dispersion_spec is not None:
        lines.append(f"wrong_dispersion: mode={result.wrong_dispersion_spec.dispersion_mode}, alpha={result.wrong_dispersion_spec.alpha}")
    if result.kernel_spec is not None:
        lines.append(f"kernel_mode: {result.kernel_spec.kernel_mode}")
    lines.extend([f"theta_crit: {result.theta_crit}", f"n_edges: {len(result.connected_pairs)}", f"connected_components: {result.connected_components}", f"graph_diameter: {result.graph_diameter}", f"connected_pairs: {result.connected_pairs}", f"disconnected_pairs: {result.disconnected_pairs}", "standard_pairs:"])
    for key in ["d03_minus_d01", "d03_minus_d12", "d02_minus_d13"]:
        lines.append(f"  {key}: {result.standard_pairs.get(key)}")
    lines.append("bridge_predictions:")
    for key in ["d03_minus_d01", "d03_minus_d12", "d02_minus_d13"]:
        lines.append(f"  {key}: {result.bridge_predictions.get(key)}")
    return "\\n".join(lines) + "\\n"


def write_result_artifacts(result: K0N0Result, outdir: str | Path) -> None:
    out = Path(outdir)
    out.mkdir(parents=True, exist_ok=True)
    with (out / "result.json").open("w", encoding="utf-8") as f:
        json.dump(result_to_jsonable(result), f, indent=2)
    np.savez(out / "matrices.npz", kbar=result.kbar, G=result.G, adjacency=result.adjacency, graph_distance=result.graph_distance, edge_length=result.edge_length, d_rel=result.d_rel)
    (out / "summary.txt").write_text(render_summary(result), encoding="utf-8")


def _add_common(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--mode", choices=["free", "force"], required=True)
    parser.add_argument("--p", required=True)
    parser.add_argument("--m", type=float, required=True)
    parser.add_argument("--t", type=float, required=True)
    parser.add_argument("--L", type=float, required=True)
    parser.add_argument("--theta", type=float, required=True)
    parser.add_argument("--F", type=float, default=0.0)
    parser.add_argument("--hbar", type=float, default=1.0)
    parser.add_argument("--c", type=float, default=1.0)
    parser.add_argument("--ell0", type=float, default=1.0)
    parser.add_argument("--s-min", dest="s_min", type=float, default=1.0)
    parser.add_argument("--epsilon", type=float, default=1e-12)
    parser.add_argument("--outdir", required=True)


def _build_config_from_args(args: argparse.Namespace) -> BaseConfig:
    return BaseConfig(mode=args.mode, p=parse_float_list(args.p), m=args.m, t=args.t, L=args.L, theta=args.theta, hbar=args.hbar, c=args.c, ell0=args.ell0, s_min=args.s_min, epsilon=args.epsilon, F=args.F, weight="uniform")


def main() -> None:
    parser = argparse.ArgumentParser(description="K0/N0/N1a reference implementation")
    sub = parser.add_subparsers(dest="cmd", required=True)
    p_k0 = sub.add_parser("run-k0", help="Run K.0 reference pipeline")
    _add_common(p_k0)
    p_n0 = sub.add_parser("run-n0", help="Run N.0 null-model pipeline")
    _add_common(p_n0)
    p_n0.add_argument("--seed", type=int, required=True)
    p_n1a = sub.add_parser("run-n1a", help="Run N.1a wrong-dispersion control")
    _add_common(p_n1a)
    p_n1a.add_argument("--dispersion-mode", choices=["scaled_quadratic"], required=True)
    p_n1a.add_argument("--alpha", type=float, required=True)
    p_n0e = sub.add_parser("run-n0-ensemble", help="Run N.0 null-model ensemble")
    _add_common(p_n0e)
    p_n0e.add_argument("--seeds", required=True)

    args = parser.parse_args()
    config = _build_config_from_args(args)

    if args.cmd == "run-k0":
        result = run_k0(config)
        write_result_artifacts(result, args.outdir)
        print(render_summary(result), end="")
        return
    if args.cmd == "run-n0":
        result = run_n0(config, NullSpec(null_mode="random_phase", seed=args.seed))
        write_result_artifacts(result, args.outdir)
        print(render_summary(result), end="")
        return
    if args.cmd == "run-n1a":
        result = run_n1a(config, WrongDispersionSpec(dispersion_mode=args.dispersion_mode, alpha=args.alpha))
        write_result_artifacts(result, args.outdir)
        print(render_summary(result), end="")
        return
    if args.cmd == "run-n0-ensemble":
        seeds = [int(x.strip()) for x in args.seeds.split(",") if x.strip()]
        results = run_n0_ensemble(config, seeds)
        out = Path(args.outdir)
        out.mkdir(parents=True, exist_ok=True)
        with (out / "ensemble_summary.json").open("w", encoding="utf-8") as f:
            json.dump({"n_runs": len(results), "seeds": seeds, "results": [result_to_jsonable(r) for r in results]}, f, indent=2)
        for seed, result in zip(seeds, results):
            write_result_artifacts(result, out / f"seed_{seed}")
        print(f"Wrote ensemble to: {out}")
        return


if __name__ == "__main__":
    main()
