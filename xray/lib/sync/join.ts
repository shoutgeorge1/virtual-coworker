/**
 * Join paid Ads / GA4 / Zoho rows using the strongest available identifier.
 * Priority: GCLID → UTM campaign/ad group/keyword → date+landing page (fallback).
 */

export type JoinMethod =
  | "gclid"
  | "utm_campaign_adgroup_keyword"
  | "date_landing_page_fallback"
  | "unjoined";

export type Joinable = {
  gclid?: string | null;
  utm_campaign?: string | null;
  utm_content?: string | null;
  utm_term?: string | null;
  ad_group?: string | null;
  keyword?: string | null;
  date?: string | null;
  landing_page?: string | null;
};

function clean(v: string | null | undefined): string {
  return (v || "").trim();
}

export function normalizeGclid(raw: string | null | undefined): string | null {
  const v = clean(raw);
  if (!v || v.toLowerCase() === "null" || v.toLowerCase() === "none") return null;
  return v;
}

/**
 * Resolve join method + stable key for a CRM / analytics row.
 * Keys never include PII; GCLID is hashed for storage keys when present.
 */
export function resolveJoin(row: Joinable): {
  method: JoinMethod;
  key: string;
  label: string;
} {
  const gclid = normalizeGclid(row.gclid);
  if (gclid) {
    return {
      method: "gclid",
      key: `gclid:${fingerprint(gclid)}`,
      label: "GCLID",
    };
  }

  const campaign = clean(row.utm_campaign);
  const adGroup = clean(row.ad_group || row.utm_content);
  const keyword = clean(row.keyword || row.utm_term);
  if (campaign && adGroup && keyword) {
    const key = `utm:${norm(campaign)}|${norm(adGroup)}|${norm(keyword)}`;
    return {
      method: "utm_campaign_adgroup_keyword",
      key,
      label: "UTM campaign / ad group / keyword",
    };
  }

  const date = clean(row.date);
  const lp = clean(row.landing_page);
  if (date && lp) {
    return {
      method: "date_landing_page_fallback",
      key: `inferred:${date}|${norm(lp)}`,
      // Guardrail: never treat date+LP as a confirmed lead-to-click match.
      label: "Inferred (date + landing page — not a confirmed click match)",
    };
  }

  return {
    method: "unjoined",
    key: "unjoined",
    label: "Unjoined",
  };
}

function norm(s: string): string {
  return s.toLowerCase().replace(/\s+/g, " ").trim();
}

/** Short non-reversible fingerprint so logs/keys never store raw GCLID. */
export function fingerprint(value: string): string {
  let h = 2166136261;
  for (let i = 0; i < value.length; i++) {
    h ^= value.charCodeAt(i);
    h = Math.imul(h, 16777619);
  }
  return (h >>> 0).toString(16).padStart(8, "0");
}
