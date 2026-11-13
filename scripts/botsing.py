"""Proef: botsingskaart (lokbeeld voor sociale media) naast de huidige strip.
Leest data/proeftuin/botsing/<id>.json en bouwt tools/proeftuin-botsing/index.html (+ strip.js, style.css, manga)."""
import json, shutil, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
import proeftuin  # noqa: E402

ids = sys.argv[1:] or ["dd194a7c-3fbf-4bc5-b275-5f733e839dd6", "be0a626e-43e2-48d7-8d1e-2c60fd372f02-d1"]
uit = ROOT / "tools" / "proeftuin-botsing"
if uit.exists():
    shutil.rmtree(uit)
uit.mkdir(parents=True)
for f in ("strip.js", "style.css"):
    shutil.copy(ROOT / "site" / f, uit / f)
alles = []
for pid in ids:
    kaart = json.loads((ROOT / "data" / "proeftuin" / "botsing" / f"{pid}.json").read_text())
    huidig = proeftuin.debat_data(pid, json.loads((ROOT / "data" / "strips" / f"{pid}.json").read_text()))
    for sp in huidig["strip"]["sprekers"]:
        m = (sp.get("uiterlijk") or {}).get("manga")
        if m and not (uit / "manga" / m).exists():
            shutil.copytree(ROOT / "site" / "manga" / m, uit / "manga" / m)
    alles.append({"kaart": kaart, "strip": huidig})
sjabloon = (ROOT / "tools" / "botsing-sjabloon.html").read_text()
(uit / "index.html").write_text(sjabloon.replace("__DATA__", json.dumps(alles, ensure_ascii=False).replace("</", "<\\/")))
print("klaar:", uit, len(alles), "debatten")
