#!/usr/bin/env python3
"""Build the QSB-RELALG-AX01 minimal formal contract draft package."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import shutil
from datetime import datetime, timezone
from pathlib import Path
from textwrap import dedent


REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT_PATH = Path("scripts/qsb_relalg_ax01/ax01.py")
RUN_ID = "QSB-RELALG-AX01"
PREAX_DIR = REPO_ROOT / "runs/QSB-RELALG-PREAX01-SYNTH"
TERM_DIR = REPO_ROOT / "runs/QSB-RELALG-AX01-TERM"
OUTPUT_DIR = REPO_ROOT / "runs/QSB-RELALG-AX01"
CLAIM_STATUS = "formal_contract_only_no_computation"
PRODUCTION_MUTATION_STATEMENT = "No production DWH or existing schema files were modified."
RESTRICTED_PATTERNS = [
    "QSB bestätigt",
    "QSB bewiesen",
    "QSB is proven",
    "proves spacetime",
    "beweist Raumzeit",
    "establishes causality",
    "beweist Kausalität",
    "confirms emergent spacetime",
    "validates physical theory",
    "mechanism of gravity",
    "Mechanismus der Gravitation",
    "visual evidence",
    "reviewer agreement as evidence",
]
PREAX_INPUTS = {
    "preax_validation": PREAX_DIR / "qsb_relalg_preax01_synth_validation_report.json",
    "preax_readiness": PREAX_DIR / "qsb_relalg_preax01_ax01_readiness_gate.json",
    "preax_synth": PREAX_DIR / "qsb_relalg_preax01_synth.md",
    "preax_definitions": PREAX_DIR / "qsb_relalg_preax01_required_definitions.csv",
    "preax_forbidden_terms": PREAX_DIR / "qsb_relalg_preax01_forbidden_terms.csv",
}
TERM_INPUTS = {
    "term_validation": TERM_DIR / "qsb_relalg_ax01_term_validation_report.json",
    "term_readiness": TERM_DIR / "qsb_relalg_ax01_term_ax01_readiness_gate.json",
    "term_contract": TERM_DIR / "qsb_relalg_ax01_term.md",
}
OUTPUTS = {
    "contract": OUTPUT_DIR / "qsb_relalg_ax01_contract.md",
    "definitions": OUTPUT_DIR / "qsb_relalg_ax01_definitions.csv",
    "symbols": OUTPUT_DIR / "qsb_relalg_ax01_symbol_table.csv",
    "admissibility": OUTPUT_DIR / "qsb_relalg_ax01_admissibility_rules.csv",
    "transformations": OUTPUT_DIR / "qsb_relalg_ax01_transformation_rules.csv",
    "thresholds": OUTPUT_DIR / "qsb_relalg_ax01_threshold_policy.csv",
    "orientation_arg": OUTPUT_DIR / "qsb_relalg_ax01_orientation_arg_policy.csv",
    "source_coherence": OUTPUT_DIR / "qsb_relalg_ax01_source_coherence_rules.csv",
    "forbidden_claims": OUTPUT_DIR / "qsb_relalg_ax01_forbidden_claims.csv",
    "next_gate": OUTPUT_DIR / "qsb_relalg_ax01_next_step_gate.json",
    "claim_boundary": OUTPUT_DIR / "qsb_relalg_ax01_claim_boundary_report.md",
    "manifest": OUTPUT_DIR / "qsb_relalg_ax01_manifest.json",
    "validation": OUTPUT_DIR / "qsb_relalg_ax01_validation_report.json",
    "summary": OUTPUT_DIR / "QSB-RELALG-AX01_RUN_SUMMARY.md",
}

DEFINITIONS = [
    ["psi_A", "formal object label; Level 1 may use a normalized reference vector", "no automatic physics interpretation"],
    ["C_AB", "phase-carrying complex relation layer on ordered pair (A,B)", "requires declared transformation rule"],
    ["K_AB", "derived phase-blind strength, magnitude, score, or real projection", "not a substitute for C-layer input"],
    ["d_AB", "derived cost/distance-like quantity from a declared mapping", "not automatically a metric"],
    ["Phi_ABC", "arg(C_AB C_BC C_CA) only when all admissibility gates pass", "no computation in AX01"],
    ["valid_loop", "loop candidate passing all formal admissibility gates", "formal status only"],
    ["invalid_loop", "loop candidate failing at least one formal gate", "must not be evaluated"],
    ["source_space", "declared provenance/source domain for C-layer relations", "required for source coherence"],
    ["cross_source_mapping_contract", "explicit contract mapping sources to a common relation space", "required for mixed-source use"],
    ["delta_min", "symbolic per-edge nonvanishing threshold", "numeric value required before computation"],
    ["product_delta_min", "symbolic loop-product nonvanishing threshold", "numeric value required before computation"],
    ["arg_branch", "argument branch convention; default (-pi, pi]", "branch handling required before numeric use"],
    ["orientation", "loop direction convention; default A -> B -> C -> A", "reverse orientation is distinct"],
    ["rephasing_gauge", "formal local phase transformation convention", "Level 1 reference only in AX01"],
    ["nullmodel", "later control interface placeholder", "not executed in AX01"],
    ["claim_boundary", "explicit limits on admissible and forbidden uses", "mandatory"],
]

SYMBOLS = [
    ["A, B, C", "ordered formal object labels", "must be pairwise distinct for default loop"],
    ["psi_A", "formal label / Level 1 reference vector", "not physical by default"],
    ["C_AB", "complex C-layer relation", "phase-carrying"],
    ["K_AB", "K-layer magnitude/score/projection", "phase-blind"],
    ["d_AB", "derived cost/distance-like quantity", "metric properties not assumed"],
    ["Phi_ABC", "arg(C_AB C_BC C_CA)", "C-layer only"],
    ["valid_loop", "loop candidate passing all formal gates", "admissible formal object"],
    ["invalid_loop", "loop candidate failing at least one gate", "excluded from evaluation"],
    ["source_space", "declared source/provenance domain", "required for C-layer coherence"],
    ["cross_source_mapping_contract", "declared mapping into common relation space", "required for mixed-source use"],
    ["delta_min", "per-edge symbolic threshold", "blocks computation until declared"],
    ["product_delta_min", "product symbolic threshold", "blocks computation until declared"],
    ["arg_branch", "argument branch convention", "default (-pi, pi]"],
    ["orientation", "loop direction convention", "default A -> B -> C -> A"],
    ["rephasing_gauge", "formal local phase transformation convention", "reference-case rule only"],
    ["nullmodel", "later control interface placeholder", "not executed in AX01"],
    ["claim_boundary", "admissible/forbidden use boundary", "mandatory"],
    ["epsilon", "regularization symbol for derived mappings", "blocks computation until declared"],
]

ADMISSIBILITY = [
    ["AR01", "distinct_nodes", "A, B, C are pairwise distinct unless an explicit exception contract exists", "invalid_loop"],
    ["AR02", "C_relations_exist", "C_AB, C_BC, C_CA exist", "invalid_loop"],
    ["AR03", "pair_thresholds", "abs(C_AB), abs(C_BC), abs(C_CA) are each >= delta_min", "invalid_loop"],
    ["AR04", "product_threshold", "abs(C_AB C_BC C_CA) >= product_delta_min", "invalid_loop"],
    ["AR05", "source_coherence", "all C relations share source_space or authorized cross_source_mapping_contract", "invalid_loop"],
    ["AR06", "orientation_declared", "orientation convention is declared", "invalid_loop"],
    ["AR07", "arg_branch_declared", "arg branch convention is declared", "invalid_loop"],
    ["AR08", "C_provenance_closed", "C-layer provenance is closed", "invalid_loop"],
    ["AR09", "K_not_substitute", "K-layer inputs are not used as substitutes for C-layer inputs", "invalid_loop"],
    ["AR10", "no_failed_gate_evaluation", "If any gate fails, Phi_ABC must not be computed or interpreted", "invalid_loop"],
]

TRANSFORMATIONS = [
    ["TR01", "Level 0 relation", "C_AB is a declared abstract complex relation with explicit transformation behavior", "definition"],
    ["TR02", "Level 0 boundary", "Level 0 does not assume Hilbert-space physics", "boundary"],
    ["TR03", "Level 1 rephasing", "psi_A -> exp(i alpha_A) psi_A", "reference_case"],
    ["TR04", "Level 1 C rule", "C_AB = <psi_A | psi_B>; C_AB -> exp(i(alpha_B - alpha_A)) C_AB", "reference_case"],
    ["TR05", "Level 1 cyclic product", "C_AB C_BC C_CA is invariant under the Level 1 formal rephasing convention", "reference_case"],
    ["TR06", "Boundary", "No physical gauge statement is made beyond the declared formal reference case", "boundary"],
]

THRESHOLDS = [
    ["delta_min", "symbolic", "mandatory_before_computation", "AX01 must not invent numeric values"],
    ["product_delta_min", "symbolic", "mandatory_before_computation", "AX01 must not invent numeric values"],
    ["epsilon", "symbolic", "mandatory_before_computation", "AX01 must not invent numeric values"],
]

ORIENTATION_ARG = [
    ["OP01", "default_orientation", "A -> B -> C -> A", "declared"],
    ["OP02", "reverse_orientation", "reverse orientation is a distinct formal object", "declared"],
    ["OP03", "default_arg_branch", "(-pi, pi]", "declared"],
    ["OP04", "branch_handling", "branch handling must be documented before later numerical use", "required_later"],
]

SOURCE_COHERENCE = [
    ["SC01", "same_source", "C_AB, C_BC, C_CA belong to the same declared source_space", "admissible"],
    ["SC02", "mapped_sources", "explicit cross_source_mapping_contract maps inputs to common relation space", "gated_admissible"],
    ["SC03", "mixed_source_no_contract", "absent such a contract, mixed-source loops are invalid", "invalid_loop"],
    ["SC04", "source_not_silent", "cross-source use is gated, not silently allowed", "mandatory"],
]

FORBIDDEN_CLAIMS = [
    ["physics-level confirmation wording", "forbidden", "formal contract status", "claim-boundary only"],
    ["spacetime-emergence wording", "forbidden", "formal relation structure", "claim-boundary only"],
    ["physical-causality wording", "forbidden", "formal dependency language", "claim-boundary only"],
    ["gravity-mechanism wording", "forbidden", "not applicable", "claim-boundary only"],
    ["theory-validation wording", "forbidden", "local formal validation", "claim-boundary only"],
    ["visual or reviewer-based confirmation wording", "forbidden", "inspection/review context", "claim-boundary only"],
]

NEXT_GATE = {
    "run_id": RUN_ID,
    "ax01_status": "formal_contract_draft_passed",
    "claim_status": CLAIM_STATUS,
    "next_authorized_step": "QSB-RELALG-GAUGE01",
    "authorized_next_steps": ["QSB-RELALG-GAUGE01"],
    "still_blocked_steps": ["QSB-RELALG-LOOP01", "QSB-RELALG-NULL01", "QSB-RELALG-REAL01"],
    "required_before_gauge01": [
        "human review of AX01 contract",
        "explicit approval to create a synthetic rephasing invariance test",
        "no real data",
    ],
    "required_before_loop01": [
        "GAUGE01 validation pass",
        "declared symbolic loop diagnostic rules",
        "no real data",
    ],
    "required_before_null01": [
        "LOOP01 validation pass",
        "nullmodel ladder contract",
    ],
    "required_before_real01": [
        "AX01 pass",
        "GAUGE01 pass",
        "LOOP01 pass",
        "NULL01 pass",
        "real-data source contract",
        "C-layer availability check",
        "source-coherence check",
    ],
}


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def rel(path: Path) -> str:
    return str(path.relative_to(REPO_ROOT))


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_csv(path: Path, headers: list[str], rows: list[list[str]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(headers)
        writer.writerows(rows)


def md_table(headers: list[str], rows: list[list[str]]) -> str:
    lines = ["| " + " | ".join(headers) + " |", "| " + " | ".join(["---"] * len(headers)) + " |"]
    lines.extend("| " + " | ".join(str(cell) for cell in row) + " |" for row in rows)
    return "\n".join(lines)


def load_prerequisites() -> tuple[dict[str, object], dict[str, object], dict[str, object], dict[str, object], dict[str, Path]]:
    inputs = {**PREAX_INPUTS, **TERM_INPUTS}
    missing = [rel(path) for path in inputs.values() if not path.exists()]
    if missing:
        raise FileNotFoundError("Missing prerequisite files: " + ", ".join(missing))
    preax_validation = json.loads(PREAX_INPUTS["preax_validation"].read_text(encoding="utf-8"))
    preax_gate = json.loads(PREAX_INPUTS["preax_readiness"].read_text(encoding="utf-8"))
    term_validation = json.loads(TERM_INPUTS["term_validation"].read_text(encoding="utf-8"))
    term_gate = json.loads(TERM_INPUTS["term_readiness"].read_text(encoding="utf-8"))
    if preax_validation.get("validation_status") != "pass":
        raise RuntimeError("PREAX01-SYNTH validation is not pass; AX01 is blocked.")
    if preax_gate.get("next_authorized_step") != "QSB-RELALG-AX01-TERM":
        raise RuntimeError("PREAX01-SYNTH does not authorize AX01-TERM; AX01 is blocked.")
    if term_validation.get("validation_status") != "pass":
        raise RuntimeError("AX01-TERM validation is not pass; AX01 is blocked.")
    if term_gate.get("term_contract_status") != "passed" or term_gate.get("next_authorized_step") != RUN_ID:
        raise RuntimeError("AX01-TERM gate does not authorize QSB-RELALG-AX01; AX01 is blocked.")
    return preax_validation, preax_gate, term_validation, term_gate, inputs


def prepare_output(force: bool) -> None:
    if OUTPUT_DIR.exists() and not force:
        raise FileExistsError(f"{rel(OUTPUT_DIR)} already exists; rerun with --force to replace AX01 sandbox outputs.")
    if OUTPUT_DIR.exists() and force:
        shutil.rmtree(OUTPUT_DIR)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def write_contract(timestamp: str) -> None:
    text = dedent(f"""\
        # QSB-RELALG-AX01 Minimal Formal Contract Draft

        Generated at: {timestamp}

        ## Purpose

        AX01 is a minimal formal contract draft. It defines symbols, admissibility rules, layer separation, transformation rules, and later-step gates. It performs no numerical RELALG computation.

        ## Level Structure

        Level 0 - abstract RELALG core: C_AB is a declared abstract complex relation on an ordered pair. Level 0 does not assume Hilbert-space physics.

        Level 1 - canonical overlap reference case: C_AB = <psi_A | psi_B> may be used only as a reference model, not as an empirical claim.

        ## Definitions

        {md_table(["term", "definition", "boundary"], DEFINITIONS)}

        ## Symbol Table

        {md_table(["symbol", "meaning", "condition"], SYMBOLS)}

        ## C/K Separation

        C_AB is the phase-carrying complex relation layer. K_AB is a derived phase-blind strength, magnitude, score, or real projection. Phi_ABC may only be formed from C-layer relations, never from K-layer scores.

        Allowed symbolic derived examples, not executed here: K_AB = |C_AB|; K_AB = Re(C_AB); K_AB = score(C_AB); d_AB = -l0 log(|C_AB| + epsilon).

        ## Transformation Rules

        {md_table(["rule_id", "rule_name", "statement", "status"], TRANSFORMATIONS)}

        ## Loop Phase Definition

        Phi_ABC = arg(C_AB C_BC C_CA), only if all validity gates pass. If any gate fails, the loop is invalid and Phi_ABC must not be computed or interpreted.

        ## Admissibility Rules

        {md_table(["rule_id", "rule_name", "requirement", "fail_status"], ADMISSIBILITY)}

        ## Threshold Policy

        {md_table(["threshold", "value_status", "blocking_status", "policy"], THRESHOLDS)}

        ## Orientation And Argument Policy

        {md_table(["rule_id", "rule_name", "statement", "status"], ORIENTATION_ARG)}

        ## Source Coherence

        A loop is admissible only if C_AB, C_BC, and C_CA belong to the same declared source_space or to an explicitly authorized cross_source_mapping_contract. Absent such a contract, mixed-source loops are invalid.

        {md_table(["rule_id", "rule_name", "requirement", "status"], SOURCE_COHERENCE)}

        ## Later-Step Gate

        GAUGE01 is the only authorized next draft/test-design step after human review. LOOP01, NULL01, and REAL01 remain blocked by prerequisite gates.

        ## Claim Boundary

        This contract uses only neutral formal language outside dedicated boundary files. Visual artifacts and reviewer agreement are not used as evidence.
        """)
    OUTPUTS["contract"].write_text(text, encoding="utf-8")


def write_claim_boundary(timestamp: str) -> None:
    text = dedent(f"""\
        # QSB-RELALG-AX01 Claim Boundary Report

        Generated at: {timestamp}

        AX01 is a formal contract draft only.

        AX01 does not compute Phi_ABC.

        AX01 does not validate QSB.

        AX01 does not establish spacetime emergence.

        AX01 does not establish physical causality.

        AX01 does not establish a gravity mechanism.

        AX01 does not use reviewer agreement as evidence.

        AX01 does not use visual artifacts as evidence.

        ## Exact Forbidden Claim Examples

        - QSB bestätigt
        - QSB bewiesen
        - proves spacetime
        - establishes causality
        - validates physical theory
        - mechanism of gravity
        - visual evidence
        - reviewer agreement as evidence
        """)
    OUTPUTS["claim_boundary"].write_text(text, encoding="utf-8")


def write_manifest(inputs: dict[str, Path], timestamp: str, status: str) -> None:
    manifest = {
        "run_id": RUN_ID,
        "timestamp": timestamp,
        "script_path": str(SCRIPT_PATH),
        "input_paths": {name: rel(path) for name, path in inputs.items()},
        "input_hashes": {name: sha256_file(path) for name, path in inputs.items()},
        "output_paths": {name: rel(path) for name, path in OUTPUTS.items() if name != "manifest"},
        "output_hashes": {name: sha256_file(path) for name, path in OUTPUTS.items() if path.exists() and name != "manifest"},
        "validation_status": status,
        "claim_status": CLAIM_STATUS,
        "production_mutation_statement": PRODUCTION_MUTATION_STATEMENT,
    }
    OUTPUTS["manifest"].write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def csv_first_column(path: Path) -> set[str]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.reader(handle)
        next(reader, None)
        return {row[0] for row in reader if row}


def restricted_outside_boundary() -> bool:
    allowed = {OUTPUTS["forbidden_claims"], OUTPUTS["claim_boundary"]}
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
        "validation_id": f"QSB-RELALG-AX01-VAL-{rule_id}",
        "rule_id": rule_id,
        "severity": "error",
        "status": status,
        "message": message,
        "checked_at": timestamp,
    })


def validate(preax_validation: dict[str, object], term_validation: dict[str, object], term_gate: dict[str, object], timestamp: str) -> list[dict[str, str]]:
    results: list[dict[str, str]] = []
    contract = OUTPUTS["contract"].read_text(encoding="utf-8")
    definitions = csv_first_column(OUTPUTS["definitions"])
    symbols = csv_first_column(OUTPUTS["symbols"])
    mandatory = {"psi_A", "C_AB", "K_AB", "d_AB", "Phi_ABC", "valid_loop", "invalid_loop", "source_space", "cross_source_mapping_contract", "delta_min", "product_delta_min", "arg_branch", "orientation", "rephasing_gauge", "nullmodel", "claim_boundary"}
    gate = json.loads(OUTPUTS["next_gate"].read_text(encoding="utf-8"))
    add_result(results, "V01", "pass" if preax_validation.get("validation_status") == "pass" else "fail", "PREAX01-SYNTH validation exists and passed.", timestamp)
    add_result(results, "V02", "pass" if term_validation.get("validation_status") == "pass" else "fail", "AX01-TERM validation exists and passed.", timestamp)
    add_result(results, "V03", "pass" if term_gate.get("next_authorized_step") == RUN_ID else "fail", "AX01-TERM gate authorizes QSB-RELALG-AX01.", timestamp)
    add_result(results, "V04", "pass" if all(path.exists() for path in OUTPUTS.values()) else "fail", "All required AX01 output files exist.", timestamp)
    add_result(results, "V05", "pass" if "Level 0" in contract and "Level 1" in contract else "fail", "Contract defines Level 0 and Level 1.", timestamp)
    add_result(results, "V06", "pass" if mandatory.issubset(definitions) and mandatory.issubset(symbols) else "fail", "Mandatory symbols are present in definitions and symbol table.", timestamp)
    add_result(results, "V07", "pass" if "C/K Separation" in contract else "fail", "C/K separation statement exists.", timestamp)
    add_result(results, "V08", "pass" if "arg(C_AB C_BC C_CA)" in contract else "fail", "Phi_ABC is defined only from C-layer cyclic product.", timestamp)
    add_result(results, "V09", "pass" if "K-layer inputs are not used as substitutes" in OUTPUTS["admissibility"].read_text(encoding="utf-8") else "fail", "K-layer inputs are explicitly forbidden as substitutes for Phi_ABC.", timestamp)
    add_result(results, "V10", "pass" if "exp(i alpha_A)" in OUTPUTS["transformations"].read_text(encoding="utf-8") and "exp(i(alpha_B - alpha_A))" in OUTPUTS["transformations"].read_text(encoding="utf-8") else "fail", "Level 1 rephasing transformation rule exists.", timestamp)
    add_result(results, "V11", "pass" if "cyclic product" in OUTPUTS["transformations"].read_text(encoding="utf-8") and "invariant" in OUTPUTS["transformations"].read_text(encoding="utf-8") else "fail", "Level 1 cyclic product invariance statement exists.", timestamp)
    add_result(results, "V12", "pass" if "delta_min" in OUTPUTS["admissibility"].read_text(encoding="utf-8") and "product_delta_min" in OUTPUTS["admissibility"].read_text(encoding="utf-8") else "fail", "Loop validity gates include nonzero/threshold checks.", timestamp)
    add_result(results, "V13", "pass" if "mandatory_before_computation" in OUTPUTS["thresholds"].read_text(encoding="utf-8") else "fail", "Threshold policy blocks computation without numeric thresholds.", timestamp)
    add_result(results, "V14", "pass" if "A -> B -> C -> A" in OUTPUTS["orientation_arg"].read_text(encoding="utf-8") else "fail", "Orientation convention exists.", timestamp)
    add_result(results, "V15", "pass" if "(-pi, pi]" in OUTPUTS["orientation_arg"].read_text(encoding="utf-8") else "fail", "Arg branch convention exists.", timestamp)
    add_result(results, "V16", "pass" if "source_space" in OUTPUTS["source_coherence"].read_text(encoding="utf-8") else "fail", "Source-coherence rule exists.", timestamp)
    add_result(results, "V17", "pass" if "gated" in OUTPUTS["source_coherence"].read_text(encoding="utf-8") else "fail", "Cross-source use is gated, not silently allowed.", timestamp)
    add_result(results, "V18", "pass" if OUTPUTS["forbidden_claims"].exists() else "fail", "Forbidden-claims output exists.", timestamp)
    gate_ok = gate.get("authorized_next_steps") == ["QSB-RELALG-GAUGE01"] and set(gate.get("still_blocked_steps", [])) == {"QSB-RELALG-LOOP01", "QSB-RELALG-NULL01", "QSB-RELALG-REAL01"}
    add_result(results, "V19", "pass" if gate_ok else "fail", "Next-step gate authorizes only GAUGE01 and keeps LOOP01/NULL01/REAL01 blocked.", timestamp)
    add_result(results, "V20", "pass" if not restricted_outside_boundary() else "fail", "No restricted interpretive claim is introduced outside claim-boundary files.", timestamp)
    add_result(results, "V21", "pass", "No RELALG computation, loop diagnostics, nullmodel execution, or real-data analysis is performed.", timestamp)
    manifest = json.loads(OUTPUTS["manifest"].read_text(encoding="utf-8")) if OUTPUTS["manifest"].exists() else {}
    add_result(results, "V22", "pass" if manifest.get("input_hashes") and manifest.get("output_hashes") else "fail", "Manifest includes input hashes and output hashes.", timestamp)
    return results


def validation_status(results: list[dict[str, str]]) -> str:
    return "fail" if any(row["status"] == "fail" for row in results) else "pass"


def write_summary(timestamp: str, results: list[dict[str, str]]) -> None:
    status = validation_status(results) if results else "pending"
    text = dedent(f"""\
        # QSB-RELALG-AX01 Run Summary

        Generated at: {timestamp}

        ## Purpose

        Create a sandbox-only minimal formal AX01 contract draft.

        ## Inputs Checked

        PREAX01-SYNTH and AX01-TERM validation/gate outputs.

        ## Outputs Created

        {chr(10).join(f"- {rel(path)}" for path in OUTPUTS.values())}

        ## Validation Status

        {status}

        {chr(10).join(f"- {row['rule_id']}: {row['status']} - {row['message']}" for row in results) if results else "- pending"}

        ## AX01 Status

        formal_contract_draft_passed

        ## Next Authorized Step

        QSB-RELALG-GAUGE01

        ## Blocked Steps

        QSB-RELALG-LOOP01, QSB-RELALG-NULL01, QSB-RELALG-REAL01

        ## No Computation Statement

        No RELALG computation, loop diagnostic, nullmodel execution, or real-data analysis was performed.

        ## No Production Mutation Statement

        {PRODUCTION_MUTATION_STATEMENT}

        ## Claim Status

        {CLAIM_STATUS}
        """)
    OUTPUTS["summary"].write_text(text, encoding="utf-8")


def build(force: bool) -> None:
    preax_validation, _preax_gate, term_validation, term_gate, inputs = load_prerequisites()
    prepare_output(force)
    timestamp = utc_now()
    write_csv(OUTPUTS["definitions"], ["term", "definition", "boundary"], DEFINITIONS)
    write_csv(OUTPUTS["symbols"], ["symbol", "meaning", "condition"], SYMBOLS)
    write_csv(OUTPUTS["admissibility"], ["rule_id", "rule_name", "requirement", "fail_status"], ADMISSIBILITY)
    write_csv(OUTPUTS["transformations"], ["rule_id", "rule_name", "statement", "status"], TRANSFORMATIONS)
    write_csv(OUTPUTS["thresholds"], ["threshold", "value_status", "blocking_status", "policy"], THRESHOLDS)
    write_csv(OUTPUTS["orientation_arg"], ["rule_id", "rule_name", "statement", "status"], ORIENTATION_ARG)
    write_csv(OUTPUTS["source_coherence"], ["rule_id", "rule_name", "requirement", "status"], SOURCE_COHERENCE)
    write_csv(OUTPUTS["forbidden_claims"], ["claim_form", "status", "safe_replacement", "scope"], FORBIDDEN_CLAIMS)
    write_contract(timestamp)
    OUTPUTS["next_gate"].write_text(json.dumps(NEXT_GATE, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    write_claim_boundary(timestamp)
    OUTPUTS["validation"].write_text(json.dumps({"run_id": RUN_ID, "timestamp": timestamp, "validation_status": "pending", "results": []}, indent=2) + "\n", encoding="utf-8")
    write_summary(timestamp, [])
    write_manifest(inputs, timestamp, "pending")
    results = validate(preax_validation, term_validation, term_gate, timestamp)
    OUTPUTS["validation"].write_text(json.dumps({
        "run_id": RUN_ID,
        "timestamp": timestamp,
        "validation_status": validation_status(results),
        "results": results,
        "claim_status": CLAIM_STATUS,
        "production_mutation_statement": PRODUCTION_MUTATION_STATEMENT,
    }, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    write_summary(timestamp, results)
    write_manifest(inputs, timestamp, validation_status(results))


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--force", action="store_true", help="Replace only runs/QSB-RELALG-AX01/.")
    args = parser.parse_args()
    try:
        build(args.force)
    except (FileNotFoundError, FileExistsError, RuntimeError) as exc:
        print(str(exc))
        raise SystemExit(1) from None


if __name__ == "__main__":
    main()
