/**
 * Preliminary lead scoring / modeled value — ONE config module.
 * Edit multipliers here. Do not hardcode scores in components.
 *
 * Hypothesis knob: a truly strong employer lead ≈ $1,000 economically.
 * That is a calibration ceiling, not a flat conversion value and not revenue.
 *
 * Modeled (website) ≠ CRM-qualified ≠ Job Order ≠ Placement.
 * Never send estimated_lead_value into Google Ads bidding until Zoho
 * qualification exists. Job seekers / invalid / non-employer → $0 / score 0.
 *
 * Main drivers (the two form / quiz chips):
 *   1. Positions needed — strongest lever (more seats ≈ more placement $)
 *   2. Company size — modest. VC ICP is SMB, not enterprise.
 *      11–50 / 51–200 + multiple seats = sweet zone.
 *      201+ is not automatically the best lead (longer cycle, weaker fit).
 *      1–10 with 1 seat is real but smaller.
 *
 * Urgency / timeline / role stay small modifiers if present. No extra fields.
 *
 * Tune after 20 / 50 / 100 manually qualified leads. No ML.
 * CRM / Zoho later overrides this website estimate; keep both in history.
 *
 * Quiz LP (`/us/quiz`, `/au/quiz`) asks size + seats chips inside the quiz.
 * Homepage form (`/us`, `/au`) — Phase 0 (2026-08-11): qualify chips off;
 * scoring uses unknown-size / unknown-seats defaults when blank.
 */

export const COMPANY_SIZE_OPTIONS = [
  /** Modest base. Real SMB, smaller wallet / fewer seats later. */
  { id: "1-10", label: "1–10 people", score: 10, valueMult: 1.0 },
  /** Sweet zone — budget + still a fit for dedicated seats. */
  { id: "11-50", label: "11–50 people", score: 24, valueMult: 1.25 },
  /** Sweet zone — more budget, still SMB-shaped. */
  { id: "51-200", label: "51–200 people", score: 30, valueMult: 1.45 },
  /**
   * Larger can mean more seats later, but do NOT 3× this.
   * Longer cycle, maybe worse ICP fit than 51–200.
   */
  { id: "201+", label: "201+ people", score: 18, valueMult: 1.28 },
] as const;

export const POSITIONS_OPTIONS = [
  { id: "1", label: "1 role", score: 12, valueMult: 1.0 },
  { id: "2-3", label: "2–3 roles", score: 30, valueMult: 2.0 },
  { id: "4-10", label: "4–10 roles", score: 44, valueMult: 3.5 },
  /** Big dial, but $ is still capped — no pretend $10k until sales data. */
  { id: "11+", label: "11+ roles", score: 54, valueMult: 5.0 },
] as const;

/** Optional. CEO ICP is established companies needing dedicated seats, FT or PT. */
export const SCHEDULE_OPTIONS = [
  { id: "full-time", label: "Full-time" },
  { id: "part-time", label: "Part-time" },
  { id: "mix", label: "A mix" },
] as const;

/** Optional timeline — not shown on form yet; scoring uses it if present. */
export const HIRING_TIMELINE_OPTIONS = [
  { id: "asap", label: "ASAP", urgency: 0.9 },
  { id: "this-month", label: "This month", urgency: 0.7 },
  { id: "1-3-months", label: "1–3 months", urgency: 0.4 },
  { id: "exploring", label: "Just exploring", urgency: 0.15 },
] as const;

export type CompanySizeId = (typeof COMPANY_SIZE_OPTIONS)[number]["id"];
export type PositionsId = (typeof POSITIONS_OPTIONS)[number]["id"];
export type ScheduleId = (typeof SCHEDULE_OPTIONS)[number]["id"];
export type HiringTimelineId = (typeof HIRING_TIMELINE_OPTIONS)[number]["id"];

/** Editable coefficients — expected-value sketch, not accounting. */
export const LEAD_VALUE_MODEL = {
  scoreMax: 100,
  /** Calibration knob: a truly strong employer lead ≈ this, not truth. */
  strongLeadBenchmarkUsd: 1000,
  /** 1–10 employees, 1 seat, default urgency. Target ~$200–350. */
  baseEmployerUsd: 280,
  /** Employer submitted but chips skipped / weak signals. Still not $0. */
  weakEmployerFloorUsd: 80,
  /** Exceptional multi-seat + good-size ceiling. Do not pretend $10k. */
  capUsd: 1200,
  jobSeekerUsd: 0,
  jobSeekerScore: 0,
  unknownIntentScore: 15,
  unknownIntentUsd: 40,
  /** Default urgency when timeline not captured (~mid, not assumed ASAP). */
  defaultUrgency: 0.35,
  baseScore: 14,
  /** Small score modifier. Positions + size do the real work. */
  urgencyScoreScale: 10,
  unknownSizeScore: 8,
  unknownSeatsScore: 8,
  unknownSizeMult: 0.9,
  unknownSeatsMult: 0.85,
  /** urgencyMult = base + urgency × scale → ~1.0 at default, ~±8% ASAP/explore. */
  urgencyMultBase: 0.94,
  urgencyMultScale: 0.16,
  currency: "USD",
  valueKind: "estimated_modeled" as const,
} as const;

export type LeadValueInput = {
  intent: "employer" | "job_seeker" | "unknown";
  companySize?: CompanySizeId | string | null;
  positionsNeeded?: PositionsId | string | null;
  hiringTimeline?: HiringTimelineId | string | null;
  /** Optional 0–1 override; timeline wins if both set. */
  urgencyBoost?: number;
};

export type LeadValueResult = {
  lead_score: number;
  estimated_lead_value: number;
  currency: string;
  value_kind: typeof LEAD_VALUE_MODEL.valueKind;
  fit_label: "Strong fit" | "Good fit" | "Let’s discuss" | "Not a fit";
};

/** CRM / offline ladder. Website estimate never trains Ads bidding. */
export const VALUE_LADDER = [
  "website_modeled",
  "crm_qualified",
  "job_order",
  "placement",
] as const;

export type ValueLadderStage = (typeof VALUE_LADDER)[number];

/**
 * Interface only — do not call Zoho/Ads from here.
 * CRM value supersedes website estimate; keep both in history.
 */
export type OfflineConversionDraft = {
  submission_id: string;
  market: "us" | "au";
  gclid?: string;
  gbraid?: string;
  wbraid?: string;
  stage: Exclude<ValueLadderStage, "website_modeled">;
  conversion_value?: number;
  currency: "USD" | "AUD";
  converted_at: string;
  website_estimated_lead_value?: number;
  website_lead_score?: number;
};

function optionById<T extends { id: string }>(
  options: readonly T[],
  id: string | null | undefined,
): T | undefined {
  if (!id) return undefined;
  return options.find((o) => o.id === id);
}

function urgencyFromInput(input: LeadValueInput): number {
  const timeline = (input.hiringTimeline || "").trim();
  const fromTimeline = HIRING_TIMELINE_OPTIONS.find((o) => o.id === timeline);
  if (fromTimeline) return fromTimeline.urgency;
  if (typeof input.urgencyBoost === "number" && Number.isFinite(input.urgencyBoost)) {
    return Math.max(0, Math.min(1, input.urgencyBoost));
  }
  return LEAD_VALUE_MODEL.defaultUrgency;
}

/**
 * Deterministic preliminary score + modeled $.
 *
 * Score ≈ baseScore + size.score + seats.score + round(urgency × 10) (cap 100).
 * $     ≈ clamp(floor, baseEmployer × sizeMult × posMult × urgencyMult, capUsd)
 *
 * Positions multiplier is the big dial. Size is modest. Urgency is small.
 */
export function scoreLeadValue(input: LeadValueInput): LeadValueResult {
  if (input.intent === "job_seeker") {
    return {
      lead_score: LEAD_VALUE_MODEL.jobSeekerScore,
      estimated_lead_value: LEAD_VALUE_MODEL.jobSeekerUsd,
      currency: LEAD_VALUE_MODEL.currency,
      value_kind: LEAD_VALUE_MODEL.valueKind,
      fit_label: "Not a fit",
    };
  }

  if (input.intent !== "employer") {
    return {
      lead_score: LEAD_VALUE_MODEL.unknownIntentScore,
      estimated_lead_value: LEAD_VALUE_MODEL.unknownIntentUsd,
      currency: LEAD_VALUE_MODEL.currency,
      value_kind: LEAD_VALUE_MODEL.valueKind,
      fit_label: "Let’s discuss",
    };
  }

  const size = optionById(COMPANY_SIZE_OPTIONS, input.companySize);
  const pos = optionById(POSITIONS_OPTIONS, input.positionsNeeded);
  const urgency = urgencyFromInput(input);
  const urgencyPts = Math.round(urgency * LEAD_VALUE_MODEL.urgencyScoreScale);

  const lead_score = Math.min(
    LEAD_VALUE_MODEL.scoreMax,
    LEAD_VALUE_MODEL.baseScore +
      (size?.score ?? LEAD_VALUE_MODEL.unknownSizeScore) +
      (pos?.score ?? LEAD_VALUE_MODEL.unknownSeatsScore) +
      urgencyPts,
  );

  const sizeMult = size?.valueMult ?? LEAD_VALUE_MODEL.unknownSizeMult;
  const posMult = pos?.valueMult ?? LEAD_VALUE_MODEL.unknownSeatsMult;
  const urgencyMult =
    LEAD_VALUE_MODEL.urgencyMultBase + urgency * LEAD_VALUE_MODEL.urgencyMultScale;
  const raw = LEAD_VALUE_MODEL.baseEmployerUsd * sizeMult * posMult * urgencyMult;
  const estimated_lead_value = Math.round(
    Math.min(
      LEAD_VALUE_MODEL.capUsd,
      Math.max(LEAD_VALUE_MODEL.weakEmployerFloorUsd, raw),
    ),
  );

  let fit_label: LeadValueResult["fit_label"] = "Let’s discuss";
  if (lead_score >= 72) fit_label = "Strong fit";
  else if (lead_score >= 48) fit_label = "Good fit";

  return {
    lead_score,
    estimated_lead_value,
    currency: LEAD_VALUE_MODEL.currency,
    value_kind: LEAD_VALUE_MODEL.valueKind,
    fit_label,
  };
}

/** Server-side scoring from form/API fields (do not trust client scores). */
export function scoreLeadFromSignals(input: {
  intent?: string | null;
  company_size?: string | null;
  positions_needed?: string | null;
  hiring_timeline?: string | null;
}): LeadValueResult {
  const raw = String(input.intent || "").trim().toLowerCase();
  const intent: LeadValueInput["intent"] =
    raw === "job_seeker" || raw === "job" || raw === "applicant"
      ? "job_seeker"
      : raw === "employer" || raw === "hire" || raw === "hiring"
        ? "employer"
        : "unknown";
  return scoreLeadValue({
    intent,
    companySize: input.company_size,
    positionsNeeded: input.positions_needed,
    hiringTimeline: input.hiring_timeline,
  });
}
