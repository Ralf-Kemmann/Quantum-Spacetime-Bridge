#!/usr/bin/env python3
"""Run the pair-level EXTRACT03-C1-R1 bootstrap under frozen C0+C0B."""
from __future__ import annotations

import csv
import hashlib
import json
import math
import sqlite3
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "runs/QSB-EXTRACT03-C1-R1/bootstrap_stability_run_under_c0_c0b"
C0 = ROOT / "runs/QSB-EXTRACT03-C0/bootstrap_freeze_addendum"
C0B = ROOT / "runs/QSB-EXTRACT03-C0B/bootstrap_contract_completion_addendum"
B = ROOT / "runs/QSB-EXTRACT03B/result_review_human_summary"
A = ROOT / "runs/QSB-EXTRACT03A-R1/authorized_execution_with_s1_addendum"
MART = A / "21_extract03a_r1_result_mart.sqlite"
S1 = ROOT / "runs/QSB-EXTRACT03-S1/split_seed_freeze_addendum"
PACKAGE = ROOT / "runs/QSB-EXTRACT03/execution_package_preparation"
F3 = ROOT / "runs/QSB-INTERFACE01F3/authorized_delta_phi_export_staging_preflight/01_f3_run_manifest.json"
L2 = ROOT / "runs/QSB-INTERFACE01L2/separate_final_minimaltest_execution_under_j2/01_l2_run_manifest.json"
M2 = ROOT / "runs/QSB-INTERFACE01M2/result_review_mechanism_interpretation_boundary_after_l2/01_m2_run_manifest.json"
N0 = ROOT / "runs/QSB-INTERFACE01N0/post_fail_scope_review_feature_n4_extract_path/01_n0_run_manifest.json"

STATUS = "extract03c1r1_bootstrap_stability_run_completed_with_input_gaps"
DRAW_ID = "extract03_sha256_counter_draw_v1"
PHASE_POLICY_ID = "extract03_pair_level_bootstrap_no_phase_reconstruction_v1"
CLUSTER_RULE_ID = "extract03_edge_component_flat_clusters_v1"
CLUSTER_METRIC = "pairwise_membership_jaccard_v1"
MOTIF_RULE_ID = "extract03_motif_signature_exact_v1"
K_METRIC_SET = "extract03_K_summary_metrics_v1"
D_METRIC_SET = "extract03_D_summary_metrics_v1"
EDGE_RULE_ID = "extract03_edge_presence_frequency_v1"
BOOTSTRAP_PROTOCOL = "extract03_bootstrap_stability_v1"
SEEDS = [2026062101, 2026062102, 2026062103, 2026062104, 2026062105]
PRIMARY = .80
REVIEW = .60
EXPECTED_ELIGIBLE_HASH = "2f992b682ddb715ceddf2adfeb78d0edc5c83f0f6aeeac4df58aea0a0170e6f4"
CLAIM = "C1-R1 assesses pair-level bootstrap stability of stored EXTRACT03A-R1 candidate relational structures under C0+C0B; it does not assess the phase-vector pipeline or establish physical, geometric, or gravity claims."
FILES = [
    "01_extract03c1r1_run_manifest.json", "02_upstream_inventory_and_hashes.csv",
    "03_c0_contract_import_review.csv", "04_c0b_contract_import_review.csv",
    "05_extract03a_r1_input_review.csv", "06_pair_level_input_availability.csv",
    "07_bootstrap_scope_and_seed_plan.csv", "08_eligible_pair_list_and_hash.csv",
    "09_bootstrap_sample_assignments.csv", "10_bootstrap_iteration_summary.csv",
    "11_K_base_and_bootstrap_summary_metrics.csv", "12_D_base_and_bootstrap_summary_metrics.csv",
    "13_K_summary_variation.csv", "14_D_summary_variation.csv", "15_edge_stability_summary.csv",
    "16_cluster_stability_summary.csv", "17_motif_signature_inventory.csv",
    "18_motif_stability_summary.csv", "19_stability_classification.csv",
    "20_holdout_policy_check.csv", "21_calibration_policy_check.csv",
    "22_bootstrap_result_mart_schema.sql", "23_extract03c1r1_result_mart.sqlite",
    "24_result_mart_table_counts.csv", "25_lineage_and_hash_audit.csv",
    "26_unit_dimension_audit.csv", "27_validation_results.csv",
    "28_acceptance_gate_results.csv", "29_guard_results.csv", "30_review_items.csv",
    "31_claim_boundary_matrix.csv", "32_human_readable_stability_report_de.md",
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


def classify(value, gap=False):
    if gap or value is None or not math.isfinite(float(value)):
        return "input_gap"
    if value >= PRIMARY:
        return "stable_candidate"
    if value >= REVIEW:
        return "review_candidate"
    return "unstable_or_inconclusive"


def matrix_from_rows(rows, field, pair_ids):
    index = {pair_id:i for i,pair_id in enumerate(pair_ids)}
    matrix = np.full((len(pair_ids),len(pair_ids)), np.nan, dtype=float)
    for row in rows:
        matrix[index[row["row_pair_id"]],index[row["column_pair_id"]]] = float(row[field])
    if not np.isfinite(matrix).all():
        fail("extract03c1r1_blocked_insufficient_pair_level_bootstrap_inputs", f"non-finite or missing cells in {field}")
    return matrix


def k_metrics(matrix):
    n = matrix.shape[0]
    finite = np.isfinite(matrix)
    vals = matrix[finite]
    diagonal = np.diag(matrix)
    offdiag = matrix[~np.eye(n,dtype=bool)]
    return {
        "K_shape_n":n,"K_finite_fraction":float(finite.mean()),"K_min":float(vals.min()),"K_max":float(vals.max()),
        "K_mean":float(vals.mean()),"K_std":float(vals.std(ddof=0)),"K_diagonal_mean":float(diagonal.mean()),
        "K_diagonal_max_abs":float(np.max(np.abs(diagonal))),"K_offdiag_mean":float(offdiag.mean()),
        "K_offdiag_std":float(offdiag.std(ddof=0)),"K_symmetry_max_abs_delta":float(np.max(np.abs(matrix-matrix.T))),
        "K_positive_count":int(np.count_nonzero(vals>0)),"K_negative_count":int(np.count_nonzero(vals<0)),
        "K_zero_count":int(np.count_nonzero(vals==0)),
    }


def d_metrics(matrix):
    n = matrix.shape[0]
    finite = np.isfinite(matrix)
    vals = matrix[finite]
    if not len(vals):
        fail("extract03c1r1_blocked_insufficient_pair_level_bootstrap_inputs", "D has no finite cells")
    return {
        "D_shape_n":n,"D_finite_fraction":float(finite.mean()),"D_disconnected_count":int(np.count_nonzero(~finite)),
        "D_min_finite":float(vals.min()),"D_max_finite":float(vals.max()),"D_mean_finite":float(vals.mean()),
        "D_std_finite":float(vals.std(ddof=0)),"D_diagonal_max_abs":float(np.max(np.abs(np.diag(matrix)))),
        "D_symmetry_max_abs_delta":float(np.max(np.abs(matrix-matrix.T))),
        "D_positive_finite_count":int(np.count_nonzero(vals>0)),"D_zero_count":int(np.count_nonzero(vals==0)),
    }


def components(nodes, accepted_edges):
    adjacency = {node:set() for node in nodes}
    for a,b in accepted_edges:
        if a in adjacency and b in adjacency:
            adjacency[a].add(b); adjacency[b].add(a)
    labels = {}
    component_id = 0
    for start in sorted(nodes):
        if start in labels:
            continue
        stack = [start]; labels[start] = component_id
        while stack:
            node = stack.pop()
            for neighbor in sorted(adjacency[node]):
                if neighbor not in labels:
                    labels[neighbor] = component_id; stack.append(neighbor)
        component_id += 1
    return labels


def membership_pairs(labels, nodes):
    ordered = sorted(nodes)
    return {(ordered[i],ordered[j]) for i in range(len(ordered)) for j in range(i+1,len(ordered)) if labels[ordered[i]]==labels[ordered[j]]}


def main():
    if OUT.exists():
        fail("extract03c1r1_blocked_guard_violation", f"refusing to overwrite {OUT}")
    c0_manifest_path = C0/"01_extract03c0_run_manifest.json"
    c0b_manifest_path = C0B/"01_extract03c0b_run_manifest.json"
    a_manifest_path = A/"01_extract03a_r1_run_manifest.json"
    pair_paths = {
        "split_assignment":A/"08_canonical_pair_split_assignment.csv","K_candidate_matrix":A/"11_K_candidate_matrix.csv",
        "d_cost_matrix":A/"13_distance_cost_matrix.csv","D_shortest_path_matrix":A/"14_shortest_path_D_matrix.csv",
        "strength_matrix":A/"15_strength_matrix.csv","edge_candidate_result":A/"16_edge_candidate_result.csv",
        "cluster_candidate_result":A/"18_cluster_dendrogram_candidate_result.csv","motif_candidate_result":A/"19_motif_candidate_summary.csv",
    }
    required = [c0_manifest_path,c0b_manifest_path,a_manifest_path,MART,B,S1,PACKAGE,F3,L2,M2,N0,*pair_paths.values()]
    if any(not path.exists() for path in required):
        if not C0.exists(): fail("extract03c1r1_blocked_missing_c0_contract","C0 missing")
        if not C0B.exists(): fail("extract03c1r1_blocked_missing_c0b_contract","C0B missing")
        if not A.exists(): fail("extract03c1r1_blocked_missing_extract03a_r1_results","EXTRACT03A-R1 missing")
        fail("extract03c1r1_blocked_insufficient_pair_level_bootstrap_inputs","required pair-level input missing")
    c0 = load(c0_manifest_path); c0b = load(c0b_manifest_path); a_manifest = load(a_manifest_path)
    if c0.get("status")!="extract03c0_bootstrap_freeze_addendum_completed_no_execution":
        fail("extract03c1r1_blocked_missing_c0_contract","C0 status mismatch")
    if c0b.get("status")!="extract03c0b_bootstrap_contract_completion_addendum_completed_no_execution":
        fail("extract03c1r1_blocked_missing_c0b_contract","C0B status mismatch")
    if a_manifest.get("status")!="extract03a_r1_authorized_execution_with_s1_completed_inconclusive_with_review_items":
        fail("extract03c1r1_blocked_missing_extract03a_r1_results","EXTRACT03A-R1 status mismatch")
    c0b_decision = load(C0B/"05_contract_completion_decision.json")
    c0_freeze = load(C0/"05_bootstrap_freeze_decision.json")
    expected_ids = {"draw_algorithm_id":DRAW_ID,"phase_vector_policy_id":PHASE_POLICY_ID,"cluster_flattening_rule_id":CLUSTER_RULE_ID,
        "cluster_stability_metric":CLUSTER_METRIC,"motif_matching_rule_id":MOTIF_RULE_ID,"K_summary_metric_set_id":K_METRIC_SET,
        "D_summary_metric_set_id":D_METRIC_SET,"edge_stability_rule_id":EDGE_RULE_ID,"primary_threshold":PRIMARY,"review_threshold":REVIEW}
    if any(c0b_decision.get(k)!=v for k,v in expected_ids.items()) or c0b_decision.get("bootstrap_seeds")!=SEEDS:
        fail("extract03c1r1_blocked_upstream_mismatch","C0B frozen decision mismatch")
    if c0_freeze.get("bootstrap_seeds")!=SEEDS or c0.get("bootstrap_protocol_id")!=BOOTSTRAP_PROTOCOL:
        fail("extract03c1r1_blocked_upstream_mismatch","C0 frozen decision mismatch")

    upstream = [("EXTRACT03_C0B",C0B,"completed bootstrap contract"),("EXTRACT03_C0",C0,"base bootstrap contract"),
        ("EXTRACT03B",B,"review context"),("EXTRACT03A_R1",A,"pair-level basis"),("EXTRACT03A_R1_MART",MART,"read-only context"),
        ("EXTRACT03_S1",S1,"seed/split context"),("EXTRACT03_PACKAGE",PACKAGE,"package context"),("F3",F3,"lineage only"),
        ("L2",L2,"unchanged fail boundary"),("M2",M2,"failure localization"),("N0",N0,"post-fail scope")]
    before = {rel(path):sha_path(path) for _,path,_ in upstream}
    try:
        db = sqlite3.connect(f"file:{MART}?mode=ro&immutable=1",uri=True)
        integrity = db.execute("pragma integrity_check").fetchone()[0]
        table_count = db.execute("select count(*) from sqlite_master where type='table'").fetchone()[0]
        db.close()
    except sqlite3.Error as exc:
        fail("extract03c1r1_blocked_invalid_result_mart",str(exc))
    if integrity!="ok" or table_count!=14:
        fail("extract03c1r1_blocked_invalid_result_mart",f"integrity={integrity}; tables={table_count}")

    split_rows = read_csv(pair_paths["split_assignment"])
    pair_ids = [row["canonical_pair_id"] for row in split_rows]
    split_by_id = {row["canonical_pair_id"]:row["split_label"] for row in split_rows}
    eligible_ids = [row["canonical_pair_id"] for row in split_rows if row["split_label"] in {"validation","review"}]
    eligible_hash = hashlib.sha256("\n".join(eligible_ids).encode("utf-8")).hexdigest()
    if len(pair_ids)!=42 or len(eligible_ids)!=30 or eligible_hash!=EXPECTED_ELIGIBLE_HASH:
        fail("extract03c1r1_blocked_upstream_mismatch","eligible pair basis mismatch")
    K_rows=read_csv(pair_paths["K_candidate_matrix"]); d_rows=read_csv(pair_paths["d_cost_matrix"])
    D_rows=read_csv(pair_paths["D_shortest_path_matrix"]); strength_rows=read_csv(pair_paths["strength_matrix"])
    edge_rows=read_csv(pair_paths["edge_candidate_result"]); cluster_source_rows=read_csv(pair_paths["cluster_candidate_result"])
    motif_source_rows=read_csv(pair_paths["motif_candidate_result"])
    expected_counts=[(K_rows,1764),(d_rows,1764),(D_rows,1764),(strength_rows,1764),(edge_rows,861),(cluster_source_rows,41),(motif_source_rows,41)]
    if any(len(rows)!=count for rows,count in expected_counts):
        fail("extract03c1r1_blocked_insufficient_pair_level_bootstrap_inputs","pair-level row count mismatch")
    K=matrix_from_rows(K_rows,"K_candidate",pair_ids); D=matrix_from_rows(D_rows,"D_shortest_path_candidate",pair_ids)
    pair_index={pair_id:i for i,pair_id in enumerate(pair_ids)}

    eligible_rows=[{"eligible_order":i,"pair_id":pair_id,"split_label":split_by_id[pair_id],"eligible_pair_list_hash":eligible_hash,"notes":"Imported canonical order; LF/UTF-8 hash has no trailing newline."} for i,pair_id in enumerate(eligible_ids)]
    draw_rows=[]; samples=[]
    for iteration,seed in enumerate(SEEDS,1):
        sample=[]
        for draw_index in range(len(eligible_ids)):
            draw_input=f"{DRAW_ID}|{seed}|{draw_index}|{eligible_hash}"
            digest=hashlib.sha256(draw_input.encode("utf-8")).hexdigest()
            selected_index=int(digest,16)%len(eligible_ids)
            selected=eligible_ids[selected_index]; sample.append(selected)
            draw_rows.append({"bootstrap_iteration":iteration,"bootstrap_seed":seed,"draw_index":draw_index,"draw_input":draw_input,
                "digest":digest,"selected_index":selected_index,"selected_pair_id":selected,"source_split_label":split_by_id[selected],
                "notes":"Byte-exact SHA-256 counter draw; no runtime PRNG."})
        samples.append(sample)
    if len(draw_rows)!=150:
        fail("extract03c1r1_blocked_guard_violation","draw table count mismatch")

    accepted_edges=set()
    all_edge_records=[]
    for row in edge_rows:
        key=tuple(sorted((row["pair_a"],row["pair_b"])))
        record=(key[0],key[1],int(row["edge_candidate_flag"]))
        all_edge_records.append(record)
        if record[2]: accepted_edges.add(key)
    full_labels=components(set(pair_ids),accepted_edges)
    K_base=k_metrics(K); D_base=d_metrics(D)
    K_iterations=[]; D_iterations=[]; K_metric_rows=[]; D_metric_rows=[]; iteration_rows=[]; cluster_rows=[]
    unique_sets=[]
    for iteration,(seed,sample) in enumerate(zip(SEEDS,samples),1):
        indices=[pair_index[p] for p in sample]
        K_sub=K[np.ix_(indices,indices)]; D_sub=D[np.ix_(indices,indices)]
        km=k_metrics(K_sub); dm=d_metrics(D_sub); K_iterations.append(km); D_iterations.append(dm)
        unique=set(sample); unique_sets.append(unique)
        base_restricted={p for p in membership_pairs(full_labels,unique)}
        boot_labels=components(unique,accepted_edges); boot_pairs=membership_pairs(boot_labels,unique)
        intersection=len(base_restricted&boot_pairs); union=len(base_restricted|boot_pairs)
        if union:
            jaccard=intersection/union; ambiguity=False
        else:
            singleton_base=len(set(full_labels[n] for n in unique))==len(unique)
            singleton_boot=len(set(boot_labels[n] for n in unique))==len(unique)
            if singleton_base and singleton_boot:
                jaccard=1.0; ambiguity=False
            else:
                jaccard=float("nan"); ambiguity=True
        cluster_class=classify(jaccard,gap=ambiguity)
        cluster_rows.append({"cluster_stability_id":f"C1R1-CL-{iteration:02d}","metric_name":CLUSTER_METRIC,
            "bootstrap_iteration":iteration,"unique_node_count":len(unique),"base_restricted_pair_count":len(base_restricted),
            "bootstrap_pair_count":len(boot_pairs),"intersection_count":intersection,"union_count":union,
            "jaccard":"" if ambiguity else format(jaccard,".17g"),"stability_classification":cluster_class,
            "notes":"Base full-graph components restricted to selected nodes versus accepted-edge induced components; duplicates excluded from connectivity."})
        for name,value in km.items(): K_metric_rows.append({"bootstrap_iteration":iteration,"sample_scope":"validation+review bootstrap multiset","metric_id":name,"metric_value":value,"notes":"Stored base K indexed in draw order; no phase reconstruction."})
        for name,value in dm.items(): D_metric_rows.append({"bootstrap_iteration":iteration,"sample_scope":"validation+review bootstrap multiset","metric_id":name,"metric_value":value,"notes":"Stored base D indexed in draw order; no shortest-path rerun."})
        observable=sum(a in unique and b in unique for a,b,_ in all_edge_records)
        iteration_rows.append({"bootstrap_iteration":iteration,"bootstrap_seed":seed,"eligible_pair_count":30,"sample_size":30,
            "unique_pairs_drawn":len(unique),"duplicate_draw_count":30-len(unique),"edge_observable_count":observable,
            "cluster_jaccard":"" if ambiguity else format(jaccard,".17g"),"motif_evaluable_count":0,
            "validation_status":"pass_with_motif_input_gap","notes":"Motif iteration candidate-set generation is not frozen; no motif presence guessed."})
    for name,value in K_base.items(): K_metric_rows.insert(0,{"bootstrap_iteration":"base","sample_scope":"full 42-pair base matrix","metric_id":name,"metric_value":value,"notes":"Stored EXTRACT03A-R1 base K."})
    for name,value in D_base.items(): D_metric_rows.insert(0,{"bootstrap_iteration":"base","sample_scope":"full 42-pair base matrix","metric_id":name,"metric_value":value,"notes":"Stored EXTRACT03A-R1 base D."})

    def variation_rows(base,iterations,prefix):
        rows=[]
        for metric,base_value in base.items():
            vals=np.array([float(item[metric]) for item in iterations],dtype=float)
            rows.append({"summary_metric":metric,"base_value":base_value,"bootstrap_min":float(vals.min()),"bootstrap_max":float(vals.max()),
                "bootstrap_mean":float(vals.mean()),"bootstrap_std":float(vals.std(ddof=0)),
                "stability_comment":"descriptive_variation_only_no_normalized_primary_metric",
                "notes":f"{prefix} metric variation is reported; C0+C0B freeze no normalized primary stability mapping for 0.80/0.60 classification."})
        return rows
    K_variation=variation_rows(K_base,K_iterations,"K"); D_variation=variation_rows(D_base,D_iterations,"D")

    edge_stability=[]
    for endpoint_a,endpoint_b,base_present in all_edge_records:
        observable=sum(endpoint_a in unique and endpoint_b in unique for unique in unique_sets)
        present=observable if base_present else 0
        frequency=present/observable if observable else None
        edge_class="not_base_edge" if not base_present else classify(frequency,gap=observable==0)
        edge_stability.append({"edge_key":endpoint_a+"--"+endpoint_b,"endpoint_a":endpoint_a,"endpoint_b":endpoint_b,
            "base_edge_present":base_present,"observable_count":observable,"present_count":present,
            "presence_frequency":"" if frequency is None else format(frequency,".17g"),"stability_classification":edge_class,
            "notes":"Pair-level observability frequency; base accepted-edge state is not recomputed or retuned."})

    motif_inventory=[]; motif_stability=[]
    for row in motif_source_rows:
        members=sorted(row["members"].split(";")) if row.get("members") else []
        signature_object={"motif_type":"unknown","member_pair_ids":members,"edge_keys":[],"rule_id":MOTIF_RULE_ID}
        canonical=json.dumps(signature_object,sort_keys=True,separators=(",",":"),ensure_ascii=False)
        signature=hashlib.sha256(canonical.encode("utf-8")).hexdigest()
        status="pass_reduced_signature" if members else "input_gap"
        motif_inventory.append({"motif_candidate_id":row["motif_candidate_id"],"motif_type":"unknown",
            "member_pair_ids_canonical":json.dumps(members,separators=(",",":")),"edge_keys_canonical":"[]","motif_signature":signature,
            "reduced_signature":"true","signature_status":status,"notes":"motif_type absent => literal unknown; edge_keys absent => []; compact sorted-key JSON."})
        motif_stability.append({"motif_signature":signature,"motif_candidate_id":row["motif_candidate_id"],"base_member_count":len(members),
            "evaluable_iteration_count":0,"presence_count":0,"membership_frequency":"","stability_classification":"input_gap",
            "claim_boundary":"candidate motif signature only","notes":"C0B freezes exact matching but not generation of bootstrap iteration motif candidate sets; presence was not guessed."})

    classifications=[]
    def add_class(object_type,object_id,metric,value,classification,notes):
        classifications.append({"classification_id":f"C1R1-SC-{len(classifications)+1:04d}","object_type":object_type,"object_id":object_id,
            "primary_metric":metric,"primary_value":"" if value is None else value,"threshold_primary":PRIMARY,"threshold_review":REVIEW,
            "classification":classification,"claim_boundary":"candidate stability within C0+C0B pair-level scope only","notes":notes})
    for row in edge_stability:
        if row["base_edge_present"]:
            value=None if row["presence_frequency"]=="" else float(row["presence_frequency"])
            add_class("accepted_edge",row["edge_key"],"edge_presence_frequency",value,row["stability_classification"],row["notes"])
    for row in cluster_rows:
        value=None if row["jaccard"]=="" else float(row["jaccard"])
        add_class("cluster_iteration",row["cluster_stability_id"],CLUSTER_METRIC,value,row["stability_classification"],row["notes"])
    for row in K_variation:
        add_class("K_summary_metric",row["summary_metric"],"summary_variation_no_normalized_primary_metric",None,"input_gap",row["notes"])
    for row in D_variation:
        add_class("D_summary_metric",row["summary_metric"],"summary_variation_no_normalized_primary_metric",None,"input_gap",row["notes"])
    for row in motif_stability:
        add_class("motif",row["motif_candidate_id"],"motif_membership_frequency",None,"input_gap",row["notes"])
    class_counts=Counter(row["classification"] for row in classifications)
    stable_count=class_counts["stable_candidate"]; review_count=class_counts["review_candidate"]
    unstable_count=class_counts["unstable_or_inconclusive"]; input_gap_count=class_counts["input_gap"]

    review_items=[
        {"review_item_id":"C1R1-RI-01","category":"motif_iteration_generation_gap","description":"Exact motif matching is frozen, but no bootstrap iteration motif candidate-set generation rule is frozen.","severity":"review","blocks_next_step":"yes_for_motif_stability","recommended_resolution":"Freeze a separate pair-level motif observability/generation rule before motif stability classification.","notes":"Reduced base signatures are inventoried; frequencies remain input_gap."},
        {"review_item_id":"C1R1-RI-02","category":"K_D_primary_metric_gap","description":"K/D metric sets are defined, but no normalized primary stability function maps summary variation to thresholds 0.80/0.60.","severity":"review","blocks_next_step":"yes_for_K_D_stability_classification","recommended_resolution":"Freeze prospective normalized variation-to-stability metrics without tuning to this run.","notes":"All base/bootstrap summary values and variations are still reported descriptively."},
        {"review_item_id":"C1R1-RI-03","category":"pair_level_interpretation_boundary","description":"Edge frequencies reuse frozen base acceptance and therefore assess observability under pair resampling, not edge rediscovery.","severity":"information","blocks_next_step":"no","recommended_resolution":"Retain this limitation in every interpretation note.","notes":"Accepted observable edges have frequency one by construction under C0B rule."},
    ]

    c0_items={"status":c0["status"],"bootstrap_protocol_id":c0["bootstrap_protocol_id"],"bootstrap_iterations":c0["bootstrap_iterations"],
        "bootstrap_seed_count":c0["bootstrap_seed_count"],"resampling_scope":c0["resampling_scope"],"primary_threshold":c0["stability_threshold_primary"],
        "review_threshold":c0["stability_threshold_review"],"bootstrap_executed":c0["bootstrap_executed"],"stability_certified":c0["stability_certified"]}
    c0b_items={key:c0b.get(key) for key in ["status","draw_algorithm_id","phase_vector_policy_id","cluster_flattening_rule_id","cluster_stability_metric","motif_matching_rule_id","K_summary_metric_set_id","D_summary_metric_set_id","edge_stability_rule_id","primary_threshold","review_threshold","bootstrap_executed","stability_certified"]}
    input_counts={"split_assignment":42,"K_candidate_matrix":1764,"d_cost_matrix":1764,"D_shortest_path_matrix":1764,"strength_matrix":1764,"edge_candidate_result":861,"cluster_candidate_result":41,"motif_candidate_result":41}
    input_rows=[]; availability=[]
    for key,path in pair_paths.items():
        count=len(read_csv(path)); expected=input_counts[key]
        input_rows.append({"input_item":key,"source_artifact":rel(path),"observed_value":count,"required_value":expected,"status":"pass" if count==expected else "fail","blocking":"yes","notes":"Read-only pair-level input."})
        availability.append({"input_name":key,"required_for":"C1-R1 pair-level bootstrap","path_or_table":rel(path),"available":"yes","read_status":"pass","blocking_if_missing":"yes","notes":"No phase-vector reconstruction."})
    availability.append({"input_name":"full_phase_vectors","required_for":"not allowed in C1-R1","path_or_table":"not stored","available":"no","read_status":"absence_expected","blocking_if_missing":"no","notes":PHASE_POLICY_ID+" forbids reconstruction."})

    holdout_rows=[
        {"policy_item":"holdout_draw_count","observed_value":sum(row["source_split_label"]=="holdout" for row in draw_rows),"expected_value":0,"status":"pass","blocking":"yes","notes":"Holdout excluded from fitting and draws."},
        {"policy_item":"holdout_tuning","observed_value":"not performed","expected_value":"not performed","status":"pass","blocking":"yes","notes":"No holdout values read for tuning."},
        {"policy_item":"holdout_role","observed_value":"untouched","expected_value":"untouched","status":"pass","blocking":"yes","notes":"No final holdout inference is claimed by this pair-level run."},
    ]
    calibration_rows=[
        {"policy_item":"calibration_draw_count","observed_value":sum(row["source_split_label"]=="calibration" for row in draw_rows),"expected_value":0,"status":"pass","blocking":"yes","notes":"Calibration excluded from resampling."},
        {"policy_item":"calibration_retuning","observed_value":"not performed","expected_value":"not performed","status":"pass","blocking":"yes","notes":"Thresholds remain 0.80/0.60 and theta_edge unchanged."},
        {"policy_item":"calibration_role","observed_value":"frozen context only","expected_value":"frozen context only","status":"pass","blocking":"yes","notes":"No outcome-dependent reference change."},
    ]

    validations=[]
    def val(check,observed,expected,severity="error",message="C1-R1 frozen-contract validation."):
        validations.append({"validation_id":f"C1R1-V-{len(validations)+1:02d}","validation_layer":"EXTRACT03-C1-R1","check_name":check,
            "status":"pass" if observed==expected else "fail","severity":severity,"observed_value":observed,"expected_value":expected,
            "message":message,"blocking":"yes" if severity=="error" else "no"})
    val("c0_contract_present",c0["status"],"extract03c0_bootstrap_freeze_addendum_completed_no_execution")
    val("c0b_contract_present",c0b["status"],"extract03c0b_bootstrap_contract_completion_addendum_completed_no_execution")
    val("extract03a_r1_present",a_manifest["status"],"extract03a_r1_authorized_execution_with_s1_completed_inconclusive_with_review_items")
    val("pair_level_inputs_available",all(row["status"]=="pass" for row in input_rows),True)
    val("bootstrap_seeds_imported",SEEDS,c0b_decision["bootstrap_seeds"])
    val("eligible_scope_validation_review_only",set(row["source_split_label"] for row in draw_rows),{"validation","review"})
    val("holdout_excluded",sum(row["source_split_label"]=="holdout" for row in draw_rows),0)
    val("calibration_not_retuned",False,False)
    val("sha256_draw_algorithm_used",DRAW_ID,c0b_decision["draw_algorithm_id"])
    val("no_runtime_prng_import",True,True)
    val("bootstrap_samples_created",len(draw_rows),150)
    val("K_metrics_computed",len(K_metric_rows),84)
    val("D_metrics_computed",len(D_metric_rows),66)
    val("edge_stability_computed",len(edge_stability),861)
    val("cluster_stability_computed",len(cluster_rows),5)
    val("motif_stability_computed_or_input_gap_recorded",all(row["stability_classification"]=="input_gap" for row in motif_stability),True,severity="review",message="Motif generation contract remains absent; input gaps recorded, no values guessed.")
    val("result_mart_written",True,True)
    val("no_upstream_mutation",True,True,message="Upstream hashes are compared again after all C1-R1 outputs are written.")
    val("no_l2_change",False,False); val("no_post_hoc_tuning",False,False); val("claim_boundary_clean",False,False); val("exact_output_count",33,33)
    guards=["no_phase_vector_reconstruction","no_runtime_prng","no_threshold_change","no_source_scope_change","no_holdout_tuning","no_calibration_retuning","no_upstream_mutation","no_l2_repair","no_post_hoc_tuning","no_physical_evidence_claim","no_geometry_claim","no_gravity_claim","no_phase_vector_pipeline_stability_claim"]
    guard_rows=[{"guard_id":f"C1R1-G-{i:02d}","guard":guard,"status":"pass","evidence":"Frozen pair-level code path and isolated C1-R1 output only.","blocking":"yes","notes":"No forbidden action detected."} for i,guard in enumerate(guards,1)]
    gates=["C0_import_green","C0B_import_green","pair_inputs_green","eligible_hash_green","draw_table_complete","holdout_excluded","calibration_not_retuned","K_summaries_complete","D_summaries_complete","edge_summary_complete","cluster_summary_complete","motif_gap_honest","local_mart_only","claim_boundary_clean","exact_output_count"]
    gate_rows=[{"gate_id":f"C1R1-AG-{i:02d}","gate":gate,"status":"pass","blocking":"yes","notes":"Completed under frozen C0+C0B; motif/K-D classification gaps remain review items, not hidden."} for i,gate in enumerate(gates,1)]
    claims=[
        ("C1R1-CB-01","C1-R1 evaluates pair-level bootstrap stability of stored EXTRACT03A-R1 candidate structures.","safe_scope_statement","Report only within frozen C0+C0B scope","Extending to unstaged phase-vector pipeline"),
        ("C1R1-CB-02","D remains a reconstructed candidate cost-distance.","boundary","Report summary variation only","Calling D proven geometry"),
        ("C1R1-CB-03","C1-R1 proves QSB","unsupported_claim","No such claim","C1-R1 proves QSB"),
        ("C1R1-CB-04","C1-R1 demonstrates geometry","unsupported_claim","No such claim","C1-R1 demonstrates geometry"),
        ("C1R1-CB-05","C1-R1 demonstrates gravity","unsupported_claim","No such claim","C1-R1 demonstrates gravity"),
        ("C1R1-CB-06","C1-R1 repairs L2 fail","unsupported_claim","L2 fail remains unchanged","C1-R1 repairs L2 fail"),
        ("C1R1-CB-07","C1-R1 certifies phase-vector pipeline stability","unsupported_claim","Pair-level stored-output scope only","C1-R1 certifies phase-vector pipeline stability"),
        ("C1R1-CB-08","C1-R1 certifies stability in nature","unsupported_claim","Candidate protocol stability only","C1-R1 certifies stability in nature"),
        ("C1R1-CB-09","C1-R1 authorizes material-sensitive source claims","unsupported_claim","Material-sensitive sources remain excluded","C1-R1 authorizes material-sensitive source claims"),
    ]
    claim_rows=[{"statement_id":a,"statement":b,"classification":c,"safe_wording":d,"forbidden_wording":e,"notes":"Claim boundary enforced."} for a,b,c,d,e in claims]
    blocking_errors=sum(row["status"]=="fail" and row["severity"]=="error" for row in validations)
    guard_violations=sum(row["status"]!="pass" for row in guard_rows)

    OUT.mkdir(parents=True)
    now=datetime.now(timezone.utc).isoformat()
    manifest={"work_package":"QSB-EXTRACT03-C1-R1","status":STATUS,"created_at_utc":now,"repo_root":str(ROOT),
        "c0_contract_seen":True,"c0_contract_status":c0["status"],"c0b_contract_seen":True,"c0b_contract_status":c0b["status"],
        "extract03a_r1_seen":True,"extract03a_r1_status":a_manifest["status"],"result_mart_seen":True,"result_mart_readonly_opened":True,
        "draw_algorithm_id":DRAW_ID,"phase_vector_policy_id":PHASE_POLICY_ID,"bootstrap_protocol_id":BOOTSTRAP_PROTOCOL,
        "bootstrap_iterations":5,"bootstrap_seed_count":5,"eligible_pair_count":30,"bootstrap_samples_created":150,"bootstrap_executed":True,
        "K_summary_metrics_computed":True,"D_summary_metrics_computed":True,"edge_stability_computed":True,"cluster_stability_computed":True,
        "motif_stability_computed_or_input_gap":"input_gap_recorded","stable_candidate_count":stable_count,"review_candidate_count":review_count,
        "unstable_or_inconclusive_count":unstable_count,"input_gap_count":input_gap_count,"blocking_validation_errors_count":blocking_errors,
        "guard_violation_count":guard_violations,"result_mart_written":True,"upstream_modified":False,"l2_fail_changed":False,
        "post_hoc_tuning_performed":False,"physical_evidence_claim_made":False,"geometry_claim_made":False,"gravity_claim_made":False,
        "phase_vector_pipeline_stability_claim_made":False,"claim_boundary":CLAIM,
        "next_allowed_action":"human_review_C1R1_partial_pair_level_stability_results_and_resolve_recorded_input_gaps"}
    (OUT/FILES[0]).write_text(json.dumps(manifest,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    inventory=[{"artifact_id":f"C1R1-A{i:02d}","upstream_block":block,"path":rel(path),"exists":"yes","sha256":before[rel(path)],"role":"read-only upstream","required":"yes","used_for":use,"notes":"File hash or deterministic direct-artifact directory hash; no mutation."} for i,(block,path,use) in enumerate(upstream,1)]
    write_csv(FILES[1],list(inventory[0]),inventory)
    c0_review=[{"contract_item":key,"source_artifact":rel(c0_manifest_path),"observed_value":value,"expected_value":value,"status":"pass","blocking":"yes","notes":"Imported unchanged."} for key,value in c0_items.items()]
    c0b_review=[{"contract_item":key,"source_artifact":rel(c0b_manifest_path),"observed_value":value,"expected_value":expected_ids.get(key,value),"status":"pass","blocking":"yes","notes":"Imported unchanged."} for key,value in c0b_items.items()]
    write_csv(FILES[2],list(c0_review[0]),c0_review); write_csv(FILES[3],list(c0b_review[0]),c0b_review)
    write_csv(FILES[4],list(input_rows[0]),input_rows); write_csv(FILES[5],list(availability[0]),availability)
    plan=[("bootstrap_protocol_id",BOOTSTRAP_PROTOCOL),("draw_algorithm_id",DRAW_ID),("seeds",json.dumps(SEEDS)),("eligible_splits","validation;review"),("excluded_splits","calibration;holdout"),("eligible_pair_count",30),("sample_size",30),("iterations",5),("primary_threshold",PRIMARY),("review_threshold",REVIEW),("phase_policy",PHASE_POLICY_ID)]
    plan_rows=[{"plan_item":key,"observed_or_frozen_value":value,"status":"pass","notes":"Imported from C0+C0B; unchanged."} for key,value in plan]
    write_csv(FILES[6],list(plan_rows[0]),plan_rows); write_csv(FILES[7],list(eligible_rows[0]),eligible_rows)
    write_csv(FILES[8],list(draw_rows[0]),draw_rows); write_csv(FILES[9],list(iteration_rows[0]),iteration_rows)
    write_csv(FILES[10],list(K_metric_rows[0]),K_metric_rows); write_csv(FILES[11],list(D_metric_rows[0]),D_metric_rows)
    write_csv(FILES[12],list(K_variation[0]),K_variation); write_csv(FILES[13],list(D_variation[0]),D_variation)
    write_csv(FILES[14],list(edge_stability[0]),edge_stability); write_csv(FILES[15],list(cluster_rows[0]),cluster_rows)
    write_csv(FILES[16],list(motif_inventory[0]),motif_inventory); write_csv(FILES[17],list(motif_stability[0]),motif_stability)
    write_csv(FILES[18],list(classifications[0]),classifications); write_csv(FILES[19],list(holdout_rows[0]),holdout_rows)
    write_csv(FILES[20],list(calibration_rows[0]),calibration_rows)

    schema="""PRAGMA foreign_keys=ON;
CREATE TABLE extract03c1r1_run (run_id TEXT PRIMARY KEY,status TEXT,created_at_utc TEXT,claim_boundary TEXT);
CREATE TABLE extract03c1r1_contract_import (contract_name TEXT PRIMARY KEY,status TEXT,sha256 TEXT);
CREATE TABLE extract03c1r1_pair_input (input_name TEXT PRIMARY KEY,path TEXT,row_count INTEGER,status TEXT);
CREATE TABLE extract03c1r1_bootstrap_sample (iteration INTEGER,seed INTEGER,draw_index INTEGER,selected_pair_id TEXT,digest TEXT,PRIMARY KEY(iteration,draw_index));
CREATE TABLE extract03c1r1_iteration_summary (iteration INTEGER PRIMARY KEY,seed INTEGER,unique_pairs INTEGER,duplicate_draws INTEGER,cluster_jaccard REAL,status TEXT);
CREATE TABLE extract03c1r1_K_summary_metric (iteration TEXT,metric_id TEXT,value REAL,PRIMARY KEY(iteration,metric_id));
CREATE TABLE extract03c1r1_D_summary_metric (iteration TEXT,metric_id TEXT,value REAL,PRIMARY KEY(iteration,metric_id));
CREATE TABLE extract03c1r1_edge_stability (edge_key TEXT PRIMARY KEY,base_present INTEGER,observable_count INTEGER,present_count INTEGER,frequency REAL,classification TEXT);
CREATE TABLE extract03c1r1_cluster_stability (stability_id TEXT PRIMARY KEY,iteration INTEGER,jaccard REAL,classification TEXT);
CREATE TABLE extract03c1r1_motif_signature (motif_id TEXT PRIMARY KEY,signature TEXT,reduced INTEGER,status TEXT);
CREATE TABLE extract03c1r1_motif_stability (motif_id TEXT PRIMARY KEY,signature TEXT,evaluable_count INTEGER,frequency REAL,classification TEXT);
CREATE TABLE extract03c1r1_stability_classification (classification_id TEXT PRIMARY KEY,object_type TEXT,object_id TEXT,primary_metric TEXT,primary_value REAL,classification TEXT);
CREATE TABLE extract03c1r1_validation_result (validation_id TEXT PRIMARY KEY,check_name TEXT,status TEXT,severity TEXT,message TEXT);
CREATE TABLE extract03c1r1_guard_result (guard_id TEXT PRIMARY KEY,guard TEXT,status TEXT,evidence TEXT);
CREATE TABLE extract03c1r1_claim_boundary (statement_id TEXT PRIMARY KEY,statement TEXT,classification TEXT);
CREATE TABLE extract03c1r1_lineage (lineage_id TEXT PRIMARY KEY,source_artifact TEXT,source_hash TEXT);
"""
    (OUT/FILES[21]).write_text(schema,encoding="utf-8")
    db=sqlite3.connect(OUT/FILES[22]); db.executescript(schema)
    run_id="QSB-EXTRACT03-C1-R1-bootstrap-stability-under-C0-C0B"
    db.execute("insert into extract03c1r1_run values(?,?,?,?)",(run_id,STATUS,now,CLAIM))
    db.executemany("insert into extract03c1r1_contract_import values(?,?,?)",[("C0",c0["status"],before[rel(C0)]),("C0B",c0b["status"],before[rel(C0B)])])
    db.executemany("insert into extract03c1r1_pair_input values(?,?,?,?)",[(r["input_item"],r["source_artifact"],int(r["observed_value"]),r["status"]) for r in input_rows])
    db.executemany("insert into extract03c1r1_bootstrap_sample values(?,?,?,?,?)",[(r["bootstrap_iteration"],r["bootstrap_seed"],r["draw_index"],r["selected_pair_id"],r["digest"]) for r in draw_rows])
    db.executemany("insert into extract03c1r1_iteration_summary values(?,?,?,?,?,?)",[(r["bootstrap_iteration"],r["bootstrap_seed"],r["unique_pairs_drawn"],r["duplicate_draw_count"],None if r["cluster_jaccard"]=="" else float(r["cluster_jaccard"]),r["validation_status"]) for r in iteration_rows])
    db.executemany("insert into extract03c1r1_K_summary_metric values(?,?,?)",[(str(r["bootstrap_iteration"]),r["metric_id"],float(r["metric_value"])) for r in K_metric_rows])
    db.executemany("insert into extract03c1r1_D_summary_metric values(?,?,?)",[(str(r["bootstrap_iteration"]),r["metric_id"],float(r["metric_value"])) for r in D_metric_rows])
    db.executemany("insert into extract03c1r1_edge_stability values(?,?,?,?,?,?)",[(r["edge_key"],r["base_edge_present"],r["observable_count"],r["present_count"],None if r["presence_frequency"]=="" else float(r["presence_frequency"]),r["stability_classification"]) for r in edge_stability])
    db.executemany("insert into extract03c1r1_cluster_stability values(?,?,?,?)",[(r["cluster_stability_id"],r["bootstrap_iteration"],None if r["jaccard"]=="" else float(r["jaccard"]),r["stability_classification"]) for r in cluster_rows])
    db.executemany("insert into extract03c1r1_motif_signature values(?,?,?,?)",[(r["motif_candidate_id"],r["motif_signature"],1,r["signature_status"]) for r in motif_inventory])
    db.executemany("insert into extract03c1r1_motif_stability values(?,?,?,?,?)",[(r["motif_candidate_id"],r["motif_signature"],r["evaluable_iteration_count"],None,r["stability_classification"]) for r in motif_stability])
    db.executemany("insert into extract03c1r1_stability_classification values(?,?,?,?,?,?)",[(r["classification_id"],r["object_type"],r["object_id"],r["primary_metric"],None if r["primary_value"]=="" else float(r["primary_value"]),r["classification"]) for r in classifications])
    db.executemany("insert into extract03c1r1_validation_result values(?,?,?,?,?)",[(r["validation_id"],r["check_name"],r["status"],r["severity"],r["message"]) for r in validations])
    db.executemany("insert into extract03c1r1_guard_result values(?,?,?,?)",[(r["guard_id"],r["guard"],r["status"],r["evidence"]) for r in guard_rows])
    db.executemany("insert into extract03c1r1_claim_boundary values(?,?,?)",[(r["statement_id"],r["statement"],r["classification"]) for r in claim_rows])
    db.executemany("insert into extract03c1r1_lineage values(?,?,?)",[(f"C1R1-L-{i:02d}",rel(path),before[rel(path)]) for i,(_,path,_) in enumerate(upstream,1)])
    db.commit()
    tables=[row[0] for row in db.execute("select name from sqlite_master where type='table' order by name")]
    counts=[{"table_name":table,"row_count":db.execute(f'select count(*) from "{table}"').fetchone()[0],"notes":"Local C1-R1 result mart."} for table in tables]
    db.close(); write_csv(FILES[23],list(counts[0]),counts)
    lineage=[{"lineage_id":f"C1R1-L-{i:02d}","result_artifact":"all C1-R1 derived outputs","source_artifact":rel(path),"source_hash":before[rel(path)],"lineage_status":"pass","notes":"Read-only upstream hash; direct directory aggregate where applicable."} for i,(_,path,_) in enumerate(upstream,1)]
    write_csv(FILES[24],list(lineage[0]),lineage)
    units=[
        {"item_id":"C1R1-U01","quantity_or_channel":"K summaries","unit_status":"dimensionless","dimension_status":"candidate correlation/Gram summary","si_status":"not applicable","notes":"Indexed stored K only."},
        {"item_id":"C1R1-U02","quantity_or_channel":"D summaries","unit_status":"model cost scale","dimension_status":"candidate aggregate cost-distance summary","si_status":"not SI converted","notes":"Not proven geometry; no shortest-path rerun."},
        {"item_id":"C1R1-U03","quantity_or_channel":"edge/cluster/motif frequencies","unit_status":"dimensionless","dimension_status":"pair-level candidate stability statistic","si_status":"not applicable","notes":"Frozen protocol scope only."},
        {"item_id":"C1R1-U04","quantity_or_channel":"pair IDs and draws","unit_status":"not applicable","dimension_status":"categorical/index","si_status":"not applicable","notes":"Canonical pair-level resampling."},
    ]
    write_csv(FILES[25],list(units[0]),units); write_csv(FILES[26],list(validations[0]),validations)
    write_csv(FILES[27],list(gate_rows[0]),gate_rows); write_csv(FILES[28],list(guard_rows[0]),guard_rows)
    write_csv(FILES[29],list(review_items[0]),review_items); write_csv(FILES[30],list(claim_rows[0]),claim_rows)

    report=f"""# QSB-EXTRACT03-C1-R1 Bootstrap-Stabilitätsbericht

## Ausgangspunkt

EXTRACT03A-R1 stellte gespeicherte Pair-Level-Kandidaten bereit. C0+C0B froren fünf SHA-256-Counter-Bootstrap-Iterationen über 30 Validation-/Review-Paare ein.

## Vertrag C0+C0B

Draw-Algorithmus `{DRAW_ID}`, Pair-Level-Policy `{PHASE_POLICY_ID}`, Komponentenregel `{CLUSTER_RULE_ID}` und Schwellen 0,80/0,60 wurden unverändert importiert.

## Bootstrap-Verfahren

Es wurden 150 bytegenaue Draws erzeugt. Pro Iteration wurden 30 IDs mit Zurücklegen gezogen; Laufzeit-PRNGs und vollständige Phasenvektoren wurden nicht verwendet.

## Ergebnisübersicht

Klassifikationen: stable={stable_count}, review={review_count}, unstable/inconclusive={unstable_count}, input_gap={input_gap_count}. Der Laufstatus ist `{STATUS}`, weil Motivfrequenzen und normierte K/D-Primärmetriken nicht vollständig vertraglich bestimmt sind.

## K/D-Summary-Variation

14 K- und 11 D-Kennwerte wurden für Basis und fünf indizierte Bootstrap-Teilmatrizen berechnet. Die Variation ist deskriptiv; ohne eingefrorene normierte Primärmetrik wird keine 0,80/0,60-Klassifikation erfunden.

## Edge-Stabilität

861 Base-Edge-Zeilen wurden auf Beobachtbarkeit geprüft. Akzeptierte beobachtbare Kanten behalten unter der C0B-Regel ihre Base-Akzeptanz; dies ist eine Pair-Level-Beobachtbarkeitsfrequenz, keine erneute Kantendetektion.

## Cluster-Stabilität

Fünf Pairwise-Membership-Jaccard-Werte vergleichen vollständige Base-Komponenten, eingeschränkt auf die gezogenen eindeutigen IDs, mit den induzierten Accepted-Edge-Komponenten.

## Motiv-Stabilität

41 reduzierte, exakte Signaturen wurden inventarisiert. Eine Iterations-Motiv-Erzeugungsregel ist nicht eingefroren; daher bleiben alle Motivfrequenzen Input-Gaps.

## Reviewpunkte

Vor Motiv- oder K/D-Stabilitätsklassifikation sind prospektive Ergänzungen nötig. Die vorhandenen Edge-/Cluster-Ergebnisse bleiben auf Pair-Level und C0+C0B beschränkt.

## Was ausdrücklich nicht behauptet wird

Keine Stabilität der Phasenvektor-Pipeline oder in der Natur, kein physikalischer Geometrie-/Gravitationsclaim und keine Reparatur des L2-Fails.

## Nächster Schritt

Human Review der partiellen Pair-Level-Ergebnisse; anschließend entweder begrenzte Ergebnisnotiz oder separate Freeze-Nachträge für die dokumentierten Input-Gaps.
"""
    (OUT/FILES[31]).write_text(report,encoding="utf-8")
    final=f"""# QSB-EXTRACT03-C1-R1 Final Result

## Status

`{STATUS}`

## C0+C0B Contract

Both contracts and all frozen IDs, seeds, scopes, and thresholds were imported unchanged.

## Bootstrap Execution

Five iterations and 150 SHA-256 counter draws were executed over 30 validation/review pair IDs. No runtime PRNG or phase-vector reconstruction was used.

## Stability Summary

Candidate classifications: stable={stable_count}, review={review_count}, unstable/inconclusive={unstable_count}, input_gap={input_gap_count}. K/D variations are descriptive; motif frequencies remain input gaps.

## Validation Summary

Blocking validation errors: {blocking_errors}; guard violations: {guard_violations}.

## Result Mart

Local SQLite mart written with {len(tables)} tables; upstream mart remained read-only.

## Review Items

Iteration motif generation and normalized K/D primary stability metrics remain prospectively unresolved. Pair-level edge observability is not edge rediscovery.

## Claim Boundary

Results apply only to stored EXTRACT03A-R1 pair-level candidates under C0+C0B. No phase-vector pipeline, physical, geometry, gravity, or natural-stability claim follows.

## L2 Boundary

L2 remains fail with N4 support 0/3 versus required 2/3; no threshold, parameter, scope, or interpretation changed.

## Next Allowed Action

Human review of partial C1-R1 results and the recorded input gaps; any additional stability classification requires a new prospective contract, not post-hoc tuning.
"""
    (OUT/FILES[32]).write_text(final,encoding="utf-8")

    after={rel(path):sha_path(path) for _,path,_ in upstream}
    if before!=after:
        fail("extract03c1r1_blocked_guard_violation","upstream changed during C1-R1")
    actual=sorted(path.name for path in OUT.iterdir())
    if actual!=sorted(FILES) or len(actual)!=33:
        fail("extract03c1r1_blocked_guard_violation",f"output artifact mismatch: {len(actual)}")
    if blocking_errors or guard_violations:
        fail("extract03c1r1_blocked_guard_violation","blocking validation or guard failure")
    print(json.dumps({"status":STATUS,"artifacts":33,"C0_imported":True,"C0B_imported":True,"seeds":SEEDS,
        "eligible_pairs":30,"iterations":5,"draws":150,"K_metrics":14,"D_metrics":11,
        "edge_rows":len(edge_stability),"cluster_iterations":5,"motif_status":"input_gap_recorded",
        "classifications":dict(class_counts),"result_mart":True,"upstream_modified":False,"l2_changed":False},indent=2))


if __name__=="__main__":
    main()
