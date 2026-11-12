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
    """Spreekbeurten in documentvolgorde. 'deel' = volgnummer van het bovenste <activiteitdeel>
    (één spreker met de interrupties op zijn tekst); beurten daarbuiten krijgen het vorige deel."""
    deel_van, deel = {}, -1
    for n, d in enumerate(x for x in act.iter(NS + "activiteitdeel")
                          if not any(x in list(y.iter()) for y in act.iter(NS + "activiteitdeel") if y is not x)):
        for el in d.iter():
            deel_van[el] = n
    for el in act.iter():
        deel = deel_van.get(el, deel)
        tag = el.tag.replace(NS, "")
        if tag not in ("woordvoerder", "interrumpant"):
            continue
        sp, txt = spreker(el), tekst(el)
        if not sp or not txt:
            continue
        yield {
            "rol": tag, "voorzitter": t(el, "isvoorzitter") == "true",
            "begin": t(el, "markeertijdbegin"), "spreker": sp, "tekst": txt, "deel": max(deel, 0),
        }


SPLITS_VANAF = 16000   # woorden; daarboven wordt een agendapunt in delen geknipt
DOEL_PER_DEEL = 12000  # streefmaximum per deel


def fase(beurten_van_deel):
    """'kamer' of 'kabinet': wie houdt de spreekbeurt (de woordvoerder, niet de interrumpanten)."""
    hoofd = next((b for b in beurten_van_deel if b["rol"] == "woordvoerder" and not b["voorzitter"]), None)
    if not hoofd:
        return None
    return "kabinet" if hoofd["spreker"]["soort"] in ("Minister", "Staatssecretaris", "Minister-president") or not hoofd["spreker"]["fractie"] else "kamer"


def knip(punt):
    """Knip een lang agendapunt in delen langs spreekbeurten, zonder fases (inbreng Kamer,
    antwoord kabinet, tweede termijn) te mengen. Geeft een lijst agendapunten terug."""
    bs = punt["beurten"]
    if punt["woorden"] <= SPLITS_VANAF:
        return [punt]
    groepen = {}
    for b in bs:
        groepen.setdefault(b["deel"], []).append(b)
    # een te lange spreekbeurt knippen waar de voorzitter het woord teruggeeft aan de spreker
    # (dan is een interruptiedebatje net afgelopen), zodat geen interruptie van zijn antwoord loskomt
    def aantal(xs):
        return sum(len(b["tekst"].split()) for b in xs)
    def splits(groep):
        if aantal(groep) <= DOEL_PER_DEEL * 1.15:
            return [groep]
        hoofd = next((b["spreker"]["id"] for b in groep if b["rol"] == "woordvoerder" and not b["voorzitter"]), None)
        n = -(-aantal(groep) // DOEL_PER_DEEL); doel = aantal(groep) / n
        uit, cur = [], []
        for i, b in enumerate(groep):
            grens = (i > 0 and groep[i - 1]["voorzitter"] and b["rol"] == "woordvoerder"
                     and not b["voorzitter"] and b["spreker"]["id"] == hoofd)
            if grens and cur and aantal(cur) >= doel * 0.85:
                uit.append(cur); cur = []
            cur.append(b)
        if cur:
            uit.append(cur)
        return uit
    reeks = [g for _, groep in sorted(groepen.items()) for g in splits(groep)]
    # fases: opeenvolgende spreekbeurten van dezelfde kant; voorzitter-deeltjes horen bij de vorige
    fases, huidige = [], None
    for groep in reeks:
        f = fase(groep) or (huidige or "kamer")
        if f != huidige:
            fases.append({"kant": f, "groepen": []})
            huidige = f
        fases[-1]["groepen"].append(groep)
    namen = {"kamer": ["Inbreng van de Kamer", "Tweede termijn van de Kamer", "Derde termijn van de Kamer"],
             "kabinet": ["Antwoord van het kabinet", "Antwoord in tweede termijn", "Antwoord in derde termijn"]}
    teller, stukken = {"kamer": 0, "kabinet": 0}, []
    for f in fases:
        naam = namen[f["kant"]][min(teller[f["kant"]], 2)]
        teller[f["kant"]] += 1
        woorden = sum(len(b["tekst"].split()) for g in f["groepen"] for b in g)
        n = max(1, -(-woorden // DOEL_PER_DEEL))
        doel, cur, cur_w = woorden / n, [], 0
        for g in f["groepen"]:
            w = sum(len(b["tekst"].split()) for b in g)
            if cur and cur_w + w > doel * 1.15 and len(stukken) < 50:
                stukken.append((naam, cur)); cur, cur_w = [], 0
            cur.append(g); cur_w += w
        if cur:
            stukken.append((naam, cur))
    # te kleine stukken (< 2500 woorden, of zonder andere hoofdspreker dan de voorzitter)
    # samenvoegen met het vorige stuk, of met het volgende als het het eerste is
    def klein(gr):
        bs_ = [b for g in gr for b in g]
        return aantal(bs_) < 2500 or not any(b["rol"] == "woordvoerder" and not b["voorzitter"] for b in bs_)
    samen = []
    for naam, gr in stukken:
        def label(a, b):
            return a if a == b or b in a.split(" en ") else f"{a} en {b[0].lower()}{b[1:]}"
        if samen and klein(gr):
            samen[-1] = (label(samen[-1][0], naam), samen[-1][1] + gr)
        elif samen and klein(samen[-1][1]):
            samen[-1] = (label(samen[-1][0], naam), samen[-1][1] + gr)
        else:
            samen.append((naam, list(gr)))
    delen = []
    for i, (naam, gr) in enumerate(samen, 1):
        dbs = [b for g in gr for b in g]
        sprekers = []
        for b in dbs:
            if b["rol"] == "woordvoerder" and not b["voorzitter"] and b["spreker"]["verslagnaam"] not in sprekers:
                sprekers.append(b["spreker"]["verslagnaam"])
        wie = ", ".join(sprekers[:4]) + (f" en {len(sprekers) - 4} anderen" if len(sprekers) > 4 else "")
        delen.append({**punt, "id": f"{punt['id']}-d{i}", "begin": dbs[0]["begin"] or punt["begin"],
                      "deel": {"nummer": i, "van": len(samen), "fase": naam, "sprekers": wie,
                               "ouder_id": punt["id"], "ouder_titel": punt["titel"], "woorden_totaal": punt["woorden"]},
                      "woorden": sum(len(b["tekst"].split()) for b in dbs), "beurten": dbs})
    return delen


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
            delen = knip(punt)
            for oud in OUT.glob(f"{punt['id']}-d*.json"):  # delen van een eerdere indeling
                oud.unlink()
            if len(delen) > 1:
                (OUT / f"{punt['id']}.json").unlink(missing_ok=True)  # alleen de delen bestaan nog
            for d in delen:
                (OUT / f"{d['id']}.json").write_text(json.dumps(d, ensure_ascii=False, indent=1))
                n += 1
    print(f"{n} agendapunten geschreven")


if __name__ == "__main__":
    main()
