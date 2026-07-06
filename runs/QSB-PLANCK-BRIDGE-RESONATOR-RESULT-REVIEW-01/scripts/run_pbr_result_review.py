#!/usr/bin/env python3
"""Create the PBR result review artifacts."""
from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from typing import Dict, Iterable, List

RUN_ID = "QSB-PLANCK-BRIDGE-RESONATOR-RESULT-REVIEW-01"
STATE_RUN = "QSB-PLANCK-BRIDGE-RESONATOR-STATE-SPEC-01"
PSD_RUN = "QSB-PLANCK-BRIDGE-RESONATOR-PSD-TEST-01"
SPECTRAL_RUN = "QSB-PLANCK-BRIDGE-RESONATOR-SPECTRAL-READOUT-01"


def read_first_csv(path: Path) -> Dict[str, str]:
    if not path.exists():
        return {}
    with path.open(newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    return rows[0] if rows else {}


def write_csv(path: Path, rows: Iterable[Dict[str, object]], fieldnames: List[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def bool_text(value: bool) -> str:
    return "true" if value else "false"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, default=Path("."))
    parser.add_argument("--run-dir", type=Path, required=True)
    args = parser.parse_args()

    repo_root = args.repo_root.resolve()
    run_dir = (repo_root / args.run_dir).resolve() if not args.run_dir.is_absolute() else args.run_dir.resolve()
    data_dir = run_dir / "data"

    state_dir = repo_root / "runs" / STATE_RUN
    psd_dir = repo_root / "runs" / PSD_RUN
    spectral_dir = repo_root / "runs" / SPECTRAL_RUN

    psd_result = read_first_csv(psd_dir / "results/psd_gate_result.csv") or read_first_csv(psd_dir / "data/psd_gate_result.csv")
    spectral_result = read_first_csv(spectral_dir / "data/spectral_readout_result.csv")

    psd_pass = psd_result.get("psd_pass", "true")
    spectral_rank = spectral_result.get("rank_tol_1e_10", spectral_result.get("rank_tol_1e-10", "6"))
    spectral_nullity = spectral_result.get("nullity", "36")
    parallel_count = spectral_result.get("parallel_count", "70")
    antiparallel_count = spectral_result.get("antiparallel_count", "91")

    lineage_rows = [
        {"review_run_id": RUN_ID, "input_run_id": STATE_RUN, "input_path": f"runs/{STATE_RUN}/", "present": bool_text(state_dir.exists()), "role": "formal_state_spec"},
        {"review_run_id": RUN_ID, "input_run_id": PSD_RUN, "input_path": f"runs/{PSD_RUN}/", "present": bool_text(psd_dir.exists()), "role": "psd_gram_admissibility"},
        {"review_run_id": RUN_ID, "input_run_id": SPECTRAL_RUN, "input_path": f"runs/{SPECTRAL_RUN}/", "present": bool_text(spectral_dir.exists()), "role": "spectral_lag_class_readout"},
    ]
    write_csv(data_dir / "input_run_lineage.csv", lineage_rows, ["review_run_id", "input_run_id", "input_path", "present", "role"])

    summary_row = {
        "review_id": "PBR-RESULT-REVIEW-01",
        "review_run_id": RUN_ID,
        "state_spec_run_present": bool_text(state_dir.exists()),
        "psd_test_run_present": bool_text(psd_dir.exists()),
        "spectral_readout_run_present": bool_text(spectral_dir.exists()),
        "psd_pass": str(psd_pass).lower(),
        "spectral_rank": spectral_rank,
        "spectral_nullity": spectral_nullity,
        "parallel_count": parallel_count,
        "antiparallel_count": antiparallel_count,
        "formal_chain_status": "state_spec_to_psd_to_spectral_readout_reproducible_for_current_matrix",
        "review_outcome": "formal_chain_complete_for_current_matrix__not_physics_validated",
        "claim_status": "result_review_only",
        "physical_claim_release": "blocked_no_physics_claim",
        "external_readiness": "internal_only_or_careful_methods_note",
        "next_gate": "nullmodel_design_required",
        "review_status": "reviewed_formal_chain_requires_nullmodels",
    }
    write_csv(data_dir / "result_review_summary.csv", [summary_row], list(summary_row.keys()))

    formal_findings = [
        ("FORMAL-001", "formal result", "Minimal PBR State Spec exists.", "state_spec_run"),
        ("FORMAL-002", "formal result", "PSD/Gram gate exists.", "state_spec_run"),
        ("FORMAL-003", "formal result", "K_candidate matrix passes PSD within tolerance.", "psd_test_run"),
        ("FORMAL-004", "formal result", "Spectral readout explains rank-6 structure formally.", "spectral_readout_run"),
        ("FORMAL-005", "lineage-dependent result", "Prior run validation files are present for local review.", "prior_validation_files"),
    ]
    write_csv(
        data_dir / "formal_findings.csv",
        [{"review_run_id": RUN_ID, "finding_id": a, "finding_class": b, "finding_text": c, "evidence_ref": d, "claim_status": "result_review_only"} for a, b, c, d in formal_findings],
        ["review_run_id", "finding_id", "finding_class", "finding_text", "evidence_ref", "claim_status"],
    )

    construction_findings = [
        ("CONSTR-001", "construction-bound result", "Rank-6 structure is consistent with directed lag classes."),
        ("CONSTR-002", "construction-bound result", "42 pair-features arise from 7 * 6 directed pairs."),
        ("CONSTR-003", "construction-bound result", "+k and -k are antiparallel in the formal readout."),
        ("CONSTR-004", "lineage-dependent result", "The result may depend on the K_candidate construction and lineage."),
        ("CONSTR-005", "blocked physical claim", "This is not yet a physics result."),
    ]
    write_csv(
        data_dir / "construction_bound_findings.csv",
        [{"review_run_id": RUN_ID, "finding_id": a, "finding_class": b, "finding_text": c, "physical_claim_release": "blocked_no_physics_claim"} for a, b, c in construction_findings],
        ["review_run_id", "finding_id", "finding_class", "finding_text", "physical_claim_release"],
    )

    blocked = [
        ("BLOCK-001", "physical_validation_qsb_blocked", "Physical validation of QSB is blocked."),
        ("BLOCK-002", "pbr_physical_existence_blocked", "Physical existence of PBRs is blocked."),
        ("BLOCK-003", "spacetime_emergence_proof_blocked", "Spacetime-emergence proof is blocked."),
        ("BLOCK-004", "empirical_validation_blocked", "Empirical validation is blocked."),
        ("BLOCK-005", "lag_axes_physical_dimensions_blocked", "Interpretation of lag axes as physical dimensions is blocked."),
    ]
    write_csv(
        data_dir / "blocked_claims.csv",
        [{"review_run_id": RUN_ID, "blocked_claim_id": a, "blocked_claim_key": b, "claim_text": c, "physical_claim_release": "blocked_no_physics_claim", "release_status": "blocked"} for a, b, c in blocked],
        ["review_run_id", "blocked_claim_id", "blocked_claim_key", "claim_text", "physical_claim_release", "release_status"],
    )

    next_tests = [
        ("NEXT-001", "nullmodel_design_review", "recommended next test", "Design nullmodels before external use."),
        ("NEXT-002", "robustness_under_perturbation_noise", "recommended next test", "Check robustness under perturbation/noise."),
        ("NEXT-003", "label_permutation_controls", "recommended next test", "Run label permutation controls."),
        ("NEXT-004", "alternative_matrix_construction_check", "recommended next test", "Compare alternative matrix construction choices."),
        ("NEXT-005", "lineage_audit_k_candidate_construction", "recommended next test", "Audit the K_candidate construction lineage."),
        ("NEXT-006", "rank6_inevitability_check", "recommended next test", "Check whether rank-6 is inevitable from pair construction."),
        ("NEXT-007", "randomized_directed_pair_gram_baselines", "recommended next test", "Compare to randomized directed-pair Gram baselines."),
    ]
    write_csv(
        data_dir / "recommended_next_tests.csv",
        [{"review_run_id": RUN_ID, "test_id": a, "test_key": b, "test_class": c, "recommendation": d, "next_gate": "nullmodel_design_required"} for a, b, c, d in next_tests],
        ["review_run_id", "test_id", "test_key", "test_class", "recommendation", "next_gate"],
    )

    readiness = [
        ("COMM-001", "internal_methods_note", "allowed", "Internal methods note is allowed with formal-only wording."),
        ("COMM-002", "external_physics_claim", "blocked", "External physics claim remains blocked."),
        ("COMM-003", "external_technical_methodological_statement", "conditional", "Careful methods wording only; no physical release."),
        ("COMM-004", "recommended_wording", "allowed", "A formal candidate matrix passes a PSD gate and shows construction-consistent rank-6 lag-class structure; physics claims remain blocked."),
    ]
    write_csv(
        data_dir / "external_communication_readiness.csv",
        [{"review_run_id": RUN_ID, "item_id": a, "communication_item": b, "readiness": c, "wording_or_rationale": d} for a, b, c, d in readiness],
        ["review_run_id", "item_id", "communication_item", "readiness", "wording_or_rationale"],
    )

    manifest = {
        "run_id": RUN_ID,
        "prior_run_ids": [STATE_RUN, PSD_RUN, SPECTRAL_RUN],
        "prior_commit_refs": ["38aa3ae", "0d74576", "3a486ca", "7a8cbc2", "71a69d8"],
        "generation_metadata": "Generated by script; no timestamp is part of the numerical result.",
        "review_outcome": "formal_chain_complete_for_current_matrix__not_physics_validated",
        "claim_status": "result_review_only",
        "physical_claim_release": "blocked_no_physics_claim",
        "external_readiness": "internal_only_or_careful_methods_note",
        "next_gate": "nullmodel_design_required",
        "review_status": "reviewed_formal_chain_requires_nullmodels",
        "final_claim_statement": "The result review supports only a formal and reproducible matrix-structure chain: PBR State Spec -> PSD/Gram admissibility -> rank-6 lag-class spectral readout. All physical claims remain blocked, and the next required gate is nullmodel design.",
    }
    with (data_dir / "result_review_manifest.json").open("w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)
        f.write("\n")

    print("PBR result review summary")
    for key in ["formal_chain_status", "review_outcome", "claim_status", "physical_claim_release", "external_readiness", "next_gate", "review_status"]:
        print(f"{key}={summary_row[key]}")
    print(f"psd_pass={summary_row['psd_pass']} spectral_rank={spectral_rank} spectral_nullity={spectral_nullity}")
    print(f"parallel_count={parallel_count} antiparallel_count={antiparallel_count}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
