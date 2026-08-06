import { describe, expect, it } from "vitest";
import { ROLE_TO_CATEGORY } from "../config/categories";

describe("HR canonical slug", () => {
  it("maps human-resources aliases to hr", () => {
    expect(ROLE_TO_CATEGORY["human-resources"]).toBe("hr");
    expect(ROLE_TO_CATEGORY.human_resources).toBe("hr");
    expect(ROLE_TO_CATEGORY.hr).toBe("hr");
  });
});
