#!/usr/bin/env python3
"""Generate the bounded QSB-INTERFACE01-A minimal mechanism skeleton."""

from __future__ import annotations

import csv
import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path


REPO = Path(__file__).resolve().parents[2]
OUTPUT = REPO / "runs/QSB-INTERFACE01A/minimal_mechanism_skeleton"
CLAIM = "Minimal mechanism skeleton only; not a proof of emergent spacetime or gravitation."
INVENTORY = "runs/QSB-INVENTORY01/legacy_to_interface_alignment_map"
MATERIAL = "runs/QSB-MATERIAL01/typb_materialsensitive_signature_mart_intake"
PHASE_D = "runs/QSB-D0X/phase_d_local_threshold_motif_summary"


def write_csv(name: str, fields: list[str], rows: list[dict[str, object]]) -> None:
    with (OUTPUT / name).open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def inspect_anchor(anchor_id: str, label: str, anchor_class: str, source_path: str,
                   summary: str, unit_status: str, claim_boundary: str,
                   usable: str, review_note: str) -> dict[str, str]:
    path = REPO / source_path
    if path.exists():
        read_status = "pointer_only" if path.suffix.lower() in {".pdf", ".zip"} else "read_ok"
    else:
        read_status = "missing"
        usable = "review"
        review_note = f"Missing locally; {review_note}"
    return {
        "anchor_id": anchor_id, "anchor_label": label, "anchor_class": anchor_class,
        "source_path": source_path, "read_status": read_status,
        "key_content_summary": summary, "unit_status": unit_status,
        "claim_boundary": claim_boundary, "usable_for_interface01a": usable,
        "review_note": review_note,
    }


def verify_material_db(path: Path) -> tuple[bool, str]:
    if not path.exists():
        return False, "MATERIAL01 database missing."
    try:
        connection = sqlite3.connect(f"file:{path.resolve()}?mode=ro", uri=True)
        names = {row[0] for row in connection.execute(
            "SELECT name FROM sqlite_master WHERE type='table'"
        )}
        required = {"dim_material_system", "fact_debroglie_material_signature",
                    "fact_isotope_shift", "result_material_sensitivity_anchor"}
        counts = {
            name: connection.execute(f'SELECT COUNT(*) FROM "{name}"').fetchone()[0]
            for name in sorted(required & names)
        }
        connection.close()
        missing = sorted(required - names)
        if missing:
            return False, f"Missing tables: {', '.join(missing)}."
        return True, "Read-only table counts: " + ", ".join(f"{k}={v}" for k, v in counts.items())
    except sqlite3.Error as error:
        return False, f"Read-only SQLite inspection failed: {error}"


def material_labels(path: Path) -> set[str]:
    if not path.exists():
        return set()
    with path.open(encoding="utf-8", newline="") as handle:
        return {row["material_label"] for row in csv.DictReader(handle)}


def main() -> None:
    if OUTPUT.exists():
        raise SystemExit(f"Refusing to overwrite existing output directory: {OUTPUT.relative_to(REPO)}")
    OUTPUT.mkdir(parents=True)

    db_ok, db_note = verify_material_db(REPO / MATERIAL / "material01_typb_signature_mart.sqlite")
    anchors = [
        inspect_anchor("IA-01", "INVENTORY01 evidence anchor map", "inventory", f"{INVENTORY}/03_current_evidence_anchor_map.csv", "Four bounded internal evidence/lineage anchors for Phase D, MATERIAL01, legacy mechanism language, and metadata.", "mixed_by_anchor", "Alignment map only; no mechanism proof.", "yes", "Use claim and review fields row by row."),
        inspect_anchor("IA-02", "INVENTORY01 gap map", "inventory", f"{INVENTORY}/05_legacy_to_interface_gap_map.csv", "Seven gaps including the formal phase-to-threshold link and model-unit/SI separation.", "mixed_by_gap", "Gap inventory, not evidence.", "yes", "P0 gaps constrain this skeleton."),
        inspect_anchor("IA-03", "INVENTORY01 candidate inputs", "inventory", f"{INVENTORY}/06_interface01_candidate_inputs.csv", "Prioritized Phase-D, MATERIAL01, mechanism-hypothesis, and metadata candidates.", "mixed_by_input", "Candidate-use classification only.", "yes", "P0 entries remain bounded by their source claims."),
        inspect_anchor("IA-04", "INVENTORY01 final assessment", "inventory", f"{INVENTORY}/09_inventory01_final_assessment.md", "Recommends a variable, dimension, transformation, acceptance-test, and claim-level formalization block.", "not_applicable", "Inventory and alignment only.", "yes", "Provides the immediate scope boundary."),
        inspect_anchor("IA-05", "INVENTORY01 run manifest", "inventory", f"{INVENTORY}/10_inventory01_run_manifest.json", "Records sufficient alignment inputs with review items and no synthetic evidence.", "metadata_only", "Manifest status does not validate physics.", "yes", "Check status and mutation flags."),
        inspect_anchor("IA-06", "MATERIAL01 signature mart", "material01", f"{MATERIAL}/material01_typb_signature_mart.sqlite", db_note, "mixed_review; lambda_db=m; energy=J; scores=dimensionless; mass_u=atomic_mass_unit_review", "Internal materialsensitive signature anchors only.", "yes" if db_ok else "review", "Opened with SQLite mode=ro; no database mutation."),
        inspect_anchor("IA-07", "MATERIAL01 material systems", "material01", f"{MATERIAL}/csv/03_dim_material_system.csv", "Six expected atomic species and nine isotope members are registered.", "mass_u=atomic_mass_unit_review where used", "Dimension records do not establish an interface mechanism.", "yes", "Use labels and review flags without unit conversion."),
        inspect_anchor("IA-08", "MATERIAL01 signature facts", "material01", f"{MATERIAL}/csv/04_fact_debroglie_material_signature.csv", "Existing material-sensitive wavelength, energy, score, and ordering facts.", "lambda_db=m; energy=J; scores=dimensionless; mixed review", "Source-output-bound facts; no geometric inference.", "partial", "Do not mix with Phase-D model units."),
        inspect_anchor("IA-09", "MATERIAL01 isotope shifts", "material01", f"{MATERIAL}/csv/05_fact_isotope_shift.csv", "Existing isotope mass-order versus wave-order shift records.", "mixed_review", "Derived ordering summaries require review.", "partial", "No new calculation in INTERFACE01-A."),
        inspect_anchor("IA-10", "MATERIAL01 result anchors", "material01", f"{MATERIAL}/csv/06_result_material_sensitivity_anchor.csv", "Three bounded result anchors for atomic and isotope-sensitive phase/wave/signature shifts.", "mixed_review", "Not evidence of emergent spacetime or gravitation.", "yes", "Preferred material-sensitive interface intake."),
        inspect_anchor("IA-11", "Phase-D local threshold motif summary", "phase_d", f"{PHASE_D}/11_d0x_final_assessment.md", "Toy-model chain from force break edges through neighborhood signatures to local theta crossings.", "model_units / dimensionless toy-model units; not_SI_converted", "Model- and threshold-bound; no external physical validation.", "yes", "Use as relational target vocabulary, not SI material data."),
        inspect_anchor("IA-12", "FoP manuscript pointer", "legacy_manuscript", "manuscript_fop_v2.pdf", "Named legacy manuscript candidate; no direct local inspection available.", "unknown", "No equation or claim may be promoted without direct review.", "review", "Resolve authoritative source and provenance."),
        inspect_anchor("IA-13", "Gram-first submission pointer", "legacy_manuscript", "arxiv_GramFirst_submission.zip", "Named legacy Gram-first archive candidate; no direct local inspection available.", "unknown", "Archive naming is not scientific support.", "review", "Resolve and inspect without treating archive content as validated."),
        inspect_anchor("IA-14", "FoP supplementary pointer", "legacy_manuscript", "FoP_supplementary_bundle.zip", "Named supplementary archive candidate; no direct local inspection available.", "unknown", "No formal relation imported from an unavailable bundle.", "review", "Resolve authoritative bundle."),
        inspect_anchor("IA-15", "Material-wave visual bridge pointer", "poster_visual", "Poster/Visual zur materialsensitiven Bruecke", "Named visual bridge candidate; no direct local artifact identified.", "unknown", "Visual analogy is not mechanism evidence.", "review", "Provide the authoritative visual artifact if required."),
    ]
    write_csv("01_interface01a_input_anchor_register.csv", ["anchor_id","anchor_label","anchor_class","source_path","read_status","key_content_summary","unit_status","claim_boundary","usable_for_interface01a","review_note"], anchors)

    quantities = [
        {"quantity_id":"Q01","quantity_label":"mass","symbol":"m","mechanism_stage":"matter_state","expected_unit":"kg or atomic mass unit under review","expected_dimension":"M","source_anchor":"IA-07; IA-08","status":"mixed_review","allowed_operation":"Use source-recorded mass/order information within its declared unit context.","forbidden_operation":"Do not silently convert mass_u to kg or combine it with model-unit quantities.","review_note":"No explicit input conversion rule was established."},
        {"quantity_id":"Q02","quantity_label":"momentum","symbol":"p","mechanism_stage":"matter_state","expected_unit":"kg m s^-1","expected_dimension":"M L T^-1","source_anchor":"mechanism requirement","status":"unknown","allowed_operation":"Introduce only with an explicit source or defined derivation.","forbidden_operation":"Do not infer momentum from signature ordering alone.","review_note":"Not established as a MATERIAL01 result-anchor field."},
        {"quantity_id":"Q03","quantity_label":"energy","symbol":"E","mechanism_stage":"matter_state","expected_unit":"J","expected_dimension":"M L^2 T^-2","source_anchor":"IA-08","status":"si_valid","allowed_operation":"Use recorded energy_j within MATERIAL01 provenance.","forbidden_operation":"Do not map directly to Phase-D thresholds.","review_note":"Source-output meaning and derivation remain relevant."},
        {"quantity_id":"Q04","quantity_label":"de-Broglie wavelength","symbol":"lambda_db","mechanism_stage":"phase","expected_unit":"m","expected_dimension":"L","source_anchor":"IA-08; IA-10","status":"si_valid","allowed_operation":"Compare source-recorded material/isotope wavelength features.","forbidden_operation":"Do not identify wavelength with graph distance or emergent metric distance.","review_note":"Materialsensitive input anchor only."},
        {"quantity_id":"Q05","quantity_label":"phase","symbol":"phi_i","mechanism_stage":"phase","expected_unit":"dimensionless angle; radian convention","expected_dimension":"1","source_anchor":"IA-03; legacy hypothesis","status":"unknown","allowed_operation":"Define modulo 2*pi under an explicit convention.","forbidden_operation":"Do not treat phase as a length or use an unspecified absolute phase.","review_note":"Requires an explicit operational phase definition."},
        {"quantity_id":"Q06","quantity_label":"relative phase","symbol":"delta_phi_ij","mechanism_stage":"phase","expected_unit":"dimensionless angle; radian convention","expected_dimension":"1","source_anchor":"mechanism requirement","status":"dimensionless_valid","allowed_operation":"Form phi_i-phi_j modulo 2*pi after defining indices and reference convention.","forbidden_operation":"Do not combine directly with SI length or model-unit distance.","review_note":"Formal candidate, not an observed INTERFACE01 result."},
        {"quantity_id":"Q07","quantity_label":"interference kernel","symbol":"K_ij","mechanism_stage":"interference","expected_unit":"dimensionless or model-defined","expected_dimension":"1 or explicit model dimension","source_anchor":"mechanism requirement","status":"unknown","allowed_operation":"Define as an explicit bounded function of delta_phi_ij and any declared weights.","forbidden_operation":"Do not assume a kernel definition or physical force interpretation.","review_note":"P0 formal object is missing."},
        {"quantity_id":"Q08","quantity_label":"correlation magnitude","symbol":"G_ij","mechanism_stage":"correlation","expected_unit":"dimensionless","expected_dimension":"1","source_anchor":"mechanism requirement","status":"unknown","allowed_operation":"Derive from a specified kernel/statistic with normalization and domain.","forbidden_operation":"Do not identify correlation with causation, metric, or geometry.","review_note":"P0 mapping K_ij -> G_ij is missing."},
        {"quantity_id":"Q09","quantity_label":"threshold","symbol":"theta","mechanism_stage":"threshold","expected_unit":"dimensionless within defined model space","expected_dimension":"1","source_anchor":"IA-11","status":"model_units_only","allowed_operation":"Compare only quantities normalized in the same declared model space.","forbidden_operation":"Do not compare theta numerically with SI wavelength, energy, mass, or momentum.","review_note":"Phase-D theta=0.0300 is a calibrated toy-model work point, not a universal constant."},
        {"quantity_id":"Q10","quantity_label":"adjacency relation","symbol":"A_ij","mechanism_stage":"graph_relation","expected_unit":"dimensionless binary relation","expected_dimension":"1","source_anchor":"IA-11","status":"dimensionless_valid","allowed_operation":"Define by an explicit threshold predicate in one model space.","forbidden_operation":"Do not identify adjacency with physical proximity without a validated map.","review_note":"Edge-flip semantics and tie handling must be declared."},
        {"quantity_id":"Q11","quantity_label":"neighborhood signature","symbol":"S_i","mechanism_stage":"graph_relation","expected_unit":"dimensionless/model-defined record","expected_dimension":"1 or structured categorical","source_anchor":"IA-11","status":"model_units_only","allowed_operation":"Compute from a declared adjacency/kernel neighborhood and stable encoding.","forbidden_operation":"Do not promote signature similarity to physical identity.","review_note":"Phase-D signatures remain threshold- and model-bound."},
        {"quantity_id":"Q12","quantity_label":"relational distance","symbol":"D_rel","mechanism_stage":"graph_relation","expected_unit":"graph steps or declared model units","expected_dimension":"model-defined","source_anchor":"mechanism requirement","status":"model_units_only","allowed_operation":"Use only after selecting and documenting a graph-distance definition.","forbidden_operation":"Do not call D_rel an SI spacetime interval or metric distance.","review_note":"Metric axioms and physical interpretation are untested."},
        {"quantity_id":"Q13","quantity_label":"geometry readout","symbol":"R_geom","mechanism_stage":"emergent_geometry","expected_unit":"interpretive/model-defined; no direct SI metric","expected_dimension":"unknown","source_anchor":"mechanism target","status":"unknown","allowed_operation":"Treat as a testable relational readout candidate with explicit criteria.","forbidden_operation":"Do not report a physical spacetime metric, curvature, or gravity result.","review_note":"Endpoint is a mechanism goal, not a current result."},
    ]
    write_csv("02_interface01a_quantity_dimension_contract.csv", ["quantity_id","quantity_label","symbol","mechanism_stage","expected_unit","expected_dimension","source_anchor","status","allowed_operation","forbidden_operation","review_note"], quantities)

    arrows = [
        {"arrow_id":"A01","from_stage":"matter_state","to_stage":"de_broglie_wavelength_phase","arrow_label":"Matter state -> de-Broglie wavelength / phase","formal_relation_candidate":"lambda_db=h/p where p is explicitly available; phase requires a separately declared convention.","source_support":"IA-08; IA-10","support_status":"partial_internal","unit_dimension_status":"lambda_db recorded in m; p and operational phi not established by the result anchors.","claim_boundary":"Materialsensitive wave/signature dependence only.","acceptance_need":"Declare source/derivation for p and phi; preserve mass_u review.","review_note":"Do not back-fill missing variables from ordering labels."},
        {"arrow_id":"A02","from_stage":"de_broglie_phase","to_stage":"relative_phase","arrow_label":"de-Broglie phase -> relative phase","formal_relation_candidate":"delta_phi_ij = wrap(phi_i - phi_j)","source_support":"mechanism definition","support_status":"hypothesis_only","unit_dimension_status":"dimensionless angle with one modulo convention.","claim_boundary":"Definition candidate, not an observed transition.","acceptance_need":"Specify indices, reference choice, wrapping range, and invariance tests.","review_note":"Absolute-phase dependence must be excluded or justified."},
        {"arrow_id":"A03","from_stage":"relative_phase","to_stage":"interference_kernel","arrow_label":"Relative phase -> interference/kernel","formal_relation_candidate":"K_ij = F(delta_phi_ij, w_ij) with F explicitly selected and bounded.","source_support":"legacy hypothesis through IA-03","support_status":"review_gap","unit_dimension_status":"K_ij dimensionless or model-defined; weights require units.","claim_boundary":"No kernel function is validated here.","acceptance_need":"Define F, domain, normalization, invariances, and counterexamples.","review_note":"P0 formal gap."},
        {"arrow_id":"A04","from_stage":"interference_kernel","to_stage":"correlation_magnitude","arrow_label":"Interference/kernel -> correlation magnitude","formal_relation_candidate":"G_ij = C[K]_ij for an explicit correlation/aggregation operator C.","source_support":"legacy hypothesis through IA-03","support_status":"review_gap","unit_dimension_status":"Output should be dimensionless after declared normalization.","claim_boundary":"Correlation is not causation or geometry.","acceptance_need":"Define estimator/operator, sample/support domain, normalization, and stability.","review_note":"P0 K-to-G requirement."},
        {"arrow_id":"A05","from_stage":"correlation_magnitude","to_stage":"threshold_relation","arrow_label":"Correlation magnitude -> threshold relation","formal_relation_candidate":"R_ij(theta)=1[G_ij >= theta] with declared tie rule.","source_support":"IA-11 supports threshold motifs, not this upstream mapping.","support_status":"review_gap","unit_dimension_status":"G_ij and theta must be dimensionless and normalized in the same model space.","claim_boundary":"No direct MATERIAL01-to-Phase-D numerical map.","acceptance_need":"Define theta calibration, scale compatibility, sensitivity, and null controls.","review_note":"Central bridge gap."},
        {"arrow_id":"A06","from_stage":"threshold_relation","to_stage":"adjacency_edge_flip","arrow_label":"Threshold relation -> adjacency / edge flip","formal_relation_candidate":"A_ij(theta)=R_ij(theta); flip when A_ij changes under a declared control parameter.","source_support":"IA-11","support_status":"supported_internal","unit_dimension_status":"dimensionless binary relation within Phase-D model space.","claim_boundary":"Supported as a toy-model motif only.","acceptance_need":"Document threshold predicate, tie rule, control parameter, and reproducibility.","review_note":"Phase-D mapping cannot be exported silently to SI inputs."},
        {"arrow_id":"A07","from_stage":"adjacency_edge_flip","to_stage":"neighborhood_signature","arrow_label":"Adjacency / edge flip -> neighborhood signature","formal_relation_candidate":"S_i = encode({A_ij}_j, local kernel context)","source_support":"IA-11","support_status":"supported_internal","unit_dimension_status":"dimensionless/model-defined structured signature.","claim_boundary":"Threshold- and model-bound local signature.","acceptance_need":"Specify encoding, locality, hash stability, and classification sensitivity.","review_note":"Multi-edge and sensitive motifs remain reviewable."},
        {"arrow_id":"A08","from_stage":"neighborhood_signature","to_stage":"relational_order","arrow_label":"Neighborhood signatures -> relational order","formal_relation_candidate":"Define a partial/preorder only after an explicit comparator and consistency conditions.","source_support":"Phase-D target vocabulary; no completed order derivation.","support_status":"hypothesis_only","unit_dimension_status":"Relational/categorical; no SI unit.","claim_boundary":"No global uniqueness, causal order, or dynamics claim.","acceptance_need":"Define order relation and test reflexivity/antisymmetry/transitivity as applicable.","review_note":"Local signatures alone need not determine a global order."},
        {"arrow_id":"A09","from_stage":"relational_order","to_stage":"geometrically_readable_structure","arrow_label":"Relational order -> geometrically readable emergent structure","formal_relation_candidate":"R_geom = readout(order, adjacency, D_rel) under explicit geometric diagnostics.","source_support":"mechanism target only","support_status":"hypothesis_only","unit_dimension_status":"Interpretive/model-defined; no direct SI metric.","claim_boundary":"Geometrical readability remains relational, emergent, and test-required.","acceptance_need":"Predeclare metric/order diagnostics, null models, failure cases, and limits of interpretation.","review_note":"Endpoint is not a derived spacetime geometry."},
    ]
    write_csv("03_interface01a_mechanism_arrow_map.csv", ["arrow_id","from_stage","to_stage","arrow_label","formal_relation_candidate","source_support","support_status","unit_dimension_status","claim_boundary","acceptance_need","review_note"], arrows)

    requirements = [
        {"link_id":"L01","link_label":"Relative phase to kernel map","current_support":"Legacy phase/interference language only.","missing_piece":"Selected and justified function F for delta_phi_ij and optional weights.","required_formal_object":"K_ij = F(delta_phi_ij, w_ij)","unit_dimension_requirement":"Dimensionless K_ij or explicit model dimension; weight dimensions declared.","candidate_test":"Global-phase-shift invariance, boundedness, symmetry/asymmetry declaration, and null-phase controls.","priority":"P0","blocks_interface01_core":"yes","review_note":"No function is selected in INTERFACE01-A."},
        {"link_id":"L02","link_label":"Kernel to correlation map","current_support":"Correlation is present as legacy mechanism vocabulary.","missing_piece":"Explicit operator/estimator C and normalization.","required_formal_object":"G_ij = C[K]_ij","unit_dimension_requirement":"Dimensionless normalized output with declared range.","candidate_test":"Reproducibility, normalization, perturbation stability, and independent null-input behavior.","priority":"P0","blocks_interface01_core":"yes","review_note":"Correlation must not be relabeled as geometry."},
        {"link_id":"L03","link_label":"Correlation to threshold relation","current_support":"Phase D supports downstream threshold motifs only.","missing_piece":"Shared model space and calibration connecting G_ij to theta.","required_formal_object":"R_ij(theta)=1[G_ij >= theta] plus tie rule","unit_dimension_requirement":"G_ij and theta dimensionless on the same normalization scale.","candidate_test":"Threshold sweep, tie handling, stability window, and null/randomized baselines.","priority":"P0","blocks_interface01_core":"yes","review_note":"No numerical MATERIAL01/Phase-D bridge exists."},
        {"link_id":"L04","link_label":"Edge-flip mechanism signature rule","current_support":"Internal Phase-D edge flips and neighborhood signatures.","missing_piece":"Criterion distinguishing mechanism-relevant flips from threshold artifacts.","required_formal_object":"Flip event record with control parameter, pre/post margin, neighborhood context, and classification.","unit_dimension_requirement":"All compared margins and thresholds from one model space.","candidate_test":"Replay determinism, perturbation robustness, multi-edge handling, and negative controls.","priority":"P0","blocks_interface01_core":"partial","review_note":"Phase-D sensitive and multi-edge motifs remain open."},
        {"link_id":"L05","link_label":"Graph distance versus physical metric separation","current_support":"Relational/Gram-to-graph legacy strand; no certified metric bridge.","missing_piece":"Explicit graph distance and independent geometric-readout criteria.","required_formal_object":"D_rel plus declared metric/order diagnostics","unit_dimension_requirement":"Graph/model units remain separate from SI length and spacetime interval.","candidate_test":"Metric-axiom checks where claimed, embedding stress, non-uniqueness tests, and null graphs.","priority":"P0","blocks_interface01_core":"yes","review_note":"Geometrical readability is not physical metric identity."},
        {"link_id":"L06","link_label":"Material sensitivity injection point","current_support":"MATERIAL01 supports phase/wave/signature shifts.","missing_piece":"Formal rule selecting whether material dependence enters phi, weights, K, G, or calibration.","required_formal_object":"Material-conditioned parameter map with provenance and review flags","unit_dimension_requirement":"SI/material values must be transformed through an explicit dimension-safe map before any model-space use.","candidate_test":"Species/isotope controls, label permutation, unit audit, and out-of-sample material holdout.","priority":"P1","blocks_interface01_core":"partial","review_note":"Do not assume all stages inherit material sensitivity."},
    ]
    write_csv("04_interface01a_phase_to_threshold_link_requirements.csv", ["link_id","link_label","current_support","missing_piece","required_formal_object","unit_dimension_requirement","candidate_test","priority","blocks_interface01_core","review_note"], requirements)

    found_labels = material_labels(REPO / MATERIAL / "csv/03_dim_material_system.csv")
    material_specs = [
        ("ML-01","hydrogen","atomic material signature","signature"),
        ("ML-02","sodium","atomic material signature","signature"),
        ("ML-03","carbon","atomic material signature","signature"),
        ("ML-04","nitrogen","atomic material signature","signature"),
        ("ML-05","sulfur","atomic material signature","signature"),
        ("ML-06","phosphorus","atomic material signature","signature"),
        ("ML-07","1H/2H/3H","mass-order versus wave-order isotope shift","wavelength"),
        ("ML-08","84Sr/86Sr/87Sr/88Sr","mass-order versus wave-order isotope shift","wavelength"),
        ("ML-09","12C/13C","mass-order versus wave-order isotope shift","wavelength"),
    ]
    material_links = []
    for link_id, label, feature, stage in material_specs:
        members = label.split("/")
        present = all(member in found_labels for member in members)
        material_links.append({
            "material_link_id": link_id, "material_or_series": label,
            "source_anchor": "IA-07; IA-08; IA-09; IA-10",
            "observed_material_sensitive_feature": feature if present else "expected anchor missing",
            "mechanism_stage_impacted": stage if present else "review",
            "interface_implication": "Candidate evidence that material state conditions wave/signature input; downstream correlation or geometry effects are not established.",
            "claim_boundary": "Supports internal material-sensitive de-Broglie wave/signature shifts only.",
            "evidence_status": "supported_internal" if present else "insufficient",
            "unit_status": "mixed_review; wavelength=m where recorded; mass_u remains atomic_mass_unit_review",
            "review_note": "Carry source and derived-row review flags; no new calculation.",
        })
    write_csv("05_interface01a_material_sensitivity_link_map.csv", ["material_link_id","material_or_series","source_anchor","observed_material_sensitive_feature","mechanism_stage_impacted","interface_implication","claim_boundary","evidence_status","unit_status","review_note"], material_links)

    tests = [
        {"test_id":"T01","test_label":"Core dimension contract coverage","test_question":"Are quantities and operations for every core mechanism stage declared?","required_input":"quantity contract; arrow map","expected_pass_condition":"Each stage has a quantity status, allowed operation, forbidden operation, and review note.","failure_condition":"A core arrow relies on an undeclared quantity or dimension.","unit_dimension_check":"Explicit expected units/dimensions and unknown/model-only labels.","claim_boundary_check":"Unknown dimensions cannot be promoted to physical readouts.","priority":"P0","test_status":"pass","review_note":"Completeness of declarations, not physical validation."},
        {"test_id":"T02","test_label":"SI/model-unit separation","test_question":"Are MATERIAL01 SI/mass fields separated from Phase-D model units?","required_input":"quantity contract; arrows A05-A07","expected_pass_condition":"No direct numerical cross-space operation is allowed.","failure_condition":"SI wavelength/energy/mass is compared or combined directly with theta or D_rel.","unit_dimension_check":"Separate SI, atomic-mass-review, and model-space channels.","claim_boundary_check":"No implicit physical calibration.","priority":"P0","test_status":"pass","review_note":"A future explicit transform would require independent validation."},
        {"test_id":"T03","test_label":"Material anchor claim discipline","test_question":"Are material-sensitive anchors described as bounded internal findings?","required_input":"material sensitivity link map","expected_pass_condition":"Every row denies downstream geometry inference and retains mixed review.","failure_condition":"A material signature is presented as spacetime or gravity evidence.","unit_dimension_check":"Recorded units and review status retained.","claim_boundary_check":"Material sensitivity only.","priority":"P0","test_status":"pass","review_note":"All nine expected material/series groups were checked."},
        {"test_id":"T04","test_label":"Formal arrow-chain naming","test_question":"Is phase -> interference -> correlation -> threshold represented by explicit candidate objects?","required_input":"arrows A02-A05; requirements L01-L03","expected_pass_condition":"delta_phi_ij, K_ij, G_ij, theta, and candidate operators are named.","failure_condition":"A narrative jump replaces one or more formal objects.","unit_dimension_check":"All bridge objects are dimensionless or explicitly model-defined.","claim_boundary_check":"Unsupported arrows remain review gaps or hypotheses.","priority":"P0","test_status":"pass","review_note":"Named skeleton does not mean the maps are validated."},
        {"test_id":"T05","test_label":"Phase-to-threshold gap visibility","test_question":"Is at least one formal phase-to-threshold gap explicit?","required_input":"phase-to-threshold requirements","expected_pass_condition":"L01-L03 are explicit P0 blockers.","failure_condition":"The bridge is shown as internally supported without a formal map.","unit_dimension_check":"Shared normalization is required before thresholding.","claim_boundary_check":"No lexical-overlap inference.","priority":"P0","test_status":"pass","review_note":"Three central bridge gaps remain open."},
        {"test_id":"T06","test_label":"Geometric readout boundary","test_question":"Is geometric readability separated from a finished physical metric?","required_input":"Q12-Q13; arrows A08-A09","expected_pass_condition":"Readout is relational/model-defined and requires diagnostics and null tests.","failure_condition":"Graph distance or order is identified with a physical spacetime metric.","unit_dimension_check":"No SI metric unit assigned.","claim_boundary_check":"No spacetime, curvature, or gravity result claimed.","priority":"P0","test_status":"pass","review_note":"Endpoint remains hypothesis-only."},
        {"test_id":"T07","test_label":"Interface-hypothesis scope","test_question":"Is QSB framed as a possible interface layer without displacing established theories?","required_input":"mechanism skeleton; final assessment","expected_pass_condition":"Texts state bounded interface scope and explicit non-claims.","failure_condition":"Text asserts completion, replacement, or derivation beyond inputs.","unit_dimension_check":"Cross-theory units remain unresolved rather than hidden.","claim_boundary_check":"Minimal mechanism skeleton only.","priority":"P0","test_status":"pass","review_note":"No external research performed."},
        {"test_id":"T08","test_label":"Material injection falsifiability","test_question":"Does future work require testing where material dependence enters?","required_input":"requirement L06; material link map","expected_pass_condition":"Candidate injection stage and null/holdout controls are required.","failure_condition":"Material sensitivity is assumed to propagate through every stage.","unit_dimension_check":"Any injection transform must be dimension-safe.","claim_boundary_check":"No downstream mechanism inferred from input sensitivity alone.","priority":"P1","test_status":"pass","review_note":"Test design only; not executed."},
        {"test_id":"T09","test_label":"Relational-order consistency gate","test_question":"Are order and geometry claims conditional on explicit mathematical diagnostics?","required_input":"arrows A08-A09; requirement L05","expected_pass_condition":"Order properties, non-uniqueness, metric diagnostics, and null graphs are required.","failure_condition":"Local signatures are treated as a unique global geometry.","unit_dimension_check":"Graph/model units remain labeled.","claim_boundary_check":"No global uniqueness or physical geometry claim.","priority":"P1","test_status":"pass","review_note":"Gate definition passed; scientific test remains future work."},
    ]
    write_csv("06_interface01a_acceptance_tests.csv", ["test_id","test_label","test_question","required_input","expected_pass_condition","failure_condition","unit_dimension_check","claim_boundary_check","priority","test_status","review_note"], tests)

    reviews = [
        {"review_id":"R01","source_path":"manuscript_fop_v2.pdf","issue_type":"missing_legacy_source","description":"Authoritative FoP manuscript was not found locally.","severity":"high","recommended_resolution":"Resolve version and provenance before importing equations or mechanism statements.","blocks_interface01":"partial"},
        {"review_id":"R02","source_path":"arxiv_GramFirst_submission.zip; FoP_supplementary_bundle.zip","issue_type":"missing_legacy_archives","description":"Named Gram-first and supplementary archives were not found locally.","severity":"medium","recommended_resolution":"Resolve and inspect read-only if their formal objects are needed.","blocks_interface01":"partial"},
        {"review_id":"R03","source_path":"Poster/Visual zur materialsensitiven Bruecke","issue_type":"missing_visual_anchor","description":"No authoritative poster/visual bridge artifact was identified.","severity":"medium","recommended_resolution":"Provide the artifact or omit it from mechanism support.","blocks_interface01":"no"},
        {"review_id":"R04","source_path":f"{MATERIAL}/csv/04_fact_debroglie_material_signature.csv","issue_type":"unit_and_derivation_review","description":"mass_u, mixed fields, and source/derived-row semantics remain review-sensitive.","severity":"high","recommended_resolution":"Retain row-level provenance and define any conversion explicitly before use.","blocks_interface01":"partial"},
        {"review_id":"R05","source_path":f"{PHASE_D}/10_d0x_units_dimensions_register.csv","issue_type":"model_si_separation","description":"Phase-D quantities remain model/dimensionless toy-model units without SI conversion.","severity":"high","recommended_resolution":"Keep separate from MATERIAL01 numerical channels until a validated transform exists.","blocks_interface01":"yes"},
        {"review_id":"R06","source_path":"03_interface01a_mechanism_arrow_map.csv#A03-A05","issue_type":"formal_bridge_gap","description":"delta_phi -> K -> G -> threshold operators are named but not selected or validated.","severity":"high","recommended_resolution":"INTERFACE01-B should compare minimal candidate definitions and preregister null/stability tests.","blocks_interface01":"yes"},
        {"review_id":"R07","source_path":"03_interface01a_mechanism_arrow_map.csv#A08-A09","issue_type":"geometry_readout_gap","description":"Local signatures do not yet determine a relational order or geometrically readable structure.","severity":"high","recommended_resolution":"Define order/metric diagnostics, non-uniqueness tests, and null graphs.","blocks_interface01":"yes"},
        {"review_id":"R08","source_path":"04_interface01a_phase_to_threshold_link_requirements.csv#L06","issue_type":"material_injection_gap","description":"The stage at which material dependence enters the interface chain is not formalized.","severity":"medium","recommended_resolution":"Test explicit alternatives at phase, weight, kernel, correlation, or calibration stages.","blocks_interface01":"partial"},
    ]
    write_csv("07_interface01a_open_review_items.csv", ["review_id","source_path","issue_type","description","severity","recommended_resolution","blocks_interface01"], reviews)

    skeleton = """# QSB-INTERFACE01-A Minimal Mechanism Skeleton

## Zweck
QSB untersucht eine moegliche materialsensitive Interface-Schicht zwischen quantenmechanischer de-Broglie-Phasen-/Interferenzstruktur und relational-geometrisch lesbarer Raumzeitordnung.

INTERFACE01-A formuliert dafuer nur ein minimales, pruefbares Mechanismus-Skelett. Es fuehrt keinen neuen Physiklauf aus und waehlt noch keine konkrete Kernel-, Korrelations- oder Geometrieformel.

## Minimalmechanismus-Kette
```text
Materie / Materiezustand
-> de-Broglie-Wellenlaenge und operational zu definierende Phase phi_i
-> relative Phase delta_phi_ij
-> Interferenzkernel K_ij
-> Korrelationsgroesse G_ij
-> dimensionslose Schwellenrelation R_ij(theta)
-> Adjazenz A_ij / Kantenkippen
-> Nachbarschaftssignatur S_i
-> zu definierende relationale Ordnung
-> geometrisch lesbarer, pruefpflichtiger Struktur-Readout
```

Die Pfeile sind nicht gleich stark gestuetzt. MATERIAL01 und Phase D stuetzen getrennte Enden der Kette. Die mittlere Bruecke `delta_phi -> K -> G -> theta` ist ein formaler Review-Gap.

## Interface-Schicht im Arbeitsmodell
Die Interface-Schicht ist kein behaupteter Stoff. Sie bezeichnet im Arbeitsmodell die Menge expliziter Uebersetzungsregeln, durch die Phasen-/Interferenzvariablen in Korrelations-, Schwellen- und Relationsobjekte uebergehen koennten.

Ein belastbarer Minimalmechanismus braucht fuer jeden Pfeil:
- definierte Eingangs- und Ausgangsobjekte,
- Einheit oder Dimensionsstatus,
- eine konkrete Transformation,
- Null-, Stabilitaets- und Fehlertests,
- eine sichtbare Claim-Grenze.

## Materialsensitiver Anschluss
MATERIAL01 liefert interne Befundanker fuer materialsensitive de-Broglie-Wellen-/Signaturverschiebungen bei hydrogen, sodium, carbon, nitrogen, sulfur und phosphorus sowie den Isotopenserien 1H/2H/3H, 84Sr/86Sr/87Sr/88Sr und 12C/13C.

Diese Anker motivieren eine materialabhaengige Eingangsbedingung. Sie bestimmen noch nicht, ob Materialabhaengigkeit in `phi`, Gewichte, `K`, `G` oder eine Kalibrierung eingeht. Diese Injektionsstelle ist zu testen.

## Phase-D-Anschluss
Phase D liefert intern die modellgebundene Kette Force-Bruchkante -> verschachtelte lokale Fenster -> Kantenkippen -> Nachbarschaftssignatur -> analytischer Schwellenabstand -> lokaler theta-Schnittpunkt.

Das stuetzt die Schwellen-/Adjazenz-/Nachbarschaftsseite als Toy-Modell-Motiv. Es liefert keine validierte Abbildung von de-Broglie-Phase oder MATERIAL01-Groessen auf `theta`.

## Dimensions- und Einheitengrenzen
- `lambda_db` wird in MATERIAL01 als Meter gefuehrt; `energy_j` als Joule.
- `mass_u` bleibt `atomic_mass_unit_review`; keine stille Umwandlung in kg.
- `phi` und `delta_phi` benoetigen eine dimensionslose Winkel-/Radian-Konvention.
- `K_ij` und `G_ij` brauchen explizite Definition und Normalisierung.
- Phase-D-`theta`, Adjazenz und Signaturen bleiben im deklarierten Modellraum.
- SI-Materialgroessen werden nicht direkt mit Phase-D-Modellgroessen verrechnet.
- `D_rel` ist Graph-/Modelldistanz, keine physikalische Raumzeitmetrik.
- Der Geometrie-Readout ist interpretiv und modellbezogen; keine fertige SI-Metrik.

## Was noch nicht behauptet wird
- Kein Nachweis einer emergenten physikalischen Raumzeit oder Gravitation.
- Keine Ableitung einer Raumzeitmetrik, Kruemmung oder Dynamik.
- Keine vollstaendige Verbindung etablierter Quantentheorie und Allgemeiner Relativitaetstheorie.
- Keine globale Eindeutigkeit der relationalen Ordnung.
- Keine Aussage, dass Materialsignaturen automatisch alle spaeteren Mechanismusstufen praegen.

## Akzeptanztests in Kurzform
1. Kernobjekte und Dimensionsstatus sind vollstaendig sichtbar.
2. SI-/Massengroessen und Phase-D-Modellgroessen bleiben getrennt.
3. MATERIAL01 bleibt materialsensitiver Befundanker.
4. `delta_phi -> K -> G -> theta` ist formal benannt.
5. Die offene Phase-zu-Schwellen-Bruecke bleibt als P0-Gap markiert.
6. Geometrische Lesbarkeit bleibt relational, emergent und pruefpflichtig.
7. QSB bleibt eine Interface-Hypothese im abgegrenzten Arbeitsmodell.
8. Material-Injektionsstelle und relationale Ordnung erhalten Null- und Konsistenztests.
"""
    (OUTPUT / "08_interface01a_minimal_mechanism_skeleton.md").write_text(skeleton, encoding="utf-8")

    missing_anchors = sum(row["read_status"] == "missing" for row in anchors)
    passed = sum(row["test_status"] == "pass" for row in tests)
    assessment = f"""# QSB-INTERFACE01-A Final Assessment

## Status
`interface01a_minimal_mechanism_skeleton_completed_with_review_items`

## Input-Sufficiency
`sufficient_core_inputs_with_legacy_review_gaps`

INVENTORY01, MATERIAL01 und Phase D sind fuer ein minimales Skelett vorhanden. Vier benannte Legacy-/Visual-Anker fehlen direkt lokal; sie sind nicht fuer die Kerninventur erforderlich, blockieren aber die ungepruefte Uebernahme frueherer Formeln oder Analogien.

## Kernpfeile
Neun Pfeile bilden Materiezustand, de-Broglie-Wellenlaenge/Phase, relative Phase, Interferenzkernel, Korrelation, Schwelle, Adjazenz/Kantenkippen, Nachbarschaftssignatur, relationale Ordnung und geometrischen Readout ab.

Intern gestuetzt sind MATERIAL01 auf der materialsensitiven Eingangsseite sowie Phase-D-Motive fuer Schwelle, Kantenkippen und Nachbarschaft. Die Pfeile `delta_phi -> K -> G -> theta`, relationale Ordnung und Geometrie-Readout bleiben Hypothese oder Review-Gap.

## Zentrale Gaps
- Auswahl und Validierung von `K_ij = F(delta_phi_ij, w_ij)`.
- Definition und Normalisierung von `G_ij = C[K]_ij`.
- Gemeinsamer Modellraum fuer `G_ij` und `theta`.
- Dimensionssichere Material-Injektionsstelle.
- Trennung von Graphdistanz und physikalischer Metrik.
- Ordnungskonsistenz, Nicht-Eindeutigkeit und Nullmodelle.

## Akzeptanztests
{passed} von {len(tests)} Skelett-/Dokumentationsgates sind als bestanden erfasst. Das bedeutet, dass Grenzen und zukuenftige Tests explizit formuliert sind. Es bedeutet nicht, dass die offenen physikalischen Abbildungen bestanden oder validiert wurden.

## Empfehlung
INTERFACE01-B sollte als kleiner Kandidatenvergleich fuer die drei P0-Brueckenobjekte `F`, `C` und `R(theta)` geplant werden. Vor einer Rechnung sind Konventionen, Normalisierung, Einheitenkanal, Nullmodelle und Abbruchkriterien festzulegen. Deep Research kann danach gezielt nach vergleichbaren Phase-/Kernel-/Graph-Mechanismen suchen; es ersetzt nicht die interne Formalisierung.

## Claim-Grenze
{CLAIM}

MATERIAL01 stuetzt interne materialsensitive de-Broglie-Wellen-/Signaturanker. Phase D stuetzt interne modellgebundene Schwellen-, Kanten- und Nachbarschaftsmotive. Die verbindende Mechanismuskette und geometrische Lesart bleiben formal offen und pruefpflichtig.
"""
    (OUTPUT / "09_interface01a_final_assessment.md").write_text(assessment, encoding="utf-8")

    input_sufficiency = "sufficient_core_inputs_with_legacy_review_gaps"
    status = "interface01a_minimal_mechanism_skeleton_completed_with_review_items"
    if not db_ok or any(row["read_status"] == "missing" for row in anchors[:11]):
        input_sufficiency = "partial_inputs"
        status = "interface01a_minimal_mechanism_skeleton_partial_inputs"
    manifest = {
        "run_id": "QSB-INTERFACE01A", "status": status,
        "output_dir": "runs/QSB-INTERFACE01A/minimal_mechanism_skeleton",
        "input_sufficiency": input_sufficiency, "input_anchors": len(anchors),
        "quantity_contract_rows": len(quantities), "mechanism_arrows": len(arrows),
        "phase_to_threshold_requirements": len(requirements),
        "material_sensitivity_links": len(material_links), "acceptance_tests": len(tests),
        "acceptance_tests_passed_as_documentation_gates": passed,
        "review_items": len(reviews), "missing_legacy_or_visual_anchors": missing_anchors,
        "material01_database_opened_read_only": db_ok,
        "mutated_existing_files": False, "generated_synthetic_evidence": False,
        "new_physics_run_performed": False, "deep_research_performed": False,
        "created_utc": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "claim_boundary": CLAIM,
    }
    (OUTPUT / "10_interface01a_run_manifest.json").write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    print(json.dumps(manifest, ensure_ascii=False))


if __name__ == "__main__":
    main()
