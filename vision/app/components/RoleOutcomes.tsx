import type { CategorySlug } from "../../config/categories";
import { CATEGORIES } from "../../config/categories";
import { ROLE_OUTCOMES, PRIMARY_HIRE_CTA } from "../../config/employer-cro";
import type { MarketId } from "../../config/markets";

/**
 * Role-specific problem → tasks → gain block for category LPs.
 */
export default function RoleOutcomes({
  category,
  market,
  light = false,
}: {
  category: CategorySlug;
  market: MarketId;
  light?: boolean;
}) {
  const cat = CATEGORIES[category];
  const outcome = ROLE_OUTCOMES[category];
  const shell = market === "us" ? "us" : "au";

  return (
    <section
      className={`role-outcomes${light ? " role-outcomes-light" : ""}`}
      aria-labelledby="role-outcomes-title"
    >
      <div className="role-outcomes-inner">
        <header className="role-outcomes-head">
          <p className={market === "us" ? "us-proof-label" : "au-proof-label"}>
            {cat.label} outcomes
          </p>
          <h2 id="role-outcomes-title">
            Business problem → work handed off → operational gain
          </h2>
          <p className="role-outcomes-lead">{outcome.problem}</p>
        </header>

        <div className="role-outcomes-body">
          <div className="role-outcomes-tasks">
            <h3>What a dedicated coworker can take over</h3>
            <ul>
              {outcome.tasks.map((t) => (
                <li key={t}>{t}</li>
              ))}
            </ul>
          </div>
          <div className="role-outcomes-gain">
            <h3>What you gain</h3>
            <p>{outcome.gain}</p>
            <a href="#gate" className={`${shell}-btn ${shell}-btn-primary`}>
              {PRIMARY_HIRE_CTA}
            </a>
          </div>
        </div>
      </div>
    </section>
  );
}
