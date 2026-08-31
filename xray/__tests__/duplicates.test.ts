import { describe, expect, it } from "vitest";
import { createMemoryStore } from "@/lib/db/store";
import { resolveJoin } from "@/lib/sync/join";
import type { CampaignDayRow, ZohoInquiryDayRow } from "@/lib/sync/types";

describe("idempotent upserts", () => {
  it("does not duplicate campaign rows on re-upsert of the same day key", async () => {
    const store = createMemoryStore();
    const base: CampaignDayRow = {
      date: "2026-08-15",
      market: "US",
      customer_id: "4967151855",
      campaign_id: "111",
      campaign_name: "VC_US_CORE",
      currency: "USD",
      impressions: 10,
      clicks: 1,
      cost: 2.5,
      conversions: 0,
      conversions_value: 0,
      all_conversions: 0,
    };

    await store.upsertCampaigns([base]);
    await store.upsertCampaigns([{ ...base, impressions: 99, cost: 9.9 }]);

    const counts = await store.countRows();
    expect(counts.daily_campaign_performance).toBe(1);
    const stored = store._maps.campaigns.get("2026-08-15\u0001US\u0001111");
    expect(stored?.impressions).toBe(99);
    expect(stored?.cost).toBe(9.9);
  });

  it("keeps distinct days as separate historical snapshots", async () => {
    const store = createMemoryStore();
    const row = (date: string): CampaignDayRow => ({
      date,
      market: "AU",
      customer_id: "5735391940",
      campaign_id: "222",
      campaign_name: "VC_AU_CORE",
      currency: "AUD",
      impressions: 5,
      clicks: 1,
      cost: 1,
      conversions: 0,
      conversions_value: 0,
      all_conversions: 0,
    });
    await store.upsertCampaigns([row("2026-08-14"), row("2026-08-15")]);
    await store.upsertCampaigns([row("2026-08-15")]);
    expect((await store.countRows()).daily_campaign_performance).toBe(2);
  });

  it("upserts Zoho inquiries by date+record_id without duplicates", async () => {
    const store = createMemoryStore();
    const join = resolveJoin({ gclid: "Cj0TEST" });
    const row: ZohoInquiryDayRow = {
      date: "2026-08-15",
      market: "US",
      record_id: "z-1",
      status: "New Enquiry (Auto)",
      lead_source: "Website",
      utm_source: "google",
      utm_medium: "cpc",
      utm_campaign: "VC_US_CORE",
      utm_term: "virtual coworker",
      utm_content: "AG1",
      has_gclid: true,
      landing_page: "/us/hire",
      join_method: join.method,
      join_key: join.key,
      join_inferred: false,
      paid_likely: true,
    };
    await store.upsertZohoInquiries([row]);
    await store.upsertZohoInquiries([{ ...row, status: "Contacted" }]);
    expect((await store.countRows()).daily_zoho_inquiries).toBe(1);
    expect(store._maps.zoho.get("2026-08-15\u0001z-1")?.status).toBe("Contacted");
  });
});

describe("join priority", () => {
  it("prefers GCLID over UTM over date+landing fallback", () => {
    expect(resolveJoin({ gclid: "abc", utm_campaign: "c", utm_content: "a", utm_term: "k" }).method).toBe(
      "gclid",
    );
    expect(
      resolveJoin({
        utm_campaign: "c",
        ad_group: "a",
        keyword: "k",
        date: "2026-08-15",
        landing_page: "/us",
      }).method,
    ).toBe("utm_campaign_adgroup_keyword");
    const fb = resolveJoin({ date: "2026-08-15", landing_page: "/us/hire" });
    expect(fb.method).toBe("date_landing_page_fallback");
    expect(fb.label.toLowerCase()).toContain("inferred");
    expect(fb.label.toLowerCase()).toContain("not a confirmed click match");
  });
});
