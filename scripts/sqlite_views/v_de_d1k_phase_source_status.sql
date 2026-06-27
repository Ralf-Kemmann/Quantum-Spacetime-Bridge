DROP VIEW IF EXISTS v_de_d1k_phase_source_status;

CREATE VIEW v_de_d1k_phase_source_status AS
SELECT
    run_id AS "Lauf-ID",
    case_id AS "Fall-ID",

    phase_source_label AS "Phasenquellen-Kennung",
    CASE phase_source_label
        WHEN 'diagnostic_synthetic_phase_extension_v1'
        THEN 'Diagnostische synthetische Phasenerweiterung v1'
        ELSE phase_source_label
    END AS "Phasenquelle, lesbar",

    phase_exposure_mode AS "Phasenfreilegungsmodus",
    CASE phase_exposure_mode
        WHEN 'deterministic_synthetic_phase_extension'
        THEN 'Deterministische synthetische Phasenfreilegung'
        ELSE phase_exposure_mode
    END AS "Phasenmodus, lesbar",

    phase_construction_rule AS "Konstruktionsregel",
    CASE phase_construction_rule
        WHEN 'deterministic_atan2_from_available_diagnostic_components'
        THEN 'Deterministische atan2-Konstruktion aus vorhandenen Diagnosekomponenten'
        ELSE phase_construction_rule
    END AS "Konstruktionsregel, lesbar",

    CASE lower(phase_is_synthetic_diagnostic)
        WHEN 'true' THEN 'Ja – synthetisches Diagnosefeld'
        WHEN 'false' THEN 'Nein'
        ELSE phase_is_synthetic_diagnostic
    END AS "Synthetisches Diagnosefeld",

    CASE lower(phase_is_physical)
        WHEN 'true' THEN 'Ja – physikalische Phase'
        WHEN 'false' THEN 'Nein – keine physikalische Phase'
        ELSE phase_is_physical
    END AS "Physikalische Phase",

    CASE
        WHEN lower(phase_is_synthetic_diagnostic) = 'true'
         AND lower(phase_is_physical) = 'false'
        THEN 'Methodischer Kontrollraum; keine reale C-layer-Quelle; keine physikalische Interpretation'
        ELSE 'Bitte prüfen'
    END AS "Einordnung",

    interpretation_note AS "Interpretationshinweis",

    phi_i AS "phi_i",
    phi_j AS "phi_j",
    delta_phi_wrapped AS "delta_phi_wrapped",
    cos_delta_phi AS "cos_delta_phi",
    sin_delta_phi AS "sin_delta_phi",
    angular_phase_distance AS "angular_phase_distance"

FROM st_comp01d1k_phase_exposed_case_profile_summary;
