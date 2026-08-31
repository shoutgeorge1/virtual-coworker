/**
 * Job-seeker exit from the employer funnel → PH WordPress careers.
 * Always location.replace (Back must not return them to the LP gate).
 * Never counts as an employer lead. Never Ads conversion.
 */

import { DEFAULT_CAREERS_URL } from "../config/markets";
import { trackJobSeekerRedirected } from "./lp-events";
import { AUTHORITATIVE_LP_VERSION } from "../config/lp-version";

export function exitToCareers(
  careersUrl: string,
  payload: Record<string, string | number | boolean | undefined> = {},
): void {
  const url = (careersUrl || "").trim() || DEFAULT_CAREERS_URL;
  trackJobSeekerRedirected({
    market: String(payload.market || ""),
    lp_version: String(payload.lp_version || AUTHORITATIVE_LP_VERSION),
    page_path: payload.page_path ? String(payload.page_path) : undefined,
    landing_page_type: payload.landing_page_type
      ? String(payload.landing_page_type)
      : undefined,
    redirect_location: String(
      payload.redirect_location || payload.source || "careers_link",
    ),
    redirect_reason: String(payload.redirect_reason || "careers_escape"),
    destination: url,
  });
  if (typeof window === "undefined") return;
  window.location.replace(url);
}
