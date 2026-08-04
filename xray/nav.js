/* Shared sidebar for the VC paid command center.
   One source of truth so nav can never drift between pages.
   Each page sets <body data-page="index.html" data-foot="..."> */
(function () {
  var ITEMS = [
    { label: "Paid command center" },
    { href: "index.html", text: "Executive Overview" },
    { href: "action.html", text: "Action Plan" },
    { href: "landing-pages.html", text: "Landing Pages" },
    { href: "ads.html", text: "Google Ads" },
    { href: "leadflow.html", text: "Zoho / Lead Flow" },
    { label: "Reference" },
    { href: "findings.html", text: "Findings Archive", quiet: true },
    { href: "future.html", text: "Later ideas", quiet: true },
    { href: "tracking.html", text: "Tracking inventory", quiet: true },
    { href: "evidence.html", text: "Source files", quiet: true }
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
    '<img class="brand-mark" src="assets/logo-vc.png" width="168" height="52" alt="Virtual Coworker" />' +
    '<p class="name">Paid Acquisition</p>' +
    '<p class="sub">Command center</p>' +
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
