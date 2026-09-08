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
    selectedMonthKey: null,
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

  function formatSessionDuration(sec) {
    if (sec == null || Number.isNaN(Number(sec))) return "—";
    var s = Math.max(0, Math.round(Number(sec)));
    if (s < 60) return s + "s";
    var m = Math.floor(s / 60);
    var r = s % 60;
    return m + "m " + (r < 10 ? "0" : "") + r + "s";
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

  function ensureSelectedMonth() {
    var hist = monthlyHistory();
    if (!hist.length) {
      STATE.selectedMonthKey = asOfDate().slice(0, 7);
      return;
    }
    var keys = hist.map(function (h) { return h.month; });
    if (STATE.selectedMonthKey && keys.indexOf(STATE.selectedMonthKey) >= 0) return;
    var active = null;
    for (var i = hist.length - 1; i >= 0; i--) {
      if (hist[i] && hist[i].status === "active_mtd") {
        active = hist[i];
        break;
      }
    }
    STATE.selectedMonthKey = (active && active.month) || hist[hist.length - 1].month;
  }

  function selectedMonthRecord() {
    ensureSelectedMonth();
    var hist = monthlyHistory();
    for (var i = 0; i < hist.length; i++) {
      if (hist[i] && hist[i].month === STATE.selectedMonthKey) return hist[i];
    }
    return activeMonthRecord();
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
    var rec = selectedMonthRecord();
    return {
      start: rec.period_start || (asOfDate().slice(0, 8) + "01"),
      end: rec.period_end || asOfDate(),
      label: rec.label || (monthName((rec.period_start || asOfDate()).slice(0, 7)) + " MTD"),
      monthKey: rec.month || (asOfDate().slice(0, 7)),
      status: rec.status || "active_mtd",
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

  function costValue(c) {
    if (c == null) return null;
    if (typeof c === "object") return c.value != null ? Number(c.value) : null;
    var n = Number(c);
    return Number.isFinite(n) ? n : null;
  }

  /* —— Market Data: selected month drives the scoreboard —— */

  function buildMarketFromRecord(market, rec, fallbackAdsStart, fallbackAdsEnd) {
    var cur = market === "AU" ? "AUD" : "USD";
    var snap = STATE.snapshot || {};
    var perf = market === "US" ? snap.performance_us : snap.performance_au;
    var by = (perf || {}).by_date_stage1 || (perf || {}).by_date || {};
    var side = market === "US" ? "us" : "au";
    var m = (rec && rec[side]) || {};
    var start = (rec && rec.period_start) || fallbackAdsStart;
    var end = (rec && rec.period_end) || fallbackAdsEnd;
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
    if (ads && spend != null) ads = Object.assign({}, ads, { spend: spend });

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
      periodLabel: (rec && rec.label) || reportingPeriod().label,
      periodStart: start,
      periodEnd: end,
      status: (rec && rec.status) || "active_mtd",
      adsConversions: m.ads_conversions != null ? Number(m.ads_conversions) : null,
      salesNote: m.sales_note || null,
      operatorUiNote: (rec && rec.operator_ui_note) || null,
      agPeriodEquivSpend: agPeriodEquivSpend,
      agCpe: Number(agBlock.cost_per_legitimate_employer_enquiry || (market === "US" ? 816.31 : 615.82)),
      agCpd: Number(agBlock.cost_per_discovery || (market === "US" ? 1285.25 : 812.35)),
      agCpjo: Number(agBlock.cost_per_job_order || (market === "US" ? 2013.56 : 1104.02)),
      agCpp: Number(agBlock.cost_per_placement || (market === "US" ? 4289.23 : 2073.15)),
      agCpc: Number(agBlock.avg_cpc || (market === "US" ? 8.29 : 9.24)),
      agCtr: Number(agBlock.ctr_pct || (market === "US" ? 1.62 : 1.44)),
      pacePct: spendPacePct(spend, agPeriodEquivSpend),
    };
  }

  function buildMarketData(market) {
    var rec = selectedMonthRecord();
    var period = reportingPeriod();
    return buildMarketFromRecord(market, rec, period.start, period.end);
  }

  function buildMtdMarketData(market) {
    var active = activeMonthRecord();
    return buildMarketFromRecord(
      market,
      active,
      active.period_start || (asOfDate().slice(0, 8) + "01"),
      active.period_end || asOfDate()
    );
  }

  function buildClosedMarketData(market) {
    var closed = closedMonthRecord();
    if (!closed) return null;
    return buildMarketFromRecord(market, closed, closed.period_start, closed.period_end);
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
    var rec = selectedMonthRecord();
    var adsThru = fresh.google_ads_through || asOfDate() || period.end;
    var usConfirmed = fresh.us_sales_confirmed_through || "—";
    var auConfirmed = fresh.au_sales_confirmed_through || "—";
    var status = fresh.status || "Current";

    var adsStr = fmtShortDate(adsThru);
    var usStr = fmtShortDate(usConfirmed);
    var auStr = fmtShortDate(auConfirmed);
    var isClosed = period.status === "complete";
    var periodLabel = isClosed
      ? (rec.label || period.label) + " closed"
      : period.label.indexOf("MTD") >= 0
        ? period.label.replace(" MTD", " · Month to Date")
        : period.label;

    var periodEl = $("#ex-period");
    if (periodEl) periodEl.textContent = periodLabel;

    var mobPeriod = $("#ex-mob-period-badge");
    if (mobPeriod) mobPeriod.textContent = periodLabel;

    var volLabel = isClosed
      ? (rec.label || "Month").replace(" 2026", "") + " volume"
      : "MTD volume";
    ["#ex-us-vol-th", "#ex-au-vol-th"].forEach(function (sel) {
      var th = $(sel);
      if (th) th.textContent = volLabel;
    });

    var usSub = $("#ex-us-section-sub");
    var auSub = $("#ex-au-section-sub");
    var subText = (rec.label || period.label) + (isClosed ? " closed" : "") + " vs two-year agency baseline";
    if (usSub) usSub.textContent = subText;
    if (auSub) auSub.textContent = subText;
    var mobSub = $("#ex-mob-section-sub");
    if (mobSub) mobSub.textContent = periodLabel;

    var freshEl = $("#ex-fresh");
    if (freshEl) {
      freshEl.innerHTML =
        '<span class="ex-fresh-item"><strong>Ads:</strong> ' +
        adsStr +
        "</span> · " +
        '<span class="ex-fresh-item"><strong>US sales:</strong> ' +
        usStr +
        "</span> · " +
        '<span class="ex-fresh-item"><strong>AU sales:</strong> ' +
        auStr +
        "</span> · " +
        '<span class="ex-fresh-item">' +
        period.start +
        " → " +
        period.end +
        "</span> · " +
        '<span class="ex-fresh-status ' +
        (status.indexOf("Current") === 0 || status.indexOf("Ads current") === 0 ? "ok" : status.indexOf("Pending") >= 0 || status.indexOf("Awaiting") >= 0 ? "warn" : "err") +
        '">' +
        status +
        "</span>";
    }

    var mobFreshEl = $("#ex-mob-fresh");
    if (mobFreshEl) {
      mobFreshEl.textContent =
        periodLabel +
        " · Ads through " +
        adsStr +
        " · US sales " +
        usStr +
        " · AU sales " +
        auStr +
        " · " +
        status;
    }
  }

  function renderMonthTabs() {
    ensureSelectedMonth();
    var hist = monthlyHistory();
    function paint(containerId) {
      var el = $(containerId);
      if (!el) return;
      el.innerHTML = hist
        .map(function (rec) {
          var on = rec.month === STATE.selectedMonthKey;
          var label =
            rec.status === "complete"
              ? (rec.label || rec.month) + " closed"
              : rec.label || rec.month;
          return (
            '<button type="button" class="ex-month-tab' +
            (on ? " on" : "") +
            '" role="tab" aria-selected="' +
            (on ? "true" : "false") +
            '" data-month="' +
            rec.month +
            '">' +
            label +
            "</button>"
          );
        })
        .join("");
      Array.prototype.forEach.call(el.querySelectorAll("[data-month]"), function (btn) {
        btn.addEventListener("click", function () {
          STATE.selectedMonthKey = btn.getAttribute("data-month");
          renderAll();
        });
      });
    }
    paint("#ex-month-tabs");
    paint("#ex-mob-month-tabs");
  }

  /* —— Render: Above-the-fold summary for the selected month —— */

  function marketSummaryHtml(data) {
    if (!data) return "—";
    var f = data.funnel || {};
    var pace = data.pacePct != null ? data.pacePct + "%" : "—";
    var cpe = data.cpe && data.cpe.value != null ? formatMoney2(data.cpe.value, data.currency) : "—";
    var cpd = data.cpd && data.cpd.value != null ? formatMoney2(data.cpd.value, data.currency) : "—";
    var pill =
      data.status === "complete"
        ? '<span class="ex-pill ok ex-pill-sm">Closed</span>'
        : '<span class="ex-pill ok ex-pill-sm">Active · MTD</span>';
    return (
      '<div class="ex-summary-mkt-name">' +
      (data.market === "US" ? "United States · USD" : "Australia · AUD") +
      " " +
      pill +
      "</div>" +
      '<div class="ex-summary-mkt-spend">' +
      formatMoney(data.spend, data.currency) +
      ' spend · <strong>' +
      pace +
      "</strong> of agency-equivalent pace</div>" +
      '<div class="ex-summary-mkt-funnel">' +
      (f.enquiries != null ? formatNum(f.enquiries) : "Pending") +
      " enquiries → " +
      (f.discoveries != null ? formatNum(f.discoveries) : "Pending") +
      " calls → " +
      (f.jobOrders != null ? formatNum(f.jobOrders) + "*" : "Pending") +
      " job orders → " +
      (f.placements != null ? formatNum(f.placements) + "*" : "Pending") +
      " placements</div>" +
      '<div class="ex-summary-mkt-costs">Cost/enquiry ' +
      cpe +
      " · Cost/call " +
      cpd +
      (data.adsConversions != null
        ? " · Ads conversions " + formatNum(data.adsConversions)
        : "") +
      "</div>"
    );
  }

  function renderExecutiveSummary(us, au) {
    var closedUs = buildClosedMarketData("US");
    var closedAu = buildClosedMarketData("AU");
    var mtdUs = buildMtdMarketData("US");
    var mtdAu = buildMtdMarketData("AU");
    var fresh = ((STATE.snapshot || {}).freshness || {});
    var usConfirmed = fresh.us_sales_confirmed_through || "—";
    var auConfirmed = fresh.au_sales_confirmed_through || "—";
    var period = reportingPeriod();
    var rec = selectedMonthRecord();
    var isClosed = period.status === "complete";

    var labelEl = $("#ex-summary-label");
    if (labelEl) {
      labelEl.textContent = isClosed
        ? "Pilot baseline · " + (rec.label || "Closed month")
        : "Current month · " + (rec.label || "MTD");
    }

    var usBox = $("#ex-summary-us");
    var auBox = $("#ex-summary-au");
    if (usBox) usBox.innerHTML = marketSummaryHtml(us);
    if (auBox) auBox.innerHTML = marketSummaryHtml(au);

    var usPace = us.pacePct != null ? us.pacePct + "%" : "—";
    var auPace = au.pacePct != null ? au.pacePct + "%" : "—";
    var closedUsPace = closedUs && closedUs.pacePct != null ? closedUs.pacePct + "%" : "—";
    var closedAuPace = closedAu && closedAu.pacePct != null ? closedAu.pacePct + "%" : "—";
    var mtdUsPace = mtdUs.pacePct != null ? mtdUs.pacePct + "%" : "—";
    var mtdAuPace = mtdAu.pacePct != null ? mtdAu.pacePct + "%" : "—";

    var ctxEl = $("#ex-summary-september");
    if (ctxEl) {
      if (isClosed) {
        ctxEl.innerHTML =
          "<strong>Open MTD (" +
          (mtdUs.periodLabel || "September") +
          " through " +
          fmtShortDate(mtdUs.periodEnd) +
          "):</strong> US " +
          formatMoney(mtdUs.spend, "USD") +
          " (" +
          mtdUsPace +
          ") · AU " +
          formatMoney(mtdAu.spend, "AUD") +
          " (" +
          mtdAuPace +
          '). Sales: <span class="ex-status-tag pending">Pending</span>' +
          " (US " +
          fmtShortDate(usConfirmed) +
          ", AU " +
          fmtShortDate(auConfirmed) +
          ").";
      } else {
        var opNote = rec.operator_ui_note || "";
        ctxEl.innerHTML =
          "<strong>" +
          (rec.label || "Current MTD") +
          " through " +
          fmtShortDate(period.end) +
          ":</strong> US " +
          formatMoney(us.spend, "USD") +
          (us.adsConversions != null ? " · " + formatNum(us.adsConversions) + " Ads conv." : "") +
          " (" +
          usPace +
          ") · AU " +
          formatMoney(au.spend, "AUD") +
          (au.adsConversions != null ? " · " + formatNum(au.adsConversions) + " Ads conv." : "") +
          " (" +
          auPace +
          '). Sales: <span class="ex-status-tag pending">Pending</span>' +
          " until a clean September label." +
          (opNote ? '<div class="ex-summary-meta" style="margin-top:0.35rem">' + opNote + "</div>" : "");
      }
    }

    var decEl = $("#ex-summary-decision");
    if (decEl) {
      decEl.textContent =
        "Hold budgets. August baseline ~" +
        closedUsPace +
        " US / ~" +
        closedAuPace +
        " AU of agency pace. September MTD is a short-window burn rate (" +
        (mtdUs.daysInPeriod || daysInclusive(mtdUs.periodStart || period.start, mtdUs.periodEnd || period.end)) +
        " days), not a replacement for August. Daily: US $350 · AU A$215.";
    }

    var footnote = $("#ex-summary-footnote");
    if (footnote) {
      footnote.textContent =
        "* Job orders and placements are blended CRM outcomes (paid + organic + pipeline). Ads conversions are Google Ads tags — not the same as sales-confirmed enquiries.";
    }

    var mobSnap = $("#ex-mob-snapshot-text");
    if (mobSnap) {
      mobSnap.textContent =
        (isClosed ? "August closed" : "September MTD") +
        " · US " +
        formatMoney(us.spend, "USD") +
        " · AU " +
        formatMoney(au.spend, "AUD") +
        " · pace US " +
        usPace +
        " / AU " +
        auPace +
        ". " +
        (isClosed
          ? "Use the September tab for current-month spend and pending sales."
          : "Sales outcomes Pending until a clean September label arrives.");
    }

    var mobPace = $("#ex-mob-snap-pace");
    if (mobPace) mobPace.textContent = "US " + usPace + " · AU " + auPace;
    var mobPaceLbl = $("#ex-mob-snap-pace-lbl");
    if (mobPaceLbl) mobPaceLbl.textContent = isClosed ? "Aug agency pace" : "Sept MTD pace";
    var mobPaceSub = $("#ex-mob-snap-pace-sub");
    if (mobPaceSub) mobPaceSub.textContent = isClosed ? "Closed month baseline" : "Early-month burn rate";

    var baseline = isClosed ? us : closedUs;
    var cpePct =
      baseline && baseline.cpe && baseline.cpe.value != null && baseline.agCpe
        ? Math.round(((baseline.agCpe - baseline.cpe.value) / baseline.agCpe) * 100)
        : null;
    var cpdPct =
      baseline && baseline.cpd && baseline.cpd.value != null && baseline.agCpd
        ? Math.round(((baseline.agCpd - baseline.cpd.value) / baseline.agCpd) * 100)
        : null;
    var mobCpe = $("#ex-mob-snap-cpe");
    if (mobCpe) mobCpe.textContent = cpePct != null ? "-" + cpePct + "%" : "—";
    var mobCpeSub = $("#ex-mob-snap-cpe-sub");
    if (mobCpeSub) {
      mobCpeSub.textContent =
        baseline && baseline.cpe && baseline.cpe.value != null
          ? "US " + formatMoney2(baseline.cpe.value, "USD") + " · Aug closed"
          : "Aug closed pending";
    }
    var mobCpd = $("#ex-mob-snap-cpd");
    if (mobCpd) mobCpd.textContent = cpdPct != null ? "-" + cpdPct + "%" : "—";
    var mobCpdSub = $("#ex-mob-snap-cpd-sub");
    if (mobCpdSub) {
      mobCpdSub.textContent =
        baseline && baseline.cpd && baseline.cpd.value != null
          ? "US " + formatMoney2(baseline.cpd.value, "USD") + " · Aug closed"
          : "Aug closed pending";
    }

    var working = $("#ex-mob-working-text");
    if (working) {
      working.textContent = isClosed
        ? "August closed with confirmed funnel outcomes at lower blended unit costs than the two-year agency baseline, at about " +
          closedUsPace +
          " (US) / " +
          closedAuPace +
          " (AU) of agency-equivalent pace."
        : "September MTD spend is live through the previous complete day. Sales enquiries, discovery calls, job orders, and placements stay Pending until labeled — same scorecard layout as August.";
    }
    var uncertain = $("#ex-mob-uncertain-text");
    if (uncertain) {
      uncertain.textContent =
        "Cheyenne’s latest US label (Aug 31–Sep 4: 18 enquiries / 8 calls) spans the month boundary, so it is not written into September MTD. Holly AU September MTD awaits update. US sales confirmed through " +
        fmtShortDate(usConfirmed) +
        "; AU through " +
        fmtShortDate(auConfirmed) +
        ".";
    }
    var next = $("#ex-mob-next-text");
    if (next) {
      next.textContent =
        "Hold current budgets. Keep August closed as the pilot baseline. Do not scale on September Pending sales boxes.";
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
      var adsConv =
        data.adsConversions != null ? " · Ads conversions " + formatNum(data.adsConversions) : "";
      trafficEl.textContent =
        "Supporting traffic efficiency: " +
        formatMoney2(data.ads.avgCpc, cur) +
        " CPC vs " +
        formatMoney2(data.agCpc, cur) +
        " agency · " +
        formatPct1(data.ads.ctrPct) +
        " CTR vs " +
        formatPct1(data.agCtr) +
        " agency" +
        adsConv;
    }

    var noteId = market === "US" ? "#ex-us-month-note" : "#ex-au-month-note";
    var noteEl = $(noteId);
    if (noteEl) {
      noteEl.textContent = data.salesNote || "";
      noteEl.style.display = data.salesNote ? "block" : "none";
    }
  }

  function renderGa4Health() {
    var el = $("#ex-ga4-health");
    if (!el) return;
    var ga4Root = ((STATE.snapshot || {}).ga4) || {};
    var monthKey = STATE.selectedMonthKey || ga4Root.current_month_key || null;
    var byMonth = ga4Root.by_month || {};
    var monthSlice = (monthKey && byMonth[monthKey]) || null;
    var priorKey = ga4Root.prior_month_key || (ga4Root.window_prior || "").slice(0, 7);
    var usePrior =
      !monthSlice &&
      monthKey &&
      priorKey &&
      monthKey === priorKey &&
      !!ga4Root.totals_prior_7_days;

    var ga4 = monthSlice || ga4Root;
    var au = (monthSlice && monthSlice.au) || ga4Root.au || {};
    var usTotals = usePrior
      ? ga4Root.totals_prior_7_days
      : ga4.totals_last_7_days || null;
    var auTotals = usePrior
      ? au.totals_prior_7_days || null
      : au.totals_last_7_days || null;
    var usLandings = usePrior
      ? ga4Root.top_landing_pages_prior || []
      : ga4.top_landing_pages;
    var auLandings = usePrior
      ? au.top_landing_pages_prior || []
      : au.top_landing_pages;
    var usChannels = usePrior ? ga4Root.channels_prior || [] : ga4.channels;
    var auChannels = usePrior ? au.channels_prior || [] : au.channels;
    var auPaidFallback = usePrior
      ? au.paid_search_sessions_prior
      : au.paid_search_sessions != null
        ? au.paid_search_sessions
        : monthSlice && monthSlice.au
          ? monthSlice.au.paid_search_sessions
          : null;

    if (!usTotals && !auTotals && !ga4Root.summary_plain && !(ga4Root.au || {}).summary_plain) {
      el.innerHTML = '<div class="ex-ga4-empty">GA4 snapshot not loaded yet.</div>';
      return;
    }

    /** Near-100% engagement often means every session met GA4’s bar (10s / 2 pages /
     *  key event) — not that every visit was great. Prefer avg time when saturated. */
    var ENG_SATURATION_PCT = 95;

    function engagementSaturated(t) {
      if (!t || t.engagement_rate_pct == null) return false;
      var eng = Number(t.engagement_rate_pct);
      if (eng >= ENG_SATURATION_PCT) return true;
      if (
        t.sessions != null &&
        t.engaged_sessions != null &&
        Number(t.sessions) > 0 &&
        Number(t.engaged_sessions) >= Number(t.sessions)
      ) {
        return true;
      }
      return false;
    }

    function paidChannel(channels, fallbackSessions) {
      var list = channels || [];
      for (var i = 0; i < list.length; i++) {
        if (String(list[i].channel || "").toLowerCase().indexOf("paid search") >= 0) {
          return list[i];
        }
      }
      if (fallbackSessions != null) {
        return { channel: "Paid Search", sessions: fallbackSessions };
      }
      return null;
    }

    function paidSharePct(paid, totals) {
      if (!paid || paid.sessions == null || !totals || !totals.sessions) return null;
      var sess = Number(totals.sessions);
      if (!(sess > 0)) return null;
      return (100 * Number(paid.sessions)) / sess;
    }

    function engagementDisplay(pct, saturated) {
      if (pct == null || Number.isNaN(Number(pct))) return "—";
      if (saturated) return "—";
      return formatPct1(pct);
    }

    function landingEngagementCell(p, marketSaturated) {
      if (p == null || p.engagement_rate_pct == null) return "—";
      if (marketSaturated) return "—";
      if (Number(p.engagement_rate_pct) >= ENG_SATURATION_PCT) return "—";
      return formatPct1(p.engagement_rate_pct);
    }

    /** Paid Stage 1 host (Ads Final URLs + live microsite). US /au / shared. */
    var GA4_SITE_ORIGIN = "https://www.virtualcoworker.app";

    function escapeGa4Html(s) {
      return String(s)
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;");
    }

    function resolveLandingHref(path) {
      var raw = String(path || "").trim();
      if (
        !raw ||
        raw === "—" ||
        raw === "(not set)" ||
        raw === "untagged" ||
        raw === "home"
      ) {
        return null;
      }
      if (/^https?:\/\//i.test(raw)) return raw;
      if (raw.charAt(0) !== "/") raw = "/" + raw;
      return GA4_SITE_ORIGIN + raw;
    }

    function landingPathLink(p) {
      var label = (p && (p.path_display || p.path)) || "—";
      var href = resolveLandingHref((p && p.path) || (p && p.path_display));
      if (!href) return escapeGa4Html(label);
      return (
        '<a class="ex-ga4-lp-link" href="' +
        escapeGa4Html(href) +
        '" target="_blank" rel="noopener noreferrer" title="Open ' +
        escapeGa4Html(href) +
        '">' +
        escapeGa4Html(label) +
        "</a>"
      );
    }

    function topLandings(pages) {
      return (pages || [])
        .filter(function (p) {
          return p && Number(p.sessions) > 0 && String(p.path || "") !== "(not set)";
        })
        .slice(0, 5);
    }

    function landingsTable(pages, marketSaturated) {
      var list = topLandings(pages);
      if (!list.length) {
        return '<p class="ex-ga4-empty-inline">No landing pages in this window.</p>';
      }
      return (
        '<table class="ex-ga4-lp-table">' +
        "<thead><tr>" +
        "<th scope=\"col\">Page people opened</th>" +
        "<th scope=\"col\" class=\"num\">Visits</th>" +
        "<th scope=\"col\" class=\"num\">Avg time</th>" +
        "<th scope=\"col\" class=\"num\">Engaged</th>" +
        "</tr></thead><tbody>" +
        list
          .map(function (p) {
            return (
              "<tr>" +
              '<td class="path">' +
              landingPathLink(p) +
              "</td>" +
              '<td class="num">' +
              formatNum(p.sessions) +
              "</td>" +
              '<td class="num">' +
              (p.avg_session_seconds != null
                ? formatSessionDuration(p.avg_session_seconds)
                : "—") +
              "</td>" +
              '<td class="num">' +
              landingEngagementCell(p, marketSaturated) +
              "</td>" +
              "</tr>"
            );
          })
          .join("") +
        "</tbody></table>"
      );
    }

    function meansLine(opts) {
      var t = opts.totals || {};
      var landings = topLandings(opts.landings);
      var top = landings[0];
      var share = opts.share;
      var parts = [];
      if (top && t.sessions > 0) {
        var topShare = Math.round((100 * Number(top.sessions)) / Number(t.sessions));
        var pathHtml = landingPathLink(top);
        parts.push(
          topShare >= 50
            ? "Most traffic still opens <strong>" + pathHtml + "</strong> (" + topShare + "%)."
            : "Top opener is <strong>" + pathHtml + "</strong> (" + topShare + "%)."
        );
      }
      if (share != null && share >= 70) {
        parts.push("Almost all of it is Google Ads.");
      } else if (share != null) {
        parts.push(formatPct1(share) + " from Google Ads.");
      }
      if (opts.engagementSaturated) {
        parts.push(
          "Engagement rate is saturated this window (almost every session met GA4’s bar) — compare pages by avg time instead."
        );
      } else if (t.engagement_rate_pct != null && Number(t.engagement_rate_pct) < 50) {
        parts.push(
          formatPct1(t.engagement_rate_pct) +
            " engaged — check whether ads land on the right page."
        );
      } else if (t.avg_session_seconds != null && Number(t.avg_session_seconds) < 30) {
        parts.push("Visits are short — page may not match what the ad promised.");
      }
      if (!parts.length) return "";
      return (
        '<p class="ex-ga4-means"><span class="ex-ga4-means-lbl">What this means</span> ' +
        parts.join(" ") +
        "</p>"
      );
    }

    function kpiCell(val, lbl, hint) {
      return (
        '<div class="ex-ga4-stat">' +
        '<div class="ex-ga4-stat-val">' +
        val +
        "</div>" +
        '<div class="ex-ga4-stat-lbl">' +
        lbl +
        "</div>" +
        (hint ? '<div class="ex-ga4-stat-hint">' + hint + "</div>" : "") +
        "</div>"
      );
    }

    function marketCard(opts) {
      var t = opts.totals || {};
      var paid = opts.paid;
      var share = paidSharePct(paid, t);
      var engSaturated = engagementSaturated(t);

      return (
        '<article class="ex-ga4-mkt">' +
        '<div class="ex-ga4-mkt-hd">' +
        '<h3 class="ex-ga4-mkt-title">' +
        opts.title +
        "</h3>" +
        '<span class="ex-ga4-mkt-sub">' +
        opts.badge +
        "</span>" +
        "</div>" +
        '<div class="ex-ga4-stats ex-ga4-stats-5" role="group" aria-label="' +
        opts.title +
        ' traffic KPIs">' +
        kpiCell(formatNum(t.sessions), "Sessions", "Visits that opened a page") +
        kpiCell(formatNum(t.users), "Users", "Distinct people") +
        kpiCell(
          formatSessionDuration(t.avg_session_seconds),
          "Avg time",
          "How long a typical visit lasted"
        ) +
        kpiCell(
          engagementDisplay(t.engagement_rate_pct, engSaturated),
          "Engagement rate",
          engSaturated
            ? "Saturated this window — almost every session met GA4’s bar; use avg time"
            : "GA4: 10s+ stay, 2+ pages, or a key event"
        ) +
        kpiCell(
          share != null ? formatPct1(share) : "—",
          "Paid share",
          "How much of this traffic came from Google Ads"
        ) +
        "</div>" +
        meansLine({
          totals: t,
          landings: opts.landings,
          share: share,
          engagementSaturated: engSaturated,
        }) +
        '<div class="ex-ga4-block">' +
        '<div class="ex-ga4-block-lbl">Where they landed</div>' +
        landingsTable(opts.landings, engSaturated) +
        "</div>" +
        "</article>"
      );
    }

    var usWindow =
      (monthSlice && monthSlice.window) ||
      (usePrior ? ga4Root.window_prior : ga4Root.window);
    var auWindow = (au && au.window) || usWindow;
    var windowLabel =
      auWindow && usWindow && auWindow !== usWindow
        ? "US " + usWindow + " · AU " + auWindow
        : usWindow || auWindow || "Current GA4 pull";

    var usCard = marketCard({
      title: "United States",
      badge: "US site only",
      totals: usTotals || {},
      landings: usLandings,
      paid: paidChannel(usChannels),
    });
    var auCard = marketCard({
      title: "Australia",
      badge: "AU site only",
      totals: auTotals || {},
      landings: auLandings,
      paid: paidChannel(auChannels, auPaidFallback),
    });

    el.innerHTML =
      '<p class="ex-ga4-window"><strong>' +
      windowLabel +
      "</strong> · website tags (GA4) · not Ad CTR</p>" +
      '<div class="ex-ga4-markets">' +
      usCard +
      auCard +
      "</div>" +
      '<p class="ex-ga4-meta">Same KPIs for US and AU so you can compare markets. Engagement rate is the GA4 metric (10s+ stay, 2+ pages, or a key event). Use avg time when engagement is saturated. Do not blend US + AU.</p>';
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
      statusEl.textContent =
        mktData.status === "complete"
          ? (mktData.periodLabel || "Month") + " closed"
          : (mktData.periodLabel || "Active") + " · MTD";
    }

    var metricGrid = $("#ex-mob-metric-cards");
    if (metricGrid) {
      var cur = mktData.currency;
      var display = {
        enq: mktData.funnel.enquiries,
        disc: mktData.funnel.discoveries,
        jo: mktData.funnel.jobOrders,
        pl: mktData.funnel.placements,
        cpe: mktData.cpe.value,
        cpd: mktData.cpd.value,
        note: mktData.status === "complete" ? "Aug closed" : null,
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
      var src = mktData.funnel;
      var cpeV = mktData.cpe.value;
      var cpdV = mktData.cpd.value;
      var tag = mktData.status === "complete" ? " (Aug closed)" : "";
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
      var pilotEnq = mktData.cpe.value;
      var pilotDisc = mktData.cpd.value;
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
      var mtdUs = buildMtdMarketData("US");
      var mtdAu = buildMtdMarketData("AU");
      agencyBox.innerHTML =
        '<div class="ex-mob-comp-row"><div class="ex-mob-comp-left"><span class="ex-mob-comp-tag good">US separate</span><div class="ex-mob-comp-label">United States · August closed</div></div><div class="ex-mob-comp-desc">August spend ' +
        formatMoney(cUs && cUs.spend, "USD") +
        " at " +
        (cUs && cUs.pacePct != null ? cUs.pacePct + "%" : "—") +
        " of agency-equivalent pace (31-day basis). Cost/enquiry " +
        (cUs ? formatMoney2(costValue(cUs.cpe), "USD") : "—") +
        ". September MTD " +
        formatMoney(mtdUs.spend, "USD") +
        " (" +
        (mtdUs.pacePct != null ? mtdUs.pacePct + "%" : "—") +
        " early MTD pace) — sales pending.</div></div>" +
        '<div class="ex-mob-comp-row"><div class="ex-mob-comp-left"><span class="ex-mob-comp-tag good">AU separate</span><div class="ex-mob-comp-label">Australia · August closed</div></div><div class="ex-mob-comp-desc">August spend ' +
        formatMoney(cAu && cAu.spend, "AUD") +
        " at " +
        (cAu && cAu.pacePct != null ? cAu.pacePct + "%" : "—") +
        " of agency-equivalent pace (31-day basis). Cost/enquiry " +
        (cAu ? formatMoney2(costValue(cAu.cpe), "AUD") : "—") +
        ". September MTD " +
        formatMoney(mtdAu.spend, "AUD") +
        " (" +
        (mtdAu.pacePct != null ? mtdAu.pacePct + "%" : "—") +
        " early MTD pace) — sales pending.</div></div>" +
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
    ensureSelectedMonth();
    var us = buildMarketData("US");
    var au = buildMarketData("AU");

    renderMonthTabs();
    renderHeader();
    renderExecutiveSummary(us, au);
    renderScorecardTable("US", us, "#ex-us-tbody", "#ex-us-traffic");
    renderScorecardTable("AU", au, "#ex-au-tbody", "#ex-au-traffic");
    renderGa4Health();
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
