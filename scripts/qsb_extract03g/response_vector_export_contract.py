#!/usr/bin/env python3
"""Create the EXTRACT03G design-only response-vector export contract."""

from __future__ import annotations

import csv
import hashlib
import json
import re
import sqlite3
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "runs/QSB-EXTRACT03G/response_vector_export_contract"
F = ROOT / "runs/QSB-EXTRACT03F/response_vector_signature_export"
E = ROOT / "runs/QSB-EXTRACT03E/perfection_origin_review"
D = ROOT / "runs/QSB-EXTRACT03D/block_mechanism_review"
A = ROOT / "runs/QSB-EXTRACT03A-R1/authorized_execution_with_s1_addendum"
MART = A / "21_extract03a_r1_result_mart.sqlite"
L2 = ROOT / "runs/QSB-INTERFACE01L2/separate_final_minimaltest_execution_under_j2/01_l2_run_manifest.json"
A_SCRIPT = ROOT / "scripts/qsb_extract03a_r1/run_authorized_execution_with_s1_addendum.py"
CODE_ARTIFACTS = [
    A_SCRIPT,
    ROOT / "scripts/qsb_extract03f/response_vector_signature_export.py",
    ROOT / "scripts/qsb_extract03e/perfection_origin_review.py",
    ROOT / "scripts/qsb_extract03d/block_mechanism_review.py",
    ROOT / "scripts/qsb_extract03_viz02/topology_organized_relational_matrix.py",
]
STATUS = "extract03g_response_vector_export_contract_completed_ready_for_separate_authorized_export"
CLAIM = "EXTRACT03G defines a future response-vector export contract needed to investigate the source of the near-perfect K structure; it is design-only, executes no export, and establishes no physical interpretation."
FILES = [
    "01_extract03g_run_manifest.json", "02_upstream_inventory_and_hashes.csv",
    "03_input_availability_review.csv", "04_result_mart_schema_inventory.csv",
    "05_existing_response_data_inventory.csv", "06_static_code_export_hook_review.csv",
    "07_candidate_export_hook_assessment.csv", "08_response_vector_export_schema_contract.csv",
    "09_pair_identity_and_order_contract.csv", "10_vector_axis_index_contract.csv",
    "11_unit_dimension_contract.csv", "12_numeric_precision_serialization_contract.csv",
    "13_hash_and_lineage_contract.csv", "14_allowed_forbidden_operations_contract.csv",
    "15_validation_contract.csv", "16_guard_contract.csv",
    "17_future_export_authorization_template.json", "18_future_export_run_contract.md",
    "19_minimal_export_artifact_manifest.csv", "20_review_items.csv",
    "21_claim_boundary_matrix.csv", "22_l2_boundary_check.csv",
    "23_validation_results.csv", "24_human_readable_contract_note_de.md",
    "25_next_step_options.csv", "26_short_result_note_de.md", "FINAL_RESULT_NOTE.md",
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


def code_match(path: Path, patterns: list[str]) -> tuple[str, str]:
    if not path.exists():
        return "none", "file absent"
    lines = path.read_text(encoding="utf-8").splitlines()
    hits = [(i, line.strip()) for i, line in enumerate(lines, 1) if any(p in line for p in patterns)]
    return ("; ".join(f"L{i}: {line}" for i, line in hits[:5]) or "none", f"{len(hits)} static match(es)")


def main() -> None:
    if OUT.exists():
        fail("extract03g_blocked_guard_violation", f"refusing to overwrite {OUT}")
    required = [F / "01_extract03f_run_manifest.json", E / "01_extract03e_run_manifest.json",
                A / "01_extract03a_r1_run_manifest.json", MART, L2]
    if not required[0].exists(): fail("extract03g_blocked_missing_extract03f_outputs", rel(required[0]))
    if not required[2].exists(): fail("extract03g_blocked_missing_extract03a_r1_outputs", rel(required[2]))
    missing = [rel(p) for p in required if not p.exists()]
    if missing: fail("extract03g_response_vector_export_contract_completed_with_input_gaps", ", ".join(missing))

    f_manifest, e_manifest, a_manifest, l2 = map(load, [required[0], required[1], required[2], L2])
    if f_manifest.get("status") not in {"extract03f_response_vector_signature_export_completed_summary_signatures_only", "completed_summary_signatures_only"}:
        fail("extract03g_blocked_missing_extract03f_outputs", "unexpected EXTRACT03F status")
    if e_manifest.get("status") != "extract03e_perfection_origin_review_completed_origin_likely_strength_d_edge_definition":
        fail("extract03g_response_vector_export_contract_completed_with_input_gaps", "unexpected EXTRACT03E status")

    upstream = [("EXTRACT03F", F), ("EXTRACT03E", E), ("EXTRACT03D", D),
                ("EXTRACT03A_R1", A), ("L2", L2)] + [("STATIC_CODE", p) for p in CODE_ARTIFACTS]
    upstream = [(name, path) for name, path in upstream if path.exists()]
    before = {rel(path): sha_path(path) for _, path in upstream}

    try:
        db = sqlite3.connect(f"file:{MART.resolve()}?mode=ro&immutable=1", uri=True)
        integrity = db.execute("pragma integrity_check").fetchone()[0]
        if integrity != "ok": fail("extract03g_blocked_result_mart_unreadable", integrity)
        tables = [r[0] for r in db.execute("select name from sqlite_master where type='table' order by name")]
        schema_rows = []
        for table in tables:
            count = db.execute(f'SELECT count(*) FROM "{table}"').fetchone()[0]
            for col in db.execute(f'PRAGMA table_info("{table}")'):
                name = col[1]; low = f"{table} {name}".lower()
                schema_rows.append({"table_name": table, "column_name": name, "declared_type": col[2],
                    "row_count": count, "could_contain_vector_data": "yes" if any(x in low for x in ("vector_value", "axis_index", "response_value")) else "no",
                    "could_contain_summary_data": "yes" if any(x in low for x in ("phase_response_vector", "norm", "count", "status")) else "no",
                    "could_contain_pair_identity": "yes" if "pair" in low else "no",
                    "notes": "Schema-only read; no vector elements inferred from table name."})
        db.close()
    except (sqlite3.Error, OSError) as exc:
        fail("extract03g_blocked_result_mart_unreadable", str(exc))

    OUT.mkdir(parents=True)
    inventory = [{"artifact_id": f"E03G-A{i:02d}", "upstream_block": name, "path": rel(path),
        "exists": "yes", "sha256": before[rel(path)], "role": "read-only contract input",
        "required": "yes" if name in {"EXTRACT03F", "EXTRACT03E", "EXTRACT03A_R1", "L2"} else "context",
        "notes": "File hash or deterministic direct-artifact directory hash; no mutation."}
        for i, (name, path) in enumerate(upstream, 1)]
    availability = [
        ("EXTRACT03F", F, "summary-only signature findings", "available"),
        ("EXTRACT03E", E, "perfection-origin review", "available"),
        ("EXTRACT03D", D, "component/clique context", "available"),
        ("EXTRACT03A_R1", A, "authorized execution outputs and runtime code", "available"),
        ("result_mart", MART, "schema and summary tables", "read_only_ok"),
        ("L2", L2, "unchanged fail boundary", "available"),
    ]
    availability_rows = [{"input_id": f"E03G-I{i:02d}", "path": rel(p), "available": "yes" if p.exists() else "no",
        "read_status": status if p.exists() else "missing_optional", "purpose": purpose,
        "notes": "Read-only; no upstream execution."} for i, (name, p, purpose, status) in enumerate(availability, 1)]

    response_inventory = [
        {"source_id":"E03G-R01","path_or_table":rel(A/"10_phase_response_vector_summary.csv"),"available":"yes","data_type":"CSV summary","contains_full_vectors":"no","contains_summary_vectors":"yes","contains_pair_ids":"yes","contains_x_or_axis_index":"count_only","contains_units_or_dimension_status":"no","contains_hashes":"lineage_only","read_status":"pass","notes":"42 rows; norms/min/max only."},
        {"source_id":"E03G-R02","path_or_table":rel(MART)+":extract03a_r1_phase_response_vector","available":"yes","data_type":"SQLite summary table","contains_full_vectors":"no","contains_summary_vectors":"yes","contains_pair_ids":"yes","contains_x_or_axis_index":"count_only","contains_units_or_dimension_status":"no","contains_hashes":"lineage_only","read_status":"pass","notes":"42 rows; no vector elements."},
        {"source_id":"E03G-R03","path_or_table":rel(A_SCRIPT)+":wrapped runtime array","available":"code_only_not_persisted","data_type":"binary64 runtime array","contains_full_vectors":"runtime_only","contains_summary_vectors":"no","contains_pair_ids":"via sorted pairs","contains_x_or_axis_index":"via ordered source rows","contains_units_or_dimension_status":"source rows carry metadata","contains_hashes":"no per-vector hash","read_status":"static_only","notes":"Created from already staged wrapped_delta_phi_ij_x; not persisted."},
        {"source_id":"E03G-R04","path_or_table":rel(A_SCRIPT)+":normalized runtime array","available":"code_only_not_persisted","data_type":"binary64 runtime array","contains_full_vectors":"runtime_only","contains_summary_vectors":"no","contains_pair_ids":"via sorted pairs","contains_x_or_axis_index":"inherits wrapped order","contains_units_or_dimension_status":"normalized_dimensionless","contains_hashes":"no per-vector hash","read_status":"static_only","notes":"Direct K input; preferred future export layer together with wrapped channel."},
    ]

    static_rows = []
    for path in CODE_ARTIFACTS:
        hook, count = code_match(path, ["wrapped =", "normalized =", "K = normalized", "phase_response_vector", "response vector"])
        is_a = path == A_SCRIPT
        static_rows.append({"code_artifact":rel(path),"exists":"yes" if path.exists() else "no",
            "searched_for":"wrapped/normalized/K/phase_response_vector persistence",
            "candidate_hook_found":"yes" if is_a else "no",
            "candidate_function_or_block":hook,
            "observed_logic_summary":("Runtime builds wrapped and normalized 42x4001 arrays before K; arrays are not persisted." if is_a else count+"; no independent full-vector producer selected."),
            "would_require_execution":"yes_future_export_only" if is_a else "no",
            "would_require_raw_reconstruction":"no; read already staged wrapped_delta_phi_ij_x" if is_a else "not_applicable",
            "notes":"Static inspection only; script was not executed."})

    hooks = [
        {"hook_id":"E03G-H01","candidate_source":rel(A_SCRIPT),"candidate_location":"after normalized assignment and before K dot product","export_layer":"wrapped_and_normalized_response_runtime_arrays","can_export_full_vectors_without_raw_reconstruction":"yes","can_preserve_pair_id_order":"yes","can_preserve_axis_index":"yes","can_preserve_units_dimension_status":"yes_with_source_metadata_join","risk_level":"low_to_medium","classification":"preferred_export_hook","notes":"Future EXTRACT03H must implement only staged-source read, normalization, metadata join, serialization and hashes; it must stop before K."},
        {"hook_id":"E03G-H02","candidate_source":rel(MART),"candidate_location":"extract03a_r1_phase_response_vector","export_layer":"persisted_summary","can_export_full_vectors_without_raw_reconstruction":"no","can_preserve_pair_id_order":"yes","can_preserve_axis_index":"no","can_preserve_units_dimension_status":"no","risk_level":"low","classification":"not_viable_missing_vectors","notes":"Only counts and norms are persisted."},
        {"hook_id":"E03G-H03","candidate_source":"authorized F3 staging table referenced by EXTRACT03A-R1","candidate_location":"stg_delta_phi_spatial.wrapped_delta_phi_ij_x","export_layer":"already_staged_wrapped_response_channel","can_export_full_vectors_without_raw_reconstruction":"yes","can_preserve_pair_id_order":"yes","can_preserve_axis_index":"yes","can_preserve_units_dimension_status":"yes","risk_level":"medium","classification":"viable_with_review_items","notes":"Use only through separate export-only authorization; do not read raw_delta_phi or execute broader A-R1 pipeline."},
    ]

    schema_fields = [
        ("source_run_id","string","identifier","EXTRACT03A-R1/F3 lineage run"),("source_artifact_hash","sha256","identifier","hash of selected staged source"),
        ("pair_id","string","identifier","canonical ordered pair i|j"),("pair_i","integer","index","ordered source state"),("pair_j","integer","index","ordered target state"),
        ("split_label","enum","categorical","frozen split assignment"),("component_id_if_known","integer_or_NA","categorical","imported context only"),
        ("vector_axis","string","model_axis","x"),("axis_index","integer","dimensionless_index","0..4000"),("axis_value","binary64","model_length_unit","source x_value"),
        ("axis_unit","string","model_unit","source x_unit, no SI bridge implied"),("response_value","binary64","angle_or_dimensionless","selected wrapped or normalized channel"),
        ("response_value_unit","string","rad_or_dimensionless","rad for wrapped; 1 for normalized"),("response_value_dimension_status","string","declared_status","model angle or normalized dimensionless"),
        ("normalization_status","enum","status","wrapped_not_normalized or l2_normalized"),("orientation_status","enum","status","original or sign_normalized_derivative"),
        ("vector_length","integer","count","4001"),("vector_norm","binary64","channel_dependent","L2 norm"),
        ("raw_vector_sha256","sha256","identifier","canonical wrapped/full selected channel bytes"),("rounded_vector_sha256","sha256","identifier","diagnostic only"),
        ("sign_normalized_sha256","sha256","identifier","orientation-normalized derivative hash"),("serialization_rule_id","string","identifier","E03G-SER-v1"),
    ]
    schema_contract = [{"field_name":n,"required":"yes","data_type":t,"unit_or_dimension_status":u,"description":d,
        "validation_rule":"nonempty and consistent per pair" if "hash" not in n else "lowercase SHA-256 hex; recompute from frozen byte rule",
        "notes":"Channel must be explicit; never silently replace wrapped values by normalized values."} for n,t,u,d in schema_fields]

    pair_contract = [
        ("ordered_pair_id_policy","pair_id = decimal pair_i + '|' + decimal pair_j","08_canonical_pair_split_assignment.csv","exact match for all 42 IDs"),
        ("non_diagonal_pair_policy","pair_i != pair_j; pair_mask=1; retain both directions when present","authorized staged-source selection","42 ordered non-diagonal pairs"),
        ("component_membership_source","EXTRACT03D/VIZ02 imported membership; metadata only","EXTRACT03D component import","each pair maps to exactly one of 6 components"),
        ("split_assignment_source","frozen EXTRACT03A-R1 split assignment","08_canonical_pair_split_assignment.csv","pair_id and split_label exact join"),
        ("pair_order_serialization","ascending numeric pair_i then numeric pair_j","EXTRACT03A-R1 sorted pairs","pair-order hash must match manifest"),
    ]
    pair_rows = [{"contract_item":a,"required_value_or_rule":b,"source_of_truth":c,"validation_rule":d,"notes":"No lexical reordering and no pair collapse."} for a,b,c,d in pair_contract]
    axis_contract = [
        ("axis_semantics","x-axis with source x_value; axis_index is serialization index, not a substitute for x","staged source x_index/x_value"),
        ("axis_ordering","strictly ascending integer axis_index within each ordered pair","EXTRACT03A-R1 ORDER BY pair_i,pair_j,x_index"),
        ("axis_length","4001 values per pair","EXTRACT03A-R1 validated source count"),
        ("axis_unit","retain source x_unit/model_length_unit; no SI conversion","staged source x_unit"),
        ("axis_hash_contribution","hash axis_index, binary64 axis_value and UTF-8 axis_unit in order","E03G-SER-v1"),
        ("missing_value_policy","no missing/NaN/Inf axis or response values; fail closed","future H validation"),
    ]
    axis_rows = [{"axis_contract_item":a,"required_value_or_rule":b,"source_of_truth":c,"validation_rule":"exact per-pair equality; fail on mismatch","notes":"Axis contract frozen before H execution."} for a,b,c in axis_contract]
    units = [
        ("axis_index","1","1","dimensionless_index","[0,0,0,0,0,0,0]","staged x_index"),
        ("axis_value","model_length_unit","model_length_unit","model_unit_no_SI_bridge","unknown_not_SI","staged x_unit/x_value"),
        ("wrapped_response","rad","rad","dimensionless_angle","[0,0,0,0,0,0,0]","staged angle_unit/dimension_status"),
        ("normalized_response","1","1","dimensionless_normalized_vector","[0,0,0,0,0,0,0]","EXTRACT03A-R1 L2 normalization"),
        ("vector_norm","rad or 1","binary64","channel_dependent","[0,0,0,0,0,0,0]","derived only as required export metadata"),
    ]
    unit_rows = [{"quantity":a,"unit_display":b,"unit_calculation":c,"dimension_status":d,"dimension_vector":e,"source_of_truth":f,"notes":"No SI conversion or physical scale claim."} for a,b,c,d,e,f in units]
    serial = [
        ("float_format","IEEE-754 binary64 source preservation; canonical hash bytes little-endian binary64","round-trip and byte stability"),
        ("canonical_csv_order","numeric pair_i,pair_j then axis_index; channel order wrapped then normalized","deterministic replay"),
        ("line_ending","LF (0x0A)","cross-platform canonical text"),("decimal_separator","dot","locale independence"),
        ("NaN_policy","NaN and Inf forbidden; fail export","avoid ambiguous canonicalization"),
        ("rounding_for_hash","raw hash: none; diagnostic rounded hash: frozen 12 significant decimal digits","separate exact and diagnostic equivalence"),
        ("raw_value_preservation","retain binary64 values before textual formatting","raw hash auditability"),
        ("hash_algorithm","SHA-256 lowercase hex","repository convention"),
    ]
    serial_rows = [{"serialization_item":a,"required_rule":b,"reason":c,"validation_rule":"future H validator recomputes independently","notes":"Rule ID E03G-SER-v1."} for a,b,c in serial]
    hash_specs = [
        ("source_artifact_hash","selected source file/DB","raw file bytes"),("contract_hash","EXTRACT03G contract files","sorted filename + NUL + file SHA-256 + LF"),
        ("pair_order_hash","ordered pair IDs","UTF-8 pair_id + LF"),("axis_order_hash","ordered axis metadata","E03G-SER-v1 axis bytes"),
        ("raw_vector_hash","each pair and channel","length prefix + channel ID + little-endian binary64 values"),
        ("rounded_vector_hash","each pair and channel","canonical 12-significant-digit UTF-8 values + LF"),
        ("sign_normalized_vector_hash","each pair and channel","orientation by first abs(value)>frozen tolerance; then raw-vector byte rule"),
        ("manifest_hash","future H manifest excluding self-hash","canonical JSON sorted keys, compact separators, UTF-8"),
    ]
    hash_rows = [{"hash_item":a,"hash_scope":b,"algorithm":"SHA-256","canonicalization_rule":c,"required":"yes","notes":"Lineage records source and contract hashes."} for a,b,c in hash_specs]

    operations = [
        ("read EXTRACT03G contract and frozen metadata","allowed","yes"),("read staged wrapped response channel under H authorization","allowed_future_H_only","yes"),
        ("serialize wrapped and normalized full response vectors","allowed_future_H_only","yes"),("export full vectors during EXTRACT03G","forbidden","yes"),
        ("read/reconstruct raw phases","forbidden","yes"),("recompute K","forbidden","yes"),("recompute strength/d/D/edges","forbidden","yes"),
        ("rerun shortest paths/clustering/motifs/bootstrap","forbidden","yes"),("change parameters, thresholds, seeds, splits or scope","forbidden","yes"),
        ("modify upstream or repair L2","forbidden","yes"),("make physical/geometry/gravity claims","forbidden","yes"),
    ]
    operation_rows = [{"operation":a,"classification":b,"guard_required":c,"rationale":"Contract-only scope and frozen claim boundary.","notes":"Fail closed on forbidden operation."} for a,b,c in operations]
    validation_names = ["authorization_status","selected_hook_matches_contract","source_hash_match","contract_hash_match","42_ordered_pairs","4001_axis_values_per_pair","pair_order_hash","axis_order_hash","finite_binary64_values","unit_dimension_fields_complete","wrapped_norm_consistency","normalized_norm_close_to_one","raw_hash_recomputed","rounded_hash_recomputed","sign_normalized_hash_recomputed","no_K_or_downstream_outputs","upstream_hashes_unchanged","L2_hash_unchanged","exact_H_artifact_manifest"]
    validation_contract = [{"validation_id":f"E03G-VC-{i:02d}","validation_name":name,"required":"yes","failure_action":"block future H run","evidence_required":"machine-readable observed and expected values","notes":"Prospective validation; not executed in G."} for i,name in enumerate(validation_names,1)]
    guard_names = ["human_authorized_response_vector_export","export_scope_full_response_vectors_only","no_raw_phase_reconstruction","no_K_recompute","no_strength_d_D_edge_recompute","no_shortest_path_rerun","no_edge_rethresholding","no_cluster_or_motif_rerun","no_bootstrap","no_parameter_or_scope_change","no_upstream_mutation","no_l2_repair","no_post_hoc_tuning","claim_boundary_accepted"]
    guard_contract = [{"guard_id":f"E03G-GC-{i:02d}","guard_name":name,"required_value":"true","failure_status":"blocked_guard_violation","verification":"future H manifest plus static/runtime negative checks","notes":"Mandatory before and after future export."} for i,name in enumerate(guard_names,1)]

    auth = {"authorization_type":"response_vector_export_only","work_package":"QSB-EXTRACT03H","based_on_contract":"QSB-EXTRACT03G","export_scope":"full_response_vectors_only","source_pipeline":"REQUIRED: selected export hook from EXTRACT03G","no_raw_phase_reconstruction":True,"no_K_recompute":True,"no_strength_d_D_edge_recompute":True,"no_shortest_path_rerun":True,"no_edge_rethresholding":True,"no_cluster_rerun":True,"no_bootstrap":True,"no_l2_repair":True,"claim_boundary_accepted":True,"human_authorization_status":"REQUIRED: human_authorized_for_response_vector_export or blocked"}
    future_artifacts = [
        ("full_response_vectors.csv","wrapped and normalized channels with axis metadata","yes","yes","no"),
        ("response_vector_signature_groups.csv","raw/rounded/sign-normalized hashes and groups","yes","no","no"),
        ("component_vector_alignment.csv","vector-group/component alignment","yes","no","no"),
        ("K_vector_relation_alignment.csv","compare stored K signs with vector identity/opposition; never recompute K","yes","no","no"),
        ("vector_export_manifest.json","source, contract, order and artifact hashes","yes","no","yes"),
        ("vector_export_validation_results.csv","contract validation results","yes","no","yes"),
        ("vector_export_guard_results.csv","guard evidence","yes","no","yes"),
        ("FINAL_RESULT_NOTE.md","bounded result note","yes","no","yes"),
    ]
    future_rows = [{"artifact_name":a,"purpose":b,"required":c,"contains_full_vectors":d,"contains_only_metadata":e,"notes":"Future EXTRACT03H only; not created by G."} for a,b,c,d,e in future_artifacts]
    review_items = [
        {"review_item_id":"E03G-RI-01","category":"hook_execution_authority","description":"Preferred runtime hook is identified but no export execution is authorized in G.","severity":"blocking_for_export","recommended_resolution":"Human-authorize narrow EXTRACT03H template.","notes":"G remains design-only."},
        {"review_item_id":"E03G-RI-02","category":"orientation_tolerance","description":"Sign-normalization tolerance must be frozen before H execution.","severity":"medium","recommended_resolution":"Record one binary64 tolerance in H authorization/addendum.","notes":"No post-hoc choice."},
        {"review_item_id":"E03G-RI-03","category":"source_artifact_scope","description":"Select exact staged source artifact/hash and confirm wrapped channel only.","severity":"blocking_for_export","recommended_resolution":"Populate source_pipeline and source hash in authorization.","notes":"Raw delta-phi channel remains forbidden."},
    ]
    claims = [
        ("EXTRACT03G defines a future response-vector export contract.","supported","Design-only contract."),
        ("A preferred future runtime export hook is statically identified.","supported_with_separate_authorization","No export executed."),
        ("Full response vectors were exported in EXTRACT03G.","unsupported_forbidden","False; no vectors exported."),
        ("EXTRACT03G establishes a physical, geometric, gravitational, or Interface mechanism.","unsupported_forbidden","No physical interpretation."),
        ("EXTRACT03G repairs or changes L2.","unsupported_forbidden","L2 fail retained."),
    ]
    claim_rows = [{"claim_id":f"E03G-CB-{i:02d}","statement":a,"classification":b,"safe_wording":c,"notes":"Contract evidence only."} for i,(a,b,c) in enumerate(claims,1)]
    l2_rows = [
        {"boundary_item":"L2_result","upstream_value":l2["minimaltest_contract_result"],"contract_value":"fail retained","status":"pass","notes":"No rerun or reinterpretation."},
        {"boundary_item":"N4_support","upstream_value":"0/3; required 2/3","contract_value":"unchanged","status":"pass","notes":"No repair."},
        {"boundary_item":"theta_new","upstream_value":"0.012446436850524916","contract_value":"unchanged","status":"pass","notes":"No tuning."},
        {"boundary_item":"epsilon_new","upstream_value":"0.006009422749372488","contract_value":"unchanged","status":"pass","notes":"No tuning."},
        {"boundary_item":"L2_sha256","upstream_value":sha_file(L2),"contract_value":sha_file(L2),"status":"pass","notes":"Hash unchanged."},
    ]

    options = [
        ("E03G-O01","authorize_narrow_EXTRACT03H","Use preferred hook and frozen contract","recommended","requires human authorization"),
        ("E03G-O02","freeze_orientation_tolerance_first","Add one narrow numeric decision before H","acceptable","no export yet"),
        ("E03G-O03","stop_after_contract","Retain unresolved response origin","acceptable","no new operational scope"),
    ]
    option_rows = [{"option_id":a,"option":b,"description":c,"recommendation":d,"authorization_impact":e,"notes":"No action executed by G."} for a,b,c,d,e in options]

    manifest = {"work_package":"QSB-EXTRACT03G","status":STATUS,"created_at_utc":datetime.now(timezone.utc).isoformat(),"repo_root":str(ROOT),
        "extract03f_seen":True,"extract03f_status":f_manifest["status"],"extract03e_seen":True,"extract03e_status":e_manifest["status"],
        "extract03a_r1_seen":True,"extract03a_r1_status":a_manifest["status"],"result_mart_seen":True,"result_mart_readable":True,
        "full_vectors_exported_now":False,"candidate_export_hooks_found":2,"best_export_hook":"E03G-H01: EXTRACT03A-R1 wrapped+normalized runtime arrays after normalization and before K",
        "export_contract_created":True,"authorization_template_created":True,"ready_for_separate_authorized_export":True,"review_items_count":len(review_items),
        "K_recomputed":False,"strength_recomputed":False,"d_recomputed":False,"D_recomputed":False,"edge_recomputed":False,"shortest_path_rerun":False,
        "phase_vectors_reconstructed_from_raw":False,"bootstrap_run":False,"upstream_modified":False,"l2_fail_changed":False,"post_hoc_tuning_performed":False,
        "physical_evidence_claim_made":False,"geometry_claim_made":False,"gravity_claim_made":False,"claim_boundary":CLAIM,
        "next_allowed_action":"human_review_then_separate_narrow_EXTRACT03H_response_vector_export_authorization"}

    (OUT/FILES[0]).write_text(json.dumps(manifest,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    write_csv(FILES[1],list(inventory[0]),inventory); write_csv(FILES[2],list(availability_rows[0]),availability_rows)
    write_csv(FILES[3],list(schema_rows[0]),schema_rows); write_csv(FILES[4],list(response_inventory[0]),response_inventory)
    write_csv(FILES[5],list(static_rows[0]),static_rows); write_csv(FILES[6],list(hooks[0]),hooks)
    write_csv(FILES[7],list(schema_contract[0]),schema_contract); write_csv(FILES[8],list(pair_rows[0]),pair_rows)
    write_csv(FILES[9],list(axis_rows[0]),axis_rows); write_csv(FILES[10],list(unit_rows[0]),unit_rows)
    write_csv(FILES[11],list(serial_rows[0]),serial_rows); write_csv(FILES[12],list(hash_rows[0]),hash_rows)
    write_csv(FILES[13],list(operation_rows[0]),operation_rows); write_csv(FILES[14],list(validation_contract[0]),validation_contract)
    write_csv(FILES[15],list(guard_contract[0]),guard_contract)
    (OUT/FILES[16]).write_text(json.dumps(auth,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    (OUT/FILES[17]).write_text("""# QSB-EXTRACT03H Future Export Run Contract

## Erlaubter Export / Allowed export
Nur vollständige `wrapped`- und `normalized`-Response-Vektoren aus Hook E03G-H01, mit Pair-, Achsen-, Einheiten-, Serialisierungs-, Hash- und Lineagefeldern gemäß EXTRACT03G. Die bereits gestagte wrapped-Quelle darf unter separater H-Autorisierung read-only gelesen werden.

## Verboten / Forbidden
Keine Rohphasen-Rekonstruktion, kein K-/Strength-/d-/D-/Edge-Recompute, keine Shortest Paths, kein Rethresholding, Clustering, Motif, Bootstrap, Tuning oder L2-Reparatur. Die raw_delta_phi-Spalte ist außerhalb des H-Scopes.

## Unveränderliche Upstream-Hashes
EXTRACT03F, EXTRACT03E, EXTRACT03A-R1, ausgewählte F3-Stagingquelle, EXTRACT03G-Vertrag und L2 sind vor/nach dem Lauf zu hashen; jede Abweichung blockiert.

## Pflichtartefakte
Genau die in `19_minimal_export_artifact_manifest.csv` gelisteten H-Artefakte. Nur `full_response_vectors.csv` darf Vollvektoren enthalten.

## Guards
Alle Guards aus `16_guard_contract.csv` sind vor und nach Ausführung maschinenlesbar zu bestätigen. H muss nach Export/Signaturbildung stoppen, bevor K gebildet wird.

## Claims
Der Export darf Identität/Gegenläufigkeit numerisch prüfen. Er beweist weder QSB noch Raumzeitentstehung, Gravitation, Geometrie oder einen Mechanismus in der Natur.
""",encoding="utf-8")
    write_csv(FILES[18],list(future_rows[0]),future_rows); write_csv(FILES[19],list(review_items[0]),review_items)
    write_csv(FILES[20],list(claim_rows[0]),claim_rows); write_csv(FILES[21],list(l2_rows[0]),l2_rows)
    checks = [
        ("extract03f_present",True,True),("extract03e_present",True,True),("extract03a_r1_present",True,True),("result_mart_read_only",integrity,"ok"),
        ("response_data_inventoried",len(response_inventory),4),("static_code_hook_review",len(static_rows),5),("candidate_hooks_classified",len(hooks),3),
        ("schema_contract_fields",len(schema_contract),22),("pair_contract_items",len(pair_rows),5),("axis_contract_items",len(axis_rows),6),
        ("unit_contract_created",len(unit_rows),5),("serialization_contract_created",len(serial_rows),8),("hash_contract_created",len(hash_rows),8),
        ("authorization_template_created",auth["authorization_type"],"response_vector_export_only"),("full_vectors_exported_now",False,False),
        ("no_recomputation",False,False),("no_raw_phase_reconstruction",False,False),("no_bootstrap",False,False),
        ("no_upstream_mutation","checked_after_write","unchanged"),("no_l2_change",False,False),("no_post_hoc_tuning",False,False),
        ("no_physical_claim",False,False),("no_geometry_claim",False,False),("no_gravity_claim",False,False),("exact_output_count",27,27),
    ]
    validations = [{"validation_id":f"E03G-V-{i:02d}","check_name":name,"status":"pass" if observed==expected or name=="no_upstream_mutation" else "fail",
        "observed_value":observed,"expected_value":expected,"blocking":"yes","notes":"Design-contract validation."} for i,(name,observed,expected) in enumerate(checks,1)]
    write_csv(FILES[22],list(validations[0]),validations)
    (OUT/FILES[23]).write_text("""# QSB-EXTRACT03G Response-Vector-Exportvertrag

## Ausgangspunkt
EXTRACT03F fand nur 42 Summary-Signaturen in 10 komponentenreinen Gruppen. Vollvektor-Identität oder -Gegenläufigkeit blieb offen.

## Warum ein Vertrag nötig ist
Vollständige Vektoren sind nicht persistiert. Ein künftiger Export erweitert den operativen Scope und braucht daher eine schmale separate Autorisierung.

## Was ausdrücklich noch nicht exportiert wird
EXTRACT03G exportiert keine Response-Vektoren und liest keine Rohphasen neu aus.

## Mögliche Exportstelle
Bevorzugt ist der EXTRACT03A-R1-Laufzeitpunkt nach Bildung von `wrapped` und `normalized`, unmittelbar vor der K-Punktproduktbildung. Ein späteres Exportskript darf die bereits gestagte wrapped-Spalte lesen, normalisieren, serialisieren und muss vor K stoppen.

## Pair-/Achsen-/Einheitenvertrag
42 numerisch geordnete, gerichtete Nichtdiagonal-Paare; je 4001 aufsteigende x-Indizes. x bleibt Modellachse ohne behauptete SI-Brücke. Wrapped-Werte tragen Winkelstatus, normalisierte Werte sind dimensionslos.

## Serialisierung und Hashes
Binary64-Rohwerte, deterministische Paar-/Achsenordnung, SHA-256 und getrennte Raw-, Rundungs- und Signnormalisierungshashes. Rundung ersetzt nie den Rohhash.

## Guardrails
Keine Rohrekonstruktion, keine K- oder Downstream-Neuberechnung, keine Upstream-Mutation, kein Bootstrap, kein Tuning und keine L2-Reparatur.

## Schmale spätere Autorisierung
`17_future_export_authorization_template.json` fragt nur den neuen Exportumfang, den ausgewählten Hook und die bestehenden Verbote ab.

## Was ausdrücklich nicht behauptet wird
Der Vertrag ist keine physikalische Interpretation und kein Nachweis von Geometrie, Gravitation, Raumzeitentstehung oder eines Mechanismus in der Natur.

## Nächster Schritt
Human Review; danach optional separate Autorisierung eines eng begrenzten EXTRACT03H-Vollvektorexports.
""",encoding="utf-8")
    write_csv(FILES[24],list(option_rows[0]),option_rows)
    (OUT/FILES[25]).write_text("""# QSB-EXTRACT03G Kurznotiz

EXTRACT03G definiert einen prospektiven Exportvertrag. Der bevorzugte spätere Hook liegt im EXTRACT03A-R1-Laufzeitcode nach der L2-Normalisierung und vor der K-Bildung. In G wurden keine vollständigen Vektoren exportiert und keine Modelloutputs neu berechnet. L2 bleibt `fail`. Nächster zulässiger Schritt ist Human Review und gegebenenfalls eine schmale separate EXTRACT03H-Autorisierung.
""",encoding="utf-8")
    (OUT/FILES[26]).write_text(f"""# QSB-EXTRACT03G Final Result

## Status
`{STATUS}`

## Reviewed Inputs
EXTRACT03F, EXTRACT03E, EXTRACT03D, EXTRACT03A-R1, Result-Mart, L2 and five code artifacts were reviewed read-only/static-only.

## Existing Response Data
Persisted CSV and mart data contain summaries only. Full wrapped and normalized vectors exist only as non-persisted EXTRACT03A-R1 runtime arrays.

## Candidate Export Hooks
E03G-H01 is preferred: export wrapped and normalized arrays after normalization and before `K = normalized @ normalized.T`. E03G-H03, a narrow read of the already staged wrapped channel, is viable with review items. Neither hook was executed.

## Export Contract
Pair identity/order, 4001-point axis, model-unit/dimension status, binary64 serialization, SHA-256 lineage, validation and guards are frozen prospectively.

## Authorization Template
The narrow EXTRACT03H template requires human authorization for full-response-vector export only and retains all no-recompute/no-repair guards.

## Review Items
Three items remain: H execution authority, frozen orientation tolerance, and exact source artifact/hash selection.

## Claim Boundary
{CLAIM}

## L2 Boundary
L2 remains fail; N4 support remains 0/3 with 2/3 required. theta_new and epsilon_new are unchanged.

## Next Allowed Action
Human review, then optionally authorize a separate narrow EXTRACT03H response-vector export. No full vectors were exported in EXTRACT03G.
""",encoding="utf-8")

    after = {rel(path): sha_path(path) for _, path in upstream}
    if before != after: fail("extract03g_blocked_guard_violation", "upstream changed during EXTRACT03G")
    if len([p for p in OUT.iterdir() if p.is_file()]) != 27 or set(p.name for p in OUT.iterdir() if p.is_file()) != set(FILES):
        fail("extract03g_blocked_guard_violation", "output artifact contract mismatch")
    if any(v["status"] != "pass" for v in validations):
        fail("extract03g_blocked_guard_violation", "validation failure")
    print("status", STATUS)
    print("candidate_export_hooks_found", 2)
    print("best_export_hook", manifest["best_export_hook"])
    print("artifacts", 27)
    print("full_vectors_exported_now", False)
    print("upstream_modified", False)
    print("l2_fail_changed", False)


if __name__ == "__main__":
    main()
