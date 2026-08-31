import type { TrustFirstStep } from "../../../config/trust-first";

export default function HowItWorks({ steps }: { steps: readonly TrustFirstStep[] }) {
  return (
    <section className="tf-section">
      <div className="tf-wrap">
        <p className="tf-section-kicker">How it works</p>
        <h2>Recruit, vet, shortlist. You interview.</h2>
        <div className="tf-grid-3">
          {steps.map((step) => (
            <article className="tf-well-card" key={step.k}>
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
                <span className="tf-step-k">Step {step.k}</span>
                <h3>{step.t}</h3>
                <p>{step.d}</p>
              </div>
            </article>
          ))}
        </div>
      </div>
    </section>
  );
}
