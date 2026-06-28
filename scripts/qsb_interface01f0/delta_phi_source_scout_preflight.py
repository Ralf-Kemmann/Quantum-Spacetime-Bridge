#!/usr/bin/env python3
"""Read-only repository scout for operational delta_phi_ij source candidates."""

from __future__ import annotations

import csv
import json
import re
import sqlite3
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable


REPO = Path(__file__).resolve().parents[2]
OUTPUT = REPO / "runs/QSB-INTERFACE01F0/delta_phi_source_scout_provenance_preflight"
SCRIPT_DIR = REPO / "scripts/qsb_interface01f0"
SUPPORTED = {".csv", ".tsv", ".json", ".jsonl", ".md", ".txt", ".py", ".sql", ".sqlite", ".db"}
SKIP_PARTS = {".git", ".venv", "__pycache__", "node_modules"}
MAX_TEXT_BYTES = 2_000_000
MAX_STRUCTURED_BYTES = 20_000_000
MAX_TEXT_HITS = 2500
MAX_HITS_PER_FILE = 12
MAX_SAMPLE_ROWS = 5

PHASE_TERMS = [
    "delta_phi_ij", "delta_phi", "phase_delta", "phase_difference", "relative_phase",
    "relative_phase_delta", "phi_i", "phi_j", "phase_i", "phase_j", "phi_rel",
    "dphi", "phase_relation", "phase_pair",
]
PAIR_TERMS = [
    "i", "j", "idx_i", "idx_j", "node_i", "node_j", "source_i", "target_j",
    "pair_i", "pair_j", "material_i", "material_j", "isotope_i", "isotope_j",
    "pair_id", "source_id", "target_id", "wave_id_i", "wave_id_j",
]
UNIT_TERMS = ["unit", "units", "dimension", "radian", "radians", "angle", "dimensionless"]
PROVENANCE_TERMS = [
    "source", "source_id", "source_file", "source_path", "run_id", "record_id", "checksum",
    "sha256", "provenance", "derivation", "construction_rule", "origin", "input_file",
]
EXPLICIT_DELTA_MARKERS = [
    "delta_phi_ij", "delta_phi", "phase_delta", "phase_difference", "relative_phase",
    "relative_phase_delta", "phi_rel", "dphi", "circular_phase_delta", "naive_phase_delta",
]
PHI_I_MARKERS = {"phi_i", "phase_i"}
PHI_J_MARKERS = {"phi_j", "phase_j"}
SYNTHETIC_MARKERS = [
    "synthetic", "toy", "proxy", "phase_is_physical,false", '"phase_is_physical": false',
    "diagnostic only", "not a physical phase", "no physical phase", "play data",
]
PERIODIC_MARKERS = [
    "delta_phi_wrapped", "wrapped_delta_phi", "cos_delta_phi", "sin_delta_phi", "circular_phase",
    "2pi", "2*pi", "2π", "atan2(sin", "modulo 2",
]
POSTHOC_MARKERS = ["post-hoc", "post hoc", "result-driven", "outcome-driven", "tuning"]


def rel(path: Path) -> str:
    return path.relative_to(REPO).as_posix()


def clean_name(value: str) -> str:
    return re.sub(r"[^a-z0-9_]+", "_", value.strip().lower()).strip("_")


def matches_phase(name: str) -> str | None:
    normalized = clean_name(name)
    for term in PHASE_TERMS:
        if term in normalized:
            return term
    return None


def write_csv(name: str, fields: list[str], rows: list[dict[str, Any]]) -> None:
    with (OUTPUT / name).open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def iter_files() -> Iterable[Path]:
    for path in sorted(REPO.rglob("*")):
        if not path.is_file() or path.suffix.lower() not in SUPPORTED:
            continue
        if any(part in SKIP_PARTS for part in path.parts):
            continue
        if OUTPUT in path.parents or SCRIPT_DIR in path.parents:
            continue
        yield path


def read_text_bounded(path: Path, byte_limit: int = MAX_TEXT_BYTES) -> str:
    try:
        with path.open("rb") as handle:
            data = handle.read(byte_limit + 1)
        if len(data) > byte_limit:
            data = data[:byte_limit]
        return data.decode("utf-8", errors="replace")
    except OSError:
        return ""


def directory_context(path: Path) -> str:
    chunks = []
    for name in ("readout.md", "summary.json", "resolved_config.json", "run_summary.json"):
        sibling = path.parent / name
        if sibling.is_file() and sibling != path:
            chunks.append(read_text_bounded(sibling, 80_000))
    return "\n".join(chunks).lower()


def hit_class(path: Path) -> str:
    lower = rel(path).lower()
    if "prompt" in lower:
        return "prompt_reference"
    if path.suffix.lower() in {".py", ".sql"}:
        return "code_reference"
    if "/runs/" in f"/{lower}" or lower.startswith("runs/"):
        return "result_reference"
    if "spec" in lower or "plan" in lower:
        return "spec_reference"
    if path.suffix.lower() in {".md", ".txt"}:
        return "doc_reference"
    return "ambiguous_text_reference"


def collect_text_hits(files: list[Path]) -> list[dict[str, Any]]:
    hits: list[dict[str, Any]] = []
    for path in files:
        if len(hits) >= MAX_TEXT_HITS or path.suffix.lower() in {".sqlite", ".db"}:
            continue
        text = read_text_bounded(path)
        if not text:
            continue
        per_file = 0
        for line_number, line in enumerate(text.splitlines(), 1):
            lower = line.lower()
            for term in PHASE_TERMS:
                if term in lower:
                    context = re.sub(r"\s+", " ", line.strip())[:240]
                    cls = hit_class(path)
                    relevance = "textual_reference_only" if cls in {"prompt_reference", "spec_reference", "doc_reference", "code_reference"} else "review_structured_source_separately"
                    hits.append({
                        "hit_id": f"HIT-{len(hits)+1:05d}", "relative_path": rel(path),
                        "file_type": path.suffix.lower().lstrip("."), "term": term,
                        "line_number": line_number, "context_snippet": context,
                        "hit_class": cls, "candidate_relevance": relevance,
                        "review_note": "Short bounded snippet; occurrence alone is not an operational source.",
                    })
                    per_file += 1
                    break
            if per_file >= MAX_HITS_PER_FILE or len(hits) >= MAX_TEXT_HITS:
                break
    return hits


def flatten_json_keys(value: Any, prefix: str = "root", depth: int = 0,
                      limit: int = 2000) -> list[tuple[str, list[str], Any]]:
    found: list[tuple[str, list[str], Any]] = []
    if depth > 8:
        return found
    if isinstance(value, dict):
        keys = [str(key) for key in value.keys()]
        for key, child in value.items():
            found.append((prefix, keys, key))
            if len(found) >= limit:
                break
            found.extend(flatten_json_keys(child, f"{prefix}.{key}", depth + 1, limit - len(found)))
            if len(found) >= limit:
                break
    elif isinstance(value, list):
        for index, child in enumerate(value[:20]):
            found.extend(flatten_json_keys(child, f"{prefix}[{index}]", depth + 1, limit - len(found)))
            if len(found) >= limit:
                break
    return found


def structured_objects(path: Path) -> list[dict[str, Any]]:
    suffix = path.suffix.lower()
    objects: list[dict[str, Any]] = []
    try:
        if suffix in {".csv", ".tsv"}:
            delimiter = "\t" if suffix == ".tsv" else ","
            with path.open(encoding="utf-8-sig", newline="", errors="replace") as handle:
                reader = csv.reader(handle, delimiter=delimiter)
                header = next(reader, [])
                samples = [row for _, row in zip(range(MAX_SAMPLE_ROWS), reader)]
            objects.append({"container_type": suffix.lstrip("."), "object": "header", "columns": header, "samples": samples})
        elif suffix == ".json" and path.stat().st_size <= MAX_STRUCTURED_BYTES:
            value = json.loads(path.read_text(encoding="utf-8", errors="replace"))
            grouped: dict[str, set[str]] = defaultdict(set)
            for object_path, keys, key in flatten_json_keys(value):
                grouped[object_path].update(keys)
            for object_path, keys in list(grouped.items())[:200]:
                objects.append({"container_type": "json", "object": object_path, "columns": sorted(keys), "samples": []})
        elif suffix == ".jsonl":
            grouped: set[str] = set()
            samples = []
            with path.open(encoding="utf-8", errors="replace") as handle:
                for _, line in zip(range(20), handle):
                    try:
                        item = json.loads(line)
                    except json.JSONDecodeError:
                        continue
                    if isinstance(item, dict):
                        grouped.update(str(key) for key in item)
                        samples.append(item)
            objects.append({"container_type": "jsonl", "object": "records", "columns": sorted(grouped), "samples": samples[:MAX_SAMPLE_ROWS]})
        elif suffix in {".sqlite", ".db"}:
            connection = sqlite3.connect(f"file:{path.resolve()}?mode=ro", uri=True)
            names = connection.execute(
                "SELECT type,name FROM sqlite_master WHERE type IN ('table','view') "
                "AND name NOT LIKE 'sqlite_%' ORDER BY type,name"
            ).fetchall()
            for object_type, name in names:
                columns = [row[1] for row in connection.execute(f'PRAGMA table_info("{name}")')]
                samples: list[Any] = []
                if any(matches_phase(column) for column in columns):
                    try:
                        samples = connection.execute(f'SELECT * FROM "{name}" LIMIT {MAX_SAMPLE_ROWS}').fetchall()
                    except sqlite3.Error:
                        samples = []
                objects.append({"container_type": f"sqlite_{object_type}", "object": name, "columns": columns, "samples": samples})
            connection.close()
    except (OSError, csv.Error, json.JSONDecodeError, sqlite3.Error, UnicodeError):
        return []
    return objects


def nearby(columns: list[str], terms: list[str]) -> str:
    normalized = [(column, clean_name(column)) for column in columns]
    result = [column for column, clean in normalized if clean in terms or any(term in clean for term in terms if len(term) > 2)]
    return ";".join(result[:20]) or "none_detected"


def collect_structured_hits(files: list[Path]) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    hits: list[dict[str, Any]] = []
    containers: list[dict[str, Any]] = []
    for path in files:
        if path.suffix.lower() not in {".csv", ".tsv", ".json", ".jsonl", ".sqlite", ".db"}:
            continue
        for obj in structured_objects(path):
            columns = [str(column) for column in obj["columns"]]
            matched = [(column, matches_phase(column)) for column in columns if matches_phase(column)]
            if not matched:
                continue
            sample_text = json.dumps(obj["samples"], ensure_ascii=False, default=str)[:10_000]
            context = (sample_text + "\n" + directory_context(path)).lower()
            container = {
                "relative_path": rel(path), "container_type": obj["container_type"],
                "table_or_object": obj["object"], "columns": columns,
                "matched": matched, "sample_text": sample_text, "context": context,
            }
            containers.append(container)
            for column, term in matched:
                hits.append({
                    "column_hit_id": f"COL-{len(hits)+1:05d}", "relative_path": rel(path),
                    "container_type": obj["container_type"], "table_or_object": obj["object"],
                    "column_or_key": column, "matched_term": term,
                    "nearby_pair_fields": nearby(columns, PAIR_TERMS),
                    "nearby_unit_fields": nearby(columns, UNIT_TERMS),
                    "nearby_provenance_fields": nearby(columns, PROVENANCE_TERMS),
                    "sample_checked": f"yes_bounded_max_{MAX_SAMPLE_ROWS}_rows" if obj["samples"] else "schema_or_header_only",
                    "candidate_relevance": "structured_phase_like_field",
                    "review_note": "Column/key match requires P01-P09 assessment; name alone is insufficient.",
                })
    return hits, containers


def has_pair_structure(columns: list[str]) -> bool:
    names = {clean_name(column) for column in columns}
    direct_pairs = [
        ({"i", "j"}), ({"idx_i", "idx_j"}), ({"node_i", "node_j"}),
        ({"pair_i", "pair_j"}), ({"material_i", "material_j"}),
        ({"isotope_i", "isotope_j"}), ({"phi_i", "phi_j"}), ({"phase_i", "phase_j"}),
        ({"wave_id_i", "wave_id_j"}), ({"source_id", "target_id"}),
    ]
    return "pair_id" in names or any(pair <= names for pair in direct_pairs)


def assess_candidates(containers: list[dict[str, Any]]) -> list[dict[str, Any]]:
    assessments = []
    seen = set()
    for container in containers:
        key = (container["relative_path"], container["table_or_object"])
        if key in seen:
            continue
        seen.add(key)
        columns = container["columns"]
        names = {clean_name(column) for column in columns}
        matched_names = [clean_name(column) for column, _ in container["matched"]]
        path_lower = container["relative_path"].lower()
        context = container["context"]
        combined = " ".join(matched_names) + " " + context
        explicit = any(any(marker in name for marker in EXPLICIT_DELTA_MARKERS) for name in matched_names)
        phi_only = bool(names & PHI_I_MARKERS) and bool(names & PHI_J_MARKERS) and not explicit
        pair = has_pair_structure(columns)
        synthetic = any(marker in path_lower or marker in context for marker in SYNTHETIC_MARKERS)
        interface_reference = "qsb-interface01" in path_lower or "interface01" in path_lower
        periodic = any(marker in combined for marker in PERIODIC_MARKERS)
        unit_documented = any(marker in combined for marker in ("radian", "dimensionless", "angle unit", "phase_unit"))
        provenance_fields = nearby(columns, PROVENANCE_TERMS) != "none_detected"
        source_context = any(marker in context for marker in ("source", "input", "derivation", "construction"))
        provenance = provenance_fields and source_context and not synthetic
        theta_reuse = "0.0300" in context and "theta" in context
        mixing = any(marker in context for marker in ("lambda_db", "energy_j", "mass_u")) and "model_units" in context
        posthoc = any(marker in context for marker in POSTHOC_MARKERS)

        if interface_reference:
            candidate_class = "textual_reference_only"
            operational = "not_operational"
            note = "INTERFACE specification/review output describes requirements but is not a phase source."
        elif synthetic:
            candidate_class = "not_a_candidate"
            operational = "not_operational"
            note = "Explicit synthetic/toy/proxy/diagnostic boundary detected; cannot close provenance-secured G02."
        elif explicit and pair:
            if unit_documented and periodic and provenance and not theta_reuse and not mixing and not posthoc:
                candidate_class = "operational_candidate"
                operational = "candidate_found"
                note = "Automated P01-P09 preflight appears complete; human authorization is still required."
            else:
                candidate_class = "ambiguous_requires_human_review"
                operational = "ambiguous"
                note = "Pairwise phase-like quantity found, but units/periodicity/provenance or risk checks are incomplete."
        elif phi_only and pair:
            candidate_class = "derivable_only_not_authorized"
            operational = "not_operational"
            note = "phi_i/phi_j-like fields exist without a locally authorized delta_phi_ij derivation in this container."
        else:
            candidate_class = "not_a_candidate"
            operational = "not_operational"
            note = "Phase-like key lacks explicit operational pairwise relative-phase structure."

        assessments.append({
            "candidate_id": f"CAND-{len(assessments)+1:04d}",
            "relative_path": container["relative_path"], "container_type": container["container_type"],
            "table_or_object": container["table_or_object"],
            "candidate_quantity_name": ";".join(sorted(set(matched_names))),
            "candidate_class": candidate_class,
            "has_pairwise_ij_structure": str(pair).lower(),
            "has_explicit_delta_phi_ij": str(explicit).lower(),
            "has_phi_i_phi_j_only": str(phi_only).lower(),
            "dimension_or_unit_status": "dimensionless_or_angle_documented" if unit_documented else "missing_or_review",
            "periodicity_status": "documented_or_directly_enforceable" if periodic else "missing_or_review",
            "provenance_status": "traceable_preflight" if provenance else "partial_or_missing",
            "phase_d_theta_reuse_risk": "detected_review" if theta_reuse else "none_detected",
            "si_model_unit_mixing_risk": "detected_review" if mixing else "none_detected",
            "posthoc_tuning_risk": "detected_review" if posthoc else "none_detected",
            "operational_status": operational,
            "blocks_g02_closure": "no_pending_human_authorization" if operational == "candidate_found" else "yes",
            "review_note": note,
        })
    return assessments


def preflight_matrix(assessments: list[dict[str, Any]]) -> list[dict[str, Any]]:
    conditions = [
        ("P01", "explicit pairwise i-j structure exists"),
        ("P02", "explicit delta_phi_ij or equivalent exists"),
        ("P03", "dimensionless/angle/radian convention compatible"),
        ("P04", "2pi-periodic handling documented or directly enforceable"),
        ("P05", "provenance traceable to raw source or authorized derivation"),
        ("P06", "no hidden Phase-D theta=0.0300 reuse"),
        ("P07", "no MATERIAL01 SI and Phase-D model-unit mixing"),
        ("P08", "no post-hoc selection or result-driven thresholding"),
        ("P09", "feeds frozen INTERFACE01 chain without policy changes"),
    ]
    rows = []
    relevant = [row for row in assessments if row["candidate_class"] not in {"not_a_candidate", "textual_reference_only"}]
    for candidate in relevant:
        observed = {
            "P01": candidate["has_pairwise_ij_structure"] == "true",
            "P02": candidate["has_explicit_delta_phi_ij"] == "true",
            "P03": candidate["dimension_or_unit_status"] == "dimensionless_or_angle_documented",
            "P04": candidate["periodicity_status"] == "documented_or_directly_enforceable",
            "P05": candidate["provenance_status"] == "traceable_preflight",
            "P06": candidate["phase_d_theta_reuse_risk"] == "none_detected",
            "P07": candidate["si_model_unit_mixing_risk"] == "none_detected",
            "P08": candidate["posthoc_tuning_risk"] == "none_detected",
            "P09": candidate["operational_status"] == "candidate_found",
        }
        for condition_id, label in conditions:
            value = observed[condition_id]
            rows.append({
                "candidate_id": candidate["candidate_id"], "condition_id": condition_id,
                "condition_label": label, "required_status": "pass",
                "observed_status": "present/clear" if value else "missing/unclear",
                "pass_fail_review": "pass" if value else "review" if condition_id in {"P03", "P04", "P05", "P08"} else "fail",
                "supporting_path": candidate["relative_path"],
                "supporting_field_or_line": candidate["candidate_quantity_name"],
                "review_note": "Automated bounded preflight; review cannot upgrade absent provenance by assumption.",
            })
    return rows


def main() -> None:
    if OUTPUT.exists():
        raise SystemExit(f"Refusing to overwrite existing output directory: {rel(OUTPUT)}")
    OUTPUT.mkdir(parents=True)

    files = list(iter_files())
    terms = []
    for index, term in enumerate(PHASE_TERMS + PAIR_TERMS, 1):
        group = "phase_quantity" if index <= len(PHASE_TERMS) else "pair_structure"
        terms.append({
            "term_id": f"TERM-{index:03d}", "term": term, "term_group": group,
            "purpose": "Locate explicit relative-phase quantity or derivation fields." if group == "phase_quantity" else "Establish explicit pairwise i-j structure.",
            "required_for_operational_candidate": "yes" if group == "phase_quantity" or term in {"i", "j", "pair_id"} else "supporting_alternative",
        })
    write_csv("01_interface01f0_search_terms.csv", ["term_id", "term", "term_group", "purpose", "required_for_operational_candidate"], terms)

    text_hits = collect_text_hits(files)
    write_csv("02_interface01f0_text_hits.csv", ["hit_id", "relative_path", "file_type", "term", "line_number", "context_snippet", "hit_class", "candidate_relevance", "review_note"], text_hits)

    structured_hits, containers = collect_structured_hits(files)
    write_csv("03_interface01f0_structured_column_hits.csv", ["column_hit_id", "relative_path", "container_type", "table_or_object", "column_or_key", "matched_term", "nearby_pair_fields", "nearby_unit_fields", "nearby_provenance_fields", "sample_checked", "candidate_relevance", "review_note"], structured_hits)

    assessments = assess_candidates(containers)
    write_csv("04_interface01f0_candidate_source_assessment.csv", ["candidate_id", "relative_path", "container_type", "table_or_object", "candidate_quantity_name", "candidate_class", "has_pairwise_ij_structure", "has_explicit_delta_phi_ij", "has_phi_i_phi_j_only", "dimension_or_unit_status", "periodicity_status", "provenance_status", "phase_d_theta_reuse_risk", "si_model_unit_mixing_risk", "posthoc_tuning_risk", "operational_status", "blocks_g02_closure", "review_note"], assessments)

    matrix = preflight_matrix(assessments)
    write_csv("05_interface01f0_provenance_preflight_matrix.csv", ["candidate_id", "condition_id", "condition_label", "required_status", "observed_status", "pass_fail_review", "supporting_path", "supporting_field_or_line", "review_note"], matrix)

    operational = [row for row in assessments if row["operational_status"] == "candidate_found"]
    ambiguous = [row for row in assessments if row["operational_status"] == "ambiguous"]
    if len(operational) == 1 and not ambiguous:
        result = "candidate_found"
        status = "interface01f0_delta_phi_source_scout_completed_candidate_found_for_human_authorization"
        sufficiency = "one_operational_candidate_preflight_requires_human_authorization"
        g02 = "candidate_found_for_human_authorization"
        action = "Human Authorization + read-only staging of the single candidate, then recompute G02/G13."
    elif operational or ambiguous:
        result = "ambiguous"
        status = "interface01f0_delta_phi_source_scout_completed_ambiguous_requires_human_review"
        sufficiency = "candidate_traces_found_but_p01_p09_not_uniquely_satisfied"
        g02 = "ambiguous_requires_human_review"
        action = "Review the bounded ambiguous candidates for units, periodicity, and authorized provenance; do not stage until one passes P01-P09."
    else:
        result = "not_found"
        status = "interface01f0_delta_phi_source_scout_completed_no_operational_source_found"
        sufficiency = "repository_scan_sufficient_no_operational_source"
        g02 = "unresolved_blocker"
        action = "Provide an authorized provenance-secured delta_phi_ij source; do not generate a replacement in F0."

    decisions = [
        {"decision_id":"DEC-01","gate_id":"G02","previous_status":"unresolved_blocker","preflight_status":g02,"can_close_gate_now":"no","can_conditionally_close_gate_now":"yes_pending_human_authorization" if result == "candidate_found" else "no","blocks_execution_later":"yes","recommended_next_action":action,"review_note":"F0 is source preflight only and cannot authorize or repair a source."},
        {"decision_id":"DEC-02","gate_id":"G13","previous_status":"no_go_unresolved_blockers","preflight_status":"no_go","can_close_gate_now":"no","can_conditionally_close_gate_now":"no","blocks_execution_later":"yes","recommended_next_action":"Keep G13 no-go until an authorized staged source closes G02 and gates are recomputed.","review_note":"F0 must never mark G13 go."},
    ]
    write_csv("06_interface01f0_g02_g13_preflight_decision.csv", ["decision_id", "gate_id", "previous_status", "preflight_status", "can_close_gate_now", "can_conditionally_close_gate_now", "blocks_execution_later", "recommended_next_action", "review_note"], decisions)

    note = f"""# INTERFACE01-F0 Final Result

## Status
`{status}`

## What was scanned
Read-only scan of `{len(files)}` supported local files (`csv`, `tsv`, `json`, `jsonl`, `md`, `txt`, `py`, `sql`, `sqlite`, `db`). Generated F0 paths, caches, environments, archives, and unsupported binaries were excluded. SQLite access used read-only mode and bounded samples only for phase-like schemas.

## Candidate decision
Decision: `{result}`.

Structured candidate assessments: {len(assessments)}. Operational candidates passing automated P01-P09 preflight: {len(operational)}. Ambiguous candidates: {len(ambiguous)}.

Explicit synthetic/toy/proxy phase tables remain non-operational for G02. Text in plans, prompts, code, or result notes remains a reference, not a source. Pairwise phase-like tables with incomplete unit, periodicity, or provenance documentation remain review items.

## G02/G13 preflight decision
- G02: `{g02}`; cannot close now.
- G13: `no_go`.

## Blocking review items
- An operational source must pass all P01-P09 conditions in one traceable source/authorized derivation chain.
- Promising aggregate or pairwise fields cannot be upgraded by column naming alone.
- Synthetic diagnostic phase exposure cannot substitute for an authorized operational source.

## Claim boundary
Candidate-interface source preflight only; no physics result, no minimal-test execution, and no claim about spacetime or gravitation.

## Recommended next smallest action
{action}
"""
    (OUTPUT / "INTERFACE01F0_FINAL_RESULT_NOTE.md").write_text(note, encoding="utf-8")

    output_names = [
        "01_interface01f0_search_terms.csv", "02_interface01f0_text_hits.csv",
        "03_interface01f0_structured_column_hits.csv", "04_interface01f0_candidate_source_assessment.csv",
        "05_interface01f0_provenance_preflight_matrix.csv", "06_interface01f0_g02_g13_preflight_decision.csv",
        "INTERFACE01F0_FINAL_RESULT_NOTE.md", "INTERFACE01F0_RUN_MANIFEST.json",
    ]
    manifest = {
        "run_id": "QSB-INTERFACE01F0", "title": "delta_phi_ij Source Scout / Provenance Preflight",
        "created_at_utc": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "repo_root": str(REPO), "status": status, "input_sufficiency": sufficiency,
        "outputs": output_names, "files_scanned": len(files), "text_hits": len(text_hits),
        "structured_column_hits": len(structured_hits), "candidate_count": len(assessments),
        "operational_candidate_count": len(operational), "ambiguous_candidate_count": len(ambiguous),
        "g02_preflight_status": g02, "g13_preflight_status": "no_go",
        "mutated_existing_files": False, "generated_synthetic_evidence": False,
        "sqlite_access_mode": "read_only", "claim_boundary": "candidate-interface source preflight only; no physics result",
    }
    (OUTPUT / "INTERFACE01F0_RUN_MANIFEST.json").write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    print(json.dumps(manifest, ensure_ascii=False))


if __name__ == "__main__":
    main()
