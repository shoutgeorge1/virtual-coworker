import type { TrustFirstStep } from "../../../config/trust-first";

export default function HowItWorks({ steps }: { steps: readonly TrustFirstStep[] }) {
  return (
    <section className="tf-section tf-section-alt">
      <div className="tf-wrap">
        <p className="tf-section-kicker">How it works</p>
        <h2>Recruit, vet, shortlist. You interview.</h2>
        <div className="tf-grid-3">
          {steps.map((step) => (
            <article className="tf-item" key={step.k}>
              <span className="tf-step-k">Step {step.k}</span>
              <h3>{step.t}</h3>
              <p>{step.d}</p>
            </article>
          ))}
        </div>
      </div>
    </section>
  );
}
