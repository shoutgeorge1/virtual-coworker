/**
 * Local screenshot helper for CRO V2. Does not touch production deploys.
 */
const { chromium } = require("playwright");
const path = require("path");
const fs = require("fs");

const OUT = path.join(
  __dirname,
  "../../research/screenshots/mobile-cro-v2",
);
const LIVE = "https://www.virtualcoworker.app/us";
const PROP =
  "http://127.0.0.1:8765/mocks/paid-lp-mobile-cro-v2/index.html?preview=1";

async function sequential(page, prefix, n, w, h) {
  await page.setViewportSize({ width: w, height: h });
  await page.waitForTimeout(700);
  for (let i = 0; i < n; i += 1) {
    await page.evaluate((y) => window.scrollTo(0, y), i * h);
    await page.waitForTimeout(220);
    const dest = path.join(OUT, `${prefix}-s${i + 1}.png`);
    await page.screenshot({ path: dest });
    console.log(dest);
  }
}

(async () => {
  fs.mkdirSync(OUT, { recursive: true });
  const browser = await chromium.launch();
  const page = await browser.newPage();

  if (!process.env.AFTER_ONLY) {
    await page.goto(LIVE, { waitUntil: "networkidle", timeout: 45000 });
    await sequential(page, "before-us-390", 6, 390, 844);

    await page.setViewportSize({ width: 1440, height: 900 });
    await page.goto(LIVE, { waitUntil: "networkidle", timeout: 45000 });
    await page.waitForTimeout(500);
    const deskBefore = path.join(OUT, "before-us-desktop-1440.png");
    await page.screenshot({ path: deskBefore });
    console.log(deskBefore);
  }

  await page.goto(PROP, { waitUntil: "networkidle", timeout: 45000 });
  await sequential(page, "after-us-390", 6, 390, 844);
  await sequential(page, "after-us-375", 1, 375, 812);
  await sequential(page, "after-us-430", 1, 430, 932);

  await page.setViewportSize({ width: 1440, height: 900 });
  await page.goto(PROP, { waitUntil: "networkidle", timeout: 45000 });
  await page.waitForTimeout(500);
  const deskAfter = path.join(OUT, "after-us-desktop-1440.png");
  await page.screenshot({ path: deskAfter });
  console.log(deskAfter);

  await page.setViewportSize({ width: 390, height: 844 });
  await page.goto(PROP, { waitUntil: "networkidle" });
  await page.waitForSelector("#match .kicker");
  await page.locator("#match .kicker").scrollIntoViewIfNeeded();
  await page.waitForTimeout(400);
  const match = path.join(OUT, "after-us-390-match.png");
  await page.screenshot({ path: match });
  console.log(match);

  await browser.close();
})().catch((err) => {
  console.error(err);
  process.exit(1);
});
