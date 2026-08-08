import { describe, expect, it } from "vitest";
import { CATEGORY_SLUGS } from "../config/categories";
import {
  ROLE_IMAGERY,
  assertUniqueCategoryImagery,
  portraitSrcForCategory,
} from "../config/role-imagery";

describe("role imagery — unique per title", () => {
  it("arm A has nine distinct category srcs", () => {
    expect(assertUniqueCategoryImagery(ROLE_IMAGERY.a)).toEqual([]);
  });

  it("arm B has nine distinct category srcs", () => {
    expect(assertUniqueCategoryImagery(ROLE_IMAGERY.b)).toEqual([]);
  });

  it("every category slug resolves on both arms", () => {
    for (const slug of CATEGORY_SLUGS) {
      expect(portraitSrcForCategory(slug, "a")).toMatch(/^\/(roles|brand)\//);
      expect(portraitSrcForCategory(slug, "b")).toMatch(/^\/(roles|brand)\//);
    }
  });
});
