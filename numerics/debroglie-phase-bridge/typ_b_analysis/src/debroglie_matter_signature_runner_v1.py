#!/usr/bin/env python3
"""
debroglie_matter_signature_runner_v1.py

Minimal exploratory runner for materialspecific de Broglie signatures of atomic species
under defined thermodynamic conditions.

This runner is intentionally conservative. It does not claim to model spacetime or
prove a resonance theory. It computes simple, transparent surrogate quantities and
compares species responses relative to a tau grid.
"""

from __future__ import annotations

import argparse
import csv
import json
import math
import os
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

try:
    import yaml  # type: ignore
except Exception as exc:  # pragma: no cover
    raise SystemExit(
        "PyYAML is required for this runner. Install it in your environment first."
    ) from exc


# -----------------------------
# Physical constants (SI)
# -----------------------------
PLANCK_CONSTANT = 6.62607015e-34         # J*s
HBAR = PLANCK_CONSTANT / (2.0 * math.pi)
BOLTZMANN_CONSTANT = 1.380649e-23        # J/K
AVOGADRO_CONSTANT = 6.02214076e23        # 1/mol
ATOMIC_MASS_UNIT = 1.66053906660e-27     # kg
GAS_CONSTANT = 8.31446261815324          # J/(mol*K)


# Atomic masses in u. Intentional minimal set for the current config series.
ATOMIC_MASS_U: Dict[str, float] = {
    "hydrogen": 1.00784,
    "carbon": 12.011,
    "nitrogen": 14.007,
    "sodium": 22.98976928,
    "phosphorus": 30.973761998,
    "sulfur": 32.06,
}


@dataclass
class Conditions:
    temperature_C: float
    pressure_mbar: float
    volume_m3: float

    @property
    def temperature_K(self) -> float:
        return self.temperature_C + 273.15

    @property
    def pressure_Pa(self) -> float:
        return self.pressure_mbar * 100.0


@dataclass
class ModelAssumptions:
    species_mode: str
    gas_model: str
    velocity_model: str
    frequency_mode: str
    density_mode: str


@dataclass
class SpeciesBaseResult:
    species: str
    symbol: str
    mass_u: float
    mass_kg: float
    temperature_K: float
    pressure_Pa: float
    volume_m3: float
    number_density_m3: float
    particle_count: float
    velocity_m_s: float
    momentum_kg_m_s: float
    lambda_db_m: float
    k_m_inv: float
    omega_rad_s: Optional[float]
    frequency_hz: Optional[float]
    energy_j: float


@dataclass
class SpeciesSurrogates:
    length_scale_score: float
    energy_score: float
    occupancy_score: float
    signature_score: float


@dataclass
class TauResponse:
    tau: float
    tau_alignment_score: float
    tau_response_score: float
    tau_window_label: str


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Compute de Broglie matter signature surrogates for atomic species."
    )
    parser.add_argument("--config", required=True, help="Path to YAML config.")
    parser.add_argument("--output-dir", help="Override output directory.")
    parser.add_argument("--run-id", help="Override run_id from config.")
    parser.add_argument("--species", nargs="*", help="Override species list.")
    parser.add_argument("--temperature", type=float, help="Override temperature in °C.")
    parser.add_argument("--pressure", type=float, help="Override pressure in mbar.")
    parser.add_argument("--volume", type=float, help="Override volume in m^3.")
    parser.add_argument(
        "--tau-grid",
        help="Comma-separated floats, e.g. 0.001,0.01,0.1,1.0",
    )
    parser.add_argument("--dry-run", action="store_true", help="Parse and validate only.")
    return parser.parse_args()


def load_config(path: Path) -> Dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        data = yaml.safe_load(handle)
    if not isinstance(data, dict):
        raise ValueError("Config root must be a mapping.")
    return data


def apply_overrides(config: Dict[str, Any], args: argparse.Namespace) -> Dict[str, Any]:
    cfg = json.loads(json.dumps(config))  # deep copy via JSON-safe structure

    if args.run_id:
        cfg["run_id"] = args.run_id

    if args.species:
        cfg["species_list"] = list(args.species)

    conditions = cfg.setdefault("conditions", {})
    if args.temperature is not None:
        conditions["temperature_C"] = args.temperature
    if args.pressure is not None:
        conditions["pressure_mbar"] = args.pressure
    if args.volume is not None:
        conditions["volume_m3"] = args.volume

    if args.tau_grid:
        tau_values = [float(item.strip()) for item in args.tau_grid.split(",") if item.strip()]
        cfg["tau_grid"] = tau_values

    if args.output_dir:
        output = cfg.setdefault("output", {})
        output["base_dir"] = args.output_dir

    return cfg


def validate_config(cfg: Dict[str, Any]) -> None:
    required_root = ["run_id", "species_list", "conditions", "model_assumptions", "tau_grid"]
    for key in required_root:
        if key not in cfg:
            raise ValueError(f"Missing required config field: {key}")

    if not isinstance(cfg["species_list"], list) or not cfg["species_list"]:
        raise ValueError("species_list must be a non-empty list.")

    cond = cfg["conditions"]
    for key in ["temperature_C", "pressure_mbar", "volume_m3"]:
        if key not in cond:
            raise ValueError(f"Missing conditions.{key}")

    model = cfg["model_assumptions"]
    for key in ["species_mode", "gas_model", "velocity_model", "frequency_mode", "density_mode"]:
        if key not in model:
            raise ValueError(f"Missing model_assumptions.{key}")

    tau_grid = cfg["tau_grid"]
    if not isinstance(tau_grid, list) or not tau_grid:
        raise ValueError("tau_grid must be a non-empty list.")
    for tau in tau_grid:
        if float(tau) <= 0.0:
            raise ValueError("All tau values must be > 0.")

    temp_C = float(cond["temperature_C"])
    pressure_mbar = float(cond["pressure_mbar"])
    volume_m3 = float(cond["volume_m3"])
    if volume_m3 <= 0:
        raise ValueError("volume_m3 must be > 0.")
    if pressure_mbar <= 0:
        raise ValueError("pressure_mbar must be > 0.")
    if temp_C <= -273.15:
        raise ValueError("temperature_C must be above absolute zero.")


def canonical_symbol(species: str) -> str:
    symbols = {
        "hydrogen": "H",
        "carbon": "C",
        "nitrogen": "N",
        "sodium": "Na",
        "phosphorus": "P",
        "sulfur": "S",
    }
    return symbols.get(species.lower(), species[:2].capitalize())


def get_atomic_mass_u(species: str, cfg: Dict[str, Any]) -> float:
    species_data = cfg.get("species_data", {})
    if isinstance(species_data, dict):
        per_species = species_data.get(species)
        if isinstance(per_species, dict) and "mass_u" in per_species:
            return float(per_species["mass_u"])
    try:
        return ATOMIC_MASS_U[species.lower()]
    except KeyError as exc:
        raise KeyError(
            f"No atomic mass available for species '{species}'. Add it via species_data."
        ) from exc


def compute_number_density(conditions: Conditions, assumptions: ModelAssumptions) -> float:
    if assumptions.gas_model != "ideal_gas":
        raise NotImplementedError(f"Unsupported gas_model: {assumptions.gas_model}")
    # Ideal gas: n/V = P / (k_B T)
    return conditions.pressure_Pa / (BOLTZMANN_CONSTANT * conditions.temperature_K)


def compute_particle_count(number_density_m3: float, volume_m3: float) -> float:
    return number_density_m3 * volume_m3


def compute_characteristic_velocity(
    mass_kg: float,
    temperature_K: float,
    velocity_model: str,
) -> float:
    if velocity_model == "mean":
        return math.sqrt((8.0 * BOLTZMANN_CONSTANT * temperature_K) / (math.pi * mass_kg))
    if velocity_model == "rms":
        return math.sqrt((3.0 * BOLTZMANN_CONSTANT * temperature_K) / mass_kg)
    if velocity_model == "most_probable":
        return math.sqrt((2.0 * BOLTZMANN_CONSTANT * temperature_K) / mass_kg)
    raise NotImplementedError(f"Unsupported velocity_model: {velocity_model}")


def compute_frequency_and_omega(
    velocity_m_s: float,
    lambda_db_m: float,
    energy_j: float,
    frequency_mode: str,
) -> Tuple[Optional[float], Optional[float]]:
    if frequency_mode == "none":
        return None, None
    if frequency_mode == "kinetic_energy_based":
        frequency_hz = energy_j / PLANCK_CONSTANT
        return frequency_hz, 2.0 * math.pi * frequency_hz
    if frequency_mode == "omega_from_v_over_lambda":
        if lambda_db_m <= 0.0:
            return None, None
        frequency_hz = velocity_m_s / lambda_db_m
        return frequency_hz, 2.0 * math.pi * frequency_hz
    raise NotImplementedError(f"Unsupported frequency_mode: {frequency_mode}")


def compute_species_base_result(
    species: str,
    conditions: Conditions,
    assumptions: ModelAssumptions,
    cfg: Dict[str, Any],
) -> SpeciesBaseResult:
    mass_u = get_atomic_mass_u(species, cfg)
    mass_kg = mass_u * ATOMIC_MASS_UNIT

    number_density_m3 = compute_number_density(conditions, assumptions)
    particle_count = compute_particle_count(number_density_m3, conditions.volume_m3)

    velocity_m_s = compute_characteristic_velocity(
        mass_kg=mass_kg,
        temperature_K=conditions.temperature_K,
        velocity_model=assumptions.velocity_model,
    )
    momentum = mass_kg * velocity_m_s
    lambda_db = PLANCK_CONSTANT / momentum
    k_m_inv = (2.0 * math.pi) / lambda_db
    energy_j = 0.5 * mass_kg * velocity_m_s * velocity_m_s
    frequency_hz, omega_rad_s = compute_frequency_and_omega(
        velocity_m_s=velocity_m_s,
        lambda_db_m=lambda_db,
        energy_j=energy_j,
        frequency_mode=assumptions.frequency_mode,
    )

    return SpeciesBaseResult(
        species=species,
        symbol=canonical_symbol(species),
        mass_u=mass_u,
        mass_kg=mass_kg,
        temperature_K=conditions.temperature_K,
        pressure_Pa=conditions.pressure_Pa,
        volume_m3=conditions.volume_m3,
        number_density_m3=number_density_m3,
        particle_count=particle_count,
        velocity_m_s=velocity_m_s,
        momentum_kg_m_s=momentum,
        lambda_db_m=lambda_db,
        k_m_inv=k_m_inv,
        omega_rad_s=omega_rad_s,
        frequency_hz=frequency_hz,
        energy_j=energy_j,
    )


def normalize_log_scores(values: Dict[str, float], invert: bool = False) -> Dict[str, float]:
    """
    Log-normalize positive quantities to [0,1].
    If invert=True, larger raw values become smaller scores.
    """
    for key, value in values.items():
        if value <= 0.0 or not math.isfinite(value):
            raise ValueError(f"Non-positive or non-finite value for score normalization: {key}={value}")

    logs = {key: math.log10(value) for key, value in values.items()}
    min_v = min(logs.values())
    max_v = max(logs.values())

    if math.isclose(min_v, max_v):
        normalized = {key: 0.5 for key in logs}
    else:
        normalized = {key: (val - min_v) / (max_v - min_v) for key, val in logs.items()}

    if invert:
        normalized = {key: 1.0 - val for key, val in normalized.items()}

    return normalized


def build_surrogates(
    base_results: List[SpeciesBaseResult],
    weights: Dict[str, float],
) -> Dict[str, SpeciesSurrogates]:
    # length scale score based directly on lambda_db
    lambda_map = {r.species: r.lambda_db_m for r in base_results}
    energy_map = {r.species: r.energy_j for r in base_results}
    occupancy_map = {r.species: r.number_density_m3 for r in base_results}

    length_scores = normalize_log_scores(lambda_map, invert=False)
    energy_scores = normalize_log_scores(energy_map, invert=False)
    occupancy_scores = normalize_log_scores(occupancy_map, invert=False)

    out: Dict[str, SpeciesSurrogates] = {}
    for result in base_results:
        sp = result.species
        ws_length = float(weights.get("length_scale_score", 1.0))
        ws_energy = float(weights.get("energy_score", 1.0))
        ws_occupancy = float(weights.get("occupancy_score", 1.0))
        denom = ws_length + ws_energy + ws_occupancy
        if denom <= 0:
            raise ValueError("At least one surrogate weight must be positive.")

        signature_score = (
            ws_length * length_scores[sp]
            + ws_energy * energy_scores[sp]
            + ws_occupancy * occupancy_scores[sp]
        ) / denom

        out[sp] = SpeciesSurrogates(
            length_scale_score=length_scores[sp],
            energy_score=energy_scores[sp],
            occupancy_score=occupancy_scores[sp],
            signature_score=signature_score,
        )
    return out


def compute_tau_alignment_and_response(
    tau: float,
    base: SpeciesBaseResult,
    surrogate: SpeciesSurrogates,
) -> TauResponse:
    # Conservative exploratory choice:
    # Compare tau to a characteristic timescale from kinetic-energy-based frequency if available.
    # If not, use inverse velocity-over-lambda proxy if frequency exists. Otherwise fallback.
    if base.frequency_hz and base.frequency_hz > 0:
        char_time = 1.0 / base.frequency_hz
    elif base.omega_rad_s and base.omega_rad_s > 0:
        char_time = 1.0 / (base.omega_rad_s / (2.0 * math.pi))
    else:
        # fallback: use a generic timescale proxy lambda/v
        char_time = base.lambda_db_m / base.velocity_m_s

    ratio = tau / char_time
    # Alignment score near 1.0 when ratio ~ 1 on a log scale.
    alignment = max(0.0, 1.0 - abs(math.log10(ratio)) / 3.0)
    alignment = min(1.0, alignment)

    # Response score folds in signature strength but stays simple and transparent.
    response = alignment * surrogate.signature_score

    if alignment >= 0.85:
        label = "near_window"
    elif alignment >= 0.55:
        label = "moderate_window"
    else:
        label = "off_window"

    return TauResponse(
        tau=tau,
        tau_alignment_score=alignment,
        tau_response_score=response,
        tau_window_label=label,
    )


def rank_dict_desc(values: Dict[str, float]) -> List[str]:
    return [key for key, _ in sorted(values.items(), key=lambda item: (-item[1], item[0]))]


def compute_matter_sensitive_delta(
    base_results: List[SpeciesBaseResult],
    surrogates: Dict[str, SpeciesSurrogates],
) -> Dict[str, float]:
    mass_scores = {r.species: r.mass_kg for r in base_results}
    sig_scores = {sp: sur.signature_score for sp, sur in surrogates.items()}

    mass_rank = rank_dict_desc(mass_scores)
    sig_rank = rank_dict_desc(sig_scores)

    mass_pos = {species: idx for idx, species in enumerate(mass_rank)}
    sig_pos = {species: idx for idx, species in enumerate(sig_rank)}

    return {species: float(sig_pos[species] - mass_pos[species]) for species in mass_pos}


def ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def write_json(path: Path, payload: Dict[str, Any]) -> None:
    with path.open("w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2, ensure_ascii=False)


def write_csv(path: Path, rows: List[Dict[str, Any]]) -> None:
    if not rows:
        raise ValueError(f"No rows to write for CSV: {path}")
    fieldnames = list(rows[0].keys())
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def summarize_claims(
    base_results: List[SpeciesBaseResult],
    tau_rows: List[Dict[str, Any]],
    matter_sensitive_delta: Dict[str, float],
) -> Dict[str, Any]:
    unique_signature_species = len(base_results) >= 2

    response_by_species: Dict[str, List[float]] = {}
    for row in tau_rows:
        response_by_species.setdefault(str(row["species"]), []).append(float(row["tau_response_score"]))

    ds2_supported = False
    if response_by_species:
        means = {sp: sum(vals) / len(vals) for sp, vals in response_by_species.items() if vals}
        if len(set(round(v, 9) for v in means.values())) > 1:
            ds2_supported = True

    deltas = [abs(v) for v in matter_sensitive_delta.values()]
    max_delta = max(deltas) if deltas else 0.0
    ds3_supported = max_delta >= 1.0

    candidate_rows = [r for r in tau_rows if str(r["tau_window_label"]) == "near_window"]
    ds4_supported = len(candidate_rows) > 0

    overall = "supported" if (unique_signature_species and ds2_supported) else "partly_supported"

    return {
        "claim_ds1_status": "supported" if unique_signature_species else "not_supported",
        "claim_ds2_status": "supported" if ds2_supported else "partly_supported",
        "claim_ds3_status": "supported" if ds3_supported else "partly_supported",
        "claim_ds4_status": "supported" if ds4_supported else "partly_supported",
        "claim_ds5_status": "supported",
        "mass_only_status": "partly_supported" if ds3_supported else "supported",
        "matter_sensitive_status": "supported" if ds3_supported else "partly_supported",
        "tau_window_candidate_status": "supported" if ds4_supported else "partly_supported",
        "overall_status": overall,
        "notes": {
            "max_matter_sensitive_delta": max_delta,
            "tau_candidate_count": len(candidate_rows),
        },
    }


def build_readout(
    cfg: Dict[str, Any],
    base_results: List[SpeciesBaseResult],
    surrogates: Dict[str, SpeciesSurrogates],
    tau_rows: List[Dict[str, Any]],
    matter_sensitive_delta: Dict[str, float],
    claims: Dict[str, Any],
) -> str:
    run_id = cfg["run_id"]
    conditions = cfg["conditions"]
    model = cfg["model_assumptions"]
    tau_grid = cfg["tau_grid"]

    strongest_surrogate_species = max(
        surrogates.items(), key=lambda item: item[1].signature_score
    )[0]
    largest_delta_species = max(matter_sensitive_delta.items(), key=lambda item: abs(item[1]))[0]

    candidate_rows = [r for r in tau_rows if str(r["tau_window_label"]) == "near_window"]
    best_candidate = None
    if candidate_rows:
        best_candidate = max(candidate_rows, key=lambda row: float(row["tau_response_score"]))

    robust_points = [
        "Reproduzierbare de-Broglie-bezogene Grundgrößen wurden pro Spezies konstruiert.",
        f"Die kombinierte Signatur ist im aktuellen Lauf für '{strongest_surrogate_species}' am stärksten ausgeprägt.",
        f"Die stärkste Abweichung von bloßer Massenordnung zeigt '{largest_delta_species}'.",
    ]

    signal_points = [
        "Die Tau-Fensterantwort ist explorativ und noch nicht als starke Resonanzbehauptung zu lesen.",
        "Materiesensitive Unterschiede sollten gegen alternative Modellannahmen weiter geprüft werden.",
    ]

    unclear_points = [
        "Noch offen ist, welche Einzelsurrogate physikalisch am tragfähigsten sind.",
        "Noch offen ist, wie direkt tau als physikalische Antwort- oder Taktskala interpretiert werden darf.",
    ]

    readout_lines = [
        f"# debroglie_matter_signature_readout for {run_id}",
        "",
        "## 1. Run-Kontext",
        f"- **Run-ID:** {run_id}",
        f"- **Spezies:** {', '.join(cfg['species_list'])}",
        (
            f"- **Bedingungen:** {conditions['temperature_C']} °C, "
            f"{conditions['pressure_mbar']} mbar, {conditions['volume_m3']} m^3"
        ),
        f"- **Geschwindigkeitsmodell:** {model['velocity_model']}",
        f"- **Frequenzmodus:** {model['frequency_mode']}",
        f"- **Tau-Grid:** {tau_grid}",
        "",
        "Kurzlesart:",
        "",
        "> Explorationslauf für materialspezifische de-Broglie-Signaturen atomarer Spezies unter definierten Standardbedingungen.",
        "",
        "## 2. Signatur-Surrogate",
    ]

    for base in base_results:
        sur = surrogates[base.species]
        readout_lines.extend([
            f"### {base.species}",
            f"- `lambda_db`: {base.lambda_db_m:.6e} m",
            f"- `energy`: {base.energy_j:.6e} J",
            f"- `number_density`: {base.number_density_m3:.6e} 1/m^3",
            f"- `length_scale_score`: {sur.length_scale_score:.6f}",
            f"- `energy_score`: {sur.energy_score:.6f}",
            f"- `occupancy_score`: {sur.occupancy_score:.6f}",
            f"- `signature_score`: {sur.signature_score:.6f}",
            "",
        ])

    readout_lines.extend([
        "## 3. Massen- vs. Materiesensitivität",
        "",
        "Abweichung von bloßer Massenordnung (`matter_sensitive_delta`):",
        "",
    ])
    for species, delta in sorted(matter_sensitive_delta.items()):
        readout_lines.append(f"- `{species}`: {delta:+.0f}")

    readout_lines.extend([
        "",
        "## 4. Tau-Fenstervergleich",
        "",
    ])

    if best_candidate:
        readout_lines.extend([
            f"- Bester defensiver Fensterkandidat: `{best_candidate['species']}` bei `tau = {best_candidate['tau']}`",
            f"- `tau_response_score = {float(best_candidate['tau_response_score']):.6f}`",
            f"- `tau_window_label = {best_candidate['tau_window_label']}`",
        ])
    else:
        readout_lines.append("- Kein starker `near_window`-Kandidat im aktuellen Lauf.")

    readout_lines.extend([
        "",
        "## 5. Claim-Status",
        f"- DS1: {claims['claim_ds1_status']}",
        f"- DS2: {claims['claim_ds2_status']}",
        f"- DS3: {claims['claim_ds3_status']}",
        f"- DS4: {claims['claim_ds4_status']}",
        f"- DS5: {claims['claim_ds5_status']}",
        "",
        "## 6. Gesamtbewertung",
        "",
        "### Belastbar steht",
    ])
    readout_lines.extend([f"- {item}" for item in robust_points])

    readout_lines.extend([
        "",
        "### Signalhaft, aber noch offen",
    ])
    readout_lines.extend([f"- {item}" for item in signal_points])

    readout_lines.extend([
        "",
        "### Nicht gestützt oder unklar",
    ])
    readout_lines.extend([f"- {item}" for item in unclear_points])

    readout_lines.extend([
        "",
        "## 7. Bottom line",
        "",
        (
            "> Der Lauf zeigt, dass aus de-Broglie-bezogenen Materiedaten atomarer Spezies "
            "reproduzierbare Signatur-Surrogate konstruiert werden können. Die entscheidende "
            "Frage bleibt nun, ob die beobachteten Unterschiede robust über triviale Massenskalierung "
            "hinausgehen und sich gegen alternative Modellannahmen halten."
        ),
        "",
        "Kurzformel:",
        "",
        "> Erst Signatur sichtbar machen, dann prüfen, ob mehr als Masse übrig bleibt.",
    ])

    return "\n".join(readout_lines)


def main() -> None:
    args = parse_args()
    cfg = apply_overrides(load_config(Path(args.config)), args)
    validate_config(cfg)

    if args.dry_run:
        print("Config valid. Dry run completed.")
        return

    conditions = Conditions(**cfg["conditions"])
    assumptions = ModelAssumptions(**cfg["model_assumptions"])

    species_list = [str(species).lower() for species in cfg["species_list"]]
    weights = cfg.get("surrogates", {}).get("weights", {})
    tau_grid = [float(tau) for tau in cfg["tau_grid"]]

    base_results = [
        compute_species_base_result(species, conditions, assumptions, cfg)
        for species in species_list
    ]
    surrogates = build_surrogates(base_results, weights)

    tau_rows: List[Dict[str, Any]] = []
    state_species_results: List[Dict[str, Any]] = []

    for base in base_results:
        surrogate = surrogates[base.species]
        tau_response_items: List[Dict[str, Any]] = []

        for tau in tau_grid:
            response = compute_tau_alignment_and_response(tau, base, surrogate)
            row = {
                "run_id": cfg["run_id"],
                "species": base.species,
                "mass_kg": base.mass_kg,
                "velocity_model": assumptions.velocity_model,
                "velocity": base.velocity_m_s,
                "momentum": base.momentum_kg_m_s,
                "lambda_db": base.lambda_db_m,
                "k": base.k_m_inv,
                "frequency_mode": assumptions.frequency_mode,
                "frequency": base.frequency_hz,
                "number_density": base.number_density_m3,
                "length_scale_score": surrogate.length_scale_score,
                "energy_score": surrogate.energy_score,
                "occupancy_score": surrogate.occupancy_score,
                "signature_score": surrogate.signature_score,
                "tau": response.tau,
                "tau_alignment_score": response.tau_alignment_score,
                "tau_response_score": response.tau_response_score,
                "tau_window_label": response.tau_window_label,
            }
            tau_rows.append(row)
            tau_response_items.append({
                "tau": response.tau,
                "tau_alignment_score": response.tau_alignment_score,
                "tau_response_score": response.tau_response_score,
                "tau_window_label": response.tau_window_label,
            })

        state_species_results.append({
            **asdict(base),
            "signature_surrogates": asdict(surrogate),
            "tau_response": tau_response_items,
        })

    matter_sensitive_delta = compute_matter_sensitive_delta(base_results, surrogates)

    mass_order = rank_dict_desc({r.species: r.mass_kg for r in base_results})
    signature_order = rank_dict_desc({sp: sur.signature_score for sp, sur in surrogates.items()})

    claims = summarize_claims(base_results, tau_rows, matter_sensitive_delta)

    state_payload = {
        "run_id": cfg["run_id"],
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "conditions": {
            **cfg["conditions"],
            "temperature_K": conditions.temperature_K,
            "pressure_Pa": conditions.pressure_Pa,
        },
        "model_assumptions": cfg["model_assumptions"],
        "tau_grid": tau_grid,
        "species_results": state_species_results,
        "comparisons": {
            "mass_only_ordering": mass_order,
            "signature_ordering": signature_order,
            "matter_sensitive_delta": matter_sensitive_delta,
        },
    }

    base_dir = Path(cfg.get("output", {}).get("base_dir", "results/debroglie_matter_signature"))
    run_dir = base_dir / str(cfg["run_id"])
    ensure_dir(run_dir)

    if cfg.get("output", {}).get("write_state_json", True):
        write_json(run_dir / "debroglie_matter_signature_state.json", state_payload)

    if cfg.get("output", {}).get("write_claims_json", True):
        write_json(run_dir / "debroglie_matter_signature_claims.json", claims)

    if cfg.get("output", {}).get("write_scan_csv", True):
        # add rankings
        mass_rank_pos = {species: idx + 1 for idx, species in enumerate(mass_order)}
        sig_rank_pos = {species: idx + 1 for idx, species in enumerate(signature_order)}
        csv_rows = []
        for row in tau_rows:
            species = str(row["species"])
            extended = dict(row)
            extended["mass_only_rank"] = mass_rank_pos[species]
            extended["matter_sensitive_rank"] = sig_rank_pos[species]
            delta = matter_sensitive_delta[species]
            extended["matter_sensitive_delta"] = delta
            extended["response_label"] = (
                "nontrivial_candidate"
                if abs(delta) >= 1.0 and row["tau_window_label"] != "off_window"
                else "mass_like"
            )
            csv_rows.append(extended)
        write_csv(run_dir / "debroglie_matter_signature_scan.csv", csv_rows)

    if cfg.get("output", {}).get("write_tau_response_csv", True):
        write_csv(run_dir / "debroglie_matter_signature_tau_response.csv", tau_rows)

    if cfg.get("output", {}).get("write_readout_md", True):
        readout = build_readout(
            cfg=cfg,
            base_results=base_results,
            surrogates=surrogates,
            tau_rows=tau_rows,
            matter_sensitive_delta=matter_sensitive_delta,
            claims=claims,
        )
        (run_dir / "debroglie_matter_signature_readout.md").write_text(readout, encoding="utf-8")

    print(f"[OK] Run completed: {cfg['run_id']}")
    print(f"[OK] Output directory: {run_dir}")


if __name__ == "__main__":
    main()
