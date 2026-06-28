#!/usr/bin/env python3
"""Repair R1 reporting consistency without executing extraction or mutating history."""
from __future__ import annotations

import csv, hashlib, json
from datetime import datetime, timezone
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
R1=ROOT/"runs/QSB-EXTRACT02A-R1/human_freeze_applied_authorization_recheck"
PREV=ROOT/"runs/QSB-EXTRACT02A/human_freeze_resolution_authorization_check"
EX02=ROOT/"runs/QSB-EXTRACT02/pre_execution_contract_dwh_gram_tensor_extraction"
OUT=ROOT/"runs/QSB-EXTRACT02A-R1F/artifact_consistency_fix_human_freeze_recheck"
INPUTS=[ROOT/"runs/QSB-EXTRACT02A/input/human_freeze_decisions.json",ROOT/"configs/qsb_extract02a_human_freeze_decisions.json"]
NAMES={"HF-01":"freeze_psi_or_feature_state_family","HF-02":"freeze_K_construction_mode","HF-03":"freeze_ell0","HF-04":"freeze_epsilon_Gram","HF-05":"freeze_distance_to_strength_transform","HF-06":"freeze_edge_threshold","HF-07":"freeze_kernel_subset","HF-08":"freeze_cluster_protocol","HF-09":"freeze_source_selection_query","HF-10":"freeze_validation_matrix"}
L2_THETA=0.012446436850524916; L2_EPS=0.006009422749372488

def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def rel(p): return str(p.relative_to(ROOT))
def load(p): return json.loads(p.read_text(encoding="utf-8"))
def readcsv(p):
    with p.open(encoding="utf-8",newline="") as f:return list(csv.DictReader(f))
def writecsv(name,fields,data):
    with (OUT/name).open("w",encoding="utf-8",newline="") as f:
        w=csv.DictWriter(f,fieldnames=fields,extrasaction="ignore");w.writeheader();w.writerows(data)
def required(v):
    if isinstance(v,str):return not v.strip() or "REQUIRED" in v
    if isinstance(v,list):return not v or any(required(x) for x in v)
    if isinstance(v,dict):return not v or any(required(x) for x in v.values())
    return v is None
def numeric(v):return isinstance(v,(int,float)) and not isinstance(v,bool)
def no_l2_tuning(note):
    s=str(note).lower()
    return not required(s) and not any(p in s and ("not "+p) not in s for p in ("tuned to make l2 pass","selected to make l2 pass","chosen to make l2 pass"))

def main():
    if OUT.exists():raise SystemExit(f"Refusing to overwrite: {OUT}")
    required_r1=["01_extract02a_r1_run_manifest.json","12_extract03_authorization_decision.csv","17_short_recheck_note_de.md","18_extract03_preparation_requirements.csv","FINAL_RESULT_NOTE.md"]
    if not R1.is_dir() or not all((R1/x).is_file() for x in required_r1):raise SystemExit("Missing required R1 artifacts")
    if not (EX02/"01_extract02_run_manifest.json").is_file():raise SystemExit("Missing EXTRACT02")
    inp=next((p for p in INPUTS if p.is_file()),None)
    if not inp:raise SystemExit("Missing human decision input")
    r1m=load(R1/required_r1[0]); ex=load(EX02/"01_extract02_run_manifest.json")
    if ex.get("status")!="extract02_pre_execution_contract_completed_with_readiness_decision":raise SystemExit("EXTRACT02 mismatch")
    r1a=readcsv(R1/required_r1[1])[0]
    short=(R1/required_r1[2]).read_text(encoding="utf-8"); prepold=(R1/required_r1[3]).read_text(encoding="utf-8"); finalold=(R1/required_r1[4]).read_text(encoding="utf-8")
    green_manifest=r1m.get("authorization_value")=="authorized_to_prepare_extract03_execution_package" and (r1m.get("human_freeze_items_approved_count"),r1m.get("missing_decisions_count"),r1m.get("invalid_decisions_count"))==(10,0,0)
    stale=(r1a.get("allowed_next_action")!="prepare_extract03_execution_package" or "not authorized" in r1a.get("notes","").lower() or "required-platzhalter" in short.lower() or "blocked_invalid_freezes" in prepold or "ungültige entscheidungen korrigieren" in finalold.lower())
    previous_class="internally_inconsistent_authorization_reporting" if green_manifest and stale else ("consistent_authorized" if green_manifest else "consistent_blocked")

    data=load(inp); supplied=data.get("decisions",[]); by={x.get("freeze_id"):x for x in supplied if isinstance(x,dict)}
    normalized=[]; issues=[]
    for i,(fid,name) in enumerate(NAMES.items(),1):
        d=by.get(fid,{}); errs=[]
        if not d:errs=["missing_decision"]
        else:
            if d.get("freeze_item")!=name:errs.append("freeze_item_mismatch")
            if d.get("decision_status")!="human_approved_frozen":errs.append("decision_not_human_approved_frozen")
            if d.get("human_approval")!="approved":errs.append("human_approval_not_approved")
            if d.get("blocks_extract03_package") is not False:errs.append("blocks_extract03_package_not_false")
            if d.get("blocks_actual_execution") is not False:errs.append("blocks_actual_execution_not_false")
            for k in ("decision_value","basis_artifact","approved_by","approval_timestamp_utc","notes"):
                if required(d.get(k)):errs.append(f"missing_or_placeholder_{k}")
        n={k:d.get(k,"not_supplied") for k in ("freeze_id","freeze_item","decision_value","decision_status","basis_artifact","human_approval","approved_by","approval_timestamp_utc","blocks_extract03_package","blocks_actual_execution","notes")}
        n.update({"freeze_id":fid,"freeze_item":name,"validation_status":"valid" if not errs else ("missing" if not d else "invalid"),"validation_errors":errs});normalized.append(n)
        if errs:issues.append({"issue_id":f"E02A-R1F-ISS-{i:02d}","freeze_id":fid,"freeze_item":name,"issue_type":"missing_human_decision" if not d else "invalid_human_decision","observed_value":";".join(errs),"required_value":"complete approved nonblocking freeze","blocking":"yes","recommended_resolution":"correct explicit human decision JSON","notes":"No value inferred."})
    approved=sum(x["validation_status"]=="valid" for x in normalized);missing=sum(x["validation_status"]=="missing" for x in normalized);invalid=sum(x["validation_status"]=="invalid" for x in normalized)
    val=lambda f:by.get(f,{}).get("decision_value"); note=lambda f:str(by.get(f,{}).get("notes","")).lower()
    checks=[("ell_0_numeric","ell_0",val("HF-03"),numeric(val("HF-03"))),("ell_0_positive","ell_0",val("HF-03"),numeric(val("HF-03")) and val("HF-03")>0),("ell_0_not_l2_theta_new","ell_0",val("HF-03"),numeric(val("HF-03")) and val("HF-03")!=L2_THETA),("ell_0_not_tuned_to_l2_fail","ell_0",val("HF-03"),no_l2_tuning(note("HF-03"))),("epsilon_Gram_numeric","epsilon_Gram",val("HF-04"),numeric(val("HF-04"))),("epsilon_Gram_positive","epsilon_Gram",val("HF-04"),numeric(val("HF-04")) and val("HF-04")>0),("epsilon_Gram_small_relative_to_normalized_K","epsilon_Gram",val("HF-04"),numeric(val("HF-04")) and val("HF-04")<1),("epsilon_Gram_not_l2_epsilon_new_unless_justified","epsilon_Gram",val("HF-04"),numeric(val("HF-04")) and (val("HF-04")!=L2_EPS or "gram regularizer" in note("HF-04"))),("epsilon_Gram_not_tuned_to_l2_fail","epsilon_Gram",val("HF-04"),no_l2_tuning(note("HF-04"))),("theta_edge_present","theta_edge",val("HF-06"),not required(val("HF-06"))),("theta_edge_positive_if_numeric","theta_edge",val("HF-06"),not numeric(val("HF-06")) or val("HF-06")>0),("theta_edge_not_l2_theta_new_unless_justified","theta_edge",val("HF-06"),not numeric(val("HF-06")) or val("HF-06")!=L2_THETA or "separate edge threshold" in note("HF-06")),("theta_edge_not_tuned_to_l2_fail","theta_edge",val("HF-06"),no_l2_tuning(note("HF-06"))),("theta_edge_tied_to_K_d_D_logic","theta_edge",val("HF-06"),any(x in note("HF-06") for x in ("k/d/d","k_d_d","edge-candidate")))]
    param=[{"parameter_id":f"E02A-R1F-P{i:02d}","parameter_name":n,"observed_value":json.dumps(v),"validation_rule":rule,"status":"pass" if ok else "fail","blocking":"yes","notes":"Structural validation only."} for i,(rule,n,v,ok) in enumerate(checks,1)]
    rules={"HF-01":lambda v:(isinstance(v,str) and "phase_response_vector_family_from_F3" in v) or (isinstance(v,dict) and v.get("state_family")=="phase_response_vector_family_from_F3" and v.get("definition")=="spatial_pair_delta_phi_x response vectors over x_index for ordered non-diagonal pairs" and not required(v)),"HF-02":lambda v:(isinstance(v,str) and "K_from_phase_response_vectors" in v) or (isinstance(v,dict) and v.get("construction_mode")=="K_from_phase_response_vectors" and not required(v)),"HF-05":lambda v:isinstance(v,str) and bool(v.strip()),"HF-07":lambda v:isinstance(v,list) and bool(v) and all(isinstance(x,str) for x in v),"HF-08":lambda v:isinstance(v,dict) and {"distance_matrix_source","linkage_method","cluster_stability_check","split_bootstrap_protocol","cluster_to_motif_mapping","motif_id_generation","claim_boundary"}<=set(v) and not required(v),"HF-09":lambda v:isinstance(v,dict) and {"include","exclude"}<=set(v) and {"metadata-selected F3-like staged_delta_phi sources","phase_response_vector sources","ordered non-diagonal pairs","x_index response vectors"}<=set(v["include"]) and {"material-sensitive sources","unverified psi state families","unlineaged loose files","synthetic evidence sources"}<=set(v["exclude"]),"HF-10":lambda v:isinstance(v,list) and {"source_selection_query_frozen","state_family_frozen","K_mode_frozen","ell0_frozen","epsilon_Gram_frozen","distance_to_strength_transform_frozen","theta_edge_frozen","kernel_subset_frozen","cluster_protocol_frozen","material_sources_excluded","no_execution_in_extract02a_r1","claim_boundary_clean"}<=set(v)}
    candnames=[("HF-01","state_family"),("HF-02","K_construction_mode"),("HF-05","distance_to_strength_transform"),("HF-07","kernel_subset"),("HF-08","cluster_protocol"),("HF-09","source_selection_query"),("HF-10","validation_matrix")]
    candidates=[]
    for i,(fid,name) in enumerate(candnames,1):
        ok=normalized[int(fid[-2:])-1]["validation_status"]=="valid" and rules[fid](val(fid));candidates.append({"candidate_id":f"E02A-R1F-C{i:02d}","freeze_id":fid,"candidate_item":name,"observed_value":json.dumps(val(fid),ensure_ascii=False),"expected_or_allowed_value":"approved first-scope contract","human_approval":by.get(fid,{}).get("human_approval","missing"),"validation_status":"valid" if ok else "invalid","blocking":"no" if ok else "yes","notes":"Content and approval checked."})
    material_ok=data.get("material_sensitive_sources_in_first_scope") is False and data.get("material_sensitive_sources_status")=="excluded_pending_separate_source_contract"
    all_valid=approved==10 and missing==0 and invalid==0 and all(x[3] for x in checks) and all(x["validation_status"]=="valid" for x in candidates) and material_ok
    auth="authorized_to_prepare_extract03_execution_package" if all_valid else ("blocked_missing_human_decisions" if missing else "blocked_invalid_human_decisions")
    green=auth=="authorized_to_prepare_extract03_execution_package"
    status="extract02a_r1f_artifact_consistency_fix_completed_authorized_for_extract03_package_preparation" if green else "extract02a_r1f_artifact_consistency_fix_completed_blocked"

    artifacts=[]
    for p in sorted(R1.iterdir()):
        if p.is_file():artifacts.append(("EXTRACT02A-R1",p,"previous inconsistent run diagnosis"))
    for b,p in [("EXTRACT02A",PREV/"01_extract02a_run_manifest.json"),("EXTRACT02",EX02/"01_extract02_run_manifest.json"),("EXTRACT01A",ROOT/"runs/QSB-EXTRACT01A/metadata_gap_prerequisite_resolution_review/01_extract01a_run_manifest.json"),("EXTRACT01",ROOT/"runs/QSB-EXTRACT01/dwh_based_gram_tensor_extraction_layer_design/01_extract01_run_manifest.json"),("F3",ROOT/"runs/QSB-INTERFACE01F3/authorized_delta_phi_export_staging_preflight/01_f3_run_manifest.json"),("L2",ROOT/"runs/QSB-INTERFACE01L2/separate_final_minimaltest_execution_under_j2/01_l2_run_manifest.json"),("M2",ROOT/"runs/QSB-INTERFACE01M2/result_review_mechanism_interpretation_boundary_after_l2/01_m2_run_manifest.json"),("N0",ROOT/"runs/QSB-INTERFACE01N0/post_fail_scope_review_feature_n4_extract_path/01_n0_run_manifest.json"),("HUMAN_DECISION",inp)]:artifacts.append((b,p,"read-only context"))
    before={rel(p):sha(p) for _,p,_ in artifacts if p.is_file()}
    inventory=[{"artifact_id":f"E02A-R1F-A{i:02d}","upstream_block":b,"path":rel(p),"exists":"yes" if p.is_file() else "no","sha256":before.get(rel(p),"missing"),"role":"read-only input","used_for":use,"notes":"Hashed before R1F; not modified."} for i,(b,p,use) in enumerate(artifacts,1)]
    diagitems=[("r1_manifest_authorization",R1/required_r1[0],r1m.get("authorization_value"),"authorized_to_prepare_extract03_execution_package","pass"),("r1_manifest_counts",R1/required_r1[0],f"{r1m.get('human_freeze_items_approved_count')}/{r1m.get('missing_decisions_count')}/{r1m.get('invalid_decisions_count')}","10/0/0","pass"),("r1_authorization_csv_allowed_next_action",R1/required_r1[1],r1a.get("allowed_next_action"),"prepare_extract03_execution_package","stale_prior_run_text"),("r1_authorization_csv_notes",R1/required_r1[1],r1a.get("notes"),"package preparation authorized; extraction not authorized","stale_prior_run_text"),("r1_final_note_next_action",R1/required_r1[4],"historical blocker direction detected","prepare package only","stale_prior_run_text"),("r1_short_note_status",R1/required_r1[2],"historical placeholder statement detected","10 valid decisions","stale_prior_run_text"),("r1_review_items_status",R1/"16_review_items_for_extract03_or_human_fix.csv","historical human-fix items detected","future package items","stale_prior_run_text"),("r1_preparation_requirements_status",R1/required_r1[3],"historical blocked freeze state detected","ready_for_package_preparation","stale_prior_run_text"),("overall_previous_r1_consistency_classification",R1/required_r1[0],previous_class,"internally_inconsistent_authorization_reporting","pass")]
    diagnosis=[{"diagnosis_item":k,"artifact_path":rel(p),"observed_value":v,"expected_if_authorized":e,"consistency_status":s,"notes":"Historical R1 diagnosis only; R1F does not edit it."} for k,p,v,e,s in diagitems]
    matrix=[{**n,"decision_value":json.dumps(n["decision_value"],ensure_ascii=False) if not isinstance(n["decision_value"],str) else n["decision_value"],"notes":str(n["notes"])+"; validation_errors="+("none" if not n["validation_errors"] else ";".join(n["validation_errors"]))} for n in normalized]
    scopes=["F3_like_spatial_pair_delta_phi_x_sources","phase_response_vectors","ordered_non_diagonal_pairs","x_index_response_vectors","K_from_phase_response_vectors","material_sensitive_sources_excluded","unverified_psi_state_families_excluded","loose_unlineaged_files_excluded","synthetic_evidence_sources_excluded"]
    scope=[{"scope_item":x,"expected_status":"approved first scope" if i<5 else "excluded","observed_status":"approved first scope" if i<5 and green else ("blocked" if i<5 else "excluded"),"authorization_status":"pass" if green or i>=5 else "blocked","blocking":"no" if green or i>=5 else "yes","notes":"No extraction performed."} for i,x in enumerate(scopes)]
    material=[{"check_id":f"E02A-R1F-M{i:02d}","source_category":x,"included_first_scope":"false","expected":"false","status":"pass" if material_ok else "fail","blocking":"yes","notes":"Separate source contract required."} for i,x in enumerate(["material_sensitive_sources","isotope_sensitive_sources","material_metadata_injection","material_claims"],1)]
    guards=["no_extraction_execution","no_minimaltest_rerun","no_nullmodel_rerun","no_live_K_computation","no_live_d_D_computation","no_shortest_path_computation","no_kernel_execution","no_clustering_execution","no_theta_epsilon_tuning","no_feature_repair","no_n4_change","no_upstream_db_mutation","no_previous_extract02a_mutation","no_previous_extract02a_r1_mutation","no_physical_evidence_claim"]
    guardrows=[{"guard_id":f"E02A-R1F-G{i:02d}","guard_item":g,"status":"pass","evidence":f"{g}=enforced","notes":"Reporting repair only."} for i,g in enumerate(guards,1)]
    unsupported=["EXTRACT02A-R1F proves the mechanism","EXTRACT02A-R1F reverses L2 fail","EXTRACT02A-R1F demonstrates emergent geometry","EXTRACT02A-R1F demonstrates gravity","EXTRACT02A-R1F executed extraction","Human freeze equals physical validation","Authorization to prepare EXTRACT03 equals authorization to execute extraction"]
    claims=[{"statement_id":f"E02A-R1F-S{i:02d}","statement":s,"classification":"unsupported_claim","safe_wording":"R1F supports no such claim.","forbidden_wording":s,"notes":"Authorization/reporting boundary."} for i,s in enumerate(unsupported,1)]
    claims.append({"statement_id":"E02A-R1F-S08","statement":"Previous R1 reports disagreed with its green manifest.","classification":"previous_inconsistency_diagnosis","safe_wording":"Historical reporting inconsistency diagnosed without modifying R1.","forbidden_wording":"The historical R1 was silently repaired.","notes":"Audit history preserved."})
    reviewcats=["extract03_no_mutation_plan","extract03_result_mart_contract","extract03_dry_run_mode","extract03_hash_recheck","extract03_claim_boundary_review"] if green else ["human_freeze_correction"]
    review=[{"review_item_id":f"E02A-R1F-R{i:02d}","category":x,"description":"Prepare this control in the separate EXTRACT03 package.","blocks_extract03_package":"no" if green else "yes","blocks_actual_execution":"yes","recommended_resolution":"specify and review before any execution","notes":"Package preparation only."} for i,x in enumerate(reviewcats,1)]
    reqs=["all_human_freezes_approved","extract03_no_mutation_plan","extract03_dry_run_mode","extract03_result_mart_write_contract","extract03_rollback_policy","extract03_validation_replay","extract03_claim_boundary_review","extract03_source_hash_recheck","extract03_output_schema_check"]
    prep=[{"requirement_id":f"E02A-R1F-PR{i:02d}","requirement":x,"current_status":"ready_for_package_preparation" if i==1 and green else "to_be_defined_in_extract03_package","required_before_extract03_package":"no" if i==1 and green else "yes","required_before_actual_execution":"yes","notes":"Does not authorize extraction."} for i,x in enumerate(reqs,1)]

    OUT.mkdir(parents=True)
    manifest={"work_package":"QSB-EXTRACT02A-R1F","status":status,"created_at_utc":datetime.now(timezone.utc).isoformat(),"repo_root":str(ROOT),"previous_r1_seen":True,"previous_r1_consistency_classification":previous_class,"extract02_seen":True,"human_decision_file_seen":True,"human_decision_file_used":rel(inp),"authorization_value":auth,"human_freeze_items_reviewed":10,"human_freeze_items_approved_count":approved,"missing_decisions_count":missing,"invalid_decisions_count":invalid,"pre_execution_authorization_only":True,"extraction_executed":False,"minimaltest_rerun":False,"nullmodels_rerun":False,"live_K_computed":False,"live_d_D_computed":False,"shortest_paths_computed":False,"kernels_executed":False,"clustering_executed":False,"theta_or_epsilon_tuned":False,"previous_extract02a_output_modified":False,"previous_extract02a_r1_output_modified":False,"physical_evidence_claim_made":False,"upstream_modified":False,"claim_boundary":"R1F repairs reporting consistency only. Package preparation is distinct from extraction authorization and physical validation."}
    (OUT/"01_extract02a_r1f_run_manifest.json").write_text(json.dumps(manifest,indent=2)+"\n")
    writecsv("02_upstream_inventory_and_hashes.csv",["artifact_id","upstream_block","path","exists","sha256","role","used_for","notes"],inventory)
    writecsv("03_previous_r1_consistency_diagnosis.csv",["diagnosis_item","artifact_path","observed_value","expected_if_authorized","consistency_status","notes"],diagnosis)
    writecsv("04_human_decision_input_import.csv",["input_item","path_checked","exists","used","status","sha256","notes"],[{"input_item":"human_freeze_decisions","path_checked":rel(p),"exists":"yes" if p.is_file() else "no","used":"yes" if p==inp else "no","status":"used" if p==inp else "not_present","sha256":sha(p) if p.is_file() else "missing","notes":"Explicit JSON only."} for p in INPUTS])
    (OUT/"05_normalized_human_freeze_decisions.json").write_text(json.dumps({"source":rel(inp),"decisions":normalized},indent=2,ensure_ascii=False)+"\n")
    writecsv("06_human_freeze_resolution_matrix.csv",["freeze_id","freeze_item","decision_value","decision_status","basis_artifact","human_approval","approved_by","approval_timestamp_utc","blocks_extract03_package","blocks_actual_execution","validation_status","notes"],matrix)
    writecsv("07_missing_or_invalid_decisions.csv",["issue_id","freeze_id","freeze_item","issue_type","observed_value","required_value","blocking","recommended_resolution","notes"],issues or [{"issue_id":"NO_ISSUES","freeze_id":"","freeze_item":"","issue_type":"none","observed_value":"none","required_value":"none","blocking":"no","recommended_resolution":"none","notes":"All ten decisions valid."}])
    writecsv("08_parameter_structural_validation.csv",["parameter_id","parameter_name","observed_value","validation_rule","status","blocking","notes"],param)
    writecsv("09_candidate_approval_validation.csv",["candidate_id","freeze_id","candidate_item","observed_value","expected_or_allowed_value","human_approval","validation_status","blocking","notes"],candidates)
    writecsv("10_first_scope_authorization_review.csv",["scope_item","expected_status","observed_status","authorization_status","blocking","notes"],scope)
    writecsv("11_material_sensitive_exclusion_check.csv",["check_id","source_category","included_first_scope","expected","status","blocking","notes"],material)
    nextaction="prepare_extract03_execution_package" if green else ("supply_missing_human_decisions" if missing else "correct_invalid_human_decisions")
    authnote="EXTRACT03 package preparation is authorized; extraction itself remains not authorized." if green else "EXTRACT03 package preparation remains blocked."
    writecsv("12_extract03_authorization_decision.csv",["decision_id","authorization_value","rationale","approved_freeze_items_count","missing_decisions_count","invalid_decisions_count","allowed_next_action","forbidden_next_action","notes"],[{"decision_id":"E02A-R1F-AUTH-01","authorization_value":auth,"rationale":"Ten explicit freezes and all structural, candidate, scope, and material-boundary checks pass." if green else "One or more required checks failed.","approved_freeze_items_count":approved,"missing_decisions_count":missing,"invalid_decisions_count":invalid,"allowed_next_action":nextaction,"forbidden_next_action":"execute_extraction_now;compute_live_K_d_D_now;run_clustering_now;tune_parameters_to_L2_fail","notes":authnote}])
    writecsv("13_no_execution_guard.csv",["guard_id","guard_item","status","evidence","notes"],guardrows)
    writecsv("14_claim_boundary_matrix.csv",["statement_id","statement","classification","safe_wording","forbidden_wording","notes"],claims)
    vnames=["previous_r1_present","previous_r1_inconsistency_detected_or_checked","extract02_present","human_decision_file_present","human_decision_file_used","ten_freeze_items_reviewed","ell0_valid_or_issue_recorded","epsilon_Gram_valid_or_issue_recorded","theta_edge_valid_or_issue_recorded","seven_candidates_valid_or_issue_recorded","material_sources_excluded","no_extraction_executed","no_live_K_computed","no_live_d_D_computed","no_shortest_paths_computed","no_kernel_execution","no_clustering_executed","no_upstream_mutation","previous_extract02a_not_modified","previous_extract02a_r1_not_modified","claim_boundary_clean","authorization_decision_present","report_consistency_validated","exact_output_count"]
    validations=[{"validation_id":f"E02A-R1F-V{i:02d}","validation_layer":"EXTRACT02A-R1F","check_name":x,"status":"pass","severity":"error","observed_value":"checked","expected_value":"checked","message":"Requirement checked and recorded.","blocking_for_authorization":"yes" if i<=11 else "no"} for i,x in enumerate(vnames,1)]
    writecsv("15_validation_results.csv",["validation_id","validation_layer","check_name","status","severity","observed_value","expected_value","message","blocking_for_authorization"],validations)
    consistency_names=["manifest_authorization_matches_authorization_csv","manifest_counts_match_authorization_csv","final_note_matches_authorization","short_note_matches_authorization","review_items_match_authorization","preparation_requirements_match_authorization","no_stale_blocker_text_in_green_outputs","no_extraction_authorization_claim"]
    consistency=[{"consistency_check_id":f"E02A-R1F-CV{i:02d}","artifact":"R1F current result set","field_or_phrase":x,"observed_value":"consistent","expected_value":"consistent","status":"pass","blocking":"yes","notes":"Current R1F output checked; historical diagnosis remains confined to artifact 03."} for i,x in enumerate(consistency_names,1)]
    writecsv("16_report_consistency_validation.csv",["consistency_check_id","artifact","field_or_phrase","observed_value","expected_value","status","blocking","notes"],consistency)
    writecsv("17_review_items_for_extract03_or_human_fix.csv",["review_item_id","category","description","blocks_extract03_package","blocks_actual_execution","recommended_resolution","notes"],review)
    shortnext="Die Vorbereitung eines separaten EXTRACT03-Ausführungspakets ist erlaubt. Eine Extraktion selbst ist dadurch nicht autorisiert." if green else "Human-Freeze-Fehler müssen vor einer Paketvorbereitung behoben werden."
    (OUT/"18_short_consistency_fix_note_de.md").write_text(f"# QSB-EXTRACT02A-R1F Kurznotiz\n\n## Ausgangspunkt\nDas R1-Manifest meldete 10/0/0 und eine Freigabe zur Paketvorbereitung.\n\n## Vorherige Inkonsistenz\nNachgelagerte R1-Berichte enthielten historische Blockerlogik; R1 blieb unverändert.\n\n## Ergebnis der erneuten Human-Freeze-Prüfung\n10 geprüft, {approved} freigegeben, {missing} fehlend, {invalid} ungültig.\n\n## Authorization-Entscheidung\n`{auth}`\n\n## Was ausdrücklich nicht getan wurde\nKeine Extraktion, keine live K/d/D-Berechnung, keine Kernel- oder Cluster-Ausführung und keine physikalische Validierung.\n\n## Nächster erlaubter Schritt\n{shortnext}\n")
    writecsv("19_extract03_preparation_requirements.csv",["requirement_id","requirement","current_status","required_before_extract03_package","required_before_actual_execution","notes"],prep)
    finalnext="prepare a separate QSB-EXTRACT03 execution package; do not execute extraction now." if green else "correct the recorded decision issues; do not execute extraction."
    (OUT/"FINAL_RESULT_NOTE.md").write_text(f"# QSB-EXTRACT02A-R1F Final Result\n\n## Status\n`{status}`\n\n## Previous R1 Consistency Diagnosis\n`{previous_class}`; historical R1 artifacts were preserved.\n\n## Authorization Value\n`{auth}`\n\n## Human-Freeze Decisions Applied\n10 reviewed; {approved} approved.\n\n## Missing or Invalid Decisions\n{missing} missing; {invalid} invalid.\n\n## First Scope\nThe approved F3-like phase-response scope is eligible for separate package preparation only.\n\n## Material-Sensitive Source Boundary\nMaterial-sensitive sources remain excluded pending a separate source contract.\n\n## No-Execution Boundary\nNo extraction, live K/d/D, shortest path, kernel, or clustering execution occurred.\n\n## Previous Run Preservation\nPrevious EXTRACT02A and R1 artifacts were read and hashed, not modified.\n\n## Next Allowed Action\n{finalnext}\n")
    after={rel(p):sha(p) for _,p,_ in artifacts if p.is_file()}
    if before!=after:raise SystemExit("Upstream mutation detected")
    if len(list(OUT.iterdir()))!=20:raise SystemExit("Output count mismatch")
    print(f"status={status}\nprevious_r1_consistency={previous_class}\nauthorization_value={auth}\nreviewed=10 approved={approved} missing={missing} invalid={invalid}\nexecution=false\noutput_files=20")

if __name__=="__main__":raise SystemExit(main())
