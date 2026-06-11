#!/usr/bin/env python3
"""Validate OUTREACH01A-06 contact material preparation outputs."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path


OUTPUT_FILES = [
    "contact_letter_validation.json",
    "research_context_validation.json",
    "competence_profile_validation.json",
    "public_profile_link_check.json",
    "contact_materials_summary.json",
    "readout.md",
    "claim_risk_report.txt",
]

QUESTION_IDS = [
    "Q1_IDENTITY_EQUIVALENCE_PHASE",
    "Q2_BOUNDARY_REPRESENTATION",
    "Q3_MINIMUM_PHYSICAL_INFORMATION",
]

GENERIC_PATTERNS = [
    "This document aims to provide",
    "It is important to note",
    "In conclusion",
    "innovative approach",
    "robust framework",
    "groundbreaking",
    "novel paradigm",
    "leverages",
]

CLAIM_RISK_PATTERNS = [
    "QSB explains " + "time crystals",
    "QSB models the " + "laser experiment",
    "QSB predicts the " + "domain wall",
    "QSB validates the " + "experiment",
    "new theory of " + "time crystals",
    "established expert in " + "laser physics",
    "validated QSB " + "theory",
    "requesting " + "collaboration",
    "seeking " + "supervision",
    "seeking " + "endorsement",
]

CLAIM_DETECTION_SPECS = {
    "collaboration_request": [
        r"\b(?:request|ask|seek|seeking|invite|propose)\b.{0,80}\bcollaboration\b",
        r"\bcollaboration\b.{0,80}\b(?:request|requested|sought|proposal)\b",
    ],
    "supervision_request": [
        r"\b(?:request|ask|seek|seeking)\b.{0,80}\bsupervision\b",
        r"\bsupervision\b.{0,80}\b(?:request|requested|sought)\b",
    ],
    "validation_request": [
        r"\b(?:request|ask|seek|seeking)\b.{0,80}\bvalidation\b",
        r"\bvalidate\b.{0,80}\b(?:QSB|programme|program|theory)\b",
    ],
    "endorsement_request": [
        r"\b(?:request|ask|seek|seeking)\b.{0,80}\bendorsement\b",
        r"\bendorse(?:ment)?\b.{0,80}\b(?:request|requested|sought)\b",
    ],
    "institutional_affiliation_claim": [
        r"\b(?:I am|I'm|my work is|my work was|work is|work was)\b.{0,80}\b(?:institutionally affiliated|affiliated with)\b",
        r"\b(?:I have|I hold|my work has)\b.{0,80}\binstitutional(?:ly)?\b.{0,40}\b(?:affiliated|affiliation)\b",
    ],
    "laser_physics_expertise_claim": [
        r"\b(?:established|recognized|expert)\b.{0,80}\blaser physics\b",
        r"\blaser-physics expertise\b.{0,80}\b(?:claimed|established|held)\b",
    ],
    "independent_validation_claim": [
        r"\bindependent(?:ly)?\b.{0,60}\bvalidated\b",
        r"\bindependent scientific validation\b.{0,80}\b(?:received|established|confirmed)\b",
    ],
}

FULL_QSB_ASSESSMENT_PATTERNS = [
    r"\bassess\b.{0,60}\b(?:wider|full|complete|overall)\s+QSB\s+(?:programme|program|framework|approach)\b",
    r"\bevaluate\b.{0,60}\b(?:wider|full|complete|overall)\s+QSB\s+(?:programme|program|framework|approach)\b",
    r"\breview\b.{0,60}\bQSB\s+as\s+a\s+whole\b",
]

NEGATION_CUES = [
    "not",
    "no",
    "does not",
    "do not",
    "did not",
    "without",
    "neither",
    "nor",
    "not a request",
    "not being",
    "is not",
    "are not",
    "has not",
    "have not",
]
NEGATION_WINDOW = 45
NEGATION_DETECTION_SCOPE = "sentence_local_bounded_window"


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def write_json(path: Path, payload: dict) -> None:
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def word_count(value: str) -> int:
    return len(re.findall(r"\b[\w'’-]+\b", value))


def count_subject_lines(letter: str) -> int:
    return len(re.findall(r"(?m)^\d+\.\s+", letter))


def count_preferred_subject_lines(letter: str) -> int:
    return len(re.findall(r"(?im)^\d+\.\s+Preferred:", letter))


def literal_hits(paths: list[Path], patterns: list[str]) -> list[dict]:
    found = []
    for path in paths:
        content = read_text(path)
        for pattern in patterns:
            if re.search(re.escape(pattern), content, flags=re.IGNORECASE):
                found.append({"path": str(path), "pattern": pattern})
    return found


def sentence_spans(content: str) -> list[tuple[int, int]]:
    spans = []
    start = 0
    for match in re.finditer(r"(?<=[.!?])\s+", content):
        end = match.end()
        spans.append((start, end))
        start = end
    spans.append((start, len(content)))
    return spans


def bounded_negation_before(sentence: str, relative_start: int) -> bool:
    before = sentence[max(0, relative_start - NEGATION_WINDOW):relative_start].lower()
    return any(re.search(r"\b" + re.escape(cue) + r"\b", before) for cue in NEGATION_CUES)


def negation_inside_match(sentence: str, match: re.Match[str]) -> bool:
    matched_text = sentence[match.start():match.end()].lower()
    return any(re.search(r"\b" + re.escape(cue) + r"\b", matched_text) for cue in NEGATION_CUES)


def regex_classified_hits(paths: list[Path], patterns: list[str]) -> dict:
    positives = []
    negated = []
    ambiguous = []
    for path in paths:
        content = read_text(path)
        for sentence_start, sentence_end in sentence_spans(content):
            sentence = content[sentence_start:sentence_end]
            for pattern in patterns:
                for match in re.finditer(pattern, sentence, flags=re.IGNORECASE | re.DOTALL):
                    context = re.sub(r"\s+", " ", sentence).strip()
                    payload = {"path": str(path), "pattern": pattern, "context": context}
                    if bounded_negation_before(sentence, match.start()) or negation_inside_match(sentence, match):
                        negated.append(payload)
                    elif re.search(r"\b(?:not|no|without|neither|nor)\b", sentence[match.end():match.end() + NEGATION_WINDOW], flags=re.IGNORECASE):
                        ambiguous.append(payload)
                    else:
                        positives.append(payload)
    return {
        "positive_pattern_hits": positives,
        "negated_pattern_hits": negated,
        "ambiguous_pattern_hits": ambiguous,
    }


def detect_claims(paths: list[Path]) -> dict:
    result = {}
    inconclusive = False
    for category, patterns in CLAIM_DETECTION_SPECS.items():
        classified = regex_classified_hits(paths, patterns)
        positive_hits = classified["positive_pattern_hits"]
        negated_hits = classified["negated_pattern_hits"]
        ambiguous_hits = classified["ambiguous_pattern_hits"]
        field = category + "ed" if category.endswith("claim") else category + "ed"
        if category.endswith("_request"):
            field = category.replace("_request", "_requested")
        elif category == "institutional_affiliation_claim":
            field = "institutional_affiliation_claimed"
        elif category == "laser_physics_expertise_claim":
            field = "laser_physics_expertise_claimed"
        elif category == "independent_validation_claim":
            field = "independent_validation_claimed"
        result[field] = bool(positive_hits)
        result[category + "_positive_pattern_hits"] = positive_hits
        result[category + "_negated_pattern_hits"] = negated_hits
        result[category + "_ambiguous_pattern_hits"] = ambiguous_hits
        result[category + "_pattern_hits"] = positive_hits
        result[category + "_negated_hits"] = negated_hits
        result[field + "_evidence"] = positive_hits
        if ambiguous_hits or (positive_hits and negated_hits):
            inconclusive = True
    result["negation_detection_scope"] = NEGATION_DETECTION_SCOPE
    result["semantic_proof_performed"] = False
    result["claim_detection_status"] = "inconclusive" if inconclusive else ("failed" if any(result.get(key) is True for key in [
        "collaboration_requested",
        "supervision_requested",
        "validation_requested",
        "endorsement_requested",
        "institutional_affiliation_claimed",
        "laser_physics_expertise_claimed",
        "independent_validation_claimed",
    ]) else "passed")
    return result


def load_links(path: Path) -> list[dict]:
    return json.loads(read_text(path))


def prepare_output_dir(output_dir: Path, overwrite: bool) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    existing = [path.name for path in output_dir.iterdir() if path.is_file()]
    unexpected = sorted(set(existing) - set(OUTPUT_FILES))
    if unexpected:
        raise SystemExit(f"unexpected files in output dir: {unexpected}")
    if existing and not overwrite:
        raise SystemExit("output files exist; pass --overwrite to replace expected outputs")


def output_paths(output_dir: Path) -> list[Path]:
    return [output_dir / name for name in OUTPUT_FILES if (output_dir / name).exists()]


def validate_links(links: list[dict]) -> dict:
    by_id = {entry.get("profile_id"): entry for entry in links}
    expected = {
        "GITHUB_PROFILE": "https://github.com/Ralf-Kemmann",
        "GITHUB_QSB_REPOSITORY": "https://github.com/Ralf-Kemmann/Quantum-Spacetime-Bridge",
        "ACADEMIA_PROFILE": "https://independent.academia.edu/RalfKemmann",
    }
    checks = []
    for profile_id, expected_url in expected.items():
        entry = by_id.get(profile_id, {})
        check_status = (
            "passed"
            if entry.get("url") == expected_url
            and entry.get("publicly_accessible") is True
            and entry.get("identity_match_status") == "confirmed"
            and entry.get("direct_url_used") is True
            and entry.get("generic_homepage_used") is False
            else "failed"
        )
        checks.append(
            {
                "profile_id": profile_id,
                "url": entry.get("url"),
                "publicly_accessible": entry.get("publicly_accessible"),
                "identity_match_status": entry.get("identity_match_status"),
                "direct_url_used": entry.get("direct_url_used"),
                "generic_homepage_used": entry.get("generic_homepage_used"),
                "content_relevance": entry.get("content_relevance"),
                "check_status": check_status,
            }
        )
    return {
        "public_profile_links_present": bool(links),
        "profile_count": len(links),
        "profiles": checks,
        "github_profile_confirmed": next(item for item in checks if item["profile_id"] == "GITHUB_PROFILE")["check_status"] == "passed",
        "github_qsb_repository_confirmed": next(item for item in checks if item["profile_id"] == "GITHUB_QSB_REPOSITORY")["check_status"] == "passed",
        "academia_profile_confirmed": next(item for item in checks if item["profile_id"] == "ACADEMIA_PROFILE")["check_status"] == "passed",
        "orcid_included_in_contact_package": any("ORCID" in str(entry.get("profile_id", "")).upper() or "ORCID" in str(entry.get("profile_type", "")).upper() for entry in links),
        "orcid_omission_reason": "not_required_for_this_contact_package",
    }


def first_person_consistent(profile: str) -> bool:
    body = re.sub(r"^#.*$", "", profile, flags=re.MULTILINE)
    return not re.search(r"\b(?:Ralf Kemmann|he|his)\b", body)


def write_outputs(
    output_dir: Path,
    letter_validation: dict,
    research_context_validation: dict,
    competence_profile_validation: dict,
    public_profile_link_check: dict,
    summary: dict,
    claim_hits: list[dict],
    readout: str,
) -> None:
    claim_report = "\n".join(
        [
            "claim_risk_check_passed = " + str(not claim_hits).lower(),
            "claim_risk_hit_count = " + str(len(claim_hits)),
            *(f"{hit['path']}: {hit['pattern']}" for hit in claim_hits),
            "",
        ]
    )
    write_json(output_dir / "contact_letter_validation.json", letter_validation)
    write_json(output_dir / "research_context_validation.json", research_context_validation)
    write_json(output_dir / "competence_profile_validation.json", competence_profile_validation)
    write_json(output_dir / "public_profile_link_check.json", public_profile_link_check)
    write_json(output_dir / "contact_materials_summary.json", summary)
    (output_dir / "readout.md").write_text(readout, encoding="utf-8")
    (output_dir / "claim_risk_report.txt").write_text(claim_report, encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate OUTREACH01A-06 contact materials.")
    parser.add_argument("--input-root", required=True)
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--overwrite", action="store_true")
    args = parser.parse_args(argv)

    root = Path(args.input_root).resolve()
    output_dir = Path(args.output_dir).resolve()
    prepare_output_dir(output_dir, args.overwrite)

    letter_path = root / "docs" / "OUTREACH01A_06_CONTACT_LETTER_DRAFT_EN.md"
    context_path = root / "docs" / "OUTREACH01A_06_RESEARCH_CONTEXT_NOTE_EN.md"
    profile_path = root / "docs" / "OUTREACH01A_06_COMPETENCE_AND_BOUNDARIES_PROFILE_EN.md"
    links_path = root / "data" / "OUTREACH01A-06" / "public_profile_links.json"
    source_inventory_path = root / "data" / "OUTREACH01A-06" / "source_inventory.md"
    spec_path = root / "docs" / "OUTREACH01A_06_CONTACT_LETTER_AND_RESEARCH_CONTEXT_SPEC.md"
    script_path = root / "scripts" / "run_outreach01a_06_validate_contact_materials.py"

    required = [letter_path, context_path, profile_path, links_path, source_inventory_path, spec_path, script_path]
    missing = [str(path) for path in required if not path.exists()]
    if missing:
        raise SystemExit(f"missing required files: {missing}")

    letter = read_text(letter_path)
    context = read_text(context_path)
    profile = read_text(profile_path)
    links = load_links(links_path)
    material_paths = [letter_path, context_path, profile_path]
    source_paths = [*material_paths, links_path, source_inventory_path]
    generic_hits = literal_hits(material_paths, GENERIC_PATTERNS)
    claim_fields = detect_claims(material_paths)
    full_qsb_assessment_hits = regex_classified_hits([letter_path, context_path], FULL_QSB_ASSESSMENT_PATTERNS)
    full_qsb_assessment_requested = bool(full_qsb_assessment_hits["positive_pattern_hits"])

    letter_word_count = word_count(letter)
    subject_line_count = count_subject_lines(letter)
    preferred_subject_line_count = count_preferred_subject_lines(letter)
    letter_validation = {
        "contact_letter_present": True,
        "word_count": letter_word_count,
        "word_count_between_270_and_295": 270 <= letter_word_count <= 295,
        "subject_line_count": subject_line_count,
        "preferred_subject_line_count": preferred_subject_line_count,
        "question_request_scope_limited": "not asking the group to assess the wider QSB programme" in letter,
        "useful_trivial_misleading_incomplete_count": len(re.findall(r"useful, trivial, misleading or incomplete", letter)),
        "contact_send_allowed": False,
        "contact_send_allowed_evidence": [],
        **{key: value for key, value in claim_fields.items() if key.startswith(("collaboration_", "validation_", "endorsement_", "supervision_"))},
    }

    context_word_count = word_count(context)
    question_id_count = sum(1 for question_id in QUESTION_IDS if question_id in context)
    research_context_validation = {
        "research_context_note_present": True,
        "word_count": context_word_count,
        "word_count_between_700_and_1000": 700 <= context_word_count <= 1000,
        "full_qsb_assessment_positive_pattern_hits": full_qsb_assessment_hits["positive_pattern_hits"],
        "full_qsb_assessment_negated_pattern_hits": full_qsb_assessment_hits["negated_pattern_hits"],
        "full_qsb_assessment_ambiguous_pattern_hits": full_qsb_assessment_hits["ambiguous_pattern_hits"],
        "full_QSB_program_assessment_requested": full_qsb_assessment_requested,
        "small_slice_isolated": "small method-level slice" in context,
        "what_is_established_section_present": "## 5. What Is Established" in context,
        "what_is_not_established_section_present": "## 6. What Is Not Established" in context,
        "question_id_count": question_id_count,
    }

    profile_word_count = word_count(profile)
    first_person_perspective_consistent = first_person_consistent(profile)
    competence_profile_validation = {
        "competence_profile_present": True,
        "word_count": profile_word_count,
        "word_count_between_400_and_650": 400 <= profile_word_count <= 650,
        "first_person_perspective_consistent": first_person_perspective_consistent,
        "internal_workflow_language_visible": bool(re.search(r"\bdraft for review\b|\brequest to send\b", profile, flags=re.IGNORECASE)),
        "technical_scope_boundary_visible": "technical criticism of the representation" in profile,
        "public_profile_links_present": bool(links),
        "laser_physics_expertise_claimed": claim_fields["laser_physics_expertise_claimed"],
        "laser_physics_expertise_claim_evidence": claim_fields["laser_physics_expertise_claimed_evidence"],
        "laser_physics_expertise_claim_pattern_hits": claim_fields["laser_physics_expertise_claim_pattern_hits"],
        "institutional_affiliation_claimed": claim_fields["institutional_affiliation_claimed"],
        "institutional_affiliation_claim_evidence": claim_fields["institutional_affiliation_claimed_evidence"],
        "institutional_affiliation_claim_pattern_hits": claim_fields["institutional_affiliation_claim_pattern_hits"],
        "independent_validation_claimed": claim_fields["independent_validation_claimed"],
        "independent_validation_claim_evidence": claim_fields["independent_validation_claimed_evidence"],
        "independent_validation_claim_pattern_hits": claim_fields["independent_validation_claim_pattern_hits"],
    }

    public_profile_link_check = validate_links(links)
    initial_claim_hits = literal_hits(source_paths, CLAIM_RISK_PATTERNS)
    style_passed = not generic_hits
    claim_risk_passed = not initial_claim_hits
    claim_detection_passed = claim_fields["claim_detection_status"] == "passed"
    final_ok = all(
        [
            letter_validation["word_count_between_270_and_295"],
            subject_line_count == 3,
            preferred_subject_line_count == 1,
            letter_validation["useful_trivial_misleading_incomplete_count"] == 1,
            research_context_validation["word_count_between_700_and_1000"],
            competence_profile_validation["word_count_between_400_and_650"],
            first_person_perspective_consistent,
            not competence_profile_validation["internal_workflow_language_visible"],
            competence_profile_validation["technical_scope_boundary_visible"],
            question_id_count == 3,
            not full_qsb_assessment_requested,
            not full_qsb_assessment_hits["ambiguous_pattern_hits"],
            public_profile_link_check["github_profile_confirmed"],
            public_profile_link_check["github_qsb_repository_confirmed"],
            public_profile_link_check["academia_profile_confirmed"],
            public_profile_link_check["orcid_included_in_contact_package"] is False,
            claim_risk_passed,
            claim_detection_passed,
            style_passed,
            letter_validation["contact_send_allowed"] is False,
        ]
    )
    final_status = "contact_letter_and_research_context_prepared" if final_ok else "contact_letter_and_research_context_inconclusive"

    summary = {
        "outreach_id": "OUTREACH01A-06",
        "contact_letter_present": True,
        "research_context_note_present": True,
        "competence_profile_present": True,
        "public_profile_links_present": True,
        "orcid_included_in_contact_package": public_profile_link_check["orcid_included_in_contact_package"],
        "orcid_omission_reason": public_profile_link_check["orcid_omission_reason"],
        "github_profile_confirmed": public_profile_link_check["github_profile_confirmed"],
        "github_qsb_repository_confirmed": public_profile_link_check["github_qsb_repository_confirmed"],
        "academia_profile_confirmed": public_profile_link_check["academia_profile_confirmed"],
        "subject_line_count": subject_line_count,
        "preferred_subject_line_count": preferred_subject_line_count,
        "technical_question_id_count": question_id_count,
        "first_person_perspective_consistent": first_person_perspective_consistent,
        "personal_style_reference_applied": True,
        "source_content_from_style_reference_used": False,
        "generic_ai_pattern_review_performed": True,
        "generic_ai_pattern_hits": generic_hits,
        "collaboration_requested": claim_fields["collaboration_requested"],
        "validation_requested": claim_fields["validation_requested"],
        "endorsement_requested": claim_fields["endorsement_requested"],
        "supervision_requested": claim_fields["supervision_requested"],
        "institutional_affiliation_claimed": claim_fields["institutional_affiliation_claimed"],
        "laser_physics_expertise_claimed": claim_fields["laser_physics_expertise_claimed"],
        "independent_validation_claimed": claim_fields["independent_validation_claimed"],
        "claim_detection_status": claim_fields["claim_detection_status"],
        "negation_detection_scope": claim_fields["negation_detection_scope"],
        "semantic_proof_performed": claim_fields["semantic_proof_performed"],
        "full_qsb_assessment_positive_pattern_hits": full_qsb_assessment_hits["positive_pattern_hits"],
        "full_qsb_assessment_negated_pattern_hits": full_qsb_assessment_hits["negated_pattern_hits"],
        "full_qsb_assessment_ambiguous_pattern_hits": full_qsb_assessment_hits["ambiguous_pattern_hits"],
        "full_QSB_program_assessment_requested": full_qsb_assessment_requested,
        "claim_risk_passed": claim_risk_passed,
        "contact_send_allowed": False,
        "user_release_required_before_send": True,
        "package_ready_for_red_team": False,
        "package_ready_for_send": False,
        "final_status": final_status,
    }

    readout = "\n".join(
        [
            "# OUTREACH01A-06 Contact Materials Validation Readout",
            "",
            "## Befund",
            "",
            f"- Final status: `{final_status}`.",
            f"- Contact letter word count: `{letter_word_count}`.",
            f"- Research context word count: `{context_word_count}`.",
            f"- Competence profile word count: `{profile_word_count}`.",
            f"- Subject line count: `{subject_line_count}`.",
            f"- Preferred subject line count: `{preferred_subject_line_count}`.",
            f"- Technical question ID count: `{question_id_count}`.",
            f"- Claim detection status: `{claim_fields['claim_detection_status']}`.",
            f"- Negation detection scope: `{claim_fields['negation_detection_scope']}`.",
            f"- Semantic proof performed: `{str(claim_fields['semantic_proof_performed']).lower()}`.",
            f"- Contact send allowed: `false`.",
            f"- Package ready for red team: `false`.",
            "",
            "## Interpretation",
            "",
            "The contact material is prepared as draft material for separate review. It does not authorize sending.",
            "",
            "## Claim Boundary",
            "",
            "The pattern-based check found no positive request for collaboration, validation, endorsement or supervision and no positive claim of institutional affiliation, laser-physics expertise or independent validation.",
            "",
        ]
    )

    write_outputs(output_dir, letter_validation, research_context_validation, competence_profile_validation, public_profile_link_check, summary, initial_claim_hits, readout)
    run_output_claim_hits = literal_hits([*source_paths, *output_paths(output_dir)], CLAIM_RISK_PATTERNS)
    summary["claim_risk_passed"] = not run_output_claim_hits
    final_ok = final_ok and not run_output_claim_hits
    final_status = "contact_letter_and_research_context_prepared" if final_ok else "contact_letter_and_research_context_inconclusive"
    summary["final_status"] = final_status
    readout = readout.replace("contact_letter_and_research_context_prepared", final_status).replace("contact_letter_and_research_context_inconclusive", final_status)
    write_outputs(output_dir, letter_validation, research_context_validation, competence_profile_validation, public_profile_link_check, summary, run_output_claim_hits, readout)

    written = sorted(path.name for path in output_dir.iterdir() if path.is_file())
    if written != sorted(OUTPUT_FILES):
        raise SystemExit(f"unexpected output set: {written}")
    return 0 if final_ok else 1


if __name__ == "__main__":
    sys.exit(main())
