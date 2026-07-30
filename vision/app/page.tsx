import Link from "next/link";

export default function HubPage() {
  return (
    <main className="hub">
      <div className="hub-top anim-fade">
        <p className="hub-eyebrow">Vision demo · not live product</p>
        <p className="hub-note">
          Three markets. Three looks. Same company — different doors.
        </p>
      </div>

      <header className="hub-hero">
        <h1 className="anim-rise">Where Virtual Coworker could go.</h1>
        <p className="anim-rise-d1">
          A sharp visual direction for US buyers, Australian buyers, and
          Philippine talent — built to show how hire vs job intent should feel
          different the moment you land.
        </p>
      </header>

      <div className="hub-grid">
        <Link href="/us" className="hub-card hub-card-us anim-rise">
          <p className="hub-card-label">Market 01</p>
          <h2>US Buyers</h2>
          <p className="hub-card-meta">
            American businesses hiring dedicated VAs. Steel &amp; teal.
          </p>
          <p className="hub-card-cta">Open US experience →</p>
        </Link>

        <Link href="/au" className="hub-card hub-card-au anim-rise-d1">
          <p className="hub-card-label">Market 02</p>
          <h2>AU Buyers</h2>
          <p className="hub-card-meta">
            Australian businesses hiring VAs. Coastal light — not a US twin.
          </p>
          <p className="hub-card-cta">Open AU experience →</p>
        </Link>

        <Link href="/ph" className="hub-card hub-card-ph anim-rise-d2">
          <p className="hub-card-label">Market 03</p>
          <h2>PH Talent</h2>
          <p className="hub-card-meta">
            People building a VA career. Opportunity energy — not a buyer site.
          </p>
          <p className="hub-card-cta">Open PH experience →</p>
        </Link>
      </div>

      <p className="hub-foot">
        Interview vision only. Not a proposal to rip-and-replace WordPress on
        Monday. Hub · US · AU · PH — flip between looks for the shock factor.
      </p>
    </main>
  );
}
