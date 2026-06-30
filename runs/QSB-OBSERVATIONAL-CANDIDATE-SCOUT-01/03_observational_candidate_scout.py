#!/usr/bin/env python3
"""Create an observational candidate scout scaffold for QSB."""

from __future__ import annotations

import csv
import json
import re
import subprocess
from pathlib import Path


RUN_ID = "QSB-OBSERVATIONAL-CANDIDATE-SCOUT-01"
RUN_DIR = Path("runs") / RUN_ID
CLAIM_BOUNDARY = [
    "observational_candidate_scout",
    "methodological_prioritization",
    "observable_contract_preparation",
    "no_physics_claim",
    "no_qsb_detection_claim",
    "no_spacetime_claim",
    "no_gravity_claim",
    "no_causality_claim",
]
INPUT_CANDIDATES = [
    RUN_DIR / "input/deep_research_report.md",
    RUN_DIR / "input/deep_research_report.txt",
    RUN_DIR / "input/deep_research_report.json",
    Path("docs/QSB_OBSERVATIONAL_CANDIDATE_SCOUT_01_DEEP_RESEARCH_REPORT.md"),
    Path("docs/QSB_OBSERVATIONAL_CANDIDATE_SCOUT_01_DEEP_RESEARCH_REPORT.txt"),
]


FIELD_COLUMNS = [
    "candidate_id",
    "candidate_name",
    "domain",
    "short_description",
    "primary_observables",
    "established_explanation",
    "open_questions_or_residuals",
    "qsb_relevance_hypothesis",
    "why_not_qsb",
    "public_data_sources",
    "reproducibility_notes",
    "systematic_risks",
    "overclaim_risks",
    "first_minimal_test",
    "recommended_run_id",
    "priority",
]

SCORE_COLUMNS = [
    "candidate_id",
    "score_qsb_mechanistic_proximity",
    "score_data_accessibility",
    "score_reproducibility",
    "score_standard_physics_separability",
    "score_overclaim_risk_control",
    "score_minimal_test_effort",
    "score_clear_observable_potential",
    "score_total",
    "rank",
    "score_source",
    "notes",
]


def run_command(args: list[str]) -> str:
    completed = subprocess.run(args, check=False, text=True, capture_output=True)
    text = completed.stdout
    if completed.stderr:
        text += completed.stderr
    return text


def write_text(path: Path, text: str) -> None:
    path.write_text(text, encoding="utf-8")


def write_csv(path: Path, fieldnames: list[str], rows: list[dict[str, object]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, lineterminator="\n", extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def find_deep_research_input() -> Path | None:
    for path in INPUT_CANDIDATES:
        if path.exists():
            return path
    return None


def read_deep_research(path: Path | None) -> tuple[str, dict]:
    if path is None:
        return "", {}
    text = path.read_text(encoding="utf-8", errors="replace")
    if path.suffix.lower() == ".json":
        try:
            return text, json.loads(text)
        except json.JSONDecodeError:
            return text, {"json_parse_error": True}
    return text, {}


def base_candidates() -> list[dict[str, object]]:
    return [
        {
            "candidate_id": "A_matterwave_interferometry",
            "candidate_name": "Matter-wave / interferometry coherence fields",
            "domain": "laboratory_quantum_interference",
            "short_description": "Candidate field for later observable contracts around controlled matter-wave phase, coherence, interference, and coupling residuals.",
            "primary_observables": "not_available_without_deep_research_input",
            "established_explanation": "not_available_without_deep_research_input",
            "open_questions_or_residuals": "not_available_without_deep_research_input",
            "qsb_relevance_hypothesis": "Prepared as a mechanistic-near search space for phase/interference/coupling patterns; no QSB claim.",
            "why_not_qsb": "Standard quantum, environmental, instrumental, and modeling explanations must be separated first.",
            "public_data_sources": "not_available_without_deep_research_input",
            "reproducibility_notes": "Requires source inventory and reproducible protocol after deep research input.",
            "systematic_risks": "not_available_without_deep_research_input",
            "overclaim_risks": "High if interpreted as new physics before null models and standard controls.",
            "first_minimal_test": "Define observable columns and null controls after literature/data ingest.",
            "recommended_run_id": "QSB-OBS-MATTERWAVE-OBSERVABLE-CONTRACT-01",
            "priority": "high_seed",
        },
        {
            "candidate_id": "B_sparc_radial_acceleration_relation",
            "candidate_name": "SPARC / radial acceleration relation",
            "domain": "galaxy_rotation_scaling_relations",
            "short_description": "Candidate field for later observable contracts around galaxy acceleration relation residuals and model separability.",
            "primary_observables": "not_available_without_deep_research_input",
            "established_explanation": "not_available_without_deep_research_input",
            "open_questions_or_residuals": "not_available_without_deep_research_input",
            "qsb_relevance_hypothesis": "Prepared as a relational-pattern search space; no QSB or dark-matter claim.",
            "why_not_qsb": "Astrophysical modeling, baryonic systematics, dark-matter modeling, selection effects, and calibration must be separated first.",
            "public_data_sources": "not_available_without_deep_research_input",
            "reproducibility_notes": "Requires dataset contract and baseline reproduction plan after deep research input.",
            "systematic_risks": "not_available_without_deep_research_input",
            "overclaim_risks": "Very high if framed as an alternative gravity or dark-matter explanation.",
            "first_minimal_test": "Define residual-only contract and standard-baseline comparison after literature/data ingest.",
            "recommended_run_id": "QSB-OBS-SPARC-RAR-RESIDUAL-CONTRACT-01",
            "priority": "high_seed",
        },
        {
            "candidate_id": "C_fast_radio_bursts",
            "candidate_name": "Fast radio burst path-residual scout",
            "domain": "transient_radio_astrophysics",
            "short_description": "Candidate field for later observable contracts around repeatability, dispersion/path residuals, and environment controls.",
            "primary_observables": "not_available_without_deep_research_input",
            "established_explanation": "not_available_without_deep_research_input",
            "open_questions_or_residuals": "not_available_without_deep_research_input",
            "qsb_relevance_hypothesis": "Prepared as a path/residual search space; no QSB signal claim.",
            "why_not_qsb": "Source physics, propagation, plasma effects, selection, and instrument pipelines must be controlled first.",
            "public_data_sources": "not_available_without_deep_research_input",
            "reproducibility_notes": "Requires event catalog and observable definitions after deep research input.",
            "systematic_risks": "not_available_without_deep_research_input",
            "overclaim_risks": "High if residuals are interpreted without astrophysical and instrumental baselines.",
            "first_minimal_test": "Build catalog-level path-residual schema after source ingest.",
            "recommended_run_id": "QSB-OBS-FRB-PATH-RESIDUAL-CONTRACT-01",
            "priority": "medium_high_seed",
        },
        {
            "candidate_id": "D_pulsar_timing_arrays",
            "candidate_name": "Pulsar timing array residual contracts",
            "domain": "precision_timing_gravitational_wave_background",
            "short_description": "Candidate field for later observable contracts around timing residuals and correlation structures.",
            "primary_observables": "not_available_without_deep_research_input",
            "established_explanation": "not_available_without_deep_research_input",
            "open_questions_or_residuals": "not_available_without_deep_research_input",
            "qsb_relevance_hypothesis": "Prepared as a correlation/residual search space; no gravitational or causal claim.",
            "why_not_qsb": "Timing noise, ephemeris, gravitational-wave-background models, and analysis pipelines must be separated first.",
            "public_data_sources": "not_available_without_deep_research_input",
            "reproducibility_notes": "Requires public data inventory and baseline model contract after deep research input.",
            "systematic_risks": "not_available_without_deep_research_input",
            "overclaim_risks": "Very high if connected to gravity or spacetime without validated controls.",
            "first_minimal_test": "Prepare timing residual field list and null-correlation controls.",
            "recommended_run_id": "QSB-OBS-PTA-RESIDUAL-CONTRACT-01",
            "priority": "medium_seed",
        },
        {
            "candidate_id": "E_gravitational_lensing_substructure",
            "candidate_name": "Gravitational lensing substructure residuals",
            "domain": "strong_lensing_substructure",
            "short_description": "Candidate field for later observable contracts around lensing residuals and substructure model controls.",
            "primary_observables": "not_available_without_deep_research_input",
            "established_explanation": "not_available_without_deep_research_input",
            "open_questions_or_residuals": "not_available_without_deep_research_input",
            "qsb_relevance_hypothesis": "Prepared as a structured-residual search space; no lensing or gravity claim.",
            "why_not_qsb": "Mass modeling, line-of-sight structure, baryonic effects, and selection must be separated first.",
            "public_data_sources": "not_available_without_deep_research_input",
            "reproducibility_notes": "Requires reproducible lens sample and model-comparison plan after deep research input.",
            "systematic_risks": "not_available_without_deep_research_input",
            "overclaim_risks": "Very high if framed as gravity or dark-sector evidence.",
            "first_minimal_test": "Define residual feature table and standard lens-model baseline.",
            "recommended_run_id": "QSB-OBS-LENSING-SUBSTRUCTURE-CONTRACT-01",
            "priority": "medium_late_seed",
        },
        {
            "candidate_id": "F_spectroscopy_fundamental_constants",
            "candidate_name": "Spectroscopy / fundamental-constant constraint fields",
            "domain": "precision_spectroscopy_constraints",
            "short_description": "Candidate field for later observable contracts around precision spectral residuals and constraint reproducibility.",
            "primary_observables": "not_available_without_deep_research_input",
            "established_explanation": "not_available_without_deep_research_input",
            "open_questions_or_residuals": "not_available_without_deep_research_input",
            "qsb_relevance_hypothesis": "Prepared as a constraint-field search space; no variation or new-physics claim.",
            "why_not_qsb": "Calibration, astrophysical environments, atomic data, and instrument systematics must be controlled first.",
            "public_data_sources": "not_available_without_deep_research_input",
            "reproducibility_notes": "Requires measurement table and uncertainty contract after deep research input.",
            "systematic_risks": "not_available_without_deep_research_input",
            "overclaim_risks": "High if residuals are interpreted as fundamental variation.",
            "first_minimal_test": "Prepare constraint-only observable contract with explicit uncertainty fields.",
            "recommended_run_id": "QSB-OBS-SPECTROSCOPY-CONSTRAINT-CONTRACT-01",
            "priority": "medium_seed_constraint_field",
        },
        {
            "candidate_id": "G_cmb_anomalies_large_scale_correlations",
            "candidate_name": "CMB anomalies / large-scale correlations",
            "domain": "cosmological_large_scale_correlations",
            "short_description": "Candidate field for later observable contracts around already-reported large-scale correlation features and analysis choices.",
            "primary_observables": "not_available_without_deep_research_input",
            "established_explanation": "not_available_without_deep_research_input",
            "open_questions_or_residuals": "not_available_without_deep_research_input",
            "qsb_relevance_hypothesis": "Prepared as a late-stage correlation search space; no cosmological claim.",
            "why_not_qsb": "Look-elsewhere effects, foregrounds, masks, analysis choices, and standard cosmology must be separated first.",
            "public_data_sources": "not_available_without_deep_research_input",
            "reproducibility_notes": "Requires careful preregistered statistic selection after deep research input.",
            "systematic_risks": "not_available_without_deep_research_input",
            "overclaim_risks": "Extremely high if anomaly language is overinterpreted.",
            "first_minimal_test": "Gap report only until source/statistic contract is frozen.",
            "recommended_run_id": "QSB-OBS-CMB-ANOMALY-GAP-REVIEW-01",
            "priority": "low_late_seed",
        },
        {
            "candidate_id": "H_desi_bao_hubble_tension",
            "candidate_name": "DESI / BAO / Hubble-tension constraint field",
            "domain": "cosmological_distance_ladder_and_bao_constraints",
            "short_description": "Candidate field for later observable contracts around cosmological constraint residuals and model-dependence.",
            "primary_observables": "not_available_without_deep_research_input",
            "established_explanation": "not_available_without_deep_research_input",
            "open_questions_or_residuals": "not_available_without_deep_research_input",
            "qsb_relevance_hypothesis": "Prepared as a late-stage constraint search space; no Hubble-tension or new-physics claim.",
            "why_not_qsb": "Dataset covariance, calibration, model-dependence, selection, and standard cosmology must be separated first.",
            "public_data_sources": "not_available_without_deep_research_input",
            "reproducibility_notes": "Requires source-specific data and covariance contract after deep research input.",
            "systematic_risks": "not_available_without_deep_research_input",
            "overclaim_risks": "Extremely high if framed as resolving cosmological tension.",
            "first_minimal_test": "Gap report only until public-data/covariance contract is frozen.",
            "recommended_run_id": "QSB-OBS-DESI-BAO-CONSTRAINT-GAP-REVIEW-01",
            "priority": "low_late_seed",
        },
    ]


def normalize_heading(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", text.lower()).strip("_")


def apply_simple_ingest(candidates: list[dict[str, object]], input_text: str, input_json: dict) -> tuple[list[dict[str, object]], list[dict[str, object]]]:
    citations: list[dict[str, object]] = []
    if not input_text:
        return candidates, citations
    lower_text = input_text.lower()
    for row in candidates:
        key = row["candidate_id"].split("_", 1)[1].replace("_", " ")
        if key in lower_text or row["candidate_name"].split("/")[0].lower() in lower_text:
            row["deep_research_presence"] = "mentioned_in_input"
        else:
            row["deep_research_presence"] = "not_detected_by_simple_ingest"
    for line_number, line in enumerate(input_text.splitlines(), start=1):
        stripped = line.strip()
        if not stripped:
            continue
        if any(marker in stripped.lower() for marker in ["http://", "https://", "doi:", "arxiv", "source", "citation"]):
            citations.append(
                {
                    "source_item_id": f"SRC-{len(citations)+1:03d}",
                    "input_path": "deep_research_input",
                    "line_number": line_number,
                    "excerpt": stripped[:500],
                    "candidate_id": "not_assigned_by_simple_ingest",
                    "claim_boundary": "source inventory only; not independently verified",
                }
            )
    if input_json and isinstance(input_json.get("candidates"), list):
        by_id = {row["candidate_id"]: row for row in candidates}
        for item in input_json["candidates"]:
            if isinstance(item, dict) and item.get("candidate_id") in by_id:
                target = by_id[item["candidate_id"]]
                for field in FIELD_COLUMNS:
                    if field in item and item[field] not in (None, ""):
                        target[field] = item[field]
    return candidates, citations


def scoring_rows(candidates: list[dict[str, object]], has_input: bool) -> list[dict[str, object]]:
    rows = []
    for row in candidates:
        score_row = {"candidate_id": row["candidate_id"]}
        for column in SCORE_COLUMNS[1:8]:
            score_row[column] = None if not has_input else "not_available_in_input"
        score_row["score_total"] = None
        score_row["rank"] = None
        score_row["score_source"] = "pending_deep_research_input" if not has_input else "not_available_in_input"
        score_row["notes"] = "Scores intentionally left null; no deep research input available." if not has_input else "Simple ingest did not find structured scores."
        rows.append(score_row)
    return rows


def ranking_rows(candidates: list[dict[str, object]], has_input: bool) -> list[dict[str, object]]:
    return [
        {
            "rank": None,
            "candidate_id": row["candidate_id"],
            "candidate_name": row["candidate_name"],
            "priority_seed": row["priority"],
            "score_total": None,
            "ranking_status": "not_ranked_without_deep_research_input" if not has_input else "not_ranked_no_structured_scores_in_input",
            "notes": "Priority seed is a project-start hint, not an evidence-based result.",
        }
        for row in candidates
    ]


def observable_contract_rows(candidates: list[dict[str, object]]) -> list[dict[str, object]]:
    return [
        {
            "candidate_id": row["candidate_id"],
            "candidate_name": row["candidate_name"],
            "observable_contract_status": "contract_skeleton_pending_deep_research_input",
            "observable_table": "to_be_defined",
            "required_inputs": "deep_research_report; public_data_inventory; baseline_model_contract",
            "minimal_question": row["first_minimal_test"],
            "expected_outputs": "field_list_csv; source_inventory_csv; null_model_plan_md; claim_boundary_md",
            "claim_boundary": ";".join(CLAIM_BOUNDARY),
        }
        for row in candidates
    ]


def public_data_rows(candidates: list[dict[str, object]], has_input: bool) -> list[dict[str, object]]:
    return [
        {
            "candidate_id": row["candidate_id"],
            "candidate_name": row["candidate_name"],
            "public_data_source": row["public_data_sources"],
            "source_url_or_reference": "not_available_without_deep_research_input" if not has_input else "not_available_in_input",
            "access_status": "pending_deep_research_input" if not has_input else "requires_manual_review",
            "reproducibility_status": "pending_source_contract",
            "notes": "No external lookup performed by this run.",
        }
        for row in candidates
    ]


def main() -> None:
    RUN_DIR.mkdir(parents=True, exist_ok=True)
    write_text(RUN_DIR / "00_git_status_short_before.txt", run_command(["git", "status", "--short"]))
    write_text(RUN_DIR / "01_git_log_oneline_before.txt", run_command(["git", "--no-pager", "log", "--oneline", "-14"]))

    input_path = find_deep_research_input()
    input_text, input_json = read_deep_research(input_path)
    has_input = input_path is not None
    candidates, citations = apply_simple_ingest(base_candidates(), input_text, input_json)

    status = (
        "observational_candidate_scout_completed_with_deep_research_input"
        if has_input and input_text
        else "observational_candidate_scout_completed_pending_deep_research_input"
    )
    top_ranked = "not_ranked_without_deep_research_input" if not has_input else "not_ranked_no_structured_scores_in_input"
    first_recommendation = "pending_deep_research_input"
    recommended_next = "QSB-OBSERVATIONAL-CANDIDATE-SCOUT-01-DEEP-RESEARCH-INGEST"

    scope = f"""# {RUN_ID}

## Purpose

This is a methodological observational candidate scout for preparing later observable contracts. It catalogs candidate search fields and keeps sources, claims, scoring, and testability separated.

## Deep Research Input

Input found: `{str(input_path) if input_path else "none"}`.

## Working Mode

No internet lookup was performed. Where no Deep Research input exists, candidates are scaffolded with null scores and pending source fields.

## Claim Boundary

{chr(10).join(f"- {item}" for item in CLAIM_BOUNDARY)}
"""
    write_text(RUN_DIR / "02_observational_candidate_scout_scope.md", scope)

    write_csv(RUN_DIR / "05_candidate_field_registry.csv", FIELD_COLUMNS, candidates)
    write_csv(RUN_DIR / "06_candidate_scoring_matrix.csv", SCORE_COLUMNS, scoring_rows(candidates, has_input))
    write_csv(RUN_DIR / "07_candidate_ranking.csv", ["rank", "candidate_id", "candidate_name", "priority_seed", "score_total", "ranking_status", "notes"], ranking_rows(candidates, has_input))
    write_csv(RUN_DIR / "08_observable_contract_candidates.csv", ["candidate_id", "candidate_name", "observable_contract_status", "observable_table", "required_inputs", "minimal_question", "expected_outputs", "claim_boundary"], observable_contract_rows(candidates))
    write_csv(RUN_DIR / "09_public_data_source_inventory.csv", ["candidate_id", "candidate_name", "public_data_source", "source_url_or_reference", "access_status", "reproducibility_status", "notes"], public_data_rows(candidates, has_input))

    no_go = f"""# Claim Boundary and No-Go Statements

Allowed statement classes:

{chr(10).join(f"- `{item}`" for item in CLAIM_BOUNDARY)}

Forbidden statements:

- QSB explains dark matter.
- QSB explains Hubble tension.
- QSB proves new physics.
- QSB refutes many-worlds.
- QSB proves spacetime emergence.
- QSB replaces standard physics.
- A QSB signal was found.

This run is a scout and ingest scaffold only.
"""
    write_text(RUN_DIR / "10_claim_boundary_and_no_go.md", no_go)

    if has_input:
        minimal = f"""# First Minimal Test Recommendation

Deep Research input was detected at `{input_path}`, but this scaffold only performs simple deterministic ingest. A follow-up pass should extract structured scores, sources, datasets, and minimal-test fields from the report before selecting a first run.

Claim Boundary:

{'; '.join(CLAIM_BOUNDARY)}
"""
    else:
        minimal = """# First Minimal Test Recommendation

Status: provisional only, pending Deep Research input.

Wait for Deep Research report, then rerun or extend candidate scout.

Provisional best first practical areas:

1. matterwave/interferometry
2. SPARC/Radial Acceleration Relation
3. FRB path-residual scout

These are project-start seeds, not evidence-based rankings.

Claim Boundary:

methodological scout only; no physics, spacetime, gravity, causality, or QSB-detection claim.
"""
    write_text(RUN_DIR / "11_first_minimal_test_recommendation.md", minimal)

    ingest = {
        "run_id": RUN_ID,
        "deep_research_input_found": has_input,
        "deep_research_input_path": str(input_path) if input_path else None,
        "input_candidates_checked": [str(path) for path in INPUT_CANDIDATES],
        "ingest_mode": "simple_deterministic_scaffold" if not has_input else "simple_deterministic_input_scan",
        "structured_json_detected": bool(input_json),
        "citation_like_items_detected": len(citations),
        "status": "pending_deep_research_input" if not has_input else "input_detected_requires_manual_structured_review",
        "claim_boundary": CLAIM_BOUNDARY,
    }
    write_text(RUN_DIR / "12_deep_research_ingest_status.json", json.dumps(ingest, indent=2, ensure_ascii=False) + "\n")

    review = f"""# {RUN_ID}

## Purpose

This run is a search-space and observable-contract scout for QSB-related observational candidates.

## QSB Status

No QSB claim is made. The run does not claim physics, spacetime, gravity, causality, source-signal support, or detection.

## Deep Research Input

Deep Research input found: `{has_input}`.

Path: `{str(input_path) if input_path else "none"}`.

Because no Deep Research input is available, the run creates a clean candidate scaffold with null scores and pending source fields.

## Candidate Fields Prepared

{chr(10).join(f"- `{row['candidate_id']}`: {row['candidate_name']}" for row in candidates)}

## Gaps

Public data sources, established explanations, open residuals, score values, and reproducibility notes remain pending until a Deep Research report or curated source file is added.

## Minimal Tests

The provisional practical starting areas are matterwave/interferometry, SPARC/Radial Acceleration Relation, and FRB path-residual scouting. These are not ranked results.

## Motivation Note

The Knöpfchen-Spaziergang motivation is treated as Ralf Kemmann's origin idea for asking how relational coupling could be made observable. It is not treated as evidence.

## Tooling Note

DWH, CSV, and scoring tables are tools for auditability and later contract formation. They are not the project goal.

## Claim Boundary

{chr(10).join(f"- {item}" for item in CLAIM_BOUNDARY)}
"""
    write_text(RUN_DIR / "13_observational_candidate_scout_review_note.md", review)

    citation_rows = citations or [
        {
            "source_item_id": "SRC-000",
            "input_path": "none",
            "line_number": "",
            "excerpt": "No Deep Research input available; no citations ingested.",
            "candidate_id": "not_applicable",
            "claim_boundary": "source inventory only; no external lookup performed",
        }
    ]
    write_csv(RUN_DIR / "14_source_quote_or_citation_inventory.csv", ["source_item_id", "input_path", "line_number", "excerpt", "candidate_id", "claim_boundary"], citation_rows)

    details = "# Candidate Field Detail Notes\n\n"
    for row in candidates:
        details += f"## {row['candidate_id']}\n\n"
        details += f"- Candidate name: {row['candidate_name']}\n"
        details += f"- Priority seed: {row['priority']}\n"
        details += f"- First minimal test scaffold: {row['first_minimal_test']}\n"
        details += "- Status: pending Deep Research input.\n\n"
    write_text(RUN_DIR / "15_candidate_field_detail_notes.md", details)

    next_run = f"""# Next Codex Run Recommendation

Recommended next run:

`{recommended_next}`

Purpose:

Ingest a curated Deep Research report, populate source-backed observables, established explanations, residuals, public data sources, scores, and a source-based first minimal test recommendation.

Claim Boundary:

{'; '.join(CLAIM_BOUNDARY)}
"""
    write_text(RUN_DIR / "16_next_codex_run_recommendation.md", next_run)

    gap_report = """# External Research Gap Report

No Deep Research input file was found in the configured locations. This run did not use the internet and did not fabricate literature details.

Required before evidence-based ranking:

- source-backed public dataset inventory
- established explanation summary per candidate
- open residuals and constraint fields per candidate
- reproducibility notes
- systematic and overclaim risk assessment
- score assignments with source rationale
"""
    write_text(RUN_DIR / "17_external_research_gap_report.md", gap_report)

    summary = {
        "run_id": RUN_ID,
        "status": status,
        "deep_research_input_found": has_input,
        "deep_research_input_path": str(input_path) if input_path else None,
        "candidate_field_count": len(candidates),
        "ranked_candidate_count": len(candidates),
        "top_ranked_candidate": top_ranked,
        "first_practical_run_recommendation": first_recommendation,
        "claim_boundary": CLAIM_BOUNDARY,
        "recommended_next_run_id": recommended_next,
        "notes": "No Deep Research input found; generated scaffold with null scores and pending source fields." if not has_input else "Deep Research input detected; simple deterministic ingest performed without external lookup.",
    }
    write_text(RUN_DIR / "04_observational_candidate_scout_summary.json", json.dumps(summary, indent=2, ensure_ascii=False) + "\n")

    print(json.dumps(summary, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
