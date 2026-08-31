import { NextRequest, NextResponse } from "next/server";
import {
  duplicateKey,
  rejectLogPayload,
  validateEmployerLead,
  type LeadInput,
} from "../../../lib/lead-validation";
import {
  checkDuplicate,
  rateLimitAllow,
  rememberSubmission,
} from "../../../lib/rate-limit";
import {
  allowLogOnlyLeads,
  configuredChannels,
  deliveryBlockerMessage,
  durableTrafficChannels,
  formatLeadEmailText,
  parseLeadCc,
} from "../../../lib/lead-delivery";
import { createEmployerLead } from "../../../lib/zoho/client";
import { leadLogSafe } from "../../../lib/zoho/redact";
import { scoreLeadFromSignals } from "../../../config/lead-value";
import { normalizePhoneForStorage } from "../../../lib/phone-format";

function splitName(name: string): { firstName: string; lastName: string } {
  const parts = name.trim().split(/\s+/).filter(Boolean);
  if (parts.length === 0) return { firstName: "", lastName: "" };
  if (parts.length === 1) return { firstName: parts[0], lastName: "" };
  return { firstName: parts[0], lastName: parts.slice(1).join(" ") };
}

function clientKey(req: NextRequest, email: string): string {
  const fwd = req.headers.get("x-forwarded-for") || "";
  const ip = fwd.split(",")[0]?.trim() || req.headers.get("x-real-ip") || "unknown";
  return `${ip}:${email.slice(0, 3)}`;
}

async function postJson(url: string, body: unknown): Promise<{ ok: boolean; detail: string }> {
  try {
    const headers: Record<string, string> = { "Content-Type": "application/json" };
    // Optional bearer for LEAD_WEBHOOK_URL / sheet / zoho_webhook sinks (e.g. lead-sink).
    const auth = (process.env.LEAD_WEBHOOK_AUTH || "").trim();
    if (auth) headers.Authorization = `Bearer ${auth}`;
    const res = await fetch(url, {
      method: "POST",
      headers,
      body: JSON.stringify(body),
    });
    if (!res.ok) {
      const text = await res.text().catch(() => "");
      return { ok: false, detail: `HTTP ${res.status}` };
    }
    return { ok: true, detail: "ok" };
  } catch (err) {
    return { ok: false, detail: err instanceof Error ? err.message : "network error" };
  }
}

function turnstileConfigured(): boolean {
  return Boolean(process.env.TURNSTILE_SECRET_KEY && process.env.NEXT_PUBLIC_TURNSTILE_SITE_KEY);
}

async function verifyTurnstile(token: string | undefined, ip: string): Promise<boolean> {
  const secret = process.env.TURNSTILE_SECRET_KEY;
  if (!secret) return true;
  if (!token) return false;
  try {
    const body = new URLSearchParams();
    body.set("secret", secret);
    body.set("response", token);
    if (ip && ip !== "unknown") body.set("remoteip", ip);
    const res = await fetch("https://challenges.cloudflare.com/turnstile/v0/siteverify", {
      method: "POST",
      body,
    });
    const data = (await res.json()) as { success?: boolean };
    return Boolean(data.success);
  } catch {
    return false;
  }
}

export async function POST(req: NextRequest) {
  let body: LeadInput & { turnstile_token?: string };
  try {
    body = (await req.json()) as LeadInput & { turnstile_token?: string };
  } catch {
    return NextResponse.json({ ok: false, error: "Invalid JSON" }, { status: 400 });
  }

  const validation = validateEmployerLead(body);
  if (!validation.ok) {
    console.info(
      "[lead-reject]",
      JSON.stringify(
        rejectLogPayload(validation.code, String(body.market || ""), {
          reason: validation.reason,
        }),
      ),
    );
    const status =
      validation.code === "job_seeker" || validation.code === "honeypot" ? 403 : 400;
    return NextResponse.json(
      {
        ok: false,
        error: validation.code === "honeypot" ? "Unable to submit." : validation.reason,
        code: validation.code,
      },
      { status },
    );
  }

  const { market, email, name } = validation;
  const rlKey = clientKey(req, email);
  if (!rateLimitAllow(rlKey)) {
    console.info("[lead-reject]", JSON.stringify(rejectLogPayload("rate_limit", market)));
    return NextResponse.json(
      { ok: false, error: "Too many attempts. Please try again shortly.", code: "rate_limit" },
      { status: 429 },
    );
  }

  const dupKey = duplicateKey(email, market);
  const dup = checkDuplicate(dupKey);
  if (dup.duplicate) {
    // Conversion-eligible if a durable traffic channel exists (log-only never is).
    // Zoho CRM alone is not the traffic gate.
    const durable = durableTrafficChannels().length > 0;
    const dupScored = scoreLeadFromSignals({
      intent: "employer",
      company_size: String(body.company_size || "").trim(),
      positions_needed: String(body.positions_needed || "").trim(),
      hiring_timeline: String(body.hiring_timeline || body.timeline || "").trim(),
    });
    return NextResponse.json({
      ok: true,
      stored: true,
      duplicate: true,
      submission_id: dup.submissionId,
      delivery: durable ? "durable" : "log_only",
      conversion_eligible: durable,
      lead_delivery_succeeded: durable,
      lead_score: dupScored.lead_score,
      estimated_lead_value: dupScored.estimated_lead_value,
      value_kind: dupScored.value_kind,
      fit_label: dupScored.fit_label,
    });
  }

  const ip = (req.headers.get("x-forwarded-for") || "").split(",")[0]?.trim() || "unknown";
  if (turnstileConfigured()) {
    const okTs = await verifyTurnstile(body.turnstile_token, ip);
    if (!okTs) {
      console.info("[lead-reject]", JSON.stringify(rejectLogPayload("turnstile", market)));
      return NextResponse.json(
        { ok: false, error: "Verification failed. Please try again.", code: "turnstile" },
        { status: 403 },
      );
    }
  }

  const names = splitName(name);
  const submittedAt = body.submitted_at || new Date().toISOString();
  const submissionId = `vc_${market}_${Date.now().toString(36)}_${Math.random().toString(36).slice(2, 8)}`;
  const cfg = configuredChannels();
  const companySize = String(body.company_size || "").trim();
  const positionsNeeded = String(body.positions_needed || "").trim();
  const schedule = String(body.schedule || "").trim();
  const hiringTimeline = String(body.hiring_timeline || body.timeline || "").trim();
  const phoneRaw = String(body.phone || "").trim();
  const phone = validation.phone || normalizePhoneForStorage(phoneRaw, market) || phoneRaw;
  const scored = scoreLeadFromSignals({
    intent: "employer",
    company_size: companySize,
    positions_needed: positionsNeeded,
    hiring_timeline: hiringTimeline,
  });

  const record = {
    submission_id: submissionId,
    firstName: names.firstName,
    lastName: names.lastName,
    email,
    phone,
    company: String(body.company || "").trim(),
    company_website: String(body.company_website || "").trim(),
    role: String(body.role || "").trim(),
    category: String(body.category || "").trim(),
    variant: String(body.variant || "").trim(),
    timeline: hiringTimeline,
    message: String(body.message || "").trim(),
    company_size: companySize,
    positions_needed: positionsNeeded,
    schedule,
    hiring_timeline: hiringTimeline,
    lead_score: scored.lead_score,
    estimated_lead_value: scored.estimated_lead_value,
    value_kind: scored.value_kind,
    fit_label: scored.fit_label,
    lp_surface: String(body.lp_surface || "").trim(),
    market,
    intent: "employer" as const,
    utm_source: body.utm_source || "",
    utm_medium: body.utm_medium || "",
    utm_campaign: body.utm_campaign || "",
    utm_term: body.utm_term || "",
    utm_content: body.utm_content || "",
    gclid: body.gclid || "",
    gbraid: body.gbraid || "",
    wbraid: body.wbraid || "",
    match_type: body.utm_matchtype || "",
    device: body.utm_device || "",
    landing_page_url: body.landing_page_url || "",
    referrer: body.referrer || "",
    lp_version: body.lp_version || "",
    lp_variant: body.lp_variant || "",
    baseline_label: body.baseline_label || "",
    session_id: body.session_id || "",
    captured_at: body.captured_at || "",
    submitted_at: submittedAt,
    form_source: String(body.lp_surface || "").trim() || "virtualcoworker.app",
    lead_source: "Website",
    // Honesty: never imply CRM/job-order success
    is_job_order: false,
    is_placement: false,
    zoho_synced: false,
  };

  const deliveries: { channel: string; ok: boolean; detail: string; record_id?: string }[] = [];
  let zohoSynced = false;
  let zohoRecordId: string | undefined;
  let zohoDetail = "skipped";

  if (cfg.webhook) {
    const t0 = Date.now();
    const r = await postJson(cfg.webhook, record);
    deliveries.push({ channel: "webhook", ...r });
    console.info(
      "[lead]",
      JSON.stringify(
        leadLogSafe({
          submission_id: submissionId,
          market,
          channel: "webhook",
          ok: r.ok,
          error: r.ok ? undefined : r.detail,
          duration_ms: Date.now() - t0,
        }),
      ),
    );
  }
  if (cfg.sheet) {
    const t0 = Date.now();
    const r = await postJson(cfg.sheet, record);
    deliveries.push({ channel: "sheet", ...r });
    console.info(
      "[lead]",
      JSON.stringify(
        leadLogSafe({
          submission_id: submissionId,
          market,
          channel: "sheet",
          ok: r.ok,
          error: r.ok ? undefined : r.detail,
          duration_ms: Date.now() - t0,
        }),
      ),
    );
  }

  // Generic ZOHO_WEBHOOK_URL — NOT CRM API. Success does not set zoho_synced.
  if (cfg.zohoWebhook) {
    const t0 = Date.now();
    const z = await postJson(cfg.zohoWebhook, record);
    deliveries.push({ channel: "zoho_webhook", ...z });
    console.info(
      "[lead]",
      JSON.stringify(
        leadLogSafe({
          submission_id: submissionId,
          market,
          channel: "zoho_webhook",
          ok: z.ok,
          error: z.ok ? undefined : z.detail,
          duration_ms: Date.now() - t0,
        }),
      ),
    );
  }

  // Email first. Zoho is additional and must not fail email.
  const to = market === "au" ? cfg.emailToAu : cfg.emailToUs;
  if (to && cfg.resend && cfg.from) {
    const t0 = Date.now();
    const hostLabel =
      market === "au" ? "virtualcoworker.app/au" : "virtualcoworker.app/us";
    const displayName =
      [names.firstName, names.lastName].filter(Boolean).join(" ").trim() ||
      "employer";
    const cc = parseLeadCc().filter((addr) => addr.toLowerCase() !== to.toLowerCase());
    try {
      const payload: Record<string, unknown> = {
        from: cfg.from,
        to: [to],
        subject: `Free Consultation (${hostLabel}) - ${displayName}`,
        text: formatLeadEmailText(record),
      };
      if (cc.length) payload.cc = cc;
      const res = await fetch("https://api.resend.com/emails", {
        method: "POST",
        headers: {
          Authorization: `Bearer ${cfg.resend}`,
          "Content-Type": "application/json",
        },
        body: JSON.stringify(payload),
      });
      const ok = res.ok;
      let detail = "sent";
      if (!ok) {
        const errText = await res.text().catch(() => "");
        // Keep log short; Resend often returns {"message":"..."}.
        detail = `HTTP ${res.status}${errText ? `: ${errText.slice(0, 180)}` : ""}`;
      }
      deliveries.push({
        channel: "email",
        ok,
        detail,
      });
      console.info(
        "[lead]",
        JSON.stringify(
          leadLogSafe({
            submission_id: submissionId,
            market,
            channel: "email",
            ok,
            error: ok ? undefined : detail,
            duration_ms: Date.now() - t0,
          }),
        ),
      );
    } catch (err) {
      deliveries.push({
        channel: "email",
        ok: false,
        detail: err instanceof Error ? err.message : "email error",
      });
      console.info(
        "[lead]",
        JSON.stringify(
          leadLogSafe({
            submission_id: submissionId,
            market,
            channel: "email",
            ok: false,
            error: err instanceof Error ? err.message : "email error",
            duration_ms: Date.now() - t0,
          }),
        ),
      );
    }
  }

  // Direct Zoho CRM create-only. After email. Failure must not fail email.
  // Gated by ZOHO_SUBMISSION_ENABLED (default off). Never upsert.
  if (cfg.zohoCrm) {
    try {
      const z = await createEmployerLead(record);
      zohoDetail = z.detail;
      deliveries.push({
        channel: "zoho_crm",
        ok: z.ok,
        detail: z.detail,
        record_id: z.recordId,
      });
      if (z.zoho_synced && z.recordId) {
        zohoSynced = true;
        zohoRecordId = z.recordId;
      }
    } catch (err) {
      zohoDetail = err instanceof Error ? err.message : "zoho_error";
      deliveries.push({
        channel: "zoho_crm",
        ok: false,
        detail: "zoho_error",
      });
    }
  }

  const trafficOk = deliveries.some(
    (d) =>
      d.ok &&
      (d.channel === "email" ||
        d.channel === "webhook" ||
        d.channel === "sheet" ||
        d.channel === "zoho_webhook"),
  );
  const anyTrafficConfigured = durableTrafficChannels().length > 0;
  // CRM-only config without email/webhook/sheet is NOT enough for conversion / traffic
  const crmOnlyConfigured =
    !anyTrafficConfigured && cfg.channels.includes("zoho_crm");

  if (!anyTrafficConfigured && !crmOnlyConfigured) {
    if (allowLogOnlyLeads()) {
      console.warn(
        "[lead] ALLOW_LOG_ONLY_LEADS=true — log-only blocked mode (not TRAFFIC READY, not conversion-eligible)",
      );
      rememberSubmission(dupKey, submissionId);
      return NextResponse.json({
        ok: true,
        stored: true,
        submission_id: submissionId,
        delivery: "log_only",
        conversion_eligible: false,
        lead_delivery_succeeded: false,
        zoho_synced: false,
        zoho_record_id: null,
        zoho_status: zohoDetail,
        deliveries,
        warning: "log_only — not a live lead delivery channel; not conversion-eligible",
        lead_score: scored.lead_score,
        estimated_lead_value: scored.estimated_lead_value,
        value_kind: scored.value_kind,
        fit_label: scored.fit_label,
      });
    }
    console.error("[lead] BLOCKER: no durable traffic delivery channel configured");
    return NextResponse.json(
      {
        ok: false,
        stored: false,
        error: deliveryBlockerMessage(),
        code: "delivery_not_configured",
        conversion_eligible: false,
        lead_delivery_succeeded: false,
        zoho_synced: false,
        deliveries,
      },
      { status: 503 },
    );
  }

  if (crmOnlyConfigured && !trafficOk) {
    // CRM attempted but traffic channel missing — do not claim conversion-eligible.
    const crmOk = deliveries.some((d) => d.channel === "zoho_crm" && d.ok);
    rememberSubmission(dupKey, submissionId);
    return NextResponse.json({
      ok: crmOk,
      stored: crmOk,
      submission_id: submissionId,
      delivery: crmOk ? "crm_only" : "failed",
      conversion_eligible: false,
      lead_delivery_succeeded: false,
      zoho_synced: zohoSynced,
      zoho_record_id: zohoRecordId || null,
      zoho_status: zohoDetail,
      deliveries,
      warning:
        "zoho_crm without email/webhook/sheet — CRM READY path only; not TRAFFIC READY",
      lead_score: scored.lead_score,
      estimated_lead_value: scored.estimated_lead_value,
      value_kind: scored.value_kind,
      fit_label: scored.fit_label,
    });
  }

  if (!trafficOk) {
    console.error("[lead] all traffic deliveries failed");
    return NextResponse.json(
      {
        ok: false,
        stored: false,
        error: "We could not deliver your request to the team. Please try again shortly.",
        code: "delivery_failed",
        conversion_eligible: false,
        lead_delivery_succeeded: false,
        zoho_synced: zohoSynced,
        zoho_record_id: zohoRecordId || null,
        zoho_status: zohoDetail,
        deliveries,
      },
      { status: 502 },
    );
  }

  rememberSubmission(dupKey, submissionId);
  return NextResponse.json({
    ok: true,
    stored: true,
    submission_id: submissionId,
    delivery: "durable",
    conversion_eligible: true,
    lead_delivery_succeeded: true,
    // Paid/traffic readiness is a Launch Control verdict — not this API field.
    zoho_synced: zohoSynced,
    zoho_record_id: zohoRecordId || null,
    zoho_status: zohoDetail,
    deliveries,
    lead_score: scored.lead_score,
    estimated_lead_value: scored.estimated_lead_value,
    value_kind: scored.value_kind,
    fit_label: scored.fit_label,
  });
}
