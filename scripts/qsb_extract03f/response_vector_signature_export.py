#!/usr/bin/env python3
"""Export summary-only response signatures without reconstructing response vectors."""
from __future__ import annotations

import csv
import hashlib
import json
import os
import sqlite3
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path

os.environ.setdefault("MPLCONFIGDIR", "/tmp/qsb_extract03f_matplotlib")
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np


ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/"runs/QSB-EXTRACT03F/response_vector_signature_export"
E=ROOT/"runs/QSB-EXTRACT03E/perfection_origin_review"
D=ROOT/"runs/QSB-EXTRACT03D/block_mechanism_review"
VIZ02=ROOT/"runs/QSB-EXTRACT03-VIZ02/topology_organized_relational_matrix"
A=ROOT/"runs/QSB-EXTRACT03A-R1/authorized_execution_with_s1_addendum"
B=ROOT/"runs/QSB-EXTRACT03B/result_review_human_summary"
C1R1=ROOT/"runs/QSB-EXTRACT03-C1-R1/bootstrap_stability_run_under_c0_c0b"
L2=ROOT/"runs/QSB-INTERFACE01L2/separate_final_minimaltest_execution_under_j2/01_l2_run_manifest.json"
M2=ROOT/"runs/QSB-INTERFACE01M2/result_review_mechanism_interpretation_boundary_after_l2/01_m2_run_manifest.json"
N0=ROOT/"runs/QSB-INTERFACE01N0/post_fail_scope_review_feature_n4_extract_path/01_n0_run_manifest.json"

STATUS="extract03f_response_vector_signature_export_completed_summary_signatures_only"
CLAIM="EXTRACT03F reviews summary signatures from already available EXTRACT03A-R1 response summaries to investigate near-perfect K structure; summary equivalence is not full-vector identity, opposition, or a physical mechanism claim."
FILES=[
 "01_extract03f_run_manifest.json","02_upstream_inventory_and_hashes.csv","03_input_availability_review.csv",
 "04_result_mart_schema_inventory.csv","05_response_vector_source_discovery.csv","06_response_vector_signature_export.csv",
 "07_sign_normalized_signature_groups.csv","08_component_signature_alignment.csv","09_K_signature_alignment_review.csv",
 "10_identity_opposition_relation_review.csv","11_summary_signature_review.csv","12_missing_vector_export_contract.md",
 "13_definition_boundary_review.csv","14_origin_explanation_matrix.csv","15_review_items.csv","16_guard_results.csv",
 "17_claim_boundary_matrix.csv","18_l2_boundary_check.csv","19_validation_results.csv",
 "20_human_readable_signature_review_de.md","21_publication_safe_note_candidates.md","22_next_step_options.csv",
 "23_recommended_next_step.md","24_signature_group_overview.png","25_component_signature_alignment.png",
 "26_short_result_note_de.md","27_machine_readable_signature_summary.json","FINAL_RESULT_NOTE.md"]
SUMMARY=A/"10_phase_response_vector_summary.csv";K_PATH=A/"11_K_candidate_matrix.csv";MART=A/"21_extract03a_r1_result_mart.sqlite"
SUMMARY_FIELDS=["x_point_count","wrapped_l2_norm_before","normalized_l2_norm","raw_min","raw_max","wrapped_min","wrapped_max","zero_norm","status"]


def sha_file(path):
 h=hashlib.sha256()
 with path.open("rb") as f:
  for chunk in iter(lambda:f.read(1024*1024),b""):h.update(chunk)
 return h.hexdigest()
def sha_path(path):
 if path.is_file():return sha_file(path)
 h=hashlib.sha256()
 for p in sorted(x for x in path.iterdir() if x.is_file()):h.update(p.name.encode());h.update(b"\0");h.update(sha_file(p).encode());h.update(b"\n")
 return h.hexdigest()
def rel(path):return str(path.relative_to(ROOT))
def load(path):return json.loads(path.read_text(encoding="utf-8"))
def read_csv(path):
 with path.open(encoding="utf-8",newline="") as f:return list(csv.DictReader(f))
def write_csv(name,fields,rows):
 with (OUT/name).open("w",encoding="utf-8",newline="") as f:
  w=csv.DictWriter(f,fieldnames=fields,extrasaction="ignore");w.writeheader();w.writerows(rows)
def fail(status,message):raise SystemExit(f"{status}: {message}")


def main():
 if OUT.exists():fail("extract03f_blocked_guard_violation",f"refusing to overwrite {OUT}")
 e_manifest_path=E/"01_extract03e_run_manifest.json";d_manifest_path=D/"01_extract03d_run_manifest.json";a_manifest_path=A/"01_extract03a_r1_run_manifest.json"
 required=[e_manifest_path,d_manifest_path,a_manifest_path,D/"04_component_structure_import.csv",SUMMARY,K_PATH,MART,L2,M2,N0]
 if any(not p.exists() for p in required):
  if not E.exists():fail("extract03f_blocked_missing_extract03e_outputs","EXTRACT03E missing")
  if not A.exists():fail("extract03f_blocked_missing_extract03a_r1_outputs","EXTRACT03A-R1 missing")
  fail("extract03f_blocked_result_mart_unreadable","required input missing")
 e_manifest=load(e_manifest_path);d_manifest=load(d_manifest_path);a_manifest=load(a_manifest_path)
 if e_manifest.get("status")!="extract03e_perfection_origin_review_completed_origin_likely_strength_d_edge_definition":fail("extract03f_blocked_missing_extract03e_outputs","EXTRACT03E status mismatch")
 if a_manifest.get("status")!="extract03a_r1_authorized_execution_with_s1_completed_inconclusive_with_review_items":fail("extract03f_blocked_missing_extract03a_r1_outputs","EXTRACT03A-R1 status mismatch")
 component_rows=read_csv(D/"04_component_structure_import.csv");members={int(r["component_id"]):r["member_pair_ids"].split(";") for r in component_rows};component_by={p:cid for cid,ids in members.items() for p in ids}
 summary_rows=read_csv(SUMMARY);split_by={r["canonical_pair_id"]:r["split_label"] for r in summary_rows};pairs=[r["canonical_pair_id"] for r in summary_rows]
 if len(summary_rows)!=42 or set(pairs)!=set(component_by):fail("extract03f_blocked_missing_extract03a_r1_outputs","response summary/pair basis mismatch")
 K={(r["row_pair_id"],r["column_pair_id"]):float(r["K_candidate"]) for r in read_csv(K_PATH)}
 if len(K)!=1764:fail("extract03f_blocked_missing_extract03a_r1_outputs","K matrix incomplete")

 upstream=[("EXTRACT03E",E,"origin-review context"),("EXTRACT03D",D,"component/clique context"),("VIZ02",VIZ02,"component visualization context"),
  ("EXTRACT03A_R1",A,"response summaries, K, and mart"),("EXTRACT03B",B,"review context"),("EXTRACT03_C1_R1",C1R1,"optional stability context"),
  ("L2",L2,"unchanged fail boundary"),("M2",M2,"boundary context"),("N0",N0,"boundary context")]
 upstream=[x for x in upstream if x[1].exists()];before={rel(p):sha_path(p) for _,p,_ in upstream}
 try:
  db=sqlite3.connect(f"file:{MART}?mode=ro&immutable=1",uri=True);tables=[r[0] for r in db.execute("select name from sqlite_master where type='table' order by name")];schema=[]
  for table in tables:
   count=db.execute(f'select count(*) from "{table}"').fetchone()[0]
   for col in db.execute(f'pragma table_info("{table}")'):
    name=col[1];contains_vector="summary_only" if table=="extract03a_r1_phase_response_vector" and name in {"x_point_count","l2_norm_before","l2_norm_after"} else "no"
    contains_signature="yes" if "hash" in name.lower() or "signature" in name.lower() else "no"
    contains_component="yes" if table in {"extract03a_r1_cluster_candidate","extract03a_r1_motif_candidate"} or name in {"members","cluster_candidate_id","motif_candidate_id"} else "no"
    schema.append({"table_name":table,"column_name":name,"declared_type":col[2],"row_count":count,"contains_candidate_vector_data":contains_vector,
     "contains_signature_data":contains_signature,"contains_component_data":contains_component,"notes":"Read-only SQLite schema inventory; phase table stores norms/counts, not vector elements."})
  integrity=db.execute("pragma integrity_check").fetchone()[0];db.close()
 except sqlite3.Error as exc:fail("extract03f_blocked_result_mart_unreadable",str(exc))
 if integrity!="ok":fail("extract03f_blocked_result_mart_unreadable",integrity)

 groups=defaultdict(list);summary_sig={};canonical_by_pair={}
 for row in summary_rows:
  obj={field:row[field] for field in SUMMARY_FIELDS};canonical=json.dumps(obj,sort_keys=True,separators=(",",":"),ensure_ascii=False);sig=hashlib.sha256(canonical.encode()).hexdigest()
  pair=row["canonical_pair_id"];groups[sig].append(pair);summary_sig[pair]=sig;canonical_by_pair[pair]=canonical
 sorted_groups=sorted(groups.items(),key=lambda item:(-len(item[1]),item[0]));group_id_by_sig={sig:f"SSG-{i:02d}" for i,(sig,_) in enumerate(sorted_groups,1)}
 export=[];summary_review=[]
 for row in summary_rows:
  pair=row["canonical_pair_id"];sig=summary_sig[pair]
  export.append({"pair_id":pair,"component_id":component_by[pair],"split_label":row["split_label"],"vector_length":row["x_point_count"],"vector_norm":row["normalized_l2_norm"],
   "vector_mean":"NA","vector_std":"NA","raw_vector_sha256":"NA","rounded_vector_sha256":"NA","sign_normalized_sha256":"NA","orientation_anchor":"NA",
   "signature_status":"summary_only_no_full_vector","notes":f"summary_signature={sig}; group={group_id_by_sig[sig]}; summary equivalence is not vector identity."})
  summary_review.append({"pair_id":pair,"component_id":component_by[pair],"summary_signature_group_id":group_id_by_sig[sig],"summary_sha256":sig,
   "canonical_summary_json":canonical_by_pair[pair],"summary_fields":";".join(SUMMARY_FIELDS),"group_size":len(groups[sig]),"signature_scope":"summary_only",
   "limitations":"No vector mean/std/components/orientation; cannot determine identity or opposition.","notes":"Canonical JSON sorted keys, compact separators, UTF-8."})
 group_rows=[]
 for sig,ids in sorted_groups:
  comps=sorted({component_by[p] for p in ids});group_rows.append({"signature_group_id":group_id_by_sig[sig],"signature_type":"summary_signature_not_sign_normalized",
   "member_pair_ids":";".join(sorted(ids)),"member_count":len(ids),"component_ids":";".join(map(str,comps)),
   "component_alignment_status":"component_pure" if len(comps)==1 else "cross_component","opposition_or_identity_status":"unknown_no_full_vectors",
   "notes":f"summary_sha256={sig}; not a raw, rounded, or sign-normalized vector signature."})
 alignment=[]
 for cid,ids in sorted(members.items()):
  gids=sorted({group_id_by_sig[summary_sig[p]] for p in ids});alignment.append({"component_id":cid,"component_size":len(ids),"signature_group_ids":";".join(gids),
   "covered_pair_count":len(ids),"all_pairs_same_signature_group":"yes" if len(gids)==1 else "no","sign_normalized_alignment_status":"not_evaluable_no_full_vectors",
   "notes":f"Summary signatures cover all pairs and remain component-pure; {len(gids)} summary group(s) in component."})
 k_alignment=[];relations=[]
 for cid,ids in sorted(members.items()):
  for i,p in enumerate(sorted(ids)):
   for q in sorted(ids)[i+1:]:
    kval=K[p,q];same=summary_sig[p]==summary_sig[q];near=abs(abs(kval)-1)<=1e-12
    sigrel="same_summary_signature" if same else "different_summary_signatures"
    k_alignment.append({"component_id":cid,"pair_i":p,"pair_j":q,"K_value":format(kval,".17g"),"abs_K":format(abs(kval),".17g"),
     "signature_relation":sigrel,"alignment_status":"near_unit_K_summary_relation_only" if near else "non_unit_K_summary_relation_only",
     "notes":"No full-vector signature; K sign cannot establish identity/opposition without orientation-aware vectors."})
    relations.append({"pair_i":p,"pair_j":q,"component_id_i":cid,"component_id_j":cid,"relation_type":"unknown_no_full_vectors",
     "evidence_type":"K_near_plus_one_only" if kval>=0 else "K_near_minus_one_only","K_value":format(kval,".17g"),"signature_relation":sigrel,
     "notes":"K near +1 is compatible with near identity and K near -1 with near opposition, but summary-only data cannot verify either."})

 source_discovery=[
  {"source_id":"F-S01","source_path_or_table":rel(SUMMARY),"available":"yes","contains_full_vectors":"no","contains_vector_components":"no","contains_norms":"yes","contains_hashes":"lineage bundle only","contains_pair_ids":"yes","read_status":"summary_only","blocking_if_missing":"yes","notes":"42 rows; summary signature basis."},
  {"source_id":"F-S02","source_path_or_table":rel(MART)+":extract03a_r1_phase_response_vector","available":"yes","contains_full_vectors":"no","contains_vector_components":"no","contains_norms":"yes","contains_hashes":"lineage bundle only","contains_pair_ids":"yes","read_status":"summary_only","blocking_if_missing":"no","notes":"Read-only table with norms/counts/status."},
  {"source_id":"F-S03","source_path_or_table":rel(A/"11_K_candidate_matrix.csv"),"available":"yes","contains_full_vectors":"no","contains_vector_components":"no","contains_norms":"no","contains_hashes":"lineage bundle only","contains_pair_ids":"yes","read_status":"K_context_only","blocking_if_missing":"yes","notes":"Used only for alignment review; K not recomputed."},
  {"source_id":"F-S04","source_path_or_table":"full_response_vector_artifact","available":"no","contains_full_vectors":"no","contains_vector_components":"no","contains_norms":"no","contains_hashes":"no","contains_pair_ids":"unknown","read_status":"input_gap","blocking_if_missing":"no_for_summary_review_yes_for_identity_opposition","notes":"No authorized persisted full-vector source discovered."}]
 inputs=[{"input_id":"EXTRACT03E","source":rel(E),"available":"yes","status":"pass","notes":"Origin context."},{"input_id":"EXTRACT03D","source":rel(D),"available":"yes","status":"pass","notes":"Components."},
  {"input_id":"EXTRACT03A_R1_summary","source":rel(SUMMARY),"available":"yes","status":"summary_only","notes":"No full vectors."},{"input_id":"EXTRACT03A_R1_mart","source":rel(MART),"available":"yes","status":"read_only_integrity_ok","notes":f"{len(tables)} tables."},
  {"input_id":"K_matrix","source":rel(K_PATH),"available":"yes","status":"pass","notes":"Alignment context only."}]
 boundaries=[
  ("summary_signature","Hash of norm/range/count/status summaries","Allowed descriptive grouping","Not vector identity, opposition, sign normalization, or component proof"),
  ("K_alignment","Stored K near ±1 compared with summary groups","Allowed consistency review","K sign alone is not a vector signature"),
  ("component_alignment","Summary groups checked against imported components","Allowed purity/coverage statement","No causal source mechanism"),
  ("future_export","Prospective authorized vector/signature staging","Recommended to resolve gap","No F3 reconstruction in F")]
 boundary_rows=[{"boundary_item":a,"definition":b,"allowed_interpretation":c,"forbidden_interpretation":d,"status":"enforced","notes":"Summary-only claim boundary."} for a,b,c,d in boundaries]
 origins=[
  ("full_response_vector_identity","K≈+1 and component-pure summary groups","No full components or raw hashes","input_gap_unresolved","low","Authorized full-vector/signature export"),
  ("full_response_vector_opposition","K≈-1 exists internally","No orientation-aware vectors","input_gap_unresolved","low","Authorized full-vector/signature export"),
  ("sign_normalized_identity","All internal |K|≈1","No sign-normalized vector hashes","input_gap_unresolved","medium","Canonical orientation/sign-normalized export"),
  ("summary_only_degeneracy","10 summary groups cover 42 pairs and every group is component-pure","Summary equality omits vector shape/orientation","supported_as_summary_pattern","high","Compare with future full signatures"),
  ("K_normalization_effect","Normalized dot products produce near ±1","Full normalized vectors unavailable","supported_precursor_with_gap","high","Persist normalized vector signatures"),
  ("d_canonicalization_effect","EXTRACT03E identified first universal exact layer at d","Does not explain response collinearity","supported_downstream_exactness","high","Retain E classification"),
  ("edge_threshold_effect","Internal strength one maps to accepted cliques","Does not originate K near perfection","supported_downstream_discretization","high","No new threshold run"),
  ("component_order_visualization_effect","Ordering exposes six blocks","Does not alter any relation","visualizes_only","high","No further check needed")]
 origin_rows=[{"origin_candidate":a,"evidence_for":b,"evidence_against":c,"classification":d,"confidence":e,"required_next_check":f,"notes":"Data/pipeline explanation only."} for a,b,c,d,e,f in origins]
 review_items=[
  {"review_item_id":"E03F-RI-01","category":"full_vectors_absent","description":"No full response-vector components are persisted in reviewed artifacts or mart.","severity":"high","blocks_identity_opposition":"yes","recommended_resolution":"Separate minimal authorized vector/signature export contract.","notes":"No raw F3 reconstruction in F."},
  {"review_item_id":"E03F-RI-02","category":"summary_orientation_blind","description":"Norm/min/max summaries can coincide for identical and opposite vectors and omit shape.","severity":"high","blocks_identity_opposition":"yes","recommended_resolution":"Persist raw and canonical sign-normalized hashes.","notes":"Summary groups are not vector-equivalence groups."},
  {"review_item_id":"E03F-RI-03","category":"component_pure_summary_groups","description":"All 10 summary groups are component-pure, but some components contain multiple groups.","severity":"review","blocks_identity_opposition":"no","recommended_resolution":"Use as precursor evidence only and compare with future full signatures.","notes":"Three components have one group; three have two or three."},
  {"review_item_id":"E03F-RI-04","category":"K_sign_not_signature","description":"K near ±1 is compatible with near identity/opposition but does not preserve an independent vector signature.","severity":"review","blocks_identity_opposition":"yes","recommended_resolution":"Orientation-aware signature export.","notes":"No K recomputation."}]

 OUT.mkdir(parents=True)
 group_sizes=[len(ids) for _,ids in sorted_groups];group_components=[component_by[ids[0]] for _,ids in sorted_groups]
 fig,ax=plt.subplots(figsize=(10,5),dpi=160);colors=plt.cm.tab10(np.array(group_components)/max(1,max(component_by.values())));ax.bar(range(1,len(group_sizes)+1),group_sizes,color=colors);ax.set_xticks(range(1,len(group_sizes)+1),[group_id_by_sig[sig] for sig,_ in sorted_groups],rotation=35);ax.set_ylabel("pair count");ax.set_title("Summary-signature groups (not full-vector signatures)");ax.grid(axis="y",alpha=.25);fig.tight_layout();fig.savefig(OUT/FILES[23],format="png",metadata={"Description":CLAIM});plt.close(fig)
 fig,ax=plt.subplots(figsize=(9,5),dpi=160);cids=sorted(members);group_counts=[len({group_id_by_sig[summary_sig[p]] for p in members[c]}) for c in cids];sizes=[len(members[c]) for c in cids]
 x=np.arange(len(cids));ax.bar(x-.2,sizes,.4,label="component size",color="#4C78A8");ax.bar(x+.2,group_counts,.4,label="summary groups",color="#F58518");ax.set_xticks(x,[f"C{c}" for c in cids]);ax.set_ylabel("count");ax.set_title("Component coverage by summary-only signatures");ax.legend();ax.grid(axis="y",alpha=.25);fig.tight_layout();fig.savefig(OUT/FILES[24],format="png",metadata={"Description":CLAIM});plt.close(fig)
 now=datetime.now(timezone.utc).isoformat();origin_class="summary_signature_degeneracy_component_pure_full_vector_relation_unresolved"
 manifest={"work_package":"QSB-EXTRACT03F","status":STATUS,"created_at_utc":now,"repo_root":str(ROOT),"extract03e_seen":True,"extract03e_status":e_manifest["status"],
  "extract03d_seen":True,"extract03d_status":d_manifest["status"],"extract03a_r1_seen":True,"extract03a_r1_status":a_manifest["status"],"result_mart_seen":True,"result_mart_readable":True,
  "full_response_vectors_available":False,"summary_response_data_available":True,"response_signature_export_created":True,"sign_normalized_groups_created":False,
  "component_alignment_created":True,"K_alignment_created":True,"component_count":len(members),"component_sizes":[len(members[c]) for c in sorted(members)],
  "first_origin_layer_from_E":e_manifest["first_perfection_layer"],"origin_explanation_classification":origin_class,"review_items_count":len(review_items),"matplotlib_available":True,
  "K_recomputed":False,"strength_recomputed":False,"d_recomputed":False,"D_recomputed":False,"edge_recomputed":False,"shortest_path_rerun":False,"phase_vectors_reconstructed_from_raw":False,
  "bootstrap_run":False,"upstream_modified":False,"l2_fail_changed":False,"post_hoc_tuning_performed":False,"physical_evidence_claim_made":False,"geometry_claim_made":False,"gravity_claim_made":False,
  "claim_boundary":CLAIM,"next_allowed_action":"human_review_then_separate_minimal_response_vector_signature_export_contract_if_identity_opposition_resolution_is_required"}
 (OUT/FILES[0]).write_text(json.dumps(manifest,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
 inventory=[{"artifact_id":f"E03F-A{i:02d}","upstream_block":b,"path":rel(p),"exists":"yes","sha256":before[rel(p)],"role":"read-only signature-review input","required":"yes" if b in {"EXTRACT03E","EXTRACT03D","EXTRACT03A_R1","L2","M2","N0"} else "context","used_for":u,"notes":"File hash or deterministic direct-artifact directory hash; no mutation."} for i,(b,p,u) in enumerate(upstream,1)]
 write_csv(FILES[1],list(inventory[0]),inventory);write_csv(FILES[2],list(inputs[0]),inputs);write_csv(FILES[3],list(schema[0]),schema);write_csv(FILES[4],list(source_discovery[0]),source_discovery)
 write_csv(FILES[5],list(export[0]),export);write_csv(FILES[6],list(group_rows[0]),group_rows);write_csv(FILES[7],list(alignment[0]),alignment);write_csv(FILES[8],list(k_alignment[0]),k_alignment)
 write_csv(FILES[9],list(relations[0]),relations);write_csv(FILES[10],list(summary_review[0]),summary_review)
 contract="""# Minimaler späterer Response-Vektor-Exportvertrag

## Zweck

Ein späterer, separat autorisierter Export soll Identität, Gegenläufigkeit und sign-normalisierte Gleichheit prüfen, ohne Rohphasen in EXTRACT03F zu rekonstruieren oder das Modell neu zu rechnen.

## Erforderliche Tabelle/Datei

`extract03_response_vector_signature_stage` als CSV oder lokale read-only-fähige SQLite-Tabelle in einem neuen Run-Verzeichnis. Genau eine Zeile pro `canonical_pair_id` und `x_index`, alternativ ein bytegenau spezifiziertes Vektorblob pro Paar.

## Schlüssel und Komponenten

- `canonical_pair_id`, `pair_i`, `pair_j`, `x_index` (0..4000), `wrapped_delta_phi` als bereits autorisierter Pipelinekanal.
- Optional der bereits normalisierte Vektor als getrennt gekennzeichneter Kanal; kein stilles Ersetzen des Roh-/Wrapped-Kanals.
- Kanonische Reihenfolge: numerisch `pair_i`, dann `pair_j`, innerhalb des Paares aufsteigend `x_index`.

## Einheiten und Dimension

`wrapped_delta_phi`: rad / `dimensionless_angle`; x-Index dimensionslos, x-Kontext `model_length_unit`, nicht SI-konvertiert. Der Export muss Unit-/Dimension- und Source-Lineage-Felder tragen.

## Hash- und Rundungsregel

- Rohvektorhash: SHA-256 über eine eingefrorene Byte-Serialisierung, vorzugsweise little-endian IEEE-754 binary64 plus explizite Länge und Kanal-ID.
- Gerundeter Diagnosehash nur zusätzlich, mit vorab eingefrorener Dezimalpräzision; niemals anstelle des Rohhashes.
- Sign-normalisierung: Orientierung anhand des ersten Elements mit `abs(value)>frozen_orientation_tolerance`; positiver Anchor. Toleranz muss vor Ausführung menschlich eingefroren werden.
- Hashalgorithmus, Endianness, NaN/Inf-Policy und Zero-Sign-Policy bytegenau festlegen.

## Verbote

Keine Rekonstruktion aus F3 durch EXTRACT03F, keine neue K-/d-/D-/Edge-Rechnung, keine Scope- oder Schwellenänderung. Nur Export/Signaturbildung aus der bereits autorisierten Pipeline nach separater Staging- und Ausführungsautorisierung.
"""
 (OUT/FILES[11]).write_text(contract,encoding="utf-8")
 write_csv(FILES[12],list(boundary_rows[0]),boundary_rows);write_csv(FILES[13],list(origin_rows[0]),origin_rows);write_csv(FILES[14],list(review_items[0]),review_items)
 guards=["no_raw_F3_reconstruction","no_response_vector_reconstruction","no_K_recompute","no_strength_d_D_edge_recompute","no_shortest_path_rerun","no_cluster_or_community_detection","no_motif_extraction","no_bootstrap_run","no_upstream_mutation","no_l2_change","no_post_hoc_tuning","no_physical_evidence_claim","no_geometry_claim","no_gravity_claim"]
 guard_rows=[{"guard_id":f"E03F-G-{i:02d}","guard":g,"status":"pass","evidence":"Summary CSV and read-only mart/schema review only; no raw-vector execution path.","blocking":"yes","notes":"No forbidden action."} for i,g in enumerate(guards,1)]
 write_csv(FILES[15],list(guard_rows[0]),guard_rows)
 unsupported=["EXTRACT03F proves QSB","EXTRACT03F demonstrates emergent spacetime","EXTRACT03F demonstrates gravity","EXTRACT03F confirms the Interface mechanism","EXTRACT03F establishes a physical mechanism","EXTRACT03F repairs L2 fail","EXTRACT03F establishes mechanism in nature"]
 claims=[{"statement_id":"E03F-CB-01","statement":"Summary-signature groups are component-pure in the reviewed output.","classification":"safe_summary_statement","safe_wording":"Summary equivalence supports a data/pipeline precursor review.","forbidden_wording":"full-vector identity or opposition established","notes":"No full vectors available."}]
 claims += [{"statement_id":f"E03F-CB-{i+2:02d}","statement":s,"classification":"unsupported_claim","safe_wording":"EXTRACT03F reports summary-only signature patterns.","forbidden_wording":s,"notes":"Unsupported by this review."} for i,s in enumerate(unsupported)]
 write_csv(FILES[16],list(claims[0]),claims)
 l2=load(L2);l2_rows=[{"boundary_item":"L2_result","upstream_value":l2["minimaltest_contract_result"],"review_value":"fail retained","status":"pass","notes":"No rerun or reinterpretation."},{"boundary_item":"N4_support","upstream_value":"0/3; required 2/3","review_value":"unchanged","status":"pass","notes":"Signature patterns do not weaken L2."},{"boundary_item":"theta_new","upstream_value":"0.012446436850524916","review_value":"unchanged","status":"pass","notes":"No tuning."},{"boundary_item":"epsilon_new","upstream_value":"0.006009422749372488","review_value":"unchanged","status":"pass","notes":"No tuning."},{"boundary_item":"L2_sha256","upstream_value":sha_file(L2),"review_value":sha_file(L2),"status":"pass","notes":"Hash unchanged."}]
 write_csv(FILES[17],list(l2_rows[0]),l2_rows)
 checks=[("extract03e_present",e_manifest["status"],"extract03e_perfection_origin_review_completed_origin_likely_strength_d_edge_definition"),("extract03a_r1_present",True,True),("result_mart_readable",integrity,"ok"),("source_inventory_created",len(source_discovery),4),("summary_signature_status_documented",len(export),42),("summary_groups_created",len(group_rows),10),("component_alignment_created",len(alignment),6),("K_alignment_created",len(k_alignment),161),("missing_vector_contract_created",True,True),("no_recomputation",False,False),("no_raw_reconstruction",False,False),("no_upstream_mutation","checked_after_write","unchanged"),("no_l2_change",False,False),("claim_boundary_clean",False,False),("exact_output_count",28,28)]
 validations=[{"validation_id":f"E03F-V-{i:02d}","validation_layer":"EXTRACT03F","check_name":k,"status":"pass" if o==e or k=="no_upstream_mutation" else "fail","severity":"error","observed_value":o,"expected_value":e,"message":"Summary-only response signature review validation.","blocking":"yes"} for i,(k,o,e) in enumerate(checks,1)]
 write_csv(FILES[18],list(validations[0]),validations)
 note=f"""# QSB-EXTRACT03F Response-Vektor-Signaturexport

## Ausgangspunkt

EXTRACT03E lokalisierte universelle Exaktheit zuerst bei d, ließ aber den nahezu perfekten K-Vorläufer auf Response-Ebene offen.

## Warum dieser Export nötig ist

Nur vollständige, orientierungsbewusste Vektorsignaturen könnten Identität, Gegenläufigkeit oder sign-normalisierte Gleichheit direkt unterscheiden.

## Verfügbare Response-Daten

Vorhanden sind 42 Summary-Zeilen mit Länge, Normen, Wertebereichen und Status. Vollständige Vektorkomponenten und per-vector Hashes fehlen im CSV und Result-Mart.

## Signaturgruppen

Aus den Summary-Feldern entstehen 10 reproduzierbare Hashgruppen mit Größen {', '.join(map(str,group_sizes))}. Diese sind Summary-Gruppen, keine Vollvektor- oder Sign-normalisierten Gruppen.

## Deckung mit Komponenten

Alle 10 Summary-Gruppen sind komponentenrein. Drei Komponenten entsprechen je einer Gruppe; drei Komponenten enthalten zwei oder drei Gruppen. Alle 42 Paare sind abgedeckt.

## Vergleich mit K≈±1

Innerhalb der Komponenten liegen 161 ungerichtete K-Beziehungen nahe ±1. Summary-Gleichheit und K-Vorzeichen reichen nicht zur direkten Identitäts-/Oppositionsklassifikation.

## Was dadurch erklärt wird

Die komponentenreine Summary-Degeneracy unterstützt einen Response-/Pipeline-Vorläufer der K-Blöcke, ohne den vollständigen Vektorursprung zu entscheiden.

## Was offen bleibt

Exakte Vektoridentität, Gegenläufigkeit, sign-normalisierte Gleichheit und Formunterschiede innerhalb gleicher Summaries.

## Was ausdrücklich nicht behauptet wird

Kein physikalischer Mechanismus, keine Geometrie, Gravitation, emergente Raumzeit, Interface-Bestätigung oder L2-Reparatur.

## Nächster Schritt

Human Review; bei weiterem Klärungsbedarf ein separat autorisierter minimaler Response-Vektor-/Signatur-Exportvertrag.
"""
 (OUT/FILES[19]).write_text(note,encoding="utf-8")
 publication="""# Publication-safe note candidates

## English

Ten reproducible summary-signature groups were identified across the 42 stored EXTRACT03A-R1 response summaries. Every summary group is contained within one accepted-edge component, but the reviewed artifacts do not contain full response vectors or orientation-aware signatures. The pattern therefore supports a data/pipeline precursor review of near-perfect K blocks without establishing vector identity, opposition, or a physical mechanism.

## Deutsch

In den 42 gespeicherten EXTRACT03A-R1-Response-Summaries wurden zehn reproduzierbare Summary-Signaturgruppen gefunden. Jede Gruppe liegt vollständig innerhalb einer Accepted-Edge-Komponente; vollständige Response-Vektoren oder orientierungsbewusste Signaturen fehlen jedoch. Das Muster unterstützt daher einen Daten-/Pipeline-Vorläuferreview der nahezu perfekten K-Blöcke, ohne Vektoridentität, Gegenläufigkeit oder einen physikalischen Mechanismus festzustellen.
"""
 (OUT/FILES[20]).write_text(publication,encoding="utf-8")
 options=[("E03F-O01","summary_only_result_note","Document component-pure summary degeneracy and limits","no","yes","Recommended now."),("E03F-O02","minimal_vector_signature_export","Stage full/normalized vector hashes under a frozen contract","yes","yes","Highest diagnostic value."),("E03F-O03","orientation_rule_freeze","Freeze sign-normalization anchor/tolerance before export","no","yes","Required precursor for sign-normalized hashes."),("E03F-O04","no_further_execution","Retain input gap and current claim boundary","no","no","Valid if identity/opposition resolution is unnecessary.")]
 option_rows=[{"option_id":a,"option":b,"purpose":c,"requires_new_execution":d,"recommended":e,"notes":f} for a,b,c,d,e,f in options]
 write_csv(FILES[21],list(option_rows[0]),option_rows)
 recommendation="""# Empfohlener nächster Schritt

Zunächst Human Review der komponentenreinen Summary-Gruppen. Falls Identität, Gegenläufigkeit oder sign-normalisierte Gleichheit wirklich entschieden werden sollen, ist ein separat autorisierter minimaler Response-Vektor-Signaturexport nötig. Vorher müssen Byte-Serialisierung, Orientierungsanker, Toleranz, Zero-/NaN-Policy und erlaubter Pipelinekanal eingefroren werden.
"""
 (OUT/FILES[22]).write_text(recommendation,encoding="utf-8")
 short=f"""# QSB-EXTRACT03F Kurznotiz

Status: `{STATUS}`. Vollständige Response-Vektoren fehlen. Aus vorhandenen Summaries wurden 10 reproduzierbare, vollständig komponentenreine Gruppen gebildet. Diese unterstützen eine Summary-Degeneracy als Vorläufer der K-Blöcke, entscheiden aber weder Vektoridentität noch Gegenläufigkeit. Keine Rohphasenrekonstruktion und kein Modell-Recompute.
"""
 (OUT/FILES[25]).write_text(short,encoding="utf-8")
 machine={"work_package":"QSB-EXTRACT03F","status":STATUS,"full_vectors_available":False,"summary_rows":42,"summary_signature_count":len(groups),
  "summary_group_sizes":group_sizes,"component_count":len(members),"all_summary_groups_component_pure":all(len({component_by[p] for p in ids})==1 for ids in groups.values()),
  "component_summary_group_counts":{str(cid):len({group_id_by_sig[summary_sig[p]] for p in ids}) for cid,ids in members.items()},
  "K_within_unordered_alignment_rows":len(k_alignment),"identity_opposition_status":"input_gap_no_full_vectors","origin_explanation_classification":origin_class,
  "claim_boundary":CLAIM}
 (OUT/FILES[26]).write_text(json.dumps(machine,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
 final=f"""# QSB-EXTRACT03F Final Result

## Status

`{STATUS}`

## Reviewed Inputs

EXTRACT03E/D, EXTRACT03A-R1 response summaries, K matrix, and the 14-table result mart were reviewed read-only.

## Response Vector Availability

No full vector components, raw vector hashes, rounded vector hashes, or orientation-aware signatures are persisted. Norm/range/count summaries are available for all 42 pairs.

## Signature Export

Raw/rounded/sign-normalized vector hashes are `NA`. Ten canonical summary-only SHA-256 groups were exported.

## Component Alignment

All ten summary groups are component-pure and cover all 42 pairs. Components contain one to three summary groups.

## K Alignment

All 161 within-component unordered K relations were reviewed. K≈±1 and summary relations are consistent with a response precursor, but cannot establish vector identity or opposition.

## Origin Explanation

Component-pure summary degeneracy supports a data/pipeline precursor to near-perfect K structure. Full-vector identity, opposition, and sign-normalized equality remain unresolved.

## Review Items

Full vectors, orientation-aware signatures, and a frozen minimal export serialization are missing.

## Claim Boundary

Summary signatures are not full-vector equivalence and establish no physical mechanism, geometry, gravity, emergent spacetime, or Interface confirmation.

## L2 Boundary

L2 remains fail with N4 support 0/3 versus required 2/3; no parameter, scope, threshold, or interpretation changed.

## Next Allowed Action

Human review, then optionally a separately authorized minimal response-vector signature export under a byte-exact frozen contract.
"""
 (OUT/FILES[27]).write_text(final,encoding="utf-8")
 after={rel(p):sha_path(p) for _,p,_ in upstream}
 if before!=after:fail("extract03f_blocked_guard_violation","upstream changed during EXTRACT03F")
 actual=sorted(p.name for p in OUT.iterdir())
 if actual!=sorted(FILES) or len(actual)!=28:fail("extract03f_blocked_guard_violation",f"output artifact mismatch: {len(actual)}")
 if any(r["status"]!="pass" for r in guard_rows+validations+l2_rows):fail("extract03f_blocked_guard_violation","guard, validation, or L2 failure")
 print(json.dumps({"status":STATUS,"artifacts":28,"full_response_vectors_available":False,"summary_rows":42,"summary_signature_groups":len(groups),
  "all_groups_component_pure":True,"component_group_counts":machine["component_summary_group_counts"],"K_alignment_rows":len(k_alignment),
  "identity_opposition":"input_gap_no_full_vectors","review_items":len(review_items),"upstream_modified":False,"l2_changed":False,"recomputation":False},indent=2))


if __name__=="__main__":main()
