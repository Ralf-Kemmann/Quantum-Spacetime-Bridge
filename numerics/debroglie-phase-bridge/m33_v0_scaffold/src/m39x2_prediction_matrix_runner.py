#!/usr/bin/env python3
"""
m39x2_prediction_matrix_runner.py

M.3.9x.2 — Spektraltyp-Vorhersagen und Kontrollfälle

Ziel:
- Vorab definierte Spektraltyp-Vorhersagen gegen beobachtete Markerbefunde prüfen
- Mischbild-Lesart aus dem Bereich bloßer Nachdeutung herausziehen
- fehlende Kontrollfälle explizit offen reporten

Erwartete Konfiguration:
- configs/config_m39x2_prediction_matrix.yaml
- configs/m39x2_prediction_matrix_families.yaml
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
# YAML / IO
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

    if pairing_mode in {
        "degeneracy_safe_pairs",
        "unique_abs_pairs",
        "no_sign_mirror_pairs",
    }:
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
    mode_table = family["mode_table"]
    geom = mode_table["geometry"]
    a = float(geom["a"])
    b = float(geom["b"])
    d = float(geom["d"])

    k_values: List[float] = []
    for mode in mode_table["mode_indices"]:
        m, n, p = mode
        k = math.sqrt(
            (m * math.pi / a) ** 2
            + (n * math.pi / b) ** 2
            + (p * math.pi / d) ** 2
        )
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

    k_values: List[float] = []
    for mode in family["mode_table"]["mode_indices"]:
        m, n = mode
        key = (int(m), int(n))
        if key not in bessel_zero_lookup:
            raise ValueError(
                f"Missing Bessel zero lookup for membrane mode {key} in family {family['family_id']}."
            )
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
            raise NotImplementedError(
                f"Family {family['family_id']} has unsupported mode_table type: {mode_type}"
            )
    else:
        raise NotImplementedError(
            f"Family {family['family_id']} requires unsupported base spectrum construction."
        )

    for item in family.get("derived_spectra", []):
        src = item["from"]
        if src not in out:
            raise ValueError(
                f"Derived spectrum source '{src}' missing for family {family['family_id']}."
            )
        out[item["variable_name"]] = derive_spectrum(
            out[src],
            item["transform"],
            item.get("parameters", {}),
        )

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
# Ziel-/Scoringlogik
# ---------------------------------------------------------------------

def infer_pair_labels_from_existing_logic(
    family: Dict[str, Any],
    pairs: List[Tuple[int, int]],
    spec: Dict[str, np.ndarray],
) -> np.ndarray:
    """
    Konservativer Scaffold-Fallback.
    """
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
        s = rank_separation_score(marker_values[sample_idx], labels[sample_idx])
        scores.append(s)

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
    n = len(labels)
    idx = np.arange(n)
    wins = {name: 0 for name in names}

    for _ in range(n_bootstrap):
        sample_idx = rng.choice(idx, size=n, replace=True)
        scores = {
            name: rank_separation_score(vec[sample_idx], labels[sample_idx])
            for name, vec in marker_vectors.items()
        }
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
    ranks = np.arange(1, n + 1, dtype=float)
    return ranks / float(n)


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
        if a <= 0 or b <= 0:
            continue
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


# ---------------------------------------------------------------------
# Familien-Diagnostik
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
        pairs = apply_ring_pair_filters(
            spec_all["p"],
            pairs,
            degeneracy_policy,
            active_spectrum,
        )

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
    if family["family_id"] == "ER1_RING":
        has_delta_p = "delta_p" in set(df["marker_name"])
        has_delta_p2 = "delta_p2" in set(df["marker_name"])
        if variant["variant_id"] == "RING_SIGNED" and has_delta_p and has_delta_p2:
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
    }

    return df, observed, irregularity


# ---------------------------------------------------------------------
# Vorhersage-Prüfung
# ---------------------------------------------------------------------

def irregularity_matches_expected(observed_cv: float, expected_level: Optional[str]) -> bool:
    if expected_level is None:
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
    if expected_level == "open":
        return True

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
    exact_winner_ok = (
        True if expected_relative_winner in {None, "open"} else dominant_marker == expected_relative_winner
    )
    irregularity_ok = irregularity_matches_expected(observed_cv, expected_irregularity_level)
    direction_ok = (
        True if not expected_direction_blindness_relevant else bool(direction_blindness_flag)
    )

    # delta_p2 role checks nur grob-konservativ
    delta_p2_role_ok = True
    if expected_delta_p2_role == "not_necessarily_dominant":
        delta_p2_role_ok = True
    elif expected_delta_p2_role == "structure_support_expected":
        delta_p2_role_ok = dominant_marker in expected_allowed_winners
    elif expected_delta_p2_role in {"open_test_case", "critical_control_case"}:
        delta_p2_role_ok = True

    if winner_ok and exact_winner_ok and irregularity_ok and direction_ok and delta_p2_role_ok:
        return "supported", "Core prediction matched.", 1, 0, 0

    if winner_ok and delta_p2_role_ok:
        return "partially_supported", "Allowed winner matched, but not all side expectations fit.", 0, 1, 0

    if not winner_ok and (irregularity_ok or direction_ok):
        return "stressed", "Prediction under pressure: winner mismatch with partial side support.", 0, 0, 0

    return "failed", "Observed dominant marker contradicts prediction profile.", 0, 0, 1


# ---------------------------------------------------------------------
# Reporting / Summaries
# ---------------------------------------------------------------------

def build_markdown_report(
    run_id: str,
    family_prediction_df: pd.DataFrame,
    spectral_type_df: pd.DataFrame,
    missing_cases_df: pd.DataFrame,
    global_summary: Dict[str, Any],
) -> str:
    lines = []
    lines.append(f"# {run_id}")
    lines.append("")
    lines.append("## 1. Ziel und Methode")
    lines.append("Prediction-matrix run over predefined spectral types and control cases.")
    lines.append("")
    lines.append("## 2. Family-wise Vorhersage-Passung")
    lines.append(family_prediction_df.to_markdown(index=False) if len(family_prediction_df) else "_keine Familiendaten_")
    lines.append("")
    lines.append("## 3. Zusammenfassung nach Spektraltyp")
    lines.append(spectral_type_df.to_markdown(index=False) if len(spectral_type_df) else "_keine Typdaten_")
    lines.append("")
    lines.append("## 4. Fehlende Kontrollfälle")
    lines.append(missing_cases_df.to_markdown(index=False) if len(missing_cases_df) else "_keine fehlenden Fälle_")
    lines.append("")
    lines.append("## 5. Globaler Status")
    lines.append("```json")
    lines.append(json.dumps(global_summary, indent=2, ensure_ascii=False))
    lines.append("```")
    lines.append("")
    return "\n".join(lines)


def summarize_by_spectral_type(df: pd.DataFrame) -> pd.DataFrame:
    if len(df) == 0:
        return pd.DataFrame(columns=[
            "spectral_type",
            "n_families",
            "n_supported",
            "n_partially_supported",
            "n_open",
            "n_stressed",
            "n_failed",
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
    families: List[Dict[str, Any]],
) -> Dict[str, Any]:
    n_total = len(families)
    n_implemented = int(sum(1 for f in families if f.get("status", "implemented") == "implemented" and f.get("enabled", False)))

    n_supported = int((family_prediction_df["prediction_match_status"] == "supported").sum()) if len(family_prediction_df) else 0
    n_partially_supported = int((family_prediction_df["prediction_match_status"] == "partially_supported").sum()) if len(family_prediction_df) else 0
    n_open = int((family_prediction_df["prediction_match_status"] == "open").sum()) if len(family_prediction_df) else 0
    n_stressed = int((family_prediction_df["prediction_match_status"] == "stressed").sum()) if len(family_prediction_df) else 0
    n_failed = int((family_prediction_df["prediction_match_status"] == "failed").sum()) if len(family_prediction_df) else 0

    missing_type_B_flag = int(any(
        f.get("spectral_type") == "type_B_quadratic_nontrivial" and f.get("status") == "placeholder"
        for f in families
    ))
    missing_type_D_flag = int(any(
        f.get("spectral_type") == "type_D_regular_nonring" and f.get("status") == "placeholder"
        for f in families
    ))

    majority_ok = (n_supported + n_partially_supported) >= max(1, n_implemented - n_failed)

    ring_prediction_stressed = int(any(
        (row["family_id"] == "ER1_RING" and row["prediction_match_status"] in {"stressed", "failed"})
        for _, row in family_prediction_df.iterrows()
    )) if len(family_prediction_df) else 0

    type_C_prediction_stressed = int(any(
        (row["spectral_type"] == "type_C_multiindex_structure" and row["prediction_match_status"] in {"stressed", "failed"})
        for _, row in family_prediction_df.iterrows()
    )) if len(family_prediction_df) else 0

    if n_failed == 0 and majority_ok and not (ring_prediction_stressed or type_C_prediction_stressed) and not (missing_type_B_flag or missing_type_D_flag):
        global_status = "prediction_matrix_supported"
    elif n_failed == 0 and majority_ok:
        global_status = "prediction_matrix_partially_supported"
    elif n_failed > 0 or ring_prediction_stressed or type_C_prediction_stressed:
        global_status = "prediction_matrix_stressed"
    else:
        global_status = "prediction_matrix_failed"

    return {
        "run_id": "M39x2_prediction_matrix",
        "n_families_total": n_total,
        "n_families_implemented": n_implemented,
        "n_prediction_supported": n_supported,
        "n_prediction_partially_supported": n_partially_supported,
        "n_prediction_open": n_open,
        "n_prediction_stressed": n_stressed,
        "n_prediction_failed": n_failed,
        "missing_type_B_flag": missing_type_B_flag,
        "missing_type_D_flag": missing_type_D_flag,
        "ring_prediction_stressed": ring_prediction_stressed,
        "type_C_prediction_stressed": type_C_prediction_stressed,
        "global_prediction_status": global_status,
    }


# ---------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--config",
        default="configs/config_m39x2_prediction_matrix.yaml",
        help="Path to main config",
    )
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
            df, observed, irregularity = run_family_variant_diagnostics(family, variant, config, rng)

            for _, row in df.iterrows():
                marker_rows.append(
                    MarkerScore(
                        family_id=family_id,
                        variant_id=variant_id,
                        spectral_type=spectral_type,
                        model_class=model_class,
                        marker_name=str(row["marker_name"]),
                        pairing_mode=variant["pairing_mode"],
                        n_pairs=int(len(df)),
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

            match_status, match_note, hard_pass, soft_pass, fail_flag = evaluate_prediction_match(
                family, observed, irregularity
            )

            family_prediction_rows.append(
                FamilyPredictionResult(
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
                    extra={},
                )
            )

            irregularity_rows.append({
                "family_id": family_id,
                "variant_id": variant_id,
                "spectral_type": spectral_type,
                **irregularity,
            })

    marker_df = pd.DataFrame([asdict(x) for x in marker_rows])
    family_prediction_df = pd.DataFrame([asdict(x) for x in family_prediction_rows])
    irregularity_df = pd.DataFrame(irregularity_rows)
    missing_cases_df = pd.DataFrame(missing_case_rows)
    spectral_type_df = summarize_by_spectral_type(family_prediction_df)

    global_summary = build_global_prediction_status(family_prediction_df, families)

    # outputs
    marker_df.to_csv(outdir / config["outputs"]["marker_summary_csv"], index=False)
    family_prediction_df.to_csv(outdir / config["outputs"]["family_prediction_summary_csv"], index=False)
    irregularity_df.to_csv(outdir / config["outputs"]["irregularity_summary_csv"], index=False)
    spectral_type_df.to_csv(outdir / config["outputs"]["spectral_type_summary_csv"], index=False)
    missing_cases_df.to_csv(outdir / config["outputs"]["missing_cases_summary_csv"], index=False)

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

    report_md = build_markdown_report(
        run_id=config["run"]["run_id"],
        family_prediction_df=family_prediction_df,
        spectral_type_df=spectral_type_df,
        missing_cases_df=missing_cases_df,
        global_summary=global_summary,
    )
    write_markdown(report_md, outdir / config["outputs"]["markdown_report"])

    source_notes = (
        "# Source Notes\n\n"
        "- M39x2 prediction-matrix runner\n"
        "- Built to test predeclared spectral-type predictions against observed results\n"
        "- Missing Type-B and Type-D cases are reported explicitly as open\n"
    )
    write_markdown(source_notes, outdir / config["outputs"]["source_notes_md"])

    print(f"[OK] Run completed: {config['run']['run_id']}")
    print(f"[OK] Output directory: {outdir}")


if __name__ == "__main__":
    main()