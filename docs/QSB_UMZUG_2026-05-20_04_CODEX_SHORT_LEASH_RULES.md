# QSB / Gravitation und RaumZeit — Codex-Kurze-Leine-Regeln

## 1. Rolle von Codex

Codex ist der lokale Schraubenschlüssel.

Codex erstellt:

- neue Dateien,
- Scripts,
- Configs,
- lokale Runs,
- Acceptance-Outputs,
- kurze technische Berichte.

Codex entscheidet nicht über wissenschaftliche Claims.

## 2. Harte Pfadregel

Jeder Codex-Auftrag beginnt mit:

```bash
cd /home/ralf-kemmann/Downloads/deBroglie_Kaster_Theorie/quantum-spacetime-bridge
pwd
git status -sb
git log --oneline -12
```

Wenn `pwd` nicht exakt ist:

```text
/home/ralf-kemmann/Downloads/deBroglie_Kaster_Theorie/quantum-spacetime-bridge
```

dann:

```text
STOPP
nichts ändern
berichten
```

Erwarteter sauberer Status:

```text
## main...origin/main
```

## 3. Git-Regel

Codex darf nicht ungefragt:

```text
git add
git commit
git push
git reset
git checkout
git clean
git rm
```

Git-Aktionen macht Ralf, nachdem Nova das Ergebnis geprüft hat.

## 4. Datei-Regel

Codex darf nur die explizit erlaubten Dateien erstellen oder ändern.

Keine stillen Änderungen.

## 5. Output-Regel

Run-Outputs nur in angegebenen Ordnern:

```text
runs/<BLOCK>/<run_name>/
```

Lange Acceptance-Outputs:

```text
~/Downloads/Textfiles/
```

## 6. Acceptance-Regel

Implementierungen brauchen:

```text
python -m py_compile <script>
python <script>
summary.json check
csv row count check
readout section check
claim-risk grep
required boundary terms grep
git diff --check
git status -sb
```

Dokumentdateien brauchen:

```text
required section check
claim-risk grep
required boundary terms grep
git diff --check
git status -sb
```

## 7. Claim-Risk-Grep

Typische verbotene Ausdrücke:

```text
physical time recovered
proper time recovered
Lorentz metric derived
spacetime validated
Bridge validated
specificity proven
causal order established
physical wavefunction proven
electron created
Big Bang explained
redshift detected
```

## 8. Pflichtgrenzen für aktuelle COMP01-D-Linie

Neue COMP01-D-Dateien müssen sinngemäß enthalten:

```text
psi is a diagnostic pattern object here, not automatically a physical wavefunction.
wave identity fingerprints are diagnostic distinguishability observables, not physical observables by themselves.
spectral shift is used here as a diagnostic analogy, not as cosmological redshift.
phase drift is used here as a structure-internal pattern marker, not as physical time delay.
real_imag_proxy is a diagnostic component split, not a physical derivation.
The complex trigonometric notation is a planned formal representation, not yet an implemented physical wavefunction model.
tau is not physical time.
tau is not proper time.
tau is not a universal clock.
COMP01-D does not attach D(A,B).
COMP01-D does not construct S_rel2.
COMP01-D does not derive a Lorentzian metric.
COMP01-D does not validate a physical Bridge.
COMP01-D does not establish diagnostic specificity yet.
This is synthetic diagnostic concept/design work only.
```

## 9. Berichtspflicht am Ende

Codex berichtet immer:

```text
- pwd
- git status vor Beginn
- Datei erstellt
- bestehende Dateien geändert
- Run-Outputs
- Kommandos
- Checks
- Claim Boundary
- Offene Grenzen
- git status -sb
```
