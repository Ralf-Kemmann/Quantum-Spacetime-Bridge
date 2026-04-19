#!/usr/bin/env python3
"""
m39x3_prediction_matrix_hardening_runner.py

M.3.9x.3 — Typ-B-/Typ-D-Kontrollfälle und Härtung der Vorhersagematrix
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
# IO / YAML
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
# Spektren / Paarbildung
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
    k_values = []
    for m, n, p in family["mode_table"]["mode_indices"]:
        k = math.sqrt((m * math.pi / a) ** 2 + (n * math.pi / b) ** 2 + (p * math.pi / d) ** 2)
        k_values.append(k)
    return np.asarray(k_values, dtype=float)


def build_circular_membrane_k_values(family: Dict[str, Any]) -> np.ndarray:
    bessel_zero_lookup: Dict[Tuple[int, int], float] = {
        (0, 1): 2.4048255577,
        (0, 2): 5.5200781103,
        (0, 3): 8.6537279129,
        (1, 1): 3.8317059702,
        (1, 2): 7.0155866698,
        (1, 3): 10.1734681351,
        (2, 1): 5.1356223018,
        (2, 2): 8.4172441404,
        (2, 3): 11.6198411721,
        (3, 1): 6.3801618952,
        (3, 2): 9.7610231299,
        (3, 3): 13.0152007217,
    }
    k_values = []
    for m, n in family["mode_table"]["mode_indices"]:
        key = (int(m), int(n))
        if key not in bessel_zero_lookup:
            raise ValueError(f"Missing Bessel zero lookup for membrane mode {key} in family {family['family_id']}.")
        k_values.append(bessel_zero_lookup[key])
    return np.asarray(k_values, dtype=float)


def build_family_spectra(family: Dict[str, Any]) -> Dict[str, np.ndarray]:
    out: Dict[str, np.ndarray] = {}
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
        raise NotImplementedError(f"Unsupported base spectrum construction for {family['family_id']}.")

    for item in family.get("derived_spectra", []):
        out[item["variable_name"]] = derive_spectrum(out[item["from"]], item["transform"], item.get("parameters", {}))

    return out


# ---------------------------------------------------------------------
# Marker
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
        return float(p2[i] - p2[j]) if p2 is not None else float(k2[i] - k2[j])
    if marker_name == "abs_delta_p2":
        return abs(float(p2[i] - p2[j])) if p2 is not None else abs(float(k2[i] - k2[j]))
    if marker_name == "delta_E_quad":
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
# Labels / Scores
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
    names = list(marker_vectors.keys())
    idx = np.arange(len(labels))
    wins = {name: 0 for name in names}

    for _ in range(n_bootstrap):
        sample_idx = rng.choice(idx, size=len(idx), replace=True)
        scores = {name: rank_separation_score(vec[sample_idx], labels[sample_idx]) for name, vec in marker_vectors.items()}
        best = max(scores.items(), key=lambda x: x[1])[0]
        wins[best] += 1

    return {name: wins[name] / n_bootstrap for name in names}


# ---------------------------------------------------------------------
# Irregularität
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
# Family diagnostics
# ---------------------------------------------------------------------

def run_family_variant_diagnostics(
    family: Dict[str, Any],
    variant: Dict[str, Any],
    config: Dict[str, Any],
    rng: np.random.Generator,
) -> Tuple[pd.DataFrame, Dict[str, Any], Dict[str, Any]]:
    spec_all = build_family_spectra(family)
    pairing_mode = variant["pairing_mode"]
    active_spectrum = variant["active_spectrum"]
    active_markers = variant["active_markers"]
    degeneracy_policy = variant.get("degeneracy_policy", {})

    pairs = build_pairs(spec_all[active_spectrum], pairing_mode)

    if family["family_id"] == "ER1_RING":
        pairs = apply_ring_pair_filters(spec_all["p"], pairs, degeneracy_policy, active_spectrum)

    labels = infer_pair_labels_from_existing_logic(family, pairs, spec_all)
    n_boot = int(config["bootstrap"]["n_bootstrap"])

    marker_vectors = {marker: compute_marker_vector(marker, spec_all, pairs) for marker in active_markers}
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
        if idx == 0:
            dominance_margin_map[row["marker_name"]] = float(row["absolute_strength"]) - second_abs
        else:
            dominance_margin_map[row["marker_name"]] = float(row["absolute_strength"]) - best_abs
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
# x.2 prediction evaluation
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
    family: Dict[str, Any],
    observed: Dict[str, Any],
    irregularity: Dict[str, Any],
) -> Tuple[str, str, int, int, int]:
    status = family.get("status", "implemented")
    profile = family["prediction_profile"]

    if status == "placeholder":
        return "open", "Family is placeholder and not yet implemented.", 0, 0, 0

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
# x.3 derived flags / hardening
# ---------------------------------------------------------------------

def get_marker_row(marker_df: pd.DataFrame, marker_names: List[str]) -> Optional[pd.Series]:
    sub = marker_df[marker_df["marker_name"].isin(marker_names)]
    if len(sub) == 0:
        return None
    return sub.sort_values(["relative_rank", "bootstrap_win_fraction"], ascending=[True, False]).iloc[0]


def build_derived_flags_for_family(
    family_result_row: pd.Series,
    type_a_reference_row: Optional[pd.Series],
    config: Dict[str, Any],
) -> Dict[str, Any]:
    flags: Dict[str, Any] = {}

    marker_df = family_result_row["extra"].get("marker_df")
    if marker_df is None or len(marker_df) == 0:
        return flags

    spacing_cv = float(family_result_row["observed_spacing_cv"]) if pd.notna(family_result_row["observed_spacing_cv"]) else 0.0
    flags["observed_irregularity_level"] = irregularity_level_from_cv(spacing_cv, config)

    delta_p_row = get_marker_row(marker_df, ["delta_p", "abs_delta_p"])
    delta_p2_row = get_marker_row(marker_df, ["delta_p2", "abs_delta_p2"])

    competitive_margin_max = float(config["strength_scoring"]["support_thresholds"]["competitive_margin_max"])
    absolute_support_min = float(config["strength_scoring"]["support_thresholds"]["absolute_support_min"])
    dominance_margin_min = float(config["strength_scoring"]["support_thresholds"]["dominance_margin_min"])

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

    # type-B specific vs type-A reference
    if type_a_reference_row is not None and delta_p2_row is not None:
        ref_marker_df = type_a_reference_row["extra"].get("marker_df")
        ref_delta_p2_row = get_marker_row(ref_marker_df, ["delta_p2", "abs_delta_p2"]) if ref_marker_df is not None else None
        if ref_delta_p2_row is not None:
            gain = float(delta_p2_row["bootstrap_win_fraction"]) - float(ref_delta_p2_row["bootstrap_win_fraction"])
            flags["delta_p2_relative_gain_vs_type_A"] = gain
        else:
            flags["delta_p2_relative_gain_vs_type_A"] = 0.0
    else:
        flags["delta_p2_relative_gain_vs_type_A"] = 0.0

    return flags


def build_behavior_matches_type_d_too_closely(
    type_b_flags: Dict[str, Any],
    type_d_row: Optional[pd.Series],
    type_b_row: pd.Series,
) -> bool:
    if type_d_row is None:
        return False

    type_d_level = irregularity_level_from_cv(float(type_d_row["observed_spacing_cv"]), {
        "irregularity_levels": {
            "low": {"spacing_cv_max": 0.20},
            "low_to_moderate": {"spacing_cv_max": 0.45},
            "moderate": {"spacing_cv_min": 0.15, "spacing_cv_max": 0.60},
            "moderate_to_high": {"spacing_cv_min": 0.20},
            "high": {"spacing_cv_min": 0.50},
        }
    })

    return bool(
        type_b_row["dominant_marker"] == type_d_row["dominant_marker"]
        and type_b_flags.get("observed_irregularity_level") == type_d_level
        and type_b_flags.get("delta_p2_relative_gain_vs_type_A", 0.0) <= 0.0
    )


def evaluate_type_b_decision(flags: Dict[str, Any], dominant_marker: str) -> Tuple[str, str]:
    winner = dominant_marker
    irr = flags.get("observed_irregularity_level", "open")
    gain = float(flags.get("delta_p2_relative_gain_vs_type_A", 0.0))
    too_close = bool(flags.get("behavior_matches_type_D_too_closely", False))

    if winner in {"delta_p2", "abs_delta_p2"} and gain > 0 and irr in {"moderate", "moderate_to_high"}:
        return "supported", "Type B shows delta_p2 gain over Type A with nontrivial irregularity."

    if winner in {"delta_p", "abs_delta_p", "delta_p2", "abs_delta_p2"} and gain >= 0:
        if not (winner in {"delta_p2", "abs_delta_p2"} and irr in {"moderate", "moderate_to_high"}):
            return "partially_supported", "Type B is plausible but not yet sharply distinct."

    if winner in {"delta_p", "abs_delta_p"} and gain == 0:
        return "stressed", "Type B behaves too much like a regular spacing-dominated case."

    if winner in {"delta_p", "abs_delta_p"} and gain <= 0 and too_close and irr in {"low", "low_to_moderate"}:
        return "failed", "Type B collapses into a cosmetic deformation of a regular case."

    return "open", "Type B decision remains open."


def evaluate_type_d_decision(flags: Dict[str, Any], dominant_marker: str) -> Tuple[str, str]:
    winner = dominant_marker
    irr = flags.get("observed_irregularity_level", "open")
    dp_comp = bool(flags.get("delta_p_competitive", False))
    dp2_abs_high = bool(flags.get("delta_p2_absolute_strength_high", False))
    dp2_not_clear = bool(flags.get("delta_p2_not_clearly_dominant", True))

    if winner in {"delta_p", "abs_delta_p"} or (winner in {"delta_p", "abs_delta_p"} and dp2_abs_high):
        return "supported", "Type D supports a broader regularity reading."

    if winner in {"delta_p", "abs_delta_p", "delta_p2", "abs_delta_p2"} and (dp_comp or dp2_not_clear):
        return "partially_supported", "Type D is compatible with regularity reading but not decisive."

    if winner in {"delta_p2", "abs_delta_p2"} and dp_comp:
        return "stressed", "Type D pressures the broad regularity reading."

    if winner in {"delta_p2", "abs_delta_p2"} and (not dp_comp) and irr in {"low", "low_to_moderate"}:
        return "failed", "Type D damages the broad regularity reading."

    return "open", "Type D decision remains open."


def evaluate_cross_type(
    type_b_row: Optional[pd.Series],
    type_d_row: Optional[pd.Series],
    type_b_flags: Dict[str, Any],
    config: Dict[str, Any],
) -> Tuple[str, str]:
    if type_b_row is None or type_d_row is None:
        return "no_cross_type_alarm", "Cross-type comparison incomplete."

    type_b_level = type_b_flags.get("observed_irregularity_level", "open")
    type_d_level = irregularity_level_from_cv(float(type_d_row["observed_spacing_cv"]), config)
    type_b_winner = type_b_row["dominant_marker"]
    type_d_winner = type_d_row["dominant_marker"]
    type_b_status = type_b_row["prediction_match_status"]
    type_d_status = type_d_row["prediction_match_status"]
    gain = float(type_b_flags.get("delta_p2_relative_gain_vs_type_A", 0.0))

    if (
        type_b_winner in {"delta_p", "abs_delta_p"}
        and type_d_winner in {"delta_p", "abs_delta_p"}
        and gain <= 0
        and type_b_level == type_d_level
    ):
        return "prediction_matrix_revised", "Type B collapses into Type D and fails to function as an intermediate class."

    if (
        (type_b_winner == type_d_winner and type_b_level == type_d_level)
        or (type_b_status == "partially_supported" and type_d_status == "partially_supported")
        or bool(type_b_flags.get("behavior_matches_type_D_too_closely", False))
    ):
        return "prediction_matrix_stressed_by_controls", "Type B and Type D are not cleanly distinguishable."

    return "no_cross_type_alarm", "Type B and Type D remain distinguishable enough."


# ---------------------------------------------------------------------
# Summary / Reporting
# ---------------------------------------------------------------------

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


def build_global_prediction_status(
    family_prediction_df: pd.DataFrame,
    control_hardening_df: pd.DataFrame,
    cross_type_status: str,
    families: List[Dict[str, Any]],
) -> Dict[str, Any]:
    n_total = len(families)
    n_implemented = int(sum(1 for f in families if f.get("status", "implemented") == "implemented" and f.get("enabled", False)))

    n_supported = int((family_prediction_df["prediction_match_status"] == "supported").sum()) if len(family_prediction_df) else 0
    n_partially_supported = int((family_prediction_df["prediction_match_status"] == "partially_supported").sum()) if len(family_prediction_df) else 0
    n_open = int((family_prediction_df["prediction_match_status"] == "open").sum()) if len(family_prediction_df) else 0
    n_stressed = int((family_prediction_df["prediction_match_status"] == "stressed").sum()) if len(family_prediction_df) else 0
    n_failed = int((family_prediction_df["prediction_match_status"] == "failed").sum()) if len(family_prediction_df) else 0

    type_b_row = control_hardening_df[control_hardening_df["family_id"] == "TB1_1D_BOX_WEAKLY_DEFORMED"]
    type_d_row = control_hardening_df[control_hardening_df["family_id"] == "TD1_1D_BOX"]
    type_b_status = type_b_row.iloc[0]["hardening_status"] if len(type_b_row) else "open"
    type_d_status = type_d_row.iloc[0]["hardening_status"] if len(type_d_row) else "open"

    no_failed_core_prediction = (n_failed == 0)
    at_least_one_new_control_supported = type_b_status == "supported" or type_d_status == "supported"

    if no_failed_core_prediction and cross_type_status == "no_cross_type_alarm" and at_least_one_new_control_supported:
        global_status = "prediction_matrix_strengthened"
    elif no_failed_core_prediction and type_b_status in {"partially_supported", "open"} and type_d_status in {"partially_supported", "open"}:
        global_status = "prediction_matrix_still_partial"
    elif cross_type_status == "prediction_matrix_stressed_by_controls" or type_b_status == "stressed" or type_d_status == "stressed":
        global_status = "prediction_matrix_stressed_by_controls"
    elif cross_type_status == "prediction_matrix_revised" or type_b_status == "failed" or type_d_status == "failed":
        global_status = "prediction_matrix_revised"
    else:
        global_status = "prediction_matrix_still_partial"

    return {
        "run_id": "M39x3_prediction_matrix_hardening",
        "n_families_total": n_total,
        "n_families_implemented": n_implemented,
        "n_prediction_supported": n_supported,
        "n_prediction_partially_supported": n_partially_supported,
        "n_prediction_open": n_open,
        "n_prediction_stressed": n_stressed,
        "n_prediction_failed": n_failed,
        "type_B_hardening_status": type_b_status,
        "type_D_hardening_status": type_d_status,
        "cross_type_status": cross_type_status,
        "global_prediction_status": global_status,
    }


def build_markdown_report(
    run_id: str,
    family_prediction_df: pd.DataFrame,
    spectral_type_df: pd.DataFrame,
    control_hardening_df: pd.DataFrame,
    global_summary: Dict[str, Any],
) -> str:
    lines = [
        f"# {run_id}",
        "",
        "## 1. Ziel und Methode",
        "Prediction-matrix hardening run with explicit Type-B and Type-D control cases.",
        "",
        "## 2. Family-wise Vorhersage-Passung",
        family_prediction_df.to_markdown(index=False) if len(family_prediction_df) else "_keine Familiendaten_",
        "",
        "## 3. Zusammenfassung nach Spektraltyp",
        spectral_type_df.to_markdown(index=False) if len(spectral_type_df) else "_keine Typdaten_",
        "",
        "## 4. Control Hardening Summary",
        control_hardening_df.to_markdown(index=False) if len(control_hardening_df) else "_keine Härtungsdaten_",
        "",
        "## 5. Globaler Status",
        "```json",
        json.dumps(global_summary, indent=2, ensure_ascii=False),
        "```",
        "",
    ]
    return "\n".join(lines)


# ---------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", default="configs/config_m39x3_prediction_matrix_hardening.yaml")
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
    missing_case_rows: List[Dict[str, Any]] = []

    # collect per family/variant results for later comparisons
    implemented_result_rows: List[Dict[str, Any]] = []

    for family in families:
        family_id = family["family_id"]
        family_label = family["family_label"]
        spectral_type = family["spectral_type"]
        model_class = family["model_class"]
        status = family.get("status", "implemented")
        enabled = bool(family.get("enabled", False))

        if status == "placeholder" or not enabled:
            missing_case_rows.append({
                "family_id": family_id,
                "family_label": family_label,
                "spectral_type": spectral_type,
                "status": status,
                "implementation_note": family.get("implementation_note", ""),
            })
            family_prediction_rows.append(
                FamilyPredictionResult(
                    family_id=family_id,
                    family_label=family_label,
                    spectral_type=spectral_type,
                    model_class=model_class,
                    status=status,
                    enabled=enabled,
                    variant_id="N/A",
                    dominant_marker=None,
                    absolute_best_marker=None,
                    relative_rank_top3="",
                    dominance_margin=None,
                    bootstrap_win_fraction=None,
                    prediction_match_status="open",
                    prediction_match_note="Placeholder / missing control case.",
                    prediction_hard_pass_flag=0,
                    prediction_soft_pass_flag=0,
                    prediction_fail_flag=0,
                    expected_relative_winner=family["prediction_profile"].get("expected_relative_winner"),
                    expected_allowed_winners=",".join(family["prediction_profile"].get("expected_allowed_winners", [])),
                    expected_delta_p2_role=family["prediction_profile"].get("expected_delta_p2_role"),
                    expected_irregularity_level=family["prediction_profile"].get("expected_irregularity_level"),
                    expected_direction_blindness_relevant=family["prediction_profile"].get("expected_direction_blindness_relevant"),
                    observed_spacing_cv=None,
                    observed_spacing_ratio_mean=None,
                    observed_direction_blindness_flag=None,
                    extra={},
                )
            )
            continue

        for variant in family.get("analysis_variants", []):
            if not variant.get("enabled", True):
                continue

            variant_id = variant["variant_id"]
            marker_df, observed, irregularity = run_family_variant_diagnostics(family, variant, config, rng)

            for _, row in marker_df.iterrows():
                marker_rows.append(
                    MarkerScore(
                        family_id=family_id,
                        variant_id=variant_id,
                        spectral_type=spectral_type,
                        model_class=model_class,
                        marker_name=str(row["marker_name"]),
                        pairing_mode=variant["pairing_mode"],
                        n_pairs=int(len(marker_df)),
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

            match_status, match_note, hard_pass, soft_pass, fail_flag = evaluate_prediction_match(family, observed, irregularity)

            result_obj = FamilyPredictionResult(
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
                expected_relative_winner=family["prediction_profile"].get("expected_relative_winner"),
                expected_allowed_winners=",".join(family["prediction_profile"].get("expected_allowed_winners", [])),
                expected_delta_p2_role=family["prediction_profile"].get("expected_delta_p2_role"),
                expected_irregularity_level=family["prediction_profile"].get("expected_irregularity_level"),
                expected_direction_blindness_relevant=family["prediction_profile"].get("expected_direction_blindness_relevant"),
                observed_spacing_cv=irregularity.get("spacing_cv"),
                observed_spacing_ratio_mean=irregularity.get("spacing_ratio_mean"),
                observed_direction_blindness_flag=observed.get("direction_blindness_flag", 0),
                extra={"marker_df": observed.get("marker_df")},
            )

            family_prediction_rows.append(result_obj)
            irregularity_rows.append({
                "family_id": family_id,
                "variant_id": variant_id,
                "spectral_type": spectral_type,
                **irregularity,
            })
            implemented_result_rows.append(asdict(result_obj))

    marker_df = pd.DataFrame([asdict(x) for x in marker_rows])
    family_prediction_df = pd.DataFrame([asdict(x) for x in family_prediction_rows])
    irregularity_df = pd.DataFrame(irregularity_rows)
    missing_cases_df = pd.DataFrame(missing_case_rows)
    spectral_type_df = summarize_by_spectral_type(family_prediction_df)

    # control hardening
    implemented_df = pd.DataFrame(implemented_result_rows)

    type_a_ref_family = config["control_hardening"]["type_A_reference_family"]
    type_a_ref_variant = config["control_hardening"]["type_A_reference_variant"]
    type_a_ref_row = None
    if len(implemented_df):
        ref_sub = implemented_df[
            (implemented_df["family_id"] == type_a_ref_family) &
            (implemented_df["variant_id"] == type_a_ref_variant)
        ]
        if len(ref_sub):
            type_a_ref_row = ref_sub.iloc[0]

    # per-family hardening
    type_b_row = None
    type_d_row = None
    type_b_flags: Dict[str, Any] = {}

    for _, row in implemented_df.iterrows():
        if row["family_id"] in {"TB1_1D_BOX_WEAKLY_DEFORMED", "TD1_1D_BOX"}:
            flags = build_derived_flags_for_family(row, type_a_ref_row, config)

            if row["family_id"] == "TB1_1D_BOX_WEAKLY_DEFORMED":
                type_b_row = row
                type_b_flags = flags
            if row["family_id"] == "TD1_1D_BOX":
                type_d_row = row

    if type_b_row is not None:
        type_b_flags["behavior_matches_type_D_too_closely"] = build_behavior_matches_type_d_too_closely(
            type_b_flags, type_d_row, type_b_row
        )
        hard_status, hard_note = evaluate_type_b_decision(type_b_flags, type_b_row["dominant_marker"])
        control_hardening_rows.append({
            "family_id": type_b_row["family_id"],
            "variant_id": type_b_row["variant_id"],
            "spectral_type": type_b_row["spectral_type"],
            "hardening_status": hard_status,
            "hardening_note": hard_note,
            **type_b_flags,
        })

        family_prediction_df.loc[
            (family_prediction_df["family_id"] == type_b_row["family_id"]) &
            (family_prediction_df["variant_id"] == type_b_row["variant_id"]),
            ["prediction_match_status", "prediction_match_note"]
        ] = [hard_status, hard_note]

    if type_d_row is not None:
        type_d_flags = build_derived_flags_for_family(type_d_row, type_a_ref_row, config)
        hard_status, hard_note = evaluate_type_d_decision(type_d_flags, type_d_row["dominant_marker"])
        control_hardening_rows.append({
            "family_id": type_d_row["family_id"],
            "variant_id": type_d_row["variant_id"],
            "spectral_type": type_d_row["spectral_type"],
            "hardening_status": hard_status,
            "hardening_note": hard_note,
            **type_d_flags,
        })

        family_prediction_df.loc[
            (family_prediction_df["family_id"] == type_d_row["family_id"]) &
            (family_prediction_df["variant_id"] == type_d_row["variant_id"]),
            ["prediction_match_status", "prediction_match_note"]
        ] = [hard_status, hard_note]

    cross_type_status, cross_type_note = evaluate_cross_type(type_b_row, type_d_row, type_b_flags, config)
    control_hardening_rows.append({
        "family_id": "CROSS_TYPE",
        "variant_id": "TYPE_B_VS_TYPE_D",
        "spectral_type": "cross_type",
        "hardening_status": cross_type_status,
        "hardening_note": cross_type_note,
    })

    control_hardening_df = pd.DataFrame(control_hardening_rows)
    spectral_type_df = summarize_by_spectral_type(family_prediction_df)

    global_summary = build_global_prediction_status(
        family_prediction_df=family_prediction_df,
        control_hardening_df=control_hardening_df,
        cross_type_status=cross_type_status,
        families=families,
    )

    # outputs
    marker_df.to_csv(outdir / config["outputs"]["marker_summary_csv"], index=False)
    family_prediction_df.to_csv(outdir / config["outputs"]["family_prediction_summary_csv"], index=False)
    irregularity_df.to_csv(outdir / config["outputs"]["irregularity_summary_csv"], index=False)
    spectral_type_df.to_csv(outdir / config["outputs"]["spectral_type_summary_csv"], index=False)
    missing_cases_df.to_csv(outdir / config["outputs"]["missing_cases_summary_csv"], index=False)
    control_hardening_df.to_csv(outdir / config["outputs"]["control_hardening_summary_csv"], index=False)

    bootstrap_cols = [
        "family_id", "variant_id", "marker_name", "strength_mean",
        "strength_ci_low", "strength_ci_high", "bootstrap_win_fraction", "dominance_stable_flag",
    ]
    if len(marker_df):
        marker_df[bootstrap_cols].to_csv(outdir / config["outputs"]["bootstrap_summary_csv"], index=False)
    else:
        pd.DataFrame(columns=bootstrap_cols).to_csv(outdir / config["outputs"]["bootstrap_summary_csv"], index=False)

    write_json(global_summary, outdir / config["outputs"]["global_summary_json"])

    report_md = build_markdown_report(
        run_id=config["run"]["run_id"],
        family_prediction_df=family_prediction_df,
        spectral_type_df=spectral_type_df,
        control_hardening_df=control_hardening_df,
        global_summary=global_summary,
    )
    write_markdown(report_md, outdir / config["outputs"]["markdown_report"])

    source_notes = (
        "# Source Notes\n\n"
        "- M39x3 prediction-matrix hardening runner\n"
        "- Includes explicit Type-B and Type-D control hardening logic\n"
        "- Cross-type distinguishability is checked explicitly\n"
    )
    write_markdown(source_notes, outdir / config["outputs"]["source_notes_md"])

    print(f"[OK] Run completed: {config['run']['run_id']}")
    print(f"[OK] Output directory: {outdir}")


if __name__ == "__main__":
    main()