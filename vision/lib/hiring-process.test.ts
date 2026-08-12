import { describe, expect, it } from "vitest";
import { hiringProcessSteps } from "../config/hiring-process";

describe("hiring process copy", () => {
  it("covers the white-glove client journey in four steps", () => {
    for (const market of ["us", "au"] as const) {
      const steps = hiringProcessSteps(market);
      expect(steps).toHaveLength(4);
      const blob = steps.map((s) => `${s.t} ${s.d}`).join(" ").toLowerCase();
      expect(blob).toContain("free consultation");
      expect(blob).toContain("job description");
      expect(blob).toContain("hourly rates");
      expect(blob).toContain("time tracker");
      expect(blob).toContain("ongoing support");
      expect(blob).not.toMatch(/\bva\b/);
    }
  });
});
