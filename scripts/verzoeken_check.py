"""Controleer de vastgelegde verzoeken van een regeling. Gebruik: python3 scripts/verzoeken_check.py <id> [...]

Fouten: citaat niet letterlijk bij die spreker, onbekende spreker, reactie buiten het stuk van het
verzoek, onbekende waarden. Waarschuwingen: Kamerlid sprak in het stuk maar staat niet bij de reacties.
"""
import json, re, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
from check import norm  # noqa: E402

OORDELEN = {"steun", "geen_steun", "steun_brief", "onduidelijk"}
UITKOMSTEN = {"meerderheid", "geen_meerderheid", "dertigledendebat", "ingetrokken", "anders", "onbekend"}
SOORTEN = {"debat", "dertigledendebat", "brief", "stemmingen", "agenda", "anders"}


def gevonden(citaat, teksten):
    stukken = [x for x in re.split(r"\s*(?:…|\.\.\.)\s*", norm(citaat)) if x]
    return bool(stukken) and all(any(st in t for t in teksten) for st in stukken)


def check(pid):
    proc = json.loads((ROOT / "data" / "procedure" / f"{pid}.json").read_text())
    vz = json.loads((ROOT / "data" / "verzoeken" / f"{pid}.json").read_text())
    bs = proc["beurten"]
    fouten, waarsch = [], []
    # positie van elk verzoek = eerste beurt van de verzoeker met het citaat
    posities = []
    for i, v in enumerate(vz.get("verzoeken", []), 1):
        if v.get("soort") not in SOORTEN:
            fouten.append(f"verzoek {i}: soort '{v.get('soort')}' onbekend")
        if v.get("uitkomst") not in UITKOMSTEN:
            fouten.append(f"verzoek {i}: uitkomst '{v.get('uitkomst')}' onbekend")
        start = next((j for j, b in enumerate(bs) if b["spreker"]["id"] == v.get("verzoeker_id")
                      and gevonden(v.get("citaat", ""), [norm(b["tekst"])])), None)
        if start is None:
            fouten.append(f"verzoek {i}: citaat van de verzoeker niet letterlijk gevonden")
        posities.append(start)
    bekende = [p for p in posities if p is not None]
    if bekende != sorted(bekende):
        fouten.append("verzoeken staan niet in de volgorde van het verslag")
    for i, v in enumerate(vz.get("verzoeken", []), 1):
        start = posities[i - 1]
        if start is None:
            continue
        eind = next((p for p in posities[i:] if p is not None), len(bs))
        stuk = bs[start:eind]
        sprak = {b["spreker"]["id"]: b["spreker"] for b in stuk if not b["voorzitter"]}
        for r in v.get("reacties", []):
            if r.get("oordeel") not in OORDELEN:
                fouten.append(f"verzoek {i}: oordeel '{r.get('oordeel')}' onbekend")
            if r.get("spreker_id") not in sprak:
                fouten.append(f"verzoek {i}: reageerder {r.get('spreker_id')} sprak niet in dit stuk")
            elif not gevonden(r.get("citaat", ""), [norm(b["tekst"]) for b in stuk if b["spreker"]["id"] == r["spreker_id"]]):
                fouten.append(f"verzoek {i}: citaat van {sprak[r['spreker_id']]['verslagnaam']} niet letterlijk gevonden")
        genoemd = {r.get("spreker_id") for r in v.get("reacties", [])} | {v.get("verzoeker_id")}
        for sid, sp in sprak.items():
            if sid not in genoemd:
                waarsch.append(f"verzoek {i}: {sp['verslagnaam']} ({sp['fractie']}) sprak maar staat niet bij de reacties")
        if v.get("uitkomst") != "onbekend" and v.get("uitkomst_citaat"):
            if not gevonden(v["uitkomst_citaat"], [norm(b["tekst"]) for b in stuk if b["voorzitter"]]):
                fouten.append(f"verzoek {i}: uitkomst_citaat niet letterlijk bij de voorzitter gevonden")
        elif v.get("uitkomst") != "onbekend":
            fouten.append(f"verzoek {i}: uitkomst zonder uitkomst_citaat")
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
