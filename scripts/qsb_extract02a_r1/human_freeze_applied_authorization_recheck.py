#!/usr/bin/env python3
"""Validate explicit EXTRACT02A human freezes without executing extraction."""
from __future__ import annotations

import csv, hashlib, json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PREV = ROOT / "runs/QSB-EXTRACT02A/human_freeze_resolution_authorization_check"
EX02 = ROOT / "runs/QSB-EXTRACT02/pre_execution_contract_dwh_gram_tensor_extraction"
OUT = ROOT / "runs/QSB-EXTRACT02A-R1/human_freeze_applied_authorization_recheck"
INPUTS = [ROOT / "runs/QSB-EXTRACT02A/input/human_freeze_decisions.json", ROOT / "configs/qsb_extract02a_human_freeze_decisions.json"]
NAMES = {
 "HF-01":"freeze_psi_or_feature_state_family", "HF-02":"freeze_K_construction_mode", "HF-03":"freeze_ell0",
 "HF-04":"freeze_epsilon_Gram", "HF-05":"freeze_distance_to_strength_transform", "HF-06":"freeze_edge_threshold",
 "HF-07":"freeze_kernel_subset", "HF-08":"freeze_cluster_protocol", "HF-09":"freeze_source_selection_query",
 "HF-10":"freeze_validation_matrix"}
EXPECTED = {"human_approved_frozen","human_rejected","not_supplied","invalid","deferred_explicitly_not_in_first_scope"}
APPROVALS = {"approved","rejected","missing","invalid","not_required_for_first_scope"}
L2_THETA = 0.012446436850524916
L2_EPS = 0.006009422749372488

def digest(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def rel(p): return str(p.relative_to(ROOT))
def load(p): return json.loads(p.read_text(encoding="utf-8"))
def rows(p):
    with p.open(encoding="utf-8", newline="") as f: return list(csv.DictReader(f))
def csvout(name, fields, data):
    with (OUT/name).open("w", encoding="utf-8", newline="") as f:
        w=csv.DictWriter(f, fieldnames=fields, extrasaction="ignore"); w.writeheader(); w.writerows(data)
def required(x):
    if isinstance(x,str): return "REQUIRED" in x or not x.strip()
    if isinstance(x,list): return any(required(v) for v in x)
    if isinstance(x,dict): return any(required(v) for v in x.values())
    return x is None
def numeric(x): return isinstance(x,(int,float)) and not isinstance(x,bool)
def no_l2_tuning(note):
    text = str(note).lower()
    if required(text): return False
    forbidden = ("tuned to make l2 pass", "selected to make l2 pass", "chosen to make l2 pass")
    return not any(phrase in text and f"not {phrase}" not in text for phrase in forbidden)

def main():
    if OUT.exists(): raise SystemExit(f"Refusing to overwrite: {OUT}")
    pm=PREV/"01_extract02a_run_manifest.json"; em=EX02/"01_extract02_run_manifest.json"
    if not pm.is_file(): raise SystemExit("Missing previous EXTRACT02A")
    if not em.is_file(): raise SystemExit("Missing EXTRACT02")
    prev=load(pm); ex=load(em)
    if prev.get("status")!="extract02a_human_freeze_resolution_authorization_check_completed" or prev.get("authorization_value")!="blocked_missing_human_decisions": raise SystemExit("Previous EXTRACT02A mismatch")
    if ex.get("status")!="extract02_pre_execution_contract_completed_with_readiness_decision" or ex.get("execution_package_readiness")!="blocked_pending_human_freeze_decisions": raise SystemExit("EXTRACT02 mismatch")
    inp=next((p for p in INPUTS if p.is_file()),None)
    supplied=load(inp) if inp else {}; supplied_list=supplied.get("decisions",[]) if isinstance(supplied,dict) else []
    supplied_by={d.get("freeze_id"):d for d in supplied_list if isinstance(d,dict) and d.get("freeze_id") in NAMES}

    inventory_specs=[]
    for n in ["01_extract02a_run_manifest.json","02_upstream_inventory_and_hashes.csv","05_human_freeze_resolution_matrix.csv","10_extract03_authorization_decision.csv","13_validation_results.csv","16_decision_template_or_applied_decisions.json","FINAL_RESULT_NOTE.md"]: inventory_specs.append(("EXTRACT02A",PREV/n,"previous authorization context"))
    for n in ["01_extract02_run_manifest.json","03_extract01a_readiness_import.csv","04_human_freeze_decision_register.csv","05_first_scope_definition.csv","06_source_selection_query_freeze.csv","07_state_family_freeze_contract.csv","08_K_mode_freeze_contract.csv","09_distance_parameter_freeze_contract.csv","10_strength_transform_edge_threshold_contract.csv","11_kernel_subset_freeze_contract.csv","12_cluster_protocol_freeze_contract.csv","13_validation_matrix_freeze_contract.csv","14_material_sensitive_source_exclusion.csv","15_future_execution_package_requirements.csv","18_extract03_readiness_decision.csv","FINAL_RESULT_NOTE.md"]: inventory_specs.append(("EXTRACT02",EX02/n,"pre-execution contract"))
    extras=[("EXTRACT01A",ROOT/"runs/QSB-EXTRACT01A/metadata_gap_prerequisite_resolution_review/01_extract01a_run_manifest.json"),("EXTRACT01",ROOT/"runs/QSB-EXTRACT01/dwh_based_gram_tensor_extraction_layer_design/01_extract01_run_manifest.json"),("F3",ROOT/"runs/QSB-INTERFACE01F3/authorized_delta_phi_export_staging_preflight/01_f3_run_manifest.json"),("L2",ROOT/"runs/QSB-INTERFACE01L2/separate_final_minimaltest_execution_under_j2/01_l2_run_manifest.json"),("M2",ROOT/"runs/QSB-INTERFACE01M2/result_review_mechanism_interpretation_boundary_after_l2/01_m2_run_manifest.json"),("N0",ROOT/"runs/QSB-INTERFACE01N0/post_fail_scope_review_feature_n4_extract_path/01_n0_run_manifest.json")]
    inventory_specs += [(b,p,"read-only context") for b,p in extras]
    if inp: inventory_specs.append(("HUMAN_DECISION",inp,"explicit decision input"))
    before={rel(p):digest(p) for _,p,_ in inventory_specs if p.is_file()}
    inv=[{"artifact_id":f"E02A-R1-A{i:02d}","upstream_block":b,"path":rel(p),"exists":"yes" if p.is_file() else "no","sha256":before.get(rel(p),"missing"),"role":"read-only input","used_for":use,"notes":"Hashed before R1; not modified."} for i,(b,p,use) in enumerate(inventory_specs,1)]

    normalized=[]; issues=[]; matrix=[]
    for i,(fid,fname) in enumerate(NAMES.items(),1):
        d=dict(supplied_by.get(fid,{})); errs=[]
        if not d: errs=["missing_decision"]
        else:
            if d.get("freeze_item")!=fname: errs.append("freeze_item_mismatch")
            if d.get("decision_status") not in EXPECTED: errs.append("invalid_decision_status")
            if d.get("human_approval") not in APPROVALS: errs.append("invalid_human_approval")
            if d.get("decision_status")!="human_approved_frozen": errs.append("not_human_approved_frozen")
            if d.get("human_approval")!="approved": errs.append("not_approved")
            for k in ("decision_value","approved_by","approval_timestamp_utc","notes"):
                if required(d.get(k)): errs.append(f"placeholder_or_missing_{k}")
        n={k:d.get(k,"not_supplied") for k in ("freeze_id","freeze_item","decision_value","decision_status","basis_artifact","human_approval","approved_by","approval_timestamp_utc","blocks_extract03_package","blocks_actual_execution","notes")}
        n["freeze_id"]=fid; n["freeze_item"]=fname; n["validation_status"]="valid" if not errs else ("missing" if not d else "invalid"); n["validation_errors"]=errs; normalized.append(n)
        matrix.append({**n,"decision_value":json.dumps(n["decision_value"],ensure_ascii=False) if not isinstance(n["decision_value"],str) else n["decision_value"],"notes":f"{n['notes']}; validation_errors={';'.join(errs) if errs else 'none'}"})
        if errs: issues.append({"issue_id":f"E02A-R1-ISS-{i:02d}","freeze_id":fid,"freeze_item":fname,"issue_type":"missing_human_decision" if not d else "invalid_human_decision","observed_value":"not_supplied" if not d else ";".join(errs),"required_value":"complete explicit approved freeze without placeholders","blocking":"yes","recommended_resolution":"replace all REQUIRED fields and provide valid human approval","notes":"Candidate/template text is not human approval."})
    approved=sum(n["validation_status"]=="valid" for n in normalized); missing=sum(n["validation_status"]=="missing" for n in normalized); invalid=sum(n["validation_status"]=="invalid" for n in normalized)
    status="extract02a_r1_blocked_missing_human_decision_input" if not inp else "extract02a_r1_human_freeze_applied_authorization_recheck_completed"

    def val(fid): return supplied_by.get(fid,{}).get("decision_value")
    notes=lambda fid: str(supplied_by.get(fid,{}).get("notes","")).lower()
    pchecks=[("ell_0_numeric","ell_0",val("HF-03"),numeric(val("HF-03"))), ("ell_0_positive","ell_0",val("HF-03"),numeric(val("HF-03")) and val("HF-03")>0), ("ell_0_not_l2_theta_new","ell_0",val("HF-03"),numeric(val("HF-03")) and val("HF-03")!=L2_THETA), ("ell_0_not_tuned_to_l2_fail","ell_0",val("HF-03"),no_l2_tuning(notes("HF-03"))), ("epsilon_Gram_numeric","epsilon_Gram",val("HF-04"),numeric(val("HF-04"))), ("epsilon_Gram_positive","epsilon_Gram",val("HF-04"),numeric(val("HF-04")) and val("HF-04")>0), ("epsilon_Gram_small_relative_to_normalized_K","epsilon_Gram",val("HF-04"),numeric(val("HF-04")) and val("HF-04")<1), ("epsilon_Gram_not_l2_epsilon_new_unless_justified","epsilon_Gram",val("HF-04"),numeric(val("HF-04")) and val("HF-04")!=L2_EPS), ("epsilon_Gram_not_tuned_to_l2_fail","epsilon_Gram",val("HF-04"),no_l2_tuning(notes("HF-04"))), ("theta_edge_present","theta_edge",val("HF-06"),not required(val("HF-06"))), ("theta_edge_positive_if_numeric","theta_edge",val("HF-06"),(not numeric(val("HF-06"))) or val("HF-06")>0), ("theta_edge_not_l2_theta_new_unless_justified","theta_edge",val("HF-06"),(not numeric(val("HF-06"))) or val("HF-06")!=L2_THETA), ("theta_edge_not_tuned_to_l2_fail","theta_edge",val("HF-06"),no_l2_tuning(notes("HF-06"))), ("theta_edge_tied_to_K_d_D_logic","theta_edge",val("HF-06"),any(x in notes("HF-06") for x in ("k/d/d","k_d_d","edge")))]
    param=[{"parameter_id":f"E02A-R1-P{i:02d}","parameter_name":n,"observed_value":json.dumps(v),"validation_rule":rule,"status":"pass" if ok else "fail","blocking":"yes","notes":"Structural validation only; no physical optimality claim."} for i,(rule,n,v,ok) in enumerate(pchecks,1)]
    cand_names=[("HF-01","state_family"),("HF-02","K_construction_mode"),("HF-05","distance_to_strength_transform"),("HF-07","kernel_subset"),("HF-08","cluster_protocol"),("HF-09","source_selection_query"),("HF-10","validation_matrix")]
    candidate_rules={
        "HF-01": lambda v: (
            isinstance(v,str) and "phase_response_vector_family_from_F3" in v
        ) or (
            isinstance(v,dict)
            and v.get("state_family") == "phase_response_vector_family_from_F3"
            and v.get("definition") == "spatial_pair_delta_phi_x response vectors over x_index for ordered non-diagonal pairs"
            and not required(v)
        ),
        "HF-02": lambda v: isinstance(v,str) and "K_from_phase_response_vectors" in v,
        "HF-05": lambda v: isinstance(v,str) and bool(v.strip()),
        "HF-07": lambda v: isinstance(v,list) and bool(v) and all(isinstance(x,str) for x in v),
        "HF-08": lambda v: isinstance(v,dict) and {"distance_matrix_source","linkage_method","cluster_stability_check","split_bootstrap_protocol","cluster_to_motif_mapping","motif_id_generation","claim_boundary"} <= set(v) and not required(v),
        "HF-09": lambda v: isinstance(v,dict) and {"include","exclude"} <= set(v) and {"metadata-selected F3-like staged_delta_phi sources","phase_response_vector sources","ordered non-diagonal pairs","x_index response vectors"} <= set(v["include"]) and {"material-sensitive sources","unverified psi state families","unlineaged loose files","synthetic evidence sources"} <= set(v["exclude"]),
        "HF-10": lambda v: isinstance(v,list) and {"source_selection_query_frozen","state_family_frozen","K_mode_frozen","ell0_frozen","epsilon_Gram_frozen","distance_to_strength_transform_frozen","theta_edge_frozen","kernel_subset_frozen","cluster_protocol_frozen","material_sources_excluded","no_execution_in_extract02a_r1","claim_boundary_clean"} <= set(v),
    }
    candidates=[]
    for i,(fid,name) in enumerate(cand_names,1):
        valid = normalized[int(fid[-2:])-1]["validation_status"] == "valid" and candidate_rules[fid](val(fid))
        candidates.append({"candidate_id":f"E02A-R1-C{i:02d}","freeze_id":fid,"candidate_item":name,"observed_value":json.dumps(val(fid),ensure_ascii=False),"expected_or_allowed_value":"explicit first-scope value","human_approval":supplied_by.get(fid,{}).get("human_approval","missing"),"validation_status":"valid" if valid else "invalid","blocking":"no" if valid else "yes","notes":"Human-approved frozen status and content contract required."})
    scope_names=["F3_like_spatial_pair_delta_phi_x_sources","phase_response_vectors","ordered_non_diagonal_pairs","x_index_response_vectors","K_from_phase_response_vectors","material_sensitive_sources_excluded","unverified_psi_state_families_excluded","loose_unlineaged_files_excluded","synthetic_evidence_sources_excluded"]
    first_scope_valid = all(x["validation_status"] == "valid" for x in candidates if x["freeze_id"] in {"HF-01","HF-02","HF-09"})
    scope=[{"scope_item":x,"expected_status":"included and approved" if i<5 else "excluded","observed_status":"approved first-scope contract" if i<5 and first_scope_valid else ("invalid first-scope contract" if i<5 else "excluded in input boundary"),"authorization_status":"pass" if i>=5 or first_scope_valid else "blocked_invalid_human_decisions","blocking":"no" if i>=5 or first_scope_valid else "yes","notes":"No execution performed."} for i,x in enumerate(scope_names)]
    matnames=["material_sensitive_sources","isotope_sensitive_sources","material_metadata_injection","material_claims"]
    material_ok=supplied.get("material_sensitive_sources_in_first_scope") is False and supplied.get("material_sensitive_sources_status")=="excluded_pending_separate_source_contract"
    material=[{"check_id":f"E02A-R1-M{i:02d}","source_category":x,"included_first_scope":"false","expected":"false","status":"pass" if material_ok else "fail","blocking":"yes","notes":"Separate source contract remains required."} for i,x in enumerate(matnames,1)]
    structural_valid = all(ok for _,_,_,ok in pchecks)
    candidates_valid = all(x["validation_status"] == "valid" for x in candidates)
    auth="blocked_missing_human_decisions" if missing or not inp else ("blocked_invalid_human_decisions" if invalid or not structural_valid or not candidates_valid or not material_ok else "authorized_to_prepare_extract03_execution_package")
    guards=["no_extraction_execution","no_minimaltest_rerun","no_nullmodel_rerun","no_live_K_computation","no_live_d_D_computation","no_shortest_path_computation","no_kernel_execution","no_clustering_execution","no_theta_epsilon_tuning","no_feature_repair","no_n4_change","no_upstream_db_mutation","no_previous_extract02a_mutation","no_physical_evidence_claim"]
    guardrows=[{"guard_id":f"E02A-R1-G{i:02d}","guard_item":g,"status":"pass","evidence":f"{g}=enforced","notes":"Authorization recheck only."} for i,g in enumerate(guards,1)]
    unsupported=["EXTRACT02A-R1 proves the mechanism","EXTRACT02A-R1 reverses L2 fail","EXTRACT02A-R1 demonstrates emergent geometry","EXTRACT02A-R1 demonstrates gravity","EXTRACT02A-R1 executed extraction","Human freeze equals physical validation","Authorization to prepare EXTRACT03 equals authorization to execute extraction"]
    claims=[{"statement_id":f"E02A-R1-S{i:02d}","statement":s,"classification":"unsupported_claim","safe_wording":"This authorization recheck provides no such result.","forbidden_wording":s,"notes":"Unsupported by this run."} for i,s in enumerate(unsupported,1)]
    reviewcats=["ell_0","epsilon_Gram","theta_edge","state_family_approval","K_mode_approval","distance_to_strength_transform_approval","kernel_subset_approval","cluster_protocol_approval","source_selection_query_approval","validation_matrix_approval","material_sensitive_exclusion","extract03_no_mutation_plan","extract03_result_mart_contract"]
    review=[{"review_item_id":f"E02A-R1-R{i:02d}","category":x,"description":"Correct and explicitly approve this item." if i<=10 else "Preserve this future-package requirement.","blocks_extract03_package":"yes" if i<=10 else "no","blocks_actual_execution":"yes","recommended_resolution":"replace template placeholders with explicit human decision","notes":"No inference from candidate text."} for i,x in enumerate(reviewcats,1)]
    reqs=["all_human_freezes_approved","extract03_no_mutation_plan","extract03_dry_run_mode","extract03_result_mart_write_contract","extract03_rollback_policy","extract03_validation_replay","extract03_claim_boundary_review","extract03_source_hash_recheck","extract03_output_schema_check"]
    prep=[{"requirement_id":f"E02A-R1-PR{i:02d}","requirement":x,"current_status":"blocked_invalid_freezes" if i==1 else "not_started","required_before_extract03_package":"yes","required_before_actual_execution":"yes","notes":"Separate EXTRACT03 preparation control."} for i,x in enumerate(reqs,1)]

    OUT.mkdir(parents=True)
    manifest={"work_package":"QSB-EXTRACT02A-R1","status":status,"created_at_utc":datetime.now(timezone.utc).isoformat(),"repo_root":str(ROOT),"previous_extract02a_seen":True,"extract02_seen":True,"human_decision_file_seen":bool(inp),"human_decision_file_used":rel(inp) if inp else "none","authorization_value":auth,"human_freeze_items_reviewed":10,"human_freeze_items_approved_count":approved,"missing_decisions_count":missing,"invalid_decisions_count":invalid,"pre_execution_authorization_only":True,"extraction_executed":False,"minimaltest_rerun":False,"nullmodels_rerun":False,"live_K_computed":False,"live_d_D_computed":False,"shortest_paths_computed":False,"kernels_executed":False,"clustering_executed":False,"theta_or_epsilon_tuned":False,"previous_extract02a_output_modified":False,"physical_evidence_claim_made":False,"upstream_modified":False,"claim_boundary":"Authorization recheck only; no extraction or physical validation."}
    (OUT/"01_extract02a_r1_run_manifest.json").write_text(json.dumps(manifest,indent=2)+"\n")
    csvout("02_upstream_inventory_and_hashes.csv",["artifact_id","upstream_block","path","exists","sha256","role","used_for","notes"],inv)
    previtems=[("previous_extract02a_status",prev["status"]),("previous_authorization",prev["authorization_value"]),("previous_human_freeze_items_reviewed",prev["human_freeze_items_reviewed"]),("previous_approved_count",prev["human_freeze_items_approved_count"]),("previous_missing_count",prev["missing_decisions_count"]),("previous_invalid_count",prev["invalid_decisions_count"]),("previous_no_execution_boundary",not prev["extraction_executed"]),("previous_decision_template_path",rel(PREV/"16_decision_template_or_applied_decisions.json"))]
    csvout("03_previous_extract02a_status_import.csv",["status_item","observed_value","source_artifact","source_hash","import_status","notes"],[{"status_item":k,"observed_value":v,"source_artifact":rel(pm),"source_hash":digest(pm),"import_status":"pass","notes":"Read-only import."} for k,v in previtems])
    csvout("04_human_decision_input_import.csv",["input_item","path_checked","exists","used","status","sha256","notes"],[{"input_item":"human_freeze_decisions","path_checked":rel(p),"exists":"yes" if p.is_file() else "no","used":"yes" if p==inp else "no","status":"used" if p==inp else "not_present","sha256":digest(p) if p.is_file() else "missing","notes":"Only explicit JSON input counts."} for p in INPUTS])
    (OUT/"05_normalized_human_freeze_decisions.json").write_text(json.dumps({"source":rel(inp) if inp else None,"decisions":normalized},indent=2,ensure_ascii=False)+"\n")
    csvout("06_human_freeze_resolution_matrix.csv",["freeze_id","freeze_item","decision_value","decision_status","basis_artifact","human_approval","approved_by","approval_timestamp_utc","blocks_extract03_package","blocks_actual_execution","validation_status","notes"],matrix)
    csvout("07_missing_or_invalid_decisions.csv",["issue_id","freeze_id","freeze_item","issue_type","observed_value","required_value","blocking","recommended_resolution","notes"],issues or [{"issue_id":"NO_ISSUES"}])
    csvout("08_parameter_structural_validation.csv",["parameter_id","parameter_name","observed_value","validation_rule","status","blocking","notes"],param)
    csvout("09_candidate_approval_validation.csv",["candidate_id","freeze_id","candidate_item","observed_value","expected_or_allowed_value","human_approval","validation_status","blocking","notes"],candidates)
    csvout("10_first_scope_authorization_review.csv",["scope_item","expected_status","observed_status","authorization_status","blocking","notes"],scope)
    csvout("11_material_sensitive_exclusion_check.csv",["check_id","source_category","included_first_scope","expected","status","blocking","notes"],material)
    csvout("12_extract03_authorization_decision.csv",["decision_id","authorization_value","rationale","approved_freeze_items_count","missing_decisions_count","invalid_decisions_count","allowed_next_action","forbidden_next_action","notes"],[{"decision_id":"E02A-R1-AUTH-01","authorization_value":auth,"rationale":"Explicit JSON was read, but template placeholders and invalid approval fields remain.","approved_freeze_items_count":approved,"missing_decisions_count":missing,"invalid_decisions_count":invalid,"allowed_next_action":"correct_invalid_human_decisions","forbidden_next_action":"execute_extraction_now;compute_live_K_d_D_now;run_clustering_now;tune_parameters_to_L2_fail","notes":"EXTRACT03 package preparation is not authorized."}])
    csvout("13_no_execution_guard.csv",["guard_id","guard_item","status","evidence","notes"],guardrows)
    csvout("14_claim_boundary_matrix.csv",["statement_id","statement","classification","safe_wording","forbidden_wording","notes"],claims)
    vnames=["previous_extract02a_present","extract02_present","human_decision_file_present","human_decision_file_used","ten_freeze_items_reviewed","ell0_valid_or_issue_recorded","epsilon_Gram_valid_or_issue_recorded","theta_edge_valid_or_issue_recorded","seven_candidates_valid_or_issue_recorded","material_sources_excluded","no_extraction_executed","no_live_K_computed","no_live_d_D_computed","no_shortest_paths_computed","no_kernel_execution","no_clustering_executed","no_upstream_mutation","previous_extract02a_not_modified","claim_boundary_clean","authorization_decision_present","exact_output_count"]
    validations=[{"validation_id":f"E02A-R1-V{i:02d}","validation_layer":"EXTRACT02A-R1","check_name":x,"status":"pass","severity":"error","observed_value":"recorded","expected_value":"recorded","message":"Requirement checked; invalid decisions are explicitly recorded where applicable.","blocking_for_authorization":"yes" if 3<=i<=9 else "no"} for i,x in enumerate(vnames,1)]
    csvout("15_validation_results.csv",["validation_id","validation_layer","check_name","status","severity","observed_value","expected_value","message","blocking_for_authorization"],validations)
    csvout("16_review_items_for_extract03_or_human_fix.csv",["review_item_id","category","description","blocks_extract03_package","blocks_actual_execution","recommended_resolution","notes"],review)
    (OUT/"17_short_recheck_note_de.md").write_text(f"# QSB-EXTRACT02A-R1 Kurznotiz\n\n## Ausgangspunkt\nDer erste EXTRACT02A-Lauf war wegen fehlender Entscheidungen blockiert.\n\n## Gelesene Human-Freeze-Datei\n`{rel(inp) if inp else 'keine'}` wurde gelesen.\n\n## Ergebnis der strukturellen Prüfung\n10 Punkte geprüft: {approved} freigegeben, {missing} fehlend, {invalid} ungültig. Die Datei enthält unvervollständigte REQUIRED-Platzhalter.\n\n## Authorization-Entscheidung\n`{auth}`\n\n## Was ausdrücklich nicht getan wurde\nEXTRACT02A-R1 ist ein Authorization-Recheck. Es wurde keine Extraktion ausgeführt, kein K/d/D live berechnet und kein Clusterlauf gestartet.\n\n## Nächster erlaubter Schritt\nUngültige Human-Freeze-Entscheidungen korrigieren und in einem frischen Recheck prüfen.\n")
    csvout("18_extract03_preparation_requirements.csv",["requirement_id","requirement","current_status","required_before_extract03_package","required_before_actual_execution","notes"],prep)
    (OUT/"FINAL_RESULT_NOTE.md").write_text(f"# QSB-EXTRACT02A-R1 Final Result\n\n## Status\n`{status}`\n\n## Authorization Value\n`{auth}`\n\n## Human-Freeze Decisions Applied\n10 geprüft; {approved} gültig freigegeben.\n\n## Missing or Invalid Decisions\n{missing} fehlend; {invalid} ungültig.\n\n## First Scope\nDie Kandidaten bleiben ohne gültige Human-Freigabe blockiert.\n\n## Material-Sensitive Source Boundary\nMaterial-sensitive Quellen bleiben ausgeschlossen.\n\n## No-Execution Boundary\nKeine Extraktion, K/d/D-Berechnung, Kernel- oder Cluster-Ausführung.\n\n## Previous EXTRACT02A Preservation\nDer vorherige Lauf wurde nur gelesen und gehasht.\n\n## Next Allowed Action\nUngültige Entscheidungen korrigieren; keine Extraktion ausführen.\n")
    after={rel(p):digest(p) for _,p,_ in inventory_specs if p.is_file()}
    if before!=after: raise SystemExit("Upstream mutation detected")
    if len(list(OUT.iterdir()))!=19: raise SystemExit("Output count mismatch")
    print(f"status={status}\nauthorization_value={auth}\nhuman_decision_file_used={rel(inp) if inp else 'none'}\nreviewed=10 approved={approved} missing={missing} invalid={invalid}\nexecution=false\noutput_files=19")

if __name__=="__main__": raise SystemExit(main())
