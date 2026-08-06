/**
 * Honest lead delivery adapter.
 * Never claim Zoho/CRM success when no endpoint is configured.
 */

export type DeliveryChannel = "email" | "webhook" | "sheet" | "zoho";

export type DeliveryAttempt = {
  channel: DeliveryChannel;
  ok: boolean;
  detail: string;
};

export function configuredChannels(env: NodeJS.ProcessEnv = process.env): {
  channels: DeliveryChannel[];
  emailToUs?: string;
  emailToAu?: string;
  from?: string;
  resend?: string;
  webhook?: string;
  sheet?: string;
  zoho?: string;
} {
  const emailToUs = (env.LEAD_EMAIL_US || "").trim() || undefined;
  const emailToAu = (env.LEAD_EMAIL_AU || "").trim() || undefined;
  const from = (env.LEAD_FROM_EMAIL || "").trim() || undefined;
  const resend = (env.RESEND_API_KEY || "").trim() || undefined;
  const webhook = (env.LEAD_WEBHOOK_URL || "").trim() || undefined;
  const sheet = (env.LEAD_SHEET_WEBHOOK_URL || "").trim() || undefined;
  const zoho = (env.ZOHO_WEBHOOK_URL || "").trim() || undefined;

  const channels: DeliveryChannel[] = [];
  if ((emailToUs || emailToAu) && from && resend) channels.push("email");
  if (webhook) channels.push("webhook");
  if (sheet) channels.push("sheet");
  if (zoho) channels.push("zoho");

  return { channels, emailToUs, emailToAu, from, resend, webhook, sheet, zoho };
}

/**
 * Explicit opt-in for local/QA log-only blocked mode.
 * Never default-on. Never conversion-eligible. Never paid-ready.
 * Production paid traffic requires a real email/webhook/sheet channel.
 */
export function allowLogOnlyLeads(env: NodeJS.ProcessEnv = process.env): boolean {
  return (env.ALLOW_LOG_ONLY_LEADS || "").trim() === "true";
}

export function deliveryBlockerMessage(): string {
  return (
    "Lead delivery is not configured. We could not send your request to the team. " +
    "Please try again later, or use the business phone if shown."
  );
}
