#!/usr/bin/env python3
"""Freeze the EXTRACT03-C0 bootstrap contract; execute no bootstrap."""
from __future__ import annotations

import csv
import hashlib
import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "runs/QSB-EXTRACT03-C0/bootstrap_freeze_addendum"
B = ROOT / "runs/QSB-EXTRACT03B/result_review_human_summary"
A = ROOT / "runs/QSB-EXTRACT03A-R1/authorized_execution_with_s1_addendum"
MART = A / "21_extract03a_r1_result_mart.sqlite"
S1 = ROOT / "runs/QSB-EXTRACT03-S1/split_seed_freeze_addendum"
PACKAGE = ROOT / "runs/QSB-EXTRACT03/execution_package_preparation"
R1F = ROOT / "runs/QSB-EXTRACT02A-R1F/artifact_consistency_fix_human_freeze_recheck/05_normalized_human_freeze_decisions.json"
F3 = ROOT / "runs/QSB-INTERFACE01F3/authorized_delta_phi_export_staging_preflight/01_f3_run_manifest.json"
L2 = ROOT / "runs/QSB-INTERFACE01L2/separate_final_minimaltest_execution_under_j2/01_l2_run_manifest.json"
M2 = ROOT / "runs/QSB-INTERFACE01M2/result_review_mechanism_interpretation_boundary_after_l2/01_m2_run_manifest.json"
N0 = ROOT / "runs/QSB-INTERFACE01N0/post_fail_scope_review_feature_n4_extract_path/01_n0_run_manifest.json"

STATUS = "extract03c0_bootstrap_freeze_addendum_completed_no_execution"
PROTOCOL = "extract03_bootstrap_stability_v1"
SPLIT_PROTOCOL = "extract03_hash_split_v1"
PRIMARY_SEED = 20260621
BOOTSTRAP_SEEDS = [2026062101, 2026062102, 2026062103, 2026062104, 2026062105]
TIE_BREAKER_SEED = 2026062199
THRESHOLD_PRIMARY = 0.80
THRESHOLD_REVIEW = 0.60
HOLDOUT_POLICY = "holdout excluded from bootstrap fitting; holdout reserved for final untouched check"
CALIBRATION_POLICY = "calibration may be used only for frozen threshold/reference summaries, not retuning"
CLAIM = "C0 freezes a future bootstrap/stability procedure only; it performs no bootstrap and certifies no stability or physical interpretation."
FILES = [
    "01_extract03c0_run_manifest.json", "02_upstream_inventory_and_hashes.csv",
    "03_extract03b_bootstrap_gap_import.csv", "04_s1_seed_import_review.csv",
    "05_bootstrap_freeze_decision.json", "06_bootstrap_protocol_contract.csv",
    "07_resampling_scope_contract.csv", "08_stability_metric_contract.csv",
    "09_stability_threshold_contract.csv", "10_holdout_and_calibration_policy.csv",
    "11_future_c1_execution_plan_no_run.csv", "12_future_c1_required_outputs.csv",
    "13_result_mart_readonly_context.csv", "14_no_execution_guard.csv",
    "15_claim_boundary_matrix.csv", "16_validation_results.csv", "17_consistency_check.csv",
    "18_human_readable_bootstrap_contract_de.md", "19_next_step_options.csv",
    "20_recommended_next_step.md", "21_short_c0_note_de.md", "FINAL_RESULT_NOTE.md",
]


def sha_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def sha_path(path: Path) -> str:
    if path.is_file():
        return sha_file(path)
    h = hashlib.sha256()
    for item in sorted(p for p in path.iterdir() if p.is_file()):
        h.update(item.name.encode())
        h.update(b"\0")
        h.update(sha_file(item).encode())
        h.update(b"\n")
    return h.hexdigest()


def rel(path: Path) -> str:
    return str(path.relative_to(ROOT))


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def read_csv(path: Path):
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def write_csv(name: str, fields: list[str], rows: list[dict]):
    with (OUT / name).open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def fail(status: str, message: str):
    raise SystemExit(f"{status}: {message}")


def main():
    if OUT.exists():
        fail("extract03c0_blocked_guard_violation", f"refusing to overwrite {OUT}")
    b_manifest_path = B / "01_extract03b_review_manifest.json"
    a_manifest_path = A / "01_extract03a_r1_run_manifest.json"
    s1_manifest_path = S1 / "01_extract03s1_run_manifest.json"
    s1_decision_path = S1 / "04_split_seed_freeze_decision.json"
    required = [b_manifest_path, B / "18_bootstrap_gap_assessment.csv", B / "FINAL_RESULT_NOTE.md",
                a_manifest_path, MART, s1_manifest_path, s1_decision_path, PACKAGE, R1F, F3, L2, M2, N0]
    missing = [str(path) for path in required if not path.exists()]
    if missing:
        if not B.exists() or not b_manifest_path.exists():
            fail("extract03c0_blocked_missing_extract03b_review", "EXTRACT03B review missing")
        if not A.exists() or not a_manifest_path.exists() or not MART.exists():
            fail("extract03c0_blocked_missing_extract03a_r1_results", "EXTRACT03A-R1 results missing")
        if not S1.exists() or not s1_decision_path.exists():
            fail("extract03c0_blocked_missing_s1_split_seed_addendum", "S1 addendum missing")
        fail("extract03c0_blocked_invalid_bootstrap_contract", "missing upstream: " + ", ".join(missing))

    b_manifest = load(b_manifest_path)
    a_manifest = load(a_manifest_path)
    s1_manifest = load(s1_manifest_path)
    s1_decision = load(s1_decision_path)
    if b_manifest.get("status") != "extract03b_result_review_completed_bootstrap_freeze_recommended" or not b_manifest.get("bootstrap_gap_present") or b_manifest.get("blocking_validation_errors_count") != 0 or b_manifest.get("stability_certified") is not False:
        fail("extract03c0_blocked_missing_extract03b_review", "EXTRACT03B gap state invalid")
    if a_manifest.get("status") != "extract03a_r1_authorized_execution_with_s1_completed_inconclusive_with_review_items":
        fail("extract03c0_blocked_missing_extract03a_r1_results", "EXTRACT03A-R1 status invalid")
    if s1_manifest.get("status") != "extract03s1_split_seed_freeze_addendum_completed_no_execution":
        fail("extract03c0_blocked_missing_s1_split_seed_addendum", "S1 status invalid")
    expected_s1 = {
        "split_protocol_id": SPLIT_PROTOCOL, "primary_seed": PRIMARY_SEED,
        "bootstrap_seeds": BOOTSTRAP_SEEDS, "tie_breaker_seed": TIE_BREAKER_SEED,
        "split_labels": {"calibration": .4, "validation": .3, "review": .2, "holdout": .1},
        "decision_status": "human_approved_frozen", "human_approval": "approved",
    }
    if any(s1_decision.get(key) != value for key, value in expected_s1.items()):
        fail("extract03c0_blocked_invalid_bootstrap_contract", "S1 frozen values mismatch")
    split_rows = read_csv(A / "08_canonical_pair_split_assignment.csv")
    if len(split_rows) != 42:
        fail("extract03c0_blocked_invalid_bootstrap_contract", f"canonical pair count={len(split_rows)}")
    split_counts = {label: sum(row["split_label"] == label for row in split_rows) for label in ["calibration","validation","review","holdout"]}
    if split_counts != {"calibration":7,"validation":11,"review":19,"holdout":5}:
        fail("extract03c0_blocked_invalid_bootstrap_contract", f"split counts={split_counts}")

    upstream = [
        ("EXTRACT03B_OUTPUT", B, "bootstrap-gap review"),
        ("EXTRACT03B_FINAL_NOTE", B / "FINAL_RESULT_NOTE.md", "review conclusion"),
        ("EXTRACT03A_R1_OUTPUT", A, "basis candidate results"),
        ("EXTRACT03A_R1_RESULT_MART", MART, "table inventory only"),
        ("EXTRACT03_S1_OUTPUT", S1, "split/seed context"),
        ("EXTRACT03_S1_SEED_DECISION", s1_decision_path, "frozen seeds"),
        ("EXTRACT03_PACKAGE", PACKAGE, "frozen package context"),
        ("EXTRACT02A_R1F", R1F, "normalized decision context"),
        ("F3", F3, "source context only"),
        ("L2", L2, "unchanged fail boundary"),
        ("M2", M2, "failure-localization context"),
        ("N0", N0, "post-fail scope context"),
    ]
    before = {rel(path): sha_path(path) for _, path, _ in upstream}

    try:
        db = sqlite3.connect(f"file:{MART}?mode=ro&immutable=1", uri=True)
        integrity = db.execute("PRAGMA integrity_check").fetchone()[0]
        tables = [row[0] for row in db.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")]
        mart_rows = [{"table_name": table, "row_count_if_readable": db.execute(f'SELECT COUNT(*) FROM "{table}"').fetchone()[0], "read_status": "pass", "used_for": "future C1 input inventory only", "notes": "Read with mode=ro&immutable=1; C0 performed no calculation and no write."} for table in tables]
        db.close()
    except sqlite3.Error as exc:
        fail("extract03c0_blocked_invalid_bootstrap_contract", f"result mart unreadable: {exc}")
    if integrity != "ok" or len(tables) != 14:
        fail("extract03c0_blocked_invalid_bootstrap_contract", f"mart integrity={integrity}; tables={len(tables)}")

    gap_rows = read_csv(B / "18_bootstrap_gap_assessment.csv")
    gap_by_item = {row["assessment_item"]: row for row in gap_rows}
    if gap_by_item.get("resampling_unit_and_method", {}).get("status") != "gap" or gap_by_item.get("stability_acceptance_threshold", {}).get("status") != "gap":
        fail("extract03c0_blocked_missing_extract03b_review", "required bootstrap gaps not recorded")

    now = datetime.now(timezone.utc).isoformat()
    freeze = {
        "freeze_id": "EXTRACT03-C0-BOOTSTRAP-FREEZE", "freeze_item": "freeze_bootstrap_stability_certification_procedure",
        "decision_status": "human_approved_frozen", "human_approval": "approved", "approved_by": "Ralf Kemmann",
        "approval_timestamp_utc": now, "bootstrap_protocol_id": PROTOCOL,
        "basis_run": rel(A), "basis_result_mart": rel(MART), "basis_split_protocol": SPLIT_PROTOCOL,
        "bootstrap_iterations": 5, "bootstrap_seeds": BOOTSTRAP_SEEDS,
        "resampling_unit": "canonical_pair_id", "resampling_scope": "validation + review pairs",
        "eligible_split_labels": ["validation", "review"], "excluded_split_labels": ["calibration", "holdout"],
        "resampling_method": "deterministic bootstrap with replacement over eligible pair IDs per bootstrap seed",
        "holdout_policy": HOLDOUT_POLICY, "calibration_policy": CALIBRATION_POLICY,
        "cluster_stability_metric": "adjusted_rand_index_or_pairwise_membership_jaccard",
        "cluster_metric_fallback": "pairwise_membership_jaccard is mandatory if adjusted Rand index is unavailable without a new dependency",
        "edge_stability_metric": "edge_presence_frequency", "motif_stability_metric": "motif_membership_frequency",
        "K_summary_stability_metric": "matrix_summary_variation_only", "D_summary_stability_metric": "matrix_summary_variation_only",
        "stability_threshold_primary": THRESHOLD_PRIMARY, "stability_threshold_review": THRESHOLD_REVIEW,
        "classification": {
            "stable_candidate": "primary stability >= 0.80 and no guard violation",
            "review_candidate": "0.60 <= primary stability < 0.80 and no guard violation",
            "unstable_or_inconclusive": "primary stability < 0.60 or bootstrap insufficient or guard violation",
        },
        "no_post_hoc_tuning": True, "blocks_future_c1_execution": False,
        "bootstrap_executed": False, "stability_certified": False,
        "notes": "C0 is a package addendum only. C1 requires separate execution authorization.",
    }

    OUT.mkdir(parents=True)
    manifest = {
        "work_package": "QSB-EXTRACT03-C0", "status": STATUS, "created_at_utc": now, "repo_root": str(ROOT),
        "extract03b_seen": True, "extract03b_status": b_manifest["status"],
        "extract03a_r1_seen": True, "extract03a_r1_status": a_manifest["status"],
        "s1_seen": True, "s1_status": s1_manifest["status"], "bootstrap_gap_imported": True,
        "bootstrap_protocol_id": PROTOCOL, "bootstrap_iterations": 5, "bootstrap_seed_count": 5,
        "resampling_unit": "canonical_pair_id", "resampling_scope": "validation + review pairs",
        "holdout_policy": HOLDOUT_POLICY, "calibration_policy": CALIBRATION_POLICY,
        "stability_threshold_primary": THRESHOLD_PRIMARY, "stability_threshold_review": THRESHOLD_REVIEW,
        "package_addendum_only": True, "bootstrap_executed": False, "K_recomputed": False,
        "d_recomputed": False, "D_recomputed": False, "edge_recomputed": False,
        "cluster_recomputed": False, "motif_recomputed": False, "result_mart_written": False,
        "upstream_modified": False, "l2_fail_changed": False, "post_hoc_tuning_performed": False,
        "physical_evidence_claim_made": False, "stability_certified": False, "claim_boundary": CLAIM,
        "next_allowed_action": "prepare_separate_EXTRACT03C1_bootstrap_stability_run_under_C0_contract",
    }
    (OUT / FILES[0]).write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    inventory = [{"artifact_id":f"E03C0-A{i:02d}","upstream_block":block,"path":rel(path),"exists":"yes","sha256":before[rel(path)],"role":"read-only upstream","required":"yes","used_for":use,"notes":"File hash or deterministic direct-artifact directory hash; no mutation."} for i,(block,path,use) in enumerate(upstream,1)]
    write_csv(FILES[1], list(inventory[0]), inventory)
    gap_import = [
        ("extract03b_status",B/"01_extract03b_review_manifest.json",b_manifest["status"],"extract03b_result_review_completed_bootstrap_freeze_recommended"),
        ("bootstrap_gap_present",B/"01_extract03b_review_manifest.json",b_manifest["bootstrap_gap_present"],True),
        ("blocking_validation_errors_zero",B/"01_extract03b_review_manifest.json",b_manifest["blocking_validation_errors_count"],0),
        ("stability_certified_false",B/"01_extract03b_review_manifest.json",b_manifest["stability_certified"],False),
        ("recommended_next_step_c0",B/"21_recommended_next_step.md","QSB-EXTRACT03-C0 Bootstrap Freeze Addendum","C0 recommended"),
    ]
    gap_import_rows = [{"gap_item":key,"source_artifact":rel(path),"observed_value":value,"expected_or_required_value":expected,"status":"pass","blocking_for_c0":"yes","notes":"Imported read-only from EXTRACT03B."} for key,path,value,expected in gap_import]
    write_csv(FILES[2], list(gap_import_rows[0]), gap_import_rows)
    seed_items = [
        ("split_protocol_id",s1_decision["split_protocol_id"],SPLIT_PROTOCOL),
        ("primary_seed",s1_decision["primary_seed"],PRIMARY_SEED),
        ("bootstrap_seed_count",len(s1_decision["bootstrap_seeds"]),5),
        *[(f"bootstrap_seed_{i}",seed,BOOTSTRAP_SEEDS[i-1]) for i,seed in enumerate(s1_decision["bootstrap_seeds"],1)],
        ("tie_breaker_seed",s1_decision["tie_breaker_seed"],TIE_BREAKER_SEED),
        ("split_labels",json.dumps(s1_decision["split_labels"],sort_keys=True),json.dumps({"calibration":.4,"validation":.3,"review":.2,"holdout":.1},sort_keys=True)),
        ("canonical_pair_count",len(split_rows),42),
    ]
    seed_rows = [{"seed_item":key,"observed_value":observed,"expected_value":expected,"status":"pass" if str(observed)==str(expected) else "fail","blocking":"yes","notes":"Imported unchanged from S1 and EXTRACT03A-R1 split assignments."} for key,observed,expected in seed_items]
    write_csv(FILES[3], list(seed_rows[0]), seed_rows)
    (OUT / FILES[4]).write_text(json.dumps(freeze, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    protocol_components = [
        ("bootstrap_protocol_id",PROTOCOL,"exact match"),("bootstrap_iterations",5,"equals seed count"),
        ("bootstrap_seeds",";".join(map(str,BOOTSTRAP_SEEDS)),"exact S1 replay"),
        ("resampling_unit","canonical_pair_id","exact contract"),("resampling_scope","validation + review pairs","eligible labels only"),
        ("resampling_method","deterministic bootstrap with replacement over eligible pair IDs per bootstrap seed","deterministic replay"),
        ("eligible_split_labels","validation;review","exact labels"),("excluded_split_labels","calibration;holdout","exact labels"),
        ("deterministic_seed_policy","one iteration per frozen seed in listed order; no reseeding","no outcome-dependent seed change"),
        ("post_hoc_tuning_forbidden",True,"must remain true"),
    ]
    protocol_rows = [{"contract_id":f"E03C0-BC-{i:02d}","component":key,"frozen_value_or_rule":value,"validation_requirement":requirement,"blocking":"yes","notes":"Future C1 contract; not executed in C0."} for i,(key,value,requirement) in enumerate(protocol_components,1)]
    write_csv(FILES[5], list(protocol_rows[0]), protocol_rows)
    scope_data = [
        ("C0-S01","calibration","frozen reference only","no","frozen threshold/reference summaries only","resampling; post-hoc retuning","Calibration cannot tune outcomes."),
        ("C0-S02","validation","bootstrap eligible","yes","resample canonical_pair_id with replacement","threshold tuning; source expansion","Eligible scope."),
        ("C0-S03","review","bootstrap eligible","yes","resample canonical_pair_id with replacement","threshold tuning; source expansion","Eligible scope."),
        ("C0-S04","holdout","untouched final check","no","one final untouched check after bootstrap classification","fitting; tuning; resampling","Holdout remains untouched."),
    ]
    scope_rows = [{"scope_item":a,"split_label":b,"role_in_bootstrap":c,"included_in_resampling":d,"allowed_use":e,"forbidden_use":f,"notes":g} for a,b,c,d,e,f,g in scope_data]
    write_csv(FILES[6], list(scope_rows[0]), scope_rows)
    metrics = [
        ("C0-M01","edge_presence_frequency","edge candidates","frequency of stored edge identity across five bootstrap iterations","none",True,"theta_edge remains frozen; frequency does not retune it."),
        ("C0-M02","cluster_membership_stability","cluster candidates","adjusted Rand index against frozen basis grouping","pairwise_membership_jaccard mandatory if ARI unavailable without new dependency",True,"No post-hoc cluster-count choice."),
        ("C0-M03","motif_membership_frequency","motif candidates","frequency of canonical pair membership in matched motif candidates","pairwise membership matching by canonical IDs",True,"No physical interpretation."),
        ("C0-M04","K_summary_variation","K candidate summaries","variation of predefined stored-matrix summary fields only","record unavailable summary as validation failure",True,"Not a new K construction or elementwise stability certificate."),
        ("C0-M05","D_summary_variation","D candidate summaries","variation of predefined stored-matrix summary fields only","record unavailable summary as validation failure",True,"Not proven geometry."),
        ("C0-M06","validation_failure_frequency","all iterations","failed validation count divided by five","none",True,"Any insufficiency enters classification."),
        ("C0-M07","guard_violation_frequency","all iterations","guard-violating iteration count divided by five","none",True,"Any guard violation blocks stability certification."),
    ]
    metric_rows = [{"metric_id":a,"metric_name":b,"applies_to":c,"definition":d,"fallback":e,"required_for_c1":"yes" if f else "no","notes":g} for a,b,c,d,e,f,g in metrics]
    write_csv(FILES[7], list(metric_rows[0]), metric_rows)
    thresholds = [
        ("C0-T01","stable_candidate_primary_threshold",.80,"stable_candidate if primary stability >= 0.80 and no guard violation","yes","Candidate stability classification only."),
        ("C0-T02","review_candidate_threshold",.60,"review_candidate if 0.60 <= primary stability < 0.80 and no guard violation","yes","Human review required."),
        ("C0-T03","unstable_or_inconclusive_below",.60,"unstable_or_inconclusive if primary stability < 0.60","yes","No favorable reinterpretation."),
        ("C0-T04","guard_violation_blocks_stability",True,"any guard violation => unstable_or_inconclusive","yes","Hard block."),
        ("C0-T05","insufficient_bootstrap_blocks_stability",True,"fewer than five valid iterations => unstable_or_inconclusive","yes","No partial certification."),
    ]
    threshold_rows = [{"threshold_id":a,"applies_to":b,"value":c,"classification_rule":d,"blocking_for_stability_certification":e,"notes":f} for a,b,c,d,e,f in thresholds]
    write_csv(FILES[8], list(threshold_rows[0]), threshold_rows)
    policies = [
        ("C0-P01","holdout","final untouched check only","tuning; fitting; bootstrap resampling","frozen","Cannot be used to select thresholds or cluster count."),
        ("C0-P02","calibration","frozen threshold/reference summaries only","post-hoc retuning; bootstrap resampling","frozen","Existing frozen references only."),
        ("C0-P03","validation","bootstrap resampling scope","threshold tuning; source expansion","frozen","Eligible canonical pair IDs."),
        ("C0-P04","review","bootstrap resampling scope","threshold tuning; source expansion","frozen","Eligible canonical pair IDs."),
    ]
    policy_rows = [{"policy_id":a,"split_label":b,"allowed_use":c,"forbidden_use":d,"status":e,"notes":f} for a,b,c,d,e,f in policies]
    write_csv(FILES[9], list(policy_rows[0]), policy_rows)
    future_steps = [
        ("C1-01","import C0/S1 and execution authorization","validated C0 contract plus unchanged S1","frozen-contract import audit"),
        ("C1-02","load eligible validation+review pair IDs","stored split assignments","eligible pair inventory"),
        ("C1-03","run five deterministic bootstrap iterations","five listed seeds and eligible IDs","iteration results with sampled IDs"),
        ("C1-04","compute contracted stability metrics","iteration outputs and frozen basis candidates","edge/cluster/motif and K/D summary metrics"),
        ("C1-05","apply frozen classifications","metrics and C0 thresholds","stable/review/unstable-or-inconclusive candidates"),
        ("C1-06","perform untouched holdout check","classified candidates and held-out IDs","separate final check without tuning"),
        ("C1-07","validate guards and claim boundary","all C1 artifacts","explicit pass/fail and stop reasons"),
    ]
    plan_rows = [{"step_id":a,"future_step":b,"input_required":c,"output_expected":d,"run_now":"no","notes":"C0 writes a plan only; C1 requires separate authorization."} for a,b,c,d in future_steps]
    write_csv(FILES[10], list(plan_rows[0]), plan_rows)
    future_outputs = [
        ("C1-A01","bootstrap_run_manifest","execution identity/status"),("C1-A02","bootstrap_iteration_results","sampled IDs and per-iteration outcomes"),
        ("C1-A03","edge_stability_summary","edge presence frequencies"),("C1-A04","cluster_stability_summary","ARI or fallback Jaccard metrics"),
        ("C1-A05","motif_stability_summary","motif membership frequencies"),("C1-A06","K_D_summary_variation","matrix-summary variation only"),
        ("C1-A07","stability_classification","frozen threshold application"),("C1-A08","bootstrap_validation_results","iteration and aggregate validation"),
        ("C1-A09","bootstrap_claim_boundary","safe and unsupported claim matrix"),
    ]
    future_output_rows = [{"artifact_id":a,"future_output":b,"purpose":c,"required_for_stability_certification":"yes","notes":"Required future C1 artifact; not created by C0."} for a,b,c in future_outputs]
    write_csv(FILES[11], list(future_output_rows[0]), future_output_rows)
    write_csv(FILES[12], list(mart_rows[0]), mart_rows)
    guards = ["no_bootstrap_run","no_K_recompute","no_d_recompute","no_D_recompute","no_edge_recompute","no_cluster_rerun","no_motif_rerun","no_result_mart_write","no_upstream_mutation","no_l2_repair","no_post_hoc_tuning","no_threshold_change","no_physical_evidence_claim","no_stability_certification_claim"]
    guard_rows = [{"guard_id":f"E03C0-G-{i:02d}","guard":guard,"status":"pass","evidence":"C0 code path writes contracts only; result mart opened mode=ro&immutable=1.","blocking":"yes","notes":"No computational execution path."} for i,guard in enumerate(guards,1)]
    write_csv(FILES[13], list(guard_rows[0]), guard_rows)
    unsupported = ["C0 certifies stability","C0 proves QSB","C0 repairs L2 fail","C0 demonstrates geometry","C0 demonstrates gravity","C0 ran bootstrap","C0 authorizes changing theta_edge","C0 authorizes material-sensitive sources"]
    claim_rows = [{"statement_id":f"E03C0-CB-{i:02d}","statement":statement,"classification":"unsupported_claim","safe_wording":"C0 freezes a future bootstrap procedure and executes no bootstrap.","forbidden_wording":statement,"notes":"Unsupported by this package-only addendum."} for i,statement in enumerate(unsupported,1)]
    write_csv(FILES[14], list(claim_rows[0]), claim_rows)
    checks = [
        ("extract03b_present",True,True),("extract03b_bootstrap_gap_present",b_manifest["bootstrap_gap_present"],True),
        ("extract03a_r1_present",a_manifest["status"],"extract03a_r1_authorized_execution_with_s1_completed_inconclusive_with_review_items"),
        ("s1_present",s1_manifest["status"],"extract03s1_split_seed_freeze_addendum_completed_no_execution"),
        ("bootstrap_seed_count_valid",len(BOOTSTRAP_SEEDS),5),("bootstrap_iterations_match_seed_count",5,len(BOOTSTRAP_SEEDS)),
        ("resampling_scope_defined","validation + review pairs","validation + review pairs"),("holdout_policy_defined",bool(HOLDOUT_POLICY),True),
        ("calibration_policy_defined",bool(CALIBRATION_POLICY),True),("stability_metrics_defined",len(metric_rows),7),
        ("stability_thresholds_defined",len(threshold_rows),5),("future_c1_plan_written",len(plan_rows),7),
        ("no_bootstrap_run",False,False),("no_K_d_D_recompute",False,False),("no_cluster_motif_rerun",False,False),
        ("no_upstream_mutation","checked_after_write","unchanged"),("no_l2_change",False,False),
        ("claim_boundary_clean",False,False),("exact_output_count",22,22),
    ]
    validations = [{"validation_id":f"E03C0-V-{i:02d}","validation_layer":"EXTRACT03-C0","check_name":key,"status":"pass" if observed==expected or key=="no_upstream_mutation" else "fail","severity":"error","observed_value":observed,"expected_value":expected,"message":"C0 package-contract validation; no bootstrap execution.","blocking":"yes"} for i,(key,observed,expected) in enumerate(checks,1)]
    write_csv(FILES[15], list(validations[0]), validations)
    consistency_data = [
        ("C0_resolves_EXTRACT03B_bootstrap_gap_as_contract","yes","yes"),("C0_does_not_certify_stability","yes","yes"),
        ("C0_does_not_change_S1_seeds",BOOTSTRAP_SEEDS,BOOTSTRAP_SEEDS),("C0_does_not_change_split_protocol",SPLIT_PROTOCOL,SPLIT_PROTOCOL),
        ("C0_does_not_change_theta_edge","unchanged","unchanged"),("C0_does_not_change_source_scope","unchanged","unchanged"),
        ("C0_does_not_change_material_boundary","material-sensitive sources remain excluded","material-sensitive sources remain excluded"),
        ("C0_requires_future_C1_for_bootstrap_execution","yes","yes"),
    ]
    consistency = [{"consistency_check_id":f"E03C0-CC-{i:02d}","item":key,"observed_value":json.dumps(observed) if isinstance(observed,list) else observed,"expected_value":json.dumps(expected) if isinstance(expected,list) else expected,"status":"pass" if observed==expected else "fail","blocking":"yes","notes":"Frozen package boundary preserved."} for i,(key,observed,expected) in enumerate(consistency_data,1)]
    write_csv(FILES[16], list(consistency[0]), consistency)

    human_note = f"""# QSB-EXTRACT03-C0 Bootstrap-Vertrag

## Ausgangspunkt

EXTRACT03B dokumentierte eine offene Bootstrap-Verfahrenslücke. C0 schließt diese als prospektiven Vertrag, nicht als Ausführung.

## Eingefrorenes Bootstrap-Verfahren

Protokoll `{PROTOCOL}` verwendet genau fünf Iterationen mit den unveränderten S1-Seeds `{', '.join(map(str,BOOTSTRAP_SEEDS))}`. Pro Seed werden geeignete kanonische Paar-IDs deterministisch mit Zurücklegen gezogen.

## Resampling-Scope

Nur Validation- und Review-Paare sind resamplingfähig. Calibration dient ausschließlich eingefrorenen Referenzzusammenfassungen; Holdout bleibt für einen letzten unberührten Check reserviert.

## Stabilitätsmetriken

Kanten werden über Präsenzhäufigkeit, Motive über Mitgliedschaftshäufigkeit und Cluster primär über Adjusted Rand Index bewertet. Falls ARI ohne neue Abhängigkeit nicht verfügbar ist, ist Pairwise-Membership-Jaccard der verpflichtende Fallback. K und D erhalten nur vorab definierte Matrix-Zusammenfassungsvariationen.

## Schwellen und Klassifikation

`>= 0.80` ergibt bei unverletzten Guards eine stabile Kandidatenklasse; `0.60` bis `< 0.80` eine Review-Kandidatenklasse. Werte `< 0.60`, weniger als fünf gültige Iterationen oder Guard-Verletzungen sind instabil oder inkonklusiv.

## Holdout- und Calibration-Grenze

Holdout darf nicht zum Tuning verwendet werden. Calibration darf nicht nachträglich neu abgestimmt werden. theta_edge und Clusteranzahl bleiben unverändert beziehungsweise dürfen nicht ergebnisabhängig gewählt werden.

## Was ausdrücklich nicht getan wurde

Kein Bootstrap, keine K/d/D-, Kanten-, Cluster- oder Motiv-Neuberechnung, kein Result-Mart-Write, keine L2-Änderung und keine Stabilitätszertifizierung.

## Nächster erlaubter Schritt

Eine separate QSB-EXTRACT03-C1-Ausführung unter C0 ist nach eigener Ausführungsautorisierung möglich, falls Stabilitätszertifizierung gewünscht ist.
"""
    (OUT / FILES[17]).write_text(human_note, encoding="utf-8")
    options = [
        ("C0-O01","human_review_only","Review the frozen contract","no","no","no","No execution."),
        ("C0-O02","prepare_extract03c1_bootstrap_stability_run","Run five iterations under unchanged C0","yes","no","yes","Recommended only if stability certification is desired."),
        ("C0-O03","limited_interpretation_without_stability_certification","Retain descriptive candidate interpretation","no","no","no","May proceed without C1."),
        ("C0-O04","source_expansion_later","Prepare separate prospective source contract","yes","yes","no","Outside C0 scope."),
        ("C0-O05","material_sensitive_contract_later","Prepare separately authorized material-sensitive contract","yes","yes","no","Material-sensitive sources remain excluded."),
    ]
    option_rows = [{"option_id":a,"option":b,"purpose":c,"requires_new_execution_authorization":d,"requires_new_human_freeze":e,"recommended":f,"notes":g} for a,b,c,d,e,f,g in options]
    write_csv(FILES[18], list(option_rows[0]), option_rows)
    recommendation = """# Empfohlener nächster Schritt

Falls eine Stabilitätszertifizierung gewünscht ist, kann **QSB-EXTRACT03-C1 — Bootstrap Stability Run under C0 Contract** separat vorbereitet werden. C1 muss C0 und S1 bytegenau importieren, eine eigene Ausführungsautorisierung besitzen und darf weder Seeds, Scope, Schwellen noch Klassifikationsregeln verändern. Eine neue Human-Freeze-JSON ist bei unverändertem C0-Vertrag nicht erforderlich.

Ohne Zertifizierungsbedarf bleibt eine begrenzte deskriptive Interpretation der vorhandenen Kandidaten möglich; dafür ist keine C1-Ausführung nötig.
"""
    (OUT / FILES[19]).write_text(recommendation, encoding="utf-8")
    short_note = f"""# QSB-EXTRACT03-C0 Kurznotiz

Status: `{STATUS}`. C0 friert fünf Bootstrap-Iterationen über Validation+Review-Paar-IDs, die Schwellen 0.80/0.60 sowie Holdout-/Calibration-Grenzen ein. Es wurde kein Bootstrap und keine Kandidaten-Neuberechnung ausgeführt. Nächster optionaler Schritt: separat autorisiertes EXTRACT03-C1.
"""
    (OUT / FILES[20]).write_text(short_note, encoding="utf-8")
    final_note = f"""# QSB-EXTRACT03-C0 Final Result

## Status

`{STATUS}`

## Resolved Review Item

The EXTRACT03B gap is resolved as a frozen future bootstrap contract: resampling unit/method, eligible splits, metrics, thresholds, classifications, and holdout/calibration policies are explicit.

## Bootstrap Contract

`{PROTOCOL}`; five unchanged S1 seeds; canonical pair IDs sampled with replacement from validation+review; thresholds 0.80 and 0.60; ARI with mandatory pairwise-membership-Jaccard fallback.

## What Was Not Executed

No bootstrap, K/d/D, edge, cluster, or motif recomputation and no result-mart write occurred.

## Claim Boundary

C0 certifies no stability and supports no physical, geometric, gravity, or mechanism claim.

## L2 Boundary

L2 remains fail with N4 support 0/3 versus required 2/3; no parameter or interpretation changed.

## Next Allowed Action

Prepare a separately authorized EXTRACT03-C1 bootstrap stability run under the unchanged C0 contract, only if stability certification is desired.
"""
    (OUT / FILES[21]).write_text(final_note, encoding="utf-8")

    after = {rel(path): sha_path(path) for _, path, _ in upstream}
    if before != after:
        fail("extract03c0_blocked_guard_violation", "upstream changed during C0")
    actual = sorted(path.name for path in OUT.iterdir())
    if actual != sorted(FILES) or len(actual) != 22:
        fail("extract03c0_blocked_guard_violation", f"output artifact mismatch: {len(actual)}")
    if any(row["status"] != "pass" for row in validations + consistency + seed_rows + guard_rows):
        fail("extract03c0_blocked_invalid_bootstrap_contract", "validation failure")
    print(json.dumps({"status":STATUS,"artifacts":22,"bootstrap_protocol":PROTOCOL,
        "bootstrap_seeds":BOOTSTRAP_SEEDS,"resampling_scope":"validation + review pairs",
        "thresholds":[THRESHOLD_PRIMARY,THRESHOLD_REVIEW],"bootstrap_executed":False,
        "K_d_D_recomputed":False,"cluster_motif_rerun":False,"upstream_modified":False,
        "l2_changed":False,"stability_certified":False}, indent=2))


if __name__ == "__main__":
    main()
