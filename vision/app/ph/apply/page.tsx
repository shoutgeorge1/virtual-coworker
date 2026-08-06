"use client";

import Link from "next/link";
import SiteFooter from "../../components/SiteFooter";
import "../ph.css";

export default function PHApply() {
  return (
    <main className="ph">
      <nav className="ph-nav">
        <Link href="/ph" className="ph-brand">
          {/* eslint-disable-next-line @next/next/no-img-element */}
          <img
            src="/brand/logo-vc.png"
            alt="Virtual Coworker"
            className="logo-img logo-img-on-dark"
          />
          <span className="ph-brand-tag">Careers</span>
        </Link>
        <div className="ph-nav-right">
          <Link href="/ph" className="ph-nav-link">
            ← Careers home
          </Link>
        </div>
      </nav>

      <div className="ph-apply">
        <h1 className="anim-rise">Apply for VA opportunities</h1>
        <p className="anim-rise-d1">
          For people building a virtual assistant career. Businesses hiring
          staff: use the US or Australia hiring pages in the footer — not this
          form.
        </p>

        <p className="ph-gate-note" style={{ marginBottom: "2rem" }}>
          This form is talent-only. Hire intent is redirected away on purpose.
        </p>

        <form
          className="ph-form anim-rise-d2"
          onSubmit={(e) => {
            e.preventDefault();
          }}
        >
          <label>
            Full name
            <input name="name" type="text" placeholder="Maria Santos" required />
          </label>
          <label>
            Email
            <input
              name="email"
              type="email"
              placeholder="you@email.com"
              required
            />
          </label>
          <label>
            City / region (PH)
            <input name="city" type="text" placeholder="Cebu City" />
          </label>
          <label>
            Experience level
            <select name="level" defaultValue="">
              <option value="" disabled>
                Select
              </option>
              <option>New to VA work</option>
              <option>1–2 years</option>
              <option>3+ years</option>
            </select>
          </label>
          <label>
            Strengths
            <textarea
              name="strengths"
              rows={3}
              placeholder="Admin, support, tools you know…"
            />
          </label>
          <button type="submit" className="ph-btn ph-btn-primary">
            Submit application
          </button>
        </form>
        <p
          style={{
            marginTop: "1.5rem",
            fontSize: "0.8rem",
            color: "var(--mute)",
          }}
        >
          Demo only — form does not submit.
        </p>
      </div>

      <SiteFooter tone="dark" market="ph" />
    </main>
  );
}
