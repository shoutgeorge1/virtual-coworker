import { describe, expect, it } from "vitest";
import { withRetry, QuotaExhaustedError } from "@/lib/sync/retry";
import { microsToMajor } from "@/lib/sync/currency";
import {
  normalizeCampaignRows,
  campaignQuery,
} from "@/lib/google-ads/client";

describe("withRetry", () => {
  it("retries transient failures then succeeds", async () => {
    let n = 0;
    const sleeps: number[] = [];
    const value = await withRetry(
      async () => {
        n += 1;
        if (n < 3) throw new Error("503 upstream");
        return "ok";
      },
      {
        attempts: 3,
        baseDelayMs: 1,
        sleep: async (ms) => {
          sleeps.push(ms);
        },
      },
    );
    expect(value).toBe("ok");
    expect(n).toBe(3);
    expect(sleeps).toEqual([1, 2]);
  });

  it("does not retry quota exhaustion", async () => {
    let n = 0;
    await expect(
      withRetry(
        async () => {
          n += 1;
          throw new QuotaExhaustedError();
        },
        { attempts: 5, baseDelayMs: 1, sleep: async () => {} },
      ),
    ).rejects.toBeInstanceOf(QuotaExhaustedError);
    expect(n).toBe(1);
  });
});

describe("Google Ads normalize", () => {
  it("uses AUD for AU and converts micros", () => {
    const rows = normalizeCampaignRows(
      [
        {
          campaign: { id: "1", name: "VC_AU_CORE" },
          segments: { date: "2026-08-15" },
          metrics: { impressions: 10, clicks: 2, costMicros: 3_000_000, conversions: 1 },
        },
      ],
      "AU",
      "5735391940",
    );
    expect(rows[0]?.currency).toBe("AUD");
    expect(rows[0]?.cost).toBe(microsToMajor(3_000_000));
  });

  it("scopes GAQL to VC_* prefix and date window", () => {
    const q = campaignQuery("2026-08-07", "2026-08-20", "US");
    expect(q).toContain("VC_US_%");
    expect(q).toContain("2026-08-07");
    expect(q).toContain("2026-08-20");
    expect(q.toLowerCase()).toContain("from campaign");
  });
});
