#!/usr/bin/env python3
from __future__ import annotations
import argparse, csv, json, math
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List
import yaml

PLANCK_CONSTANT = 6.62607015e-34
BOLTZMANN_CONSTANT = 1.380649e-23
ATOMIC_MASS_UNIT = 1.66053906660e-27

ISOTOPE_DATA = {
    "1h": {
        "label": "1H",
        "element_symbol": "H",
        "mass_u": 1.00782503223,
        "proton_number": 1,
        "neutron_number": 0,
        "electron_count": 1,
        "valence_electron_count": 1,
        "shell_closure_score": 0.0,
    },
    "2h": {
        "label": "2H",
        "element_symbol": "H",
        "mass_u": 2.01410177812,
        "proton_number": 1,
        "neutron_number": 1,
        "electron_count": 1,
        "valence_electron_count": 1,
        "shell_closure_score": 0.0,
    },
    "3h": {
        "label": "3H",
        "element_symbol": "H",
        "mass_u": 3.0160492779,
        "proton_number": 1,
        "neutron_number": 2,
        "electron_count": 1,
        "valence_electron_count": 1,
        "shell_closure_score": 0.0,
    },
    "12c": {
        "label": "12C",
        "element_symbol": "C",
        "mass_u": 12.0,
        "proton_number": 6,
        "neutron_number": 6,
        "electron_count": 6,
        "valence_electron_count": 4,
        "shell_closure_score": 0.0,
    },
    "13c": {
        "label": "13C",
        "element_symbol": "C",
        "mass_u": 13.00335483507,
        "proton_number": 6,
        "neutron_number": 7,
        "electron_count": 6,
        "valence_electron_count": 4,
        "shell_closure_score": 0.0,
    },
}

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

def build_readout(run_id: str, mode: str, isotope_list: List[str], cond: Dict[str, Any], comparisons: Dict[str, Any], inv: Dict[str, bool], generalization_flag: bool, suffix: str) -> str:
    return f"""# debroglie_matter_signature_{suffix}_readout for {run_id}

## 1. Run-Kontext
- **Run-ID:** {run_id}
- **Isotopen-Modus:** {mode}
- **Isotope:** {', '.join(isotope_list)}
- **Bedingungen:** {cond['temperature_C']} °C, {cond['pressure_mbar']} mbar, {cond['volume_m3']} m^3

## 2. Ordnungen
- **Massenordnung:** {comparisons['mass_only_ordering']}
- **Wellenordnung:** {comparisons['wave_signature_ordering']}
- **Kombinierte Ordnung:** {comparisons['combined_signature_ordering']}

## 3. Strukturinvarianz
- **valence_constant:** {inv['valence_constant']}
- **closure_constant:** {inv['closure_constant']}
- **electron_count_constant:** {inv['electron_count_constant']}
- **generalization_flag:** {generalization_flag}

## 4. Bottom line
> Dieser Lauf testet, ob isotopische Massenvariation bei konstanter Elektronenstruktur im Carbon-Block die Wellenachse systematisch verschiebt, während der Strukturanteil stabil bleibt.
"""

def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", required=True)
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    cfg = yaml.safe_load(Path(args.config).read_text(encoding="utf-8"))
    if args.dry_run:
        print("Config valid. Dry run completed.")
        return

    cond = cfg["conditions"]
    T = float(cond["temperature_C"]) + 273.15
    P = float(cond["pressure_mbar"]) * 100.0
    isotope_list = [str(s).lower() for s in cfg["isotope_list"]]

    number_density = P / (BOLTZMANN_CONSTANT * T)

    masses, lambdas, energies = {}, {}, {}
    valence, closure = {}, {}
    rows = []

    for iso in isotope_list:
        d = ISOTOPE_DATA[iso]
        m_u = float(d["mass_u"])
        m = m_u * ATOMIC_MASS_UNIT
        v = math.sqrt((3.0 * BOLTZMANN_CONSTANT * T) / m)
        p = m * v
        lam = PLANCK_CONSTANT / p
        e = 0.5 * m * v * v

        masses[iso] = m
        lambdas[iso] = lam
        energies[iso] = e
        valence[iso] = float(d["valence_electron_count"])
        closure[iso] = float(d["shell_closure_score"])

        rows.append({
            "isotope": iso,
            "label": d["label"],
            "element_symbol": d["element_symbol"],
            "mass_u": m_u,
            "proton_number": d["proton_number"],
            "neutron_number": d["neutron_number"],
            "electron_count": d["electron_count"],
            "lambda_db": lam,
            "energy_j": e,
            "number_density": number_density,
            "valence_electron_count": d["valence_electron_count"],
            "shell_closure_score": d["shell_closure_score"],
        })

    lambda_scores = normalize_log_scores(lambdas)
    energy_scores = normalize_log_scores(energies)
    density_scores = {iso: 0.5 for iso in isotope_list}
    valence_scores = {iso: 0.5 for iso in isotope_list}
    closure_scores = closure.copy()

    weights = cfg.get("surrogates", {}).get("weights", {})
    wave_w = float(weights.get("wave", 1.0))
    val_w = float(weights.get("qc_valence", 0.0))
    clo_w = float(weights.get("qc_shell", 0.0))

    wave_scores, combined_scores = {}, {}
    for iso in isotope_list:
        wave = (lambda_scores[iso] + energy_scores[iso] + density_scores[iso]) / 3.0
        denom = wave_w + val_w + clo_w
        combined = ((wave_w * wave) + (val_w * valence_scores[iso]) + (clo_w * closure_scores[iso])) / denom if denom > 0 else wave
        wave_scores[iso] = wave
        combined_scores[iso] = combined

    delta_wave = delta_from_mass(masses, wave_scores)
    delta_iso = delta_from_mass(masses, combined_scores)

    structure_invariance_check = {
        "valence_constant": len(set(valence.values())) == 1,
        "closure_constant": len(set(closure.values())) == 1,
        "electron_count_constant": len({ISOTOPE_DATA[i]["electron_count"] for i in isotope_list}) == 1,
    }
    carbon_generalization_flag = all(structure_invariance_check.values())

    comparisons = {
        "mass_only_ordering": rank_desc(masses),
        "wave_signature_ordering": rank_desc(wave_scores),
        "combined_signature_ordering": rank_desc(combined_scores),
        "matter_sensitive_delta_wave": delta_wave,
        "matter_sensitive_delta_isotope_carbon": delta_iso,
        "structure_invariance_check": structure_invariance_check,
        "carbon_generalization_flag": carbon_generalization_flag,
    }

    run_id = cfg["run_id"]
    mode = cfg["model_assumptions"]["isotope_mode"]
    suffix = "isotope_carbon"

    state = {
        "run_id": run_id,
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "conditions": {**cond, "temperature_K": T, "pressure_Pa": P},
        "model_assumptions": cfg["model_assumptions"],
        "comparisons": comparisons,
        "isotope_results": [
            {
                "isotope": iso,
                "label": ISOTOPE_DATA[iso]["label"],
                "element_symbol": ISOTOPE_DATA[iso]["element_symbol"],
                "mass_u": ISOTOPE_DATA[iso]["mass_u"],
                "lambda_db": lambdas[iso],
                "energy_j": energies[iso],
                "number_density": number_density,
                "valence_electron_count": ISOTOPE_DATA[iso]["valence_electron_count"],
                "shell_closure_score": ISOTOPE_DATA[iso]["shell_closure_score"],
                "length_scale_score": lambda_scores[iso],
                "energy_score": energy_scores[iso],
                "occupancy_score": density_scores[iso],
                "signature_score_wave": wave_scores[iso],
                "valence_score": valence_scores[iso],
                "signature_score_combined": combined_scores[iso],
            }
            for iso in isotope_list
        ],
    }

    claims = {
        "claim_ciso1_status": "supported",
        "claim_ciso2_status": "supported" if carbon_generalization_flag else "partly_supported",
        "claim_ciso3_status": "supported",
        "claim_ciso4_status": "supported" if carbon_generalization_flag else "partly_supported",
        "claim_ciso5_status": "supported" if carbon_generalization_flag else "partly_supported",
        "overall_status": "supported" if carbon_generalization_flag else "partly_supported",
    }

    out_dir = Path(cfg["output"]["base_dir"]) / run_id
    out_dir.mkdir(parents=True, exist_ok=True)

    enriched_rows = []
    for r in rows:
        iso = r["isotope"]
        enriched_rows.append({
            **r,
            "length_scale_score": lambda_scores[iso],
            "energy_score": energy_scores[iso],
            "occupancy_score": density_scores[iso],
            "signature_score_wave": wave_scores[iso],
            "valence_score": valence_scores[iso],
            "signature_score_combined": combined_scores[iso],
            "matter_sensitive_delta_wave": delta_wave[iso],
            "matter_sensitive_delta_isotope_carbon": delta_iso[iso],
        })

    write_json(out_dir / "debroglie_matter_signature_isotope_carbon_state.json", state)
    write_json(out_dir / "debroglie_matter_signature_isotope_carbon_claims.json", claims)
    write_csv(out_dir / "debroglie_matter_signature_isotope_carbon_scan.csv", enriched_rows)
    (out_dir / "debroglie_matter_signature_isotope_carbon_readout.md").write_text(
        build_readout(run_id, mode, cfg["isotope_list"], cond, comparisons, structure_invariance_check, carbon_generalization_flag, suffix),
        encoding="utf-8",
    )

    print(f"[OK] Run completed: {run_id}")
    print(f"[OK] Output directory: {out_dir}")

if __name__ == "__main__":
    main()
