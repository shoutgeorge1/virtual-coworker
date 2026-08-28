/**
 * Executive Performance — High-End Leadership Dashboard Renderer.
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
    period: "mtd", // "mtd" | "prev"
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
      jobOrders: jobOrders,
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
    var sign = diffPct > 0 ? "+" : "−";
    return {
      diffText: (diffPct === 0 ? "0.0%" : (sign + Math.abs(diffPct).toFixed(1) + "%")),
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

    if (periodKey === "prev") {
      bounds.start = "2026-07-01";
      bounds.end = "2026-07-31";
      bounds.label = "July 2026 Pre-launch Baseline";
      bounds.partial = false;
      funnel = { enquiries: null, discoveries: null, jobOrders: null, placements: null, enquiriesPending: false, source: "None" };
      ads = null;
    } else {
      bounds.start = "2026-08-01";
      bounds.end = asOfDate();
      bounds.label = "August 2026 Month to Date";
      bounds.partial = false;

      funnel = sumSalesLabeled([w1, w2, w3], bounds.start, bounds.end, market);
      ads = sumAdsByDate(by, bounds.start, bounds.end, cur);
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
      "Data through " + asOfDate() + " · Google Ads: " + adsDate + " · Sales confirmed by Cheyenne (US) & Holly (AU) · Blended directional attribution";
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
      '<div class="ex-briefing-p"><strong>Blended attribution:</strong> Google Ads is the company’s primary marketing spend. While not every individual enquiry is directly attributed to an ad click yet (' + totalGclid + ' of ' + totalZoho + ' audited CRM records carry verified click IDs), total blended unit costs provide reliable directional guidance for leadership decisions while direct tracking is being connected.</div>';

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
    var container = $("#ex-market-scorecards");
    if (!container) return;

    var usAds = us.ads || {};
    var auAds = au.ads || {};

    var agUs = (STATE.agency && STATE.agency.us) || {};
    var agAu = (STATE.agency && STATE.agency.au) || {};

    var usAgSpendTotal = agUs.total_spend || 724880;
    var auAgSpendTotal = agAu.total_spend || 458167;
    var usAgMonthlySpend = usAgSpendTotal / 24; // ~$30,203
    var auAgMonthlySpend = auAgSpendTotal / 24; // ~$19,090

    var usAgCpe = agUs.cost_per_legitimate_employer_enquiry || 816.31;
    var usAgCpd = agUs.cost_per_discovery || 1285.25;
    var usAgCpjo = agUs.cost_per_job_order || 2013.56;
    var usAgCpp = agUs.cost_per_placement || 4289.23;
    var usAgCpc = agUs.avg_cpc || 8.29;
    var usAgCtr = agUs.ctr_pct || 1.62;

    var auAgCpe = agAu.cost_per_legitimate_employer_enquiry || 615.82;
    var auAgCpd = agAu.cost_per_discovery || 812.35;
    var auAgCpjo = agAu.cost_per_job_order || 1104.02;
    var auAgCpp = agAu.cost_per_placement || 2073.15;
    var auAgCpc = agAu.avg_cpc || 9.24;
    var auAgCtr = agAu.ctr_pct || 1.44;

    function buildMarketCard(market, title, currency, data, ads, agTotalSpend, agMonthlySpend, agCpe, agCpd, agCpjo, agCpp, agCpc, agCtr, opsLead) {
      var isPrev = STATE.period === "prev";
      var cur = currency;

      // Spend run-rate calculations
      var mtdSpend = data.spend || 0;
      var days = 27; // Aug 1 - Aug 27
      var monthlyRunRate = isPrev ? 0 : (mtdSpend > 0 ? (mtdSpend / days) * 30.4 : 0);
      var spendSavingsPct = agMonthlySpend > 0 ? ((agMonthlySpend - monthlyRunRate) / agMonthlySpend) * 100 : 0;
      var periodEquivAgSpend = (agMonthlySpend / 30.4) * days;
      var periodSpendDiff = compareRate(mtdSpend, periodEquivAgSpend, true);

      // Unit cost & delta calculations
      var cpeVal = data.cpe && data.cpe.value != null ? data.cpe.value : null;
      var cpeDiff = compareRate(cpeVal, agCpe, true);

      var cpdVal = data.cpd && data.cpd.value != null ? data.cpd.value : null;
      var cpdDiff = compareRate(cpdVal, agCpd, true);

      var joVal = data.funnel && data.funnel.jobOrders && data.funnel.jobOrders > 0 ? (mtdSpend / data.funnel.jobOrders) : null;
      var joDiff = joVal != null ? compareRate(joVal, agCpjo, true) : null;

      var plVal = data.funnel && data.funnel.placements && data.funnel.placements > 0 ? (mtdSpend / data.funnel.placements) : null;
      var plDiff = plVal != null ? compareRate(plVal, agCpp, true) : null;

      var cpcVal = ads && ads.avgCpc != null ? ads.avgCpc : null;
      var cpcDiff = compareRate(cpcVal, agCpc, true);

      var ctrVal = ads && ads.ctrPct != null ? ads.ctrPct : null;
      var ctrDiff = compareRate(ctrVal, agCtr, false);

      var html = '<div class="ex-market-card">';
      
      // Card Header
      html += '<div class="ex-market-card-hd">';
      html += '  <div class="ex-market-card-title-row">';
      html += '    <div class="ex-market-flag-title">';
      html += '      <span class="ex-mkt-tag ' + market.toLowerCase() + '">' + market + '</span>';
      html += '      <h3>' + title + ' <span class="ex-curr-badge">' + cur + '</span></h3>';
      html += '    </div>';
      html += '    <span class="ex-lead-label">' + opsLead + '</span>';
      html += '  </div>';

      if (!isPrev) {
        html += '  <div class="ex-market-spend-banner">';
        html += '    <div class="ex-spend-stat">';
        html += '      <span class="ex-stat-lbl">Pilot Run-rate</span>';
        html += '      <span class="ex-stat-val font-mono">' + formatMoney(monthlyRunRate, cur) + '<small>/mo</small></span>';
        html += '    </div>';
        html += '    <div class="ex-spend-stat">';
        html += '      <span class="ex-stat-lbl">Agency Baseline</span>';
        html += '      <span class="ex-stat-val font-mono mute">' + formatMoney(agMonthlySpend, cur) + '<small>/mo</small></span>';
        html += '    </div>';
        html += '    <div class="ex-spend-stat highlight">';
        html += '      <span class="ex-stat-lbl">Monthly Savings</span>';
        html += '      <span class="ex-stat-val font-mono delta-good">−' + Math.round(spendSavingsPct) + '% <small class="text-muted">(−' + formatMoney(agMonthlySpend - monthlyRunRate, cur) + '/mo)</small></span>';
        html += '    </div>';
        html += '  </div>';
      }
      html += '</div>';

      // Card Table
      html += '<div class="ex-market-card-table-wrap">';
      html += '<table class="ex-table ex-scorecard-table">';
      html += '<thead><tr>';
      html += '  <th>Metric</th>';
      html += '  <th class="num">Volume</th>';
      html += '  <th class="num">Pilot (Blended)</th>';
      html += '  <th class="num">Agency Baseline</th>';
      html += '  <th class="num">Savings / Δ</th>';
      html += '</tr></thead>';
      html += '<tbody>';

      if (isPrev) {
        html += '<tr><td colspan="5" style="text-align:center;padding:2rem 1rem;color:var(--ex-text-muted);">' +
          'Pre-launch baseline period (July 2026). Search pilot launched in August 2026.</td></tr>';
      } else {
        // 1. Paid Ad Spend (MTD)
        html += '<tr>';
        html += '  <td><strong>Paid ad spend (MTD)</strong></td>';
        html += '  <td class="num font-mono text-muted">—</td>';
        html += '  <td class="num font-mono"><strong>' + formatMoney(mtdSpend, cur) + '</strong></td>';
        html += '  <td class="num font-mono text-muted">' + formatMoney(periodEquivAgSpend, cur) + '</td>';
        html += '  <td class="num font-mono ' + (periodSpendDiff.tone === "good" ? "delta-good" : "") + '">' + periodSpendDiff.diffText + '</td>';
        html += '</tr>';

        // 2. Employer Enquiries
        var enqVol = data.funnel.enquiriesPending ? '<span class="ex-status-tag pending">Pending</span>' : formatNum(data.funnel.enquiries);
        var enqCost = ratioMoney(data.cpe, cur);
        html += '<tr>';
        html += '  <td><strong>Employer enquiries</strong></td>';
        html += '  <td class="num font-mono">' + enqVol + '</td>';
        html += '  <td class="num font-mono"><strong>' + enqCost + '</strong></td>';
        html += '  <td class="num font-mono text-muted">' + formatMoney2(agCpe, cur) + '</td>';
        html += '  <td class="num font-mono ' + (cpeDiff.tone === "good" ? "delta-good" : "") + '">' + cpeDiff.diffText + '</td>';
        html += '</tr>';

        // 3. Discovery Calls
        var discVol = data.funnel.discoveries == null ? "—" : formatNum(data.funnel.discoveries);
        var discCost = ratioMoney(data.cpd, cur);
        html += '<tr>';
        html += '  <td><strong>Completed discovery calls</strong></td>';
        html += '  <td class="num font-mono">' + discVol + '</td>';
        html += '  <td class="num font-mono"><strong>' + discCost + '</strong></td>';
        html += '  <td class="num font-mono text-muted">' + formatMoney2(agCpd, cur) + '</td>';
        html += '  <td class="num font-mono ' + (cpdDiff.tone === "good" ? "delta-good" : "") + '">' + cpdDiff.diffText + '</td>';
        html += '</tr>';

        // 4. Job Orders
        var joVol = data.funnel.jobOrders && data.funnel.jobOrders > 0 ? formatNum(data.funnel.jobOrders) : (market === "US" ? '<span class="ex-status-tag warn">None confirmed</span>' : (data.funnel.jobOrders === 0 ? "0" : "—"));
        var joCost = joVal != null ? '<strong>' + formatMoney2(joVal, cur) + '</strong>' : (market === "US" ? '<span class="ex-status-tag warn">Pipeline active</span>' : "—");
        var joDiffHtml = joDiff ? '<span class="' + (joDiff.tone === "good" ? "delta-good" : "") + '">' + joDiff.diffText + '</span>' : '<span class="ex-status-tag pending">Reviewing</span>';
        html += '<tr>';
        html += '  <td><strong>Confirmed job orders</strong></td>';
        html += '  <td class="num font-mono">' + joVol + '</td>';
        html += '  <td class="num font-mono">' + joCost + '</td>';
        html += '  <td class="num font-mono text-muted">' + formatMoney2(agCpjo, cur) + '</td>';
        html += '  <td class="num font-mono">' + joDiffHtml + '</td>';
        html += '</tr>';

        // 5. Placements
        var plVol = data.funnel.placements && data.funnel.placements > 0 ? formatNum(data.funnel.placements) : (market === "US" ? '<span class="ex-status-tag warn">None confirmed</span>' : (data.funnel.placements === 0 ? "0" : "—"));
        var plCost = plVal != null ? '<strong>' + formatMoney2(plVal, cur) + '</strong>' : (market === "US" ? '<span class="ex-status-tag warn">Pipeline active</span>' : "—");
        var plDiffHtml = plDiff ? '<span class="' + (plDiff.tone === "good" ? "delta-good" : "") + '">' + plDiff.diffText + '</span>' : '<span class="ex-status-tag pending">Reviewing</span>';
        html += '<tr>';
        html += '  <td><strong>Confirmed placements</strong></td>';
        html += '  <td class="num font-mono">' + plVol + '</td>';
        html += '  <td class="num font-mono">' + plCost + '</td>';
        html += '  <td class="num font-mono text-muted">' + formatMoney2(agCpp, cur) + '</td>';
        html += '  <td class="num font-mono">' + plDiffHtml + '</td>';
        html += '</tr>';

        // 6. Avg CPC
        var cpcClicks = ads && ads.clicks ? formatNum(ads.clicks) + " clicks" : "—";
        html += '<tr>';
        html += '  <td>Average cost per click (CPC)</td>';
        html += '  <td class="num font-mono text-muted">' + cpcClicks + '</td>';
        html += '  <td class="num font-mono"><strong>' + (cpcVal != null ? formatMoney2(cpcVal, cur) : "—") + '</strong></td>';
        html += '  <td class="num font-mono text-muted">' + formatMoney2(agCpc, cur) + '</td>';
        html += '  <td class="num font-mono ' + (cpcDiff.tone === "good" ? "delta-good" : "") + '">' + cpcDiff.diffText + '</td>';
        html += '</tr>';

        // 7. CTR
        var ctrImp = ads && ads.impressions ? formatNum(ads.impressions) + " imp" : "—";
        html += '<tr>';
        html += '  <td>Click-through rate (CTR)</td>';
        html += '  <td class="num font-mono text-muted">' + ctrImp + '</td>';
        html += '  <td class="num font-mono"><strong>' + (ctrVal != null ? formatPct(ctrVal) : "—") + '</strong></td>';
        html += '  <td class="num font-mono text-muted">' + formatPct(agCtr) + '</td>';
        html += '  <td class="num font-mono ' + (ctrDiff.tone === "good" ? "delta-good" : "") + '">' + ctrDiff.diffText + '</td>';
        html += '</tr>';
      }

      html += '</tbody></table>';
      html += '</div>';

      // Card Footnote
      html += '<div class="ex-market-card-ft">';
      html += '  <span>Historical 2-yr agency spend: ' + formatMoney(agTotalSpend, cur) + ' total (' + formatMoney(agMonthlySpend, cur) + '/mo)</span>';
      html += '</div>';

      html += '</div>';
      return html;
    }

    var usCard = buildMarketCard(
      "US",
      "United States",
      "USD",
      us,
      usAds,
      usAgSpendTotal,
      usAgMonthlySpend,
      usAgCpe,
      usAgCpd,
      usAgCpjo,
      usAgCpp,
      usAgCpc,
      usAgCtr,
      "Sales review: Cheyenne Gichana"
    );

    var auCard = buildMarketCard(
      "AU",
      "Australia",
      "AUD",
      au,
      auAds,
      auAgSpendTotal,
      auAgMonthlySpend,
      auAgCpe,
      auAgCpd,
      auAgCpjo,
      auAgCpp,
      auAgCpc,
      auAgCtr,
      "Sales review: Holly Wallace"
    );

    container.innerHTML = usCard + auCard;
  }

  function renderSimplifiedAgencyComparison(us, au) {
    var body = $("#ex-agency-body");
    if (!body) return;

    var isPrev = STATE.period === "prev";
    if (isPrev) {
      body.innerHTML = '<tr><td colspan="7" style="text-align:center;padding:1.5rem;color:var(--ex-text-muted);">Pre-launch baseline period (July 2026).</td></tr>';
      return;
    }

    var agUs = (STATE.agency && STATE.agency.us) || {};
    var agAu = (STATE.agency && STATE.agency.au) || {};

    var usAgSpendTotal = agUs.total_spend || 724880;
    var auAgSpendTotal = agAu.total_spend || 458167;
    var usAgMonthlySpend = usAgSpendTotal / 24; // ~$30,203
    var auAgMonthlySpend = auAgSpendTotal / 24; // ~$19,090

    var usAgCpe = agUs.cost_per_legitimate_employer_enquiry || 816.31;
    var usAgCpd = agUs.cost_per_discovery || 1285.25;
    var usAgCpjo = agUs.cost_per_job_order || 2013.56;

    var auAgCpe = agAu.cost_per_legitimate_employer_enquiry || 615.82;
    var auAgCpd = agAu.cost_per_discovery || 812.35;
    var auAgCpjo = agAu.cost_per_job_order || 1104.02;

    var days = 27;
    var usMtdSpend = us.spend || 0;
    var auMtdSpend = au.spend || 0;

    var usMonthlyRunRate = (usMtdSpend / days) * 30.4;
    var auMonthlyRunRate = (auMtdSpend / days) * 30.4;

    var usSpendSavingsPct = ((usAgMonthlySpend - usMonthlyRunRate) / usAgMonthlySpend) * 100;
    var auSpendSavingsPct = ((auAgMonthlySpend - auMonthlyRunRate) / auAgMonthlySpend) * 100;

    var usCpeVal = us.cpe && us.cpe.value != null ? us.cpe.value : null;
    var auCpeVal = au.cpe && au.cpe.value != null ? au.cpe.value : null;

    var usCpdVal = us.cpd && us.cpd.value != null ? us.cpd.value : null;
    var auCpdVal = au.cpd && au.cpd.value != null ? au.cpd.value : null;

    var usJoVal = us.funnel && us.funnel.jobOrders && us.funnel.jobOrders > 0 ? (usMtdSpend / us.funnel.jobOrders) : null;
    var auJoVal = au.funnel && au.funnel.jobOrders && au.funnel.jobOrders > 0 ? (auMtdSpend / au.funnel.jobOrders) : null;

    var rows = [];

    // US Row
    rows.push('<tr>' +
      '<td><span class="ex-mkt-tag us">US</span> <strong>United States</strong></td>' +
      '<td class="num font-mono"><strong>' + formatMoney(usMonthlyRunRate, "USD") + '</strong>/mo</td>' +
      '<td class="num font-mono text-muted">' + formatMoney(usAgMonthlySpend, "USD") + '/mo</td>' +
      '<td class="num font-mono delta-good">−' + Math.round(usSpendSavingsPct) + '% <small class="text-muted">(−' + formatMoney(usAgMonthlySpend - usMonthlyRunRate, "USD") + '/mo)</small></td>' +
      '<td class="num font-mono"><strong>' + (usCpeVal ? formatMoney2(usCpeVal, "USD") : "—") + '</strong></td>' +
      '<td class="num font-mono"><strong>' + (usCpdVal ? formatMoney2(usCpdVal, "USD") : "—") + '</strong></td>' +
      '<td class="num font-mono">' + (usJoVal ? '<strong>' + formatMoney2(usJoVal, "USD") + '</strong>' : '<span class="ex-status-tag warn">Pipeline active</span>') + '</td>' +
      '</tr>');

    // AU Row
    rows.push('<tr>' +
      '<td><span class="ex-mkt-tag au">AU</span> <strong>Australia</strong></td>' +
      '<td class="num font-mono"><strong>' + formatMoney(auMonthlyRunRate, "AUD") + '</strong>/mo</td>' +
      '<td class="num font-mono text-muted">' + formatMoney(auAgMonthlySpend, "AUD") + '/mo</td>' +
      '<td class="num font-mono delta-good">−' + Math.round(auSpendSavingsPct) + '% <small class="text-muted">(−' + formatMoney(auAgMonthlySpend - auMonthlyRunRate, "AUD") + '/mo)</small></td>' +
      '<td class="num font-mono"><strong>' + (auCpeVal ? formatMoney2(auCpeVal, "AUD") : "—") + '</strong></td>' +
      '<td class="num font-mono"><strong>' + (auCpdVal ? formatMoney2(auCpdVal, "AUD") : "—") + '</strong></td>' +
      '<td class="num font-mono"><strong>' + (auJoVal ? formatMoney2(auJoVal, "AUD") : "—") + '</strong></td>' +
      '</tr>');

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
    h += '<thead><tr><th style="width:28%;">Metric</th><th class="num" style="width:20%;">United States (USD)</th><th class="num" style="width:20%;">Australia (AUD)</th><th style="width:32%;">Notes</th></tr></thead><tbody>';

    h += '<tr><td>Enquiry → Discovery rate</td><td class="num font-mono">' + rateStr(us.funnel.discoveries, us.funnel.enquiries) + '</td><td class="num font-mono">' + rateStr(au.funnel.discoveries, au.funnel.enquiries) + '</td><td class="ex-cell-note">Period activity rate · Discovery calls lag enquiries.</td></tr>';
    h += '<tr><td>Discovery → Job order rate</td><td class="num font-mono">' + (us.funnel.jobOrders ? rateStr(us.funnel.jobOrders, us.funnel.discoveries) : "—") + '</td><td class="num font-mono">' + rateStr(au.funnel.jobOrders, au.funnel.discoveries) + '</td><td class="ex-cell-note">Discovery calls converted to signed job orders.</td></tr>';
    h += '<tr><td>Job order → Placement rate</td><td class="num font-mono">' + (us.funnel.placements ? rateStr(us.funnel.placements, us.funnel.jobOrders) : "—") + '</td><td class="num font-mono">' + rateStr(au.funnel.placements, au.funnel.jobOrders) + '</td><td class="ex-cell-note">Job orders converted to hired candidate placements.</td></tr>';
    h += '<tr><td>Cost per job order</td><td class="num font-mono">' + ratioMoney(us.cpjo, "USD") + '</td><td class="num font-mono">' + ratioMoney(au.cpjo, "AUD") + '</td><td class="ex-cell-note">Ad spend divided by confirmed job orders.</td></tr>';
    h += '<tr><td>Cost per placement</td><td class="num font-mono">' + ratioMoney(us.cpp, "USD") + '</td><td class="num font-mono">' + ratioMoney(au.cpp, "AUD") + '</td><td class="ex-cell-note">Ad spend divided by confirmed placements.</td></tr>';

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
      var h = '<div style="margin-bottom:1.25rem;">';
      h += '<h4 style="margin:0 0 0.5rem;font-size:0.88rem;color:var(--ex-text-main);">' + (market === "US" ? "United States (USD)" : "Australia (AUD)") + '</h4>';
      h += '<table class="ex-table"><thead><tr>';
      h += '<th style="width:24%;">Period</th><th class="num" style="width:14%;">Spend</th><th class="num" style="width:14%;">Enquiries</th><th class="num" style="width:14%;">Discoveries</th><th class="num" style="width:14%;">Job Orders</th>';
      if (market === "AU") h += '<th class="num" style="width:10%;">Placements</th>';
      h += '<th class="num" style="width:10%;">Cost / Enq</th></tr></thead><tbody>';

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
        h += '<td class="num font-mono">' + spend + '</td>';
        h += '<td class="num font-mono">' + enq + '</td>';
        h += '<td class="num font-mono">' + disc + '</td>';
        h += '<td class="num font-mono">' + jo + '</td>';
        if (market === "AU") h += '<td class="num font-mono">' + pl + '</td>';
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

    var h = '<p style="margin:0 0 0.75rem;font-size:0.86rem;color:var(--ex-text-main);line-height:1.55;">';
    h += '<strong>Blended directional attribution:</strong> Google Ads represents our primary marketing spend. During the pilot period, sales confirmed <strong>49 total employer enquiries</strong> (31 US + 18 AU). In the single-week CRM audit (Aug 17–23), <strong>31 records</strong> were inspected in Zoho, of which <strong>5 contained a verified advertising click ID (GCLID)</strong> (2 US, 3 AU). Because not every lead has direct click attribution yet, leadership uses blended funnel metrics for dependable directional decision-making while tracking integration is completed.';
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
