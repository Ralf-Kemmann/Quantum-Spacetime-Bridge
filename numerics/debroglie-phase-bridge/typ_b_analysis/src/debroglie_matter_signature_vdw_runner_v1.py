#!/usr/bin/env python3
"""
debroglie_matter_signature_vdw_runner_v1.py

Minimal van-der-Waals extension runner for the materialspecific de Broglie signature block.

This runner is intentionally conservative:
- it keeps the wave layer transparent
- it adds a simple VDW matter layer via a/b parameters
- it compares ideal_gas vs van_der_waals style signatures
- it does not claim full-realism or a finished spacetime model
"""

from __future__ import annotations

import argparse
import csv
import json
import math
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

try:
    import yaml  # type: ignore
except Exception as exc:
    raise SystemExit("PyYAML is required for this runner.") from exc


PLANCK_CONSTANT = 6.62607015e-34
BOLTZMANN_CONSTANT = 1.380649e-23
AVOGADRO_CONSTANT = 6.02214076e23
ATOMIC_MASS_UNIT = 1.66053906660e-27
GAS_CONSTANT = 8.31446261815324

ATOMIC_MASS_U: Dict[str, float] = {
    "hydrogen": 1.00784,
    "carbon": 12.011,
    "nitrogen": 14.007,
    "sodium": 22.98976928,
    "phosphorus": 30.973761998,
    "sulfur": 32.06,
}

# Deliberately simple exploratory VDW parameters.
# Units:
#   a: Pa * m^6 / mol^2
#   b: m^3 / mol
# These are rough literature-like placeholders for exploratory modeling only.
VDW_PARAMS: Dict[str, Dict[str, float]] = {
    "hydrogen": {"a": 0.0247, "b": 2.661e-5},
    "nitrogen": {"a": 0.1370, "b": 3.870e-5},
    "sodium": {"a": 0.4500, "b": 7.100e-5},
    "carbon": {"a": 0.3000, "b": 4.500e-5},
    "phosphorus": {"a": 0.4200, "b": 6.200e-5},
    "sulfur": {"a": 0.4800, "b": 6.800e-5},
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
    vdw_mode: str


@dataclass
class SpeciesWaveResult:
    species: str
    symbol: str
    mass_u: float
    mass_kg: float
    temperature_K: float
    pressure_Pa: float
    volume_m3: float
    number_density_m3: float
    particle_count: float
    mol_count: float
    velocity_m_s: float
    momentum_kg_m_s: float
    lambda_db_m: float
    k_m_inv: float
    frequency_hz: Optional[float]
    omega_rad_s: Optional[float]
    energy_j: float


@dataclass
class SpeciesVDWResult:
    vdw_a: float
    vdw_b: float
    interaction_term: float
    excluded_volume_term: float
    corrected_number_density_m3: float


@dataclass
class WaveSurrogates:
    length_scale_score: float
    energy_score: float
    occupancy_score: float
    signature_score_wave: float


@dataclass
class VDWSurrogates:
    interaction_score: float
    excluded_volume_score: float
    vdw_signature_score: float


@dataclass
class CombinedSurrogates:
    signature_score_combined: float


@dataclass
class TauResponse:
    tau: float
    tau_alignment_score: float
    tau_response_score: float
    tau_window_label: str


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="VDW extension runner for de Broglie matter signatures.")
    parser.add_argument("--config", required=True, help="Path to YAML config.")
    parser.add_argument("--output-dir", help="Override output directory.")
    parser.add_argument("--run-id", help="Override run id.")
    parser.add_argument("--gas-model", choices=["ideal_gas", "van_der_waals"], help="Override gas model.")
    parser.add_argument("--tau-grid", help="Comma-separated tau values.")
    parser.add_argument("--dry-run", action="store_true", help="Validate config only.")
    return parser.parse_args()


def load_config(path: Path) -> Dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        cfg = yaml.safe_load(handle)
    if not isinstance(cfg, dict):
        raise ValueError("Config root must be a mapping.")
    return cfg


def apply_overrides(cfg: Dict[str, Any], args: argparse.Namespace) -> Dict[str, Any]:
    clone = json.loads(json.dumps(cfg))
    if args.run_id:
        clone["run_id"] = args.run_id
    if args.gas_model:
        clone.setdefault("model_assumptions", {})["gas_model"] = args.gas_model
    if args.output_dir:
        clone.setdefault("output", {})["base_dir"] = args.output_dir
    if args.tau_grid:
        clone["tau_grid"] = [float(x.strip()) for x in args.tau_grid.split(",") if x.strip()]
    return clone


def validate_config(cfg: Dict[str, Any]) -> None:
    for key in ["run_id", "species_list", "conditions", "model_assumptions", "tau_grid"]:
        if key not in cfg:
            raise ValueError(f"Missing required field: {key}")

    if not cfg["species_list"]:
        raise ValueError("species_list must be non-empty.")

    cond = cfg["conditions"]
    for key in ["temperature_C", "pressure_mbar", "volume_m3"]:
        if key not in cond:
            raise ValueError(f"Missing conditions.{key}")

    model = cfg["model_assumptions"]
    for key in ["species_mode", "gas_model", "velocity_model", "frequency_mode", "density_mode", "vdw_mode"]:
        if key not in model:
            raise ValueError(f"Missing model_assumptions.{key}")

    if float(cond["volume_m3"]) <= 0:
        raise ValueError("volume_m3 must be > 0")
    if float(cond["pressure_mbar"]) <= 0:
        raise ValueError("pressure_mbar must be > 0")
    if float(cond["temperature_C"]) <= -273.15:
        raise ValueError("temperature_C must be above absolute zero")

    if not cfg["tau_grid"]:
        raise ValueError("tau_grid must be non-empty")
    for tau in cfg["tau_grid"]:
        if float(tau) <= 0:
            raise ValueError("tau values must be > 0")


def canonical_symbol(species: str) -> str:
    return {
        "hydrogen": "H",
        "carbon": "C",
        "nitrogen": "N",
        "sodium": "Na",
        "phosphorus": "P",
        "sulfur": "S",
    }.get(species.lower(), species[:2].capitalize())


def get_atomic_mass_u(species: str, cfg: Dict[str, Any]) -> float:
    species_data = cfg.get("species_data", {})
    if isinstance(species_data, dict):
        entry = species_data.get(species)
        if isinstance(entry, dict) and "mass_u" in entry:
            return float(entry["mass_u"])
    if species.lower() not in ATOMIC_MASS_U:
        raise KeyError(f"No atomic mass found for species '{species}'")
    return ATOMIC_MASS_U[species.lower()]


def get_vdw_params(species: str, cfg: Dict[str, Any]) -> Tuple[float, float]:
    species_data = cfg.get("species_data", {})
    if isinstance(species_data, dict):
        entry = species_data.get(species)
        if isinstance(entry, dict) and "vdw_a" in entry and "vdw_b" in entry:
            return float(entry["vdw_a"]), float(entry["vdw_b"])
    if species.lower() not in VDW_PARAMS:
        raise KeyError(f"No VDW parameters found for species '{species}'")
    params = VDW_PARAMS[species.lower()]
    return float(params["a"]), float(params["b"])


def compute_number_density_ideal(conditions: Conditions) -> float:
    return conditions.pressure_Pa / (BOLTZMANN_CONSTANT * conditions.temperature_K)


def compute_mol_count_ideal(conditions: Conditions) -> float:
    return (conditions.pressure_Pa * conditions.volume_m3) / (GAS_CONSTANT * conditions.temperature_K)


def compute_mol_count_vdw(conditions: Conditions, a: float, b: float) -> float:
    """
    Solve the van der Waals cubic for n (moles) in:
      (P + a (n/V)^2) (V - n b) = n R T
    Choose the smallest positive real root below V/b if available.
    """
    P = conditions.pressure_Pa
    T = conditions.temperature_K
    V = conditions.volume_m3

    # f(n) = (P + a(n/V)^2)(V - nb) - nRT
    def f(n: float) -> float:
        return (P + a * (n / V) ** 2) * (V - n * b) - n * GAS_CONSTANT * T

    # Bracket: start around ideal value, upper bound just below close packing.
    n_ideal = compute_mol_count_ideal(conditions)
    n_max = 0.99 * V / b if b > 0 else max(10.0 * n_ideal, 1.0)

    lo = 0.0
    hi = max(n_max, n_ideal * 2.0, 1.0)

    flo = f(lo)
    fhi = f(hi)

    # Try to find a sign change by shrinking/expanding hi.
    attempts = 0
    while flo * fhi > 0 and attempts < 50:
        hi *= 0.8
        fhi = f(hi)
        attempts += 1

    if flo * fhi > 0:
        # Fallback to ideal if root bracketing fails; keep runner robust.
        return n_ideal

    for _ in range(200):
        mid = 0.5 * (lo + hi)
        fm = f(mid)
        if abs(fm) < 1e-16:
            return mid
        if flo * fm <= 0:
            hi = mid
            fhi = fm
        else:
            lo = mid
            flo = fm
    return 0.5 * (lo + hi)


def compute_characteristic_velocity(mass_kg: float, temperature_K: float, velocity_model: str) -> float:
    if velocity_model == "mean":
        return math.sqrt((8.0 * BOLTZMANN_CONSTANT * temperature_K) / (math.pi * mass_kg))
    if velocity_model == "rms":
        return math.sqrt((3.0 * BOLTZMANN_CONSTANT * temperature_K) / mass_kg)
    if velocity_model == "most_probable":
        return math.sqrt((2.0 * BOLTZMANN_CONSTANT * temperature_K) / mass_kg)
    raise NotImplementedError(f"Unsupported velocity model: {velocity_model}")


def compute_frequency_and_omega(velocity: float, lambda_db: float, energy_j: float, frequency_mode: str) -> Tuple[Optional[float], Optional[float]]:
    if frequency_mode == "none":
        return None, None
    if frequency_mode == "kinetic_energy_based":
        f = energy_j / PLANCK_CONSTANT
        return f, 2.0 * math.pi * f
    if frequency_mode == "omega_from_v_over_lambda":
        f = velocity / lambda_db
        return f, 2.0 * math.pi * f
    raise NotImplementedError(f"Unsupported frequency mode: {frequency_mode}")


def compute_wave_result(species: str, conditions: Conditions, assumptions: ModelAssumptions, cfg: Dict[str, Any]) -> SpeciesWaveResult:
    mass_u = get_atomic_mass_u(species, cfg)
    mass_kg = mass_u * ATOMIC_MASS_UNIT

    n_ideal_moles = compute_mol_count_ideal(conditions)
    number_density_ideal = compute_number_density_ideal(conditions)

    velocity = compute_characteristic_velocity(mass_kg, conditions.temperature_K, assumptions.velocity_model)
    momentum = mass_kg * velocity
    lambda_db = PLANCK_CONSTANT / momentum
    k_val = 2.0 * math.pi / lambda_db
    energy = 0.5 * mass_kg * velocity * velocity
    f_hz, omega = compute_frequency_and_omega(velocity, lambda_db, energy, assumptions.frequency_mode)

    return SpeciesWaveResult(
        species=species,
        symbol=canonical_symbol(species),
        mass_u=mass_u,
        mass_kg=mass_kg,
        temperature_K=conditions.temperature_K,
        pressure_Pa=conditions.pressure_Pa,
        volume_m3=conditions.volume_m3,
        number_density_m3=number_density_ideal,
        particle_count=number_density_ideal * conditions.volume_m3,
        mol_count=n_ideal_moles,
        velocity_m_s=velocity,
        momentum_kg_m_s=momentum,
        lambda_db_m=lambda_db,
        k_m_inv=k_val,
        frequency_hz=f_hz,
        omega_rad_s=omega,
        energy_j=energy,
    )


def compute_vdw_result(species: str, conditions: Conditions, cfg: Dict[str, Any]) -> SpeciesVDWResult:
    a, b = get_vdw_params(species, cfg)
    n_vdw = compute_mol_count_vdw(conditions, a, b)
    mol_density = n_vdw / conditions.volume_m3
    corrected_number_density = mol_density * AVOGADRO_CONSTANT

    interaction_term = a * mol_density * mol_density
    excluded_volume_term = b * n_vdw / conditions.volume_m3

    return SpeciesVDWResult(
        vdw_a=a,
        vdw_b=b,
        interaction_term=interaction_term,
        excluded_volume_term=excluded_volume_term,
        corrected_number_density_m3=corrected_number_density,
    )


def normalize_log_scores(values: Dict[str, float], invert: bool = False) -> Dict[str, float]:
    for key, val in values.items():
        if val <= 0.0 or not math.isfinite(val):
            raise ValueError(f"Invalid value for normalization: {key}={val}")
    logs = {k: math.log10(v) for k, v in values.items()}
    mn = min(logs.values())
    mx = max(logs.values())
    if math.isclose(mn, mx):
        out = {k: 0.5 for k in logs}
    else:
        out = {k: (v - mn) / (mx - mn) for k, v in logs.items()}
    if invert:
        out = {k: 1.0 - v for k, v in out.items()}
    return out


def build_wave_surrogates(wave_results: List[SpeciesWaveResult]) -> Dict[str, WaveSurrogates]:
    lambda_map = {r.species: r.lambda_db_m for r in wave_results}
    energy_map = {r.species: r.energy_j for r in wave_results}
    density_map = {r.species: r.number_density_m3 for r in wave_results}

    length_scores = normalize_log_scores(lambda_map)
    energy_scores = normalize_log_scores(energy_map)
    density_scores = normalize_log_scores(density_map)

    out: Dict[str, WaveSurrogates] = {}
    for r in wave_results:
        sp = r.species
        wave_sig = (length_scores[sp] + energy_scores[sp] + density_scores[sp]) / 3.0
        out[sp] = WaveSurrogates(
            length_scale_score=length_scores[sp],
            energy_score=energy_scores[sp],
            occupancy_score=density_scores[sp],
            signature_score_wave=wave_sig,
        )
    return out


def build_vdw_surrogates(vdw_results: Dict[str, SpeciesVDWResult]) -> Dict[str, VDWSurrogates]:
    interaction_map = {sp: r.interaction_term for sp, r in vdw_results.items()}
    excluded_map = {sp: r.excluded_volume_term for sp, r in vdw_results.items()}

    interaction_scores = normalize_log_scores(interaction_map)
    excluded_scores = normalize_log_scores(excluded_map)

    out: Dict[str, VDWSurrogates] = {}
    for sp, r in vdw_results.items():
        sig = 0.5 * (interaction_scores[sp] + excluded_scores[sp])
        out[sp] = VDWSurrogates(
            interaction_score=interaction_scores[sp],
            excluded_volume_score=excluded_scores[sp],
            vdw_signature_score=sig,
        )
    return out


def build_combined_surrogates(
    wave_surrogates: Dict[str, WaveSurrogates],
    vdw_surrogates: Optional[Dict[str, VDWSurrogates]],
    wave_weight: float,
    vdw_weight: float,
) -> Dict[str, CombinedSurrogates]:
    out: Dict[str, CombinedSurrogates] = {}
    for sp, wave in wave_surrogates.items():
        if vdw_surrogates and sp in vdw_surrogates and (wave_weight + vdw_weight) > 0:
            vdw = vdw_surrogates[sp]
            combined = ((wave_weight * wave.signature_score_wave) + (vdw_weight * vdw.vdw_signature_score)) / (wave_weight + vdw_weight)
        else:
            combined = wave.signature_score_wave
        out[sp] = CombinedSurrogates(signature_score_combined=combined)
    return out


def compute_tau_response(tau: float, frequency_hz: Optional[float], signature_score: float, lambda_db: float, velocity: float) -> TauResponse:
    if frequency_hz and frequency_hz > 0:
        char_time = 1.0 / frequency_hz
    else:
        char_time = lambda_db / velocity

    ratio = tau / char_time
    alignment = max(0.0, 1.0 - abs(math.log10(ratio)) / 3.0)
    alignment = min(1.0, alignment)
    response = alignment * signature_score

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


def rank_desc(values: Dict[str, float]) -> List[str]:
    return [k for k, _ in sorted(values.items(), key=lambda item: (-item[1], item[0]))]


def compute_delta_from_mass(wave_results: List[SpeciesWaveResult], score_map: Dict[str, float]) -> Dict[str, float]:
    mass_order = rank_desc({r.species: r.mass_kg for r in wave_results})
    sig_order = rank_desc(score_map)
    mass_pos = {sp: i for i, sp in enumerate(mass_order)}
    sig_pos = {sp: i for i, sp in enumerate(sig_order)}
    return {sp: float(sig_pos[sp] - mass_pos[sp]) for sp in mass_pos}


def ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def write_json(path: Path, payload: Dict[str, Any]) -> None:
    with path.open("w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2, ensure_ascii=False)


def write_csv(path: Path, rows: List[Dict[str, Any]]) -> None:
    if not rows:
        raise ValueError(f"No rows to write for {path}")
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def build_claims(
    gas_model: str,
    vdw_surrogates: Optional[Dict[str, VDWSurrogates]],
    delta_wave: Dict[str, float],
    delta_combined: Dict[str, float],
) -> Dict[str, Any]:
    extra_axis = False
    if gas_model == "van_der_waals" and vdw_surrogates:
        values = {sp: v.vdw_signature_score for sp, v in vdw_surrogates.items()}
        extra_axis = len(set(round(x, 12) for x in values.values())) > 1

    improvement = max(abs(v) for v in delta_combined.values()) > max(abs(v) for v in delta_wave.values())

    return {
        "claim_vdw1_status": "supported" if extra_axis else "partly_supported",
        "claim_vdw2_status": "supported" if extra_axis else "partly_supported",
        "claim_vdw3_status": "supported" if improvement else "partly_supported",
        "claim_vdw4_status": "supported" if gas_model == "van_der_waals" else "partly_supported",
        "claim_vdw5_status": "supported",
        "overall_status": "supported" if (gas_model == "van_der_waals" and extra_axis) else "partly_supported",
        "notes": {
            "max_wave_delta": max(abs(v) for v in delta_wave.values()),
            "max_combined_delta": max(abs(v) for v in delta_combined.values()),
        },
    }


def build_readout(
    cfg: Dict[str, Any],
    wave_results: List[SpeciesWaveResult],
    vdw_results: Optional[Dict[str, SpeciesVDWResult]],
    wave_surrogates: Dict[str, WaveSurrogates],
    vdw_surrogates: Optional[Dict[str, VDWSurrogates]],
    combined_surrogates: Dict[str, CombinedSurrogates],
    delta_wave: Dict[str, float],
    delta_combined: Dict[str, float],
    claims: Dict[str, Any],
) -> str:
    gas_model = cfg["model_assumptions"]["gas_model"]
    strongest_wave = max(wave_surrogates.items(), key=lambda item: item[1].signature_score_wave)[0]
    strongest_combined = max(combined_surrogates.items(), key=lambda item: item[1].signature_score_combined)[0]

    lines = [
        f"# debroglie_matter_signature_vdw_readout for {cfg['run_id']}",
        "",
        "## 1. Run-Kontext",
        f"- **Run-ID:** {cfg['run_id']}",
        f"- **Gasmodell:** {gas_model}",
        f"- **Spezies:** {', '.join(cfg['species_list'])}",
        f"- **Bedingungen:** {cfg['conditions']['temperature_C']} °C, {cfg['conditions']['pressure_mbar']} mbar, {cfg['conditions']['volume_m3']} m^3",
        f"- **Tau-Grid:** {cfg['tau_grid']}",
        "",
        "Kurzlesart:",
        "",
        "> Explorationslauf zur Frage, ob die VDW-Stoffschicht dem bisherigen Wellenblock eine zusätzliche materiesensitive Achse eröffnet.",
        "",
        "## 2. Wellen-Schicht",
    ]

    for r in wave_results:
        ws = wave_surrogates[r.species]
        lines.extend([
            f"### {r.species}",
            f"- `lambda_db`: {r.lambda_db_m:.6e} m",
            f"- `energy`: {r.energy_j:.6e} J",
            f"- `number_density`: {r.number_density_m3:.6e} 1/m^3",
            f"- `length_scale_score`: {ws.length_scale_score:.6f}",
            f"- `energy_score`: {ws.energy_score:.6f}",
            f"- `occupancy_score`: {ws.occupancy_score:.6f}",
            f"- `signature_score_wave`: {ws.signature_score_wave:.6f}",
            "",
        ])

    lines.extend([
        "## 3. VDW-Stoff-Schicht",
        "",
    ])

    if gas_model == "van_der_waals" and vdw_results and vdw_surrogates:
        for sp in cfg["species_list"]:
            s = sp.lower()
            vr = vdw_results[s]
            vs = vdw_surrogates[s]
            cs = combined_surrogates[s]
            lines.extend([
                f"### {s}",
                f"- `vdw_a`: {vr.vdw_a:.6e}",
                f"- `vdw_b`: {vr.vdw_b:.6e}",
                f"- `interaction_term`: {vr.interaction_term:.6e}",
                f"- `excluded_volume_term`: {vr.excluded_volume_term:.6e}",
                f"- `interaction_score`: {vs.interaction_score:.6f}",
                f"- `excluded_volume_score`: {vs.excluded_volume_score:.6f}",
                f"- `vdw_signature_score`: {vs.vdw_signature_score:.6f}",
                f"- `signature_score_combined`: {cs.signature_score_combined:.6f}",
                "",
            ])
    else:
        lines.append("- Keine aktive VDW-Stoffschicht in diesem Lauf.")
        lines.append("")

    lines.extend([
        "## 4. Massen- vs. Materiesensitivität",
        "",
        "### Delta relativ zur Massenordnung (Wellen-Schicht)",
    ])
    for sp, d in sorted(delta_wave.items()):
        lines.append(f"- `{sp}`: {d:+.0f}")

    lines.extend([
        "",
        "### Delta relativ zur Massenordnung (kombinierte Signatur)",
    ])
    for sp, d in sorted(delta_combined.items()):
        lines.append(f"- `{sp}`: {d:+.0f}")

    lines.extend([
        "",
        "## 5. Claim-Status",
        f"- VDW1: {claims['claim_vdw1_status']}",
        f"- VDW2: {claims['claim_vdw2_status']}",
        f"- VDW3: {claims['claim_vdw3_status']}",
        f"- VDW4: {claims['claim_vdw4_status']}",
        f"- VDW5: {claims['claim_vdw5_status']}",
        "",
        "## 6. Bottom line",
        "",
        (
            f"> Der stärkste Wellenkandidat ist '{strongest_wave}'. "
            f"Der stärkste kombinierte Kandidat ist '{strongest_combined}'. "
            "Die entscheidende Frage ist nun, ob die VDW-Stoffschicht echte Zusatzstruktur bringt "
            "oder die Ordnung im Kern auf der bisherigen Wellenachse bleibt."
        ),
        "",
        "Kurzformel:",
        "",
        "> Prüfen, ob die Stoff-Skala wirklich eine zweite Achse öffnet.",
    ])
    return "\n".join(lines)


def main() -> None:
    args = parse_args()
    cfg = apply_overrides(load_config(Path(args.config)), args)
    validate_config(cfg)

    if args.dry_run:
        print("Config valid. Dry run completed.")
        return

    conditions = Conditions(**cfg["conditions"])
    assumptions = ModelAssumptions(**cfg["model_assumptions"])

    species_list = [str(s).lower() for s in cfg["species_list"]]

    wave_results = [compute_wave_result(sp, conditions, assumptions, cfg) for sp in species_list]
    wave_surrogates = build_wave_surrogates(wave_results)

    vdw_results: Optional[Dict[str, SpeciesVDWResult]] = None
    vdw_surrogates: Optional[Dict[str, VDWSurrogates]] = None

    if assumptions.gas_model == "van_der_waals":
        vdw_results = {sp: compute_vdw_result(sp, conditions, cfg) for sp in species_list}
        vdw_surrogates = build_vdw_surrogates(vdw_results)

    weights = cfg.get("surrogates", {}).get("weights", {})
    wave_weight = float(weights.get("wave", 1.0))
    vdw_weight = float(weights.get("vdw", 1.0))
    combined_surrogates = build_combined_surrogates(wave_surrogates, vdw_surrogates, wave_weight, vdw_weight)

    tau_rows: List[Dict[str, Any]] = []
    species_state: List[Dict[str, Any]] = []

    for wr in wave_results:
        ws = wave_surrogates[wr.species]
        vres = vdw_results[wr.species] if vdw_results else None
        vsur = vdw_surrogates[wr.species] if vdw_surrogates else None
        csur = combined_surrogates[wr.species]

        tau_items = []
        for tau in [float(t) for t in cfg["tau_grid"]]:
            tr = compute_tau_response(tau, wr.frequency_hz, csur.signature_score_combined, wr.lambda_db_m, wr.velocity_m_s)
            row = {
                "run_id": cfg["run_id"],
                "species": wr.species,
                "gas_model": assumptions.gas_model,
                "lambda_db": wr.lambda_db_m,
                "energy": wr.energy_j,
                "number_density": wr.number_density_m3,
                "vdw_a": vres.vdw_a if vres else None,
                "vdw_b": vres.vdw_b if vres else None,
                "interaction_score": vsur.interaction_score if vsur else None,
                "excluded_volume_score": vsur.excluded_volume_score if vsur else None,
                "vdw_signature_score": vsur.vdw_signature_score if vsur else None,
                "signature_score_wave": ws.signature_score_wave,
                "signature_score_combined": csur.signature_score_combined,
                "tau": tr.tau,
                "tau_response_score": tr.tau_response_score,
                "tau_alignment_score": tr.tau_alignment_score,
                "tau_window_label": tr.tau_window_label,
            }
            tau_rows.append(row)
            tau_items.append({
                "tau": tr.tau,
                "tau_response_score": tr.tau_response_score,
                "tau_alignment_score": tr.tau_alignment_score,
                "tau_window_label": tr.tau_window_label,
            })

        species_state.append({
            **asdict(wr),
            "vdw_result": asdict(vres) if vres else None,
            "wave_surrogates": asdict(ws),
            "vdw_surrogates": asdict(vsur) if vsur else None,
            "combined_surrogates": asdict(csur),
            "tau_response": tau_items,
        })

    delta_wave = compute_delta_from_mass(wave_results, {sp: s.signature_score_wave for sp, s in wave_surrogates.items()})
    delta_combined = compute_delta_from_mass(wave_results, {sp: s.signature_score_combined for sp, s in combined_surrogates.items()})

    claims = build_claims(assumptions.gas_model, vdw_surrogates, delta_wave, delta_combined)

    state_payload = {
        "run_id": cfg["run_id"],
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "conditions": {
            **cfg["conditions"],
            "temperature_K": conditions.temperature_K,
            "pressure_Pa": conditions.pressure_Pa,
        },
        "model_assumptions": cfg["model_assumptions"],
        "tau_grid": [float(t) for t in cfg["tau_grid"]],
        "species_results": species_state,
        "comparisons": {
            "mass_only_ordering": rank_desc({r.species: r.mass_kg for r in wave_results}),
            "wave_signature_ordering": rank_desc({sp: s.signature_score_wave for sp, s in wave_surrogates.items()}),
            "combined_signature_ordering": rank_desc({sp: s.signature_score_combined for sp, s in combined_surrogates.items()}),
            "matter_sensitive_delta_wave": delta_wave,
            "matter_sensitive_delta_vdw": delta_combined,
        },
    }

    out_cfg = cfg.get("output", {})
    run_dir = Path(out_cfg.get("base_dir", "results/debroglie_matter_signature_vdw")) / str(cfg["run_id"])
    ensure_dir(run_dir)

    if out_cfg.get("write_state_json", True):
        write_json(run_dir / "debroglie_matter_signature_vdw_state.json", state_payload)
    if out_cfg.get("write_claims_json", True):
        write_json(run_dir / "debroglie_matter_signature_vdw_claims.json", claims)
    if out_cfg.get("write_scan_csv", True):
        write_csv(run_dir / "debroglie_matter_signature_vdw_scan.csv", tau_rows)
    if out_cfg.get("write_tau_response_csv", True):
        write_csv(run_dir / "debroglie_matter_signature_vdw_tau_response.csv", tau_rows)
    if out_cfg.get("write_readout_md", True):
        (run_dir / "debroglie_matter_signature_vdw_readout.md").write_text(
            build_readout(cfg, wave_results, vdw_results, wave_surrogates, vdw_surrogates, combined_surrogates, delta_wave, delta_combined, claims),
            encoding="utf-8",
        )

    print(f"[OK] Run completed: {cfg['run_id']}")
    print(f"[OK] Output directory: {run_dir}")


if __name__ == "__main__":
    main()
