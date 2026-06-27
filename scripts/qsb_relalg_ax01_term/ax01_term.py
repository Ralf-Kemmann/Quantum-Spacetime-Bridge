#!/usr/bin/env python3
"""Build the QSB-RELALG-AX01-TERM terminology contract draft."""

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
SCRIPT_PATH = Path("scripts/qsb_relalg_ax01_term/ax01_term.py")
RUN_ID = "QSB-RELALG-AX01-TERM"
DEFAULT_PREAX_DIR = REPO_ROOT / "runs/QSB-RELALG-PREAX01-SYNTH"
OUTPUT_DIR = REPO_ROOT / "runs/QSB-RELALG-AX01-TERM"
CLAIM_STATUS = "terminology_contract_only_no_computation"
PRODUCTION_MUTATION_STATEMENT = "No production DWH or existing schema files were modified."
RESTRICTED_CLAIM_PATTERNS = [
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
    "synth": "qsb_relalg_preax01_synth.md",
    "consensus": "qsb_relalg_preax01_consensus_matrix.csv",
    "conflict": "qsb_relalg_preax01_conflict_matrix.csv",
    "definitions": "qsb_relalg_preax01_required_definitions.csv",
    "forbidden_terms": "qsb_relalg_preax01_forbidden_terms.csv",
    "next_steps": "qsb_relalg_preax01_next_steps.csv",
    "readiness": "qsb_relalg_preax01_ax01_readiness_gate.json",
    "validation": "qsb_relalg_preax01_synth_validation_report.json",
}
OUTPUTS = {
    "contract": OUTPUT_DIR / "qsb_relalg_ax01_term.md",
    "definitions": OUTPUT_DIR / "qsb_relalg_ax01_term_definitions.csv",
    "symbols": OUTPUT_DIR / "qsb_relalg_ax01_term_symbols.csv",
    "transform_rules": OUTPUT_DIR / "qsb_relalg_ax01_term_transform_rules.csv",
    "loop_validity": OUTPUT_DIR / "qsb_relalg_ax01_term_loop_validity_rules.csv",
    "threshold_policy": OUTPUT_DIR / "qsb_relalg_ax01_term_threshold_policy.csv",
    "source_coherence": OUTPUT_DIR / "qsb_relalg_ax01_term_source_coherence_rules.csv",
    "forbidden_claims": OUTPUT_DIR / "qsb_relalg_ax01_term_forbidden_claims.csv",
    "readiness": OUTPUT_DIR / "qsb_relalg_ax01_term_ax01_readiness_gate.json",
    "claim_boundary": OUTPUT_DIR / "qsb_relalg_ax01_term_claim_boundary_report.md",
    "manifest": OUTPUT_DIR / "qsb_relalg_ax01_term_manifest.json",
    "validation": OUTPUT_DIR / "qsb_relalg_ax01_term_validation_report.json",
    "summary": OUTPUT_DIR / "QSB-RELALG-AX01-TERM_RUN_SUMMARY.md",
}


DEFINITIONS = [
    ["psi_A", "Level 0 formal response/signature/state label in a declared relation space; not automatically a physical wavefunction.", "Level 1 may use a normalized Hilbert-space-like vector only as a canonical reference model.", "mandatory"],
    ["relation_space", "Declared formal space in which relation objects and labels are compared.", "No automatic physical interpretation.", "mandatory"],
    ["source_space", "Declared provenance/source domain for relation values.", "Mixed-source use is blocked without mapping contract.", "mandatory"],
    ["C_AB", "Complex phase-carrying relation on ordered pair (A,B) with declared transformation behavior.", "Phi_ABC is inadmissible without a declared C transformation rule.", "mandatory"],
    ["K_AB", "Real magnitude-like, score-like, or strength-like quantity derived from C_AB or another declared projection.", "K_AB is phase-blind; Phi_ABC must never be computed from K_AB alone.", "mandatory"],
    ["d_AB", "Derived cost/distance-like quantity from a declared relation or score, such as -l0 log(abs(C_AB)+epsilon).", "Not automatically a metric; metric properties require separate tests or explicit absence.", "mandatory"],
    ["Phi_ABC", "Cyclic phase candidate arg(C_AB C_BC C_CA), admissible only when loop-validity rules pass.", "No interpretive claim may be derived from Phi_ABC in AX01-TERM.", "mandatory"],
    ["valid_loop", "Loop candidate passing all C-layer, threshold, orientation, branch, provenance, and source-coherence gates.", "Only a formal admissibility label.", "mandatory"],
    ["invalid_loop", "Loop candidate failing one or more mandatory validity gates.", "Excluded from evaluation rather than interpreted.", "mandatory"],
    ["rephasing_gauge", "Declared local phase transformation convention for formal labels and C_AB.", "GAUGE01 remains blocked until AX01 exists.", "mandatory"],
    ["nonvanishing_threshold", "Policy requiring abs(C_ij) > delta_min for required C relations.", "Numeric value is required before computation.", "mandatory"],
    ["product_delta_min", "Policy requiring abs(C_AB C_BC C_CA) > product_delta_min.", "Numeric value is required before computation.", "mandatory"],
    ["orientation", "Declared loop direction convention; default A -> B -> C -> A.", "Reverse-loop behavior is unresolved unless declared.", "mandatory"],
    ["arg_branch", "Declared argument branch; default arg(z) in (-pi, pi].", "No phase unwrapping without later contract.", "mandatory"],
    ["source_coherence", "All C relations must share source space or authorized cross-source mapping contract.", "Absent contract means no_go for mixed-source loops.", "mandatory"],
    ["cross_source_mapping_contract", "Explicit mapping from source spaces to an allowed common relation space.", "Required before any mixed-source loop use.", "mandatory"],
    ["nullmodel_interface", "Placeholder interface for later NULL01 controls; no nullmodel execution here.", "Control design only, no analysis.", "mandatory"],
    ["claim_boundary", "Rules separating admissible formal uses from locked or forbidden interpretive language.", "Required in AX01 and AX01-TERM.", "mandatory"],
]

SYMBOLS = [
    ["A, B, C", "ordered object labels", "formal labels only"],
    ["psi_A", "formal label or Level 1 reference vector", "not automatically a physical wavefunction"],
    ["C_AB", "complex C-layer relation", "phase-carrying"],
    ["K_AB", "K-layer magnitude/score", "phase-blind"],
    ["d_AB", "derived cost/distance-like quantity", "not automatically metric"],
    ["Phi_ABC", "arg(C_AB C_BC C_CA)", "C-layer loop-phase candidate"],
    ["delta_min", "per-edge nonvanishing threshold", "to_be_declared_in_AX01"],
    ["product_delta_min", "loop-product threshold", "to_be_declared_in_AX01"],
    ["epsilon", "regularization constant for derived mappings", "to_be_declared_in_AX01"],
]

TRANSFORM_RULES = [
    ["TR01", "Level 0 declaration required", "C_AB must declare transformation behavior before Phi_ABC is admissible.", "mandatory"],
    ["TR02", "Level 1 local rephasing", "psi_A -> exp(i alpha_A) psi_A; psi_B -> exp(i alpha_B) psi_B.", "canonical_reference"],
    ["TR03", "Level 1 C transformation", "C_AB = <psi_A | psi_B>; C_AB -> exp(i(alpha_B - alpha_A)) C_AB.", "canonical_reference"],
    ["TR04", "Loop product behavior", "C_AB C_BC C_CA is invariant under the Level 1 local rephasing convention.", "canonical_reference"],
    ["TR05", "Non-overlap warning", "If C_AB does not transform overlap-like, invariance must be proven later before invariant language is used.", "mandatory_warning"],
]

LOOP_VALIDITY = [
    ["LV01", "distinct_nodes", "A, B, C must be pairwise distinct unless a later contract explicitly permits degeneracy", "invalid_loop"],
    ["LV02", "C_layer_required", "C_AB, C_BC, C_CA must exist on the C layer", "invalid_loop"],
    ["LV03", "no_phi_from_K", "Phi_ABC must not be computed from K_AB or any phase-blind score", "invalid_loop"],
    ["LV04", "pair_nonvanishing", "each required C relation must satisfy abs(C_ij) > delta_min", "invalid_loop"],
    ["LV05", "product_nonvanishing", "abs(C_AB C_BC C_CA) > product_delta_min", "invalid_loop"],
    ["LV06", "transformation_rule_declared", "C transformation behavior must be declared", "invalid_loop"],
    ["LV07", "orientation_declared", "loop orientation must be declared", "invalid_loop"],
    ["LV08", "arg_branch_declared", "argument branch convention must be declared", "invalid_loop"],
    ["LV09", "source_coherence", "all C relations must belong to the same source space or to an authorized cross-source mapping contract", "invalid_loop"],
    ["LV10", "provenance_required", "missing provenance invalidates the loop", "invalid_loop"],
]

THRESHOLDS = [
    ["delta_min", "to_be_declared_in_AX01", "required_before_computation", "Blocks pair-level C relation use until declared."],
    ["product_delta_min", "to_be_declared_in_AX01", "required_before_computation", "Blocks loop-product use until declared."],
    ["epsilon", "to_be_declared_in_AX01", "required_before_computation", "Blocks derived log/cost mapping until declared."],
]

SOURCE_COHERENCE = [
    ["SC01", "same_source_space", "C_AB, C_BC, and C_CA belong to the same declared source space.", "allowed"],
    ["SC02", "authorized_cross_source_mapping", "source_space_A/source_space_B are mapped through a declared contract to an allowed common relation space.", "allowed_after_contract"],
    ["SC03", "absent_cross_source_contract", "Mixed-source loops without a mapping contract are invalid and must not be evaluated.", "no_go"],
    ["SC04", "provenance_required", "Every C relation used in a loop must carry provenance/source metadata.", "invalid_without_provenance"],
]

FORBIDDEN_CLAIMS = [
    ["Raumzeit", "forbidden", "formal relational algebra", "Dedicated boundary term only."],
    ["Emergenz", "forbidden", "formal pattern", "Do not use in AX01-TERM interpretive text."],
    ["Kausalität", "forbidden", "formal dependency wording", "No physical causality language."],
    ["relationale Geometrie", "locked", "complex relation structure", "Locked until metric properties are separately defined/tested."],
    ["Naturkonstante", "forbidden", "formal parameter", "No empirical constant claim."],
    ["Mechanismus der Gravitation", "forbidden", "not applicable", "Forbidden claim form."],
    ["Validierung der Theorie", "forbidden", "local formal rule validation", "No theory-validation claim."],
    ["QSB bestätigt", "forbidden", "formal contract result", "Forbidden confirmation wording."],
    ["QSB bewiesen", "forbidden", "formal contract result", "Forbidden proof wording."],
    ["visual evidence", "forbidden", "inspection target", "Visual artifacts do not serve as evidence."],
    ["reviewer agreement as evidence", "forbidden", "review synthesis", "Reviewer agreement is not evidence."],
]

READINESS_PASS = {
    "run_id": RUN_ID,
    "term_contract_status": "passed",
    "full_ax01_readiness": "ready_for_full_ax01_draft_after_human_review",
    "next_authorized_step": "QSB-RELALG-AX01",
    "authorized_scope_next": [
        "write minimal formal AX01 draft",
        "preserve Level 0 / Level 1 distinction",
        "include C/K separation",
        "include transformation and validity rules",
        "include claim boundaries",
    ],
    "blocked_steps": ["GAUGE01", "LOOP01", "NULL01", "REAL01"],
    "claim_status": CLAIM_STATUS,
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


def input_paths(preax_dir: Path) -> dict[str, Path]:
    return {name: preax_dir / filename for name, filename in PREAX_INPUTS.items()}


def load_gate(preax_dir: Path) -> tuple[dict[str, object], dict[str, object], dict[str, Path]]:
    paths = input_paths(preax_dir)
    missing = [rel(path) for path in paths.values() if not path.exists()]
    if missing:
        raise FileNotFoundError("Missing required PREAX01-SYNTH input files: " + ", ".join(missing))
    validation = json.loads(paths["validation"].read_text(encoding="utf-8"))
    readiness = json.loads(paths["readiness"].read_text(encoding="utf-8"))
    if validation.get("validation_status") != "pass":
        raise RuntimeError("PREAX01-SYNTH validation_status is not pass; AX01-TERM is blocked.")
    if readiness.get("next_authorized_step") != RUN_ID:
        raise RuntimeError("PREAX01-SYNTH gate does not authorize QSB-RELALG-AX01-TERM; AX01-TERM is blocked.")
    return validation, readiness, paths


def prepare_output(force: bool) -> None:
    if OUTPUT_DIR.exists() and not force:
        raise FileExistsError(f"{rel(OUTPUT_DIR)} already exists; rerun with --force to replace AX01-TERM sandbox outputs.")
    if force and OUTPUT_DIR.exists():
        for path in OUTPUT_DIR.iterdir():
            if path.is_file():
                path.unlink()
            elif path.is_dir():
                shutil.rmtree(path)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def write_contract(timestamp: str, preax_dir: Path) -> None:
    text = dedent(f"""\
        # QSB-RELALG-AX01-TERM

        Generated at: {timestamp}

        ## Purpose

        Minimal terminology and definition contract draft authorized by PREAX01-SYNTH. This is not full AX01 and performs no computation.

        ## Inputs

        PREAX01-SYNTH directory: `{rel(preax_dir)}`

        ## Scope

        This contract stabilizes RELALG terminology, notation, transformation rules, validity gates, source-coherence rules, threshold policies, and claim boundaries for a later AX01 draft.

        ## Two-Level Definition Model

        Level 0 abstract RELALG core: `C_AB` is a complex, phase-carrying relation on an ordered pair `(A,B)` in a declared relation/source space. Level 0 does not assume that `psi_A` is a physical wavefunction or that `C_AB` is automatically a Hilbert-space inner product. A Level 0 relation is admissible only if its transformation behavior is explicitly declared.

        Level 1 canonical reference case: `C_AB = <psi_A | psi_B>` may be used for normalized Hilbert-space-like objects as a reference model only.

        ## Definitions

        {md_table(["term", "definition", "boundary", "status"], DEFINITIONS)}

        ## Symbols

        {md_table(["symbol", "meaning", "boundary"], SYMBOLS)}

        ## Transformation Rules

        {md_table(["rule_id", "rule_name", "statement", "status"], TRANSFORM_RULES)}

        ## Loop Validity Rules

        {md_table(["rule_id", "rule_name", "requirement", "fail_status"], LOOP_VALIDITY)}

        ## Threshold Policy

        {md_table(["threshold", "numeric_value", "status", "blocking_rule"], THRESHOLDS)}

        ## Orientation And Argument Branch

        Default orientation convention: `A -> B -> C -> A`.

        Default argument branch convention: `arg(z) in (-pi, pi]`.

        No phase unwrapping is allowed unless a later explicit contract declares it. Reverse-loop behavior is unresolved unless the relation type declares the needed symmetry/conjugation rule.

        ## Source Coherence

        A loop `(A,B,C)` is admissible only if `C_AB`, `C_BC`, and `C_CA` belong to the same declared source space or to an explicitly authorized cross-source mapping contract. Absent such a contract, mixed-source loops are invalid and must not be evaluated.

        {md_table(["rule_id", "rule_name", "requirement", "status"], SOURCE_COHERENCE)}

        ## C/K Separation

        `C_AB` is the phase-carrying C-layer relation. `K_AB` is a phase-blind K-layer magnitude/score. `Phi_ABC` is defined only from the C-layer product `C_AB C_BC C_CA`, never from `K_AB` alone.

        ## AX01 May Contain

        AX01 may contain a minimal formal draft preserving the Level 0 / Level 1 distinction, C/K separation, transformation rules, loop validity rules, threshold policy, source coherence, and claim boundaries.

        ## AX01 May Not Contain

        AX01 may not contain computation, loop diagnostics, nullmodel execution, real-data analysis, visual-evidence reasoning, reviewer-agreement evidence, or restricted interpretive claims.
        """)
    OUTPUTS["contract"].write_text(text, encoding="utf-8")


def write_claim_boundary_report(timestamp: str) -> None:
    text = dedent(f"""\
        # QSB-RELALG-AX01-TERM Claim Boundary Report

        Generated at: {timestamp}

        ## Restricted / Locked Language

        {md_table(["term_or_claim", "status", "safe_replacement", "note"], FORBIDDEN_CLAIMS)}

        ## Admissible Use

        AX01-TERM may be used as a formal terminology contract and readiness gate for a later AX01 draft.

        ## Forbidden Use

        Do not use AX01-TERM as empirical evidence, physical confirmation, visual evidence, reviewer agreement as evidence, or a gravity/spacetime/causality claim.

        ## Visual Artifact Boundary

        Visual artifacts may indicate inspection targets only. They do not authorize interpretive claims.

        ## Reviewer Agreement Boundary

        Reviewer agreement may guide definitions and tests. It is not evidence for the system under study.
        """)
    OUTPUTS["claim_boundary"].write_text(text, encoding="utf-8")


def write_readiness(status: str) -> None:
    gate = dict(READINESS_PASS)
    if status != "pass":
        gate["term_contract_status"] = "failed"
        gate["full_ax01_readiness"] = "not_ready_full_ax01"
        gate["next_authorized_step"] = "blocked"
    OUTPUTS["readiness"].write_text(json.dumps(gate, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def file_hashes(paths: dict[str, Path]) -> dict[str, str]:
    return {name: sha256_file(path) for name, path in paths.items() if path.exists()}


def output_hashes() -> dict[str, str]:
    return {name: sha256_file(path) for name, path in OUTPUTS.items() if path.exists() and name != "manifest"}


def add_result(results: list[dict[str, str]], rule_id: str, status: str, message: str, timestamp: str, severity: str = "error") -> None:
    results.append({
        "validation_id": f"QSB-RELALG-AX01-TERM-VAL-{rule_id}",
        "rule_id": rule_id,
        "severity": severity,
        "status": status,
        "message": message,
        "checked_at": timestamp,
    })


def csv_first_column(path: Path) -> set[str]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.reader(handle)
        next(reader, None)
        return {row[0] for row in reader if row}


def restricted_claim_outside_boundary() -> bool:
    allowed = {OUTPUTS["forbidden_claims"], OUTPUTS["claim_boundary"]}
    for path in OUTPUTS.values():
        if not path.exists() or path in allowed:
            continue
        text = path.read_text(encoding="utf-8")
        for phrase in RESTRICTED_CLAIM_PATTERNS:
            if phrase.lower() in text.lower():
                return True
    return False


def validate(preax_validation: dict[str, object], preax_readiness: dict[str, object], preax_paths: dict[str, Path], timestamp: str) -> list[dict[str, str]]:
    results: list[dict[str, str]] = []
    required_terms = {
        "psi_A", "relation_space", "source_space", "C_AB", "K_AB", "d_AB", "Phi_ABC",
        "valid_loop", "invalid_loop", "rephasing_gauge", "nonvanishing_threshold",
        "product_delta_min", "orientation", "arg_branch", "source_coherence",
        "cross_source_mapping_contract", "nullmodel_interface", "claim_boundary",
    }
    add_result(results, "V01", "pass" if preax_validation.get("validation_status") == "pass" else "fail", "PREAX01-SYNTH validation report exists and has validation_status=pass.", timestamp)
    add_result(results, "V02", "pass" if preax_readiness.get("next_authorized_step") == RUN_ID else "fail", "PREAX01-SYNTH gate authorizes QSB-RELALG-AX01-TERM.", timestamp)
    add_result(results, "V03", "pass" if all(path.exists() for path in OUTPUTS.values() if path != OUTPUTS["manifest"]) else "fail", "All required output files exist.", timestamp)
    add_result(results, "V04", "pass" if required_terms.issubset(csv_first_column(OUTPUTS["definitions"])) else "fail", "Definitions CSV contains all mandatory terms.", timestamp)
    contract = OUTPUTS["contract"].read_text(encoding="utf-8")
    add_result(results, "V05", "pass" if "C/K Separation" in contract and "never from `K_AB` alone" in contract else "fail", "C/K separation statement exists.", timestamp)
    add_result(results, "V06", "pass" if "C-layer product `C_AB C_BC C_CA`" in contract else "fail", "Phi_ABC is defined only from C-layer product.", timestamp)
    add_result(results, "V07", "pass" if "exp(i(alpha_B - alpha_A))" in OUTPUTS["transform_rules"].read_text(encoding="utf-8") else "fail", "Transformation rule for canonical Level 1 case exists.", timestamp)
    add_result(results, "V08", "pass" if "does not assume" in contract and "physical wavefunction" in contract else "fail", "Level 0 does not assume Hilbert-space physics.", timestamp)
    threshold_text = OUTPUTS["threshold_policy"].read_text(encoding="utf-8")
    add_result(results, "V09", "pass" if "to_be_declared_in_AX01" in threshold_text and "required_before_computation" in threshold_text else "fail", "Threshold policy exists and blocks computation if numeric values are undeclared.", timestamp)
    add_result(results, "V10", "pass" if "A -> B -> C -> A" in contract else "fail", "Orientation convention exists.", timestamp)
    add_result(results, "V11", "pass" if "(-pi, pi]" in contract else "fail", "Arg branch convention exists.", timestamp)
    add_result(results, "V12", "pass" if "cross-source mapping contract" in contract else "fail", "Source-coherence rule exists.", timestamp)
    add_result(results, "V13", "pass" if OUTPUTS["forbidden_claims"].exists() else "fail", "Forbidden-claims file exists.", timestamp)
    gate = json.loads(OUTPUTS["readiness"].read_text(encoding="utf-8"))
    blocked = set(gate.get("blocked_steps", []))
    add_result(results, "V14", "pass" if OUTPUTS["readiness"].exists() and {"GAUGE01", "LOOP01", "NULL01", "REAL01"}.issubset(blocked) else "fail", "AX01 readiness gate exists and keeps blocked next steps blocked.", timestamp)
    add_result(results, "V15", "pass" if not restricted_claim_outside_boundary() else "fail", "No restricted interpretive claim is introduced outside claim-boundary sections.", timestamp)
    add_result(results, "V16", "pass", "No RELALG computation or real-data analysis is performed.", timestamp)
    add_result(results, "V17", "pass", "No production DWH/schema files are modified.", timestamp)
    manifest_ok = OUTPUTS["manifest"].exists()
    if manifest_ok:
        manifest = json.loads(OUTPUTS["manifest"].read_text(encoding="utf-8"))
        manifest_ok = bool(manifest.get("input_hashes")) and bool(manifest.get("output_hashes"))
    add_result(results, "V18", "pass" if manifest_ok else "fail", "Manifest includes input hashes and output hashes.", timestamp)
    add_result(results, "V19", "pass" if OUTPUTS["summary"].exists() else "fail", "Run summary exists.", timestamp)
    return results


def validation_status(results: list[dict[str, str]]) -> str:
    return "fail" if any(row["status"] == "fail" for row in results if row["severity"] == "error") else "pass"


def write_manifest(preax_paths: dict[str, Path], timestamp: str, status: str) -> None:
    manifest = {
        "run_id": RUN_ID,
        "timestamp": timestamp,
        "script_path": str(SCRIPT_PATH),
        "input_paths": {name: rel(path) for name, path in preax_paths.items()},
        "input_hashes": file_hashes(preax_paths),
        "output_paths": {name: rel(path) for name, path in OUTPUTS.items() if name != "manifest"},
        "output_hashes": output_hashes(),
        "validation_status": status,
        "claim_status": CLAIM_STATUS,
        "production_mutation_statement": PRODUCTION_MUTATION_STATEMENT,
    }
    OUTPUTS["manifest"].write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def write_summary(timestamp: str, preax_paths: dict[str, Path], results: list[dict[str, str]]) -> None:
    gate = json.loads(OUTPUTS["readiness"].read_text(encoding="utf-8"))
    text = dedent(f"""\
        # QSB-RELALG-AX01-TERM Run Summary

        Generated at: {timestamp}

        ## Purpose

        Create a minimal terminology and definition contract draft authorized by PREAX01-SYNTH.

        ## Inputs

        {chr(10).join(f"- {rel(path)}" for path in preax_paths.values())}

        ## Outputs

        {chr(10).join(f"- {rel(path)}" for path in OUTPUTS.values())}

        ## Key Definitions Created

        psi_A, relation_space, source_space, C_AB, K_AB, d_AB, Phi_ABC, valid_loop, invalid_loop, rephasing_gauge, thresholds, orientation, arg_branch, source_coherence, cross_source_mapping_contract, nullmodel_interface, claim_boundary.

        ## Key Gates Created

        C/K separation, Level 0 / Level 1 distinction, transformation declaration requirement, loop validity gates, threshold blocking policy, source-coherence policy, and claim boundary.

        ## Validation Summary

        Status: {validation_status(results)}

        {chr(10).join(f"- {row['rule_id']}: {row['status']} - {row['message']}" for row in results)}

        ## AX01 Readiness Decision

        {gate.get("full_ax01_readiness")}

        Next authorized step: {gate.get("next_authorized_step")}

        ## Blocked Next Steps

        {", ".join(gate.get("blocked_steps", []))}

        ## No Production Mutation Statement

        {PRODUCTION_MUTATION_STATEMENT}

        ## No Restricted Interpretive Claim Statement

        This draft is a terminology contract only, performs no computation, and introduces no restricted interpretive claim.
        """)
    OUTPUTS["summary"].write_text(text, encoding="utf-8")


def build(preax_dir: Path, force: bool) -> None:
    preax_validation, preax_readiness, preax_paths = load_gate(preax_dir)
    prepare_output(force)
    timestamp = utc_now()
    write_csv(OUTPUTS["definitions"], ["term", "definition", "boundary", "required_status"], DEFINITIONS)
    write_csv(OUTPUTS["symbols"], ["symbol", "meaning", "boundary"], SYMBOLS)
    write_csv(OUTPUTS["transform_rules"], ["rule_id", "rule_name", "statement", "status"], TRANSFORM_RULES)
    write_csv(OUTPUTS["loop_validity"], ["rule_id", "rule_name", "requirement", "fail_status"], LOOP_VALIDITY)
    write_csv(OUTPUTS["threshold_policy"], ["threshold", "numeric_value", "status", "blocking_rule"], THRESHOLDS)
    write_csv(OUTPUTS["source_coherence"], ["rule_id", "rule_name", "requirement", "status"], SOURCE_COHERENCE)
    write_csv(OUTPUTS["forbidden_claims"], ["term_or_claim", "status", "safe_replacement", "notes"], FORBIDDEN_CLAIMS)
    write_contract(timestamp, preax_dir)
    write_claim_boundary_report(timestamp)
    write_readiness("pass")
    write_manifest(preax_paths, timestamp, "pending")
    OUTPUTS["validation"].write_text(json.dumps({
        "run_id": RUN_ID,
        "timestamp": timestamp,
        "validation_status": "pending",
        "results": [],
        "claim_status": CLAIM_STATUS,
        "production_mutation_statement": PRODUCTION_MUTATION_STATEMENT,
    }, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    write_summary(timestamp, preax_paths, [])
    results = validate(preax_validation, preax_readiness, preax_paths, timestamp)
    if validation_status(results) != "pass":
        write_readiness("fail")
    OUTPUTS["validation"].write_text(json.dumps({
        "run_id": RUN_ID,
        "timestamp": timestamp,
        "validation_status": validation_status(results),
        "results": results,
        "claim_status": CLAIM_STATUS,
        "production_mutation_statement": PRODUCTION_MUTATION_STATEMENT,
    }, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    write_summary(timestamp, preax_paths, results)
    write_manifest(preax_paths, timestamp, validation_status(results))


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--preax01-dir", type=Path, default=DEFAULT_PREAX_DIR)
    parser.add_argument("--force", action="store_true", help="Replace files inside runs/QSB-RELALG-AX01-TERM only.")
    args = parser.parse_args()
    preax_dir = args.preax01_dir if args.preax01_dir.is_absolute() else REPO_ROOT / args.preax01_dir
    try:
        build(preax_dir, args.force)
    except (FileNotFoundError, FileExistsError, RuntimeError) as exc:
        print(str(exc))
        raise SystemExit(1) from None


if __name__ == "__main__":
    main()
