# Extra Notes Classification Audit

This helper classifies notes that are present in `typ_b_analysis/notes` but not part
of the expected core manifest.

Outputs:
- `extra_notes_classification.csv`
- `summary.json`

Suggested use:

```bash
python classify_extra_notes.py \
  --notes-dir ./typ_b_analysis/notes \
  --manifest ./typ_b_analysis/typ_b_notes_expected_manifest.json \
  --outdir ./typ_b_analysis/results_extra_notes_classification
```

What it gives you:
- a coarse category for each extra note
- a first archive hint (`yes` / `maybe`)
- a category count summary
