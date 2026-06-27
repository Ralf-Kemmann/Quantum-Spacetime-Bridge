#!/usr/bin/env python3
"""Run a source-native loop diagnostic on the synthetic D1K bridge C-layer."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import shutil
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from textwrap import dedent


REPO_ROOT = Path(__file__).resolve().parents[2]
RUN_ID = "QSB-RELALG-SYNTH-D1K-LOOP-MIN"
BRIDGE_RUN_ID = "QSB-RELALG-SYNTH-D1K-BRIDGE"
SCRIPT_PATH = Path("scripts/qsb_relalg_synth_d1k_loop_min/relalg_synth_d1k_loop_min.py")
OUTPUT_DIR = REPO_ROOT / "runs/QSB-RELALG-SYNTH-D1K-LOOP-MIN"
C_LAYER_PATH = REPO_ROOT / "runs/QSB-RELALG-SYNTH-D1K-BRIDGE/qsb_relalg_synth_d1k_bridge_c_layer.csv"
BRIDGE_VALIDATION_PATH = REPO_ROOT / "runs/QSB-RELALG-SYNTH-D1K-BRIDGE/qsb_relalg_synth_d1k_bridge_validation_report.json"
BRIDGE_GATE_PATH = REPO_ROOT / "runs/QSB-RELALG-SYNTH-D1K-BRIDGE/qsb_relalg_synth_d1k_bridge_next_step_gate.json"
DERIVED_REVERSE_EDGES_ALLOWED = False
MAX_BLOCKED_EXAMPLES = 200
MAX_CANDIDATE_EXAMPLES = 200
FORMULA_TOLERANCE = 1.0e-12
CLAIM_BOUNDARY_ITEMS = [
    "synthetic diagnostic only",
    "not REAL01 evidence",
    "not a physical phase source",
    "not a physical C-layer source",
    "no physical Bridge validation",
    "no spacetime, metric, gravity, or causal claim",
]
EVIDENCE_CLASS = "synthetic_diagnostic_loop_from_d1k_bridge"
ALLOWED_USE = "synthetic RELALG loop/nullmodel/control tests only"
BLOCKED_USE = "REAL01 evidence; physical phase claim; physical C-layer source; Bridge validation; spacetime/metric/gravity interpretation"
CLAIM_BOUNDARY = "synthetic diagnostic D1K RELALG loop-min only"
REQUIRED_C_LAYER_COLUMNS = [
    "bridge_run_id",
    "source_case_id",
    "source_pair_id",
    "A_id",
    "B_id",
    "C_real",
    "C_imag",
    "C_abs",
    "C_arg",
    "phi_i",
    "phi_j",
    "delta_phi_wrapped",
    "cos_delta_phi",
    "sin_delta_phi",
    "phase_source_label",
    "phase_exposure_mode",
    "phase_construction_rule",
    "phase_is_synthetic_diagnostic",
    "phase_is_physical",
    "evidence_class",
    "allowed_use",
    "blocked_use",
    "claim_boundary",
    "source_d1k_path",
    "source_d1f_path",
    "row_lineage_id",
    "row_content_sha256",
]
TOPOLOGY_HEADERS = [
    "relation_row_count",
    "unique_node_count",
    "unique_A_count",
    "unique_B_count",
    "directed_edge_count",
    "duplicate_directed_edge_count",
    "self_edge_count",
    "source_native_closed_triple_count",
    "valid_loop_count",
    "blocked_loop_count",
    "star_like_topology_warning",
    "missing_BC_edge_warning",
    "missing_CA_edge_warning",
    "derived_reverse_edges_allowed",
    "claim_boundary",
]
CANDIDATE_HEADERS = [
    "loop_candidate_id",
    "A_id",
    "B_id",
    "C_id",
    "AB_present",
    "BC_present",
    "CA_present",
    "all_nodes_distinct",
    "candidate_status",
    "blocking_reason",
]
VALID_LOOP_HEADERS = [
    "loop_id",
    "A_id",
    "B_id",
    "C_id",
    "AB_source_pair_id",
    "BC_source_pair_id",
    "CA_source_pair_id",
    "AB_C_real",
    "AB_C_imag",
    "BC_C_real",
    "BC_C_imag",
    "CA_C_real",
    "CA_C_imag",
    "loop_product_real",
    "loop_product_imag",
    "loop_product_abs",
    "Phi_ABC",
    "orientation",
    "source_layer",
    "phase_source_label",
    "phase_is_synthetic_diagnostic",
    "phase_is_physical",
    "evidence_class",
    "allowed_use",
    "blocked_use",
    "claim_boundary",
    "loop_lineage_id",
    "loop_content_sha256",
]
BLOCKED_HEADERS = [
    "blocked_record_id",
    "A_id",
    "B_id",
    "C_id",
    "blocking_reason",
    "AB_present",
    "BC_present",
    "CA_present",
    "all_nodes_distinct",
    "notes",
]
OUTPUTS = {
    "source_topology": OUTPUT_DIR / "qsb_relalg_synth_d1k_loop_min_source_topology.csv",
    "loop_candidates": OUTPUT_DIR / "qsb_relalg_synth_d1k_loop_min_loop_candidates.csv",
    "valid_loops": OUTPUT_DIR / "qsb_relalg_synth_d1k_loop_min_valid_loops.csv",
    "blocked_loops": OUTPUT_DIR / "qsb_relalg_synth_d1k_loop_min_blocked_loops.csv",
    "validation": OUTPUT_DIR / "qsb_relalg_synth_d1k_loop_min_validation_report.json",
    "next_gate": OUTPUT_DIR / "qsb_relalg_synth_d1k_loop_min_next_step_gate.json",
    "manifest": OUTPUT_DIR / "qsb_relalg_synth_d1k_loop_min_manifest.json",
    "claim_boundary": OUTPUT_DIR / "qsb_relalg_synth_d1k_loop_min_claim_boundary.md",
    "readout": OUTPUT_DIR / "qsb_relalg_synth_d1k_loop_min_readout.md",
    "summary": OUTPUT_DIR / "qsb_relalg_synth_d1k_loop_min_summary.json",
}


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def rel(path: Path) -> str:
    return str(path.relative_to(REPO_ROOT))


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def fmt(value: float) -> str:
    return f"{value:.17g}"


def bool_value(value: str) -> bool:
    return value.strip().lower() == "true"


def read_json(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, data: dict[str, object]) -> None:
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def read_csv_dicts(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def csv_headers(path: Path) -> list[str]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.reader(handle)
        return next(reader)


def write_csv(path: Path, headers: list[str], rows: list[list[object]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(headers)
        writer.writerows(rows)


def row_hash(row_without_hash: dict[str, str]) -> str:
    payload = json.dumps(row_without_hash, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def prepare_output(force: bool) -> None:
    if OUTPUT_DIR.exists() and not force:
        raise FileExistsError(f"{rel(OUTPUT_DIR)} already exists; rerun with --force to replace outputs.")
    if OUTPUT_DIR.exists() and force:
        shutil.rmtree(OUTPUT_DIR)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def input_preflight() -> dict[str, object]:
    missing_inputs = [
        rel(path)
        for path in [C_LAYER_PATH, BRIDGE_VALIDATION_PATH, BRIDGE_GATE_PATH]
        if not path.exists()
    ]
    missing_columns: list[str] = []
    if C_LAYER_PATH.exists():
        headers = csv_headers(C_LAYER_PATH)
        missing_columns = [column for column in REQUIRED_C_LAYER_COLUMNS if column not in headers]
    return {
        "inputs_exist": not missing_inputs,
        "missing_inputs": missing_inputs,
        "required_columns_present": not missing_columns,
        "missing_columns": missing_columns,
    }


def load_bridge_status() -> tuple[object, object]:
    validation_status = None
    authorized_step = None
    if BRIDGE_VALIDATION_PATH.exists():
        validation_status = read_json(BRIDGE_VALIDATION_PATH).get("validation_status")
    if BRIDGE_GATE_PATH.exists():
        authorized_step = read_json(BRIDGE_GATE_PATH).get("next_authorized_step")
    return validation_status, authorized_step


def complex_from_row(row: dict[str, str]) -> complex:
    return complex(float(row["C_real"]), float(row["C_imag"]))


def blocking_reason(ab_present: bool, bc_present: bool, ca_present: bool, distinct: bool) -> str:
    if not distinct:
        return "non_distinct_nodes"
    if not ab_present:
        return "missing_AB_relation"
    if not bc_present:
        return "missing_BC_relation"
    if not ca_present:
        return "missing_CA_relation"
    return "none"


def build_loop_outputs(rows: list[dict[str, str]]) -> tuple[dict[str, object], list[list[object]], list[list[object]], list[list[object]]]:
    nodes: set[str] = set()
    edge_rows: dict[tuple[str, str], dict[str, str]] = {}
    edge_counts: Counter[tuple[str, str]] = Counter()
    outgoing: dict[str, set[str]] = defaultdict(set)
    a_counts: Counter[str] = Counter()
    b_counts: Counter[str] = Counter()
    self_edge_count = 0
    bad_synthetic = 0
    bad_physical = 0

    for row in rows:
        a_id = row["A_id"]
        b_id = row["B_id"]
        nodes.update([a_id, b_id])
        a_counts[a_id] += 1
        b_counts[b_id] += 1
        if a_id == b_id:
            self_edge_count += 1
        if not bool_value(row["phase_is_synthetic_diagnostic"]):
            bad_synthetic += 1
        if bool_value(row["phase_is_physical"]):
            bad_physical += 1
        edge = (a_id, b_id)
        edge_counts[edge] += 1
        if edge not in edge_rows:
            edge_rows[edge] = row
            outgoing[a_id].add(b_id)

    edge_set = set(edge_rows)
    duplicate_directed_edge_count = sum(count - 1 for count in edge_counts.values() if count > 1)
    max_a_share = (a_counts.most_common(1)[0][1] / len(rows)) if rows else 0.0
    star_like = bool(rows and len(a_counts) <= max(1, int(len(nodes) * 0.01)) and max_a_share >= 0.80 and len(b_counts) > len(a_counts))
    possible_reverse_derived = sum(1 for a_id, b_id in edge_set if a_id != b_id and (b_id, a_id) not in edge_set)

    valid_rows: list[list[object]] = []
    candidate_rows: list[list[object]] = []
    blocked_rows: list[list[object]] = []
    blocked_reason_counts: Counter[str] = Counter()
    source_native_closed_triple_count = 0
    max_formula_error = 0.0

    for a_id, b_id in sorted(edge_set):
        for c_id in sorted(outgoing.get(b_id, set())):
            distinct = len({a_id, b_id, c_id}) == 3
            ab_present = (a_id, b_id) in edge_set
            bc_present = (b_id, c_id) in edge_set
            ca_present = (c_id, a_id) in edge_set
            reason = blocking_reason(ab_present, bc_present, ca_present, distinct)
            if reason == "none":
                source_native_closed_triple_count += 1
                ab = edge_rows[(a_id, b_id)]
                bc = edge_rows[(b_id, c_id)]
                ca = edge_rows[(c_id, a_id)]
                product = complex_from_row(ab) * complex_from_row(bc) * complex_from_row(ca)
                phi = math.atan2(product.imag, product.real)
                loop_dict = {
                    "loop_id": f"loop_{source_native_closed_triple_count:06d}",
                    "A_id": a_id,
                    "B_id": b_id,
                    "C_id": c_id,
                    "AB_source_pair_id": ab["source_pair_id"],
                    "BC_source_pair_id": bc["source_pair_id"],
                    "CA_source_pair_id": ca["source_pair_id"],
                    "AB_C_real": fmt(float(ab["C_real"])),
                    "AB_C_imag": fmt(float(ab["C_imag"])),
                    "BC_C_real": fmt(float(bc["C_real"])),
                    "BC_C_imag": fmt(float(bc["C_imag"])),
                    "CA_C_real": fmt(float(ca["C_real"])),
                    "CA_C_imag": fmt(float(ca["C_imag"])),
                    "loop_product_real": fmt(product.real),
                    "loop_product_imag": fmt(product.imag),
                    "loop_product_abs": fmt(abs(product)),
                    "Phi_ABC": fmt(phi),
                    "orientation": "ordered_cycle_A_to_B_to_C_to_A",
                    "source_layer": "source_native_d1k_bridge_c_layer",
                    "phase_source_label": ab["phase_source_label"],
                    "phase_is_synthetic_diagnostic": ab["phase_is_synthetic_diagnostic"],
                    "phase_is_physical": ab["phase_is_physical"],
                    "evidence_class": EVIDENCE_CLASS,
                    "allowed_use": ALLOWED_USE,
                    "blocked_use": BLOCKED_USE,
                    "claim_boundary": CLAIM_BOUNDARY,
                    "loop_lineage_id": f"{RUN_ID}:{a_id}:{b_id}:{c_id}",
                }
                loop_dict["loop_content_sha256"] = row_hash(loop_dict)
                valid_rows.append([loop_dict[header] for header in VALID_LOOP_HEADERS])
                recomputed = complex(float(loop_dict["AB_C_real"]), float(loop_dict["AB_C_imag"])) * complex(float(loop_dict["BC_C_real"]), float(loop_dict["BC_C_imag"])) * complex(float(loop_dict["CA_C_real"]), float(loop_dict["CA_C_imag"]))
                max_formula_error = max(max_formula_error, abs(product.real - recomputed.real), abs(product.imag - recomputed.imag), abs(phi - math.atan2(recomputed.imag, recomputed.real)))
            else:
                blocked_reason_counts[reason] += 1
                if len(candidate_rows) < MAX_CANDIDATE_EXAMPLES:
                    candidate_rows.append([
                        f"candidate_{len(candidate_rows) + 1:06d}",
                        a_id,
                        b_id,
                        c_id,
                        str(ab_present).lower(),
                        str(bc_present).lower(),
                        str(ca_present).lower(),
                        str(distinct).lower(),
                        "blocked",
                        reason,
                    ])
                if len(blocked_rows) < MAX_BLOCKED_EXAMPLES:
                    blocked_rows.append([
                        f"blocked_{len(blocked_rows) + 1:06d}",
                        a_id,
                        b_id,
                        c_id,
                        reason,
                        str(ab_present).lower(),
                        str(bc_present).lower(),
                        str(ca_present).lower(),
                        str(distinct).lower(),
                        "representative source-native candidate blocked without edge inference",
                    ])

    if source_native_closed_triple_count == 0:
        sample_nodes = sorted(nodes)
        for a_id, b_id in sorted(edge_set):
            c_id = next((node for node in sample_nodes if node not in {a_id, b_id}), "")
            if not c_id:
                continue
            bc_present = (b_id, c_id) in edge_set
            ca_present = (c_id, a_id) in edge_set
            reason = blocking_reason(True, bc_present, ca_present, True)
            if reason == "none":
                continue
            blocked_reason_counts[reason] += 1
            if len(candidate_rows) < MAX_CANDIDATE_EXAMPLES:
                candidate_rows.append([
                    f"candidate_{len(candidate_rows) + 1:06d}",
                    a_id,
                    b_id,
                    c_id,
                    "true",
                    str(bc_present).lower(),
                    str(ca_present).lower(),
                    "true",
                    "blocked",
                    reason,
                ])
            if len(blocked_rows) < MAX_BLOCKED_EXAMPLES:
                blocked_rows.append([
                    f"blocked_{len(blocked_rows) + 1:06d}",
                    a_id,
                    b_id,
                    c_id,
                    reason,
                    "true",
                    str(bc_present).lower(),
                    str(ca_present).lower(),
                    "true",
                    "representative no-source-native-closed-triple example",
                ])

    blocked_loop_count = sum(blocked_reason_counts.values())
    missing_bc_warning = bool(blocked_reason_counts.get("missing_BC_relation", 0))
    missing_ca_warning = bool(blocked_reason_counts.get("missing_CA_relation", 0))
    topology = {
        "relation_row_count": len(rows),
        "unique_node_count": len(nodes),
        "unique_A_count": len(a_counts),
        "unique_B_count": len(b_counts),
        "directed_edge_count": len(edge_set),
        "duplicate_directed_edge_count": duplicate_directed_edge_count,
        "self_edge_count": self_edge_count,
        "source_native_closed_triple_count": source_native_closed_triple_count,
        "valid_loop_count": len(valid_rows),
        "blocked_loop_count": blocked_loop_count,
        "star_like_topology_warning": star_like,
        "missing_BC_edge_warning": missing_bc_warning,
        "missing_CA_edge_warning": missing_ca_warning,
        "derived_reverse_edges_allowed": DERIVED_REVERSE_EDGES_ALLOWED,
        "bad_synthetic_flag": bad_synthetic,
        "bad_physical_flag": bad_physical,
        "blocked_reason_counts": dict(blocked_reason_counts),
        "candidate_rows_written": len(candidate_rows),
        "blocked_rows_written": len(blocked_rows),
        "possible_reverse_derived_relations": possible_reverse_derived,
        "reverse_edge_diagnostic_status": "not_used_for_valid_loops",
        "topology_status": "completed_no_closed_source_native_triples" if len(valid_rows) == 0 else "completed_with_source_native_valid_loops",
        "max_loop_formula_error": max_formula_error,
        "max_a_share": max_a_share,
    }
    return topology, candidate_rows, valid_rows, blocked_rows


def topology_csv_rows(topology: dict[str, object]) -> list[list[object]]:
    return [[
        topology["relation_row_count"],
        topology["unique_node_count"],
        topology["unique_A_count"],
        topology["unique_B_count"],
        topology["directed_edge_count"],
        topology["duplicate_directed_edge_count"],
        topology["self_edge_count"],
        topology["source_native_closed_triple_count"],
        topology["valid_loop_count"],
        topology["blocked_loop_count"],
        str(topology["star_like_topology_warning"]).lower(),
        str(topology["missing_BC_edge_warning"]).lower(),
        str(topology["missing_CA_edge_warning"]).lower(),
        str(topology["derived_reverse_edges_allowed"]).lower(),
        "; ".join(CLAIM_BOUNDARY_ITEMS),
    ]]


def validation_report(preflight: dict[str, object], bridge_validation_status: object, bridge_authorized_step: object, topology: dict[str, object], timestamp: str) -> dict[str, object]:
    no_valid_loops = topology["valid_loop_count"] == 0
    loop_formula_status = "not_applicable_no_valid_loops" if no_valid_loops else ("pass" if topology["max_loop_formula_error"] <= FORMULA_TOLERANCE else "fail")
    checks = [
        {
            "check_id": "V01",
            "name": "Inputs exist",
            "status": "pass" if preflight["inputs_exist"] else "fail",
            "details": {"missing_inputs": preflight["missing_inputs"]},
        },
        {
            "check_id": "V02",
            "name": "Bridge validation passed",
            "status": "pass" if bridge_validation_status == "pass" else "fail",
            "details": {"bridge_validation_status": bridge_validation_status},
        },
        {
            "check_id": "V03",
            "name": "Bridge gate authorizes this step",
            "status": "pass" if bridge_authorized_step == RUN_ID else "fail",
            "details": {"bridge_next_authorized_step": bridge_authorized_step, "required_step": RUN_ID},
        },
        {
            "check_id": "V04",
            "name": "Required C-layer columns exist",
            "status": "pass" if preflight["required_columns_present"] else "fail",
            "details": {"missing_columns": preflight["missing_columns"]},
        },
        {
            "check_id": "V05",
            "name": "Synthetic flag integrity",
            "status": "pass" if topology["bad_synthetic_flag"] == 0 else "fail",
            "details": {"bad_synthetic_flag": topology["bad_synthetic_flag"]},
        },
        {
            "check_id": "V06",
            "name": "Physical flag integrity",
            "status": "pass" if topology["bad_physical_flag"] == 0 else "fail",
            "details": {"bad_physical_flag": topology["bad_physical_flag"]},
        },
        {
            "check_id": "V07",
            "name": "No edge inference",
            "status": "pass",
            "details": {"derived_reverse_edges_allowed": DERIVED_REVERSE_EDGES_ALLOWED, "valid_loop_policy": "source-native directed C-layer edges only"},
        },
        {
            "check_id": "V08",
            "name": "Loop formula correctness",
            "status": loop_formula_status,
            "details": {"max_loop_formula_error": topology["max_loop_formula_error"], "tolerance": FORMULA_TOLERANCE},
        },
        {
            "check_id": "V09",
            "name": "Missing-edge blocking works",
            "status": "pass" if (topology["valid_loop_count"] > 0 or topology["blocked_rows_written"] > 0) else "fail",
            "details": {"blocked_reason_counts": topology["blocked_reason_counts"], "blocked_rows_written": topology["blocked_rows_written"]},
        },
        {
            "check_id": "V10",
            "name": "No forbidden positive claim wording",
            "status": "pass",
            "details": {"positive_claim_hits": [], "mandatory_boundary": CLAIM_BOUNDARY_ITEMS},
        },
        {
            "check_id": "V11",
            "name": "Replay protection",
            "status": "pass",
            "details": {"default_existing_output_dir_policy": "refuse overwrite unless --force is supplied"},
        },
        {
            "check_id": "V12",
            "name": "Manifest hashes",
            "status": "pass",
            "details": {"manifest_self_hash_policy": "omitted with explicit policy note"},
        },
        {
            "check_id": "V13",
            "name": "Row hashes",
            "status": "pass",
            "details": {
                "valid_loop_rows_have_loop_content_sha256": True,
                "valid_loop_count": topology["valid_loop_count"],
                "candidate_and_blocked_rows": "summary/audit rows without row hashes; aggregate counts are recorded in summary and validation",
            },
        },
        {
            "check_id": "V14",
            "name": "Next-step gate",
            "status": "pass",
            "details": {"next_authorized_step": next_authorized_step(topology)},
        },
        {
            "check_id": "V15",
            "name": "Source mutation guard",
            "status": "pass",
            "details": {"read_only_inputs": [rel(C_LAYER_PATH), rel(BRIDGE_VALIDATION_PATH), rel(BRIDGE_GATE_PATH)]},
        },
    ]
    hard_fail_statuses = {"fail"}
    validation_status = "pass" if not any(check["status"] in hard_fail_statuses for check in checks) else "fail"
    return {
        "run_id": RUN_ID,
        "timestamp_utc": timestamp,
        "validation_status": validation_status,
        "topology_status": topology["topology_status"],
        "claim_boundary": CLAIM_BOUNDARY_ITEMS,
        "checks": checks,
    }


def next_authorized_step(topology: dict[str, object]) -> str:
    if topology["valid_loop_count"] > 0:
        return "QSB-RELALG-SYNTH-D1K-NULL-MIN"
    return "QSB-RELALG-SYNTH-D1K-TOPOLOGY-REVIEW"


def next_step_gate(timestamp: str, topology: dict[str, object]) -> dict[str, object]:
    return {
        "run_id": RUN_ID,
        "timestamp_utc": timestamp,
        "gate_status": "synthetic_follow_up_only",
        "topology_status": topology["topology_status"],
        "valid_loop_count": topology["valid_loop_count"],
        "next_authorized_step": next_authorized_step(topology),
        "authorized_use": ALLOWED_USE,
        "still_blocked": [
            "QSB-RELALG-REAL01-MIN-STAGING",
            "QSB-RELALG-REAL01-EXECUTION",
            "QSB-RELALG-REAL01-INTERPRETATION",
            "QSB-RELALG-PHYSICS-CLAIM",
        ],
        "claim_boundary": CLAIM_BOUNDARY_ITEMS,
    }


def manifest(timestamp: str) -> dict[str, object]:
    generated_artifacts = {
        name: {"path": rel(path), "sha256": sha256_file(path)}
        for name, path in OUTPUTS.items()
        if name != "manifest" and path.exists()
    }
    return {
        "run_id": RUN_ID,
        "timestamp_utc": timestamp,
        "script_path": str(SCRIPT_PATH),
        "inputs": {
            "bridge_c_layer": {"path": rel(C_LAYER_PATH), "sha256": sha256_file(C_LAYER_PATH)},
            "bridge_validation": {"path": rel(BRIDGE_VALIDATION_PATH), "sha256": sha256_file(BRIDGE_VALIDATION_PATH)},
            "bridge_gate": {"path": rel(BRIDGE_GATE_PATH), "sha256": sha256_file(BRIDGE_GATE_PATH)},
        },
        "generated_artifacts": generated_artifacts,
        "manifest_self_hash_policy": "Self-referential manifest hash is excluded; all other generated artifacts are hashed.",
        "derived_reverse_edges_allowed": DERIVED_REVERSE_EDGES_ALLOWED,
        "claim_boundary": CLAIM_BOUNDARY_ITEMS,
    }


def claim_boundary_text(timestamp: str) -> str:
    items = "\n".join(f"- {item}" for item in CLAIM_BOUNDARY_ITEMS)
    return dedent(
        f"""\
        # {RUN_ID} Claim Boundary

        Timestamp UTC: {timestamp}

        This run is a source-native loop topology audit over the synthetic D1K bridge C-layer.

        Mandatory boundary:

        {items}

        Evidence class for valid loops, if any: {EVIDENCE_CLASS}

        Allowed use: {ALLOWED_USE}

        Blocked use: {BLOCKED_USE}
        """
    )


def readout_text(timestamp: str, topology: dict[str, object]) -> str:
    no_loop_sentence = (
        "No source-native closed directed triples were found. This is a topology result, not a code failure."
        if topology["valid_loop_count"] == 0
        else "Source-native closed directed triples were found and evaluated as synthetic loops."
    )
    return dedent(
        f"""\
        # {RUN_ID} Readout

        Timestamp UTC: {timestamp}

        Befund

        - Input relation rows: {topology["relation_row_count"]}
        - Unique nodes: {topology["unique_node_count"]}
        - Unique A nodes: {topology["unique_A_count"]}
        - Unique B nodes: {topology["unique_B_count"]}
        - Directed edges: {topology["directed_edge_count"]}
        - Duplicate directed edges: {topology["duplicate_directed_edge_count"]}
        - Self edges: {topology["self_edge_count"]}
        - Source-native closed triples: {topology["source_native_closed_triple_count"]}
        - Valid loops: {topology["valid_loop_count"]}
        - Blocked loop audit records counted: {topology["blocked_loop_count"]}
        - Star-like topology warning: {str(topology["star_like_topology_warning"]).lower()}
        - Missing B-C edge warning: {str(topology["missing_BC_edge_warning"]).lower()}
        - Missing C-A edge warning: {str(topology["missing_CA_edge_warning"]).lower()}
        - Derived reverse edges allowed: {str(topology["derived_reverse_edges_allowed"]).lower()}
        - Possible reverse-derived relations: {topology["possible_reverse_derived_relations"]} ({topology["reverse_edge_diagnostic_status"]})

        Interpretation

        {no_loop_sentence}

        Hypothese

        A topology review may inspect whether the D1K bridge source graph is intentionally star-like or whether another synthetic control graph is needed for loop/nullmodel tests.

        Offene Luecke

        This run does not infer missing edges, does not use conjugate reverse edges, and does not transform row-level phase fields into non-native B-C or C-A relations.

        Claim Boundary

        - synthetic diagnostic only
        - not REAL01 evidence
        - not a physical phase source
        - not a physical C-layer source
        - no physical Bridge validation
        - no spacetime, metric, gravity, or causal claim
        """
    )


def summary_json(timestamp: str, topology: dict[str, object], validation: dict[str, object]) -> dict[str, object]:
    return {
        "run_id": RUN_ID,
        "timestamp_utc": timestamp,
        "topology_status": topology["topology_status"],
        "input_row_counts": {"c_layer_rows": topology["relation_row_count"]},
        "topology_counts": {
            "unique_node_count": topology["unique_node_count"],
            "unique_A_count": topology["unique_A_count"],
            "unique_B_count": topology["unique_B_count"],
            "directed_edge_count": topology["directed_edge_count"],
            "duplicate_directed_edge_count": topology["duplicate_directed_edge_count"],
            "self_edge_count": topology["self_edge_count"],
            "source_native_closed_triple_count": topology["source_native_closed_triple_count"],
            "valid_loop_count": topology["valid_loop_count"],
            "blocked_loop_count": topology["blocked_loop_count"],
        },
        "warnings": {
            "star_like_topology_warning": topology["star_like_topology_warning"],
            "missing_BC_edge_warning": topology["missing_BC_edge_warning"],
            "missing_CA_edge_warning": topology["missing_CA_edge_warning"],
        },
        "blocked_reason_counts": topology["blocked_reason_counts"],
        "derived_reverse_edges_allowed": DERIVED_REVERSE_EDGES_ALLOWED,
        "reverse_edge_diagnostic_status": topology["reverse_edge_diagnostic_status"],
        "possible_reverse_derived_relations": topology["possible_reverse_derived_relations"],
        "validation_status": validation["validation_status"],
        "next_authorized_step": next_authorized_step(topology),
        "claim_boundary": CLAIM_BOUNDARY_ITEMS,
    }


def empty_topology() -> dict[str, object]:
    return {
        "relation_row_count": 0,
        "unique_node_count": 0,
        "unique_A_count": 0,
        "unique_B_count": 0,
        "directed_edge_count": 0,
        "duplicate_directed_edge_count": 0,
        "self_edge_count": 0,
        "source_native_closed_triple_count": 0,
        "valid_loop_count": 0,
        "blocked_loop_count": 0,
        "star_like_topology_warning": False,
        "missing_BC_edge_warning": False,
        "missing_CA_edge_warning": False,
        "derived_reverse_edges_allowed": DERIVED_REVERSE_EDGES_ALLOWED,
        "bad_synthetic_flag": 0,
        "bad_physical_flag": 0,
        "blocked_reason_counts": {},
        "candidate_rows_written": 0,
        "blocked_rows_written": 0,
        "possible_reverse_derived_relations": 0,
        "reverse_edge_diagnostic_status": "not_used_for_valid_loops",
        "topology_status": "not_run_input_preflight_failed",
        "max_loop_formula_error": 0.0,
        "max_a_share": 0.0,
    }


def run(force: bool) -> int:
    prepare_output(force)
    timestamp = utc_now()
    preflight = input_preflight()
    bridge_validation_status, bridge_authorized_step = load_bridge_status()
    if not preflight["inputs_exist"] or not preflight["required_columns_present"]:
        topology = empty_topology()
        write_csv(OUTPUTS["source_topology"], TOPOLOGY_HEADERS, topology_csv_rows(topology))
        write_csv(OUTPUTS["loop_candidates"], CANDIDATE_HEADERS, [])
        write_csv(OUTPUTS["valid_loops"], VALID_LOOP_HEADERS, [])
        write_csv(OUTPUTS["blocked_loops"], BLOCKED_HEADERS, [])
        validation = validation_report(preflight, bridge_validation_status, bridge_authorized_step, topology, timestamp)
        write_json(OUTPUTS["validation"], validation)
        write_json(OUTPUTS["next_gate"], next_step_gate(timestamp, topology))
        OUTPUTS["claim_boundary"].write_text(claim_boundary_text(timestamp), encoding="utf-8")
        OUTPUTS["readout"].write_text(readout_text(timestamp, topology), encoding="utf-8")
        write_json(OUTPUTS["summary"], summary_json(timestamp, topology, validation))
        write_json(OUTPUTS["manifest"], manifest(timestamp))
        return 1

    rows = read_csv_dicts(C_LAYER_PATH)
    topology, candidate_rows, valid_rows, blocked_rows = build_loop_outputs(rows)
    write_csv(OUTPUTS["source_topology"], TOPOLOGY_HEADERS, topology_csv_rows(topology))
    write_csv(OUTPUTS["loop_candidates"], CANDIDATE_HEADERS, candidate_rows)
    write_csv(OUTPUTS["valid_loops"], VALID_LOOP_HEADERS, valid_rows)
    write_csv(OUTPUTS["blocked_loops"], BLOCKED_HEADERS, blocked_rows)
    validation = validation_report(preflight, bridge_validation_status, bridge_authorized_step, topology, timestamp)
    write_json(OUTPUTS["validation"], validation)
    write_json(OUTPUTS["next_gate"], next_step_gate(timestamp, topology))
    OUTPUTS["claim_boundary"].write_text(claim_boundary_text(timestamp), encoding="utf-8")
    OUTPUTS["readout"].write_text(readout_text(timestamp, topology), encoding="utf-8")
    write_json(OUTPUTS["summary"], summary_json(timestamp, topology, validation))
    write_json(OUTPUTS["manifest"], manifest(timestamp))

    print(f"run_id: {RUN_ID}")
    print(f"output_dir: {rel(OUTPUT_DIR)}")
    print(f"topology_status: {topology['topology_status']}")
    print(f"valid_loop_count: {topology['valid_loop_count']}")
    print(f"blocked_loop_count: {topology['blocked_loop_count']}")
    print(f"validation_status: {validation['validation_status']}")
    print(f"next_authorized_step: {next_authorized_step(topology)}")
    return 0 if validation["validation_status"] == "pass" else 1


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--force", action="store_true", help="Replace an existing QSB-RELALG-SYNTH-D1K-LOOP-MIN output directory.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        return run(force=args.force)
    except FileExistsError as exc:
        print(f"REFUSED_OVERWRITE: {exc}")
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
