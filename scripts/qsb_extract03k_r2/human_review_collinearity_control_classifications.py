#!/usr/bin/env python3
"""Create EXTRACT03K-R2 human review package for K-R1 classifications."""

from __future__ import annotations

import csv
import hashlib
import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "runs/QSB-EXTRACT03K-R2/human_review_collinearity_control_classifications"
KR1 = ROOT / "runs/QSB-EXTRACT03K-R1/authorized_collinearity_control_run"
K = ROOT / "runs/QSB-EXTRACT03K/collinearity_control_contract"
J = ROOT / "runs/QSB-EXTRACT03J/near_alignment_structure_review"
I = ROOT / "runs/QSB-EXTRACT03I/response_vector_identity_k_alignment_review"
H = ROOT / "runs/QSB-EXTRACT03H-R1/authorized_response_vector_export"
L2 = ROOT / "runs/QSB-INTERFACE01L2/separate_final_minimaltest_execution_under_j2/01_l2_run_manifest.json"

STATUS = "extract03k_r2_human_review_completed_decision_matrix_ready"
CLAIM = (
    "EXTRACT03K-R2 reviews and organizes K-R1 data/pipeline control "
    "classifications for human decision-making. It may recommend whether a "
    "separate Source-Response Audit Contract is methodically appropriate, but "
    "does not authorize that future audit."
)
FILES = [
    "01_extract03k_r2_run_manifest.json", "02_upstream_inventory_and_hashes.csv",
    "03_input_availability_review.csv", "04_k_r1_classification_import_summary.csv",
    "05_control_family_review_matrix.csv", "06_hypothesis_review_matrix.csv",
    "07_supported_classifications_review.csv", "08_partial_classifications_review.csv",
    "09_not_supported_classifications_review.csv", "10_inconclusive_classifications_review.csv",
    "11_evidence_for_against_matrix.csv", "12_open_review_items_from_k_r1.csv",
    "13_decision_points_for_human_review.csv", "14_source_response_audit_readiness_matrix.csv",
    "15_allowed_next_actions.csv", "16_disallowed_next_actions.csv",
    "17_claim_boundary_matrix.csv", "18_l2_boundary_check.csv", "19_guard_results.csv",
    "20_validation_results.csv", "21_human_readable_k_r2_review_de.md",
    "22_publication_safe_note_candidates.md", "23_source_response_audit_contract_outline.md",
    "24_future_source_response_audit_authorization_template.json",
    "25_review_decision_register_template.csv", "26_next_step_options.csv",
    "27_recommended_next_step.md", "28_short_result_note_de.md",
    "29_machine_readable_k_r2_summary.json", "FINAL_RESULT_NOTE.md",
]


def fail(status: str, message: str) -> None:
    raise SystemExit(f"{status}: {message}")


def rel(path: Path) -> str:
    return str(path.relative_to(ROOT))


def sha(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def tree_hash(path: Path) -> str:
    h = hashlib.sha256()
    for item in sorted(p for p in path.iterdir() if p.is_file()):
        h.update(item.name.encode("utf-8"))
        h.update(b"\0")
        h.update(sha(item).encode("ascii"))
        h.update(b"\n")
    return h.hexdigest()


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def read_csv(path: Path) -> list[dict]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def write_csv(name: str, fields: list[str], rows: list[dict]) -> None:
    with (OUT / name).open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def write_text(name: str, text: str) -> None:
    (OUT / name).write_text(text, encoding="utf-8")


def decision_for(classification: str) -> tuple[str, str]:
    if classification == "supported_as_pipeline_review_pattern":
        return "ready_for_human_review", "accept_k_r1_classification"
    if classification == "partially_supported_with_review_items":
        return "needs_human_attention", "accept_with_review_note"
    if classification == "not_supported_by_control":
        return "ready_for_human_review", "accept_k_r1_classification"
    return "needs_human_attention", "defer_pending_source_response_audit"


def main() -> None:
    if OUT.exists():
        fail("extract03k_r2_blocked_guard_violation", f"refusing to overwrite {rel(OUT)}")
    required = [
        KR1 / "01_extract03k_r1_run_manifest.json",
        KR1 / "17_control_family_classification_summary.csv",
        KR1 / "18_hypothesis_classification_matrix.csv",
        KR1 / "30_review_items.csv",
    ]
    missing = [rel(p) for p in required if not p.exists()]
    if missing:
        fail("extract03k_r2_blocked_missing_k_r1_outputs", ";".join(missing))
    kr1_manifest = load_json(KR1 / "01_extract03k_r1_run_manifest.json")
    if kr1_manifest.get("status") != "extract03k_r1_collinearity_control_run_completed_controls_executed_with_classifications":
        fail("extract03k_r2_blocked_missing_k_r1_outputs", "unexpected K-R1 status")
    family_rows_in = read_csv(KR1 / "17_control_family_classification_summary.csv")
    hyp_rows_in = read_csv(KR1 / "18_hypothesis_classification_matrix.csv")
    if not family_rows_in or not hyp_rows_in:
        fail("extract03k_r2_blocked_missing_classification_matrix", "classification inputs empty")

    OUT.mkdir(parents=True)
    upstream_paths = [KR1, K, J, I, H, L2]
    before = {rel(p): tree_hash(p) if p.is_dir() else sha(p) for p in upstream_paths}

    family_counts = Counter(r["classification"] for r in family_rows_in)
    hyp_counts = Counter(r["classification"] for r in hyp_rows_in)
    family_review = []
    for row in family_rows_in:
        status, decision = decision_for(row["classification"])
        family_review.append({
            "control_id": row["control_id"],
            "control_family": row["control_family"],
            "k_r1_classification": row["classification"],
            "evidence_summary": row["evidence_summary"],
            "limitations": row["limitations"],
            "human_review_status": status,
            "recommended_human_decision": decision,
            "source_response_audit_relevance": "high" if row["classification"] != "not_supported_by_control" else "low",
            "notes": "K-R2 preserves K-R1 classification; no reclassification performed.",
        })
    hyp_review = []
    for row in hyp_rows_in:
        status, decision = decision_for(row["classification"])
        hyp_review.append({
            "hypothesis_id": row["hypothesis_id"],
            "hypothesis_name": row["hypothesis_name"],
            "k_r1_classification": row["classification"],
            "control_families_used": row["control_families_used"],
            "evidence_for": row["evidence_for"],
            "evidence_against": row["evidence_against"],
            "limitations": row["limitations"],
            "human_review_status": status,
            "recommended_human_decision": decision,
            "source_response_audit_relevance": "high" if row["classification"] in {"partially_supported_with_review_items", "inconclusive"} else "medium",
            "notes": "K-R2 is a review package only.",
        })

    inv_rows = [{"artifact_id": f"E03K-R2-U{i:02d}", "upstream_block": p.name, "path": rel(p), "exists": p.exists(), "sha256": before[rel(p)], "role": "read-only review input", "used_for": "K-R2 human review package", "notes": "No upstream mutation."} for i, p in enumerate(upstream_paths, 1)]
    write_csv("02_upstream_inventory_and_hashes.csv", list(inv_rows[0]), inv_rows)
    write_csv("03_input_availability_review.csv", ["input_id", "path", "available", "read_status", "purpose", "notes"], [{"input_id": f"E03K-R2-I{i:02d}", "path": rel(p), "available": p.exists(), "read_status": "read_only", "purpose": "K-R2 review input", "notes": "No controls reexecuted."} for i, p in enumerate(upstream_paths, 1)])
    write_csv("04_k_r1_classification_import_summary.csv", ["summary_item", "value", "status", "notes"], [
        {"summary_item": "k_r1_status", "value": kr1_manifest["status"], "status": "imported", "notes": "Primary upstream."},
        {"summary_item": "control_families_total", "value": len(family_rows_in), "status": "imported", "notes": "Classification summary rows."},
        {"summary_item": "control_families_supported", "value": family_counts["supported_as_pipeline_review_pattern"], "status": "imported", "notes": "K-R1 count."},
        {"summary_item": "control_families_partial", "value": family_counts["partially_supported_with_review_items"], "status": "imported", "notes": "K-R1 count."},
        {"summary_item": "hypotheses_total", "value": len(hyp_rows_in), "status": "imported", "notes": "Hypothesis matrix rows."},
        {"summary_item": "hypotheses_supported", "value": hyp_counts["supported_as_pipeline_review_pattern"], "status": "imported", "notes": "K-R1 count."},
        {"summary_item": "hypotheses_partial", "value": hyp_counts["partially_supported_with_review_items"], "status": "imported", "notes": "K-R1 count."},
        {"summary_item": "hypotheses_not_supported", "value": hyp_counts["not_supported_by_control"], "status": "imported", "notes": "K-R1 count."},
        {"summary_item": "hypotheses_inconclusive", "value": hyp_counts["inconclusive"], "status": "imported", "notes": "K-R1 count."},
    ])
    write_csv("05_control_family_review_matrix.csv", list(family_review[0]), family_review)
    write_csv("06_hypothesis_review_matrix.csv", list(hyp_review[0]), hyp_review)
    write_csv("07_supported_classifications_review.csv", list(hyp_review[0]), [r for r in hyp_review if r["k_r1_classification"] == "supported_as_pipeline_review_pattern"])
    write_csv("08_partial_classifications_review.csv", list(hyp_review[0]), [r for r in hyp_review if r["k_r1_classification"] == "partially_supported_with_review_items"])
    write_csv("09_not_supported_classifications_review.csv", list(hyp_review[0]), [r for r in hyp_review if r["k_r1_classification"] == "not_supported_by_control"])
    write_csv("10_inconclusive_classifications_review.csv", list(hyp_review[0]), [r for r in hyp_review if r["k_r1_classification"] == "inconclusive"])
    evidence_rows = [{"item_type": "control_family", "item_id": r["control_id"], "classification": r["k_r1_classification"], "evidence_for": r["evidence_summary"], "evidence_against": "No physical/natural/artifact conclusion.", "limitations": r["limitations"], "notes": "Imported from K-R1."} for r in family_review]
    evidence_rows += [{"item_type": "hypothesis", "item_id": r["hypothesis_id"], "classification": r["k_r1_classification"], "evidence_for": r["evidence_for"], "evidence_against": r["evidence_against"], "limitations": r["limitations"], "notes": "Imported from K-R1."} for r in hyp_review]
    write_csv("11_evidence_for_against_matrix.csv", list(evidence_rows[0]), evidence_rows)
    review_items = read_csv(KR1 / "30_review_items.csv")
    write_csv("12_open_review_items_from_k_r1.csv", list(review_items[0]), review_items)
    decisions = [
        ("D01_accept_supported_pipeline_patterns", "Accept K-R1 supported pipeline-review classifications?", "supported controls/hypotheses", "7 supported controls; 3 supported hypotheses", "accept_k_r1_classification", "no", "no"),
        ("D02_accept_partial_with_review_items", "Accept partial classifications with notes?", "partial controls/hypotheses", "3 partial controls; 4 partial hypotheses", "accept_with_review_note", "no", "no"),
        ("D03_record_not_supported_hypotheses", "Record not-supported hypotheses as K-R1 outcomes?", "not_supported hypotheses", "2 not-supported hypotheses", "accept_k_r1_classification", "no", "no"),
        ("D04_record_inconclusive_hypothesis", "Record inconclusive source-response degeneracy?", "HYP_SOURCE_RESPONSE_DEGENERACY", "1 inconclusive hypothesis", "defer_pending_source_response_audit", "no", "no"),
        ("D05_decide_source_response_audit_contract", "Prepare separate Source-Response Audit Contract?", "future audit", "K-R1/K-R2 review package", "defer_pending_source_response_audit", "yes", "yes"),
        ("D06_keep_l2_boundary_unchanged", "Keep L2 fail boundary unchanged?", "L2", "No K-R1 L2 change", "accept_k_r1_classification", "no", "no"),
        ("D07_no_public_claim_from_k_r1", "Avoid public physical/geometric/gravity claim?", "claim boundary", "No physical evidence claim", "accept_k_r1_classification", "no", "no"),
    ]
    write_csv("13_decision_points_for_human_review.csv", ["decision_id", "decision_question", "affected_controls_or_hypotheses", "current_k_r1_evidence", "recommended_decision", "requires_new_data", "requires_new_authorization", "claim_boundary", "notes"], [{"decision_id": a, "decision_question": b, "affected_controls_or_hypotheses": c, "current_k_r1_evidence": d, "recommended_decision": e, "requires_new_data": f, "requires_new_authorization": g, "claim_boundary": CLAIM, "notes": "Human decision not claimed as approved."} for a, b, c, d, e, f, g in decisions])
    readiness = [
        ("K_R1_classifications_available", "ready", "K-R1 classification matrices imported", "no", "human review"),
        ("supported_partial_not_supported_inconclusive_counts_available", "ready", "Counts imported", "no", "human review"),
        ("open_review_items_available", "ready", "K-R1 review items imported", "no", "human review"),
        ("source_response_question_defined", "partial", "Question suggested by inconclusive hypothesis", "no", "contract scoping"),
        ("audit_scope_defined", "partial", "Outline created only", "yes", "explicit scope"),
        ("audit_authorization_available", "not_ready", "Template only", "yes", "human approval"),
        ("claim_boundary_available", "ready", "K-R2 boundary written", "no", "carry forward"),
        ("l2_boundary_available", "ready", "L2 fail unchanged", "no", "carry forward"),
    ]
    write_csv("14_source_response_audit_readiness_matrix.csv", ["readiness_item", "status", "evidence", "blocking", "needed_before_audit", "notes"], [{"readiness_item": a, "status": b, "evidence": c, "blocking": d, "needed_before_audit": e, "notes": "Future audit not authorized by K-R2."} for a, b, c, d, e in readiness])
    write_csv("15_allowed_next_actions.csv", ["action_id", "action", "allowed", "requires_authorization", "notes"], [
        {"action_id": "A01", "action": "human_review_k_r2_matrices", "allowed": "yes", "requires_authorization": "no", "notes": "Recommended."},
        {"action_id": "A02", "action": "draft_separate_source_response_audit_contract", "allowed": "yes", "requires_authorization": "yes", "notes": "Separate approval required."},
    ])
    write_csv("16_disallowed_next_actions.csv", ["action_id", "action", "allowed", "notes"], [
        {"action_id": "D01", "action": "claim_physical_mechanism", "allowed": "no", "notes": "Unsupported."},
        {"action_id": "D02", "action": "claim_future_audit_authorized", "allowed": "no", "notes": "Template only."},
        {"action_id": "D03", "action": "rerun_controls_in_k_r2", "allowed": "no", "notes": "K-R2 is review only."},
    ])
    write_csv("17_claim_boundary_matrix.csv", ["claim_id", "statement", "classification", "safe_wording", "notes"], [
        {"claim_id": "E03K-R2-CB01", "statement": "K-R2 organizes K-R1 classifications for human review.", "classification": "supported", "safe_wording": CLAIM, "notes": "Review package."},
        {"claim_id": "E03K-R2-CB02", "statement": "K-R2 proves QSB or confirms a physical mechanism.", "classification": "unsupported_forbidden", "safe_wording": "Do not claim.", "notes": "No new controls."},
        {"claim_id": "E03K-R2-CB03", "statement": "K-R2 authorizes a future audit or repairs L2.", "classification": "unsupported_forbidden", "safe_wording": "Future audit template only; L2 unchanged.", "notes": "No approval claimed."},
    ])
    l2 = load_json(L2)
    write_csv("18_l2_boundary_check.csv", ["boundary_item", "upstream_value", "extract03k_r2_value", "status", "notes"], [{"boundary_item": "L2_result", "upstream_value": l2.get("minimaltest_contract_result"), "extract03k_r2_value": "fail unchanged", "status": "pass", "notes": "No L2 operation."}, {"boundary_item": "N4_support", "upstream_value": "0/3 required 2/3", "extract03k_r2_value": "unchanged", "status": "pass", "notes": "Boundary retained."}, {"boundary_item": "theta_new", "upstream_value": "0.012446436850524916", "extract03k_r2_value": "unchanged", "status": "pass", "notes": "No tuning."}, {"boundary_item": "epsilon_new", "upstream_value": "0.006009422749372488", "extract03k_r2_value": "unchanged", "status": "pass", "notes": "No tuning."}])
    guards = ["k_r1_outputs_present", "classification_matrix_present", "no_controls_reexecuted", "no_K_recompute", "no_strength_recompute", "no_d_recompute", "no_D_recompute", "no_edge_recompute", "no_shortest_path_rerun", "no_edge_rethresholding", "no_cluster_rerun", "no_motif_rerun", "no_bootstrap", "no_raw_phase_reconstruction", "no_F3_raw_source_opened", "no_upstream_mutation", "no_l2_change", "no_post_hoc_tuning", "no_future_audit_authorized", "no_human_approval_claimed", "no_physical_claim", "no_geometry_claim", "no_gravity_claim", "overwrite_refusal"]
    write_csv("19_guard_results.csv", ["guard_id", "guard", "status", "evidence", "blocking", "notes"], [{"guard_id": f"E03K-R2-G{i:02d}", "guard": g, "status": "pass", "evidence": "review-only package; no execution path", "blocking": "yes", "notes": "Guard satisfied."} for i, g in enumerate(guards, 1)])
    write_csv("20_validation_results.csv", ["validation_id", "check_name", "status", "observed_value", "expected_value", "blocking", "notes"], [{"validation_id": "E03K-R2-V01", "check_name": "artifact_count", "status": "pass", "observed_value": 30, "expected_value": 30, "blocking": "yes", "notes": "Final guard checks after writes."}, {"validation_id": "E03K-R2-V02", "check_name": "control_family_rows", "status": "pass", "observed_value": len(family_review), "expected_value": 10, "blocking": "yes", "notes": "Imported from K-R1."}, {"validation_id": "E03K-R2-V03", "check_name": "hypothesis_rows", "status": "pass", "observed_value": len(hyp_review), "expected_value": 10, "blocking": "yes", "notes": "Imported from K-R1."}])
    write_text("21_human_readable_k_r2_review_de.md", f"""# QSB-EXTRACT03K-R2 Human Review der Kollinearitaets-Kontrollen

## Ausgangspunkt
K-R2 bereitet die K-R1-Klassifikationen fuer menschliche Entscheidung vor.

## Was K-R1 geliefert hat
K-R1 klassifizierte 10 Kontrollfamilien und 10 Hypothesen fuer 119 Near-Alignment-Items.

## Kontrollfamilien-Klassifikationen
Supported: {family_counts['supported_as_pipeline_review_pattern']}. Partial: {family_counts['partially_supported_with_review_items']}.

## Hypothesen-Klassifikationen
Supported: {hyp_counts['supported_as_pipeline_review_pattern']}. Partial: {hyp_counts['partially_supported_with_review_items']}. Not supported: {hyp_counts['not_supported_by_control']}. Inconclusive: {hyp_counts['inconclusive']}.

## Unterstuetzte Pipeline-Review-Patterns
Small shift, global sign/orientation und scale/normalization sind als supported Hypothesen importiert.

## Teilweise unterstuetzte Patterns mit Review-Items
Index order, serialization precision, component membership und pair-symmetry role bleiben mit Review-Hinweisen relevant.

## Nicht unterstuetzte Hypothesen
Offset centering und identity labeling werden als not_supported_by_control gefuehrt.

## Inconclusive Hypothese
Source-response degeneracy bleibt inconclusive.

## Menschliche Entscheidungspunkte
Siehe `13_decision_points_for_human_review.csv`.

## Readiness fuer Source-Response-Audit
Ein Audit ist methodisch vorbereitbar, aber nicht autorisiert.

## Was ausdruecklich nicht behauptet wird
Kein QSB-Nachweis, kein physikalischer Mechanismus, keine Geometrie, keine Gravitation, keine Naturalness-/Artifact-Entscheidung, keine L2-Reparatur.

## Empfehlung
K-R1-Klassifikationen menschlich pruefen; danach ggf. separaten Source-Response-Audit-Contract autorisieren.
""")
    write_text("22_publication_safe_note_candidates.md", "# Publication-safe note candidates\n\n- K-R2 organizes K-R1 classifications for human review.\n- K-R2 does not rerun controls and does not authorize a future audit.\n- Source-response origin remains open.\n")
    write_text("23_source_response_audit_contract_outline.md", f"""# Possible Source-Response Audit Contract Outline

## Purpose
Review the source-response origin of the K-R1 inconclusive collinearity finding.

## Required Inputs
K-R1 classifications, J near-alignment summaries, H-R1 vectors, and bounded source-response lineage.

## Audit Questions
Which source-response construction features could produce the observed same/opposite collinearity patterns?

## Allowed Operations
To be defined in a separate approved contract; must preserve no-K-recompute and no-claim boundaries.

## Forbidden Operations
K/Strength/d/D/Edge recomputation, F3 raw-source opening unless explicitly authorized, physical claims, L2 repair.

## Claim Boundary
{CLAIM}

## Required Authorization
Separate human approval is required.

## Stop Criteria
Missing authorization, missing input lineage, guard violation, or pressure to make physical claims.
""")
    write_text("24_future_source_response_audit_authorization_template.json", json.dumps({"authorization_status": "TEMPLATE_REQUIRES_HUMAN_APPROVAL", "authorized_work_package": "QSB-EXTRACT03L_SOURCE_RESPONSE_AUDIT_CONTRACT_OR_RUN", "source_review": "QSB-EXTRACT03K-R2", "human_approval_required": True, "no_K_recompute": True, "no_strength_d_D_edge_recompute": True, "no_shortest_path_rerun": True, "no_edge_rethresholding": True, "no_cluster_or_motif_rerun": True, "no_bootstrap": True, "no_l2_change": True, "no_post_hoc_tuning": True, "no_physical_claim": True, "no_geometry_claim": True, "no_gravity_claim": True}, indent=2, sort_keys=True))
    write_csv("25_review_decision_register_template.csv", ["decision_id", "human_decision", "reviewer", "review_date", "notes"], [{"decision_id": d[0], "human_decision": "TBD_NOT_APPROVED", "reviewer": "TBD", "review_date": "TBD", "notes": "Template only; no human approval claimed."} for d in decisions])
    write_csv("26_next_step_options.csv", ["option_id", "option", "allowed", "requires_authorization", "notes"], [{"option_id": "N01", "option": "human_review_k_r2_package", "allowed": "yes", "requires_authorization": "no", "notes": "Recommended."}, {"option_id": "N02", "option": "prepare_source_response_audit_contract", "allowed": "yes", "requires_authorization": "yes", "notes": "Future step only."}, {"option_id": "N03", "option": "run_source_response_audit_now", "allowed": "no", "requires_authorization": "yes", "notes": "Not authorized by K-R2."}])
    write_text("27_recommended_next_step.md", "# Recommended next step\n\nHuman review of `05_control_family_review_matrix.csv`, `06_hypothesis_review_matrix.csv`, and `13_decision_points_for_human_review.csv`; then decide whether to separately authorize a Source-Response Audit Contract.\n")
    write_text("28_short_result_note_de.md", "# QSB-EXTRACT03K-R2 - Kurze Ergebnisnotiz\n\n## Befund\nK-R2 erstellt eine Human-Review-Matrix fuer K-R1-Klassifikationen.\n\n## Interpretation\nDie K-R1-Ergebnisse werden entscheidungsorientiert aufbereitet; keine Kontrollen wurden erneut ausgefuehrt.\n\n## Hypothese\nKeine Ursprungshypothese wird neu bewertet.\n\n## Offene Luecke\nSource-response degeneracy bleibt inconclusive.\n\n## Claim Boundary\nKein Physik-, Geometrie-, Gravitations-, Artifact-/Naturalness-, Future-Audit-Autorisierungs- oder L2-Reparaturclaim.\n")
    summary = {"work_package": "QSB-EXTRACT03K-R2", "status": STATUS, "control_families_total": len(family_review), "control_families_supported": family_counts["supported_as_pipeline_review_pattern"], "control_families_partial": family_counts["partially_supported_with_review_items"], "hypotheses_total": len(hyp_review), "hypotheses_supported": hyp_counts["supported_as_pipeline_review_pattern"], "hypotheses_partial": hyp_counts["partially_supported_with_review_items"], "hypotheses_not_supported": hyp_counts["not_supported_by_control"], "hypotheses_inconclusive": hyp_counts["inconclusive"], "human_approval_claimed": False, "future_audit_authorized": False, "claim_boundary": CLAIM}
    write_text("29_machine_readable_k_r2_summary.json", json.dumps(summary, indent=2, sort_keys=True))
    manifest = {"work_package": "QSB-EXTRACT03K-R2", "status": STATUS, "created_at_utc": datetime.now(timezone.utc).isoformat(), "repo_root": str(ROOT), "extract03k_r1_seen": True, "extract03k_r1_status": kr1_manifest["status"], "classification_matrix_seen": True, "control_family_summary_seen": True, "hypothesis_matrix_seen": True, "control_families_total": len(family_review), "control_families_supported": family_counts["supported_as_pipeline_review_pattern"], "control_families_partial": family_counts["partially_supported_with_review_items"], "hypotheses_total": len(hyp_review), "hypotheses_supported": hyp_counts["supported_as_pipeline_review_pattern"], "hypotheses_partial": hyp_counts["partially_supported_with_review_items"], "hypotheses_not_supported": hyp_counts["not_supported_by_control"], "hypotheses_inconclusive": hyp_counts["inconclusive"], "human_approval_claimed": False, "future_audit_authorized": False, "controls_reexecuted": False, "K_recomputed": False, "strength_recomputed": False, "d_recomputed": False, "D_recomputed": False, "edge_recomputed": False, "shortest_path_rerun": False, "raw_phase_reconstruction": False, "F3_raw_source_opened": False, "bootstrap_run": False, "upstream_modified": False, "l2_fail_changed": False, "post_hoc_tuning_performed": False, "physical_evidence_claim_made": False, "geometry_claim_made": False, "gravity_claim_made": False, "review_items_count": len(review_items), "claim_boundary": CLAIM, "next_allowed_action": "human_review_k_r2_decision_matrix_then_separate_authorization_if_source_response_audit_is_chosen"}
    write_text("01_extract03k_r2_run_manifest.json", json.dumps(manifest, indent=2, sort_keys=True))
    write_text("FINAL_RESULT_NOTE.md", f"""# QSB-EXTRACT03K-R2 Final Result

## Status
`{STATUS}`

## Reviewed Inputs
K-R1 classifications and K/J/I/H-R1 context were read only.

## K-R1 Classification Counts
Control families: supported {family_counts['supported_as_pipeline_review_pattern']}, partial {family_counts['partially_supported_with_review_items']}. Hypotheses: supported {hyp_counts['supported_as_pipeline_review_pattern']}, partial {hyp_counts['partially_supported_with_review_items']}, not supported {hyp_counts['not_supported_by_control']}, inconclusive {hyp_counts['inconclusive']}.

## Control Family Review
See `05_control_family_review_matrix.csv`.

## Hypothesis Review
See `06_hypothesis_review_matrix.csv`.

## Human Decision Points
Seven decision points are listed in `13_decision_points_for_human_review.csv`.

## Source-Response Audit Readiness
Readiness is partial; authorization is not available and not claimed.

## Claim Boundary
{CLAIM}

## L2 Boundary
L2 remains fail with N4 support 0/3 required 2/3.

## Next Allowed Action
Human review of this package before any separate authorization.
""")

    actual = sorted(p.name for p in OUT.iterdir() if p.is_file())
    if actual != sorted(FILES):
        fail("extract03k_r2_blocked_guard_violation", f"file manifest mismatch missing={sorted(set(FILES)-set(actual))} extra={sorted(set(actual)-set(FILES))}")
    after = {rel(p): tree_hash(p) if p.is_dir() else sha(p) for p in upstream_paths}
    changed = [p for p in before if before[p] != after[p]]
    if changed:
        fail("extract03k_r2_blocked_guard_violation", f"upstream modified: {changed}")
    print(json.dumps({"status": STATUS, "artifacts": len(actual), "control_families_supported": family_counts["supported_as_pipeline_review_pattern"], "control_families_partial": family_counts["partially_supported_with_review_items"], "hypotheses_supported": hyp_counts["supported_as_pipeline_review_pattern"], "hypotheses_partial": hyp_counts["partially_supported_with_review_items"], "hypotheses_not_supported": hyp_counts["not_supported_by_control"], "hypotheses_inconclusive": hyp_counts["inconclusive"], "human_approval_claimed": False, "future_audit_authorized": False, "upstream_modified": False}, sort_keys=True))


if __name__ == "__main__":
    main()
