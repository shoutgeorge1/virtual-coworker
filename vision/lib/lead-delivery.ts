/**
 * Honest lead delivery adapter.
 *
 * Channels:
 * - email / webhook / sheet — durable delivery for TRAFFIC READY (not CRM sync)
 * - zoho_webhook — generic ZOHO_WEBHOOK_URL POST (env name kept for compatibility).
 *   HTTP 200 ≠ Zoho CRM sync. Never set zoho_synced from this channel.
 * - zoho_crm — direct Zoho CRM V8 adapter (feature-flagged). zoho_synced only
 *   when response includes a CRM record id.
 *
 * TRAFFIC READY (Launch Control) ≠ CRM READY ≠ OPTIMIZATION READY.
 * API must not claim "paid_ready" as a launch verdict — use lead_delivery_succeeded.
 */

import { zohoCrmConfigured } from "./zoho/config";

export type DeliveryChannel =
  | "email"
  | "webhook"
  | "sheet"
  | "zoho_webhook"
  | "zoho_crm";

/** @deprecated Use zoho_webhook — kept only for reading old test expectations */
export type LegacyZohoChannel = "zoho";

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
  /** Generic webhook URL (ZOHO_WEBHOOK_URL) — not CRM API */
  zohoWebhook?: string;
  zohoCrm: boolean;
} {
  const emailToUs = (env.LEAD_EMAIL_US || "").trim() || undefined;
  const emailToAu = (env.LEAD_EMAIL_AU || "").trim() || undefined;
  const from = (env.LEAD_FROM_EMAIL || "").trim() || undefined;
  const resend = (env.RESEND_API_KEY || "").trim() || undefined;
  const webhook = (env.LEAD_WEBHOOK_URL || "").trim() || undefined;
  const sheet = (env.LEAD_SHEET_WEBHOOK_URL || "").trim() || undefined;
  const zohoWebhook = (env.ZOHO_WEBHOOK_URL || "").trim() || undefined;
  const zohoCrm = zohoCrmConfigured(env);

  const channels: DeliveryChannel[] = [];
  if ((emailToUs || emailToAu) && from && resend) channels.push("email");
  if (webhook) channels.push("webhook");
  if (sheet) channels.push("sheet");
  if (zohoWebhook) channels.push("zoho_webhook");
  if (zohoCrm) channels.push("zoho_crm");

  return {
    channels,
    emailToUs,
    emailToAu,
    from,
    resend,
    webhook,
    sheet,
    zohoWebhook,
    zohoCrm,
  };
}

/**
 * Durable channels that satisfy the TRAFFIC READY delivery gate.
 * Zoho CRM alone does not count — CRM READY is a separate Launch Control status.
 * Generic zoho_webhook counts as a monitored webhook destination.
 */
export function durableTrafficChannels(
  env: NodeJS.ProcessEnv = process.env,
): DeliveryChannel[] {
  return configuredChannels(env).channels.filter((c) =>
    c === "email" || c === "webhook" || c === "sheet" || c === "zoho_webhook",
  );
}

/**
 * Explicit opt-in for local/QA log-only blocked mode.
 * Never default-on. Never conversion-eligible. Never TRAFFIC READY.
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
