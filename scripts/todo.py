"""Welke agendapunten hebben (opnieuw) een strip nodig? Gebruik: python3 scripts/todo.py [MAX]

Een agendapunt telt mee als er geen strip is, of als de strip bij een oudere versie van het
verslag hoort. Overgeslagen: stemmingen, regeling van werkzaamheden, procedurevergaderingen,
punten met alleen de voorzitter, en punten boven LANG woorden (die moeten eerst opgeknipt worden).
Volgorde: plenair voor commissie, nieuwste eerst. Print één id per regel; de reden op stderr.
"""
import json, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
LANG = 25000  # parse.py knipt alles boven 16.000 woorden al in delen
SKIP = {"Stemmingen", "Regeling van werkzaamheden", "Procedurevergadering"}


def main(maximum):
    rijen, te_lang = [], []
    for f in (ROOT / "data" / "agendapunten").glob("*.json"):
        p = json.loads(f.read_text())
        if p["soort_activiteit"] in SKIP or "regeling van werkzaamheden" in p["titel"].lower():
            continue
        sf = ROOT / "data" / "strips" / f.name
        if sf.exists() and json.loads(sf.read_text()).get("verslag_id") == p["vergadering"]["verslag_id"]:
            continue
        if p["woorden"] > LANG:
            te_lang.append(p)
            continue
        reden = "nieuwe versie van het verslag" if sf.exists() else "nog geen strip"
        rijen.append((p["vergadering"]["soort"] != "Plenair", p["begin"], p, reden))
    # delen van één debat blijven bij elkaar en op volgorde
    def volgorde(r):
        commissie, _, p, _ = r
        d = p.get("deel") or {}
        datum = [-ord(c) for c in p["vergadering"]["datum"]]  # nieuwste eerst
        return (commissie, datum, d.get("ouder_id", p["id"]), d.get("nummer", 0))
    rijen.sort(key=volgorde)
    for _, _, p, reden in rijen[:maximum]:
        print(p["id"])
        d = p.get("deel")
        deel = f" [deel {d['nummer']}/{d['van']}: {d['fase']}]" if d else ""
        print(f"  {p['vergadering']['datum']} {p['vergadering']['soort']:9} {p['woorden']:>6} woorden  {p['titel'][:50]}{deel}  ({reden})", file=sys.stderr)
    if len(rijen) > maximum:
        print(f"  … nog {len(rijen) - maximum} voor een volgende nacht", file=sys.stderr)
    for p in te_lang:
        print(f"  TE LANG ({p['woorden']} woorden), eerst opknippen: {p['titel'][:60]}", file=sys.stderr)


if __name__ == "__main__":
    main(int(sys.argv[1]) if len(sys.argv) > 1 else 10)
