#!/usr/bin/env python3
"""Build the RSA challenger visual review page. No Ads upload.

Reads ads-launch/_rsa_challenger_evidence.json + rsa_challengers.py
Writes:
  xray/rsa-review.html
  xray/data/rsa-challenger-review.json
  ads-launch/_rsa_challenger_review.json
"""

from __future__ import annotations

import html
import json
import re
import sys
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from rsa_challengers import CHALLENGERS, COMPETITORS, LEAVE_REASONS  # noqa: E402

REPO = HERE.parent
EVIDENCE = HERE / "_rsa_challenger_evidence.json"
POST = HERE / "_rsa_challenger_post.json"
OUT_HTML = REPO / "xray" / "rsa-review.html"
OUT_JSON = REPO / "xray" / "data" / "rsa-challenger-review.json"
OUT_AUDIT = HERE / "_rsa_challenger_review.json"
LAST2 = {"2026-08-12", "2026-08-13"}
HOST = "www.virtualcoworker.app"


def esc(s: object) -> str:
    return html.escape("" if s is None else str(s), quote=True)


def money(v: float) -> str:
    return f"${v:,.0f}" if v >= 10 else f"${v:,.2f}"


def pct(clicks: int, impr: int) -> float | None:
    if not impr:
        return None
    return round(100.0 * clicks / impr, 1)


def ctr_s(clicks: int, impr: int) -> str:
    v = pct(clicks, impr)
    return "—" if v is None else f"{v}%"


def roll_metrics(rows: list[dict], *, last2: bool = False) -> dict:
    out = {"impr": 0, "clicks": 0, "conv": 0.0, "cost": 0.0}
    for r in rows:
        if last2 and r.get("date") not in LAST2:
            continue
        out["impr"] += int(r.get("impressions") or 0)
        out["clicks"] += int(r.get("clicks") or 0)
        out["conv"] += float(r.get("conversions") or 0)
        out["cost"] += float(r.get("cost") or 0)
    out["cost"] = round(out["cost"], 2)
    out["ctr"] = pct(out["clicks"], out["impr"])
    return out


def near_dup(a: str, b: str) -> bool:
    na = re.sub(r"[^a-z0-9]+", " ", a.lower()).strip()
    nb = re.sub(r"[^a-z0-9]+", " ", b.lower()).strip()
    if na == nb:
        return True
    if na in nb or nb in na:
        return len(min(na, nb, key=len)) >= 12
    wa, wb = set(na.split()), set(nb.split())
    if not wa or not wb:
        return False
    return len(wa & wb) / len(wa | wb) >= 0.82


def predict_strength(headlines: list[str], descs: list[str], keywords: list[str]) -> tuple[str, list[str]]:
    issues: list[str] = []
    if len(headlines) != 15:
        issues.append(f"{len(headlines)} headlines (need 15)")
    if len(descs) != 4:
        issues.append(f"{len(descs)} descriptions (need 4)")
    if len(set(headlines)) != len(headlines):
        issues.append("duplicate headlines")
    if len(set(descs)) != len(descs):
        issues.append("duplicate descriptions")
    lengths = [len(h) for h in headlines]
    if lengths and (max(lengths) - min(lengths) < 5):
        issues.append("headline lengths too similar")
    short = sum(1 for n in lengths if n <= 22)
    long = sum(1 for n in lengths if n >= 25)
    if short < 2:
        issues.append("need more short headlines")
    if long < 2:
        issues.append("need more long headlines")
    kw_roots = []
    for k in keywords[:8]:
        k = re.sub(r"[^a-z0-9 ]+", " ", k.lower())
        for token in ("virtual assistant", "staffing agency", "bookkeep", "appointment setter",
                      "customer service", "marketing", "social media", "recruit", "offshore",
                      "filipino", "philippines", "accounting", "sales"):
            if token in k:
                kw_roots.append(token)
        kw_roots.extend([w for w in k.split() if len(w) > 4][:3])
    kw_roots = list(dict.fromkeys(kw_roots))
    blob = " ".join(headlines).lower()
    hits = sum(1 for root in kw_roots if root and root in blob)
    if kw_roots and hits < 2:
        issues.append("weak keyword coverage")
    if any("{" in h for h in headlines):
        issues.append("DKI present — check natural language")
    if not issues:
        return "Excellent", []
    if len(issues) == 1 and issues[0].startswith("DKI"):
        return "Excellent", issues
    if len(issues) <= 2:
        return "Good", issues
    return "Average", issues


def combos(headlines: list[str], descs: list[str]) -> list[dict]:
    """Three realistic 3-headline + 1-desc assemblies in different orders."""
    picks = [
        (0, 5, 9, 0),
        (1, 6, 10, 1),
        (3, 7, 8, 2),
    ]
    out = []
    used_h: set[int] = set()
    for a, b, c, d in picks:
        idxs = []
        for i in (a, b, c):
            if i < len(headlines) and i not in idxs:
                idxs.append(i)
        # fill if collision
        for i, _ in enumerate(headlines):
            if len(idxs) >= 3:
                break
            if i not in idxs:
                idxs.append(i)
        used_h.update(idxs)
        title = " · ".join(headlines[i] for i in idxs[:3])
        desc = descs[d] if d < len(descs) else descs[0]
        out.append({"title": title, "desc": desc, "heads": [headlines[i] for i in idxs[:3]]})
    return out


def pick_paused_target(paused: list[dict], perf: dict[str, dict]) -> dict | None:
    """Rewrite the weakest paused RSA. Never burn a paused ad with CTR>=12% and 20+ impr."""
    if not paused:
        return None
    scored = []
    for ad in paused:
        s = perf.get(ad["ad_id"], {"impr": 0, "clicks": 0})
        impr, clicks = s["impr"], s["clicks"]
        ctr = pct(clicks, impr)
        winnerish = ctr is not None and ctr >= 12 and impr >= 20
        scored.append((winnerish, clicks, impr, ad["ad_id"], ad))
    scored.sort(key=lambda x: (x[0], x[1], x[2], x[3]))
    for winnerish, *_rest, ad in scored:
        if not winnerish:
            return ad
    return None


def assemble_groups(payload: dict) -> list[dict]:
    inv = defaultdict(list)
    for market in ("US", "AU"):
        for ad in payload["inventory"][market]:
            if ad["campaign_status"] != "ENABLED" or ad["ad_group_status"] != "ENABLED":
                continue
            inv[(market, ad["campaign"], ad["ad_group"])].append(ad)

    rsa_perf: dict[str, dict] = defaultdict(lambda: {"impr": 0, "clicks": 0, "conv": 0.0, "cost": 0.0, "l2": {"impr": 0, "clicks": 0, "conv": 0.0, "cost": 0.0}})
    for market in ("US", "AU"):
        for r in payload["rsa_daily"][market]:
            s = rsa_perf[r["ad_id"]]
            s["impr"] += r["impressions"]
            s["clicks"] += r["clicks"]
            s["conv"] += r["conversions"]
            s["cost"] += r["cost"]
            if r["date"] in LAST2:
                s["l2"]["impr"] += r["impressions"]
                s["l2"]["clicks"] += r["clicks"]
                s["l2"]["conv"] += r["conversions"]
                s["l2"]["cost"] += r["cost"]

    kws = defaultdict(list)
    for market in ("US", "AU"):
        rolled = defaultdict(lambda: {"impr": 0, "clicks": 0, "conv": 0.0, "cost": 0.0})
        for r in payload["keywords"][market]:
            key = (market, r["campaign"], r["ad_group"], r["keyword"].lower())
            s = rolled[key]
            s["impr"] += r["impressions"]
            s["clicks"] += r["clicks"]
            s["conv"] += r["conversions"]
            s["cost"] += r["cost"]
            s["keyword"] = r["keyword"]
            s["match"] = r["match"]
        for (market, camp, ag, _), s in rolled.items():
            kws[(market, camp, ag)].append(s)

    terms = defaultdict(list)
    for market in ("US", "AU"):
        rolled = defaultdict(lambda: {"impr": 0, "clicks": 0, "conv": 0.0, "cost": 0.0})
        for r in payload["search_terms"][market]:
            key = (market, r["campaign"], r["ad_group"], r["search_term"].lower())
            s = rolled[key]
            s["impr"] += r["impressions"]
            s["clicks"] += r["clicks"]
            s["conv"] += r["conversions"]
            s["cost"] += r["cost"]
            s["term"] = r["search_term"]
            s["status"] = r["status"]
        for (market, camp, ag, _), s in rolled.items():
            terms[(market, camp, ag)].append(s)

    assets = defaultdict(list)
    for market in ("US", "AU"):
        rolled = defaultdict(lambda: {"impr": 0, "clicks": 0, "conv": 0.0})
        for r in payload["assets_daily"][market]:
            key = (market, r["campaign"], r["ad_group"], r["field_type"], r["text"])
            s = rolled[key]
            s["impr"] += r["impressions"]
            s["clicks"] += r["clicks"]
            s["conv"] += r["conversions"]
            s["text"] = r["text"]
            s["field_type"] = r["field_type"]
            s["label"] = r.get("performance_label") or ""
        for (market, camp, ag, _, _), s in rolled.items():
            assets[(market, camp, ag)].append(s)

    by_spec = {(c["market"], c["campaign"], c["ad_group"]): c for c in CHALLENGERS}

    groups = []
    for key, ads in sorted(inv.items(), key=lambda x: (x[0][0] != "US", x[0][1], x[0][2])):
        market, camp, ag = key
        enabled = [a for a in ads if a["status"] == "ENABLED"]
        paused = [a for a in ads if a["status"] == "PAUSED"]
        url = ""
        if enabled:
            url = (enabled[0].get("final_urls") or [""])[0]
        elif paused:
            url = (paused[0].get("final_urls") or [""])[0]

        en_perf = []
        launch = {"impr": 0, "clicks": 0, "conv": 0.0, "cost": 0.0}
        l2 = {"impr": 0, "clicks": 0, "conv": 0.0, "cost": 0.0}
        best = None
        for ad in enabled:
            s = rsa_perf.get(ad["ad_id"], {"impr": 0, "clicks": 0, "conv": 0.0, "cost": 0.0, "l2": {"impr": 0, "clicks": 0, "conv": 0.0, "cost": 0.0}})
            row = {
                "ad_id": ad["ad_id"],
                "path": f"{ad.get('path1','')}/{ad.get('path2','')}",
                "headlines": [h["text"] for h in ad.get("headlines") or []],
                "descriptions": [d["text"] for d in ad.get("descriptions") or []],
                "impr": s["impr"],
                "clicks": s["clicks"],
                "conv": s["conv"],
                "cost": round(s["cost"], 2),
                "ctr": pct(s["clicks"], s["impr"]),
                "l2": {
                    "impr": s["l2"]["impr"],
                    "clicks": s["l2"]["clicks"],
                    "ctr": pct(s["l2"]["clicks"], s["l2"]["impr"]),
                },
            }
            en_perf.append(row)
            for k in ("impr", "clicks", "conv", "cost"):
                launch[k] += s[k]
                l2[k] += s["l2"][k]
            if best is None or (row["impr"], row["clicks"]) > (best["impr"], best["clicks"]):
                best = row
        launch["ctr"] = pct(launch["clicks"], launch["impr"])
        l2["ctr"] = pct(l2["clicks"], l2["impr"])
        launch["cost"] = round(launch["cost"], 2)

        kw_rows = sorted(kws.get(key, []), key=lambda x: (-x["clicks"], -x["impr"]))[:8]
        st_rows = sorted(terms.get(key, []), key=lambda x: (-x["clicks"], -x["cost"], -x["impr"]))[:8]
        converted = [t for t in terms.get(key, []) if t["conv"] > 0]
        asset_rows = sorted(assets.get(key, []), key=lambda x: (-x["conv"], -(pct(x["clicks"], x["impr"]) or 0), -x["impr"]))
        best_assets = [a for a in asset_rows if a["field_type"] == "HEADLINE" and a["impr"] >= 8][:8]
        best_desc_assets = [a for a in asset_rows if a["field_type"] == "DESCRIPTION" and a["impr"] >= 8][:8]
        conv_assets = [a for a in asset_rows if a["conv"] > 0][:8]

        spec = by_spec.get(key)
        leave = LEAVE_REASONS.get((market, ag))
        existing_heads = {h["text"] for ad in enabled for h in ad.get("headlines") or []}

        card: dict = {
            "market": market,
            "campaign": camp,
            "ad_group": ag,
            "ad_group_id": (enabled or paused or [{}])[0].get("ad_group_id", ""),
            "enabled_rsas": len(enabled),
            "paused_rsas": len(paused),
            "total_rsas": len(ads),
            "final_url": url,
            "launch": launch,
            "last2": l2,
            "enabled_ads": en_perf,
            "best_rsa": best,
            "keywords": kw_rows,
            "search_terms": st_rows,
            "converted_queries": converted,
            "best_assets": best_assets,
            "best_desc_assets": best_desc_assets,
            "conv_assets": conv_assets,
            "challenger": None,
            "status": "leave",
            "status_label": "Insufficient evidence—leave alone",
            "leave_why": None,
            "replacement_hint": None,
        }

        if leave:
            card["status"] = leave["status"]
            card["status_label"] = (
                "Insufficient evidence—leave alone"
                if "Brand" not in ag and "Already 3" not in leave["why"]
                else ("Insufficient evidence—leave alone" if "Brand" in ag else "Insufficient evidence—leave alone")
            )
            if "Brand" in ag:
                card["status_label"] = "Insufficient evidence—leave alone"
            if "Already 3" in leave["why"]:
                card["status_label"] = "Insufficient evidence—leave alone"
            card["leave_why"] = leave["why"]
            card["replacement_hint"] = leave.get("replacement_hint")
            groups.append(card)
            continue

        if not spec:
            card["leave_why"] = "No challenger written this pass — evidence too thin or already covered."
            groups.append(card)
            continue

        hs, ds = spec["headlines"], spec["descriptions"]
        issues = []
        if len(hs) != 15 or len(ds) != 4:
            issues.append("need 15 headlines + 4 descriptions")
        for h in hs:
            if len(h) > 30:
                issues.append(f"headline {len(h)}: {h}")
        for d in ds:
            if len(d) > 90:
                issues.append(f"desc {len(d)}: {d}")
        if len(set(hs)) != 15 or len(set(ds)) != 4:
            issues.append("duplicates in proposed assets")
        overlap = [h for h in hs if h in existing_heads]
        for i, a in enumerate(hs):
            for b in hs[i + 1 :]:
                if near_dup(a, b):
                    issues.append(f"near-dup: {a!r} / {b!r}")
                    break
        qn = sum(x.count("?") for x in hs + ds)
        bn = sum(x.count("!") for x in hs + ds)
        if qn > 2 or bn > 1:
            issues.append("too many ? or !")
        if spec["market"] == "US" and any("{KeyWord" in x or "{KEYWORD" in x for x in hs + ds):
            issues.append("US DKI is unsafe (VA can mean Virginia)")
        if spec["market"] == "US" and re.search(r"\bVA\b", " ".join(hs)):
            issues.append("US headline uses VA — spell out Virtual Assistant")

        kw_texts = [k["keyword"] for k in kw_rows]
        strength, s_issues = predict_strength(hs, ds, kw_texts)
        issues.extend(s_issues)

        target = pick_paused_target(paused, rsa_perf)
        if len(enabled) >= 3:
            card["status"] = "leave"
            card["status_label"] = "Insufficient evidence—leave alone"
            card["leave_why"] = "Already 3 enabled RSAs. Challenger copy was drafted as a future replacement only."
            card["replacement_hint"] = "Do not add a fourth RSA."
            groups.append(card)
            continue

        api_action = "create"
        paused_id = None
        if len(ads) >= 3:
            api_action = "update_paused"
            paused_id = target["ad_id"] if target else (paused[0]["ad_id"] if paused else None)
            if not paused_id:
                issues.append("at 3-ad cap with no paused RSA to rewrite")

        status = spec["status"]
        if spec.get("claims"):
            status = "needs_claim"
        if strength == "Average":
            status = "needs_claim"
            issues.append(f"predicted Ad Strength is {strength}")
        if any(
            s in i
            for i in issues
            for s in ("headline ", "desc ", "duplicates", "US DKI", "US headline uses VA", "need 15", "near-dup")
        ):
            status = "needs_claim"

        label = {
            "ready": "Ready for review",
            "needs_claim": "Needs claim confirmation",
            "leave": "Insufficient evidence—leave alone",
        }[status]

        comp = COMPETITORS.get(spec.get("cluster") or "", {})
        card["status"] = status
        card["status_label"] = label
        card["challenger"] = {
            "headlines": [{"text": h, "n": len(h)} for h in hs],
            "descriptions": [{"text": d, "n": len(d)} for d in ds],
            "path1": spec["path1"],
            "path2": spec["path2"],
            "final_url": url or spec.get("final_url") or "",
            "predicted_strength": strength,
            "preflight_issues": issues,
            "combos": combos(hs, ds),
            "why_ctr": spec["why_ctr"],
            "why_cvr": spec["why_cvr"],
            "new_pct": spec.get("new_pct", 35),
            "claims": spec.get("claims") or [],
            "proven_overlap": overlap,
            "lp": spec.get("lp"),
            "competitors": comp,
            "api_action": api_action,
            "paused_ad_id": paused_id,
            "paused_headline": (target["headlines"][0]["text"] if target else None),
        }
        groups.append(card)
    return groups


def serp_html(combo: dict, url: str, path1: str, path2: str) -> str:
    path = f"{HOST}/{path1}/{path2}" if path1 else HOST
    display = url.replace("https://", "").replace("http://", "")
    crumbs = ""
    if path1:
        crumbs = f"<span> › {esc(path1)}" + (f" › {esc(path2)}" if path2 else "") + "</span>"
    return f"""
    <div class="serp">
      <div class="serp-cite">
        <span class="serp-favicon" aria-hidden="true">V</span>
        <div class="serp-cite-meta">
          <p class="serp-site">Virtual Coworker <span class="serp-ad">Sponsored</span></p>
          <p class="serp-url">{esc(display)}{crumbs}</p>
        </div>
      </div>
      <p class="serp-title">{esc(combo.get("title") or "")}</p>
      <p class="serp-desc">{esc(combo.get("desc") or "")}</p>
      <p class="serp-path-note">{esc(path)}</p>
    </div>"""


def split_path(path: str) -> tuple[str, str]:
    parts = [p for p in (path or "").strip("/").split("/") if p]
    return (parts[0] if parts else "", parts[1] if len(parts) > 1 else "")


def preview_combo_for_group(g: dict) -> dict:
    """Typical Google mix: strongest headlines + strongest description from this RSA."""
    best = g.get("best_rsa") or {}
    rsa_heads = list(best.get("headlines") or [])
    rsa_descs = list(best.get("descriptions") or [])
    if not rsa_heads:
        ads = g.get("enabled_ads") or []
        if ads:
            rsa_heads = list(ads[0].get("headlines") or [])
            rsa_descs = list(ads[0].get("descriptions") or [])
    head_set, desc_set = set(rsa_heads), set(rsa_descs)

    def is_dki(text: str) -> bool:
        return "{" in text

    ranked_h: list[str] = []
    for a in g.get("best_assets") or []:
        t = str(a.get("text") or "")
        if t and t in head_set and t not in ranked_h and not is_dki(t):
            ranked_h.append(t)
        if len(ranked_h) >= 3:
            break
    for h in rsa_heads:
        if len(ranked_h) >= 3:
            break
        if h not in ranked_h and not is_dki(h):
            ranked_h.append(h)
    for h in rsa_heads:
        if len(ranked_h) >= 3:
            break
        if h not in ranked_h:
            ranked_h.append(h)
    ranked_d: list[str] = []
    for a in g.get("best_desc_assets") or []:
        t = str(a.get("text") or "")
        if t and t in desc_set and t not in ranked_d:
            ranked_d.append(t)
        if ranked_d:
            break
    if not ranked_d and rsa_descs:
        ranked_d = [rsa_descs[0]]
    return {
        "title": " · ".join(ranked_h[:3]),
        "desc": ranked_d[0] if ranked_d else "",
        "heads": ranked_h[:3],
    }


def rank_assets(
    groups: list[dict], source: str, field_type: str, *, min_impr: int, limit: int
) -> list[tuple[str, float, int, str]]:
    rows: list[tuple[float, int, str, str]] = []
    for g in groups:
        for a in g.get(source) or []:
            if str(a.get("field_type") or "").upper() != field_type:
                continue
            himpr = int(a.get("impr") or 0)
            hclicks = int(a.get("clicks") or 0)
            if himpr < min_impr:
                continue
            hctr = round(100.0 * hclicks / himpr, 1) if himpr else 0.0
            rows.append((hctr, himpr, str(a.get("text") or ""), str(g.get("ad_group") or "")))
    rows.sort(key=lambda r: (-r[0], -r[1]))
    seen: set[str] = set()
    out: list[tuple[str, float, int, str]] = []
    for hctr, himpr, text, ag in rows:
        key = text.lower().strip()
        if not text or key in seen:
            continue
        seen.add(key)
        out.append((text, hctr, himpr, ag))
        if len(out) >= limit:
            break
    return out


def asset_rank_html(rows: list[tuple[str, float, int, str]]) -> str:
    if not rows:
        return '<p class="muted">None in this window.</p>'
    items = []
    for text, hctr, himpr, ag in rows:
        items.append(
            f"<li><span class='copy'>{esc(text)}</span>"
            f"<span class='meta'>{hctr:.1f}% CTR · {himpr:,} impr · {esc(ag)}</span></li>"
        )
    return f'<ol class="asset-rank">{"".join(items)}</ol>'


def best_rsa_html(g: dict) -> str:
    best = g.get("best_rsa")
    if not best:
        return "<p class='muted'>No enabled RSA served in the clean window.</p>"
    combo = preview_combo_for_group(g)
    path1, path2 = split_path(str(best.get("path") or ""))
    serp = serp_html(combo, g.get("final_url") or "", path1, path2)
    heads = "".join(f"<li>{esc(h)}</li>" for h in (best.get("headlines") or []))
    descs = "".join(f"<li>{esc(d)}</li>" for d in (best.get("descriptions") or []))
    return (
        f"<p class='best-ad'><strong>Ad {esc(best['ad_id'])}</strong> · "
        f"{best['impr']:,} impr · {best['clicks']} clicks · {esc(ctr_s(best['clicks'], best['impr']))} CTR</p>"
        f"{serp}"
        f"<details class='asset-details'><summary>All headlines and descriptions in this ad</summary>"
        f"<div class='cols'><div><p class='kicker'>Headlines</p><ol class='assets'>{heads}</ol></div>"
        f"<div><p class='kicker'>Descriptions</p><ol class='assets'>{descs}</ol></div></div></details>"
    )


def chip_row(items: list[str], cls: str = "") -> str:
    if not items:
        return '<p class="muted">None in this window.</p>'
    return '<div class="chips">' + "".join(f'<span class="chip {cls}">{esc(i)}</span>' for i in items) + "</div>"


def winners_html(groups: list[dict], conv_leaders: list[dict] | None = None) -> str:
    """Conversion-weighted winners first; CTR fillers after. Headline/desc ranks prefer converting groups."""
    conv_map: dict[tuple[str, str], dict] = {}
    for row in conv_leaders or []:
        key = (str(row.get("market") or "").upper(), str(row.get("ad_group") or ""))
        if key[0] and key[1]:
            conv_map[key] = row

    # Prefer Ads conversions when provided; else fall back to launch-window conv/CTR.
    scored: list[tuple[float, float, int, dict, dict | None]] = []
    for g in groups:
        launch = g.get("launch") or {}
        impr = int(launch.get("impr") or 0)
        key = (str(g.get("market") or "").upper(), str(g.get("ad_group") or ""))
        live = conv_map.get(key)
        conv = float((live or {}).get("conv") or launch.get("conv") or 0)
        ctr = float((live or {}).get("ctr") or launch.get("ctr") or 0)
        clicks = int((live or {}).get("clicks") or launch.get("clicks") or 0)
        if conv <= 0 and impr < 40:
            continue
        scored.append((conv, ctr, clicks if live else impr, g, live))
    scored.sort(key=lambda r: (-r[0], -r[1], -r[2]))
    top = scored[:8]
    if not top:
        return ""

    cards = []
    for conv, ctr, vol, g, live in top:
        launch = g.get("launch") or {}
        clicks = int((live or {}).get("clicks") or launch.get("clicks") or 0)
        impr = int((live or {}).get("impr") or launch.get("impr") or 0)
        best = g.get("best_rsa") or {}
        combo = preview_combo_for_group(g)
        path1, path2 = split_path(str(best.get("path") or ""))
        serp = serp_html(combo, g.get("final_url") or "", path1, path2)
        aid = f"{g['market'].lower()}-{g['ad_group'].lower().replace('_', '-')}"
        cls = "win-card conv" if conv > 0 else "win-card ctr-only"
        tag = (
            "<p class='win-tag'>Ads conversion</p>"
            if conv > 0
            else "<p class='win-tag muted'>CTR only · 0 Ads conv</p>"
        )
        kpi = (
            f"<p class='win-kpi'><b class='conv'>{conv:g}</b> Ads conv · {clicks:,} clicks · {ctr:.1f}% CTR"
            + (f" · {impr:,} impr" if impr else "")
            + "</p>"
            if conv > 0
            else f"<p class='win-kpi'><b>{ctr:.1f}%</b> CTR · {impr:,} impr · {clicks:,} clicks</p>"
        )
        cards.append(
            f"<a class='{cls}' href='#{esc(aid)}'>"
            + tag
            + f"<p class='win-ag'>{esc(g['market'])} · {esc(g['ad_group'])}</p>"
            + kpi
            + serp
            + "</a>"
        )

    head_rows = rank_assets(groups, "best_assets", "HEADLINE", min_impr=20, limit=10)
    desc_rows = rank_assets(groups, "best_desc_assets", "DESCRIPTION", min_impr=20, limit=8)

    return f"""
      <section class="panel winners" id="winners">
        <div class="panel-hd"><p class="kicker">Heavyweight conversions</p><h2>Winners — ads that got conversions</h2></div>
        <div class="panel-bd">
          <p>Rank is <strong>Ads conversions first</strong>, then CTR for filler. Sales quality still outranks raw Ads tags — see <a href="executive">Executive</a> and <a href="aug18-conversions">Aug 18 conversions</a>.</p>
          <div class="win-grid">{"".join(cards)}</div>
          <p class="kicker">Assets doing the best</p>
          <p class="tiny">These are the individual lines inside the ads — not a second scoreboard. One click can count on several lines. Prefer lines from converting groups when choosing what to keep.</p>
          <div class="asset-rank-grid">
            <div>
              <p class="kicker">Headlines</p>
              {asset_rank_html(head_rows)}
            </div>
            <div>
              <p class="kicker">Descriptions</p>
              {asset_rank_html(desc_rows)}
            </div>
          </div>
        </div>
      </section>
"""


def metric_pills(m: dict, prefix: str) -> str:
    return (
        f'<div class="pills">'
        f'<span><b>{m.get("impr", 0):,}</b> impr</span>'
        f'<span><b>{m.get("clicks", 0):,}</b> clicks</span>'
        f'<span><b>{ctr_s(m.get("clicks",0), m.get("impr",0))}</b> CTR</span>'
        f'<span><b>{m.get("conv", 0):g}</b> conv*</span>'
        f'<span><b>{money(m.get("cost", 0))}</b></span>'
        f"</div>"
        f'<p class="tiny">{esc(prefix)}</p>'
    )


def attach_post(groups: list[dict], post: dict | None) -> None:
    if not post:
        return
    by_key = {(r["market"], r["ad_group"]): r for r in post.get("jobs") or []}
    for g in groups:
        rec = by_key.get((g["market"], g["ad_group"]))
        if rec:
            g["post"] = rec


def post_outcome(g: dict) -> str | None:
    rec = g.get("post")
    if not rec:
        return None
    if rec.get("enabled"):
        return "enabled"
    if rec.get("error"):
        return "failed"
    if rec.get("copy_ok") and rec.get("left_paused"):
        return "paused"
    if rec.get("copy_ok"):
        return "posted"
    return "failed"


def render(groups: list[dict], meta: dict, conv_leaders: list[dict] | None = None) -> str:
    ready = sum(1 for g in groups if g["status"] == "ready")
    claim = sum(1 for g in groups if g["status"] == "needs_claim")
    leave = sum(1 for g in groups if g["status"] == "leave")
    posted = meta.get("post") or {}
    counts = posted.get("counts") or {}
    uploaded = bool(posted)
    enable_pass = (posted.get("enable_pass") or {}) if posted else {}
    all_pending = bool(enable_pass.get("all_pending"))
    override_pending = bool(enable_pass.get("override_pending"))
    toc = []
    sections = []
    for g in groups:
        aid = f"{g['market'].lower()}-{g['ad_group'].lower().replace('_', '-')}"
        outcome = post_outcome(g)
        toc_cls = f"toc-{outcome}" if outcome else f"toc-{g['status']}"
        toc_em = {
            "enabled": "Enabled",
            "paused": "Paused",
            "failed": "Failed",
            "posted": "Posted",
        }.get(outcome) or (
            g["status_label"].split("—")[0] if "—" in g["status_label"] else g["status_label"].split()[0]
        )
        toc.append(
            f'<a class="{toc_cls}" href="#{aid}">{esc(g["market"])} · {esc(g["ad_group"])} '
            f"<em>{esc(toc_em)}</em></a>"
        )
        ch = g.get("challenger")
        kw_chips = [
            f'{k["keyword"]} ({k["clicks"]}c · {ctr_s(k["clicks"], k["impr"])})'
            for k in g["keywords"][:6]
        ]
        st_chips = []
        for t in g["search_terms"][:6]:
            flag = " · excl" if str(t.get("status", "")).startswith("EXCLUD") else ""
            st_chips.append(f'{t["term"]} ({t["clicks"]}c{flag})')
        asset_chips = [
            f'{a["text"]} · {ctr_s(a["clicks"], a["impr"])} · {a["impr"]} impr'
            for a in g["best_assets"][:6]
        ]
        desc_chips = [
            f'{a["text"]} · {ctr_s(a["clicks"], a["impr"])} · {a["impr"]} impr'
            for a in (g.get("best_desc_assets") or [])[:5]
        ]
        conv_chips = [
            f'{a["text"]} · {a["conv"]:g} assoc. · {a["field_type"].title()}'
            for a in g["conv_assets"]
        ] or ["None in the clean window — conversions are not additive across assets."]

        best_html = best_rsa_html(g)

        proposed = ""
        if ch:
            hl = "".join(
                f"<li><span class='copy'>{esc(h['text'])}</span> <span class='len {('ok' if h['n']<=30 else 'bad')}'>{h['n']}</span></li>"
                for h in ch["headlines"]
            )
            de = "".join(
                f"<li><span class='copy'>{esc(d['text'])}</span> <span class='len {('ok' if d['n']<=90 else 'bad')}'>{d['n']}</span></li>"
                for d in ch["descriptions"]
            )
            serps = "".join(serp_html(c, ch["final_url"], ch["path1"], ch["path2"]) for c in ch["combos"])
            issues = ch["preflight_issues"]
            issue_html = (
                "<ul class='issues'>" + "".join(f"<li>{esc(i)}</li>" for i in issues) + "</ul>"
                if issues
                else "<p class='ok-line'>Preflight clear for character limits, duplicates, and predicted Excellent.</p>"
            )
            claims = ch["claims"]
            claim_html = (
                "<ul class='claims'>" + "".join(f"<li>{esc(c)}</li>" for c in claims) + "</ul>"
                if claims
                else "<p class='muted'>No extra claims beyond live site facts (since 2011, recruit/screen, you interview, payroll/employment admin, employer-only).</p>"
            )
            lp = ch.get("lp")
            if lp:
                lp_html = f"""
                <div class="lp-grid">
                  <div>
                    <p class="kicker">Live first screen</p>
                    <div class="lp-card">
                      <p class="lp-kicker">virtualcoworker.app</p>
                      <h3>{esc(lp['before_h1'])}</h3>
                      <p>{esc(lp['before_sub'])}</p>
                    </div>
                  </div>
                  <div>
                    <p class="kicker">Preview only — not deployed</p>
                    <div class="lp-card after">
                      <p class="lp-kicker">copy tweak</p>
                      <h3>{esc(lp['after_h1'])}</h3>
                      <p>{esc(lp['after_sub'])}</p>
                    </div>
                  </div>
                </div>
                <p class="tiny">{esc(lp.get('note') or '')} URL stays {esc(lp['url'])}.</p>"""
            else:
                lp_html = "<p class='muted'>First screen already continues the ad promise. No LP copy change proposed.</p>"
            comp = ch.get("competitors") or {}
            api_note = (
                f"After approval: <strong>{esc(ch['api_action'])}</strong>"
                + (f" paused RSA <code>{esc(ch['paused_ad_id'])}</code> (“{esc(ch.get('paused_headline') or '')}”)." if ch.get("paused_ad_id") else ".")
                + " Validate, keep paused unless Google reports Good or Excellent (above Average), then enable. No Editor."
            )
            post = g.get("post")
            post_box = ""
            if post:
                strength = post.get("ad_strength") or "n/a"
                live_st = post.get("live_status") or "n/a"
                cls = "enabled" if post.get("enabled") else ("failed" if post.get("error") else "paused")
                post_box = f"""
              <div class="post-box post-{cls}">
                <p class="kicker">API result · 14 Aug 2026</p>
                <p><strong>{'Enabled' if post.get('enabled') else ('Failed' if post.get('error') else 'Left paused')}</strong>
                  · Ad <code>{esc(post.get('ad_id'))}</code>
                  · Google Ad Strength <b>{esc(strength)}</b>
                  · status <b>{esc(live_st)}</b></p>
                <p class="tiny">{esc(post.get('note') or '')}</p>
                {f"<p class='tiny'>Error: {esc(post.get('error'))}</p>" if post.get('error') else ""}
                <p class="tiny">Final URL <code>{esc((post.get('live_final_urls') or [post.get('final_url')])[0] if (post.get('live_final_urls') or post.get('final_url')) else '')}</code>
                  · paths <code>{esc(post.get('live_path1') or post.get('path1') or '')}/{esc(post.get('live_path2') or post.get('path2') or '')}</code></p>
              </div>"""
            proposed = f"""
            <div class="proposed">
              {post_box}
              <div class="strength strength-{esc(ch['predicted_strength'].lower())}">
                Predicted Ad Strength <b>{esc(ch['predicted_strength'])}</b>
                · ~{ch['new_pct']}% new / {100-ch['new_pct']}% proven
              </div>
              <p class="tiny">{api_note}</p>
              <div class="cols">
                <div>
                  <p class="kicker">Headlines</p>
                  <ol class="assets">{hl}</ol>
                </div>
                <div>
                  <p class="kicker">Descriptions</p>
                  <ol class="assets">{de}</ol>
                  <p class="kicker">Paths</p>
                  <p class="mono">{esc(ch['path1'])} / {esc(ch['path2'])}</p>
                </div>
              </div>
              <p class="kicker">Three realistic combinations</p>
              {serps}
              <div class="why-grid">
                <div><p class="kicker">Why CTR</p><p>{esc(ch['why_ctr'])}</p></div>
                <div><p class="kicker">Why qualified conversion</p><p>{esc(ch['why_cvr'])}</p></div>
              </div>
              <p class="kicker">Preflight</p>
              {issue_html}
              <p class="kicker">Claims requiring confirmation</p>
              {claim_html}
              <p class="kicker">Landing-page first screen</p>
              {lp_html}
              <p class="kicker">Competitor gap (public pages, not clicked ads)</p>
              <p>{esc(comp.get('summary') or 'Cluster uses the known pack: Wing, MyOutDesk, Magic, Outsourcing Angel, 24x7 Direct, Cherry.')}</p>
              <p><strong>Own:</strong> {esc(comp.get('gap') or 'Philippines dedicated staff + you interview + consultation.')}</p>
            </div>"""
        else:
            proposed = f"<div class='leave-box'><p>{esc(g.get('leave_why') or 'Leave this ad group alone this pass.')}</p>"
            if g.get("replacement_hint"):
                proposed += f"<p class='tiny'>{esc(g['replacement_hint'])}</p>"
            proposed += "</div>"

        outcome_attr = f' data-outcome="{esc(outcome)}"' if outcome else ""
        extra_badge = ""
        if outcome == "enabled":
            extra_badge = f'<span class="badge badge-enabled">Enabled · {esc((g.get("post") or {}).get("ad_strength") or "Good+")}</span>'
        elif outcome == "paused":
            extra_badge = f'<span class="badge badge-paused">Left paused · {esc((g.get("post") or {}).get("ad_strength") or "Average or below")}</span>'
        elif outcome == "failed":
            extra_badge = '<span class="badge badge-failed">Post failed</span>'
        sections.append(f"""
        <article class="ag status-{esc(g['status'])}" id="{esc(aid)}" data-status="{esc(g['status'])}" data-market="{esc(g['market'])}"{outcome_attr}>
          <header>
            <p class="kicker">{esc(g['campaign'])} · {esc(g['market'])}</p>
            <h2>{esc(g['ad_group'])}</h2>
            <span class="badge badge-{esc(g['status'])}">{esc(g['status_label'])}</span>
            {extra_badge}
            <p class="meta">Enabled RSAs <b>{g['enabled_rsas']}</b> · Paused {g['paused_rsas']} · Total {g['total_rsas']}
              · <a href="{esc(g['final_url'] or '#')}" target="_blank" rel="noopener">{esc(g['final_url'] or 'no final URL')}</a></p>
          </header>
          <div class="ev-grid">
            <div>
              <p class="kicker">Since launch (4–13 Aug)</p>
              {metric_pills(g['launch'], 'Enabled RSAs only. Tiny samples stay directional.')}
              <p class="kicker">Last two complete days (12–13 Aug)</p>
              {metric_pills(g['last2'], 'Complete days only. Today (14 Aug) excluded.')}
            </div>
            <div>
              <p class="kicker">Best existing enabled ad</p>
              {best_html}
              <p class="kicker">Conversion-associated assets</p>
              {chip_row(conv_chips)}
              <p class="tiny">*One conversion can attach to several assets in the same ad. Not additive.</p>
            </div>
          </div>
          <p class="kicker">Top keywords (enabled, launch window)</p>
          {chip_row(kw_chips)}
          <p class="kicker">Recent search terms</p>
          {chip_row(st_chips)}
          <p class="kicker">Best-performing headlines</p>
          {chip_row(asset_chips)}
          <p class="kicker">Best-performing descriptions</p>
          {chip_row(desc_chips) if desc_chips else '<p class="muted">No description with enough impressions in this window.</p>'}
          {proposed}
        </article>""")

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <meta name="robots" content="noindex,nofollow" />
  <title>Conversion leaders · Virtual Coworker</title>
  <link rel="preconnect" href="https://fonts.googleapis.com" />
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
  <link href="https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500&family=IBM+Plex+Sans:wght@400;500;600;700&display=swap" rel="stylesheet" />
  <link rel="stylesheet" href="xray.css" />
  <style>
    .draft-banner {{ background:#1a1a1a; color:#fff; padding:1rem 1.2rem; border-radius:10px; border-left:6px solid #e8a317; margin:0 0 1.25rem; }}
    .draft-banner strong {{ color:#ffd56a; }}
    .stats {{ display:flex; flex-wrap:wrap; gap:.7rem; margin:0 0 1.25rem; }}
    .stat {{ background:#fff; border:1px solid var(--edge); padding:.7rem 1rem; border-radius:10px; min-width:7.5rem; }}
    .stat b {{ display:block; font-size:1.35rem; }}
    .filters {{ display:flex; flex-wrap:wrap; gap:.4rem; margin:0 0 1rem; }}
    .filters button {{ font:inherit; font-size:.8rem; padding:.25rem .6rem; border-radius:999px; border:1px solid var(--edge); background:#fff; cursor:pointer; }}
    .filters button.on {{ background:#1a1a1a; color:#fff; border-color:#1a1a1a; }}
    .toc {{ display:flex; flex-wrap:wrap; gap:.35rem .7rem; font-size:.82rem; }}
    .toc a {{ color:var(--ink); }}
    .toc em {{ font-style:normal; color:var(--muted); font-size:.72rem; }}
    article.ag {{ background:#fff; border:1px solid var(--edge); border-radius:14px; padding:1.1rem 1.2rem 1.3rem; margin:0 0 1.15rem; }}
    article.ag h2 {{ margin:.1rem 0 .35rem; font-size:1.25rem; }}
    article.ag.hidden {{ display:none; }}
    .badge {{ display:inline-block; font-size:.68rem; font-weight:700; letter-spacing:.03em; padding:.18rem .5rem; border-radius:4px; color:#fff; }}
    .badge-ready {{ background:#0b6e4f; }}
    .badge-needs_claim {{ background:#8a5a00; }}
    .badge-leave {{ background:#5a6270; }}
    .badge-enabled {{ background:#0b6e4f; }}
    .badge-paused {{ background:#8a5a00; }}
    .badge-failed {{ background:#8b1e1e; }}
    .post-box {{ padding:.7rem .85rem; border-radius:10px; margin:0 0 .7rem; }}
    .post-enabled {{ background:var(--tint-green); border:1px solid var(--tint-green-edge); }}
    .post-paused {{ background:var(--tint-amber); border:1px solid var(--tint-amber-edge); }}
    .post-failed {{ background:var(--tint-rose); border:1px solid var(--tint-rose-edge); }}
    .draft-banner.posted {{ border-left-color:#0b6e4f; }}
    .draft-banner.posted strong {{ color:#9be7c4; }}
    .meta, .tiny, .muted {{ color:var(--muted); }}
    .tiny {{ font-size:.78rem; }}
    .pills {{ display:flex; flex-wrap:wrap; gap:.45rem .8rem; margin:.2rem 0; }}
    .pills span {{ font-size:.88rem; }}
    .ev-grid, .cols, .why-grid, .lp-grid {{ display:grid; grid-template-columns:1fr 1fr; gap:1rem; }}
    @media (max-width:900px) {{ .ev-grid,.cols,.why-grid,.lp-grid {{ grid-template-columns:1fr; }} }}
    .chips {{ display:flex; flex-wrap:wrap; gap:.35rem; margin:.2rem 0 .7rem; }}
    .chip {{ background:var(--tint-cool); border:1px solid var(--tint-cool-edge); font-size:.75rem; padding:.15rem .45rem; border-radius:4px; }}
    .mono, .assets {{ font-family:var(--mono); font-size:.78rem; }}
    .assets {{ margin:.2rem 0 .6rem; padding-left:1.1rem; }}
    .assets .len {{ color:var(--dim); font-size:.68rem; }}
    .assets .len.bad {{ color:var(--bad); font-weight:700; }}
    .best-ad {{ margin:.2rem 0 .6rem; }}
    .serp {{
      font-family: Arial, Helvetica, sans-serif;
      border: 1px solid #dadce0;
      border-radius: 8px;
      padding: 0.85rem 1rem 0.95rem;
      margin: 0 0 0.55rem;
      background: #fff;
    }}
    .serp-cite {{ display: flex; align-items: center; gap: 0.55rem; margin: 0 0 0.28rem; }}
    .serp-favicon {{
      width: 26px; height: 26px; border-radius: 50%;
      background: #188038; color: #fff;
      font-size: 0.7rem; font-weight: 700; letter-spacing: 0;
      display: inline-flex; align-items: center; justify-content: center;
      flex-shrink: 0;
    }}
    .serp-cite-meta {{ min-width: 0; }}
    .serp-site {{
      margin: 0; font-size: 0.875rem; line-height: 1.25; color: #202124; font-weight: 400;
    }}
    .serp-ad {{ color: #70757a; font-size: 0.75rem; font-weight: 400; }}
    .serp-url {{
      margin: 0; font-size: 0.72rem; line-height: 1.3; color: #4d5156;
      white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
    }}
    .serp-url span {{ color: #4d5156; }}
    .serp-title {{
      color: #1a0dab; font-size: 1.375rem; font-weight: 600;
      line-height: 1.28; margin: 0.12rem 0 0.22rem; letter-spacing: -0.01em;
    }}
    .serp-desc {{
      color: #4d5156; font-size: 0.875rem; line-height: 1.58;
      margin: 0; font-weight: 400;
    }}
    .serp-label, .serp-path-note {{ display: none; }}
    .strength {{ padding:.45rem .7rem; border-radius:8px; margin:0 0 .6rem; font-size:.88rem; }}
    .strength-excellent {{ background:var(--tint-green); border:1px solid var(--tint-green-edge); }}
    .strength-good {{ background:var(--tint-amber); border:1px solid var(--tint-amber-edge); }}
    .strength-average {{ background:var(--tint-rose); border:1px solid var(--tint-rose-edge); }}
    .ok-line {{ color:var(--ok); }}
    .issues, .claims {{ margin:.2rem 0 .7rem; }}
    .leave-box {{ background:var(--tint-cool); border:1px dashed var(--tint-cool-edge); padding:.8rem 1rem; border-radius:10px; }}
    .lp-card {{ background:var(--tint-cool); border:1px solid var(--tint-cool-edge); padding:.8rem 1rem; border-radius:10px; }}
    .lp-card.after {{ background:var(--tint-green); border-color:var(--tint-green-edge); }}
    .lp-card h3 {{ margin:.2rem 0 .35rem; font-size:1.05rem; }}
    .lp-kicker {{ font-size:.7rem; letter-spacing:.04em; text-transform:uppercase; color:var(--muted); margin:0; }}
    .proposed {{ margin-top:.8rem; padding-top:.7rem; border-top:1px solid var(--edge-soft); }}
    .winners {{ margin: 0 0 1.15rem; }}
    .win-grid {{
      display: grid;
      grid-template-columns: repeat(auto-fill, minmax(380px, 1fr));
      gap: 0.85rem;
      margin: 0.45rem 0 0.85rem;
    }}
    .win-card {{
      display: block;
      padding: 0.75rem 0.85rem 0.9rem;
      border-radius: 10px;
      border: 1px solid var(--tint-green-edge);
      background: var(--tint-green);
      text-decoration: none;
      color: inherit;
    }}
    .win-card:hover {{ border-color: var(--accent-hot); }}
    .win-card.conv {{
      border-color: #0b6e4f;
      border-width: 2px;
      background: var(--tint-green);
      box-shadow: 0 0 0 1px rgba(11,110,79,0.12);
    }}
    .win-card.ctr-only {{
      border-color: var(--edge);
      background: var(--panel);
    }}
    .win-tag {{
      display: inline-block;
      margin: 0 0 0.25rem;
      font-size: 0.62rem;
      font-weight: 700;
      letter-spacing: 0.04em;
      text-transform: uppercase;
      color: #0b6e4f;
    }}
    .win-tag.warn {{ color: #8a5a00; }}
    .win-tag.muted {{ color: var(--muted); }}
    .win-ag {{ margin: 0; font-size: 0.78rem; font-weight: 700; color: var(--ink); }}
    .win-kpi {{ margin: 0.2rem 0 0.45rem; font-size: 0.78rem; color: var(--body); }}
    .win-kpi b.conv {{ color: #0b6e4f; font-size: 1.05rem; }}
    .win-card .serp {{ margin: 0; }}
    .asset-rank-grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 1rem; margin: 0.35rem 0 0; }}
    @media (max-width:900px) {{ .asset-rank-grid {{ grid-template-columns: 1fr; }} }}
    .asset-rank {{ margin: 0.2rem 0 0; padding-left: 1.2rem; }}
    .asset-rank li {{ margin: 0 0 0.5rem; line-height: 1.35; }}
    .asset-rank .copy {{ display: block; font-weight: 600; }}
    .asset-rank .meta {{ display: block; font-size: 0.75rem; color: var(--muted); }}
    .asset-details {{ margin: 0.35rem 0 0.55rem; }}
    .asset-details summary {{ cursor: pointer; font-size: 0.82rem; color: var(--muted); }}
    .asset-details .cols {{ margin-top: 0.45rem; }}
  </style>
</head>
<body data-page="rsa-review.html" data-foot="{'RSA challengers ON<br />George overrode PENDING' if override_pending else ('RSA challengers posted<br />Enable if Good or Excellent' if uploaded else 'RSA review only<br />Nothing uploaded')}">
  <div class="app">
    <aside class="sidebar" data-nav></aside>
    <main class="main">
      <header class="page-head">
        <p class="kicker">Ads · Google Search · {'posted 14 Aug' if uploaded else 'review only'}</p>
        <h1>Conversion leaders</h1>
        <p>Groups with Ads conversions sit first. CTR-only groups are below for copy ideas. {'The 29 posted challengers are ON even if Google still shows PENDING. Brand and existing winners were not touched.' if override_pending else ('Approved batch posted. Enabled when Google reported Good or Excellent. Brand untouched.' if uploaded else 'One new challenger per ad group that still has an open enabled slot. Nothing has been uploaded.')}</p>
        <p class="data-fresh">Ads conversions when available · launch window 4–13 Aug for article evidence · source: Google Ads RSA pull + conv leaders file</p>
      </header>

      <div class="draft-banner{' posted' if uploaded else ''}" role="status">
        {("<strong>Enabled.</strong> George overrode PENDING. The posted challengers are ON. Nothing else was paused or edited. Brand, leave-alone groups, US Hire_VA_PH, AU Recruitment_Hire_PH, and existing winners were not touched." if override_pending else ("<strong>Still PENDING.</strong> One Ad Strength pull on the 29 posted challengers. Google still reports PENDING on all 29. None enabled. Average / Poor / Pending stay paused. Brand, leave-alone, and 3-enabled groups were not touched." if all_pending else "<strong>Posted via API.</strong> Copy rewritten on the paused RSA. Enabled if Google Ad Strength is Good or Excellent (above Average). Average / Poor / Pending stay paused. Brand, leave-alone, and 3-enabled groups were not touched.")) if uploaded else "<strong>Not uploaded.</strong> Wait for George to review this page in Chrome. After an explicit OK we snapshot live ads, submit each approved RSA <em>paused</em> via the Google Ads API (update a weak paused RSA when the 3-ad cap is full), read Google’s Ad Strength, and enable if Good or Excellent. Brand, legacy, and paused campaigns are out of scope."}
      </div>

      <div class="stats">
        <div class="stat"><b>{len(groups)}</b> enabled ad groups</div>
        {f'<div class="stat"><b>{counts.get("copy_updated", 0)}</b> copy updated</div><div class="stat"><b>{counts.get("enabled_override", counts.get("enabled_above_average", counts.get("enabled_excellent", 0)))}</b> {"enabled" if override_pending else "enabled (Good+)"}</div><div class="stat"><b>{counts.get("left_paused", 0)}</b> left paused</div><div class="stat"><b>{counts.get("failed", 0)}</b> failed</div>' if uploaded else f'<div class="stat"><b>{ready}</b> ready for review</div><div class="stat"><b>{claim}</b> need confirmation</div><div class="stat"><b>{leave}</b> leave alone</div>'}
        <div class="stat"><b>{esc(meta['windows']['since_launch'])}</b> launch window</div>
        <div class="stat"><b>{esc(meta['windows']['last2'])}</b> last 2 complete days</div>
      </div>

      {winners_html(groups, conv_leaders)}

      <section class="panel">
        <div class="panel-hd"><p class="kicker">How to read this</p><h2>Evidence, then the ad</h2></div>
        <div class="panel-bd">
          <p>Clean window only: enabled <code>VC_US_S_CORE</code> / <code>ROLES</code> and <code>VC_AU_S_*</code>. Brand deferred. No agency history.</p>
          <p>Ads “conv” on an asset is not a company conversion. One booking can also show against several headlines. Do not treat it as a scoreboard.</p>
          <p>Internal directional targets remain ~12% RSA CTR and ~10% keyword CTR. Do not overreact to tiny samples. No bids, budgets, keywords, or landing-page deploys in this pass.</p>
        </div>
      </section>

      <div class="filters" id="filters">
        <button type="button" data-f="all" class="on">All</button>
        {('<button type="button" data-o="enabled">Enabled</button><button type="button" data-o="paused">Left paused</button><button type="button" data-o="failed">Failed</button>' if uploaded else '<button type="button" data-f="ready">Ready</button><button type="button" data-f="needs_claim">Needs confirmation</button>')}
        <button type="button" data-f="leave">Leave alone</button>
        <button type="button" data-m="US">US</button>
        <button type="button" data-m="AU">AU</button>
      </div>
      <nav class="toc">{"".join(toc)}</nav>

      {"".join(sections)}

      <p class="tiny">Pulled {esc(meta['generated_at'])} · {esc(meta['api_note'])} · Auction Insights fields were not available on API v25 in this pull — competitor notes are from public landing pages plus AU search terms (24x7 Direct, Outsourcing Angel).</p>
    </main>
  </div>
  <script src="nav.js?v=20260818-search-ads"></script>
  <script>
    (function () {{
      var f = "all", m = "all", o = "all";
      var btns = document.querySelectorAll("#filters button");
      function apply() {{
        document.querySelectorAll("article.ag").forEach(function (el) {{
          var okF = f === "all" || el.getAttribute("data-status") === f;
          var okM = m === "all" || el.getAttribute("data-market") === m;
          var okO = o === "all" || el.getAttribute("data-outcome") === o;
          el.classList.toggle("hidden", !(okF && okM && okO));
        }});
      }}
      btns.forEach(function (b) {{
        b.addEventListener("click", function () {{
          if (b.dataset.f) {{
            f = b.dataset.f;
            o = "all";
            document.querySelectorAll("#filters [data-f]").forEach(function (x) {{ x.classList.toggle("on", x === b); }});
            document.querySelectorAll("#filters [data-o]").forEach(function (x) {{ x.classList.remove("on"); }});
          }}
          if (b.dataset.o) {{
            o = o === b.dataset.o ? "all" : b.dataset.o;
            f = "all";
            document.querySelectorAll("#filters [data-o]").forEach(function (x) {{ x.classList.toggle("on", x.dataset.o === o); }});
            document.querySelectorAll("#filters [data-f]").forEach(function (x) {{ x.classList.toggle("on", x.dataset.f === "all"); }});
          }}
          if (b.dataset.m) {{
            m = m === b.dataset.m ? "all" : b.dataset.m;
            document.querySelectorAll("#filters [data-m]").forEach(function (x) {{ x.classList.toggle("on", x.dataset.m === m); }});
          }}
          apply();
        }});
      }});
    }})();
  </script>
</body>
</html>
"""


def main() -> int:
    payload = json.loads(EVIDENCE.read_text(encoding="utf-8"))
    groups = assemble_groups(payload)

    # Fail the build on hard copy errors in ready/needs_claim cards
    hard = []
    for g in groups:
        ch = g.get("challenger") or {}
        for i in ch.get("preflight_issues") or []:
            if any(s in i for s in ("headline ", "desc ", "duplicates", "US DKI", "US headline uses VA", "need 15")):
                hard.append(f"{g['market']} {g['ad_group']}: {i}")
    if hard:
        print("COPY ERRORS:", file=sys.stderr)
        for h in hard:
            print(" ", h, file=sys.stderr)
        return 1

    post = None
    if POST.is_file():
        post = json.loads(POST.read_text(encoding="utf-8"))
        attach_post(groups, post)
    meta = {
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC"),
        "windows": {
            "since_launch": "4–13 Aug 2026",
            "last2": "12–13 Aug 2026",
        },
        "api_note": (
            f"{payload.get('api_calls_used')} Ads API reads (plus keyword_view resume)"
            + (
                f" · enable pass {(post or {}).get('api_calls_this_pass')} calls"
                if post and (post or {}).get("api_calls_this_pass")
                else ""
            )
        ),
        "uploaded": bool(post),
        "post": {
            "generated_at": (post or {}).get("generated_at"),
            "api_calls": (post or {}).get("api_calls"),
            "api_calls_this_pass": (post or {}).get("api_calls_this_pass"),
            "mutate_items": (post or {}).get("mutate_items"),
            "counts": (post or {}).get("counts"),
            "errors": (post or {}).get("errors"),
            "enable_pass": (post or {}).get("enable_pass"),
            "banner": (post or {}).get("banner"),
        }
        if post
        else None,
    }
    OUT_HTML.parent.mkdir(parents=True, exist_ok=True)
    (OUT_JSON.parent).mkdir(parents=True, exist_ok=True)
    conv_path = REPO / "xray" / "data" / "conv-leaders-readonly.json"
    conv_leaders: list[dict] = []
    if conv_path.is_file():
        try:
            conv_leaders = list(json.loads(conv_path.read_text(encoding="utf-8")).get("rows") or [])
        except (json.JSONDecodeError, OSError):
            conv_leaders = []
    html_out = render(groups, meta, conv_leaders)
    OUT_HTML.write_text(html_out, encoding="utf-8")
    blob = {"meta": meta, "groups": groups}
    OUT_JSON.write_text(json.dumps(blob, indent=2) + "\n", encoding="utf-8")
    OUT_AUDIT.write_text(json.dumps(blob, indent=2) + "\n", encoding="utf-8")
    ready = sum(1 for g in groups if g["status"] == "ready")
    claim = sum(1 for g in groups if g["status"] == "needs_claim")
    leave = sum(1 for g in groups if g["status"] == "leave")
    print(f"Wrote {OUT_HTML.relative_to(REPO)}")
    print(f"  {len(groups)} groups · ready {ready} · needs confirmation {claim} · leave {leave}")
    for g in groups:
        if g["status"] != "leave":
            ch = g["challenger"]
            print(
                f"  {g['status']:12} {g['market']} {g['ad_group']:32} "
                f"{ch['predicted_strength']:9} {ch['api_action']} {ch.get('paused_ad_id') or ''}"
            )
            for i in ch.get("preflight_issues") or []:
                print(f"               ⚠ {i}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
