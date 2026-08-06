import Link from "next/link";
import SiteNav from "./components/SiteNav";
import SiteFooter from "./components/SiteFooter";
import { SITE } from "../config/site";

const HERO_MAPS = {
  a: "/brand/hero-hub-map-a.jpg",
  b: "/brand/hero-hub-map-b.jpg",
  c: "/brand/hero-hub-map-c.jpg",
} as const;

type HeroKey = keyof typeof HERO_MAPS;

const markets = [
  {
    href: "/us",
    cls: "hub-card-us",
    tag: "Employers",
    label: "United States · hire",
    name: "United States",
    meta: "US businesses hiring dedicated Philippines staff — dark casting LP, phone + form, employer gate.",
    img: "/brand/hero-us-2026.jpg",
    pos: "72% 24%",
    anim: "anim-rise",
  },
  {
    href: "/au",
    cls: "hub-card-au",
    tag: "Employers",
    label: "Australia · hire",
    name: "Australia",
    meta: "Australian employers on a daylight LP — form-primary path, same Philippines staffing model.",
    img: "/brand/hero-au-2026.jpg",
    pos: "70% 26%",
    anim: "anim-rise-d1",
  },
  {
    href: "/ph",
    cls: "hub-card-ph",
    tag: "Talent",
    label: "Philippines · careers",
    name: "Philippines",
    meta: "Job seekers only. Careers path so applicants never pollute the employer hire funnel.",
    img: "/brand/talent-john.jpeg",
    pos: "50% 18%",
    anim: "anim-rise-d2",
  },
];

function resolveHero(raw: string | string[] | undefined): HeroKey {
  const v = Array.isArray(raw) ? raw[0] : raw;
  if (v === "a" || v === "c") return v;
  return "b";
}

export default async function HubPage({
  searchParams,
}: {
  searchParams: Promise<{ hero?: string | string[] }>;
}) {
  const params = await searchParams;
  const hero = resolveHero(params.hero);
  const heroSrc = HERO_MAPS[hero];

  return (
    <main className="hub">
      <SiteNav tone="dark" />

      <header className="hub-hero">
        <div className="hub-hero-map" aria-hidden>
          {/* eslint-disable-next-line @next/next/no-img-element */}
          <img src={heroSrc} alt="" />
        </div>
        <div className="hub-hero-veil" aria-hidden />

        <div className="hub-hero-copy">
          <p className="hub-kicker anim-rise">
            <i />
            Paid hiring microsite · Philippines talent
          </p>
          <h1 className="anim-rise-d1">
            Hire dedicated <em>Philippines</em> staff for your US or Australian
            business.
          </h1>
          <p className="hub-hero-lead anim-rise-d2">
            A lean Next.js hiring site for paid Search — not WordPress. You brief
            the role, interview shortlisted talent, and hire with staffing
            support.
          </p>
          <div className="hub-hero-actions anim-rise-d2">
            <Link href="/us#gate" className="hub-hero-cta hub-hero-cta-primary">
              Start hiring · US
            </Link>
            <Link href="/au#gate" className="hub-hero-cta hub-hero-cta-ghost">
              Start hiring · AU
            </Link>
            <Link href="/how-it-works" className="hub-hero-cta hub-hero-cta-ghost">
              How it works
            </Link>
          </div>
        </div>

        <div className="hub-frame anim-fade">
          <div className="hub-frame-no">
            <strong>For employers</strong>
            <p>
              US and Australia doors for businesses hiring dedicated Philippines
              teammates — with an employer gate so job seekers don’t hit the form.
            </p>
          </div>
          <div className="hub-frame-yes">
            <strong>For talent</strong>
            <p>
              Looking for work? Use the{" "}
              <Link href="/ph">Philippines careers path</Link> — not the employer
              inquiry forms.
            </p>
          </div>
        </div>
      </header>

      <div className="hub-section-head">
        <h2>Choose your door.</h2>
        <span>Same brand · different job</span>
      </div>
      <p className="hub-gate-note anim-fade">
        Money pages live under /us and /au (plus nine role LPs). This hub is the
        microsite home — Services and How it works keep the path feeling like a
        site, not orphan ads.
      </p>

      <div className="hub-grid">
        {markets.map((m) => (
          <Link
            key={m.href}
            href={m.href}
            className={`hub-card ${m.cls} ${m.anim}`}
          >
            <div className="hub-card-img" aria-hidden>
              {/* eslint-disable-next-line @next/next/no-img-element */}
              <img
                src={m.img}
                alt=""
                style={{ objectPosition: m.pos }}
                className="face-img"
              />
            </div>
            <span className="hub-card-flag">{m.tag}</span>
            <p className="hub-card-label">{m.label}</p>
            <h3>{m.name}</h3>
            <p className="hub-card-meta">{m.meta}</p>
            <span className="hub-card-cta">Open →</span>
          </Link>
        ))}
      </div>

      <section className="hub-build">
        <div className="hub-build-intro">
          <h2>What you can open next.</h2>
          <p>
            Minimal site map — enough that every click still feels like Virtual
            Coworker, without rebuilding WordPress.
          </p>
        </div>
        <dl className="hub-stack">
          <div>
            <span>01</span>
            <dt>
              <Link href="/services">Services</Link>
            </dt>
            <dd>Nine employer role LPs for US and AU.</dd>
          </div>
          <div>
            <span>02</span>
            <dt>
              <Link href="/how-it-works">How it works</Link>
            </dt>
            <dd>Recruit · Choose · Operate — expanded for employers.</dd>
          </div>
          <div>
            <span>03</span>
            <dt>
              <Link href="/privacy">Privacy</Link> · <Link href="/terms">Terms</Link>
            </dt>
            <dd>
              Microsite notices + links to corporate policies on{" "}
              {SITE.corporateUrl.replace("https://", "")}.
            </dd>
          </div>
        </dl>
      </section>

      <p className="hub-foot">
        <b>{SITE.tagline}.</b> {SITE.disclaimer} US line{" "}
        <a href={SITE.usPhoneHref}>{SITE.usPhoneDisplay}</a>.
      </p>

      <SiteFooter tone="dark" />
    </main>
  );
}
