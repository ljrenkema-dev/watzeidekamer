"""Proef: botsingskaart (lokbeeld voor sociale media) naast de huidige strip.
Leest data/proeftuin/botsing/<id>.json en bouwt tools/proeftuin-botsing/index.html (+ strip.js, style.css, manga)."""
import json, shutil, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
import proeftuin  # noqa: E402

ids = sys.argv[1:] or [i for i in proeftuin.TEST if (ROOT / "data" / "proeftuin" / "botsing" / f"{i}.json").exists()]
uit = ROOT / "tools" / "proeftuin-botsing"
if uit.exists():
    shutil.rmtree(uit)
uit.mkdir(parents=True)
for f in ("strip.js", "style.css"):
    shutil.copy(ROOT / "site" / f, uit / f)
alles = []
for pid in ids:
    kaart = json.loads((ROOT / "data" / "proeftuin" / "botsing" / f"{pid}.json").read_text())
    # figuur per geciteerde spreker (zelfde kenmerken en manga-beeld als in de strip)
    import build
    uiterlijk = json.loads((ROOT / "data" / "uiterlijk.json").read_text())
    koppeling = json.loads((ROOT / "data" / "sprekers.json").read_text())
    punt = json.loads((ROOT / "data" / "agendapunten" / f"{pid}.json").read_text())
    for v in kaart["versies"].values():
        for c in v["citaten"]:
            sp = punt["beurten"][c["beurt"]]["spreker"]
            sl = koppeling.get(sp["id"])
            u = uiterlijk.get(sl or "")
            k = {x: u[x] for x in build.KENMERKEN if x in u} if u else None
            if k and build.manga(sl):
                k["manga"] = build.manga(sl)
                m = build.manga(sl)
                if not (uit / "manga" / m).exists():
                    shutil.copytree(ROOT / "site" / "manga" / m, uit / "manga" / m)
            c["figuur"] = {"id": sp["id"], "fractie": sp.get("fractie") or "", "u": k}
    huidig = proeftuin.debat_data(pid, json.loads((ROOT / "data" / "strips" / f"{pid}.json").read_text()))
    for sp in huidig["strip"]["sprekers"]:
        m = (sp.get("uiterlijk") or {}).get("manga")
        if m and not (uit / "manga" / m).exists():
            shutil.copytree(ROOT / "site" / "manga" / m, uit / "manga" / m)
    alles.append({"kaart": kaart, "strip": huidig})
sjabloon = (ROOT / "tools" / "botsing-sjabloon.html").read_text()
(uit / "index.html").write_text(sjabloon.replace("__DATA__", json.dumps(alles, ensure_ascii=False).replace("</", "<\\/")))
print("klaar:", uit, len(alles), "debatten")
