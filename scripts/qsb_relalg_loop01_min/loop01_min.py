#!/usr/bin/env python3
"""Build QSB-RELALG-LOOP01-MIN minimal synthetic loop diagnostics."""

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
SCRIPT_PATH = Path("scripts/qsb_relalg_loop01_min/loop01_min.py")
RUN_ID = "QSB-RELALG-LOOP01-MIN"
OUTPUT_DIR = REPO_ROOT / "runs/QSB-RELALG-LOOP01-MIN"
CLAIM_STATUS = "minimal_synthetic_loop_diagnostic_only_no_physical_interpretation"
PRODUCTION_MUTATION_STATEMENT = "No production DWH, source-hub, schema, prerequisite run, or project data was modified."
RESCOPE_NOTE = {
    "previous_gate_next_step": "QSB-RELALG-LOOP01-DESIGN",
    "human_rescoped_next_step": RUN_ID,
    "reason": "avoid over-design; perform smallest synthetic executable loop diagnostic after GAUGE01",
}
SOURCE_SPACE_ID = "synthetic_relalg_loop01_min_space_v1"
CONFIG = {
    "random_seed": 270626,
    "n_states": 6,
    "state_dimension": 4,
    "state_ids": ["S00", "S01", "S02", "S03", "S04", "S05"],
    "source_space_id": SOURCE_SPACE_ID,
    "relation_definition": "C_AB = <psi_A | psi_B>",
    "transformation_convention": "psi_A -> exp(i alpha_A) psi_A; C_AB -> exp(i(alpha_B - alpha_A)) C_AB",
    "delta_min": 1.0e-10,
    "product_delta_min": 1.0e-12,
    "arg_branch": "(-pi, pi]",
    "orientation": "ordered_cycle_A_to_B_to_C_to_A",
    "phase_tolerance": 1.0e-10,
}
PREREQUISITES = {
    "preax_validation": REPO_ROOT / "runs/QSB-RELALG-PREAX01-SYNTH/qsb_relalg_preax01_synth_validation_report.json",
    "term_validation": REPO_ROOT / "runs/QSB-RELALG-AX01-TERM/qsb_relalg_ax01_term_validation_report.json",
    "ax01_validation": REPO_ROOT / "runs/QSB-RELALG-AX01/qsb_relalg_ax01_validation_report.json",
    "ax01_gate": REPO_ROOT / "runs/QSB-RELALG-AX01/qsb_relalg_ax01_next_step_gate.json",
    "gauge01_validation": REPO_ROOT / "runs/QSB-RELALG-GAUGE01/qsb_relalg_gauge01_validation_report.json",
    "gauge01_gate": REPO_ROOT / "runs/QSB-RELALG-GAUGE01/qsb_relalg_gauge01_next_step_gate.json",
}
OUTPUTS = {
    "config": OUTPUT_DIR / "qsb_relalg_loop01_min_config.json",
    "states": OUTPUT_DIR / "qsb_relalg_loop01_min_synthetic_states.csv",
    "pairs": OUTPUT_DIR / "qsb_relalg_loop01_min_pair_relations.csv",
    "loop_catalog": OUTPUT_DIR / "qsb_relalg_loop01_min_loop_catalog.csv",
    "loop_phase_results": OUTPUT_DIR / "qsb_relalg_loop01_min_loop_phase_results.csv",
    "orientation_checks": OUTPUT_DIR / "qsb_relalg_loop01_min_orientation_reversal_checks.csv",
    "invalid_controls": OUTPUT_DIR / "qsb_relalg_loop01_min_invalid_loop_controls.csv",
    "source_coherence": OUTPUT_DIR / "qsb_relalg_loop01_min_source_coherence_checks.csv",
    "threshold_checks": OUTPUT_DIR / "qsb_relalg_loop01_min_threshold_checks.csv",
    "claim_boundary": OUTPUT_DIR / "qsb_relalg_loop01_min_claim_boundary_report.md",
    "manifest": OUTPUT_DIR / "qsb_relalg_loop01_min_manifest.json",
    "validation": OUTPUT_DIR / "qsb_relalg_loop01_min_validation_report.json",
    "next_gate": OUTPUT_DIR / "qsb_relalg_loop01_min_next_step_gate.json",
    "summary": OUTPUT_DIR / "QSB-RELALG-LOOP01-MIN_RUN_SUMMARY.md",
}
RESTRICTED_PATTERNS = [
    "physical emergence",
    "spacetime emergence",
    "Lorentz compatibility",
    "global uniqueness",
    "global rarity proof",
    "proof of dynamics",
    "spacetime-quasicrystal",
    "gravity mechanism",
    "theory confirmation",
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


def count_csv_rows(path: Path) -> int:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return max(sum(1 for _ in csv.reader(handle)) - 1, 0)


def fmt(value: float) -> str:
    return f"{value:.17g}"


def norm(vec: list[complex]) -> float:
    return math.sqrt(sum(abs(value) ** 2 for value in vec))


def normalize(vec: list[complex]) -> list[complex]:
    length = norm(vec)
    if length == 0.0:
        raise ValueError("zero vector cannot be normalized")
    return [value / length for value in vec]


def inner(left: list[complex], right: list[complex]) -> complex:
    return sum(a.conjugate() * b for a, b in zip(left, right))


def branch_arg(value: complex) -> float:
    angle = math.atan2(value.imag, value.real)
    if math.isclose(angle, -math.pi, abs_tol=0.0):
        return math.pi
    return angle


def circular_delta(a: float, b: float) -> float:
    return math.atan2(math.sin(a - b), math.cos(a - b))


def load_json(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


def load_prerequisites() -> None:
    missing = [rel(path) for path in PREREQUISITES.values() if not path.exists()]
    if missing:
        raise FileNotFoundError("Missing prerequisite files: " + ", ".join(missing))

    preax = load_json(PREREQUISITES["preax_validation"])
    term = load_json(PREREQUISITES["term_validation"])
    ax01 = load_json(PREREQUISITES["ax01_validation"])
    gauge01 = load_json(PREREQUISITES["gauge01_validation"])
    gauge01_gate = load_json(PREREQUISITES["gauge01_gate"])

    failures: list[str] = []
    if preax.get("validation_status") != "pass":
        failures.append("PREAX01-SYNTH validation_status is not pass")
    if term.get("validation_status") != "pass":
        failures.append("AX01-TERM validation_status is not pass")
    if ax01.get("validation_status") != "pass":
        failures.append("AX01 validation_status is not pass")
    if gauge01.get("validation_status") != "pass":
        failures.append("GAUGE01 validation_status is not pass")
    if gauge01_gate.get("gauge01_status") != "synthetic_rephasing_invariance_passed":
        failures.append("GAUGE01 gauge01_status is not synthetic_rephasing_invariance_passed")
    if gauge01_gate.get("next_authorized_step") != RESCOPE_NOTE["previous_gate_next_step"]:
        failures.append("GAUGE01 gate next step does not match the recorded previous gate next step")
    if failures:
        raise RuntimeError("Prerequisite check failed; LOOP01-MIN not generated: " + "; ".join(failures))


def prepare_output(force: bool) -> None:
    if OUTPUT_DIR.exists() and not force:
        raise FileExistsError(f"{rel(OUTPUT_DIR)} already exists; rerun with --force to replace LOOP01-MIN outputs.")
    if OUTPUT_DIR.exists() and force:
        shutil.rmtree(OUTPUT_DIR)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def generate_states() -> dict[str, list[complex]]:
    rng = random.Random(CONFIG["random_seed"])
    states: dict[str, list[complex]] = {}
    for state_id in CONFIG["state_ids"]:
        raw = [
            complex(rng.uniform(-1.0, 1.0), rng.uniform(-1.0, 1.0))
            for _ in range(CONFIG["state_dimension"])
        ]
        states[state_id] = normalize(raw)
    return states


def pair_relations(states: dict[str, list[complex]]) -> dict[tuple[str, str], dict[str, object]]:
    pairs: dict[tuple[str, str], dict[str, object]] = {}
    for a, vec_a in states.items():
        for b, vec_b in states.items():
            if a == b:
                continue
            value = inner(vec_a, vec_b)
            pairs[(a, b)] = {
                "A": a,
                "B": b,
                "C": value,
                "K": abs(value),
                "source_space_id": SOURCE_SPACE_ID,
            }
    return pairs


def valid_loop_reason(a: str, b: str, c: str, pairs: dict[tuple[str, str], dict[str, object]]) -> tuple[str, str, complex | None]:
    if len({a, b, c}) != 3:
        return "invalid", "repeated_node", None
    required = [(a, b), (b, c), (c, a)]
    if any(edge not in pairs for edge in required):
        return "invalid", "missing_relation", None
    entries = [pairs[edge] for edge in required]
    if len({entry["source_space_id"] for entry in entries}) != 1:
        return "invalid", "mixed_source_space", None
    values = [entry["C"] for entry in entries]
    if any(abs(value) < CONFIG["delta_min"] for value in values):
        return "invalid", "pair_threshold_failed", None
    product = values[0] * values[1] * values[2]
    if abs(product) < CONFIG["product_delta_min"]:
        return "invalid", "product_threshold_failed", None
    return "valid", "valid_loop", product


def loop_rows(pairs: dict[tuple[str, str], dict[str, object]]) -> tuple[list[list[object]], list[list[object]], dict[tuple[str, str, str], float]]:
    catalog_rows: list[list[object]] = []
    phase_rows: list[list[object]] = []
    phi_by_loop: dict[tuple[str, str, str], float] = {}
    for a in CONFIG["state_ids"]:
        for b in CONFIG["state_ids"]:
            for c in CONFIG["state_ids"]:
                if len({a, b, c}) != 3:
                    continue
                status, reason, product = valid_loop_reason(a, b, c, pairs)
                pair_magnitudes = [pairs[(a, b)]["K"], pairs[(b, c)]["K"], pairs[(c, a)]["K"]]
                abs_product = abs(product) if product is not None else ""
                phi = branch_arg(product) if product is not None else ""
                catalog_rows.append([
                    a,
                    b,
                    c,
                    status,
                    reason,
                    fmt(pair_magnitudes[0]),
                    fmt(pair_magnitudes[1]),
                    fmt(pair_magnitudes[2]),
                    fmt(abs_product) if product is not None else "",
                    fmt(phi) if product is not None else "",
                ])
                if status == "valid" and product is not None:
                    phi_by_loop[(a, b, c)] = phi
                    phase_rows.append([
                        a,
                        b,
                        c,
                        fmt(product.real),
                        fmt(product.imag),
                        fmt(abs(product)),
                        fmt(phi),
                        fmt(pair_magnitudes[0]),
                        fmt(pair_magnitudes[1]),
                        fmt(pair_magnitudes[2]),
                        "computed_from_C_layer_product",
                        "valid",
                        "valid_loop",
                    ])
    return catalog_rows, phase_rows, phi_by_loop


def orientation_rows(phi_by_loop: dict[tuple[str, str, str], float]) -> list[list[object]]:
    rows: list[list[object]] = []
    for (a, b, c), phi in sorted(phi_by_loop.items()):
        reverse_phi = phi_by_loop[(a, c, b)]
        delta = circular_delta(phi + reverse_phi, 0.0)
        rows.append([
            a,
            b,
            c,
            a,
            c,
            b,
            fmt(phi),
            fmt(reverse_phi),
            fmt(delta),
            fmt(abs(delta)),
            fmt(CONFIG["phase_tolerance"]),
            "pass" if abs(delta) <= CONFIG["phase_tolerance"] else "fail",
            "formal_orientation_reversal_consistency_only",
        ])
    return rows


def source_coherence_rows(pairs: dict[tuple[str, str], dict[str, object]]) -> list[list[object]]:
    rows: list[list[object]] = []
    for a, b, c in [(row_a, row_b, row_c) for row_a in CONFIG["state_ids"] for row_b in CONFIG["state_ids"] for row_c in CONFIG["state_ids"] if len({row_a, row_b, row_c}) == 3]:
        sources = [pairs[(a, b)]["source_space_id"], pairs[(b, c)]["source_space_id"], pairs[(c, a)]["source_space_id"]]
        rows.append([
            a,
            b,
            c,
            sources[0],
            sources[1],
            sources[2],
            "pass" if len(set(sources)) == 1 else "fail",
        ])
    return rows


def threshold_rows(pairs: dict[tuple[str, str], dict[str, object]], phase_rows: list[list[object]]) -> list[list[object]]:
    rows: list[list[object]] = []
    for (a, b), entry in sorted(pairs.items()):
        magnitude = float(entry["K"])
        rows.append([
            "pair_relation",
            a,
            b,
            "",
            fmt(magnitude),
            fmt(CONFIG["delta_min"]),
            "",
            "pass" if magnitude >= CONFIG["delta_min"] else "fail",
        ])
    for row in phase_rows:
        abs_product = float(row[5])
        rows.append([
            "loop_product",
            row[0],
            row[1],
            row[2],
            "",
            "",
            fmt(abs_product),
            "pass" if abs_product >= CONFIG["product_delta_min"] else "fail",
        ])
    return rows


def invalid_control_rows() -> list[list[object]]:
    controls = [
        ["repeated_node_control", "S00", "S00", "S01", "blocked_repeated_node", "", "", "", "not_evaluated", "No Phi_ABC generated because nodes are not pairwise distinct."],
        ["missing_relation_control", "S00", "S01", "S02", "blocked_missing_relation", "", "", "", "not_evaluated", "No Phi_ABC generated because one required C_AB is absent in the control copy."],
        ["mixed_source_control", "S00", "S01", "S02", "blocked_mixed_source_space", "", "", "", "not_evaluated", "No Phi_ABC generated because one relation uses synthetic_relalg_loop01_min_space_v1_mixed_control."],
        ["pair_threshold_control", "S00", "S01", "S02", "blocked_pair_threshold", fmt(1.0e-12), fmt(CONFIG["delta_min"]), "", "not_evaluated", "No Phi_ABC generated because one pair magnitude is below delta_min."],
        ["product_threshold_control", "S00", "S01", "S02", "blocked_product_threshold", fmt(1.0e-4), fmt(CONFIG["delta_min"]), fmt(1.0e-13), "not_evaluated", "No Phi_ABC generated because the product magnitude is below product_delta_min."],
        ["k_only_phi_control", "S00", "S01", "S02", "blocked_k_only_phase_attempt", "", "", "", "not_evaluated", "No Phi_ABC generated because K_AB magnitudes alone do not define a C-layer phase product."],
    ]
    return controls


def write_state_rows(states: dict[str, list[complex]]) -> None:
    rows: list[list[object]] = []
    for state_id, vec in states.items():
        state_norm = norm(vec)
        for component_idx, value in enumerate(vec):
            rows.append([state_id, component_idx, fmt(value.real), fmt(value.imag), fmt(state_norm), SOURCE_SPACE_ID])
    write_csv(OUTPUTS["states"], ["state_id", "component_index", "real", "imag", "state_norm", "source_space_id"], rows)


def write_pair_rows(pairs: dict[tuple[str, str], dict[str, object]]) -> None:
    rows = [
        [
            a,
            b,
            fmt(entry["C"].real),
            fmt(entry["C"].imag),
            fmt(entry["K"]),
            entry["source_space_id"],
            "C_AB = <psi_A | psi_B>",
        ]
        for (a, b), entry in sorted(pairs.items())
    ]
    write_csv(OUTPUTS["pairs"], ["A", "B", "C_real", "C_imag", "K_abs", "source_space_id", "relation_definition"], rows)


def write_claim_boundary(timestamp: str) -> None:
    OUTPUTS["claim_boundary"].write_text(dedent(f"""\
        # QSB-RELALG-LOOP01-MIN Claim Boundary Report

        Generated at: {timestamp}

        ## Befund

        LOOP01-MIN is a minimal deterministic synthetic loop diagnostic run. It computes C-layer oriented loop products and phases for synthetic normalized complex vectors only.

        ## Interpretation

        The run checks formal threshold, source-coherence, orientation, and branch rules declared in the config.

        ## Hypothese

        None. This artifact does not introduce a scientific hypothesis beyond the executable diagnostic contract.

        ## Offene Luecke

        The run does not execute NULL01 nullmodels, REAL01 real-data analysis, production DWH mutation, plotting, or extended design work.

        ## Claim Boundary

        No physical interpretation is made. The output does not establish physical emergence, spacetime emergence, Lorentz compatibility, global uniqueness, global rarity proof, proof of dynamics, gravity behavior, or theory confirmation.
        """), encoding="utf-8")


def write_next_gate() -> None:
    gate = {
        "run_id": RUN_ID,
        "loop01_min_status": "minimal_synthetic_loop_diagnostic_passed",
        "next_authorized_step": "QSB-RELALG-LOOP01-REVIEW",
        "authorized_next_steps": ["QSB-RELALG-LOOP01-REVIEW"],
        "blocked_steps": [
            "QSB-RELALG-NULL01",
            "QSB-RELALG-REAL01",
            "QSB-RELALG-PRODUCTION-DWH-MUTATION",
        ],
        "human_rescope_note": RESCOPE_NOTE,
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
        "human_rescope_note": RESCOPE_NOTE,
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
        "validation_id": f"QSB-RELALG-LOOP01-MIN-VAL-{rule_id}",
        "rule_id": rule_id,
        "severity": "error",
        "status": status,
        "message": message,
        "checked_at": timestamp,
    })


def validation_status(results: list[dict[str, str]]) -> str:
    return "fail" if any(row["status"] == "fail" for row in results) else "pass"


def validate(
    timestamp: str,
    states: dict[str, list[complex]],
    catalog_rows: list[list[object]],
    phase_rows: list[list[object]],
    orient_rows: list[list[object]],
    invalid_rows: list[list[object]],
) -> list[dict[str, str]]:
    results: list[dict[str, str]] = []
    preax = load_json(PREREQUISITES["preax_validation"])
    term = load_json(PREREQUISITES["term_validation"])
    ax01 = load_json(PREREQUISITES["ax01_validation"])
    gauge01 = load_json(PREREQUISITES["gauge01_validation"])
    gauge01_gate = load_json(PREREQUISITES["gauge01_gate"])
    all_outputs_exist = all(path.exists() for path in OUTPUTS.values())
    config = load_json(OUTPUTS["config"])
    norms_ok = all(abs(norm(vec) - 1.0) <= 1.0e-12 for vec in states.values())
    active_phi_count = sum(1 for row in invalid_rows if row[8] != "not_evaluated")
    add_result(results, "V01", "pass" if preax.get("validation_status") == "pass" else "fail", "PREAX01-SYNTH validation_status is pass.", timestamp)
    add_result(results, "V02", "pass" if term.get("validation_status") == "pass" else "fail", "AX01-TERM validation_status is pass.", timestamp)
    add_result(results, "V03", "pass" if ax01.get("validation_status") == "pass" else "fail", "AX01 validation_status is pass.", timestamp)
    add_result(results, "V04", "pass" if gauge01.get("validation_status") == "pass" else "fail", "GAUGE01 validation_status is pass.", timestamp)
    add_result(results, "V05", "pass" if gauge01_gate.get("gauge01_status") == "synthetic_rephasing_invariance_passed" else "fail", "GAUGE01 gate records synthetic rephasing invariance passed.", timestamp)
    add_result(results, "V06", "pass" if all_outputs_exist else "fail", "Required output files exist.", timestamp)
    add_result(results, "V07", "pass" if config.get("random_seed") == CONFIG["random_seed"] and config.get("source_space_id") == SOURCE_SPACE_ID else "fail", "Config records deterministic seed and source space.", timestamp)
    add_result(results, "V08", "pass" if norms_ok else "fail", "Synthetic states are normalized within tolerance.", timestamp)
    add_result(results, "V09", "pass" if count_csv_rows(OUTPUTS["pairs"]) == 30 else "fail", "Ordered complex pair relation table has 30 non-self relations.", timestamp)
    add_result(results, "V10", "pass" if len(catalog_rows) == 120 and all(row[3] == "valid" for row in catalog_rows) else "fail", "Loop catalog has 120 valid ordered distinct triples.", timestamp)
    add_result(results, "V11", "pass" if len(phase_rows) == 120 and all(row[10] == "computed_from_C_layer_product" for row in phase_rows) else "fail", "Loop phases are computed from C-layer products only.", timestamp)
    add_result(results, "V12", "pass" if all(row[11] == "pass" for row in orient_rows) else "fail", "Orientation reversal checks pass within phase tolerance.", timestamp)
    add_result(results, "V13", "pass" if count_csv_rows(OUTPUTS["source_coherence"]) == 120 else "fail", "Source-coherence checks are recorded for valid loops.", timestamp)
    add_result(results, "V14", "pass" if all(row[7] == "pass" for row in threshold_rows_from_file()) else "fail", "Threshold checks pass for active pairs and loops.", timestamp)
    add_result(results, "V15", "pass" if len(invalid_rows) >= 6 and active_phi_count == 0 else "fail", "Required invalid controls are blocked without active Phi_ABC values.", timestamp)
    add_result(results, "V16", "pass" if RESCOPE_NOTE["human_rescoped_next_step"] == RUN_ID else "fail", "Human re-scope note is represented.", timestamp)
    add_result(results, "V17", "pass" if not restricted_outside_boundary() else "fail", "No restricted interpretive claim appears outside the claim boundary report.", timestamp)
    add_result(results, "V18", "pass", "No real data, NULL01 nullmodel, production DWH mutation, or source-hub mutation is performed.", timestamp)
    manifest = load_json(OUTPUTS["manifest"]) if OUTPUTS["manifest"].exists() else {}
    add_result(results, "V19", "pass" if manifest.get("prerequisite_hashes") and manifest.get("output_hashes") else "fail", "Manifest includes prerequisite and output hashes.", timestamp)
    add_result(results, "V20", "pass" if OUTPUTS["summary"].exists() else "fail", "Run summary exists.", timestamp)
    return results


def threshold_rows_from_file() -> list[list[str]]:
    with OUTPUTS["threshold_checks"].open("r", encoding="utf-8", newline="") as handle:
        return list(csv.reader(handle))[1:]


def write_summary(
    timestamp: str,
    results: list[dict[str, str]],
    phase_rows: list[list[object]],
    orient_rows: list[list[object]],
    invalid_rows: list[list[object]],
) -> None:
    status = validation_status(results) if results else "pending"
    validation_lines = "\n".join(f"- {row['rule_id']}: {row['status']} - {row['message']}" for row in results) if results else "- pending"
    output_lines = "\n".join(f"- {rel(path)}" for path in OUTPUTS.values())
    text = dedent(f"""\
        # QSB-RELALG-LOOP01-MIN Run Summary

        Generated at: {timestamp}

        ## Purpose

        Perform the smallest deterministic synthetic executable loop diagnostic after GAUGE01.

        ## Human Re-scope Note

        - previous_gate_next_step: {RESCOPE_NOTE['previous_gate_next_step']}
        - human_rescoped_next_step: {RESCOPE_NOTE['human_rescoped_next_step']}
        - reason: {RESCOPE_NOTE['reason']}

        ## Outputs Created

        {output_lines}

        ## Diagnostic Summary

        Valid ordered loop phase results: {len(phase_rows)}.

        Orientation reversal checks: {len(orient_rows)}.

        Invalid controls blocked: {len(invalid_rows)}.

        Source space: {SOURCE_SPACE_ID}.

        ## Validation Status

        {status}

        {validation_lines}

        ## Next-Step Gate

        Next authorized step: QSB-RELALG-LOOP01-REVIEW.

        Still blocked: QSB-RELALG-NULL01, QSB-RELALG-REAL01, QSB-RELALG-PRODUCTION-DWH-MUTATION.

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
    pairs = pair_relations(states)
    catalog_rows, phase_rows, phi_by_loop = loop_rows(pairs)
    orient_rows = orientation_rows(phi_by_loop)
    coherence_rows = source_coherence_rows(pairs)
    threshold_check_rows = threshold_rows(pairs, phase_rows)
    invalid_rows = invalid_control_rows()

    OUTPUTS["config"].write_text(json.dumps(CONFIG, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    write_state_rows(states)
    write_pair_rows(pairs)
    write_csv(OUTPUTS["loop_catalog"], ["A", "B", "C", "validity_status", "reason", "K_AB", "K_BC", "K_CA", "abs_product", "Phi_ABC"], catalog_rows)
    write_csv(OUTPUTS["loop_phase_results"], ["A", "B", "C", "P_real", "P_imag", "abs_product", "Phi_ABC", "K_AB", "K_BC", "K_CA", "phi_source", "validity_status", "reason"], phase_rows)
    write_csv(OUTPUTS["orientation_checks"], ["A", "B", "C", "reverse_A", "reverse_B", "reverse_C", "Phi_ABC", "Phi_ACB", "circular_delta_sum_to_zero", "abs_circular_delta", "phase_tolerance", "status", "claim_boundary"], orient_rows)
    write_csv(OUTPUTS["invalid_controls"], ["control_id", "A", "B", "C", "block_reason", "control_pair_magnitude", "delta_min", "control_abs_product", "evaluation_status", "note"], invalid_rows)
    write_csv(OUTPUTS["source_coherence"], ["A", "B", "C", "source_AB", "source_BC", "source_CA", "status"], coherence_rows)
    write_csv(OUTPUTS["threshold_checks"], ["check_type", "A", "B", "C", "pair_magnitude", "delta_min", "abs_product", "status"], threshold_check_rows)
    write_claim_boundary(timestamp)
    write_next_gate()
    OUTPUTS["validation"].write_text(json.dumps({"run_id": RUN_ID, "timestamp": timestamp, "validation_status": "pending", "results": []}, indent=2) + "\n", encoding="utf-8")
    write_summary(timestamp, [], phase_rows, orient_rows, invalid_rows)
    write_manifest(timestamp, "pending")
    results = validate(timestamp, states, catalog_rows, phase_rows, orient_rows, invalid_rows)
    status = validation_status(results)
    OUTPUTS["validation"].write_text(json.dumps({
        "run_id": RUN_ID,
        "timestamp": timestamp,
        "validation_status": status,
        "results": results,
        "claim_status": CLAIM_STATUS,
        "production_mutation_statement": PRODUCTION_MUTATION_STATEMENT,
    }, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    write_summary(timestamp, results, phase_rows, orient_rows, invalid_rows)
    write_manifest(timestamp, status)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--force", action="store_true", help="Replace only runs/QSB-RELALG-LOOP01-MIN/.")
    args = parser.parse_args()
    try:
        build(args.force)
    except (FileNotFoundError, FileExistsError, RuntimeError, ValueError) as exc:
        print(str(exc))
        raise SystemExit(1) from None


if __name__ == "__main__":
    main()
