"""Welke lessen uit prompts/lessen.md gaan nog mis? Gebruik: python3 scripts/lessen.py [DAGEN]

Telt de bevindingen in data/redactie/*.json per les (veld 'les'), per soort en per ernst,
over de laatste DAGEN (standaard 30). Bevindingen met 'les': 'nieuw' worden apart getoond:
dat zijn kandidaten voor een nieuwe les.
"""
import json, sys
from collections import Counter
from datetime import date, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def main(dagen):
    grens = (date.today() - timedelta(days=dagen)).isoformat()
    per_les, per_soort, nieuw, strips, totaal = Counter(), Counter(), [], 0, 0
    for f in sorted((ROOT / "data" / "redactie").glob("*.json")):
        r = json.loads(f.read_text())
        if r.get("datum", "") < grens:
            continue
        strips += 1
        for b in r.get("bevindingen", []):
            totaal += 1
            les = b.get("les") or "zonder les"
            per_les[les] += 1
            per_soort[(b.get("soort"), b.get("ernst"))] += 1
            if les == "nieuw":
                nieuw.append(f"  [{b.get('soort')}/{b.get('ernst')}] {b.get('waarom', '')[:140]}")
    print(f"{totaal} bevindingen in {strips} nagelezen strips (laatste {dagen} dagen), {totaal / max(strips, 1):.1f} per strip")
    print("Per les:")
    for les, n in sorted(per_les.items(), key=lambda x: -x[1]):
        print(f"  {les:12} {n}")
    print("Per soort en ernst:")
    for (soort, ernst), n in sorted(per_soort.items(), key=lambda x: -x[1]):
        print(f"  {soort}/{ernst}: {n}")
    if nieuw:
        print("Nieuwe fouten (kandidaat voor een les):")
        print("\n".join(nieuw))


if __name__ == "__main__":
    main(int(sys.argv[1]) if len(sys.argv) > 1 else 30)
