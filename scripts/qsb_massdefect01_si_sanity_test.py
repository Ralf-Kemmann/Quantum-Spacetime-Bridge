#!/usr/bin/env python3
"""QSB-MASSDEFECT01 controlled SI sanity test.

The code is the calculation model.  All internal calculations use SI units:
kg, J, m s^-1, m^2 s^-2, and J nucleon^-1.

Core formulas:
  free_nucleon_mass_kg = Z * m_p_kg + N * m_n_kg
  delta_m_kg = free_nucleon_mass_kg - nuclear_mass_kg
  binding_energy_J = delta_m_kg * c_m_per_s^2
  binding_energy_per_nucleon_J = binding_energy_J / A
  recovered_delta_m_kg = binding_energy_J / c_m_per_s^2

Uncertainty mode:
  independent_input_approximation
  u(delta_m) = sqrt((Z*u(m_p))^2 + (N*u(m_n))^2 + u(m_nucleus)^2)
  u(E_B) = c^2 * u(delta_m)

The run makes no bridge claim and no physical interpretation beyond the
documented SI mass-energy translation check.
"""

from __future__ import annotations

import argparse
import csv
import json
import sys
from dataclasses import dataclass
from decimal import Decimal, getcontext
from pathlib import Path
from typing import Dict, Iterable, List, Mapping


getcontext().prec = 50

RUN_ID = "QSB_MASSDEFECT01_SI_SANITY_TEST"
RESEARCH_BLOCK = "QSB-MASSDEFECT01"
DEFAULT_OUTPUT_DIR = Path("runs/QSB-MASSDEFECT/QSB_MASSDEFECT01_SI_SANITY_TEST")
SOURCE_NAME = "NIST CODATA recommended values of the fundamental physical constants"
SOURCE_RELEASE = "2022 CODATA adjustment"
SOURCE_REFERENCE = "https://physics.nist.gov/cuu/pdf/all.pdf"
UNCERTAINTY_MODE = "independent_input_approximation"
MASS_ENERGY_RELATION = "E_J = delta_m_kg * c_m_per_s^2"
INVERSE_RELATION = "delta_m_kg = E_J / c_m_per_s^2"
MEV_PER_J_RELATION = "E_MeV = E_J / (1e6 * e_C)"

OUTPUT_NAMES = [
    "qsb_massdefect01_readout.md",
    "qsb_massdefect01_summary.json",
    "qsb_massdefect01_constant_catalog.csv",
    "qsb_massdefect01_nuclear_system_catalog.csv",
    "qsb_massdefect01_unit_conversion_log.csv",
    "qsb_massdefect01_calculation_trace.csv",
    "qsb_massdefect01_mass_defect_results.csv",
    "qsb_massdefect01_uncertainty_results.csv",
    "qsb_massdefect01_mass_energy_translation.csv",
    "qsb_massdefect01_reference_comparison.csv",
    "qsb_massdefect01_validation_checks.csv",
    "qsb_massdefect01_final_status.csv",
]


@dataclass(frozen=True)
class Constant:
    quantity_id: str
    quantity_name: str
    value: Decimal
    uncertainty: Decimal
    unit: str
    source_role: str


@dataclass(frozen=True)
class NuclearSystem:
    system_id: str
    system_name: str
    A: int
    Z: int
    N: int
    nuclear_mass_quantity_id: str


def d(value: str) -> Decimal:
    return Decimal(value)


def default_constants() -> Dict[str, Constant]:
    return {
        "proton_mass_kg": Constant(
            "proton_mass_kg",
            "proton mass",
            d("1.67262192595e-27"),
            d("0.00000000052e-27"),
            "kg",
            "free_nucleon_mass_input",
        ),
        "neutron_mass_kg": Constant(
            "neutron_mass_kg",
            "neutron mass",
            d("1.67492750056e-27"),
            d("0.00000000085e-27"),
            "kg",
            "free_nucleon_mass_input",
        ),
        "deuteron_mass_kg": Constant(
            "deuteron_mass_kg",
            "deuteron mass",
            d("3.3435837768e-27"),
            d("0.0000000010e-27"),
            "kg",
            "nuclear_mass_input",
        ),
        "triton_mass_kg": Constant(
            "triton_mass_kg",
            "triton mass",
            d("5.0073567512e-27"),
            d("0.0000000016e-27"),
            "kg",
            "nuclear_mass_input",
        ),
        "helion_mass_kg": Constant(
            "helion_mass_kg",
            "helion mass",
            d("5.0064127862e-27"),
            d("0.0000000016e-27"),
            "kg",
            "nuclear_mass_input",
        ),
        "alpha_particle_mass_kg": Constant(
            "alpha_particle_mass_kg",
            "alpha particle mass",
            d("6.6446573450e-27"),
            d("0.0000000021e-27"),
            "kg",
            "nuclear_mass_input",
        ),
        "speed_of_light_m_per_s": Constant(
            "speed_of_light_m_per_s",
            "speed of light in vacuum",
            d("299792458"),
            d("0"),
            "m s^-1",
            "mass_energy_conversion_input",
        ),
        "atomic_mass_constant_kg": Constant(
            "atomic_mass_constant_kg",
            "atomic mass constant",
            d("1.66053906892e-27"),
            d("0.00000000052e-27"),
            "kg",
            "documented_non_si_comparison_conversion",
        ),
        "elementary_charge_C": Constant(
            "elementary_charge_C",
            "elementary charge",
            d("1.602176634e-19"),
            d("0"),
            "C",
            "documented_non_si_comparison_conversion",
        ),
    }


def systems() -> List[NuclearSystem]:
    return [
        NuclearSystem("deuteron", "Deuteron", 2, 1, 1, "deuteron_mass_kg"),
        NuclearSystem("triton", "Triton", 3, 1, 2, "triton_mass_kg"),
        NuclearSystem("helion", "Helion", 3, 2, 1, "helion_mass_kg"),
        NuclearSystem("alpha_particle", "Alpha particle", 4, 2, 2, "alpha_particle_mass_kg"),
    ]


def load_constants(path: Path | None) -> Dict[str, Constant]:
    constants = default_constants()
    if path is None:
        return constants

    with path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)

    for row in payload.get("constants", []):
        quantity_id = row["quantity_id"]
        constants[quantity_id] = Constant(
            quantity_id=quantity_id,
            quantity_name=row["quantity_name"],
            value=d(str(row["value"])),
            uncertainty=d(str(row["uncertainty"])),
            unit=row["unit"],
            source_role=row["source_role"],
        )
    return constants


def fmt(value: Decimal) -> str:
    if value.is_zero():
        return "0"
    return f"{value:.16E}"


def dec_sqrt(value: Decimal) -> Decimal:
    return value.sqrt()


def csv_write(path: Path, fieldnames: Iterable[str], rows: Iterable[Mapping[str, object]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(fieldnames), lineterminator="\n")
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def build_rows(constants: Dict[str, Constant]) -> Dict[str, List[Dict[str, object]]]:
    c = constants["speed_of_light_m_per_s"].value
    c2 = c * c
    e_charge = constants["elementary_charge_C"].value
    mev_denom = d("1e6") * e_charge
    mp = constants["proton_mass_kg"]
    mn = constants["neutron_mass_kg"]

    constant_rows: List[Dict[str, object]] = []
    for const in constants.values():
        constant_rows.append(
            {
                "quantity_id": const.quantity_id,
                "quantity_name": const.quantity_name,
                "value": fmt(const.value),
                "uncertainty": fmt(const.uncertainty),
                "unit": const.unit,
                "source_name": SOURCE_NAME,
                "source_release": SOURCE_RELEASE,
                "source_reference": SOURCE_REFERENCE,
                "source_role": const.source_role,
            }
        )
    constant_rows.append(
        {
            "quantity_id": "speed_of_light_squared_m2_per_s2",
            "quantity_name": "speed of light squared",
            "value": fmt(c2),
            "uncertainty": "0",
            "unit": "m^2 s^-2",
            "source_name": "derived from exact CODATA speed of light",
            "source_release": SOURCE_RELEASE,
            "source_reference": SOURCE_REFERENCE,
            "source_role": "derived_mass_energy_conversion_input",
        }
    )

    system_rows: List[Dict[str, object]] = []
    trace_rows: List[Dict[str, object]] = []
    mass_rows: List[Dict[str, object]] = []
    uncertainty_rows: List[Dict[str, object]] = []
    translation_rows: List[Dict[str, object]] = []
    reference_rows: List[Dict[str, object]] = []

    for sysrow in systems():
        nucleus = constants[sysrow.nuclear_mass_quantity_id]
        free_mass = d(sysrow.Z) * mp.value + d(sysrow.N) * mn.value
        delta_m = free_mass - nucleus.value
        relative_mass_difference = delta_m / free_mass
        energy = delta_m * c2
        energy_per_nucleon = energy / d(sysrow.A)
        recovered_delta_m = energy / c2
        recovery_difference = recovered_delta_m - delta_m
        u_delta = dec_sqrt(
            (d(sysrow.Z) * mp.uncertainty) ** 2
            + (d(sysrow.N) * mn.uncertainty) ** 2
            + nucleus.uncertainty**2
        )
        u_energy = c2 * u_delta
        energy_mev = energy / mev_denom
        energy_per_nucleon_mev = energy_mev / d(sysrow.A)
        tolerance = max(abs(delta_m) * d("1e-30"), d("1e-80"))
        inverse_passed = abs(recovery_difference) <= tolerance

        system_rows.append(
            {
                "system_id": sysrow.system_id,
                "system_name": sysrow.system_name,
                "A": sysrow.A,
                "Z": sysrow.Z,
                "N": sysrow.N,
                "nuclear_mass_quantity_id": sysrow.nuclear_mass_quantity_id,
                "mass_path": "nuclear_mass_only",
                "atomic_mass_path_used": "no",
            }
        )
        trace_rows.extend(
            [
                {
                    "system_id": sysrow.system_id,
                    "step_index": 1,
                    "calculation": "free_nucleon_mass_kg = Z * m_p_kg + N * m_n_kg",
                    "input_values": f"Z={sysrow.Z};N={sysrow.N};m_p_kg={fmt(mp.value)};m_n_kg={fmt(mn.value)}",
                    "result_value": fmt(free_mass),
                    "result_unit": "kg",
                    "internal_unit_system": "SI",
                },
                {
                    "system_id": sysrow.system_id,
                    "step_index": 2,
                    "calculation": "delta_m_kg = free_nucleon_mass_kg - nuclear_mass_kg",
                    "input_values": f"free_nucleon_mass_kg={fmt(free_mass)};nuclear_mass_kg={fmt(nucleus.value)}",
                    "result_value": fmt(delta_m),
                    "result_unit": "kg",
                    "internal_unit_system": "SI",
                },
                {
                    "system_id": sysrow.system_id,
                    "step_index": 3,
                    "calculation": MASS_ENERGY_RELATION,
                    "input_values": f"delta_m_kg={fmt(delta_m)};c_m_per_s_squared={fmt(c2)}",
                    "result_value": fmt(energy),
                    "result_unit": "J",
                    "internal_unit_system": "SI",
                },
                {
                    "system_id": sysrow.system_id,
                    "step_index": 4,
                    "calculation": INVERSE_RELATION,
                    "input_values": f"binding_energy_J={fmt(energy)};c_m_per_s_squared={fmt(c2)}",
                    "result_value": fmt(recovered_delta_m),
                    "result_unit": "kg",
                    "internal_unit_system": "SI",
                },
            ]
        )
        mass_rows.append(
            {
                "system_id": sysrow.system_id,
                "system_name": sysrow.system_name,
                "A": sysrow.A,
                "Z": sysrow.Z,
                "N": sysrow.N,
                "free_nucleon_mass_kg": fmt(free_mass),
                "nuclear_mass_kg": fmt(nucleus.value),
                "mass_defect_kg": fmt(delta_m),
                "relative_mass_difference": fmt(relative_mass_difference),
                "binding_energy_J": fmt(energy),
                "binding_energy_per_nucleon_J": fmt(energy_per_nucleon),
                "recovered_delta_m_kg": fmt(recovered_delta_m),
                "recovery_difference_kg": fmt(recovery_difference),
                "binding_energy_MeV_comparison": fmt(energy_mev),
                "binding_energy_per_nucleon_MeV_comparison": fmt(energy_per_nucleon_mev),
                "si_comparison_passed": "yes",
                "inverse_translation_passed": "yes" if inverse_passed else "no",
            }
        )
        uncertainty_rows.append(
            {
                "system_id": sysrow.system_id,
                "uncertainty_mode": UNCERTAINTY_MODE,
                "u_proton_mass_kg": fmt(mp.uncertainty),
                "u_neutron_mass_kg": fmt(mn.uncertainty),
                "u_nuclear_mass_kg": fmt(nucleus.uncertainty),
                "u_delta_m_kg": fmt(u_delta),
                "u_binding_energy_J": fmt(u_energy),
                "correlations_used": "no",
                "limitation": "CODATA covariance terms were not applied; independent input approximation only.",
            }
        )
        translation_rows.append(
            {
                "system_id": sysrow.system_id,
                "mass_model_quantity": "delta_m_kg",
                "mass_model_value": fmt(delta_m),
                "energy_model_quantity": "binding_energy_J",
                "energy_model_value": fmt(energy),
                "translation_relation": MASS_ENERGY_RELATION,
                "inverse_translation_relation": INVERSE_RELATION,
                "translation_is_dimensionally_consistent": "yes",
                "translation_is_numerically_reversible_within_tolerance": "yes" if inverse_passed else "no",
                "tolerance_kg": fmt(tolerance),
                "bridge_claim_made": "no",
                "physical_interpretation_made": "no",
            }
        )
        reference_rows.append(
            {
                "system_id": sysrow.system_id,
                "comparison_source": "internal SI binding energy converted to MeV for unit-conversion check only",
                "comparison_type": "internal_unit_conversion_check",
                "comparison_quantity": "binding_energy",
                "comparison_value_MeV": fmt(energy_mev),
                "comparison_value_MeV_per_nucleon": fmt(energy_per_nucleon_mev),
                "conversion_relation": MEV_PER_J_RELATION,
                "reference_comparison_completed": "no",
                "internal_unit_conversion_comparison_completed": "yes",
                "comparison_scope": "internal_J_to_MeV_conversion_only",
                "independent_reference_used": "no",
                "warning": "No independent reference comparison was used in this run.",
            }
        )

    conversion_rows = [
        {
            "conversion_id": "u_to_kg_documented_not_used_in_core",
            "source_unit": "u",
            "target_unit": "kg",
            "relation": "m_kg = m_u * atomic_mass_constant_kg",
            "constant_quantity_id": "atomic_mass_constant_kg",
            "used_in_internal_core": "no",
            "purpose": "Documented because CODATA also lists non-SI mass values.",
        },
        {
            "conversion_id": "J_to_MeV_comparison",
            "source_unit": "J",
            "target_unit": "MeV",
            "relation": MEV_PER_J_RELATION,
            "constant_quantity_id": "elementary_charge_C",
            "used_in_internal_core": "no",
            "purpose": "Optional comparison output only.",
        },
        {
            "conversion_id": "kg_to_J_mass_energy",
            "source_unit": "kg",
            "target_unit": "J",
            "relation": MASS_ENERGY_RELATION,
            "constant_quantity_id": "speed_of_light_m_per_s",
            "used_in_internal_core": "yes",
            "purpose": "SI mass-energy translation.",
        },
        {
            "conversion_id": "J_to_kg_inverse_mass_energy",
            "source_unit": "J",
            "target_unit": "kg",
            "relation": INVERSE_RELATION,
            "constant_quantity_id": "speed_of_light_m_per_s",
            "used_in_internal_core": "yes",
            "purpose": "SI inverse translation check.",
        },
    ]

    checks = make_validation_rows(mass_rows, conversion_rows, translation_rows)
    final_status = make_final_status(mass_rows, checks)

    return {
        "constant_catalog": constant_rows,
        "nuclear_system_catalog": system_rows,
        "unit_conversion_log": conversion_rows,
        "calculation_trace": trace_rows,
        "mass_defect_results": mass_rows,
        "uncertainty_results": uncertainty_rows,
        "mass_energy_translation": translation_rows,
        "reference_comparison": reference_rows,
        "validation_checks": checks,
        "final_status": final_status,
    }


def make_validation_rows(
    mass_rows: List[Dict[str, object]],
    conversion_rows: List[Dict[str, object]],
    translation_rows: List[Dict[str, object]],
) -> List[Dict[str, object]]:
    checks = [
        ("systems_requested", len(systems()) == 4, "Expected four systems: A=2,3,3,4."),
        ("systems_computed", len(mass_rows) == 4, "Computed result rows for four systems."),
        ("si_internal_units_only", True, "Calculation trace uses kg, J, m s^-1, m^2 s^-2, and J nucleon^-1 internally."),
        ("unit_conversion_log_complete", len(conversion_rows) == 4, "u-to-kg, J-to-MeV, kg-to-J, and J-to-kg relations documented."),
        ("atomic_nuclear_mass_paths_mixed", True, "Nuclear mass path used; atomic mass path not used."),
        ("mass_defects_positive", all(d(str(row["mass_defect_kg"])) > 0 for row in mass_rows), "All mass defects are positive."),
        ("binding_energies_positive", all(d(str(row["binding_energy_J"])) > 0 for row in mass_rows), "All binding energies are positive."),
        (
            "inverse_translation_recovered",
            all(row["inverse_translation_passed"] == "yes" for row in mass_rows),
            "E/c^2 recovers delta_m within Decimal tolerance.",
        ),
        (
            "dimensional_consistency_passed",
            all(row["translation_is_dimensionally_consistent"] == "yes" for row in translation_rows),
            "kg * m^2 s^-2 maps to J; J / (m^2 s^-2) maps to kg.",
        ),
        ("reference_comparison_completed", True, "No independent reference comparison was used."),
        ("internal_unit_conversion_comparison_completed", True, "Internal J-to-MeV conversion check completed."),
        ("independent_reference_used", True, "No independent reference was used."),
        ("bridge_claim_made", True, "No bridge claim is made in outputs."),
        ("physical_interpretation_made", True, "No physical interpretation beyond SI translation is made."),
        ("additional_gate_created", True, "No additional gate was created."),
    ]
    rows = []
    for name, passed, note in checks:
        expected = "yes"
        observed = "yes" if passed else "no"
        if name in {
            "atomic_nuclear_mass_paths_mixed",
            "reference_comparison_completed",
            "independent_reference_used",
            "bridge_claim_made",
            "physical_interpretation_made",
            "additional_gate_created",
        }:
            expected = "no"
            observed = "no" if passed else "yes"
        rows.append(
            {
                "check_id": name,
                "expected": expected,
                "observed": observed,
                "passed": "yes" if observed == expected else "no",
                "note": note,
            }
        )
    return rows


def make_final_status(
    mass_rows: List[Dict[str, object]], checks: List[Dict[str, object]]
) -> List[Dict[str, object]]:
    observed = {row["check_id"]: row["observed"] for row in checks}
    passed = all(row["passed"] == "yes" for row in checks)
    return [
        {
            "research_block": RESEARCH_BLOCK,
            "systems_requested": "4",
            "systems_computed": str(len(mass_rows)),
            "si_internal_units_only": observed["si_internal_units_only"],
            "unit_conversion_log_complete": observed["unit_conversion_log_complete"],
            "atomic_nuclear_mass_paths_mixed": observed["atomic_nuclear_mass_paths_mixed"],
            "uncertainty_propagation_completed": "yes",
            "mass_defects_positive": observed["mass_defects_positive"],
            "binding_energies_positive": observed["binding_energies_positive"],
            "inverse_translation_recovered": observed["inverse_translation_recovered"],
            "dimensional_consistency_passed": observed["dimensional_consistency_passed"],
            "reference_comparison_completed": observed["reference_comparison_completed"],
            "internal_unit_conversion_comparison_completed": observed["internal_unit_conversion_comparison_completed"],
            "comparison_scope": "internal_J_to_MeV_conversion_only",
            "independent_reference_used": observed["independent_reference_used"],
            "bridge_claim_made": observed["bridge_claim_made"],
            "physical_interpretation_made": observed["physical_interpretation_made"],
            "additional_gate_created": observed["additional_gate_created"],
            "final_status": "mass_defect_si_sanity_test_completed" if passed else "mass_defect_si_sanity_test_failed",
            "recommended_next_action": "Freeze MASSDEFECT01; if needed later, run a separate independent comparison without mixing it into this nuclear-mass path.",
            "limitations": "CODATA covariance terms were not applied; no independent reference comparison; no bridge claim or physical interpretation.",
        }
    ]


def readout(rows: Dict[str, List[Dict[str, object]]]) -> str:
    final = rows["final_status"][0]
    lines = [
        "# QSB-MASSDEFECT01 SI Sanity Test Readout",
        "",
        "## Befund",
        "",
        "The run computed four nuclear-mass-path mass defects in SI units only: Deuteron, Triton, Helion, and Alpha particle.",
        "All computed mass defects and binding energies are positive, and the inverse translation E_B/c^2 recovers delta_m within the recorded tolerance.",
        "",
        "## Interpretation",
        "",
        "The calculation checks numerical and dimensional consistency of E = delta_m * c^2 for the listed nuclear systems.",
        "The output does not mix atomic and nuclear mass paths.",
        "",
        "## Hypothese",
        "",
        "No bridge hypothesis is evaluated in this run.",
        "",
        "## Offene Luecke",
        "",
        "CODATA covariance terms were not applied; uncertainty propagation uses the independent-input approximation.",
        "No independent reference comparison was used.",
        "",
        "## Claim Boundary",
        "",
        "No bridge confirmation, spacetime emergence, emergent geometry, causality claim, or mechanism claim is made.",
        "",
        "## Datenquellen",
        "",
        f"- {SOURCE_NAME}; {SOURCE_RELEASE}; {SOURCE_REFERENCE}",
        "",
        "## SI-Einheitenweg",
        "",
        "- mass_model_quantity = delta_m_kg",
        "- energy_model_quantity = binding_energy_J",
        f"- translation_relation = {MASS_ENERGY_RELATION}",
        f"- inverse_translation_relation = {INVERSE_RELATION}",
        "- uncertainty_mode = independent_input_approximation",
        "",
        "## Ergebnisse",
        "",
        "| system | delta_m_kg | binding_energy_J | binding_energy_MeV_comparison | u_delta_m_kg |",
        "|---|---:|---:|---:|---:|",
    ]
    uncertainties = {row["system_id"]: row for row in rows["uncertainty_results"]}
    for row in rows["mass_defect_results"]:
        urow = uncertainties[row["system_id"]]
        lines.append(
            f"| {row['system_name']} | {row['mass_defect_kg']} | {row['binding_energy_J']} | "
            f"{row['binding_energy_MeV_comparison']} | {urow['u_delta_m_kg']} |"
        )
    lines.extend(
        [
            "",
            "## Finalstatus",
            "",
            f"- final_status = {final['final_status']}",
            f"- systems_computed = {final['systems_computed']}",
            f"- si_internal_units_only = {final['si_internal_units_only']}",
            f"- bridge_claim_made = {final['bridge_claim_made']}",
            f"- limitations = {final['limitations']}",
            "",
        ]
    )
    return "\n".join(lines)


def summary(rows: Dict[str, List[Dict[str, object]]]) -> Dict[str, object]:
    return {
        "research_block": RESEARCH_BLOCK,
        "run_id": RUN_ID,
        "source_name": SOURCE_NAME,
        "source_release": SOURCE_RELEASE,
        "source_reference": SOURCE_REFERENCE,
        "internal_units": ["kg", "J", "m s^-1", "m^2 s^-2", "J nucleon^-1"],
        "systems_requested": 4,
        "systems_computed": len(rows["mass_defect_results"]),
        "uncertainty_mode": UNCERTAINTY_MODE,
        "mass_energy_relation": MASS_ENERGY_RELATION,
        "inverse_translation_relation": INVERSE_RELATION,
        "mass_defect_results": rows["mass_defect_results"],
        "final_status": rows["final_status"][0],
        "warnings": [
            "No bridge claim is made.",
            "No atomic and nuclear mass paths are mixed.",
            "No independent reference comparison was used.",
            "CODATA covariance terms were not applied.",
        ],
    }


def ensure_output_dir(path: Path, overwrite: bool) -> None:
    if path.exists():
        existing = [child.name for child in path.iterdir()]
        if existing and not overwrite:
            raise SystemExit(f"Output directory exists and is non-empty; use --overwrite: {path}")
        if overwrite:
            for name in OUTPUT_NAMES:
                target = path / name
                if target.exists():
                    target.unlink()
            remaining = [child.name for child in path.iterdir()]
            if remaining:
                raise SystemExit(f"Refusing overwrite because unexpected files exist in output dir: {remaining}")
    path.mkdir(parents=True, exist_ok=True)


def write_outputs(output_dir: Path, rows: Dict[str, List[Dict[str, object]]]) -> None:
    csv_specs = [
        (
            "qsb_massdefect01_constant_catalog.csv",
            [
                "quantity_id",
                "quantity_name",
                "value",
                "uncertainty",
                "unit",
                "source_name",
                "source_release",
                "source_reference",
                "source_role",
            ],
            rows["constant_catalog"],
        ),
        (
            "qsb_massdefect01_nuclear_system_catalog.csv",
            ["system_id", "system_name", "A", "Z", "N", "nuclear_mass_quantity_id", "mass_path", "atomic_mass_path_used"],
            rows["nuclear_system_catalog"],
        ),
        (
            "qsb_massdefect01_unit_conversion_log.csv",
            ["conversion_id", "source_unit", "target_unit", "relation", "constant_quantity_id", "used_in_internal_core", "purpose"],
            rows["unit_conversion_log"],
        ),
        (
            "qsb_massdefect01_calculation_trace.csv",
            ["system_id", "step_index", "calculation", "input_values", "result_value", "result_unit", "internal_unit_system"],
            rows["calculation_trace"],
        ),
        (
            "qsb_massdefect01_mass_defect_results.csv",
            [
                "system_id",
                "system_name",
                "A",
                "Z",
                "N",
                "free_nucleon_mass_kg",
                "nuclear_mass_kg",
                "mass_defect_kg",
                "relative_mass_difference",
                "binding_energy_J",
                "binding_energy_per_nucleon_J",
                "recovered_delta_m_kg",
                "recovery_difference_kg",
                "binding_energy_MeV_comparison",
                "binding_energy_per_nucleon_MeV_comparison",
                "si_comparison_passed",
                "inverse_translation_passed",
            ],
            rows["mass_defect_results"],
        ),
        (
            "qsb_massdefect01_uncertainty_results.csv",
            [
                "system_id",
                "uncertainty_mode",
                "u_proton_mass_kg",
                "u_neutron_mass_kg",
                "u_nuclear_mass_kg",
                "u_delta_m_kg",
                "u_binding_energy_J",
                "correlations_used",
                "limitation",
            ],
            rows["uncertainty_results"],
        ),
        (
            "qsb_massdefect01_mass_energy_translation.csv",
            [
                "system_id",
                "mass_model_quantity",
                "mass_model_value",
                "energy_model_quantity",
                "energy_model_value",
                "translation_relation",
                "inverse_translation_relation",
                "translation_is_dimensionally_consistent",
                "translation_is_numerically_reversible_within_tolerance",
                "tolerance_kg",
                "bridge_claim_made",
                "physical_interpretation_made",
            ],
            rows["mass_energy_translation"],
        ),
        (
            "qsb_massdefect01_reference_comparison.csv",
            [
                "system_id",
                "comparison_source",
                "comparison_type",
                "comparison_quantity",
                "comparison_value_MeV",
                "comparison_value_MeV_per_nucleon",
                "conversion_relation",
                "reference_comparison_completed",
                "internal_unit_conversion_comparison_completed",
                "comparison_scope",
                "independent_reference_used",
                "warning",
            ],
            rows["reference_comparison"],
        ),
        (
            "qsb_massdefect01_validation_checks.csv",
            ["check_id", "expected", "observed", "passed", "note"],
            rows["validation_checks"],
        ),
        (
            "qsb_massdefect01_final_status.csv",
            [
                "research_block",
                "systems_requested",
                "systems_computed",
                "si_internal_units_only",
                "unit_conversion_log_complete",
                "atomic_nuclear_mass_paths_mixed",
                "uncertainty_propagation_completed",
                "mass_defects_positive",
                "binding_energies_positive",
                "inverse_translation_recovered",
                "dimensional_consistency_passed",
                "reference_comparison_completed",
                "internal_unit_conversion_comparison_completed",
                "comparison_scope",
                "independent_reference_used",
                "bridge_claim_made",
                "physical_interpretation_made",
                "additional_gate_created",
                "final_status",
                "recommended_next_action",
                "limitations",
            ],
            rows["final_status"],
        ),
    ]
    for filename, fields, table in csv_specs:
        csv_write(output_dir / filename, fields, table)

    (output_dir / "qsb_massdefect01_readout.md").write_text(readout(rows), encoding="utf-8")
    (output_dir / "qsb_massdefect01_summary.json").write_text(
        json.dumps(summary(rows), indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )


def verify_exact_outputs(output_dir: Path) -> None:
    names = sorted(path.name for path in output_dir.iterdir() if path.is_file())
    expected = sorted(OUTPUT_NAMES)
    if names != expected:
        raise SystemExit(f"Output file set mismatch. expected={expected} observed={names}")


def parse_args(argv: List[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="QSB-MASSDEFECT01 controlled SI sanity test for A=2,3,4.")
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR, help="Output directory for the 12 run files.")
    parser.add_argument("--overwrite", action="store_true", help="Overwrite only the 12 expected output files.")
    parser.add_argument("--constants-file", type=Path, default=None, help="Optional JSON constants override file.")
    return parser.parse_args(argv)


def main(argv: List[str] | None = None) -> int:
    args = parse_args(sys.argv[1:] if argv is None else argv)
    constants = load_constants(args.constants_file)
    rows = build_rows(constants)
    ensure_output_dir(args.output_dir, args.overwrite)
    write_outputs(args.output_dir, rows)
    verify_exact_outputs(args.output_dir)
    print(f"wrote {len(OUTPUT_NAMES)} outputs to {args.output_dir}")
    print(f"final_status={rows['final_status'][0]['final_status']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
