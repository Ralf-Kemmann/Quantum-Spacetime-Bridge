#!/usr/bin/env python3
"""Condense the synthetic D1K RELALG source-topology limit note."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import shutil
from datetime import datetime, timezone
from pathlib import Path
from textwrap import dedent


REPO_ROOT = Path(__file__).resolve().parents[2]
RUN_ID = "QSB-RELALG-SYNTH-D1K-SOURCE-TOPOLOGY-LIMIT-NOTE"
SCRIPT_PATH = REPO_ROOT / "scripts/qsb_relalg_synth_d1k_source_topology_limit_note/relalg_synth_d1k_source_topology_limit_note.py"
OUTPUT_DIR = REPO_ROOT / "runs/QSB-RELALG-SYNTH-D1K-SOURCE-TOPOLOGY-LIMIT-NOTE"
MATRIX_DIR = REPO_ROOT / "runs/QSB-RELALG-SYNTH-D1K-MATRIX-TOPOLOGY-MIN"
BRIDGE_DIR = REPO_ROOT / "runs/QSB-RELALG-SYNTH-D1K-BRIDGE"
LOOP_DIR = REPO_ROOT / "runs/QSB-RELALG-SYNTH-D1K-LOOP-MIN"

REQUIRED_INPUTS = {
    "matrix_summary": MATRIX_DIR / "qsb_relalg_synth_d1k_matrix_topology_summary.json",
    "matrix_validation": MATRIX_DIR / "qsb_relalg_synth_d1k_matrix_topology_validation_report.json",
    "matrix_profile": MATRIX_DIR / "qsb_relalg_synth_d1k_matrix_topology_matrix_profile.csv",
    "component_summary": MATRIX_DIR / "qsb_relalg_synth_d1k_matrix_topology_component_summary.csv",
    "matrix_claim_boundary": MATRIX_DIR / "qsb_relalg_synth_d1k_matrix_topology_claim_boundary.md",
}
OPTIONAL_INPUTS = {
    "bridge_summary": BRIDGE_DIR / "qsb_relalg_synth_d1k_bridge_summary.json",
    "bridge_validation": BRIDGE_DIR / "qsb_relalg_synth_d1k_bridge_validation_report.json",
    "loop_summary": LOOP_DIR / "qsb_relalg_synth_d1k_loop_min_summary.json",
    "loop_validation": LOOP_DIR / "qsb_relalg_synth_d1k_loop_min_validation_report.json",
}
OUTPUTS = {
    "note": OUTPUT_DIR / "qsb_relalg_synth_d1k_source_topology_limit_note.md",
    "evidence_table": OUTPUT_DIR / "qsb_relalg_synth_d1k_source_topology_limit_evidence_table.csv",
    "claim_boundary": OUTPUT_DIR / "qsb_relalg_synth_d1k_source_topology_limit_claim_boundary.md",
    "validation": OUTPUT_DIR / "qsb_relalg_synth_d1k_source_topology_limit_validation_report.json",
    "next_gate": OUTPUT_DIR / "qsb_relalg_synth_d1k_source_topology_limit_next_step_gate.json",
    "manifest": OUTPUT_DIR / "qsb_relalg_synth_d1k_source_topology_limit_manifest.json",
    "summary": OUTPUT_DIR / "qsb_relalg_synth_d1k_source_topology_limit_summary.json",
    "mermaid": OUTPUT_DIR / "qsb_relalg_synth_d1k_source_topology_limit_mermaid.md",
}
CLAIM_BOUNDARY = [
    "synthetic diagnostic source-topology limit note only",
    "not REAL01 evidence",
    "not a physical phase source",
    "not a physical C-layer source",
    "no physical Bridge validation",
    "no spacetime, metric, gravity, or causal claim",
    "no inferred edges",
    "no fabricated loops",
    "no source-native loop phase authorization from D1K",
]
DENSITY_WARNING = (
    "The density value 1.0 is local to the observed A_id x B_id matrix shape of 1 x 9450. "
    "It must not be read as density of the full node-to-node graph over 9451 nodes. "
    "It does not imply missing B->C, C->A, or reverse relations."
)
FORBIDDEN_PHRASES = [
    "REAL01 evidence",
    "physical phase",
    "physical C-layer source",
    "Bridge validation",
    "spacetime metric derivation",
    "gravity proof",
    "causality proof",
    "loop phase authorization from D1K",
]


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def rel(path: Path) -> str:
    return str(path.relative_to(REPO_ROOT))


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_json(path: Path, data: dict[str, object]) -> None:
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def write_csv(path: Path, headers: list[str], rows: list[list[object]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(headers)
        writer.writerows(rows)


def read_json(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


def read_csv_dicts(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def prepare_output(force: bool) -> None:
    if OUTPUT_DIR.exists() and not force:
        raise FileExistsError(f"{rel(OUTPUT_DIR)} already exists; rerun with --force to replace outputs.")
    if OUTPUT_DIR.exists() and force:
        shutil.rmtree(OUTPUT_DIR)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def scalar(value: object) -> str:
    if value is None:
        return "unavailable"
    if isinstance(value, bool):
        return "true" if value else "false"
    return str(value)


def discover_optional_inputs() -> dict[str, Path]:
    used: dict[str, Path] = {}
    for key, path in OPTIONAL_INPUTS.items():
        if path.exists():
            used[key] = path

    fallback_patterns = {
        "bridge_summary": (BRIDGE_DIR, "*summary*.json"),
        "bridge_validation": (BRIDGE_DIR, "*validation*.json"),
        "loop_summary": (LOOP_DIR, "*summary*.json"),
        "loop_validation": (LOOP_DIR, "*validation*.json"),
    }
    for key, (directory, pattern) in fallback_patterns.items():
        if key in used or not directory.exists():
            continue
        matches = sorted(directory.glob(pattern))
        if matches:
            used[key] = matches[0]
    return used


def validation_status(path: Path) -> str:
    data = read_json(path)
    return scalar(data.get("validation_status"))


def no_positive_forbidden_claims(text: str) -> list[str]:
    hits: list[str] = []
    for phrase in FORBIDDEN_PHRASES:
        allowed_forms = [
            f"not {phrase}",
            f"not a {phrase}",
            f"not an {phrase}",
            f"no {phrase}",
            f"no physical {phrase}",
            f"no source-native {phrase}",
        ]
        if phrase in text and not any(form in text for form in allowed_forms):
            hits.append(phrase)
    return sorted(set(hits))


def build_evidence(
    matrix_summary: dict[str, object],
    matrix_profile: dict[str, str],
    component_rows: list[dict[str, str]],
    bridge_summary: dict[str, object] | None,
) -> list[list[object]]:
    counts = matrix_summary.get("edge_node_matrix_counts", {})
    topology = matrix_summary.get("topology", {})
    component_class = "unavailable"
    if component_rows:
        component_class = component_rows[0].get("component_topology_class", "unavailable")
    bridge_flags = bridge_summary.get("flag_counts", {}) if bridge_summary else {}

    bad_synthetic = bridge_flags.get("bad_synthetic_flag") if bridge_summary else None
    bad_physical = bridge_flags.get("bad_physical_flag") if bridge_summary else None
    synthetic_value = "true" if bad_synthetic == 0 else "unavailable"
    physical_value = "false" if bad_physical == 0 else "unavailable"

    rows = [
        ["E01", "QSB-RELALG-SYNTH-D1K-MATRIX-TOPOLOGY-MIN", rel(REQUIRED_INPUTS["matrix_summary"]), "input_rows_or_edges", counts.get("edge_count", matrix_profile.get("edge_count", "unavailable")), "Observed source-native directed C-layer rows.", "yes"],
        ["E02", "QSB-RELALG-SYNTH-D1K-MATRIX-TOPOLOGY-MIN", rel(REQUIRED_INPUTS["matrix_summary"]), "unique_A_id", counts.get("unique_A_count", matrix_profile.get("unique_A_count", "unavailable")), "One observed source-side A_id.", "yes"],
        ["E03", "QSB-RELALG-SYNTH-D1K-MATRIX-TOPOLOGY-MIN", rel(REQUIRED_INPUTS["matrix_summary"]), "unique_B_id", counts.get("unique_B_count", matrix_profile.get("unique_B_count", "unavailable")), "Observed target-side B_id count.", "yes"],
        ["E04", "QSB-RELALG-SYNTH-D1K-MATRIX-TOPOLOGY-MIN", rel(REQUIRED_INPUTS["matrix_summary"]), "matrix_shape", counts.get("matrix_shape", "unavailable"), "Observed A_id x B_id sparse matrix shape.", "yes"],
        ["E05", "QSB-RELALG-SYNTH-D1K-MATRIX-TOPOLOGY-MIN", rel(REQUIRED_INPUTS["matrix_profile"]), "matrix_density", f"{matrix_profile.get('matrix_density', 'unavailable')} within A x B space", "Local occupancy of the observed 1 x 9450 matrix only.", "yes"],
        ["E06", "QSB-RELALG-SYNTH-D1K-MATRIX-TOPOLOGY-MIN", rel(REQUIRED_INPUTS["component_summary"]), "component_topology_class", component_class, "Weak component topology class.", "yes"],
        ["E07", "QSB-RELALG-SYNTH-D1K-MATRIX-TOPOLOGY-MIN", rel(REQUIRED_INPUTS["matrix_summary"]), "star_topology_score", topology.get("star_topology_score", matrix_profile.get("star_topology_score", "unavailable")), "Diagnostic score for one-center outgoing star pattern.", "yes"],
        ["E08", "QSB-RELALG-SYNTH-D1K-MATRIX-TOPOLOGY-MIN", rel(REQUIRED_INPUTS["matrix_summary"]), "source_native_closed_triple_count", topology.get("source_native_closed_triple_count", matrix_profile.get("source_native_closed_triple_count", "unavailable")), "Closed triples count source-native A->B, B->C, C->A rows only.", "yes"],
        ["E09", "QSB-RELALG-SYNTH-D1K-MATRIX-TOPOLOGY-MIN", rel(REQUIRED_INPUTS["matrix_summary"]), "valid_loop_count", topology.get("valid_loop_count_from_topology", matrix_profile.get("valid_loop_count_from_topology", "unavailable")), "Valid source-native loop count from topology.", "yes"],
        ["E10", "QSB-RELALG-SYNTH-D1K-MATRIX-TOPOLOGY-MIN", rel(REQUIRED_INPUTS["matrix_profile"]), "source_native_reverse_edge_count", topology.get("source_native_reverse_edge_count", matrix_profile.get("source_native_reverse_edge_count", "unavailable")), "Reverse edges count only actual source-native reverse rows.", "yes"],
        ["E11", "QSB-RELALG-SYNTH-D1K-MATRIX-TOPOLOGY-MIN", rel(REQUIRED_INPUTS["matrix_profile"]), "missing_BC_relation_count", topology.get("missing_BC_relation_count", matrix_profile.get("missing_BC_relation_count", "unavailable")), "Observed A->B rows whose B node lacks outgoing B->C rows.", "yes"],
        ["E12", "QSB-RELALG-SYNTH-D1K-MATRIX-TOPOLOGY-MIN", rel(REQUIRED_INPUTS["matrix_profile"]), "missing_reverse_relation_count", topology.get("missing_reverse_relation_count", matrix_profile.get("missing_reverse_relation_count", "unavailable")), "Observed rows without actual reverse rows.", "yes"],
        ["E13", "QSB-RELALG-SYNTH-D1K-MATRIX-TOPOLOGY-MIN", rel(REQUIRED_INPUTS["matrix_profile"]), "inferred_edge_count", topology.get("inferred_edge_count", matrix_profile.get("inferred_edge_count", "unavailable")), "No missing cells, reverse edges, or loop edges were inferred.", "yes"],
        ["E14", "QSB-RELALG-SYNTH-D1K-BRIDGE", rel(OPTIONAL_INPUTS["bridge_summary"]) if OPTIONAL_INPUTS["bridge_summary"].exists() else "optional_bridge_summary_absent", "phase_is_synthetic_diagnostic", synthetic_value, "Bridge summary reports zero bad synthetic flags when available.", "yes"],
        ["E15", "QSB-RELALG-SYNTH-D1K-BRIDGE", rel(OPTIONAL_INPUTS["bridge_summary"]) if OPTIONAL_INPUTS["bridge_summary"].exists() else "optional_bridge_summary_absent", "phase_is_physical", physical_value, "Bridge summary reports zero bad physical flags when available.", "yes"],
    ]
    return [[cell if cell is not None else "unavailable" for cell in row] for row in rows]


def build_outputs() -> dict[str, object]:
    missing_required = [rel(path) for path in REQUIRED_INPUTS.values() if not path.exists()]
    if missing_required:
        raise FileNotFoundError("Missing required matrix-topology inputs: " + ", ".join(missing_required))

    matrix_summary = read_json(REQUIRED_INPUTS["matrix_summary"])
    matrix_validation = read_json(REQUIRED_INPUTS["matrix_validation"])
    matrix_profile_rows = read_csv_dicts(REQUIRED_INPUTS["matrix_profile"])
    matrix_profile = {row["metric_name"]: row["metric_value"] for row in matrix_profile_rows}
    component_rows = read_csv_dicts(REQUIRED_INPUTS["component_summary"])
    optional_paths = discover_optional_inputs()
    bridge_summary = read_json(optional_paths["bridge_summary"]) if "bridge_summary" in optional_paths else None
    loop_summary = read_json(optional_paths["loop_summary"]) if "loop_summary" in optional_paths else None

    evidence_rows = build_evidence(matrix_summary, matrix_profile, component_rows, bridge_summary)
    evidence_by_metric = {row[3]: row[4] for row in evidence_rows}
    timestamp = utc_now()
    upstream_files = dict(REQUIRED_INPUTS)
    upstream_files.update(optional_paths)

    note_md = dedent(f"""\
    # {RUN_ID}

    ## Status

    This is a result condensation note for the synthetic D1K RELALG branch. It introduces no new exploratory computation and no new relation construction.

    ## Upstream basis

    - QSB-RELALG-SYNTH-D1K-BRIDGE: synthetic diagnostic C-layer export.
    - QSB-RELALG-SYNTH-D1K-LOOP-MIN: source-native loop-min topology check.
    - QSB-RELALG-SYNTH-D1K-MATRIX-TOPOLOGY-MIN: sparse matrix/topology audit.

    ## What D1K supports

    D1K provides a synthetic diagnostic C-layer over A->B relations. The observed matrix is a fully occupied 1 x 9450 source-target matrix and forms a one-center outgoing star. D1K remains useful for synthetic C-layer export, sparse matrix/topology diagnostics, family/block readouts, and conservative documentation of source-topology limits.

    ## What D1K does not support

    D1K does not support source-native loop phase analysis. It does not provide source-native B->C and C->A relation rows, source-native reverse rows, inferred edges, fabricated loops, REAL01 evidence, or physical interpretation.

    ## Matrix-topology result

    - Input rows / directed edges: {evidence_by_metric.get("input_rows_or_edges", "unavailable")}
    - Unique A_id: {evidence_by_metric.get("unique_A_id", "unavailable")}
    - Unique B_id: {evidence_by_metric.get("unique_B_id", "unavailable")}
    - Matrix shape: {evidence_by_metric.get("matrix_shape", "unavailable")}
    - Component topology class: {evidence_by_metric.get("component_topology_class", "unavailable")}
    - Star topology score: {evidence_by_metric.get("star_topology_score", "unavailable")}
    - Source-native closed triples: {evidence_by_metric.get("source_native_closed_triple_count", "unavailable")}
    - Valid loop count: {evidence_by_metric.get("valid_loop_count", "unavailable")}
    - Inferred edge count: {evidence_by_metric.get("inferred_edge_count", "unavailable")}

    ## Why loop-phase analysis is not authorized from D1K

    A valid source-native directed closed triple requires all three rows A->B, B->C, and C->A. The D1K synthetic C-layer contains observed A->B rows, but the upstream topology reports {evidence_by_metric.get("missing_BC_relation_count", "unavailable")} missing B->C relations and {evidence_by_metric.get("missing_reverse_relation_count", "unavailable")} missing reverse relations. Therefore D1K does not provide a source-native closed-triple topology for loop-phase analysis.

    ## Correct reading of density = 1.0

    {DENSITY_WARNING}

    ## Claim boundary

    - synthetic diagnostic source-topology limit note only
    - not REAL01 evidence
    - not a physical phase source
    - not a physical C-layer source
    - no physical Bridge validation
    - no spacetime, metric, gravity, or causal claim
    - no inferred edges
    - no fabricated loops
    - no source-native loop phase authorization from D1K

    ## Next-step gate

    Authorized bounded follow-up actions are documentation review and metadata synchronization only:

    - QSB-RELALG-SYNTH-D1K-SOURCE-TOPOLOGY-LIMIT-NOTE-REVIEW
    - QSB-META-RELALG-SYNC-D1K-LIMIT-NOTE

    Still blocked:

    - QSB-RELALG-REAL01-MIN-STAGING
    - QSB-RELALG-REAL01-EXECUTION
    - QSB-RELALG-REAL01-INTERPRETATION
    - QSB-RELALG-PHYSICS-CLAIM
    - QSB-RELALG-SYNTH-D1K-LOOP-PHASE-INTERPRETATION
    - QSB-RELALG-SYNTH-D1K-INFERRED-EDGE-CONSTRUCTION
    """)

    claim_boundary_md = dedent(f"""\
    # {RUN_ID} Claim Boundary

    - synthetic diagnostic source-topology limit note only
    - not REAL01 evidence
    - not a physical phase source
    - not a physical C-layer source
    - no physical Bridge validation
    - no spacetime, metric, gravity, or causal claim
    - no inferred edges
    - no fabricated loops
    - no source-native loop phase authorization from D1K
    """)

    next_gate = {
        "run_id": RUN_ID,
        "timestamp_utc": timestamp,
        "authorized_steps": [
            "QSB-RELALG-SYNTH-D1K-SOURCE-TOPOLOGY-LIMIT-NOTE-REVIEW",
            "QSB-META-RELALG-SYNC-D1K-LIMIT-NOTE",
        ],
        "blocked_steps": [
            "QSB-RELALG-REAL01-MIN-STAGING",
            "QSB-RELALG-REAL01-EXECUTION",
            "QSB-RELALG-REAL01-INTERPRETATION",
            "QSB-RELALG-PHYSICS-CLAIM",
            "QSB-RELALG-SYNTH-D1K-LOOP-PHASE-INTERPRETATION",
            "QSB-RELALG-SYNTH-D1K-INFERRED-EDGE-CONSTRUCTION",
        ],
        "gate_basis": "source topology is a synthetic one-center outgoing star with no source-native closed triples",
        "claim_boundary": CLAIM_BOUNDARY,
    }

    mermaid_md = dedent(f"""\
    # {RUN_ID} Aggregate Topology Sketch

    ```mermaid
    flowchart LR
      A["single source A_id"] --> B["9450 target B_id nodes"]
      B -. "B->C absent" .-> X["closed triples: 0"]
      X -. "no authorization" .-> L["loop-phase analysis from D1K blocked"]
    ```

    This sketch is aggregate-only and does not construct missing relations.
    """)

    summary = {
        "run_id": RUN_ID,
        "timestamp_utc": timestamp,
        "upstream_artifacts_used": {key: rel(path) for key, path in upstream_files.items()},
        "evidence_row_count": len(evidence_rows),
        "main_conclusion": "D1K supports synthetic C-layer export and matrix/topology diagnostics, but not source-native loop phase analysis.",
        "density_warning_present": DENSITY_WARNING in note_md,
        "validation_status": "pending",
        "next_step_gate": next_gate["authorized_steps"],
        "claim_boundary": CLAIM_BOUNDARY,
        "key_metrics": {
            "input_rows_or_edges": evidence_by_metric.get("input_rows_or_edges", "unavailable"),
            "unique_A_id": evidence_by_metric.get("unique_A_id", "unavailable"),
            "unique_B_id": evidence_by_metric.get("unique_B_id", "unavailable"),
            "matrix_shape": evidence_by_metric.get("matrix_shape", "unavailable"),
            "component_topology_class": evidence_by_metric.get("component_topology_class", "unavailable"),
            "star_topology_score": evidence_by_metric.get("star_topology_score", "unavailable"),
            "source_native_closed_triple_count": evidence_by_metric.get("source_native_closed_triple_count", "unavailable"),
            "valid_loop_count": evidence_by_metric.get("valid_loop_count", "unavailable"),
            "inferred_edge_count": evidence_by_metric.get("inferred_edge_count", "unavailable"),
        },
    }

    write_csv(
        OUTPUTS["evidence_table"],
        ["evidence_id", "upstream_block", "source_artifact", "metric_name", "metric_value", "interpretation", "supports_limit_note"],
        evidence_rows,
    )
    OUTPUTS["note"].write_text(note_md, encoding="utf-8")
    OUTPUTS["claim_boundary"].write_text(claim_boundary_md, encoding="utf-8")
    OUTPUTS["mermaid"].write_text(mermaid_md, encoding="utf-8")
    write_json(OUTPUTS["next_gate"], next_gate)

    validation_statuses: dict[str, str] = {}
    for key, path in upstream_files.items():
        if "validation" in key:
            validation_statuses[key] = validation_status(path)

    forbidden_hits = no_positive_forbidden_claims(note_md + "\n" + claim_boundary_md + "\n" + json.dumps(next_gate, sort_keys=True))
    checks = [
        {"check_id": "V01", "name": "Required matrix-topology inputs exist", "status": "pass", "details": {"missing_required_inputs": []}},
        {"check_id": "V02", "name": "Upstream validations pass or are recorded", "status": "pass" if matrix_validation.get("validation_status") == "pass" else "fail", "details": {"validation_statuses": validation_statuses}},
        {"check_id": "V03", "name": "Star topology evidence present", "status": "pass" if evidence_by_metric.get("unique_A_id") == 1 and int(evidence_by_metric.get("unique_B_id", 0)) > 0 and float(evidence_by_metric.get("star_topology_score", 0)) == 1.0 and "star" in str(evidence_by_metric.get("component_topology_class", "")) else "fail", "details": {"unique_A_id": evidence_by_metric.get("unique_A_id"), "unique_B_id": evidence_by_metric.get("unique_B_id"), "star_topology_score": evidence_by_metric.get("star_topology_score"), "component_topology_class": evidence_by_metric.get("component_topology_class")}},
        {"check_id": "V04", "name": "No source-native loop evidence", "status": "pass" if str(evidence_by_metric.get("source_native_closed_triple_count")) == "0" and str(evidence_by_metric.get("valid_loop_count")) == "0" else "fail", "details": {"source_native_closed_triple_count": evidence_by_metric.get("source_native_closed_triple_count"), "valid_loop_count": evidence_by_metric.get("valid_loop_count")}},
        {"check_id": "V05", "name": "No inferred edges", "status": "pass" if str(evidence_by_metric.get("inferred_edge_count")) == "0" else "fail", "details": {"inferred_edge_count": evidence_by_metric.get("inferred_edge_count")}},
        {"check_id": "V06", "name": "Synthetic/physical flag boundary", "status": "pass" if evidence_by_metric.get("phase_is_synthetic_diagnostic") == "true" and evidence_by_metric.get("phase_is_physical") == "false" else "warning", "details": {"phase_is_synthetic_diagnostic": evidence_by_metric.get("phase_is_synthetic_diagnostic"), "phase_is_physical": evidence_by_metric.get("phase_is_physical")}},
        {"check_id": "V07", "name": "Density warning present", "status": "pass" if DENSITY_WARNING in note_md else "fail", "details": {"density_warning": DENSITY_WARNING}},
        {"check_id": "V08", "name": "Forbidden claim wording absent", "status": "pass" if not forbidden_hits else "fail", "details": {"positive_claim_hits": forbidden_hits}},
        {"check_id": "V09", "name": "Replay protection", "status": "pass", "details": {"default_existing_output_dir_policy": "refuse overwrite unless --force is supplied"}},
        {"check_id": "V10", "name": "Manifest hashes", "status": "pending_manifest_written", "details": {"manifest_includes_input_and_generated_hashes": True}},
    ]
    validation_status_final = "pass" if all(check["status"] in {"pass", "warning", "pending_manifest_written"} for check in checks) else "fail"
    summary["validation_status"] = validation_status_final
    write_json(OUTPUTS["summary"], summary)

    input_hashes = {rel(path): sha256_file(path) for path in upstream_files.values()}
    input_hashes[rel(SCRIPT_PATH)] = sha256_file(SCRIPT_PATH)
    manifest = {
        "run_id": RUN_ID,
        "timestamp_utc": timestamp,
        "input_artifacts": input_hashes,
        "generated_artifacts": {},
        "manifest_self_hash_policy": "not included because the manifest hash would be self-referential",
        "claim_boundary": CLAIM_BOUNDARY,
    }
    write_json(OUTPUTS["manifest"], manifest)
    generated_hashes = {
        rel(path): sha256_file(path)
        for key, path in OUTPUTS.items()
        if key not in {"manifest", "validation"} and path.exists()
    }
    manifest["generated_artifacts"] = generated_hashes
    write_json(OUTPUTS["manifest"], manifest)

    for check in checks:
        if check["check_id"] == "V10":
            check["status"] = "pass"
            check["details"]["input_hash_count"] = len(input_hashes)
            check["details"]["generated_hash_count"] = len(generated_hashes)

    validation_report = {
        "run_id": RUN_ID,
        "timestamp_utc": timestamp,
        "validation_status": validation_status_final,
        "checks": checks,
        "claim_boundary": CLAIM_BOUNDARY,
    }
    write_json(OUTPUTS["validation"], validation_report)
    manifest["generated_artifacts"][rel(OUTPUTS["validation"])] = sha256_file(OUTPUTS["validation"])
    write_json(OUTPUTS["manifest"], manifest)

    return summary


def main() -> int:
    parser = argparse.ArgumentParser(description="Create the D1K source-topology limit note.")
    parser.add_argument("--force", action="store_true", help="Replace an existing output directory.")
    args = parser.parse_args()

    prepare_output(args.force)
    summary = build_outputs()
    print(f"run_id: {RUN_ID}")
    print(f"output_dir: {rel(OUTPUT_DIR)}")
    print(f"evidence_row_count: {summary['evidence_row_count']}")
    print(f"main_conclusion: {summary['main_conclusion']}")
    print(f"density_warning_present: {summary['density_warning_present']}")
    print(f"validation_status: {summary['validation_status']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
