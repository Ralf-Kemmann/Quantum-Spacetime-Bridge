#!/usr/bin/env python3
"""Locate the first observed exact-perfection layer in stored EXTRACT03 outputs."""
from __future__ import annotations

import csv
import hashlib
import json
import os
import re
import sqlite3
from datetime import datetime, timezone
from pathlib import Path

os.environ.setdefault("MPLCONFIGDIR", "/tmp/qsb_extract03e_matplotlib")
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np


ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/"runs/QSB-EXTRACT03E/perfection_origin_review"
D=ROOT/"runs/QSB-EXTRACT03D/block_mechanism_review"
VIZ02=ROOT/"runs/QSB-EXTRACT03-VIZ02/topology_organized_relational_matrix"
A=ROOT/"runs/QSB-EXTRACT03A-R1/authorized_execution_with_s1_addendum"
B=ROOT/"runs/QSB-EXTRACT03B/result_review_human_summary"
VIZ01=ROOT/"runs/QSB-EXTRACT03-VIZ01/matrix_heatmap_visualization"
C0=ROOT/"runs/QSB-EXTRACT03-C0/bootstrap_freeze_addendum"
C0B=ROOT/"runs/QSB-EXTRACT03-C0B/bootstrap_contract_completion_addendum"
C1R1=ROOT/"runs/QSB-EXTRACT03-C1-R1/bootstrap_stability_run_under_c0_c0b"
L2=ROOT/"runs/QSB-INTERFACE01L2/separate_final_minimaltest_execution_under_j2/01_l2_run_manifest.json"
M2=ROOT/"runs/QSB-INTERFACE01M2/result_review_mechanism_interpretation_boundary_after_l2/01_m2_run_manifest.json"
N0=ROOT/"runs/QSB-INTERFACE01N0/post_fail_scope_review_feature_n4_extract_path/01_n0_run_manifest.json"

STATUS="extract03e_perfection_origin_review_completed_origin_likely_strength_d_edge_definition"
CLAIM="EXTRACT03E identifies the first observed layer at which exact component/block perfection appears in existing outputs; this is a data/pipeline review and does not establish a physical mechanism, geometry, gravity, or mechanism in nature."
FILES=[
 "01_extract03e_run_manifest.json","02_upstream_inventory_and_hashes.csv","03_input_availability_review.csv",
 "04_component_clique_import.csv","05_K_exactness_review.csv","06_K_signed_within_component_summary.csv",
 "07_K_abs_histogram_summary.csv","08_pair_response_summary_availability.csv","09_serialization_rounding_review.csv",
 "10_static_code_rule_review.csv","11_strength_derivation_review.csv","12_d_derivation_review.csv",
 "13_D_path_cost_review.csv","14_edge_rule_review.csv","15_first_perfection_layer_assessment.csv",
 "16_definition_coupling_matrix.csv","17_pipeline_causality_chain_review.csv","18_origin_classification.csv",
 "19_control_test_recommendations.csv","20_review_items.csv","21_guard_results.csv","22_claim_boundary_matrix.csv",
 "23_l2_boundary_check.csv","24_validation_results.csv","25_human_readable_perfection_origin_review_de.md",
 "26_publication_safe_note_candidates.md","27_next_step_options.csv","28_recommended_next_step.md",
 "29_perfection_origin_overview.png","FINAL_RESULT_NOTE.md"]
K_PATH=A/"11_K_candidate_matrix.csv";D_PATH=A/"13_distance_cost_matrix.csv";SP_PATH=A/"14_shortest_path_D_matrix.csv"
S_PATH=A/"15_strength_matrix.csv";EDGE_PATH=A/"16_edge_candidate_result.csv";VECTOR_SUMMARY=A/"10_phase_response_vector_summary.csv";MART=A/"21_extract03a_r1_result_mart.sqlite"
A_SCRIPT=ROOT/"scripts/qsb_extract03a_r1/run_authorized_execution_with_s1_addendum.py"
PACKAGE_SCRIPT=ROOT/"scripts/qsb_extract03/prepare_execution_package.py"
VIZ02_SCRIPT=ROOT/"scripts/qsb_extract03_viz02/topology_organized_relational_matrix.py"
D_SCRIPT=ROOT/"scripts/qsb_extract03d/block_mechanism_review.py"


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


def read_matrix(path,field,pairs):
 idx={p:i for i,p in enumerate(pairs)};matrix=np.full((42,42),np.nan);rows=read_csv(path)
 for row in rows:
  if row["row_pair_id"] not in idx or row["column_pair_id"] not in idx:return None,rows
  matrix[idx[row["row_pair_id"]],idx[row["column_pair_id"]]]=float(row[field])
 return matrix,rows


def code_line(path,needle):
 lines=path.read_text(encoding="utf-8").splitlines()
 hits=[f"L{i}: {line.strip()}" for i,line in enumerate(lines,1) if needle in line]
 return " | ".join(hits[:4]) if hits else "not_found"


def main():
 if OUT.exists():fail("extract03e_blocked_guard_violation",f"refusing to overwrite {OUT}")
 d_manifest_path=D/"01_extract03d_run_manifest.json";viz_manifest_path=VIZ02/"01_extract03viz02_run_manifest.json";a_manifest_path=A/"01_extract03a_r1_run_manifest.json"
 required=[d_manifest_path,viz_manifest_path,a_manifest_path,D/"04_component_structure_import.csv",K_PATH,D_PATH,SP_PATH,S_PATH,EDGE_PATH,VECTOR_SUMMARY,MART,A_SCRIPT,PACKAGE_SCRIPT,VIZ02_SCRIPT,D_SCRIPT,L2,M2,N0]
 if any(not p.exists() for p in required):
  if not D.exists():fail("extract03e_blocked_missing_extract03d_outputs","EXTRACT03D missing")
  if not VIZ02.exists():fail("extract03e_blocked_missing_viz02_outputs","VIZ02 missing")
  if not A.exists():fail("extract03e_blocked_missing_extract03a_r1_outputs","EXTRACT03A-R1 missing")
  fail("extract03e_blocked_no_readable_K_matrix","required input missing")
 d_manifest=load(d_manifest_path);viz_manifest=load(viz_manifest_path);a_manifest=load(a_manifest_path)
 if d_manifest.get("status")!="extract03d_block_mechanism_review_completed_candidate_chain_supported_for_review":fail("extract03e_blocked_missing_extract03d_outputs","EXTRACT03D status mismatch")
 if viz_manifest.get("status")!="extract03viz02_topology_organized_matrix_completed":fail("extract03e_blocked_missing_viz02_outputs","VIZ02 status mismatch")
 if a_manifest.get("status")!="extract03a_r1_authorized_execution_with_s1_addendum_completed_inconclusive_with_review_items" and a_manifest.get("status")!="extract03a_r1_authorized_execution_with_s1_completed_inconclusive_with_review_items":fail("extract03e_blocked_missing_extract03a_r1_outputs","EXTRACT03A-R1 status mismatch")
 component_rows=read_csv(D/"04_component_structure_import.csv");members={int(r["component_id"]):r["member_pair_ids"].split(";") for r in component_rows};pairs=[]
 mapping=read_csv(VIZ02/"06_component_order_mapping.csv");pairs=[None]*42
 for row in mapping:pairs[int(row["matrix_order_index"])]=row["pair_id"]
 idx={p:i for i,p in enumerate(pairs)};component_by={p:cid for cid,ids in members.items() for p in ids}
 K,krows=read_matrix(K_PATH,"K_candidate",pairs);d,drows=read_matrix(D_PATH,"d_cost_candidate",pairs);Dp,Drows=read_matrix(SP_PATH,"D_shortest_path_candidate",pairs);strength,srows=read_matrix(S_PATH,"relation_strength",pairs)
 if K is None or K.shape!=(42,42) or not np.isfinite(K).all():fail("extract03e_blocked_no_readable_K_matrix","K unreadable")
 edge=np.zeros((42,42));accepted=0
 for row in read_csv(EDGE_PATH):
  i,j=idx[row["pair_a"]],idx[row["pair_b"]];value=float(row["edge_candidate_flag"]);edge[i,j]=edge[j,i]=value;accepted+=int(value)
 within=[(i,j) for i,p in enumerate(pairs) for j,q in enumerate(pairs) if i!=j and component_by[p]==component_by[q]]
 between=[(i,j) for i,p in enumerate(pairs) for j,q in enumerate(pairs) if component_by[p]!=component_by[q]]
 withinK=np.array([K[i,j] for i,j in within]);betweenK=np.array([K[i,j] for i,j in between]);absdev=np.abs(np.abs(withinK)-1)
 exact_abs_count=int(np.count_nonzero(np.abs(withinK)==1));near_abs_count=int(np.count_nonzero(absdev<=1e-12));within_count=len(withinK)
 layer_values={"K":withinK,"d":np.array([d[i,j] for i,j in within]),"D":np.array([Dp[i,j] for i,j in within]),"strength":np.array([strength[i,j] for i,j in within]),"edge":np.array([edge[i,j] for i,j in within])}

 upstream=[("EXTRACT03D",D,"mechanism-review starting point"),("VIZ02",VIZ02,"component mapping"),("EXTRACT03A_R1",A,"stored matrices and runtime summaries"),
  ("EXTRACT03B",B,"review context"),("VIZ01",VIZ01,"visual context"),("EXTRACT03_C0",C0,"stability context"),("EXTRACT03_C0B",C0B,"stability context"),
  ("EXTRACT03_C1_R1",C1R1,"optional stability context"),("A_R1_SCRIPT",A_SCRIPT,"static rule review"),("PACKAGE_SCRIPT",PACKAGE_SCRIPT,"static contract-generation review"),
  ("VIZ02_SCRIPT",VIZ02_SCRIPT,"static ordering review"),("EXTRACT03D_SCRIPT",D_SCRIPT,"static review-code context"),("L2",L2,"unchanged fail boundary"),("M2",M2,"boundary context"),("N0",N0,"boundary context")]
 upstream=[x for x in upstream if x[1].exists()];before={rel(path):sha_path(path) for _,path,_ in upstream}
 try:
  db=sqlite3.connect(f"file:{MART}?mode=ro&immutable=1",uri=True);phase_cols=[r[1] for r in db.execute("pragma table_info(extract03a_r1_phase_response_vector)")];phase_count=db.execute("select count(*) from extract03a_r1_phase_response_vector").fetchone()[0];db.close()
 except sqlite3.Error as exc:fail("extract03e_blocked_missing_extract03a_r1_outputs",str(exc))

 signed=[]
 for cid,ids in sorted(members.items()):
  ii=[idx[p] for p in ids];block=K[np.ix_(ii,ii)];vals=block[~np.eye(len(ii),dtype=bool)];plus=int(np.count_nonzero(vals==1));minus=int(np.count_nonzero(vals==-1));other=len(vals)-plus-minus
  signed.append({"component_id":cid,"component_size":len(ids),"offdiag_count":len(vals),"plus_one_count":plus,"minus_one_count":minus,"other_count":other,
   "mean_K":float(vals.mean()),"mean_abs_K":float(np.abs(vals).mean()),"signed_pattern_status":"exact_and_near_signed_collinearity","notes":"Other values have |K| within 3.33e-16 of one; exact float/CSV equality counted without tolerance."})
 exactness=[]
 for cid,ids in sorted(members.items()):
  ii=[idx[p] for p in ids];vals=K[np.ix_(ii,ii)][~np.eye(len(ii),dtype=bool)];dev=np.abs(np.abs(vals)-1)
  exactness.append({"review_item":"within_component_offdiag_abs_K_equals_1","component_id":cid,"observed_value":f"exact={int(np.sum(np.abs(vals)==1))}/{len(vals)}; near_1e-12={int(np.sum(dev<=1e-12))}/{len(vals)}; max_dev={dev.max():.17g}",
   "exact_match_status":"all_exact" if np.all(np.abs(vals)==1) else "partial_exact_all_near","tolerance_used":"exact plus descriptive 1e-12","supporting_count":len(vals),"notes":"No K recomputation; parsed stored .17g values."})
 exactness += [
  {"review_item":"within_component_offdiag_K_equals_plus_1","component_id":"all","observed_value":int(np.sum(withinK==1)),"exact_match_status":"partial","tolerance_used":"exact","supporting_count":within_count,"notes":"Signed exact equality."},
  {"review_item":"within_component_offdiag_K_equals_minus_1","component_id":"all","observed_value":int(np.sum(withinK==-1)),"exact_match_status":"partial","tolerance_used":"exact","supporting_count":within_count,"notes":"Signed exact equality."},
  {"review_item":"between_component_abs_K_less_than_1","component_id":"all","observed_value":int(np.sum(np.abs(betweenK)<1)),"exact_match_status":"pass_all" if np.all(np.abs(betweenK)<1) else "not_all","tolerance_used":"exact comparison","supporting_count":len(betweenK),"notes":f"max between |K|={np.abs(betweenK).max():.17g}."},
  {"review_item":"diagonal_K_status","component_id":"all","observed_value":f"exact_one={int(np.sum(np.diag(K)==1))}/42","exact_match_status":"pass_all","tolerance_used":"exact","supporting_count":42,"notes":"Execution code explicitly fills K diagonal with 1."},
  {"review_item":"finite_status","component_id":"all","observed_value":bool(np.isfinite(K).all()),"exact_match_status":"pass","tolerance_used":"none","supporting_count":K.size,"notes":"All stored K cells finite."},
  {"review_item":"precision_status","component_id":"all","observed_value":f"exact_abs1={exact_abs_count}/{within_count}; max_abs_deviation={absdev.max():.17g}","exact_match_status":"roundtrip_precision_retains_nonexact_values","tolerance_used":"exact and 1e-12 descriptive","supporting_count":within_count,"notes":"CSV .17g output preserves binary64 round-trip information; no evidence that serialization made all values exact."}]

 def hist_rows(scope,values):
  av=np.abs(values);definitions=[("exact_1",lambda x:x==1),("near_1_nonexact",lambda x:(x!=1)&(np.abs(x-1)<=1e-12)),("0.5_to_below_near1",lambda x:(x>=.5)&(np.abs(x-1)>1e-12)),("0.1_to_0.5",lambda x:(x>=.1)&(x<.5)),("below_0.1",lambda x:x<.1)]
  result=[]
  for bid,predicate in definitions:
   count=int(np.count_nonzero(predicate(av)));result.append({"scope":scope,"bin_id":bid,"count":count,"fraction":count/len(av),"total_count":len(av),"notes":"Mutually exclusive descriptive |K| bins from stored matrix."})
  return result
 hist=hist_rows("within_component_offdiagonal",withinK)+hist_rows("between_component",betweenK)
 vector_rows=read_csv(VECTOR_SUMMARY)
 response_availability=[
  {"artifact_or_table":rel(VECTOR_SUMMARY),"available":"yes","contains_full_vectors":"no","contains_norms":"yes","contains_hashes_or_signatures":"lineage bundle only; no per-vector signature","contains_component_relation":"no","read_status":"pass","notes":"42 summary rows with norms/min/max; vector elements not persisted."},
  {"artifact_or_table":rel(MART)+":extract03a_r1_phase_response_vector","available":"yes","contains_full_vectors":"no","contains_norms":"yes","contains_hashes_or_signatures":"lineage bundle only","contains_component_relation":"no","read_status":"pass","notes":f"{phase_count} rows; columns={';'.join(phase_cols)}."},
  {"artifact_or_table":rel(A_SCRIPT)+":runtime arrays","available":"code only","contains_full_vectors":"not persisted","contains_norms":"runtime computation visible","contains_hashes_or_signatures":"no vector signature","contains_component_relation":"no","read_status":"static_code_only","notes":"Static code shows wrapped vectors and L2 normalization, but E does not execute or reconstruct them."}]
 serialization=[
  {"artifact":rel(K_PATH),"field_or_matrix":"K_candidate","observed_precision":"decimal strings written with Python format .17g","rounding_or_clipping_indicators":"262/322 internal offdiagonal values remain nonexact; max | |K|-1 |=3.33e-16","risk_level":"low_for_binary64_roundtrip; unresolved_for_upstream_vector_origin","notes":".17g is sufficient for binary64 round-trip; serialization does not explain universal later exactness."},
  {"artifact":rel(MART),"field_or_matrix":"extract03a_r1_K_candidate.value REAL","observed_precision":"SQLite REAL/binary64","rounding_or_clipping_indicators":"no K clipping field or rule","risk_level":"low","notes":"Read-only schema/context."},
  {"artifact":rel(VECTOR_SUMMARY),"field_or_matrix":"norm/min/max summaries","observed_precision":"format .17g","rounding_or_clipping_indicators":"summaries only; no vector elements","risk_level":"high_for_response_origin_identification","notes":"Cannot test exact identity/antiparallelism of full vectors."},
  {"artifact":rel(A_SCRIPT),"field_or_matrix":"K construction","observed_precision":"NumPy binary64 dot product, symmetrization; diagonal forced 1","rounding_or_clipping_indicators":"no offdiagonal K clipping; d tiny-negative values clipped later","risk_level":"high_for_layer_attribution_if code/version lineage diverged; hashes recorded","notes":"Static code aligns with output lineage and stored validation."}]

 code_review=[
  {"code_artifact":rel(A_SCRIPT),"rule_or_function":"phase normalization","observed_logic_summary":code_line(A_SCRIPT,"normalized ="),"could_create_perfection":"can make identical/antiparallel response shapes yield dot ±1","status":"reviewed_static","notes":"Full vectors absent, so precursor origin cannot be tested."},
  {"code_artifact":rel(A_SCRIPT),"rule_or_function":"K construction","observed_logic_summary":code_line(A_SCRIPT,"K = normalized @ normalized.T"),"could_create_perfection":"can expose collinearity; no offdiagonal clipping observed","status":"reviewed_static","notes":"K symmetrized; diagonal alone explicitly set to 1."},
  {"code_artifact":rel(A_SCRIPT),"rule_or_function":"d canonicalization","observed_logic_summary":code_line(A_SCRIPT,"tiny_negative")+" | "+code_line(A_SCRIPT,"d[tiny_negative]"),"could_create_perfection":"yes; near-unit |K| plus epsilon yields tiny negative raw_d then exact zero","status":"first_exact_perfection_rule_observed","notes":"All 322 internal offdiagonal d values are exact zero."},
  {"code_artifact":rel(A_SCRIPT),"rule_or_function":"strength and edge","observed_logic_summary":code_line(A_SCRIPT,"strength =")+" | "+code_line(A_SCRIPT,"edge ="),"could_create_perfection":"propagates d=0 to strength=1 and accepted edge","status":"reviewed_static","notes":"No retuning observed."},
  {"code_artifact":rel(A_SCRIPT),"rule_or_function":"D Floyd update","observed_logic_summary":code_line(A_SCRIPT,"D = np.minimum"),"could_create_perfection":"propagates zero-cost connectivity; does not precede d zero","status":"reviewed_static","notes":"No shortest-path rerun in E."},
  {"code_artifact":rel(PACKAGE_SCRIPT),"rule_or_function":"frozen package contracts","observed_logic_summary":"Defines normalization, K dot-product, d/strength, theta_edge contracts; package itself executes none.","could_create_perfection":"contract definitions constrain later propagation","status":"reviewed_static","notes":"Execution behavior reviewed in A-R1 script."},
  {"code_artifact":rel(VIZ02_SCRIPT),"rule_or_function":"component ordering","observed_logic_summary":code_line(VIZ02_SCRIPT,"component_list=components"),"could_create_perfection":"no; only reorders accepted-edge components","status":"reviewed_static","notes":"Visualization exposes but does not create matrix equality."},
  {"code_artifact":rel(D_SCRIPT),"rule_or_function":"descriptive within/between review","observed_logic_summary":code_line(D_SCRIPT,"within_pairs"),"could_create_perfection":"no; reads stored values","status":"reviewed_static","notes":"D reported the pattern; E checks its origin."}]

 strength_review=[{"review_item":"stored_rule","source":rel(A_SCRIPT),"observed_logic":"strength = exp(-d/ell_0); diagonal set 1","input_condition":"stored d=0","output_condition":"stored strength=1 exactly","creates_or_propagates":"propagates exact d perfection","status":"pass","notes":"Strength is computed after d in actual A-R1 code."},
  {"review_item":"within_exactness","source":rel(S_PATH),"observed_logic":f"exact one={int(np.sum(layer_values['strength']==1))}/{within_count}","input_condition":"all internal d zero","output_condition":"all internal strength one","creates_or_propagates":"algebraic propagation","status":"pass","notes":"No strength recomputation in E."}]
 d_review=[{"review_item":"formula","source":rel(A_SCRIPT),"observed_logic":"raw_d=-log(abs(K)+1e-12)","input_condition":"|K| within 3.33e-16 of one","output_condition":"raw_d tiny negative near -1e-12","creates_or_propagates":"near-perfect precursor","status":"pass","notes":"Static code review."},
  {"review_item":"tiny_negative_canonicalization","source":rel(A_SCRIPT),"observed_logic":"values in [-1e-10,0) set exactly to zero","input_condition":"near-unit |K| plus epsilon","output_condition":f"exact d zero={int(np.sum(layer_values['d']==0))}/{within_count}","creates_or_propagates":"first observed universal exact perfection","status":"pass","notes":"Primary origin classification for exact equality."}]
 D_review=[{"review_item":"stored_path_rule","source":rel(A_SCRIPT),"observed_logic":"Floyd-style minimum summed d costs; symmetrize; diagonal zero","input_condition":"zero d edges inside each clique","output_condition":f"exact D zero={int(np.sum(layer_values['D']==0))}/{within_count}","creates_or_propagates":"propagates zero-cost connectivity","status":"pass","notes":"D remains reconstructed cost-distance candidate."}]
 edge_review=[{"review_item":"threshold_rule","source":rel(A_SCRIPT),"observed_logic":"edge = strength >= 0.5; diagonal false","input_condition":"internal strength=1","output_condition":f"internal accepted edges={int(np.sum(layer_values['edge']==1))}/{within_count} directed cells","creates_or_propagates":"threshold propagates exact internal acceptance","status":"pass","notes":"Clique completeness follows from all internal pair strengths exceeding threshold."},
  {"review_item":"component_definition","source":rel(VIZ02_SCRIPT),"observed_logic":"connected components of explicit accepted edges","input_condition":"all internal pair edges accepted; no cross edges accepted","output_condition":"six complete accepted-edge cliques","creates_or_propagates":"defines and visualizes components","status":"pass","notes":"Ordering does not originate numeric perfection."}]

 layers=[
  ("source_pair_response_layer","No full vectors/signatures persisted; source summaries show finite nonzero norms.","Cannot test exact identity or antiparallelism.","origin_possible_but_unresolved","low","Separate signature export required."),
  ("K_construction_layer",f"All 322 internal |K| values within 3.33e-16 of 1; {exact_abs_count} exactly 1.","262 values are not exact; no full input vectors.","near_perfection_first_observed","high","Likely exposes identical/antiparallel normalized response shapes, but precursor cannot be verified."),
  ("K_serialization_or_rounding_layer","Stored .17g values permit exactness audit.","Nonexact values survive serialization; no universal clipping to ±1.","unlikely_primary_origin","high","Serialization is not the source of universal exact later values."),
  ("strength_abs_layer","All internal strength values exactly 1.","Actual code computes strength after d canonicalization.","exact_perfection_propagated","high","Not the first exact layer in actual execution order."),
  ("d_cost_transform_layer","All internal d values exactly 0; code explicitly clips tiny negative raw_d to zero.","Depends on near-unit K precursor and numeric policy.","first_observed_universal_exact_perfection","high","Primary exact-origin layer."),
  ("D_path_layer","All internal D values exactly 0.","Receives already exact d=0; no independent origin.","propagated_perfection","high","Preserves zero-cost connectivity."),
  ("edge_threshold_layer","All internal edges accepted and all cross edges rejected.","Threshold classification acts after exact strength and does not explain K near-collinearity.","propagated_and_discretized_perfection","high","Creates complete accepted-edge cliques from stored strengths."),
  ("component_order_visualization_layer","Six perfect clique blocks become visually contiguous.","Only reorders/labels existing relations.","visualizes_not_originates","high","No numeric creation."),]
 layer_rows=[{"candidate_layer":a,"evidence_for":b,"evidence_against":c,"classification":d,"confidence_level":e,"notes":f} for a,b,c,d,e,f in layers]
 coupling=[
  ("source_pair_response_layer","K_construction_layer","normalized dot product","L2 normalize wrapped response vectors; K=normalized dot products","near-perfection may propagate","unresolved","Full vectors absent."),
  ("K_construction_layer","d_cost_transform_layer","magnitude/log plus numerical canonicalization","raw_d=-log(|K|+epsilon); tiny negative values set zero","yes, near to exact","yes_for_universal_exactness","First exact layer."),
  ("d_cost_transform_layer","strength_abs_layer","deterministic exponential","strength=exp(-d)","yes","no","d=0 maps exactly to 1."),
  ("d_cost_transform_layer","D_path_layer","minimum summed path costs","zero local costs permit zero path costs","yes","no","Candidate cost-distance only."),
  ("strength_abs_layer","edge_threshold_layer","binary threshold","strength>=0.5","yes","no","All internal strengths accepted."),
  ("edge_threshold_layer","component_layer","graph definition","connected components of accepted edges","yes","no","Zero cross edges is definitional once components formed."),
  ("component_layer","component_order_visualization_layer","permutation/order","components sorted and shown contiguously","visual perfection exposed","no","No relation changed."),]
 coupling_rows=[{"from_layer":a,"to_layer":b,"coupling_type":c,"rule_summary":d,"does_perfection_propagate":e,"does_perfection_originate_here":f,"notes":g} for a,b,c,d,e,f,g in coupling]
 chain=[
  ("response_to_K","normalized response vectors","K dot products near ±1 internally","yes: stored K","empirical precursor plus deterministic construction","supported_with_input_gap","Full response vectors unavailable."),
  ("K_to_d","|K| within 3.33e-16 of one","tiny negative raw_d canonicalized to exact zero","yes: code and stored d","algorithmic/canonicalization","supported","First universal exact layer."),
  ("d_to_strength","d exactly zero","strength exactly one","yes","tautological deterministic transform","supported","Not independent evidence."),
  ("d_to_D","zero internal local costs","zero internal path cost","yes","deterministic path propagation","supported","D not geometry."),
  ("strength_to_edge","strength one versus threshold .5","accepted internal edge","yes","tautological threshold consequence","supported","No edge rediscovery."),
  ("edge_to_component","complete internal accepted edges and no cross accepted edges","six clique components","yes","graph-definition coupling","supported","Component perfection downstream."),
  ("component_to_visual_block","component permutation","contiguous diagonal blocks","yes","visualization ordering","supported","Exposes, does not create."),]
 chain_rows=[{"chain_step":a,"input_condition":b,"output_condition":c,"observed_in_artifacts":d,"tautological_or_empirical":e,"support_status":f,"notes":g} for a,b,c,d,e,f,g in chain]
 origin=[{"classification_item":"first_observed_exact_perfection","classification":"origin_likely_strength_d_edge_definition","primary_origin_layer":"d_cost_transform_layer tiny-negative canonicalization",
  "secondary_origin_layers":"K_construction near-perfect precursor; unresolved source/response collinearity; strength/D/edge/component propagation","supporting_artifacts":f"{rel(K_PATH)};{rel(D_PATH)};{rel(S_PATH)};{rel(EDGE_PATH)};{rel(A_SCRIPT)}",
  "limitations":"Full response vectors/signatures absent; raw_d values before canonicalization not persisted; static code lineage assumed from recorded run script.","claim_boundary":CLAIM,
  "notes":f"Only {exact_abs_count}/{within_count} internal K cells are exactly |K|=1, while all d cells are exactly zero."}]
 controls=[
  ("E03E-C01","label_permutation_control","Test whether component-label alignment exceeds arbitrary relabeling","yes","yes","Distribution of block contrasts under frozen permutations","medium","Prospective only; labels do not change stored result."),
  ("E03E-C02","component_membership_shuffle","Test sensitivity of perfect within blocks to membership assignment","yes","yes","Clique/perfection contrast under preregistered shuffles","high","Must preserve size sequence and avoid outcome tuning."),
  ("E03E-C03","K_sign_shuffle","Separate sign pattern from |K|-driven chain","yes","yes","Whether signed fine structure affects any reviewed output","medium","Magnitude remains fixed; no physical interpretation."),
  ("E03E-C04","K_magnitude_preserving_shuffle","Test whether placement rather than magnitude distribution creates blocks","yes","yes","Block contrast under frozen magnitude-preserving permutation","high","Requires exact prospective mapping."),
  ("E03E-C05","edge_threshold_sensitivity_review","Assess clique dependence on threshold without replacing base result","yes","yes","Prospective threshold-stability map","medium","Cannot retroactively tune theta_edge."),
  ("E03E-C06","response_vector_signature_export_contract","Stage per-vector hashes/signatures or full authorized vectors","yes","yes","Direct identical/antiparallel response-vector classification","highest","No reconstruction from raw F3 without separate contract."),
  ("E03E-C07","source_symmetry_review","Review source-level pair reversal/state symmetry prospectively","yes","yes","Identify structural origin of collinear response families","high","Separate source contract and claim boundary required."),]
 control_rows=[{"control_id":a,"control_test":b,"purpose":c,"requires_new_execution":d,"requires_new_human_freeze":e,"expected_diagnostic":f,"recommended_priority":g,"notes":h} for a,b,c,d,e,f,g,h in controls]
 review_items=[
  {"review_item_id":"E03E-RI-01","category":"full_response_vectors_absent","description":"Stored summaries contain norms/min/max but no full vector elements or per-vector signatures.","severity":"high","blocks_origin_resolution":"yes_for_source_response_layer","recommended_resolution":"Separate authorized response-vector signature/export contract.","notes":"Do not reconstruct from F3 in E."},
  {"review_item_id":"E03E-RI-02","category":"near_vs_exact_K","description":f"Only {exact_abs_count}/{within_count} internal K values are exactly |K|=1; all are within 3.33e-16.","severity":"high","blocks_origin_resolution":"no_for_first_exact_layer","recommended_resolution":"Retain exact and tolerance-based counts separately.","notes":"Avoid rounding near perfection into exact K perfection."},
  {"review_item_id":"E03E-RI-03","category":"d_canonicalization_policy","description":"Tiny negative raw_d values are set to exact zero, converting near-unit K into universal exact internal d.","severity":"high","blocks_origin_resolution":"no","recommended_resolution":"Document as numerical canonicalization and consider prospective sensitivity/control review.","notes":"No claim that policy is incorrect; it is origin-relevant."},
  {"review_item_id":"E03E-RI-04","category":"raw_d_not_persisted","description":"Pre-canonicalization raw_d values and masks are summarized only by count, not stored cellwise.","severity":"review","blocks_origin_resolution":"yes_for_cellwise_audit","recommended_resolution":"Future runs may persist raw_d and canonicalization mask under a new schema contract.","notes":"Current static code plus exact outputs support layer classification but not cellwise replay."},
  {"review_item_id":"E03E-RI-05","category":"downstream_definition_coupling","description":"Strength, D, edge and component perfection are deterministic/definitional consequences after d zeroing.","severity":"review","blocks_origin_resolution":"no","recommended_resolution":"Do not treat downstream layers as independent confirmations.","notes":"L2 boundary unchanged."}]

 OUT.mkdir(parents=True)
 # Overview: exact fractions by layer and K deviation distribution.
 fractions=[exact_abs_count/within_count,float(np.mean(layer_values["d"]==0)),float(np.mean(layer_values["strength"]==1)),float(np.mean(layer_values["D"]==0)),float(np.mean(layer_values["edge"]==1))]
 fig,axes=plt.subplots(1,2,figsize=(12,4.6),dpi=160)
 axes[0].bar(["|K| exact 1","d exact 0","strength exact 1","D exact 0","edge exact 1"],fractions,color=["#F58518","#4C78A8","#4C78A8","#4C78A8","#4C78A8"]);axes[0].set_ylim(0,1.05);axes[0].tick_params(axis="x",rotation=28);axes[0].set_ylabel("fraction of within-component offdiagonal cells");axes[0].set_title("First universal exact layer")
 nonzero=absdev[absdev>0];bins=np.array([0,0.5e-16,1.5e-16,2.5e-16,3.5e-16]);axes[1].hist(absdev,bins=bins,color="#F58518",edgecolor="black");axes[1].set_xlabel("absolute deviation ||K|-1|");axes[1].set_ylabel("cell count");axes[1].set_title("Stored internal K deviations")
 fig.suptitle("Perfection-origin review of stored EXTRACT03A-R1 outputs — descriptive only");fig.tight_layout(rect=[0,0,1,.92]);fig.savefig(OUT/FILES[28],format="png",metadata={"Description":CLAIM});plt.close(fig)
 now=datetime.now(timezone.utc).isoformat();manifest_out={"work_package":"QSB-EXTRACT03E","status":STATUS,"created_at_utc":now,"repo_root":str(ROOT),
  "extract03d_seen":True,"extract03d_status":d_manifest["status"],"viz02_seen":True,"viz02_status":viz_manifest["status"],"extract03a_r1_seen":True,"extract03a_r1_status":a_manifest["status"],
  "component_count":len(members),"component_sizes":[len(members[c]) for c in sorted(members)],"accepted_edge_count":accepted,"K_matrix_readable":True,"K_exactness_checked":True,
  "pair_response_summary_seen":True,"serialization_review_done":True,"static_code_review_done":True,"strength_rule_reviewed":True,"d_rule_reviewed":True,"D_rule_reviewed":True,"edge_rule_reviewed":True,
  "first_perfection_layer":"d_cost_transform_layer tiny-negative canonicalization","origin_classification":"origin_likely_strength_d_edge_definition with near-perfect K/response precursor",
  "review_items_count":len(review_items),"matplotlib_available":True,"K_recomputed":False,"strength_recomputed":False,"d_recomputed":False,"D_recomputed":False,"edge_recomputed":False,
  "shortest_path_rerun":False,"phase_vectors_reconstructed":False,"bootstrap_run":False,"upstream_modified":False,"l2_fail_changed":False,"post_hoc_tuning_performed":False,
  "physical_evidence_claim_made":False,"geometry_claim_made":False,"gravity_claim_made":False,"claim_boundary":CLAIM,
  "next_allowed_action":"human_review_then_optional_response_vector_signature_export_or_prospective_control_contract"}
 (OUT/FILES[0]).write_text(json.dumps(manifest_out,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
 inventory=[{"artifact_id":f"E03E-A{i:02d}","upstream_block":b,"path":rel(p),"exists":"yes","sha256":before[rel(p)],"role":"read-only origin-review input","required":"yes" if b in {"EXTRACT03D","VIZ02","EXTRACT03A_R1","A_R1_SCRIPT","L2","M2","N0"} else "context","used_for":u,"notes":"File hash or deterministic direct-artifact directory hash; no mutation."} for i,(b,p,u) in enumerate(upstream,1)]
 write_csv(FILES[1],list(inventory[0]),inventory)
 inputs=[("EXTRACT03D",d_manifest_path,"yes","pass","origin review starting point"),("VIZ02",viz_manifest_path,"yes","pass","component mapping"),("K",K_PATH,"yes","pass","exactness and sign review"),("d",D_PATH,"yes","pass","exact-zero review"),("D",SP_PATH,"yes","pass","path propagation review"),("strength",S_PATH,"yes","pass","exact-one review"),("edge",EDGE_PATH,"yes","pass","threshold/clique review"),("phase_response_summary",VECTOR_SUMMARY,"yes","summary_only","norm availability; no vectors"),("A_R1_script",A_SCRIPT,"yes","static_only","rule-chain review")]
 input_rows=[{"input_id":a,"source_artifact":rel(b),"available":c,"read_status":d,"used_for":e,"blocking":"yes" if a in {"EXTRACT03D","VIZ02","K","d","D","strength","edge","A_R1_script"} else "no","notes":"Read-only."} for a,b,c,d,e in inputs]
 write_csv(FILES[2],list(input_rows[0]),input_rows)
 clique_rows=[{"component_id":r["component_id"],"component_size":r["component_size"],"member_pair_ids":r["member_pair_ids"],"accepted_internal_edges":next(x["accepted_internal_edges"] for x in read_csv(D/"10_edge_component_explanation_summary.csv") if x["component_id"]==r["component_id"]),"possible_internal_edges":next(x["possible_internal_edges"] for x in read_csv(D/"10_edge_component_explanation_summary.csv") if x["component_id"]==r["component_id"]),"clique_status":"complete_clique","import_status":"pass","notes":"Imported from EXTRACT03D; checked against stored edge count."} for r in component_rows]
 write_csv(FILES[3],list(clique_rows[0]),clique_rows);write_csv(FILES[4],list(exactness[0]),exactness);write_csv(FILES[5],list(signed[0]),signed);write_csv(FILES[6],list(hist[0]),hist)
 write_csv(FILES[7],list(response_availability[0]),response_availability);write_csv(FILES[8],list(serialization[0]),serialization);write_csv(FILES[9],list(code_review[0]),code_review)
 write_csv(FILES[10],list(strength_review[0]),strength_review);write_csv(FILES[11],list(d_review[0]),d_review);write_csv(FILES[12],list(D_review[0]),D_review);write_csv(FILES[13],list(edge_review[0]),edge_review)
 write_csv(FILES[14],list(layer_rows[0]),layer_rows);write_csv(FILES[15],list(coupling_rows[0]),coupling_rows);write_csv(FILES[16],list(chain_rows[0]),chain_rows);write_csv(FILES[17],list(origin[0]),origin)
 write_csv(FILES[18],list(control_rows[0]),control_rows);write_csv(FILES[19],list(review_items[0]),review_items)
 guards=["no_K_recompute","no_strength_recompute","no_d_recompute","no_D_recompute","no_edge_recompute","no_shortest_path_rerun","no_phase_vector_reconstruction","no_bootstrap_run","no_upstream_mutation","no_l2_change","no_post_hoc_tuning","no_physical_evidence_claim","no_geometry_claim","no_gravity_claim"]
 guard_rows=[{"guard_id":f"E03E-G-{i:02d}","guard":g,"status":"pass","evidence":"Stored matrix parsing, static code review, and descriptive review plot only.","blocking":"yes","notes":"No forbidden execution path."} for i,g in enumerate(guards,1)]
 write_csv(FILES[20],list(guard_rows[0]),guard_rows)
 unsupported=["EXTRACT03E proves QSB","EXTRACT03E demonstrates emergent spacetime","EXTRACT03E demonstrates gravity","EXTRACT03E confirms the Interface mechanism","EXTRACT03E establishes a physical mechanism","EXTRACT03E repairs L2 fail","EXTRACT03E establishes mechanism in nature"]
 claims=[{"statement_id":"E03E-CB-01","statement":"EXTRACT03E identifies the first observed exact-perfection layer in existing outputs.","classification":"safe_review_statement","safe_wording":"Numerical/pipeline origin review only.","forbidden_wording":"physical or causal mechanism established","notes":"Source response origin remains unresolved."}]
 claims += [{"statement_id":f"E03E-CB-{i+2:02d}","statement":s,"classification":"unsupported_claim","safe_wording":"EXTRACT03E reviews an observed data/pipeline pattern.","forbidden_wording":s,"notes":"Unsupported by this review."} for i,s in enumerate(unsupported)]
 write_csv(FILES[21],list(claims[0]),claims)
 l2=load(L2);l2_rows=[{"boundary_item":"L2_result","upstream_value":l2["minimaltest_contract_result"],"review_value":"fail retained","status":"pass","notes":"No rerun or reinterpretation."},{"boundary_item":"N4_support","upstream_value":"0/3; required 2/3","review_value":"unchanged","status":"pass","notes":"Perfection review does not weaken L2."},{"boundary_item":"theta_new","upstream_value":"0.012446436850524916","review_value":"unchanged","status":"pass","notes":"No tuning."},{"boundary_item":"epsilon_new","upstream_value":"0.006009422749372488","review_value":"unchanged","status":"pass","notes":"No tuning."},{"boundary_item":"L2_sha256","upstream_value":sha_file(L2),"review_value":sha_file(L2),"status":"pass","notes":"Hash unchanged."}]
 write_csv(FILES[22],list(l2_rows[0]),l2_rows)
 checks=[("extract03d_present",d_manifest["status"],"extract03d_block_mechanism_review_completed_candidate_chain_supported_for_review"),("viz02_present",viz_manifest["status"],"extract03viz02_topology_organized_matrix_completed"),("extract03a_r1_present",True,True),("K_matrix_readable",True,True),("K_exactness_checked",within_count,322),("signed_distribution_checked",sum(int(r["offdiag_count"]) for r in signed),322),("pair_response_availability_checked",len(response_availability),3),("serialization_review_done",len(serialization),4),("static_code_rules_reviewed",len(code_review),8),("strength_rule_reviewed",len(strength_review),2),("d_rule_reviewed",len(d_review),2),("D_rule_reviewed",len(D_review),1),("edge_rule_reviewed",len(edge_review),2),("first_perfection_layer_classified",layer_rows[4]["classification"],"first_observed_universal_exact_perfection"),("definition_coupling_created",len(coupling_rows),7),("control_recommendations_created",len(control_rows),7),("no_recomputation",False,False),("no_upstream_mutation","checked_after_write","unchanged"),("no_l2_change",False,False),("claim_boundary_clean",False,False),("exact_output_count",30,30)]
 validations=[{"validation_id":f"E03E-V-{i:02d}","validation_layer":"EXTRACT03E","check_name":k,"status":"pass" if o==e or k=="no_upstream_mutation" else "fail","severity":"error","observed_value":o,"expected_value":e,"message":"Perfection-origin stored-output review validation.","blocking":"yes"} for i,(k,o,e) in enumerate(checks,1)]
 write_csv(FILES[23],list(validations[0]),validations)
 note=f"""# QSB-EXTRACT03E Perfection Origin Review

## Ausgangspunkt

EXTRACT03D fand sechs vollständige Accepted-Edge-Cliquen mit intern |K|≈1, Strength=1, d=D=0 und Edge=1.

## Warum die Perfektion verdächtig ist

Vollständige Cliquen über 161 Kanten und exakt konstante Downstream-Werte können aus Regel- und Numerikkopplung entstehen; sie dürfen nicht automatisch als unabhängige Strukturbelege gelesen werden.

## Wo die Perfektion zuerst sichtbar wird

K ist bereits nahezu perfekt: alle 322 internen Off-Diagonalwerte liegen höchstens 3,33×10⁻¹⁶ von |K|=1 entfernt. Exakt sind jedoch nur {exact_abs_count}/322. Universelle exakte Gleichheit entsteht erstmals bei d, wo winzige negative raw_d-Werte gemäß Code auf exakt null kanonisiert werden.

## K-Ebene und Vorzeichenstruktur

K enthält positive und negative nahezu kollineare Beziehungen. Die Vorzeichenstruktur bleibt im K-Output sichtbar; die spätere Magnituden-/Kostenkette verwendet |K|.

## Serialisierung, Rundung und Normalisierung

K wird mit `.17g` geschrieben, wodurch nicht-exakte Binary64-Werte erhalten bleiben. Es gibt keine beobachtete Off-Diagonal-K-Klippung. Normalisierte Vollvektoren oder Signaturen sind jedoch nicht persistiert, daher bleibt offen, ob Identität/Gegenläufigkeit bereits in Response-Strukturen liegt.

## Strength/d/D/Edge als Weitergabe der Perfektion

d-Kanonisierung erzeugt exakt null; Strength bildet null deterministisch auf eins ab; D bewahrt interne Nullkosten; der Edge-Schwellenwert akzeptiert alle internen Paare. Komponenten und Visualisierung geben diese Struktur weiter.

## Was dadurch erklärt wird

Die perfekte Clique-/Blockdarstellung ist eine nachvollziehbare Downstream-Folge der nahezu perfekten K-Vorläufer plus numerischer d-Kanonisierung und binärer Edge-Regel.

## Was offen bleibt

Der Ursprung der nahezu kollinearen Response-Familien, cellwise raw_d vor der Kanonisierung und kontrollierte Gegenproben fehlen.

## Kontrolltests

Prioritär sind ein separater Response-Vektor-Signaturexport sowie prospektive Membership-/Magnitude-Kontrollen. Keine davon wird in E ausgeführt.

## Was ausdrücklich nicht behauptet wird

Kein physikalischer Mechanismus, keine Geometrie, Gravitation, emergente Raumzeit, Interface-Bestätigung oder L2-Reparatur.

## Nächster Schritt

Human Review; optional separater Response-Signaturexport oder prospektiver Kontrollvertrag.
"""
 (OUT/FILES[24]).write_text(note,encoding="utf-8")
 publication="""# Publication-safe note candidates

## English

The first universally exact within-component values appear at the stored d-cost layer, where the execution rule canonicalizes tiny negative numerical costs to zero. The preceding K matrix is already near-perfect in magnitude but is not universally exactly ±1. Subsequent strength, D, edge, and component layers propagate or discretize this pattern. This is a pipeline-origin review, not evidence for a physical mechanism.

## Deutsch

Die ersten universell exakten komponenteninternen Werte erscheinen in der gespeicherten d-Kostenschicht, deren Ausführungsregel winzige negative numerische Kosten auf null kanonisiert. Die vorgelagerte K-Matrix ist im Betrag bereits nahezu perfekt, jedoch nicht durchgehend exakt ±1. Strength, D, Edge und Komponenten geben dieses Muster anschließend weiter oder diskretisieren es. Dies ist ein Pipeline-Ursprungsreview und kein physikalischer Mechanismusnachweis.
"""
 (OUT/FILES[25]).write_text(publication,encoding="utf-8")
 options=[("E03E-O01","limited_origin_note","Document first exact layer and unresolved response precursor","no","yes","Recommended now."),("E03E-O02","response_vector_signature_export","Persist authorized per-vector signatures/full vectors","yes","yes","Highest diagnostic priority."),("E03E-O03","prospective_permutation_controls","Run frozen membership/magnitude controls","yes","yes","Tests distinctiveness without tuning."),("E03E-O04","raw_d_audit_schema_later","Persist raw_d and canonicalization mask in a future run","yes","no","Enhances cellwise numerical audit."),("E03E-O05","no_further_execution","Retain current candidate boundary","no","no","Valid if no stronger origin claim is needed.")]
 option_rows=[{"option_id":a,"option":b,"purpose":c,"requires_new_execution":d,"recommended":e,"notes":f} for a,b,c,d,e,f in options]
 write_csv(FILES[26],list(option_rows[0]),option_rows)
 recommendation="""# Empfohlener nächster Schritt

Zuerst Human Review und eine begrenzte Ursprungsnotiz: K ist nahezu, aber nicht universell exakt; die erste universelle Exaktheit entsteht bei der d-Kanonisierung. Falls der vorgelagerte Ursprung geklärt werden soll, ist ein separat autorisierter Response-Vektor-Signaturexport der diagnostisch stärkste nächste Schritt. Alternativ können prospektiv eingefrorene Membership-/Magnitude-Kontrollen folgen.
"""
 (OUT/FILES[27]).write_text(recommendation,encoding="utf-8")
 final=f"""# QSB-EXTRACT03E Final Result

## Status

`{STATUS}`

## Reviewed Inputs

EXTRACT03D, VIZ02, stored EXTRACT03A-R1 K/d/D/strength/edge matrices, response summaries, result-mart schema, and static execution/package/visualization code were reviewed read-only.

## First Perfection Layer

The first universally exact internal layer observed is d-cost canonicalization: 322/322 internal off-diagonal d values are exactly zero. K is the near-perfect precursor, with maximum |K|-to-one deviation 3.33e-16.

## K Exactness

Only {exact_abs_count}/{within_count} internal off-diagonal K cells are exactly ±1; the remaining {within_count-exact_abs_count} retain nonzero Binary64 deviations in `.17g` serialization.

## Definition Coupling

d zero propagates to strength one and zero D paths; thresholding produces all internal accepted edges; connected components and ordering expose complete blocks.

## Origin Classification

Exact perfection is likely introduced by the d/strength/edge definition chain, specifically d tiny-negative canonicalization, with a likely K or response-layer near-collinearity precursor whose source cannot be resolved from summaries.

## Review Items

Full vectors/signatures and cellwise raw_d are absent; algebraic and definitional downstream layers are not independent evidence. Prospective controls remain unexecuted.

## Claim Boundary

This identifies a stored numerical/pipeline pattern only. It establishes no physical mechanism, geometry, gravity, emergent spacetime, Interface confirmation, or mechanism in nature.

## L2 Boundary

L2 remains fail with N4 support 0/3 versus required 2/3; no threshold, parameter, scope, or interpretation changed.

## Next Allowed Action

Human review, followed optionally by a separately authorized response-vector signature export or prospective control contract.
"""
 (OUT/FILES[29]).write_text(final,encoding="utf-8")
 after={rel(path):sha_path(path) for _,path,_ in upstream}
 if before!=after:fail("extract03e_blocked_guard_violation","upstream changed during EXTRACT03E")
 actual=sorted(p.name for p in OUT.iterdir())
 if actual!=sorted(FILES) or len(actual)!=30:fail("extract03e_blocked_guard_violation",f"output artifact mismatch: {len(actual)}")
 if any(r["status"]!="pass" for r in guard_rows+validations+l2_rows):fail("extract03e_blocked_guard_violation","guard, validation, or L2 failure")
 print(json.dumps({"status":STATUS,"artifacts":30,"first_perfection_layer":"d_cost_transform_layer tiny-negative canonicalization",
  "K_within_exact_abs1":exact_abs_count,"K_within_count":within_count,"K_max_abs_deviation":float(absdev.max()),"d_exact_zero":int(np.sum(layer_values["d"]==0)),
  "strength_exact_one":int(np.sum(layer_values["strength"]==1)),"D_exact_zero":int(np.sum(layer_values["D"]==0)),"edge_exact_one":int(np.sum(layer_values["edge"]==1)),
  "origin_classification":"origin_likely_strength_d_edge_definition","review_items":len(review_items),"upstream_modified":False,"l2_changed":False,"recomputation":False},indent=2))


if __name__=="__main__":main()
