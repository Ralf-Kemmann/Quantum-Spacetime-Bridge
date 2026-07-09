#!/usr/bin/env python3
"""QSB/PBR Matrix Construction Contract infrastructure.

This callable exposes explicit contract-field export and validation hooks for
the historical QSB/PBR K_candidate construction. It is not a physics-claim
generator, does not authorize Execution 01A, and does not run Lag-Class
Sufficiency, nullmodels, DWH writes, literature imports, or mechanism tests.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import sys
from pathlib import Path


FIELDNAMES = ["field", "value", "status", "evidence", "blocking_if_unset", "notes"]
LAG_FIELDNAMES = ["field", "value", "status", "validation_rule", "blocking_if_unset", "notes"]
CONTROL_FIELDNAMES = ["field", "value", "status", "validation_rule", "blocking_if_unset", "notes"]
VALIDATION_FIELDNAMES = ["check_id", "check_name", "status", "observed", "expected", "blocking", "notes"]

CLAIM_BOUNDARY = "blocked_no_physics_claim;blocked_no_mechanism_claim;execution_01a_authorized=false"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def write_csv(path: Path, fieldnames: list[str], rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def contract_rows(args: argparse.Namespace) -> list[dict[str, str]]:
    callable_args = (
        "--mode;--source-db;--pair-basis;--k-candidate;--expected-k-sha256;"
        "--output-dir;--contract-manifest"
    )
    return [
        row("source_code_artifact_path", "scripts/qsb_extract03a_r1/run_authorized_execution_with_s1_addendum.py", "documented_existing_evidence", "source alignment hash inventory", "false", "Historical reference runner; read-only."),
        row("source_code_artifact_sha256", "283aa9295d76c1243398550e0da4447072628989c21f3d987c4b5e8ca1649c06", "documented_existing_evidence", "source alignment hash inventory", "false", "Historical reference runner hash."),
        row("K_candidate_export_path", str(args.k_candidate), "documented_existing_evidence", "source alignment K export inventory", "false", "Existing export only; not recomputed by this command."),
        row("K_candidate_export_sha256", args.expected_k_sha256, "documented_existing_evidence", "source patch design expected hash", "false", "Baseline hash gate."),
        row("input_pair_table_path", str(args.pair_basis), "documented_existing_evidence", "source patch design pair basis", "false", "Pair basis artifact supplied explicitly."),
        row("pair_identifier_columns", "canonical_pair_id", "documented_existing_evidence", "pair basis review", "false", "canonical_pair_id is pair_i|pair_j."),
        row("endpoint_columns", "pair_i;pair_j", "documented_existing_evidence", "pair basis review", "false", "Endpoint columns are declared."),
        row("lag_class_column", "requires_human_value", "requires_human_value", "source patch design", "true", "Must be declared before Execution 01A."),
        row("pair_policy", "ordered non-diagonal pairs sorted numeric ascending pair_i then pair_j", "documented_existing_evidence", "pair basis review", "false", "Pair policy is documented."),
        row("pair_symmetry_policy", "K symmetrized after dot product", "documented_existing_evidence", "EXTRACT03A-R1 code trace", "false", "Restated as contract field."),
        row("diagonal_policy", "K diagonal filled with 1.0", "documented_existing_evidence", "EXTRACT03A-R1 code trace", "false", "Restated as contract field."),
        row("zero_diagonal_policy", "not_applicable_with_reason: K diagonal policy is 1.0; zero diagonal applies outside K", "not_applicable_with_reason", "source patch design", "false", "K-only contract does not use zero diagonal."),
        row("duplicate_pair_policy", "requires_human_value", "requires_human_value", "source patch design", "true", "Implementation exposes declaration point; value not invented."),
        row("missing_pair_policy", "requires_human_value", "requires_human_value", "source patch design", "true", "Implementation exposes declaration point; value not invented."),
        row("lag_class_definition", "requires_human_value", "requires_human_value", "source patch design", "true", "Must be declared before Execution 01A."),
        row("lag_sort_order", "requires_human_value", "requires_human_value", "source patch design", "true", "Must be declared before controls."),
        row("matrix_shape_rule", "42x42 over canonical ordered non-diagonal pair basis", "documented_existing_evidence", "EXTRACT03A-R1 validation", "false", "Shape rule is documented."),
        row("matrix_index_order_rule", "numeric ascending pair_i then pair_j", "documented_existing_evidence", "pair basis review", "false", "Order rule is documented."),
        row("matrix_entry_formula_or_callable", "dot product of L2-normalized wrapped_delta_phi vectors", "documented_existing_evidence", "runtime mapping", "false", "Formula field only; this command does not recompute K in validation-only mode."),
        row("weighting_rule", "uniform over x_index for first scope", "documented_existing_evidence", "human freeze decision", "false", "Weighting rule is documented."),
        row("normalization_rule", "L2-normalize each phase-response vector; reject zero-norm vectors", "documented_existing_evidence", "human freeze decision", "false", "Normalization rule is documented."),
        row("aggregation_rule", "normalized @ normalized.T", "documented_existing_evidence", "EXTRACT03A-R1 code trace", "false", "Restated as contract field."),
        row("symmetrization_rule", "(K + K.T) / 2", "documented_existing_evidence", "EXTRACT03A-R1 code trace", "false", "Restated as contract field."),
        row("missing_value_policy", "requires_human_value", "requires_human_value", "source patch design", "true", "Must be declared before Execution 01A."),
        row("PSD_check_rule", "minimum eigenvalue >= -1e-10", "documented_existing_evidence", "EXTRACT03A-R1 K validation", "false", "PSD lower tolerance is documented."),
        row("rank_check_rule", "requires_human_value", "requires_human_value", "source patch design", "true", "Must be declared or explicitly not_required."),
        row("eigenvalue_threshold_policy", "requires_human_value", "requires_human_value", "source patch design", "true", "Full threshold policy is a declaration point."),
        row("numerical_rank_threshold", "requires_human_value", "requires_human_value", "source patch design", "true", "Must be declared if rank check is required."),
        row("baseline_validation_rule", "finite;shape;symmetry;diagonal;PSD;range;hash", "documented_existing_evidence", "EXTRACT03A-R1 validation and source patch design", "false", "Baseline validation field."),
        row("expected_output_hash_or_similarity_rule", f"exact_sha256:{args.expected_k_sha256}", "documented_existing_evidence", "source patch design", "false", "Exact hash gate unless future review approves similarity."),
        row("equal_cardinality_partition_eligibility", "requires_human_value", "requires_human_value", "source patch design", "true", "Controls remain declaration points."),
        row("random_seed_policy", "requires_human_value", "requires_human_value", "source patch design", "true", "Seed values are not invented."),
        row("trial_count_policy", "requires_human_value", "requires_human_value", "source patch design", "true", "Trial counts are not invented."),
        row("reconstruction_script_or_function", "scripts/qsb_pbr_matrix_contract/reconstruct_k_candidate.py", "documented_existing_evidence", "this implementation", "false", "Scoped contract infrastructure callable."),
        row("required_arguments", callable_args, "documented_existing_evidence", "this implementation", "false", "Explicit CLI arguments."),
        row("expected_outputs", "contract_field_export.csv;lag_class_handoff.csv;control_policy_export.csv;validation_summary.csv;dry_run_manifest.json", "documented_existing_evidence", "this implementation", "false", "Outputs are explicit."),
        row("validation_command", "python scripts/qsb_pbr_matrix_contract/reconstruct_k_candidate.py --mode validate ...", "documented_existing_evidence", "this implementation", "false", "Validation command is explicit."),
        row("claim_boundary", CLAIM_BOUNDARY, "documented_existing_evidence", "this implementation", "false", "Execution 01A remains unauthorized."),
    ]


def row(field: str, value: str, status: str, evidence: str, blocking: str, notes: str) -> dict[str, str]:
    return {
        "field": field,
        "value": value,
        "status": status,
        "evidence": evidence,
        "blocking_if_unset": blocking,
        "notes": notes,
    }


def lag_rows() -> list[dict[str, str]]:
    return [
        lag_row("lag_value_column", "requires_human_value", "requires_human_value", "lag_value column present and reproducible", "true", "No lag values are inferred by this implementation."),
        lag_row("lag_class_column", "requires_human_value", "requires_human_value", "lag_class column keyed by canonical_pair_id", "true", "Required before Execution 01A."),
        lag_row("lag_class_definition", "requires_human_value", "requires_human_value", "definition field non-empty and matches export", "true", "Signed/absolute/other lag class must be reviewed."),
        lag_row("lag_class_sort_order", "requires_human_value", "requires_human_value", "class order hash recorded", "true", "Sort order declaration point."),
        lag_row("lag_class_cardinality_export", "requires_human_value", "requires_human_value", "sum cardinalities equals pair count", "true", "Cardinality export declaration point."),
        lag_row("lag_preserving_shuffle_definition", "requires_human_value", "requires_human_value", "shuffle dry-run validates preserved class counts", "true", "Controls declaration point."),
        lag_row("lag_alias_exclusion_rule", "requires_human_value", "requires_human_value", "alias exclusion list present", "true", "Leakage guard declaration point."),
        lag_row("lag_handoff_validation", "one row per canonical_pair_id; no missing lag class once declared", "documented_existing_evidence", "validation command checks schema and placeholders", "false", "Infrastructure validation only."),
    ]


def lag_row(field: str, value: str, status: str, validation: str, blocking: str, notes: str) -> dict[str, str]:
    return {
        "field": field,
        "value": value,
        "status": status,
        "validation_rule": validation,
        "blocking_if_unset": blocking,
        "notes": notes,
    }


def control_rows() -> list[dict[str, str]]:
    fields = [
        ("random_seed_policy", "seed field present and immutable"),
        ("trial_count_policy", "trial count positive integer or control disabled"),
        ("equal_cardinality_partition_eligibility", "eligibility field in allowed vocabulary"),
        ("class_count_control_eligibility", "eligibility field in allowed vocabulary"),
        ("membership_destruction_eligibility", "marginal rule validates or disabled"),
        ("label_relabeling_eligibility", "label invariance condition present"),
        ("matrix_rule_tautology_screen_eligibility", "tautology screen schema validates"),
        ("randomization_manifest_schema", "CSV schema check"),
    ]
    return [
        {
            "field": field,
            "value": "requires_human_value",
            "status": "requires_human_value",
            "validation_rule": validation,
            "blocking_if_unset": "true",
            "notes": "Declaration point only; no randomization or controls are executed.",
        }
        for field, validation in fields
    ]


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Export and validate QSB/PBR Matrix Construction Contract infrastructure. "
            "This command does not authorize Execution 01A."
        )
    )
    parser.add_argument("--mode", choices=["dry-run", "export", "validate"], required=True)
    parser.add_argument("--source-db", type=Path, required=True)
    parser.add_argument("--pair-basis", type=Path, required=True)
    parser.add_argument("--k-candidate", type=Path, required=True)
    parser.add_argument("--expected-k-sha256", required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--contract-manifest", type=Path)
    parser.add_argument("--k-validation", type=Path)
    return parser.parse_args(argv)


def dry_run(args: argparse.Namespace) -> int:
    manifest = {
        "mode": "dry-run",
        "would_read": {
            "source_db": str(args.source_db),
            "pair_basis": str(args.pair_basis),
            "k_candidate": str(args.k_candidate),
            "contract_manifest": str(args.contract_manifest) if args.contract_manifest else "not_supplied",
            "k_validation": str(args.k_validation) if args.k_validation else "not_supplied",
        },
        "would_write": {
            "output_dir": str(args.output_dir),
            "contract_field_export": "contract_field_export.csv",
            "lag_class_handoff": "lag_class_handoff.csv",
            "control_policy_export": "control_policy_export.csv",
            "validation_summary": "validation_summary.csv",
            "dry_run_manifest": "dry_run_manifest.json",
        },
        "hidden_state_policy": "all inputs must be supplied via explicit CLI arguments",
        "execution_01a_authorized": False,
        "claim_boundary": CLAIM_BOUNDARY,
    }
    print(json.dumps(manifest, indent=2, sort_keys=True))
    return 0


def export_contract(args: argparse.Namespace) -> int:
    args.output_dir.mkdir(parents=True, exist_ok=True)
    write_csv(args.output_dir / "contract_field_export.csv", FIELDNAMES, contract_rows(args))
    write_csv(args.output_dir / "lag_class_handoff.csv", LAG_FIELDNAMES, lag_rows())
    write_csv(args.output_dir / "control_policy_export.csv", CONTROL_FIELDNAMES, control_rows())
    dry_manifest = {
        "explicit_inputs": sorted(
            {
                "source_db": str(args.source_db),
                "pair_basis": str(args.pair_basis),
                "k_candidate": str(args.k_candidate),
                "expected_k_sha256": args.expected_k_sha256,
                "output_dir": str(args.output_dir),
            }.items()
        ),
        "hidden_state_policy": "no implicit notebook, environment, DWH, or session state",
        "execution_01a_authorized": False,
        "claim_boundary": CLAIM_BOUNDARY,
    }
    (args.output_dir / "dry_run_manifest.json").write_text(
        json.dumps(dry_manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    return validate(args)


def validate(args: argparse.Namespace) -> int:
    checks: list[dict[str, str]] = []

    def check(name: str, passed: bool, observed: str, expected: str, blocking: str, notes: str) -> None:
        checks.append(
            {
                "check_id": f"VAL-{len(checks)+1:02d}",
                "check_name": name,
                "status": "pass" if passed else "fail",
                "observed": observed,
                "expected": expected,
                "blocking": blocking,
                "notes": notes,
            }
        )

    explicit_paths = [args.source_db, args.pair_basis, args.k_candidate]
    for path in explicit_paths:
        check(f"input_exists:{path.name}", path.exists(), str(path), "existing explicit path", "yes", "No hidden fallback path is used.")

    if args.k_candidate.exists():
        observed_k_hash = sha256(args.k_candidate)
        check(
            "K_candidate_export_hash_check",
            observed_k_hash == args.expected_k_sha256,
            observed_k_hash,
            args.expected_k_sha256,
            "yes",
            "Existing K export hash check; no K reconstruction performed.",
        )

    contract_path = args.output_dir / "contract_field_export.csv"
    lag_path = args.output_dir / "lag_class_handoff.csv"
    control_path = args.output_dir / "control_policy_export.csv"
    for path, fields in [
        (contract_path, set(FIELDNAMES)),
        (lag_path, set(LAG_FIELDNAMES)),
        (control_path, set(CONTROL_FIELDNAMES)),
    ]:
        if path.exists():
            rows = read_csv(path)
            actual = set(rows[0]) if rows else set()
            check(f"CSV_schema_check:{path.name}", fields.issubset(actual), ",".join(sorted(actual)), ",".join(sorted(fields)), "yes", "Schema must be explicit.")
        else:
            check(f"CSV_schema_check:{path.name}", False, "missing", "present", "yes", "Run export mode before validation.")

    if contract_path.exists():
        rows = read_csv(contract_path)
        field_set = {r["field"] for r in rows}
        required_fields = {r["field"] for r in contract_rows(args)}
        check(
            "contract_fields_exported_check",
            required_fields.issubset(field_set),
            str(len(field_set)),
            str(len(required_fields)),
            "yes",
            "All essential contract field names must be exported.",
        )
        placeholders = [r for r in rows if r.get("status") in {"requires_human_value", "requires_source_evidence"}]
        check(
            "required_placeholder_status_check",
            bool(placeholders),
            str(len(placeholders)),
            ">0 explicit placeholders",
            "no",
            "Placeholders are explicit declaration points, not silent defaults.",
        )
        claim_rows = [r for r in rows if r.get("field") == "claim_boundary"]
        claim_ok = bool(claim_rows) and "execution_01a_authorized=false" in claim_rows[0].get("value", "")
        check(
            "claim_boundary_check",
            claim_ok,
            claim_rows[0].get("value", "missing") if claim_rows else "missing",
            "execution_01a_authorized=false",
            "yes",
            "Execution 01A remains blocked.",
        )

    manifest_path = args.output_dir / "dry_run_manifest.json"
    if manifest_path.exists():
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        no_hidden = "explicit_inputs" in manifest and manifest.get("execution_01a_authorized") is False
        check("no_hidden_state_check", no_hidden, json.dumps(manifest, sort_keys=True), "explicit_inputs and execution_01a_authorized=false", "yes", "Dry-run manifest enumerates explicit inputs.")
    else:
        check("no_hidden_state_check", False, "missing", "dry_run_manifest.json", "yes", "Run export mode before validation.")

    write_csv(args.output_dir / "validation_summary.csv", VALIDATION_FIELDNAMES, checks)
    failed_blocking = [c for c in checks if c["status"] == "fail" and c["blocking"] == "yes"]
    print(json.dumps({"validation_checks": len(checks), "blocking_failures": len(failed_blocking)}, indent=2, sort_keys=True))
    return 1 if failed_blocking else 0


def main(argv: list[str] | None = None) -> int:
    args = parse_args(sys.argv[1:] if argv is None else argv)
    if args.mode == "dry-run":
        return dry_run(args)
    if args.mode == "export":
        return export_contract(args)
    return validate(args)


if __name__ == "__main__":
    raise SystemExit(main())
