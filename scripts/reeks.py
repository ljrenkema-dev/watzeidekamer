"""Spreiding over een reeks debatten met losse onderwerpen (zoals het vragenuur).
Bij zo'n debat belicht de strip één onderwerp (strip_onderwerp). Deze controle kijkt over de laatste
REEKS (10) van die debatten welke fractie de vraag stelde over het onderwerp in de strip, en vergelijkt dat
met haar zetelaandeel. Een fractie mag in die reeks hooguit max(2, afgerond 2 × zetelaandeel × REEKS) keer
de vraagsteller van het stripzonderwerp zijn.
Gebruik:
  python3 scripts/reeks.py                 # overzicht, schrijft data/reeks/vragenuur.json
  python3 scripts/reeks.py --voor <datum>  # wie zit nu al aan de grens (voor de schrijver, vóór de keuze)"""
import json, math, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
import zetels  # noqa: E402

REEKS = 10
SOORTEN = ("vragenuur",)


def is_reeksdebat(punt):
    return any(s in (punt.get("titel") or "").lower() for s in SOORTEN)


def vraagsteller(punt, strip):
    """Fractie van de eerste Kamerlid-spreker bij het onderwerp in de strip, of None."""
    k = strip.get("strip_onderwerp")
    ond = strip.get("onderwerpen") or []
    if k is None or not (0 <= k < len(ond)):
        return None
    bekend = {b["spreker"]["id"]: b["spreker"] for b in punt["beurten"]}
    for sid in ond[k].get("sprekers", []):
        f = (bekend.get(sid) or {}).get("fractie")
        if f:
            return f
    return None


def reeks(tot=None):
    rij = []
    for f in sorted((ROOT / "data" / "strips").glob("*.json")):
        strip = json.loads(f.read_text())
        if strip.get("ingetrokken"):
            continue
        ap = ROOT / "data" / "agendapunten" / f.name
        if not ap.exists():
            continue
        punt = json.loads(ap.read_text())
        datum = punt["vergadering"]["datum"]
        if not is_reeksdebat(punt) or (tot and datum >= tot):
            continue
        rij.append({"id": f.stem, "datum": datum, "fractie": vraagsteller(punt, strip),
                    "onderwerp": ((strip.get("onderwerpen") or [{}])[strip.get("strip_onderwerp") or 0].get("titel") or {}).get("normaal")
                    if strip.get("onderwerpen") else None})
    rij.sort(key=lambda r: r["datum"])
    return rij[-REEKS:]


def grenzen(datum):
    z = zetels.zetels_op(datum)
    totaal = sum(v["zetels"] for v in z.values()) or 150
    return {f: max(2, round(2 * v["zetels"] / totaal * REEKS)) for f, v in z.items()}


def main():
    a = sys.argv[1:]
    tot = a[a.index("--voor") + 1] if "--voor" in a else None
    rij = reeks(tot)
    datum = tot or (rij[-1]["datum"] if rij else "2026-11-13")
    grens = grenzen(datum)
    telling = {}
    for r in rij:
        if r["fractie"]:
            telling[r["fractie"]] = telling.get(r["fractie"], 0) + 1
    oordeel = {f: {"keer": n, "grens": grens.get(f, 2), "status": "boven de grens" if n > grens.get(f, 2)
                   else ("op de grens" if n == grens.get(f, 2) else "ok")} for f, n in sorted(telling.items(), key=lambda x: -x[1])}
    uit = {"reeks": REEKS, "debatten": rij, "per_fractie": oordeel,
           "regel": "Een fractie is in de laatste 10 vragenuren hooguit max(2, afgerond 2 × zetelaandeel × 10) keer de vraagsteller van het onderwerp in de strip."}
    if not tot:
        (ROOT / "data" / "reeks").mkdir(parents=True, exist_ok=True)
        (ROOT / "data" / "reeks" / "vragenuur.json").write_text(json.dumps(uit, ensure_ascii=False, indent=1))
    print(f"Laatste {len(rij)} vragenuren{' vóór ' + tot if tot else ''}:")
    for f, o in oordeel.items():
        print(f"  {f}: {o['keer']} keer (grens {o['grens']}) — {o['status']}")
    vol = [f for f, o in oordeel.items() if o["status"] != "ok"]
    if tot:
        print("Kies bij voorkeur geen onderwerp van: " + (", ".join(vol) if vol else "(geen beperking)"))


if __name__ == "__main__":
    main()
