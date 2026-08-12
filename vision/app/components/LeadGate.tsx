"use client";

import { useEffect, useRef, useState } from "react";
import { useRouter } from "next/navigation";
import {
  captureAttribution,
  readAttribution,
  trackEvent,
  trackPhoneClick,
  trackValidEmployerSubmit,
} from "../../lib/tracking";
import { exitToCareers } from "../../lib/job-seeker-exit";
import {
  assignExperiment,
  trackExperimentConvert,
  trackExperimentView,
  type ExpVariant,
} from "../../lib/experiments";
import {
  GATE_ASSIST_EVENT,
  type GateAssistDetail,
} from "../../lib/focus-gate";
import type { MarketId } from "../../config/markets";
import type { AbVariant, CategorySlug } from "../../config/categories";
import { formLabelForSlug } from "../../config/categories";
import {
  COMPANY_SIZE_OPTIONS,
  POSITIONS_OPTIONS,
  SCHEDULE_OPTIONS,
  scoreLeadValue,
  type CompanySizeId,
  type PositionsId,
  type ScheduleId,
} from "../../config/lead-value";
import {
  formatPhoneInput,
  normalizePhoneForStorage,
} from "../../lib/phone-format";

const GATE_TITLES: Record<ExpVariant, { title: string; eyebrowSuffix: string }> = {
  a: { title: "Start Hiring - 2 minutes.", eyebrowSuffix: "2 minutes" },
  b: { title: "Start Hiring - short form.", eyebrowSuffix: "about a minute" },
  c: { title: "Start Hiring - 2 minutes.", eyebrowSuffix: "2 minutes" },
};

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
      onClick={() => {
        trackPhoneClick({
          market,
          category: category || "",
          variant: variant || "",
        });
        trackExperimentConvert("phone_click", {
          market,
          source: "lead_gate",
        });
      }}
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
  assumeEmployer = false,
  lpSurface = "form",
  preselectedCompanySize = null,
  preselectedPositions = null,
  compactAfterQuiz = false,
  ctaMode,
}: {
  copy: GateCopy;
  market: MarketId;
  category?: CategorySlug | null;
  variant?: AbVariant;
  preselectedRole?: string | null;
  /** Quiz LP follow-up: start on employer path (still allows job-seeker divert). */
  assumeEmployer?: boolean;
  lpSurface?: "form" | "quiz";
  preselectedCompanySize?: CompanySizeId | string | null;
  preselectedPositions?: PositionsId | string | null;
  /** Quiz LP after reward: name/email/phone/company only (role + size + seats known). */
  compactAfterQuiz?: boolean;
  ctaMode?: "form_primary" | "quiz_lp";
}) {
  const router = useRouter();
  const initialRole =
    preselectedRole || (category ? formLabelForSlug(category) : null);
  const [intent, setIntent] = useState<"employer" | "job_seeker" | null>(
    assumeEmployer ? "employer" : null,
  );
  const [role, setRole] = useState<string | null>(initialRole);
  const [done, setDone] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [fieldErrors, setFieldErrors] = useState<Record<string, string>>({});
  const [startedAt, setStartedAt] = useState<number | null>(null);
  const startedRef = useRef(false);
  const exitingSeeker = useRef(false);
  const [headlineVariant, setHeadlineVariant] = useState<ExpVariant>("a");
  const [roleEmphasize, setRoleEmphasize] = useState(false);
  const [companySize, setCompanySize] = useState<CompanySizeId | null>(() => {
    const id = String(preselectedCompanySize || "").trim();
    return COMPANY_SIZE_OPTIONS.some((o) => o.id === id)
      ? (id as CompanySizeId)
      : null;
  });
  const [positionsNeeded, setPositionsNeeded] = useState<PositionsId | null>(
    () => {
      const id = String(preselectedPositions || "").trim();
      return POSITIONS_OPTIONS.some((o) => o.id === id)
        ? (id as PositionsId)
        : null;
    },
  );
  const [schedule, setSchedule] = useState<ScheduleId | null>(null);
  const [phone, setPhone] = useState("");
  const resolvedCtaMode = ctaMode || (lpSurface === "quiz" ? "quiz_lp" : "form_primary");

  useEffect(() => {
    captureAttribution(market, {
      category: category || "",
      variant: variant || "",
      lp_variant: lpSurface === "quiz" ? "quiz" : "",
    });
  }, [market, category, variant, lpSurface]);

  useEffect(() => {
    const v = assignExperiment("gate_headline");
    setHeadlineVariant(v);
    trackExperimentView("gate_headline", v, { market });
  }, [market]);

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
      lp_surface: lpSurface,
      cta_mode: resolvedCtaMode,
      landing_type: resolvedCtaMode === "quiz_lp" ? "quiz_lp" : "form_lp",
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
      lp_surface: lpSurface,
      cta_mode: resolvedCtaMode,
      landing_type: resolvedCtaMode === "quiz_lp" ? "quiz_lp" : "form_lp",
    });
    markStart();
  }

  useEffect(() => {
    const onAssist = (e: Event) => {
      const detail = (e as CustomEvent<GateAssistDetail>).detail || {};
      if (detail.intent === "employer") {
        setIntent((prev) => {
          if (prev === "employer") return prev;
          queueMicrotask(() => {
            trackEvent("employer_gate_selected", {
              market,
              category: category || "",
              variant: variant || "",
              gate_variant: "inline",
              intent: "employer",
              source: "gate_assist",
              lp_surface: lpSurface,
              cta_mode: resolvedCtaMode,
              landing_type: resolvedCtaMode === "quiz_lp" ? "quiz_lp" : "form_lp",
            });
            markStart();
          });
          return "employer";
        });
        setError(null);
      }
      const assistRole = detail.role?.trim();
      if (assistRole && copy.roles.includes(assistRole)) {
        setRole(assistRole);
        markStart();
      }
      if (detail.emphasize === "role") {
        setRoleEmphasize(true);
        window.setTimeout(() => setRoleEmphasize(false), 2400);
        window.setTimeout(() => {
          const gate = document.getElementById("gate");
          const selected = gate?.querySelector(
            ".gate-chips button.on",
          ) as HTMLElement | null;
          const chip =
            selected ||
            (gate?.querySelector(
              ".gate-chips button, [data-gate-role-step] .gate-chips",
            ) as HTMLElement | null);
          try {
            chip?.focus({ preventScroll: true });
          } catch {
            /* ignore */
          }
        }, 80);
      }
    };
    window.addEventListener(GATE_ASSIST_EVENT, onAssist);
    return () => window.removeEventListener(GATE_ASSIST_EVENT, onAssist);
  }, [market, category, variant, copy.roles, lpSurface]);

  function onJobSeekerGate() {
    if (exitingSeeker.current) return;
    exitingSeeker.current = true;
    setError(null);
    exitToCareers(copy.careersHref, {
      market,
      category: category || "",
      variant: variant || "",
      gate_variant: "inline",
      source: "lead_gate",
      lp_surface: lpSurface,
      cta_mode: resolvedCtaMode,
      landing_type: resolvedCtaMode === "quiz_lp" ? "quiz_lp" : "form_lp",
    });
  }

  function validateClient(fd: FormData): Record<string, string> {
    const errs: Record<string, string> = {};
    if (!String(fd.get("name") || "").trim()) errs.name = "Enter your name.";
    if (!String(fd.get("email") || "").trim()) errs.email = "Enter your work email.";
    if (!phone.trim() && !String(fd.get("phone") || "").trim()) {
      errs.phone = "Enter a business phone.";
    }
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
        lp_surface: lpSurface,
        cta_mode: resolvedCtaMode,
        landing_type: resolvedCtaMode === "quiz_lp" ? "quiz_lp" : "form_lp",
      });
      return;
    }

    setSubmitting(true);
    const attr = readAttribution(market, {
      category: category || "",
      variant: variant || "",
      lp_variant: lpSurface === "quiz" ? "quiz" : "",
    });
    const clientScored = scoreLeadValue({
      intent: "employer",
      companySize,
      positionsNeeded,
    });
    const payload = {
      ...attr,
      name: String(fd.get("name") || ""),
      email: String(fd.get("email") || ""),
      phone:
        normalizePhoneForStorage(phone || String(fd.get("phone") || ""), market) ||
        String(fd.get("phone") || "").trim(),
      company: String(fd.get("company") || ""),
      role: role || "",
      category: category || "",
      variant: variant || "",
      intent: "employer",
      website: String(fd.get("website") || ""),
      form_started_at: startedAt || Date.now(),
      market,
      lp_version: attr.lp_version || "stage1-v8",
      submitted_at: new Date().toISOString(),
      company_size: companySize || "",
      positions_needed: positionsNeeded || "",
      schedule: schedule || "",
      hiring_timeline: "",
      lp_surface: lpSurface,
      cta_mode: resolvedCtaMode,
      landing_type: resolvedCtaMode === "quiz_lp" ? "quiz_lp" : "form_lp",
      lp_variant: lpSurface === "quiz" ? "quiz" : attr.lp_variant || "",
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
        lead_score?: number;
        estimated_lead_value?: number;
        value_kind?: string;
        fit_label?: string;
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
        companySize: companySize || "",
        positionsNeeded: positionsNeeded || "",
        hiringTimeline: "",
        leadScore: typeof data.lead_score === "number" ? data.lead_score : clientScored.lead_score,
        estimatedLeadValue:
          typeof data.estimated_lead_value === "number"
            ? data.estimated_lead_value
            : clientScored.estimated_lead_value,
        valueKind: data.value_kind || clientScored.value_kind,
        fitLabel: data.fit_label || clientScored.fit_label,
        landingPage: attr.landing_page_url,
        utmSource: attr.utm_source,
        utmMedium: attr.utm_medium,
        utmCampaign: attr.utm_campaign,
        utmTerm: attr.utm_term,
        utmContent: attr.utm_content,
        gclid: attr.gclid,
        gbraid: attr.gbraid,
        wbraid: attr.wbraid,
        submittedAt: payload.submitted_at,
        lpSurface,
        ctaMode: resolvedCtaMode,
        lpVariant: lpSurface === "quiz" ? "quiz" : attr.lp_variant || "",
      });
      if (eligible) {
        trackExperimentConvert("form_submit", {
          market,
          category: category || "",
          submission_id: data.submission_id,
        });
      }
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
        "Network error - your request was not sent. Please try again" +
          (copy.phoneHref ? ", or call us." : "."),
      );
      setSubmitting(false);
    }
  }

  const gateFrame = GATE_TITLES[headlineVariant] || GATE_TITLES.a;
  const isGenericTitle = /start hiring|tell us who you need/i.test(copy.title);
  const displayTitle = isGenericTitle ? gateFrame.title : copy.title;
  const displayEyebrow = isGenericTitle
    ? copy.eyebrow.replace(/about a minute|2 minutes/i, gateFrame.eyebrowSuffix)
    : copy.eyebrow;

  const hideRoleStep = Boolean(initialRole && assumeEmployer);
  const hideQualifyChips = compactAfterQuiz && Boolean(companySize && positionsNeeded);
  const hideIntentStep = compactAfterQuiz && assumeEmployer;
  const roleStepNum = hideIntentStep ? 1 : 2;
  const qualifyStepNum = hideIntentStep ? (hideRoleStep ? 1 : 2) : hideRoleStep ? 2 : 3;
  const detailsStepNum = hideIntentStep
    ? hideRoleStep && hideQualifyChips
      ? 1
      : hideRoleStep || hideQualifyChips
        ? 2
        : 3
    : hideRoleStep && hideQualifyChips
      ? 2
      : hideRoleStep || hideQualifyChips
        ? 3
        : 4;

  useEffect(() => {
    if (compactAfterQuiz && assumeEmployer) markStart();
    // eslint-disable-next-line react-hooks/exhaustive-deps -- once on reveal
  }, [compactAfterQuiz, assumeEmployer]);

  return (
    <aside
      className={`gate-card anim-rise-d1${compactAfterQuiz ? " gate-card-quiz-reveal" : ""}`}
      id="gate"
      data-exp-gate={headlineVariant}
      data-cta-mode={resolvedCtaMode}
      data-lp-surface={lpSurface}
      data-landing-type={resolvedCtaMode === "quiz_lp" ? "quiz_lp" : "form_lp"}
    >
      <div className="gate-card-head">
        <p className="gate-card-eyebrow">{displayEyebrow}</p>
        <h2>{displayTitle}</h2>
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
          {hideIntentStep ? null : (
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
          )}

          {intent === "employer" ? (
            <form onSubmit={onSubmit} noValidate>
              {!hideRoleStep ? (
                <fieldset
                  className={`gate-step${roleEmphasize ? " is-role-emphasize" : ""}`}
                  data-gate-role-step
                >
                  <legend>
                    <b>{roleStepNum}</b> {copy.roleLabel}
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
              ) : (
                <input type="hidden" name="role" value={role || ""} readOnly />
              )}

              {hideQualifyChips ? (
                <>
                  <input type="hidden" name="company_size" value={companySize || ""} readOnly />
                  <input type="hidden" name="positions_needed" value={positionsNeeded || ""} readOnly />
                  <input type="hidden" name="schedule" value={schedule || ""} readOnly />
                  {role || companySize || positionsNeeded || schedule ? (
                    <p className="gate-quiz-summary">
                      {[
                        role,
                        companySize,
                        positionsNeeded,
                        schedule,
                      ]
                        .filter(Boolean)
                        .join(" · ")}
                    </p>
                  ) : null}
                </>
              ) : (
                <fieldset className="gate-step gate-qualify">
                  <legend>
                    <b>{qualifyStepNum}</b> About the hire
                  </legend>
                  <p className="gate-sublabel">Company size</p>
                  <div className="gate-chips" role="group" aria-label="Company size">
                    {COMPANY_SIZE_OPTIONS.map((o) => (
                      <button
                        type="button"
                        key={o.id}
                        className={companySize === o.id ? "on" : ""}
                        aria-pressed={companySize === o.id}
                        onClick={() => {
                          setCompanySize(o.id);
                          markStart();
                        }}
                      >
                        {o.label}
                      </button>
                    ))}
                  </div>
                  <p className="gate-sublabel">How many positions?</p>
                  <div className="gate-chips" role="group" aria-label="Positions needed">
                    {POSITIONS_OPTIONS.map((o) => (
                      <button
                        type="button"
                        key={o.id}
                        className={positionsNeeded === o.id ? "on" : ""}
                        aria-pressed={positionsNeeded === o.id}
                        onClick={() => {
                          setPositionsNeeded(o.id);
                          markStart();
                        }}
                      >
                        {o.label}
                      </button>
                    ))}
                  </div>
                  <p className="gate-sublabel">Full-time or part-time?</p>
                  <div className="gate-chips" role="group" aria-label="Full-time or part-time">
                    {SCHEDULE_OPTIONS.map((o) => (
                      <button
                        type="button"
                        key={o.id}
                        className={schedule === o.id ? "on" : ""}
                        aria-pressed={schedule === o.id}
                        onClick={() => {
                          setSchedule(o.id);
                          markStart();
                        }}
                      >
                        {o.label}
                      </button>
                    ))}
                  </div>
                </fieldset>
              )}

              <fieldset className="gate-step">
                <legend>
                  <b>{detailsStepNum}</b> {copy.detailsLabel}
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
                      inputMode="tel"
                      autoComplete="tel"
                      autoCorrect="off"
                      spellCheck={false}
                      value={phone}
                      placeholder={copy.phonePlaceholder}
                      aria-invalid={Boolean(fieldErrors.phone)}
                      aria-describedby={fieldErrors.phone ? "err-phone" : undefined}
                      onChange={(e) => {
                        setPhone(formatPhoneInput(e.target.value, market));
                        markStart();
                      }}
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
