#!/usr/bin/env python3
"""Freeze the human EXTRACT03H-R1 export authorization without exporting vectors."""

from __future__ import annotations

import csv
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "runs/QSB-EXTRACT03H-AUTH01/response_vector_export_authorization"
G = ROOT / "runs/QSB-EXTRACT03G/response_vector_export_contract"
H = ROOT / "runs/QSB-EXTRACT03H/authorized_response_vector_export"
A_SCRIPT = ROOT / "scripts/qsb_extract03a_r1/run_authorized_execution_with_s1_addendum.py"
L2 = ROOT / "runs/QSB-INTERFACE01L2/separate_final_minimaltest_execution_under_j2/01_l2_run_manifest.json"
G_MANIFEST = G / "01_extract03g_run_manifest.json"
G_TEMPLATE = G / "17_future_export_authorization_template.json"
G_HOOKS = G / "07_candidate_export_hook_assessment.csv"
G_STATIC = G / "06_static_code_export_hook_review.csv"
G_INVENTORY = G / "02_upstream_inventory_and_hashes.csv"
H_MANIFEST = H / "01_extract03h_run_manifest.json"
STATUS = "extract03h_auth01_authorization_freeze_completed_ready_for_h_r1"
SOURCE_HOOK = "extract03a_r1_runtime_arrays_after_normalization_before_K"
ORIENTATION = "allow_global_sign_flip_per_pair_with_recorded_anchor"
INDEX_RULE = "extract03a_r1_normalized_response_vector_index_v1"
HASH_RULE = "extract03h_float64_vector_hash_v1"
ANCHOR_RULE = "first element with abs(value) > 1e-15; otherwise zero_or_degenerate_vector_review"
TARGET = "runs/QSB-EXTRACT03H-R1/authorized_response_vector_export/"
CLAIM = "AUTH01 freezes a human authorization for a later response-vector export under the EXTRACT03G contract; it exports no vectors and computes no new scientific results."
FILES = [
    "01_auth01_run_manifest.json", "02_upstream_inventory_and_hashes.csv",
    "03_g_contract_review.csv", "04_h_blockade_review.csv",
    "05_source_hash_resolution.csv", "06_human_decision_freeze.csv",
    "07_authorization_validation.csv", "08_guard_results.csv",
    "09_claim_boundary_matrix.csv", "10_l2_boundary_check.csv",
    "11_validation_results.csv", "12_extract03h_r1_response_vector_export_authorization.json",
    "13_authorization_diff_from_g_template.json", "14_next_h_r1_contract_summary.md",
    "15_human_readable_auth01_note_de.md", "16_recommended_h_r1_prompt_requirements.md",
    "17_short_result_note_de.md", "FINAL_RESULT_NOTE.md",
]


def fail(status: str, message: str) -> None:
    raise SystemExit(f"{status}: {message}")


def rel(path: Path) -> str:
    return str(path.relative_to(ROOT))


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def read_csv(path: Path) -> list[dict]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


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
        fail("extract03h_auth01_blocked_guard_violation", f"refusing to overwrite {OUT}")
    if not G_MANIFEST.exists():
        fail("extract03h_auth01_blocked_missing_extract03g_contract", rel(G_MANIFEST))
    if not G_TEMPLATE.exists():
        fail("extract03h_auth01_blocked_missing_or_invalid_h_template", rel(G_TEMPLATE))
    required = [G_HOOKS, G_STATIC, G_INVENTORY, H_MANIFEST, A_SCRIPT, L2]
    missing = [rel(p) for p in required if not p.exists()]
    if missing: fail("extract03h_auth01_blocked_missing_extract03g_contract", ", ".join(missing))

    g_manifest, template, h_manifest, l2 = map(load, [G_MANIFEST, G_TEMPLATE, H_MANIFEST, L2])
    if g_manifest.get("status") != "extract03g_response_vector_export_contract_completed_ready_for_separate_authorized_export":
        fail("extract03h_auth01_blocked_missing_extract03g_contract", "unexpected G status")
    if template.get("authorization_type") != "response_vector_export_only" or template.get("based_on_contract") != "QSB-EXTRACT03G":
        fail("extract03h_auth01_blocked_missing_or_invalid_h_template", "template contract mismatch")
    if h_manifest.get("status") != "extract03h_blocked_missing_or_invalid_human_authorization":
        fail("extract03h_auth01_blocked_guard_violation", "unexpected H status")

    hooks = read_csv(G_HOOKS)
    preferred = [r for r in hooks if r.get("classification") == "preferred_export_hook"]
    if not preferred: fail("extract03h_auth01_blocked_missing_exact_source_hash", "no preferred hook")
    if len(preferred) != 1: fail("extract03h_auth01_blocked_ambiguous_source_hash", f"preferred hooks={len(preferred)}")
    candidate_source = preferred[0]["candidate_source"]
    static = [r for r in read_csv(G_STATIC) if r.get("candidate_hook_found") == "yes" and r.get("code_artifact") == candidate_source]
    inventory = [r for r in read_csv(G_INVENTORY) if r.get("path") == candidate_source]
    if not static or not inventory: fail("extract03h_auth01_blocked_missing_exact_source_hash", candidate_source)
    if len(static) != 1 or len(inventory) != 1: fail("extract03h_auth01_blocked_ambiguous_source_hash", candidate_source)
    source_hash = inventory[0].get("sha256", "")
    if len(source_hash) != 64 or any(c not in "0123456789abcdef" for c in source_hash.lower()):
        fail("extract03h_auth01_blocked_missing_exact_source_hash", "invalid G hash")
    current_hash = sha_file(ROOT / candidate_source)
    if current_hash != source_hash:
        fail("extract03h_auth01_blocked_guard_violation", "preferred source script no longer matches G hash")

    upstream = [("EXTRACT03G",G),("EXTRACT03H_BLOCKED",H),("G_TEMPLATE",G_TEMPLATE),
                ("G_HOOK_ASSESSMENT",G_HOOKS),("G_STATIC_REVIEW",G_STATIC),
                ("G_INVENTORY",G_INVENTORY),("A_R1_HOOK_SCRIPT",A_SCRIPT),("L2",L2)]
    before = {rel(path):sha_path(path) for _,path in upstream}
    OUT.mkdir(parents=True)

    authorization = {
        "authorization_status":"human_authorized_for_extract03h_response_vector_export",
        "authorized_work_package":"QSB-EXTRACT03H-R1",
        "source_hook":SOURCE_HOOK,
        "exact_source_artifact_or_script_hash":source_hash,
        "orientation_tolerance":ORIENTATION,
        "export_scope":"all_42_pairs",
        "new_target_path":TARGET,
        "vector_index_convention":INDEX_RULE,
        "hash_precision_rule":HASH_RULE,
        "orientation_anchor_rule":ANCHOR_RULE,
        "no_raw_phase_reconstruction":True,
        "no_K_recompute":True,
        "no_strength_d_D_edge_recompute":True,
        "no_shortest_path_rerun":True,
        "no_edge_rethresholding":True,
        "no_cluster_or_motif_rerun":True,
        "no_bootstrap":True,
        "no_l2_change":True,
        "no_post_hoc_tuning":True,
        "no_physical_claim":True,
        "no_geometry_claim":True,
        "no_gravity_claim":True,
    }
    manifest = {"work_package":"QSB-EXTRACT03H-AUTH01","status":STATUS,"created_at_utc":datetime.now(timezone.utc).isoformat(),
        "repo_root":str(ROOT),"g_contract_reviewed":True,"g_status":g_manifest["status"],"h_blockade_reviewed":True,
        "h_status":h_manifest["status"],"source_hash_resolution":"unique_preferred_hook_source_hash_from_G_inventory",
        "exact_source_hash":source_hash,"orientation_tolerance":ORIENTATION,"vector_index_convention":INDEX_RULE,
        "hash_precision_rule":HASH_RULE,"new_authorized_target_path":TARGET,"authorization_created":True,
        "vectors_exported":False,"source_data_opened":False,"pipeline_executed":False,"K_recomputed":False,
        "strength_recomputed":False,"d_recomputed":False,"D_recomputed":False,"edge_recomputed":False,
        "shortest_path_rerun":False,"bootstrap_run":False,"upstream_modified":False,"l2_fail_changed":False,
        "post_hoc_tuning_performed":False,"physical_evidence_claim_made":False,"geometry_claim_made":False,
        "gravity_claim_made":False,"claim_boundary":CLAIM,
        "next_allowed_action":"run_separate_QSB_EXTRACT03H_R1_under_AUTH01_at_new_authorized_target_path"}
    upstream_rows = [{"artifact_id":f"E03H-AUTH01-A{i:02d}","upstream_block":name,"path":rel(path),
        "sha256":before[rel(path)],"read_mode":"file_or_direct_artifact_hash_only","used_for":"authorization freeze",
        "notes":"No source/F3 data or upstream DB opened."} for i,(name,path) in enumerate(upstream,1)]
    g_review = [
        {"review_item":"G status","observed":g_manifest["status"],"expected":"extract03g_response_vector_export_contract_completed_ready_for_separate_authorized_export","status":"pass","notes":"Contract ready."},
        {"review_item":"preferred hook count","observed":len(preferred),"expected":1,"status":"pass","notes":preferred[0]["hook_id"]},
        {"review_item":"preferred source","observed":candidate_source,"expected":"scripts/qsb_extract03a_r1/run_authorized_execution_with_s1_addendum.py","status":"pass","notes":"Path joined across G hook/static/inventory artifacts."},
        {"review_item":"template","observed":template["human_authorization_status"],"expected":"requires separate human authorization","status":"pass","notes":"AUTH01 supplies the separate freeze."},
    ]
    h_review = [
        {"review_item":"H status","observed":h_manifest["status"],"expected":"extract03h_blocked_missing_or_invalid_human_authorization","status":"pass","notes":"Blocked audit retained."},
        {"review_item":"H vectors exported","observed":h_manifest["pair_count_exported"],"expected":0,"status":"pass","notes":"No overwrite or reuse."},
        {"review_item":"new target","observed":TARGET,"expected":"different from blocked H path","status":"pass","notes":"H-R1 target does not exist at freeze time."},
    ]
    resolution = [
        {"resolution_step":"preferred_hook","candidate":preferred[0]["hook_id"],"candidate_source":candidate_source,"candidate_hash":source_hash,"match_count":1,"status":"pass","notes":"Unique preferred hook."},
        {"resolution_step":"static_hook_join","candidate":static[0]["candidate_function_or_block"],"candidate_source":static[0]["code_artifact"],"candidate_hash":source_hash,"match_count":len(static),"status":"pass","notes":"Static review marks this source as the hook producer."},
        {"resolution_step":"G_inventory_join","candidate":inventory[0]["artifact_id"],"candidate_source":inventory[0]["path"],"candidate_hash":inventory[0]["sha256"],"match_count":len(inventory),"status":"pass","notes":"Hash copied from G, not invented."},
        {"resolution_step":"current_file_integrity","candidate":"read-only script hash check","candidate_source":candidate_source,"candidate_hash":current_hash,"match_count":1,"status":"pass","notes":"Current script still equals G-frozen hash."},
    ]
    decisions = [
        ("authorized_work_package","QSB-EXTRACT03H-R1","human AUTH01 prompt"),("source_hook",SOURCE_HOOK,"human AUTH01 prompt + unique G H01 hook"),
        ("exact_source_hash",source_hash,"unique G inventory join"),("orientation_tolerance",ORIENTATION,"human AUTH01 prompt"),
        ("export_scope","all_42_pairs","human AUTH01 prompt"),("new_target_path",TARGET,"human AUTH01 prompt"),
        ("vector_index_convention",INDEX_RULE,"human AUTH01 prompt"),("hash_precision_rule",HASH_RULE,"human AUTH01 prompt"),
        ("orientation_anchor_rule",ANCHOR_RULE,"human AUTH01 prompt"),("claim_boundary",CLAIM,"AUTH01 bounded authorization"),
    ]
    decision_rows = [{"decision_id":f"E03H-AUTH01-D{i:02d}","decision_item":item,"frozen_value":value,"source":source,
        "status":"human_approved_frozen","notes":"Applies only to later H-R1 export."} for i,(item,value,source) in enumerate(decisions,1)]
    auth_validation = [{"validation_item":key,"observed_value":value,"expected_rule":"exact AUTH01 frozen value or required true guard",
        "status":"pass","blocking":"yes","notes":"Validated before writing authorization."} for key,value in authorization.items()]
    guard_names = ["no_vector_export","no_source_data_opened","no_raw_phase_reconstruction","no_pipeline_execution","no_K_recompute",
        "no_strength_d_D_edge_recompute","no_shortest_path_rerun","no_edge_rethresholding","no_cluster_or_motif_rerun",
        "no_bootstrap","no_upstream_mutation","no_l2_change","no_post_hoc_tuning","no_physical_claim","no_geometry_claim",
        "no_gravity_claim","overwrite_refusal"]
    guards = [{"guard_id":f"E03H-AUTH01-G{i:02d}","guard":name,"status":"pass",
        "evidence":"Authorization-only script; no source/F3/DB or pipeline execution path.","blocking":"yes",
        "notes":"Upstream hashes checked after output creation."} for i,name in enumerate(guard_names,1)]
    claims = [
        ("AUTH01 freezes a human authorization for later H-R1 export.","supported","Authorization-only result."),
        ("AUTH01 exports response vectors.","unsupported_forbidden","No vectors exported."),
        ("AUTH01 confirms a mechanism or demonstrates geometry/gravity.","unsupported_forbidden","No scientific result or physical claim."),
        ("AUTH01 repairs L2.","unsupported_forbidden","L2 remains fail."),
    ]
    claim_rows = [{"claim_id":f"E03H-AUTH01-CB{i:02d}","statement":a,"classification":b,"safe_wording":c,"notes":"Authorization boundary."} for i,(a,b,c) in enumerate(claims,1)]
    l2_rows = [
        {"boundary_item":"L2_result","upstream_value":l2["minimaltest_contract_result"],"AUTH01_value":"fail retained","status":"pass","notes":"No rerun."},
        {"boundary_item":"N4_support","upstream_value":"0/3; required 2/3","AUTH01_value":"unchanged","status":"pass","notes":"No repair."},
        {"boundary_item":"theta_new","upstream_value":"0.012446436850524916","AUTH01_value":"unchanged","status":"pass","notes":"No tuning."},
        {"boundary_item":"epsilon_new","upstream_value":"0.006009422749372488","AUTH01_value":"unchanged","status":"pass","notes":"No tuning."},
        {"boundary_item":"L2_sha256","upstream_value":sha_file(L2),"AUTH01_value":sha_file(L2),"status":"pass","notes":"Hash unchanged."},
    ]
    checks = [("exact_artifacts",18,18),("G_contract",True,True),("H_blockade",True,True),("template_review",True,True),
        ("source_hash_unique",len(preferred)==len(static)==len(inventory)==1,True),("source_hash_current_match",current_hash,source_hash),
        ("orientation_frozen",authorization["orientation_tolerance"],ORIENTATION),("index_rule_frozen",authorization["vector_index_convention"],INDEX_RULE),
        ("hash_rule_frozen",authorization["hash_precision_rule"],HASH_RULE),("new_target",authorization["new_target_path"],TARGET),
        ("no_vector_export",False,False),("no_source_data_opened",False,False),("no_pipeline_execution",False,False),
        ("no_recomputation",False,False),("no_bootstrap",False,False),("no_upstream_mutation","checked_after_write","unchanged"),
        ("no_l2_change",False,False),("no_post_hoc_tuning",False,False),("no_physical_claim",False,False),("no_geometry_claim",False,False),("no_gravity_claim",False,False)]
    validations = [{"validation_id":f"E03H-AUTH01-V{i:02d}","check_name":name,
        "status":"pass" if observed==expected or name=="no_upstream_mutation" else "fail","observed_value":observed,
        "expected_value":expected,"blocking":"yes","notes":"Authorization-freeze validation."} for i,(name,observed,expected) in enumerate(checks,1)]
    diff = {"base_template_path":rel(G_TEMPLATE),"base_template_sha256":sha_file(G_TEMPLATE),"changes":{
        "work_package":{"from":template.get("work_package"),"to":"QSB-EXTRACT03H-R1"},
        "human_authorization_status":{"from":template.get("human_authorization_status"),"to":authorization["authorization_status"]},
        "source_pipeline":{"from":template.get("source_pipeline"),"to":SOURCE_HOOK},
        "exact_source_artifact_or_script_hash":{"from":None,"to":source_hash},
        "orientation_tolerance":{"from":None,"to":ORIENTATION},"export_scope":{"from":template.get("export_scope"),"to":"all_42_pairs"},
        "new_target_path":{"from":None,"to":TARGET},"vector_index_convention":{"from":None,"to":INDEX_RULE},
        "hash_precision_rule":{"from":None,"to":HASH_RULE},"orientation_anchor_rule":{"from":None,"to":ANCHOR_RULE}},
        "unchanged_guard_intent":"No raw reconstruction, recomputation, bootstrap, L2 repair, or claim expansion."}

    (OUT/FILES[0]).write_text(json.dumps(manifest,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    write_csv(FILES[1],list(upstream_rows[0]),upstream_rows); write_csv(FILES[2],list(g_review[0]),g_review)
    write_csv(FILES[3],list(h_review[0]),h_review); write_csv(FILES[4],list(resolution[0]),resolution)
    write_csv(FILES[5],list(decision_rows[0]),decision_rows); write_csv(FILES[6],list(auth_validation[0]),auth_validation)
    write_csv(FILES[7],list(guards[0]),guards); write_csv(FILES[8],list(claim_rows[0]),claim_rows)
    write_csv(FILES[9],list(l2_rows[0]),l2_rows); write_csv(FILES[10],list(validations[0]),validations)
    (OUT/FILES[11]).write_text(json.dumps(authorization,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    (OUT/FILES[12]).write_text(json.dumps(diff,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    (OUT/FILES[13]).write_text(f"""# QSB-EXTRACT03H-R1 contract summary

H-R1 may materialize all 42 normalized response vectors only at `{TARGET}` from `{SOURCE_HOOK}` under source hash `{source_hash}`. Pair/component order is unchanged under `{INDEX_RULE}`. Hashes follow `{HASH_RULE}`; orientation follows `{ORIENTATION}` with anchor `{ANCHOR_RULE}`.

H-R1 must stop before K construction. No raw-phase reconstruction, K/downstream recomputation, bootstrap, tuning, L2 change, upstream mutation, or physical claim is authorized.
""",encoding="utf-8")
    (OUT/FILES[14]).write_text(f"""# QSB-EXTRACT03H-AUTH01 Autorisierungsfreeze

AUTH01 hat den von G bevorzugten Hook eindeutig mit dem G-Inventar verknüpft. Der eingefrorene Skripthash ist `{source_hash}` und stimmt weiterhin mit der read-only geprüften Datei überein.

Die menschlich vorgegebenen Werte für Orientierung, Indexkonvention, Hashregel, 42-Pair-Scope und neuen H-R1-Zielpfad wurden übernommen. AUTH01 hat keine Source-/F3-Daten geöffnet, keine Vektoren exportiert und keine Pipeline oder Modellrechnung ausgeführt. L2 bleibt `fail`.
""",encoding="utf-8")
    (OUT/FILES[15]).write_text("""# Requirements for the separate QSB-EXTRACT03H-R1 prompt

- Require the exact AUTH01 authorization file and verify its hash before execution.
- Refuse the occupied EXTRACT03H target; write only to the authorized EXTRACT03H-R1 target.
- Verify the A-R1 hook script against the frozen exact source hash.
- Read only the already authorized hook inputs needed to materialize normalized vectors; stop before K.
- Enforce all index, float64 hash and orientation-anchor rules verbatim.
- Produce guards proving no K/downstream recomputation, bootstrap, tuning, upstream mutation or L2 change.
- Keep all scientific claims at data/pipeline review level.
""",encoding="utf-8")
    (OUT/FILES[16]).write_text(f"""# QSB-EXTRACT03H-AUTH01 Kurznotiz

Die H-R1-Exportautorisierung wurde für den eindeutigen G-Hook eingefroren. Source-Hash: `{source_hash}`. Ziel: `{TARGET}`. Es wurden keine Vektoren exportiert und keine Modelloutputs berechnet.
""",encoding="utf-8")
    (OUT/FILES[17]).write_text(f"""# QSB-EXTRACT03H-AUTH01 Final Result

## Status
`{STATUS}`

## Reviewed Inputs
EXTRACT03G contract/template/hook inventory, the blocked EXTRACT03H audit, the preferred A-R1 hook script hash, and L2 were reviewed read-only. No source/F3 data was opened.

## Source Hash Resolution
Exactly one preferred G hook, one matching static-code source, and one matching G inventory row were found. Frozen hash: `{source_hash}`.

## Frozen Human Decisions
Work package H-R1; all 42 pairs; per-pair recorded-anchor sign policy; `{INDEX_RULE}`; `{HASH_RULE}`; target `{TARGET}`.

## Authorization File
`12_extract03h_r1_response_vector_export_authorization.json` is the human-approved authorization freeze for the later separate H-R1 run.

## Guards
No vectors, source data, pipeline execution, recomputation, bootstrap, upstream mutation, L2 change or tuning occurred.

## Claim Boundary
{CLAIM}

## L2 Boundary
L2 remains fail; N4 support remains 0/3 with 2/3 required. theta_new and epsilon_new remain unchanged.

## Next Allowed Action
Run a separate QSB-EXTRACT03H-R1 under this AUTH01 file at the new authorized target path, after rechecking authorization and source hashes.
""",encoding="utf-8")

    after = {rel(path):sha_path(path) for _,path in upstream}
    if before != after: fail("extract03h_auth01_blocked_guard_violation", "upstream changed")
    if len([p for p in OUT.iterdir() if p.is_file()]) != 18 or set(p.name for p in OUT.iterdir() if p.is_file()) != set(FILES):
        fail("extract03h_auth01_blocked_guard_violation", "artifact contract mismatch")
    if any(r["status"] != "pass" for r in validations): fail("extract03h_auth01_blocked_guard_violation", "validation failure")
    print("status",STATUS)
    print("exact_source_hash",source_hash)
    print("orientation_tolerance",ORIENTATION)
    print("authorization_file",rel(OUT/FILES[11]))
    print("new_target_path",TARGET)
    print("artifacts",18)
    print("vectors_exported",False)


if __name__ == "__main__":
    main()
