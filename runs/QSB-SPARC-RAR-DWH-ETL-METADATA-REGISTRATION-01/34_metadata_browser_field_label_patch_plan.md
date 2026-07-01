# Metadata Browser Field Label Patch Plan

Befund: Deutsche SPARC/RAR-Aliase sind in der run-lokalen Tabelle `meta_alias` und View `v_de_sparc_feldnamen` registriert.

Interpretation: Ein Patch an `scripts/sqlite_tkinter_crud_app/src/field_labels.py` ist nicht erforderlich, solange der Browser DB-Views lesen kann.

Offene Lücke: Falls statische UI-Labels verlangt werden, sollte ein separater, explizit freigegebener Patch-Run erstellt werden.
