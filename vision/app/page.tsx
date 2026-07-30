import Link from "next/link";

export default function HubPage() {
  return (
    <main className="hub">
      <div className="hub-top anim-fade">
        <p className="hub-eyebrow">Vision demo · not live product</p>
        <p className="hub-note">
          One brand family. Three market doors — same blues, cyan, and gold.
        </p>
      </div>

      <header className="hub-hero">
        <div className="hub-hero-logo anim-rise">
          {/* eslint-disable-next-line @next/next/no-img-element */}
          <img
            src="/brand/logo-vc.png"
            alt="Virtual Coworker"
            className="logo-img-lg logo-img-on-dark"
          />
        </div>
        <h1 className="anim-rise-d1">Where Virtual Coworker could go.</h1>
        <p className="anim-rise-d2">
          A modern evolution of their Kadence look — Poppins + Century Gothic,
          teal/navy/gold — tuned per market so hire vs job intent feels clear the
          moment you land.
        </p>
      </header>

      <div className="hub-grid">
        <Link href="/us" className="hub-card hub-card-us anim-rise">
          <p className="hub-card-label">Market 01 · Buyers</p>
          <h2>United States</h2>
          <p className="hub-card-meta">
            Dark navy evolution for US businesses hiring dedicated VAs.
          </p>
          <p className="hub-card-cta">Open US experience →</p>
        </Link>

        <Link href="/au" className="hub-card hub-card-au anim-rise-d1">
          <p className="hub-card-label">Market 02 · Buyers</p>
          <h2>Australia</h2>
          <p className="hub-card-meta">
            Light coastal evolution — same palette, softer daylight feel.
          </p>
          <p className="hub-card-cta">Open AU experience →</p>
        </Link>

        <Link href="/ph" className="hub-card hub-card-ph anim-rise-d2">
          <p className="hub-card-label">Market 03 · Talent</p>
          <h2>Philippines</h2>
          <p className="hub-card-meta">
            Same brand, warmer opportunity energy for VA careers.
          </p>
          <p className="hub-card-cta">Open PH experience →</p>
        </Link>
      </div>

      <p className="hub-foot">
        Interview vision only. Not a proposal to rip-and-replace WordPress on
        Monday. Assets pulled from virtualcoworker.com / .com.au / .com.ph.
      </p>
    </main>
  );
}
