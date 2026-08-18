/**
 * Local screenshot gallery for /preview/trust-first.
 * Preview only. Does not hit production.
 */
import { mkdirSync } from "node:fs";
import { join } from "node:path";
import { spawnSync } from "node:child_process";

const chrome =
  process.env.CHROME_PATH ||
  "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome";
const base = process.env.PREVIEW_BASE || "http://127.0.0.1:4321";
const outDir = join(
  process.cwd(),
  "public/preview/trust-first/screenshots",
);
mkdirSync(outDir, { recursive: true });

const slugs = [
  "us",
  "philippines-virtual-assistants",
  "virtual-assistant-agency",
  "staffing",
  "real-estate",
  "bookkeeping",
  "customer-service",
  "sales",
  "administrative-support",
  "digital-marketing",
];

const shots = [
  { name: "index-desktop", url: `${base}/preview/trust-first`, size: "1440,900" },
  { name: "index-mobile", url: `${base}/preview/trust-first`, size: "390,844" },
];
for (const slug of slugs) {
  shots.push({
    name: `${slug}-desktop`,
    url: `${base}/preview/trust-first/${slug}`,
    size: "1440,900",
  });
  shots.push({
    name: `${slug}-mobile`,
    url: `${base}/preview/trust-first/${slug}`,
    size: "390,844",
  });
  shots.push({
    name: `${slug}-proof-desktop`,
    url: `${base}/preview/trust-first/${slug}?v=proof`,
    size: "1440,900",
  });
}

for (const shot of shots) {
  const dest = join(outDir, `${shot.name}.png`);
  const result = spawnSync(
    chrome,
    [
      "--headless=new",
      "--hide-scrollbars",
      "--disable-gpu",
      `--window-size=${shot.size}`,
      `--screenshot=${dest}`,
      "--virtual-time-budget=4000",
      shot.url,
    ],
    { encoding: "utf8" },
  );
  if (result.status !== 0) {
    console.error(shot.name, result.stderr || result.stdout);
    process.exit(result.status || 1);
  }
  console.log("wrote", dest);
}
