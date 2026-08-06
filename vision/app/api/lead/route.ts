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
} from "../../../lib/lead-delivery";

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
    const res = await fetch(url, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
    });
    if (!res.ok) {
      const text = await res.text().catch(() => "");
      return { ok: false, detail: `HTTP ${res.status} ${text.slice(0, 200)}` };
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
    // Only conversion-eligible if a durable channel exists (log-only never is).
    const durable = configuredChannels().channels.length > 0;
    return NextResponse.json({
      ok: true,
      stored: true,
      duplicate: true,
      submission_id: dup.submissionId,
      delivery: durable ? "durable" : "log_only",
      conversion_eligible: durable,
      paid_ready: durable,
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

  const record = {
    submission_id: submissionId,
    firstName: names.firstName,
    lastName: names.lastName,
    email,
    phone: String(body.phone || "").trim(),
    company: String(body.company || "").trim(),
    role: String(body.role || "").trim(),
    category: String(body.category || "").trim(),
    variant: String(body.variant || "").trim(),
    timeline: String(body.timeline || "").trim(),
    message: String(body.message || "").trim(),
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
    landing_page_url: body.landing_page_url || "",
    referrer: body.referrer || "",
    lp_version: body.lp_version || "",
    captured_at: body.captured_at || "",
    submitted_at: submittedAt,
    // Honesty: never imply CRM/job-order success
    is_job_order: false,
    is_placement: false,
    zoho_synced: false,
  };

  console.info(
    "[lead]",
    JSON.stringify({
      ...record,
      email: email.replace(/(^.).*(@.*$)/, "$1***$2"),
      phone: record.phone ? "[set]" : "",
      message: record.message ? "[set]" : "",
    }),
  );

  const deliveries: { channel: string; ok: boolean; detail: string }[] = [];

  if (cfg.webhook) {
    deliveries.push({ channel: "webhook", ...(await postJson(cfg.webhook, record)) });
  }
  if (cfg.sheet) {
    deliveries.push({ channel: "sheet", ...(await postJson(cfg.sheet, record)) });
  }
  // Zoho optional — never fake success if missing
  if (cfg.zoho) {
    const z = await postJson(cfg.zoho, record);
    deliveries.push({ channel: "zoho", ...z });
    if (z.ok) {
      (record as { zoho_synced: boolean }).zoho_synced = true;
    }
  }

  const to = market === "au" ? cfg.emailToAu : cfg.emailToUs;
  if (to && cfg.resend && cfg.from) {
    try {
      const res = await fetch("https://api.resend.com/emails", {
        method: "POST",
        headers: {
          Authorization: `Bearer ${cfg.resend}`,
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          from: cfg.from,
          to: [to],
          subject: `[VC Pilot] ${market.toUpperCase()} employer inquiry — ${names.firstName}`.trim(),
          text: JSON.stringify(record, null, 2),
        }),
      });
      deliveries.push({
        channel: "email",
        ok: res.ok,
        detail: res.ok ? "sent" : `HTTP ${res.status}`,
      });
    } catch (err) {
      deliveries.push({
        channel: "email",
        ok: false,
        detail: err instanceof Error ? err.message : "email error",
      });
    }
  }

  const anyOk = deliveries.some((d) => d.ok);
  const anyConfigured = cfg.channels.length > 0;

  if (!anyConfigured) {
    if (allowLogOnlyLeads()) {
      // Explicit blocked mode for local/QA — NOT paid-ready.
      // Do not treat as conversion_eligible; client must not fire primary.
      console.warn(
        "[lead] ALLOW_LOG_ONLY_LEADS=true — log-only blocked mode (not paid-ready, not conversion-eligible)",
      );
      rememberSubmission(dupKey, submissionId);
      return NextResponse.json({
        ok: true,
        stored: true,
        submission_id: submissionId,
        delivery: "log_only",
        conversion_eligible: false,
        paid_ready: false,
        deliveries,
        warning: "log_only — not a live lead delivery channel; not conversion-eligible",
      });
    }
    console.error("[lead] BLOCKER: no delivery channel configured");
    return NextResponse.json(
      {
        ok: false,
        stored: false,
        error: deliveryBlockerMessage(),
        code: "delivery_not_configured",
        conversion_eligible: false,
        paid_ready: false,
        deliveries,
      },
      { status: 503 },
    );
  }

  if (!anyOk) {
    console.error("[lead] all deliveries failed", deliveries);
    return NextResponse.json(
      {
        ok: false,
        stored: false,
        error: "We could not deliver your request to the team. Please try again shortly.",
        code: "delivery_failed",
        conversion_eligible: false,
        paid_ready: false,
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
    paid_ready: true,
    deliveries,
    zoho_synced: Boolean((record as { zoho_synced?: boolean }).zoho_synced),
  });
}
