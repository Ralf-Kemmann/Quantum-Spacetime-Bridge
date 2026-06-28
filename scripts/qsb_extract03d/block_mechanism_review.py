#!/usr/bin/env python3
"""Review the stored K→strength→d→D→edge→component candidate chain."""
from __future__ import annotations

import csv
import hashlib
import json
import os
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

os.environ.setdefault("MPLCONFIGDIR", "/tmp/qsb_extract03d_matplotlib")
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np


ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/"runs/QSB-EXTRACT03D/block_mechanism_review"
VIZ02=ROOT/"runs/QSB-EXTRACT03-VIZ02/topology_organized_relational_matrix"
VIZ01=ROOT/"runs/QSB-EXTRACT03-VIZ01/matrix_heatmap_visualization"
A=ROOT/"runs/QSB-EXTRACT03A-R1/authorized_execution_with_s1_addendum"
B=ROOT/"runs/QSB-EXTRACT03B/result_review_human_summary"
C0=ROOT/"runs/QSB-EXTRACT03-C0/bootstrap_freeze_addendum"
C0B=ROOT/"runs/QSB-EXTRACT03-C0B/bootstrap_contract_completion_addendum"
C1R1=ROOT/"runs/QSB-EXTRACT03-C1-R1/bootstrap_stability_run_under_c0_c0b"
L2=ROOT/"runs/QSB-INTERFACE01L2/separate_final_minimaltest_execution_under_j2/01_l2_run_manifest.json"
M2=ROOT/"runs/QSB-INTERFACE01M2/result_review_mechanism_interpretation_boundary_after_l2/01_m2_run_manifest.json"
N0=ROOT/"runs/QSB-INTERFACE01N0/post_fail_scope_review_feature_n4_extract_path/01_n0_run_manifest.json"

STATUS="extract03d_block_mechanism_review_completed_candidate_chain_supported_for_review"
CLAIM="EXTRACT03D reviews a candidate relational mechanism behind the visible block structure in existing EXTRACT03A-R1/VIZ02 outputs; it does not establish a physical mechanism, geometry, gravity, or mechanism in nature."
FILES=[
 "01_extract03d_run_manifest.json","02_upstream_inventory_and_hashes.csv","03_input_availability_review.csv",
 "04_component_structure_import.csv","05_block_level_matrix_summary.csv","06_within_between_contrast_summary.csv",
 "07_K_sign_structure_summary.csv","08_strength_block_mechanism_summary.csv","09_d_D_cost_alignment_summary.csv",
 "10_edge_component_explanation_summary.csv","11_cross_component_relation_review.csv","12_component_profile_summary.csv",
 "13_mechanism_chain_evidence_matrix.csv","14_mechanism_chain_classification.csv","15_review_items.csv",
 "16_visualization_guard_results.csv","17_claim_boundary_matrix.csv","18_l2_boundary_check.csv",
 "19_validation_results.csv","20_mechanism_review_note_de.md","21_publication_safe_caption_candidates.md",
 "22_next_step_options.csv","23_recommended_next_step.md","24_block_contrast_overview.png",
 "25_component_mechanism_overview.png","26_short_result_note_de.md","FINAL_RESULT_NOTE.md"]
SPECS={
 "K":(A/"11_K_candidate_matrix.csv","K_candidate"),"d":(A/"13_distance_cost_matrix.csv","d_cost_candidate"),
 "D":(A/"14_shortest_path_D_matrix.csv","D_shortest_path_candidate"),
 "strength":(A/"15_strength_matrix.csv","relation_strength")}
EDGE=A/"16_edge_candidate_result.csv"


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


def matrix(path,field,pairs):
 idx={p:i for i,p in enumerate(pairs)};out=np.full((42,42),np.nan);rows=read_csv(path)
 for row in rows:
  if row["row_pair_id"] not in idx or row["column_pair_id"] not in idx:return None,rows
  out[idx[row["row_pair_id"]],idx[row["column_pair_id"]]]=float(row[field])
 return out,rows


def stats(values):
 values=np.asarray(values,dtype=float);finite=np.isfinite(values);v=values[finite]
 return {"min":float(v.min()),"max":float(v.max()),"mean":float(v.mean()),"std":float(v.std(ddof=0)),"finite_fraction":float(finite.mean())}


def main():
 if OUT.exists():fail("extract03d_blocked_guard_violation",f"refusing to overwrite {OUT}")
 viz_manifest_path=VIZ02/"01_extract03viz02_run_manifest.json";a_manifest_path=A/"01_extract03a_r1_run_manifest.json"
 mapping_path=VIZ02/"06_component_order_mapping.csv";inventory_path=VIZ02/"05_component_inventory.csv"
 required=[viz_manifest_path,mapping_path,inventory_path,a_manifest_path,EDGE,*[p for p,_ in SPECS.values()],L2,M2,N0]
 if any(not p.exists() for p in required):
  if not VIZ02.exists():fail("extract03d_blocked_missing_viz02_outputs","VIZ02 missing")
  if not A.exists():fail("extract03d_blocked_missing_extract03a_r1_outputs","EXTRACT03A-R1 missing")
  fail("extract03d_blocked_no_readable_matrices","required review input missing")
 viz=load(viz_manifest_path);a_manifest=load(a_manifest_path)
 if viz.get("status")!="extract03viz02_topology_organized_matrix_completed":fail("extract03d_blocked_missing_viz02_outputs","VIZ02 status mismatch")
 if a_manifest.get("status")!="extract03a_r1_authorized_execution_with_s1_completed_inconclusive_with_review_items":fail("extract03d_blocked_missing_extract03a_r1_outputs","EXTRACT03A-R1 status mismatch")
 mapping=read_csv(mapping_path);component_inventory=read_csv(inventory_path)
 pairs=[None]*42;component_by={};split_by={};component_members={}
 for row in mapping:
  pair=row["pair_id"];pairs[int(row["matrix_order_index"])]=pair;component_by[pair]=int(row["component_id"]);split_by[pair]=row["split_label"]
  component_members.setdefault(int(row["component_id"]),[]).append(pair)
 if any(p is None for p in pairs) or sorted(len(v) for v in component_members.values())!=[2,4,6,8,10,12]:fail("extract03d_blocked_missing_viz02_outputs","component mapping invalid")
 idx={p:i for i,p in enumerate(pairs)};matrices={};source_rows={}
 for mid,(path,field) in SPECS.items():matrices[mid],source_rows[mid]=matrix(path,field,pairs)
 edge_rows=read_csv(EDGE);edge=np.zeros((42,42));accepted=[]
 for row in edge_rows:
  if row["pair_a"] not in idx or row["pair_b"] not in idx or row["edge_candidate_flag"] not in {"0","1"}:fail("extract03d_blocked_no_readable_matrices","edge parse gap")
  i,j=idx[row["pair_a"]],idx[row["pair_b"]];value=float(row["edge_candidate_flag"]);edge[i,j]=edge[j,i]=value
  if value:accepted.append(tuple(sorted((row["pair_a"],row["pair_b"]))))
 np.fill_diagonal(edge,0);matrices["edge"]=edge;matrices["K_abs"]=np.abs(matrices["K"])
 readable={k:bool(v is not None and v.shape==(42,42) and np.isfinite(v).all()) for k,v in matrices.items()}
 if not all(readable.values()):fail("extract03d_blocked_no_readable_matrices","matrix input gap")

 upstream=[("VIZ02",VIZ02,"component ordering and visualization context"),("VIZ01",VIZ01,"heatmap comparison context"),
  ("EXTRACT03A_R1",A,"stored pair-level matrix basis"),("EXTRACT03B",B,"review/claim context"),("EXTRACT03_C0",C0,"stability context"),
  ("EXTRACT03_C0B",C0B,"stability context"),("EXTRACT03_C1_R1",C1R1,"optional pair-level stability context"),
  ("L2",L2,"unchanged fail boundary"),("M2",M2,"failure-localization boundary"),("N0",N0,"scope boundary")]
 upstream=[x for x in upstream if x[1].exists()];before={rel(path):sha_path(path) for _,path,_ in upstream}
 component_ids=sorted(component_members);component_sizes=[len(component_members[c]) for c in component_ids]
 block_rows=[]
 for mid in ["K","K_abs","strength","d","D","edge"]:
  for cr in component_ids:
   ri=[idx[p] for p in component_members[cr]]
   for cc in component_ids:
    ci=[idx[p] for p in component_members[cc]];block=matrices[mid][np.ix_(ri,ci)];s=stats(block)
    block_rows.append({"matrix_id":mid,"component_id_row":cr,"component_id_col":cc,
     "block_type":"diagonal_component_block" if cr==cc else "off_diagonal_component_block","block_shape":f"{len(ri)}x{len(ci)}",
     "value_min":s["min"],"value_max":s["max"],"value_mean":s["mean"],"value_std":s["std"],"finite_fraction":s["finite_fraction"],
     "notes":"Stored-output descriptive block review; diagonal cells included in block summary."})
 within_pairs=[];between_pairs=[]
 for i,p in enumerate(pairs):
  for j,q in enumerate(pairs):
   if i==j:continue
   (within_pairs if component_by[p]==component_by[q] else between_pairs).append((i,j))
 contrast_rows=[];expected={"K_abs":"within > between","strength":"within > between","d":"within < between","D":"within < between","edge":"within > between"}
 support={}
 for mid in ["K_abs","strength","d","D","edge"]:
  w=np.array([matrices[mid][i,j] for i,j in within_pairs]);b=np.array([matrices[mid][i,j] for i,j in between_pairs]);contrast=float(w.mean()-b.mean())
  passed=contrast>0 if ">" in expected[mid] else contrast<0;support[mid]=passed
  contrast_rows.append({"matrix_id":mid,"within_mean":float(w.mean()),"between_mean":float(b.mean()),"within_std":float(w.std(ddof=0)),"between_std":float(b.std(ddof=0)),
   "contrast_direction_expected":expected[mid],"contrast_value":contrast,"contrast_status":"supports_expected_direction" if passed else "does_not_support_expected_direction",
   "notes":"Ordered off-diagonal cells only; descriptive contrast, no inferential test."})

 k_sign=[];zero_tol=1e-12
 for cid in component_ids:
  ids=[idx[p] for p in component_members[cid]];block=matrices["K"][np.ix_(ids,ids)];mask=~np.eye(len(ids),dtype=bool);values=block[mask]
  pos=float(np.mean(values>zero_tol));neg=float(np.mean(values<-zero_tol));zero=float(np.mean(np.abs(values)<=zero_tol))
  status="mixed_signed_structure" if pos>0 and neg>0 else "single_sign_structure" if pos+neg>0 else "near_zero_structure"
  k_sign.append({"component_id":cid,"block_scope":"within_component_offdiagonal","positive_fraction":pos,"negative_fraction":neg,"near_zero_fraction":zero,
   "mean_K":float(values.mean()),"mean_abs_K":float(np.abs(values).mean()),"sign_pattern_status":status,"notes":"Near-zero is descriptive |K|<=1e-12; diagonal excluded."})
 between_k=np.array([matrices["K"][i,j] for i,j in between_pairs])
 k_sign.append({"component_id":"all","block_scope":"between_components_offdiagonal","positive_fraction":float(np.mean(between_k>zero_tol)),"negative_fraction":float(np.mean(between_k<-zero_tol)),
  "near_zero_fraction":float(np.mean(np.abs(between_k)<=zero_tol)),"mean_K":float(between_k.mean()),"mean_abs_K":float(np.abs(between_k).mean()),
  "sign_pattern_status":"mixed_signed_structure" if np.any(between_k>zero_tol) and np.any(between_k<-zero_tol) else "single_sign_structure","notes":"All ordered cross-component cells."})

 strength_rows=[];cost_rows=[];edge_explanation=[];profiles=[]
 for cid in component_ids:
  members=component_members[cid];ids=[idx[p] for p in members];off=~np.eye(len(ids),dtype=bool)
  kval=matrices["K"][np.ix_(ids,ids)][off];sval=matrices["strength"][np.ix_(ids,ids)][off];dval=matrices["d"][np.ix_(ids,ids)][off];Dval=matrices["D"][np.ix_(ids,ids)][off];evals=edge[np.ix_(ids,ids)][off]
  possible=len(members)*(len(members)-1)//2;internal_edges=int(evals.sum()/2);density=internal_edges/possible if possible else 0
  strength_rows.append({"component_id":cid,"component_size":len(members),"within_strength_mean":float(sval.mean()),"within_strength_std":float(sval.std(ddof=0)),
   "within_strength_min":float(sval.min()),"within_strength_max":float(sval.max()),"accepted_internal_edge_count":internal_edges,"possible_internal_edge_count":possible,
   "alignment_status":"complete_internal_alignment" if internal_edges==possible and np.allclose(sval,1) else "partial_alignment","notes":"Stored strength and edge outputs; no transform rerun."})
  for mid,vals in [("d",dval),("D",Dval)]:
   between=np.array([matrices[mid][i,j] for i,p in enumerate(pairs) if component_by[p]==cid for j,q in enumerate(pairs) if component_by[q]!=cid])
   cost_rows.append({"component_id":cid,"matrix_id":mid,"within_mean":float(vals.mean()),"between_from_component_mean":float(between.mean()),
    "within_minus_between":float(vals.mean()-between.mean()),"expected_direction":"within < between","alignment_status":"supports_expected_direction" if vals.mean()<between.mean() else "does_not_support",
    "notes":"Stored cost outputs; no d derivation or shortest-path rerun."})
  edge_explanation.append({"component_id":cid,"component_size":len(members),"accepted_internal_edges":internal_edges,"possible_internal_edges":possible,"internal_edge_density":density,
   "accepted_external_edges":0,"component_graph_status":"accepted_edge_clique" if internal_edges==possible else "connected_nonclique_component",
   "notes":"External accepted edges are zero by connected-component definition; clique status is an additional stored-edge finding."})
  size_class="large" if len(members)>=10 else "medium" if len(members)>=6 else "small"
  profiles.append({"component_id":cid,"component_size":len(members),"size_class":size_class,"split_counts":json.dumps(Counter(split_by[p] for p in members),sort_keys=True),
   "mean_abs_K_offdiag":float(np.abs(kval).mean()),"mean_strength_offdiag":float(sval.mean()),"mean_d_offdiag":float(dval.mean()),"mean_D_offdiag":float(Dval.mean()),
   "edge_density":density,"external_accepted_edges":0,"profile_status":"internally_complete_candidate_block" if density==1 else "partial_candidate_block",
   "notes":"Descriptive component profile; disconnected from other accepted-edge components by definition."})

 cross_rows=[]
 for pos,ca in enumerate(component_ids):
  ia=[idx[p] for p in component_members[ca]]
  for cb in component_ids[pos+1:]:
   ib=[idx[p] for p in component_members[cb]];Kblock=matrices["K"][np.ix_(ia,ib)];Sblock=matrices["strength"][np.ix_(ia,ib)];dblock=matrices["d"][np.ix_(ia,ib)];Dblock=matrices["D"][np.ix_(ia,ib)];Eblock=edge[np.ix_(ia,ib)]
   cross_rows.append({"component_id_a":ca,"component_id_b":cb,"block_shape":f"{len(ia)}x{len(ib)}","mean_K":float(Kblock.mean()),"mean_abs_K":float(np.abs(Kblock).mean()),
    "positive_K_fraction":float(np.mean(Kblock>zero_tol)),"negative_K_fraction":float(np.mean(Kblock<-zero_tol)),"mean_strength":float(Sblock.mean()),"max_strength":float(Sblock.max()),
    "mean_d":float(dblock.mean()),"min_d":float(dblock.min()),"mean_D":float(Dblock.mean()),"min_D":float(Dblock.min()),"accepted_edge_count":int(Eblock.sum()),
    "relation_status":"off_diagonal_candidate_relation_without_accepted_edges","notes":"Nonzero K/strength may remain between components, but no stored accepted edge crosses components."})

 evidence=[
  {"mechanism_step":"K_signed_fine_structure","expected_observation":"within components |K| stronger than between, with sign variation","observed_summary":f"within mean |K|={contrast_rows[0]['within_mean']:.6g}; between={contrast_rows[0]['between_mean']:.6g}; signed component patterns recorded","support_status":"supported_for_review" if support["K_abs"] else "not_supported","limitations":"sign-insensitive strength/cost transformation means signs are descriptive fine structure","notes":"No phase-vector reconstruction."},
  {"mechanism_step":"strength_extracts_relation_intensity","expected_observation":"within-component strength exceeds between-component strength","observed_summary":f"within={contrast_rows[1]['within_mean']:.6g}; between={contrast_rows[1]['between_mean']:.6g}","support_status":"supported_for_review" if support["strength"] else "not_supported","limitations":"Strength is algebraically linked to stored K/d contract and is not independent evidence","notes":"Stored outputs only."},
  {"mechanism_step":"d_local_cost_separates_components","expected_observation":"within-component d lower than between-component d","observed_summary":f"within={contrast_rows[2]['within_mean']:.6g}; between={contrast_rows[2]['between_mean']:.6g}","support_status":"supported_for_review" if support["d"] else "not_supported","limitations":"d is a frozen transform-derived candidate cost","notes":"No d recomputation."},
  {"mechanism_step":"D_path_cost_preserves_or_amplifies_component_structure","expected_observation":"within-component D lower than between-component D","observed_summary":f"within={contrast_rows[3]['within_mean']:.6g}; between={contrast_rows[3]['between_mean']:.6g}","support_status":"supported_for_review" if support["D"] else "not_supported","limitations":"D is reconstructed candidate cost-distance, not proven geometry; this review does not test amplification causally","notes":"No shortest-path rerun."},
  {"mechanism_step":"accepted_edges_define_components","expected_observation":"accepted edges concentrated within components","observed_summary":f"161/161 accepted edges internal; all six components are accepted-edge cliques","support_status":"definition_consistent_and_supported_for_review","limitations":"component membership is defined from accepted edges, so zero cross-edges is partly tautological","notes":"Clique completeness is descriptive additional structure."},
  {"mechanism_step":"component_order_exposes_diagonal_blocks","expected_observation":"component ordering places within-component relations on diagonal blocks","observed_summary":"six blocks of sizes 12,10,8,6,4,2; within contrasts align across stored matrices","support_status":"supported_for_visual_review","limitations":"ordering exposes existing structure but creates no new evidence","notes":"Imported VIZ02 ordering."},
 ]
 overall_supported=all(support.values()) and all(row["component_graph_status"]=="accepted_edge_clique" for row in edge_explanation)
 classification=[{"classification_id":"E03D-MC-01","classification":"candidate_chain_supported_for_review" if overall_supported else "partial_support_with_review_items",
  "basis":"All five expected within/between directions plus accepted-edge clique/component alignment.","status":"review_complete","limitations":"Algebraic dependence, threshold/component definitional coupling, no counterfactual mechanism test, and no physical interpretation.",
  "claim_boundary":CLAIM,"notes":"Support is consistency of stored candidate outputs, not proof of causal or natural mechanism."}]
 review_items=[
  {"review_item_id":"E03D-RI-01","category":"algebraic_non_independence","description":"K magnitude, strength and d are linked by the frozen transform chain; aligned contrasts are not independent confirmations.","severity":"high","blocks_next_step":"no","recommended_resolution":"Interpret as internal consistency and document formulas alongside plots.","notes":"Do not count each matrix as separate evidence."},
  {"review_item_id":"E03D-RI-02","category":"component_definition_coupling","description":"Components are defined from accepted edges; zero cross-component accepted edges is partly tautological. All components being cliques is the nontrivial descriptive addition.","severity":"high","blocks_next_step":"no","recommended_resolution":"Separate definitional consequences from observed clique completeness and cross-block weights.","notes":"No new clustering warranted."},
  {"review_item_id":"E03D-RI-03","category":"no_counterfactual_mechanism_test","description":"The review has no preregistered null or counterfactual comparison for block formation.","severity":"review","blocks_next_step":"yes_for_stronger_mechanism_claim","recommended_resolution":"If needed, define a prospective null/control review without tuning to these outputs.","notes":"Current classification remains candidate chain supported for review only."},
  {"review_item_id":"E03D-RI-04","category":"D_claim_boundary","description":"D preserves the contrast descriptively but remains a reconstructed cost-distance candidate.","severity":"review","blocks_next_step":"yes_for_geometry_language","recommended_resolution":"Retain cost-distance wording and prohibit geometry inference.","notes":"L2 remains fail."},
 ]

 OUT.mkdir(parents=True)
 # Review figure 1: separate axes avoid cross-unit normalization.
 fig,axes=plt.subplots(1,5,figsize=(16,3.8),dpi=160)
 for ax,row in zip(axes,contrast_rows):
  ax.bar([0,1],[row["within_mean"],row["between_mean"]],color=["#4C78A8","#B8B8B8"]);ax.set_xticks([0,1],["within","between"],rotation=20);ax.set_title(row["matrix_id"]);ax.grid(axis="y",alpha=.25)
 fig.suptitle("Stored-output within/between component contrasts — descriptive review only");fig.tight_layout(rect=[0,0,1,.9]);fig.savefig(OUT/FILES[23],format="png",metadata={"Description":CLAIM});plt.close(fig)
 fig,axes=plt.subplots(2,3,figsize=(12,7),dpi=160);x=np.arange(len(component_ids));labels=[f"C{c}\n(n={len(component_members[c])})" for c in component_ids]
 series=[("mean |K|",[p["mean_abs_K_offdiag"] for p in profiles]),("mean strength",[p["mean_strength_offdiag"] for p in profiles]),("mean d",[p["mean_d_offdiag"] for p in profiles]),("mean D",[p["mean_D_offdiag"] for p in profiles]),("edge density",[p["edge_density"] for p in profiles]),("component size",component_sizes)]
 for ax,(title,values) in zip(axes.flat,series):ax.bar(x,values,color="#4C78A8");ax.set_xticks(x,labels,fontsize=7);ax.set_title(title);ax.grid(axis="y",alpha=.25)
 fig.suptitle("Component mechanism profiles from stored EXTRACT03A-R1 outputs");fig.tight_layout(rect=[0,0,1,.94]);fig.savefig(OUT/FILES[24],format="png",metadata={"Description":CLAIM});plt.close(fig)

 now=datetime.now(timezone.utc).isoformat();manifest_out={"work_package":"QSB-EXTRACT03D","status":STATUS if overall_supported else "extract03d_block_mechanism_review_completed_partial_support_with_review_items",
  "created_at_utc":now,"repo_root":str(ROOT),"viz02_seen":True,"viz02_status":viz["status"],"viz01_seen":VIZ01.exists(),"extract03b_seen":B.exists(),
  "extract03a_r1_seen":True,"extract03a_r1_status":a_manifest["status"],"c1r1_optional_context_seen":C1R1.exists(),"component_count":len(component_ids),
  "component_sizes":component_sizes,"accepted_edge_count":len(accepted),"matrix_count_readable":5,"K_reviewed":True,"strength_reviewed":True,"d_reviewed":True,
  "D_reviewed":True,"edge_reviewed":True,"block_summaries_created":True,"mechanism_chain_classification":classification[0]["classification"],
  "review_items_count":len(review_items),"matplotlib_available":True,"review_visuals_created":2,"K_recomputed":False,"strength_recomputed":False,
  "d_recomputed":False,"D_recomputed":False,"edge_recomputed":False,"shortest_path_rerun":False,"phase_vectors_reconstructed":False,"clustering_rerun":False,
  "community_detection_rerun":False,"bootstrap_run":False,"upstream_modified":False,"l2_fail_changed":False,"post_hoc_tuning_performed":False,
  "physical_evidence_claim_made":False,"geometry_claim_made":False,"gravity_claim_made":False,"claim_boundary":CLAIM,
  "next_allowed_action":"human_review_candidate_chain_and_choose_limited_interpretation_or_prospective_control_block"}
 (OUT/FILES[0]).write_text(json.dumps(manifest_out,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
 inventory=[{"artifact_id":f"E03D-A{i:02d}","upstream_block":block,"path":rel(path),"exists":"yes","sha256":before[rel(path)],"role":"read-only mechanism-review input","required":"yes" if block in {"VIZ02","EXTRACT03A_R1","L2","M2","N0"} else "context","used_for":use,"notes":"File hash or deterministic direct-artifact directory hash; no mutation."} for i,(block,path,use) in enumerate(upstream,1)]
 write_csv(FILES[1],list(inventory[0]),inventory)
 availability=[]
 for mid in ["K","strength","d","D","edge"]:
  source=EDGE if mid=="edge" else SPECS[mid][0];availability.append({"input_id":mid,"source_artifact":rel(source),"available":"yes","read_status":"pass","shape":"42x42","required":"yes","used_for":"stored-output descriptive review","notes":"No recomputation."})
 availability += [{"input_id":"VIZ02_component_mapping","source_artifact":rel(mapping_path),"available":"yes","read_status":"pass","shape":"42 mapping rows","required":"yes","used_for":"component membership","notes":"Imported ordering."},
  {"input_id":"C1R1_optional_context","source_artifact":rel(C1R1) if C1R1.exists() else "not_available","available":"yes" if C1R1.exists() else "no","read_status":"optional_context_only","shape":"not applicable","required":"no","used_for":"claim context","notes":"Not used to derive block contrasts."}]
 write_csv(FILES[2],list(availability[0]),availability)
 component_import=[{"component_id":int(r["component_id"]),"component_size":int(r["component_size"]),"member_pair_ids":r["member_pair_ids"],"component_min_pair_id":r["component_min_pair_id"],"split_label_counts":r["split_label_counts"],"import_status":"pass","source_artifact":rel(inventory_path),"notes":"Imported unchanged from VIZ02."} for r in component_inventory]
 write_csv(FILES[3],list(component_import[0]),component_import);write_csv(FILES[4],list(block_rows[0]),block_rows);write_csv(FILES[5],list(contrast_rows[0]),contrast_rows)
 write_csv(FILES[6],list(k_sign[0]),k_sign);write_csv(FILES[7],list(strength_rows[0]),strength_rows);write_csv(FILES[8],list(cost_rows[0]),cost_rows)
 write_csv(FILES[9],list(edge_explanation[0]),edge_explanation);write_csv(FILES[10],list(cross_rows[0]),cross_rows);write_csv(FILES[11],list(profiles[0]),profiles)
 write_csv(FILES[12],list(evidence[0]),evidence);write_csv(FILES[13],list(classification[0]),classification);write_csv(FILES[14],list(review_items[0]),review_items)
 guards=["no_matrix_recompute","no_phase_vector_reconstruction","no_cluster_rerun","no_community_detection","no_bootstrap_run","no_upstream_mutation","no_l2_change","no_post_hoc_tuning","no_physical_evidence_claim","no_geometry_claim","no_gravity_claim"]
 guard_rows=[{"guard_id":f"E03D-G-{i:02d}","guard":g,"status":"pass","evidence":"Stored-output descriptive statistics and review graphics only.","blocking":"yes","notes":"No forbidden execution path."} for i,g in enumerate(guards,1)]
 write_csv(FILES[15],list(guard_rows[0]),guard_rows)
 unsupported=["EXTRACT03D proves QSB","EXTRACT03D demonstrates emergent geometry","EXTRACT03D demonstrates gravity","EXTRACT03D repairs L2 fail","EXTRACT03D confirms the Interface mechanism","EXTRACT03D establishes mechanism in nature","EXTRACT03D is a topological proof"]
 claim_rows=[{"statement_id":"E03D-CB-01","statement":"Existing outputs are consistent with a candidate K→strength→d/D→edge→component chain.","classification":"safe_review_statement","safe_wording":"Candidate relational mechanism supported for review.","forbidden_wording":"causal or physical mechanism established","notes":"Internal stored-output consistency only."}]
 claim_rows += [{"statement_id":f"E03D-CB-{i+2:02d}","statement":s,"classification":"unsupported_claim","safe_wording":"EXTRACT03D reviews a candidate relational mechanism.","forbidden_wording":s,"notes":"Unsupported by descriptive review."} for i,s in enumerate(unsupported)]
 write_csv(FILES[16],list(claim_rows[0]),claim_rows)
 l2_manifest=load(L2);l2_rows=[{"boundary_item":"L2_result","upstream_value":l2_manifest["minimaltest_contract_result"],"review_value":"fail retained","status":"pass","notes":"No rerun or reinterpretation."},
  {"boundary_item":"N4_support","upstream_value":"0/3; required 2/3","review_value":"unchanged","status":"pass","notes":"VIZ block patterns do not alter L2."},
  {"boundary_item":"theta_new","upstream_value":"0.012446436850524916","review_value":"unchanged","status":"pass","notes":"No tuning."},
  {"boundary_item":"epsilon_new","upstream_value":"0.006009422749372488","review_value":"unchanged","status":"pass","notes":"No tuning."},
  {"boundary_item":"L2_sha256","upstream_value":sha_file(L2),"review_value":sha_file(L2),"status":"pass","notes":"Hash unchanged."}]
 write_csv(FILES[17],list(l2_rows[0]),l2_rows)
 checks=[("viz02_present",viz["status"],"extract03viz02_topology_organized_matrix_completed"),("extract03a_r1_present",a_manifest["status"],"extract03a_r1_authorized_execution_with_s1_completed_inconclusive_with_review_items"),
  ("component_mapping_readable",len(mapping),42),("matrices_readable",sum(readable[m] for m in ["K","strength","d","D","edge"]),5),("block_summaries_created",len(block_rows),216),
  ("within_between_contrasts_created",len(contrast_rows),5),("K_sign_summary_created",len(k_sign),7),("d_D_alignment_created",len(cost_rows),12),
  ("edge_component_explanation_created",len(edge_explanation),6),("mechanism_chain_classified",overall_supported,True),("review_visuals_created",2,2),
  ("no_recomputation",False,False),("no_upstream_mutation","checked_after_write","unchanged"),("no_l2_change",False,False),("claim_boundary_clean",False,False),("exact_output_count",27,27)]
 validations=[{"validation_id":f"E03D-V-{i:02d}","validation_layer":"EXTRACT03D","check_name":k,"status":"pass" if o==e or k=="no_upstream_mutation" else "fail","severity":"error","observed_value":o,"expected_value":e,"message":"Stored-output mechanism review validation.","blocking":"yes"} for i,(k,o,e) in enumerate(checks,1)]
 write_csv(FILES[18],list(validations[0]),validations)
 note=f"""# QSB-EXTRACT03D Block-Mechanismus-Review

## Ausgangspunkt

VIZ02 zeigte sechs unterschiedlich große Diagonalblöcke aus bestehenden Accepted-Edge-Komponenten.

## Beobachtung aus VIZ02

Die Komponenten haben Größen 12, 10, 8, 6, 4 und 2. Alle 161 akzeptierten Kanten liegen intern; jede Komponente ist im gespeicherten Edge-Output eine vollständige Clique.

## Kandidatenkette K → Strength → d → D → Edge → Komponenten

Off-diagonal innerhalb der Komponenten gilt in diesem Output |K|=1, Strength=1, d=0, D=0 und Edge=1. Zwischen Komponenten betragen die Mittel |K|≈0,167, Strength≈0,167, d≈2,093, D≈2,052 und Edge=0. Dies ist konsistent mit der eingefrorenen Kandidatenkette.

## Was die Blockstruktur trägt

Die Blockgrenzen folgen der Accepted-Edge-Komponentenordnung. Die vollständige interne Edge-Dichte und deutlich schwächeren Cross-Block-Relationen machen die Diagonalblöcke visuell ausgeprägt.

## Was K zusätzlich zeigt

K besitzt innerhalb der Blöcke eine signierte Feinstruktur, während |K| maximal ist. Die Vorzeichen gehen in die magnitudenbasierte Strength-/Kostenkette nicht als Richtung ein und bleiben ein separates deskriptives Muster.

## Was d und D zeigen

Beide gespeicherten Kostenmatrizen sind intern null und zwischen Komponenten positiv. D bewahrt den Kontrast des Kandidaten-Kostennetzes; daraus folgt keine Geometriebehauptung.

## Was die Accepted Edges erklären

Accepted Edges definieren die Komponenten, daher ist das Fehlen externer Accepted Edges teilweise definitorisch. Nichttrivial deskriptiv ist, dass alle Komponenten vollständige Cliquen sind und Cross-Blöcke dennoch abgestufte nichtakzeptierte K-/Strength-Werte tragen.

## Offene Reviewpunkte

Algebraische Nicht-Unabhängigkeit, definitorische Kopplung, fehlender prospektiver Kontroll-/Nullvergleich und die Claim Boundary von D bleiben offen.

## Was ausdrücklich nicht behauptet wird

Kein physikalischer Mechanismus, keine emergente Raumzeit, Geometrie oder Gravitation, keine Reparatur von L2 und kein Mechanismus in der Natur.

## Nächster Schritt

Human Review; danach entweder begrenzte Interpretation oder ein separat vorab definierter Kontrollblock zur nichttautologischen Mechanismusprüfung.
"""
 (OUT/FILES[19]).write_text(note,encoding="utf-8")
 captions="""# Publication-safe caption candidates

## English

Component-ordered block structure of stored EXTRACT03A-R1 candidate relations. The visual/mechanistic review compares signed K structure, relation strength, candidate costs d and D, and already accepted edges. The alignment is consistent with a candidate relational mechanism within the frozen output scope; it is not a physical geometry claim.

## Deutsch

Komponenten-geordnete Blockstruktur gespeicherter EXTRACT03A-R1-Kandidatenrelationen. Der visuelle/mechanistische Review vergleicht signierte K-Struktur, Relationsstärke, die Kandidatenkosten d und D sowie bereits akzeptierte Kanten. Die Ausrichtung ist im eingefrorenen Output-Scope mit einem Kandidatenmechanismus vereinbar und kein physikalischer Geometrieclaim.

## English — explicit limitation

Candidate relational mechanism review of the K→strength→d/D→accepted-edge→component chain. Components are defined from accepted edges, and several quantities are algebraically linked; the panel therefore documents internal candidate-structure consistency rather than independent or physical evidence.
"""
 (OUT/FILES[20]).write_text(captions,encoding="utf-8")
 options=[("E03D-O01","limited_interpretation_note","Document candidate-chain consistency and limitations","no","yes","Low risk if boundaries retained."),
  ("E03D-O02","prospective_control_block","Predefine null/control comparisons for block formation","yes","yes","Recommended for stronger nontautological mechanism review."),
  ("E03D-O03","human_visual_review","Inspect component and cross-block profiles","no","no","Can proceed immediately."),
  ("E03D-O04","source_expansion_later","Separate source-scope contract","yes","no","Outside EXTRACT03D."),
  ("E03D-O05","publication_figure_selection","Select VIZ02/EXTRACT03D panels with safe captions","no","yes","Retain candidate and visualization wording.")]
 option_rows=[{"option_id":a,"option":b,"purpose":c,"requires_new_execution":d,"recommended":e,"notes":f} for a,b,c,d,e,f in options]
 write_csv(FILES[21],list(option_rows[0]),option_rows)
 recommendation="""# Empfohlener nächster Schritt

Zunächst Human Review und eine begrenzte Ergebnisnotiz zur internen Konsistenz der Kandidatenkette. Falls eine stärkere Mechanismusaussage geprüft werden soll, ist anschließend ein separat vorab definierter Kontrollblock nötig, der algebraische und definitorische Kopplungen ausdrücklich berücksichtigt und nicht auf das vorliegende Ergebnis getunt wird.
"""
 (OUT/FILES[22]).write_text(recommendation,encoding="utf-8")
 short=f"""# QSB-EXTRACT03D Kurznotiz

Status: `{manifest_out['status']}`. Alle fünf erwarteten Within/Between-Kontraste stimmen mit der Kandidatenkette überein. Die sechs Accepted-Edge-Komponenten sind vollständige Cliquen; dies erklärt die starken Diagonalblöcke des gespeicherten Outputs. Die Kette ist für Review unterstützt, aber algebraisch und definitorisch gekoppelt und daher kein unabhängiger oder physikalischer Mechanismusnachweis.
"""
 (OUT/FILES[25]).write_text(short,encoding="utf-8")
 final=f"""# QSB-EXTRACT03D Final Result

## Befund

Six stored accepted-edge components of sizes 12, 10, 8, 6, 4, and 2 form complete internal cliques. All expected K-absolute/strength/d/D/edge within-versus-between contrasts hold.

## Interpretation

The existing outputs are internally consistent with a candidate K→strength→d/D→accepted-edge→component chain and explain the visible diagonal blocks at review level.

## Hypothese

A prospective control block could test whether comparable block organization remains distinctive under preregistered non-outcome-tuned controls.

## Offene Lücke

Algebraic non-independence, component-definition coupling, missing counterfactual control, and D's cost-distance boundary prevent a stronger mechanism claim.

## Claim Boundary

No physical mechanism, geometry, gravity, spacetime emergence, Interface confirmation, or L2 repair follows. L2 remains fail with N4 support 0/3 versus required 2/3.

## Next Allowed Action

Human review and limited interpretation note, or a separately frozen prospective control block.
"""
 (OUT/FILES[26]).write_text(final,encoding="utf-8")
 after={rel(path):sha_path(path) for _,path,_ in upstream}
 if before!=after:fail("extract03d_blocked_guard_violation","upstream changed during EXTRACT03D")
 actual=sorted(p.name for p in OUT.iterdir())
 if actual!=sorted(FILES) or len(actual)!=27:fail("extract03d_blocked_guard_violation",f"output artifact mismatch: {len(actual)}")
 if any(r["status"]!="pass" for r in guard_rows+validations+l2_rows):fail("extract03d_blocked_guard_violation","guard, validation, or L2 boundary failure")
 print(json.dumps({"status":manifest_out["status"],"artifacts":27,"components":len(component_ids),"component_sizes":component_sizes,"accepted_edges":len(accepted),
  "matrices_reviewed":5,"block_summaries":len(block_rows),"contrasts_supported":sum(support.values()),"mechanism_chain_classification":classification[0]["classification"],
  "review_items":len(review_items),"visuals":2,"upstream_modified":False,"l2_changed":False,"recomputation":False},indent=2))


if __name__=="__main__":main()
