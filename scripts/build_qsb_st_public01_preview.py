#!/usr/bin/env python3
"""Build PREVIEW02 for the QSB-ST PUBLIC01 draft.

The builder reads the source markdown, rewrites image paths only in the
preview copy, copies local figure assets into the preview output directory,
and emits an HTML preview plus a PDF when a local renderer is available.
"""

from __future__ import annotations

import html
import re
import shutil
import subprocess
from pathlib import Path


SOURCE = Path("docs/QSB_ST_PUBLIC01_METHOD_GATE_RESEARCH_NOTE_DRAFT.md")
OUT_DIR = Path("runs/QSB-ST-PUBLIC01-PREVIEW02/layout_preview_open")
FIGURE_OUT_DIR = OUT_DIR / "figures"
HTML_OUT = OUT_DIR / "public01_preview.html"
PDF_OUT = OUT_DIR / "public01_preview.pdf"
READOUT_OUT = OUT_DIR / "preview_build_readout.md"

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

    def stash(pattern: str, repl):
        nonlocal text

        def inner(match: re.Match[str]) -> str:
            key = f"@@HTML_PLACEHOLDER_{len(placeholders)}@@"
            placeholders[key] = repl(match)
            return key

        text = re.sub(pattern, inner, text)

    stash(r"`([^`]+)`", lambda m: f"<code>{html.escape(m.group(1))}</code>")
    stash(
        r"!\[([^\]]*)\]\(([^\)]+)\)",
        lambda m: (
            f'<figure><img src="{html.escape(m.group(2), quote=True)}" '
            f'alt="{html.escape(m.group(1), quote=True)}">'
            f'<figcaption>{html.escape(m.group(1))}</figcaption></figure>'
        ),
    )
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


def table_to_html(lines: list[str]) -> str:
    rows = []
    for line in lines:
        cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
        if cells and all(re.fullmatch(r":?-{3,}:?", c) for c in cells):
            continue
        tag = "th" if not rows else "td"
        rows.append("<tr>" + "".join(f"<{tag}>{render_inline(cell)}</{tag}>" for cell in cells) + "</tr>")
    return "<table>" + "\n".join(rows) + "</table>"


def markdown_to_html(markdown_text: str) -> str:
    lines = markdown_text.splitlines()
    out: list[str] = []
    i = 0
    in_code = False
    code_lines: list[str] = []
    para: list[str] = []
    list_lines: list[str] = []

    def flush_para() -> None:
        nonlocal para
        if para:
            out.append("<p>" + render_inline(" ".join(para).strip()) + "</p>")
            para = []

    def flush_list() -> None:
        nonlocal list_lines
        if list_lines:
            out.append("<ul>" + "".join(f"<li>{render_inline(item)}</li>" for item in list_lines) + "</ul>")
            list_lines = []

    while i < len(lines):
        line = lines[i]

        if line.startswith("```"):
            if not in_code:
                flush_para()
                flush_list()
                in_code = True
                code_lines = []
            else:
                out.append("<pre><code>" + html.escape("\n".join(code_lines)) + "</code></pre>")
                in_code = False
            i += 1
            continue

        if in_code:
            code_lines.append(line)
            i += 1
            continue

        if not line.strip():
            flush_para()
            flush_list()
            i += 1
            continue

        if line.startswith("|") and "|" in line[1:]:
            flush_para()
            flush_list()
            table_lines = []
            while i < len(lines) and lines[i].startswith("|") and "|" in lines[i][1:]:
                table_lines.append(lines[i])
                i += 1
            out.append(table_to_html(table_lines))
            continue

        heading = re.match(r"^(#{1,6})\s+(.*)$", line)
        if heading:
            flush_para()
            flush_list()
            level = len(heading.group(1))
            out.append(f"<h{level}>{render_inline(heading.group(2))}</h{level}>")
            i += 1
            continue

        if line.startswith("- "):
            flush_para()
            list_lines.append(line[2:].strip())
            i += 1
            continue

        if line.startswith("!["):
            flush_para()
            flush_list()
            out.append(render_inline(line))
            i += 1
            continue

        para.append(line.strip())
        i += 1

    flush_para()
    flush_list()
    return "\n".join(out)


def build_html(body: str) -> str:
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>QSB-ST PUBLIC01 PREVIEW02</title>
<style>
:root {{
  --ink: #1f2c33;
  --muted: #637178;
  --line: #d8dedf;
  --paper: #fbfaf6;
  --card: #ffffff;
  --accent: #2e6f97;
}}
* {{ box-sizing: border-box; }}
body {{
  margin: 0;
  color: var(--ink);
  background: var(--paper);
  font-family: Georgia, 'Times New Roman', serif;
  line-height: 1.68;
}}
main {{
  max-width: 980px;
  margin: 0 auto;
  padding: 48px 28px 80px;
}}
.preview-note {{
  border-left: 5px solid var(--accent);
  background: #eef5f7;
  padding: 14px 18px;
  margin-bottom: 32px;
  font-family: system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
  color: var(--muted);
}}
h1, h2, h3, h4 {{
  font-family: system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
  line-height: 1.18;
  color: #172229;
}}
h1 {{ font-size: 2.55rem; margin: 0 0 0.4em; }}
h2 {{ font-size: 1.85rem; margin-top: 2.2em; border-top: 1px solid var(--line); padding-top: 0.9em; }}
h3 {{ font-size: 1.35rem; margin-top: 1.8em; }}
p {{ margin: 1em 0; }}
figure {{
  margin: 2.4em 0;
  padding: 18px;
  background: var(--card);
  border: 1px solid var(--line);
  box-shadow: 0 14px 34px rgba(31, 44, 51, 0.07);
}}
figure img {{ display: block; width: 100%; height: auto; }}
figcaption {{
  margin-top: 0.8em;
  color: var(--muted);
  font-size: 0.94rem;
  font-style: italic;
  font-family: system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
}}
code {{ background: #eef1f2; border-radius: 4px; padding: 0.1em 0.35em; }}
pre {{ background: #eef1f2; border-left: 4px solid var(--accent); padding: 16px; overflow-x: auto; }}
pre code {{ background: transparent; padding: 0; }}
table {{ width: 100%; border-collapse: collapse; margin: 1.5em 0; background: var(--card); }}
th, td {{ border: 1px solid var(--line); padding: 10px 12px; vertical-align: top; }}
th {{ background: #eef1f2; font-family: system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; }}
.footer {{
  margin-top: 48px;
  padding-top: 18px;
  border-top: 2px solid var(--line);
  color: var(--muted);
  font-family: system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
}}
@media print {{
  body {{ background: white; }}
  main {{ max-width: none; padding: 24px; }}
  figure {{ break-inside: avoid; box-shadow: none; }}
}}
</style>
</head>
<body>
<main>
<div class="preview-note">
<strong>PREVIEW02:</strong> Layout preview only. Image paths are rewritten locally for this preview; the source draft is unchanged.
</div>
{body}
<div class="footer">
Preview only. No public release, no upload, no final PDF, and no new scientific result.
</div>
</main>
</body>
</html>
"""


def try_pdf(html_path: Path, pdf_path: Path) -> tuple[bool, str]:
    candidates = [
        ("weasyprint", ["weasyprint", str(html_path), str(pdf_path)]),
        ("wkhtmltopdf", ["wkhtmltopdf", str(html_path), str(pdf_path)]),
    ]
    for name, cmd in candidates:
        if shutil.which(name):
            result = subprocess.run(cmd, cwd=Path.cwd(), text=True, capture_output=True)
            if result.returncode == 0 and pdf_path.exists():
                return True, f"PDF generated with {name}."
            if pdf_path.exists():
                pdf_path.unlink()
            return False, f"PDF generation with {name} failed: {result.stderr.strip() or result.stdout.strip()}"
    return False, "PDF generation skipped: no local weasyprint or wkhtmltopdf executable found."


def write_readout(referenced: list[str], copied: list[str], pdf_ok: bool, pdf_message: str) -> None:
    lines = [
        "# QSB-ST PUBLIC01 PREVIEW02 Build Readout",
        "",
        "## Source",
        f"- `{SOURCE}`",
        "",
        "## Output directory",
        f"- `{OUT_DIR}`",
        "",
        "## Path handling",
        "- Rewrote preview-only Markdown image paths from `../figures/<filename>` to `figures/<filename>`.",
        "- Source draft was not modified.",
        "",
        "## Figures copied",
    ]
    lines.extend(f"- `{path}`" for path in copied)
    lines.extend([
        "",
        "## Referenced figure filenames",
    ])
    lines.extend(f"- `{name}`" for name in referenced)
    lines.extend([
        "",
        "## Outputs",
        f"- HTML: `{HTML_OUT}`",
        f"- PDF: `{PDF_OUT}`" if pdf_ok else "- PDF: not created",
        "",
        "## PDF status",
        f"- {pdf_message}",
        "",
        "## Claim Boundary",
        "- Preview/review step only.",
        "- No public release.",
        "- No upload.",
        "- No final PDF.",
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
    preview_markdown, referenced = rewrite_image_paths(markdown)
    copied = copy_figures(referenced)
    body = markdown_to_html(preview_markdown)
    HTML_OUT.write_text(build_html(body), encoding="utf-8")
    pdf_ok, pdf_message = try_pdf(HTML_OUT, PDF_OUT)
    write_readout(referenced, copied, pdf_ok, pdf_message)
    print(f"HTML preview: {HTML_OUT}")
    print(pdf_message)
    print(f"Readout: {READOUT_OUT}")


if __name__ == "__main__":
    main()
