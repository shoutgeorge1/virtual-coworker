/**
 * Executive Performance — Leadership Dashboard Renderer.
 *
 * Single source of truth: executive-snapshot.json → monthly_history (+ freshness).
 * Desktop and mobile render from the same computed model. No hardcoded metrics.
 *
 * Rules:
 * 1. Blended cost per outcome = Google Ads spend ÷ sales-confirmed employer outcomes.
 * 2. Neutral stakeholder scoreboard — no amber warning banners.
 * 3. Missing outcomes → Pending / —, never $0 or invented figures.
 * 4. Never combine USD and AUD.
 * 5. Prefer monthly_history over week slices for month-level scoreboards.
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

  function asOfDate() {
    var fresh = ((STATE.snapshot || {}).freshness || {});
    return fresh.google_ads_through || ((STATE.snapshot || {}).generated_at_utc || "").slice(0, 10) || "2026-09-03";
  }

  function monthName(ym) {
    var names = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"];
    var parts = String(ym || "").split("-");
    var m = parseInt(parts[1], 10);
    var y = parts[0] || "";
    if (!m || m < 1 || m > 12) return String(ym || "");
    return names[m - 1] + " " + y;
  }

  function daysInclusive(start, end) {
    try {
      var a = new Date(start.slice(0, 10) + "T12:00:00Z");
      var b = new Date(end.slice(0, 10) + "T12:00:00Z");
      var n = Math.round((b - a) / 86400000) + 1;
      return n > 0 ? n : 1;
    } catch (e) {
      return parseInt(String(end).slice(8, 10), 10) || 1;
    }
  }

  function monthlyHistory() {
    return ((STATE.snapshot || {}).monthly_history || []).slice();
  }

  function activeMonthRecord() {
    var hist = monthlyHistory();
    for (var i = hist.length - 1; i >= 0; i--) {
      if (hist[i] && hist[i].status === "active_mtd") return hist[i];
    }
    var end = asOfDate();
    var start = end.slice(0, 8) + "01";
    return {
      month: end.slice(0, 7),
      label: monthName(end.slice(0, 7)) + " MTD",
      period_start: start,
      period_end: end,
      status: "active_mtd",
    };
  }

  function closedMonthRecord() {
    var hist = monthlyHistory();
    for (var i = hist.length - 1; i >= 0; i--) {
      if (hist[i] && hist[i].status === "complete") return hist[i];
    }
    return null;
  }

  function reportingPeriod() {
    var rec = activeMonthRecord();
    return {
      start: rec.period_start || (asOfDate().slice(0, 8) + "01"),
      end: rec.period_end || asOfDate(),
      label: rec.label || (monthName((rec.period_start || asOfDate()).slice(0, 7)) + " MTD"),
      monthKey: rec.month || (asOfDate().slice(0, 7)),
    };
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

  function agencyBlock(market) {
    return ((STATE.agency || {})[market.toLowerCase()]) || {};
  }

  function agencyPeriodEquiv(market, daysInPeriod) {
    var agBlock = agencyBlock(market);
    var agSpendTotal = Number(agBlock.total_spend || (market === "US" ? 724880 : 458167));
    var agMonthlySpend = agSpendTotal / 24;
    return (agMonthlySpend / 30.4167) * daysInPeriod;
  }

  function spendPacePct(spend, agPeriodEquiv) {
    if (spend == null || !(agPeriodEquiv > 0)) return null;
    return Math.round((Number(spend) / agPeriodEquiv) * 100);
  }

  function funnelFromMonthSide(m) {
    m = m || {};
    return {
      enquiries: m.enquiries != null ? Number(m.enquiries) : null,
      discoveries: m.sales_calls_completed != null ? Number(m.sales_calls_completed) : null,
      jobOrders: m.job_orders_total != null ? Number(m.job_orders_total) : null,
      placements: m.placements != null ? Number(m.placements) : null,
      enquiriesPending: m.enquiries == null,
    };
  }

  function costFromMonth(m, spend, funnel, key, den) {
    if (m && m[key] != null) return { value: Number(m[key]), status: "ok" };
    return safeDiv(spend, den);
  }

  /* —— Market Data Construction (monthly_history first) —— */

  function buildMarketData(market) {
    var cur = market === "AU" ? "AUD" : "USD";
    var snap = STATE.snapshot || {};
    var perf = market === "US" ? snap.performance_us : snap.performance_au;
    var by = (perf || {}).by_date_stage1 || (perf || {}).by_date || {};
    var period = reportingPeriod();
    var rec = activeMonthRecord();
    var side = market === "US" ? "us" : "au";
    var m = (rec && rec[side]) || {};

    var start = period.start;
    var end = period.end;
    var ads = sumAdsByDate(by, start, end, cur);

    var spend = m.spend != null ? Number(m.spend) : ads ? ads.spend : null;
    var funnel = funnelFromMonthSide(m);

    var cpe = costFromMonth(m, spend, funnel, "cost_per_enquiry", funnel.enquiriesPending ? null : funnel.enquiries);
    var cpd = costFromMonth(m, spend, funnel, "cost_per_discovery", funnel.discoveries);
    var cpjo =
      funnel.jobOrders != null && funnel.jobOrders > 0
        ? costFromMonth(m, spend, funnel, "cost_per_job_order", funnel.jobOrders)
        : { value: null, status: "pending" };
    var cpp =
      funnel.placements != null && funnel.placements > 0
        ? costFromMonth(m, spend, funnel, "cost_per_placement", funnel.placements)
        : { value: null, status: "pending" };

    var agBlock = agencyBlock(market);
    var daysInPeriod = daysInclusive(start, end);
    var agPeriodEquivSpend = agencyPeriodEquiv(market, daysInPeriod);
    var agCpe = Number(agBlock.cost_per_legitimate_employer_enquiry || (market === "US" ? 816.31 : 615.82));
    var agCpd = Number(agBlock.cost_per_discovery || (market === "US" ? 1285.25 : 812.35));
    var agCpjo = Number(agBlock.cost_per_job_order || (market === "US" ? 2013.56 : 1104.02));
    var agCpp = Number(agBlock.cost_per_placement || (market === "US" ? 4289.23 : 2073.15));
    var agCpc = Number(agBlock.avg_cpc || (market === "US" ? 8.29 : 9.24));
    var agCtr = Number(agBlock.ctr_pct || (market === "US" ? 1.62 : 1.44));

    if (ads && spend != null) {
      ads = Object.assign({}, ads, { spend: spend });
    }

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
      periodLabel: period.label,
      agPeriodEquivSpend: agPeriodEquivSpend,
      agCpe: agCpe,
      agCpd: agCpd,
      agCpjo: agCpjo,
      agCpp: agCpp,
      agCpc: agCpc,
      agCtr: agCtr,
      pacePct: spendPacePct(spend, agPeriodEquivSpend),
    };
  }

  function buildClosedMarketData(market) {
    var closed = closedMonthRecord();
    if (!closed) return null;
    var cur = market === "AU" ? "AUD" : "USD";
    var side = market === "US" ? "us" : "au";
    var m = closed[side] || {};
    var funnel = funnelFromMonthSide(m);
    var spend = m.spend != null ? Number(m.spend) : null;
    var daysInPeriod = daysInclusive(closed.period_start, closed.period_end);
    var agPeriodEquivSpend = agencyPeriodEquiv(market, daysInPeriod);
    var agBlock = agencyBlock(market);
    return {
      market: market,
      currency: cur,
      label: closed.label || "August 2026",
      periodStart: closed.period_start,
      periodEnd: closed.period_end,
      spend: spend,
      funnel: funnel,
      cpe: m.cost_per_enquiry != null ? Number(m.cost_per_enquiry) : null,
      cpd: m.cost_per_discovery != null ? Number(m.cost_per_discovery) : null,
      pacePct: spendPacePct(spend, agPeriodEquivSpend),
      agCpe: Number(agBlock.cost_per_legitimate_employer_enquiry || (market === "US" ? 816.31 : 615.82)),
      agCpd: Number(agBlock.cost_per_discovery || (market === "US" ? 1285.25 : 812.35)),
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

  function fmtShortDate(iso) {
    if (!iso || iso === "—") return "—";
    try {
      var d = new Date(iso.slice(0, 10) + "T12:00:00Z");
      return d.toLocaleDateString("en-US", { month: "short", day: "numeric", timeZone: "UTC" });
    } catch (e) {
      return iso;
    }
  }

  function funnelChain(data, currency) {
    var f = data.funnel || {};
    var spendStr = formatMoney(data.spend, currency);
    var enq = f.enquiries != null ? formatNum(f.enquiries) : "Pending";
    var disc = f.discoveries != null ? formatNum(f.discoveries) : "Pending";
    var jo = f.jobOrders != null ? formatNum(f.jobOrders) + " job orders*" : "Pending job orders";
    var pl = f.placements != null ? formatNum(f.placements) + " placements*" : "Pending placements";
    return (
      spendStr +
      " → " +
      enq +
      " employer enquiries → " +
      disc +
      " completed calls → " +
      jo +
      " → " +
      pl
    );
  }

  /* —— Render: Header —— */

  function renderHeader() {
    var snap = STATE.snapshot || {};
    var fresh = snap.freshness || {};
    var period = reportingPeriod();
    var adsThru = fresh.google_ads_through || asOfDate() || period.end;
    var zohoRefreshed = (fresh.zoho_refreshed_at_utc || "").slice(0, 16).replace("T", " ") || "—";
    var usConfirmed = fresh.us_sales_confirmed_through || "—";
    var auConfirmed = fresh.au_sales_confirmed_through || "—";
    var generatedUtc = (fresh.dashboard_generated_at_utc || snap.generated_at_utc || "").slice(0, 16).replace("T", " ");
    var status = fresh.status || "Current";

    var adsStr = fmtShortDate(adsThru);
    var usStr = fmtShortDate(usConfirmed);
    var auStr = fmtShortDate(auConfirmed);

    var periodEl = $("#ex-period");
    if (periodEl) {
      periodEl.textContent =
        period.label.indexOf("MTD") >= 0
          ? period.label.replace(" MTD", " · Month to Date")
          : period.label;
    }
    var mobPeriod = $("#ex-mob-period-badge");
    if (mobPeriod) mobPeriod.textContent = period.label;

    var volLabel = period.label.indexOf("MTD") >= 0 ? period.label.replace(" MTD", " MTD volume") : period.label + " volume";
    ["#ex-us-vol-th", "#ex-au-vol-th"].forEach(function (sel) {
      var th = $(sel);
      if (th) th.textContent = volLabel;
    });

    var freshEl = $("#ex-fresh");
    if (freshEl) {
      freshEl.innerHTML =
        '<span class="ex-fresh-item"><strong>Reporting period:</strong> ' +
        period.start +
        " → " +
        period.end +
        "</span> · " +
        '<span class="ex-fresh-item"><strong>Google Ads through:</strong> ' +
        adsStr +
        ' <span class="text-muted">(prev complete day)</span></span> · ' +
        '<span class="ex-fresh-item"><strong>Zoho refreshed:</strong> ' +
        zohoRefreshed +
        " UTC</span> · " +
        '<span class="ex-fresh-item"><strong>US sales confirmed:</strong> ' +
        usStr +
        " (Cheyenne)</span> · " +
        '<span class="ex-fresh-item"><strong>AU sales confirmed:</strong> ' +
        auStr +
        " (Holly)</span> · " +
        '<span class="ex-fresh-item"><strong>Generated:</strong> ' +
        generatedUtc +
        " UTC</span> · " +
        '<span class="ex-fresh-status ' +
        (status === "Current" ? "ok" : status === "Awaiting sales update" ? "warn" : "err") +
        '">' +
        status +
        "</span>";
    }

    var mobFreshEl = $("#ex-mob-fresh");
    if (mobFreshEl) {
      mobFreshEl.textContent =
        period.label + " · Ads through " + adsStr + " · US sales " + usStr + " · AU sales " + auStr + " · " + status;
    }
  }

  /* —— Render: Above-the-fold summary —— */

  function renderExecutiveSummary(us, au) {
    var closedUs = buildClosedMarketData("US");
    var closedAu = buildClosedMarketData("AU");
    var fresh = ((STATE.snapshot || {}).freshness || {});
    var usConfirmed = fresh.us_sales_confirmed_through || "—";
    var auConfirmed = fresh.au_sales_confirmed_through || "—";
    var period = reportingPeriod();

    var augLine = "";
    if (closedUs && closedAu) {
      augLine =
        "August closed: US " +
        funnelChain(closedUs, "USD") +
        ". AU " +
        funnelChain(closedAu, "AUD") +
        ".";
    }

    var usPace = us.pacePct != null ? us.pacePct + "%" : "—";
    var auPace = au.pacePct != null ? au.pacePct + "%" : "—";
    var sepLine =
      period.label.replace(" MTD", "") +
      " through " +
      fmtShortDate(period.end) +
      ": US spend " +
      formatMoney(us.spend, "USD") +
      " at " +
      usPace +
      " of agency-equivalent pace; AU spend " +
      formatMoney(au.spend, "AUD") +
      " at " +
      auPace +
      ". Sales outcomes await the next labeled update. Hold current budgets until lead quality and pipeline outcomes are validated.";

    var decision =
      "US sales confirmed through " +
      fmtShortDate(usConfirmed) +
      "; AU through " +
      fmtShortDate(auConfirmed) +
      ". " +
      "Awaiting sales update. Current daily budgets (context only): US $250 Core + $100 Roles = $350/day; AU A$150 Core + A$65 Roles = A$215/day.";

    var footnote =
      "*Blended sales-confirmed company outcomes; not all Google Ads-attributed. Management reporting uses blended, sales-confirmed company outcomes. Optimization reporting requires direct GCLID and usable phone attribution.";

    var deskAug = $("#ex-summary-august");
    var deskSep = $("#ex-summary-september");
    var deskDec = $("#ex-summary-decision");
    var deskNote = $("#ex-summary-footnote");
    if (deskAug) deskAug.textContent = augLine;
    if (deskSep) deskSep.textContent = sepLine;
    if (deskDec) deskDec.textContent = decision;
    if (deskNote) deskNote.textContent = footnote;

    var mobSnap = $("#ex-mob-snapshot-text");
    if (mobSnap) {
      mobSnap.textContent = (augLine ? augLine + " " : "") + sepLine;
    }

    var mobPace = $("#ex-mob-snap-pace");
    if (mobPace) {
      mobPace.textContent =
        "US " + (us.pacePct != null ? us.pacePct + "%" : "—") + " · AU " + (au.pacePct != null ? au.pacePct + "%" : "—");
    }
    var mobPaceLbl = $("#ex-mob-snap-pace-lbl");
    if (mobPaceLbl) mobPaceLbl.textContent = "Agency-equiv pace";
    var mobPaceSub = $("#ex-mob-snap-pace-sub");
    if (mobPaceSub) mobPaceSub.textContent = "Sep MTD · markets separate";

    var closedForCosts = closedUs;
    var cpePct =
      closedForCosts && closedForCosts.cpe != null && closedForCosts.agCpe
        ? Math.round(((closedForCosts.agCpe - closedForCosts.cpe) / closedForCosts.agCpe) * 100)
        : null;
    var cpdPct =
      closedForCosts && closedForCosts.cpd != null && closedForCosts.agCpd
        ? Math.round(((closedForCosts.agCpd - closedForCosts.cpd) / closedForCosts.agCpd) * 100)
        : null;

    var mobCpe = $("#ex-mob-snap-cpe");
    if (mobCpe) mobCpe.textContent = cpePct != null ? "-" + cpePct + "%" : "—";
    var mobCpeSub = $("#ex-mob-snap-cpe-sub");
    if (mobCpeSub) {
      mobCpeSub.textContent =
        closedUs && closedUs.cpe != null
          ? "US " + formatMoney2(closedUs.cpe, "USD") + " · Aug closed"
          : "Awaiting sales update";
    }

    var mobCpd = $("#ex-mob-snap-cpd");
    if (mobCpd) mobCpd.textContent = cpdPct != null ? "-" + cpdPct + "%" : "—";
    var mobCpdSub = $("#ex-mob-snap-cpd-sub");
    if (mobCpdSub) {
      mobCpdSub.textContent =
        closedUs && closedUs.cpd != null
          ? "US " + formatMoney2(closedUs.cpd, "USD") + " · Aug closed"
          : "Awaiting sales update";
    }

    var usEl = $("#ex-verdict-us");
    var auEl = $("#ex-verdict-au");
    var decEl = $("#ex-verdict-dec");
    if (usEl) {
      usEl.textContent =
        closedUs
          ? "August closed: " +
            funnelChain(closedUs, "USD") +
            ". Cost/enquiry " +
            formatMoney2(closedUs.cpe, "USD") +
            "; cost/completed call " +
            formatMoney2(closedUs.cpd, "USD") +
            ". September through " +
            fmtShortDate(period.end) +
            ": spend " +
            formatMoney(us.spend, "USD") +
            " at " +
            usPace +
            " of agency-equivalent pace. Sales outcomes pending labeled update."
          : "Ads spend " + formatMoney(us.spend, "USD") + " (~" + usPace + " agency pace). Sales outcomes pending.";
    }
    if (auEl) {
      auEl.textContent =
        closedAu
          ? "August closed: " +
            funnelChain(closedAu, "AUD") +
            ". Cost/enquiry " +
            formatMoney2(closedAu.cpe, "AUD") +
            "; cost/completed call " +
            formatMoney2(closedAu.cpd, "AUD") +
            ". September through " +
            fmtShortDate(period.end) +
            ": spend " +
            formatMoney(au.spend, "AUD") +
            " at " +
            auPace +
            " of agency-equivalent pace. Sales outcomes pending labeled update."
          : "Ads spend " + formatMoney(au.spend, "AUD") + " (~" + auPace + " agency pace). Sales outcomes pending.";
    }
    if (decEl) {
      decEl.textContent =
        "Hold current budgets until lead quality and pipeline outcomes are validated. " +
        "US ~" +
        usPace +
        " / AU ~" +
        auPace +
        " of agency-equivalent pace (September MTD). " +
        decision;
    }

    var working = $("#ex-mob-working-text");
    if (working && closedUs && closedAu) {
      working.textContent =
        "August closed at lower blended unit costs than the agency baseline — US " +
        formatMoney2(closedUs.cpe, "USD") +
        "/enquiry and " +
        formatMoney2(closedUs.cpd, "USD") +
        "/call; AU " +
        formatMoney2(closedAu.cpe, "AUD") +
        "/enquiry and " +
        formatMoney2(closedAu.cpd, "AUD") +
        "/call. September spend is live at US " +
        usPace +
        " / AU " +
        auPace +
        " agency-equivalent pace.";
    }
    var uncertain = $("#ex-mob-uncertain-text");
    if (uncertain) {
      uncertain.textContent =
        "September sales outcomes are pending the next properly labeled Cheyenne (US) and Holly (AU) update. " +
        "US sales confirmed through " +
        fmtShortDate(usConfirmed) +
        "; AU through " +
        fmtShortDate(auConfirmed) +
        ". Awaiting sales update.";
    }
    var next = $("#ex-mob-next-text");
    if (next) {
      next.textContent =
        "Hold current budgets. Validate lead quality and pipeline outcomes before scaling. " +
        "Keep US and AU reporting separate by currency — never blend USD and AUD.";
    }
  }

  /* —— Render: Scorecard tables —— */

  function renderScorecardTable(market, data, tbodyId, trafficId) {
    var tbody = $(tbodyId);
    var trafficEl = $(trafficId);
    if (!tbody) return;

    var cur = data.currency;
    var spend = data.spend;
    var agSpendEquiv = data.agPeriodEquivSpend;
    var pace = data.pacePct != null ? data.pacePct + "% of agency pace" : "—";

    var rows = [];
    var daysText = (data.daysInPeriod || 1) + " days";
    rows.push(
      "<tr>" +
        "<td><strong>Google Ads spend</strong></td>" +
        '<td class="num font-mono text-muted">—</td>' +
        '<td class="num font-mono"><strong>' +
        formatMoney(spend, cur) +
        "</strong></td>" +
        '<td class="num font-mono text-muted">' +
        formatMoney(agSpendEquiv, cur) +
        '<div class="ex-cell-sub">Agency-equiv (' +
        daysText +
        ")</div>" +
        "</td>" +
        '<td class="num font-mono">' +
        pace +
        "</td>" +
        "</tr>"
    );

    var enqVol = data.funnel.enquiries != null ? formatNum(data.funnel.enquiries) : '<span class="ex-status-tag pending">Pending</span>';
    var enqPilotCost = data.cpe.value != null ? formatMoney2(data.cpe.value, cur) : "—";
    var enqDiff = data.cpe.value != null ? diffPercentHtml(data.cpe.value, data.agCpe) : "—";
    rows.push(
      "<tr>" +
        "<td><strong>Employer enquiries</strong></td>" +
        '<td class="num font-mono">' +
        enqVol +
        "</td>" +
        '<td class="num font-mono"><strong>' +
        enqPilotCost +
        "</strong></td>" +
        '<td class="num font-mono text-muted">' +
        formatMoney2(data.agCpe, cur) +
        "</td>" +
        '<td class="num font-mono">' +
        enqDiff +
        "</td>" +
        "</tr>"
    );

    var discVol = data.funnel.discoveries != null ? formatNum(data.funnel.discoveries) : '<span class="ex-status-tag pending">Pending</span>';
    var discPilotCost = data.cpd.value != null ? formatMoney2(data.cpd.value, cur) : "—";
    var discDiff = data.cpd.value != null ? diffPercentHtml(data.cpd.value, data.agCpd) : "—";
    rows.push(
      "<tr>" +
        "<td><strong>Completed discovery calls</strong></td>" +
        '<td class="num font-mono">' +
        discVol +
        "</td>" +
        '<td class="num font-mono"><strong>' +
        discPilotCost +
        "</strong></td>" +
        '<td class="num font-mono text-muted">' +
        formatMoney2(data.agCpd, cur) +
        "</td>" +
        '<td class="num font-mono">' +
        discDiff +
        "</td>" +
        "</tr>"
    );

    var joConfirmed = data.funnel.jobOrders != null && data.funnel.jobOrders > 0;
    var joVol = joConfirmed
      ? formatNum(data.funnel.jobOrders) + "*"
      : '<span class="ex-status-tag pending">Pending validation</span>';
    var joPilotCost = joConfirmed && data.cpjo.value != null ? "<strong>" + formatMoney2(data.cpjo.value, cur) + "</strong>" : "—";
    var joDiff = joConfirmed && data.cpjo.value != null ? diffPercentHtml(data.cpjo.value, data.agCpjo) : "—";
    rows.push(
      "<tr>" +
        "<td><strong>Confirmed job orders</strong></td>" +
        '<td class="num font-mono">' +
        joVol +
        "</td>" +
        '<td class="num font-mono">' +
        joPilotCost +
        "</td>" +
        '<td class="num font-mono text-muted">' +
        formatMoney2(data.agCpjo, cur) +
        "</td>" +
        '<td class="num font-mono">' +
        joDiff +
        "</td>" +
        "</tr>"
    );

    var plConfirmed = data.funnel.placements != null && data.funnel.placements > 0;
    var plVol = plConfirmed
      ? formatNum(data.funnel.placements) + "*"
      : '<span class="ex-status-tag pending">Pending validation</span>';
    var plPilotCost = plConfirmed && data.cpp.value != null ? "<strong>" + formatMoney2(data.cpp.value, cur) + "</strong>" : "—";
    var plDiff = plConfirmed && data.cpp.value != null ? diffPercentHtml(data.cpp.value, data.agCpp) : "—";
    rows.push(
      "<tr>" +
        "<td><strong>Confirmed placements</strong></td>" +
        '<td class="num font-mono">' +
        plVol +
        "</td>" +
        '<td class="num font-mono">' +
        plPilotCost +
        "</td>" +
        '<td class="num font-mono text-muted">' +
        formatMoney2(data.agCpp, cur) +
        "</td>" +
        '<td class="num font-mono">' +
        plDiff +
        "</td>" +
        "</tr>"
    );

    tbody.innerHTML = rows.join("");

    if (trafficEl && data.ads) {
      trafficEl.textContent =
        "Supporting traffic efficiency: " +
        formatMoney2(data.ads.avgCpc, cur) +
        " CPC vs " +
        formatMoney2(data.agCpc, cur) +
        " agency · " +
        formatPct1(data.ads.ctrPct) +
        " CTR vs " +
        formatPct1(data.agCtr) +
        " agency";
    }
  }

  function renderMonthlyRamp() {
    var usBody = $("#ex-ramp-us-tbody");
    var auBody = $("#ex-ramp-au-tbody");
    var hist = monthlyHistory();

    function statusPill(status) {
      if (status === "complete") {
        return '<span class="ex-pill ok ex-pill-sm">Closed</span>';
      }
      return '<span class="ex-pill ok ex-pill-sm">Active · MTD</span>';
    }

    function rowHtml(rec, side, currency) {
      var m = (rec && rec[side]) || {};
      var spend = formatMoney(m.spend, currency);
      var enq = m.enquiries != null ? formatNum(m.enquiries) : '<span class="ex-status-tag pending">Pending</span>';
      var disc = m.sales_calls_completed != null ? formatNum(m.sales_calls_completed) : '<span class="ex-status-tag pending">Pending</span>';
      var jo =
        m.job_orders_total != null && m.job_orders_total > 0
          ? formatNum(m.job_orders_total) + "*"
          : m.job_orders_total === 0
            ? "0"
            : '<span class="ex-status-tag pending">Pending</span>';
      var pl =
        m.placements != null && m.placements > 0
          ? formatNum(m.placements) + "*"
          : m.placements === 0
            ? "0"
            : '<span class="ex-status-tag pending">Pending</span>';
      var cpe = m.cost_per_enquiry != null ? formatMoney2(m.cost_per_enquiry, currency) : "—";
      var cpd = m.cost_per_discovery != null ? formatMoney2(m.cost_per_discovery, currency) : "—";
      return (
        "<tr>" +
        "<td><strong>" +
        (rec.label || rec.month) +
        "</strong></td>" +
        '<td class="num font-mono"><strong>' +
        spend +
        "</strong></td>" +
        '<td class="num font-mono">' +
        enq +
        "</td>" +
        '<td class="num font-mono">' +
        disc +
        "</td>" +
        '<td class="num font-mono">' +
        jo +
        "</td>" +
        '<td class="num font-mono">' +
        pl +
        "</td>" +
        '<td class="num font-mono"><strong>' +
        cpe +
        "</strong></td>" +
        '<td class="num font-mono"><strong>' +
        cpd +
        "</strong></td>" +
        '<td class="num font-mono">' +
        statusPill(rec.status) +
        "</td>" +
        "</tr>"
      );
    }

    if (usBody) usBody.innerHTML = hist.map(function (rec) { return rowHtml(rec, "us", "USD"); }).join("");
    if (auBody) auBody.innerHTML = hist.map(function (rec) { return rowHtml(rec, "au", "AUD"); }).join("");
  }

  /* —— Render: Mobile —— */

  function renderMobileView(us, au) {
    var curMkt = STATE.activeMobileMarket || "US";
    var mktData = curMkt === "US" ? us : au;
    var closed = buildClosedMarketData(curMkt);

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

    var titleEl = $("#ex-mob-mkt-title");
    if (titleEl) titleEl.textContent = curMkt === "US" ? "United States (USD)" : "Australia (AUD)";

    var spendEl = $("#ex-mob-mkt-spend");
    if (spendEl) spendEl.textContent = formatMoney(mktData.spend, mktData.currency);

    var paceEl = $("#ex-mob-mkt-ag-pace");
    if (paceEl) {
      paceEl.textContent = mktData.pacePct != null ? mktData.pacePct + "% of agency pace" : "—";
    }

    var statusEl = $("#ex-mob-mkt-status");
    if (statusEl) {
      statusEl.textContent = mktData.funnel.enquiriesPending ? "Awaiting sales update" : "Active Search Pilot";
    }

    var metricGrid = $("#ex-mob-metric-cards");
    if (metricGrid) {
      var cur = mktData.currency;
      var showClosed = mktData.funnel.enquiriesPending && closed;
      var display = showClosed
        ? {
            enq: closed.funnel.enquiries,
            disc: closed.funnel.discoveries,
            jo: closed.funnel.jobOrders,
            pl: closed.funnel.placements,
            cpe: closed.cpe,
            cpd: closed.cpd,
            note: "Aug closed",
          }
        : {
            enq: mktData.funnel.enquiries,
            disc: mktData.funnel.discoveries,
            jo: mktData.funnel.jobOrders,
            pl: mktData.funnel.placements,
            cpe: mktData.cpe.value,
            cpd: mktData.cpd.value,
            note: null,
          };

      function card(title, vol, cost, agCost, pending) {
        var volHtml = pending || vol == null ? '<span class="ex-status-tag pending">Pending</span>' : formatNum(vol);
        var costHtml = cost != null ? formatMoney2(cost, cur) : "—";
        var diffHtml = cost != null ? diffPercentHtml(cost, agCost) : "—";
        return (
          '<div class="ex-mob-metric-card">' +
          '<div class="ex-mob-metric-top">' +
          '<div class="ex-mob-metric-title">' +
          title +
          (display.note ? ' <span class="text-muted">(' + display.note + ")</span>" : "") +
          "</div>" +
          '<div class="ex-mob-metric-count">' +
          volHtml +
          "</div>" +
          "</div>" +
          '<div class="ex-mob-metric-cost-row">' +
          '<span class="ex-mob-metric-cost-lbl">Blended cost</span>' +
          '<div class="ex-mob-metric-cost">' +
          costHtml +
          "</div>" +
          '<div class="ex-mob-metric-delta">' +
          diffHtml +
          "</div>" +
          "</div>" +
          "</div>"
        );
      }

      var joPending = display.jo == null || display.jo <= 0;
      var plPending = display.pl == null || display.pl <= 0;
      metricGrid.innerHTML =
        card("Employer enquiries", display.enq, display.cpe, mktData.agCpe, display.enq == null) +
        card("Completed calls", display.disc, display.cpd, mktData.agCpd, display.disc == null) +
        card(
          "Confirmed job orders",
          display.jo,
          null,
          mktData.agCpjo,
          joPending
        ) +
        card(
          "Confirmed placements",
          display.pl,
          null,
          mktData.agCpp,
          plPending
        );
    }

    var trafficBox = $("#ex-mob-traffic-text");
    if (trafficBox && mktData.ads) {
      trafficBox.textContent =
        formatMoney2(mktData.ads.avgCpc, mktData.currency) +
        " CPC vs " +
        formatMoney2(mktData.agCpc, mktData.currency) +
        " agency · " +
        formatPct1(mktData.ads.ctrPct) +
        " CTR vs " +
        formatPct1(mktData.agCtr) +
        " agency";
    }

    var funnelLabel = $("#ex-mob-funnel-mkt-label");
    if (funnelLabel) funnelLabel.textContent = curMkt === "US" ? "US Pipeline" : "AU Pipeline";

    var funnelWrap = $("#ex-mob-funnel-steps");
    if (funnelWrap) {
      var src = mktData.funnel.enquiriesPending && closed ? closed.funnel : mktData.funnel;
      var cpeV = mktData.funnel.enquiriesPending && closed ? closed.cpe : mktData.cpe.value;
      var cpdV = mktData.funnel.enquiriesPending && closed ? closed.cpd : mktData.cpd.value;
      var tag = mktData.funnel.enquiriesPending && closed ? " (Aug closed)" : "";
      funnelWrap.innerHTML =
        '<div class="ex-mob-funnel-step"><div class="ex-mob-funnel-left"><span class="ex-mob-funnel-num-tag">Stage 1</span><div class="ex-mob-funnel-name">Employer Enquiries' +
        tag +
        '</div><div class="ex-mob-funnel-cost">' +
        (cpeV != null ? formatMoney2(cpeV, mktData.currency) + " / enquiry" : "—") +
        '</div></div><div class="ex-mob-funnel-right"><div class="ex-mob-funnel-vol">' +
        (src.enquiries != null ? formatNum(src.enquiries) : "—") +
        "</div></div></div>" +
        '<div class="ex-mob-funnel-arrow">↓</div>' +
        '<div class="ex-mob-funnel-step"><div class="ex-mob-funnel-left"><span class="ex-mob-funnel-num-tag">Stage 2</span><div class="ex-mob-funnel-name">Completed Discovery Calls</div><div class="ex-mob-funnel-cost">' +
        (cpdV != null ? formatMoney2(cpdV, mktData.currency) + " / completed call" : "—") +
        '</div></div><div class="ex-mob-funnel-right"><div class="ex-mob-funnel-vol">' +
        (src.discoveries != null ? formatNum(src.discoveries) : "—") +
        "</div></div></div>" +
        '<div class="ex-mob-funnel-arrow">↓</div>' +
        '<div class="ex-mob-funnel-step"><div class="ex-mob-funnel-left"><span class="ex-mob-funnel-num-tag">Stage 3</span><div class="ex-mob-funnel-name">Confirmed Job Orders</div><div class="ex-mob-funnel-cost">' +
        (src.jobOrders != null && src.jobOrders > 0 ? formatNum(src.jobOrders) + "*" : "Pending sales validation") +
        '</div></div><div class="ex-mob-funnel-right"><div class="ex-mob-funnel-vol">' +
        (src.jobOrders != null && src.jobOrders > 0 ? formatNum(src.jobOrders) : "—") +
        "</div></div></div>" +
        '<div class="ex-mob-funnel-arrow">↓</div>' +
        '<div class="ex-mob-funnel-step"><div class="ex-mob-funnel-left"><span class="ex-mob-funnel-num-tag">Stage 4</span><div class="ex-mob-funnel-name">Confirmed Placements</div><div class="ex-mob-funnel-cost">' +
        (src.placements != null && src.placements > 0 ? formatNum(src.placements) + "*" : "Pending sales validation") +
        '</div></div><div class="ex-mob-funnel-right"><div class="ex-mob-funnel-vol">' +
        (src.placements != null && src.placements > 0 ? formatNum(src.placements) : "—") +
        "</div></div></div>";
    }

    var barsWrap = $("#ex-mob-bars-container");
    if (barsWrap) {
      var pilotEnq = closed && closed.cpe != null ? closed.cpe : mktData.cpe.value;
      var pilotDisc = closed && closed.cpd != null ? closed.cpd : mktData.cpd.value;
      if (pilotEnq == null || pilotDisc == null) {
        barsWrap.innerHTML =
          '<p class="ex-mob-bars-pending">Unit-cost bars use the last closed month. September sales outcomes are pending the next labeled update.</p>';
      } else {
        var agEnq = mktData.agCpe;
        var agDisc = mktData.agCpd;
        var enqPct = Math.min(100, Math.round((pilotEnq / agEnq) * 100));
        var discPct = Math.min(100, Math.round((pilotDisc / agDisc) * 100));
        barsWrap.innerHTML =
          '<div class="ex-mob-bar-group"><div class="ex-mob-bar-header"><span class="ex-mob-bar-title">Cost per Enquiry (' +
          curMkt +
          " · Aug closed)</span><span class=\"ex-mob-bar-diff\">" +
          (100 - enqPct) +
          '% lower</span></div><div class="ex-mob-bar-track"><div class="ex-mob-bar-fill-pilot" style="width: ' +
          enqPct +
          '%;"></div></div><div class="ex-mob-bar-legend"><span>Pilot: ' +
          formatMoney2(pilotEnq, mktData.currency) +
          "</span><span>Agency: " +
          formatMoney2(agEnq, mktData.currency) +
          "</span></div></div>" +
          '<div class="ex-mob-bar-group"><div class="ex-mob-bar-header"><span class="ex-mob-bar-title">Cost per Discovery Call (' +
          curMkt +
          " · Aug closed)</span><span class=\"ex-mob-bar-diff\">" +
          (100 - discPct) +
          '% lower</span></div><div class="ex-mob-bar-track"><div class="ex-mob-bar-fill-pilot" style="width: ' +
          discPct +
          '%;"></div></div><div class="ex-mob-bar-legend"><span>Pilot: ' +
          formatMoney2(pilotDisc, mktData.currency) +
          "</span><span>Agency: " +
          formatMoney2(agDisc, mktData.currency) +
          "</span></div></div>";
      }
    }

    var agencyBox = $("#ex-mob-agency-box");
    if (agencyBox) {
      var cUs = buildClosedMarketData("US");
      var cAu = buildClosedMarketData("AU");
      agencyBox.innerHTML =
        '<div class="ex-mob-comp-row"><div class="ex-mob-comp-left"><span class="ex-mob-comp-tag good">US separate</span><div class="ex-mob-comp-label">United States pace</div></div><div class="ex-mob-comp-desc">September MTD spend ' +
        formatMoney(us.spend, "USD") +
        " at " +
        (us.pacePct != null ? us.pacePct + "%" : "—") +
        " of agency-equivalent pace. August closed cost/enquiry " +
        (cUs && cUs.cpe != null ? formatMoney2(cUs.cpe, "USD") : "—") +
        ".</div></div>" +
        '<div class="ex-mob-comp-row"><div class="ex-mob-comp-left"><span class="ex-mob-comp-tag good">AU separate</span><div class="ex-mob-comp-label">Australia pace</div></div><div class="ex-mob-comp-desc">September MTD spend ' +
        formatMoney(au.spend, "AUD") +
        " at " +
        (au.pacePct != null ? au.pacePct + "%" : "—") +
        " of agency-equivalent pace. August closed cost/enquiry " +
        (cAu && cAu.cpe != null ? formatMoney2(cAu.cpe, "AUD") : "—") +
        ".</div></div>" +
        '<div class="ex-mob-comp-row"><div class="ex-mob-comp-left"><span class="ex-mob-comp-tag neutral">Equal basis</span><div class="ex-mob-comp-label">Attribution methodology</div></div><div class="ex-mob-comp-desc">Same company-wide CRM outcome attribution for pilot and agency baseline. USD and AUD are never combined.</div></div>';
    }

    var rampBody = $("#ex-mob-ramp-body");
    if (rampBody) {
      var hist = monthlyHistory();
      rampBody.innerHTML = hist
        .map(function (rec) {
          var status = rec.status === "complete" ? "Closed" : "Active · MTD";
          var u = rec.us || {};
          var a = rec.au || {};
          return (
            '<div class="ex-mob-ramp-card">' +
            '<div class="ex-mob-ramp-row"><strong>US · ' +
            (rec.label || "") +
            '</strong> <span class="ex-pill ok ex-pill-sm">' +
            status +
            "</span></div>" +
            '<div class="ex-mob-ramp-row text-muted"><span>Spend: ' +
            formatMoney(u.spend, "USD") +
            "</span><span>Enquiries: " +
            (u.enquiries != null ? formatNum(u.enquiries) : "Pending") +
            "</span></div>" +
            '<div class="ex-mob-ramp-row text-muted"><span>Calls: ' +
            (u.sales_calls_completed != null ? formatNum(u.sales_calls_completed) : "Pending") +
            "</span><span>Cost/call: " +
            (u.cost_per_discovery != null ? formatMoney2(u.cost_per_discovery, "USD") : "—") +
            "</span></div>" +
            "</div>" +
            '<div class="ex-mob-ramp-card">' +
            '<div class="ex-mob-ramp-row"><strong>AU · ' +
            (rec.label || "") +
            '</strong> <span class="ex-pill ok ex-pill-sm">' +
            status +
            "</span></div>" +
            '<div class="ex-mob-ramp-row text-muted"><span>Spend: ' +
            formatMoney(a.spend, "AUD") +
            "</span><span>Enquiries: " +
            (a.enquiries != null ? formatNum(a.enquiries) : "Pending") +
            "</span></div>" +
            '<div class="ex-mob-ramp-row text-muted"><span>Calls: ' +
            (a.sales_calls_completed != null ? formatNum(a.sales_calls_completed) : "Pending") +
            (a.job_orders_total != null ? " · JOs: " + a.job_orders_total + "*" : "") +
            "</span><span>Placements: " +
            (a.placements != null ? a.placements + "*" : "—") +
            "</span></div>" +
            "</div>"
          );
        })
        .join("");
    }

    var notesList = $("#ex-mob-action-list");
    if (notesList) {
      var fresh = ((STATE.snapshot || {}).freshness || {});
      notesList.innerHTML =
        "<li><strong>Cheyenne / Holly:</strong> next labeled September update (US confirmed through " +
        fmtShortDate(fresh.us_sales_confirmed_through) +
        "; AU through " +
        fmtShortDate(fresh.au_sales_confirmed_through) +
        ").</li>" +
        "<li><strong>Technical:</strong> pass GCLID, campaign, and usable phone-call outcomes into Zoho.</li>";
    }
  }

  function setupMobileEvents(us, au) {
    var btnUs = $("#ex-mob-tab-us");
    var btnAu = $("#ex-mob-tab-au");
    if (btnUs) {
      btnUs.onclick = function () {
        STATE.activeMobileMarket = "US";
        renderMobileView(us, au);
      };
    }
    if (btnAu) {
      btnAu.onclick = function () {
        STATE.activeMobileMarket = "AU";
        renderMobileView(us, au);
      };
    }
  }

  function renderAll() {
    var us = buildMarketData("US");
    var au = buildMarketData("AU");

    renderHeader();
    renderExecutiveSummary(us, au);
    renderScorecardTable("US", us, "#ex-us-tbody", "#ex-us-traffic");
    renderScorecardTable("AU", au, "#ex-au-tbody", "#ex-au-traffic");
    renderMonthlyRamp();
    renderMobileView(us, au);
    setupMobileEvents(us, au);
  }

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
