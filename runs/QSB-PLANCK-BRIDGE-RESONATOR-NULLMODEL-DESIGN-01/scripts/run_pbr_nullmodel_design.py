#!/usr/bin/env python3
"""Create the PBR nullmodel design run package."""
from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from typing import Dict, Iterable, List

RUN_ID = "QSB-PLANCK-BRIDGE-RESONATOR-NULLMODEL-DESIGN-01"
PREVIOUS_RUN = "QSB-PLANCK-BRIDGE-RESONATOR-RESULT-REVIEW-01"
SCHEMA = "qsb_planck_bridge"
EXECUTION_STATUS = "design_only_not_executed"
PHYSICAL_CLAIM_RELEASE = "blocked_no_physics_claim"
CLAIM_STATUS = "nullmodel_design_only"
EXTERNAL_READINESS = "internal_only"
NEXT_GATE = "nullmodel_execution_required"
DESIGN_STATUS = "nullmodel_design_completed_execution_required"


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    clean = "\n".join(line.rstrip() for line in text.strip().splitlines()) + "\n"
    path.write_text(clean, encoding="utf-8")


def write_csv(path: Path, rows: Iterable[Dict[str, object]], fieldnames: List[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def nullmodels() -> List[Dict[str, str]]:
    return [
        {
            "nullmodel_id": "NM-001",
            "nullmodel_key": "label_permutation_null",
            "purpose": "Prueft, ob die beobachtete Rang-6-Lag-Klassenstruktur durch Index-Labels oder geordnete Paarbenennung getrieben wird.",
            "preserved_quantities": "Matrixform 42x42; PSD-Ausgangsbefund als Referenz; Paaranzahl; Lag-Multimenge; Spektral-Auswertemethode.",
            "randomized_quantities": "Indexlabels i und j; pair_id-Zuordnung; Reihenfolge der gerichteten Paarfeatures.",
            "expected_diagnostic_outputs": "Rank-Verteilung; Nullitaet-Verteilung; Eigenwertspektren; Trefferquote Rang 6; Abweichung zur beobachteten Lag-Klassenblockung.",
            "admissibility_criteria": "Permutation ist bijektiv; keine Feature-Duplikate; Matrixdimension bleibt 42x42; kein Nullmodel-Output wird als ausgefuehrt behauptet.",
            "failure_modes": "Permutation zerstoert erforderliche Paarstruktur; nicht-bijektive Labelabbildung; zufaellige Ordnung nicht dokumentiert; Rangvergleich ohne Toleranzangabe.",
            "required_input_artifacts": "Vorheriger Result-Review; K_candidate-Matrix; pair_id-Liste; Lag-Zuordnung; Spektral-Readout-Konfiguration.",
            "execution_authorization_status": EXECUTION_STATUS,
            "claim_boundary": "Nur Designkontrolle; keine physikalische Claim-Freigabe; affirmative physikalische Aussagen sind gesperrt.",
            "next_gate_implication": "Wenn formal passend, Nullmodel-Ausfuehrung mit Seeds und Ergebnisfeldern autorisieren.",
        },
        {
            "nullmodel_id": "NM-002",
            "nullmodel_key": "lag_preserving_shuffle_null",
            "purpose": "Prueft, ob innerhalb einer Lag-Klasse Information ueber reine Lag-Mitgliedschaft hinaus getragen wird.",
            "preserved_quantities": "Lag-Zugehoerigkeit; Anzahl Features je Lag; Matrixdimension; globale Trace-Zielgroesse; Auswertetoleranzen.",
            "randomized_quantities": "Featureordnung und Wertezuordnung innerhalb gleicher Lag-Klasse; optionale blockinterne Paarpositionen.",
            "expected_diagnostic_outputs": "Innerhalb-Lag-Streuung; Rang- und Nullitaetsverteilung; Blockkoharenzmetriken; Vergleich der +k/-k-Beziehung.",
            "admissibility_criteria": "Shuffle bleibt lag-erhaltend; keine Cross-Lag-Vermischung; Trace- und Symmetriebedingungen werden protokolliert.",
            "failure_modes": "Lag-Grenzen werden verletzt; blockinterne Randomisierung ist nicht reproduzierbar; PSD-Reparatur veraendert das Nullmodell unprotokolliert.",
            "required_input_artifacts": "Lag-Zuordnung je pair_id; K_candidate-Matrix; Trace-Referenz; Spektraldiagnostik-Spezifikation.",
            "execution_authorization_status": EXECUTION_STATUS,
            "claim_boundary": "Kontrolliert nur formale Binnenstruktur; keine Aussage ueber reale Dynamik oder physikalische Dimensionen.",
            "next_gate_implication": "Bei bestandener Designpruefung als Pflicht-Nullmodell vor staerkerer Interpretation ausfuehren.",
        },
        {
            "nullmodel_id": "NM-003",
            "nullmodel_key": "random_gram_psd_null",
            "purpose": "Vergleicht die aktuelle PSD-Matrix mit generischen PSD-Gram-Matrizen gleicher Form, Trace und approximativer Rangvorgaben.",
            "preserved_quantities": "Matrixform 42x42; PSD-Eigenschaft; Ziel-Trace; approximative Rangklasse; numerische Toleranzfamilie.",
            "randomized_quantities": "Gram-Vektororientierungen; Eigenbasis; nicht durch Lag definierte Korrelationen; Seed-abhaengige Stichprobe.",
            "expected_diagnostic_outputs": "Eigenwertquantile; Ranghaeufigkeit; Nullitaetsverteilung; Distanz zur Lag-Klassen-Signatur; PSD-Minimum-Eigenwert.",
            "admissibility_criteria": "Matrix ist symmetrisch; PSD innerhalb Toleranz; Trace-Matching dokumentiert; approximativer Rangzwang ist explizit.",
            "failure_modes": "Trace passt nicht; Rangzwang dominiert Ergebnis; numerische PSD-Projektion verschleiert Konstruktion; Seedanzahl zu klein.",
            "required_input_artifacts": "K_candidate-Matrix; Trace; Rang- und Toleranzdefinition; PSD-Testparameter; Spektral-Auswertecode oder Feldliste.",
            "execution_authorization_status": EXECUTION_STATUS,
            "claim_boundary": "Vergleich gegen generische formale PSD-Baselines; keine empirische Validierung und keine physikalische Freigabe.",
            "next_gate_implication": "Erfordert vor Ausfuehrung Festlegung von Seedplan, Stichprobengroesse und Rang-Toleranz.",
        },
        {
            "nullmodel_id": "NM-004",
            "nullmodel_key": "directed_pair_rewire_null",
            "purpose": "Prueft, ob die gerichtete Paargraph-Struktur allein ausreicht, um das beobachtete Spektralmuster zu induzieren.",
            "preserved_quantities": "42 gerichtete Paarfeatures; Knotenmenge mit 7 Indizes; In-/Out-Degree-Zielstruktur; Vergleichsdiagnostik.",
            "randomized_quantities": "Gerichtete Kanten-/Paarzuordnung; pair_id-Rewire; Zuordnung von Lags nach Rewire-Regel.",
            "expected_diagnostic_outputs": "Graphstrukturmetriken; Rangverteilung; Lag-Achsen-Kollapsmetrik; Parallel-/Antiparallel-Zaehlungen; Rewire-Ablehnungsrate.",
            "admissibility_criteria": "Keine Selbstkanten, wenn Ausgangsmodell diese ausschliesst; gerichtete Paaranzahl bleibt 42; Rewire-Regel ist eindeutig.",
            "failure_modes": "Rewire erzeugt unzulaessige Selbstpaare; Mehrfachkanten werden falsch behandelt; Lag-Begriffe werden nach Rewire uneindeutig.",
            "required_input_artifacts": "Paargraph-Spezifikation; pair_id-Tabelle; Lag-Regel; K_candidate-Referenz; Spektralvergleichsfelder.",
            "execution_authorization_status": EXECUTION_STATUS,
            "claim_boundary": "Testet Konstruktionsabhaengigkeit der gerichteten Paare; keine Aussage ueber physikalische Existenz.",
            "next_gate_implication": "Vor Ausfuehrung muss festgelegt werden, ob Lags neu berechnet oder als Labels transportiert werden.",
        },
        {
            "nullmodel_id": "NM-005",
            "nullmodel_key": "sign_flip_antiparallel_null",
            "purpose": "Prueft die Robustheit der +k/-k-Antiparallel-Beziehungen unter Sign-Flip- oder Orientierungsstoerungen.",
            "preserved_quantities": "Lag-Paarung +k/-k; Matrixdimension; Ausgangszaehlung parallel_count und antiparallel_count als Referenz; PSD-Gate als Diagnose.",
            "randomized_quantities": "Vorzeichen je Lag-Achse; Orientierung einzelner Paarfeatures; kontrollierte Flip-Rate.",
            "expected_diagnostic_outputs": "Parallel-/Antiparallel-Zaehldifferenzen; Rangstabilitaet; PSD-Minimum-Eigenwert; Flip-Sensitivitaetskurve.",
            "admissibility_criteria": "Flip-Regel ist vorab fixiert; Orientierungsaenderung wird protokolliert; PSD-Status wird gemessen und nicht vorausgesetzt.",
            "failure_modes": "Flip-Regel vermischt Vorzeichen und Labelpermutation; PSD-Verlust wird nicht berichtet; Orientierungsaenderung ist nicht reversibel.",
            "required_input_artifacts": "+k/-k-Lagachsenliste; pair_id-Orientierungen; K_candidate-Matrix; PSD- und Spektraldiagnostik.",
            "execution_authorization_status": EXECUTION_STATUS,
            "claim_boundary": "Robustheitsdesign fuer formale Antiparallelstruktur; keine Freigabe von Dimensionen- oder Raumzeit-Claims.",
            "next_gate_implication": "Erfordert Ausfuehrungsplan mit Flip-Raten, Seeds und Akzeptanzlogik.",
        },
    ]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", type=Path, default=Path("."))
    parser.add_argument("--run-dir", type=Path, default=Path(f"runs/{RUN_ID}"))
    args = parser.parse_args()

    repo_root = args.repo_root.resolve()
    run_dir = (repo_root / args.run_dir).resolve() if not args.run_dir.is_absolute() else args.run_dir.resolve()
    data_dir = run_dir / "data"
    docs_dir = run_dir / "docs"
    sql_dir = run_dir / "sql"

    families = [
        {"run_id": RUN_ID, **family, "next_gate_implication": NEXT_GATE}
        for family in nullmodels()
    ]
    summary = {
        "run_id": RUN_ID,
        "previous_run_id": PREVIOUS_RUN,
        "design_status": DESIGN_STATUS,
        "execution_status": EXECUTION_STATUS,
        "claim_status": CLAIM_STATUS,
        "physical_claim_release": PHYSICAL_CLAIM_RELEASE,
        "external_readiness": EXTERNAL_READINESS,
        "next_gate": NEXT_GATE,
        "schema_name": SCHEMA,
        "nullmodel_family_count": len(families),
        "formal_reference_finding": "Die K_candidate-Matrix ist PSD innerhalb numerischer Toleranz und zeigt eine Rang-6 gerichtete Lag-Klassen-Gramstruktur. Dies ist ein formaler Matrixstruktur-Befund; alle physikalischen Claims bleiben gesperrt.",
    }
    write_csv(data_dir / "nullmodel_design_summary.csv", [summary], list(summary.keys()))
    write_csv(data_dir / "nullmodel_family_spec.csv", families, list(families[0].keys()))

    claim_rows = [
        {
            "run_id": RUN_ID,
            "boundary_id": "CB-001",
            "claim_key": "formal_matrix_structure_only",
            "status": "allowed",
            "claim_boundary_text": "Erlaubt ist nur der formale Matrixstruktur-Befund zur PSD-Toleranz und Rang-6-Lag-Klassen-Gramstruktur.",
        },
        {
            "run_id": RUN_ID,
            "boundary_id": "CB-002",
            "claim_key": "qsb_physical_validation",
            "status": "blocked",
            "claim_boundary_text": "Die Aussage 'QSB is physically validated' ist als affirmative Aussage gesperrt.",
        },
        {
            "run_id": RUN_ID,
            "boundary_id": "CB-003",
            "claim_key": "pbr_physical_existence",
            "status": "blocked",
            "claim_boundary_text": "Die Aussage 'PBR exists physically' ist als affirmative Aussage gesperrt.",
        },
        {
            "run_id": RUN_ID,
            "boundary_id": "CB-004",
            "claim_key": "six_lag_axes_as_spacetime_dimensions",
            "status": "blocked",
            "claim_boundary_text": "Die Aussage 'The six lag axes are spacetime dimensions' ist als affirmative Aussage gesperrt.",
        },
        {
            "run_id": RUN_ID,
            "boundary_id": "CB-005",
            "claim_key": "spacetime_emergence_proof",
            "status": "blocked",
            "claim_boundary_text": "Die Aussage 'Spacetime emergence is proven' ist als affirmative Aussage gesperrt.",
        },
        {
            "run_id": RUN_ID,
            "boundary_id": "CB-006",
            "claim_key": "empirical_validation",
            "status": "blocked",
            "claim_boundary_text": "Die Aussage 'Empirical validation exists' ist als affirmative Aussage gesperrt.",
        },
    ]
    write_csv(data_dir / "claim_boundaries.csv", claim_rows, list(claim_rows[0].keys()))

    input_rows = [
        {"run_id": RUN_ID, "artifact_id": "IN-001", "artifact_key": "result_review_summary", "required_path": f"runs/{PREVIOUS_RUN}/data/result_review_summary.csv", "required_for": "lineage_reference", "status": "required_before_execution"},
        {"run_id": RUN_ID, "artifact_id": "IN-002", "artifact_key": "k_candidate_matrix", "required_path": "prior PBR matrix artifact path to be resolved before execution", "required_for": "all_nullmodels", "status": "required_before_execution"},
        {"run_id": RUN_ID, "artifact_id": "IN-003", "artifact_key": "pair_id_table", "required_path": "pair_id table with i|j directed pairs", "required_for": "label_permutation_null;directed_pair_rewire_null", "status": "required_before_execution"},
        {"run_id": RUN_ID, "artifact_id": "IN-004", "artifact_key": "lag_assignment_table", "required_path": "lag table with lag=j-i and +k/-k relations", "required_for": "lag_preserving_shuffle_null;sign_flip_antiparallel_null", "status": "required_before_execution"},
        {"run_id": RUN_ID, "artifact_id": "IN-005", "artifact_key": "spectral_readout_config", "required_path": "spectral readout tolerance and diagnostic config", "required_for": "all_nullmodels", "status": "required_before_execution"},
        {"run_id": RUN_ID, "artifact_id": "IN-006", "artifact_key": "seed_plan", "required_path": "future execution seed manifest", "required_for": "all_nullmodels", "status": "not_created_in_design_run"},
    ]
    write_csv(data_dir / "input_artifact_requirements.csv", input_rows, list(input_rows[0].keys()))

    gate_rows = [
        {
            "run_id": RUN_ID,
            "gate_id": "GATE-001",
            "gate_name": "nullmodel_design_gate",
            "gate_decision": "passed_design_only",
            "execution_status": EXECUTION_STATUS,
            "physical_claim_release": PHYSICAL_CLAIM_RELEASE,
            "external_readiness": EXTERNAL_READINESS,
            "next_gate": NEXT_GATE,
            "revision_trigger": "nullmodel_design_revision_required if any required family, input artifact, diagnostic output, or claim boundary is missing",
        }
    ]
    write_csv(data_dir / "gate_decision.csv", gate_rows, list(gate_rows[0].keys()))

    diagnostic_rows = []
    for family in families:
        for diag_key in ["rank_distribution", "nullity_distribution", "eigenvalue_spectrum", "lag_signature_distance", "psd_min_eigenvalue"]:
            diagnostic_rows.append({
                "run_id": RUN_ID,
                "nullmodel_key": family["nullmodel_key"],
                "diagnostic_key": diag_key,
                "required": "true",
                "execution_status": EXECUTION_STATUS,
                "output_claim_status": "not_produced_in_design_run",
            })
    write_csv(data_dir / "nullmodel_diagnostics_required.csv", diagnostic_rows, list(diagnostic_rows[0].keys()))

    failure_rows = []
    for family in families:
        for idx, mode in enumerate(family["failure_modes"].split("; "), start=1):
            failure_rows.append({
                "run_id": RUN_ID,
                "nullmodel_key": family["nullmodel_key"],
                "failure_mode_id": f"{family['nullmodel_id']}-FM-{idx:02d}",
                "failure_mode": mode,
                "mitigation_status": "must_be_handled_before_execution",
            })
    write_csv(data_dir / "nullmodel_failure_modes.csv", failure_rows, list(failure_rows[0].keys()))

    auth_rows = [
        {
            "run_id": RUN_ID,
            "nullmodel_key": family["nullmodel_key"],
            "execution_authorization_status": EXECUTION_STATUS,
            "authorization_note": "Dieses Paket spezifiziert nur das Design. Es erzeugt keine Nullmodell-Stichproben und keine Ergebnisdiagnostik.",
            "required_before_execution": "seed_plan;input_artifact_resolution;execution_config;output_field_list",
        }
        for family in families
    ]
    write_csv(data_dir / "nullmodel_execution_authorization.csv", auth_rows, list(auth_rows[0].keys()))

    manifest = {
        "run_id": RUN_ID,
        "previous_run_id": PREVIOUS_RUN,
        "previous_git_chain": ["71a69d8", "7a8cbc2", "3a486ca", "0d74576", "38aa3ae", "8dd7a1e"],
        "schema": SCHEMA,
        "design_status": DESIGN_STATUS,
        "execution_status": EXECUTION_STATUS,
        "claim_status": CLAIM_STATUS,
        "physical_claim_release": PHYSICAL_CLAIM_RELEASE,
        "external_readiness": EXTERNAL_READINESS,
        "next_gate": NEXT_GATE,
        "nullmodel_families": [family["nullmodel_key"] for family in families],
        "validation_results": f"runs/{RUN_ID}/validation/validation_results.csv",
        "claim_boundary": "No physical claims are released. Forbidden physics phrases are allowed only in blocked, prohibited, or claim-boundary contexts.",
    }
    with (data_dir / "nullmodel_design_manifest.json").open("w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False)
        f.write("\n")

    write_text(run_dir / "README.md", f"""
    # {RUN_ID}

    Design-only run package for PBR nullmodels.

    ## Status

    - `design_status = {DESIGN_STATUS}`
    - `execution_status = {EXECUTION_STATUS}`
    - `claim_status = {CLAIM_STATUS}`
    - `physical_claim_release = {PHYSICAL_CLAIM_RELEASE}`
    - `external_readiness = {EXTERNAL_READINESS}`
    - `next_gate = {NEXT_GATE}`

    ## Scope

    This package defines five nullmodel families required before any stronger interpretation of the rank-6 lag-class spectral readout can be considered. It does not execute nullmodels and does not claim nullmodel results.

    ## Output

    Validation output is written to `validation/validation_results.csv`.
    """)

    write_text(run_dir / f"{RUN_ID}.md", f"""
    # {RUN_ID}

    ## Befund

    Die K_candidate-Matrix ist PSD innerhalb numerischer Toleranz und zeigt eine Rang-6 gerichtete Lag-Klassen-Gramstruktur. Dies ist ein formaler Matrixstruktur-Befund; alle physikalischen Claims bleiben gesperrt.

    Dieses Paket definiert fuenf Nullmodell-Familien fuer die naechste formale Pruefung: `label_permutation_null`, `lag_preserving_shuffle_null`, `random_gram_psd_null`, `directed_pair_rewire_null` und `sign_flip_antiparallel_null`.

    ## Interpretation

    Das Design trennt Label-, Lag-, PSD-Gram-, gerichtete-Paargraph- und Orientierungs-/Vorzeichenkontrollen. Die Spezifikation dient dazu, das DWH und die spaetere Ausfuehrung mit eindeutigen Feldern, Claim-Grenzen und Gate-Entscheidungen vorzubereiten.

    ## Hypothese

    Die Rang-6-Lag-Klassenstruktur kann eine Folge der formalen Konstruktion, der Labelwahl, der Lag-Mitgliedschaft, der PSD-Gram-Bedingung, der gerichteten Paarstruktur oder der +k/-k-Orientierungsdefinition sein. Diese Moeglichkeiten sind vor staerkerer Interpretation durch Nullmodelle zu pruefen.

    ## Offene Luecke

    Dieses Paket fuehrt keine Nullmodelle aus. Es erzeugt keine Stichproben, keine Eigenwertverteilungen und keine empirischen oder physikalischen Befunde. Die benoetigten Input-Artefakte und Seed-/Ausfuehrungsplaene muessen vor dem naechsten Gate festgelegt werden.

    ## Claim Boundary

    - `design_status = {DESIGN_STATUS}`
    - `execution_status = {EXECUTION_STATUS}`
    - `claim_status = {CLAIM_STATUS}`
    - `physical_claim_release = {PHYSICAL_CLAIM_RELEASE}`
    - `external_readiness = {EXTERNAL_READINESS}`
    - `next_gate = {NEXT_GATE}`

    Es werden keine physikalischen Claims freigegeben.
    """)

    write_text(run_dir / "RUN_COMMANDS_PBR_NULLMODEL_DESIGN01.md", f"""
    # Run Commands: {RUN_ID}

    ## Generate artifacts

    ```bash
    python runs/{RUN_ID}/scripts/run_pbr_nullmodel_design.py --repo-root . --run-dir runs/{RUN_ID}
    ```

    ## Validate package

    ```bash
    python runs/{RUN_ID}/scripts/validate_pbr_nullmodel_design.py runs/{RUN_ID}
    ```

    ## Optional DWH import

    ```bash
    RUN_DIR="runs/{RUN_ID}"
    psql -d qsb_research_dwh -f runs/{RUN_ID}/sql/001_create_qsb_pbr_nullmodel_design.sql
    psql -d qsb_research_dwh -f runs/{RUN_ID}/sql/002_insert_qsb_pbr_nullmodel_design.sql
    psql -d qsb_research_dwh -f runs/{RUN_ID}/sql/003_validation_queries.sql
    ```

    The import is repeatable for this run package. The insert script clears rows for `{RUN_ID}` using table-specific keys and runs inside one transaction.

    ## Local checks

    ```bash
    git diff --check
    git status --short
    ```
    """)

    write_text(docs_dir / "PBR_NULLMODEL_DESIGN_SUMMARY_DE.md", f"""
    # PBR Nullmodell-Design Zusammenfassung

    ## Befund

    Die K_candidate-Matrix ist PSD innerhalb numerischer Toleranz und zeigt eine Rang-6 gerichtete Lag-Klassen-Gramstruktur. Dies ist ein formaler Matrixstruktur-Befund; alle physikalischen Claims bleiben gesperrt.

    Das vorliegende Designpaket beschreibt fuenf erforderliche Nullmodell-Familien. Es ist fuer das DWH als Designstand dokumentiert und enthaelt keine ausgefuehrten Nullmodell-Ergebnisse.

    ## Interpretation

    Die Nullmodelle adressieren getrennte formale Alternativen: Label-Effekte, Lag-Mitgliedschaft, generische PSD-Gram-Strukturen, gerichtete Paargraph-Struktur und Vorzeichen-/Orientierungsrobustheit.

    ## Hypothese

    Erst nach ausgefuehrten Nullmodellen kann beurteilt werden, ob die beobachtete Rang-6-Struktur ueber naheliegende formale Konstruktionskontrollen hinaus auffaellig bleibt.

    ## Offene Luecke

    Seedplan, Input-Artefaktauflosung, Ausfuehrungskonfiguration und Ergebnisfeldlisten fehlen noch fuer das naechste Gate.

    ## Claim Boundary

    `physical_claim_release = {PHYSICAL_CLAIM_RELEASE}`. Es werden keine physikalischen Claims freigegeben.
    """)

    write_text(docs_dir / "PBR_NULLMODEL_DESIGN_CLAIM_BOUNDARY_DE.md", f"""
    # PBR Nullmodell-Design Claim Boundary

    ## Befund

    Dieses Paket ist ein Design-only-Artefakt. Es dokumentiert, welche formalen Kontrollen vor staerkerer Interpretation erforderlich sind.

    ## Interpretation

    Verbotene physikalische Formulierungen duerfen nur als gesperrte, verbotene oder Claim-Boundary-Texte erscheinen. Affirmative physikalische Claims sind nicht Teil dieses Pakets.

    ## Hypothese

    Die spaetere Nullmodell-Ausfuehrung kann die formale Robustheit einschaetzen. Sie ersetzt keine physikalische Validierung.

    ## Offene Luecke

    Nullmodelle wurden nicht ausgefuehrt. Keine empirische Validierung liegt vor.

    ## Claim Boundary

    Die Aussage 'QSB is physically validated' ist gesperrt. Die Aussage 'PBR exists physically' ist gesperrt. Die Aussage 'The six lag axes are spacetime dimensions' ist gesperrt. Die Aussage 'Spacetime emergence is proven' ist gesperrt. Die Aussage 'Empirical validation exists' ist gesperrt.
    """)

    write_text(docs_dir / "PBR_NULLMODEL_DESIGN_NEXT_GATE_DE.md", f"""
    # PBR Nullmodell-Design Next Gate

    ## Befund

    Das Design-Gate ist formal erfuellt, wenn alle fuenf Nullmodell-Familien, ihre Eingaben, Diagnostiken, Fehlermodi und Claim-Grenzen dokumentiert sind.

    ## Interpretation

    Das naechste Gate ist `nullmodel_execution_required`. Falls eine Familie, ein Input-Artefakt, eine Diagnostik oder eine Claim-Grenze fehlt, ist `nullmodel_design_revision_required` zu setzen.

    ## Hypothese

    Eine spaetere Ausfuehrung kann zeigen, welche Teile des Rang-6-Readouts durch die formale Konstruktion erwartbar sind.

    ## Offene Luecke

    Ohne Ausfuehrung bleiben Verteilungen, p-Werte, Quantile, Robustheitskurven und Akzeptanzraten offen.

    ## Claim Boundary

    Auch bei bestandenem Design-Gate bleibt `physical_claim_release = {PHYSICAL_CLAIM_RELEASE}`.
    """)

    create_sql = f"""
    -- QSB Planck Bridge Resonator Nullmodel Design 01

    CREATE SCHEMA IF NOT EXISTS {SCHEMA};

    CREATE TABLE IF NOT EXISTS {SCHEMA}.pbr_nullmodel_design_summary (
        run_id text PRIMARY KEY,
        previous_run_id text NOT NULL,
        design_status text NOT NULL,
        execution_status text NOT NULL,
        claim_status text NOT NULL,
        physical_claim_release text NOT NULL,
        external_readiness text NOT NULL,
        next_gate text NOT NULL,
        schema_name text NOT NULL,
        nullmodel_family_count integer NOT NULL,
        formal_reference_finding text NOT NULL
    );

    CREATE TABLE IF NOT EXISTS {SCHEMA}.pbr_nullmodel_family_spec (
        run_id text NOT NULL,
        nullmodel_id text NOT NULL,
        nullmodel_key text NOT NULL,
        purpose text NOT NULL,
        preserved_quantities text NOT NULL,
        randomized_quantities text NOT NULL,
        expected_diagnostic_outputs text NOT NULL,
        admissibility_criteria text NOT NULL,
        failure_modes text NOT NULL,
        required_input_artifacts text NOT NULL,
        execution_authorization_status text NOT NULL,
        claim_boundary text NOT NULL,
        next_gate_implication text NOT NULL,
        PRIMARY KEY (run_id, nullmodel_id)
    );

    CREATE TABLE IF NOT EXISTS {SCHEMA}.pbr_nullmodel_claim_boundaries (
        run_id text NOT NULL,
        boundary_id text NOT NULL,
        claim_key text NOT NULL,
        status text NOT NULL,
        claim_boundary_text text NOT NULL,
        PRIMARY KEY (run_id, boundary_id)
    );

    CREATE TABLE IF NOT EXISTS {SCHEMA}.pbr_nullmodel_input_artifact_requirements (
        run_id text NOT NULL,
        artifact_id text NOT NULL,
        artifact_key text NOT NULL,
        required_path text NOT NULL,
        required_for text NOT NULL,
        status text NOT NULL,
        PRIMARY KEY (run_id, artifact_id)
    );

    CREATE TABLE IF NOT EXISTS {SCHEMA}.pbr_nullmodel_gate_decision (
        run_id text NOT NULL,
        gate_id text NOT NULL,
        gate_name text NOT NULL,
        gate_decision text NOT NULL,
        execution_status text NOT NULL,
        physical_claim_release text NOT NULL,
        external_readiness text NOT NULL,
        next_gate text NOT NULL,
        revision_trigger text NOT NULL,
        PRIMARY KEY (run_id, gate_id)
    );

    CREATE TABLE IF NOT EXISTS {SCHEMA}.pbr_nullmodel_diagnostics_required (
        run_id text NOT NULL,
        nullmodel_key text NOT NULL,
        diagnostic_key text NOT NULL,
        required boolean NOT NULL,
        execution_status text NOT NULL,
        output_claim_status text NOT NULL,
        PRIMARY KEY (run_id, nullmodel_key, diagnostic_key)
    );

    CREATE TABLE IF NOT EXISTS {SCHEMA}.pbr_nullmodel_failure_modes (
        run_id text NOT NULL,
        nullmodel_key text NOT NULL,
        failure_mode_id text NOT NULL,
        failure_mode text NOT NULL,
        mitigation_status text NOT NULL,
        PRIMARY KEY (run_id, failure_mode_id)
    );

    CREATE TABLE IF NOT EXISTS {SCHEMA}.pbr_nullmodel_execution_authorization (
        run_id text NOT NULL,
        nullmodel_key text NOT NULL,
        execution_authorization_status text NOT NULL,
        authorization_note text NOT NULL,
        required_before_execution text NOT NULL,
        PRIMARY KEY (run_id, nullmodel_key)
    );

    CREATE TABLE IF NOT EXISTS {SCHEMA}.pbr_nullmodel_validation_results (
        run_id text NOT NULL,
        validation_id text NOT NULL,
        check_name text NOT NULL,
        status text NOT NULL,
        severity text NOT NULL,
        observed_value text NOT NULL,
        expected_value text NOT NULL,
        message text NOT NULL,
        blocking text NOT NULL,
        PRIMARY KEY (run_id, validation_id)
    );

    ALTER TABLE {SCHEMA}.pbr_nullmodel_design_summary
        ADD COLUMN IF NOT EXISTS run_id text;

    ALTER TABLE {SCHEMA}.pbr_nullmodel_family_spec
        ADD COLUMN IF NOT EXISTS run_id text;

    ALTER TABLE {SCHEMA}.pbr_nullmodel_family_spec
        ADD COLUMN IF NOT EXISTS next_gate_implication text;

    ALTER TABLE {SCHEMA}.pbr_nullmodel_claim_boundaries
        ADD COLUMN IF NOT EXISTS run_id text;

    ALTER TABLE {SCHEMA}.pbr_nullmodel_input_artifact_requirements
        ADD COLUMN IF NOT EXISTS run_id text;

    ALTER TABLE {SCHEMA}.pbr_nullmodel_gate_decision
        ADD COLUMN IF NOT EXISTS run_id text;

    ALTER TABLE {SCHEMA}.pbr_nullmodel_diagnostics_required
        ADD COLUMN IF NOT EXISTS run_id text;

    ALTER TABLE {SCHEMA}.pbr_nullmodel_failure_modes
        ADD COLUMN IF NOT EXISTS run_id text;

    ALTER TABLE {SCHEMA}.pbr_nullmodel_execution_authorization
        ADD COLUMN IF NOT EXISTS run_id text;

    ALTER TABLE {SCHEMA}.pbr_nullmodel_validation_results
        ADD COLUMN IF NOT EXISTS run_id text;

    UPDATE {SCHEMA}.pbr_nullmodel_validation_results
    SET run_id = '{RUN_ID}'
    WHERE run_id IS NULL;
    """
    write_text(sql_dir / "001_create_qsb_pbr_nullmodel_design.sql", create_sql)

    insert_sql = f"""
    -- Import CSV artifacts for {RUN_ID}.
    -- Run from repository root after 001_create_qsb_pbr_nullmodel_design.sql.

    \\set ON_ERROR_STOP on
    BEGIN;

    DELETE FROM {SCHEMA}.pbr_nullmodel_validation_results WHERE run_id = '{RUN_ID}';
    DELETE FROM {SCHEMA}.pbr_nullmodel_execution_authorization WHERE run_id = '{RUN_ID}';
    DELETE FROM {SCHEMA}.pbr_nullmodel_failure_modes WHERE run_id = '{RUN_ID}';
    DELETE FROM {SCHEMA}.pbr_nullmodel_diagnostics_required WHERE run_id = '{RUN_ID}';
    DELETE FROM {SCHEMA}.pbr_nullmodel_gate_decision WHERE run_id = '{RUN_ID}';
    DELETE FROM {SCHEMA}.pbr_nullmodel_input_artifact_requirements WHERE run_id = '{RUN_ID}';
    DELETE FROM {SCHEMA}.pbr_nullmodel_claim_boundaries WHERE run_id = '{RUN_ID}';
    DELETE FROM {SCHEMA}.pbr_nullmodel_family_spec WHERE run_id = '{RUN_ID}';
    DELETE FROM {SCHEMA}.pbr_nullmodel_design_summary WHERE run_id = '{RUN_ID}';

    \\copy {SCHEMA}.pbr_nullmodel_design_summary (run_id, previous_run_id, design_status, execution_status, claim_status, physical_claim_release, external_readiness, next_gate, schema_name, nullmodel_family_count, formal_reference_finding) FROM 'runs/{RUN_ID}/data/nullmodel_design_summary.csv' WITH (FORMAT csv, HEADER true)
    \\copy {SCHEMA}.pbr_nullmodel_family_spec (run_id, nullmodel_id, nullmodel_key, purpose, preserved_quantities, randomized_quantities, expected_diagnostic_outputs, admissibility_criteria, failure_modes, required_input_artifacts, execution_authorization_status, claim_boundary, next_gate_implication) FROM 'runs/{RUN_ID}/data/nullmodel_family_spec.csv' WITH (FORMAT csv, HEADER true)
    \\copy {SCHEMA}.pbr_nullmodel_claim_boundaries (run_id, boundary_id, claim_key, status, claim_boundary_text) FROM 'runs/{RUN_ID}/data/claim_boundaries.csv' WITH (FORMAT csv, HEADER true)
    \\copy {SCHEMA}.pbr_nullmodel_input_artifact_requirements (run_id, artifact_id, artifact_key, required_path, required_for, status) FROM 'runs/{RUN_ID}/data/input_artifact_requirements.csv' WITH (FORMAT csv, HEADER true)
    \\copy {SCHEMA}.pbr_nullmodel_gate_decision (run_id, gate_id, gate_name, gate_decision, execution_status, physical_claim_release, external_readiness, next_gate, revision_trigger) FROM 'runs/{RUN_ID}/data/gate_decision.csv' WITH (FORMAT csv, HEADER true)
    \\copy {SCHEMA}.pbr_nullmodel_diagnostics_required (run_id, nullmodel_key, diagnostic_key, required, execution_status, output_claim_status) FROM 'runs/{RUN_ID}/data/nullmodel_diagnostics_required.csv' WITH (FORMAT csv, HEADER true)
    \\copy {SCHEMA}.pbr_nullmodel_failure_modes (run_id, nullmodel_key, failure_mode_id, failure_mode, mitigation_status) FROM 'runs/{RUN_ID}/data/nullmodel_failure_modes.csv' WITH (FORMAT csv, HEADER true)
    \\copy {SCHEMA}.pbr_nullmodel_execution_authorization (run_id, nullmodel_key, execution_authorization_status, authorization_note, required_before_execution) FROM 'runs/{RUN_ID}/data/nullmodel_execution_authorization.csv' WITH (FORMAT csv, HEADER true)
    \\copy {SCHEMA}.pbr_nullmodel_validation_results (run_id, validation_id, check_name, status, severity, observed_value, expected_value, message, blocking) FROM 'runs/{RUN_ID}/validation/validation_results.csv' WITH (FORMAT csv, HEADER true)

    COMMIT;
    """
    write_text(sql_dir / "002_insert_qsb_pbr_nullmodel_design.sql", insert_sql)

    validation_sql = f"""
    -- Validation queries for {RUN_ID}.

    SELECT run_id, design_status, execution_status, physical_claim_release, external_readiness, next_gate
    FROM {SCHEMA}.pbr_nullmodel_design_summary
    WHERE run_id = '{RUN_ID}';

    SELECT nullmodel_key, count(*) AS rows
    FROM {SCHEMA}.pbr_nullmodel_family_spec
    WHERE run_id = '{RUN_ID}'
    GROUP BY nullmodel_key
    ORDER BY nullmodel_key;

    SELECT status, count(*) AS checks
    FROM {SCHEMA}.pbr_nullmodel_validation_results
    WHERE run_id = '{RUN_ID}'
    GROUP BY status
    ORDER BY status;

    SELECT physical_claim_release, next_gate
    FROM {SCHEMA}.pbr_nullmodel_gate_decision
    WHERE run_id = '{RUN_ID}';

    SELECT *
    FROM {SCHEMA}.pbr_nullmodel_claim_boundaries
    WHERE run_id = '{RUN_ID}'
    ORDER BY boundary_id;
    """
    write_text(sql_dir / "003_validation_queries.sql", validation_sql)

    print(f"run_id={RUN_ID}")
    print(f"design_status={DESIGN_STATUS}")
    print(f"execution_status={EXECUTION_STATUS}")
    print(f"claim_status={CLAIM_STATUS}")
    print(f"physical_claim_release={PHYSICAL_CLAIM_RELEASE}")
    print(f"external_readiness={EXTERNAL_READINESS}")
    print(f"next_gate={NEXT_GATE}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
