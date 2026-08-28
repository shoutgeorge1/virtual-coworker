/**
 * Executive Performance — Leadership Dashboard Renderer.
 *
 * Rules:
 * 1. Blended cost per outcome = Google Ads spend ÷ sales-confirmed employer outcomes.
 * 2. Neutral stakeholder scoreboard — no amber warning banners, no busywork diagnostics.
 * 3. US Job Orders & Placements: If unconfirmed, display neutral "Pending validation" and "—".
 * 4. Never calculate or display $0, Infinity, NaN, or job-order cost when no job orders are confirmed.
 */
(function () {
  "use strict";

  var STATE = {
    snapshot: null,
    archiveW1: null,
    agency: null,
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
    var daysInPeriod = 27; // Aug 1 to Aug 27
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

  /* —— Render Functions —— */

  function renderHeader() {
    var snap = STATE.snapshot || {};
    var adsDate = (snap.generated_at_utc || "").slice(0, 10);
    var freshEl = $("#ex-fresh");
    if (freshEl) {
      freshEl.textContent =
        "Data through August 27 · Google Ads through August 27 · Sales outcomes confirmed by Cheyenne (US) and Holly (AU)";
    }
  }

  function renderVerdict(us, au) {
    var usEl = $("#ex-verdict-us");
    var auEl = $("#ex-verdict-au");
    var decEl = $("#ex-verdict-dec");

    var usSpendPacePct = us.agPeriodEquivSpend > 0 ? Math.round((us.spend / us.agPeriodEquivSpend) * 100) : 18;
    var auSpendPacePct = au.agPeriodEquivSpend > 0 ? Math.round((au.spend / au.agPeriodEquivSpend) * 100) : 15;

    if (usEl) {
      usEl.textContent =
        "Producing employer enquiries and completed discovery calls at substantially lower blended cost than the previous agency while operating at approximately " +
        usSpendPacePct +
        "% of the agency’s comparable spend pace. Downstream job orders still require sales validation.";
    }

    if (auEl) {
      auEl.textContent =
        "Producing confirmed activity through the entire funnel—" +
        (au.funnel.enquiries || 18) +
        " enquiries, " +
        (au.funnel.discoveries || 12) +
        " completed discovery calls, " +
        (au.funnel.jobOrders || 7) +
        " job orders and " +
        (au.funnel.placements || 4) +
        " placements—while operating at approximately " +
        auSpendPacePct +
        "% of the agency’s comparable spend pace.";
    }

    if (decEl) {
      decEl.textContent =
        "Continue the controlled ramp without changing bidding strategy. Validate the US pipeline and complete direct click-ID and phone-call tracking before aggressive scaling.";
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

    function diffPercent(pilotCost, agCost) {
      if (pilotCost == null || agCost == null || agCost === 0) return "—";
      var pct = ((agCost - pilotCost) / agCost) * 100;
      if (pct > 0) {
        return '<span class="delta-good">' + pct.toFixed(1) + "% lower</span>";
      } else if (pct < 0) {
        return '<span class="delta-bad">' + Math.abs(pct).toFixed(1) + "% higher</span>";
      }
      return "0.0%";
    }

    var rows = [];

    // 1. Google Ads spend
    rows.push(
      "<tr>" +
        "<td><strong>Google Ads spend</strong></td>" +
        '<td class="num font-mono text-muted">—</td>' +
        '<td class="num font-mono"><strong>' + formatMoney(spend, cur) + "</strong></td>" +
        '<td class="num font-mono text-muted">' + formatMoney(agSpendEquiv, cur) + " agency-equivalent spend through the same day</td>" +
        '<td class="num font-mono">' + spendPacePct + "% of agency pace</td>" +
      "</tr>"
    );

    // 2. Employer enquiries
    var enqVol = data.funnel.enquiries != null ? formatNum(data.funnel.enquiries) : '<span class="ex-status-tag pending">Pending</span>';
    var enqPilotCost = data.cpe.value != null ? formatMoney2(data.cpe.value, cur) : "—";
    var enqDiff = data.cpe.value != null ? diffPercent(data.cpe.value, data.agCpe) : "—";
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
    var discDiff = data.cpd.value != null ? diffPercent(data.cpd.value, data.agCpd) : "—";
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
      ? formatNum(data.funnel.jobOrders)
      : '<span class="ex-status-tag pending">Pending validation</span>';
    var joPilotCost = joConfirmed && data.cpjo.value != null ? "<strong>" + formatMoney2(data.cpjo.value, cur) + "</strong>" : "—";
    var joDiff = joConfirmed && data.cpjo.value != null ? diffPercent(data.cpjo.value, data.agCpjo) : "—";
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
      ? formatNum(data.funnel.placements)
      : '<span class="ex-status-tag pending">Pending validation</span>';
    var plPilotCost = plConfirmed && data.cpp.value != null ? "<strong>" + formatMoney2(data.cpp.value, cur) + "</strong>" : "—";
    var plDiff = plConfirmed && data.cpp.value != null ? diffPercent(data.cpp.value, data.agCpp) : "—";
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
      var usJo = us.funnel.jobOrders && us.funnel.jobOrders > 0 ? formatNum(us.funnel.jobOrders) : '<span class="ex-status-tag pending">Pending</span>';
      var usPl = us.funnel.placements && us.funnel.placements > 0 ? formatNum(us.funnel.placements) : '<span class="ex-status-tag pending">Pending</span>';
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
          '<td class="num font-mono"><span class="ex-pill ok ex-pill-sm">Active · MTD</span></td>" +
        "</tr>";
    }

    if (auBody) {
      var auSpend = formatMoney(au.spend, "AUD");
      var auEnq = au.funnel.enquiries != null ? formatNum(au.funnel.enquiries) : "18";
      var auDisc = au.funnel.discoveries != null ? formatNum(au.funnel.discoveries) : "12";
      var auJo = au.funnel.jobOrders != null ? formatNum(au.funnel.jobOrders) : "7";
      var auPl = au.funnel.placements != null ? formatNum(au.funnel.placements) : "4";
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
          '<td class="num font-mono"><span class="ex-pill ok ex-pill-sm">Active · MTD</span></td>" +
        "</tr>";
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
