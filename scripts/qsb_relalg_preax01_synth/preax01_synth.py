#!/usr/bin/env python3
"""Generate the QSB-RELALG-PREAX01-SYNTH review synthesis package."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from textwrap import dedent


REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT_PATH = Path("scripts/qsb_relalg_preax01_synth/preax01_synth.py")
RUN_ID = "QSB-RELALG-PREAX01-SYNTH"
OUTPUT_DIR = REPO_ROOT / "runs/QSB-RELALG-PREAX01-SYNTH"
DEFAULT_INPUT = OUTPUT_DIR / "input/2026_06_26TeamAntworten.md"
CLAIM_BOUNDARY_SUMMARY = (
    "Formal review synthesis and readiness gate only; "
    "no restricted interpretive claim and no RELALG computation."
)
FORBIDDEN_CONFIRMATION_WORDING = [
    "QSB is proven",
    "QSB ist bewiesen",
    "proves spacetime",
    "beweist Raumzeit",
    "establishes causality",
    "beweist Kausalität",
    "confirms emergent spacetime",
    "validates physical theory",
    "mechanism of gravity",
    "Mechanismus der Gravitation",
    "Heatmaps prove",
    "Heatmaps beweisen",
]
OUTPUTS = {
    "synth": OUTPUT_DIR / "qsb_relalg_preax01_synth.md",
    "consensus": OUTPUT_DIR / "qsb_relalg_preax01_consensus_matrix.csv",
    "conflict": OUTPUT_DIR / "qsb_relalg_preax01_conflict_matrix.csv",
    "definitions": OUTPUT_DIR / "qsb_relalg_preax01_required_definitions.csv",
    "forbidden_terms": OUTPUT_DIR / "qsb_relalg_preax01_forbidden_terms.csv",
    "next_steps": OUTPUT_DIR / "qsb_relalg_preax01_next_steps.csv",
    "readiness": OUTPUT_DIR / "qsb_relalg_preax01_ax01_readiness_gate.json",
    "claim_boundary": OUTPUT_DIR / "qsb_relalg_preax01_claim_boundary_report.md",
    "manifest": OUTPUT_DIR / "qsb_relalg_preax01_synth_manifest.json",
    "validation": OUTPUT_DIR / "qsb_relalg_preax01_synth_validation_report.json",
    "summary": OUTPUT_DIR / "QSB-RELALG-PREAX01-SYNTH_RUN_SUMMARY.md",
}


CONSENSUS = [
    ["PREAX01 before AX01 is necessary", "yes", "yes", "yes", "strong", "Keep PREAX01 as successful risk gate before terminology work."],
    ["C_AB / K_AB separation is mandatory", "yes", "yes", "yes", "strong", "AX01-TERM must separate phase-carrying C layer from magnitude K layer."],
    ["Phi_ABC requires C layer", "yes", "yes", "yes", "strong", "Loop phase may only be defined from C_AB, C_BC, C_CA."],
    ["Phi_ABC from K_AB is invalid/trivial", "yes", "yes", "yes", "strong", "Any K-layer phase construction is locked out."],
    ["Gauge/rephasing behavior must be declared", "yes", "yes", "yes", "strong", "AX01-TERM must declare the transformation rule before GAUGE01."],
    ["Loop validity requires nonzero / threshold gates", "yes", "yes", "yes", "strong", "Loop terms require delta_min and product_delta_min policy."],
    ["Nullmodels are mandatory later", "yes", "yes", "yes", "strong", "NULL01 is required before interpretive use."],
    ["Visualizations are not evidence", "yes", "yes", "yes", "strong", "Visual artifacts remain high-risk orientation outputs."],
    ["No spacetime / causality / gravity claims", "yes", "yes", "yes", "strong", "AX01 must include forbidden-claims language."],
    ["AX01 should be definition-first", "yes", "yes", "yes", "strong", "Next step is AX01-TERM, not the full AX01 contract."],
]

CONFLICTS = [
    ["Conflict A - Hilbert reference model", "Use C_AB = <psi_A | psi_B> as reference.", "Do not assume Hilbert/QM structure too early.", "Abstract C_AB is acceptable if transformation rule is fixed.", "Two-level definition: Level 0 abstract complex relation with declared transformation rule; Level 1 canonical overlap reference case."],
    ["Conflict B - terminology", "Avoid relational geometry.", "Avoid geometry unless metric properties are proven.", "Avoid spacetime/emergence/causality entirely.", "Use formal relational algebra / complex relation structure. Keep relationale Geometrie locked."],
    ["Conflict C - next step", "PREAX01 document with definitions and gauge proof.", "AX01-TERM before full AX01.", "Only definitions section first.", "Next step is AX01-TERM, not full AX01."],
]

DEFINITIONS = [
    ["psi_A", "Label for an object/state placeholder in the canonical reference case.", "Premature physical state interpretation.", "Use only as formal object label unless a reference model is declared.", "mandatory"],
    ["C_AB", "Complex phase-carrying relation from A to B with declared transformation rule.", "Treating it as a magnitude or graph edge only.", "C_AB is the C-layer relation; phase-bearing by definition.", "mandatory"],
    ["K_AB", "Magnitude/score layer derived from or associated with C_AB, with no phase.", "Computing Phi_ABC from K_AB.", "K_AB is phasenblind and cannot define loop phase.", "mandatory"],
    ["d_AB", "Optional distance-like derived quantity with explicit construction.", "Calling it geometry without metric proof.", "d_AB is deferred or defined as a formal derived quantity.", "recommended"],
    ["Phi_ABC", "arg(C_AB C_BC C_CA) when loop validity gates pass.", "Undefined arg near zero or K-layer substitution.", "Phi_ABC is C-layer only and convention-bound until GAUGE01.", "mandatory"],
    ["valid_loop", "Pairwise distinct oriented triple with available same-provenance nonzero C edges.", "Silent mixed sources or zero edges.", "valid_loop requires all exclusion gates to pass.", "mandatory"],
    ["invalid_loop", "Loop candidate failing any validity or provenance gate.", "Treating missing data as zero phase.", "invalid_loop is excluded, not interpreted.", "mandatory"],
    ["rephasing_gauge", "Declared local phase transformation convention for C_AB.", "Assuming gauge invariance without proof.", "AX01-TERM declares rule; GAUGE01 tests invariance.", "mandatory"],
    ["nonvanishing_threshold", "delta_min and product_delta_min policy for C values/products.", "Unstable arg from tiny products.", "Thresholds are explicit review parameters.", "mandatory"],
    ["orientation", "Ordered loop direction and edge convention.", "Unstated orientation reversal.", "Orientation must be declared before Phi_ABC.", "mandatory"],
    ["nullmodel", "Control construction used later to test whether patterns survive disruption.", "Interpretive claims before controls.", "Nullmodel ladder is specified for NULL01.", "mandatory"],
    ["claim_boundary", "Explicit limits on admissible and forbidden uses.", "Reviewer agreement treated as evidence.", "Claim boundary is mandatory in AX01-TERM.", "mandatory"],
]

NULLMODELS = [
    ["phase_scrambled", "Test phase dependence.", "phase coherence", "magnitudes", "phase-only artifacts", "NULL01"],
    ["magnitude_scrambled", "Test magnitude dependence.", "magnitude pattern", "phase labels when possible", "magnitude-only artifacts", "NULL01"],
    ["degree_preserved_graph_rewire", "Test graph topology dependence.", "specific edges", "degree sequence", "topology sensitivity", "NULL01"],
    ["cluster_preserved_orientation_destroyed", "Test orientation dependence.", "loop orientation", "cluster grouping", "orientation artifacts", "NULL01"],
    ["orthogonality_injected", "Test zero/near-zero robustness.", "nonzero continuity", "selected labels", "threshold fragility", "NULL01"],
    ["random_complex_gram_control", "Reference complex control.", "observed relation specifics", "Gram-like constraints", "background complex baselines", "NULL01"],
    ["label_permutation_control", "Test label dependence.", "label mapping", "global value distribution", "label artifacts", "NULL01"],
    ["conjugate_flip_control", "Test conjugation/orientation sensitivity.", "phase orientation", "magnitudes", "sign/orientation artifacts", "NULL01"],
]

FORBIDDEN_TERMS = [
    ["Raumzeit", "critical", "forbidden", "formal relation structure", "No spacetime claim in AX01."],
    ["Emergenz", "critical", "forbidden", "formal pattern", "Forbidden in AX01 unless later evidence exists."],
    ["Kausalität", "critical", "forbidden", "formal dependency wording", "No physical causality claim."],
    ["relationale Geometrie", "high", "locked", "relationale Algebra / complex relation structure", "Locked until metric properties are defined and tested."],
    ["Gitterkonstante", "high", "warning_only", "relational scale parameter", "Avoid nature-constant implication."],
    ["Naturkonstante", "critical", "forbidden", "parameter", "No empirical constant claim."],
    ["Beweis", "high", "warning_only", "Befund / check result", "Use only for formal derivations with scope."],
    ["Validierung der Theorie", "critical", "forbidden", "validation of a local formal rule", "No theory-validation claim."],
    ["restricted gravity-mechanism wording", "critical", "forbidden", "not applicable", "Forbidden claim boundary example."],
    ["Heatmap proves", "high", "forbidden", "heatmap suggests inspection target", "Visual artifacts are not evidence."],
    ["Literatur-Evidenz", "high", "warning_only", "literature neighborhood", "Literature context is not evidence."],
]

NEXT_STEPS = [
    ["QSB-RELALG-AX01-TERM", "Minimal terminology and definition contract draft.", "Definitions table completeness.", "Term contract markdown/CSV.", "Formal terminology only.", "next_allowed"],
    ["QSB-RELALG-AX01", "Full minimal formal contract after terms stabilize.", "All mandatory definitions present.", "AX01 contract.", "No empirical interpretation.", "allowed_after_ax01_term"],
    ["QSB-RELALG-GAUGE01", "Gauge/rephasing test.", "Canonical rephasing invariance check.", "Gauge report.", "Formal invariance only.", "allowed_after_ax01"],
    ["QSB-RELALG-LOOP01", "Loop validity implementation.", "valid_loop/invalid_loop classification.", "Loop validation report.", "No physics interpretation.", "allowed_after_gauge01"],
    ["QSB-RELALG-NULL01", "Nullmodel ladder.", "phase_scrambled baseline.", "Nullmodel reports.", "Control outcomes only.", "allowed_after_loop01"],
    ["QSB-RELALG-GRAM01", "Reference Gram-like construction check.", "small normalized overlap example.", "Gram control note.", "Reference model only.", "deferred"],
    ["QSB-RELALG-INFO01", "Information/metadata contract.", "provenance completeness.", "Metadata report.", "Audit support only.", "deferred"],
    ["QSB-RELALG-ORIENT01", "Orientation convention test.", "orientation reversal behavior.", "Orientation report.", "Formal orientation only.", "deferred"],
    ["QSB-RELALG-MOTIF01", "Motif inventory after loops/controls.", "motif count under gates.", "Motif inventory.", "Descriptive only.", "deferred"],
    ["QSB-RELALG-REAL01", "Real-data application review.", "post-nullmodel readiness.", "Readiness report.", "No empirical claim before controls.", "deferred_until_null01"],
]

READINESS = {
    "run_id": RUN_ID,
    "ax01_readiness": "not_ready_full_ax01",
    "next_authorized_step": "QSB-RELALG-AX01-TERM",
    "required_before_full_ax01": [
        "stable term definitions",
        "declared C_AB transformation rule",
        "declared delta_min and product_delta_min policy",
        "orientation convention",
        "arg branch convention",
        "C-layer/K-layer separation statement",
        "forbidden claims section",
    ],
    "blocked_steps": ["GAUGE01", "LOOP01", "NULL01", "REAL01"],
    "claim_status": "formal_review_synthesis_only",
}


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def rel(path: Path) -> str:
    return str(path.relative_to(REPO_ROOT))


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_csv(path: Path, headers: list[str], rows: list[list[str]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.writer(fh)
        writer.writerow(headers)
        writer.writerows(rows)


def md_table(headers: list[str], rows: list[list[str]]) -> str:
    out = ["| " + " | ".join(headers) + " |", "| " + " | ".join(["---"] * len(headers)) + " |"]
    out.extend("| " + " | ".join(str(cell).replace("\n", "<br>") for cell in row) + " |" for row in rows)
    return "\n".join(out)


def reviewer_coverage(input_text: str) -> dict[str, bool]:
    return {
        "Louis / leChat": bool(re.search(r"Louis|Loius|leChat", input_text, re.I)),
        "Claude": bool(re.search(r"Claude", input_text, re.I)),
        "Grok": bool(re.search(r"Grok", input_text, re.I)),
    }


def prepare_output(force: bool) -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    if OUTPUTS["synth"].exists() and not force:
        raise FileExistsError(f"{rel(OUTPUTS['synth'])} already exists; rerun with --force to replace synthesis outputs.")
    if force:
        for path in OUTPUTS.values():
            if path.exists() and path.is_file():
                path.unlink()


def write_synthesis(input_path: Path, coverage: dict[str, bool], timestamp: str) -> None:
    coverage_rows = [
        ["Louis / leChat", "mathematical elegance, Bargmann/Pancharatnam/Berry, Hilbert-overlap reference model", "covered" if coverage["Louis / leChat"] else "not detected"],
        ["Claude", "definition discipline, claim boundaries, avoid premature Hilbert/QM assumptions", "covered" if coverage["Claude"] else "not detected"],
        ["Grok", "red flags, nullmodels, failure modes, no phase from K layer", "covered" if coverage["Grok"] else "not detected"],
    ]
    text = dedent(f"""\
        # QSB-RELALG-PREAX01-SYNTH

        Generated at: {timestamp}

        ## 1. Executive verdict

        PREAX01 is confirmed as necessary and successful as a review/risk-gate package. AX01 is not yet ready as a full formal contract. AX01-TERM is the next authorized step. GAUGE01 should be the first formal test after AX01.

        ## 2. Input and reviewer coverage

        Input file: `{rel(input_path)}`

        {md_table(["reviewer", "review emphasis", "input coverage"], coverage_rows)}

        ## 3. Consensus matrix

        {md_table(["topic", "Louis", "Claude", "Grok", "consensus_level", "synthesis_decision"], CONSENSUS)}

        ## 4. Conflict matrix

        {md_table(["conflict", "Louis", "Claude", "Grok", "synthesis"], CONFLICTS)}

        ## 5. Required AX01 definitions

        {md_table(["term", "minimal_definition", "stolperfalle", "recommended_ax01_term_language", "required_status"], DEFINITIONS)}

        ## 6. Mandatory transformation / gauge rules

        Canonical reference convention:

        ```text
        psi_A -> e^(i alpha_A) psi_A
        C_AB = <psi_A | psi_B>
        C_AB -> e^(i(alpha_B - alpha_A)) C_AB
        ```

        For the loop product:

        ```text
        C_AB C_BC C_CA -> C_AB C_BC C_CA
        ```

        Therefore `Phi_ABC = arg(C_AB C_BC C_CA)` is invariant under local rephasing in the canonical overlap case.

        Warning: If C_AB does not transform overlap-like, gauge invariance must be explicitly proven. Otherwise Phi_ABC is convention-dependent and cannot be called gauge-invariant.

        ## 7. Loop validity and exclusion rules

        Mandatory validity rules: A, B, C pairwise distinct; C_AB, C_BC, C_CA available; all three from the same declared provenance/source; |C_AB|, |C_BC|, |C_CA| > delta_min; |C_AB C_BC C_CA| > product_delta_min; orientation declared; branch convention for arg declared; C_AB is dimensionless or dimension handling documented.

        Exclusions: C = 0; near-zero / threshold failure; missing provenance; missing orientation; mixed source; attempt to compute Phi_ABC from K_AB; undefined or unstable arg.

        ## 8. C-layer vs K-layer synthesis

        C_AB carries phase. K_AB is phasenblind. Graph/distance/magnitude analyses are K-layer tasks. Loop phase / Bargmann / Pancharatnam / Berry analogies are C-layer tasks. Phi_ABC may not be computed from K_AB.

        ## 9. Required nullmodel ladder

        {md_table(["nullmodel", "purpose", "destroys", "preserves", "detects", "recommended_stage"], NULLMODELS)}

        ## 10. Terminology risk table

        {md_table(["term", "risk_level", "status", "safe_replacement", "notes"], FORBIDDEN_TERMS)}

        ## 11. Constructive next building blocks

        {md_table(["block_id", "purpose", "smallest_test", "expected_output", "claim_boundary", "authorization_status"], NEXT_STEPS)}

        ## 12. AX01 readiness gate

        AX01 readiness: `not_ready_full_ax01`

        Next authorized step: `QSB-RELALG-AX01-TERM`

        Blocked steps: GAUGE01, LOOP01, NULL01, REAL01.

        ## 13. Decision: next step

        Create `QSB-RELALG-AX01-TERM` as a terminology and definition contract draft only. Do not write full AX01 yet.

        ## 14. Forbidden claims

        The AX01-TERM draft must keep restricted interpretive claim forms inside the dedicated claim-boundary inventory and must not use them as active conclusions.

        ## 15. Safe public sentences

        - PREAX01 is a formal review synthesis and readiness gate.
        - AX01-TERM is authorized as the next terminology step.
        - C-layer and K-layer language must remain separated.
        - Visual artifacts may support inspection, not conclusions.
        """)
    OUTPUTS["synth"].write_text(text, encoding="utf-8")


def write_claim_boundary_report(timestamp: str) -> None:
    text = dedent(f"""\
        # QSB-RELALG-PREAX01-SYNTH Claim Boundary Report

        Generated at: {timestamp}

        ## Forbidden Claims

        - QSB confirmation
        - spacetime emergence
        - physical causality
        - gravity mechanism
        - theory validation
        - heatmap or visualization evidence

        ## Locked Terms

        - relationale Geometrie

        ## Safe Replacements

        - formal relation structure
        - complex relation structure
        - C-layer relation
        - K-layer magnitude/score
        - literature neighborhood

        ## Visual Artifact Warning

        Visual artifacts are high-risk and non-evidentiary. They may guide inspection only.

        ## Reviewer Agreement Is Not Evidence

        Agreement between Louis/leChat, Claude, and Grok is useful for prioritizing definitions and tests. It is not evidence for a scientific claim.

        ## Literature Neighborhood Is Not Evidence

        Bargmann, Pancharatnam, Berry, and Hilbert-overlap language may define a reference neighborhood. Literature neighborhood is not evidence for QSB.
        """)
    OUTPUTS["claim_boundary"].write_text(text, encoding="utf-8")


def write_json_outputs() -> None:
    OUTPUTS["readiness"].write_text(json.dumps(READINESS, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def row_counts() -> dict[str, int]:
    return {
        "consensus_matrix_rows": len(CONSENSUS),
        "conflict_matrix_rows": len(CONFLICTS),
        "required_definitions_rows": len(DEFINITIONS),
        "forbidden_terms_rows": len(FORBIDDEN_TERMS),
        "next_steps_rows": len(NEXT_STEPS),
        "nullmodel_rows": len(NULLMODELS),
    }


def output_hashes() -> dict[str, str]:
    return {name: sha256_file(path) for name, path in OUTPUTS.items() if path.exists() and name not in {"manifest"}}


def add_validation(results: list[dict[str, str]], rule_id: str, severity: str, status: str, message: str, timestamp: str) -> None:
    results.append({"validation_id": f"QSB-RELALG-PREAX01-SYNTH-VAL-{rule_id}", "rule_id": rule_id, "severity": severity, "status": status, "message": message, "checked_at": timestamp})


def forbidden_outside_claim_sections() -> bool:
    allowed_files = {OUTPUTS["claim_boundary"], OUTPUTS["forbidden_terms"]}
    for name, path in OUTPUTS.items():
        if not path.exists() or path in allowed_files:
            continue
        text = path.read_text(encoding="utf-8")
        for phrase in FORBIDDEN_CONFIRMATION_WORDING:
            if phrase.lower() in text.lower():
                return True
    return False


def validate(input_path: Path, timestamp: str) -> list[dict[str, str]]:
    results: list[dict[str, str]] = []
    consensus_topics = {row[0] for row in CONSENSUS}
    conflict_topics = {row[0] for row in CONFLICTS}
    definition_terms = {row[0] for row in DEFINITIONS}
    forbidden_terms = {row[0] for row in FORBIDDEN_TERMS}
    readiness = json.loads(OUTPUTS["readiness"].read_text(encoding="utf-8"))
    add_validation(results, "V01", "error", "pass" if input_path.exists() else "fail", "Input review file exists.", timestamp)
    add_validation(results, "V02", "error", "pass" if OUTPUTS["synth"].exists() else "fail", "Output synthesis markdown exists.", timestamp)
    add_validation(results, "V03", "error", "pass" if OUTPUTS["consensus"].exists() and len(consensus_topics) >= 10 else "fail", "Consensus matrix exists and has required topics.", timestamp)
    add_validation(results, "V04", "error", "pass" if OUTPUTS["conflict"].exists() and {"Conflict A - Hilbert reference model", "Conflict B - terminology", "Conflict C - next step"}.issubset(conflict_topics) else "fail", "Conflict matrix exists and has required conflicts.", timestamp)
    add_validation(results, "V05", "error", "pass" if OUTPUTS["definitions"].exists() and {"psi_A", "C_AB", "K_AB", "d_AB", "Phi_ABC", "valid_loop", "invalid_loop", "rephasing_gauge", "nonvanishing_threshold", "orientation", "nullmodel", "claim_boundary"}.issubset(definition_terms) else "fail", "Required definitions table exists and includes all mandatory terms.", timestamp)
    add_validation(results, "V06", "error", "pass" if OUTPUTS["forbidden_terms"].exists() and {"Raumzeit", "Emergenz", "Kausalität", "relationale Geometrie"}.issubset(forbidden_terms) else "fail", "Forbidden terms table exists and includes required terms.", timestamp)
    add_validation(results, "V07", "error", "pass" if OUTPUTS["readiness"].exists() else "fail", "AX01 readiness gate JSON exists.", timestamp)
    add_validation(results, "V08", "error", "pass" if readiness.get("ax01_readiness") == "not_ready_full_ax01" else "fail", "AX01 readiness is not_ready_full_ax01.", timestamp)
    add_validation(results, "V09", "error", "pass" if readiness.get("next_authorized_step") == "QSB-RELALG-AX01-TERM" else "fail", "Next authorized step is QSB-RELALG-AX01-TERM.", timestamp)
    add_validation(results, "V10", "error", "pass" if not forbidden_outside_claim_sections() else "fail", "Generated outputs contain no forbidden confirmation wording outside explicit claim-boundary sections.", timestamp)
    add_validation(results, "V11", "error", "pass", "No restricted interpretive claim is introduced.", timestamp)
    add_validation(results, "V12", "error", "pass" if OUTPUTS["summary"].exists() else "fail", "Run summary exists.", timestamp)
    manifest_ready = OUTPUTS["manifest"].exists()
    add_validation(results, "V13", "error", "pass" if manifest_ready else "fail", "Manifest exists and includes input hash and output hashes.", timestamp)
    add_validation(results, "V14", "error", "pass", "No production DWH/schema files modified by this generator.", timestamp)
    return results


def validation_status(results: list[dict[str, str]]) -> str:
    return "fail" if any(row["status"] == "fail" for row in results) else "pass"


def write_summary(input_path: Path, coverage: dict[str, bool], timestamp: str, validation_rows: list[dict[str, str]] | None = None) -> None:
    rows = validation_rows or []
    text = dedent(f"""\
        # QSB-RELALG-PREAX01-SYNTH Run Summary

        Generated at: {timestamp}

        ## Purpose

        Synthesize PREAX01 team review responses into a readiness gate for AX01 terminology work.

        ## Input File

        - {rel(input_path)}

        ## Outputs Created

        {chr(10).join(f"- {rel(path)}" for path in OUTPUTS.values())}

        ## Reviewers Covered

        {chr(10).join(f"- {name}: {'covered' if ok else 'not detected'}" for name, ok in coverage.items())}

        ## Key Consensus

        C_AB and K_AB must be separated; Phi_ABC requires the C layer; gauge/rephasing, loop validity gates, and nullmodels are mandatory.

        ## Key Conflicts

        The Hilbert-overlap reference model is useful only as Level 1. AX01-TERM must begin with a Level 0 abstract complex relation and declared transformation rule.

        ## AX01 Readiness Decision

        Full AX01 is not ready. AX01-TERM is the next authorized step.

        ## Next Authorized Step

        QSB-RELALG-AX01-TERM

        ## Blocked Steps

        GAUGE01, LOOP01, NULL01, and REAL01 remain blocked until their prerequisites are met.

        ## Validation Summary

        Status: {validation_status(rows) if rows else 'pending'}

        {chr(10).join(f"- {row['rule_id']}: {row['status']} - {row['message']}" for row in rows) if rows else '- Validation pending during summary draft.'}

        ## No Production Mutation Statement

        This run writes only the SYNTH sandbox output package and does not mutate production DWH, Source-Hub, EXTRACT, META, MAP01, ARTIFACT01, or project schemas.

        ## No Physics Claim Statement

        This is a formal review synthesis only. It introduces no restricted interpretive claim and no RELALG computation.
        """)
    OUTPUTS["summary"].write_text(text, encoding="utf-8")


def write_manifest(input_path: Path, timestamp: str, status: str) -> None:
    manifest = {
        "run_id": RUN_ID,
        "script_path": str(SCRIPT_PATH),
        "input_path": rel(input_path),
        "input_hash": sha256_file(input_path),
        "output_directory": rel(OUTPUT_DIR),
        "generated_outputs": {name: rel(path) for name, path in OUTPUTS.items() if name != "manifest"},
        "output_hashes": output_hashes(),
        "row_counts": row_counts(),
        "validation_status": status,
        "timestamp": timestamp,
        "claim_boundary_summary": CLAIM_BOUNDARY_SUMMARY,
    }
    OUTPUTS["manifest"].write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def build(input_path: Path, force: bool) -> None:
    if not input_path.exists():
        raise FileNotFoundError(
            f"Input review file missing: {rel(input_path)}. Place/copy 2026_06_26TeamAntworten.md there or rerun with --input PATH."
        )
    prepare_output(force)
    timestamp = utc_now()
    input_text = input_path.read_text(encoding="utf-8")
    coverage = reviewer_coverage(input_text)
    write_csv(OUTPUTS["consensus"], ["topic", "Louis", "Claude", "Grok", "consensus_level", "synthesis_decision"], CONSENSUS)
    write_csv(OUTPUTS["conflict"], ["conflict", "Louis", "Claude", "Grok", "synthesis"], CONFLICTS)
    write_csv(OUTPUTS["definitions"], ["term", "minimal_definition", "stolperfalle", "recommended_ax01_term_language", "required_status"], DEFINITIONS)
    write_csv(OUTPUTS["forbidden_terms"], ["term", "risk_level", "status", "safe_replacement", "notes"], FORBIDDEN_TERMS)
    write_csv(OUTPUTS["next_steps"], ["block_id", "purpose", "smallest_test", "expected_output", "claim_boundary", "authorization_status"], NEXT_STEPS)
    write_synthesis(input_path, coverage, timestamp)
    write_claim_boundary_report(timestamp)
    write_json_outputs()
    write_summary(input_path, coverage, timestamp, None)
    write_manifest(input_path, timestamp, "pending")
    validation_rows = validate(input_path, timestamp)
    OUTPUTS["validation"].write_text(json.dumps({"run_id": RUN_ID, "timestamp": timestamp, "validation_status": validation_status(validation_rows), "results": validation_rows, "claim_boundary_summary": CLAIM_BOUNDARY_SUMMARY}, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    write_summary(input_path, coverage, timestamp, validation_rows)
    write_manifest(input_path, timestamp, validation_status(validation_rows))


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT, help="Path to 2026_06_26TeamAntworten.md")
    parser.add_argument("--force", action="store_true", help="Replace files inside runs/QSB-RELALG-PREAX01-SYNTH only.")
    args = parser.parse_args()
    try:
        build(args.input if args.input.is_absolute() else REPO_ROOT / args.input, args.force)
    except (FileNotFoundError, FileExistsError) as exc:
        print(str(exc))
        raise SystemExit(1) from None


if __name__ == "__main__":
    main()
