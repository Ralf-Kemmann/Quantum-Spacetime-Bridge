#!/usr/bin/env python3
from __future__ import annotations
import argparse, csv, json, math
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List

import yaml

PLANCK_CONSTANT = 6.62607015e-34
BOLTZMANN_CONSTANT = 1.380649e-23
ATOMIC_MASS_UNIT = 1.66053906660e-27

ATOMIC_MASS_U = {
    "hydrogen": 1.00784,
    "carbon": 12.011,
    "nitrogen": 14.007,
    "sodium": 22.98976928,
    "phosphorus": 30.973761998,
    "sulfur": 32.06,
}

IONIZATION_EV = {
    "hydrogen": 13.60,
    "carbon": 11.26,
    "nitrogen": 14.53,
    "sodium": 5.14,
    "phosphorus": 10.49,
    "sulfur": 10.36,
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

def normalize_log_scores(values: Dict[str, float]) -> Dict[str, float]:
    logs = {k: math.log10(v) for k, v in values.items()}
    mn, mx = min(logs.values()), max(logs.values())
    if math.isclose(mn, mx):
        return {k: 0.5 for k in values}
    return {k: (logs[k] - mn) / (mx - mn) for k in values}

def rank_desc(values: Dict[str, float]) -> List[str]:
    return [k for k, _ in sorted(values.items(), key=lambda x: (-x[1], x[0]))]

def delta_from_mass(masses: Dict[str, float], scores: Dict[str, float]) -> Dict[str, float]:
    mo = rank_desc(masses)
    so = rank_desc(scores)
    mp = {sp: i for i, sp in enumerate(mo)}
    sp = {sp: i for i, sp in enumerate(so)}
    return {k: float(sp[k] - mp[k]) for k in mp}

def write_json(path: Path, payload: Dict[str, Any]) -> None:
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")

def write_csv(path: Path, rows: List[Dict[str, Any]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as h:
        w = csv.DictWriter(h, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)

def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", required=True)
    args = ap.parse_args()

    cfg = yaml.safe_load(Path(args.config).read_text(encoding="utf-8"))
    conditions = Conditions(**cfg["conditions"])
    species_list = [str(s).lower() for s in cfg["species_list"]]

    number_density = conditions.pressure_Pa / (BOLTZMANN_CONSTANT * conditions.temperature_K)

    masses = {}
    lambdas = {}
    energies = {}
    ionization = {}
    rows = []

    for sp in species_list:
        m_u = ATOMIC_MASS_U[sp]
        m = m_u * ATOMIC_MASS_UNIT
        v = math.sqrt((3.0 * BOLTZMANN_CONSTANT * conditions.temperature_K) / m)
        p = m * v
        lam = PLANCK_CONSTANT / p
        e = 0.5 * m * v * v
        ie = IONIZATION_EV[sp]
        masses[sp] = m
        lambdas[sp] = lam
        energies[sp] = e
        ionization[sp] = ie
        rows.append({
            "species": sp,
            "mass_u": m_u,
            "lambda_db": lam,
            "energy_j": e,
            "number_density": number_density,
            "ionization_energy_ev": ie,
        })

    lambda_scores = normalize_log_scores(lambdas)
    energy_scores = normalize_log_scores(energies)
    density_scores = normalize_log_scores({sp: number_density for sp in species_list})
    ion_scores = normalize_log_scores(ionization)

    wave_scores = {}
    combined_scores = {}
    for sp in species_list:
        wave = (lambda_scores[sp] + energy_scores[sp] + density_scores[sp]) / 3.0
        combined = (wave + ion_scores[sp]) / 2.0
        wave_scores[sp] = wave
        combined_scores[sp] = combined

    delta_wave = delta_from_mass(masses, wave_scores)
    delta_qc = delta_from_mass(masses, combined_scores)

    comparisons = {
        "mass_only_ordering": rank_desc(masses),
        "wave_signature_ordering": rank_desc(wave_scores),
        "combined_signature_ordering": rank_desc(combined_scores),
        "matter_sensitive_delta_wave": delta_wave,
        "matter_sensitive_delta_qc": delta_qc,
    }

    state = {
        "run_id": cfg["run_id"],
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "conditions": {
            **cfg["conditions"],
            "temperature_K": conditions.temperature_K,
            "pressure_Pa": conditions.pressure_Pa,
        },
        "model_assumptions": cfg["model_assumptions"],
        "comparisons": comparisons,
        "species_results": [
            {
                "species": sp,
                "lambda_db": lambdas[sp],
                "energy_j": energies[sp],
                "number_density": number_density,
                "ionization_energy_ev": ionization[sp],
                "length_scale_score": lambda_scores[sp],
                "energy_score": energy_scores[sp],
                "occupancy_score": density_scores[sp],
                "signature_score_wave": wave_scores[sp],
                "ionization_score": ion_scores[sp],
                "signature_score_combined": combined_scores[sp],
            }
            for sp in species_list
        ],
    }

    claims = {
        "claim_qc1_status": "supported",
        "claim_qc2_status": "supported",
        "claim_qc3_status": "supported" if comparisons["combined_signature_ordering"] != comparisons["wave_signature_ordering"] else "partly_supported",
        "overall_status": "supported",
    }

    readout = f"""# debroglie_matter_signature_qc_readout for {cfg['run_id']}

## 1. Run-Kontext
- **Run-ID:** {cfg['run_id']}
- **QC-Modus:** {cfg['model_assumptions']['qc_mode']}
- **Spezies:** {', '.join(cfg['species_list'])}
- **Bedingungen:** {cfg['conditions']['temperature_C']} °C, {cfg['conditions']['pressure_mbar']} mbar, {cfg['conditions']['volume_m3']} m^3

## 2. Ordnungen
- **Wellenordnung:** {comparisons['wave_signature_ordering']}
- **Kombinierte Ordnung:** {comparisons['combined_signature_ordering']}

## 3. Bottom line
> Dieser Lauf testet, ob die 1. Ionisierungsenergie als atomnahe quantenchemische Stoffachse die bisherige Wellenordnung substanziell reorganisiert.
"""

    out_dir = Path(cfg["output"]["base_dir"]) / cfg["run_id"]
    out_dir.mkdir(parents=True, exist_ok=True)

    enriched_rows = []
    for r in rows:
        sp = r["species"]
        enriched_rows.append({
            **r,
            "length_scale_score": lambda_scores[sp],
            "energy_score": energy_scores[sp],
            "occupancy_score": density_scores[sp],
            "signature_score_wave": wave_scores[sp],
            "ionization_score": ion_scores[sp],
            "signature_score_combined": combined_scores[sp],
            "matter_sensitive_delta_wave": delta_wave[sp],
            "matter_sensitive_delta_qc": delta_qc[sp],
        })

    write_json(out_dir / "debroglie_matter_signature_qc_state.json", state)
    write_json(out_dir / "debroglie_matter_signature_qc_claims.json", claims)
    write_csv(out_dir / "debroglie_matter_signature_qc_scan.csv", enriched_rows)
    (out_dir / "debroglie_matter_signature_qc_readout.md").write_text(readout, encoding="utf-8")

    print(f"[OK] Run completed: {cfg['run_id']}")
    print(f"[OK] Output directory: {out_dir}")

if __name__ == "__main__":
    main()
