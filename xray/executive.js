/**
 * Executive Performance — Simplified Leadership Dashboard Renderer.
 *
 * Rules:
 * 1. Blended cost per enquiry = Google Ads spend ÷ sales-confirmed employer enquiries.
 * 2. Paid attribution requires verified advertising click ID (GCLID).
 * 3. US Job Orders & Placements: If unconfirmed or absent from sales email, display
 *    "None confirmed yet" rather than an ambiguous 0.
 * 4. Human-first leadership copy: Results, Tracking, What we're doing.
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

  /* —— Math & Formatting Helpers —— */

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

  function sumSalesLabeled(slices, start, end, market) {
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
      jobOrders: jobOrders, // null if not explicitly reported
      placements: placements,
      enquiriesPending: anyPending && enquiries == null,
      source: anyPending && enquiries == null ? "Pending" : "Sales labeled",
    };
  }

  function compareRate(pilot, agency, lowerIsBetter) {
    if (pilot == null || agency == null || agency === 0) {
      return { diffText: "—", tone: "neutral" };
    }
    var diffPct = ((pilot - agency) / Math.abs(agency)) * 100;
    var improved = lowerIsBetter ? pilot < agency : pilot > agency;
    var sign = diffPct > 0 ? "+" : "";
    return {
      diffText: sign + diffPct.toFixed(1) + "%",
      tone: improved ? "good" : "bad",
    };
  }

  /* —— Data Assembly —— */

  function buildMarketData(market, periodKey) {
    var cur = currencyForMarket(market);
    var perf = market === "US" ? STATE.snapshot.performance_us : STATE.snapshot.performance_au;
    var by = (perf || {}).by_date_stage1 || (perf || {}).by_date || {};
    var snap = STATE.snapshot;
    var arch = STATE.archiveW1;

    var w1 = market === "US" ? (arch && arch.sales_ops_us) : (arch && arch.sales_ops_au);
    var w2 = market === "US" ? snap.sales_ops_us : snap.sales_ops_au;
    var w3 = market === "US" ? snap.sales_ops_us_now : snap.sales_ops_au_now;

    var bounds = { start: "", end: "", label: "", partial: false };
    var funnel = null;
    var ads = null;

    if (periodKey === "mtd") {
      bounds.start = "2026-08-01";
      bounds.end = asOfDate();
      bounds.label = "August 2026 to date";
      bounds.partial = true;

      funnel = sumSalesLabeled([w1, w2, w3], bounds.start, bounds.end, market);
      ads = sumAdsByDate(by, bounds.start, bounds.end, cur);
    } else if (periodKey === "prev") {
      bounds.start = "2026-07-01";
      bounds.end = "2026-07-31";
      bounds.label = "July 2026 (Pre-pilot)";
      bounds.partial = false;
      funnel = { enquiries: null, discoveries: null, jobOrders: null, placements: null, enquiriesPending: false, source: "None" };
      ads = null;
    } else if (periodKey === "week") {
      var ops = w2 || {};
      bounds.start = ops.window_start || "2026-08-17";
      bounds.end = ops.window_end || "2026-08-23";
      bounds.label = ops.label || "Mon Aug 17 – Sun Aug 23";
      bounds.partial = false;

      funnel = sumSalesLabeled([ops], bounds.start, bounds.end, market);
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
      var opsNow = w3 || {};
      bounds.start = opsNow.window_start || "2026-08-24";
      bounds.end = opsNow.window_end || "2026-08-25";
      bounds.label = opsNow.label || "Mon Aug 24 – Tue Aug 25";
      bounds.partial = true;

      funnel = sumSalesLabeled([opsNow], bounds.start, bounds.end, market);
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

    var census =
      market === "US"
        ? ((snap.sales_ops_us || {}).zoho_census || {})
        : ((snap.sales_ops_au || {}).zoho_census || {});
    var zohoRows = market === "US" ? Number(census.usa_sales_enquiries || 0) : Number(census.au_sales_enquiries || 0);
    var withGclid = market === "US" ? Number(census.usa_with_gclid || 0) : Number(census.au_with_gclid || 0);

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
      census: census,
      zohoRows: zohoRows,
      withGclid: withGclid,
      agency: agencyBlock,
    };
  }

  /* —— Render Functions —— */

  function renderHeader(us) {
    $("#ex-period").textContent = us.bounds.label + (us.bounds.partial ? " (Partial month)" : "");
    var snap = STATE.snapshot;
    var adsDate = (snap.generated_at_utc || "").slice(0, 10);
    $("#ex-fresh").textContent =
      "Data through " + asOfDate() + " · Google Ads: " + adsDate + " · Sales confirmed by Cheyenne (US) & Holly (AU)";
  }

  function renderBottomLine(us, au) {
    var perfEl = $("#ex-sum-perf");
    var confEl = $("#ex-sum-conf");
    var decEl = $("#ex-sum-dec");

    if (STATE.period === "prev") {
      perfEl.innerHTML = "<p>Search pilot had not yet launched in July 2026. Pre-pilot historical baseline only.</p>";
      confEl.innerHTML = "<p>No Stage 1 ad traffic or tracking live during this period.</p>";
      decEl.innerHTML = "<p>Review recorded legacy agency baseline for historical context.</p>";
      return;
    }

    // Results briefing
    var usSpend = formatMoney(us.spend, "USD");
    var auSpend = formatMoney(au.spend, "AUD");

    var usEnq = us.funnel.enquiriesPending ? "Pending review" : formatNum(us.funnel.enquiries) + " employer enquiries";
    var usDisc = us.funnel.discoveries == null ? "—" : formatNum(us.funnel.discoveries) + " discovery calls";
    var auEnq = formatNum(au.funnel.enquiries) + " enquiries";
    var auDisc = formatNum(au.funnel.discoveries) + " discovery calls";
    var auJo = (au.funnel.jobOrders == null ? "0" : formatNum(au.funnel.jobOrders)) + " job orders";
    var auPl = (au.funnel.placements == null ? "0" : formatNum(au.funnel.placements)) + " placements";

    perfEl.innerHTML =
      '<div class="ex-briefing-p"><strong>United States:</strong> ' + usSpend + ' ad spend produced ' + usEnq + ' and ' + usDisc + '. Job orders and placements await confirmation.</div>' +
      '<div class="ex-briefing-p"><strong>Australia:</strong> ' + auSpend + ' ad spend produced ' + auEnq + ', ' + auDisc + ', ' + auJo + ', and ' + auPl + '.</div>';

    // Tracking briefing
    var totalGclid = us.withGclid + au.withGclid;
    var totalZoho = us.zohoRows + au.zohoRows;
    confEl.innerHTML =
      '<div class="ex-briefing-p"><strong>Blended attribution:</strong> Google Ads is the company’s primary marketing spend, but not every lead is directly tied to an ad click yet (' + totalGclid + ' of ' + totalZoho + ' audited CRM records carry verified click IDs). We evaluate total blended results as directional commercial intelligence while tracking is refined.</div>';

    // What we're doing
    decEl.innerHTML =
      '<div class="ex-briefing-p">Hold budgets and bidding steady while Cheyenne confirms US downstream pipeline status and tech maps website click IDs directly to Zoho CRM.</div>';
  }

  function renderUSNotice(us) {
    var alertEl = $("#ex-us-alert");
    if (!alertEl) return;

    if (STATE.period === "prev") {
      alertEl.style.display = "none";
      return;
    }

    var hasEnquiries = (us.funnel.enquiries || 0) > 0;
    var hasDiscoveries = (us.funnel.discoveries || 0) > 0;
    var noJobOrders = us.funnel.jobOrders == null || us.funnel.jobOrders === 0;

    if (hasEnquiries && hasDiscoveries && noJobOrders) {
      alertEl.className = "ex-pipeline-notice warn";
      alertEl.innerHTML =
        "<strong>US pipeline watch:</strong> Enquiries (31) and completed discovery calls (16) are occurring, but no job orders have been confirmed yet in weekly sales updates. Discovery call follow-up and Zoho CRM status need review.";
      alertEl.style.display = "block";
    } else {
      alertEl.style.display = "none";
    }
  }

  function renderMainScorecard(us, au) {
    var body = $("#ex-scorecard-body");
    var rows = [];

    function marketDivider(title) {
      return (
        '<tr class="ex-row-header">' +
        '<th colspan="4"><span class="ex-hdr-title">' + title + '</span></th>' +
        '</tr>'
      );
    }

    function dataRow(metric, volume, costPerOutcome, statusHtml) {
      return (
        '<tr>' +
        '<td>' + metric + '</td>' +
        '<td class="num font-mono">' + volume + '</td>' +
        '<td class="num font-mono">' + costPerOutcome + '</td>' +
        '<td class="ex-cell-note">' + statusHtml + '</td>' +
        '</tr>'
      );
    }

    // United States Section
    rows.push(marketDivider("United States (USD)"));
    rows.push(dataRow("Paid ad spend", formatMoney(us.spend, "USD"), "—", "Google Ads Search pilot (Core + Roles)"));
    
    var usEnq = us.funnel.enquiriesPending ? '<span class="ex-status-tag pending">Pending</span>' : formatNum(us.funnel.enquiries);
    rows.push(dataRow("Employer enquiries", usEnq, ratioMoney(us.cpe, "USD"), "Validated employer leads (Cheyenne ops review)"));
    
    var usDisc = us.funnel.discoveries == null ? "—" : formatNum(us.funnel.discoveries);
    rows.push(dataRow("Completed discovery calls", usDisc, ratioMoney(us.cpd, "USD"), "Sales calls completed by US team"));
    
    var usJo = us.funnel.jobOrders && us.funnel.jobOrders > 0 ? formatNum(us.funnel.jobOrders) : '<span class="ex-status-tag warn">None confirmed yet</span>';
    var usCpjo = us.funnel.jobOrders && us.funnel.jobOrders > 0 ? ratioMoney(us.cpjo, "USD") : "—";
    rows.push(dataRow("Confirmed job orders", usJo, usCpjo, "Awaiting sales validation from discovery cohort"));
    
    var usPl = us.funnel.placements && us.funnel.placements > 0 ? formatNum(us.funnel.placements) : '<span class="ex-status-tag warn">None confirmed yet</span>';
    var usCpp = us.funnel.placements && us.funnel.placements > 0 ? ratioMoney(us.cpp, "USD") : "—";
    rows.push(dataRow("Confirmed placements", usPl, usCpp, "Candidate hiring & placement in progress"));

    // Australia Section
    rows.push(marketDivider("Australia (AUD)"));
    rows.push(dataRow("Paid ad spend", formatMoney(au.spend, "AUD"), "—", "Google Ads Search pilot (Core + Roles)"));
    
    var auEnq = au.funnel.enquiries == null ? '<span class="ex-status-tag pending">Pending</span>' : formatNum(au.funnel.enquiries);
    rows.push(dataRow("Employer enquiries", auEnq, ratioMoney(au.cpe, "AUD"), "Validated employer leads (Holly ops review)"));
    
    var auDisc = au.funnel.discoveries == null ? "—" : formatNum(au.funnel.discoveries);
    rows.push(dataRow("Completed discovery calls", auDisc, ratioMoney(au.cpd, "AUD"), "Sales calls completed by AU team"));
    
    var auJo = au.funnel.jobOrders && au.funnel.jobOrders > 0 ? formatNum(au.funnel.jobOrders) : (au.funnel.jobOrders === 0 ? "0" : "—");
    var auCpjo = au.funnel.jobOrders && au.funnel.jobOrders > 0 ? ratioMoney(au.cpjo, "AUD") : "—";
    rows.push(dataRow("Confirmed job orders", auJo, auCpjo, "Signed client job requisitions"));
    
    var auPl = au.funnel.placements && au.funnel.placements > 0 ? formatNum(au.funnel.placements) : (au.funnel.placements === 0 ? "0" : "—");
    var auCpp = au.funnel.placements && au.funnel.placements > 0 ? ratioMoney(au.cpp, "AUD") : "—";
    rows.push(dataRow("Confirmed placements", auPl, auCpp, "Candidate hires active"));

    body.innerHTML = rows.join("");
  }

  function renderSimplifiedAgencyComparison(us, au) {
    var body = $("#ex-agency-body");
    var rows = [];

    var snap = STATE.snapshot;
    var usPerf = (snap.performance_us || {}).totals_stage1_last_7_days || {};
    var auPerf = (snap.performance_au || {}).totals_stage1_last_7_days || {};
    var usOps = snap.sales_ops_us || {};
    var auOps = snap.sales_ops_au || {};
    var agUs = (STATE.agency && STATE.agency.us) || {};
    var agAu = (STATE.agency && STATE.agency.au) || {};

    function cmpRow(metricName, pilotVal, agencyVal, diffObj) {
      var diffCls = diffObj.tone === "good" ? "delta-good" : diffObj.tone === "bad" ? "delta-bad" : "";
      return (
        '<tr>' +
        '<td>' + metricName + '</td>' +
        '<td class="num font-mono">' + pilotVal + '</td>' +
        '<td class="num font-mono">' + agencyVal + '</td>' +
        '<td class="num font-mono ' + diffCls + '">' + diffObj.diffText + '</td>' +
        '</tr>'
      );
    }

    function marketDivider(title) {
      return (
        '<tr class="ex-row-header">' +
        '<th colspan="4"><span class="ex-hdr-title">' + title + '</span></th>' +
        '</tr>'
      );
    }

    // United States Section
    rows.push(marketDivider("United States (USD)"));
    var agUsReportedCpa = (STATE.agency && STATE.agency.raw && STATE.agency.raw.us_totals && STATE.agency.raw.us_totals.reported_cpa) || agUs.blended_cost_per_enquiry;
    var usCpeDiff = compareRate(usOps.cost_per_enquiry_usd, agUsReportedCpa, true);
    rows.push(cmpRow("Cost per employer enquiry", formatMoney2(usOps.cost_per_enquiry_usd, "USD"), formatMoney2(agUsReportedCpa, "USD"), usCpeDiff));

    var usCpdDiff = compareRate(usOps.cost_per_sales_call_completed_usd, agUs.blended_cost_per_discovery, true);
    rows.push(cmpRow("Cost per discovery call", formatMoney2(usOps.cost_per_sales_call_completed_usd, "USD"), formatMoney2(agUs.blended_cost_per_discovery, "USD"), usCpdDiff));

    rows.push(cmpRow("Cost per job order", '<span class="ex-status-tag warn">None confirmed yet</span>', formatMoney2(agUs.blended_cost_per_job_order, "USD"), { diffText: "—", tone: "neutral" }));
    rows.push(cmpRow("Cost per placement", '<span class="ex-status-tag warn">None confirmed yet</span>', '<span style="color:#64748b;font-size:0.78rem">Not tracked in CRM</span>', { diffText: "—", tone: "neutral" }));

    var usCpcDiff = compareRate(usPerf.avg_cpc_usd, agUs.avg_cpc, true);
    rows.push(cmpRow("Average cost per click (CPC)", formatMoney2(usPerf.avg_cpc_usd, "USD"), formatMoney2(agUs.avg_cpc, "USD"), usCpcDiff));

    var usCtrDiff = compareRate(usPerf.ctr_pct, agUs.ctr_pct, false);
    rows.push(cmpRow("Click-through rate (CTR)", formatPct(usPerf.ctr_pct), formatPct(agUs.ctr_pct), usCtrDiff));

    // Australia Section
    rows.push(marketDivider("Australia (AUD)"));
    var agAuReportedCpa = (STATE.agency && STATE.agency.raw && STATE.agency.raw.au_totals && STATE.agency.raw.au_totals.reported_cpa) || agAu.blended_cost_per_enquiry;
    var auCpeDiff = compareRate(auOps.cost_per_enquiry_usd, agAuReportedCpa, true);
    rows.push(cmpRow("Cost per employer enquiry", formatMoney2(auOps.cost_per_enquiry_usd, "AUD"), formatMoney2(agAuReportedCpa, "AUD"), auCpeDiff));

    var auCpdDiff = compareRate(auOps.cost_per_sales_call_completed_usd, agAu.blended_cost_per_discovery, true);
    rows.push(cmpRow("Cost per discovery call", formatMoney2(auOps.cost_per_sales_call_completed_usd, "AUD"), formatMoney2(agAu.blended_cost_per_discovery, "AUD"), auCpdDiff));

    var auJoCost = au.funnel.jobOrders && au.funnel.jobOrders > 0 ? (au.spend / au.funnel.jobOrders) : null;
    var auCpjoDiff = compareRate(auJoCost, agAu.blended_cost_per_job_order, true);
    rows.push(cmpRow("Cost per job order", formatMoney2(auJoCost, "AUD"), formatMoney2(agAu.blended_cost_per_job_order, "AUD"), auCpjoDiff));

    var auPlaceCost = au.funnel.placements && au.funnel.placements > 0 ? (au.spend / au.funnel.placements) : null;
    rows.push(cmpRow("Cost per placement", formatMoney2(auPlaceCost, "AUD"), '<span style="color:#64748b;font-size:0.78rem">Not tracked in CRM</span>', { diffText: "—", tone: "neutral" }));

    var auCpcDiff = compareRate(auPerf.avg_cpc_usd, agAu.avg_cpc, true);
    rows.push(cmpRow("Average cost per click (CPC)", formatMoney2(auPerf.avg_cpc_usd, "AUD"), formatMoney2(agAu.avg_cpc, "AUD"), auCpcDiff));

    var auCtrDiff = compareRate(auPerf.ctr_pct, agAu.ctr_pct, false);
    rows.push(cmpRow("Click-through rate (CTR)", formatPct(auPerf.ctr_pct), formatPct(agAu.ctr_pct), auCtrDiff));

    body.innerHTML = rows.join("");
  }

  function renderDeepFunnel(us, au) {
    var container = $("#ex-deep-funnel");
    if (!container) return;

    function rateStr(numVal, denVal) {
      if (numVal == null || denVal == null || denVal === 0) return "—";
      return formatPct((numVal / denVal) * 100);
    }

    var h = '<table class="ex-table">';
    h += '<thead><tr><th>Metric</th><th class="num">United States (USD)</th><th class="num">Australia (AUD)</th><th>Notes</th></tr></thead><tbody>';

    h += '<tr><td>Enquiry → Discovery rate</td><td class="num">' + rateStr(us.funnel.discoveries, us.funnel.enquiries) + '</td><td class="num">' + rateStr(au.funnel.discoveries, au.funnel.enquiries) + '</td><td class="ex-cell-note">Period activity rate · Discovery calls lag enquiries.</td></tr>';
    h += '<tr><td>Discovery → Job order rate</td><td class="num">' + (us.funnel.jobOrders ? rateStr(us.funnel.jobOrders, us.funnel.discoveries) : "—") + '</td><td class="num">' + rateStr(au.funnel.jobOrders, au.funnel.discoveries) + '</td><td class="ex-cell-note">Discovery calls converted to signed job orders.</td></tr>';
    h += '<tr><td>Job order → Placement rate</td><td class="num">' + (us.funnel.placements ? rateStr(us.funnel.placements, us.funnel.jobOrders) : "—") + '</td><td class="num">' + rateStr(au.funnel.placements, au.funnel.jobOrders) + '</td><td class="ex-cell-note">Job orders converted to hired candidate placements.</td></tr>';
    h += '<tr><td>Cost per job order</td><td class="num">' + ratioMoney(us.cpjo, "USD") + '</td><td class="num">' + ratioMoney(au.cpjo, "AUD") + '</td><td class="ex-cell-note">Ad spend divided by confirmed job orders.</td></tr>';
    h += '<tr><td>Cost per placement</td><td class="num">' + ratioMoney(us.cpp, "USD") + '</td><td class="num">' + ratioMoney(au.cpp, "AUD") + '</td><td class="ex-cell-note">Ad spend divided by confirmed placements.</td></tr>';

    h += '</tbody></table>';
    container.innerHTML = h;
  }

  function renderWeeklyTrend() {
    var grid = $("#ex-trend-grid");
    if (!grid) return;

    var snap = STATE.snapshot;
    var arch = STATE.archiveW1;

    var usW1 = (arch && arch.sales_ops_us) || { window_start: "2026-08-10", window_end: "2026-08-16", spend_usd: 1439.73, enquiries: 18, sales_calls_completed: 9, job_orders_total: 0, cost_per_enquiry_usd: 79.98 };
    var usW2 = snap.sales_ops_us || { window_start: "2026-08-17", window_end: "2026-08-23", spend_usd: 2036.15, enquiries: 13, sales_calls_completed: 7, job_orders_total: 0, cost_per_enquiry_usd: 156.63 };
    var usW3 = snap.sales_ops_us_now || { window_start: "2026-08-24", window_end: "2026-08-25", spend_usd: 621.12, enquiries: null, sales_calls_completed: 0, job_orders_total: 0, cost_per_enquiry_usd: null, caveat: "enquiry count pending" };

    var auW1 = (arch && arch.sales_ops_au) || { window_start: "2026-08-10", window_end: "2026-08-16", spend_usd: 526.84, enquiries: 8, sales_calls_completed: 5, job_orders_total: 6, placements: 4, cost_per_enquiry_usd: 65.86 };
    var auW2 = snap.sales_ops_au || { window_start: "2026-08-17", window_end: "2026-08-23", spend_usd: 933.68, enquiries: 8, sales_calls_completed: 7, job_orders_total: 0, placements: 0, cost_per_enquiry_usd: 116.71 };
    var auW3 = snap.sales_ops_au_now || { window_start: "2026-08-24", window_end: "2026-08-25", spend_usd: 303.65, enquiries: 2, sales_calls_completed: 0, job_orders_total: 1, placements: 0, cost_per_enquiry_usd: 151.82 };

    var usWeeks = [
      { label: "W1: Aug 10–16", complete: true, data: usW1 },
      { label: "W2: Aug 17–23", complete: true, data: usW2 },
      { label: "W3: Aug 24–25 (2d)", complete: false, data: usW3 },
    ];

    var auWeeks = [
      { label: "W1: Aug 10–16", complete: true, data: auW1 },
      { label: "W2: Aug 17–23", complete: true, data: auW2 },
      { label: "W3: Aug 24–25 (2d)", complete: false, data: auW3 },
    ];

    function buildTableHtml(market, cur, weeks) {
      var h = '<div style="margin-bottom:1rem;">';
      h += '<h4 style="margin:0 0 0.5rem;font-size:0.9rem;">' + (market === "US" ? "United States (USD)" : "Australia (AUD)") + '</h4>';
      h += '<table class="ex-table"><thead><tr>';
      h += '<th>Period</th><th class="num">Spend</th><th class="num">Enquiries</th><th class="num">Discoveries</th><th class="num">Job Orders</th>';
      if (market === "AU") h += '<th class="num">Placements</th>';
      h += '<th class="num">Cost / Enq</th></tr></thead><tbody>';

      weeks.forEach(function (w) {
        var d = w.data || {};
        var isPending = isEnquiryPending(d);
        var spend = formatMoney(d.spend_usd, cur);
        var enq = isPending ? '<span class="ex-status-tag pending">Pending</span>' : formatNum(d.enquiries);
        var disc = d.sales_calls_completed != null ? formatNum(d.sales_calls_completed) : "—";
        var jo = d.job_orders_total != null && d.job_orders_total > 0 ? formatNum(d.job_orders_total) : (market === "US" ? "None confirmed" : "0");
        var pl = d.placements != null && d.placements > 0 ? formatNum(d.placements) : (market === "US" ? "None confirmed" : "0");
        var cpe = isPending || d.cost_per_enquiry_usd == null ? "—" : formatMoney2(d.cost_per_enquiry_usd, cur);

        h += '<tr>';
        h += '<td><strong>' + w.label + '</strong></td>';
        h += '<td class="num">' + spend + '</td>';
        h += '<td class="num">' + enq + '</td>';
        h += '<td class="num">' + disc + '</td>';
        h += '<td class="num">' + jo + '</td>';
        if (market === "AU") h += '<td class="num">' + pl + '</td>';
        h += '<td class="num font-mono">' + cpe + '</td>';
        h += '</tr>';
      });

      h += '</tbody></table></div>';
      return h;
    }

    grid.innerHTML = buildTableHtml("US", "USD", usWeeks) + buildTableHtml("AU", "AUD", auWeeks);
  }

  function renderAttributionBreakdown() {
    var panel = $("#ex-attrib-panel");
    if (!panel) return;

    var h = '<p style="margin:0 0 0.75rem;font-size:0.86rem;color:var(--body);line-height:1.5;">';
    h += '<strong>Reconciliation:</strong> During the 3-week pilot, sales confirmed <strong>49 total employer enquiries</strong> (31 US + 18 AU). In the single-week CRM audit (Aug 17–23), <strong>31 records</strong> were inspected in Zoho, of which <strong>5 contained a valid advertising click ID (GCLID)</strong> (2 US, 3 AU).';
    h += '</p>';
    h += '<ul class="ex-rules-list">';
    h += '<li><strong>Known Exclusions:</strong> 16 disqualified contacts (10 job seekers and 6 not-a-fit) were filtered out by sales operations and are excluded from employer numbers.</li>';
    h += '<li><strong>Phone Calls:</strong> 62 website phone-link clicks were recorded, but voice calls lack CRM dispositioning and caller ANI, requiring manual sales triage.</li>';
    h += '</ul>';

    panel.innerHTML = h;
  }

  function renderAll() {
    var us = buildMarketData("US", STATE.period);
    var au = buildMarketData("AU", STATE.period);

    renderHeader(us);
    renderBottomLine(us, au);
    renderUSNotice(us);
    renderMainScorecard(us, au);
    renderSimplifiedAgencyComparison(us, au);
    renderDeepFunnel(us, au);
    renderWeeklyTrend();
    renderAttributionBreakdown();
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

  function init() {
    var loadingEl = $("#ex-loading");
    if (loadingEl) loadingEl.style.display = "block";

    Promise.all([
      fetchJson("data/executive-snapshot.json"),
      fetchJson("data/executive-snapshot-frozen-2026-08-10.json").catch(function () { return null; }),
      fetchJson("data/agency-baseline.json").catch(function () { return null; }),
      fetchJson("data/sales-ops-week-zoho.json").catch(function () { return null; }),
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
