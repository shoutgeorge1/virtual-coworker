/**
 * Isolated mobile-CRO V2 mock. Production vision/ is untouched.
 * Guided-match after persuasion. Submit is VCContract.mockLeadApi — never hits /api/lead.
 */
(function () {
  const ASSET = "../assets";
  const PREVIEW = new URLSearchParams(location.search).get("preview") === "1"
    || new URLSearchParams(location.search).get("clean") === "1";
  if (PREVIEW) document.documentElement.classList.add("preview");
  if (new URLSearchParams(location.search).get("review") === "1") {
    document.documentElement.classList.remove("preview");
  }

  const ROLES = [
    { chip: "Admin / EA", role: "Administrative / virtual assistant", category: "administrative-support", blurb: "Inbox, calendar, documents, follow-up." },
    { chip: "Bookkeeping", role: "Bookkeeping support", category: "bookkeeping", blurb: "Invoices, reconciliations, routine reporting." },
    { chip: "Marketing / Social", role: "Digital marketing support", category: "digital-marketing", blurb: "Content, campaigns, posting, reporting." },
    { chip: "Customer Support", role: "Customer service support", category: "customer-service", blurb: "Tickets, chat, and customer follow-through." },
    { chip: "Sales", role: "Sales support", category: "sales", blurb: "Lists, outreach support, CRM hygiene." },
    { chip: "Recruiting / HR", role: "Recruitment support", category: "recruitment", blurb: "Sourcing support, scheduling, people admin." },
    { chip: "Other / Not sure", role: "Other / not sure", category: "", blurb: "Describe the help you need and we will match the role." },
  ];
  const SCHEDULES = [
    { id: "full-time", label: "Full-time", blurb: "Dedicated seat, your business hours." },
    { id: "part-time", label: "Part-time", blurb: "A dedicated person, fewer hours." },
    { id: "mix", label: "Not sure / mix", blurb: "We will talk it through." },
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
  const JOB_SEEKER = "Looking for work? View careers in the Philippines →";
  const CAREERS = "https://www.virtualcoworker.com.ph/careers/";

  const state = {
    market: "us",
    surface: "core",
    quiz: 1,
    quizStarted: false,
    roleChip: "",
    schedule: "",
    positions: "",
    size: "",
    tzNote: "",
    startedAt: 0,
    error: "",
    fieldErrors: {},
    submitting: false,
    name: "",
    email: "",
    phone: "",
    companyWebsite: "",
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
      hoursDefault: au ? "Australian business hours" : "US business hours",
      hoursShort: au ? "Australian hours" : "your hours",
      hoursPeople: au ? "Australian hours" : "US hours",
      admin: au ? "employment admin" : "payroll and HR",
      hero: au ? ASSET + "/people/va-au.jpg" : ASSET + "/people/va-us.jpg",
      heroAlt: au
        ? "Filipino teammate at work for an Australian business"
        : "Filipino teammate at work for a US business",
      closer: au ? ASSET + "/people/hero-au-2026.jpg" : ASSET + "/people/hero-us-2026.jpg",
      team: ASSET + "/people/trust-team-office.png",
      scene: ASSET + "/people/trust-consult.png",
    };
  }

  function headlines(c) {
    const book = state.surface === "bookkeeping";
    if (book) {
      return {
        h1: "Hire bookkeeping staff who work " + c.hoursShort + ".",
        diff: "A dedicated bookkeeper in the Philippines, on " + c.hoursPeople + ". Full-time or part-time. We recruit. You choose. We handle " + c.admin + ".",
      };
    }
    return {
      h1: "Hire reliable Filipino staff who work " + c.hoursShort + ".",
      diff: "Dedicated teammates in the Philippines, on " + c.hoursPeople + ". Full-time or part-time. We recruit. You choose. We handle employment.",
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
      ads_conversion: false,
      bidding_primary: false,
      assist_type: "guided_match",
    };
  }

  function logEvents() {
    const el = document.getElementById("log");
    if (!el) return;
    const last = (window.dataLayer || []).slice(-8).map((e) => e.event).filter(Boolean);
    el.textContent = last.join(" · ") || "events: (none yet)";
  }

  function markMatchStarted(stepN, answer) {
    const extra = Object.assign({}, ctx(), { step: String(stepN), answer: answer });
    if (!state.quizStarted) {
      state.quizStarted = true;
      VCContract.trackEvent("quiz_started", extra);
      VCContract.trackEvent("guided_match_started", Object.assign({}, extra, { alias_of: "quiz_started" }));
    }
    VCContract.trackEvent("quiz_step", extra);
    logEvents();
  }

  function onPhone(e) {
    VCContract.trackPhoneClick({
      market: state.market,
      category: ctx().category,
      variant: "",
      source: "paid_lp_nav",
    });
    logEvents();
  }

  function onCareers(e) {
    e.preventDefault();
    VCContract.trackEvent("job_seeker_redirected", Object.assign({}, ctx(), {
      intent: "job_seeker",
      destination: CAREERS,
      primary_eligible: false,
      bidding_primary: false,
      source: "paid_lp_footer",
    }));
    window.location.replace(CAREERS);
  }

  function tile(on, attrs, title, blurb) {
    return `<button type="button" class="tile${on ? " on" : ""}" ${attrs}>
      <b>${on ? "✓ " : ""}${title}</b>
      ${blurb ? `<span>${blurb}</span>` : ""}
    </button>`;
  }

  function nav(c) {
    return `<div class="wrap wrap-wide"><nav class="lp">
      <img src="${ASSET}/logo-vc.png" alt="Virtual Coworker" />
      <div class="links">
        <a href="#how">How it works</a>
        <a href="#trust">Trust</a>
        <a href="#match">Hire</a>
      </div>
      <a class="phone-pill js-phone" href="${c.tel}">${c.phone}</a>
    </nav></div>`;
  }

  function hero(c) {
    const h = headlines(c);
    const ctaLabel = state.surface === "bookkeeping" ? "See how bookkeeping hires work" : "See how hiring works";
    const copy = `<div>
      <h1>${h.h1}</h1>
      <p class="diff">${h.diff}</p>
      <p class="since">Staffing businesses since 2011.</p>
      <a class="cta" href="#how">${ctaLabel}</a>
    </div>
    <img class="hero-photo" src="${c.hero}" alt="${c.heroAlt}" />`;
    return `<section class="hero"><div class="wrap wrap-wide hero-grid">${copy}</div></section>`;
  }

  function statements(c) {
    return `
      <section class="band white statement" id="how">
        <div class="wrap">
          <p class="kicker">Your hours</p>
          <h2>They work ${c.hoursShort}.</h2>
          <p class="body">Dedicated staff recruited for ${c.hoursDefault} — not a rotating freelancer for the afternoon. Full-time or part-time.</p>
        </div>
      </section>
      <section class="band mist statement">
        <div class="wrap">
          <p class="kicker">You decide</p>
          <h2>We recruit. You choose.</h2>
          <p class="body">We source and vet in the Philippines. You interview on video. Nobody is assigned to you as a leftover profile.</p>
        </div>
      </section>
      <section class="band sand statement">
        <div class="wrap">
          <p class="kicker">Employment</p>
          <h2>We handle employment.</h2>
          <p class="body">Once you hire, we handle onboarding, ${c.admin}, and the time tracker. Smarter team expansion — you run the work.</p>
        </div>
      </section>`;
  }

  function trust(c) {
    return `<section class="band white" id="trust">
      <div class="wrap">
        <p class="kicker">A real staffing company</p>
        <h2>Since 2011.</h2>
        <p class="body">US and Australian offices. Philippines recruitment hub. Not a gig app. Placing Filipino staff for businesses since then.</p>
        <div class="trust-block">
          <div class="trust-item">
            <p class="n"><span class="stars" aria-hidden="true">★★★★★</span></p>
            <p>${c.google}</p>
          </div>
          <div class="trust-item">
            <p class="n"><span class="stars" aria-hidden="true">★★★★★</span></p>
            <p>${c.clutch}</p>
          </div>
        </div>
        <p class="hint" style="margin-top:2.2rem">450K+ LinkedIn. 290K+ Facebook <span class="review-only">(Facebook: CEO floor 11 Aug; live scrape blocked).</span></p>
      </div>
    </section>`;
  }

  function featuredQuote() {
    const q = state.surface === "bookkeeping" ? QUOTES[2] : QUOTES[0];
    return `<section class="band sand" id="stories">
      <div class="wrap">
        <p class="kicker">Employers</p>
        <blockquote class="quote">
          <p>“${q.text}”</p>
          <cite>${q.by}</cite>
        </blockquote>
      </div>
    </section>`;
  }

  function howSteps(c) {
    return `<section class="band mist" id="process">
      <div class="wrap">
        <p class="kicker">The process</p>
        <h2>How hiring works</h2>
        <p class="lead">Tell us the role when you are ready. We scope. We recruit after you are aligned. You interview.</p>
        <div class="step-stack">
          <div class="step">
            <b>1. You tell us</b>
            <p>Role, hours, and how many people. That becomes a hiring brief.</p>
          </div>
          <div class="step">
            <b>2. We scope</b>
            <p>A staffing specialist reviews the role, schedule, and requirements.</p>
          </div>
          <div class="step">
            <b>3. We recruit</b>
            <p>Philippines team sources and vets after you are aligned. You meet people on video.</p>
          </div>
          <div class="step">
            <b>4. We stay</b>
            <p>You choose who starts. We handle onboarding, ${c.admin}, and the time tracker.</p>
          </div>
        </div>
      </div>
    </section>`;
  }

  function socialProof() {
    return `<section class="band white">
      <div class="wrap">
        <div class="logo-row">
          ${LOGOS.map(([f, a]) => `<img src="${ASSET}/clients/${f}" alt="${a}">`).join("")}
        </div>
      </div>
    </section>
    <section class="band white" id="people">
      <div class="wrap wrap-wide">
        <p class="kicker">The team</p>
        <h2>The people who recruit your hire</h2>
        <p class="lead">Philippines recruitment floor. US and Australian offices behind the account.</p>
        <img class="wide" src="${ASSET}/people/trust-team-office.png" alt="Virtual Coworker recruitment team at work" />
      </div>
    </section>`;
  }

  function moreQuotes() {
    const feat = state.surface === "bookkeeping" ? QUOTES[2] : QUOTES[0];
    const rest = QUOTES.filter((q) => q !== feat);
    return `<section class="band sand">
      <div class="wrap wrap-wide">
        <p class="kicker">More from employers</p>
        <div class="quote-more">
          ${rest.map((q) => `<blockquote class="quote"><p>“${q.text}”</p><cite>${q.by}</cite></blockquote>`).join("")}
        </div>
      </div>
    </section>`;
  }

  function askCta() {
    const label = state.surface === "bookkeeping" ? "Tell us the workload" : "Tell us the role";
    return `<section class="band white">
      <div class="wrap">
        <h2>Ready to talk about a hire?</h2>
        <p class="lead">A few questions, then your details. We send a hiring brief. No live price on this page — rates depend on the role, hours, and seniority.</p>
        <a class="cta" href="#match">${label}</a>
      </div>
    </section>`;
  }

  function faq(c) {
    const items = [
      ["What happens after I tell you the role?", "A staffing specialist reviews your role, schedule and requirements, then sends a hiring brief with the recruiting path, timeline, and hourly-rate structure. Then we recruit if you are aligned. You interview on video."],
      ["Full-time or part-time?", "Both. Tell us the capacity you need. Dedicated staff, not a rotating freelancer for the afternoon."],
      [c.au ? "Can they work Australian hours?" : "Can they work US hours?", "Yes. We recruit for " + c.hoursDefault + ". Hours are confirmed before recruiting starts."],
      [c.au ? "Do you handle employment admin?" : "Do you handle payroll?", "Yes. Once you hire, we handle onboarding, " + c.admin + ", and the time tracker."],
      ["How do rates work?", "Hourly rates depend on the role, hours, and seniority. We’ll explain the structure in the hiring brief rather than publish a live price here."],
      ["Who is this page for?", "Employers hiring staff. If you are looking for work, use the Philippines careers link in the footer."],
    ];
    return `<section class="band mist" id="faq">
      <div class="wrap">
        <h2>Questions employers ask</h2>
        ${items.map(([q, a]) => `<details><summary>${q}</summary><p>${a}</p></details>`).join("")}
      </div>
    </section>`;
  }

  function closer(c) {
    const label = state.surface === "bookkeeping" ? "Tell us the workload" : "Tell us the role";
    return `<section class="band ocean" id="again">
      <div class="wrap">
        <p class="kicker">Next step</p>
        <h2>Ready to hire?</h2>
        <p class="lead">Tell us the ${state.surface === "bookkeeping" ? "workload" : "role"}. We’ll build the hiring brief and walk you through recruiting.</p>
        <a class="cta" href="#match">${label}</a>
        <p class="phone-line">Or call <a class="js-phone" href="${c.tel}">${c.phone}</a></p>
      </div>
    </section>`;
  }

  function gate() {
    lockBookkeepingRole();
    const shown = quizDisplayIndex();
    const total = quizTotal();
    const pct = Math.round((shown / total) * 100) + "%";
    let inner = `<div class="bar" aria-hidden="true"><span style="width:${pct}"></span></div>
      <p class="step-n">${shown} of ${total}</p>`;

    if (state.quiz === 1 && state.surface !== "bookkeeping") {
      inner += `<h2>What role are you hiring for?</h2>
        <div class="tiles" role="group" aria-label="Role">
          ${ROLES.map((r) => tile(state.roleChip === r.chip, `data-act="role" data-v="${r.chip}"`, r.chip, r.blurb)).join("")}
        </div>`;
    } else if (state.quiz === 2) {
      const locked = selectedRole();
      inner += `<h2>${state.surface === "bookkeeping" ? "Tell us about the bookkeeping help you need." : "Hours and how many people"}</h2>
        ${locked ? `<p class="locked">Hiring for ${locked.chip}</p>` : ""}
        <p class="kicker" style="margin-top:1.4rem">Full-time or part-time</p>
        <div class="tiles" role="group" aria-label="Schedule">
          ${SCHEDULES.map((s) => tile(state.schedule === s.id, `data-act="sched" data-v="${s.id}"`, s.label, s.blurb)).join("")}
        </div>`;
      if (state.schedule) {
        inner += `<p class="kicker" style="margin-top:2rem">How many people</p>
          <div class="tiles" role="group" aria-label="Headcount">
            ${POSITIONS.map((s) => tile(state.positions === s.id, `data-act="pos" data-v="${s.id}"`, s.label, "")).join("")}
          </div>`;
      }
      if (state.schedule && state.positions) {
        inner += `<p class="kicker" style="margin-top:2rem">Company size (optional)</p>
          <div class="tiles" role="group" aria-label="Company size">
            ${SIZES.map((s) => tile(state.size === s.id, `data-act="size" data-v="${s.id}"`, s.label, "")).join("")}
          </div>
          <label for="tz">Different hours or time zone? (optional)</label>
          <input id="tz" value="${escapeAttr(state.tzNote)}" placeholder="Only if it is not the usual hours for this page" data-act="tz" />
          <button class="submit" type="button" data-act="continue" style="margin-top:1.2rem">Continue</button>`;
      }
      if (state.surface !== "bookkeeping") {
        inner += `<button class="ghost-btn" type="button" data-act="back">Back</button>`;
      }
    } else if (state.quiz === 3) {
      const sel = selectedRole();
      const hint = [sel && sel.chip, state.schedule, state.positions].filter(Boolean).join(" · ");
      inner += `<h2>Where should we send your hiring brief?</h2>
        <p class="hint">${hint}</p>
        <form data-act="submit" novalidate>
          <div class="hid" aria-hidden="true"><label>Website<input name="website" tabindex="-1" autocomplete="off" value=""></label></div>
          <label for="nm">Full name</label>
          <input id="nm" name="name" autocomplete="name" value="${escapeAttr(state.name)}" data-pii="1" />
          ${state.fieldErrors.name ? `<span class="err" role="alert">${state.fieldErrors.name}</span>` : ""}
          <label for="em">Work email</label>
          <input id="em" name="email" type="email" autocomplete="email" value="${escapeAttr(state.email)}" data-pii="1" />
          ${state.fieldErrors.email ? `<span class="err" role="alert">${state.fieldErrors.email}</span>` : ""}
          <label for="ph">Phone</label>
          <input id="ph" name="phone" type="tel" inputmode="tel" autocomplete="tel" placeholder="${state.market === "au" ? "0400 000 000" : "(201) 555-0123"}" value="${escapeAttr(state.phone)}" data-pii="1" />
          ${state.fieldErrors.phone ? `<span class="err" role="alert">${state.fieldErrors.phone}</span>` : ""}
          <label for="ws">Company website (optional)</label>
          <input id="ws" name="company_website" placeholder="https://" autocomplete="url" value="${escapeAttr(state.companyWebsite)}" />
          ${state.error ? `<p class="err" role="alert">${state.error}</p>` : ""}
          <button class="submit" type="submit" ${state.submitting ? "disabled" : ""}>${state.submitting ? "Sending…" : "Get my hiring brief"}</button>
          <p class="hint">We’ll use this to build your hiring brief. We don’t sell your information.</p>
        </form>
        <button class="ghost-btn" type="button" data-act="back">Back</button>`;
    }

    return `<section class="band mist" id="match">
      <div class="wrap">
        <p class="kicker">Hiring brief</p>
        <div class="gate" id="gate">${inner}</div>
      </div>
    </section>`;
  }

  function footer(c) {
    return `<footer class="lp"><div class="wrap">
      <strong>${c.entity}</strong><br />
      ${c.nap}<br />
      Philippines recruitment hub · Serving employers since 2011 ·
      <a href="https://www.virtualcoworker.app/privacy">Privacy</a> ·
      <a href="https://www.virtualcoworker.app/terms">Terms</a><br />
      <a href="${CAREERS}" data-act="careers">${JOB_SEEKER}</a>
    </div></footer>`;
  }

  function escapeAttr(s) {
    return String(s || "").replace(/&/g, "&amp;").replace(/"/g, "&quot;").replace(/</g, "&lt;");
  }

  function switcher() {
    const mkt = document.getElementById("mkt");
    const surf = document.getElementById("surf");
    if (!mkt) return;
    mkt.innerHTML = ["us", "au"].map((m) =>
      `<button type="button" class="${state.market === m ? "on" : ""}" data-m="${m}">${m.toUpperCase()}</button>`
    ).join("");
    surf.innerHTML = ["core", "bookkeeping"].map((s) =>
      `<button type="button" class="${state.surface === s ? "on" : ""}" data-s="${s}">${s === "core" ? "Core /us" : "Bookkeeping"}</button>`
    ).join("");
  }

  function render() {
    const c = mcopy();
    VCContract.captureAttribution(state.market, { category: ctx().category, variant: "" });
    document.getElementById("app").innerHTML =
      nav(c) + hero(c) + statements(c) + trust(c) + featuredQuote() + howSteps(c) +
      socialProof() + askCta() + gate() + moreQuotes() + faq(c) + closer(c) + footer(c);
    switcher();
    logEvents();
    bind();
  }

  function bind() {
    document.querySelectorAll(".js-phone").forEach((a) => {
      a.addEventListener("click", onPhone);
    });
    document.querySelectorAll("[data-m]").forEach((b) => {
      b.addEventListener("click", () => {
        state.market = b.getAttribute("data-m");
        render();
      });
    });
    document.querySelectorAll("[data-s]").forEach((b) => {
      b.addEventListener("click", () => {
        state.surface = b.getAttribute("data-s");
        state.quiz = firstQuizStep();
        state.roleChip = "";
        state.schedule = "";
        state.positions = "";
        state.size = "";
        lockBookkeepingRole();
        render();
      });
    });
    document.querySelectorAll("[data-act]").forEach((el) => {
      const act = el.getAttribute("data-act");
      if (act === "role") {
        el.addEventListener("click", () => {
          state.roleChip = el.getAttribute("data-v");
          markMatchStarted(1, state.roleChip);
          state.quiz = 2;
          render();
          document.getElementById("match").scrollIntoView({ behavior: "smooth", block: "start" });
        });
      }
      if (act === "sched") {
        el.addEventListener("click", () => {
          state.schedule = el.getAttribute("data-v");
          markMatchStarted(2, state.schedule);
          render();
          document.getElementById("match").scrollIntoView({ behavior: "smooth", block: "start" });
        });
      }
      if (act === "pos") {
        el.addEventListener("click", () => {
          state.positions = el.getAttribute("data-v");
          markMatchStarted(2, state.positions);
          render();
        });
      }
      if (act === "size") {
        el.addEventListener("click", () => {
          state.size = el.getAttribute("data-v");
          markMatchStarted(2, "size:" + state.size);
          render();
        });
      }
      if (act === "tz") {
        el.addEventListener("input", () => { state.tzNote = el.value; });
      }
      if (act === "continue") {
        el.addEventListener("click", () => {
          if (!state.schedule || !state.positions) return;
          VCContract.trackEvent("quiz_step_completed", Object.assign({}, ctx(), { step: "2", answer: "complete" }));
          const extra = Object.assign({}, ctx(), {
            result: (selectedRole() && selectedRole().role) || "",
            funnel_step: "contact_step_reached",
          });
          VCContract.trackEvent("quiz_completed", extra);
          VCContract.trackEvent("contact_step_reached", extra);
          VCContract.trackEvent("lead_magnet_completed", Object.assign({}, ctx(), {
            magnet: "guided_match",
            result_role: (selectedRole() && selectedRole().role) || "",
          }));
          state.quiz = 3;
          render();
          document.getElementById("match").scrollIntoView({ behavior: "smooth", block: "start" });
        });
      }
      if (act === "back") {
        el.addEventListener("click", () => {
          state.fieldErrors = {};
          state.error = "";
          if (state.quiz === 3) state.quiz = 2;
          else if (state.quiz === 2 && state.surface !== "bookkeeping") state.quiz = 1;
          render();
        });
      }
      if (act === "careers") el.addEventListener("click", onCareers);
      if (act === "submit") {
        el.addEventListener("submit", onSubmit);
        el.querySelectorAll("[data-pii]").forEach((input) => {
          input.addEventListener("focus", () => {
            VCContract.markFormStarted(ctx());
            if (!state.startedAt) state.startedAt = Date.now();
            logEvents();
          });
        });
        el.querySelector("[name=name]").addEventListener("input", (e) => { state.name = e.target.value; });
        el.querySelector("[name=email]").addEventListener("input", (e) => { state.email = e.target.value; });
        el.querySelector("[name=phone]").addEventListener("input", (e) => {
          state.phone = e.target.value;
          VCContract.markFormStarted(ctx());
          if (!state.startedAt) state.startedAt = Date.now();
        });
        el.querySelector("[name=company_website]").addEventListener("input", (e) => { state.companyWebsite = e.target.value; });
      }
    });
  }

  function onSubmit(e) {
    e.preventDefault();
    const form = e.currentTarget;
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
      document.getElementById("match").scrollIntoView({ behavior: "smooth", block: "start" });
      return;
    }
    state.submitting = true;
    render();
    const role = selectedRole();
    const payload = Object.assign({}, VCContract.readAttribution(state.market, { category: ctx().category }), ctx(), {
      name: name,
      email: email,
      phone: phone,
      company: "",
      role: (role && role.role) || "",
      intent: "employer",
      website: String(fd.get("website") || ""),
      company_website: String(fd.get("company_website") || "").trim(),
      form_started_at: state.startedAt || Date.now(),
      submitted_at: new Date().toISOString(),
      company_size: state.size || "",
      positions_needed: state.positions || "",
      schedule: state.schedule || "",
      hiring_timeline: "",
      message: "Hours requested: " + mcopy().hoursDefault + (state.tzNote ? "\nTime zone notes: " + state.tzNote : ""),
    });
    const res = VCContract.mockLeadApi(payload);
    if (!res.json.ok || !res.json.submission_id) {
      state.submitting = false;
      state.error = res.json.error || "We could not deliver your request just now. Please try again, or call us.";
      render();
      return;
    }
    VCContract.trackValidEmployerSubmit({
      market: state.market,
      submissionId: res.json.submission_id,
      role: payload.role,
      category: payload.category,
      conversionEligible: true,
      companySize: state.size,
      positionsNeeded: state.positions,
      lpSurface: "form",
      ctaMode: "form_primary",
    });
    const q = new URLSearchParams({
      market: state.market,
      sid: res.json.submission_id,
      preview: PREVIEW ? "1" : "",
    });
    if (payload.category) q.set("category", payload.category);
    location.href = "thank-you.html?" + q.toString();
  }

  const boot = new URLSearchParams(location.search);
  if (boot.get("market") === "au") state.market = "au";
  if (boot.get("role") === "bookkeeping" || boot.get("surface") === "bookkeeping") state.surface = "bookkeeping";
  lockBookkeepingRole();
  render();
})();
