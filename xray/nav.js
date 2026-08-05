/* Shared sidebar — Stage 1 launch control first; technical docs secondary. */
(function () {
  var root = document.body.getAttribute("data-root") || "";
  var ITEMS = [
    { href: "launch-control.html", text: "Launch Control" },
    { href: "index.html", text: "Pilot Overview" },
    { label: "Technical documentation" },
    { href: "clean-rebuild.html", text: "Clean Rebuild", quiet: true },
    { href: "launch-checklist", text: "Launch Checklist", quiet: true },
    { href: "keyword-strategy", text: "Keyword Strategy", quiet: true },
    { href: "project-status", text: "Project Status", quiet: true },
    { href: "us.html", text: "US Campaign", quiet: true },
    { href: "au.html", text: "Australia Campaign", quiet: true },
    { href: "landing-pages.html", text: "Landing Pages", quiet: true },
    { href: "tracking.html", text: "Tracking", quiet: true },
    { href: "lead-routing.html", text: "Lead Routing", quiet: true },
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
    "Stage 1 · US + AU employers<br />Paused until checklist green";

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
    '<p class="name">Stage 1 launch</p>' +
    '<p class="sub">US + AU · employer Search</p>' +
    "</div>" +
    '<nav class="nav" aria-label="Primary">';

  var inDocs = false;
  var docsOpen =
    typeof window.matchMedia === "function" &&
    window.matchMedia("(min-width: 821px)").matches;
  ITEMS.forEach(function (item) {
    if (item.label) {
      if (inDocs) html += "</div></details>";
      html +=
        '<details class="nav-docs"' +
        (docsOpen ? " open" : "") +
        ">" +
        "<summary>" +
        item.label +
        "</summary>" +
        '<div class="nav-docs-body">' +
        '<p class="nav-label">' +
        item.label +
        "</p>";
      inDocs = true;
      return;
    }
    html += linkHtml(item);
  });
  if (inDocs) html += "</div></details>";

  html += "</nav>" + '<div class="side-foot">' + foot + "</div>";
  host.innerHTML = html;
})();
