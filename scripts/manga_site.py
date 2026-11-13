"""Zet goedgekeurde manga-beelden verkleind in site/manga/<sleutel>/, zodat build.py ze meeneemt.
De site gebruikt het neutrale beeld (uitdrukking blijft neutraal; de emotie zit in de achtergrond van het vak)
en, waar goedgekeurd, de houding bij een interruptie. Alleen beelden die de eigenaar keurde
(data/manga/beschrijvingen.json: 'neutraal_goedgekeurd', of 'interruptie' in 'manga_goedgekeurd').
Gebruik: python3 scripts/manga_site.py   (vereist Pillow)."""
import json, shutil
from pathlib import Path
from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
BRON = ROOT / "data" / "manga" / "manga"
UIT = ROOT / "site" / "manga"
BREED, HOOG = 360, 480


def zet(src, doel):
    doel.parent.mkdir(parents=True, exist_ok=True)
    im = Image.open(src).convert("RGB")
    if abs(im.width / im.height - 0.75) >= 0.02:
        im = im.crop((0, 0, im.width, int(im.width / 0.75)))
    im.resize((BREED, HOOG)).save(doel, "JPEG", quality=82, optimize=True)


def main():
    beschr = json.loads((ROOT / "data" / "manga" / "beschrijvingen.json").read_text())
    if UIT.exists():
        shutil.rmtree(UIT)
    n = 0
    for sleutel, b in beschr.items():
        map_ = BRON / sleutel.replace(":", "-")
        doel = UIT / sleutel.replace(":", "-")
        if not b.get("neutraal_goedgekeurd") or not (map_ / "neutraal.jpg").exists():
            continue
        zet(map_ / "neutraal.jpg", doel / "neutraal.jpg")
        if "interruptie" in (b.get("manga_goedgekeurd") or {}).get("beelden", []) and (map_ / "interruptie.jpg").exists():
            zet(map_ / "interruptie.jpg", doel / "interruptie.jpg")
        n += 1
    print(f"{n} politici met een manga-figuur op de site")


if __name__ == "__main__":
    main()
