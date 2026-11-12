"""Zet goedgekeurde manga-beelden verkleind in site/manga/<sleutel>/<emotie>.jpg, zodat build.py ze meeneemt.
Alleen voor wie in data/manga/beschrijvingen.json 'manga_goedgekeurd' heeft (keuring door de eigenaar).
Gebruik: python3 scripts/manga_site.py   (vereist Pillow)."""
import json, shutil
from pathlib import Path
from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
BRON = ROOT / "data" / "manga" / "manga"
UIT = ROOT / "site" / "manga"
BREED, HOOG = 360, 480


def main():
    beschr = json.loads((ROOT / "data" / "manga" / "beschrijvingen.json").read_text())
    if UIT.exists():
        shutil.rmtree(UIT)
    for sleutel, b in beschr.items():
        ok = (b.get("manga_goedgekeurd") or {}).get("beelden", [])
        map_ = BRON / sleutel.replace(":", "-")
        n = 0
        for emo in ok:
            src = next(iter(sorted(map_.glob(f"{emo}.*[gp]"))), None)
            if not src:
                continue
            doel = UIT / sleutel.replace(":", "-") / f"{emo}.jpg"
            doel.parent.mkdir(parents=True, exist_ok=True)
            im = Image.open(src).convert("RGB")
            im = im.resize((BREED, HOOG)) if abs(im.width / im.height - 0.75) < 0.02 else im.crop(
                (0, 0, im.width, int(im.width / 0.75))).resize((BREED, HOOG))
            im.save(doel, "JPEG", quality=82, optimize=True)
            n += 1
        if n:
            print(f"{b.get('naam', sleutel)}: {n} beelden")


if __name__ == "__main__":
    main()
