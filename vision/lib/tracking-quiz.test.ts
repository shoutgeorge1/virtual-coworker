import { beforeEach, describe, expect, it, vi } from "vitest";

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

describe("quiz LP attribution", () => {
  beforeEach(() => {
    vi.resetModules();
    const store = createSessionStore();
    const durable = createSessionStore();
    vi.stubGlobal("window", {
      dataLayer: [] as Array<Record<string, unknown>>,
      sessionStorage: store,
      localStorage: durable,
      location: {
        href: "https://www.virtualcoworker.app/us/quiz?lp_variant=quiz&gclid=abc",
        search: "?lp_variant=quiz&gclid=abc",
        pathname: "/us/quiz",
      },
    });
    vi.stubGlobal("sessionStorage", store);
    vi.stubGlobal("localStorage", durable);
    vi.stubGlobal("document", { referrer: "https://google.com" });
  });

  it("captures lp_variant=quiz and click ids without changing lp_version", async () => {
    const { captureAttribution, LP_VERSION, trackEvent } = await import("./tracking");
    const attr = captureAttribution("us", { lp_variant: "quiz" });
    expect(attr.lp_variant).toBe("quiz");
    expect(attr.gclid).toBe("abc");
    expect(attr.lp_version).toBe(LP_VERSION);
    expect(LP_VERSION).toBe("baseline_v1_2026_08");

    trackEvent("quiz_started", { market: "us", lp_variant: "quiz" });
    const events = (
      window as unknown as { dataLayer: Array<Record<string, unknown>> }
    ).dataLayer;
    expect(events[0].event).toBe("quiz_started");
    expect(events[0].lp_variant).toBe("quiz");
    expect(events[0].lp_version).toBe(LP_VERSION);
  });

  it("queues experiment_* for GA4 when bridge is not ready yet", async () => {
    const { trackEvent } = await import("./tracking");
    trackEvent("experiment_view", {
      market: "us",
      experiment_id: "quiz_copy",
      experiment_variant: "a",
    });
    const w = window as unknown as {
      dataLayer: Array<Record<string, unknown>>;
      __vcExpGa4Queue?: Array<[string, Record<string, string | number | boolean>]>;
    };
    expect(w.dataLayer.some((e) => e.event === "experiment_view")).toBe(true);
    expect(w.__vcExpGa4Queue?.[0]?.[0]).toBe("experiment_view");
    expect(w.__vcExpGa4Queue?.[0]?.[1]?.experiment_id).toBe("quiz_copy");
  });

  it("dual-sends experiment_* via __vcSendExpGa4 when present", async () => {
    const send = vi.fn();
    (window as unknown as { __vcSendExpGa4: typeof send }).__vcSendExpGa4 = send;
    const { trackEvent } = await import("./tracking");
    trackEvent("experiment_click", {
      market: "us",
      experiment_id: "chat_launcher",
      experiment_variant: "b",
    });
    expect(send).toHaveBeenCalledWith(
      "experiment_click",
      expect.objectContaining({
        experiment_id: "chat_launcher",
        experiment_variant: "b",
        market: "us",
      }),
    );
  });
});
