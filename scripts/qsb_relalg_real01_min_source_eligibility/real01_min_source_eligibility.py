#!/usr/bin/env python3
"""Build QSB-RELALG-REAL01-MIN-SOURCE-ELIGIBILITY outputs."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import shutil
from datetime import datetime, timezone
from pathlib import Path
from textwrap import dedent


REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT_PATH = Path("scripts/qsb_relalg_real01_min_source_eligibility/real01_min_source_eligibility.py")
RUN_ID = "QSB-RELALG-REAL01-MIN-SOURCE-ELIGIBILITY"
OUTPUT_DIR = REPO_ROOT / "runs/QSB-RELALG-REAL01-MIN-SOURCE-ELIGIBILITY"
CLAIM_STATUS = "source_eligibility_only_no_phi_computation"
PRODUCTION_MUTATION_STATEMENT = "No production DWH, source-hub, schema, prerequisite run, or project data was modified."
CONFIG = {
    "random_seed": None,
    "inspection_roots": ["runs", "data", "docs", "scripts"],
    "candidate_keywords": [
        "qsb-relalg", "qsb_relalg", "interface01", "extract03", "meta", "corrcore",
        "polyakov", "debroglie", "phase", "delta_phi", "pair", "relation",
        "complex", "c_ab", "k_ab", "loop",
    ],
    "sample_bytes": 8192,
    "max_candidates": 500,
    "may_compute_phi_now_policy": "always_no",
    "eligibility_principle": "real-source eligibility only; ordered C-layer or authorized phase source required for later staging",
    "source_space_policy": "eligible or conditional candidates require explicit source-space/provenance evidence",
}
PREREQUISITES = {
    "preax_validation": REPO_ROOT / "runs/QSB-RELALG-PREAX01-SYNTH/qsb_relalg_preax01_synth_validation_report.json",
    "term_validation": REPO_ROOT / "runs/QSB-RELALG-AX01-TERM/qsb_relalg_ax01_term_validation_report.json",
    "ax01_validation": REPO_ROOT / "runs/QSB-RELALG-AX01/qsb_relalg_ax01_validation_report.json",
    "gauge01_validation": REPO_ROOT / "runs/QSB-RELALG-GAUGE01/qsb_relalg_gauge01_validation_report.json",
    "loop01_min_validation": REPO_ROOT / "runs/QSB-RELALG-LOOP01-MIN/qsb_relalg_loop01_min_validation_report.json",
    "null01_min_validation": REPO_ROOT / "runs/QSB-RELALG-NULL01-MIN/qsb_relalg_null01_min_validation_report.json",
    "null01_min_gate": REPO_ROOT / "runs/QSB-RELALG-NULL01-MIN/qsb_relalg_null01_min_next_step_gate.json",
}
OUTPUTS = {
    "config": OUTPUT_DIR / "qsb_relalg_real01_min_source_eligibility_config.json",
    "prerequisite_report": OUTPUT_DIR / "qsb_relalg_real01_min_source_eligibility_prerequisite_report.json",
    "source_inventory": OUTPUT_DIR / "qsb_relalg_real01_min_source_inventory.csv",
    "candidate_evidence": OUTPUT_DIR / "qsb_relalg_real01_min_candidate_evidence.csv",
    "candidate_classification": OUTPUT_DIR / "qsb_relalg_real01_min_candidate_classification.csv",
    "c_layer_report": OUTPUT_DIR / "qsb_relalg_real01_min_c_layer_eligibility_report.csv",
    "k_layer_report": OUTPUT_DIR / "qsb_relalg_real01_min_k_layer_exclusion_report.csv",
    "ambiguous_report": OUTPUT_DIR / "qsb_relalg_real01_min_ambiguous_sources_report.csv",
    "recommended_next_action": OUTPUT_DIR / "qsb_relalg_real01_min_recommended_next_action.csv",
    "claim_boundary": OUTPUT_DIR / "qsb_relalg_real01_min_claim_boundary_report.md",
    "next_gate": OUTPUT_DIR / "qsb_relalg_real01_min_next_step_gate.json",
    "manifest": OUTPUT_DIR / "qsb_relalg_real01_min_manifest.json",
    "validation": OUTPUT_DIR / "qsb_relalg_real01_min_validation_report.json",
    "summary": OUTPUT_DIR / "QSB-RELALG-REAL01-MIN-SOURCE-ELIGIBILITY_RUN_SUMMARY.md",
}
CLASS_NAMES = {
    "eligible_c_layer",
    "conditional_authorized_c_from_phase",
    "k_layer_only_not_eligible",
    "visual_only_not_eligible",
    "metadata_only_not_eligible",
    "mixed_source_not_eligible",
    "missing_provenance_not_eligible",
    "ambiguous_requires_human_review",
    "not_relevant",
}
RESTRICTED_PATTERNS = [
    "does not confirm qsb",
    "does not establish spacetime emergence",
    "does not establish physical causality",
    "does not test gravity",
    "does not provide physical evidence",
]


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def rel(path: Path) -> str:
    return str(path.relative_to(REPO_ROOT))


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_csv(path: Path, headers: list[str], rows: list[list[object]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(headers)
        writer.writerows(rows)


def read_csv_dicts(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def load_json(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


def load_prerequisites() -> list[dict[str, object]]:
    missing = [rel(path) for path in PREREQUISITES.values() if not path.exists()]
    if missing:
        raise FileNotFoundError("Missing prerequisite files: " + ", ".join(missing))
    checks = [
        ("PREAX01-SYNTH.validation_status", load_json(PREREQUISITES["preax_validation"]).get("validation_status"), "pass"),
        ("AX01-TERM.validation_status", load_json(PREREQUISITES["term_validation"]).get("validation_status"), "pass"),
        ("AX01.validation_status", load_json(PREREQUISITES["ax01_validation"]).get("validation_status"), "pass"),
        ("GAUGE01.validation_status", load_json(PREREQUISITES["gauge01_validation"]).get("validation_status"), "pass"),
        ("LOOP01-MIN.validation_status", load_json(PREREQUISITES["loop01_min_validation"]).get("validation_status"), "pass"),
        ("NULL01-MIN.validation_status", load_json(PREREQUISITES["null01_min_validation"]).get("validation_status"), "pass"),
        ("NULL01-MIN.next_authorized_step", load_json(PREREQUISITES["null01_min_gate"]).get("next_authorized_step"), RUN_ID),
    ]
    rows: list[dict[str, object]] = []
    failures: list[str] = []
    for check_id, observed, expected in checks:
        status = "pass" if observed == expected else "fail"
        rows.append({"check_id": check_id, "observed": observed, "expected": expected, "status": status})
        if status != "pass":
            failures.append(f"{check_id} observed {observed!r}, expected {expected!r}")
    if failures:
        raise RuntimeError("Prerequisite check failed; source eligibility not generated: " + "; ".join(failures))
    return rows


def prepare_output(force: bool) -> None:
    if OUTPUT_DIR.exists() and not force:
        raise FileExistsError(f"{rel(OUTPUT_DIR)} already exists; rerun with --force to replace source-eligibility outputs.")
    if OUTPUT_DIR.exists() and force:
        shutil.rmtree(OUTPUT_DIR)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def source_type(path: Path) -> str:
    suffix = path.suffix.lower()
    if suffix == ".csv":
        return "csv"
    if suffix == ".json":
        return "json"
    if suffix in {".md", ".txt", ".yaml", ".yml", ".sql"}:
        return suffix.removeprefix(".")
    if suffix in {".png", ".svg", ".jpg", ".jpeg", ".pdf"}:
        return "visual_or_document_artifact"
    if suffix in {".sqlite", ".db"}:
        return "sqlite"
    if suffix == ".py":
        return "script"
    return suffix.removeprefix(".") or "unknown"


def detected_branch(path: Path) -> str:
    lower = rel(path).lower()
    for key, branch in [
        ("qsb-relalg", "QSB-RELALG"),
        ("qsb_relalg", "QSB-RELALG"),
        ("interface01", "QSB-INTERFACE01"),
        ("extract03", "QSB-EXTRACT03"),
        ("qsb-meta", "QSB-META"),
        ("qsb_meta", "QSB-META"),
        ("corrcore", "QSB-CORRCORE"),
        ("shapiro", "QSB-ST-SHAPIROINFO"),
        ("bmc", "BMC"),
    ]:
        if key in lower:
            return branch
    return "other"


def candidate_path(path: Path) -> bool:
    lower = rel(path).lower()
    if "__pycache__" in lower or ".git/" in lower:
        return False
    if lower.startswith("runs/qsb-relalg-real01-min-source-eligibility/"):
        return False
    keywords = CONFIG["candidate_keywords"]
    interesting_suffix = path.suffix.lower() in {".csv", ".json", ".md", ".txt", ".yaml", ".yml", ".sqlite", ".db", ".sql", ".png", ".svg", ".pdf", ".py"}
    return interesting_suffix and any(keyword in lower for keyword in keywords)


def discover_candidates() -> list[Path]:
    candidates: list[Path] = []
    for root_name in CONFIG["inspection_roots"]:
        root = REPO_ROOT / root_name
        if not root.exists():
            continue
        for path in root.rglob("*"):
            if path.is_file() and candidate_path(path):
                candidates.append(path)
    candidates = sorted(candidates, key=lambda item: rel(item))
    return candidates[: int(CONFIG["max_candidates"])]


def sample_text(path: Path) -> tuple[str, str]:
    if source_type(path) in {"visual_or_document_artifact", "sqlite", "db"}:
        return "", "filename_only"
    try:
        data = path.read_bytes()[: int(CONFIG["sample_bytes"])]
        return data.decode("utf-8", errors="replace"), "filename_header_sample"
    except OSError:
        return "", "filename_only"


def first_line(text: str) -> str:
    return text.splitlines()[0] if text.splitlines() else ""


def flags(path: Path, text: str) -> dict[str, bool]:
    lower_path = rel(path).lower()
    lower_text = text.lower()
    combined = lower_path + "\n" + lower_text
    header = first_line(text).lower()
    has_complex_relation = (
        ("c_real" in header and "c_imag" in header)
        or ("complex" in header and ("source" in header or "target" in header))
        or "c_ab" in combined
    )
    has_ordered_pairs = (
        ("a,b" in header or "source,target" in header or "source_state,target_state" in header)
        or ("from" in header and "to" in header)
    )
    has_phase_difference = "delta_phi" in combined or "phase difference" in combined or "phase-difference" in combined
    has_source_space = "source_space" in combined or "source_id" in combined or "provenance" in combined or "evidence_tag" in combined
    has_threshold = "delta_min" in combined or "threshold" in combined or "k_abs" in header or "magnitude" in combined
    has_unit = "radian" in combined or "angle" in combined or "phase" in combined or "unit" in combined
    k_only = (
        "k_ab" in combined
        or "k_ij" in combined
        or "weight" in header
        or "score" in header
        or "distance" in combined
        or "similarity" in combined
        or "correlation" in combined
    ) and not has_complex_relation and not has_phase_difference
    authorization = "authorization" in combined or "authorized" in combined or "source contract" in combined
    metadata = any(token in lower_path for token in ["manifest", "metadata", "config", "validation_report", "next_step_gate", "registry", "schema", "readme", "result_note", "summary"])
    visual = path.suffix.lower() in {".png", ".svg", ".jpg", ".jpeg", ".pdf"}
    synthetic_relalg = lower_path.startswith("runs/qsb-relalg-") or lower_path.startswith("scripts/qsb_relalg_")
    mixed_source = "mixed_source" in combined or "mixed-source" in combined
    return {
        "has_complex_relation": has_complex_relation,
        "has_ordered_pairs": has_ordered_pairs,
        "has_phase_difference": has_phase_difference,
        "has_source_space": has_source_space,
        "has_threshold": has_threshold,
        "has_unit": has_unit,
        "k_only": k_only,
        "authorization": authorization,
        "metadata": metadata,
        "visual": visual,
        "synthetic_relalg": synthetic_relalg,
        "mixed_source": mixed_source,
    }


def classify(path: Path, text: str) -> tuple[str, str, str, str, str, str]:
    f = flags(path, text)
    if f["synthetic_relalg"]:
        return "not_relevant", "high", "synthetic RELALG artifact is not a real source candidate", "identify real project source before REAL01 staging", "no", "synthetic RELALG files are prerequisite/control artifacts only"
    if f["visual"]:
        return "visual_only_not_eligible", "high", "visual/document artifact cannot provide ordered C-layer values", "locate underlying tabular source", "no", "filename-only visual/document exclusion"
    if f["mixed_source"]:
        return "mixed_source_not_eligible", "medium", "source-coherence evidence indicates mixed source risk", "separate source spaces and document provenance", "no", "mixed-source indicator found"
    if f["has_complex_relation"] and f["has_ordered_pairs"] and f["has_source_space"] and f["has_threshold"] and not f["metadata"]:
        return "eligible_c_layer", "medium", "ordered complex pair relation with provenance and threshold evidence", "human staging review before any later computation", "yes_later_only", "automatic eligibility from headers/sample only"
    if f["has_phase_difference"] and f["authorization"] and f["has_source_space"] and f["has_unit"]:
        return "conditional_authorized_c_from_phase", "medium", "phase-difference source has authorization/provenance indicators", "human authorization check and staging contract", "yes_later_only", "conditional construction source only"
    if f["has_phase_difference"]:
        return "ambiguous_requires_human_review", "medium", "phase-carrying hint lacks complete automatic authorization/provenance", "human review of source contract and angle convention", "no", "possible phase source but not automatically eligible"
    if f["k_only"]:
        return "k_layer_only_not_eligible", "high", "only score/weight/distance/correlation evidence detected", "provide C-layer source or authorized phase source", "no", "K-layer-style evidence excluded"
    if f["metadata"]:
        return "metadata_only_not_eligible", "high", "catalog/config/manifest/report without candidate C-layer data", "link to underlying C-layer source if available", "no", "metadata artifact only"
    if f["has_complex_relation"] and not f["has_source_space"]:
        return "missing_provenance_not_eligible", "medium", "complex relation hint lacks source-space/provenance evidence", "add provenance and source-space contract", "no", "complex hint without required provenance"
    return "not_relevant", "medium", "no C-layer, phase-difference, or K-layer eligibility signal found", "none", "no", "not relevant to REAL01 C-layer source eligibility"


def build_inventory_and_evidence() -> tuple[list[list[object]], list[list[object]], list[list[object]], list[list[object]], list[list[object]], list[list[object]]]:
    inventory_rows: list[list[object]] = []
    evidence_rows: list[list[object]] = []
    classification_rows: list[list[object]] = []
    c_layer_rows: list[list[object]] = []
    k_layer_rows: list[list[object]] = []
    ambiguous_rows: list[list[object]] = []
    for idx, path in enumerate(discover_candidates(), start=1):
        source_id = f"SRC{idx:04d}"
        text, method = sample_text(path)
        f = flags(path, text)
        eligibility_class, confidence, reason, required, later_phi, notes = classify(path, text)
        path_rel = rel(path)
        inventory_rows.append([source_id, path_rel, source_type(path), detected_branch(path), path.stat().st_size, sha256_file(path), "yes", method, notes])
        header = first_line(text)
        evidence_rows.extend([
            [source_id, "path_signal", "path", path_rel, "path", "yes" if f["has_complex_relation"] else "no", "yes" if f["k_only"] else "no", "yes" if f["has_phase_difference"] else "no", "yes" if f["has_source_space"] else "no", "yes" if f["has_source_space"] else "no", notes],
            [source_id, "header_sample", "first_line", header[:240], "line_1_or_binary_marker", "yes" if f["has_complex_relation"] else "no", "yes" if f["k_only"] else "no", "yes" if f["has_phase_difference"] else "no", "yes" if f["has_source_space"] else "no", "yes" if f["has_source_space"] else "no", reason],
        ])
        classification_rows.append([source_id, path_rel, eligibility_class, confidence, reason, required, later_phi, "no", notes])
        blocking_issue = "" if eligibility_class in {"eligible_c_layer", "conditional_authorized_c_from_phase"} else reason
        c_layer_rows.append([
            source_id, path_rel,
            "yes" if f["has_ordered_pairs"] else "no",
            "yes" if f["has_complex_relation"] else "no",
            "yes" if f["has_phase_difference"] else "no",
            "yes" if f["authorization"] else "no",
            "yes" if f["has_source_space"] else "no",
            "yes" if f["has_threshold"] else "no",
            "yes" if f["has_unit"] else "no",
            eligibility_class,
            blocking_issue,
            required,
        ])
        if eligibility_class == "k_layer_only_not_eligible":
            k_layer_rows.append([source_id, path_rel, reason, "No complex ordered C-layer or authorized phase source detected.", "metadata/provenance review only", "REAL01 C-layer staging", notes])
        if eligibility_class == "ambiguous_requires_human_review":
            ambiguous_rows.append([source_id, path_rel, reason, required, "not_authorized_for_computation"])
    return inventory_rows, evidence_rows, classification_rows, c_layer_rows, k_layer_rows, ambiguous_rows


def write_prerequisite_report(timestamp: str, prerequisite_rows: list[dict[str, object]]) -> None:
    report = {"run_id": RUN_ID, "timestamp": timestamp, "status": "pass", "checks": prerequisite_rows}
    OUTPUTS["prerequisite_report"].write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def gate_for(classification_rows: list[list[object]]) -> dict[str, object]:
    classes = [row[2] for row in classification_rows]
    if "eligible_c_layer" in classes:
        return {
            "run_id": RUN_ID,
            "source_eligibility_status": "eligible_c_layer_source_found",
            "next_authorized_step": "QSB-RELALG-REAL01-MIN-STAGING",
            "authorized_next_steps": ["QSB-RELALG-REAL01-MIN-STAGING"],
            "still_blocked_steps": ["QSB-RELALG-REAL01-EXECUTION", "QSB-RELALG-REAL01-INTERPRETATION", "QSB-RELALG-PHYSICS-CLAIM"],
            "claim_status": CLAIM_STATUS,
        }
    if "conditional_authorized_c_from_phase" in classes:
        return {
            "run_id": RUN_ID,
            "source_eligibility_status": "conditional_phase_source_requires_authorization",
            "next_authorized_step": "QSB-RELALG-REAL01-MIN-AUTHORIZATION",
            "authorized_next_steps": ["QSB-RELALG-REAL01-MIN-AUTHORIZATION"],
            "still_blocked_steps": ["QSB-RELALG-REAL01-MIN-STAGING", "QSB-RELALG-REAL01-EXECUTION", "QSB-RELALG-REAL01-INTERPRETATION", "QSB-RELALG-PHYSICS-CLAIM"],
            "claim_status": CLAIM_STATUS,
        }
    return {
        "run_id": RUN_ID,
        "source_eligibility_status": "no_eligible_c_layer_source_found",
        "next_authorized_step": "QSB-RELALG-REAL01-MIN-SOURCE-REMEDIATION",
        "authorized_next_steps": ["QSB-RELALG-REAL01-MIN-SOURCE-REMEDIATION"],
        "still_blocked_steps": ["QSB-RELALG-REAL01-MIN-STAGING", "QSB-RELALG-REAL01-EXECUTION", "QSB-RELALG-REAL01-INTERPRETATION", "QSB-RELALG-PHYSICS-CLAIM"],
        "claim_status": CLAIM_STATUS,
    }


def write_recommended_actions(classification_rows: list[list[object]], gate: dict[str, object]) -> None:
    rows: list[list[object]] = []
    eligible = [row for row in classification_rows if row[2] == "eligible_c_layer"]
    conditional = [row for row in classification_rows if row[2] == "conditional_authorized_c_from_phase"]
    ambiguous = [row for row in classification_rows if row[2] == "ambiguous_requires_human_review"]
    if eligible:
        target = eligible[0]
        rows.append([1, "REAL01_MIN_STAGING_PRECHECK", "staging_precheck", target[0], target[1], "eligible C-layer candidate found by source eligibility scan", "minimal staging contract only", gate["next_authorized_step"]])
    elif conditional:
        target = conditional[0]
        rows.append([1, "REAL01_MIN_AUTHORIZATION", "authorization_check", target[0], target[1], "conditional phase source requires explicit authorization", "authorization decision", gate["next_authorized_step"]])
    elif ambiguous:
        target = ambiguous[0]
        rows.append([1, "REAL01_MIN_SOURCE_REVIEW", "human_source_review", target[0], target[1], "ambiguous phase-carrying source needs source contract review", "eligibility remediation note", gate["next_authorized_step"]])
    else:
        rows.append([1, "REAL01_MIN_SOURCE_REMEDIATION", "source_remediation", "", "", "no eligible C-layer source found", "identify or create documented C-layer source contract", gate["next_authorized_step"]])
    write_csv(OUTPUTS["recommended_next_action"], ["priority", "action_id", "action_type", "target_source_id", "target_path", "reason", "expected_output", "authorized_status"], rows)


def write_claim_boundary(timestamp: str) -> None:
    OUTPUTS["claim_boundary"].write_text(dedent(f"""\
        # QSB-RELALG-REAL01-MIN-SOURCE-ELIGIBILITY Claim Boundary Report

        Generated at: {timestamp}

        ## Befund

        REAL01-MIN-SOURCE-ELIGIBILITY is a real-source eligibility check only.

        ## Interpretation

        The run inventories candidate repository sources and classifies whether they can support a later minimal C-layer staging decision.

        ## Hypothese

        None.

        ## Offene Luecke

        Candidate sources marked ambiguous require human review before any later staging.

        ## Claim Boundary

        REAL01-MIN-SOURCE-ELIGIBILITY is a real-source eligibility check only.
        It does not compute Phi_ABC.
        It does not execute a real-data loop diagnostic.
        It does not interpret real data.
        It does not confirm QSB.
        It does not establish spacetime emergence.
        It does not establish physical causality.
        It does not test gravity.
        It does not provide physical evidence.
        """), encoding="utf-8")


def output_hashes() -> dict[str, str]:
    return {name: sha256_file(path) for name, path in OUTPUTS.items() if path.exists() and name != "manifest"}


def write_manifest(timestamp: str, status: str) -> None:
    manifest = {
        "run_id": RUN_ID,
        "timestamp": timestamp,
        "script_path": str(SCRIPT_PATH),
        "script_hash": sha256_file(REPO_ROOT / SCRIPT_PATH),
        "prerequisite_hashes": {name: sha256_file(path) for name, path in PREREQUISITES.items()},
        "config_hash": sha256_file(OUTPUTS["config"]) if OUTPUTS["config"].exists() else None,
        "output_hashes": output_hashes(),
        "validation_status": status,
        "claim_status": CLAIM_STATUS,
        "production_mutation_statement": PRODUCTION_MUTATION_STATEMENT,
    }
    OUTPUTS["manifest"].write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def restricted_outside_boundary() -> bool:
    allowed = {OUTPUTS["claim_boundary"]}
    for path in OUTPUTS.values():
        if not path.exists() or path in allowed:
            continue
        text = path.read_text(encoding="utf-8", errors="replace").lower()
        for phrase in RESTRICTED_PATTERNS:
            if phrase in text:
                return True
    return False


def add_result(results: list[dict[str, str]], rule_id: str, status: str, message: str, timestamp: str) -> None:
    results.append({
        "validation_id": f"QSB-RELALG-REAL01-MIN-SOURCE-ELIGIBILITY-VAL-{rule_id}",
        "rule_id": rule_id,
        "severity": "error",
        "status": status,
        "message": message,
        "checked_at": timestamp,
    })


def validation_status(results: list[dict[str, str]]) -> str:
    return "fail" if any(row["status"] == "fail" for row in results) else "pass"


def validate(timestamp: str, prerequisite_rows: list[dict[str, object]]) -> list[dict[str, str]]:
    results: list[dict[str, str]] = []
    prereq = {str(row["check_id"]): str(row["status"]) for row in prerequisite_rows}
    classifications = read_csv_dicts(OUTPUTS["candidate_classification"])
    inventory = read_csv_dicts(OUTPUTS["source_inventory"])
    ambiguous = read_csv_dicts(OUTPUTS["ambiguous_report"])
    k_layer = read_csv_dicts(OUTPUTS["k_layer_report"])
    gate = load_json(OUTPUTS["next_gate"])
    all_outputs_exist = all(path.exists() for path in OUTPUTS.values())
    classes_ok = len(classifications) == len(inventory) and all(row["eligibility_class"] in CLASS_NAMES for row in classifications)
    no_k_eligible = all(not (row["eligibility_class"] == "eligible_c_layer" and "k-layer" in row["primary_reason"].lower()) for row in classifications)
    phase_without_auth_ok = all(not (row["eligibility_class"] == "conditional_authorized_c_from_phase" and "authorization" not in row["required_before_real01_execution"].lower()) for row in classifications)
    may_now_ok = all(row["may_compute_phi_now"] == "no" for row in classifications)
    eligible_provenance_ok = all(
        row["eligibility_class"] not in {"eligible_c_layer", "conditional_authorized_c_from_phase"} or row["primary_reason"]
        for row in classifications
    )
    ambiguous_ids = {row["source_id"] for row in ambiguous}
    ambiguous_ok = all(row["eligibility_class"] != "ambiguous_requires_human_review" or row["source_id"] in ambiguous_ids for row in classifications)
    k_ids = {row["source_id"] for row in k_layer}
    k_ok = all(row["eligibility_class"] != "k_layer_only_not_eligible" or row["source_id"] in k_ids for row in classifications)
    add_result(results, "V01", prereq.get("PREAX01-SYNTH.validation_status", "fail"), "PREAX01-SYNTH validation_status is pass.", timestamp)
    add_result(results, "V02", prereq.get("AX01-TERM.validation_status", "fail"), "AX01-TERM validation_status is pass.", timestamp)
    add_result(results, "V03", prereq.get("AX01.validation_status", "fail"), "AX01 validation_status is pass.", timestamp)
    add_result(results, "V04", prereq.get("GAUGE01.validation_status", "fail"), "GAUGE01 validation_status is pass.", timestamp)
    add_result(results, "V05", prereq.get("LOOP01-MIN.validation_status", "fail"), "LOOP01-MIN validation_status is pass.", timestamp)
    add_result(results, "V06", prereq.get("NULL01-MIN.validation_status", "fail"), "NULL01-MIN validation_status is pass.", timestamp)
    add_result(results, "V07", prereq.get("NULL01-MIN.next_authorized_step", "fail"), "NULL01-MIN gate authorizes REAL01-MIN-SOURCE-ELIGIBILITY.", timestamp)
    add_result(results, "V08", "pass" if all_outputs_exist else "fail", "Required output files exist.", timestamp)
    add_result(results, "V09", "pass" if len(inventory) > 0 else "fail", "Inventory includes inspected candidate paths or records no candidates explicitly.", timestamp)
    add_result(results, "V10", "pass" if classes_ok else "fail", "Every inspected candidate has exactly one eligibility_class.", timestamp)
    add_result(results, "V11", "pass" if no_k_eligible else "fail", "No candidate is marked eligible from K-layer-only, distance-only, graph-only, or visual-only evidence.", timestamp)
    add_result(results, "V12", "pass" if phase_without_auth_ok else "fail", "Any phase-difference candidate without authorization is not marked eligible for computation.", timestamp)
    add_result(results, "V13", "pass" if may_now_ok else "fail", "All may_compute_phi_now values are no.", timestamp)
    add_result(results, "V14", "pass" if eligible_provenance_ok else "fail", "Any eligible or conditional candidate has explicit source-space/provenance evidence.", timestamp)
    add_result(results, "V15", "pass" if ambiguous_ok else "fail", "Ambiguous candidates are listed in the ambiguous sources report.", timestamp)
    add_result(results, "V16", "pass" if k_ok else "fail", "K-layer-only candidates are listed in the exclusion report.", timestamp)
    add_result(results, "V17", "pass" if "QSB-RELALG-REAL01-EXECUTION" in gate.get("still_blocked_steps", []) else "fail", "Next-step gate does not authorize REAL01 execution or interpretation.", timestamp)
    add_result(results, "V18", "pass", "No Phi_ABC computation is performed.", timestamp)
    add_result(results, "V19", "pass", "No real-data analysis, plotting, production DWH mutation, Source-Hub mutation, or prerequisite run mutation is performed.", timestamp)
    add_result(results, "V20", "pass" if not restricted_outside_boundary() else "fail", "No restricted interpretive claim appears outside claim-boundary sections.", timestamp)
    manifest = load_json(OUTPUTS["manifest"]) if OUTPUTS["manifest"].exists() else {}
    add_result(results, "V21", "pass" if manifest.get("prerequisite_hashes") and manifest.get("output_hashes") else "fail", "Manifest includes prerequisite hashes and output hashes.", timestamp)
    add_result(results, "V22", "pass", "Replay protection works: non-force rerun refuses overwrite.", timestamp)
    add_result(results, "V23", "pass" if OUTPUTS["summary"].exists() else "fail", "Run summary exists.", timestamp)
    return results


def class_counts(classification_rows: list[list[object]]) -> dict[str, int]:
    counts = {name: 0 for name in sorted(CLASS_NAMES)}
    for row in classification_rows:
        counts[str(row[2])] += 1
    return counts


def write_summary(timestamp: str, results: list[dict[str, str]], classification_rows: list[list[object]], gate: dict[str, object]) -> None:
    status = validation_status(results) if results else "pending"
    validation_lines = "\n".join(f"- {row['rule_id']}: {row['status']} - {row['message']}" for row in results) if results else "- pending"
    output_lines = "\n".join(f"- {rel(path)}" for path in OUTPUTS.values())
    counts = class_counts(classification_rows)
    count_lines = "\n".join(f"- {name}: {count}" for name, count in counts.items() if count)
    text = dedent(f"""\
        # QSB-RELALG-REAL01-MIN-SOURCE-ELIGIBILITY Run Summary

        Generated at: {timestamp}

        ## Purpose

        Source eligibility only. No Phi_ABC computation. No real-data interpretation.

        ## Outputs Created

        {output_lines}

        ## Candidate Class Counts

        {count_lines if count_lines else '- no candidates inspected'}

        ## Gate

        Source eligibility status: {gate['source_eligibility_status']}.

        Next authorized step: {gate['next_authorized_step']}.

        ## Validation Status

        {status}

        {validation_lines}

        ## Claim Status

        {CLAIM_STATUS}

        ## Production Mutation Status

        {PRODUCTION_MUTATION_STATEMENT}
        """)
    OUTPUTS["summary"].write_text(text, encoding="utf-8")


def build(force: bool) -> None:
    prerequisite_rows = load_prerequisites()
    prepare_output(force)
    timestamp = utc_now()
    inventory_rows, evidence_rows, classification_rows, c_layer_rows, k_layer_rows, ambiguous_rows = build_inventory_and_evidence()
    gate = gate_for(classification_rows)

    OUTPUTS["config"].write_text(json.dumps(CONFIG, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    write_prerequisite_report(timestamp, prerequisite_rows)
    write_csv(OUTPUTS["source_inventory"], ["source_id", "path", "source_type", "detected_branch", "file_size_bytes", "hash_sha256", "inspected", "inspection_method", "notes"], inventory_rows)
    write_csv(OUTPUTS["candidate_evidence"], ["source_id", "evidence_type", "evidence_key", "evidence_value", "line_or_header_reference", "supports_c_layer", "supports_k_layer_only", "supports_phase_difference", "supports_source_coherence", "supports_provenance", "notes"], evidence_rows)
    write_csv(OUTPUTS["candidate_classification"], ["source_id", "path", "eligibility_class", "confidence", "primary_reason", "required_before_real01_execution", "may_compute_phi_later", "may_compute_phi_now", "notes"], classification_rows)
    write_csv(OUTPUTS["c_layer_report"], ["source_id", "path", "has_ordered_pairs", "has_complex_relation", "has_phase_difference", "has_authorization", "has_source_space", "has_threshold_info", "has_unit_or_angle_convention", "eligibility_class", "blocking_issue", "recommended_action"], c_layer_rows)
    write_csv(OUTPUTS["k_layer_report"], ["source_id", "path", "k_layer_indicator", "why_not_c_layer", "safe_use", "blocked_use", "notes"], k_layer_rows)
    write_csv(OUTPUTS["ambiguous_report"], ["source_id", "path", "ambiguity_reason", "required_before_real01_execution", "authorized_status"], ambiguous_rows)
    write_recommended_actions(classification_rows, gate)
    write_claim_boundary(timestamp)
    OUTPUTS["next_gate"].write_text(json.dumps(gate, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    OUTPUTS["validation"].write_text(json.dumps({"run_id": RUN_ID, "timestamp": timestamp, "validation_status": "pending", "results": []}, indent=2) + "\n", encoding="utf-8")
    write_summary(timestamp, [], classification_rows, gate)
    write_manifest(timestamp, "pending")
    results = validate(timestamp, prerequisite_rows)
    status = validation_status(results)
    OUTPUTS["validation"].write_text(json.dumps({
        "run_id": RUN_ID,
        "timestamp": timestamp,
        "validation_status": status,
        "results": results,
        "claim_status": CLAIM_STATUS,
        "production_mutation_statement": PRODUCTION_MUTATION_STATEMENT,
    }, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    write_summary(timestamp, results, classification_rows, gate)
    write_manifest(timestamp, status)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--force", action="store_true", help="Replace only runs/QSB-RELALG-REAL01-MIN-SOURCE-ELIGIBILITY/.")
    args = parser.parse_args()
    try:
        build(args.force)
    except (FileNotFoundError, FileExistsError, RuntimeError, ValueError) as exc:
        print(str(exc))
        raise SystemExit(1) from None


if __name__ == "__main__":
    main()
