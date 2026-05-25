#!/usr/bin/env python3
"""Build release-style HTML/PDF for QSB-ST PUBLIC01.

This builder creates a release layout from a temporary render copy. It does not
modify the source draft and does not change scientific content.
"""

from __future__ import annotations

import html
import re
import shutil
import subprocess
from pathlib import Path


SOURCE = Path("docs/QSB_ST_PUBLIC01_METHOD_GATE_RESEARCH_NOTE_DRAFT.md")
OUT_DIR = Path("runs/QSB-ST-PUBLIC01-PDF01/release_pdf_open")
FIGURE_OUT_DIR = OUT_DIR / "figures"
HTML_OUT = OUT_DIR / "public01_release.html"
PDF_OUT = OUT_DIR / "QSB_ST_PUBLIC01_Method_Gate_Route_2026-05-25.pdf"
READOUT_OUT = OUT_DIR / "pdf_build_readout.md"

IMAGE_PATTERN = re.compile(r"!\[([^\]]*)\]\((\.\./figures/([^\)]+))\)")


def rewrite_image_paths(markdown_text: str) -> tuple[str, list[str]]:
    referenced: list[str] = []

    def replace(match: re.Match[str]) -> str:
        alt = match.group(1)
        filename = match.group(3)
        referenced.append(filename)
        return f"![{alt}](figures/{filename})"

    return IMAGE_PATTERN.sub(replace, markdown_text), referenced


def copy_figures(filenames: list[str]) -> list[str]:
    copied: list[str] = []
    FIGURE_OUT_DIR.mkdir(parents=True, exist_ok=True)
    for filename in filenames:
        src = Path("figures") / filename
        dst = FIGURE_OUT_DIR / filename
        if not src.exists():
            raise FileNotFoundError(f"Referenced figure missing: {src}")
        shutil.copy2(src, dst)
        copied.append(str(dst))
    return copied


def render_inline(text: str) -> str:
    placeholders: dict[str, str] = {}

    def stash(pattern: str, repl) -> None:
        nonlocal text

        def inner(match: re.Match[str]) -> str:
            key = f"@@HTML_PLACEHOLDER_{len(placeholders)}@@"
            placeholders[key] = repl(match)
            return key

        text = re.sub(pattern, inner, text)

    stash(r"`([^`]+)`", lambda m: f"<code>{html.escape(m.group(1))}</code>")
    stash(
        r"\[([^\]]+)\]\(([^\)]+)\)",
        lambda m: f'<a href="{html.escape(m.group(2), quote=True)}">{html.escape(m.group(1))}</a>',
    )

    escaped = html.escape(text)
    escaped = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", escaped)
    escaped = re.sub(r"\*([^*]+)\*", r"<em>\1</em>", escaped)

    for key, value in placeholders.items():
        escaped = escaped.replace(html.escape(key), value)
    return escaped


def render_image(line: str) -> str:
    match = re.match(r"!\[([^\]]*)\]\(([^\)]+)\)", line.strip())
    if not match:
        raise ValueError(f"not an image line: {line}")
    alt = html.escape(match.group(1), quote=True)
    src = html.escape(match.group(2), quote=True)
    return f'<img src="{src}" alt="{alt}">'


def table_to_source_list(lines: list[str]) -> str:
    table_rows: list[list[str]] = []
    for line in lines:
        cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
        if cells and all(re.fullmatch(r":?-{3,}:?", c) for c in cells):
            continue
        table_rows.append(cells)

    if not table_rows:
        return ""

    header = table_rows[0]
    rows = table_rows[1:]
    title_left = header[0] if header else "Item"
    title_right = header[1] if len(header) > 1 else "Detail"
    parts = [f'<div class="source-list" role="table" aria-label="{html.escape(title_left)} / {html.escape(title_right)}">']
    for cells in rows:
        left = render_inline(cells[0]) if cells else ""
        right = render_inline(cells[1]) if len(cells) > 1 else ""
        parts.append('<div class="source-row">')
        parts.append(f'<div class="source-key">{left}</div>')
        parts.append(f'<div class="source-value">{right}</div>')
        parts.append("</div>")
    parts.append("</div>")
    return "\n".join(parts)


def render_paragraph(lines: list[str]) -> str:
    return "<p>" + render_inline(" ".join(line.strip() for line in lines).strip()) + "</p>"


def markdown_to_html(markdown_text: str) -> str:
    lines = markdown_text.splitlines()
    out: list[str] = []
    i = 0

    def flush_list(items: list[str]) -> None:
        if items:
            out.append("<ul>" + "".join(f"<li>{render_inline(item)}</li>" for item in items) + "</ul>")

    while i < len(lines):
        line = lines[i]

        if not line.strip():
            i += 1
            continue

        if line.startswith("```"):
            code_lines: list[str] = []
            i += 1
            while i < len(lines) and not lines[i].startswith("```"):
                code_lines.append(lines[i])
                i += 1
            if i < len(lines):
                i += 1
            out.append("<pre><code>" + html.escape("\n".join(code_lines)) + "</code></pre>")
            continue

        figure_heading = re.match(r"^###\s+(Figure\s+\d+\..*)$", line)
        if figure_heading:
            block: list[str] = [f"<h3>{render_inline(figure_heading.group(1))}</h3>"]
            i += 1
            while i < len(lines) and not re.match(r"^#{2,3}\s+", lines[i]):
                current = lines[i]
                if not current.strip():
                    i += 1
                    continue
                if current.startswith("!["):
                    block.append('<figure class="release-figure">' + render_image(current) + "</figure>")
                    i += 1
                    continue
                if current.startswith("- "):
                    items: list[str] = []
                    while i < len(lines) and lines[i].startswith("- "):
                        items.append(lines[i][2:].strip())
                        i += 1
                    block.append("<ul>" + "".join(f"<li>{render_inline(item)}</li>" for item in items) + "</ul>")
                    continue
                para_lines = [current]
                i += 1
                while i < len(lines) and lines[i].strip() and not lines[i].startswith("![") and not lines[i].startswith("- ") and not re.match(r"^#{2,3}\s+", lines[i]):
                    para_lines.append(lines[i])
                    i += 1
                block.append(render_paragraph(para_lines))
            out.append('<section class="figure-block">' + "\n".join(block) + "</section>")
            continue

        if line.startswith("!["):
            block = ['<section class="opening-figure">', '<figure class="release-figure">', render_image(line), "</figure>"]
            i += 1
            if i < len(lines) and lines[i].strip().startswith("*"):
                block.append(render_paragraph([lines[i]]))
                i += 1
            block.append("</section>")
            out.append("\n".join(block))
            continue

        if line.startswith("|") and "|" in line[1:]:
            table_lines: list[str] = []
            while i < len(lines) and lines[i].startswith("|") and "|" in lines[i][1:]:
                table_lines.append(lines[i])
                i += 1
            out.append(table_to_source_list(table_lines))
            continue

        heading = re.match(r"^(#{1,6})\s+(.*)$", line)
        if heading:
            level = len(heading.group(1))
            out.append(f"<h{level}>{render_inline(heading.group(2))}</h{level}>")
            i += 1
            continue

        if line.startswith("- "):
            items: list[str] = []
            while i < len(lines) and lines[i].startswith("- "):
                items.append(lines[i][2:].strip())
                i += 1
            flush_list(items)
            continue

        para_lines = [line]
        i += 1
        while i < len(lines) and lines[i].strip() and not lines[i].startswith("```") and not lines[i].startswith("|") and not lines[i].startswith("- ") and not lines[i].startswith("![") and not re.match(r"^#{1,6}\s+", lines[i]):
            para_lines.append(lines[i])
            i += 1
        out.append(render_paragraph(para_lines))

    return "\n".join(out)


def build_html(body: str) -> str:
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>QSB-ST PUBLIC01 Method-Gate Route</title>
<style>
@page {{
  size: A4;
  margin: 18mm;
}}
* {{ box-sizing: border-box; }}
body {{
  margin: 0;
  color: #1f2b32;
  background: #ffffff;
  font-family: Georgia, 'Times New Roman', serif;
  font-size: 11.2pt;
  line-height: 1.56;
}}
main {{
  max-width: 176mm;
  margin: 0 auto;
}}
h1, h2, h3, h4 {{
  font-family: Arial, Helvetica, sans-serif;
  color: #15242c;
  line-height: 1.18;
  page-break-after: avoid;
  break-after: avoid;
}}
h1 {{
  font-size: 23pt;
  margin: 0 0 8mm;
}}
h2 {{
  font-size: 16pt;
  margin: 10mm 0 3.8mm;
  padding-top: 4mm;
  border-top: 0.6pt solid #d7dee0;
}}
h3 {{
  font-size: 12.8pt;
  margin: 5mm 0 3mm;
}}
p {{ margin: 0 0 3.6mm; }}
ul {{ margin: 0 0 4mm 6mm; padding-left: 5mm; }}
li {{ margin: 0 0 1.4mm; }}
a {{ color: #245f86; text-decoration: none; }}
code {{
  font-family: 'Courier New', monospace;
  font-size: 9.4pt;
  background: #eef2f3;
  padding: 0.2mm 0.8mm;
  border-radius: 1mm;
}}
pre {{
  page-break-inside: avoid;
  break-inside: avoid;
  background: #eef2f3;
  border-left: 2.4pt solid #2d6f95;
  padding: 3mm;
  white-space: pre-wrap;
  font-size: 9.2pt;
  line-height: 1.34;
}}
.opening-figure {{
  page-break-inside: avoid;
  break-inside: avoid;
  margin: 5mm 0 9mm;
}}
.figure-block {{
  page-break-inside: avoid;
  break-inside: avoid;
  margin: 7mm 0 8mm;
  padding-top: 1mm;
}}
.figure-block + .figure-block {{
  page-break-before: auto;
}}
.release-figure {{
  margin: 0 0 3.5mm;
  padding: 3.5mm;
  border: 0.6pt solid #d7dee0;
  background: #fafaf7;
  page-break-inside: avoid;
  break-inside: avoid;
}}
.release-figure img {{
  display: block;
  width: 100%;
  max-height: 116mm;
  object-fit: contain;
}}
.opening-figure .release-figure img {{
  max-height: 105mm;
}}
.source-list {{
  display: table;
  width: 100%;
  table-layout: fixed;
  margin: 4mm 0 6mm;
  border-collapse: collapse;
  font-size: 8.7pt;
  page-break-inside: auto;
}}
.source-row {{
  display: table-row;
  page-break-inside: avoid;
  break-inside: avoid;
}}
.source-key, .source-value {{
  display: table-cell;
  border: 0.5pt solid #d7dee0;
  padding: 1.8mm 2mm;
  vertical-align: top;
  overflow-wrap: anywhere;
  word-break: break-word;
}}
.source-key {{
  width: 31%;
  font-family: Arial, Helvetica, sans-serif;
  font-weight: 700;
  background: #eef4f6;
}}
.source-value {{
  width: 69%;
}}
#document-apparatus, #references, #figure-and-ai-transparency, #next-steps {{
  page-break-inside: avoid;
  break-inside: avoid;
}}
</style>
</head>
<body>
<main>
{body}
</main>
</body>
</html>
"""


def run_wkhtmltopdf() -> tuple[bool, str, list[str]]:
    wkhtmltopdf = shutil.which("wkhtmltopdf")
    if not wkhtmltopdf:
        return False, "wkhtmltopdf not available.", []
    cmd = [
        wkhtmltopdf,
        "--enable-local-file-access",
        "--page-size",
        "A4",
        "--margin-top",
        "18mm",
        "--margin-bottom",
        "18mm",
        "--margin-left",
        "18mm",
        "--margin-right",
        "18mm",
        "--quiet",
        str(HTML_OUT),
        str(PDF_OUT),
    ]
    result = subprocess.run(cmd, text=True, capture_output=True)
    if result.returncode == 0 and PDF_OUT.exists():
        return True, "PDF generated with wkhtmltopdf.", cmd
    if PDF_OUT.exists():
        PDF_OUT.unlink()
    detail = result.stderr.strip() or result.stdout.strip() or f"exit code {result.returncode}"
    return False, f"wkhtmltopdf failed: {detail}", cmd


def write_readout(referenced: list[str], copied: list[str], pdf_ok: bool, pdf_message: str, cmd: list[str]) -> None:
    lines = [
        "# QSB-ST PUBLIC01 PDF01 Build Readout",
        "",
        "## Source",
        f"- `{SOURCE}`",
        "",
        "## Outputs",
        f"- HTML: `{HTML_OUT}`",
        f"- PDF: `{PDF_OUT}`" if pdf_ok else "- PDF: not created",
        f"- Figures directory: `{FIGURE_OUT_DIR}`",
        "",
        "## Figure path handling",
        "- Rewrote preview-independent release paths from `../figures/<filename>` to `figures/<filename>`.",
        "- Copied referenced local figure assets into the release output directory.",
        "",
        "## Figures copied",
    ]
    lines.extend(f"- `{path}`" for path in copied)
    lines.extend([
        "",
        "## Referenced figures",
    ])
    lines.extend(f"- `{name}`" for name in referenced)
    lines.extend([
        "",
        "## PDF renderer",
        f"- {pdf_message}",
    ])
    if cmd:
        lines.append("- Command: `" + " ".join(cmd) + "`")
    lines.extend([
        "",
        "## Release transformations",
        "- No preview banner included.",
        "- Image alt text is kept as image `alt` metadata, not duplicated as visible caption text.",
        "- Figure blocks are wrapped to reduce heading/image/caption separation.",
        "- Repository and commit anchor tables are rendered as compact two-column source lists.",
        "",
        "## Claim Boundary",
        "- PDF layout/build step only.",
        "- No public release.",
        "- No upload.",
        "- No new scientific result.",
        "- No Bridge confirmation.",
        "- No diagnostic specificity claim.",
        "- No physical validation.",
        "- No real degeneracy measurement.",
    ])
    READOUT_OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    markdown = SOURCE.read_text(encoding="utf-8")
    release_markdown, referenced = rewrite_image_paths(markdown)
    copied = copy_figures(referenced)
    body = markdown_to_html(release_markdown)
    HTML_OUT.write_text(build_html(body), encoding="utf-8")
    pdf_ok, pdf_message, cmd = run_wkhtmltopdf()
    write_readout(referenced, copied, pdf_ok, pdf_message, cmd)
    print(f"release html: {HTML_OUT}")
    print(pdf_message)
    print(f"readout: {READOUT_OUT}")


if __name__ == "__main__":
    main()
