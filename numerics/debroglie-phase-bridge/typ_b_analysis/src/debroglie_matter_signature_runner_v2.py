#!/usr/bin/env python3
"""
debroglie_matter_signature_runner_v2.py

Extension of v1 with an explicit frequency_score as a first-class surrogate.
This runner remains conservative: it does not prove a resonance theory, but
tests whether a frequency-based axis adds real differentiation beyond the
de Broglie length scale.
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
    raise SystemExit(
        "PyYAML is required for this runner. Install it in your environment first."
    ) from exc


PLANCK_CONSTANT = 6.62607015e-34
BOLTZMANN_CONSTANT = 1.380649e-23
AVOGADRO_CONSTANT = 6.02214076e23
ATOMIC_MASS_UNIT = 1.66053906660e-27

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
    frequency_score: float
    signature_score: float


@dataclass
class TauResponse:
    tau: float
    tau_alignment_score: float
    tau_response_score: float
    tau_window_label: str


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Compute de Broglie matter signature surrogates with explicit frequency axis."
    )
    parser.add_argument("--config", required=True, help="Path to YAML config.")
    parser.add_argument("--output-dir", help="Override output directory.")
    parser.add_argument("--run-id", help="Override run_id from config.")
    parser.add_argument("--species", nargs="*", help="Override species list.")
    parser.add_argument("--temperature", type=float, help="Override temperature in °C.")
    parser.add_argument("--pressure", type=float, help="Override pressure in mbar.")
    parser.add_argument("--volume", type=float, help="Override volume in m^3.")
    parser.add_argument("--tau-grid", help="Comma-separated tau values.")
    parser.add_argument("--dry-run", action="store_true", help="Validate config only.")
    return parser.parse_args()


def load_config(path: Path) -> Dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        data = yaml.safe_load(handle)
    if not isinstance(data, dict):
        raise ValueError("Config root must be a mapping.")
    return data


def deep_copy_cfg(cfg: Dict[str, Any]) -> Dict[str, Any]:
    return json.loads(json.dumps(cfg))


def apply_overrides(config: Dict[str, Any], args: argparse.Namespace) -> Dict[str, Any]:
    cfg = deep_copy_cfg(config)

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
        cfg["tau_grid"] = [float(x.strip()) for x in args.tau_grid.split(",") if x.strip()]

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

    for tau in cfg["tau_grid"]:
        if float(tau) <= 0:
            raise ValueError("All tau values must be > 0.")

    if float(cond["temperature_C"]) <= -273.15:
        raise ValueError("temperature_C must be above absolute zero.")
    if float(cond["pressure_mbar"]) <= 0:
        raise ValueError("pressure_mbar must be > 0.")
    if float(cond["volume_m3"]) <= 0:
        raise ValueError("volume_m3 must be > 0.")


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
        raise KeyError(f"No atomic mass available for species '{species}'.")
    return ATOMIC_MASS_U[species.lower()]


def compute_number_density(conditions: Conditions, assumptions: ModelAssumptions) -> float:
    if assumptions.gas_model != "ideal_gas":
        raise NotImplementedError(f"Unsupported gas_model: {assumptions.gas_model}")
    return conditions.pressure_Pa / (BOLTZMANN_CONSTANT * conditions.temperature_K)


def compute_characteristic_velocity(mass_kg: float, temperature_K: float, velocity_model: str) -> float:
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
        f = energy_j / PLANCK_CONSTANT
        return f, 2.0 * math.pi * f
    if frequency_mode == "omega_from_v_over_lambda":
        f = velocity_m_s / lambda_db_m
        return f, 2.0 * math.pi * f
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
    particle_count = number_density_m3 * conditions.volume_m3
    velocity = compute_characteristic_velocity(mass_kg, conditions.temperature_K, assumptions.velocity_model)
    momentum = mass_kg * velocity
    lambda_db = PLANCK_CONSTANT / momentum
    k_m_inv = 2.0 * math.pi / lambda_db
    energy_j = 0.5 * mass_kg * velocity * velocity
    frequency_hz, omega_rad_s = compute_frequency_and_omega(
        velocity_m_s=velocity,
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
        velocity_m_s=velocity,
        momentum_kg_m_s=momentum,
        lambda_db_m=lambda_db,
        k_m_inv=k_m_inv,
        omega_rad_s=omega_rad_s,
        frequency_hz=frequency_hz,
        energy_j=energy_j,
    )


def normalize_log_scores(values: Dict[str, float], invert: bool = False) -> Dict[str, float]:
    for key, value in values.items():
        if value <= 0.0 or not math.isfinite(value):
            raise ValueError(f"Invalid normalization input {key}={value}")
    logs = {k: math.log10(v) for k, v in values.items()}
    min_v = min(logs.values())
    max_v = max(logs.values())

    if math.isclose(min_v, max_v):
        out = {k: 0.5 for k in logs}
    else:
        out = {k: (v - min_v) / (max_v - min_v) for k, v in logs.items()}

    if invert:
        out = {k: 1.0 - v for k, v in out.items()}
    return out


def build_surrogates(base_results: List[SpeciesBaseResult], weights: Dict[str, float]) -> Dict[str, SpeciesSurrogates]:
    lambda_map = {r.species: r.lambda_db_m for r in base_results}
    energy_map = {r.species: r.energy_j for r in base_results}
    occupancy_map = {r.species: r.number_density_m3 for r in base_results}
    frequency_map = {}
    for r in base_results:
        if r.frequency_hz is not None and r.frequency_hz > 0:
            frequency_map[r.species] = r.frequency_hz
        else:
            frequency_map[r.species] = 1.0

    length_scores = normalize_log_scores(lambda_map, invert=False)
    energy_scores = normalize_log_scores(energy_map, invert=False)
    occupancy_scores = normalize_log_scores(occupancy_map, invert=False)
    frequency_scores = normalize_log_scores(frequency_map, invert=False)

    enabled = set(weights.get("__enabled__", ["length_scale_score", "energy_score", "occupancy_score", "frequency_score"]))
    wl = float(weights.get("length_scale_score", 1.0)) if "length_scale_score" in enabled else 0.0
    we = float(weights.get("energy_score", 1.0)) if "energy_score" in enabled else 0.0
    wo = float(weights.get("occupancy_score", 1.0)) if "occupancy_score" in enabled else 0.0
    wf = float(weights.get("frequency_score", 1.0)) if "frequency_score" in enabled else 0.0
    denom = wl + we + wo + wf
    if denom <= 0:
        raise ValueError("At least one enabled surrogate must have positive weight.")

    out: Dict[str, SpeciesSurrogates] = {}
    for r in base_results:
        sp = r.species
        signature = (
            wl * length_scores[sp]
            + we * energy_scores[sp]
            + wo * occupancy_scores[sp]
            + wf * frequency_scores[sp]
        ) / denom
        out[sp] = SpeciesSurrogates(
            length_scale_score=length_scores[sp],
            energy_score=energy_scores[sp],
            occupancy_score=occupancy_scores[sp],
            frequency_score=frequency_scores[sp],
            signature_score=signature,
        )
    return out


def compute_tau_alignment_and_response(tau: float, base: SpeciesBaseResult, surrogate: SpeciesSurrogates) -> TauResponse:
    if base.frequency_hz and base.frequency_hz > 0:
        char_time = 1.0 / base.frequency_hz
    else:
        char_time = base.lambda_db_m / base.velocity_m_s

    ratio = tau / char_time
    alignment = max(0.0, 1.0 - abs(math.log10(ratio)) / 3.0)
    alignment = min(1.0, alignment)
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
    return [k for k, _ in sorted(values.items(), key=lambda item: (-item[1], item[0]))]


def compute_matter_sensitive_delta(base_results: List[SpeciesBaseResult], surrogates: Dict[str, SpeciesSurrogates]) -> Dict[str, float]:
    mass_rank = rank_dict_desc({r.species: r.mass_kg for r in base_results})
    sig_rank = rank_dict_desc({sp: s.signature_score for sp, s in surrogates.items()})
    mass_pos = {sp: idx for idx, sp in enumerate(mass_rank)}
    sig_pos = {sp: idx for idx, sp in enumerate(sig_rank)}
    return {sp: float(sig_pos[sp] - mass_pos[sp]) for sp in mass_pos}


def ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def write_json(path: Path, payload: Dict[str, Any]) -> None:
    with path.open("w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2, ensure_ascii=False)


def write_csv(path: Path, rows: List[Dict[str, Any]]) -> None:
    if not rows:
        raise ValueError(f"No rows for CSV: {path}")
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def summarize_claims(base_results: List[SpeciesBaseResult], tau_rows: List[Dict[str, Any]], delta: Dict[str, float]) -> Dict[str, Any]:
    ds2 = False
    by_species: Dict[str, List[float]] = {}
    for row in tau_rows:
        by_species.setdefault(str(row["species"]), []).append(float(row["tau_response_score"]))
    means = {sp: sum(vals) / len(vals) for sp, vals in by_species.items() if vals}
    if len(set(round(v, 12) for v in means.values())) > 1:
        ds2 = True

    max_delta = max(abs(v) for v in delta.values()) if delta else 0.0
    ds3 = max_delta >= 1.0
    near_count = sum(1 for row in tau_rows if str(row["tau_window_label"]) == "near_window")
    ds4 = near_count > 0

    return {
        "claim_ds1_status": "supported",
        "claim_ds2_status": "supported" if ds2 else "partly_supported",
        "claim_ds3_status": "supported" if ds3 else "partly_supported",
        "claim_ds4_status": "supported" if ds4 else "partly_supported",
        "claim_ds5_status": "supported",
        "overall_status": "supported" if ds2 else "partly_supported",
        "notes": {
            "max_matter_sensitive_delta": max_delta,
            "near_window_count": near_count,
        },
    }


def build_readout(
    cfg: Dict[str, Any],
    base_results: List[SpeciesBaseResult],
    surrogates: Dict[str, SpeciesSurrogates],
    tau_rows: List[Dict[str, Any]],
    delta: Dict[str, float],
    claims: Dict[str, Any],
) -> str:
    strongest = max(surrogates.items(), key=lambda item: item[1].signature_score)[0]
    largest_delta_species = max(delta.items(), key=lambda item: abs(item[1]))[0]
    best_tau = None
    near_rows = [r for r in tau_rows if r["tau_window_label"] == "near_window"]
    if near_rows:
        best_tau = max(near_rows, key=lambda r: float(r["tau_response_score"]))

    lines = [
        f"# debroglie_matter_signature_readout for {cfg['run_id']}",
        "",
        "## 1. Run-Kontext",
        f"- **Run-ID:** {cfg['run_id']}",
        f"- **Spezies:** {', '.join(cfg['species_list'])}",
        f"- **Bedingungen:** {cfg['conditions']['temperature_C']} °C, {cfg['conditions']['pressure_mbar']} mbar, {cfg['conditions']['volume_m3']} m^3",
        f"- **Geschwindigkeitsmodell:** {cfg['model_assumptions']['velocity_model']}",
        f"- **Frequenzmodus:** {cfg['model_assumptions']['frequency_mode']}",
        f"- **Tau-Grid:** {cfg['tau_grid']}",
        "",
        "Kurzlesart:",
        "",
        "> Explorationslauf mit explizit aktivierter Frequenz als zweite Signaturachse.",
        "",
        "## 2. Signatur-Surrogate",
    ]

    for base in base_results:
        s = surrogates[base.species]
        lines.extend([
            f"### {base.species}",
            f"- `lambda_db`: {base.lambda_db_m:.6e} m",
            f"- `energy`: {base.energy_j:.6e} J",
            f"- `number_density`: {base.number_density_m3:.6e} 1/m^3",
            f"- `frequency`: {base.frequency_hz:.6e} Hz" if base.frequency_hz is not None else "- `frequency`: null",
            f"- `length_scale_score`: {s.length_scale_score:.6f}",
            f"- `energy_score`: {s.energy_score:.6f}",
            f"- `occupancy_score`: {s.occupancy_score:.6f}",
            f"- `frequency_score`: {s.frequency_score:.6f}",
            f"- `signature_score`: {s.signature_score:.6f}",
            "",
        ])

    lines.extend([
        "## 3. Massen- vs. Materiesensitivität",
        "",
        "Abweichung von bloßer Massenordnung (`matter_sensitive_delta`):",
        "",
    ])
    for species, value in sorted(delta.items()):
        lines.append(f"- `{species}`: {value:+.0f}")

    lines.extend([
        "",
        "## 4. Tau-Fenstervergleich",
        "",
    ])
    if best_tau:
        lines.extend([
            f"- Bester defensiver Fensterkandidat: `{best_tau['species']}` bei `tau = {best_tau['tau']}`",
            f"- `tau_response_score = {float(best_tau['tau_response_score']):.6f}`",
            f"- `tau_window_label = {best_tau['tau_window_label']}`",
        ])
    else:
        lines.append("- Kein starker `near_window`-Kandidat im aktuellen Lauf.")

    lines.extend([
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
        "- Reproduzierbare de-Broglie-bezogene Grundgrößen wurden pro Spezies konstruiert.",
        f"- Die kombinierte Signatur ist im aktuellen Lauf für '{strongest}' am stärksten ausgeprägt.",
        f"- Die stärkste Abweichung von bloßer Massenordnung zeigt '{largest_delta_species}'.",
        "",
        "### Signalhaft, aber noch offen",
        "- Die Frequenzachse ist jetzt explizit aktiviert, muss aber gegen alternative Annahmen weiter geprüft werden.",
        "- Die Tau-Fensterantwort ist weiterhin explorativ und noch nicht als starke Resonanzbehauptung zu lesen.",
        "",
        "### Nicht gestützt oder unklar",
        "- Noch offen ist, ob frequency_score echte Zusatzstruktur bringt oder nur dieselbe Ordnung neu parametrisiert.",
        "- Noch offen ist, wie direkt tau als physikalische Antwort- oder Taktskala interpretiert werden darf.",
        "",
        "## 7. Bottom line",
        "",
        "> Der Lauf testet, ob eine explizit aktivierte Frequenzachse die materialspezifische Signatur verbreitert. Entscheidend ist nun, ob dadurch gegenüber der reinen Längenskalenordnung wirklich neue Struktur entsteht oder nur dieselbe Ordnung in neuer Sprache erscheint.",
        "",
        "Kurzformel:",
        "",
        "> Frequenz ist jetzt im Spiel — jetzt zeigt sich, ob sie wirklich etwas trägt.",
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

    base_results = [
        compute_species_base_result(str(species).lower(), conditions, assumptions, cfg)
        for species in cfg["species_list"]
    ]

    sur_cfg = cfg.get("surrogates", {})
    weights = dict(sur_cfg.get("weights", {}))
    weights["__enabled__"] = sur_cfg.get(
        "enabled",
        ["length_scale_score", "energy_score", "occupancy_score", "frequency_score", "signature_score"],
    )
    surrogates = build_surrogates(base_results, weights)

    tau_rows: List[Dict[str, Any]] = []
    species_results_state: List[Dict[str, Any]] = []

    for base in base_results:
        s = surrogates[base.species]
        tau_items = []
        for tau in [float(x) for x in cfg["tau_grid"]]:
            tr = compute_tau_alignment_and_response(tau, base, s)
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
                "length_scale_score": s.length_scale_score,
                "energy_score": s.energy_score,
                "occupancy_score": s.occupancy_score,
                "frequency_score": s.frequency_score,
                "signature_score": s.signature_score,
                "tau": tr.tau,
                "tau_alignment_score": tr.tau_alignment_score,
                "tau_response_score": tr.tau_response_score,
                "tau_window_label": tr.tau_window_label,
            }
            tau_rows.append(row)
            tau_items.append({
                "tau": tr.tau,
                "tau_alignment_score": tr.tau_alignment_score,
                "tau_response_score": tr.tau_response_score,
                "tau_window_label": tr.tau_window_label,
            })

        species_results_state.append({
            **asdict(base),
            "signature_surrogates": asdict(s),
            "tau_response": tau_items,
        })

    delta = compute_matter_sensitive_delta(base_results, surrogates)
    mass_order = rank_dict_desc({r.species: r.mass_kg for r in base_results})
    signature_order = rank_dict_desc({sp: s.signature_score for sp, s in surrogates.items()})
    claims = summarize_claims(base_results, tau_rows, delta)

    state = {
        "run_id": cfg["run_id"],
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "conditions": {
            **cfg["conditions"],
            "temperature_K": conditions.temperature_K,
            "pressure_Pa": conditions.pressure_Pa,
        },
        "model_assumptions": cfg["model_assumptions"],
        "tau_grid": [float(x) for x in cfg["tau_grid"]],
        "species_results": species_results_state,
        "comparisons": {
            "mass_only_ordering": mass_order,
            "signature_ordering": signature_order,
            "matter_sensitive_delta": delta,
        },
    }

    out_cfg = cfg.get("output", {})
    run_dir = Path(out_cfg.get("base_dir", "results/debroglie_matter_signature")) / str(cfg["run_id"])
    ensure_dir(run_dir)

    if out_cfg.get("write_state_json", True):
        write_json(run_dir / "debroglie_matter_signature_state.json", state)
    if out_cfg.get("write_claims_json", True):
        write_json(run_dir / "debroglie_matter_signature_claims.json", claims)

    mass_rank_pos = {sp: idx + 1 for idx, sp in enumerate(mass_order)}
    sig_rank_pos = {sp: idx + 1 for idx, sp in enumerate(signature_order)}
    csv_rows = []
    for row in tau_rows:
        sp = str(row["species"])
        enriched = dict(row)
        enriched["mass_only_rank"] = mass_rank_pos[sp]
        enriched["matter_sensitive_rank"] = sig_rank_pos[sp]
        enriched["matter_sensitive_delta"] = delta[sp]
        enriched["response_label"] = (
            "nontrivial_candidate"
            if abs(delta[sp]) >= 1.0 and row["tau_window_label"] != "off_window"
            else "mass_like"
        )
        csv_rows.append(enriched)

    if out_cfg.get("write_scan_csv", True):
        write_csv(run_dir / "debroglie_matter_signature_scan.csv", csv_rows)
    if out_cfg.get("write_tau_response_csv", True):
        write_csv(run_dir / "debroglie_matter_signature_tau_response.csv", tau_rows)
    if out_cfg.get("write_readout_md", True):
        (run_dir / "debroglie_matter_signature_readout.md").write_text(
            build_readout(cfg, base_results, surrogates, tau_rows, delta, claims),
            encoding="utf-8",
        )

    print(f"[OK] Run completed: {cfg['run_id']}")
    print(f"[OK] Output directory: {run_dir}")


if __name__ == "__main__":
    main()
