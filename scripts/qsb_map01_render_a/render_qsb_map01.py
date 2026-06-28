#!/usr/bin/env python3
"""Render the QSB-MAP01 Mermaid mindmap to SVG and PNG with Mermaid CLI."""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT_PATH = Path("scripts/qsb_map01_render_a/render_qsb_map01.py")
RUN_ID = "QSB-MAP01-RENDER-A"
INPUT_MMD = REPO_ROOT / "runs/QSB-MAP01-DWH-A/qsb_map01.mmd"
OPTIONAL_MD = REPO_ROOT / "runs/QSB-MAP01-DWH-A/qsb_map01.md"
OUTPUT_DIR = REPO_ROOT / "runs/QSB-MAP01-RENDER-A"
OUTPUT_SVG = OUTPUT_DIR / "qsb_map01.svg"
OUTPUT_PNG = OUTPUT_DIR / "qsb_map01.png"
MANIFEST_PATH = OUTPUT_DIR / "qsb_map01_render_manifest.json"
VALIDATION_PATH = OUTPUT_DIR / "qsb_map01_render_validation_report.json"
SUMMARY_PATH = OUTPUT_DIR / "QSB-MAP01-RENDER-A_RUN_SUMMARY.md"
CLAIM_BOUNDARY_SUMMARY = (
    "Rendered QSB-MAP01 mindmap for internal orientation/review only; "
    "no physical confirmation, no spacetime claim, no causality claim."
)
FORBIDDEN_CONFIRMATION_WORDING = [
    "proves QSB",
    "proves spacetime",
    "establishes causality",
    "confirms emergent spacetime",
    "validates physical theory",
    "demonstrates new gravity",
]


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def rel(path: Path) -> str:
    return str(path.relative_to(REPO_ROOT))


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def output_paths() -> list[Path]:
    return [OUTPUT_SVG, OUTPUT_PNG, MANIFEST_PATH, VALIDATION_PATH, SUMMARY_PATH]


def existing_render_outputs() -> list[Path]:
    return [path for path in [OUTPUT_SVG, OUTPUT_PNG] if path.exists()]


def refuse_existing_outputs() -> None:
    existing = existing_render_outputs()
    if existing:
        rendered = ", ".join(rel(path) for path in existing)
        raise FileExistsError(f"Refusing to overwrite existing render output(s): {rendered}. Rerun with --force to replace files inside {rel(OUTPUT_DIR)} only.")


def prepare_output_dir(force: bool) -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    existing_render_outputs = [path for path in [OUTPUT_SVG, OUTPUT_PNG] if path.exists()]
    if existing_render_outputs and not force:
        rendered = ", ".join(rel(path) for path in existing_render_outputs)
        raise FileExistsError(f"Refusing to overwrite existing render output(s): {rendered}. Rerun with --force to replace files inside {rel(OUTPUT_DIR)} only.")
    if force:
        for path in output_paths():
            if path.exists() and path.is_file():
                path.unlink()


def run_mmdc(mmdc_path: str, output_path: Path, extra_args: list[str]) -> None:
    cmd = [
        mmdc_path,
        "-i",
        rel(INPUT_MMD),
        "-o",
        rel(output_path),
        "-b",
        "white",
        *extra_args,
    ]
    subprocess.run(cmd, cwd=REPO_ROOT, check=True)


def validation_row(rule_id: str, severity: str, status: str, message: str, timestamp: str) -> dict[str, str]:
    return {
        "validation_id": f"QSB-MAP01-RENDER-A-VAL-{rule_id}",
        "rule_id": rule_id,
        "severity": severity,
        "status": status,
        "message": message,
        "checked_at": timestamp,
    }


def text_has_forbidden_claim(text: str) -> bool:
    lowered = text.lower()
    return any(phrase.lower() in lowered for phrase in FORBIDDEN_CONFIRMATION_WORDING)


def build_validation(
    timestamp: str,
    mmdc_path: str,
    input_mtime_before: int,
    input_mtime_after: int,
    manifest_preview: dict[str, object],
    summary_text: str,
) -> list[dict[str, str]]:
    svg_hash = str(manifest_preview.get("svg_hash") or "")
    png_hash = str(manifest_preview.get("png_hash") or "")
    rows = [
        validation_row("V01", "error", "pass" if INPUT_MMD.exists() else "fail", "Input Mermaid file exists.", timestamp),
        validation_row("V02", "error", "pass" if mmdc_path else "fail", "Mermaid CLI is available.", timestamp),
        validation_row("V03", "error", "pass" if OUTPUT_SVG.exists() else "fail", "SVG output exists.", timestamp),
        validation_row("V04", "error", "pass" if OUTPUT_PNG.exists() else "fail", "PNG output exists.", timestamp),
        validation_row("V05", "error", "pass" if OUTPUT_SVG.exists() and OUTPUT_SVG.stat().st_size > 0 else "fail", "SVG output has nonzero size.", timestamp),
        validation_row("V06", "error", "pass" if OUTPUT_PNG.exists() and OUTPUT_PNG.stat().st_size > 0 else "fail", "PNG output has nonzero size.", timestamp),
        validation_row("V07", "error", "pass" if len(svg_hash) == 64 else "fail", "SVG hash computed.", timestamp),
        validation_row("V08", "error", "pass" if len(png_hash) == 64 else "fail", "PNG hash computed.", timestamp),
        validation_row("V09", "error", "pass" if input_mtime_before == input_mtime_after else "fail", "No original input file was modified.", timestamp),
        validation_row(
            "V10",
            "error",
            "fail" if text_has_forbidden_claim(json.dumps(manifest_preview, ensure_ascii=False)) or text_has_forbidden_claim(summary_text) else "pass",
            "No forbidden confirmation claim appears in generated run summary or manifest.",
            timestamp,
        ),
    ]
    return rows


def validation_status(rows: list[dict[str, str]]) -> str:
    if any(row["status"] == "fail" for row in rows):
        return "fail"
    if any(row["status"] == "warning" for row in rows):
        return "warning"
    return "pass"


def write_outputs(mmdc_path: str, timestamp: str, input_mtime_before: int) -> None:
    svg_hash = sha256_file(OUTPUT_SVG)
    png_hash = sha256_file(OUTPUT_PNG)
    manifest = {
        "run_id": RUN_ID,
        "script_path": str(SCRIPT_PATH),
        "input_mmd": rel(INPUT_MMD),
        "optional_input_md": rel(OPTIONAL_MD) if OPTIONAL_MD.exists() else None,
        "output_svg": rel(OUTPUT_SVG),
        "output_png": rel(OUTPUT_PNG),
        "renderer": "mmdc",
        "renderer_path": mmdc_path,
        "timestamp": timestamp,
        "svg_hash": svg_hash,
        "png_hash": png_hash,
        "svg_size_bytes": OUTPUT_SVG.stat().st_size,
        "png_size_bytes": OUTPUT_PNG.stat().st_size,
        "claim_boundary_summary": CLAIM_BOUNDARY_SUMMARY,
    }
    summary_text = f"""# QSB-MAP01-RENDER-A Run Summary

Generated at: {timestamp}

## Purpose

Render the existing QSB-MAP01 Mermaid mindmap into SVG and PNG artifacts for internal orientation and review.

## Input File

- {rel(INPUT_MMD)}

## Outputs Created

- {rel(OUTPUT_SVG)}
- {rel(OUTPUT_PNG)}
- {rel(MANIFEST_PATH)}
- {rel(VALIDATION_PATH)}
- {rel(SUMMARY_PATH)}

## Hashes

- SVG SHA256: {svg_hash}
- PNG SHA256: {png_hash}

## Renderer Used

- renderer: mmdc
- renderer_path: {mmdc_path}

## Sandbox-Only Statement

This is a rendering dry run for internal visual inspection.

## No Production Mutation Statement

No production DWH, Source-Hub, EXTRACT, META, MAP01, ARTIFACT01, or existing schema was mutated.

## No Physics Claim Statement

The rendered images are not evidence for QSB and are not physics validation.

## Next Allowed Step

Register qsb_map01.svg and qsb_map01.png via QSB-ARTIFACT01-DWH-C or a focused artifact registration update.
"""
    input_mtime_after = INPUT_MMD.stat().st_mtime_ns
    rows = build_validation(timestamp, mmdc_path, input_mtime_before, input_mtime_after, manifest, summary_text)
    validation = {
        "run_id": RUN_ID,
        "timestamp": timestamp,
        "validation_status": validation_status(rows),
        "results": rows,
        "claim_boundary_summary": CLAIM_BOUNDARY_SUMMARY,
    }
    MANIFEST_PATH.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    VALIDATION_PATH.write_text(json.dumps(validation, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    SUMMARY_PATH.write_text(
        summary_text.replace(
            "## Sandbox-Only Statement",
            f"## Validation Summary\n\nStatus: {validation_status(rows)}\n\n"
            + "\n".join(f"- {row['rule_id']}: {row['status']} ({row['severity']}) - {row['message']}" for row in rows)
            + "\n\n## Sandbox-Only Statement",
        ),
        encoding="utf-8",
    )


def render(force: bool) -> None:
    if not INPUT_MMD.exists():
        raise FileNotFoundError(f"Required input Mermaid file is missing: {rel(INPUT_MMD)}")
    if not force:
        refuse_existing_outputs()
    mmdc_path = shutil.which("mmdc")
    if not mmdc_path:
        raise RuntimeError("Mermaid CLI not found. Install or provide mmdc, then rerun.")
    prepare_output_dir(force)
    timestamp = utc_now()
    input_mtime_before = INPUT_MMD.stat().st_mtime_ns
    run_mmdc(mmdc_path, OUTPUT_SVG, [])
    run_mmdc(mmdc_path, OUTPUT_PNG, ["-s", "2"])
    write_outputs(mmdc_path, timestamp, input_mtime_before)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--force", action="store_true", help=f"Replace files inside {rel(OUTPUT_DIR)} only.")
    args = parser.parse_args()
    try:
        render(force=args.force)
    except (FileNotFoundError, FileExistsError, RuntimeError, subprocess.CalledProcessError) as exc:
        print(str(exc), file=sys.stderr)
        raise SystemExit(1) from None


if __name__ == "__main__":
    main()
