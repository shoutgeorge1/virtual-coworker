/* Shared sidebar for the VC paid-search pilot command center.
   One source of truth so nav can never drift between pages.
   Each page sets <body data-page="index.html" data-foot="...">
   Archive pages set data-root="../" so links resolve from archive/. */
(function () {
  var root = document.body.getAttribute("data-root") || "";
  var ITEMS = [
    { href: "index.html", text: "Pilot Overview" },
    { href: "launch-checklist", text: "Launch Checklist" },
    { href: "keyword-strategy", text: "Keyword Strategy" },
    { href: "project-status", text: "Project Status" },
    { href: "us.html", text: "US Campaign" },
    { href: "au.html", text: "Australia Campaign" },
    { href: "landing-pages.html", text: "Landing Pages" },
    { href: "tracking.html", text: "Tracking" },
    { href: "lead-routing.html", text: "Lead Routing" },
    { href: "results.html", text: "Results" },
    { href: "later.html", text: "Later Phases" },
    { label: "Archive" },
    { href: "archive/findings.html", text: "Site notes", quiet: true }
  ];

  var host = document.querySelector("[data-nav]");
  if (!host) return;

  var body = document.body;
  var current =
    body.getAttribute("data-page") ||
    (location.pathname.split("/").pop() || "index.html");
  var foot =
    body.getAttribute("data-foot") ||
    "$3,000 Google Search pilot<br />US + Australia employers";

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
    '<p class="name">Search pilot</p>' +
    '<p class="sub">US + AU · $3,000 PoC</p>' +
    "</div>" +
    '<nav class="nav" aria-label="Primary">';

  ITEMS.forEach(function (item) {
    if (item.label) {
      html += '<p class="nav-label">' + item.label + "</p>";
      return;
    }
    html += linkHtml(item);
  });

  html += "</nav>" + '<div class="side-foot">' + foot + "</div>";
  host.innerHTML = html;
})();
