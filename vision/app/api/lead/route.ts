import { NextRequest, NextResponse } from "next/server";

export type LeadPayload = {
  firstName?: string;
  lastName?: string;
  name?: string;
  email: string;
  phone?: string;
  company?: string;
  country?: string;
  companySize?: string;
  role?: string;
  timeline?: string;
  message?: string;
  market: "us" | "au";
  utm_source?: string;
  utm_medium?: string;
  utm_campaign?: string;
  utm_term?: string;
  utm_content?: string;
  gclid?: string;
  landing_page_url?: string;
  referrer?: string;
  submitted_at?: string;
};

function splitName(name: string | undefined): { firstName: string; lastName: string } {
  const parts = (name || "").trim().split(/\s+/).filter(Boolean);
  if (parts.length === 0) return { firstName: "", lastName: "" };
  if (parts.length === 1) return { firstName: parts[0], lastName: "" };
  return { firstName: parts[0], lastName: parts.slice(1).join(" ") };
}

function destinationFor(market: "us" | "au"): string | undefined {
  return market === "au" ? process.env.LEAD_EMAIL_AU : process.env.LEAD_EMAIL_US;
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

export async function POST(req: NextRequest) {
  let body: LeadPayload;
  try {
    body = (await req.json()) as LeadPayload;
  } catch {
    return NextResponse.json({ ok: false, error: "Invalid JSON" }, { status: 400 });
  }

  const email = (body.email || "").trim();
  const market = body.market;
  if (!email || (market !== "us" && market !== "au")) {
    return NextResponse.json(
      { ok: false, error: "email and market (us|au) are required" },
      { status: 400 },
    );
  }

  const names = splitName(body.name);
  const firstName = (body.firstName || names.firstName).trim();
  const lastName = (body.lastName || names.lastName).trim();
  const submittedAt = body.submitted_at || new Date().toISOString();

  const record = {
    firstName,
    lastName,
    email,
    phone: (body.phone || "").trim(),
    company: (body.company || "").trim(),
    country: (body.country || "").trim(),
    companySize: (body.companySize || "").trim(),
    role: (body.role || "").trim(),
    timeline: (body.timeline || "").trim(),
    message: (body.message || "").trim(),
    market,
    utm_source: body.utm_source || "",
    utm_medium: body.utm_medium || "",
    utm_campaign: body.utm_campaign || "",
    utm_term: body.utm_term || "",
    utm_content: body.utm_content || "",
    gclid: body.gclid || "",
    landing_page_url: body.landing_page_url || "",
    referrer: body.referrer || "",
    submitted_at: submittedAt,
  };

  // Always keep a server-side log line for failed-delivery diagnosis (no secrets).
  console.info("[lead]", JSON.stringify({ ...record, email: email.replace(/(^.).*(@.*$)/, "$1***$2") }));

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
  if (zoho) {
    deliveries.push({ channel: "zoho", ...(await postJson(zoho, record)) });
  }

  // Email via optional Resend if configured; otherwise rely on webhook/sheet.
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
          subject: `[VC Pilot] ${market.toUpperCase()} lead — ${firstName} ${lastName}`.trim(),
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
  } else if (to && !resendKey) {
    deliveries.push({
      channel: "email",
      ok: false,
      detail: "LEAD_EMAIL set but RESEND_API_KEY / LEAD_FROM_EMAIL missing — configure delivery",
    });
  }

  const anyOk = deliveries.some((d) => d.ok);
  const anyConfigured = Boolean(to || webhook || sheet || zoho);

  if (!anyConfigured) {
    console.error("[lead] delivery not configured", deliveries);
    return NextResponse.json(
      {
        ok: false,
        stored: true,
        error:
          "Lead received by server but delivery is not configured. Set LEAD_EMAIL_US / LEAD_EMAIL_AU + RESEND_API_KEY, or a webhook.",
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
        stored: true,
        error: "Lead stored in logs but external delivery failed. Check server logs.",
        deliveries,
      },
      { status: 502 },
    );
  }

  return NextResponse.json({ ok: true, stored: true, deliveries });
}
