/**
 * Preview-only helpers for the trust-first US LP family.
 * Do not wire this into live /us assignment or Ads.
 */

import type { Metadata } from "next";
import {
  DEFAULT_TRUST_FIRST_VARIANT,
  TRUST_FIRST_EXPERIMENT_ID,
  TRUST_FIRST_LANDING_PAGE_TYPE,
  TRUST_FIRST_LP_VERSION,
  TRUST_FIRST_NAMESPACE,
  TRUST_FIRST_SPLIT_LIVE,
  TRUST_FIRST_VARIANTS,
  type TrustFirstPageConfig,
  type TrustFirstVariant,
} from "../config/trust-first";
import { SITE_URL } from "./seo";

export const TRUST_FIRST_VARIANT_QUERY = "v";

export function previewRobots(): NonNullable<Metadata["robots"]> {
  return {
    index: false,
    follow: false,
    nocache: true,
    noarchive: true,
    nosnippet: true,
    googleBot: {
      index: false,
      follow: false,
      noarchive: true,
      nosnippet: true,
    },
  };
}

export function previewPageMetadata(page: TrustFirstPageConfig): Metadata {
  return {
    title: `${page.title} (Preview)`,
    description: page.description,
    robots: previewRobots(),
    alternates: {
      canonical: `${SITE_URL}${page.previewPath}`,
    },
    openGraph: {
      title: page.title,
      description: page.description,
      url: `${SITE_URL}${page.previewPath}`,
      siteName: "Virtual Coworker",
      type: "website",
    },
  };
}

export function normalizeTrustFirstVariant(
  raw: string | null | undefined,
): TrustFirstVariant | null {
  if (!raw) return null;
  const v = raw.trim().toLowerCase().replace("-", "_");
  if (v === "simple" || v === "a") return "simple";
  if (v === "proof_heavy" || v === "proof" || v === "b") return "proof_heavy";
  return null;
}

/**
 * Deterministic assignment. Disabled until George approves a live split.
 * Preview uses the toolbar / ?v= override only.
 */
export function assignTrustFirstVariant(opts: {
  query?: string | null;
  seed?: string;
}): { variant: TrustFirstVariant; source: "query" | "default" | "assigned" } {
  const fromQuery = normalizeTrustFirstVariant(opts.query);
  if (fromQuery) return { variant: fromQuery, source: "query" };
  if (!TRUST_FIRST_SPLIT_LIVE) {
    return { variant: DEFAULT_TRUST_FIRST_VARIANT, source: "default" };
  }
  const seed = opts.seed || "preview";
  let h = 0;
  for (let i = 0; i < seed.length; i++) {
    h = (h * 31 + seed.charCodeAt(i)) >>> 0;
  }
  const variant: TrustFirstVariant =
    h % 2 === 0 ? "simple" : "proof_heavy";
  return { variant, source: "assigned" };
}

export function variantHref(path: string, variant: TrustFirstVariant): string {
  const url = new URL(path, "https://www.virtualcoworker.app");
  url.searchParams.set(TRUST_FIRST_VARIANT_QUERY, variant === "proof_heavy" ? "proof" : "simple");
  return `${url.pathname}?${url.searchParams.toString()}`;
}

export function isProofHeavy(variant: TrustFirstVariant): boolean {
  return variant === "proof_heavy";
}

export function previewAnalyticsMeta(
  page: TrustFirstPageConfig,
  variant: TrustFirstVariant,
) {
  return {
    market: "us",
    lp_key: page.key,
    lp_version: TRUST_FIRST_LP_VERSION,
    lp_variant: variant,
    landing_page_type: TRUST_FIRST_LANDING_PAGE_TYPE,
    experiment_id: TRUST_FIRST_EXPERIMENT_ID,
    split_running: TRUST_FIRST_SPLIT_LIVE,
    preview: true,
    intended_campaign: page.intendedCampaign,
    intended_ad_group: page.intendedAdGroup,
    proposed_production_path: page.proposedProductionPath,
  };
}

export function highlightPhrase(
  text: string,
  phrase: string,
): { before: string; accent: string; after: string } | null {
  if (!phrase) return null;
  const idx = text.toLowerCase().indexOf(phrase.toLowerCase());
  if (idx < 0) return null;
  return {
    before: text.slice(0, idx),
    accent: text.slice(idx, idx + phrase.length),
    after: text.slice(idx + phrase.length),
  };
}

/** First clause stays navy. Second clause is the light-blue pop. */
export function splitHeadline(text: string): { lead: string; accent: string } {
  const period = text.match(/^(.*?[.!?])\s+(.+)$/);
  if (period) return { lead: period[1], accent: period[2] };
  const comma = text.match(/^(.*?,)\s+(.+)$/);
  if (comma) return { lead: comma[1], accent: comma[2] };
  return { lead: text, accent: "" };
}

export { TRUST_FIRST_NAMESPACE, TRUST_FIRST_VARIANTS };
