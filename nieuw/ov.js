// Kleine schermafdrukken van de voorpagina en een debatpagina per variant, voor de overzichtspagina.
const { chromium } = require("playwright");
const path = require("path");
(async () => {
  const b = await chromium.launch();
  const p = await (await b.newContext({ viewport: { width: 390, height: 760 }, deviceScaleFactor: 1 })).newPage();
  for (const v of ["a", "b", "c"]) for (const [n, f] of [["home", "index.html"], ["debat", "debat/2026-11-10-vragenuur.html"]]) {
    await p.goto("file://" + path.resolve("uit", v, f));
    await p.evaluate(() => document.fonts.ready);
    await p.screenshot({ path: `overzicht/${v}-${n}.jpg`, type: "jpeg", quality: 72 });
  }
  await b.close();
})();
