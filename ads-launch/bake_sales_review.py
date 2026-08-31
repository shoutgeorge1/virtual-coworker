#!/usr/bin/env python3
"""Bake xray/sales-review.html — plain English, people not Ads tags."""

from __future__ import annotations

import html
import json
from pathlib import Path
from typing import Any

REPO = Path(__file__).resolve().parents[1]
XRAY = REPO / "xray"
DATA = XRAY / "data" / "lead-quality-recon.json"
OUT = XRAY / "sales-review.html"

LP_BY_TERM = {
    "hire a social media manager": "Australia social-media page",
    "virtual assistant agency in usa": "US home page",
    "virtual assistant for real estate investors": "US home page",
    "australia virtual assistant": "Australia recruitment page",
}

WHAT_HAPPENED = {
    "Information Brochure Sent": "Holly sent a brochure. No call booked yet.",
    "Attempted to Contact 3 (Auto)": "Cheyenne tried them three times. No call booked yet.",
    "Attempted to Contact 2 (Auto)": "Cheyenne tried them. No call booked yet.",
    "Decided Against / Not a Fit": "Sales said this is not our customer.",
    "Junk Lead": "Sales marked this junk.",
    "Discovery Scheduled": "They booked a call.",
    "Job Order Submitted": "Sales says they want to hire.",
    "New Enquiry (Auto)": "New form. Sales has not sorted it yet.",
}

VERDICT = {
    "qualified_employer": ("Looks like a real employer", "ok"),
    "probable_employer": ("Maybe — sales is still on it", "mid"),
    "job_seeker": ("Looking for a job", "seek"),
    "junk": ("Junk", "bad"),
    "test": ("Our own test", "unk"),
    "not_a_fit": ("Real person, wrong customer", "mid"),
    "needs_review": ("Sales has not said yet", "unk"),
}


def esc(value: Any) -> str:
    return html.escape(str(value or ""), quote=True)


def tag(quality: str) -> str:
    label, kind = VERDICT.get(quality, ("Sales has not said yet", "unk"))
    return f'<span class="tag tag-{kind}">{esc(label)}</span>'


def date_short(created: str) -> str:
    raw = (created or "")[:10]
    if len(raw) == 10:
        _y, m, d = raw.split("-")
        months = "Jan Feb Mar Apr May Jun Jul Aug Sep Oct Nov Dec".split()
        return f"{int(d)} {months[int(m) - 1]}"
    return created or "—"


def bake(data: dict[str, Any]) -> str:
    people = list(data.get("people") or [])
    rows = []
    for p in people:
        term = str(p.get("utm_term") or "—")
        page = LP_BY_TERM.get(term.lower(), "—")
        happened = WHAT_HAPPENED.get(str(p.get("status") or ""), str(p.get("status") or "—"))
        country = "US" if str(p.get("region") or "").upper() in {"USA", "US"} else "Australia"
        rows.append(
            "<tr>"
            f"<td>{esc(date_short(str(p.get('created') or '')))}</td>"
            f"<td>{esc(country)}</td>"
            f"<td>{esc(term)}</td>"
            f"<td>{esc(page)}</td>"
            f"<td>{esc(happened)}</td>"
            f"<td>{tag(str(p.get('quality') or 'needs_review'))}</td>"
            "</tr>"
        )

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <meta name="robots" content="noindex,nofollow" />
  <title>Were these real leads? · Virtual Coworker</title>
  <link rel="preconnect" href="https://fonts.googleapis.com" />
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
  <link href="https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500&family=IBM+Plex+Sans:wght@400;500;600;700&display=swap" rel="stylesheet" />
  <link rel="stylesheet" href="xray.css" />
  <style>
    body[data-page="sales-review.html"] .main {{ max-width: 880px; }}
    .sr-hero {{
      margin: 0 0 1rem;
      padding: 1.05rem 1.1rem;
      border-radius: 10px;
      border: 1px solid var(--tint-amber-edge);
      background: var(--tint-amber);
    }}
    .sr-hero h1 {{ margin: 0 0 0.45rem; font-size: 1.35rem; letter-spacing: -0.02em; }}
    .sr-hero p {{ margin: 0.3rem 0; font-size: 1.02rem; line-height: 1.45; }}
    .sr-box {{
      margin: 0 0 0.85rem;
      padding: 0.9rem 1rem;
      border-radius: 10px;
      border: 1px solid var(--edge-soft);
      background: var(--panel);
    }}
    .sr-box h2 {{ margin: 0 0 0.4rem; font-size: 1rem; }}
    .sr-box p, .sr-box li {{ margin: 0.3rem 0; font-size: 0.95rem; line-height: 1.45; }}
    .sr-box ol {{ margin: 0.2rem 0 0; padding: 0 0 0 1.2rem; }}
    table.data-table {{ width: 100%; border-collapse: collapse; font-size: 0.88rem; }}
    table.data-table th, table.data-table td {{
      text-align: left; padding: 0.5rem 0.4rem;
      border-bottom: 1px solid var(--edge-soft); vertical-align: top;
    }}
    table.data-table th {{ color: var(--muted); font-weight: 650; }}
    .tag {{ display: inline-block; padding: 0.12rem 0.42rem; border-radius: 4px; font-size: 0.78rem; font-weight: 700; }}
    .tag-ok {{ background: var(--tint-green-hd); }}
    .tag-mid {{ background: var(--tint-amber-hd); }}
    .tag-bad {{ background: var(--tint-rose-hd); }}
    .tag-unk {{ background: var(--tint-cool-hd); }}
    .tag-seek {{ background: var(--tint-violet-hd); }}
  </style>
</head>
<body data-page="sales-review.html" data-foot="Were these real leads?">
  <div class="app">
    <aside class="sidebar" data-nav></aside>
    <main class="main">
      <div class="sr-hero">
        <h1>Google said 7 conversions. That was 5 people. None are a confirmed hire yet.</h1>
        <p>If someone fills in the form and later books a call, that is still one person — not two wins.</p>
        <p>Do not treat the 7 as seven good leads.</p>
      </div>

      <div class="sr-box">
        <h2>The five people</h2>
        <table class="data-table">
          <thead>
            <tr>
              <th>When</th>
              <th>Where</th>
              <th>What they searched</th>
              <th>What page</th>
              <th>What sales did</th>
              <th>So what</th>
            </tr>
          </thead>
          <tbody>
            {"".join(rows)}
          </tbody>
        </table>
      </div>

      <div class="sr-box">
        <h2>In English</h2>
        <ol>
          <li>Two Australia people searched “australia virtual assistant.” Junk. Google still counted them.</li>
          <li>One US person searched real-estate virtual assistant. Sales said not a fit.</li>
          <li>One US person searched “virtual assistant agency in usa.” Cheyenne is still trying to reach them.</li>
          <li>One Australia person searched “hire a social media manager.” Holly sent a brochure. No call yet.</li>
        </ol>
        <p>So: two junk, one wrong customer, two maybes. Zero “yes, this is a real employer who wants to hire.”</p>
      </div>

      <div class="sr-box">
        <h2>What I need from Cheyenne and Holly</h2>
        <p>For each new paid lead, mark one of these: <strong>real employer</strong>, <strong>looking for a job</strong>, <strong>junk</strong>, or <strong>our test</strong>.</p>
        <p>They have not done that in Zoho yet. I can see they moved some rows (junk, not a fit, brochure). I cannot see a simple “this is a real employer” box. Ash is looking at Zoho this week.</p>
      </div>
    </main>
  </div>
  <script src="nav.js"></script>
</body>
</html>
"""


def verify(path: Path) -> None:
    text = path.read_text(encoding="utf-8")
    required = (
        "Google said 7 conversions. That was 5 people.",
        "Do not treat the 7 as seven good leads",
        "The five people",
        "hire a social media manager",
        "virtual assistant agency in usa",
        "What I need from Cheyenne and Holly",
        "real employer",
    )
    for phrase in required:
        if phrase not in text:
            raise SystemExit(f"sales-review.html missing required phrase: {phrase}")
    print("sales-review.html verify ok")


def main() -> int:
    if not DATA.is_file():
        print(f"Missing {DATA}")
        return 1
    data = json.loads(DATA.read_text(encoding="utf-8"))
    OUT.write_text(bake(data), encoding="utf-8")
    print(f"Wrote {OUT}")
    verify(OUT)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
