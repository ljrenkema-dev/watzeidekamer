"""Koppel sprekers uit de verslagen aan een figuur in data/uiterlijk.json.

Gebruik: python3 scripts/koppel.py
Zoekt voor elke spreker in data/agendapunten/ zonder koppeling een persoon met dezelfde
achternaam en voornaam in data/uiterlijk.json. Schrijft data/sprekers.json bij en meldt
sprekers zonder figuur: voor hen moet een figuur gemaakt en gekeurd worden.
"""
import json, unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def plat(s):
    return unicodedata.normalize("NFKD", s or "").encode("ascii", "ignore").decode().lower().replace("-", " ")


def main():
    uiterlijk = json.loads((ROOT / "data" / "uiterlijk.json").read_text())
    pad = ROOT / "data" / "sprekers.json"
    koppeling = json.loads(pad.read_text()) if pad.exists() else {}
    zonder = {}
    for f in (ROOT / "data" / "agendapunten").glob("*.json"):
        for b in json.loads(f.read_text())["beurten"]:
            sp = b["spreker"]
            if sp["id"] in koppeling:
                continue
            naam = plat(sp["naam"]).split()
            hits = [k for k, u in uiterlijk.items()
                    if plat(u["naam"]).split()[-1] == naam[-1] and plat(u["naam"]).split()[0] == naam[0]]
            if len(hits) == 1:
                koppeling[sp["id"]] = hits[0]
            else:
                zonder[sp["id"]] = f"{sp['naam']} ({sp['fractie'] or sp['functie']})"
    pad.write_text(json.dumps(koppeling, ensure_ascii=False, indent=1, sort_keys=True))
    print(f"{len(koppeling)} sprekers gekoppeld")
    for n in sorted(set(zonder.values())):
        print(f"  geen figuur: {n}")


if __name__ == "__main__":
    main()
