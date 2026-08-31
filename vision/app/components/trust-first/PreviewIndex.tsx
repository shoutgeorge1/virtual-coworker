import {
  allTrustFirstPages,
  TRUST_FIRST_NAMESPACE,
} from "../../../config/trust-first";
import { variantHref } from "../../../lib/trust-first";

export default function PreviewIndex() {
  const pages = allTrustFirstPages();
  return (
    <div className="tf tf-index">
      <div className="tf-wrap">
        <p className="tf-banner" style={{ marginBottom: "1rem" }}>
          PREVIEW INDEX — live pages are /us
        </p>
        <p className="tf-eyebrow">Internal review</p>
        <h1>Trust-first US landing pages</h1>
        <p className="tf-lead">
          Isolated under {TRUST_FIRST_NAMESPACE} (noindex). Default view is proof-heavy.
          Simple stays at <code>?v=simple</code>. Live paid pages are the <code>/us</code> routes.
          Preview forms still do not go to Zoho.
        </p>
        <div className="tf-table-wrap">
          <table className="tf-table">
            <thead>
              <tr>
                <th>Page</th>
                <th>Keyword cluster</th>
                <th>Proposed prod</th>
                <th>Current prod</th>
                <th>Variants</th>
                <th>Screens</th>
                <th>Kind</th>
                <th>Status</th>
                <th>Job-seeker</th>
                <th>Confidence</th>
                <th>Notes</th>
              </tr>
            </thead>
            <tbody>
              {pages.map((page) => (
                <tr key={page.key}>
                  <td>
                    <strong>{page.name}</strong>
                    <br />
                    <a href={page.previewPath}>{page.previewPath}</a>
                  </td>
                  <td>{page.keywordCluster}</td>
                  <td>{page.proposedProductionPath}</td>
                  <td>{page.currentProductionEquivalent}</td>
                  <td>
                    <a href={variantHref(page.previewPath, "simple")}>Simple</a>
                    <br />
                    <a href={variantHref(page.previewPath, "proof_heavy")}>Proof-heavy</a>
                  </td>
                  <td>
                    <a href={`/preview/trust-first/screenshots/${page.key}-desktop.png`}>
                      Desktop
                    </a>
                    <br />
                    <a href={`/preview/trust-first/screenshots/${page.key}-mobile.png`}>
                      Mobile
                    </a>
                  </td>
                  <td>{page.pageKind}</td>
                  <td>{page.recommendedStatus}</td>
                  <td>{page.jobSeekerRisk}</td>
                  <td>{page.confidence}</td>
                  <td>{page.notes}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
