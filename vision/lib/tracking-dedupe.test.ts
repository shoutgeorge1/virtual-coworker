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
    vi.stubGlobal("window", {
      dataLayer: [] as Array<{ event: string }>,
      sessionStorage: store,
      location: { href: "https://example.test/us", search: "" },
    });
    vi.stubGlobal("sessionStorage", store);
    vi.stubGlobal("document", { referrer: "" });
  });

  it("fires employer_form_valid_submit once per submission id", async () => {
    const { trackValidEmployerSubmit } = await import("./tracking");
    trackValidEmployerSubmit({ market: "us", submissionId: "sid_abc", role: "Admin" });
    trackValidEmployerSubmit({ market: "us", submissionId: "sid_abc", role: "Admin" });

    const events = ((window as unknown as { dataLayer: Array<{ event: string }> }).dataLayer || []).map(
      (e) => e.event,
    );
    expect(events.filter((e) => e === "employer_form_valid_submit")).toHaveLength(1);
    expect(events).toContain("employer_form_valid_submit_deduped");
  });
});
