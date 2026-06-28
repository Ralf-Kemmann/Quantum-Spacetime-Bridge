#!/usr/bin/env python3
"""Build the sandbox QSB-MAP01-DWH-A SQLite mart and Mermaid export."""

from __future__ import annotations

import hashlib
import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from textwrap import dedent


REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT_PATH = Path("scripts/qsb_map01_dwh_a/qsb_map01_dwh_a.py")
SCHEMA_PATH = REPO_ROOT / "scripts/qsb_map01_dwh_a/schema.sql"
OUTPUT_DIR = REPO_ROOT / "runs/QSB-MAP01-DWH-A"
DB_PATH = OUTPUT_DIR / "qsb_map01.sqlite"
MAP_ID = "QSB-MAP01"
GENERATOR_NAME = "qsb_map01_dwh_a.py"
GENERATOR_VERSION = "0.1"
CLAIM_BOUNDARY_SUMMARY = (
    "Orientation map only; no physical confirmation, no spacetime claim, "
    "no causality claim."
)
FORBIDDEN_CONFIRMATION_WORDING = [
    "proves QSB",
    "proves spacetime",
    "establishes causality",
]
MERMAID_GENERATED_FROM_DB = False


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def rel(path: Path) -> str:
    return str(path.relative_to(REPO_ROOT))


def connect_fresh_database() -> sqlite3.Connection:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    if DB_PATH.exists():
        raise FileExistsError(
            f"{rel(DB_PATH)} already exists; remove or archive the sandbox output before rerun."
        )
    con = sqlite3.connect(DB_PATH)
    con.row_factory = sqlite3.Row
    con.execute("PRAGMA foreign_keys = ON")
    con.executescript(SCHEMA_PATH.read_text(encoding="utf-8"))
    return con


def seed_map(con: sqlite3.Connection, timestamp: str) -> None:
    con.execute(
        """
        INSERT INTO qsb_map (
            map_id, title, map_level, scope, status, version, created_at,
            updated_at, owner_role, claim_boundary_summary, notes
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            MAP_ID,
            "Große Projektlandkarte",
            1,
            "project_overview",
            "sandbox_seed",
            GENERATOR_VERSION,
            timestamp,
            None,
            "project_lead",
            CLAIM_BOUNDARY_SUMMARY,
            "Standalone sandbox mart; no production DWH or Source-Hub mutation.",
        ),
    )


def node(
    node_id: str,
    parent_node_id: str | None,
    label: str,
    canonical_key: str,
    node_type: str,
    qsb_layer: str,
    short_description: str,
    sort_order: int,
    status: str = "sandbox_seed",
    review_status: str = "draft",
) -> dict[str, object]:
    return {
        "node_id": node_id,
        "map_id": MAP_ID,
        "parent_node_id": parent_node_id,
        "label": label,
        "canonical_key": canonical_key,
        "node_type": node_type,
        "qsb_layer": qsb_layer,
        "short_description": short_description,
        "sort_order": sort_order,
        "status": status,
        "review_status": review_status,
    }


def seed_nodes(con: sqlite3.Connection) -> list[dict[str, object]]:
    nodes = [
        node(
            "QSB-MAP01-ROOT",
            None,
            "QSB / Quantum-Spacetime-Bridge",
            "qsb_root",
            "project_root",
            "project_overview",
            "Root node for the QSB-MAP01 orientation map.",
            0,
        ),
        node("QSB-MAP01-A", "QSB-MAP01-ROOT", "Ursprung & Leitfrage", "origin_leitfrage", "branch", "project_overview", "Origin and guiding question branch.", 10),
        node("QSB-MAP01-B", "QSB-MAP01-ROOT", "Daten- & Pipeline-Zweige", "data_pipeline_branches", "branch", "project_overview", "Data and pipeline context branch.", 20),
        node("QSB-MAP01-C", "QSB-MAP01-ROOT", "RELALG-Theorie", "relalg_theory", "branch", "formal_sandbox", "Formal relation-algebra orientation branch; no RELALG computation.", 30),
        node("QSB-MAP01-D", "QSB-MAP01-ROOT", "Literaturanschluss", "literature_context", "branch", "literature_context", "Literature-neighbor context branch.", 40),
        node("QSB-MAP01-E", "QSB-MAP01-ROOT", "Metadaten & Google-Effekt", "metadata_google_effect", "branch", "metadata", "Metadata, source, alias, and search context branch.", 50),
        node("QSB-MAP01-F", "QSB-MAP01-ROOT", "Claim-Gates & Prüfregeln", "claim_gates_pruefregeln", "branch", "claim_boundary", "Claim-gate and review-rule branch.", 60),
        node("QSB-MAP01-A-01", "QSB-MAP01-A", "de-Broglie / Materiewelle", "de_broglie_materiewelle", "formal_object", "origin_context", "Historical/formal context node for matter-wave language.", 11),
        node("QSB-MAP01-A-02", "QSB-MAP01-A", "ψ-/Phasen-/Response-Signaturen", "psi_phase_response_signatures", "concept", "origin_context", "Signature vocabulary node for ψ, phase, and response language.", 12),
        node("QSB-MAP01-A-03", "QSB-MAP01-A", "Relation statt isolierter Zustand", "relation_not_isolated_state", "concept", "origin_context", "Orientation node for relation-first phrasing.", 13),
        node("QSB-MAP01-B-01", "QSB-MAP01-B", "debroglie-correlation-structure", "debroglie_correlation_structure", "pipeline", "pipeline_context", "External repository context for correlation-structure work.", 21),
        node("QSB-MAP01-B-02", "QSB-MAP01-B", "polyakov-gram-graph", "polyakov_gram_graph", "pipeline", "pipeline_context", "External repository context for Gram-graph work.", 22),
        node("QSB-MAP01-B-03", "QSB-MAP01-B", "EXTRACT03 / K-Matrix-Linie", "extract03_k_matrix_line", "pipeline", "pipeline_context", "Project-local extraction and K-matrix lineage context.", 23),
        node("QSB-MAP01-B-04", "QSB-MAP01-B", "Source-Hub / DWH / Lineage", "source_hub_dwh_lineage", "metadata_system", "metadata", "Metadata lineage and source-context orientation.", 24),
        node("QSB-MAP01-C-01", "QSB-MAP01-C", "Zweischichtige Relation", "two_layer_relation", "formal_concept", "formal_sandbox", "Formal two-layer relation vocabulary.", 31),
        node("QSB-MAP01-C-02", "QSB-MAP01-C", "C_AB = komplexe / phasentragende Relation", "c_ab_complex_phase_relation", "formal_object", "formal_sandbox", "Complex or phase-bearing relation object.", 32),
        node("QSB-MAP01-C-03", "QSB-MAP01-C", "K_AB = Stärke / Betrag / Score aus C_AB", "k_ab_strength_score_from_c_ab", "formal_object", "formal_sandbox", "Strength, magnitude, or score layer derived from C_AB.", 33),
        node("QSB-MAP01-C-04", "QSB-MAP01-C", "Graph / Distanz", "graph_distance", "formal_object", "formal_sandbox", "Graph and distance vocabulary for formal orientation only.", 34),
        node("QSB-MAP01-C-05", "QSB-MAP01-C", "Loop-Phase", "loop_phase", "formal_object", "formal_sandbox", "Formal sandbox object for oriented relational loop residues.", 35),
        node("QSB-MAP01-C-06", "QSB-MAP01-C", "Φ_ABC = arg(C_AB · C_BC · C_CA)", "phi_abc_cyclic_product_phase", "formal_object", "formal_sandbox", "Cyclic product phase expression for formal comparison.", 36),
        node("QSB-MAP01-C-07", "QSB-MAP01-C", "Höhere Motive", "higher_motifs", "formal_concept", "formal_sandbox", "Placeholder for higher motif orientation, not a computed result.", 37),
        node("QSB-MAP01-C-08", "QSB-MAP01-C", "a_rel / ℓ_rel", "a_rel_l_rel", "formal_object", "formal_sandbox", "Candidate local relational scale vocabulary.", 38),
        node("QSB-MAP01-D-01", "QSB-MAP01-D", "Bargmann", "bargmann", "formal_object", "literature_context", "Literature-neighbor node for Bargmann invariant context.", 41),
        node("QSB-MAP01-D-02", "QSB-MAP01-D", "Pancharatnam", "pancharatnam", "literature_neighbor", "literature_context", "Literature-neighbor context for Pancharatnam phase language.", 42),
        node("QSB-MAP01-D-03", "QSB-MAP01-D", "Berry", "berry", "literature_neighbor", "literature_context", "Literature-neighbor context for Berry phase language.", 43),
        node("QSB-MAP01-D-04", "QSB-MAP01-D", "Polyakov / Pfadintegral-Nachbarschaft", "polyakov_path_integral_neighborhood", "formal_object", "literature_context", "Formal literature-neighborhood context only.", 44),
        node("QSB-MAP01-D-05", "QSB-MAP01-D", "Matrixmechanik / Kernel-Komposition", "matrix_mechanics_kernel_composition", "literature_neighbor", "literature_context", "Literature-neighbor context for kernel composition language.", 45),
        node("QSB-MAP01-E-01", "QSB-MAP01-E", "Quellenpool", "source_pool", "metadata", "metadata", "Source-pool orientation node.", 51),
        node("QSB-MAP01-E-02", "QSB-MAP01-E", "Motivindex", "motif_index", "metadata", "metadata", "Motif-index orientation node.", 52),
        node("QSB-MAP01-E-03", "QSB-MAP01-E", "Claim-Boundary-Index", "claim_boundary_index", "metadata", "metadata", "Claim-boundary index orientation node.", 53),
        node("QSB-MAP01-E-04", "QSB-MAP01-E", "Suchachsen / Aliase", "search_axes_aliases", "metadata", "metadata", "Search-axis and alias orientation node.", 54),
        node("QSB-MAP01-F-01", "QSB-MAP01-F", "Keine Raumzeitbehauptung", "no_spacetime_claim", "claim_gate", "claim_boundary", "Gate forbidding spacetime claims.", 61),
        node("QSB-MAP01-F-02", "QSB-MAP01-F", "Keine physikalische Kausalitätsbehauptung", "no_physical_causality_claim", "claim_gate", "claim_boundary", "Gate forbidding physical causality claims.", 62),
        node("QSB-MAP01-F-03", "QSB-MAP01-F", "Graph ≠ Raumzeit", "graph_not_spacetime", "claim_gate", "claim_boundary", "Gate separating graph objects from spacetime claims.", 63),
        node("QSB-MAP01-F-04", "QSB-MAP01-F", "Graph ≠ Gitter", "graph_not_lattice", "claim_gate", "claim_boundary", "Gate separating graph vocabulary from lattice claims.", 64),
        node("QSB-MAP01-F-05", "QSB-MAP01-F", "C_AB und K_AB sauber trennen", "separate_c_ab_and_k_ab", "claim_gate", "claim_boundary", "Gate requiring separation of C_AB and K_AB layers.", 65),
        node("QSB-MAP01-F-06", "QSB-MAP01-F", "Nichtorthogonalitäts-/Nullstellen-Gates prüfen", "nonorthogonality_zero_gates", "claim_gate", "claim_boundary", "Review gate for nonorthogonality and zero cases.", 66),
        node("QSB-MAP01-F-07", "QSB-MAP01-F", "Rephasing-/Gauge-Verhalten prüfen", "rephasing_gauge_behavior", "claim_gate", "claim_boundary", "Review gate for rephasing and gauge behavior.", 67),
        node("QSB-MAP01-F-08", "QSB-MAP01-F", "Nullmodelle gegenhalten", "compare_null_models", "claim_gate", "claim_boundary", "Review gate for null model comparison.", 68),
        node("QSB-MAP01-F-09", "QSB-MAP01-F", "Reproduzierbarkeit dokumentieren", "document_reproducibility", "claim_gate", "claim_boundary", "Review gate requiring reproducibility documentation.", 69),
    ]
    con.executemany(
        """
        INSERT INTO qsb_map_node (
            node_id, map_id, parent_node_id, label, canonical_key, node_type,
            qsb_layer, short_description, sort_order, status, review_status
        )
        VALUES (
            :node_id, :map_id, :parent_node_id, :label, :canonical_key, :node_type,
            :qsb_layer, :short_description, :sort_order, :status, :review_status
        )
        """,
        nodes,
    )
    return nodes


def edge(
    edge_id: str,
    source_node_id: str,
    target_node_id: str,
    relation_type: str,
    relation_label: str | None,
    directionality: str = "directed",
    confidence_level: str = "sandbox_structural",
    status: str = "sandbox_seed",
) -> dict[str, str | None]:
    return {
        "edge_id": edge_id,
        "map_id": MAP_ID,
        "source_node_id": source_node_id,
        "target_node_id": target_node_id,
        "relation_type": relation_type,
        "relation_label": relation_label,
        "directionality": directionality,
        "confidence_level": confidence_level,
        "status": status,
    }


def seed_edges(con: sqlite3.Connection, nodes: list[dict[str, object]]) -> None:
    edges: list[dict[str, str | None]] = []
    parent_edges = [
        (row["parent_node_id"], row["node_id"])
        for row in nodes
        if row["parent_node_id"] is not None
    ]
    for idx, (parent, child) in enumerate(parent_edges, start=1):
        edges.append(edge(f"QSB-MAP01-E-{idx:03d}", str(parent), str(child), "contains", "contains"))
    special_edges = [
        ("QSB-MAP01-E-S01", "QSB-MAP01-C-05", "QSB-MAP01-D-01", "formal_neighbor_of", "formal neighbor of"),
        ("QSB-MAP01-E-S02", "QSB-MAP01-C-03", "QSB-MAP01-C-02", "derives_from", "derived from"),
        ("QSB-MAP01-E-S03", "QSB-MAP01-C-06", "QSB-MAP01-C-02", "depends_on", "depends on"),
        ("QSB-MAP01-E-S04", "QSB-MAP01-C-04", "QSB-MAP01-F-03", "has_claim_boundary", "bounded by"),
        ("QSB-MAP01-E-S05", "QSB-MAP01-C-04", "QSB-MAP01-F-04", "has_claim_boundary", "bounded by"),
        ("QSB-MAP01-E-S06", "QSB-MAP01-C-02", "QSB-MAP01-F-05", "has_claim_boundary", "bounded by"),
        ("QSB-MAP01-E-S07", "QSB-MAP01-C-03", "QSB-MAP01-F-05", "has_claim_boundary", "bounded by"),
        ("QSB-MAP01-E-S08", "QSB-MAP01-C-05", "QSB-MAP01-F-02", "has_claim_boundary", "bounded by"),
        ("QSB-MAP01-E-S09", "QSB-MAP01-C-06", "QSB-MAP01-F-07", "has_claim_boundary", "bounded by"),
        ("QSB-MAP01-E-S10", "QSB-MAP01-C-08", "QSB-MAP01-F-04", "has_claim_boundary", "bounded by"),
    ]
    for row in special_edges:
        edges.append(edge(*row))
    con.executemany(
        """
        INSERT INTO qsb_map_edge (
            edge_id, map_id, source_node_id, target_node_id, relation_type,
            relation_label, directionality, confidence_level, status
        )
        VALUES (
            :edge_id, :map_id, :source_node_id, :target_node_id, :relation_type,
            :relation_label, :directionality, :confidence_level, :status
        )
        """,
        edges,
    )


def seed_aliases(con: sqlite3.Connection) -> None:
    alias_groups = {
        "QSB-MAP01-C-05": [
            "Schleifenphase",
            "triangular loop phase",
            "three-vertex phase",
            "three-vertex geometric phase",
            "Bargmann phase",
            "cyclic product phase",
            "Φ_ABC",
            "arg(C_AB C_BC C_CA)",
        ],
        "QSB-MAP01-C-02": [
            "complex relation",
            "phasentragende Relation",
            "overlap-like relation",
            "complex_pair_relation",
        ],
        "QSB-MAP01-C-03": [
            "strength layer",
            "Betragsschicht",
            "score layer",
            "Gram strength",
        ],
        "QSB-MAP01-C-08": [
            "relationale Skalenkonstante",
            "local relational scale",
            "nearest-neighbor scale",
            "typical local edge length",
        ],
    }
    rows = []
    counter = 1
    for node_id, aliases in alias_groups.items():
        for alias_value in aliases:
            language = "de" if any(term in alias_value for term in ["Schleifen", "tragende", "Betrags", "relationale"]) else "en"
            rows.append(
                {
                    "alias_id": f"QSB-MAP01-ALIAS-{counter:03d}",
                    "node_id": node_id,
                    "alias": alias_value,
                    "language": language,
                    "alias_type": "search_alias",
                    "status": "sandbox_seed",
                }
            )
            counter += 1
    con.executemany(
        """
        INSERT INTO qsb_map_alias (
            alias_id, node_id, alias, language, alias_type, status
        )
        VALUES (
            :alias_id, :node_id, :alias, :language, :alias_type, :status
        )
        """,
        rows,
    )


def seed_source_links(con: sqlite3.Connection) -> None:
    literature_note = (
        "The report identifies Φ_ABC-like cyclic products as formal neighbors of "
        "the third-order Bargmann invariant / three-vertex geometric phase, under "
        "overlap-like complex relation conditions; no physical causality or "
        "spacetime claim follows."
    )
    rows = [
        {
            "link_id": "QSB-MAP01-SRC-001",
            "node_id": "QSB-MAP01-C-05",
            "source_type": "deep_research_report",
            "source_ref": "deep-research-report.md",
            "source_title": "Literaturkarte zu Bargmann-, Pancharatnam- und Berry-Phasen",
            "evidence_role": "formal_neighbor",
            "claim_use": "literature_context_only",
            "source_status": "accepted_as_context",
            "notes": literature_note,
        },
        {
            "link_id": "QSB-MAP01-SRC-002",
            "node_id": "QSB-MAP01-D-01",
            "source_type": "deep_research_report",
            "source_ref": "deep-research-report.md",
            "source_title": "Literaturkarte zu Bargmann-, Pancharatnam- und Berry-Phasen",
            "evidence_role": "formal_neighbor",
            "claim_use": "literature_context_only",
            "source_status": "accepted_as_context",
            "notes": literature_note,
        },
        {
            "link_id": "QSB-MAP01-SRC-003",
            "node_id": "QSB-MAP01-B-01",
            "source_type": "github_repo",
            "source_ref": "https://github.com/Ralf-Kemmann/debroglie-correlation-structure",
            "source_title": "debroglie-correlation-structure",
            "evidence_role": "pipeline_context",
            "claim_use": "method_context_only",
            "source_status": "accepted_as_context",
            "notes": "Repository context only; no physical claim is introduced by this map link.",
        },
        {
            "link_id": "QSB-MAP01-SRC-004",
            "node_id": "QSB-MAP01-B-02",
            "source_type": "github_repo",
            "source_ref": "https://github.com/Ralf-Kemmann/polyakov-gram-graph",
            "source_title": "polyakov-gram-graph",
            "evidence_role": "pipeline_context",
            "claim_use": "method_context_only",
            "source_status": "accepted_as_context",
            "notes": "Repository context only; no physical claim is introduced by this map link.",
        },
    ]
    con.executemany(
        """
        INSERT INTO qsb_map_source_link (
            link_id, node_id, source_type, source_ref, source_title, evidence_role,
            claim_use, source_status, notes
        )
        VALUES (
            :link_id, :node_id, :source_type, :source_ref, :source_title, :evidence_role,
            :claim_use, :source_status, :notes
        )
        """,
        rows,
    )


def boundary(
    boundary_id: str,
    node_id: str,
    admissible_use: str,
    forbidden_use: str,
    overclaim_risk: str,
    notes: str,
) -> dict[str, str]:
    return {
        "boundary_id": boundary_id,
        "node_id": node_id,
        "admissible_use": admissible_use,
        "forbidden_use": forbidden_use,
        "overclaim_risk": overclaim_risk,
        "review_status": "draft_review_required",
        "notes": notes,
    }


def seed_claim_boundaries(con: sqlite3.Connection) -> None:
    rows = [
        boundary(
            "QSB-MAP01-CB-001",
            "QSB-MAP01-C-05",
            "Formal sandbox object for oriented relational loop residues.",
            "Do not claim physical causality, spacetime emergence, or new dynamics from the loop phase alone.",
            "critical",
            "Loop phase is formal-orientation vocabulary only in this mart.",
        ),
        boundary(
            "QSB-MAP01-CB-002",
            "QSB-MAP01-C-06",
            "May be compared formally with third-order Bargmann invariants / three-vertex geometric phases when C_AB behaves like an overlap-like complex relation.",
            "Do not treat Φ_ABC as evidence for QSB, spacetime emergence, or physical causality.",
            "critical",
            "Comparison is conditional and formal; no empirical or physical confirmation is asserted.",
        ),
        boundary(
            "QSB-MAP01-CB-003",
            "QSB-MAP01-D-01",
            "May be used as literature-neighbor context for cyclic product phase vocabulary.",
            "Do not claim that the Bargmann invariant validates QSB, spacetime emergence, or physical causality.",
            "high",
            "Literature context is not a validation result.",
        ),
        boundary(
            "QSB-MAP01-CB-004",
            "QSB-MAP01-C-02",
            "May be used as a formal complex or phase-bearing relation placeholder.",
            "Do not treat C_AB as a measured physical field, a spacetime object, or a dynamics law.",
            "high",
            "C_AB must remain distinct from K_AB in this dry run.",
        ),
        boundary(
            "QSB-MAP01-CB-005",
            "QSB-MAP01-C-03",
            "May be used as a formal strength, magnitude, or score layer derived from C_AB.",
            "Do not merge K_AB with C_AB or claim that a score layer proves physical structure.",
            "high",
            "K_AB is a formal score-layer node, not a physical confirmation.",
        ),
        boundary(
            "QSB-MAP01-CB-006",
            "QSB-MAP01-C-04",
            "May be used as formal graph and distance vocabulary for map orientation.",
            "Do not claim graph equals spacetime, graph equals a physical lattice, or graph distance equals physical distance.",
            "critical",
            "Graph vocabulary is structurally useful but claim-bounded.",
        ),
        boundary(
            "QSB-MAP01-CB-007",
            "QSB-MAP01-C-08",
            "May be used as a candidate robust local relational scale in a weighted signature graph.",
            "Do not claim a physical lattice constant, spacetime length, or natural constant.",
            "critical",
            "Scale vocabulary is local and formal in this sandbox map.",
        ),
        boundary(
            "QSB-MAP01-CB-008",
            "QSB-MAP01-D-04",
            "May be used as formal literature-neighborhood context for path-integral adjacency language.",
            "Do not claim Polyakov formalism validates QSB, spacetime emergence, or physical causality.",
            "high",
            "Literature-neighbor context only.",
        ),
        boundary(
            "QSB-MAP01-CB-009",
            "QSB-MAP01-A-01",
            "May be used as historical and vocabulary context for matter-wave phrasing.",
            "Do not claim de-Broglie matter-wave language confirms QSB or establishes a new physical mechanism.",
            "medium",
            "Origin-context vocabulary only.",
        ),
    ]
    con.executemany(
        """
        INSERT INTO qsb_map_claim_boundary (
            boundary_id, node_id, admissible_use, forbidden_use, overclaim_risk,
            review_status, notes
        )
        VALUES (
            :boundary_id, :node_id, :admissible_use, :forbidden_use, :overclaim_risk,
            :review_status, :notes
        )
        """,
        rows,
    )


def row_count(con: sqlite3.Connection, table_name: str) -> int:
    return int(con.execute(f"SELECT COUNT(*) AS n FROM {table_name}").fetchone()["n"])


def fetch_node_tree(con: sqlite3.Connection) -> dict[str | None, list[sqlite3.Row]]:
    rows = con.execute(
        """
        SELECT node_id, parent_node_id, label, sort_order
        FROM qsb_map_node
        WHERE map_id = ?
        ORDER BY COALESCE(parent_node_id, ''), sort_order, node_id
        """,
        (MAP_ID,),
    ).fetchall()
    children: dict[str | None, list[sqlite3.Row]] = {}
    for row in rows:
        children.setdefault(row["parent_node_id"], []).append(row)
    return children


def mermaid_label(label: str, is_root: bool) -> str:
    if is_root:
        return f"root(({label}))"
    return label


def render_mermaid_from_db(con: sqlite3.Connection) -> str:
    global MERMAID_GENERATED_FROM_DB
    children = fetch_node_tree(con)
    roots = children.get(None, [])
    if len(roots) != 1:
        raise ValueError(f"Expected one root node, found {len(roots)}")

    lines = ["mindmap"]

    def walk(row: sqlite3.Row, depth: int) -> None:
        lines.append(f"{'    ' * depth}{mermaid_label(row['label'], depth == 1)}")
        for child in children.get(row["node_id"], []):
            walk(child, depth + 1)

    walk(roots[0], 1)
    MERMAID_GENERATED_FROM_DB = True
    return "\n".join(lines) + "\n"


def high_risk_rows(con: sqlite3.Connection) -> list[sqlite3.Row]:
    return con.execute(
        """
        SELECT label, canonical_key, overclaim_risk, admissible_use, forbidden_use
        FROM v_qsb_map_claim_risk
        WHERE overclaim_risk IN ('medium', 'high', 'critical')
        ORDER BY
            CASE overclaim_risk
                WHEN 'critical' THEN 1
                WHEN 'high' THEN 2
                WHEN 'medium' THEN 3
                ELSE 4
            END,
            label
        """
    ).fetchall()


def source_context_rows(con: sqlite3.Connection) -> list[sqlite3.Row]:
    return con.execute(
        """
        SELECT label, source_type, source_ref, source_title, evidence_role, claim_use, source_status
        FROM v_qsb_map_source_context
        ORDER BY label, source_ref
        """
    ).fetchall()


def render_markdown_summary(con: sqlite3.Connection, mermaid_text: str) -> str:
    map_row = con.execute("SELECT * FROM qsb_map WHERE map_id = ?", (MAP_ID,)).fetchone()
    risk_lines = [
        f"- {row['label']} ({row['overclaim_risk']}): {row['forbidden_use']}"
        for row in high_risk_rows(con)
    ]
    source_lines = [
        f"- {row['label']}: {row['source_type']} `{row['source_ref']}`; "
        f"evidence_role={row['evidence_role']}; claim_use={row['claim_use']}"
        for row in source_context_rows(con)
    ]
    return dedent(
        f"""\
        # {map_row['title']}

        Scope: `{map_row['scope']}`

        Claim boundary: {map_row['claim_boundary_summary']}

        This Markdown summary is generated from the sandbox SQLite mart. It does
        not mutate production DWH objects, Source-Hub schema, EXTRACT tables, or
        existing project data.

        ```mermaid
        {mermaid_text.rstrip()}
        ```

        ## High-Risk Nodes

        {chr(10).join(risk_lines)}

        ## Source Context Summary

        {chr(10).join(source_lines)}
        """
    )


def render_claim_boundary_report(con: sqlite3.Connection) -> str:
    lines = [
        "# QSB-MAP01 Claim Boundary Report",
        "",
        "Sandbox-only report for nodes with overclaim risk `medium`, `high`, or `critical`.",
        "",
    ]
    for row in high_risk_rows(con):
        lines.extend(
            [
                f"## {row['label']}",
                "",
                f"- canonical_key: `{row['canonical_key']}`",
                f"- overclaim_risk: `{row['overclaim_risk']}`",
                f"- admissible_use: {row['admissible_use']}",
                f"- forbidden_use: {row['forbidden_use']}",
                "",
            ]
        )
    return "\n".join(lines)


def insert_export_record(
    con: sqlite3.Connection,
    export_id: str,
    export_type: str,
    output_path: Path,
    timestamp: str,
) -> None:
    con.execute(
        """
        INSERT INTO qsb_map_export (
            export_id, map_id, export_type, output_path, generated_at,
            generator_name, generator_version, content_hash, status
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            export_id,
            MAP_ID,
            export_type,
            rel(output_path),
            timestamp,
            GENERATOR_NAME,
            GENERATOR_VERSION,
            sha256_file(output_path),
            "generated",
        ),
    )


def write_initial_exports(con: sqlite3.Connection, timestamp: str) -> dict[str, Path]:
    mermaid_path = OUTPUT_DIR / "qsb_map01.mmd"
    summary_path = OUTPUT_DIR / "qsb_map01.md"
    boundary_path = OUTPUT_DIR / "qsb_map01_claim_boundary_report.md"

    mermaid_text = render_mermaid_from_db(con)
    mermaid_path.write_text(mermaid_text, encoding="utf-8")
    summary_path.write_text(render_markdown_summary(con, mermaid_text), encoding="utf-8")
    boundary_path.write_text(render_claim_boundary_report(con), encoding="utf-8")

    insert_export_record(con, "QSB-MAP01-EXPORT-001", "mermaid_mindmap", mermaid_path, timestamp)
    insert_export_record(con, "QSB-MAP01-EXPORT-002", "markdown_summary", summary_path, timestamp)
    insert_export_record(con, "QSB-MAP01-EXPORT-003", "claim_boundary_report", boundary_path, timestamp)
    con.commit()
    return {
        "mermaid": mermaid_path,
        "markdown_summary": summary_path,
        "claim_boundary_report": boundary_path,
    }


def validation_result(rule_id: str, severity: str, passed: bool, message: str, timestamp: str) -> dict[str, str]:
    return {
        "validation_id": f"QSB-MAP01-VAL-{rule_id}",
        "map_id": MAP_ID,
        "rule_id": rule_id,
        "severity": severity,
        "status": "pass" if passed else "fail",
        "message": message,
        "checked_at": timestamp,
    }


def run_validations(con: sqlite3.Connection, timestamp: str) -> list[dict[str, str]]:
    results: list[dict[str, str]] = []

    orphan_maps = con.execute(
        """
        SELECT COUNT(*) AS n
        FROM qsb_map_node AS n
        LEFT JOIN qsb_map AS m ON m.map_id = n.map_id
        WHERE m.map_id IS NULL OR n.map_id <> ?
        """,
        (MAP_ID,),
    ).fetchone()["n"]
    results.append(validation_result("V01", "error", orphan_maps == 0, "Every node belongs to exactly one existing QSB-MAP01 map.", timestamp))

    invalid_parents = con.execute(
        """
        SELECT COUNT(*) AS n
        FROM qsb_map_node AS n
        LEFT JOIN qsb_map_node AS p ON p.node_id = n.parent_node_id
        WHERE n.parent_node_id IS NOT NULL AND p.node_id IS NULL
        """
    ).fetchone()["n"]
    non_root_without_parent = con.execute(
        """
        SELECT COUNT(*) AS n
        FROM qsb_map_node
        WHERE node_type <> 'project_root' AND parent_node_id IS NULL
        """
    ).fetchone()["n"]
    results.append(validation_result("V02", "error", invalid_parents == 0 and non_root_without_parent == 0, "Every non-root node has a valid parent_node_id.", timestamp))

    invalid_edges = con.execute(
        """
        SELECT COUNT(*) AS n
        FROM qsb_map_edge AS e
        LEFT JOIN qsb_map_node AS s ON s.node_id = e.source_node_id
        LEFT JOIN qsb_map_node AS t ON t.node_id = e.target_node_id
        WHERE s.node_id IS NULL OR t.node_id IS NULL
        """
    ).fetchone()["n"]
    results.append(validation_result("V03", "error", invalid_edges == 0, "Every edge references existing source and target nodes.", timestamp))

    unstable_keys = con.execute(
        """
        SELECT COUNT(*) AS n
        FROM qsb_map_node
        WHERE TRIM(canonical_key) = ''
           OR canonical_key GLOB '*[^a-z0-9_]*'
           OR LENGTH(canonical_key) < 3
        """
    ).fetchone()["n"]
    results.append(validation_result("V04", "error", unstable_keys == 0, "Every canonical_key is non-empty and stable-looking.", timestamp))

    formal_without_boundary = con.execute(
        """
        SELECT COUNT(*) AS n
        FROM qsb_map_node AS n
        LEFT JOIN qsb_map_claim_boundary AS b ON b.node_id = n.node_id
        WHERE n.node_type = 'formal_object' AND b.boundary_id IS NULL
        """
    ).fetchone()["n"]
    results.append(validation_result("V05", "error", formal_without_boundary == 0, "Every formal_object node has at least one claim boundary.", timestamp))

    high_risk_without_forbidden = con.execute(
        """
        SELECT COUNT(*) AS n
        FROM qsb_map_claim_boundary
        WHERE overclaim_risk IN ('high', 'critical') AND TRIM(forbidden_use) = ''
        """
    ).fetchone()["n"]
    results.append(validation_result("V06", "error", high_risk_without_forbidden == 0, "Every high-risk node has forbidden_use filled.", timestamp))

    incomplete_source_links = con.execute(
        """
        SELECT COUNT(*) AS n
        FROM qsb_map_source_link
        WHERE TRIM(evidence_role) = '' OR TRIM(claim_use) = ''
        """
    ).fetchone()["n"]
    results.append(validation_result("V07", "error", incomplete_source_links == 0, "Every source_link has evidence_role and claim_use.", timestamp))

    exports_without_hash = con.execute(
        """
        SELECT COUNT(*) AS n
        FROM qsb_map_export
        WHERE content_hash IS NULL OR TRIM(content_hash) = ''
        """
    ).fetchone()["n"]
    results.append(validation_result("V08", "error", exports_without_hash == 0, "Every export record has content_hash after generation.", timestamp))

    text_rows = []
    for table_name, fields in [
        ("qsb_map_node", ["label", "short_description"]),
        ("qsb_map_claim_boundary", ["admissible_use", "forbidden_use", "notes"]),
        ("qsb_map_source_link", ["notes"]),
    ]:
        for field in fields:
            text_rows.extend(
                row[field] or ""
                for row in con.execute(f"SELECT {field} FROM {table_name}").fetchall()
            )
    forbidden_hits = [
        wording
        for wording in FORBIDDEN_CONFIRMATION_WORDING
        if any(wording.lower() in text.lower() for text in text_rows)
    ]
    results.append(validation_result("V09", "error", not forbidden_hits, "No node/admissible_use/source note contains forbidden confirmation wording.", timestamp))

    results.append(validation_result("V10", "error", MERMAID_GENERATED_FROM_DB, "Mermaid export is generated from database nodes, not manually hardcoded as the canonical source.", timestamp))

    con.executemany(
        """
        INSERT INTO qsb_map_validation_result (
            validation_id, map_id, rule_id, severity, status, message, checked_at
        )
        VALUES (
            :validation_id, :map_id, :rule_id, :severity, :status, :message, :checked_at
        )
        """,
        results,
    )
    con.commit()
    return results


def table_counts(con: sqlite3.Connection) -> dict[str, int]:
    tables = [
        "qsb_map",
        "qsb_map_node",
        "qsb_map_edge",
        "qsb_map_alias",
        "qsb_map_source_link",
        "qsb_map_claim_boundary",
        "qsb_map_export",
        "qsb_map_validation_result",
    ]
    return {table: row_count(con, table) for table in tables}


def view_counts(con: sqlite3.Connection) -> dict[str, int]:
    views = [
        "v_qsb_map_search",
        "v_qsb_map_claim_risk",
        "v_qsb_map_source_context",
    ]
    return {view: row_count(con, view) for view in views}


def write_validation_report(results: list[dict[str, str]], counts: dict[str, int]) -> Path:
    path = OUTPUT_DIR / "qsb_map01_validation_report.json"
    payload = {
        "map_id": MAP_ID,
        "timestamp": utc_now(),
        "validation_status": "pass" if all(row["status"] == "pass" for row in results) else "fail",
        "results": results,
        "row_counts": counts,
        "claim_boundary_summary": CLAIM_BOUNDARY_SUMMARY,
    }
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return path


def write_manifest(
    con: sqlite3.Connection,
    output_paths: dict[str, Path],
    validation_report_path: Path,
    run_summary_path: Path,
    timestamp: str,
) -> Path:
    path = OUTPUT_DIR / "qsb_map01_seed_manifest.json"
    text_outputs = {
        "qsb_map01.mmd": output_paths["mermaid"],
        "qsb_map01.md": output_paths["markdown_summary"],
        "qsb_map01_claim_boundary_report.md": output_paths["claim_boundary_report"],
        "qsb_map01_validation_report.json": validation_report_path,
        "QSB-MAP01-DWH-A_RUN_SUMMARY.md": run_summary_path,
    }
    payload = {
        "script_path": str(SCRIPT_PATH),
        "schema_path": "scripts/qsb_map01_dwh_a/schema.sql",
        "database_path": rel(DB_PATH),
        "output_paths": {name: rel(path_value) for name, path_value in text_outputs.items()},
        "row_counts_per_table": table_counts(con),
        "view_counts": view_counts(con),
        "hashes_of_generated_text_outputs": {
            name: sha256_file(path_value) for name, path_value in text_outputs.items()
        },
        "timestamp": timestamp,
        "claim_boundary_summary": CLAIM_BOUNDARY_SUMMARY,
        "sandbox_only": True,
        "production_dwh_mutated": False,
        "source_hub_schema_patched": False,
        "relalg_computation_performed": False,
    }
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return path


def write_run_summary(con: sqlite3.Connection, results: list[dict[str, str]]) -> Path:
    path = OUTPUT_DIR / "QSB-MAP01-DWH-A_RUN_SUMMARY.md"
    counts = table_counts(con)
    result_lines = [
        f"- {row['rule_id']}: {row['status']} - {row['message']}"
        for row in results
    ]
    count_lines = [f"- {table}: {count}" for table, count in counts.items()]
    text = dedent(
        f"""\
        # QSB-MAP01-DWH-A Run Summary

        Status: sandbox-only SQLite mart and Mermaid export dry run.

        Claim Boundary: {CLAIM_BOUNDARY_SUMMARY}

        No production DWH mutation was performed. No Source-Hub schema patch was
        performed. No existing EXTRACT tables or project data were modified. No
        physical claim, spacetime claim, causality claim, or RELALG computation
        is introduced by this run.

        ## Outputs

        - `{rel(DB_PATH)}`
        - `runs/QSB-MAP01-DWH-A/qsb_map01_seed_manifest.json`
        - `runs/QSB-MAP01-DWH-A/qsb_map01_validation_report.json`
        - `runs/QSB-MAP01-DWH-A/qsb_map01.mmd`
        - `runs/QSB-MAP01-DWH-A/qsb_map01.md`
        - `runs/QSB-MAP01-DWH-A/qsb_map01_claim_boundary_report.md`
        - `runs/QSB-MAP01-DWH-A/QSB-MAP01-DWH-A_RUN_SUMMARY.md`

        ## Row Counts

        {chr(10).join(count_lines)}

        ## Validation

        {chr(10).join(result_lines)}
        """
    )
    path.write_text(text, encoding="utf-8")
    return path


def verify_required_outputs(paths: list[Path]) -> None:
    missing = [rel(path) for path in paths if not path.exists()]
    if missing:
        raise FileNotFoundError("Missing required outputs: " + ", ".join(missing))


def main() -> None:
    timestamp = utc_now()
    with connect_fresh_database() as con:
        seed_map(con, timestamp)
        nodes = seed_nodes(con)
        seed_edges(con, nodes)
        seed_aliases(con)
        seed_source_links(con)
        seed_claim_boundaries(con)
        con.commit()

        output_paths = write_initial_exports(con, timestamp)
        results = run_validations(con, utc_now())
        validation_report_path = write_validation_report(results, table_counts(con))
        run_summary_path = write_run_summary(con, results)
        manifest_path = write_manifest(
            con,
            output_paths,
            validation_report_path,
            run_summary_path,
            timestamp,
        )

    verify_required_outputs(
        [
            DB_PATH,
            manifest_path,
            validation_report_path,
            output_paths["mermaid"],
            output_paths["markdown_summary"],
            output_paths["claim_boundary_report"],
            run_summary_path,
        ]
    )
    print(f"created sandbox mart: {rel(DB_PATH)}")
    print(f"validation report: {rel(validation_report_path)}")
    print(f"validation status: {'pass' if all(row['status'] == 'pass' for row in results) else 'fail'}")


if __name__ == "__main__":
    main()
