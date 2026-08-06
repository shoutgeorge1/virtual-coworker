import type { Metadata } from "next";
import Link from "next/link";
import SiteNav from "../components/SiteNav";
import SiteFooter from "../components/SiteFooter";
import MarketGtm from "../components/MarketGtm";
import type { MarketId } from "../../config/markets";
import type { SiteSurface } from "../../config/site";

export const metadata: Metadata = {
  title: "How it works · Virtual Coworker Hiring",
  description:
    "How Virtual Coworker recruits, shortlists, and supports Philippines staff for employers.",
  robots: { index: false, follow: false },
};

const STEPS = [
  {
    k: "01 · Recruit",
    t: "Tell us the role. We source and screen.",
    d: "You share the seat you need filled — tools, hours, must-haves. Our recruitment team in the Philippines sources candidates and screens for fit before anyone reaches you.",
    points: [
      "Role brief, not a blank “send resumes” inbox",
      "Screening against your workflow and language needs",
      "Shortlist prepared for employer interviews",
    ],
  },
  {
    k: "02 · Choose",
    t: "You interview. You decide.",
    d: "You meet shortlisted talent on video. Ask culture and craft questions that matter to your business. Hire only when you’re ready — no forced match.",
    points: [
      "Video interviews on your schedule",
      "You own the hiring decision",
      "Clear path from shortlist to offer conversation",
    ],
  },
  {
    k: "03 · Operate",
    t: "We support the hire after you say yes.",
    d: "Once you hire, Virtual Coworker handles employment operations and ongoing account support so you stay focused on the work — and remain the client.",
    points: [
      "Payroll and employment ops after placement",
      "Account management for the working relationship",
      "A staffing partner model — not a freelance marketplace",
    ],
  },
] as const;

function resolveMarket(raw: string | string[] | undefined): MarketId {
  const v = Array.isArray(raw) ? raw[0] : raw;
  return v === "au" ? "au" : "us";
}

export default async function HowItWorksPage({
  searchParams,
}: {
  searchParams: Promise<{ market?: string | string[] }>;
}) {
  const params = await searchParams;
  const market = resolveMarket(params.market);
  const surface: SiteSurface = market;
  const home = market === "au" ? "/au" : "/us";
  const marketLabel = market === "au" ? "Australian" : "US";

  return (
    <main className="micro">
      <MarketGtm surface={surface} />
      <SiteNav tone="dark" market={surface} active="how" />

      <header className="micro-hero">
        <p className="micro-kicker">
          Employers · {market === "au" ? "Australia" : "United States"} ·
          Philippines talent
        </p>
        <h1>How hiring works with Virtual Coworker.</h1>
        <p className="micro-lead">
          Three steps. You keep ownership of who joins your team. We recruit,
          screen, and support dedicated Philippines staff for {marketLabel}{" "}
          businesses.
        </p>
        <div className="micro-actions">
          <Link href={`${home}#gate`} className="micro-btn micro-btn-primary">
            Start hiring
          </Link>
          <Link
            href={`/services?market=${market}`}
            className="micro-btn micro-btn-ghost"
          >
            Browse services
          </Link>
        </div>
      </header>

      <section className="micro-section">
        <div className="how-steps">
          {STEPS.map((s) => (
            <article className="how-step" key={s.k}>
              <em>{s.k}</em>
              <h2>{s.t}</h2>
              <p>{s.d}</p>
              <ul>
                {s.points.map((p) => (
                  <li key={p}>{p}</li>
                ))}
              </ul>
            </article>
          ))}
        </div>
      </section>

      <section className="micro-cta">
        <h2>Ready to brief a role?</h2>
        <p>
          Tell us who you need. Job seekers should use the Philippines careers
          path instead — linked quietly in the footer.
        </p>
        <div className="micro-actions">
          <Link href={`${home}#gate`} className="micro-btn micro-btn-primary">
            Tell us who you need
          </Link>
        </div>
      </section>

      <SiteFooter tone="dark" market={surface} />
    </main>
  );
}
