#!/usr/bin/env python3
"""Audit artifact-level and upstream traces for QSB matrix block structure origin."""

from __future__ import annotations

import csv
import json
import random
import statistics
from pathlib import Path


RUN_ID = "QSB-MATRIX-TOPOLOGY-STRUCTURE-ORIGIN-AUDIT"
RUN_DIR = Path("runs") / RUN_ID

SOURCE_EDGE_FILE = Path(
    "runs/QSB-EXTRACT03A-R1/authorized_execution_with_s1_addendum/"
    "16_edge_candidate_result.csv"
)
EXTRACT03_RUN_DIR = Path("runs/QSB-EXTRACT03A-R1/authorized_execution_with_s1_addendum")
CLOSURE_SUMMARY_SOURCE = Path("runs/QSB-MATRIX-TOPOLOGY-CLOSURE-TEST/04_closure_summary.json")
BLOCK_STRUCTURE_SUMMARY_SOURCE = Path(
    "runs/QSB-MATRIX-TOPOLOGY-BLOCK-STRUCTURE-AUDIT/04_block_structure_summary.json"
)
BLOCK_SEMANTICS_SUMMARY_SOURCE = Path(
    "runs/QSB-MATRIX-TOPOLOGY-BLOCK-SEMANTICS-AUDIT/04_block_semantics_summary.json"
)
BLOCK_STRENGTH_SUMMARY_SOURCE = Path(
    "runs/QSB-MATRIX-TOPOLOGY-BLOCK-STRENGTH-PROFILE/04_block_strength_summary.json"
)
NULLMODEL_SUMMARY_SOURCE = Path(
    "runs/QSB-MATRIX-TOPOLOGY-BLOCK-NULLMODEL-AUDIT/04_nullmodel_summary.json"
)

PERMUTATION_SEED = 20260632
PERMUTATION_TRIALS = 1000
TRACE_BOUNDARY = "trace_only_no_unverified_rule_claim"
CLAIM_BOUNDARY = (
    "Purely methodical structural graph-theoretic and data-lineage-oriented audit. "
    "No claim is made about physical geometry, spacetime, metric structure, "
    "gravitation, causality, dynamics, experimental validation, or physical emergence."
)
TRACE_QUERIES = [
    "edge_candidate_flag",
    "theta_edge",
    "16_edge_candidate_result",
    "relation_strength",
    "strength",
    "pair_a",
    "pair_b",
    "abs_delta",
]


def read_json(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def read_csv_rows(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: Path, fieldnames: list[str], rows: list[dict[str, object]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def parse_pair(pair_id: str) -> tuple[int, int]:
    parts = pair_id.split("|")
    if len(parts) != 2:
        raise ValueError(f"Pair-ID does not have i|j form: {pair_id}")
    return int(parts[0]), int(parts[1])


def pair_sort_key(pair_id: str) -> tuple[int, int]:
    return parse_pair(pair_id)


def bool_text(value: bool) -> str:
    return str(value).lower()


def format_float(value: float | None) -> str:
    if value is None:
        return ""
    return repr(float(value))


def stats(values: list[float]) -> dict[str, float | None]:
    if not values:
        return {"min": None, "median": None, "mean": None, "max": None}
    return {
        "min": min(values),
        "median": statistics.median(values),
        "mean": statistics.fmean(values),
        "max": max(values),
    }


def pair_semantics(pair_id: str) -> dict[str, int | str]:
    i, j = parse_pair(pair_id)
    if j > i:
        orientation = "forward"
    elif j < i:
        orientation = "backward"
    else:
        orientation = "diagonal"
    return {
        "i": i,
        "j": j,
        "delta": j - i,
        "abs_delta": abs(j - i),
        "orientation": orientation,
    }


def make_equivalence_rows() -> tuple[list[dict[str, object]], list[dict[str, object]], dict[str, object], set[tuple[str, str]], dict[str, int]]:
    rows: list[dict[str, object]] = []
    mismatches: list[dict[str, object]] = []
    candidate_edges: set[tuple[str, str]] = set()
    pair_abs_delta: dict[str, int] = {}

    for source_row in read_csv_rows(SOURCE_EDGE_FILE):
        pair_a = source_row["pair_a"]
        pair_b = source_row["pair_b"]
        sem_a = pair_semantics(pair_a)
        sem_b = pair_semantics(pair_b)
        pair_abs_delta[pair_a] = int(sem_a["abs_delta"])
        pair_abs_delta[pair_b] = int(sem_b["abs_delta"])
        strength = float(source_row["strength"])
        theta_edge = float(source_row["theta_edge"])
        edge_candidate_flag = int(source_row["edge_candidate_flag"])
        same_abs_delta = sem_a["abs_delta"] == sem_b["abs_delta"]
        expected_flag_by_same_abs_delta = 1 if same_abs_delta else 0
        expected_flag_by_strength_threshold = 1 if strength >= theta_edge else 0
        strength_is_one = strength == 1.0
        audit_row = {
            "pair_a": pair_a,
            "pair_b": pair_b,
            "abs_delta_a": sem_a["abs_delta"],
            "abs_delta_b": sem_b["abs_delta"],
            "same_abs_delta": bool_text(same_abs_delta),
            "strength": format_float(strength),
            "theta_edge": format_float(theta_edge),
            "edge_candidate_flag": edge_candidate_flag,
            "expected_flag_by_same_abs_delta": expected_flag_by_same_abs_delta,
            "expected_flag_by_strength_threshold": expected_flag_by_strength_threshold,
            "flag_matches_same_abs_delta": bool_text(edge_candidate_flag == expected_flag_by_same_abs_delta),
            "flag_matches_strength_threshold": bool_text(edge_candidate_flag == expected_flag_by_strength_threshold),
            "strength_is_one": bool_text(strength_is_one),
            "strength_one_matches_same_abs_delta": bool_text(strength_is_one == same_abs_delta),
        }
        rows.append(audit_row)
        if edge_candidate_flag == 1:
            candidate_edges.add(tuple(sorted((pair_a, pair_b), key=pair_sort_key)))

        mismatch_types: list[str] = []
        if edge_candidate_flag != expected_flag_by_same_abs_delta:
            mismatch_types.append("flag_not_same_abs_delta")
        if edge_candidate_flag != expected_flag_by_strength_threshold:
            mismatch_types.append("flag_not_strength_threshold")
        if strength_is_one != same_abs_delta:
            mismatch_types.append("strength_one_not_same_abs_delta")
        if mismatch_types:
            mismatches.append({**audit_row, "mismatch_type": ";".join(mismatch_types)})

    rows.sort(
        key=lambda row: (
            int(row["abs_delta_a"]),
            int(row["abs_delta_b"]),
            pair_sort_key(str(row["pair_a"])),
            pair_sort_key(str(row["pair_b"])),
        )
    )
    mismatches.sort(key=lambda row: (pair_sort_key(str(row["pair_a"])), pair_sort_key(str(row["pair_b"]))))
    summary = {
        "edge_rows_total": len(rows),
        "candidate_edge_count": sum(1 for row in rows if row["edge_candidate_flag"] == 1),
        "non_candidate_edge_count": sum(1 for row in rows if row["edge_candidate_flag"] == 0),
        "same_abs_delta_edge_count": sum(1 for row in rows if row["same_abs_delta"] == "true"),
        "cross_abs_delta_edge_count": sum(1 for row in rows if row["same_abs_delta"] == "false"),
        "edge_candidate_equivalent_to_same_abs_delta": all(
            row["flag_matches_same_abs_delta"] == "true" for row in rows
        ),
        "edge_candidate_equivalent_to_strength_threshold": all(
            row["flag_matches_strength_threshold"] == "true" for row in rows
        ),
        "strength_one_equivalent_to_same_abs_delta": all(
            row["strength_one_matches_same_abs_delta"] == "true" for row in rows
        ),
        "mismatch_count": len(mismatches),
        "theta_edge_min": min(float(row["theta_edge"]) for row in rows),
        "theta_edge_max": max(float(row["theta_edge"]) for row in rows),
        "within_same_abs_delta_strength_min": min(
            float(row["strength"]) for row in rows if row["same_abs_delta"] == "true"
        ),
        "within_same_abs_delta_strength_max": max(
            float(row["strength"]) for row in rows if row["same_abs_delta"] == "true"
        ),
        "cross_abs_delta_strength_min": min(
            float(row["strength"]) for row in rows if row["same_abs_delta"] == "false"
        ),
        "cross_abs_delta_strength_max": max(
            float(row["strength"]) for row in rows if row["same_abs_delta"] == "false"
        ),
    }
    return rows, mismatches, summary, candidate_edges, pair_abs_delta


def make_threshold_rows(equivalence_rows: list[dict[str, object]]) -> list[dict[str, object]]:
    groups: dict[str, list[dict[str, object]]] = {}
    groups["same_abs_delta=true"] = [row for row in equivalence_rows if row["same_abs_delta"] == "true"]
    groups["same_abs_delta=false"] = [row for row in equivalence_rows if row["same_abs_delta"] == "false"]
    groups["edge_candidate_flag=1"] = [row for row in equivalence_rows if row["edge_candidate_flag"] == 1]
    groups["edge_candidate_flag=0"] = [row for row in equivalence_rows if row["edge_candidate_flag"] == 0]
    abs_pairs = sorted(
        {
            (int(row["abs_delta_a"]), int(row["abs_delta_b"]))
            for row in equivalence_rows
        }
    )
    for abs_a, abs_b in abs_pairs:
        groups[f"abs_delta_pair={abs_a},{abs_b}"] = [
            row
            for row in equivalence_rows
            if int(row["abs_delta_a"]) == abs_a and int(row["abs_delta_b"]) == abs_b
        ]

    output: list[dict[str, object]] = []
    for group_name, rows in groups.items():
        strengths = [float(row["strength"]) for row in rows]
        thetas = [float(row["theta_edge"]) for row in rows]
        margins = [float(row["strength"]) - float(row["theta_edge"]) for row in rows]
        strength_stats = stats(strengths)
        margin_stats = stats(margins)
        output.append(
            {
                "group_name": group_name,
                "edge_rows": len(rows),
                "strength_min": format_float(strength_stats["min"]),
                "strength_median": format_float(strength_stats["median"]),
                "strength_mean": format_float(strength_stats["mean"]),
                "strength_max": format_float(strength_stats["max"]),
                "theta_edge_min": format_float(min(thetas) if thetas else None),
                "theta_edge_max": format_float(max(thetas) if thetas else None),
                "margin_min": format_float(margin_stats["min"]),
                "margin_median": format_float(margin_stats["median"]),
                "margin_mean": format_float(margin_stats["mean"]),
                "margin_max": format_float(margin_stats["max"]),
            }
        )
    return output


def safe_excerpt(line: str) -> str:
    return line.strip().replace("\t", " ")[:240]


def text_files() -> list[Path]:
    suffixes = {
        ".py",
        ".md",
        ".txt",
        ".csv",
        ".json",
        ".yaml",
        ".yml",
        ".toml",
        ".sh",
    }
    candidates: list[Path] = []
    for root in [Path("scripts"), Path("runs"), Path("docs"), Path("data")]:
        if not root.exists():
            continue
        for path in root.rglob("*"):
            if path.is_file() and path.suffix.lower() in suffixes:
                candidates.append(path)
    return sorted(set(candidates), key=lambda path: str(path))


def make_trace_inventory() -> tuple[list[dict[str, object]], str, list[str]]:
    rows: list[dict[str, object]] = []
    raw_lines: list[str] = []
    source_header = ""
    with SOURCE_EDGE_FILE.open("r", encoding="utf-8", newline="") as handle:
        source_header = handle.readline().strip()
    rows.append(
        {
            "trace_type": "primary_file_exists",
            "query_or_item": "16_edge_candidate_result.csv",
            "path": str(SOURCE_EDGE_FILE),
            "line_number": "",
            "excerpt": f"exists={SOURCE_EDGE_FILE.exists()}",
            "interpretation_boundary": TRACE_BOUNDARY,
        }
    )
    rows.append(
        {
            "trace_type": "primary_file_header",
            "query_or_item": "header",
            "path": str(SOURCE_EDGE_FILE),
            "line_number": 1,
            "excerpt": source_header,
            "interpretation_boundary": TRACE_BOUNDARY,
        }
    )
    lineage_values = sorted({row.get("lineage_bundle_sha256", "") for row in read_csv_rows(SOURCE_EDGE_FILE) if row.get("lineage_bundle_sha256", "")})
    for value in lineage_values:
        rows.append(
            {
                "trace_type": "lineage_bundle_sha256",
                "query_or_item": "lineage_bundle_sha256",
                "path": str(SOURCE_EDGE_FILE),
                "line_number": "",
                "excerpt": value,
                "interpretation_boundary": TRACE_BOUNDARY,
            }
        )
    if EXTRACT03_RUN_DIR.exists():
        for path in sorted(EXTRACT03_RUN_DIR.iterdir(), key=lambda item: item.name):
            rows.append(
                {
                    "trace_type": "extract03_run_file",
                    "query_or_item": "run_dir_listing",
                    "path": str(path),
                    "line_number": "",
                    "excerpt": "directory" if path.is_dir() else "file",
                    "interpretation_boundary": TRACE_BOUNDARY,
                }
            )

    files = text_files()
    for query in TRACE_QUERIES:
        query_hits = 0
        raw_lines.append(f"## Query: {query}")
        for path in files:
            try:
                with path.open("r", encoding="utf-8", errors="replace") as handle:
                    for line_number, line in enumerate(handle, start=1):
                        if query in line:
                            raw = f"{path}:{line_number}: {safe_excerpt(line)}"
                            raw_lines.append(raw)
                            if query_hits < 25:
                                rows.append(
                                    {
                                        "trace_type": "repo_text_match",
                                        "query_or_item": query,
                                        "path": str(path),
                                        "line_number": line_number,
                                        "excerpt": safe_excerpt(line),
                                        "interpretation_boundary": TRACE_BOUNDARY,
                                    }
                                )
                            query_hits += 1
            except OSError:
                continue
        raw_lines.append(f"matches={query_hits}")
        raw_lines.append("")

    # Conservative classification: matches in scripts that calculate flag/strength are partial traces,
    # but this audit does not certify full upstream rule reconstruction from snippets alone.
    script_rule_indicators = [
        row
        for row in rows
        if row["trace_type"] == "repo_text_match"
        and str(row["path"]).startswith("scripts/")
        and row["query_or_item"] in {"edge_candidate_flag", "theta_edge", "strength", "pair_a", "pair_b"}
    ]
    if script_rule_indicators:
        status = "upstream_rule_trace_partial"
    else:
        status = "upstream_rule_trace_unresolved"
    return rows, status, raw_lines


def permutation_probe(candidate_edges: set[tuple[str, str]], pair_abs_delta: dict[str, int]) -> tuple[list[dict[str, object]], dict[str, object]]:
    rng = random.Random(PERMUTATION_SEED)
    nodes = sorted(pair_abs_delta, key=pair_sort_key)
    labels = nodes[:]
    output_rows: list[dict[str, object]] = []
    exact_count = 0
    for trial_id in range(1, PERMUTATION_TRIALS + 1):
        shuffled_labels = labels[:]
        rng.shuffle(shuffled_labels)
        node_to_label = dict(zip(nodes, shuffled_labels))
        same_count = 0
        for a, b in candidate_edges:
            label_a = node_to_label[a]
            label_b = node_to_label[b]
            if pair_abs_delta[label_a] == pair_abs_delta[label_b]:
                same_count += 1
        cross_count = len(candidate_edges) - same_count
        exact_preserved = same_count == len(candidate_edges)
        if exact_preserved:
            exact_count += 1
        output_rows.append(
            {
                "trial_id": trial_id,
                "candidate_edges_same_abs_delta_under_permuted_labels": same_count,
                "candidate_edges_cross_abs_delta_under_permuted_labels": cross_count,
                "exact_same_abs_delta_rule_preserved": bool_text(exact_preserved),
            }
        )
    return output_rows, {
        "permutation_trials": PERMUTATION_TRIALS,
        "permutation_exact_rule_preserved_count": exact_count,
        "permutation_exact_rule_preserved_plus_one_p": (exact_count + 1) / (PERMUTATION_TRIALS + 1),
    }


def main() -> None:
    RUN_DIR.mkdir(parents=True, exist_ok=True)
    closure_summary = read_json(CLOSURE_SUMMARY_SOURCE)
    block_structure_summary = read_json(BLOCK_STRUCTURE_SUMMARY_SOURCE)
    block_semantics_summary = read_json(BLOCK_SEMANTICS_SUMMARY_SOURCE)
    _block_strength_summary = read_json(BLOCK_STRENGTH_SUMMARY_SOURCE)
    _nullmodel_summary = read_json(NULLMODEL_SUMMARY_SOURCE)

    equivalence_rows, mismatch_rows, equivalence_summary, candidate_edges, pair_abs_delta = make_equivalence_rows()
    write_csv(
        RUN_DIR / "05_edge_rule_equivalence_audit.csv",
        [
            "pair_a",
            "pair_b",
            "abs_delta_a",
            "abs_delta_b",
            "same_abs_delta",
            "strength",
            "theta_edge",
            "edge_candidate_flag",
            "expected_flag_by_same_abs_delta",
            "expected_flag_by_strength_threshold",
            "flag_matches_same_abs_delta",
            "flag_matches_strength_threshold",
            "strength_is_one",
            "strength_one_matches_same_abs_delta",
        ],
        equivalence_rows,
    )
    write_csv(
        RUN_DIR / "06_rule_mismatch_report.csv",
        [
            "pair_a",
            "pair_b",
            "abs_delta_a",
            "abs_delta_b",
            "same_abs_delta",
            "strength",
            "theta_edge",
            "edge_candidate_flag",
            "expected_flag_by_same_abs_delta",
            "expected_flag_by_strength_threshold",
            "flag_matches_same_abs_delta",
            "flag_matches_strength_threshold",
            "strength_is_one",
            "strength_one_matches_same_abs_delta",
            "mismatch_type",
        ],
        mismatch_rows,
    )
    threshold_rows = make_threshold_rows(equivalence_rows)
    write_csv(
        RUN_DIR / "07_strength_threshold_audit.csv",
        [
            "group_name",
            "edge_rows",
            "strength_min",
            "strength_median",
            "strength_mean",
            "strength_max",
            "theta_edge_min",
            "theta_edge_max",
            "margin_min",
            "margin_median",
            "margin_mean",
            "margin_max",
        ],
        threshold_rows,
    )
    trace_rows, upstream_trace_status, raw_trace_lines = make_trace_inventory()
    write_csv(
        RUN_DIR / "08_upstream_trace_inventory.csv",
        [
            "trace_type",
            "query_or_item",
            "path",
            "line_number",
            "excerpt",
            "interpretation_boundary",
        ],
        trace_rows,
    )
    permutation_rows, permutation_summary = permutation_probe(candidate_edges, pair_abs_delta)
    write_csv(
        RUN_DIR / "09_pair_label_permutation_probe.csv",
        [
            "trial_id",
            "candidate_edges_same_abs_delta_under_permuted_labels",
            "candidate_edges_cross_abs_delta_under_permuted_labels",
            "exact_same_abs_delta_rule_preserved",
        ],
        permutation_rows,
    )

    data_level_origin_status = (
        "candidate_rule_equivalent_to_pair_id_abs_delta_classes_in_current_artifact"
        if equivalence_summary["edge_candidate_equivalent_to_same_abs_delta"]
        and equivalence_summary["strength_one_equivalent_to_same_abs_delta"]
        and equivalence_summary["edge_candidate_equivalent_to_strength_threshold"]
        and equivalence_summary["mismatch_count"] == 0
        else "data_level_origin_requires_review"
    )
    if data_level_origin_status != "data_level_origin_requires_review" and upstream_trace_status == "upstream_rule_trace_found":
        origin_audit_status = "structure_origin_rule_confirmed_from_upstream_and_artifact"
    elif data_level_origin_status != "data_level_origin_requires_review":
        origin_audit_status = "structure_constructively_explained_at_artifact_level_pending_upstream_trace"
    else:
        origin_audit_status = "structure_origin_requires_review"

    summary = {
        "run_id": RUN_ID,
        "source_edge_file": str(SOURCE_EDGE_FILE),
        "closure_summary_source": str(CLOSURE_SUMMARY_SOURCE),
        "block_structure_summary_source": str(BLOCK_STRUCTURE_SUMMARY_SOURCE),
        "block_semantics_summary_source": str(BLOCK_SEMANTICS_SUMMARY_SOURCE),
        "block_strength_summary_source": str(BLOCK_STRENGTH_SUMMARY_SOURCE),
        "nullmodel_summary_source": str(NULLMODEL_SUMMARY_SOURCE),
        **equivalence_summary,
        **permutation_summary,
        "upstream_trace_status": upstream_trace_status,
        "data_level_origin_status": data_level_origin_status,
        "origin_audit_status": origin_audit_status,
        "claim_boundary": CLAIM_BOUNDARY,
    }
    with (RUN_DIR / "04_structure_origin_summary.json").open("w", encoding="utf-8") as handle:
        json.dump(summary, handle, indent=2, ensure_ascii=False)
        handle.write("\n")

    review_note = f"""# QSB-MATRIX-TOPOLOGY-STRUCTURE-ORIGIN-AUDIT

## Source basis

This run uses the EXTRACT03 edge-candidate artifact and the prior closure, block-structure, block-semantics, block-strength, and nullmodel summaries listed in `02_structure_origin_audit_scope.md`.

## Method

The audit parsed Pair-IDs into integer index distances, tested row-wise equivalence between candidate flags, thresholding, `strength == 1.0`, and shared `abs_delta`, inventoried upstream text traces, and ran deterministic Pair-label permutations.

## Data-level rule equivalence

At artifact level, `edge_candidate_flag` is equivalent to shared Pair-ID `abs_delta`: {summary["edge_candidate_equivalent_to_same_abs_delta"]}. `strength == 1.0` is equivalent to shared `abs_delta`: {summary["strength_one_equivalent_to_same_abs_delta"]}. Mismatch count: {summary["mismatch_count"]}.

## Strength and threshold relation

At artifact level, `edge_candidate_flag` is equivalent to `strength >= theta_edge`: {summary["edge_candidate_equivalent_to_strength_threshold"]}. Within same-abs-delta strengths range from {summary["within_same_abs_delta_strength_min"]} to {summary["within_same_abs_delta_strength_max"]}; cross-abs-delta strengths range from {summary["cross_abs_delta_strength_min"]} to {summary["cross_abs_delta_strength_max"]}. Theta range: {summary["theta_edge_min"]} to {summary["theta_edge_max"]}.

## Pair-label permutation probe

Permutation trials: {summary["permutation_trials"]}. Exact rule-preserved count: {summary["permutation_exact_rule_preserved_count"]}. Plus-one p-value: {summary["permutation_exact_rule_preserved_plus_one_p"]}. This probes label binding of the current Pair-ID distance semantics; it is not a recomputation of upstream candidate generation.

## Upstream trace inventory

Trace status: `{summary["upstream_trace_status"]}`. The inventory records file/header/lineage information, run-directory files, and bounded text matches. Text matches are trace evidence only and are not treated as a full upstream rule proof unless explicitly reconstructed.

## Interpretation

The observed clique-block structure is genuine in the candidate graph, but at the current artifact level it is constructively explained by the equivalence between candidate edges and shared Pair-ID index-distance classes. This makes it a robust rule-structured relational pattern, not an independent spacetime or physics claim.

The upstream origin is only stated at the level supported by the trace inventory. If the upstream trace is partial or unresolved, this audit does not claim that the source generation rule has been fully proven from upstream code.

## Claim boundary

This audit is methodical, structural, graph-theoretic, and data-lineage oriented. It makes no physical, geometric, metric, gravitative, causal, dynamical, experimental, or physical-emergence interpretation.

## Next-step gate

Further work should distinguish artifact-level equivalence from upstream rule reconstruction. A stronger origin claim would require direct review of the exact generator path that writes `16_edge_candidate_result.csv`.
"""
    (RUN_DIR / "10_structure_origin_review_note.md").write_text(review_note, encoding="utf-8")

    raw_notes = "# Upstream Trace Raw Grep Notes\n\n" + "\n".join(raw_trace_lines)
    (RUN_DIR / "11_upstream_trace_raw_grep_notes.md").write_text(raw_notes, encoding="utf-8")

    negative_controls = """# Negative Control Recommendations

- Source-/rule-ablation: recompute candidate edges with any Pair-ID distance component removed or masked.
- Label-permuted recomputation: rerun the upstream generator after permuting labels before candidate generation, not only after artifact creation.
- Alternative Pair-ID construction: test whether a different Pair-ID indexing scheme produces the same candidate relation.
- Theta sweeps: vary `theta_edge` and check whether the block structure persists or changes predictably.
- Independent source matrix: compare against a matrix not generated from the same Pair-ID distance logic.
- Upstream quantity comparison: if validated source quantities exist, compare candidate flags against those quantities independently of Pair-ID labels.

These are recommendations only and make no physics claim.
"""
    (RUN_DIR / "12_negative_control_recommendations.md").write_text(negative_controls, encoding="utf-8")

    if closure_summary.get("edge_candidate_rows_total") != summary["edge_rows_total"]:
        raise ValueError("Edge row count differs from closure summary")
    if closure_summary.get("candidate_edge_count") != summary["candidate_edge_count"]:
        raise ValueError("Candidate count differs from closure summary")
    if block_structure_summary.get("candidate_edge_count") != summary["candidate_edge_count"]:
        raise ValueError("Candidate count differs from block-structure summary")
    if block_semantics_summary.get("node_count") != len(pair_abs_delta):
        raise ValueError("Node count differs from block-semantics summary")


if __name__ == "__main__":
    main()
