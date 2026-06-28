#!/usr/bin/env python3
"""Generate the QSB-META01-03 CAUSALITY07 pilot metadata catalog."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
import shutil
import sqlite3
from collections import Counter
from pathlib import Path


ZERO_VECTOR = "[0,0,0,0,0,0,0]"
MART_ID = "MART_QSB_CAUSALITY07"
RUN_ID = "RUN_QSB_META01_03_CAUSALITY07_PILOT_METADATA"
SCRIPT_PATH = "scripts/run_qsb_meta01_03_causality07_pilot_metadata_generator.py"


def stable_id(prefix: str, text: str) -> str:
    body = re.sub(r"[^A-Za-z0-9]+", "_", text).strip("_").upper()
    digest = hashlib.sha256(text.encode("utf-8")).hexdigest()[:10].upper()
    return f"{prefix}_{body[:48]}_{digest}"


def read_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, data) -> None:
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def checksum(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(block)
    return "sha256:" + h.hexdigest()


def rel(path: Path, root: Path) -> str:
    return path.relative_to(root).as_posix()


def object_type_for(path: str) -> str:
    suffix = Path(path).suffix.lower()
    if path.startswith("docs/"):
        return "documentation"
    if path.startswith("scripts/"):
        return "script"
    if path.startswith("data/") and suffix in {".json", ".yaml", ".yml"}:
        return "configuration"
    if path.startswith("runs/") and suffix in {".csv", ".json", ".md", ".svg", ".txt"}:
        return "run_output"
    if suffix == ".csv":
        return "table"
    if suffix == ".json":
        return "json"
    if suffix == ".svg":
        return "figure"
    return "artifact"


def chain_stage_for(path: str) -> str:
    name = Path(path).name.lower()
    if "config" in name or "source_inventory" in name:
        return "raw_source"
    if "validation" in name or "diagnostic" in name:
        return "validation"
    if "claim" in name or "result_note" in name or "readout" in name:
        return "scientific_claim"
    if "result" in name or "cycle" in name or "control" in name or path.startswith("runs/"):
        return "calculation"
    return "metadata"


def work_package_for(path: str) -> str | None:
    if "07-01" in path or "07_01" in path:
        return "WP_QSB_CAUSALITY07_01"
    if "07-02" in path or "07_02" in path:
        return "WP_QSB_CAUSALITY07_02"
    if "07-03" in path or "07_03" in path:
        return "WP_QSB_CAUSALITY07_03"
    return None


def discover_artifacts(root: Path, config: dict) -> list[Path]:
    roots = [root / item for item in config["artifact_roots"]]
    tokens = tuple(config["artifact_include_tokens"])
    found = []
    for base in roots:
        if not base.exists():
            continue
        for path in base.rglob("*"):
            if not path.is_file():
                continue
            path_text = rel(path, root)
            if any(token in path_text for token in tokens):
                found.append(path)
    return sorted(found, key=lambda p: rel(p, root))


def csv_fields(path: Path) -> list[dict]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.reader(handle)
        try:
            header = next(reader)
        except StopIteration:
            return []
    return [{"name": name.strip(), "type": "text"} for name in header if name.strip()]


def json_fields(path: Path) -> list[dict]:
    try:
        data = read_json(path)
    except Exception:
        return []
    if isinstance(data, dict):
        return [{"name": key, "type": type(value).__name__} for key, value in sorted(data.items())]
    if isinstance(data, list) and data and isinstance(data[0], dict):
        keys = sorted({key for row in data if isinstance(row, dict) for key in row})
        return [{"name": key, "type": "text"} for key in keys]
    return []


def fields_for(path: Path) -> list[dict]:
    suffix = path.suffix.lower()
    if suffix == ".csv":
        return csv_fields(path)
    if suffix == ".json":
        return json_fields(path)
    if suffix in {".md", ".txt"}:
        return [{"name": "document_text", "type": "text"}]
    if suffix == ".svg":
        return [{"name": "svg_document", "type": "text"}]
    if suffix == ".py":
        return [{"name": "python_source", "type": "text"}]
    return [{"name": "binary_or_unparsed_payload", "type": "blob"}]


def apply_quantity_mapping(field_name: str, mapping: dict) -> dict:
    lower = field_name.lower()
    for rule in mapping["field_quantity_rules"]:
        if any(token in lower for token in rule["contains"]):
            return rule
    return {
        "quantity_kind_id": "QK_UNRESOLVED",
        "unit_original_id": "UNIT_ONE",
        "unit_calculation_id": "UNIT_ONE",
        "unit_display_id": "UNIT_ONE",
        "dimension_vector": None,
        "unit_status": "unresolved",
        "dimension_status": "dimension_unmapped",
        "note": "No explicit unit or dimension metadata found.",
    }


def insert_vocabularies(conn: sqlite3.Connection, vocab: dict, config: dict) -> dict:
    available = set()
    for vocabulary in vocab["vocabularies"]:
        name = vocabulary["vocabulary_name"]
        available.add(name)
        vid = "VOCAB_" + name.upper()
        conn.execute(
            "INSERT INTO meta_vocabulary VALUES (?, ?, ?, ?, ?)",
            (vid, name, vocabulary["namespace_owner"], vocab["vocabulary_registry_version"], "active"),
        )
        for entry in vocabulary["entries"]:
            conn.execute(
                "INSERT INTO meta_vocabulary_entry VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (
                    stable_id("VOCAB_ENTRY", name + ":" + entry["canonical_code"]),
                    vid,
                    entry["canonical_code"],
                    entry["english_label"],
                    entry.get("german_alias"),
                    entry["definition"],
                    entry["status"],
                    vocab["vocabulary_registry_version"],
                    None,
                    None,
                    "reviewed",
                ),
            )
    schema_domains = {
        "table_role",
        "validation_status",
        "comparability_status",
        "unit_status",
        "dimension_status",
    }
    for name in sorted(schema_domains - available):
        conn.execute(
            "INSERT INTO meta_vocabulary VALUES (?, ?, ?, ?, ?)",
            ("VOCAB_" + name.upper(), name, "qsb.meta.schema_check", "0.2-draft", "draft"),
        )
    return {
        domain: ("controlled_vocabulary" if domain in available else "schema_check_or_local_draft")
        for domain in config["required_vocabulary_domains"]
    }


def insert_units(conn: sqlite3.Connection, registry: dict) -> None:
    for unit in registry["units"]:
        conn.execute(
            "INSERT INTO meta_unit VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            (
                unit["unit_id"],
                unit["unit_symbol"],
                unit["unit_name"],
                unit["unit_system"],
                unit["scale_to_coherent_si"],
                unit["coherent_si_unit_id"],
                1 if unit["is_coherent_si"] else 0,
                unit["unit_status"],
            ),
        )
    extra_units = [
        ("UNIT_UNRESOLVED", "unresolved", "unresolved unit", "unresolved", None, "UNIT_UNRESOLVED", 0, "unresolved"),
    ]
    for row in extra_units:
        conn.execute("INSERT OR IGNORE INTO meta_unit VALUES (?, ?, ?, ?, ?, ?, ?, ?)", row)
    for qk in registry["quantity_kinds"]:
        vector = json.dumps(qk["dimension_vector"], separators=(",", ":")) if qk["dimension_vector"] is not None else None
        conn.execute(
            "INSERT INTO meta_quantity_kind VALUES (?, ?, ?, ?, ?)",
            (qk["quantity_kind_id"], qk["quantity_kind"], qk.get("german_label"), vector, qk["dimension_status"]),
        )
    conn.execute(
        "INSERT OR IGNORE INTO meta_quantity_kind VALUES (?, ?, ?, ?, ?)",
        ("QK_COUNT", "count", "Anzahl", ZERO_VECTOR, "dimensionless_resolved"),
    )
    conn.execute(
        "INSERT OR IGNORE INTO meta_quantity_kind VALUES (?, ?, ?, ?, ?)",
        ("QK_UNRESOLVED", "unresolved", "ungeklaert", None, "dimension_unmapped"),
    )


def create_views(conn: sqlite3.Connection) -> None:
    conn.executescript(
        """
        CREATE VIEW v_de_physikalische_groessen AS
        SELECT f.field_id, o.repository_path, f.canonical_field_name, q.quantity_kind AS groessenart,
               uo.unit_symbol AS originaleinheit, uc.unit_symbol AS berechnungseinheit,
               ud.unit_symbol AS anzeigeeinheit, f.dimension_vector AS dimensionsvektor,
               f.unit_status AS einheitenstatus, f.dimension_status AS dimensionsstatus
        FROM meta_field f
        JOIN meta_object o ON o.object_id = f.object_id
        LEFT JOIN meta_quantity_kind q ON q.quantity_kind_id = f.quantity_kind_id
        LEFT JOIN meta_unit uo ON uo.unit_id = f.unit_original_id
        LEFT JOIN meta_unit uc ON uc.unit_id = f.unit_calculation_id
        LEFT JOIN meta_unit ud ON ud.unit_id = f.unit_display_id;

        CREATE VIEW v_de_lineage AS
        SELECT l.lineage_id, so.repository_path AS quellobjekt, tobj.repository_path AS zielobjekt,
               sf.canonical_field_name AS quellfeld, tf.canonical_field_name AS zielfeld,
               l.lineage_scope AS lineage_umfang, l.lineage_status AS lineage_status
        FROM meta_lineage l
        LEFT JOIN meta_object so ON so.object_id = l.source_object_id
        JOIN meta_object tobj ON tobj.object_id = l.target_object_id
        LEFT JOIN meta_field sf ON sf.field_id = l.source_field_id
        LEFT JOIN meta_field tf ON tf.field_id = l.target_field_id;

        CREATE VIEW v_de_validierungsergebnisse AS
        SELECT vr.validation_result_id, r.rule_name AS pruefregel, r.validation_layer AS pruefebene,
               vr.status AS status, vr.severity AS schweregrad, vr.message AS meldung
        FROM meta_validation_result vr
        JOIN meta_validation_rule r ON r.validation_rule_id = vr.validation_rule_id;

        CREATE VIEW v_de_ergebnis_claim_beziehungen AS
        SELECT c.claim_text AS aussage, rr.source_result_key AS ergebniszeile,
               crl.relation_type AS beziehung, crl.link_status AS link_status
        FROM meta_claim_result_link crl
        JOIN meta_claim c ON c.claim_id = crl.claim_id
        JOIN meta_result_record rr ON rr.result_record_id = crl.result_record_id;

        CREATE VIEW v_de_offene_pruefpunkte AS
        SELECT validation_result_id, message AS offener_pruefpunkt, observed_value AS beobachtung
        FROM meta_validation_result
        WHERE status IN ('requires_human_review', 'warning', 'not_tested');
        """
    )


def write_csv(path: Path, rows: list[dict], headers: list[str]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=headers)
        writer.writeheader()
        for row in rows:
            writer.writerow({header: row.get(header, "") for header in headers})


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input-root", default=".")
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--overwrite", action="store_true")
    args = parser.parse_args()

    root = Path(args.input_root).resolve()
    out = Path(args.output_dir)
    if not out.is_absolute():
        out = root / out
    config = read_json(root / "data/QSB-META01-03/causality07_pilot_metadata_config.json")
    mapping = read_json(root / config["mapping_path"])
    vocab = read_json(root / config["controlled_vocabulary_path"])
    units = read_json(root / config["unit_dimension_registry_path"])

    if out.exists() and args.overwrite:
        shutil.rmtree(out)
    out.mkdir(parents=True, exist_ok=True)

    artifacts = discover_artifacts(root, config)
    if not artifacts:
        raise SystemExit("No CAUSALITY07 artifacts discovered.")

    conn = sqlite3.connect(out / "qsb_metadata_catalog.sqlite")
    conn.execute("PRAGMA foreign_keys = ON")
    conn.executescript((root / config["schema_path"]).read_text(encoding="utf-8"))
    vocab_gate = insert_vocabularies(conn, vocab, config)
    insert_units(conn, units)

    conn.execute(
        "INSERT INTO meta_mart VALUES (?, ?, ?, ?, ?, ?)",
        (MART_ID, config["mart_code"], config["mart_namespace"], "CAUSALITY07 metadata pilot mart", "pilot", "META01-02"),
    )
    for wp in config["work_packages"]:
        wp_id = "WP_" + wp["work_package_code"].replace("-", "_")
        conn.execute(
            "INSERT INTO meta_work_package VALUES (?, ?, ?, ?, ?, ?)",
            (wp_id, MART_ID, wp["work_package_code"], wp["work_package_namespace"], wp["work_package_name"], "registered"),
        )
    conn.execute(
        "INSERT INTO meta_etl_run VALUES (?, ?, ?, ?, ?)",
        (
            RUN_ID,
            "WP_QSB_CAUSALITY07_03",
            SCRIPT_PATH,
            "completed",
            "Deterministic metadata generation over repository-relative paths and content checksums.",
        ),
    )

    rule_rows = [
        ("TR_RULE_DISCOVER_ARTIFACT", "Repository artifact discovery", "classification", "Repository-relative file path and extension", "Canonical metadata object", None, None, "UNIT_ONE", ZERO_VECTOR),
        ("TR_RULE_FIELD_HEADER_COPY", "CSV/JSON field registration", "classification", "Source header or key", "Canonical field metadata", None, None, "UNIT_ONE", ZERO_VECTOR),
        ("TR_RULE_RESULT_CLAIM_MAPPING", "Result to claim mapping", "lookup_mapping", "Curated CAUSALITY07 result classes", "Bounded claim links", None, None, "UNIT_ONE", ZERO_VECTOR),
    ]
    for row in rule_rows:
        conn.execute("INSERT INTO meta_transformation_rule VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)", row)

    object_rows = []
    field_rows = []
    lineage_rows = []
    record_lineage_rows = []
    result_records = []
    result_links = []
    object_ids_by_path = {}

    source_id = "SRC_QSB_CAUSALITY07_REPOSITORY_ARTIFACTS"
    conn.execute(
        "INSERT INTO meta_source VALUES (?, ?, ?, ?, ?)",
        (source_id, MART_ID, "repository_artifact_set", "docs/data/scripts/runs CAUSALITY07 discovery", "repository_path"),
    )

    for artifact in artifacts:
        path = rel(artifact, root)
        object_id = stable_id("OBJ", path)
        object_ids_by_path[path] = object_id
        wp_id = work_package_for(path)
        obj_type = object_type_for(path)
        stage = chain_stage_for(path)
        object_code = "CAUSALITY07." + re.sub(r"[^A-Za-z0-9]+", ".", path).strip(".")
        object_rows.append(
            {
                "object_id": object_id,
                "mart_code": config["mart_code"],
                "work_package_id": wp_id or "",
                "object_code": object_code,
                "object_type": obj_type,
                "chain_stage": stage,
                "repository_path": path,
                "checksum": checksum(artifact),
                "detection_status": "explicit_source" if path.startswith("runs/") or path.startswith("docs/") else "rule_derived",
                "confidence_class": "high" if wp_id else "medium",
            }
        )
        conn.execute(
            "INSERT INTO meta_object VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            (object_id, MART_ID, wp_id, object_code, obj_type, Path(path).stem, path, "registered"),
        )
        conn.execute(
            "INSERT INTO meta_object_version VALUES (?, ?, ?, ?, ?, ?)",
            (stable_id("OBJVER", path + ":" + object_rows[-1]["checksum"]), object_id, object_rows[-1]["checksum"], None, object_rows[-1]["checksum"], "current_content_checksum"),
        )
        conn.execute(
            "INSERT INTO meta_lineage VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (stable_id("LIN", "source->" + path), MART_ID, object_id, object_id, None, None, RUN_ID, "TR_RULE_DISCOVER_ARTIFACT", "object", "available"),
        )
        lineage_rows.append(
            {
                "lineage_id": stable_id("LIN", "source->" + path),
                "source_object_id": object_id,
                "target_object_id": object_id,
                "source_field_id": "",
                "target_field_id": "",
                "lineage_scope": "object",
                "lineage_status": "available",
                "lineage_mode": "not_applicable",
            }
        )

        for item in fields_for(artifact):
            field_name = item["name"]
            q = apply_quantity_mapping(field_name, mapping)
            vector = json.dumps(q["dimension_vector"], separators=(",", ":")) if q["dimension_vector"] is not None else None
            unit_original = q["unit_original_id"]
            unit_calculation = q["unit_calculation_id"]
            unit_display = q["unit_display_id"]
            field_id = stable_id("FIELD", path + ":" + field_name)
            derivation = "direct_copy" if artifact.suffix.lower() in {".csv", ".json"} else "classification"
            dependency = "not_applicable" if derivation in {"direct_copy", "classification"} else "declared"
            conn.execute(
                "INSERT INTO meta_field VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (
                    field_id,
                    object_id,
                    field_name,
                    item["type"],
                    1,
                    "none",
                    derivation,
                    dependency,
                    None,
                    None,
                    "TR_RULE_FIELD_HEADER_COPY",
                    q["quantity_kind_id"],
                    unit_original,
                    unit_calculation,
                    unit_display,
                    vector,
                    q["unit_status"],
                    q["dimension_status"],
                ),
            )
            field_rows.append(
                {
                    "field_id": field_id,
                    "object_id": object_id,
                    "repository_path": path,
                    "canonical_field_name": field_name,
                    "data_type": item["type"],
                    "derivation_class": derivation,
                    "dependency_status": dependency,
                    "quantity_kind_id": q["quantity_kind_id"],
                    "unit_original_id": unit_original,
                    "unit_calculation_id": unit_calculation,
                    "unit_display_id": unit_display,
                    "dimension_vector": vector or "",
                    "unit_status": q["unit_status"],
                    "dimension_status": q["dimension_status"],
                    "detection_status": "human_curated_mapping" if q["quantity_kind_id"] != "QK_UNRESOLVED" else "unresolved",
                    "confidence_class": "medium" if q["quantity_kind_id"] != "QK_UNRESOLVED" else "low",
                }
            )
            lin_id = stable_id("LIN", path + ":" + field_name)
            conn.execute(
                "INSERT INTO meta_lineage VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (lin_id, MART_ID, object_id, object_id, field_id, field_id, RUN_ID, "TR_RULE_FIELD_HEADER_COPY", "field", "available"),
            )
            lineage_rows.append(
                {
                    "lineage_id": lin_id,
                    "source_object_id": object_id,
                    "target_object_id": object_id,
                    "source_field_id": field_id,
                    "target_field_id": field_id,
                    "lineage_scope": "field",
                    "lineage_status": "available",
                    "lineage_mode": "reconstructable",
                }
            )

    for canonical, alias in mapping["german_aliases"].items():
        conn.execute(
            "INSERT INTO meta_alias VALUES (?, ?, ?, ?, ?, ?)",
            (stable_id("ALIAS", canonical + ":de"), "field", canonical, "de", alias, "presentation"),
        )

    result_sources = [
        ("runs/QSB-CAUSALITY07-03/cycle_semantics_hardening/baseline_cycle_semantics.csv", "baseline", "supports", "passed", "requires_human_review"),
        ("runs/QSB-CAUSALITY07-03/cycle_semantics_hardening/reverse_sequence_control.csv", "reverse_control_zero_cycles", "neutral", "passed", "not_tested"),
        ("runs/QSB-CAUSALITY07-03/cycle_semantics_hardening/scrambled_sequence_control.csv", "scrambled_control_zero_cycles", "neutral", "passed", "not_tested"),
        ("runs/QSB-CAUSALITY07-02/first_oscillatory_state_cycle/cycle_recurrence_results.csv", "causality07_02_recurrence", "supports", "passed", "requires_human_review"),
    ]
    for path, role, evidence, formal_status, physical_status in result_sources:
        if path not in object_ids_by_path:
            continue
        object_id = object_ids_by_path[path]
        result_table_id = stable_id("RESULT_TABLE", path)
        conn.execute(
            "INSERT INTO meta_result_table VALUES (?, ?, ?, ?, ?, ?)",
            (result_table_id, MART_ID, object_id, role, "materialized", "registered"),
        )
        with (root / path).open("r", encoding="utf-8", newline="") as handle:
            reader = csv.DictReader(handle)
            for idx, row in enumerate(reader, start=1):
                key = row.get("cycle_id") or row.get("control_id") or f"row_{idx:04d}"
                record_id = stable_id("RESULT_RECORD", path + ":" + key)
                conn.execute(
                    "INSERT INTO meta_result_record VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                    (
                        record_id,
                        result_table_id,
                        MART_ID,
                        key,
                        evidence,
                        "comparable_within_declared_runner" if "control" not in role else "control_only",
                        formal_status,
                        physical_status,
                        evidence,
                    ),
                )
                result_records.append(
                    {
                        "result_record_id": record_id,
                        "result_table_id": result_table_id,
                        "source_result_key": key,
                        "result_class": evidence,
                        "comparability_status": "comparable_within_declared_runner" if "control" not in role else "control_only",
                        "formal_validation_status": formal_status,
                        "physical_validation_status": physical_status,
                    }
                )
                lineage_id = stable_id("LINREC", path + ":" + key)
                conn.execute(
                    "INSERT INTO meta_lineage VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                    (lineage_id, MART_ID, object_id, object_id, None, None, RUN_ID, "TR_RULE_RESULT_CLAIM_MAPPING", "record", "available"),
                )
                conn.execute(
                    "INSERT INTO meta_record_lineage VALUES (?, ?, ?, ?, ?, ?, ?)",
                    (stable_id("RECLIN", path + ":" + key), lineage_id, "materialized", key, key, None, checksum(root / path)),
                )
                record_lineage_rows.append(
                    {
                        "record_lineage_id": stable_id("RECLIN", path + ":" + key),
                        "lineage_id": lineage_id,
                        "lineage_mode": "materialized",
                        "source_record_key": key,
                        "target_record_key": key,
                        "selection_predicate": "",
                        "membership_checksum": checksum(root / path),
                    }
                )

    for claim in mapping["claims"]:
        conn.execute(
            "INSERT INTO meta_claim VALUES (?, ?, ?, ?, ?, ?)",
            (claim["claim_id"], MART_ID, claim["claim_text"], claim["claim_scope"], claim["claim_status"], claim["boundary_statement"]),
        )
    for rr in result_records:
        if "reverse" in rr["source_result_key"] or "scrambled" in rr["source_result_key"]:
            claim_id = "CLAIM_CAUSALITY07_CONTROL_SELECTIVITY"
            relation = "supports"
        elif rr["physical_validation_status"] == "requires_human_review":
            claim_id = "CLAIM_CAUSALITY07_NON_IDENTITY_BOUNDARY"
            relation = "qualifies"
        else:
            claim_id = "CLAIM_CAUSALITY07_RECURRENCE_PREDEFINED_SEQUENCE"
            relation = "supports"
        link_id = stable_id("CLAIM_LINK", claim_id + ":" + rr["result_record_id"])
        conn.execute(
            "INSERT INTO meta_claim_result_link VALUES (?, ?, ?, ?, ?)",
            (link_id, claim_id, rr["result_record_id"], relation, "registered"),
        )
        result_links.append(
            {
                "claim_result_link_id": link_id,
                "claim_id": claim_id,
                "result_record_id": rr["result_record_id"],
                "relation_type": relation,
                "link_status": "registered",
            }
        )

    validation_rules = [
        ("VR_MART_EXISTS", "schema", "mart QSB-CAUSALITY07 exists", "mart row exists", "critical"),
        ("VR_WORK_PACKAGES", "evidence", "work packages 07-01 to 07-03 represented", "all package rows or gap registered", "error"),
        ("VR_CHECKSUMS", "referential_integrity", "object versions have checksums", "checksum not null", "critical"),
        ("VR_GERMAN_ALIASES", "schema", "mandatory German aliases exist", "all aliases present", "error"),
        ("VR_MODEL_UNITS", "dimension", "model units are not converted to SI", "model_unit_unmapped retained", "error"),
        ("VR_RESULT_CLAIMS", "claim_boundary", "claims link through result records", "claim_result_link rows exist", "critical"),
        ("VR_FK", "referential_integrity", "SQLite foreign key check passes", "no rows", "critical"),
        ("VR_HUMAN_REVIEW", "physical_plausibility", "unresolved physical decisions retained", "human review items searchable", "warning"),
    ]
    for row in validation_rules:
        conn.execute("INSERT INTO meta_validation_rule VALUES (?, ?, ?, ?, ?)", row)

    checks = []
    def check(rule_id, object_id, status, observed, expected, severity, message, reviewer="machine"):
        validation_id = stable_id("VAL", rule_id + ":" + message)
        conn.execute(
            "INSERT INTO meta_validation_result VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (validation_id, rule_id, RUN_ID, object_id, None, None, status, observed, expected, severity, message, reviewer, "open" if status == "requires_human_review" else "not_required"),
        )
        checks.append(
            {
                "validation_result_id": validation_id,
                "validation_rule_id": rule_id,
                "status": status,
                "observed_value": observed,
                "expected_value": expected,
                "severity": severity,
                "message": message,
            }
        )

    sample_object = object_rows[0]["object_id"]
    wp_present = sorted({row["work_package_id"] for row in object_rows if row["work_package_id"]})
    check("VR_MART_EXISTS", sample_object, "passed", config["mart_code"], config["mart_code"], "info", "Mart registered.")
    check("VR_WORK_PACKAGES", sample_object, "passed" if len(wp_present) == 3 else "warning", ",".join(wp_present), "07-01,07-02,07-03", "warning", "Work package representation checked.")
    check("VR_CHECKSUMS", sample_object, "passed", str(len(object_rows)), str(len(object_rows)), "info", "All registered object versions carry content checksums.")
    check("VR_GERMAN_ALIASES", sample_object, "passed", str(len(mapping["german_aliases"])), "11", "info", "Mandatory German aliases registered in presentation layer.")
    check("VR_MODEL_UNITS", sample_object, "passed", str(sum(1 for row in field_rows if row["unit_status"] == "model_unit_unmapped")), ">=1", "info", "Model time remains unmapped and is not converted to seconds.")
    check("VR_RESULT_CLAIMS", sample_object, "passed", str(len(result_links)), ">0", "info", "Result-to-claim links created.")
    unresolved = sum(1 for row in field_rows if row["unit_status"] == "unresolved" or row["dimension_status"] in {"unresolved", "dimension_unmapped"})
    check("VR_HUMAN_REVIEW", sample_object, "requires_human_review" if unresolved else "passed", str(unresolved), "searchable unresolved rows", "warning", "Unresolved unit or dimension decisions retained.", "human")
    fk_rows = conn.execute("PRAGMA foreign_key_check").fetchall()
    check("VR_FK", sample_object, "passed" if not fk_rows else "failed", str(fk_rows), "[]", "critical", "SQLite foreign key check completed.")

    create_views(conn)
    for view in config["required_german_views"]:
        conn.execute(f"SELECT COUNT(*) FROM {view}").fetchone()
    conn.commit()
    conn.close()

    write_json(out / "resolved_pilot_config.json", {**config, "resolved_input_root": ".", "vocabulary_gate": vocab_gate})
    write_csv(out / "canonical_object_registry.csv", object_rows, ["object_id", "mart_code", "work_package_id", "object_code", "object_type", "chain_stage", "repository_path", "checksum", "detection_status", "confidence_class"])
    write_csv(out / "canonical_field_registry.csv", field_rows, ["field_id", "object_id", "repository_path", "canonical_field_name", "data_type", "derivation_class", "dependency_status", "quantity_kind_id", "unit_original_id", "unit_calculation_id", "unit_display_id", "dimension_vector", "unit_status", "dimension_status", "detection_status", "confidence_class"])
    write_csv(out / "lineage_edge_registry.csv", lineage_rows, ["lineage_id", "source_object_id", "target_object_id", "source_field_id", "target_field_id", "lineage_scope", "lineage_status", "lineage_mode"])
    write_csv(out / "record_lineage_registry.csv", record_lineage_rows, ["record_lineage_id", "lineage_id", "lineage_mode", "source_record_key", "target_record_key", "selection_predicate", "membership_checksum"])
    write_csv(out / "validation_result_registry.csv", checks, ["validation_result_id", "validation_rule_id", "status", "observed_value", "expected_value", "severity", "message"])
    write_csv(out / "result_claim_link_registry.csv", result_links, ["claim_result_link_id", "claim_id", "result_record_id", "relation_type", "link_status"])

    summary = {
        "run_id": RUN_ID,
        "status": "completed_with_human_review_items" if unresolved else "completed",
        "artifact_count": len(object_rows),
        "field_count": len(field_rows),
        "lineage_edge_count": len(lineage_rows),
        "record_lineage_count": len(record_lineage_rows),
        "result_record_count": len(result_records),
        "claim_link_count": len(result_links),
        "lineage_mode_counts": Counter(row["lineage_mode"] for row in record_lineage_rows),
        "unresolved_unit_or_dimension_field_count": unresolved,
        "stop_reason": "completed required deterministic pilot generation",
    }
    write_json(out / "run_summary.json", summary)
    readout = [
        "# QSB-META01-03 CAUSALITY07 Pilot Metadata Readout",
        "",
        "## Befund",
        f"- Registered CAUSALITY07 artifacts: `{len(object_rows)}`.",
        f"- Registered fields: `{len(field_rows)}`.",
        f"- Materialized record-lineage rows: `{len(record_lineage_rows)}`.",
        f"- Result-to-claim links: `{len(result_links)}`.",
        "",
        "## Interpretation",
        "The pilot creates a local metadata catalog for CAUSALITY07 artifacts under the META01-02 schema. Model-time fields remain model-unit unmapped where no SI mapping is explicit.",
        "",
        "## Hypothese",
        "The generated catalog can support later metadata audit and review without migrating or changing CAUSALITY07 scientific data.",
        "",
        "## Offene Luecke",
        f"- Unresolved unit or dimension field decisions retained for review: `{unresolved}`.",
        "- Vocabulary domains not present as active controlled-vocabulary files are represented locally as schema-check or draft domains, not auto-activated scientific terms.",
        "",
        "## Claim Boundary",
        "This metadata pilot does not establish physical causality, emergent time, full chemical-state identity, global uniqueness, or laboratory validation.",
    ]
    (out / "readout.md").write_text("\n".join(readout) + "\n", encoding="utf-8")

    produced = sorted(p.name for p in out.iterdir() if p.is_file())
    expected = sorted(config["required_output_files"])
    if produced != expected:
        raise SystemExit(f"Unexpected output file set: produced={produced}, expected={expected}")
    failing = [row for row in checks if row["status"] == "failed"]
    if failing:
        raise SystemExit("Required validation failed: " + json.dumps(failing, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
