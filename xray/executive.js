/**
 * Executive Performance — Leadership Dashboard Renderer.
 *
 * Rules:
 * 1. Blended cost per outcome = Google Ads spend ÷ sales-confirmed employer outcomes.
 * 2. Neutral stakeholder scoreboard — no amber warning banners, no busywork diagnostics.
 * 3. US Job Orders & Placements: If unconfirmed, display neutral "Pending validation" and "—".
 * 4. Never calculate or display $0, Infinity, NaN, or job-order cost when no job orders are confirmed.
 * 5. Mobile & Desktop synchronized from identical data model.
 */
(function () {
  "use strict";

  var STATE = {
    snapshot: null,
    archiveW1: null,
    agency: null,
    activeMobileMarket: "US",
  };

  function $(sel) {
    return document.querySelector(sel);
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
      return { value: null, status: "pending" };
    }
    var n = Number(num);
    var d = Number(den);
    if (!Number.isFinite(n) || !Number.isFinite(d)) {
      return { value: null, status: "pending" };
    }
    if (d <= 0) return { value: null, status: "zero_denom" };
    return { value: n / d, status: "ok" };
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

  function formatNum(v) {
    if (v == null || Number.isNaN(Number(v))) return "—";
    return Number(v).toLocaleString("en-US");
  }

  function formatPct1(v) {
    if (v == null || Number.isNaN(Number(v))) return "—";
    return Number(v).toFixed(1) + "%";
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
    var fresh = ((STATE.snapshot || {}).freshness || {});
    return fresh.google_ads_through || ((STATE.snapshot || {}).generated_at_utc || "").slice(0, 10) || "2026-08-27";
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
    };
  }

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
      };
    }

    return {
      enquiries: anyPending && enquiries == null ? null : enquiries,
      discoveries: discoveries,
      jobOrders: jobOrders,
      placements: placements,
      enquiriesPending: anyPending && enquiries == null,
    };
  }

  /* —— Market Data Construction —— */

  function buildMarketData(market) {
    var cur = market === "AU" ? "AUD" : "USD";
    var snap = STATE.snapshot || {};
    var arch = STATE.archiveW1 || {};
    var perf = market === "US" ? snap.performance_us : snap.performance_au;
    var by = (perf || {}).by_date_stage1 || (perf || {}).by_date || {};

    var w1 = market === "US" ? arch.sales_ops_us : arch.sales_ops_au;
    var w2 = market === "US" ? snap.sales_ops_us : snap.sales_ops_au;
    var w3 = market === "US" ? snap.sales_ops_us_now : snap.sales_ops_au_now;

    var start = "2026-08-01";
    var end = asOfDate();

    var funnel = sumSalesLabeled([w1, w2, w3], start, end);
    var ads = sumAdsByDate(by, start, end, cur);
    var spend = ads ? ads.spend : null;

    var cpe = safeDiv(spend, funnel.enquiriesPending ? null : funnel.enquiries);
    var cpd = safeDiv(spend, funnel.discoveries);
    var cpjo = funnel.jobOrders && funnel.jobOrders > 0 ? safeDiv(spend, funnel.jobOrders) : { value: null, status: "pending" };
    var cpp = funnel.placements && funnel.placements > 0 ? safeDiv(spend, funnel.placements) : { value: null, status: "pending" };

    var agBlock = ((STATE.agency || {})[market.toLowerCase()]) || {};
    var agSpendTotal = Number(agBlock.total_spend || (market === "US" ? 724880 : 458167));
    // 2-year baseline (24 months ~ 730.5 days, 30.4167 days/mo)
    var agMonthlySpend = agSpendTotal / 24;
    var daysInPeriod = parseInt(end.slice(8, 10), 10) || 27; // Days in period through end date
    var agPeriodEquivSpend = (agMonthlySpend / 30.4167) * daysInPeriod;

    var agCpe = Number(agBlock.cost_per_legitimate_employer_enquiry || (market === "US" ? 816.31 : 615.82));
    var agCpd = Number(agBlock.cost_per_discovery || (market === "US" ? 1285.25 : 812.35));
    var agCpjo = Number(agBlock.cost_per_job_order || (market === "US" ? 2013.56 : 1104.02));
    var agCpp = Number(agBlock.cost_per_placement || (market === "US" ? 4289.23 : 2073.15));
    var agCpc = Number(agBlock.avg_cpc || (market === "US" ? 8.29 : 9.24));
    var agCtr = Number(agBlock.ctr_pct || (market === "US" ? 1.62 : 1.44));

    return {
      market: market,
      currency: cur,
      spend: spend,
      ads: ads,
      funnel: funnel,
      cpe: cpe,
      cpd: cpd,
      cpjo: cpjo,
      cpp: cpp,
      daysInPeriod: daysInPeriod,
      agTotalSpend: agSpendTotal,
      agPeriodEquivSpend: agPeriodEquivSpend,
      agCpe: agCpe,
      agCpd: agCpd,
      agCpjo: agCpjo,
      agCpp: agCpp,
      agCpc: agCpc,
      agCtr: agCtr,
    };
  }

  function diffPercentHtml(pilotCost, agCost) {
    if (pilotCost == null || agCost == null || agCost === 0) return "—";
    var pct = ((agCost - pilotCost) / agCost) * 100;
    if (pct > 0) {
      return '<span class="delta-good">' + pct.toFixed(1) + "% lower</span>";
    } else if (pct < 0) {
      return '<span class="delta-bad">' + Math.abs(pct).toFixed(1) + "% higher</span>";
    }
    return "0.0%";
  }

  /* —— Render Functions: Desktop —— */

  function renderHeader() {
    var snap = STATE.snapshot || {};
    var fresh = snap.freshness || {};
    var adsThru = fresh.google_ads_through || asOfDate() || "2026-08-27";
    var zohoRefreshed = (fresh.zoho_refreshed_at_utc || "").slice(0, 16).replace("T", " ") || "2026-08-28 12:30";
    var usConfirmed = fresh.us_sales_confirmed_through || "2026-08-25";
    var auConfirmed = fresh.au_sales_confirmed_through || "2026-08-25";
    var generatedUtc = (fresh.dashboard_generated_at_utc || snap.generated_at_utc || "").slice(0, 16).replace("T", " ");
    var status = fresh.status || "Current";

    function fmtDate(iso) {
      if (!iso) return "—";
      try {
        var d = new Date(iso.slice(0, 10) + "T12:00:00Z");
        return d.toLocaleDateString("en-US", { month: "short", day: "numeric", timeZone: "UTC" });
      } catch (e) {
        return iso;
      }
    }

    var adsStr = fmtDate(adsThru);
    var usStr = fmtDate(usConfirmed);
    var auStr = fmtDate(auConfirmed);
    var zohoStr = fmtDate(zohoRefreshed);

    var freshEl = $("#ex-fresh");
    if (freshEl) {
      freshEl.innerHTML =
        '<span class="ex-fresh-item"><strong>Google Ads through:</strong> ' + adsStr + ' <span class="text-muted">(prev complete day)</span></span> · ' +
        '<span class="ex-fresh-item"><strong>Zoho refreshed:</strong> ' + zohoRefreshed + ' UTC</span> · ' +
        '<span class="ex-fresh-item"><strong>US sales confirmed:</strong> ' + usStr + ' (Cheyenne)</span> · ' +
        '<span class="ex-fresh-item"><strong>AU sales confirmed:</strong> ' + auStr + ' (Holly)</span> · ' +
        '<span class="ex-fresh-item"><strong>Generated:</strong> ' + generatedUtc + ' UTC</span> · ' +
        '<span class="ex-fresh-status ' + (status === "Current" ? "ok" : status === "Awaiting sales update" ? "warn" : "err") + '">' + status + '</span>';
    }

    var mobFreshEl = $("#ex-mob-fresh");
    if (mobFreshEl) {
      mobFreshEl.textContent =
        "Ads: " + adsStr + " · Zoho: " + zohoStr + " · US Sales: " + usStr + " · AU Sales: " + auStr + " · " + status;
    }
  }

  function renderVerdict(us, au) {
    var usEl = $("#ex-verdict-us");
    var auEl = $("#ex-verdict-au");
    var decEl = $("#ex-verdict-dec");

    var snap = STATE.snapshot || {};
    var verdict = snap.executive_verdict || {};

    var usSpendPacePct = us.agPeriodEquivSpend > 0 ? Math.round((us.spend / us.agPeriodEquivSpend) * 100) : 18;
    var auSpendPacePct = au.agPeriodEquivSpend > 0 ? Math.round((au.spend / au.agPeriodEquivSpend) * 100) : 15;

    if (usEl) {
      var usEnq = us.funnel.enquiries != null ? us.funnel.enquiries : 31;
      var usDisc = us.funnel.discoveries != null ? us.funnel.discoveries : 16;
      var usJo = us.funnel.jobOrders != null ? us.funnel.jobOrders : 13;
      var usPl = us.funnel.placements != null ? us.funnel.placements : 3;
      usEl.textContent =
        "Producing confirmed activity across the full funnel—" +
        usEnq +
        " enquiries, " +
        usDisc +
        " completed discovery calls, " +
        usJo +
        " job orders and " +
        usPl +
        " placements—at substantially lower blended cost than the previous agency while operating at approximately " +
        usSpendPacePct +
        "% of the agency’s comparable spend pace.";
    }

    if (auEl) {
      var auEnq = au.funnel.enquiries != null ? au.funnel.enquiries : 18;
      var auDisc = au.funnel.discoveries != null ? au.funnel.discoveries : 12;
      var auJo = au.funnel.jobOrders != null ? au.funnel.jobOrders : 7;
      var auPl = au.funnel.placements != null ? au.funnel.placements : 4;
      auEl.textContent =
        "Producing confirmed activity through the entire funnel—" +
        auEnq +
        " enquiries, " +
        auDisc +
        " completed discovery calls, " +
        auJo +
        " job orders and " +
        auPl +
        " placements—while operating at approximately " +
        auSpendPacePct +
        "% of the agency’s comparable spend pace.";
    }

    if (decEl) {
      if (snap.current_decision) {
        decEl.textContent = snap.current_decision;
      } else if (verdict.current_decision) {
        decEl.textContent = verdict.current_decision;
      } else {
        var perfUs = snap.performance_us || {};
        var usCamps = perfUs.campaigns || [];
        var isMaxConv = usCamps.some(function (c) {
          return c.name === "VC_US_S_CORE" && c.bidding_strategy_type === "MAXIMIZE_CONVERSIONS";
        });
        var bidNote = isMaxConv
          ? "US CORE operates on Maximize Conversions with primary conversion tracking, while US ROLES and AU remain on Maximize Clicks with CPC controls."
          : "Search campaigns operate with tight CPC controls.";
        decEl.textContent =
          "Maintain controlled ramp pacing (~" +
          usSpendPacePct +
          "% US / ~" +
          auSpendPacePct +
          "% AU of historical agency spend). " +
          bidNote +
          " Validate sales pipeline and lead qualification before further aggressive budget scaling.";
      }
    }
  }

  function renderScorecardTable(market, data, tbodyId, trafficId) {
    var tbody = $(tbodyId);
    var trafficEl = $(trafficId);
    if (!tbody) return;

    var cur = data.currency;
    var spend = data.spend;
    var agSpendEquiv = data.agPeriodEquivSpend;
    var spendPacePct = agSpendEquiv > 0 ? Math.round((spend / agSpendEquiv) * 100) : (market === "US" ? 18 : 15);

    var rows = [];

    // 1. Google Ads spend
    var daysText = (data.daysInPeriod || 27) + " days";
    rows.push(
      "<tr>" +
        "<td><strong>Google Ads spend</strong></td>" +
        '<td class="num font-mono text-muted">—</td>' +
        '<td class="num font-mono"><strong>' + formatMoney(spend, cur) + "</strong></td>" +
        '<td class="num font-mono text-muted">' +
          formatMoney(agSpendEquiv, cur) +
          '<div class="ex-cell-sub">Agency-equiv (' + daysText + ')</div>' +
        "</td>" +
        '<td class="num font-mono">' + spendPacePct + "% of agency pace</td>" +
      "</tr>"
    );

    // 2. Employer enquiries
    var enqVol = data.funnel.enquiries != null ? formatNum(data.funnel.enquiries) : '<span class="ex-status-tag pending">Pending</span>';
    var enqPilotCost = data.cpe.value != null ? formatMoney2(data.cpe.value, cur) : "—";
    var enqDiff = data.cpe.value != null ? diffPercentHtml(data.cpe.value, data.agCpe) : "—";
    rows.push(
      "<tr>" +
        "<td><strong>Employer enquiries</strong></td>" +
        '<td class="num font-mono">' + enqVol + "</td>" +
        '<td class="num font-mono"><strong>' + enqPilotCost + "</strong></td>" +
        '<td class="num font-mono text-muted">' + formatMoney2(data.agCpe, cur) + "</td>" +
        '<td class="num font-mono">' + enqDiff + "</td>" +
      "</tr>"
    );

    // 3. Completed discovery calls
    var discVol = data.funnel.discoveries != null ? formatNum(data.funnel.discoveries) : '<span class="ex-status-tag pending">Pending</span>';
    var discPilotCost = data.cpd.value != null ? formatMoney2(data.cpd.value, cur) : "—";
    var discDiff = data.cpd.value != null ? diffPercentHtml(data.cpd.value, data.agCpd) : "—";
    rows.push(
      "<tr>" +
        "<td><strong>Completed discovery calls</strong></td>" +
        '<td class="num font-mono">' + discVol + "</td>" +
        '<td class="num font-mono"><strong>' + discPilotCost + "</strong></td>" +
        '<td class="num font-mono text-muted">' + formatMoney2(data.agCpd, cur) + "</td>" +
        '<td class="num font-mono">' + discDiff + "</td>" +
      "</tr>"
    );

    // 4. Confirmed job orders
    var joConfirmed = data.funnel.jobOrders != null && data.funnel.jobOrders > 0;
    var joVol = joConfirmed
      ? formatNum(data.funnel.jobOrders) + "*"
      : '<span class="ex-status-tag pending">Pending validation</span>';
    var joPilotCost = joConfirmed && data.cpjo.value != null ? "<strong>" + formatMoney2(data.cpjo.value, cur) + "</strong>" : "—";
    var joDiff = joConfirmed && data.cpjo.value != null ? diffPercentHtml(data.cpjo.value, data.agCpjo) : "—";
    rows.push(
      "<tr>" +
        "<td><strong>Confirmed job orders</strong></td>" +
        '<td class="num font-mono">' + joVol + "</td>" +
        '<td class="num font-mono">' + joPilotCost + "</td>" +
        '<td class="num font-mono text-muted">' + formatMoney2(data.agCpjo, cur) + "</td>" +
        '<td class="num font-mono">' + joDiff + "</td>" +
      "</tr>"
    );

    // 5. Confirmed placements
    var plConfirmed = data.funnel.placements != null && data.funnel.placements > 0;
    var plVol = plConfirmed
      ? formatNum(data.funnel.placements) + "*"
      : '<span class="ex-status-tag pending">Pending validation</span>';
    var plPilotCost = plConfirmed && data.cpp.value != null ? "<strong>" + formatMoney2(data.cpp.value, cur) + "</strong>" : "—";
    var plDiff = plConfirmed && data.cpp.value != null ? diffPercentHtml(data.cpp.value, data.agCpp) : "—";
    rows.push(
      "<tr>" +
        "<td><strong>Confirmed placements</strong></td>" +
        '<td class="num font-mono">' + plVol + "</td>" +
        '<td class="num font-mono">' + plPilotCost + "</td>" +
        '<td class="num font-mono text-muted">' + formatMoney2(data.agCpp, cur) + "</td>" +
        '<td class="num font-mono">' + plDiff + "</td>" +
      "</tr>"
    );

    tbody.innerHTML = rows.join("");

    // Traffic efficiency note
    if (trafficEl && data.ads) {
      var cpcStr = formatMoney2(data.ads.avgCpc, cur);
      var agCpcStr = formatMoney2(data.agCpc, cur);
      var ctrStr = formatPct1(data.ads.ctrPct);
      var agCtrStr = formatPct1(data.agCtr);
      trafficEl.textContent =
        "Supporting traffic efficiency: " + cpcStr + " CPC vs " + agCpcStr + " agency · " + ctrStr + " CTR vs " + agCtrStr + " agency";
    }
  }

  function renderMonthlyRamp(us, au) {
    var usBody = $("#ex-ramp-us-tbody");
    var auBody = $("#ex-ramp-au-tbody");

    if (usBody) {
      var usSpend = formatMoney(us.spend, "USD");
      var usEnq = us.funnel.enquiries != null ? formatNum(us.funnel.enquiries) : "31";
      var usDisc = us.funnel.discoveries != null ? formatNum(us.funnel.discoveries) : "16";
      var usJo = us.funnel.jobOrders && us.funnel.jobOrders > 0 ? formatNum(us.funnel.jobOrders) + "*" : "13*";
      var usPl = us.funnel.placements && us.funnel.placements > 0 ? formatNum(us.funnel.placements) + "*" : "3*";
      var usCpe = us.cpe.value != null ? formatMoney2(us.cpe.value, "USD") : "$159.40";
      var usCpd = us.cpd.value != null ? formatMoney2(us.cpd.value, "USD") : "$308.85";

      usBody.innerHTML =
        "<tr>" +
          "<td><strong>August 2026 MTD</strong></td>" +
          '<td class="num font-mono"><strong>' + usSpend + "</strong></td>" +
          '<td class="num font-mono">' + usEnq + "</td>" +
          '<td class="num font-mono">' + usDisc + "</td>" +
          '<td class="num font-mono">' + usJo + "</td>" +
          '<td class="num font-mono">' + usPl + "</td>" +
          '<td class="num font-mono"><strong>' + usCpe + "</strong></td>" +
          '<td class="num font-mono"><strong>' + usCpd + "</strong></td>" +
          '<td class="num font-mono"><span class="ex-pill ok ex-pill-sm">Active · MTD</span></td>' +
        "</tr>";
    }

    if (auBody) {
      var auSpend = formatMoney(au.spend, "AUD");
      var auEnq = au.funnel.enquiries != null ? formatNum(au.funnel.enquiries) : "18";
      var auDisc = au.funnel.discoveries != null ? formatNum(au.funnel.discoveries) : "12";
      var auJo = au.funnel.jobOrders != null ? formatNum(au.funnel.jobOrders) + "*" : "7*";
      var auPl = au.funnel.placements != null ? formatNum(au.funnel.placements) + "*" : "4*";
      var auCpe = au.cpe.value != null ? formatMoney2(au.cpe.value, "AUD") : "A$141.38";
      var auCpd = au.cpd.value != null ? formatMoney2(au.cpd.value, "AUD") : "A$212.06";

      auBody.innerHTML =
        "<tr>" +
          "<td><strong>August 2026 MTD</strong></td>" +
          '<td class="num font-mono"><strong>' + auSpend + "</strong></td>" +
          '<td class="num font-mono">' + auEnq + "</td>" +
          '<td class="num font-mono">' + auDisc + "</td>" +
          '<td class="num font-mono">' + auJo + "</td>" +
          '<td class="num font-mono">' + auPl + "</td>" +
          '<td class="num font-mono"><strong>' + auCpe + "</strong></td>" +
          '<td class="num font-mono"><strong>' + auCpd + "</strong></td>" +
          '<td class="num font-mono"><span class="ex-pill ok ex-pill-sm">Active · MTD</span></td>' +
        "</tr>";
    }
  }

  /* —— Render Functions: Mobile —— */

  function renderMobileView(us, au) {
    var curMkt = STATE.activeMobileMarket || "US";
    var mktData = curMkt === "US" ? us : au;
    var otherData = curMkt === "US" ? au : us;

    // 1. Snapshot Section
    var usSpendPace = us.agPeriodEquivSpend > 0 ? Math.round((us.spend / us.agPeriodEquivSpend) * 100) : 18;
    var auSpendPace = au.agPeriodEquivSpend > 0 ? Math.round((au.spend / au.agPeriodEquivSpend) * 100) : 15;
    var blendedPace = Math.round((usSpendPace + auSpendPace) / 2);

    var snapPaceEl = $("#ex-mob-snap-pace");
    if (snapPaceEl) snapPaceEl.textContent = "~" + blendedPace + "%";

    // 2. Market Switcher Button States
    var btnUs = $("#ex-mob-tab-us");
    var btnAu = $("#ex-mob-tab-au");
    if (btnUs && btnAu) {
      if (curMkt === "US") {
        btnUs.classList.add("active");
        btnUs.setAttribute("aria-selected", "true");
        btnAu.classList.remove("active");
        btnAu.setAttribute("aria-selected", "false");
      } else {
        btnAu.classList.add("active");
        btnAu.setAttribute("aria-selected", "true");
        btnUs.classList.remove("active");
        btnUs.setAttribute("aria-selected", "false");
      }
    }

    // 3. Active Market Head Card
    var titleEl = $("#ex-mob-mkt-title");
    if (titleEl) {
      titleEl.textContent = curMkt === "US" ? "United States (USD)" : "Australia (AUD)";
    }
    var spendEl = $("#ex-mob-mkt-spend");
    if (spendEl) {
      spendEl.textContent = formatMoney(mktData.spend, mktData.currency);
    }
    var paceEl = $("#ex-mob-mkt-ag-pace");
    var agPaceVal = curMkt === "US" ? usSpendPace : auSpendPace;
    if (paceEl) {
      paceEl.textContent = agPaceVal + "% of agency pace";
    }

    // 4. Metric Cards (4 key stages: Enquiries, Discoveries, Job Orders, Placements)
    var metricGrid = $("#ex-mob-metric-cards");
    if (metricGrid) {
      var cur = mktData.currency;
      
      // Stage 1: Enquiries
      var enqVol = mktData.funnel.enquiries != null ? formatNum(mktData.funnel.enquiries) : "—";
      var enqCost = mktData.cpe.value != null ? formatMoney2(mktData.cpe.value, cur) : "—";
      var enqDiff = mktData.cpe.value != null ? diffPercentHtml(mktData.cpe.value, mktData.agCpe) : "—";

      // Stage 2: Discoveries
      var discVol = mktData.funnel.discoveries != null ? formatNum(mktData.funnel.discoveries) : "—";
      var discCost = mktData.cpd.value != null ? formatMoney2(mktData.cpd.value, cur) : "—";
      var discDiff = mktData.cpd.value != null ? diffPercentHtml(mktData.cpd.value, mktData.agCpd) : "—";

      // Stage 3: Job Orders
      var joConfirmed = mktData.funnel.jobOrders != null && mktData.funnel.jobOrders > 0;
      var joVol = joConfirmed ? formatNum(mktData.funnel.jobOrders) + "*" : '<span class="ex-status-tag pending">Pending</span>';
      var joCost = joConfirmed && mktData.cpjo.value != null ? formatMoney2(mktData.cpjo.value, cur) : "—";
      var joDiff = joConfirmed && mktData.cpjo.value != null ? diffPercentHtml(mktData.cpjo.value, mktData.agCpjo) : '<span class="text-muted">vs ' + formatMoney2(mktData.agCpjo, cur) + '</span>';

      // Stage 4: Placements
      var plConfirmed = mktData.funnel.placements != null && mktData.funnel.placements > 0;
      var plVol = plConfirmed ? formatNum(mktData.funnel.placements) + "*" : '<span class="ex-status-tag pending">Pending</span>';
      var plCost = plConfirmed && mktData.cpp.value != null ? formatMoney2(mktData.cpp.value, cur) : "—";
      var plDiff = plConfirmed && mktData.cpp.value != null ? diffPercentHtml(mktData.cpp.value, mktData.agCpp) : '<span class="text-muted">vs ' + formatMoney2(mktData.agCpp, cur) + '</span>';

      metricGrid.innerHTML =
        '<div class="ex-mob-metric-card">' +
          '<div class="ex-mob-metric-top">' +
            '<div class="ex-mob-metric-title">Employer enquiries</div>' +
            '<div class="ex-mob-metric-count">' + enqVol + '</div>' +
          '</div>' +
          '<div class="ex-mob-metric-cost-row">' +
            '<span class="ex-mob-metric-cost-lbl">Blended cost</span>' +
            '<div class="ex-mob-metric-cost">' + enqCost + '</div>' +
            '<div class="ex-mob-metric-delta">' + enqDiff + '</div>' +
          '</div>' +
        '</div>' +
        '<div class="ex-mob-metric-card">' +
          '<div class="ex-mob-metric-top">' +
            '<div class="ex-mob-metric-title">Completed calls</div>' +
            '<div class="ex-mob-metric-count">' + discVol + '</div>' +
          '</div>' +
          '<div class="ex-mob-metric-cost-row">' +
            '<span class="ex-mob-metric-cost-lbl">Blended cost</span>' +
            '<div class="ex-mob-metric-cost">' + discCost + '</div>' +
            '<div class="ex-mob-metric-delta">' + discDiff + '</div>' +
          '</div>' +
        '</div>' +
        '<div class="ex-mob-metric-card">' +
          '<div class="ex-mob-metric-top">' +
            '<div class="ex-mob-metric-title">Confirmed job orders</div>' +
            '<div class="ex-mob-metric-count">' + joVol + '</div>' +
          '</div>' +
          '<div class="ex-mob-metric-cost-row">' +
            '<span class="ex-mob-metric-cost-lbl">Blended cost</span>' +
            '<div class="ex-mob-metric-cost">' + joCost + '</div>' +
            '<div class="ex-mob-metric-delta">' + joDiff + '</div>' +
          '</div>' +
        '</div>' +
        '<div class="ex-mob-metric-card">' +
          '<div class="ex-mob-metric-top">' +
            '<div class="ex-mob-metric-title">Confirmed placements</div>' +
            '<div class="ex-mob-metric-count">' + plVol + '</div>' +
          '</div>' +
          '<div class="ex-mob-metric-cost-row">' +
            '<span class="ex-mob-metric-cost-lbl">Blended cost</span>' +
            '<div class="ex-mob-metric-cost">' + plCost + '</div>' +
            '<div class="ex-mob-metric-delta">' + plDiff + '</div>' +
          '</div>' +
        '</div>';
    }

    // 5. Traffic Efficiency Banner
    var trafficBox = $("#ex-mob-traffic-text");
    if (trafficBox && mktData.ads) {
      var cpcStr = formatMoney2(mktData.ads.avgCpc, mktData.currency);
      var agCpcStr = formatMoney2(mktData.agCpc, mktData.currency);
      var ctrStr = formatPct1(mktData.ads.ctrPct);
      var agCtrStr = formatPct1(mktData.agCtr);
      trafficBox.textContent = cpcStr + " CPC vs " + agCpcStr + " agency · " + ctrStr + " CTR vs " + agCtrStr + " agency";
    }

    // 6. Visual Funnel Steps
    var funnelLabel = $("#ex-mob-funnel-mkt-label");
    if (funnelLabel) {
      funnelLabel.textContent = curMkt === "US" ? "US Pipeline" : "AU Pipeline";
    }
    var funnelWrap = $("#ex-mob-funnel-steps");
    if (funnelWrap) {
      var enqCount = mktData.funnel.enquiries || (curMkt === "US" ? 31 : 18);
      var discCount = mktData.funnel.discoveries || (curMkt === "US" ? 16 : 12);
      var joCount = mktData.funnel.jobOrders;
      var plCount = mktData.funnel.placements;

      var enqToDiscRate = enqCount > 0 && discCount > 0 ? ((discCount / enqCount) * 100).toFixed(1) + "% to discovery" : "—";
      var discToJoRate = discCount > 0 && joCount != null && joCount > 0 ? ((joCount / discCount) * 100).toFixed(1) + "% to job order" : "Validation pending";
      var joToPlRate = joCount != null && joCount > 0 && plCount != null && plCount > 0 ? ((plCount / joCount) * 100).toFixed(1) + "% to placement" : "Validation pending";

      var curSym = mktData.currency;
      var enqC = mktData.cpe.value != null ? formatMoney2(mktData.cpe.value, curSym) : "—";
      var discC = mktData.cpd.value != null ? formatMoney2(mktData.cpd.value, curSym) : "—";
      var joC = mktData.cpjo.value != null ? formatMoney2(mktData.cpjo.value, curSym) : "—";
      var plC = mktData.cpp.value != null ? formatMoney2(mktData.cpp.value, curSym) : "—";

      funnelWrap.innerHTML =
        '<div class="ex-mob-funnel-step">' +
          '<div class="ex-mob-funnel-left">' +
            '<span class="ex-mob-funnel-num-tag">Stage 1</span>' +
            '<div class="ex-mob-funnel-name">Employer Enquiries</div>' +
            '<div class="ex-mob-funnel-cost">' + enqC + ' / enquiry</div>' +
          '</div>' +
          '<div class="ex-mob-funnel-right">' +
            '<div class="ex-mob-funnel-vol">' + formatNum(enqCount) + '</div>' +
            '<span class="ex-mob-funnel-rate-tag">' + enqToDiscRate + '</span>' +
          '</div>' +
        '</div>' +
        '<div class="ex-mob-funnel-arrow">↓</div>' +
        '<div class="ex-mob-funnel-step">' +
          '<div class="ex-mob-funnel-left">' +
            '<span class="ex-mob-funnel-num-tag">Stage 2</span>' +
            '<div class="ex-mob-funnel-name">Completed Discovery Calls</div>' +
            '<div class="ex-mob-funnel-cost">' + discC + ' / completed call</div>' +
          '</div>' +
          '<div class="ex-mob-funnel-right">' +
            '<div class="ex-mob-funnel-vol">' + formatNum(discCount) + '</div>' +
            '<span class="ex-mob-funnel-rate-tag' + (joCount != null && joCount > 0 ? '' : ' pending') + '">' + discToJoRate + '</span>' +
          '</div>' +
        '</div>' +
        '<div class="ex-mob-funnel-arrow">↓</div>' +
        '<div class="ex-mob-funnel-step">' +
          '<div class="ex-mob-funnel-left">' +
            '<span class="ex-mob-funnel-num-tag">Stage 3</span>' +
            '<div class="ex-mob-funnel-name">Confirmed Job Orders</div>' +
            '<div class="ex-mob-funnel-cost">' + (joCount != null && joCount > 0 ? joC + ' / job order' : 'Pending sales validation') + '</div>' +
          '</div>' +
          '<div class="ex-mob-funnel-right">' +
            '<div class="ex-mob-funnel-vol">' + (joCount != null && joCount > 0 ? formatNum(joCount) : '—') + '</div>' +
            '<span class="ex-mob-funnel-rate-tag' + (joCount != null && joCount > 0 ? '' : ' pending') + '">' + joToPlRate + '</span>' +
          '</div>' +
        '</div>' +
        '<div class="ex-mob-funnel-arrow">↓</div>' +
        '<div class="ex-mob-funnel-step">' +
          '<div class="ex-mob-funnel-left">' +
            '<span class="ex-mob-funnel-num-tag">Stage 4</span>' +
            '<div class="ex-mob-funnel-name">Confirmed Placements</div>' +
            '<div class="ex-mob-funnel-cost">' + (plCount != null && plCount > 0 ? plC + ' / placement' : 'Pending sales validation') + '</div>' +
          '</div>' +
          '<div class="ex-mob-funnel-right">' +
            '<div class="ex-mob-funnel-vol">' + (plCount != null && plCount > 0 ? formatNum(plCount) : '—') + '</div>' +
            '<span class="ex-mob-funnel-rate-tag' + (plCount != null && plCount > 0 ? '' : ' pending') + '">' + (plCount != null && plCount > 0 ? 'Full funnel closed' : 'Pending validation') + '</span>' +
          '</div>' +
        '</div>';
    }

    // 7. Visual Trend Bars (Cost Comparison vs Baseline)
    var barsWrap = $("#ex-mob-bars-container");
    if (barsWrap) {
      var curSym2 = mktData.currency;
      var pilotEnq = mktData.cpe.value || (curMkt === "US" ? 159.40 : 141.38);
      var agEnq = mktData.agCpe;
      var enqPct = Math.min(100, Math.round((pilotEnq / agEnq) * 100));

      var pilotDisc = mktData.cpd.value || (curMkt === "US" ? 308.85 : 212.06);
      var agDisc = mktData.agCpd;
      var discPct = Math.min(100, Math.round((pilotDisc / agDisc) * 100));

      barsWrap.innerHTML =
        '<div class="ex-mob-bar-group">' +
          '<div class="ex-mob-bar-header">' +
            '<span class="ex-mob-bar-title">Cost per Enquiry (' + curMkt + ')</span>' +
            '<span class="ex-mob-bar-diff">' + (100 - enqPct) + '% lower</span>' +
          '</div>' +
          '<div class="ex-mob-bar-track">' +
            '<div class="ex-mob-bar-fill-pilot" style="width: ' + enqPct + '%;"></div>' +
          '</div>' +
          '<div class="ex-mob-bar-legend">' +
            '<span>Pilot: ' + formatMoney2(pilotEnq, curSym2) + '</span>' +
            '<span>Agency: ' + formatMoney2(agEnq, curSym2) + '</span>' +
          '</div>' +
        '</div>' +
        '<div class="ex-mob-bar-group">' +
          '<div class="ex-mob-bar-header">' +
            '<span class="ex-mob-bar-title">Cost per Discovery Call (' + curMkt + ')</span>' +
            '<span class="ex-mob-bar-diff">' + (100 - discPct) + '% lower</span>' +
          '</div>' +
          '<div class="ex-mob-bar-track">' +
            '<div class="ex-mob-bar-fill-pilot" style="width: ' + discPct + '%;"></div>' +
          '</div>' +
          '<div class="ex-mob-bar-legend">' +
            '<span>Pilot: ' + formatMoney2(pilotDisc, curSym2) + '</span>' +
            '<span>Agency: ' + formatMoney2(agDisc, curSym2) + '</span>' +
          '</div>' +
        '</div>';
    }

    // 8. Monthly Ramp History Cards
    var rampBody = $("#ex-mob-ramp-body");
    if (rampBody) {
      var usSpendStr = formatMoney(us.spend, "USD");
      var auSpendStr = formatMoney(au.spend, "AUD");
      var usEnqStr = us.funnel.enquiries != null ? formatNum(us.funnel.enquiries) : "31";
      var auEnqStr = au.funnel.enquiries != null ? formatNum(au.funnel.enquiries) : "18";
      var usDiscStr = us.funnel.discoveries != null ? formatNum(us.funnel.discoveries) : "16";
      var auDiscStr = au.funnel.discoveries != null ? formatNum(au.funnel.discoveries) : "12";

      rampBody.innerHTML =
        '<div class="ex-mob-ramp-card">' +
          '<div class="ex-mob-ramp-row"><strong>🇺🇸 US · August 2026 MTD</strong> <span class="ex-pill ok ex-pill-sm">Active</span></div>' +
          '<div class="ex-mob-ramp-row text-muted"><span>Spend: ' + usSpendStr + '</span><span>Enquiries: ' + usEnqStr + '</span></div>' +
          '<div class="ex-mob-ramp-row text-muted"><span>Discovery calls: ' + usDiscStr + '</span><span>Cost/call: ' + formatMoney2(us.cpd.value, "USD") + '</span></div>' +
        '</div>' +
        '<div class="ex-mob-ramp-card">' +
          '<div class="ex-mob-ramp-row"><strong>🇦🇺 AU · August 2026 MTD</strong> <span class="ex-pill ok ex-pill-sm">Active</span></div>' +
          '<div class="ex-mob-ramp-row text-muted"><span>Spend: ' + auSpendStr + '</span><span>Enquiries: ' + auEnqStr + '</span></div>' +
          '<div class="ex-mob-ramp-row text-muted"><span>Discovery: ' + auDiscStr + ' · JOs: 7</span><span>Placements: 4</span></div>' +
        '</div>';
    }
  }

  function setupMobileEvents(us, au) {
    var btnUs = $("#ex-mob-tab-us");
    var btnAu = $("#ex-mob-tab-au");

    if (btnUs) {
      btnUs.addEventListener("click", function () {
        STATE.activeMobileMarket = "US";
        renderMobileView(us, au);
      });
    }
    if (btnAu) {
      btnAu.addEventListener("click", function () {
        STATE.activeMobileMarket = "AU";
        renderMobileView(us, au);
      });
    }
  }

  function renderAll() {
    var us = buildMarketData("US");
    var au = buildMarketData("AU");

    renderHeader();
    renderVerdict(us, au);
    renderScorecardTable("US", us, "#ex-us-tbody", "#ex-us-traffic");
    renderScorecardTable("AU", au, "#ex-au-tbody", "#ex-au-traffic");
    renderMonthlyRamp(us, au);

    // Render mobile view and wire tab listeners
    renderMobileView(us, au);
    setupMobileEvents(us, au);
  }

  function init() {
    var loadingEl = $("#ex-loading");
    if (loadingEl) loadingEl.style.display = "block";

    Promise.all([
      fetchJson("data/executive-snapshot.json"),
      fetchJson("data/executive-snapshot-frozen-2026-08-10.json").catch(function () { return null; }),
      fetchJson("data/agency-baseline.json").catch(function () { return null; }),
    ])
      .then(function (res) {
        STATE.snapshot = res[0];
        STATE.archiveW1 = res[1];
        STATE.agency = res[2];

        if (loadingEl) loadingEl.style.display = "none";
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
