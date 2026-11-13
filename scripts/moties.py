"""Moties bij een debat: welke moties in het verslag genoemd worden, met indieners, de volledige tekst,
het oordeel van het kabinet (uit het verslag) en, zodra er gestemd is, de uitslag per fractie.
Bron: Gegevensmagazijn (Document, soort Motie; Zaak → Besluit → Stemming). De tekst komt uit de pdf (pdftotext).
Gebruik: python3 scripts/moties.py [id ...]   (zonder id: alle agendapunten; uitslagen worden steeds bijgewerkt)
Uitvoer: data/moties/<agendapunt-id>.json"""
import json, re, subprocess, sys, tempfile, time, urllib.parse, urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
B = "https://gegevensmagazijn.tweedekamer.nl/OData/v4/2.0"
UA = {"User-Agent": "watzeidekamer/0.1 (open data hergebruik)"}
UIT = ROOT / "data" / "moties"
OORDELEN = [("oordeel kamer", "oordeel Kamer"), ("overnemen", "overgenomen"), ("overgenomen", "overgenomen"),
            ("ontraad", "ontraden"), ("ontraden", "ontraden"), ("aangehouden", "aangehouden"), ("aanhouden", "aangehouden"),
            ("ingetrokken", "ingetrokken"), ("ondersteuning van beleid", "ondersteuning van beleid"), ("ontijdig", "ontijdig")]


def get(url, binair=False, pogingen=3):
    for i in range(pogingen):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=90) as r:
                data = r.read()
                return data if binair else json.loads(data)
        except Exception:
            if i == pogingen - 1:
                raise
            time.sleep(3 * (i + 1))


def odata(pad, **q):
    return get(f"{B}/{pad}?" + urllib.parse.urlencode({f"${k}": v for k, v in q.items()}, quote_via=urllib.parse.quote))


def genoemd(punt):
    """Nummers van moties die in het verslag genoemd worden, met het oordeel van het kabinet erbij."""
    nrs, oordeel = set(), {}
    for b in punt["beurten"]:
        tekst = b["tekst"]
        for m in re.finditer(r"(?:stuk|stukken)\s+nr(?:s)?\.\s*(\d{1,4})", tekst, re.I):
            nr = m.group(1)
            nrs.add(nr)
            if b["spreker"].get("fractie"):
                continue  # het oordeel komt van een bewindspersoon
            na = tekst[m.end(): m.end() + 220].lower()
            na = re.split(r"stuk nr\.", na)[0]
            for sleutel, waarde in OORDELEN:
                if sleutel in na:
                    oordeel.setdefault(nr, waarde)
                    break
    return nrs, oordeel


def tekst_uit_pdf(data):
    with tempfile.NamedTemporaryFile(suffix=".pdf") as f:
        f.write(data); f.flush()
        t = subprocess.run(["pdftotext", "-layout", f.name, "-"], capture_output=True, text=True).stdout
    t = re.sub(r"[ \t]+", " ", t)
    begin = t.find("De Kamer,")
    eind = t.find("en gaat over tot de orde van de dag.")
    kern = t[begin: eind + len("en gaat over tot de orde van de dag.")] if begin >= 0 and eind > begin else t
    kern = "\n".join(r.strip() for r in kern.splitlines() if r.strip())
    return re.sub(r"([a-zà-ÿ])-\n([a-zà-ÿ])", r"\1\2", kern)  # afgebroken woorden weer heel


def uitslag(zaken):
    for z in zaken or []:
        for b in z.get("Besluit") or []:
            st = [s for s in (b.get("Stemming") or []) if s.get("ActorFractie")]
            if st:
                voor = sorted({s["ActorFractie"] for s in st if s["Soort"] == "Voor"})
                tegen = sorted({s["ActorFractie"] for s in st if s["Soort"] == "Tegen"})
                return {"besluit": (b.get("BesluitTekst") or "").strip(), "voor": voor, "tegen": tegen,
                        "zetels_voor": sum(s.get("FractieGrootte") or 0 for s in st if s["Soort"] == "Voor"),
                        "zetels_tegen": sum(s.get("FractieGrootte") or 0 for s in st if s["Soort"] == "Tegen")}
    return None


def moties_voor(punt):
    nrs, oordeel = genoemd(punt)
    if not nrs:
        return []
    datum = punt["vergadering"]["datum"]
    sprekers = {b["spreker"]["verslagnaam"].lower() for b in punt["beurten"]}
    docs = []
    lijst = sorted(nrs, key=int)
    for i in range(0, len(lijst), 8):  # in porties: een te lange zoekvraag geeft een fout
        flt = (f"Soort eq 'Motie' and Verwijderd eq false and Datum ge {datum} and Datum le {datum}T23:59:59Z "
               f"and ({' or '.join(f'Volgnummer eq {n}' for n in lijst[i:i + 8])})")
        docs += odata("Document", filter=flt, select="Id,DocumentNummer,Volgnummer,Onderwerp,Titel,Datum",
                      expand="Kamerstukdossier($select=Nummer,Toevoeging,Titel),DocumentActor($select=ActorNaam,ActorFractie,Relatie),"
                             "Zaak($select=Id,Nummer;$expand=Besluit($select=BesluitTekst,BesluitSoort;$expand=Stemming($select=ActorFractie,Soort,FractieGrootte)))")["value"]
    uit = []
    for d in docs:
        indieners = sorted([a for a in d.get("DocumentActor") or [] if any(w in (a.get("Relatie") or "").lower() for w in ("ondertekenaar", "indiener"))],
                           key=lambda a: 0 if (a.get("Relatie") or "").lower().startswith("eerste") else 1)
        namen = [a["ActorNaam"] for a in indieners]
        # bij twee moties met hetzelfde nummer (ander dossier) kiezen we die waarvan een indiener in het debat sprak
        if indieners and not any(n.split()[-1].lower() in s or s in n.lower() for n in namen for s in sprekers):
            continue
        ks = (d.get("Kamerstukdossier") or [{}])[0] if isinstance(d.get("Kamerstukdossier"), list) else (d.get("Kamerstukdossier") or {})
        try:
            tekst = tekst_uit_pdf(get(f"{B}/Document({d['Id']})/resource", binair=True))
        except Exception as e:
            tekst = ""
            print(f"  geen tekst voor {d['DocumentNummer']}: {str(e)[:60]}")
        nr = str(d["Volgnummer"])
        uit.append({"nummer": nr, "document": d["DocumentNummer"], "id": d["Id"],
                    "dossier": f"{ks.get('Nummer', '')}{' ' + ks['Toevoeging'] if ks.get('Toevoeging') else ''}".strip(),
                    "dossier_titel": ks.get("Titel"), "onderwerp": d.get("Onderwerp"),
                    "indieners": [{"naam": a["ActorNaam"], "fractie": a.get("ActorFractie"), "rol": a.get("Relatie")} for a in indieners],
                    "tekst": tekst, "oordeel_kabinet": oordeel.get(nr), "uitslag": uitslag(d.get("Zaak")),
                    "bron": f"{B}/Document({d['Id']})/resource"})
    return sorted(uit, key=lambda m: int(m["nummer"]))


def main(ids):
    UIT.mkdir(parents=True, exist_ok=True)
    bestanden = [ROOT / "data" / "agendapunten" / f"{i}.json" for i in ids] if ids else sorted((ROOT / "data" / "agendapunten").glob("*.json"))
    for f in bestanden:
        punt = json.loads(f.read_text())
        doel = UIT / f"{punt['id']}.json"
        oud = json.loads(doel.read_text()) if doel.exists() else None
        if oud and all(m.get("uitslag") for m in oud["moties"]):
            continue  # alles bekend, ook de stemmingen
        try:
            ms = moties_voor(punt)
        except Exception as e:
            print(f"{punt['id']}: mislukt ({str(e)[:80]})"); continue
        if not ms and not oud:
            continue
        doel.write_text(json.dumps({"agendapunt": punt["id"], "moties": ms}, ensure_ascii=False, indent=1))
        print(f"{punt['id']}: {len(ms)} moties, {sum(1 for m in ms if m['uitslag'])} met uitslag")


if __name__ == "__main__":
    main(sys.argv[1:])
