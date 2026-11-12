"""Haal vergaderingen en hun nieuwste verslag op bij het Gegevensmagazijn van de Tweede Kamer.

Gebruik: python3 scripts/fetch.py 2026-11-05 2026-11-12
Schrijft data/raw/<vergadering_id>.xml en data/vergaderingen.json.
Een verslag wordt alleen opnieuw opgehaald als er een nieuwere versie is.
"""
import json, sys, time, urllib.parse, urllib.request
from pathlib import Path

BASE = "https://gegevensmagazijn.tweedekamer.nl/OData/v4/2.0"
ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "data" / "raw"
INDEX = ROOT / "data" / "vergaderingen.json"
UA = {"User-Agent": "watzeidekamer/0.1 (open data hergebruik)"}


def get(url, as_json=True):
    for attempt in range(4):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=120) as r:
                data = r.read()
            return json.loads(data) if as_json else data
        except Exception as e:  # netwerk hapert soms; probeer een paar keer
            if attempt == 3:
                raise
            print(f"  opnieuw ({e})", file=sys.stderr)
            time.sleep(2 ** attempt * 2)


def vergaderingen(van, tot):
    flt = (f"Verwijderd eq false and Datum ge {van}T00:00:00Z and Datum le {tot}T23:59:59Z")
    q = urllib.parse.urlencode({
        "$filter": flt,
        "$select": "Id,Soort,Titel,Datum,Zaal,VergaderingNummer,Kamer",
        "$expand": "Verslag($filter=Verwijderd eq false;$select=Id,Soort,Status,GewijzigdOp)",
        "$orderby": "Datum desc",
    }, safe="$,() ")
    url = f"{BASE}/Vergadering?{q}".replace(" ", "%20")
    while url:
        page = get(url)
        yield from page["value"]
        url = page.get("@odata.nextLink")


def main(van, tot):
    RAW.mkdir(parents=True, exist_ok=True)
    index = json.loads(INDEX.read_text()) if INDEX.exists() else {}
    for v in vergaderingen(van, tot):
        verslagen = sorted(v.get("Verslag") or [], key=lambda s: s["GewijzigdOp"])
        if not verslagen:
            continue
        nieuwste = verslagen[-1]
        oud = index.get(v["Id"], {})
        pad = RAW / f"{v['Id']}.xml"
        if oud.get("verslag_id") == nieuwste["Id"] and oud.get("gewijzigd") == nieuwste["GewijzigdOp"] and pad.exists():
            continue
        print(f"{v['Datum'][:10]} {v['Soort']:9} {nieuwste['Status']:15} {v['Titel']}")
        pad.write_bytes(get(f"{BASE}/Verslag({nieuwste['Id']})/resource", as_json=False))
        index[v["Id"]] = {
            "titel": v["Titel"], "soort": v["Soort"], "datum": v["Datum"][:10],
            "verslag_id": nieuwste["Id"], "verslag_soort": nieuwste["Soort"],
            "status": nieuwste["Status"], "gewijzigd": nieuwste["GewijzigdOp"],
        }
    INDEX.write_text(json.dumps(index, ensure_ascii=False, indent=1, sort_keys=True))
    print(f"{len(index)} vergaderingen in de index")


if __name__ == "__main__":
    main(*sys.argv[1:3])
