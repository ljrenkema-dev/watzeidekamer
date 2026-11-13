"""Proef: botsingskaart (lokbeeld voor sociale media) naast de huidige strip.
Leest data/proeftuin/botsing/<id>.json en bouwt tools/proeftuin-botsing/index.html (+ strip.js, style.css, manga)."""
import json, shutil, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
import proeftuin  # noqa: E402

pid = sys.argv[1] if len(sys.argv) > 1 else "be0a626e-43e2-48d7-8d1e-2c60fd372f02-d1"
kaart = json.loads((ROOT / "data" / "proeftuin" / "botsing" / f"{pid}.json").read_text())
strip = json.loads((ROOT / "data" / "strips" / f"{pid}.json").read_text())
huidig = proeftuin.debat_data(pid, strip)
uit = ROOT / "tools" / "proeftuin-botsing"
if uit.exists():
    shutil.rmtree(uit)
uit.mkdir(parents=True)
for f in ("strip.js", "style.css"):
    shutil.copy(ROOT / "site" / f, uit / f)
for sp in huidig["strip"]["sprekers"]:
    m = (sp.get("uiterlijk") or {}).get("manga")
    if m and not (uit / "manga" / m).exists():
        shutil.copytree(ROOT / "site" / "manga" / m, uit / "manga" / m)
sjabloon = (ROOT / "tools" / "botsing-sjabloon.html").read_text()
(uit / "index.html").write_text(sjabloon.replace("__KAART__", json.dumps(kaart, ensure_ascii=False))
                                .replace("__STRIP__", json.dumps(huidig, ensure_ascii=False).replace("</", "<\\/")))
print("klaar:", uit)
