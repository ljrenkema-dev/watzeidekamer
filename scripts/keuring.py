"""Maak de keuringspagina voor de figuren: portret naast figuur, per vijf, met Goed/Niet goed.

Gebruik: python3 scripts/keuring.py UITVOER.html [--alleen naam1,naam2,...] [--vergelijk GIT-REF]
Met --vergelijk staat naast het nieuwe figuur ook het figuur zoals het in GIT-REF was (bijv. HEAD).
Haalt portretten op (Tweede Kamer: Persoon(<id>)/resource; anders 'foto_url' in data/uiterlijk.json)
naar data/portret/ (niet in git) en bouwt één HTML-bestand met de tekencode uit site/strip.js.
Publiceer het bestand als Artifact met capabilities {"db": {}}; oordelen staan in de
collectie "keuring" (doc-id = sleutel uit uiterlijk.json met ':' vervangen door '-').
De portretten staan alleen in die privé-keuringspagina, nooit op de site.
"""
import base64, io, json, subprocess, sys, urllib.request
from pathlib import Path
from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
from fetch import BASE, get, UA  # noqa: E402

KEYS = ("gezicht", "haarkleur", "kapsel", "bril", "baard", "huid", "leeftijd", "spiegel",
        "gezichtsvorm", "wenkbrauw", "oogkleur", "kleding", "onder", "montuur", "oorbel", "pony", "volume")


def foto(key, v):
    pad = ROOT / "data" / "portret" / f"{key.replace(':', '-')}.jpg"
    if not pad.exists():
        pad.parent.mkdir(parents=True, exist_ok=True)
        if v.get("persoon_id"):
            data = get(f"{BASE}/Persoon({v['persoon_id']})/resource", as_json=False)
        elif v.get("foto_url"):
            try:  # Wikimedia vraagt een user-agent met contactgegevens; zonder die kan het 429 geven
                with urllib.request.urlopen(urllib.request.Request(v["foto_url"], headers=UA), timeout=60) as r:
                    data = r.read()
            except Exception as e:
                print(f"  portret niet opgehaald voor {v['naam']}: {e}. Zet het handmatig in {pad}.")
                return ""
        else:
            return ""
        img = Image.open(io.BytesIO(data)).convert("RGB"); img.thumbnail((400, 400)); img.save(pad, quality=85)
    im = Image.open(pad); im.thumbnail((180, 220)); b = io.BytesIO(); im.save(b, "JPEG", quality=72)
    return "data:image/jpeg;base64," + base64.b64encode(b.getvalue()).decode()


def main(uit, alleen=None, vergelijk=None):
    u = json.loads((ROOT / "data" / "uiterlijk.json").read_text())
    oud = json.loads(subprocess.run(["git", "show", f"{vergelijk}:data/uiterlijk.json"], cwd=ROOT, capture_output=True,
                                    text=True, check=True).stdout) if vergelijk else {}
    rows = []
    for key, v in u.items():
        if alleen and v["naam"] not in alleen:
            continue
        rows.append({"id": key.replace(":", "-"), "naam": v["naam"], "fractie": v.get("fractie") or "kabinet",
                     "foto": foto(key, v), "u": {k: v[k] for k in KEYS if k in v}})
        if key in oud and {k: oud[key].get(k) for k in KEYS} != {k: v.get(k) for k in KEYS}:
            rows[-1]["oud"] = {k: oud[key][k] for k in KEYS if k in oud[key]}
    rows.sort(key=lambda r: (r["fractie"] == "kabinet", r["fractie"].lower(), r["naam"].split()[-1].lower()))
    t = (ROOT / "tools" / "keuring-sjabloon.html").read_text()
    t = t.replace("__STRIP__", (ROOT / "site" / "strip.js").read_text())
    t = t.replace("__ROWS__", json.dumps(rows, ensure_ascii=False).replace("</", "<\\/"))
    Path(uit).write_text(t)
    print(f"{len(rows)} figuren in {uit}")


if __name__ == "__main__":
    a = sys.argv[1:]
    alleen = set(a[a.index("--alleen") + 1].split(",")) if "--alleen" in a else None
    vergelijk = a[a.index("--vergelijk") + 1] if "--vergelijk" in a else None
    main(a[0], alleen, vergelijk)
