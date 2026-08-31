/**
 * Executive V2 — client-side renderer (preview only).
 */
(function () {
  "use strict";

  var STATE = {
    window: "frozen",
    snapshot: null,
    archivePrior: null,
    ga4: null,
  };

  function $(sel) {
    return document.querySelector(sel);
  }

  function esc(s) {
    var d = document.createElement("div");
    d.textContent = s == null ? "" : String(s);
    return d.innerHTML;
  }

  function num(n) {
    if (n == null || n === "" || Number.isNaN(Number(n))) return "—";
    return Number(n).toLocaleString("en-US");
  }

  function money(v, cur) {
    if (v == null || v === "" || Number.isNaN(Number(v))) return "—";
    var sym = cur === "AUD" ? "A$" : "$";
    return sym + Number(v).toLocaleString("en-US", { maximumFractionDigits: 0 });
  }

  function money2(v, cur) {
    if (v == null || v === "" || Number.isNaN(Number(v))) return "—";
    var sym = cur === "AUD" ? "A$" : "$";
    return sym + Number(v).toLocaleString("en-US", { minimumFractionDigits: 2, maximumFractionDigits: 2 });
  }

  function pct(v) {
    if (v == null || v === "") return "—";
    return Number(v).toFixed(1) + "%";
  }

  function fetchJson(url) {
    return fetch(url).then(function (r) {
      if (!r.ok) throw new Error(url + " " + r.status);
      return r.json();
    });
  }

  function todayIso() {
    return ((STATE.snapshot || {}).generated_at_utc || "").slice(0, 10) || "2026-08-27";
  }

  function monthLabel() {
    var d = new Date(todayIso() + "T12:00:00Z");
    return d.toLocaleString("en-US", { month: "long", year: "numeric", timeZone: "UTC" });
  }

  function sumByDateRangeObj(market, start, end) {
    var perf = market === "US" ? STATE.snapshot.performance_us : STATE.snapshot.performance_au;
    var by = (perf || {}).by_date_stage1 || (perf || {}).by_date || {};
    var cost = 0;
    var clicks = 0;
    var any = false;
    Object.keys(by).forEach(function (d) {
      if (d >= start && d <= end) {
        any = true;
        cost += Number(by[d].cost_usd || 0);
        clicks += Number(by[d].clicks || 0);
      }
    });
    return any ? { cost_usd: cost, clicks: clicks } : null;
  }

  function isEnquiryPending(ops) {
    if (!ops) return true;
    var caveat = String(ops.caveat || "").toLowerCase();
    if (caveat.indexOf("count pending") >= 0 || caveat.indexOf("enquiry count pending") >= 0) return true;
    return ops.enquiries == null;
  }

  function salesEnquiries(ops) {
    if (!ops) return { value: "Pending", pending: true, raw: null };
    if (isEnquiryPending(ops)) return { value: "Pending", pending: true, raw: null };
    return { value: ops.enquiries, pending: false, raw: ops.enquiries };
  }

  function discoveryCalls(ops) {
    if (!ops) return { value: "Pending", pending: true, raw: null };
    if (ops.sales_calls_completed != null)
      return { value: ops.sales_calls_completed, pending: false, raw: ops.sales_calls_completed };
    return { value: "Pending", pending: true, raw: null };
  }

  function jobOrders(ops, market) {
    if (!ops) return { value: "Pending", pending: true, raw: null };
    if (market === "AU" && ops.job_orders_total != null)
      return { value: ops.job_orders_total, pending: false, raw: ops.job_orders_total };
    if (ops.job_orders_total != null) return { value: ops.job_orders_total, pending: false, raw: ops.job_orders_total };
    return { value: 0, pending: false, raw: 0 };
  }

  function placements(ops) {
    if (!ops || ops.placements == null) return { value: "Pending", pending: true, raw: null };
    return { value: ops.placements, pending: false, raw: ops.placements };
  }

  function monthToDateOps(market) {
    var snap = STATE.snapshot;
    var arch = STATE.archivePrior;
    var w1 = market === "US" ? (arch && arch.sales_ops_us) : arch && arch.sales_ops_au;
    var w2 = market === "US" ? snap.sales_ops_us : snap.sales_ops_au;
    var wtd = market === "US" ? snap.sales_ops_us_now : snap.sales_ops_au_now;

    function add(a, b) {
      if (a == null && b == null) return null;
      return Number(a || 0) + Number(b || 0);
    }

    var enq = add(w1 && w1.enquiries, w2 && w2.enquiries);
    var disc = add(w1 && w1.sales_calls_completed, w2 && w2.sales_calls_completed);
    var jo = market === "AU" ? add(w1 && w1.job_orders_total, w2 && w2.job_orders_total) : null;

    var monthStart = todayIso().slice(0, 8) + "01";
    var ads = sumByDateRangeObj(market, monthStart, todayIso());
    var spend = ads && ads.cost_usd;

    var cpe = enq > 0 && spend != null ? spend / enq : null;
    var cpd = disc > 0 && spend != null ? spend / disc : null;

    return {
      enquiries: enq,
      sales_calls_completed: disc,
      job_orders_total: jo,
      spend_usd: spend,
      cost_per_enquiry_usd: cpe,
      cost_per_sales_call_completed_usd: cpd,
      label: monthLabel() + " to date",
      caveat: wtd && String(wtd.caveat || "").indexOf("pending") >= 0 ? "WTD sales labels still pending" : null,
    };
  }

  function priorMonthOps(market) {
    var arch = STATE.archivePrior;
    if (!arch) return null;
    return market === "US" ? arch.sales_ops_us : arch.sales_ops_au;
  }

  function getWindowConfig(key) {
    var snap = STATE.snapshot;
    return {
      month: {
        key: "month",
        label: monthLabel() + " to date",
        usOps: monthToDateOps("US"),
        auOps: monthToDateOps("AU"),
        usPrior: priorMonthOps("US"),
        auPrior: priorMonthOps("AU"),
        compareLabel: "vs first August week",
        partial: true,
      },
      frozen: {
        key: "frozen",
        label: (snap.sales_ops_us || {}).label || "Last complete week",
        usOps: snap.sales_ops_us,
        auOps: snap.sales_ops_au,
        usPrior: STATE.archivePrior && STATE.archivePrior.sales_ops_us,
        auPrior: STATE.archivePrior && STATE.archivePrior.sales_ops_au,
        compareLabel: "vs prior week",
        partial: false,
      },
      now: {
        key: "now",
        label: ((snap.performance_us || {}).scoreboard_now || {}).label || "This week so far",
        usOps: snap.sales_ops_us_now,
        auOps: snap.sales_ops_au_now,
        usPrior: snap.sales_ops_us,
        auPrior: snap.sales_ops_au,
        compareLabel: "vs last complete week (pacing)",
        partial: true,
      },
    }[key];
  }

  function deltaText(cur, prior, fmt, higherGood, minDenom) {
    if (cur == null || prior == null) return { text: "", cls: "flat" };
    if (minDenom != null && (Number(prior) < minDenom || Number(cur) < minDenom))
      return { text: "Small sample", cls: "sample" };
    if (prior === 0) return { text: "—", cls: "flat" };
    var pctChg = ((Number(cur) - Number(prior)) / Math.abs(Number(prior))) * 100;
    if (Math.abs(pctChg) < 2) return { text: "≈ flat vs " + fmt(prior), cls: "flat" };
    var dir = pctChg > 0 ? "↑" : "↓";
    var improved = pctChg > 0 ? higherGood : !higherGood;
    return {
      text: dir + " " + Math.abs(Math.round(pctChg)) + "% vs " + fmt(prior),
      cls: improved ? "good" : "bad",
    };
  }

  function renderHeader() {
    var snap = STATE.snapshot;
    var cfg = getWindowConfig(STATE.window);
    var adsDate = (snap.generated_at_utc || "").slice(0, 10);
    var frozen = snap.sales_ops_us || {};

    $("#ev2-subtitle").textContent = cfg.label;
    $("#ev2-fresh-line").textContent =
      "Ads updated " +
      adsDate +
      " · Sales labels through " +
      ((snap.sales_ops_us_now || {}).window_end || frozen.window_end || "—").slice(5);

    var meta = $("#ev2-scorecard-meta");
    if (meta) {
      var monthName = monthLabel();
      meta.textContent =
        STATE.window === "month"
          ? monthName + " totals · compared to first week of month (no prior-month sales data yet)"
          : cfg.compareLabel + " · blended costs are not Google Ads CPA";
    }
  }

  function renderCommentary() {
    var snap = STATE.snapshot;
    var us = snap.sales_ops_us || {};
    var au = snap.sales_ops_au || {};
    var usNow = snap.sales_ops_us_now || {};
    var auNow = snap.sales_ops_au_now || {};
    var arch = STATE.archivePrior;
    var archUs = (arch && arch.sales_ops_us) || {};

    var bullets = [
      "Last complete week (Aug 17–23): US " +
        num(us.enquiries) +
        " employer enquiries, " +
        num(us.sales_calls_completed) +
        " discovery calls (" +
        money2(us.cost_per_enquiry_usd, "USD") +
        "/enquiry). AU " +
        num(au.enquiries) +
        " enquiries, " +
        num(au.sales_calls_completed) +
        " calls, " +
        num(au.job_orders_total) +
        " job orders.",
      "August so far: US " +
        num((archUs.enquiries || 0) + (us.enquiries || 0)) +
        " labelled enquiries across two complete weeks — up from " +
        num(archUs.enquiries) +
        " in the first week. Spend is climbing as Stage 1 scales; enquiry volume is the thing to watch.",
      "This week is partial. Holly has " +
        num(auNow.enquiries) +
        " enquiries and " +
        num(auNow.job_orders_total) +
        " job order so far. Cheyenne's Mon–Tue count is still pending — don't read US cost/enquiry until she emails.",
      "Budget and bidding: hold on both markets. Stay on Max Clicks until more sales-confirmed employer leads carry a click ID.",
    ];

    var el = $("#ev2-commentary");
    if (el) el.innerHTML = "<ul>" + bullets.map(function (b) {
      return "<li>" + esc(b) + "</li>";
    }).join("") + "</ul>";

    var gclid = gclidSummary();
    var one = $("#ev2-attrib-oneline");
    if (one) {
      one.innerHTML = esc(gclid.plain) + ' <a href="#" id="ev2-attrib-link">Details</a>';
      var link = $("#ev2-attrib-link");
      if (link) {
        link.addEventListener("click", function (e) {
          e.preventDefault();
          var d = document.getElementById("ev2-attrib-details");
          if (d) d.open = true;
        });
      }
    }
  }

  function gclidSummary() {
    var us = (STATE.snapshot.sales_ops_us || {}).zoho_census || {};
    var au = (STATE.snapshot.sales_ops_au || {}).zoho_census || {};
    var t = Number(us.usa_sales_enquiries || 0) + Number(au.au_sales_enquiries || 0);
    var g = Number(us.usa_with_gclid || 0) + Number(au.au_with_gclid || 0);
    return {
      plain:
        "Attribution is still weak — only " +
        g +
        " of " +
        t +
        " Zoho rows have a click ID. Paid CPA is not trustworthy yet.",
    };
  }

  function renderScorecard() {
    var cfg = getWindowConfig(STATE.window);
    var tbody = $("#ev2-scorecard-body");
    if (!tbody) return;

    var rows = [
      { key: "enq", label: "Employer enquiries", hi: true },
      { key: "disc", label: "Discovery calls", hi: true },
      { key: "jo", label: "Job orders", hi: true },
      { key: "spend", label: "Ads spend", hi: false },
      { key: "cpe", label: "Blended spend / enquiry", hi: false },
      { key: "cpd", label: "Blended spend / discovery", hi: false },
    ];

    function cell(market) {
      var ops = market === "US" ? cfg.usOps : cfg.auOps;
      var prior = market === "US" ? cfg.usPrior : cfg.auPrior;
      var sym = market === "US" ? "USD" : "AUD";

      function vals() {
        var e = salesEnquiries(ops);
        var d = discoveryCalls(ops);
        var j = jobOrders(ops, market);
        return {
          enq: { d: e.pending ? "Pending" : num(e.value), r: e.raw },
          disc: { d: d.pending ? "Pending" : num(d.value), r: d.raw },
          jo: { d: j.pending ? "Pending" : num(j.value), r: j.raw },
          spend: { d: money(ops && ops.spend_usd, sym), r: ops && ops.spend_usd },
          cpe: {
            d: ops && ops.cost_per_enquiry_usd != null ? money2(ops.cost_per_enquiry_usd, sym) : ops && ops.enquiries > 0 ? "—" : "Pending",
            r: ops && ops.cost_per_enquiry_usd,
          },
          cpd: {
            d: ops && ops.cost_per_sales_call_completed_usd != null ? money2(ops.cost_per_sales_call_completed_usd, sym) : "—",
            r: ops && ops.cost_per_sales_call_completed_usd,
          },
        };
      }

      function priorVals() {
        if (!prior) return {};
        return {
          enq: prior.enquiries,
          disc: prior.sales_calls_completed,
          jo: prior.job_orders_total,
          spend: prior.spend_usd,
          cpe: prior.cost_per_enquiry_usd,
          cpd: prior.cost_per_sales_call_completed_usd,
        };
      }

      var v = vals();
      var p = priorVals();
      var out = {};
      rows.forEach(function (r) {
        var fmt = r.key.indexOf("cp") === 0 || r.key === "spend"
          ? function (x) {
              return r.key === "spend" ? money(x, sym) : money2(x, sym);
            }
          : num;
        var cmp = { text: "", cls: "flat" };
        if (v[r.key].r != null && p[r.key] != null) {
          cmp = deltaText(v[r.key].r, p[r.key], fmt, r.hi, r.key === "enq" || r.key === "disc" ? 3 : null);
        } else if (cfg.partial && (r.key === "enq" || r.key === "disc")) {
          cmp = { text: cfg.compareLabel, cls: "flat" };
        }
        out[r.key] = { display: v[r.key].d, cmp: cmp };
      });
      return out;
    }

    var us = cell("US");
    var au = cell("AU");
    tbody.innerHTML = rows
      .map(function (r) {
        return (
          "<tr><td class=\"metric\">" + esc(r.label) +
          '</td><td class="num"><span class="val">' + esc(us[r.key].display) +
          '</span><span class="cmp ' + us[r.key].cmp.cls + '">' + esc(us[r.key].cmp.text) +
          '</span></td><td class="num"><span class="val">' + esc(au[r.key].display) +
          '</span><span class="cmp ' + au[r.key].cmp.cls + '">' + esc(au[r.key].cmp.text) +
          "</span></td></tr>"
        );
      })
      .join("");
  }

  function renderFunnels() {
    var cfg = getWindowConfig(STATE.window);
    var host = $("#ev2-funnels");
    if (!host) return;

    function one(market) {
      var ops = market === "US" ? cfg.usOps : cfg.auOps;
      var steps = [
        { n: "Employer enquiries", d: salesEnquiries(ops) },
        { n: "Discovery calls", d: discoveryCalls(ops) },
        { n: "Job orders", d: jobOrders(ops, market) },
        { n: "Placements", d: placements(ops) },
      ];
      var html = '<div class="ev2-card ev2-funnel"><h3>' + esc(market === "US" ? "United States" : "Australia") + '</h3><div class="ev2-funnel-steps">';
      var prev = null;
      steps.forEach(function (s, i) {
        if (i) html += '<div class="ev2-funnel-arrow">↓</div>';
        var pend = s.d.pending;
        var count = pend ? "Pending" : num(s.d.value);
        var rate = "";
        if (!pend && prev != null && Number(prev) >= 5 && s.d.raw != null)
          rate = Math.round((Number(s.d.raw) / Number(prev)) * 100) + "%";
        else if (!pend && prev != null && Number(prev) < 5) rate = "Small sample";
        if (!pend && s.d.raw != null) prev = s.d.raw;
        html += '<div class="ev2-funnel-step' + (pend ? " pending" : "") + '"><span class="name">' + esc(s.n) +
          '</span><span class="count">' + esc(count) + '</span><span class="rate">' + esc(rate) + "</span></div>";
      });
      return html + "</div></div>";
    }
    host.innerHTML = one("US") + one("AU");
  }

  function weeklyTrendSeries() {
    var snap = STATE.snapshot;
    var arch = STATE.archivePrior;
    var weeks = [];
    if (arch && arch.sales_ops_us) {
      weeks.push({
        label: "Aug 10–16",
        short: "W1",
        partial: false,
        us: { spend: arch.sales_ops_us.spend_usd, enq: arch.sales_ops_us.enquiries, disc: arch.sales_ops_us.sales_calls_completed, jo: null },
        au: { spend: (arch.sales_ops_au || {}).spend_usd, enq: (arch.sales_ops_au || {}).enquiries, disc: (arch.sales_ops_au || {}).sales_calls_completed, jo: (arch.sales_ops_au || {}).job_orders_total },
      });
    }
    if (snap.sales_ops_us) {
      weeks.push({
        label: "Aug 17–23",
        short: "W2",
        partial: false,
        us: { spend: snap.sales_ops_us.spend_usd, enq: snap.sales_ops_us.enquiries, disc: snap.sales_ops_us.sales_calls_completed, jo: null },
        au: { spend: (snap.sales_ops_au || {}).spend_usd, enq: (snap.sales_ops_au || {}).enquiries, disc: (snap.sales_ops_au || {}).sales_calls_completed, jo: (snap.sales_ops_au || {}).job_orders_total },
      });
    }
    var usNow = snap.sales_ops_us_now || {};
    var auNow = snap.sales_ops_au_now || {};
    weeks.push({
      label: "Aug 24+",
      short: "WTD",
      partial: true,
      us: {
        spend: usNow.spend_usd,
        enq: usNow.enquiries,
        enqPending: isEnquiryPending(usNow),
        disc: usNow.sales_calls_completed,
        jo: null,
      },
      au: {
        spend: auNow.spend_usd,
        enq: auNow.enquiries,
        enqPending: false,
        disc: auNow.sales_calls_completed,
        jo: auNow.job_orders_total,
      },
    });
    return weeks;
  }

  function renderTrends() {
    var host = $("#ev2-trends");
    if (!host) return;
    var weeks = weeklyTrendSeries();

    function trendCell(v, w, market, kind) {
      if (v == null && !(w.partial && kind === "enq" && ((market === "US" && w.us.enqPending) || false)))
        return "—";
      if (kind === "enq" && w.partial && market === "US" && w.us.enqPending) return "Pending";
      if (kind === "enq" && w.partial && market === "AU" && v === 0 && !w.partial) return num(v);
      if (typeof v === "number" && kind === "spend") return money(v, market === "AU" ? "AUD" : "USD");
      return num(v);
    }

    function row(label, market, kind, fn) {
      return "<tr><th scope=\"row\">" + esc(label) + "</th>" +
        weeks.map(function (w) {
          var v = fn(w);
          var partial = w.partial ? " partial" : "";
          return '<td class="num' + partial + '">' + esc(trendCell(v, w, market, kind)) + (w.partial && kind !== "spend" ? "*" : "") + "</td>";
        }).join("") + "</tr>";
    }

    host.innerHTML =
      '<table class="ev2-trend-table"><thead><tr><th>Metric</th>' +
      weeks.map(function (w) {
        return "<th class=\"num\">" + esc(w.label) + (w.partial ? "*" : "") + "</th>";
      }).join("") +
      "</tr></thead><tbody>" +
      row("US spend", "US", "spend", function (w) { return w.us.spend; }) +
      row("AU spend", "AU", "spend", function (w) { return w.au.spend; }) +
      row("US enquiries", "US", "enq", function (w) { return w.us.enq; }) +
      row("AU enquiries", "AU", "enq", function (w) { return w.au.enq; }) +
      row("US discovery calls", "US", "disc", function (w) { return w.us.disc; }) +
      row("AU discovery calls", "AU", "disc", function (w) { return w.au.disc; }) +
      row("AU job orders", "AU", "jo", function (w) { return w.au.jo; }) +
      "</tbody></table>" +
      '<p class="ev2-trend-note">* = partial week · WTD counts may be pending · Stage 1 started ~Aug 6 — full month-over-month needs more history</p>';
  }

  function renderDecisions() {
    var el = $("#ev2-decisions");
    if (!el) return;
    var cards = [
      { m: "US", type: "Budget", v: "Controlled Ramp", r: "Operating at ~18% of historical agency spend pace" },
      { m: "AU", type: "Budget", v: "Controlled Ramp", r: "Operating at ~15% of historical agency spend pace" },
      { m: "US", type: "Bidding", v: "CORE Max Conv · ROLES Max Clicks", r: "CORE optimizes to primary conversions; ROLES holds Max Clicks with CPC cap" },
      { m: "AU", type: "Bidding", v: "Hold Max Clicks", r: "Maintain CPC controls while GA4/GTM conversions build attribution history" },
    ];
    el.innerHTML = cards.map(function (c) {
      return '<article class="ev2-card ev2-decision"><div class="label">' + esc(c.m + " " + c.type) +
        '</div><div class="verdict">' + esc(c.v) + '</div><p class="reason">' + esc(c.r) + "</p></article>";
    }).join("");
  }

  function renderAttribution() {
    var el = $("#ev2-attribution");
    if (!el) return;
    el.innerHTML =
      '<ul class="ev2-status-list">' +
      '<li><div>GCLID on Zoho rows — most records still lack a paid click ID</div><span class="ev2-status-badge broken">Weak</span></li>' +
      '<li><div>Sales labels — Cheyenne Mon–Tue pending this week</div><span class="ev2-status-badge pending">Pending</span></li>' +
      '<li><div>Phone calls — weekend US calls were job seekers, not employers</div><span class="ev2-status-badge degraded">Watch</span></li>' +
      '<li><div><a href="employer-signal-report.html">Employer signal report</a> · <a href="attribution.html">Funnel &amp; CRM</a></div></li>' +
      "</ul>";
  }

  function renderDetails() {
    var days = ((STATE.snapshot.performance_us || {}).scoreboard_now || {}).days || [];
    $("#ev2-daily-body").innerHTML = days.map(function (d) {
      var n = d.now || {};
      return "<tr><th scope=\"row\">" + esc(d.dow + " " + d.date.slice(5)) +
        '</th><td class="num">' + esc(money(n.cost_usd, "USD")) +
        '</td><td class="num">' + esc(num(n.clicks)) +
        '</td><td class="num">' + esc(pct(n.ctr_pct)) + "</td></tr>";
    }).join("") || "<tr><td colspan=\"4\">—</td></tr>";

    $("#ev2-legacy-summary").textContent =
      "Legacy agency spent ~5× more per week at worse CPC. Stage 1 is cheaper — employer enquiry volume is the benchmark now, not Ads conversions.";
  }

  function renderAll() {
    renderHeader();
    renderCommentary();
    renderScorecard();
    renderFunnels();
    renderTrends();
    renderDecisions();
    renderAttribution();
    renderDetails();
  }

  function bindSeg() {
    document.querySelectorAll("[data-ev2-window]").forEach(function (btn) {
      btn.addEventListener("click", function () {
        STATE.window = btn.getAttribute("data-ev2-window");
        document.querySelectorAll("[data-ev2-window]").forEach(function (b) {
          var on = b.getAttribute("data-ev2-window") === STATE.window;
          b.classList.toggle("on", on);
          b.setAttribute("aria-pressed", on ? "true" : "false");
        });
        renderHeader();
        renderScorecard();
        renderFunnels();
      });
    });
  }

  function init() {
    Promise.all([
      fetchJson("data/executive-snapshot.json"),
      fetchJson("data/executive-snapshot-frozen-2026-08-10.json").catch(function () { return null; }),
    ]).then(function (res) {
      STATE.snapshot = res[0];
      STATE.archivePrior = res[1];
      var loading = $(".ev2-loading");
      if (loading) loading.hidden = true;
      bindSeg();
      renderAll();
    }).catch(function (err) {
      $("#ev2-root").innerHTML = '<div class="ev2-error">' + esc(err.message) + "</div>";
    });
  }

  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", init);
  else init();
})();
