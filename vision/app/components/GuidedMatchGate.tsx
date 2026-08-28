"use client";

import { useEffect, useRef, useState } from "react";
import { useRouter } from "next/navigation";
import type { MarketId } from "../../config/markets";
import type { CategorySlug } from "../../config/categories";
import {
  GUIDED_MATCH_HOURS_MINIMUM_NOTE,
  GUIDED_MATCH_POSITIONS,
  GUIDED_MATCH_ROLES,
  GUIDED_MATCH_SCHEDULES,
  GUIDED_MATCH_SIZES,
  JOB_SEEKER_LINE,
  buildHiringMessage,
  firstGuidedMatchStep,
  hoursDefaultForMarket,
  marketLandingCopy,
  roleByChip,
  roleForCategory,
  type GuidedMatchStep,
} from "../../config/guided-match";
import {
  captureAttribution,
  readAttribution,
  trackEvent,
  trackValidEmployerSubmit,
} from "../../lib/tracking";
import { DEFAULT_CAREERS_URL } from "../../config/markets";
import { scoreLeadValue } from "../../config/lead-value";
import {
  canGoBack,
  diagnosticMatchPayload,
  guidedMatchLandingFlags,
  guidedMatchStepIndex,
  previousStep,
  shouldStartEmployerFormOnPii,
} from "../../lib/guided-match";

type Props = {
  market: MarketId;
  category?: CategorySlug | null;
  variant?: string;
  careersHref?: string;
  /** Skip the role/hours quiz. Name, email, and phone are the first fields. */
  contactFirst?: boolean;
  contactHeading?: string;
  /** Hide 1 of 3 / progress until the visitor has entered the quiz. */
  quietStart?: boolean;
  /** Optional preview identifier. Default empty so live /us tracking is unchanged. */
  lpVariant?: string;
  /**
   * When false, parent owns id="gate" (e.g. heading + chips as one scroll target).
   * Default true so live /us keeps the anchor on this card.
   */
  includeGateId?: boolean;
  /**
   * When true, role chips select only. Continue advances. Live /us stays false
   * so a role tap still moves to hours immediately.
   */
  explicitContinue?: boolean;
  /**
   * When true (or when explicitContinue is true), needs become one question per
   * screen: hours → people → optional size → contact. Live /us stays false.
   */
  sequentialNeeds?: boolean;
  /** Staffing-partner only. Default keeps "Get my hiring brief" on /us. */
  submitLabel?: string;
  /** "step" shows "Step 1 of N" plus a segmented bar. Default keeps "1 of 3". */
  progressLabel?: "step";
  /** Show hours and people as two always-visible questions. Default hides people until hours. */
  hoursQuestionSplit?: boolean;
  /** Marks the wrapper for challenger-scoped CSS. Default off so /us is unchanged. */
  spQuiz?: boolean;
  /** Page lp_version override (baseline). Default keeps global LP_VERSION. */
  lpVersion?: string;
  /**
   * Role pages: start with Hiring for preselected, but allow Change back to role.
   * Default false so locked category pages stay locked.
   */
  allowRoleChange?: boolean;
};

export default function GuidedMatchGate({
  market,
  category,
  variant = "",
  careersHref = DEFAULT_CAREERS_URL,
  contactFirst = false,
  contactHeading,
  quietStart = false,
  lpVariant = "",
  includeGateId = true,
  explicitContinue = false,
  sequentialNeeds = false,
  submitLabel,
  progressLabel,
  hoursQuestionSplit = false,
  spQuiz = false,
  lpVersion = "",
  allowRoleChange = false,
}: Props) {
  const router = useRouter();
  const pageRole = category ? roleForCategory(category) : null;
  const copy = marketLandingCopy(market);
  const hoursDefault = hoursDefaultForMarket(market);
  const useSequentialNeeds = sequentialNeeds || explicitContinue;

  const [roleUnlocked, setRoleUnlocked] = useState(false);
  const locked = Boolean(category) && !(allowRoleChange && roleUnlocked);
  const lockedRole = locked ? pageRole : null;

  const [step, setStep] = useState<GuidedMatchStep>(
    contactFirst
      ? "contact"
      : firstGuidedMatchStep(category, useSequentialNeeds),
  );
  const [roleChip, setRoleChip] = useState(pageRole?.chip || "");
  const [schedule, setSchedule] = useState("");
  const [positions, setPositions] = useState("");
  const [size, setSize] = useState("");
  const [tzNote, setTzNote] = useState("");
  const [phone, setPhone] = useState("");
  const [startedAt, setStartedAt] = useState(0);
  const [error, setError] = useState("");
  const [fieldErrors, setFieldErrors] = useState<Record<string, string>>({});
  const [submitting, setSubmitting] = useState(false);
  const startedRef = useRef(false);
  const matchStartedRef = useRef(false);
  const contactReachedRef = useRef(false);
  const exitingSeeker = useRef(false);

  const selected = lockedRole
    ? {
        formLabel: lockedRole.formLabel,
        category: lockedRole.category,
        chip: lockedRole.chip,
      }
    : roleByChip(roleChip);

  useEffect(() => {
    captureAttribution(market, {
      category: category || "",
      variant: variant || "",
      ...(lpVariant ? { lp_variant: lpVariant } : {}),
      ...(lpVersion ? { lp_version: lpVersion } : {}),
    });
  }, [market, category, variant, lpVariant, lpVersion]);

  function ctx() {
    return diagnosticMatchPayload({
      market,
      category: selected?.category || category || "",
      variant,
      lpVariant,
      lpVersion: lpVersion || undefined,
      rolePreselected: Boolean(category) && !roleUnlocked,
      schedule,
      positionsNeeded: positions,
      companySize: size,
    });
  }

  function changeRole() {
    if (!allowRoleChange) return;
    setRoleUnlocked(true);
    setStep("role");
  }

  function markMatchStarted(stepN: string, answer: string) {
    const extra = { ...ctx(), step: stepN, answer };
    if (!matchStartedRef.current) {
      matchStartedRef.current = true;
      trackEvent("quiz_started", extra);
      trackEvent("guided_match_started", { ...extra, alias_of: "quiz_started" });
    }
    trackEvent("quiz_step", extra);
  }

  function markFormStarted() {
    if (!shouldStartEmployerFormOnPii(startedRef.current)) return;
    startedRef.current = true;
    const t = Date.now();
    setStartedAt(t);
    const flags = guidedMatchLandingFlags(lpVariant, lpVersion || undefined);
    trackEvent("employer_form_started", {
      market,
      category: selected?.category || category || "",
      variant: variant || "",
      gate_variant: "inline",
      start_reason: "field_interaction",
      ...flags,
    });
    trackEvent("form_start", {
      market,
      category: selected?.category || category || "",
      variant: variant || "",
      alias_of: "employer_form_started",
      start_reason: "field_interaction",
      ...flags,
    });
  }

  function onRole(chip: string) {
    if (locked) return;
    setRoleChip(chip);
    markMatchStarted("1", chip);
    if (!explicitContinue) setStep("needs");
  }

  function continueRole() {
    if (!roleChip) return;
    setStep(useSequentialNeeds ? "hours" : "needs");
  }

  function onSchedule(id: string) {
    setSchedule(id);
    markMatchStarted("2", id);
  }

  function onPositions(id: string) {
    setPositions(id);
    markMatchStarted("2", id);
  }

  function onSize(id: string) {
    setSize(id);
    markMatchStarted("2", id);
  }

  function reachContact() {
    trackEvent("quiz_step_completed", {
      ...ctx(),
      step: "2",
      answer: "complete",
    });
    setStep("contact");
    if (!contactReachedRef.current) {
      contactReachedRef.current = true;
      const extra = {
        ...ctx(),
        result: selected?.formLabel || "",
        funnel_step: "contact_step_reached",
      };
      trackEvent("quiz_completed", extra);
      trackEvent("contact_step_reached", extra);
      trackEvent("lead_magnet_completed", {
        ...ctx(),
        magnet: "guided_match",
        result_role: selected?.formLabel || "",
      });
    }
  }

  function continueNeeds() {
    if (!schedule || !positions) return;
    reachContact();
  }

  function continueHours() {
    if (!schedule) return;
    setStep("people");
  }

  function continuePeople() {
    if (!positions) return;
    setStep("size");
  }

  function continueSize() {
    reachContact();
  }

  function skipSize() {
    setSize("");
    reachContact();
  }

  function onBack() {
    setFieldErrors({});
    setError("");
    setStep(previousStep(step, locked ? category : null, useSequentialNeeds));
  }

  function onCareers(e: React.MouseEvent<HTMLAnchorElement>) {
    e.preventDefault();
    if (exitingSeeker.current) return;
    exitingSeeker.current = true;
    const flags = guidedMatchLandingFlags(lpVariant, lpVersion || undefined);
    trackEvent("job_seeker_redirected", {
      market,
      category: selected?.category || category || "",
      variant: variant || "",
      intent: "job_seeker",
      destination: careersHref,
      primary_eligible: false,
      bidding_primary: false,
      source: "lead_gate_ungated_link",
      ...flags,
    });
    window.location.replace(careersHref);
  }

  async function onSubmit(e: React.FormEvent<HTMLFormElement>) {
    e.preventDefault();
    if (submitting) return;
    const form = e.currentTarget;
    const fd = new FormData(form);
    const name = String(fd.get("name") || "").trim();
    const email = String(fd.get("email") || "").trim();
    const errs: Record<string, string> = {};
    if (!name) errs.name = "Enter your name.";
    if (!email) errs.email = "Enter your business email address.";
    if (!phone.trim()) errs.phone = "Enter a phone number.";
    setFieldErrors(errs);
    setError("");
    if (Object.keys(errs).length) {
      trackEvent("employer_form_validation_error", {
        market,
        category: selected?.category || category || "",
        variant: variant || "",
        fields: Object.keys(errs).join(","),
        ...guidedMatchLandingFlags(lpVariant),
      });
      return;
    }

    setSubmitting(true);
    const flags = guidedMatchLandingFlags(lpVariant);
    const attr = readAttribution(market, {
      category: selected?.category || category || "",
      variant: variant || "",
      ...(lpVariant ? { lp_variant: lpVariant } : {}),
    });
    const scored = scoreLeadValue({
      intent: "employer",
      companySize: size,
      positionsNeeded: positions,
    });
    const payload = {
      ...attr,
      ...flags,
      name,
      email,
      phone: phone.trim(),
      company: String(fd.get("company") || "").trim(),
      role: selected?.formLabel || "",
      category: selected?.category || category || "",
      variant: variant || "",
      intent: "employer",
      website: String(fd.get("website") || ""),
      company_website: String(fd.get("company_website") || "").trim(),
      form_started_at: startedAt || Date.now(),
      market,
      submitted_at: new Date().toISOString(),
      company_size: size || "",
      positions_needed: positions || "",
      schedule: schedule || "",
      hiring_timeline: "",
      message: buildHiringMessage({
        hoursDefault,
        timezoneNote: tzNote,
      }),
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
        delivery?: string;
        conversion_eligible?: boolean;
        lead_score?: number;
        estimated_lead_value?: number;
        value_kind?: string;
        fit_label?: string;
      };

      if (!res.ok || !data.ok || !data.submission_id) {
        if (
          data.code === "job_seeker" ||
          data.code === "honeypot" ||
          data.code === "too_fast"
        ) {
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
            category: selected?.category || "",
            variant: variant || "",
            code: data.code || `http_${res.status}`,
          });
        }
        setError(
          data.error ||
            "We could not deliver your request just now. Please try again, or call us.",
        );
        setSubmitting(false);
        return;
      }

      const eligible =
        data.conversion_eligible !== false && data.delivery !== "log_only";
      trackValidEmployerSubmit({
        market,
        submissionId: data.submission_id,
        role: selected?.formLabel || "",
        category: selected?.category || category || "",
        variant: variant || "",
        conversionEligible: eligible,
        companySize: size || "",
        positionsNeeded: positions || "",
        hiringTimeline: "",
        leadScore:
          typeof data.lead_score === "number" ? data.lead_score : scored.lead_score,
        estimatedLeadValue:
          typeof data.estimated_lead_value === "number"
            ? data.estimated_lead_value
            : scored.estimated_lead_value,
        valueKind: data.value_kind || scored.value_kind,
        fitLabel: data.fit_label || scored.fit_label,
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
        lpSurface: "form",
        ctaMode: "form_primary",
        lpVariant: lpVariant || attr.lp_variant || "",
      });

      const q = new URLSearchParams({ market, sid: data.submission_id });
      const cat = selected?.category || category || "";
      if (cat) q.set("category", cat);
      if (variant) q.set("variant", variant);
      if (!eligible) q.set("eligible", "0");
      router.push(`/thank-you?${q.toString()}`);
    } catch {
      trackEvent("employer_inquiry_delivery_failed", {
        market,
        category: selected?.category || "",
        variant: variant || "",
        code: "network_error",
      });
      setError("Network error - your request was not sent. Please try again, or call us.");
      setSubmitting(false);
    }
  }

  const progress = guidedMatchStepIndex(
    step,
    locked ? category : null,
    contactFirst,
    useSequentialNeeds,
  );
  const showBack = canGoBack(
    step,
    locked ? category : null,
    contactFirst,
    useSequentialNeeds,
  );
  const hideQuizChrome =
    contactFirst ||
    (quietStart &&
      step === firstGuidedMatchStep(category, useSequentialNeeds));

  const showPositions = hoursQuestionSplit || Boolean(schedule);
  const showOptionalNeeds = Boolean(schedule && positions);
  const showNeedsContinue = explicitContinue || Boolean(schedule && positions);

  const hiringSummary = [selected?.chip, schedule, positions]
    .filter(Boolean)
    .join(" · ");

  const hiringForChip = lockedRole?.chip || roleChip;
  const hiringForLine =
    hiringForChip || allowRoleChange ? (
      <p className="gm-locked">
        {hiringForChip ? `Hiring for: ${hiringForChip}` : null}
        {allowRoleChange && locked && hiringForChip ? (
          <>
            {" · "}
            <button
              type="button"
              className="gm-change-role"
              onClick={changeRole}
            >
              Change
            </button>
          </>
        ) : null}
      </p>
    ) : null;

  return (
    <div
      className="gm-gate"
      id={includeGateId ? "gate" : undefined}
      data-contact-first={contactFirst || undefined}
      data-sp-quiz={spQuiz ? "true" : undefined}
    >
      {hideQuizChrome ? null : (
        <>
          {progressLabel === "step" ? (
            <div className="gm-bar-steps" aria-hidden="true">
              {Array.from({ length: progress.total }, (_, i) => (
                <span
                  key={i}
                  className={i < progress.shown ? "is-filled" : undefined}
                />
              ))}
            </div>
          ) : (
            <div className="gm-bar" aria-hidden="true">
              <span style={{ width: progress.pct }} />
            </div>
          )}
          <p className="gm-step-n">
            {progressLabel === "step"
              ? `Step ${progress.shown} of ${progress.total}`
              : `${progress.shown} of ${progress.total}`}
          </p>
        </>
      )}

      {step === "role" ? (
        <>
          <h2>What role are you hiring for?</h2>
          {explicitContinue ? <p className="gm-hint">Choose one.</p> : null}
          <div className="gm-chips" role="group" aria-label="Role">
            {GUIDED_MATCH_ROLES.map((r) => {
              const on = roleChip === r.chip;
              return (
                <button
                  key={r.id}
                  type="button"
                  className="gm-chip"
                  aria-pressed={on}
                  onClick={() => onRole(r.chip)}
                >
                  {on ? <span className="gm-check">✓</span> : null}
                  {r.chip}
                </button>
              );
            })}
          </div>
          {explicitContinue ? (
            <button
              className="gm-submit"
              type="button"
              onClick={continueRole}
              disabled={!roleChip}
            >
              Continue
            </button>
          ) : null}
          <Seeker href={careersHref} onClick={onCareers} />
        </>
      ) : null}

      {step === "hours" && useSequentialNeeds ? (
        <>
          <h2>How many hours per week?</h2>
          <p className="gm-hint">Choose one.</p>
          <p className="gm-hint">{GUIDED_MATCH_HOURS_MINIMUM_NOTE}</p>
          {hiringForLine}
          <div className="gm-chips" role="group" aria-label="Hours per week">
            {GUIDED_MATCH_SCHEDULES.map((s) => {
              const on = schedule === s.id;
              return (
                <button
                  key={s.id}
                  type="button"
                  className="gm-chip"
                  aria-pressed={on}
                  onClick={() => onSchedule(s.id)}
                >
                  {on ? <span className="gm-check">✓</span> : null}
                  {s.label}
                </button>
              );
            })}
          </div>
          <button
            className="gm-submit"
            type="button"
            onClick={continueHours}
            disabled={!schedule}
          >
            Continue
          </button>
          {showBack ? (
            <button className="gm-ghost" type="button" onClick={onBack}>
              Back
            </button>
          ) : null}
          <Seeker href={careersHref} onClick={onCareers} />
        </>
      ) : null}

      {step === "people" && useSequentialNeeds ? (
        <>
          <h2>How many people do you need?</h2>
          <p className="gm-hint">Choose one.</p>
          {hiringSummary ? <p className="gm-locked">{hiringSummary}</p> : null}
          <div className="gm-chips" role="group" aria-label="People needed">
            {GUIDED_MATCH_POSITIONS.map((s) => {
              const on = positions === s.id;
              return (
                <button
                  key={s.id}
                  type="button"
                  className="gm-chip"
                  aria-pressed={on}
                  onClick={() => onPositions(s.id)}
                >
                  {on ? <span className="gm-check">✓</span> : null}
                  {s.label}
                </button>
              );
            })}
          </div>
          <button
            className="gm-submit"
            type="button"
            onClick={continuePeople}
            disabled={!positions}
          >
            Continue
          </button>
          {showBack ? (
            <button className="gm-ghost" type="button" onClick={onBack}>
              Back
            </button>
          ) : null}
          <Seeker href={careersHref} onClick={onCareers} />
        </>
      ) : null}

      {step === "size" && useSequentialNeeds ? (
        <>
          <h2>About how many people in your company?</h2>
          <p className="gm-hint">Optional. Choose one or skip.</p>
          {hiringSummary ? <p className="gm-locked">{hiringSummary}</p> : null}
          <div className="gm-chips" role="group" aria-label="Company size">
            {GUIDED_MATCH_SIZES.map((s) => {
              const on = size === s.id;
              return (
                <button
                  key={s.id}
                  type="button"
                  className="gm-chip"
                  aria-pressed={on}
                  onClick={() => onSize(s.id)}
                >
                  {on ? <span className="gm-check">✓</span> : null}
                  {s.label}
                </button>
              );
            })}
          </div>
          <label className="gm-label" htmlFor="gm-tz">
            Different hours or time zone? (optional)
          </label>
          <input
            id="gm-tz"
            value={tzNote}
            onChange={(e) => setTzNote(e.target.value)}
            placeholder="Only if it is not the usual hours for this page"
          />
          <button className="gm-submit" type="button" onClick={continueSize}>
            Continue
          </button>
          <button className="gm-ghost" type="button" onClick={skipSize}>
            Skip
          </button>
          {showBack ? (
            <button className="gm-ghost" type="button" onClick={onBack}>
              Back
            </button>
          ) : null}
          <Seeker href={careersHref} onClick={onCareers} />
        </>
      ) : null}

      {step === "needs" && !useSequentialNeeds ? (
        <>
          <h2>
            {category
              ? `Tell us about the ${lockedRole?.chip.toLowerCase() || "role"} help you need.`
              : "Hours and how many people"}
          </h2>
          {hiringForLine}

          {hoursQuestionSplit ? (
            <div className="gm-needs-split">
              <div className="gm-q">
                <p className="gm-label" id="gm-sched-label">
                  How many hours per week?
                </p>
                <p className="gm-hint">Choose one.</p>
                <p className="gm-hint">{GUIDED_MATCH_HOURS_MINIMUM_NOTE}</p>
                <div
                  className="gm-chips"
                  role="group"
                  aria-labelledby="gm-sched-label"
                >
                  {GUIDED_MATCH_SCHEDULES.map((s) => {
                    const on = schedule === s.id;
                    return (
                      <button
                        key={s.id}
                        type="button"
                        className="gm-chip"
                        aria-pressed={on}
                        onClick={() => onSchedule(s.id)}
                      >
                        {on ? <span className="gm-check">✓</span> : null}
                        {s.label}
                      </button>
                    );
                  })}
                </div>
              </div>
              {showPositions ? (
                <div className="gm-q">
                  <p className="gm-label" id="gm-pos-label">
                    How many people do you need?
                  </p>
                  <p className="gm-hint">Choose one.</p>
                  <div
                    className="gm-chips"
                    role="group"
                    aria-labelledby="gm-pos-label"
                  >
                    {GUIDED_MATCH_POSITIONS.map((s) => {
                      const on = positions === s.id;
                      return (
                        <button
                          key={s.id}
                          type="button"
                          className="gm-chip"
                          aria-pressed={on}
                          onClick={() => onPositions(s.id)}
                        >
                          {on ? <span className="gm-check">✓</span> : null}
                          {s.label}
                        </button>
                      );
                    })}
                  </div>
                </div>
              ) : null}
            </div>
          ) : (
            <>
              <p className="gm-label" id="gm-sched-label">
                Full-time or part-time
              </p>
              <p className="gm-hint">{GUIDED_MATCH_HOURS_MINIMUM_NOTE}</p>
              <div
                className="gm-chips"
                role="group"
                aria-labelledby="gm-sched-label"
              >
                {GUIDED_MATCH_SCHEDULES.map((s) => {
                  const on = schedule === s.id;
                  return (
                    <button
                      key={s.id}
                      type="button"
                      className="gm-chip"
                      aria-pressed={on}
                      onClick={() => onSchedule(s.id)}
                    >
                      {on ? <span className="gm-check">✓</span> : null}
                      {s.label}
                    </button>
                  );
                })}
              </div>

              {showPositions ? (
                <>
                  <p className="gm-label" id="gm-pos-label">
                    How many people
                  </p>
                  <div
                    className="gm-chips"
                    role="group"
                    aria-labelledby="gm-pos-label"
                  >
                    {GUIDED_MATCH_POSITIONS.map((s) => {
                      const on = positions === s.id;
                      return (
                        <button
                          key={s.id}
                          type="button"
                          className="gm-chip"
                          aria-pressed={on}
                          onClick={() => onPositions(s.id)}
                        >
                          {on ? <span className="gm-check">✓</span> : null}
                          {s.label}
                        </button>
                      );
                    })}
                  </div>
                </>
              ) : null}
            </>
          )}

          {showOptionalNeeds ? (
            <>
              <p className="gm-label" id="gm-size-label">
                Company size (optional)
              </p>
              <div className="gm-chips" role="group" aria-labelledby="gm-size-label">
                {GUIDED_MATCH_SIZES.map((s) => {
                  const on = size === s.id;
                  return (
                    <button
                      key={s.id}
                      type="button"
                      className="gm-chip"
                      aria-pressed={on}
                      onClick={() => onSize(s.id)}
                    >
                      {on ? <span className="gm-check">✓</span> : null}
                      {s.label}
                    </button>
                  );
                })}
              </div>
              <label className="gm-label" htmlFor="gm-tz">
                Different hours or time zone? (optional)
              </label>
              <input
                id="gm-tz"
                value={tzNote}
                onChange={(e) => setTzNote(e.target.value)}
                placeholder="Only if it is not the usual hours for this page"
              />
            </>
          ) : null}

          {showNeedsContinue ? (
            <button
              className="gm-submit"
              type="button"
              onClick={continueNeeds}
              disabled={explicitContinue && (!schedule || !positions)}
            >
              Continue
            </button>
          ) : null}

          {showBack ? (
            <button className="gm-ghost" type="button" onClick={onBack}>
              Back
            </button>
          ) : null}
          <Seeker href={careersHref} onClick={onCareers} />
        </>
      ) : null}

      {step === "contact" ? (
        <>
          <h2>
            {contactHeading || "Where should we send your hiring brief?"}
          </h2>
          {contactFirst ? (
            <p className="gm-hint">
              Employers only. Name, email, and phone start a hiring conversation. Not an instant hire.
            </p>
          ) : (
            <p className="gm-hint">{hiringSummary}</p>
          )}
          <form onSubmit={onSubmit} noValidate>
            <div className="gm-hid" aria-hidden="true">
              <label>
                Website
                <input name="website" tabIndex={-1} autoComplete="off" defaultValue="" />
              </label>
            </div>
            <div className="gm-pair">
              <div>
                <label className="gm-label" htmlFor="gm-name">
                  Full name
                </label>
                <input
                  id="gm-name"
                  name="name"
                  autoComplete="name"
                  aria-invalid={Boolean(fieldErrors.name)}
                  onFocus={markFormStarted}
                />
                {fieldErrors.name ? (
                  <span className="gm-err" role="alert">
                    {fieldErrors.name}
                  </span>
                ) : null}
              </div>
              <div>
                <label className="gm-label" htmlFor="gm-email">
                  Business Email Address
                </label>
                <input
                  id="gm-email"
                  name="email"
                  type="email"
                  autoComplete="email"
                  aria-invalid={Boolean(fieldErrors.email)}
                  onFocus={markFormStarted}
                />
                {fieldErrors.email ? (
                  <span className="gm-err" role="alert">
                    {fieldErrors.email}
                  </span>
                ) : null}
              </div>
            </div>

            <label className="gm-label" htmlFor="gm-phone">
              Phone
            </label>
            <input
              id="gm-phone"
              name="phone"
              type="tel"
              inputMode="tel"
              autoComplete="tel"
              placeholder={copy.phonePlaceholder}
              value={phone}
              aria-invalid={Boolean(fieldErrors.phone)}
              onFocus={markFormStarted}
              onChange={(e) => {
                setPhone(e.target.value);
                markFormStarted();
              }}
            />
            {fieldErrors.phone ? (
              <span className="gm-err" role="alert">
                {fieldErrors.phone}
              </span>
            ) : null}

            <label className="gm-label" htmlFor="gm-site">
              Company website (optional)
            </label>
            <input
              id="gm-site"
              name="company_website"
              placeholder="https://"
              autoComplete="url"
            />

            {contactFirst && !locked ? (
              <>
                <p className="gm-label" id="gm-opt-role">
                  Role (optional)
                </p>
                <div className="gm-chips" role="group" aria-labelledby="gm-opt-role">
                  {GUIDED_MATCH_ROLES.map((r) => {
                    const on = roleChip === r.chip;
                    return (
                      <button
                        key={r.id}
                        type="button"
                        className="gm-chip"
                        aria-pressed={on}
                        onClick={() => {
                          setRoleChip(r.chip);
                          markMatchStarted("1", r.chip);
                        }}
                      >
                        {on ? <span className="gm-check">✓</span> : null}
                        {r.chip}
                      </button>
                    );
                  })}
                </div>
                <p className="gm-label" id="gm-opt-sched">
                  Hours (optional)
                </p>
                <p className="gm-hint">{GUIDED_MATCH_HOURS_MINIMUM_NOTE}</p>
                <div className="gm-chips" role="group" aria-labelledby="gm-opt-sched">
                  {GUIDED_MATCH_SCHEDULES.map((s) => {
                    const on = schedule === s.id;
                    return (
                      <button
                        key={s.id}
                        type="button"
                        className="gm-chip"
                        aria-pressed={on}
                        onClick={() => {
                          setSchedule(s.id);
                          markMatchStarted("2", s.id);
                        }}
                      >
                        {on ? <span className="gm-check">✓</span> : null}
                        {s.label}
                      </button>
                    );
                  })}
                </div>
              </>
            ) : null}

            {error ? (
              <p className="gm-err" role="alert">
                {error}
              </p>
            ) : null}

            <button className="gm-submit" type="submit" disabled={submitting}>
              {submitting ? "Sending…" : submitLabel || "Get my hiring brief"}
            </button>
            <p className="gm-hint">
              We’ll use this to build your hiring brief. We don’t sell your information.
            </p>
          </form>
          {showBack ? (
            <button className="gm-ghost" type="button" onClick={onBack}>
              Back
            </button>
          ) : null}
          <Seeker href={careersHref} onClick={onCareers} />
        </>
      ) : null}
    </div>
  );
}

function Seeker({
  href,
  onClick,
}: {
  href: string;
  onClick: (e: React.MouseEvent<HTMLAnchorElement>) => void;
}) {
  return (
    <p className="gm-seeker">
      <a href={href} onClick={onClick}>
        {JOB_SEEKER_LINE}
      </a>
    </p>
  );
}
