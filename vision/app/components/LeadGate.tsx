"use client";

import Link from "next/link";
import { useState } from "react";

export type GateCopy = {
  eyebrow: string;
  title: string;
  intentLabel: string;
  intentPrimary: string;
  intentSecondary: string;
  divertHref: string;
  divertTitle: string;
  divertBody: string;
  divertCta: string;
  q1Label: string;
  q1: string[];
  q2Label: string;
  q2: string[];
  detailsLabel: string;
  namePlaceholder: string;
  emailLabel: string;
  emailPlaceholder: string;
  phoneLabel: string;
  phonePlaceholder: string;
  submit: string;
  reassure: string;
  callLabel: string;
  phoneDisplay: string;
  phoneHref: string;
  doneTitle: string;
  doneBody: string;
};

/* Markets without a published public number show the tracking slot as static
   copy rather than a tel: link, so the demo never dials a real person. */
function CallBlock({ copy, solo }: { copy: GateCopy; solo?: boolean }) {
  const cls = `gate-call${solo ? " gate-call-solo" : ""}`;
  const inner = (
    <>
      <span className="gate-call-ico" aria-hidden>
        ☎
      </span>
      <span>
        <b>{copy.phoneDisplay}</b>
        <em>{copy.callLabel}</em>
      </span>
    </>
  );

  if (!copy.phoneHref) {
    return <div className={`${cls} gate-call-static`}>{inner}</div>;
  }
  return (
    <a className={cls} href={copy.phoneHref}>
      {inner}
    </a>
  );
}

export default function LeadGate({ copy }: { copy: GateCopy }) {
  const [intent, setIntent] = useState<"primary" | "secondary">("primary");
  const [q1, setQ1] = useState<string | null>(null);
  const [q2, setQ2] = useState<string | null>(null);
  const [done, setDone] = useState(false);

  const steps = [true, q1 !== null, q2 !== null, done];
  const progress = (steps.filter(Boolean).length / steps.length) * 100;

  return (
    <aside className="gate-card anim-rise-d1" id="gate">
      <div className="gate-card-head">
        <p className="gate-card-eyebrow">{copy.eyebrow}</p>
        <h2>{copy.title}</h2>
        <div className="gate-progress" aria-hidden>
          <span style={{ width: `${done ? 100 : progress}%` }} />
        </div>
      </div>

      {done ? (
        <div className="gate-done">
          <p className="gate-done-mark" aria-hidden>
            ✓
          </p>
          <h3>{copy.doneTitle}</h3>
          <p>{copy.doneBody}</p>
          <CallBlock copy={copy} solo />
        </div>
      ) : (
        <div className="gate-card-body">
          <fieldset className="gate-step">
            <legend>
              <b>1</b> {copy.intentLabel}
            </legend>
            <div className="gate-intent">
              <button
                type="button"
                className={intent === "primary" ? "on" : ""}
                aria-pressed={intent === "primary"}
                onClick={() => setIntent("primary")}
              >
                {copy.intentPrimary}
              </button>
              <button
                type="button"
                className={intent === "secondary" ? "on" : ""}
                aria-pressed={intent === "secondary"}
                onClick={() => setIntent("secondary")}
              >
                {copy.intentSecondary}
              </button>
            </div>
          </fieldset>

          {intent === "secondary" ? (
            <div className="gate-divert">
              <strong>{copy.divertTitle}</strong>
              <p>{copy.divertBody}</p>
              <Link href={copy.divertHref} className="gate-submit">
                {copy.divertCta}
              </Link>
            </div>
          ) : (
            <form
              onSubmit={(e) => {
                e.preventDefault();
                setDone(true);
              }}
            >
              <fieldset className="gate-step">
                <legend>
                  <b>2</b> {copy.q1Label}
                </legend>
                <div className="gate-chips">
                  {copy.q1.map((o) => (
                    <button
                      type="button"
                      key={o}
                      className={q1 === o ? "on" : ""}
                      aria-pressed={q1 === o}
                      onClick={() => setQ1(o)}
                    >
                      {o}
                    </button>
                  ))}
                </div>
              </fieldset>

              <fieldset className="gate-step">
                <legend>
                  <b>3</b> {copy.q2Label}
                </legend>
                <div className="gate-chips">
                  {copy.q2.map((o) => (
                    <button
                      type="button"
                      key={o}
                      className={q2 === o ? "on" : ""}
                      aria-pressed={q2 === o}
                      onClick={() => setQ2(o)}
                    >
                      {o}
                    </button>
                  ))}
                </div>
              </fieldset>

              <fieldset className="gate-step">
                <legend>
                  <b>4</b> {copy.detailsLabel}
                </legend>
                <div className="gate-fields">
                  <input
                    type="text"
                    name="name"
                    required
                    placeholder={copy.namePlaceholder}
                    aria-label={copy.detailsLabel}
                  />
                  <input
                    type="email"
                    name="email"
                    required
                    placeholder={copy.emailPlaceholder}
                    aria-label={copy.emailLabel}
                  />
                  <input
                    type="tel"
                    name="phone"
                    placeholder={copy.phonePlaceholder}
                    aria-label={copy.phoneLabel}
                  />
                </div>
              </fieldset>

              <button type="submit" className="gate-submit">
                {copy.submit}
              </button>
              <p className="gate-reassure">{copy.reassure}</p>
            </form>
          )}

          <div className="gate-or">
            <span>or</span>
          </div>

          <CallBlock copy={copy} />
        </div>
      )}
    </aside>
  );
}
