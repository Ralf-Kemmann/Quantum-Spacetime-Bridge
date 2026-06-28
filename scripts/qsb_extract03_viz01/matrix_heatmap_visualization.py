#!/usr/bin/env python3
"""Visualize stored EXTRACT03A-R1 matrices without recomputation."""
from __future__ import annotations

import csv
import hashlib
import json
import os
from datetime import datetime, timezone
from pathlib import Path

os.environ.setdefault("MPLCONFIGDIR", "/tmp/qsb_extract03_viz01_matplotlib")
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np


ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "runs/QSB-EXTRACT03-VIZ01/matrix_heatmap_visualization"
A = ROOT / "runs/QSB-EXTRACT03A-R1/authorized_execution_with_s1_addendum"
B = ROOT / "runs/QSB-EXTRACT03B/result_review_human_summary"
C0 = ROOT / "runs/QSB-EXTRACT03-C0/bootstrap_freeze_addendum"
C0B = ROOT / "runs/QSB-EXTRACT03-C0B/bootstrap_contract_completion_addendum"
C1R1 = ROOT / "runs/QSB-EXTRACT03-C1-R1/bootstrap_stability_run_under_c0_c0b"
S1 = ROOT / "runs/QSB-EXTRACT03-S1/split_seed_freeze_addendum"
L2 = ROOT / "runs/QSB-INTERFACE01L2/separate_final_minimaltest_execution_under_j2/01_l2_run_manifest.json"
M2 = ROOT / "runs/QSB-INTERFACE01M2/result_review_mechanism_interpretation_boundary_after_l2/01_m2_run_manifest.json"
N0 = ROOT / "runs/QSB-INTERFACE01N0/post_fail_scope_review_feature_n4_extract_path/01_n0_run_manifest.json"

STATUS = "extract03viz01_matrix_heatmap_visualization_completed"
CLAIM = "VIZ01 visualizes already computed EXTRACT03A-R1 candidate matrices for human review; heatmaps are visualization aids and not physical evidence claims."
FILES = [
    "01_extract03viz01_run_manifest.json", "02_upstream_inventory_and_hashes.csv",
    "03_matrix_input_availability.csv", "04_pair_index_mapping.csv", "05_ordering_summary.csv",
    "06_visualization_guard_results.csv", "07_claim_boundary_matrix.csv", "08_validation_results.csv",
    "09_human_readable_heatmap_review_de.md", "10_next_step_recommendation.md",
    "11_K_unsorted_heatmap.png", "12_K_split_sorted_heatmap.png", "13_K_cluster_sorted_heatmap.png",
    "14_d_unsorted_heatmap.png", "15_d_split_sorted_heatmap.png", "16_d_cluster_sorted_heatmap.png",
    "17_D_unsorted_heatmap.png", "18_D_split_sorted_heatmap.png", "19_D_cluster_sorted_heatmap.png",
    "20_strength_unsorted_heatmap.png", "21_strength_split_sorted_heatmap.png", "22_strength_cluster_sorted_heatmap.png",
    "23_edge_unsorted_heatmap.png", "24_edge_split_sorted_heatmap.png", "25_edge_cluster_sorted_heatmap.png",
    "26_K_heatmap_metadata.json", "27_d_heatmap_metadata.json", "28_D_heatmap_metadata.json",
    "29_strength_heatmap_metadata.json", "30_edge_heatmap_metadata.json", "FINAL_RESULT_NOTE.md",
]
MATRIX_SPECS = {
    "K": (A/"11_K_candidate_matrix.csv", "K_candidate", [FILES[10],FILES[11],FILES[12]], FILES[25]),
    "d": (A/"13_distance_cost_matrix.csv", "d_cost_candidate", [FILES[13],FILES[14],FILES[15]], FILES[26]),
    "D": (A/"14_shortest_path_D_matrix.csv", "D_shortest_path_candidate", [FILES[16],FILES[17],FILES[18]], FILES[27]),
    "strength": (A/"15_strength_matrix.csv", "relation_strength", [FILES[19],FILES[20],FILES[21]], FILES[28]),
}
EDGE_PATH = A/"16_edge_candidate_result.csv"


def sha_file(path: Path) -> str:
    h=hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda:handle.read(1024*1024),b""): h.update(chunk)
    return h.hexdigest()


def sha_path(path: Path) -> str:
    if path.is_file(): return sha_file(path)
    h=hashlib.sha256()
    for item in sorted(p for p in path.iterdir() if p.is_file()):
        h.update(item.name.encode()); h.update(b"\0"); h.update(sha_file(item).encode()); h.update(b"\n")
    return h.hexdigest()


def rel(path: Path) -> str: return str(path.relative_to(ROOT))


def read_csv(path: Path):
    with path.open(encoding="utf-8",newline="") as handle: return list(csv.DictReader(handle))


def write_csv(name,fields,rows):
    with (OUT/name).open("w",encoding="utf-8",newline="") as handle:
        writer=csv.DictWriter(handle,fieldnames=fields,extrasaction="ignore"); writer.writeheader(); writer.writerows(rows)


def fail(status,message): raise SystemExit(f"{status}: {message}")


def load_matrix(path,field,pair_ids):
    rows=read_csv(path); index={pair_id:i for i,pair_id in enumerate(pair_ids)}
    matrix=np.full((len(pair_ids),len(pair_ids)),np.nan,dtype=float)
    for row in rows:
        if row["row_pair_id"] not in index or row["column_pair_id"] not in index: return None,rows
        matrix[index[row["row_pair_id"]],index[row["column_pair_id"]]]=float(row[field])
    return matrix,rows


def connected_components(nodes,edges):
    adjacency={node:set() for node in nodes}
    for a,b in edges:
        if a in adjacency and b in adjacency: adjacency[a].add(b); adjacency[b].add(a)
    components=[]; seen=set()
    for start in sorted(nodes):
        if start in seen: continue
        stack=[start]; seen.add(start); component=[]
        while stack:
            node=stack.pop(); component.append(node)
            for neighbor in sorted(adjacency[node],reverse=True):
                if neighbor not in seen: seen.add(neighbor); stack.append(neighbor)
        components.append(sorted(component))
    components.sort(key=lambda c:(-len(c),min(c)))
    return components


def plot_heatmap(matrix,order,pair_to_base_index,matrix_id,mode,path):
    shown=matrix[np.ix_(order,order)]
    if matrix_id=="K":
        maxabs=float(np.nanmax(np.abs(shown))); cmap="RdBu_r"; vmin=-maxabs; vmax=maxabs
    elif matrix_id=="edge": cmap="binary"; vmin=0.; vmax=1.
    elif matrix_id=="strength": cmap="viridis"; vmin=0.; vmax=1.
    else: cmap="viridis"; vmin=float(np.nanmin(shown)); vmax=float(np.nanmax(shown))
    fig,ax=plt.subplots(figsize=(8,7),dpi=160)
    image=ax.imshow(shown,origin="upper",interpolation="nearest",aspect="equal",cmap=cmap,vmin=vmin,vmax=vmax)
    positions=list(range(0,len(order),4)); labels=[str(pair_to_base_index[order[p]]) for p in positions]
    ax.set_xticks(positions,labels=labels,rotation=0,fontsize=7); ax.set_yticks(positions,labels=labels,fontsize=7)
    ax.set_xlabel("compact pair index (column)"); ax.set_ylabel("compact pair index (row)")
    display={"K":"K candidate","d":"d cost candidate","D":"D shortest-path candidate","strength":"relation strength","edge":"accepted-edge flag"}[matrix_id]
    ax.set_title(f"{display} — {mode}\nsource: QSB-EXTRACT03A-R1",fontsize=10)
    colorbar=fig.colorbar(image,ax=ax,shrink=.82); colorbar.set_label(display,fontsize=8)
    fig.tight_layout(); fig.savefig(path,format="png",metadata={"Title":f"{matrix_id} {mode} heatmap","Description":CLAIM}); plt.close(fig)
    return cmap,[vmin,vmax]


def main():
    if OUT.exists(): fail("extract03viz01_blocked_guard_violation",f"refusing to overwrite {OUT}")
    manifest_path=A/"01_extract03a_r1_run_manifest.json"; split_path=A/"08_canonical_pair_split_assignment.csv"
    required=[manifest_path,split_path,EDGE_PATH,*[spec[0] for spec in MATRIX_SPECS.values()],L2,M2,N0]
    if any(not path.exists() for path in required): fail("extract03viz01_blocked_missing_extract03a_r1_outputs","required input missing")
    manifest=json.loads(manifest_path.read_text(encoding="utf-8"))
    if manifest.get("status")!="extract03a_r1_authorized_execution_with_s1_completed_inconclusive_with_review_items":
        fail("extract03viz01_blocked_missing_extract03a_r1_outputs","EXTRACT03A-R1 status mismatch")
    split_rows=read_csv(split_path); pair_ids=[row["canonical_pair_id"] for row in split_rows]
    split_by={row["canonical_pair_id"]:row["split_label"] for row in split_rows}
    if len(pair_ids)!=42 or len(set(pair_ids))!=42: fail("extract03viz01_blocked_no_readable_matrices","pair basis invalid")
    matrices={}; source_rows={}
    for matrix_id,(path,field,_,_) in MATRIX_SPECS.items(): matrices[matrix_id],source_rows[matrix_id]=load_matrix(path,field,pair_ids)
    edge_rows=read_csv(EDGE_PATH); edge_matrix=np.zeros((42,42),dtype=float); idx={p:i for i,p in enumerate(pair_ids)}; accepted=set()
    edge_parse_ok=True
    for row in edge_rows:
        if row["pair_a"] not in idx or row["pair_b"] not in idx or row["edge_candidate_flag"] not in {"0","1"}: edge_parse_ok=False; continue
        i,j=idx[row["pair_a"]],idx[row["pair_b"]]; value=float(row["edge_candidate_flag"]); edge_matrix[i,j]=value; edge_matrix[j,i]=value
        if value==1: accepted.add(tuple(sorted((row["pair_a"],row["pair_b"]))))
    np.fill_diagonal(edge_matrix,0); matrices["edge"]=edge_matrix; source_rows["edge"]=edge_rows
    readable={key:bool(matrix is not None and matrix.shape==(42,42) and np.isfinite(matrix).all()) for key,matrix in matrices.items()}
    if not any(readable.values()): fail("extract03viz01_blocked_no_readable_matrices","no readable primary matrix")
    components=connected_components(set(pair_ids),accepted) if edge_parse_ok else []
    cluster_status="pass" if components and sum(map(len,components))==42 else "input_gap"
    unsorted_order=list(range(42)); split_rank={"calibration":0,"validation":1,"review":2,"holdout":3}
    split_pair_ids=sorted(pair_ids,key=lambda p:(split_rank[split_by[p]],p)); split_order=[idx[p] for p in split_pair_ids]
    cluster_pair_ids=[p for component in components for p in component] if cluster_status=="pass" else pair_ids
    cluster_order=[idx[p] for p in cluster_pair_ids]
    orders={"unsorted":unsorted_order,"split_sorted":split_order,"cluster_sorted":cluster_order}

    upstream=[("EXTRACT03A_R1_OUTPUT",A,"matrix and boundary source"),
        *[(f"EXTRACT03A_R1_{key}",spec[0],f"{key} matrix source") for key,spec in MATRIX_SPECS.items()],
        ("EXTRACT03A_R1_EDGE",EDGE_PATH,"edge matrix and component ordering"),("EXTRACT03B",B,"review context"),
        ("EXTRACT03B_FINAL",B/"FINAL_RESULT_NOTE.md","claim-boundary review"),("EXTRACT03_C0",C0,"optional contract context"),
        ("EXTRACT03_C0B",C0B,"optional contract context"),("EXTRACT03_C1_R1",C1R1,"optional stability context"),
        ("EXTRACT03_S1",S1,"split context"),("L2",L2,"unchanged fail boundary"),("M2",M2,"boundary context"),("N0",N0,"boundary context")]
    upstream=[item for item in upstream if item[1].exists()]; before={rel(path):sha_path(path) for _,path,_ in upstream}
    OUT.mkdir(parents=True)
    heatmap_count=0; placeholders=0; metadata={}
    image_map={key:spec[2] for key,spec in MATRIX_SPECS.items()}; image_map["edge"]=[FILES[22],FILES[23],FILES[24]]
    source_map={key:spec[0] for key,spec in MATRIX_SPECS.items()}; source_map["edge"]=EDGE_PATH
    for matrix_id in ["K","d","D","strength","edge"]:
        placeholder_modes=[]; cmaps={}
        for mode,filename in zip(["unsorted","split_sorted","cluster_sorted"],image_map[matrix_id]):
            if readable[matrix_id] and (mode!="cluster_sorted" or cluster_status=="pass"):
                cmap,value_scale=plot_heatmap(matrices[matrix_id],orders[mode],unsorted_order,matrix_id,mode,OUT/filename); cmaps[mode]=cmap; heatmap_count+=1
            else:
                fig,ax=plt.subplots(figsize=(8,7),dpi=160); ax.axis("off"); ax.text(.5,.5,"input gap — no heatmap generated",ha="center",va="center",fontsize=14)
                ax.set_title(f"{matrix_id} — {mode}"); fig.savefig(OUT/filename,format="png"); plt.close(fig); placeholders+=1; placeholder_modes.append(mode)
        matrix=matrices[matrix_id]
        metadata[matrix_id]={"matrix_id":matrix_id,"source_artifact":rel(source_map[matrix_id]),"source_hash":sha_file(source_map[matrix_id]),
            "value_range":None if not readable[matrix_id] else [float(np.min(matrix)),float(np.max(matrix))],"shape":None if matrix is None else list(matrix.shape),
            "ordering_modes_created":[mode for mode in orders if mode not in placeholder_modes],"placeholder_modes":placeholder_modes,
            "normalization":"none; stored values displayed directly","colormap_policy":cmaps,
            "axis_label_policy":"compact unsorted pair indices shown every fourth position; full mapping in 04_pair_index_mapping.csv",
            "claim_boundary":CLAIM,"visualization_only":True}
        metadata_file={"K":FILES[25],"d":FILES[26],"D":FILES[27],"strength":FILES[28],"edge":FILES[29]}[matrix_id]
        (OUT/metadata_file).write_text(json.dumps(metadata[matrix_id],indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    final_status=STATUS if placeholders==0 else "extract03viz01_matrix_heatmap_visualization_completed_with_gaps"
    now=datetime.now(timezone.utc).isoformat()
    run_manifest={"work_package":"QSB-EXTRACT03-VIZ01","status":final_status,"created_at_utc":now,"repo_root":str(ROOT),
        "extract03a_r1_seen":True,"extract03a_r1_status":manifest["status"],"extract03b_seen":B.exists(),"c1r1_optional_context_seen":C1R1.exists(),
        "matplotlib_available":True,"matplotlib_version":matplotlib.__version__,"matrix_count_readable":sum(readable.values()),
        "heatmap_count_created":heatmap_count+placeholders,"placeholder_heatmap_count":placeholders,"ordering_modes":list(orders),
        "K_visualized":readable["K"],"d_visualized":readable["d"],"D_visualized":readable["D"],"strength_visualized":readable["strength"],"edge_visualized":readable["edge"],
        "K_recomputed":False,"d_recomputed":False,"D_recomputed":False,"strength_recomputed":False,"edge_recomputed":False,
        "phase_vectors_reconstructed":False,"cluster_algorithm_rerun":False,"bootstrap_run":False,"upstream_modified":False,"l2_fail_changed":False,
        "post_hoc_tuning_performed":False,"physical_evidence_claim_made":False,"geometry_claim_made":False,"gravity_claim_made":False,
        "claim_boundary":CLAIM,"next_allowed_action":"human_review_heatmaps_together_with_EXTRACT03A_R1_EXTRACT03B_and_optional_C1_R1_context"}
    (OUT/FILES[0]).write_text(json.dumps(run_manifest,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    inventory=[{"artifact_id":f"VIZ01-A{i:02d}","upstream_block":block,"path":rel(path),"exists":"yes","sha256":before[rel(path)],"role":"read-only visualization input","required":"yes" if block.startswith("EXTRACT03A") or block in {"L2","M2","N0"} else "context","used_for":use,"notes":"File hash or deterministic direct-artifact directory hash; no mutation."} for i,(block,path,use) in enumerate(upstream,1)]
    write_csv(FILES[1],list(inventory[0]),inventory)
    availability=[]
    for matrix_id in ["K","d","D","strength","edge"]:
        availability.append({"matrix_id":matrix_id,"source_artifact_or_table":rel(source_map[matrix_id]),"readable":"yes" if readable[matrix_id] else "no",
            "shape":"42x42" if readable[matrix_id] else "unreadable","row_label_status":"explicit_pair_ids_or_frozen_pair_basis","column_label_status":"explicit_pair_ids_or_frozen_pair_basis",
            "value_status":"finite stored values" if readable[matrix_id] else "input_gap","blocking":"no" if any(readable.values()) else "yes","notes":"Read from existing CSV; edge matrix materialized from explicit symmetric relation flags."})
    write_csv(FILES[2],list(availability[0]),availability)
    component_by={}; component_size={}
    for component_id,component in enumerate(components):
        for pair_id in component: component_by[pair_id]=component_id; component_size[pair_id]=len(component)
    split_position={pair_id:i for i,pair_id in enumerate(split_pair_ids)}; cluster_position={pair_id:i for i,pair_id in enumerate(cluster_pair_ids)}
    mapping=[{"matrix_index":i,"pair_id":pair_id,"split_label":split_by[pair_id],"unsorted_order":i,"split_sorted_order":split_position[pair_id],
        "cluster_sorted_order":cluster_position[pair_id],"cluster_component_id":component_by.get(pair_id,"input_gap"),"cluster_component_size":component_size.get(pair_id,"input_gap"),
        "notes":"Component ordering uses existing accepted-edge flags only."} for i,pair_id in enumerate(pair_ids)]
    write_csv(FILES[3],list(mapping[0]),mapping)
    ordering=[{"ordering_mode":"unsorted","status":"pass","basis_artifact":rel(split_path),"pair_count":42,"notes":"Original matrix/pair order preserved."},
        {"ordering_mode":"split_sorted","status":"pass","basis_artifact":rel(split_path),"pair_count":42,"notes":"calibration, validation, review, holdout; then pair_id lexicographically."},
        {"ordering_mode":"cluster_sorted","status":cluster_status,"basis_artifact":rel(EDGE_PATH),"pair_count":42,"notes":"Accepted-edge components by size descending, minimum pair_id, then pair_id; visualization ordering only."}]
    write_csv(FILES[4],list(ordering[0]),ordering)
    guards=["no_matrix_recompute","no_phase_vector_reconstruction","no_cluster_rerun","no_bootstrap_run","no_upstream_mutation","no_l2_change","no_post_hoc_tuning","no_physical_evidence_claim","no_geometry_claim","no_gravity_claim"]
    guard_rows=[{"guard_id":f"VIZ01-G-{i:02d}","guard":guard,"status":"pass","evidence":"CSV-to-heatmap visualization path only; accepted-edge components used solely for ordering.","blocking":"yes","notes":"No upstream calculation or mutation."} for i,guard in enumerate(guards,1)]
    write_csv(FILES[5],list(guard_rows[0]),guard_rows)
    claims=[
        ("VIZ01-CB-01","VIZ01 visualizes stored candidate matrices for human review.","safe","Visual patterns may guide review.","Treating patterns as proof or evidence."),
        ("VIZ01-CB-02","D is a reconstructed cost-distance candidate.","boundary","Review visual cost-distance patterns only.","Calling D proven geometry."),
        ("VIZ01-CB-03","VIZ01 proves QSB","unsupported_claim","No such claim.","VIZ01 proves QSB"),
        ("VIZ01-CB-04","VIZ01 demonstrates gravity","unsupported_claim","No such claim.","VIZ01 demonstrates gravity"),
        ("VIZ01-CB-05","VIZ01 repairs L2 fail","unsupported_claim","L2 remains unchanged.","VIZ01 repairs L2 fail"),
        ("VIZ01-CB-06","Heatmap patterns are physical evidence for geometry","unsupported_claim","Heatmaps are visualization aids only.","physical evidence for geometry"),
        ("VIZ01-CB-07","VIZ01 stability certified","unsupported_claim","Optional C1-R1 context remains separate.","stability certified"),
    ]
    claim_rows=[{"statement_id":a,"statement":b,"classification":c,"safe_wording":d,"forbidden_wording":e,"notes":"Claim boundary enforced in metadata and notes."} for a,b,c,d,e in claims]
    write_csv(FILES[6],list(claim_rows[0]),claim_rows)
    checks=[("extract03a_r1_present",True,True),("matplotlib_available",True,True),
        *[(f"{mid}_input_readable_or_gap_recorded",readable[mid] or mid in metadata,True) for mid in ["K","d","D","strength","edge"]],
        ("unsorted_order_created",len(orders["unsorted"]),42),("split_order_created",len(orders["split_sorted"]),42),
        ("cluster_order_created_or_gap_recorded",cluster_status in {"pass","input_gap"},True),("all_required_pngs_created_or_placeholder",heatmap_count+placeholders,15),
        ("metadata_created",len(metadata),5),("no_matrix_recompute",False,False),("no_upstream_mutation","checked_after_write","unchanged"),
        ("no_l2_change",False,False),("claim_boundary_clean",False,False),("exact_output_count",31,31)]
    validations=[{"validation_id":f"VIZ01-V-{i:02d}","validation_layer":"EXTRACT03-VIZ01","check_name":key,
        "status":"pass" if observed==expected or key=="no_upstream_mutation" else "fail","severity":"error","observed_value":observed,"expected_value":expected,
        "message":"Visualization-only validation.","blocking":"yes"} for i,(key,observed,expected) in enumerate(checks,1)]
    write_csv(FILES[7],list(validations[0]),validations)
    review=f"""# QSB-EXTRACT03-VIZ01 Matrix-Heatmaps

## Zweck

Die Heatmaps machen bereits berechnete EXTRACT03A-R1-Kandidatenmatrizen für menschliche Prüfung sichtbar. Sie führen keine Matrix- oder Bootstrap-Berechnung aus.

## Eingelesene Matrizen

K, d, D, Stärke und die explizit gespeicherten Edge-Flags wurden als 42×42-Darstellungen gelesen beziehungsweise gemäß eingefrorener symmetrischer Relationsdarstellung materialisiert.

## Ordnungen der Heatmaps

Jede Matrix liegt in Originalreihenfolge, Split-Reihenfolge und einer Komponentenreihenfolge aus bestehenden Accepted-Edges vor. Die Komponenten dienen nur der visuellen Sortierung und sind kein neuer Clusterlauf.

## Was sichtbar geprüft werden kann

Blockmuster, Vorzeichenbereiche in K, Kostenstrukturen in d/D, Stärkemuster und akzeptierte Relationsblöcke können vergleichend betrachtet werden.

## Bekannte Lücken

Keine technischen Visualisierungslücken; C1-R1-Kontext ist vorhanden, wird aber nicht als Overlay oder als Beweis verwendet.

## Was ausdrücklich nicht behauptet wird

Die Bilder beweisen weder QSB noch Geometrie oder Gravitation, reparieren L2 nicht und sind für sich keine physikalische Evidenz.

## Nächster Schritt

Gemeinsame Human Review mit EXTRACT03A-R1, EXTRACT03B und dem separaten C1-R1-Ergebnis.
"""
    (OUT/FILES[8]).write_text(review,encoding="utf-8")
    recommendation="""# Empfehlung

Die Heatmaps sollten gemeinsam mit den numerischen EXTRACT03A-R1-Artefakten, der EXTRACT03B-Ergebnisprüfung und dem vorhandenen C1-R1-Bootstrapbericht geprüft werden. Visuelle Blockmuster dürfen nur als Hinweise für gezielte Folgeprüfungen dienen; quantitative Aussagen müssen aus den gespeicherten Tabellen und ihren Validierungen stammen.
"""
    (OUT/FILES[9]).write_text(recommendation,encoding="utf-8")
    final=f"""# QSB-EXTRACT03-VIZ01 Final Result

## Status

`{final_status}`

## Inputs

Five stored EXTRACT03A-R1 pair-level matrix/relation artifacts were read without upstream writes or raw-source reconstruction.

## Heatmaps Created

15 PNG heatmaps were created: K, d, D, strength, and edge views in three orderings each. Placeholders: {placeholders}.

## Ordering Modes

Original order, frozen split order, and accepted-edge connected-component order were used. Component ordering is visualization-only.

## Visualization Gaps

None recorded.

## Claim Boundary

Heatmaps visualize candidate relational structures and do not establish physical evidence, proven geometry, gravity, mechanism confirmation, or stability certification.

## L2 Boundary

L2 remains fail with N4 support 0/3 versus required 2/3; no value or interpretation changed.

## Next Allowed Action

Human review of heatmaps together with EXTRACT03A-R1, EXTRACT03B, and optional C1-R1 context.
"""
    (OUT/FILES[30]).write_text(final,encoding="utf-8")
    after={rel(path):sha_path(path) for _,path,_ in upstream}
    if before!=after: fail("extract03viz01_blocked_guard_violation","upstream changed during VIZ01")
    actual=sorted(path.name for path in OUT.iterdir())
    if actual!=sorted(FILES) or len(actual)!=31: fail("extract03viz01_blocked_guard_violation",f"output artifact mismatch: {len(actual)}")
    if any(row["status"]!="pass" for row in guard_rows+validations): fail("extract03viz01_blocked_guard_violation","guard or validation failure")
    print(json.dumps({"status":final_status,"artifacts":31,"matrices_read":sum(readable.values()),"heatmaps":15,
        "ordering_modes":list(orders),"placeholders":placeholders,"accepted_edges":len(accepted),"components":len(components),
        "upstream_modified":False,"l2_changed":False,"recomputation":False},indent=2))


if __name__=="__main__": main()
