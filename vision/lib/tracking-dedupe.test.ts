import { beforeEach, describe, expect, it, vi } from "vitest";

/**
 * Duplicate primary conversion prevention.
 * Uses a minimal sessionStorage stub so refresh cannot re-fire.
 */

function createSessionStore() {
  const map = new Map<string, string>();
  return {
    getItem: (k: string) => map.get(k) ?? null,
    setItem: (k: string, v: string) => {
      map.set(k, v);
    },
    removeItem: (k: string) => {
      map.delete(k);
    },
    clear: () => map.clear(),
    get length() {
      return map.size;
    },
    key: (i: number) => [...map.keys()][i] ?? null,
  };
}

describe("trackValidEmployerSubmit dedupe", () => {
  beforeEach(() => {
    vi.resetModules();
    const store = createSessionStore();
    const durable = createSessionStore();
    vi.stubGlobal("window", {
      dataLayer: [] as Array<{ event: string }>,
      sessionStorage: store,
      localStorage: durable,
      location: { href: "https://example.test/us", search: "", pathname: "/us" },
    });
    vi.stubGlobal("sessionStorage", store);
    vi.stubGlobal("localStorage", durable);
    vi.stubGlobal("document", { referrer: "" });
  });

  it("fires employer_inquiry_submitted once per submission id", async () => {
    const { trackValidEmployerSubmit } = await import("./tracking");
    trackValidEmployerSubmit({
      market: "us",
      submissionId: "sid_abc",
      role: "Admin",
      category: "administrative-support",
      variant: "a",
    });
    trackValidEmployerSubmit({
      market: "us",
      submissionId: "sid_abc",
      role: "Admin",
      category: "administrative-support",
      variant: "a",
    });

    const events = ((window as unknown as { dataLayer: Array<{ event: string }> }).dataLayer || []).map(
      (e) => e.event,
    );
    expect(events.filter((e) => e === "employer_inquiry_submitted")).toHaveLength(1);
    expect(events.filter((e) => e === "form_submit_success")).toHaveLength(0);
    expect(events).toContain("employer_inquiry_submitted_deduped");
  });

  it("marks calendly embed view as diagnostic, not Ads primary", async () => {
    const { trackCalendlyEmbedViewed, trackCalendlyClick } = await import("./tracking");
    trackCalendlyEmbedViewed({ market: "us", href: "https://calendly.com/cheyenne-virtualcoworker/30min" });
    trackCalendlyClick({ market: "us", href: "https://calendly.com/cheyenne-virtualcoworker/30min" });

    const events = (
      window as unknown as {
        dataLayer: Array<Record<string, unknown>>;
      }
    ).dataLayer;
    const viewed = events.find((e) => e.event === "calendly_embed_viewed");
    expect(viewed).toMatchObject({
      event: "calendly_embed_viewed",
      market: "us",
      bidding_primary: false,
      is_qualified_call: false,
    });
    expect(events.some((e) => e.event === "calendly_cta_clicked")).toBe(true);
    expect(events.some((e) => e.event === "calendly_click")).toBe(false);
  });
});
