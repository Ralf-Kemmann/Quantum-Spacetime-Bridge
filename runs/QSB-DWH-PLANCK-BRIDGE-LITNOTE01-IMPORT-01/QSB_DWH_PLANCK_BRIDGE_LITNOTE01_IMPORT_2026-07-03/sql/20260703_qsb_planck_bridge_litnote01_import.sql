-- QSB-DWH-PLANCK-BRIDGE-LITNOTE01-IMPORT-01
-- Idempotent PostgreSQL import for Literature Note 01 bibliography + claim mapping.
-- Claim boundary: literature motivates the interface question; no physics claims are released.

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


CREATE OR REPLACE VIEW qsb_literature.v_planck_bridge_litnote01_claim_boundary AS
SELECT
    s.pillar_label,
    s.bib_key,
    s.title,
    s.authors,
    s.year,
    c.supports,
    c.does_not_support,
    c.qsb_connection,
    s.claim_status,
    s.physical_claim_release,
    c.review_status
FROM qsb_literature.reference_source s
JOIN qsb_literature.reference_claim_map c USING (bib_key)
WHERE s.run_id = 'QSB-DWH-PLANCK-BRIDGE-LITNOTE01-IMPORT-01'
ORDER BY s.pillar_id, s.year NULLS LAST, s.bib_key;


INSERT INTO qsb_literature.litnote_run (run_id, work_package, created_at, artifact_kind, source_bib_file, source_sha256, source_entry_count, claim_map_count, claim_boundary, physical_claim_status, lineage_note) VALUES (
'QSB-DWH-PLANCK-BRIDGE-LITNOTE01-IMPORT-01',
'QSB-PLANCK-BRIDGE-RESONATOR-LITERATURE-NOTE-01',
'2026-07-03T00:00:00+02:00',
'literature_bibliography_claim_mapping_import',
'qsb_planck_bridge_resonator_litnote01.bib',
'78b2233167efe0f4830b918eb0231ec5ec748ed77e789b988cd3705e82b9fb27',
14,
14,
'References motivate the interface question; they do not prove the existence of a Planck-Bridge-Resonator.',
'blocked_no_physics_claim',
'Derived from QSB-PLANCK-BRIDGE-RESONATOR-LITERATURE-NOTE-01 bibliography v0.1.'
)
ON CONFLICT (run_id) DO UPDATE SET
    source_sha256 = EXCLUDED.source_sha256,
    source_entry_count = EXCLUDED.source_entry_count,
    claim_map_count = EXCLUDED.claim_map_count,
    claim_boundary = EXCLUDED.claim_boundary,
    physical_claim_status = EXCLUDED.physical_claim_status,
    lineage_note = EXCLUDED.lineage_note;

INSERT INTO qsb_literature.reference_source (run_id, work_package, bib_key, entry_type, title, authors, year, journal, booktitle, publisher, series, volume, number, pages, doi, arxiv_id, archive_prefix, primary_class, url, isbn, note, keywords, pillar_id, pillar_label, source_file, source_sha256, claim_status, physical_claim_release) VALUES ('QSB-DWH-PLANCK-BRIDGE-LITNOTE01-IMPORT-01', 'QSB-PLANCK-BRIDGE-RESONATOR-LITERATURE-NOTE-01', 'mead1964_fundamental_length', 'article', 'Possible Connection Between Gravitation and Fundamental Length', 'Mead, C. A.', 1964, 'Physical Review', NULL, NULL, NULL, '135', '3B', 'B849--B862', '10.1103/PhysRev.135.B849', NULL, NULL, NULL, 'https://doi.org/10.1103/PhysRev.135.B849', NULL, NULL, 'qsb, planck-boundary, minimal-length, localization-limit', 'planck_boundary_minimal_length', 'Planck-Grenze / Minimal-Länge / Lokalisierungsgrenze', 'qsb_planck_bridge_resonator_litnote01.bib', '78b2233167efe0f4830b918eb0231ec5ec748ed77e789b988cd3705e82b9fb27', 'motivational_reference_only', 'blocked_no_physics_claim')
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

INSERT INTO qsb_literature.reference_source (run_id, work_package, bib_key, entry_type, title, authors, year, journal, booktitle, publisher, series, volume, number, pages, doi, arxiv_id, archive_prefix, primary_class, url, isbn, note, keywords, pillar_id, pillar_label, source_file, source_sha256, claim_status, physical_claim_release) VALUES ('QSB-DWH-PLANCK-BRIDGE-LITNOTE01-IMPORT-01', 'QSB-PLANCK-BRIDGE-RESONATOR-LITERATURE-NOTE-01', 'garay1995_quantum_gravity_minimum_length', 'article', 'Quantum Gravity and Minimum Length', 'Garay, Luis J.', 1995, 'International Journal of Modern Physics A', NULL, NULL, NULL, '10', NULL, '145--166', '10.1142/S0217751X95000085', 'gr-qc/9403008', 'arXiv', 'gr-qc', 'https://arxiv.org/abs/gr-qc/9403008', NULL, NULL, 'qsb, planck-boundary, minimal-length, quantum-gravity', 'planck_boundary_minimal_length', 'Planck-Grenze / Minimal-Länge / Lokalisierungsgrenze', 'qsb_planck_bridge_resonator_litnote01.bib', '78b2233167efe0f4830b918eb0231ec5ec748ed77e789b988cd3705e82b9fb27', 'motivational_reference_only', 'blocked_no_physics_claim')
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

INSERT INTO qsb_literature.reference_source (run_id, work_package, bib_key, entry_type, title, authors, year, journal, booktitle, publisher, series, volume, number, pages, doi, arxiv_id, archive_prefix, primary_class, url, isbn, note, keywords, pillar_id, pillar_label, source_file, source_sha256, claim_status, physical_claim_release) VALUES ('QSB-DWH-PLANCK-BRIDGE-LITNOTE01-IMPORT-01', 'QSB-PLANCK-BRIDGE-RESONATOR-LITERATURE-NOTE-01', 'hossenfelder2013_minimal_length_scenarios', 'article', 'Minimal Length Scale Scenarios for Quantum Gravity', 'Hossenfelder, Sabine', 2013, 'Living Reviews in Relativity', NULL, NULL, NULL, '16', '2', NULL, '10.12942/lrr-2013-2', '1203.6191', 'arXiv', 'gr-qc', 'https://arxiv.org/abs/1203.6191', NULL, NULL, 'qsb, planck-boundary, minimal-length, finite-resolution', 'planck_boundary_minimal_length', 'Planck-Grenze / Minimal-Länge / Lokalisierungsgrenze', 'qsb_planck_bridge_resonator_litnote01.bib', '78b2233167efe0f4830b918eb0231ec5ec748ed77e789b988cd3705e82b9fb27', 'motivational_reference_only', 'blocked_no_physics_claim')
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

INSERT INTO qsb_literature.reference_source (run_id, work_package, bib_key, entry_type, title, authors, year, journal, booktitle, publisher, series, volume, number, pages, doi, arxiv_id, archive_prefix, primary_class, url, isbn, note, keywords, pillar_id, pillar_label, source_file, source_sha256, claim_status, physical_claim_release) VALUES ('QSB-DWH-PLANCK-BRIDGE-LITNOTE01-IMPORT-01', 'QSB-PLANCK-BRIDGE-RESONATOR-LITERATURE-NOTE-01', 'devega_sanchez1987_string_quantization_curved', 'article', 'A New Approach to String Quantization in Curved Spacetimes', 'de Vega, H. J. and S{\''a}nchez, N.', 1987, 'Physics Letters B', NULL, NULL, NULL, '197', '3', '320--326', '10.1016/0370-2693(87)90392-3', NULL, NULL, NULL, 'https://doi.org/10.1016/0370-2693(87)90392-3', NULL, NULL, 'qsb, sanchez-line, strings, curved-spacetime, modes, geometry-coupling', 'sanchez_devega_strings_curved_spacetime', 'Sanchez / de Vega / Sanchez: Strings in gekrümmter Raumzeit', 'qsb_planck_bridge_resonator_litnote01.bib', '78b2233167efe0f4830b918eb0231ec5ec748ed77e789b988cd3705e82b9fb27', 'motivational_reference_only', 'blocked_no_physics_claim')
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

INSERT INTO qsb_literature.reference_source (run_id, work_package, bib_key, entry_type, title, authors, year, journal, booktitle, publisher, series, volume, number, pages, doi, arxiv_id, archive_prefix, primary_class, url, isbn, note, keywords, pillar_id, pillar_label, source_file, source_sha256, claim_status, physical_claim_release) VALUES ('QSB-DWH-PLANCK-BRIDGE-LITNOTE01-IMPORT-01', 'QSB-PLANCK-BRIDGE-RESONATOR-LITERATURE-NOTE-01', 'devega1993_strings_curved_spacetimes', 'misc', 'Strings in Curved Spacetimes', 'de Vega, H. J.', 1993, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, 'hep-th/9302052', 'arXiv', 'hep-th', 'https://arxiv.org/abs/hep-th/9302052', NULL, 'Lectures delivered at the Erice School ``String Quantum Gravity and Physics at the Planck Energy Scale'''', 21--28 June 1992; proceedings edited by N. S{\''a}nchez, World Scientific.', 'qsb, sanchez-line, strings, curved-spacetime, particle-transmutation, internal-modes', 'sanchez_devega_strings_curved_spacetime', 'Sanchez / de Vega / Sanchez: Strings in gekrümmter Raumzeit', 'qsb_planck_bridge_resonator_litnote01.bib', '78b2233167efe0f4830b918eb0231ec5ec748ed77e789b988cd3705e82b9fb27', 'motivational_reference_only', 'blocked_no_physics_claim')
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

INSERT INTO qsb_literature.reference_source (run_id, work_package, bib_key, entry_type, title, authors, year, journal, booktitle, publisher, series, volume, number, pages, doi, arxiv_id, archive_prefix, primary_class, url, isbn, note, keywords, pillar_id, pillar_label, source_file, source_sha256, claim_status, physical_claim_release) VALUES ('QSB-DWH-PLANCK-BRIDGE-LITNOTE01-IMPORT-01', 'QSB-PLANCK-BRIDGE-RESONATOR-LITERATURE-NOTE-01', 'devega_sanchez1995_lectures_string_curved_spacetimes', 'misc', 'Lectures on String Theory in Curved Spacetimes', 'de Vega, H. J. and S{\''a}nchez, N.', 1995, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, 'hep-th/9512074', 'arXiv', 'hep-th', 'https://arxiv.org/abs/hep-th/9512074', NULL, 'Lectures/review on string dynamics in cosmological and black-hole spacetimes.', 'qsb, sanchez-line, strings, curved-spacetime, stable-unstable-classes, multistring-solutions', 'sanchez_devega_strings_curved_spacetime', 'Sanchez / de Vega / Sanchez: Strings in gekrümmter Raumzeit', 'qsb_planck_bridge_resonator_litnote01.bib', '78b2233167efe0f4830b918eb0231ec5ec748ed77e789b988cd3705e82b9fb27', 'motivational_reference_only', 'blocked_no_physics_claim')
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

INSERT INTO qsb_literature.reference_source (run_id, work_package, bib_key, entry_type, title, authors, year, journal, booktitle, publisher, series, volume, number, pages, doi, arxiv_id, archive_prefix, primary_class, url, isbn, note, keywords, pillar_id, pillar_label, source_file, source_sha256, claim_status, physical_claim_release) VALUES ('QSB-DWH-PLANCK-BRIDGE-LITNOTE01-IMPORT-01', 'QSB-PLANCK-BRIDGE-RESONATOR-LITERATURE-NOTE-01', 'birrell_davies1982_quantum_fields_curved_space', 'book', 'Quantum Fields in Curved Space', 'Birrell, N. D. and Davies, P. C. W.', 1982, NULL, NULL, 'Cambridge University Press', 'Cambridge Monographs on Mathematical Physics', NULL, NULL, NULL, '10.1017/CBO9780511622632', NULL, NULL, NULL, 'https://doi.org/10.1017/CBO9780511622632', '9780521278584', NULL, 'qsb, qft-curved-spacetime, modes, vacuum, hawking-radiation', 'qft_curved_spacetime', 'QFT in gekrümmter Raumzeit', 'qsb_planck_bridge_resonator_litnote01.bib', '78b2233167efe0f4830b918eb0231ec5ec748ed77e789b988cd3705e82b9fb27', 'motivational_reference_only', 'blocked_no_physics_claim')
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

INSERT INTO qsb_literature.reference_source (run_id, work_package, bib_key, entry_type, title, authors, year, journal, booktitle, publisher, series, volume, number, pages, doi, arxiv_id, archive_prefix, primary_class, url, isbn, note, keywords, pillar_id, pillar_label, source_file, source_sha256, claim_status, physical_claim_release) VALUES ('QSB-DWH-PLANCK-BRIDGE-LITNOTE01-IMPORT-01', 'QSB-PLANCK-BRIDGE-RESONATOR-LITERATURE-NOTE-01', 'hollands_wald2015_qft_curved_spacetime', 'article', 'Quantum Fields in Curved Spacetime', 'Hollands, Stefan and Wald, Robert M.', 2015, 'Physics Reports', NULL, NULL, NULL, '574', NULL, '1--35', '10.1016/j.physrep.2015.02.001', '1401.2026', 'arXiv', 'gr-qc', 'https://arxiv.org/abs/1401.2026', NULL, NULL, 'qsb, qft-curved-spacetime, local-covariance, hadamard-states, unruh-effect, hawking-effect', 'qft_curved_spacetime', 'QFT in gekrümmter Raumzeit', 'qsb_planck_bridge_resonator_litnote01.bib', '78b2233167efe0f4830b918eb0231ec5ec748ed77e789b988cd3705e82b9fb27', 'motivational_reference_only', 'blocked_no_physics_claim')
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

INSERT INTO qsb_literature.reference_source (run_id, work_package, bib_key, entry_type, title, authors, year, journal, booktitle, publisher, series, volume, number, pages, doi, arxiv_id, archive_prefix, primary_class, url, isbn, note, keywords, pillar_id, pillar_label, source_file, source_sha256, claim_status, physical_claim_release) VALUES ('QSB-DWH-PLANCK-BRIDGE-LITNOTE01-IMPORT-01', 'QSB-PLANCK-BRIDGE-RESONATOR-LITERATURE-NOTE-01', 'jacobson1995_thermodynamics_spacetime', 'article', 'Thermodynamics of Spacetime: The Einstein Equation of State', 'Jacobson, Ted', 1995, 'Physical Review Letters', NULL, NULL, NULL, '75', '7', '1260--1263', '10.1103/PhysRevLett.75.1260', 'gr-qc/9504004', 'arXiv', 'gr-qc', 'https://arxiv.org/abs/gr-qc/9504004', NULL, NULL, 'qsb, emergent-spacetime, thermodynamics, horizon-entropy, einstein-equation', 'emergent_relational_spacetime', 'Emergente / relationale Raumzeit', 'qsb_planck_bridge_resonator_litnote01.bib', '78b2233167efe0f4830b918eb0231ec5ec748ed77e789b988cd3705e82b9fb27', 'motivational_reference_only', 'blocked_no_physics_claim')
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

INSERT INTO qsb_literature.reference_source (run_id, work_package, bib_key, entry_type, title, authors, year, journal, booktitle, publisher, series, volume, number, pages, doi, arxiv_id, archive_prefix, primary_class, url, isbn, note, keywords, pillar_id, pillar_label, source_file, source_sha256, claim_status, physical_claim_release) VALUES ('QSB-DWH-PLANCK-BRIDGE-LITNOTE01-IMPORT-01', 'QSB-PLANCK-BRIDGE-RESONATOR-LITERATURE-NOTE-01', 'ryu_takayanagi2006_holographic_entanglement_entropy', 'article', 'Holographic Derivation of Entanglement Entropy from {AdS/CFT}', 'Ryu, Shinsei and Takayanagi, Tadashi', 2006, 'Physical Review Letters', NULL, NULL, NULL, '96', '18', '181602', '10.1103/PhysRevLett.96.181602', 'hep-th/0603001', 'arXiv', 'hep-th', 'https://arxiv.org/abs/hep-th/0603001', NULL, NULL, 'qsb, emergent-spacetime, holography, entanglement-entropy, geometry', 'emergent_relational_spacetime', 'Emergente / relationale Raumzeit', 'qsb_planck_bridge_resonator_litnote01.bib', '78b2233167efe0f4830b918eb0231ec5ec748ed77e789b988cd3705e82b9fb27', 'motivational_reference_only', 'blocked_no_physics_claim')
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

INSERT INTO qsb_literature.reference_source (run_id, work_package, bib_key, entry_type, title, authors, year, journal, booktitle, publisher, series, volume, number, pages, doi, arxiv_id, archive_prefix, primary_class, url, isbn, note, keywords, pillar_id, pillar_label, source_file, source_sha256, claim_status, physical_claim_release) VALUES ('QSB-DWH-PLANCK-BRIDGE-LITNOTE01-IMPORT-01', 'QSB-PLANCK-BRIDGE-RESONATOR-LITERATURE-NOTE-01', 'vanraamsdonk2010_spacetime_entanglement', 'article', 'Building Up Spacetime with Quantum Entanglement', 'Van Raamsdonk, Mark', 2010, 'General Relativity and Gravitation', NULL, NULL, NULL, '42', NULL, '2323--2329', '10.1007/s10714-010-1034-0', '1005.3035', 'arXiv', 'hep-th', 'https://arxiv.org/abs/1005.3035', NULL, 'Also published in International Journal of Modern Physics D 19, 2429--2435 (2010), doi:10.1142/S0218271810018529.', 'qsb, emergent-spacetime, quantum-entanglement, holography, connectivity', 'emergent_relational_spacetime', 'Emergente / relationale Raumzeit', 'qsb_planck_bridge_resonator_litnote01.bib', '78b2233167efe0f4830b918eb0231ec5ec748ed77e789b988cd3705e82b9fb27', 'motivational_reference_only', 'blocked_no_physics_claim')
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

INSERT INTO qsb_literature.reference_source (run_id, work_package, bib_key, entry_type, title, authors, year, journal, booktitle, publisher, series, volume, number, pages, doi, arxiv_id, archive_prefix, primary_class, url, isbn, note, keywords, pillar_id, pillar_label, source_file, source_sha256, claim_status, physical_claim_release) VALUES ('QSB-DWH-PLANCK-BRIDGE-LITNOTE01-IMPORT-01', 'QSB-PLANCK-BRIDGE-RESONATOR-LITERATURE-NOTE-01', 'rovelli_smolin1995_spin_networks_quantum_gravity', 'article', 'Spin Networks and Quantum Gravity', 'Rovelli, Carlo and Smolin, Lee', 1995, 'Physical Review D', NULL, NULL, NULL, '52', NULL, '5743--5759', '10.1103/PhysRevD.52.5743', 'gr-qc/9505006', 'arXiv', 'gr-qc', 'https://arxiv.org/abs/gr-qc/9505006', NULL, NULL, 'qsb, emergent-spacetime, quantum-geometry, spin-networks, loop-quantum-gravity', 'emergent_relational_spacetime', 'Emergente / relationale Raumzeit', 'qsb_planck_bridge_resonator_litnote01.bib', '78b2233167efe0f4830b918eb0231ec5ec748ed77e789b988cd3705e82b9fb27', 'motivational_reference_only', 'blocked_no_physics_claim')
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

INSERT INTO qsb_literature.reference_source (run_id, work_package, bib_key, entry_type, title, authors, year, journal, booktitle, publisher, series, volume, number, pages, doi, arxiv_id, archive_prefix, primary_class, url, isbn, note, keywords, pillar_id, pillar_label, source_file, source_sha256, claim_status, physical_claim_release) VALUES ('QSB-DWH-PLANCK-BRIDGE-LITNOTE01-IMPORT-01', 'QSB-PLANCK-BRIDGE-RESONATOR-LITERATURE-NOTE-01', 'bombelli_lee_meyer_sorkin1987_causal_set', 'article', 'Space-Time as a Causal Set', 'Bombelli, Luca and Lee, Joohan and Meyer, David and Sorkin, Rafael D.', 1987, 'Physical Review Letters', NULL, NULL, NULL, '59', '5', '521--524', '10.1103/PhysRevLett.59.521', NULL, NULL, NULL, 'https://doi.org/10.1103/PhysRevLett.59.521', NULL, NULL, 'qsb, emergent-spacetime, causal-set, partial-order, discreteness', 'emergent_relational_spacetime', 'Emergente / relationale Raumzeit', 'qsb_planck_bridge_resonator_litnote01.bib', '78b2233167efe0f4830b918eb0231ec5ec748ed77e789b988cd3705e82b9fb27', 'motivational_reference_only', 'blocked_no_physics_claim')
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

INSERT INTO qsb_literature.reference_source (run_id, work_package, bib_key, entry_type, title, authors, year, journal, booktitle, publisher, series, volume, number, pages, doi, arxiv_id, archive_prefix, primary_class, url, isbn, note, keywords, pillar_id, pillar_label, source_file, source_sha256, claim_status, physical_claim_release) VALUES ('QSB-DWH-PLANCK-BRIDGE-LITNOTE01-IMPORT-01', 'QSB-PLANCK-BRIDGE-RESONATOR-LITERATURE-NOTE-01', 'swingle2012_holographic_spacetimes_entanglement_renormalization', 'misc', 'Constructing Holographic Spacetimes Using Entanglement Renormalization', 'Swingle, Brian', 2012, NULL, NULL, NULL, NULL, NULL, NULL, NULL, '10.48550/arXiv.1209.3304', '1209.3304', 'arXiv', 'hep-th', 'https://arxiv.org/abs/1209.3304', NULL, NULL, 'qsb, emergent-spacetime, tensor-networks, entanglement-renormalization, holography', 'emergent_relational_spacetime', 'Emergente / relationale Raumzeit', 'qsb_planck_bridge_resonator_litnote01.bib', '78b2233167efe0f4830b918eb0231ec5ec748ed77e789b988cd3705e82b9fb27', 'motivational_reference_only', 'blocked_no_physics_claim')
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

INSERT INTO qsb_literature.reference_claim_map (run_id, claim_map_id, bib_key, pillar_id, supports, does_not_support, qsb_connection, allowed_claim, forbidden_claim, review_status) VALUES ('QSB-DWH-PLANCK-BRIDGE-LITNOTE01-IMPORT-01', 'QSB-DWH-PLANCK-BRIDGE-LITNOTE01-IMPORT-01-CM-001', 'mead1964_fundamental_length', 'planck_boundary_minimal_length', 'Motiviert eine Interface-Frage an der Grenze von Lokalisierung, Energie, Quantenzustand und gravitativer Rückwirkung.', 'Beweist keine Planck-Bridge-Resonatoren und keine Planck-Länge als Raum-Pixel.', 'Planck-Grenze wird als Suchraum für einen formal prüfbaren Interface-Kandidaten registriert.', 'Die Quelle motiviert die Interface-Frage und wird als Literaturanker registriert.', 'Die Quelle beweist nicht die Existenz des Planck-Bridge-Resonators und schaltet keine physikalischen QSB-Claims frei.', 'registered_requires_human_literature_review')
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

INSERT INTO qsb_literature.reference_claim_map (run_id, claim_map_id, bib_key, pillar_id, supports, does_not_support, qsb_connection, allowed_claim, forbidden_claim, review_status) VALUES ('QSB-DWH-PLANCK-BRIDGE-LITNOTE01-IMPORT-01', 'QSB-DWH-PLANCK-BRIDGE-LITNOTE01-IMPORT-01-CM-002', 'garay1995_quantum_gravity_minimum_length', 'planck_boundary_minimal_length', 'Motiviert eine Interface-Frage an der Grenze von Lokalisierung, Energie, Quantenzustand und gravitativer Rückwirkung.', 'Beweist keine Planck-Bridge-Resonatoren und keine Planck-Länge als Raum-Pixel.', 'Planck-Grenze wird als Suchraum für einen formal prüfbaren Interface-Kandidaten registriert.', 'Die Quelle motiviert die Interface-Frage und wird als Literaturanker registriert.', 'Die Quelle beweist nicht die Existenz des Planck-Bridge-Resonators und schaltet keine physikalischen QSB-Claims frei.', 'registered_requires_human_literature_review')
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

INSERT INTO qsb_literature.reference_claim_map (run_id, claim_map_id, bib_key, pillar_id, supports, does_not_support, qsb_connection, allowed_claim, forbidden_claim, review_status) VALUES ('QSB-DWH-PLANCK-BRIDGE-LITNOTE01-IMPORT-01', 'QSB-DWH-PLANCK-BRIDGE-LITNOTE01-IMPORT-01-CM-003', 'hossenfelder2013_minimal_length_scenarios', 'planck_boundary_minimal_length', 'Motiviert eine Interface-Frage an der Grenze von Lokalisierung, Energie, Quantenzustand und gravitativer Rückwirkung.', 'Beweist keine Planck-Bridge-Resonatoren und keine Planck-Länge als Raum-Pixel.', 'Planck-Grenze wird als Suchraum für einen formal prüfbaren Interface-Kandidaten registriert.', 'Die Quelle motiviert die Interface-Frage und wird als Literaturanker registriert.', 'Die Quelle beweist nicht die Existenz des Planck-Bridge-Resonators und schaltet keine physikalischen QSB-Claims frei.', 'registered_requires_human_literature_review')
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

INSERT INTO qsb_literature.reference_claim_map (run_id, claim_map_id, bib_key, pillar_id, supports, does_not_support, qsb_connection, allowed_claim, forbidden_claim, review_status) VALUES ('QSB-DWH-PLANCK-BRIDGE-LITNOTE01-IMPORT-01', 'QSB-DWH-PLANCK-BRIDGE-LITNOTE01-IMPORT-01-CM-004', 'devega_sanchez1987_string_quantization_curved', 'sanchez_devega_strings_curved_spacetime', 'Stützt das Strukturmotiv modentragender, ausgedehnter Quantensysteme in gekrümmter Raumzeit und geometrisch beeinflusster Dynamik.', 'Beweist weder QSB noch einen spezifischen Resonator-Baustein; Stringtheorie wird nicht als Beweisanker verwendet.', 'Motiviert den Übergang a -> a'' als Strukturmotiv geometrisch vermittelter Zustandsänderung.', 'Die Quelle motiviert die Interface-Frage und wird als Literaturanker registriert.', 'Die Quelle beweist nicht die Existenz des Planck-Bridge-Resonators und schaltet keine physikalischen QSB-Claims frei.', 'registered_requires_human_literature_review')
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

INSERT INTO qsb_literature.reference_claim_map (run_id, claim_map_id, bib_key, pillar_id, supports, does_not_support, qsb_connection, allowed_claim, forbidden_claim, review_status) VALUES ('QSB-DWH-PLANCK-BRIDGE-LITNOTE01-IMPORT-01', 'QSB-DWH-PLANCK-BRIDGE-LITNOTE01-IMPORT-01-CM-005', 'devega1993_strings_curved_spacetimes', 'sanchez_devega_strings_curved_spacetime', 'Stützt das Strukturmotiv modentragender, ausgedehnter Quantensysteme in gekrümmter Raumzeit und geometrisch beeinflusster Dynamik.', 'Beweist weder QSB noch einen spezifischen Resonator-Baustein; Stringtheorie wird nicht als Beweisanker verwendet.', 'Motiviert den Übergang a -> a'' als Strukturmotiv geometrisch vermittelter Zustandsänderung.', 'Die Quelle motiviert die Interface-Frage und wird als Literaturanker registriert.', 'Die Quelle beweist nicht die Existenz des Planck-Bridge-Resonators und schaltet keine physikalischen QSB-Claims frei.', 'registered_requires_human_literature_review')
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

INSERT INTO qsb_literature.reference_claim_map (run_id, claim_map_id, bib_key, pillar_id, supports, does_not_support, qsb_connection, allowed_claim, forbidden_claim, review_status) VALUES ('QSB-DWH-PLANCK-BRIDGE-LITNOTE01-IMPORT-01', 'QSB-DWH-PLANCK-BRIDGE-LITNOTE01-IMPORT-01-CM-006', 'devega_sanchez1995_lectures_string_curved_spacetimes', 'sanchez_devega_strings_curved_spacetime', 'Stützt das Strukturmotiv modentragender, ausgedehnter Quantensysteme in gekrümmter Raumzeit und geometrisch beeinflusster Dynamik.', 'Beweist weder QSB noch einen spezifischen Resonator-Baustein; Stringtheorie wird nicht als Beweisanker verwendet.', 'Motiviert den Übergang a -> a'' als Strukturmotiv geometrisch vermittelter Zustandsänderung.', 'Die Quelle motiviert die Interface-Frage und wird als Literaturanker registriert.', 'Die Quelle beweist nicht die Existenz des Planck-Bridge-Resonators und schaltet keine physikalischen QSB-Claims frei.', 'registered_requires_human_literature_review')
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

INSERT INTO qsb_literature.reference_claim_map (run_id, claim_map_id, bib_key, pillar_id, supports, does_not_support, qsb_connection, allowed_claim, forbidden_claim, review_status) VALUES ('QSB-DWH-PLANCK-BRIDGE-LITNOTE01-IMPORT-01', 'QSB-DWH-PLANCK-BRIDGE-LITNOTE01-IMPORT-01-CM-007', 'birrell_davies1982_quantum_fields_curved_space', 'qft_curved_spacetime', 'Motiviert, dass Geometrie Vakuumbegriff, Modenzerlegung, Teilchenbegriff und beobachtbare Feldgrößen beeinflussen kann.', 'Liefert keine mikroskopische Theorie der Raumzeit und keine Resonator-Entität.', 'Stützt die Interface-Frage zwischen Zustand, Moden, Phase und geometrischer Bedingung.', 'Die Quelle motiviert die Interface-Frage und wird als Literaturanker registriert.', 'Die Quelle beweist nicht die Existenz des Planck-Bridge-Resonators und schaltet keine physikalischen QSB-Claims frei.', 'registered_requires_human_literature_review')
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

INSERT INTO qsb_literature.reference_claim_map (run_id, claim_map_id, bib_key, pillar_id, supports, does_not_support, qsb_connection, allowed_claim, forbidden_claim, review_status) VALUES ('QSB-DWH-PLANCK-BRIDGE-LITNOTE01-IMPORT-01', 'QSB-DWH-PLANCK-BRIDGE-LITNOTE01-IMPORT-01-CM-008', 'hollands_wald2015_qft_curved_spacetime', 'qft_curved_spacetime', 'Motiviert, dass Geometrie Vakuumbegriff, Modenzerlegung, Teilchenbegriff und beobachtbare Feldgrößen beeinflussen kann.', 'Liefert keine mikroskopische Theorie der Raumzeit und keine Resonator-Entität.', 'Stützt die Interface-Frage zwischen Zustand, Moden, Phase und geometrischer Bedingung.', 'Die Quelle motiviert die Interface-Frage und wird als Literaturanker registriert.', 'Die Quelle beweist nicht die Existenz des Planck-Bridge-Resonators und schaltet keine physikalischen QSB-Claims frei.', 'registered_requires_human_literature_review')
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

INSERT INTO qsb_literature.reference_claim_map (run_id, claim_map_id, bib_key, pillar_id, supports, does_not_support, qsb_connection, allowed_claim, forbidden_claim, review_status) VALUES ('QSB-DWH-PLANCK-BRIDGE-LITNOTE01-IMPORT-01', 'QSB-DWH-PLANCK-BRIDGE-LITNOTE01-IMPORT-01-CM-009', 'jacobson1995_thermodynamics_spacetime', 'emergent_relational_spacetime', 'Zeigt, dass emergente, relationale, informationelle, kausale oder netzwerkartige Geometrie eine seriöse Forschungsfrage ist.', 'Bestätigt QSB nicht automatisch und macht relationale Netzwerke nicht automatisch zu physikalischer Raumzeit.', 'Erlaubt, ein Resonator-Netz als operationalisierbaren Emergenzkandidaten zu prüfen.', 'Die Quelle motiviert die Interface-Frage und wird als Literaturanker registriert.', 'Die Quelle beweist nicht die Existenz des Planck-Bridge-Resonators und schaltet keine physikalischen QSB-Claims frei.', 'registered_requires_human_literature_review')
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

INSERT INTO qsb_literature.reference_claim_map (run_id, claim_map_id, bib_key, pillar_id, supports, does_not_support, qsb_connection, allowed_claim, forbidden_claim, review_status) VALUES ('QSB-DWH-PLANCK-BRIDGE-LITNOTE01-IMPORT-01', 'QSB-DWH-PLANCK-BRIDGE-LITNOTE01-IMPORT-01-CM-010', 'ryu_takayanagi2006_holographic_entanglement_entropy', 'emergent_relational_spacetime', 'Zeigt, dass emergente, relationale, informationelle, kausale oder netzwerkartige Geometrie eine seriöse Forschungsfrage ist.', 'Bestätigt QSB nicht automatisch und macht relationale Netzwerke nicht automatisch zu physikalischer Raumzeit.', 'Erlaubt, ein Resonator-Netz als operationalisierbaren Emergenzkandidaten zu prüfen.', 'Die Quelle motiviert die Interface-Frage und wird als Literaturanker registriert.', 'Die Quelle beweist nicht die Existenz des Planck-Bridge-Resonators und schaltet keine physikalischen QSB-Claims frei.', 'registered_requires_human_literature_review')
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

INSERT INTO qsb_literature.reference_claim_map (run_id, claim_map_id, bib_key, pillar_id, supports, does_not_support, qsb_connection, allowed_claim, forbidden_claim, review_status) VALUES ('QSB-DWH-PLANCK-BRIDGE-LITNOTE01-IMPORT-01', 'QSB-DWH-PLANCK-BRIDGE-LITNOTE01-IMPORT-01-CM-011', 'vanraamsdonk2010_spacetime_entanglement', 'emergent_relational_spacetime', 'Zeigt, dass emergente, relationale, informationelle, kausale oder netzwerkartige Geometrie eine seriöse Forschungsfrage ist.', 'Bestätigt QSB nicht automatisch und macht relationale Netzwerke nicht automatisch zu physikalischer Raumzeit.', 'Erlaubt, ein Resonator-Netz als operationalisierbaren Emergenzkandidaten zu prüfen.', 'Die Quelle motiviert die Interface-Frage und wird als Literaturanker registriert.', 'Die Quelle beweist nicht die Existenz des Planck-Bridge-Resonators und schaltet keine physikalischen QSB-Claims frei.', 'registered_requires_human_literature_review')
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

INSERT INTO qsb_literature.reference_claim_map (run_id, claim_map_id, bib_key, pillar_id, supports, does_not_support, qsb_connection, allowed_claim, forbidden_claim, review_status) VALUES ('QSB-DWH-PLANCK-BRIDGE-LITNOTE01-IMPORT-01', 'QSB-DWH-PLANCK-BRIDGE-LITNOTE01-IMPORT-01-CM-012', 'rovelli_smolin1995_spin_networks_quantum_gravity', 'emergent_relational_spacetime', 'Zeigt, dass emergente, relationale, informationelle, kausale oder netzwerkartige Geometrie eine seriöse Forschungsfrage ist.', 'Bestätigt QSB nicht automatisch und macht relationale Netzwerke nicht automatisch zu physikalischer Raumzeit.', 'Erlaubt, ein Resonator-Netz als operationalisierbaren Emergenzkandidaten zu prüfen.', 'Die Quelle motiviert die Interface-Frage und wird als Literaturanker registriert.', 'Die Quelle beweist nicht die Existenz des Planck-Bridge-Resonators und schaltet keine physikalischen QSB-Claims frei.', 'registered_requires_human_literature_review')
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

INSERT INTO qsb_literature.reference_claim_map (run_id, claim_map_id, bib_key, pillar_id, supports, does_not_support, qsb_connection, allowed_claim, forbidden_claim, review_status) VALUES ('QSB-DWH-PLANCK-BRIDGE-LITNOTE01-IMPORT-01', 'QSB-DWH-PLANCK-BRIDGE-LITNOTE01-IMPORT-01-CM-013', 'bombelli_lee_meyer_sorkin1987_causal_set', 'emergent_relational_spacetime', 'Zeigt, dass emergente, relationale, informationelle, kausale oder netzwerkartige Geometrie eine seriöse Forschungsfrage ist.', 'Bestätigt QSB nicht automatisch und macht relationale Netzwerke nicht automatisch zu physikalischer Raumzeit.', 'Erlaubt, ein Resonator-Netz als operationalisierbaren Emergenzkandidaten zu prüfen.', 'Die Quelle motiviert die Interface-Frage und wird als Literaturanker registriert.', 'Die Quelle beweist nicht die Existenz des Planck-Bridge-Resonators und schaltet keine physikalischen QSB-Claims frei.', 'registered_requires_human_literature_review')
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

INSERT INTO qsb_literature.reference_claim_map (run_id, claim_map_id, bib_key, pillar_id, supports, does_not_support, qsb_connection, allowed_claim, forbidden_claim, review_status) VALUES ('QSB-DWH-PLANCK-BRIDGE-LITNOTE01-IMPORT-01', 'QSB-DWH-PLANCK-BRIDGE-LITNOTE01-IMPORT-01-CM-014', 'swingle2012_holographic_spacetimes_entanglement_renormalization', 'emergent_relational_spacetime', 'Zeigt, dass emergente, relationale, informationelle, kausale oder netzwerkartige Geometrie eine seriöse Forschungsfrage ist.', 'Bestätigt QSB nicht automatisch und macht relationale Netzwerke nicht automatisch zu physikalischer Raumzeit.', 'Erlaubt, ein Resonator-Netz als operationalisierbaren Emergenzkandidaten zu prüfen.', 'Die Quelle motiviert die Interface-Frage und wird als Literaturanker registriert.', 'Die Quelle beweist nicht die Existenz des Planck-Bridge-Resonators und schaltet keine physikalischen QSB-Claims frei.', 'registered_requires_human_literature_review')
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


-- Hard validation inside transaction: fail if counts or claim lock are wrong.
DO $$
DECLARE
    source_count INTEGER;
    claim_count INTEGER;
    released_count INTEGER;
BEGIN
    SELECT COUNT(*) INTO source_count FROM qsb_literature.reference_source
     WHERE run_id = 'QSB-DWH-PLANCK-BRIDGE-LITNOTE01-IMPORT-01';
    SELECT COUNT(*) INTO claim_count FROM qsb_literature.reference_claim_map
     WHERE run_id = 'QSB-DWH-PLANCK-BRIDGE-LITNOTE01-IMPORT-01';
    SELECT COUNT(*) INTO released_count FROM qsb_literature.reference_source
     WHERE run_id = 'QSB-DWH-PLANCK-BRIDGE-LITNOTE01-IMPORT-01'
       AND physical_claim_release <> 'blocked_no_physics_claim';

    IF source_count <> 14 THEN
        RAISE EXCEPTION 'Expected 14 reference sources, got %', source_count;
    END IF;
    IF claim_count <> 14 THEN
        RAISE EXCEPTION 'Expected 14 claim-map rows, got %', claim_count;
    END IF;
    IF released_count <> 0 THEN
        RAISE EXCEPTION 'Physical claim release must remain blocked; got % released rows', released_count;
    END IF;
END $$;

COMMIT;
