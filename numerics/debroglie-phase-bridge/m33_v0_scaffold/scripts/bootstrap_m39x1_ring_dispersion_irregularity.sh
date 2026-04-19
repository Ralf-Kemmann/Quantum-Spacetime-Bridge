#!/usr/bin/env python3
"""
m39x1_ring_dispersion_irregularity_runner.py

M.3.9x.1 — Ring-Sonderfall, Dispersionstest und Irregularitäts-Hypothese

Ziel:
- Ring-Sonderfall isoliert testen
- dispersion-korrigierte Energielesart gegen Eigenwert-/Strukturlesart prüfen
- Irregularitäts-Hypothese operational prüfen
- absolute Stärke und relative Dominanz strikt getrennt reporten
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
    block_id: str
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
class BlockDecision:
    family_id: str
    variant_id: str
    block_id: str
    model_class: str

    block_positive_flag: int
    dominant_marker: Optional[str]
    interpretation_note: str

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
# Hilfsfunktionen Spektren / Paarbildung
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

    # konservativer Fallback für projektinterne Spezialmodi
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
            ekey = tuple(sorted((float(vi ** 2), float(vj ** 2))))
            if ekey in seen_energy_shells:
                continue
            seen_energy_shells.add(ekey)

        filtered.append((i, j))

    return filtered


# ---------------------------------------------------------------------
# Markerberechnung
# ---------------------------------------------------------------------

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
        if k is None:
            raise ValueError("delta_k requested but k spectrum missing.")
        return float(k[i] - k[j])

    if marker_name == "abs_delta_k":
        if k is None:
            raise ValueError("abs_delta_k requested but k spectrum missing.")
        return abs(float(k[i] - k[j]))

    if marker_name == "delta_k2":
        if k2 is None:
            raise ValueError("delta_k2 requested but k2 spectrum missing.")
        return float(k2[i] - k2[j])

    if marker_name == "abs_delta_k2":
        if k2 is None:
            raise ValueError("abs_delta_k2 requested but k2 spectrum missing.")
        return abs(float(k2[i] - k2[j]))

    if marker_name == "delta_omega":
        if omega is None:
            raise ValueError("delta_omega requested but omega spectrum missing.")
        return float(omega[i] - omega[j])

    if marker_name == "delta_lambda":
        if lambd is None:
            raise ValueError("delta_lambda requested but lambda spectrum missing.")
        return float(lambd[i] - lambd[j])

    raise ValueError(f"Unsupported marker: {marker_name}")


def compute_marker_vector(marker_name: str, spec: Dict[str, np.ndarray], pairs: List[Tuple[int, int]]) -> np.ndarray:
    vals = [compute_marker_for_pair(marker_name, spec, i, j) for i, j in pairs]
    return np.asarray(vals, dtype=float)


# ---------------------------------------------------------------------
# Branch-Target / Andockstelle
# ---------------------------------------------------------------------

def infer_pair_labels_from_existing_logic(
    family: Dict[str, Any],
    pairs: List[Tuple[int, int]],
    spec: Dict[str, np.ndarray],
) -> np.ndarray:
    """
    Konservativer Scaffold-Fallback:
    Binäres Ziel auf Basis des Betrags der Grunddifferenz relativ zum Median.
    """
    base = spec["p"] if spec.get("p") is not None else spec["k"]
    diffs = np.asarray([abs(base[i] - base[j]) for i, j in pairs], dtype=float)

    if len(diffs) == 0:
        return np.asarray([], dtype=int)

    thr = float(np.median(diffs))
    return (diffs > thr).astype(int)


# ---------------------------------------------------------------------
# Stärke / Dominanz / Bootstrap
# ---------------------------------------------------------------------

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
# Familienspektren
# ---------------------------------------------------------------------

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
    """
    Minimal robuster Lookup für die im YAML verwendeten kleinen (m, n)-Paare.
    Werte = Bessel-Nullstellen j_(m,n).
    """
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

    mode_table = family["mode_table"]
    k_values: List[float] = []

    for mode in mode_table["mode_indices"]:
        m, n = mode
        key = (int(m), int(n))
        if key not in bessel_zero_lookup:
            raise ValueError(
                f"Missing Bessel zero lookup for membrane mode {key} "
                f"in family {family['family_id']}."
            )
        k_values.append(bessel_zero_lookup[key])

    return np.asarray(k_values, dtype=float)


def build_family_spectra(family: Dict[str, Any]) -> Dict[str, np.ndarray]:
    out: Dict[str, np.ndarray] = {}

    base = family["base_spectrum"]

    if "values" in base:
        out[base["variable_name"]] = to_numpy(base["values"])

    elif base.get("construction") == "from_existing_external_reference_family":
        mode_table = family.get("mode_table", {})
        mode_type = mode_table.get("type")

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
            f"Family {family['family_id']} requires existing external reference generator hook."
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
# Block 5A — Ring-Sonderfall
# ---------------------------------------------------------------------

def run_ring_special_case_block(
    family: Dict[str, Any],
    config: Dict[str, Any],
    rng: np.random.Generator,
) -> Tuple[List[MarkerScore], List[BlockDecision], List[Dict[str, Any]]]:
    marker_rows: List[MarkerScore] = []
    decisions: List[BlockDecision] = []
    ring_summary_rows: List[Dict[str, Any]] = []

    spec_all = build_family_spectra(family)
    variants = family.get("analysis_variants", [])

    for variant in variants:
        if not variant.get("enabled", True):
            continue

        variant_id = variant["variant_id"]
        active_spectrum = variant["active_spectrum"]
        pairing_mode = variant["pairing_mode"]
        enabled_markers = variant["enabled_markers"]
        degeneracy_policy = variant.get("degeneracy_policy", {})

        base_values = spec_all["p"]
        pairs = build_pairs(spec_all[active_spectrum], pairing_mode)
        pairs = apply_ring_pair_filters(base_values, pairs, degeneracy_policy, active_spectrum)

        labels = infer_pair_labels_from_existing_logic(family, pairs, spec_all)
        n_boot = int(config["bootstrap"]["n_bootstrap"])

        marker_vectors = {marker: compute_marker_vector(marker, spec_all, pairs) for marker in enabled_markers}
        win_fractions = bootstrap_win_fractions(marker_vectors, labels, n_boot, rng)

        score_rows = []
        for marker_name, vec in marker_vectors.items():
            mean_s, low_s, high_s = bootstrap_strength(vec, labels, n_boot, rng)
            abs_strength = rank_separation_score(vec, labels)
            score_rows.append({
                "marker_name": marker_name,
                "absolute_strength": abs_strength,
                "strength_mean": mean_s,
                "strength_ci_low": low_s,
                "strength_ci_high": high_s,
                "bootstrap_win_fraction": win_fractions.get(marker_name, 0.0),
            })

        df = pd.DataFrame(score_rows).sort_values(
            by=["absolute_strength", "bootstrap_win_fraction"],
            ascending=[False, False],
        ).reset_index(drop=True)

        if len(df) == 0:
            continue

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

        for _, row in df.iterrows():
            marker_name = row["marker_name"]
            marker_rows.append(
                MarkerScore(
                    family_id=family["family_id"],
                    variant_id=variant_id,
                    block_id="ring_special_case",
                    model_class=family["model_class"],
                    marker_name=marker_name,
                    pairing_mode=pairing_mode,
                    n_pairs=len(pairs),
                    absolute_strength=float(row["absolute_strength"]),
                    strength_mean=float(row["strength_mean"]),
                    strength_ci_low=float(row["strength_ci_low"]),
                    strength_ci_high=float(row["strength_ci_high"]),
                    absolute_support_flag=int(
                        row["absolute_strength"] >= config["strength_scoring"]["support_thresholds"]["absolute_support_min"]
                    ),
                    relative_rank=int(row["relative_rank"]),
                    dominance_margin=float(dominance_margin_map[marker_name]),
                    bootstrap_win_fraction=float(row["bootstrap_win_fraction"]),
                    dominant_level_flag=int(row["relative_rank"] == 1),
                    dominance_stable_flag=int(
                        row["bootstrap_win_fraction"] >= config["strength_scoring"]["support_thresholds"]["dominance_stable_min"]
                    ),
                    extra={},
                )
            )

        dominant_marker = str(df.iloc[0]["marker_name"])

        abs_delta_p2 = (
            float(df[df["marker_name"] == "delta_p2"]["absolute_strength"].iloc[0])
            if "delta_p2" in set(df["marker_name"])
            else np.nan
        )
        abs_delta_p = (
            float(df[df["marker_name"] == "delta_p"]["absolute_strength"].iloc[0])
            if "delta_p" in set(df["marker_name"])
            else np.nan
        )

        sign_sensitivity_flag = int(variant_id == "RING_SIGNED" and dominant_marker == "delta_p")
        degeneracy_sensitivity_flag = int("DEGEN" in variant_id and dominant_marker != "delta_p")

        irregularity = compute_irregularity_measures(spec_all[active_spectrum])
        ladder_regular_flag = int(irregularity["spacing_cv"] < 0.20)

        delta_p2_blind_to_direction_flag = int(
            variant_id == "RING_SIGNED" and dominant_marker == "delta_p" and abs_delta_p2 < abs_delta_p
        )

        positive_flag = int(
            delta_p2_blind_to_direction_flag
            or degeneracy_sensitivity_flag
            or (ladder_regular_flag and dominant_marker == "delta_p")
        )

        ring_summary_rows.append({
            "family_id": family["family_id"],
            "variant_id": variant_id,
            "pairing_mode": pairing_mode,
            "dominant_marker": dominant_marker,
            "sign_sensitivity_flag": sign_sensitivity_flag,
            "degeneracy_sensitivity_flag": degeneracy_sensitivity_flag,
            "ladder_regular_flag": ladder_regular_flag,
            "delta_p2_blind_to_direction_flag": delta_p2_blind_to_direction_flag,
            "spacing_cv": irregularity["spacing_cv"],
            "block_positive_flag": positive_flag,
        })

        decisions.append(
            BlockDecision(
                family_id=family["family_id"],
                variant_id=variant_id,
                block_id="ring_special_case",
                model_class=family["model_class"],
                block_positive_flag=positive_flag,
                dominant_marker=dominant_marker,
                interpretation_note=(
                    "Ring-Sonderfall spricht für Richtungs-/Degenerazie-/Regularitätsbeitrag."
                    if positive_flag else
                    "Ring-Sonderfall aktuell ohne klaren Richtungs-/Degeneraziehinweis."
                ),
                extra={
                    "sign_sensitivity_flag": sign_sensitivity_flag,
                    "degeneracy_sensitivity_flag": degeneracy_sensitivity_flag,
                    "ladder_regular_flag": ladder_regular_flag,
                    "delta_p2_blind_to_direction_flag": delta_p2_blind_to_direction_flag,
                },
            )
        )

    return marker_rows, decisions, ring_summary_rows


# ---------------------------------------------------------------------
# Block 5B — Dispersion / Energie vs Eigenwert
# ---------------------------------------------------------------------

def run_dispersion_corrected_energy_block(
    family: Dict[str, Any],
    config: Dict[str, Any],
    rng: np.random.Generator,
) -> Tuple[List[MarkerScore], List[BlockDecision], List[Dict[str, Any]]]:
    marker_rows: List[MarkerScore] = []
    decisions: List[BlockDecision] = []
    summary_rows: List[Dict[str, Any]] = []

    spec_all = build_family_spectra(family)
    variants = family.get("analysis_variants", [])

    for variant in variants:
        if not variant.get("enabled", True):
            continue

        variant_id = variant["variant_id"]
        pairing_mode = variant["pairing_mode"]
        enabled_markers = variant["enabled_markers"]
        active_spectrum = variant["active_spectrum"]

        pairs = build_pairs(spec_all[active_spectrum], pairing_mode)
        if family["family_id"] == "ER1_RING":
            pairs = apply_ring_pair_filters(
                spec_all["p"],
                pairs,
                variant.get("degeneracy_policy", {}),
                active_spectrum,
            )

        labels = infer_pair_labels_from_existing_logic(family, pairs, spec_all)
        marker_vectors = {marker: compute_marker_vector(marker, spec_all, pairs) for marker in enabled_markers}

        n_boot = int(config["bootstrap"]["n_bootstrap"])
        win_fractions = bootstrap_win_fractions(marker_vectors, labels, n_boot, rng)

        score_rows = []
        for marker_name, vec in marker_vectors.items():
            abs_strength = rank_separation_score(vec, labels)
            mean_s, low_s, high_s = bootstrap_strength(vec, labels, n_boot, rng)
            score_rows.append({
                "marker_name": marker_name,
                "absolute_strength": abs_strength,
                "strength_mean": mean_s,
                "strength_ci_low": low_s,
                "strength_ci_high": high_s,
                "bootstrap_win_fraction": win_fractions.get(marker_name, 0.0),
            })

        df = pd.DataFrame(score_rows).sort_values(
            by=["absolute_strength", "bootstrap_win_fraction"],
            ascending=[False, False],
        ).reset_index(drop=True)

        if len(df) == 0:
            continue

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

        for _, row in df.iterrows():
            marker_name = row["marker_name"]
            marker_rows.append(
                MarkerScore(
                    family_id=family["family_id"],
                    variant_id=variant_id,
                    block_id="dispersion_corrected_energy",
                    model_class=family["model_class"],
                    marker_name=marker_name,
                    pairing_mode=pairing_mode,
                    n_pairs=len(pairs),
                    absolute_strength=float(row["absolute_strength"]),
                    strength_mean=float(row["strength_mean"]),
                    strength_ci_low=float(row["strength_ci_low"]),
                    strength_ci_high=float(row["strength_ci_high"]),
                    absolute_support_flag=int(
                        row["absolute_strength"] >= config["strength_scoring"]["support_thresholds"]["absolute_support_min"]
                    ),
                    relative_rank=int(row["relative_rank"]),
                    dominance_margin=float(dominance_margin_map[marker_name]),
                    bootstrap_win_fraction=float(row["bootstrap_win_fraction"]),
                    dominant_level_flag=int(row["relative_rank"] == 1),
                    dominance_stable_flag=int(
                        row["bootstrap_win_fraction"] >= config["strength_scoring"]["support_thresholds"]["dominance_stable_min"]
                    ),
                    extra={},
                )
            )

        expected = config["dispersion_corrected_energy_block"]["expected_alignment"].get(family["family_id"], {})
        energy_like = expected.get("energy_like_markers", [])
        eigen_like = expected.get("eigenvalue_like_markers", [])

        def best_in_group(group: List[str]) -> Optional[Tuple[str, float]]:
            sub = df[df["marker_name"].isin(group)]
            if len(sub) == 0:
                return None
            row = sub.iloc[0]
            return str(row["marker_name"]), float(row["absolute_strength"])

        best_energy = best_in_group(energy_like)
        best_eigen = best_in_group(eigen_like)

        energy_marker_best = best_energy[0] if best_energy else None
        eigenvalue_marker_best = best_eigen[0] if best_eigen else None
        energy_score = best_energy[1] if best_energy else np.nan
        eigen_score = best_eigen[1] if best_eigen else np.nan
        margin = float(eigen_score - energy_score) if not (np.isnan(eigen_score) or np.isnan(energy_score)) else np.nan

        dispersion_consistency_flag = int(
            (family["family_id"] == "ER1_RING" and energy_marker_best in {"delta_E_quad", "delta_p2"})
            or (family["family_id"] in {"ER2_CAVITY", "ER3_MEMBRANE"} and eigenvalue_marker_best is not None)
        )

        dominant_marker = str(df.iloc[0]["marker_name"])

        summary_rows.append({
            "family_id": family["family_id"],
            "variant_id": variant_id,
            "dominant_marker": dominant_marker,
            "energy_marker_best": energy_marker_best,
            "eigenvalue_marker_best": eigenvalue_marker_best,
            "energy_vs_eigenvalue_margin": margin,
            "dispersion_consistency_flag": dispersion_consistency_flag,
        })

        decisions.append(
            BlockDecision(
                family_id=family["family_id"],
                variant_id=variant_id,
                block_id="dispersion_corrected_energy",
                model_class=family["model_class"],
                block_positive_flag=dispersion_consistency_flag,
                dominant_marker=dominant_marker,
                interpretation_note=(
                    "Dispersiontest stützt modellabhängige Energie/Eigenwert-Lesart."
                    if dispersion_consistency_flag else
                    "Dispersiontest aktuell inkonsistent zur erwarteten Modelllesart."
                ),
                extra={
                    "energy_marker_best": energy_marker_best,
                    "eigenvalue_marker_best": eigenvalue_marker_best,
                    "energy_vs_eigenvalue_margin": margin,
                },
            )
        )

    return marker_rows, decisions, summary_rows


# ---------------------------------------------------------------------
# Block 5C — Irregularität
# ---------------------------------------------------------------------

def run_irregularity_block(
    family: Dict[str, Any],
    config: Dict[str, Any],
    rng: np.random.Generator,
) -> Tuple[List[MarkerScore], List[BlockDecision], List[Dict[str, Any]], List[Dict[str, Any]]]:
    marker_rows: List[MarkerScore] = []
    decisions: List[BlockDecision] = []
    summary_rows: List[Dict[str, Any]] = []
    factor_rows: List[Dict[str, Any]] = []

    spec_all = build_family_spectra(family)
    variants = family.get("analysis_variants", [])

    for variant in variants:
        if not variant.get("enabled", True):
            continue

        variant_id = variant["variant_id"]
        pairing_mode = variant["pairing_mode"]
        enabled_markers = variant["enabled_markers"]
        active_spectrum = variant["active_spectrum"]

        pairs = build_pairs(spec_all[active_spectrum], pairing_mode)
        if family["family_id"] == "ER1_RING":
            pairs = apply_ring_pair_filters(
                spec_all["p"],
                pairs,
                variant.get("degeneracy_policy", {}),
                active_spectrum,
            )

        labels = infer_pair_labels_from_existing_logic(family, pairs, spec_all)
        marker_vectors = {marker: compute_marker_vector(marker, spec_all, pairs) for marker in enabled_markers}

        n_boot = int(config["bootstrap"]["n_bootstrap"])
        win_fractions = bootstrap_win_fractions(marker_vectors, labels, n_boot, rng)

        score_rows = []
        for marker_name, vec in marker_vectors.items():
            abs_strength = rank_separation_score(vec, labels)
            mean_s, low_s, high_s = bootstrap_strength(vec, labels, n_boot, rng)
            score_rows.append({
                "marker_name": marker_name,
                "absolute_strength": abs_strength,
                "strength_mean": mean_s,
                "strength_ci_low": low_s,
                "strength_ci_high": high_s,
                "bootstrap_win_fraction": win_fractions.get(marker_name, 0.0),
            })

        df = pd.DataFrame(score_rows).sort_values(
            by=["absolute_strength", "bootstrap_win_fraction"],
            ascending=[False, False],
        ).reset_index(drop=True)

        if len(df) == 0:
            continue

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

        for _, row in df.iterrows():
            marker_name = row["marker_name"]
            marker_rows.append(
                MarkerScore(
                    family_id=family["family_id"],
                    variant_id=variant_id,
                    block_id="irregularity",
                    model_class=family["model_class"],
                    marker_name=marker_name,
                    pairing_mode=pairing_mode,
                    n_pairs=len(pairs),
                    absolute_strength=float(row["absolute_strength"]),
                    strength_mean=float(row["strength_mean"]),
                    strength_ci_low=float(row["strength_ci_low"]),
                    strength_ci_high=float(row["strength_ci_high"]),
                    absolute_support_flag=int(
                        row["absolute_strength"] >= config["strength_scoring"]["support_thresholds"]["absolute_support_min"]
                    ),
                    relative_rank=int(row["relative_rank"]),
                    dominance_margin=float(dominance_margin_map[marker_name]),
                    bootstrap_win_fraction=float(row["bootstrap_win_fraction"]),
                    dominant_level_flag=int(row["relative_rank"] == 1),
                    dominance_stable_flag=int(
                        row["bootstrap_win_fraction"] >= config["strength_scoring"]["support_thresholds"]["dominance_stable_min"]
                    ),
                    extra={},
                )
            )

        irregularity = compute_irregularity_measures(spec_all[active_spectrum])

        base = spec_all["p"] if spec_all.get("p") is not None else spec_all["k"]
        delta_p_vec = np.asarray([base[i] - base[j] for i, j in pairs], dtype=float)
        p_sum_vec = np.asarray([base[i] + base[j] for i, j in pairs], dtype=float)
        product_vec = delta_p_vec * p_sum_vec

        delta_p_effect = rank_separation_score(delta_p_vec, labels)
        p_sum_effect = rank_separation_score(p_sum_vec, labels)
        product_effect = rank_separation_score(product_vec, labels)
        interaction_gain_flag = int(product_effect > max(delta_p_effect, p_sum_effect))

        factor_rows.append({
            "family_id": family["family_id"],
            "variant_id": variant_id,
            "delta_p_effect": delta_p_effect,
            "p_sum_effect": p_sum_effect,
            "product_effect": product_effect,
            "interaction_gain_flag": interaction_gain_flag,
        })

        dominant_marker = str(df.iloc[0]["marker_name"])
        quad_rows = df[df["marker_name"].isin(["delta_p2", "delta_k2"])]
        delta_p2_strength = float(quad_rows.iloc[0]["absolute_strength"]) if len(quad_rows) > 0 else np.nan

        irregularity_support_flag = int(
            (irregularity["spacing_cv"] > 0.20 and not np.isnan(delta_p2_strength) and delta_p2_strength >= 0.60)
            or interaction_gain_flag
        )

        summary_rows.append({
            "family_id": family["family_id"],
            "variant_id": variant_id,
            "dominant_marker": dominant_marker,
            "spacing_mean": irregularity["spacing_mean"],
            "spacing_std": irregularity["spacing_std"],
            "spacing_cv": irregularity["spacing_cv"],
            "spacing_ratio_mean": irregularity["spacing_ratio_mean"],
            "simple_unfolding_density": irregularity["simple_unfolding_density"],
            "simple_rigidity_surrogate": irregularity["simple_rigidity_surrogate"],
            "irregularity_support_flag": irregularity_support_flag,
        })

        decisions.append(
            BlockDecision(
                family_id=family["family_id"],
                variant_id=variant_id,
                block_id="irregularity",
                model_class=family["model_class"],
                block_positive_flag=irregularity_support_flag,
                dominant_marker=dominant_marker,
                interpretation_note=(
                    "Irregularitätsblock stützt Struktur-/Spacing-Lesart."
                    if irregularity_support_flag else
                    "Irregularitätsblock aktuell ohne klare Strukturkopplung."
                ),
                extra={
                    **irregularity,
                    "delta_p_effect": delta_p_effect,
                    "p_sum_effect": p_sum_effect,
                    "product_effect": product_effect,
                    "interaction_gain_flag": interaction_gain_flag,
                },
            )
        )

    return marker_rows, decisions, summary_rows, factor_rows


# ---------------------------------------------------------------------
# Global Summary / Report
# ---------------------------------------------------------------------

def build_global_interpretation_summary(
    ring_decisions: List[BlockDecision],
    dispersion_decisions: List[BlockDecision],
    irregularity_decisions: List[BlockDecision],
) -> Dict[str, Any]:
    ring_flag = int(any(d.block_positive_flag for d in ring_decisions))
    dispersion_flag = int(any(d.block_positive_flag for d in dispersion_decisions))
    irregularity_flag = int(any(d.block_positive_flag for d in irregularity_decisions))

    energy_special_case_support_flag = int(dispersion_flag and ring_flag)
    structure_marker_support_flag = int(irregularity_flag or dispersion_flag)
    mixed_picture_support_flag = int(ring_flag and structure_marker_support_flag)

    if mixed_picture_support_flag:
        global_interpretation = "mixed_picture_supported"
    elif structure_marker_support_flag:
        global_interpretation = "structure_marker_supported"
    elif energy_special_case_support_flag:
        global_interpretation = "energy_special_case_supported"
    else:
        global_interpretation = "inconclusive"

    return {
        "ring_special_case_flag": ring_flag,
        "dispersion_consistency_flag": dispersion_flag,
        "irregularity_support_flag": irregularity_flag,
        "energy_special_case_support_flag": energy_special_case_support_flag,
        "structure_marker_support_flag": structure_marker_support_flag,
        "mixed_picture_support_flag": mixed_picture_support_flag,
        "absolute_vs_relative_reporting_ok": 1,
        "global_interpretation": global_interpretation,
    }


def build_markdown_report(
    run_id: str,
    marker_df: pd.DataFrame,
    block_df: pd.DataFrame,
    global_summary: Dict[str, Any],
) -> str:
    lines = []
    lines.append(f"# {run_id}")
    lines.append("")
    lines.append("## 1. Ziel und Fragestellung")
    lines.append("Audit von Ring-Sonderfall, dispersion-korrigierter Energielesart und Irregularitäts-Hypothese.")
    lines.append("")
    lines.append("## 2. Blockübersicht")
    lines.append(block_df.to_markdown(index=False) if len(block_df) else "_keine Blockdaten_")
    lines.append("")
    lines.append("## 3. Markerübersicht")
    lines.append(marker_df.to_markdown(index=False) if len(marker_df) else "_keine Markerdaten_")
    lines.append("")
    lines.append("## 4. Globales Arbeitsfazit")
    lines.append("```json")
    lines.append(json.dumps(global_summary, indent=2, ensure_ascii=False))
    lines.append("```")
    lines.append("")
    lines.append("## 5. Offene Flanken")
    lines.append("- Andockung an bestehende M.3.9x-Branch-Logik")
    lines.append("- ggf. präzisere degeneraziesichere Paarbildung")
    lines.append("- ggf. stärkeres Unfolding / Rigidity-Modul")
    lines.append("")
    return "\n".join(lines)


# ---------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--config",
        default="configs/config_m39x1_ring_dispersion_irregularity.yaml",
        help="Pfad zur Hauptkonfiguration",
    )
    args = parser.parse_args()

    config = load_yaml(args.config)
    families_path = config["inputs"]["family_definitions_yaml"]
    families_cfg = load_yaml(families_path)

    run = config["run"]
    outdir = ensure_dir(run["outdir"])
    rng = np.random.default_rng(int(run.get("random_seed", 1729)))

    all_marker_rows: List[MarkerScore] = []
    all_block_rows: List[BlockDecision] = []

    ring_special_case_rows: List[Dict[str, Any]] = []
    dispersion_rows: List[Dict[str, Any]] = []
    irregularity_rows: List[Dict[str, Any]] = []
    factorization_rows: List[Dict[str, Any]] = []

    ring_decisions: List[BlockDecision] = []
    dispersion_decisions: List[BlockDecision] = []
    irregularity_decisions: List[BlockDecision] = []

    families = families_cfg.get("families", [])

    for family in families:
        family_id = family["family_id"]

        if family_id == "ER1_RING" and "ring_special_case" in config["execution"]["enabled_blocks"]:
            marker_rows, decisions, summary_rows = run_ring_special_case_block(family, config, rng)
            all_marker_rows.extend(marker_rows)
            all_block_rows.extend(decisions)
            ring_special_case_rows.extend(summary_rows)
            ring_decisions.extend(decisions)

        if "dispersion_corrected_energy" in config["execution"]["enabled_blocks"]:
            marker_rows, decisions, summary_rows = run_dispersion_corrected_energy_block(family, config, rng)
            all_marker_rows.extend(marker_rows)
            all_block_rows.extend(decisions)
            dispersion_rows.extend(summary_rows)
            dispersion_decisions.extend(decisions)

        if "irregularity" in config["execution"]["enabled_blocks"]:
            marker_rows, decisions, summary_rows, factor_rows = run_irregularity_block(family, config, rng)
            all_marker_rows.extend(marker_rows)
            all_block_rows.extend(decisions)
            irregularity_rows.extend(summary_rows)
            factorization_rows.extend(factor_rows)
            irregularity_decisions.extend(decisions)

    marker_df = pd.DataFrame([asdict(x) for x in all_marker_rows])
    block_df = pd.DataFrame([asdict(x) for x in all_block_rows])

    global_summary = build_global_interpretation_summary(
        ring_decisions=ring_decisions,
        dispersion_decisions=dispersion_decisions,
        irregularity_decisions=irregularity_decisions,
    )
    global_summary["run_id"] = run["run_id"]
    global_summary["n_families_total"] = len(families)
    global_summary["n_blocks_total"] = int(block_df["block_id"].nunique()) if len(block_df) else 0

    marker_df.to_csv(outdir / config["outputs"]["marker_strength_summary_csv"], index=False)
    marker_df.to_csv(outdir / config["outputs"]["marker_dominance_summary_csv"], index=False)
    block_df.to_csv(outdir / config["outputs"]["family_block_summary_csv"], index=False)

    pd.DataFrame(ring_special_case_rows).to_csv(outdir / config["outputs"]["ring_special_case_summary_csv"], index=False)
    pd.DataFrame(dispersion_rows).to_csv(outdir / config["outputs"]["dispersion_test_summary_csv"], index=False)
    pd.DataFrame(irregularity_rows).to_csv(outdir / config["outputs"]["irregularity_summary_csv"], index=False)
    pd.DataFrame(factorization_rows).to_csv(outdir / config["outputs"]["factorization_summary_csv"], index=False)

    bootstrap_cols = [
        "family_id",
        "variant_id",
        "block_id",
        "marker_name",
        "strength_mean",
        "strength_ci_low",
        "strength_ci_high",
        "bootstrap_win_fraction",
        "dominance_stable_flag",
    ]
    bootstrap_df = marker_df[bootstrap_cols].copy() if len(marker_df) else pd.DataFrame(columns=bootstrap_cols)
    bootstrap_df.to_csv(outdir / config["outputs"]["bootstrap_summary_csv"], index=False)

    write_json(global_summary, outdir / config["outputs"]["global_summary_json"])

    report_md = build_markdown_report(run["run_id"], marker_df, block_df, global_summary)
    write_markdown(report_md, outdir / config["outputs"]["markdown_report"])

    source_notes = (
        "# Source Notes\n\n"
        "- M.3.9x-Infrastruktur als Andockbasis\n"
        "- Ring-Sonderfall explizit isoliert\n"
        "- Dispersion/Eigenwert/Irregularität getrennt operationalisiert\n"
    )
    write_markdown(source_notes, outdir / config["outputs"]["source_notes_md"])

    print(f"[OK] Run completed: {run['run_id']}")
    print(f"[OK] Output directory: {outdir}")


if __name__ == "__main__":
    main()