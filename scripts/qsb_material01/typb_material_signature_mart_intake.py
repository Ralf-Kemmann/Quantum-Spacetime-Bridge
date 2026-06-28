#!/usr/bin/env python3
"""MATERIAL01 Typ-B materialsensitive signature mart intake."""

from __future__ import annotations

import csv
import hashlib
import json
import re
import shutil
import sqlite3
import sys
import zipfile
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
OUTPUT_DIR = REPO_ROOT / "runs/QSB-MATERIAL01/typb_materialsensitive_signature_mart_intake"
DB_PATH = OUTPUT_DIR / "material01_typb_signature_mart.sqlite"
CSV_DIR = OUTPUT_DIR / "csv"
REPORT_DIR = OUTPUT_DIR / "reports"
EXTRACT_DIR = OUTPUT_DIR / "extract"
TYPEB_ROOT = REPO_ROOT / "numerics/debroglie-phase-bridge/typ_b_analysis"
CLAIM_BOUNDARY = (
    "Evidence anchor for material-sensitive de-Broglie phase/wave/signature "
    "shifts within the QSB working model; not a proof of emergent spacetime "
    "or gravitation."
)

EXPECTED_ATOMIC = ["hydrogen", "sodium", "carbon", "nitrogen", "sulfur", "phosphorus"]
EXPECTED_ISOTOPES = ["1H", "2H", "3H", "84Sr", "86Sr", "87Sr", "88Sr", "12C", "13C"]
ELEMENTS = {
    "hydrogen": "H",
    "sodium": "Na",
    "carbon": "C",
    "nitrogen": "N",
    "sulfur": "S",
    "phosphorus": "P",
}
ISO_SERIES = {"H": "hydrogen", "Sr": "strontium", "C": "carbon"}
TEXT_SUFFIXES = {".csv", ".json", ".md", ".txt", ".yaml", ".yml", ".py"}


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def rel(path: Path) -> str:
    return str(path.relative_to(REPO_ROOT))


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def parse_float(value: str | None) -> float | None:
    if value is None or value == "":
        return None
    try:
        return float(value)
    except ValueError:
        return None


def parse_int(value: str | None) -> int | None:
    if value is None or value == "":
        return None
    try:
        return int(float(value))
    except ValueError:
        return None


def isotope_parts(label: str | None) -> tuple[int | None, str | None]:
    if not label:
        return None, None
    m = re.fullmatch(r"(\d+)([A-Za-z]+)", label.strip())
    if not m:
        return None, None
    return int(m.group(1)), m.group(2)


def canonical_isotope(label: str | None) -> str | None:
    mass, sym = isotope_parts(label)
    if mass is None or sym is None:
        return None
    return f"{mass}{sym[0].upper()}{sym[1:]}"


def detect_role(path: Path) -> str:
    name = path.name.lower()
    if name.endswith("_scan.csv") or name.endswith("_tau_response.csv"):
        return "result_csv"
    if name.endswith("_state.json") or name.endswith("_claims.json"):
        return "result_json"
    if "readout" in name or name.endswith(".md"):
        return "readout"
    if path.suffix == ".py":
        return "runner"
    return "unknown"


def source_kind(path: Path) -> str:
    return "file"


def find_sources() -> list[Path]:
    sources: set[Path] = set()
    if TYPEB_ROOT.exists():
        for p in TYPEB_ROOT.rglob("*"):
            if p.is_file() and p.suffix.lower() in TEXT_SUFFIXES:
                text = rel(p).lower()
                if "debroglie_matter_signature" in text or p.parent.name.startswith("debroglie_matter_signature"):
                    sources.add(p)
    for zname in ("typ_b_analysis.zip", "files.zip"):
        zpath = REPO_ROOT / zname
        if zpath.exists():
            sources.add(zpath)
    return sorted(sources)


def extract_zip_sources(paths: list[Path]) -> list[tuple[Path, str, str, str, int]]:
    extracted: list[tuple[Path, str, str, str, int]] = []
    for zpath in paths:
        if not zipfile.is_zipfile(zpath):
            continue
        target = EXTRACT_DIR / zpath.stem
        target.mkdir(parents=True, exist_ok=True)
        with zipfile.ZipFile(zpath) as zf:
            for info in zf.infolist():
                if info.is_dir():
                    continue
                member = info.filename
                suffix = Path(member).suffix.lower()
                if suffix not in TEXT_SUFFIXES:
                    continue
                if "debroglie_matter_signature" not in member.lower() and "typ_b" not in member.lower():
                    continue
                data = zf.read(info)
                safe_name = re.sub(r"[^A-Za-z0-9._-]+", "_", member)
                out_path = target / safe_name
                out_path.write_bytes(data)
                extracted.append((out_path, rel(zpath), member, sha256_bytes(data), len(data)))
    return extracted


def read_csv_rows(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def material_from_row(row: dict[str, str]) -> tuple[str, str, str | None, int | None]:
    if "species" in row and row.get("species"):
        label = row["species"].strip()
        return "atomic_species", label, ELEMENTS.get(label.lower()), None
    iso = row.get("label") or row.get("isotope")
    can = canonical_isotope(iso)
    mass, sym = isotope_parts(can)
    if can and sym == "H":
        return "hydrogen_isotope", can, sym, mass
    if can and sym == "Sr":
        return "strontium_isotope", can, sym, mass
    if can and sym == "C":
        return "carbon_isotope", can, sym, mass
    return "other", iso or row.get("material_label") or "unknown", row.get("element_symbol"), mass


def score_from_row(row: dict[str, str]) -> float | None:
    for key in ("signature_score", "signature_score_combined", "signature_score_wave"):
        value = parse_float(row.get(key))
        if value is not None:
            return value
    return None


def structure_score_from_row(row: dict[str, str]) -> float | None:
    for key in ("structure_score", "shell_closure_score", "valence_score"):
        value = parse_float(row.get(key))
        if value is not None:
            return value
    return None


def lambda_from_row(row: dict[str, str]) -> float | None:
    return parse_float(row.get("lambda_db") or row.get("lambda_db_m"))


def energy_from_row(row: dict[str, str]) -> float | None:
    return parse_float(row.get("energy_j"))


def create_schema(conn: sqlite3.Connection) -> None:
    conn.executescript(
        """
        CREATE TABLE raw_source_file_inventory (
            source_file_id TEXT PRIMARY KEY,
            source_path TEXT NOT NULL,
            source_kind TEXT NOT NULL,
            archive_path TEXT,
            archive_member_path TEXT,
            sha256 TEXT NOT NULL,
            file_size_bytes INTEGER,
            detected_role TEXT,
            ingested_at_utc TEXT NOT NULL,
            requires_human_review INTEGER NOT NULL DEFAULT 1,
            review_note TEXT
        );
        CREATE TABLE raw_typb_signature_row (
            raw_row_id TEXT PRIMARY KEY,
            source_file_id TEXT NOT NULL,
            source_path TEXT NOT NULL,
            row_number INTEGER,
            record_kind TEXT NOT NULL,
            material_label TEXT,
            element_symbol TEXT,
            isotope_label TEXT,
            mass_number INTEGER,
            quantity_name TEXT,
            value_text TEXT,
            value_numeric REAL,
            unit_text TEXT,
            dimension_status TEXT,
            extraction_note TEXT,
            requires_human_review INTEGER NOT NULL DEFAULT 1
        );
        CREATE TABLE dim_material_system (
            material_system_id TEXT PRIMARY KEY,
            material_label TEXT NOT NULL,
            system_class TEXT NOT NULL,
            element_name TEXT,
            element_symbol TEXT,
            isotope_label TEXT,
            mass_number INTEGER,
            electron_structure_class TEXT,
            expected_anchor_status TEXT,
            requires_human_review INTEGER NOT NULL DEFAULT 1,
            review_note TEXT
        );
        CREATE TABLE fact_debroglie_material_signature (
            signature_fact_id TEXT PRIMARY KEY,
            material_system_id TEXT NOT NULL,
            source_file_id TEXT NOT NULL,
            lambda_db_m REAL,
            energy_j REAL,
            signature_score REAL,
            mass_order_rank INTEGER,
            wave_order_rank INTEGER,
            structure_score REAL,
            quantity_origin TEXT,
            unit_status TEXT NOT NULL,
            dimension_status TEXT NOT NULL,
            requires_human_review INTEGER NOT NULL DEFAULT 1,
            review_note TEXT
        );
        CREATE TABLE fact_isotope_shift (
            isotope_shift_id TEXT PRIMARY KEY,
            series_label TEXT NOT NULL,
            isotope_label TEXT NOT NULL,
            mass_number INTEGER,
            mass_order_rank INTEGER,
            wave_order_rank INTEGER,
            mass_order_direction TEXT,
            wave_order_direction TEXT,
            shift_pattern_label TEXT,
            source_file_id TEXT NOT NULL,
            requires_human_review INTEGER NOT NULL DEFAULT 1,
            review_note TEXT
        );
        CREATE TABLE result_material_sensitivity_anchor (
            anchor_id TEXT PRIMARY KEY,
            anchor_label TEXT NOT NULL,
            anchor_class TEXT NOT NULL,
            evidence_summary TEXT NOT NULL,
            supported_materials TEXT,
            claim_boundary TEXT NOT NULL,
            evidence_status TEXT NOT NULL,
            unit_status TEXT NOT NULL,
            requires_human_review INTEGER NOT NULL DEFAULT 1,
            review_note TEXT
        );
        CREATE TABLE run_manifest (
            key TEXT PRIMARY KEY,
            value TEXT NOT NULL
        );
        """
    )


def insert_many(conn: sqlite3.Connection, table: str, rows: list[dict[str, object]]) -> None:
    if not rows:
        return
    keys = list(rows[0].keys())
    placeholders = ",".join("?" for _ in keys)
    conn.executemany(
        f"INSERT INTO {table} ({','.join(keys)}) VALUES ({placeholders})",
        [[row.get(k) for k in keys] for row in rows],
    )


def export_table(conn: sqlite3.Connection, table: str, out_name: str) -> None:
    cur = conn.execute(f"SELECT * FROM {table}")
    names = [d[0] for d in cur.description]
    with (CSV_DIR / out_name).open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(names)
        writer.writerows(cur.fetchall())


def build_review_items(conn: sqlite3.Connection) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    specs = [
        ("raw_source_file_inventory", "source_file_id", "review_note"),
        ("raw_typb_signature_row", "raw_row_id", "extraction_note"),
        ("dim_material_system", "material_system_id", "review_note"),
        ("fact_debroglie_material_signature", "signature_fact_id", "review_note"),
        ("fact_isotope_shift", "isotope_shift_id", "review_note"),
        ("result_material_sensitivity_anchor", "anchor_id", "review_note"),
    ]
    idx = 1
    for table, id_col, note_col in specs:
        for item_id, note in conn.execute(
            f"SELECT {id_col}, COALESCE({note_col}, '') FROM {table} WHERE requires_human_review = 1"
        ):
            rows.append(
                {
                    "review_item_id": f"MATERIAL01-REV-{idx:05d}",
                    "source_table": table,
                    "source_id": item_id,
                    "review_note": note or "requires human review",
                }
            )
            idx += 1
    return rows


def write_review_csv(rows: list[dict[str, object]]) -> None:
    fieldnames = ["review_item_id", "source_table", "source_id", "review_note"]
    with (CSV_DIR / "07_material01_review_items.csv").open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def main() -> int:
    if OUTPUT_DIR.exists():
        print(f"Refusing to overwrite existing output directory: {rel(OUTPUT_DIR)}", file=sys.stderr)
        return 2

    CSV_DIR.mkdir(parents=True)
    REPORT_DIR.mkdir(parents=True)
    EXTRACT_DIR.mkdir(parents=True)

    source_paths = find_sources()
    zip_paths = [p for p in source_paths if p.suffix.lower() == ".zip"]
    extracted = extract_zip_sources(zip_paths)

    inventory: list[dict[str, object]] = []
    source_id_by_path: dict[str, str] = {}
    now = utc_now()

    all_file_entries: list[tuple[Path, str, str | None, str | None, str, int]] = []
    for p in source_paths:
        if p.suffix.lower() == ".zip":
            all_file_entries.append((p, "file", None, None, sha256_file(p), p.stat().st_size))
        else:
            all_file_entries.append((p, source_kind(p), None, None, sha256_file(p), p.stat().st_size))
    for p, archive, member, digest, size in extracted:
        all_file_entries.append((p, "extracted_file", archive, member, digest, size))

    for idx, (p, kind, archive, member, digest, size) in enumerate(sorted(all_file_entries), 1):
        sid = f"MATERIAL01-SRC-{idx:05d}"
        spath = rel(p)
        source_id_by_path[spath] = sid
        inventory.append(
            {
                "source_file_id": sid,
                "source_path": spath,
                "source_kind": "zip_entry" if member else kind,
                "archive_path": archive,
                "archive_member_path": member,
                "sha256": digest,
                "file_size_bytes": size,
                "detected_role": detect_role(p),
                "ingested_at_utc": now,
                "requires_human_review": 0 if detect_role(p) in {"result_csv", "result_json", "readout"} else 1,
                "review_note": "" if detect_role(p) in {"result_csv", "result_json", "readout"} else "Inventoried support/source file; role not used as primary result evidence.",
            }
        )

    scan_files = [
        p for p, _, _, _, _, _ in all_file_entries
        if p.name.endswith("_scan.csv") and "debroglie_matter_signature" in rel(p)
    ]
    scan_files = sorted(scan_files)

    raw_rows: list[dict[str, object]] = []
    dim_by_key: dict[str, dict[str, object]] = {}
    facts: list[dict[str, object]] = []
    isotope_shift_rows: list[dict[str, object]] = []
    found_labels: set[str] = set()
    found_atomic: set[str] = set()
    found_isotopes: set[str] = set()
    per_source_rows: dict[str, list[tuple[dict[str, str], str, str, str | None, int | None]]] = {}

    numeric_quantities = [
        ("lambda_db", "m", "si"),
        ("lambda_db_m", "m", "si"),
        ("energy_j", "J", "si"),
        ("signature_score", "dimensionless", "dimensionless"),
        ("signature_score_wave", "dimensionless", "dimensionless"),
        ("signature_score_combined", "dimensionless", "dimensionless"),
        ("mass_only_rank", "dimensionless index", "dimensionless"),
        ("matter_sensitive_rank", "dimensionless index", "dimensionless"),
        ("mass_u", "u", "si"),
        ("structure_score", "dimensionless", "dimensionless"),
        ("shell_closure_score", "dimensionless", "dimensionless"),
        ("valence_score", "dimensionless", "dimensionless"),
    ]

    raw_idx = 1
    fact_idx = 1
    for path in scan_files:
        spath = rel(path)
        source_id = source_id_by_path.get(spath)
        if source_id is None:
            continue
        rows = read_csv_rows(path)
        source_material_rows: list[tuple[dict[str, str], str, str, str | None, int | None]] = []
        for row_number, row in enumerate(rows, 2):
            record_kind, label, symbol, mass_number = material_from_row(row)
            isotope_label = label if record_kind.endswith("_isotope") else None
            found_labels.add(label)
            if record_kind == "atomic_species":
                found_atomic.add(label.lower())
            if isotope_label:
                found_isotopes.add(isotope_label)
            source_material_rows.append((row, record_kind, label, symbol, mass_number))

            dim_key = isotope_label or label.lower()
            if dim_key not in dim_by_key:
                system_class = "isotope_member" if isotope_label else "atomic_species"
                dim_by_key[dim_key] = {
                    "material_system_id": f"MATERIAL01-MAT-{len(dim_by_key)+1:04d}",
                    "material_label": label,
                    "system_class": system_class,
                    "element_name": None if isotope_label else label,
                    "element_symbol": symbol,
                    "isotope_label": isotope_label,
                    "mass_number": mass_number,
                    "electron_structure_class": "same_element_isotope" if isotope_label else "atomic_species",
                    "expected_anchor_status": "not_expected",
                    "requires_human_review": 1,
                    "review_note": "Found in Typ-B outputs; expectation status assigned after anchor check.",
                }

            for qname, unit, dim_status in numeric_quantities:
                if qname in row and row[qname] != "":
                    raw_rows.append(
                        {
                            "raw_row_id": f"MATERIAL01-RAW-{raw_idx:06d}",
                            "source_file_id": source_id,
                            "source_path": spath,
                            "row_number": row_number,
                            "record_kind": record_kind,
                            "material_label": label,
                            "element_symbol": symbol,
                            "isotope_label": isotope_label,
                            "mass_number": mass_number,
                            "quantity_name": qname,
                            "value_text": row[qname],
                            "value_numeric": parse_float(row[qname]),
                            "unit_text": unit,
                            "dimension_status": dim_status,
                            "extraction_note": "Extracted from existing Typ-B scan CSV.",
                            "requires_human_review": 0,
                        }
                    )
                    raw_idx += 1

            facts.append(
                {
                    "signature_fact_id": f"MATERIAL01-SIG-{fact_idx:06d}",
                    "material_system_id": dim_by_key[dim_key]["material_system_id"],
                    "source_file_id": source_id,
                    "lambda_db_m": lambda_from_row(row),
                    "energy_j": energy_from_row(row),
                    "signature_score": score_from_row(row),
                    "mass_order_rank": parse_int(row.get("mass_only_rank")),
                    "wave_order_rank": parse_int(row.get("matter_sensitive_rank")),
                    "structure_score": structure_score_from_row(row),
                    "quantity_origin": "extracted",
                    "unit_status": "mixed_review" if "mass_u" in row else "si",
                    "dimension_status": "review" if "mass_u" in row else "valid",
                    "requires_human_review": 1 if "mass_u" in row else 0,
                    "review_note": "Mixed SI and atomic-mass-unit columns require unit review." if "mass_u" in row else "",
                }
            )
            fact_idx += 1
        per_source_rows[source_id] = source_material_rows

    # Anchor status rows, including expected missing.
    for atom in EXPECTED_ATOMIC:
        key = atom.lower()
        if key in dim_by_key:
            dim_by_key[key]["expected_anchor_status"] = "expected_found"
            dim_by_key[key]["requires_human_review"] = 0
            dim_by_key[key]["review_note"] = "Expected atomic species found in Typ-B outputs."
        else:
            dim_by_key[key] = {
                "material_system_id": f"MATERIAL01-MAT-{len(dim_by_key)+1:04d}",
                "material_label": atom,
                "system_class": "atomic_species",
                "element_name": atom,
                "element_symbol": ELEMENTS.get(atom),
                "isotope_label": None,
                "mass_number": None,
                "electron_structure_class": "atomic_species",
                "expected_anchor_status": "expected_missing",
                "requires_human_review": 1,
                "review_note": "Expected atomic species not found in parsed Typ-B result rows.",
            }
    for iso in EXPECTED_ISOTOPES:
        key = iso
        mass, sym = isotope_parts(iso)
        if key in dim_by_key:
            dim_by_key[key]["expected_anchor_status"] = "expected_found"
            dim_by_key[key]["requires_human_review"] = 0
            dim_by_key[key]["review_note"] = "Expected isotope anchor found in Typ-B outputs."
        else:
            dim_by_key[key] = {
                "material_system_id": f"MATERIAL01-MAT-{len(dim_by_key)+1:04d}",
                "material_label": iso,
                "system_class": "isotope_member",
                "element_name": None,
                "element_symbol": sym,
                "isotope_label": iso,
                "mass_number": mass,
                "electron_structure_class": "same_element_isotope",
                "expected_anchor_status": "expected_missing",
                "requires_human_review": 1,
                "review_note": "Expected isotope anchor not found in parsed Typ-B result rows.",
            }
    expected_keys = {a.lower() for a in EXPECTED_ATOMIC} | set(EXPECTED_ISOTOPES)
    for key, row in dim_by_key.items():
        if key not in expected_keys and row["expected_anchor_status"] == "not_expected":
            row["expected_anchor_status"] = "found_extra"
            row["requires_human_review"] = 1
            row["review_note"] = "Additional plausible material system found in Typ-B outputs."

    # Isotope shift facts from each source CSV.
    shift_idx = 1
    for source_id, items in per_source_rows.items():
        iso_items = [x for x in items if x[1].endswith("_isotope")]
        if not iso_items:
            continue
        groups: dict[str, list[tuple[dict[str, str], str, str, str | None, int | None]]] = defaultdict(list)
        for item in iso_items:
            _row, _kind, _label, sym, _mass = item
            if sym in ISO_SERIES:
                groups[ISO_SERIES[sym]].append(item)
        for series, group in groups.items():
            unique: dict[str, tuple[dict[str, str], str, str, str | None, int | None]] = {}
            for item in group:
                unique[item[2]] = item
            ordered_mass = sorted(unique.values(), key=lambda x: (x[4] if x[4] is not None else 9999))
            ordered_wave = sorted(unique.values(), key=lambda x: (lambda_from_row(x[0]) is None, -(lambda_from_row(x[0]) or 0.0)))
            mass_rank = {item[2]: idx + 1 for idx, item in enumerate(ordered_mass)}
            wave_rank = {item[2]: idx + 1 for idx, item in enumerate(ordered_wave)}
            lambdas = [lambda_from_row(item[0]) for item in ordered_mass]
            monotone = all(a is not None and b is not None and a > b for a, b in zip(lambdas, lambdas[1:]))
            label = "monotone_wave_shift" if monotone else "review"
            for item in ordered_mass:
                row, _kind, iso_label, _sym, mass = item
                isotope_shift_rows.append(
                    {
                        "isotope_shift_id": f"MATERIAL01-ISO-{shift_idx:05d}",
                        "series_label": series,
                        "isotope_label": iso_label,
                        "mass_number": mass,
                        "mass_order_rank": mass_rank.get(iso_label),
                        "wave_order_rank": wave_rank.get(iso_label),
                        "mass_order_direction": "lighter_to_heavier",
                        "wave_order_direction": "larger_to_smaller_lambda" if monotone else "unknown",
                        "shift_pattern_label": label,
                        "source_file_id": source_id,
                        "requires_human_review": 1,
                        "review_note": "Isotope wave-shift row derived from source ordering; review before physical interpretation.",
                    }
                )
                shift_idx += 1

    found_expected_atomic = sorted(a for a in EXPECTED_ATOMIC if a in found_atomic)
    found_expected_isotopes = sorted((i for i in EXPECTED_ISOTOPES if i in found_isotopes), key=lambda x: (re.sub(r"\\D", "", x), x))
    result_anchors = [
        {
            "anchor_id": "MATERIAL01-ANCHOR-001",
            "anchor_label": "Typ-B atomic species material signature",
            "anchor_class": "atomic_species_signature",
            "evidence_summary": "Typ-B outputs document material-sensitive de-Broglie signature differences for atomic species where present in source outputs.",
            "supported_materials": ";".join(found_expected_atomic),
            "claim_boundary": CLAIM_BOUNDARY,
            "evidence_status": "supported_by_typb_outputs" if found_expected_atomic else "insufficient",
            "unit_status": "mixed_review",
            "requires_human_review": 1,
            "review_note": "Anchor is source-output bound and not a new physics calculation.",
        },
        {
            "anchor_id": "MATERIAL01-ANCHOR-002",
            "anchor_label": "Typ-B isotope wave shift",
            "anchor_class": "isotope_wave_shift",
            "evidence_summary": "Typ-B isotope outputs document mass-order versus wave-order shifts where present in source outputs.",
            "supported_materials": ";".join(found_expected_isotopes),
            "claim_boundary": CLAIM_BOUNDARY,
            "evidence_status": "supported_by_typb_outputs" if found_expected_isotopes else "insufficient",
            "unit_status": "mixed_review",
            "requires_human_review": 1,
            "review_note": "Derived ordering summary from existing isotope scan rows; no new scan.",
        },
        {
            "anchor_id": "MATERIAL01-ANCHOR-003",
            "anchor_label": "INTERFACE01 material sensitivity anchor",
            "anchor_class": "material_sensitivity",
            "evidence_summary": "These outputs support MATERIAL01 as an evidence anchor for material-sensitive phase/wave/signature shifts in INTERFACE01.",
            "supported_materials": ";".join(sorted(found_labels)),
            "claim_boundary": CLAIM_BOUNDARY,
            "evidence_status": "supported_by_typb_outputs" if found_labels else "insufficient",
            "unit_status": "mixed_review",
            "requires_human_review": 1,
            "review_note": "Use only as bounded MATERIAL01 anchor for INTERFACE01 intake.",
        },
    ]

    conn = sqlite3.connect(DB_PATH)
    create_schema(conn)
    insert_many(conn, "raw_source_file_inventory", inventory)
    insert_many(conn, "raw_typb_signature_row", raw_rows)
    insert_many(conn, "dim_material_system", list(dim_by_key.values()))
    insert_many(conn, "fact_debroglie_material_signature", facts)
    insert_many(conn, "fact_isotope_shift", isotope_shift_rows)
    insert_many(conn, "result_material_sensitivity_anchor", result_anchors)

    review_rows = build_review_items(conn)
    status = (
        "material01_typb_signature_mart_intake_completed_with_review_items"
        if review_rows else "material01_typb_signature_mart_intake_completed"
    )
    input_sufficiency = "sufficient_typb_outputs_found" if scan_files else "insufficient_inputs"
    unit_status = "mixed_review; lambda_db=m; energy=J; scores=dimensionless; mass_u=atomic_mass_unit_review"
    manifest = {
        "run_id": "QSB-MATERIAL01",
        "status": status,
        "output_dir": rel(OUTPUT_DIR),
        "input_sufficiency": input_sufficiency,
        "sources_found": len(inventory),
        "material_systems_found": len(dim_by_key),
        "signature_facts": len(facts),
        "isotope_shift_rows": len(isotope_shift_rows),
        "result_anchors": len(result_anchors),
        "review_items": len(review_rows),
        "unit_status": unit_status,
        "claim_boundary": CLAIM_BOUNDARY,
        "mutated_existing_files": False,
        "generated_synthetic_evidence": False,
    }
    conn.executemany("INSERT INTO run_manifest (key, value) VALUES (?, ?)", [(k, json.dumps(v) if isinstance(v, (bool, int, list, dict)) else str(v)) for k, v in manifest.items()])
    conn.commit()

    export_table(conn, "raw_source_file_inventory", "01_source_file_inventory.csv")
    export_table(conn, "raw_typb_signature_row", "02_raw_typb_signature_rows.csv")
    export_table(conn, "dim_material_system", "03_dim_material_system.csv")
    export_table(conn, "fact_debroglie_material_signature", "04_fact_debroglie_material_signature.csv")
    export_table(conn, "fact_isotope_shift", "05_fact_isotope_shift.csv")
    export_table(conn, "result_material_sensitivity_anchor", "06_result_material_sensitivity_anchor.csv")
    write_review_csv(review_rows)
    conn.close()

    (REPORT_DIR / "MATERIAL01_RUN_MANIFEST.json").write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    missing_atomic = [a for a in EXPECTED_ATOMIC if a not in found_atomic]
    missing_iso = [i for i in EXPECTED_ISOTOPES if i not in found_isotopes]
    report = f"""# MATERIAL01 Final Assessment

## Input-Sufficiency
Status: {input_sufficiency}

Gefundene Typ-B-Signaturquellen: {len(inventory)}
Geparste Scan-Dateien: {len(scan_files)}

## Gefundene Quellen
Primaere Quelle ist `numerics/debroglie-phase-bridge/typ_b_analysis/results/` mit vorhandenen `debroglie_matter_signature*`-Outputs. ZIP-Kandidaten wurden nur beruecksichtigt, wenn sie als `typ_b_analysis.zip` oder `files.zip` im Repo-Root vorhanden waren.

## Gefundene Materialanker
Erwartete atomare Spezies gefunden: {', '.join(found_expected_atomic) if found_expected_atomic else 'none'}
Erwartete atomare Spezies mit Review-Status fehlend: {', '.join(missing_atomic) if missing_atomic else 'none'}

## Gefundene Isotopenanker
Erwartete Isotope gefunden: {', '.join(found_expected_isotopes) if found_expected_isotopes else 'none'}
Erwartete Isotope mit Review-Status fehlend: {', '.join(missing_iso) if missing_iso else 'none'}

## Result-Anker
1. Atomare Typ-B-Materialsignatur fuer gefundene Spezies.
2. Isotopische mass-order versus wave-order Verschiebungen fuer gefundene H-, Sr- und C-Serien.
3. MATERIAL01 als knapper Befundanker fuer materialsensitive phase/wave/signature shifts in INTERFACE01.

## Einheiten-/Dimensionsstatus
`lambda_db` wurde als m, `energy_j` als J und Signatur-Scores als dimensionslos gefuehrt. `mass_u` bleibt als atomic-mass-unit-Spalte review-pflichtig. Gesamtstatus: {unit_status}

## Review-Items
Review-Items: {len(review_rows)}
Hauptgruende: inventarisierte Support-Dateien, zusaetzliche plausible Materialsysteme, gemischte Einheitenfelder und abgeleitete Isotopen-Shift-Zeilen.

## Claim-Grenze
{CLAIM_BOUNDARY}

## Naechster sinnvoller Schritt fuer INTERFACE01
INTERFACE01 sollte zuerst die drei Result-Anker aus `result_material_sensitivity_anchor` nutzen und dabei die Review-Items zu Einheiten, Zusatzsystemen und abgeleiteten Isotopenordnungen sichtbar mitfuehren.
"""
    (REPORT_DIR / "MATERIAL01_FINAL_ASSESSMENT.md").write_text(report, encoding="utf-8")

    # Remove empty extract dir if no zip content was used, keeping the requested folder present.
    if not any(EXTRACT_DIR.iterdir()):
        (EXTRACT_DIR / "README.txt").write_text("No typ_b_analysis.zip or files.zip extraction was used in this MATERIAL01 run.\n", encoding="utf-8")

    print(json.dumps(manifest, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
