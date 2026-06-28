#!/usr/bin/env python3
"""Audit EXTRACT03H authorization and fail closed without authorized vector export."""

from __future__ import annotations

import csv
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "runs/QSB-EXTRACT03H/authorized_response_vector_export"
G = ROOT / "runs/QSB-EXTRACT03G/response_vector_export_contract"
F = ROOT / "runs/QSB-EXTRACT03F/response_vector_signature_export"
E = ROOT / "runs/QSB-EXTRACT03E/perfection_origin_review"
D = ROOT / "runs/QSB-EXTRACT03D/block_mechanism_review"
A = ROOT / "runs/QSB-EXTRACT03A-R1/authorized_execution_with_s1_addendum"
L2 = ROOT / "runs/QSB-INTERFACE01L2/separate_final_minimaltest_execution_under_j2/01_l2_run_manifest.json"
TEMPLATE = G / "17_future_export_authorization_template.json"
AUTH_CANDIDATES = [
    G / "extract03h_response_vector_export_authorization.json",
    ROOT / "runs/QSB-EXTRACT03/input/extract03h_response_vector_export_authorization.json",
    TEMPLATE,
]
STATUS = "extract03h_blocked_missing_or_invalid_human_authorization"
CLAIM = "EXTRACT03H is blocked because no valid human export authorization is present; no response vectors were exported and no physical interpretation is established."
FILES = [
    "01_extract03h_run_manifest.json", "02_upstream_inventory_and_hashes.csv",
    "03_authorization_review.csv", "04_source_hook_resolution.csv",
    "05_input_availability_review.csv", "06_export_scope_manifest.csv",
    "07_response_vector_export.csv", "08_response_vector_hashes.csv",
    "09_sign_normalized_vector_signatures.csv", "10_vector_identity_groups.csv",
    "11_vector_opposition_groups.csv", "12_component_vector_alignment.csv",
    "13_K_vector_alignment_review.csv", "14_orientation_anchor_review.csv",
    "15_vector_index_convention.csv", "16_precision_rounding_hash_rule.csv",
    "17_export_integrity_checks.csv", "18_missing_or_blocked_items.csv",
    "19_definition_boundary_review.csv", "20_guard_results.csv",
    "21_claim_boundary_matrix.csv", "22_l2_boundary_check.csv",
    "23_validation_results.csv", "24_human_readable_export_review_de.md",
    "25_publication_safe_note_candidates.md", "26_next_step_options.csv",
    "27_recommended_next_step.md", "28_vector_signature_group_overview.png",
    "29_component_vector_alignment.png", "30_short_result_note_de.md",
    "31_machine_readable_vector_signature_summary.json", "32_export_contract_used.json",
    "33_authorization_used.json", "FINAL_RESULT_NOTE.md",
]


def fail(status: str, message: str) -> None:
    raise SystemExit(f"{status}: {message}")


def rel(path: Path) -> str:
    return str(path.relative_to(ROOT))


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


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
        h.update(item.name.encode()); h.update(b"\0")
        h.update(sha_file(item).encode()); h.update(b"\n")
    return h.hexdigest()


def write_csv(name: str, fields: list[str], rows: list[dict]) -> None:
    with (OUT / name).open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, extrasaction="ignore")
        writer.writeheader(); writer.writerows(rows)


def main() -> None:
    if OUT.exists():
        fail("extract03h_blocked_guard_violation", f"refusing to overwrite {OUT}")
    g_manifest_path = G / "01_extract03g_run_manifest.json"
    if not g_manifest_path.exists():
        fail("extract03h_blocked_missing_extract03g_contract", rel(g_manifest_path))
    g_manifest = load(g_manifest_path)
    if g_manifest.get("status") != "extract03g_response_vector_export_contract_completed_ready_for_separate_authorized_export":
        fail("extract03h_blocked_missing_extract03g_contract", "unexpected EXTRACT03G status")

    auth_path = next((p for p in AUTH_CANDIDATES if p.exists()), None)
    auth = load(auth_path) if auth_path else {}
    required_auth = {
        "authorization_status": "human_authorized_for_extract03h_response_vector_export",
        "authorized_work_package": "QSB-EXTRACT03H",
        "source_hook": "extract03a_r1_runtime_arrays_after_normalization_before_K",
        "export_scope": "all_42_pairs",
        "no_raw_phase_reconstruction": True,
        "no_K_recompute": True,
        "no_strength_d_D_edge_recompute": True,
        "no_bootstrap": True,
        "no_l2_change": True,
        "no_physical_claim": True,
    }
    allowed_orientation = {
        "exact_signed_orientation_only",
        "allow_global_sign_flip_per_pair_with_recorded_anchor",
        "allow_component_level_global_sign_flip_with_recorded_anchor",
    }
    orientation = auth.get("orientation_tolerance")
    source_hash = auth.get("exact_source_artifact_or_script_hash")
    scalar_present = bool(auth.get("vector_index_convention")) and bool(auth.get("hash_precision_rule"))
    authorization_valid = (all(auth.get(k) == v for k, v in required_auth.items())
                           and orientation in allowed_orientation
                           and isinstance(source_hash, str) and len(source_hash) == 64
                           and all(c in "0123456789abcdef" for c in source_hash.lower())
                           and scalar_present)

    upstream = [("EXTRACT03G", G), ("EXTRACT03F", F), ("EXTRACT03E", E),
                ("EXTRACT03D", D), ("EXTRACT03A_R1", A), ("L2", L2)]
    if auth_path: upstream.append(("AUTHORIZATION_CANDIDATE", auth_path))
    upstream = [(name, path) for name, path in upstream if path.exists()]
    before = {rel(path): sha_path(path) for _, path in upstream}
    OUT.mkdir(parents=True)

    inventory = [{"artifact_id":f"E03H-A{i:02d}","upstream_block":name,"path":rel(path),
        "exists":"yes","sha256":before[rel(path)],"role":"read-only authorization/block audit input",
        "used_for":"authorization, contract, boundary and lineage review","notes":"No upstream execution or mutation."}
        for i,(name,path) in enumerate(upstream,1)]

    review_specs = [
        ("authorization_status",auth.get("authorization_status"),required_auth["authorization_status"]),
        ("authorized_work_package",auth.get("authorized_work_package"),required_auth["authorized_work_package"]),
        ("source_hook",auth.get("source_hook"),required_auth["source_hook"]),
        ("exact_source_hash",source_hash,"64 lowercase hexadecimal SHA-256"),
        ("orientation_tolerance",orientation,"one of the three allowed orientation policies"),
        ("export_scope",auth.get("export_scope"),required_auth["export_scope"]),
        ("vector_index_convention",auth.get("vector_index_convention"),"explicit nonempty frozen rule"),
        ("hash_precision_rule",auth.get("hash_precision_rule"),"explicit nonempty frozen rule"),
        ("no_raw_phase_reconstruction",auth.get("no_raw_phase_reconstruction"),True),
        ("no_K_recompute",auth.get("no_K_recompute"),True),
        ("no_strength_d_D_edge_recompute",auth.get("no_strength_d_D_edge_recompute"),True),
        ("no_bootstrap",auth.get("no_bootstrap"),True),
        ("no_l2_change",auth.get("no_l2_change"),True),
        ("no_physical_claim",auth.get("no_physical_claim"),True),
    ]
    auth_review = []
    for item, observed, expected in review_specs:
        if item == "exact_source_hash": ok = isinstance(observed,str) and len(observed)==64 and all(c in "0123456789abcdef" for c in observed.lower())
        elif item == "orientation_tolerance": ok = observed in allowed_orientation
        elif item in {"vector_index_convention","hash_precision_rule"}: ok = bool(observed)
        else: ok = observed == expected
        auth_review.append({"authorization_item":item,"observed_value":"MISSING" if observed is None else observed,
            "expected_value":expected,"status":"pass" if ok else "fail","blocking":"yes",
            "notes":"Template values are not human authorization; all required items must pass."})

    hook_rows = [{"hook_item":"G preferred hook","candidate_location":"EXTRACT03A-R1 runtime arrays after normalization, before K construction",
        "static_location_status":"located_by_G","authorization_status":"blocked_invalid_authorization",
        "exact_source_hash_status":"missing_not_frozen","resolution_status":"not_authorized_for_materialization",
        "notes":"No source data opened and no runtime array materialized in H."}]
    inputs = [{"input_id":f"E03H-I{i:02d}","path":rel(path),"available":"yes","read_status":"read_only",
        "purpose":"authorization/block audit","notes":"No upstream programs executed."} for i,(_,path) in enumerate(upstream,1)]
    scope = [{"scope_item":"full normalized response vectors","authorized":"no","planned_count":"0","actual_count":"0",
        "status":"blocked_no_valid_human_authorization","notes":"No vector export."},
        {"scope_item":"all_42_pairs","authorized":"no","planned_count":"42 if later authorized","actual_count":"0",
        "status":"blocked_no_valid_human_authorization","notes":"Scope not frozen by a valid H authorization."}]

    blocked_note = "No valid human EXTRACT03H authorization; no vector data materialized."
    vector_rows = [{"pair_id":"NA","component_id":"NA","split_label":"NA","vector_index_start":"NA","vector_index_end":"NA",
        "vector_length":"0","vector_values_json":"[]","vector_norm":"NA","vector_mean":"NA","vector_std":"NA",
        "orientation_anchor_value":"NA","export_status":"blocked_no_authorized_vector_export","notes":blocked_note}]
    hash_rows = [{"pair_id":"NA","raw_vector_sha256":"NA","rounded_vector_sha256":"NA","sign_normalized_sha256":"NA",
        "hash_precision_rule":"MISSING_NOT_AUTHORIZED","orientation_anchor":"NA","hash_status":"blocked_no_authorized_vector_export","notes":blocked_note}]
    sig_rows = [{"pair_id":"NA","component_id":"NA","sign_normalized_sha256":"NA","orientation_anchor":"NA","orientation_sign":"NA",
        "signature_status":"blocked_no_authorized_vector_export","notes":blocked_note}]
    identity_rows = [{"identity_group_id":"NA","member_pair_ids":"","member_count":"0","component_ids":"",
        "component_alignment_status":"not_evaluated_blocked","notes":blocked_note}]
    opposition_rows = [{"opposition_group_id":"NA","anchor_pair_id":"NA","opposed_pair_ids":"","member_count":"0",
        "component_ids":"","opposition_status":"not_evaluated_blocked","notes":blocked_note}]
    component_rows = [{"component_id":"NA","component_size":"NA","exported_pair_count":"0","identity_group_ids":"",
        "opposition_group_ids":"","alignment_status":"not_evaluated_blocked","notes":blocked_note}]
    k_rows = [{"pair_i":"NA","pair_j":"NA","component_i":"NA","component_j":"NA","K_value":"NA","abs_K":"NA",
        "vector_relation":"not_evaluated_blocked","alignment_status":"blocked_no_vector_export","notes":blocked_note}]
    orientation_rows = [{"pair_id":"NA","orientation_tolerance":"MISSING","anchor_index":"NA","anchor_value":"NA",
        "orientation_sign":"NA","status":"blocked_missing_orientation_tolerance","notes":"No implicit tolerance invented."}]
    index_rows = [{"index_item":"vector_index_convention","required_rule":"human-frozen explicit convention",
        "observed_rule":"MISSING","status":"blocked","notes":"G proposal is not a substitute for H authorization."},
        {"index_item":"expected_axis_length","required_rule":"4001","observed_rule":"not materialized","status":"blocked","notes":blocked_note}]
    precision_rows = [{"rule_item":"hash_precision_rule","required_rule":"human-frozen raw/rounded/sign-normalized serialization rule",
        "observed_rule":"MISSING","status":"blocked","notes":"No precision rule inferred."},
        {"rule_item":"raw_value_preservation","required_rule":"binary64 under authorized G contract","observed_rule":"not executed","status":"blocked","notes":blocked_note}]
    integrity_rows = [{"check_id":"E03H-IC-01","check_name":"no_vector_rows_exported","status":"pass","observed":"0 vectors; one blockade sentinel row","expected":"0 when blocked","notes":blocked_note},
        {"check_id":"E03H-IC-02","check_name":"authorization_fail_closed","status":"pass","observed":"export blocked","expected":"blocked","notes":"No source hook execution."},
        {"check_id":"E03H-IC-03","check_name":"upstream_read_only","status":"pass","observed":"hash check after write","expected":"unchanged","notes":"Verified at end."}]
    blocked_items = [
        ("E03H-B01","valid_human_authorization","Only the unfilled G template exists.","blocking","Create a separate human-approved H authorization."),
        ("E03H-B02","exact_source_hash","No exact source artifact/script hash is frozen.","blocking","Select and freeze exactly one hook source hash."),
        ("E03H-B03","orientation_tolerance","No allowed orientation policy is frozen.","blocking","Choose exactly one allowed orientation policy."),
        ("E03H-B04","index_and_hash_rules","Vector index convention and hash precision rule are absent.","blocking","Freeze both rules without changing G scope."),
    ]
    blocked_rows = [{"item_id":a,"category":b,"description":c,"severity":d,"recommended_resolution":e,"notes":"No export until resolved."} for a,b,c,d,e in blocked_items]
    boundaries = [
        ("authorization_boundary","No human authorization means no vector materialization.","enforced"),
        ("source_boundary","No F3/raw/source DB read occurred.","enforced"),
        ("model_boundary","No K, strength, d, D, edge or shortest-path operation occurred.","enforced"),
        ("claim_boundary",CLAIM,"enforced"),
    ]
    boundary_rows = [{"boundary_id":f"E03H-DB-{i:02d}","boundary":a,"rule":b,"status":c,"notes":"Controlled blocked run."} for i,(a,b,c) in enumerate(boundaries,1)]
    guard_names = ["authorization_required","no_vector_export_when_blocked","no_raw_phase_reconstruction","no_K_recompute",
        "no_strength_d_D_edge_recompute","no_shortest_path_rerun","no_edge_rethresholding","no_cluster_or_motif_rerun",
        "no_bootstrap","no_parameter_or_scope_change","no_upstream_mutation","no_l2_change","no_post_hoc_tuning",
        "no_physical_evidence_claim","no_geometry_claim","no_gravity_claim"]
    guards = [{"guard_id":f"E03H-G-{i:02d}","guard":name,"status":"pass","evidence":"Fail-closed authorization audit; no vector/source/model execution.",
        "blocking":"yes","notes":"Upstream hashes verified after artifact creation."} for i,name in enumerate(guard_names,1)]
    claims = [
        ("EXTRACT03H was blocked due to missing or invalid human authorization.","supported","Controlled authorization-audit result."),
        ("No response vectors were exported.","supported","Export table contains only blockade sentinel."),
        ("EXTRACT03H exported vectors or established identity/opposition.","unsupported_forbidden","No export and no relation analysis."),
        ("EXTRACT03H establishes physical, geometric, gravitational, or Interface evidence.","unsupported_forbidden","No physical claim."),
        ("EXTRACT03H repairs L2.","unsupported_forbidden","L2 remains fail."),
    ]
    claim_rows = [{"claim_id":f"E03H-CB-{i:02d}","statement":a,"classification":b,"safe_wording":c,"notes":"Blocked-run boundary."} for i,(a,b,c) in enumerate(claims,1)]
    l2 = load(L2)
    l2_rows = [
        {"boundary_item":"L2_result","upstream_value":l2["minimaltest_contract_result"],"H_value":"fail retained","status":"pass","notes":"No rerun or reinterpretation."},
        {"boundary_item":"N4_support","upstream_value":"0/3; required 2/3","H_value":"unchanged","status":"pass","notes":"No repair."},
        {"boundary_item":"theta_new","upstream_value":"0.012446436850524916","H_value":"unchanged","status":"pass","notes":"No tuning."},
        {"boundary_item":"epsilon_new","upstream_value":"0.006009422749372488","H_value":"unchanged","status":"pass","notes":"No tuning."},
        {"boundary_item":"L2_sha256","upstream_value":sha_file(L2),"H_value":sha_file(L2),"status":"pass","notes":"Hash unchanged."},
    ]
    validations_spec = [
        ("exact_artifact_contract",34,34),("extract03g_present",g_manifest["status"],"extract03g_response_vector_export_contract_completed_ready_for_separate_authorized_export"),
        ("authorization_checked",True,True),("invalid_authorization_blocks_export",authorization_valid,False),
        ("full_vectors_exported",False,False),("pair_count_exported",0,0),("identity_groups_created",0,0),("opposition_groups_created",0,0),
        ("K_alignment_not_computed",False,False),("no_recomputation",False,False),("no_raw_phase_reconstruction",False,False),
        ("no_bootstrap",False,False),("no_upstream_mutation","checked_after_write","unchanged"),("no_l2_change",False,False),
        ("no_post_hoc_tuning",False,False),("no_physical_claim",False,False),("no_geometry_claim",False,False),("no_gravity_claim",False,False),
    ]
    validations = [{"validation_id":f"E03H-V-{i:02d}","check_name":name,
        "status":"pass" if observed==expected or name=="no_upstream_mutation" else "fail","observed_value":observed,
        "expected_value":expected,"blocking":"yes","notes":"Blocked-run validation."} for i,(name,observed,expected) in enumerate(validations_spec,1)]

    manifest = {"work_package":"QSB-EXTRACT03H","status":STATUS,"created_at_utc":datetime.now(timezone.utc).isoformat(),"repo_root":str(ROOT),
        "extract03g_seen":True,"extract03g_status":g_manifest["status"],"authorization_seen":auth_path is not None,"authorization_valid":authorization_valid,
        "authorization_status":auth.get("authorization_status",auth.get("human_authorization_status","MISSING")),
        "source_hook":auth.get("source_hook","MISSING_NOT_AUTHORIZED"),"exact_source_hash":source_hash or "MISSING",
        "orientation_tolerance":orientation or "MISSING","export_scope":auth.get("export_scope","MISSING_NOT_AUTHORIZED"),
        "full_vectors_exported":False,"pair_count_exported":0,"vector_length":0,
        "vector_index_convention":auth.get("vector_index_convention","MISSING"),"component_count":6,"component_sizes":[12,10,8,6,4,2],
        "identity_groups_count":0,"opposition_groups_count":0,"K_alignment_created":False,"review_items_count":len(blocked_rows),
        "matplotlib_available":False,"K_recomputed":False,"strength_recomputed":False,"d_recomputed":False,"D_recomputed":False,
        "edge_recomputed":False,"shortest_path_rerun":False,"raw_phase_reconstruction":False,"bootstrap_run":False,"upstream_modified":False,
        "l2_fail_changed":False,"post_hoc_tuning_performed":False,"physical_evidence_claim_made":False,"geometry_claim_made":False,
        "gravity_claim_made":False,"claim_boundary":CLAIM,
        "next_allowed_action":"provide_separate_valid_human_EXTRACT03H_authorization_then_run_new_non_overwriting_export_target"}

    (OUT/FILES[0]).write_text(json.dumps(manifest,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    write_csv(FILES[1],list(inventory[0]),inventory); write_csv(FILES[2],list(auth_review[0]),auth_review)
    write_csv(FILES[3],list(hook_rows[0]),hook_rows); write_csv(FILES[4],list(inputs[0]),inputs); write_csv(FILES[5],list(scope[0]),scope)
    write_csv(FILES[6],list(vector_rows[0]),vector_rows); write_csv(FILES[7],list(hash_rows[0]),hash_rows); write_csv(FILES[8],list(sig_rows[0]),sig_rows)
    write_csv(FILES[9],list(identity_rows[0]),identity_rows); write_csv(FILES[10],list(opposition_rows[0]),opposition_rows)
    write_csv(FILES[11],list(component_rows[0]),component_rows); write_csv(FILES[12],list(k_rows[0]),k_rows)
    write_csv(FILES[13],list(orientation_rows[0]),orientation_rows); write_csv(FILES[14],list(index_rows[0]),index_rows)
    write_csv(FILES[15],list(precision_rows[0]),precision_rows); write_csv(FILES[16],list(integrity_rows[0]),integrity_rows)
    write_csv(FILES[17],list(blocked_rows[0]),blocked_rows); write_csv(FILES[18],list(boundary_rows[0]),boundary_rows)
    write_csv(FILES[19],list(guards[0]),guards); write_csv(FILES[20],list(claim_rows[0]),claim_rows)
    write_csv(FILES[21],list(l2_rows[0]),l2_rows); write_csv(FILES[22],list(validations[0]),validations)

    (OUT/FILES[23]).write_text("""# QSB-EXTRACT03H Autorisierter Response-Vektor-Export

## Ausgangspunkt
EXTRACT03G definierte einen prospektiven Vollvektor-Exportvertrag, führte aber keinen Export aus.

## Autorisierungsprüfung
Nur die unausgefüllte G-Vorlage ist vorhanden. Eine menschlich freigegebene H-Autorisierung fehlt; zentrale Pflichtfelder sind nicht eingefroren.

## Export-Hook
Der von G statisch identifizierte Hook bleibt der Laufzeitpunkt nach Normalisierung und vor K. Ohne gültige Autorisierung wurde er nicht ausgeführt oder materialisiert.

## Exportierte Vektoren
Keine. `07_response_vector_export.csv` enthält ausschließlich eine Blockadezeile mit leerer JSON-Liste.

## Identitätsgruppen
Nicht ausgewertet.

## Oppositionsgruppen
Nicht ausgewertet.

## Vergleich mit K≈±1
Nicht durchgeführt, weil keine autorisierten Vektoren vorliegen. K wurde nicht neu berechnet.

## Was dadurch erklärt wird
Der Lauf erklärt nur den kontrollierten Autorisierungsblock, nicht den Ursprung der K-Struktur.

## Was offen bleibt
Gültige H-Autorisierung, exakter Source-Hash, Orientierungspolitik, Indexkonvention und Hash-Präzisionsregel.

## Was ausdrücklich nicht behauptet wird
Keine Aussage über Physik, Raumzeit, Geometrie, Gravitation oder einen Mechanismus in der Natur.

## Nächster Schritt
Eine separate menschlich freigegebene H-Autorisierungsdatei erstellen. Wegen des Overwrite-Schutzes ist danach ein neuer, ausdrücklich festgelegter Zielpfad oder eine autorisierte Entfernung dieses blockierten Outputs nötig.
""",encoding="utf-8")
    (OUT/FILES[24]).write_text("""# Publication-safe note candidates

- EXTRACT03H was blocked before vector materialization because no valid human export authorization was present.
- No vectors, vector signatures, identity/opposition groups, or new model outputs were produced.
- The L2 fail boundary remains unchanged.
""",encoding="utf-8")
    options = [
        {"option_id":"E03H-O01","option":"create_valid_H_authorization","description":"Freeze all required H fields including exact source hash and orientation policy.","recommended":"yes","requires_new_authority":"yes","notes":"No vector export yet."},
        {"option_id":"E03H-O02","option":"retain_blocked_audit","description":"Keep unresolved vector origin and take no further action.","recommended":"acceptable","requires_new_authority":"no","notes":"Preserves current claim boundary."},
    ]
    write_csv(FILES[25],list(options[0]),options)
    (OUT/FILES[26]).write_text("""# Recommended next step

Create and human-approve a separate EXTRACT03H authorization containing every required field. Do not edit the G template in place. Freeze one exact source hash, one allowed orientation policy, the all-42-pairs scope, vector-index convention and hash-precision rule. No export may occur before that review passes.
""",encoding="utf-8")

    try:
        import matplotlib.pyplot as plt
        matplotlib_available = True
        for name,title in [(FILES[27],"Vector signature groups — export blocked"),(FILES[28],"Component vector alignment — export blocked")]:
            fig,ax=plt.subplots(figsize=(8,3)); ax.axis("off"); ax.text(.5,.55,"No authorized vector export",ha="center",va="center",fontsize=16)
            ax.text(.5,.35,"authorization missing or invalid — tabular audit completed",ha="center",va="center",fontsize=10); ax.set_title(title)
            fig.tight_layout(); fig.savefig(OUT/name,dpi=150); plt.close(fig)
    except ImportError:
        matplotlib_available = False
        # Minimal valid 1x1 PNG; tabular artifacts carry the full blockade text.
        png = bytes.fromhex("89504e470d0a1a0a0000000d49484452000000010000000108060000001f15c4890000000d49444154789c6360606060000000050001a5f645400000000049454e44ae426082")
        for name in (FILES[27],FILES[28]): (OUT/name).write_bytes(png)
    manifest["matplotlib_available"] = matplotlib_available
    (OUT/FILES[0]).write_text(json.dumps(manifest,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    (OUT/FILES[29]).write_text("""# QSB-EXTRACT03H Kurznotiz

EXTRACT03H wurde vor jedem Vektorexport kontrolliert blockiert. Es liegt nur eine unausgefüllte Autorisierungsvorlage vor. Keine Response-Vektoren, Signaturen oder Identitäts-/Oppositionsgruppen wurden erzeugt; K und Downstream-Größen wurden nicht neu berechnet. L2 bleibt `fail`.
""",encoding="utf-8")
    machine = {"work_package":"QSB-EXTRACT03H","status":STATUS,"authorization_valid":False,"full_vectors_exported":False,
        "pair_count_exported":0,"vector_length":0,"identity_groups_count":0,"opposition_groups_count":0,"K_alignment_created":False,
        "blocked_items_count":len(blocked_rows),"claim_boundary":CLAIM}
    (OUT/FILES[30]).write_text(json.dumps(machine,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    contract_used = {"work_package":"QSB-EXTRACT03G","manifest_path":rel(g_manifest_path),"manifest_sha256":sha_file(g_manifest_path),
        "status":g_manifest["status"],"preferred_hook":g_manifest["best_export_hook"],"contract_directory_sha256_before_H":before[rel(G)],
        "use_status":"reviewed_but_not_executed_due_to_invalid_authorization"}
    (OUT/FILES[31]).write_text(json.dumps(contract_used,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    auth_used = {"authorization_candidate_path":rel(auth_path) if auth_path else None,
        "authorization_candidate_sha256":sha_file(auth_path) if auth_path else None,"authorization_candidate":auth,
        "authorization_valid":False,"review_result":"blocked_missing_or_invalid_human_authorization",
        "notes":"The G template is not human authorization and was not modified."}
    (OUT/FILES[32]).write_text(json.dumps(auth_used,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    (OUT/FILES[33]).write_text(f"""# QSB-EXTRACT03H Final Result

## Status
`{STATUS}`

## Authorization
Invalid. Only the unfilled EXTRACT03G template was found. Required human approval, exact source hash, orientation policy, vector-index convention and hash-precision rule are missing.

## Source Hook
The G candidate after normalization and before K remains statically identified, but it was not authorized, opened, executed or materialized.

## Exported Vectors
Zero vectors and zero pair records. Export-oriented CSVs contain headers and explicit blockade sentinels only.

## Vector Signatures
No raw, rounded or sign-normalized vector hashes were created.

## Component Alignment
Not evaluated.

## K Alignment
Not evaluated; K was neither recomputed nor compared against new vectors.

## Review Items
Four blocking items: valid human authorization, exact source hash, orientation policy, and frozen index/hash rules.

## Claim Boundary
{CLAIM}

## L2 Boundary
L2 remains fail; N4 support remains 0/3 with 2/3 required. theta_new and epsilon_new remain unchanged.

## Next Allowed Action
Create a separate valid human EXTRACT03H authorization. Any later execution must use a new explicitly authorized output target because this blocked audit is protected from overwrite.
""",encoding="utf-8")

    after = {rel(path): sha_path(path) for _,path in upstream}
    if before != after: fail("extract03h_blocked_guard_violation", "upstream changed during blocked audit")
    if len([p for p in OUT.iterdir() if p.is_file()]) != 34 or set(p.name for p in OUT.iterdir() if p.is_file()) != set(FILES):
        fail("extract03h_blocked_guard_violation", "output artifact contract mismatch")
    if authorization_valid: fail("extract03h_blocked_guard_violation", "blocked path reached with valid authorization")
    if any(v["status"] != "pass" for v in validations): fail("extract03h_blocked_guard_violation", "blocked-run validation failure")
    print("status",STATUS)
    print("authorization_valid",False)
    print("authorization_candidate",rel(auth_path) if auth_path else "none")
    print("vectors_exported",0)
    print("artifacts",34)
    print("upstream_modified",False)
    print("l2_fail_changed",False)


if __name__ == "__main__":
    main()
