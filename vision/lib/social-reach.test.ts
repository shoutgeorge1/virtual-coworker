import { describe, expect, it } from "vitest";
import { TRUST_PROOF } from "../config/site";

describe("socialReach trust badges", () => {
  it("prints LinkedIn floor verified against live observation", () => {
    const s = TRUST_PROOF.socialReach;
    expect(s.linkedinDisplay).toBe("450K+");
    expect(s.linkedinFollowers).toBe(450_000);
    expect(s.linkedinObservedExact).toBeGreaterThanOrEqual(s.linkedinFollowers);
    expect(s.linkedinSource).toBe("linkedin_live");
    expect(s.linkedinVerifiedAt).toBe("2026-08-11");
  });

  it("prints Facebook CEO-approved floor without inventing a live exact", () => {
    const s = TRUST_PROOF.socialReach;
    expect(s.facebookDisplay).toBe("290K+");
    expect(s.facebookFollowers).toBe(290_000);
    expect(s.facebookSource).toBe("ceo_meeting_2026-08-11");
    // Empty = not live-scraped; do not pretend we have a live exact.
    expect(s.facebookVerifiedAt).toBe("");
  });
});
