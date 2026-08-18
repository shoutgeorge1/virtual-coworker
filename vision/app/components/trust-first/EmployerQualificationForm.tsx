"use client";

import { useMemo, useState } from "react";
import {
  COMPANY_SIZE_OPTIONS,
  EMPLOYER_ROLE_OPTIONS,
  HIRING_TIMELINE_OPTIONS,
  JOB_SEEKER_DIVERSION,
  TRUST_FIRST_LP_VERSION,
  VERIFIED_PROOF,
  type TrustFirstPageConfig,
  type TrustFirstVariant,
} from "../../../config/trust-first";
import {
  formatPhoneInput,
  PH_PHONE_CAREERS_MESSAGE,
  US_PHONE_ERROR,
  validateUsPhone,
} from "../../../lib/phone-format";

type Props = {
  page: TrustFirstPageConfig;
  variant: TrustFirstVariant;
};

function readParam(name: string): string {
  if (typeof window === "undefined") return "";
  return new URLSearchParams(window.location.search).get(name) || "";
}

export default function EmployerQualificationForm({ page, variant }: Props) {
  const startedAt = useMemo(() => Date.now(), []);
  const [name, setName] = useState("");
  const [company, setCompany] = useState("");
  const [email, setEmail] = useState("");
  const [phone, setPhone] = useState("");
  const [role, setRole] = useState(page.formRoleDefault);
  const [size, setSize] = useState("");
  const [timeline, setTimeline] = useState("");
  const [honeypot, setHoneypot] = useState("");
  const [error, setError] = useState("");
  const [done, setDone] = useState(false);
  const [busy, setBusy] = useState(false);

  const roles = EMPLOYER_ROLE_OPTIONS.includes(
    page.formRoleDefault as (typeof EMPLOYER_ROLE_OPTIONS)[number],
  )
    ? EMPLOYER_ROLE_OPTIONS
    : ([page.formRoleDefault, ...EMPLOYER_ROLE_OPTIONS] as const);

  async function onSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError("");

    if (!name.trim() || !company.trim() || !email.trim() || !phone.trim()) {
      setError("Company name, your name, work email, and a US phone are required.");
      return;
    }

    const usPhone = validateUsPhone(phone);
    if (!usPhone.ok) {
      setError(usPhone.code === "ph_job_seeker_phone" ? PH_PHONE_CAREERS_MESSAGE : US_PHONE_ERROR);
      return;
    }

    setBusy(true);
    try {
      const res = await fetch("/api/lead-preview", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          preview: true,
          intent: "employer",
          market: "us",
          name: name.trim(),
          company: company.trim(),
          email: email.trim(),
          phone: usPhone.e164,
          role,
          company_size: size,
          hiring_timeline: timeline,
          website: honeypot,
          form_started_at: startedAt,
          lp_key: page.key,
          lp_version: TRUST_FIRST_LP_VERSION,
          lp_variant: variant,
          landing_page_url: typeof window !== "undefined" ? window.location.href.split("#")[0] : page.previewPath,
          gclid: readParam("gclid"),
          gbraid: readParam("gbraid"),
          wbraid: readParam("wbraid"),
          utm_source: readParam("utm_source"),
          utm_medium: readParam("utm_medium"),
          utm_campaign: readParam("utm_campaign"),
          utm_term: readParam("utm_term"),
          utm_content: readParam("utm_content"),
          utm_matchtype: readParam("utm_matchtype"),
        }),
      });
      const data = (await res.json()) as { ok?: boolean; error?: string };
      if (!res.ok || !data.ok) {
        setError(data.error || "Unable to submit this preview form.");
        return;
      }
      setDone(true);
    } catch {
      setError("Unable to submit this preview form.");
    } finally {
      setBusy(false);
    }
  }

  function goCareers(e: React.MouseEvent<HTMLAnchorElement>) {
    e.preventDefault();
    window.location.replace(VERIFIED_PROOF.careersUrl);
  }

  return (
    <div className="tf-card tf-form" id="gate">
      <h2>{page.formHeading}</h2>
      <p className="tf-muted" style={{ marginBottom: "0.9rem" }}>
        For businesses hiring staff. This preview does not send a live inquiry.
      </p>
      {done ? (
        <p className="tf-ok">
          Preview received. Nothing was sent to Virtual Coworker, Zoho, or email.
        </p>
      ) : (
        <form onSubmit={onSubmit} noValidate>
          <label htmlFor="tf-company">Company name</label>
          <input
            id="tf-company"
            name="company"
            autoComplete="organization"
            value={company}
            onChange={(e) => setCompany(e.target.value)}
            required
          />

          <label htmlFor="tf-name">Your name</label>
          <input
            id="tf-name"
            name="name"
            autoComplete="name"
            value={name}
            onChange={(e) => setName(e.target.value)}
            required
          />

          <label htmlFor="tf-email">Work email</label>
          <input
            id="tf-email"
            name="email"
            type="email"
            autoComplete="email"
            inputMode="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
          />

          <label htmlFor="tf-phone">US phone</label>
          <input
            id="tf-phone"
            name="phone"
            type="tel"
            autoComplete="tel"
            inputMode="tel"
            value={phone}
            onChange={(e) => setPhone(formatPhoneInput(e.target.value, "us"))}
            required
          />

          <label htmlFor="tf-role">Role needed</label>
          <select
            id="tf-role"
            name="role"
            value={role}
            onChange={(e) => setRole(e.target.value)}
          >
            {roles.map((opt) => (
              <option key={opt} value={opt}>
                {opt}
              </option>
            ))}
          </select>

          {variant === "proof_heavy" ? (
            <>
              <label htmlFor="tf-size">Company size</label>
              <select
                id="tf-size"
                name="company_size"
                value={size}
                onChange={(e) => setSize(e.target.value)}
              >
                <option value="">Optional</option>
                {COMPANY_SIZE_OPTIONS.map((opt) => (
                  <option key={opt} value={opt}>
                    {opt}
                  </option>
                ))}
              </select>

              <label htmlFor="tf-timeline">Hiring timeline</label>
              <select
                id="tf-timeline"
                name="hiring_timeline"
                value={timeline}
                onChange={(e) => setTimeline(e.target.value)}
              >
                <option value="">Optional</option>
                {HIRING_TIMELINE_OPTIONS.map((opt) => (
                  <option key={opt} value={opt}>
                    {opt}
                  </option>
                ))}
              </select>
            </>
          ) : null}

          <div className="tf-hp" aria-hidden="true">
            <label htmlFor="tf-website">Website</label>
            <input
              id="tf-website"
              name="website"
              tabIndex={-1}
              autoComplete="off"
              value={honeypot}
              onChange={(e) => setHoneypot(e.target.value)}
            />
          </div>

          {error ? <p className="tf-error">{error}</p> : null}

          <button className="tf-btn" type="submit" disabled={busy}>
            {busy ? "Sending preview…" : page.cta}
          </button>
        </form>
      )}

      <p className="tf-jobseeker">
        {JOB_SEEKER_DIVERSION.label}{" "}
        <a href={VERIFIED_PROOF.careersUrl} onClick={goCareers}>
          {JOB_SEEKER_DIVERSION.cta}
        </a>
        <span className="tf-muted"> {JOB_SEEKER_DIVERSION.body}</span>
      </p>
    </div>
  );
}
