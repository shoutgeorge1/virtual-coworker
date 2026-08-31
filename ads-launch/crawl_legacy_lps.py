#!/usr/bin/env python3
"""Read-only crawl of legacy WP / try.* / current .app employer pages.

No publishes. Writes xray/data/recovery-lp-crawl.json
"""

from __future__ import annotations

import json
import re
import ssl
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from html.parser import HTMLParser
from pathlib import Path
from typing import Any

REPO = Path(__file__).resolve().parents[1]
OUT = REPO / "xray" / "data" / "recovery-lp-crawl.json"
UA = "VC-recovery-audit/1.0 (+read-only; george@virtual-coworker)"
TIMEOUT = 18

URLS = [
    {"url": "https://virtualcoworker.com/", "role": "US WP home (historical Brand Final URL)"},
    {"url": "https://virtualcoworker.com/contact-us/", "role": "US WP contact / Gravity Form"},
    {"url": "https://virtualcoworker.com/contact/", "role": "US WP /contact alias"},
    {
        "url": "https://virtualcoworker.com/services/virtual-assistant-services/",
        "role": "US WP VA services (typical sitelink)",
    },
    {"url": "https://virtualcoworker.com/lp-fb/", "role": "US WP Facebook landing"},
    {"url": "https://virtualcoworker.com/thank-you-landing/", "role": "US WP thank-you landing"},
    {"url": "https://virtualcoworker.com/pricing/", "role": "US WP pricing"},
    {"url": "https://virtualcoworker.com.au/", "role": "AU WP home (historical Brand Final URL)"},
    {"url": "https://virtualcoworker.com.au/contact-us/", "role": "AU WP contact / Gravity Form"},
    {
        "url": "https://virtualcoworker.com.au/services/virtual-assistant-services/",
        "role": "AU WP VA services",
    },
    {"url": "https://try.virtualcoworker.com/us", "role": "try.* US (paused Brand ad destination)"},
    {"url": "https://try.virtualcoworker.com/apac", "role": "try.* AU/APAC"},
    {"url": "https://try.virtualcoworker.com/us/thank-you", "role": "try.* thank-you (historically 404)"},
    {"url": "https://www.virtualcoworker.app/us", "role": "Current paid US hub"},
    {"url": "https://www.virtualcoworker.app/au", "role": "Current paid AU hub"},
    {"url": "https://www.virtualcoworker.app/thank-you", "role": "Current .app thank-you"},
    {"url": "https://virtualcoworker.com.ph/", "role": "PH careers / job-seeker site"},
]


class FormProbe(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.title = ""
        self._in_title = False
        self.gtm: list[str] = []
        self.aw: list[str] = []
        self.forms = 0
        self.required: list[str] = []
        self.optional: list[str] = []
        self.placeholders: list[str] = []
        self.job_nav = False
        self.phones: list[str] = []
        self.has_recaptcha = False
        self._cur_label = ""
        self._in_label = False

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        ad = {k: (v or "") for k, v in attrs}
        if tag == "title":
            self._in_title = True
        if tag == "label":
            self._in_label = True
            self._cur_label = ""
        if tag == "form":
            self.forms += 1
        if tag in ("input", "textarea", "select"):
            itype = (ad.get("type") or "text").lower()
            if itype in ("hidden", "submit", "button", "reset", "image"):
                return
            name = ad.get("name") or ad.get("id") or ad.get("placeholder") or itype
            req = "required" in ad or ad.get("aria-required") == "true"
            label = (self._cur_label or ad.get("placeholder") or name).strip()
            if itype == "checkbox" and "honeypot" in (ad.get("class") or "").lower():
                return
            bucket = self.required if req else self.optional
            if label and label not in bucket:
                bucket.append(label[:80])
            ph = ad.get("placeholder")
            if ph and ph not in self.placeholders:
                self.placeholders.append(ph[:80])
        href = ad.get("href") or ""
        low = href.lower()
        if any(
            x in low
            for x in (
                ".ph",
                "/careers",
                "search-jobs",
                "looking-for-a-job",
                "become-a-va",
                "/jobs",
                "/apply",
            )
        ):
            self.job_nav = True
        if href.startswith("tel:"):
            self.phones.append(href.replace("tel:", "").strip())

    def handle_endtag(self, tag: str) -> None:
        if tag == "title":
            self._in_title = False
        if tag == "label":
            self._in_label = False

    def handle_data(self, data: str) -> None:
        if self._in_title:
            self.title += data
        if self._in_label:
            self._cur_label += data


def fetch(url: str) -> dict[str, Any]:
    ctx = ssl.create_default_context()
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "text/html"})
    chain: list[str] = [url]
    status = None
    final = url
    html = ""
    bytes_n = 0
    err = None
    t0 = time.time()
    try:
        with urllib.request.urlopen(req, timeout=TIMEOUT, context=ctx) as resp:
            status = getattr(resp, "status", None) or resp.getcode()
            final = resp.geturl()
            raw = resp.read(1_200_000)
            bytes_n = len(raw)
            html = raw.decode("utf-8", errors="replace")
            if hasattr(resp, "geturl") and resp.geturl() != url:
                chain.append(resp.geturl())
    except urllib.error.HTTPError as exc:
        status = exc.code
        err = str(exc.reason)
        try:
            raw = exc.read(80_000)
            bytes_n = len(raw)
            html = raw.decode("utf-8", errors="replace")
            final = exc.geturl() if hasattr(exc, "geturl") else url
        except Exception:  # noqa: BLE001
            html = ""
    except Exception as exc:  # noqa: BLE001
        err = str(exc)
    elapsed_ms = int((time.time() - t0) * 1000)

    probe = FormProbe()
    if html:
        try:
            probe.feed(html)
        except Exception:  # noqa: BLE001
            pass

    gtm = sorted(set(re.findall(r"GTM-[A-Z0-9]+", html)))
    aw = sorted(set(re.findall(r"AW-\d{6,}", html)))
    ga4 = sorted(set(re.findall(r"G-[A-Z0-9]{6,}", html)))
    if "recaptcha" in html.lower() or "g-recaptcha" in html.lower():
        probe.has_recaptcha = True
    if re.search(
        r"looking for a job|search jobs|become a va|i.m looking for a job",
        html,
        re.I,
    ):
        probe.job_nav = True
    phones = list(probe.phones)
    phones += re.findall(r"\+?1[\s.-]?\(?888\)?[\s.-]?\d{3}[\s.-]?\d{4}", html)
    phones += re.findall(r"1300[\s.-]?\d{3}[\s.-]?\d{3}", html)
    phones = sorted(set(p.strip() for p in phones if p.strip()))[:6]

    employer_form = probe.forms > 0 and not re.search(
        r"apply for (this )?job|upload (your )?resume|cv attach", html, re.I
    )

    return {
        "requested": url,
        "final_url": final,
        "status": status,
        "error": err,
        "elapsed_ms": elapsed_ms,
        "bytes": bytes_n,
        "redirected": final.rstrip("/") != url.rstrip("/"),
        "title": (probe.title or "").strip()[:140],
        "gtm": gtm,
        "aw": aw,
        "ga4": ga4,
        "forms": probe.forms,
        "employer_form_present": bool(employer_form),
        "required_fields": probe.required[:12],
        "optional_fields": probe.optional[:12],
        "placeholders": probe.placeholders[:12],
        "job_seeker_nav": probe.job_nav,
        "phones_visible": phones,
        "recaptcha": probe.has_recaptcha,
        "indexable_hint": "noindex" not in html[:4000].lower(),
    }


def main() -> int:
    rows: list[dict[str, Any]] = []
    for item in URLS:
        print(f"GET {item['url']}", flush=True)
        row = fetch(item["url"])
        row["role"] = item["role"]
        rows.append(row)
        time.sleep(0.35)
    payload = {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "read_only": True,
        "pages": rows,
        "note": "Live HEAD/GET 13 Aug 2026. Form field lists are HTML-derived; Gravity Forms may mark required in JS.",
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {OUT} ({len(rows)} pages)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
