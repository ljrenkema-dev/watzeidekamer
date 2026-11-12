"""Zet de verslag-XML om naar agendapunten met spreekbeurten.

Gebruik: python3 scripts/parse.py
Leest data/raw/*.xml en data/vergaderingen.json, schrijft data/agendapunten/<id>.json.
Een agendapunt = een <activiteit> in het verslag. Elke spreekbeurt bewaart de spreker
precies zoals de Kamer hem vastlegt (id, naam, fractie, functie).
"""
import json, re
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RAW, OUT = ROOT / "data" / "raw", ROOT / "data" / "agendapunten"
NS = "{http://www.tweedekamer.nl/ggm/vergaderverslag/v1.0}"
OVERSLAAN = {"Opening", "Mededelingen", "Sluiting", "Regeling van werkzaamheden"}


def t(el, name):
    c = el.find(NS + name)
    return (c.text or "").strip() if c is not None and c.text else ""


def tekst(el):
    """Alle alinea's uit het directe <tekst>-kind, zonder het label 'De heer X (VVD):'."""
    tk = el.find(NS + "tekst")
    if tk is None:
        return ""
    alineas = []
    for al in tk.iter(NS + "alinea"):
        items = ["".join(it.itertext()).strip() for it in al.iter(NS + "alineaitem")]
        items = [i for i in items if i]
        if items and not alineas and len(items[0]) < 90 and items[0].endswith(":"):
            items = items[1:]  # sprekerslabel
        if items:
            alineas.append(" ".join(items))
    return "\n".join(re.sub(r"\s+", " ", a) for a in alineas)


def spreker(el):
    s = el.find(NS + "spreker")
    if s is None:
        return None
    voornaam, verslagnaam = t(s, "voornaam"), t(s, "verslagnaam")
    return {
        "id": s.get("objectid"), "soort": s.get("soort"),
        "naam": verslagnaam if voornaam and voornaam in verslagnaam else f"{voornaam} {verslagnaam}".strip(), "verslagnaam": verslagnaam,
        "fractie": t(s, "fractie"), "functie": t(s, "functie"),
    }


def beurten(act):
    for el in act.iter():
        tag = el.tag.replace(NS, "")
        if tag not in ("woordvoerder", "interrumpant"):
            continue
        sp, txt = spreker(el), tekst(el)
        if not sp or not txt:
            continue
        yield {
            "rol": tag, "voorzitter": t(el, "isvoorzitter") == "true",
            "begin": t(el, "markeertijdbegin"), "spreker": sp, "tekst": txt,
        }


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    index = json.loads((ROOT / "data" / "vergaderingen.json").read_text())
    n = 0
    for verg_id, meta in index.items():
        root = ET.parse(RAW / f"{verg_id}.xml").getroot()
        for act in root.iter(NS + "activiteit"):
            titel = t(act, "titel")
            if titel in OVERSLAAN:
                continue
            bs = list(beurten(act))
            if not any(not b["voorzitter"] for b in bs):
                continue
            punt = {
                "id": act.get("objectid"), "titel": titel, "onderwerp": t(act, "onderwerp"),
                "soort_activiteit": act.get("soort"), "begin": t(act, "aanvangstijd"),
                "eind": t(act, "eindtijd"), "vergadering": {"id": verg_id, **meta},
                "woorden": sum(len(b["tekst"].split()) for b in bs), "beurten": bs,
            }
            (OUT / f"{punt['id']}.json").write_text(json.dumps(punt, ensure_ascii=False, indent=1))
            n += 1
    print(f"{n} agendapunten geschreven")


if __name__ == "__main__":
    main()
