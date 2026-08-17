/**
 * Guided-match helpers. Diagnostic events only - never Ads Primary.
 * Lead POST flags stay on the existing form_lp contract.
 */

import type { MarketId } from "../config/markets";
import type { CategorySlug } from "../config/categories";
import {
  GUIDED_MATCH_CTA_MODE,
  GUIDED_MATCH_LANDING_TYPE,
  GUIDED_MATCH_LP_SURFACE,
  firstGuidedMatchStep,
  type GuidedMatchStep,
} from "../config/guided-match";
import { LP_VERSION } from "./tracking";

export function guidedMatchLandingFlags() {
  return {
    lp_surface: GUIDED_MATCH_LP_SURFACE,
    cta_mode: GUIDED_MATCH_CTA_MODE,
    landing_type: GUIDED_MATCH_LANDING_TYPE,
    lp_variant: "",
    lp_version: LP_VERSION,
  };
}

export function guidedMatchStepIndex(
  step: GuidedMatchStep,
  lockedCategory?: CategorySlug | null,
  contactFirst = false,
): { shown: number; total: number; pct: string } {
  if (contactFirst) return { shown: 1, total: 1, pct: "100%" };
  const first = firstGuidedMatchStep(lockedCategory);
  if (first === "needs") {
    if (step === "contact") return { shown: 2, total: 2, pct: "100%" };
    return { shown: 1, total: 2, pct: "50%" };
  }
  if (step === "role") return { shown: 1, total: 3, pct: "33%" };
  if (step === "needs") return { shown: 2, total: 3, pct: "66%" };
  return { shown: 3, total: 3, pct: "100%" };
}

export function canGoBack(
  step: GuidedMatchStep,
  lockedCategory?: CategorySlug | null,
  contactFirst = false,
): boolean {
  if (contactFirst) return false;
  return step !== firstGuidedMatchStep(lockedCategory);
}

export function previousStep(
  step: GuidedMatchStep,
  lockedCategory?: CategorySlug | null,
): GuidedMatchStep {
  const first = firstGuidedMatchStep(lockedCategory);
  if (step === "contact") return "needs";
  if (step === "needs") return first === "role" ? "role" : "needs";
  return first;
}

export function diagnosticMatchPayload(opts: {
  market: MarketId;
  category?: string;
  variant?: string;
  step?: string;
  answer?: string;
  rolePreselected?: boolean;
  schedule?: string;
  positionsNeeded?: string;
  companySize?: string;
}) {
  const flags = guidedMatchLandingFlags();
  return {
    market: opts.market,
    category: opts.category || "",
    variant: opts.variant || "",
    step: opts.step || "",
    answer: opts.answer || "",
    assist_type: "guided_match",
    ads_conversion: false,
    bidding_primary: false,
    role_preselected: Boolean(opts.rolePreselected),
    schedule: opts.schedule || "",
    positions_needed: opts.positionsNeeded || "",
    company_size: opts.companySize || "",
    ...flags,
  };
}

export function shouldStartEmployerFormOnPii(alreadyFired: boolean): boolean {
  if (alreadyFired) return false;
  return true;
}

/** Role / hours chips must never count as employer_form_started. */
export function chipClickIsFormStart(): boolean {
  return false;
}
