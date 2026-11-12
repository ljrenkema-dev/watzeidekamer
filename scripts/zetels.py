"""Leg de zetelverdeling van vandaag vast in data/fracties.json (per datum, zodat oude verzoeken
later met de zetels van toen worden gerekend). Gebruik: python3 scripts/zetels.py"""
import json, sys, urllib.parse
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
from fetch import BASE, get  # noqa: E402


def main():
    q = urllib.parse.quote("Verwijderd eq false and DatumInactief eq null")
    rijen = get(f"{BASE}/Fractie?$filter={q}&$select=Afkorting,NaamNL,AantalZetels")["value"]
    pad = ROOT / "data" / "fracties.json"
    alles = json.loads(pad.read_text()) if pad.exists() else {}
    nu = {r["Afkorting"]: {"naam": r["NaamNL"], "zetels": r["AantalZetels"] or 0} for r in rijen}
    laatste = alles[max(alles)] if alles else None
    if nu != laatste:  # alleen een nieuwe stand als er iets veranderd is
        alles[date.today().isoformat()] = nu
    pad.write_text(json.dumps(dict(sorted(alles.items())), ensure_ascii=False, indent=1))
    print(f"{len(nu)} fracties, {sum(f['zetels'] for f in nu.values())} zetels")


def zetels_op(datum):
    """Zetelverdeling die gold op datum (de laatste stand op of vóór die datum, anders de oudste)."""
    alles = json.loads((ROOT / "data" / "fracties.json").read_text())
    geldig = [d for d in alles if d <= datum]
    return alles[max(geldig) if geldig else min(alles)]


if __name__ == "__main__":
    main()
