#!/usr/bin/env python3
"""Execute PBR nullmodel families against the existing K_candidate matrix."""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import subprocess
from collections import Counter
from datetime import datetime, timezone
from itertools import combinations
from pathlib import Path
from typing import Any, Dict, Iterable, List, Sequence, Tuple

import numpy as np

RUN_ID = "QSB-PLANCK-BRIDGE-RESONATOR-NULLMODEL-EXECUTION-01"
SOURCE_RUN_ID = "QSB-PLANCK-BRIDGE-RESONATOR-NULLMODEL-DESIGN-01"
MATRIX_ID = "QSB-EXTRACT03A-R1_K_candidate"
MATRIX_REL = "runs/QSB-EXTRACT03A-R1/authorized_execution_with_s1_addendum/11_K_candidate_matrix.csv"
VALIDATION_REL = "runs/QSB-EXTRACT03A-R1/authorized_execution_with_s1_addendum/12_K_validation_results.csv"
SPECTRAL_RUN_REL = "runs/QSB-PLANCK-BRIDGE-RESONATOR-SPECTRAL-READOUT-01"
SCHEMA = "qsb_planck_bridge"
PHYSICAL_CLAIM_RELEASE = "blocked_no_physics_claim"
CLAIM_STATUS = "nullmodel_execution_only"
TOLERANCE = 1e-10
PAIR_TOLERANCE = 1e-12
FAMILIES = [
    "label_permutation_null",
    "lag_preserving_shuffle_null",
    "random_gram_psd_null",
    "directed_pair_rewire_null",
    "sign_flip_antiparallel_null",
]
GERMAN_LABELS = {
    "run_id": "Lauf-ID",
    "source_run_id": "Quell-Lauf-ID",
    "matrix_id": "Matrix-ID",
    "matrix_source": "Matrix-Herkunft",
    "nullmodel_family": "Nullmodell-Familie",
    "nullmodel_name": "Nullmodell-Name",
    "sample_id": "Nullmodell-Probe-ID",
    "seed": "Zufalls-Seed",
    "samples_per_family": "Anzahl-Proben",
    "execution_status": "Ausführungsstatus",
    "executed_at_utc": "Ausführungszeitpunkt",
    "code_version": "Code-Version",
    "git_commit": "Git-Commit",
    "psd_pass": "PSD-bestanden",
    "lambda_min": "kleinster Eigenwert",
    "lambda_max": "größter Eigenwert",
    "eigenvalue_tolerance": "Eigenwert-Toleranz",
    "rank_tol_1e_10": "Rang",
    "rank_tolerance": "Rang-Toleranz",
    "nullity": "Nullität",
    "trace": "Spur",
    "eigenvalue_profile": "Eigenwertprofil",
    "eigen_profile_distance": "Eigenprofil-Abstand",
    "spectral_gap_distance": "Spektrallücken-Abstand",
    "rank6_preserved": "Rang-6-erhalten",
    "psd_and_rank_preserved": "PSD-und-Rang-erhalten",
    "directed_pair_feature_count": "Anzahl gerichteter Paarfeatures",
    "lag_class_count": "Anzahl Lag-Klassen",
    "lag_class_structure_preserved": "Lag-Klassen-Struktur erhalten",
    "lag_axis_collapse_score": "Lag-Achsen-Kollapswert",
    "within_lag_similarity": "Innerhalb-Lag-Ähnlichkeit",
    "between_lag_separation": "Zwischen-Lag-Trennung",
    "directed_pair_consistency": "Gerichtete-Paar-Konsistenz",
    "plus_minus_k_antiparallel_score": "Plus-Minus-k-Antiparallelitätswert",
    "antiparallelity_preserved": "Antiparallelität erhalten",
    "lag_structure_distance": "Lag-Struktur-Abstand",
    "lag_structure_reproduction_class": "Lag-Struktur-Reproduktion",
    "observed_value": "Originalwert",
    "null_mean": "Nullmodell-Mittelwert",
    "null_std": "Nullmodell-Standardabweichung",
    "null_min": "Nullmodell-Minimum",
    "null_max": "Nullmodell-Maximum",
    "rank_z_score": "Rang-Z-Wert",
    "eigen_profile_z_score": "Eigenprofil-Z-Wert",
    "lag_structure_z_score": "Lagstruktur-Z-Wert",
    "empirical_p_value": "empirischer p-Wert",
    "null_reproduction_rate": "Null-Reproduktionsrate",
    "complete_structure_reproduction": "vollständige Strukturreproduktion",
    "partial_structure_reproduction": "teilweise Strukturreproduktion",
    "critical_nullmodel_reproduction": "kritische Nullmodell-Reproduktion",
    "specificity_classification": "Spezifitätsstufe",
    "specificity_reason": "Spezifitätsbegründung",
    "critical_nullmodel": "kritisches Nullmodell",
    "strengthening_nullmodel": "stärkendes Nullmodell",
    "formal_claim_status": "formaler Claim-Status",
    "physical_claim_release": "physikalische Claim-Freigabe",
    "next_gate": "nächster Gate",
    "external_readiness": "externe Kommunikationsreife",
    "reviewer_risk": "Reviewer-Risiko",
    "red_team_status": "Red-Team-Status",
}


def bool_text(value: bool) -> str:
    return "true" if value else "false"


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


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


def git_commit(repo_root: Path) -> str:
    try:
        out = subprocess.check_output(["git", "rev-parse", "--short", "HEAD"], cwd=repo_root, text=True).strip()
        return out
    except Exception:
        return "unknown"


def parse_pair_id(pair_id: str) -> Tuple[int, int, int, int, str, str]:
    left, right = pair_id.split("|", 1)
    i = int(left)
    j = int(right)
    lag = j - i
    if lag == 0:
        raise ValueError(f"diagonal pair id is not allowed: {pair_id}")
    abs_lag = abs(lag)
    direction = "+" if lag > 0 else "-"
    return i, j, lag, abs_lag, direction, f"{direction}{abs_lag}"


def parse_matrix(path: Path) -> Tuple[np.ndarray, List[str], List[str]]:
    required = ["row_pair_id", "column_pair_id", "K_candidate", "lineage_bundle_sha256"]
    rows = read_csv(path)
    if not rows:
        raise ValueError("empty matrix CSV")
    if list(rows[0].keys()) != required:
        raise ValueError(f"unexpected matrix header: {list(rows[0].keys())}")
    row_order: List[str] = []
    col_order: List[str] = []
    row_seen = set()
    col_seen = set()
    lineages = set()
    for row in rows:
        if row["row_pair_id"] not in row_seen:
            row_order.append(row["row_pair_id"])
            row_seen.add(row["row_pair_id"])
        if row["column_pair_id"] not in col_seen:
            col_order.append(row["column_pair_id"])
            col_seen.add(row["column_pair_id"])
        lineages.add(row["lineage_bundle_sha256"])
    if row_order != col_order:
        raise ValueError("row and column pair ordering differ")
    matrix = np.full((len(row_order), len(col_order)), np.nan, dtype=float)
    filled = np.zeros_like(matrix, dtype=bool)
    row_idx = {v: i for i, v in enumerate(row_order)}
    col_idx = {v: i for i, v in enumerate(col_order)}
    for row in rows:
        i = row_idx[row["row_pair_id"]]
        j = col_idx[row["column_pair_id"]]
        if filled[i, j]:
            raise ValueError(f"duplicate matrix cell: {row['row_pair_id']} x {row['column_pair_id']}")
        matrix[i, j] = float(row["K_candidate"])
        filled[i, j] = True
    if not np.all(filled):
        raise ValueError("matrix CSV does not contain a complete square matrix")
    return matrix, row_order, sorted(lineages)


def pair_metadata(pair_ids: Sequence[str]) -> List[Dict[str, Any]]:
    rows = []
    for pair_id in pair_ids:
        i, j, lag, abs_lag, direction, lag_class = parse_pair_id(pair_id)
        rows.append({"pair_id": pair_id, "i": i, "j": j, "lag": lag, "abs_lag": abs_lag, "direction": direction, "lag_class": lag_class})
    return rows


def canonical_lag_vector(matrix: np.ndarray, meta: Sequence[Dict[str, Any]]) -> np.ndarray:
    values: List[float] = []
    classes = sorted({m["lag_class"] for m in meta}, key=lambda v: (int(v[1:]), v[0]))
    for a in classes:
        ia = [idx for idx, row in enumerate(meta) if row["lag_class"] == a]
        for b in classes:
            ib = [idx for idx, row in enumerate(meta) if row["lag_class"] == b]
            block = matrix[np.ix_(ia, ib)]
            values.append(float(np.mean(block)))
    return np.array(values, dtype=float)


def relation_counts(matrix: np.ndarray) -> Tuple[int, int]:
    parallel = 0
    antiparallel = 0
    for i, j in combinations(range(matrix.shape[0]), 2):
        value = float(matrix[i, j])
        if abs(value - 1.0) <= PAIR_TOLERANCE:
            parallel += 1
        if abs(value + 1.0) <= PAIR_TOLERANCE:
            antiparallel += 1
    return parallel, antiparallel


def diagnostics(matrix: np.ndarray, meta: Sequence[Dict[str, Any]], observed: Dict[str, Any] | None = None) -> Dict[str, Any]:
    eig = np.linalg.eigvalsh(matrix)
    rank = int(np.count_nonzero(eig > TOLERANCE))
    nullity = int(matrix.shape[0] - rank)
    trace = float(np.trace(matrix))
    lambda_min = float(np.min(eig))
    lambda_max = float(np.max(eig))
    psd_pass = bool(lambda_min >= -TOLERANCE and float(np.max(np.abs(matrix - matrix.T))) <= TOLERANCE)
    profile = np.sort(np.maximum(eig, 0.0))[::-1]
    if trace > 0:
        profile = profile / trace
    gaps = np.diff(np.sort(eig)[::-1])
    lag_vector = canonical_lag_vector(matrix, meta)
    parallel, antiparallel = relation_counts(matrix)

    classes = sorted({m["lag_class"] for m in meta}, key=lambda v: (int(v[1:]), v[0]))
    within_values: List[float] = []
    between_values: List[float] = []
    for i, row_i in enumerate(meta):
        for j, row_j in enumerate(meta):
            if i >= j:
                continue
            value = abs(float(matrix[i, j]))
            if row_i["lag_class"] == row_j["lag_class"]:
                within_values.append(value)
            else:
                between_values.append(value)
    within_lag_similarity = float(np.mean(within_values)) if within_values else 0.0
    between_lag_separation = float(1.0 - np.mean(between_values)) if between_values else 0.0
    lag_axis_collapse_score = within_lag_similarity
    directed_pair_consistency = 1.0 if len(meta) == 42 and len(classes) == 12 else 0.0
    anti_scores = []
    for k in range(1, 7):
        plus = [idx for idx, row in enumerate(meta) if row["lag_class"] == f"+{k}"]
        minus = [idx for idx, row in enumerate(meta) if row["lag_class"] == f"-{k}"]
        if plus and minus:
            anti_scores.append(float(np.mean(matrix[np.ix_(plus, minus)])))
    plus_minus_score = float(np.mean(anti_scores)) if anti_scores else 0.0

    if observed is None:
        eigen_distance = 0.0
        gap_distance = 0.0
        lag_distance = 0.0
        antiparallelity_preserved = True
        lag_preserved = True
    else:
        eigen_distance = float(np.linalg.norm(profile - observed["eigen_profile"]))
        gap_distance = float(np.linalg.norm(gaps - observed["spectral_gaps"]))
        lag_distance = float(np.linalg.norm(lag_vector - observed["lag_vector"]))
        antiparallelity_preserved = abs(plus_minus_score - observed["plus_minus_k_antiparallel_score"]) <= 1e-8
        lag_preserved = lag_distance <= 1e-8

    rank6 = rank == 6
    trace_ok = abs(trace - 42.0) <= 1e-8
    nullity_ok = nullity == 36
    eigen_ok = eigen_distance <= 1e-8
    complete = bool(psd_pass and rank6 and nullity_ok and trace_ok and eigen_ok and lag_preserved and antiparallelity_preserved)
    partial = bool(rank6 and not complete)
    if complete:
        reproduction_class = "vollständig"
    elif partial:
        reproduction_class = "teilweise"
    else:
        reproduction_class = "nicht_reproduziert"
    return {
        "psd_pass": psd_pass,
        "lambda_min": lambda_min,
        "lambda_max": lambda_max,
        "eigenvalue_tolerance": TOLERANCE,
        "rank_tol_1e_10": rank,
        "rank_tolerance": TOLERANCE,
        "nullity": nullity,
        "trace": trace,
        "eigen_profile": profile,
        "eigenvalue_profile": json.dumps([round(float(x), 17) for x in profile.tolist()], ensure_ascii=False),
        "spectral_gaps": gaps,
        "eigen_profile_distance": eigen_distance,
        "spectral_gap_distance": gap_distance,
        "rank6_preserved": rank6,
        "psd_and_rank_preserved": bool(psd_pass and rank6),
        "directed_pair_feature_count": len(meta),
        "lag_class_count": len(classes),
        "lag_vector": lag_vector,
        "lag_class_structure_preserved": lag_preserved,
        "lag_axis_collapse_score": lag_axis_collapse_score,
        "within_lag_similarity": within_lag_similarity,
        "between_lag_separation": between_lag_separation,
        "directed_pair_consistency": directed_pair_consistency,
        "plus_minus_k_antiparallel_score": plus_minus_score,
        "antiparallelity_preserved": antiparallelity_preserved,
        "lag_structure_distance": lag_distance,
        "lag_structure_reproduction_class": reproduction_class,
        "complete_structure_reproduction": complete,
        "partial_structure_reproduction": partial,
        "parallel_count": parallel,
        "antiparallel_count": antiparallel,
    }


def permuted_matrix(matrix: np.ndarray, order: Sequence[int]) -> np.ndarray:
    return matrix[np.ix_(order, order)]


def sample_nullmodel(family: str, matrix: np.ndarray, meta: Sequence[Dict[str, Any]], rng: np.random.Generator) -> Tuple[np.ndarray, List[Dict[str, Any]], str]:
    n = matrix.shape[0]
    if family == "label_permutation_null":
        labels = list(range(7))
        shuffled = labels[:]
        rng.shuffle(shuffled)
        label_map = dict(zip(labels, shuffled))
        relabeled = [f"{label_map[row['i']]}|{label_map[row['j']]}" for row in meta]
        return matrix.copy(), pair_metadata(relabeled), "node_label_permutation_metadata_only"
    if family == "lag_preserving_shuffle_null":
        order = list(range(n))
        for lag_class in sorted({m["lag_class"] for m in meta}):
            idx = [i for i, row in enumerate(meta) if row["lag_class"] == lag_class]
            shuffled = idx[:]
            rng.shuffle(shuffled)
            for target, source in zip(idx, shuffled):
                order[target] = source
        return permuted_matrix(matrix, order), list(meta), "within_signed_lag_class_feature_shuffle"
    if family == "random_gram_psd_null":
        vectors = rng.normal(size=(n, 6))
        norms = np.linalg.norm(vectors, axis=1)
        vectors = vectors / norms[:, None]
        return vectors @ vectors.T, list(meta), "random_unit_vector_gram_rank6_trace42"
    if family == "directed_pair_rewire_null":
        all_pairs = [f"{i}|{j}" for i in range(7) for j in range(7) if i != j]
        rng.shuffle(all_pairs)
        return matrix.copy(), pair_metadata(all_pairs), "directed_pair_metadata_rewire_without_self_pairs"
    if family == "sign_flip_antiparallel_null":
        signs = rng.choice(np.array([-1.0, 1.0]), size=n)
        signed = matrix * np.outer(signs, signs)
        return signed, list(meta), "independent_feature_orientation_sign_flip"
    raise ValueError(f"unknown family: {family}")


def fmt(value: Any) -> str:
    if isinstance(value, bool):
        return bool_text(value)
    if isinstance(value, float):
        return f"{value:.17g}"
    if isinstance(value, np.floating):
        return f"{float(value):.17g}"
    return str(value)


def z_score(observed: float, values: Sequence[float]) -> float:
    arr = np.array(values, dtype=float)
    std = float(np.std(arr))
    if std == 0.0:
        return 0.0 if abs(float(np.mean(arr)) - observed) <= 1e-15 else math.inf
    return float((observed - float(np.mean(arr))) / std)


def classify(family_summaries: Sequence[Dict[str, Any]]) -> Tuple[str, str, str, str, str]:
    max_rate = max(float(row["null_reproduction_rate"]) for row in family_summaries)
    critical = [row for row in family_summaries if row["nullmodel_family"] in {"random_gram_psd_null", "directed_pair_rewire_null"}]
    critical_rate = max(float(row["null_reproduction_rate"]) for row in critical)
    critical_name = max(family_summaries, key=lambda row: float(row["null_reproduction_rate"]))["nullmodel_family"]
    strengthening = min(family_summaries, key=lambda row: float(row["null_reproduction_rate"]))["nullmodel_family"]
    if max_rate > 0.25 or critical_rate > 0.25:
        return (
            "no_specificity",
            "keine formale Spezifität",
            "Mindestens ein geprüftes Nullmodell reproduziert die vollständige Struktur regelmäßig.",
            critical_name,
            strengthening,
        )
    if max_rate > 0.05:
        return (
            "weak_specificity",
            "schwache Spezifität",
            "Mehrere oder einzelne Nullmodellstichproben erzeugen ähnliche formale Strukturen in relevanter Häufigkeit.",
            critical_name,
            strengthening,
        )
    if max_rate > 0.01:
        return (
            "moderate_formal_specificity",
            "mäßige formale Spezifität",
            "Rang-6 oder Teilstrukturen werden nullmodellseitig beobachtet, vollständige Reproduktion bleibt aber begrenzt.",
            critical_name,
            strengthening,
        )
    return (
        "strong_formal_specificity",
        "starke formale Spezifität",
        "Vollständige Strukturreproduktion ist in den geprüften Nullmodellen selten oder nicht beobachtet.",
        critical_name,
        strengthening,
    )


def csv_literal(value: str) -> str:
    return value.replace("\\", "\\\\").replace("\t", " ").replace("\n", " ")


def sql_type(field: str) -> str:
    if field in {"sample_id", "seed", "samples_per_family", "directed_pair_feature_count", "lag_class_count", "rank_tol_1e_10", "nullity", "sample_count", "complete_reproduction_count", "partial_reproduction_count"}:
        return "integer"
    if field.endswith("_count"):
        return "integer"
    if field in {"lambda_min", "lambda_max", "eigenvalue_tolerance", "rank_tolerance", "trace", "eigen_profile_distance", "spectral_gap_distance", "lag_axis_collapse_score", "within_lag_similarity", "between_lag_separation", "directed_pair_consistency", "plus_minus_k_antiparallel_score", "lag_structure_distance", "null_mean", "null_std", "null_min", "null_max", "rank_z_score", "eigen_profile_z_score", "lag_structure_z_score", "empirical_p_value", "null_reproduction_rate"}:
        return "double precision"
    if field.startswith("is_") or field in {"psd_pass", "rank6_preserved", "psd_and_rank_preserved", "lag_class_structure_preserved", "antiparallelity_preserved", "complete_structure_reproduction", "partial_structure_reproduction", "critical_nullmodel_reproduction"}:
        return "boolean"
    return "text"


def create_sql(run_dir: Path, table_rows: Dict[str, Tuple[List[str], List[Dict[str, Any]]]]) -> None:
    sql_dir = run_dir / "sql"
    create_parts = [f"CREATE SCHEMA IF NOT EXISTS {SCHEMA};", ""]
    for table, (fields, _rows) in table_rows.items():
        cols = ",\n  ".join(f"{field} {sql_type(field)}" for field in fields)
        create_parts.append(f"CREATE TABLE IF NOT EXISTS {SCHEMA}.{table} (\n  {cols}\n);")
        create_parts.append("")
    create_parts.append(f"DROP VIEW IF EXISTS {SCHEMA}.v_pbr_nullmodell_ergebnis_de;")
    create_parts.append(f"""CREATE VIEW {SCHEMA}.v_pbr_nullmodell_ergebnis_de AS
SELECT
  s.run_id AS "Lauf-ID",
  s.source_run_id AS "Quell-Lauf-ID",
  s.matrix_id AS "Matrix-ID",
  s.matrix_source AS "Matrix-Herkunft",
  s.nullmodel_family AS "Nullmodell-Familie",
  s.nullmodel_name AS "Nullmodell-Name",
  s.sample_id AS "Nullmodell-Probe-ID",
  s.seed AS "Zufalls-Seed",
  s.samples_per_family AS "Anzahl-Proben",
  s.execution_status AS "Ausführungsstatus",
  s.executed_at_utc AS "Ausführungszeitpunkt",
  s.code_version AS "Code-Version",
  s.git_commit AS "Git-Commit",
  s.psd_pass AS "PSD-bestanden",
  s.lambda_min AS "kleinster Eigenwert",
  s.lambda_max AS "größter Eigenwert",
  s.eigenvalue_tolerance AS "Eigenwert-Toleranz",
  s.rank_tol_1e_10 AS "Rang",
  s.rank_tolerance AS "Rang-Toleranz",
  s.nullity AS "Nullität",
  s.trace AS "Spur",
  s.eigen_profile_distance AS "Eigenprofil-Abstand",
  s.spectral_gap_distance AS "Spektrallücken-Abstand",
  s.rank6_preserved AS "Rang-6-erhalten",
  s.psd_and_rank_preserved AS "PSD-und-Rang-erhalten",
  s.directed_pair_feature_count AS "Anzahl gerichteter Paarfeatures",
  s.lag_class_count AS "Anzahl Lag-Klassen",
  s.lag_class_structure_preserved AS "Lag-Klassen-Struktur erhalten",
  s.lag_axis_collapse_score AS "Lag-Achsen-Kollapswert",
  s.within_lag_similarity AS "Innerhalb-Lag-Ähnlichkeit",
  s.between_lag_separation AS "Zwischen-Lag-Trennung",
  s.directed_pair_consistency AS "Gerichtete-Paar-Konsistenz",
  s.plus_minus_k_antiparallel_score AS "Plus-Minus-k-Antiparallelitätswert",
  s.antiparallelity_preserved AS "Antiparallelität erhalten",
  s.lag_structure_distance AS "Lag-Struktur-Abstand",
  s.lag_structure_reproduction_class AS "Lag-Struktur-Reproduktion",
  s.complete_structure_reproduction AS "vollständige Strukturreproduktion",
  s.partial_structure_reproduction AS "teilweise Strukturreproduktion",
  c.specificity_classification AS "Spezifitätsstufe",
  c.specificity_reason AS "Spezifitätsbegründung",
  c.critical_nullmodel AS "kritisches Nullmodell",
  c.strengthening_nullmodel AS "stärkendes Nullmodell",
  c.formal_claim_status AS "formaler Claim-Status",
  c.physical_claim_release AS "physikalische Claim-Freigabe",
  c.next_gate AS "nächster Gate",
  c.external_readiness AS "externe Kommunikationsreife",
  c.reviewer_risk AS "Reviewer-Risiko",
  c.red_team_status AS "Red-Team-Status"
FROM {SCHEMA}.pbr_nullmodel_sample_results s
CROSS JOIN {SCHEMA}.pbr_nullmodel_specificity_classification c
WHERE s.run_id = '{RUN_ID}' AND c.run_id = '{RUN_ID}';""")
    write_text(sql_dir / "001_create_qsb_pbr_nullmodel_execution.sql", "\n".join(create_parts))

    insert_parts = ["BEGIN;", ""]
    for table in table_rows:
        insert_parts.append(f"DELETE FROM {SCHEMA}.{table} WHERE run_id = '{RUN_ID}';")
    insert_parts.append("")
    for table, (fields, rows) in table_rows.items():
        if not rows:
            continue
        insert_parts.append(f"COPY {SCHEMA}.{table} ({', '.join(fields)}) FROM stdin WITH (FORMAT csv, HEADER true, DELIMITER E'\\t');")
        insert_parts.append("\t".join(fields))
        for row in rows:
            insert_parts.append("\t".join(csv_literal(fmt(row.get(field, ""))) for field in fields))
        insert_parts.append("\\.")
        insert_parts.append("")
    insert_parts.append("COMMIT;")
    write_text(sql_dir / "002_insert_qsb_pbr_nullmodel_execution.sql", "\n".join(insert_parts))

    validation = f"""
SELECT 'sample_count' AS check_name, count(*)::text AS value
FROM {SCHEMA}.pbr_nullmodel_sample_results
WHERE run_id = '{RUN_ID}';

SELECT 'families' AS check_name, count(DISTINCT nullmodel_family)::text AS value
FROM {SCHEMA}.pbr_nullmodel_sample_results
WHERE run_id = '{RUN_ID}';

SELECT 'physical_claim_release' AS check_name, physical_claim_release AS value
FROM {SCHEMA}.pbr_nullmodel_specificity_classification
WHERE run_id = '{RUN_ID}';

SELECT 'specificity_classification' AS check_name, specificity_classification AS value
FROM {SCHEMA}.pbr_nullmodel_specificity_classification
WHERE run_id = '{RUN_ID}';
"""
    write_text(sql_dir / "003_validation_queries.sql", validation)


def build_docs(run_dir: Path, classification: Dict[str, Any], samples_per_family: int, source_paths: Dict[str, str]) -> None:
    summary = f"""
# PBR Nullmodell-Ausführung 01

## Befund

Der Lauf `{RUN_ID}` hat fünf definierte Nullmodellfamilien mit jeweils `{samples_per_family}` deterministischen Proben ausgeführt. Eingabe war die Matrix `{source_paths['matrix']}`.

Die finale Spezifitätsstufe lautet `{classification['specificity_classification']}` (`{classification['specificity_label_de']}`).

## Interpretation

Der Lauf beantwortet nur die formale Frage, ob die Rang-6 gerichtete Lag-Klassen-Gramstruktur durch die geprüften Nullmodelle reproduziert wird. Die Klassifikation folgt aus den vollständigen Strukturreproduktionsraten der Nullmodellfamilien.

## Hypothese

Weitere robuste Auswertungen können prüfen, ob zusätzliche Nullmodelle oder alternative Toleranzfenster die formale Spezifitätsklassifikation verändern.

## Offene Lücke

Die Operationalisierung der Nullmodelle ist lauflokal dokumentiert. Wenn ein späterer Review andere Nullmodellregeln fordert, ist ein neuer Lauf erforderlich.

## Claim Boundary

No physical claims are released.
`physical_claim_release=blocked_no_physics_claim`
"""
    metrics = f"""
# Metriken der PBR Nullmodell-Ausführung

## Befund

Berechnet wurden spektrale Kernmetriken, Lag-Klassen-Metriken und Nullmodell-Vergleichsmetriken. Die vollständige Strukturreproduktion verlangt gleichzeitig PSD-Bestand, Rang 6, Nullität 36, Spur 42, hinreichend ähnliches Eigenprofil, hinreichend ähnliche Lag-Klassenstruktur und hinreichend ähnliche +k/-k-Antiparallelität.

## Interpretation

Eine teilweise Strukturreproduktion liegt vor, wenn Rang 6 reproduziert wird, aber Eigenprofil, Lag-Struktur oder Antiparallelität abweichen.

## Hypothese

Die Metriken können als Review-Anker für strengere Nullmodelle oder andere Toleranzdefinitionen dienen.

## Offene Lücke

Die Distanzen sind formale Matrixdistanzen und keine physikalischen Messgrößen.

## Claim Boundary

Alle Metriken sind formale Diagnostik. `physical_claim_release=blocked_no_physics_claim`.
"""
    boundary = f"""
# Claim Boundary

## Befund

Der Lauf trägt den formalen Claim-Status `{CLAIM_STATUS}`. Die physikalische Claim-Freigabe bleibt `{PHYSICAL_CLAIM_RELEASE}`.

## Interpretation

Erlaubt ist nur eine Aussage über die formale Nullmodell-Reproduktion der Rang-6 gerichteten Lag-Klassen-Gramstruktur.

## Hypothese

Eine spätere physikalische Interpretation wäre nur nach separaten Gates zulässig.

## Offene Lücke

Dieser Lauf enthält kein physikalisches oder empirisches Gate.

## Claim Boundary

Gesperrt bleiben affirmative Aussagen zu physischer QSB-Validierung, physischer PBR-Existenz, Raumzeitdimensionen, Raumzeit-Entstehung und empirischer Validierung.
"""
    next_gate = f"""
# Nächster Gate

## Befund

Der nächste Gate ist `{classification['next_gate']}`.

## Interpretation

Die Nullmodell-Ausführung ist ein formaler Robustheitslauf. Das Ergebnis sollte reviewt werden, bevor es außerhalb des internen Kontexts verwendet wird.

## Hypothese

Ein Folgelauf kann strengere oder zusätzliche Nullmodelle prüfen.

## Offene Lücke

Keine externe Kommunikationsreife ist freigegeben.

## Claim Boundary

No physical claims are released.
"""
    write_text(run_dir / "docs/PBR_NULLMODEL_EXECUTION_SUMMARY_DE.md", summary)
    write_text(run_dir / "docs/PBR_NULLMODEL_EXECUTION_METRICS_DE.md", metrics)
    write_text(run_dir / "docs/PBR_NULLMODEL_EXECUTION_CLAIM_BOUNDARY_DE.md", boundary)
    write_text(run_dir / "docs/PBR_NULLMODEL_EXECUTION_NEXT_GATE_DE.md", next_gate)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, default=Path("."))
    parser.add_argument("--run-dir", type=Path, default=Path(f"runs/{RUN_ID}"))
    parser.add_argument("--samples-per-family", type=int, default=1000)
    parser.add_argument("--base-seed", type=int, default=2026070801)
    args = parser.parse_args()

    repo_root = args.repo_root.resolve()
    run_dir = (repo_root / args.run_dir).resolve() if not args.run_dir.is_absolute() else args.run_dir.resolve()
    data_dir = run_dir / "data"
    matrix_path = repo_root / MATRIX_REL
    validation_path = repo_root / VALIDATION_REL
    if not matrix_path.exists():
        raise SystemExit(f"blocked_missing_input_artifact: {MATRIX_REL}")
    matrix, pair_ids, lineages = parse_matrix(matrix_path)
    meta = pair_metadata(pair_ids)
    observed = diagnostics(matrix, meta)
    observed["eigen_profile"] = observed["eigen_profile"]
    observed["spectral_gaps"] = observed["spectral_gaps"]
    observed["lag_vector"] = observed["lag_vector"]
    observed["plus_minus_k_antiparallel_score"] = observed["plus_minus_k_antiparallel_score"]

    executed_at = datetime.now(timezone.utc).replace(microsecond=0).isoformat()
    commit = git_commit(repo_root)
    sample_rows: List[Dict[str, Any]] = []
    spectral_rows: List[Dict[str, Any]] = []
    lag_rows: List[Dict[str, Any]] = []
    seeds: Dict[str, List[int]] = {}
    for family_index, family in enumerate(FAMILIES, start=1):
        seeds[family] = []
        for sample_id in range(1, args.samples_per_family + 1):
            seed = args.base_seed + family_index * 1_000_000 + sample_id
            seeds[family].append(seed)
            rng = np.random.default_rng(seed)
            sample_matrix, sample_meta, nullmodel_name = sample_nullmodel(family, matrix, meta, rng)
            diag = diagnostics(sample_matrix, sample_meta, observed)
            common = {
                "run_id": RUN_ID,
                "source_run_id": SOURCE_RUN_ID,
                "matrix_id": MATRIX_ID,
                "matrix_source": MATRIX_REL,
                "nullmodel_family": family,
                "nullmodel_name": nullmodel_name,
                "sample_id": sample_id,
                "seed": seed,
                "samples_per_family": args.samples_per_family,
                "execution_status": "executed",
                "executed_at_utc": executed_at,
                "code_version": "run_pbr_nullmodel_execution.py",
                "git_commit": commit,
            }
            sample_rows.append({**common, **{k: v for k, v in diag.items() if not isinstance(v, np.ndarray)}})
            spectral_rows.append({**common, **{k: diag[k] for k in ["psd_pass", "lambda_min", "lambda_max", "eigenvalue_tolerance", "rank_tol_1e_10", "rank_tolerance", "nullity", "trace", "eigenvalue_profile", "eigen_profile_distance", "spectral_gap_distance", "rank6_preserved", "psd_and_rank_preserved"]}})
            lag_rows.append({**common, **{k: diag[k] for k in ["directed_pair_feature_count", "lag_class_count", "lag_class_structure_preserved", "lag_axis_collapse_score", "within_lag_similarity", "between_lag_separation", "directed_pair_consistency", "plus_minus_k_antiparallel_score", "antiparallelity_preserved", "lag_structure_distance", "lag_structure_reproduction_class"]}})

    family_rows: List[Dict[str, Any]] = []
    comparison_rows: List[Dict[str, Any]] = []
    for family in FAMILIES:
        rows = [row for row in sample_rows if row["nullmodel_family"] == family]
        complete_count = sum(1 for row in rows if row["complete_structure_reproduction"])
        partial_count = sum(1 for row in rows if row["partial_structure_reproduction"])
        rate = complete_count / len(rows)
        family_rows.append({
            "run_id": RUN_ID,
            "nullmodel_family": family,
            "sample_count": len(rows),
            "complete_reproduction_count": complete_count,
            "partial_reproduction_count": partial_count,
            "null_reproduction_rate": rate,
            "rank6_rate": sum(1 for row in rows if row["rank6_preserved"]) / len(rows),
            "psd_and_rank_rate": sum(1 for row in rows if row["psd_and_rank_preserved"]) / len(rows),
            "physical_claim_release": PHYSICAL_CLAIM_RELEASE,
        })
        comparison_rows.append({
            "run_id": RUN_ID,
            "nullmodel_family": family,
            "observed_value": 0.0,
            "null_mean": float(np.mean([float(row["lag_structure_distance"]) for row in rows])),
            "null_std": float(np.std([float(row["lag_structure_distance"]) for row in rows])),
            "null_min": float(np.min([float(row["lag_structure_distance"]) for row in rows])),
            "null_max": float(np.max([float(row["lag_structure_distance"]) for row in rows])),
            "rank_z_score": z_score(float(observed["rank_tol_1e_10"]), [float(row["rank_tol_1e_10"]) for row in rows]),
            "eigen_profile_z_score": z_score(0.0, [float(row["eigen_profile_distance"]) for row in rows]),
            "lag_structure_z_score": z_score(0.0, [float(row["lag_structure_distance"]) for row in rows]),
            "empirical_p_value": rate,
            "null_reproduction_rate": rate,
            "complete_structure_reproduction": complete_count > 0,
            "partial_structure_reproduction": partial_count > 0,
            "critical_nullmodel_reproduction": bool(family in {"random_gram_psd_null", "directed_pair_rewire_null"} and rate > 0.0),
        })

    class_key, class_label, reason, critical, strengthening = classify(family_rows)
    next_gate = "result_review_required"
    classification = {
        "run_id": RUN_ID,
        "specificity_classification": class_key,
        "specificity_label_de": class_label,
        "specificity_reason": reason,
        "critical_nullmodel": critical,
        "strengthening_nullmodel": strengthening,
        "formal_claim_status": CLAIM_STATUS,
        "physical_claim_release": PHYSICAL_CLAIM_RELEASE,
        "next_gate": next_gate,
        "external_readiness": "internal_only",
        "reviewer_risk": "hoch_bei_lag_erhaltendem_nullmodell",
        "red_team_status": "required",
    }

    summary_row = {
        "run_id": RUN_ID,
        "source_run_id": SOURCE_RUN_ID,
        "matrix_id": MATRIX_ID,
        "matrix_source": MATRIX_REL,
        "execution_status": "executed",
        "executed_at_utc": executed_at,
        "samples_per_family": args.samples_per_family,
        "nullmodel_family_count": len(FAMILIES),
        "sample_total": len(sample_rows),
        "specificity_classification": class_key,
        "specificity_reason": reason,
        "claim_status": CLAIM_STATUS,
        "physical_claim_release": PHYSICAL_CLAIM_RELEASE,
        "next_gate": next_gate,
        "git_commit": commit,
    }
    lineage_rows = [
        {
            "run_id": RUN_ID,
            "source_run_id": SOURCE_RUN_ID,
            "input_id": "K_candidate_matrix",
            "source_path": MATRIX_REL,
            "sha256": sha256_file(matrix_path),
            "lineage_bundle_sha256": lineages[0] if len(lineages) == 1 else "|".join(lineages),
        },
        {
            "run_id": RUN_ID,
            "source_run_id": "QSB-PLANCK-BRIDGE-RESONATOR-SPECTRAL-READOUT-01",
            "input_id": "spectral_readout_run",
            "source_path": SPECTRAL_RUN_REL,
            "sha256": "directory_reference",
            "lineage_bundle_sha256": "not_applicable",
        },
        {
            "run_id": RUN_ID,
            "source_run_id": "QSB-PLANCK-BRIDGE-RESONATOR-PSD-TEST-01",
            "input_id": "K_validation_results",
            "source_path": VALIDATION_REL,
            "sha256": sha256_file(validation_path) if validation_path.exists() else "missing",
            "lineage_bundle_sha256": "not_applicable",
        },
    ]
    claim_rows = [
        {"run_id": RUN_ID, "boundary_id": "ALLOW-001", "claim_key": "formal_nullmodel_specificity", "status": "allowed_formal_only", "claim_text": "Die Rang-6 gerichtete Lag-Klassen-Gramstruktur wird nur formal gegen die geprüften Nullmodelle bewertet.", "physical_claim_release": PHYSICAL_CLAIM_RELEASE},
        {"run_id": RUN_ID, "boundary_id": "BLOCK-001", "claim_key": "qsb_physical_validation", "status": "blocked", "claim_text": "Eine physische QSB-Validierungsbehauptung ist nicht freigegeben.", "physical_claim_release": PHYSICAL_CLAIM_RELEASE},
        {"run_id": RUN_ID, "boundary_id": "BLOCK-002", "claim_key": "pbr_physical_existence", "status": "blocked", "claim_text": "Eine physische PBR-Existenzbehauptung ist nicht freigegeben.", "physical_claim_release": PHYSICAL_CLAIM_RELEASE},
        {"run_id": RUN_ID, "boundary_id": "BLOCK-003", "claim_key": "six_lag_axes_spacetime_dimensions", "status": "blocked", "claim_text": "Eine Deutung der sechs Lag-Achsen als physische Raumzeitdimensionen ist nicht freigegeben.", "physical_claim_release": PHYSICAL_CLAIM_RELEASE},
        {"run_id": RUN_ID, "boundary_id": "BLOCK-004", "claim_key": "spacetime_emergence_proof", "status": "blocked", "claim_text": "Ein Beweis für Raumzeit-Entstehung ist nicht freigegeben.", "physical_claim_release": PHYSICAL_CLAIM_RELEASE},
        {"run_id": RUN_ID, "boundary_id": "BLOCK-005", "claim_key": "empirical_validation", "status": "blocked", "claim_text": "Empirische Validierung ist nicht freigegeben.", "physical_claim_release": PHYSICAL_CLAIM_RELEASE},
    ]

    write_csv(data_dir / "nullmodel_execution_summary.csv", [summary_row], list(summary_row.keys()))
    sample_fields = list(sample_rows[0].keys())
    write_csv(data_dir / "nullmodel_sample_results.csv", sample_rows, sample_fields)
    family_fields = list(family_rows[0].keys())
    write_csv(data_dir / "nullmodel_family_summary.csv", family_rows, family_fields)
    write_csv(data_dir / "spectral_core_metrics.csv", spectral_rows, list(spectral_rows[0].keys()))
    write_csv(data_dir / "lag_class_metrics.csv", lag_rows, list(lag_rows[0].keys()))
    write_csv(data_dir / "nullmodel_comparison_metrics.csv", comparison_rows, list(comparison_rows[0].keys()))
    write_csv(data_dir / "specificity_classification.csv", [classification], list(classification.keys()))
    write_csv(data_dir / "claim_boundaries.csv", claim_rows, list(claim_rows[0].keys()))
    write_csv(data_dir / "input_run_lineage.csv", lineage_rows, list(lineage_rows[0].keys()))
    manifest = {
        "run_id": RUN_ID,
        "source_run_id": SOURCE_RUN_ID,
        "matrix_source": MATRIX_REL,
        "samples_per_family": args.samples_per_family,
        "base_seed": args.base_seed,
        "seeds": {k: {"first": v[0], "last": v[-1], "count": len(v)} for k, v in seeds.items()},
        "nullmodel_families": FAMILIES,
        "observed_reference": {k: fmt(v) for k, v in observed.items() if not isinstance(v, np.ndarray)},
        "specificity_classification": classification,
        "physical_claim_release": PHYSICAL_CLAIM_RELEASE,
    }
    (data_dir / "nullmodel_execution_manifest.json").write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    validation_fields = ["run_id", "check_name", "status", "detail"]
    write_csv(run_dir / "validation/validation_results.csv", [{"run_id": RUN_ID, "check_name": "pending_validator", "status": "not_run", "detail": "Run script completed; execute validator."}], validation_fields)

    table_rows = {
        "pbr_nullmodel_execution_summary": (list(summary_row.keys()), [summary_row]),
        "pbr_nullmodel_sample_results": (sample_fields, sample_rows),
        "pbr_nullmodel_family_summary": (family_fields, family_rows),
        "pbr_nullmodel_spectral_core_metrics": (list(spectral_rows[0].keys()), spectral_rows),
        "pbr_nullmodel_lag_class_metrics": (list(lag_rows[0].keys()), lag_rows),
        "pbr_nullmodel_comparison_metrics": (list(comparison_rows[0].keys()), comparison_rows),
        "pbr_nullmodel_specificity_classification": (list(classification.keys()), [classification]),
        "pbr_nullmodel_execution_claim_boundaries": (list(claim_rows[0].keys()), claim_rows),
        "pbr_nullmodel_execution_lineage": (list(lineage_rows[0].keys()), lineage_rows),
        "pbr_nullmodel_execution_validation_results": (validation_fields, []),
    }
    create_sql(run_dir, table_rows)
    build_docs(run_dir, classification, args.samples_per_family, {"matrix": MATRIX_REL})
    readme = f"""
# {RUN_ID}

Formaler Ausführungslauf für PBR-Nullmodelle.

- Ausführungsstatus: executed
- Stichproben je Nullmodellfamilie: {args.samples_per_family}
- Finale Spezifitätsstufe: {class_key}
- Claim Boundary: `physical_claim_release=blocked_no_physics_claim`
"""
    write_text(run_dir / "README.md", readme)
    run_note = f"""
# {RUN_ID}

## Befund

Fünf Nullmodellfamilien wurden deterministisch gegen `{MATRIX_REL}` ausgeführt. Die finale Klassifikation lautet `{class_key}`.

## Interpretation

{reason}

## Hypothese

Zusätzliche Nullmodelle oder geänderte Toleranzen können die formale Bewertung in einem separaten Lauf prüfen.

## Offene Lücke

Die Ausführung enthält kein physikalisches Gate.

## Claim Boundary

No physical claims are released.
`physical_claim_release=blocked_no_physics_claim`
"""
    write_text(run_dir / f"{RUN_ID}.md", run_note)
    commands = f"""
# Run Commands

```bash
RUN_DIR="runs/{RUN_ID}"
.venv/bin/python "$RUN_DIR/scripts/run_pbr_nullmodel_execution.py" --repo-root . --run-dir "$RUN_DIR"
.venv/bin/python "$RUN_DIR/scripts/validate_pbr_nullmodel_execution.py" "$RUN_DIR"
git diff --check
git status --short --untracked-files=all
```

No git add, commit, push, reset, or destructive git command is part of this run.
"""
    write_text(run_dir / "RUN_COMMANDS_PBR_NULLMODEL_EXECUTION01.md", commands)

    print("PBR nullmodel execution completed")
    print(f"run_id={RUN_ID}")
    print(f"samples_per_family={args.samples_per_family}")
    print(f"sample_total={len(sample_rows)}")
    print(f"specificity_classification={class_key}")
    print(f"physical_claim_release={PHYSICAL_CLAIM_RELEASE}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
