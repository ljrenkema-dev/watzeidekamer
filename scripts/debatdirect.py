"""Haalt per agendapunt de spreekmomenten uit Debat Direct op, zodat een citaat kan linken naar het moment in de video.
Debat Direct gebruikt dezelfde id's als de agendapunten in het Gegevensmagazijn. Per debat bewaren we
data/debatdirect/<id>.json met datum, categorie, zaal, slug en de spreekmomenten (persoon-id, soort, tijd).
Gebruik: python3 scripts/debatdirect.py [--opnieuw]"""
import json, sys, time, urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
API = "https://cdn.debatdirect.tweedekamer.nl/api/agenda/{datum}/debates/{id}"
SITE = "https://debatdirect.tweedekamer.nl"
UIT = ROOT / "data" / "debatdirect"
UA = {"User-Agent": "WatZeiDeKamer/1.0 (watzeidekamer.nl)"}


def haal(datum, id_):
    req = urllib.request.Request(API.format(datum=datum, id=id_), headers=UA)
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.loads(r.read())


def main(opnieuw=False):
    UIT.mkdir(parents=True, exist_ok=True)
    gedaan = set()
    for f in sorted((ROOT / "data" / "agendapunten").glob("*.json")):
        punt = json.loads(f.read_text())
        id_ = punt["id"][:36]
        if id_ in gedaan:
            continue
        gedaan.add(id_)
        doel = UIT / f"{id_}.json"
        if doel.exists() and not opnieuw:
            continue
        datum = (punt.get("begin") or punt["vergadering"]["datum"])[:10]
        try:
            d = haal(datum, id_)
        except Exception as e:  # niet elk agendapunt staat in Debat Direct (bijv. besloten overleg)
            print(f"{id_}: niet gevonden ({str(e)[:60]})")
            continue
        momenten = [{"persoon": e["objectId"], "soort": e["eventType"], "start": e["eventStart"]}
                    for e in d.get("events", []) if e.get("eventType") in ("speaker", "interrupter", "chairman")]
        doel.write_text(json.dumps({
            "id": id_, "datum": d.get("debateDate") or datum, "categorie": (d.get("categoryIds") or ["onbekend"])[0],
            "zaal": d.get("locationId"), "slug": d.get("slug"), "naam": d.get("name"),
            "url": f"{SITE}/{d.get('debateDate') or datum}/{(d.get('categoryIds') or ['onbekend'])[0]}/{d.get('locationId')}/{d.get('slug')}",
            "momenten": sorted(momenten, key=lambda m: m["start"])}, ensure_ascii=False, indent=1))
        print(f"{id_}: {len(momenten)} spreekmomenten")
        time.sleep(0.5)


if __name__ == "__main__":
    main("--opnieuw" in sys.argv)
