/**
 * Shared conversion-assist timing tests (absorb-first money LP rules).
 */
import { describe, expect, it } from "vitest";
import {
  CONVERSION_ASSIST,
  shouldSuppressSecondaryAssist,
  wasFormStarted,
  wasPrimaryConverted,
} from "./conversion-assist";

describe("CONVERSION_ASSIST timing", () => {
  it("keeps exit absorb-first delays in the 30–45s band", () => {
    expect(CONVERSION_ASSIST.absorbMs).toBeGreaterThanOrEqual(30_000);
    expect(CONVERSION_ASSIST.absorbMs).toBeLessThanOrEqual(45_000);
    expect(CONVERSION_ASSIST.timedExitMs).toBeGreaterThanOrEqual(
      CONVERSION_ASSIST.absorbMs,
    );
    expect(CONVERSION_ASSIST.timedExitMs).toBeLessThanOrEqual(60_000);
  });

  it("delays chat launcher longer than exit absorb, with mobile even longer", () => {
    expect(CONVERSION_ASSIST.chatRevealMs).toBeGreaterThanOrEqual(40_000);
    expect(CONVERSION_ASSIST.chatRevealMs).toBeLessThanOrEqual(60_000);
    expect(CONVERSION_ASSIST.chatRevealMobileMs).toBeGreaterThanOrEqual(45_000);
    expect(CONVERSION_ASSIST.chatRevealMobileMs).toBeLessThanOrEqual(90_000);
    expect(CONVERSION_ASSIST.chatRevealMobileMs).toBeGreaterThan(
      CONVERSION_ASSIST.chatRevealMs,
    );
    expect(CONVERSION_ASSIST.chatRevealMs).toBeGreaterThan(
      CONVERSION_ASSIST.absorbMs,
    );
  });

  it("uses mid-page scroll for exit and deeper scroll for chat", () => {
    expect(CONVERSION_ASSIST.scrollDepth).toBeGreaterThanOrEqual(0.25);
    expect(CONVERSION_ASSIST.scrollDepth).toBeLessThanOrEqual(0.4);
    expect(CONVERSION_ASSIST.chatScrollDepth).toBeGreaterThanOrEqual(0.5);
    expect(CONVERSION_ASSIST.chatScrollDepth).toBeLessThanOrEqual(0.7);
    expect(CONVERSION_ASSIST.chatScrollDepth).toBeGreaterThan(
      CONVERSION_ASSIST.scrollDepth,
    );
  });
});

describe("secondary suppress helpers", () => {
  it("exports suppress predicates", () => {
    expect(typeof shouldSuppressSecondaryAssist).toBe("function");
    expect(typeof wasFormStarted).toBe("function");
    expect(typeof wasPrimaryConverted).toBe("function");
  });
});
