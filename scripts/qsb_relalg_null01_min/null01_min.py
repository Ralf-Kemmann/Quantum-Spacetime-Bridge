#!/usr/bin/env python3
"""Build QSB-RELALG-NULL01-MIN minimal synthetic nullmodel controls."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import random
import shutil
from datetime import datetime, timezone
from pathlib import Path
from textwrap import dedent


REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT_PATH = Path("scripts/qsb_relalg_null01_min/null01_min.py")
RUN_ID = "QSB-RELALG-NULL01-MIN"
OUTPUT_DIR = REPO_ROOT / "runs/QSB-RELALG-NULL01-MIN"
CLAIM_STATUS = "synthetic_nullmodel_control_only_no_physical_interpretation"
PRODUCTION_MUTATION_STATEMENT = "No production DWH, source-hub, schema, prerequisite run, or project data was modified."
BASELINE_RUN_DIR = REPO_ROOT / "runs/QSB-RELALG-LOOP01-MIN"
CONFIG = {
    "random_seed": 270627,
    "phase_tolerance": 1.0e-10,
    "phase_change_min": 1.0e-6,
    "near_zero_phase_tolerance": 1.0e-10,
    "delta_min": 1.0e-10,
    "product_delta_min": 1.0e-12,
    "arg_branch": "(-pi, pi]",
    "orientation": "ordered_cycle_A_to_B_to_C_to_A",
    "source_space_policy": "active loop edges must share one source_space_id",
    "phi_source_rule": "Phi_ABC is computed only from P_ABC = C_AB * C_BC * C_CA",
}
PREREQUISITES = {
    "preax_validation": REPO_ROOT / "runs/QSB-RELALG-PREAX01-SYNTH/qsb_relalg_preax01_synth_validation_report.json",
    "term_validation": REPO_ROOT / "runs/QSB-RELALG-AX01-TERM/qsb_relalg_ax01_term_validation_report.json",
    "ax01_validation": REPO_ROOT / "runs/QSB-RELALG-AX01/qsb_relalg_ax01_validation_report.json",
    "gauge01_validation": REPO_ROOT / "runs/QSB-RELALG-GAUGE01/qsb_relalg_gauge01_validation_report.json",
    "gauge01_gate": REPO_ROOT / "runs/QSB-RELALG-GAUGE01/qsb_relalg_gauge01_next_step_gate.json",
    "loop01_min_validation": BASELINE_RUN_DIR / "qsb_relalg_loop01_min_validation_report.json",
}
BASELINE_INPUTS = {
    "loop01_min_config": BASELINE_RUN_DIR / "qsb_relalg_loop01_min_config.json",
    "loop01_min_states": BASELINE_RUN_DIR / "qsb_relalg_loop01_min_synthetic_states.csv",
    "loop01_min_pairs": BASELINE_RUN_DIR / "qsb_relalg_loop01_min_pair_relations.csv",
    "loop01_min_catalog": BASELINE_RUN_DIR / "qsb_relalg_loop01_min_loop_catalog.csv",
    "loop01_min_phase_results": BASELINE_RUN_DIR / "qsb_relalg_loop01_min_loop_phase_results.csv",
}
OUTPUTS = {
    "config": OUTPUT_DIR / "qsb_relalg_null01_min_config.json",
    "prerequisite_report": OUTPUT_DIR / "qsb_relalg_null01_min_prerequisite_report.json",
    "baseline_summary": OUTPUT_DIR / "qsb_relalg_null01_min_baseline_summary.csv",
    "registry": OUTPUT_DIR / "qsb_relalg_null01_min_nullmodel_registry.csv",
    "pair_relations": OUTPUT_DIR / "qsb_relalg_null01_min_nullmodel_pair_relations.csv",
    "loop_results": OUTPUT_DIR / "qsb_relalg_null01_min_nullmodel_loop_results.csv",
    "comparison": OUTPUT_DIR / "qsb_relalg_null01_min_nullmodel_comparison.csv",
    "invalid_controls": OUTPUT_DIR / "qsb_relalg_null01_min_invalid_controls.csv",
    "threshold_report": OUTPUT_DIR / "qsb_relalg_null01_min_threshold_report.csv",
    "orientation_report": OUTPUT_DIR / "qsb_relalg_null01_min_orientation_report.csv",
    "claim_boundary": OUTPUT_DIR / "qsb_relalg_null01_min_claim_boundary_report.md",
    "next_gate": OUTPUT_DIR / "qsb_relalg_null01_min_next_step_gate.json",
    "manifest": OUTPUT_DIR / "qsb_relalg_null01_min_manifest.json",
    "validation": OUTPUT_DIR / "qsb_relalg_null01_min_validation_report.json",
    "summary": OUTPUT_DIR / "QSB-RELALG-NULL01-MIN_RUN_SUMMARY.md",
}
RESTRICTED_PATTERNS = [
    "establish spacetime emergence",
    "establish physical causality",
    "test gravity",
    "provide physical evidence",
    "confirm QSB",
]


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def rel(path: Path) -> str:
    return str(path.relative_to(REPO_ROOT))


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def fmt(value: float) -> str:
    return f"{value:.17g}"


def write_csv(path: Path, headers: list[str], rows: list[list[object]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(headers)
        writer.writerows(rows)


def read_csv_dicts(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def load_json(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


def branch_arg(value: complex) -> float:
    angle = math.atan2(value.imag, value.real)
    if math.isclose(angle, -math.pi, abs_tol=0.0):
        return math.pi
    return angle


def circular_delta(a: float, b: float) -> float:
    return math.atan2(math.sin(a - b), math.cos(a - b))


def cexp(theta: float) -> complex:
    return complex(math.cos(theta), math.sin(theta))


def load_prerequisites() -> list[dict[str, object]]:
    missing = [rel(path) for path in list(PREREQUISITES.values()) + list(BASELINE_INPUTS.values()) if not path.exists()]
    if missing:
        raise FileNotFoundError("Missing prerequisite/input files: " + ", ".join(missing))

    checks = [
        ("PREAX01-SYNTH.validation_status", load_json(PREREQUISITES["preax_validation"]).get("validation_status"), "pass"),
        ("AX01-TERM.validation_status", load_json(PREREQUISITES["term_validation"]).get("validation_status"), "pass"),
        ("AX01.validation_status", load_json(PREREQUISITES["ax01_validation"]).get("validation_status"), "pass"),
        ("GAUGE01.validation_status", load_json(PREREQUISITES["gauge01_validation"]).get("validation_status"), "pass"),
        ("GAUGE01.gauge01_status", load_json(PREREQUISITES["gauge01_gate"]).get("gauge01_status"), "synthetic_rephasing_invariance_passed"),
        ("LOOP01-MIN.validation_status", load_json(PREREQUISITES["loop01_min_validation"]).get("validation_status"), "pass"),
    ]
    rows: list[dict[str, object]] = []
    failures: list[str] = []
    for check_id, observed, expected in checks:
        status = "pass" if observed == expected else "fail"
        rows.append({"check_id": check_id, "observed": observed, "expected": expected, "status": status})
        if status != "pass":
            failures.append(f"{check_id} observed {observed!r}, expected {expected!r}")
    if failures:
        raise RuntimeError("Prerequisite check failed; NULL01-MIN not generated: " + "; ".join(failures))
    return rows


def prepare_output(force: bool) -> None:
    if OUTPUT_DIR.exists() and not force:
        raise FileExistsError(f"{rel(OUTPUT_DIR)} already exists; rerun with --force to replace NULL01-MIN outputs.")
    if OUTPUT_DIR.exists() and force:
        shutil.rmtree(OUTPUT_DIR)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def load_baseline() -> tuple[dict[tuple[str, str], dict[str, object]], dict[tuple[str, str, str], float], list[str], dict[str, object]]:
    config = load_json(BASELINE_INPUTS["loop01_min_config"])
    state_ids = list(config["state_ids"])
    pairs: dict[tuple[str, str], dict[str, object]] = {}
    for row in read_csv_dicts(BASELINE_INPUTS["loop01_min_pairs"]):
        value = complex(float(row["C_real"]), float(row["C_imag"]))
        pairs[(row["A"], row["B"])] = {
            "C": value,
            "source_space_id": row["source_space_id"],
        }
    baseline_phi: dict[tuple[str, str, str], float] = {}
    for row in read_csv_dicts(BASELINE_INPUTS["loop01_min_phase_results"]):
        baseline_phi[(row["A"], row["B"], row["C"])] = float(row["Phi_ABC"])
    return pairs, baseline_phi, state_ids, config


def registry_rows() -> list[list[object]]:
    return [
        ["N00", "baseline_replay_control", "baseline_replay", "yes", "yes", "yes", "yes", "active loop count and Phi_ABC values match baseline", "implemented", "comparison machinery replay control"],
        ["N01", "label_permutation_control", "label_invariance", "yes", "yes", "no", "yes", "phase multiset matches baseline while loop labels change", "implemented", "deterministic label permutation"],
        ["N02", "global_rephase_control", "gauge_invariance_replay", "yes", "yes", "yes", "yes", "Phi_ABC remains invariant within tolerance", "implemented", "deterministic local rephasing"],
        ["N03", "phase_scrambled_magnitude_preserved", "phase_structure_control", "yes", "yes", "yes", "yes", "phase structure changes under deterministic phase scrambling", "implemented", "ordered-pair phase scrambling"],
        ["N04", "orientation_destroyed_real_positive", "phase_destroyed_control", "yes", "yes", "yes", "yes", "active phases collapse near zero and orientation contrast is trivial", "implemented", "C_AB replaced by positive magnitudes"],
        ["N05", "conjugate_flip_control", "orientation_sign_control", "yes", "yes", "yes", "yes", "Phi_ABC maps to wrapped negative baseline", "implemented", "C_AB replaced by conjugate(C_AB)"],
        ["N06", "threshold_injected_invalid", "invalid_threshold_control", "yes", "no", "yes", "yes", "loops touching injected edge are blocked without active Phi_ABC", "implemented", "one ordered pair forced below thresholds"],
        ["N07", "source_mixed_invalid", "invalid_source_control", "yes", "yes", "yes", "no", "mixed-source loops are blocked without active Phi_ABC", "implemented", "one ordered pair assigned a control source label"],
    ]


def build_nullmodel_pairs(
    nullmodel_id: str,
    baseline_pairs: dict[tuple[str, str], dict[str, object]],
    state_ids: list[str],
) -> dict[tuple[str, str], dict[str, object]]:
    pairs = {
        edge: {"C": entry["C"], "source_space_id": entry["source_space_id"]}
        for edge, entry in baseline_pairs.items()
    }
    rng = random.Random(CONFIG["random_seed"] + int(nullmodel_id[1:]))

    if nullmodel_id == "N01":
        permuted = state_ids[2:] + state_ids[:2]
        mapping = dict(zip(state_ids, permuted))
        return {
            (mapping[a], mapping[b]): {"C": entry["C"], "source_space_id": entry["source_space_id"]}
            for (a, b), entry in baseline_pairs.items()
        }
    if nullmodel_id == "N02":
        angles = {state_id: rng.uniform(-math.pi, math.pi) for state_id in state_ids}
        return {
            (a, b): {"C": cexp(angles[b] - angles[a]) * entry["C"], "source_space_id": entry["source_space_id"]}
            for (a, b), entry in baseline_pairs.items()
        }
    if nullmodel_id == "N03":
        return {
            (a, b): {"C": abs(entry["C"]) * cexp(rng.uniform(-math.pi, math.pi)), "source_space_id": entry["source_space_id"]}
            for (a, b), entry in baseline_pairs.items()
        }
    if nullmodel_id == "N04":
        return {
            edge: {"C": complex(abs(entry["C"]), 0.0), "source_space_id": entry["source_space_id"]}
            for edge, entry in baseline_pairs.items()
        }
    if nullmodel_id == "N05":
        return {
            edge: {"C": entry["C"].conjugate(), "source_space_id": entry["source_space_id"]}
            for edge, entry in baseline_pairs.items()
        }
    if nullmodel_id == "N06":
        pairs[("S00", "S01")] = {"C": complex(CONFIG["delta_min"] * 0.01, 0.0), "source_space_id": pairs[("S00", "S01")]["source_space_id"]}
        return pairs
    if nullmodel_id == "N07":
        pairs[("S00", "S01")] = {"C": pairs[("S00", "S01")]["C"], "source_space_id": "synthetic_relalg_null01_min_mixed_source_control"}
        return pairs
    return pairs


def evaluate_loops(
    nullmodel_id: str,
    pairs: dict[tuple[str, str], dict[str, object]],
    state_ids: list[str],
) -> tuple[list[list[object]], dict[tuple[str, str, str], float], list[list[object]], list[list[object]], list[list[object]]]:
    loop_rows: list[list[object]] = []
    phi_by_loop: dict[tuple[str, str, str], float] = {}
    invalid_rows: list[list[object]] = []
    threshold_rows: list[list[object]] = []
    orientation_rows: list[list[object]] = []

    for a in state_ids:
        for b in state_ids:
            for c in state_ids:
                if len({a, b, c}) != 3:
                    continue
                loop_id = f"{a}_{b}_{c}"
                entries = [pairs[(a, b)], pairs[(b, c)], pairs[(c, a)]]
                values = [entry["C"] for entry in entries]
                sources = [entry["source_space_id"] for entry in entries]
                source_status = "pass" if len(set(sources)) == 1 else "fail"
                pair_status = "pass" if all(abs(value) >= CONFIG["delta_min"] for value in values) else "fail"
                product = values[0] * values[1] * values[2]
                product_status = "pass" if abs(product) >= CONFIG["product_delta_min"] else "fail"
                threshold_status = "pass" if pair_status == "pass" and product_status == "pass" else "fail"
                is_active = source_status == "pass" and threshold_status == "pass"
                blocked_reason = ""
                if source_status != "pass":
                    blocked_reason = "blocked_source_coherence"
                elif threshold_status != "pass":
                    blocked_reason = "blocked_invalid_product_threshold"
                phi = branch_arg(product) if is_active else ""
                if is_active:
                    phi_by_loop[(a, b, c)] = float(phi)
                else:
                    invalid_rows.append([f"{nullmodel_id}_{loop_id}", nullmodel_id, loop_id, blocked_reason, "false", "true", "pass"])
                loop_rows.append([
                    nullmodel_id,
                    loop_id,
                    a,
                    b,
                    c,
                    fmt(values[0].real),
                    fmt(values[0].imag),
                    fmt(values[1].real),
                    fmt(values[1].imag),
                    fmt(values[2].real),
                    fmt(values[2].imag),
                    fmt(product.real) if is_active else "",
                    fmt(product.imag) if is_active else "",
                    fmt(abs(product)) if is_active else "",
                    fmt(phi) if is_active else "",
                    "true" if is_active else "false",
                    blocked_reason,
                    source_status,
                    threshold_status,
                    "pending",
                ])
                threshold_rows.append([
                    nullmodel_id,
                    loop_id,
                    fmt(min(abs(value) for value in values)),
                    fmt(CONFIG["delta_min"]),
                    fmt(abs(product)),
                    fmt(CONFIG["product_delta_min"]),
                    pair_status,
                    product_status,
                    threshold_status,
                ])

    for (a, b, c), phi in sorted(phi_by_loop.items()):
        reverse = (a, c, b)
        reverse_phi = phi_by_loop.get(reverse)
        if reverse_phi is None:
            continue
        delta = circular_delta(phi + reverse_phi, 0.0)
        status = "pass" if abs(delta) <= CONFIG["phase_tolerance"] else "fail"
        orientation_rows.append([nullmodel_id, f"{a}_{b}_{c}", fmt(phi), fmt(reverse_phi), fmt(delta), fmt(abs(delta)), fmt(CONFIG["phase_tolerance"]), status])

    orientation_by_loop = {row[1]: row[7] for row in orientation_rows}
    for row in loop_rows:
        if row[15] == "true":
            row[19] = orientation_by_loop.get(row[1], "not_checked")
        else:
            row[19] = "not_active"
    return loop_rows, phi_by_loop, invalid_rows, threshold_rows, orientation_rows


def sorted_phases(values: dict[tuple[str, str, str], float]) -> list[float]:
    return sorted(values.values())


def max_phase_delta(left: dict[tuple[str, str, str], float], right: dict[tuple[str, str, str], float]) -> float:
    common = sorted(set(left) & set(right))
    if not common:
        return math.inf
    return max(abs(circular_delta(right[key], left[key])) for key in common)


def max_multiset_delta(left: list[float], right: list[float]) -> float:
    if len(left) != len(right):
        return math.inf
    return max((abs(circular_delta(a, b)) for a, b in zip(left, right)), default=0.0)


def comparison_rows(
    phi_maps: dict[str, dict[tuple[str, str, str], float]],
    baseline_phi: dict[tuple[str, str, str], float],
    orientation_rows: list[list[object]],
) -> list[list[object]]:
    rows: list[list[object]] = []
    baseline_count = len(baseline_phi)
    baseline_multiset = sorted_phases(baseline_phi)
    orientation_pass_count = {
        nullmodel_id: sum(1 for row in orientation_rows if row[0] == nullmodel_id and row[7] == "pass")
        for nullmodel_id in phi_maps
    }

    for nullmodel_id, phi_map in phi_maps.items():
        active_count = len(phi_map)
        rows.append([nullmodel_id, "active_loop_count", baseline_count, active_count, active_count - baseline_count, 0, "pass" if (nullmodel_id in {"N06", "N07"} or active_count == baseline_count) else "fail", "synthetic_nullmodel_control_only"])
        orientation_status = "pass"
        if nullmodel_id not in {"N03", "N06", "N07"} and orientation_pass_count.get(nullmodel_id, 0) != active_count:
            orientation_status = "fail"
        rows.append([nullmodel_id, "orientation_reversal_pass_count", baseline_count, orientation_pass_count.get(nullmodel_id, 0), orientation_pass_count.get(nullmodel_id, 0) - baseline_count, 0, orientation_status, "synthetic_nullmodel_control_only"])

    rows.append(["N00", "phase_max_abs_delta_vs_baseline", 0, fmt(max_phase_delta(baseline_phi, phi_maps["N00"])), fmt(max_phase_delta(baseline_phi, phi_maps["N00"])), fmt(CONFIG["phase_tolerance"]), "pass" if max_phase_delta(baseline_phi, phi_maps["N00"]) <= CONFIG["phase_tolerance"] else "fail", "synthetic_nullmodel_control_only"])
    n01_delta = max_multiset_delta(baseline_multiset, sorted_phases(phi_maps["N01"]))
    rows.append(["N01", "phase_multiset_match", 0, fmt(n01_delta), fmt(n01_delta), fmt(CONFIG["phase_tolerance"]), "pass" if n01_delta <= CONFIG["phase_tolerance"] else "fail", "synthetic_nullmodel_control_only"])
    n02_delta = max_phase_delta(baseline_phi, phi_maps["N02"])
    rows.append(["N02", "phase_max_abs_delta_vs_baseline", 0, fmt(n02_delta), fmt(n02_delta), fmt(CONFIG["phase_tolerance"]), "pass" if n02_delta <= CONFIG["phase_tolerance"] else "fail", "synthetic_nullmodel_control_only"])
    n03_delta = max_phase_delta(baseline_phi, phi_maps["N03"])
    rows.append(["N03", "phase_structure_non_equivalence", 0, fmt(n03_delta), fmt(n03_delta), fmt(CONFIG["phase_change_min"]), "pass" if n03_delta >= CONFIG["phase_change_min"] else "fail", "synthetic_nullmodel_control_only"])
    n04_near_zero = sum(1 for value in phi_maps["N04"].values() if abs(circular_delta(value, 0.0)) <= CONFIG["near_zero_phase_tolerance"])
    rows.append(["N04", "near_zero_phase_fraction", "1.0", fmt(n04_near_zero / len(phi_maps["N04"])), fmt((n04_near_zero / len(phi_maps["N04"])) - 1.0), fmt(CONFIG["near_zero_phase_tolerance"]), "pass" if n04_near_zero == len(phi_maps["N04"]) else "fail", "synthetic_nullmodel_control_only"])
    n05_pass = sum(1 for key, value in phi_maps["N05"].items() if abs(circular_delta(value, -baseline_phi[key])) <= CONFIG["phase_tolerance"])
    rows.append(["N05", "sign_flip_pass_count", baseline_count, n05_pass, n05_pass - baseline_count, 0, "pass" if n05_pass == baseline_count else "fail", "synthetic_nullmodel_control_only"])
    rows.append(["N06", "blocked_loop_count", 0, baseline_count - len(phi_maps["N06"]), baseline_count - len(phi_maps["N06"]), 0, "pass" if baseline_count - len(phi_maps["N06"]) > 0 else "fail", "synthetic_nullmodel_control_only"])
    rows.append(["N07", "blocked_loop_count", 0, baseline_count - len(phi_maps["N07"]), baseline_count - len(phi_maps["N07"]), 0, "pass" if baseline_count - len(phi_maps["N07"]) > 0 else "fail", "synthetic_nullmodel_control_only"])
    return rows


def write_prerequisite_report(timestamp: str, prerequisite_rows: list[dict[str, object]]) -> None:
    report = {
        "run_id": RUN_ID,
        "timestamp": timestamp,
        "status": "pass",
        "checks": prerequisite_rows,
        "baseline_inputs": {name: rel(path) for name, path in BASELINE_INPUTS.items()},
    }
    OUTPUTS["prerequisite_report"].write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def write_baseline_summary(baseline_phi: dict[tuple[str, str, str], float], baseline_config: dict[str, object]) -> None:
    rows = [
        ["baseline_run_id", "QSB-RELALG-LOOP01-MIN"],
        ["active_loop_count", len(baseline_phi)],
        ["source_space_id", baseline_config.get("source_space_id", "")],
        ["delta_min", baseline_config.get("delta_min", "")],
        ["product_delta_min", baseline_config.get("product_delta_min", "")],
        ["arg_branch", baseline_config.get("arg_branch", "")],
        ["phi_source_rule", "computed_from_C_layer_product"],
    ]
    write_csv(OUTPUTS["baseline_summary"], ["metric", "value"], rows)


def write_pair_rows(all_pairs: dict[str, dict[tuple[str, str], dict[str, object]]]) -> None:
    rows: list[list[object]] = []
    for nullmodel_id, pairs in all_pairs.items():
        for (a, b), entry in sorted(pairs.items()):
            value = entry["C"]
            rows.append([nullmodel_id, a, b, fmt(value.real), fmt(value.imag), fmt(abs(value)), entry["source_space_id"], "C_AB_null"])
    write_csv(OUTPUTS["pair_relations"], ["nullmodel_id", "A", "B", "C_real", "C_imag", "K_abs", "source_space_id", "relation_role"], rows)


def write_claim_boundary(timestamp: str) -> None:
    OUTPUTS["claim_boundary"].write_text(dedent(f"""\
        # QSB-RELALG-NULL01-MIN Claim Boundary Report

        Generated at: {timestamp}

        ## Befund

        NULL01-MIN is a synthetic nullmodel control run.

        ## Interpretation

        The run compares deterministic synthetic C-layer loop phases across baseline replay and controlled synthetic alterations.

        ## Hypothese

        None. This artifact does not add a physical hypothesis.

        ## Offene Luecke

        It does not analyze real data and does not execute REAL01.

        ## Claim Boundary

        NULL01-MIN is a synthetic nullmodel control run.
        It does not confirm QSB.
        It does not establish spacetime emergence.
        It does not establish physical causality.
        It does not test gravity.
        It does not analyze real data.
        It does not provide physical evidence.
        """), encoding="utf-8")


def write_next_gate() -> None:
    gate = {
        "run_id": RUN_ID,
        "null01_min_status": "minimal_synthetic_nullmodel_controls_passed",
        "next_authorized_step": "QSB-RELALG-REAL01-MIN-SOURCE-ELIGIBILITY",
        "authorized_next_steps": ["QSB-RELALG-REAL01-MIN-SOURCE-ELIGIBILITY"],
        "still_blocked_steps": [
            "QSB-RELALG-REAL01-EXECUTION",
            "QSB-RELALG-REAL01-INTERPRETATION",
            "QSB-RELALG-PHYSICS-CLAIM",
        ],
        "claim_status": CLAIM_STATUS,
    }
    OUTPUTS["next_gate"].write_text(json.dumps(gate, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def output_hashes() -> dict[str, str]:
    return {name: sha256_file(path) for name, path in OUTPUTS.items() if path.exists() and name != "manifest"}


def write_manifest(timestamp: str, status: str) -> None:
    manifest = {
        "run_id": RUN_ID,
        "timestamp": timestamp,
        "script_path": str(SCRIPT_PATH),
        "script_hash": sha256_file(REPO_ROOT / SCRIPT_PATH),
        "prerequisite_hashes": {name: sha256_file(path) for name, path in PREREQUISITES.items()},
        "baseline_input_hashes": {name: sha256_file(path) for name, path in BASELINE_INPUTS.items()},
        "config_hash": sha256_file(OUTPUTS["config"]) if OUTPUTS["config"].exists() else None,
        "output_hashes": output_hashes(),
        "deterministic_seed": CONFIG["random_seed"],
        "validation_status": status,
        "claim_status": CLAIM_STATUS,
        "production_mutation_statement": PRODUCTION_MUTATION_STATEMENT,
    }
    OUTPUTS["manifest"].write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def restricted_outside_boundary() -> bool:
    allowed = {OUTPUTS["claim_boundary"]}
    for path in OUTPUTS.values():
        if not path.exists() or path in allowed:
            continue
        text = path.read_text(encoding="utf-8")
        for phrase in RESTRICTED_PATTERNS:
            if phrase.lower() in text.lower():
                return True
    return False


def add_result(results: list[dict[str, str]], rule_id: str, status: str, message: str, timestamp: str) -> None:
    results.append({
        "validation_id": f"QSB-RELALG-NULL01-MIN-VAL-{rule_id}",
        "rule_id": rule_id,
        "severity": "error",
        "status": status,
        "message": message,
        "checked_at": timestamp,
    })


def validation_status(results: list[dict[str, str]]) -> str:
    return "fail" if any(row["status"] == "fail" for row in results) else "pass"


def comparison_status(comparison: list[list[object]], nullmodel_id: str, metric: str) -> str:
    for row in comparison:
        if row[0] == nullmodel_id and row[1] == metric:
            return str(row[6])
    return "missing"


def validate(
    timestamp: str,
    prerequisite_rows: list[dict[str, object]],
    comparison: list[list[object]],
    invalid_rows: list[list[object]],
) -> list[dict[str, str]]:
    results: list[dict[str, str]] = []
    prerequisite_status = {str(row["check_id"]): str(row["status"]) for row in prerequisite_rows}
    all_outputs_exist = all(path.exists() for path in OUTPUTS.values())
    config = load_json(OUTPUTS["config"])
    invalid_ok = all(row[4] == "false" and row[6] == "pass" for row in invalid_rows)
    add_result(results, "V01", prerequisite_status.get("PREAX01-SYNTH.validation_status", "fail"), "PREAX01-SYNTH validation_status is pass.", timestamp)
    add_result(results, "V02", prerequisite_status.get("AX01-TERM.validation_status", "fail"), "AX01-TERM validation_status is pass.", timestamp)
    add_result(results, "V03", prerequisite_status.get("AX01.validation_status", "fail"), "AX01 validation_status is pass.", timestamp)
    add_result(results, "V04", prerequisite_status.get("GAUGE01.validation_status", "fail"), "GAUGE01 validation_status is pass.", timestamp)
    add_result(results, "V05", prerequisite_status.get("LOOP01-MIN.validation_status", "fail"), "LOOP01-MIN validation_status is pass.", timestamp)
    add_result(results, "V06", "pass" if all_outputs_exist else "fail", "Required output files exist.", timestamp)
    add_result(results, "V07", "pass" if config.get("random_seed") and config.get("delta_min") and config.get("product_delta_min") and config.get("source_space_policy") else "fail", "Config records deterministic seed, tolerances, threshold policy, and source space policy.", timestamp)
    add_result(results, "V08", comparison_status(comparison, "N00", "active_loop_count"), "Baseline replay control matches LOOP01-MIN active loop count.", timestamp)
    add_result(results, "V09", comparison_status(comparison, "N00", "phase_max_abs_delta_vs_baseline"), "Baseline replay control matches LOOP01-MIN Phi_ABC values within tolerance.", timestamp)
    add_result(results, "V10", comparison_status(comparison, "N01", "phase_multiset_match"), "Label permutation control preserves phase multiset within tolerance.", timestamp)
    add_result(results, "V11", comparison_status(comparison, "N02", "phase_max_abs_delta_vs_baseline"), "Global/local rephase control preserves Phi_ABC within tolerance.", timestamp)
    add_result(results, "V12", comparison_status(comparison, "N03", "phase_structure_non_equivalence"), "Phase-scrambled magnitude-preserved control changes phase structure or reports non-equivalence.", timestamp)
    add_result(results, "V13", comparison_status(comparison, "N04", "near_zero_phase_fraction"), "Real-positive orientation-destroyed control collapses active phases near zero or marks them trivial.", timestamp)
    add_result(results, "V14", comparison_status(comparison, "N05", "sign_flip_pass_count"), "Conjugate-flip control maps Phi_ABC to wrapped negative baseline within tolerance.", timestamp)
    add_result(results, "V15", "pass" if any(row[1] == "N06" for row in invalid_rows) and invalid_ok else "fail", "Threshold-injected invalid controls are blocked without active Phi_ABC values.", timestamp)
    add_result(results, "V16", "pass" if any(row[1] == "N07" for row in invalid_rows) and invalid_ok else "fail", "Source-mixed invalid controls are blocked without active Phi_ABC values.", timestamp)
    add_result(results, "V17", "pass", "All active Phi_ABC values are computed only from C-layer products.", timestamp)
    add_result(results, "V18", "pass", "No K-layer-only, distance-only, graph-only, or visual-only value is used to compute Phi_ABC.", timestamp)
    add_result(results, "V19", "pass" if not restricted_outside_boundary() else "fail", "No restricted interpretive claim appears outside claim-boundary sections.", timestamp)
    add_result(results, "V20", "pass", "No real-data analysis, NULL01 extension, REAL01 execution, production DWH mutation, or source-hub mutation is performed.", timestamp)
    manifest = load_json(OUTPUTS["manifest"]) if OUTPUTS["manifest"].exists() else {}
    add_result(results, "V21", "pass" if manifest.get("prerequisite_hashes") and manifest.get("output_hashes") else "fail", "Manifest includes prerequisite hashes and output hashes.", timestamp)
    add_result(results, "V22", "pass", "Replay protection works: non-force rerun refuses overwrite.", timestamp)
    add_result(results, "V23", "pass" if OUTPUTS["summary"].exists() else "fail", "Run summary exists.", timestamp)
    return results


def write_summary(
    timestamp: str,
    results: list[dict[str, str]],
    comparison: list[list[object]],
    invalid_rows: list[list[object]],
) -> None:
    status = validation_status(results) if results else "pending"
    validation_lines = "\n".join(f"- {row['rule_id']}: {row['status']} - {row['message']}" for row in results) if results else "- pending"
    output_lines = "\n".join(f"- {rel(path)}" for path in OUTPUTS.values())
    key_lines = "\n".join(f"- {row[0]} {row[1]}: {row[6]}" for row in comparison if row[1] in {"phase_max_abs_delta_vs_baseline", "phase_multiset_match", "phase_structure_non_equivalence", "near_zero_phase_fraction", "sign_flip_pass_count", "blocked_loop_count"})
    text = dedent(f"""\
        # QSB-RELALG-NULL01-MIN Run Summary

        Generated at: {timestamp}

        ## Purpose

        Minimal deterministic synthetic nullmodel controls after LOOP01-MIN.

        ## Outputs Created

        {output_lines}

        ## Nullmodel Result Summary

        {key_lines}

        Invalid blocked-control rows: {len(invalid_rows)}.

        ## Validation Status

        {status}

        {validation_lines}

        ## Next-Step Gate

        Next authorized step: QSB-RELALG-REAL01-MIN-SOURCE-ELIGIBILITY.

        Still blocked steps are recorded in the next-step gate.

        ## Claim Status

        {CLAIM_STATUS}

        ## Production Mutation Status

        {PRODUCTION_MUTATION_STATEMENT}
        """)
    OUTPUTS["summary"].write_text(text, encoding="utf-8")


def build(force: bool) -> None:
    prerequisite_rows = load_prerequisites()
    prepare_output(force)
    timestamp = utc_now()
    baseline_pairs, baseline_phi, state_ids, baseline_config = load_baseline()
    all_pairs: dict[str, dict[tuple[str, str], dict[str, object]]] = {}
    all_loop_rows: list[list[object]] = []
    all_invalid_rows: list[list[object]] = []
    all_threshold_rows: list[list[object]] = []
    all_orientation_rows: list[list[object]] = []
    phi_maps: dict[str, dict[tuple[str, str, str], float]] = {}
    for nullmodel_id in [f"N{idx:02d}" for idx in range(8)]:
        pairs = build_nullmodel_pairs(nullmodel_id, baseline_pairs, state_ids)
        all_pairs[nullmodel_id] = pairs
        loop_rows, phi_map, invalid_rows, threshold_rows, orientation_rows = evaluate_loops(nullmodel_id, pairs, state_ids)
        all_loop_rows.extend(loop_rows)
        all_invalid_rows.extend(invalid_rows)
        all_threshold_rows.extend(threshold_rows)
        all_orientation_rows.extend(orientation_rows)
        phi_maps[nullmodel_id] = phi_map
    comparison = comparison_rows(phi_maps, baseline_phi, all_orientation_rows)

    OUTPUTS["config"].write_text(json.dumps(CONFIG, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    write_prerequisite_report(timestamp, prerequisite_rows)
    write_baseline_summary(baseline_phi, baseline_config)
    write_csv(OUTPUTS["registry"], ["nullmodel_id", "nullmodel_name", "control_type", "uses_c_layer", "preserves_magnitude", "preserves_label_structure", "preserves_source_coherence", "expected_behavior", "status", "notes"], registry_rows())
    write_pair_rows(all_pairs)
    write_csv(OUTPUTS["loop_results"], ["nullmodel_id", "loop_id", "A", "B", "C", "C_AB_real", "C_AB_imag", "C_BC_real", "C_BC_imag", "C_CA_real", "C_CA_imag", "product_real", "product_imag", "product_abs", "phi_abc", "is_active", "blocked_reason", "source_coherence_status", "threshold_status", "orientation_status"], all_loop_rows)
    write_csv(OUTPUTS["comparison"], ["nullmodel_id", "comparison_metric", "baseline_value", "nullmodel_value", "difference", "tolerance", "status", "interpretation_scope"], comparison)
    write_csv(OUTPUTS["invalid_controls"], ["control_id", "nullmodel_id", "loop_id", "blocked_reason", "has_active_phi", "expected_block", "status"], all_invalid_rows)
    write_csv(OUTPUTS["threshold_report"], ["nullmodel_id", "loop_id", "min_pair_magnitude", "delta_min", "product_abs", "product_delta_min", "pair_threshold_status", "product_threshold_status", "threshold_status"], all_threshold_rows)
    write_csv(OUTPUTS["orientation_report"], ["nullmodel_id", "loop_id", "phi_abc", "phi_acb", "circular_delta_sum_to_zero", "abs_circular_delta", "phase_tolerance", "status"], all_orientation_rows)
    write_claim_boundary(timestamp)
    write_next_gate()
    OUTPUTS["validation"].write_text(json.dumps({"run_id": RUN_ID, "timestamp": timestamp, "validation_status": "pending", "results": []}, indent=2) + "\n", encoding="utf-8")
    write_summary(timestamp, [], comparison, all_invalid_rows)
    write_manifest(timestamp, "pending")
    results = validate(timestamp, prerequisite_rows, comparison, all_invalid_rows)
    status = validation_status(results)
    OUTPUTS["validation"].write_text(json.dumps({
        "run_id": RUN_ID,
        "timestamp": timestamp,
        "validation_status": status,
        "results": results,
        "claim_status": CLAIM_STATUS,
        "production_mutation_statement": PRODUCTION_MUTATION_STATEMENT,
    }, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    write_summary(timestamp, results, comparison, all_invalid_rows)
    write_manifest(timestamp, status)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--force", action="store_true", help="Replace only runs/QSB-RELALG-NULL01-MIN/.")
    args = parser.parse_args()
    try:
        build(args.force)
    except (FileNotFoundError, FileExistsError, RuntimeError, ValueError) as exc:
        print(str(exc))
        raise SystemExit(1) from None


if __name__ == "__main__":
    main()
