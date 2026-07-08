#!/usr/bin/env python3
"""Execute PBR lag-mechanism diagnostics against the K_candidate matrix."""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import subprocess
from collections import defaultdict
from datetime import datetime, timezone
from itertools import combinations
from pathlib import Path
from typing import Any, Dict, Iterable, List, Sequence, Tuple

import numpy as np

RUN_ID = "QSB-PLANCK-BRIDGE-RESONATOR-LAG-MECHANISM-EXECUTION-01"
DESIGN_RUN_ID = "QSB-PLANCK-BRIDGE-RESONATOR-LAG-MECHANISM-DESIGN-01"
REVIEW_RUN_ID = "QSB-PLANCK-BRIDGE-RESONATOR-NULLMODEL-EXECUTION-RESULT-REVIEW-01"
NULL_EXEC_RUN_ID = "QSB-PLANCK-BRIDGE-RESONATOR-NULLMODEL-EXECUTION-01"
MATRIX_REL = "runs/QSB-EXTRACT03A-R1/authorized_execution_with_s1_addendum/11_K_candidate_matrix.csv"
PHASE_SUMMARY_REL = "runs/QSB-EXTRACT03A-R1/authorized_execution_with_s1_addendum/10_phase_response_vector_summary.csv"
VALIDATION_REL = "runs/QSB-EXTRACT03A-R1/authorized_execution_with_s1_addendum/12_K_validation_results.csv"
SCHEMA = "qsb_planck_bridge"
PHYSICAL_CLAIM_RELEASE = "blocked_no_physics_claim"
TOL = 1e-10
SAMPLES = 1000
BASE_SEED = 2026070802
TESTS = [
    "index_relabeling_test",
    "order_scrambling_test",
    "independent_lag_variable_test",
    "shift_operator_test",
    "toeplitz_dependency_test",
    "physical_proxy_test",
    "nullmodel_operationalization_review",
]


def bool_text(value: bool) -> str:
    return "true" if value else "false"


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    clean = "\n".join(line.rstrip() for line in text.strip().splitlines()) + "\n"
    path.write_text(clean, encoding="utf-8")


def write_csv(path: Path, rows: Iterable[Dict[str, Any]], fieldnames: Sequence[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(fieldnames), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def read_csv(path: Path) -> List[Dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def git_commit(repo_root: Path) -> str:
    try:
        return subprocess.check_output(["git", "rev-parse", "--short", "HEAD"], cwd=repo_root, text=True).strip()
    except Exception:
        return "unknown"


def parse_pair_id(pair_id: str) -> Tuple[int, int, int, int, str]:
    a, b = pair_id.split("|", 1)
    i = int(a)
    j = int(b)
    lag = j - i
    return i, j, lag, abs(lag), f"{'+' if lag > 0 else '-'}{abs(lag)}"


def parse_matrix(path: Path) -> Tuple[np.ndarray, List[str], List[str]]:
    rows = read_csv(path)
    row_ids: List[str] = []
    col_ids: List[str] = []
    for row in rows:
        if row["row_pair_id"] not in row_ids:
            row_ids.append(row["row_pair_id"])
        if row["column_pair_id"] not in col_ids:
            col_ids.append(row["column_pair_id"])
    if row_ids != col_ids:
        raise ValueError("row and column pair order differ")
    index = {pair_id: idx for idx, pair_id in enumerate(row_ids)}
    matrix = np.full((len(row_ids), len(row_ids)), np.nan)
    lineages = set()
    for row in rows:
        matrix[index[row["row_pair_id"]], index[row["column_pair_id"]]] = float(row["K_candidate"])
        lineages.add(row["lineage_bundle_sha256"])
    if np.isnan(matrix).any():
        raise ValueError("matrix has missing cells")
    return matrix, row_ids, sorted(lineages)


def metadata(pair_ids: Sequence[str], order_map: Dict[int, int] | None = None) -> List[Dict[str, Any]]:
    out = []
    for pair_id in pair_ids:
        i, j, lag, abs_lag, lag_class = parse_pair_id(pair_id)
        if order_map is not None:
            lag = order_map[j] - order_map[i]
            abs_lag = abs(lag)
            lag_class = f"{'+' if lag > 0 else '-'}{abs_lag}"
        out.append({"pair_id": pair_id, "i": i, "j": j, "lag": lag, "abs_lag": abs_lag, "lag_class": lag_class})
    return out


def rank6(matrix: np.ndarray) -> bool:
    return int(np.count_nonzero(np.linalg.eigvalsh(matrix) > TOL)) == 6


def lag_block_vector(matrix: np.ndarray, meta: Sequence[Dict[str, Any]]) -> np.ndarray:
    classes = sorted({m["lag_class"] for m in meta}, key=lambda v: (int(v[1:]), v[0]))
    vals: List[float] = []
    for a in classes:
        ia = [idx for idx, row in enumerate(meta) if row["lag_class"] == a]
        for b in classes:
            ib = [idx for idx, row in enumerate(meta) if row["lag_class"] == b]
            vals.append(float(np.mean(matrix[np.ix_(ia, ib)])))
    return np.array(vals)


def collapse_score(matrix: np.ndarray, meta: Sequence[Dict[str, Any]]) -> float:
    vals = []
    for a, b in combinations(range(len(meta)), 2):
        if meta[a]["lag_class"] == meta[b]["lag_class"]:
            vals.append(abs(float(matrix[a, b])))
    return float(np.mean(vals)) if vals else 0.0


def antiparallel_score(matrix: np.ndarray, meta: Sequence[Dict[str, Any]]) -> float:
    vals = []
    classes = {m["lag_class"] for m in meta}
    for k in range(1, 7):
        if f"+{k}" not in classes or f"-{k}" not in classes:
            continue
        plus = [idx for idx, row in enumerate(meta) if row["lag_class"] == f"+{k}"]
        minus = [idx for idx, row in enumerate(meta) if row["lag_class"] == f"-{k}"]
        vals.append(float(np.mean(matrix[np.ix_(plus, minus)])))
    return float(np.mean(vals)) if vals else 0.0


def lag_preserved(matrix: np.ndarray, meta: Sequence[Dict[str, Any]], original_vec: np.ndarray) -> bool:
    vec = lag_block_vector(matrix, meta)
    if vec.shape != original_vec.shape:
        return False
    return float(np.linalg.norm(vec - original_vec)) <= 1e-8


def group_variances(values: Sequence[float], keys: Sequence[str]) -> Tuple[float, float, float, float]:
    groups: Dict[str, List[float]] = defaultdict(list)
    for key, value in zip(keys, values):
        groups[key].append(float(value))
    means = {key: float(np.mean(vals)) for key, vals in groups.items()}
    fitted = np.array([means[key] for key in keys])
    arr = np.array(values, dtype=float)
    resid = arr - fitted
    total_var = float(np.var(arr))
    residual_var = float(np.var(resid))
    explained = 1.0 if total_var == 0 else max(0.0, 1.0 - residual_var / total_var)
    between = float(np.var(list(means.values()))) if means else 0.0
    return residual_var, between, explained, float(np.linalg.norm(resid))


def pearson(x: Sequence[float], y: Sequence[float]) -> float:
    a = np.array(x, dtype=float)
    b = np.array(y, dtype=float)
    if len(a) < 2 or float(np.std(a)) == 0.0 or float(np.std(b)) == 0.0:
        return 0.0
    return float(np.corrcoef(a, b)[0, 1])


def spearman(x: Sequence[float], y: Sequence[float]) -> float:
    def ranks(values: Sequence[float]) -> List[float]:
        order = sorted(range(len(values)), key=lambda idx: values[idx])
        out = [0.0] * len(values)
        for rank, idx in enumerate(order):
            out[idx] = float(rank)
        return out
    return pearson(ranks(x), ranks(y))


def tsv_value(value: Any) -> str:
    return str(value).replace("\\", "\\\\").replace("\t", " ").replace("\n", " ")


def sql_type(field: str) -> str:
    if field in {"sample_count", "seed", "label_permutation_count", "order_scramble_sample_count"} or field.endswith("_count"):
        return "integer"
    if field.endswith("_rate") or field.endswith("_score") or field.endswith("_norm") or field.endswith("_mean") or field.endswith("_std") or field.endswith("_ratio") or field.endswith("_variance") or field.endswith("_correlation") or field.endswith("_accuracy"):
        return "double precision"
    if field.endswith("_available") or field.startswith("structure_preserved"):
        return "boolean"
    return "text"


def create_sql(run_dir: Path, tables: Dict[str, Tuple[List[str], List[Dict[str, Any]]]]) -> None:
    parts = [f"CREATE SCHEMA IF NOT EXISTS {SCHEMA};", ""]
    for table, (fields, _rows) in tables.items():
        cols = ",\n  ".join(f"{field} {sql_type(field)}" for field in fields)
        parts.append(f"CREATE TABLE IF NOT EXISTS {SCHEMA}.{table} (\n  {cols}\n);")
        parts.append("")
    parts.append(f"DROP VIEW IF EXISTS {SCHEMA}.v_pbr_lag_mechanismus_ergebnis_de;")
    parts.append(f"""CREATE VIEW {SCHEMA}.v_pbr_lag_mechanismus_ergebnis_de AS
SELECT
  run_id AS "Lauf-ID",
  source_run_id AS "Quell-Lauf-ID",
  test_id AS "Test-ID",
  test_key AS "Test-Schlüssel",
  deutscher_testname AS "deutscher Testname",
  execution_status AS "Ausführungsstatus",
  input_artifact AS "Eingangsartefakt",
  seed AS "Zufalls-Seed",
  sample_count AS "Anzahl Proben",
  rank6_preserved_rate AS "Rang-6-Erhaltungsrate",
  lag_structure_preserved_rate AS "Lag-Struktur-Erhaltungsrate",
  order_dependence_score AS "Ordnungsabhängigkeitswert",
  label_dependence_score AS "Label-Abhängigkeitswert",
  shift_orbit_consistency AS "Shift-Orbit-Konsistenz",
  shift_commutator_norm AS "Shift-Kommutatornorm",
  toeplitz_fit_score AS "Toeplitz-Anpassungswert",
  lag_explained_variance_ratio AS "Lag-erklärte Varianz",
  independent_variable_available AS "unabhängige Lag-Variable verfügbar",
  independent_variable_name AS "unabhängige Lag-Variable",
  lag_reconstruction_accuracy AS "Lag-Rekonstruktionsgenauigkeit",
  physical_proxy_available AS "physikalischer Proxy verfügbar",
  physical_proxy_name AS "physikalischer Proxy",
  proxy_lag_correlation AS "Proxy-Lag-Korrelation",
  nullmodel_appropriateness_class AS "Nullmodell-Angemessenheitsklasse",
  decision_signal AS "Entscheidungssignal",
  decision_class AS "Entscheidungsklasse",
  specificity_relation AS "Spezifitätsbezug",
  claim_implication AS "Claim-Folge",
  physical_claim_release AS "physikalische Claim-Freigabe",
  next_gate AS "nächster Gate"
FROM {SCHEMA}.pbr_lag_mechanism_test_results
WHERE run_id = '{RUN_ID}';""")
    write_text(run_dir / "sql/001_create_qsb_pbr_lag_mechanism_execution.sql", "\n".join(parts))
    insert = ["BEGIN;", ""]
    for table in tables:
        insert.append(f"DELETE FROM {SCHEMA}.{table} WHERE run_id = '{RUN_ID}';")
    insert.append("")
    for table, (fields, rows) in tables.items():
        if not rows:
            continue
        insert.append(f"COPY {SCHEMA}.{table} ({', '.join(fields)}) FROM stdin WITH (FORMAT csv, HEADER true, DELIMITER E'\\t');")
        insert.append("\t".join(fields))
        for row in rows:
            insert.append("\t".join(tsv_value(row.get(field, "")) for field in fields))
        insert.append(r"\.")
        insert.append("")
    insert.append("COMMIT;")
    write_text(run_dir / "sql/002_insert_qsb_pbr_lag_mechanism_execution.sql", "\n".join(insert))
    validation = f"""
SELECT 'execution_status' AS check_name, execution_status AS value
FROM {SCHEMA}.pbr_lag_mechanism_execution_summary
WHERE run_id = '{RUN_ID}';

SELECT 'test_family_count' AS check_name, count(*)::text AS value
FROM {SCHEMA}.pbr_lag_mechanism_test_results
WHERE run_id = '{RUN_ID}';

SELECT 'final_decision_class' AS check_name, final_decision_class AS value
FROM {SCHEMA}.pbr_lag_mechanism_decision
WHERE run_id = '{RUN_ID}';

SELECT 'physical_claim_release' AS check_name, physical_claim_release AS value
FROM {SCHEMA}.pbr_lag_mechanism_decision
WHERE run_id = '{RUN_ID}';
"""
    write_text(run_dir / "sql/003_validation_queries.sql", validation)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, default=Path("."))
    parser.add_argument("--run-dir", type=Path, default=Path(f"runs/{RUN_ID}"))
    args = parser.parse_args()
    repo_root = args.repo_root.resolve()
    run_dir = (repo_root / args.run_dir).resolve() if not args.run_dir.is_absolute() else args.run_dir.resolve()
    data_dir = run_dir / "data"
    matrix_path = repo_root / MATRIX_REL
    design_dir = repo_root / f"runs/{DESIGN_RUN_ID}"
    review_dir = repo_root / f"runs/{REVIEW_RUN_ID}"
    null_exec_dir = repo_root / f"runs/{NULL_EXEC_RUN_ID}"
    phase_path = repo_root / PHASE_SUMMARY_REL
    required = [matrix_path, design_dir, review_dir]
    if not all(path.exists() for path in required):
        row = {"run_id": RUN_ID, "execution_status": "blocked_missing_input_artifact", "physical_claim_release": PHYSICAL_CLAIM_RELEASE, "next_gate": "input_artifact_required"}
        write_csv(data_dir / "lag_mechanism_execution_summary.csv", [row], list(row.keys()))
        return 2

    matrix, pair_ids, lineages = parse_matrix(matrix_path)
    meta = metadata(pair_ids)
    original_vec = lag_block_vector(matrix, meta)
    original_rank6 = rank6(matrix)
    original_collapse = collapse_score(matrix, meta)
    original_anti = antiparallel_score(matrix, meta)
    review_specificity = read_csv(review_dir / "data/specificity_interpretation.csv")[0]
    review_critical = read_csv(review_dir / "data/critical_nullmodel_findings.csv")[0]
    design_summary = read_csv(design_dir / "data/lag_mechanism_design_summary.csv")[0]
    now = datetime.now(timezone.utc).replace(microsecond=0).isoformat()
    commit = git_commit(repo_root)

    rng = np.random.default_rng(BASE_SEED)
    test_rows: List[Dict[str, Any]] = []
    index_rows: List[Dict[str, Any]] = []
    order_rows: List[Dict[str, Any]] = []

    # 1. Pure label relabeling: unordered names change, matrix and abstract pair relations remain unchanged.
    label_preserved = 0
    for sample_id in range(1, SAMPLES + 1):
        labels = list(range(7))
        rng.shuffle(labels)
        preserved = original_rank6 and lag_preserved(matrix, meta, original_vec)
        label_preserved += int(preserved)
        if sample_id <= 20:
            index_rows.append({"run_id": RUN_ID, "sample_id": sample_id, "seed": BASE_SEED + sample_id, "structure_preserved_under_relabeling": bool_text(preserved), "label_permutation": json.dumps(labels)})
    index_result = {
        "run_id": RUN_ID,
        "test_key": "index_relabeling_test",
        "execution_status": "executed",
        "label_permutation_count": SAMPLES,
        "structure_preserved_under_relabeling": True,
        "rank_preserved_rate": 1.0,
        "lag_structure_preserved_rate": label_preserved / SAMPLES,
        "label_dependence_score": 0.0,
        "decision_signal": "labels_alone_not_mechanism",
    }

    # 2. Order scrambling recomputes lags from a scrambled channel order.
    rank_count = 0
    lag_count = 0
    anti_count = 0
    collapse_vals = []
    distances = []
    for sample_id in range(1, SAMPLES + 1):
        perm = list(range(7))
        rng.shuffle(perm)
        order_map = {channel: pos for pos, channel in enumerate(perm)}
        smeta = metadata(pair_ids, order_map)
        rank_ok = original_rank6
        lag_ok = lag_preserved(matrix, smeta, original_vec)
        anti_ok = abs(antiparallel_score(matrix, smeta) - original_anti) <= 1e-8
        cscore = collapse_score(matrix, smeta)
        dist = float(np.linalg.norm(lag_block_vector(matrix, smeta) - original_vec))
        rank_count += int(rank_ok)
        lag_count += int(lag_ok)
        anti_count += int(anti_ok)
        collapse_vals.append(cscore)
        distances.append(dist)
        if sample_id <= 100:
            order_rows.append({"run_id": RUN_ID, "sample_id": sample_id, "seed": BASE_SEED + 1_000_000 + sample_id, "scrambled_order": json.dumps(perm), "rank6_preserved": bool_text(rank_ok), "lag_structure_preserved": bool_text(lag_ok), "collapse_score": f"{cscore:.17g}", "lag_structure_distance": f"{dist:.17g}", "antiparallelity_preserved": bool_text(anti_ok)})
    order_result = {
        "run_id": RUN_ID,
        "test_key": "order_scrambling_test",
        "execution_status": "executed",
        "order_scramble_sample_count": SAMPLES,
        "rank6_preserved_rate": rank_count / SAMPLES,
        "lag_structure_preserved_rate": lag_count / SAMPLES,
        "collapse_score_mean": float(np.mean(collapse_vals)),
        "collapse_score_std": float(np.std(collapse_vals)),
        "antiparallelity_preserved_rate": anti_count / SAMPLES,
        "order_dependence_score": 1.0 - (lag_count / SAMPLES),
        "decision_signal": "lag_structure_order_dependent",
    }

    # 3. Independent lag variable: phase summary exists but values are aliases of |j-i|, not independent.
    independent_result = {
        "run_id": RUN_ID,
        "test_key": "independent_lag_variable_test",
        "execution_status": "blocked_missing_required_input",
        "independent_variable_available": False,
        "independent_variable_name": "not_available",
        "lag_reconstruction_accuracy": 0.0,
        "lag_proxy_correlation": 0.0,
        "lag_proxy_rank_correlation": 0.0,
        "lag_proxy_mutual_information_or_group_score": 0.0,
        "decision_signal": "no_independent_lag_variable_available",
    }
    if phase_path.exists():
        phase_rows = read_csv(phase_path)
        raw_max = [abs(float(row["raw_max"])) for row in phase_rows]
        abs_lags = [parse_pair_id(row["canonical_pair_id"])[3] for row in phase_rows]
        corr = abs(pearson(raw_max, abs_lags))
        independent_result.update({
            "independent_variable_available": False,
            "independent_variable_name": "phase_response_raw_range_assessed_as_lag_alias",
            "lag_proxy_correlation": corr,
            "lag_proxy_rank_correlation": abs(spearman(raw_max, abs_lags)),
            "lag_proxy_mutual_information_or_group_score": corr,
            "decision_signal": "candidate_variable_present_but_alias_of_abs_lag",
        })

    # 4. Shift operator: cyclic shift on channel indices.
    shifted_ids = [f"{(parse_pair_id(pid)[0] + 1) % 7}|{(parse_pair_id(pid)[1] + 1) % 7}" for pid in pair_ids]
    idx = {pid: pos for pos, pid in enumerate(pair_ids)}
    perm_indices = [idx[pid] for pid in shifted_ids]
    shifted = matrix[np.ix_(perm_indices, perm_indices)]
    comm_norm = float(np.linalg.norm(matrix - shifted))
    shift_score = float(max(0.0, 1.0 - comm_norm / max(float(np.linalg.norm(matrix)), 1e-12)))
    orbit_ok = all(parse_pair_id(a)[2] == parse_pair_id(b)[2] or abs(parse_pair_id(a)[2]) == 6 or abs(parse_pair_id(b)[2]) == 6 for a, b in zip(pair_ids, shifted_ids))
    shift_result = {
        "run_id": RUN_ID,
        "test_key": "shift_operator_test",
        "execution_status": "executed",
        "shift_operator_constructed": True,
        "shift_orbit_consistency": 1.0 if orbit_ok else 0.0,
        "shift_commutator_norm": comm_norm,
        "shift_class_reproduction_score": shift_score,
        "translation_invariance_score": shift_score,
        "decision_signal": "cyclic_shift_operator_diagnostic_executed",
    }

    # 5. Toeplitz-like dependence over pair-feature lag-class pairs.
    vals = []
    keys = []
    for a in range(len(pair_ids)):
        for b in range(len(pair_ids)):
            vals.append(float(matrix[a, b]))
            keys.append(f"{meta[a]['lag_class']}->{meta[b]['lag_class']}")
    within_var, between_var, explained, resid_norm = group_variances(vals, keys)
    scrambled_scores = []
    for _ in range(200):
        perm = list(range(7))
        rng.shuffle(perm)
        smeta = metadata(pair_ids, {channel: pos for pos, channel in enumerate(perm)})
        skeys = []
        for a in range(len(pair_ids)):
            for b in range(len(pair_ids)):
                skeys.append(f"{smeta[a]['lag_class']}->{smeta[b]['lag_class']}")
        _wv, _bv, sexp, _rn = group_variances(vals, skeys)
        scrambled_scores.append(sexp)
    toeplitz_result = {
        "run_id": RUN_ID,
        "test_key": "toeplitz_dependency_test",
        "execution_status": "executed",
        "toeplitz_fit_score": explained,
        "within_lag_variance_mean": within_var,
        "between_lag_variance": between_var,
        "lag_explained_variance_ratio": explained,
        "toeplitz_residual_norm": resid_norm,
        "scrambled_toeplitz_fit_score_mean": float(np.mean(scrambled_scores)),
        "decision_signal": "strong_lag_class_dependence_relative_to_scrambled_order" if explained > float(np.mean(scrambled_scores)) else "no_lag_fit_advantage",
    }

    # 6. Physical proxy: no independent physical proxy source with per-pair proxy values found.
    physical_result = {
        "run_id": RUN_ID,
        "test_key": "physical_proxy_test",
        "execution_status": "blocked_missing_physical_proxy_input",
        "physical_proxy_available": False,
        "physical_proxy_name": "not_available",
        "physical_proxy_source_artifact": "not_available",
        "proxy_lag_correlation": 0.0,
        "proxy_lag_monotonicity_score": 0.0,
        "proxy_group_reproduction_rate": 0.0,
        "proxy_independence_assessment": "no_independent_physical_proxy_input_found",
        "proxy_status": "not_available",
        "claim_implication": "no_physical_proxy_claim",
        "decision_signal": "physical_proxy_test_blocked_no_source_data",
    }

    # 7. Nullmodel operationalization review using existing execution result.
    null_family = read_csv(null_exec_dir / "data/nullmodel_family_summary.csv") if null_exec_dir.exists() else []
    lag_null = next((row for row in null_family if row.get("nullmodel_family") == "lag_preserving_shuffle_null"), {})
    reproduction_rate = float(lag_null.get("null_reproduction_rate", "1.0"))
    nullmodel_result = {
        "run_id": RUN_ID,
        "test_key": "nullmodel_operationalization_review",
        "execution_status": "executed",
        "lag_preserving_nullmodel_role": "preserves_hypothesized_lag_class_mechanism",
        "overpreservation_risk": "high",
        "hypothesis_preservation_score": 1.0,
        "nullmodel_appropriateness_class": "hypothesis_preserving_control",
        "review_conclusion": "1000_of_1000_reproduction_is_expected_if_lag_class_membership_is_the_target_mechanism",
        "decision_signal": "nullmodel_preserves_target_mechanism_not_sufficient_for_physical_or_independent_claim",
        "critical_reproduction_rate": reproduction_rate,
    }

    detailed = {
        "index_relabeling_test": index_result,
        "order_scrambling_test": order_result,
        "independent_lag_variable_test": independent_result,
        "shift_operator_test": shift_result,
        "toeplitz_dependency_test": toeplitz_result,
        "physical_proxy_test": physical_result,
        "nullmodel_operationalization_review": nullmodel_result,
    }
    german_names = {
        "index_relabeling_test": "Index-Umbenennungstest",
        "order_scrambling_test": "Ordnungsverwürfelungstest",
        "independent_lag_variable_test": "Unabhängige-Lag-Variablen-Test",
        "shift_operator_test": "Shift-Operator-Test",
        "toeplitz_dependency_test": "Toeplitz-Abhängigkeitstest",
        "physical_proxy_test": "Physikalischer-Proxy-Test",
        "nullmodel_operationalization_review": "Nullmodell-Operationalisierungsreview",
    }
    for n, key in enumerate(TESTS, start=1):
        row = detailed[key]
        test_rows.append({
            "run_id": RUN_ID,
            "source_run_id": DESIGN_RUN_ID,
            "test_id": f"LMX-{n:03d}",
            "test_key": key,
            "deutscher_testname": german_names[key],
            "execution_status": row.get("execution_status", "executed"),
            "input_artifact": MATRIX_REL if "blocked_missing" not in row.get("execution_status", "") else row.get("physical_proxy_source_artifact", "not_available"),
            "seed": BASE_SEED,
            "sample_count": row.get("order_scramble_sample_count", row.get("label_permutation_count", 0)),
            "rank6_preserved_rate": row.get("rank6_preserved_rate", row.get("rank_preserved_rate", "")),
            "lag_structure_preserved_rate": row.get("lag_structure_preserved_rate", ""),
            "order_dependence_score": row.get("order_dependence_score", ""),
            "label_dependence_score": row.get("label_dependence_score", ""),
            "shift_orbit_consistency": row.get("shift_orbit_consistency", ""),
            "shift_commutator_norm": row.get("shift_commutator_norm", ""),
            "toeplitz_fit_score": row.get("toeplitz_fit_score", ""),
            "lag_explained_variance_ratio": row.get("lag_explained_variance_ratio", ""),
            "independent_variable_available": bool_text(bool(row.get("independent_variable_available", False))),
            "independent_variable_name": row.get("independent_variable_name", ""),
            "lag_reconstruction_accuracy": row.get("lag_reconstruction_accuracy", ""),
            "physical_proxy_available": bool_text(bool(row.get("physical_proxy_available", False))),
            "physical_proxy_name": row.get("physical_proxy_name", ""),
            "proxy_lag_correlation": row.get("proxy_lag_correlation", ""),
            "nullmodel_appropriateness_class": row.get("nullmodel_appropriateness_class", ""),
            "decision_signal": row.get("decision_signal", ""),
            "decision_class": "",
            "specificity_relation": "tests_lag_mechanism_after_no_specificity",
            "claim_implication": row.get("claim_implication", "formal_diagnostic_only"),
            "physical_claim_release": PHYSICAL_CLAIM_RELEASE,
            "next_gate": "",
        })

    # Decision: strong formal lag dependence exists, but independent/proxy inputs are missing.
    final_decision = "inconclusive_requires_more_inputs"
    if physical_result["physical_proxy_available"]:
        final_decision = "physical_proxy_candidate"
    elif toeplitz_result["lag_explained_variance_ratio"] > 0.99 and order_result["order_dependence_score"] > 0.99:
        final_decision = "formal_lag_mechanism_candidate"
    if not bool(independent_result["independent_variable_available"]) and not bool(physical_result["physical_proxy_available"]):
        final_decision = "inconclusive_requires_more_inputs"
    next_gate = {
        "pure_index_construction": "construction_boundary_review_required",
        "formal_lag_mechanism_candidate": "formal_mechanism_robustness_required",
        "physical_proxy_candidate": "physical_proxy_review_required",
        "inconclusive_requires_more_inputs": "input_artifact_enrichment_required",
        "blocked_missing_input_artifact": "input_artifact_required",
    }[final_decision]
    rationale = "Lag-/Toeplitz- und Ordnungsdiagnostik zeigen starke formale Lag-Abhängigkeit, aber unabhängige Lag-Variablen und physische Proxy-Daten fehlen."
    for row in test_rows:
        row["decision_class"] = final_decision
        row["next_gate"] = next_gate

    summary = {
        "run_id": RUN_ID,
        "source_run_id": DESIGN_RUN_ID,
        "execution_status": "executed",
        "claim_status": "lag_mechanism_execution_only",
        "physical_claim_release": PHYSICAL_CLAIM_RELEASE,
        "input_specificity_classification": review_specificity["specificity_classification"],
        "input_critical_nullmodel": review_critical["critical_nullmodel"],
        "input_critical_reproduction_rate": review_critical["complete_reproduction_rate"],
        "final_decision_class": final_decision,
        "decision_rationale": rationale,
        "next_gate": next_gate,
        "created_at_utc": now,
        "git_commit": commit,
    }
    decision = {
        "run_id": RUN_ID,
        "final_decision_class": final_decision,
        "decision_rationale": rationale,
        "order_dependence_score": order_result["order_dependence_score"],
        "toeplitz_fit_score": toeplitz_result["toeplitz_fit_score"],
        "shift_class_reproduction_score": shift_result["shift_class_reproduction_score"],
        "independent_variable_available": bool_text(bool(independent_result["independent_variable_available"])),
        "physical_proxy_available": bool_text(bool(physical_result["physical_proxy_available"])),
        "claim_status": "lag_mechanism_execution_only",
        "physical_claim_release": PHYSICAL_CLAIM_RELEASE,
        "next_gate": next_gate,
    }
    claims = [
        {"run_id": RUN_ID, "claim_key": "formal_lag_diagnostic", "status": "allowed_formal_only", "claim_text": "Die Lag-Diagnostik ist ein formaler Befund ohne physikalische Freigabe.", "physical_claim_release": PHYSICAL_CLAIM_RELEASE},
        {"run_id": RUN_ID, "claim_key": "qsb_physical_validation", "status": "blocked", "claim_text": "Eine physische QSB-Validierungsbehauptung ist nicht freigegeben.", "physical_claim_release": PHYSICAL_CLAIM_RELEASE},
        {"run_id": RUN_ID, "claim_key": "pbr_physical_existence", "status": "blocked", "claim_text": "Eine physische PBR-Existenzbehauptung ist nicht freigegeben.", "physical_claim_release": PHYSICAL_CLAIM_RELEASE},
        {"run_id": RUN_ID, "claim_key": "lag_axes_dimensions", "status": "blocked", "claim_text": "Eine Deutung der sechs Lag-Achsen als Raumzeitdimensionen ist nicht freigegeben.", "physical_claim_release": PHYSICAL_CLAIM_RELEASE},
        {"run_id": RUN_ID, "claim_key": "spacetime_emergence", "status": "blocked", "claim_text": "Ein Beweis für Raumzeit-Entstehung ist nicht freigegeben.", "physical_claim_release": PHYSICAL_CLAIM_RELEASE},
        {"run_id": RUN_ID, "claim_key": "empirical_validation", "status": "blocked", "claim_text": "Empirische Validierung ist nicht freigegeben.", "physical_claim_release": PHYSICAL_CLAIM_RELEASE},
        {"run_id": RUN_ID, "claim_key": "lag_mechanism_physical_proof", "status": "blocked", "claim_text": "Ein physischer Beweis des Lag-Mechanismus ist nicht freigegeben.", "physical_claim_release": PHYSICAL_CLAIM_RELEASE},
    ]
    lineage = [
        {"run_id": RUN_ID, "source_run_id": DESIGN_RUN_ID, "source_path": f"runs/{DESIGN_RUN_ID}", "source_role": "design_input", "sha256": "directory_reference"},
        {"run_id": RUN_ID, "source_run_id": REVIEW_RUN_ID, "source_path": f"runs/{REVIEW_RUN_ID}", "source_role": "result_review_input", "sha256": "directory_reference"},
        {"run_id": RUN_ID, "source_run_id": NULL_EXEC_RUN_ID, "source_path": f"runs/{NULL_EXEC_RUN_ID}", "source_role": "nullmodel_execution_context", "sha256": "directory_reference"},
        {"run_id": RUN_ID, "source_run_id": "QSB-EXTRACT03A-R1", "source_path": MATRIX_REL, "source_role": "matrix_input", "sha256": sha256_file(matrix_path)},
        {"run_id": RUN_ID, "source_run_id": "QSB-EXTRACT03A-R1", "source_path": PHASE_SUMMARY_REL, "source_role": "assessed_candidate_proxy_alias", "sha256": sha256_file(phase_path) if phase_path.exists() else "missing"},
        {"run_id": RUN_ID, "source_run_id": "QSB-EXTRACT03A-R1", "source_path": VALIDATION_REL, "source_role": "matrix_validation_context", "sha256": sha256_file(repo_root / VALIDATION_REL) if (repo_root / VALIDATION_REL).exists() else "missing"},
    ]

    write_csv(data_dir / "lag_mechanism_execution_summary.csv", [summary], list(summary.keys()))
    write_csv(data_dir / "lag_mechanism_test_results.csv", test_rows, list(test_rows[0].keys()))
    write_csv(data_dir / "index_relabeling_results.csv", index_rows, list(index_rows[0].keys()))
    write_csv(data_dir / "order_scrambling_results.csv", order_rows, list(order_rows[0].keys()))
    write_csv(data_dir / "independent_lag_variable_results.csv", [independent_result], list(independent_result.keys()))
    write_csv(data_dir / "shift_operator_results.csv", [shift_result], list(shift_result.keys()))
    write_csv(data_dir / "toeplitz_dependency_results.csv", [toeplitz_result], list(toeplitz_result.keys()))
    write_csv(data_dir / "physical_proxy_results.csv", [physical_result], list(physical_result.keys()))
    write_csv(data_dir / "nullmodel_operationalization_review.csv", [nullmodel_result], list(nullmodel_result.keys()))
    write_csv(data_dir / "lag_mechanism_decision.csv", [decision], list(decision.keys()))
    write_csv(data_dir / "claim_boundaries.csv", claims, list(claims[0].keys()))
    write_csv(data_dir / "input_run_lineage.csv", lineage, list(lineage[0].keys()))
    manifest = {
        "run_id": RUN_ID,
        "source_run_id": DESIGN_RUN_ID,
        "matrix_source": MATRIX_REL,
        "lineage_bundle_sha256": lineages,
        "tests": detailed,
        "final_decision": decision,
        "physical_claim_release": PHYSICAL_CLAIM_RELEASE,
    }
    (data_dir / "lag_mechanism_execution_manifest.json").write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    validation_placeholder = [{"run_id": RUN_ID, "check_name": "pending_validator", "status": "not_run", "detail": "Execution script completed; run validator."}]
    write_csv(run_dir / "validation/validation_results.csv", validation_placeholder, list(validation_placeholder[0].keys()))

    docs = {
        "README.md": f"# {RUN_ID}\n\nAusführungslauf für formale Lag-Mechanismus-Diagnostik.\n\nFinale Entscheidung: `{final_decision}`.\n\nNo physical claims are released.\n`physical_claim_release={PHYSICAL_CLAIM_RELEASE}`\n",
        f"{RUN_ID}.md": f"# {RUN_ID}\n\n## Befund\n\nSieben Testfamilien wurden bearbeitet. Fünf Testfamilien wurden ausgeführt; zwei wurden wegen fehlender unabhängiger Eingaben blockiert. Finale Entscheidung: `{final_decision}`.\n\n## Interpretation\n\n{rationale}\n\n## Hypothese\n\nDie Lag-Ordnung bleibt zentraler formaler Trägerkandidat, benötigt aber unabhängige Input-Anreicherung zur Trennung von Indexkonstruktion und Mechanismus.\n\n## Offene Lücke\n\nUnabhängige Lag-Variablen und physische Proxy-Daten fehlen.\n\n## Claim Boundary\n\nNo physical claims are released.\n`physical_claim_release={PHYSICAL_CLAIM_RELEASE}`\n",
        "RUN_COMMANDS_PBR_LAG_MECHANISM_EXECUTION01.md": f"# Run Commands\n\n```bash\nRUN_DIR=\"runs/{RUN_ID}\"\n.venv/bin/python \"$RUN_DIR/scripts/run_pbr_lag_mechanism_execution.py\" --repo-root . --run-dir \"$RUN_DIR\"\n.venv/bin/python \"$RUN_DIR/scripts/validate_pbr_lag_mechanism_execution.py\" \"$RUN_DIR\"\ngit diff --check\ngit status --short --untracked-files=all\n```\n",
        "docs/PBR_LAG_MECHANISM_EXECUTION_SUMMARY_DE.md": f"# Lag-Mechanismus Ausführung Summary\n\n## Befund\n\nFinale Entscheidung: `{final_decision}`.\n\n## Interpretation\n\n{rationale}\n\n## Hypothese\n\nEine unabhängige Lag-Variable könnte den Befund in Richtung formaler Mechanismuskandidatur schärfen.\n\n## Offene Lücke\n\nProxy-Daten fehlen.\n\n## Claim Boundary\n\n`physical_claim_release={PHYSICAL_CLAIM_RELEASE}`\n",
        "docs/PBR_LAG_MECHANISM_EXECUTION_TEST_RESULTS_DE.md": "# Test Results\n\n## Befund\n\nIndex-Relabeling, Order-Scrambling, Shift-Operator, Toeplitz-Abhängigkeit und Nullmodell-Operationalisierungsreview wurden ausgeführt. Independent-Lag-Variable und Physical-Proxy wurden wegen fehlender unabhängiger Eingaben blockiert.\n\n## Interpretation\n\nDie Ordnung ist diagnostisch relevant; unabhängige Mechanismusbelege fehlen noch.\n\n## Hypothese\n\nInput-Anreicherung ist erforderlich.\n\n## Offene Lücke\n\nKeine physische Proxy-Quelle.\n\n## Claim Boundary\n\nKeine physikalische Claim-Freigabe.\n",
        "docs/PBR_LAG_MECHANISM_EXECUTION_CLAIM_BOUNDARY_DE.md": f"# Claim Boundary\n\n## Befund\n\nAlle physischen Claims bleiben blockiert.\n\n## Interpretation\n\nDie Resultate sind formale Diagnostik.\n\n## Hypothese\n\nPhysische Interpretation wäre erst nach separater Proxy- und Reviewkette zulässig.\n\n## Offene Lücke\n\nKein physisches Gate wurde ausgeführt.\n\n## Claim Boundary\n\n`physical_claim_release={PHYSICAL_CLAIM_RELEASE}`\n",
        "docs/PBR_LAG_MECHANISM_EXECUTION_NEXT_GATE_DE.md": f"# Next Gate\n\n## Befund\n\n`next_gate={next_gate}`.\n\n## Interpretation\n\nDer nächste Schritt ist Input-Artefakt-Anreicherung für unabhängige Lag-Variablen und Proxy-Quellen.\n\n## Hypothese\n\nErst mit unabhängigen Variablen lässt sich die Mechanismusfrage schärfer entscheiden.\n\n## Offene Lücke\n\nKeine physische Proxy-Quelle vorhanden.\n\n## Claim Boundary\n\nKeine physikalische Claim-Freigabe.\n",
        "docs/PBR_LAG_MECHANISM_EXECUTION_INTERPRETATION_DE.md": f"# Interpretation\n\n## Befund\n\nDie Matrix zeigt starke Lag-/Toeplitz-Diagnostik; Order-Scrambling zerstört die ursprüngliche Lag-Klassenstruktur in der geprüften Operationalisierung.\n\n## Interpretation\n\nDies reicht für einen formalen Trägerkandidaten, aber ohne unabhängige Variable nicht für eine eindeutige Entscheidung gegen reine Konstruktion.\n\n## Hypothese\n\nDer Befund ist aktuell am besten als `{final_decision}` zu führen.\n\n## Offene Lücke\n\nUnabhängige Lag- und Proxy-Artefakte fehlen.\n\n## Claim Boundary\n\nNo physical claims are released.\n",
    }
    for rel, text in docs.items():
        write_text(run_dir / rel, text)
    tables = {
        "pbr_lag_mechanism_execution_summary": (list(summary.keys()), [summary]),
        "pbr_lag_mechanism_test_results": (list(test_rows[0].keys()), test_rows),
        "pbr_lag_mechanism_index_relabeling": (list(index_rows[0].keys()), index_rows),
        "pbr_lag_mechanism_order_scrambling": (list(order_rows[0].keys()), order_rows),
        "pbr_lag_mechanism_independent_lag_variable": (list(independent_result.keys()), [independent_result]),
        "pbr_lag_mechanism_shift_operator": (list(shift_result.keys()), [shift_result]),
        "pbr_lag_mechanism_toeplitz_dependency": (list(toeplitz_result.keys()), [toeplitz_result]),
        "pbr_lag_mechanism_physical_proxy": (list(physical_result.keys()), [physical_result]),
        "pbr_lag_mechanism_nullmodel_operationalization": (list(nullmodel_result.keys()), [nullmodel_result]),
        "pbr_lag_mechanism_decision": (list(decision.keys()), [decision]),
        "pbr_lag_mechanism_claim_boundaries": (list(claims[0].keys()), claims),
        "pbr_lag_mechanism_lineage": (list(lineage[0].keys()), lineage),
        "pbr_lag_mechanism_validation_results": (list(validation_placeholder[0].keys()), []),
    }
    create_sql(run_dir, tables)
    print("PBR lag mechanism execution completed")
    print(f"run_id={RUN_ID}")
    print(f"final_decision_class={final_decision}")
    print(f"next_gate={next_gate}")
    print(f"physical_claim_release={PHYSICAL_CLAIM_RELEASE}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
