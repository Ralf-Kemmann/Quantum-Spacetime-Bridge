# QSB Research Data Browser

**Forschungsdaten, Metadaten und Herkunftsnachweise**

## Zweck

Der QSB Research Data Browser ist eine lokale Tkinter-Desktopanwendung zum lesenden Inspizieren des QSB-Metadatenkatalogs. Die Anwendung öffnet mit einer exhibit-first Präsentationsschicht für CAUSALITY07 und behält die vollständigen Forschungsansichten, Metadaten, physikalischen Größen, Einheiten, Dimensionen, Herkunftsnachweise, Validierungen, Ergebnis-Claim-Beziehungen und offenen Prüfpunkte in einem getrennten Bereich für Fachprüfung.

Die Anwendung ist eine Präsentations- und Inspektionsschicht. Sie validiert keine wissenschaftlichen Aussagen neu und verändert weder Datenbank noch Repository-Inhalte.

## Striktes Read-only-Verhalten

Normale Nutzung arbeitet nicht direkt auf dem Quellkatalog, sondern auf einer verifizierten Snapshot-Kopie:

```text
source database -> verified snapshot copy -> read-only browser
```

Snapshots werden unter `runs/qsb_research_data_browser/snapshots/` erzeugt. Zu jedem Snapshot wird eine Manifestdatei mit Quelle, Snapshotpfad, SHA-256-Prüfsummen, Größe, Zeitstempel, Tabellen-/View-Anzahl, Mart-Codes und Work-Package-Codes geschrieben.

Die Snapshot-Verbindung verwendet `mode=ro&immutable=1` und setzt `PRAGMA query_only = ON`. Zusätzlich blockiert ein Runtime-Guard schreibende oder schemaändernde SQL-Anweisungen.

## Quellauflösung

Die Quelle wird in dieser Reihenfolge gesucht:

1. `--database PATH`
2. `QSB_METADATA_DB`
3. `runs/QSB-META01-03A/unit_dimension_applicability_hardening/qsb_metadata_catalog_hardened.sqlite`
4. `runs/QSB-META01-03/causality07_pilot_metadata/qsb_metadata_catalog.sqlite`

## Start

Aus dem Repository-Root:

```bash
.venv/bin/python scripts/sqlite_tkinter_crud_app/main.py
```

Mit abweichender Datenbank:

```bash
.venv/bin/python scripts/sqlite_tkinter_crud_app/main.py --database /pfad/zu/katalog.sqlite
```

Entwicklerdiagnose ohne Snapshot:

```bash
.venv/bin/python scripts/sqlite_tkinter_crud_app/main.py --no-snapshot --smoke-test
```

`--no-snapshot` ist nicht der normale GUI-Pfad und gibt eine Warnung aus.

## CLI-Optionen

- `--help`
- `--version`
- `--database PATH`
- `--create-snapshot`
- `--snapshot-dir PATH`
- `--overwrite-snapshot`
- `--no-snapshot`
- `--smoke-test`
- `--list-views`
- `--list-tables`

Der Smoke-Test läuft headless und berichtet Quelle, Snapshot, Prüfsummenstatus, Read-only-Verbindung, `query_only`, Tabellen-/View-Anzahl, gefundene deutsche Views und Write-Rejection.

## GUI-Sektionen

- **Überblick / Overview**: Standard-Startseite und visuelles Foyer der CAUSALITY07-Ausstellung. Sie zeigt Titel, kurzen Untertitel, das visuelle Eintrittsexponat, eine kurze Einführung, fünf Exponatkarten und einen kompakten Snapshot-/Read-only-Status.
- **Ausstellung / Exhibition**: Live-Bereich mit fünf datengetriebenen CAUSALITY07-Exponaten. Beim Öffnen einer Foyer-Karte wird das passende Exponat hier angezeigt.
- **Fachprüfung / Expert inspection**: Getrennter Bereich für die bisherigen technischen und auditierbaren Ansichten.
- **Übersicht**: App-Name, Snapshotpfad, Quellpfad, Manifest, Prüfsummen, Mart-/Work-Package-Codes, Tabellen-/View-Anzahl und Read-only-Status.
- **Forschungsansichten**: Dynamisch erkannte Views, bevorzugt `v_de_*`, mit Pagination, Schnellfilter, Spaltenfilter, Sortierung, Kopieren und CSV-Export.
- **Metadatensuche**: Strukturierte Suche über erkannte Metadatenquellen, mit optionalen Filtern für Mart, Arbeitspaket, Objekttyp und Evidenzklasse.
- **Diagramme / Charts**: Diagrammarbeitsbereich für Balken-, Linien-, Streu-, Kreis- und Histogramm-Diagramme aus dem geöffneten Snapshot.
- **Herkunft / Lineage**: Geführte Anzeige von Lineage-Relationen, soweit im Katalog vorhanden.
- **Validierungen**: Anzeige von Validierungsergebnissen und Regeln. Formal-, Dimensions- und physische Ebenen bleiben als Katalogfelder sichtbar getrennt.
- **Claims und Ergebnisse**: Claims, Result Records und Claim-Result-Links, inklusive stützender, qualifizierender, begrenzender und kontextueller Beziehungen.
- **Offene Prüfpunkte**: Unresolved- und Human-Review-nahe Katalogeinträge als reine Anzeige.
- **Datenbankinfo**: Tabellen, Views, Spalten, Manifestinformationen und Snapshotstatus für Expert:innen.

## Überblick / Overview

Der Überblick ist die normale erste Ansicht nach dem Öffnen eines verifizierten Snapshots. Er ist als Foyer der lokalen Tkinter-Ausstellung angelegt: visuell, knapp und orientierend, nicht als technisches Dashboard. Die Seite verwendet die Konfiguration `overview` in `scripts/sqlite_tkinter_crud_app/resources/showcase_exhibits.json` für Tabtitel, Titel, Untertitel, Einführung, Bildressource, Bildcaption, Fallback-Text, Kartenreihenfolge und Statusstrip-Labels.

Die bevorzugte Bildressource ist `scripts/sqlite_tkinter_crud_app/resources/qsb_causality07_exhibition_overview.png`. Sie wird über dieselbe Source-Tree-/Zipapp-Ressourcenlogik geladen wie die Exponatbilder. Das Bild ist ein Präsentationsanker und keine kanonische wissenschaftliche Quelle. Wenn die Ressource fehlt oder nicht dekodiert werden kann, bleibt die Anwendung startfähig und zeigt Titel, Einführung, fünf Exponatkarten und einen kurzen Fallback-Hinweis.

Die fünf Foyer-Karten öffnen direkt die Live-Exponate:

- `CAUSALITY07 — Reaktionszyklus` / `CAUSALITY07 — Reaction Cycle`
- `Zyklus und Kontrollläufe` / `Cycle and Control Runs`
- `Ergebnisse und Grenzen` / `Results and Boundaries`
- `Physikalische Größen` / `Physical Quantities`
- `Offene Fragen` / `Open Questions`

Jede Karte zeigt eine stabile Inventarnummer, einen bilingualen Titel und einen kurzen bilingualen Untertitel. Tastaturfokus, Hover und der aktuell ausgewählte Exponatpfad sind sichtbar markiert. Die Karten verwenden keine rohen internen Exhibit-IDs als sichtbare Labels.

Der kompakte Foyer-Footer zeigt Datamart, Arbeitspakete, Snapshot-Prüfstatus, Read-only-Status, Snapshot-Zeit und Checksum-Status. Raw-Dateipfade bleiben der Fachprüfung vorbehalten.

### Foyer presentation route

```text
Overview -> exhibit -> live data -> chart -> validation -> lineage -> source
```

Diese Route wird über Navigation und Fachprüfungsziele sichtbar gehalten, nicht über lange technische Einführungstexte.

## Ausstellung / Exhibition

Die Ausstellung zeigt die aktive Live-Exponatansicht. Sie zeigt keine rohen `meta_*`-Tabellen als erste Oberfläche, sondern fünf verständliche Exponate:

- `CAUSALITY07 — Reaktionszyklus` / `CAUSALITY07 — Reaction Cycle`
- `Zyklus und Kontrollläufe` / `Cycle and Control Runs`
- `Ergebnisse und Grenzen` / `Results and Boundaries`
- `Physikalische Größen` / `Physical Quantities`
- `Offene Fragen` / `Open Questions`

Die fünf Exponatkarten liegen im Überblick/Foyer und sind die einzige primäre Exponat-Navigation. Die Ausstellung selbst zeigt das ausgewählte Live-Exponat mit Visual-Panel, Museum-Label, Live-Fakten, Daten und Diagramm. Die Fachprüfungs-Navigation bleibt davon getrennt erhalten.

### Per-exhibit posters

Jedes CAUSALITY07-Exponat hat ein eigenes Poster als visuellen Anker. Die Poster liegen unter:

```text
scripts/sqlite_tkinter_crud_app/resources/exhibits/
```

Aktuelle Zuordnung:

- `causality07_reaction_cycle` -> `exhibits/causality_07_reaktionszyklus.png`
- `cycle_control_runs` -> `exhibits/causality_07_zyklus_und_kontrolllaeufe.png`
- `results_boundaries` -> `exhibits/causality_07_ergebnisse_und_grenzen.png`
- `physical_quantities` -> `exhibits/causality_07_physikalische_groessen.png`
- `open_questions` -> `exhibits/causality_07_offene_fragen.png`

Die Zuordnung und die deutsch/englischen Captions stehen in `resources/showcase_exhibits.json` im jeweiligen `visual_panel`. Dort sind außerdem Alt-Text, `image_fit_mode = contain`, Maximalbreite, Maximalhöhe, bevorzugtes Layout und Fallback-Texte hinterlegt. Die GUI liest diese Werte aus der Konfiguration; die Mappings werden nicht in Python dupliziert.

Poster werden über `importlib.resources` beziehungsweise den Source-Tree-Fallback geladen und funktionieren dadurch aus dem Entwicklungsbaum und aus der Zipapp. Die Anzeige bewahrt das Seitenverhältnis, skaliert responsiv nach unten, vermeidet Verzerrung und wird bei Größenänderungen verzögert neu gerendert. Wenn ein Poster fehlt, bleibt das Live-Exponat nutzbar und zeigt einen ruhigen Platzhalter mit bilingualer Fallback-Caption.

Die Poster sind Präsentationsartefakte. Sie überschreiben keine Snapshot-Werte, erzeugen keine Evidenz, ändern keine Claim Boundaries und sind keine kanonischen wissenschaftlichen Datenquellen. Das Foyer-Bild `qsb_causality07_exhibition_overview.png` bleibt davon getrennt und wird nicht durch die Exponatposter ersetzt.

Die Bildressource wird über `importlib.resources` beziehungsweise einen Source-Tree-Fallback geladen, sodass dieselbe Logik aus dem Entwicklungsbaum und aus der Zipapp funktioniert. Wenn das Bild fehlt oder nicht dekodiert werden kann, startet die Anwendung weiter und zeigt die fünf Exponatkarten mit einem kurzen Fallback-Hinweis. In der englischen UI erscheint zusätzlich der Hinweis, dass die Übersichtsgrafik derzeit deutschsprachig ist, während die interaktiven Inhalte auf Englisch angezeigt werden.

Jedes Exponat hat zusätzlich ein eigenes `visual_panel` in `resources/showcase_exhibits.json`. Dort stehen die Posterressource, Alt-Texte, deutsch/englische Caption, deutsch/englische Fallback-Caption und bevorzugter Layoutmodus. Bildressourcen werden wie die Landing-Grafik aus Source-Tree und Zipapp geladen. Wenn eine Exponatgrafik fehlt oder nicht dekodiert werden kann, rendert die GUI eine ruhige schematische Platzhaltergrafik mit kurzer Caption. Diese Platzhalter sind Präsentationsflächen, keine wissenschaftlichen Daten und keine neuen Claims.

Die Live-Exponatansicht folgt der Reihenfolge Titel, kurzer Untertitel, Visual-Panel, Museum-Label, Live-Fakten beziehungsweise Reaktions-/Chart-Bereich und danach die separaten Daten-/Diagramm-Tabs. Der frühere große technische Textblock im Exponat-Intro wurde entfernt; Detailzeilen bleiben im Daten-Tab und technische Herkunft bleibt im Museum-Label aufklappbar.

Das Exponat-Layout ist responsiv. Auf breiteren Fenstern stehen Visual-Panel und Museum-Label nebeneinander; bei kleiner Breite stapelt die Ansicht Visual, Label, Live-Bereich und Fakten vertikal. Der Summary-Bereich ist scrollbar und aktualisiert seine Scrollregion nach Layoutänderungen sowie nach dem Aufklappen der technischen Herkunft. Dadurch bleiben lange deutsche oder englische Labels und lange Provenance-Texte erreichbar, ohne Labelzeilen zu verbergen oder abzuschneiden.

Die Exponate lösen Inhalte in dieser Reihenfolge auf: explizite Showcase-Konfiguration, Datenbankaliasse und Metadaten, dynamische Felderkennung, leere Anzeige mit Quellenhinweis. Die Konfiguration liegt in `scripts/sqlite_tkinter_crud_app/resources/showcase_exhibits.json`. Sie enthält Titel, Untertitel, bevorzugte Quellen, Fallback-Quellen, Feldlisten, Reaktionsgleichungs-/Reaktionsschema-Quellen, Chart-Presets, Claim-/Boundary-Themen und Expert-Navigationsziele. Sie enthält keine wissenschaftlichen Ergebniswerte; Werte kommen aus dem geöffneten Snapshot oder aus explizit referenzierten Projektquellen.

Das erste Exponat zeigt eine prominente Reaktionsgleichungs- oder Reaktionsschema-Fläche. Für CAUSALITY07 wird kein generisches Oregonator-Lehrbuchschema konstruiert. Wenn der aktuelle Snapshot keine Gleichung enthält, kann die kuratierte Konfiguration auf eine belegte Projektquelle verweisen. Die aktuelle Konfiguration verweist auf `data/QSB-CAUSALITY07-02/oregonator_config.json` und zeigt daraus die registrierten dimensionslosen Modellgleichungen als `Modellreaktionsschema` / `Model reaction scheme`; die Evidenzreferenz ist `data/QSB-CAUSALITY07-02/source_inventory.md#SRC_OREGONATOR_1974`. Das ist keine Netto-Reaktionsgleichung und keine vollständige FKN-Mechanismusdarstellung.

### Museum-style exhibit labels

Jedes der fünf CAUSALITY07-Exponate zeigt zusätzlich ein kompaktes Museum-Label im dunklen PM-/Dashboard-Stil. Diese Labels sind Präsentationsobjekte, keine kanonischen wissenschaftlichen Datensätze. Sie verwenden Inventarnummern:

- `QSB-EXH-C07-01`
- `QSB-EXH-C07-02`
- `QSB-EXH-C07-03`
- `QSB-EXH-C07-04`
- `QSB-EXH-C07-05`

Die Labels können je nach Datenlage Felder wie Exponatname, Objekttyp, physikalische Domäne, Modell/System, Datamart, Arbeitspakete, Datenstand, Status, Evidenzklasse, Einheitenstatus, Dimensionsstatus, Quelle/Herkunft, offene Frage und Bezug zur QSB-Interface-Schicht zeigen. Nicht verfügbare Felder werden ausgelassen; es gibt keine leeren dekorativen Zeilen.

Die Auflösung folgt derselben Auditlogik wie die Exponate:

1. explizite Feld- und Präsentationsmappings in `showcase_exhibits.json`,
2. Datenbankmetadaten und Aliasauflösung,
3. live aus dem geöffneten Snapshot gelesene Exponatdaten,
4. kuratierte bilinguale Präsentationstexte,
5. saubere Auslassung nicht belegter Felder.

Über `Technische Herkunft anzeigen` / `Show technical provenance` kann eine kompakte technische Herkunft aufgeklappt werden. Sie zeigt Canonical Mart-Code, Work-Package-Code, Quellrelation, Quellfelder und Snapshot-Checksumme. Diese technischen Angaben sind standardmäßig verborgen, damit das Exponat lesbar bleibt, bleiben aber auditierbar.

Wenn ein Snapshot für ein Exponat keine geeigneten Daten enthält, zeigt die Anwendung einen ruhigen Empty-State mit Snapshotpfad, erwarteter Quelle und Verweis auf die Fachprüfung. Es werden keine Python-Exceptions als Nutzertext angezeigt.

### Academia presentation route

```text
Exhibit -> result -> chart -> validation -> lineage -> source
```

Die Ausstellung ist eine Einstiegsschicht in die Evidenzkette. Diagramme sind abgeleitete Ansichten aus dem Snapshot und keine eigenständigen wissenschaftlichen Claims.

## Metadatensuche

Die Suche durchsucht nicht blind alle fachlichen Viewdaten. Sie erkennt Metadatenrelationen anhand von Relationnamen und introspektierten Spalten, insbesondere `meta_*`-Tabellen und `v_de_*`-Views. Mehrere Suchwörter werden mit UND-Semantik kombiniert; Werte werden als SQL-Parameter gebunden.

## Sprache und Labels

Die Anwendung unterstützt Deutsch und Englisch:

```bash
./runs/qsb_research_data_browser/qsb_research_data_browser.pyz --language de
./runs/qsb_research_data_browser/qsb_research_data_browser.pyz --language en
```

Die GUI bietet zusätzlich einen sichtbaren Sprachumschalter. Die Auswahl wird in `~/.config/qsb_research_data_browser/settings.json` gespeichert, sofern sie nicht per CLI überschrieben wird. Die Ausstellungstitel, Untertitel, Empty-States, Buttons und Gruppenlabels wechseln live; Canonical IDs und Query-Felder bleiben unverändert.

Canonical SQLite-Namen bleiben intern unverändert. Übersetzte Labels werden nur in der Präsentationsschicht verwendet. Die Labelauflösung erfolgt in dieser Reihenfolge:

1. sprachspezifischer Alias aus der Datenbank-Metadaten-/Alias-Schicht,
2. sprachspezifische App-Label-Registry,
3. kuratierte Canonical-Name-Zuordnung,
4. lesbare Formatierung des technischen Namens,
5. unveränderter technischer Name.

Technische Feldnamen können optional zusätzlich angezeigt werden.

## Diagramme / Charts

Unterstützte Diagrammtypen:

- Balkendiagramm / Bar chart
- Liniendiagramm / Line chart
- Streudiagramm / Scatter plot
- Kreisdiagramm / Pie chart
- Histogramm / Histogram

Die Diagramme werden aus dem geöffneten read-only Snapshot erzeugt. Es gibt keinen SQL-Editor und keine Schreiboperationen. Chart-Abfragen laufen über die bestehende allowlist- und guard-basierte Datenbankschicht.

Chart-Presets werden nur angeboten, wenn die dafür benötigten Felder tatsächlich vorhanden sind, etwa Validierungen nach Status, Felder nach Einheitenstatus, Felder nach Dimensionsstatus, Evidenzrelationen nach Beziehungstyp oder CAUSALITY07-Zyklusfelder.

Die Ausstellung kann für registrierte Baseline-/Kontrollzählungen ein Standard-Balkendiagramm erzeugen. Die Y-Achse verwendet `detected complete cycles`; Zählwerte werden als `count` behandelt und nicht als physikalische Einheit.

### Safeguards

- Scatterplots benötigen numerische X- und Y-Felder.
- Histogramme benötigen ein numerisches Feld.
- Kreisdiagramme blockieren negative Werte und zu viele Kategorien.
- Liniendiagramme verlangen eine sinnvoll geordnete X-Achse.
- Feldnamen allein erzeugen keine Einheiten oder Dimensionen.
- Ungeklärte Einheiten bleiben als ungeklärt sichtbar.
- Diagramme sind abgeleitete Visualisierungen, keine eigenständigen wissenschaftlichen Aussagen.

### Chart Engine

Wenn `matplotlib` in der lokalen `.venv` verfügbar ist, wird es für eingebettete Diagramme sowie PNG/SVG-Export verwendet. Falls nicht, startet die Anwendung weiterhin mit einem Tkinter-Canvas-Fallback für einfache Balken-, Linien- und Streudiagramme; SVG-Export bleibt soweit praktisch verfügbar.

```bash
./runs/qsb_research_data_browser/qsb_research_data_browser.pyz --chart-engine-info
```

### Chart Export

Unterstützt werden:

- PNG, wenn `matplotlib` verfügbar ist,
- SVG,
- CSV des exakt geplotteten Datensatzes,
- JSON-Manifest mit Snapshot-Checksumme, Quelle, Feldern, Labels, Aggregation, Sprache, Einheiten-/Dimensionsmetadaten und Chart Engine.

## CSV-Export

Die aktuell angezeigte Seite kann als UTF-8-CSV exportiert werden. Der Export schreibt eine neue Datei außerhalb der Datenbank und erzeugt eine Manifestdatei mit Snapshot-Checksumme, Relation, aktiven Filtern, Zeitstempel und Zeilenzahl. Exporte sind abgeleitete Kopien und keine kanonischen Datenquellen.

## Build

```bash
mkdir -p runs/qsb_research_data_browser
.venv/bin/python -m zipapp \
  scripts/sqlite_tkinter_crud_app \
  -m main:main \
  -p '/usr/bin/env python3' \
  -o runs/qsb_research_data_browser/qsb_research_data_browser.pyz
chmod +x runs/qsb_research_data_browser/qsb_research_data_browser.pyz
```

Start der Zipapp:

```bash
.venv/bin/python runs/qsb_research_data_browser/qsb_research_data_browser.pyz
```

## Tests

```bash
PYTHONPYCACHEPREFIX=/tmp/qsb_pycache \
  .venv/bin/python -m compileall scripts/sqlite_tkinter_crud_app

.venv/bin/python -m unittest discover \
  -s scripts/sqlite_tkinter_crud_app/tests \
  -v

git diff --check
```

## Grenzen

- Die Ausstellung deckt zunächst CAUSALITY07 ab.
- Inhalte hängen vom aktuell geöffneten Metadaten-Snapshot ab.
- Einzelne Exponate können Empty-States zeigen, wenn Daten noch nicht registriert sind.
- Der Browser enthält weiterhin keine einheitliche zentrale Forschungsdatenbank.
- Kuratierte Präsentationsmappings müssen für neue Marts erweitert werden.
- Die Tkinter-Oberfläche ist eine lokale Desktop-App und noch keine öffentliche Web-Erfahrung.
- Diagramme sind abgeleitete Views, keine wissenschaftlichen Claims.
- Eine manuelle Usability-Prüfung bleibt notwendig.

Die Tests verwenden temporäre SQLite-Datenbanken und schreiben nicht in den produktiven QSB-Katalog.

## Einschränkungen

- Diese Version browsed primär den Metadatenkatalog; es gibt noch keine zentrale SQLite-Datenbank mit allen wissenschaftlichen Ergebnisdaten.
- Die Suche ist strukturiert und heuristisch, keine semantische KI-Suche.
- Lineage-Vollständigkeit hängt vom Kataloginhalt ab.
- Die Anwendung ist eine Tkinter-Desktopanwendung, keine öffentliche Webanwendung.
- Interaktive Usability muss manuell geprüft werden.
- Exporte sind abgeleitete Kopien, nicht kanonische Datenquellen.
