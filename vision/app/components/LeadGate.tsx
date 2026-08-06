"use client";

import { useEffect, useRef, useState } from "react";
import { useRouter } from "next/navigation";
import {
  captureAttribution,
  readAttribution,
  trackEvent,
  trackValidEmployerSubmit,
} from "../../lib/tracking";
import type { MarketId } from "../../config/markets";
import type { AbVariant, CategorySlug } from "../../config/categories";
import { formLabelForSlug } from "../../config/categories";

export type GateCopy = {
  eyebrow: string;
  title: string;
  intentLabel: string;
  intentPrimary: string;
  intentSecondary: string;
  divertTitle: string;
  divertBody: string;
  divertCta: string;
  careersHref: string;
  roleLabel: string;
  roles: string[];
  detailsLabel: string;
  nameLabel: string;
  namePlaceholder: string;
  emailLabel: string;
  emailPlaceholder: string;
  phoneLabel: string;
  phonePlaceholder: string;
  companyLabel: string;
  companyPlaceholder: string;
  submit: string;
  reassure: string;
  callLabel: string;
  phoneDisplay: string;
  phoneHref: string | null;
  doneTitle: string;
  doneBody: string;
  /** When false, hide phone block entirely (AU form-primary). */
  showPhone?: boolean;
};

function CallBlock({
  copy,
  market,
  solo,
  category,
  variant,
}: {
  copy: GateCopy;
  market: MarketId;
  solo?: boolean;
  category?: string;
  variant?: string;
}) {
  if (copy.showPhone === false || (!copy.phoneHref && !copy.phoneDisplay)) {
    return null;
  }
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
    return null;
  }
  return (
    <a
      className={cls}
      href={copy.phoneHref}
      onClick={() =>
        trackEvent("phone_cta_clicked", {
          market,
          category: category || "",
          variant: variant || "",
          is_qualified_call: false,
        })
      }
    >
      {inner}
    </a>
  );
}

export default function LeadGate({
  copy,
  market,
  category,
  variant,
  preselectedRole,
}: {
  copy: GateCopy;
  market: MarketId;
  category?: CategorySlug | null;
  variant?: AbVariant;
  preselectedRole?: string | null;
}) {
  const router = useRouter();
  const initialRole =
    preselectedRole ||
    (category ? formLabelForSlug(category) : null);
  const [intent, setIntent] = useState<"employer" | "job_seeker" | null>(null);
  const [role, setRole] = useState<string | null>(initialRole);
  const [done, setDone] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [fieldErrors, setFieldErrors] = useState<Record<string, string>>({});
  const [startedAt, setStartedAt] = useState<number | null>(null);
  const startedRef = useRef(false);

  useEffect(() => {
    captureAttribution(market, {
      category: category || "",
      variant: variant || "",
    });
  }, [market, category, variant]);

  useEffect(() => {
    if (initialRole) setRole(initialRole);
  }, [initialRole]);

  function markStart() {
    if (startedRef.current) return;
    startedRef.current = true;
    const t = Date.now();
    setStartedAt(t);
    trackEvent("employer_form_started", {
      market,
      category: category || "",
      variant: variant || "",
      gate_variant: "inline",
    });
  }

  function onEmployerGate() {
    setIntent("employer");
    setError(null);
    trackEvent("employer_gate_selected", {
      market,
      category: category || "",
      variant: variant || "",
      gate_variant: "inline",
      intent: "employer",
    });
    markStart();
  }

  function onJobSeekerGate() {
    setIntent("job_seeker");
    setError(null);
    // Interaction only — primary conversion never fires for job seekers.
    // job_seeker_redirected fires when they click through to /ph.
  }

  function validateClient(fd: FormData): Record<string, string> {
    const errs: Record<string, string> = {};
    if (!String(fd.get("name") || "").trim()) errs.name = "Enter your name.";
    if (!String(fd.get("email") || "").trim()) errs.email = "Enter your work email.";
    if (!String(fd.get("phone") || "").trim()) errs.phone = "Enter a business phone.";
    if (!String(fd.get("company") || "").trim()) errs.company = "Enter your company name.";
    if (!role) errs.role = "Select what you need help with.";
    return errs;
  }

  async function onSubmit(e: React.FormEvent<HTMLFormElement>) {
    e.preventDefault();
    setError(null);
    const form = e.currentTarget;
    const fd = new FormData(form);
    const errs = validateClient(fd);
    setFieldErrors(errs);
    if (Object.keys(errs).length) {
      trackEvent("employer_form_validation_error", {
        market,
        category: category || "",
        variant: variant || "",
        fields: Object.keys(errs).join(","),
      });
      return;
    }

    setSubmitting(true);
    const attr = readAttribution(market, {
      category: category || "",
      variant: variant || "",
    });
    const payload = {
      ...attr,
      name: String(fd.get("name") || ""),
      email: String(fd.get("email") || ""),
      phone: String(fd.get("phone") || ""),
      company: String(fd.get("company") || ""),
      role: role || "",
      category: category || "",
      variant: variant || "",
      intent: "employer",
      website: String(fd.get("website") || ""),
      form_started_at: startedAt || Date.now(),
      market,
      lp_version: attr.lp_version || "stage1-v7",
      submitted_at: new Date().toISOString(),
    };

    try {
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
      };

      if (!res.ok || !data.ok || !data.submission_id) {
        if (data.code === "job_seeker" || data.code === "honeypot" || data.code === "too_fast") {
          trackEvent("spam_or_applicant_rejected", {
            market,
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
            market,
            category: category || "",
            variant: variant || "",
            code: data.code || `http_${res.status}`,
          });
        }
        setError(
          data.error ||
            "We could not deliver your request just now. Please try again" +
              (copy.phoneHref ? ", or call us." : "."),
        );
        setSubmitting(false);
        return;
      }

      const eligible = data.conversion_eligible !== false && data.delivery !== "log_only";
      trackValidEmployerSubmit({
        market,
        submissionId: data.submission_id,
        role: role || "",
        category: category || "",
        variant: variant || "",
        conversionEligible: eligible,
      });
      setDone(true);
      setSubmitting(false);
      const q = new URLSearchParams({
        market,
        sid: data.submission_id,
      });
      if (category) q.set("category", category);
      if (variant) q.set("variant", variant);
      if (!eligible) q.set("eligible", "0");
      router.push(`/thank-you?${q.toString()}`);
    } catch {
      trackEvent("employer_inquiry_delivery_failed", {
        market,
        category: category || "",
        variant: variant || "",
        code: "network_error",
      });
      setError(
        "Network error — your request was not sent. Please try again" +
          (copy.phoneHref ? ", or call us." : "."),
      );
      setSubmitting(false);
    }
  }

  return (
    <aside className="gate-card anim-rise-d1" id="gate">
      <div className="gate-card-head">
        <p className="gate-card-eyebrow">{copy.eyebrow}</p>
        <h2>{copy.title}</h2>
      </div>

      {done ? (
        <div className="gate-done">
          <p className="gate-done-mark" aria-hidden>
            ✓
          </p>
          <h3>{copy.doneTitle}</h3>
          <p>{copy.doneBody}</p>
          <CallBlock
            copy={copy}
            market={market}
            solo
            category={category || undefined}
            variant={variant}
          />
        </div>
      ) : (
        <div className="gate-card-body">
          <fieldset className="gate-step">
            <legend>
              <b>1</b> {copy.intentLabel}
            </legend>
            <div className="gate-intent" role="group" aria-label={copy.intentLabel}>
              <button
                type="button"
                className={intent === "employer" ? "on" : ""}
                aria-pressed={intent === "employer"}
                onClick={onEmployerGate}
              >
                {copy.intentPrimary}
              </button>
              <button
                type="button"
                className={intent === "job_seeker" ? "on" : ""}
                aria-pressed={intent === "job_seeker"}
                onClick={onJobSeekerGate}
              >
                {copy.intentSecondary}
              </button>
            </div>
          </fieldset>

          {intent === "job_seeker" ? (
            <div className="gate-divert">
              <strong>{copy.divertTitle}</strong>
              <p>{copy.divertBody}</p>
              <a
                href={copy.careersHref}
                className="gate-submit"
                onClick={() =>
                  trackEvent("job_seeker_redirected", {
                    market,
                    category: category || "",
                    variant: variant || "",
                    gate_variant: "inline",
                    intent: "job_seeker",
                    destination: copy.careersHref,
                    primary_eligible: false,
                  })
                }
              >
                {copy.divertCta}
              </a>
            </div>
          ) : null}

          {intent === "employer" ? (
            <form onSubmit={onSubmit} noValidate>
              <fieldset className="gate-step">
                <legend>
                  <b>2</b> {copy.roleLabel}
                </legend>
                <div className="gate-chips" role="group" aria-label={copy.roleLabel}>
                  {copy.roles.map((o) => (
                    <button
                      type="button"
                      key={o}
                      className={role === o ? "on" : ""}
                      aria-pressed={role === o}
                      onClick={() => {
                        setRole(o);
                        markStart();
                      }}
                    >
                      {o}
                    </button>
                  ))}
                </div>
                {fieldErrors.role ? (
                  <p className="gate-field-error" role="alert">
                    {fieldErrors.role}
                  </p>
                ) : null}
              </fieldset>

              <fieldset className="gate-step">
                <legend>
                  <b>3</b> {copy.detailsLabel}
                </legend>
                <label className="gate-hp" aria-hidden="true">
                  Website
                  <input
                    type="text"
                    name="website"
                    tabIndex={-1}
                    autoComplete="off"
                    defaultValue=""
                  />
                </label>
                <div className="gate-fields">
                  <label>
                    <span className="gate-label">{copy.nameLabel}</span>
                    <input
                      type="text"
                      name="name"
                      autoComplete="name"
                      placeholder={copy.namePlaceholder}
                      aria-invalid={Boolean(fieldErrors.name)}
                      aria-describedby={fieldErrors.name ? "err-name" : undefined}
                      onFocus={markStart}
                    />
                    {fieldErrors.name ? (
                      <span id="err-name" className="gate-field-error" role="alert">
                        {fieldErrors.name}
                      </span>
                    ) : null}
                  </label>
                  <label>
                    <span className="gate-label">{copy.emailLabel}</span>
                    <input
                      type="email"
                      name="email"
                      autoComplete="email"
                      placeholder={copy.emailPlaceholder}
                      aria-invalid={Boolean(fieldErrors.email)}
                      aria-describedby={fieldErrors.email ? "err-email" : undefined}
                    />
                    {fieldErrors.email ? (
                      <span id="err-email" className="gate-field-error" role="alert">
                        {fieldErrors.email}
                      </span>
                    ) : null}
                  </label>
                  <label>
                    <span className="gate-label">{copy.phoneLabel}</span>
                    <input
                      type="tel"
                      name="phone"
                      autoComplete="tel"
                      placeholder={copy.phonePlaceholder}
                      aria-invalid={Boolean(fieldErrors.phone)}
                      aria-describedby={fieldErrors.phone ? "err-phone" : undefined}
                    />
                    {fieldErrors.phone ? (
                      <span id="err-phone" className="gate-field-error" role="alert">
                        {fieldErrors.phone}
                      </span>
                    ) : null}
                  </label>
                  <label>
                    <span className="gate-label">{copy.companyLabel}</span>
                    <input
                      type="text"
                      name="company"
                      autoComplete="organization"
                      placeholder={copy.companyPlaceholder}
                      aria-invalid={Boolean(fieldErrors.company)}
                      aria-describedby={fieldErrors.company ? "err-company" : undefined}
                    />
                    {fieldErrors.company ? (
                      <span id="err-company" className="gate-field-error" role="alert">
                        {fieldErrors.company}
                      </span>
                    ) : null}
                  </label>
                </div>
              </fieldset>

              {error ? (
                <p className="gate-reassure" role="alert" style={{ color: "#9f2d2d" }}>
                  {error}
                </p>
              ) : null}

              <button type="submit" className="gate-submit" disabled={submitting}>
                {submitting ? "Sending…" : copy.submit}
              </button>
              <p className="gate-reassure">{copy.reassure}</p>
            </form>
          ) : null}

          {intent === null ? (
            <p className="gate-reassure">Choose one option to continue.</p>
          ) : null}

          {copy.showPhone !== false && copy.phoneHref ? (
            <>
              <div className="gate-or">
                <span>or</span>
              </div>
              <CallBlock
                copy={copy}
                market={market}
                category={category || undefined}
                variant={variant}
              />
            </>
          ) : null}
        </div>
      )}
    </aside>
  );
}
