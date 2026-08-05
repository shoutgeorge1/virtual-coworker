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

function splitName(name: string): { firstName: string; lastName: string } {
  const parts = name.trim().split(/\s+/).filter(Boolean);
  if (parts.length === 0) return { firstName: "", lastName: "" };
  if (parts.length === 1) return { firstName: parts[0], lastName: "" };
  return { firstName: parts[0], lastName: parts.slice(1).join(" ") };
}

function destinationFor(market: "us" | "au"): string | undefined {
  return market === "au" ? process.env.LEAD_EMAIL_AU : process.env.LEAD_EMAIL_US;
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
  if (!secret) return true; // env boundary — do not block baseline when missing
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
    console.info("[lead-reject]", JSON.stringify(rejectLogPayload(validation.code, String(body.market || ""), { reason: validation.reason })));
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
    // Same employer within window — acknowledge without re-firing pipeline/primary.
    return NextResponse.json({
      ok: true,
      stored: true,
      duplicate: true,
      submission_id: dup.submissionId,
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

  const record = {
    submission_id: submissionId,
    firstName: names.firstName,
    lastName: names.lastName,
    email,
    phone: String(body.phone || "").trim(),
    company: String(body.company || "").trim(),
    role: String(body.role || "").trim(),
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
    submitted_at: submittedAt,
  };

  // Redacted server log after validation (attribution kept; email masked).
  console.info(
    "[lead]",
    JSON.stringify({
      ...record,
      email: email.replace(/(^.).*(@.*$)/, "$1***$2"),
      phone: record.phone ? "[set]" : "",
      message: record.message ? "[set]" : "",
    }),
  );

  const to = destinationFor(market);
  const webhook = process.env.LEAD_WEBHOOK_URL;
  const sheet = process.env.LEAD_SHEET_WEBHOOK_URL;
  const zoho = process.env.ZOHO_WEBHOOK_URL;

  const deliveries: { channel: string; ok: boolean; detail: string }[] = [];

  if (webhook) {
    deliveries.push({ channel: "webhook", ...(await postJson(webhook, record)) });
  }
  if (sheet) {
    deliveries.push({ channel: "sheet", ...(await postJson(sheet, record)) });
  }
  // Zoho is optional — do not block launch if missing.
  if (zoho) {
    deliveries.push({ channel: "zoho", ...(await postJson(zoho, record)) });
  }

  const resendKey = process.env.RESEND_API_KEY;
  const from = process.env.LEAD_FROM_EMAIL;
  if (to && resendKey && from) {
    try {
      const res = await fetch("https://api.resend.com/emails", {
        method: "POST",
        headers: {
          Authorization: `Bearer ${resendKey}`,
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          from,
          to: [to],
          subject: `[VC Pilot] ${market.toUpperCase()} employer lead — ${names.firstName}`.trim(),
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
  const anyConfigured = Boolean(to || webhook || sheet || zoho);

  // Dev / pre-delivery: accept validated employer leads into logs so LP QA can proceed.
  // Production should configure at least one delivery channel before paid traffic.
  if (!anyConfigured) {
    console.warn("[lead] no delivery channel configured — accepting validated lead to logs only");
    rememberSubmission(dupKey, submissionId);
    return NextResponse.json({
      ok: true,
      stored: true,
      submission_id: submissionId,
      delivery: "log_only",
      deliveries,
    });
  }

  if (!anyOk) {
    console.error("[lead] all deliveries failed", deliveries);
    return NextResponse.json(
      {
        ok: false,
        stored: true,
        error: "Lead stored in logs but external delivery failed. Check server logs.",
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
    deliveries,
  });
}
