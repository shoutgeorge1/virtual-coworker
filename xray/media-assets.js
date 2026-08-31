(function () {
  var ASSETS = {
    testHero: [
      { folder: "brand", file: "va-us.jpg", label: "A · Female navy", note: "Control · /us · converting path" },
      { folder: "au", file: "va-au.jpg", label: "B · Male portrait", note: "Challenger · live 50/50 on /us" }
    ],
    testMarketing: [
      { folder: "roles", file: "marketing-a.png", label: "Marketing A · orange", note: "Live on /us/digital-marketing + social-media" },
      { folder: "roles", file: "marketing-v2.png", label: "Marketing v2 · prior", note: "Previous digital-marketing default" }
    ],
    orangePeople: [
      { folder: "hopper", file: "hopper-orange-marketing.jpg", label: "Orange marketing · new", note: "Hopper · orange accent · LP candidate" },
      { folder: "hopper", file: "hopper-orange-male.jpg", label: "Orange male · new", note: "Hopper · orange + male · LP candidate" },
      { folder: "roles", file: "marketing-a.png", label: "Marketing A · proven orange", note: "Already live on marketing LPs" }
    ],
    hopperPeople: [
      { folder: "hopper", file: "hopper-people-recruiter-room.jpg", label: "Recruiter in the glass room", note: "Idea · standing · you pick" },
      { folder: "hopper", file: "hopper-people-home-evening.jpg", label: "Home evening desk", note: "Idea · dedicated teammate · US hours" },
      { folder: "hopper", file: "hopper-people-staff-bench.jpg", label: "Staff bench · group of 4", note: "Idea · staffing team" },
      { folder: "hopper", file: "hopper-people-balcony.jpg", label: "Balcony portrait", note: "Idea · remote teammate" },
      { folder: "hopper", file: "hopper-people-whiteboard.jpg", label: "Whiteboard pair", note: "Idea · dedicated team" },
      { folder: "hopper", file: "hopper-people-agency-floor.jpg", label: "Agency floor · coordinator + team", note: "Idea · agency look" },
      { folder: "hopper", file: "hopper-people-hallway.jpg", label: "Walking the floor", note: "Idea · staffing coordinator" },
      { folder: "hopper", file: "hopper-people-shortlist-huddle.jpg", label: "Shortlist huddle · group of 3", note: "Idea · recruitment" },
      { folder: "hopper", file: "hopper-people-content-phone.jpg", label: "Shooting content", note: "Idea · marketing hire" },
      { folder: "hopper", file: "hopper-people-va-pair.jpg", label: "Dedicated pair at desks", note: "Idea · dedicated teammate" },
      { folder: "hopper", file: "hopper-people-offshore-hours.jpg", label: "US hours · evening desk", note: "Idea · offshore hours" },
      { folder: "hopper", file: "hopper-people-au-dedicated.jpg", label: "AU dedicated hire", note: "Idea · AU hire" },
      { folder: "hopper", file: "hopper-people-marketing.jpg", label: "Digital marketing hire", note: "Idea · marketing desk" },
      { folder: "hopper", file: "hopper-people-books.jpg", label: "Bookkeeping hire", note: "Idea · books" }
    ],
    peopleWinners: [
      { folder: "brand", file: "va-us.jpg", label: "VA US portrait", note: "On /us · converting · A/B control" },
      { folder: "au", file: "va-au.jpg", label: "VA AU / male", note: "AU LPs · now US /us challenger" },
      { folder: "roles", file: "marketing-a.png", label: "Marketing A · orange", note: "Live on US marketing LPs" },
      { folder: "brand", file: "hero-us-2026.jpg", label: "US hero 2026", note: "On /us · converting path" },
      { folder: "au", file: "hero-au-2026.jpg", label: "AU hero 2026", note: "On /au hub" },
      { folder: "brand", file: "va-ph.jpg", label: "VA Philippines", note: "Live on the site" },
      { folder: "brand", file: "va-team.webp", label: "VA team", note: "Live on the site" },
      { folder: "brand", file: "ea.jpg", label: "EA", note: "Live on the site" },
      { folder: "brand", file: "support.jpg", label: "Support", note: "Live on the site" }
    ],
    hopper: [
      { folder: "hopper", file: "hopper-businesses-only.png", label: "Businesses only", logo: true, note: "Weak in Ads · try on LP" },
      { folder: "hopper", file: "hopper-you-interview.png", label: "You interview. You pick.", logo: true, note: "Weak in Ads · try on LP" },
      { folder: "hopper", file: "hopper-dedicated-teammate.png", label: "Dedicated teammate", logo: true, note: "Weak in Ads · try on LP" },
      { folder: "hopper", file: "hopper-14-years.png", label: "14 years", logo: true, note: "Weak in Ads · try on LP" }
    ],
    winners: [
      { folder: "brand", file: "badge-google-5star.webp", label: "Google 5-star", logo: true, note: "On converting LPs" },
      { folder: "brand", file: "clutch-us.webp", label: "Clutch US", logo: true, note: "On converting LPs" },
      { folder: "brand", file: "badge-forbes-navy.webp", label: "Forbes navy", logo: true, note: "On converting LPs" },
      { folder: "trust", file: "badge-14-year.webp", label: "14-year badge", logo: true, note: "Ads logo · still live" },
      { folder: "trust", file: "badge-5-star-reviews.webp", label: "5-star reviews", logo: true, note: "Ads logo · still live" },
      { folder: "brand", file: "hero-us-2026.jpg", label: "US hero 2026", cover: true, note: "On /us · converting" },
      { folder: "brand", file: "va-us.jpg", label: "VA US portrait", cover: true, note: "On /us · converting" },
      { folder: "au", file: "badge-clutch-au.webp", label: "Clutch AU", logo: true, note: "AU only" }
    ],
    us: [
      { folder: "brand", file: "hero-us-2026.jpg", label: "US hero 2026", cover: true },
      { folder: "brand", file: "va-us.jpg", label: "VA US portrait", cover: true },
      { folder: "au", file: "va-au.jpg", label: "Male challenger (AU file)", cover: true },
      { folder: "roles", file: "marketing-a.png", label: "Marketing A orange", cover: true },
      { folder: "brand", file: "logo-vc.png", label: "Logo VC", logo: true },
      { folder: "brand", file: "clutch-us.webp", label: "Clutch US 2026", logo: true },
      { folder: "brand", file: "badge-forbes-navy.webp", label: "Forbes navy", logo: true },
      { folder: "brand", file: "badge-google-5star.webp", label: "Google 5-star", logo: true }
    ],
    au: [
      { folder: "au", file: "hero-au-2026.jpg", label: "AU hero 2026", cover: true },
      { folder: "au", file: "va-au.jpg", label: "VA AU portrait", cover: true },
      { folder: "au", file: "logo-au.png", label: "Logo AU", logo: true },
      { folder: "au", file: "badge-clutch-au.webp", label: "Clutch AU badge", logo: true }
    ],
    trustUs: [
      { folder: "brand", file: "badge-forbes-navy.webp", label: "Forbes navy", logo: true },
      { folder: "brand", file: "badge-forbes-white.webp", label: "Forbes white", logo: true },
      { folder: "brand", file: "badge-google-5star.webp", label: "Google 5-star", logo: true },
      { folder: "brand", file: "clutch-us.webp", label: "Clutch US 2026", logo: true },
      { placeholder: true, label: "US client logos pack", note: "need clean US client marks" },
      { placeholder: true, label: "US press / as-seen-in", note: "US media strip if available" },
      { placeholder: true, label: "BBB / Trustpilot US", note: "only if real + approved" }
    ],
    trustAu: [
      { folder: "au", file: "badge-clutch-au.webp", label: "Clutch AU", logo: true },
      { folder: "trust", file: "press-smh.webp", label: "SMH", logo: true },
      { folder: "trust", file: "press-brw.webp", label: "BRW", logo: true },
      { folder: "trust", file: "press-anthill.webp", label: "Anthill", logo: true },
      { folder: "trust", file: "press-startup.webp", label: "Startup", logo: true },
      { folder: "trust", file: "press-startupdaily.webp", label: "Startup Daily", logo: true },
      { folder: "trust", file: "press-startupsmart.webp", label: "Startup Smart", logo: true },
      { folder: "trust", file: "client-buzinga.png", label: "Client · Buzinga", logo: true },
      { folder: "trust", file: "client-credit-card-compare.png", label: "Client · CCC", logo: true },
      { folder: "trust", file: "client-good-co.png", label: "Client · Good Co", logo: true },
      { folder: "trust", file: "client-learning-deli.png", label: "Client · Learning Deli", logo: true },
      { folder: "trust", file: "client-recruitloop.png", label: "Client · RecruitLoop", logo: true },
      { placeholder: true, label: "AU Google reviews badge", note: "market-specific reviews mark" },
      { placeholder: true, label: "AU industry awards", note: "if VC has current ones" }
    ],
    trustShared: [
      { folder: "trust", file: "trust-team-office.png", label: "Team office", cover: true },
      { folder: "trust", file: "trust-consult.png", label: "Consult", cover: true },
      { folder: "trust", file: "trust-company.png", label: "Company", cover: true },
      { folder: "trust", file: "badge-14-year.webp", label: "14-year badge", logo: true },
      { folder: "trust", file: "badge-5-star-reviews.webp", label: "5-star reviews", logo: true },
      { placeholder: true, label: "Fresh office / team stills", note: "newer photography when ready" }
    ],
    roles: [
      { folder: "roles", file: "marketing-a.png", label: "Marketing A · orange · priority" },
      { folder: "roles", file: "admin-a.png", label: "Admin A" },
      { folder: "roles", file: "admin-b.png", label: "Admin B" },
      { folder: "roles", file: "bookkeeper-a.png", label: "Bookkeeper A" },
      { folder: "roles", file: "bookkeeper-b.png", label: "Bookkeeper B" },
      { folder: "roles", file: "bookkeeper-v2.png", label: "Bookkeeper v2" },
      { folder: "roles", file: "accounting-v2.png", label: "Accounting v2" },
      { folder: "roles", file: "customer-service-v2.png", label: "Customer service v2" },
      { folder: "roles", file: "hr-v2.png", label: "HR v2" },
      { folder: "roles", file: "hr-v3.png", label: "HR v3" },
      { folder: "roles", file: "marketing-b.png", label: "Marketing B" },
      { folder: "roles", file: "marketing-v2.png", label: "Marketing v2" },
      { folder: "roles", file: "sales-a.png", label: "Sales A" },
      { folder: "roles", file: "sales-b.png", label: "Sales B" },
      { folder: "roles", file: "sales-v2.png", label: "Sales v2" }
    ],
    brand: [
      { folder: "brand", file: "logo-vc.png", label: "Logo VC", logo: true },
      { folder: "brand", file: "logo-au.png", label: "Logo AU", logo: true },
      { folder: "brand", file: "hero-hub-map-a.jpg", label: "Hub map A", cover: true },
      { folder: "brand", file: "hero-hub-map-b.jpg", label: "Hub map B", cover: true },
      { folder: "brand", file: "hero-hub-map-c.jpg", label: "Hub map C", cover: true },
      { folder: "brand", file: "va-ph.jpg", label: "VA PH", cover: true },
      { folder: "brand", file: "va-face-1.jpg", label: "VA face 1", cover: true },
      { folder: "brand", file: "va-face-2.jpg", label: "VA face 2", cover: true },
      { folder: "brand", file: "va-face-3.jpg", label: "VA face 3", cover: true },
      { folder: "brand", file: "va-team.webp", label: "VA team", cover: true },
      { folder: "brand", file: "talent-arvin.jpg", label: "Talent · Arvin", cover: true },
      { folder: "brand", file: "ea.jpg", label: "EA", cover: true },
      { folder: "brand", file: "support.jpg", label: "Support", cover: true },
      { folder: "brand", file: "how-it-works.webp", label: "How it works" },
      { folder: "brand", file: "industries.webp", label: "Industries" },
      { folder: "brand", file: "marketing.webp", label: "Marketing" }
    ]
  };

  function card(item) {
    if (item.placeholder) {
      return (
        '<div class="media-card placeholder" title="' +
        (item.note || "Placeholder") +
        '">' +
        '<div class="media-thumb landscape ph">Need asset</div>' +
        '<div class="media-meta">' +
        '<p class="name">' +
        (item.label || "Placeholder") +
        "</p>" +
        '<p class="cat">' +
        (item.note || "to collect") +
        "</p>" +
        "</div></div>"
      );
    }
    var folder = item.folder;
    var src = "assets/media/" + folder + "/" + item.file;
    var thumbCls = ["media-thumb"];
    if (item.cover) thumbCls.push("cover", "landscape");
    if (item.logo) thumbCls.push("logo");
    if (!item.cover && !item.logo) thumbCls.push("cover");
    return (
      '<a class="media-card" href="' +
      src +
      '" target="_blank" rel="noopener" title="Open ' +
      item.file +
      '">' +
      '<div class="' +
      thumbCls.join(" ") +
      '"><img src="' +
      src +
      '" alt="' +
      (item.label || item.file) +
      '" loading="lazy" /></div>' +
      '<div class="media-meta">' +
      '<p class="name">' +
      (item.label || item.file) +
      "</p>" +
      '<p class="cat">' +
      (item.note || folder + " · " + item.file) +
      "</p>" +
      "</div></a>"
    );
  }

  function peopleCard(item) {
    var src = "assets/media/" + item.folder + "/" + item.file;
    return (
      '<a class="people-card" href="' +
      src +
      '" target="_blank" rel="noopener">' +
      '<div class="media-thumb cover"><img src="' +
      src +
      '" alt="' +
      (item.label || item.file) +
      '" loading="lazy" /></div>' +
      '<div class="media-meta">' +
      '<span class="tag">' +
      (item.note || "") +
      "</span>" +
      '<p class="name">' +
      (item.label || item.file) +
      "</p>" +
      "</div></a>"
    );
  }

  function fill(id, list) {
    var el = document.getElementById(id);
    if (!el) return;
    el.innerHTML = list.map(card).join("");
  }

  function fillPeople(id, list) {
    var el = document.getElementById(id);
    if (!el) return;
    el.innerHTML = list.map(peopleCard).join("");
  }

  fillPeople("grid-test-hero", ASSETS.testHero);
  fillPeople("grid-test-marketing", ASSETS.testMarketing);
  fillPeople("grid-orange", ASSETS.orangePeople);
  fillPeople("grid-hopper-people", ASSETS.hopperPeople);
  fillPeople("grid-people-winners", ASSETS.peopleWinners);
  fill("grid-hopper", ASSETS.hopper);
  fill("grid-winners", ASSETS.winners);
  fill("grid-us", ASSETS.us);
  fill("grid-au", ASSETS.au);
  fill("grid-trust-us", ASSETS.trustUs);
  fill("grid-trust-au", ASSETS.trustAu);
  fill("grid-trust-shared", ASSETS.trustShared);
  fill("grid-roles", ASSETS.roles);
  fill("grid-brand", ASSETS.brand);
})();
