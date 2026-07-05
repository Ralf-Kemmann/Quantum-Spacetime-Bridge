-- QSB-DWH-PLANCK-BRIDGE-LIT-ADDENDUM-ASHREUROV-2014-01
-- Idempotent PostgreSQL import for Ashtekar/Reuter/Rovelli 2014 literature addendum.
-- Claim boundary: motivational overview only; no physics claims are released.

BEGIN;

CREATE SCHEMA IF NOT EXISTS qsb_literature;

CREATE TABLE IF NOT EXISTS qsb_literature.litnote_run (
    run_id TEXT PRIMARY KEY,
    work_package TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    artifact_kind TEXT NOT NULL,
    source_bib_file TEXT NOT NULL,
    source_sha256 TEXT NOT NULL,
    source_entry_count INTEGER NOT NULL,
    claim_map_count INTEGER NOT NULL,
    claim_boundary TEXT NOT NULL,
    physical_claim_status TEXT NOT NULL CHECK (physical_claim_status IN ('blocked_no_physics_claim','review_required','released')),
    lineage_note TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS qsb_literature.reference_source (
    bib_key TEXT PRIMARY KEY,
    run_id TEXT NOT NULL REFERENCES qsb_literature.litnote_run(run_id) ON UPDATE CASCADE,
    work_package TEXT NOT NULL,
    entry_type TEXT NOT NULL,
    title TEXT NOT NULL,
    authors TEXT,
    year INTEGER,
    journal TEXT,
    booktitle TEXT,
    publisher TEXT,
    series TEXT,
    volume TEXT,
    number TEXT,
    pages TEXT,
    doi TEXT,
    arxiv_id TEXT,
    archive_prefix TEXT,
    primary_class TEXT,
    url TEXT,
    isbn TEXT,
    note TEXT,
    keywords TEXT,
    pillar_id TEXT NOT NULL,
    pillar_label TEXT NOT NULL,
    source_file TEXT NOT NULL,
    source_sha256 TEXT NOT NULL,
    claim_status TEXT NOT NULL DEFAULT 'motivational_reference_only',
    physical_claim_release TEXT NOT NULL DEFAULT 'blocked_no_physics_claim',
    registered_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT qsb_reference_no_claim_release CHECK (physical_claim_release = 'blocked_no_physics_claim')
);

CREATE TABLE IF NOT EXISTS qsb_literature.reference_claim_map (
    claim_map_id TEXT PRIMARY KEY,
    run_id TEXT NOT NULL REFERENCES qsb_literature.litnote_run(run_id) ON UPDATE CASCADE,
    bib_key TEXT NOT NULL REFERENCES qsb_literature.reference_source(bib_key) ON UPDATE CASCADE,
    pillar_id TEXT NOT NULL,
    supports TEXT NOT NULL,
    does_not_support TEXT NOT NULL,
    qsb_connection TEXT NOT NULL,
    allowed_claim TEXT NOT NULL,
    forbidden_claim TEXT NOT NULL,
    review_status TEXT NOT NULL,
    registered_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE OR REPLACE VIEW qsb_literature.v_planck_bridge_lit_addendum_ashreurov_2014_claim_boundary AS
SELECT
    s.pillar_label,
    s.bib_key,
    s.title,
    s.authors,
    s.year,
    s.arxiv_id,
    c.supports,
    c.does_not_support,
    c.qsb_connection,
    c.allowed_claim,
    c.forbidden_claim,
    s.claim_status,
    s.physical_claim_release,
    c.review_status
FROM qsb_literature.reference_source s
JOIN qsb_literature.reference_claim_map c USING (bib_key)
WHERE s.run_id = 'QSB-DWH-PLANCK-BRIDGE-LIT-ADDENDUM-ASHREUROV-2014-01'
ORDER BY s.pillar_id, s.year NULLS LAST, s.bib_key;

INSERT INTO qsb_literature.litnote_run (run_id, work_package, created_at, artifact_kind, source_bib_file, source_sha256, source_entry_count, claim_map_count, claim_boundary, physical_claim_status, lineage_note) VALUES (
'QSB-DWH-PLANCK-BRIDGE-LIT-ADDENDUM-ASHREUROV-2014-01',
'QSB-PLANCK-BRIDGE-LITERATURE-ADDENDUM-ASHREUROV-2014-01',
'2026-07-05T00:00:00+02:00',
'literature_addendum_bibliography_claim_mapping_import',
'qsb_planck_bridge_lit_addendum_ashreurov_2014.bib',
'587b77f00067bedb34660bde76b284f316853a7efa13c9a1a876c6c9b00978b7',
1,
1,
'Ashtekar/Reuter/Rovelli 2014 motivates dynamic geometry, Planck-regime short-distance structure, and suitable-limit recovery of classical GR; it does not prove QSB or a Planck-Bridge-Resonator.',
'blocked_no_physics_claim',
'Derived from uploaded PDF From_general_relativity_to_quantum_gravi-1.pdf and qsb_planck_bridge_lit_addendum_ashreurov_2014.bib. Source PDF SHA256: 0a7fb2a4d3d23263a34507ef69506a349e3bbe7cfa70fd2657be63715274681a'
)
ON CONFLICT (run_id) DO UPDATE SET
    source_sha256 = EXCLUDED.source_sha256,
    source_entry_count = EXCLUDED.source_entry_count,
    claim_map_count = EXCLUDED.claim_map_count,
    claim_boundary = EXCLUDED.claim_boundary,
    physical_claim_status = EXCLUDED.physical_claim_status,
    lineage_note = EXCLUDED.lineage_note;

INSERT INTO qsb_literature.reference_source (run_id, work_package, bib_key, entry_type, title, authors, year, journal, booktitle, publisher, series, volume, number, pages, doi, arxiv_id, archive_prefix, primary_class, url, isbn, note, keywords, pillar_id, pillar_label, source_file, source_sha256, claim_status, physical_claim_release) VALUES ('QSB-DWH-PLANCK-BRIDGE-LIT-ADDENDUM-ASHREUROV-2014-01', 'QSB-PLANCK-BRIDGE-LITERATURE-ADDENDUM-ASHREUROV-2014-01', 'ashtekar_reuter_rovelli2014_from_gr_to_quantum_gravity', 'misc', 'From General Relativity to Quantum Gravity', 'Ashtekar, Abhay and Reuter, Martin and Rovelli, Carlo', 2014, NULL, 'General Relativity and Gravitation: A Centennial Survey', 'Cambridge University Press', NULL, NULL, NULL, NULL, NULL, '1408.4336', 'arXiv', 'gr-qc', 'https://arxiv.org/abs/1408.4336', NULL, 'arXiv:1408.4336v1 [gr-qc], 19 Aug 2014; chapter for General Relativity and Gravitation: A Centennial Survey.', 'qsb, planck-bridge, quantum-gravity-overview, dynamic-geometry, loop-quantum-gravity, asymptotic-safety, planck-regime, coarse-graining', 'dynamic_quantum_geometry_planck_regime', 'Quantum Gravity Overview / Dynamic Geometry / Planck-Regime', 'qsb_planck_bridge_lit_addendum_ashreurov_2014.bib', '587b77f00067bedb34660bde76b284f316853a7efa13c9a1a876c6c9b00978b7', 'motivational_reference_only', 'blocked_no_physics_claim')
ON CONFLICT (bib_key) DO UPDATE SET
    run_id = EXCLUDED.run_id,
    work_package = EXCLUDED.work_package,
    entry_type = EXCLUDED.entry_type,
    title = EXCLUDED.title,
    authors = EXCLUDED.authors,
    year = EXCLUDED.year,
    journal = EXCLUDED.journal,
    booktitle = EXCLUDED.booktitle,
    publisher = EXCLUDED.publisher,
    series = EXCLUDED.series,
    volume = EXCLUDED.volume,
    number = EXCLUDED.number,
    pages = EXCLUDED.pages,
    doi = EXCLUDED.doi,
    arxiv_id = EXCLUDED.arxiv_id,
    archive_prefix = EXCLUDED.archive_prefix,
    primary_class = EXCLUDED.primary_class,
    url = EXCLUDED.url,
    isbn = EXCLUDED.isbn,
    note = EXCLUDED.note,
    keywords = EXCLUDED.keywords,
    pillar_id = EXCLUDED.pillar_id,
    pillar_label = EXCLUDED.pillar_label,
    source_file = EXCLUDED.source_file,
    source_sha256 = EXCLUDED.source_sha256,
    claim_status = EXCLUDED.claim_status,
    physical_claim_release = EXCLUDED.physical_claim_release;

INSERT INTO qsb_literature.reference_claim_map (claim_map_id, run_id, bib_key, pillar_id, supports, does_not_support, qsb_connection, allowed_claim, forbidden_claim, review_status) VALUES ('CLAIM-ASHREUROV-2014-01', 'QSB-DWH-PLANCK-BRIDGE-LIT-ADDENDUM-ASHREUROV-2014-01', 'ashtekar_reuter_rovelli2014_from_gr_to_quantum_gravity', 'dynamic_quantum_geometry_planck_regime', 'Motiviert dynamische Raumzeitgeometrie, qualitativ anderes Kurzdistanzverhalten im Quantengravitationsbereich, nicht-perturbative Planck-Regime-Strategien und Rückgewinnung klassischer Raumzeit nur in geeignetem Grenz- beziehungsweise Coarse-Graining-Limit.', 'Beweist weder QSB noch Planck-Bridge-Resonatoren; bestätigt weder beta_B noch Xi_CS als physikalische Observablen; identifiziert keine Raumzeit-aus-Resonatoren-Struktur.', 'Stützt den Suchraum und die methodische Vorsicht für Planck-Bridge-Resonator-State-Spec: Skala, Kurzdistanzstruktur, dynamische Geometrie und geeignete Grenzfälle zuerst prüfen.', 'The source can be cited as a motivational overview reference for dynamic quantum geometry, Planck-regime short-distance structure, and suitable-limit recovery of classical GR.', 'The source must not be used as evidence for the existence of Planck-Bridge-Resonators, for QSB as a confirmed theory, or for beta_B/Xi_CS as physical observables.', 'registered_requires_human_literature_review')
ON CONFLICT (claim_map_id) DO UPDATE SET
    run_id = EXCLUDED.run_id,
    bib_key = EXCLUDED.bib_key,
    pillar_id = EXCLUDED.pillar_id,
    supports = EXCLUDED.supports,
    does_not_support = EXCLUDED.does_not_support,
    qsb_connection = EXCLUDED.qsb_connection,
    allowed_claim = EXCLUDED.allowed_claim,
    forbidden_claim = EXCLUDED.forbidden_claim,
    review_status = EXCLUDED.review_status;

COMMIT;
