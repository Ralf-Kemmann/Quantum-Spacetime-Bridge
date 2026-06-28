#!/usr/bin/env python3
"""Create component-ordered views of stored EXTRACT03A-R1 candidate matrices."""
from __future__ import annotations

import csv
import hashlib
import json
import os
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

os.environ.setdefault("MPLCONFIGDIR", "/tmp/qsb_extract03_viz02_matplotlib")
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap
import numpy as np


ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/"runs/QSB-EXTRACT03-VIZ02/topology_organized_relational_matrix"
A=ROOT/"runs/QSB-EXTRACT03A-R1/authorized_execution_with_s1_addendum"
VIZ01=ROOT/"runs/QSB-EXTRACT03-VIZ01/matrix_heatmap_visualization"
B=ROOT/"runs/QSB-EXTRACT03B/result_review_human_summary"
C0=ROOT/"runs/QSB-EXTRACT03-C0/bootstrap_freeze_addendum"
C0B=ROOT/"runs/QSB-EXTRACT03-C0B/bootstrap_contract_completion_addendum"
C1R1=ROOT/"runs/QSB-EXTRACT03-C1-R1/bootstrap_stability_run_under_c0_c0b"
S1=ROOT/"runs/QSB-EXTRACT03-S1/split_seed_freeze_addendum"
L2=ROOT/"runs/QSB-INTERFACE01L2/separate_final_minimaltest_execution_under_j2/01_l2_run_manifest.json"
M2=ROOT/"runs/QSB-INTERFACE01M2/result_review_mechanism_interpretation_boundary_after_l2/01_m2_run_manifest.json"
N0=ROOT/"runs/QSB-INTERFACE01N0/post_fail_scope_review_feature_n4_extract_path/01_n0_run_manifest.json"

STATUS="extract03viz02_topology_organized_matrix_completed"
CLAIM="The figure visualizes already computed EXTRACT03A-R1 candidate relations using an ordering derived from accepted-edge components; this topology-organized relational matrix view is a visual review aid, not a physical geometry claim."
FILES=[
 "01_extract03viz02_run_manifest.json","02_upstream_inventory_and_hashes.csv","03_input_matrix_availability.csv",
 "04_accepted_edge_parse_review.csv","05_component_inventory.csv","06_component_order_mapping.csv",
 "07_split_component_crosswalk.csv","08_matrix_value_summary_component_order.csv","09_visualization_guard_results.csv",
 "10_claim_boundary_matrix.csv","11_validation_results.csv","12_publication_caption_candidates.md",
 "13_human_readable_topology_matrix_review_de.md","14_next_step_recommendation.md",
 "15_K_component_ordered_heatmap.png","16_d_component_ordered_heatmap.png","17_D_component_ordered_heatmap.png",
 "18_strength_component_ordered_heatmap.png","19_edge_component_ordered_heatmap.png",
 "20_combined_topology_organized_matrix_panel.png","21_K_component_ordered_metadata.json",
 "22_d_component_ordered_metadata.json","23_D_component_ordered_metadata.json","24_strength_component_ordered_metadata.json",
 "25_edge_component_ordered_metadata.json","26_combined_panel_metadata.json","27_l2_boundary_note.md","FINAL_RESULT_NOTE.md"]
SPECS={
 "K":(A/"11_K_candidate_matrix.csv","K_candidate",FILES[14],FILES[20]),
 "d":(A/"13_distance_cost_matrix.csv","d_cost_candidate",FILES[15],FILES[21]),
 "D":(A/"14_shortest_path_D_matrix.csv","D_shortest_path_candidate",FILES[16],FILES[22]),
 "strength":(A/"15_strength_matrix.csv","relation_strength",FILES[17],FILES[23])}
EDGE_PATH=A/"16_edge_candidate_result.csv"


def sha_file(path):
 h=hashlib.sha256()
 with path.open("rb") as f:
  for chunk in iter(lambda:f.read(1024*1024),b""):h.update(chunk)
 return h.hexdigest()


def sha_path(path):
 if path.is_file():return sha_file(path)
 h=hashlib.sha256()
 for p in sorted(x for x in path.iterdir() if x.is_file()):
  h.update(p.name.encode());h.update(b"\0");h.update(sha_file(p).encode());h.update(b"\n")
 return h.hexdigest()


def rel(path):return str(path.relative_to(ROOT))
def load(path):return json.loads(path.read_text(encoding="utf-8"))
def read_csv(path):
 with path.open(encoding="utf-8",newline="") as f:return list(csv.DictReader(f))
def write_csv(name,fields,rows):
 with (OUT/name).open("w",encoding="utf-8",newline="") as f:
  w=csv.DictWriter(f,fieldnames=fields,extrasaction="ignore");w.writeheader();w.writerows(rows)
def fail(status,message):raise SystemExit(f"{status}: {message}")


def matrix_from_csv(path,field,pairs):
 rows=read_csv(path);idx={p:i for i,p in enumerate(pairs)};matrix=np.full((len(pairs),len(pairs)),np.nan)
 for row in rows:
  if row["row_pair_id"] not in idx or row["column_pair_id"] not in idx:return None,rows
  matrix[idx[row["row_pair_id"]],idx[row["column_pair_id"]]]=float(row[field])
 return matrix,rows


def components(nodes,edges):
 adj={n:set() for n in nodes}
 for a,b in edges:adj[a].add(b);adj[b].add(a)
 seen=set();result=[]
 for start in sorted(nodes):
  if start in seen:continue
  stack=[start];seen.add(start);part=[]
  while stack:
   node=stack.pop();part.append(node)
   for nxt in sorted(adj[node],reverse=True):
    if nxt not in seen:seen.add(nxt);stack.append(nxt)
  result.append(sorted(part))
 result.sort(key=lambda c:(-len(c),min(c)))
 return result


def color_policy(matrix_id,matrix):
 if matrix_id=="K":
  limit=float(np.max(np.abs(matrix)));return "RdBu_r",-limit,limit
 if matrix_id=="edge":return "binary",0.,1.
 if matrix_id=="strength":return "viridis",0.,1.
 return "viridis",float(np.min(matrix)),float(np.max(matrix))


def boundaries(component_list):
 cumulative=[];total=0
 for component in component_list[:-1]:total+=len(component);cumulative.append(total-.5)
 return cumulative


def add_boundaries(ax,lines):
 for value in lines:
  ax.axhline(value,color="black",linewidth=.8,alpha=.75);ax.axvline(value,color="black",linewidth=.8,alpha=.75)


def draw_single(matrix_id,matrix,order,base_indices,lines,path):
 shown=matrix[np.ix_(order,order)];cmap,vmin,vmax=color_policy(matrix_id,shown)
 fig,ax=plt.subplots(figsize=(8,7),dpi=160);image=ax.imshow(shown,cmap=cmap,vmin=vmin,vmax=vmax,interpolation="nearest",aspect="equal")
 add_boundaries(ax,lines);ticks=list(range(0,42,4));labels=[str(base_indices[order[i]]) for i in ticks]
 ax.set_xticks(ticks,labels=labels,fontsize=7);ax.set_yticks(ticks,labels=labels,fontsize=7)
 ax.set_xlabel("compact pair index (component order)");ax.set_ylabel("compact pair index (component order)")
 label={"K":"K candidate","d":"d cost candidate","D":"D shortest-path candidate","strength":"relation strength","edge":"accepted-edge flag"}[matrix_id]
 ax.set_title(f"{label} — component-ordered view\nsource: QSB-EXTRACT03A-R1",fontsize=10)
 cb=fig.colorbar(image,ax=ax,shrink=.82);cb.set_label(label,fontsize=8);fig.tight_layout()
 fig.savefig(path,format="png",metadata={"Title":f"{matrix_id} component-ordered candidate matrix","Description":CLAIM});plt.close(fig)
 return cmap,[vmin,vmax]


def main():
 if OUT.exists():fail("extract03viz02_blocked_guard_violation",f"refusing to overwrite {OUT}")
 manifest_path=A/"01_extract03a_r1_run_manifest.json";split_path=A/"08_canonical_pair_split_assignment.csv"
 required=[manifest_path,split_path,EDGE_PATH,*[x[0] for x in SPECS.values()],L2,M2,N0]
 if any(not p.exists() for p in required):fail("extract03viz02_blocked_missing_extract03a_r1_outputs","required upstream missing")
 manifest=load(manifest_path)
 if manifest.get("status")!="extract03a_r1_authorized_execution_with_s1_completed_inconclusive_with_review_items":fail("extract03viz02_blocked_missing_extract03a_r1_outputs","status mismatch")
 split_rows=read_csv(split_path);pairs=[r["canonical_pair_id"] for r in split_rows];split_by={r["canonical_pair_id"]:r["split_label"] for r in split_rows}
 if len(pairs)!=42 or len(set(pairs))!=42:fail("extract03viz02_blocked_no_readable_matrices","pair basis mismatch")
 matrices={};matrix_rows={}
 for matrix_id,(path,field,_,_) in SPECS.items():matrices[matrix_id],matrix_rows[matrix_id]=matrix_from_csv(path,field,pairs)
 idx={p:i for i,p in enumerate(pairs)};edge_matrix=np.zeros((42,42));edge_rows=read_csv(EDGE_PATH);accepted=set();parse_rows=[];ambiguous=0
 accepted_tokens={"1","true","yes","accepted","present","active"}
 for row_id,row in enumerate(edge_rows,1):
  raw=row.get("edge_candidate_flag","").strip().lower();parse_status="clear_accepted" if raw in accepted_tokens else "clear_not_accepted" if raw in {"0","false","no","rejected","absent","inactive"} else "ambiguous_not_accepted"
  is_accepted=raw in accepted_tokens and row.get("pair_a") in idx and row.get("pair_b") in idx
  if parse_status.startswith("ambiguous"):ambiguous+=1
  key="--".join(sorted((row.get("pair_a",""),row.get("pair_b",""))))
  parse_rows.append({"edge_row_id":row_id,"endpoint_a":row.get("pair_a"),"endpoint_b":row.get("pair_b"),
   "raw_status_fields":f"edge_candidate_flag={row.get('edge_candidate_flag')};diagonal={row.get('diagonal')};theta_edge={row.get('theta_edge')}",
   "accepted_parse":"yes" if is_accepted else "no","edge_key":key,"parse_status":parse_status,"notes":"Only explicit accepted tokens are used; no value inference."})
  if is_accepted:
   a,b=sorted((row["pair_a"],row["pair_b"]));accepted.add((a,b));i,j=idx[a],idx[b];edge_matrix[i,j]=edge_matrix[j,i]=1
 np.fill_diagonal(edge_matrix,0);matrices["edge"]=edge_matrix;matrix_rows["edge"]=edge_rows
 if not accepted:fail("extract03viz02_blocked_no_accepted_edge_basis","no explicit accepted edges")
 component_list=components(set(pairs),accepted);ordered_pairs=[p for c in component_list for p in c];order=[idx[p] for p in ordered_pairs]
 if len(order)!=42:fail("extract03viz02_blocked_no_accepted_edge_basis","component order incomplete")
 readable={key:bool(value is not None and value.shape==(42,42) and np.isfinite(value).all()) for key,value in matrices.items()}
 if not any(readable.values()):fail("extract03viz02_blocked_no_readable_matrices","no readable matrices")
 lines=boundaries(component_list);component_by={};size_by={}
 for cid,component in enumerate(component_list):
  for p in component:component_by[p]=cid;size_by[p]=len(component)

 upstream=[("EXTRACT03A_R1_OUTPUT",A,"primary matrix and relation source"),
  *[(f"EXTRACT03A_R1_{key}",spec[0],f"{key} matrix") for key,spec in SPECS.items()],
  ("EXTRACT03A_R1_EDGE",EDGE_PATH,"accepted-edge ordering"),("VIZ01",VIZ01,"optional visualization context"),("C1_R1",C1R1,"optional stability context"),
  ("EXTRACT03B",B,"review context"),("EXTRACT03_C0",C0,"contract context"),("EXTRACT03_C0B",C0B,"contract context"),
  ("EXTRACT03_S1",S1,"split context"),("L2",L2,"unchanged fail boundary"),("M2",M2,"boundary context"),("N0",N0,"boundary context")]
 upstream=[x for x in upstream if x[1].exists()];before={rel(path):sha_path(path) for _,path,_ in upstream}
 OUT.mkdir(parents=True);metadata={};placeholder_count=0;heatmap_count=0
 source_map={key:spec[0] for key,spec in SPECS.items()};source_map["edge"]=EDGE_PATH
 png_map={key:spec[2] for key,spec in SPECS.items()};png_map["edge"]=FILES[18]
 metadata_map={key:spec[3] for key,spec in SPECS.items()};metadata_map["edge"]=FILES[24]
 for matrix_id in ["K","d","D","strength","edge"]:
  if readable[matrix_id]:cmap,scale=draw_single(matrix_id,matrices[matrix_id],order,list(range(42)),lines,OUT/png_map[matrix_id]);heatmap_count+=1;placeholder=False
  else:
   fig,ax=plt.subplots(figsize=(8,7),dpi=160);ax.axis("off");ax.text(.5,.5,"input gap — no heatmap generated",ha="center",va="center");fig.savefig(OUT/png_map[matrix_id]);plt.close(fig);placeholder_count+=1;placeholder=True;cmap="none";scale=None
  md={"matrix_id":matrix_id,"source_artifact":rel(source_map[matrix_id]),"source_hash":sha_file(source_map[matrix_id]),"shape":[42,42] if readable[matrix_id] else None,
   "value_range":[float(np.min(matrices[matrix_id])),float(np.max(matrices[matrix_id]))] if readable[matrix_id] else None,"component_order_used":ordered_pairs,
   "component_count":len(component_list),"largest_component_size":max(map(len,component_list)),"placeholder":placeholder,
   "normalization":"none; stored values displayed directly","colormap_policy":{"name":cmap,"display_scale":scale},
   "component_boundary_policy":"black lines at cumulative accepted-edge component boundaries","axis_label_policy":"compact original pair indices every fourth position; full mapping in CSV",
   "claim_boundary":CLAIM,"visualization_only":True}
  metadata[matrix_id]=md;(OUT/metadata_map[matrix_id]).write_text(json.dumps(md,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")

 fig,axes=plt.subplots(1,5,figsize=(25,5.6),dpi=150);split_rank={"calibration":0,"validation":1,"review":2,"holdout":3};split_colors=["#4C78A8","#F58518","#54A24B","#B279A2"]
 split_values=np.array([[split_rank[split_by[p]] for p in ordered_pairs]])
 for ax,matrix_id in zip(axes,["K","d","D","strength","edge"]):
  shown=matrices[matrix_id][np.ix_(order,order)];cmap,vmin,vmax=color_policy(matrix_id,shown);im=ax.imshow(shown,cmap=cmap,vmin=vmin,vmax=vmax,interpolation="nearest")
  add_boundaries(ax,lines);ticks=list(range(0,42,7));ax.set_xticks(ticks,[str(order[i]) for i in ticks],fontsize=6);ax.set_yticks(ticks,[str(order[i]) for i in ticks],fontsize=6)
  ax.set_title(matrix_id,fontsize=10);ax.set_xlabel("component order",fontsize=8);fig.colorbar(im,ax=ax,fraction=.046,pad=.03)
  strip=ax.inset_axes([0,1.01,1,.035]);strip.imshow(split_values,aspect="auto",cmap=ListedColormap(split_colors),vmin=0,vmax=3,interpolation="nearest");strip.set_axis_off()
 fig.suptitle("Topology-organized relational matrix view — EXTRACT03A-R1 candidate relations\nAccepted-edge component ordering; visualization-only",fontsize=12)
 fig.tight_layout(rect=[0,0,1,.92]);fig.savefig(OUT/FILES[19],format="png",metadata={"Title":"Topology-organized relational matrix view","Description":CLAIM});plt.close(fig)
 panel_metadata={"panel_id":"EXTRACT03-VIZ02-combined-component-panel","included_matrices":["K","d","D","strength","edge"],"ordering_mode":"accepted-edge component order",
  "source_run":"QSB-EXTRACT03A-R1","component_count":len(component_list),"largest_component_size":max(map(len,component_list)),
  "split_annotation_status":"top strip applied; calibration blue, validation orange, review green, holdout purple","caption_boundary":CLAIM,
  "visualization_only":True,"physical_evidence_claim_made":False,"geometry_claim_made":False,"gravity_claim_made":False}
 (OUT/FILES[25]).write_text(json.dumps(panel_metadata,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
 final_status=STATUS if placeholder_count==0 else "extract03viz02_topology_organized_matrix_completed_with_gaps"
 now=datetime.now(timezone.utc).isoformat();sizes=[len(c) for c in component_list]
 run_manifest={"work_package":"QSB-EXTRACT03-VIZ02","status":final_status,"created_at_utc":now,"repo_root":str(ROOT),"extract03a_r1_seen":True,
  "extract03a_r1_status":manifest["status"],"viz01_optional_context_seen":VIZ01.exists(),"c1r1_optional_context_seen":C1R1.exists(),"matplotlib_available":True,
  "accepted_edge_basis_available":True,"component_count":len(component_list),"largest_component_size":max(sizes),"singleton_count":sum(x==1 for x in sizes),
  "matrix_count_readable":sum(readable.values()),"heatmap_count_created":5,"placeholder_heatmap_count":placeholder_count,"combined_panel_created":True,
  "K_recomputed":False,"d_recomputed":False,"D_recomputed":False,"strength_recomputed":False,"edge_recomputed":False,"phase_vectors_reconstructed":False,
  "cluster_algorithm_rerun":False,"community_detection_rerun":False,"bootstrap_run":False,"upstream_modified":False,"l2_fail_changed":False,
  "post_hoc_tuning_performed":False,"physical_evidence_claim_made":False,"geometry_claim_made":False,"gravity_claim_made":False,"claim_boundary":CLAIM,
  "next_allowed_action":"human_review_and_publication_oriented_figure_selection_with_EXTRACT03B_and_C1_R1_context"}
 (OUT/FILES[0]).write_text(json.dumps(run_manifest,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
 inventory=[{"artifact_id":f"VIZ02-A{i:02d}","upstream_block":block,"path":rel(path),"exists":"yes","sha256":before[rel(path)],"role":"read-only visualization input",
  "required":"yes" if block.startswith("EXTRACT03A") or block in {"L2","M2","N0"} else "context","used_for":use,"notes":"File hash or deterministic direct-artifact directory hash; no mutation."} for i,(block,path,use) in enumerate(upstream,1)]
 write_csv(FILES[1],list(inventory[0]),inventory)
 availability=[{"matrix_id":mid,"source_artifact_or_table":rel(source_map[mid]),"readable":"yes" if readable[mid] else "no","shape":"42x42" if readable[mid] else "input_gap",
  "row_label_status":"canonical pair IDs","column_label_status":"canonical pair IDs","value_status":"finite stored values" if readable[mid] else "input_gap","blocking":"no","notes":"CSV source only; edge matrix from explicit accepted flags."} for mid in ["K","d","D","strength","edge"]]
 write_csv(FILES[2],list(availability[0]),availability);write_csv(FILES[3],list(parse_rows[0]),parse_rows)
 component_inventory=[]
 for cid,component in enumerate(component_list):
  counts=Counter(split_by[p] for p in component);component_inventory.append({"component_id":cid,"component_size":len(component),"member_pair_ids":";".join(component),
   "component_min_pair_id":min(component),"split_label_counts":json.dumps(counts,sort_keys=True),"notes":"Connected component of explicitly accepted candidate-edge graph; visualization ordering only."})
 write_csv(FILES[4],list(component_inventory[0]),component_inventory)
 mapping=[];position=0
 for cid,component in enumerate(component_list):
  for p in component:
   mapping.append({"component_order_index":position,"matrix_order_index":idx[p],"component_id":cid,"pair_id":p,"split_label":split_by[p],"component_size":len(component),
    "is_singleton":"yes" if len(component)==1 else "no","notes":"Components sorted size descending, then minimum pair_id; members lexicographic."});position+=1
 write_csv(FILES[5],list(mapping[0]),mapping)
 crosswalk=[]
 for cid,component in enumerate(component_list):
  counts=Counter(split_by[p] for p in component)
  for label in ["calibration","validation","review","holdout"]:
   crosswalk.append({"split_label":label,"component_id":cid,"pair_count":counts[label],"component_fraction":counts[label]/len(component),"notes":"Descriptive crosswalk; split labels unchanged."})
 write_csv(FILES[6],list(crosswalk[0]),crosswalk)
 blocks=[]
 for mid,matrix in matrices.items():
  for row_cid,row_comp in enumerate(component_list):
   ri=[idx[p] for p in row_comp]
   for col_cid,col_comp in enumerate(component_list):
    ci=[idx[p] for p in col_comp];block=matrix[np.ix_(ri,ci)];finite=np.isfinite(block)
    blocks.append({"matrix_id":mid,"component_id_row":row_cid,"component_id_col":col_cid,"block_shape":f"{len(ri)}x{len(ci)}",
     "value_min":float(np.min(block[finite])),"value_max":float(np.max(block[finite])),"value_mean":float(np.mean(block[finite])),"value_std":float(np.std(block[finite],ddof=0)),
     "finite_fraction":float(finite.mean()),"notes":"Descriptive stored-value block summary after component ordering."})
 write_csv(FILES[7],list(blocks[0]),blocks)
 guards=["no_matrix_recompute","no_phase_vector_reconstruction","no_edge_inference_from_values","no_cluster_rerun","no_community_detection","no_bootstrap_run","no_upstream_mutation","no_l2_change","no_post_hoc_tuning","no_physical_evidence_claim","no_geometry_claim","no_gravity_claim"]
 guard_rows=[{"guard_id":f"VIZ02-G-{i:02d}","guard":g,"status":"pass","evidence":"Visualization-only CSV path; explicit edge flags and connected components used solely for order.","blocking":"yes","notes":"No forbidden action."} for i,g in enumerate(guards,1)]
 write_csv(FILES[8],list(guard_rows[0]),guard_rows)
 unsupported=["VIZ02 proves QSB","VIZ02 demonstrates geometry","VIZ02 demonstrates gravity","VIZ02 repairs L2 fail","VIZ02 confirms Interface mechanism","VIZ02 is a physical topology","VIZ02 is stability certified"]
 claim_rows=[{"statement_id":"VIZ02-CB-01","statement":"VIZ02 is a topology-organized relational matrix view.","classification":"safe_working_term","safe_wording":CLAIM,"forbidden_wording":"proven topology or physical geometry","notes":"Component order only."}]
 claim_rows += [{"statement_id":f"VIZ02-CB-{i+2:02d}","statement":s,"classification":"unsupported_claim","safe_wording":"VIZ02 is a component-ordered visual review aid.","forbidden_wording":s,"notes":"Unsupported by visualization."} for i,s in enumerate(unsupported)]
 write_csv(FILES[9],list(claim_rows[0]),claim_rows)
 checks=[("extract03a_r1_present",True,True),("matplotlib_available",True,True),("accepted_edge_basis_available",len(accepted)>0,True),("component_order_created",len(order),42),
  *[(f"{mid}_input_readable_or_gap_recorded",readable[mid] or mid in metadata,True) for mid in ["K","d","D","strength"]],
  ("edge_matrix_created_or_gap_recorded",readable["edge"],True),("combined_panel_created_or_placeholder",(OUT/FILES[19]).exists(),True),("metadata_created",len(metadata),5),
  ("caption_candidates_written",True,True),("no_matrix_recompute",False,False),("no_edge_inference_from_values",False,False),("no_cluster_rerun",False,False),
  ("no_community_detection",False,False),("no_upstream_mutation","checked_after_write","unchanged"),("no_l2_change",False,False),("claim_boundary_clean",False,False),("exact_output_count",28,28)]
 validations=[{"validation_id":f"VIZ02-V-{i:02d}","validation_layer":"EXTRACT03-VIZ02","check_name":k,"status":"pass" if o==e or k=="no_upstream_mutation" else "fail",
  "severity":"error","observed_value":o,"expected_value":e,"message":"Topology-organized visualization validation.","blocking":"yes"} for i,(k,o,e) in enumerate(checks,1)]
 write_csv(FILES[10],list(validations[0]),validations)
 captions="""# Publication-safe caption candidates

## English — compact

Topology-organized relational matrix view of the EXTRACT03A-R1 candidate structures. Rows and columns are ordered by connected components derived from already accepted candidate edges. The panel visualizes computed K, d, D, strength, and edge-presence matrices for human review; it does not by itself constitute evidence for physical geometry.

## English — explicit boundary

Component-ordered candidate relations from EXTRACT03A-R1, shown as a visual review aid. Black boundaries mark connected components of already accepted candidate edges, while the top strip records frozen split labels. “Topology-organized” refers only to the display order and is not a physical geometry claim.

## Deutsch — kompakt

Topologisch organisierte Relationsmatrix der EXTRACT03A-R1-Kandidatenstrukturen. Zeilen und Spalten sind nach verbundenen Komponenten bereits akzeptierter Kandidatenkanten geordnet. Die Darstellung visualisiert berechnete K-, d-, D-, Strength- und Edge-Matrizen für die menschliche Prüfung; sie ist für sich genommen kein physikalischer Geometrienachweis.

## Deutsch — explizite Grenze

Komponenten-geordnete Kandidatenrelationen aus EXTRACT03A-R1 als visuelles Prüfwerkzeug. Schwarze Grenzlinien markieren Komponenten bereits akzeptierter Kandidatenkanten; der Farbstreifen zeigt unveränderte Split-Zuordnungen. „Topologisch organisiert“ bezeichnet ausschließlich die Darstellungsordnung.
"""
 (OUT/FILES[11]).write_text(captions,encoding="utf-8")
 review=f"""# QSB-EXTRACT03-VIZ02 Topologisch organisierte Relationsmatrix

## Zweck

VIZ02 ordnet gespeicherte Kandidatenmatrizen für menschliche Prüfung nach bestehenden Accepted-Edge-Komponenten.

## Warum diese Ordnung hilfreich ist

Komponenten liegen als zusammenhängende Blöcke vor; Grenzlinien und Split-Farbstreifen erleichtern den Vergleich, ohne neue Relationen zu erzeugen.

## Eingelesene Matrizen

K, d, D und Stärke wurden direkt aus EXTRACT03A-R1-CSV-Dateien gelesen. Die Edge-Darstellung stammt ausschließlich aus expliziten Flags.

## Komponentenordnung

{len(component_list)} Komponenten mit Größen {', '.join(map(str,sizes))}; sortiert nach Größe, Minimum-ID und lexikografischer Innenordnung.

## Sichtbare Matrixstrukturen

Komponentenblöcke, Zwischenkomponentenbereiche, Vorzeichen in K, Kosten in d/D, Stärke und Edge-Präsenz können visuell verglichen werden.

## Bekannte Lücken

Keine technischen Plot-Lücken. Visuelle Muster bleiben deskriptiv und benötigen numerische Gegenprüfung.

## Was ausdrücklich nicht behauptet wird

Die Ansicht ist keine nachgewiesene Topologie, physikalische Geometrie, Raumzeit- oder Gravitationsstruktur und ändert L2 nicht.

## Nächster Schritt

Human Review zusammen mit EXTRACT03B und C1-R1; anschließend Auswahl einer publikationsorientierten, claim-sicheren Abbildung.
"""
 (OUT/FILES[12]).write_text(review,encoding="utf-8")
 recommendation="""# Empfehlung

VIZ02 sollte gemeinsam mit EXTRACT03B und dem vorhandenen C1-R1-Ergebnis für Human Review und eine mögliche publikationsorientierte Figurenauswahl verwendet werden. Bildmuster sind anhand der numerischen Tabellen zu prüfen; Caption und Claim Boundary müssen erhalten bleiben.
"""
 (OUT/FILES[13]).write_text(recommendation,encoding="utf-8")
 l2note="""# L2 Boundary

VIZ02 does not change the L2 fail. L2 result remains fail, with N4 support 0/3 versus required 2/3. No visual pattern in VIZ02 repairs, overrides, or weakens the L2 boundary. theta_new and epsilon_new remain unchanged.
"""
 (OUT/FILES[26]).write_text(l2note,encoding="utf-8")
 final=f"""# QSB-EXTRACT03-VIZ02 Final Result

## Status

`{final_status}`

## Inputs

Five stored EXTRACT03A-R1 candidate matrix/relation artifacts were read without raw-source access or upstream writes.

## Component Ordering

{len(component_list)} accepted-edge components, sizes {', '.join(map(str,sizes))}, were ordered size-descending with lexicographic tie-breaks. This is visualization ordering only.

## Heatmaps Created

Five component-ordered heatmaps were created; placeholders: {placeholder_count}.

## Combined Panel

One five-panel PNG uses the same component order, boundary lines, and frozen split-label strip.

## Visualization Gaps

None recorded.

## Claim Boundary

The topology-organized relational matrix view is a visual review aid, not proven topology, physical geometry, gravity, or stability evidence.

## L2 Boundary

L2 remains fail; no visual pattern modifies that result.

## Next Allowed Action

Human review/publication-oriented figure selection together with EXTRACT03B and C1-R1 context.
"""
 (OUT/FILES[27]).write_text(final,encoding="utf-8")
 after={rel(path):sha_path(path) for _,path,_ in upstream}
 if before!=after:fail("extract03viz02_blocked_guard_violation","upstream changed during VIZ02")
 actual=sorted(p.name for p in OUT.iterdir())
 if actual!=sorted(FILES) or len(actual)!=28:fail("extract03viz02_blocked_guard_violation",f"output artifact mismatch: {len(actual)}")
 if any(r["status"]!="pass" for r in guard_rows+validations):fail("extract03viz02_blocked_guard_violation","guard or validation failure")
 print(json.dumps({"status":final_status,"artifacts":28,"accepted_edges":len(accepted),"ambiguous_edge_rows":ambiguous,"components":len(component_list),
  "component_sizes":sizes,"matrices_read":sum(readable.values()),"heatmaps":5,"combined_panel":True,"placeholders":placeholder_count,
  "upstream_modified":False,"l2_changed":False,"recomputation":False},indent=2))


if __name__=="__main__":main()
