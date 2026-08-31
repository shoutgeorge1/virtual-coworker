#!/usr/bin/env python3
"""Iterative MyOutDesk /lp/ discovery. Local candidate gen can be large; remote GETs are ranked, cached, throttled."""

from __future__ import annotations

import csv
import hashlib
import json
import re
import time
import urllib.error
import urllib.request
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path("/Users/george/Developer/virtual-coworker")
OUT = ROOT / "ads-launch/research/myoutdesk-2026-08-18"
CACHE = OUT / "cache"
CACHE.mkdir(parents=True, exist_ok=True)

UA = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36"
)
BASE = "https://www.myoutdesk.com"
SLEEP_S = 0.85
MAX_REMOTE = 420
STOP_ON = {403, 429, 503}

STOPWORDS = {
    "a", "an", "the", "in", "on", "of", "for", "to", "and", "or", "from",
    "with", "near", "me", "my", "our", "your", "best", "top",
}

# Observed grammar: /lp/google-{hyphen-slug}/
KNOWN_CONFIRMED = {
    "google-philippines-virtual-assistants": "ph_va_geo",
    "google-brand-search-campaign-b": "brand",
}

SITEMAP_SERVICE = [
    "administrative-virtual-assistants",
    "ai",
    "bookkeeping",
    "customer-service-virtual-assistant",
    "help-desk-outsourcing",
    "inside-sales-agent",
    "loan-processor-assistant",
    "marketing-virtual-assistants",
    "medical-billing-virtual-assistant",
    "real-estate-isa",
    "recruiting-assistant",
    "sales-development-representative",
    "transaction-coordinator",
    "virtual-medical-receptionist",
    "virtual-personal-assistant",
    "virtual-receptionist",
]
SITEMAP_INDUSTRY = [
    "ecommerce-virtual-assistants",
    "financial-planning",
    "healthcare",
    "hr-virtual-assistants",
    "insurance-virtual-assistants",
    "legal",
    "marketing-agency",
    "mortgage-virtual-assistants",
    "property-management",
    "real-estate-virtual-assistants",
    "tech-virtual-assistants",
]

ROLE_STEMS = [
    "bookkeeping", "bookkeeper", "accounting", "accountant",
    "customer-service", "customer-support", "admin", "administrative",
    "executive-assistant", "virtual-receptionist", "appointment-setter",
    "sales", "inside-sales", "sdr", "digital-marketing", "marketing",
    "social-media", "hr", "human-resources", "recruiting", "recruitment",
    "transaction-coordinator", "isa",
]
INDUSTRY_STEMS = [
    "real-estate", "property-management", "healthcare", "insurance",
    "mortgage", "legal", "ecommerce", "tech", "staffing",
]
GEO_STEMS = ["philippines", "filipino", "offshore", "remote"]
SERVICE_STEMS = [
    "virtual-assistants", "virtual-assistant", "va",
    "staffing-agency", "staffing", "outsourcing",
    "virtual-staff", "remote-staff",
]
INTENT_STEMS = ["hire", "outsource", "outsourcing"]

CLUSTERS = {
    "ph_va_geo": ["virtual assistant philippines", "filipino virtual assistant", "hire virtual assistant philippines"],
    "offshore_outsourcing": ["offshore virtual assistants", "outsourcing virtual assistant", "va outsourcing philippines"],
    "agency_firm": ["virtual assistant agency", "virtual assistant company", "virtual assistant firm", "philippines va agency"],
    "staffing": ["remote staffing agency", "virtual staffing agency", "philippines staffing agency", "offshore staffing agency"],
    "virtual_staff": ["virtual staff philippines", "hire virtual staff", "filipino virtual staff"],
    "bookkeeping": ["virtual assistant bookkeeping", "bookkeeper philippines", "outsource bookkeeping philippines"],
    "accounting": ["virtual assistant accounting", "accountant philippines", "outsource accounting philippines"],
    "customer_service": ["customer service philippines", "virtual assistant customer service", "outsource customer service"],
    "admin_ea": ["executive assistant philippines", "virtual administrative assistant", "virtual receptionist"],
    "appointment_sales": ["virtual appointment setter", "inside sales agent", "virtual sales assistant"],
    "marketing": ["digital marketing virtual assistant", "marketing virtual assistant", "social media marketing va"],
    "hr_recruit": ["hr virtual assistant", "recruiting assistant", "outsource hr philippines"],
    "real_estate": ["real estate virtual assistant", "real estate isa", "transaction coordinator"],
    "brand": ["myoutdesk", "my out desk"],
}


def utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def slugify(text: str) -> str:
    text = text.lower()
    text = re.sub(r"[^a-z0-9\s-]", " ", text)
    parts = [p for p in re.split(r"[\s_]+", text) if p and p not in STOPWORDS]
    return "-".join(parts)


def permutations_from_phrase(phrase: str) -> list[str]:
    words = [w for w in slugify(phrase).split("-") if w]
    if not words:
        return []
    out = ["-".join(words)]
    if len(words) >= 2:
        out.append("-".join(reversed(words)))
        out.append("-".join(words[1:] + words[:1]))
    # drop leading hire/outsource for service-first
    if words[0] in INTENT_STEMS and len(words) > 1:
        out.append("-".join(words[1:]))
    # plural/singular
    last = words[-1]
    if last.endswith("s") and len(last) > 3:
        out.append("-".join(words[:-1] + [last[:-1]]))
    elif last in {"assistant", "agency", "company", "firm", "bookkeeper", "accountant"}:
        out.append("-".join(words[:-1] + [last + "s"]))
    return [s for s in dict.fromkeys(out) if s]


def load_vc_keywords() -> list[tuple[str, str]]:
    """Return (keyword, source_cluster) from local cache."""
    rows: list[tuple[str, str]] = []
    rsa = ROOT / "ads-launch/_rsa_challenger_review.json"
    if rsa.exists():
        data = json.loads(rsa.read_text())
        groups = data if isinstance(data, list) else data.get("ad_groups") or data.get("groups") or []
        if isinstance(data, dict) and not groups:
            # try common keys
            for key in ("ad_groups", "groups", "items", "data"):
                if isinstance(data.get(key), list):
                    groups = data[key]
                    break
        if isinstance(data, dict) and "ad_group" in data:
            groups = [data]
        # file is a list of ad group objects in this repo
        if isinstance(data, dict):
            maybe = data.get("us") or data.get("review") or data.get("adGroups")
            if isinstance(maybe, list):
                groups = maybe
        if not groups and isinstance(data, dict):
            # walk for objects with keywords
            def walk(obj):
                if isinstance(obj, dict):
                    if "ad_group" in obj and "keywords" in obj:
                        yield obj
                    for v in obj.values():
                        yield from walk(v)
                elif isinstance(obj, list):
                    for i in obj:
                        yield from walk(i)
            groups = list(walk(data))
        for g in groups:
            if not isinstance(g, dict):
                continue
            ag = str(g.get("ad_group") or "unknown")
            for kw in g.get("keywords") or []:
                term = kw.get("keyword") if isinstance(kw, dict) else kw
                if term:
                    rows.append((str(term), ag))
            for st in g.get("search_terms") or []:
                term = st.get("term") if isinstance(st, dict) else st
                if term:
                    rows.append((str(term), ag + "_st"))
    csv_path = ROOT / "ads-launch/google-ads-editor-agency-intent-keywords-add.csv"
    if csv_path.exists():
        with csv_path.open(newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for r in reader:
                kw = (r.get("Keyword") or "").strip()
                ag = (r.get("Ad Group") or "agency_intent").strip()
                if kw:
                    rows.append((kw, ag))
    return rows


def generate_candidates() -> list[dict]:
    """Large local universe; each item has slug, url, cluster, score, source."""
    seen: dict[str, dict] = {}

    def add(slug: str, cluster: str, score: int, source: str):
        slug = slug.strip("-")
        slug = re.sub(r"-{2,}", "-", slug)
        if not slug or len(slug) > 80:
            return
        # skip junk
        if any(x in slug for x in ("http", "www", "virtual-coworker", "nexrep", "pineapple")):
            return
        url = f"{BASE}/lp/{slug}/"
        prev = seen.get(slug)
        if prev:
            prev["score"] = max(prev["score"], score)
            if cluster not in prev["clusters"]:
                prev["clusters"].append(cluster)
            return
        seen[slug] = {
            "slug": slug,
            "url": url,
            "cluster": cluster,
            "clusters": [cluster],
            "score": score,
            "source": source,
        }

    # Known confirmed / high value
    for slug, cluster in KNOWN_CONFIRMED.items():
        add(slug, cluster, 1000, "known")

    # Brand grammar variants learned from campaign-b
    for slug in [
        "google-brand-search-campaign-a",
        "google-brand-search-campaign-c",
        "google-brand-search-campaign",
        "google-brand-search",
        "google-brand",
        "google-brand-campaign",
        "google-myoutdesk",
        "google-branded-search",
    ]:
        add(slug, "brand", 860, "brand_grammar")

    # Sitemap service/industry → google-{slug}  (highest non-known)
    for s in SITEMAP_SERVICE:
        add(f"google-{s}", "sitemap_service", 920, "sitemap_service")
        add(f"google-{s}s" if not s.endswith("s") else f"google-{s.rstrip('s')}", "sitemap_service", 700, "sitemap_plural")
    for s in SITEMAP_INDUSTRY:
        add(f"google-{s}", "sitemap_industry", 930, "sitemap_industry")

    # Seed grammar: google-philippines-virtual-assistants
    add("google-virtual-assistants-philippines", "ph_va_geo", 880, "seed_word_order")
    add("google-philippines-virtual-assistant", "ph_va_geo", 870, "seed_singular")
    add("google-filipino-virtual-assistants", "ph_va_geo", 890, "seed_filipino")
    add("google-filipino-virtual-assistant", "ph_va_geo", 800, "seed_filipino_s")
    add("google-hire-virtual-assistant", "ph_va_geo", 850, "hire")
    add("google-hire-virtual-assistants", "ph_va_geo", 840, "hire")
    add("google-hire-a-virtual-assistant", "ph_va_geo", 620, "hire_stopword")
    add("google-virtual-assistant-philippines", "ph_va_geo", 860, "service_first")
    add("google-virtual-assistants", "ph_va_geo", 780, "generic")
    add("google-virtual-assistant", "ph_va_geo", 760, "generic")

    # UTM-derived
    add("google-virtual-assistants-outsourcing", "offshore_outsourcing", 900, "utm_campaign")
    add("google-virtual-assistant-outsourcing", "offshore_outsourcing", 820, "utm_campaign")
    add("google-outsourcing-virtual-assistants", "offshore_outsourcing", 810, "utm_campaign")
    add("google-offshore-virtual-assistants", "offshore_outsourcing", 840, "offshore")
    add("google-offshore-virtual-assistant", "offshore_outsourcing", 760, "offshore")

    # Agency / staffing
    for slug, cluster, score in [
        ("google-virtual-assistant-agency", "agency_firm", 880),
        ("google-virtual-assistant-agencies", "agency_firm", 760),
        ("google-virtual-assistant-company", "agency_firm", 860),
        ("google-virtual-assistant-companies", "agency_firm", 740),
        ("google-virtual-assistant-firm", "agency_firm", 850),
        ("google-philippines-virtual-assistant-agency", "agency_firm", 870),
        ("google-philippines-va-agency", "agency_firm", 800),
        ("google-filipino-virtual-assistant-agency", "agency_firm", 830),
        ("google-remote-staffing-agency", "staffing", 880),
        ("google-virtual-staffing-agency", "staffing", 860),
        ("google-philippines-staffing-agency", "staffing", 850),
        ("google-offshore-staffing-agency", "staffing", 840),
        ("google-staffing-agency-philippines", "staffing", 820),
        ("google-virtual-staff-philippines", "virtual_staff", 830),
        ("google-philippines-virtual-staff", "virtual_staff", 820),
        ("google-hire-virtual-staff", "virtual_staff", 780),
        ("google-filipino-virtual-staff", "virtual_staff", 800),
        ("google-virtual-staffing", "virtual_staff", 760),
        ("google-remote-staff-philippines", "virtual_staff", 740),
    ]:
        add(slug, cluster, score, "core_cluster")

    # Role + industry × google- + optional philippines
    for stem in ROLE_STEMS + INDUSTRY_STEMS:
        add(f"google-{stem}", stem.replace("-", "_")[:24], 720, "stem")
        add(f"google-{stem}-virtual-assistants", stem.replace("-", "_")[:24], 800, "stem_va_pl")
        add(f"google-{stem}-virtual-assistant", stem.replace("-", "_")[:24], 760, "stem_va")
        add(f"google-philippines-{stem}", stem.replace("-", "_")[:24], 740, "ph_stem")
        add(f"google-{stem}-philippines", stem.replace("-", "_")[:24], 730, "stem_ph")
        add(f"google-hire-{stem}", stem.replace("-", "_")[:24], 700, "hire_stem")
        add(f"google-outsource-{stem}", stem.replace("-", "_")[:24], 690, "outsource_stem")
        add(f"google-{stem}-outsourcing", stem.replace("-", "_")[:24], 710, "stem_outsourcing")

    # VC keyword expansions
    for kw, ag in load_vc_keywords():
        cluster = ag.replace("_st", "")
        for perm in permutations_from_phrase(kw)[:6]:
            add(f"google-{perm}", cluster, 640, "vc_kw")
            if "philippines" not in perm and "filipino" not in perm:
                add(f"google-philippines-{perm}", cluster, 610, "vc_kw_ph")
            if not perm.startswith("hire-") and "virtual" in perm:
                add(f"google-hire-{perm}", cluster, 600, "vc_kw_hire")

    # Cluster phrases
    for cluster, phrases in CLUSTERS.items():
        for ph in phrases:
            for perm in permutations_from_phrase(ph):
                add(f"google-{perm}", cluster, 750, "cluster_phrase")

    # Non-google /lp/ prefix test (small, high-prob only)
    for slug in [
        "philippines-virtual-assistants",
        "virtual-assistants-outsourcing",
        "brand-search-campaign-b",
        "real-estate-virtual-assistants",
        "bookkeeping",
    ]:
        add(slug, "prefix_test", 400, "no_google_prefix")

    # facebook/bing prefix test (tiny)
    for slug in [
        "facebook-philippines-virtual-assistants",
        "bing-philippines-virtual-assistants",
        "microsoft-philippines-virtual-assistants",
    ]:
        add(slug, "network_prefix_test", 350, "other_network")

    items = list(seen.values())
    items.sort(key=lambda x: (-x["score"], x["slug"]))
    return items


def parse_html(html: str) -> dict:
    def meta(name: str) -> str:
        m = re.search(
            rf'<meta[^>]+name=["\']{re.escape(name)}["\'][^>]*content=["\']([^"\']*)["\']',
            html,
            re.I,
        )
        if m:
            return m.group(1)
        m = re.search(
            rf'<meta[^>]+content=["\']([^"\']*)["\'][^>]*name=["\']{re.escape(name)}["\']',
            html,
            re.I,
        )
        return m.group(1) if m else ""

    title_m = re.search(r"<title>(.*?)</title>", html, re.I | re.S)
    title = re.sub(r"\s+", " ", title_m.group(1)).strip() if title_m else ""
    can_m = re.search(r'<link[^>]+rel=["\']canonical["\'][^>]+href=["\']([^"\']+)', html, re.I)
    if not can_m:
        can_m = re.search(r'<link[^>]+href=["\']([^"\']+)["\'][^>]+rel=["\']canonical["\']', html, re.I)
    h1s = []
    for m in re.finditer(r"<h1[^>]*>(.*?)</h1>", html, re.I | re.S):
        t = re.sub(r"<[^>]+>", " ", m.group(1))
        t = re.sub(r"\s+", " ", t).strip()
        if t:
            h1s.append(t)
    h2s = []
    for m in re.finditer(r"<h2[^>]*>(.*?)</h2>", html, re.I | re.S):
        t = re.sub(r"<[^>]+>", " ", m.group(1))
        t = re.sub(r"\s+", " ", t).strip()
        if t and t not in h2s:
            h2s.append(t)
    desc = meta("description")
    robots = meta("robots")
    has_form = bool(re.search(r'name=["\']businessEmail["\']', html) or re.search(r'name=["\']fullName["\']', html))
    has_cta = bool(re.search(r"strategy (session|call)|book a call|#book-call|#signup", html, re.I))
    phone_prominence = bool(re.search(r"800[^\d]{0,3}583[^\d]{0,3}9950|tel:\+?18005839950", html, re.I))
    body_hash = hashlib.sha256(html.encode("utf-8", errors="replace")).hexdigest()[:16]
    # hero: first substantial paragraph-like text after h1
    hero = ""
    if h1s:
        idx = html.lower().find("<h1")
        chunk = html[idx : idx + 2500] if idx >= 0 else ""
        ps = re.findall(r"<p[^>]*>(.*?)</p>", chunk, re.I | re.S)
        for p in ps:
            t = re.sub(r"<[^>]+>", " ", p)
            t = re.sub(r"\s+", " ", t).strip()
            if len(t) > 40:
                hero = t[:280]
                break
    return {
        "title": title,
        "h1": " | ".join(h1s[:2]),
        "h2s": h2s[:12],
        "canonical": can_m.group(1) if can_m else "",
        "robots": robots,
        "meta_description": desc,
        "has_form": has_form,
        "has_cta": has_cta,
        "phone_prominence": phone_prominence,
        "body_len": len(html),
        "body_hash": body_hash,
        "hero": hero,
    }


def classify(status: int, final_url: str, parsed: dict, seed: dict, notfound: dict) -> tuple[str, bool, str, str]:
    """Return page_type, genuine_paid_lp, evidence, confidence."""
    title = parsed["title"]
    h1 = parsed["h1"]
    can = parsed["canonical"]
    robots = parsed["robots"].lower()
    if status in (403, 429, 503):
        return "blocked", False, f"HTTP {status}", "observed"
    if status == 404 or (status >= 400):
        return "missing", False, f"HTTP {status}", "observed"
    # redirects away from /lp/
    if "/lp/" not in (final_url or ""):
        return "redirected", False, f"final URL left /lp/: {final_url}", "observed"
    # soft 404
    if (
        "page not found" in title.lower()
        or "/404" in can
        or (notfound and parsed["body_hash"] == notfound.get("body_hash"))
    ):
        return "soft_404", False, "404 title/canonical/hash match", "observed"
    if parsed["body_len"] < 8000 and "not found" in (title + h1).lower():
        return "soft_404", False, "short body + not-found language", "observed"
    # catch-all: identical to seed but different slug/canonical would still be a real unique page if canonical matches self
    slug_in_can = can.rstrip("/").split("/")[-1] if can else ""
    slug_in_final = final_url.rstrip("/").split("/")[-1] if final_url else ""
    is_noindex = "noindex" in robots
    looks_paid = is_noindex and parsed["has_form"] and parsed["has_cta"] and parsed["body_len"] > 40000
    if looks_paid and slug_in_can and slug_in_can == slug_in_final:
        # genuine if not the generic 404
        if seed and parsed["body_hash"] == seed.get("body_hash") and slug_in_final != "google-philippines-virtual-assistants":
            return "catch_all", False, "identical body hash to seed on different slug", "observed"
        evidence = []
        if is_noindex:
            evidence.append("noindex")
        if parsed["has_form"]:
            evidence.append("employer form")
        if parsed["has_cta"]:
            evidence.append("strategy-call CTA")
        if slug_in_can == slug_in_final:
            evidence.append("self-canonical")
        ev = "; ".join(evidence)
        if title and h1:
            return "confirmed_paid_lp", True, ev, "observed"
        return "uncertain", False, ev + "; missing title/h1", "speculative"
    if parsed["has_form"] and parsed["body_len"] > 20000:
        return "uncertain", False, "form present but missing noindex/self-canonical combo", "high-confidence inference"
    if 300 <= status < 400:
        return "redirected", False, f"HTTP {status} → {final_url}", "observed"
    return "missing_or_thin", False, f"HTTP {status}; len={parsed['body_len']}; robots={robots or 'none'}", "observed"


def cache_name(url: str) -> Path:
    slug = url.rstrip("/").split("/")[-1] or "root"
    safe = re.sub(r"[^a-z0-9-]", "_", slug)[:80]
    return CACHE / f"lp-{safe}.html"


def fetch(url: str) -> tuple[int, str, str, str]:
    """GET clean URL. Returns status, final_url, html, error."""
    path = cache_name(url)
    hdr = path.with_suffix(".headers")
    if path.exists() and path.stat().st_size > 200:
        html = path.read_text(errors="replace")
        status = 200
        final = url
        if hdr.exists():
            head = hdr.read_text(errors="replace")
            m = re.search(r"^HTTP/\S+\s+(\d+)", head, re.M)
            if m:
                status = int(m.group(1))
            loc = re.search(r"^x-final-url:\s+(\S+)", head, re.I | re.M)
            if loc:
                final = loc.group(1)
        return status, final, html, "cache"
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "text/html,application/xhtml+xml"})
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            html = resp.read().decode("utf-8", errors="replace")
            status = resp.getcode() or 200
            final = resp.geturl() or url
            path.write_text(html, encoding="utf-8")
            hdr.write_text(
                f"HTTP/2 {status}\nx-final-url: {final}\ndate: {utc_now()}\n",
                encoding="utf-8",
            )
            return status, final, html, "live"
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", errors="replace") if e.fp else ""
        path.write_text(body, encoding="utf-8")
        hdr.write_text(
            f"HTTP/2 {e.code}\nx-final-url: {url}\ndate: {utc_now()}\nerror: HTTPError\n",
            encoding="utf-8",
        )
        return e.code, url, body, "http_error"
    except Exception as e:
        return 0, url, "", f"error:{type(e).__name__}:{e}"


def write_probes(rows: list[dict], path: Path) -> None:
    fields = [
        "keyword_cluster",
        "tested_url",
        "status",
        "final_url",
        "page_title",
        "h1",
        "canonical",
        "robots_status",
        "page_type",
        "genuine_paid_lp",
        "evidence",
        "confidence",
        "body_len",
        "body_hash",
        "has_form",
        "has_cta",
        "score",
        "source",
        "fetch",
        "checked_at",
    ]
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
        w.writeheader()
        for r in rows:
            w.writerow(r)


def load_seed_and_404() -> tuple[dict, dict]:
    seed_html = (CACHE / "lp-google-philippines-virtual-assistants.html").read_text(errors="replace")
    seed = parse_html(seed_html)
    nf_path = CACHE / "wp-json.json"
    notfound = parse_html(nf_path.read_text(errors="replace")) if nf_path.exists() else {}
    return seed, notfound


def main() -> None:
    candidates = generate_candidates()
    (OUT / "candidate-universe.json").write_text(
        json.dumps(
            {
                "generated_at": utc_now(),
                "total_candidates": len(candidates),
                "by_cluster": dict(Counter(c["cluster"] for c in candidates)),
                "top_50": [
                    {"slug": c["slug"], "score": c["score"], "cluster": c["cluster"], "source": c["source"]}
                    for c in candidates[:50]
                ],
            },
            indent=2,
        ),
        encoding="utf-8",
    )
    seed, notfound = load_seed_and_404()
    probes_path = OUT / "myoutdesk-lp-probes.csv"
    rows: list[dict] = []
    confirmed: list[dict] = []
    remote = 0
    stopped = ""
    # Always include seed from cache first
    batch_no = 1
    empty_batches = 0
    tested_slugs: set[str] = set()

    def probe_item(c: dict) -> dict | None:
        nonlocal remote, stopped
        if c["slug"] in tested_slugs:
            return None
        tested_slugs.add(c["slug"])
        url = c["url"]
        cached = cache_name(url).exists() and cache_name(url).stat().st_size > 200
        if not cached:
            if remote >= MAX_REMOTE:
                stopped = "max_remote"
                return None
            time.sleep(SLEEP_S)
            remote += 1
        status, final, html, fetch_src = fetch(url)
        if status in STOP_ON:
            stopped = f"http_{status}"
        parsed = parse_html(html) if html else {
            "title": "", "h1": "", "canonical": "", "robots": "", "meta_description": "",
            "has_form": False, "has_cta": False, "phone_prominence": False,
            "body_len": 0, "body_hash": "", "hero": "", "h2s": [],
        }
        page_type, genuine, evidence, conf = classify(status, final, parsed, seed, notfound)
        row = {
            "keyword_cluster": c["cluster"],
            "tested_url": url,
            "status": status,
            "final_url": final,
            "page_title": parsed["title"],
            "h1": parsed["h1"],
            "canonical": parsed["canonical"],
            "robots_status": parsed["robots"],
            "page_type": page_type,
            "genuine_paid_lp": "yes" if genuine else "no",
            "evidence": evidence,
            "confidence": conf,
            "body_len": parsed["body_len"],
            "body_hash": parsed["body_hash"],
            "has_form": parsed["has_form"],
            "has_cta": parsed["has_cta"],
            "score": c["score"],
            "source": c["source"],
            "fetch": fetch_src,
            "checked_at": utc_now(),
            "meta_description": parsed.get("meta_description", ""),
            "hero": parsed.get("hero", ""),
            "h2s": parsed.get("h2s", []),
            "slug": c["slug"],
        }
        return row

    # Batch plan: high-score slices, then expand around confirmed
    queue = [c for c in candidates if c["score"] >= 690]
    # ensure known first
    queue.sort(key=lambda x: (-x["score"], x["slug"]))

    while queue and not stopped and empty_batches < 2:
        # take next 80 untested
        batch = []
        for c in queue:
            if c["slug"] not in tested_slugs:
                batch.append(c)
            if len(batch) >= 80:
                break
        if not batch:
            break
        new_confirmed = 0
        for c in batch:
            if stopped:
                break
            row = probe_item(c)
            if not row:
                continue
            rows.append(row)
            if row["genuine_paid_lp"] == "yes":
                confirmed.append(row)
                new_confirmed += 1
            write_probes(rows, probes_path)
            print(f"[{len(rows)} remote~{remote}] {row['status']} {row['page_type']} {row['tested_url']} :: {row['page_title'][:60]}")
        if new_confirmed == 0:
            empty_batches += 1
        else:
            empty_batches = 0
            # expand around confirmed slugs
            extras = []
            for row in confirmed:
                slug = row["slug"]
                parts = slug.split("-")
                if parts[:1] == ["google"] and len(parts) > 2:
                    rest = parts[1:]
                    extras.append((f"google-{'-'.join(reversed(rest))}", row["keyword_cluster"], 780, "learned_reverse"))
                    if rest[-1] == "assistants":
                        extras.append((f"google-{'-'.join(rest[:-1]+['assistant'])}", row["keyword_cluster"], 770, "learned_singular"))
                    if rest[-1] == "assistant":
                        extras.append((f"google-{'-'.join(rest[:-1]+['assistants'])}", row["keyword_cluster"], 770, "learned_plural"))
                    if "philippines" not in rest:
                        extras.append((f"google-philippines-{'-'.join(rest)}", row["keyword_cluster"], 760, "learned_ph"))
            for slug, cluster, score, source in extras:
                if slug not in tested_slugs:
                    queue.append({"slug": slug, "url": f"{BASE}/lp/{slug}/", "cluster": cluster, "score": score, "source": source, "clusters": [cluster]})
            queue.sort(key=lambda x: (-x["score"], x["slug"]))
        batch_no += 1
        # after two empty high-score batches, pull a lower-score slice once
        if empty_batches >= 2 and batch_no <= 4:
            more = [c for c in candidates if c["score"] < 690 and c["score"] >= 600 and c["slug"] not in tested_slugs][:80]
            if more:
                queue.extend(more)
                empty_batches = 1  # allow one more empty then stop

    summary = {
        "generated_at": utc_now(),
        "total_candidates_generated": len(candidates),
        "urls_tested": len(rows),
        "remote_gets_approx": remote,
        "confirmed": [r["tested_url"] for r in confirmed],
        "confirmed_count": len(confirmed),
        "stopped": stopped or "two_empty_or_queue_done",
        "page_type_counts": dict(Counter(r["page_type"] for r in rows)),
        "hash_counts": dict(Counter(r["body_hash"] for r in rows if r["body_hash"]).most_common(8)),
        "pattern_hits": {},
    }
    # hit rate by prefix pattern
    patterns = defaultdict(lambda: {"tested": 0, "confirmed": 0})
    for r in rows:
        slug = r["slug"]
        if slug.startswith("google-"):
            pat = "google-*"
        elif slug.startswith("facebook-"):
            pat = "facebook-*"
        elif slug.startswith("bing-"):
            pat = "bing-*"
        else:
            pat = "lp-no-google-prefix"
        patterns[pat]["tested"] += 1
        if r["genuine_paid_lp"] == "yes":
            patterns[pat]["confirmed"] += 1
    summary["pattern_hits"] = dict(patterns)
    (OUT / "probe-summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    (OUT / "confirmed-lp-extracts.json").write_text(
        json.dumps(
            [
                {
                    "url": r["tested_url"],
                    "slug": r["slug"],
                    "cluster": r["keyword_cluster"],
                    "title": r["page_title"],
                    "h1": r["h1"],
                    "canonical": r["canonical"],
                    "robots": r["robots_status"],
                    "meta_description": r.get("meta_description", ""),
                    "hero": r.get("hero", ""),
                    "h2s": r.get("h2s", []),
                    "body_len": r["body_len"],
                    "body_hash": r["body_hash"],
                    "has_form": r["has_form"],
                    "has_cta": r["has_cta"],
                }
                for r in confirmed
            ],
            indent=2,
        ),
        encoding="utf-8",
    )
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
