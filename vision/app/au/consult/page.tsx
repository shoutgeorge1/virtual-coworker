"use client";

import Link from "next/link";
import "../au.css";

export default function AUConsult() {
  return (
    <main className="au">
      <p className="vision-banner au-banner">
        Vision demo ·{" "}
        <Link href="/">back to hub</Link> · hire path only
      </p>

      <nav className="au-nav">
        <Link href="/au" className="au-brand">
          Virtual Coworker
        </Link>
        <div className="au-nav-links">
          <Link href="/au">← AU home</Link>
        </div>
      </nav>

      <div className="au-consult">
        <h1 className="anim-rise">Book a free chat</h1>
        <p className="anim-rise-d1">
          For Australian businesses hiring a VA. Looking for work? Head to the{" "}
          <Link href="/ph" style={{ color: "var(--sea)" }}>
            PH opportunities site
          </Link>
          .
        </p>

        <div className="au-gate-wrap" style={{ marginBottom: "2rem" }}>
          <p className="au-gate-label">Confirm your path</p>
          <div className="gate">
            <div className="gate-btn gate-hire" style={{ cursor: "default" }}>
              <strong>✓ Hiring for my business</strong>
              <span>Owners, founders &amp; ops leads welcome</span>
            </div>
            <Link href="/ph" className="gate-btn gate-job">
              <strong>Job seeker?</strong>
              <span>PH talent site is the right door →</span>
            </Link>
          </div>
        </div>

        <form
          className="au-form anim-rise-d2"
          onSubmit={(e) => {
            e.preventDefault();
          }}
        >
          <label>
            Your name
            <input name="name" type="text" placeholder="Sam Nguyen" required />
          </label>
          <label>
            Work email
            <input
              name="email"
              type="email"
              placeholder="you@business.com.au"
              required
            />
          </label>
          <label>
            Business name
            <input name="company" type="text" placeholder="Coastal Co." />
          </label>
          <label>
            State / territory
            <select name="state" defaultValue="">
              <option value="" disabled>
                Select
              </option>
              <option>NSW</option>
              <option>VIC</option>
              <option>QLD</option>
              <option>WA</option>
              <option>SA</option>
              <option>TAS</option>
              <option>ACT</option>
              <option>NT</option>
            </select>
          </label>
          <label>
            What would help most?
            <textarea
              name="notes"
              rows={3}
              placeholder="A bit of context helps us prepare"
            />
          </label>
          <button type="submit" className="au-btn au-btn-primary">
            Request a chat
          </button>
        </form>
        <p style={{ marginTop: "1.5rem", fontSize: "0.8rem", color: "var(--mute)" }}>
          Demo only — form does not submit.
        </p>
      </div>
    </main>
  );
}
