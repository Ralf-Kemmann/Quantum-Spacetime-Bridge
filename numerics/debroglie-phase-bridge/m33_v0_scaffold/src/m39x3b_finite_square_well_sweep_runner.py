#!/usr/bin/env python3
"""
m39x3b_finite_square_well_sweep_runner.py

M.3.9x.3b — Finite-Square-Well-Sweep und Typ-B-Robustheit
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
# IO
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
            (m * math.pi / a) ** 2
            + (n * math.pi / b) ** 2
            + (p * math.pi / d) ** 2
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
        out[base["variable_name"]] = to_numpy(base["values"])

        # WICHTIGER FIX:
        # Sweep-Familien haben in der YAML aktuell keine eigenen derived_spectra.
        # Deshalb bauen wir die projektweit benötigten Ableitungen hier explizit nach.
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

    return {
        "spacing_mean": spacing_mean,
        "spacing_std": spacing_std,
        "spacing_cv": spacing_cv,
        "spacing_ratio_mean": spacing_ratio_mean,
        "simple_unfolding_density": density,
        "simple_rigidity_surrogate": rigidity,
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

def irregularity_matches_expected(observed_cv: float, expected_level: Optional[str]) -> bool:
    if expected_level is None or expected_level == "open":
        return True
    if expected_level == "low":
        return observed_cv < 0.20
    if expected_level == "low_to_moderate":
        return observed_cv < 0.45
    if expected_level == "moderate":
        return 0.15 <= observed_cv <= 0.60
    if expected_level == "moderate_to_high":
        return observed_cv >= 0.20
    if expected_level == "high":
        return observed_cv >= 0.50
    return True


def evaluate_prediction_match(
    profile: Dict[str, Any],
    observed: Dict[str, Any],
    irregularity: Dict[str, Any],
) -> Tuple[str, str, int, int, int]:
    dominant_marker = observed.get("dominant_marker")
    direction_blindness_flag = observed.get("direction_blindness_flag", 0)
    observed_cv = irregularity.get("spacing_cv", 0.0)

    expected_relative_winner = profile.get("expected_relative_winner")
    expected_allowed_winners = profile.get("expected_allowed_winners", [])
    expected_delta_p2_role = profile.get("expected_delta_p2_role")
    expected_irregularity_level = profile.get("expected_irregularity_level")
    expected_direction_blindness_relevant = profile.get("expected_direction_blindness_relevant", False)

    winner_ok = dominant_marker in expected_allowed_winners if expected_allowed_winners else True
    exact_winner_ok = True if expected_relative_winner in {None, "open"} else dominant_marker == expected_relative_winner
    irregularity_ok = irregularity_matches_expected(observed_cv, expected_irregularity_level)
    direction_ok = True if not expected_direction_blindness_relevant else bool(direction_blindness_flag)

    delta_p2_role_ok = True
    if expected_delta_p2_role == "structure_support_expected":
        delta_p2_role_ok = dominant_marker in expected_allowed_winners

    if winner_ok and exact_winner_ok and irregularity_ok and direction_ok and delta_p2_role_ok:
        return "supported", "Core prediction matched.", 1, 0, 0
    if winner_ok and delta_p2_role_ok:
        return "partially_supported", "Allowed winner matched, but not all side expectations fit.", 0, 1, 0
    if (not winner_ok) and (irregularity_ok or direction_ok):
        return "stressed", "Prediction under pressure: winner mismatch with partial side support.", 0, 0, 0
    return "failed", "Observed dominant marker contradicts prediction profile.", 0, 0, 1


# ---------------------------------------------------------------------
# Diagnostics per family/variant
# ---------------------------------------------------------------------

def run_family_variant_diagnostics(
    family: Dict[str, Any],
    variant: Dict[str, Any],
    config: Dict[str, Any],
    rng: np.random.Generator,
) -> Tuple[pd.DataFrame, Dict[str, Any], Dict[str, Any]]:
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
        return df, {}, {}

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

    direction_blindness_flag = 0
    if family["family_id"] == "ER1_RING" and variant["variant_id"] == "RING_SIGNED":
        if "delta_p" in set(df["marker_name"]) and "delta_p2" in set(df["marker_name"]):
            dom = str(df.iloc[0]["marker_name"])
            dp = float(df[df["marker_name"] == "delta_p"]["absolute_strength"].iloc[0])
            dp2 = float(df[df["marker_name"] == "delta_p2"]["absolute_strength"].iloc[0])
            direction_blindness_flag = int(dom == "delta_p" and dp > dp2)

    observed = {
        "dominant_marker": str(df.iloc[0]["marker_name"]),
        "absolute_best_marker": str(df.sort_values("absolute_strength", ascending=False).iloc[0]["marker_name"]),
        "relative_rank_top3": ",".join(df["marker_name"].head(3).tolist()),
        "dominance_margin": float(df.iloc[0]["dominance_margin"]),
        "bootstrap_win_fraction": float(df.iloc[0]["bootstrap_win_fraction"]),
        "direction_blindness_flag": direction_blindness_flag,
        "marker_df": df.copy(),
    }

    return df, observed, irregularity


# ---------------------------------------------------------------------
# Helper flags / decision logic
# ---------------------------------------------------------------------

def get_marker_row(marker_df: pd.DataFrame, marker_names: List[str]) -> Optional[pd.Series]:
    sub = marker_df[marker_df["marker_name"].isin(marker_names)]
    if len(sub) == 0:
        return None
    return sub.sort_values(["relative_rank", "bootstrap_win_fraction"], ascending=[True, False]).iloc[0]


def build_common_flags_for_row(
    row: pd.Series,
    type_a_reference_row: Optional[pd.Series],
    config: Dict[str, Any],
) -> Dict[str, Any]:
    flags: Dict[str, Any] = {}
    marker_df = row["extra"].get("marker_df")
    if marker_df is None or len(marker_df) == 0:
        return flags

    spacing_cv = float(row["observed_spacing_cv"]) if pd.notna(row["observed_spacing_cv"]) else 0.0
    flags["observed_irregularity_level"] = irregularity_level_from_cv(spacing_cv, config)

    delta_p_row = get_marker_row(marker_df, ["delta_p", "abs_delta_p"])
    delta_p2_row = get_marker_row(marker_df, ["delta_p2", "abs_delta_p2"])

    thresholds = config["strength_scoring"]["support_thresholds"]
    competitive_margin_max = float(thresholds["competitive_margin_max"])
    absolute_support_min = float(thresholds["absolute_support_min"])
    dominance_margin_min = float(thresholds["dominance_margin_min"])

    if delta_p_row is not None:
        flags["delta_p_competitive"] = bool(
            int(delta_p_row["relative_rank"]) <= 2 or abs(float(delta_p_row["dominance_margin"])) <= competitive_margin_max
        )
    else:
        flags["delta_p_competitive"] = False

    if delta_p2_row is not None:
        flags["delta_p2_absolute_strength_high"] = bool(float(delta_p2_row["absolute_strength"]) >= absolute_support_min)
        flags["delta_p2_not_clearly_dominant"] = not (
            int(delta_p2_row["relative_rank"]) == 1 and float(delta_p2_row["dominance_margin"]) > dominance_margin_min
        )
    else:
        flags["delta_p2_absolute_strength_high"] = False
        flags["delta_p2_not_clearly_dominant"] = True

    if type_a_reference_row is not None and delta_p2_row is not None:
        ref_marker_df = type_a_reference_row["extra"].get("marker_df")
        ref_delta_p2_row = get_marker_row(ref_marker_df, ["delta_p2", "abs_delta_p2"]) if ref_marker_df is not None else None
        if ref_delta_p2_row is not None:
            flags["delta_p2_relative_gain_vs_type_A"] = (
                float(delta_p2_row["bootstrap_win_fraction"]) - float(ref_delta_p2_row["bootstrap_win_fraction"])
            )
        else:
            flags["delta_p2_relative_gain_vs_type_A"] = 0.0
    else:
        flags["delta_p2_relative_gain_vs_type_A"] = 0.0

    return flags


def compute_distance_to_type_d(
    sweep_row: pd.Series,
    type_d_row: Optional[pd.Series],
    sweep_flags: Dict[str, Any],
    config: Dict[str, Any],
) -> float:
    if type_d_row is None:
        return 0.0

    score = 0.0

    if sweep_row["dominant_marker"] != type_d_row["dominant_marker"]:
        score += 0.10

    sweep_level = sweep_flags.get("observed_irregularity_level", "open")
    type_d_level = irregularity_level_from_cv(float(type_d_row["observed_spacing_cv"]), config)
    if sweep_level != type_d_level:
        score += 0.10

    gain = float(sweep_flags.get("delta_p2_relative_gain_vs_type_A", 0.0))
    if gain > 0:
        score += min(0.20, gain)

    return float(score)


def build_sweep_flags(
    sweep_row: pd.Series,
    type_a_reference_row: Optional[pd.Series],
    type_d_row: Optional[pd.Series],
    config: Dict[str, Any],
) -> Dict[str, Any]:
    flags = build_common_flags_for_row(sweep_row, type_a_reference_row, config)
    flags["distance_to_type_D"] = compute_distance_to_type_d(sweep_row, type_d_row, flags, config)

    dist = float(flags.get("distance_to_type_D", 0.0))
    gain = float(flags.get("delta_p2_relative_gain_vs_type_A", 0.0))
    irr = flags.get("observed_irregularity_level", "open")
    n_bound_states = int(sweep_row["extra"].get("n_bound_states", 0))

    flags["box_like_proximity_flag"] = bool(
        dist <= 0.0
        and sweep_row["dominant_marker"] in {"delta_p", "abs_delta_p"}
        and irr in {"low", "low_to_moderate"}
    )

    flags["edge_case_instability_flag"] = bool(
        n_bound_states < 5 or (irr in {"moderate_to_high", "high"} and dist <= 0.0)
    )

    flags["best_type_B_window_candidate_flag"] = bool(
        gain > 0.0
        and dist > 0.0
        and sweep_row["prediction_match_status"] in {"partially_supported", "supported"}
    )

    return flags


def evaluate_type_d(flags: Dict[str, Any], dominant_marker: str) -> Tuple[str, str]:
    winner = dominant_marker
    irr = flags.get("observed_irregularity_level", "open")
    dp_comp = bool(flags.get("delta_p_competitive", False))
    dp2_abs_high = bool(flags.get("delta_p2_absolute_strength_high", False))
    dp2_not_clear = bool(flags.get("delta_p2_not_clearly_dominant", True))

    if winner in {"delta_p", "abs_delta_p"} or (winner in {"delta_p", "abs_delta_p"} and dp2_abs_high):
        return "supported", "Type D supports the broader regularity reading."

    if winner in {"delta_p", "abs_delta_p", "delta_p2", "abs_delta_p2"} and (dp_comp or dp2_not_clear):
        return "partially_supported", "Type D remains compatible with the broader regularity reading."

    if winner in {"delta_p2", "abs_delta_p2"} and dp_comp:
        return "stressed", "Type D pressures the broader regularity reading."

    if winner in {"delta_p2", "abs_delta_p2"} and (not dp_comp) and irr in {"low", "low_to_moderate"}:
        return "failed", "Type D damages the broader regularity reading."

    return "open", "Type D decision remains open."


def evaluate_regime(rule_key: str, flags: Dict[str, Any], row: pd.Series) -> Tuple[str, str]:
    regime_id = row["extra"].get("regime_id", rule_key)
    gain = float(flags.get("delta_p2_relative_gain_vs_type_A", 0.0))
    dist = float(flags.get("distance_to_type_D", 0.0))
    box_like = bool(flags.get("box_like_proximity_flag", False))
    edge_case = bool(flags.get("edge_case_instability_flag", False))
    best_window = bool(flags.get("best_type_B_window_candidate_flag", False))

    if regime_id == "FSW_DEEP":
        if row["prediction_match_status"] in {"partially_supported", "supported"} and box_like:
            return "supported", "Deep regime behaves as expected: box-like and Type-D-close."
        if row["prediction_match_status"] in {"partially_supported", "supported"}:
            return "partially_supported", "Deep regime remains plausible but less box-like than expected."
        if box_like:
            return "stressed", "Deep regime is overly box-like without stable support."
        return "open", "Deep regime remains open."

    if regime_id == "FSW_INTERMEDIATE":
        if row["prediction_match_status"] in {"partially_supported", "supported"} and gain > 0 and dist > 0 and best_window:
            return "supported", "Intermediate regime is the strongest Type-B-window candidate."
        if row["prediction_match_status"] in {"partially_supported", "supported"} and gain > 0:
            return "partially_supported", "Intermediate regime is plausible but not yet maximally sharp."
        if dist <= 0:
            return "stressed", "Intermediate regime remains too close to Type D."
        return "open", "Intermediate regime remains open."

    if regime_id == "FSW_SHALLOW":
        if row["prediction_match_status"] in {"partially_supported", "supported"} and dist > 0 and not edge_case:
            return "supported", "Shallow regime remains useful without edge-case instability."
        if row["prediction_match_status"] in {"partially_supported", "supported"} and dist > 0:
            return "partially_supported", "Shallow regime is plausible but edge-case sensitive."
        if edge_case:
            return "stressed", "Shallow regime behaves like an edge-case only."
        return "open", "Shallow regime remains open."

    return "open", f"Unknown regime {regime_id}."


def evaluate_global_sweep(regime_rows: pd.DataFrame) -> str:
    if len(regime_rows) == 0:
        return "finite_square_well_too_close_to_type_D"

    def get_row(rid: str) -> Optional[pd.Series]:
        sub = regime_rows[regime_rows["regime_id"] == rid]
        return sub.iloc[0] if len(sub) else None

    deep = get_row("FSW_DEEP")
    inter = get_row("FSW_INTERMEDIATE")
    shallow = get_row("FSW_SHALLOW")

    any_positive_dist = bool((regime_rows["distance_to_type_D"] > 0).any())
    any_positive_gain = bool((regime_rows["delta_p2_relative_gain_vs_type_A"] > 0).any())

    if inter is not None:
        if bool(inter["best_type_B_window_candidate_flag"]) and inter["prediction_match_status"] in {"partially_supported", "supported"} and float(inter["distance_to_type_D"]) > 0:
            return "finite_square_well_type_B_window_found"

    if any_positive_dist and any_positive_gain:
        shallow_edge = bool(shallow["edge_case_instability_flag"]) if shallow is not None else False
        if shallow_edge or (inter is not None and inter["prediction_match_status"] == "partially_supported"):
            return "finite_square_well_type_B_window_plausible_but_narrow"

    all_box_like = bool(regime_rows["box_like_proximity_flag"].all())
    all_nonpositive_dist = bool((regime_rows["distance_to_type_D"] <= 0).all())
    if all_box_like or all_nonpositive_dist:
        return "finite_square_well_too_close_to_type_D"

    if shallow is not None:
        only_shallow_positive = False
        if float(shallow["distance_to_type_D"]) > 0:
            others = regime_rows[regime_rows["regime_id"] != "FSW_SHALLOW"]
            only_shallow_positive = bool((others["distance_to_type_D"] <= 0).all())
        if only_shallow_positive or bool(shallow["edge_case_instability_flag"]):
            return "finite_square_well_edge_case_only"

    return "finite_square_well_type_B_window_plausible_but_narrow"


# ---------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", default="configs/config_m39x3b_finite_square_well_sweep.yaml")
    args = parser.parse_args()

    config = load_yaml(args.config)
    families_cfg = load_yaml(config["inputs"]["family_definitions_yaml"])
    families = families_cfg.get("families", [])

    outdir = ensure_dir(config["run"]["outdir"])
    rng = np.random.default_rng(int(config["run"].get("random_seed", 1729)))

    marker_rows: List[MarkerScore] = []
    family_prediction_rows: List[FamilyPredictionResult] = []
    irregularity_rows: List[Dict[str, Any]] = []
    control_hardening_rows: List[Dict[str, Any]] = []
    sweep_summary_rows: List[Dict[str, Any]] = []
    missing_case_rows: List[Dict[str, Any]] = []
    implemented_result_rows: List[Dict[str, Any]] = []

    analysis_items: List[Tuple[Dict[str, Any], Dict[str, Any], Dict[str, Any]]] = []

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
                    analysis_items.append((family, variant, family["prediction_profile"]))

        if "sweep_regimes" in family:
            regime_profiles = config.get("regime_prediction_profiles", {})
            for regime in family["sweep_regimes"]:
                regime_id = regime["regime_id"]
                variant = {
                    "variant_id": regime_id,
                    "enabled": True,
                    "pairing_mode": "all_pairs",
                    "degeneracy_policy": {
                        "treat_sign_as_distinct": False,
                        "collapse_equal_energy_shells": False,
                        "exclude_sign_mirror_pairs": True,
                    },
                    "active_spectrum": regime["base_spectrum"]["variable_name"],
                    "active_markers": ["delta_p", "abs_delta_p", "delta_p2", "abs_delta_p2", "delta_E_quad"],
                    "base_spectrum": regime["base_spectrum"],
                    "regime_id": regime_id,
                    "regime_label": regime.get("regime_label", regime_id),
                    "well_depth": regime.get("well_depth"),
                    "expectation": regime.get("expectation"),
                }
                profile = regime_profiles.get(regime_id, family.get("prediction_profile", {}))
                analysis_items.append((family, variant, profile))

    for family, variant, profile in analysis_items:
        family_id = family["family_id"]
        family_label = family["family_label"]
        spectral_type = family["spectral_type"]
        model_class = family["model_class"]
        status = family.get("status", "implemented")
        enabled = bool(family.get("enabled", False))
        variant_id = variant["variant_id"]

        marker_df, observed, irregularity = run_family_variant_diagnostics(family, variant, config, rng)

        n_pairs = 0
        if len(marker_df):
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

        match_status, match_note, hard_pass, soft_pass, fail_flag = evaluate_prediction_match(profile, observed, irregularity)

        spec_for_counts = build_family_spectra(family, variant)
        active_spectrum_name = variant["active_spectrum"]
        n_bound_states = len(spec_for_counts[active_spectrum_name])

        result = FamilyPredictionResult(
            family_id=family_id,
            family_label=family_label,
            spectral_type=spectral_type,
            model_class=model_class,
            status=status,
            enabled=enabled,
            variant_id=variant_id,
            dominant_marker=observed.get("dominant_marker"),
            absolute_best_marker=observed.get("absolute_best_marker"),
            relative_rank_top3=observed.get("relative_rank_top3", ""),
            dominance_margin=observed.get("dominance_margin"),
            bootstrap_win_fraction=observed.get("bootstrap_win_fraction"),
            prediction_match_status=match_status,
            prediction_match_note=match_note,
            prediction_hard_pass_flag=hard_pass,
            prediction_soft_pass_flag=soft_pass,
            prediction_fail_flag=fail_flag,
            expected_relative_winner=profile.get("expected_relative_winner"),
            expected_allowed_winners=",".join(profile.get("expected_allowed_winners", [])),
            expected_delta_p2_role=profile.get("expected_delta_p2_role"),
            expected_irregularity_level=profile.get("expected_irregularity_level"),
            expected_direction_blindness_relevant=profile.get("expected_direction_blindness_relevant"),
            observed_spacing_cv=irregularity.get("spacing_cv"),
            observed_spacing_ratio_mean=irregularity.get("spacing_ratio_mean"),
            observed_direction_blindness_flag=observed.get("direction_blindness_flag", 0),
            extra={
                "marker_df": observed.get("marker_df"),
                "n_bound_states": n_bound_states,
                "regime_id": variant.get("regime_id"),
                "regime_label": variant.get("regime_label"),
                "well_depth": variant.get("well_depth"),
                "expectation": variant.get("expectation"),
                "well_width": family.get("fixed_parameters", {}).get("well_width"),
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

    def get_impl_row(fid: str, variant_id: str) -> Optional[pd.Series]:
        if len(implemented_df) == 0:
            return None
        sub = implemented_df[
            (implemented_df["family_id"] == fid) &
            (implemented_df["variant_id"] == variant_id)
        ]
        if len(sub) == 0:
            return None
        return sub.iloc[0]

    type_a_ref = get_impl_row(
        config["control_hardening"]["type_A_reference_family"],
        config["control_hardening"]["type_A_reference_variant"],
    )
    type_d_ref = get_impl_row(
        config["control_hardening"]["type_D_reference_family"],
        config["control_hardening"]["type_D_reference_variant"],
    )

    if type_d_ref is not None:
        type_d_flags = build_common_flags_for_row(type_d_ref, type_a_ref, config)
        hard_status, hard_note = evaluate_type_d(type_d_flags, type_d_ref["dominant_marker"])
        control_hardening_rows.append({
            "family_id": type_d_ref["family_id"],
            "variant_id": type_d_ref["variant_id"],
            "spectral_type": type_d_ref["spectral_type"],
            "hardening_status": hard_status,
            "hardening_note": hard_note,
            **type_d_flags,
        })
        family_prediction_df.loc[
            (family_prediction_df["family_id"] == type_d_ref["family_id"]) &
            (family_prediction_df["variant_id"] == type_d_ref["variant_id"]),
            ["prediction_match_status", "prediction_match_note"]
        ] = [hard_status, hard_note]

    sweep_rows = implemented_df[implemented_df["family_id"] == config["finite_square_well_sweep"]["family_id"]].copy()

    for _, row in sweep_rows.iterrows():
        flags = build_sweep_flags(row, type_a_ref, type_d_ref, config)
        regime_status, regime_note = evaluate_regime(str(row["variant_id"]), flags, row)

        family_prediction_df.loc[
            (family_prediction_df["family_id"] == row["family_id"]) &
            (family_prediction_df["variant_id"] == row["variant_id"]),
            ["prediction_match_status", "prediction_match_note"]
        ] = [regime_status, regime_note]

        sweep_summary_rows.append({
            "regime_id": row["variant_id"],
            "well_depth": row["extra"].get("well_depth"),
            "well_width": row["extra"].get("well_width"),
            "n_bound_states": row["extra"].get("n_bound_states"),
            "dominant_marker": row["dominant_marker"],
            "delta_p2_relative_gain_vs_type_A": flags.get("delta_p2_relative_gain_vs_type_A", 0.0),
            "distance_to_type_D": flags.get("distance_to_type_D", 0.0),
            "observed_irregularity_level": flags.get("observed_irregularity_level", "open"),
            "prediction_match_status": regime_status,
            "box_like_proximity_flag": flags.get("box_like_proximity_flag", False),
            "edge_case_instability_flag": flags.get("edge_case_instability_flag", False),
            "best_type_B_window_candidate_flag": flags.get("best_type_B_window_candidate_flag", False),
            "type_B_robustness_value": float(flags.get("delta_p2_relative_gain_vs_type_A", 0.0))
            + float(flags.get("distance_to_type_D", 0.0)),
            "regime_interpretation": row["extra"].get("expectation"),
        })

        control_hardening_rows.append({
            "family_id": row["family_id"],
            "variant_id": row["variant_id"],
            "spectral_type": row["spectral_type"],
            "hardening_status": regime_status,
            "hardening_note": regime_note,
            **flags,
        })

    sweep_summary_df = pd.DataFrame(sweep_summary_rows)
    global_sweep_status = evaluate_global_sweep(sweep_summary_df)
    control_hardening_df = pd.DataFrame(control_hardening_rows)

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

    global_summary = {
        "run_id": config["run"]["run_id"],
        "n_families_total": len(families),
        "n_families_implemented": int(sum(1 for f in families if f.get("status", "implemented") == "implemented" and f.get("enabled", False))),
        "n_prediction_supported": int((family_prediction_df["prediction_match_status"] == "supported").sum()) if len(family_prediction_df) else 0,
        "n_prediction_partially_supported": int((family_prediction_df["prediction_match_status"] == "partially_supported").sum()) if len(family_prediction_df) else 0,
        "n_prediction_open": int((family_prediction_df["prediction_match_status"] == "open").sum()) if len(family_prediction_df) else 0,
        "n_prediction_stressed": int((family_prediction_df["prediction_match_status"] == "stressed").sum()) if len(family_prediction_df) else 0,
        "n_prediction_failed": int((family_prediction_df["prediction_match_status"] == "failed").sum()) if len(family_prediction_df) else 0,
        "global_prediction_status": global_sweep_status,
    }

    marker_df.to_csv(outdir / config["outputs"]["marker_summary_csv"], index=False)
    family_prediction_df.to_csv(outdir / config["outputs"]["family_prediction_summary_csv"], index=False)
    irregularity_df.to_csv(outdir / config["outputs"]["irregularity_summary_csv"], index=False)
    spectral_type_df.to_csv(outdir / config["outputs"]["spectral_type_summary_csv"], index=False)
    missing_cases_df.to_csv(outdir / config["outputs"]["missing_cases_summary_csv"], index=False)
    control_hardening_df.to_csv(outdir / config["outputs"]["control_hardening_summary_csv"], index=False)
    sweep_summary_df.to_csv(outdir / config["outputs"]["finite_square_well_sweep_summary_csv"], index=False)

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
        "Finite-square-well sweep with fixed width and varying depth regimes.",
        "",
        "## 2. Family prediction summary",
        family_prediction_df.to_markdown(index=False) if len(family_prediction_df) else "_keine Daten_",
        "",
        "## 3. Spectral type summary",
        spectral_type_df.to_markdown(index=False) if len(spectral_type_df) else "_keine Daten_",
        "",
        "## 4. Control hardening summary",
        control_hardening_df.to_markdown(index=False) if len(control_hardening_df) else "_keine Daten_",
        "",
        "## 5. Finite square well sweep summary",
        sweep_summary_df.to_markdown(index=False) if len(sweep_summary_df) else "_keine Daten_",
        "",
        "## 6. Global status",
        "```json",
        json.dumps(global_summary, indent=2, ensure_ascii=False),
        "```",
        "",
    ])
    write_markdown(report_md, outdir / config["outputs"]["markdown_report"])

    write_markdown(
        "# Source Notes\n\n"
        "- M39x3b finite-square-well sweep runner\n"
        "- Fixed width, depth sweep across deep/intermediate/shallow regimes\n"
        "- Type-A and Type-D references retained for relative comparison\n",
        outdir / config["outputs"]["source_notes_md"],
    )

    print(f"[OK] Run completed: {config['run']['run_id']}")
    print(f"[OK] Output directory: {outdir}")


if __name__ == "__main__":
    main()