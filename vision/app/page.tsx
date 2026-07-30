import Link from "next/link";

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
    tag: "Buyers",
    label: "Market 01 · virtualcoworker.com",
    name: "United States",
    meta: "US companies hiring VAs. Its own portal so paid search can run a hire-first message — and A/B the headline, gate and form — without touching the main site.",
    img: "/brand/hero-us-2026.jpg",
    pos: "72% 24%",
    anim: "anim-rise",
  },
  {
    href: "/au",
    cls: "hub-card-au",
    tag: "Buyers",
    label: "Market 02 · virtualcoworker.com.au",
    name: "Australia",
    meta: "Australian companies hiring VAs. Own daylight, own plain-talking copy, own 1300 number and its own tests — not the US page with the spelling swapped.",
    img: "/brand/hero-au-2026.jpg",
    pos: "70% 26%",
    anim: "anim-rise-d1",
  },
  {
    href: "/ph",
    cls: "hub-card-ph",
    tag: "Talent",
    label: "Market 03 · virtualcoworker.com.ph",
    name: "Philippines",
    meta: "Filipino talent and opportunities. A separate door with EN/TL and real VA faces, so career ads get tested on their own and applicants never pollute the hire funnel.",
    img: "/brand/talent-john.jpeg",
    pos: "50% 18%",
    anim: "anim-rise-d2",
  },
];

const stack = [
  {
    n: "01",
    t: "Next.js on Vercel",
    d: "Same stack this demo runs on. A new campaign page goes live in minutes instead of waiting in a dev queue.",
  },
  {
    n: "02",
    t: "Keyword → page mapping",
    d: "Every ad group lands on a page written for that intent, instead of dumping all of it on one homepage.",
  },
  {
    n: "03",
    t: "A market door each",
    d: "US, AU and PH get their own copy, offer and proof — not one site with the flag swapped out.",
  },
  {
    n: "04",
    t: "A/B and multivariate",
    d: "Headline, hero, gate, form length. Test on the fly, keep what wins, roll it out the same day.",
  },
  {
    n: "05",
    t: "Quizzes and intent gates",
    d: "Qualify hire vs job before the form so we stop paying for leads we were never going to convert.",
  },
  {
    n: "06",
    t: "Gated forms + call tracking",
    d: "Every form and every number maps back to a source, so we know what the spend actually bought.",
  },
];

function resolveHero(raw: string | string[] | undefined): HeroKey {
  const v = Array.isArray(raw) ? raw[0] : raw;
  if (v === "b" || v === "c") return v;
  return "a";
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
      <div className="hub-top anim-fade">
        {/* eslint-disable-next-line @next/next/no-img-element */}
        <img
          src="/brand/logo-vc.png"
          alt="Virtual Coworker"
          className="logo-img logo-img-on-dark"
        />
        <div className="hub-top-right">
          <nav className="hub-hero-pick" aria-label="Hero map option">
            {(["a", "b", "c"] as const).map((key) => (
              <Link
                key={key}
                href={key === "a" ? "/" : `/?hero=${key}`}
                className={hero === key ? "is-active" : undefined}
                prefetch={false}
              >
                Map {key.toUpperCase()}
              </Link>
            ))}
          </nav>
          <p className="hub-eyebrow">Vision demo · not live product</p>
        </div>
      </div>

      <header className="hub-hero">
        <div
          className="hub-hero-map"
          style={{ backgroundImage: `url(${heroSrc})` }}
          aria-hidden
        />
        <div className="hub-hero-veil" aria-hidden />

        <div className="hub-hero-copy">
          <p className="hub-kicker anim-rise">
            <i />
            Creative refresh · ad &amp; PPC portal layer
          </p>
          <h1 className="anim-rise-d1">
            Audience-specific landing experiences for{" "}
            <em>paid acquisition</em>.
          </h1>
          <p className="hub-hero-lead anim-rise-d2">
            So this is a <b>creative refresh that lives where the ads land</b>{" "}
            — three market portals for paid, on a stack where I can change the
            page the same day I change the campaign.
          </p>
        </div>

        <div className="hub-frame anim-fade">
          <div className="hub-frame-no">
            <strong>What this isn&apos;t</strong>
            <p>
              A pitch to rip out virtualcoworker.com. The WordPress site keeps
              doing what it&apos;s good at — brand, content, organic. Nobody has
              to touch it.
            </p>
          </div>
          <div className="hub-frame-yes">
            <strong>What this is</strong>
            <p>
              The ad placement layer. Where PPC, paid social and every funnel
              test lands — hyper-optimised pages, quizzes and gated forms I can
              A/B on the fly.
            </p>
          </div>
        </div>
      </header>

      <div className="hub-section-head">
        <h2>Three doors, three audiences.</h2>
        <span>Same brand family · different job to do</span>
      </div>
      <p className="hub-gate-note anim-fade">
        Job seekers who land on a US/AU door get routed to the Philippines
        careers portal — they never submit on a hire form.
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
              <img src={m.img} alt="" style={{ objectPosition: m.pos }} className="face-img" />
            </div>
            <span className="hub-card-flag">{m.tag}</span>
            <p className="hub-card-label">{m.label}</p>
            <h3>{m.name}</h3>
            <p className="hub-card-meta">{m.meta}</p>
            <span className="hub-card-cta">Open the landing experience</span>
          </Link>
        ))}
      </div>

      <section className="hub-build">
        <div className="hub-build-intro">
          <h2>How I&apos;d actually build it.</h2>
          <p>
            Nothing exotic. The point is speed — a place where paid can move
            without asking anyone&apos;s permission.
          </p>
        </div>
        <dl className="hub-stack">
          {stack.map((s) => (
            <div key={s.n}>
              <span>{s.n}</span>
              <dt>{s.t}</dt>
              <dd>{s.d}</dd>
            </div>
          ))}
        </dl>
      </section>

      <p className="hub-foot">
        <b>Interview vision only.</b> Nothing here is live product and no form
        submits. If the WordPress team or the PH developers want to lift
        patterns or code out of this later, take it — but this is the piece
        I&apos;d build first, and I&apos;d own it.
      </p>
    </main>
  );
}
