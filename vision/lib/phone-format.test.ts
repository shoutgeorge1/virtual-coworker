import { describe, expect, it } from "vitest";
import { formatPhoneInput, normalizePhoneForStorage, phoneDigits, validateUsPhone } from "./phone-format";

describe("formatPhoneInput US", () => {
  it("formats NANP as the user types", () => {
    expect(formatPhoneInput("2", "us")).toBe("(2");
    expect(formatPhoneInput("201", "us")).toBe("(201");
    expect(formatPhoneInput("2015", "us")).toBe("(201) 5");
    expect(formatPhoneInput("2015550123", "us")).toBe("(201) 555-0123");
    expect(formatPhoneInput("(201) 555-0123", "us")).toBe("(201) 555-0123");
  });

  it("keeps a leading +1 country code", () => {
    expect(formatPhoneInput("+12015550123", "us")).toBe("+1 (201) 555-0123");
    expect(formatPhoneInput("12015550123", "us")).toBe("+1 (201) 555-0123");
  });

  it("does not force NANP on a foreign + number", () => {
    expect(formatPhoneInput("+61412345678", "us")).toBe("+61412345678");
  });

  it("allows extra digits as an extension tail", () => {
    expect(formatPhoneInput("201555012399", "us")).toBe("(201) 555-0123 99");
  });
});

describe("formatPhoneInput AU", () => {
  it("formats mobile 04XX XXX XXX", () => {
    expect(formatPhoneInput("04", "au")).toBe("04");
    expect(formatPhoneInput("0412345678", "au")).toBe("0412 345 678");
  });

  it("formats 1300 and +61", () => {
    expect(formatPhoneInput("1300886740", "au")).toBe("1300 886 740");
    expect(formatPhoneInput("+61412345678", "au")).toBe("+61 412 345 678");
  });

  it("does not force +61 while the country code is still incomplete", () => {
    expect(formatPhoneInput("+", "au")).toBe("+");
    expect(formatPhoneInput("+6", "au")).toBe("+6");
    expect(formatPhoneInput("+61", "au")).toBe("+61");
    expect(formatPhoneInput("+614", "au")).toBe("+61 4");
    expect(formatPhoneInput("+61412", "au")).toBe("+61 412");
  });

  it("does not force +61 on a non-AU plus number", () => {
    expect(formatPhoneInput("+12015550123", "au")).toBe("+12015550123");
  });

  it("formats landlines as (0X) XXXX XXXX", () => {
    expect(formatPhoneInput("0298765432", "au")).toBe("(02) 9876 5432");
  });
});

describe("normalizePhoneForStorage", () => {
  it("stores US as E.164 when complete", () => {
    expect(normalizePhoneForStorage("(201) 555-0123", "us")).toBe("+12015550123");
    expect(normalizePhoneForStorage("+1 (201) 555-0123", "us")).toBe("+12015550123");
  });

  it("stores AU mobile / 1300 as +61", () => {
    expect(normalizePhoneForStorage("0412 345 678", "au")).toBe("+61412345678");
    expect(normalizePhoneForStorage("1300 886 740", "au")).toBe("+611300886740");
  });

  it("does not invent a country code for short values", () => {
    expect(normalizePhoneForStorage("555", "us")).toBe("555");
    expect(normalizePhoneForStorage("04", "au")).toBe("04");
  });

  it("phoneDigits strips formatting", () => {
    expect(phoneDigits("(201) 555-0123")).toBe("2015550123");
  });
});

describe("validateUsPhone", () => {
  it("accepts formatted US numbers", () => {
    expect(validateUsPhone("(951) 555-0123")).toEqual({
      ok: true,
      e164: "+19515550123",
      national10: "9515550123",
    });
    expect(validateUsPhone("951-555-0123")).toMatchObject({ ok: true, e164: "+19515550123" });
    expect(validateUsPhone("+1 951 555 0123")).toMatchObject({ ok: true, e164: "+19515550123" });
  });

  it("rejects Philippine numbers", () => {
    expect(validateUsPhone("+63 917 123 4567")).toEqual({
      ok: false,
      code: "ph_job_seeker_phone",
    });
    expect(validateUsPhone("0917 123 4567")).toEqual({
      ok: false,
      code: "ph_job_seeker_phone",
    });
  });

  it("rejects incomplete and overlong numbers", () => {
    expect(validateUsPhone("951-555")).toEqual({ ok: false, code: "invalid_us_phone" });
    expect(validateUsPhone("95155501231234")).toEqual({
      ok: false,
      code: "invalid_us_phone",
    });
    expect(validateUsPhone("")).toEqual({ ok: false, code: "invalid_us_phone" });
  });

  it("does not reject a legitimate US 917 area code as PH", () => {
    expect(validateUsPhone("917-555-0123")).toMatchObject({ ok: true, e164: "+19175550123" });
  });
});

