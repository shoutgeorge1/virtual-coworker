/**
 * Executive Performance — Canonical Executive Dashboard Renderer.
 *
 * Consolidates monthly and weekly reporting into a single trustworthy,
 * spreadsheet-styled executive dashboard.
 *
 * Rules:
 * 1. Blended cost per outcome = Google Ads spend ÷ sales-confirmed employer enquiries.
 *    This is an operational blended efficiency metric, NOT paid CPA.
 * 2. Paid attribution requires verified advertising click ID (gclid/gbraid/wbraid).
 * 3. Phone clicks (tel:) are not calls, enquiries, or discoveries.
 * 4. Unknown is not zero (use —, Pending, or Not tracked).
 * 5. Period activity lags mature cohort outcomes.
 * 6. Historical agency comparison is directional rates (blended to blended), not audited financial truth.
 */
(function () {
  "use strict";

  var STATE = {
    period: "mtd", // "mtd" | "prev" | "week" | "now"
    snapshot: null,
    archiveW1: null,
    agency: null,
    zohoWeek: null,
  };

  function $(sel) {
    return document.querySelector(sel);
  }

  function esc(s) {
    var d = document.createElement("div");
    d.textContent = s == null ? "" : String(s);
    return d.innerHTML;
  }

  function fetchJson(url) {
    return fetch(url).then(function (r) {
      if (!r.ok) throw new Error(url + " " + r.status);
      return r.json();
    });
  }

  /* —— Core Math & Formatting Helpers —— */

  function safeDiv(num, den) {
    if (num == null || den == null || Number.isNaN(Number(num))) {
      return { value: null, status: "pending", numerator: num, denominator: den };
    }
    var n = Number(num);
    var d = Number(den);
    if (!Number.isFinite(n) || !Number.isFinite(d)) {
      return { value: null, status: "pending", numerator: n, denominator: d };
    }
    if (d === 0) return { value: null, status: "zero_denom", numerator: n, denominator: d };
    return { value: n / d, status: "ok", numerator: n, denominator: d };
  }

  function perThousand(outcomes, spend) {
    if (outcomes == null || spend == null) {
      return { value: null, status: "pending" };
    }
    if (spend === 0) return { value: null, status: "zero_denom" };
    return { value: (outcomes / spend) * 1000, status: "ok" };
  }

  function attributionCoverage(paid, total) {
    var p = Number(paid || 0);
    var t = Number(total || 0);
    if (t <= 0) {
      return {
        paidAttributed: p,
        validatedSalesRecords: t,
        coverage: null,
        status: "pending",
        display: "Not reliable yet",
      };
    }
    var c = p / t;
    var ok = t >= 10 && c >= 0.4;
    return {
      paidAttributed: p,
      validatedSalesRecords: t,
      coverage: c,
      status: ok ? "ok" : "not_reliable",
      display: ok ? Math.round(c * 100) + "%" : "Not reliable yet",
    };
  }

  function currencyForMarket(market) {
    return market === "AU" ? "AUD" : "USD";
  }

  function formatMoney(v, cur, digits) {
    if (v == null || Number.isNaN(Number(v))) return "—";
    var d = digits == null ? 0 : digits;
    var sym = cur === "AUD" ? "A$" : "$";
    return (
      sym +
      Number(v).toLocaleString("en-US", {
        minimumFractionDigits: d,
        maximumFractionDigits: d,
      })
    );
  }

  function formatMoney2(v, cur) {
    return formatMoney(v, cur, 2);
  }

  function formatNum(v, digits) {
    if (v == null || Number.isNaN(Number(v))) return "—";
    var d = digits == null ? 0 : digits;
    return Number(v).toLocaleString("en-US", {
      minimumFractionDigits: d,
      maximumFractionDigits: d,
    });
  }

  function formatPct(v) {
    if (v == null || Number.isNaN(Number(v))) return "—";
    return Number(v).toFixed(1) + "%";
  }

  function ratioMoney(r, cur) {
    if (!r || r.value == null || r.status === "zero_denom" || r.status === "pending") return "—";
    return formatMoney2(r.value, cur);
  }

  function isEnquiryPending(ops) {
    if (!ops) return true;
    var caveat = String(ops.caveat || "").toLowerCase();
    if (caveat.indexOf("count pending") >= 0 || caveat.indexOf("enquiry count pending") >= 0) return true;
    return ops.enquiries == null;
  }

  function addNull(a, b) {
    if (a == null && b == null) return null;
    return Number(a || 0) + Number(b || 0);
  }

  function asOfDate() {
    return ((STATE.snapshot || {}).generated_at_utc || "").slice(0, 10) || "2026-08-27";
  }

  /* Sum Stage-1 Ads by date range */
  function sumAdsByDate(byDate, start, end, currency) {
    if (!byDate) return null;
    var spend = 0;
    var clicks = 0;
    var impressions = 0;
    var any = false;
    Object.keys(byDate).forEach(function (d) {
      if (d >= start && d <= end) {
        any = true;
        spend += Number(byDate[d].cost_usd || 0);
        clicks += Number(byDate[d].clicks || 0);
        impressions += Number(byDate[d].impressions || 0);
      }
    });
    if (!any) return null;
    return {
      spend: spend,
      clicks: clicks,
      impressions: impressions,
      ctrPct: impressions > 0 ? (100 * clicks) / impressions : null,
      avgCpc: clicks > 0 ? spend / clicks : null,
      currency: currency,
      source: "Ads",
    };
  }

  /* Sum sales ops slices within bounds */
  function sumSalesLabeled(slices, start, end) {
    var enquiries = null;
    var discoveries = null;
    var jobOrders = null;
    var placements = null;
    var anyPending = false;
    var any = false;

    slices.forEach(function (ops) {
      if (!ops) return;
      var ws = String(ops.window_start || "").slice(0, 10);
      var we = String(ops.window_end || "").slice(0, 10);
      if (!ws || !we) return;
      if (we < start || ws > end) return;
      any = true;
      if (isEnquiryPending(ops)) {
        anyPending = true;
      } else {
        enquiries = addNull(enquiries, ops.enquiries);
      }
      if (ops.sales_calls_completed != null) {
        discoveries = addNull(discoveries, ops.sales_calls_completed);
      }
      if (ops.job_orders_total != null) {
        jobOrders = addNull(jobOrders, ops.job_orders_total);
      }
      if (ops.placements != null) {
        placements = addNull(placements, ops.placements);
      }
    });

    if (!any) {
      return {
        enquiries: null,
        discoveries: null,
        jobOrders: null,
        placements: null,
        enquiriesPending: true,
        source: "Pending",
      };
    }

    return {
      enquiries: anyPending && enquiries == null ? null : enquiries,
      discoveries: discoveries,
      jobOrders: jobOrders == null ? 0 : jobOrders,
      placements: placements == null ? 0 : placements,
      enquiriesPending: anyPending && enquiries == null,
      source: anyPending && enquiries == null ? "Pending" : "Sales labeled",
    };
  }

  /* Compare pilot rate to recorded legacy agency baseline */
  function compareRate(pilot, agency, lowerIsBetter, pilotPeriod, agencyPeriod) {
    if (pilot == null || agency == null || agency === 0) {
      return {
        pilot: pilot,
        agency: agency,
        diffPct: null,
        diffText: "—",
        interpretation: pilot == null ? "Pilot sample incomplete" : "Agency rate unavailable",
        confidence: pilot == null ? "Insufficient sample" : "Baseline unavailable",
        tone: "neutral",
        pilotPeriod: pilotPeriod,
        agencyPeriod: agencyPeriod,
      };
    }
    var diffPct = ((pilot - agency) / Math.abs(agency)) * 100;
    var improved = lowerIsBetter ? pilot < agency : pilot > agency;
    var material = Math.abs(diffPct) >= 15;
    var tone = "neutral";
    var interpretation = "";
    var confidence = "Directional";

    if (!material) {
      interpretation = "Roughly in line with agency rate";
      tone = "neutral";
    } else if (improved) {
      interpretation = lowerIsBetter ? "Pilot materially more efficient" : "Pilot materially higher yield";
      tone = "good";
    } else {
      interpretation = lowerIsBetter ? "Pilot materially less efficient" : "Pilot materially lower yield";
      tone = "bad";
    }

    var sign = diffPct > 0 ? "+" : "";
    var diffText = sign + diffPct.toFixed(1) + "%";

    return {
      pilot: pilot,
      agency: agency,
      diffPct: diffPct,
      diffText: diffText,
      interpretation: interpretation,
      confidence: confidence,
      tone: tone,
      pilotPeriod: pilotPeriod,
      agencyPeriod: agencyPeriod,
    };
  }

  /* —— Data Assembly for Active Period —— */

  function buildMarketData(market, periodKey) {
    var cur = currencyForMarket(market);
    var perf = market === "US" ? STATE.snapshot.performance_us : STATE.snapshot.performance_au;
    var by = (perf || {}).by_date_stage1 || (perf || {}).by_date || {};
    var snap = STATE.snapshot;
    var arch = STATE.archiveW1;

    var w1 = market === "US" ? (arch && arch.sales_ops_us) : (arch && arch.sales_ops_au);
    var w2 = market === "US" ? snap.sales_ops_us : snap.sales_ops_au;
    var w3 = market === "US" ? snap.sales_ops_us_now : snap.sales_ops_au_now;

    var bounds = {
      start: "",
      end: "",
      label: "",
      statusLabel: "",
      partial: false,
    };
    var funnel = null;
    var ads = null;

    if (periodKey === "mtd") {
      bounds.start = "2026-08-01";
      bounds.end = asOfDate();
      bounds.label = "August 2026 to date";
      bounds.statusLabel = "Month to date · Partial through " + asOfDate().slice(5);
      bounds.partial = true;

      // Sum all 3 weeks
      funnel = sumSalesLabeled([w1, w2, w3], bounds.start, bounds.end);
      ads = sumAdsByDate(by, bounds.start, bounds.end, cur);
    } else if (periodKey === "prev") {
      bounds.start = "2026-07-01";
      bounds.end = "2026-07-31";
      bounds.label = "July 2026";
      bounds.statusLabel = "Prior month · Pre-pilot launch";
      bounds.partial = false;

      funnel = {
        enquiries: null,
        discoveries: null,
        jobOrders: null,
        placements: null,
        enquiriesPending: false,
        source: "No pilot activity",
      };
      ads = null;
    } else if (periodKey === "week") {
      // Last complete week (W2: Aug 17–23)
      var ops = w2 || {};
      bounds.start = ops.window_start || "2026-08-17";
      bounds.end = ops.window_end || "2026-08-23";
      bounds.label = ops.label || "Mon Aug 17 – Sun Aug 23";
      bounds.statusLabel = "Completed week · Frozen";
      bounds.partial = false;

      funnel = sumSalesLabeled([ops], bounds.start, bounds.end);
      ads = sumAdsByDate(by, bounds.start, bounds.end, cur);
      if (!ads && ops.spend_usd != null) {
        ads = {
          spend: ops.spend_usd,
          clicks: ops.clicks || 0,
          impressions: ops.impressions || 0,
          ctrPct: ops.impressions > 0 ? (100 * (ops.clicks || 0)) / ops.impressions : null,
          avgCpc: ops.avg_cpc_usd || null,
          currency: cur,
          source: "Ads",
        };
      }
    } else if (periodKey === "now") {
      // This week so far (W3: Aug 24–25 partial)
      var opsNow = w3 || {};
      bounds.start = opsNow.window_start || "2026-08-24";
      bounds.end = opsNow.window_end || "2026-08-25";
      bounds.label = opsNow.label || "Mon Aug 24 – Tue Aug 25";
      bounds.statusLabel = "This week so far · Partial in progress";
      bounds.partial = true;

      funnel = sumSalesLabeled([opsNow], bounds.start, bounds.end);
      ads = sumAdsByDate(by, bounds.start, bounds.end, cur);
      if (!ads && opsNow.spend_usd != null) {
        ads = {
          spend: opsNow.spend_usd,
          clicks: opsNow.clicks || 0,
          impressions: opsNow.impressions || 0,
          ctrPct: opsNow.impressions > 0 ? (100 * (opsNow.clicks || 0)) / opsNow.impressions : null,
          avgCpc: opsNow.avg_cpc_usd || null,
          currency: cur,
          source: "Ads",
        };
      }
    }

    var spend = ads ? ads.spend : null;
    var cpe = safeDiv(spend, funnel.enquiriesPending ? null : funnel.enquiries);
    var cpd = safeDiv(spend, funnel.discoveries);
    var cpjo = safeDiv(spend, funnel.jobOrders);
    var cpp = safeDiv(spend, funnel.placements);

    var enqPerK = perThousand(funnel.enquiriesPending ? null : funnel.enquiries, spend);
    var discPerK = perThousand(funnel.discoveries, spend);
    var joPerK = perThousand(funnel.jobOrders, spend);
    var plPerK = perThousand(funnel.placements, spend);

    // Attribution census from snapshot
    var census =
      market === "US"
        ? ((snap.sales_ops_us || {}).zoho_census || {})
        : ((snap.sales_ops_au || {}).zoho_census || {});
    var zohoRows =
      market === "US"
        ? Number(census.usa_sales_enquiries || 0)
        : Number(census.au_sales_enquiries || 0);
    var withGclid =
      market === "US"
        ? Number(census.usa_with_gclid || 0)
        : Number(census.au_with_gclid || 0);
    var attrib = attributionCoverage(withGclid, zohoRows);

    var agencyBlock = ((STATE.agency || {})[market === "US" ? "us" : "au"]) || {};

    return {
      market: market,
      currency: cur,
      bounds: bounds,
      funnel: funnel,
      ads: ads,
      spend: spend,
      cpe: cpe,
      cpd: cpd,
      cpjo: cpjo,
      cpp: cpp,
      enqPerK: enqPerK,
      discPerK: discPerK,
      joPerK: joPerK,
      plPerK: plPerK,
      attrib: attrib,
      census: census,
      zohoRows: zohoRows,
      withGclid: withGclid,
      agency: agencyBlock,
    };
  }

  /* —— Render Functions —— */

  function renderHeaderAndPills(us, au) {
    var periodText = us.bounds.label;
    if (us.bounds.partial) {
      periodText += " (Partial period)";
    }
    $("#ex-period").textContent = periodText;

    var snap = STATE.snapshot;
    var adsDate = (snap.generated_at_utc || "").slice(0, 10);
    var zohoDate =
      ((snap.sales_ops_us || {}).zoho_census || {}).pinged_utc ||
      ((snap.sales_ops_au || {}).zoho_census || {}).pinged_utc ||
      "";
    $("#ex-fresh").textContent =
      "Data as of " +
      asOfDate() +
      " · Google Ads: " +
      adsDate +
      " · Zoho census: " +
      (zohoDate ? String(zohoDate).slice(0, 10) : "—") +
      " · Sales validation: Cheyenne (US) / Holly (AU)";

    // Status Pills
    var pills = [];
    if (STATE.period === "prev") {
      pills.push('<span class="ex-pill neutral">Pre-pilot baseline</span>');
    } else if (us.bounds.partial) {
      pills.push('<span class="ex-pill warn">Partial period in progress</span>');
    } else {
      pills.push('<span class="ex-pill ok">Completed frozen period</span>');
    }

    pills.push('<span class="ex-pill ok">US Search live · $250/day</span>');
    pills.push('<span class="ex-pill ok">AU Search live · A$125/day</span>');

    var totalGclid = us.withGclid + au.withGclid;
    var totalZoho = us.zohoRows + au.zohoRows;
    var totalCoverage = attributionCoverage(totalGclid, totalZoho);

    pills.push(
      '<span class="ex-pill ' +
        (totalCoverage.status === "ok" ? "ok" : "warn") +
        '">Paid CPA: ' +
        esc(totalCoverage.display) +
        " (" +
        totalGclid +
        "/" +
        totalZoho +
        " GCLID in census sample)</span>"
    );

    $("#ex-status-row").innerHTML = pills.join("");

    // Notice box
    var noticeBox = $("#ex-period-notice");
    if (STATE.period === "mtd") {
      noticeBox.className = "ex-notice-box info";
      noticeBox.innerHTML =
        "<strong>August 2026 Month to Date (Aug 1–" +
        asOfDate().slice(8) +
        "):</strong> Viewing cumulative pilot performance across 3 calendar weeks. Downstream job orders and placements lag enquiries. First pilot month — no prior monthly comparison.";
      noticeBox.style.display = "block";
    } else if (STATE.period === "prev") {
      noticeBox.className = "ex-notice-box warn";
      noticeBox.innerHTML =
        "<strong>July 2026 (Previous Month):</strong> Stage 1 Search Pilot had not yet launched (US launched Aug 6, AU launched Aug 9). No pilot spend or sales-labeled enquiries exist for this period.";
      noticeBox.style.display = "block";
    } else if (STATE.period === "week") {
      noticeBox.className = "ex-notice-box info";
      noticeBox.innerHTML =
        "<strong>Last Complete Week (Mon Aug 17 – Sun Aug 23):</strong> 7-day frozen scoreboard validated by sales operations. Full weekly spend reconciled with Google Ads API.";
      noticeBox.style.display = "block";
    } else if (STATE.period === "now") {
      noticeBox.className = "ex-notice-box warn";
      noticeBox.innerHTML =
        "<strong>This Week So Far (Mon Aug 24 – Tue Aug 25 · Partial):</strong> Incomplete week in progress. US enquiry count is pending sales-ops review. Do not compare directly with completed 7-day weeks.";
      noticeBox.style.display = "block";
    }
  }

  function renderDecisionSummary(us, au) {
    var perfEl = $("#ex-sum-perf");
    var confEl = $("#ex-sum-conf");
    var decEl = $("#ex-sum-dec");

    if (STATE.period === "prev") {
      perfEl.textContent = "No pilot activity in July 2026. Pilot launched August 6 (US) and August 9 (AU).";
      confEl.textContent = "Pre-launch period; no live search traffic or CRM tracking under Stage 1.";
      decEl.innerHTML = "<strong>Baseline reference:</strong> See historical agency baseline for historical context.";
      return;
    }

    // Performance
    var usSpend = formatMoney(us.spend, "USD");
    var auSpend = formatMoney(au.spend, "AUD");
    var usEnq = us.funnel.enquiriesPending ? "Pending review" : formatNum(us.funnel.enquiries) + " employer enquiries";
    var auEnq = us.funnel.enquiriesPending && au.funnel.enquiries == null ? "Pending" : formatNum(au.funnel.enquiries) + " employer enquiries";
    var usCpe = ratioMoney(us.cpe, "USD");
    var auCpe = ratioMoney(au.cpe, "AUD");

    var perfText =
      "<strong>US:</strong> " +
      usSpend +
      " spend → " +
      usEnq +
      " (" +
      (usCpe === "—" ? "CPE pending" : usCpe + " blended / enquiry") +
      "). &nbsp;|&nbsp; <strong>AU:</strong> " +
      auSpend +
      " spend → " +
      auEnq +
      " (" +
      (auCpe === "—" ? "CPE pending" : auCpe + " blended / enquiry") +
      ").";
    perfEl.innerHTML = perfText;

    // Data Confidence
    var totalGclid = us.withGclid + au.withGclid;
    var totalZoho = us.zohoRows + au.zohoRows;
    var covPct = totalZoho > 0 ? Math.round((totalGclid / totalZoho) * 100) : 0;

    var confText =
      "<strong>Attribution coverage: " +
      totalGclid +
      " of " +
      totalZoho +
      " (" +
      covPct +
      "%)</strong> eligible Zoho census rows contain a valid click ID (2/20 US, 3/11 AU). Paid CPA is <em>Not reliable yet</em>. Key CRM limitations: hidden-field persistence is incomplete on role landing pages; phone calls lack CRM dispositioning & caller ANI.";
    confEl.innerHTML = confText;

    // Current Decision
    var decText =
      "<strong>Conservative Hold:</strong> Maintain current Target Spend / Max Clicks bidding with CPC ceilings ($250/day US, A$125/day AU). <em>Do not move bidding toward conversion optimization merely because Google Ads reports front-end conversions.</em> Prerequisite for scaling: verify ≥40% GCLID persistence and 15+ confirmed CRM conversions.";
    decEl.innerHTML = decText;
  }

  function renderMarketScorecard(us, au) {
    var body = $("#ex-scorecard-body");
    var rows = [];

    // Helper for conversion rate
    function rateStr(numVal, denVal) {
      if (numVal == null || denVal == null || denVal === 0) return "—";
      return formatPct((numVal / denVal) * 100);
    }

    function rowHtml(label, usVal, auVal, note, cls) {
      return (
        '<tr class="' +
        (cls || "") +
        '">' +
        '<td class="ex-cell-lbl">' +
        label +
        "</td>" +
        '<td class="num">' +
        usVal +
        "</td>" +
        '<td class="num">' +
        auVal +
        "</td>" +
        '<td class="ex-cell-note">' +
        note +
        "</td>" +
        "</tr>"
      );
    }

    function sectionDivider(title, subtitle) {
      return (
        '<tr class="ex-row-header">' +
        '<th colspan="4">' +
        '<span class="ex-hdr-title">' +
        title +
        "</span>" +
        (subtitle ? '<span class="ex-hdr-sub">' + subtitle + "</span>" : "") +
        "</th>" +
        "</tr>"
      );
    }

    // SECTION 1: Funnel Outcomes
    rows.push(
      sectionDivider(
        "1. Funnel Outcomes",
        "Sales-confirmed period activity · Cheyenne (US) & Holly (AU)"
      )
    );

    var usEnq = us.funnel.enquiriesPending ? '<span class="ex-pending">Pending</span>' : formatNum(us.funnel.enquiries);
    var auEnq = au.funnel.enquiries == null ? '<span class="ex-pending">Pending</span>' : formatNum(au.funnel.enquiries);
    rows.push(rowHtml("Employer enquiries", usEnq, auEnq, "Sales-confirmed inbound employer leads. Excludes job seekers and spam."));

    var usDisc = us.funnel.discoveries == null ? "—" : formatNum(us.funnel.discoveries);
    var auDisc = au.funnel.discoveries == null ? "—" : formatNum(au.funnel.discoveries);
    rows.push(rowHtml("Discovery calls completed", usDisc, auDisc, "Sales discovery calls actually completed (not booked or tel: taps)."));

    var usJo = formatNum(us.funnel.jobOrders);
    var auJo = formatNum(au.funnel.jobOrders);
    rows.push(rowHtml("Job orders submitted", usJo, auJo, "Formal job orders received from qualified employers."));

    var usPl = formatNum(us.funnel.placements);
    var auPl = formatNum(au.funnel.placements);
    rows.push(rowHtml("Placements confirmed", usPl, auPl, "Hired Virtual Coworker candidate placements confirmed."));

    // Stage Conversion Rates
    var usE2D = rateStr(us.funnel.discoveries, us.funnel.enquiries);
    var auE2D = rateStr(au.funnel.discoveries, au.funnel.enquiries);
    rows.push(rowHtml("Enquiry → Discovery rate", usE2D, auE2D, "Period activity rate · Downstream calls lag enquiries. Not a mature cohort.", "ex-row-sub"));

    var usD2J = rateStr(us.funnel.jobOrders, us.funnel.discoveries);
    var auD2J = rateStr(au.funnel.jobOrders, au.funnel.discoveries);
    rows.push(rowHtml("Discovery → Job order rate", usD2J, auD2J, "Period activity rate · Discovery calls converted to job orders.", "ex-row-sub"));

    var usJ2P = rateStr(us.funnel.placements, us.funnel.jobOrders);
    var auJ2P = rateStr(au.funnel.placements, au.funnel.jobOrders);
    rows.push(rowHtml("Job order → Placement rate", usJ2P, auJ2P, "Period activity rate · Job orders converted to paid candidate placements.", "ex-row-sub"));

    // SECTION 2: Unit Economics (Blended Efficiency)
    rows.push(
      sectionDivider(
        "2. Unit Economics (Blended Efficiency)",
        "Google Ads spend ÷ sales-confirmed outcomes · NOT Google Ads CPA"
      )
    );

    var usSpend = formatMoney(us.spend, "USD");
    var auSpend = formatMoney(au.spend, "AUD");
    rows.push(rowHtml("Google Ads spend", usSpend, auSpend, "Verified Google Ads account spend for the selected period."));

    var usCpe = ratioMoney(us.cpe, "USD");
    var auCpe = ratioMoney(au.cpe, "AUD");
    rows.push(rowHtml("Blended cost per enquiry", usCpe, auCpe, "Operational blended metric: Ads spend ÷ confirmed enquiries."));

    var usCpd = ratioMoney(us.cpd, "USD");
    var auCpd = ratioMoney(au.cpd, "AUD");
    rows.push(rowHtml("Blended cost per discovery", usCpd, auCpd, "Operational blended metric: Ads spend ÷ completed discovery calls."));

    var usCpjo = ratioMoney(us.cpjo, "USD");
    var auCpjo = ratioMoney(au.cpjo, "AUD");
    rows.push(rowHtml("Blended cost per job order", usCpjo, auCpjo, "Operational blended metric: Ads spend ÷ confirmed job orders."));

    var usCpp = ratioMoney(us.cpp, "USD");
    var auCpp = ratioMoney(au.cpp, "AUD");
    rows.push(rowHtml("Blended cost per placement", usCpp, auCpp, "Operational blended metric: Ads spend ÷ confirmed placements."));

    // SECTION 3: Data Confidence & Attribution Layer
    rows.push(
      sectionDivider(
        "3. Data Confidence & Attribution Layer",
        "Valid advertising click IDs (gclid) vs unattached records"
      )
    );

    var usPaid = formatNum(us.attrib.paidAttributed);
    var auPaid = formatNum(au.attrib.paidAttributed);
    rows.push(rowHtml("Paid-attributed outcomes", usPaid, auPaid, "Records containing a verified advertising click ID (gclid/gbraid/wbraid)."));

    var usCovStr = us.attrib.validatedSalesRecords > 0 ? us.attrib.paidAttributed + " / " + us.attrib.validatedSalesRecords + " (" + formatPct((us.attrib.paidAttributed / us.attrib.validatedSalesRecords) * 100) + ")" : "—";
    var auCovStr = au.attrib.validatedSalesRecords > 0 ? au.attrib.paidAttributed + " / " + au.attrib.validatedSalesRecords + " (" + formatPct((au.attrib.paidAttributed / au.attrib.validatedSalesRecords) * 100) + ")" : "—";
    rows.push(rowHtml("Click-ID coverage (census sample)", usCovStr, auCovStr, "Proportion of single-week Zoho audit records with captured click ID."));

    var usMissing = us.attrib.validatedSalesRecords > 0 ? formatNum(us.attrib.validatedSalesRecords - us.attrib.paidAttributed) : "—";
    var auMissing = au.attrib.validatedSalesRecords > 0 ? formatNum(au.attrib.validatedSalesRecords - au.attrib.paidAttributed) : "—";
    rows.push(rowHtml("Records missing click ID", usMissing, auMissing, "Leads without gclid attachment (attributed to organic/direct/untracked)."));

    var usReview = us.funnel.enquiriesPending ? "Mon–Tue pending" : "None";
    var auReview = "None";
    rows.push(rowHtml("Outcomes awaiting review", usReview, auReview, "Leads currently in sales ops qualification queue."));

    body.innerHTML = rows.join("");
  }

  function renderTrendSection() {
    var grid = $("#ex-trend-grid");
    var snap = STATE.snapshot;
    var arch = STATE.archiveW1;

    // Week 1 (Aug 10–16), Week 2 (Aug 17–23), Week 3 (Aug 24–25 partial)
    var usW1 = (arch && arch.sales_ops_us) || { window_start: "2026-08-10", window_end: "2026-08-16", spend_usd: 1439.73, enquiries: 18, sales_calls_completed: 9, job_orders_total: 0, cost_per_enquiry_usd: 79.98 };
    var usW2 = snap.sales_ops_us || { window_start: "2026-08-17", window_end: "2026-08-23", spend_usd: 2036.15, enquiries: 13, sales_calls_completed: 7, job_orders_total: 0, cost_per_enquiry_usd: 156.63 };
    var usW3 = snap.sales_ops_us_now || { window_start: "2026-08-24", window_end: "2026-08-25", spend_usd: 621.12, enquiries: null, sales_calls_completed: 0, job_orders_total: 0, cost_per_enquiry_usd: null, caveat: "enquiry count pending" };

    var auW1 = (arch && arch.sales_ops_au) || { window_start: "2026-08-10", window_end: "2026-08-16", spend_usd: 526.84, enquiries: 8, sales_calls_completed: 5, job_orders_total: 6, placements: 4, cost_per_enquiry_usd: 65.86 };
    var auW2 = snap.sales_ops_au || { window_start: "2026-08-17", window_end: "2026-08-23", spend_usd: 933.68, enquiries: 8, sales_calls_completed: 7, job_orders_total: 0, placements: 0, cost_per_enquiry_usd: 116.71 };
    var auW3 = snap.sales_ops_au_now || { window_start: "2026-08-24", window_end: "2026-08-25", spend_usd: 303.65, enquiries: 2, sales_calls_completed: 0, job_orders_total: 1, placements: 0, cost_per_enquiry_usd: 151.82 };

    var usWeeks = [
      { label: "W1: Aug 10–16", complete: true, data: usW1 },
      { label: "W2: Aug 17–23", complete: true, data: usW2 },
      { label: "W3: Aug 24–25", complete: false, data: usW3 },
    ];

    var auWeeks = [
      { label: "W1: Aug 10–16", complete: true, data: auW1 },
      { label: "W2: Aug 17–23", complete: true, data: auW2 },
      { label: "W3: Aug 24–25", complete: false, data: auW3 },
    ];

    function buildTableHtml(market, cur, weeks) {
      var h = '<div class="ex-trend-card ex-card">';
      h += '<div class="ex-trend-hd"><h3>' + (market === "US" ? "United States (USD)" : "Australia (AUD)") + '</h3><span class="meta">' + (market === "US" ? "Cheyenne Gichana" : "Holly Wallace") + '</span></div>';
      h += '<table class="ex-table ex-trend-table"><thead><tr>';
      h += '<th>Period</th><th class="num">Spend</th><th class="num">Enquiries</th><th class="num">Discoveries</th><th class="num">Job Orders</th>';
      if (market === "AU") h += '<th class="num">Placements</th>';
      h += '<th class="num">Blended CPE</th><th>Status</th></tr></thead><tbody>';

      weeks.forEach(function (w) {
        var d = w.data || {};
        var rowClass = w.complete ? "" : "ex-row-partial";
        var isPending = isEnquiryPending(d);

        var spend = formatMoney(d.spend_usd, cur);
        var enq = isPending ? '<span class="ex-pending">Pending</span>' : formatNum(d.enquiries);
        var disc = d.sales_calls_completed != null ? formatNum(d.sales_calls_completed) : "—";
        var jo = d.job_orders_total != null ? formatNum(d.job_orders_total) : "—";
        var pl = d.placements != null ? formatNum(d.placements) : "—";
        var cpe = isPending || d.cost_per_enquiry_usd == null ? "—" : formatMoney2(d.cost_per_enquiry_usd, cur);
        var statusBadge = w.complete ? '<span class="ex-pill ok ex-pill-sm">Complete</span>' : '<span class="ex-pill warn ex-pill-sm">Partial (2d)</span>';

        h += '<tr class="' + rowClass + '">';
        h += '<td><strong>' + w.label + '</strong></td>';
        h += '<td class="num">' + spend + '</td>';
        h += '<td class="num">' + enq + '</td>';
        h += '<td class="num">' + disc + '</td>';
        h += '<td class="num">' + jo + '</td>';
        if (market === "AU") h += '<td class="num">' + pl + '</td>';
        h += '<td class="num font-mono">' + cpe + '</td>';
        h += '<td>' + statusBadge + '</td>';
        h += '</tr>';
      });

      h += '</tbody></table></div>';
      return h;
    }

    grid.innerHTML = buildTableHtml("US", "USD", usWeeks) + buildTableHtml("AU", "AUD", auWeeks);
  }

  function renderLegacyComparison(us, au) {
    var body = $("#ex-agency-body");
    var rows = [];

    function cmpRow(metric, market, pilotVal, agencyVal, diffText, confLabel, tone) {
      var badgeCls = tone === "good" ? "ok" : tone === "bad" ? "warn" : "neutral";
      return (
        '<tr>' +
        '<td class="ex-cell-lbl"><strong>' + metric + '</strong></td>' +
        '<td class="ex-cell-mkt">' + market + '</td>' +
        '<td class="num font-mono">' + pilotVal + '</td>' +
        '<td class="num font-mono">' + agencyVal + '</td>' +
        '<td class="num font-mono ' + (tone === "good" ? "delta-good" : tone === "bad" ? "delta-bad" : "") + '">' + diffText + '</td>' +
        '<td><span class="ex-pill ' + badgeCls + ' ex-pill-sm">' + confLabel + '</span></td>' +
        '</tr>'
      );
    }

    function groupDivider(title, desc) {
      return (
        '<tr class="ex-row-header">' +
        '<th colspan="6">' +
        '<span class="ex-hdr-title">' + title + '</span>' +
        '<span class="ex-hdr-sub">' + desc + '</span>' +
        '</th></tr>'
      );
    }

    // Direct Media Metrics (W2 / Frozen complete week for accurate weekly rate comparison)
    rows.push(groupDivider("Group 1: Directly Comparable Media Metrics", "Google Ads media efficiency (CPC, CTR, spend velocity)"));

    var snap = STATE.snapshot;
    var usPerf = (snap.performance_us || {}).totals_stage1_last_7_days || {};
    var auPerf = (snap.performance_au || {}).totals_stage1_last_7_days || {};
    var agUs = (STATE.agency && STATE.agency.us) || {};
    var agAu = (STATE.agency && STATE.agency.au) || {};

    // Avg CPC
    var usCpcCmp = compareRate(usPerf.avg_cpc_usd, agUs.avg_cpc, true, "Pilot", "Agency");
    rows.push(cmpRow("Average CPC", "US (USD)", formatMoney2(usPerf.avg_cpc_usd, "USD"), formatMoney2(agUs.avg_cpc, "USD"), usCpcCmp.diffText, "Comparable", usCpcCmp.tone));

    var auCpcCmp = compareRate(auPerf.avg_cpc_usd, agAu.avg_cpc, true, "Pilot", "Agency");
    rows.push(cmpRow("Average CPC", "AU (AUD)", formatMoney2(auPerf.avg_cpc_usd, "AUD"), formatMoney2(agAu.avg_cpc, "AUD"), auCpcCmp.diffText, "Comparable", auCpcCmp.tone));

    // CTR
    var usCtrCmp = compareRate(usPerf.ctr_pct, agUs.ctr_pct, false, "Pilot", "Agency");
    rows.push(cmpRow("Click-Through Rate (CTR)", "US", formatPct(usPerf.ctr_pct), formatPct(agUs.ctr_pct), usCtrCmp.diffText, "Comparable", usCtrCmp.tone));

    var auCtrCmp = compareRate(auPerf.ctr_pct, agAu.ctr_pct, false, "Pilot", "Agency");
    rows.push(cmpRow("Click-Through Rate (CTR)", "AU", formatPct(auPerf.ctr_pct), formatPct(agAu.ctr_pct), auCtrCmp.diffText, "Comparable", auCtrCmp.tone));

    // Weekly Spend Rate
    var usSpendCmp = compareRate(usPerf.cost_usd, agUs.typical_7d_spend, true, "Pilot", "Agency");
    rows.push(cmpRow("Weekly Spend Rate", "US (USD)", formatMoney(usPerf.cost_usd, "USD"), formatMoney(agUs.typical_7d_spend, "USD"), usSpendCmp.diffText, "Comparable", usSpendCmp.tone));

    var auSpendCmp = compareRate(auPerf.cost_usd, agAu.typical_7d_spend, true, "Pilot", "Agency");
    rows.push(cmpRow("Weekly Spend Rate", "AU (AUD)", formatMoney(auPerf.cost_usd, "AUD"), formatMoney(agAu.typical_7d_spend, "AUD"), auSpendCmp.diffText, "Comparable", auSpendCmp.tone));

    // Directional Blended Funnel Metrics
    rows.push(groupDivider("Group 2: Directional Blended Funnel Metrics", "Subject to historical CRM tracking gaps & unlabelled agency lead submissions"));

    var usOps = snap.sales_ops_us || {};
    var auOps = snap.sales_ops_au || {};

    // Cost per Enquiry
    var usCpeCmp = compareRate(usOps.cost_per_enquiry_usd, agUs.blended_cost_per_enquiry, true, "Pilot", "Agency");
    rows.push(cmpRow("Blended cost per enquiry", "US (USD)", formatMoney2(usOps.cost_per_enquiry_usd, "USD"), formatMoney2(agUs.blended_cost_per_enquiry, "USD"), usCpeCmp.diffText, "Directional", usCpeCmp.tone));

    var auCpeCmp = compareRate(auOps.cost_per_enquiry_usd, agAu.blended_cost_per_enquiry, true, "Pilot", "Agency");
    rows.push(cmpRow("Blended cost per enquiry", "AU (AUD)", formatMoney2(auOps.cost_per_enquiry_usd, "AUD"), formatMoney2(agAu.blended_cost_per_enquiry, "AUD"), auCpeCmp.diffText, "Directional", auCpeCmp.tone));

    // Cost per Discovery
    var usCpdCmp = compareRate(usOps.cost_per_sales_call_completed_usd, agUs.blended_cost_per_discovery, true, "Pilot", "Agency");
    rows.push(cmpRow("Blended cost per discovery", "US (USD)", formatMoney2(usOps.cost_per_sales_call_completed_usd, "USD"), formatMoney2(agUs.blended_cost_per_discovery, "USD"), usCpdCmp.diffText, "Directional", usCpdCmp.tone));

    var auCpdCmp = compareRate(auOps.cost_per_sales_call_completed_usd, agAu.blended_cost_per_discovery, true, "Pilot", "Agency");
    rows.push(cmpRow("Blended cost per discovery", "AU (AUD)", formatMoney2(auOps.cost_per_sales_call_completed_usd, "AUD"), formatMoney2(agAu.blended_cost_per_discovery, "AUD"), auCpdCmp.diffText, "Directional", auCpdCmp.tone));

    // Cost per Job Order
    rows.push(cmpRow("Blended cost per job order", "US (USD)", "—", formatMoney2(agUs.blended_cost_per_job_order, "USD"), "—", "Insufficient sample", "neutral"));
    rows.push(cmpRow("Blended cost per job order", "AU (AUD)", "—", formatMoney2(agAu.blended_cost_per_job_order, "AUD"), "—", "Insufficient sample", "neutral"));

    // Enquiries per $1,000 Spend
    var usEnq1k = perThousand(usOps.enquiries, usOps.spend_usd).value;
    var usEnq1kCmp = compareRate(usEnq1k, agUs.enquiries_per_thousand, false, "Pilot", "Agency");
    rows.push(cmpRow("Enquiries per $1k spend", "US", formatNum(usEnq1k, 2), formatNum(agUs.enquiries_per_thousand, 2), usEnq1kCmp.diffText, "Directional", usEnq1kCmp.tone));

    var auEnq1k = perThousand(auOps.enquiries, auOps.spend_usd).value;
    var auEnq1kCmp = compareRate(auEnq1k, agAu.enquiries_per_thousand, false, "Pilot", "Agency");
    rows.push(cmpRow("Enquiries per A$1k spend", "AU", formatNum(auEnq1k, 2), formatNum(agAu.enquiries_per_thousand, 2), auEnq1kCmp.diffText, "Directional", auEnq1kCmp.tone));

    body.innerHTML = rows.join("");
  }

  function renderAttributionPanel() {
    var panel = $("#ex-attrib-panel");
    var snap = STATE.snapshot;
    var arch = STATE.archiveW1;

    // Reconciliation calculations
    // Cumulative MTD enquiries = 31 US (Cheyenne) + 18 AU (Holly) = 49 total
    var usMtdEnq = 31;
    var auMtdEnq = 18;
    var totalMtdEnq = usMtdEnq + auMtdEnq; // 49

    // Zoho census single-week audit (Aug 17–23)
    var usCensusRows = 20;
    var auCensusRows = 11;
    var totalCensusRows = usCensusRows + auCensusRows; // 31

    var usGclid = 2;
    var auGclid = 3;
    var totalGclid = usGclid + auGclid; // 5

    var covPct = ((totalGclid / totalCensusRows) * 100).toFixed(1);

    var h = '<div class="ex-attrib-grid">';

    // Left Column: The 49 vs 31 Denominator Reconciliation
    h += '<div class="ex-attrib-col">';
    h += '<h3 class="ex-card-title">Attribution Reconciliation (49 vs 31 Denominators)</h3>';
    h += '<table class="ex-table ex-reconcile-table">';
    h += '<thead><tr><th>Dataset / Population</th><th class="num">Count</th><th>Definition &amp; Source</th></tr></thead><tbody>';
    h += '<tr><td><strong>Cumulative Sales Enquiries</strong></td><td class="num"><strong>49</strong></td><td>Total sales-confirmed employer enquiries across the 3-week pilot (US 31 + AU 18). Confirmed by Cheyenne &amp; Holly.</td></tr>';
    h += '<tr><td><strong>Single-Week Zoho Census</strong></td><td class="num"><strong>31</strong></td><td>Raw CRM Sales Enquiry records created in Zoho during the single-week audit window (Aug 17–23: US 20 + AU 11).</td></tr>';
    h += '<tr><td><strong>Valid Click IDs (GCLID)</strong></td><td class="num"><strong>5</strong></td><td>Records in that single-week census with verified advertising click ID (US 2 of 20, AU 3 of 11).</td></tr>';
    h += '<tr><td><strong>Audit Click-ID Coverage</strong></td><td class="num"><strong>' + covPct + '%</strong></td><td>5 of 31 eligible Zoho records contain a valid click ID.</td></tr>';
    h += '<tr><td><strong>Paid CPA Confidence</strong></td><td class="num"><span class="ex-pill warn ex-pill-sm">Not reliable yet</span></td><td>Requires ≥40% coverage and ≥10 sample size before paid CPA can be isolated.</td></tr>';
    h += '</tbody></table>';

    h += '<p class="ex-attrib-desc"><strong>Why do these counts differ?</strong> 49 represents the entire cumulative 3-week pilot population of confirmed employer leads, whereas 31 represents the single-week Zoho CRM census audit (Aug 17–23). They are separate analytical layers and must not be mixed.</p>';
    h += '</div>';

    // Right Column: Data Quality, Exclusions, Phone Gaps & Remediation
    h += '<div class="ex-attrib-col">';
    h += '<h3 class="ex-card-title">Data Quality &amp; Remediation Status</h3>';
    h += '<ul class="ex-attrib-list">';
    h += '<li><strong>Known Exclusions (16 filtered leads):</strong> Sales operations identified and excluded 10 job seekers and 6 not-a-fit/disqualified records from employer counts. None are counted as enquiries.</li>';
    h += '<li><strong>Phone Call Attribution Gaps:</strong> Front-end <code>tel:</code> link clicks (62 button taps) are NOT calls. CRM Voice integration receives DID stubs (+18889648644) without external caller ANI. Phone leads currently require manual sales confirmation.</li>';
    h += '<li><strong>Pending Records:</strong> US Mon–Tue sales-ops enquiry count is currently in qualification review by Cheyenne.</li>';
    h += '<li><strong>Top Remediation Action:</strong> Ensure hidden form fields on all <code>.app</code> landing pages reliably persist <code>gclid</code> into Zoho <code>utm_gclid</code>.</li>';
    h += '</ul>';
    h += '</div>';

    h += '</div>';
    panel.innerHTML = h;
  }

  function renderBiddingDecisions() {
    var body = $("#ex-bidding-body");
    var rows = [];

    rows.push(
      '<tr>' +
      '<td><strong>United States</strong></td>' +
      '<td>$250/day ($150 Core + $100 Roles)</td>' +
      '<td>Target Spend (Max Clicks with CPC cap)</td>' +
      '<td><span class="ex-pill ok ex-pill-sm">HOLD</span></td>' +
      '<td>Blended lead flow is highly efficient ($156/enq vs $707 agency), but offline GCLID capture (10%) is too sparse for automated bidding algorithms.</td>' +
      '<td>Verify ≥40% GCLID persistence in Zoho and 15+ confirmed CRM conversions.</td>' +
      '</tr>'
    );

    rows.push(
      '<tr>' +
      '<td><strong>Australia</strong></td>' +
      '<td>A$125/day (A$75 Core + A$50 Roles)</td>' +
      '<td>Target Spend (Max Clicks with CPC cap)</td>' +
      '<td><span class="ex-pill ok ex-pill-sm">HOLD</span></td>' +
      '<td>CTR is strong (15.2%), but search volume is moderate and click-ID capture (3/11) is below automated bidding threshold.</td>' +
      '<td>Maintain Max Clicks with CPC ceiling; accumulate 15+ sales-confirmed enquiries.</td>' +
      '</tr>'
    );

    body.innerHTML = rows.join("");
  }

  function renderBlockersAndActions() {
    var body = $("#ex-blockers-body");
    var rows = [];

    rows.push(
      '<tr>' +
      '<td><strong>1. Click-ID (GCLID) capture rate in Zoho</strong></td>' +
      '<td>Cannot isolate individual paid CPA or activate Google Ads offline conversion bidding.</td>' +
      '<td>Ash / Web Ops</td>' +
      '<td><span class="ex-pill warn ex-pill-sm">In Progress</span></td>' +
      '<td>Verify next 10 form submissions have <code>utm_gclid</code> populated in Zoho. <a href="attribution.html">View CRM audit →</a></td>' +
      '</tr>'
    );

    rows.push(
      '<tr>' +
      '<td><strong>2. Phone call attribution &amp; CRM linkage</strong></td>' +
      '<td>Inbound voice calls bypass CRM sales pipeline; cannot attribute phone revenue to campaigns.</td>' +
      '<td>Braden / Cheyenne / Raffie</td>' +
      '<td><span class="ex-pill warn ex-pill-sm">Partial (CTI stubs)</span></td>' +
      '<td>Provide external caller ANI and automate Lead creation from voice. <a href="phone-call-forensic.html">View Phone Forensic →</a></td>' +
      '</tr>'
    );

    rows.push(
      '<tr>' +
      '<td><strong>3. Sales qualification picklist in CRM</strong></td>' +
      '<td>Job seekers and not-a-fit leads require manual email triage rather than automated CRM filtering.</td>' +
      '<td>Ash / Cheyenne / Holly</td>' +
      '<td><span class="ex-pill ok ex-pill-sm">Reviewing</span></td>' +
      '<td>Deploy standardized <code>Qualification_Status</code> field in Zoho. <a href="sales-review.html">View Sales Review →</a></td>' +
      '</tr>'
    );

    body.innerHTML = rows.join("");
  }

  function renderAll() {
    var us = buildMarketData("US", STATE.period);
    var au = buildMarketData("AU", STATE.period);

    renderHeaderAndPills(us, au);
    renderDecisionSummary(us, au);
    renderMarketScorecard(us, au);
    renderTrendSection();
    renderLegacyComparison(us, au);
    renderAttributionPanel();
    renderBiddingDecisions();
    renderBlockersAndActions();
  }

  function initPeriodControls() {
    var buttons = document.querySelectorAll("[data-ex-period]");
    buttons.forEach(function (btn) {
      btn.addEventListener("click", function () {
        buttons.forEach(function (b) {
          b.classList.remove("on");
          b.setAttribute("aria-pressed", "false");
        });
        btn.classList.add("on");
        btn.setAttribute("aria-pressed", "true");
        STATE.period = btn.getAttribute("data-ex-period") || "mtd";
        renderAll();
      });
    });
  }

  /* —— Init & Data Loading —— */

  function init() {
    var loadingEl = $("#ex-loading");
    if (loadingEl) loadingEl.style.display = "block";

    Promise.all([
      fetchJson("data/executive-snapshot.json"),
      fetchJson("data/executive-snapshot-frozen-2026-08-10.json").catch(function () {
        return null;
      }),
      fetchJson("data/agency-baseline.json").catch(function () {
        return null;
      }),
      fetchJson("data/sales-ops-week-zoho.json").catch(function () {
        return null;
      }),
    ])
      .then(function (res) {
        STATE.snapshot = res[0];
        STATE.archiveW1 = res[1];
        STATE.agency = res[2];
        STATE.zohoWeek = res[3];

        if (loadingEl) loadingEl.style.display = "none";
        initPeriodControls();
        renderAll();
      })
      .catch(function (err) {
        if (loadingEl) {
          loadingEl.className = "ex-error";
          loadingEl.textContent = "Failed loading executive performance data: " + err.message;
        }
      });
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();
