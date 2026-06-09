-- QSB-OUTREACH01A SQLite presentation views.
-- Review artifact only; not executed during setup or correction run.
-- Canonical storage fields remain unchanged; language-specific SQL aliases are ASCII-safe.

CREATE VIEW qsb_v_outreach01a_state_en AS
SELECT
    hs.event_instance_id AS event_instance_id,
    hs.state_descriptor_id AS state_descriptor_id,
    hs.state_id AS state_id,
    hs.source_record_id AS source_record_id,
    hs.forcing_cycle_index AS forcing_cycle_index,
    hs.forcing_phase AS forcing_phase,
    hs.response_phase_class AS response_phase_class,
    hs.observable_recurrence_class AS observable_recurrence_class,
    hs.full_state_equivalence_class AS full_state_equivalence_class,
    hs.domain_label AS domain_label,
    hs.background_state_type AS background_state_type,
    hs.background_state_json AS background_state_json,
    hs.history_representation_type AS history_representation_type,
    hs.history_descriptor_json AS history_descriptor_json,
    hs.history_window_start AS history_window_start,
    hs.history_window_end AS history_window_end,
    hs.history_embedding_method AS history_embedding_method,
    hs.history_embedding_version AS history_embedding_version,
    hs.transformation_version AS transformation_version
FROM outreach_harmonized_state AS hs;

CREATE VIEW qsb_v_outreach01a_state_de AS
SELECT
    hs.event_instance_id AS ereignisinstanz_id,
    hs.state_descriptor_id AS zustandsbeschreibung_id,
    hs.state_id AS zustands_id,
    hs.source_record_id AS quell_datensatz_id,
    hs.forcing_cycle_index AS anregungszyklus_index,
    hs.forcing_phase AS anregungsphase,
    hs.response_phase_class AS antwortphasenklasse,
    hs.observable_recurrence_class AS beobachtbare_wiederkehrklasse,
    hs.full_state_equivalence_class AS vollzustands_aequivalenzklasse,
    hs.domain_label AS domaenenbezeichnung,
    hs.background_state_type AS hintergrundzustand_typ,
    hs.background_state_json AS hintergrundzustand_json,
    hs.history_representation_type AS historienrepraesentation_typ,
    hs.history_descriptor_json AS historiendeskriptor_json,
    hs.history_window_start AS historienfenster_start,
    hs.history_window_end AS historienfenster_ende,
    hs.history_embedding_method AS historienembedding_methode,
    hs.history_embedding_version AS historienembedding_version,
    hs.transformation_version AS transformationsversion
FROM outreach_harmonized_state AS hs;

CREATE VIEW qsb_v_outreach01a_state_ca AS
SELECT
    hs.event_instance_id AS identificador_instancia_esdeveniment,
    hs.state_descriptor_id AS identificador_descriptor_estat,
    hs.state_id AS identificador_estat,
    hs.source_record_id AS identificador_registre_origen,
    hs.forcing_cycle_index AS index_cicle_excitacio,
    hs.forcing_phase AS fase_excitacio,
    hs.response_phase_class AS classe_fase_resposta,
    hs.observable_recurrence_class AS classe_recurrencia_observable,
    hs.full_state_equivalence_class AS classe_equivalencia_estat_complet,
    hs.domain_label AS etiqueta_domini,
    hs.background_state_type AS tipus_estat_fons,
    hs.background_state_json AS json_estat_fons,
    hs.history_representation_type AS tipus_representacio_historia,
    hs.history_descriptor_json AS json_descriptor_historia,
    hs.history_window_start AS inici_finestra_historia,
    hs.history_window_end AS final_finestra_historia,
    hs.history_embedding_method AS metode_incrustacio_historia,
    hs.history_embedding_version AS versio_incrustacio_historia,
    hs.transformation_version AS versio_transformacio
FROM outreach_harmonized_state AS hs;

CREATE VIEW qsb_v_outreach01a_relation_en AS
SELECT
    mr.run_code AS run_code,
    mr.model_version AS model_version,
    si.event_instance_id AS event_instance_i,
    sj.event_instance_id AS event_instance_j,
    si.state_descriptor_id AS state_descriptor_i,
    sj.state_descriptor_id AS state_descriptor_j,
    rp.pair_logic AS pair_logic,
    rp.similarity_score AS similarity_score,
    rp.phase_distance AS phase_distance,
    rp.cycle_distance AS cycle_distance,
    rp.observable_match AS observable_match,
    rp.class_match AS class_match,
    rp.edge_status AS edge_status
FROM outreach_relational_pair AS rp
JOIN outreach_model_run AS mr ON mr.model_run_id = rp.model_run_id
JOIN outreach_harmonized_state AS si ON si.harmonized_state_id = rp.state_i_id
JOIN outreach_harmonized_state AS sj ON sj.harmonized_state_id = rp.state_j_id;

CREATE VIEW qsb_v_outreach01a_relation_de AS
SELECT
    mr.run_code AS lauf_code,
    mr.model_version AS modellversion,
    si.event_instance_id AS ereignisinstanz_i,
    sj.event_instance_id AS ereignisinstanz_j,
    si.state_descriptor_id AS zustandsbeschreibung_i,
    sj.state_descriptor_id AS zustandsbeschreibung_j,
    rp.pair_logic AS paarlogik,
    rp.similarity_score AS aehnlichkeitswert,
    rp.phase_distance AS phasenabstand,
    rp.cycle_distance AS zyklusabstand,
    rp.observable_match AS beobachtbare_uebereinstimmung,
    rp.class_match AS klassenuebereinstimmung,
    rp.edge_status AS kantenstatus
FROM outreach_relational_pair AS rp
JOIN outreach_model_run AS mr ON mr.model_run_id = rp.model_run_id
JOIN outreach_harmonized_state AS si ON si.harmonized_state_id = rp.state_i_id
JOIN outreach_harmonized_state AS sj ON sj.harmonized_state_id = rp.state_j_id;

CREATE VIEW qsb_v_outreach01a_relation_ca AS
SELECT
    mr.run_code AS codi_execucio,
    mr.model_version AS versio_model,
    si.event_instance_id AS instancia_esdeveniment_i,
    sj.event_instance_id AS instancia_esdeveniment_j,
    si.state_descriptor_id AS descriptor_estat_i,
    sj.state_descriptor_id AS descriptor_estat_j,
    rp.pair_logic AS logica_parella,
    rp.similarity_score AS puntuacio_similitud,
    rp.phase_distance AS distancia_fase,
    rp.cycle_distance AS distancia_cicle,
    rp.observable_match AS coincidencia_observable,
    rp.class_match AS coincidencia_classe,
    rp.edge_status AS estat_aresta
FROM outreach_relational_pair AS rp
JOIN outreach_model_run AS mr ON mr.model_run_id = rp.model_run_id
JOIN outreach_harmonized_state AS si ON si.harmonized_state_id = rp.state_i_id
JOIN outreach_harmonized_state AS sj ON sj.harmonized_state_id = rp.state_j_id;
