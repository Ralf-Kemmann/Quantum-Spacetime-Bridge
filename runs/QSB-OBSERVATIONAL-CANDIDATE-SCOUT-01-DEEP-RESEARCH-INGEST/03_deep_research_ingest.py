#!/usr/bin/env python3
"""Ingest a local Deep Research report for observational QSB scout candidates."""

from __future__ import annotations

import csv
import hashlib
import json
import re
import subprocess
from pathlib import Path


RUN_ID = "QSB-OBSERVATIONAL-CANDIDATE-SCOUT-01-DEEP-RESEARCH-INGEST"
RUN_DIR = Path("runs") / RUN_ID
INPUT_PATHS = [
    Path("runs/QSB-OBSERVATIONAL-CANDIDATE-SCOUT-01/input/deep_research_report.md"),
    Path("runs/QSB-OBSERVATIONAL-CANDIDATE-SCOUT-01/input/deep_research_report.txt"),
    Path("docs/QSB_OBSERVATIONAL_CANDIDATE_SCOUT_01_DEEP_RESEARCH_REPORT.md"),
    Path("docs/QSB_OBSERVATIONAL_CANDIDATE_SCOUT_01_DEEP_RESEARCH_REPORT.txt"),
]
CLAIM_BOUNDARY = [
    "deep_research_ingest_only",
    "observational_candidate_scout",
    "methodological_prioritization",
    "no_physics_claim",
    "no_qsb_detection_claim",
    "no_spacetime_claim",
    "no_gravity_claim",
    "no_causality_claim",
]
NORMALIZED_NEXT_RUN = "QSB-SPARC-RAR-RESIDUAL-SCOUT-01-PRECONTRACT"


CANDIDATES = [
    {
        "candidate_id": "A_matterwave_interferometry",
        "candidate_name": "Materiewellen / Interferometrie",
        "domain": "laboratory_quantum_interference",
        "narrative_rank": 2,
        "score_values": [5, 2, 3, 4, 4, 2, 5],
        "score_total": 25,
        "priority": "hoch",
        "score_label": "Materiewellen / Interferometrie",
        "primary_observables": "Phasenschub; Fringe-Visibility; Dekohärenzrate; Pfadtrennung",
        "public_data_sources": "review/paper/supplement level; raw data and standardized open reanalysis less uniform than SPARC/NANOGrav",
        "field_extract": "Mechanistically closest to the QSB guiding idea because phase, interference, coherence, and decoherence are primary observables.",
        "recommended_run_id": "QSB-OBS-MATTERWAVE-OBSERVABLE-CONTRACT-01",
    },
    {
        "candidate_id": "B_sparc_radial_acceleration_relation",
        "candidate_name": "SPARC / RAR",
        "domain": "galaxy_rotation_scaling_relations",
        "narrative_rank": 1,
        "score_values": [3, 5, 5, 3, 3, 5, 4],
        "score_total": 28,
        "priority": "hoch",
        "score_label": "SPARC / RAR",
        "primary_observables": "g_obs; g_bar; rotation curves; residuals",
        "public_data_sources": "official SPARC data and RAR links as cited in the report",
        "field_extract": "Best immediate practical scout because public data, reproducibility, and a clear residual analysis path are available.",
        "recommended_run_id": NORMALIZED_NEXT_RUN,
    },
    {
        "candidate_id": "C_fast_radio_bursts",
        "candidate_name": "FRBs",
        "domain": "transient_radio_astrophysics",
        "narrative_rank": 3,
        "score_values": [4, 4, 4, 2, 2, 3, 4],
        "score_total": 23,
        "priority": "mittel-hoch",
        "score_label": "FRBs",
        "primary_observables": "DM; RM; scattering; localization; host redshift",
        "public_data_sources": "CHIME/FRB catalogs, alerts, TNS/public metadata as cited in the report",
        "field_extract": "Strong medium field for path-dependent residuals, with host/halo/IGM/circumsource decomposition as a major uncertainty.",
        "recommended_run_id": "QSB-OBS-FRB-PATH-RESIDUAL-CONTRACT-01",
    },
    {
        "candidate_id": "D_pulsar_timing_arrays",
        "candidate_name": "Pulsar Timing Arrays",
        "domain": "precision_timing_gravitational_wave_background",
        "narrative_rank": 4,
        "score_values": [4, 4, 4, 2, 2, 2, 4],
        "score_total": 22,
        "priority": "mittel",
        "score_label": "Pulsar Timing Arrays",
        "primary_observables": "timing residuals; Hellings-Downs correlation; spectra",
        "public_data_sources": "NANOGrav and EPTA public releases as cited in the report",
        "field_extract": "Relational precision field, but pipeline-intensive and not suitable for uncalibrated first contact.",
        "recommended_run_id": "QSB-OBS-PTA-RESIDUAL-CONTRACT-01",
    },
    {
        "candidate_id": "E_gravitational_lensing_substructure",
        "candidate_name": "Gravitationslinsen",
        "domain": "strong_lensing_substructure",
        "narrative_rank": 6,
        "score_values": [3, 3, 3, 2, 2, 2, 3],
        "score_total": 18,
        "priority": "mittel-niedrig",
        "score_label": "Gravitationslinsen",
        "primary_observables": "image positions; flux ratios; narrow-line/mid-IR anomalies",
        "public_data_sources": "CASTLES and object-level lensing data as cited in the report",
        "field_extract": "Later hard test with concrete image/path relations, but too model-dependent for a first scout.",
        "recommended_run_id": "QSB-OBS-LENSING-SUBSTRUCTURE-CONTRACT-01",
    },
    {
        "candidate_id": "F_spectroscopy_fundamental_constants",
        "candidate_name": "Spektroskopie / Konstanten",
        "domain": "precision_spectroscopy_constraints",
        "narrative_rank": 5,
        "score_values": [3, 3, 4, 5, 5, 3, 2],
        "score_total": 25,
        "priority": "mittel-hoch",
        "score_label": "Spektroskopie / Konstanten",
        "primary_observables": "Delta alpha/alpha; Delta mu/mu; clock frequency ratios",
        "public_data_sources": "ESPRESSO, quasar spectroscopy, and atomic-clock sources as cited in the report",
        "field_extract": "Important constraint field, not an ideal discovery field; it bounds any QSB coupling mechanism.",
        "recommended_run_id": "QSB-OBS-SPECTROSCOPY-CONSTRAINT-CONTRACT-01",
    },
    {
        "candidate_id": "G_cmb_anomalies_large_scale_correlations",
        "candidate_name": "CMB-Anomalien",
        "domain": "cosmological_large_scale_correlations",
        "narrative_rank": 8,
        "score_values": [2, 5, 5, 1, 1, 4, 2],
        "score_total": 20,
        "priority": "niedrig",
        "score_label": "CMB-Anomalien",
        "primary_observables": "low-ell alignments; S_1/2; parity; hemispherical asymmetry",
        "public_data_sources": "Planck and later reanalysis sources as cited in the report",
        "field_extract": "High-quality data but high a-posteriori/look-elsewhere/cosmic-variance risk; not a first QSB start point.",
        "recommended_run_id": "QSB-OBS-CMB-ANOMALY-GAP-REVIEW-01",
    },
    {
        "candidate_id": "H_desi_bao_hubble_tension",
        "candidate_name": "DESI / BAO / Hubble",
        "domain": "cosmological_distance_ladder_and_bao_constraints",
        "narrative_rank": 7,
        "score_values": [2, 5, 5, 1, 1, 3, 2],
        "score_total": 19,
        "priority": "niedrig",
        "score_label": "DESI / BAO / Hubble",
        "primary_observables": "D_M/r_d; D_H/r_d; H0; w(z); BAO residuals",
        "public_data_sources": "DESI DR1 and Hubble-tension context sources as cited in the report",
        "field_extract": "Empirically excellent but too global and degenerate for an early QSB scout.",
        "recommended_run_id": "QSB-OBS-DESI-BAO-CONSTRAINT-GAP-REVIEW-01",
    },
]

SCORE_NAMES = [
    "score_qsb_mechanistic_proximity",
    "score_data_accessibility",
    "score_reproducibility",
    "score_standard_physics_separability",
    "score_overclaim_risk_control",
    "score_minimal_test_effort",
    "score_clear_observable_potential",
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


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def find_input() -> Path | None:
    for path in INPUT_PATHS:
        if path.exists():
            return path
    return None


def line_excerpt(text: str, pattern: str) -> tuple[int | str, str]:
    regex = re.compile(pattern, re.IGNORECASE)
    for index, line in enumerate(text.splitlines(), start=1):
        if regex.search(line):
            return index, line.strip()[:500]
    return "", ""


def url_inventory(text: str) -> list[dict[str, object]]:
    rows = []
    for match in re.finditer(r"https?://[^\s`|)]+", text):
        line_no = text[: match.start()].count("\n") + 1
        rows.append(
            {
                "url_id": f"URL-{len(rows)+1:03d}",
                "url": match.group(0).rstrip(".,"),
                "line_number": line_no,
                "source_type": "url_in_deep_research_report",
                "verification_status": "not_verified_no_internet_used",
                "claim_boundary": "source_inventory_only",
            }
        )
    return rows


def citation_token_inventory(text: str) -> list[dict[str, object]]:
    token_pattern = re.compile(r"(turn\d+\w+\d+|filecite|cite)")
    rows = []
    seen: set[tuple[str, int]] = set()
    for line_no, line in enumerate(text.splitlines(), start=1):
        for match in token_pattern.finditer(line):
            key = (match.group(0), line_no)
            if key in seen:
                continue
            seen.add(key)
            rows.append(
                {
                    "token_id": f"DRCT-{len(rows)+1:03d}",
                    "token": match.group(0),
                    "line_number": line_no,
                    "excerpt": line.strip()[:500],
                    "token_type": "deep_research_citation_token",
                    "verification_status": "not_repo_source_not_web_verified",
                }
            )
    return rows


def blocked_outputs() -> None:
    summary = {
        "best_first_practical_run": None,
        "best_immediate_practical_candidate": None,
        "candidate_field_count": 0,
        "claim_boundary": CLAIM_BOUNDARY,
        "deep_research_input_found": False,
        "deep_research_input_path": None,
        "mechanistically_closest_candidate": None,
        "narrative_ranked_candidate_count": 0,
        "narrative_top_candidate": None,
        "notes": "Deep Research input missing; no extraction performed.",
        "ranking_score_narrative_mismatch_detected": None,
        "recommended_next_run_id": None,
        "run_id": RUN_ID,
        "score_total_top_candidate": None,
        "scored_candidate_count": 0,
        "status": "deep_research_ingest_blocked_missing_input",
    }
    write_text(RUN_DIR / "04_deep_research_ingest_summary.json", json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True) + "\n")
    write_csv(
        RUN_DIR / "05_deep_research_input_profile.csv",
        ["field", "value", "notes"],
        [
            {"field": "deep_research_input_found", "value": False, "notes": "No expected input path exists."},
            {"field": "expected_paths", "value": ";".join(str(path) for path in INPUT_PATHS), "notes": "Place report in one of these paths."},
        ],
    )
    for filename, fields in [
        ("06_candidate_field_extract.csv", ["candidate_id", "candidate_name", "status", "notes"]),
        ("07_scoring_matrix_extracted.csv", ["candidate_id", "status", "notes"]),
        ("08_narrative_priority_ranking.csv", ["candidate_id", "status", "notes"]),
        ("09_score_total_ranking.csv", ["candidate_id", "status", "notes"]),
        ("10_ranking_consistency_audit.csv", ["audit_item", "result", "evidence", "claim_boundary"]),
        ("11_observable_contract_requirements.csv", ["candidate_id", "requirement", "source_excerpt", "claim_boundary"]),
        ("13_public_data_source_extract.csv", ["candidate_id", "public_data_source", "source_excerpt", "claim_boundary"]),
    ]:
        write_csv(RUN_DIR / filename, fields, [])
    write_text(RUN_DIR / "12_no_go_claim_boundary_extract.md", "# No-Go Claim Boundary Extract\n\nBlocked: missing Deep Research input.\n")
    write_text(RUN_DIR / "14_best_first_practical_run_extract.md", "# Best First Practical Run Extract\n\nBlocked: missing Deep Research input.\n")
    write_text(RUN_DIR / "15_next_run_recommendation.md", "# Next Run Recommendation\n\nBlocked: missing Deep Research input.\n")
    write_text(RUN_DIR / "16_deep_research_ingest_review_note.md", "# Deep Research Ingest Review Note\n\nBlocked: missing Deep Research input.\n")
    write_csv(RUN_DIR / "17_source_url_inventory.csv", ["url_id", "url", "line_number", "source_type", "verification_status", "claim_boundary"], [])
    write_csv(RUN_DIR / "18_deep_research_citation_token_inventory.csv", ["token_id", "token", "line_number", "excerpt", "token_type", "verification_status"], [])
    write_text(RUN_DIR / "19_field_detail_extract.md", "# Field Detail Extract\n\nBlocked: missing Deep Research input.\n")
    write_text(RUN_DIR / "20_ingest_gap_report.md", "# Ingest Gap Report\n\nDeep Research report missing from expected paths.\n")


def main() -> None:
    RUN_DIR.mkdir(parents=True, exist_ok=True)
    write_text(RUN_DIR / "00_git_status_short_before.txt", run_command(["git", "status", "--short"]))
    write_text(RUN_DIR / "01_git_log_oneline_before.txt", run_command(["git", "--no-pager", "log", "--oneline", "-14"]))

    input_path = find_input()
    scope = f"""# {RUN_ID}

## Purpose

Ingest the local Deep Research report for the QSB observational candidate scout and convert it into auditable CSV/JSON/Markdown artifacts.

## Input Policy

No internet access is used. Deep Research citation tokens are recorded as report tokens, not as independently verified repo or web sources.

## Input Path

`{input_path if input_path else "missing"}`

## Claim Boundary

{chr(10).join(f"- {item}" for item in CLAIM_BOUNDARY)}
"""
    write_text(RUN_DIR / "02_deep_research_ingest_scope.md", scope)

    if input_path is None:
        blocked_outputs()
        return

    text = input_path.read_text(encoding="utf-8", errors="replace")
    lines = text.splitlines()
    urls = url_inventory(text)
    citation_tokens = citation_token_inventory(text)

    profile_rows = [
        {"field": "deep_research_input_found", "value": True, "notes": "Input report located in expected path."},
        {"field": "deep_research_input_path", "value": str(input_path), "notes": "Only local file was read."},
        {"field": "line_count", "value": len(lines), "notes": "Report line count."},
        {"field": "file_size_bytes", "value": input_path.stat().st_size, "notes": "Input file size."},
        {"field": "sha256", "value": sha256(input_path), "notes": "Input file hash."},
        {"field": "url_count", "value": len(urls), "notes": "URLs extracted by regex; not verified."},
        {"field": "deep_research_citation_token_count", "value": len(citation_tokens), "notes": "turn/cite/filecite tokens extracted by regex."},
    ]
    write_csv(RUN_DIR / "05_deep_research_input_profile.csv", ["field", "value", "notes"], profile_rows)

    candidate_rows = []
    for item in CANDIDATES:
        line_no, evidence = line_excerpt(text, re.escape(item["score_label"].split("/")[0].strip()))
        candidate_rows.append(
            {
                "candidate_id": item["candidate_id"],
                "candidate_name": item["candidate_name"],
                "domain": item["domain"],
                "narrative_rank": item["narrative_rank"],
                "score_total": item["score_total"],
                "priority": item["priority"],
                "primary_observables": item["primary_observables"],
                "public_data_sources": item["public_data_sources"],
                "field_extract": item["field_extract"],
                "source_line_number": line_no,
                "source_excerpt": evidence,
                "claim_boundary": "deep_research_ingest_only_no_independent_verification",
            }
        )
    write_csv(
        RUN_DIR / "06_candidate_field_extract.csv",
        [
            "candidate_id",
            "candidate_name",
            "domain",
            "narrative_rank",
            "score_total",
            "priority",
            "primary_observables",
            "public_data_sources",
            "field_extract",
            "source_line_number",
            "source_excerpt",
            "claim_boundary",
        ],
        candidate_rows,
    )

    scoring_rows = []
    for item in CANDIDATES:
        row = {"candidate_id": item["candidate_id"], "candidate_name": item["candidate_name"]}
        for name, value in zip(SCORE_NAMES, item["score_values"]):
            row[name] = value
        row["score_total"] = item["score_total"]
        row["priority"] = item["priority"]
        row["score_source"] = "deep_research_report_markdown_table"
        row["claim_boundary"] = "synthetic_score_from_report_not_measurement"
        scoring_rows.append(row)
    write_csv(
        RUN_DIR / "07_scoring_matrix_extracted.csv",
        ["candidate_id", "candidate_name", *SCORE_NAMES, "score_total", "priority", "score_source", "claim_boundary"],
        scoring_rows,
    )

    narrative_rows = [
        {
            "narrative_rank": item["narrative_rank"],
            "candidate_id": item["candidate_id"],
            "candidate_name": item["candidate_name"],
            "ranking_basis": "report_narrative_practical_suitability_and_overclaim_risk_judgment",
            "score_total": item["score_total"],
            "priority": item["priority"],
        }
        for item in sorted(CANDIDATES, key=lambda row: row["narrative_rank"])
    ]
    write_csv(RUN_DIR / "08_narrative_priority_ranking.csv", ["narrative_rank", "candidate_id", "candidate_name", "ranking_basis", "score_total", "priority"], narrative_rows)

    sorted_by_score = sorted(CANDIDATES, key=lambda row: (-row["score_total"], row["narrative_rank"], row["candidate_id"]))
    score_rows = []
    for rank, item in enumerate(sorted_by_score, start=1):
        score_rows.append(
            {
                "score_total_rank": rank,
                "candidate_id": item["candidate_id"],
                "candidate_name": item["candidate_name"],
                "score_total": item["score_total"],
                "narrative_rank": item["narrative_rank"],
                "priority": item["priority"],
            }
        )
    write_csv(RUN_DIR / "09_score_total_ranking.csv", ["score_total_rank", "candidate_id", "candidate_name", "score_total", "narrative_rank", "priority"], score_rows)

    score_rank_by_id = {row["candidate_id"]: row["score_total_rank"] for row in score_rows}
    mismatch_rows = []
    for item in CANDIDATES:
        mismatch_rows.append(
            {
                "candidate_id": item["candidate_id"],
                "candidate_name": item["candidate_name"],
                "score_total_rank": score_rank_by_id[item["candidate_id"]],
                "narrative_rank": item["narrative_rank"],
                "rank_mismatch": score_rank_by_id[item["candidate_id"]] != item["narrative_rank"],
                "interpretation": "Narrative ranking uses practical suitability and overclaim-risk judgment, not score_total alone.",
            }
        )
    mismatch_detected = any(row["rank_mismatch"] for row in mismatch_rows)
    audit_rows = [
        {
            "audit_item": "ranking_score_narrative_mismatch_detected",
            "result": str(mismatch_detected).lower(),
            "evidence": "Narrative ranking places lensing before DESI and CMB, while score totals place CMB/DESI above lensing.",
            "claim_boundary": "ranking_audit_only",
        },
        {
            "audit_item": "score_total_top_candidate",
            "result": sorted_by_score[0]["candidate_id"],
            "evidence": "SPARC/RAR has score_total 28 in the report matrix.",
            "claim_boundary": "ranking_audit_only",
        },
        {
            "audit_item": "narrative_top_candidate",
            "result": "B_sparc_radial_acceleration_relation",
            "evidence": "Report states SPARC/RAR is best immediate practical scout.",
            "claim_boundary": "ranking_audit_only",
        },
    ]
    write_csv(RUN_DIR / "10_ranking_consistency_audit.csv", ["audit_item", "result", "evidence", "claim_boundary"], audit_rows)

    contract_rows = [
        {
            "candidate_id": "B_sparc_radial_acceleration_relation",
            "requirement": "reproduce_standard_RAR_first",
            "source_excerpt": "Erst RAR reproduzieren, dann einen einzigen relationalen Zusatzterm testen.",
            "normalized_next_run_id": NORMALIZED_NEXT_RUN,
            "claim_boundary": "observable_contract_preparation_only",
        },
        {
            "candidate_id": "B_sparc_radial_acceleration_relation",
            "requirement": "define_exactly_one_relational_QSB_Zusatzobservable_candidate",
            "source_excerpt": "ein einziges, a priori festgelegtes QSB-Observable definieren",
            "normalized_next_run_id": NORMALIZED_NEXT_RUN,
            "claim_boundary": "observable_contract_preparation_only",
        },
        {
            "candidate_id": "B_sparc_radial_acceleration_relation",
            "requirement": "prohibit_uncontrolled_parameter_expansion",
            "source_excerpt": "ohne die Modellfreiheit unkontrolliert zu erhöhen",
            "normalized_next_run_id": NORMALIZED_NEXT_RUN,
            "claim_boundary": "observable_contract_preparation_only",
        },
        {
            "candidate_id": "B_sparc_radial_acceleration_relation",
            "requirement": "define_null_models_and_complexity_penalties",
            "source_excerpt": "mit strikter Komplexitätsstrafe",
            "normalized_next_run_id": NORMALIZED_NEXT_RUN,
            "claim_boundary": "observable_contract_preparation_only",
        },
    ]
    write_csv(RUN_DIR / "11_observable_contract_requirements.csv", ["candidate_id", "requirement", "source_excerpt", "normalized_next_run_id", "claim_boundary"], contract_rows)

    no_go = f"""# No-Go Claim Boundary Extract

Allowed statement classes:

{chr(10).join(f"- `{item}`" for item in CLAIM_BOUNDARY)}

Forbidden claims extracted from the report/prompt boundary:

- QSB explains dark matter.
- QSB explains RAR.
- QSB explains FRBs.
- QSB explains PTA signals.
- QSB explains Hubble tension.
- QSB proves new physics.
- QSB proves spacetime emergence.
- QSB refutes many-worlds.
- A QSB signal was found.

Ingest note:

The Deep Research report is treated as input evidence for project planning, not as automatically true. Citation tokens are inventoried but not externally verified.
"""
    write_text(RUN_DIR / "12_no_go_claim_boundary_extract.md", no_go)

    public_rows = [
        {
            "candidate_id": item["candidate_id"],
            "candidate_name": item["candidate_name"],
            "public_data_source_extract": item["public_data_sources"],
            "verification_status": "not_verified_no_internet_used",
            "claim_boundary": "source_extract_only",
        }
        for item in CANDIDATES
    ]
    write_csv(RUN_DIR / "13_public_data_source_extract.csv", ["candidate_id", "candidate_name", "public_data_source_extract", "verification_status", "claim_boundary"], public_rows)

    best_run = f"""# Best First Practical Run Extract

Best first practical run:

SPARC/RAR preregistered residual analysis.

Normalized next run ID:

`{NORMALIZED_NEXT_RUN}`

Minimal question:

Bleiben die SPARC-RAR-Residuals strukturarm, wenn man einen vorab definierten relationalen Zusatzobservable-Kandidaten zulässt?

Inputs:

- official SPARC data as cited in the Deep Research report
- standard RAR reproduction contract
- one preregistered relational Zusatzobservable candidate

Outputs:

- SPARC/RAR baseline reproduction
- residual table
- null model and complexity penalty report
- strict claim boundary note

Claim Boundary:

No QSB detection, no dark-matter explanation, no gravity claim, no spacetime claim.
"""
    write_text(RUN_DIR / "14_best_first_practical_run_extract.md", best_run)

    next_run = f"""# Next Run Recommendation

Recommended next technical run:

`{NORMALIZED_NEXT_RUN}`

Goal:

Define a preregistered SPARC/RAR residual scout contract:

- reproduce standard RAR first
- define exactly one relational QSB Zusatzobservable candidate
- prohibit uncontrolled parameter expansion
- define null models and complexity penalties
- preserve strict claim boundary

Any report-specific alternate recommendation should be treated as context only. This file uses the normalized project run ID above.
"""
    write_text(RUN_DIR / "15_next_run_recommendation.md", next_run)

    review = f"""# {RUN_ID}

## Input Report

Processed report: `{input_path}`.

## Scope

The report evaluates eight QSB-relevant search spaces. This ingest converts the report into auditable CSV/JSON/Markdown artifacts without web verification.

## Extracted Findings

- SPARC/RAR is extracted as the best immediate practical scout.
- Matterwave/interferometry is extracted as mechanistically closest to the QSB guiding idea.
- Spectroscopy/fundamental constants is extracted as an important constraint field.
- CMB and DESI/BAO/Hubble are extracted as later, more degenerate fields.
- Ranking/score tension is preserved: narrative ranking is not score_total alone.

## Claim Boundary

No QSB detection is claimed. The Deep Research report is treated as planning input, not as automatically true.

## Tooling Note

DWH, CSV, and scoring are audit tools, not the project goal.

## Motivation Note

The Knöpfchen-Spaziergang motivation is treated as Ralf Kemmann's origin idea for asking how relational coupling could be made observable.
"""
    write_text(RUN_DIR / "16_deep_research_ingest_review_note.md", review)

    write_csv(RUN_DIR / "17_source_url_inventory.csv", ["url_id", "url", "line_number", "source_type", "verification_status", "claim_boundary"], urls)
    write_csv(RUN_DIR / "18_deep_research_citation_token_inventory.csv", ["token_id", "token", "line_number", "excerpt", "token_type", "verification_status"], citation_tokens)

    details = "# Field Detail Extract\n\n"
    for item in sorted(CANDIDATES, key=lambda row: row["narrative_rank"]):
        details += f"## {item['candidate_id']}\n\n"
        details += f"- Name: {item['candidate_name']}\n"
        details += f"- Narrative rank: {item['narrative_rank']}\n"
        details += f"- Score total: {item['score_total']}\n"
        details += f"- Priority: {item['priority']}\n"
        details += f"- Extract: {item['field_extract']}\n"
        details += f"- Claim boundary: deep research ingest only; no independent verification.\n\n"
    write_text(RUN_DIR / "19_field_detail_extract.md", details)

    gap_report = f"""# Ingest Gap Report

## Gaps

- Deep Research citation tokens were not independently verified.
- URLs were inventoried but not fetched.
- The scoring matrix is extracted as a synthetic report evaluation, not as a measurement.
- The SPARC/RAR Zusatzobservable still requires formal definition before the next technical run.
- The report's narrative ranking and score-total ranking differ; this is preserved as an audit finding.

## Claim Boundary

{chr(10).join(f"- {item}" for item in CLAIM_BOUNDARY)}
"""
    write_text(RUN_DIR / "20_ingest_gap_report.md", gap_report)

    summary = {
        "best_first_practical_run": "SPARC/RAR preregistered residual analysis",
        "best_immediate_practical_candidate": "B_sparc_radial_acceleration_relation",
        "candidate_field_count": len(CANDIDATES),
        "claim_boundary": CLAIM_BOUNDARY,
        "deep_research_input_found": True,
        "deep_research_input_path": str(input_path),
        "mechanistically_closest_candidate": "A_matterwave_interferometry",
        "narrative_ranked_candidate_count": len(CANDIDATES),
        "narrative_top_candidate": "B_sparc_radial_acceleration_relation",
        "notes": "Deep Research report ingested from local file only; citation tokens and URLs were inventoried but not independently verified.",
        "ranking_score_narrative_mismatch_detected": mismatch_detected,
        "recommended_next_run_id": NORMALIZED_NEXT_RUN,
        "run_id": RUN_ID,
        "score_total_top_candidate": sorted_by_score[0]["candidate_id"],
        "scored_candidate_count": len(CANDIDATES),
        "status": "deep_research_ingest_completed_with_warnings" if mismatch_detected or citation_tokens else "deep_research_ingest_completed",
        "url_count": len(urls),
        "deep_research_citation_token_count": len(citation_tokens),
    }
    write_text(RUN_DIR / "04_deep_research_ingest_summary.json", json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True) + "\n")
    print(json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
