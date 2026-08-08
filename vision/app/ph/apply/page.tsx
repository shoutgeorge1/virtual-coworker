"use client";

import { useEffect, useMemo } from "react";
import SiteFooter from "../../components/SiteFooter";
import { resolveCareersUrl } from "../../../config/markets";
import { trackEvent } from "../../../lib/tracking";
import "../ph.css";

/** Apply route is an exit ramp — no on-host job form. */
export default function PHApply() {
  const careers = useMemo(() => resolveCareersUrl(), []);

  useEffect(() => {
    trackEvent("job_seeker_interstitial_viewed", {
      market: "ph",
      destination: careers,
      source: "ph_apply",
      primary_eligible: false,
    });
  }, [careers]);

  return (
    <main className="ph">
      <nav className="ph-nav" aria-label="Careers">
        <a
          href={careers}
          className="ph-brand"
          target="_blank"
          rel="noopener noreferrer"
          aria-label="Virtual Coworker Philippines careers (opens in new tab)"
        >
          {/* eslint-disable-next-line @next/next/no-img-element */}
          <img
            src="/brand/logo-vc.png"
            alt="Virtual Coworker"
            className="logo-img logo-img-on-dark"
          />
          <span className="ph-brand-tag">Careers</span>
        </a>
      </nav>

      <div className="ph-apply">
        <h1 className="anim-rise">Applications move to Philippines careers</h1>
        <p className="anim-rise-d1">
          We don’t collect job applications on this hiring microsite. Continue to
          our Philippines careers site to apply — opens in a new tab.
        </p>
        <a
          href={careers}
          className="gate-submit anim-rise-d2"
          target="_blank"
          rel="noopener noreferrer"
          onClick={() =>
            trackEvent("job_seeker_redirected", {
              market: "ph",
              destination: careers,
              source: "ph_apply",
              primary_eligible: false,
            })
          }
        >
          Go to Philippines careers →
        </a>
        <p className="ph-gate-note" style={{ marginTop: "1.5rem" }}>
          Businesses hiring staff: use the US or Australia pages in the footer.
        </p>
      </div>

      <SiteFooter tone="dark" market="ph" />
    </main>
  );
}
