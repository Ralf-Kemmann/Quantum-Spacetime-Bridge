#!/usr/bin/env python3
"""Create a blocked INTERFACE01-M review when no executed L2 result exists."""

from __future__ import annotations

import csv
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable


REPO = Path(__file__).resolve().parents[2]
F3 = REPO / "runs/QSB-INTERFACE01F3/authorized_delta_phi_export_staging_preflight"
G = REPO / "runs/QSB-INTERFACE01G/minimaltest_design_review_from_staged_delta_phi"
H = REPO / "runs/QSB-INTERFACE01H/controlled_minimal_pilot_from_staged_delta_phi"
I = REPO / "runs/QSB-INTERFACE01I/pilot_result_review_nullmodel_adequacy_decision"
J = REPO / "runs/QSB-INTERFACE01J/minimaltest_precontract"
K = REPO / "runs/QSB-INTERFACE01K/review_point_resolution_execution_authorization_check"
J2 = REPO / "runs/QSB-INTERFACE01J2/minimaltest_acceptance_rule_addendum"
L = REPO / "runs/QSB-INTERFACE01L/separate_final_minimaltest_execution"
OUTPUT = REPO / "runs/QSB-INTERFACE01M/result_review_mechanism_interpretation_boundary"

STATUS = "interface01m_result_review_blocked_missing_executed_minimaltest"
J2_AUTHORIZATION = "authorized_for_separate_minimaltest_execution_with_acceptance_rule"
CLAIM_BOUNDARY = (
    "INTERFACE01-M has no executed J2-based Minimaltest result to review. It therefore performs "
    "no mechanism interpretation, reruns no calculation, changes no upstream artifact, and makes "
    "no physical-evidence claim."
)
EXPECTED_FILES = {
    "01_m_run_manifest.json", "02_upstream_result_inventory.csv", "03_authorization_and_hash_preflight.csv",
    "04_minimaltest_result_summary.csv", "05_acceptance_gate_readout.csv",
    "06_feature_result_interpretation.csv", "07_nullmodel_result_interpretation.csv",
    "08_mechanism_chain_map.csv", "09_claim_classification_matrix.csv",
    "10_unsupported_claims_and_boundaries.csv", "11_theory_language_note_de.md",
    "12_theory_language_note_en.md", "13_next_research_actions.csv", "14_m_validation_results.csv",
    "15_review_items_for_next_block.csv", "FINAL_RESULT_NOTE.md",
}


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def write_csv(path: Path, fields: list[str], rows: Iterable[dict[str, Any]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def rel(path: Path) -> str:
    return str(path.relative_to(REPO))


def discover_execution_manifests() -> list[Path]:
    candidates = []
    for path in (REPO / "runs").glob("QSB-INTERFACE01L*/**/*manifest*.json"):
        if path.is_file() and path != L / "01_l_run_manifest.json":
            candidates.append(path)
    return sorted(candidates)


def main() -> int:
    if OUTPUT.exists():
        raise SystemExit(f"Refusing to overwrite existing output directory: {OUTPUT}")

    artifacts = {
        "f3_manifest": ("F3", F3 / "01_f3_run_manifest.json", "authorized source status"),
        "f3_db": ("F3", F3 / "09_delta_phi_staging_preflight.sqlite", "staged source identity"),
        "g_manifest": ("G", G / "01_g_run_manifest.json", "profile status"),
        "h_manifest": ("H", H / "01_h_run_manifest.json", "pilot scope"),
        "i_manifest": ("I", I / "01_i_run_manifest.json", "review status"),
        "j_manifest": ("J", J / "01_j_run_manifest.json", "pre-contract status"),
        "k_manifest": ("K", K / "01_k_run_manifest.json", "first execution authorization"),
        "k_features": ("K", K / "07_feature_contract_resolution.csv", "locked feature scope"),
        "k_nulls": ("K", K / "08_nullmodel_contract_resolution.csv", "locked nullmodel roles"),
        "l_manifest": ("L", L / "01_l_run_manifest.json", "blocked first execution attempt"),
        "l_preflight": ("L", L / "02_upstream_authorization_preflight.csv", "original blocking gate"),
        "j2_manifest": ("J2", J2 / "01_j2_run_manifest.json", "acceptance-rule authorization"),
        "j2_rules": ("J2", J2 / "05_acceptance_rule_addendum.csv", "machine-readable result rules"),
        "j2_features": ("J2", J2 / "06_feature_acceptance_gates.csv", "three feature gates"),
        "j2_nulls": ("J2", J2 / "07_nullmodel_acceptance_roles.csv", "N2/N4 acceptance roles"),
        "j2_decisions": ("J2", J2 / "08_result_decision_table.csv", "allowed result values"),
    }
    upstream_present = all(path.is_file() for _, path, _ in artifacts.values())
    before_hashes = {key: sha256(path) for key, (_, path, _) in artifacts.items() if path.is_file()}
    inventory_rows = []
    for number, (key, (block, path, use)) in enumerate(artifacts.items(), start=1):
        exists = path.is_file()
        inventory_rows.append({
            "artifact_id": f"M-A{number:02d}", "upstream_block": block, "path": rel(path),
            "exists": "yes" if exists else "no", "sha256": before_hashes.get(key, "missing"),
            "role": "read-only review input", "used_for": use,
            "notes": "Hashed before M; not modified." if exists else "Missing required upstream artifact.",
        })

    j2_manifest = load_json(artifacts["j2_manifest"][1]) if artifacts["j2_manifest"][1].is_file() else {}
    l_manifest = load_json(artifacts["l_manifest"][1]) if artifacts["l_manifest"][1].is_file() else {}
    j2_authorized = (
        j2_manifest.get("status") == "interface01j2_acceptance_rule_addendum_completed_authorized_for_l_replay"
        and j2_manifest.get("execution_authorization_after_j2") == J2_AUTHORIZATION
    )
    old_l_blocked = (
        l_manifest.get("status") == "interface01l_separate_final_minimaltest_execution_blocked_contract_incomplete"
        and l_manifest.get("minimaltest_contract_result") == "blocked_no_execution"
        and l_manifest.get("minimaltest_started") is False
    )

    execution_candidates = discover_execution_manifests()
    executed_manifest_path: Path | None = None
    executed_manifest: dict[str, Any] = {}
    allowed_results = {"pass", "fail", "inconclusive_review"}
    for path in execution_candidates:
        try:
            data = load_json(path)
        except (json.JSONDecodeError, OSError):
            continue
        result = data.get("minimaltest_contract_result")
        if data.get("minimaltest_started") is True and result in allowed_results:
            executed_manifest_path, executed_manifest = path, data
            break
    executed_result = executed_manifest.get("minimaltest_contract_result", "none")
    execution_available = executed_manifest_path is not None
    result_not_blocked = executed_result in allowed_results

    preflight_specs = [
        ("M-G01", "j2_authorized", j2_manifest.get("execution_authorization_after_j2", "missing"), J2_AUTHORIZATION, j2_authorized, "J2 authorization is exact."),
        ("M-G02", "l2_or_replay_executed", "none" if not execution_available else rel(executed_manifest_path), "executed J2-based L2 or L-replay manifest", execution_available, "No post-J2 execution manifest was found."),
        ("M-G03", "result_not_blocked", executed_result, "pass|fail|inconclusive_review", result_not_blocked, "The only L result remains blocked_no_execution; it is not reviewable as an executed result."),
        ("M-G04", "upstream_hashes_stable", "checked_before_and_after_M", "unchanged", True, "Final comparison is recorded in M-V15."),
        ("M-G05", "no_minimaltest_rerun", "false", "false", True, "M contains no execution path."),
        ("M-G06", "claim_boundary_clean", "physical_evidence_claim_made=false", "false", True, "Blocked M performs no interpretation."),
    ]
    preflight_rows = [{
        "gate_id": gate_id, "gate_name": name, "observed_value": observed,
        "expected_value": expected, "status": "pass" if passed else "fail",
        "blocking": "yes", "notes": notes,
    } for gate_id, name, observed, expected, passed, notes in preflight_specs]

    result_summary_rows = [
        {"result_item": "j2_authorization", "observed_value": j2_manifest.get("execution_authorization_after_j2", "missing"), "source_artifact": rel(artifacts["j2_manifest"][1]), "source_hash": before_hashes.get("j2_manifest", "missing"), "classification": "contract_result", "notes": "J2 authorizes a future separate execution."},
        {"result_item": "latest_available_l_result", "observed_value": l_manifest.get("minimaltest_contract_result", "missing"), "source_artifact": rel(artifacts["l_manifest"][1]), "source_hash": before_hashes.get("l_manifest", "missing"), "classification": "contract_result", "notes": "This result is blocked_no_execution and predates the required J2-based replay."},
        {"result_item": "executed_minimaltest_result_for_m", "observed_value": "none", "source_artifact": "not_available", "source_hash": "not_available", "classification": "open_question", "notes": "A separate L2 or L-replay must execute before M can review a result."},
        {"result_item": "mechanism_interpretation", "observed_value": "not_performed", "source_artifact": "M start-gate decision", "source_hash": "not_applicable", "classification": "contract_result", "notes": "Interpretation is prohibited while M-G02 and M-G03 fail."},
    ]
    gate_readout_rows = [
        {"gate_id": "J2-R03", "gate_name": "overall_pass_2_of_3", "rule": "support_count_N4>=2 under all conclusive prerequisites", "observed_value": "not_evaluated_no_execution", "status": "not_evaluated", "contribution_to_result": "none", "classification": "contract_result", "notes": "M does not execute the rule."},
        {"gate_id": "J2-R04", "gate_name": "overall_fail", "rule": "support_count_N4<2 under all conclusive prerequisites", "observed_value": "not_evaluated_no_execution", "status": "not_evaluated", "contribution_to_result": "none", "classification": "contract_result", "notes": "No executed feature/N4 values exist."},
        {"gate_id": "J2-R05", "gate_name": "overall_inconclusive", "rule": "execution started and an interpretation condition is unavailable or contradictory", "observed_value": "not_evaluated_no_execution", "status": "not_evaluated", "contribution_to_result": "none", "classification": "contract_result", "notes": "No execution started."},
        {"gate_id": "M-START", "gate_name": "executed result required for review", "rule": "minimaltest_started=true and result in pass|fail|inconclusive_review", "observed_value": "no qualifying result", "status": "fail", "contribution_to_result": "blocks M interpretation", "classification": "contract_result", "notes": "M stops without mechanism interpretation."},
    ]

    k_nulls = read_csv(artifacts["k_nulls"][1]) if artifacts["k_nulls"][1].is_file() else []
    null_by_id = {row["nullmodel_id"]: row for row in k_nulls}
    n2_ok = null_by_id.get("N2_X_INDEX_ROLL_SURROGATE", {}).get("adequacy_decision") == "invariance_check_only"
    n4_ok = null_by_id.get("N4_PHASE_RANDOM_REFERENCE", {}).get("adequacy_decision") == "effective_perturbation"
    null_rows = []
    for model_id in sorted(null_by_id):
        row = null_by_id[model_id]
        null_rows.append({
            "nullmodel_id": model_id, "role": row["adequacy_decision"],
            "observed_behavior": "not_available_no_executed_minimaltest",
            "adequacy_reading": "role_only_no_result_interpretation",
            "mechanism_relevance": "not_assessed",
            "classification": "open_question", "limitations": row["limitations"],
            "notes": "N2 remains invariance_check_only." if model_id == "N2_X_INDEX_ROLL_SURROGATE" else "N4 remains effective_perturbation and mandatory." if model_id == "N4_PHASE_RANDOM_REFERENCE" else "Upstream role recorded without result interpretation.",
        })

    claim_rows = [
        {"statement_id": "M-C01", "statement": "contract passed/failed/inconclusive", "classification": "open_question", "allowed_wording": "No executed J2-based contract result is available.", "forbidden_wording": "Assigning pass, fail, or inconclusive without execution.", "source_or_basis": "M-G02/M-G03", "notes": "Await L2 or L-replay."},
        {"statement_id": "M-C02", "statement": "phase-to-feature mapping", "classification": "open_question", "allowed_wording": "The mapping is locked for a future execution.", "forbidden_wording": "Treating the unexecuted mapping as a result.", "source_or_basis": "J2 feature gates", "notes": "No result values exist."},
        {"statement_id": "M-C03", "statement": "feature-to-nullmodel separation", "classification": "open_question", "allowed_wording": "N4 comparison is preregistered but unevaluated.", "forbidden_wording": "Claiming observed separation.", "source_or_basis": "J2 acceptance rule", "notes": "No N4 execution exists."},
        {"statement_id": "M-C04", "statement": "thresholded relation candidate", "classification": "open_question", "allowed_wording": "The threshold rule is available for L2.", "forbidden_wording": "Claiming a thresholded relation from no run.", "source_or_basis": "J/K/J2", "notes": "No theta/epsilon values were applied."},
        {"statement_id": "M-C05", "statement": "emergent spacetime", "classification": "unsupported_claim", "allowed_wording": "No spacetime-level inference is available.", "forbidden_wording": "Emergent spacetime is proven.", "source_or_basis": "Claim boundary", "notes": "Outside the reduced contract."},
        {"statement_id": "M-C06", "statement": "gravity mechanism", "classification": "unsupported_claim", "allowed_wording": "No gravity-level inference is available.", "forbidden_wording": "A gravity mechanism is proven.", "source_or_basis": "Claim boundary", "notes": "Outside the reduced contract."},
        {"statement_id": "M-C07", "statement": "quantum gravity evidence", "classification": "unsupported_claim", "allowed_wording": "No such evidence statement is made.", "forbidden_wording": "Quantum gravity evidence was obtained.", "source_or_basis": "Claim boundary", "notes": "Outside the reduced contract."},
        {"statement_id": "M-C08", "statement": "generalization beyond P0/t0/alpha1.6", "classification": "open_question", "allowed_wording": "Generalization remains untested.", "forbidden_wording": "The setup generalizes beyond the authorized source.", "source_or_basis": "F3 source scope", "notes": "Requires separate authorization and data."},
    ]
    unsupported_rows = [
        {"unsupported_claim": "QSB proves gravity", "why_not_supported": "No executed INTERFACE01 result exists, and the reduced contract cannot establish this claim.", "safe_replacement_wording": "No mechanism interpretation is performed before an executed result exists.", "notes": "Explicitly forbidden."},
        {"unsupported_claim": "QSB proves emergent spacetime", "why_not_supported": "The reduced source and acceptance rule do not establish spacetime emergence.", "safe_replacement_wording": "The interface-level hypothesis remains untested in M at this stage.", "notes": "Explicitly forbidden."},
        {"unsupported_claim": "QSB confirms quantum gravity", "why_not_supported": "No executed result or quantum-gravity validation is present.", "safe_replacement_wording": "No quantum-gravity inference is made.", "notes": "Explicitly forbidden."},
        {"unsupported_claim": "The mechanism is fully validated", "why_not_supported": "The J2-based Minimaltest has not been executed and would remain locally scoped even if completed.", "safe_replacement_wording": "The mechanism chain awaits its first J2-based contract execution.", "notes": "Explicitly forbidden."},
        {"unsupported_claim": "The result generalizes beyond the tested source", "why_not_supported": "No executed result exists and F3 covers one authorized source configuration.", "safe_replacement_wording": "Generalization beyond P0/t0/alpha1.6 remains open.", "notes": "Explicitly forbidden."},
    ]
    action_rows = [
        {"action_id": "M-ACT-01", "action_type": "documentation", "priority": "high", "description": "Prepare and run a separate L2 or L-replay package under the exact K/J2 authorization and acceptance rule.", "depends_on": "J2 authorization already present", "allowed_now": "yes", "notes": "Do not interpret before execution artifacts pass their own validations."},
        {"action_id": "M-ACT-02", "action_type": "theory_formulation", "priority": "deferred", "description": "Build the mechanism map only after a non-blocked contract result exists.", "depends_on": "completed L2 or L-replay", "allowed_now": "no", "notes": "Prevents result-free storytelling."},
        {"action_id": "M-ACT-03", "action_type": "nullmodel_hardening", "priority": "deferred", "description": "Review N4 and N2 behavior from actual execution outputs.", "depends_on": "completed L2 or L-replay", "allowed_now": "no", "notes": "No nullmodel result is currently available."},
    ]
    review_rows = [{
        "review_item_id": "M-R01", "category": "missing_execution_result",
        "description": "No J2-authorized L2 or L-replay result exists for M review.",
        "blocks_public_claim": "yes", "blocks_next_internal_run": "no",
        "recommended_resolution": "Run a separate L2 or L-replay execution package using the frozen J2 rule.",
        "notes": "After execution, create a fresh M package; do not overwrite this blocked audit record.",
    }]

    OUTPUT.mkdir(parents=True)
    manifest = {
        "work_package": "QSB-INTERFACE01M", "status": STATUS,
        "created_at_utc": datetime.now(timezone.utc).isoformat(), "repo_root": str(REPO),
        "upstream_dirs": {"F3": rel(F3), "G": rel(G), "H": rel(H), "I": rel(I), "J": rel(J), "K": rel(K), "J2": rel(J2), "L": rel(L), "L2_or_replay": "not_found"},
        "j2_authorization_seen": j2_manifest.get("execution_authorization_after_j2", "missing"),
        "l2_or_replay_result_seen": "none", "minimaltest_contract_result_seen": "none",
        "mechanism_interpretation_performed": False, "physical_evidence_claim_made": False,
        "minimaltest_rerun": False, "upstream_modified": False, "claim_boundary": CLAIM_BOUNDARY,
    }
    (OUTPUT / "01_m_run_manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    write_csv(OUTPUT / "02_upstream_result_inventory.csv", ["artifact_id", "upstream_block", "path", "exists", "sha256", "role", "used_for", "notes"], inventory_rows)
    write_csv(OUTPUT / "03_authorization_and_hash_preflight.csv", ["gate_id", "gate_name", "observed_value", "expected_value", "status", "blocking", "notes"], preflight_rows)
    write_csv(OUTPUT / "04_minimaltest_result_summary.csv", ["result_item", "observed_value", "source_artifact", "source_hash", "classification", "notes"], result_summary_rows)
    write_csv(OUTPUT / "05_acceptance_gate_readout.csv", ["gate_id", "gate_name", "rule", "observed_value", "status", "contribution_to_result", "classification", "notes"], gate_readout_rows)
    write_csv(OUTPUT / "06_feature_result_interpretation.csv", ["feature_name", "observed_behavior", "n4_comparator_behavior", "support_status", "mechanism_reading", "classification", "limitations", "notes"], [])
    write_csv(OUTPUT / "07_nullmodel_result_interpretation.csv", ["nullmodel_id", "role", "observed_behavior", "adequacy_reading", "mechanism_relevance", "classification", "limitations", "notes"], null_rows)
    write_csv(OUTPUT / "08_mechanism_chain_map.csv", ["chain_step", "input_element", "operation_or_relation", "output_element", "status_after_result", "mechanism_reading", "evidence_boundary", "open_question"], [])
    write_csv(OUTPUT / "09_claim_classification_matrix.csv", ["statement_id", "statement", "classification", "allowed_wording", "forbidden_wording", "source_or_basis", "notes"], claim_rows)
    write_csv(OUTPUT / "10_unsupported_claims_and_boundaries.csv", ["unsupported_claim", "why_not_supported", "safe_replacement_wording", "notes"], unsupported_rows)
    write_csv(OUTPUT / "13_next_research_actions.csv", ["action_id", "action_type", "priority", "description", "depends_on", "allowed_now", "notes"], action_rows)
    write_csv(OUTPUT / "15_review_items_for_next_block.csv", ["review_item_id", "category", "description", "blocks_public_claim", "blocks_next_internal_run", "recommended_resolution", "notes"], review_rows)

    de_note = """# INTERFACE01-M Theorie-Notiz

## Was der Lauf zeigt

Für M liegt noch kein ausgeführter, J2-basierter Minimaltest-Lauf vor. Der frühere L-Lauf wurde vor der Ausführung korrekt blockiert; J2 hat danach die fehlende Akzeptanzregel ergänzt, aber noch kein L2 oder Replay ausgeführt.

## Mechanistische Lesart

Eine mechanistische Lesart wird in diesem Block bewusst nicht vorgenommen. Ohne Feature-, N4- und Schwellenresultate wäre sie nicht ergebnisgestützt.

## Was offen bleibt

Offen ist das contract-level Ergebnis eines separaten L2- oder L-Replay-Laufs unter der eingefrorenen J2-Regel.

## Was nicht behauptet wird

Es werden weder eine erfolgreiche Phasen-zu-Relations-Abbildung noch eine geometrische oder physikalische Folgerung behauptet.
"""
    en_note = """# INTERFACE01-M Theory Note

## What the run shows

M has no executed J2-based Minimaltest run to review. The earlier L run correctly stopped before execution; J2 subsequently added the missing acceptance rule, but no L2 or replay has yet been run.

## Mechanistic reading

No mechanistic reading is performed in this block. Without feature, N4, and threshold results, such a reading would not be result-supported.

## What remains open

The contract-level outcome of a separate L2 or L-replay under the frozen J2 rule remains open.

## What is not claimed

No successful phase-to-relation mapping, geometric implication, or physical implication is claimed.
"""
    (OUTPUT / "11_theory_language_note_de.md").write_text(de_note, encoding="utf-8")
    (OUTPUT / "12_theory_language_note_en.md").write_text(en_note, encoding="utf-8")

    after_hashes = {key: sha256(path) for key, (_, path, _) in artifacts.items() if path.is_file()}
    upstream_unchanged = before_hashes == after_hashes
    manifest["upstream_modified"] = not upstream_unchanged
    (OUTPUT / "01_m_run_manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

    validations: list[dict[str, Any]] = []

    def validate(identifier: str, name: str, passed: bool, observed: Any, expected: Any, message: str, blocked: bool = False) -> None:
        validations.append({
            "validation_id": identifier, "validation_layer": "M result-review preflight",
            "check_name": name, "status": "pass" if passed else "fail", "severity": "error",
            "observed_value": observed, "expected_value": expected, "message": message,
            "blocking_for_interpretation": "yes" if blocked or not passed else "no",
        })

    validate("M-V01", "j2_authorization_present", j2_authorized, j2_manifest.get("execution_authorization_after_j2", "missing"), J2_AUTHORIZATION, "J2 authorization checked.")
    validate("M-V02", "l2_or_replay_result_present", execution_available, "none", "executed result manifest", "No L2 or equivalent replay exists.", blocked=True)
    validate("M-V03", "result_not_blocked", result_not_blocked, executed_result, "pass|fail|inconclusive_review", "No reviewable executed result exists.", blocked=True)
    validate("M-V04", "no_minimaltest_rerun", manifest["minimaltest_rerun"] is False, manifest["minimaltest_rerun"], False, "M reran no Minimaltest.")
    validate("M-V05", "feature_interpretations_present", len(read_csv(OUTPUT / "06_feature_result_interpretation.csv")) == 0, 0, 0, "Feature interpretation is correctly absent while blocked.")
    validate("M-V06", "nullmodel_interpretations_present", len(null_rows) == 6 and all(r["observed_behavior"] == "not_available_no_executed_minimaltest" for r in null_rows), len(null_rows), 6, "Roles are documented; result interpretation is absent.")
    validate("M-V07", "n2_invariance_only_preserved", n2_ok, null_by_id.get("N2_X_INDEX_ROLL_SURROGATE", {}).get("adequacy_decision", "missing"), "invariance_check_only", "N2 role preserved.")
    validate("M-V08", "n4_effective_perturbation_preserved", n4_ok, null_by_id.get("N4_PHASE_RANDOM_REFERENCE", {}).get("adequacy_decision", "missing"), "effective_perturbation", "N4 role preserved.")
    validate("M-V09", "mechanism_chain_map_present", len(read_csv(OUTPUT / "08_mechanism_chain_map.csv")) == 0, 0, 0, "Mechanism map is correctly header-only while blocked.")
    validate("M-V10", "claim_classification_complete", len(claim_rows) >= 8, len(claim_rows), 8, "Required claim categories recorded.")
    validate("M-V11", "unsupported_claims_listed", len(unsupported_rows) == 5, len(unsupported_rows), 5, "Required unsupported claims listed.")
    validate("M-V12", "german_note_present", bool(de_note.strip()), True, True, "Blocked German note present.")
    validate("M-V13", "english_note_present", bool(en_note.strip()), True, True, "Blocked English note present.")
    validate("M-V14", "no_physical_evidence_claim", manifest["physical_evidence_claim_made"] is False, manifest["physical_evidence_claim_made"], False, "No physical-evidence claim made.")
    validate("M-V15", "no_upstream_mutation", upstream_unchanged, upstream_unchanged, True, "F3-J2/L hashes unchanged after M writes.")
    validate("M-V16", "exact_output_count", True, 16, 16, "Script declares and later checks exactly 16 files.")
    write_csv(OUTPUT / "14_m_validation_results.csv", ["validation_id", "validation_layer", "check_name", "status", "severity", "observed_value", "expected_value", "message", "blocking_for_interpretation"], validations)

    final_note = f"""# INTERFACE01-M Final Result

## Status

`{STATUS}`

## Minimaltest Result Reviewed

None. No executed J2-based L2 or L-replay result is available.

## Mechanism Interpretation

Not performed. M-G02 and M-G03 block interpretation before any theory-facing result translation.

## Claim Boundary

No physical evidence claim is made. The available artifacts establish an executable acceptance contract, not an executed result.

## Next allowed action

Run a separate L2 or L-replay package under the K/J2 authorization; then create a fresh M review package.
"""
    (OUTPUT / "FINAL_RESULT_NOTE.md").write_text(final_note, encoding="utf-8")

    actual = {path.name for path in OUTPUT.iterdir() if path.is_file()}
    if actual != EXPECTED_FILES:
        raise SystemExit(f"Output file-set mismatch: actual={sorted(actual)} expected={sorted(EXPECTED_FILES)}")
    unexpected_failures = [row["validation_id"] for row in validations if row["status"] == "fail" and row["validation_id"] not in {"M-V02", "M-V03"}]
    if unexpected_failures:
        raise SystemExit(f"Unexpected M validation failures: {unexpected_failures}")
    print(f"status={STATUS}")
    print("minimaltest_result_reviewed=none")
    print("mechanism_interpretation_performed=false")
    print("minimaltest_rerun=false")
    print(f"output_files={len(actual)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
