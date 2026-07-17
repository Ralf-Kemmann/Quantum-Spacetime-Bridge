# Claim-Safe Literature Expansion Source Copy

Source status: `deep-research-report(3).md` was not found in the repository during this run.

This source copy is reconstructed only from the user-supplied task prompt for `QSB/PBR Literature Metadata Server Import 01`. Missing DOI, arXiv, and source URL fields are intentionally left empty or marked as needing verification. No web access was used.

Claim boundary:

```text
literature_context_only_no_internal_evidence_no_mechanism_claim
```

Required boundary values for every imported row:

```text
internal_evidence_flag = false
mechanism_claim_support = false
physical_claim_support = false
allowed_use = context;vocabulary;comparison_structure;red_team_question;mechanism_search_orientation
```

## Seed Rows

### LQG / Discrete Quantum Geometry

L1 | Ashtekar & Lewandowski | 1997 | Quantum theory of geometry. 1: Area operators | GREEN | Primärliteratur | relational_area_operator;area_volume_spectrum
L2 | Ashtekar & Lewandowski | 1998 | Quantum theory of geometry. 2. Volume operators | GREEN | Primärliteratur | area_volume_spectrum;spin_network_polyhedral_geometry
L3 | Lewandowski; Okołów; Sahlmann; Thiemann | 2006 | Uniqueness of diffeomorphism invariant states on holonomy-flux algebras | GREEN | Primärliteratur | holonomy_flux_algebra;gauge_reference_frame_sensitivity
L4 | Haggard; Lewandowski; Sahlmann | 2023 | Emergence of Riemannian Quantum Geometry | GREEN | Review/Handbook-Kapitel | relational_area_operator;holonomy_flux_algebra;spin_network_polyhedral_geometry;area_volume_spectrum
L5 | Freidel & Speziale | 2010 | Twisted geometries: A geometric parametrisation of SU(2) phase space | GREEN | Primärliteratur | spin_network_polyhedral_geometry;gauge_reference_frame_sensitivity
L6 | Bianchi; Donà; Speziale | 2011 | Polyhedra in loop quantum gravity | GREEN | Primärliteratur | spin_network_polyhedral_geometry;area_volume_spectrum
L7 | Bianchi & Haggard | 2012 | Bohr-Sommerfeld Quantization of Space | GREEN-YELLOW | Primärliteratur | area_volume_spectrum;spin_network_polyhedral_geometry

### Holography / D1-D5 / Wadia-Near String Gravity

W1 | Strominger & Vafa | 1996 | Microscopic origin of the Bekenstein-Hawking entropy | GREEN | Primärliteratur | holography_black_hole_entropy
W2 | Maldacena | 1998 | The Large N Limit of Superconformal Field Theories and Supergravity | GREEN | Primärliteratur | gauge_gravity_duality;holography_black_hole_entropy
W3 | Witten | 1998 | Anti de Sitter space and holography | GREEN | Primärliteratur | gauge_gravity_duality;holography_black_hole_entropy
W4 | Aharony; Gubser; Maldacena; Ooguri; Oz | 2000 | Large N field theories, string theory and gravity | GREEN | Review | gauge_gravity_duality;holography_black_hole_entropy
W5 | David; Mandal; Wadia | 2002 | Microscopic formulation of black holes in string theory | GREEN | Review | holography_black_hole_entropy;gauge_gravity_duality
W6 | Dhar; Mandal; Wadia | 1996 | Absorption versus decay of black holes in string theory and T symmetry | GREEN-YELLOW | Primärliteratur | holography_black_hole_entropy
W7 | Alvarez-Gaumé; Basu; Mariño; Wadia | 2006 | Blackhole/String Transition for the Small Schwarzschild Blackhole of AdS5 x S5 and Critical Unitary Matrix Models | YELLOW | Primärliteratur | gauge_gravity_duality;holography_black_hole_entropy;red_team_pathology_warning

### Born Geometry / Metastring / Modular Spacetime

F1 | Tseytlin | 1990 | Duality Symmetric Formulation of String World Sheet Dynamics | GREEN | Primärliteratur | doubled_string_geometry;born_geometry_phase_space
F2 | Hohm; Hull; Zwiebach | 2010 | Generalized metric formulation of double field theory | GREEN | Primärliteratur | doubled_string_geometry;born_geometry_phase_space
F3 | Amelino-Camelia; Freidel; Kowalski-Glikman; Smolin | 2011 | The principle of relative locality | GREEN-YELLOW | Primärliteratur | relative_locality;gauge_reference_frame_sensitivity
F4 | Freidel; Leigh; Minic | 2014 | Born Reciprocity in String Theory and the Nature of Spacetime | YELLOW | Primärliteratur | born_geometry_phase_space;doubled_string_geometry
F5 | Freidel; Leigh; Minic | 2015 | Metastring Theory and Modular Space-time | GREEN-YELLOW | Primärliteratur | modular_spacetime;born_geometry_phase_space;doubled_string_geometry;relative_locality
F6 | Freidel; Leigh; Minic | 2016 | Quantum Spaces are Modular | GREEN-YELLOW | Primärliteratur | modular_spacetime;gauge_reference_frame_sensitivity
F7 | Freidel; Leigh; Minic | 2017 | Intrinsic non-commutativity of closed string theory | GREEN-YELLOW | Primärliteratur | modular_spacetime;doubled_string_geometry;born_geometry_phase_space
F8 | Freidel; Rudolph; Svoboda | 2019 | A Unique Connection for Born Geometry | GREEN | Primärliteratur | born_geometry_phase_space;doubled_string_geometry
F9 | Marotta & Szabo | 2019 | Para-Hermitian Geometry, Dualities and Generalized Flux Backgrounds | GREEN-YELLOW | Review | born_geometry_phase_space;doubled_string_geometry
