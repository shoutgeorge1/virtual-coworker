import {
  APPROVED_TESTIMONIALS,
  REVIEW_BADGES,
  TRUST_STAT_CHIPS,
  type TrustFirstPageConfig,
  type TrustFirstVariant,
} from "../../../config/trust-first";
import { clientMarksForMarket } from "../../../config/site";
import { isProofHeavy, splitHeadline } from "../../../lib/trust-first";
import EmployerQualificationForm from "./EmployerQualificationForm";

function initials(name: string) {
  return name
    .split(/\s+/)
    .filter(Boolean)
    .slice(0, 2)
    .map((part) => part[0]?.toUpperCase() || "")
    .join("");
}

function SplitHeadline({
  text,
  leadClass,
}: {
  text: string;
  leadClass?: string;
}) {
  const parts = splitHeadline(text);
  if (!parts.accent) return <>{text}</>;
  return (
    <>
      <span className={leadClass}>{parts.lead}</span>
      <em>{parts.accent}</em>
    </>
  );
}

function Starline() {
  const g = REVIEW_BADGES.google;
  const c = REVIEW_BADGES.clutch;
  return (
    <p className="tf-starline">
      <span className="tf-stars" aria-hidden="true">
        ★★★★★
      </span>
      <span>
        <b>
          {g.rating}
        </b>{" "}
        Google · {g.reviewCount} reviews
      </span>
      <span className="tf-stars tf-stars-clutch" aria-hidden="true">
        ★★★★★
      </span>
      <span>
        <b>
          {c.rating}
        </b>{" "}
        Rated on Clutch
      </span>
    </p>
  );
}

export default function TrustHero({
  page,
  variant,
  surface = "preview",
}: {
  page: TrustFirstPageConfig;
  variant: TrustFirstVariant;
  surface?: "preview" | "production";
}) {
  const heavy = isProofHeavy(variant);
  const logos = clientMarksForMarket("us").slice(0, heavy ? 6 : 4);
  const quote = APPROVED_TESTIMONIALS[0];
  const stats = heavy ? TRUST_STAT_CHIPS : TRUST_STAT_CHIPS.slice(0, 3);

  return (
    <section className="tf-hero" id="top">
      <div className="tf-wrap tf-hero-grid">
        <div>
          <p className="tf-eyebrow">{page.eyebrow}</p>
          <h1 className="tf-h1">
            <SplitHeadline text={page.h1} leadClass="tf-h1-lead" />
          </h1>
          <Starline />
          <p className="tf-lead">{page.supporting}</p>
          <ul className="tf-bullets">
            {page.heroBullets.map((item) => (
              <li key={item}>
                <span className="tf-icon-well tf-icon-yes" aria-hidden="true">
                  <svg viewBox="0 0 24 24">
                    <path
                      d="M6.6 12.4 10.2 16 17.4 8"
                      fill="none"
                      stroke="currentColor"
                      strokeWidth="2.6"
                      strokeLinecap="round"
                      strokeLinejoin="round"
                    />
                  </svg>
                </span>
                <span>{item}</span>
              </li>
            ))}
          </ul>
          <div className="tf-logos" aria-label="Clients we have staffed">
            {logos.map((mark) => (
              // eslint-disable-next-line @next/next/no-img-element
              <img key={mark.id} src={mark.src} alt={mark.alt || mark.name} />
            ))}
          </div>
          <div className="tf-stats">
            {stats.map((stat) => (
              <p className="tf-stat" key={stat.label}>
                <b>{stat.value}</b>
                <span>{stat.label}</span>
              </p>
            ))}
          </div>
          {heavy && quote ? (
            <blockquote className="tf-hero-quote">
              <p>“{quote.quote}”</p>
              <footer>
                <span className="tf-avatar" aria-hidden="true">
                  {initials(quote.name)}
                </span>
                {quote.name}
                {quote.company ? ` · ${quote.company}` : ""}
              </footer>
            </blockquote>
          ) : null}
        </div>
        <EmployerQualificationForm page={page} variant={variant} surface={surface} />
      </div>
    </section>
  );
}
