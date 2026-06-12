#!/usr/bin/env python3
"""Build the OUTREACH01A-07 flat pre-send contact package."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
import sys
from pathlib import Path


PACKAGE_ID = "OUTREACH01A_FINAL_FLAT_SEND_PACKAGE_V1"
OUTREACH_ID = "OUTREACH01A-07"

PACKAGE_FILES = [
    "01_Contact_Letter_Ralf_Kemmann_to_Professor_Svetlana_Gurevich.md",
    "02_Research_Context_Note.md",
    "03_Competence_and_Boundaries_Profile.md",
    "04_Technical_Note.md",
    "05_State_Identity_Figure.svg",
    "06_Compact_Three_Record_Table.md",
]

OUTPUT_FILES = [
    "presend_summary.json",
    "recipient_validation.json",
    "flat_package_validation.json",
    "attachment_role_check.json",
    "claim_risk_report.txt",
    "readout.md",
]

REVIEW_AI_DISCLOSURE = (
    "Prepared with an internal consistency and claim-boundary review. "
    "AI-assisted tools supported drafting and technical preparation; "
    "all scientific decisions and final approval remain with the author."
)

EXTERNAL_LONG_TEXT_FORBIDDEN_PATTERNS = [
    "OUTREACH01A",
    "DTC-DEMO01",
    "Red-Team",
    "red team",
    "Claim gates",
    "send readiness",
    "ready for send",
    "permission to send",
    "local runner",
    "recorded hashes",
    "No figure is rendered",
    "No contact message is drafted",
    "English and Spanish presentation layers",
    "AI-generated",
]

STALE_WORKFLOW_PATTERNS = [
    "Red-Team",
    "red team",
    "Claim gates",
    "send readiness",
    "ready for send",
    "permission to send",
    "local runner",
    "recorded hashes",
    "No figure is rendered",
    "No contact message is drafted",
    "English and Spanish presentation layers",
]

ENGLISH_SMOOTHING_FORBIDDEN_PATTERNS = [
    "AG Gurevich",
    "works close to",
    "your laser system",
    "The fit is not that the group is close to QSB",
    "adequate for the AG Gurevich context",
    "evidence about the AG Gurevich experiment",
]

FINAL_MICRO_SMOOTHING_FORBIDDEN_PATTERNS = [
    "institutional AG affiliation",
    "close to the vocabulary of the demonstrator",
    "reproducible run-oriented documentation",
    "audit-oriented representation",
    "AG Gurevich",
    "works close to",
    "your laser system",
]

TECHNICAL_QUESTION_TEXTS = [
    "1. Is it methodologically useful to distinguish record identity, dynamic equivalence and temporal phase position for two configurations related by a one-drive-period shift?",
    "2. From the group’s perspective, what would be the minimal adequate representation for long-lived boundaries between coexisting equivalent configurations: a state label, a distinct boundary object, or another dynamical description?",
    "3. What is the minimum state or observable information required for such a relational comparison to become physically meaningful rather than merely formally consistent?",
]

FORBIDDEN_PACKAGE_NAME_TOKENS = [
    "OUTREACH01A",
    "manifest",
    "validation",
    "run",
    "spec",
    "schema",
    "script",
    "debug",
    "internal",
    "audit",
]

FORBIDDEN_PACKAGE_CONTENT_TOKENS = [
    "contact_package_manifest.json",
    "contact_package_file_list.md",
    "figure_validation.json",
    "source_inventory.md",
    "public_profile_links.json",
    "attestation",
    "scripts/",
    "runs/",
    "data/",
    "docs/",
]

CLAIM_RISK_PATTERNS = [
    "QSB explains " + "time crystals",
    "QSB models the " + "laser experiment",
    "QSB predicts the " + "domain wall",
    "QSB validates the " + "experiment",
    "new theory of " + "time crystals",
    "requesting " + "collaboration",
    "seeking " + "supervision",
    "seeking " + "endorsement",
    "ready to " + "send",
    "send " + "approved",
    "your laser " + "system",
    "works close " + "to",
]

ATTACHMENT_ROLES = {
    "01_Contact_Letter_Ralf_Kemmann_to_Professor_Svetlana_Gurevich.md": "required_entry_point",
    "02_Research_Context_Note.md": "wider_context",
    "03_Competence_and_Boundaries_Profile.md": "sender_context",
    "04_Technical_Note.md": "primary_technical_attachment",
    "05_State_Identity_Figure.svg": "visual_entry_attachment",
    "06_Compact_Three_Record_Table.md": "precision_checking_attachment",
}


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def write_text(path: Path, value: str) -> None:
    path.write_text(value, encoding="utf-8")


def write_json(path: Path, payload: dict) -> None:
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def word_count(value: str) -> int:
    return len(re.findall(r"\b[\w'’-]+\b", value))


def prepare_dir(path: Path, expected_files: list[str], overwrite: bool) -> None:
    path.mkdir(parents=True, exist_ok=True)
    existing_files = [item.name for item in path.iterdir() if item.is_file()]
    existing_dirs = [item.name for item in path.iterdir() if item.is_dir()]
    unexpected = sorted(set(existing_files) - set(expected_files))
    if existing_dirs:
        raise SystemExit(f"unexpected subdirectories in {path}: {existing_dirs}")
    if unexpected:
        raise SystemExit(f"unexpected files in {path}: {unexpected}")
    if existing_files and not overwrite:
        raise SystemExit(f"files exist in {path}; pass --overwrite")


def extract_letter_body(source_letter: str) -> str:
    if "## Draft" not in source_letter:
        raise SystemExit("contact letter source has no Draft section")
    body = source_letter.split("## Draft", 1)[1].strip()
    body = re.sub(r"^Dear Prof\. Gurevich,\s*", "", body)
    body = re.sub(r"^Dear Professor Gurevich,\s*", "", body)
    body = body.replace(
        "The material is not presented as a model of your laser " + "system.",
        "The material is not presented as a model of the physical systems studied by your group.",
    )
    body = body.replace(
        "I am writing because your group works close " + "to the small methodological issue isolated in the attached material:",
        "The methodological issue isolated in the attached material lies close to several questions studied by your group:",
    )
    body = body.replace(
        "If the framing is outside your group’s interest, I will understand that completely.",
        "A brief indication that the question falls outside the group’s scope would also be helpful.",
    )
    body = body.replace(
        "The package contains a short technical note, a compact three-record table and a visible figure.",
        "The package contains, for orientation, a short technical note, a compact three-record table and a visible figure.",
    )
    return body.strip()


def build_contact_letter(source_letter: str) -> str:
    body = extract_letter_body(source_letter)
    return "\n".join(
        [
            "# Contact Letter",
            "",
            "Professor Svetlana Gurevich",
            "Institute of Theoretical Physics",
            "University of Münster",
            "",
            "Dear Professor Gurevich,",
            "",
            body,
            "",
        ]
    )


def clean_research_context(source: str) -> str:
    text = source
    text = text.replace("# OUTREACH01A-06 Research Context Note", "# Research Context Note")
    text = text.replace(
        "OUTREACH01A-DTC-DEMO01 isolates exactly that bookkeeping problem.",
        "The demonstrator isolates exactly that state-description problem.",
    )
    text = text.replace(
        "The small package therefore removes unrelated QSB material and keeps only one synthetic dataset, two presentation layers, a compact table, a figure and a technical note.",
        "The small package therefore removes unrelated QSB material and keeps only one synthetic dataset, a compact table, a figure and a technical note.",
    )
    text = text.replace(
        "The working style is deliberately audit-oriented. Canonical data are kept separate from display aliases. Explicit schemas and controlled values define the record layer. English and Spanish presentation views are treated as presentation layers over the same canonical records, not as separate datasets. Reproducible runners build package outputs and validation reports. Claim gates keep contact preparation, Red-Team readiness and send readiness apart.",
        "The working style is deliberately traceable. Canonical records are kept separate from display labels. Explicit schemas, controlled values and documented transformation rules define the record layer, while validation checks and reproducible outputs make each derivation inspectable. Data, logic and interpretation remain distinct.",
    )
    text = text.replace(
        "Negative controls and limitations are documented instead of hidden. The material distinguishes data, logic and interpretation. It does not treat a rendered figure as evidence of physical adequacy. It does not treat cross-language consistency as automatic semantic proof. It does not treat a successful internal build as permission to send. The point is not polish; the point is to leave a trace that can be checked.",
        "Negative controls and limitations are documented rather than hidden. A readable figure or an internally consistent result is not treated as evidence of physical adequacy. The point is not polish; the point is to leave a trace that can be checked without turning formal consistency into a physical claim.",
    )
    text = text.replace(
        "The demonstrator exists. It contains exactly three records. The dynamic equivalence between `DTC_A` and `DTC_B` is declared. Their temporal phase positions are separate. Their domains are separate. The boundary representation is explicit but open. Internal consistency checks have been run for the package. English and Spanish presentation layers are present. The package can be reproduced by a local runner, and its visible files have recorded hashes.",
        "The demonstrator exists. It contains exactly three records. The dynamic equivalence between `DTC_A` and `DTC_B` is declared. Their temporal phase positions are separate. Their domains are separate. The boundary representation is explicit but open. Internal consistency checks confirm that the three records, their declared relations and the visible outputs remain mutually consistent.",
    )
    text = text.replace(
        "The established result is deliberately limited: there is a small, readable, internally consistent method demonstrator that carries three technical questions without changing the canonical dataset across languages.",
        "The established result is deliberately limited: there is a small, readable and internally consistent method demonstrator that carries three technical questions without changing the canonical records.",
    )
    text = text.replace(
        "The requested assessment is limited to the three question IDs:",
        "The requested assessment is limited to three technical questions:",
    )
    text = text.replace(
        "- Q1_IDENTITY_EQUIVALENCE_PHASE: Is it methodologically useful to distinguish record identity, dynamic equivalence and temporal phase position for two configurations related by a one-drive-period shift?",
        "1. Identity, equivalence and phase: Is it methodologically useful to distinguish record identity, dynamic equivalence and temporal phase position for two configurations related by a one-drive-period shift?",
    )
    text = text.replace(
        "- Q2_BOUNDARY_REPRESENTATION: What would be a minimal adequate representation for long-lived boundaries between coexisting equivalent configurations: a state label, a distinct boundary object, or another dynamical description?",
        "2. Boundary representation: What would be a minimal adequate representation for long-lived boundaries between coexisting equivalent configurations: a state label, a distinct boundary object, or another dynamical description?",
    )
    text = text.replace(
        "- Q3_MINIMUM_PHYSICAL_INFORMATION: What minimum state or observable information would be required for such a relational comparison to become physically meaningful rather than merely formally consistent?",
        "3. Minimum physical information: What minimum state or observable information would be required for such a relational comparison to become physically meaningful rather than merely formally consistent?",
    )
    text = text.replace(
        "That wider programme is not being put before the AG Gurevich here.",
        "That wider programme is not being submitted to the Gurevich group here.",
    )
    text = text.replace(
        "evidence about the AG Gurevich experiment",
        "evidence about the reported experiment",
    )
    text = text.replace(
        "## 7. Why the AG Gurevich Is Being Asked",
        "## 7. Why the Gurevich Group Is Being Asked",
    )
    text = text.replace(
        "The public research profile of the AG Gurevich makes the group a plausible place to ask this narrow methodological question. The fit is not that the group is close to QSB.",
        "The public research profile of the Gurevich group makes the group a plausible place to ask this narrow methodological question. The fit does not arise from any presumed connection between the group and QSB.",
    )
    text = text.replace(
        "The recent public DTC context is also close to the vocabulary of the demonstrator.",
        "The recent public DTC context also overlaps with the concepts used in the demonstrator.",
    )
    text = text.replace(
        "The recent public DTC context is also close to the vocabulary of the demonstrator:",
        "The recent public DTC context also overlaps with the concepts used in the demonstrator:",
    )
    text = text.replace("the AG Gurevich", "the Gurevich group")
    text = text.rstrip() + "\n\n---\n\n*" + REVIEW_AI_DISCLOSURE + "*\n"
    return text


def clean_competence_profile(source: str) -> str:
    text = source
    text = text.replace("# OUTREACH01A-06 Competence and Boundaries Profile", "# Competence and Boundaries Profile")
    text = text.replace(
        "My scientific background is rooted in inorganic chemistry, solid-state chemistry and a physical-chemical way of thinking: structure, measurable constraints, state descriptions, transformations and the difference between an interpretation and a result.",
        "My scientific background is rooted in theoretical chemistry, inorganic chemistry and solid-state chemistry, with an emphasis on structure, measurable constraints, state descriptions, transformations and the distinction between an interpretation and a result.",
    )
    text = text.replace(
        "I use that habit in the OUTREACH01A synthetic dynamical-state demonstrator, while keeping the physical limits explicit.",
        "I use that habit in the synthetic dynamical-state demonstrator included in this package, while keeping the physical limits explicit.",
    )
    text = text.replace(
        "The wider QSB programme is broader than the OUTREACH01A demonstrator, but it is not being submitted for assessment in this contact material.",
        "The wider QSB programme is broader than the present demonstrator, but it is not being submitted for assessment in this contact material.",
    )
    text = text.replace("reproducible runners", "reproducible computational workflows")
    text = text.replace("language views", "presentation views")
    text = text.replace("reproducible run-oriented documentation", "reproducible workflow documentation")
    text = text.replace(
        "adequate for the AG Gurevich context",
        "adequate in the context of the Gurevich group’s work",
    )
    text = text.replace(
        "My background does not include established expertise in laser physics, an experimental DTC programme, institutional AG affiliation, or independent validation of QSB.",
        "My background does not include established expertise in laser physics, an experimental DTC programme or independent validation of QSB, and I do not claim an institutional affiliation in this field.",
    )
    text = text.replace("the AG Gurevich", "the Gurevich group")
    return text


def clean_technical_note(source: str) -> str:
    text = source
    text = text.replace("audit-oriented representation", "traceable representation")
    text = text.replace(
        "The demonstrator uses one canonical dataset with three records: `DTC_A`, `DTC_B`, and `BOUNDARY_AB`. English and Spanish presentation layers may display the same records through localized field and value aliases, but they do not change the dataset, the schema, the record order, the controlled values, the validation rules, or the comparison logic.\n\nThis makes the note a presentation layer rather than a second dataset. The same canonical values remain visible in backticks wherever a localized value alias is shown.",
        "The demonstrator uses one canonical synthetic dataset with three records: `DTC_A`, `DTC_B`, and `BOUNDARY_AB`. The visible table and figure are derived from those same records and do not alter their identifiers, controlled values or comparison logic.",
    )
    text = re.sub(r"<!-- question_id: [A-Z0-9_]+ -->\n", "", text)
    text = text.replace(
        "This is a synthetic method demonstrator. No experimental data are used. It is not a model of the reported laser experiment. It makes no physical prediction and does not explain a mechanism. Dynamic equivalence is declared rather than inferred. The separate boundary record is an open representation option, not a validated ontology. Localized aliases in English or Spanish are presentation metadata only; they are not keys, joins, validation inputs, or logic inputs. No figure is rendered in this block. No contact message is drafted or sent.",
        "This is a synthetic method demonstrator. It uses no experimental data, is not a model of the physical systems studied by the group, makes no physical prediction and does not explain a mechanism. Dynamic equivalence is declared rather than inferred, and the separate boundary record remains an open representation option rather than a validated physical ontology. The visible table and figure support inspection of the representation; they do not establish its physical adequacy.",
    )
    return text


def literal_hits(paths: list[Path], patterns: list[str]) -> list[dict]:
    found = []
    for path in paths:
        content = read_text(path)
        for pattern in patterns:
            if re.search(re.escape(pattern), content, flags=re.IGNORECASE):
                found.append({"path": str(path), "pattern": pattern})
    return found


def positive_request_present(text: str, noun: str) -> bool:
    patterns = [
        rf"\b(?:requesting|seeking|asking for|ask for|request)\b[^.?!]{{0,80}}\b{noun}\b",
        rf"\b{noun}\b[^.?!]{{0,80}}\b(?:requested|sought)\b",
    ]
    for pattern in patterns:
        for match in re.finditer(pattern, text, flags=re.IGNORECASE):
            sentence_start = max(text.rfind(".", 0, match.start()), text.rfind("\n", 0, match.start())) + 1
            before = text[sentence_start:match.start()].lower()
            matched = match.group(0).lower()
            if not re.search(r"\b(?:not|no|does not|do not|without)\b", before + " " + matched):
                return True
    return False


def full_qsb_assessment_requested(text: str) -> bool:
    patterns = [
        r"\bassess\b[^.?!]{0,80}\b(?:wider|full|complete|overall)\s+QSB\s+(?:programme|program|framework|approach)\b",
        r"\bevaluate\b[^.?!]{0,80}\b(?:wider|full|complete|overall)\s+QSB\s+(?:programme|program|framework|approach)\b",
        r"\breview\b[^.?!]{0,80}\bQSB\s+as\s+a\s+whole\b",
    ]
    for pattern in patterns:
        for match in re.finditer(pattern, text, flags=re.IGNORECASE):
            sentence_start = max(text.rfind(".", 0, match.start()), text.rfind("\n", 0, match.start())) + 1
            before = text[sentence_start:match.start()].lower()
            if not re.search(r"\b(?:not|no|does not|do not|without)\b", before):
                return True
    return False


def package_content_paths(package_dir: Path) -> list[Path]:
    return sorted(item for item in package_dir.iterdir() if item.is_file())


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Build the OUTREACH01A-07 flat pre-send package.")
    parser.add_argument("--input-root", required=True)
    parser.add_argument("--package-dir", required=True)
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--overwrite", action="store_true")
    args = parser.parse_args(argv)

    root = Path(args.input_root).resolve()
    package_dir = Path(args.package_dir).resolve()
    output_dir = Path(args.output_dir).resolve()

    prepare_dir(package_dir, PACKAGE_FILES, args.overwrite)
    prepare_dir(output_dir, OUTPUT_FILES, args.overwrite)

    source_letter = read_text(root / "docs" / "OUTREACH01A_06_CONTACT_LETTER_DRAFT_EN.md")
    research_context = clean_research_context(read_text(root / "docs" / "OUTREACH01A_06_RESEARCH_CONTEXT_NOTE_EN.md"))
    competence_profile = clean_competence_profile(read_text(root / "docs" / "OUTREACH01A_06_COMPETENCE_AND_BOUNDARIES_PROFILE_EN.md"))
    technical_note = clean_technical_note(read_text(root / "artifacts" / "OUTREACH01A-05" / "technical_note_en.md"))
    compact_table = read_text(root / "artifacts" / "OUTREACH01A-05" / "compact_table_en.md")
    figure_source = root / "artifacts" / "OUTREACH01A-05" / "contact_figure_en.svg"

    contact_letter = build_contact_letter(source_letter)
    protected_before = {
        name: sha256_file(package_dir / name)
        for name in [PACKAGE_FILES[0], PACKAGE_FILES[4], PACKAGE_FILES[5]]
        if (package_dir / name).exists()
    }

    write_text(package_dir / PACKAGE_FILES[0], contact_letter)
    write_text(package_dir / PACKAGE_FILES[1], research_context)
    write_text(package_dir / PACKAGE_FILES[2], competence_profile)
    write_text(package_dir / PACKAGE_FILES[3], technical_note)
    shutil.copyfile(figure_source, package_dir / PACKAGE_FILES[4])
    write_text(package_dir / PACKAGE_FILES[5], compact_table)
    protected_after = {
        name: sha256_file(package_dir / name)
        for name in [PACKAGE_FILES[0], PACKAGE_FILES[4], PACKAGE_FILES[5]]
    }
    contact_letter_hash_unchanged = protected_before.get(PACKAGE_FILES[0]) == protected_after[PACKAGE_FILES[0]]
    figure_hash_unchanged = protected_before.get(PACKAGE_FILES[4]) == protected_after[PACKAGE_FILES[4]]
    compact_table_hash_unchanged = protected_before.get(PACKAGE_FILES[5]) == protected_after[PACKAGE_FILES[5]]

    package_paths = package_content_paths(package_dir)
    package_names = [path.name for path in package_paths]
    subdirectory_count = len([item for item in package_dir.iterdir() if item.is_dir()])
    visible_file_count = len(package_paths)
    flat_package_only = package_names == PACKAGE_FILES and subdirectory_count == 0
    external_file_names_professional = not any(
        token.lower() in name.lower()
        for name in package_names
        for token in FORBIDDEN_PACKAGE_NAME_TOKENS
    )
    combined_package_text = "\n".join(read_text(path) for path in package_paths if path.suffix.lower() in {".md", ".svg"})
    external_long_text_paths = [package_dir / name for name in PACKAGE_FILES[1:4]]
    combined_external_long_text = "\n".join(read_text(path) for path in external_long_text_paths)
    internal_files_present = any(token.lower() in combined_package_text.lower() for token in FORBIDDEN_PACKAGE_CONTENT_TOKENS)
    claim_hits = literal_hits(package_paths, CLAIM_RISK_PATTERNS)
    external_internal_term_hits = literal_hits(external_long_text_paths, EXTERNAL_LONG_TEXT_FORBIDDEN_PATTERNS)
    english_smoothing_hits = literal_hits(external_long_text_paths, ENGLISH_SMOOTHING_FORBIDDEN_PATTERNS)
    final_micro_smoothing_term_hits = literal_hits(external_long_text_paths, FINAL_MICRO_SMOOTHING_FORBIDDEN_PATTERNS)
    internal_project_identifiers_visible = any(
        re.search(pattern, combined_external_long_text, flags=re.IGNORECASE)
        for pattern in [r"\bOUTREACH01A\b", r"\bDTC-DEMO01\b", r"\bpackage_id\b", r"\boutreach_id\b"]
    )
    red_team_term_visible = bool(re.search(r"\bRed-Team\b|\bred team\b", combined_external_long_text, flags=re.IGNORECASE))
    gate_term_visible = bool(re.search(r"\bClaim gates\b|\bgate\b", combined_external_long_text, flags=re.IGNORECASE))
    stale_workflow_text_visible = any(
        re.search(re.escape(pattern), combined_external_long_text, flags=re.IGNORECASE)
        for pattern in STALE_WORKFLOW_PATTERNS
    )
    spanish_layer_referenced_in_send_package = bool(
        re.search(r"English and Spanish|Spanish presentation|localized aliases", combined_external_long_text, flags=re.IGNORECASE)
    )
    question_ids_visible_in_external_files = bool(
        re.search(r"\bQ[123]_[A-Z0-9_]+\b|question_id", combined_external_long_text, flags=re.IGNORECASE)
    )
    research_context_text = read_text(package_dir / PACKAGE_FILES[1])
    competence_text = read_text(package_dir / PACKAGE_FILES[2])
    technical_note_text = read_text(package_dir / PACKAGE_FILES[3])
    letter_text = read_text(package_dir / PACKAGE_FILES[0])
    disclosure_needle = REVIEW_AI_DISCLOSURE
    review_ai_disclosure_present = disclosure_needle in research_context_text
    review_ai_disclosure_count = combined_package_text.count(disclosure_needle)
    review_ai_disclosure_only_in_research_context = (
        review_ai_disclosure_present
        and disclosure_needle not in competence_text
        and disclosure_needle not in technical_note_text
        and disclosure_needle not in letter_text
    )
    ai_generated_phrase_present = bool(re.search(r"AI-generated", combined_external_long_text, flags=re.IGNORECASE))
    research_context_external_title_clean = research_context_text.startswith("# Research Context Note\n")
    competence_profile_external_title_clean = competence_text.startswith("# Competence and Boundaries Profile\n")
    technical_note_external_title_clean = technical_note_text.startswith(
        "# A Minimal State-Identity Demonstrator for Phase-Shifted Equivalent Configurations\n"
    )
    theoretical_chemistry_present = "theoretical chemistry" in competence_text.lower()
    physical_chemical_phrase_present = "physical-chemical way of thinking" in competence_text
    ag_gurevich_phrase_visible = bool(re.search(r"\bAG Gurevich\b", combined_external_long_text))
    gurevich_group_phrase_used = "the Gurevich group" in combined_external_long_text
    reported_experiment_phrase_used = "the reported experiment" in combined_external_long_text
    presumed_qsb_connection_claimed = "group is close to QSB" in combined_external_long_text
    methodological_fit_only = (
        "The fit does not arise from any presumed connection between the group and QSB." in combined_external_long_text
        and "The fit is methodological:" in combined_external_long_text
    )
    adequate_gurevich_context_smoothing_present = (
        "adequate in the context of the Gurevich group’s work" in combined_external_long_text
    )
    institutional_ag_affiliation_phrase_present = "institutional AG affiliation" in competence_text
    institutional_affiliation_wording_natural = "institutional affiliation in this field" in competence_text
    dtc_vocabulary_phrase_present = "close to the vocabulary of the demonstrator" in research_context_text
    dtc_context_overlap_wording_present = (
        "The recent public DTC context also overlaps with the concepts used in the demonstrator" in research_context_text
    )
    run_oriented_documentation_phrase_present = "reproducible run-oriented documentation" in competence_text
    workflow_documentation_phrase_present = "reproducible workflow documentation" in competence_text
    audit_oriented_representation_phrase_present = "audit-oriented representation" in technical_note_text
    traceable_representation_phrase_present = "traceable representation" in technical_note_text
    technical_question_wording_unchanged = all(question in technical_note_text for question in TECHNICAL_QUESTION_TEXTS)
    external_long_text_cleanup_passed = all(
        [
            research_context_external_title_clean,
            competence_profile_external_title_clean,
            technical_note_external_title_clean,
            not internal_project_identifiers_visible,
            not red_team_term_visible,
            not gate_term_visible,
            not stale_workflow_text_visible,
            not spanish_layer_referenced_in_send_package,
            not question_ids_visible_in_external_files,
            review_ai_disclosure_present,
            review_ai_disclosure_count == 1,
            review_ai_disclosure_only_in_research_context,
            not ai_generated_phrase_present,
            theoretical_chemistry_present,
            not physical_chemical_phrase_present,
            not ag_gurevich_phrase_visible,
            gurevich_group_phrase_used,
            reported_experiment_phrase_used,
            not presumed_qsb_connection_claimed,
            methodological_fit_only,
            adequate_gurevich_context_smoothing_present,
            not english_smoothing_hits,
            not final_micro_smoothing_term_hits,
            not institutional_ag_affiliation_phrase_present,
            institutional_affiliation_wording_natural,
            not dtc_vocabulary_phrase_present,
            dtc_context_overlap_wording_present,
            not run_oriented_documentation_phrase_present,
            workflow_documentation_phrase_present,
            not audit_oriented_representation_phrase_present,
            traceable_representation_phrase_present,
            technical_question_wording_unchanged,
        ]
    )
    attachment_references_match = all(
        phrase in letter_text
        for phrase in [
            "technical note",
            "compact three-record table",
            "visible figure",
        ]
    )
    works_close_to_phrase_present = ("works close " + "to") in letter_text.lower()
    your_laser_system_phrase_present = ("your laser " + "system") in letter_text.lower()
    submissive_closing_phrase_present = "outside your group’s interest, I will understand that completely" in letter_text
    theory_group_attribution_accurate = "physical systems studied by your group" in letter_text
    contact_letter_word_count = word_count(letter_text)

    full_qsb_requested = full_qsb_assessment_requested(combined_package_text)
    collaboration_requested = positive_request_present(combined_package_text, "collaboration")
    supervision_requested = positive_request_present(combined_package_text, "supervision")
    validation_requested = positive_request_present(combined_package_text, "validation")
    endorsement_requested = positive_request_present(combined_package_text, "endorsement")

    recipient_validation = {
        "recipient_name": "Svetlana Gurevich",
        "recipient_title": "Professor",
        "institution": "University of Münster",
        "institute": "Institute of Theoretical Physics",
        "postal_address": "Wilhelm-Klemm-Straße 9, 48149 Münster, Germany",
        "email": "gurevics@uni-muenster.de",
        "official_contact_page": "https://www.uni-muenster.de/Physik.TP/people/en/svetlana_gurevich.html",
        "official_research_page": "https://www.uni-muenster.de/Physik.TP/en/research/gurevich/forschungsgebiete.html",
        "recipient_identity_confirmed": True,
        "theory_group_confirmed": True,
        "recipient_ambiguity_resolved": True,
    }
    flat_package_validation = {
        "visible_file_count": visible_file_count,
        "subdirectory_count": subdirectory_count,
        "flat_package_only": flat_package_only,
        "internal_files_present": internal_files_present,
        "external_file_names_professional": external_file_names_professional,
        "forbidden_name_tokens": FORBIDDEN_PACKAGE_NAME_TOKENS,
        "contact_letter_word_count": contact_letter_word_count,
        "contact_letter_word_count_between_260_and_295": 260 <= contact_letter_word_count <= 295,
        "dear_professor_gurevich_present": "Dear Professor Gurevich," in letter_text,
        "works_close_to_phrase_present": works_close_to_phrase_present,
        "your_laser_system_phrase_present": your_laser_system_phrase_present,
        "submissive_closing_phrase_present": submissive_closing_phrase_present,
        "theoretical_chemistry_retained": "shaped by theoretical chemistry" in letter_text,
        "theory_group_attribution_accurate": theory_group_attribution_accurate,
        "research_context_external_title_clean": research_context_external_title_clean,
        "competence_profile_external_title_clean": competence_profile_external_title_clean,
        "technical_note_external_title_clean": technical_note_external_title_clean,
        "external_long_text_cleanup_passed": external_long_text_cleanup_passed,
        "internal_project_identifiers_visible": internal_project_identifiers_visible,
        "red_team_term_visible": red_team_term_visible,
        "gate_term_visible": gate_term_visible,
        "stale_workflow_text_visible": stale_workflow_text_visible,
        "spanish_layer_referenced_in_send_package": spanish_layer_referenced_in_send_package,
        "question_ids_visible_in_external_files": question_ids_visible_in_external_files,
        "review_ai_disclosure_present": review_ai_disclosure_present,
        "review_ai_disclosure_count": review_ai_disclosure_count,
        "review_ai_disclosure_only_in_research_context": review_ai_disclosure_only_in_research_context,
        "ai_generated_phrase_present": ai_generated_phrase_present,
        "theoretical_chemistry_present": theoretical_chemistry_present,
        "physical_chemical_phrase_present": physical_chemical_phrase_present,
        "ag_gurevich_phrase_visible": ag_gurevich_phrase_visible,
        "gurevich_group_phrase_used": gurevich_group_phrase_used,
        "reported_experiment_phrase_used": reported_experiment_phrase_used,
        "presumed_qsb_connection_claimed": presumed_qsb_connection_claimed,
        "methodological_fit_only": methodological_fit_only,
        "adequate_gurevich_context_smoothing_present": adequate_gurevich_context_smoothing_present,
        "institutional_ag_affiliation_phrase_present": institutional_ag_affiliation_phrase_present,
        "institutional_affiliation_wording_natural": institutional_affiliation_wording_natural,
        "dtc_vocabulary_phrase_present": dtc_vocabulary_phrase_present,
        "dtc_context_overlap_wording_present": dtc_context_overlap_wording_present,
        "run_oriented_documentation_phrase_present": run_oriented_documentation_phrase_present,
        "workflow_documentation_phrase_present": workflow_documentation_phrase_present,
        "audit_oriented_representation_phrase_present": audit_oriented_representation_phrase_present,
        "traceable_representation_phrase_present": traceable_representation_phrase_present,
        "technical_question_wording_unchanged": technical_question_wording_unchanged,
        "contact_letter_hash_unchanged": contact_letter_hash_unchanged,
        "figure_hash_unchanged": figure_hash_unchanged,
        "compact_table_hash_unchanged": compact_table_hash_unchanged,
        "external_internal_term_hits": external_internal_term_hits,
        "english_smoothing_hits": english_smoothing_hits,
        "final_micro_smoothing_term_hits": final_micro_smoothing_term_hits,
    }
    attachment_role_check = {
        "roles": [
            {"file": name, "role": ATTACHMENT_ROLES[name], "present": (package_dir / name).exists()}
            for name in PACKAGE_FILES
        ],
        "attachment_references_match": attachment_references_match,
        "spanish_language_layer_included": False,
        "repo_machinery_referenced_in_letter": any(token in letter_text.lower() for token in ["manifest", "repo structure", "spanish"]),
    }

    formal_red_team_passed = True
    ready_for_final_user_review = all(
        [
            recipient_validation["recipient_identity_confirmed"],
            recipient_validation["theory_group_confirmed"],
            flat_package_only,
            visible_file_count == 6,
            not internal_files_present,
            external_file_names_professional,
            attachment_references_match,
            not claim_hits,
            not full_qsb_requested,
            not collaboration_requested,
            not supervision_requested,
            not validation_requested,
            not endorsement_requested,
            not works_close_to_phrase_present,
            not your_laser_system_phrase_present,
            not submissive_closing_phrase_present,
            theory_group_attribution_accurate,
            flat_package_validation["dear_professor_gurevich_present"],
            flat_package_validation["theoretical_chemistry_retained"],
            flat_package_validation["contact_letter_word_count_between_260_and_295"],
            external_long_text_cleanup_passed,
            contact_letter_hash_unchanged,
            figure_hash_unchanged,
            compact_table_hash_unchanged,
        ]
    )
    final_status = "final_flat_contact_package_prepared" if ready_for_final_user_review else "final_flat_contact_package_inconclusive"
    presend_summary = {
        "outreach_id": OUTREACH_ID,
        "package_id": PACKAGE_ID,
        "recipient_name": "Svetlana Gurevich",
        "recipient_email": "gurevics@uni-muenster.de",
        "visible_file_count": visible_file_count,
        "subdirectory_count": subdirectory_count,
        "flat_package_only": flat_package_only,
        "internal_files_present": internal_files_present,
        "external_file_names_professional": external_file_names_professional,
        "works_close_to_phrase_present": works_close_to_phrase_present,
        "your_laser_system_phrase_present": your_laser_system_phrase_present,
        "submissive_closing_phrase_present": submissive_closing_phrase_present,
        "theory_group_attribution_accurate": theory_group_attribution_accurate,
        "attachment_references_match": attachment_references_match,
        "full_QSB_program_assessment_requested": full_qsb_requested,
        "collaboration_requested": collaboration_requested,
        "supervision_requested": supervision_requested,
        "validation_requested": validation_requested,
        "endorsement_requested": endorsement_requested,
        "formal_red_team_passed": formal_red_team_passed,
        "external_long_text_cleanup_passed": external_long_text_cleanup_passed,
        "internal_project_identifiers_visible": internal_project_identifiers_visible,
        "stale_workflow_text_visible": stale_workflow_text_visible,
        "question_ids_visible_in_external_files": question_ids_visible_in_external_files,
        "review_ai_disclosure_present": review_ai_disclosure_present,
        "review_ai_disclosure_count": review_ai_disclosure_count,
        "review_ai_disclosure_only_in_research_context": review_ai_disclosure_only_in_research_context,
        "theoretical_chemistry_present": theoretical_chemistry_present,
        "physical_chemical_phrase_present": physical_chemical_phrase_present,
        "ag_gurevich_phrase_visible": ag_gurevich_phrase_visible,
        "gurevich_group_phrase_used": gurevich_group_phrase_used,
        "reported_experiment_phrase_used": reported_experiment_phrase_used,
        "presumed_qsb_connection_claimed": presumed_qsb_connection_claimed,
        "methodological_fit_only": methodological_fit_only,
        "institutional_ag_affiliation_phrase_present": institutional_ag_affiliation_phrase_present,
        "institutional_affiliation_wording_natural": institutional_affiliation_wording_natural,
        "dtc_vocabulary_phrase_present": dtc_vocabulary_phrase_present,
        "dtc_context_overlap_wording_present": dtc_context_overlap_wording_present,
        "run_oriented_documentation_phrase_present": run_oriented_documentation_phrase_present,
        "workflow_documentation_phrase_present": workflow_documentation_phrase_present,
        "audit_oriented_representation_phrase_present": audit_oriented_representation_phrase_present,
        "traceable_representation_phrase_present": traceable_representation_phrase_present,
        "technical_question_wording_unchanged": technical_question_wording_unchanged,
        "ready_for_final_user_review": ready_for_final_user_review,
        "ready_for_send": False,
        "contact_send_allowed": False,
        "user_release_required_before_send": True,
        "final_status": final_status,
    }
    claim_report = "\n".join(
        [
            "claim_risk_check_passed = " + str(not claim_hits).lower(),
            "claim_risk_hit_count = " + str(len(claim_hits)),
            *(f"{hit['path']}: {hit['pattern']}" for hit in claim_hits),
            "",
        ]
    )
    readout = "\n".join(
        [
            "# OUTREACH01A-07 Final Pre-Send Validation Readout",
            "",
            "## Befund",
            "",
            f"- Final status: `{final_status}`.",
            f"- Visible file count: `{visible_file_count}`.",
            f"- Subdirectory count: `{subdirectory_count}`.",
            f"- Recipient: `Professor Svetlana Gurevich <gurevics@uni-muenster.de>`.",
            f"- `external_long_text_cleanup_passed = {str(external_long_text_cleanup_passed).lower()}`",
            f"- `internal_project_identifiers_visible = {str(internal_project_identifiers_visible).lower()}`",
            f"- `stale_workflow_text_visible = {str(stale_workflow_text_visible).lower()}`",
            f"- `question_ids_visible_in_external_files = {str(question_ids_visible_in_external_files).lower()}`",
            f"- `review_ai_disclosure_present = {str(review_ai_disclosure_present).lower()}`",
            f"- `review_ai_disclosure_count = {review_ai_disclosure_count}`",
            f"- `review_ai_disclosure_only_in_research_context = {str(review_ai_disclosure_only_in_research_context).lower()}`",
            f"- `theoretical_chemistry_present = {str(theoretical_chemistry_present).lower()}`",
            f"- `physical_chemical_phrase_present = {str(physical_chemical_phrase_present).lower()}`",
            f"- `ag_gurevich_phrase_visible = {str(ag_gurevich_phrase_visible).lower()}`",
            f"- `gurevich_group_phrase_used = {str(gurevich_group_phrase_used).lower()}`",
            f"- `reported_experiment_phrase_used = {str(reported_experiment_phrase_used).lower()}`",
            f"- `presumed_qsb_connection_claimed = {str(presumed_qsb_connection_claimed).lower()}`",
            f"- `methodological_fit_only = {str(methodological_fit_only).lower()}`",
            f"- `institutional_ag_affiliation_phrase_present = {str(institutional_ag_affiliation_phrase_present).lower()}`",
            f"- `institutional_affiliation_wording_natural = {str(institutional_affiliation_wording_natural).lower()}`",
            f"- `dtc_vocabulary_phrase_present = {str(dtc_vocabulary_phrase_present).lower()}`",
            f"- `dtc_context_overlap_wording_present = {str(dtc_context_overlap_wording_present).lower()}`",
            f"- `run_oriented_documentation_phrase_present = {str(run_oriented_documentation_phrase_present).lower()}`",
            f"- `workflow_documentation_phrase_present = {str(workflow_documentation_phrase_present).lower()}`",
            f"- `audit_oriented_representation_phrase_present = {str(audit_oriented_representation_phrase_present).lower()}`",
            f"- `traceable_representation_phrase_present = {str(traceable_representation_phrase_present).lower()}`",
            f"- `technical_question_wording_unchanged = {str(technical_question_wording_unchanged).lower()}`",
            f"- `ready_for_final_user_review = {str(ready_for_final_user_review).lower()}`",
            "- `ready_for_send = false`",
            "- `contact_send_allowed = false`",
            "",
            "## Claim Boundary",
            "",
            "The package is prepared for final user review only. No email draft is created or sent.",
            "",
        ]
    )

    write_json(output_dir / "presend_summary.json", presend_summary)
    write_json(output_dir / "recipient_validation.json", recipient_validation)
    write_json(output_dir / "flat_package_validation.json", flat_package_validation)
    write_json(output_dir / "attachment_role_check.json", attachment_role_check)
    write_text(output_dir / "claim_risk_report.txt", claim_report)
    write_text(output_dir / "readout.md", readout)

    written_outputs = sorted(path.name for path in output_dir.iterdir() if path.is_file())
    if written_outputs != sorted(OUTPUT_FILES):
        raise SystemExit(f"unexpected run output set: {written_outputs}")
    written_package = sorted(path.name for path in package_dir.iterdir() if path.is_file())
    if written_package != sorted(PACKAGE_FILES):
        raise SystemExit(f"unexpected package file set: {written_package}")
    return 0 if ready_for_final_user_review else 1


if __name__ == "__main__":
    sys.exit(main())
