#!/usr/bin/env python3
"""Build the read-only QSB-INVENTORY01 legacy-to-INTERFACE01 alignment map."""

from __future__ import annotations

import csv
import hashlib
import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path


REPO = Path(__file__).resolve().parents[2]
OUTPUT = REPO / "runs/QSB-INVENTORY01/legacy_to_interface_alignment_map"
CLAIM = "Inventory and alignment only; not a proof of emergent spacetime or gravitation."

PHASE_D = REPO / "runs/QSB-D0X/phase_d_local_threshold_motif_summary"
MATERIAL = REPO / "runs/QSB-MATERIAL01/typb_materialsensitive_signature_mart_intake"

SOURCE_PATHS = [
    REPO / "docs/QSB_DEBROGLIE_RELATIVITY_BRIDGE_ANCHOR_NOTE_2026-05-17.md",
    REPO / "docs/QSB_DEBROGLIE_EXKURS_CHAT_TRANSCRIPT_2026-05-17.md",
    REPO / "docs/_archive/quantum_spacetime_bridge_core_texts_v1.md",
    PHASE_D / "04_d0x_motif_chain_summary.csv",
    PHASE_D / "06_d0x_threshold_motif_catalog.csv",
    PHASE_D / "09_d0x_claim_boundary_note.md",
    PHASE_D / "10_d0x_units_dimensions_register.csv",
    PHASE_D / "11_d0x_final_assessment.md",
    PHASE_D / "12_d0x_run_manifest.json",
    MATERIAL / "csv/03_dim_material_system.csv",
    MATERIAL / "csv/04_fact_debroglie_material_signature.csv",
    MATERIAL / "csv/05_fact_isotope_shift.csv",
    MATERIAL / "csv/06_result_material_sensitivity_anchor.csv",
    MATERIAL / "csv/07_material01_review_items.csv",
    MATERIAL / "reports/MATERIAL01_FINAL_ASSESSMENT.md",
    MATERIAL / "reports/MATERIAL01_RUN_MANIFEST.json",
    MATERIAL / "material01_typb_signature_mart.sqlite",
    REPO / "runs/QSB-GAP01/legacy_lineage_cross_mart_mapping/01_legacy_source_inventory.csv",
    REPO / "runs/QSB-GAP01/legacy_lineage_cross_mart_mapping/02_legacy_source_classification.csv",
    REPO / "runs/QSB-GAP01/legacy_lineage_cross_mart_mapping/08_gap01_final_assessment.md",
    REPO / "runs/QSB-GAP01C/additional_legacy_intake/01_gap01c_additional_source_inventory.csv",
    REPO / "runs/QSB-GAP02A/source_hub_schema_dry_run_loader/qsb_source_hub_dry_run.sqlite",
    REPO / "runs/QSB-GAP02C/source_hub_schema_hardening/qsb_source_hub_hardened_dry_run.sqlite",
    REPO / "runs/QSB-GAP02C/source_hub_schema_hardening/09_gap02c_final_assessment.md",
    REPO / "runs/QSB-META01-01/repository_metadata_inventory/readout.md",
    REPO / "runs/QSB-META01-02/canonical_metadata_contract/readout.md",
    REPO / "runs/QSB-META01-03/causality07_pilot_metadata/qsb_metadata_catalog.sqlite",
    REPO / "runs/QSB-META01-03/causality07_pilot_metadata/readout.md",
]

DB_PURPOSES = {
    "material01_typb_signature_mart.sqlite": "Material systems, de-Broglie signatures, isotope shifts, and three result anchors.",
    "qsb_source_hub_dry_run.sqlite": "Legacy source-object, file, archive, candidate-mart, and claim-boundary staging.",
    "qsb_source_hub_hardened_dry_run.sqlite": "Hardened metadata-only Source-Hub staging with normalized keys and review flags.",
    "qsb_metadata_catalog.sqlite": "Canonical metadata, field, unit, lineage, validation, result, and claim-link pilot catalog.",
}


def rel(path: Path) -> str:
    try:
        return path.relative_to(REPO).as_posix()
    except ValueError:
        return str(path)


def write_csv(name: str, fields: list[str], rows: list[dict[str, object]]) -> None:
    with (OUTPUT / name).open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def kind(path: Path) -> str:
    if path.is_dir():
        return "directory"
    return {
        ".sqlite": "sqlite_db", ".db": "sqlite_db", ".csv": "csv",
        ".json": "json", ".md": "md", ".pdf": "pdf_pointer", ".zip": "zip_pointer",
    }.get(path.suffix.lower(), "unknown")


def block(path: Path) -> str:
    text = rel(path).lower()
    if "qsb-d0" in text:
        return "Phase-D"
    if "material01" in text:
        return "MATERIAL01"
    if "gap0" in text:
        return "GAP"
    if "meta0" in text:
        return "META"
    if "debroglie" in text or "core_text" in text:
        return "legacy_debroglie"
    return "unknown"


def inventory_sources() -> list[dict[str, object]]:
    rows = []
    for number, path in enumerate(SOURCE_PATHS, 1):
        exists = path.exists()
        stat = path.stat() if exists else None
        rows.append({
            "source_id": f"SRC-{number:03d}", "source_path": rel(path),
            "source_kind": kind(path) if exists else kind(path), "detected_block": block(path),
            "sha256_or_na": sha256(path) if exists and path.is_file() else "na",
            "file_size_bytes_or_na": stat.st_size if stat and path.is_file() else "na",
            "modified_time_or_na": datetime.fromtimestamp(stat.st_mtime, timezone.utc).isoformat() if stat else "na",
            "read_status": "read_ok" if exists else "missing",
            "review_note": "Curated internal anchor; indexed read-only." if exists else "Expected internal anchor missing; human review required.",
        })
    return rows


def db_assets() -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    db_paths = [path for path in SOURCE_PATHS if path.suffix.lower() in {".sqlite", ".db"}]
    asset_number = 1
    for path in db_paths:
        if not path.exists():
            rows.append({"asset_id": f"ASSET-{asset_number:03d}", "asset_path": rel(path),
                         "asset_type": "sqlite_db", "db_table_or_view": "na", "purpose": DB_PURPOSES.get(path.name, "Review."),
                         "usable_for_interface01": "no", "why_usable": "Database is missing.", "limitations": "No inspection possible.",
                         "read_status": "missing", "review_note": "Resolve path."})
            asset_number += 1
            continue
        uri = f"file:{path.resolve()}?mode=ro"
        try:
            connection = sqlite3.connect(uri, uri=True)
            objects = connection.execute(
                "SELECT type, name FROM sqlite_master WHERE type IN ('table','view') "
                "AND name NOT LIKE 'sqlite_%' ORDER BY type, name"
            ).fetchall()
            for object_type, name in objects:
                count = connection.execute(f'SELECT COUNT(*) FROM "{name}"').fetchone()[0]
                columns = [row[1] for row in connection.execute(f'PRAGMA table_info("{name}")')]
                lineage = [c for c in columns if any(token in c.lower() for token in ("source", "lineage", "claim", "unit", "status", "review"))]
                usable = "yes" if path.name == "material01_typb_signature_mart.sqlite" else "partial"
                rows.append({
                    "asset_id": f"ASSET-{asset_number:03d}", "asset_path": rel(path), "asset_type": object_type,
                    "db_table_or_view": name, "purpose": DB_PURPOSES.get(path.name, "Internal metadata asset."),
                    "usable_for_interface01": usable,
                    "why_usable": f"Read-only schema inspection: {count} rows; relevant fields: {', '.join(lineage[:8]) or 'none detected'}.",
                    "limitations": "Internal staging/catalog context; table presence and counts do not establish scientific validity.",
                    "read_status": "read_ok", "review_note": f"Columns inspected: {len(columns)}; opened with SQLite mode=ro.",
                })
                asset_number += 1
            connection.close()
        except sqlite3.Error as error:
            rows.append({"asset_id": f"ASSET-{asset_number:03d}", "asset_path": rel(path), "asset_type": "sqlite_db",
                         "db_table_or_view": "na", "purpose": DB_PURPOSES.get(path.name, "Review."),
                         "usable_for_interface01": "review", "why_usable": "Inspection failed.", "limitations": str(error),
                         "read_status": "failed", "review_note": "SQLite read-only inspection requires review."})
            asset_number += 1
    return rows


def main() -> None:
    if OUTPUT.exists():
        raise SystemExit(f"Refusing to overwrite existing output directory: {rel(OUTPUT)}")
    OUTPUT.mkdir(parents=True)

    sources = inventory_sources()
    write_csv("01_inventory_input_sources.csv", ["source_id", "source_path", "source_kind", "detected_block", "sha256_or_na", "file_size_bytes_or_na", "modified_time_or_na", "read_status", "review_note"], sources)

    clusters = [
        {"cluster_id":"CL-01","cluster_label":"de-Broglie phase/interference core","german_label":"de-Broglie-Phasen-/Interferenzkern","description":"Legacy texts and GAP classification retain phase, interference, correlation, and bridge terminology.","representative_sources":"docs/QSB_DEBROGLIE_RELATIVITY_BRIDGE_ANCHOR_NOTE_2026-05-17.md; runs/QSB-GAP01/legacy_lineage_cross_mart_mapping/02_legacy_source_classification.csv","relation_to_qsb_core":"deBroglie","confidence":"medium","review_note":"Mechanism statements remain hypotheses and require source-level review."},
        {"cluster_id":"CL-02","cluster_label":"materialsensitive Typ-B tests","german_label":"materialsensitive Typ-B-Tests","description":"Existing Typ-B outputs cover atomic and isotope-sensitive signature records.","representative_sources":"runs/QSB-MATERIAL01/typb_materialsensitive_signature_mart_intake/csv/04_fact_debroglie_material_signature.csv","relation_to_qsb_core":"material_sensitivity","confidence":"high","review_note":"Use only with recorded mixed unit status."},
        {"cluster_id":"CL-03","cluster_label":"emergent relational geometry / Gram-first / FoP","german_label":"emergente relationale Geometrie / Gram-first / FoP","description":"GAP lineage identifies Gram-to-graph and relational-geometry strands in legacy sources.","representative_sources":"runs/QSB-GAP01/legacy_lineage_cross_mart_mapping/02_legacy_source_classification.csv; runs/QSB-GAP01C/additional_legacy_intake/01_gap01c_additional_source_inventory.csv","relation_to_qsb_core":"relational_geometry","confidence":"medium","review_note":"Lineage recognition is not formal or physical validation; FoP source was previously missing in GAP01."},
        {"cluster_id":"CL-04","cluster_label":"Phase-D threshold motif line","german_label":"Phase-D-Schwellenmotivlinie","description":"Consolidated local toy-model chain from force break edges to local theta crossings.","representative_sources":"runs/QSB-D0X/phase_d_local_threshold_motif_summary/11_d0x_final_assessment.md","relation_to_qsb_core":"relational_geometry","confidence":"high","review_note":"Model- and threshold-bound; no SI conversion."},
        {"cluster_id":"CL-05","cluster_label":"MATERIAL01 material signature mart","german_label":"MATERIAL01-Materialsignatur-Mart","description":"Read-only mart with material systems, signature facts, isotope shifts, and result anchors.","representative_sources":"runs/QSB-MATERIAL01/typb_materialsensitive_signature_mart_intake/material01_typb_signature_mart.sqlite","relation_to_qsb_core":"material_sensitivity","confidence":"high","review_note":"Review flags and atomic-mass-unit status remain active."},
        {"cluster_id":"CL-06","cluster_label":"Source-Hub / GAP lineage","german_label":"Source-Hub-/GAP-Lineage","description":"Legacy provenance, claim-risk, and candidate-mart staging without evidence promotion.","representative_sources":"runs/QSB-GAP02C/source_hub_schema_hardening/qsb_source_hub_hardened_dry_run.sqlite","relation_to_qsb_core":"metadata","confidence":"high","review_note":"Metadata-only staging; source relationships remain unpopulated."},
        {"cluster_id":"CL-07","cluster_label":"Metadata catalog / DWH support","german_label":"Metadatenkatalog-/DWH-Unterstuetzung","description":"Canonical object, field, unit, lineage, validation, result, and claim-link structures.","representative_sources":"runs/QSB-META01-03/causality07_pilot_metadata/qsb_metadata_catalog.sqlite","relation_to_qsb_core":"metadata","confidence":"high","review_note":"Pilot scope is CAUSALITY07; transfer to INTERFACE01 needs explicit mapping."},
    ]
    write_csv("02_legacy_work_cluster_map.csv", ["cluster_id","cluster_label","german_label","description","representative_sources","relation_to_qsb_core","confidence","review_note"], clusters)

    anchors = [
        {"anchor_id":"ANCH-01","anchor_label":"Phase-D threshold/edge/neighborhood motifs","anchor_class":"phase_d_threshold_motif","source_path":"runs/QSB-D0X/phase_d_local_threshold_motif_summary/11_d0x_final_assessment.md","key_finding":"Internal toy-model chain: force break edge -> nested local windows -> edge flips -> neighborhood signature -> analytic threshold distance -> local theta crossing.","unit_status":"model_units / dimensionless toy-model units; not_SI_converted","claim_boundary":"Model- and threshold-bound local motif summary; no external physical validation.","interface_relevance":"Candidate structural vocabulary for thresholds, edges, and neighborhoods.","evidence_status":"supported","requires_human_review":"yes","review_note":"Formal bridge to de-Broglie phase/correlation is absent."},
        {"anchor_id":"ANCH-02","anchor_label":"MATERIAL01 materialsensitive de-Broglie signature shifts","anchor_class":"material_signature_shift","source_path":"runs/QSB-MATERIAL01/typb_materialsensitive_signature_mart_intake/csv/06_result_material_sensitivity_anchor.csv","key_finding":"Three internal result anchors summarize atomic material signatures and isotope mass-order versus wave-order shifts.","unit_status":"mixed_review; lambda_db=m; energy=J; scores=dimensionless; mass_u=atomic_mass_unit_review","claim_boundary":"Working-model evidence anchor; not evidence of emergent spacetime or gravitation.","interface_relevance":"Material-sensitive candidate input for an interface mechanism hypothesis.","evidence_status":"supported","requires_human_review":"yes","review_note":"Carry all unit and derived-shift review flags."},
        {"anchor_id":"ANCH-03","anchor_label":"Legacy phase/interference/correlation to relational geometry strand","anchor_class":"manuscript_mechanism","source_path":"runs/QSB-GAP01/legacy_lineage_cross_mart_mapping/02_legacy_source_classification.csv","key_finding":"Lexical/provenance inventory recognizes de-Broglie, phase, interference, correlation, and Gram-to-graph strands.","unit_status":"not_applicable_lineage_inventory","claim_boundary":"Lineage context only; no certified equivalence, derivation, or physical mechanism.","interface_relevance":"Supplies hypotheses and terminology to test, not established inputs.","evidence_status":"partial_review","requires_human_review":"yes","review_note":"Direct manuscript/FoP source review remains necessary."},
        {"anchor_id":"ANCH-04","anchor_label":"Source-Hub and metadata lineage support","anchor_class":"metadata_lineage","source_path":"runs/QSB-GAP02C/source_hub_schema_hardening/qsb_source_hub_hardened_dry_run.sqlite","key_finding":"Internal metadata structures retain source, claim-boundary, candidate-mart, field, unit, lineage, and validation context.","unit_status":"metadata_only","claim_boundary":"Metadata availability does not establish scientific validity.","interface_relevance":"Supports auditable source selection and future INTERFACE01 lineage.","evidence_status":"supported","requires_human_review":"yes","review_note":"No automatic promotion of legacy records into evidence."},
    ]
    write_csv("03_current_evidence_anchor_map.csv", ["anchor_id","anchor_label","anchor_class","source_path","key_finding","unit_status","claim_boundary","interface_relevance","evidence_status","requires_human_review","review_note"], anchors)

    assets = db_assets()
    write_csv("04_dwh_metadata_usable_assets.csv", ["asset_id","asset_path","asset_type","db_table_or_view","purpose","usable_for_interface01","why_usable","limitations","read_status","review_note"], assets)

    gaps = [
        {"gap_id":"GAP-01","gap_label":"Missing formal phase-to-threshold bridge","from_legacy_anchor":"ANCH-03","to_interface_need":"Explicit map from phase/interference/correlation variables to thresholds, edges, and neighborhoods.","gap_type":"missing_formal_link","gap_description":"Legacy mechanism language and Phase-D motifs coexist but are not connected by a validated formal transformation.","severity":"high","recommended_action":"Define a minimal equation/variable map and falsifiable acceptance checks before a new physics run.","do_before_interface01":"yes","review_note":"Do not infer this link from lexical overlap."},
        {"gap_id":"GAP-02","gap_label":"Model-unit versus SI separation","from_legacy_anchor":"ANCH-01; ANCH-02","to_interface_need":"Unit-safe interface variables.","gap_type":"unit_status_gap","gap_description":"Phase-D model units cannot be numerically mixed with MATERIAL01 SI and atomic-mass-unit fields.","severity":"high","recommended_action":"Create an explicit dimensional contract; keep separate channels until a justified mapping exists.","do_before_interface01":"yes","review_note":"No conversion factor is established here."},
        {"gap_id":"GAP-03","gap_label":"Interface-layer physical reading","from_legacy_anchor":"ANCH-02","to_interface_need":"Conservative interpretation of what material-sensitive signatures can condition in the interface layer.","gap_type":"claim_boundary_gap","gap_description":"MATERIAL01 establishes internal signature anchors, not an emergence or gravity mechanism.","severity":"high","recommended_action":"State candidate causal roles as hypotheses and define disconfirming outcomes.","do_before_interface01":"yes","review_note":"Retain MATERIAL01 review flags."},
        {"gap_id":"GAP-04","gap_label":"Terminology contract","from_legacy_anchor":"ANCH-03","to_interface_need":"Stable definitions for correlation field, structure field, interface layer, threshold, and geometry.","gap_type":"terminology_gap","gap_description":"Near-synonyms currently risk hiding distinct mathematical objects and claim levels.","severity":"medium","recommended_action":"Create a short term-to-object-to-unit-to-claim table in INTERFACE01.","do_before_interface01":"yes","review_note":"Definitions should precede narrative synthesis."},
        {"gap_id":"GAP-05","gap_label":"Legacy source-level verification","from_legacy_anchor":"ANCH-03","to_interface_need":"Directly reviewed manuscript/FoP/visual bridge sources.","gap_type":"lineage_gap","gap_description":"Current support is partly lexical/provenance-oriented; direct source review is incomplete and poster evidence was not found as a repo anchor.","severity":"medium","recommended_action":"Resolve and review the authoritative legacy manuscript and visual source without promoting review material to evidence.","do_before_interface01":"yes","review_note":"GAP01 reported missing named sources."},
        {"gap_id":"GAP-06","gap_label":"External parallel-work context","from_legacy_anchor":"internal anchors only","to_interface_need":"Context against established relational, correlation, graph/kernel, and semiclassical approaches.","gap_type":"external_context_gap","gap_description":"No targeted external literature comparison was performed in INVENTORY01.","severity":"medium","recommended_action":"Run guided Deep Research only after the internal variable and claim-boundary map is fixed.","do_before_interface01":"optional","review_note":"No external confirmation is asserted."},
        {"gap_id":"GAP-07","gap_label":"INTERFACE01 metadata mapping","from_legacy_anchor":"ANCH-04","to_interface_need":"Object/field/unit/lineage registration for selected INTERFACE01 inputs.","gap_type":"data_access_gap","gap_description":"Existing metadata pilot targets CAUSALITY07, not the proposed INTERFACE01 objects.","severity":"low","recommended_action":"Reuse the contract selectively after the physics input set is decided.","do_before_interface01":"no","review_note":"Do not design a new DWH architecture for this gap."},
    ]
    write_csv("05_legacy_to_interface_gap_map.csv", ["gap_id","gap_label","from_legacy_anchor","to_interface_need","gap_type","gap_description","severity","recommended_action","do_before_interface01","review_note"], gaps)

    candidates = [
        {"candidate_id":"IN-01","input_label":"Phase-D local threshold motif chain","source_anchor":"ANCH-01","why_needed":"Provides the current internal threshold/edge/neighborhood vocabulary.","interface_question_answered":"What relational motif family could an interface mechanism be required to produce?","priority":"P0","claim_boundary":"Toy-model target pattern only.","unit_status":"model_units; not_SI_converted","recommended_use":"core_input","review_note":"Use structurally, not as SI material data."},
        {"candidate_id":"IN-02","input_label":"MATERIAL01 result material sensitivity anchors","source_anchor":"ANCH-02","why_needed":"Provides concrete internal material and isotope sensitivity records.","interface_question_answered":"Which material-sensitive phase/wave/signature variations require a candidate interface interpretation?","priority":"P0","claim_boundary":"No emergence or gravity inference.","unit_status":"mixed_review","recommended_use":"core_input","review_note":"Use three result anchors first; retain review flags."},
        {"candidate_id":"IN-03","input_label":"Minimal phase/interference/correlation hypothesis chain","source_anchor":"ANCH-03","why_needed":"Supplies the mechanism question that INTERFACE01 must formalize or reject.","interface_question_answered":"How might phase/interference variables relate to correlation structure?","priority":"P0","claim_boundary":"Hypothesis requiring formalization and tests.","unit_status":"not_yet_formalized","recommended_use":"review_only","review_note":"Direct manuscript review required before equation reuse."},
        {"candidate_id":"IN-04","input_label":"Source-Hub claim-boundary and provenance records","source_anchor":"ANCH-04","why_needed":"Preserves lineage and prevents accidental evidence promotion.","interface_question_answered":"Which source and claim restrictions accompany each candidate input?","priority":"P1","claim_boundary":"Metadata support only.","unit_status":"metadata_only","recommended_use":"supporting_context","review_note":"Read-only use."},
        {"candidate_id":"IN-05","input_label":"META01 field/unit/lineage contract patterns","source_anchor":"ANCH-04","why_needed":"Offers reusable audit patterns after variables are selected.","interface_question_answered":"How can future INTERFACE01 fields and lineage be recorded consistently?","priority":"P2","claim_boundary":"No scientific inference from catalog structure.","unit_status":"pilot_with_unresolved_fields","recommended_use":"supporting_context","review_note":"Adapt selectively; do not expand architecture now."},
    ]
    write_csv("06_interface01_candidate_inputs.csv", ["candidate_id","input_label","source_anchor","why_needed","interface_question_answered","priority","claim_boundary","unit_status","recommended_use","review_note"], candidates)

    questions = [
        ("DR-01","emergent_spacetime","Which established works treat effective geometry as an emergent relational or correlation-based structure?","Contextualizes the proposed interface layer without assuming QSB equivalence.","papers, textbooks, reviews","emergent relational geometry correlation structure effective spacetime","P0","high"),
        ("DR-02","deBroglie_phase","Which works formulate an explicit, testable map from quantum phase or interference observables to geometric or adjacency order?","Targets the highest-severity formal-link gap.","papers, textbooks, code_repositories","quantum phase interference emergent geometry adjacency mechanism","P0","high"),
        ("DR-03","graph_geometry","Which models derive effective distance, neighborhood, or geometry from Gram, kernel, or weighted-graph structures?","Provides comparison families for Phase-D motifs.","papers, textbooks, code_repositories","Gram matrix kernel graph effective distance emergent geometry","P0","medium"),
        ("DR-04","materialsensitivity","Which experimental or computational studies report mass-, isotope-, or material-sensitive de-Broglie phase/interference signatures, with explicit units and controls?","Frames MATERIAL01 against external source and data candidates.","papers, datasets, code_repositories, reviews","isotope mass dependent de Broglie phase interference material sensitivity","P0","high"),
        ("DR-05","semiclassical_gravity","Which semiclassical or quantum-gravity approaches explicitly analyze a mediation mechanism between stress-energy descriptions and geometry?","Clarifies nearby mechanism questions and terminology boundaries.","papers, textbooks, reviews","semiclassical gravity stress energy geometry mediation mechanism","P0","high"),
        ("DR-06","entanglement_geometry","How do entanglement-geometry proposals distinguish correlation measures from metric, causal, and dynamical claims?","Helps construct a defensive claim and terminology contract.","papers, textbooks, reviews","entanglement geometry correlation metric causality claim boundary","P1","high"),
        ("DR-07","computational_models","Which open computational models expose phase-to-kernel-to-graph pipelines with reproducible threshold sensitivity analyses?","May identify benchmarkable algorithm families after formalization.","papers, code_repositories, datasets","phase kernel graph threshold reproducible simulation","P1","medium"),
        ("DR-08","relational_quantum","Which relational quantum frameworks define observables and reference structures without presupposing background geometry?","Supplies foundational comparison context.","papers, textbooks, reviews","relational quantum observables background independent geometry","P2","medium"),
    ]
    question_rows = [{"question_id":q[0],"research_area":q[1],"question":q[2],"why_relevant_for_qsb":q[3],"expected_source_types":q[4],"search_terms":q[5],"priority":q[6],"risk_of_overclaim":q[7],"notes":"Question only; INVENTORY01 performed no external search."} for q in questions]
    write_csv("07_deep_research_candidate_questions.csv", ["question_id","research_area","question","why_relevant_for_qsb","expected_source_types","search_terms","priority","risk_of_overclaim","notes"], question_rows)

    reviews = [
        {"review_id":"REV-01","source_path":"runs/QSB-GAP01/legacy_lineage_cross_mart_mapping/01_legacy_source_inventory.csv","issue_type":"missing_authoritative_sources","description":"Named FoP/de-Broglie manuscript sources were missing in the prior GAP01 inventory.","severity":"high","recommended_resolution":"Identify the authoritative source version and review it directly before importing equations or mechanism claims.","blocks_interface01":"yes"},
        {"review_id":"REV-02","source_path":"runs/QSB-GAP01C/additional_legacy_intake/01_gap01c_additional_source_inventory.csv","issue_type":"external_pointer_review","description":"Additional phase-line-element PDFs are represented through prior inventory pointers, not reinterpreted here.","severity":"medium","recommended_resolution":"Perform controlled human source review with provenance and claim boundaries.","blocks_interface01":"optional"},
        {"review_id":"REV-03","source_path":"poster/visual source not identified in indexed repo anchors","issue_type":"missing_visual_anchor","description":"No direct poster/visual bridge artifact was established by the curated repo scan.","severity":"medium","recommended_resolution":"Provide or identify the authoritative visual artifact if it should inform INTERFACE01.","blocks_interface01":"no"},
        {"review_id":"REV-04","source_path":"runs/QSB-D0X/phase_d_local_threshold_motif_summary/10_d0x_units_dimensions_register.csv","issue_type":"unit_mapping","description":"Phase-D remains in model/dimensionless toy-model units without SI conversion.","severity":"high","recommended_resolution":"Keep Phase-D and MATERIAL01 numeric channels separate until a justified dimensional map is defined.","blocks_interface01":"yes"},
        {"review_id":"REV-05","source_path":"runs/QSB-MATERIAL01/typb_materialsensitive_signature_mart_intake/csv/07_material01_review_items.csv","issue_type":"material_unit_and_derivation_review","description":"MATERIAL01 retains mixed units, atomic-mass-unit review, support files, and derived isotope-shift review items.","severity":"high","recommended_resolution":"Select only reviewed result anchors and carry row-level review flags.","blocks_interface01":"yes"},
        {"review_id":"REV-06","source_path":"runs/QSB-GAP02C/source_hub_schema_hardening/qsb_source_hub_hardened_dry_run.sqlite","issue_type":"unresolved_lineage","description":"Source-Hub relationships are empty and unresolved references remain.","severity":"medium","recommended_resolution":"Use provenance records conservatively; require human lineage decisions for source promotion.","blocks_interface01":"optional"},
        {"review_id":"REV-07","source_path":"runs/QSB-META01-03/causality07_pilot_metadata/qsb_metadata_catalog.sqlite","issue_type":"scope_transfer","description":"Metadata catalog pilot coverage is CAUSALITY07-specific and includes unresolved unit/dimension decisions.","severity":"low","recommended_resolution":"Map only selected patterns after INTERFACE01 objects and fields are fixed.","blocks_interface01":"no"},
    ]
    write_csv("08_open_review_items.csv", ["review_id","source_path","issue_type","description","severity","recommended_resolution","blocks_interface01"], reviews)

    assessment = f"""# QSB-INVENTORY01 Final Assessment

## Zweck
QSB-INVENTORY01 kartiert vorhandene interne Legacy-, Phase-D-, MATERIAL01-, GAP- und META-Anker fuer eine moegliche INTERFACE01-Fortsetzung. Es wurde kein neuer Physiklauf und keine externe Recherche ausgefuehrt.

## Input-Sufficiency
Status: sufficient_for_alignment_with_review_items

Die vorhandenen Artefakte reichen fuer eine knappe Anschluss- und Gap-Karte. Sie reichen nicht fuer einen validierten Mechanismus von de-Broglie-Phase oder Interferenz zu geometrischer Ordnung.

## Wichtigste Legacy-Cluster
- de-Broglie-Phasen-/Interferenzkern: als interne Anchor-Note und GAP-Lineage erkennbar; Mechanismusstatus review-pflichtig.
- Emergent relationale Geometrie / Gram-first / FoP: als Legacy-Strang erkennbar; keine zertifizierte formale oder physikalische Aequivalenz.
- Phase-D-Schwellenmotivlinie: konsolidierter Toy-Modell-Anker.
- MATERIAL01: material- und isotopensensitive Signaturdaten mit gemischtem Einheitenstatus.
- Source-Hub/GAP und META: nutzbare Provenienz-, Claim-, Feld-, Einheiten- und Lineage-Strukturen.

Ein direkter Poster-/Visual-Anker wurde in den kuratierten Repo-Quellen nicht etabliert und bleibt Review-Item.

## Aktuelle Befundanker
1. Phase D dokumentiert intern die lokale Kette Force-Bruchkante -> verschachtelte Fenster -> Kantenkippen -> Nachbarschaftssignatur -> analytischer Schwellenabstand -> lokaler theta-Schnittpunkt.
2. MATERIAL01 stellt drei interne Result-Anker fuer materialsensitive de-Broglie-Phase/Welle/Signatur-Verschiebungen bereit.
3. GAP dokumentiert Legacy-Strands und Claim-Risiken als Lineage-Kontext, nicht als aktuelle Validierung.
4. Source-Hub und META unterstuetzen eine spaetere auditierbare Auswahl und Registrierung.

## Nutzbare DWH-/Metadatenartefakte
Vier SQLite-Datenbanken wurden ausschliesslich read-only geoeffnet. MATERIAL01 ist fuer konkrete interne Result-Anker nutzbar. Source-Hub- und META-Tabellen sind partiell fuer Provenienz, Claim-Grenzen, Felder, Einheiten, Lineage und Validierung nutzbar. Ihre Metadatenstruktur erzeugt keine wissenschaftliche Evidenz.

## Zentrale Gaps
- Es fehlt eine formale, pruefbare Abbildung von Phase/Interferenz/Korrelation auf Threshold-, Kanten- und Nachbarschaftsobjekte.
- Phase-D-Modellgroessen duerfen nicht numerisch mit MATERIAL01-SI-/Massengroessen vermischt werden.
- Die physikalische Rolle der Interface-Schicht ist noch Hypothese und benoetigt Disconfirmationskriterien.
- Korrelationsfeld, Strukturfeld, Interface-Schicht und geometrische Ordnung brauchen getrennte Definitionen.
- Autoritative Legacy-Manuskript- und Visualquellen muessen direkt geprueft werden.

## Empfehlung fuer INTERFACE01
INTERFACE01 sollte als kleiner Formalisierungs- und Entscheidungsblock beginnen: zuerst Variable/Objekt, Einheit/Dimension, Transformation und Claim-Level fuer jeden Pfeil der Kernkette festlegen. P0-Inputs sind die Phase-D-Motivkette, die drei MATERIAL01-Result-Anker und die explizit als Hypothese markierte Phase/Interferenz/Korrelationskette. Ein neuer Physiklauf sollte erst nach einem akzeptierten Einheiten- und Transformationsvertrag geplant werden.

## Deep-Research-Einschaetzung
Deep Research ist hilfreich, aber erst nach INVENTORY01 und nach Fixierung der internen Begriffe. Die vorbereiteten Fragen zielen auf relationale und korrelationsbasierte Geometrie, Phase-zu-Geometrie-Mechanismen, Gram-/Kernel-/Graph-Modelle, materialsensitive de-Broglie-Signaturen und semiklassische Vermittlungsfragen. INVENTORY01 behauptet keine externen Ergebnisse oder Bestaetigungen.

## Claim-Grenze
{CLAIM}

Phase-D und MATERIAL01 sind komplementaere interne Anker fuer lokale Threshold-/Relationsmotive beziehungsweise materialsensitive de-Broglie-Signaturverschiebungen. Daraus folgt weder eine Raumzeit- oder Gravitationsemergenz noch eine vollstaendige Verbindung von Quantenmechanik und Allgemeiner Relativitaetstheorie.

## Naechster Schritt
Eine knappe INTERFACE01-Eingangsspezifikation erstellen, die GAP-01 bis GAP-05 mit Definitionen, Dimensionsvertrag, formaler Pfeilkarte, Akzeptanztests und Claim-Grenzen adressiert. Deep Research danach gezielt gegen diese Karte ausfuehren.
"""
    (OUTPUT / "09_inventory01_final_assessment.md").write_text(assessment, encoding="utf-8")

    missing = sum(row["read_status"] == "missing" for row in sources)
    failed_assets = sum(row["read_status"] == "failed" for row in assets)
    status = "inventory01_legacy_to_interface_alignment_failed_checks" if failed_assets else "inventory01_legacy_to_interface_alignment_completed_with_review_items"
    manifest = {
        "run_id": "QSB-INVENTORY01", "status": status,
        "output_dir": "runs/QSB-INVENTORY01/legacy_to_interface_alignment_map",
        "input_sufficiency": "sufficient_for_alignment_with_review_items" if not missing else "partial_inputs",
        "sources_indexed": len(sources), "legacy_clusters": len(clusters), "current_evidence_anchors": len(anchors),
        "dwh_assets": len(assets), "gap_items": len(gaps), "interface01_candidate_inputs": len(candidates),
        "deep_research_questions": len(question_rows), "review_items": len(reviews),
        "sqlite_databases_opened_read_only": 4, "missing_curated_sources": missing,
        "mutated_existing_files": False, "generated_synthetic_evidence": False,
        "external_research_performed": False, "new_physics_run_performed": False,
        "created_utc": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "claim_boundary": CLAIM,
    }
    (OUTPUT / "10_inventory01_run_manifest.json").write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps(manifest, ensure_ascii=False))


if __name__ == "__main__":
    main()
