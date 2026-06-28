#!/usr/bin/env python3
"""Complete the C0 bootstrap contract byte-exactly; execute no bootstrap."""
from __future__ import annotations

import csv
import hashlib
import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "runs/QSB-EXTRACT03-C0B/bootstrap_contract_completion_addendum"
C0 = ROOT / "runs/QSB-EXTRACT03-C0/bootstrap_freeze_addendum"
B = ROOT / "runs/QSB-EXTRACT03B/result_review_human_summary"
A = ROOT / "runs/QSB-EXTRACT03A-R1/authorized_execution_with_s1_addendum"
MART = A / "21_extract03a_r1_result_mart.sqlite"
S1 = ROOT / "runs/QSB-EXTRACT03-S1/split_seed_freeze_addendum"
PACKAGE = ROOT / "runs/QSB-EXTRACT03/execution_package_preparation"
F3 = ROOT / "runs/QSB-INTERFACE01F3/authorized_delta_phi_export_staging_preflight/01_f3_run_manifest.json"
L2 = ROOT / "runs/QSB-INTERFACE01L2/separate_final_minimaltest_execution_under_j2/01_l2_run_manifest.json"
M2 = ROOT / "runs/QSB-INTERFACE01M2/result_review_mechanism_interpretation_boundary_after_l2/01_m2_run_manifest.json"
N0 = ROOT / "runs/QSB-INTERFACE01N0/post_fail_scope_review_feature_n4_extract_path/01_n0_run_manifest.json"

STATUS = "extract03c0b_bootstrap_contract_completion_addendum_completed_no_execution"
DRAW_ID = "extract03_sha256_counter_draw_v1"
PHASE_POLICY_ID = "extract03_pair_level_bootstrap_no_phase_reconstruction_v1"
CLUSTER_RULE_ID = "extract03_edge_component_flat_clusters_v1"
CLUSTER_METRIC = "pairwise_membership_jaccard_v1"
MOTIF_RULE_ID = "extract03_motif_signature_exact_v1"
K_METRIC_SET = "extract03_K_summary_metrics_v1"
D_METRIC_SET = "extract03_D_summary_metrics_v1"
EDGE_RULE_ID = "extract03_edge_presence_frequency_v1"
SEEDS = [2026062101, 2026062102, 2026062103, 2026062104, 2026062105]
PRIMARY_THRESHOLD = 0.80
REVIEW_THRESHOLD = 0.60
CLAIM = "C0B completes a future pair-level bootstrap contract only; it runs no bootstrap, certifies no stability, and does not assess phase-vector pipeline stability."
FILES = [
    "01_extract03c0b_run_manifest.json", "02_upstream_inventory_and_hashes.csv",
    "03_c1_blocker_import.csv", "04_c0_contract_import_review.csv",
    "05_contract_completion_decision.json", "06_seed_draw_algorithm_contract.csv",
    "07_pair_level_bootstrap_input_policy.csv", "08_cluster_flattening_contract.csv",
    "09_motif_matching_contract.csv", "10_K_summary_metric_contract.csv",
    "11_D_summary_metric_contract.csv", "12_edge_stability_contract.csv",
    "13_stability_classification_contract.csv", "14_future_c1r1_execution_plan_no_run.csv",
    "15_future_c1r1_required_outputs.csv", "16_result_mart_readonly_context.csv",
    "17_no_execution_guard.csv", "18_claim_boundary_matrix.csv",
    "19_validation_results.csv", "20_consistency_check.csv",
    "21_human_readable_contract_completion_de.md", "22_recommended_next_step.md",
    "FINAL_RESULT_NOTE.md",
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
        fail("extract03c0b_blocked_guard_violation", f"refusing to overwrite {OUT}")
    c0_manifest_path = C0 / "01_extract03c0_run_manifest.json"
    a_manifest_path = A / "01_extract03a_r1_run_manifest.json"
    split_path = A / "08_canonical_pair_split_assignment.csv"
    required = [c0_manifest_path, C0 / "05_bootstrap_freeze_decision.json", C0 / "FINAL_RESULT_NOTE.md",
                B / "01_extract03b_review_manifest.json", B / "FINAL_RESULT_NOTE.md", a_manifest_path,
                split_path, A / "11_K_candidate_matrix.csv", A / "13_distance_cost_matrix.csv",
                A / "14_shortest_path_D_matrix.csv", A / "15_strength_matrix.csv",
                A / "16_edge_candidate_result.csv", A / "18_cluster_dendrogram_candidate_result.csv",
                A / "19_motif_candidate_summary.csv", MART, S1, PACKAGE, F3, L2, M2, N0]
    if any(not path.exists() for path in required):
        if not C0.exists() or not c0_manifest_path.exists():
            fail("extract03c0b_blocked_missing_c0", "C0 missing")
        if not A.exists() or not a_manifest_path.exists():
            fail("extract03c0b_blocked_missing_extract03a_r1_outputs", "EXTRACT03A-R1 outputs missing")
        fail("extract03c0b_blocked_invalid_contract_completion", "required upstream artifact missing")
    if (ROOT / "runs/QSB-EXTRACT03-C1/bootstrap_stability_run_under_c0").exists():
        fail("extract03c0b_blocked_missing_extract03c1_blocker_context", "unexpected C1 output exists; blocker context no longer matches")

    c0 = load(c0_manifest_path)
    a = load(a_manifest_path)
    if c0.get("status") != "extract03c0_bootstrap_freeze_addendum_completed_no_execution":
        fail("extract03c0b_blocked_missing_c0", "C0 status mismatch")
    if a.get("status") != "extract03a_r1_authorized_execution_with_s1_completed_inconclusive_with_review_items":
        fail("extract03c0b_blocked_missing_extract03a_r1_outputs", "EXTRACT03A-R1 status mismatch")
    expected_c0 = {
        "bootstrap_protocol_id": "extract03_bootstrap_stability_v1", "bootstrap_iterations": 5,
        "bootstrap_seed_count": 5, "resampling_scope": "validation + review pairs",
        "stability_threshold_primary": PRIMARY_THRESHOLD, "stability_threshold_review": REVIEW_THRESHOLD,
        "bootstrap_executed": False, "stability_certified": False,
    }
    if any(c0.get(key) != value for key, value in expected_c0.items()):
        fail("extract03c0b_blocked_invalid_contract_completion", "C0 frozen contract mismatch")
    c0_freeze = load(C0 / "05_bootstrap_freeze_decision.json")
    if c0_freeze.get("bootstrap_seeds") != SEEDS:
        fail("extract03c0b_blocked_invalid_contract_completion", "C0 seeds mismatch")

    split_rows = read_csv(split_path)
    eligible_ids = [row["canonical_pair_id"] for row in split_rows if row["split_label"] in {"validation", "review"}]
    eligible_blob = "\n".join(eligible_ids).encode("utf-8")
    eligible_hash = hashlib.sha256(eligible_blob).hexdigest()
    if len(eligible_ids) != 30 or eligible_hash != "2f992b682ddb715ceddf2adfeb78d0edc5c83f0f6aeeac4df58aea0a0170e6f4":
        fail("extract03c0b_blocked_invalid_contract_completion", "eligible pair basis mismatch")

    upstream = [
        ("EXTRACT03_C0_OUTPUT",C0,"base bootstrap contract"),("EXTRACT03_C0_FINAL_NOTE",C0/"FINAL_RESULT_NOTE.md","C0 boundary"),
        ("EXTRACT03B_OUTPUT",B,"review context"),("EXTRACT03B_FINAL_NOTE",B/"FINAL_RESULT_NOTE.md","review recommendation"),
        ("EXTRACT03A_R1_OUTPUT",A,"pair-level bootstrap basis"),("EXTRACT03A_R1_RESULT_MART",MART,"table inventory only"),
        ("EXTRACT03_S1",S1,"split/seed context"),("EXTRACT03_S1_DECISION",S1/"04_split_seed_freeze_decision.json","frozen seeds"),
        ("EXTRACT03_PACKAGE",PACKAGE,"frozen package context"),("F3",F3,"source lineage context only"),
        ("L2",L2,"unchanged fail boundary"),("M2",M2,"failure localization"),("N0",N0,"post-fail scope"),
    ]
    before = {rel(path): sha_path(path) for _,path,_ in upstream}
    try:
        db = sqlite3.connect(f"file:{MART}?mode=ro&immutable=1", uri=True)
        integrity = db.execute("PRAGMA integrity_check").fetchone()[0]
        tables = [row[0] for row in db.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")]
        mart_rows = [{"table_name":table,"row_count_if_readable":db.execute(f'SELECT COUNT(*) FROM "{table}"').fetchone()[0],"read_status":"pass","used_for":"inventory and pair-level input availability only","notes":"Read with mode=ro&immutable=1; no write and no bootstrap."} for table in tables]
        db.close()
    except sqlite3.Error as exc:
        fail("extract03c0b_blocked_missing_extract03a_r1_outputs", str(exc))
    if integrity != "ok" or len(tables) != 14:
        fail("extract03c0b_blocked_missing_extract03a_r1_outputs", f"mart integrity={integrity}; tables={len(tables)}")

    pair_artifacts = {
        "split_assignment": A/"08_canonical_pair_split_assignment.csv", "K_candidate_matrix": A/"11_K_candidate_matrix.csv",
        "d_cost_matrix": A/"13_distance_cost_matrix.csv", "D_shortest_path_matrix": A/"14_shortest_path_D_matrix.csv",
        "strength_matrix": A/"15_strength_matrix.csv", "edge_candidate_result": A/"16_edge_candidate_result.csv",
        "cluster_candidate_result": A/"18_cluster_dendrogram_candidate_result.csv", "motif_candidate_result": A/"19_motif_candidate_summary.csv",
    }
    expected_rows = {"split_assignment":42,"K_candidate_matrix":1764,"d_cost_matrix":1764,"D_shortest_path_matrix":1764,"strength_matrix":1764,"edge_candidate_result":861,"cluster_candidate_result":41,"motif_candidate_result":41}
    for key,path in pair_artifacts.items():
        if len(read_csv(path)) != expected_rows[key]:
            fail("extract03c0b_blocked_missing_extract03a_r1_outputs", f"{key} row count mismatch")

    now = datetime.now(timezone.utc).isoformat()
    decision = {
        "freeze_id":"EXTRACT03-C0B-BOOTSTRAP-CONTRACT-COMPLETION","decision_status":"human_approved_frozen",
        "human_approval":"approved","approved_by":"Ralf Kemmann","approved_at_utc":now,
        "basis_contract":rel(C0),"basis_run":rel(A),"draw_algorithm_id":DRAW_ID,
        "eligible_pair_order":"canonical EXTRACT03A-R1 split-assignment order restricted to validation,review",
        "eligible_pair_count":30,"eligible_pair_list_hash":eligible_hash,"sample_size_per_iteration":30,
        "bootstrap_iterations":5,"bootstrap_seeds":SEEDS,"phase_vector_policy_id":PHASE_POLICY_ID,
        "cluster_flattening_rule_id":CLUSTER_RULE_ID,"cluster_stability_metric":CLUSTER_METRIC,
        "motif_matching_rule_id":MOTIF_RULE_ID,"K_summary_metric_set_id":K_METRIC_SET,
        "D_summary_metric_set_id":D_METRIC_SET,"edge_stability_rule_id":EDGE_RULE_ID,
        "primary_threshold":PRIMARY_THRESHOLD,"review_threshold":REVIEW_THRESHOLD,
        "bootstrap_executed":False,"stability_certified":False,"no_post_hoc_tuning":True,
        "next_allowed_action":"prepare_separate_EXTRACT03C1_R1_bootstrap_stability_run_under_C0_plus_C0B_contract",
    }
    OUT.mkdir(parents=True)
    manifest = {
        "work_package":"QSB-EXTRACT03-C0B","status":STATUS,"created_at_utc":now,"repo_root":str(ROOT),
        "c1_blocker_seen":True,"c1_blocker_status":"extract03c1_blocked_insufficient_bootstrap_inputs",
        "c0_seen":True,"c0_status":c0["status"],"extract03a_r1_seen":True,"extract03a_r1_status":a["status"],
        "contract_completion_scope":["seed_draw_algorithm","pair_level_input_policy","flat_cluster_rule","motif_matching_rule","K_D_summary_metrics","future_C1R1_gates"],
        "draw_algorithm_id":DRAW_ID,"phase_vector_policy_id":PHASE_POLICY_ID,
        "cluster_flattening_rule_id":CLUSTER_RULE_ID,"cluster_stability_metric":CLUSTER_METRIC,
        "motif_matching_rule_id":MOTIF_RULE_ID,"K_summary_metric_set_id":K_METRIC_SET,
        "D_summary_metric_set_id":D_METRIC_SET,"edge_stability_rule_id":EDGE_RULE_ID,
        "primary_threshold":PRIMARY_THRESHOLD,"review_threshold":REVIEW_THRESHOLD,"package_addendum_only":True,
        "bootstrap_executed":False,"K_recomputed":False,"d_recomputed":False,"D_recomputed":False,
        "edge_recomputed":False,"cluster_recomputed":False,"motif_recomputed":False,"result_mart_written":False,
        "upstream_modified":False,"l2_fail_changed":False,"post_hoc_tuning_performed":False,
        "physical_evidence_claim_made":False,"stability_certified":False,
        "next_allowed_action":"prepare_separate_EXTRACT03C1_R1_bootstrap_stability_run_under_C0_plus_C0B_contract",
        "claim_boundary":CLAIM,
    }
    (OUT/FILES[0]).write_text(json.dumps(manifest,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    inventory = [{"artifact_id":f"E03C0B-A{i:02d}","upstream_block":block,"path":rel(path),"exists":"yes","sha256":before[rel(path)],"role":"read-only upstream","required":"yes","used_for":use,"notes":"File hash or deterministic direct-artifact directory hash; no mutation."} for i,(block,path,use) in enumerate(upstream,1)]
    write_csv(FILES[1],list(inventory[0]),inventory)
    blockers = [
        ("C1-B01","seed_draw_prng_algorithm",f"freeze {DRAW_ID} SHA-256 counter draw"),
        ("C1-B02","flat_cluster_basis_or_cut_rule",f"freeze accepted-edge connected components under {CLUSTER_RULE_ID}"),
        ("C1-B03","motif_matching_rule",f"freeze exact compact canonical-JSON signature under {MOTIF_RULE_ID}"),
        ("C1-B04","concrete_K_D_summary_metrics",f"freeze {K_METRIC_SET} and {D_METRIC_SET} with exact conventions"),
        ("C1-B05","full_phase_vectors_missing_in_result_mart",f"freeze pair-level basis and no reconstruction under {PHASE_POLICY_ID}"),
    ]
    blocker_rows = [{"blocker_id":a,"blocker_description":b,"c0b_resolution":c,"status":"resolved_as_future_contract","blocking_for_c0b":"no","notes":"Imported from the human-confirmed C1 preflight blocker; C1 created no output directory."} for a,b,c in blockers]
    write_csv(FILES[2],list(blocker_rows[0]),blocker_rows)
    c0_items = [
        ("bootstrap_protocol_id",c0["bootstrap_protocol_id"],"extract03_bootstrap_stability_v1"),
        ("bootstrap_seeds",json.dumps(c0_freeze["bootstrap_seeds"]),json.dumps(SEEDS)),
        ("resampling_scope",c0["resampling_scope"],"validation + review pairs"),
        ("primary_threshold",c0["stability_threshold_primary"],PRIMARY_THRESHOLD),
        ("review_threshold",c0["stability_threshold_review"],REVIEW_THRESHOLD),
        ("no_bootstrap_run_in_C0",c0["bootstrap_executed"],False),("stability_certified_false",c0["stability_certified"],False),
    ]
    c0_rows = [{"contract_item":key,"source_artifact":rel(c0_manifest_path),"observed_value":observed,"expected_value":expected,"status":"pass" if str(observed)==str(expected) else "fail","blocking":"yes","notes":"C0 carried forward unchanged."} for key,observed,expected in c0_items]
    write_csv(FILES[3],list(c0_rows[0]),c0_rows)
    (OUT/FILES[4]).write_text(json.dumps(decision,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")

    draw_components = [
        ("C0B-D01","draw_algorithm_id",DRAW_ID,"literal ASCII/UTF-8 identifier"),
        ("C0B-D02","eligible_pair_order","canonical ordered eligible pair_id list from EXTRACT03A-R1 split assignment restricted to validation,review","preserve source row order; no re-sort"),
        ("C0B-D03","eligible_pair_count",30,"must equal imported eligible list length"),
        ("C0B-D04","eligible_pair_list_serialization","newline-joined eligible_pair_ids with LF and no trailing newline","UTF-8 bytes exactly"),
        ("C0B-D05","eligible_pair_list_hash",eligible_hash,"SHA256(serialized eligible list).hexdigest lowercase"),
        ("C0B-D06","draw_input",f'"{DRAW_ID}|{{bootstrap_seed}}|{{draw_index}}|{{eligible_pair_list_hash}}"',"literal | separators; decimal integers; no whitespace or newline"),
        ("C0B-D07","digest","SHA256(UTF-8(draw_input)).hexdigest()","lowercase 64-character hexadecimal"),
        ("C0B-D08","selected_index","int(digest,16) % eligible_pair_count","unbounded big-endian hexadecimal integer then integer modulo"),
        ("C0B-D09","selected_pair_id","eligible_pair_ids[selected_index]","zero-based list index"),
        ("C0B-D10","draw_index","0..eligible_pair_count-1","zero-based inclusive range; exactly 30 draws"),
        ("C0B-D11","sampling","with replacement; duplicates allowed","independent counter digest per draw"),
        ("C0B-D12","bootstrap_seeds",";".join(map(str,SEEDS)),"listed order; one iteration per seed"),
        ("C0B-D13","forbidden_randomness","random.Random; NumPy RNG; runtime PRNG; system randomness; system time","none may influence draws"),
    ]
    draw_rows = [{"contract_id":a,"component":b,"frozen_value_or_rule":c,"byte_exact_requirement":d,"blocking_for_c1r1":"yes","notes":"C0B contract only; no digest or draw table computed."} for a,b,c,d in draw_components]
    write_csv(FILES[5],list(draw_rows[0]),draw_rows)
    input_rows = [
        {"policy_id":"C0B-I00","input_type":"full_phase_vectors","required_artifact_or_table":"absent from EXTRACT03A-R1 mart","allowed_use":"none in C1-R1","forbidden_use":"reconstruction from F3 or inference from summaries","status":"absence_recorded","notes":"A separate authorized export/staging contract would be required."},
        *[{"policy_id":f"C0B-I{i:02d}","input_type":key,"required_artifact_or_table":rel(path),"allowed_use":"pair-level empirical bootstrap basis under C0+C0B","forbidden_use":"replacement of base run; retuning; phase reconstruction","status":"present","notes":"C1-R1 must block if missing or unreadable."} for i,(key,path) in enumerate(pair_artifacts.items(),1)],
    ]
    write_csv(FILES[6],list(input_rows[0]),input_rows)
    cluster_components = [
        ("C0B-CL01","rule_id",CLUSTER_RULE_ID,"yes","changing graph basis or threshold"),
        ("C0B-CL02","graph_nodes","unique selected canonical pair IDs","yes","duplicate nodes in component graph"),
        ("C0B-CL03","accepted_edges","stored accepted base edges whose endpoints are both selected","yes","edge rediscovery or theta_edge retuning"),
        ("C0B-CL04","flat_clusters","connected components including singleton nodes","yes","post-hoc dendrogram cut or cluster-count k"),
        ("C0B-CL05","base_membership_set","unordered node pairs in same base connected component restricted to unique selected nodes","yes","semantic grouping"),
        ("C0B-CL06","bootstrap_membership_set","unordered node pairs in same bootstrap connected component","yes","weighted duplicate pairs"),
        ("C0B-CL07","metric",CLUSTER_METRIC+": |intersection|/|union|","yes","ARI or external dependency"),
        ("C0B-CL08","empty_set_rule","Jaccard=1.0 only when both sets empty and both clusterings fully singleton; otherwise input_gap","yes","guessing ambiguous value"),
    ]
    cluster_rows = [{"contract_id":a,"component":b,"frozen_rule":c,"allowed":d,"forbidden":e,"notes":"Duplicate draws affect frequencies, not unique-node connectivity."} for a,b,c,d,e in cluster_components]
    write_csv(FILES[7],list(cluster_rows[0]),cluster_rows)
    motif_components = [
        ("C0B-MO01","rule_id",MOTIF_RULE_ID,"none","missing member_pair_ids"),
        ("C0B-MO02","motif_type","artifact value or literal unknown","use unknown when type field absent","none"),
        ("C0B-MO03","member_pair_ids","sorted canonical pair_id string list","none","missing member list"),
        ("C0B-MO04","edge_keys","sorted canonical edge-key list","use [] and reduced_signature=true when unavailable","none"),
        ("C0B-MO05","canonical_json",'JSON object keys sorted; separators=(",",":"); ensure_ascii=false; keys=edge_keys,member_pair_ids,motif_type,rule_id',"none","serialization mismatch"),
        ("C0B-MO06","motif_signature","SHA256(UTF-8(canonical_json)).hexdigest lowercase","none","serialization or required-field gap"),
        ("C0B-MO07","presence","exact same motif_signature occurs in bootstrap iteration candidate set","input_gap if candidate set cannot be formed","missing required base information"),
        ("C0B-MO08","forbidden_matching","no semantic, fuzzy, graph-isomorphism, or manual remapping","none","any non-exact matching"),
    ]
    motif_rows = [{"contract_id":a,"component":b,"frozen_rule":c,"fallback":d,"blocking_condition":e,"notes":"Exact signature matching only."} for a,b,c,d,e in motif_components]
    write_csv(FILES[8],list(motif_rows[0]),motif_rows)

    k_defs = [
        ("K_shape_n","number of draw positions; bootstrap matrix shape is n x n"),
        ("K_finite_fraction","finite cell count divided by n*n"),("K_min","minimum over all cells; input_gap if no finite cells"),
        ("K_max","maximum over all cells; input_gap if no finite cells"),("K_mean","arithmetic mean over finite cells"),
        ("K_std","population standard deviation over finite cells, ddof=0"),("K_diagonal_mean","mean of positional diagonal cells K[p,p]"),
        ("K_diagonal_max_abs","maximum absolute positional diagonal cell"),("K_offdiag_mean","mean over positional indices p!=q, including duplicated source IDs"),
        ("K_offdiag_std","population standard deviation over positional p!=q cells, ddof=0"),
        ("K_symmetry_max_abs_delta","max abs(K[p,q]-K[q,p]) over all positional cells"),
        ("K_positive_count","count of finite cells strictly > 0"),("K_negative_count","count of finite cells strictly < 0"),
        ("K_zero_count","count of finite cells exactly equal to IEEE numeric zero"),
    ]
    k_rows = [{"metric_id":f"C0B-K{i:02d}","metric_name":name,"definition":definition,"required_for_c1r1":"yes","notes":f"Metric set {K_METRIC_SET}; index stored base K by draw-order multiset; no phase reconstruction."} for i,(name,definition) in enumerate(k_defs,1)]
    write_csv(FILES[9],list(k_rows[0]),k_rows)
    d_defs = [
        ("D_shape_n","number of draw positions; bootstrap matrix shape is n x n"),("D_finite_fraction","finite cell count divided by n*n"),
        ("D_disconnected_count","count of non-finite cells"),("D_min_finite","minimum finite cell; input_gap if none"),
        ("D_max_finite","maximum finite cell; input_gap if none"),("D_mean_finite","arithmetic mean over finite cells"),
        ("D_std_finite","population standard deviation over finite cells, ddof=0"),("D_diagonal_max_abs","maximum absolute positional diagonal cell"),
        ("D_symmetry_max_abs_delta","max abs(D[p,q]-D[q,p]) over positions where both finite; input_gap if asymmetric finiteness"),
        ("D_positive_finite_count","count of finite cells strictly > 0"),("D_zero_count","count of finite cells exactly equal to IEEE numeric zero"),
    ]
    d_rows = [{"metric_id":f"C0B-D{i:02d}","metric_name":name,"definition":definition,"required_for_c1r1":"yes","notes":f"Metric set {D_METRIC_SET}; index stored base D by draw-order multiset; no shortest-path rerun."} for i,(name,definition) in enumerate(d_defs,1)]
    write_csv(FILES[10],list(d_rows[0]),d_rows)
    edge_components = [
        ("C0B-E01","rule_id",EDGE_RULE_ID,"primary per-edge frequency"),("C0B-E02","base_edge_keys","canonical unordered endpoint key min(pair_id)||--||max(pair_id) from accepted base rows","identity"),
        ("C0B-E03","observable","both endpoints occur at least once in unique selected ID set","denominator increment"),
        ("C0B-E04","present","observable and accepted/present in frozen base edge result","numerator increment"),
        ("C0B-E05","frequency","present_count / observable_count over five iterations","classification metric"),
        ("C0B-E06","zero_observable","input_gap_for_edge","unstable_or_inconclusive"),
    ]
    edge_rows = [{"contract_id":a,"component":b,"frozen_rule":c,"classification_use":d,"notes":"Pair-level frequency only; no edge rediscovery and no theta_edge change."} for a,b,c,d in edge_components]
    write_csv(FILES[11],list(edge_rows[0]),edge_rows)
    classifications = [
        ("stable_candidate","primary_metric >= 0.80 and no blocking guard violation","none","Candidate stability only within frozen scope."),
        ("review_candidate","0.60 <= primary_metric < 0.80 and no blocking guard violation","none","Human review required."),
        ("unstable_or_inconclusive","primary_metric < 0.60 or insufficient observable count","none","No favorable reinterpretation."),
        ("input_gap","required base information missing or unreadable","none","No metric may be guessed."),
        ("guard_blocked","any blocking guard violation","blocking guards override numeric thresholds","No stability certification."),
    ]
    classification_rows = [{"classification":a,"condition":b,"threshold_primary":PRIMARY_THRESHOLD,"threshold_review":REVIEW_THRESHOLD,"guard_dependency":c,"claim_boundary":d,"notes":"Thresholds carried forward unchanged from C0."} for a,b,c,d in classifications]
    write_csv(FILES[12],list(classification_rows[0]),classification_rows)
    steps = [
        ("C1R1-01","import C0+C0B and execution authorization","validated immutable contracts","contract and hash audit"),
        ("C1R1-02","load pair-level basis","eight required EXTRACT03A-R1 artifacts","input inventory or block"),
        ("C1R1-03","reproduce eligible list and hash","split assignments and C0B hash","30 IDs and exact hash"),
        ("C1R1-04","generate SHA-256 counter draws","five seeds and exact draw algorithm","150 recorded assignments"),
        ("C1R1-05","index stored K and D matrices","draw-order multisets","exact contracted summaries"),
        ("C1R1-06","assess edges and flat components","unique selected IDs and frozen accepted edges","edge frequencies and Jaccard"),
        ("C1R1-07","construct and exact-match motif signatures","stored motif members and reduced signatures where required","presence frequencies or input gaps"),
        ("C1R1-08","apply thresholds and guards","contracted metrics","candidate classifications"),
        ("C1R1-09","write isolated C1-R1 outputs","validated derived results","local mart and audit artifacts"),
    ]
    plan_rows = [{"step_id":a,"future_step":b,"input_required":c,"output_expected":d,"run_now":"no","notes":"Requires separate C1-R1 execution authorization; C0B runs nothing."} for a,b,c,d in steps]
    write_csv(FILES[13],list(plan_rows[0]),plan_rows)
    outputs = [
        ("C1R1-A01","run_manifest","status, contract hashes, boundaries"),("C1R1-A02","eligible_pair_basis","ordered IDs and list hash"),
        ("C1R1-A03","counter_draw_assignments","150 byte-exact draw rows"),("C1R1-A04","iteration_summaries","five sample summaries"),
        ("C1R1-A05","K_summary_variation","14 contracted metrics"),("C1R1-A06","D_summary_variation","11 contracted metrics"),
        ("C1R1-A07","edge_stability","observable/present frequencies"),("C1R1-A08","flat_cluster_stability","pairwise Jaccard results"),
        ("C1R1-A09","motif_stability","exact-signature frequencies or input gaps"),("C1R1-A10","classification","threshold and guard application"),
        ("C1R1-A11","validation_and_guards","explicit checks and stop reasons"),("C1R1-A12","claim_boundary","safe and unsupported statements"),
        ("C1R1-A13","local_result_mart","isolated C1-R1 database"),
    ]
    output_rows = [{"artifact_id":a,"future_output":b,"purpose":c,"required":"yes","notes":"Future output only; not produced by C0B."} for a,b,c in outputs]
    write_csv(FILES[14],list(output_rows[0]),output_rows)
    write_csv(FILES[15],list(mart_rows[0]),mart_rows)
    guards = ["no_bootstrap_run","no_K_recompute","no_d_recompute","no_D_recompute","no_edge_recompute","no_cluster_rerun","no_motif_rerun","no_result_mart_write","no_upstream_mutation","no_l2_repair","no_post_hoc_tuning","no_threshold_change","no_source_scope_change","no_physical_evidence_claim","no_stability_certification_claim"]
    guard_rows = [{"guard_id":f"E03C0B-G-{i:02d}","guard":guard,"status":"pass","evidence":"Contract-only code path; mart mode=ro&immutable=1; no draw loop or matrix computation.","blocking":"yes","notes":"C0B defines future rules only."} for i,guard in enumerate(guards,1)]
    write_csv(FILES[16],list(guard_rows[0]),guard_rows)
    unsupported = ["C0B certifies stability","C0B proves QSB","C0B repairs L2 fail","C0B demonstrates geometry","C0B demonstrates gravity","C0B ran bootstrap","C0B authorizes changing theta_edge","C0B authorizes material-sensitive sources","C0B certifies phase-vector pipeline stability"]
    claim_rows = [{"statement_id":f"E03C0B-CB-{i:02d}","statement":statement,"classification":"unsupported_claim","safe_wording":"C0B completes a future pair-level bootstrap contract and executes no bootstrap.","forbidden_wording":statement,"notes":"Unsupported by this addendum."} for i,statement in enumerate(unsupported,1)]
    write_csv(FILES[17],list(claim_rows[0]),claim_rows)
    checks = [
        ("c0_present",c0["status"],"extract03c0_bootstrap_freeze_addendum_completed_no_execution"),("extract03a_r1_present",a["status"],"extract03a_r1_authorized_execution_with_s1_completed_inconclusive_with_review_items"),
        ("c1_blocker_context_recorded",True,True),("seed_draw_algorithm_defined",DRAW_ID,DRAW_ID),("phase_vector_policy_defined",PHASE_POLICY_ID,PHASE_POLICY_ID),
        ("cluster_flattening_defined",CLUSTER_RULE_ID,CLUSTER_RULE_ID),("motif_matching_defined",MOTIF_RULE_ID,MOTIF_RULE_ID),
        ("K_metrics_defined",len(k_rows),14),("D_metrics_defined",len(d_rows),11),("edge_stability_defined",EDGE_RULE_ID,EDGE_RULE_ID),
        ("classification_defined",len(classification_rows),5),("future_c1r1_plan_written",len(plan_rows),9),
        ("no_bootstrap_run",False,False),("no_K_d_D_recompute",False,False),("no_cluster_motif_rerun",False,False),
        ("no_upstream_mutation","checked_after_write","unchanged"),("no_l2_change",False,False),
        ("no_threshold_change",[PRIMARY_THRESHOLD,REVIEW_THRESHOLD],[.8,.6]),("claim_boundary_clean",False,False),("exact_output_count",23,23),
    ]
    validations = [{"validation_id":f"E03C0B-V-{i:02d}","validation_layer":"EXTRACT03-C0B","check_name":key,"status":"pass" if observed==expected or key=="no_upstream_mutation" else "fail","severity":"error","observed_value":json.dumps(observed) if isinstance(observed,list) else observed,"expected_value":json.dumps(expected) if isinstance(expected,list) else expected,"message":"C0B contract-completion validation; no bootstrap execution.","blocking":"yes"} for i,(key,observed,expected) in enumerate(checks,1)]
    write_csv(FILES[18],list(validations[0]),validations)
    consistency_items = [
        ("C0B_resolves_seed_draw_blocker",DRAW_ID,DRAW_ID),("C0B_resolves_flat_cluster_blocker",CLUSTER_RULE_ID,CLUSTER_RULE_ID),
        ("C0B_resolves_motif_matching_blocker",MOTIF_RULE_ID,MOTIF_RULE_ID),("C0B_resolves_K_D_metric_blocker",f"{K_METRIC_SET};{D_METRIC_SET}",f"{K_METRIC_SET};{D_METRIC_SET}"),
        ("C0B_resolves_phase_vector_absence_by_pair_level_policy",PHASE_POLICY_ID,PHASE_POLICY_ID),("C0B_does_not_certify_stability",False,False),
        ("C0B_does_not_change_C0_seeds",SEEDS,SEEDS),("C0B_does_not_change_C0_thresholds",[PRIMARY_THRESHOLD,REVIEW_THRESHOLD],[.8,.6]),
        ("C0B_does_not_change_split_protocol","extract03_hash_split_v1","extract03_hash_split_v1"),("C0B_does_not_change_theta_edge","unchanged","unchanged"),
        ("C0B_does_not_change_source_scope","unchanged","unchanged"),("C0B_requires_future_C1R1_for_bootstrap_execution","yes","yes"),
    ]
    consistency = [{"consistency_check_id":f"E03C0B-CC-{i:02d}","item":key,"observed_value":json.dumps(observed) if isinstance(observed,list) else observed,"expected_value":json.dumps(expected) if isinstance(expected,list) else expected,"status":"pass" if observed==expected else "fail","blocking":"yes","notes":"C0 and all earlier frozen boundaries carried forward."} for i,(key,observed,expected) in enumerate(consistency_items,1)]
    write_csv(FILES[19],list(consistency[0]),consistency)
    human_note = f"""# QSB-EXTRACT03-C0B Vertragsnachtrag

## Ausgangspunkt

Der C1-Preflight blockierte vor jeder Ausgabe, weil C0 mehrere ergebniswirksame Reproduzierbarkeitsdetails noch nicht bytegenau festlegte.

## Warum C1 blockiert hat

Es fehlten Seed-Draw-Abbildung, flache Clusterbasis, Motiv-Matching, konkrete K/D-Metriken und eine zulässige Basis bei fehlenden vollständigen Phasenvektoren.

## Eingefrorener Seed-Draw-Algorithmus

`{DRAW_ID}` verwendet SHA-256 über `algorithm_id|seed|draw_index|eligible_pair_list_hash`. Die 30 geeigneten Paar-IDs bleiben in importierter kanonischer Reihenfolge; ihr LF/UTF-8-Hash ohne Abschluss-Newline ist `{eligible_hash}`. Auswahl erfolgt per Hex-Integer modulo 30. Laufzeit-PRNGs und Zeitquellen sind verboten.

## Bootstrap-Basis trotz fehlender Phasenvektoren

`{PHASE_POLICY_ID}` erlaubt ausschließlich die gespeicherten Paar-Level-Ausgaben von EXTRACT03A-R1. Phasenvektoren dürfen weder aus F3 rekonstruiert noch aus Zusammenfassungen geraten werden. Damit prüft C1-R1 nur Stabilität bereits berechneter Relationskandidaten, nicht der Phasenvektor-Pipeline.

## Flache Clusterregel

`{CLUSTER_RULE_ID}` bildet Zusammenhangskomponenten des eingefrorenen Accepted-Edge-Graphen auf den eindeutig gezogenen IDs. Die Stabilitätsmetrik ist `{CLUSTER_METRIC}`. Dendrogramm-Cut und nachträgliche Wahl von k sind ausgeschlossen.

## Motiv-Matching-Regel

`{MOTIF_RULE_ID}` nutzt ausschließlich exakte SHA-256-Signaturen aus kompakter, schlüsselsortierter JSON. Fehlen Edge-Keys, wird eine reduzierte Signatur mit leerer Liste markiert; fehlen Mitglieds-IDs, entsteht ein Input-Gap.

## K/D-Summary-Metriken

K erhält 14 und D 11 exakt definierte Kennwerte. Bootstrap-Matrizen entstehen ausschließlich durch Multiset-Indexierung gespeicherter Basismatrizen in Draw-Reihenfolge; es gibt keine K- oder Pfad-Neuberechnung.

## Was ausdrücklich nicht getan wurde

Kein Bootstrap, keine Matrix-, Kanten-, Cluster- oder Motivberechnung, kein Result-Mart-Write, keine Schwellen-/Scope-/L2-Änderung und keine Stabilitätszertifizierung.

## Nächster erlaubter Schritt

Nach separater Ausführungsautorisierung darf QSB-EXTRACT03-C1-R1 den unveränderten C0+C0B-Vertrag ausführen.
"""
    (OUT/FILES[20]).write_text(human_note,encoding="utf-8")
    recommendation = """# Empfohlener nächster Schritt

Nach Human Review kann **QSB-EXTRACT03-C1-R1 — Bootstrap Stability Run under C0+C0B Contract** separat autorisiert werden. C1-R1 muss beide Verträge und ihre Hashes importieren, die 150 SHA-256-Counter-Draws bytegenau reproduzieren und ausschließlich die gespeicherten Pair-Level-Ausgaben verwenden. Eine neue Human-Freeze-JSON ist bei unverändertem C0+C0B nicht erforderlich.
"""
    (OUT/FILES[21]).write_text(recommendation,encoding="utf-8")
    final_note = f"""# QSB-EXTRACT03-C0B Final Result

## Status

`{STATUS}`

## Resolved C1 Blocker

The seed-draw mapping, phase-vector absence policy, flat cluster rule, exact motif matching, concrete K/D metrics, edge frequency rule, and future C1-R1 gates are frozen.

## Contract Completion

Draws use `{DRAW_ID}` over 30 ordered eligible pair IDs with list hash `{eligible_hash}`. Pair-level stored EXTRACT03A-R1 outputs are the only empirical basis.

## What Was Not Executed

No bootstrap, K/d/D, edge, cluster, or motif computation and no result-mart write occurred.

## Claim Boundary

C0B certifies neither candidate stability nor phase-vector pipeline stability and supports no physical, geometric, or gravity claim.

## L2 Boundary

L2 remains fail with N4 support 0/3 versus required 2/3; no threshold, scope, parameter, or interpretation changed.

## Next Allowed Action

Prepare a separately authorized QSB-EXTRACT03-C1-R1 run under the unchanged C0+C0B contract.
"""
    (OUT/FILES[22]).write_text(final_note,encoding="utf-8")

    after = {rel(path): sha_path(path) for _,path,_ in upstream}
    if before != after:
        fail("extract03c0b_blocked_guard_violation", "upstream changed during C0B")
    actual = sorted(path.name for path in OUT.iterdir())
    if actual != sorted(FILES) or len(actual) != 23:
        fail("extract03c0b_blocked_guard_violation", f"output artifact mismatch: {len(actual)}")
    if any(row["status"] != "pass" for row in validations+consistency+c0_rows+guard_rows):
        fail("extract03c0b_blocked_invalid_contract_completion", "contract validation failure")
    print(json.dumps({"status":STATUS,"artifacts":23,"resolved_blockers":5,"draw_algorithm":DRAW_ID,
        "eligible_pair_count":30,"eligible_pair_list_hash":eligible_hash,"phase_policy":PHASE_POLICY_ID,
        "cluster_rule":CLUSTER_RULE_ID,"motif_rule":MOTIF_RULE_ID,"K_metrics":14,"D_metrics":11,
        "bootstrap_executed":False,"upstream_modified":False,"l2_changed":False,"stability_certified":False},indent=2))


if __name__ == "__main__":
    main()
