const WELLS = [
  {
    title: "Staffing since 2011",
    body: "Fifteen years recruiting dedicated Filipino staff for employers. A company, not an app.",
  },
  {
    title: "You interview the shortlist",
    body: "We recruit and vet. Nobody starts until you say yes.",
  },
  {
    title: "We employ them after you hire",
    body: "Payroll stays with us. You do not run Philippines payroll yourself.",
  },
  {
    title: "Privacy and terms on this host",
    body: "Hiring conversations follow the same Privacy and Terms pages already on this site.",
  },
] as const;

export default function BuiltForTrust() {
  return (
    <section className="tf-section">
      <div className="tf-wrap">
        <p className="tf-section-kicker">Built for trust</p>
        <h2>What we can stand behind</h2>
        <div className="tf-grid-2">
          {WELLS.map((item) => (
            <article className="tf-well-card" key={item.title}>
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
              <div>
                <h3>{item.title}</h3>
                <p>{item.body}</p>
              </div>
            </article>
          ))}
        </div>
      </div>
    </section>
  );
}
