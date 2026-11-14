// Tekent de figuren zonder manga-beeld als vaste SVG-bestanden, met de tekenfunctie uit site/strip.js
// (alleen gelezen, niet gewijzigd). Invoer op stdin: [{sleutel, u}]; uitvoer op stdout: {sleutel: svg}.
// Kleding: voor iedereen dezelfde neutrale kleur, zodat geen partijkleur als vlak in beeld komt.
const fs = require("fs"), vm = require("vm"), path = require("path");
const bron = fs.readFileSync(path.join(__dirname, "..", "..", "site", "strip.js"), "utf8");
const ctx = { document: { currentScript: null, querySelectorAll: () => [], getElementById: () => null, documentElement: { dataset: {} } }, window: {}, console };
vm.createContext(ctx);
vm.runInContext(bron + "\n;this.__teken=(u)=>character({u:Object.assign({},u,{manga:undefined}),outfit:'#3d4257',accent:'#9aa0b0'},'neutraal');", ctx);
const invoer = JSON.parse(fs.readFileSync(0, "utf8"));
const uit = {};
for (const x of invoer) {
  uit[x.sleutel] = `<svg xmlns="http://www.w3.org/2000/svg" viewBox="10 10 80 90">${ctx.__teken(x.u)}</svg>`;
}
process.stdout.write(JSON.stringify(uit));
