"use client";

import { useEffect, useMemo, useState } from "react";
import { useRouter } from "next/navigation";
import {
  COMPANY_SIZE_OPTIONS,
  EMPLOYER_ROLE_OPTIONS,
  HIRING_TIMELINE_OPTIONS,
  JOB_SEEKER_DIVERSION,
  TRUST_FIRST_LP_VERSION,
  TRUST_FIRST_PRODUCTION_LANDING_PAGE_TYPE,
  TRUST_FIRST_PRODUCTION_LP_VERSION,
  VERIFIED_PROOF,
  type TrustFirstPageConfig,
  type TrustFirstVariant,
} from "../../../config/trust-first";
import { US_BASELINE_LABEL } from "../../../config/lp-version";
import { scoreLeadValue } from "../../../config/lead-value";
import {
  formatPhoneInput,
  PH_PHONE_CAREERS_MESSAGE,
  US_PHONE_ERROR,
  validateUsPhone,
} from "../../../lib/phone-format";
import { exitToCareers } from "../../../lib/job-seeker-exit";
import {
  readAttribution,
  trackEvent,
  trackValidEmployerSubmit,
} from "../../../lib/tracking";
import { trackFormStart, trackFormValidationError } from "../../../lib/lp-events";
import { trackExperimentConvert } from "../../../lib/experiments";

type Surface = "preview" | "production";

type Props = {
  page: TrustFirstPageConfig;
  variant: TrustFirstVariant;
  surface?: Surface;
};

function readParam(name: string): string {
  if (typeof window === "undefined") return "";
  return new URLSearchParams(window.location.search).get(name) || "";
}

export default function EmployerQualificationForm({
  page,
  variant,
  surface = "preview",
}: Props) {
  const router = useRouter();
  const live = surface === "production";
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
  const [attrHidden, setAttrHidden] = useState<Record<string, string> | null>(null);

  const roles = EMPLOYER_ROLE_OPTIONS.includes(
    page.formRoleDefault as (typeof EMPLOYER_ROLE_OPTIONS)[number],
  )
    ? EMPLOYER_ROLE_OPTIONS
    : ([page.formRoleDefault, ...EMPLOYER_ROLE_OPTIONS] as const);

  const category = page.key === "us" ? "" : page.key;
  const lpVersion = live ? TRUST_FIRST_PRODUCTION_LP_VERSION : TRUST_FIRST_LP_VERSION;

  useEffect(() => {
    if (!live) return;
    const attr = readAttribution("us", {
      category,
      lp_version: lpVersion,
      baseline_label: US_BASELINE_LABEL,
    });
    setAttrHidden({
      gclid: attr.gclid || readParam("gclid"),
      gbraid: attr.gbraid || readParam("gbraid"),
      wbraid: attr.wbraid || readParam("wbraid"),
      utm_source: attr.utm_source || readParam("utm_source"),
      utm_medium: attr.utm_medium || readParam("utm_medium"),
      utm_campaign: attr.utm_campaign || readParam("utm_campaign"),
      utm_term: attr.utm_term || readParam("utm_term"),
      utm_content: attr.utm_content || readParam("utm_content"),
      utm_matchtype: attr.utm_matchtype || readParam("utm_matchtype"),
      lp_version: lpVersion,
      lp_key: page.key,
    });
  }, [live, lpVersion, page.key, category]);

  function markFormStart() {
    if (!live) return;
    trackFormStart({
      market: "us",
      lp_version: lpVersion,
      landing_page_type: TRUST_FIRST_PRODUCTION_LANDING_PAGE_TYPE,
      role_selected: role,
      start_reason: "trust_first_form",
    });
  }

  async function onSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError("");

    if (!name.trim() || !company.trim() || !email.trim() || !phone.trim()) {
      setError("Company name, your name, work email, and a US phone are required.");
      if (live) {
        trackFormValidationError({
          market: "us",
          error_category: "missing_required_field",
          form_step: "contact",
          landing_page_type: TRUST_FIRST_PRODUCTION_LANDING_PAGE_TYPE,
          lp_version: lpVersion,
        });
      }
      return;
    }

    const usPhone = validateUsPhone(phone);
    if (!usPhone.ok) {
      const jobSeeker = usPhone.code === "ph_job_seeker_phone";
      setError(jobSeeker ? PH_PHONE_CAREERS_MESSAGE : US_PHONE_ERROR);
      if (live) {
        trackFormValidationError({
          market: "us",
          error_category: jobSeeker ? "job_seeker_intent" : "invalid_us_phone",
          form_step: "contact",
          landing_page_type: TRUST_FIRST_PRODUCTION_LANDING_PAGE_TYPE,
          lp_version: lpVersion,
        });
        if (jobSeeker) {
          exitToCareers(VERIFIED_PROOF.careersUrl, {
            market: "us",
            redirect_location: "us_phone_validation",
            redirect_reason: "ph_phone_number",
            landing_page_type: TRUST_FIRST_PRODUCTION_LANDING_PAGE_TYPE,
            lp_version: lpVersion,
          });
        }
      }
      return;
    }

    setBusy(true);
    try {
      if (!live) {
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
            landing_page_url:
              typeof window !== "undefined" ? window.location.href.split("#")[0] : page.previewPath,
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
        return;
      }

      const attr = readAttribution("us", {
        category,
        variant,
        lp_variant: variant,
        lp_version: lpVersion,
        baseline_label: US_BASELINE_LABEL,
      });
      const clientScored = scoreLeadValue({
        intent: "employer",
        companySize: size,
        hiringTimeline: timeline,
      });
      const payload = {
        ...attr,
        name: name.trim(),
        email: email.trim(),
        phone: usPhone.e164,
        company: company.trim(),
        role,
        category,
        variant,
        intent: "employer" as const,
        website: honeypot,
        form_started_at: startedAt,
        market: "us",
        lp_version: attr.lp_version || lpVersion,
        submitted_at: new Date().toISOString(),
        company_size: size,
        hiring_timeline: timeline,
        lp_surface: "trust_first",
        cta_mode: "form_primary",
        landing_type: "form_lp",
        lp_variant: variant,
        lp_key: page.key,
        gclid: attr.gclid || readParam("gclid"),
        gbraid: attr.gbraid || readParam("gbraid"),
        wbraid: attr.wbraid || readParam("wbraid"),
        utm_source: attr.utm_source || readParam("utm_source"),
        utm_medium: attr.utm_medium || readParam("utm_medium"),
        utm_campaign: attr.utm_campaign || readParam("utm_campaign"),
        utm_term: attr.utm_term || readParam("utm_term"),
        utm_content: attr.utm_content || readParam("utm_content"),
        utm_matchtype: attr.utm_matchtype || readParam("utm_matchtype"),
        landing_page_url:
          attr.landing_page_url ||
          (typeof window !== "undefined" ? window.location.href.split("#")[0] : page.productionPath),
      };

      const res = await fetch("/api/lead", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });
      const data = (await res.json().catch(() => ({}))) as {
        ok?: boolean;
        error?: string;
        code?: string;
        submission_id?: string;
        duplicate?: boolean;
        delivery?: string;
        conversion_eligible?: boolean;
        lead_score?: number;
        estimated_lead_value?: number;
        value_kind?: string;
        fit_label?: string;
      };

      if (!res.ok || !data.ok || !data.submission_id) {
        if (data.code === "job_seeker" || data.code === "honeypot" || data.code === "too_fast") {
          trackEvent("spam_or_applicant_rejected", {
            market: "us",
            code: data.code || "rejected",
          });
        }
        if (
          data.code === "delivery_failed" ||
          data.code === "delivery_not_configured" ||
          res.status === 502 ||
          res.status === 503
        ) {
          trackEvent("employer_inquiry_delivery_failed", {
            market: "us",
            category,
            variant,
            code: data.code || `http_${res.status}`,
          });
        }
        setError(
          data.error ||
            "We could not deliver your request just now. Please try again, or call us.",
        );
        return;
      }

      const eligible = data.conversion_eligible !== false && data.delivery !== "log_only";
      trackValidEmployerSubmit({
        market: "us",
        submissionId: data.submission_id,
        role,
        category,
        variant,
        conversionEligible: eligible,
        companySize: size,
        hiringTimeline: timeline,
        leadScore: typeof data.lead_score === "number" ? data.lead_score : clientScored.lead_score,
        estimatedLeadValue:
          typeof data.estimated_lead_value === "number"
            ? data.estimated_lead_value
            : clientScored.estimated_lead_value,
        valueKind: data.value_kind || clientScored.value_kind,
        fitLabel: data.fit_label || clientScored.fit_label,
        landingPage: attr.landing_page_url,
        lpVersion: attr.lp_version,
        lpSurface: "trust_first",
        ctaMode: "form_primary",
        lpVariant: variant,
      });
      if (eligible) {
        trackExperimentConvert("form_submit", {
          market: "us",
          category,
          submission_id: data.submission_id,
        });
      }
      setDone(true);
      const q = new URLSearchParams({
        market: "us",
        sid: data.submission_id,
      });
      if (category) q.set("category", category);
      if (variant) q.set("variant", variant);
      if (!eligible) q.set("eligible", "0");
      router.push(`/thank-you?${q.toString()}`);
    } catch {
      if (live) {
        trackEvent("employer_inquiry_delivery_failed", {
          market: "us",
          category,
          variant,
          code: "network_error",
        });
      }
      setError(
        live
          ? "Network error - your request was not sent. Please try again, or call us."
          : "Unable to submit this preview form.",
      );
    } finally {
      setBusy(false);
    }
  }

  function goCareers(e: React.MouseEvent<HTMLAnchorElement>) {
    e.preventDefault();
    if (live) {
      exitToCareers(VERIFIED_PROOF.careersUrl, {
        market: "us",
        redirect_location: "careers_link",
        redirect_reason: "careers_escape",
        landing_page_type: TRUST_FIRST_PRODUCTION_LANDING_PAGE_TYPE,
        lp_version: lpVersion,
      });
      return;
    }
    window.location.replace(VERIFIED_PROOF.careersUrl);
  }

  return (
    <div className="tf-card tf-form" id="gate">
      <h2>{page.formHeading}</h2>
      {live ? (
        <p className="tf-muted" style={{ marginBottom: "0.9rem" }}>
          For businesses hiring staff. A short call — not a contract.
        </p>
      ) : (
        <p className="tf-muted" style={{ marginBottom: "0.9rem" }}>
          For businesses hiring staff. This preview does not send a live inquiry.
        </p>
      )}
      {done ? (
        <p className="tf-ok">
          {live
            ? "Thanks. We received your request and will follow up shortly."
            : "Preview received. Nothing was sent to Virtual Coworker, Zoho, or email."}
        </p>
      ) : (
        <form onSubmit={onSubmit} noValidate>
          {live && attrHidden
            ? Object.entries(attrHidden).map(([key, value]) => (
                <input key={key} type="hidden" name={key} value={value} readOnly />
              ))
            : null}

          <label htmlFor="tf-company">Company name</label>
          <input
            id="tf-company"
            name="company"
            autoComplete="organization"
            value={company}
            onChange={(e) => {
              markFormStart();
              setCompany(e.target.value);
            }}
            required
          />

          <label htmlFor="tf-name">Your name</label>
          <input
            id="tf-name"
            name="name"
            autoComplete="name"
            value={name}
            onChange={(e) => {
              markFormStart();
              setName(e.target.value);
            }}
            required
          />

          <label htmlFor="tf-email">Business Email Address</label>
          <input
            id="tf-email"
            name="email"
            type="email"
            autoComplete="email"
            inputMode="email"
            value={email}
            onChange={(e) => {
              markFormStart();
              setEmail(e.target.value);
            }}
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
            onChange={(e) => {
              markFormStart();
              setPhone(formatPhoneInput(e.target.value, "us"));
            }}
            required
          />

          <label htmlFor="tf-role">Role needed</label>
          <select
            id="tf-role"
            name="role"
            value={role}
            onChange={(e) => {
              markFormStart();
              setRole(e.target.value);
            }}
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
            {busy ? (live ? "Sending…" : "Sending preview…") : page.cta}
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
