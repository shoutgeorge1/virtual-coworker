/**
 * Local mock of the live conversion contract (vision/lib/tracking.ts + /api/lead).
 * MOCK ONLY — does not POST to production, Zoho, or Ads.
 * Event names, aliases, and payload keys must stay aligned with production.
 */
(function (root) {
  const LP_VERSION = "mobile-cro-v2-mock";
  const ATTR_KEY = "vc_pilot_attribution";
  const PRIMARY_FIRED_KEY = "vc_primary_fired_ids";
  const FORM_START_KEY = "vc_mock_form_started";
  const PHONE_CLICK_GUARD = "vc_mock_phone_click_ts";
  const MOCK_LABEL = "MOCK_LOCAL";

  function param(name) {
    return new URLSearchParams(location.search).get(name) || "";
  }

  root.dataLayer = root.dataLayer || [];

  function emptyAttr(market) {
    return {
      utm_source: "",
      utm_medium: "",
      utm_campaign: "",
      utm_term: "",
      utm_content: "",
      gclid: "",
      gbraid: "",
      wbraid: "",
      landing_page_url: "",
      referrer: "",
      lp_version: LP_VERSION,
      lp_variant: "",
      market: market || "",
      category: "",
      variant: "",
      captured_at: "",
    };
  }

  function captureAttribution(market, extras) {
    extras = extras || {};
    const next = {
      utm_source: param("utm_source"),
      utm_medium: param("utm_medium"),
      utm_campaign: param("utm_campaign"),
      utm_term: param("utm_term"),
      utm_content: param("utm_content"),
      gclid: param("gclid"),
      gbraid: param("gbraid"),
      wbraid: param("wbraid"),
      landing_page_url: location.href.split("#")[0],
      referrer: document.referrer || "",
      lp_version: LP_VERSION,
      lp_variant: extras.lp_variant || param("lp_variant") || "",
      market: market || param("market") || "",
      category: extras.category || param("category") || "",
      variant: extras.variant || param("variant") || "",
      captured_at: new Date().toISOString(),
    };
    try {
      const prev = JSON.parse(sessionStorage.getItem(ATTR_KEY) || "{}");
      const merged = {
        utm_source: next.utm_source || prev.utm_source || "",
        utm_medium: next.utm_medium || prev.utm_medium || "",
        utm_campaign: next.utm_campaign || prev.utm_campaign || "",
        utm_term: next.utm_term || prev.utm_term || "",
        utm_content: next.utm_content || prev.utm_content || "",
        gclid: next.gclid || prev.gclid || "",
        gbraid: next.gbraid || prev.gbraid || "",
        wbraid: next.wbraid || prev.wbraid || "",
        landing_page_url: next.landing_page_url || prev.landing_page_url || "",
        referrer: next.referrer || prev.referrer || "",
        lp_version: LP_VERSION,
        lp_variant: next.lp_variant || prev.lp_variant || "",
        market: next.market || prev.market || market || "",
        category: next.category || prev.category || "",
        variant: next.variant || prev.variant || "",
        captured_at: prev.captured_at || next.captured_at,
      };
      sessionStorage.setItem(ATTR_KEY, JSON.stringify(merged));
      return merged;
    } catch {
      return next;
    }
  }

  function readAttribution(market, extras) {
    try {
      const raw = sessionStorage.getItem(ATTR_KEY);
      if (raw) {
        const prev = JSON.parse(raw);
        return Object.assign(emptyAttr(market), prev, captureAttribution(market || prev.market, {
          category: (extras && extras.category) || prev.category,
          variant: (extras && extras.variant) || prev.variant,
          lp_variant: (extras && extras.lp_variant) || prev.lp_variant,
        }));
      }
    } catch (_) {}
    return captureAttribution(market, extras || {});
  }

  function trackEvent(name, payload) {
    payload = payload || {};
    const market = String(payload.market || "");
    const eventPayload = Object.assign({ event: name }, payload, {
      market: market,
      site_surface: market || undefined,
      lp_version: LP_VERSION,
    });
    if (payload.lp_variant) eventPayload.lp_variant = payload.lp_variant;
    root.dataLayer.push(eventPayload);
    return eventPayload;
  }

  function alreadyFiredPrimary(submissionId) {
    try {
      const ids = JSON.parse(sessionStorage.getItem(PRIMARY_FIRED_KEY) || "[]");
      return ids.indexOf(submissionId) !== -1;
    } catch {
      return false;
    }
  }

  function markPrimaryFired(submissionId) {
    try {
      const ids = JSON.parse(sessionStorage.getItem(PRIMARY_FIRED_KEY) || "[]");
      if (ids.indexOf(submissionId) === -1) {
        ids.push(submissionId);
        sessionStorage.setItem(PRIMARY_FIRED_KEY, JSON.stringify(ids.slice(-50)));
      }
    } catch (_) {}
  }

  function trackPhoneClick(payload) {
    // Per-click pair (canonical + alias). Guard only against the same tick double-bind.
    const now = Date.now();
    const last = Number(sessionStorage.getItem(PHONE_CLICK_GUARD) || 0);
    if (now - last < 40) return;
    sessionStorage.setItem(PHONE_CLICK_GUARD, String(now));
    trackEvent("phone_cta_clicked", Object.assign({}, payload, { is_qualified_call: false }));
    trackEvent("phone_click", Object.assign({}, payload, {
      is_qualified_call: false,
      alias_of: "phone_cta_clicked",
    }));
  }

  function trackCalendlyClick(payload) {
    trackEvent("calendly_cta_clicked", payload);
    trackEvent("calendly_click", Object.assign({}, payload, { alias_of: "calendly_cta_clicked" }));
  }

  function markFormStarted(ctx) {
    if (sessionStorage.getItem(FORM_START_KEY) === "1") return false;
    sessionStorage.setItem(FORM_START_KEY, "1");
    const extra = Object.assign({
      gate_variant: "inline",
      lp_surface: "form",
      cta_mode: "form_primary",
      landing_type: "form_lp",
      start_reason: "field_interaction",
    }, ctx || {});
    trackEvent("employer_form_started", extra);
    trackEvent("form_start", Object.assign({}, extra, { alias_of: "employer_form_started" }));
    return true;
  }

  function resetFormStartedForQa() {
    sessionStorage.removeItem(FORM_START_KEY);
  }

  function trackValidEmployerSubmit(opts) {
    if (opts.conversionEligible === false) {
      trackEvent("employer_inquiry_log_only", {
        market: opts.market,
        submission_id: opts.submissionId,
        primary_eligible: false,
        bidding_primary: false,
        modeled_value_for_bidding: false,
      });
      return;
    }
    if (!opts.submissionId || alreadyFiredPrimary(opts.submissionId)) {
      trackEvent("employer_inquiry_submitted_deduped", {
        market: opts.market,
        submission_id: opts.submissionId,
      });
      return;
    }
    markPrimaryFired(opts.submissionId);
    const payload = {
      market: opts.market,
      country: opts.market === "au" ? "AU" : "US",
      submission_id: opts.submissionId,
      role: opts.role || "",
      role_category: opts.category || "",
      category: opts.category || "",
      variant: opts.variant || "",
      company_size: opts.companySize || "",
      positions_needed: opts.positionsNeeded || "",
      hiring_timeline: opts.hiringTimeline || "",
      lead_score: opts.leadScore,
      estimated_lead_value: opts.estimatedLeadValue,
      value_kind: opts.valueKind || "estimated_modeled",
      fit_label: opts.fitLabel || "",
      landing_page: opts.landingPage || "",
      utm_source: opts.utmSource || "",
      utm_medium: opts.utmMedium || "",
      utm_campaign: opts.utmCampaign || "",
      utm_term: opts.utmTerm || "",
      utm_content: opts.utmContent || "",
      gclid: opts.gclid || "",
      gbraid: opts.gbraid || "",
      wbraid: opts.wbraid || "",
      submitted_at: opts.submittedAt || "",
      lp_surface: opts.lpSurface || "form",
      cta_mode: opts.ctaMode || "form_primary",
      landing_type: "form_lp",
      lp_variant: opts.lpVariant || "",
      primary_eligible: true,
      bidding_primary: false,
      modeled_value_for_bidding: false,
      funnel_step: "form_submit_success",
      is_job_order: false,
      is_placement: false,
      is_qualified_call: false,
      mock: MOCK_LABEL,
    };
    trackEvent("employer_inquiry_submitted", payload);
    trackEvent("form_submit_success", Object.assign({}, payload, { alias_of: "employer_inquiry_submitted" }));
    trackEvent("form_submit", Object.assign({}, payload, { alias_of: "employer_inquiry_submitted" }));
  }

  function normalizePhone(raw, market) {
    const d = String(raw || "").replace(/\D/g, "");
    if (!d) return "";
    if (market === "au") {
      if (d.indexOf("61") === 0) return "+" + d;
      return "+61" + d.replace(/^0/, "");
    }
    if (d.indexOf("1") === 0 && d.length === 11) return "+" + d;
    return "+1" + d;
  }

  const EMAIL_RE = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

  /** Mirrors validateEmployerLead + a mock durable accept. Never hits Zoho. */
  function mockLeadApi(body) {
    const market = String(body.market || "").toLowerCase();
    if (market !== "us" && market !== "au") {
      return { status: 400, json: { ok: false, code: "invalid_market", error: "market must be us|au" } };
    }
    if (String(body.intent || "") !== "employer") {
      return { status: 400, json: { ok: false, code: "invalid_intent", error: "employer intent required" } };
    }
    if (String(body.website || body.company_url || "").trim()) {
      return { status: 403, json: { ok: false, code: "honeypot", error: "Unable to submit." } };
    }
    const name = String(body.name || "").trim();
    const email = String(body.email || "").trim().toLowerCase();
    const phone = String(body.phone || "").trim();
    if (!name || !email || !phone) {
      return { status: 400, json: { ok: false, code: "missing_fields", error: "name, work email, and phone are required" } };
    }
    if (!EMAIL_RE.test(email)) {
      return { status: 400, json: { ok: false, code: "invalid_email", error: "valid work email required" } };
    }
    const started = Number(body.form_started_at || 0);
    if (started > 0 && Date.now() - started < 2500) {
      return { status: 400, json: { ok: false, code: "too_fast", error: "Please take a moment and try again." } };
    }
    const submission_id = "vc_" + market + "_mock_" + Date.now().toString(36);
    const record = Object.assign({}, body, {
      submission_id: submission_id,
      phone: normalizePhone(phone, market) || phone,
      mock: MOCK_LABEL,
      delivery: "mock_local",
      conversion_eligible: true,
      lead_delivery_succeeded: true,
      zoho_synced: false,
      is_job_order: false,
      is_placement: false,
    });
    try {
      sessionStorage.setItem("vc_mock_last_lead", JSON.stringify(record));
    } catch (_) {}
    return {
      status: 200,
      json: {
        ok: true,
        stored: true,
        duplicate: false,
        submission_id: submission_id,
        delivery: "mock_local",
        conversion_eligible: true,
        lead_delivery_succeeded: true,
        lead_score: 40,
        estimated_lead_value: 280,
        value_kind: "estimated_modeled",
        fit_label: "employer",
        mock: MOCK_LABEL,
      },
    };
  }

  root.VCContract = {
    LP_VERSION: LP_VERSION,
    MOCK_LABEL: MOCK_LABEL,
    captureAttribution: captureAttribution,
    readAttribution: readAttribution,
    trackEvent: trackEvent,
    trackPhoneClick: trackPhoneClick,
    trackCalendlyClick: trackCalendlyClick,
    markFormStarted: markFormStarted,
    resetFormStartedForQa: resetFormStartedForQa,
    trackValidEmployerSubmit: trackValidEmployerSubmit,
    alreadyFiredPrimary: alreadyFiredPrimary,
    mockLeadApi: mockLeadApi,
    normalizePhone: normalizePhone,
    EMAIL_RE: EMAIL_RE,
  };
})(window);
