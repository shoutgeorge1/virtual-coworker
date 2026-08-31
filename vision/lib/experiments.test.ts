import { describe, expect, it, beforeEach, vi } from "vitest";

describe("experiments", () => {
  beforeEach(() => {
    vi.resetModules();
    const store = new Map<string, string>();
    const session = new Map<string, string>();
    vi.stubGlobal("window", {
      dataLayer: [] as Record<string, unknown>[],
      location: { search: "" },
    });
    vi.stubGlobal("localStorage", {
      getItem: (k: string) => store.get(k) ?? null,
      setItem: (k: string, v: string) => {
        store.set(k, v);
      },
      removeItem: (k: string) => {
        store.delete(k);
      },
    });
    vi.stubGlobal("sessionStorage", {
      getItem: (k: string) => session.get(k) ?? null,
      setItem: (k: string, v: string) => {
        session.set(k, v);
      },
      removeItem: (k: string) => {
        session.delete(k);
      },
    });
    vi.stubGlobal("document", {
      cookie: "",
      documentElement: { dataset: {} as Record<string, string> },
    });
  });

  it("is parked — frozen simplified LP, not random assignment", async () => {
    const {
      EXPERIMENTS_LIVE,
      assignExperiment,
      PARKED_DEFAULTS,
      isExperimentLive,
      SELECTIVE_LIVE_EXPERIMENTS,
    } = await import("./experiments");
    expect(EXPERIMENTS_LIVE).toBe(false);
    expect(assignExperiment("exit_popup")).toBe(PARKED_DEFAULTS.exit_popup);
    expect(assignExperiment("quiz_copy")).toBe("a");
    expect(assignExperiment("chat_launcher")).toBe("a");
    expect(assignExperiment("gate_headline")).toBe("a");
    expect(assignExperiment("lp_density")).toBe("b");
    expect(assignExperiment("role_imagery")).toBe("a");
    expect(SELECTIVE_LIVE_EXPERIMENTS.us_hero_portrait).toBe(true);
    expect(isExperimentLive("us_hero_portrait")).toBe(true);
    expect(isExperimentLive("exit_popup")).toBe(false);
  });

  it("us_hero_portrait assigns and sticks while other tests stay parked", async () => {
    vi.spyOn(Math, "random").mockReturnValue(0.9);
    const { assignExperiment } = await import("./experiments");
    expect(assignExperiment("us_hero_portrait")).toBe("b");
    expect(localStorage.getItem("vc_exp_us_hero_portrait")).toBe("b");
    expect(assignExperiment("us_hero_portrait")).toBe("b");
    expect(assignExperiment("exit_popup")).toBe("a");
  });

  it("ignores old sticky storage while parked", async () => {
    localStorage.setItem("vc_exp_lp_density", "a");
    localStorage.setItem("vc_exp_exit_popup", "c");
    const { assignExperiment } = await import("./experiments");
    expect(assignExperiment("lp_density")).toBe("b");
    expect(assignExperiment("exit_popup")).toBe("a");
  });

  it("does not fire experiment_* for parked ids; does for selective live", async () => {
    const {
      assignExperiment,
      trackExperimentView,
      trackExperimentClick,
      trackExperimentConvert,
    } = await import("./experiments");
    const parked = assignExperiment("quiz_copy");
    trackExperimentView("quiz_copy", parked);
    trackExperimentClick("quiz_copy", parked);
    trackExperimentConvert("form_submit");
    const dl = (window as unknown as { dataLayer: { event: string }[] }).dataLayer;
    expect(dl.filter((e) => String(e.event || "").startsWith("experiment_"))).toEqual(
      [],
    );

    localStorage.setItem("vc_exp_us_hero_portrait", "b");
    const hero = assignExperiment("us_hero_portrait");
    trackExperimentView("us_hero_portrait", hero, { surface: "us_hub" });
    expect(
      dl.filter((e) => e.event === "experiment_view").map((e) => e.event),
    ).toEqual(["experiment_view"]);
  });

  it("chat_launcher only allows a|b", async () => {
    const { EXPERIMENTS } = await import("./experiments");
    expect(EXPERIMENTS.chat_launcher.variants).toEqual(["a", "b"]);
  });

  it("forces variant from ?vc_exp=&vc_var= and sticks it", async () => {
    (window as unknown as { location: { search: string } }).location.search =
      "?vc_exp=lp_density&vc_var=a";
    const { assignExperiment, applyUrlForceVariant, densityFromVariant } =
      await import("./experiments");
    const forced = applyUrlForceVariant();
    expect(forced).toEqual({ id: "lp_density", variant: "a" });
    expect(localStorage.getItem("vc_exp_lp_density")).toBe("a");
    expect(assignExperiment("lp_density")).toBe("a");
    expect(
      (document.documentElement.dataset as { lpDensity?: string }).lpDensity,
    ).toBe(densityFromVariant("a"));
  });

  it("rejects invalid force params", async () => {
    const { applyUrlForceVariant } = await import("./experiments");
    expect(applyUrlForceVariant("?vc_exp=lp_density&vc_var=z")).toBeNull();
    expect(applyUrlForceVariant("?vc_exp=nope&vc_var=a")).toBeNull();
  });

  it("buildForceVariantUrl encodes query params", async () => {
    const { buildForceVariantUrl } = await import("./experiments");
    expect(
      buildForceVariantUrl("https://www.virtualcoworker.app/us", "quiz_copy", "c"),
    ).toBe("https://www.virtualcoworker.app/us?vc_exp=quiz_copy&vc_var=c");
  });

  it("EXPERIMENTS_BOOT_SCRIPT paints lean while parked (ignores old sticky a)", async () => {
    const { EXPERIMENTS_BOOT_SCRIPT } = await import("./experiments");
    expect(EXPERIMENTS_BOOT_SCRIPT).toContain("vc_exp");
    expect(EXPERIMENTS_BOOT_SCRIPT).toContain("lpDensity");
    expect(EXPERIMENTS_BOOT_SCRIPT).toContain('var live=0');
    localStorage.setItem("vc_exp_lp_density", "a");
    const classList = { add: vi.fn() };
    const dataset: Record<string, string> = {};
    vi.stubGlobal("document", {
      cookie: "",
      documentElement: {
        classList,
        dataset,
      },
    });
    vi.stubGlobal("location", { search: "" });
    // eslint-disable-next-line no-eval
    eval(EXPERIMENTS_BOOT_SCRIPT);
    expect(classList.add).toHaveBeenCalledWith("js");
    expect(dataset.lpDensity).toBe("lean");
  });

  it("EXPERIMENTS_BOOT_SCRIPT still applies URL force", async () => {
    const { EXPERIMENTS_BOOT_SCRIPT } = await import("./experiments");
    const classList = { add: vi.fn() };
    vi.stubGlobal("document", {
      cookie: "",
      documentElement: {
        classList,
        dataset: {} as Record<string, string>,
      },
    });
    vi.stubGlobal("location", { search: "?vc_exp=exit_popup&vc_var=c" });
    // eslint-disable-next-line no-eval
    eval(EXPERIMENTS_BOOT_SCRIPT);
    expect(localStorage.getItem("vc_exp_exit_popup")).toBe("c");
    expect(classList.add).toHaveBeenCalledWith("js");
  });
});
