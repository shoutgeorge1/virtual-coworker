#!/usr/bin/env python3
"""Concatenate the ChatGPT paste pack. Disk only. No APIs. No keyword dump."""

from __future__ import annotations

import csv
import html
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]

BANNER = (
    "THIS IS THE ONE FILE. Select all, copy, paste into ChatGPT. "
    "Read as source of truth. Do not summarize unless asked. "
    "Do not parody. Do not recommend Broad/PMax/Max Conv."
)
CENSUS_WARNING = (
    "Sections below are the earlier census; prefer the addendum where they conflict."
)

NEW_PASS = [
    ("FINAL-EVIDENCE-ADDENDUM-2026-08-13.md", "Final evidence addendum"),
    ("ATTRIBUTION-NUMBERS-2026-08-13.csv", "Attribution numbers"),
    ("CHECKLIST-PATCH-2026-08-13.md", "Checklist patch"),
    ("TEAM-UPDATE-DRAFT-2026-08-13.md", "Team update draft"),
    ("API-CALL-LOG-2026-08-13.md", "API call log"),
]


def csv_to_markdown(path: Path) -> str:
    with path.open(newline="", encoding="utf-8") as f:
        rows = list(csv.reader(f))
    if not rows:
        return "_Empty CSV._"
    header, body = rows[0], rows[1:]
    lines = [
        "| " + " | ".join(header) + " |",
        "| " + " | ".join("---" for _ in header) + " |",
    ]
    for row in body:
        padded = row + [""] * (len(header) - len(row))
        lines.append("| " + " | ".join(padded[: len(header)]) + " |")
    return "\n".join(lines)


def inline(text: str) -> str:
    text = html.escape(text)
    text = re.sub(r"`([^`]+)`", r"<code>\1</code>", text)
    text = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", text)
    text = re.sub(r"(?<!\*)\*([^*]+)\*(?!\*)", r"<em>\1</em>", text)
    text = re.sub(
        r"\[([^\]]+)\]\(([^)]+)\)",
        r'<a href="\2">\1</a>',
        text,
    )
    return text


def md_to_html(md: str) -> str:
    lines = md.replace("\r\n", "\n").split("\n")
    out: list[str] = []
    i = 0
    in_code = False
    code_buf: list[str] = []
    in_ul = False
    in_ol = False
    in_table = False
    table_rows: list[list[str]] = []

    def close_lists() -> None:
        nonlocal in_ul, in_ol
        if in_ul:
            out.append("</ul>")
            in_ul = False
        if in_ol:
            out.append("</ol>")
            in_ol = False

    def flush_table() -> None:
        nonlocal in_table, table_rows
        if not table_rows:
            in_table = False
            return
        out.append("<table>")
        for ti, row in enumerate(table_rows):
            if ti == 1 and all(re.fullmatch(r":?-{3,}:?", c.strip()) for c in row):
                continue
            tag = "th" if ti == 0 else "td"
            wrap = "thead" if ti == 0 else "tbody"
            if ti == 0:
                out.append("<thead>")
            elif ti == 2 or (ti == 1 and wrap == "tbody"):
                if "<tbody>" not in "".join(out[-3:]):
                    out.append("<tbody>")
            cells = "".join(f"<{tag}>{inline(c.strip())}</{tag}>" for c in row)
            out.append(f"<tr>{cells}</tr>")
            if ti == 0:
                out.append("</thead>")
        out.append("</tbody>")
        out.append("</table>")
        table_rows = []
        in_table = False

    para: list[str] = []

    def flush_para() -> None:
        nonlocal para
        if para:
            out.append("<p>" + inline(" ".join(para)) + "</p>")
            para = []

    while i < len(lines):
        line = lines[i]
        if in_code:
            if line.strip().startswith("```"):
                out.append("<pre><code>" + html.escape("\n".join(code_buf)) + "</code></pre>")
                code_buf = []
                in_code = False
            else:
                code_buf.append(line)
            i += 1
            continue
        if line.strip().startswith("```"):
            flush_para()
            close_lists()
            flush_table()
            in_code = True
            i += 1
            continue
        if re.match(r"^\|.+\|$", line.strip()):
            flush_para()
            close_lists()
            in_table = True
            cells = [c.strip() for c in line.strip().strip("|").split("|")]
            table_rows.append(cells)
            i += 1
            continue
        if in_table:
            flush_table()
        m = re.match(r"^(#{1,6})\s+(.*)$", line)
        if m:
            flush_para()
            close_lists()
            level = len(m.group(1))
            out.append(f"<h{level}>{inline(m.group(2))}</h{level}>")
            i += 1
            continue
        if re.match(r"^---+\s*$", line.strip()):
            flush_para()
            close_lists()
            out.append("<hr>")
            i += 1
            continue
        ul = re.match(r"^[-*]\s+(.*)$", line)
        if ul:
            flush_para()
            if in_ol:
                out.append("</ol>")
                in_ol = False
            if not in_ul:
                out.append("<ul>")
                in_ul = True
            out.append(f"<li>{inline(ul.group(1))}</li>")
            i += 1
            continue
        ol = re.match(r"^\d+\.\s+(.*)$", line)
        if ol:
            flush_para()
            if in_ul:
                out.append("</ul>")
                in_ul = False
            if not in_ol:
                out.append("<ol>")
                in_ol = True
            out.append(f"<li>{inline(ol.group(1))}</li>")
            i += 1
            continue
        if not line.strip():
            flush_para()
            close_lists()
            i += 1
            continue
        close_lists()
        para.append(line.strip())
        i += 1
    flush_para()
    close_lists()
    flush_table()
    if in_code:
        out.append("<pre><code>" + html.escape("\n".join(code_buf)) + "</code></pre>")
    return "\n".join(out)


def source_block(title: str, rel: str, body: str) -> str:
    return (
        f"# SOURCE: {title}\n\n"
        f"*Original file: `{rel}` — full text below.*\n\n"
        f"{body.rstrip()}\n"
    )


def build_markdown() -> str:
    parts: list[str] = []
    parts.append("# Attribution recovery — EVERYTHING — 13 August 2026\n")
    parts.append("## Instruction for ChatGPT\n")
    parts.append(
        "Read this entire document as source of truth. Do not summarize unless George asks. "
        "Do not parody. Do not imitate George. Do not invent Broad/PMax/Max Conv. "
        "Facts vs interpretation stay labeled.\n"
    )
    parts.append(
        "This file is the **one** paste. New evidence pass first. "
        "HTML twin: `everything.html`.\n"
    )
    parts.append("**Decision gate:** `NOT READY FOR CRM WRITES OR OFFLINE IMPORT`\n")
    parts.append(
        "Read-only forensic pack. Nothing was written in Zoho. Nothing was sent. "
        "Google Ads was not mutated. No Editor import/post. CRM writes stayed off. "
        "No keyword / ad group / campaign performance dump.\n"
    )
    parts.append("## Contents\n")
    parts.append("**New pass (correction — read first)**\n")
    parts.append("1. Final evidence addendum (`FINAL-EVIDENCE-ADDENDUM-2026-08-13.md`)")
    parts.append("2. Attribution numbers (`ATTRIBUTION-NUMBERS-2026-08-13.csv`)")
    parts.append("3. Checklist patch (`CHECKLIST-PATCH-2026-08-13.md`)")
    parts.append("4. Team update draft (`TEAM-UPDATE-DRAFT-2026-08-13.md`) — do not send")
    parts.append("5. API call log (`API-CALL-LOG-2026-08-13.md`)")
    parts.append("")
    parts.append("**Earlier census (addendum wins where they conflict)**\n")
    parts.append("6. README through ChatGPT audio debrief, plus Zoho appendices\n")
    parts.append("---\n")

    for fname, title in NEW_PASS:
        path = HERE / fname
        rel = f"ads-launch/ATTRIBUTION-RECOVERY-2026-08-13/{fname}"
        if fname.endswith(".csv"):
            body = csv_to_markdown(path)
            parts.append(source_block(title, rel, body))
        else:
            parts.append(source_block(title, rel, path.read_text(encoding="utf-8")))
        parts.append("\n---\n")

    parts.append(f"**{CENSUS_WARNING}**\n")
    parts.append("---\n")

    old = (HERE / "EVERYTHING.md").read_text(encoding="utf-8")
    marker = "# SOURCE: README — pack index"
    idx = old.find(marker)
    if idx == -1:
        raise SystemExit("Could not find earlier census marker in EVERYTHING.md")
    parts.append(old[idx:].rstrip())
    parts.append("")
    return "\n".join(parts)


CSS = """
  :root {
    --bg: #f6f1e8;
    --ink: #1c1917;
    --muted: #57534e;
    --banner: #1c1917;
    --banner-ink: #faf6ee;
    --rule: #d6d3d1;
    --code-bg: #ece7dc;
    --th: #e7e0d4;
    --accent: #9a3412;
    --warn: #7c2d12;
    --warn-bg: #ffedd5;
  }
  * { box-sizing: border-box; }
  html, body {
    margin: 0;
    padding: 0;
    background: var(--bg);
    color: var(--ink);
    font: 20px/1.55 "Iowan Old Style", "Palatino Linotype", Palatino, Georgia, serif;
  }
  .banner {
    position: sticky;
    top: 0;
    z-index: 2;
    background: var(--banner);
    color: var(--banner-ink);
    padding: 14px 20px;
    font: 600 16px/1.35 -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
    letter-spacing: 0.02em;
    text-align: center;
  }
  .banner small {
    display: block;
    margin-top: 4px;
    font-weight: 400;
    opacity: 0.8;
  }
  article {
    max-width: 720px;
    margin: 0 auto;
    padding: 36px 22px 80px;
  }
  h1 { font-size: 1.7rem; line-height: 1.25; margin: 2.2rem 0 0.7rem; }
  h2 { font-size: 1.35rem; line-height: 1.3; margin: 2rem 0 0.6rem; }
  h3 { font-size: 1.15rem; margin: 1.6rem 0 0.5rem; }
  h4, h5, h6 { font-size: 1.05rem; margin: 1.4rem 0 0.4rem; }
  p { margin: 0 0 1rem; }
  ul, ol { margin: 0 0 1rem 1.3rem; padding: 0; }
  li { margin: 0.25rem 0; }
  hr { border: 0; border-top: 1px solid var(--rule); margin: 2.2rem 0; }
  code {
    font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace;
    font-size: 0.82em;
    background: var(--code-bg);
    padding: 0.08em 0.28em;
    border-radius: 3px;
  }
  pre {
    background: var(--code-bg);
    padding: 14px 16px;
    overflow-x: auto;
    border-radius: 6px;
    font-size: 0.78rem;
    line-height: 1.45;
    margin: 0 0 1.2rem;
  }
  pre code { background: none; padding: 0; font-size: inherit; }
  table {
    border-collapse: collapse;
    width: 100%;
    margin: 0 0 1.2rem;
    font-size: 0.88rem;
    line-height: 1.4;
  }
  th, td {
    border: 1px solid var(--rule);
    padding: 6px 8px;
    text-align: left;
    vertical-align: top;
  }
  th { background: var(--th); }
  a { color: var(--accent); }
  .gate {
    border: 2px solid var(--ink);
    padding: 10px 14px;
    font-weight: 700;
    margin: 1rem 0 1.4rem;
  }
  .warn {
    background: var(--warn-bg);
    color: var(--warn);
    border: 2px solid var(--warn);
    padding: 12px 14px;
    font-weight: 700;
    margin: 1.6rem 0;
  }
"""


def wrap_html(body_html: str, words: int, pages: float) -> str:
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Attribution recovery — EVERYTHING — 13 August 2026</title>
<style>{CSS}
</style>
</head>
<body>
<div class="banner">{html.escape(BANNER)}<small>~{words:,} words · ~{pages:.0f} pages · new evidence first · 13 August 2026</small></div>
<article>
{body_html}
</article>
</body>
</html>
"""


def main() -> None:
    md_path = HERE / "EVERYTHING.md"
    html_path = HERE / "everything.html"
    md = build_markdown()
    md_path.write_text(md, encoding="utf-8")
    body = md_to_html(md)
    body = body.replace(
        f"<p><strong>{html.escape(CENSUS_WARNING)}</strong></p>",
        f'<p class="warn">{html.escape(CENSUS_WARNING)}</p>',
    )
    words = len(re.findall(r"\S+", md))
    pages = words / 400.0
    html_path.write_text(wrap_html(body, words, pages), encoding="utf-8")
    print(f"wrote {md_path}")
    print(f"wrote {html_path}")
    print(f"words={words} pages~{pages:.1f}")


if __name__ == "__main__":
    main()
