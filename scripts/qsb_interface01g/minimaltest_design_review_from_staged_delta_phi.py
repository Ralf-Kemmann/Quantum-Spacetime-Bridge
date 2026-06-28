#!/usr/bin/env python3
"""Profile the authorized F3 delta-phi staging source for G design review only."""

from __future__ import annotations

import csv
import json
import math
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


REPO = Path(__file__).resolve().parents[2]
SOURCE_DB = REPO / "runs/QSB-INTERFACE01F3/authorized_delta_phi_export_staging_preflight/09_delta_phi_staging_preflight.sqlite"
OUTPUT = REPO / "runs/QSB-INTERFACE01G/minimaltest_design_review_from_staged_delta_phi"
EXPECTED_F3_STATUS = "interface01f3_authorized_delta_phi_export_staging_preflight_completed_export_staged"
SUCCESS_STATUS = "interface01g_minimaltest_design_review_completed_with_staged_source_profile"
BLOCKED_STATUS = "interface01g_minimaltest_design_review_blocked_upstream_validation_failed"
EXPECTED_TABLES = {
    "stg_delta_phi_export_metadata",
    "stg_delta_phi_static",
    "stg_delta_phi_spatial",
    "stg_delta_phi_validation_result",
}
CLAIM_BOUNDARY = (
    "G profiles an authorized staged delta_phi source and freezes design inputs only. "
    "It does not run the Minimaltest, validate thresholds as physics, or establish physical evidence."
)


def write_csv(path: Path, fields: list[str], rows: list[dict[str, Any]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def text(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, float):
        return format(value, ".17g")
    return str(value)


def fetch_one(connection: sqlite3.Connection, query: str, parameters: tuple[Any, ...] = ()) -> Any:
    row = connection.execute(query, parameters).fetchone()
    return row[0] if row else None


def profile_source(connection: sqlite3.Connection, metadata: dict[str, Any]) -> dict[str, Any]:
    table = "stg_delta_phi_spatial"
    scalar_queries = {
        "total_rows": f"SELECT COUNT(*) FROM {table}",
        "ordered_pairs": f"SELECT COUNT(*) FROM (SELECT DISTINCT pair_i,pair_j FROM {table})",
        "unordered_pairs": f"SELECT COUNT(*) FROM (SELECT DISTINCT min(pair_i,pair_j),max(pair_i,pair_j) FROM {table})",
        "states": f"SELECT COUNT(*) FROM (SELECT state_i AS state FROM {table} UNION SELECT state_j FROM {table})",
        "x_indices": f"SELECT COUNT(DISTINCT x_index) FROM {table}",
        "x_min": f"SELECT MIN(x_value) FROM {table}",
        "x_max": f"SELECT MAX(x_value) FROM {table}",
        "wrapped_min": f"SELECT MIN(wrapped_delta_phi_ij_x) FROM {table}",
        "wrapped_max": f"SELECT MAX(wrapped_delta_phi_ij_x) FROM {table}",
        "raw_min": f"SELECT MIN(raw_delta_phi_ij_x) FROM {table}",
        "raw_max": f"SELECT MAX(raw_delta_phi_ij_x) FROM {table}",
        "diagonal_rows": f"SELECT COUNT(*) FROM {table} WHERE pair_i=pair_j",
        "pair_mask_zero_rows": f"SELECT COUNT(*) FROM {table} WHERE pair_mask=0",
        "non_finite_rows": f"SELECT COUNT(*) FROM {table} WHERE raw_delta_phi_ij_x IS NULL OR wrapped_delta_phi_ij_x IS NULL OR x_value IS NULL OR raw_delta_phi_ij_x!=raw_delta_phi_ij_x OR wrapped_delta_phi_ij_x!=wrapped_delta_phi_ij_x OR x_value!=x_value OR abs(raw_delta_phi_ij_x)>1.7976931348623157e308 OR abs(wrapped_delta_phi_ij_x)>1.7976931348623157e308 OR abs(x_value)>1.7976931348623157e308",
        "outside_wrapped_interval_rows": f"SELECT COUNT(*) FROM {table} WHERE wrapped_delta_phi_ij_x < ? OR wrapped_delta_phi_ij_x >= ?",
        "non_rad_rows": f"SELECT COUNT(*) FROM {table} WHERE angle_unit!='rad'",
        "non_dimensionless_angle_rows": f"SELECT COUNT(*) FROM {table} WHERE dimension_status!='dimensionless_angle'",
        "non_model_length_unit_rows": f"SELECT COUNT(*) FROM {table} WHERE x_unit!='model_length_unit'",
    }
    result: dict[str, Any] = {}
    for name, query in scalar_queries.items():
        params = (-math.pi, math.pi) if name == "outside_wrapped_interval_rows" else ()
        result[name] = fetch_one(connection, query, params)
    result["metadata_spatial_rows"] = metadata.get("spatial_row_count")
    result["static_rows_actual"] = fetch_one(connection, "SELECT COUNT(*) FROM stg_delta_phi_static")
    result["input_hash"] = metadata.get("input_hash", "")
    return result


def coverage_rows(connection: sqlite3.Connection) -> list[dict[str, Any]]:
    query = """
        SELECT pair_i,pair_j,state_i,state_j,COUNT(*) AS row_count,
               COUNT(DISTINCT x_index) AS x_index_count,MIN(x_value) AS x_min,MAX(x_value) AS x_max,
               GROUP_CONCAT(DISTINCT pair_mask) AS pair_mask_values,
               GROUP_CONCAT(DISTINCT angle_unit) AS angle_unit_values,
               GROUP_CONCAT(DISTINCT dimension_status) AS dimension_status_values,
               GROUP_CONCAT(DISTINCT x_unit) AS x_unit_values,
               MIN(raw_delta_phi_ij_x) AS raw_min,MAX(raw_delta_phi_ij_x) AS raw_max,
               MIN(wrapped_delta_phi_ij_x) AS wrapped_min,MAX(wrapped_delta_phi_ij_x) AS wrapped_max
        FROM stg_delta_phi_spatial
        GROUP BY pair_i,pair_j,state_i,state_j ORDER BY pair_i,pair_j
    """
    return [dict(row) for row in connection.execute(query)]


def summary_rows(connection: sqlite3.Connection) -> list[dict[str, Any]]:
    query = """
        SELECT pair_i,pair_j,state_i,state_j,COUNT(*) AS row_count,
               AVG(raw_delta_phi_ij_x) AS raw_mean,
               AVG(raw_delta_phi_ij_x*raw_delta_phi_ij_x) AS raw_mean_square,
               MIN(raw_delta_phi_ij_x) AS raw_min,MAX(raw_delta_phi_ij_x) AS raw_max,
               AVG(wrapped_delta_phi_ij_x) AS wrapped_mean,
               AVG(wrapped_delta_phi_ij_x*wrapped_delta_phi_ij_x) AS wrapped_mean_square,
               MIN(wrapped_delta_phi_ij_x) AS wrapped_min,MAX(wrapped_delta_phi_ij_x) AS wrapped_max
        FROM stg_delta_phi_spatial
        GROUP BY pair_i,pair_j,state_i,state_j ORDER BY pair_i,pair_j
    """
    rows: list[dict[str, Any]] = []
    for source in connection.execute(query):
        row = dict(source)
        row["p_i_if_available"] = ""
        row["p_j_if_available"] = ""
        row["raw_std"] = math.sqrt(max(0.0, row.pop("raw_mean_square") - row["raw_mean"] ** 2))
        row["wrapped_std"] = math.sqrt(max(0.0, row.pop("wrapped_mean_square") - row["wrapped_mean"] ** 2))
        trig = connection.execute(
            "SELECT AVG(cos(wrapped_delta_phi_ij_x)),AVG(sin(wrapped_delta_phi_ij_x)),AVG(abs(cos(wrapped_delta_phi_ij_x))) FROM stg_delta_phi_spatial WHERE pair_i=? AND pair_j=?",
            (row["pair_i"], row["pair_j"]),
        ).fetchone()
        row["mean_cos_wrapped"], row["mean_sin_wrapped"], row["mean_abs_cos_wrapped"] = trig
        rows.append(row)
    return rows


def validation_rows(connection: sqlite3.Connection, metadata: dict[str, Any], profile: dict[str, Any], upstream_ok: bool) -> tuple[list[dict[str, Any]], bool]:
    tolerance = 1e-12
    raw_max_error, raw_bad = connection.execute(
        """SELECT MAX(abs(a.raw_delta_phi_ij_x+b.raw_delta_phi_ij_x)),
                  SUM(CASE WHEN abs(a.raw_delta_phi_ij_x+b.raw_delta_phi_ij_x)>? THEN 1 ELSE 0 END)
           FROM stg_delta_phi_spatial a JOIN stg_delta_phi_spatial b
             ON a.pair_i=b.pair_j AND a.pair_j=b.pair_i AND a.x_index=b.x_index""",
        (tolerance,),
    ).fetchone()
    wrapped_max_circular_error, wrapped_bad = connection.execute(
        """SELECT MAX(abs(atan2(sin(a.wrapped_delta_phi_ij_x+b.wrapped_delta_phi_ij_x),cos(a.wrapped_delta_phi_ij_x+b.wrapped_delta_phi_ij_x)))),
                  SUM(CASE WHEN abs(atan2(sin(a.wrapped_delta_phi_ij_x+b.wrapped_delta_phi_ij_x),cos(a.wrapped_delta_phi_ij_x+b.wrapped_delta_phi_ij_x)))>? THEN 1 ELSE 0 END)
           FROM stg_delta_phi_spatial a JOIN stg_delta_phi_spatial b
             ON a.pair_i=b.pair_j AND a.pair_j=b.pair_i AND a.x_index=b.x_index""",
        (tolerance,),
    ).fetchone()
    coverage_variants = fetch_one(
        connection,
        "SELECT COUNT(*) FROM (SELECT n,nx,lo,hi FROM (SELECT COUNT(*) n,COUNT(DISTINCT x_index) nx,MIN(x_index) lo,MAX(x_index) hi FROM stg_delta_phi_spatial GROUP BY pair_i,pair_j) GROUP BY n,nx,lo,hi)",
    )

    def check(check_name: str, passed: bool, observed: Any, expected: Any, notes: str) -> dict[str, Any]:
        return {
            "validation_id": f"G-VAL-{len(rows)+1:02d}", "check_name": check_name,
            "status": "pass" if passed else "fail", "observed": text(observed), "expected": text(expected),
            "blocking_for_next_design": "yes" if not passed else "no", "notes": notes,
        }

    rows: list[dict[str, Any]] = []
    rows.append(check("F3 metadata status ok", metadata.get("status") == EXPECTED_F3_STATUS and upstream_ok, metadata.get("status"), EXPECTED_F3_STATUS, "Includes required source-mode/export/count/hash preconditions."))
    rows.append(check("Spatial row count equals metadata row count", profile["total_rows"] == profile["metadata_spatial_rows"], profile["total_rows"], profile["metadata_spatial_rows"], "Actual staged rows compared with F3 metadata."))
    rows.append(check("Static rows zero", profile["static_rows_actual"] == 0, profile["static_rows_actual"], 0, "Spatial source mode contract."))
    rows.append(check("Diagonal rows zero", profile["diagonal_rows"] == 0, profile["diagonal_rows"], 0, "Diagonal policy is exclude."))
    rows.append(check("pair_mask false rows zero", profile["pair_mask_zero_rows"] == 0, profile["pair_mask_zero_rows"], 0, "Every staged off-diagonal row must be active."))
    rows.append(check("Wrapped values inside [-pi, pi)", profile["outside_wrapped_interval_rows"] == 0, profile["outside_wrapped_interval_rows"], 0, "Half-open wrapping interval."))
    rows.append(check("Raw ordered-pair antisymmetry", (raw_bad or 0) == 0, f"bad={raw_bad or 0};max_abs_error={text(raw_max_error)}", f"0 errors at tolerance {tolerance}", "Matched at equal x_index."))
    rows.append(check("Wrapped circular antisymmetry", (wrapped_bad or 0) == 0, f"bad={wrapped_bad or 0};max_circular_error={text(wrapped_max_circular_error)}", f"0 circular errors at tolerance {tolerance}", "Circular residual is used; exact linear antisymmetry can be discontinuous at wrap boundaries."))
    rows.append(check("x coverage identical across ordered pairs", coverage_variants == 1, coverage_variants, 1, "Compares row count, distinct x count, and x-index bounds."))
    label_bad = profile["non_rad_rows"] + profile["non_dimensionless_angle_rows"] + profile["non_model_length_unit_rows"]
    rows.append(check("Labels and units consistent", label_bad == 0, label_bad, 0, "Requires rad, dimensionless_angle, and model_length_unit."))
    rows.append(check("Input hash present and stable", bool(profile["input_hash"]) and fetch_one(connection, "SELECT COUNT(DISTINCT input_hash) FROM stg_delta_phi_spatial") == 1 and fetch_one(connection, "SELECT MIN(input_hash) FROM stg_delta_phi_spatial") == profile["input_hash"], profile["input_hash"], "one non-empty value equal to F3 metadata", "No source-hash substitution is allowed."))
    return rows, all(row["status"] == "pass" for row in rows)


def main() -> int:
    if OUTPUT.exists():
        raise SystemExit(f"Refusing to overwrite existing output directory: {OUTPUT}")
    if not SOURCE_DB.is_file():
        raise SystemExit(f"Required F3 staging database not found: {SOURCE_DB}")

    with sqlite3.connect(SOURCE_DB) as connection:
        connection.row_factory = sqlite3.Row
        tables = {row[0] for row in connection.execute("SELECT name FROM sqlite_master WHERE type='table'")}
        missing_tables = sorted(EXPECTED_TABLES - tables)
        if missing_tables:
            raise SystemExit(f"F3 staging database lacks required tables: {missing_tables}")
        metadata_rows = [dict(row) for row in connection.execute("SELECT * FROM stg_delta_phi_export_metadata")]
        if len(metadata_rows) != 1:
            raise SystemExit(f"Expected exactly one F3 metadata row, found {len(metadata_rows)}")
        metadata = metadata_rows[0]
        upstream_checks = {
            "status": metadata.get("status") == EXPECTED_F3_STATUS,
            "source_mode": metadata.get("source_mode") == "spatial_pair_delta_phi_x",
            "export_performed": metadata.get("export_performed") == 1,
            "static_row_count": metadata.get("static_row_count") == 0,
            "spatial_row_count": metadata.get("spatial_row_count") == 168042,
            "input_hash": bool(metadata.get("input_hash")),
        }
        upstream_ok = all(upstream_checks.values())
        profile = profile_source(connection, metadata) if upstream_ok else {}
        coverage = coverage_rows(connection) if upstream_ok else []
        summaries = summary_rows(connection) if upstream_ok else []
        validations, all_profile_checks_pass = validation_rows(connection, metadata, profile, upstream_ok) if upstream_ok else ([], False)

    status = SUCCESS_STATUS if upstream_ok and all_profile_checks_pass else BLOCKED_STATUS
    next_ready = status == SUCCESS_STATUS
    OUTPUT.mkdir(parents=True)

    manifest = {
        "work_package": "QSB-INTERFACE01G", "title": "INTERFACE01-G — Minimaltest Design Review from Staged delta_phi Source",
        "status": status, "created_at_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "source_db": str(SOURCE_DB.relative_to(REPO)), "source_table": "stg_delta_phi_spatial",
        "upstream_checks": upstream_checks, "real_staged_data_profiled": upstream_ok,
        "source_row_counts": {"spatial": profile.get("total_rows", 0), "static": profile.get("static_rows_actual", 0)},
        "profile_checks_passed": all_profile_checks_pass, "minimaltest_started": False,
        "g02_carry_forward": "resolved_authorized_export_staged" if upstream_ok else "blocked_upstream_validation_failed",
        "g13_carry_forward": "ready_for_minimaltest_design_not_started" if next_ready else "blocked_upstream_validation_failed",
        "seed_plan": 20260620, "claim_boundary": CLAIM_BOUNDARY,
        "modified_existing_files": [],
    }
    (OUTPUT / "01_g_run_manifest.json").write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    metadata_csv = []
    for key, value in metadata.items():
        expected = {"status": EXPECTED_F3_STATUS, "source_mode": "spatial_pair_delta_phi_x", "export_performed": 1, "static_row_count": 0, "spatial_row_count": 168042}.get(key, "recorded F3 value")
        metadata_csv.append({"metadata_field": key, "value": text(value), "expected_or_role": text(expected), "status": "pass" if key not in upstream_checks or upstream_checks[key] else "fail", "notes": "Read-only F3 staging metadata inspection."})
    write_csv(OUTPUT / "02_f3_source_metadata.csv", ["metadata_field", "value", "expected_or_role", "status", "notes"], metadata_csv)

    quality_notes = {
        "total_rows": "Staged spatial source rows.", "ordered_pairs": "Distinct directed pairs.", "unordered_pairs": "Canonical undirected pair keys.",
        "states": "Distinct labels across both pair endpoints.", "x_indices": "Distinct x indices.", "diagonal_rows": "Must be zero.",
        "pair_mask_zero_rows": "Must be zero.", "non_finite_rows": "Must be zero.", "outside_wrapped_interval_rows": "Must be zero.",
        "non_rad_rows": "Must be zero.", "non_dimensionless_angle_rows": "Must be zero.", "non_model_length_unit_rows": "Must be zero.",
    }
    quality = [{"metric": key, "value": text(value), "status": "profiled", "notes": quality_notes.get(key, "Descriptive staged-source profile only.")} for key, value in profile.items()]
    write_csv(OUTPUT / "03_staged_delta_phi_quality_profile.csv", ["metric", "value", "status", "notes"], quality)
    coverage_fields = ["pair_i", "pair_j", "state_i", "state_j", "row_count", "x_index_count", "x_min", "x_max", "pair_mask_values", "angle_unit_values", "dimension_status_values", "x_unit_values", "raw_min", "raw_max", "wrapped_min", "wrapped_max"]
    write_csv(OUTPUT / "04_pair_x_coverage_profile.csv", coverage_fields, coverage)
    summary_fields = ["pair_i", "pair_j", "state_i", "state_j", "p_i_if_available", "p_j_if_available", "row_count", "raw_mean", "raw_std", "raw_min", "raw_max", "wrapped_mean", "wrapped_std", "wrapped_min", "wrapped_max", "mean_cos_wrapped", "mean_sin_wrapped", "mean_abs_cos_wrapped"]
    write_csv(OUTPUT / "05_pair_phase_source_summary.csv", summary_fields, summaries)
    write_csv(OUTPUT / "06_symmetry_wrapping_validation.csv", ["validation_id", "check_name", "status", "observed", "expected", "blocking_for_next_design", "notes"], validations)

    contracts = [
        ("source_table", "stg_delta_phi_spatial"), ("source_mode", "spatial_pair_delta_phi_x"),
        ("allowed_input_hash", metadata.get("input_hash", "")), ("angle_unit", "rad"),
        ("dimension_status", "dimensionless_angle"), ("x_unit", "model_length_unit"),
        ("pair_diagonal_policy", "exclude"), ("ordered_pairs", "true"), ("expected_states", "7"),
        ("expected_ordered_pairs", "42"), ("expected_x_points", "4001"),
        ("source_claim_boundary", "source only, no physics claim"), ("minimaltest_execution_allowed_in_G", "no"),
    ]
    write_csv(OUTPUT / "07_minimaltest_input_contract.csv", ["contract_item", "value", "status", "notes"], [{"contract_item": k, "value": text(v), "status": "fixed" if next_ready else "blocked", "notes": "Contract for a later controlled pilot; not an outcome."} for k, v in contracts])

    previews = []
    for row in summaries:
        for feature in ["mean_cos_wrapped", "mean_sin_wrapped", "mean_abs_cos_wrapped", "wrapped_std", "raw_std"]:
            previews.append({"pair_i": row["pair_i"], "pair_j": row["pair_j"], "state_i": row["state_i"], "state_j": row["state_j"], "feature_set_id": "G_PREVIEW_V1", "feature_name": feature, "feature_value": text(row[feature]), "feature_unit_or_status": "dimensionless" if "cos" in feature or "sin" in feature else "rad", "claim_status": "non_evidential_design_preview_not_minimaltest_result", "notes": "Descriptive source-derived preview; no threshold or graph decision."})
    write_csv(OUTPUT / "08_candidate_feature_preview_non_evidential.csv", ["pair_i", "pair_j", "state_i", "state_j", "feature_set_id", "feature_name", "feature_value", "feature_unit_or_status", "claim_status", "notes"], previews)

    null_specs = [
        ("N01", "N01_phase_shuffle_within_x", "phase values within each x slice", "x-wise marginal distribution", "state-phase correspondence"),
        ("N02", "N02_pair_label_permutation", "ordered pair labels", "feature values and x grid", "pair identity association"),
        ("N03", "N03_x_order_reversal", "x sequence within each pair", "pair values and x support", "forward x ordering"),
        ("N04", "N04_phase_sign_flip", "raw phase differences", "absolute phase scale", "phase orientation"),
        ("N05", "N05_circular_phase_shift", "wrapped phase sequence per pair", "periodicity and within-pair sequence", "absolute x alignment"),
        ("N06", "N06_independent_pair_resample", "ordered-pair phase sequences", "per-pair empirical support", "cross-pair dependence"),
    ]
    null_rows = [{"null_model_id": i, "null_model_name": n, "input_scope": scope, "preserves": preserves, "breaks": breaks, "seed_policy": "locked seed 20260620 with deterministic sub-seed by null_model_id", "required_for_next_minimaltest": "yes", "notes": "design_required; no nullmodel data generated in G"} for i, n, scope, preserves, breaks in null_specs]
    write_csv(OUTPUT / "09_null_model_design_matrix.csv", ["null_model_id", "null_model_name", "input_scope", "preserves", "breaks", "seed_policy", "required_for_next_minimaltest", "notes"], null_rows)

    split_rows = [{"split_name": name, "fraction_target": fraction, "unit_of_split": "ordered_pair", "seed": 20260620, "assignment_method": "deterministic seeded assignment after human approval", "status": "design_fixed_assignment_not_run", "notes": "Pair-level split prevents shared x-grid rows from crossing splits; no final pair keys assigned in G."} for name, fraction in [("train_design_40", "0.40"), ("calibration_30", "0.30"), ("validation_20", "0.20"), ("holdout_10", "0.10")]]
    write_csv(OUTPUT / "10_split_seed_plan.csv", ["split_name", "fraction_target", "unit_of_split", "seed", "assignment_method", "status", "notes"], split_rows)

    calibration_rows = [
        ("theta_new", "pre-registered candidate grid", "calibration split only", "quantile pre-registration plus nullmodel-informed margin", "outcome optimization or holdout peeking", "design_required", "No value selected in G."),
        ("epsilon_new", "numerical tolerance audit", "train-design then calibration split", "pre-register precision/margin rule before validation", "post-hoc tightening to change outcomes", "design_required", "No value selected in G."),
        ("R01", "candidate relation threshold rule", "calibration split only", "apply pre-registered theta_new rule", "selection from validation or holdout outcomes", "design_required", "Relation rule remains unexecuted."),
        ("R02", "margin audit rule", "calibration then locked validation", "nullmodel-informed margin and explicit boundary audit", "discarding near-threshold cases post hoc", "design_required", "Margin audit remains unexecuted."),
        ("old Phase-D theta guardrail", "theta=0.0300 from Phase D", "none", "record solely as forbidden legacy reference", "direct transfer into INTERFACE01", "forbidden_direct_transfer", "theta=0.0300 from Phase D is forbidden as direct transfer."),
    ]
    write_csv(OUTPUT / "11_theta_epsilon_calibration_plan.csv", ["parameter", "candidate_source", "calibration_scope", "allowed_method", "forbidden_method", "status", "notes"], [{"parameter": a, "candidate_source": b, "calibration_scope": c, "allowed_method": d, "forbidden_method": e, "status": f, "notes": g} for a, b, c, d, e, f, g in calibration_rows])

    decision = [{"decision_item": "INTERFACE01-G status", "status": status, "allowed_next_action": "INTERFACE01-H small controlled Minimaltest pilot design/implementation, not broad execution" if next_ready else "resolve listed G validation failures before any pilot", "forbidden_next_action": "running the Minimaltest inside G; claiming physics evidence; post-hoc tuning", "notes": "All required G profile checks passed." if next_ready else "One or more required checks failed; see 06_symmetry_wrapping_validation.csv."}]
    write_csv(OUTPUT / "12_next_action_decision.csv", ["decision_item", "status", "allowed_next_action", "forbidden_next_action", "notes"], decision)

    note = f"""# INTERFACE01-G Final Result

## Status
`{status}`

## Befund
- Real staged data flowed through G profiling: `{'yes' if upstream_ok else 'no'}`.
- Source rows: spatial `{profile.get('total_rows', 0)}`, static `{profile.get('static_rows_actual', 0)}`.
- F3 source passed all G profile checks: `{'yes' if all_profile_checks_pass else 'no'}`.
- `p_i` and `p_j` are not stored in F3 staging rows; their summary columns remain empty.
- No Minimaltest was run.

## Interpretation
The staged source is {'ready for the narrowly scoped next design step' if next_ready else 'not ready for a downstream pilot'}; previews are descriptive and non-evidential.

## Hypothese
No physical hypothesis was tested in G.

## Offene Luecke
The pair-level split assignment, nullmodel generation, and theta/epsilon calibration remain unexecuted.

## Gates und naechste Aktion
- G02: `{'resolved_authorized_export_staged' if upstream_ok else 'blocked_upstream_validation_failed'}`.
- G13: `{'ready_for_minimaltest_design_not_started' if next_ready else 'blocked_upstream_validation_failed'}`.
- Next allowed action: `{'INTERFACE01-H small controlled Minimaltest pilot design/implementation, not broad execution' if next_ready else 'resolve G validation failures'}`.

## Claim Boundary
{CLAIM_BOUNDARY}
"""
    (OUTPUT / "FINAL_RESULT_NOTE.md").write_text(note, encoding="utf-8")
    print(f"status={status}")
    print(f"output={OUTPUT}")
    return 0 if next_ready else 2


if __name__ == "__main__":
    raise SystemExit(main())
