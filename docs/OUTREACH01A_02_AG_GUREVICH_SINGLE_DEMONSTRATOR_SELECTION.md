# OUTREACH01A-02 — AG Gurevich Technical Slice and Single Demonstrator Selection

## 1. Status and Purpose

```text
outreach_id = OUTREACH01A-02
document_type = internal_single_demonstrator_selection_note
contact_message_present = no
contact_sent = no
demonstrator_created = no
exactly_one_demonstrator_selected = yes
selected_demonstrator_count = 1
contact_package_preparation_allowed = yes
contact_message_drafting_allowed = no
contact_send_allowed = no
```

Zweck dieses internen Blocks ist die verbindliche Auswahl genau eines Demonstrators für ein späteres, eng begrenztes Kontaktpaket an die AG Gurevich. Die Auswahl betrifft Kontakttauglichkeit für drei technische Fragen, nicht wissenschaftliche Überlegenheit der Kandidaten.

Gelesene Abhängigkeiten:

- `docs/OUTREACH01A_01_AG_GUREVICH_FIT_CONTACT_GOAL_AND_EVIDENCE_BOUNDARY.md`
- `docs/QSB_CAUSALITY07_01_OSCILLATORY_REACTION_STATE_CYCLE_CASE_DEFINITION.md`
- `docs/QSB_CAUSALITY07_02_FIRST_OSCILLATORY_STATE_CYCLE_DATA_AND_RUNNER_SPEC.md`
- `docs/QSB_ST_IDSPACE01_IDENTITY_SPACE_DEFINITION_SPEC.md`
- `docs/QSB_ST_IDSPACE_CPNS04_MINIMAL_SCHEMA_SCAFFOLD_RESULT_NOTE.md`

Gezielt gesichtete Artefakte:

- `data/QSB-ST-IDSPACE-CPNS04/idspace_cpns04_minimal_schema.json`
- `data/QSB-ST-IDSPACE-CPNS04/idspace_cpns04_example_records.json`
- `data/QSB-CAUSALITY07-02/cycle_phase_rules.json`
- `data/QSB-CAUSALITY07-02/field_aliases_de.json`
- `runs/QSB-CAUSALITY07-02/first_oscillatory_state_cycle/run_summary.json`
- `runs/QSB-CAUSALITY07-02/first_oscillatory_state_cycle/cycle_recurrence_results.csv`
- `runs/QSB-CAUSALITY07-02/first_oscillatory_state_cycle/p0_vs_p0_prime_comparison.csv`

Vorbedingung aus OUTREACH01A-01:

```text
fit_to_full_QSB_program = no
fit_to_narrow_state_transition_slice = yes
contact_goal = request_for_technical_assessment
technical_relevance_established = no
contact_gate_status = held
user_release_required_before_send = yes
```

## 2. Contact Questions to Support

Der spätere Demonstrator soll genau diese drei technischen Fragen tragen:

1. Ist es methodisch sinnvoll, bei zwei um eine Antriebsperiode verschobenen, aber physikalisch äquivalenten zeitkristallinen Konfigurationen zwischen Identität, dynamischer Äquivalenz und zeitlicher Phasenlage explizit zu unterscheiden?

2. Welche minimale Repräsentation wäre angemessen, um langlebige Grenzen zwischen koexistierenden äquivalenten Konfigurationen abzubilden: ein Zustandslabel, ein eigenes Grenzobjekt oder eine andere dynamische Beschreibung?

3. Welche minimale Zustands- oder Beobachtungsinformation wäre aus Sicht der AG erforderlich, damit ein solcher relationaler Zustandsvergleich nicht nur formal sauber, sondern physikalisch aussagekräftig ist?

## 3. Candidate Inventory

```text
candidate_id = A
candidate_name = Existing Oregonator cycle run
existing_or_new = existing
source_artifacts = QSB-CAUSALITY07-02
relevance = temporal_recurrence_and_nonidentity_precedent
main_strength = machine_readable_recurrence_with_P0_vs_P0_prime_and_alias_view
main_weakness = BZ_chemistry_context_and_no_equivalent_DTC_domain_boundary
```

Kandidat A zeigt zehn referenzsequenz-konditionierte Zyklen, P0/P0-prime-Vergleich, beobachtbare Nähe und nicht etablierte vollständige Zustandsidentität. Er ist als interne methodische Vorarbeit nützlich, aber der BZ-/Oregonator-Kontext würde beim Erstkontakt wahrscheinlich von der DTC-nahen Frage ablenken.

```text
candidate_id = B
candidate_name = Existing IDSPACE/CPNS identity demonstrator
existing_or_new = existing
source_artifacts = QSB-ST-IDSPACE / CPNS04
relevance = schema_identity_and_ambiguity_scaffold
main_strength = clean_identity_schema_with_boundary_flags_and_ambiguity_states
main_weakness = no_temporal_phase_shift_no_subharmonic_order_no_domains
```

Kandidat B liefert starke Schema- und Claim-Grenzen: Identitätsobjekte, Fingerprint-Objekte, Äquivalenzentscheidungen, Transformklassen, Ambiguität und boundary flags. Für die AG-Fragen ist er allein zu abstrakt, weil zeitliche Phasenverschiebung, koexistierende Domänen und Grenzstruktur fehlen.

```text
candidate_id = C
candidate_name = New minimal synthetic DTC-near state-identity demonstrator
existing_or_new = new_concept_only_not_created
source_artifacts = OUTREACH01A_DTC_DEMO01_planned
relevance = direct_carrier_for_identity_equivalence_phase_domain_boundary_questions
main_strength = directly_matches_contact_questions_without_BZ_or_full_QSB_context
main_weakness = synthetic_only_and_requires_explicit_non_model_boundary
```

Kandidat C ist noch nicht erzeugt. Er kann gezielt zwei dynamisch äquivalente Konfigurationen `A` und `B`, eine Verschiebung um eine Antriebsperiode, getrennte Domänen, ein eigenes Grenzobjekt und minimale Beobachtungssignaturen abbilden. Seine Synthetik ist keine Schwäche, solange sie vollständig offengelegt wird.

## 4. Selection Matrix

Bewertungsskala:

```text
0 = ungeeignet
1 = schwach
2 = begrenzt
3 = brauchbar
4 = gut
5 = sehr gut
```

Für `Claim-Risiko` bedeutet `5` geringes Claim-Risiko und `0` hohes Claim-Risiko.

| Kriterium | Gewicht | A Score | A Beitrag | B Score | B Beitrag | C Score | C Beitrag |
|---|---:|---:|---:|---:|---:|---:|---:|
| Direkte Passung zu den drei Kontaktfragen | 5 | 2 | 10 | 2 | 10 | 5 | 25 |
| Geringes Missverständnisrisiko | 5 | 2 | 10 | 4 | 20 | 4 | 20 |
| Minimale fachfremde Last | 4 | 1 | 4 | 4 | 16 | 5 | 20 |
| Auditierbare Zustandsidentität | 4 | 4 | 16 | 5 | 20 | 4 | 16 |
| Darstellung dynamischer Äquivalenz | 5 | 1 | 5 | 3 | 15 | 5 | 25 |
| Darstellung zeitlicher Phasenverschiebung | 5 | 2 | 10 | 0 | 0 | 5 | 25 |
| Darstellung einer Grenzstruktur | 5 | 0 | 0 | 0 | 0 | 5 | 25 |
| Reproduzierbarkeit | 3 | 5 | 15 | 4 | 12 | 3 | 9 |
| Umfang für eine Zwei-Seiten-Notiz | 4 | 2 | 8 | 4 | 16 | 5 | 20 |
| Claim-Risiko | 5 | 3 | 15 | 5 | 25 | 4 | 20 |
| `weighted_selection_score` | 45 |  | 93 |  | 134 |  | 205 |

Kurzbegründung:

- A ist reproduzierbar und auditierbar, aber chemisch belastet und ohne DTC-nahe Domänen-/Grenzstruktur.
- B ist schema-stark und claim-arm, aber für zeitliche Phasenlage und Grenzstruktur nicht direkt genug.
- C trifft die Kontaktfragen am unmittelbarsten und vermeidet den BZ-Exkurs. Sein Risiko liegt darin, dass die synthetische Natur sehr klar markiert werden muss.

Die Punktzahl unterstützt die Entscheidung, ersetzt aber nicht das fachliche Urteil.

## 5. Selected Demonstrator

```text
selected_candidate = C
selected_demonstrator_id = OUTREACH01A_DTC_DEMO01
selected_demonstrator_name = Minimal synthetic DTC-near state-identity demonstrator
selected_demonstrator = OUTREACH01A_DTC_DEMO01
demonstrator_status = selected_not_yet_created
selected_demonstrator_count = 1
```

Selection reason:

- Der spätere Kontakt soll keinen BZ-Chemieexkurs auslösen.
- Der vorhandene Oregonator-Lauf bleibt interne methodische Vorarbeit, ist aber nicht der beste Erstkontakt-Demonstrator.
- IDSPACE/CPNS liefert wichtige Architekturbausteine, bildet zeitliche Äquivalenz aber nicht direkt ab.
- Ein kleiner synthetischer DTC-naher Demonstrator trifft die drei Kontaktfragen am direktesten.
- Seine Synthetik kann vollständig offengelegt werden.
- Er behauptet weder eine Simulation noch eine Erklärung des berichteten Lasersystems.

Contact-question coverage:

- Frage 1 wird durch `DTC_A` und `DTC_B` mit gleicher Zustandsklasse, gleicher dynamischer Äquivalenzklasse und unterschiedlicher zeitlicher Phasenlage getragen.
- Frage 2 wird durch `BOUNDARY_AB` als eigenes Grenzobjekt getragen, ohne festzulegen, dass dies physikalisch die richtige Modellierung ist.
- Frage 3 wird durch explizite Unsicherheits- und Nichtbelegungsfelder getragen, insbesondere durch die Markierung fehlender physikalischer Mindestinformation.

## 6. Rejected Candidates

```text
rejected_candidate_id = A
rejection_reason = useful_internal_precedent_but_too_much_BZ_chemistry_context_and_no_equivalent_DTC_domain_boundary
retained_internal_role = methodological_precedent_for_recurrence_and_nonidentity
```

Kandidat A wird nicht in das spätere Kontaktpaket übernommen. Er darf intern zeigen, wie Wiederkehr, P0/P0-prime-Nichtidentität, Alias-Views und Claim-Grenzen auditierbar behandelt werden.

```text
rejected_candidate_id = B
rejection_reason = useful_identity_schema_but_no_temporal_phase_shift_no_subharmonic_order_no_domain_boundary
retained_internal_role = schema_and_identity_safeguard_source
```

Kandidat B wird nicht als sichtbarer Erstkontakt-Demonstrator gewählt. Er darf intern die Feldauswahl, Ambiguitätsbehandlung, Transformklassen und boundary flags des späteren synthetischen Demonstrators informieren.

## 7. Selected Demonstrator Boundary

Der ausgewählte Demonstrator darf zeigen:

- zwei äquivalente Zustandskonfigurationen;
- zeitliche Verschiebung um eine Antriebsperiode;
- gleiche Zustandsklasse trotz anderer Phasenlage;
- Domänenzugehörigkeit;
- Grenzstruktur;
- minimale beobachtbare Signaturen;
- Unsicherheits- und Nichtbelegungsfelder.

Er darf nicht zeigen oder behaupten:

```text
real_laser_simulation
experimental_fit
time_crystal_prediction
domain_wall_mechanism_explained
QSB_explains_DTC
QSB_validated_by_DTC
physical_causality_reconstructed
spacetime_or_gravity_claim
```

```text
data_status = synthetic_method_demonstrator
models_reported_laser_experiment = no
experimental_data_used = no
physical_prediction_present = no
real_system_equivalence_claimed = no
```

## 8. Required Minimal Content

Der spätere Demonstrator soll maximal diese Zustandsrecords enthalten:

```text
DTC_A
DTC_B
BOUNDARY_AB
```

Optional ist nur ein minimaler Beobachtungsrecord pro Zeitschritt zulässig, falls er für die Verständlichkeit der drei Records nötig ist.

Kanonische Kernfelder:

```text
record_id
record_type
state_class
dynamic_equivalence_class
temporal_phase_offset
drive_period_units
domain_id
boundary_role
observable_signature
observable_similarity
full_state_identity
equivalence_basis
uncertainty_status
evidence_status
```

Menschenlesbare deutsche Aliase:

| Kanonisches Feld | Deutscher Alias |
|---|---|
| `state_class` | `Zustandsklasse` |
| `dynamic_equivalence_class` | `Klasse der dynamischen Äquivalenz` |
| `temporal_phase_offset` | `Zeitliche Phasenverschiebung` |
| `drive_period_units` | `Verschiebung in Antriebsperioden` |
| `domain_id` | `Domänen-ID` |
| `boundary_role` | `Rolle der Grenzstruktur` |
| `observable_signature` | `Beobachtbare Signatur` |
| `full_state_identity` | `Vollständige Zustandsidentität` |
| `uncertainty_status` | `Unsicherheitsstatus` |

Die Aliase bleiben reine Präsentationsmetadaten. Sie dürfen nicht als Logikinputs verwendet werden.

## 9. Contact-Package Role

```text
contact_package_role = small_auditable_question_carrier
```

Der ausgewählte Demonstrator soll später genau diese Rolle erfüllen:

- eine kompakte Abbildung;
- eine kleine Tabelle mit drei Records;
- maximal ein kurzer Maschinenlesbarkeits-Ausschnitt;
- drei technische Fragen;
- klare Caveats.

Er ist nicht:

```text
proof
theory_summary
laser_model
prediction_engine
repository_showcase
```

Das spätere Kontaktpaket darf bestehende QSB-Artefakte nicht wholesale übernehmen. Oregonator und IDSPACE/CPNS dienen nur als interne Konstruktionsquellen.

## 10. Next Step

Der nächste Block ist:

> **OUTREACH01A-03 — Minimal Synthetic DTC State-Identity Demonstrator**

Dort werden erzeugt:

- Demonstrator-Spezifikation;
- drei minimale Records;
- deutsches Alias-Mapping;
- eine kompakte Abbildung oder Tabellenansicht;
- Validierungsregeln;
- noch keine Kontaktmail.

Keine weitere Auswahlrunde.
