"""Koppel sprekers aan hun officiële portret bij de Tweede Kamer en maak een overzichtsvel.

Gebruik: python3 scripts/portretten.py
Zoekt in de Persoon-tabel op achternaam en voornaam. Portretten komen in data/portret/
(niet in git) en worden alleen gebruikt om kenmerken voor data/uiterlijk.json te bepalen.
Schrijft data/portret/vel.png en data/portret/koppeling.json.
"""
import io, json, re, sys, unicodedata, urllib.parse
from pathlib import Path
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
from fetch import BASE, get  # noqa: E402

OUT = ROOT / "data" / "portret"


def plat(s):
    return unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode().lower()


def sprekers():
    seen = {}
    for sf in (ROOT / "data" / "strips").glob("*.json"):
        s = json.loads(sf.read_text())
        p = json.loads((ROOT / "data" / "agendapunten" / f"{s['agendapunt']}.json").read_text())
        bek = {b["spreker"]["id"]: b["spreker"] for b in p["beurten"]}
        for i in {x["id"] for x in s["sprekers"]} | {v["spreker_id"] for v in s["strip"] if v["spreker_id"]}:
            seen[i] = bek[i]
    return seen


def zoek(sp):
    deel = sp["verslagnaam"].split()
    achternaam = deel[-1]
    q = urllib.parse.quote(f"Achternaam eq '{achternaam}' and Verwijderd eq false")
    rows = get(f"{BASE}/Persoon?$filter={q}&$select=Id,Roepnaam,Voornamen,Tussenvoegsel,Achternaam,ContentLength")["value"]
    voornaam = plat(sp["naam"].split()[0])
    hits = [r for r in rows if voornaam in plat(f"{r.get('Roepnaam') or ''} {r.get('Voornamen') or ''}")] or rows
    hits = [r for r in hits if r.get("ContentLength")]
    return hits[0] if len(hits) == 1 else None


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    koppeling, tegels = {}, []
    for sid, sp in sorted(sprekers().items(), key=lambda x: x[1]["verslagnaam"]):
        r = zoek(sp)
        if not r:
            print(f"geen eenduidig portret: {sp['naam']}")
            continue
        pad = OUT / f"{r['Id']}.jpg"
        if not pad.exists():
            img = Image.open(io.BytesIO(get(f"{BASE}/Persoon({r['Id']})/resource", as_json=False))).convert("RGB")
            img.thumbnail((400, 400))
            img.save(pad, quality=85)
        koppeling[sid] = {"persoon_id": r["Id"], "naam": sp["naam"], "fractie": sp["fractie"], "functie": sp["functie"]}
        tegels.append((sp["naam"], Image.open(pad)))
    (OUT / "koppeling.json").write_text(json.dumps(koppeling, ensure_ascii=False, indent=1))
    k, w, h = 6, 180, 230
    vel = Image.new("RGB", (k * w, -(-len(tegels) // k) * h), "white")
    d = ImageDraw.Draw(vel)
    for n, (naam, img) in enumerate(tegels):
        t = img.copy(); t.thumbnail((w - 10, h - 30))
        x, y = (n % k) * w, (n // k) * h
        vel.paste(t, (x + (w - t.width) // 2, y + 4))
        d.text((x + 6, y + h - 22), f"{n + 1}. {naam}", fill="black")
    vel.save(OUT / "vel.png")
    print(f"{len(koppeling)} van {len(sprekers())} sprekers gekoppeld")


if __name__ == "__main__":
    main()
