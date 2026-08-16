/* Stage 1 shell — keep primary short; park unfinished / reference under Archive. */
(function () {
  var root = document.body.getAttribute("data-root") || "";
  /* Stakeholder front: Checklist + Executive. Tools stay primary. Ops reference → Archive. */
  var ITEMS = [
    { href: "launch-control.html", text: "Checklist" },
    { href: "executive.html", text: "Executive" },
    { href: "attribution.html", text: "Funnel & CRM" },
    { href: "landing-pages.html", text: "LP previews" },
    { href: "rsa-review.html", text: "RSA review" },
    { href: "media.html", text: "Media" },
    { label: "Archive" },
    { href: "experiments.html", text: "Experiments (parked)", quiet: true },
    { href: "recovery-audit.html", text: "Recovery audit", quiet: true },
    { href: "growth-os.html", text: "Growth OS", quiet: true },
    { href: "conversion-path.html", text: "Conversion path", quiet: true },
    { href: "tracking.html", text: "Tracking", quiet: true },
    { href: "keyword-strategy.html", text: "Keyword Strategy", quiet: true },
    { href: "daily-watch.html", text: "Daily watch", quiet: true },
    { href: "lead-routing.html", text: "Lead Routing", quiet: true },
    { href: "ads-package.html", text: "Ads package", quiet: true },
    { href: "project-status.html", text: "Project Status", quiet: true },
    { href: "us.html", text: "US Campaign", quiet: true },
    { href: "au.html", text: "Australia Campaign", quiet: true },
    { href: "au-rsa-review.html", text: "AU RSA review", quiet: true },
    { href: "us-brand-ag-review.html", text: "US Brand AG", quiet: true },
    { href: "au-brand-ag-review.html", text: "AU Brand AG", quiet: true },
    { href: "assets-audit.html", text: "Assets audit", quiet: true },
    { href: "clean-rebuild.html", text: "Clean Rebuild docs", quiet: true },
    { href: "results.html", text: "Results (wireframe)", quiet: true },
    { href: "later.html", text: "Later Phases", quiet: true },
    { href: "archive/findings.html", text: "Archive notes", quiet: true }
  ];

  var host = document.querySelector("[data-nav]");
  if (!host) return;

  var body = document.body;
  var current =
    body.getAttribute("data-page") ||
    (location.pathname.split("/").pop() || "launch-control.html");
  var foot =
    body.getAttribute("data-foot") ||
    "US + AU Search live<br />Checklist first";

  function pageOf(href) {
    var base = (href || "").split("#")[0].split("/").pop();
    return base.replace(/\.html$/, "");
  }

  function resolve(href) {
    if (!root) return href;
    if (href.indexOf("archive/") === 0) return href.replace(/^archive\//, "");
    return root + href;
  }

  function isActive(item) {
    var itemPage = pageOf(item.href);
    var curPage = pageOf(current);
    if (itemPage === curPage || item.href === current) return true;
    /* Treat old checklist aliases as Checklist active state */
    if (
      itemPage === "launch-control" &&
      (curPage === "launch-checklist" || curPage === "checklist" || curPage === "action")
    ) {
      return true;
    }
    return false;
  }

  function linkHtml(item) {
    var cls = [];
    var active = isActive(item);
    if (item.quiet) cls.push("nav-quiet");
    if (active) cls.push("active");
    return (
      '<a class="' +
      cls.join(" ") +
      '" href="' +
      resolve(item.href) +
      '"' +
      (active ? ' aria-current="page"' : "") +
      ">" +
      item.text +
      "</a>"
    );
  }

  var logoSrc = root ? root + "assets/logo-vc.png" : "assets/logo-vc.png";
  var onQuietPage = ITEMS.some(function (item) {
    return item.quiet && isActive(item);
  });

  var html =
    '<div class="brand">' +
    '<img class="brand-mark" src="' +
    logoSrc +
    '" width="168" height="52" alt="Virtual Coworker" />' +
    '<p class="name">Stage 1 command center</p>' +
    '<p class="sub">US + AU Search live</p>' +
    "</div>" +
    '<nav class="nav" aria-label="Primary">';

  var inArchive = false;
  ITEMS.forEach(function (item) {
    if (item.label) {
      if (inArchive) html += "</div></details>";
      html +=
        '<details class="nav-docs"' +
        (onQuietPage ? " open" : "") +
        ">" +
        "<summary>" +
        item.label +
        "</summary>" +
        '<div class="nav-docs-body">' +
        '<p class="nav-label">' +
        item.label +
        "</p>";
      inArchive = true;
      return;
    }
    html += linkHtml(item);
  });
  if (inArchive) html += "</div></details>";

  html += "</nav>" + '<div class="side-foot">' + foot + "</div>";
  host.innerHTML = html;
})();
