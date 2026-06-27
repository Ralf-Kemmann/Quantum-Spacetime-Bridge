# QSB RELALG REAL01 MIN Upstream Export Authorized

This package runs the authorized minimal upstream C-layer export attempt for
`QSB-RELALG-REAL01-MIN-UPSTREAM-EXPORT-AUTHORIZED`.

The runner reads the authorization gate, authorization decisions, prior export
contract specs, prior template registry, and export templates. It creates export
CSV files only when the source artifact has explicit ordered-pair fields,
C-layer value fields, source-space information, and row lineage/hash evidence.
If those requirements are not present, it writes blocked status rows and does
not create fake export rows.

Default execution refuses to overwrite an existing non-empty run directory:

```bash
python scripts/qsb_relalg_real01_min_upstream_export_authorized/real01_min_upstream_export_authorized.py
```

Use `--force` only for an intentional rerun:

```bash
python scripts/qsb_relalg_real01_min_upstream_export_authorized/real01_min_upstream_export_authorized.py --force
```

The run does not perform staging, diagnostics, interpretation, or physics-claim
work. Claim status remains
`authorized_upstream_export_only_no_phi_computation`.
