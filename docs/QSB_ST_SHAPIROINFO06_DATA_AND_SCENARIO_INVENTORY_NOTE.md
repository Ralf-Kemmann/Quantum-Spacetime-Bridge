# QSB-ST-SHAPIROINFO06 — Data and Scenario Inventory Note

## Current anchor

`0f2565e Add QSB-ST ShapiroInfo toy comparator result note`

## Source

`deep-research-report(10).md`

Lokal gelesen aus:

`/home/ralf-kemmann/Downloads/deep-research-report(10).md`

Berichtstitel:

`SHAPIROINFO06 Daten- und Szenarioinventar fuer eine vorsichtige ShapiroInfo-Residualsuche`

Builds on:

- `docs/QSB_ST_SHAPIROINFO01_RELATIONAL_DELAY_TO_INFORMATION_RESIDUAL_SPEC.md`
- `docs/QSB_ST_SHAPIROINFO02_MINIMAL_SIGNAL_RECORD_SCHEMA_SPEC.md`
- `docs/QSB_ST_SHAPIROINFO03_TOY_COMPARATOR_PLAN.md`
- `docs/QSB_ST_SHAPIROINFO04_TOY_COMPARATOR_MINIMAL_RUNNER_SPEC.md`
- `docs/QSB_ST_SHAPIROINFO05_TOY_COMPARATOR_RESULT_NOTE.md`

## Kurzfassung Fuer Menschen

- SHAPIROINFO04/05 haben gezeigt, dass der Toy-Comparator technisch
  funktioniert.
- SHAPIROINFO06 fragt nun: Welche oeffentlichen Datenraeume waeren fuer
  spaetere vorsichtige Tests geeignet?
- Ergebnis: PTA-/Pulsar-Timing-Daten sind der sicherste erste halb-reale
  Einstieg.
- Cassini ist physikalisch sehr passend, aber archiv- und korrekturseitig
  schwer.
- VLBI ist relevant, aber modellierungs- und QC-lastig.
- Lensing ist nur sekundaer als Delay-Taxonomie sinnvoll.

## Befund

- Oeffentliche PTA-/Pulsar-Timing-Releases sind derzeit der risikoaermste
  Einstieg fuer einen spaeteren halb-realen Workflow.
- NANOGrav, EPTA, PPTA, IPTA und InPTA liefern dokumentierte Timing-Produkte,
  meist mit `.par`/`.tim`-Formaten, Timingmodellen, Noise-Konventionen,
  Ephemeriden- oder Clock-Kontext und Begleitinformationen.
- Cassini SCE1 liefert eher rohe oder niedrigverarbeitete Radio-Science-
  Produkte wie ATDF/TDF, ODF und RSR. Eine einfache oeffentliche
  Standard-Residualserie liegt daraus nicht als Startprodukt vor.
- Mars Express MaRS und Rosetta RSI sind spaetere Vergleichs- und
  Machbarkeitspfade fuer Radio-Science-Signale.
- VLBI CDDIS NGS/vgosDB ist oeffentlich und fuer Gruppenlaufzeiten relevant,
  aber QC-, Modellierungs- und Provider-/Reprocessing-Last sind hoch.
- Starke Linsen-Zeitverzoegerungen sollten nur sekundaer-taxonomisch genutzt
  werden, weil dort Lichtkurven, Linsenmodelle und Mikrolensing dominieren.

## Dataset-Inventar Kompakt

| dataset_family | examples | observable_type | data_access_level | correction_burden | fingerprint_potential | first_step_suitability | risk_note |
|---|---|---|---|---|---|---|---|
| PTA / Pulsar Timing | NANOGrav 15-year, EPTA DR2, PPTA DR3, IPTA DR2, InPTA DR2 | TOAs, Timingmodelle, DM-/Noise-Kontext, Pulsar-Residualfenster | oeffentliche, dokumentierte Timing-Produkte | mittel; DM, Solarwind, Clock, Ephemeriden, Backend-Jumps, Noise-Modelle | mittel bis gut, je nach Release durch Wideband-DM, Profile, Dynamikspektren oder Templates | hoch; risikoaermster halb-realer Einstieg | Heterogenitaet, Noise-/Correction-Konventionen und Backendeffekte muessen strikt protokolliert werden. |
| Targeted binary pulsar packages, e.g. J0740+6620 | NANOGrav J0740+6620 Timingdaten und Parameterdatei | einzelnes binaeres MSP-Timing-Paket | oeffentliches Spezialpaket | mittel; Orbitmodell, Phasenabdeckung, Clock/Ephemeris, Noise | begrenzt bis mittel; Timing stark, Zusatzkanaele im Paket begrenzt | sehr hoch fuer ersten kleinen Pilot | Orbitmodell-Kovarianzen koennen Residualsprache schnell unklar machen. |
| Cassini SCE1 radio science | Cassini SCE1 RSS, PDS Radio-Science-Produkte | Doppler, Range, offene/geschlossene Schleife, RSR-nahe Signale | oeffentliches Roh-/niedrigverarbeitetes Archiv | hoch; X/Ka-Plasma, Troposphaere, OD-Kette, DSN-Kontext, Pass-QC | gut bei offenen Receiver-/Spektralprodukten | niedrig fuer ersten Schritt; gut fuer spaetere Machbarkeit | Keine einfache oeffentliche Residualserie; Rekonstruktions- und Ancillary-Last hoch. |
| Mars Express MaRS / Rosetta RSI | ESA/NASA MaRS- und RSI-Archive | Doppler, Ranging, Radio-Science-Tracking, teils Phase/Amplitude/Polarisation | oeffentliche rohe und teilweise prozessierte Missionsprodukte | hoch; Solarplasma, Stationen, Ancillaries, Orbit/Tracking-Kette | begrenzt bis gut, je nach Mission und Produktlevel | mittel bis niedrig; spaeterer Vergleichspfad | Missionsphasen, Bodenstationen und Produktlevel duerfen nicht vermischt werden. |
| VLBI group delay | CDDIS NGS, CDDIS vgosDB | Gruppenlaufzeiten, Sessions, Baselines, Sonnenelongation | oeffentlich dokumentierte NGS-/vgosDB-Produkte | hoch; Troposphaere, Ionosphare, Quellenstruktur, Ambiguitaeten, Provider | begrenzt im Standardprodukt; staerker nur mit Roh-/Zusatzdaten | mittel bis niedrig; nach PTA sinnvoller | Modellierungs- und QC-Last kann einfache A/B-Deutung ueberdecken. |
| Strong lensing time delays | COSMOGRAIL, TDCOSMO-artige Produkte | photometrische Lichtkurven und Bild-Zeitverzoegerungen | oeffentliche Kurven/Delay-/Likelihood-Produkte je nach Projekt | hoch, aber andersartig; Linsenmodell, Mikrolensing, Sampling | gut fuer Lichtkurvenform, aber fachlich anderer Kanal | niedrig; nur sekundaere Taxonomie | Nicht als primaeres ShapiroInfo-Propagation-Dataset verwenden. |

## Correction-State Als Pflichtkonzept

Jede spaetere Residualsuche braucht zwingend protokollierte
`Correction-State`-Felder. Ohne diese Felder waeren Residuen nicht
interpretierbar, weil nicht klar waere, welche Standardmodelle,
Kalibrationen, Flags und Noise-Annahmen bereits in einem Produkt stecken.

Mindestens zu protokollieren:

- `GR/Shapiro model state`
- `plasma / DM / ISM state`
- `solar wind state`
- `troposphere / ionosphere state`
- `clock correction state`
- `ephemeris state`
- `source model state`
- `instrument/backend state`
- `noise model state`
- `QC / flag state`

Praktische Konsequenz: Der Correction-State ist nicht Begleittext, sondern ein
Pflichtteil jedes spaeteren Records. Ein Residualkanal ohne gleich starkes
Provenance- und Kontrollprotokoll bleibt nur ein technischer Restwert.

## Testszenarien

| scenario_id | scenario_name | input_data | preprocessing_needed | controls_needed | likely_failure_modes | recommendation |
|---|---|---|---|---|---|---|
| S0 | synthetic benchmark extension | keine Realwelt-Eingaben; SHAPIROINFO04-Toy-Logik mit realistischeren Stoerarten | synthetische DM-/Clock-/Backend-/Troposphaeren-/Session-Flags modellieren | Nullsignal, Inject-and-Recover, Shuffle, falsche vs. richtige Correction-State-Layer | zu einfache Noise-Modelle, zu glatte Toy-Inputs, falsches Vertrauen in Uebertragbarkeit | zuerst ausbauen; bleibt der sauberste Vorlauf vor halb-realen Daten |
| S1 | semi-real pulsar timing workflow | NANOGrav J0740+6620 oder kleines NANOGrav/InPTA-Subset mit `.par`/`.tim` und Correction-Kontext | PINT/tempo2-kompatible Kette, Standard-Timingfit, Residualexport, QC, A/B-Fensterung | Orbitphasen-/Zeitfenster-Kontrollen, DM-/Bandkontrollen, Epoch-Shuffle, Backend-Homogenitaet | DM-/Solarwind-Leckage, Backend-Jumps, Profilentwicklung, Rotrausch-Kovarianz | bester erster halb-realer Pfad |
| S2 | Cassini-style radio-science feasibility study | Cassini SCE1 ATDF/TDF, ODF, RSR plus Ancillary-Kontext | ODF/ATDF lesen, X/Ka- oder Plasma-Korrektur nachbilden, Troposphaere/OD-Kontext pruefen, Pass-QC | Vor/Nach-Konjunktion, Einzelband vs. Dualband, offene vs. geschlossene Schleife, Pass-Holdout | fehlende Ancillaries, DSN-Probleme, ODP-Details, Plasmaextreme, Passarmut | spaeter als Machbarkeitsstudie; nicht erster Ingest |
| S3 | VLBI group-delay feasibility study | CDDIS NGS/vgosDB Sessions, bevorzugt sonnennahe Geometrien | Sessionauswahl, Provider-/Observable-Wahl, geodaetische Standardloesung oder Residualimport, QC | nahe vs. ferne Elongation, Baseline-Schnitte, Provider-Vergleich, Leave-one-source-out | Quellenstruktur, Troposphaere, Ionosphare, Ambiguitaeten, Edit-Regeln | zweiter Realwelt-Track nach PTA, nicht Startpunkt |
| S4 | lensing-delay taxonomy comparison | starke Linsen-Lichtkurven, Delay- und Likelihood-Produkte | Zeitachsen und Unsicherheiten vereinheitlichen; keine Primaeruebertragung auf ShapiroInfo | Vergleich von Shift-/Likelihood-Methoden, Mikrolensing-Sensitivitaet | falsche Analogiebildung, Massenmodell- statt Propagationsdominanz | nur sekundaere Delay- und Artefakt-Taxonomie |

## Empfohlene Reihenfolge

- SHAPIROINFO06 Inventarnotiz jetzt.
- SHAPIROINFO07 Public Dataset Feasibility Matrix.
- SHAPIROINFO08 Toy-to-Semi-Real Adapter.
- Erster halb-realer Kandidat: NANOGrav J0740+6620 oder kleines
  NANOGrav/InPTA-Subset.
- Cassini und VLBI spaeter.
- Lensing nur sekundaer.

## Interpretation

Der Bericht verschiebt das Projekt nicht zu Realweltclaims. Er liefert eine
Landkarte fuer Datenverfuegbarkeit, Korrekturschichten und Risiken. Der
naechste Schritt sollte deshalb nicht sofort ein Download oder Ingest sein,
sondern eine formale Feasibility-Matrix mit klaren Go/No-Go-Kriterien.

## Hypothese

Ein kontrollierter Pulsar-Timing-Pilot koennte der risikoaermste naechste
halb-reale Testpfad sein, weil Format, Timingmodelle und Noise-/Correction-
Konventionen bereits oeffentlich dokumentiert sind.

## Offene Luecke

- keine Daten geladen
- keine echte Analyse
- keine neue Residualsuche
- keine Feasibility-Matrix implementiert
- keine Entscheidung fuer einen konkreten Download
- kein Realwelt-Claim

## Claim Boundary

- no Bridge confirmation
- no physical validation
- no new Shapiro effect claim
- no claim that GR is incomplete
- no claim that any future residual would imply QSB-ST
- no dataset ingestion in this note
- no evidence claim from inventory alone

## Next Possible Blocks

- SHAPIROINFO07 Public Dataset Feasibility Matrix Spec
- SHAPIROINFO07A Correction-State Schema Note
- SHAPIROINFO08 Toy-to-Semi-Real Adapter Plan
- SHAPIROINFO09 Pulsar Timing Pilot Plan

## Acceptance Checks

- Datei existiert.
- Enthaelt PTA / Pulsar Timing.
- Enthaelt Cassini.
- Enthaelt VLBI.
- Enthaelt Correction-State.
- Enthaelt empfohlene Reihenfolge SHAPIROINFO07 und SHAPIROINFO08.
- Risk grep clean.
- `git diff --check` clean.
- `git status --short` reported.
