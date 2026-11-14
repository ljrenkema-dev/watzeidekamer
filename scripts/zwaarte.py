"""Hoe uitgebreid wordt een agendapunt verwerkt? Gebruik: python3 scripts/zwaarte.py <id> [...]

volledig: pagina + kaart + lezing van beide (prompts/lezer.md).
licht:    pagina + korte lezing van alleen de pagina; geen kaart.
Licht is: een ordedebat, stemmingen, een tweeminutendebat, of minder dan 2.500 gesproken woorden
(zonder de voorzitter). Een vragenuur is altijd volledig. (Besluit eigenaar, 14 nov 2026; de grens volgt
uit de debatten van november 2026: alles onder 2.000 woorden was procedure of moties, echte debatten
begonnen boven 3.000.)
"""
import json, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
GRENS = 2500


def zwaarte(pid):
    a = json.loads((ROOT / "data" / "agendapunten" / f"{pid}.json").read_text())
    woorden = sum(len(b["tekst"].split()) for b in a["beurten"] if not b.get("voorzitter"))
    fase = ((a.get("deel") or {}).get("fase") or "").lower()
    soort = (a.get("soort_activiteit") or "").lower()
    opening = " ".join(b["tekst"] for b in a["beurten"][:3] if b.get("voorzitter")).lower()
    if "vragenuur" in soort:
        return "volledig", "vragenuur"
    if "ordedebat" in fase:
        return "licht", "ordedebat"
    if "stemming" in soort:
        return "licht", "stemmingen"
    if "tweeminutendebat" in opening:
        return "licht", "tweeminutendebat"
    if woorden < GRENS:
        return "licht", f"{woorden} woorden (< {GRENS})"
    return "volledig", f"{woorden} woorden"


if __name__ == "__main__":
    for pid in sys.argv[1:]:
        z, waarom = zwaarte(pid)
        print(f"{pid}: {z} ({waarom})")
