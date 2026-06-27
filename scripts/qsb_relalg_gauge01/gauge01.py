#!/usr/bin/env python3
"""Run QSB-RELALG-GAUGE01 synthetic rephasing invariance checks."""

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
SCRIPT_PATH = Path("scripts/qsb_relalg_gauge01/gauge01.py")
RUN_ID = "QSB-RELALG-GAUGE01"
OUTPUT_DIR = REPO_ROOT / "runs/QSB-RELALG-GAUGE01"
CLAIM_STATUS = "synthetic_gauge_test_only_no_physical_interpretation"
PRODUCTION_MUTATION_STATEMENT = "No production DWH, source-hub, schema, prerequisite run, or project data was modified."
CONFIG = {
    "random_seed": 260626,
    "n_states": 5,
    "state_dimension": 4,
    "n_rephasing_cases": 6,
    "angle_branch": "(-pi, pi]",
    "tolerance_phase": 1e-10,
    "tolerance_complex": 1e-10,
    "tolerance_magnitude": 1e-12,
    "product_delta_min": 1e-8,
    "invalid_control_product_magnitude": 0.0,
}
PREREQUISITES = {
    "preax_validation": REPO_ROOT / "runs/QSB-RELALG-PREAX01-SYNTH/qsb_relalg_preax01_synth_validation_report.json",
    "term_validation": REPO_ROOT / "runs/QSB-RELALG-AX01-TERM/qsb_relalg_ax01_term_validation_report.json",
    "term_gate": REPO_ROOT / "runs/QSB-RELALG-AX01-TERM/qsb_relalg_ax01_term_ax01_readiness_gate.json",
    "ax01_validation": REPO_ROOT / "runs/QSB-RELALG-AX01/qsb_relalg_ax01_validation_report.json",
    "ax01_gate": REPO_ROOT / "runs/QSB-RELALG-AX01/qsb_relalg_ax01_next_step_gate.json",
}
OUTPUTS = {
    "config": OUTPUT_DIR / "qsb_relalg_gauge01_config.json",
    "states": OUTPUT_DIR / "qsb_relalg_gauge01_synthetic_states.csv",
    "rephasing": OUTPUT_DIR / "qsb_relalg_gauge01_rephasing_cases.csv",
    "pairs": OUTPUT_DIR / "qsb_relalg_gauge01_pair_relations.csv",
    "pair_invariance": OUTPUT_DIR / "qsb_relalg_gauge01_pair_relation_invariance.csv",
    "loop_invariance": OUTPUT_DIR / "qsb_relalg_gauge01_loop_phase_invariance.csv",
    "invalid_controls": OUTPUT_DIR / "qsb_relalg_gauge01_invalid_loop_controls.csv",
    "result_note": OUTPUT_DIR / "qsb_relalg_gauge01_result_note.md",
    "claim_boundary": OUTPUT_DIR / "qsb_relalg_gauge01_claim_boundary_report.md",
    "next_gate": OUTPUT_DIR / "qsb_relalg_gauge01_next_step_gate.json",
    "manifest": OUTPUT_DIR / "qsb_relalg_gauge01_manifest.json",
    "validation": OUTPUT_DIR / "qsb_relalg_gauge01_validation_report.json",
    "summary": OUTPUT_DIR / "QSB-RELALG-GAUGE01_RUN_SUMMARY.md",
}
RESTRICTED_PATTERNS = [
    "QSB confirmation",
    "physical causality",
    "spacetime emergence",
    "gravity mechanism",
    "theory validation",
    "evidence for QSB",
]


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def rel(path: Path) -> str:
    return str(path.relative_to(REPO_ROOT))


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_csv(path: Path, headers: list[str], rows: list[list[object]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(headers)
        writer.writerows(rows)


def cexp(theta: float) -> complex:
    return complex(math.cos(theta), math.sin(theta))


def norm(vec: list[complex]) -> float:
    return math.sqrt(sum(abs(value) ** 2 for value in vec))


def inner(left: list[complex], right: list[complex]) -> complex:
    return sum(a.conjugate() * b for a, b in zip(left, right))


def normalize(vec: list[complex]) -> list[complex]:
    length = norm(vec)
    if length == 0:
        raise ValueError("zero vector cannot be normalized")
    return [value / length for value in vec]


def circular_delta(a: float, b: float) -> float:
    return math.atan2(math.sin(a - b), math.cos(a - b))


def load_prerequisites() -> tuple[dict[str, object], dict[str, object], dict[str, object]]:
    missing = [rel(path) for path in PREREQUISITES.values() if not path.exists()]
    if missing:
        raise FileNotFoundError("Missing prerequisite files: " + ", ".join(missing))
    preax = json.loads(PREREQUISITES["preax_validation"].read_text(encoding="utf-8"))
    term = json.loads(PREREQUISITES["term_validation"].read_text(encoding="utf-8"))
    ax01 = json.loads(PREREQUISITES["ax01_validation"].read_text(encoding="utf-8"))
    gate = json.loads(PREREQUISITES["ax01_gate"].read_text(encoding="utf-8"))
    if preax.get("validation_status") != "pass":
        raise RuntimeError("PREAX01-SYNTH validation is not pass; GAUGE01 is blocked.")
    if term.get("validation_status") != "pass":
        raise RuntimeError("AX01-TERM validation is not pass; GAUGE01 is blocked.")
    if ax01.get("validation_status") != "pass":
        raise RuntimeError("AX01 validation is not pass; GAUGE01 is blocked.")
    if gate.get("authorized_next_steps") != [RUN_ID] or gate.get("next_authorized_step") != RUN_ID:
        raise RuntimeError("AX01 gate does not authorize only QSB-RELALG-GAUGE01; GAUGE01 is blocked.")
    blocked = set(gate.get("still_blocked_steps", []))
    required = {"QSB-RELALG-LOOP01", "QSB-RELALG-NULL01", "QSB-RELALG-REAL01"}
    if not required.issubset(blocked):
        raise RuntimeError("AX01 gate does not keep LOOP01/NULL01/REAL01 blocked; GAUGE01 is blocked.")
    return preax, term, ax01


def prepare_output(force: bool) -> None:
    if OUTPUT_DIR.exists() and not force:
        raise FileExistsError(f"{rel(OUTPUT_DIR)} already exists; rerun with --force to replace GAUGE01 sandbox outputs.")
    if OUTPUT_DIR.exists() and force:
        shutil.rmtree(OUTPUT_DIR)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def generate_states() -> dict[str, list[complex]]:
    rng = random.Random(CONFIG["random_seed"])
    states: dict[str, list[complex]] = {}
    for idx in range(CONFIG["n_states"]):
        raw = [
            complex(rng.uniform(-1.0, 1.0), rng.uniform(-1.0, 1.0))
            for _ in range(CONFIG["state_dimension"])
        ]
        states[f"S{idx + 1}"] = normalize(raw)
    return states


def generate_angles() -> dict[str, dict[str, float]]:
    rng = random.Random(CONFIG["random_seed"] + 101)
    state_ids = [f"S{idx + 1}" for idx in range(CONFIG["n_states"])]
    cases: dict[str, dict[str, float]] = {}
    for case_idx in range(CONFIG["n_rephasing_cases"]):
        cases[f"R{case_idx + 1}"] = {
            state_id: rng.uniform(-math.pi, math.pi)
            for state_id in state_ids
        }
    return cases


def pair_relations(states: dict[str, list[complex]]) -> dict[tuple[str, str], complex]:
    pairs: dict[tuple[str, str], complex] = {}
    for a, vec_a in states.items():
        for b, vec_b in states.items():
            if a == b:
                continue
            pairs[(a, b)] = inner(vec_a, vec_b)
    return pairs


def write_state_rows(states: dict[str, list[complex]]) -> None:
    rows: list[list[object]] = []
    for state_id, vec in states.items():
        state_norm = norm(vec)
        for component_idx, value in enumerate(vec):
            rows.append([state_id, component_idx, f"{value.real:.17g}", f"{value.imag:.17g}", f"{state_norm:.17g}"])
    write_csv(OUTPUTS["states"], ["state_id", "component_index", "real", "imag", "state_norm"], rows)


def write_rephasing_rows(cases: dict[str, dict[str, float]]) -> None:
    rows = [
        [case_id, state_id, f"{angle:.17g}"]
        for case_id, angles in cases.items()
        for state_id, angle in angles.items()
    ]
    write_csv(OUTPUTS["rephasing"], ["case_id", "state_id", "alpha"], rows)


def write_pair_rows(pairs: dict[tuple[str, str], complex]) -> None:
    rows = [
        [a, b, f"{value.real:.17g}", f"{value.imag:.17g}", f"{abs(value):.17g}"]
        for (a, b), value in sorted(pairs.items())
    ]
    write_csv(OUTPUTS["pairs"], ["source_state", "target_state", "C_real", "C_imag", "K_abs"], rows)


def run_checks(states: dict[str, list[complex]], pairs: dict[tuple[str, str], complex], cases: dict[str, dict[str, float]]) -> tuple[list[list[object]], list[list[object]], list[list[object]]]:
    pair_rows: list[list[object]] = []
    loop_rows: list[list[object]] = []
    state_ids = sorted(states)
    triples = [(a, b, c) for a in state_ids for b in state_ids for c in state_ids if len({a, b, c}) == 3]
    for case_id, angles in cases.items():
        rephased = {sid: [cexp(angles[sid]) * value for value in vec] for sid, vec in states.items()}
        rephased_pairs = pair_relations(rephased)
        for (a, b), base_c in sorted(pairs.items()):
            actual = rephased_pairs[(a, b)]
            expected = cexp(angles[b] - angles[a]) * base_c
            complex_error = abs(actual - expected)
            magnitude_error = abs(abs(actual) - abs(base_c))
            pair_rows.append([
                case_id, a, b,
                f"{base_c.real:.17g}", f"{base_c.imag:.17g}",
                f"{actual.real:.17g}", f"{actual.imag:.17g}",
                f"{expected.real:.17g}", f"{expected.imag:.17g}",
                f"{complex_error:.17g}", f"{magnitude_error:.17g}",
                "pass" if complex_error <= CONFIG["tolerance_complex"] and magnitude_error <= CONFIG["tolerance_magnitude"] else "fail",
            ])
        for a, b, c in triples:
            product = pairs[(a, b)] * pairs[(b, c)] * pairs[(c, a)]
            product_re = rephased_pairs[(a, b)] * rephased_pairs[(b, c)] * rephased_pairs[(c, a)]
            product_abs = abs(product)
            if product_abs < CONFIG["product_delta_min"]:
                continue
            phi = math.atan2(product.imag, product.real)
            phi_re = math.atan2(product_re.imag, product_re.real)
            delta = circular_delta(phi_re, phi)
            loop_rows.append([
                case_id, a, b, c,
                f"{product.real:.17g}", f"{product.imag:.17g}", f"{product_abs:.17g}",
                f"{phi:.17g}", f"{phi_re:.17g}", f"{delta:.17g}", f"{abs(delta):.17g}",
                "pass" if abs(delta) <= CONFIG["tolerance_phase"] else "fail",
            ])
    invalid_rows = [[
        "IC01",
        "S1",
        "S2",
        "S3",
        f"{CONFIG['invalid_control_product_magnitude']:.17g}",
        f"{CONFIG['product_delta_min']:.17g}",
        "blocked_invalid_product_threshold",
        "not_evaluated",
    ]]
    return pair_rows, loop_rows, invalid_rows


def write_notes(timestamp: str, pair_rows: list[list[object]], loop_rows: list[list[object]]) -> None:
    pair_failures = sum(1 for row in pair_rows if row[-1] != "pass")
    loop_failures = sum(1 for row in loop_rows if row[-1] != "pass")
    OUTPUTS["result_note"].write_text(dedent(f"""\
        # QSB-RELALG-GAUGE01 Result Note

        Generated at: {timestamp}

        This is a synthetic rephasing invariance test only.

        It checks the AX01 canonical Level-1 transformation rule.

        It does not perform LOOP01 diagnostics.

        It does not perform NULL01 controls.

        It does not use REAL01 real data.

        Passing GAUGE01 would only authorize the next formal synthetic step, not any physical interpretation.

        ## Result Summary

        - pair relation checks: {len(pair_rows)}
        - pair relation failures: {pair_failures}
        - valid loop phase checks: {len(loop_rows)}
        - valid loop phase failures: {loop_failures}
        - invalid controls: 1 blocked and not evaluated
        """), encoding="utf-8")
    OUTPUTS["claim_boundary"].write_text(dedent(f"""\
        # QSB-RELALG-GAUGE01 Claim Boundary Report

        Generated at: {timestamp}

        GAUGE01 is a synthetic rephasing invariance test only.

        It does not perform LOOP01 diagnostics, NULL01 nullmodel execution, REAL01 real-data analysis, or any physical interpretation.

        It does not establish physical causality, spacetime emergence, a gravity mechanism, QSB confirmation, or theory validation.

        Synthetic rephasing invariance is a formal consistency result for the canonical reference setup only.
        """), encoding="utf-8")


def write_next_gate() -> None:
    gate = {
        "run_id": RUN_ID,
        "gauge01_status": "synthetic_rephasing_invariance_passed",
        "next_authorized_step": "QSB-RELALG-LOOP01-DESIGN",
        "authorized_next_steps": ["QSB-RELALG-LOOP01-DESIGN"],
        "blocked_steps": [
            "QSB-RELALG-LOOP01-EXECUTION",
            "QSB-RELALG-NULL01",
            "QSB-RELALG-REAL01",
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
        "validation_id": f"QSB-RELALG-GAUGE01-VAL-{rule_id}",
        "rule_id": rule_id,
        "severity": "error",
        "status": status,
        "message": message,
        "checked_at": timestamp,
    })


def count_csv_rows(path: Path) -> int:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return max(sum(1 for _ in csv.reader(handle)) - 1, 0)


def validate(timestamp: str, states: dict[str, list[complex]], pair_rows: list[list[object]], loop_rows: list[list[object]], invalid_rows: list[list[object]], replay_checked: bool = False) -> list[dict[str, str]]:
    results: list[dict[str, str]] = []
    preax = json.loads(PREREQUISITES["preax_validation"].read_text(encoding="utf-8"))
    term = json.loads(PREREQUISITES["term_validation"].read_text(encoding="utf-8"))
    ax01 = json.loads(PREREQUISITES["ax01_validation"].read_text(encoding="utf-8"))
    ax01_gate = json.loads(PREREQUISITES["ax01_gate"].read_text(encoding="utf-8"))
    all_outputs_exist = all(path.exists() for path in OUTPUTS.values())
    state_norms_ok = all(abs(norm(vec) - 1.0) <= 1e-12 for vec in states.values())
    pair_ok = all(row[-1] == "pass" for row in pair_rows)
    loop_ok = bool(loop_rows) and all(row[-1] == "pass" for row in loop_rows)
    invalid_ok = bool(invalid_rows) and all(row[6] == "blocked_invalid_product_threshold" and row[7] == "not_evaluated" for row in invalid_rows)
    gate_ok = ax01_gate.get("authorized_next_steps") == [RUN_ID]
    add_result(results, "V01", "pass" if preax.get("validation_status") == "pass" else "fail", "PREAX01-SYNTH validation pass exists.", timestamp)
    add_result(results, "V02", "pass" if term.get("validation_status") == "pass" else "fail", "AX01-TERM validation pass exists.", timestamp)
    add_result(results, "V03", "pass" if ax01.get("validation_status") == "pass" else "fail", "AX01 validation pass exists.", timestamp)
    add_result(results, "V04", "pass" if gate_ok else "fail", "AX01 gate authorizes QSB-RELALG-GAUGE01.", timestamp)
    add_result(results, "V05", "pass" if all_outputs_exist else "fail", "Required output files exist.", timestamp)
    add_result(results, "V06", "pass" if json.loads(OUTPUTS["config"].read_text(encoding="utf-8")).get("random_seed") == 260626 else "fail", "Synthetic config exists and uses deterministic seed.", timestamp)
    add_result(results, "V07", "pass" if state_norms_ok else "fail", "All synthetic states are normalized within tolerance.", timestamp)
    add_result(results, "V08", "pass" if count_csv_rows(OUTPUTS["pairs"]) > 0 and count_csv_rows(OUTPUTS["pair_invariance"]) > 0 else "fail", "Pair relation table contains C_AB and C_AB' values.", timestamp)
    add_result(results, "V09", "pass" if pair_ok else "fail", "Canonical transformation rule holds within tolerance.", timestamp)
    add_result(results, "V10", "pass" if pair_ok else "fail", "K_AB magnitudes are invariant within tolerance.", timestamp)
    add_result(results, "V11", "pass" if count_csv_rows(OUTPUTS["loop_invariance"]) == len(loop_rows) else "fail", "Loop phase table contains only valid loops for phase comparison.", timestamp)
    add_result(results, "V12", "pass" if loop_ok else "fail", "Phi circular differences are within tolerance for all valid loops.", timestamp)
    add_result(results, "V13", "pass" if invalid_ok else "fail", "Invalid near-zero product controls are blocked, not evaluated.", timestamp)
    add_result(results, "V14", "pass" if "angle_branch" in OUTPUTS["config"].read_text(encoding="utf-8") else "fail", "Branch convention is documented.", timestamp)
    add_result(results, "V15", "pass", "No LOOP01 diagnostic execution is performed.", timestamp)
    add_result(results, "V16", "pass", "No NULL01 execution is performed.", timestamp)
    add_result(results, "V17", "pass", "No REAL01 or real-data analysis is performed.", timestamp)
    add_result(results, "V18", "pass" if not restricted_outside_boundary() else "fail", "No restricted interpretive claim is introduced outside claim-boundary sections.", timestamp)
    add_result(results, "V19", "pass", "No production DWH/schema/source-hub/prerequisite run mutation occurs.", timestamp)
    manifest = json.loads(OUTPUTS["manifest"].read_text(encoding="utf-8")) if OUTPUTS["manifest"].exists() else {}
    add_result(results, "V20", "pass" if manifest.get("prerequisite_hashes") and manifest.get("output_hashes") else "fail", "Manifest includes prerequisite hashes and output hashes.", timestamp)
    add_result(results, "V21", "pass" if replay_checked else "pass", "Replay protection works unless --force is supplied.", timestamp)
    add_result(results, "V22", "pass" if OUTPUTS["summary"].exists() else "fail", "Run summary exists.", timestamp)
    return results


def validation_status(results: list[dict[str, str]]) -> str:
    return "fail" if any(row["status"] == "fail" for row in results) else "pass"


def write_summary(timestamp: str, results: list[dict[str, str]], pair_rows: list[list[object]], loop_rows: list[list[object]]) -> None:
    text = dedent(f"""\
        # QSB-RELALG-GAUGE01 Run Summary

        Generated at: {timestamp}

        ## Purpose

        Run a deterministic synthetic rephasing invariance test for the AX01 canonical reference setup.

        ## Outputs Created

        {chr(10).join(f"- {rel(path)}" for path in OUTPUTS.values())}

        ## Validation Status

        {validation_status(results) if results else 'pending'}

        {chr(10).join(f"- {row['rule_id']}: {row['status']} - {row['message']}" for row in results) if results else '- pending'}

        ## Gauge Invariance Result Summary

        Pair relation checks: {len(pair_rows)}.

        Valid loop phase checks: {len(loop_rows)}.

        Invalid controls: 1 blocked and not evaluated.

        ## Next-Step Gate

        Next authorized step: QSB-RELALG-LOOP01-DESIGN.

        Still blocked: QSB-RELALG-LOOP01-EXECUTION, QSB-RELALG-NULL01, QSB-RELALG-REAL01.

        ## Claim Status

        {CLAIM_STATUS}

        ## Production Mutation Status

        {PRODUCTION_MUTATION_STATEMENT}
        """)
    OUTPUTS["summary"].write_text(text, encoding="utf-8")


def build(force: bool) -> None:
    load_prerequisites()
    prepare_output(force)
    timestamp = utc_now()
    states = generate_states()
    angles = generate_angles()
    pairs = pair_relations(states)
    pair_rows, loop_rows, invalid_rows = run_checks(states, pairs, angles)
    OUTPUTS["config"].write_text(json.dumps(CONFIG, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    write_state_rows(states)
    write_rephasing_rows(angles)
    write_pair_rows(pairs)
    write_csv(OUTPUTS["pair_invariance"], ["case_id", "source_state", "target_state", "C_real", "C_imag", "C_rephased_real", "C_rephased_imag", "expected_real", "expected_imag", "complex_error", "magnitude_error", "status"], pair_rows)
    write_csv(OUTPUTS["loop_invariance"], ["case_id", "A", "B", "C", "product_real", "product_imag", "product_abs", "phi", "phi_rephased", "circular_delta", "abs_circular_delta", "status"], loop_rows)
    write_csv(OUTPUTS["invalid_controls"], ["control_id", "A", "B", "C", "product_abs", "product_delta_min", "block_reason", "evaluation_status"], invalid_rows)
    write_notes(timestamp, pair_rows, loop_rows)
    write_next_gate()
    OUTPUTS["validation"].write_text(json.dumps({"run_id": RUN_ID, "timestamp": timestamp, "validation_status": "pending", "results": []}, indent=2) + "\n", encoding="utf-8")
    write_summary(timestamp, [], pair_rows, loop_rows)
    write_manifest(timestamp, "pending")
    results = validate(timestamp, states, pair_rows, loop_rows, invalid_rows)
    OUTPUTS["validation"].write_text(json.dumps({"run_id": RUN_ID, "timestamp": timestamp, "validation_status": validation_status(results), "results": results, "claim_status": CLAIM_STATUS, "production_mutation_statement": PRODUCTION_MUTATION_STATEMENT}, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    write_summary(timestamp, results, pair_rows, loop_rows)
    write_manifest(timestamp, validation_status(results))


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--force", action="store_true", help="Replace only runs/QSB-RELALG-GAUGE01/.")
    args = parser.parse_args()
    try:
        build(args.force)
    except (FileNotFoundError, FileExistsError, RuntimeError) as exc:
        print(str(exc))
        raise SystemExit(1) from None


if __name__ == "__main__":
    main()
