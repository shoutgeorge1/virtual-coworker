"use client";

import Link from "next/link";
import "../us.css";

export default function USConsult() {
  return (
    <main className="us">
      <p className="vision-banner us-banner">
        Vision demo ·{" "}
        <Link href="/">back to hub</Link> · hire path only
      </p>

      <nav className="us-nav">
        <Link href="/us" className="us-brand">
          {/* eslint-disable-next-line @next/next/no-img-element */}
          <img
            src="/brand/logo-vc.png"
            alt="Virtual Coworker"
            className="logo-img logo-img-on-dark"
          />
        </Link>
        <div className="us-nav-links">
          <Link href="/us">← US home</Link>
        </div>
      </nav>

      <div className="us-consult">
        <h1 className="anim-rise">Free consultation</h1>
        <p className="anim-rise-d1">
          For US businesses hiring a virtual assistant. Job seekers: please use
          the{" "}
          <Link href="/ph" style={{ color: "var(--cyan)" }}>
            PH talent site
          </Link>
          .
        </p>

        <div className="us-gate-wrap" style={{ marginBottom: "2rem" }}>
          <p className="us-gate-label">Confirm your intent</p>
          <div className="gate">
            <div className="gate-btn gate-hire" style={{ cursor: "default" }}>
              <strong>✓ Hiring a VA</strong>
              <span>This form is for business owners &amp; managers</span>
            </div>
            <Link href="/ph" className="gate-btn gate-job">
              <strong>Looking for a job?</strong>
              <span>Go to PH opportunities →</span>
            </Link>
          </div>
        </div>

        <form
          className="us-form anim-rise-d2"
          onSubmit={(e) => {
            e.preventDefault();
          }}
        >
          <label>
            Full name
            <input name="name" type="text" placeholder="Jordan Lee" required />
          </label>
          <label>
            Work email
            <input
              name="email"
              type="email"
              placeholder="you@company.com"
              required
            />
          </label>
          <label>
            Company
            <input name="company" type="text" placeholder="Acme Co." />
          </label>
          <label>
            What do you need help with?
            <select name="need" defaultValue="">
              <option value="" disabled>
                Select a focus
              </option>
              <option>Admin &amp; inbox</option>
              <option>Customer support</option>
              <option>Sales ops / CRM</option>
              <option>Marketing support</option>
              <option>Other</option>
            </select>
          </label>
          <label>
            Anything else?
            <textarea name="notes" rows={3} placeholder="Optional context" />
          </label>
          <button type="submit" className="us-btn us-btn-primary">
            Request consultation
          </button>
        </form>
        <p style={{ marginTop: "1.5rem", fontSize: "0.8rem", color: "var(--mute)" }}>
          Demo only — form does not submit.
        </p>
      </div>
    </main>
  );
}
