# WORKFLOW_ACTIVE_BLOCK.md
## Aktiver Block: M.3.9a.2 — Family Full Audit

### Status
Aktiv

---

## 1. Blockname

**M.3.9a.2 — Vollaudit der neuen Familien mit matched-pair- und F5-Falsifikationsblock**

---

## 2. Ziel

Dieser Block soll prüfen, ob die im Familien-Precheck getrennten Typen

- **F1** als Kontrolle,
- **F2** als kompakt-negativer Typ,
- **F3/F4** als groß-negative Typen,
- optional **F5** als Falsifikationskandidat,

nicht nur strukturell unterscheidbar sind, sondern auch in der **Branch-Mechanik** belastbar unterschiedliche oder gemeinsame Rollen zeigen.

Kernfrage:

> Bleibt `delta_p2` auf dem neuen Familien-Set der stärkste branchrelevante Marker, und ist seine Rolle eher mechanistisch oder nur korrelativ?

---

## 3. Nicht-Ziel

Dieser Block soll **noch nicht** beweisen, dass `delta_p2` die endgültige fundamentale Größe des Projekts ist.

Er soll vielmehr klären:

- ob `delta_p2` im neuen Familienraum wieder dominant bleibt,
- ob kompakt-negative und groß-negative Familien mechanisch gleich oder verschieden wirken,
- ob F1 erwartungsgemäß kontrollartig bleibt,
- und ob F5 als echter Falsifikationskandidat funktioniert.

---

## 4. Eingangsset

### Hauptset
- **F1** — symmetrische Kontrolle
- **F2** — kompakt-negativer Kandidat
- **F3** — groß-negativer Kandidat
- **F4** — nichtaffin verzerrter groß-negativer Kandidat

### Zusatzset
- **F5** — asymmetrie-abgeschwächte Gegenprobe / Falsifikationskandidat

---

## 5. Zentrale Verschärfungen

### 5.1 Matched-pair strategy

Verpflichtend zwischen:
- **F2 vs F3**
- **F2 vs F4**
- optional **F3 vs F4**

Leitfrage:

> Erzeugen Paare aus F2 und F3/F4 mit vergleichbarem `delta_p2` dieselben Branch-Identitäten oder verschiedene?

Operative Matching-Regel:
- relative `delta_p2`-Toleranz: **±5 %**
- optionale absolute Toleranz zusätzlich
- gleiches Vorzeichen von `delta_p2` bevorzugt
- best match only zunächst zulässig

### 5.2 F5 als echter Falsifikationskandidat

Vorhersage:

> F5 soll keine stabilen Branch-Identitäten oder jedenfalls deutlich schwächere `branch_match_frac`-/Identity-Maße zeigen als F2/F3/F4.

Falsifikationslogik:
- wenn F5 ähnlich stark brancht wie F2/F3/F4, ist das ein Problem für die aktuelle Mechanismus-Hypothese

### 5.3 `alpha != 1`-Klausel

- `delta_p2` bleibt generell eine quadratische Impulsdifferenz
- direkte Energiebedeutung nur im freien quadratischen Referenzbild

Defensive Regel:
- `alpha = 1` → relationale kinetische Energiedifferenz lesbar
- `alpha != 1` → nur noch dispersionsneutrale quadratische Impulsdifferenz, direkte Energielesart nicht naiv übertragbar

---

## 6. Implementationsartefakte

### Config
- `configs/config_m39a_family_full_audit.yaml`

### Runner
- `src/m39a_family_full_audit_runner.py`

### Erwartetes Bootstrap-Skript
- `scripts/bootstrap_m39a_family_full_audit.sh`

### Familien-Input
- `configs/m39a_family_definitions.yaml`

---

## 7. Erwartete Outputs

Mindestens:
- `family_audit_case_table.csv`
- `family_audit_pair_summary.csv`
- `family_audit_class_summary.csv`
- `family_audit_global_summary.json`
- `family_audit_branch_summary.csv`
- `family_audit_report.md`

Zusätzlich verpflichtend:
- `family_matched_pair_summary.csv`
- `family_matched_pair_branch_compare.csv`
- `family_f5_falsification_summary.csv`
- `family_alpha_interpretation_notes.md`

---

## 8. Erfolgskriterien

Der Block gilt als positiv, wenn:

1. `delta_p2` im neuen Familien-Set wieder die stärkste Klassenebene ist
2. F1 kontrollartig bleibt
3. F5 deutlich schwächer bleibt als F2/F3/F4
4. der matched-pair-Vergleich interpretierbar ist
5. aus F2 vs F3/F4 ein klarer mechanischer Befund entsteht:
   - gleiche Branch-Identitäten → stärkt `delta_p2` als Mechanismuskandidat
   - verschiedene Branch-Identitäten → spricht für zusätzliche Typstruktur jenseits von `delta_p2`

---

## 9. Gegenkriterien

Der Block spricht gegen die aktuelle Mechanismus-Hypothese, wenn:

1. `delta_p2` seine Dominanz verliert
2. F1 künstlich stark brancht
3. F5 ähnlich stark brancht wie F2/F3/F4
4. matched pairs keine interpretierbare Struktur liefern
5. Paaridentität wieder robuster wird als Klassenstruktur

---

## 10. Aktueller nächster Schritt

1. Config und Runner in die aktive Werkbank übernehmen
2. Bootstrap-Skript für `m39a_family_full_audit` anlegen
3. ersten Lauf durchführen
4. Outputs physikalisch auswerten
5. F5 und matched-pair-Befund gezielt prüfen

---

## 11. Ein-Satz-Synthese

> M.3.9a.2 ist der erste volle Mechanismusblock auf dem neuen Familien-Set und soll durch Dominanzprüfung, matched-pair-Vergleich und expliziten F5-Falsifikationstest klären, ob `delta_p2` mechanisch trägt oder vor allem korrelativ stark ist.

