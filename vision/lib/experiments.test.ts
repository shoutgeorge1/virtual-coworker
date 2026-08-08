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

  it("assigns a sticky variant for exit_popup", async () => {
    const { assignExperiment } = await import("./experiments");
    const first = assignExperiment("exit_popup");
    expect(["a", "b", "c"]).toContain(first);
    expect(assignExperiment("exit_popup")).toBe(first);
  });

  it("chat_launcher only allows a|b", async () => {
    const { assignExperiment, EXPERIMENTS } = await import("./experiments");
    expect(EXPERIMENTS.chat_launcher.variants).toEqual(["a", "b"]);
    const v = assignExperiment("chat_launcher");
    expect(["a", "b"]).toContain(v);
  });

  it("fires experiment_view once per session key", async () => {
    const { assignExperiment, trackExperimentView } = await import("./experiments");
    const v = assignExperiment("quiz_copy");
    trackExperimentView("quiz_copy", v);
    trackExperimentView("quiz_copy", v);
    const dl = (window as unknown as { dataLayer: { event: string }[] }).dataLayer;
    const views = dl.filter((e) => e.event === "experiment_view");
    expect(views.length).toBe(1);
  });

  it("forces variant from ?vc_exp=&vc_var= and sticks it", async () => {
    (window as unknown as { location: { search: string } }).location.search =
      "?vc_exp=lp_density&vc_var=b";
    const { assignExperiment, applyUrlForceVariant, densityFromVariant } =
      await import("./experiments");
    const forced = applyUrlForceVariant();
    expect(forced).toEqual({ id: "lp_density", variant: "b" });
    expect(localStorage.getItem("vc_exp_lp_density")).toBe("b");
    expect(assignExperiment("lp_density")).toBe("b");
    expect(
      (document.documentElement.dataset as { lpDensity?: string }).lpDensity,
    ).toBe(densityFromVariant("b"));
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

  it("EXPERIMENTS_BOOT_SCRIPT applies force + density paint", async () => {
    const { EXPERIMENTS_BOOT_SCRIPT } = await import("./experiments");
    expect(EXPERIMENTS_BOOT_SCRIPT).toContain("vc_exp");
    expect(EXPERIMENTS_BOOT_SCRIPT).toContain("lpDensity");
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
