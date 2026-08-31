"use client";

import { useEffect, useMemo } from "react";
import SiteFooter from "../components/SiteFooter";
import { resolveCareersUrl } from "../../config/markets";
import { trackEvent } from "../../lib/tracking";
import "./ph.css";

/**
 * Job-seeker interstitial — hard exit to WordPress PH careers.
 * Not a paid employer LP. Not a re-entry funnel.
 */
export default function PHHome() {
  const careers = useMemo(() => resolveCareersUrl(), []);

  useEffect(() => {
    trackEvent("job_seeker_interstitial_viewed", {
      market: "ph",
      destination: careers,
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

      <section className="ph-hero">
        <div className="ph-hero-bg" aria-hidden />
        <div className="ph-hero-inner" style={{ gridTemplateColumns: "1fr" }}>
          <div className="ph-hero-copy" style={{ maxWidth: "36rem" }}>
            <p className="ph-kicker anim-rise">Looking for work?</p>
            <h1 className="anim-rise">This hiring site is for businesses.</h1>
            <p className="ph-lead anim-rise-d1">
              Job applications live on our Philippines careers site. Continue
              there to search roles and apply - this page won’t take applications.
            </p>
            <ul className="ph-ticks anim-rise-d1">
              <li>Opens our official PH careers WordPress site</li>
              <li>Not a business hiring form</li>
              <li>Looking for a job? Apply on the careers site</li>
            </ul>
            <div className="anim-rise-d2" style={{ marginTop: "1.25rem" }}>
              <a
                href={careers}
                className="gate-submit"
                target="_blank"
                rel="noopener noreferrer"
                onClick={() =>
                  trackEvent("job_seeker_redirected", {
                    market: "ph",
                    destination: careers,
                    source: "ph_interstitial",
                    primary_eligible: false,
                  })
                }
              >
                Continue to Philippines careers →
              </a>
            </div>
          </div>
        </div>
      </section>

      <SiteFooter tone="dark" market="ph" />
    </main>
  );
}
