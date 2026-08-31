import { describe, expect, it } from "vitest";
import {
  isUngatedEmployerLp,
  shouldFireEmployerFormStarted,
  shouldFireEmployerGateSelected,
} from "./ungated-us-home";

describe("isUngatedEmployerLp", () => {
  it("is on for US and AU employer form LPs, including category pages", () => {
    expect(isUngatedEmployerLp({ market: "us" })).toBe(true);
    expect(isUngatedEmployerLp({ market: "au" })).toBe(true);
    expect(
      isUngatedEmployerLp({ market: "us", category: null, conversionSurface: "form" }),
    ).toBe(true);
    expect(
      isUngatedEmployerLp({
        market: "us",
        category: "administrative-support",
        conversionSurface: "form",
      }),
    ).toBe(true);
    expect(
      isUngatedEmployerLp({
        market: "au",
        category: "bookkeeping",
        conversionSurface: "form",
      }),
    ).toBe(true);
  });

  it("stays gated for quiz, PH, and non-employer surfaces", () => {
    expect(isUngatedEmployerLp({ market: "us", conversionSurface: "quiz" })).toBe(false);
    expect(isUngatedEmployerLp({ market: "au", conversionSurface: "quiz" })).toBe(false);
    expect(isUngatedEmployerLp({ market: "ph" })).toBe(false);
    expect(
      isUngatedEmployerLp({
        market: "ph",
        category: "administrative-support",
        conversionSurface: "form",
      }),
    ).toBe(false);
  });
});

describe("shouldFireEmployerGateSelected", () => {
  it("never fires on ungated employer LPs, including page load", () => {
    expect(
      shouldFireEmployerGateSelected({
        ungated: true,
        alreadyEmployer: false,
        reason: "page_load",
      }),
    ).toBe(false);
    expect(
      shouldFireEmployerGateSelected({
        ungated: true,
        alreadyEmployer: true,
        reason: "user_click",
      }),
    ).toBe(false);
    expect(
      shouldFireEmployerGateSelected({
        ungated: true,
        alreadyEmployer: false,
        reason: "gate_assist",
      }),
    ).toBe(false);
  });

  it("fires on gated Yes click, not when already employer", () => {
    expect(
      shouldFireEmployerGateSelected({
        ungated: false,
        alreadyEmployer: false,
        reason: "user_click",
      }),
    ).toBe(true);
    expect(
      shouldFireEmployerGateSelected({
        ungated: false,
        alreadyEmployer: true,
        reason: "user_click",
      }),
    ).toBe(false);
    expect(
      shouldFireEmployerGateSelected({
        ungated: false,
        alreadyEmployer: false,
        reason: "page_load",
      }),
    ).toBe(false);
  });
});

describe("shouldFireEmployerFormStarted", () => {
  it("ungated: first field only, once, never on load or visible form", () => {
    expect(
      shouldFireEmployerFormStarted({
        alreadyFired: false,
        reason: "page_load",
        ungated: true,
      }),
    ).toBe(false);
    expect(
      shouldFireEmployerFormStarted({
        alreadyFired: false,
        reason: "form_visible",
        ungated: true,
      }),
    ).toBe(false);
    expect(
      shouldFireEmployerFormStarted({
        alreadyFired: false,
        reason: "gate_click",
        ungated: true,
      }),
    ).toBe(false);
    expect(
      shouldFireEmployerFormStarted({
        alreadyFired: false,
        reason: "field_interaction",
        ungated: true,
      }),
    ).toBe(true);
    expect(
      shouldFireEmployerFormStarted({
        alreadyFired: true,
        reason: "field_interaction",
        ungated: true,
      }),
    ).toBe(false);
  });

  it("gated: Yes click, first field, or quiz reveal still start the form", () => {
    expect(
      shouldFireEmployerFormStarted({
        alreadyFired: false,
        reason: "gate_click",
        ungated: false,
      }),
    ).toBe(true);
    expect(
      shouldFireEmployerFormStarted({
        alreadyFired: false,
        reason: "field_interaction",
        ungated: false,
      }),
    ).toBe(true);
    expect(
      shouldFireEmployerFormStarted({
        alreadyFired: false,
        reason: "form_visible",
        ungated: false,
      }),
    ).toBe(true);
    expect(
      shouldFireEmployerFormStarted({
        alreadyFired: true,
        reason: "field_interaction",
        ungated: false,
      }),
    ).toBe(false);
  });
});
