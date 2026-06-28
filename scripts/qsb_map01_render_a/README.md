# QSB-MAP01-RENDER-A

Mermaid to SVG/PNG render dry run for the existing QSB-MAP01-DWH-A Mermaid
mindmap.

This package renders:

- `runs/QSB-MAP01-DWH-A/qsb_map01.mmd`
- to `runs/QSB-MAP01-RENDER-A/qsb_map01.svg`
- and `runs/QSB-MAP01-RENDER-A/qsb_map01.png`

The original Mermaid source is not rewritten. This step does not mutate a
production DWH, Source-Hub, EXTRACT, META, MAP01, ARTIFACT01, or any existing
schema.

## Renderer

The wrapper requires Mermaid CLI on `PATH` as `mmdc`.

If `mmdc` is unavailable, the script fails with:

```text
Mermaid CLI not found. Install or provide mmdc, then rerun.
```

It does not create fake image files.

## Run

```bash
python scripts/qsb_map01_render_a/render_qsb_map01.py
```

The wrapper refuses to overwrite `qsb_map01.svg` or `qsb_map01.png` unless
called with:

```bash
python scripts/qsb_map01_render_a/render_qsb_map01.py --force
```

The `--force` mode deletes or replaces only files inside
`runs/QSB-MAP01-RENDER-A/` and never touches the input Mermaid source.

## Expected Outputs

- `runs/QSB-MAP01-RENDER-A/qsb_map01.svg`
- `runs/QSB-MAP01-RENDER-A/qsb_map01.png`
- `runs/QSB-MAP01-RENDER-A/qsb_map01_render_manifest.json`
- `runs/QSB-MAP01-RENDER-A/qsb_map01_render_validation_report.json`
- `runs/QSB-MAP01-RENDER-A/QSB-MAP01-RENDER-A_RUN_SUMMARY.md`

## Claim Boundary

Rendered QSB-MAP01 mindmap for internal orientation/review only; no physical
confirmation, no spacetime claim, no causality claim, no RELALG computation,
and no public publishing authorization.
