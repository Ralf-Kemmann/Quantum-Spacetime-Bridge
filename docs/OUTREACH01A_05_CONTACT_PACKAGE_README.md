# OUTREACH01A-05 Contact Package README

package_id = OUTREACH01A_CONTACT_PACKAGE_V1
outreach_id = OUTREACH01A-05
package_title = Visible Contact Figure and Contact-Package Assembly

## 1. Zweck des Pakets

Das Paket macht den kleinen synthetischen OUTREACH01A-DTC-DEMO01-Fall sichtbar lesbar. Es zeigt zuerst die Zustands- und Grenzstruktur, dann die knappe Tabelle, und erst danach die technische Einordnung.

## 2. Primäre englische Fassung

primary_visible_package_language = English

Die englische Fassung ist die primäre sichtbare Paketfassung. Sie trägt die erste technische Leseschicht und bleibt an den kanonischen Records `DTC_A`, `DTC_B` und `BOUNDARY_AB`.

Die vollständige englische Technical Note `artifacts/OUTREACH01A-05/technical_note_en.md` ist Bestandteil des ersten Kontaktpakets. Sie wird aus der geprüften OUTREACH01A-04-Zweiseiten-Notiz übernommen und nicht durch die kurze Preview ersetzt.

## 3. Spanische Sprachdemonstration

secondary_demonstration_language = Spanish
spanish_view_included_to_demonstrate_language_layer_architecture = yes

Die spanische Fassung ist eine Demonstration der Sprachschicht. Sie soll zeigen, dass Anzeigenamen und erklärende Sätze wechseln können, ohne den Datensatz, die Logik oder die Claim Boundary zu verändern.

Die spanische Technical Note ist die parallele Sprachschicht zur vollständigen englischen Notiz. Sie ist nicht für den ersten Kontakt erforderlich, bleibt aber Teil des Review-Pakets, weil sie die Spracharchitektur sichtbar prüfbar macht.

## 4. Sichtbare Abbildungen

Die beiden Kontaktfiguren zeigen dieselbe Struktur in zwei Sprachen. Die Architekturabbildung zeigt einen einzelnen kanonischen Datensatz mit zwei Leseschichten. Diese Figuren ersetzen keine Messdaten und keine quantitative Auswertung.

## 5. Kompakte Tabellen

Die Tabellen listen genau drei Records: `DTC_A`, `DTC_B` und `BOUNDARY_AB`. Sie halten Typ, Äquivalenzklasse, Phase, Domäne, Boundary-Rolle und Evidenzstatus knapp nebeneinander.

## 6. Was intern bleibt

Manifest, File-List, Figure Validation, Builder-Ausgaben und temporäre Renderdateien sind Audit- und Prüfmaterial. Sie sind nicht als Kontakttext gemeint.

Die Dateien `preview_en.md` und `preview_es.md` sind kompakte Paketübersichten. Sie sind keine Technical Notes und ersetzen die vollständigen Notizen nicht.

## 7. Red-Team-Prüfweg

Der Red-Team-Prüfweg beginnt mit der englischen Preview, vergleicht danach die spanische Fassung und prüft schließlich Manifest, Hashes, Cross-Language-Check, Rendercheck und externe Attestationen.

Die automatische Renderprüfung ist keine menschliche Sichtprüfung. Der Builder darf SVGs rendern, Dimensionen prüfen und Textmarker detektieren. Lesbarkeit, Textüberlappung und Stilwirkung werden nicht vom Builder selbst attestiert, sondern nur über externe Review-JSONs dokumentiert.

## 8. Formeller Eingangsscheck

Der formelle Check fragt zuerst: Sind alle sichtbaren Dateien vorhanden, stimmen die sieben Hashes, wurden die drei SVGs real gerendert, liegen externe Sicht- und Stilattestationen vor, und bleibt der Send-Gate geschlossen?

Die Paket-ID `OUTREACH01A_CONTACT_PACKAGE_V1` ist vom Titel `Visible Contact Figure and Contact-Package Assembly` getrennt. Die englischen und spanischen technischen Fragen werden über stabile HTML-kommentierte Frage-IDs abgeglichen. Dieser Abgleich bestätigt ID- und Reihenfolgenparität, behauptet aber keine automatische semantische Äquivalenz.

## 9. Fachliches Interview

Das fachliche Interview sollte bei der kleinen Frage bleiben: Was folgt aus geteilter dynamischer Äquivalenz, was folgt nicht, und wie offen bleibt die Grenzrepräsentation?

## 10. Interne AG-Prüfung

Die interne AG-Prüfung kann die Spracharchitektur getrennt von der Fachstruktur lesen. Genau diese Trennung ist der Sinn der spanischen Demonstrationsschicht.

## 11. Versand-Gate

red_team_review_required = true
package_ready_for_red_team = true
package_ready_for_send = false
contact_message_present = false
contact_send_allowed = false
user_release_required_before_send = true

Dieses Paket enthält keine Mail und keine Versandfreigabe. `package_ready_for_red_team` erfordert sowohl die externe Sichtprüfung als auch die externe Stilprüfung. `package_ready_for_send` bleibt false.

## 12. bekannte Grenzen

Die Daten sind synthetisch. Das Paket behauptet keine experimentelle Validierung, keine Erklärung eines realen Lasersystems und keine physikalische Entstehungsaussage.
