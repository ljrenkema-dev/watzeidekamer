"""Figuren voor de site: de goedgekeurde manga-beelden (site/manga/<sleutel>/neutraal.webp) worden gekopieerd;
wie geen manga-beeld heeft, krijgt het getekende figuur uit site/strip.js als vast SVG-bestand (kern/teken.js);
wie geen goedgekeurd figuur heeft, krijgt een neutraal figuur. Geen portretfoto's."""
import json, shutil, subprocess
from pathlib import Path
from functools import lru_cache
from . import model as M

NEUTRAAL = ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="10 10 80 90">'
            '<rect x="10" y="10" width="80" height="90" fill="#e4e2ec"/>'
            '<path d="M24 100 Q26 80 50 78 Q74 80 76 100 Z" fill="#a9a6bd"/>'
            '<circle cx="50" cy="52" r="17" fill="#a9a6bd"/></svg>')

KAMER_BRON = "officieel portret Tweede Kamer"


def alle_sprekers():
    uit = {}
    for d in M.debatten():
        for x in d.delen:
            for b in x.beurten:
                uit[b["spreker"]["id"]] = b["spreker"]
    return uit


@lru_cache(None)
def getekend():
    """{sleutel: svg} voor goedgekeurde figuren zonder manga-beeld."""
    nodig = []
    for sid in alle_sprekers():
        k = M.figuur_sleutel(sid)
        if k and not M.manga_map(k):
            nodig.append({"sleutel": k, "u": M.uiterlijk(k)})
    if not nodig:
        return {}
    r = subprocess.run(["node", str(Path(__file__).with_name("teken.js"))], input=json.dumps(nodig),
                       capture_output=True, text=True, check=True)
    return json.loads(r.stdout)


def schrijf(uit_dir):
    """Zet alle figuren in <uit_dir>/fig/. Geeft het aantal bestanden."""
    fig = Path(uit_dir) / "fig"
    fig.mkdir(parents=True, exist_ok=True)
    (fig / "neutraal.svg").write_text(NEUTRAAL)
    n = 1
    svg = getekend()
    for sid in alle_sprekers():
        k = M.figuur_sleutel(sid)
        if not k:
            continue
        m = M.manga_map(k)
        if m:
            shutil.copyfile(M.ROOT / "site" / "manga" / m / "neutraal.webp", fig / f"{m}.webp")
        else:
            (fig / f"{k.replace(':', '-')}.svg").write_text(svg[k])
        n += 1
    return n


def statistiek():
    """Hoeveel figuren naar een Kamerportret getekend zijn en hoeveel niet (voor de tekst over de figuren)."""
    kamer, anders, geen = 0, 0, 0
    for sid in alle_sprekers():
        k = M.figuur_sleutel(sid)
        if not k:
            geen += 1
        elif (M.uiterlijk(k) or {}).get("bron") == KAMER_BRON:
            kamer += 1
        else:
            anders += 1
    return {"kamerportret": kamer, "ander_portret": anders, "geen_figuur": geen}


def als_beeld(rel, maat):
    """Het figuur als PIL-beeld (RGBA, vierkant maat×maat, bovenkant van het figuur), voor deelbeelden."""
    from PIL import Image
    import io
    rel = str(rel)
    if rel.endswith(".webp"):
        im = Image.open(M.ROOT / "site" / "manga" / Path(rel).stem / "neutraal.webp").convert("RGBA")
    else:
        naam = Path(rel).stem
        data = NEUTRAAL if naam == "neutraal" else next(v for k, v in getekend().items() if k.replace(":", "-") == naam)
        r = subprocess.run(["convert", "-background", "none", "-density", "300", "svg:-", "png:-"],
                           input=data.encode(), capture_output=True, check=True)
        im = Image.open(io.BytesIO(r.stdout)).convert("RGBA")
    w, h = im.size
    s = min(w, h)
    im = im.crop(((w - s) // 2, 0, (w - s) // 2 + s, s))
    return im.resize((maat, maat), Image.LANCZOS)
