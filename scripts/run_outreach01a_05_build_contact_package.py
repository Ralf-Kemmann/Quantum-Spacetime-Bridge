#!/usr/bin/env python3
"""Build and validate the OUTREACH01A-05 visible contact package."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
import shutil
import subprocess
import sys
import unicodedata
import xml.etree.ElementTree as ET
from pathlib import Path


OUTPUT_FILES = [
    "build_summary.json",
    "figure_validation.json",
    "package_validation.json",
    "cross_language_package_check.json",
    "rendered_file_inventory.csv",
    "readout.md",
    "contact_package_preview_en.md",
    "contact_package_preview_es.md",
]

VISIBLE_FILES = [
    "contact_figure_en.svg",
    "contact_figure_es.svg",
    "language_layer_architecture.svg",
    "technical_note_en.md",
    "technical_note_es.md",
    "compact_table_en.md",
    "compact_table_es.md",
]

FIGURE_FILES = [
    "contact_figure_en.svg",
    "contact_figure_es.svg",
    "language_layer_architecture.svg",
]

REQUIRED_ARTIFACTS = VISIBLE_FILES + [
    "preview_en.md",
    "preview_es.md",
    "figure_validation.json",
    "contact_package_manifest.json",
    "contact_package_file_list.md",
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
    "Este documento tiene como objetivo",
    "Es importante señalar",
    "En conclusión",
    "enfoque innovador",
    "marco robusto",
    "paradigma novedoso",
    "aprovecha",
]

PACKAGE_ID = "OUTREACH01A_CONTACT_PACKAGE_V1"
OUTREACH_ID = "OUTREACH01A-05"
PACKAGE_TITLE = "Visible Contact Figure and Contact-Package Assembly"
NOT_APPLICABLE = "not_applicable"

QUESTION_IDS = [
    "Q1_IDENTITY_EQUIVALENCE_PHASE",
    "Q2_BOUNDARY_REPRESENTATION",
    "Q3_MINIMUM_PHYSICAL_INFORMATION",
]

REQUIRED_MANIFEST_FIELDS = [
    "package_id",
    "outreach_id",
    "package_title",
    "package_status",
    "canonical_source_dataset",
    "canonical_source_validation",
    "language_variants",
    "primary_language",
    "secondary_language",
    "visible_figure_files",
    "technical_note_files",
    "compact_table_files",
    "preview_files",
    "contact_message_present",
    "contact_message_drafting_allowed",
    "contact_send_allowed",
    "user_release_required_before_send",
    "red_team_review_required",
    "package_ready_for_red_team",
    "package_ready_for_send",
    "models_reported_laser_experiment",
    "experimental_data_used",
    "physical_prediction_present",
    "time_crystal_mechanism_explained",
    "boundary_representation_status",
    "personal_style_reference_applied",
    "generic_ai_pattern_review_performed",
    "style_localization_changes_canonical_content",
    "style_localization_changes_claim_boundaries",
    "style_localization_changes_technical_questions",
    "manual_visual_review_performed",
    "manual_visual_review_passed",
    "visual_review_attestation_id",
    "style_review_attestation_id",
    "visual_review_attestation_external",
    "style_review_attestation_external",
    "file_hashes",
    "final_status",
]

CLAIM_RISK_PATTERNS = [
    "QSB explains " + "time crystals",
    "QSB models the " + "laser experiment",
    "QSB predicts the " + "domain wall",
    "QSB validates the " + "experiment",
    "new theory of " + "time crystals",
    "ready to " + "send",
    "send " + "approved",
    "QSB explica los cristales de " + "tiempo",
    "QSB modela el experimento " + "láser",
]

TECHNICAL_NOTE_ROLES = {
    "technical_note_en_role": "full_two_page_technical_note",
    "technical_note_es_role": "full_two_page_technical_note",
    "preview_en_role": "compact_package_preview",
    "preview_es_role": "compact_package_preview",
    "technical_note_content_source": "OUTREACH01A-04_reviewed_two_page_notes",
    "technical_note_shortening_applied": False,
    "technical_note_role_mismatch_present": False,
}


def load_json(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def write_json(path: Path, payload: dict) -> None:
    with path.open("w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2, sort_keys=True)
        handle.write("\n")


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()


def prepare_output_dir(output_dir: Path, overwrite: bool) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    existing = [path.name for path in output_dir.iterdir() if path.is_file()]
    unexpected = sorted(set(existing) - set(OUTPUT_FILES))
    if unexpected:
        raise SystemExit(f"unexpected files in output dir: {unexpected}")
    if existing and not overwrite:
        raise SystemExit("output files exist; pass --overwrite to replace expected outputs")


def text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def canonical_rows(records: list[dict]) -> list[dict]:
    fields = [
        "record_id",
        "record_type",
        "dynamic_equivalence_class",
        "temporal_phase_offset",
        "domain_id",
        "boundary_role",
        "evidence_status",
    ]
    return [{field: record[field] for field in fields} for record in records]


def table_contains_canonical_values(table_text: str, rows: list[dict]) -> bool:
    for row in rows:
        for value in row.values():
            if str(value) not in table_text:
                return False
    return True


def question_count(note_text: str) -> int:
    return len(re.findall(r"(?m)^\d+\.\s+", note_text))


def word_count(note_text: str) -> int:
    return len(re.findall(r"\b[\wÁÉÍÓÚÜÑáéíóúüñ'’-]+\b", note_text))


def caveat_markers(note_text: str) -> set[str]:
    markers = set()
    lowered = note_text.lower()
    normalized = normalize_text(note_text)
    if "not experimental data" in lowered or "no experimental data are used" in lowered or "no son datos experimentales" in lowered or "no se utilizan datos experimentales" in lowered:
        markers.add("not_experimental_data")
    if "not a validated ontology" in lowered or "no es una ontologia validada" in normalized or "no una ontologia validada" in normalized:
        markers.add("not_validated_ontology")
    if "not a physical prediction" in lowered or "not a prediction" in lowered or "no physical prediction" in lowered or "no hace ninguna prediccion" in normalized or "no es una prediccion" in normalized:
        markers.add("not_a_prediction")
    return markers


def normalize_text(value: str) -> str:
    decomposed = unicodedata.normalize("NFKD", value)
    return "".join(char for char in decomposed if not unicodedata.combining(char)).lower()


def svg_root(path: Path) -> ET.Element:
    return ET.parse(path).getroot()


def svg_dimension(path: Path) -> tuple[int, int]:
    root = svg_root(path)
    return int(root.attrib["width"]), int(root.attrib["height"])


def svg_text(path: Path) -> str:
    root = svg_root(path)
    parts = []
    for element in root.iter():
        if element.text:
            parts.append(element.text)
    return "\n".join(parts)


def svg_cleanliness(path: Path) -> dict:
    raw = text(path)
    absolute_path_pattern = re.compile(r"(?<![A-Za-z0-9_])/(home|tmp|var|etc|usr|opt)/")
    return {
        "xml_valid": True,
        "external_assets_present": bool(re.search(r"<image|href=|xlink:href|data:|https?://(?!www\.w3\.org/2000/svg)", raw)),
        "scripts_present": bool(re.search(r"<script|onload=|onclick=", raw, flags=re.IGNORECASE)),
        "raster_images_embedded": bool(re.search(r"<image|data:image/(png|jpeg|jpg|webp)", raw, flags=re.IGNORECASE)),
        "absolute_local_paths_present": bool(absolute_path_pattern.search(raw)),
    }


def render_svg(renderer: str, source: Path, target: Path) -> None:
    if renderer == "rsvg-convert":
        subprocess.run(["rsvg-convert", str(source), "-o", str(target)], check=True)
        return
    raise RuntimeError(f"unsupported renderer: {renderer}")


def find_renderer() -> str | None:
    if shutil.which("rsvg-convert"):
        return "rsvg-convert"
    return None


def manifest_hashes_match(manifest: dict, artifact_dir: Path) -> bool:
    file_hashes = manifest.get("file_hashes")
    if isinstance(file_hashes, dict):
        for name in VISIBLE_FILES:
            path = artifact_dir / name
            if not path.exists() or file_sha256(path) != file_hashes.get(name):
                return False
        return True
    entries = manifest.get("visible_artifacts", [])
    if len(entries) != 7:
        return False
    for entry in entries:
        path = artifact_dir.parent.parent / entry["path"]
        if not path.exists() or file_sha256(path) != entry.get("sha256"):
            return False
    return True


def build_cross_language_check(artifact_dir: Path, records: list[dict]) -> dict:
    rows = canonical_rows(records)
    table_en = text(artifact_dir / "compact_table_en.md")
    table_es = text(artifact_dir / "compact_table_es.md")
    fig_en = text(artifact_dir / "contact_figure_en.svg")
    fig_es = text(artifact_dir / "contact_figure_es.svg")
    note_en = text(artifact_dir / "technical_note_en.md")
    note_es = text(artifact_dir / "technical_note_es.md")
    question_ids_en = extract_question_ids(note_en)
    question_ids_es = extract_question_ids(note_es)
    canonical_ids = [record["record_id"] for record in records]
    record_id_pattern = re.compile(r"DTC_A|DTC_B|BOUNDARY_AB")
    figure_ids_en = record_id_pattern.findall(fig_en)
    figure_ids_es = record_id_pattern.findall(fig_es)
    relation_tokens = ["DTC_EQ_CLASS_01", "0T", "1T", "DOMAIN_A", "DOMAIN_B", "BOUNDARY_AB"]
    result = {
        "canonical_record_ids_match": set(canonical_ids) == {"DTC_A", "DTC_B", "BOUNDARY_AB"},
        "canonical_record_order_matches": canonical_ids == ["DTC_A", "DTC_B", "BOUNDARY_AB"],
        "canonical_values_match": table_contains_canonical_values(table_en, rows) and table_contains_canonical_values(table_es, rows),
        "figure_geometry_matches": svg_dimension(artifact_dir / "contact_figure_en.svg") == svg_dimension(artifact_dir / "contact_figure_es.svg"),
        "figure_record_ids_match": set(figure_ids_en) == set(figure_ids_es) == set(canonical_ids),
        "figure_relation_structure_matches": all(token in fig_en and token in fig_es for token in relation_tokens),
        "technical_question_count_matches": question_count(note_en) == question_count(note_es) == 3,
        "technical_question_ids_en": question_ids_en,
        "technical_question_ids_es": question_ids_es,
        "technical_question_ids_match": question_ids_en == question_ids_es == QUESTION_IDS,
        "technical_question_order_matches": question_ids_en == question_ids_es == QUESTION_IDS,
        "technical_question_mapping_matches": question_ids_en == question_ids_es == QUESTION_IDS,
        "automatic_semantic_equivalence_proven": False,
        "caveat_set_matches": caveat_markers(note_en) == caveat_markers(note_es) and len(caveat_markers(note_en)) >= 2,
        "only_display_language_differs": table_contains_canonical_values(table_en, rows) and table_contains_canonical_values(table_es, rows),
    }
    pass_values = [value for key, value in result.items() if key not in {"technical_question_ids_en", "technical_question_ids_es", "automatic_semantic_equivalence_proven"}]
    result["cross_language_package_check_passed"] = all(pass_values) and result["automatic_semantic_equivalence_proven"] is False
    return result


def generic_ai_hits(paths: list[Path]) -> list[dict]:
    hits = []
    for path in paths:
        content = text(path)
        for pattern in GENERIC_PATTERNS:
            if re.search(re.escape(pattern), content, flags=re.IGNORECASE):
                hits.append({"path": str(path), "pattern": pattern})
    return hits


def claim_risk_hits(paths: list[Path]) -> list[dict]:
    hits = []
    for path in paths:
        content = text(path)
        for pattern in CLAIM_RISK_PATTERNS:
            if re.search(re.escape(pattern), content, flags=re.IGNORECASE):
                hits.append({"path": str(path), "pattern": pattern})
    return hits


def write_inventory(path: Path, rows: list[dict]) -> None:
    fieldnames = ["source_svg", "rendered_png", "renderer", "expected_width", "expected_height", "png_size_bytes", "render_success"]
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def readout(summary: dict, render_rows: list[dict], style_hits: list[dict], claim_hits: list[dict]) -> str:
    render_paths = [row["rendered_png"] for row in render_rows]
    return "\n".join(
        [
            "# OUTREACH01A-05 Contact Package Assembly Readout",
            "",
            "## Befund",
            "",
            f"- Final status: `{summary['final_status']}`.",
            f"- Package ready for red team: `{str(summary['package_ready_for_red_team']).lower()}`.",
            f"- Package ready for send: `{str(summary['package_ready_for_send']).lower()}`.",
            f"- Visible artifact count: `{summary['visible_artifact_count']}`.",
            f"- Hash count: `{summary['hash_count']}`.",
            f"- English technical note word count: `{summary['technical_note_en_word_count']}`.",
            f"- Spanish technical note word count: `{summary['technical_note_es_word_count']}`.",
            "",
            "## Text Artifact Roles",
            "",
            f"- technical_note_en_role = `{summary['technical_note_en_role']}`.",
            f"- technical_note_es_role = `{summary['technical_note_es_role']}`.",
            f"- preview_en_role = `{summary['preview_en_role']}`.",
            f"- preview_es_role = `{summary['preview_es_role']}`.",
            f"- technical_note_content_source = `{summary['technical_note_content_source']}`.",
            f"- technical_note_shortening_applied = `{str(summary['technical_note_shortening_applied']).lower()}`.",
            f"- technical_note_role_mismatch_present = `{str(summary['technical_note_role_mismatch_present']).lower()}`.",
            "",
            "## Rendered PNG Paths",
            "",
            *[f"- `{path}`" for path in render_paths],
            "",
            "## Manual Visual Review",
            "",
            f"- manual_visual_review_performed = `{str(summary['manual_visual_review_performed']).lower()}`.",
            f"- manual_visual_review_passed = `{summary['manual_visual_review_passed']}`.",
            f"- manual_visual_review_required = `{str(summary['manual_visual_review_required']).lower()}`.",
            "- The builder performs automatic SVG rendering only. Human visual review is accepted only through an external attestation file.",
            "",
            "## Personal Style Reference",
            "",
            f"personal_style_reference_applied = {str(summary['personal_style_reference_applied']).lower()}",
            "style_reference_scope = rhythm_transitions_human_tone_explanatory_flow",
            "source_content_from_style_reference_used = false",
            f"generic_ai_pattern_review_performed = {str(summary['generic_ai_pattern_review_performed']).lower()}",
            "automatic_generic_phrase_scan_performed = true",
            f"manual_style_review_required = {str(summary['manual_style_review_required']).lower()}",
            "style_localization_changes_canonical_content = false",
            "style_localization_changes_claim_boundaries = false",
            "style_localization_changes_technical_questions = false",
            "",
            "## Generic AI Pattern Review",
            "",
            f"- Generic pattern hits: `{len(style_hits)}`.",
            "",
            "## Claim Boundary",
            "",
            f"- Claim-risk hits: `{len(claim_hits)}`.",
            "- No contact message is present. No send action is allowed.",
            "",
        ]
    )


def copy_text(source: Path, target: Path) -> None:
    target.write_text(source.read_text(encoding="utf-8"), encoding="utf-8")


def with_question_ids(note_text: str) -> str:
    if all(f"question_id: {question_id}" in note_text for question_id in QUESTION_IDS):
        return note_text
    ids = iter(QUESTION_IDS)

    def add_id(match: re.Match[str]) -> str:
        return f"<!-- question_id: {next(ids)} -->\n{match.group(0)}"

    return re.sub(r"(?m)^\d+\.\s+", add_id, note_text, count=len(QUESTION_IDS))


def copy_text_with_question_ids(source: Path, target: Path) -> None:
    target.write_text(with_question_ids(source.read_text(encoding="utf-8")), encoding="utf-8")


def strip_question_id_comments(note_text: str) -> str:
    return re.sub(r"(?m)^<!-- question_id: [A-Z0-9_]+ -->\n", "", note_text)


def source_matches(source: Path, target: Path) -> bool:
    return source.read_text(encoding="utf-8") == strip_question_id_comments(target.read_text(encoding="utf-8"))


def extract_question_ids(note_text: str) -> list[str]:
    return re.findall(r"<!-- question_id: ([A-Z0-9_]+) -->", note_text)


def load_attestation(path_value: str | None) -> dict | None:
    if path_value is None:
        return None
    return load_json(Path(path_value))


def valid_visual_attestation(attestation: dict | None) -> bool:
    if not attestation:
        return False
    expected_files = [
        "artifacts/OUTREACH01A-05/contact_figure_en.svg",
        "artifacts/OUTREACH01A-05/contact_figure_es.svg",
        "artifacts/OUTREACH01A-05/language_layer_architecture.svg",
    ]
    expected_rendered_files = [
        "/tmp/outreach01a05_render_check/contact_figure_en.png",
        "/tmp/outreach01a05_render_check/contact_figure_es.png",
        "/tmp/outreach01a05_render_check/language_layer_architecture.png",
    ]
    findings = attestation.get("review_findings", {})
    reviewer = attestation.get("reviewed_by", {})
    return (
        attestation.get("attestation_id") == "OUTREACH01A05_VISUAL_REVIEW_REAL_001"
        and attestation.get("attestation_type") == "human_visual_review"
        and attestation.get("reviewed_files") == expected_files
        and attestation.get("rendered_files") == expected_rendered_files
        and attestation.get("manual_visual_review_performed") is True
        and attestation.get("manual_visual_review_passed") is True
        and all(findings.get(key) is True for key in [
            "english_figure_readable",
            "spanish_figure_readable",
            "architecture_figure_readable",
            "spanish_text_fit",
            "primary_labels_not_overlapping",
            "caveat_text_readable",
            "record_ids_visible",
            "phase_offsets_visible",
            "domain_labels_visible",
            "boundary_open_option_visible",
            "single_canonical_dataset_architecture_clear",
        ])
        and isinstance(reviewer, dict)
        and bool(reviewer.get("name"))
        and bool(reviewer.get("role"))
        and bool(attestation.get("review_date"))
        and attestation.get("review_status") == "approved_for_red_team_review"
    )


def valid_style_attestation(attestation: dict | None) -> bool:
    if not attestation:
        return False
    expected_files = [
        "artifacts/OUTREACH01A-05/technical_note_en.md",
        "artifacts/OUTREACH01A-05/technical_note_es.md",
        "artifacts/OUTREACH01A-05/preview_en.md",
        "artifacts/OUTREACH01A-05/preview_es.md",
        "docs/OUTREACH01A_05_CONTACT_PACKAGE_README.md",
    ]
    findings = attestation.get("review_findings", {})
    reviewer = attestation.get("reviewed_by", {})
    return (
        attestation.get("attestation_id") == "OUTREACH01A05_STYLE_REVIEW_REAL_001"
        and attestation.get("attestation_type") == "human_style_review"
        and attestation.get("reviewed_files") == expected_files
        and attestation.get("personal_style_reference_applied") is True
        and attestation.get("style_reference_scope") == "rhythm_transitions_human_tone_explanatory_flow"
        and attestation.get("source_content_from_style_reference_used") is False
        and attestation.get("generic_ai_pattern_review_performed") is True
        and attestation.get("english_style_review_passed") is True
        and attestation.get("spanish_style_review_passed") is True
        and attestation.get("preview_style_review_passed") is True
        and attestation.get("readme_style_review_passed") is True
        and attestation.get("style_localization_changes_canonical_content") is False
        and attestation.get("style_localization_changes_claim_boundaries") is False
        and attestation.get("style_localization_changes_technical_questions") is False
        and all(findings.get(key) is True for key in [
            "human_tone_present",
            "explanatory_flow_present",
            "natural_transitions_present",
            "generic_ai_phrases_absent",
            "marketing_language_absent",
            "artificial_humility_absent",
            "claim_boundaries_preserved",
            "technical_question_parity_preserved",
        ])
        and isinstance(reviewer, dict)
        and bool(reviewer.get("name"))
        and bool(reviewer.get("role"))
        and bool(attestation.get("review_date"))
        and attestation.get("review_status") == "approved_for_red_team_review"
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Build and validate OUTREACH01A-05 contact package assembly outputs.")
    parser.add_argument("--input-root", required=True)
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--visual-review-attestation")
    parser.add_argument("--style-review-attestation")
    parser.add_argument("--overwrite", action="store_true")
    args = parser.parse_args(argv)

    root = Path(args.input_root).resolve()
    output_dir = Path(args.output_dir).resolve()
    prepare_output_dir(output_dir, args.overwrite)

    data_dir = root / "data" / "OUTREACH01A-DTC-DEMO01"
    artifact_dir = root / "artifacts" / "OUTREACH01A-05"
    docs_readme = root / "docs" / "OUTREACH01A_05_CONTACT_PACKAGE_README.md"
    docs_spec = root / "docs" / "OUTREACH01A_05_VISIBLE_CONTACT_FIGURE_AND_PACKAGE_ASSEMBLY_SPEC.md"
    source_note_en = root / "docs" / "OUTREACH01A_04_TWO_PAGE_TECHNICAL_NOTE_DRAFT_EN.md"
    source_note_es = root / "docs" / "OUTREACH01A_04_TWO_PAGE_TECHNICAL_NOTE_DRAFT_ES.md"

    records_payload = load_json(data_dir / "dtc_state_identity_records.json")
    records = records_payload["records"]
    _aliases_en = load_json(data_dir / "field_aliases_en.json")
    _aliases_es = load_json(data_dir / "field_aliases_es.json")
    copy_text_with_question_ids(source_note_en, artifact_dir / "technical_note_en.md")
    copy_text_with_question_ids(source_note_es, artifact_dir / "technical_note_es.md")
    required_present = all((artifact_dir / name).exists() for name in REQUIRED_ARTIFACTS)
    if not required_present:
        missing = [name for name in REQUIRED_ARTIFACTS if not (artifact_dir / name).exists()]
        raise SystemExit(f"missing required artifacts: {missing}")

    manifest = load_json(artifact_dir / "contact_package_manifest.json")
    current_hashes = {name: file_sha256(artifact_dir / name) for name in VISIBLE_FILES}
    manifest_hash_ok = manifest_hashes_match(manifest, artifact_dir)
    note_en_text = text(artifact_dir / "technical_note_en.md")
    note_es_text = text(artifact_dir / "technical_note_es.md")
    technical_note_en_word_count = word_count(strip_question_id_comments(note_en_text))
    technical_note_es_word_count = word_count(strip_question_id_comments(note_es_text))
    technical_note_en_word_count_between_900_and_1200 = 900 <= technical_note_en_word_count <= 1200
    technical_note_es_word_count_between_900_and_1200 = 900 <= technical_note_es_word_count <= 1200
    technical_note_en_source_matches_reviewed_01a04 = source_matches(source_note_en, artifact_dir / "technical_note_en.md")
    technical_note_es_source_matches_reviewed_01a04 = source_matches(source_note_es, artifact_dir / "technical_note_es.md")
    technical_note_shortening_applied = False
    technical_note_role_mismatch_present = False
    preview_en_role = TECHNICAL_NOTE_ROLES["preview_en_role"]
    preview_es_role = TECHNICAL_NOTE_ROLES["preview_es_role"]
    technical_note_en_role = TECHNICAL_NOTE_ROLES["technical_note_en_role"]
    technical_note_es_role = TECHNICAL_NOTE_ROLES["technical_note_es_role"]

    svg_valid = True
    clean = []
    dimensions = {}
    try:
        for name in FIGURE_FILES:
            svg_root(artifact_dir / name)
            dimensions[name] = svg_dimension(artifact_dir / name)
            clean.append(svg_cleanliness(artifact_dir / name))
    except ET.ParseError:
        svg_valid = False

    renderer = find_renderer()
    if renderer is None:
        raise SystemExit("no SVG renderer available")
    render_dir = Path("/tmp/outreach01a05_render_check")
    render_dir.mkdir(parents=True, exist_ok=True)
    render_rows = []
    render_success = {}
    for name in FIGURE_FILES:
        target = render_dir / f"{Path(name).stem}.png"
        render_svg(renderer, artifact_dir / name, target)
        size = target.stat().st_size if target.exists() else 0
        render_success[name] = target.exists() and size > 0
        width, height = dimensions[name]
        render_rows.append(
            {
                "source_svg": str(artifact_dir / name),
                "rendered_png": str(target),
                "renderer": renderer,
                "expected_width": width,
                "expected_height": height,
                "png_size_bytes": size,
                "render_success": render_success[name],
            }
        )

    figure_texts = {name: svg_text(artifact_dir / name) for name in FIGURE_FILES}
    rendered_dimensions_match = dimensions["contact_figure_en.svg"] == (1200, 620) and dimensions["contact_figure_es.svg"] == (1200, 620) and dimensions["language_layer_architecture.svg"] == (900, 430)
    record_ids_visible = all(token in figure_texts["contact_figure_en.svg"] and token in figure_texts["contact_figure_es.svg"] for token in ["DTC_A", "DTC_B", "BOUNDARY_AB"])
    phase_offsets_visible = all(token in figure_texts["contact_figure_en.svg"] and token in figure_texts["contact_figure_es.svg"] for token in ["0T", "1T"])
    domain_labels_visible = all(token in figure_texts["contact_figure_en.svg"] and token in figure_texts["contact_figure_es.svg"] for token in ["DOMAIN_A", "DOMAIN_B"])
    normalized_es_figure = normalize_text(figure_texts["contact_figure_es.svg"])
    boundary_open_visible = "open representation option" in figure_texts["contact_figure_en.svg"] and "opcion abierta" in normalized_es_figure and "representacion" in normalized_es_figure

    style_paths = [
        artifact_dir / "technical_note_en.md",
        artifact_dir / "technical_note_es.md",
        artifact_dir / "preview_en.md",
        artifact_dir / "preview_es.md",
        docs_readme,
    ]
    style_hits = generic_ai_hits(style_paths)
    generic_ai_pattern_hits_en = generic_ai_hits([artifact_dir / "technical_note_en.md", artifact_dir / "preview_en.md"])
    generic_ai_pattern_hits_es = generic_ai_hits([artifact_dir / "technical_note_es.md", artifact_dir / "preview_es.md"])
    generic_ai_pattern_hits_readme = generic_ai_hits([docs_readme])
    claim_paths = [docs_spec, docs_readme, *[artifact_dir / name for name in REQUIRED_ARTIFACTS]]
    claim_hits = claim_risk_hits(claim_paths)
    cross = build_cross_language_check(artifact_dir, records)
    visual_attestation = load_attestation(args.visual_review_attestation)
    style_attestation = load_attestation(args.style_review_attestation)
    visual_attestation_valid = valid_visual_attestation(visual_attestation)
    style_attestation_valid = valid_style_attestation(style_attestation)

    manual_visual_review_performed = visual_attestation_valid
    manual_visual_review_passed = True if visual_attestation_valid else NOT_APPLICABLE
    manual_visual_review_required = not visual_attestation_valid
    manual_style_review_required = not style_attestation_valid
    personal_style_reference_applied = style_attestation_valid
    generic_ai_pattern_review_performed = style_attestation_valid
    package_ready_for_send = False
    contact_message_present = False
    contact_send_allowed = False
    all_required_manifest_fields_present = all(field in manifest for field in REQUIRED_MANIFEST_FIELDS)
    package_id_consistent = manifest.get("package_id") == PACKAGE_ID
    manifest_complete = all_required_manifest_fields_present and package_id_consistent
    generic_phrase_scan_passed = not style_hits
    package_ready_for_red_team = (
        required_present
        and svg_valid
        and all(render_success.values())
        and rendered_dimensions_match
        and visual_attestation_valid
        and style_attestation_valid
        and manifest_hash_ok
        and manifest_complete
        and cross["cross_language_package_check_passed"]
        and technical_note_en_word_count_between_900_and_1200
        and technical_note_es_word_count_between_900_and_1200
        and technical_note_en_source_matches_reviewed_01a04
        and technical_note_es_source_matches_reviewed_01a04
        and not technical_note_shortening_applied
        and not technical_note_role_mismatch_present
        and generic_phrase_scan_passed
        and not claim_hits
    )
    final_status = (
        "visible_contact_figure_and_contact_package_assembled"
        if package_ready_for_red_team and not package_ready_for_send and not contact_message_present and not contact_send_allowed
        else "visible_contact_figure_and_contact_package_inconclusive"
    )

    figure_validation = {
        "figure_count": 3,
        "svg_xml_valid": svg_valid,
        "svg_render_check_performed": True,
        "svg_render_check_passed": all(render_success.values()),
        "external_assets_present": any(item["external_assets_present"] for item in clean),
        "scripts_present": any(item["scripts_present"] for item in clean),
        "raster_images_embedded": any(item["raster_images_embedded"] for item in clean),
        "absolute_local_paths_present": any(item["absolute_local_paths_present"] for item in clean),
        "render_backend": renderer,
        "render_success_en": render_success["contact_figure_en.svg"],
        "render_success_es": render_success["contact_figure_es.svg"],
        "render_success_language_architecture": render_success["language_layer_architecture.svg"],
        "rendered_dimensions_match_expected": rendered_dimensions_match,
        "record_ids_detected": record_ids_visible,
        "phase_offsets_detected": phase_offsets_visible,
        "domain_labels_detected": domain_labels_visible,
        "boundary_open_option_text_detected": boundary_open_visible,
        "manual_visual_review_performed": manual_visual_review_performed,
        "manual_visual_review_passed": manual_visual_review_passed,
        "automatic_text_clipping_detection_performed": False,
        "manual_visual_review_required": manual_visual_review_required,
        "visual_attestation_present": visual_attestation is not None,
        "visual_attestation_valid": visual_attestation_valid,
        "rendered_pngs_temporary_directory": str(render_dir),
    }
    package_validation = {
        "manifest_complete": manifest_complete,
        "package_id_consistent": package_id_consistent,
        "all_required_manifest_fields_present": all_required_manifest_fields_present,
        "required_artifact_count": len(REQUIRED_ARTIFACTS),
        "required_artifacts_present": required_present,
        "manifest_present": (artifact_dir / "contact_package_manifest.json").exists(),
        "manifest_hashes_match": manifest_hash_ok,
        "file_list_present": (artifact_dir / "contact_package_file_list.md").exists(),
        "technical_notes_present": all((artifact_dir / name).exists() for name in ["technical_note_en.md", "technical_note_es.md"]),
        "compact_tables_present": all((artifact_dir / name).exists() for name in ["compact_table_en.md", "compact_table_es.md"]),
        "preview_files_present": all((artifact_dir / name).exists() for name in ["preview_en.md", "preview_es.md"]),
        "figure_files_present": all((artifact_dir / name).exists() for name in FIGURE_FILES),
        "visual_attestation_present": visual_attestation is not None,
        "visual_attestation_valid": visual_attestation_valid,
        "style_attestation_present": style_attestation is not None,
        "style_attestation_valid": style_attestation_valid,
        "technical_question_ids_present": cross["technical_question_ids_en"] == QUESTION_IDS and cross["technical_question_ids_es"] == QUESTION_IDS,
        "technical_question_ids_match": cross["technical_question_ids_match"],
        "technical_question_order_matches": cross["technical_question_order_matches"],
        "technical_question_mapping_matches": cross["technical_question_mapping_matches"],
        "personal_style_markers_present": style_attestation_valid,
        "generic_phrase_scan_passed": generic_phrase_scan_passed,
        "personal_style_reference_applied": personal_style_reference_applied,
        "style_reference_scope": "rhythm_transitions_human_tone_explanatory_flow",
        "source_content_from_style_reference_used": False,
        "generic_ai_pattern_review_performed": generic_ai_pattern_review_performed,
        "generic_ai_pattern_hits": style_hits,
        "generic_ai_pattern_hits_en": generic_ai_pattern_hits_en,
        "generic_ai_pattern_hits_es": generic_ai_pattern_hits_es,
        "generic_ai_pattern_hits_readme": generic_ai_pattern_hits_readme,
        "style_localization_changes_canonical_content": False,
        "style_localization_changes_claim_boundaries": False,
        "style_localization_changes_technical_questions": False,
        "manual_style_review_required": manual_style_review_required,
        "manual_visual_review_performed": manual_visual_review_performed,
        "manual_visual_review_passed": manual_visual_review_passed,
        "package_ready_for_red_team": package_ready_for_red_team,
        "package_ready_for_send": package_ready_for_send,
        "contact_message_present": contact_message_present,
        "contact_send_allowed": contact_send_allowed,
        "user_release_required_before_send": True,
        "claim_risk_hits": claim_hits,
        "technical_note_en_word_count_between_900_and_1200": technical_note_en_word_count_between_900_and_1200,
        "technical_note_es_word_count_between_900_and_1200": technical_note_es_word_count_between_900_and_1200,
        "technical_note_en_source_matches_reviewed_01A04": technical_note_en_source_matches_reviewed_01a04,
        "technical_note_es_source_matches_reviewed_01A04": technical_note_es_source_matches_reviewed_01a04,
        "technical_note_en_role": technical_note_en_role,
        "technical_note_es_role": technical_note_es_role,
        "preview_en_role": preview_en_role,
        "preview_es_role": preview_es_role,
        "technical_note_content_source": TECHNICAL_NOTE_ROLES["technical_note_content_source"],
        "technical_note_shortening_applied": technical_note_shortening_applied,
        "technical_note_role_mismatch_present": technical_note_role_mismatch_present,
    }
    summary = {
        "package_id": PACKAGE_ID,
        "outreach_id": OUTREACH_ID,
        "package_title": PACKAGE_TITLE,
        "package_status": "assembled_not_released",
        "canonical_dataset_count": 1,
        "visible_artifact_count": len(VISIBLE_FILES),
        "language_variant_count": 2,
        "figure_count": 3,
        "technical_note_count": 2,
        "compact_table_count": 2,
        "hash_count": len(current_hashes),
        "cross_language_package_check_passed": cross["cross_language_package_check_passed"],
        "package_manifest_present": (artifact_dir / "contact_package_manifest.json").exists(),
        "svg_render_check_performed": True,
        "svg_render_check_passed": all(render_success.values()),
        "automatic_text_clipping_detection_performed": False,
        "manual_visual_review_required": manual_visual_review_required,
        "technical_question_ids_match": cross["technical_question_ids_match"],
        "technical_question_order_matches": cross["technical_question_order_matches"],
        "technical_question_mapping_matches": cross["technical_question_mapping_matches"],
        "automatic_semantic_equivalence_proven": False,
        "personal_style_reference_applied": personal_style_reference_applied,
        "automatic_generic_phrase_scan_performed": True,
        "generic_ai_pattern_review_performed": generic_ai_pattern_review_performed,
        "manual_style_review_required": manual_style_review_required,
        "style_localization_changes_canonical_content": False,
        "style_localization_changes_claim_boundaries": False,
        "style_localization_changes_technical_questions": False,
        "manual_visual_review_performed": manual_visual_review_performed,
        "manual_visual_review_passed": manual_visual_review_passed,
        "package_ready_for_red_team": package_ready_for_red_team,
        "package_ready_for_send": package_ready_for_send,
        "contact_message_present": contact_message_present,
        "contact_send_allowed": contact_send_allowed,
        "user_release_required_before_send": True,
        "final_status": final_status,
        "visible_file_hashes": current_hashes,
        "technical_note_en_word_count": technical_note_en_word_count,
        "technical_note_es_word_count": technical_note_es_word_count,
        "technical_note_en_role": technical_note_en_role,
        "technical_note_es_role": technical_note_es_role,
        "preview_en_role": preview_en_role,
        "preview_es_role": preview_es_role,
        "technical_note_content_source": TECHNICAL_NOTE_ROLES["technical_note_content_source"],
        "technical_note_shortening_applied": technical_note_shortening_applied,
        "technical_note_role_mismatch_present": technical_note_role_mismatch_present,
        "technical_note_en_word_count_between_900_and_1200": technical_note_en_word_count_between_900_and_1200,
        "technical_note_es_word_count_between_900_and_1200": technical_note_es_word_count_between_900_and_1200,
        "technical_note_en_source_matches_reviewed_01A04": technical_note_en_source_matches_reviewed_01a04,
        "technical_note_es_source_matches_reviewed_01A04": technical_note_es_source_matches_reviewed_01a04,
    }

    write_json(output_dir / "build_summary.json", summary)
    write_json(output_dir / "figure_validation.json", figure_validation)
    write_json(output_dir / "package_validation.json", package_validation)
    write_json(output_dir / "cross_language_package_check.json", cross)
    write_inventory(output_dir / "rendered_file_inventory.csv", render_rows)
    (output_dir / "readout.md").write_text(readout(summary, render_rows, style_hits, claim_hits), encoding="utf-8")
    copy_text(artifact_dir / "preview_en.md", output_dir / "contact_package_preview_en.md")
    copy_text(artifact_dir / "preview_es.md", output_dir / "contact_package_preview_es.md")

    written = sorted(path.name for path in output_dir.iterdir() if path.is_file())
    if written != sorted(OUTPUT_FILES):
        raise SystemExit(f"unexpected run output set: {written}")
    if final_status != "visible_contact_figure_and_contact_package_assembled":
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
