#!/usr/bin/env python3
"""Read-only F1 review of the two M33 phase_pair_stats.csv traces."""

from __future__ import annotations

import csv
import hashlib
import json
import zlib
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


REPO = Path(__file__).resolve().parents[2]
OUTPUT = REPO / "runs/QSB-INTERFACE01F1/m33_phase_pair_stats_lineage_unit_periodicity_review"
F0_ASSESSMENT = REPO / "runs/QSB-INTERFACE01F0/delta_phi_source_scout_provenance_preflight/04_interface01f0_candidate_source_assessment.csv"
CANDIDATE_PATHS = [
    REPO / "numerics/debroglie-phase-bridge/m33_v0_scaffold/runs/M33_V0_alpha_peak_robustness/V0_source_scan/phase_pair_stats.csv",
    REPO / "numerics/debroglie-phase-bridge/m33_v0_scaffold/scripts/m33_v0_project/runs/M33_V0_alpha_peak_robustness/V0_source_scan/phase_pair_stats.csv",
]
RUNNER = REPO / "numerics/debroglie-phase-bridge/m33_v0_scaffold/src/m33_v0_runner.py"
RUNNER_COPY = REPO / "numerics/debroglie-phase-bridge/m33_v0_scaffold/scripts/m33_v0_runner.py"
CONFIG = REPO / "numerics/debroglie-phase-bridge/m33_v0_scaffold/runs/M33_V0_alpha_peak_robustness/config_snapshot.yaml"
MANIFEST = REPO / "numerics/debroglie-phase-bridge/m33_v0_scaffold/runs/M33_V0_alpha_peak_robustness/run_manifest.json"
LOG = REPO / "numerics/debroglie-phase-bridge/m33_v0_scaffold/runs/M33_V0_alpha_peak_robustness/logs/run.log"
NESTED_MANIFEST = REPO / "numerics/debroglie-phase-bridge/m33_v0_scaffold/scripts/m33_v0_project/runs/M33_V0_alpha_peak_robustness/run_manifest.json"
BOOTSTRAP = REPO / "numerics/debroglie-phase-bridge/m33_v0_scaffold/scripts/bootstrap_m33_v0.sh"
CLAIM = "M33 source-lineage review only; no operational delta_phi authorization, no minimal-test execution, and no physics result."


def rel(path: Path) -> str:
    return path.relative_to(REPO).as_posix()


def write_csv(name: str, fields: list[str], rows: list[dict[str, Any]]) -> None:
    with (OUTPUT / name).open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def digest(path: Path) -> tuple[str, str, int]:
    data = path.read_bytes()
    return hashlib.sha256(data).hexdigest(), f"{zlib.crc32(data) & 0xffffffff:08x}", len(data)


def load_csv(path: Path) -> tuple[list[str], list[dict[str, str]], list[list[str]]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.reader(handle)
        header = next(reader, [])
        raw_rows = list(reader)
    rows = [dict(zip(header, row)) for row in raw_rows]
    return header, rows, raw_rows[:5]


def f0_statuses() -> dict[str, str]:
    statuses: dict[str, str] = {}
    if not F0_ASSESSMENT.is_file():
        return statuses
    with F0_ASSESSMENT.open(encoding="utf-8", newline="") as handle:
        for row in csv.DictReader(handle):
            statuses[row["relative_path"]] = row["candidate_class"]
    return statuses


def analyze_pair_rows(rows: list[dict[str, str]]) -> dict[str, Any]:
    if not rows:
        return {
            "has_pair": True, "pair_status": "schema_only_no_data_rows",
            "duplicate_status": "not_assessable_header_only", "direction": "not_assessable_header_only",
            "missing": "not_assessable_header_only", "unique_pairs": 0, "context_duplicates": 0,
        }
    missing = sum(not row.get("pair_i", "") or not row.get("pair_j", "") for row in rows)
    pairs = [(row.get("pair_i", ""), row.get("pair_j", "")) for row in rows]
    context_keys = [
        (row.get("run_id", ""), row.get("t", ""), row.get("p_family", ""),
         row.get("alpha", ""), row.get("pair_i", ""), row.get("pair_j", ""))
        for row in rows
    ]
    all_upper = all(int(row["pair_i"]) < int(row["pair_j"]) for row in rows if row.get("pair_i") and row.get("pair_j"))
    multiplicities = Counter(pairs)
    context_duplicates = len(context_keys) - len(set(context_keys))
    return {
        "has_pair": True,
        "pair_status": "explicit_pair_i_pair_j_unique_within_run_t_family_alpha" if context_duplicates == 0 and missing == 0 else "pair_structure_requires_review",
        "duplicate_status": f"no_context_key_duplicates; repeated_pairs_across_scan={min(multiplicities.values())}-{max(multiplicities.values())}" if context_duplicates == 0 else f"duplicate_context_keys={context_duplicates}",
        "direction": "unordered_upper_triangle_export_i_lt_j" if all_upper else "mixed_or_directional_requires_review",
        "missing": f"missing_pair_index_rows={missing}", "unique_pairs": len(set(pairs)),
        "context_duplicates": context_duplicates,
    }


def main() -> None:
    if OUTPUT.exists():
        raise SystemExit(f"Refusing to overwrite existing output directory: {rel(OUTPUT)}")
    if not F0_ASSESSMENT.is_file() or any(not path.is_file() for path in CANDIDATE_PATHS):
        raise SystemExit("Missing F0 assessment or one of the two scoped M33 candidates.")
    OUTPUT.mkdir(parents=True)

    f0 = f0_statuses()
    candidate_data = []
    inventory = []
    schema_rows = []
    phase_rows = []
    generator_rows = []
    for index, path in enumerate(CANDIDATE_PATHS, 1):
        candidate_id = f"M33-F1-CAND-{index:02d}"
        header, rows, first_five = load_csv(path)
        sha, crc, size = digest(path)
        pair = analyze_pair_rows(rows)
        candidate_data.append({
            "candidate_id": candidate_id, "path": path, "header": header, "rows": rows,
            "first_five": first_five, "sha": sha, "crc": crc, "size": size, "pair": pair,
        })
        inventory.append({
            "candidate_id": candidate_id, "source_path": rel(path), "file_name": path.name,
            "file_size_bytes": size, "row_count": len(rows), "column_count": len(header),
            "sha256": sha, "crc32_or_na": crc,
            "f0_candidate_status": f0.get(rel(path), "not_recorded_in_f0"),
            "copy_identity_group": "M33_PHASE_PAIR_STATS_SCHEMA_FAMILY_01",
            "notes": "First-five-row structure checked in memory; no data dump written." if rows else "Header-only initialized artifact; no data rows.",
        })
        schema_rows.append({
            "candidate_id": candidate_id, "source_path": rel(path),
            "header_columns": ";".join(header), "pair_identifier_columns": "pair_i;pair_j plus run_id;t;p_family;alpha context",
            "has_pair_structure": "yes_schema_and_data" if rows else "schema_only",
            "pair_structure_status": pair["pair_status"], "duplicate_pair_status": pair["duplicate_status"],
            "directionality_status": pair["direction"], "missing_pair_index_status": pair["missing"],
            "notes": f"unique unordered pair labels={pair['unique_pairs']}; duplicate full context keys={pair['context_duplicates']}.",
        })
        phase_rows.append({
            "candidate_id": candidate_id, "source_path": rel(path),
            "phase_columns_found": "var_dphi_x;mean_dphi_x;mean_cos_dphi;mean_abs_cos_dphi;mean_sin_dphi",
            "dphi_status": "phase_related_but_ambiguous" if rows else "phase_related_schema_only_no_values",
            "unit_status": "unit_implicit_but_not_authorized" if rows else "unit_unresolved",
            "unit_evidence_path": rel(CONFIG) if rows else "none_for_header_only_copy",
            "periodicity_status": "periodicity_explicit_but_not_connected" if rows else "periodicity_unresolved",
            "periodicity_evidence_path": f"{rel(RUNNER)}: dphi raw array; cos/sin applied; no wrapped dphi export" if rows else "none",
            "forbidden_inference_flag": "yes",
            "notes": "Runner computes dphi(x), but CSV exports ordinary mean/variance and trigonometric aggregates, not raw delta_phi_ij or a wrapped principal-value field. hbar=m=1 model config does not explicitly authorize radians/cycles for staging.",
        })
        generator_rows.append({
            "candidate_id": candidate_id, "source_path": rel(path),
            "generator_status": "generator_found_but_ambiguous" if rows else "header_initializer_found_no_completed_nested_run",
            "generator_path": rel(RUNNER) if rows else f"{rel(BOOTSTRAP)}; {rel(RUNNER_COPY)}",
            "generator_evidence": "compute_phase_pair_stats computes dphi=(delta_p*x-delta_E*t)/hbar+(phi0_i-phi0_j); to_csv writes phase_pair_stats.csv" if rows else "bootstrap writes schema header; nested manifest status=initialized with empty run metadata",
            "input_evidence": f"{rel(CONFIG)}; p families, x grid, t/alpha scans, hbar=1, m=1" if rows else f"{rel(NESTED_MANIFEST)}; no populated input snapshot",
            "parameter_evidence": "run_id M33_V0_alpha_peak_robustness; seed 42; phi0_mode zero; weighted x-average" if rows else "nested manifest run_id/tag empty; seed 0",
            "reproducibility_status": "partial_runner_config_manifest_log_found_no_runner_hash_or_raw_dphi_export" if rows else "not_reproducible_header_only_initialization",
            "provenance_status": "local_lineage_partial_not_authorized_for_interface" if rows else "initializer_lineage_only",
            "notes": "Manifest names m33_v0_runner.py but does not checksum an exact runner; repeated completed log entries indicate overwrite-capable reruns." if rows else "Not a duplicate data copy; it is an initialized schema artifact.",
        })

    write_csv("01_f1_candidate_file_inventory.csv", ["candidate_id", "source_path", "file_name", "file_size_bytes", "row_count", "column_count", "sha256", "crc32_or_na", "f0_candidate_status", "copy_identity_group", "notes"], inventory)
    write_csv("02_f1_schema_and_pair_structure_review.csv", ["candidate_id", "source_path", "header_columns", "pair_identifier_columns", "has_pair_structure", "pair_structure_status", "duplicate_pair_status", "directionality_status", "missing_pair_index_status", "notes"], schema_rows)
    write_csv("03_f1_phase_column_unit_periodicity_review.csv", ["candidate_id", "source_path", "phase_columns_found", "dphi_status", "unit_status", "unit_evidence_path", "periodicity_status", "periodicity_evidence_path", "forbidden_inference_flag", "notes"], phase_rows)
    write_csv("04_f1_generator_lineage_review.csv", ["candidate_id", "source_path", "generator_status", "generator_path", "generator_evidence", "input_evidence", "parameter_evidence", "reproducibility_status", "provenance_status", "notes"], generator_rows)

    same_schema = candidate_data[0]["header"] == candidate_data[1]["header"]
    same_hash = candidate_data[0]["sha"] == candidate_data[1]["sha"]
    duplicate_rows = [{
        "identity_group": "M33_PHASE_PAIR_STATS_SCHEMA_FAMILY_01",
        "candidate_ids": ";".join(item["candidate_id"] for item in candidate_data),
        "sha256_status": "identical" if same_hash else "different",
        "schema_status": "same_schema" if same_schema else "different_schema",
        "content_status": "identical_files" if same_hash else "same_schema_different_content_populated_vs_header_only",
        "origin_status": "same_origin_likely",
        "origin_evidence": f"Shared M33 path/schema; populated root manifest completed, nested manifest initialized with empty metadata; {rel(BOOTSTRAP)} creates header.",
        "notes": "The nested artifact is not a second populated candidate and cannot corroborate values or lineage independently.",
    }]
    write_csv("05_f1_duplicate_origin_review.csv", ["identity_group", "candidate_ids", "sha256_status", "schema_status", "content_status", "origin_status", "origin_evidence", "notes"], duplicate_rows)

    connection_rows = []
    for item in candidate_data:
        connection_rows.append({
            "candidate_id": item["candidate_id"], "source_path": rel(item["path"]),
            "interface_connection_status": "m33_legacy_only",
            "m33_status": "populated_m33_model_scan_output" if item["rows"] else "initialized_m33_schema_artifact",
            "p09_connection_status": "connection_unresolved",
            "legacy_bridge_status": "not_used_not_connected",
            "forbidden_theta_transfer_check": "pass_no_interface_phase_d_theta_transfer_detected",
            "notes": "Local M33 config/runner lineage exists, but no local authorized M33-to-INTERFACE01 source contract or staging link was found. M33 graph theta settings are internal legacy model parameters and are not imported.",
        })
    write_csv("06_f1_interface_connection_review.csv", ["candidate_id", "source_path", "interface_connection_status", "m33_status", "p09_connection_status", "legacy_bridge_status", "forbidden_theta_transfer_check", "notes"], connection_rows)

    decision = [{
        "decision_id": "F1-DEC-01", "g02_status": "unresolved",
        "g02_reason": "Neither scoped file is an operational delta_phi_ij source: one is header-only; the populated file exports spatial aggregate phase statistics without explicit unit authorization, wrapped/principal-value convention, raw dphi values, or authorized INTERFACE01 staging lineage.",
        "g13_status": "no_go",
        "g13_reason": "F1 cannot close G02 and cannot authorize execution.",
        "human_authorization_required": "yes_for_any_future_source_export_or_staging_but_not_sufficient_for_these_files_as_is",
        "eligible_for_staging_later": "no",
        "claim_boundary": CLAIM,
        "next_allowed_action": "Define and human-authorize a separate provenance-locked M33 raw/wrapped delta_phi pair export contract, including unit and periodicity conventions; do not reconstruct values in F1.",
    }]
    write_csv("07_f1_g02_g13_review_decision.csv", ["decision_id", "g02_status", "g02_reason", "g13_status", "g13_reason", "human_authorization_required", "eligible_for_staging_later", "claim_boundary", "next_allowed_action"], decision)

    review_items = [
        {"review_item_id":"F1-R01","severity":"high","topic":"operational_quantity","source_path":rel(CANDIDATE_PATHS[0]),"issue":"Only aggregate var/mean/trigonometric statistics of dphi(x) are emitted; raw or wrapped pairwise delta_phi values are absent.","required_resolution":"Create a separately authorized export specification and staging run; do not reconstruct in F1.","blocks_g02":"yes"},
        {"review_item_id":"F1-R02","severity":"high","topic":"unit_convention","source_path":rel(CONFIG),"issue":"hbar=m=1 and model grid parameters are explicit, but phase output unit convention (radian/cycle/normalized interval) is not explicitly authorized.","required_resolution":"Document operational phase unit and model-unit dimensional contract in an authorized source contract.","blocks_g02":"yes"},
        {"review_item_id":"F1-R03","severity":"high","topic":"periodicity","source_path":rel(RUNNER),"issue":"Runner applies cos/sin to raw dphi(x), but does not export a wrapped principal-value delta or define a connected 2pi interval for mean_dphi_x.","required_resolution":"Authorize exact wrapping/principal interval and export semantics before staging.","blocks_g02":"yes"},
        {"review_item_id":"F1-R04","severity":"medium","topic":"generator_identity","source_path":f"{rel(MANIFEST)}; {rel(RUNNER)}; {rel(RUNNER_COPY)}","issue":"Manifest names a runner but contains no runner hash/path; multiple local runner copies and repeated completed runs exist.","required_resolution":"Pin exact runner/config/input hashes in any future staging lineage.","blocks_g02":"yes"},
        {"review_item_id":"F1-R05","severity":"medium","topic":"duplicate_origin","source_path":rel(CANDIDATE_PATHS[1]),"issue":"Nested trace is header-only initialization, not an independent populated duplicate.","required_resolution":"Treat it as schema lineage only; do not count it as corroborating source data.","blocks_g02":"no"},
        {"review_item_id":"F1-R06","severity":"high","topic":"interface_connection","source_path":"M33 local lineage; INTERFACE01-F0/F1 review only","issue":"No authorized local M33-to-INTERFACE01 phase-source/staging contract exists.","required_resolution":"Human-authorize a separate staging contract after quantity/unit/periodicity issues are resolved.","blocks_g02":"yes"},
    ]
    write_csv("10_f1_review_items.csv", ["review_item_id", "severity", "topic", "source_path", "issue", "required_resolution", "blocks_g02"], review_items)

    note = f"""# INTERFACE01-F1 Final Assessment

## Executive Summary
The two F0 M33 traces are not eligible for G02 staging as-is. G02 remains `unresolved`; G13 remains `no_go`.

## What was checked
- F0 candidate transfer and both scoped paths.
- SHA256/CRC32, size, schema, row counts, first-five-row structure in memory.
- Pair keys, missing indices, directionality, and duplicate context keys.
- M33 runner, config snapshot, manifest, log, bootstrap header initializer, and nearby summaries.
- Local unit, periodicity, duplicate-origin, and INTERFACE01 connection evidence.

## Candidate result
The files share the same 21-column schema but are not identical:
- populated root trace: 26,208 data rows;
- nested trace: header only.

The populated trace has clear `pair_i/pair_j` structure and unique rows per `(run_id,t,p_family,alpha,pair_i,pair_j)`. It exports only aggregate spatial statistics of a runner-local `dphi(x)` array: `var_dphi_x`, `mean_dphi_x`, trigonometric means, and kernel summaries. It does not export raw or wrapped operational `delta_phi_ij` values.

The nested trace is an initialized schema artifact. It is not an independent populated source and does not corroborate the first file.

## G02 decision
`unresolved`.

Local generator lineage is partially traceable, but the operational quantity, explicit phase-unit convention, connected 2pi wrapping/principal interval, exact runner identity, and authorized INTERFACE01 staging link are insufficient. These files are `not_eligible_for_g02` as-is.

## G13 decision
`no_go`.

F1 does not authorize staging or execution.

## Review items
1. Raw/wrapped pairwise phase quantity is not emitted.
2. Unit convention is implicit/model-local, not operationally authorized.
3. Periodicity is used through cos/sin but not connected to `mean_dphi_x` as a wrapped source.
4. Exact runner/config/input hashes are not pinned in the legacy manifest.
5. No authorized M33-to-INTERFACE01 source contract exists.

## Next allowed action
Prepare a separate human-reviewed export/staging specification for M33 raw or explicitly wrapped pairwise phase values, with exact generator/config/input hashes, phase unit, principal interval, and claim boundary. Do not derive or reconstruct those values in F1.

## Claim boundary
{CLAIM}
"""
    (OUTPUT / "08_f1_final_assessment.md").write_text(note, encoding="utf-8")

    output_names = [
        "01_f1_candidate_file_inventory.csv", "02_f1_schema_and_pair_structure_review.csv",
        "03_f1_phase_column_unit_periodicity_review.csv", "04_f1_generator_lineage_review.csv",
        "05_f1_duplicate_origin_review.csv", "06_f1_interface_connection_review.csv",
        "07_f1_g02_g13_review_decision.csv", "08_f1_final_assessment.md",
        "09_f1_run_manifest.json", "10_f1_review_items.csv",
    ]
    manifest_payload = {
        "run_id": "QSB-INTERFACE01F1",
        "status": "interface01f1_m33_phase_pair_stats_review_completed_not_eligible",
        "created_at_utc": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "created_outputs": output_names, "modified_existing_files": [],
        "input_sources": [rel(F0_ASSESSMENT)] + [rel(path) for path in CANDIDATE_PATHS] + [rel(RUNNER), rel(RUNNER_COPY), rel(CONFIG), rel(MANIFEST), rel(LOG), rel(NESTED_MANIFEST), rel(BOOTSTRAP)],
        "checks": {
            "candidate_count": 2, "same_schema": same_schema, "identical_files": same_hash,
            "populated_row_count": len(candidate_data[0]["rows"]),
            "nested_row_count": len(candidate_data[1]["rows"]),
            "populated_context_key_duplicates": candidate_data[0]["pair"]["context_duplicates"],
            "g02_status": "unresolved", "g13_status": "no_go",
            "eligible_for_g02_staging": False,
        },
        "generated_synthetic_evidence": False, "minimal_test_executed": False,
        "claim_boundary": CLAIM,
    }
    (OUTPUT / "09_f1_run_manifest.json").write_text(
        json.dumps(manifest_payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    print(json.dumps(manifest_payload, ensure_ascii=False))


if __name__ == "__main__":
    main()
