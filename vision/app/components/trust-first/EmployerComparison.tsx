import type { TrustFirstCompareRow } from "../../../config/trust-first";

export default function EmployerComparison({
  rows,
}: {
  rows: readonly TrustFirstCompareRow[];
}) {
  return (
    <section className="tf-section tf-section-alt">
      <div className="tf-wrap">
        <p className="tf-section-kicker">How this compares</p>
        <h2>What you are choosing</h2>
        <div className="tf-table-wrap">
          <table className="tf-compare">
            <thead>
              <tr>
                <th> </th>
                <th>Virtual Coworker</th>
                <th>Typical alternative</th>
              </tr>
            </thead>
            <tbody>
              {rows.map((row) => (
                <tr key={row.label}>
                  <th scope="row">{row.label}</th>
                  <td>{row.vc}</td>
                  <td>{row.other}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </section>
  );
}
