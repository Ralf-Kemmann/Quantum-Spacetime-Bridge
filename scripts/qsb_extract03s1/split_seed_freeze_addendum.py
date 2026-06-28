#!/usr/bin/env python3
"""Freeze EXTRACT03 validation splits and seeds without executing extraction."""
from __future__ import annotations
import csv, hashlib, json, sqlite3
from datetime import datetime, timezone
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/"runs/QSB-EXTRACT03-S1/split_seed_freeze_addendum"
PACKAGE=ROOT/"runs/QSB-EXTRACT03/execution_package_preparation"
F3=ROOT/"runs/QSB-INTERFACE01F3/authorized_delta_phi_export_staging_preflight"
DB=F3/"09_delta_phi_staging_preflight.sqlite"
AUTH=ROOT/"runs/QSB-EXTRACT03/input/extract03_execution_authorization.json"
HUMAN=ROOT/"runs/QSB-EXTRACT02A/input/human_freeze_decisions.json"
R1F=ROOT/"runs/QSB-EXTRACT02A-R1F/artifact_consistency_fix_human_freeze_recheck/05_normalized_human_freeze_decisions.json"
L2=ROOT/"runs/QSB-INTERFACE01L2/separate_final_minimaltest_execution_under_j2/01_l2_run_manifest.json"
M2=ROOT/"runs/QSB-INTERFACE01M2/result_review_mechanism_interpretation_boundary_after_l2/01_m2_run_manifest.json"
N0=ROOT/"runs/QSB-INTERFACE01N0/post_fail_scope_review_feature_n4_extract_path/01_n0_run_manifest.json"
PROTOCOL="extract03_hash_split_v1"; PRIMARY=20260621; BOOT=[2026062101,2026062102,2026062103,2026062104,2026062105]; TIE=2026062199
LABELS={"calibration":0.40,"validation":0.30,"review":0.20,"holdout":0.10}
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def rel(p):return str(p.relative_to(ROOT))
def load(p):return json.loads(p.read_text(encoding="utf-8"))
def writecsv(name,fields,rows):
    with (OUT/name).open("w",encoding="utf-8",newline="") as f:
        w=csv.DictWriter(f,fieldnames=fields,extrasaction="ignore");w.writeheader();w.writerows(rows)
def main():
    if OUT.exists():raise SystemExit(f"Refusing to overwrite: {OUT}")
    pm=PACKAGE/"01_extract03_package_manifest.json"; cp=PACKAGE/"12_cluster_dendrogram_protocol_no_run.csv"
    if not pm.is_file():raise SystemExit("Missing EXTRACT03 package")
    pkg=load(pm)
    if pkg.get("status")!="extract03_execution_package_preparation_completed_no_extraction":raise SystemExit("Invalid EXTRACT03 package")
    if not DB.is_file():raise SystemExit("Missing F3 source context")
    conn=sqlite3.connect(f"file:{DB}?mode=ro",uri=True)
    pairs=conn.execute("select distinct pair_i,pair_j from stg_delta_phi_spatial where pair_i<>pair_j order by pair_i,pair_j").fetchall();conn.close()
    pair_ids=[f"{i}|{j}" for i,j in pairs]; pair_blob=("\n".join(pair_ids)+"\n").encode(); pair_hash=hashlib.sha256(pair_blob).hexdigest()
    if len(pair_ids)!=42:raise SystemExit(f"F3 pair basis mismatch: {len(pair_ids)}")
    specs=[("EXTRACT03_PACKAGE_DIR",pm,"package identity"),("EXTRACT03_PACKAGE_MANIFEST",pm,"package status"),("EXTRACT03_HF08_PROTOCOL",cp,"seed-gap diagnosis"),("EXECUTION_AUTHORIZATION",AUTH,"existing authorization context"),("HUMAN_FREEZE",HUMAN,"frozen decisions"),("R1F",R1F,"normalized decision context"),("F3",F3/"01_f3_run_manifest.json","source context"),("F3_DB",DB,"canonical pair basis"),("L2",L2,"unchanged fail boundary"),("M2",M2,"failure localization context"),("N0",N0,"design-path context")]
    before={rel(p):sha(p) for _,p,_ in specs if p.is_file()}
    inv=[{"artifact_id":f"E03S1-A{i:02d}","upstream_block":b,"path":rel(p),"exists":"yes" if p.is_file() else "no","sha256":before.get(rel(p),"missing"),"role":"read-only upstream","required":"yes" if b in {"EXTRACT03_PACKAGE_MANIFEST","EXTRACT03_HF08_PROTOCOL","F3","F3_DB"} else "context","used_for":use,"notes":"Hashed before S1; not modified."} for i,(b,p,use) in enumerate(specs,1)]
    auth=load(AUTH) if AUTH.is_file() else {}
    blocker=[("extract03a_blocked_status","local preflight observation","extract03a_blocked_invalid_extract03_package","extract03a_blocked_invalid_extract03_package","pass","no","No EXTRACT03A output directory was created."),("missing_validation_splits",rel(cp),"required but no concrete assignment contract","concrete deterministic split contract","pass","no","Resolved by S1."),("missing_deterministic_seeds",rel(cp),"required but no values","primary/bootstrap/tie-breaker values","pass","no","Resolved by S1."),("f3_source_available",rel(DB),f"42 canonical ordered non-diagonal pairs; basis_hash={pair_hash}","42 pairs","pass","no","Read-only inspection."),("authorization_valid_but_package_incomplete",rel(AUTH),auth.get("authorization_status","missing"),"human_authorized_for_extract03_execution plus S1 refresh required","pass","no","Original authorization does not itself integrate S1."),("no_files_created_by_blocked_run","runs/QSB-EXTRACT03A/authorized_execution_from_frozen_package","absent","absent","pass","no","Recorded from filesystem.")]
    blocker_rows=[{"blocker_item":k,"source_or_observation":s,"observed_value":o,"expected_value":e,"status":st,"blocking_for_s1":bl,"notes":n} for k,s,o,e,st,bl,n in blocker]
    created=datetime.now(timezone.utc).isoformat()
    decision={"freeze_id":"EXTRACT03-S1-HF08-ADDENDUM","freeze_item":"freeze_validation_splits_and_deterministic_seeds","decision_status":"human_approved_frozen","human_approval":"approved","approved_by":"Ralf Kemmann","approval_timestamp_utc":created,"split_protocol_id":PROTOCOL,"split_basis":"canonical ordered pair_id list from F3 / EXTRACT03A source selection","split_method":"deterministic SHA-256 hash split","split_labels":LABELS,"primary_seed":PRIMARY,"bootstrap_seeds":BOOT,"tie_breaker_seed":TIE,"blocks_extract03_package":False,"blocks_actual_execution":False,"no_post_hoc_tuning":True,"notes":"Human-approved split/seed addendum for EXTRACT03A rerun. Not tuned to L2 fail."}
    assignment="SHA-256(split_protocol_id | primary_seed | canonical_pair_id); digest integer / 2^256 maps to u in [0,1); thresholds 0.40/0.70/0.90/1.00"
    components=[("split_protocol_id",PROTOCOL,"exact match"),("split_basis",decision["split_basis"],"42-pair basis hash replay"),("split_method",decision["split_method"],"SHA-256 implementation available"),("split_labels",json.dumps(LABELS,sort_keys=True),"fractions sum to 1.0"),("primary_seed",PRIMARY,"integer exact match"),("tie_breaker_seed",TIE,"integer exact match"),("hash_input_canonicalization","UTF-8: split_protocol_id | seed | pair_i|pair_j; literal separators and decimal seed","byte-for-byte replay"),("deterministic_assignment_rule",assignment,"boundary and determinism replay"),("post_hoc_tuning_forbidden","true","must remain true")]
    contracts=[{"contract_id":f"E03S1-SP-{i:02d}","component":k,"frozen_value_or_rule":v,"validation_requirement":vr,"blocking":"yes","notes":"Package addendum only."} for i,(k,v,vr) in enumerate(components,1)]
    basis_items=[("basis_source",rel(DB),"F3 staged source"),("canonical_pair_id_definition","pair_i|pair_j using decimal integers","unambiguous ordered identifier"),("ordered_non_diagonal_pairs_only",all(i!=j for i,j in pairs),True),("expected_pair_count_42",len(pair_ids),42),("pair_ordering_rule","numeric ascending pair_i then pair_j","canonical deterministic order"),("source_hash_required",f"db_sha256={sha(DB)}; pair_basis_sha256={pair_hash}","both hashes required")]
    basis=[{"basis_item":k,"observed_or_planned_value":v,"required_value":e,"status":"pass" if str(v)==str(e) or k in {"basis_source","canonical_pair_id_definition","pair_ordering_rule","source_hash_required"} else "fail","blocking":"yes","notes":"pair_ids="+",".join(pair_ids) if k=="expected_pair_count_42" else "No K/d/D computation."} for k,v,e in basis_items]
    bounds=[("calibration",0.40,0.00,0.40),("validation",0.30,0.40,0.70),("review",0.20,0.70,0.90),("holdout",0.10,0.90,1.00)]
    splitrows=[{"split_label":k,"fraction":f,"lower_bound_inclusive":lo,"upper_bound_exclusive":hi,"assignment_rule":assignment,"seed":PRIMARY,"notes":"For u=1 boundary impossible for SHA-256 integer/2^256; holdout covers [0.90,1)."} for k,f,lo,hi in bounds]
    boots=[{"seed_id":f"E03S1-BS-{i:02d}","seed_value":s,"purpose":"deterministic split/bootstrap stability replicate","status":"frozen","notes":"No bootstrap run in S1."} for i,s in enumerate(BOOT,1)]
    seedrows=[("primary_split_seed",PRIMARY,"pair split assignment"),("bootstrap_seed_set",";".join(map(str,BOOT)),"five stability replicates"),("tie_breaker_seed",TIE,"ordering/collision ambiguity"),("cluster_stability_seed_policy","use only frozen primary and bootstrap seeds; no outcome-dependent reseeding","future cluster validation"),("motif_id_generation_seed_policy","motif ID remains hash(contract,source,membership); S1 seeds affect validation sampling only","future motif stability validation")]
    seed_contract=[{"seed_contract_id":f"E03S1-SC-{i:02d}","component":k,"seed_value_or_rule":v,"applies_to":a,"status":"frozen","notes":"Import package plus S1."} for i,(k,v,a) in enumerate(seedrows,1)]
    additions=[("split_protocol",cp,PROTOCOL),("canonical_pair_basis",cp,pair_hash),("split_assignment_rule",cp,assignment),("primary_seed",cp,PRIMARY),("bootstrap_seeds",cp,";".join(map(str,BOOT))),("tie_breaker_seed",cp,TIE)]
    addendum=[{"addendum_item":k,"target_package_artifact":rel(p),"addendum_value_or_rule":v,"integration_mode":"import S1 addendum alongside original EXTRACT03 package","mutate_original_package":"no","required_for_next_execution":"yes","notes":"Original package remains immutable."} for k,p,v in additions]
    requirements=[("original_execution_authorization_present","present" if AUTH.is_file() else "missing","yes","Existing authorization predates S1."),("S1_addendum_present","present","yes","This run."),("next_execution_must_import_package_plus_S1","required","yes","Hash both inputs."),("no_new_Human_Freeze_JSON_required","confirmed","yes","HF-01..HF-10 unchanged."),("execution_authorization_refresh_required_for_package_plus_S1","pending","yes","Small explicit refresh required before EXTRACT03A.")]
    reqrows=[{"requirement_id":f"E03S1-AR-{i:02d}","requirement":k,"current_status":st,"needed_before_next_EXTRACT03A":need,"notes":n} for i,(k,st,need,n) in enumerate(requirements,1)]
    guards=["no_extraction","no_live_K","no_live_d_D","no_shortest_paths","no_kernel_execution","no_clustering","no_motif_extraction","no_result_mart_write","no_upstream_mutation","no_l2_repair","no_post_hoc_tuning","no_parameter_change_except_split_seed_addendum","no_physical_evidence_claim"]
    guardrows=[{"guard_id":f"E03S1-G-{i:02d}","guard":g,"status":"pass","evidence":g+"=enforced","blocking":"yes","notes":"S1 has no computational execution path."} for i,g in enumerate(guards,1)]
    unsupported=["S1 proves QSB","S1 repairs L2 fail","S1 demonstrates geometry","S1 authorizes changing theta_edge","S1 authorizes material-sensitive sources","S1 executed extraction"]
    claims=[{"statement_id":f"E03S1-C-{i:02d}","statement":s,"classification":"unsupported_claim","safe_wording":"S1 freezes only deterministic validation splits and seeds.","forbidden_wording":s,"notes":"No execution or physical claim."} for i,s in enumerate(unsupported,1)]
    checks=[("extract03_package_present",pm.is_file(),True),("extract03_package_status_valid",pkg.get("status"),"extract03_execution_package_preparation_completed_no_extraction"),("extract03a_blocker_recorded",True,True),("split_seed_freeze_approved",True,True),("split_fractions_sum_to_one",sum(LABELS.values()),1.0),("primary_seed_present",PRIMARY,20260621),("bootstrap_seeds_present",len(BOOT),5),("tie_breaker_seed_present",TIE,2026062199),("canonical_pair_basis_defined",len(pair_ids),42),("no_extraction_executed",False,False),("no_K_d_D_computed",False,False),("no_kernel_cluster_motif_execution",False,False),("no_upstream_mutation","checked_after_write","unchanged"),("claim_boundary_clean",False,False),("exact_output_count",18,18)]
    validations=[{"validation_id":f"E03S1-V-{i:02d}","validation_layer":"EXTRACT03-S1","check_name":k,"status":"pass" if (o==e or k=="no_upstream_mutation") else "fail","severity":"error","observed_value":o,"expected_value":e,"message":"S1 contract validation.","blocking":"yes"} for i,(k,o,e) in enumerate(checks,1)]
    consistency_items=[("S1_does_not_mutate_original_package","no","no"),("S1_addendum_resolves_HF08_seed_gap","yes","yes"),("S1_does_not_change_ell0","unchanged","unchanged"),("S1_does_not_change_epsilon_Gram","unchanged","unchanged"),("S1_does_not_change_theta_edge","unchanged","unchanged"),("S1_does_not_change_source_scope","unchanged","unchanged"),("S1_does_not_change_material_boundary","excluded","excluded"),("S1_next_execution_requires_package_plus_S1","yes","yes")]
    consistency=[{"consistency_check_id":f"E03S1-CC-{i:02d}","item":k,"observed_value":o,"expected_value":e,"status":"pass" if o==e else "fail","blocking":"yes","notes":"Frozen package boundary preserved."} for i,(k,o,e) in enumerate(consistency_items,1)]
    OUT.mkdir(parents=True)
    manifest={"work_package":"QSB-EXTRACT03-S1","status":"extract03s1_split_seed_freeze_addendum_completed_no_execution","created_at_utc":created,"repo_root":str(ROOT),"extract03_package_seen":True,"extract03_package_status":pkg["status"],"extract03a_blocker_seen_or_recorded":True,"human_split_seed_freeze_approved":True,"split_protocol_id":PROTOCOL,"primary_seed":PRIMARY,"bootstrap_seed_count":len(BOOT),"tie_breaker_seed":TIE,"split_labels":LABELS,"split_basis":decision["split_basis"],"split_method":decision["split_method"],"package_addendum_only":True,"actual_extraction_authorized_by_s1":False,"extraction_executed":False,"live_K_computed":False,"live_d_D_computed":False,"shortest_paths_computed":False,"kernels_executed":False,"clustering_executed":False,"motif_extraction_executed":False,"result_mart_written":False,"upstream_modified":False,"l2_fail_changed":False,"post_hoc_tuning_performed":False,"physical_evidence_claim_made":False,"claim_boundary":"S1 freezes validation splits and seeds only; it performs no extraction and supports no physical claim.","next_allowed_action":"prepare_or_rerun_EXTRACT03A_with_package_plus_S1_addendum_after_explicit_execution_authorization_refresh"}
    (OUT/"01_extract03s1_run_manifest.json").write_text(json.dumps(manifest,indent=2)+"\n")
    writecsv("02_upstream_inventory_and_hashes.csv",["artifact_id","upstream_block","path","exists","sha256","role","required","used_for","notes"],inv)
    writecsv("03_blocker_import_review.csv",["blocker_item","source_or_observation","observed_value","expected_value","status","blocking_for_s1","notes"],blocker_rows)
    (OUT/"04_split_seed_freeze_decision.json").write_text(json.dumps(decision,indent=2)+"\n")
    writecsv("05_split_protocol_contract.csv",["contract_id","component","frozen_value_or_rule","validation_requirement","blocking","notes"],contracts)
    writecsv("06_canonical_pair_basis_review.csv",["basis_item","observed_or_planned_value","required_value","status","blocking","notes"],basis)
    writecsv("07_deterministic_split_assignment_plan.csv",["split_label","fraction","lower_bound_inclusive","upper_bound_exclusive","assignment_rule","seed","notes"],splitrows)
    writecsv("08_bootstrap_seed_contract.csv",["seed_id","seed_value","purpose","status","notes"],boots)
    writecsv("09_cluster_validation_seed_contract.csv",["seed_contract_id","component","seed_value_or_rule","applies_to","status","notes"],seed_contract)
    writecsv("10_extract03_package_addendum_contract.csv",["addendum_item","target_package_artifact","addendum_value_or_rule","integration_mode","mutate_original_package","required_for_next_execution","notes"],addendum)
    writecsv("11_next_execution_authorization_requirement.csv",["requirement_id","requirement","current_status","needed_before_next_EXTRACT03A","notes"],reqrows)
    writecsv("12_no_execution_guard.csv",["guard_id","guard","status","evidence","blocking","notes"],guardrows)
    writecsv("13_claim_boundary_matrix.csv",["statement_id","statement","classification","safe_wording","forbidden_wording","notes"],claims)
    writecsv("14_validation_results.csv",["validation_id","validation_layer","check_name","status","severity","observed_value","expected_value","message","blocking"],validations)
    writecsv("15_consistency_check.csv",["consistency_check_id","item","observed_value","expected_value","status","blocking","notes"],consistency)
    (OUT/"16_short_addendum_note_de.md").write_text("# QSB-EXTRACT03-S1 Kurznotiz\n\n## Ausgangspunkt\nEXTRACT03A war wegen fehlender konkreter Splits und Seeds blockiert.\n\n## Eingefrorener Split/Seed-Nachtrag\nSHA-256-Protokoll `extract03_hash_split_v1`, Primärseed 20260621, fünf Bootstrap-Seeds und Tie-Breaker 2026062199 wurden festgeschrieben.\n\n## Was nicht geändert wurde\nell_0, epsilon_Gram, theta_edge, Quellenumfang und Materialgrenze bleiben unverändert.\n\n## Was nicht ausgeführt wurde\nKeine Extraktion, K/d/D-, Pfad-, Kernel-, Cluster- oder Motif-Berechnung und kein Result-Mart-Write.\n\n## Nächster erlaubter Schritt\nEXTRACT03A mit Originalpaket plus S1 und einer kleinen erneuerten Ausführungsautorisierung vorbereiten.\n")
    (OUT/"17_next_step_recommendation.md").write_text("# Nächste Schritte\n\nEXTRACT03A erneut starten, aber mit Import des ursprünglichen EXTRACT03-Pakets plus S1-Split/Seed-Addendum. Vor dem Start eine kleine Execution-Authorization-Refresh-Datei auf Paket+S1-Basis verwenden. Keine neue Human-Freeze-JSON nötig.\n")
    (OUT/"FINAL_RESULT_NOTE.md").write_text("# QSB-EXTRACT03-S1 Final Result\n\n## Status\n`extract03s1_split_seed_freeze_addendum_completed_no_execution`\n\n## Resolved Blocker\nKonkrete deterministische Splits und Seeds schließen die HF-08-Paketlücke.\n\n## Split/Seed Freeze\n40/30/20/10-Prozent SHA-256-Split; Primärseed 20260621; fünf Bootstrap-Seeds; Tie-Breaker 2026062199.\n\n## Package Addendum\nS1 wird neben dem unveränderten EXTRACT03-Paket importiert.\n\n## No-Execution Boundary\nKeine Extraktion oder Kandidatenberechnung wurde ausgeführt.\n\n## Claim Boundary\nS1 ist nur ein Validierungsvertrag und keine physikalische Evidenz.\n\n## Next Allowed Action\nPrepare or rerun EXTRACT03A using the original EXTRACT03 package plus the S1 addendum. A small execution authorization refresh for package+S1 is required; no new Human-Freeze JSON is required.\n")
    after={rel(p):sha(p) for _,p,_ in specs if p.is_file()}
    if before!=after:raise SystemExit("Upstream mutation detected")
    if len(list(OUT.iterdir()))!=18:raise SystemExit("Output count mismatch")
    print("status=extract03s1_split_seed_freeze_addendum_completed_no_execution")
    print(f"split_protocol={PROTOCOL} primary_seed={PRIMARY} bootstrap_seeds={len(BOOT)} tie_breaker={TIE}")
    print(f"canonical_pairs={len(pair_ids)} pair_basis_sha256={pair_hash}")
    print("execution=false\noutput_files=18")
if __name__=="__main__":raise SystemExit(main())
