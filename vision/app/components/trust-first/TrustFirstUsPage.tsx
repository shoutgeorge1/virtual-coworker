import type { Metadata } from "next";
import {
  isTrustFirstPageKey,
  trustFirstPage,
  type TrustFirstPageKey,
} from "../../../config/trust-first";
import { buildPageMetadata } from "../../../lib/seo";
import { assignTrustFirstVariant } from "../../../lib/trust-first";
import TrustFirstLanding from "./TrustFirstLanding";

/** Isolated TF test routes only. Live /us and role LPs stay on StaffingBaselineLanding. */
export const TRUST_FIRST_ISOLATED_KEYS = [
  "us",
  "philippines-virtual-assistants",
  "real-estate",
  "bookkeeping",
] as const;

export function trustFirstProductionMetadata(pageKey: TrustFirstPageKey): Metadata {
  const page = trustFirstPage(pageKey);
  const isolatedTest = page.productionPath.startsWith("/us/tf");
  return buildPageMetadata({
    title: page.title,
    description: page.description,
    path: page.productionPath,
    indexable: !isolatedTest,
    ogImage: "/brand/hero-us-2026.jpg",
  });
}

/**
 * Isolated trust-first surface. No preview toolbar. Forms POST /api/lead.
 * /us/tf/* is noindex (ads test). /us/philippines-virtual-assistants is a new URL.
 */
export default async function TrustFirstUsPage({
  pageKey,
  searchParams,
}: {
  pageKey: TrustFirstPageKey;
  searchParams?: Promise<{ v?: string }>;
}) {
  if (!isTrustFirstPageKey(pageKey)) return null;
  const query = searchParams ? await searchParams : {};
  const page = trustFirstPage(pageKey);
  const { variant } = assignTrustFirstVariant({ query: query.v });
  return <TrustFirstLanding page={page} variant={variant} surface="production" />;
}
