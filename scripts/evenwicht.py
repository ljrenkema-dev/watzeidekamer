"""Hoeveel ruimte krijgt elke partij in een strip, vergeleken met hoeveel zij sprak?

Gebruik: python3 scripts/evenwicht.py <agendapunt_id> [...]
Per fractie (bewindspersonen samen als 'kabinet'): aandeel gesproken woorden in het agendapunt,
aantal stripvakken, en of de fractie in 'Wie vindt wat?' staat. Signalen:
- fractie sprak maar staat niet in 'sprekers'
- fractie heeft 2+ vakken meer dan de anderen terwijl haar spreektijd dat niet rechtvaardigt
- fractie met ≥15% van de woorden heeft geen enkel vak
De uitkomst is een hulpmiddel voor de redacteur, geen automatische afkeuring.
"""
import json, sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def groep(sp):
    return sp["fractie"] or "kabinet"


def evenwicht(pid):
    punt = json.loads((ROOT / "data" / "agendapunten" / f"{pid}.json").read_text())
    strip = json.loads((ROOT / "data" / "strips" / f"{pid}.json").read_text())
    bekend = {b["spreker"]["id"]: b["spreker"] for b in punt["beurten"]}
    woorden = Counter()
    for b in punt["beurten"]:
        if not b["voorzitter"]:
            woorden[groep(b["spreker"])] += len(b["tekst"].split())
    totaal = sum(woorden.values()) or 1
    # wie in dit agendapunt alleen als voorzitter sprak, telt niet mee voor zijn partij
    voorzitter = {i for i in bekend if all(b["voorzitter"] for b in punt["beurten"] if b["spreker"]["id"] == i)}
    vakken = Counter("voorzitter" if v["spreker_id"] in voorzitter else groep(bekend[v["spreker_id"]])
                     for v in strip["strip"] if v["spreker_id"])
    genoemd = {groep(bekend[s["id"]]) for s in strip["sprekers"] if s["id"] in bekend}
    n_vak = sum(vakken.values()) or 1
    rijen, signalen = [], []
    if vakken.get("voorzitter"):
        rijen.append(("voorzitter", 0.0, vakken["voorzitter"], True))
    for g, w in woorden.most_common():
        aandeel = w / totaal
        rijen.append((g, aandeel, vakken.get(g, 0), g in genoemd))
        if g not in genoemd:
            signalen.append(f"{g} sprak ({aandeel:.0%} van de woorden) maar staat niet in 'Wie vindt wat?'")
        if aandeel >= 0.15 and not vakken.get(g):
            signalen.append(f"{g} had {aandeel:.0%} van de woorden maar geen enkel vak")
        verwacht = aandeel * n_vak
        if vakken.get(g, 0) - verwacht >= 2:
            signalen.append(f"{g} heeft {vakken[g]} vakken; op basis van spreektijd ongeveer {verwacht:.1f}")
    return rijen, signalen


if __name__ == "__main__":
    for pid in sys.argv[1:]:
        rijen, signalen = evenwicht(pid)
        print(pid)
        for g, a, v, s in rijen:
            print(f"  {g:22} {a:5.0%} van de woorden  {v} vak(ken)  {'in sprekers' if s else 'NIET in sprekers'}")
        for s in signalen:
            print(f"  LET OP {s}")
