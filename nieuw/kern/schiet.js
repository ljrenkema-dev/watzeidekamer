// Maakt schermafdrukken van lokale HTML-bestanden. Invoer op stdin: [{html, png, w, h}].
// Gebruikt voor de deelbeelden (Open Graph) per debat: het script tekent ze zelf uit tekst en bestaande figuren.
const { chromium } = require("playwright");
const fs = require("fs");
(async () => {
  const taken = JSON.parse(fs.readFileSync(0, "utf8"));
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 1200, height: 630 }, deviceScaleFactor: 1 });
  for (const t of taken) {
    await page.setViewportSize({ width: t.w || 1200, height: t.h || 630 });
    await page.goto("file://" + t.html);
    await page.evaluate(() => document.fonts.ready);
    await page.screenshot({ path: t.png, type: t.png.endsWith(".jpg") ? "jpeg" : "png", quality: t.png.endsWith(".jpg") ? 86 : undefined });
  }
  await browser.close();
})().catch(e => { console.error(e); process.exit(1); });
