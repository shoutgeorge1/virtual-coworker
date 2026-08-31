import type { TrustFirstCompareMark, TrustFirstCompareRow } from "../../../config/trust-first";

export default function EmployerComparison({
  rows,
  lead,
}: {
  rows: readonly TrustFirstCompareRow[];
  lead: string;
}) {
  return (
    <section className="tf-section" id="compare">
      <div className="tf-wrap">
        <span className="tf-accent-bar" aria-hidden="true" />
        <h2>How we compare</h2>
        <p className="tf-muted" style={{ marginBottom: "1rem" }}>
          {lead}
        </p>
        <div className="tf-compare-wrap" tabIndex={0} role="region" aria-label="Comparison table">
          <table className="tf-compare">
            <thead>
              <tr>
                <th scope="col"> </th>
                <th scope="col">Other options</th>
                <th scope="col" className="tf-compare-vc">
                  Virtual Coworker
                </th>
              </tr>
            </thead>
            <tbody>
              {rows.map((row) => (
                <tr key={row.label}>
                  <th scope="row">{row.label}</th>
                  <td>
                    <div className="tf-compare-cell">
                      <Mark mark={row.otherMark} />
                      <span>{row.other}</span>
                    </div>
                  </td>
                  <td className="tf-compare-vc">
                    <div className="tf-compare-cell">
                      <Mark mark={row.vcMark} />
                      <span>{row.vc}</span>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </section>
  );
}

function Mark({ mark }: { mark: TrustFirstCompareMark }) {
  const yes = mark === "yes";
  return (
    <span
      className={`tf-icon-well ${yes ? "tf-icon-yes" : "tf-icon-no"}`}
      aria-hidden="true"
    >
      {yes ? (
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
      ) : (
        <svg viewBox="0 0 24 24">
          <path
            d="M8 8l8 8M16 8l-8 8"
            fill="none"
            stroke="currentColor"
            strokeWidth="2.6"
            strokeLinecap="round"
          />
        </svg>
      )}
    </span>
  );
}
