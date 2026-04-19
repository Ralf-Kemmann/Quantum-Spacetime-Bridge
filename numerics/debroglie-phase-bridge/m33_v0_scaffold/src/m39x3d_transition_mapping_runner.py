#!/usr/bin/env python3
"""
m39x3d_transition_mapping_runner.py

M.3.9x.3d — Dichter FSW-/AO-Sweep und Grenzbestimmung

Ziel:
- dichte FSW- und AO-Sweeps auswerten
- quantitative Type-B-Fenster und qualitative AO-Sprungzonen kartieren
- lokale Transitionen und Kniekandidaten markieren
"""

from __future__ import annotations

import argparse
import json
import math
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
import pandas as pd
import yaml


# ---------------------------------------------------------------------
# Datenklassen
# ---------------------------------------------------------------------

@dataclass
class MarkerScore:
    family_id: str
    variant_id: str
    spectral_type: str
    model_class: str
    marker_name: str
    pairing_mode: str
    n_pairs: int
    absolute_strength: float
    strength_mean: float
    strength_ci_low: float
    strength_ci_high: float
    absolute_support_flag: int
    relative_rank: int
    dominance_margin: float
    bootstrap_win_fraction: float
    dominant_level_flag: int
    dominance_stable_flag: int
    extra: Dict[str, Any]


@dataclass
class FamilyPredictionResult:
    family_id: str
    family_label: str
    spectral_type: str
    model_class: str
    status: str
    enabled: bool
    variant_id: str

    dominant_marker: Optional[str]
    absolute_best_marker: Optional[str]
    relative_rank_top3: str
    dominance_margin: Optional[float]
    bootstrap_win_fraction: Optional[float]

    prediction_match_status: str
    prediction_match_note: str
    prediction_hard_pass_flag: int
    prediction_soft_pass_flag: int
    prediction_fail_flag: int

    expected_relative_winner: Optional[str]
    expected_allowed_winners: str
    expected_delta_p2_role: Optional[str]
    expected_irregularity_level: Optional[str]
    expected_direction_blindness_relevant: Optional[bool]

    observed_spacing_cv: Optional[float]
    observed_spacing_ratio_mean: Optional[float]
    observed_direction_blindness_flag: Optional[int]

    extra: Dict[str, Any]


# ---------------------------------------------------------------------
# IO helpers
# ---------------------------------------------------------------------

def load_yaml(path: str | Path) -> Dict[str, Any]:
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def ensure_dir(path: str | Path) -> Path:
    p = Path(path)
    p.mkdir(parents=True, exist_ok=True)
    return p


def write_json(obj: Dict[str, Any], path: str | Path) -> None:
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f, indent=2, ensure_ascii=False)


def write_markdown(text: str, path: str | Path) -> None:
    with open(path, "w", encoding="utf-8") as f:
        f.write(text)


# ---------------------------------------------------------------------
# Spectrum helpers
# ---------------------------------------------------------------------

def to_numpy(values: List[float]) -> np.ndarray:
    return np.asarray(values, dtype=float)


def build_pairs(values: np.ndarray, pairing_mode: str) -> List[Tuple[int, int]]:
    n = len(values)
    pairs: List[Tuple[int, int]] = []

    if n < 2:
        return pairs

    if pairing_mode == "all_pairs":
        for i in range(n):
            for j in range(i + 1, n):
                pairs.append((i, j))
        return pairs

    if pairing_mode == "nearest_pairs":
        order = np.argsort(values)
        for k in range(len(order) - 1):
            i, j = order[k], order[k + 1]
            pairs.append((min(i, j), max(i, j)))
        return sorted(set(pairs))

    if pairing_mode == "matched_pairs":
        order = np.argsort(values)
        half = len(order) // 2
        left = order[:half]
        right = order[-half:]
        for i, j in zip(left, right):
            pairs.append((min(i, j), max(i, j)))
        return sorted(set(pairs))

    if pairing_mode in {"degeneracy_safe_pairs", "unique_abs_pairs", "no_sign_mirror_pairs"}:
        for i in range(n):
            for j in range(i + 1, n):
                pairs.append((i, j))
        return pairs

    raise ValueError(f"Unsupported pairing mode: {pairing_mode}")


def apply_ring_pair_filters(
    base_values: np.ndarray,
    pairs: List[Tuple[int, int]],
    degeneracy_policy: Dict[str, Any],
    active_spectrum_name: str,
) -> List[Tuple[int, int]]:
    exclude_sign_mirror_pairs = degeneracy_policy.get("exclude_sign_mirror_pairs", False)
    treat_sign_as_distinct = degeneracy_policy.get("treat_sign_as_distinct", True)
    collapse_equal_energy_shells = degeneracy_policy.get("collapse_equal_energy_shells", False)

    filtered: List[Tuple[int, int]] = []
    seen_abs = set()
    seen_energy_shells = set()

    for i, j in pairs:
        vi, vj = base_values[i], base_values[j]

        if exclude_sign_mirror_pairs and np.isclose(vi, -vj):
            continue

        if not treat_sign_as_distinct and active_spectrum_name in {"abs_p", "p"}:
            key = tuple(sorted((abs(float(vi)), abs(float(vj)))))
            if key in seen_abs:
                continue
            seen_abs.add(key)

        if collapse_equal_energy_shells:
            ekey = tuple(sorted((float(vi**2), float(vj**2))))
            if ekey in seen_energy_shells:
                continue
            seen_energy_shells.add(ekey)

        filtered.append((i, j))

    return filtered


def derive_spectrum(values: np.ndarray, transform: str, parameters: Optional[Dict[str, Any]] = None) -> np.ndarray:
    parameters = parameters or {}

    if transform == "abs":
        return np.abs(values)
    if transform == "square":
        return values ** 2
    if transform == "square_over_2m":
        m = float(parameters.get("m", 1.0))
        return (values ** 2) / (2.0 * m)
    if transform == "linear_scale":
        factor = float(parameters.get("factor", 1.0))
        return factor * values

    raise ValueError(f"Unsupported transform: {transform}")


def build_rectangular_cavity_k_values(family: Dict[str, Any]) -> np.ndarray:
    geom = family["mode_table"]["geometry"]
    a = float(geom["a"])
    b = float(geom["b"])
    d = float(geom["d"])

    out = []
    for m, n, p in family["mode_table"]["mode_indices"]:
        k = math.sqrt(
            (m * math.pi / a) ** 2 +
            (n * math.pi / b) ** 2 +
            (p * math.pi / d) ** 2
        )
        out.append(k)
    return np.asarray(out, dtype=float)


def build_circular_membrane_k_values(family: Dict[str, Any]) -> np.ndarray:
    bessel_zero_lookup: Dict[Tuple[int, int], float] = {
        (0, 1): 2.4048255577,
        (0, 2): 5.5200781103,
        (0, 3): 8.6537279129,
        (1, 1): 3.8317059702,
        (1, 2): 7.0155866698,
        (2, 1): 5.1356223018,
        (2, 2): 8.4172441404,
        (3, 1): 6.3801618952,
    }

    out = []
    for m, n in family["mode_table"]["mode_indices"]:
        key = (int(m), int(n))
        if key not in bessel_zero_lookup:
            raise ValueError(f"Missing Bessel-zero lookup for membrane mode {key}")
        out.append(bessel_zero_lookup[key])
    return np.asarray(out, dtype=float)


def build_family_spectra(family: Dict[str, Any], variant: Optional[Dict[str, Any]] = None) -> Dict[str, np.ndarray]:
    out: Dict[str, np.ndarray] = {}

    if "sweep_regimes" in family:
        if variant is None or "base_spectrum" not in variant:
            raise ValueError(f"Sweep family {family['family_id']} requires variant/regime base_spectrum.")
        base = variant["base_spectrum"]
        values = base.get("values", base.get("proxy_bound_state_spectrum", base.get("proxy_spectrum")))
        out[base["variable_name"]] = to_numpy(values)

        if base["variable_name"] == "p":
            out["p2"] = derive_spectrum(out["p"], "square")
            mass = float(family.get("fixed_parameters", {}).get("mass", 1.0))
            out["E_quad"] = derive_spectrum(out["p"], "square_over_2m", {"m": mass})
    else:
        base = family["base_spectrum"]
        if "values" in base:
            out[base["variable_name"]] = to_numpy(base["values"])
        elif base.get("construction") == "from_existing_external_reference_family":
            mode_type = family.get("mode_table", {}).get("type")
            if mode_type == "rectangular_cavity_modes":
                out[base["variable_name"]] = build_rectangular_cavity_k_values(family)
            elif mode_type == "circular_membrane_bessel_modes":
                out[base["variable_name"]] = build_circular_membrane_k_values(family)
            else:
                raise NotImplementedError(f"Unsupported mode_table type: {mode_type}")
        else:
            raise NotImplementedError(f"Unsupported base spectrum construction for family {family['family_id']}.")

        for item in family.get("derived_spectra", []):
            src = item["from"]
            out[item["variable_name"]] = derive_spectrum(out[src], item["transform"], item.get("parameters", {}))

    return out


# ---------------------------------------------------------------------
# Marker computation
# ---------------------------------------------------------------------

def compute_marker_for_pair(marker_name: str, spec: Dict[str, np.ndarray], i: int, j: int) -> float:
    p = spec.get("p")
    p2 = spec.get("p2")
    e_quad = spec.get("E_quad")
    k = spec.get("k")
    k2 = spec.get("k2")
    omega = spec.get("omega")
    lambd = spec.get("lambda")

    if marker_name == "delta_p":
        return float(p[i] - p[j]) if p is not None else float(k[i] - k[j])
    if marker_name == "abs_delta_p":
        return abs(float(p[i] - p[j])) if p is not None else abs(float(k[i] - k[j]))
    if marker_name == "delta_p2":
        if p2 is not None:
            return float(p2[i] - p2[j])
        if k2 is not None:
            return float(k2[i] - k2[j])
        raise ValueError("delta_p2/delta_k2 requested but neither p2 nor k2 is available.")
    if marker_name == "abs_delta_p2":
        if p2 is not None:
            return abs(float(p2[i] - p2[j]))
        if k2 is not None:
            return abs(float(k2[i] - k2[j]))
        raise ValueError("abs_delta_p2/abs_delta_k2 requested but neither p2 nor k2 is available.")
    if marker_name == "delta_E_quad":
        if e_quad is None:
            raise ValueError("delta_E_quad requested but E_quad spectrum missing.")
        return float(e_quad[i] - e_quad[j])

    if marker_name == "delta_k":
        return float(k[i] - k[j])
    if marker_name == "abs_delta_k":
        return abs(float(k[i] - k[j]))
    if marker_name == "delta_k2":
        return float(k2[i] - k2[j])
    if marker_name == "abs_delta_k2":
        return abs(float(k2[i] - k2[j]))
    if marker_name == "delta_omega":
        return float(omega[i] - omega[j])
    if marker_name == "delta_lambda":
        return float(lambd[i] - lambd[j])

    raise ValueError(f"Unsupported marker: {marker_name}")


def compute_marker_vector(marker_name: str, spec: Dict[str, np.ndarray], pairs: List[Tuple[int, int]]) -> np.ndarray:
    return np.asarray([compute_marker_for_pair(marker_name, spec, i, j) for i, j in pairs], dtype=float)


# ---------------------------------------------------------------------
# Scoring
# ---------------------------------------------------------------------

def infer_pair_labels_from_existing_logic(
    family: Dict[str, Any],
    pairs: List[Tuple[int, int]],
    spec: Dict[str, np.ndarray],
) -> np.ndarray:
    base = spec["p"] if spec.get("p") is not None else spec["k"]
    diffs = np.asarray([abs(base[i] - base[j]) for i, j in pairs], dtype=float)
    if len(diffs) == 0:
        return np.asarray([], dtype=int)
    thr = float(np.median(diffs))
    return (diffs > thr).astype(int)


def rank_separation_score(marker_values: np.ndarray, labels: np.ndarray) -> float:
    if len(marker_values) == 0 or len(labels) == 0 or len(np.unique(labels)) < 2:
        return 0.0

    a = marker_values[labels == 0]
    b = marker_values[labels == 1]
    if len(a) == 0 or len(b) == 0:
        return 0.0

    denom = float(np.std(marker_values))
    if np.isclose(denom, 0.0):
        return 0.0

    score = abs(float(np.mean(a) - np.mean(b))) / denom
    return float(max(0.0, min(1.0, score / 3.0)))


def bootstrap_strength(
    marker_values: np.ndarray,
    labels: np.ndarray,
    n_bootstrap: int,
    rng: np.random.Generator,
) -> Tuple[float, float, float]:
    if len(marker_values) == 0:
        return 0.0, 0.0, 0.0

    idx = np.arange(len(marker_values))
    scores = []
    for _ in range(n_bootstrap):
        sample_idx = rng.choice(idx, size=len(idx), replace=True)
        scores.append(rank_separation_score(marker_values[sample_idx], labels[sample_idx]))

    arr = np.asarray(scores, dtype=float)
    return float(arr.mean()), float(np.quantile(arr, 0.025)), float(np.quantile(arr, 0.975))


def bootstrap_win_fractions(
    marker_vectors: Dict[str, np.ndarray],
    labels: np.ndarray,
    n_bootstrap: int,
    rng: np.random.Generator,
) -> Dict[str, float]:
    if not marker_vectors or len(labels) == 0:
        return {}

    wins = {name: 0 for name in marker_vectors}
    idx = np.arange(len(labels))

    for _ in range(n_bootstrap):
        sample_idx = rng.choice(idx, size=len(idx), replace=True)
        scores = {
            name: rank_separation_score(vec[sample_idx], labels[sample_idx])
            for name, vec in marker_vectors.items()
        }
        best = max(scores.items(), key=lambda x: x[1])[0]
        wins[best] += 1

    return {name: wins[name] / n_bootstrap for name in wins}


# ---------------------------------------------------------------------
# Irregularity
# ---------------------------------------------------------------------

def simple_unfold(sorted_vals: np.ndarray) -> np.ndarray:
    n = len(sorted_vals)
    if n < 2:
        return sorted_vals.copy()
    return np.arange(1, n + 1, dtype=float) / float(n)


def compute_irregularity_measures(values: np.ndarray) -> Dict[str, float]:
    s = np.sort(np.asarray(values, dtype=float))
    if len(s) < 3:
        return {
            "spacing_mean": 0.0,
            "spacing_std": 0.0,
            "spacing_cv": 0.0,
            "spacing_ratio_mean": 0.0,
            "simple_unfolding_density": 0.0,
            "simple_rigidity_surrogate": 0.0,
            "grid_deviation_score": 0.0,
            "second_difference_curvature": 0.0,
        }

    spacings = np.diff(s)
    spacing_mean = float(np.mean(spacings))
    spacing_std = float(np.std(spacings))
    spacing_cv = float(spacing_std / spacing_mean) if not np.isclose(spacing_mean, 0.0) else 0.0

    ratios = []
    for i in range(len(spacings) - 1):
        a, b = spacings[i], spacings[i + 1]
        if a > 0 and b > 0:
            ratios.append(min(a, b) / max(a, b))
    spacing_ratio_mean = float(np.mean(ratios)) if ratios else 0.0

    unfolded = simple_unfold(s)
    density = float(len(unfolded) / max(unfolded[-1] - unfolded[0], 1e-12))
    rigidity = float(np.var(spacings))

    grid = np.linspace(float(s[0]), float(s[-1]), num=len(s))
    grid_dev = float(np.mean(np.abs(s - grid)))

    second_diff = np.diff(s, n=2) if len(s) >= 4 else np.asarray([], dtype=float)
    second_difference_curvature = float(np.mean(np.abs(second_diff))) if len(second_diff) else 0.0

    return {
        "spacing_mean": spacing_mean,
        "spacing_std": spacing_std,
        "spacing_cv": spacing_cv,
        "spacing_ratio_mean": spacing_ratio_mean,
        "simple_unfolding_density": density,
        "simple_rigidity_surrogate": rigidity,
        "grid_deviation_score": grid_dev,
        "second_difference_curvature": second_difference_curvature,
    }


def irregularity_level_from_cv(cv: float, cfg: Dict[str, Any]) -> str:
    levels = cfg["irregularity_levels"]

    if cv <= levels["low"]["spacing_cv_max"]:
        return "low"
    if cv <= levels["low_to_moderate"]["spacing_cv_max"]:
        return "low_to_moderate"

    moderate_cfg = levels["moderate"]
    if moderate_cfg["spacing_cv_min"] <= cv <= moderate_cfg["spacing_cv_max"]:
        return "moderate"

    if cv >= levels["high"]["spacing_cv_min"]:
        return "high"

    return "moderate_to_high"


# ---------------------------------------------------------------------
# Prediction matching
# ---------------------------------------------------------------------

def evaluate_prediction_match_simple(
    dominant_marker: str,
    spectral_type: str,
    irregularity_level: str,
) -> Tuple[str, str]:
    if spectral_type == "type_A_ladder":
        if dominant_marker == "delta_p":
            return "supported", "Type A marker structure matched."
        return "partially_supported", "Type A partially matched."

    if spectral_type == "type_D_regular_nonring":
        if dominant_marker in {"delta_p", "abs_delta_p"} and irregularity_level in {"low", "low_to_moderate"}:
            return "supported", "Type D regular non-ring structure matched."
        return "partially_supported", "Type D partially matched."

    if spectral_type == "type_C_multiindex_structure":
        if dominant_marker in {"delta_k2", "abs_delta_k2", "delta_lambda", "delta_k"}:
            return "supported", "Type C structure marker matched."
        return "partially_supported", "Type C partially matched."

    if spectral_type == "type_B_quadratic_nontrivial":
        if dominant_marker in {"delta_p", "abs_delta_p", "delta_p2", "abs_delta_p2"}:
            return "partially_supported", "Type B baseline marker compatibility."
        return "open", "Type B remains open."

    return "open", "No specific prediction rule."


# ---------------------------------------------------------------------
# Diagnostics per family/variant
# ---------------------------------------------------------------------

def run_family_variant_diagnostics(
    family: Dict[str, Any],
    variant: Dict[str, Any],
    config: Dict[str, Any],
    rng: np.random.Generator,
) -> Tuple[pd.DataFrame, Dict[str, Any], Dict[str, Any], int]:
    spec_all = build_family_spectra(family, variant)
    pairing_mode = variant["pairing_mode"]
    active_spectrum = variant["active_spectrum"]
    active_markers = variant["active_markers"]
    degeneracy_policy = variant.get("degeneracy_policy", {})

    pairs = build_pairs(spec_all[active_spectrum], pairing_mode)

    if family["family_id"] == "ER1_RING":
        pairs = apply_ring_pair_filters(spec_all["p"], pairs, degeneracy_policy, active_spectrum)

    labels = infer_pair_labels_from_existing_logic(family, pairs, spec_all)
    n_boot = int(config["bootstrap"]["n_bootstrap"])

    marker_vectors = {
        marker: compute_marker_vector(marker, spec_all, pairs)
        for marker in active_markers
    }
    win_fractions = bootstrap_win_fractions(marker_vectors, labels, n_boot, rng)

    rows = []
    for marker_name, vec in marker_vectors.items():
        abs_strength = rank_separation_score(vec, labels)
        mean_s, low_s, high_s = bootstrap_strength(vec, labels, n_boot, rng)
        rows.append({
            "marker_name": marker_name,
            "absolute_strength": abs_strength,
            "strength_mean": mean_s,
            "strength_ci_low": low_s,
            "strength_ci_high": high_s,
            "bootstrap_win_fraction": win_fractions.get(marker_name, 0.0),
        })

    df = pd.DataFrame(rows).sort_values(
        by=["absolute_strength", "bootstrap_win_fraction"],
        ascending=[False, False],
    ).reset_index(drop=True)

    if len(df) == 0:
        return df, {}, {}, 0

    df["relative_rank"] = np.arange(1, len(df) + 1)
    best_abs = float(df.iloc[0]["absolute_strength"])
    second_abs = float(df.iloc[1]["absolute_strength"]) if len(df) > 1 else best_abs

    dominance_margin_map = {}
    for idx, row in df.iterrows():
        marker_name = row["marker_name"]
        if idx == 0:
            dominance_margin_map[marker_name] = float(row["absolute_strength"]) - second_abs
        else:
            dominance_margin_map[marker_name] = float(row["absolute_strength"]) - best_abs
    df["dominance_margin"] = df["marker_name"].map(dominance_margin_map)

    irregularity = compute_irregularity_measures(spec_all[active_spectrum])

    observed = {
        "dominant_marker": str(df.iloc[0]["marker_name"]),
        "absolute_best_marker": str(df.iloc[0]["marker_name"]),
        "relative_rank_top3": ",".join(df["marker_name"].head(3).tolist()),
        "dominance_margin": float(df.iloc[0]["dominance_margin"]),
        "bootstrap_win_fraction": float(df.iloc[0]["bootstrap_win_fraction"]),
        "direction_blindness_flag": 0,
        "marker_df": df.copy(),
    }

    return df, observed, irregularity, len(spec_all[active_spectrum])


# ---------------------------------------------------------------------
# Transition helpers
# ---------------------------------------------------------------------

def linear_excess(prev_val: float, curr_val: float, next_val: float) -> float:
    expected = curr_val + (curr_val - prev_val)
    if np.isclose(expected, 0.0):
        return 0.0
    return float((next_val - expected) / abs(expected))


def get_row(df: pd.DataFrame, family_id: str, variant_id: str) -> Optional[pd.Series]:
    sub = df[(df["family_id"] == family_id) & (df["variant_id"] == variant_id)]
    return sub.iloc[0] if len(sub) else None


def marker_df_best_row(row: pd.Series, names: List[str]) -> Optional[pd.Series]:
    marker_df = row["extra"].get("marker_df")
    if marker_df is None:
        return None
    sub = marker_df[marker_df["marker_name"].isin(names)]
    if len(sub) == 0:
        return None
    return sub.sort_values(["relative_rank", "bootstrap_win_fraction"]).iloc[0]


def delta_p2_gain_vs_type_a(row: pd.Series, type_a_ref: Optional[pd.Series]) -> float:
    if type_a_ref is None:
        return 0.0
    r = marker_df_best_row(row, ["delta_p2", "abs_delta_p2"])
    a = marker_df_best_row(type_a_ref, ["delta_p2", "abs_delta_p2"])
    if r is None or a is None:
        return 0.0
    return float(r["bootstrap_win_fraction"]) - float(a["bootstrap_win_fraction"])


def distance_between_rows(row_a: pd.Series, row_b: Optional[pd.Series], config: Dict[str, Any]) -> float:
    if row_b is None:
        return 0.0

    score = 0.0
    if row_a["dominant_marker"] != row_b["dominant_marker"]:
        score += 0.10

    irr_a = irregularity_level_from_cv(float(row_a["observed_spacing_cv"]), config)
    irr_b = irregularity_level_from_cv(float(row_b["observed_spacing_cv"]), config)
    if irr_a != irr_b:
        score += 0.10

    grid_a = float(row_a["extra"].get("grid_deviation_score", 0.0))
    grid_b = float(row_b["extra"].get("grid_deviation_score", 0.0))
    if grid_a > grid_b:
        score += min(0.10, grid_a - grid_b)

    rig_a = float(row_a["extra"].get("simple_rigidity_surrogate", 0.0))
    rig_b = float(row_b["extra"].get("simple_rigidity_surrogate", 0.0))
    if rig_a > rig_b:
        score += min(0.10, rig_a - rig_b)

    return float(score)


def local_transition_flag(prev_row: Optional[pd.Series], curr_row: pd.Series, next_row: Optional[pd.Series]) -> bool:
    if prev_row is None or next_row is None:
        return False

    cv_prev = float(prev_row["extra"].get("spacing_cv", prev_row["observed_spacing_cv"]))
    cv_curr = float(curr_row["extra"].get("spacing_cv", curr_row["observed_spacing_cv"]))
    cv_next = float(next_row["extra"].get("spacing_cv", next_row["observed_spacing_cv"]))

    rig_prev = float(prev_row["extra"].get("simple_rigidity_surrogate", 0.0))
    rig_curr = float(curr_row["extra"].get("simple_rigidity_surrogate", 0.0))
    rig_next = float(next_row["extra"].get("simple_rigidity_surrogate", 0.0))

    return bool(
        abs((cv_next - cv_curr) - (cv_curr - cv_prev)) > 0.05
        or abs((rig_next - rig_curr) - (rig_curr - rig_prev)) > 0.05
    )


def knee_candidate_flag(prev_row: Optional[pd.Series], curr_row: pd.Series, next_row: Optional[pd.Series]) -> bool:
    if prev_row is None or next_row is None:
        return False

    grid_prev = float(prev_row["extra"].get("grid_deviation_score", 0.0))
    grid_curr = float(curr_row["extra"].get("grid_deviation_score", 0.0))
    grid_next = float(next_row["extra"].get("grid_deviation_score", 0.0))

    rig_prev = float(prev_row["extra"].get("simple_rigidity_surrogate", 0.0))
    rig_curr = float(curr_row["extra"].get("simple_rigidity_surrogate", 0.0))
    rig_next = float(next_row["extra"].get("simple_rigidity_surrogate", 0.0))

    return bool(
        abs((grid_next - grid_curr) - (grid_curr - grid_prev)) > 0.10
        or abs((rig_next - rig_curr) - (rig_curr - rig_prev)) > 0.10
    )


def classify_fsw_point(
    gain: float,
    dist_d: float,
    jump_flag: bool,
    irr_level: str,
    stable_neighbors: bool,
) -> Tuple[str, bool, float]:
    if dist_d <= 0.05 and irr_level in {"low", "low_to_moderate"}:
        return "type_D_near", False, 0.0

    if gain > 0 and dist_d > 0 and not jump_flag and stable_neighbors:
        return "quantitative_type_B_window", True, gain + dist_d

    if gain > 0 and dist_d > 0:
        return "quantitative_type_B_window_narrow", True, gain + 0.5 * dist_d

    return "edge_case", False, max(0.0, gain + dist_d)


def classify_ao_point(
    gain: float,
    dist_d: float,
    qual_jump_flag: bool,
    local_flag: bool,
    knee_flag: bool,
) -> str:
    if qual_jump_flag and local_flag:
        return "qualitative_type_B_jump"
    if knee_flag or qual_jump_flag:
        return "jump_transition_candidate"
    if gain > 0 and dist_d > 0:
        return "quantitative_type_B_transfer_zone"
    return "post_jump_or_edge_case"


# ---------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", default="configs/config_m39x3d_transition_mapping.yaml")
    args = parser.parse_args()

    config = load_yaml(args.config)
    families_cfg = load_yaml(config["inputs"]["family_definitions_yaml"])
    families = families_cfg.get("families", [])

    outdir = ensure_dir(config["run"]["outdir"])
    rng = np.random.default_rng(int(config["run"].get("random_seed", 1729)))

    marker_rows: List[MarkerScore] = []
    family_prediction_rows: List[FamilyPredictionResult] = []
    irregularity_rows: List[Dict[str, Any]] = []
    missing_case_rows: List[Dict[str, Any]] = []
    implemented_result_rows: List[Dict[str, Any]] = []
    transition_rows: List[Dict[str, Any]] = []
    control_rows: List[Dict[str, Any]] = []

    analysis_items: List[Tuple[Dict[str, Any], Dict[str, Any]]] = []

    for family in families:
        status = family.get("status", "implemented")
        enabled = bool(family.get("enabled", False))

        if status == "placeholder" or not enabled:
            missing_case_rows.append({
                "family_id": family["family_id"],
                "family_label": family["family_label"],
                "spectral_type": family["spectral_type"],
                "status": status,
                "implementation_note": family.get("implementation_note", ""),
            })
            continue

        if "analysis_variants" in family:
            for variant in family["analysis_variants"]:
                if variant.get("enabled", True):
                    analysis_items.append((family, variant))

        if "sweep_regimes" in family:
            for regime in family["sweep_regimes"]:
                base = regime["base_spectrum"]
                values = base.get("values", regime.get("proxy_bound_state_spectrum", regime.get("proxy_spectrum")))
                variant = {
                    "variant_id": regime["regime_id"],
                    "enabled": True,
                    "pairing_mode": "all_pairs",
                    "degeneracy_policy": {
                        "treat_sign_as_distinct": False,
                        "collapse_equal_energy_shells": False,
                        "exclude_sign_mirror_pairs": True,
                    },
                    "active_spectrum": base["variable_name"],
                    "active_markers": ["delta_p", "abs_delta_p", "delta_p2", "abs_delta_p2", "delta_E_quad"],
                    "base_spectrum": {
                        "variable_name": base["variable_name"],
                        "values": values,
                    },
                    "regime_id": regime["regime_id"],
                    "regime_label": regime.get("regime_label", regime["regime_id"]),
                    "well_depth": regime.get("well_depth"),
                    "anharmonic_strength": regime.get("anharmonic_strength"),
                    "expectation": regime.get("expectation"),
                }
                analysis_items.append((family, variant))

    for family, variant in analysis_items:
        family_id = family["family_id"]
        variant_id = variant["variant_id"]
        spectral_type = family["spectral_type"]
        model_class = family["model_class"]

        marker_df, observed, irregularity, n_states = run_family_variant_diagnostics(
            family, variant, config, rng
        )

        n_pairs = int(len(build_pairs(build_family_spectra(family, variant)[variant["active_spectrum"]], variant["pairing_mode"])))

        for _, row in marker_df.iterrows():
            marker_rows.append(
                MarkerScore(
                    family_id=family_id,
                    variant_id=variant_id,
                    spectral_type=spectral_type,
                    model_class=model_class,
                    marker_name=str(row["marker_name"]),
                    pairing_mode=variant["pairing_mode"],
                    n_pairs=n_pairs,
                    absolute_strength=float(row["absolute_strength"]),
                    strength_mean=float(row["strength_mean"]),
                    strength_ci_low=float(row["strength_ci_low"]),
                    strength_ci_high=float(row["strength_ci_high"]),
                    absolute_support_flag=int(
                        row["absolute_strength"] >= config["strength_scoring"]["support_thresholds"]["absolute_support_min"]
                    ),
                    relative_rank=int(row["relative_rank"]),
                    dominance_margin=float(row["dominance_margin"]),
                    bootstrap_win_fraction=float(row["bootstrap_win_fraction"]),
                    dominant_level_flag=int(row["relative_rank"] == 1),
                    dominance_stable_flag=int(
                        row["bootstrap_win_fraction"] >= config["strength_scoring"]["support_thresholds"]["dominance_stable_min"]
                    ),
                    extra={},
                )
            )

        irr_level = irregularity_level_from_cv(float(irregularity["spacing_cv"]), config)
        pred_status, pred_note = evaluate_prediction_match_simple(
            observed["dominant_marker"], spectral_type, irr_level
        )

        result = FamilyPredictionResult(
            family_id=family_id,
            family_label=family["family_label"],
            spectral_type=spectral_type,
            model_class=model_class,
            status=family.get("status", "implemented"),
            enabled=bool(family.get("enabled", False)),
            variant_id=variant_id,
            dominant_marker=observed["dominant_marker"],
            absolute_best_marker=observed["absolute_best_marker"],
            relative_rank_top3=observed["relative_rank_top3"],
            dominance_margin=observed["dominance_margin"],
            bootstrap_win_fraction=observed["bootstrap_win_fraction"],
            prediction_match_status=pred_status,
            prediction_match_note=pred_note,
            prediction_hard_pass_flag=int(pred_status == "supported"),
            prediction_soft_pass_flag=int(pred_status == "partially_supported"),
            prediction_fail_flag=int(pred_status == "failed"),
            expected_relative_winner=None,
            expected_allowed_winners="",
            expected_delta_p2_role=None,
            expected_irregularity_level=None,
            expected_direction_blindness_relevant=None,
            observed_spacing_cv=irregularity["spacing_cv"],
            observed_spacing_ratio_mean=irregularity["spacing_ratio_mean"],
            observed_direction_blindness_flag=0,
            extra={
                "marker_df": observed["marker_df"],
                "n_states": n_states,
                "regime_id": variant.get("regime_id"),
                "regime_label": variant.get("regime_label"),
                "well_depth": variant.get("well_depth"),
                "anharmonic_strength": variant.get("anharmonic_strength"),
                "expectation": variant.get("expectation"),
                **irregularity,
            },
        )

        family_prediction_rows.append(result)
        irregularity_rows.append({
            "family_id": family_id,
            "variant_id": variant_id,
            "spectral_type": spectral_type,
            **irregularity,
        })
        implemented_result_rows.append(asdict(result))

    marker_df = pd.DataFrame([asdict(x) for x in marker_rows])
    family_prediction_df = pd.DataFrame([asdict(x) for x in family_prediction_rows])
    irregularity_df = pd.DataFrame(irregularity_rows)
    missing_cases_df = pd.DataFrame(missing_case_rows)
    implemented_df = pd.DataFrame(implemented_result_rows)

    # References
    ref_cfg = config["mapping_references"]
    type_a_ref = get_row(implemented_df, ref_cfg["type_A_reference"]["family_id"], ref_cfg["type_A_reference"]["variant_id"])
    type_d_ref = get_row(implemented_df, ref_cfg["type_D_reference"]["family_id"], ref_cfg["type_D_reference"]["variant_id"])
    fsw_ref = get_row(implemented_df, ref_cfg["fsw_reference"]["family_id"], ref_cfg["fsw_reference"]["regime_id"])
    ao_ref = get_row(implemented_df, ref_cfg["ao_reference"]["family_id"], ref_cfg["ao_reference"]["regime_id"])
    ao_jump_ref = get_row(implemented_df, ref_cfg["ao_jump_reference"]["family_id"], ref_cfg["ao_jump_reference"]["regime_id"])

    # Type D control entry
    if type_d_ref is not None:
        control_rows.append({
            "family_id": type_d_ref["family_id"],
            "variant_id": type_d_ref["variant_id"],
            "spectral_type": type_d_ref["spectral_type"],
            "control_status": "supported",
            "control_note": "Type D baseline reference retained.",
        })

    # Process dense sweeps
    fsw_family_id = config["transition_mapping"]["sweeps"][0]["family_id"]
    ao_family_id = config["transition_mapping"]["sweeps"][1]["family_id"]

    for family_id in [fsw_family_id, ao_family_id]:
        sub = implemented_df[implemented_df["family_id"] == family_id].copy()
        if len(sub) == 0:
            continue

        if family_id == fsw_family_id:
            sort_col = "well_depth"
            sub["regime_parameter"] = sub["extra"].apply(lambda x: float(x.get("well_depth", 0.0)))
            sub = sub.sort_values("regime_parameter", ascending=False).reset_index(drop=True)
        else:
            sort_col = "anharmonic_strength"
            sub["regime_parameter"] = sub["extra"].apply(lambda x: float(x.get("anharmonic_strength", 0.0)))
            sub = sub.sort_values("regime_parameter", ascending=True).reset_index(drop=True)

        for idx in range(len(sub)):
            row = sub.iloc[idx]
            prev_row = sub.iloc[idx - 1] if idx > 0 else None
            next_row = sub.iloc[idx + 1] if idx < len(sub) - 1 else None

            gain = delta_p2_gain_vs_type_a(row, type_a_ref)
            dist_d = distance_between_rows(row, type_d_ref, config)
            irr_level = irregularity_level_from_cv(float(row["observed_spacing_cv"]), config)

            spacing_cv = float(row["extra"].get("spacing_cv", row["observed_spacing_cv"]))
            grid_dev = float(row["extra"].get("grid_deviation_score", 0.0))
            rigidity = float(row["extra"].get("simple_rigidity_surrogate", 0.0))
            curvature = float(row["extra"].get("second_difference_curvature", 0.0))

            nl_spacing = 0.0
            nl_grid = 0.0
            nl_rig = 0.0
            if prev_row is not None and next_row is not None:
                nl_spacing = linear_excess(
                    float(prev_row["extra"].get("spacing_cv", prev_row["observed_spacing_cv"])),
                    spacing_cv,
                    float(next_row["extra"].get("spacing_cv", next_row["observed_spacing_cv"])),
                )
                nl_grid = linear_excess(
                    float(prev_row["extra"].get("grid_deviation_score", 0.0)),
                    grid_dev,
                    float(next_row["extra"].get("grid_deviation_score", 0.0)),
                )
                nl_rig = linear_excess(
                    float(prev_row["extra"].get("simple_rigidity_surrogate", 0.0)),
                    rigidity,
                    float(next_row["extra"].get("simple_rigidity_surrogate", 0.0)),
                )

            local_flag = local_transition_flag(prev_row, row, next_row)
            knee_flag = knee_candidate_flag(prev_row, row, next_row)

            qualitative_jump_flag = bool(
                family_id == ao_family_id
                and row["variant_id"] == ao_jump_ref["variant_id"] if ao_jump_ref is not None else False
            )

            if family_id == ao_family_id:
                fsw_dist = distance_between_rows(row, fsw_ref, config)
                qual_jump_candidate = bool(
                    (rigidity > 0.20)
                    and (grid_dev > 0.30)
                    and (fsw_dist > 0.10)
                    and (
                        rigidity > 2.0 * float(fsw_ref["extra"].get("simple_rigidity_surrogate", 0.0))
                        if fsw_ref is not None else False
                    )
                )
                qualitative_jump_flag = qualitative_jump_flag or qual_jump_candidate
                regime_assignment = classify_ao_point(gain, dist_d, qualitative_jump_flag, local_flag, knee_flag)
                window_or_jump_membership = regime_assignment
                nonlinearity_excess = max(nl_spacing, nl_grid, nl_rig)
                jump_flag = regime_assignment == "qualitative_type_B_jump"
            else:
                stable_neighbors = bool(
                    prev_row is not None and next_row is not None and gain > 0 and dist_d > 0
                )
                regime_assignment, fsw_window_flag, fsw_window_strength = classify_fsw_point(
                    gain, dist_d, False, irr_level, stable_neighbors
                )
                window_or_jump_membership = regime_assignment
                nonlinearity_excess = max(nl_spacing, nl_grid, nl_rig)
                jump_flag = False

            transition_rows.append({
                "family_id": row["family_id"],
                "variant_id": row["variant_id"],
                "spectral_type": row["spectral_type"],
                "regime_parameter": row["regime_parameter"],
                "dominant_marker": row["dominant_marker"],
                "delta_p2_relative_gain_vs_type_A": gain,
                "distance_to_type_D": dist_d,
                "observed_irregularity_level": irr_level,
                "spacing_cv": spacing_cv,
                "grid_deviation_score": grid_dev,
                "simple_rigidity_surrogate": rigidity,
                "second_difference_curvature": curvature,
                "prediction_match_status": row["prediction_match_status"],
                "window_or_jump_membership": window_or_jump_membership,
                "nonlinearity_excess": nonlinearity_excess,
                "nonlinearity_excess_spacing_cv": nl_spacing,
                "nonlinearity_excess_grid_dev": nl_grid,
                "nonlinearity_excess_rigidity": nl_rig,
                "local_transition_flag": local_flag,
                "knee_candidate_flag": knee_flag,
                "quantitative_type_B_window_flag": regime_assignment in {"quantitative_type_B_window", "quantitative_type_B_window_narrow", "quantitative_type_B_transfer_zone"},
                "qualitative_type_B_jump_flag": jump_flag,
                "edge_case_flag": regime_assignment in {"edge_case", "post_jump_or_edge_case"},
                "regime_assignment": regime_assignment,
            })

    transition_df = pd.DataFrame(transition_rows)

    # Update family predictions with transition reading for dense families
    if len(transition_df):
        for _, tr in transition_df.iterrows():
            note = f"Mapped regime assignment: {tr['regime_assignment']}"
            status = tr["prediction_match_status"]
            if tr["regime_assignment"] in {"quantitative_type_B_window", "qualitative_type_B_jump"}:
                status = "supported"
            elif tr["regime_assignment"] in {"quantitative_type_B_window_narrow", "quantitative_type_B_transfer_zone", "jump_transition_candidate"}:
                status = "partially_supported"

            family_prediction_df.loc[
                (family_prediction_df["family_id"] == tr["family_id"]) &
                (family_prediction_df["variant_id"] == tr["variant_id"]),
                ["prediction_match_status", "prediction_match_note"]
            ] = [status, note]

    # Spectral summary
    def summarize_by_spectral_type(df: pd.DataFrame) -> pd.DataFrame:
        if len(df) == 0:
            return pd.DataFrame(columns=[
                "spectral_type", "n_families", "n_supported", "n_partially_supported", "n_open", "n_stressed", "n_failed"
            ])

        rows = []
        for spectral_type, sub in df.groupby("spectral_type"):
            rows.append({
                "spectral_type": spectral_type,
                "n_families": len(sub),
                "n_supported": int((sub["prediction_match_status"] == "supported").sum()),
                "n_partially_supported": int((sub["prediction_match_status"] == "partially_supported").sum()),
                "n_open": int((sub["prediction_match_status"] == "open").sum()),
                "n_stressed": int((sub["prediction_match_status"] == "stressed").sum()),
                "n_failed": int((sub["prediction_match_status"] == "failed").sum()),
            })
        return pd.DataFrame(rows)

    spectral_type_df = summarize_by_spectral_type(family_prediction_df)

    # Global mapping logic
    fsw_trans = transition_df[transition_df["family_id"] == fsw_family_id]
    ao_trans = transition_df[transition_df["family_id"] == ao_family_id]

    multiple_fsw_window = int((fsw_trans["regime_assignment"] == "quantitative_type_B_window").sum()) >= 2
    any_fsw_window = int((fsw_trans["regime_assignment"].isin(["quantitative_type_B_window", "quantitative_type_B_window_narrow"])).sum()) >= 1
    ao_jump = int((ao_trans["regime_assignment"] == "qualitative_type_B_jump").sum()) >= 1
    ao_prejump = int((ao_trans["regime_assignment"] == "jump_transition_candidate").sum()) >= 1
    any_knee = bool(ao_trans["knee_candidate_flag"].any()) if len(ao_trans) else False
    any_local = bool(ao_trans["local_transition_flag"].any()) if len(ao_trans) else False

    if multiple_fsw_window and ao_jump:
        global_status = "internal_type_B_regimes_supported"
    elif ao_jump and ao_prejump:
        global_status = "ao_qualitative_jump_transition_mapped"
    elif multiple_fsw_window:
        global_status = "type_B_quantitative_window_mapped"
    elif any_fsw_window:
        global_status = "type_B_quantitative_window_narrow"
    elif any_knee or any_local:
        global_status = "transition_has_knee_or_break"
    else:
        global_status = "internal_type_B_regimes_not_yet_stable"

    global_summary = {
        "run_id": config["run"]["run_id"],
        "n_families_total": len(families),
        "n_families_implemented": int(sum(1 for f in families if f.get("status", "implemented") == "implemented" and f.get("enabled", False))),
        "n_prediction_supported": int((family_prediction_df["prediction_match_status"] == "supported").sum()) if len(family_prediction_df) else 0,
        "n_prediction_partially_supported": int((family_prediction_df["prediction_match_status"] == "partially_supported").sum()) if len(family_prediction_df) else 0,
        "n_prediction_open": int((family_prediction_df["prediction_match_status"] == "open").sum()) if len(family_prediction_df) else 0,
        "n_prediction_stressed": int((family_prediction_df["prediction_match_status"] == "stressed").sum()) if len(family_prediction_df) else 0,
        "n_prediction_failed": int((family_prediction_df["prediction_match_status"] == "failed").sum()) if len(family_prediction_df) else 0,
        "global_prediction_status": global_status,
        "multiple_fsw_window": multiple_fsw_window,
        "ao_jump_mapped": ao_jump,
        "ao_prejump_present": ao_prejump,
        "knee_or_break_detected": any_knee or any_local,
    }

    # Outputs
    marker_df.to_csv(outdir / config["outputs"]["marker_summary_csv"], index=False)
    family_prediction_df.to_csv(outdir / config["outputs"]["family_prediction_summary_csv"], index=False)
    irregularity_df.to_csv(outdir / config["outputs"]["irregularity_summary_csv"], index=False)
    spectral_type_df.to_csv(outdir / config["outputs"]["spectral_type_summary_csv"], index=False)
    missing_cases_df.to_csv(outdir / config["outputs"]["missing_cases_summary_csv"], index=False)

    control_out = config["outputs"].get(
        "control_hardening_summary_csv",
        "m39x3d_control_hardening_summary.csv",
    )
    pd.DataFrame(control_rows).to_csv(outdir / control_out, index=False)

    transition_df.to_csv(outdir / config["outputs"]["transition_mapping_summary_csv"], index=False)

    bootstrap_cols = [
        "family_id",
        "variant_id",
        "marker_name",
        "strength_mean",
        "strength_ci_low",
        "strength_ci_high",
        "bootstrap_win_fraction",
        "dominance_stable_flag",
    ]
    if len(marker_df):
        marker_df[bootstrap_cols].to_csv(outdir / config["outputs"]["bootstrap_summary_csv"], index=False)
    else:
        pd.DataFrame(columns=bootstrap_cols).to_csv(outdir / config["outputs"]["bootstrap_summary_csv"], index=False)

    write_json(global_summary, outdir / config["outputs"]["global_summary_json"])

    report_md = "\n".join([
        f"# {config['run']['run_id']}",
        "",
        "## 1. Ziel und Methode",
        "Dense FSW and AO transition mapping for quantitative and qualitative Type-B regimes.",
        "",
        "## 2. Family prediction summary",
        family_prediction_df.to_markdown(index=False) if len(family_prediction_df) else "_keine Daten_",
        "",
        "## 3. Spectral type summary",
        spectral_type_df.to_markdown(index=False) if len(spectral_type_df) else "_keine Daten_",
        "",
        "## 4. Transition mapping summary",
        transition_df.to_markdown(index=False) if len(transition_df) else "_keine Daten_",
        "",
        "## 5. Global status",
        "```json",
        json.dumps(global_summary, indent=2, ensure_ascii=False),
        "```",
        "",
    ])
    write_markdown(report_md, outdir / config["outputs"]["markdown_report"])

    write_markdown(
        "# Source Notes\n\n"
        "- M39x3d transition mapping runner\n"
        "- Dense FSW sweep for quantitative Type-B window mapping\n"
        "- Dense AO sweep for qualitative jump transition mapping\n"
        "- Local transition and knee candidate flags included\n",
        outdir / config["outputs"]["source_notes_md"],
    )

    print(f"[OK] Run completed: {config['run']['run_id']}")
    print(f"[OK] Output directory: {outdir}")


if __name__ == "__main__":
    main()