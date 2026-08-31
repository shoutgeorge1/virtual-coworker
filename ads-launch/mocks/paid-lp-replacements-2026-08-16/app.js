/**
 * Version One = launch draft (long company page + guided match).
 * Version Two stays in the switcher as backup. Existing /us /au is NOT in this file.
 * MOCK only — contract.js mirrors production events; nothing posts live.
 */
(function () {
  const ASSET = "../assets";
  const STARS = '<span class="stars" aria-hidden="true">★★★★★</span>';

  const ROLES = [
    { chip: "Admin / EA", role: "Administrative / virtual assistant", category: "administrative-support", blurb: "Inbox, calendar, documents, follow-up." },
    { chip: "Bookkeeping", role: "Bookkeeping support", category: "bookkeeping", blurb: "Invoices, reconciliations, routine reporting." },
    { chip: "Marketing / social", role: "Digital marketing support", category: "digital-marketing", blurb: "Content, campaigns, posting, reporting." },
    { chip: "Customer support", role: "Customer service support", category: "customer-service", blurb: "Tickets, chat, and customer follow-through." },
    { chip: "Sales", role: "Sales support", category: "sales", blurb: "Lists, outreach support, CRM hygiene." },
    { chip: "Recruiting / HR", role: "Recruitment support", category: "recruitment", blurb: "Sourcing support, scheduling, HR admin." },
  ];
  const SCHEDULES = [
    { id: "full-time", label: "Full-time" },
    { id: "part-time", label: "Part-time" },
    { id: "mix", label: "Not sure / mix" },
  ];
  const POSITIONS = [
    { id: "1", label: "1 person" },
    { id: "2-3", label: "2–3 people" },
    { id: "4-10", label: "4–10 people" },
    { id: "11+", label: "11+" },
  ];
  const SIZES = [
    { id: "1-10", label: "1–10" },
    { id: "11-50", label: "11–50" },
    { id: "51-200", label: "51–200" },
    { id: "201+", label: "201+" },
  ];
  const LOGOS = [
    ["client-good-co.png", "Good Co."],
    ["client-credit-card-compare.png", "Credit Card Compare"],
    ["client-buzinga.png", "Buzinga Apps"],
    ["client-proactive-media.png", "ProActive Media"],
    ["client-learning-deli.png", "The Learning Deli"],
    ["client-recruitloop.png", "RecruitLoop"],
  ];
  const QUOTES = [
    { text: "They’ve exceeded our expectations! The recruiting process was well organized, and I feel we were matched very well.", by: "Kyrstin H. · General Manager · College Hunks" },
    { text: "I’m beyond happy with the candidate hired for the role I needed to fill! Everyone I’ve dealt with has been professional and polished.", by: "Laura W. · Founder · Good Co." },
    { text: "They found me an awesome VA with loads of work experience in finance. Honestly, it’s something I should have done a long time ago!", by: "David Boyd · Director · Credit Card Compare" },
    { text: "I have worked with a number of virtual staff services. The team at Virtual Coworker have provided me with the best value to date.", by: "Logan Merrick · Strategic Director · Buzinga Apps" },
  ];

  const params = new URLSearchParams(location.search);
  const previewOn = params.get("preview") === "1" || params.get("clean") === "1";
  if (previewOn) document.documentElement.classList.add("preview");

  const state = {
    version: "one",
    market: "us",
    surface: "core",
    quiz: 1,
    quizStarted: false,
    roleChip: "",
    schedule: "",
    positions: "",
    size: "",
    hours: "",
    startedAt: 0,
    error: "",
    fieldErrors: {},
  };

  function bookRole() {
    return ROLES.find((r) => r.category === "bookkeeping");
  }

  function mcopy() {
    const au = state.market === "au";
    return {
      au: au,
      phone: au ? "1300 886 740" : "(888) 964-8644",
      tel: au ? "tel:+611300886740" : "tel:+18889648644",
      google: au ? "4.8 Google · 23 reviews" : "5.0 Google · 39 reviews",
      clutch: "4.9 Clutch · 7 reviews",
      entity: au ? "Virtual Coworker Pty. Ltd. · ABN 49 154 746 004" : "Virtual Coworker Inc.",
      nap: au
        ? "AU office · Level 8/11 York St, Sydney NSW 2000 · ABN 49 154 746 004"
        : "US office · 750 N San Vicente Blvd, West Hollywood, CA 90069",
      hoursDefault: au ? "AU business hours" : "US business hours",
      hero: au ? ASSET + "/people/va-au.jpg" : ASSET + "/people/va-us.jpg",
      scene: au ? ASSET + "/people/hero-au-2026.jpg" : ASSET + "/people/hero-us-2026.jpg",
      admin: au ? "employment admin" : "payroll and HR",
      kicker: au
        ? "Australia · Businesses · Philippines staffing · Since 2011"
        : "United States · Employers · Philippines staffing · Since 2011",
      hoursNote: au
        ? "Dedicated Filipino staff on Australian hours. We recruit. You interview. We handle employment admin."
        : "Dedicated Filipino staff on your US hours. We recruit. You interview. We handle payroll and HR.",
    };
  }

  function headlines(c) {
    const book = state.surface === "bookkeeping";
    if (state.version === "one") {
      return {
        h1: book
          ? (c.au
            ? "Hire bookkeeping staff who work Australian hours."
            : "Hire bookkeeping staff who work your hours.")
          : (c.au
            ? "Hire reliable Filipino staff who work Australian hours."
            : "Hire reliable Filipino staff who work your hours."),
        lead: book
          ? "Tell us the workload. We recruit, vet and introduce bookkeepers you can interview."
          : "Tell us the role. We recruit, vet and introduce candidates you can interview.",
      };
    }
    return {
      h1: book
        ? "Get matched with vetted Filipino bookkeeping staff"
        : "Get matched with vetted Filipino staff who work your hours",
      lead: book
        ? "We recruit a dedicated bookkeeper. You meet them on video. Serving businesses since 2011."
        : "A dedicated teammate from the Philippines, on your clock. We recruit and vet. You interview. Serving businesses since 2011.",
    };
  }

  function firstQuizStep() {
    return state.surface === "bookkeeping" ? 2 : 1;
  }

  function quizTotal() {
    return state.surface === "bookkeeping" ? 2 : 3;
  }

  function quizDisplayIndex() {
    if (state.surface === "bookkeeping") return state.quiz === 3 ? 2 : 1;
    return state.quiz;
  }

  function lockBookkeepingRole() {
    if (state.surface === "bookkeeping") {
      state.roleChip = bookRole().chip;
      if (state.quiz < 2) state.quiz = 2;
    }
  }

  function selectedRole() {
    if (state.surface === "bookkeeping") return bookRole();
    return ROLES.find((r) => r.chip === state.roleChip) || null;
  }

  function ctx() {
    const role = selectedRole();
    return {
      market: state.market,
      category: role && role.category ? role.category : (state.surface === "bookkeeping" ? "bookkeeping" : ""),
      variant: "",
      lp_surface: "form",
      cta_mode: "form_primary",
      landing_type: "form_lp",
    };
  }

  function ensureAttr() {
    const c = ctx();
    return VCContract.captureAttribution(state.market, {
      category: c.category,
      variant: "",
      lp_variant: "",
    });
  }

  function logoRow() {
    return LOGOS.map(([f, a]) => `<img src="${ASSET}/clients/${f}" alt="${a}">`).join("");
  }

  function starLine(c) {
    return `<p class="starline">${STARS} ${c.google} · ${STARS} ${c.clutch}</p>`;
  }

  function proofPills(c) {
    return `${STARS} <span class="pill">${c.google}</span> ${STARS} <span class="pill">${c.clutch}</span>
      <span class="pill">450K+ LinkedIn</span><span class="pill">290K+ Facebook</span><span class="pill">Since 2011</span>`;
  }

  function quoteBox() {
    const q = state.surface === "bookkeeping" ? QUOTES[2] : QUOTES[0];
    return `<aside class="quote"><p>“${q.text}”</p><cite>${q.by}</cite></aside>`;
  }

  function nav(c) {
    return `<div class="wrap"><nav class="lp-nav">
      <img src="${ASSET}/logo-vc.png" alt="Virtual Coworker" />
      <div class="links">
        <a href="#how">How it works</a>
        <a href="#roles">Roles</a>
        <a href="#stories">Stories</a>
        <a href="#gate">Hire</a>
      </div>
      <a class="call js-phone" href="${c.tel}">${c.phone}</a>
    </nav></div>`;
  }

  function hiddenFields() {
    const role = selectedRole();
    const attr = ensureAttr();
    return `<div class="hid" aria-hidden="true">
      <input name="website" tabindex="-1" autocomplete="off" value="" />
      <input name="utm_source" value="${attr.utm_source}" readonly />
      <input name="utm_medium" value="${attr.utm_medium}" readonly />
      <input name="utm_campaign" value="${attr.utm_campaign}" readonly />
      <input name="utm_term" value="${attr.utm_term}" readonly />
      <input name="utm_content" value="${attr.utm_content}" readonly />
      <input name="gclid" value="${attr.gclid}" readonly />
      <input name="gbraid" value="${attr.gbraid}" readonly />
      <input name="wbraid" value="${attr.wbraid}" readonly />
      <input name="role" value="${role ? role.role : ""}" readonly />
      <input name="category" value="${role ? role.category : ""}" readonly />
      <input name="schedule" value="${state.schedule}" readonly />
      <input name="positions_needed" value="${state.positions}" readonly />
      <input name="company_size" value="${state.size}" readonly />
      <input name="market" value="${state.market}" readonly />
      <input name="intent" value="employer" readonly />
      <input name="lp_version" value="${VCContract.LP_VERSION}" readonly />
    </div>`;
  }

  function seeker() {
    return `<p class="seeker">Hiring for a business? Looking for work? <a class="js-careers" href="https://virtualcoworker.com.ph">Philippines careers</a></p>`;
  }

  function footer(c) {
    return `<footer class="lp"><div class="wrap">
      <strong>${c.entity}</strong><br>${c.nap}<br>
      Philippines recruitment hub · Serving employers since 2011 ·
      <a href="https://www.virtualcoworker.app/privacy">Privacy</a> ·
      <a href="https://www.virtualcoworker.app/terms">Terms</a>
    </div></footer>`;
  }

  function chips(items, selected, act) {
    return `<div class="chips">${items.map((it) => {
      const id = it.id || it.chip;
      const label = it.label || it.chip;
      const on = selected === id ? " on" : "";
      return `<button type="button" class="chip${on}" data-act="${act}" data-v="${id}">${label}</button>`;
    }).join("")}</div>`;
  }

  function contactForm(c, submitLabel) {
    const ph = c.au ? "0400 000 000" : "(201) 555-0123";
    const err = (k) => state.fieldErrors[k] ? `<span class="err">${state.fieldErrors[k]}</span>` : "";
    return `<form id="form" onsubmit="return false;">
      ${hiddenFields()}
      <label>Full name<input name="name" autocomplete="name" data-contact="1" />${err("name")}</label>
      <label>Work email<input name="email" type="email" autocomplete="email" data-contact="1" />${err("email")}</label>
      <label>Phone<input name="phone" type="tel" placeholder="${ph}" data-contact="1" />${err("phone")}</label>
      <label>Company website (optional)<input name="company_website" placeholder="https://" /></label>
      ${state.error ? `<p class="err">${state.error}</p>` : ""}
      <button class="submit" type="button" data-act="submit">${submitLabel}</button>
      <p class="hint review-only">Mock form — labeled MOCK. Does not post to production.</p>
      <p class="hint">We’ll use this to build your hiring brief. We don’t sell your information.</p>
      ${seeker()}
    </form>`;
  }

  function gateInner(c) {
    const total = quizTotal();
    const shown = quizDisplayIndex();
    const pct = total === 2 ? (shown === 1 ? "50%" : "100%") : (state.quiz === 1 ? "33%" : state.quiz === 2 ? "66%" : "100%");
    const showBack = state.quiz > firstQuizStep();
    let inner = "";
    if (state.quiz === 1) {
      inner = `<p class="step-n">${shown} of ${total}</p>
        <h2>What role are you hiring for?</h2>
        ${chips(ROLES, state.roleChip, "roleChip")}`;
    } else if (state.quiz === 2) {
      inner = `<p class="step-n">${shown} of ${total}</p>
        <h2>${state.surface === "bookkeeping" ? "What does the bookkeeping seat look like?" : "Hours and how many people"}</h2>
        <p class="gate-label">Full-time or part-time</p>${chips(SCHEDULES, state.schedule, "schedule")}
        <p class="gate-label">How many people</p>${chips(POSITIONS, state.positions, "positions")}
        <p class="gate-label">Company size (optional)</p>${chips(SIZES, state.size, "size")}
        <p class="gate-label">They work</p>${chips(
          [{ id: "US business hours", label: "US hours" }, { id: "AU business hours", label: "AU hours" }],
          state.hours,
          "hours"
        )}
        <button class="submit" type="button" data-act="next2" ${state.schedule && state.positions ? "" : "disabled"}>Continue</button>
        ${showBack ? `<button class="ghost" type="button" data-act="back">Back</button>` : ""}`;
    } else {
      const summary = [state.roleChip, state.schedule, state.positions, state.hours].filter(Boolean).join(" · ");
      inner = `<p class="step-n">${shown} of ${total}</p>
        <h2>Where should we send your hiring brief?</h2>
        <p class="hint">${summary}</p>
        ${contactForm(c, "Get my hiring brief")}
        ${showBack ? `<button class="ghost" type="button" data-act="back">Back</button>` : ""}`;
    }
    return `<div class="gate" id="gate">
      <div class="bar" aria-hidden="true"><span style="width:${pct}"></span></div>
      ${hiddenFields()}
      ${inner}
      ${state.quiz < 3 ? seeker() : ""}
    </div>`;
  }

  function processBand(c) {
    return `<section class="band white" id="how">
      <div class="wrap">
        <h2>How hiring works</h2>
        <p class="lead">Tell us the role. A specialist reviews the seat. We recruit after you’re aligned. You interview. We handle ${c.admin}.</p>
        <div class="grid-steps">
          <div class="step"><b>1. You tell us</b><p>Role, hours, and how many people. We turn that into a hiring brief.</p></div>
          <div class="step"><b>2. We scope</b><p>A staffing specialist reviews the seat, timeline, and hourly-rate structure.</p></div>
          <div class="step"><b>3. We recruit</b><p>Philippines team sources and vets after you’re aligned. You meet people on video.</p></div>
          <div class="step"><b>4. We stay</b><p>You choose who starts. We handle onboarding, ${c.admin}, and the time tracker.</p></div>
        </div>
      </div>
    </section>`;
  }

  function roleBand() {
    const locked = state.surface === "bookkeeping";
    return `<section class="band mist" id="roles">
      <div class="wrap">
        <h2>Roles we hire for</h2>
        <p class="lead">Stage 1 seats only. Dedicated staff, not a rotating freelance pool.</p>
        <div class="role-grid">
          ${ROLES.map((r) => {
            const on = selectedRole() && selectedRole().chip === r.chip ? " on" : "";
            const act = locked ? "toGate" : "roleCard";
            return `<button type="button" class="role-card${on}" data-act="${act}" data-v="${r.chip}"><b>${r.chip}</b><span>${r.blurb}</span></button>`;
          }).join("")}
        </div>
      </div>
    </section>`;
  }

  function whyBand(c) {
    return `<section class="band sand" id="why">
      <div class="wrap split">
        <div>
          <h2>Why companies stay with Virtual Coworker</h2>
          <div class="why-grid" style="grid-template-columns:1fr 1fr;margin-top:1.4rem">
            <div><h3>Since 2011</h3><p>A staffing company, not a gig app. US and Australian offices. Philippines recruitment hub.</p></div>
            <div><h3>Your hours</h3><p>Dedicated staff recruited to ${c.hoursDefault.toLowerCase()}. Full-time or part-time.</p></div>
            <div><h3>You choose</h3><p>You interview on video. Nobody is assigned to you as a leftover profile.</p></div>
            <div><h3>We employ</h3><p>Once you hire, we handle ${c.admin} and stay on the account.</p></div>
          </div>
        </div>
        <img class="scene-photo" src="${ASSET}/people/trust-consult.png" alt="Virtual Coworker consult — existing company photograph" />
      </div>
    </section>`;
  }

  function peopleBand() {
    return `<section class="band white" id="people">
      <div class="wrap">
        <h2>The team that recruits your hire</h2>
        <p class="lead">Philippines recruitment floor. US and Australian offices behind the account.</p>
        <img class="wide-photo" src="${ASSET}/people/trust-team-office.png" alt="Virtual Coworker team at work — existing company photograph" />
      </div>
    </section>`;
  }

  function storiesBand() {
    const featured = state.surface === "bookkeeping" ? QUOTES[2] : QUOTES[0];
    const rest = QUOTES.filter((q) => q !== featured);
    return `<section class="band mist" id="stories">
      <div class="wrap">
        <h2>What employers say</h2>
        <div class="quote-grid">
          <aside class="quote feat"><p>“${featured.text}”</p><cite>${featured.by}</cite></aside>
          ${rest.map((q) => `<aside class="quote"><p>“${q.text}”</p><cite>${q.by}</cite></aside>`).join("")}
        </div>
      </div>
    </section>`;
  }

  function modelBand(c) {
    return `<section class="band white" id="model">
      <div class="wrap model-grid">
        <div>
          <h2>Full-time, part-time, hourly rates</h2>
          <p>Seats can be full-time or part-time. Dedicated staff work your clock. The hiring brief explains the recruiting path, timeline, and hourly-rate structure for that seat. Live prices are not listed on this page because rates depend on role, seniority, and hours.</p>
        </div>
        <div>
          <h2>How we operate</h2>
          <p>We recruit and vet in the Philippines. You interview. We handle ${c.admin} after you hire. We do not reprint unverified rankings, “top 1%” claims, or fake certificates here.</p>
        </div>
      </div>
    </section>`;
  }

  function faqBand(c) {
    const hours = c.au ? "Australian business hours" : "US business hours";
    const items = [
      ["What happens after I tell you the role?", "A staffing specialist reviews your answers and sends a hiring brief — recruiting path, timeline, and hourly-rate structure. Then we recruit if you’re aligned. You interview on video."],
      ["Full-time or part-time?", "Both. Tell us the capacity you need. Dedicated staff, not a rotating freelancer for the afternoon."],
      [c.au ? "Can they work Australian hours?" : "Can they work US hours?", `Yes. We recruit for ${hours}. Hours are confirmed before recruiting starts.`],
      [c.au ? "Do you handle employment admin?" : "Do you handle payroll?", `Yes. Once you hire, we handle onboarding, ${c.admin}, and the time tracker.`],
      ["How do rates work?", "Hourly rates depend on the seat, hours, and seniority. We’ll explain the structure in the hiring brief rather than publish a live price here."],
      ["Who is this page for?", "Employers hiring staff. If you’re looking for work, use the Philippines careers link."],
    ];
    return `<section class="band sand" id="faq">
      <div class="wrap" style="max-width:44rem">
        <h2>Questions employers ask</h2>
        ${items.map(([q, a]) => `<details><summary>${q}</summary><p>${a}</p></details>`).join("")}
      </div>
    </section>`;
  }

  function closerBand(c) {
    return `<section class="band ocean" id="again">
      <div class="wrap closer">
        <div>
          <h2>Ready to hire?</h2>
          <p class="lead">Tell us the role. We’ll build the hiring brief and walk you through recruiting.</p>
          <div class="cta-row">
            <button type="button" class="submit inline" data-act="toGate">${state.surface === "bookkeeping" ? "Tell us the workload" : "Tell us the role"}</button>
            <a class="call js-phone" href="${c.tel}">${c.phone}</a>
          </div>
        </div>
        <img class="scene-photo" src="${c.scene}" alt="Virtual Coworker — existing brand photograph" />
      </div>
    </section>`;
  }

  function renderOne() {
    const c = mcopy();
    const h = headlines(c);
    lockBookkeepingRole();
    if (!state.hours) state.hours = c.hoursDefault;
    document.title = state.surface === "bookkeeping"
      ? "Hire bookkeeping staff | Virtual Coworker"
      : "Hire dedicated Filipino staff | Virtual Coworker";
    return `${nav(c)}
      <section class="hero">
        <div class="wrap hero-grid">
          <div>
            <h1>${h.h1}</h1>
            <p class="lead">${h.lead}</p>
            ${starLine(c)}
            ${gateInner(c)}
          </div>
          <img class="hero-photo" src="${c.hero}" alt="Dedicated Virtual Coworker staff at work — existing paid landing photograph" />
        </div>
      </section>
      <section class="logos"><div class="wrap">
        <div class="logo-row">${logoRow()}</div>
        <p class="starline" style="text-align:center;margin:.9rem 0 0">${STARS} ${c.google} · ${STARS} ${c.clutch} · Serving employers since 2011</p>
      </section>
      ${processBand(c)}
      ${roleBand()}
      ${whyBand(c)}
      ${peopleBand()}
      ${storiesBand()}
      ${modelBand(c)}
      ${faqBand(c)}
      ${closerBand(c)}
      ${footer(c)}`;
  }

  function process(c) {
    return `<div class="wrap" id="how"><h3 class="sec">How it works</h3>
      <p class="lead" style="max-width:40rem">We recruit and shortlist. You interview on video.</p>
      <div class="grid-steps">
        <div class="step"><b>1 · Scope</b>A specialist follows up about the seat, hours, and how many people.</div>
        <div class="step"><b>2 · Recruit</b>Philippines team sources and vets dedicated staff.</div>
        <div class="step"><b>3 · You pick</b>Profiles with hourly rates. Video interview. Your yes first.</div>
        <div class="step"><b>4 · We stay</b>Onboarding, ${c.admin}, time tracker.</div>
      </div></div>`;
  }

  function renderTwo() {
    const c = mcopy();
    const h = headlines(c);
    document.title = "Replacement LP · Version Two backup";
    return `<div class="v2">${nav(c)}
      <div class="wrap">
        <section class="grid2">
          <div>
            <p class="kicker">${c.kicker}${state.surface === "bookkeeping" ? " · Bookkeeping" : ""}</p>
            <h1>${h.h1}</h1>
            <p class="lead">${h.lead}</p>
            <ul class="ticks">
              <li>${c.hoursNote}</li>
              <li>You interview before anyone starts.</li>
              <li>${c.au ? "West Hollywood + Sydney + Philippines recruitment hub." : "US and Australian offices. Philippines recruitment hub."}</li>
            </ul>
            <div class="proof-row">${proofPills(c)}</div>
            ${quoteBox()}
            <div class="cta-row" style="margin-top:1rem">
              <a class="submit inline" href="#form">Tell us who you need</a>
              <a class="call js-phone" href="${c.tel}">${c.phone}</a>
            </div>
          </div>
          <div>
            <img class="office" src="${ASSET}/people/trust-team-office.png" alt="Existing Virtual Coworker team photograph" />
          </div>
        </section>
      </div>
      <section class="logos"><div class="wrap">
        <div class="logo-row">${logoRow()}</div>
      </div></section>
      ${process(c)}
      <div class="wrap">
        <div class="card" style="max-width:34rem;margin:1.2rem 0 0" id="form-wrap">
          <p class="eyebrow">After you’ve seen how it works</p>
          <h2 id="form">Tell us who you need</h2>
          ${contactForm(c, "Tell us who you need")}
        </div>
      </div>
      ${footer(c)}</div>`;
  }

  function bind() {
    document.querySelectorAll(".js-phone").forEach((a) => {
      a.addEventListener("click", () => {
        VCContract.trackPhoneClick(ctx());
      });
    });
    document.querySelectorAll(".js-careers").forEach((a) => {
      a.addEventListener("click", (e) => {
        e.preventDefault();
        VCContract.trackEvent("job_seeker_redirected", Object.assign({}, ctx(), { source: "lead_gate_mock" }));
        window.open("https://virtualcoworker.com.ph", "_blank", "noopener");
      });
    });
    document.querySelectorAll("[data-contact]").forEach((el) => {
      el.addEventListener("focus", () => {
        if (!state.startedAt) state.startedAt = Date.now();
        VCContract.markFormStarted(ctx());
      });
    });
    const peek = document.querySelector(".review-peek");
    if (peek) peek.href = "?review=1" + location.hash;
  }

  function render() {
    const view = document.getElementById("view");
    view.innerHTML = state.version === "one" ? renderOne() : renderTwo();
    document.querySelectorAll("[data-sw]").forEach((b) => {
      const on =
        (b.dataset.sw === "version" && b.dataset.v === state.version) ||
        (b.dataset.sw === "market" && b.dataset.v === state.market) ||
        (b.dataset.sw === "surface" && b.dataset.v === state.surface);
      b.classList.toggle("on", on);
    });
    const hash = [state.version, state.market, state.surface].join("-");
    if (location.hash.replace("#", "") !== hash) location.hash = hash;
    bind();
  }

  function fireQuizStep(step, answer) {
    const extra = Object.assign({}, ctx(), {
      step: String(step),
      answer: answer || "",
      assist_type: "guided_match",
      company_size: state.size,
      positions_needed: state.positions,
      ads_conversion: false,
      bidding_primary: false,
    });
    markGuidedMatchStarted(step, extra);
    VCContract.trackEvent("quiz_step", extra);
  }

  function markGuidedMatchStarted(step, extra) {
    if (state.quizStarted) return;
    state.quizStarted = true;
    const payload = Object.assign({}, extra || {}, ctx(), {
      step: String(step),
      assist_type: "guided_match",
      ads_conversion: false,
      bidding_primary: false,
      role_preselected: state.surface === "bookkeeping",
    });
    VCContract.trackEvent("quiz_started", payload);
    VCContract.trackEvent("guided_match_started", Object.assign({}, payload, {
      alias_of: "quiz_started",
    }));
  }

  function fireStepTwoComplete() {
    const extra = Object.assign({}, ctx(), {
      step: "2",
      answer: "complete",
      assist_type: "guided_match",
      company_size: state.size,
      positions_needed: state.positions,
      schedule: state.schedule,
      ads_conversion: false,
      bidding_primary: false,
    });
    VCContract.trackEvent("quiz_step_completed", extra);
  }

  function fireContactStepReached() {
    const extra = Object.assign({}, ctx(), {
      result: (selectedRole() && selectedRole().role) || "",
      company_size: state.size,
      positions_needed: state.positions,
      schedule: state.schedule,
      assist_type: "guided_match",
      ads_conversion: false,
      bidding_primary: false,
      funnel_step: "contact_step_reached",
    });
    VCContract.trackEvent("quiz_completed", extra);
    VCContract.trackEvent("contact_step_reached", extra);
    VCContract.trackEvent("lead_magnet_completed", Object.assign({}, ctx(), {
      magnet: "guided_match",
      result_role: (selectedRole() && selectedRole().role) || "",
      company_size: state.size,
      positions_needed: state.positions,
      ads_conversion: false,
      bidding_primary: false,
    }));
  }

  async function submit() {
    const form = document.getElementById("form") || document.querySelector("form");
    if (!form) return;
    const fd = new FormData(form);
    const name = String(fd.get("name") || "").trim();
    const email = String(fd.get("email") || "").trim();
    const phone = String(fd.get("phone") || "").trim();
    const errs = {};
    if (!name) errs.name = "Enter your name.";
    if (!email) errs.email = "Enter your work email.";
    if (!phone) errs.phone = "Enter a phone number.";
    state.fieldErrors = errs;
    state.error = "";
    if (Object.keys(errs).length) {
      VCContract.trackEvent("employer_form_validation_error", Object.assign({}, ctx(), {
        fields: Object.keys(errs).join(","),
      }));
      render();
      return;
    }
    const attr = VCContract.readAttribution(state.market, { category: ctx().category });
    const hoursLine = state.hours ? "Hours requested: " + state.hours : "";
    const payload = Object.assign({}, attr, {
      name: name,
      email: email,
      phone: VCContract.normalizePhone(phone, state.market) || phone,
      company: String(fd.get("company") || "").trim(),
      role: (selectedRole() && selectedRole().role) || "",
      category: ctx().category,
      variant: "",
      intent: "employer",
      website: String(fd.get("website") || ""),
      company_website: String(fd.get("company_website") || "").trim(),
      form_started_at: state.startedAt || Date.now() - 3000,
      market: state.market,
      lp_version: VCContract.LP_VERSION,
      submitted_at: new Date().toISOString(),
      company_size: state.size || "",
      positions_needed: state.positions || "",
      schedule: state.schedule || "",
      hiring_timeline: "",
      message: hoursLine,
      lp_surface: "form",
      cta_mode: "form_primary",
      landing_type: "form_lp",
      lp_variant: "",
    });
    const res = VCContract.mockLeadApi(payload);
    if (res.status !== 200 || !res.json.ok || !res.json.submission_id) {
      if (res.json.code === "honeypot" || res.json.code === "too_fast" || res.json.code === "job_seeker") {
        VCContract.trackEvent("spam_or_applicant_rejected", { market: state.market, code: res.json.code });
      }
      state.error = res.json.error || "Could not deliver (mock).";
      render();
      return;
    }
    VCContract.trackValidEmployerSubmit({
      market: state.market,
      submissionId: res.json.submission_id,
      role: payload.role,
      category: payload.category,
      conversionEligible: true,
      companySize: payload.company_size,
      positionsNeeded: payload.positions_needed,
      landingPage: attr.landing_page_url,
      utmSource: attr.utm_source,
      utmMedium: attr.utm_medium,
      utmCampaign: attr.utm_campaign,
      gclid: attr.gclid,
      gbraid: attr.gbraid,
      wbraid: attr.wbraid,
      submittedAt: payload.submitted_at,
      lpSurface: "form",
      ctaMode: "form_primary",
      leadScore: res.json.lead_score,
      estimatedLeadValue: res.json.estimated_lead_value,
      valueKind: res.json.value_kind,
      fitLabel: res.json.fit_label,
    });
    const q = new URLSearchParams({ market: state.market, sid: res.json.submission_id });
    if (payload.category) q.set("category", payload.category);
    location.href = "thank-you.html?" + q.toString();
  }

  function scrollGate() {
    const el = document.getElementById("gate");
    if (el) el.scrollIntoView({ behavior: "smooth", block: "center" });
  }

  document.getElementById("switcher").addEventListener("click", (e) => {
    const b = e.target.closest("[data-sw]");
    if (!b) return;
    if (b.dataset.sw === "version") {
      state.version = b.dataset.v;
      state.quiz = firstQuizStep();
      state.quizStarted = false;
      state.startedAt = 0;
      state.fieldErrors = {};
      state.error = "";
      VCContract.resetFormStartedForQa();
    }
    if (b.dataset.sw === "market") state.market = b.dataset.v;
    if (b.dataset.sw === "surface") {
      state.surface = b.dataset.v;
      if (b.dataset.v === "bookkeeping") {
        state.roleChip = bookRole().chip;
        state.quiz = 2;
      }
      if (b.dataset.v === "core") {
        state.roleChip = "";
        state.quiz = 1;
      }
    }
    render();
  });

  document.getElementById("view").addEventListener("click", (e) => {
    const b = e.target.closest("[data-act]");
    if (!b) return;
    const act = b.dataset.act;
    const v = b.dataset.v;
    if (act === "roleChip" || act === "roleCard") {
      if (state.surface === "bookkeeping") {
        scrollGate();
        return;
      }
      state.roleChip = v;
      fireQuizStep(1, v);
      state.quiz = 2;
      render();
      if (act === "roleCard") scrollGate();
    }
    if (act === "schedule" || act === "positions" || act === "size" || act === "hours") {
      state[act] = v;
      fireQuizStep(2, v);
      render();
    }
    if (act === "next2" && state.schedule && state.positions) {
      fireStepTwoComplete();
      state.quiz = 3;
      fireContactStepReached();
      render();
    }
    if (act === "back") {
      state.quiz = Math.max(firstQuizStep(), state.quiz - 1);
      render();
    }
    if (act === "toGate") {
      scrollGate();
    }
    if (act === "submit") submit();
  });

  const parts = (location.hash || "#one-us-core").replace("#", "").split("-");
  if (parts[0] === "one" || parts[0] === "two") state.version = parts[0];
  if (parts[1] === "us" || parts[1] === "au") state.market = parts[1];
  if (parts[2] === "bookkeeping" || parts[2] === "core") state.surface = parts[2];
  if (state.surface === "bookkeeping") {
    state.roleChip = bookRole().chip;
    state.quiz = 2;
  }
  ensureAttr();
  render();

  if (params.get("walk") === "1") {
    window.setTimeout(function () {
      const out = [];
      function click(sel) {
        const el = document.querySelector(sel);
        if (!el) throw new Error("missing " + sel);
        el.click();
      }
      try {
        if (state.surface === "core") click('[data-act="roleChip"][data-v="Admin / EA"]');
        click('[data-act="schedule"][data-v="full-time"]');
        click('[data-act="positions"][data-v="1"]');
        click('[data-act="next2"]');
        const field = document.querySelector("[data-contact]");
        field.focus();
        field.dispatchEvent(new Event("focus", { bubbles: true }));
        const names = (window.dataLayer || []).map((e) => e.event);
        const started = names.filter((n) => n === "employer_form_started").length;
        const roleFirst = names.indexOf("quiz_step") >= 0 && names.indexOf("employer_form_started") > names.indexOf("quiz_step");
        out.push("events=" + names.join(","));
        out.push("form_started=" + started);
        out.push(started === 1 && roleFirst && names.indexOf("employer_inquiry_submitted") === -1 ? "WALK_PASS" : "WALK_FAIL");
        if (state.surface === "bookkeeping") {
          out.push(document.body.innerText.indexOf("What role are you hiring for?") === -1 ? "SKIP_PASS" : "SKIP_FAIL");
        }
      } catch (err) {
        out.push("WALK_FAIL " + err.message);
      }
      const pre = document.createElement("pre");
      pre.id = "walk-out";
      pre.className = "review-only";
      pre.textContent = out.join("\n");
      document.body.appendChild(pre);
    }, 80);
  }
})();
