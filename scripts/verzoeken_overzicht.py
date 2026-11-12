"""Overzicht van alle verzoeken met zetels voor en tegen. Gebruik: python3 scripts/verzoeken_overzicht.py

Schrijft data/verzoeken/overzicht.json. De fractie van de verzoeker telt als steun. Een fractie
die niet reageerde, telt als 'geen reactie'. Een reactie namens een fractie telt voor alle zetels
van die fractie. Bij een fractie met tegenstrijdige reacties telt de eerste.
"""
import json, sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
from zetels import zetels_op  # noqa: E402


def main():
    uit, per_fractie = [], defaultdict(lambda: defaultdict(int))
    for f in sorted((ROOT / "data" / "verzoeken").glob("*.json")):
        if f.name == "overzicht.json":
            continue
        vz = json.loads(f.read_text())
        proc = json.loads((ROOT / "data" / "procedure" / f"{vz['procedure']}.json").read_text())
        sp = {b["spreker"]["id"]: b["spreker"] for b in proc["beurten"]}
        datum = proc["vergadering"]["datum"]
        zetels = zetels_op(datum)
        for i, v in enumerate(vz["verzoeken"], 1):
            verzoeker = sp[v["verzoeker_id"]]
            oordeel = {verzoeker["fractie"]: "steun"}
            for r in v["reacties"]:
                fr = sp[r["spreker_id"]]["fractie"]
                if fr and fr not in oordeel:
                    oordeel[fr] = "geen_steun" if r["oordeel"] == "steun_brief" else r["oordeel"]
            telling = defaultdict(int)
            for fr, z in zetels.items():
                telling[oordeel.get(fr, "geen_reactie")] += z["zetels"]
            for fr, o in oordeel.items():
                per_fractie[fr][o] += 1
            per_fractie[verzoeker["fractie"]]["verzoeken"] += 1
            if v["uitkomst"] in ("meerderheid", "dertigledendebat"):
                per_fractie[verzoeker["fractie"]]["gehaald"] += 1
            # past de uitkomst bij de zetels? (meerderheid = 76; dertigledendebat = 30 leden)
            z = telling
            if v["uitkomst"] == "meerderheid":
                past = "ja" if z["steun"] >= 76 else ("mogelijk" if z["steun"] + z["onduidelijk"] + z["geen_reactie"] >= 76 else "nee")
            elif v["uitkomst"] in ("geen_meerderheid", "dertigledendebat"):
                past = "ja" if z["steun"] < 76 else "nee"
            else:
                past = "n.v.t."
            uit.append({"past_bij_zetels": past, "datum": datum, "procedure": vz["procedure"], "nr": i,
                        "verzoeker": verzoeker["naam"], "fractie": verzoeker["fractie"], "soort": v["soort"],
                        "onderwerp": v["onderwerp"], "uitkomst": v["uitkomst"],
                        "zetels": {k: telling.get(k, 0) for k in ("steun", "geen_steun", "onduidelijk", "geen_reactie")},
                        "fracties": oordeel})
    (ROOT / "data" / "verzoeken" / "overzicht.json").write_text(json.dumps(
        {"verzoeken": uit, "per_fractie": {k: dict(v) for k, v in sorted(per_fractie.items())}},
        ensure_ascii=False, indent=1))
    for x in uit:
        z = x["zetels"]
        print(f"{x['datum']} {x['nr']:>2}. {x['fractie']:18} {x['onderwerp'][:58]:58} "
              f"voor {z['steun']:>3} tegen {z['geen_steun']:>3} ? {z['onduidelijk']:>3} - {z['geen_reactie']:>3}  {x['uitkomst']}"
              + ("" if x["past_bij_zetels"] in ("ja", "n.v.t.") else f"  << past bij zetels: {x['past_bij_zetels']}"))


if __name__ == "__main__":
    main()
