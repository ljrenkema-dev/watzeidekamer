"""Controleer een debatpagina (data/paginas/<id>.json, zie prompts/pagina.md) tegen de bron.
Gebruik: python3 scripts/check_pagina.py <agendapunt_id> [...]

Fouten (exit 1): verkeerde vorm, onbekende spreker, fractie die sprak maar geen standpunt heeft,
ongeldige verwijzing naar een kernpunt, verslag_id van een andere versie, titel te lang.
De oude stripbestanden (data/strips/) blijven door scripts/check.py gecontroleerd.
"""
import json, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def tekst(x):
    return x.strip() if isinstance(x, str) else ""


def check(pid):
    punt = json.loads((ROOT / "data" / "agendapunten" / f"{pid}.json").read_text())
    p = json.loads((ROOT / "data" / "paginas" / f"{pid}.json").read_text())
    fouten, waarsch = [], []
    bekend = {b["spreker"]["id"]: b["spreker"] for b in punt["beurten"]}
    if p.get("agendapunt") != pid:
        fouten.append("veld 'agendapunt' klopt niet")
    if p.get("verslag_id") != punt["vergadering"]["verslag_id"]:
        fouten.append("verslag_id hoort bij een andere versie van het verslag")
    if not tekst(p.get("titel")):
        fouten.append("titel ontbreekt")
    elif len(p["titel"].split()) > 12:
        fouten.append(f"titel heeft {len(p['titel'].split())} woorden, hooguit 12")
    if not tekst(p.get("samenvatting")):
        fouten.append("samenvatting ontbreekt")
    kp = p.get("kernpunten")
    if not isinstance(kp, list) or not kp or not all(tekst(k) for k in kp):
        fouten.append("kernpunten: lijst met teksten nodig")
        kp = []
    ids = []
    for s in p.get("sprekers", []):
        if s.get("id") not in bekend:
            fouten.append(f"sprekers: onbekende id {s.get('id')}")
            continue
        if not tekst(s.get("standpunt")):
            fouten.append(f"sprekers: standpunt van {bekend[s['id']]['naam']} ontbreekt")
        ids.append(s["id"])
    genoemd = {bekend[i]["fractie"] for i in ids}
    sprak = {b["spreker"]["fractie"] for b in punt["beurten"] if not b["voorzitter"] and b["spreker"]["fractie"]}
    for f in sorted(sprak - genoemd):
        fouten.append(f"fractie {f} sprak maar heeft geen standpunt in 'sprekers'")
    for o in p.get("onderwerpen") or []:
        if not tekst(o.get("titel")):
            fouten.append("onderwerp zonder titel")
        for i in o.get("sprekers", []):
            if i not in bekend:
                fouten.append(f"onderwerp '{o.get('titel')}': onbekende spreker {i}")
        for n in o.get("kernpunten", []):
            if not isinstance(n, int) or not 0 <= n < len(kp):
                fouten.append(f"onderwerp '{o.get('titel')}': kernpunt {n} bestaat niet")
    for w in p.get("woorden") or []:
        if not tekst(w.get("woord")) or not tekst(w.get("uitleg")):
            fouten.append("woorden: elk woord heeft 'woord' en 'uitleg'")
    if "strip" in p:
        waarsch.append("veld 'strip' wordt niet meer gebruikt")
    return fouten, waarsch


if __name__ == "__main__":
    slecht = False
    for pid in sys.argv[1:]:
        f, w = check(pid)
        print(f"{pid}: {'OK' if not f else f'{len(f)} fout(en)'}" + (f", {len(w)} waarschuwing(en)" if w else ""))
        for x in f: print("  FOUT  " + x)
        for x in w: print("  let op " + x)
        slecht |= bool(f)
    sys.exit(1 if slecht else 0)
