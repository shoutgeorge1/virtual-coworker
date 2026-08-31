/**
 * Browser QA for the MOCK conversion contract. No Zoho. No Ads mutate.
 */
(function () {
  const lines = [];
  function pass(msg) { lines.push("PASS  " + msg); }
  function fail(msg) { lines.push("FAIL  " + msg); }
  function assert(cond, msg) { if (cond) pass(msg); else fail(msg); }

  sessionStorage.clear();
  window.dataLayer = [];
  VCContract.resetFormStartedForQa();

  const attr = VCContract.captureAttribution("us", { category: "bookkeeping" });
  assert(attr.lp_version === "stage1-v8", "lp_version stage1-v8");
  sessionStorage.clear();
  history.replaceState({}, "", location.pathname + "?gclid=TESTGCLID&utm_source=google&utm_medium=cpc&utm_campaign=VC_US_S_CORE&utm_term=hire+va");
  const attr2 = VCContract.captureAttribution("us", { category: "bookkeeping" });
  assert(attr2.gclid === "TESTGCLID", "gclid captured");
  assert(attr2.utm_campaign === "VC_US_S_CORE", "utm_campaign captured");

  VCContract.markFormStarted({ market: "us", category: "bookkeeping" });
  VCContract.markFormStarted({ market: "us", category: "bookkeeping" });
  const starts = window.dataLayer.filter((e) => e.event === "employer_form_started");
  const aliases = window.dataLayer.filter((e) => e.event === "form_start");
  assert(starts.length === 1, "employer_form_started once (got " + starts.length + ")");
  assert(aliases.length === 1, "form_start alias once");
  assert(aliases[0].alias_of === "employer_form_started", "form_start alias_of set");

  VCContract.trackEvent("employer_form_validation_error", { market: "us", fields: "name,email" });
  assert(window.dataLayer.some((e) => e.event === "employer_form_validation_error"), "validation event");

  VCContract.trackEvent("quiz_started", { market: "us", step: "1", assist_type: "guided_match" });
  VCContract.trackEvent("guided_match_started", { market: "us", step: "1", assist_type: "guided_match", alias_of: "quiz_started" });
  VCContract.trackEvent("quiz_step", { market: "us", step: "1", answer: "Bookkeeping / accounting" });
  assert(window.dataLayer.filter((e) => e.event === "quiz_step").length >= 1, "quiz_step diagnostic (not Ads)");
  assert(window.dataLayer.filter((e) => e.event === "guided_match_started").length === 1, "guided_match_started diagnostic");
  assert(window.dataLayer.filter((e) => e.event === "employer_form_started").length === 1, "quiz_step did not add another employer_form_started");

  window.dataLayer = [];
  VCContract.resetFormStartedForQa();
  sessionStorage.removeItem("vc_mock_form_started");
  VCContract.trackEvent("quiz_step", { market: "us", step: "1", answer: "Admin / EA" });
  VCContract.trackEvent("quiz_step_completed", { market: "us", step: "2", answer: "complete" });
  VCContract.trackEvent("contact_step_reached", { market: "us", funnel_step: "contact_step_reached" });
  assert(window.dataLayer.filter((e) => e.event === "employer_form_started").length === 0, "role / step / contact-reach do not fire employer_form_started");
  assert(window.dataLayer.filter((e) => e.event === "employer_inquiry_submitted").length === 0, "diagnostics are not Ads submit");
  VCContract.markFormStarted({ market: "us" });
  assert(window.dataLayer.filter((e) => e.event === "employer_form_started").length === 1, "employer_form_started only after contact-field markFormStarted");
  window.dataLayer = [];

  const honey = VCContract.mockLeadApi({
    market: "us", intent: "employer", name: "Ada", email: "ada@co.com", phone: "2015550100",
    website: "http://spam.test",
  });
  assert(honey.json.code === "honeypot", "honeypot rejects");

  const missing = VCContract.mockLeadApi({ market: "us", intent: "employer", name: "", email: "", phone: "" });
  assert(missing.json.code === "missing_fields", "missing fields reject");

  const fast = VCContract.mockLeadApi({
    market: "us", intent: "employer", name: "Ada Lovelace", email: "ada@co.com", phone: "2015550100",
    form_started_at: Date.now(),
  });
  assert(fast.json.code === "too_fast", "too_fast < 2500ms");

  const ok = VCContract.mockLeadApi({
    market: "us",
    intent: "employer",
    name: "Ada Lovelace",
    email: "ada@co.com",
    phone: "2015550100",
    role: "Bookkeeping support",
    category: "bookkeeping",
    schedule: "full-time",
    company_size: "11-50",
    positions_needed: "1",
    website: "",
    company_website: "https://co.com",
    gclid: attr2.gclid,
    utm_source: attr2.utm_source,
    utm_campaign: attr2.utm_campaign,
    form_started_at: Date.now() - 4000,
    lp_version: "stage1-v8",
    lp_surface: "form",
    message: "Hours requested: US business hours",
  });
  assert(ok.status === 200 && ok.json.ok && ok.json.submission_id, "mock /api/lead success");
  assert(ok.json.mock === "MOCK_LOCAL", "explicit MOCK label");
  assert(ok.json.zoho_synced !== true, "no Zoho write");
  const stored = JSON.parse(sessionStorage.getItem("vc_mock_last_lead") || "{}");
  assert(stored.gclid === "TESTGCLID", "attribution survives into payload");
  assert(stored.role === "Bookkeeping support", "role context on payload");
  assert(stored.schedule === "full-time", "schedule uses existing enum");
  assert(stored.lp_surface === "form", "lp_surface form (money LP, not /quiz route)");
  assert(stored.phone.indexOf("+1") === 0, "US phone normalized");

  VCContract.trackValidEmployerSubmit({
    market: "us",
    submissionId: ok.json.submission_id,
    conversionEligible: true,
    role: "Bookkeeping support",
    category: "bookkeeping",
    companySize: "11-50",
    positionsNeeded: "1",
  });
  const submitted = window.dataLayer.filter((e) => e.event === "employer_inquiry_submitted");
  const aliasA = window.dataLayer.filter((e) => e.event === "form_submit_success");
  const aliasB = window.dataLayer.filter((e) => e.event === "form_submit");
  assert(submitted.length === 1, "employer_inquiry_submitted once after success");
  assert(aliasA.length === 1 && aliasB.length === 1, "submit aliases preserved");
  assert(submitted[0].bidding_primary === false, "bidding_primary stays false");

  VCContract.trackValidEmployerSubmit({
    market: "us",
    submissionId: ok.json.submission_id,
    conversionEligible: true,
  });
  assert(
    window.dataLayer.filter((e) => e.event === "employer_inquiry_submitted_deduped").length === 1,
    "thank-you / strict-mode sid dedupe"
  );
  assert(window.dataLayer.filter((e) => e.event === "employer_inquiry_submitted").length === 1, "no duplicate submitted");

  const au = VCContract.mockLeadApi({
    market: "au", intent: "employer", name: "Alex Lee", email: "alex@co.au", phone: "0400000000",
    form_started_at: Date.now() - 4000,
  });
  const auStored = JSON.parse(sessionStorage.getItem("vc_mock_last_lead") || "{}");
  assert(au.json.ok, "AU mock accept");
  assert(auStored.phone.indexOf("+61") === 0, "AU phone +61");

  VCContract.trackPhoneClick({ market: "us" });
  const phones = window.dataLayer.filter((e) => e.event === "phone_cta_clicked");
  const phoneAlias = window.dataLayer.filter((e) => e.event === "phone_click");
  assert(phones.length === 1 && phoneAlias.length === 1, "phone click = canonical + alias once");
  assert(phones[0].is_qualified_call === false, "phone is not a qualified call");

  VCContract.trackCalendlyClick({ market: "us", href: "https://calendly.com/cheyenne-virtualcoworker/30min" });
  assert(window.dataLayer.some((e) => e.event === "calendly_cta_clicked"), "calendly canonical");
  assert(window.dataLayer.some((e) => e.event === "calendly_click"), "calendly alias");

  const fails = lines.filter((l) => l.indexOf("FAIL") === 0);
  document.getElementById("out").textContent =
    lines.join("\n") + "\n\n" + (fails.length ? fails.length + " failed" : "All checks passed") +
    "\nThank-you path: thank-you.html?market=us|au&sid=… (production /thank-you unchanged)\n";
  document.getElementById("out").className = fails.length ? "fail" : "pass";
})();
