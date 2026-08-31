"use client";

import type { MarketId } from "../../config/markets";
import type { CategorySlug } from "../../config/categories";
import {
  GUIDED_MATCH_QUOTES,
  GUIDED_MATCH_ROLES,
  JOB_SEEKER_LINE,
  featuredQuoteIndex,
  firstGuidedMatchStep,
  marketLandingCopy,
  roleHeadline,
  roleForCategory,
} from "../../config/guided-match";
import { clientMarksForMarket } from "../../config/site";
import { DEFAULT_CAREERS_URL } from "../../config/markets";
import {
  normalizeSellFirstHeadline,
  sellFirstCopy,
  type SellFirstHeadlineId,
} from "../../config/lp-sell-first";
import { trackPhoneClick, trackEvent } from "../../lib/tracking";
import GuidedMatchGate from "./GuidedMatchGate";
import "../guided-match.css";
import "../sell-first.css";

type Props = {
  market: MarketId;
  category?: CategorySlug | null;
  variant?: string;
  careersHref?: string;
  sellFirst?: boolean;
  headlineId?: SellFirstHeadlineId;
};

export default function GuidedMatchLanding({
  market,
  category,
  variant = "",
  careersHref = DEFAULT_CAREERS_URL,
  sellFirst = false,
  headlineId = "a",
}: Props) {
  const copy = marketLandingCopy(market);
  const sell = sellFirst
    ? sellFirstCopy(market, normalizeSellFirstHeadline(headlineId))
    : null;
  const headlines = sell
    ? { h1: sell.h1, lead: sell.lead }
    : roleHeadline({ market, lockedCategory: category });
  const logos = clientMarksForMarket(market);
  const featIdx = Math.max(0, featuredQuoteIndex(category));
  const featured = GUIDED_MATCH_QUOTES[featIdx];
  const rest = GUIDED_MATCH_QUOTES.filter((_, i) => i !== featIdx);
  const lockedRole = category ? roleForCategory(category) : null;
  const needsTitle = lockedRole
    ? `Tell us about the ${lockedRole.chip.toLowerCase()} help you need`
    : "Tell us the role";

  function onPhone() {
    trackPhoneClick({
      market,
      category: category || "",
      variant: variant || "",
    });
  }

  function onCareers(
    e: React.MouseEvent<HTMLAnchorElement>,
    source = "paid_lp_footer",
  ) {
    e.preventDefault();
    trackEvent("job_seeker_redirected", {
      market,
      category: category || "",
      variant: variant || "",
      intent: "job_seeker",
      destination: careersHref,
      primary_eligible: false,
      bidding_primary: false,
      source,
    });
    window.location.replace(careersHref);
  }

  function onPrimaryCta() {
    trackEvent("primary_cta_clicked", {
      market,
      category: category || "",
      variant: variant || "",
      lp_variant: variant || "",
      headline_id: sell?.headlineId || "",
      destination: "#gate",
    });
  }

  function selectBandRole(chip: string) {
    const gate = document.getElementById("gate");
    if (category) {
      gate?.scrollIntoView({ behavior: "smooth", block: "center" });
      return;
    }
    const btn = document.querySelector(
      `.gm-gate .gm-chip`,
    ) as HTMLButtonElement | null;
    const match = Array.from(
      document.querySelectorAll<HTMLButtonElement>(".gm-gate .gm-chip"),
    ).find((el) => el.textContent?.includes(chip));
    if (match && firstGuidedMatchStep(category) === "role") {
      match.click();
    } else if (btn) {
      gate?.scrollIntoView({ behavior: "smooth", block: "center" });
    }
    window.setTimeout(() => {
      document.getElementById("gate")?.scrollIntoView({
        behavior: "smooth",
        block: "center",
      });
    }, 80);
  }

    const faqs: [string, string][] = [
    [
      "What happens after I tell you the role?",
      "A staffing specialist reviews your role, schedule and requirements, then sends a hiring brief with the recruiting path, timeline, and hourly-rate structure. Then we recruit if you are aligned. You interview on video.",
    ],
    [
      "Full-time or part-time?",
      "Both. 20 hours/week minimum. Start part-time, then scale hours as you need them. Dedicated staff, not a rotating freelancer for the afternoon.",
    ],
    [copy.hoursFaqQ, copy.hoursFaqA],
    [copy.payrollFaqQ, copy.payrollFaqA],
    [
      "How do I keep systems and data safe?",
      "You stay in control of access. Individual logins, MFA, a password manager, restricted permissions, NDAs, and endpoint security. We walk through the practical steps on the call rather than asserting that offshore is automatically safe.",
    ],
    [
      "How do rates work?",
      market === "au"
        ? "Hourly rates depend on the role, hours, seniority, and specialized or Australian/New Zealand industry experience. We’ll explain the structure in the hiring brief rather than publish a live price here."
        : "Hourly rates depend on the role, hours, and seniority. We’ll explain the structure in the hiring brief rather than publish a live price here.",
    ],
    [
      "Who is this page for?",
      "Employers hiring staff. If you are looking for work, use the Philippines careers link.",
    ],
  ];

  return (
    <div className={sellFirst ? "gm gm-sell" : "gm"}>
      <div className="gm-wrap">
        <nav className="gm-nav" aria-label="Employer hiring">
          <img src="/brand/logo-vc.png" alt="Virtual Coworker" width={148} height={30} />
          {sellFirst ? null : (
            <div className="gm-nav-links">
              <a href="#how">How it works</a>
              <a href="#roles">Roles</a>
              <a href="#stories">Stories</a>
              <a href="#gate">Hire</a>
            </div>
          )}
          <a className="gm-call" href={copy.phoneHref} onClick={onPhone}>
            {copy.phoneDisplay}
          </a>
        </nav>
      </div>

      <section className="gm-hero">
        <div className="gm-wrap gm-hero-grid">
          <div>
            <h1 data-headline={sell?.headlineId || undefined}>{headlines.h1}</h1>
            <p className="gm-lead">{headlines.lead}</p>
            {sellFirst && sell ? (
              <>
                <a
                  className="gm-hero-cta"
                  href="#gate"
                  onClick={onPrimaryCta}
                >
                  {sell.cta} →
                </a>
                <p className="gm-starline">
                  <span className="gm-stars" aria-hidden="true">
                    ★★★★★
                  </span>{" "}
                  {sell.compactProof}
                </p>
                <p className="gm-since">{sell.sinceLine}</p>
                <p className="gm-hero-seeker">
                  <a
                    href={careersHref}
                    onClick={(e) => onCareers(e, "paid_lp_hero_subordinate")}
                  >
                    {JOB_SEEKER_LINE}
                  </a>
                </p>
              </>
            ) : (
              <>
                <p className="gm-starline">
                  <span className="gm-stars" aria-hidden="true">
                    ★★★★★
                  </span>{" "}
                  {copy.googleLine} ·{" "}
                  <span className="gm-stars" aria-hidden="true">
                    ★★★★★
                  </span>{" "}
                  {copy.clutchLine}
                </p>
                <GuidedMatchGate
                  market={market}
                  category={category}
                  variant={variant}
                  careersHref={careersHref}
                />
              </>
            )}
          </div>
          <img
            className="gm-hero-photo"
            src={copy.heroSrc}
            alt={copy.heroAlt}
            width={960}
            height={1280}
            fetchPriority="high"
            decoding="async"
          />
        </div>
      </section>

      {sellFirst ? (
        <section className="gm-qualify" id="qualify">
          <div className="gm-wrap">
            <GuidedMatchGate
              market={market}
              category={category}
              variant={variant}
              careersHref={careersHref}
              quietStart
            />
          </div>
        </section>
      ) : null}

      <section className="gm-logos" aria-label="Companies we have staffed">
        <div className="gm-wrap">
          <div className="gm-logo-row">
            {logos.map((m) => (
              <img key={m.id} src={m.src} alt={m.alt || m.name} height={32} />
            ))}
          </div>
          <p className="gm-proof-meta">
            Serving employers since {copy.sinceYear} · {copy.linkedin} LinkedIn
          </p>
        </div>
      </section>

      <section className="gm-band white" id="how">
        <div className="gm-wrap">
          <h2>How hiring works</h2>
          <p className="gm-lead">
            Tell us the role. A staffing specialist reviews your staffing needs. We
            recruit after you are aligned. You interview. We handle {copy.adminLabel}.
          </p>
          <div className="gm-grid-steps">
            <div className="gm-step">
              <b>1. You tell us</b>
              <p>Role, hours, and how many people. We turn that into a hiring brief.</p>
            </div>
            <div className="gm-step">
              <b>2. We scope</b>
              <p>
                A staffing specialist reviews your role, schedule and requirements.
              </p>
            </div>
            <div className="gm-step">
              <b>3. We recruit</b>
              <p>
                Philippines team sources and vets after you are aligned. You conduct a
                video interview with your chosen candidate.
              </p>
            </div>
            <div className="gm-step">
              <b>4. We stay</b>
              <p>
                You choose who starts. We handle onboarding, {copy.adminLabel}, and the
                time tracker.
              </p>
            </div>
          </div>
        </div>
      </section>

      <section className="gm-band mist" id="roles">
        <div className="gm-wrap">
          <h2>Roles we hire for</h2>
          <p className="gm-lead">Dedicated staff, not a rotating freelance pool.</p>
          <div className="gm-role-grid">
            {GUIDED_MATCH_ROLES.map((r) => {
              const on = (lockedRole?.chip || "") === r.chip;
              return (
                <button
                  key={r.id}
                  type="button"
                  className="gm-role-card"
                  aria-pressed={on}
                  onClick={() => selectBandRole(r.chip)}
                >
                  <b>
                    {on ? <span className="gm-check">✓ </span> : null}
                    {r.chip}
                  </b>
                  <span>{r.blurb}</span>
                </button>
              );
            })}
          </div>
        </div>
      </section>

      <section className="gm-band sand" id="why">
        <div className="gm-wrap gm-split">
          <div>
            <h2>Why companies stay with Virtual Coworker</h2>
            <div className="gm-why-grid">
              <div>
                <h3>Since {copy.sinceYear}</h3>
                <p>
                  A staffing company, not a gig app. US and Australian offices.
                  Philippines recruitment hub.
                </p>
              </div>
              <div>
                <h3>Your hours</h3>
                <p>
                  Dedicated staff recruited to {copy.hoursDefault.toLowerCase()}.
                  Full-time or part-time. 20 hours/week minimum.
                </p>
              </div>
              <div>
                <h3>You choose</h3>
                <p>
                  You interview on video. Nobody is assigned to you as a leftover
                  profile.
                </p>
              </div>
              <div>
                <h3>We employ</h3>
                <p>
                  Once you hire, we handle {copy.adminLabel} and stay on the account.
                </p>
              </div>
            </div>
          </div>
          <img
            className="gm-scene"
            src={copy.sceneSrc}
            alt={copy.sceneAlt}
            width={1200}
            height={800}
            loading="lazy"
          />
        </div>
      </section>

      <section className="gm-band white" id="people">
        <div className="gm-wrap">
          <h2>The team that recruits your hire</h2>
          <p className="gm-lead">
            Philippines recruitment floor. US and Australian offices behind the
            account.
          </p>
          <img
            className="gm-wide"
            src={copy.teamSrc}
            alt={copy.teamAlt}
            width={1600}
            height={900}
            loading="lazy"
          />
        </div>
      </section>

      <section className="gm-band mist" id="stories">
        <div className="gm-wrap">
          <h2>What employers say</h2>
          <div className="gm-quote-grid">
            <aside className="gm-quote feat">
              <p>“{featured.text}”</p>
              <cite>{featured.by}</cite>
            </aside>
            {rest.map((q) => (
              <aside className="gm-quote" key={q.by}>
                <p>“{q.text}”</p>
                <cite>{q.by}</cite>
              </aside>
            ))}
          </div>
        </div>
      </section>

      <section className="gm-band white" id="model">
        <div className="gm-wrap gm-model-grid">
          <div>
            <h2>Full-time, part-time, hourly rates</h2>
            <p>
              Hires can be full-time or part-time. 20 hours/week minimum. Dedicated
              staff work the hours you need. The hiring brief explains the recruiting
              path, timeline, and hourly-rate structure. Live prices are not listed
              here because rates depend on role, seniority, and hours.
            </p>
          </div>
          <div>
            <h2>How we operate</h2>
            <p>
              We recruit and vet in the Philippines. You interview. We handle{" "}
              {copy.adminLabel} after you hire. Access stays yours: individual
              logins, MFA, and a password manager rather than one shared login.
            </p>
          </div>
        </div>
      </section>

      <section className="gm-band sand" id="faq">
        <div className="gm-wrap" style={{ maxWidth: "44rem" }}>
          <h2>Questions employers ask</h2>
          {faqs.map(([q, a]) => (
            <details key={q}>
              <summary>{q}</summary>
              <p>{a}</p>
            </details>
          ))}
        </div>
      </section>

      <section className="gm-band ocean" id="again">
        <div className="gm-wrap gm-closer">
          <div>
            <h2>Ready to hire?</h2>
            <p className="gm-lead">
              {needsTitle}. We’ll build the hiring brief and walk you through
              recruiting.
            </p>
            <div className="gm-cta-row">
              <a className="gm-submit inline" href="#gate">
                {lockedRole ? "Tell us the workload" : "Tell us the role"}
              </a>
              <a className="gm-call" href={copy.phoneHref} onClick={onPhone}>
                {copy.phoneDisplay}
              </a>
            </div>
          </div>
          <img
            className="gm-scene"
            src={copy.closerSrc}
            alt={copy.closerAlt}
            width={1200}
            height={800}
            loading="lazy"
          />
        </div>
      </section>

      <footer className="gm-footer">
        <div className="gm-wrap">
          <strong>{copy.entity}</strong>
          <br />
          {copy.nap}
          <br />
          Philippines recruitment hub · Serving employers since {copy.sinceYear} ·{" "}
          <a href="/privacy">Privacy</a> · <a href="/terms">Terms</a>
          <br />
          <a href={careersHref} onClick={onCareers}>
            {JOB_SEEKER_LINE}
          </a>
        </div>
      </footer>
    </div>
  );
}
