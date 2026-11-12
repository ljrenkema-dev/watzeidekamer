"""Alle gesproken tekst per politicus, voor latere analyses (niet op de site).

Gebruik: python3 scripts/corpus.py
Leest alle data/agendapunten/*.json en schrijft per spreker data/corpus/<slug>.jsonl.gz:
één regel per spreekbeurt, in tijdsvolgorde, met de letterlijke tekst uit het verslag.
Wordt elke run helemaal opnieuw opgebouwd, zodat een nieuwere versie van een verslag
(bijv. gecorrigeerd) de oude tekst vervangt. data/corpus/index.json geeft per persoon
de naam, fractie(s), functie(s), aantal spreekbeurten en woorden, en eerste/laatste datum.

Velden per regel: datum, tijd, vergadering, soort (Plenair/Commissie), agendapunt, agendapunt_titel,
onderdeel (debat, Opening, Mededelingen, Regeling van werkzaamheden, Sluiting), deel, rol (woordvoerder/interrumpant), voorzitter, fractie, functie, verslag_status, woorden, tekst.
Ook opgenomen: wat er gezegd is bij opening, mededelingen en regeling van werkzaamheden (data/procedure/).
Presentielijsten en afmeldingen staan in data/procedure/*.json (velden aanwezig, kamerleden_aanwezig, afgemeld).
"""
import gzip, json, re, unicodedata
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "data" / "corpus"


def slug(naam):
    t = unicodedata.normalize("NFKD", naam).encode("ascii", "ignore").decode().lower()
    return re.sub(r"[^a-z0-9]+", "-", t).strip("-")


def main():
    regels, meta = defaultdict(list), {}
    bestanden = [(f, "debat") for f in sorted((ROOT / "data" / "agendapunten").glob("*.json"))]
    bestanden += [(f, "procedure") for f in sorted((ROOT / "data" / "procedure").glob("*.json"))]
    for f, soort in bestanden:
        p = json.loads(f.read_text())
        v = p["vergadering"]
        for b in p["beurten"]:
            sp = b["spreker"]
            regels[sp["id"]].append({
                "datum": v["datum"], "tijd": b["begin"], "vergadering": v["titel"], "soort": v["soort"],
                "agendapunt": p["id"], "agendapunt_titel": p["titel"],
                "onderdeel": p["soort"] if soort == "procedure" else "debat",
                "deel": (p.get("deel") or {}).get("fase"),
                "rol": b["rol"], "voorzitter": b["voorzitter"],
                "fractie": sp["fractie"], "functie": sp["functie"], "verslag_status": v["status"],
                "woorden": len(b["tekst"].split()), "tekst": b["tekst"],
            })
            m = meta.setdefault(sp["id"], {"naam": sp["naam"], "fracties": set(), "functies": set()})
            m["naam"] = sp["naam"]
            if sp["fractie"]: m["fracties"].add(sp["fractie"])
            if sp["functie"]: m["functies"].add(sp["functie"])
    OUT.mkdir(parents=True, exist_ok=True)
    for oud in OUT.glob("*.jsonl.gz"):
        oud.unlink()
    koppeling = json.loads((ROOT / "data" / "sprekers.json").read_text()) if (ROOT / "data" / "sprekers.json").exists() else {}
    index, gebruikt = {}, {}
    for sid, rs in regels.items():
        rs.sort(key=lambda r: (r["tijd"] or r["datum"], r["agendapunt"]))
        naam = meta[sid]["naam"]
        s = slug(naam)
        if s in gebruikt and gebruikt[s] != sid:  # twee mensen met dezelfde naam
            s = f"{s}-{sid[:8]}"
        gebruikt[s] = sid
        with gzip.open(OUT / f"{s}.jsonl.gz", "wt", encoding="utf-8") as fh:
            for r in rs:
                fh.write(json.dumps(r, ensure_ascii=False) + "\n")
        index[s] = {"spreker_id": sid, "persoon": koppeling.get(sid), "naam": naam, "fracties": sorted(meta[sid]["fracties"]),
                    "functies": sorted(meta[sid]["functies"]), "spreekbeurten": len(rs),
                    "woorden": sum(r["woorden"] for r in rs), "eerste": rs[0]["datum"], "laatste": rs[-1]["datum"]}
    (OUT / "index.json").write_text(json.dumps(dict(sorted(index.items())), ensure_ascii=False, indent=1))
    print(f"{len(index)} sprekers, {sum(i['spreekbeurten'] for i in index.values())} spreekbeurten, "
          f"{sum(i['woorden'] for i in index.values()):,} woorden".replace(",", "."))


if __name__ == "__main__":
    main()
