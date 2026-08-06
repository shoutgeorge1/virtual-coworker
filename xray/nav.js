/* Stage 1 shell — Checklist is the front door; everything else is Archive. */
(function () {
  var root = document.body.getAttribute("data-root") || "";
  var ITEMS = [
    { href: "launch-control.html", text: "Checklist" },
    { href: "landing-pages.html", text: "LP previews" },
    { href: "ads-package.html", text: "Ads package" },
    { href: "lead-routing.html", text: "Lead Routing" },
    { href: "tracking.html", text: "Tracking" },
    { label: "Archive" },
    { href: "index.html", text: "Pilot Overview", quiet: true },
    { href: "project-status.html", text: "Project Status", quiet: true },
    { href: "us.html", text: "US Campaign", quiet: true },
    { href: "au.html", text: "Australia Campaign", quiet: true },
    { href: "keyword-strategy.html", text: "Keyword Strategy", quiet: true },
    { href: "clean-rebuild.html", text: "Clean Rebuild docs", quiet: true },
    { href: "results.html", text: "Results", quiet: true },
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
    "Stage 1 · US + AU employers<br />Work the Checklist";

  function pageOf(href) {
    var base = (href || "").split("#")[0].split("/").pop();
    return base.replace(/\.html$/, "");
  }

  function resolve(href) {
    if (!root) return href;
    if (href.indexOf("archive/") === 0) return href.replace(/^archive\//, "");
    return root + href;
  }

  function linkHtml(item) {
    var cls = [];
    if (item.quiet) cls.push("nav-quiet");
    var itemPage = pageOf(item.href);
    var curPage = pageOf(current);
    if (itemPage === curPage || item.href === current) cls.push("active");
    /* Treat old checklist aliases as Checklist active state */
    if (
      itemPage === "launch-control" &&
      (curPage === "launch-checklist" || curPage === "checklist" || curPage === "action")
    ) {
      cls.push("active");
    }
    return (
      '<a class="' +
      cls.join(" ") +
      '" href="' +
      resolve(item.href) +
      '">' +
      item.text +
      "</a>"
    );
  }

  var logoSrc = root ? root + "assets/logo-vc.png" : "assets/logo-vc.png";

  var html =
    '<div class="brand">' +
    '<img class="brand-mark" src="' +
    logoSrc +
    '" width="168" height="52" alt="Virtual Coworker" />' +
    '<p class="name">Stage 1 checklist</p>' +
    '<p class="sub">US + AU · employer Search</p>' +
    "</div>" +
    '<nav class="nav" aria-label="Primary">';

  var inArchive = false;
  ITEMS.forEach(function (item) {
    if (item.label) {
      if (inArchive) html += "</div></details>";
      html +=
        '<details class="nav-docs">' +
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
