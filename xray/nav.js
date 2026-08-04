/* Shared sidebar for the VC paid command center.
   One source of truth so nav can never drift between pages.
   Each page sets <body data-page="index.html" data-foot="..."> */
(function () {
  var ITEMS = [
    { label: "Paid command center" },
    { href: "index.html", text: "Executive Overview" },
    { href: "roadmap.html", text: "30 / 60 / 90 Days" },
    { href: "landing-pages.html", text: "Landing Pages" },
    { href: "ads.html", text: "Google Ads Workspace" },
    { href: "leadflow.html", text: "Lead Flow &amp; Zoho" },
    { href: "measurement.html", text: "Measurement" },
    { href: "action.html", text: "Decisions &amp; Actions" },
    { href: "scope.html", text: "Scope &amp; Ownership", quiet: true },
    { href: "microsite.html", text: "LP detail", quiet: true },
    { label: "Reference &amp; handoff" },
    { href: "findings.html", text: "Findings Archive" },
    { href: "future.html", text: "Future Expansion" },
    { href: "tracking.html", text: "Tracking inventory", quiet: true },
    { href: "evidence.html", text: "Source files", quiet: true },
    { href: "package.html", text: "Discovery questions", quiet: true },
    { href: "report.html", text: "Long write-up", quiet: true }
  ];

  var host = document.querySelector("[data-nav]");
  if (!host) return;

  var body = document.body;
  var current =
    body.getAttribute("data-page") ||
    (location.pathname.split("/").pop() || "index.html");
  var foot =
    body.getAttribute("data-foot") ||
    "Paid layer · call-ready<br />Virtual Coworker command center";

  var html =
    '<div class="brand">' +
    '<p class="name">Virtual Coworker</p>' +
    '<p class="sub">Paid Acquisition</p>' +
    "</div>" +
    '<nav class="nav" aria-label="Primary">';

  ITEMS.forEach(function (item) {
    if (item.label) {
      html += '<p class="nav-label">' + item.label + "</p>";
      return;
    }
    var cls = [];
    if (item.quiet) cls.push("nav-quiet");
    if (item.href === current) cls.push("active");
    html +=
      '<a class="' + cls.join(" ") + '" href="' + item.href + '">' +
      item.text +
      "</a>";
  });

  html += "</nav>" + '<div class="side-foot">' + foot + "</div>";
  host.innerHTML = html;
})();
