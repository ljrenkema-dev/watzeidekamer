// Schermafdrukken van een gebouwde variant, op 1280 en 390 breed, in licht en donker.
// Gebruik: node kijk.js <map met site> <uitmap> pagina1.html[#anker] pagina2.html ...  (KIJK_VOL=1 voor hele pagina)
const { chromium } = require("playwright");
const path = require("path");
(async () => {
  const [site, uit, ...paginas] = process.argv.slice(2);
  const browser = await chromium.launch();
  const fouten = [];
  for (const [w, h] of [[1280, 900], [390, 844]]) {
    for (const thema of ["light", "dark"]) {
      const ctx = await browser.newContext({ viewport: { width: w, height: h }, colorScheme: thema, deviceScaleFactor: 1 });
      const page = await ctx.newPage();
      page.on("pageerror", e => fouten.push(String(e)));
      for (const p of paginas) {
        const url = "file://" + path.resolve(site, p);
        await page.goto(url);
        await page.evaluate(() => document.fonts.ready);
        const breed = await page.evaluate(() => document.documentElement.scrollWidth);
        if (breed > w + 1) fouten.push(`${p} @${w}: horizontaal scrollen (${breed}px)`);
        const naam = p.replace(/[\/#.]/g, "_") + `_${w}_${thema}.png`;
        await page.screenshot({ path: path.join(uit, naam), fullPage: !!process.env.KIJK_VOL });
      }
      await ctx.close();
    }
  }
  await browser.close();
  console.log(fouten.length ? fouten.join("\n") : "geen fouten");
})();
