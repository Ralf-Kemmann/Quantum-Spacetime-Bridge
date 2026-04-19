# Notes Completeness Audit

This small audit checks whether `typ_b_analysis/notes` contains the expected note set.

Included files:
- `audit_notes_completeness.py`
- `typ_b_notes_expected_manifest.json`

Example:

```bash
python audit_notes_completeness.py   --notes-dir ./typ_b_analysis/notes   --manifest ./typ_b_notes_expected_manifest.json
```

What it reports:
- completeness by note group
- missing notes
- extra notes not covered by the manifest
